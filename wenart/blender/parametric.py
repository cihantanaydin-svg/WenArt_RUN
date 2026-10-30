"""Parametric fallback furniture (docs/milestone4.md, Conventions): simple
but recognisable shapes built from the footprint and the type height, used
when a piece has no fitted library asset or its file is missing.

Pure Python (no ``bpy``): the parts are plain vertex/face lists in the
piece's local frame of Milestone 2 (``wenart/synthetic/blocks.py``): width
along X, depth along Y, front = -Y, back (headboard, sofa back, shelf back
panel) = +Y, origin at the footprint centre on the floor, Z up. Every part
carries a material *key* (``wood``, ``fabric``, ``bedding``, ``ceramic``,
``steel``, ``painted``, ``worktop``, ``dark``, ``glass``, ``green``,
``terracotta``) that ``wenart.blender.furniture`` maps to a style slug, and a
``role`` (``body``, ``back``, ``front``, ``handle``, ``top``, ``leg``, ...)
that the tests use to check which side things are on.

Guarantees (checked in tests/test_blender_furniture.py): the XY bounding
box of the parts equals the footprint within 1 cm (handles may stand 8 mm
proud of the front), the lowest vertex is at z = 0 (the floor) and the
``back`` parts touch the +Y side while ``front`` parts touch the -Y side.
The total height may exceed the type height of ``proxies.PROXY_HEIGHTS``
(a bed headboard rises above the mattress, a toilet tank above the seat):
``piece_bbox`` reports the real box, which the camera planner uses.

Milestone 6 (docs/milestone6.md §5 rows 2 and 8), every box unchanged (the
``m5`` cameras depend on ``piece_bbox`` / ``obstacle_rect``; tests pin them
for every type):

- kitchen counter and island fronts stand 1 mm proud of the carcass (their
  front faces were coplanar with it and rendered black), the handles sit on
  the fronts;
- beds have soft bedding inside their own box: a superellipsoid mattress, a
  duvet draped over the sides with smooth deterministic wrinkles, a
  turn-down band and pillows leaning 14 degrees on the headboard (material
  keys ``bedding`` and ``duvet``); parts made of superellipsoids carry
  ``"smooth": True``;
- ``part_bevel_radius``: the bevel radius of each part for the one Bevel
  modifier furniture.py adds (per role, at most a third of the part's
  smallest side, 0 for smooth parts);
- ``decor_rest_height`` puts decor on a parametric bed on the bedding top
  (``bedding_top``), not inside the pillows.

Milestone 7 (docs/milestone7.md §6.4), four documented-only types:

- ``stair`` (fixed equipment, built by ``shell.build_stairs`` like the walls):
  ``stair_plan`` reads the drawn flights and landing (``piece["stair"]``, or
  ``piece["details"]["stair"]`` as the recognition core writes it); every
  drawn tread line is a nosing, so a flight of n lines has n risers and
  n - 1 treads, never one more or less; riser height = rise / all risers
  (rise = ceiling height + the assumed 0.15 m slab, ``riser_source``
  "derived from assumed ceiling and slab"), a warning outside 0.15-0.20 m;
  the rise direction comes from ``stair.direction`` (else +local Y, noted);
  side-by-side flights rise in turn (a U-turn): the flight rising towards
  the landing climbs first. Steps are convex prisms on a 0.15 m waist slab
  (``stair_parts``), a riser plate closes the last riser of each flight, a
  steel handrail runs 0.90 m above the nosings on every side that is not
  against a wall. The ceiling opening (``void``) covers the last flight and
  the landing only, offset 2 mm so the shaft faces never touch the steps;
  ``void_shaft`` closes it with neutral walls and a cap 0.5 m above the
  ceiling. Every assumption is listed in ``plan["assumed"]`` (the scene
  manifest's ``assumed`` entries). Without drawn flights (an AI-typed stair)
  one straight flight along +local Y with an assumed riser count fills the
  footprint, recorded as such.
- ``side_table``: round (``piece_is_round``: the piece says ``shape:
  "round"`` or a circle fits >= 90 % of its drawn points) or square.
- ``floor_lamp``: base, pole and a fabric drum shade; no light.
- ``potted_plant``: the decor plant (pot, soil, stem, crown) filling the drawn
  footprint.

``build_parts`` takes the piece for the two types that read it (``stair``,
``side_table``); the others ignore it.

Milestone 8 (docs/milestone8.md §4):

- ``frame_bedding``: the soft bedding of the parametric bed (superellipsoid
  mattress, draped duvet, turn-down band, pillows leaning back) for a
  library bed frame (``bed_frame: true``): sized to the frame's inner box
  (the footprint minus ``FRAME_INSET`` = 4 % per side, centred), the
  mattress from the fitted deck height up ``FRAME_MATTRESS_M`` (0.20 m), the
  pillows at the back (+Y) end, the duvet from the foot (-Y) end; in the
  piece frame like every part here. ``frame_bedding_info`` is its record
  (deck, mattress top, bedding top, inner box) for the fit and the manifest.
- Decor ``rug``: a flat parametric rug (``RUG_THICKNESS_M``, fabric key)
  at the size the decor rule gives (rugs and wall art are exempt from the
  0.6 m decor cap: ``LARGE_DECOR_TYPES``). ``wall_art`` has no parametric
  shape (``decor_parts`` raises): without a library model it is not built.

Milestone 10 (docs/milestone10.md §4.4-§4.7, §1.6b row 15; track F):

- The 14 new types: the corner sofa (``l_parts``: the main seat along the back
  and the chaise on ``chaise_side``, one arm at the far end), chaise, ottoman,
  bench, bar stool, office chair (a five-star base inside the seat's
  footprint), console table, crib, bunk bed (guard rail, ladder), sideboard,
  shoe, display, tall and wall cabinets (a wall cabinet is built from z = 0 of
  its frame; ``furniture.py`` hangs it at ``mount_bottom_m``).
- Cabinet fronts (``cabinet_fronts``) in the design's front style: flat slab,
  shaker (a frame on a recessed panel), slatted (vertical slats on a dark
  backing), glass (a pane in a frame); bar handles on every front (key
  ``handle``), the fronts on key ``front``; the kitchen counter run and island
  keep their Milestone 6 boxes with these fronts; a washbasin with
  ``design.vanity`` is a wall-hung vanity under a ceramic top, a wardrobe
  with ``design.built_in`` has fronts from wall to wall; ``glass`` / ``marble``
  material tags give a table its top, ``metal`` steel legs. Builders that read
  the piece (its design, its L shape) are in ``_PIECE_BUILDERS``; every box of
  the Milestone 5 types is unchanged.
- Doors and windows (``door_parts``, ``window_parts``): pure parts in the
  opening's frame for the shell (every door style of ``DOOR_STYLES``; frames by
  material with mullions, transoms and an inside sill).
- The 12 new decor types (``_new_decor_parts``): open pleated curtains under a
  rod, a roller blind, a throw, a book stack, candles (a ``bulb`` flame each),
  a basket, a tray, a wall clock, a sculpture, a large plant of its species in
  its pot (key ``pot``), a pendant on its cord and a flush ceiling light; keys
  ``colour_*`` take the item's colour name.

Milestone 12 (docs/milestone12.md §4.7, §6.4; track S):

- Our kitchen and bath fixtures in standard sizes (the fit builds them when no audited model fits, by design):
  a full-size fridge-freezer (carcass, ventilation plinth, freezer and fridge doors with 3 mm gaps and bar handles
  inside the footprint), a front-loading washing machine (top plate, kick plate, control panel with drawer, display
  and dial, a porthole of glass over the dark drum in a chrome ring) and a shower (white tray with a drain, a glass
  front of a fixed panel and a door, glass sides in chrome profiles, a stabiliser rail, a riser, an arm with a rain
  head and a mixer).
- Cushions, throws, curtains and blinds are our procedural textiles (``wenart.blender.textiles``: a filled cushion,
  standing or lying; a cloth with folds; pleated curtain panels; roller or slatted blinds).
- No type-table rest height for decor (``decor_rest_height`` removed): decor rests on the built mesh
  (``wenart.blender.rest``).

Milestone 13 (docs/milestone13.md §3.0 K1, §12 D4, §13.2; track T2): the parametric families v2 (``FAMILY_TYPES``),
the last step of the fallback ladder (library model -> module builder of ``wenart.blender.modules`` -> family),
which must look like a real product, never a flat grey box:

- bed: a frame of side rails on the footprint's edges, foot and head rails, four legs and a deck, a headboard of
  two wooden posts with an upholstered panel (key ``fabric``: the brief's fabric colour), a superellipsoid mattress
  inside the rails (a real frame is wider than its mattress) and the textile bedding (``bed_bedding_parts``: the
  duvet is a cloth grid of ``cloth_solid`` laid on the mattress top with the modelled folds of ``fold`` and hanging
  down the mattress sides and foot to the rails' ledge, a turned-down band, pillows of ``lying_cushion_mesh``
  leaning ``PILLOW_TILT_DEG`` on the headboard; the constants ``DUVET_SHARE``, ``PILLOW_SIZE`` ... that
  ``wenart.blender.textiles`` re-exports); the frame and the mattress keep the Milestone 4 box the camera search's
  height profile reads (``camsearch.PROFILES``: roles ``body`` and ``mattress``, the posts as ``back``);
- sofa and armchair: an upholstered base on tapered wooden legs, arms, a back frame, rounded seat cushions and
  leaning back cushions (superellipsoids, role ``back_cushion``);
- tables (dining, coffee, desk, console): a ``TABLE_TOP_M`` top on an apron, tapered legs on steel feet, a lower
  shelf for coffee tables, the desk's drawer block; glass / marble tops and metal legs from the design tags as before;
- nightstand and dresser: a recessed plinth, a carcass, a top with drawer fronts and handles in the design's
  front style; tv unit: a low carcass on steel legs with drawer fronts; bookshelf: plinth, sides, a painted back
  panel and shelves; wardrobe: plinth, carcass, top and 0.50 m door modules with vertical handles.
- chair (round 4, docs/milestone13.md §14.8; ``chair_parts``): four legs on floor glides with seat rails, or a
  steel sled base for a ``metal`` design; an upholstered pad on a seat board (or a shaped wooden / rattan seat) with
  its top at 0.45 m; a back of two posts, a top rail and a back panel on the rear band the camera search models.
  The long table module builds its chairs with it (``build_parts("chair")``).

Every family gives the object several material slots (wood, fabric, bedding, front, handle, dark, steel, painted)
and keeps its box: the XY box equals the footprint within 1 cm, the lowest point is on the floor, ``back`` parts
touch +Y, fronts and handles sit on -Y (the Bevel modifier of ``furniture.add_bevel`` rounds the edges by role).
``piece_bbox`` reads a module plan (``asset.method == "module"``, ``asset.module_plan``) through
``wenart.blender.modules.plan_bbox``.

Fix round after P4b (17 Oct 2026): ``stair_parts`` builds a stair's steps, riser plates and landing to the walls its
``plan["wall_joints"]`` names (``shell.stair_wall_joints``; ``landing_with_joints``), so no slit is left between a
stair and its wall; a plan without joints is built as before.

29 Oct 2026 (user on real06 run 20261028-154514-full, lesson UL93: "Computer on the table would have been nice or a
laptop"; the catalogue holds no usable laptop, monitor or keyboard model): the desk's work set (``work_set_parts``)
at the item's real box (bottom on z = 0, front -Y = the side its user sits at), with PBR keys: an open laptop (an
aluminium base ``LAPTOP_BASE_T`` thick with a dark key field and a trackpad, the lid opened ``LAPTOP_OPEN_DEG`` with a
dark bezel and the ``screen``: a dark glossy panel with a faint lit wallpaper, ``materials.screen_material``), a
monitor on its stand (foot, neck, dark panel, screen), a keyboard (an aluminium plate with key rows and a space bar)
and a computer mouse. ``laptop_box`` is the open laptop's box from its base.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

from wenart import geometry as G
from wenart.blender import geom2d
from wenart.blender.proxies import proxy_height

Part = dict  # {"verts": [(x, y, z)], "faces": [[i, ...]], "key": str, "role": str}

# Furniture types with a parametric builder (every type of the building
# schema except ``unknown``, which keeps the striped Milestone 3 proxy box).
PARAMETRIC_TYPES: tuple[str, ...] = (
    "bed", "bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee", "desk", "chair",
    "wardrobe", "dresser", "nightstand", "tv_unit", "bookshelf", "kitchen_counter", "kitchen_island",
    "fridge", "stove", "sink_kitchen", "washbasin", "toilet", "shower", "bathtub", "washing_machine",
    # Milestone 7 documented-only types (docs/milestone7.md §6.4).
    "stair", "side_table", "floor_lamp", "potted_plant",
    # Milestone 10 (docs/milestone10.md §1.1): the corner sofa, seating, tables, children's beds and cabinets.
    "sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib", "bunk_bed",
    "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet",
)
# Built by shell.build_stairs with the walls (fixed equipment), never by furniture.create_furniture.
SHELL_TYPES: tuple[str, ...] = ("stair",)
DECOR_TYPES: tuple[str, ...] = ("cushion", "book_set", "plant", "rug",   # parametric decor builders (M8: rug)
                                 # Milestone 9 (docs/milestone9.md §3): tabletop decor and the framed wall mirror
                                 "vase", "bowl", "plant_small", "table_lamp", "mirror",
                                 # Milestone 10 (docs/milestone10.md §4.6)
                                 "curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock", "sculpture",
                                 "plant_large", "pendant_light", "ceiling_light",
                                 # 28 Oct 2026 (wenart.furniture.tabletop): a dining table's place settings
                                 "plate", "glass",
                                 # 28 Oct 2026 (user: "kettle in the kitchen, microwave in the kitchen etc"): the
                                 # kitchen worktop's small appliances and decor (``kitchen_worktop_parts``)
                                 "microwave", "kettle", "coffee_machine", "toaster", "chopping_board", "utensil_pot",
                                 "fruit_bowl",
                                 # 29 Oct 2026 (lessons UL115, UL118: the reference kitchens' styled worktops): the
                                 # styling sets (``kitchen_details.styling_parts``, one mesh per set)
                                 "storage_jars", "plate_stack", "cookware", "cutting_boards", "oil_bottles",
                                 "dried_grass_vase", "coffee_station",
                                 # 29 Oct 2026 (user: "Computer on the table would have been nice or a laptop"): the
                                 # desk's work set (``work_set_parts``)
                                 "laptop", "monitor", "keyboard", "computer_mouse")
KITCHEN_DECOR_TYPES: tuple[str, ...] = DECOR_TYPES[DECOR_TYPES.index("microwave"):DECOR_TYPES.index("coffee_station") + 1]
STYLING_DECOR_TYPES: tuple[str, ...] = DECOR_TYPES[DECOR_TYPES.index("storage_jars"):
                                                   DECOR_TYPES.index("coffee_station") + 1]
WORK_DECOR_TYPES: tuple[str, ...] = DECOR_TYPES[DECOR_TYPES.index("laptop"):]
_NEW_DECOR: tuple[str, ...] = DECOR_TYPES[DECOR_TYPES.index("curtain"):]
# Milestone 10 storage built with the cabinet fronts of the design (a design detail of the piece).
CABINET_LOOK_TYPES: tuple[str, ...] = ("sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")
# Decor without the 0.6 m cap (Milestone 8): a rug under a group of pieces, a picture over a sofa; M9: a mirror;
# M10: curtains and blinds by window size, a throw over a bed's foot, large plants and floor sculptures, pendants
# on their cord.
LARGE_DECOR_TYPES: tuple[str, ...] = ("rug", "wall_art", "mirror", "curtain", "blind", "throw", "plant_large",
                                      "sculpture", "pendant_light")
# Decor that rests on its host's built top (Milestone 9: the builder casts a ray down onto the host mesh).
SURFACE_DECOR_TYPES: tuple[str, ...] = ("vase", "bowl", "plant_small", "table_lamp",
                                        "candle", "tray", "books", "sculpture", "basket",   # M10, with a host
                                        # 28 Oct 2026: the kitchen worktop items rest on the built worktop
                                        "microwave", "kettle", "coffee_machine", "toaster", "chopping_board",
                                        "utensil_pot", "fruit_bowl",
                                        # 29 Oct 2026 (UL115, UL118): the worktop styling sets
                                        "storage_jars", "plate_stack", "cookware", "cutting_boards", "oil_bottles",
                                        "dried_grass_vase", "coffee_station",
                                        "plate", "glass",                                   # 28 Oct 2026
                                        # 29 Oct 2026: the desk's work set rests on the built desk top
                                        "laptop", "monitor", "keyboard", "computer_mouse")
# Seats decor rests on at seat height (cushions, a throw): Milestone 10 adds the corner sofa, chaise and bench.
SEAT_HOST_TYPES: tuple[str, ...] = ("sofa", "armchair", "sofa_corner", "chaise")
MATERIAL_KEYS: tuple[str, ...] = ("wood", "fabric", "bedding", "ceramic", "steel", "painted", "worktop", "dark",
                                  "glass", "green", "terracotta", "duvet", "mirror",
                                  # Milestone 10: cabinet fronts and handles of the design, table tops of a material
                                  # tag, plant pots, lamp bulbs (lit in the interior evening mood), rattan
                                  "front", "handle", "marble", "pot", "bulb", "rattan",
                                  # 29 Oct 2026: a laptop's or a monitor's screen (``materials.screen_material``)
                                  "screen",
                                  # 29 Oct 2026 (UL120): a see-through wardrobe's smoked glass (library.smoked_glass)
                                  "smoked_glass")
# Milestone 10 doors and windows (``door_parts`` / ``window_parts``; shell.py maps them to the looks).
OPENING_KEYS: tuple[str, ...] = ("frame", "leaf", "glass", "handle", "rail", "sill")
# Parts whose key starts with this take the item's colour (Milestone 9 AI decor: ``decor.colour``) as a tint of
# the key's material: ``accent_ceramic`` = the ceramic material tinted.
ACCENT_PREFIX = "accent_"
# The colours the AI decor names (docs/milestone9.md §4), linear RGB; a tint of the white ceramic or fabric.
DECOR_COLOURS: dict[str, tuple[float, float, float]] = {
    "white": (0.80, 0.80, 0.78), "cream": (0.74, 0.68, 0.55), "beige": (0.60, 0.52, 0.40),
    "sand": (0.55, 0.45, 0.30), "light grey": (0.50, 0.50, 0.50), "grey": (0.25, 0.25, 0.25),
    "charcoal": (0.06, 0.06, 0.065), "black": (0.02, 0.02, 0.02), "natural wood": (0.42, 0.26, 0.13),
    "terracotta": (0.45, 0.14, 0.06), "rust": (0.35, 0.09, 0.03), "mustard": (0.60, 0.40, 0.04),
    "olive": (0.18, 0.20, 0.06), "sage green": (0.30, 0.38, 0.27), "forest green": (0.04, 0.12, 0.05),
    "navy": (0.02, 0.04, 0.13), "dusty blue": (0.25, 0.33, 0.45), "teal": (0.02, 0.20, 0.20),
    "blush": (0.70, 0.42, 0.38), "burgundy": (0.18, 0.02, 0.04), "brass": (0.55, 0.40, 0.12),
    "copper": (0.55, 0.25, 0.12),
}
BED_TYPES: tuple[str, ...] = ("bed", "bed_single", "bed_double")
COUNTER_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
# Milestone 13 (docs/milestone13.md §13.2): the types with a v2 family (real proportions, several material slots,
# bevelled edges); the fit's ladder builds them when no library model and no module plan fits.
FAMILY_TYPES: tuple[str, ...] = ("bed", "bed_single", "bed_double", "sofa", "armchair", "table_dining", "table_coffee",
                                 "desk", "nightstand", "dresser", "bookshelf", "tv_unit", "wardrobe",
                                 # round 4 (§14.8): the chair (``chair_parts``), was the one-material box chair
                                 "chair")
# Bed v2 and the textile bedding (docs/milestone12.md §4.7 "every bed whose model has no bedding gets a duvet and two
# pillows"; the numbers of wenart.blender.textiles since Milestone 12, kept here so the pure bed family and the
# draped bedding of a library bed share them).
DUVET_SHARE = 0.75                # the duvet covers the foot 75 % of the mattress
DUVET_SIDE_DROP_M = 0.30          # it reaches this far past the mattress sides and the foot (hangs down)
DUVET_THICKNESS_M = 0.04
TURN_DOWN_M = 0.28                # the band folded back at the duvet's head end
PILLOW_SIZE = (0.65, 0.15, 0.45)  # a sleeping pillow: width across the bed, thickness, length along the bed
TWO_PILLOW_MIN_W = 1.30           # beds at least this wide take two pillows side by side
BED_DUVET_M = 0.02                # the parametric bed's duvet is thinner than a draped one (DUVET_THICKNESS_M): it
                                  # hangs in the gap between the mattress and the rails, down to the rails' ledge
BED_PLINTH_M = 0.10               # the recessed plinth under the rails of the platform bed (its "floating" base)
BED_PLINTH_RECESS_M = 0.05
BED_RAIL_M = 0.03                 # side rail thickness: the rails are the footprint's outer edges (the frame)
BED_FOOT_RAIL_M = 0.03
BED_MATTRESS_GAP_M = 0.03         # between the mattress and the rails' inner faces: the hanging duvet (CLOTH_OFFSET_M
                                  # + BED_DUVET_M) and 5 mm of air; rail + gap = 6 cm: a real frame is that much
                                  # wider than its mattress per side (wenart/recognition/size_table.yaml bed_double:
                                  # Movian Loue 160 x 200 mattress in a 1.72 x 2.06 frame)
PILLOW_LENGTH_SHARE = 0.25        # a pillow is never longer than a quarter of the mattress (a bed drawn sideways, real03
                                  # f_L0_061 1.95 x 0.95, keeps room for the duvet and for cushions on the headboard)
# Table v2: a real top (contract: "proper top thickness"), an apron under it, tapered legs on steel feet.
TABLE_TOP_M = 0.04
TABLE_APRON_M = 0.08
TABLE_FOOT_M = 0.015
# Sofa v2: legs, cushions.
SOFA_LEG_M = 0.10
SOFA_CUSHION_M = 0.14
BACK_CUSHION_T_M = 0.20
BACK_CUSHION_LEAN_DEG = 8.0
# Drawer units (nightstand, dresser, tv unit): drawer pitch and the smallest drawer front.
DRAWER_PITCH_M = 0.20
DRAWER_MIN_M = 0.12
# Kitchen fronts: this gap between the carcass front face and the back of a front.
FRONT_GAP = 0.001
FRONT_THICKNESS = 0.018
# Pillows lean back on the headboard by this angle.
PILLOW_TILT_DEG = 14.0
# Bevel (docs/milestone6.md §5 row 8): one Bevel modifier per piece, limit
# method WEIGHT, width BEVEL_WIDTH_M, BEVEL_SEGMENTS segments; every edge gets
# weight = radius / BEVEL_WIDTH_M from its part (furniture.py). Radii in
# metres per part role; fabric and bedding parts are soft whatever their role.
BEVEL_WIDTH_M = 0.05
BEVEL_SEGMENTS = 3
BEVEL_DEFAULT_M = 0.004
BEVEL_BY_ROLE: dict[str, float] = {
    "pillow": 0.045, "cushion": 0.035, "top": 0.004, "body": 0.006, "back": 0.008, "arm": 0.03, "front": 0.003,
    "handle": 0.002, "leg": 0.003, "shelf": 0.002, "side": 0.003, "bottom": 0.002, "drawers": 0.003,
    "plinth": 0.002, "tray": 0.01, "basin": 0.008, "pedestal": 0.02,
    # Milestone 7
    "step": 0.003, "riser": 0.002, "landing": 0.003, "rail": 0.008, "post": 0.004, "base": 0.006,
    "spandrel": 0.002, "landing_post": 0.004,                     # 27 Oct 2026: the closed underside of a stair
    "pole": 0.0, "shade": 0.004,
    # Milestone 10
    "panel": 0.002, "rod": 0.0, "roller": 0.0, "slat": 0.002, "castor": 0.004, "rest": 0.003, "ladder": 0.004,
    "leaf": 0.003, "frame": 0.002, "mullion": 0.002, "transom": 0.002, "sill": 0.003, "rim": 0.003, "book": 0.003,
    "candle": 0.0, "plate": 0.0, "canopy": 0.0, "cord": 0.0,
    # Milestone 13 families v2 and module builders
    "apron": 0.003, "foot": 0.002, "stretcher": 0.004, "trestle": 0.004, "hob": 0.0, "ring": 0.0,
    # 29 Oct 2026: the desk's work set (rounded laptop and monitor shells; flat screens, keys and pads)
    "lid": 0.003, "bezel": 0.0, "screen": 0.0, "keys": 0.0, "key": 0.0008, "trackpad": 0.0, "hinge": 0.0,
    "panel_back": 0.004, "neck": 0.003, "space_bar": 0.0008,
}
BEVEL_SOFT_KEYS: dict[str, float] = {"fabric": 0.03, "bedding": 0.03, "duvet": 0.03}
BEVEL_BY_KEY: dict[str, float] = {"ceramic": 0.012}

# How far a handle or a door may stand proud of the footprint (metres);
# the tests allow 1 cm.
PROUD = 0.008
# Largest decor dimension (docs/milestone4.md, Conventions: never larger than 0.6 m).
DECOR_MAX_M = 0.6
DECOR_DEFAULT_HEIGHT = {"cushion": 0.12, "book_set": 0.22, "plant": 0.6, "rug": 0.012, "wall_art": 0.6,
                        # Milestone 9
                        "vase": 0.30, "bowl": 0.10, "plant_small": 0.35, "table_lamp": 0.50, "mirror": 0.80,
                        # Milestone 10 (typical sizes, assumed)
                        "curtain": 2.4, "blind": 1.3, "throw": 0.05, "books": 0.12, "candle": 0.2, "basket": 0.35,
                        "tray": 0.04, "clock": 0.35, "sculpture": 0.4, "plant_large": 1.6, "pendant_light": 0.6,
                        "ceiling_light": 0.12,
                        # 28 Oct 2026: real products (a 20 l countertop microwave 45-49 x 33-40 x 26-30 cm, a 1.7 l
                        # kettle 22 x 16 x 25 cm, a bean-to-cup machine 24 x 43 x 35 cm, a 2-slice toaster 28 x 17 x
                        # 19 cm, a 40 x 25 cm board, a utensil pot with its tools, a 28 cm fruit bowl)
                        "microwave": 0.27, "kettle": 0.25, "coffee_machine": 0.35, "toaster": 0.19,
                        "chopping_board": 0.02, "utensil_pot": 0.30, "fruit_bowl": 0.12,
                        # 29 Oct 2026: the styling sets (kitchen_details.STYLING_SIZES: real products)
                        "storage_jars": 0.24, "plate_stack": 0.14, "cookware": 0.18, "cutting_boards": 0.45,
                        "oil_bottles": 0.30, "dried_grass_vase": 0.55, "coffee_station": 0.38,
                        "plate": 0.025, "glass": 0.14,           # 28 Oct 2026: a dinner plate, a water glass
                        # 29 Oct 2026: an open 14-15 inch laptop (``laptop_box``), a 24 inch monitor on its stand, a
                        # full-size keyboard, a mouse
                        "laptop": 0.24, "monitor": 0.45, "keyboard": 0.025, "computer_mouse": 0.038}
MIRROR_FRAME_M = 0.03            # the parametric mirror: frame width and depth; the glass sits on its front
RUG_THICKNESS_M = 0.012
# Bed frames (Milestone 8): the mattress on the deck and the inner box the bedding fills.
FRAME_MATTRESS_M = 0.20
FRAME_INSET = 0.04
SHELF_PITCH = 0.35


# --------------------------------------------------------------------------
# Primitive helpers (local frame, z from the floor)
# --------------------------------------------------------------------------

def _box(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str = "body") -> Part:
    verts, faces = geom2d.box((cx, cy, z0 + h / 2.0), (w, d, h), 0.0)
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _cylinder_z(cx: float, cy: float, z0: float, rx: float, ry: float, h: float, key: str, role: str = "body",
                n: int = 24) -> Part:
    """Elliptic cylinder along Z (outward normals: side quads ccw, top cap ccw
    seen from above, bottom cap reversed)."""
    bottom = [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n), z0) for i in range(n)]
    top = [(x, y, z0 + h) for x, y, _ in bottom]
    verts = bottom + top
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n, 2 * n)))           # top, ccw from above
    faces.append(list(range(n - 1, -1, -1)))      # bottom, reversed
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _cylinder_y(cx: float, y0: float, cz: float, rx: float, rz: float, length: float, key: str,
                role: str = "body", n: int = 24) -> Part:
    """Elliptic cylinder along +Y from ``y0`` to ``y0 + length`` (a rotated
    Z cylinder: the rotation keeps the winding, so normals stay outward)."""
    part = _cylinder_z(0.0, 0.0, 0.0, rx, rz, length, key, role, n)
    # rotate about X by -90 degrees: (x, y, z) -> (x, z, -y), so +Z -> +Y
    part["verts"] = [(cx + x, y0 + z, cz - y) for x, y, z in part["verts"]]
    return part


def _bbox(parts: Sequence[Part]) -> tuple[float, float, float, float, float, float]:
    xs = [v[0] for p in parts for v in p["verts"]]
    ys = [v[1] for p in parts for v in p["verts"]]
    zs = [v[2] for p in parts for v in p["verts"]]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


def parts_bbox(parts: Sequence[Part]) -> tuple[float, float, float, float, float, float]:
    """``(min_x, min_y, min_z, max_x, max_y, max_z)`` of the parts."""
    return _bbox(parts)


# --------------------------------------------------------------------------
# Type builders. All take (w, d, h) = footprint width, depth, type height.
# --------------------------------------------------------------------------

def _sgnpow(v: float, e: float) -> float:
    return math.copysign(abs(v) ** e, v)


def _superellipsoid(cx: float, cy: float, z0: float, w: float, d: float, h: float, e_vert: float, e_horiz: float,
                    key: str, role: str, n_eta: int = 12, n_om: int = 32, wrinkle: float = 0.0, seed: float = 0.0,
                    tilt_deg: float = 0.0) -> Part:
    """Closed superellipsoid in the box ``w x d x h`` standing on ``z0`` and
    centred on ``(cx, cy)``; the box is exact (the rings pass through the
    poles, the equator and the four axis directions: ``n_eta`` even,
    ``n_om`` a multiple of 4). ``e_vert`` < 1 flattens the top and bottom
    (duvet 0.18, pillow 0.55), ``e_horiz`` < 1 squares the corners.
    ``wrinkle`` (metres) adds a smooth deterministic bump field to the upper
    half, clamped inside the box. ``tilt_deg`` turns the part about its
    centre's X axis so its +Y end rises (a pillow propped up on the
    headboard) and lifts it back onto ``z0`` (its box then turns with it).
    Outward normals; ``"smooth": True``."""
    a, b, c = w / 2.0, d / 2.0, h / 2.0
    t = math.radians(tilt_deg)
    ct, st = math.cos(t), math.sin(t)

    def place(x: float, y: float, z: float) -> tuple[float, float, float]:
        if tilt_deg:
            y, z = y * ct - z * st, y * st + z * ct
        return (cx + x, cy + y, z0 + c + z)

    verts = [place(0.0, 0.0, -c)]                  # bottom pole
    rings = []
    for i in range(1, n_eta):
        eta = -math.pi / 2.0 + math.pi * i / n_eta
        ring = []
        for j in range(n_om):
            om = -math.pi + 2.0 * math.pi * j / n_om
            x = a * _sgnpow(math.cos(eta), e_vert) * _sgnpow(math.cos(om), e_horiz)
            y = b * _sgnpow(math.cos(eta), e_vert) * _sgnpow(math.sin(om), e_horiz)
            z = c * _sgnpow(math.sin(eta), e_vert)
            if wrinkle and z > 0:
                bump = (math.sin(7.0 * x / max(a, 1e-6) + seed) * math.sin(5.0 * y / max(b, 1e-6) + 1.3 * seed)
                        + 0.5 * math.sin(13.0 * (x + y) / max(a + b, 1e-6) + 2.1 * seed))
                z = max(-c, min(c, z + wrinkle * bump * (z / c)))
            ring.append(len(verts))
            verts.append(place(x, y, z))
        rings.append(ring)
    top = len(verts)
    verts.append(place(0.0, 0.0, c))               # top pole
    faces = []
    first = rings[0]
    for j in range(n_om):                          # bottom fan (outward = down)
        faces.append([0, first[(j + 1) % n_om], first[j]])
    for r0, r1 in zip(rings, rings[1:]):
        for j in range(n_om):
            faces.append([r0[j], r0[(j + 1) % n_om], r1[(j + 1) % n_om], r1[j]])
    last = rings[-1]
    for j in range(n_om):
        faces.append([last[j], last[(j + 1) % n_om], top])
    if tilt_deg:                                   # keep the lowest point on z0 after the lean
        zmin = min(v[2] for v in verts)
        verts = [(x, y, z - (zmin - z0)) for x, y, z in verts]
    return {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True}


def _bed(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Bed v2 (Milestone 13): a platform bed. A wooden frame whose side rails are the footprint's outer edges over
    the full length, a foot rail and a head rail between them on a recessed dark plinth, a deck; a headboard of
    two posts on the rails' rear ends with an upholstered panel between them (``fabric``, the brief's colour; role
    ``panel``, recessed 4 mm); a superellipsoid mattress ``BED_RAIL_M + BED_MATTRESS_GAP_M`` inside the rails (a
    real frame is wider than its mattress) and the textile bedding of ``bed_bedding_parts``: the duvet over the
    foot of the mattress hanging into the gap down to the rails' ledge (``frame_h``, never below: the bedding stays
    inside the Milestone 6 bed box), a turn-down band, pillows leaning on the headboard. Touching parts keep
    ``FRONT_GAP`` (1 mm) between them, so no two faces share a plane (Milestone 10: coplanar faces rendered
    black). The box is the Milestone 4 one: the footprint, the headboard top at ``max(1.0, h + 0.4)``, the
    mattress top at the type height ``h``; the frame (role ``body``) and the mattress span the footprint up to
    ``h`` and the posts (``back``) reach the rear edge, as the camera search's height profile
    (``camsearch.PROFILES``) reads them."""
    g = FRONT_GAP
    t = min(0.06, d * 0.05)                       # headboard thickness (posts and panel)
    frame_h = min(0.3, h * 0.55)                  # the rails' top: the ledge the mattress and the duvet rest on
    top = max(1.0, h + 0.4)                       # headboard top
    leg_h = min(BED_PLINTH_M, frame_h * 0.4)      # the plinth's top = the rails' bottom
    rail = min(BED_RAIL_M, w * 0.04)
    foot = min(BED_FOOT_RAIL_M, rail)
    gap = BED_MATTRESS_GAP_M
    y_foot, y_head = -d / 2.0 + foot, d / 2.0 - t  # the frame's inner span: foot rail to the headboard's front face
    parts: list[Part] = []
    for sx in (-1, 1):                            # side rails: the footprint's edges, the full length
        parts.append(_box(sx * (w / 2.0 - rail / 2.0), 0.0, leg_h, rail, d, frame_h - leg_h, "wood", "body"))
    parts.append(_box(0.0, -d / 2.0 + foot / 2.0, leg_h, w - 2 * rail - 2 * g, foot, frame_h - leg_h, "wood",
                      "body"))                     # foot rail
    parts.append(_box(0.0, d / 2.0 - t / 2.0, leg_h, w - 2 * rail - 2 * g, t, frame_h - leg_h, "wood", "body"))
    parts.append(_box(0.0, (y_foot + y_head) / 2.0, frame_h - 0.03 - g, w - 2 * rail - 2 * g, y_head - y_foot - 2 * g,
                      0.03, "wood", "bottom"))    # the deck between the rails
    recess = min(BED_PLINTH_RECESS_M, w * 0.05, d * 0.05)
    parts.append(_box(0.0, 0.0, 0.0, w - 2 * recess, d - 2 * recess, leg_h - g, "dark", "plinth"))
    post = min(0.05, rail + 0.01)
    for sx in (-1, 1):                            # headboard posts on the rails' rear ends
        parts.append(_box(sx * (w / 2.0 - post / 2.0), d / 2.0 - t / 2.0, frame_h + g, post, t, top - frame_h - g,
                          "wood", "back"))
    parts.append(_box(0.0, d / 2.0 - t / 2.0, frame_h + g, w - 2 * post - 2 * g, t - 0.008, top - 0.03 - frame_h - g,
                      "fabric", "panel"))         # the upholstered panel between the posts, recessed 4 mm
    mw = w - 2 * (rail + gap)
    m_y0, m_y1 = y_foot + gap, y_head - 0.01
    md, my = m_y1 - m_y0, (m_y0 + m_y1) / 2.0
    parts.append(_superellipsoid(0.0, my, frame_h, mw, md, h - frame_h, 0.12, 0.08, "bedding", "mattress"))
    # the duvet's cloth grid stops BED_DUVET_M above the ledge: its underside (the solid's bottom layer) rests on it
    parts += bed_bedding_parts(w, mw, md, my, top_z=h, head_y=y_head, lowest_z=frame_h + BED_DUVET_M)
    return parts


def _tilt_x(verts, deg: float, pivot_y: float, pivot_z: float = 0.0):
    """Points turned about the X axis through ``(pivot_y, pivot_z)`` by ``deg`` (positive: +Y rises)."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [(x, pivot_y + (y - pivot_y) * c - (z - pivot_z) * s, pivot_z + (y - pivot_y) * s + (z - pivot_z) * c)
            for x, y, z in verts]


def box_drape_grid(rect, box_x: float, box_y0: float, box_y1: float, top_z: float, drop: float,
                   step: float = None, offset: float = None, thickness: float = BED_DUVET_M) -> np.ndarray:
    """A cloth grid over ``rect`` = (x0, y0, x1, y1) laid on a box top (``|x| <= box_x``, ``box_y0 <= y <=
    box_y1``) at ``top_z`` (pure, no rays: the analytic twin of ``textiles.drape`` for a host whose top is a known
    box): on the top the cloth lies ``offset + thickness`` above it with the modelled folds of ``fold``; a point
    beyond the sides or the foot (``y < box_y0``) hangs straight down beside the box by the length it reaches past
    the edge (at a corner the larger of its two overhangs: a level hem), at most ``drop``, pushed
    ``offset + thickness`` out of the box's side."""
    step = CLOTH_STEP_M if step is None else step
    offset = CLOTH_OFFSET_M if offset is None else offset
    x0, y0, x1, y1 = (float(v) for v in rect)
    nu = max(2, int(round((x1 - x0) / step)))
    nv = max(2, int(round((y1 - y0) / step)))
    out = offset + thickness
    grid = np.zeros((nu + 1, nv + 1, 3))
    w, d = x1 - x0, y1 - y0
    for i in range(nu + 1):
        for j in range(nv + 1):
            x = x0 + w * i / nu
            y = y0 + d * j / nv
            dx = max(0.0, abs(x) - box_x)
            dy = max(0.0, box_y0 - y, y - box_y1)
            reach = math.hypot(dx, dy)
            if reach <= 1e-9:
                grid[i, j] = (x, y, top_z + out + fold(x - x0, y - y0, w, d))
                continue
            # the nearest point of the box edge and the outward direction from it: at a corner the hanging
            # points fan around it (as the ray drape does), so no two grid points coincide
            ex = math.copysign(box_x, x) if dx > 0 else x
            ey = (box_y0 if y < box_y0 else box_y1) if dy > 0 else y
            ux, uy = (x - ex) / reach, (y - ey) / reach
            # the hang length is the larger overhang, not the diagonal distance (reviewer fix 15 Oct 2026): with the
            # diagonal, two grid points on one ray from a corner both reached ``drop`` and coincided (degenerate faces
            # on every 1.20 m wide bed); max(dx, dy) grows strictly along a ray, so no two points coincide
            grid[i, j] = (ex + ux * out, ey + uy * out, top_z + out - min(max(dx, dy), drop))
    return grid


def bed_bedding_parts(w: float, mw: float, md: float, my: float, top_z: float, head_y: float,
                      lowest_z: float = 0.05) -> list[Part]:
    """The textile bedding of the parametric bed in the piece frame (pure): the duvet (``cloth_solid`` of
    ``box_drape_grid``: over the foot ``DUVET_SHARE`` of the mattress top at ``top_z``, hanging
    ``DUVET_SIDE_DROP_M`` down the sides and the foot but never below ``lowest_z``), the turn-down band at its head
    end and one or two pillows (``lying_cushion_mesh`` leaning ``PILLOW_TILT_DEG`` against the headboard at
    ``head_y``; ``TWO_PILLOW_MIN_W``; never longer than ``PILLOW_LENGTH_SHARE`` of the mattress). The mattress box: half width ``mw / 2`` about x = 0, ``md`` deep about
    ``my``; the duvet stays inside the footprint width ``w``."""
    out = CLOTH_OFFSET_M + BED_DUVET_M
    box_x = mw / 2.0
    y_foot = my - md / 2.0
    y_head = y_foot + DUVET_SHARE * md
    n = 2 if w >= TWO_PILLOW_MIN_W - 1e-9 else 1
    pw = min(PILLOW_SIZE[0], (mw - 0.1) / n - 0.04)
    pt, pl = PILLOW_SIZE[1], min(PILLOW_SIZE[2], md * PILLOW_LENGTH_SHARE)
    a = PILLOW_TILT_DEG
    pillow_foot = head_y - 0.02 - pl                 # the pillow lies from here to the headboard
    y_head = min(y_head, pillow_foot - 0.03)
    drop = max(0.0, min(DUVET_SIDE_DROP_M, top_z + out - lowest_z))
    rect = (-box_x - drop, y_foot - drop, box_x + drop, y_head)
    grid = box_drape_grid(rect, box_x, y_foot, my + md / 2.0, top_z, drop)
    parts = [cloth_solid(grid, BED_DUVET_M, key="duvet", role="duvet")]
    nv = grid.shape[1] - 1
    js = [j for j in range(nv + 1) if rect[1] + (rect[3] - rect[1]) * j / nv >= y_head - TURN_DOWN_M - 1e-9]
    is_ = [i for i in range(grid.shape[0]) if abs(grid[i, 0, 0]) <= box_x + 1e-9]
    if len(js) >= 2 and len(is_) >= 2:
        sub = grid[is_[0]:is_[-1] + 1, js[0]:js[-1] + 1].copy()
        sub[..., 2] += BED_DUVET_M * 0.5 + CLOTH_OFFSET_M
        parts.append(cloth_solid(sub, BED_DUVET_M * 0.6, key="bedding", role="turndown"))
    for k in range(n):
        px = 0.0 if n == 1 else (-1 if k == 0 else 1) * (pw / 2.0 + 0.02)
        pillow = lying_cushion_mesh(pw, pl, pt, key="bedding", role="pillow")
        verts = _tilt_x(pillow["verts"], a, -pl / 2.0, 0.0)
        verts = [(x + px, y + pillow_foot + pl / 2.0, z + top_z + CLOTH_OFFSET_M) for x, y, z in verts]
        parts.append(dict(pillow, verts=verts))
    return parts


def bedding_top(w: float, d: float, h: float) -> float:
    """Height of the highest bedding point of a parametric bed (pillows, duvet, band)."""
    return max(v[2] for p in _bed(float(w), float(d), float(h)) if p["key"] in ("bedding", "duvet")
               for v in p["verts"])


def frame_inner_box(w: float, d: float, inset: float = FRAME_INSET) -> tuple[float, float]:
    """``(width, depth)`` of a bed frame's inner box: the footprint minus ``inset`` (a share) per side."""
    return (float(w) * (1.0 - 2.0 * inset), float(d) * (1.0 - 2.0 * inset))


def frame_bedding(w: float, d: float, deck_z: float, mattress_h: float = FRAME_MATTRESS_M,
                  inset: float = FRAME_INSET) -> list[Part]:
    """The parametric bedding on a library bed frame of footprint ``w x d`` (docs/milestone8.md §4), in the
    piece frame (origin at the footprint centre on the floor, foot = -Y, head = +Y): the ``_bed`` mattress,
    duvet, turn-down band and pillows with the same shapes, keys and roles, but the mattress fills the
    frame's inner box (``frame_inner_box``, centred) from ``deck_z`` up ``mattress_h`` (its top at
    ``deck_z + mattress_h``), the duvet drapes 2.5 cm past the mattress sides (never past the footprint)
    over its foot 72 %, the pillows lean at the head end of the inner box."""
    iw, idp = frame_inner_box(w, d, inset)
    deck_z, mattress_h = float(deck_z), float(mattress_h)
    top = deck_z + mattress_h
    parts = [_superellipsoid(0.0, 0.0, deck_z, iw, idp, mattress_h, 0.12, 0.08, "bedding", "mattress")]
    duvet_w = min(float(w), iw + 0.05)
    duvet_d = idp * 0.72
    duvet_y = -idp / 2.0 + 0.005 + duvet_d / 2.0
    drape = min(0.18, mattress_h * 0.9)
    parts.append(_superellipsoid(0.0, duvet_y, top - drape, duvet_w, duvet_d, drape + 0.05, 0.18, 0.06, "duvet",
                                 "duvet", n_eta=14, n_om=48, wrinkle=0.012, seed=1.7))
    parts.append(_superellipsoid(0.0, duvet_y + duvet_d / 2.0 - 0.13, top + 0.02, duvet_w - 0.02, 0.26, 0.05, 0.35,
                                 0.1, "bedding", "turndown", n_om=40))
    n = 2 if float(w) >= 1.3 else 1
    pw = (iw - 0.1) / n - 0.05
    pd = min(0.45, idp * 0.22)
    py = idp / 2.0 - 0.05 - pd / 2.0
    for i in range(n):
        px = 0.0 if n == 1 else (-1 if i == 0 else 1) * (pw / 2.0 + 0.025)
        parts.append(_superellipsoid(px, py, top - 0.01, pw, pd, 0.16, 0.55, 0.25, "bedding", "pillow",
                                     tilt_deg=PILLOW_TILT_DEG))
    return parts


def frame_bedding_info(w: float, d: float, deck_z: float, mattress_h: float = FRAME_MATTRESS_M,
                       inset: float = FRAME_INSET) -> dict:
    """The record of ``frame_bedding`` (the fit's ``asset.bedding``, the manifest's ``bedding``): deck and
    mattress top above the floor, the highest bedding point (pillows), the inner box and the rule."""
    parts = frame_bedding(w, d, deck_z, mattress_h, inset)
    iw, idp = frame_inner_box(w, d, inset)
    mattress = next(p for p in parts if p["role"] == "mattress")
    return {"deck_z_m": round(float(deck_z), 4), "mattress_m": float(mattress_h),
            "mattress_top_m": round(max(v[2] for v in mattress["verts"]), 4),
            "top_m": round(max(v[2] for p in parts for v in p["verts"]), 4),
            "inner_box_m": [round(iw, 4), round(idp, 4)], "inset": inset,
            "pillows": sum(1 for p in parts if p["role"] == "pillow")}


def _sofa(w: float, d: float, h: float, cushions: int | None = None, piece: dict | None = None) -> list[Part]:
    """Sofa v2 (Milestone 13; ``cushions=1``: the armchair): an upholstered base on four tapered wooden legs, two
    arms, a back frame up to ``h``, rounded seat cushions (one per 0.75 m of seat) and leaning back cushions
    (superellipsoids, role ``back_cushion``). The box: the footprint, ``h`` high, on the floor."""
    back_t = min(0.22, d * 0.25)
    arm_w = min(0.20, w * 0.12) if cushions != 1 else min(0.15, w * 0.15)
    seat_h = sofa_seat_height(h)
    leg_h = min(SOFA_LEG_M, h * 0.12)
    arm_h = min(0.65, h * 0.78)
    cushion_t = min(SOFA_CUSHION_M, (seat_h - leg_h) * 0.5)
    seat_w = w - 2 * arm_w
    seat_d = d - back_t
    parts = [
        _box(0.0, -back_t / 2.0, leg_h, seat_w, seat_d, seat_h - cushion_t - leg_h, "fabric", "body"),
        _box(0.0, d / 2.0 - back_t / 2.0, leg_h, w, back_t, h - leg_h, "fabric", "back"),
        _box(-(w / 2.0 - arm_w / 2.0), -back_t / 2.0, leg_h, arm_w, seat_d, arm_h - leg_h, "fabric", "arm"),
        _box((w / 2.0 - arm_w / 2.0), -back_t / 2.0, leg_h, arm_w, seat_d, arm_h - leg_h, "fabric", "arm"),
    ]
    r = min(0.03, w * 0.03, d * 0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_frustum_z(sx * (w / 2.0 - 0.06), sy * (d / 2.0 - 0.06), 0.0, r * 0.7, r * 0.7, r, r,
                                    leg_h - FRONT_GAP, "wood", "leg", n=12))     # 1 mm under the base
    n = cushions or max(1, round(seat_w / 0.75))
    cw = seat_w / n
    lean = math.radians(BACK_CUSHION_LEAN_DEG)
    bt = min(BACK_CUSHION_T_M, back_t)
    # the leaning back cushion's box turns with it: its height is chosen so the top meets h exactly
    bh = max(0.10, (h - seat_h + 0.02 - bt * math.sin(lean)) / math.cos(lean))
    for i in range(n):
        cx = -seat_w / 2.0 + cw * (i + 0.5)
        parts.append(_superellipsoid(cx, -back_t / 2.0, seat_h - cushion_t, cw - 0.02, seat_d - 0.03, cushion_t, 0.25,
                                     0.22, "fabric", "cushion", n_eta=10, n_om=32))
        parts.append(_superellipsoid(cx, d / 2.0 - back_t - bt / 2.0 + 0.01, seat_h - 0.02, cw - 0.03, bt, bh, 0.3,
                                     0.22, "fabric", "back_cushion", n_eta=10, n_om=32, tilt_deg=-BACK_CUSHION_LEAN_DEG))
    return parts


def sofa_seat_height(h: float) -> float:
    return min(0.45, h * 0.55)


# Chair v2 (round 4, docs/milestone13.md §14.8: "a chair below library level is a one-material box", P3's fit sends
# f_L1_023 and f_L1_025 to it and every chair whose library GLB fails to import falls back to it). Real dining-chair
# proportions, from secondary compilations on GitHub (opened 16 Oct 2026): "Dining chair seat height 450-470 mm"
# (interaeronav/TokenEfficiencyEngine, knowledge-base/19_interior_design/06_principles-and-technical-knowledge.md);
# "Dining chair 0.46 x 0.52 x 0.9 ... Seat pad at 0.45 with a 0.42 seat depth" and "Stacking chair 0.54 x 0.5 x
# 0.84 ... Seat at 0.45-0.46" (Flynn-Mac-97/BGE, agents/skills/blockout/real-world-sizes.md); the size table's chair
# product 0.48 x 0.55 x 0.88 m (wenart/recognition/size_table.yaml, ABO median 0.52 x 0.57 x 0.92). So: the sitting
# surface at 0.45 m, 0.40-0.45 m deep, the back's top 0.80-0.90 m (the type height 0.9, proxies.PROXY_HEIGHTS).
CHAIR_SEAT_HEIGHT_M = 0.45            # the sitting surface (the pad's or the shaped seat's top)
CHAIR_SEAT_HEIGHT_SHARE = 0.5625      # a chair lower than 0.80 m keeps the 0.45 / 0.80 proportion
CHAIR_SEAT_DEPTH_M = (0.40, 0.45)     # the sitting surface's depth (front edge to the back)
CHAIR_BACK_T_M = 0.04                 # the back's band on the rear edge: camsearch.piece_profile models the back as
#                                       this slab (min(0.04, 0.1 x depth), as the Milestone 4 chair; pinned there)
CHAIR_LEG_M = 0.035                   # legs and back posts (square; the front legs taper to 80 % at the floor)
CHAIR_APRON_M = 0.06                  # the seat rails under the seat
CHAIR_BOARD_M = 0.018                 # the seat board under the pad
CHAIR_PAD_M = 0.05                    # the upholstered pad
CHAIR_SHAPED_SEAT_M = 0.035           # a wooden or rattan seat without a pad
CHAIR_GLIDE_M = 0.008                 # the floor glides under the legs
CHAIR_TOP_RAIL_M = 0.07               # the back's top rail
CHAIR_BACK_GAP_M = 0.10               # the open gap between the sitting surface and the back panel
CHAIR_SLED_TUBE_M = 0.011             # a sled base's steel tube radius


def chair_seat_height(h: float) -> float:
    """The sitting surface of the chair family at the type height ``h`` (0.45 m from a 0.80 m back up)."""
    return min(CHAIR_SEAT_HEIGHT_M, h * CHAIR_SEAT_HEIGHT_SHARE)


def chair_design(piece: dict | None) -> dict:
    """The chair family's materials from the design's ``material_tags`` (pure): ``frame`` (``steel`` for a ``metal``
    tag, else ``wood``), ``seat`` (``rattan`` for a rattan tag, ``wood`` for a wood tag without ``fabric``, else the
    upholstered ``fabric`` pad), ``base`` (``sled`` for a metal frame, else ``legs``) and ``back`` (``rail and
    panel`` on a wooden frame: a top rail over a back panel; ``panel`` on a sled), the panel in the seat's
    material (wood under a wooden seat)."""
    tags = set(piece_design(piece).get("material_tags") or ())
    frame = "steel" if "metal" in tags else "wood"
    if "rattan" in tags:
        seat = "rattan"
    elif "wood" in tags and "fabric" not in tags:
        seat = "wood"
    else:
        seat = "fabric"
    base = "sled" if frame == "steel" else "legs"
    return {"frame": frame, "seat": seat, "base": base, "back": "panel" if base == "sled" else "rail and panel"}


def _square_frustum(cx: float, cy: float, z0: float, s0: float, s1: float, h: float, key: str, role: str) -> Part:
    """A square leg from side ``s0`` at ``z0`` to ``s1`` at the top, centred on (cx, cy), wound outwards."""
    b0, b1 = s0 / 2.0, s1 / 2.0
    verts = [(cx - b0, cy - b0, z0), (cx + b0, cy - b0, z0), (cx + b0, cy + b0, z0), (cx - b0, cy + b0, z0),
             (cx - b1, cy - b1, z0 + h), (cx + b1, cy - b1, z0 + h), (cx + b1, cy + b1, z0 + h), (cx - b1, cy + b1, z0 + h)]
    faces = [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def chair_parts(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Chair v2 (round 4): the parts of a dining chair in the box ``w x d x h`` (pure; front -Y, back +Y).

    Four legs (the front ones tapered) on dark floor glides with seat rails between them, or a steel sled base
    (two floor runners, uprights, seat rails) for a ``metal`` design; a seat: a board with an upholstered pad
    (``fabric``, the brief's fabric colour) or a shaped wooden or rattan seat (role ``top``, its top at
    ``chair_seat_height``, the pad ``CHAIR_SEAT_DEPTH_M`` deep against the back); a back on the rear edge (role
    ``back``, inside ``CHAIR_BACK_T_M``): two posts and a back panel ``CHAIR_BACK_GAP_M`` above the seat
    (upholstered on a padded chair), under a top rail on a wooden frame. At least two material slots (frame, seat,
    glides); edges bevelled by role (``part_bevel_radius``), the pads smooth. The box is the footprint, ``h`` high,
    on the floor."""
    look = chair_design(piece)
    frame = look["frame"]
    t = min(CHAIR_BACK_T_M, d * 0.1)
    leg = min(CHAIR_LEG_M, w * 0.09, d * 0.09)
    seat_h = chair_seat_height(h)
    sitting = d - t - FRONT_GAP                              # front edge to the back's face
    seat_d = min(CHAIR_SEAT_DEPTH_M[1], sitting)
    y_back = d / 2.0 - t                                     # the back's front face
    parts: list[Part] = []
    # the seat: its top is the sitting surface at seat_h
    if look["seat"] == "fabric":
        pad = min(CHAIR_PAD_M, seat_h * 0.12)
        board_top = seat_h - pad
        board = min(CHAIR_BOARD_M, board_top * 0.1)
        parts.append(_box(0.0, (-d / 2.0 + y_back - FRONT_GAP) / 2.0, board_top - board, w, sitting, board,
                          "dark" if frame == "steel" else frame, "top"))
        # the pad covers the board's full width (flush with the frame): its side points then lie inside a
        # neighbouring chair that cuts into this one, so the S2 vertex sampling (scene_checks, rest.penetration)
        # measures the cut (tests/test_m13_placement.py: two chairs 3 cm into each other, depth > 0.02 m)
        parts.append(_superellipsoid(0.0, y_back - FRONT_GAP - seat_d / 2.0, board_top, w, seat_d, pad, 0.3,
                                     0.25, "fabric", "top", n_eta=8, n_om=32))
        seat_bottom = board_top - board
    else:
        shell = min(CHAIR_SHAPED_SEAT_M, seat_h * 0.1)
        parts.append(_superellipsoid(0.0, (-d / 2.0 + y_back - FRONT_GAP) / 2.0, seat_h - shell, w, sitting, shell,
                                     0.2, 0.2, look["seat"], "top", n_eta=8, n_om=32))
        seat_bottom = seat_h - shell
    apron = min(CHAIR_APRON_M, seat_bottom * 0.2)
    rail_z = seat_bottom - apron - FRONT_GAP
    if look["base"] == "legs":
        glide = CHAIR_GLIDE_M
        for sx in (-1, 1):
            cx = sx * (w / 2.0 - leg / 2.0)
            # front legs, tapered, under the seat; the glides inset 2 mm under them
            parts.append(_square_frustum(cx, -d / 2.0 + leg / 2.0, glide, leg * 0.8, leg, seat_bottom - glide - FRONT_GAP,
                                         frame, "leg"))
            for cy, side in ((-d / 2.0 + leg / 2.0, leg * 0.8), (d / 2.0 - t / 2.0, min(leg, t))):
                parts.append(_box(cx, cy, 0.0, side - 0.004, side - 0.004, glide, "dark", "foot"))
            # the back posts: the rear legs running up to the top of the back, on the rear edge
            parts.append(_box(cx, d / 2.0 - t / 2.0, glide, leg, t, h - glide, frame, "back"))
        inner_w = w - 2.0 * leg
        span_y = d - leg - t
        # seat rails between the legs (front and sides; the rear one sits in the back band), 1 mm under the seat
        parts.append(_box(0.0, -d / 2.0 + leg / 2.0, rail_z, inner_w + 0.004, leg * 0.6, apron, frame, "apron"))
        for sx in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - leg / 2.0), -d / 2.0 + leg + span_y / 2.0, rail_z, leg * 0.6,
                              span_y + 0.004, apron, frame, "apron"))
        rail_t = t * 0.7
        parts.append(_box(0.0, d / 2.0 - rail_t / 2.0, rail_z, inner_w + 0.004, rail_t, apron, frame, "back"))
        # the back: a top rail between the posts and a back panel under it (upholstered on a padded chair), all
        # flush with the rear edge. A closed panel, not slats: camsearch.piece_profile models the back as a solid
        # slab and tests/test_camsearch.py holds the built chair's ray share to the profile's within 0.005 (a
        # slatted back measured 0.0052 over it in the table cases).
        top_z = h - CHAIR_TOP_RAIL_M - 0.003
        parts.append(_box(0.0, d / 2.0 - rail_t / 2.0, top_z, inner_w + 0.004, rail_t, CHAIR_TOP_RAIL_M, frame, "back"))
        panel_t = rail_t * 0.8
        panel_z = min(seat_h + CHAIR_BACK_GAP_M, top_z - 0.10)
        parts.append(_box(0.0, d / 2.0 - panel_t / 2.0, panel_z, inner_w + 0.004, panel_t, top_z - panel_z + 0.002,
                          frame if look["seat"] == "wood" else look["seat"], "back"))
    else:
        r = min(CHAIR_SLED_TUBE_M, leg / 2.0, t / 2.0)
        for sx in (-1, 1):
            cx = sx * (w / 2.0 - r)
            # the floor runner from the front edge to the rear edge, the front upright and the rear post on it
            parts.append(_cylinder_y(cx, -d / 2.0 + r, r, r, r, d - 2.0 * r, "steel", "base", n=12))
            parts.append(_cylinder_z(cx, -d / 2.0 + r, r, r, r, seat_bottom - r - FRONT_GAP, "steel", "leg", n=12))
            parts.append(_cylinder_z(cx, d / 2.0 - r, r, r, r, h - r, "steel", "back", n=12))
            # the seat rail under the seat, from the front upright to the rear post
            parts.append(_cylinder_y(cx, -d / 2.0 + 2.0 * r, seat_bottom - r - FRONT_GAP, r, r, d - 4.0 * r, "steel",
                                     "apron", n=12))
        # an upholstered (or wooden / rattan) back panel between the posts, flush with the rear
        panel_t = t * 0.75
        panel_z = min(seat_h + CHAIR_BACK_GAP_M, h - 0.12)
        parts.append(_box(0.0, d / 2.0 - panel_t / 2.0, panel_z, w - 4.0 * r, panel_t, h - 0.02 - panel_z,
                          look["seat"], "back"))
    return parts


def _chair(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The chair family v2 (``chair_parts``); ``piece`` is optional, so the Milestone 4 call ``_chair(w, d, h)``
    and the long table module's chairs (``modules._table_parts``) keep working."""
    return chair_parts(w, d, h, piece)


def _table(w: float, d: float, h: float, desk: bool = False) -> list[Part]:
    """Table v2 (Milestone 13): a ``TABLE_TOP_M`` top, an apron under it, four tapered legs on steel feet; the
    desk adds its drawer block with a handle. The box: the footprint, ``h`` high, on the floor."""
    top_t = min(TABLE_TOP_M, h * 0.1)
    leg = min(0.06, w * 0.08, d * 0.08)
    inset = min(0.04, w * 0.05, d * 0.05)
    parts = [_box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    apron = min(TABLE_APRON_M, (h - top_t) * 0.15)
    rail_t = min(0.025, leg * 0.5)
    span_x, span_y = w - 2 * (inset + leg), d - 2 * (inset + leg)
    if span_x > 0.05 and span_y > 0.05:
        for sy in (-1, 1):                          # 1 mm under the top: no shared face plane
            parts.append(_box(0.0, sy * (d / 2.0 - inset - leg / 2.0), h - top_t - apron, span_x, rail_t,
                              apron - FRONT_GAP, "wood", "apron"))
        for sx in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - inset - leg / 2.0), 0.0, h - top_t - apron, rail_t, span_y,
                              apron - FRONT_GAP, "wood", "apron"))
    foot = min(TABLE_FOOT_M, h * 0.03)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (w / 2.0 - inset - leg / 2.0), sy * (d / 2.0 - inset - leg / 2.0)
            parts.append(_box(cx, cy, 0.0, leg, leg, foot, "steel", "foot"))
            parts.append(_frustum_z(cx, cy, foot + FRONT_GAP, leg * 0.35, leg * 0.35, leg / 2.0, leg / 2.0,
                                    h - top_t - foot - 2 * FRONT_GAP, "wood", "leg", n=16))
    if desk:
        dw, dd, dh = w * 0.3, d - 2 * inset - 0.02, min(0.35, h * 0.45)
        dx = w / 2.0 - inset - leg - 0.01 - dw / 2.0
        parts.append(_box(dx, 0.0, h - top_t - dh, dw, dd, dh, "painted", "drawers"))
        parts.append(_box(dx, -d / 2.0 + inset + 0.01 - PROUD / 2.0, h - top_t - dh / 2.0, min(0.12, dw * 0.6),
                          PROUD, 0.015, "steel", "handle"))
    return parts


def _cabinet(w: float, d: float, h: float, rows: int, cols: int, doors: bool) -> list[Part]:
    """Box with drawer fronts (or door panels) and handles on the front."""
    parts = [_box(0.0, 0.01, 0.0, w, d - 0.02, h, "wood", "body")]
    gap = 0.02
    rh = (h - 0.1) / rows if doors else h / rows
    cw = w / cols
    z_base = 0.05 if doors else 0.0
    for r in range(rows):
        for c in range(cols):
            cx = -w / 2.0 + cw * (c + 0.5)
            z0 = z_base + rh * r
            parts.append(_box(cx, -d / 2.0 + 0.01, z0 + gap / 2.0, cw - gap, 0.02, rh - gap, "painted", "front"))
            if doors:
                hx = cx + (0.03 if c % 2 == 0 else -0.03)
                parts.append(_box(hx, -d / 2.0 - PROUD / 2.0, h / 2.0 - 0.075, 0.015, PROUD, 0.15, "steel", "handle"))
            else:
                parts.append(_box(cx, -d / 2.0 - PROUD / 2.0, z0 + rh / 2.0, min(0.12, (cw - gap) * 0.5), PROUD,
                                  0.015, "steel", "handle"))
    return parts


def _wardrobe(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Wardrobe v2 (Milestone 13): a recessed plinth, a carcass, a top panel and 0.50 m door modules in the
    design's front style with vertical bar handles at the meeting edges (``cabinet_fronts``)."""
    design = piece_design(piece)
    plinth = min(0.08, h * 0.05)
    top_t = 0.02
    body, face = _carcass(w, d, plinth, h - plinth - top_t)
    parts = [_box(0.0, 0.02, 0.0, w - 0.02, d - 0.04, plinth, "dark", "plinth"), body,
             _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    parts += cabinet_fronts(w - 0.004, face, plinth + 0.003, h - top_t - 0.003, 1, max(1, round(w / 0.5)), design)
    return parts


def _drawers(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Nightstand / dresser v2 (Milestone 13): a recessed plinth, a carcass, a top and a column of drawer fronts
    (``DRAWER_PITCH_M``, none under ``DRAWER_MIN_M``) with horizontal handles in the design's front style."""
    design = piece_design(piece)
    plinth = min(0.06, h * 0.1)
    top_t = min(0.02, h * 0.05)
    body, face = _carcass(w, d, plinth, h - plinth - top_t)
    parts = [_box(0.0, 0.015, 0.0, w - 0.03, d - 0.03, plinth, "dark", "plinth"), body,
             _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    avail = h - plinth - top_t
    rows = max(1, min(round(avail / DRAWER_PITCH_M), int(avail / DRAWER_MIN_M)))
    parts += cabinet_fronts(w - 0.004, face, plinth + 0.003, h - top_t - 0.003, rows, 1, design, doors=False)
    return parts


def _tv_unit(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """TV unit v2 (Milestone 13): a low carcass on four slim steel legs, a top and a row of drawer fronts with
    centred handles in the design's front style."""
    design = piece_design(piece)
    leg_h = min(0.10, h * 0.2)
    top_t = min(0.02, h * 0.05)
    body, face = _carcass(w, d, leg_h, h - leg_h - top_t)
    parts = [body, _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.05), sy * (d / 2.0 - 0.05), 0.0, 0.03, 0.03, leg_h, "steel", "leg"))
    parts += cabinet_fronts(w - 0.004, face, leg_h + 0.003, h - top_t - 0.003, 1, max(1, round(w / 0.6)), design,
                            doors=False)
    return parts


def shelf_heights(h: float, t: float = 0.02) -> list[float]:
    """Top faces of the inner shelves of a bookshelf of height ``h``."""
    out = []
    z = SHELF_PITCH
    while z < h - t - 0.15:
        out.append(round(z, 4))
        z += SHELF_PITCH
    return out


def _bookshelf(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Bookshelf v2 (Milestone 13): a recessed plinth, two sides, bottom and top, a painted back panel and shelves
    every ``SHELF_PITCH`` (``shelf_heights``)."""
    t = 0.025
    plinth = min(0.05, h * 0.05)
    back_t = 0.008
    parts = [
        _box(0.0, 0.01, 0.0, w - 0.04, d - 0.04, plinth, "dark", "plinth"),
        _box(-(w / 2.0 - t / 2.0), 0.0, plinth, t, d, h - plinth, "wood", "side"),
        _box((w / 2.0 - t / 2.0), 0.0, plinth, t, d, h - plinth, "wood", "side"),
        _box(0.0, 0.0, plinth, w - 2 * t, d, t, "wood", "bottom"),
        _box(0.0, 0.0, h - t, w - 2 * t, d, t, "wood", "top"),
        _box(0.0, d / 2.0 - back_t / 2.0, plinth, w - 2 * t, back_t, h - plinth - t, "painted", "back"),
    ]
    for z in shelf_heights(h - plinth, t):
        parts.append(_box(0.0, -back_t / 2.0, plinth + z - t, w - 2 * t, d - back_t, t, "wood", "shelf"))
    return parts


def _counter(w: float, d: float, h: float, island: bool = False) -> list[Part]:
    top_t = 0.04
    plinth_h = min(0.1, h * 0.12)
    inset = 0.03
    if island:
        carcass = _box(0.0, 0.0, plinth_h, w - 2 * inset, d - 2 * inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, 0.0, 0.0, w - 4 * inset, d - 4 * inset, plinth_h, "dark", "plinth")
        front_y = -d / 2.0 + inset
    else:
        carcass = _box(0.0, inset / 2.0, plinth_h, w, d - inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, inset, 0.0, w, d - 2 * inset, plinth_h, "dark", "plinth")
        front_y = -d / 2.0 + inset
    parts = [plinth, carcass, _box(0.0, 0.0, h - top_t, w, d, top_t, "worktop", "top")]
    cols = max(1, round(w / 0.6))
    cw = w / cols
    # Fronts stand FRONT_GAP proud of the carcass face at front_y (Milestone 5 put them
    # inside the carcass with coplanar front faces: rendered black); handles on the fronts.
    front_face = front_y - FRONT_GAP - FRONT_THICKNESS
    for c in range(cols):
        cx = -w / 2.0 + cw * (c + 0.5)
        parts.append(_box(cx, front_y - FRONT_GAP - FRONT_THICKNESS / 2.0, plinth_h + 0.01, cw - 0.02,
                          FRONT_THICKNESS, h - top_t - plinth_h - 0.03, "painted", "front"))
        parts.append(_box(cx, front_face - PROUD / 2.0, h - top_t - 0.06, min(0.12, cw * 0.5), PROUD, 0.015,
                          "steel", "handle"))
    return parts


# Milestone 12 (docs/milestone12.md §6.4 D24, track S): our full-size fridge, washing machine and shower in standard
# sizes, built from the footprint (the fit takes them when no audited model fits: kitchen and bath fixtures come
# from code). Real proportions: doors inset in front of the carcass with 3 mm gaps, handles inside the footprint.
FIXTURE_GAP_M = 0.003
FRIDGE_DOOR_T = 0.045            # the doors' thickness in front of the carcass
FRIDGE_FREEZER_SHARE = 0.36      # a bottom freezer: this share of the height under the fridge door
FRIDGE_PLINTH_M = 0.08
WASHER_PANEL_M = 0.14            # the control panel strip at the top front
WASHER_FRONT_T = 0.012
SHOWER_TRAY_M = 0.04
SHOWER_GLASS_T = 0.008
SHOWER_PROFILE_M = 0.02          # the chrome profiles at the glass edges


def _fridge(w: float, d: float, h: float) -> list[Part]:
    """A full-size fridge-freezer (Milestone 12): carcass, a dark ventilation plinth, a bottom freezer door and the
    fridge door above it with 3 mm gaps, a vertical bar handle on each door (inside the footprint), a top cap."""
    t = min(FRIDGE_DOOR_T, d * 0.1)
    face = -d / 2.0 + t                            # the doors' back = the carcass front
    plinth = min(FRIDGE_PLINTH_M, h * 0.06)
    split = plinth + (h - plinth) * FRIDGE_FREEZER_SHARE
    g = FIXTURE_GAP_M
    hx = w / 2.0 - 0.06
    parts = [
        _box(0.0, face + (d / 2.0 - face) / 2.0, 0.0, w, d / 2.0 - face, h, "steel", "body"),
        _box(0.0, (-d / 2.0 + 0.02 + face) / 2.0, 0.0, w - 0.02, face - (-d / 2.0 + 0.02), plinth - g, "dark",
             "plinth"),
        _box(0.0, -d / 2.0 + 0.012 + (t - 0.012) / 2.0, plinth, w - 2 * g, t - 0.012, split - plinth - g / 2.0,
             "steel", "front"),
        _box(0.0, -d / 2.0 + 0.012 + (t - 0.012) / 2.0, split + g / 2.0, w - 2 * g, t - 0.012,
             h - split - g / 2.0 - g, "steel", "front"),
    ]
    for z0, z1 in ((plinth + 0.06, split - 0.12), (split + 0.12, split + 0.12 + (h - split) * 0.45)):
        parts.append(_box(hx, -d / 2.0 + 0.006, z0, 0.022, 0.012, max(0.1, z1 - z0), "steel", "handle"))
    return parts


def _stove(w: float, d: float, h: float) -> list[Part]:
    r = min(w, d) * 0.14
    parts = [
        _box(0.0, 0.0, 0.0, w, d, h - 0.02, "steel", "body"),
        _box(0.0, 0.0, h - 0.02, w, d, 0.02, "dark", "top"),
        _box(0.0, -d / 2.0 - PROUD / 2.0, h * 0.55, w - 0.08, PROUD, 0.02, "steel", "handle"),  # oven handle
        _box(0.0, -d / 2.0 - PROUD / 4.0, h * 0.2, w - 0.1, PROUD / 2.0, h * 0.3, "dark", "front"),  # oven glass
    ]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_cylinder_z(sx * w / 4.0, sy * d / 4.0, h, r, r, PROUD, "steel", "ring", n=20))
    return parts


def _basin(cx: float, cy: float, z0: float, bw: float, bd: float, depth: float, wall: float, key: str) -> list[Part]:
    """Open basin: four walls and a bottom around an inner void."""
    return [
        _box(cx, cy - bd / 2.0 + wall / 2.0, z0, bw, wall, depth, key, "basin"),
        _box(cx, cy + bd / 2.0 - wall / 2.0, z0, bw, wall, depth, key, "basin"),
        _box(cx - bw / 2.0 + wall / 2.0, cy, z0, wall, bd - 2 * wall, depth, key, "basin"),
        _box(cx + bw / 2.0 - wall / 2.0, cy, z0, wall, bd - 2 * wall, depth, key, "basin"),
        _box(cx, cy, z0, bw - 2 * wall, bd - 2 * wall, wall, key, "basin"),
    ]


# Basins in cabinets (fix round after P3, part 2, 17 Oct 2026): a carcass under an inset basin is a hollow box, as a
# real sink or vanity cabinet is. P3's sink cabinets (and the vanities) were one solid body up to the top's
# underside, so the body's top face closed the bowl a few centimetres under the rim (the kitchen sink unit of
# ``modules`` showed a 4 cm tray with a cabinet-paint floor). ``open_carcass`` keeps the solid body only up to
# ``BASIN_CLEAR_M`` under the basin bottom and closes the rest with ``CARCASS_PANEL_M`` boards.
BASIN_CLEAR_M = 0.005
CARCASS_PANEL_M = 0.018           # an 18 mm carcass board (the island back panel of ``modules`` uses the same)


def open_carcass(cx: float, cy: float, z0: float, w: float, d: float, h: float, open_z: float, key: str,
                 front: bool = False, role: str = "body") -> list[Part]:
    """A carcass box ``(cx, cy, z0, w, d, h)`` that is hollow above ``open_z`` (fix round after P3, part 2, 17 Oct
    2026; see ``BASIN_CLEAR_M``): the solid body from ``z0`` to ``open_z`` (its top face is the cavity's floor,
    under the basin), then a side board at each x end and a back board (+Y), and a front board (-Y) when ``front``
    (a carcass whose fronts do not close it up to the top), each ``CARCASS_PANEL_M`` thick, up to ``z0 + h``. The
    outer box is the solid carcass's, so every bounding box stays as it was. ``open_z`` is clamped to the carcass."""
    top = z0 + h
    open_z = min(max(float(open_z), z0), top)
    t = min(CARCASS_PANEL_M, w / 4.0, d / 4.0)
    parts: list[Part] = []
    if open_z - z0 > 1e-3:
        parts.append(_box(cx, cy, z0, w, d, open_z - z0, key, role))
    ph = top - open_z
    if ph > 1e-3:
        parts += [_box(cx - w / 2.0 + t / 2.0, cy, open_z, t, d, ph, key, role),
                  _box(cx + w / 2.0 - t / 2.0, cy, open_z, t, d, ph, key, role),
                  _box(cx, cy + d / 2.0 - t / 2.0, open_z, w - 2 * t, t, ph, key, role)]
        if front:
            parts.append(_box(cx, cy - d / 2.0 + t / 2.0, open_z, w - 2 * t, t, ph, key, role))
    return parts


def _sink(w: float, d: float, h: float) -> list[Part]:
    """A freestanding sink cabinet: a carcass, a front, a steel top with the basin and a tap. Fix round after P3,
    part 2 (17 Oct 2026): the carcass is hollow above the basin bottom (``open_carcass``), so the bowl is 18 cm deep
    (its solid body had closed the bowl 2 cm under the rim)."""
    top_t = 0.02
    bw = min(w - 0.16, 0.5)
    bd = min(d - 0.16, 0.4)
    sx, sy = (w - bw) / 2.0, (d - bd) / 2.0  # strip widths around the basin hole
    parts = [
        *open_carcass(0.0, 0.01, 0.0, w, d - 0.02, h - top_t, h - 0.18 - BASIN_CLEAR_M, "painted", front=True),
        _box(0.0, -d / 2.0 + 0.01, 0.02, w - 0.04, 0.02, h - top_t - 0.04, "painted", "front"),
        _box(0.0, -d / 2.0 + sy / 2.0, h - top_t, w, sy, top_t, "steel", "top"),
        _box(0.0, d / 2.0 - sy / 2.0, h - top_t, w, sy, top_t, "steel", "top"),
        _box(-w / 2.0 + sx / 2.0, 0.0, h - top_t, sx, bd, top_t, "steel", "top"),
        _box(w / 2.0 - sx / 2.0, 0.0, h - top_t, sx, bd, top_t, "steel", "top"),
    ]
    parts += _basin(0.0, 0.0, h - 0.18, bw, bd, 0.18, 0.01, "steel")
    tap_y = min(bd / 2.0 + 0.04, d / 2.0 - 0.03)
    parts.append(_cylinder_z(0.0, tap_y, h, 0.015, 0.015, 0.25, "steel", "tap", n=12))
    return parts


def _washbasin(w: float, d: float, h: float) -> list[Part]:
    basin_h = min(0.15, h * 0.2)
    ped = min(0.18, w * 0.4, d * 0.4)
    parts = [_box(0.0, d / 2.0 - 0.05 - ped / 2.0, 0.0, ped, ped, h - basin_h, "ceramic", "pedestal")]
    parts += _basin(0.0, 0.0, h - basin_h, w, d, basin_h, 0.03, "ceramic")
    parts.append(_cylinder_z(0.0, d / 2.0 - 0.04, h, 0.012, 0.012, 0.15, "steel", "tap", n=12))
    return parts


def _toilet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The Milestone 4 close-coupled WC; 29 Oct 2026 (UL114 B1): the wall-hung WC with its flush plate when the
    piece's bathroom look says so (``bath_parts.wall_hung_wc_parts``; on its feature wall's face, B24)."""
    look = (piece or {}).get("bath_look") if isinstance((piece or {}).get("bath_look"), dict) else {}
    if look.get("wc") == "wall_hung":
        from wenart.blender import bath_parts as BT
        return BT.wall_hung_wc_parts(w, d, h, float(look.get("wall_offset_m") or 0.0))
    tank_d = min(0.18, d * 0.3)
    bowl_d = d - tank_d
    return [
        _box(0.0, d / 2.0 - tank_d / 2.0, 0.2, w, tank_d, h + 0.4 - 0.2, "ceramic", "back"),
        _cylinder_z(0.0, -tank_d / 2.0, 0.0, w / 2.0, bowl_d / 2.0, h - 0.03, "ceramic", "bowl"),
        _cylinder_z(0.0, -tank_d / 2.0, h - 0.03, w / 2.0 * 0.98, bowl_d / 2.0 * 0.98, 0.03, "painted", "seat"),
    ]


def _shower_m14(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The Milestone 12 shower; 29 Oct 2026 (UL123 B16): the walk-in enclosure of the piece's bathroom look."""
    look = (piece or {}).get("bath_look") if isinstance((piece or {}).get("bath_look"), dict) else {}
    if look.get("shower") == "walk_in":
        from wenart.blender import bath_parts as BT
        return BT.walk_in_shower_parts(w, d, h)
    return _shower(w, d, h)


def _shower(w: float, d: float, h: float) -> list[Part]:
    """A shower (Milestone 12): a low white tray with a steel drain, clear glass on the front (a fixed panel and a
    door with a 6 mm gap) and both sides in chrome profiles with a top stabiliser rail, and on the back a riser
    pipe, an arm and a round rain head with a mixer at hand height."""
    tray = min(SHOWER_TRAY_M, h * 0.05)
    gt, pm = SHOWER_GLASS_T, SHOWER_PROFILE_M
    gh = h - tray
    parts = [
        _box(0.0, 0.0, 0.0, w, d, tray, "ceramic", "tray"),
        _cylinder_z(0.0, 0.0, tray, min(0.05, w / 8.0), min(0.05, d / 8.0), 0.002, "steel", "drain", n=20),
    ]
    door = w * 0.5
    fixed = w - door - 0.006 - 2 * pm
    yf = -d / 2.0 + gt / 2.0
    parts.append(_box(-w / 2.0 + pm + fixed / 2.0, yf, tray, fixed, gt, gh - 0.01, "glass", "front"))
    parts.append(_box(w / 2.0 - pm - door / 2.0, yf, tray + 0.005, door - 0.006, gt, gh - 0.02, "glass", "front"))
    for sx in (-1, 1):
        parts.append(_box(sx * (w / 2.0 - gt / 2.0), pm / 2.0, tray, gt, d - pm, gh - 0.01, "glass", "side"))
        parts.append(_box(sx * (w / 2.0 - pm / 2.0), -d / 2.0 + pm / 2.0, tray, pm, pm, gh, "steel", "frame"))
        parts.append(_box(sx * (w / 2.0 - pm / 2.0), d / 2.0 - pm / 2.0, tray, pm, pm, gh, "steel", "frame"))
    parts.append(_box(0.0, -d / 2.0 + pm / 2.0, h - pm, w - 2 * pm, pm, pm, "steel", "rail"))
    riser_y = d / 2.0 - 0.03
    head_r = min(0.12, w / 5.0, d / 5.0)
    parts.append(_cylinder_z(0.0, riser_y, 1.0, 0.012, 0.012, h - 0.12 - 1.0, "steel", "pipe", n=12))
    parts.append(_cylinder_y(0.0, riser_y - 0.25, h - 0.13, 0.01, 0.01, 0.25, "steel", "arm", n=12))
    parts.append(_cylinder_z(0.0, riser_y - 0.25, h - 0.16, head_r, head_r, 0.015, "steel", "head", n=32))
    parts.append(_box(0.0, riser_y + 0.005, 1.05, 0.08, 0.04, 0.16, "steel", "mixer"))
    return parts


# 28 Oct 2026 (user on real06's bathrooms: "What kind of a bath is this" / "this bath needs to make sense"; the library
# bath refused, the bath is built from code): a bath of real parts. The rim band, the panel's recess under it, the
# mixer and the drain sizes are designer values of built-in acrylic and steel baths.
BATH_RIM_BAND_M = 0.035           # the ceramic band of the rim over a panel
BATH_PANEL_INSET_M = 0.012        # a bath panel stands this far back under the rim
BATH_FLOOR_M = 0.08               # the bowl floor's thickness (capped at 15 % of the height)
BATH_MIXER_POST_M = 0.10          # the deck mixer's post over the rim
BATH_SPOUT_M = 0.13               # its spout, over the bowl


def bath_walls(piece: dict | None) -> set:
    """The sides of a bath on a wall (0 front -Y, 1 +X end, 2 back +Y, 3 -X end) the fit recorded on its asset
    (``asset.bath_walls``, ``fixture_seat.bath_walls``); empty when unknown."""
    asset = (piece or {}).get("asset") if isinstance((piece or {}).get("asset"), dict) else {}
    walls = asset.get("bath_walls", (piece or {}).get("bath_walls"))
    return {int(k) for k in walls or [] if isinstance(k, (int, float)) and int(k) in (0, 1, 2, 3)}


def _bathtub(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """A bath (28 Oct 2026, the comment above): a ceramic shell whose walls make a flat rim around the bowl, the bowl
    floor with a drain, an overflow on the inner end wall, and a chrome deck mixer (a post, a spout over the bowl, two
    handles) at the end that stands on a wall (``bath_walls``; else the +X end). With its back on a wall it has a panel
    on every side no wall covers, set back under a ceramic rim band (a niche between walls: the front panel; a corner:
    the front and the open end); without a wall behind it (freestanding or unknown) the shell shows all round."""
    walls = bath_walls(piece)
    t = min(0.07, w * 0.06, d * 0.1)
    band = min(BATH_RIM_BAND_M, h * 0.1)
    panels = ({0, 1, 2, 3} - walls) if 2 in walls else set()
    inset = min(BATH_PANEL_INSET_M, t * 0.4)
    parts: list[Part] = []
    # (side, centre x, centre y, size x, size y, outward unit)
    sides = ((0, 0.0, -d / 2.0 + t / 2.0, w, t, (0.0, -1.0)), (2, 0.0, d / 2.0 - t / 2.0, w, t, (0.0, 1.0)),
             (1, w / 2.0 - t / 2.0, 0.0, t, d - 2 * t, (1.0, 0.0)), (3, -w / 2.0 + t / 2.0, 0.0, t, d - 2 * t, (-1.0, 0.0)))
    for k, cx, cy, sx, sy, (ux, uy) in sides:
        if k in panels:
            parts.append(_box(cx, cy, h - band, sx, sy, band, "ceramic", "rim"))
            px, py = cx - ux * inset / 2.0, cy - uy * inset / 2.0
            parts.append(_box(px, py, 0.0, sx - abs(ux) * inset, sy - abs(uy) * inset, h - band, "painted", "panel"))
        else:
            parts.append(_box(cx, cy, 0.0, sx, sy, h, "ceramic", "basin"))
    floor = min(BATH_FLOOR_M, h * 0.15)
    parts.append(_box(0.0, 0.0, 0.0, w - 2 * t, d - 2 * t, floor, "ceramic", "basin"))
    end = 1.0 if 1 in walls or 3 not in walls else -1.0          # the mixer's end: on a wall
    x_post = end * (w / 2.0 - t / 2.0)
    r_post = min(0.018, t * 0.3)
    parts.append(_cylinder_z(x_post, 0.0, h, r_post, r_post, BATH_MIXER_POST_M, "steel", "tap", n=16))
    spout = min(BATH_SPOUT_M, w * 0.12)
    x0 = x_post - spout if end > 0 else x_post
    parts.append(_cylinder_x(x0, 0.0, h + BATH_MIXER_POST_M - 0.015, 0.011, 0.011, spout, "steel", "tap"))
    for sy_ in (-1.0, 1.0):
        y = sy_ * min(0.07, d / 2.0 - t)
        parts.append(_cylinder_z(x_post, y, h, 0.016, 0.016, 0.045, "steel", "tap", n=12))
    x_drain = end * (w / 2.0 - t - min(0.10, w * 0.08))
    parts.append(_cylinder_z(x_drain, 0.0, floor, 0.03, 0.03, 0.004, "steel", "drain", n=20))
    x_in = end * (w / 2.0 - t)
    parts.append(_cylinder_x(x_in - 0.004 if end > 0 else x_in, 0.0, h - min(0.12, h * 0.25), 0.025, 0.025, 0.004,
                             "steel", "drain", n=16))
    return parts


def _washing_machine(w: float, d: float, h: float) -> list[Part]:
    """A front-loading washing machine (Milestone 12): a white body with a top plate, a dark kick plate, the control
    panel strip with a detergent drawer, a dark display and a steel dial, and the porthole door: a chrome ring
    around a glass window in front of the dark drum."""
    ft = min(WASHER_FRONT_T, d * 0.03)
    face = -d / 2.0 + ft
    r = min(w, h) * 0.25
    zc = h * 0.42
    panel = min(WASHER_PANEL_M, h * 0.18)
    parts = [
        _box(0.0, face + (d / 2.0 - face) / 2.0, 0.0, w, d / 2.0 - face, h - 0.02, "painted", "body"),
        _box(0.0, 0.0, h - 0.02, w, d, 0.02, "painted", "top"),
        _box(0.0, face - ft / 4.0, 0.0, w - 0.04, ft / 2.0, 0.07, "dark", "plinth"),
        _box(-w / 2.0 + 0.11, face - ft / 2.0, h - panel + 0.015, 0.18, ft, panel - 0.05, "painted", "front"),
        _box(w * 0.05, face - ft / 4.0, h - panel + 0.035, w * 0.22, ft / 2.0, panel * 0.4, "dark", "front"),
        _cylinder_y(w / 2.0 - 0.08, face - ft, h - panel / 2.0 - 0.01, 0.028, 0.028, ft, "steel", "front", n=24),
        # the porthole, front to back: the glass, the dark drum seen through it, the chrome ring around them
        _cylinder_y(0.0, face - ft, zc, r, r, ft / 3.0, "glass", "front", n=40),
        _cylinder_y(0.0, face - ft * 2.0 / 3.0, zc, r, r, ft / 3.0, "dark", "front", n=40),
        _cylinder_y(0.0, face - ft / 3.0, zc, r + 0.035, r + 0.035, ft / 3.0, "steel", "front", n=40),
    ]
    return parts


# --------------------------------------------------------------------------
# Milestone 7: side table, floor lamp, potted plant (docs/milestone7.md §6.4)
# --------------------------------------------------------------------------

# A drawn piece is round when a circle fits at least this share of its points (the recognition core
# records ``shape: "round"`` or ``circle_fit: {"share": s}`` on the piece or in its ``details``).
ROUND_FIT_SHARE = 0.9
ROUND_SHAPES = ("round", "circle", "circular")


def piece_is_round(piece: dict | None) -> bool:
    """True when the building says the drawn piece is round: ``shape`` in
    ``ROUND_SHAPES`` or ``circle_fit.share >= ROUND_FIT_SHARE`` on the piece
    or in its ``details``. Nothing is guessed from the footprint (a square
    footprint is the box of a round and of a square table alike)."""
    if not piece:
        return False
    for src in (piece, piece.get("details") or {}):
        shape = src.get("shape")
        if isinstance(shape, str) and shape.strip().lower() in ROUND_SHAPES:
            return True
        fit = src.get("circle_fit")
        share = fit.get("share") if isinstance(fit, dict) else None
        if isinstance(share, (int, float)) and not isinstance(share, bool) and share >= ROUND_FIT_SHARE:
            return True
    return False


def _frustum_z(cx: float, cy: float, z0: float, rx0: float, ry0: float, rx1: float, ry1: float, h: float,
               key: str, role: str, n: int = 32) -> Part:
    """Elliptic truncated cone along Z (bottom radii ``rx0, ry0``, top ``rx1, ry1``), wound outwards."""
    bottom = [(cx + rx0 * math.cos(2 * math.pi * i / n), cy + ry0 * math.sin(2 * math.pi * i / n), z0)
              for i in range(n)]
    top = [(cx + rx1 * math.cos(2 * math.pi * i / n), cy + ry1 * math.sin(2 * math.pi * i / n), z0 + h)
           for i in range(n)]
    faces = [[i, (i + 1) % n, n + (i + 1) % n, n + i] for i in range(n)]
    faces.append(list(range(n, 2 * n)))
    faces.append(list(range(n - 1, -1, -1)))
    return {"verts": bottom + top, "faces": faces, "key": key, "role": role}


def _side_table(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Round side table (top disc, pedestal, base disc) when ``piece_is_round``,
    else a square one (top, four legs, a lower shelf)."""
    top_t = min(0.03, h * 0.1)
    if piece_is_round(piece):
        base_t = min(0.025, h * 0.08)
        col = min(0.035, w * 0.12, d * 0.12)
        return [
            _cylinder_z(0.0, 0.0, h - top_t, w / 2.0, d / 2.0, top_t, "wood", "top", n=40),
            _cylinder_z(0.0, 0.0, base_t, col, col, h - top_t - base_t, "wood", "leg", n=16),
            _cylinder_z(0.0, 0.0, 0.0, w * 0.3, d * 0.3, base_t, "wood", "base", n=32),
        ]
    leg = min(0.035, w * 0.1, d * 0.1)
    inset = min(0.02, w * 0.05, d * 0.05)
    parts = [_box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - inset - leg / 2.0), sy * (d / 2.0 - inset - leg / 2.0), 0.0, leg, leg,
                              h - top_t, "wood", "leg"))
    shelf_w, shelf_d = w - 2 * (inset + leg), d - 2 * (inset + leg)
    if shelf_w > 0.05 and shelf_d > 0.05:
        parts.append(_box(0.0, 0.0, min(0.15, h * 0.3), shelf_w, shelf_d, 0.02, "wood", "shelf"))
    return parts


def _floor_lamp(w: float, d: float, h: float) -> list[Part]:
    """Floor lamp: a dark base disc, a steel pole and a fabric drum shade
    whose bottom rim fills the footprint. Geometry only: no light."""
    base_t = 0.025
    shade_h = min(0.4, h * 0.3)
    r = min(w, d)
    return [
        _cylinder_z(0.0, 0.0, 0.0, max(0.05, r * 0.35), max(0.05, r * 0.35), base_t, "dark", "base", n=32),
        _cylinder_z(0.0, 0.0, base_t, 0.012, 0.012, h - shade_h + 0.05 - base_t, "steel", "pole", n=12),
        _frustum_z(0.0, 0.0, h - shade_h, w / 2.0, d / 2.0, w / 2.0 * 0.8, d / 2.0 * 0.8, shade_h, "bedding",
                   "shade"),
    ]


def _potted_plant(w: float, d: float, h: float) -> list[Part]:
    """The decor plant (``decor_parts("plant")``: terracotta pot, soil, stem,
    green crown) at the drawn size: the crown fills the footprint."""
    rx, ry = w / 2.0, d / 2.0
    pot_h = h * 0.35
    return [
        _cylinder_z(0.0, 0.0, 0.0, rx * 0.7, ry * 0.7, pot_h, "terracotta", "pot", n=24),
        _cylinder_z(0.0, 0.0, pot_h - 0.01, rx * 0.62, ry * 0.62, 0.01, "dark", "soil", n=24),
        _cylinder_z(0.0, 0.0, pot_h, 0.012, 0.012, (h - pot_h) * 0.4, "wood", "stem", n=8),
        _cylinder_z(0.0, 0.0, pot_h + (h - pot_h) * 0.35, rx, ry, (h - pot_h) * 0.65, "green", "crown", n=16),
    ]


# --------------------------------------------------------------------------
# Milestone 7: stair (docs/milestone7.md §6.4)
# --------------------------------------------------------------------------

STAIR_SLAB_M = 0.15                # assumed slab between the ceiling and the floor above
STAIR_WAIST_M = 0.15               # assumed waist slab under the steps; also the landing slab
STAIR_RISER_RANGE = (0.15, 0.20)   # a derived riser outside this range is a warning
STAIR_GENERIC_RISER_M = 0.175      # riser of a stair without drawn flights (count assumed)
STAIR_RAIL_HEIGHT = 0.90           # handrail top above the nosing line
STAIR_RAIL_W = 0.04
STAIR_RAIL_T = 0.05
STAIR_RAIL_INSET = 0.04            # rail centre this far inside the flight side
STAIR_RAIL_MIN_M = 0.3             # a rail shorter than this (cut by the cap) is left out
STAIR_POST = 0.04
STAIR_RISER_PLATE = 0.02           # closes the last riser of a flight, standing on its last tread
STAIR_SHAFT_CAP_M = 0.5            # the neutral cap of the ceiling opening, above the ceiling
STAIR_SHAFT_GAP = 0.002            # the void stands this far outside the steps and the landing
STAIR_SHAFT_LIP = 0.02             # shaft faces reach this far below the ceiling: a slab edge, no slit
STAIR_CAP_CLEARANCE = 0.03         # rails stay this far below the cap
STAIR_HEADROOM_M = 2.0             # below this under the ceiling at a flight's top: a warning
STAIR_WALL_PROBE = 0.05            # a side is against a wall when points this far outside it lie in one
STAIR_RISER_SOURCE = "derived from assumed ceiling and slab"
# 25 Oct 2026 (user: "better internal stairs"): a tread plate in the floor finish with a nosing over the riser below
# (painted risers and structure), a balustrade on every open side (balusters at a 0.104 m gap, or a glass panel fixed
# to the side of the flight, under a round handrail) and a round handrail on brackets along the wall of a flight that
# has no open side.
STAIR_TREAD_T = 0.04
STAIR_NOSING_M = 0.025
STAIR_HANDRAIL_R = 0.022
STAIR_BALUSTER = 0.016
STAIR_BALUSTER_PITCH = 0.12
STAIR_GLASS_T = 0.012
STAIR_WALL_RAIL_GAP = 0.06
STAIR_BALUSTRADE_DEFAULT = "bars"
# 25 Oct 2026 (architect K1, real04: U stairs drawn with 11 lines for a 3 m storey, risers of 0.25-0.29 m): an answer
# may turn the half landing of a U stair into winders (``stair.winders``: "auto" or a count), turning treads around
# the well, so the stair keeps its drawn footprint with comfortable risers (``STAIR_WINDER_TARGET_RISER``).
STAIR_WINDER_TARGET_RISER = 0.185
STAIR_WINDER_MAX = 8
# 27 Oct 2026 (a review: the automatic winders came from one project's U stairs): a riser over the limit is fixed for
# any stair shape. A quarter landing (an L stair: the two flights at right angles) turns 90 degrees, half a U's half
# landing, so it holds at most half the winders (``STAIR_WINDER_MAX_QUARTER``; winder treads narrower at the newel
# than that make no step); a straight flight gets a longer run at its foot instead (``stair.extra_treads``: treads of
# its drawn going added before its first riser, decided by the architect's K1 where the floor there is free).
STAIR_WINDER_MAX_QUARTER = STAIR_WINDER_MAX // 2


def stair_data(piece: dict | None) -> dict | None:
    """The stair record of a piece: ``piece["stair"]`` (building JSON,
    docs/milestone7.md §1.3) or ``piece["details"]["stair"]`` (recognition
    core output); None when there is none."""
    if not piece:
        return None
    data = piece.get("stair")
    if not isinstance(data, dict):
        data = (piece.get("details") or {}).get("stair")
    return data if isinstance(data, dict) else None


def _v(a, b) -> tuple[float, float]:
    return (float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))


def _d2(a, b) -> float:
    return float(a[0]) * float(b[0]) + float(a[1]) * float(b[1])


def _unit2(v) -> tuple[float, float] | None:
    n = math.hypot(float(v[0]), float(v[1]))
    return None if n < 1e-9 else (float(v[0]) / n, float(v[1]) / n)


def _local_to_world2(p, center, rot) -> tuple[float, float]:
    return G.rotate_point((float(center[0]) + p[0], float(center[1]) + p[1]), rot, (float(center[0]),
                                                                                     float(center[1])))


def stair_plan(piece: dict, rise: float, ceiling_height: float | None = None, cap_height: float | None = None,
               walls: Sequence[dict] = (), rise_source: str = STAIR_RISER_SOURCE) -> dict:
    """How a stair piece is built (pure; world XY, z above the level floor).

    ``rise`` = floor to the floor above (the caller: ceiling height + the
    assumed ``STAIR_SLAB_M``, or the level elevations); ``ceiling_height``
    (default ``rise - STAIR_SLAB_M``) and ``cap_height`` (default ceiling +
    ``STAIR_SHAFT_CAP_M``) place the void's shaft; ``walls`` decide which
    flight sides get a handrail. Returns ``{"flights": [...] (climbing
    order; per flight ``lines``, ``width``, ``going``, ``rise_dir``,
    ``nosings``, ``base_z``, ``top_z``), "risers", "riser_m",
    "riser_source", "rise_m", "landing", "void", "void_raw", "ceiling_z",
    "cap_z", "rails", "direction", "turn", "generic", "assumed", "warnings",
    "notes"}``. ``assumed`` entries are ``{"field", "kind", "value",
    "reason"}`` for the scene manifest."""
    fp = piece["footprint"]
    center = (float(fp["center"][0]), float(fp["center"][1]))
    rot = float(fp.get("rotation_deg") or 0.0)
    fw, fd = float(fp["size"][0]), float(fp["size"][1])
    local_y = G.rotate_point((0.0, 1.0), rot)
    data = stair_data(piece) or {}
    rise = float(rise)
    ceiling = float(ceiling_height) if ceiling_height is not None else rise - STAIR_SLAB_M
    cap = float(cap_height) if cap_height is not None else ceiling + STAIR_SHAFT_CAP_M
    assumed: list[dict] = []
    warnings: list[str] = []
    notes: list[str] = []

    flights = []
    raw = data.get("flights") or []
    for k, f in enumerate(raw):
        try:
            s = (float(f["start"][0]), float(f["start"][1]))
            e = (float(f["end"][0]), float(f["end"][1]))
            n, width = int(f["lines"]), float(f["width"])
        except (KeyError, TypeError, ValueError, IndexError):
            warnings.append(f"flight {k + 1}: start, end, width or lines missing; not built")
            continue
        length = G.distance(s, e)
        if n < 2 or length < 1e-6 or width <= 0:
            warnings.append(f"flight {k + 1}: {n} tread line(s) over {length:.3f} m, width {width:.3f} m: "
                            f"no direction to build; not built")
            continue
        flights.append({"index": k, "start": s, "end": e, "lines": n, "width": width,
                        "axis": _unit2(_v(s, e)), "going": length / (n - 1)})
    generic = not flights
    if generic:
        n = max(2, int(round(rise / STAIR_GENERIC_RISER_M)))
        s = _local_to_world2((0.0, -fd / 2.0), center, rot)
        e = _local_to_world2((0.0, fd / 2.0), center, rot)
        flights = [{"index": 0, "start": s, "end": e, "lines": n, "width": fw, "axis": local_y,
                    "going": fd / (n - 1)}]
        why = "no drawn flights" if not raw else "no buildable drawn flight"
        assumed.append({"field": "flights", "kind": "stair_flights",
                        "value": f"one straight flight of {n} risers along +local Y filling the footprint",
                        "reason": f"{why}: the riser count is assumed ({rise:.2f} m / {STAIR_GENERIC_RISER_M} m)"})
        warnings.append(f"{why}: one straight flight of {n} assumed risers fills the footprint")

    # Rise direction: the recorded one (assumed by the recognition rule unless drawn), else +local Y.
    a0 = flights[0]["axis"]
    rec = data.get("direction")
    d_vec = _unit2(rec) if isinstance(rec, (list, tuple)) and len(rec) >= 2 else None
    if d_vec is None:
        d_vec, d_src = local_y, "no direction recorded: steps rise along +local Y of the footprint"
    elif data.get("direction_assumed", True) is not False:
        d_src = str(data.get("reason") or "rise direction assumed by the recognition rule (no UP arrow drawn)")
    else:
        d_src = None                                       # drawn
    dot0 = _d2(a0, d_vec)
    if abs(dot0) < 0.5:
        if abs(_d2(a0, local_y)) >= 0.5:
            dot0 = _d2(a0, local_y)
            notes.append("the recorded direction does not run along the flights: +local Y used")
        else:
            dot0 = 1.0
            notes.append("neither the recorded direction nor +local Y runs along the flights: "
                         "first to last drawn line used")
        d_src = d_src or "recorded direction not along the flights"
    r0 = a0 if dot0 >= 0 else (-a0[0], -a0[1])
    rdirs = [r0]
    for f in flights[1:]:
        a, prev = f["axis"], rdirs[-1]
        if abs(_d2(a, prev)) >= 0.9:                        # side by side: a U-turn rises the other way
            rdirs.append(a if _d2(a, prev) < 0 else (-a[0], -a[1]))
        else:
            rdirs.append(a if _d2(a, d_vec) >= 0 else (-a[0], -a[1]))
            notes.append(f"flight {f['index'] + 1} is not parallel to flight 1: it rises along the recorded direction")
    if d_src is not None:
        assumed.append({"field": "direction", "kind": "stair_direction", "value": [round(r0[0], 4), round(r0[1], 4)],
                        "reason": d_src})
    turn = data.get("turn") or ("straight" if len(flights) == 1 else "U" if len(flights) == 2 else "other")
    if len(flights) >= 2 and data.get("turn_assumed", True) is not False:
        assumed.append({"field": "turn", "kind": "stair_turn", "value": turn,
                        "reason": "flights side by side read as a turning stair, climbed in turn; nothing drawn "
                                  "says which flight starts at the floor"})

    # Landing and climbing order: with a landing the flight rising towards it climbs first.
    land = data.get("landing")
    poly = land.get("polygon") if isinstance(land, dict) else land
    landing_poly = [(float(p[0]), float(p[1])) for p in poly] if isinstance(poly, (list, tuple)) and len(poly) >= 3 \
        else None
    order = list(range(len(flights)))
    if landing_poly is not None and len(flights) >= 2:
        c = G.polygon_centroid(landing_poly)
        mid0 = G.segment_midpoint(flights[0]["start"], flights[0]["end"])
        if _d2(_v(mid0, c), rdirs[0]) <= 0:
            order.reverse()
    elif landing_poly is None and len(flights) >= 2:
        notes.append("no landing drawn: the flights are climbed in the drawn order without a landing slab")

    # Risers: every drawn line is a nosing; riser = rise / all risers (or a documented riser). Winders (an answer to
    # the architect's K1) add their treads in the half landing of a U stair.
    total = sum(f["lines"] for f in flights)
    # 27 Oct 2026 (``STAIR_WINDER_MAX_QUARTER``): a straight flight's longer run (the architect's K1 or an answer)
    extra = 0
    if len(flights) == 1 and str(data.get("extra_treads") or "").isdigit() and not generic:
        extra = int(data["extra_treads"])
        if extra:
            total += extra
            assumed.append({"field": "extra_treads", "kind": "stair_run", "value": extra,
                            "reason": "the architect (K1): the straight flight's run is longer at its foot by "
                                      f"{extra} tread(s) of its drawn going, so its risers are comfortable"})
    winders = 0
    want = data.get("winders")
    if want and len(flights) == 2 and landing_poly is not None:
        quarter = abs(_d2(flights[0]["axis"], flights[1]["axis"])) < 0.5          # an L stair's quarter landing
        winders = int(want) if str(want).isdigit() else \
            max(0, int(math.ceil(rise / STAIR_WINDER_TARGET_RISER - 1e-9)) - total)
        winders = max(0, min(STAIR_WINDER_MAX_QUARTER if quarter else STAIR_WINDER_MAX, winders))
        if winders:
            total += winders
            assumed.append({"field": "winders", "kind": "stair_winders", "value": winders,
                            "reason": f"the architect's answer (K1): the {'quarter' if quarter else 'half'} landing "
                                      f"turned into winders, so the drawn footprint holds comfortable risers"})
    documented = data.get("riser_m")
    doc_source = str(data.get("riser_source") or "")
    if isinstance(documented, (int, float)) and not isinstance(documented, bool) and documented > 0 \
            and not doc_source.startswith("derived"):
        riser, riser_source = float(documented), doc_source or "documented"
        if abs(riser * total - rise) > 0.02:
            warnings.append(f"documented riser {riser:.3f} m x {total} risers = {riser * total:.3f} m differs from "
                            f"the rise {rise:.3f} m")
    else:
        riser, riser_source = rise / total, rise_source
        assumed.append({"field": "riser_m", "kind": "stair_riser", "value": round(riser, 4),
                        "reason": f"{riser_source}: {rise:.3f} m / {total} drawn risers"
                                  + (" (assumed count)" if generic else "")})
    lo, hi = STAIR_RISER_RANGE
    if not lo - 1e-9 <= riser <= hi + 1e-9:
        warnings.append(f"riser {riser:.3f} m outside {lo:.2f}-{hi:.2f} m ({riser_source}, {total} risers)")

    z = 0.0
    planned = []
    for idx in order:
        f = dict(flights[idx])
        r = rdirs[idx]
        n, g, a = f["lines"], f["going"], f["axis"]
        first = f["start"] if _d2(a, r) > 0 else f["end"]
        if extra and not planned:                     # the longer run: treads added before the first riser
            first = (first[0] - r[0] * g * extra, first[1] - r[1] * g * extra)
            n += extra
            f.update(lines=n, extra_treads=extra)
        f.update({"rise_dir": r, "base_z": z, "top_z": z + n * riser,
                  "nosings": [(first[0] + r[0] * g * i, first[1] + r[1] * g * i) for i in range(n)]})
        z = f["top_z"] + (winders * riser if winders and not planned else 0.0)
        planned.append(f)

    landing = None
    if landing_poly is not None:
        if len(planned) >= 2:
            role, z_l = "mid", planned[0]["top_z"]
        else:
            f = planned[0]
            towards = _d2(_v(G.segment_midpoint(f["start"], f["end"]), G.polygon_centroid(landing_poly)),
                          f["rise_dir"]) > 0
            role, z_l = ("top", f["top_z"]) if towards else ("floor", 0.0)
            if role == "floor":
                notes.append("the landing lies at the foot of the flight: it is the floor, no slab")
        landing = {"polygon": landing_poly, "z": z_l, "role": role, "thickness": STAIR_WAIST_M}
        if winders and role == "mid":
            # 28 Oct 2026 (``WINDER_TREADS_NOTE``): ``winders`` risers in the turn need winders + 1 treads, the
            # first at the landing's level
            landing.update(role="winders", winders=winder_treads(landing_poly, planned, z_l, riser, winders + 1))

    # The ceiling opening: the last flight and the landing (in the frame of flight 1).
    void, void_raw = [], []
    if rise > ceiling + 1e-6:
        o = flights[0]["start"]
        u = a0
        vx, vy = -u[1], u[0]

        def to_f(p):
            q = _v(o, p)
            return (q[0] * vx + q[1] * vy, _d2(q, u))

        def from_f(q):
            return (o[0] + vx * q[0] + u[0] * q[1], o[1] + vy * q[0] + u[1] * q[1])

        last = planned[-1]
        hw = last["width"] / 2.0
        lp = (-last["axis"][1], last["axis"][0])
        corners = [(p[0] + lp[0] * s * hw, p[1] + lp[1] * s * hw) for p in (last["start"], last["end"]) for s in (-1, 1)]
        rects = [_frame_box([to_f(c) for c in corners])]
        # 28 Oct 2026: a landing turned into winders is in the opening too (its treads climb towards the ceiling, as
        # stair_access.opening_polygon cuts it); before, its winders stood under the ceiling with under 1 m headroom
        if landing is not None and landing["role"] in ("mid", "top", "winders"):
            rects.append(_frame_box([to_f(p) for p in landing_poly]))
        rects = close_box_gaps(rects)                      # 28 Oct 2026: no sliver of slab between them
        g = STAIR_SHAFT_GAP
        void_raw = [[from_f(p) for p in loop] for loop in geom2d.rect_union_outline(rects)]
        void = [[from_f(p) for p in loop]
                for loop in geom2d.rect_union_outline([(b[0] - g, b[1] - g, b[2] + g, b[3] + g) for b in rects])]
        what = "the last flight" + (" and the landing" if len(rects) > 1 else "")
        reason = "nothing drawn above the stair; the opening is assumed" if data.get("void_assumed", True) \
            is not False else "drawn"
        assumed.append({"field": "void", "kind": "stair_void",
                        "value": f"ceiling opening over {what}, closed by a neutral shaft cap "
                                 f"{cap - ceiling:.2f} m above the ceiling",
                        "reason": f"{reason}; the floor above is not modelled, so the cap hides the shaft"})
        for f in planned[:-1]:
            headroom = ceiling - f["top_z"]
            if headroom < STAIR_HEADROOM_M:
                warnings.append(f"flight {f['index'] + 1}: {headroom:.2f} m under the ceiling at its top "
                                f"(the opening covers {what} only, assumed)")

    # Handrails: every flight side that is not against a wall.
    wall_rects = [G.centerline_to_rectangle(w["start"], w["end"], float(w["thickness"])) for w in walls
                  if G.distance(w["start"], w["end"]) > 1e-9]
    rails = []
    for f in planned:
        r = f["rise_dir"]
        p = (-r[1], r[0])
        hw = f["width"] / 2.0
        a_, b_ = f["nosings"][0], f["nosings"][-1]
        for side, sgn in (("left", 1.0), ("right", -1.0)):
            reach = sgn * (hw + STAIR_WALL_PROBE)
            probes = [(a_[0] + (b_[0] - a_[0]) * t + p[0] * reach, a_[1] + (b_[1] - a_[1]) * t + p[1] * reach)
                      for t in (0.25, 0.5, 0.75)]
            if sum(1 for q in probes if any(G.point_in_polygon(q, rect) for rect in wall_rects)) >= 2:
                continue
            rails.append({"flight": f["index"], "side": side, "offset": sgn * (hw - STAIR_RAIL_INSET)})
    # 28 Oct 2026 (stair_rails, user on real04: "There should have been better indoor stair solutions"): the two
    # climbing sides as one path each (flights, the landing's or the winders' edge, the next flight), every leg open
    # or against a wall; ``stair_parts`` builds one continuous balustrade per open stretch from it
    from wenart.blender import stair_rails as SR
    near = [p for f in planned for p in f["nosings"]] + list(landing_poly or [])
    wall_rects_kept = SR.wall_rects_near(near, walls)
    probe_plan = {"flights": planned, "riser_m": riser, "landing": landing, "rise_m": rise}
    sides = SR.side_paths(probe_plan, wall_rects_kept)
    if rails or any(not leg["wall"] for s in sides for leg in s["legs"]):
        assumed.append({"field": "handrail", "kind": "stair_handrail",
                        "value": f"one continuous balustrade with newels on every open side ({len(rails)} open flight "
                                 f"side(s)), the handrail {STAIR_RAIL_HEIGHT:.2f} m above the nosings, "
                                 f"{SR.LEVEL_GUARD_M:.2f} m along a level edge",
                        "reason": "design detail on every stair side not against a wall; not in the documents"})
    assumed.append({"field": "waist", "kind": "stair_structure",
                    "value": f"{STAIR_WAIST_M:.2f} m waist slab under the steps and landing slab",
                    "reason": "the documents show the stair in plan only"})
    # A cap lowered under the floor of a level above: the last riser (and a top landing) stop just under it.
    top_limit = cap - STAIR_CAP_CLEARANCE / 3.0 if rise > cap - STAIR_CAP_CLEARANCE / 3.0 else None
    if top_limit is not None:
        notes.append(f"the last riser stops at {top_limit:.3f} m, under the shaft cap ({cap:.3f} m)")
    return {"flights": planned, "risers": total, "riser_m": riser, "riser_source": riser_source, "rise_m": rise,
            "winders": winders,
            "landing": landing, "void": void, "void_raw": void_raw, "ceiling_z": ceiling, "cap_z": cap,
            "top_limit": top_limit, "rails": rails, "direction": [round(r0[0], 4), round(r0[1], 4)], "turn": turn,
            "generic": generic, "assumed": assumed, "warnings": warnings, "notes": notes,
            "sides": sides, "wall_rects": wall_rects_kept}


# 28 Oct 2026, WINDER_TREADS_NOTE (the review of real04's stairs after the user's "There should have been better
# indoor stair solutions"): ``stair.winders`` counts the risers the turn adds. The first flight's last riser already
# rises to the landing's level, so the turn holds winders + 1 treads, the first at that level and the last at the
# second flight's foot. Before, the turn held ``winders`` treads, the first one riser over the landing's level: the
# first flight's last riser and the first winder made one double step (real04 L-1: 1.059 m, then 1.235 m).


def winder_treads(landing_poly, planned: list[dict], z0: float, riser: float, k: int) -> list[dict]:
    """The ``k`` winder treads of a U stair's half landing (pure): sectors of 180 / k degrees around the pivot (the
    middle of the landing's edge between the two flights), from the first flight's side to the second's, clipped to
    the landing; tread ``j`` tops at ``z0 + j * riser`` (``WINDER_TREADS_NOTE``: the first at the landing's level
    ``z0``, the first flight's top). ``[{"polygon", "top"}]``. 27 Oct 2026: a quarter landing (the flights at right
    angles, an L stair) turns its treads around its inner corner (``_quarter_winders``). 28 Oct 2026:
    ``NEWEL_WINDERS_MIN`` treads or more turn as two quarter turns around the newels at the well
    (``_newel_winders``); the single fan stays for fewer, or when the flights leave no well."""
    a, b = planned[0], planned[1]
    if abs(_d2(a["rise_dir"], b["rise_dir"])) < 0.5:
        return _quarter_winders(landing_poly, a, b, z0, riser, k)
    u = a["rise_dir"]                                           # into the landing
    poly = geom2d.ccw([(float(p[0]), float(p[1])) for p in landing_poly])
    # the landing edge the flights arrive at: the one with the smallest projection on u
    proj = [_d2(p, u) for p in poly]
    base = min(proj)
    edge = [p for p, d in zip(poly, proj) if d - base < 0.05]
    ca = G.segment_midpoint(a["nosings"][0], a["nosings"][-1])
    cb = G.segment_midpoint(b["nosings"][0], b["nosings"][-1])
    mid = G.segment_midpoint(ca, cb)
    v = (-u[1], u[0])
    side_a = -1.0 if _d2(_v(mid, ca), v) < 0 else 1.0          # the first flight's side along v
    pivot = (mid[0] + u[0] * (base - _d2(mid, u)), mid[1] + u[1] * (base - _d2(mid, u)))
    if len(edge) >= 2:
        es = sorted(_d2(p, v) for p in edge)
        t = min(max(_d2(pivot, v), es[0]), es[-1])
        pivot = (pivot[0] + v[0] * (t - _d2(pivot, v)), pivot[1] + v[1] * (t - _d2(pivot, v)))
    far = 50.0
    corners = _newel_winders(poly, a, b, mid, base, u, v, side_a, z0, riser, k)
    if corners:
        return corners
    out = []
    for j in range(k):
        # angle from the first flight's side (along v * side_a, 0) through u (90) to the other side (180)
        t0, t1 = math.pi * j / k, math.pi * (j + 1) / k
        pts = [pivot]
        for t in (t0, (t0 + t1) / 2.0, t1):
            d = (v[0] * side_a * math.cos(t) + u[0] * math.sin(t), v[1] * side_a * math.cos(t) + u[1] * math.sin(t))
            pts.append((pivot[0] + d[0] * far, pivot[1] + d[1] * far))
        sector = geom2d.ccw(pts)
        piece = sector
        n = len(poly)
        for i in range(n):                                    # clip to the convex landing
            p0, p1 = poly[i], poly[(i + 1) % n]
            nx, ny = (p1[1] - p0[1]), -(p1[0] - p0[0])        # outward normal of a ccw edge
            piece = geom2d.clip_half_plane(piece, nx, ny, -(nx * p0[0] + ny * p0[1]))
            if not piece:
                break
        if len(piece) >= 3 and abs(G.polygon_signed_area(piece)) > 1e-4:
            out.append({"polygon": [(round(x, 5), round(y, 5)) for x, y in piece], "top": z0 + j * riser})
    return out


# 28 Oct 2026 (user on real04's stairs: "There should have been better indoor stair solutions"): the half landing's
# winders fanned from one point at the middle of the landing's edge (all treads meeting there, a spiral look). A U
# stair with winders turns around its well instead: two quarter turns, each around the newel at its flight's inner
# corner (the well's edge), the first flight's set climbing from its last nosing to the landing's middle, the second's
# from the middle to its first nosing; the strip between the newels (the well's width) belongs to the tread at the
# middle of each half, so the winders still tile the landing. NEWEL_WINDERS_MIN: fewer winder treads keep the single
# fan.
NEWEL_WINDERS_MIN = 3


def _sector(pivot, s, u, t0: float, t1: float, far: float = 50.0) -> list:
    """The sector from angle ``t0`` to ``t1`` (radians, ``t1 - t0`` < pi) around ``pivot`` in the frame (``s`` at 0,
    ``u`` at pi / 2)."""
    pts = [pivot]
    for t in (t0, (t0 + t1) / 2.0, t1):
        d = (s[0] * math.cos(t) + u[0] * math.sin(t), s[1] * math.cos(t) + u[1] * math.sin(t))
        pts.append((pivot[0] + d[0] * far, pivot[1] + d[1] * far))
    return geom2d.ccw(pts)


def _newel_winders(poly, a: dict, b: dict, mid, base: float, u, v, side_a: float, z0: float, riser: float,
                   k: int) -> list[dict]:
    """The ``k`` winder treads of a U stair's half landing as two quarter turns around the newels (the comment above;
    tread ``j`` tops at ``z0 + j * riser``); [] when ``k`` < ``NEWEL_WINDERS_MIN`` or the flights leave no well between
    them (the single fan then)."""
    if k < NEWEL_WINDERS_MIN:
        return []
    ca = G.segment_midpoint(a["nosings"][0], a["nosings"][-1])
    cb = G.segment_midpoint(b["nosings"][0], b["nosings"][-1])
    m_v = _d2(mid, v)
    inner_a = _d2(ca, v) - side_a * float(a["width"]) / 2.0        # the well edge of each flight along v
    inner_b = _d2(cb, v) + side_a * float(b["width"]) / 2.0
    if side_a * (inner_a - m_v) < -1e-6 or side_a * (m_v - inner_b) < -1e-6:
        return []                                                   # the flights overlap: no well
    k1 = (k + 1) // 2
    k2 = k - k1
    s_a = (v[0] * side_a, v[1] * side_a)
    s_b = (-s_a[0], -s_a[1])
    pa = (u[0] * base + v[0] * inner_a, u[1] * base + v[1] * inner_a)
    pb = (u[0] * base + v[0] * inner_b, u[1] * base + v[1] * inner_b)
    # the two halves of the landing, split along its middle line (parallel to u through mid)
    half_a = geom2d.clip_half_plane(list(poly), -s_a[0], -s_a[1], s_a[0] * mid[0] + s_a[1] * mid[1])
    half_b = geom2d.clip_half_plane(list(poly), -s_b[0], -s_b[1], s_b[0] * mid[0] + s_b[1] * mid[1])
    if not half_a or not half_b:
        return []
    out = []
    half = math.pi / 2.0
    for j in range(k1):                                             # the first flight's turn: from s_a to u (and on)
        t0, t1 = half * j / k1, (half * (j + 1) / k1 if j < k1 - 1 else math.pi - 1e-6)
        piece = _clip_convex(_sector(pa, s_a, u, t0, t1), geom2d.ccw(half_a))
        if len(piece) >= 3 and abs(G.polygon_signed_area(piece)) > 1e-4:
            out.append({"polygon": [(round(x, 5), round(y, 5)) for x, y in piece], "top": z0 + j * riser})
    for j in range(k2):                                             # the second's: from u (and before) to s_b
        hi = half - half * j / k2
        lo = half - half * (j + 1) / k2
        t0, t1 = lo, (math.pi - 1e-6 if j == 0 else hi)
        piece = _clip_convex(_sector(pb, s_b, u, t0, t1) if j else
                             _sector(pb, s_b, u, lo, math.pi - 1e-6), geom2d.ccw(half_b))
        if len(piece) >= 3 and abs(G.polygon_signed_area(piece)) > 1e-4:
            out.append({"polygon": [(round(x, 5), round(y, 5)) for x, y in piece],
                        "top": z0 + (k1 + j) * riser})
    return out if len(out) == k else []


def _clip_convex(piece: list, poly: list) -> list:
    """``piece`` clipped to the convex counter-clockwise ``poly``."""
    n = len(poly)
    for i in range(n):
        p0, p1 = poly[i], poly[(i + 1) % n]
        nx, ny = (p1[1] - p0[1]), -(p1[0] - p0[0])            # outward normal of a ccw edge
        piece = geom2d.clip_half_plane(piece, nx, ny, -(nx * p0[0] + ny * p0[1]))
        if not piece:
            break
    return piece


def _quarter_winders(landing_poly, a: dict, b: dict, z0: float, riser: float, k: int) -> list[dict]:
    """The ``k`` winder treads of an L stair's quarter landing (pure; 27 Oct 2026): the first flight arrives on one side
    of the landing (the line of its last riser), the second leaves from the next side (the line of its first riser);
    the two lines meet at the landing's inner corner, the pivot; sectors of 90 / k degrees from the first side to the
    second, clipped to the landing; tread ``j`` tops at ``z0 + j * riser`` (``WINDER_TREADS_NOTE``)."""
    u, w = a["rise_dir"], b["rise_dir"]
    pa, pb = a["nosings"][-1], b["nosings"][0]
    da, db = (-u[1], u[0]), (-w[1], w[0])
    det = da[0] * (-db[1]) - da[1] * (-db[0])
    if abs(det) < 1e-9:
        return []
    t = ((pb[0] - pa[0]) * (-db[1]) - (pb[1] - pa[1]) * (-db[0])) / det
    pivot = (pa[0] + da[0] * t, pa[1] + da[1] * t)
    ea, eb = _unit2(_v(pivot, pa)), _unit2(_v(pivot, pb))
    if ea is None or eb is None:
        return []
    t_a = math.atan2(ea[1], ea[0])
    sweep = math.atan2(ea[0] * eb[1] - ea[1] * eb[0], _d2(ea, eb))            # about +-90 degrees
    poly = geom2d.ccw([(float(p[0]), float(p[1])) for p in landing_poly])
    far = 50.0
    out = []
    for j in range(k):
        pts = [pivot] + [(pivot[0] + math.cos(t_a + sweep * s) * far, pivot[1] + math.sin(t_a + sweep * s) * far)
                         for s in (j / k, (j + 0.5) / k, (j + 1) / k)]
        piece = _clip_convex(geom2d.ccw(pts), poly)
        if len(piece) >= 3 and abs(G.polygon_signed_area(piece)) > 1e-4:
            out.append({"polygon": [(round(x, 5), round(y, 5)) for x, y in piece], "top": z0 + j * riser})
    return out


# 28 Oct 2026 (stair_rails, the review of real04's U stairs): a drawn flight may stop a little short of its landing
# (real04: 1 cm); the stair's opening, the union of the boxes of its last flight and landing, then kept a sliver of
# slab between them, and a handrail passing there was cut "under the slab". Boxes this close are joined.
BOX_GAP_CLOSE_M = 0.05


def close_box_gaps(boxes, tol: float = BOX_GAP_CLOSE_M) -> list:
    """Axis boxes ``(x0, y0, x1, y1)`` with every gap of at most ``tol`` between two of them that face each other
    (they overlap across the gap) closed: the first box grows to the second (pure)."""
    out = [list(b) for b in boxes]
    for i, a in enumerate(out):
        for j, b in enumerate(out):
            if i == j:
                continue
            if min(a[3], b[3]) - max(a[1], b[1]) > 1e-3 and 0.0 < b[0] - a[2] <= tol:
                a[2] = b[0]
            if min(a[2], b[2]) - max(a[0], b[0]) > 1e-3 and 0.0 < b[1] - a[3] <= tol:
                a[3] = b[1]
    return [tuple(b) for b in out]


def _frame_box(points) -> tuple[float, float, float, float]:
    xs, ys = [p[0] for p in points], [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys))


def _part(mesh: tuple, key: str, role: str, **extra) -> Part:
    verts, faces = mesh
    return dict({"verts": verts, "faces": faces, "key": key, "role": role}, **extra)


def stair_parts(plan: dict) -> list[Part]:
    """The parts of a planned stair (world XY, z above the level floor):
    per flight ``n - 1`` step prisms (tread between two drawn nosings, on a
    ``STAIR_WAIST_M`` waist slab, never below the floor) and the riser plate
    of the last riser; the landing slab (``mid`` / ``top`` landings); the
    rails and their two posts, cut ``STAIR_CAP_CLEARANCE`` below the cap.
    Steps, plates and the landing carry ``rise_dir`` for ``stair_face_slots``.

    Fix round after P4b (17 Oct 2026): ``plan["wall_joints"]`` (``shell.stair_wall_joints``) widens a flight's steps
    and riser plate on the side that meets a wall and moves a landing edge out by its ``extend_m``, so no slit is left
    between the stair and the wall; the rails keep the drawn flight width. A plan without joints is built as drawn.

    26 Oct 2026 (user on real06: "an unguarded stair void at the upper landing"): ``plan["rail_limit"]`` (set by
    ``shell.plan_stairs`` for a stair that comes up through the opening of the floor above) lets the balustrade of an
    open side run to the top of the flight, where the guard of the floor opening (``details.void_guards``) takes
    over; without it the rails stop under the cap as before. A wall handrail always stops under the cap (the wall
    may end at the floor above).

    28 Oct 2026 (``stair_rails``, user on real04: "There should have been better indoor stair solutions"): the rails
    are one continuous balustrade per open side with newels at its turns and ends, the infill under it and a wall
    handrail where one is wanted (``plan["guards"]``, else ``stair_rails.plan_guards`` on the plan's
    ``ceiling_voids`` and ``upper_guards``); the structure follows ``plan["design"]`` (``stair_rails.flight_waist``:
    the thin plate or the stringers of a light style, strings on the open sides); the winders of a light stair over a
    floor opening (``plan["floor_voids"]``) are thin treads with riser plates (``stair_rails.winder_parts``)."""
    from wenart.blender import stair_rails as SR

    riser = float(plan["riser_m"])
    limit = plan.get("top_limit")
    parts: list[Part] = []
    joints = plan.get("wall_joints") or []
    for f in plan["flights"]:
        n, g, width, base = f["lines"], f["going"], f["width"], f["base_z"]
        r, origin = f["rise_dir"], f["nosings"][0]
        ext = {j["side"]: float(j["extend_m"]) for j in joints if j["part"] == "flight" and j["flight"] == f["index"]}
        if ext:
            el, er = ext.get("left", 0.0), ext.get("right", 0.0)
            shift = (el - er) / 2.0
            origin = (origin[0] - r[1] * shift, origin[1] + r[0] * shift)     # left of the rise direction
            width = width + el + er
        k, t_v = SR.flight_waist(plan, f)                        # 28 Oct 2026: the waist of the stair's structure
        extra = {"flight": f["index"], "rise_dir": [r[0], r[1]]}
        for i in range(1, n):
            s0, s1 = (i - 1) * g, i * g
            top = base + i * riser
            body = top - STAIR_TREAD_T                               # the structure under the tread plate
            # the first riser stands back by the nosing (the drawn first line is the nosing: the stair stays in its
            # footprint); every other tread overhangs the riser below
            b0, n0 = (s0 + STAIR_NOSING_M, s0) if i == 1 else (s0, s0 - STAIR_NOSING_M)
            z0, z1 = base + b0 * k - t_v, base + s1 * k - t_v       # soffit under the root line
            if z0 < 0.0 < z1:
                sc = (t_v - base) / k
                profile = [(b0, 0.0), (sc, 0.0), (s1, z1), (s1, body), (b0, body)]
            else:
                profile = [(b0, max(0.0, z0)), (s1, max(0.0, z1)), (s1, body), (b0, body)]
            parts.append(_part(geom2d.extrude_profile(profile, origin, r, width), "worktop", "step", **extra))
            tread = [(n0, body), (s1, body), (s1, top), (n0, top)]
            parts.append(_part(geom2d.extrude_profile(tread, origin, r, width), "worktop", "tread", **extra))
        sn = (n - 1) * g
        z_lo = base + (n - 1) * riser
        z_hi = base + n * riser if limit is None else min(base + n * riser, limit)
        if z_hi - z_lo > 1e-4:
            parts.append(_part(geom2d.extrude_profile(
                [(sn - STAIR_RISER_PLATE, z_lo), (sn, z_lo), (sn, z_hi), (sn - STAIR_RISER_PLATE, z_hi)],
                origin, r, width), "worktop", "riser", **extra))
    landing = plan.get("landing")
    if landing is not None and landing["role"] == "winders" and SR.light_winders(plan, plan.get("floor_voids") or ()):
        parts.extend(SR.winder_parts(plan))                  # 28 Oct 2026: a light stair's winders over a void
    elif landing is not None and landing["role"] == "winders":
        z_bottom = landing["z"] - landing["thickness"]
        for j, w in enumerate(landing.get("winders") or []):
            top = w["top"] if limit is None else min(w["top"], limit)
            parts.append(_part(geom2d.prism(w["polygon"], z_bottom, top), "worktop", "winder", flight=None,
                               rise_dir=None, winder=j))
    elif landing is not None and landing["role"] in ("mid", "top"):
        z_top = landing["z"] if limit is None else min(landing["z"], limit)
        poly = landing["polygon"]
        moves = {j["edge"]: float(j["extend_m"]) for j in joints if j["part"] == "landing"}
        if moves:
            poly = landing_with_joints(poly, moves)
        parts.append(_part(geom2d.prism(poly, z_top - landing["thickness"], z_top),
                           "worktop", "landing", flight=None, rise_dir=None))
    parts.extend(_apron_part(plan))                          # 26 Oct 2026: the floor's edge meets the top step
    parts.extend(_under_parts(plan))                         # 27 Oct 2026: the space under the stair, its posts
    guards = plan.get("guards") or SR.plan_guards(plan, plan.get("ceiling_voids"), plan.get("upper_guards") or ())
    parts.extend(SR.string_parts(guards))                    # 28 Oct 2026: the strings, the rails, newels, infill
    parts.extend(SR.guard_parts(guards))
    return parts


def _under_parts(plan: dict) -> list[Part]:
    """The spandrel panels and the landing posts of ``plan["under"]`` (``stair_access.under_stair``, set by
    ``shell.stair_under_plan``; 27 Oct 2026, user on real06: "This stairs not making any sense": loose slabs seen from
    below): each panel a board ``SPANDREL_T_M`` thick standing on the floor, its outer face on the open edge, its top
    under the soffit; each post a square column up to the landing's underside; role ``spandrel`` / ``landing_post`` (the
    stair's structure finish)."""
    from wenart.blender import stair_access as SA
    under = plan.get("under") or {}
    parts: list[Part] = []
    for pan in under.get("panels") or []:
        p, q, n = pan["p"], pan["q"], pan["inward"]
        length = G.distance(p, q)
        if length < 1e-6:
            continue
        along = ((q[0] - p[0]) / length, (q[1] - p[1]) / length)
        t = SA.SPANDREL_T_M
        origin = (p[0] + n[0] * t / 2.0, p[1] + n[1] * t / 2.0)
        zp = max(0.0, float(pan["zp"]) - SA.SPANDREL_TOP_GAP_M)
        zq = max(0.0, float(pan["zq"]) - SA.SPANDREL_TOP_GAP_M)
        profile = [(0.0, 0.0), (length, 0.0)] + ([(length, zq)] if zq > 1e-4 else []) + \
            ([(0.0, zp)] if zp > 1e-4 else [])
        if len(profile) < 3:
            continue
        parts.append(_part(geom2d.extrude_profile(profile, origin, along, t), "worktop", "spandrel", flight=None,
                           rise_dir=None))
    for post in under.get("posts") or []:
        x, y = post["at"]
        h = SA.POST_M / 2.0
        top = float(post["z"]) - SA.SPANDREL_TOP_GAP_M
        if top <= 0.0:
            continue
        parts.append(_part(geom2d.prism([(x - h, y - h), (x + h, y - h), (x + h, y + h), (x - h, y + h)], 0.0, top),
                           "worktop", "landing_post", flight=None, rise_dir=None))
    return parts


# 26 Oct 2026 (user on real06: "an unguarded stair void at the upper landing"): real06's drawn stairwell opening runs
# 0.30 m past the top step of the last flight, so one stepped off the stair into a slot of the floor. A gap of at most
# STAIR_APRON_MAX_M between the last nosing and the edge of the floor's opening (along the rise) is closed by an apron
# (``top_apron``): a slab in the tread finish from the last riser to that edge, its top STAIR_APRON_UNDER_M under the
# floor above (no coplanar faces).
STAIR_APRON_MAX_M = 0.6
STAIR_APRON_UNDER_M = 0.002


def _ray_exit(o, d, polygon) -> float | None:
    """How far the ray from ``o`` along the unit ``d`` runs before it leaves ``polygon`` (the nearest edge it
    crosses ahead), None when it crosses none."""
    best = None
    n = len(polygon)
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        t = ((a[0] - o[0]) * ey - (a[1] - o[1]) * ex) / den
        s = ((a[0] - o[0]) * d[1] - (a[1] - o[1]) * d[0]) / den
        if t > 1e-6 and -1e-9 <= s <= 1.0 + 1e-9 and (best is None or t < best):
            best = t
    return best


def arrival_apron(plan: dict, openings: Sequence[Sequence[Sequence[float]]]) -> float:
    """The depth of the apron at the top of a stair (pure): how far past the last nosing of its last flight, along
    its rise, the floor's opening it comes up through (``openings``: polygons of the slab above) goes on (the most of
    three rays: the flight's centre and both sides 5 cm in), when that is between 5 mm and ``STAIR_APRON_MAX_M``; else
    0 (the floor meets the top step, or the opening is a gallery the guard closes)."""
    flights = plan.get("flights") or []
    if not flights or not openings:
        return 0.0
    f = flights[-1]
    r = f["rise_dir"]
    c = f["nosings"][-1]
    side = (-r[1], r[0])
    hw = max(0.0, float(f["width"]) / 2.0 - 0.05)
    starts = [(c[0] + side[0] * s, c[1] + side[1] * s) for s in (0.0, -hw, hw)]
    for poly in openings:
        poly = [(float(p[0]), float(p[1])) for p in poly]
        if len(poly) < 3 or not G.point_in_polygon((c[0] + r[0] * 0.003, c[1] + r[1] * 0.003), poly):
            continue
        exits = [_ray_exit(o, r, poly) for o in starts]
        exits = [t for t in exits if t is not None]
        if not exits:
            continue
        depth = max(exits)
        return depth if 0.005 <= depth <= STAIR_APRON_MAX_M else 0.0
    return 0.0


def _apron_part(plan: dict) -> list[Part]:
    """The apron of ``plan["top_apron"]`` (``arrival_apron``): a slab ``STAIR_WAIST_M`` thick across the last flight's
    drawn width, from its last riser to the floor's edge, top ``STAIR_APRON_UNDER_M`` under the rise; role
    ``landing`` (its top in the tread finish)."""
    depth = float(plan.get("top_apron") or 0.0)
    if depth <= 0.0 or not plan.get("flights"):
        return []
    f = plan["flights"][-1]
    r = f["rise_dir"]
    c = f["nosings"][-1]
    p = (-r[1], r[0])
    hw = float(f["width"]) / 2.0
    poly = [(c[0] - p[0] * hw, c[1] - p[1] * hw), (c[0] + p[0] * hw, c[1] + p[1] * hw),
            (c[0] + p[0] * hw + r[0] * depth, c[1] + p[1] * hw + r[1] * depth),
            (c[0] - p[0] * hw + r[0] * depth, c[1] - p[1] * hw + r[1] * depth)]
    top = float(plan["rise_m"]) - STAIR_APRON_UNDER_M
    return [_part(geom2d.prism(geom2d.ccw(poly), top - STAIR_WAIST_M, top), "worktop", "landing", flight=None,
                  rise_dir=None, apron=True)]


def landing_with_joints(polygon, moves: dict) -> list[tuple[float, float]]:
    """The landing polygon (counter-clockwise, as ``shell.stair_wall_joints`` numbers its edges) with edge ``k``
    moved out by ``moves[k]`` metres (pure; fix round after P4b): each vertex moves by the outward normals of the
    moved edges it ends, so a rectangle stays a rectangle."""
    pts = geom2d.ccw([tuple(p[:2]) for p in polygon])
    n = len(pts)
    shift = [[0.0, 0.0] for _ in pts]
    for k, d in moves.items():
        a, b = pts[k], pts[(k + 1) % n]
        length = G.distance(a, b)
        if length < 1e-9:
            continue
        nx, ny = (b[1] - a[1]) / length, -(b[0] - a[0]) / length
        for i in (k, (k + 1) % n):
            shift[i][0] += nx * d
            shift[i][1] += ny * d
    return [(p[0] + sx, p[1] + sy) for p, (sx, sy) in zip(pts, shift)]


# Material slots of a built stair (shell.build_stairs): treads (and the landing's top), structure (steps, risers,
# soffit: the wall paint), steel, glass; 28 Oct 2026: timber (the house's wood: a timber handrail, slats, turned
# balusters, newels and strings of the styles that have them, ``stair_rails.FAMILY_DESIGN``).
STAIR_SLOTS = ("tread", "structure", "steel", "glass", "timber")
STAIR_KEY_SLOTS = {"steel": 2, "glass": 3, "timber": 4}


def stair_face_slots(parts: Sequence[Part]) -> list[int]:
    """Slot per face of ``stair_parts`` (``STAIR_SLOTS``): the tread plates and the landing's top are ``tread``
    (the floor finish), the steps, the riser plates, the strings in the structure finish and the landing's other faces
    ``structure`` (painted risers, soffit, sides; 25 Oct 2026), rails, posts, balusters and brackets ``steel`` (or
    ``timber``, by their key), a glass panel ``glass``."""
    slots = []
    for part in parts:
        if part["key"] in STAIR_KEY_SLOTS:
            slots.extend([STAIR_KEY_SLOTS[part["key"]]] * len(part["faces"]))
            continue
        if part.get("role") == "tread":                       # the tread plate: the floor finish all round
            slots.extend([0] * len(part["faces"]))
            continue
        if part.get("role") in ("step", "riser", "spandrel", "landing_post", "string"):   # painted, the underside
            slots.extend([1] * len(part["faces"]))
            continue
        for f in part["faces"]:
            nx, ny, nz = geom2d.face_normal(part["verts"], f)
            slots.append(0 if nz > 0.5 else 1)
    return slots


def void_shaft(plan: dict) -> tuple[list, list]:
    """``(verts, faces)`` closing the ceiling opening (z above the level
    floor): one inward-facing quad per edge of every void loop, from
    ``STAIR_SHAFT_LIP`` below the ceiling up to the cap, and the cap faces
    (facing down). Empty when the stair needs no opening."""
    parts = []
    z0, z1 = plan["ceiling_z"] - STAIR_SHAFT_LIP, plan["cap_z"]
    for loop in plan["void"]:
        pts = list(loop)
        if G.polygon_signed_area(pts) < 0:
            pts = pts[::-1]
        n = len(pts)
        verts, faces = [], []
        for i in range(n):
            (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
            j = len(verts)
            verts += [(ax, ay, z0), (ax, ay, z1), (bx, by, z1), (bx, by, z0)]   # normal to the left: inwards
            faces.append([j, j + 1, j + 2, j + 3])
        parts.append((verts, faces))
        parts.append(geom2d.polygon_faces(pts, [], z1, facing_up=False))
    return geom2d.merge(parts)


def _stair(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Stair parts in the piece's local frame (``build_parts``): the drawn
    flights of ``piece`` (or one assumed flight filling ``w x d``) with ``h``
    as the rise; no walls, so every side gets a rail."""
    fp = dict((piece or {}).get("footprint") or {"center": [0.0, 0.0], "rotation_deg": 0.0})
    fp["size"] = [w, d]
    center = (float(fp["center"][0]), float(fp["center"][1]))
    rot = float(fp.get("rotation_deg") or 0.0)
    plan = stair_plan(dict(piece or {}, footprint=fp), h)
    out = []
    for part in stair_parts(plan):
        verts = [(*G.rotate_point((x - center[0], y - center[1]), -rot), z) for x, y, z in part["verts"]]
        rd = part.get("rise_dir")
        local = dict(part, verts=verts)
        if rd is not None:
            local["rise_dir"] = list(G.rotate_point((rd[0], rd[1]), -rot))
        out.append(local)
    return out


# --------------------------------------------------------------------------
# Milestone 10 (docs/milestone10.md §4.4-§4.7): cabinets with fronts, the new furniture types, doors, windows
# --------------------------------------------------------------------------

# Cabinet looks (``furniture.design``, docs/milestone10.md §1.1, §4.4). The builders read the design of the piece
# they get (``build_parts(..., piece=)``); ``furniture.py`` fills a missing design from ``style.json`` first
# (``wenart.blender.looks.design_for``), so a design here is complete or empty (defaults below, recorded there).
FRONT_STYLES: tuple[str, ...] = ("flat", "shaker", "slatted", "glass")
DEFAULT_FRONT_STYLE = "flat"
SHAKER_FRAME_M = 0.065           # shaker stiles and rails (at most 18 % of the front's side)
SHAKER_PANEL_M = 0.012           # the recessed panel; the frame stands FRONT_THICKNESS
SLAT_W_M = 0.03                  # slatted fronts: slat width and gap on a dark backing
SLAT_GAP_M = 0.012
SLAT_BACKING_M = 0.008
GLASS_FRAME_M = 0.05             # glass fronts: the frame around the pane
GLASS_PANE_M = 0.006
HANDLE_BAR = (0.012, 0.16)       # bar handle cross-section and length (doors vertical, drawers horizontal)
CABINET_DOOR_W = 0.6             # one door per this much width (at least one)
WALL_CABINET_PLINTH_M = 0.0
LEG_M = 0.035
# Glass and stone tops for tables with design.material_tags (§4.10: "glass coffee table": the parametric glass top).
TOP_TAG_KEYS: dict[str, str] = {"glass": "glass", "marble": "marble"}
TABLE_TYPES_WITH_TOP_TAGS: tuple[str, ...] = ("table_coffee", "table_dining", "side_table", "console_table", "desk")


def piece_design(piece: dict | None) -> dict:
    """The piece's ``design`` dict ({} when there is none)."""
    design = (piece or {}).get("design")
    return design if isinstance(design, dict) else {}


def front_style_of(design: dict, default: str = DEFAULT_FRONT_STYLE) -> str:
    style = design.get("front_style")
    return style if style in FRONT_STYLES else default


def _front_panel(cx: float, y_face: float, z0: float, fw: float, fh: float, style: str) -> list[Part]:
    """One cabinet front (door or drawer) of ``fw x fh`` standing in front of the carcass face at ``y_face``
    (towards -Y), its bottom at ``z0``: flat slab, shaker frame on a recessed panel, vertical slats on a dark
    backing, or a glass pane in a frame. Every part has role ``front``."""
    y0 = y_face - FRONT_GAP                        # back of the front
    t = FRONT_THICKNESS
    if style == "shaker":
        f = min(SHAKER_FRAME_M, fw * 0.18, fh * 0.18)
        parts = [_box(cx, y0 - SHAKER_PANEL_M / 2.0, z0, fw, SHAKER_PANEL_M, fh, "front", "front")]
        yc = y0 - t / 2.0
        parts += [_box(cx - fw / 2.0 + f / 2.0, yc, z0, f, t, fh, "front", "front"),
                  _box(cx + fw / 2.0 - f / 2.0, yc, z0, f, t, fh, "front", "front"),
                  _box(cx, yc, z0, fw - 2 * f, t, f, "front", "front"),
                  _box(cx, yc, z0 + fh - f, fw - 2 * f, t, f, "front", "front")]
        return parts
    if style == "slatted":
        parts = [_box(cx, y0 - SLAT_BACKING_M / 2.0, z0, fw, SLAT_BACKING_M, fh, "dark", "front")]
        n = max(1, int((fw + SLAT_GAP_M) // (SLAT_W_M + SLAT_GAP_M)))
        sw = (fw - (n - 1) * SLAT_GAP_M) / n
        st = t - SLAT_BACKING_M
        for i in range(n):
            x = cx - fw / 2.0 + sw / 2.0 + i * (sw + SLAT_GAP_M)
            parts.append(_box(x, y0 - SLAT_BACKING_M - st / 2.0, z0, sw, st, fh, "front", "front"))
        return parts
    if style == "glass":
        f = min(GLASS_FRAME_M, fw * 0.2, fh * 0.2)
        yc = y0 - t / 2.0
        return [_box(cx - fw / 2.0 + f / 2.0, yc, z0, f, t, fh, "front", "front"),
                _box(cx + fw / 2.0 - f / 2.0, yc, z0, f, t, fh, "front", "front"),
                _box(cx, yc, z0, fw - 2 * f, t, f, "front", "front"),
                _box(cx, yc, z0 + fh - f, fw - 2 * f, t, f, "front", "front"),
                _box(cx, yc, z0 + f, fw - 2 * f, GLASS_PANE_M, fh - 2 * f, "glass", "front")]
    return [_box(cx, y0 - t / 2.0, z0, fw, t, fh, "front", "front")]


def _handle(cx: float, y_face: float, zc: float, vertical: bool) -> Part:
    """A bar handle on a front whose face is at ``y_face - FRONT_GAP - FRONT_THICKNESS`` (centre ``zc``)."""
    y = y_face - FRONT_GAP - FRONT_THICKNESS - PROUD / 2.0
    t, length = HANDLE_BAR
    if vertical:
        return _box(cx, y, zc - length / 2.0, t, PROUD, length, "handle", "handle")
    return _box(cx, y, zc - t / 2.0, length, PROUD, t, "handle", "handle")


def cabinet_fronts(w: float, y_face: float, z0: float, z1: float, rows: int, cols: int, design: dict,
                   doors: bool = True, handle_at: str = "top") -> list[Part]:
    """The fronts (and handles) of a cabinet face from ``z0`` to ``z1`` in ``rows`` x ``cols`` with 3 mm gaps, in
    the design's front style; door handles stand vertically near the meeting edges (``handle_at`` ``top``: in the
    upper part of the door, a base cabinet; ``bottom``: a wall cabinet), drawer handles horizontally centred."""
    style = front_style_of(design)
    gap = 0.003
    rh = (z1 - z0) / rows
    cw = w / cols
    parts: list[Part] = []
    for r in range(rows):
        for c in range(cols):
            cx = -w / 2.0 + cw * (c + 0.5)
            fz0 = z0 + rh * r + gap / 2.0
            fw, fh = cw - gap, rh - gap
            parts += _front_panel(cx, y_face, fz0, fw, fh, style)
            if doors:
                side = 1.0 if c % 2 == 0 else -1.0          # pairs of doors: handles at the meeting edges
                if cols == 1:
                    side = 1.0
                hx = cx + side * (fw / 2.0 - 0.04)
                hz = fz0 + fh - 0.1 - HANDLE_BAR[1] / 2.0 if handle_at == "top" else fz0 + 0.1 + HANDLE_BAR[1] / 2.0
                hz = min(max(hz, fz0 + HANDLE_BAR[1] / 2.0 + 0.01), fz0 + fh - HANDLE_BAR[1] / 2.0 - 0.01)
                parts.append(_handle(hx, y_face, hz, vertical=fh >= HANDLE_BAR[1] + 0.04))
            else:
                parts.append(_handle(cx, y_face, fz0 + fh / 2.0, vertical=False))
    return parts


def _carcass(w: float, d: float, z0: float, h: float, key: str = "wood") -> tuple[Part, float]:
    """The carcass box (its front face FRONT_GAP + FRONT_THICKNESS behind the footprint's front edge) and that
    face's y."""
    inset = FRONT_GAP + FRONT_THICKNESS
    return _box(0.0, inset / 2.0, z0, w, d - inset, h, key, "body"), -d / 2.0 + inset


def _cols(w: float) -> int:
    return max(1, round(w / CABINET_DOOR_W))


def _sideboard(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Sideboard: wooden legs, a carcass, a row of doors (the design's fronts) and a top."""
    design = piece_design(piece)
    legs = min(0.15, h * 0.2)
    top_t = 0.025
    body, face = _carcass(w, d, legs, h - legs - top_t)
    parts = [body, _box(0.0, 0.0, h - top_t, w, d, top_t, "wood", "top")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.04 - LEG_M / 2.0), sy * (d / 2.0 - 0.04 - LEG_M / 2.0), 0.0, LEG_M,
                              LEG_M, legs, "wood", "leg"))
    parts += cabinet_fronts(w, face, legs + 0.005, h - top_t - 0.005, 1, max(2, _cols(w)), design)
    return parts


def _shoe_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Shoe cabinet: plinth, carcass and two or three tilt-out flaps over the whole width (horizontal handles)."""
    design = piece_design(piece)
    plinth = min(0.06, h * 0.08)
    body, face = _carcass(w, d, plinth, h - plinth)
    rows = 3 if h >= 0.9 else 2
    return ([_box(0.0, 0.02, 0.0, w - 0.04, d - 0.06, plinth, "dark", "plinth"), body]
            + cabinet_fronts(w, face, plinth + 0.003, h - 0.003, rows, 1, design, doors=False))


def _display_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Display cabinet: plinth, carcass, shelves seen through the fronts (glass unless the design says another
    front style), two doors."""
    design = dict(piece_design(piece))
    design.setdefault("front_style", "glass")
    if design.get("front_style") is None:
        design["front_style"] = "glass"
    plinth = min(0.08, h * 0.05)
    inset = FRONT_GAP + FRONT_THICKNESS
    t = 0.018
    face = -d / 2.0 + inset
    parts = [_box(0.0, 0.0, 0.0, w - 0.04, d - 0.06, plinth, "dark", "plinth"),
             _box(-(w / 2.0 - t / 2.0), inset / 2.0, plinth, t, d - inset, h - plinth, "wood", "side"),
             _box(w / 2.0 - t / 2.0, inset / 2.0, plinth, t, d - inset, h - plinth, "wood", "side"),
             _box(0.0, d / 2.0 - t / 2.0, plinth, w - 2 * t, t, h - plinth, "wood", "back"),
             _box(0.0, inset / 2.0, plinth, w - 2 * t, d - inset - t, t, "wood", "bottom"),
             _box(0.0, inset / 2.0, h - t, w - 2 * t, d - inset - t, t, "wood", "top")]
    z = plinth + SHELF_PITCH
    while z < h - t - 0.2:
        parts.append(_box(0.0, inset / 2.0 - t / 2.0, z, w - 2 * t, d - inset - 2 * t, 0.012, "glass", "shelf"))
        z += SHELF_PITCH
    parts += cabinet_fronts(w, face, plinth + 0.003, h - 0.003, 1, 2 if w >= 0.7 else 1, design)
    return parts


def _tall_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Tall (pantry) cabinet: plinth, carcass, a lower door of two thirds and an upper one per column. 29 Oct 2026
    (UL114 B5): a bathroom's storage column of an open-lit family is the open niche column with its toiletries
    (``bath_parts.open_column_parts``)."""
    look = (piece or {}).get("bath_look") if isinstance((piece or {}).get("bath_look"), dict) else {}
    if look.get("column") == "open_lit":
        from wenart.blender import bath_parts as BT
        return BT.open_column_parts(w, d, h)
    design = piece_design(piece)
    plinth = min(0.1, h * 0.05)
    body, face = _carcass(w, d, plinth, h - plinth, "painted")
    parts = [_box(0.0, 0.03, 0.0, w, d - 0.06, plinth, "dark", "plinth"), body]
    split = plinth + (h - plinth) * 2.0 / 3.0
    cols = max(1, round(w / 0.45))
    parts += cabinet_fronts(w, face, plinth + 0.003, split, 1, cols, design)
    parts += cabinet_fronts(w, face, split, h - 0.003, 1, cols, design, handle_at="bottom")
    return parts


def _wall_cabinet(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Wall cabinet (its bottom at z = 0 of its own frame; ``furniture.py`` hangs it at ``mount_bottom_m``):
    carcass and a row of doors with their handles low."""
    design = piece_design(piece)
    body, face = _carcass(w, d, 0.0, h, "painted")
    return [body] + cabinet_fronts(w, face, 0.003, h - 0.003, 1, _cols(w), design, handle_at="bottom")


def _counter_m10(w: float, d: float, h: float, island: bool = False, piece: dict | None = None) -> list[Part]:
    """Kitchen counter run or island (Milestone 6 boxes): plinth, carcass, worktop, and the design's fronts and
    handles over the base (one door per 0.6 m; handles in the upper part)."""
    design = piece_design(piece)
    top_t = 0.04
    plinth_h = min(0.1, h * 0.12)
    inset = 0.03
    if island:
        carcass = _box(0.0, 0.0, plinth_h, w - 2 * inset, d - 2 * inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, 0.0, 0.0, w - 4 * inset, d - 4 * inset, plinth_h, "dark", "plinth")
    else:
        carcass = _box(0.0, inset / 2.0, plinth_h, w, d - inset, h - top_t - plinth_h, "painted", "body")
        plinth = _box(0.0, inset, 0.0, w, d - 2 * inset, plinth_h, "dark", "plinth")
    front_y = -d / 2.0 + inset
    parts = [plinth, carcass, _box(0.0, 0.0, h - top_t, w, d, top_t, "worktop", "top")]
    parts += cabinet_fronts(w, front_y, plinth_h + 0.01, h - top_t - 0.02, 1, _cols(w), design)
    return parts


def _vanity(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """A washbasin with the vanity look (docs/milestone10.md §4.4: a drawn washbasin at least 0.45 m deep; its
    type stays ``washbasin``): a wall-hung cabinet with the design's fronts under a ceramic top with an inset
    basin and a tap. Fix round after P3, part 2 (17 Oct 2026): the cabinet is hollow above the basin bottom
    (``open_carcass``; its solid body had closed the bowl 3 cm under the rim)."""
    design = piece_design(piece)
    top_t = 0.03
    basin_h = min(0.15, h * 0.2)
    bottom = min(0.3, h * 0.35)                     # wall-hung: free floor under the cabinet
    body, face = _carcass(w, d, bottom, h - top_t - bottom)
    inset = FRONT_GAP + FRONT_THICKNESS                 # the box of ``_carcass``, hollow above the basin bottom
    parts = open_carcass(0.0, inset / 2.0, bottom, w, d - inset, h - top_t - bottom, h - basin_h - BASIN_CLEAR_M,
                         body["key"])
    parts.append(_box(0.0, d / 2.0 - 0.01, 0.0, w * 0.3, 0.02, bottom, "dark", "back"))   # the wall bracket
    bw, bd = min(w - 0.12, 0.5), min(d - 0.12, 0.36)
    sx, sy = (w - bw) / 2.0, (d - bd) / 2.0
    z_top = h - top_t
    parts += [_box(0.0, -d / 2.0 + sy / 2.0, z_top, w, sy, top_t, "ceramic", "top"),
              _box(0.0, d / 2.0 - sy / 2.0, z_top, w, sy, top_t, "ceramic", "top"),
              _box(-w / 2.0 + sx / 2.0, 0.0, z_top, sx, bd, top_t, "ceramic", "top"),
              _box(w / 2.0 - sx / 2.0, 0.0, z_top, sx, bd, top_t, "ceramic", "top")]
    parts += _basin(0.0, 0.0, h - basin_h, bw, bd, basin_h, 0.012, "ceramic")
    parts.append(_cylinder_z(0.0, d / 2.0 - sy / 2.0, h, 0.012, 0.012, 0.15, "steel", "tap", n=12))
    parts += cabinet_fronts(w, face, bottom + 0.003, z_top - 0.003, 1, 1 if w < 0.8 else 2, design, doors=w >= 0.8)
    return parts


def _washbasin_m10(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The Milestone 4 pedestal basin, or the vanity look when the design says ``vanity``; 29 Oct 2026 (UL114,
    UL123, UL124): the floating vanity of the piece's bathroom look (``bath_parts.vanity_parts``)."""
    look = (piece or {}).get("bath_look") if isinstance((piece or {}).get("bath_look"), dict) else {}
    if look.get("made_to_measure") and look.get("vanity") in ("stone_slab", "fluted", "curved"):
        from wenart.blender import bath_parts as BT
        return BT.vanity_parts(w, d, float(look.get("top_m") or h), look)
    if piece_design(piece).get("vanity"):
        return _vanity(w, d, h, piece)
    return _washbasin(w, d, h)


def _built_in_wardrobe(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """A built-in wardrobe (docs/milestone10.md §4.4: a drawn wardrobe spanning wall to wall; its type stays
    ``wardrobe``): fronts over the whole width (no carcass sides showing), a recessed plinth and a filler
    panel at the top."""
    design = piece_design(piece)
    plinth = 0.08
    filler = 0.06
    body, face = _carcass(w, d, plinth, h - plinth)
    parts = [_box(0.0, 0.04, 0.0, w, d - 0.08, plinth, "dark", "plinth"), body,
             _box(0.0, face - FRONT_GAP - FRONT_THICKNESS / 2.0, h - filler, w, FRONT_THICKNESS, filler, "front",
                  "front")]
    parts += cabinet_fronts(w, face, plinth + 0.003, h - filler - 0.003, 1, max(2, round(w / 0.5)), design)
    return parts


def _wardrobe_m10(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """The Milestone 4 wardrobe, built-in when the design says ``built_in``, with the design's fronts when it
    names a front style."""
    design = piece_design(piece)
    if design.get("built_in"):
        return _built_in_wardrobe(w, d, h, piece)
    return _wardrobe(w, d, h, piece)                 # Milestone 13: the v2 family, the design's front style


def _table_m10(w: float, d: float, h: float, piece: dict | None = None, desk: bool = False,
               shelf: bool = False) -> list[Part]:
    """The table family (v2 since Milestone 13); a ``glass`` or ``marble`` material tag of the design (§4.10:
    "glass coffee table") gives that top, ``metal`` steel legs and apron; ``shelf`` (coffee tables) or a glass top
    adds a lower wooden shelf."""
    parts = _table(w, d, h, desk=desk)
    tags = piece_design(piece).get("material_tags") or ()
    top_key = next((TOP_TAG_KEYS[t] for t in tags if t in TOP_TAG_KEYS), None)
    for p in parts:
        if p["role"] == "top" and top_key:
            p["key"] = top_key
        if p["role"] in ("leg", "apron") and "metal" in tags:
            p["key"] = "steel"
    if (top_key == "glass" or shelf) and not desk:  # a glass top shows its frame: a lower wooden shelf
        leg = min(0.06, w * 0.08, d * 0.08)
        inset = min(0.04, w * 0.05, d * 0.05)
        sw, sd = w - 2 * (inset + leg), d - 2 * (inset + leg)
        if sw > 0.1 and sd > 0.1:
            parts.append(_box(0.0, 0.0, min(0.12, h * 0.25), sw, sd, 0.02, "wood", "shelf"))
    return parts


def _console_table(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Console table: a narrow top, four slim legs and a lower shelf (tags as ``_table_m10``)."""
    parts = _table_m10(w, d, h, piece)
    leg = min(0.06, w * 0.08, d * 0.08)
    inset = min(0.04, w * 0.05, d * 0.05)
    sw, sd = w - 2 * (inset + leg), d - 2 * (inset + leg)
    if sw > 0.1 and sd > 0.05 and not any(p["role"] == "shelf" for p in parts):
        parts.append(_box(0.0, 0.0, min(0.15, h * 0.2), sw, sd, 0.02, "wood", "shelf"))
    return parts


# Corner sofa: the two rectangles of wenart.furniture.schemas.l_parts (the one geometry source, docs/milestone10.md
# §1.6b row 15). That module needs jsonschema, which Blender's Python lacks, and the build's fingerprint covers only
# the scene code, so the builder keeps this copy of the formula; tests/test_blender_furniture.py checks that both
# give the same rectangles (schemas.L_SEAT_DEPTH_M / L_CHAISE_WIDTH_M equal these defaults).
L_SEAT_DEPTH_M = 0.9
L_CHAISE_WIDTH_M = 0.9


def l_parts(size, chaise_side, chaise_depth, seat_depth=None, chaise_width=None):
    """``[(x0, x1, y0, y1) main seat, (x0, x1, y0, y1) chaise]`` of a corner sofa in its frame
    (``wenart.furniture.schemas.l_parts``): the main seat along the back (+Y) over the whole width, ``seat_depth``
    deep, the chaise ``chaise_width`` wide on ``chaise_side`` (right = +X) over ``chaise_depth`` from the back."""
    w, d = float(size[0]), float(size[1])
    depth = min(float(chaise_depth), d) if chaise_depth else d
    seat = min(float(seat_depth) if seat_depth else L_SEAT_DEPTH_M, depth)
    cw = min(float(chaise_width) if chaise_width else L_CHAISE_WIDTH_M, w / 2.0)
    main = (-w / 2.0, w / 2.0, d / 2.0 - seat, d / 2.0)
    if chaise_side == "left":
        chaise = (-w / 2.0, -w / 2.0 + cw, d / 2.0 - depth, d / 2.0)
    else:
        chaise = (w / 2.0 - cw, w / 2.0, d / 2.0 - depth, d / 2.0)
    return [main, chaise]


def _sofa_corner(w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Corner sofa (``shape: L``): the main seat along the back over the whole width and the long seat (chaise) on
    ``chaise_side`` from ``l_parts`` (default right, the schema's default sizes); a back along +Y, an arm at the
    end away from the chaise, seat cushions on both parts."""
    piece = piece or {}
    side = piece.get("chaise_side") if piece.get("chaise_side") in ("left", "right") else "right"
    main, chaise = l_parts((w, d), side, piece.get("chaise_depth"), piece.get("seat_depth"),
                           piece.get("chaise_width"))
    back_t = min(0.2, (main[3] - main[2]) * 0.25)
    arm_w = min(0.15, w * 0.06)
    seat_h = sofa_seat_height(h)
    arm_h = min(0.65, h * 0.8)
    mx0, mx1, my0, my1 = main
    cx0, cx1, cy0, cy1 = chaise
    seat_y0, seat_y1 = my0, my1 - back_t
    parts = [_box(0.0, d / 2.0 - back_t / 2.0, 0.0, w, back_t, h, "fabric", "back")]
    # The arm on the side away from the chaise; the main seat base between the arm and the chaise.
    if side == "right":
        arm_x = mx0 + arm_w / 2.0
        base_x0, base_x1 = mx0 + arm_w, cx0
    else:
        arm_x = mx1 - arm_w / 2.0
        base_x0, base_x1 = cx1, mx1 - arm_w
    parts.append(_box(arm_x, (seat_y0 + seat_y1) / 2.0, 0.0, arm_w, seat_y1 - seat_y0, arm_h, "fabric", "arm"))
    parts.append(_box((base_x0 + base_x1) / 2.0, (seat_y0 + seat_y1) / 2.0, 0.0, base_x1 - base_x0,
                      seat_y1 - seat_y0, seat_h - 0.1, "fabric", "body"))
    ch_y1 = my1 - back_t
    parts.append(_box((cx0 + cx1) / 2.0, (cy0 + ch_y1) / 2.0, 0.0, cx1 - cx0, ch_y1 - cy0, seat_h - 0.1, "fabric",
                      "body"))
    seat_w = base_x1 - base_x0
    n = max(1, round(seat_w / 0.75))
    cw = seat_w / n
    for i in range(n):
        parts.append(_box(base_x0 + cw * (i + 0.5), (seat_y0 + seat_y1) / 2.0, seat_h - 0.1, cw - 0.03,
                          seat_y1 - seat_y0 - 0.04, 0.1, "fabric", "cushion"))
    parts.append(_box((cx0 + cx1) / 2.0, (cy0 + ch_y1) / 2.0, seat_h - 0.1, cx1 - cx0 - 0.03, ch_y1 - cy0 - 0.04,
                      0.1, "fabric", "cushion"))
    return parts


def sofa_corner_parts_info(piece: dict) -> dict:
    """The corner sofa's record for the manifest: the side and both rectangles (piece frame)."""
    fp = piece["footprint"]
    side = piece.get("chaise_side") if piece.get("chaise_side") in ("left", "right") else "right"
    rects = l_parts(fp["size"], side, piece.get("chaise_depth"), piece.get("seat_depth"), piece.get("chaise_width"))
    return {"chaise_side": side, "chaise_side_assumed": piece.get("chaise_side") not in ("left", "right"),
            "rectangles": [[round(v, 4) for v in r] for r in rects]}


def _chaise(w: float, d: float, h: float) -> list[Part]:
    """Chaise longue: a seat along the depth, a raised back at the head end (+Y), one arm and a long cushion."""
    back_t = min(0.15, d * 0.1)
    seat_h = sofa_seat_height(h)
    arm_w = min(0.12, w * 0.15)
    seat_d = d - back_t
    return [_box(0.0, d / 2.0 - back_t / 2.0, 0.0, w, back_t, h, "fabric", "back"),
            _box(-(w / 2.0 - arm_w / 2.0), -back_t / 2.0 + seat_d * 0.2, 0.0, arm_w, seat_d * 0.6, seat_h + 0.12,
                 "fabric", "arm"),
            _box(arm_w / 2.0, -back_t / 2.0, 0.0, w - arm_w, seat_d, seat_h - 0.1, "fabric", "body"),
            _box(arm_w / 2.0, -back_t / 2.0, seat_h - 0.1, w - arm_w - 0.03, seat_d - 0.04, 0.1, "fabric", "cushion")]


def _ottoman(w: float, d: float, h: float) -> list[Part]:
    """Upholstered ottoman on four short legs."""
    legs = min(0.08, h * 0.2)
    parts = [_box(0.0, 0.0, legs, w, d, h - legs - 0.06, "fabric", "body"),
             _box(0.0, 0.0, h - 0.06, w - 0.02, d - 0.02, 0.06, "fabric", "cushion")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.05), sy * (d / 2.0 - 0.05), 0.0, LEG_M, LEG_M, legs, "wood", "leg"))
    return parts


def _bench(w: float, d: float, h: float) -> list[Part]:
    """Bench: a padded seat on a wooden frame with four legs."""
    pad = min(0.06, h * 0.15)
    frame_t = 0.03
    leg = min(0.045, d * 0.15)
    parts = [_box(0.0, 0.0, h - pad - frame_t, w, d, frame_t, "wood", "top"),
             _box(0.0, 0.0, h - pad, w - 0.01, d - 0.01, pad, "fabric", "cushion")]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - 0.04 - leg / 2.0), sy * (d / 2.0 - 0.03 - leg / 2.0), 0.0, leg, leg,
                              h - pad - frame_t, "wood", "leg"))
    return parts


def _bar_stool(w: float, d: float, h: float) -> list[Part]:
    """Bar stool: a round seat, four legs inside the seat's footprint and footrest bars."""
    seat_t = 0.05
    leg = 0.025
    r = min(w, d) / 2.0
    off = r * 0.62
    parts = [_cylinder_z(0.0, 0.0, h - seat_t, w / 2.0, d / 2.0, seat_t, "fabric", "top", n=32)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * off / math.sqrt(2.0), sy * off / math.sqrt(2.0), 0.0, leg, leg, h - seat_t,
                              "steel", "leg"))
    span = 2.0 * off / math.sqrt(2.0)
    rest = min(0.3, h * 0.4)
    for sy in (-1, 1):
        parts.append(_box(0.0, sy * off / math.sqrt(2.0), rest, span, 0.015, 0.015, "steel", "rest"))
    return parts


def _office_chair(w: float, d: float, h: float) -> list[Part]:
    """Office chair: a five-star base with castors, a gas lift, a seat, a back at +Y and two armrests; the seat
    fills the footprint (the star stays inside it)."""
    seat_h = min(0.48, h * 0.5)
    seat_t = 0.08
    r = min(w, d) / 2.0 - 0.02
    parts = []
    for k in range(5):
        a = math.radians(90.0 + 72.0 * k)
        mid = (math.cos(a) * r / 2.0, math.sin(a) * r / 2.0)
        verts, faces = geom2d.box((mid[0], mid[1], 0.06), (r, 0.04, 0.03), math.degrees(a))
        parts.append({"verts": verts, "faces": faces, "key": "dark", "role": "base"})
        parts.append(_cylinder_z(math.cos(a) * (r - 0.02), math.sin(a) * (r - 0.02), 0.0, 0.022, 0.022, 0.045,
                                 "dark", "castor", n=10))
    parts.append(_cylinder_z(0.0, 0.0, 0.045, 0.025, 0.025, seat_h - seat_t - 0.045, "steel", "pole", n=12))
    back_t = 0.05
    parts.append(_box(0.0, -back_t / 2.0, seat_h - seat_t, w - 0.06, d - back_t, seat_t, "fabric", "cushion"))
    parts.append(_box(0.0, d / 2.0 - back_t / 2.0, seat_h + 0.05, w * 0.85, back_t, h - seat_h - 0.05, "fabric",
                      "back"))
    for sx in (-1, 1):
        parts.append(_box(sx * (w / 2.0 - 0.02), -0.02, seat_h + 0.18, 0.04, d * 0.5, 0.03, "dark", "arm"))
        parts.append(_box(sx * (w / 2.0 - 0.02), 0.0, seat_h, 0.02, 0.03, 0.18, "dark", "arm"))
    return parts


def _crib(w: float, d: float, h: float) -> list[Part]:
    """Crib (cot): four corner posts, top and bottom rails, vertical slats on all sides, a mattress base and a
    mattress (bedding) about 0.3 m above the floor."""
    post = 0.045
    rail = 0.035
    base_z = min(0.3, h * 0.35)
    parts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - post / 2.0), sy * (d / 2.0 - post / 2.0), 0.0, post, post, h, "wood",
                              "post"))
    for y in (-(d / 2.0 - post / 2.0), d / 2.0 - post / 2.0):
        for z in (base_z - rail, h - rail):
            parts.append(_box(0.0, y, z, w - 2 * post, rail * 0.8, rail, "wood", "rail"))
    for x in (-(w / 2.0 - post / 2.0), w / 2.0 - post / 2.0):
        for z in (base_z - rail, h - rail):
            parts.append(_box(x, 0.0, z, rail * 0.8, d - 2 * post, rail, "wood", "rail"))
    slat, pitch = 0.02, 0.085
    for y in (-(d / 2.0 - post / 2.0), d / 2.0 - post / 2.0):
        n = max(1, int((w - 2 * post) / pitch))
        for i in range(n):
            x = -w / 2.0 + post + (i + 0.5) * (w - 2 * post) / n
            parts.append(_box(x, y, base_z, slat, slat, h - rail - base_z, "wood", "slat"))
    parts.append(_box(0.0, 0.0, base_z - rail, w - 2 * post, d - 2 * post, 0.02, "wood", "bottom"))
    parts.append(_superellipsoid(0.0, 0.0, base_z - rail + 0.02, w - 2 * post - 0.02, d - 2 * post - 0.02, 0.1, 0.15,
                                 0.1, "bedding", "mattress"))
    return parts


def _bunk_bed(w: float, d: float, h: float) -> list[Part]:
    """Bunk bed: four posts, two frames with mattresses (lower 0.3 m, upper 1.3 m or 60 % of the height), a guard
    rail on the upper bunk's front (-Y) and a ladder at the foot end of the front."""
    post = 0.06
    frame_t = 0.12
    lower = min(0.3, h * 0.2)
    upper = max(lower + 0.9, min(1.3, h * 0.6)) if h > lower + 1.0 else h * 0.6
    parts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            parts.append(_box(sx * (w / 2.0 - post / 2.0), sy * (d / 2.0 - post / 2.0), 0.0, post, post, h, "wood",
                              "post"))
    for z in (lower, upper):
        for x in (-(w / 2.0 - post / 2.0), w / 2.0 - post / 2.0):
            parts.append(_box(x, 0.0, z - frame_t, post * 0.8, d - 2 * post, frame_t, "wood", "rail"))
        for y in (-(d / 2.0 - post / 2.0), d / 2.0 - post / 2.0):
            parts.append(_box(0.0, y, z - frame_t, w - 2 * post, post * 0.8, frame_t, "wood", "rail"))
        parts.append(_box(0.0, 0.0, z - 0.03, w - 2 * post, d - 2 * post, 0.02, "wood", "bottom"))
        parts.append(_superellipsoid(0.0, 0.0, z - 0.01, w - 2 * post - 0.02, d - 2 * post - 0.02, 0.15, 0.15, 0.1,
                                     "bedding", "mattress"))
    # Guard rail of the upper bunk along the long side; the ladder at the foot end.
    for z in (upper + 0.15, h - 0.04):
        parts.append(_box(-w / 2.0 + post + 0.01, 0.0, z, 0.03, d - 2 * post, 0.03, "wood", "rail"))
    lx = w / 2.0 - post - 0.03
    ly0, ly1 = -d / 2.0 + post, -d / 2.0 + post + 0.4
    for y in (ly0 + 0.015, ly1 - 0.015):
        parts.append(_box(lx, y, 0.0, 0.03, 0.03, upper + 0.3, "wood", "ladder"))
    z = 0.3
    while z < upper:
        parts.append(_box(lx, (ly0 + ly1) / 2.0, z, 0.025, ly1 - ly0 - 0.06, 0.025, "wood", "ladder"))
        z += 0.27
    return parts


# --------------------------------------------------------------------------
# Doors and windows (docs/milestone10.md §4.7): pure parts in the opening's frame
# --------------------------------------------------------------------------
#
# Frame of an opening (as wenart.blender.shell builds them): x along the wall (the opening from -width/2 to
# +width/2), y across the wall (0 = the wall centre line, the wall from -thickness/2 to +thickness/2), z up from the
# opening's bottom. Keys: ``frame`` (door frame, window frame), ``leaf``, ``glass``, ``handle``, ``rail``
# (sliding / barn track), ``sill`` (inside window sill). shell.build_openings calls ``door_parts`` /
# ``window_parts`` with the looks of ``wenart.blender.looks`` (docs/milestone10.md §1.6b row 20).

DOOR_STYLES: tuple[str, ...] = ("flush", "shaker_panel", "glazed", "pocket", "sliding", "barn", "double", "entrance",
                                "folding", "glazed_sliding", "sectional")
# 26 Oct 2026 (architect D5, user on real06: "these sections not making sense": a 2.95 m flat oak leaf in the facade):
# the kinds of door an architect gives an outside or a wide door (``looks.door_look`` passes ``glazed``, ``leaves``,
# ``sidelights``): glazed leaves for a double or folding door (French doors), a glazed sliding door in the frame
# (``glazed_sliding``: panels of at most ``LEAF_MAX_M`` on two tracks, the end panels on the outer track fixed), the
# entrance door with glazed side lights beside one leaf when the opening is wider than ``SINGLE_LEAF_MAX_M``, a
# sectional garage door (``sectional``: horizontal sections with ribs), sliding leaves parting in the middle. Typical
# joinery sizes (assumed: no drawing gives them).
LEAF_MAX_M = 1.2                 # no sliding panel wider than this (= architect_actions.LEAF_MAX_M)
SLIDING_PANEL_T = 0.035          # a glazed sliding panel's thickness
SLIDING_TRACK_GAP_M = 0.006      # between the two tracks of a glazed sliding door
SLIDING_PANEL_OVERLAP_M = 0.05   # two panels on different tracks overlap this much when closed
SLIDING_STILE_M = 0.07           # a glazed sliding panel's stiles and top rail
SECTIONAL_LEAF_T = 0.045
SECTION_H_M = 0.5                # a sectional door's sections about this tall
SINGLE_LEAF_MAX_M = 1.25         # an entrance leaf wider than this gets side lights (with ``sidelights``)
ENTRANCE_LEAF_W_M = 1.0          # ... and is this wide
SIDELIGHT_MIN_M = 0.2            # a side light narrower than this is no side light: the leaf takes the width
SIDELIGHT_BASE_M = 0.25          # a solid panel under a side light's glass
LEAF_GAP_M = 0.002               # between two leaves of a pair or a folding door
DOOR_FRAME_W = 0.05
DOOR_LEAF_T = 0.04
ENTRANCE_LEAF_T = 0.065
DOOR_PANEL_FRAME_M = 0.11        # shaker panel door: stiles and rails
DOOR_PANEL_PROUD_M = 0.006
GLAZED_FRAME_M = 0.09
SLIDING_OVERLAP_M = 0.05         # a surface-mounted sliding / barn leaf covers the opening plus this per side
SLIDING_STANDOFF_M = 0.012       # off the wall face
RAIL_H = 0.04
LEVER_HEIGHT_M = 1.0
# Door stops (fix round after P3, 16-17 Oct 2026): a closed leaf stood 5 mm off its jambs (10 mm under the head of a
# Milestone 10 door) with no stop, so the sun lit a straight slit round every closed door and the camera saw the
# terrace through it (pod P3: cam_r_L1_koridor_2_2, depth 196 m). A stop on the jambs and the head (no threshold
# stop: the M10 leaf reaches the floor, light under a door is real) covers the slit with 10 mm (5 mm at the M10
# head) of overlap, on the leaf face away from the swing: the face the leaf closes against. Typical joinery sizes
# (assumed: no drawing gives them); a stop is never thinner than DOOR_STOP_MIN_T_M, even in a wall as thin as the leaf.
DOOR_STOP_W_M = 0.015
DOOR_STOP_T_M = 0.012
DOOR_STOP_MIN_T_M = 0.004
DOOR_ASTRAGAL_W_M = 0.03         # the strip over the meeting stiles of a double or folding door (on the stop face)
# Window frames by material (docs/milestone10.md §4.7): (frame width, frame depth) in metres, typical profiles
# (assumed; no drawing gives them).
WINDOW_PROFILES: dict[str, tuple[float, float]] = {
    "pvc_white": (0.065, 0.07), "aluminium_anthracite": (0.05, 0.065), "steel_black": (0.035, 0.045),
    "dark_bronze": (0.045, 0.06), "oak": (0.068, 0.068), "painted_metal_white": (0.05, 0.06),
}
DEFAULT_WINDOW_PROFILE = (0.05, 0.06)
MULLION_W = 0.04
INSIDE_SILL = {"depth_proud": 0.03, "thickness": 0.025, "ears": 0.02}


def door_style_of(look: dict | None) -> str:
    style = (look or {}).get("door_style")
    return style if style in DOOR_STYLES else "flush"


def _leaf_box(cx: float, z0: float, lw: float, lh: float, t: float, y: float = 0.0) -> Part:
    return _box(cx, y, z0, lw, t, lh, "leaf", "leaf")


GLAZING_GROOVE_M = 0.002        # the glass of a D5 leaf or panel sits this deep in its stiles and rails


MUNTIN_W_M = 0.025              # 29 Oct 2026 (D3): a divided-lite door's glazing bars


def _glazed_leaf(cx: float, y: float, lw: float, lh: float, t: float, frame: float = GLAZED_FRAME_M,
                 groove: float = 0.0, lites: Optional[Sequence[int]] = None) -> list[Part]:
    """A glazed leaf ``lw`` wide centred on ``cx`` (``y`` across the wall): two stiles, a bottom rail 1.6 times and a
    top rail as wide as a stile (``frame``, at most a fifth of the leaf) and the glass between them, ``groove`` deep
    in them (0 for the ``glazed`` style as it always was). 29 Oct 2026 (D3, docs/reference_details_20261029.md):
    ``lites`` ``(columns, rows)`` divides the glass with glazing bars (role ``muntin``, the leaf's key) through it."""
    f = min(frame, lw * 0.2)
    parts = [_box(cx - (lw / 2.0 - f / 2.0), y, 0.0, f, t, lh, "leaf", "leaf"),
             _box(cx + lw / 2.0 - f / 2.0, y, 0.0, f, t, lh, "leaf", "leaf"),
             _box(cx, y, 0.0, lw - 2 * f, t, f * 1.6, "leaf", "leaf"),
             _box(cx, y, lh - f, lw - 2 * f, t, f, "leaf", "leaf"),
             _box(cx, y, f * 1.6 - groove, lw - 2 * f + 2 * groove, 0.008, lh - f * 2.6 + 2 * groove, "glass", "glass")]
    if lites:
        cols, rows = max(1, int(lites[0])), max(1, int(lites[1]))
        gw, gz0, gh = lw - 2 * f, f * 1.6, lh - f * 2.6
        bt = min(t, 0.03)
        for i in range(1, cols):
            parts.append(_box(cx - gw / 2.0 + gw * i / cols, y, gz0, MUNTIN_W_M, bt, gh, "leaf", "muntin"))
        for j in range(1, rows):
            parts.append(_box(cx, y, gz0 + gh * j / rows - MUNTIN_W_M / 2.0, gw, bt, MUNTIN_W_M, "leaf", "muntin"))
    return parts


def sliding_panels(lw: float, thickness: float, leaves: Optional[int] = None) -> dict:
    """The panels of a glazed sliding door in a clear width ``lw`` (pure): ``n`` panels (``leaves``, else as many as
    keep each at most ``LEAF_MAX_M``, at least two), on two tracks ``d`` off the wall centre when the wall is deep
    enough for both and a stop (overlapping ``SLIDING_PANEL_OVERLAP_M``), else side by side on one line (``d`` 0,
    ``LEAF_GAP_M`` apart); ``width`` of a panel, ``centres`` along x, ``fixed`` the end panels on the outer track."""
    n = int(leaves) if isinstance(leaves, int) and not isinstance(leaves, bool) and leaves >= 2 else \
        max(2, int(math.ceil(float(lw) / LEAF_MAX_M - 1e-9)))
    d = SLIDING_PANEL_T / 2.0 + SLIDING_TRACK_GAP_M / 2.0
    staggered = d + SLIDING_PANEL_T / 2.0 + DOOR_STOP_MIN_T_M <= float(thickness) / 2.0 + 1e-9
    d = d if staggered else 0.0
    ov = SLIDING_PANEL_OVERLAP_M if staggered else -LEAF_GAP_M
    pw = (float(lw) + (n - 1) * ov) / n
    centres = [-float(lw) / 2.0 + pw / 2.0 + i * (pw - ov) for i in range(n)]
    return {"n": n, "d": d, "staggered": staggered, "width": pw, "centres": centres,
            "fixed": sorted({i for i in (0, n - 1) if i % 2 == 0})}


def entrance_sections(width: float, frame_w: float = DOOR_FRAME_W) -> list[tuple[str, float, float]]:
    """``[(kind, x0, x1)]``: the clear spans of an entrance door with side lights between its jambs and mullions
    (pure): one ``leaf`` span ``ENTRANCE_LEAF_W_M`` (+ 0.01 clearance) wide and ``light`` spans for the rest, a
    mullion ``frame_w`` wide between two spans; two balanced side lights when the rest is over 0.9 m, else one beside
    the leaf; the whole width one leaf when a side light would be narrower than ``SIDELIGHT_MIN_M``."""
    a, b = -float(width) / 2.0 + frame_w, float(width) / 2.0 - frame_w
    span = ENTRANCE_LEAF_W_M + 0.01
    rest = (b - a) - span
    if rest - frame_w < SIDELIGHT_MIN_M:
        return [("leaf", a, b)]
    if rest > 0.9 and (rest - 2 * frame_w) / 2.0 >= SIDELIGHT_MIN_M:
        light = (rest - 2 * frame_w) / 2.0
        return [("light", a, a + light), ("leaf", a + light + frame_w, a + light + frame_w + span),
                ("light", b - light, b)]
    return [("leaf", a, a + span), ("light", a + span + frame_w, b)]


def door_stop_boxes(width: float, height: float, frame_w: float, face_y: float, thickness: float,
                    side: float) -> list[tuple[float, float, float, float, float, float]]:
    """``[(cx, cy, z0, w, d, h)]`` of a door's stops in the opening's frame (pure; fix round after P3, 16-17 Oct 2026).

    What: two jamb stops (``DOOR_STOP_W_M`` wide, from the floor to the head) and a head stop between them, each
    ``DOOR_STOP_T_M`` thick, on the ``side`` face (+1 / -1: the y side), from the leaf face ``face_y`` (its distance
    from the wall centre line, proud panels included) outwards.
    Why: the leaf of a closed door is a few mm smaller than its frame; without a stop that slit runs straight through
    the wall and leaks light and view (``DOOR_STOP_W_M``).
    How: the stop's outer face is clamped to the wall face (``thickness / 2``) and never thinner than
    ``DOOR_STOP_MIN_T_M`` (a leaf that fills the wall depth: the stop stands that much proud); no head stop when the
    opening is narrower than the two jamb stops."""
    s = -1.0 if float(side) < 0 else 1.0
    y0 = max(0.0, float(face_y))
    y1 = max(y0 + DOOR_STOP_MIN_T_M, min(y0 + DOOR_STOP_T_M, float(thickness) / 2.0))
    cy, d = s * (y0 + y1) / 2.0, y1 - y0
    inner = float(width) / 2.0 - float(frame_w)           # the jamb's inner face
    top = float(height) - float(frame_w)                  # the head's underside
    boxes = [(-(inner - DOOR_STOP_W_M / 2.0), cy, 0.0, DOOR_STOP_W_M, d, top),
             (inner - DOOR_STOP_W_M / 2.0, cy, 0.0, DOOR_STOP_W_M, d, top)]
    head_w = 2.0 * (inner - DOOR_STOP_W_M)
    if head_w > 1e-6:
        boxes.append((0.0, cy, top - DOOR_STOP_W_M, head_w, d, DOOR_STOP_W_M))
    return boxes


# 29 Oct 2026 (user: "Better door models needed"; UL89): the parametric door as a real product where no library model
# fits (``looks.door_product``): the leaf's face detail, an architrave on the room faces, three hinges. Typical joinery
# sizes (assumed: no drawing gives them).
LEAF_GROOVE_W_M = 0.004          # a routed V-groove's width on the leaf face ...
LEAF_GROOVE_D_M = 0.003          # ... and its depth
LEAF_LINE_INSET_M = 0.10         # a lined leaf: the routed line this far in from the leaf's edges (at most 15 %)
ARCHITRAVE_W_M = 0.065           # the architrave (casing) round the opening on a wall face: its width ...
ARCHITRAVE_T_M = 0.018           # ... how far it stands proud of the wall face ...
ARCHITRAVE_REVEAL_M = 0.008      # ... and how far its inner edge stands back from the jamb's inner face
HINGE_SIZE_M = (0.014, 0.014, 0.10)   # a hinge knuckle (x, y, z) on the swing face at the leaf's hinge edge
HINGE_Z_M = (0.18, None, 0.28)   # the hinges' bottoms: 0.18 m up, the middle, 0.28 m under the leaf's top
FINE_GROOVE_PITCH_M = 0.06       # 29 Oct 2026 (R28): fine vertical grooves this far apart ...
FINE_GROOVE_W_M = 0.003          # ... and this wide
LOCK_ROSE_DROP_M = 0.072         # 29 Oct 2026 (R28): the lock rose this far under the lever (the DIN 72 mm centres)
LOCK_ROSE_R_M = 0.019
PIVOT_PULL_M = 1.2               # 29 Oct 2026 (D5): a pivot entrance door's long bar pull
LINING_T_M = 0.018               # 29 Oct 2026 (UL122): a reveal lining's board (a sliding door's opening, a passage)


def _detailed_leaf(cx: float, lw: float, lh: float, t: float, detail: Optional[dict], y: float = 0.0) -> list[Part]:
    """A solid leaf ``lw`` x ``lh`` centred on ``cx`` with the face detail of ``looks.door_product`` (pure; role
    ``leaf``, key ``leaf``): ``plain`` / None one box; ``horizontal`` / ``vertical`` ``count`` grooves and ``lined``
    one routed line round the face, as a core ``LEAF_GROOVE_D_M`` thinner per face and face boards with
    ``LEAF_GROOVE_W_M`` gaps between them (real recessed grooves: they catch the light); ``panelled`` the shaker stiles
    and rails proud of both faces."""
    kind = str((detail or {}).get("kind") or "plain")
    if kind == "panelled":
        f = min(DOOR_PANEL_FRAME_M, lw * 0.2)
        parts = [_leaf_box(cx, 0.0, lw, lh, t, y)]
        for s in (-1, 1):
            yy = y + s * (t / 2.0 + DOOR_PANEL_PROUD_M / 2.0)
            parts += [_box(cx - (lw / 2.0 - f / 2.0), yy, 0.0, f, DOOR_PANEL_PROUD_M, lh, "leaf", "panel"),
                      _box(cx + lw / 2.0 - f / 2.0, yy, 0.0, f, DOOR_PANEL_PROUD_M, lh, "leaf", "panel"),
                      _box(cx, yy, 0.0, lw - 2 * f, DOOR_PANEL_PROUD_M, f * 1.5, "leaf", "panel"),
                      _box(cx, yy, lh * 0.5 - f / 2.0, lw - 2 * f, DOOR_PANEL_PROUD_M, f, "leaf", "panel"),
                      _box(cx, yy, lh - f, lw - 2 * f, DOOR_PANEL_PROUD_M, f, "leaf", "panel")]
        return parts
    g, d = LEAF_GROOVE_W_M, LEAF_GROOVE_D_M
    x0, x1 = cx - lw / 2.0, cx + lw / 2.0
    boards: list[tuple[float, float, float, float]] = []          # (x0, x1, z0, z1) of the face boards
    if kind == "fine_vertical":
        # 29 Oct 2026 (R28, D2): a wood-veneer flush leaf with fine vertical grooves every FINE_GROOVE_PITCH_M
        kind, g = "vertical", FINE_GROOVE_W_M
        detail = dict(detail or {}, count=max(4, int(lw / FINE_GROOVE_PITCH_M) - 1))
    if kind in ("horizontal", "vertical"):
        n = max(1, int((detail or {}).get("count") or 1))
        if kind == "horizontal":
            cuts = [lh * k / (n + 1) for k in range(1, n + 1)]
            edges = [0.0] + [c for z in cuts for c in (z - g / 2.0, z + g / 2.0)] + [lh]
            boards = [(x0, x1, edges[i], edges[i + 1]) for i in range(0, len(edges), 2)]
        else:
            cuts = [x0 + lw * k / (n + 1) for k in range(1, n + 1)]
            edges = [x0] + [c for x in cuts for c in (x - g / 2.0, x + g / 2.0)] + [x1]
            boards = [(edges[i], edges[i + 1], 0.0, lh) for i in range(0, len(edges), 2)]
    elif kind == "lined":
        m = min(LEAF_LINE_INSET_M, lw * 0.15, lh * 0.15)
        a, b = m - g / 2.0, m + g / 2.0
        boards = [(x0, x0 + a, 0.0, lh), (x1 - a, x1, 0.0, lh), (x0 + a, x1 - a, 0.0, a), (x0 + a, x1 - a, lh - a, lh),
                  (x0 + b, x1 - b, b, lh - b)]
    if not boards:
        return [_leaf_box(cx, 0.0, lw, lh, t, y)]
    parts = [_box(cx, y, 0.0, lw, t - 2 * d, lh, "leaf", "leaf")]
    for s in (-1, 1):
        yy = y + s * (t / 2.0 - d / 2.0)
        parts += [_box((bx0 + bx1) / 2.0, yy, bz0, bx1 - bx0, d, bz1 - bz0, "leaf", "leaf")
                  for bx0, bx1, bz0, bz1 in boards if bx1 - bx0 > 1e-6 and bz1 - bz0 > 1e-6]
    return parts


def architrave_boxes(width: float, height: float, frame_w: float, thickness: float, faces=(-1.0, 1.0)
                     ) -> list[tuple[float, float, float, float, float, float]]:
    """``[(cx, cy, z0, w, d, h)]`` of a door's architrave on the wall faces ``faces`` (+1 / -1: the y sides) in the
    opening's frame (pure; 29 Oct 2026): two jamb pieces ``ARCHITRAVE_W_M`` wide from the floor to the head piece and
    the head piece across both, their inner edges ``ARCHITRAVE_REVEAL_M`` back from the jambs' inner faces, standing
    ``ARCHITRAVE_T_M`` proud of the wall face (they cover the joint of the frame and the plaster)."""
    inner = float(width) / 2.0 - float(frame_w) + ARCHITRAVE_REVEAL_M
    head = float(height) - float(frame_w) + ARCHITRAVE_REVEAL_M
    out = []
    for s in faces:
        sy = -1.0 if float(s) < 0 else 1.0
        cy = sy * (float(thickness) / 2.0 + ARCHITRAVE_T_M / 2.0)
        out += [(-(inner + ARCHITRAVE_W_M / 2.0), cy, 0.0, ARCHITRAVE_W_M, ARCHITRAVE_T_M, head),
                (inner + ARCHITRAVE_W_M / 2.0, cy, 0.0, ARCHITRAVE_W_M, ARCHITRAVE_T_M, head),
                (0.0, cy, head, 2.0 * (inner + ARCHITRAVE_W_M), ARCHITRAVE_T_M, ARCHITRAVE_W_M)]
    return out


def door_frame_parts(width: float, height: float, thickness: float, face_y: Optional[float], side: float,
                     faces=(-1.0, 1.0), frame_w: float = DOOR_FRAME_W, lining: bool = True) -> list[Part]:
    """The frame of a door whose leaf is not ours (pure; 29 Oct 2026, UL122: a library door model): with ``lining``
    the parametric door's jambs and head as deep as the wall (role ``frame``), its stops on the face away from the
    room it opens into against the leaf face ``face_y`` (role ``stop``; none when ``face_y`` is None) and the
    architrave on ``faces``; without it (a model with its own frame) the architrave alone, its inner edge over the
    model's jambs (``frame_w``: their measured width). Key ``frame`` throughout, in the opening's frame."""
    w, h, t = float(width), float(height), float(thickness)
    parts: list[Part] = []
    if lining:
        parts += [_box(-(w / 2.0 - frame_w / 2.0), 0.0, 0.0, frame_w, t, h, "frame", "frame"),
                  _box(w / 2.0 - frame_w / 2.0, 0.0, 0.0, frame_w, t, h, "frame", "frame"),
                  _box(0.0, 0.0, h - frame_w, w - 2 * frame_w, t, frame_w, "frame", "frame")]
        if face_y is not None:
            s = -1.0 if float(side) < 0 else 1.0
            parts += [_box(cx, cy, z0, bw, bd, bh, "frame", "stop")
                      for cx, cy, z0, bw, bd, bh in door_stop_boxes(w, h, frame_w, float(face_y), t, -s)]
    parts += [_box(cx, cy, z0, bw, bd, bh, "frame", "architrave")
              for cx, cy, z0, bw, bd, bh in architrave_boxes(w, h, frame_w, t, tuple(faces or ()))]
    return parts


FRAME_CENSUS_ROLES: tuple[str, ...] = ("frame", "architrave")


def frame_census(parts: Sequence[Part], height: float) -> dict:
    """What a door's frame parts hold (pure; 30 Oct 2026, lesson UL132, user: "Door frame needs fixing"): the jamb
    lining's jambs and heads (role ``frame``) and the architrave's on each wall face (role ``architrave``, ``faces``
    keyed ``"-1"`` / ``"1"`` by the side its centre stands on), the frame's top over the door's bottom (``top_m``) and
    the opening's ``height_m`` it was built for. A jamb is a part at least half the opening tall, a head any other
    (a mullion counts as a jamb). The model review's M29 (``door_states.frame_problems``) reads it: a frame part over
    its opening's head, a jamb without its head, a single jamb."""
    h = float(height)
    out: dict = {"height_m": round(h, 4), "top_m": None, "lining": {"jambs": 0, "heads": 0}, "faces": {}}
    for p in parts:
        if p.get("role") not in FRAME_CENSUS_ROLES or not p.get("verts"):
            continue
        ys = [float(v[1]) for v in p["verts"]]
        zs = [float(v[2]) for v in p["verts"]]
        z0, z1 = min(zs), max(zs)
        out["top_m"] = round(z1 if out["top_m"] is None else max(out["top_m"], z1), 4)
        if p["role"] == "frame":
            slot = out["lining"]
        else:
            slot = out["faces"].setdefault("1" if (min(ys) + max(ys)) / 2.0 > 0 else "-1", {"jambs": 0, "heads": 0})
        slot["jambs" if (z1 - z0) >= 0.5 * h else "heads"] += 1
    return out


def hinge_parts(edge_x: float, lh: float, t: float, side: float, y: float = 0.0) -> list[Part]:
    """Three hinge knuckles (``HINGE_SIZE_M``) at the leaf edge ``edge_x`` on the swing face (``side``: the room the
    door opens into), role ``hinge``, key ``handle`` (the handle metal; pure; 29 Oct 2026)."""
    hx, hy, hz = HINGE_SIZE_M
    s = -1.0 if float(side) < 0 else 1.0
    zs = [HINGE_Z_M[0], lh / 2.0 - hz / 2.0, lh - HINGE_Z_M[2]]
    return [_cylinder_z(edge_x, y + s * t / 2.0, z, hx / 2.0, hy / 2.0, hz, "handle", "hinge", n=12)
            for z in zs if 0.0 <= z <= lh - hz]


def _lever_pair(x: float, z: float, t: float, y: float = 0.0, rose: bool = False) -> list[Part]:
    """Lever handles on both faces of a leaf of thickness ``t`` centred on ``y``; ``rose`` (29 Oct 2026, R28): a round
    lock rose ``LOCK_ROSE_DROP_M`` under each lever."""
    out = []
    for s in (-1, 1):
        yy = y + s * (t / 2.0 + 0.03)
        out.append(_box(x, yy, z - 0.035, 0.02, 0.06, 0.07, "handle", "handle"))              # rose and neck
        out.append(_box(x - 0.06, yy + s * 0.02, z - 0.01, 0.13, 0.02, 0.02, "handle", "handle"))       # lever
        if rose:
            y0 = y + t / 2.0 if s > 0 else y - t / 2.0 - 0.008
            out.append(_cylinder_y(x, y0, z - LOCK_ROSE_DROP_M, LOCK_ROSE_R_M, LOCK_ROSE_R_M, 0.008, "handle",
                                   "lock_rose", n=16))
    return out


# 29 Oct 2026 (D1, lesson UL116; ``door_states``): a door's leaf as the house shows it: open, ajar or slid open. The
# parts that stay with the frame (``FIXED_ROLES``) stay; the others turn about the hinge edge on the swing face or slide.
FIXED_ROLES: tuple[str, ...] = ("frame", "rail", "stop", "architrave")       # = shell.FRAME_ROLES


def swing_angle(hinge: str, side: float, angle_deg: float) -> float:
    """The turn (degrees, counter-clockwise about +Z) of a leaf hinged at the jamb ``hinge`` (``start``: the opening's
    -x end, ``end``: its +x end) that opens ``angle_deg`` into the side ``side`` (+1: the frame's +y): its free edge
    moves towards ``side`` (= ``door_states.swing_leaf``)."""
    k = -1.0 if hinge == "start" else 1.0
    s = -1.0 if float(side) < 0 else 1.0
    return -k * s * float(angle_deg)


def turn_parts(parts: Sequence[Part], pivot: tuple[float, float], angle_deg: float) -> list[Part]:
    """Parts turned about the vertical axis through ``pivot`` (x, y) by ``angle_deg`` (a rotation keeps the faces'
    winding)."""
    a = math.radians(angle_deg)
    c, s = math.cos(a), math.sin(a)
    px, py = pivot
    return [dict(p, verts=[(px + c * (x - px) - s * (y - py), py + s * (x - px) + c * (y - py), z)
                           for x, y, z in p["verts"]]) for p in parts]


def mirror_parts_x(parts: Sequence[Part]) -> list[Part]:
    """Parts mirrored across x = 0 (faces reversed, so the normals still point out)."""
    return [dict(p, verts=[(-x, y, z) for x, y, z in p["verts"]], faces=[list(reversed(f)) for f in p["faces"]])
            for p in parts]


def shift_parts(parts: Sequence[Part], dx: float) -> list[Part]:
    return [dict(p, verts=[(x + dx, y, z) for x, y, z in p["verts"]]) for p in parts]


def _centre_x(p: Part) -> float:
    xs = [v[0] for v in p["verts"]]
    return (min(xs) + max(xs)) / 2.0


def pose_door_parts(parts: Sequence[Part], pose: Optional[dict], style: str, lw: float, leaf_t: float, side: float,
                    panels: Optional[dict] = None) -> tuple[list[Part], Optional[dict]]:
    """``(parts, pose record)`` of a door's parts posed as its ``leaf_state`` says (pure; ``door_states``): a swing
    leaf (flush, shaker panel, glazed, entrance) turned ``angle_deg`` about its hinge edge on the swing face (mirrored
    first when the hinge is at the ``end`` jamb: the parts are built hinged at the ``start`` jamb, the lever at the
    other), both leaves of a pair (``double``) each about its own jamb, a sliding or barn leaf moved ``slide_m`` along
    its wall face, a pocket leaf into its pocket, the moving panels of a glazed sliding door behind the fixed ones.
    A closed pose, or one the style cannot take, returns the parts as they are (record None)."""
    if not pose or pose.get("state") not in ("open", "ajar"):
        return list(parts), None
    fixed = [p for p in parts if p["role"] in FIXED_ROLES]
    moving = [p for p in parts if p["role"] not in FIXED_ROLES]
    angle = float(pose.get("angle_deg") or 0.0)
    s = -1.0 if float(side) < 0 else 1.0
    rec = {"state": pose.get("state"), "angle_deg": angle, "hinge": None, "slide_m": None, "style": style}
    if style in ("flush", "shaker_panel", "glazed", "entrance") and angle > 0:
        hinge = pose.get("hinge") if pose.get("hinge") in ("start", "end") else "start"
        if hinge == "end":
            moving = mirror_parts_x(moving)
        hx = -lw / 2.0 if hinge == "start" else lw / 2.0
        moving = turn_parts(moving, (hx, s * leaf_t / 2.0), swing_angle(hinge, s, angle))
        rec["hinge"] = hinge
    elif style in ("double",) and angle > 0:
        left = [p for p in moving if _centre_x(p) < -1e-6]
        right = [p for p in moving if _centre_x(p) >= -1e-6]
        moving = turn_parts(left, (-lw / 2.0, s * leaf_t / 2.0), swing_angle("start", s, angle)) + \
            turn_parts(right, (lw / 2.0, s * leaf_t / 2.0), swing_angle("end", s, angle))
        rec["hinge"] = "both"
    elif style in ("sliding", "barn"):
        dx = float(pose.get("slide_m") or 0.0)
        if abs(dx) < 1e-6:
            return list(parts), None
        moving = shift_parts(moving, dx)
        rec["slide_m"] = dx
    elif style == "pocket":
        dx = lw - 0.05
        moving = shift_parts(moving, dx)
        rec["slide_m"] = round(dx, 4)
    elif style == "glazed_sliding" and panels and panels.get("staggered"):
        centres, fixed_ix = list(panels["centres"]), set(panels.get("fixed") or ())
        out = []
        for p in moving:
            i = min(range(len(centres)), key=lambda j: abs(centres[j] - _centre_x(p)))
            if i in fixed_ix or not fixed_ix:
                out.append(p)
                continue
            j = min(fixed_ix, key=lambda f: abs(f - i))
            out += shift_parts([p], (centres[j] - centres[i]) * 0.92)
        moving = out
        rec["slide_m"] = "behind the fixed panels"
    else:
        return list(parts), None
    return fixed + moving, rec


def door_parts(look: dict | None, width: float, height: float, thickness: float,
               frame_w: float = DOOR_FRAME_W) -> tuple[list[Part], dict]:
    """``(parts, record)`` of a door in the opening's frame (see above) for a door look
    (``wenart.blender.looks.door_look``: ``door_style`` decided with the drawn operation first). Swing styles
    (flush, shaker panel, glazed, entrance) and double / folding doors sit in a frame as deep as the wall;
    pocket doors are a flush leaf with a recessed pull; sliding and barn doors hang on the room face of the wall
    (``look["side"]``: +1 / -1, the y side of the room; default -1) from a rail and overlap the opening. A drawn
    ``fixed`` door (``look["operation"]``) has no handles.

    Fix round after P3 (16-17 Oct 2026): every door in a frame gets jamb and head stops (``door_stop_boxes``, role
    ``stop``, key ``frame``: the frame object and its material) over the slit round the closed leaf: a swing door
    (flush, shaker panel, glazed, entrance, double, folding) on the face away from the room it opens into
    (``look["side"]``, so on ``-side``), against the leaf face (a shaker panel's proud stiles included); a pocket
    door on both faces (split jambs: the leaf slides between them). A double or folding door also gets an astragal
    over its meeting stiles (role ``astragal``, key ``leaf``: the leaf object), on the stop face.

    26 Oct 2026 (architect D5): ``look["glazed"]`` makes the leaves of a double or folding door glazed (French
    doors), ``look["leaves"]`` gives a folding door, a glazed sliding door or a sliding door that many leaves (a
    sliding door's leaves part in the middle), ``look["sidelights"]`` gives an entrance door wider than
    ``SINGLE_LEAF_MAX_M`` one ``ENTRANCE_LEAF_W_M`` leaf and glazed side lights (``entrance_sections``);
    ``glazed_sliding`` is a glazed sliding door in the frame (``sliding_panels``: stops against the outer track,
    pulls on the moving panels), ``sectional`` a sectional garage door (horizontal sections, ribs on both faces, a
    pull near the floor). Without these the styles are built as before."""
    style = door_style_of(look)
    side = -1.0 if float((look or {}).get("side") or -1.0) < 0 else 1.0
    w, h, t = float(width), float(height), float(thickness)
    parts: list[Part] = []
    surface = style in ("sliding", "barn")
    glazed = bool((look or {}).get("glazed")) or style in ("glazed", "glazed_sliding")
    asked = (look or {}).get("leaves")
    asked = int(asked) if isinstance(asked, int) and not isinstance(asked, bool) and asked > 0 else None
    leaves_asked = asked
    if not surface:
        parts += [_box(-(w / 2.0 - frame_w / 2.0), 0.0, 0.0, frame_w, t, h, "frame", "frame"),
                  _box(w / 2.0 - frame_w / 2.0, 0.0, 0.0, frame_w, t, h, "frame", "frame"),
                  _box(0.0, 0.0, h - frame_w, w - 2 * frame_w, t, frame_w, "frame", "frame")]
    # 29 Oct 2026 (UL89; ``looks.door_product``): the product door's architrave on the room faces, hinges, leaf detail
    product = look or {}
    detail = product.get("leaf_detail") if isinstance(product.get("leaf_detail"), dict) else None
    if detail is not None and detail.get("kind") == "plain":
        detail = None
    hinges = bool(product.get("hinges"))
    pivot = bool(product.get("pivot")) and style == "entrance"           # 29 Oct 2026 (D5): a pivot entrance door
    if pivot:
        hinges = False
    rose = bool(product.get("lock_rose"))                                # 29 Oct 2026 (R28): a lock rose
    lites = product.get("lites") if isinstance(product.get("lites"), (list, tuple)) else None     # D3
    frameless = product.get("frameless") if isinstance(product.get("frameless"), str) else None   # UL122
    arch_faces = tuple(product.get("architrave_faces") or (-1.0, 1.0)) if product.get("architrave") else ()
    if frameless:
        arch_faces = ()
    if surface and arch_faces:
        # 29 Oct 2026 (UL122): a sliding or barn leaf covers its own face: the architrave only on the other face
        arch_faces = tuple(f for f in arch_faces if (-1.0 if float(f) < 0 else 1.0) != side)
    if style != "sectional" and arch_faces:
        parts += [_box(cx, cy, z0, bw, bd, bh, "frame", "architrave")
                  for cx, cy, z0, bw, bd, bh in architrave_boxes(w, h, frame_w, t, arch_faces)]
    if surface and (product.get("architrave") or product.get("lining")):
        # 29 Oct 2026 (UL122): the opening behind a sliding or barn leaf gets a lined reveal (jambs and head lining)
        lt = LINING_T_M
        parts += [_box(-(w / 2.0 - lt / 2.0), 0.0, 0.0, lt, t, h, "frame", "frame"),
                  _box(w / 2.0 - lt / 2.0, 0.0, 0.0, lt, t, h, "frame", "frame"),
                  _box(0.0, 0.0, h - lt, w - 2 * lt, t, lt, "frame", "frame")]
    lw, lh = w - 2 * frame_w - 0.01, h - frame_w - 0.01
    leaf_t = ENTRANCE_LEAF_T if style == "entrance" else (SECTIONAL_LEAF_T if style == "sectional" else DOOR_LEAF_T)
    lever_z = min(LEVER_HEIGHT_M, lh - 0.1)
    panels = sliding_panels(lw, t, asked) if style == "glazed_sliding" else None
    if panels is not None:                                               # both tracks: the stops close the outer one
        leaf_t = 2.0 * panels["d"] + SLIDING_PANEL_T
    sections = entrance_sections(w, frame_w) if style == "entrance" and (look or {}).get("sidelights") \
        and lw > SINGLE_LEAF_MAX_M and not pivot else None
    if sections is not None and len(sections) == 1:
        sections = None
    extra: dict = {}
    if not surface:                                                      # the stops (fix round after P3)
        face = leaf_t / 2.0 + (DOOR_PANEL_PROUD_M if style == "shaker_panel" else 0.0)
        if sections is not None:
            # side lights: the head stop of the whole frame and the jamb stops of the leaf's own span
            (_k, x0, x1) = next(s for s in sections if s[0] == "leaf")
            boxes = door_stop_boxes(w, h, frame_w, face, t, -side)[2:] + [
                (cx + (x0 + x1) / 2.0, cy, z0, bw, bd, bh) for cx, cy, z0, bw, bd, bh in
                door_stop_boxes(x1 - x0 + 2 * frame_w, h, frame_w, face, t, -side)[:2]]
            parts += [_box(cx, cy, z0, bw, bd, bh, "frame", "stop") for cx, cy, z0, bw, bd, bh in boxes]
        else:
            for s in ((-1.0, 1.0) if style == "pocket" else (-side,)):
                parts += [_box(cx, cy, z0, bw, bd, bh, "frame", "stop")
                          for cx, cy, z0, bw, bd, bh in door_stop_boxes(w, h, frame_w, face, t, s)]
    if sections is not None:                                             # the entrance door with side lights
        for a, b in zip(sections, sections[1:]):
            parts.append(_box((a[2] + b[1]) / 2.0, 0.0, 0.0, b[1] - a[2], t, h - frame_w, "frame", "frame"))
        (_k, x0, x1) = next(s for s in sections if s[0] == "leaf")
        ecx, elw = (x0 + x1) / 2.0, (x1 - x0) - 0.01
        parts.append(_leaf_box(ecx, 0.0, elw, lh, leaf_t))
        if hinges:
            parts += hinge_parts(ecx - elw / 2.0, lh, leaf_t, side)
        for _k, a, b in (s for s in sections if s[0] == "light"):
            parts += [_box((a + b) / 2.0, 0.0, 0.0, b - a, leaf_t, SIDELIGHT_BASE_M, "leaf", "panel"),
                      _box((a + b) / 2.0, 0.0, SIDELIGHT_BASE_M, b - a, 0.008, h - frame_w - SIDELIGHT_BASE_M,
                           "glass", "glass")]
        for z in (lh * 0.3, lh * 0.5, lh * 0.7):
            for s in (-1, 1):
                parts.append(_box(ecx, s * (leaf_t / 2.0 + 0.002), z, elw - 0.16, 0.004, 0.012, "frame", "groove"))
        for s in (-1, 1):                                                # a long bar pull on both faces
            parts.append(_box(ecx + elw / 2.0 - 0.1, s * (leaf_t / 2.0 + 0.04), lever_z - 0.4, 0.025, 0.025, 0.8,
                              "handle", "handle"))
        extra["sidelights"] = sum(1 for s in sections if s[0] == "light")
    elif style in ("flush", "pocket", "entrance", "shaker_panel", "glazed"):
        if style == "glazed":
            parts += _glazed_leaf(0.0, 0.0, lw, lh, leaf_t, lites=lites)
        elif style == "flush" and detail is not None:
            parts += _detailed_leaf(0.0, lw, lh, leaf_t, detail)
        else:
            parts.append(_leaf_box(0.0, 0.0, lw, lh, leaf_t))
        if hinges and style != "pocket":                                 # on the swing face, opposite the lever
            parts += hinge_parts(-lw / 2.0, lh, leaf_t, side)
        if style == "shaker_panel":
            f = min(DOOR_PANEL_FRAME_M, lw * 0.2)
            for s in (-1, 1):
                y = s * (leaf_t / 2.0 + DOOR_PANEL_PROUD_M / 2.0)
                parts += [_box(-(lw / 2.0 - f / 2.0), y, 0.0, f, DOOR_PANEL_PROUD_M, lh, "leaf", "panel"),
                          _box(lw / 2.0 - f / 2.0, y, 0.0, f, DOOR_PANEL_PROUD_M, lh, "leaf", "panel"),
                          _box(0.0, y, 0.0, lw - 2 * f, DOOR_PANEL_PROUD_M, f * 1.5, "leaf", "panel"),
                          _box(0.0, y, lh * 0.5 - f / 2.0, lw - 2 * f, DOOR_PANEL_PROUD_M, f, "leaf", "panel"),
                          _box(0.0, y, lh - f, lw - 2 * f, DOOR_PANEL_PROUD_M, f, "leaf", "panel")]
        if style == "entrance":
            for z in (lh * 0.3, lh * 0.5, lh * 0.7):
                for s in (-1, 1):
                    parts.append(_box(0.0, s * (leaf_t / 2.0 + 0.002), z, lw - 0.16, 0.004, 0.012, "frame", "groove"))
            pull = PIVOT_PULL_M if pivot else 0.8
            for s in (-1, 1):                                            # a long bar pull on both faces
                parts.append(_box(lw / 2.0 - (0.14 if pivot else 0.1), s * (leaf_t / 2.0 + 0.04),
                                  lever_z - pull / 2.0, 0.025, 0.025, pull, "handle", "handle"))
            if pivot:
                extra["pivot"] = True
        elif style == "pocket":
            for s in (-1, 1):                                            # recessed flush pulls
                parts.append(_box(lw / 2.0 - 0.06, s * (leaf_t / 2.0 + 0.001), lever_z - 0.08, 0.03, 0.002, 0.16,
                                  "handle", "handle"))
        else:
            parts += _lever_pair(lw / 2.0 - 0.07, lever_z, leaf_t, rose=rose)
    elif style in ("double", "folding") and not glazed and (style == "double" or (asked or 2) == 2):
        half = lw / 2.0 - 0.002
        for s in (-1, 1):
            parts += _detailed_leaf(s * (half / 2.0 + 0.001), half, lh, DOOR_LEAF_T, detail)
            if hinges and style == "double":                             # each leaf hinged at its jamb
                parts += hinge_parts(s * lw / 2.0, lh, DOOR_LEAF_T, side)
        # the astragal over the meeting stiles, on the stop face (fix round after P3)
        (_cx, cy, _z0, _bw, bd, _bh) = door_stop_boxes(w, h, frame_w, DOOR_LEAF_T / 2.0, t, -side)[0]
        parts.append(_box(0.0, cy, 0.0, DOOR_ASTRAGAL_W_M, bd, lh, "leaf", "astragal"))
        if style == "double":
            for s in (-1, 1):
                parts += _lever_pair(s * 0.06, lever_z, DOOR_LEAF_T, rose=rose and s > 0)
        else:
            parts += _lever_pair(lw / 2.0 - 0.07, lever_z, DOOR_LEAF_T, rose=rose)
    elif style in ("double", "folding"):                                 # glazed leaves (French doors), n leaves
        n = 2 if style == "double" else max(2, asked or 2)
        lwi = (lw - LEAF_GAP_M - (n - 1) * LEAF_GAP_M) / n
        centres = [-lw / 2.0 + LEAF_GAP_M / 2.0 + lwi / 2.0 + i * (lwi + LEAF_GAP_M) for i in range(n)]
        for cx in centres:
            parts += _glazed_leaf(cx, 0.0, lwi, lh, DOOR_LEAF_T, groove=GLAZING_GROOVE_M, lites=lites) if glazed \
                else _detailed_leaf(cx, lwi, lh, DOOR_LEAF_T, detail)
        if hinges and style == "double":                                 # each leaf hinged at its jamb
            parts += hinge_parts(centres[0] - lwi / 2.0, lh, DOOR_LEAF_T, side)
            parts += hinge_parts(centres[-1] + lwi / 2.0, lh, DOOR_LEAF_T, side)
        (_cx, cy, _z0, _bw, bd, _bh) = door_stop_boxes(w, h, frame_w, DOOR_LEAF_T / 2.0, t, -side)[0]
        for a, b in zip(centres, centres[1:]):                           # an astragal over every meeting joint
            parts.append(_box((a + b) / 2.0, cy, 0.0, DOOR_ASTRAGAL_W_M, bd, lh, "leaf", "astragal"))
        if style == "double":
            for s in (-1, 1):
                parts += _lever_pair(s * 0.06, lever_z, DOOR_LEAF_T)
        else:
            parts += _lever_pair(lw / 2.0 - 0.07, lever_z, DOOR_LEAF_T)
        extra["leaves"] = n
    elif style == "glazed_sliding":                                      # glazed panels on two tracks in the frame
        pt, pw = SLIDING_PANEL_T, panels["width"]
        moving = []
        for i, cx in enumerate(panels["centres"]):
            y = (-side if i % 2 == 0 else side) * panels["d"]            # the outer track away from the room
            parts += _glazed_leaf(cx, y, pw, lh, pt, SLIDING_STILE_M, GLAZING_GROOVE_M, lites=lites)
            if i not in panels["fixed"]:
                moving.append((cx, y))
        if not panels["staggered"]:                                      # side by side: astragals over the joints
            (_cx, cy, _z0, _bw, bd, _bh) = door_stop_boxes(w, h, frame_w, pt / 2.0, t, -side)[0]
            for a, b in zip(panels["centres"], panels["centres"][1:]):
                parts.append(_box((a + b) / 2.0, cy, 0.0, DOOR_ASTRAGAL_W_M, bd, lh, "leaf", "astragal"))
        f = min(SLIDING_STILE_M, pw * 0.2)
        for cx, y in moving:                                             # a pull on the stile at the jamb's end
            hx = cx + (1.0 if cx >= 0.0 else -1.0) * (pw / 2.0 - f / 2.0)
            parts.append(_box(hx, y + side * (pt / 2.0 + 0.015), lever_z - 0.2, 0.02, 0.02, 0.4, "handle", "handle"))
            parts.append(_box(hx, y - side * (pt / 2.0 + 0.001), lever_z - 0.1, 0.03, 0.002, 0.2, "handle", "handle"))
        extra.update(leaves=panels["n"], fixed_panels=panels["fixed"], tracks=2 if panels["staggered"] else 1)
    elif style == "sectional":                                           # a sectional garage door
        n = max(3, int(round(lh / SECTION_H_M)))
        sh = lh / n
        parts += [_box(0.0, 0.0, i * sh, lw, leaf_t, sh, "leaf", "leaf") for i in range(n)]
        for k in range(1, 2 * n):                                        # ribs at the joints and mid-section
            for s in (-1, 1):
                parts.append(_box(0.0, s * (leaf_t / 2.0 + 0.0015), k * sh / 2.0 - 0.006, lw - 0.04, 0.003, 0.012,
                                  "leaf", "rib"))
        for s in (-1, 1):                                                # a pull bar near the floor, both faces
            parts.append(_box(0.0, s * (leaf_t / 2.0 + 0.02), 0.32, 0.3, 0.02, 0.03, "handle", "handle"))
        extra["sections"] = n
    else:                                                                # sliding / barn: on the room face
        sw = w + 2 * SLIDING_OVERLAP_M
        sh = h + 0.02
        y = side * (t / 2.0 + SLIDING_STANDOFF_M + DOOR_LEAF_T / 2.0)
        pair = asked if style == "sliding" and asked and asked > 1 else None
        if style == "barn":
            n = max(3, int(sw / 0.16))
            pw = sw / n
            for i in range(n):
                parts.append(_box(-sw / 2.0 + pw * (i + 0.5), y, 0.0, pw - 0.004, DOOR_LEAF_T, sh, "leaf", "leaf"))
            for z in (0.15, sh - 0.3):                                   # the ledges
                parts.append(_box(0.0, y + side * (DOOR_LEAF_T / 2.0 + 0.01), z, sw - 0.04, 0.02, 0.15, "leaf",
                                  "ledge"))
        elif pair is None:
            parts.append(_box(0.0, y, 0.0, sw, DOOR_LEAF_T, sh, "leaf", "leaf"))
        if pair is not None:                                             # leaves parting in the middle
            n = pair
            pw = (sw - (n - 1) * 0.004) / n
            centres = [-sw / 2.0 + pw / 2.0 + i * (pw + 0.004) for i in range(n)]
            parts += [_box(cx, y, 0.0, pw, DOOR_LEAF_T, sh, "leaf", "leaf") for cx in centres]
            parts.append(_box(0.0, side * (t / 2.0 + 0.02), sh + 0.02, 2.0 * sw, 0.02, RAIL_H, "rail", "rail"))
            for cx in centres:                                           # a pull at each leaf's meeting edge
                hx = cx - (1.0 if cx > 1e-9 else -1.0) * (pw / 2.0 - 0.08)
                parts.append(_box(hx, y + side * (DOOR_LEAF_T / 2.0 + 0.01), lever_z - 0.15, 0.03, 0.02, 0.3,
                                  "handle", "handle"))
            extra["leaves"] = n
        else:
            rail_y = side * (t / 2.0 + 0.02)
            parts.append(_box(w / 2.0 - 0.05, rail_y, sh + 0.02, 2.0 * sw, 0.02, RAIL_H, "rail", "rail"))
            parts.append(_box(-sw / 2.0 + 0.08, y + side * (DOOR_LEAF_T / 2.0 + 0.01), lever_z - 0.15, 0.03, 0.02,
                              0.3, "handle", "handle"))
    fixed = (look or {}).get("operation") == "fixed"
    if fixed:                                                            # a drawn fixed leaf: nothing to open it
        parts = [p for p in parts if p["key"] != "handle"]
    record = {"door_style": style, "leaf_thickness": leaf_t, "frame_width": None if surface else frame_w,
              "surface_mounted": surface, "side": side if surface else None, "handles": not fixed,
              "parts": sorted({p["role"] for p in parts}),
              # fix round after P3: the y face of the stops (both for a pocket door's split jambs), None without
              "stop_side": None if surface else ("both" if style == "pocket" else -side)}
    if style != "glazed" and any(p["role"] == "glass" for p in parts):
        extra["glazed"] = True                                          # D5: a glazed pair, sliding door, side lights
    if product.get("architrave") or hinges or product.get("leaf_detail"):
        # 29 Oct 2026 (UL89): what makes the parametric door a product (model review M20 reads it)
        solid = style in ("flush", "double", "folding") and not glazed
        asked = product.get("leaf_detail") if isinstance(product.get("leaf_detail"), dict) else {}
        extra.update(leaf_detail=asked.get("kind") if solid else None,           # "plain" when the style names it
                     architrave=sorted({-1 if float(s) < 0 else 1 for s in arch_faces})
                     if not surface and style != "sectional" else [],
                     hinges=sum(1 for p in parts if p["role"] == "hinge"))
    if rose:
        extra["lock_rose"] = any(p["role"] == "lock_rose" for p in parts)
    if lites:
        extra["lites"] = [int(v) for v in lites][:2]
    # 29 Oct 2026 (UL122): what frames the door (the model review's M20 and Argus' U33 read it)
    faces = sorted({-1 if float(s) < 0 else 1 for s in arch_faces})
    indoor = sorted({-1 if float(s) < 0 else 1 for s in (product.get("architrave_faces") or ())}) \
        if product.get("architrave") else []
    why = None
    if frameless:
        why = frameless
    elif style == "sectional":
        why = "a sectional garage door: a lined opening, no architrave"
    elif surface and set(indoor) - set(faces):
        why = "a sliding leaf covers its own face: the architrave on the other face"
    if product.get("architrave") or frameless:
        record["frame"] = {"lining": not surface or bool(product.get("architrave") or product.get("lining")),
                           "head": not surface or bool(product.get("architrave") or product.get("lining")),
                           "architrave": faces, "indoor_faces": indoor, "source": "parametric",
                           "frameless": frameless, "architrave_why": why}
    # 29 Oct 2026 (D1, UL116): the leaf as the house shows it (``door_states``: open, ajar or slid open)
    pose = (look or {}).get("leaf_state") if isinstance((look or {}).get("leaf_state"), dict) else None
    if pose is not None and style == "sliding" and leaves_asked and leaves_asked > 1:
        pose = dict(pose, pair=True)
    if pose is not None and pose.get("pair") and style == "sliding" and pose.get("state") == "open":
        left = [p for p in parts if p["role"] not in FIXED_ROLES and _centre_x(p) < 0.0]
        right = [p for p in parts if p["role"] not in FIXED_ROLES and _centre_x(p) >= 0.0]
        parts = [p for p in parts if p["role"] in FIXED_ROLES] + shift_parts(left, -w / 2.0) + \
            shift_parts(right, w / 2.0)
        record["pose"] = {"state": "open", "angle_deg": 0.0, "hinge": None, "slide_m": round(w / 2.0, 4),
                          "style": style, "pair": True}
    else:
        parts, posed = pose_door_parts(parts, pose, style, lw, leaf_t, side, panels)
        if posed is not None:
            record["pose"] = posed
    record.update(extra)
    return parts, record


def window_profile(material: str | None) -> tuple[float, float]:
    """``(frame width, frame depth)`` of a window frame material (``WINDOW_PROFILES``, assumed typical sizes)."""
    return WINDOW_PROFILES.get(str(material or ""), DEFAULT_WINDOW_PROFILE)


def window_parts(look: dict | None, width: float, height: float, wall_thickness: float, mullions: int = 0,
                 transoms: int = 0, inside: int = -1) -> tuple[list[Part], dict]:
    """``(parts, record)`` of a window in the opening's frame: the frame (the material's profile), ``mullions``
    vertical and ``transoms`` horizontal bars when the building gives them (none otherwise), the glass pane(s)
    and an inside sill on the room side (``inside``: -1 / +1, the y side of the room; the outside sill is the
    shell's), lying on the reveal from the frame to past the wall face. Profiles: ``window_profile``."""
    fw, depth = window_profile((look or {}).get("material"))
    w, h = float(width), float(height)
    depth = min(depth, float(wall_thickness))
    parts = [_box(-(w / 2.0 - fw / 2.0), 0.0, 0.0, fw, depth, h, "frame", "frame"),
             _box(w / 2.0 - fw / 2.0, 0.0, 0.0, fw, depth, h, "frame", "frame"),
             _box(0.0, 0.0, h - fw, w - 2 * fw, depth, fw, "frame", "frame"),
             _box(0.0, 0.0, 0.0, w - 2 * fw, depth, fw, "frame", "frame")]
    m, tr = max(0, int(mullions or 0)), max(0, int(transoms or 0))
    for i in range(1, m + 1):
        x = -w / 2.0 + fw + (w - 2 * fw) * i / (m + 1)
        parts.append(_box(x, 0.0, fw, MULLION_W, depth * 0.9, h - 2 * fw, "frame", "mullion"))
    for j in range(1, tr + 1):
        z = fw + (h - 2 * fw) * j / (tr + 1)
        parts.append(_box(0.0, 0.0, z - MULLION_W / 2.0, w - 2 * fw, depth * 0.9, MULLION_W, "frame", "transom"))
    parts.append(_box(0.0, 0.0, fw, w - 2 * fw, 0.006, h - 2 * fw, "glass", "glass"))
    s = -1.0 if inside < 0 else 1.0
    t = float(wall_thickness)
    proud = INSIDE_SILL["depth_proud"]
    sill_d = t / 2.0 - depth / 2.0 + proud
    parts.append(_box(0.0, s * (depth / 2.0 + sill_d / 2.0), 0.0, w + 2 * INSIDE_SILL["ears"],     # on the reveal
                      sill_d, INSIDE_SILL["thickness"], "sill", "sill"))
    record = {"material": (look or {}).get("material"), "frame_width": fw, "frame_depth": depth, "mullions": m,
              "transoms": tr, "inside_sill": {"depth": round(sill_d, 4), "proud": proud,
                                              "thickness": INSIDE_SILL["thickness"]},
              "profile_assumed": True}
    return parts, record


# --------------------------------------------------------------------------
# Milestone 10 decor (docs/milestone10.md §4.6): parametric fallbacks of the 12 new types
# --------------------------------------------------------------------------
#
# Item frame as every decor item: width X, depth Y, front = local -Y (curtains, blinds and clocks face the room
# with it; their back is +Y, on the wall side), origin at the box centre on its rest height. Keys starting with
# ``colour_`` take the item's colour name (``decor.colour``: the brief's or the AI's) as the base colour of their
# material (``furniture._Materials``); ``pot`` takes the plant's pot material and colour; ``bulb`` emits when the
# item's ``light_on`` is true (the interior evening mood).

COLOUR_PREFIX = "colour_"
CURTAIN_PANEL_SHARE = 0.22       # each curtain panel covers this share of the rod width (open curtains)
CURTAIN_PLEATS = 5
BLIND_DOWN_SHARE = 0.35          # a roller blind is drawn down this share of its window (decor_ai sizes its box)
PLANT_SPECIES: tuple[str, ...] = ("palm", "monstera", "fiddle_leaf_fig", "olive", "fern", "other")
PLANT_POT_SHARE = 0.55           # pot diameter / the smaller side of the item box
LIGHT_TYPES: tuple[str, ...] = ("pendant_light", "ceiling_light", "table_lamp")


def _cylinder_x(x0: float, cy: float, cz: float, ry: float, rz: float, length: float, key: str, role: str = "body",
                n: int = 16) -> Part:
    """Elliptic cylinder along +X from ``x0`` to ``x0 + length`` (a turned Z cylinder: (x, y, z) -> (z, y, -x),
    a proper rotation, so the faces stay wound outwards)."""
    part = _cylinder_z(0.0, 0.0, 0.0, rz, ry, length, key, role, n)
    part["verts"] = [(x0 + z, cy + y, cz - x) for x, y, z in part["verts"]]
    return part


def _leaf(bx: float, by: float, bz: float, length: float, width: float, thick: float, yaw_deg: float,
          pitch_deg: float, key: str = "green", role: str = "leaf") -> Part:
    """A flat leaf (a superellipsoid ``width x length x thick``) from the point ``(bx, by, bz)`` outwards along the
    direction ``yaw_deg`` (counter-clockwise from +Y), raised by ``pitch_deg`` (negative: drooping)."""
    part = _superellipsoid(0.0, length / 2.0, -thick / 2.0, width, length, thick, 0.5, 0.6, key, role, n_eta=6, n_om=12)
    p, yw = math.radians(pitch_deg), math.radians(yaw_deg)
    cp, sp, cy, sy = math.cos(p), math.sin(p), math.cos(yw), math.sin(yw)
    verts = []
    for x, y, z in part["verts"]:
        y1, z1 = y * cp - z * sp, y * sp + z * cp
        verts.append((bx + x * cy - y1 * sy, by + x * sy + y1 * cy, bz + z1))
    part["verts"] = verts
    part["smooth"] = True
    return part


def _leaf_length(reach: float, pitch_deg: float, room_above: float) -> float:
    """The longest leaf that stays within ``reach`` sideways and ``room_above`` upwards at ``pitch_deg``."""
    p = math.radians(pitch_deg)
    out = reach / max(math.cos(p), 0.2)
    if p > 0:
        out = min(out, room_above / max(math.sin(p), 1e-3))
    return max(0.05, out)


def _pot(w: float, d: float, h: float) -> tuple[list[Part], float, float]:
    """``(parts, pot top, crown radius)``: a tapered pot (key ``pot``) with soil."""
    r = min(w, d) / 2.0
    pr = r * PLANT_POT_SHARE
    pot_h = min(0.45, max(0.2, h * 0.22))
    parts = [_frustum_z(0.0, 0.0, 0.0, pr * 0.78, pr * 0.78, pr, pr, pot_h, "pot", "pot"),
             _cylinder_z(0.0, 0.0, pot_h - 0.015, pr * 0.92, pr * 0.92, 0.012, "dark", "soil", n=24)]
    return parts, pot_h, r


def _plant_large(w: float, d: float, h: float, species: str | None = None) -> list[Part]:
    """A large floor plant (``plant_large``) of its species (docs/milestone10.md §4.6: palm, monstera,
    fiddle-leaf fig, olive, fern; anything else a plain crown) in a pot, inside its ``w x d x h`` box."""
    parts, top, r = _pot(w, d, h)
    reach = r - 0.01
    crown_h = h - top
    sp = species if species in PLANT_SPECIES else "other"
    if sp == "palm":
        for k, (dx, dy, f) in enumerate(((0.03, 0.0, 0.75), (-0.025, 0.02, 0.9), (0.0, -0.03, 1.0))):
            stem_top = top + crown_h * 0.55 * f
            parts.append(_cylinder_z(dx, dy, top - 0.01, 0.012, 0.012, stem_top - top + 0.01, "wood", "stem", n=8))
            for j in range(6):
                pitch = 35.0 if j % 2 == 0 else -5.0
                length = _leaf_length(reach - math.hypot(dx, dy), pitch, h - stem_top - 0.02)
                parts.append(_leaf(dx, dy, stem_top, length, length * 0.16, 0.01, 60.0 * j + 20.0 * k, pitch))
    elif sp == "monstera":
        for j in range(7):
            base = top + crown_h * (0.15 + 0.07 * j)
            yaw = 51.4 * j
            off = (-0.04 * math.sin(math.radians(yaw)), 0.04 * math.cos(math.radians(yaw)))
            parts.append(_cylinder_z(off[0] * 0.5, off[1] * 0.5, top - 0.01, 0.008, 0.008, base - top + 0.01, "green",
                                     "stem", n=6))
            length = min(_leaf_length(reach - 0.04, 20.0, h - base - 0.02), 0.5)
            parts.append(_leaf(off[0], off[1], base, length, length * 0.8, 0.012, yaw, 20.0))
    elif sp == "fiddle_leaf_fig":
        trunk_top = top + crown_h * 0.95
        parts.append(_cylinder_z(0.0, 0.0, top - 0.01, 0.018, 0.018, trunk_top - top, "wood", "trunk", n=10))
        n = 14
        for j in range(n):
            base = top + crown_h * (0.4 + 0.5 * j / n)
            length = min(_leaf_length(reach - 0.02, 35.0, h - base - 0.02), 0.28)
            parts.append(_leaf(0.0, 0.0, base, length, length * 0.6, 0.01, 137.5 * j, 35.0))
    elif sp == "olive":
        trunk_top = top + crown_h * 0.45
        parts.append(_cylinder_z(0.0, 0.0, top - 0.01, 0.025, 0.025, trunk_top - top + 0.05, "wood", "trunk", n=10))
        blob = min(reach * 1.1, crown_h * 0.45)
        blobs = ((0.0, 0.0, 0.25), (reach * 0.35, 0.0, 0.0), (-reach * 0.3, reach * 0.2, 0.1))
        for dx, dy, dz in blobs:
            bw = min(blob, 2 * (reach - abs(dx)), 2 * (reach - abs(dy)))
            z0 = min(trunk_top + dz * crown_h * 0.3, h - bw * 0.8)
            parts.append(_superellipsoid(dx, dy, z0, bw, bw, bw * 0.8, 0.9, 0.9, "green", "crown", n_eta=8, n_om=16))
    elif sp == "fern":
        for j in range(12):
            pitch = 25.0 if j % 2 == 0 else -12.0
            length = _leaf_length(reach, pitch, h - top - 0.02)
            parts.append(_leaf(0.0, 0.0, top + 0.02, length, length * 0.3, 0.01, 30.0 * j, pitch))
    else:
        parts += [_cylinder_z(0.0, 0.0, top, 0.015, 0.015, crown_h * 0.4, "wood", "stem", n=8),
                  _cylinder_z(0.0, 0.0, top + crown_h * 0.35, reach, reach, crown_h * 0.65, "green", "crown", n=16)]
    return parts


def _new_decor_parts(dtype: str, w: float, d: float, h: float, item: dict | None = None) -> list[Part]:
    """The parametric fallback of a Milestone 10 decor type (``decor_parts``)."""
    r = min(w, d) / 2.0
    # Milestone 12 (§6.4): our procedural textiles (the mesh makers at the end of this module)
    if dtype == "curtain":                    # an open pair of pleated panels under a rod (one per window)
        return curtain_parts(w, d, h, item=item)
    if dtype == "blind":                      # a roller blind (default) or a slatted blind (item ``blind_kind``)
        return blind_parts(w, d, h, kind=str((item or {}).get("blind_kind") or "roller"))
    if dtype == "throw":                      # without a host: a flat cloth with its folds (on a host: textiles.drape)
        return [flat_cloth(w, d, min(h, CLOTH_THICKNESS_M * 2.0))]
    if dtype == "books":                      # a stack of three books lying flat
        keys = ("dark", "painted", "terracotta")
        parts, z = [], 0.0
        bh = h / 3.0
        for i in range(3):
            s = 1.0 - 0.08 * i
            parts.append(_box(0.01 * (i % 2), 0.0, z, w * s, d * s, bh - 0.002, keys[i], "book"))
            z += bh
        return parts
    if dtype == "candle":                     # three pillar candles on a plate, a flame each (lit at evening)
        rr = r * 0.32
        plate = 0.012
        parts = [_cylinder_z(0.0, 0.0, 0.0, w / 2.0, d / 2.0, plate, "colour_ceramic", "plate", n=24)]
        for (dx, dy), f in zip(((-w * 0.22, -d * 0.12), (w * 0.2, -d * 0.1), (0.0, d * 0.22)), (1.0, 0.75, 0.55)):
            ch = (h - plate - 0.03) * f
            parts.append(_cylinder_z(dx, dy, plate, rr, rr, ch, "ceramic", "candle", n=16))
            parts.append(_superellipsoid(dx, dy, plate + ch + 0.004, 0.01, 0.01, 0.022, 0.8, 1.0, "bulb", "flame",
                                         n_eta=6, n_om=8))
        return parts
    if dtype == "basket":                     # a woven basket, its open top shown dark
        return [_frustum_z(0.0, 0.0, 0.0, w / 2.0 * 0.85, d / 2.0 * 0.85, w / 2.0, d / 2.0, h * 0.98, "rattan", "body"),
                _cylinder_z(0.0, 0.0, h * 0.98, w / 2.0 * 0.9, d / 2.0 * 0.9, h * 0.02, "dark", "inside", n=24)]
    if dtype == "plate":                      # 28 Oct 2026: a dinner plate: a foot ring and a shallow dish
        foot = 0.004
        return [_cylinder_z(0.0, 0.0, 0.0, w * 0.3, d * 0.3, foot, "ceramic", "foot", n=24),
                _frustum_z(0.0, 0.0, foot, w * 0.34, d * 0.34, w / 2.0, d / 2.0, max(0.006, h - foot), "ceramic",
                           "plate", n=32)]
    if dtype == "glass":                      # 28 Oct 2026: a water glass, a little wider at the rim
        return [_frustum_z(0.0, 0.0, 0.0, w * 0.42, d * 0.42, w / 2.0, d / 2.0, h, "glass", "glass", n=24)]
    if dtype == "tray":                       # a flat tray with low rims
        t, rim = 0.008, min(0.012, w * 0.05, d * 0.05)
        return [_box(0.0, 0.0, 0.0, w, d, t, "colour_wood", "base"),
                _box(0.0, -d / 2.0 + rim / 2.0, t, w, rim, h - t, "colour_wood", "rim"),
                _box(0.0, d / 2.0 - rim / 2.0, t, w, rim, h - t, "colour_wood", "rim"),
                _box(-w / 2.0 + rim / 2.0, 0.0, t, rim, d - 2 * rim, h - t, "colour_wood", "rim"),
                _box(w / 2.0 - rim / 2.0, 0.0, t, rim, d - 2 * rim, h - t, "colour_wood", "rim")]
    if dtype == "clock":                      # a wall clock facing -Y: rim, face, hands
        cr = min(w, h) / 2.0
        hands = min(0.006, d / 4.0)
        face = min(0.01, d / 4.0)
        y0 = -d / 2.0 + hands                       # the face sits behind the hands
        parts = [_cylinder_y(0.0, y0 + face, cr, cr, cr, d - hands - face, "colour_steel", "rim", n=40),
                 _cylinder_y(0.0, y0, cr, cr * 0.9, cr * 0.9, face, "ceramic", "face", n=40)]
        parts.append(_box(0.0, -d / 2.0 + hands * 0.75, cr - 0.005, cr * 0.55, hands / 2.0, 0.01, "dark", "hand"))
        parts.append(_box(0.0, -d / 2.0 + hands * 0.25, cr, 0.008, hands / 2.0, cr * 0.75, "dark", "hand"))
        return parts
    if dtype == "sculpture":                  # an abstract piece: stacked smooth forms on a plinth
        base_h = min(0.05, h * 0.12)
        parts = [_box(0.0, 0.0, 0.0, w * 0.8, d * 0.8, base_h, "dark", "base")]
        z, s = base_h, 1.0
        for i in range(3):
            bh = (h - base_h) * (0.45 if i == 0 else 0.3 if i == 1 else 0.25)
            parts.append(_superellipsoid(0.0, 0.0, z, w * 0.7 * s, d * 0.7 * s, bh, 0.8, 0.9, "colour_ceramic", "form",
                                         n_eta=8, n_om=20))
            z += bh
            s *= 0.75
        return parts
    if dtype == "plant_large":
        return _plant_large(w, d, h, (item or {}).get("species"))
    if dtype == "pendant_light":              # a ceiling canopy, a cord and a cone shade with its bulb
        shade_h = min(0.3, h * 0.6)
        canopy = min(0.06, r)
        parts = [_cylinder_z(0.0, 0.0, h - 0.025, canopy, canopy, 0.025, "colour_steel", "canopy", n=16),
                 _cylinder_z(0.0, 0.0, shade_h, 0.004, 0.004, h - 0.025 - shade_h, "dark", "cord", n=6),
                 _frustum_z(0.0, 0.0, 0.0, w / 2.0, d / 2.0, w * 0.12, d * 0.12, shade_h, "colour_steel", "shade")]
        bulb = min(0.06, r * 0.4)
        parts.append(_superellipsoid(0.0, 0.0, 0.01, bulb, bulb, bulb, 1.0, 1.0, "bulb", "bulb", n_eta=6, n_om=12))
        return parts
    if dtype == "ceiling_light" and (item or {}).get("fixture") == "downlight":
        return downlight_parts(w, d, h)       # 29 Oct 2026 (UL106): a small recessed downlight
    if dtype == "ceiling_light":              # a flush canopy with a dome diffuser
        canopy = min(0.03, h * 0.3)
        return [_cylinder_z(0.0, 0.0, h - canopy, w / 2.0 * 0.8, d / 2.0 * 0.8, canopy, "colour_steel", "canopy",
                            n=32),
                _superellipsoid(0.0, 0.0, 0.0, w, d, h - canopy + 0.004, 0.6, 1.0, "bulb", "bulb", n_eta=8, n_om=32)]
    if dtype in KITCHEN_DECOR_TYPES:          # 28 Oct 2026: the kitchen worktop's appliances and decor
        return kitchen_worktop_parts(dtype, w, d, h)
    if dtype in WORK_DECOR_TYPES:             # 29 Oct 2026: the desk's laptop, monitor, keyboard and mouse
        return work_set_parts(dtype, w, d, h)
    raise KeyError(f"no decor builder for {dtype!r}")


# 29 Oct 2026 (UL106; the professional reference: small recessed downlights in the ceiling): a recessed downlight is a
# thin trim ring flush under the ceiling and a lens set a little up into it (real product: 8-9 cm cut-out, a 1 cm
# trim). Designer values; the light itself is the rig's (lighting.rig_plan hosts it under every decor ceiling light).
DOWNLIGHT_SIZE = (0.09, 0.09, 0.012)
DOWNLIGHT_LENS_SHARE = 0.62


def downlight_parts(w: float, d: float, h: float) -> list[Part]:
    """A recessed downlight in its box ``w x d x h`` (bottom on z = 0, the ceiling at h): the trim ring (``painted``)
    and the lens (``bulb``: it emits when the evening mood lights the lamps)."""
    r = min(w, d) / 2.0
    ring = min(h, 0.012)
    return [_cylinder_z(0.0, 0.0, h - ring, r, r, ring, "painted", "trim", n=32),
            _cylinder_z(0.0, 0.0, h - ring - 0.002, r * DOWNLIGHT_LENS_SHARE, r * DOWNLIGHT_LENS_SHARE, 0.004,
                        "bulb", "bulb", n=24)]


def kitchen_worktop_parts(dtype: str, w: float, d: float, h: float) -> list[Part]:
    """28 Oct 2026 (user: "More decor pieces needed ... kettle in the kitchen, microwave in the kitchen etc"): the
    parametric small appliances and decor of a kitchen worktop at the item's real box (bottom on z = 0, front -Y),
    with PBR material keys (steel, dark glass, ceramic, wood, the fruit's colours): a countertop microwave (steel
    case, dark glass door with its window, a control strip and a handle), a kettle (body, lid, spout and handle on
    its base), a bean-to-cup coffee machine (body, drip tray, spout, cup), a 2-slice toaster (body with two slots and
    a lever), a wooden chopping board, a ceramic utensil pot with its wooden tools, a fruit bowl with fruit."""
    if dtype in STYLING_DECOR_TYPES:                 # 29 Oct 2026 (UL115, UL118): a styling set, one mesh
        from wenart.blender import kitchen_details as KD
        return KD.styling_parts(dtype, w, d, h)
    r = min(w, d) / 2.0
    if dtype == "microwave":
        door, f = w * 0.68, -d / 2.0                 # every part inside the item's box: the case's front 3 cm back
        return [_box(0.0, 0.015, 0.0, w, d - 0.03, h, "steel", "body"),
                _box(-w / 2.0 + door / 2.0 + 0.01, f + 0.027, 0.02, door, 0.006, h - 0.04, "dark", "door"),
                _box(-w / 2.0 + door / 2.0 + 0.01, f + 0.023, 0.05, door * 0.7, 0.002, max(0.01, h - 0.10), "glass",
                     "window"),
                _box(w / 2.0 - (w - door) / 2.0 + 0.005, f + 0.028, 0.03, w - door - 0.03, 0.004, h - 0.06, "dark",
                     "controls"),
                _box(door - w / 2.0 - 0.01, f + 0.012, 0.06, 0.015, 0.024, max(0.01, h - 0.12), "steel", "handle")]
    if dtype == "kettle":
        base_h = 0.02
        body_r = r * 0.72
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.85, r * 0.85, base_h, "dark", "base", n=24),
                _frustum_z(0.0, 0.0, base_h, body_r, body_r, body_r * 0.8, body_r * 0.8, h * 0.78, "steel", "body",
                           n=24),
                _cylinder_z(0.0, 0.0, base_h + h * 0.78, body_r * 0.55, body_r * 0.55, h * 0.06, "dark", "lid", n=20),
                _box(-body_r - 0.015, 0.0, base_h + h * 0.5, 0.04, 0.025, 0.03, "steel", "spout"),   # along its width
                _box(body_r + 0.0125, 0.0, base_h + h * 0.15, 0.025, 0.022, h * 0.6, "dark", "handle")]
    if dtype == "coffee_machine":
        return [_box(0.0, 0.03, 0.0, w, d - 0.06, h, "dark", "body"),
                _box(0.0, -d / 2.0 + 0.04, 0.0, w * 0.8, 0.08, 0.02, "steel", "tray"),
                _box(0.0, -d / 2.0 + 0.05, h * 0.55, w * 0.7, 0.10, h * 0.12, "steel", "head"),
                _cylinder_z(0.0, -d / 2.0 + 0.05, 0.02, 0.035, 0.035, 0.075, "ceramic", "cup", n=16),
                _box(0.0, 0.03 - (d - 0.06) / 2.0 - 0.002, h * 0.78, w * 0.6, 0.004, h * 0.12, "glass", "display")]
    if dtype == "toaster":
        parts = [_box(0.0, 0.015, 0.0, w, d - 0.03, h - 0.006, "steel", "body"),
                 _box(0.0, -d / 2.0 + 0.0145, h * 0.55, 0.02, 0.025, 0.02, "dark", "lever")]
        for sy in (-1.0, 1.0):
            parts.append(_box(0.0, 0.015 + sy * d * 0.18, h - 0.006, w * 0.6, 0.03, 0.006, "dark", "slot"))
        return parts
    if dtype == "chopping_board":
        return [_box(0.0, 0.0, 0.0, w, d, h, "wood", "board"),
                _cylinder_z(w / 2.0 - 0.03, 0.0, h - 0.0008, 0.01, 0.01, 0.0008, "dark", "hole", n=12)]
    if dtype == "utensil_pot":
        pot_h = min(h * 0.55, 0.17)
        parts = [_cylinder_z(0.0, 0.0, 0.0, r * 0.9, r * 0.9, pot_h, "ceramic", "pot", n=24)]
        for k, (ox, oy) in enumerate(((-0.02, 0.0), (0.015, 0.015), (0.01, -0.02), (-0.01, 0.02))):
            parts.append(_box(ox, oy, pot_h * 0.3, 0.012, 0.012, h - pot_h * 0.3 - 0.005 * k, "wood", "tool"))
        return parts
    if dtype == "fruit_bowl":
        parts = [_cylinder_z(0.0, 0.0, 0.0, r * 0.5, r * 0.5, h * 0.25, "ceramic", "base", n=24),
                 _frustum_z(0.0, 0.0, h * 0.25, r * 0.6, r * 0.6, r, r, h * 0.45, "ceramic", "body", n=24)]
        fr = min(r * 0.32, h * 0.32)
        for k, (ox, oy) in enumerate(((-0.35, -0.2), (0.3, -0.15), (0.0, 0.3), (0.05, -0.05))):
            parts.append(_superellipsoid(ox * r, oy * r, h * 0.35, fr * 2.0, fr * 2.0, fr * 2.0, 1.0, 1.0,
                                         ("terracotta", "green")[k % 2], "fruit", n_eta=6, n_om=12))
        return parts
    raise KeyError(f"no kitchen worktop builder for {dtype!r}")


# 29 Oct 2026 (lesson UL93): the desk's work set. Real products: a 14-15 inch laptop's base is 0.32-0.36 x 0.22-0.24 m
# and 15-18 mm thick, its lid as deep as the base, opened 105-115 degrees for work; a 24 inch monitor's panel is about
# 0.54 x 0.32 m on a stand 0.10 m over the desk; a full-size keyboard 0.43 x 0.13 m; a mouse 6.5 x 11 cm.
LAPTOP_BASE_T = 0.016             # the closed base (keyboard deck), metres
LAPTOP_LID_T = 0.006              # the lid (display) slab
LAPTOP_FACE_T = 0.0015            # the bezel and the screen on the lid's inner face
LAPTOP_OPEN_DEG = 110.0           # the angle between the base and the opened lid
LAPTOP_BEZEL_M = (0.008, 0.012, 0.018)   # the screen's bezel: sides, top, bottom (the hinge side)
MONITOR_FOOT_T = 0.012
KEY_PITCH_M = 0.019               # a keyboard's key pitch (19 mm, ISO/IEC 9995)


def laptop_box(base_w: float, base_d: float, base_t: float = LAPTOP_BASE_T) -> tuple[float, float, float]:
    """The box ``(w, d, h)`` of an open laptop of base ``base_w x base_d`` (pure): the lid as deep as the base,
    opened ``LAPTOP_OPEN_DEG``, leaning back past the hinge; ``work_set_parts`` builds the laptop into it."""
    lean = math.radians(LAPTOP_OPEN_DEG - 90.0)
    d = base_d * (1.0 + math.sin(lean)) + LAPTOP_LID_T * math.cos(lean)
    h = base_t + base_d * math.cos(lean) + LAPTOP_FACE_T * math.sin(lean)
    return round(float(base_w), 4), round(d, 4), round(h, 4)


def _lid_slab(cx: float, hinge: tuple[float, float], lean: float, w: float, length: float, thick: float,
              offset: float, key: str, role: str, z_from: float = 0.0) -> Part:
    """A slab of the opened lid (pure): ``w`` wide along X, ``length`` along the lid from ``z_from`` up (the lid
    direction ``u`` = (0, sin lean, cos lean) from the hinge point ``(y, z)``), ``thick`` across it from ``offset``
    (the lid normal ``n`` = (0, cos lean, -sin lean) points behind the screen; a negative offset lies in front of the
    inner face). The box's axes go to (X, n, u), a proper rotation, so its faces keep their outward winding."""
    verts, faces = geom2d.box((0.0, 0.0, 0.0), (w, thick, length), 0.0)
    su, cu = math.sin(lean), math.cos(lean)
    oy = hinge[0] + (offset + thick / 2.0) * cu + (z_from + length / 2.0) * su
    oz = hinge[1] - (offset + thick / 2.0) * su + (z_from + length / 2.0) * cu
    out = [(cx + x, oy + y * cu + z * su, oz - y * su + z * cu) for x, y, z in verts]
    return {"verts": out, "faces": faces, "key": key, "role": role}


def work_set_parts(dtype: str, w: float, d: float, h: float) -> list[Part]:
    """29 Oct 2026 (user: "Computer on the table would have been nice or a laptop"): the parametric work set of a desk
    in the item's box (bottom on z = 0, front -Y = the user's side), PBR keys ``steel`` (the aluminium shells),
    ``dark`` (keys, bezels, the monitor's panel, the mouse) and ``screen`` (``materials.screen_material``): ``laptop``
    (the base, its key field and trackpad, the lid opened ``LAPTOP_OPEN_DEG`` with its bezel and screen; the base the
    largest that fits the box, ``laptop_box``), ``monitor`` (a foot, a neck, the panel and its screen), ``keyboard``
    (a plate, key rows of ``KEY_PITCH_M``, a space bar) and ``computer_mouse``."""
    if dtype == "laptop":
        lean = math.radians(LAPTOP_OPEN_DEG - 90.0)
        su, cu = math.sin(lean), math.cos(lean)
        bt = min(LAPTOP_BASE_T, h * 0.08)
        bd = max(0.02, min((d - LAPTOP_LID_T * cu) / (1.0 + su), (h - bt - LAPTOP_FACE_T * su) / cu))
        depth = bd * (1.0 + su) + LAPTOP_LID_T * cu
        y0 = -depth / 2.0                             # the front edge of the base, the box centred on the item
        hinge = (y0 + bd, bt)
        keys_d, pad_d = bd * 0.40, bd * 0.26
        sb, tb, bb = (min(v, w * 0.08, bd * 0.12) for v in LAPTOP_BEZEL_M)
        return [_box(0.0, y0 + bd / 2.0, 0.0, w, bd, bt, "steel", "base"),
                _box(0.0, hinge[0] - bd * 0.06 - keys_d / 2.0, bt, w * 0.86, keys_d, 0.0012, "dark", "keys"),
                _box(0.0, y0 + bd * 0.06 + pad_d / 2.0, bt, w * 0.34, pad_d, 0.0006, "dark", "trackpad"),
                _lid_slab(0.0, hinge, lean, w, bd, LAPTOP_LID_T, 0.0, "steel", "lid"),
                _lid_slab(0.0, hinge, lean, w - 0.002, bd - 0.001, LAPTOP_FACE_T * 0.6, -LAPTOP_FACE_T * 0.6,
                          "dark", "bezel"),
                _lid_slab(0.0, hinge, lean, w - 2.0 * sb, bd - bb - tb, LAPTOP_FACE_T * 0.4, -LAPTOP_FACE_T,
                          "screen", "screen", z_from=bb)]
    if dtype == "monitor":
        panel_t = min(0.03, d * 0.2)
        panel_h = min(h * 0.75, w * 0.6)
        z_p = h - panel_h
        py = max(-d / 2.0 + 0.003 + panel_t / 2.0, -panel_t / 2.0 - 0.01)   # just in front of the foot's middle
        neck_y = min(d / 2.0 - 0.0125, py + panel_t / 2.0 + 0.0125)          # the neck right behind the panel
        bezel = min(0.008, w * 0.02, panel_h * 0.05)
        return [_box(0.0, 0.0, 0.0, min(0.24, w * 0.45), d * 0.9, MONITOR_FOOT_T, "steel", "foot"),
                _box(0.0, neck_y, MONITOR_FOOT_T, min(0.05, w * 0.12), 0.025, z_p + panel_h * 0.5 - MONITOR_FOOT_T,
                     "steel", "neck"),
                _box(0.0, py, z_p, w, panel_t, panel_h, "dark", "panel_back"),
                _box(0.0, py - panel_t / 2.0 - 0.001, z_p + bezel * 1.5, w - 2.0 * bezel, 0.002,
                     panel_h - 2.5 * bezel, "screen", "screen")]
    if dtype == "keyboard":
        plate_h = h * 0.45
        margin = min(0.012, w * 0.03, d * 0.08)
        cols = max(1, int((w - 2 * margin) / KEY_PITCH_M))
        rows = max(1, min(5, int((d - 2 * margin) / KEY_PITCH_M)))
        px, py = (w - 2 * margin) / cols, (d - 2 * margin) / rows
        cap_w, cap_d = px * 0.84, py * 0.84
        parts = [_box(0.0, 0.0, 0.0, w, d, plate_h, "steel", "base")]
        x0, y0 = -w / 2.0 + margin, -d / 2.0 + margin
        for r in range(rows):
            y = y0 + py * (r + 0.5)
            if r == 0 and cols >= 9:                   # the front row: a space bar between the modifier keys
                bar = (cols - 6) * px - (px - cap_w)
                parts.append(_box(x0 + 3 * px + bar / 2.0 + (px - cap_w) / 2.0, y, plate_h, bar, cap_d,
                                  h - plate_h, "dark", "space_bar"))
                keys = list(range(3)) + list(range(cols - 3, cols))
            else:
                keys = list(range(cols))
            for c in keys:
                parts.append(_box(x0 + px * (c + 0.5), y, plate_h, cap_w, cap_d, h - plate_h, "dark", "key"))
        return parts
    if dtype == "computer_mouse":
        return [_superellipsoid(0.0, 0.0, 0.0, w, d, h, 0.55, 0.75, "dark", "body", n_eta=8, n_om=16)]
    raise KeyError(f"no work set builder for {dtype!r}")


TV_PANEL_T_M = 0.03               # 29 Oct 2026 (UL99): a slim LED panel's depth
TV_BEZEL_M = 0.01                 # its bezel (= furniture.media_wall.TV_BEZEL_M)
TV_STAND_H_M = 0.06               # the pedestal's height under the panel (= media_wall.TV_STAND_H_M)
TV_BACK_GAP_M = 0.05              # the panel's back this far in from the box's back (the host's top, by its wall)


def tv_parts(w: float, d: float, h: float, item: dict | None = None) -> list[Part]:
    """29 Oct 2026 (user on real06: "There is no TV in the house", lesson UL99): a flat TV on its pedestal at the
    item's box (bottom on z = 0, the screen facing -Y), its panel at the back of the box (the box reaches the host's
    front so nothing stands before the screen): a pedestal plate and neck (``dark`` / ``steel``), the panel housing
    with a slim bezel (``dark`` lacquer) and the screen (``screen``: dark glossy glass, a faint reflection) inset on
    its front. ``item["tv"]`` may give ``stand_depth_m`` and ``back_gap_m``."""
    spec = (item or {}).get("tv") if isinstance((item or {}).get("tv"), dict) else {}
    gap = min(float(spec.get("back_gap_m", TV_BACK_GAP_M)), max(0.0, d - TV_PANEL_T_M - 0.01))
    y_back = d / 2.0 - gap
    stand_d = min(float(spec.get("stand_depth_m", 0.22)), max(0.05, d - gap))
    stand_w = min(w * 0.35, 0.45)
    panel_h = max(0.05, h - TV_STAND_H_M)
    bezel = min(TV_BEZEL_M, w / 20.0, panel_h / 20.0)
    y_front = y_back - TV_PANEL_T_M
    return [_box(0.0, y_back - stand_d / 2.0, 0.0, stand_w, stand_d, 0.012, "dark", "foot"),
            _box(0.0, y_back - TV_PANEL_T_M / 2.0, 0.012, 0.06, 0.02, TV_STAND_H_M - 0.012 + 0.04, "steel", "neck"),
            _box(0.0, y_back - TV_PANEL_T_M / 2.0, TV_STAND_H_M, w, TV_PANEL_T_M, panel_h, "dark", "panel"),
            _box(0.0, y_front - 0.001, TV_STAND_H_M + bezel, w - 2.0 * bezel, 0.002, panel_h - 2.0 * bezel, "screen",
                 "screen")]


MEDIA_DECOR_TYPES: tuple[str, ...] = ("tv",)         # 29 Oct 2026 (UL99), built by ``tv_parts``
DECOR_TYPES = DECOR_TYPES + MEDIA_DECOR_TYPES
LARGE_DECOR_TYPES = LARGE_DECOR_TYPES + MEDIA_DECOR_TYPES          # a 43-65 inch set is 0.96-1.45 m wide
# 29 Oct 2026 (lessons UL114, UL123, UL124: the user's bathroom photos): the bathroom's decor, built by
# ``wenart.blender.bath_parts`` (= its BATH_DECOR_TYPES, pinned in tests/test_bathroom_details_20261029.py)
BATH_DECOR_TYPES: tuple[str, ...] = ("toilet_paper_holder", "toilet_brush", "towel_rail", "towel_shelf", "towel_bar",
                                     "feature_panel", "cove_light")
DECOR_TYPES = DECOR_TYPES + BATH_DECOR_TYPES
LARGE_DECOR_TYPES = LARGE_DECOR_TYPES + ("towel_rail", "feature_panel", "cove_light")   # 1.2 m, a wall, a ceiling band
SURFACE_DECOR_TYPES = SURFACE_DECOR_TYPES + MEDIA_DECOR_TYPES      # it stands on its TV unit's built top
DECOR_DEFAULT_HEIGHT["tv"] = 0.77                                  # a 55 inch set on its pedestal
if "screen" not in MATERIAL_KEYS:                                  # its glossy dark screen (also the work set's)
    MATERIAL_KEYS = MATERIAL_KEYS + ("screen",)
# 29 Oct 2026 (UL114, UL123, UL124): the bathroom's real heights (bath_parts.DECOR_HEIGHTS) and its material keys: the
# LED strips (``materials.led_material``), the light stone and terrazzo tops and panels, the towels (the room's accent)
DECOR_DEFAULT_HEIGHT.update({"toilet_paper_holder": 0.13, "toilet_brush": 0.38, "towel_rail": 1.2, "towel_shelf": 0.40,
                             "towel_bar": 0.45, "feature_panel": 2.5, "cove_light": 0.12})
MATERIAL_KEYS = MATERIAL_KEYS + tuple(k for k in ("led", "stone_light", "terrazzo", "towel") if k not in MATERIAL_KEYS)
BEVEL_BY_ROLE.update({"led": 0.0, "towel": 0.004, "rib": 0.001, "plate": 0.001, "button": 0.0005, "apron": 0.002,
                      "panel": 0.002, "glass": 0.0, "groove": 0.0})
BEVEL_BY_ROLE.update({"screen": 0.0, "neck": 0.002})


# 29 Oct 2026 (lessons UL113, UL115, UL119; the user's reference photos, docs/reference_details_20261029.md): the
# details' own decor types (a lit wall niche, an intercom panel, a floor vase with pampas, a leaning art frame, a bag, a
# desk's wall unit) and the variants of older types (a round mirror or rug, a ceiling track light, a TV on the wall, a
# vase with pampas, a styled book set) and the scheme forms of a nightstand or a desk: wenart.blender.detail_parts
DETAIL_DECOR_TYPES: tuple[str, ...] = ("wall_niche", "intercom", "floor_vase", "art_leaning", "bag",
                                       "desk_wall_unit")              # = detail_parts.DETAIL_DECOR_TYPES
DECOR_TYPES = DECOR_TYPES + DETAIL_DECOR_TYPES
LARGE_DECOR_TYPES = LARGE_DECOR_TYPES + ("wall_niche", "floor_vase", "art_leaning", "desk_wall_unit")
DECOR_DEFAULT_HEIGHT.update({"wall_niche": 2.2, "intercom": 0.22, "floor_vase": 1.3, "art_leaning": 1.4, "bag": 0.30,
                             "desk_wall_unit": 0.68})
MATERIAL_KEYS = MATERIAL_KEYS + ("led", "pampas")                  # an LED strip's glow; dried pampas plumes
BEVEL_BY_ROLE.update({"led": 0.0, "groove": 0.0, "plume": 0.0, "stem": 0.0, "bracket": 0.002, "cleat": 0.0,
                      "canvas": 0.0, "grille": 0.0, "button": 0.001, "lens": 0.0, "zip": 0.0, "strap": 0.002,
                      "object": 0.004, "knob": 0.002})
# 30 Oct 2026 (photo P16, lesson UL153): the living-dining room's own detail types, a panel wall of handle-less fronts
# with a lit niche and two round wall discs (= salon_parts.DECOR_TYPES, built by wenart.blender.salon_parts)
DETAIL_DECOR_TYPES = DETAIL_DECOR_TYPES + ("panel_wall", "wall_discs")
DECOR_TYPES = DECOR_TYPES + ("panel_wall", "wall_discs")
LARGE_DECOR_TYPES = LARGE_DECOR_TYPES + ("panel_wall", "wall_discs")
DECOR_DEFAULT_HEIGHT.update({"panel_wall": 2.6, "wall_discs": 0.72})
for _role, _r in (("lining", 0.0), ("disc", 0.003), ("bar", 0.002), ("candle", 0.002), ("stripe", 0.0)):
    BEVEL_BY_ROLE.setdefault(_role, _r)                              # new roles only: the others keep their radius


SUSPENSION_CORD_R_M = 0.004       # the cord of a hung light (as the parametric pendant's)
SUSPENSION_CANOPY_R_M = 0.06      # the ceiling canopy it hangs from
SUSPENSION_CANOPY_H_M = 0.025


def suspension_parts(cord_m: float) -> list[Part]:
    """The cord and ceiling canopy of a hung light (28 Oct 2026, user on real04's salon: "Light is flying in the air
    needs to be connected to ceiling"; pure): local frame, the cord from z = 0 (the model's top) up ``cord_m``, the
    canopy (``SUSPENSION_CANOPY_R_M`` x ``SUSPENSION_CANOPY_H_M``) above it, its top on the ceiling. Keys as the
    parametric pendant's (``dark`` cord, ``colour_steel`` canopy). A library pendant fitted to its own size hung 0.99 m
    under the ceiling with nothing up to it."""
    cord = max(0.0, float(cord_m))
    parts = [_cylinder_z(0.0, 0.0, cord, SUSPENSION_CANOPY_R_M, SUSPENSION_CANOPY_R_M, SUSPENSION_CANOPY_H_M,
                         "colour_steel", "canopy", n=16)]
    if cord > 1e-4:
        parts.insert(0, _cylinder_z(0.0, 0.0, 0.0, SUSPENSION_CORD_R_M, SUSPENSION_CORD_R_M, cord, "dark", "cord", n=6))
    return parts


_BUILDERS = {
    "bed": _bed, "bed_single": _bed, "bed_double": _bed,
    "sofa": lambda w, d, h, piece=None: _sofa(w, d, h, piece=piece),
    "armchair": lambda w, d, h, piece=None: _sofa(w, d, h, cushions=1, piece=piece),
    "table_dining": _table_m10, "table_coffee": lambda w, d, h, piece=None: _table_m10(w, d, h, piece, shelf=True),
    "desk": lambda w, d, h, piece=None: _table_m10(w, d, h, piece, desk=True),
    "chair": _chair, "wardrobe": _wardrobe_m10, "dresser": _drawers, "nightstand": _drawers, "tv_unit": _tv_unit,
    "bookshelf": _bookshelf, "kitchen_counter": lambda w, d, h, piece=None: _counter_m10(w, d, h, False, piece),
    "kitchen_island": lambda w, d, h, piece=None: _counter_m10(w, d, h, True, piece),
    "fridge": _fridge, "stove": _stove, "sink_kitchen": _sink, "washbasin": _washbasin_m10, "toilet": _toilet,
    "shower": _shower_m14, "bathtub": _bathtub, "washing_machine": _washing_machine,
    "stair": _stair, "side_table": _side_table, "floor_lamp": _floor_lamp, "potted_plant": _potted_plant,
    # Milestone 10 (docs/milestone10.md §1.1, §4.4, §4.5)
    "sofa_corner": _sofa_corner, "chaise": _chaise, "ottoman": _ottoman, "bench": _bench, "bar_stool": _bar_stool,
    "office_chair": _office_chair, "console_table": _console_table, "crib": _crib, "bunk_bed": _bunk_bed,
    "sideboard": _sideboard, "shoe_cabinet": _shoe_cabinet, "display_cabinet": _display_cabinet,
    "tall_cabinet": _tall_cabinet, "wall_cabinet": _wall_cabinet,
}
# Builders that read the piece itself (drawn flights, round shape; Milestone 10: the design, the L shape); the
# others take only the box.
_PIECE_BUILDERS = ("stair", "side_table", "table_dining", "table_coffee", "desk", "wardrobe", "kitchen_counter",
                   "kitchen_island", "washbasin", "sofa_corner", "console_table", "sideboard", "shoe_cabinet",
                   "display_cabinet", "tall_cabinet", "wall_cabinet",
                   # Milestone 13 families v2 read the design (fabric colour, front style, wood)
                   "bed", "bed_single", "bed_double", "sofa", "armchair", "nightstand", "dresser", "tv_unit",
                   "bookshelf",
                   # round 4: the chair family v2 reads the design's material tags (frame, seat, base)
                   "chair",
                   # 28 Oct 2026: the bath reads the walls it stands on (its panels, the mixer's end)
                   "bathtub",
                   # 29 Oct 2026 (UL114, UL123): the WC and the shower read their bathroom look
                   "toilet", "shower")


def build_parts(ftype: str, w: float, d: float, h: float, piece: dict | None = None) -> list[Part]:
    """Parts of a parametric piece in its local frame. ``KeyError`` for a
    type without a builder (``unknown`` keeps the proxy box). ``piece``
    (optional) is read by the stair (its drawn flights) and the side table
    (round or square); without it a stair is one assumed flight."""
    try:
        builder = _BUILDERS[ftype]
    except KeyError:
        raise KeyError(f"no parametric builder for furniture type {ftype!r}") from None
    if piece is not None and piece.get("form"):      # 29 Oct 2026 (UL119): a room scheme's drum, floating form
        from wenart.blender import detail_parts as DP
        parts = DP.form_parts(ftype, float(w), float(d), float(h), piece)
        if parts is not None:
            return parts
    if ftype in _PIECE_BUILDERS:
        return builder(float(w), float(d), float(h), piece)
    return builder(float(w), float(d), float(h))


# --------------------------------------------------------------------------
# Decor (cushion, book_set, plant)
# --------------------------------------------------------------------------

def decor_size(dtype: str, size) -> tuple[float, float, float]:
    """``(w, d, h)`` of a decor item from its ``size`` (2 or 3 values),
    the type default height, every dimension capped at ``DECOR_MAX_M``
    (rugs and wall art, ``LARGE_DECOR_TYPES``, are not capped)."""
    w, d = float(size[0]), float(size[1])
    h = float(size[2]) if len(size) > 2 and size[2] else DECOR_DEFAULT_HEIGHT.get(dtype, 0.2)
    if dtype in LARGE_DECOR_TYPES:
        return tuple(max(0.005, v) for v in (w, d, h))
    return tuple(min(DECOR_MAX_M, max(0.02, v)) for v in (w, d, h))


BATH_MIRRORS: tuple[str, ...] = ("led_mirror", "backlit_mirror", "round_mirror")    # UL114 B4, UL123 B14, UL124 B22


def decor_parts(dtype: str, w: float, d: float, h: float, item: dict | None = None) -> list[Part]:
    """Parts of a parametric decor item of box ``w x d x h`` (``item``: the decor entry, read for a large
    plant's species)."""
    from wenart.blender import detail_parts as DP  # 29 Oct 2026 (UL113, UL115, UL119): the reference details

    if dtype in DETAIL_DECOR_TYPES:
        return DP.detail_parts(dtype, w, d, h, item)
    variant = DP.variant_parts(dtype, w, d, h, item)
    if variant is not None:
        return variant
    if dtype in MEDIA_DECOR_TYPES:                 # 29 Oct 2026 (UL99): the TV on its stand
        return tv_parts(w, d, h, item)
    if dtype in BATH_DECOR_TYPES or (dtype == "mirror" and (item or {}).get("fixture") in BATH_MIRRORS) or (
            dtype == "ceiling_light" and str((item or {}).get("trim") or "").startswith("square")):
        from wenart.blender import bath_parts as BT    # 29 Oct 2026 (UL114, UL123, UL124): the bathroom's details
        return BT.decor_parts(dtype, w, d, h, item)
    if dtype in _NEW_DECOR:
        return _new_decor_parts(dtype, w, d, h, item)
    if dtype == "cushion":                         # Milestone 12: a filled cushion, not a box
        if d > h:                                  # lying (an ottoman's, a bench's): thickness = the height
            return [lying_cushion_mesh(w, d, h, key="fabric", role="body")]
        return [cushion_mesh(w, d, h, key="fabric", role="body")]
    if dtype == "book_set":
        parts = []
        n = max(2, min(6, int(w / 0.04)))
        bw = w / n
        keys = ("dark", "painted", "wood", "terracotta")
        for i in range(n):
            bh = h * (0.75 + 0.25 * ((i * 7) % 3) / 2.0)
            parts.append(_box(-w / 2.0 + bw * (i + 0.5), 0.0, 0.0, bw - 0.004, d, bh, keys[i % len(keys)], "book"))
        return parts
    if dtype == "plant":
        r = min(w, d) / 2.0
        pot_h = h * 0.35
        return [
            _cylinder_z(0.0, 0.0, 0.0, r * 0.8, r * 0.8, pot_h, "terracotta", "pot", n=16),
            _cylinder_z(0.0, 0.0, pot_h - 0.01, r * 0.7, r * 0.7, 0.01, "dark", "soil", n=16),
            _cylinder_z(0.0, 0.0, pot_h, 0.012, 0.012, h - pot_h, "wood", "stem", n=8),
            _cylinder_z(0.0, 0.0, pot_h + (h - pot_h) * 0.35, r, r, (h - pot_h) * 0.65, "green", "crown", n=10),
        ]
    if dtype == "rug":                             # Milestone 8: a flat fabric rug at the rule's size
        return [_box(0.0, 0.0, 0.0, w, d, h, "fabric", "rug")]
    r = min(w, d) / 2.0                            # Milestone 9 (docs/milestone9.md §3)
    if dtype == "vase":
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.9, r * 0.9, h * 0.72, "accent_ceramic", "body", n=20),
                _cylinder_z(0.0, 0.0, h * 0.72, r * 0.5, r * 0.5, h * 0.28, "accent_ceramic", "neck", n=20)]
    if dtype == "bowl":
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.55, r * 0.55, h * 0.3, "accent_ceramic", "base", n=24),
                _cylinder_z(0.0, 0.0, h * 0.3, r, r, h * 0.7, "accent_ceramic", "body", n=24)]
    if dtype == "plant_small":
        pot_h = h * 0.4
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.7, r * 0.7, pot_h, "accent_ceramic", "pot", n=16),
                _cylinder_z(0.0, 0.0, pot_h - 0.01, r * 0.62, r * 0.62, 0.01, "dark", "soil", n=16),
                _cylinder_z(0.0, 0.0, pot_h, r, r, h - pot_h, "green", "crown", n=10)]
    if dtype == "table_lamp":
        return [_cylinder_z(0.0, 0.0, 0.0, r * 0.45, r * 0.45, h * 0.06, "accent_ceramic", "base", n=20),
                _cylinder_z(0.0, 0.0, h * 0.06, 0.012, 0.012, h * 0.52, "steel", "pole", n=8),
                _cylinder_z(0.0, 0.0, h * 0.55, r, r, h * 0.45, "fabric", "shade", n=24)]
    if dtype == "mirror":                          # a framed mirror: the glass on the front (local -Y) of the frame
        f = min(MIRROR_FRAME_M, w / 6.0, h / 6.0)
        g = min(0.004, d / 4.0)                    # the glass: the front 4 mm of the box, the frame behind it
        return [_box(0.0, g / 2.0, 0.0, w, d - g, h, "accent_wood", "frame"),
                _box(0.0, -d / 2.0 + g / 2.0, f, max(0.01, w - 2 * f), g, max(0.01, h - 2 * f), "mirror",
                     "glass")]
    raise KeyError(f"no decor builder for {dtype!r}")


# Milestone 12 (docs/milestone12.md §4.7, D13): ``decor_rest_height`` (the type-table rest height: a library bed's
# decor at 0.55 m, a sofa's at 0.45 m, a parametric bed's on the pillow top) is gone; decor rests on the built,
# scaled host mesh (``wenart.blender.rest``).


# --------------------------------------------------------------------------
# Bevel radius per part (the Bevel modifier itself is added by furniture.py)
# --------------------------------------------------------------------------

def part_bevel_radius(part: Part) -> float:
    """Bevel radius (metres) of one part: 0 for smooth (superellipsoid) parts
    and glass, ``BEVEL_SOFT_KEYS`` for fabric and bedding, else
    ``BEVEL_BY_ROLE`` / ``BEVEL_BY_KEY`` / ``BEVEL_DEFAULT_M``; never more
    than a third of the part's smallest side (nor ``BEVEL_WIDTH_M``)."""
    if part.get("smooth") or part["key"] in ("glass", "bulb"):
        return 0.0
    key, role = part["key"], part["role"]
    if key in BEVEL_SOFT_KEYS:
        r = BEVEL_SOFT_KEYS[key]
    elif role in BEVEL_BY_ROLE:
        r = BEVEL_BY_ROLE[role]
    else:
        r = BEVEL_BY_KEY.get(key, BEVEL_DEFAULT_M)
    xs, ys, zs = zip(*part["verts"])
    smallest = min(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    return max(0.0, min(r, smallest / 3.0, BEVEL_WIDTH_M))


# --------------------------------------------------------------------------
# Placement into the world and bounding boxes
# --------------------------------------------------------------------------

def world_mesh(parts: Sequence[Part], center: Sequence[float], rotation_deg: float, floor_z: float,
               scale: Sequence[float] = (1.0, 1.0, 1.0)) -> tuple[list, list, list[str]]:
    """``(verts, faces, face_keys)``: the parts scaled in the local frame,
    rotated about +Z and moved to ``center`` on the floor ``floor_z``."""
    verts, faces, keys = [], [], []
    rad = math.radians(rotation_deg)
    c, s = math.cos(rad), math.sin(rad)
    for part in parts:
        offset = len(verts)
        for x, y, z in part["verts"]:
            x, y, z = x * scale[0], y * scale[1], z * scale[2]
            verts.append((center[0] + c * x - s * y, center[1] + s * x + c * y, floor_z + z))
        for f in part["faces"]:
            faces.append([i + offset for i in f])
            keys.append(part["key"])
    return verts, faces, keys


def parametric_bbox(ftype: str, w: float, d: float, h: float, piece: dict | None = None) -> tuple[float, float, float]:
    """``(width, depth, height)`` of the parametric mesh (its real box);
    ``piece`` as in ``build_parts``."""
    x0, y0, z0, x1, y1, z1 = _bbox(build_parts(ftype, w, d, h, piece=piece))
    return (x1 - x0, y1 - y0, z1 - z0)


def piece_bbox(piece: dict) -> tuple[float, float, float, str]:
    """``(width, depth, height, source)`` of the box a piece occupies in its
    own frame, as the scene will build it: the fitted box recorded by the
    fitter (``asset.bbox_m`` is already scaled: footprint width and depth,
    catalogue height times the z scale) for a library asset, the parametric
    box otherwise, the proxy box for ``unknown``. The camera planner uses
    this (docs/milestone4.md §2: free points from fitted boxes, not only
    footprints)."""
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    h, _ = proxy_height(piece["type"], piece.get("height"))
    asset = piece.get("asset") or {}
    if asset.get("method") == "library" and asset.get("bbox_m"):
        bw, bd, bh = (float(v) for v in asset["bbox_m"][:3])
        return (bw, bd, bh, "library")
    if asset.get("method") == "module" and isinstance(asset.get("module_plan"), dict):
        from wenart.blender import modules as MOD          # Milestone 13: the module plan's real box

        try:
            bw, bd, bh = MOD.plan_bbox(asset["module_plan"])
            return (bw, bd, bh, "module")
        except (KeyError, TypeError, ValueError):
            pass                                             # a plan the builder cannot read: the family's box
    if piece["type"] in _BUILDERS:
        bw, bd, bh = parametric_bbox(piece["type"], w, d, h, piece=piece)
        return (bw, bd, bh, "parametric")
    return (w, d, h, "proxy")


def obstacle_rect(piece: dict) -> dict:
    """Footprint-shaped rectangle of the fitted box (never smaller than the
    drawn footprint), for the free-point search."""
    fp = piece["footprint"]
    bw, bd, _, _ = piece_bbox(piece)
    return {"center": list(fp["center"]), "size": [max(float(fp["size"][0]), bw), max(float(fp["size"][1]), bd)],
            "rotation_deg": float(fp["rotation_deg"])}


def local_bbox_of_world_points(points: Sequence[Sequence[float]], center: Sequence[float], rotation_deg: float
                               ) -> tuple[float, float, float, float, float, float]:
    """Bounding box of world points in the frame rotated by ``rotation_deg``
    about ``center`` (used by the tests to check rotated pieces)."""
    local = [(*G.rotate_point((p[0], p[1]), -rotation_deg, (center[0], center[1])), p[2]) for p in points]
    xs, ys, zs = [p[0] for p in local], [p[1] for p in local], [p[2] for p in local]
    return min(xs), min(ys), min(zs), max(xs), max(ys), max(zs)


# --------------------------------------------------------------------------
# Milestone 12 (docs/milestone12.md §4.7, §6.4; track S): textile meshes (cushions, cloth, curtains, blinds);
# ``wenart.blender.textiles`` drapes the cloth on a built host with them
# --------------------------------------------------------------------------

CUSHION_GRID = (10, 10)
SEAM_M = 0.006                    # the half thickness left at a cushion's seam
EDGE_DRAW = 0.035                 # a cushion's edges are drawn in by this share of the side between the corners
CLOTH_OFFSET_M = 0.005            # the shrinkwrap offset (§4.7: 5 mm)
CLOTH_THICKNESS_M = 0.008
FOLD_AMPLITUDE_M = 0.006          # modelled wrinkles (never into the host: added above the offset)
CLOTH_STEP_M = 0.05               # cloth grid pitch
PLEAT_PITCH_M = 0.12
PLEAT_DEPTH_M = 0.035
CURTAIN_LAYER_M = 0.003
SLAT_M = 0.025
SLAT_GAP_M = 0.022
SLAT_TILT_DEG = 20.0
BLIND_KINDS = ("roller", "slats")


def _cloth_part(verts, faces, key: str, role: str, smooth: bool = True) -> Part:
    return {"verts": [tuple(float(c) for c in v) for v in verts], "faces": [list(f) for f in faces], "key": key,
            "role": role, "smooth": smooth}


def cushion_mesh(w: float, t: float, h: float, grid: tuple[int, int] = CUSHION_GRID, key: str = "colour_fabric",
                 role: str = "cushion") -> Part:
    """A filled cushion in the box ``w x t x h`` (item frame: width X, thickness Y, height Z from 0): two faces
    bulging to ``t / 2`` in the middle (``(1 - u^4)(1 - v^4)`` profile), meeting at a ``SEAM_M`` seam; the seam
    ring is shared, so the mesh is closed; the edges are drawn in by ``EDGE_DRAW`` between the corners."""
    nu, nv = grid
    w, t, h = float(w), float(t), float(h)
    verts: list[tuple[float, float, float]] = []
    index: dict[tuple[int, int, int], int] = {}

    def vid(i: int, j: int, side: int) -> int:
        boundary = i in (0, nu) or j in (0, nv)
        key_ = (i, j, 0 if boundary else side)
        if key_ in index:
            return index[key_]
        u = -1.0 + 2.0 * i / nu
        v = -1.0 + 2.0 * j / nv
        draw_x = 1.0 - EDGE_DRAW * math.sin(math.pi * (v + 1.0) / 2.0)   # sides drawn in between the corners
        draw_z = 1.0 - EDGE_DRAW * math.sin(math.pi * (u + 1.0) / 2.0)
        x = u * w / 2.0 * draw_x
        z = h / 2.0 + v * h / 2.0 * draw_z
        half = max(SEAM_M, t / 2.0 * (1.0 - u ** 4) * (1.0 - v ** 4)) if not boundary else min(SEAM_M, t / 2.0)
        y = 0.0 if boundary else side * half
        index[key_] = len(verts)
        verts.append((x, y, z))
        return index[key_]

    faces = []
    for i in range(nu):
        for j in range(nv):
            # back face (+Y) outward = +Y; front face (-Y) outward = -Y
            faces.append([vid(i, j, 1), vid(i, j + 1, 1), vid(i + 1, j + 1, 1), vid(i + 1, j, 1)])
            faces.append([vid(i, j, -1), vid(i + 1, j, -1), vid(i + 1, j + 1, -1), vid(i, j + 1, -1)])
    zmin = min(v[2] for v in verts)
    verts = [(x, y, z - zmin) for x, y, z in verts]
    return _cloth_part(verts, faces, key, role)


def lying_cushion_mesh(w: float, d: float, t: float, key: str = "colour_fabric", role: str = "cushion") -> Part:
    """A cushion lying flat in the box ``w x d x t`` (thickness along Z from 0): ``cushion_mesh`` turned so its
    faces look up and down."""
    part = cushion_mesh(w, t, d, key=key, role=role)
    part["verts"] = [(x, z - d / 2.0, y + t / 2.0) for x, y, z in part["verts"]]
    # (x, y, z) -> (x, z, y) mirrors the winding: reverse the faces to keep them outward
    part["faces"] = [list(reversed(f)) for f in part["faces"]]
    zmin = min(v[2] for v in part["verts"])
    part["verts"] = [(x, y, z - zmin) for x, y, z in part["verts"]]
    return part


def flat_cloth(w: float, d: float, t: float, key: str = "colour_fabric", role: str = "throw") -> Part:
    """A cloth lying on a flat top (no host to drape over): its modelled folds on a plane, ``t`` at most high."""
    nu = max(2, int(round(w / CLOTH_STEP_M)))
    nv = max(2, int(round(d / CLOTH_STEP_M)))
    grid = np.zeros((nu + 1, nv + 1, 3))
    for i in range(nu + 1):
        for j in range(nv + 1):
            x, y = -w / 2.0 + w * i / nu, -d / 2.0 + d * j / nv
            grid[i, j] = (x, y, min(t, CLOTH_THICKNESS_M + fold(x + w / 2.0, y + d / 2.0, w, d) * 0.5))
    part = cloth_solid(grid, CLOTH_THICKNESS_M, key=key, role=role, along=(0.0, 0.0, 1.0))
    zmin = min(v[2] for v in part["verts"])
    part["verts"] = [(x, y, z - zmin) for x, y, z in part["verts"]]
    return part


def fold(x: float, y: float, w: float, d: float) -> float:
    """Modelled wrinkles (>= 0, at most ``FOLD_AMPLITUDE_M``): smooth fixed sines over the cloth's own frame."""
    a = math.sin(7.3 * x / max(w, 1e-6) + 0.7) * math.sin(5.1 * y / max(d, 1e-6) + 1.9)
    b = math.sin(13.0 * (x + 0.6 * y) / max(w + d, 1e-6) + 2.3)
    return FOLD_AMPLITUDE_M * (0.5 + 0.3 * a + 0.2 * b)


def _vertex_normals(grid: np.ndarray) -> np.ndarray:
    """Unit vertex normals of a grid surface, turned so that they point up on average (the cloth's outside)."""
    gu = np.gradient(grid, axis=0)
    gv = np.gradient(grid, axis=1)
    n = np.cross(gu, gv)
    ln = np.linalg.norm(n, axis=2, keepdims=True)
    n = n / np.where(ln < 1e-12, 1.0, ln)
    return -n if n.reshape(-1, 3).mean(axis=0)[2] < 0 else n


def cloth_solid(grid: np.ndarray, thickness: float = CLOTH_THICKNESS_M, key: str = "colour_fabric",
                role: str = "throw", along: Optional[Sequence[float]] = None) -> Part:
    """The draped sheet as a thin closed solid: the top layer = the grid, the bottom layer ``thickness`` below it
    along the vertex normals (or along the fixed direction ``along``: a flat cloth, a curtain panel, so the solid
    stays inside its box), joined at the rim; outward normals."""
    nu, nv = grid.shape[0] - 1, grid.shape[1] - 1
    normals = _vertex_normals(grid) if along is None else np.broadcast_to(np.asarray(along, dtype=np.float64),
                                                                           grid.shape)
    top = grid
    bottom = grid - normals * thickness
    verts = [tuple(p) for p in top.reshape(-1, 3)] + [tuple(p) for p in bottom.reshape(-1, 3)]
    n = (nu + 1) * (nv + 1)

    def t(i, j):
        return i * (nv + 1) + j

    faces = []
    for i in range(nu):
        for j in range(nv):
            faces.append([t(i, j), t(i + 1, j), t(i + 1, j + 1), t(i, j + 1)])
            faces.append([n + t(i, j), n + t(i, j + 1), n + t(i + 1, j + 1), n + t(i + 1, j)])
    rim = [(i, 0) for i in range(nu)] + [(nu, j) for j in range(nv)] + [(i, nv) for i in range(nu, 0, -1)] + \
          [(0, j) for j in range(nv, 0, -1)]
    for k in range(len(rim)):
        a, b = rim[k], rim[(k + 1) % len(rim)]
        faces.append([t(*a), n + t(*a), n + t(*b), t(*b)])
    return _cloth_part(verts, faces, key, role)


def _pleated_panel(x0: float, x1: float, h: float, depth: float, key: str, y0: float = 0.0,
                   pitch: float = PLEAT_PITCH_M, amp_max: float = PLEAT_DEPTH_M, role: str = "panel") -> Part:
    """A pleated curtain panel from x0 to x1 (item frame), hanging from h down to 0: a sine of ``pitch`` in Y
    (depth ``amp_max``, a little deeper at the hem) about ``y0``, two layers ``CURTAIN_LAYER_M`` apart, closed."""
    width = x1 - x0
    nu = max(4, int(round(width / (pitch / 4.0))))
    nv = 6
    grid = np.zeros((nu + 1, nv + 1, 3))
    amp = min(amp_max, depth / 2.0 - CURTAIN_LAYER_M)
    for i in range(nu + 1):
        x = x0 + width * i / nu
        for j in range(nv + 1):
            z = h * j / nv
            flare = 1.0 + 0.25 * (1.0 - j / nv)
            grid[i, j] = (x, y0 + amp * flare * math.sin(2.0 * math.pi * (x - x0) / pitch) * 0.5, z)
    part = cloth_solid(grid, CURTAIN_LAYER_M, key=key, role=role, along=(0.0, 1.0, 0.0))
    part["smooth"] = True
    return part


# 29 Oct 2026 (UL106; the professional reference: full-height curtains on a ceiling track, a white sheer behind a
# heavier drape): a layered curtain (``item["layers"]`` holds ``sheer``) hangs two sheer panels, each
# ``SHEER_PANEL_SHARE`` of the rod drawn in from its end (the middle of the window stays clear), behind the drape
# panels; ``item["track"] == "ceiling"`` hangs both from a slim ceiling track instead of the rod. Designer values.
SHEER_PANEL_SHARE = 0.30
DRAPE_PANEL_SHARE = 0.20         # the drape of a layered curtain, stacked at the ends in front of the sheer
SHEER_PLEAT_PITCH_M = 0.07
SHEER_PLEAT_DEPTH_M = 0.018
TRACK_SIZE_M = (0.045, 0.022)    # the ceiling track's depth and height (a recessed-look aluminium track)
CURTAIN_LAYERS = ("sheer", "drape")


def curtain_parts(w: float, d: float, h: float, key: str = "colour_fabric", item: dict | None = None) -> list[Part]:
    """An open pair of pleated panels under a rod (item frame: width X along the wall, the curtain's front -Y, from
    the floor gap up to the rod at ``h``): each panel covers ``CURTAIN_PANEL_SHARE`` of the rod. 29 Oct 2026
    (UL106): a layered curtain (``item["layers"]``) adds the sheer panels behind the drape (key ``sheer``), a
    ``ceiling`` track replaces the rod (key ``painted``)."""
    item = item or {}
    layered = "sheer" in (item.get("layers") or ())
    track = item.get("track") == "ceiling"
    if track:
        td, th = TRACK_SIZE_M
        parts = [_box(0.0, 0.0, h - th, w, min(td, d), th, "painted", "track")]
        top = h - th - 0.005
    else:
        parts = [_cylinder_x(-w / 2.0, 0.0, h - 0.02, 0.012, 0.012, w, "steel", "rod", n=12)]
        top = h - 0.05
    if not layered:
        pw = w * CURTAIN_PANEL_SHARE
        parts.append(_pleated_panel(-w / 2.0, -w / 2.0 + pw, top, d, key))
        parts.append(_pleated_panel(w / 2.0 - pw, w / 2.0, top, d, key))
        return parts
    sw, pw = w * SHEER_PANEL_SHARE, w * DRAPE_PANEL_SHARE
    back, front = d / 4.0, -d / 4.0                  # the sheer on the window side, the drape on the room side
    for x0, x1 in ((-w / 2.0, -w / 2.0 + sw), (w / 2.0 - sw, w / 2.0)):
        parts.append(_pleated_panel(x0, x1, top, d / 2.0, "sheer", y0=back, pitch=SHEER_PLEAT_PITCH_M,
                                    amp_max=SHEER_PLEAT_DEPTH_M, role="sheer"))
    for x0, x1 in ((-w / 2.0, -w / 2.0 + pw), (w / 2.0 - pw, w / 2.0)):
        parts.append(_pleated_panel(x0, x1, top, d / 2.0, key, y0=front))
    return parts


def blind_parts(w: float, d: float, h: float, kind: str = "roller", key: str = "colour_fabric") -> list[Part]:
    """A roller blind (a tube at the top, the fabric panel down to a bottom bar) or a slatted blind (``SLAT_M``
    slats every ``SLAT_M + SLAT_GAP_M`` tilted ``SLAT_TILT_DEG``, a head rail, two ladder tapes) in the box
    ``w x d x h`` (bottom at 0)."""
    if kind not in BLIND_KINDS:
        kind = "roller"
    if kind == "roller":
        tube = min(0.03, d / 2.0, h / 4.0)
        bar = min(0.02, h / 8.0)
        return [_cylinder_x(-w / 2.0, 0.0, h - tube, tube, tube, w, key, "roller", n=16),
                _box(0.0, -tube * 0.4, bar, w - 0.02, 0.004, h - tube - bar, key, "panel"),
                _box(0.0, -tube * 0.4, 0.0, w - 0.02, min(0.012, d), bar, "dark", "bar")]
    head = min(0.04, h / 6.0)
    parts = [_box(0.0, 0.0, h - head, w, min(d, 0.04), head, "painted", "rail")]
    pitch = SLAT_M + SLAT_GAP_M
    n = max(1, int((h - head) / pitch))
    a = math.radians(SLAT_TILT_DEG)
    sw = min(d * 0.9, SLAT_M * 1.6)
    for k in range(n):
        zc = h - head - (k + 0.5) * pitch
        if zc - SLAT_M < 0:
            break
        verts = []
        for dy, dz in ((-sw / 2.0, 0.0), (sw / 2.0, 0.0)):
            y, z = dy * math.cos(a), zc + dy * math.sin(a)
            verts += [(-w / 2.0 + 0.01, y, z - 0.0007), (w / 2.0 - 0.01, y, z - 0.0007),
                      (w / 2.0 - 0.01, y, z + 0.0007), (-w / 2.0 + 0.01, y, z + 0.0007)]
        faces = [[0, 1, 2, 3], [4, 7, 6, 5], [0, 4, 5, 1], [1, 5, 6, 2], [2, 6, 7, 3], [3, 7, 4, 0]]
        parts.append(_cloth_part(verts, faces, key, "slat", smooth=False))
    for sx in (-w / 3.0, w / 3.0):
        parts.append(_box(sx, 0.0, 0.0, 0.012, 0.002, h - head, "dark", "tape"))
    return parts
