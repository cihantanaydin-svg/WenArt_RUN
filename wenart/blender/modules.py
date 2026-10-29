"""Module builders (Milestone 13, track T2; docs/milestone13.md §3.0 K1, §12 D4, §13.2): a drawn anchor the library
cannot fit is built from real product modules, never left out and never a grey box.

What: ``module_plan(piece, style=None)`` (pure, no ``bpy``) turns a drawn piece into a plan of real modules
(``{builder, modules: [{kind, size_m, pos_m, rot_deg, material}], footprint_m, height_m, products}``), or None when
no module builder exists for its type or the modules cannot match the drawn footprint within ``MODULE_FIT_TOL``
(then the parametric family of ``wenart.blender.parametric`` builds the exact footprint). ``module_parts(plan)``
makes the parts (``parametric`` part dicts: ``verts``, ``faces``, ``key``, ``role``) in the piece frame (width X,
depth Y, front -Y, Z up from the floor); ``build_module(plan, piece, materials)`` makes the Blender object (``bpy``
inside) with one material slot per part key, the Bevel modifier of ``furniture.add_bevel`` and
``wenart_method = "module"``.

Builders (``MODULE_BUILDERS``: furniture type -> builder):

- ``wardrobe_run`` (wardrobe): frames of 0.50 / 0.75 / 1.00 m composed to the drawn run with end fillers, a plinth,
  a top panel, doors in the design's front style with bar handles at the meeting edges;
- ``table_long`` (table_dining): a top of real thickness on four tapered legs with an apron, or on two trestles
  for runs of 2.2 m and more; a drawn footprint deeper than a real table (``TABLE_DEPTH_MAX_M``) includes its
  chairs (CLAUDE.md: "a table footprint that includes its chairs"): it is split into the table and the chairs
  along both long sides, recorded in ``plan["split"]`` so the fit logs the piece ``adjusted_by_ai``;
- ``sofa_l`` (sofa_corner, or a ``sofa`` with ``shape: L``): straight seat modules of 0.90-1.10 m with an arm at the far
  end, and a chaise module 0.90 wide and 1.60-1.80 m deep on ``chaise_side`` (the rectangles of
  ``parametric.l_parts``), seat and back cushions, a base on short legs;
- ``kitchen_run`` (kitchen_counter, kitchen_island): base units 0.60 m deep in real widths, a 0.04 m worktop at
  0.90 m, a recessed plinth, fronts and handles, a sink cutout and a hob at the drawn or inferred places
  (``piece["module_hints"]``: ``sink_x_m`` / ``sink_pos_m`` / ``window_pos_m`` for the sink under the window,
  ``hob_x_m`` / ``hob_pos_m``; without a hint no cutout is made, because the drawn sink and stove are their own
  pieces), wall units 0.35 m deep from 1.40 to 2.10 m when ``module_hints.wall_units`` is true. Fix round after P3
  (16-17 Oct 2026): the fit's kitchen pre-pass (``wenart.furniture.fit.kitchen_built_ins``, with
  ``member_in_run``) gives the drawn sink inside a run as ``sink_pos_m`` / ``sink_w_m`` / ``sink_piece`` (the sink
  unit holds it: ``plan["built_ins"]``) and the drawn stoves inside it as ``ranges`` (gaps with no base unit,
  plinth or worktop at their drawn spans: ``plan["gaps"]``); P3 had built both inside full-depth base units. Part 2
  (17 Oct 2026): the sink unit is hollow above its bowl (``parametric.open_carcass``), the sink is built in only
  within ``KITCHEN_END_SHIFT_MAX_M`` of its drawn centre (else it stands as drawn in a gap of the run, as a pinned
  sink does), and a gap never takes the whole run. Part 3 (17 Oct 2026): that distance is measured across the run
  too (the bowl sits on the run's centreline), so a sink drawn over the run's front or back edge is not built in.
  26 Oct 2026 (user: "fix should be general"): the hob and the under-counter fridge the completion built into a run
  (``solver.built_in_kitchen``; the fit gives ``hob_pos_m`` / ``hob_w_m`` / ``hob_piece`` / ``oven`` and
  ``fridge_pos_m`` / ``fridge_w_m`` / ``fridge_piece``) are held by their units (``plan["built_ins"]`` kinds ``hob``
  and ``fridge``): the hob unit carries the black hob plate with its rings on the worktop and, in a full-depth run,
  a 59.5 cm built-in oven (steel control strip with knobs, black glass door with a window and a bar handle) over a
  drawer; the fridge unit a steel appliance door with a bar handle and a vent grille (``_appliance_fronts``);
  Kitchen design (28 Oct 2026; user on real04 run 20261028-005318-full: "Kitchen design could have been a lot better
  this is terrible"; on real06 run 20261027-222248-full: "What kind of a kitchen is this", "Why is this closing the
  window"). Why: the drawn 0.75 x 0.55 m stove of real04's run f_L-1_002 stood in a gap of the run as a freestanding
  library cooker 0.77 m high under a 0.90 m worktop, no hob had a hood, the completion's wall cabinets were boxes of
  3.35 / 0.69 / 0.56 m with a 0.76 m gap at the stove and a 0.25 m gap at the corner, and real06's pinned hob and
  fridge left the run while the architect moved a window behind two wall cabinets. What: (1) a drawn hob in a run
  (``module_hints["hob_span_m"]``, from the fit's pre-pass) is a hob unit at its drawn span (``drawn_hob_span``: a
  hob's width, 0.45-0.95 m; a drawn hob wins its span before the sink unit, which takes the next smaller real width),
  never end-shifted, its plate the real class of the unit (``hob_plate_for``: five burners from 70 cm) on one
  continuous worktop, an oven under it in a full-depth run (a 60 cm oven with side fronts in a wider unit);
  (2) every hob unit takes a cooker hood (``hood_module``: ``hood_width_for`` the hob, a chimney hood on the wall up
  to ``hood_top_m``, an under-cabinet hood under a wall cabinet, an island hood over an island; the style's metal:
  the ``handle`` key), recorded as ``plan["hood"]``; the plan records its worktop line (``worktop_m``);
  (3) ``plan_wall_run`` builds a wall cabinet of the completion (one stretch of a wall run) of real wall units
  (``compose_aligned``: 300-900 mm, joints on the base joints of its run, flush at hard ends, a blind corner unit,
  fillers, never a lone box of odd width); (4) the build cuts a wall cabinet at the windows and glazed doors of the
  building as built (``wall_unit_blocks``, ``clear_windows``) and slides a worktop item off a window it would reach
  (``worktop_item_window``, ``slide_worktop_item``); (5) the kitchen modules' bar handles stand on two feet
  (``with_handle_posts``). How: pure plans; the fit gives the hints (``wenart.furniture.fit.hob_hints``,
  ``wall_run_hints``), the model review checks the result (``model_review.kitchen_design``, M13).
  Kitchen details (29 Oct 2026; lessons UL115, kitchen part, and UL118; the user's reference photos: "look at all
  these details I want these details"): with a style (``style`` or the hints' ``family``) the plan follows its
  family's row of ``kitchen_details.FAMILY_KITCHEN``: a tall-unit column at the run end the fit names
  (``module_hints["column"]``: an oven tower and a fridge, fronts to the ceiling; K1), waterfall ends on an island
  (K2 / K15), knee space for the stools on an island's back (``module_hints["seat_side"]``; G3), a cylinder island
  hood in a hanging shelf frame (K3), fluted or handle-less uppers (K4), a utensil rail (G3) and a pull-down tap in
  the handles' metal (K7); every detail is recorded in ``plan["details"]``. Without a style the plan is the one of
  before (the tap aside).
- ``bath_set`` (washbasin at least 0.45 m deep: a wall-hung vanity with drawer fronts, a ceramic top with one or
  two inset basins and taps and a framed mirror above, the vanity hollow above the basins since the fix round after
  P3, part 2; shower: a tray of a real product size with the glass screen and shower set of
  ``parametric._shower``). The toilet stays with the parametric family.

Why: the three real projects left 43 (real04), 46 and 25 drawn pieces unbuilt or as plain boxes because the
library has no model near the drawn size (docs/milestone13.md §1.3: 3.35 m tables, 2.57 and 3.11 m wardrobe runs,
a 4.38 x 1.97 m corner sofa, kitchen runs). The user's decision D4 ("yes, but we need a good model") asks for
fallbacks that look like real products: real module sizes, real proportions and PBR material slots.

How: every size comes from a real product range, cited at the constant; module widths are composed by
``compose_run`` (a small dynamic programme over the real widths, the remainder as end fillers within
``WARDROBE_FILLER_MAX_M`` / ``KITCHEN_FILLER_MAX_M``, as fitters do on site); the plan keeps the drawn footprint
exactly where the modules can, and records the deviation in ``plan["fit"]``. The parts reuse the primitives and
the cabinet fronts of ``wenart.blender.parametric`` (boxes, cylinders, frustums, superellipsoid cushions,
``cabinet_fronts`` in the design's front style). Material keys are the ``parametric.MATERIAL_KEYS`` the style
fills (``wood``, ``front``, ``handle``, ``dark``, ``worktop``, ``fabric``, ``steel``, ``ceramic``, ``glass``,
``mirror``, ``painted``), so every object has several real material slots.

Sources of the module sizes (checked 12 Oct 2026; ikea.com is blocked by this session's proxy, so the IKEA product
records were read through the GitHub mirror felixrinker/floor-planner @408e3d7c, ``daten/cache/*.json`` and
``preisvergleich_at_sk.csv``, which carry the ikea.com/at/de product URLs and ``sizeText`` of each article; on
15 Oct 2026 that repository answered 404 and ikea.com stayed blocked, so the PAX and METOD numbers keep their
12 Oct provenance and the track report flags them; the US cabinet numbers were re-read on 15 Oct from the utariga
file named below, the tables, chairs, trays, basins and wardrobe depths come from the project's own size table):

- IKEA PAX wardrobe frames ("Korpus Kleiderschrank"): 50x58x236 (art. 904.582.21), 75x58x236 (904.582.35),
  100x58x236 (804.582.07); combinations 150 / 175 / 200 / 250 / 375 x 58 x 201 or 236 cm; a 35 cm deep variant
  (53x35x201 corner element) -> frame widths 0.50 / 0.75 / 1.00 m, depths 0.35 / 0.58 m, heights 2.01 / 2.36 m.
- IKEA METOD kitchen carcasses ("Unterschrank" base 40x37x80, 60x60x80, 80x60x80, corner 88x60x80 cm;
  "Wandschrank" wall 60x37x100, 80x37x100, 40x100 cm; ikea.com/at/de/p/metod-...-50205626 / -20205538 / -90205530)
  -> base widths 0.40 / 0.60 / 0.80 m, base depth 0.60 m, wall depth 0.37 m, wall widths 0.40 / 0.60 / 0.80 m.
- US cabinetry nominal sizes (chrisrogers3d/utariga @da8dbfad, docs/research/kitchen/layout-rules-and-dimensions.md,
  compiled from bobvila.com and sebringdesignbuild.com cabinet guides and the NKBA planning guidelines): base
  widths in 3 in steps 9-48 in (0.30 / 0.45 / 0.90 m = 12 / 18 / 36 in), base box depth 610 mm, counter height
  36 in = 914 mm, toe kick 76 mm deep, upper cabinets 305 mm deep, sink base 762 / 914 mm, cooktop cutout
  699-749 x 508-533 mm (30 in class), fillers 51-76 mm.
- the project's own size table ``wenart/recognition/size_table.yaml`` (product rows: kitchen base units 0.6 deep
  with the worktop at 0.85-0.95 m, wall units 0.3-1.2 x 0.3-0.37, wardrobes 0.5-0.7 deep, shower trays
  0.80-1.20 x 0.80-0.90, washbasins 0.45-0.80 x 0.35-0.50, chairs 0.45 x 0.45, chaises 0.55-0.95 x 1.30-2.00,
  dining tables 0.80-3.00 x 0.70-1.20 with the 10-seat 3.35 x 1.00 of real02).
- docs/milestone13.md §13.1 (the lead's contract): straight sofa modules 0.90-1.10 m, chaise 1.60-1.80 m deep,
  worktop 0.04 m at 0.90 m, wall units 0.35 m deep at 1.40-2.10 m, vanity 0.60 x 0.46-0.60 m. The chaise depths
  are the size table's chaise products (0.65 x 1.60, 0.75 x 1.70, 0.85 x 1.80 m); the straight module is one and
  a half seats of the size table's sofa products (2-seat 130 / 160, 3-seat 200 / 220: 0.65-0.73 m per seat).
- seat pitch 0.60 m per cover: Neufert's 60 cm per place as quoted by the secondary compilations read in the
  Milestone 13 placement research (docs/milestone13.md §2.4; jhkim0759/SceneConductor scene_norms.yaml,
  interaeronav/TokenEfficiencyEngine 19_interior_design/06).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import kitchen_details as KD
from wenart.blender import parametric as P
from wenart.blender.proxies import proxy_height

Part = dict

# --------------------------------------------------------------------------
# Real module sizes (metres), each with its source (module docstring)
# --------------------------------------------------------------------------

MODULE_FIT_TOL = 0.10                 # the plan's footprint may differ from the drawn one by this share (per side)
MODULE_METHOD = "module"              # asset.method of a piece built here (docs/milestone13.md §13.2)

# Wardrobe runs: IKEA PAX frames (mirror of ikea.com/at/de, module docstring).
WARDROBE_FRAME_WIDTHS_M: tuple[float, ...] = (0.50, 0.75, 1.00)
WARDROBE_FRAME_DEPTHS_M: tuple[float, ...] = (0.35, 0.58)
WARDROBE_FRAME_HEIGHTS_M: tuple[float, ...] = (2.01, 2.36)
WARDROBE_FILLER_MAX_M = 0.13          # the remainder of a 0.25 m grid split on both ends (fitters' scribe panels)
WARDROBE_PLINTH_M = 0.08              # PAX frames stand on the floor; a built-in run gets a recessed plinth (D4 look)
WARDROBE_TOP_M = 0.02
WARDROBE_DOOR_MAX_M = 0.50            # PAX hinged doors are 50 cm wide: a 100 frame takes two, a 50 / 75 one
WARDROBE_DEPTH_RANGE_M = (0.35, 0.80)

# Kitchen runs: IKEA METOD (0.40 / 0.60 / 0.80) and the US 3 in series (0.30 / 0.45 / 0.90 = 12 / 18 / 36 in).
KITCHEN_BASE_WIDTHS_M: tuple[float, ...] = (0.30, 0.40, 0.45, 0.60, 0.80, 0.90)
KITCHEN_BASE_DEPTH_M = 0.60           # METOD 60 deep; US 24 in = 610 mm
KITCHEN_WORKTOP_HEIGHT_M = 0.90       # the contract; METOD 80 carcass + 8 legs + worktop; US 36 in = 914 mm
KITCHEN_WORKTOP_RANGE_M = (0.80, 1.20) # a drawn height in this range is a counter height and is kept (size table:
                                      # kitchen_counter 0.85-0.95, kitchen_island 0.85-1.10 bar height); outside it
                                      # the contract's 0.90 m, noted in the plan (reviewer fix 15 Oct 2026: a drawn
                                      # 0.85 m was silently made 0.90 m, a drawn 1.40 m became a 1.40 m counter)
KITCHEN_WORKTOP_M = 0.04              # the contract (docs/milestone13.md §13.1)
KITCHEN_PLINTH_M = 0.10               # METOD legs 8 cm, plinth 8-10 cm; US toe kick 76 mm deep
KITCHEN_PLINTH_RECESS_M = 0.06
KITCHEN_FILLER_MAX_M = 0.08           # NKBA / US guides: fillers 51-76 mm (module docstring)
KITCHEN_END_SHIFT_MAX_M = 0.10        # a sink or hob unit this close to the run's end moves to the wall (no slit
                                      # thinner than a filler); a wider slit beside it becomes a filler panel
KITCHEN_SINK_UNIT_WIDTHS_M: tuple[float, ...] = (0.60, 0.80, 0.90)   # METOD 60 sink base; US 30 / 36 in sink bases
KITCHEN_HOB_UNIT_WIDTHS_M: tuple[float, ...] = (0.45, 0.60, 0.75, 0.80, 0.90)  # 60 cm hob class (size table stove
                                      # 0.60); 36 in; 26 Oct 2026: the 45 cm hob of a short stretch (groups.yaml
                                      # built_in.hob); 28 Oct 2026: the 75 / 80 cm units of groups.yaml's wide hob
                                      # option (0.75, 0.90) and of US 30 in cooktops
# 26 Oct 2026 (module docstring): a module built into the run by the completion (``solver.built_in_kitchen``): the hob
# unit takes an oven under the hob when the run is full depth (``module_hints["oven"]``; a 60 cm built-in oven is
# 59.5 cm high, its control strip 9 cm), an under-counter fridge a 60 cm unit with an appliance door (82 cm class).
KITCHEN_FRIDGE_UNIT_WIDTHS_M: tuple[float, ...] = (0.60,)
KITCHEN_OVEN_H_M = 0.595
KITCHEN_OVEN_STRIP_M = 0.09
KITCHEN_SINK_BOWL_M = 0.18            # the steel bowl's depth under the worktop's top face (the depth it had since
                                      # Milestone 13); fix round after P3, part 2: the sink unit is hollow above it
KITCHEN_HOB_PLATE_M = (0.58, 0.51)    # a 60 cm class hob plate on the worktop (US 30 in cutout 699-749 x 508-533 mm
                                      # per the utariga compilation; the 60 cm class is the contract's EU size)
KITCHEN_WALL_WIDTHS_M: tuple[float, ...] = (0.40, 0.60, 0.80)        # METOD wall carcasses 40 / 60 / 80
KITCHEN_WALL_DEPTH_M = 0.35           # the contract (METOD 37, US 12 in = 305 mm)
KITCHEN_WALL_BOTTOM_M = 1.40          # the contract: wall units from 1.40 to 2.10 m
KITCHEN_WALL_TOP_M = 2.10
# 27 Oct 2026: a fridge-freezer column (IKEA METOD high cabinet 60x60x200 / 220; integrated fridge-freezers 177-194 cm
# in a 60 cm housing) at a run end, its top in line with the wall units; the freezer door the lower 40 %
KITCHEN_COLUMN_TOP_M = KITCHEN_WALL_TOP_M
KITCHEN_COLUMN_FREEZER_SHARE = 0.40
KITCHEN_COLUMN_MIN_REST_M = 0.60      # a column only when this much counter stays beside it
KITCHEN_DRAWER_UNIT_W_M = 0.60        # a 60 unit takes three drawers (METOD / MAXIMERA); wider ones two doors
# Fix round after P3 (16-17 Oct 2026): a drawn freestanding range (``stove``) inside a drawn run stands in a gap of
# the run (``module_hints["ranges"]``): no base unit, plinth or worktop over its drawn span, which is kept exactly
# (no end shift: the stove stays where it is drawn); a gap narrower than this is dropped (a drawing artefact).
KITCHEN_GAP_MIN_M = 0.10
KITCHEN_GAP_KIND = "range"
# 28 Oct 2026 (user on real04's kitchen: "Kitchen design could have been a lot better this is terrible"; module
# docstring "Kitchen design"): a drawn hob in a run keeps its drawn span when its width is a hob's (the stove product
# range of the library audit, 0.45-0.95 m; a 0.75 x 0.55 m drawing is the 75 cm / US 30 in class, cutout 699-749 x
# 508-533 mm); the plate is the real class that fits its unit (domino 30, 45, 60 (58 cm plate), 70, 75, 80, 90 cm),
# five burners from the 70 cm class (gas hobs of 70-90 cm carry a wok burner in the middle).
KITCHEN_HOB_SPAN_RANGE_M = (0.45, 0.95)
KITCHEN_HOB_PLATES_M: tuple[float, ...] = (0.30, 0.45, 0.58, 0.70, 0.75, 0.80, 0.90)
KITCHEN_HOB_PLATE_D_M = 0.51
KITCHEN_HOB_FIVE_FROM_M = 0.70
KITCHEN_OVEN_W_M = 0.596             # a 60 cm built-in oven (59.5-59.7 cm wide); a wider hob unit gets side fronts
# The cooker hood over every hob (28 Oct 2026): widths of real hoods (60, 75 (US 30 in), 90, 100, 120 cm), never
# narrower than the hob unit; the canopy's bottom 0.65 m over the hob (EN 60335-2-31 and the makers' minimum over a
# gas hob, which also suits electric hobs: 0.55-0.65 m), 0.70 m over an island hob; canopy depths of real chimney
# (0.50), island (0.60) and under-cabinet hoods (0.30, no deeper than a wall cabinet); a chimney of 0.28 x 0.24 m up
# to the ceiling (the fit passes ``hood_top_m``; without it 2.40 m, a usual room's lowest ceiling).
HOOD_WIDTHS_M: tuple[float, ...] = (0.60, 0.75, 0.90, 1.00, 1.20)
HOOD_CLEAR_M = 0.65
HOOD_ISLAND_CLEAR_M = 0.70
HOOD_UNDER_MIN_CLEAR_M = 0.50        # an under-cabinet hood lower than this over the hob is noted (drawn cabinets)
HOOD_DEPTHS_M = {"chimney": 0.50, "island": 0.60, "under_cabinet": 0.30}
HOOD_CANOPY_M = 0.06
HOOD_UNDER_H_M = 0.10
HOOD_CHIMNEY_M = (0.28, 0.24)
HOOD_TOP_DEFAULT_M = 2.40
HOOD_KINDS: tuple[str, ...] = ("chimney", "under_cabinet", "island")
# The wall run (28 Oct 2026): a wall cabinet the completion hangs is one stretch of a wall run; it is built of real
# wall units (300-900 mm: METOD wall 30 / 40 / 60 / 80, US 12-36 in) whose joints line up with the base units under
# them, flush at the hood, a wall and a corner, a corner filler where it meets another run's front, a blind corner
# unit where it runs into the corner behind the other run (made to measure: blind part + a door of 0.30-0.60 m).
WALL_RUN_WIDTHS_M: tuple[float, ...] = (0.30, 0.40, 0.45, 0.50, 0.60, 0.80, 0.90)
WALL_RUN_TOL_M = 0.006               # a span this close to a real width is that unit (a fitter's scribe)
WALL_RUN_FILLER_MAX_M = 0.08         # NKBA / US guides: fillers 51-76 mm (as KITCHEN_FILLER_MAX_M)
WALL_RUN_BLIND_DOOR_M = (0.30, 0.60)  # the door of a blind corner unit beside its blind part
WALL_RUN_HARD_ENDS: tuple[str, ...] = ("hood", "wall", "corner_butt", "corner_blind")
WALL_RUN_WINDOW_MARGIN_M = 0.05      # at build: a wall unit stays this far off a window or glazed door of the wall
HANDLE_POST_M = (0.010, 0.012)       # a bar handle stands off its front on two feet (post size, stand-off)

# Tables: wenart/recognition/size_table.yaml (table_dining depth 0.70-1.20; chair 0.45 x 0.45).
TABLE_DEPTH_MAX_M = 1.20              # a drawn footprint deeper than this includes its chairs
TABLE_DEPTH_RANGE_M = (0.80, 1.10)    # the table left after the split
TABLE_TOP_M = 0.04
TABLE_TRESTLE_FROM_M = 2.20           # tables this long stand on two trestles (slab legs) instead of four legs
CHAIR_SIZE_M = (0.45, 0.45)           # the size table's chair product
CHAIR_PITCH_M = 0.60                  # Neufert's 60 cm per cover (secondary compilations, module docstring)
CHAIR_TUCK_M = 0.05                   # a chair's seat slides this far under the table edge
CHAIR_ZONE_M = 0.50                   # the band a tucked chair needs beyond the table edge

# L sofas: the contract's module ranges; the chaise width of parametric.l_parts (schemas.L_CHAISE_WIDTH_M).
SOFA_MODULE_RANGE_M = (0.90, 1.10)
SOFA_CHAISE_DEPTH_RANGE_M = (1.60, 1.80)
SOFA_CHAISE_WIDTHS_M: tuple[float, ...] = (0.85, 0.90, 0.95, 1.00)
SOFA_ARM_WIDTHS_M: tuple[float, ...] = (0.15, 0.20, 0.25)
SOFA_BACK_M = 0.22
SOFA_SEAT_DEPTH_M = P.L_SEAT_DEPTH_M  # the main seat rectangle of l_parts (incl. the back)
SOFA_LEG_M = 0.10
SOFA_CUSHION_M = 0.14

# Bath set: the size table's products (shower trays, washbasins) and the contract's vanity depth.
SHOWER_TRAYS_M: tuple[tuple[float, float], ...] = ((0.90, 0.90), (0.80, 0.80), (1.00, 0.80), (1.20, 0.80), (1.20, 0.90))
VANITY_DEPTH_RANGE_M = (0.45, 0.60)   # the contract 0.46-0.60; looks.VANITY_MIN_DEPTH_M = 0.45 decides the vanity look
VANITY_WIDTH_RANGE_M = (0.45, 1.60)
VANITY_DOUBLE_FROM_M = 1.10           # two basins from this width (assumed, noted in the plan)
VANITY_BOTTOM_M = 0.30                # wall-hung: free floor under the cabinet (parametric._vanity)
VANITY_CABINET_MIN_H_M = 0.25         # the smallest vanity cabinet (one drawer front); a washbasin drawn lower than
                                      # VANITY_BOTTOM_M + top + this (0.58 m; the size table allows 0.10 m: a counter
                                      # bowl) is not a vanity and stays with the parametric family (reviewer fix
                                      # 15 Oct 2026: it got a cabinet of negative height)
VANITY_MIRROR_H_M = 0.80
VANITY_MIRROR_BOTTOM_MIN_M = 1.15
VANITY_MIRROR_DEPTH_M = 0.03
BASIN_M = (0.50, 0.36, 0.14)          # bowl width, depth, basin depth (parametric._vanity)

MODULE_BUILDERS: dict[str, str] = {
    "wardrobe": "wardrobe_run",
    "table_dining": "table_long",
    "sofa_corner": "sofa_l",
    "kitchen_counter": "kitchen_run",
    "kitchen_island": "kitchen_run",
    "wall_cabinet": "wall_run",          # 28 Oct 2026: real wall units in line with the base run (module docstring)
    "washbasin": "bath_set",
    "shower": "bath_set",
}


# --------------------------------------------------------------------------
# Pure helpers
# --------------------------------------------------------------------------

def _mm(v: float) -> int:
    return int(round(float(v) * 1000.0))


def compose_run(width: float, sizes: Sequence[float], max_filler: float) -> Optional[dict]:
    """Compose ``width`` from the real module ``sizes`` (metres): the combination whose sum is the largest not
    above ``width`` (ties: fewer modules, then the larger ones first), the remainder split as two end fillers.
    Returns ``{"widths": [..], "filler_m": per end, "sum_m"}`` or None when the width is below the smallest module
    or the fillers would exceed ``max_filler`` (pure dynamic programme over millimetres)."""
    target = _mm(width)
    steps = sorted({_mm(s) for s in sizes}, reverse=True)
    if not steps or target < min(steps):
        return None
    best: dict[int, tuple[int, list[int]]] = {0: (0, [])}            # sum -> (count, widths)
    for total in range(1, target + 1):
        for s in steps:
            prev = best.get(total - s)
            if prev is None:
                continue
            cand = (prev[0] + 1, sorted(prev[1] + [s], reverse=True))
            cur = best.get(total)
            if cur is None or cand[0] < cur[0] or (cand[0] == cur[0] and cand[1] > cur[1]):
                best[total] = cand
    reach = max(t for t in best if t <= target)
    count, widths = best[reach]
    filler = (target - reach) / 2000.0
    if filler > max_filler + 1e-9:
        return None
    return {"widths": [w / 1000.0 for w in widths], "filler_m": round(filler, 4), "sum_m": reach / 1000.0}


def nearest(value: float, options: Sequence[float]) -> float:
    return min(options, key=lambda o: abs(o - value))


def _fit_record(drawn: Sequence[float], built: Sequence[float], tol: float = MODULE_FIT_TOL) -> dict:
    dw, dd = float(built[0]) - float(drawn[0]), float(built[1]) - float(drawn[1])
    rel = max(abs(dw) / max(float(drawn[0]), 1e-6), abs(dd) / max(float(drawn[1]), 1e-6))
    return {"dw_m": round(dw, 4), "dd_m": round(dd, 4), "rel": round(rel, 4), "tol": tol, "within_cap": rel <= tol + 1e-9}


def _hints(piece: dict) -> dict:
    hints = piece.get("module_hints")
    return hints if isinstance(hints, dict) else {}


def _local_x(piece: dict, pos) -> Optional[float]:
    """A world point's x in the piece frame (along the run), or None."""
    if not pos or len(pos) < 2:
        return None
    fp = piece.get("footprint") or {}
    c = fp.get("center") or [0.0, 0.0]
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    dx, dy = float(pos[0]) - float(c[0]), float(pos[1]) - float(c[1])
    return math.cos(rot) * dx + math.sin(rot) * dy


def _local_y(piece: dict, pos) -> Optional[float]:
    """A world point's y in the piece frame (across the run, front -Y), or None (fix round after P3, part 3)."""
    if not pos or len(pos) < 2:
        return None
    fp = piece.get("footprint") or {}
    c = fp.get("center") or [0.0, 0.0]
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    dx, dy = float(pos[0]) - float(c[0]), float(pos[1]) - float(c[1])
    return -math.sin(rot) * dx + math.cos(rot) * dy


def _local_corners(piece: dict, other: dict) -> Optional[list[tuple[float, float]]]:
    """The four footprint corners of ``other`` in ``piece``'s frame (x along its width, y across), or None."""
    fp, ofp = piece.get("footprint") or {}, other.get("footprint") or {}
    try:
        c = [float(v) for v in fp["center"][:2]]
        oc = [float(v) for v in ofp["center"][:2]]
        ow, od = float(ofp["size"][0]), float(ofp["size"][1])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    orot = math.radians(float(ofp.get("rotation_deg") or 0.0))
    co, so = math.cos(orot), math.sin(orot)
    cr, sr = math.cos(rot), math.sin(rot)
    out = []
    for x, y in ((-ow / 2.0, -od / 2.0), (ow / 2.0, -od / 2.0), (ow / 2.0, od / 2.0), (-ow / 2.0, od / 2.0)):
        wx, wy = oc[0] + co * x - so * y - c[0], oc[1] + so * x + co * y - c[1]
        out.append((cr * wx + sr * wy, -sr * wx + cr * wy))
    return out


def _clip_to_box(poly: list[tuple[float, float]], hx: float, hy: float) -> list[tuple[float, float]]:
    """Sutherland-Hodgman: a convex polygon clipped to the box ``[-hx, hx] x [-hy, hy]``."""
    def clip(pts, inside, cut):
        out = []
        for i, p in enumerate(pts):
            q = pts[i - 1]
            if inside(p):
                if not inside(q):
                    out.append(cut(q, p))
                out.append(p)
            elif inside(q):
                out.append(cut(q, p))
        return out

    def at_x(xv):
        return lambda q, p: (xv, q[1] + (p[1] - q[1]) * (xv - q[0]) / (p[0] - q[0]))

    def at_y(yv):
        return lambda q, p: (q[0] + (p[0] - q[0]) * (yv - q[1]) / (p[1] - q[1]), yv)

    pts = list(poly)
    for inside, cut in ((lambda p: p[0] <= hx, at_x(hx)), (lambda p: p[0] >= -hx, at_x(-hx)),
                        (lambda p: p[1] <= hy, at_y(hy)), (lambda p: p[1] >= -hy, at_y(-hy))):
        if not pts:
            break
        pts = clip(pts, inside, cut)
    return pts


def _area(poly: Sequence[tuple[float, float]]) -> float:
    return abs(sum(poly[i - 1][0] * p[1] - p[0] * poly[i - 1][1] for i, p in enumerate(poly))) / 2.0


def member_in_run(run: dict, member: dict) -> Optional[dict]:
    """Where a drawn piece lies in a drawn run (pure; fix round after P3, 16-17 Oct 2026): ``{"share": the share of
    the member's footprint inside the run's footprint, "x0_m", "x1_m": the member's extent along the run (the run's
    frame, not clipped), "x_m": its centre, "w_m": its width along the run}``, or None without usable footprints.
    The fit's kitchen pre-pass (``wenart.furniture.fit.kitchen_built_ins``) reads it to build a drawn sink into the
    run and to leave a gap for a drawn stove."""
    corners = _local_corners(run, member)
    fp = run.get("footprint") or {}
    try:
        w, d = float(fp["size"][0]), float(fp["size"][1])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    if corners is None or not (w > 0 and d > 0):
        return None
    full = _area(corners)
    if full <= 1e-12:
        return None
    inside = _area(_clip_to_box(corners, w / 2.0, d / 2.0))
    xs = [p[0] for p in corners]
    x0, x1 = min(xs), max(xs)
    return {"share": round(inside / full, 4), "x0_m": round(x0, 4), "x1_m": round(x1, 4),
            "x_m": round((x0 + x1) / 2.0, 4), "w_m": round(x1 - x0, 4)}


def _module(kind: str, size, pos, material: str, rot_deg: float = 0.0, **extra) -> dict:
    rec = {"kind": kind, "size_m": [round(float(v), 4) for v in size], "pos_m": [round(float(v), 4) for v in pos],
           "rot_deg": float(rot_deg), "material": material}
    rec.update(extra)
    return rec


def _piece_size(piece: dict) -> tuple[float, float, float]:
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    h, _assumed = proxy_height(piece["type"], piece.get("height"))
    return w, d, float(h)


# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------

def plan_wardrobe_run(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """PAX-style frames composed to the drawn run (end fillers), a plinth, a top, doors with handles."""
    w, d, h = _piece_size(piece)
    if not (WARDROBE_DEPTH_RANGE_M[0] - 1e-9 <= d <= WARDROBE_DEPTH_RANGE_M[1] + 1e-9):
        return None
    run = compose_run(w, WARDROBE_FRAME_WIDTHS_M, WARDROBE_FILLER_MAX_M)
    if run is None:
        return None
    given = piece.get("height")
    if isinstance(given, (int, float)) and not isinstance(given, bool) and given > 1.0:
        frame_h = float(given) - WARDROBE_PLINTH_M                     # the drawn height is kept
    else:
        frame_h = nearest(h - WARDROBE_PLINTH_M, WARDROBE_FRAME_HEIGHTS_M)
    height = frame_h + WARDROBE_PLINTH_M
    depth_product = nearest(d, WARDROBE_FRAME_DEPTHS_M)
    modules = [_module("plinth", (w - 2 * 0.0, d - 0.04, WARDROBE_PLINTH_M), (0.0, 0.02), "dark")]
    x = -w / 2.0 + run["filler_m"]
    products: list[str] = []
    for i, fw in enumerate(run["widths"]):
        doors = 2 if fw > WARDROBE_DOOR_MAX_M + 1e-9 and fw >= 1.0 - 1e-9 else 1
        modules.append(_module("frame", (fw, d, frame_h), (x + fw / 2.0, 0.0), "front", z_m=WARDROBE_PLINTH_M,
                               doors=doors, hinge="left" if i % 2 == 0 else "right",
                               product=f"PAX frame {fw * 100:.0f}x{depth_product * 100:.0f}x{frame_h * 100:.0f} cm"))
        products.append(modules[-1]["product"])
        x += fw
    if run["filler_m"] > 1e-9:
        for sx in (-1, 1):
            modules.append(_module("filler", (run["filler_m"], d, frame_h),
                                   (sx * (w / 2.0 - run["filler_m"] / 2.0), 0.0), "front", z_m=WARDROBE_PLINTH_M))
    modules.append(_module("top", (w, d, WARDROBE_TOP_M), (0.0, 0.0), "wood", z_m=height - WARDROBE_TOP_M))
    notes = [f"frames {' + '.join(f'{v:.2f}' for v in run['widths'])} m" + (
        f" with {run['filler_m'] * 100:.1f} cm fillers at both ends" if run["filler_m"] > 1e-9 else " (no filler)")]
    if abs(d - depth_product) > 0.02:
        notes.append(f"depth {d:.2f} m made to measure (nearest PAX depth {depth_product:.2f} m)")
    return {"builder": "wardrobe_run", "type": piece["type"], "modules": modules, "footprint_m": [w, d],
            "height_m": round(height, 4), "drawn_m": [w, d], "fit": _fit_record((w, d), (w, d)),
            "products": sorted(set(products), key=products.index), "notes": notes,
            "design": P.piece_design(piece)}


def plan_table_long(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """A long table on legs or trestles; a footprint deeper than a real table is split into table and chairs."""
    w, d, h = _piece_size(piece)
    if w < 0.80 - 1e-9 or d < 0.60 - 1e-9:
        return None
    split = None
    table_d = d
    if d > TABLE_DEPTH_MAX_M + 1e-9:
        table_d = min(TABLE_DEPTH_RANGE_M[1], max(TABLE_DEPTH_RANGE_M[0], d - 2 * CHAIR_ZONE_M))
        split = {"table_m": [w, round(table_d, 4)], "reason": (f"the drawn footprint is {d:.2f} m deep, more than a "
                                                               f"real table ({TABLE_DEPTH_MAX_M} m): it includes the "
                                                               "chairs along both long sides (CLAUDE.md)")}
    legs = "trestles" if w >= TABLE_TRESTLE_FROM_M - 1e-9 else "legs"
    modules = [_module("top", (w, table_d, TABLE_TOP_M), (0.0, 0.0), "wood", z_m=h - TABLE_TOP_M, support=legs)]
    if legs == "trestles":
        tw = min(0.10, w * 0.05)
        for sx in (-1, 1):
            modules.append(_module("trestle", (tw, table_d - 0.30, h - TABLE_TOP_M),
                                   (sx * (w / 2.0 - 0.45), 0.0), "wood"))
    else:
        leg = min(0.07, w * 0.05, table_d * 0.08)
        inset = min(0.08, w * 0.06, table_d * 0.06)
        for sx in (-1, 1):
            for sy in (-1, 1):
                modules.append(_module("leg", (leg, leg, h - TABLE_TOP_M),
                                       (sx * (w / 2.0 - inset - leg / 2.0), sy * (table_d / 2.0 - inset - leg / 2.0)),
                                       "wood"))
    seats = 0
    if split is not None:
        per_side = max(1, int((w - 0.30 + 1e-9) // CHAIR_PITCH_M))
        pitch = (w - 0.30) / per_side
        cy = table_d / 2.0 + CHAIR_SIZE_M[1] / 2.0 - CHAIR_TUCK_M
        for k in range(per_side):
            cx = -w / 2.0 + 0.15 + pitch * (k + 0.5)
            # the chair's front (-Y in its own frame) faces the table: the -Y side chairs turn 180 degrees
            modules.append(_module("chair", (CHAIR_SIZE_M[0], CHAIR_SIZE_M[1], 0.90), (cx, -cy), "wood", rot_deg=180.0))
            modules.append(_module("chair", (CHAIR_SIZE_M[0], CHAIR_SIZE_M[1], 0.90), (cx, cy), "wood", rot_deg=0.0))
        seats = 2 * per_side
        split["chairs"] = seats
        split["chair_m"] = list(CHAIR_SIZE_M)
    built_d = d if split is None else max(d, 2 * cy + CHAIR_SIZE_M[1])
    fit = _fit_record((w, d), (w, built_d))
    if not fit["within_cap"]:
        return None
    products = [f"dining table {w:.2f} x {table_d:.2f} m on {legs}" + (f" with {seats} chairs" if seats else "")]
    return {"builder": "table_long", "type": piece["type"], "modules": modules, "footprint_m": [w, round(built_d, 4)],
            "height_m": round(h, 4), "drawn_m": [w, d], "fit": fit, "products": products, "split": split,
            "seats": seats, "notes": [f"{legs}: {'two trestles' if legs == 'trestles' else 'four tapered legs'}"],
            "design": P.piece_design(piece)}


def _sofa_modules(w: float) -> Optional[tuple[float, float, list[float]]]:
    """``(arm width, chaise width, straight module widths)`` whose sum is exactly ``w`` with every module inside
    ``SOFA_MODULE_RANGE_M`` (the arm and chaise widths are searched over their product options); None when no
    combination keeps the modules in range."""
    lo, hi = SOFA_MODULE_RANGE_M
    best = None
    for arm in SOFA_ARM_WIDTHS_M:
        for cw in SOFA_CHAISE_WIDTHS_M:
            run = w - arm - cw
            if run < lo - 1e-9:
                continue
            n = max(1, int(round(run / ((lo + hi) / 2.0))))
            for count in (n, n + 1, max(1, n - 1)):
                mw = run / count
                if lo - 1e-9 <= mw <= hi + 1e-9:
                    score = (abs(mw - 1.0), abs(arm - 0.20), abs(cw - P.L_CHAISE_WIDTH_M))
                    if best is None or score < best[0]:
                        best = (score, arm, cw, [mw] * count)
    return None if best is None else (best[1], best[2], best[3])


def plan_sofa_l(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """Straight seat modules with an arm at the far end and a chaise module on ``chaise_side``."""
    w, d, h = _piece_size(piece)
    if piece.get("type") != "sofa_corner" and str(piece.get("shape") or "").upper() != "L":
        return None
    got = _sofa_modules(w)
    if got is None:
        return None
    arm, cw, widths = got
    side = piece.get("chaise_side") if piece.get("chaise_side") in ("left", "right") else "right"
    chaise_seat = min(SOFA_CHAISE_DEPTH_RANGE_M[1], max(SOFA_CHAISE_DEPTH_RANGE_M[0], d - SOFA_BACK_M))
    depth = chaise_seat + SOFA_BACK_M
    fit = _fit_record((w, d), (w, depth))
    if not fit["within_cap"]:
        return None
    main, chaise = P.l_parts((w, depth), side, depth, SOFA_SEAT_DEPTH_M, cw)
    mx0, mx1, my0, my1 = main
    cx0, cx1, cy0, cy1 = chaise
    seat_y = (my0 + my1) / 2.0
    modules = [_module("back", (w, SOFA_BACK_M, h), (0.0, depth / 2.0 - SOFA_BACK_M / 2.0), "fabric")]
    sign = -1.0 if side == "right" else 1.0            # the arm at the end away from the chaise
    x = sign * (w / 2.0) - sign * arm / 2.0
    modules.append(_module("arm", (arm, my1 - my0 - SOFA_BACK_M, min(0.65, h * 0.78)),
                           (x, seat_y - SOFA_BACK_M / 2.0), "fabric"))
    x = sign * (w / 2.0 - arm)
    for mw in widths:
        x_c = x - sign * mw / 2.0
        modules.append(_module("seat_module", (mw, my1 - my0 - SOFA_BACK_M, h), (x_c, seat_y - SOFA_BACK_M / 2.0),
                               "fabric", product=f"sofa module {mw:.2f} m"))
        x -= sign * mw
    modules.append(_module("chaise_module", (cx1 - cx0, cy1 - cy0 - SOFA_BACK_M, h),
                           ((cx0 + cx1) / 2.0, (cy0 + cy1 - SOFA_BACK_M) / 2.0), "fabric",
                           product=f"chaise module {cx1 - cx0:.2f} x {chaise_seat:.2f} m"))
    products = [m["product"] for m in modules if m.get("product")]
    return {"builder": "sofa_l", "type": piece["type"], "modules": modules, "footprint_m": [w, round(depth, 4)],
            "height_m": round(h, 4), "drawn_m": [w, d], "fit": fit, "products": sorted(set(products), key=products.index),
            "chaise_side": side, "chaise_side_assumed": piece.get("chaise_side") not in ("left", "right"),
            "rectangles": [[round(v, 4) for v in main], [round(v, 4) for v in chaise]],
            "notes": [f"arm {arm:.2f} m, {len(widths)} straight module(s) of {widths[0]:.2f} m, chaise {cw:.2f} x "
                      f"{chaise_seat:.2f} m on the {side}"], "design": P.piece_design(piece)}


def _place_fixed(w: float, x: Optional[float], unit_w: float) -> Optional[tuple[float, float]]:
    """``(x0, x1)`` of a fixed unit centred near ``x`` (piece frame), kept inside the run."""
    if x is None:
        return None
    x0 = min(max(x - unit_w / 2.0, -w / 2.0), w / 2.0 - unit_w)
    return (x0, x0 + unit_w)


def _gap_problem(w: float, x0: float, x1: float, taken: Sequence[tuple[float, float, str]]) -> Optional[str]:
    """Why a gap ``[x0, x1]`` (already clipped to a run of width ``w``) cannot be made, or None: narrower than
    ``KITCHEN_GAP_MIN_M``, overlapping a span of ``taken`` (another gap or a fixed unit), or leaving no stretch of
    the run (fix round after P3, part 2: a stove drawn over its whole run gave a plan with no module at all, and the
    build linked an empty object)."""
    if x1 - x0 < KITCHEN_GAP_MIN_M - 1e-9:
        return f"{max(x1 - x0, 0.0):.2f} m of it lies inside the run"
    if any(x0 < f1 - 1e-9 and x1 > f0 + 1e-9 for f0, f1, _k in taken):
        return "it overlaps another gap or the sink unit"
    if not _segments(w, [(f0, f1, k) for f0, f1, k in taken if k == KITCHEN_GAP_KIND] + [(x0, x1, KITCHEN_GAP_KIND)]):
        return "it would leave nothing of the run (the run is the appliance's own outline: the run is built whole)"
    return None


def _gap_record(rid: str, gtype: str, x0: float, x1: float, reason: Optional[str]) -> dict:
    """A ``plan["gaps"]`` record (fix round after P3, part 2: with the ``reason`` of a sink's gap)."""
    rec = {"id": rid, "kind": KITCHEN_GAP_KIND, "type": gtype, "x_m": round((x0 + x1) / 2.0, 4),
           "w_m": round(x1 - x0, 4)}
    if reason:
        rec["reason"] = str(reason)
    return rec


def _range_gaps(w: float, hints: dict) -> tuple[list[tuple[float, float, str]], list[dict], list[str]]:
    """``(fixed spans, gap records, notes)`` of the drawn ranges in a run of width ``w`` (fix round after P3): each
    ``module_hints["ranges"]`` entry ``{id, x0_m, x1_m}`` (the drawn stove's span in the run's frame) clipped to the
    run and kept exactly where it is drawn; one narrower than ``KITCHEN_GAP_MIN_M`` after the clip, or overlapping an
    earlier one, is dropped with a note. Fix round after P3, part 2 (17 Oct 2026): a gap that would leave nothing of
    the run is dropped too (``_gap_problem``), and an entry's ``reason`` (a pinned sink's gap) is kept on its
    record."""
    spans: list[tuple[float, float, str]] = []
    gaps: list[dict] = []
    notes: list[str] = []
    for r in hints.get("ranges") or []:
        try:
            x0, x1 = sorted((float(r["x0_m"]), float(r["x1_m"])))
        except (KeyError, TypeError, ValueError):
            continue
        x0, x1 = max(x0, -w / 2.0), min(x1, w / 2.0)
        rid = str(r.get("id") or "?")
        gtype = r.get("type") or "stove"
        problem = _gap_problem(w, x0, x1, spans)
        if problem:
            notes.append(f"no gap for the drawn {gtype} {rid}: {problem}")
            continue
        spans.append((x0, x1, KITCHEN_GAP_KIND))
        gaps.append(_gap_record(rid, gtype, x0, x1, r.get("reason")))
        notes.append(f"a {x1 - x0:.2f} m gap for the drawn {gtype} {rid}: no base unit, plinth or worktop over it (the "
                     "drawn piece stands there, as drawn, with its own model)")
    return spans, gaps, notes


def _segments(w: float, spans: Sequence[tuple[float, float, str]]) -> list[tuple[float, float]]:
    """The stretches of a run of width ``w`` between the (sorted, disjoint) ``spans``."""
    out: list[tuple[float, float]] = []
    x = -w / 2.0
    for f0, f1, _kind in sorted(spans):
        if f0 - x > 1e-6:
            out.append((x, f0))
        x = max(x, f1)
    if w / 2.0 - x > 1e-6:
        out.append((x, w / 2.0))
    return out


def plan_kitchen_run(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """Base units composed to the run (fixed sink and hob units first), the worktop with its cutouts, plinth, fronts
    and handles; wall units above when the hints ask for them.

    Fix round after P3 (16-17 Oct 2026). What: ``module_hints["ranges"]`` (the drawn stoves inside the run, from the
    fit's kitchen pre-pass) leave gaps with no base unit, plinth or worktop at their exact drawn spans (no end shift,
    a slit to the run's end is a filler panel), so the plinth and the worktop come in one module per stretch between
    the gaps (``pos_m`` along the run); ``module_hints["sink_piece"]`` names the drawn sink the sink unit holds
    (``plan["built_ins"]``: the fit builds that sink into the run, the scene does not build it again). Why: pod P3
    built the drawn sink and stove inside full-depth base units under an uncut worktop (only a tap and a stove front
    showed). How: a sink or hob unit that would overlap a gap is not made (noted); without hints the plan is the one
    of before.

    Fix round after P3, part 2 (17 Oct 2026). What: the drawn sink is built in only when its sink unit (unit width,
    clamped into the run, end shift) stands within ``KITCHEN_END_SHIFT_MAX_M`` of the drawn centre; ``built_ins``
    records ``drawn_x_m`` and ``shift_m``. Otherwise the sink is not built in: it keeps its own model and gets a gap
    at its drawn span (``gaps``: ``type: sink_kitchen`` with the ``reason``), as a pinned sink and a drawn stove do;
    a gap that would leave nothing of the run is never made, and a stretch narrower than an island's plinth recess
    has no plinth. Why: a drawn sink overhanging the run's end was built up to 0.4 of its width away from where it
    is drawn with no record (the CLAUDE.md fixed-equipment rule: as drawn), and a stove drawn over its whole run
    gave a plan with no module (an empty object in the scene). How: the sink unit is checked after the end shifts;
    ``_gap_problem`` decides every gap.

    Fix round after P3, part 3 (17 Oct 2026). What: the distance to the drawn centre is measured across the run too:
    the bowl stands at the sink unit's centre along the run and on the run's centreline (local y 0) across it, the
    drawn centre's local y comes from ``sink_pos_m`` (or ``module_hints["sink_y_m"]``, in the run's frame), and the
    sink is built in only when the bowl's centre is within ``KITCHEN_END_SHIFT_MAX_M`` of the drawn centre (both
    axes together); ``built_ins`` also records ``drawn_y_m`` and ``shift_y_m`` (the bowl's y minus the drawn y).
    Farther away the sink is not built in and gets a gap at its drawn span, with the reason, as in part 2. Why: the
    part 2 check read only the position along the run, so a drawn sink overhanging the counter's front (centred
    0.25 m in front of the centreline, 40 % of it outside the run) was built in on the centreline, 0.25 m from where
    it is drawn, with no record (the CLAUDE.md fixed-equipment rule: as drawn; nothing changes silently). How: one
    distance for both axes; without a drawn y (an inferred place) the offset across is 0 as before."""
    w, d, h = _piece_size(piece)
    if w < min(KITCHEN_BASE_WIDTHS_M) - 1e-9 or d < 0.45 - 1e-9:
        return None
    hints = _hints(piece)
    island = piece.get("type") == "kitchen_island"
    given = piece.get("height")
    drawn_h = float(given) if isinstance(given, (int, float)) and not isinstance(given, bool) and given > 0 else None
    in_range = drawn_h is not None and KITCHEN_WORKTOP_RANGE_M[0] - 1e-9 <= drawn_h <= KITCHEN_WORKTOP_RANGE_M[1] + 1e-9
    worktop_z = drawn_h if in_range else KITCHEN_WORKTOP_HEIGHT_M
    # 29 Oct 2026 (module docstring "Kitchen details"): the style family's kitchen details (None: no style, no details)
    family = KD.family_from(style, hints, P.piece_design(piece))
    rule = KD.family_rule(family) if family is not None else None
    gap_spans, gaps, notes = _range_gaps(w, hints)
    fixed: list[tuple[float, float, str]] = []
    sink_x = hints.get("sink_x_m")
    if sink_x is None:
        sink_x = _local_x(piece, hints.get("sink_pos_m")) if hints.get("sink_pos_m") else _local_x(piece, hints.get("window_pos_m"))
    # fix round after P3, part 3: the drawn sink's centre across the run (the bowl is built on its centreline, y 0)
    sink_y = hints.get("sink_y_m")
    if sink_y is None and hints.get("sink_pos_m"):
        sink_y = _local_y(piece, hints["sink_pos_m"])
    hob_x = hints.get("hob_x_m")
    if hob_x is None and hints.get("hob_pos_m"):
        hob_x = _local_x(piece, hints["hob_pos_m"])
    # 28 Oct 2026 (module docstring "Kitchen design"): a drawn hob keeps its drawn span (the fixed-equipment rule)
    hob_span = drawn_hob_span(w, hints.get("hob_span_m"))
    if hob_span is not None and hob_x is None:
        hob_x = (hob_span[0] + hob_span[1]) / 2.0

    def free(span) -> bool:
        return not any(span[0] < f[1] - 1e-9 and span[1] > f[0] + 1e-9 for f in fixed + gap_spans)

    if hob_span is not None:
        if free(hob_span):
            fixed.append((hob_span[0], hob_span[1], "hob"))
        else:
            notes.append("no hob unit at the drawn hob's span: it overlaps the gap of a drawn piece")
    if sink_x is not None:
        sw = nearest(float(hints.get("sink_w_m") or KITCHEN_SINK_UNIT_WIDTHS_M[0]), KITCHEN_SINK_UNIT_WIDTHS_M)
        span = None
        # 28 Oct 2026: beside a drawn hob the sink unit takes the next smaller real width before it gives up
        for width in [sw] + [v for v in sorted(KITCHEN_SINK_UNIT_WIDTHS_M, reverse=True) if v < sw - 1e-9]:
            span = _place_fixed(w, float(sink_x), min(width, w))
            if span is not None and free(span):
                break
        if span is not None and free(span):
            fixed.append((span[0], span[1], "sink"))
        elif span is not None:
            notes.append("no sink unit: it would overlap the gap of a drawn stove or the drawn hob")
    if hob_x is not None and hob_span is None:
        hw = nearest(float(hints.get("hob_w_m") or KITCHEN_HOB_UNIT_WIDTHS_M[1]), KITCHEN_HOB_UNIT_WIDTHS_M)
        span = _place_fixed(w, float(hob_x), min(hw, w))
        if span is not None and free(span):
            fixed.append((span[0], span[1], "hob"))
        elif span is not None:
            notes.append("no hob unit: it would overlap the sink unit or the gap of a drawn stove")
    # 26 Oct 2026: an under-counter fridge the completion built into the run (``fridge_pos_m`` / ``fridge_x_m``)
    fridge_x = hints.get("fridge_x_m")
    if fridge_x is None and hints.get("fridge_pos_m"):
        fridge_x = _local_x(piece, hints["fridge_pos_m"])
    if fridge_x is not None:
        fw = nearest(float(hints.get("fridge_w_m") or KITCHEN_FRIDGE_UNIT_WIDTHS_M[0]), KITCHEN_FRIDGE_UNIT_WIDTHS_M)
        span = _place_fixed(w, float(fridge_x), min(fw, w))
        if span is not None and free(span):
            fixed.append((span[0], span[1], "fridge"))
        elif span is not None:
            notes.append("no under-counter fridge unit: it would overlap another unit or a gap")
    fixed.sort()
    # a fixed unit near an end of the run moves to the wall when the slit left there is narrower than the
    # smallest unit (KITCHEN_END_SHIFT_MAX_M): a sink unit against the wall, not a 20 cm panel beside it; a gap of
    # a drawn stove never moves, and no unit shifts into one
    # 28 Oct 2026: a drawn hob stays at its drawn span (a slit to the run's end is a filler panel)
    drawn_hob = None if hob_span is None else (hob_span[0], hob_span[1], "hob")
    if fixed:
        f0, f1, kind = fixed[0]
        shifted = (-w / 2.0, -w / 2.0 + (f1 - f0), kind)
        if 1e-6 < f0 + w / 2.0 <= KITCHEN_END_SHIFT_MAX_M and fixed[0] != drawn_hob and not any(
                g0 < shifted[1] - 1e-9 and g1 > shifted[0] + 1e-9 for g0, g1, _k in gap_spans):
            fixed[0] = shifted
        f0, f1, kind = fixed[-1]
        shifted = (w / 2.0 - (f1 - f0), w / 2.0, kind)
        if 1e-6 < w / 2.0 - f1 <= KITCHEN_END_SHIFT_MAX_M and fixed[-1] != drawn_hob and not any(
                g0 < shifted[1] - 1e-9 and g1 > shifted[0] + 1e-9 for g0, g1, _k in gap_spans):
            fixed[-1] = shifted
    # fix round after P3, part 2: the drawn sink (``sink_piece``) is built in only where its sink unit stands within
    # KITCHEN_END_SHIFT_MAX_M of the drawn centre (the fixed-equipment rule: as drawn); else it keeps its own model
    # and stands as drawn, in a gap of the run (as a pinned sink and a drawn stove do)
    # (part 3: measured across the run too, where the bowl stands on the run's centreline, y 0)
    built_in = None
    sink_piece = hints.get("sink_piece")
    if sink_piece and sink_x is not None:
        unit = next(((f0, f1) for f0, f1, k in fixed if k == "sink"), None)
        shift = None if unit is None else (unit[0] + unit[1]) / 2.0 - float(sink_x)
        across = 0.0 - float(sink_y) if sink_y is not None else 0.0     # the bowl's y (0) minus the drawn y
        if shift is not None and math.hypot(shift, across) <= KITCHEN_END_SHIFT_MAX_M + 1e-9:
            built_in = (unit, shift, across)
        else:
            fixed = [f for f in fixed if f[2] != "sink"]
            why = ("its sink unit would overlap the gap of a drawn stove" if unit is None else
                   _sink_off_reason(unit[1] - unit[0], shift, across))
            sw_drawn = float(hints.get("sink_w_m") or (unit[1] - unit[0] if unit else KITCHEN_SINK_UNIT_WIDTHS_M[0]))
            g0, g1 = max(float(sink_x) - sw_drawn / 2.0, -w / 2.0), min(float(sink_x) + sw_drawn / 2.0, w / 2.0)
            problem = _gap_problem(w, g0, g1, gap_spans + fixed)
            if problem is None:
                gap_spans.append((g0, g1, KITCHEN_GAP_KIND))
                gaps.append(_gap_record(str(sink_piece), "sink_kitchen", g0, g1, f"not built in: {why}"))
                notes.append(f"the drawn sink {sink_piece} is not built in: {why}; a {g1 - g0:.2f} m gap at its "
                             "drawn span, where it stands as drawn with its own model")
            else:
                notes.append(f"the drawn sink {sink_piece} is not built in: {why}; no gap either ({problem}): it "
                             "stands on its own as drawn")
    # 27 Oct 2026 (pod run 224516, real06: the judge saw "no fridge": the built-in fridge was a 60 cm steel door under
    # the worktop, read as a dishwasher): a fridge at a run end with no wall cabinet over it (``fridge_column``, the
    # fit's hint) is a fridge-freezer column up to the wall units' top; the worktop and the plinth stop at its side
    column = None
    # 29 Oct 2026 (K1): the fit's column hint names the ceiling: the fridge column's fronts go up to it (a cupboard over
    # the fridge doors)
    column_hint = hints.get("column") if isinstance(hints.get("column"), dict) else None
    col_top = KD.column_top(column_hint) if rule and rule.get("tall_column") and column_hint else KITCHEN_COLUMN_TOP_M
    if hints.get("fridge_column") and not island:
        for f0, f1, kind in fixed:
            at_end = abs(f0 + w / 2.0) < 1e-6 or abs(f1 - w / 2.0) < 1e-6
            if kind == "fridge" and at_end and w - (f1 - f0) >= KITCHEN_COLUMN_MIN_REST_M - 1e-9:
                column = (f0, f1)
                gap_spans.append((f0, f1, "fridge_column"))
                notes.append(f"the fridge stands as a {f1 - f0:.2f} m fridge-freezer column at the run's end, "
                             f"{col_top:.2f} m high (no wall cabinet over it)")
                break
    # 29 Oct 2026 (module docstring "Kitchen details", K1): the tall-unit column at the run end the fit names (an oven
    # tower and, in a kitchen with no fridge, a fridge column), its fronts to the ceiling; the worktop and the plinth stop
    # at its side, as at the fridge column
    columns: list[tuple[float, float, str]] = []
    if rule and rule.get("tall_column") and column_hint and column_hint.get("kinds"):
        columns, col_notes = KD.column_spans(w, fixed + gap_spans, column_hint, island)
        notes += col_notes
        gap_spans += [(c0, c1, "tall_column") for c0, c1, _k in columns]
    # K2 / K15: an island of a waterfall family has its top down both ends (the units stand between the panels)
    panels, wf_notes = KD.waterfall_spans(w, gap_spans, island, rule)
    notes += wf_notes
    # G3: knee space for the stools on an island's back (base units 0.60 m deep, the worktop over the stools); not
    # with a sink or a hob in the island (their bowl and plate need the full depth)
    over = KD.overhang_of(d, island, hints) if rule and not fixed else None
    cd, cy = (over["carcass_d"], over["carcass_y"]) if over else (d, 0.0)
    if over:
        notes.append(f"the island's worktop runs {over['overhang']:.2f} m over its back for the stools' knees "
                     f"(base units {cd:.2f} m deep; G3)")
    segments = _segments(w, fixed + gap_spans + panels)
    base_h = worktop_z - KITCHEN_WORKTOP_M - KITCHEN_PLINTH_M
    stretches = _segments(w, gap_spans)                   # the plinth and the worktop run between the gaps
    modules = []
    for x0, x1 in stretches:
        # an island's plinth is recessed at the run's ends (all round), a counter's only at the front; a stretch
        # narrower than the recess has no plinth (fix round after P3, part 2: its width was negative)
        r0 = KITCHEN_PLINTH_RECESS_M if island and abs(x0 + w / 2.0) < 1e-6 else 0.0
        r1 = KITCHEN_PLINTH_RECESS_M if island and abs(x1 - w / 2.0) < 1e-6 else 0.0
        if x1 - x0 - r0 - r1 <= 1e-3:
            continue
        modules.append(_module("plinth", (x1 - x0 - r0 - r1, cd - KITCHEN_PLINTH_RECESS_M * (2 if island else 1),
                                          KITCHEN_PLINTH_M),
                               ((x0 + r0 + x1 - r1) / 2.0, cy if island else KITCHEN_PLINTH_RECESS_M / 2.0), "dark"))
    for p0, p1, _k in panels:
        modules.append(_module("waterfall", (p1 - p0, d, worktop_z - KITCHEN_WORKTOP_M), ((p0 + p1) / 2.0, 0.0),
                               "worktop", z_m=0.0, product=f"waterfall end {KITCHEN_WORKTOP_M * 100:.0f} mm"))
    units: list[dict] = []
    for x0, x1 in segments:
        seg_w = x1 - x0
        run = compose_run(seg_w, KITCHEN_BASE_WIDTHS_M, KITCHEN_FILLER_MAX_M)
        if run is None:                                   # a slit narrower than the smallest unit: a filler panel
            units.append(_module("filler", (seg_w, cd, base_h), ((x0 + x1) / 2.0, cy), "front", z_m=KITCHEN_PLINTH_M))
            continue
        # fillers at the run's outer ends only; inside the run the remainder sits next to the fixed unit
        # 29 Oct 2026: a waterfall panel's inner face is the run's end for the fillers
        at_left_end = abs(x0 + w / 2.0) < 1e-6 or any(abs(x0 - p1) < 1e-6 for _p0, p1, _k in panels)
        at_right_end = abs(x1 - w / 2.0) < 1e-6 or any(abs(x1 - p0) < 1e-6 for p0, _p1, _k in panels)
        rem = seg_w - run["sum_m"]
        left_f = rem / 2.0 if (at_left_end and at_right_end) else (rem if at_left_end else 0.0)
        right_f = rem - left_f
        if left_f > 1e-9:
            units.append(_module("filler", (left_f, cd, base_h), (x0 + left_f / 2.0, cy), "front",
                                 z_m=KITCHEN_PLINTH_M))
        xx = x0 + left_f
        for uw in run["widths"]:
            front = "drawers" if abs(uw - KITCHEN_DRAWER_UNIT_W_M) < 1e-9 else ("doors" if uw >= 0.80 - 1e-9 else "door")
            units.append(_module("base_unit", (uw, cd, base_h), (xx + uw / 2.0, cy), "front", z_m=KITCHEN_PLINTH_M,
                                 front=front, product=f"base unit {uw * 100:.0f}x{KITCHEN_BASE_DEPTH_M * 100:.0f} cm"))
            xx += uw
        if right_f > 1e-9:
            units.append(_module("filler", (right_f, cd, base_h), (xx + right_f / 2.0, cy), "front",
                                 z_m=KITCHEN_PLINTH_M))
    oven_tower = any(k == "oven_tower" for _c0, _c1, k in columns)
    for f0, f1, kind in fixed:
        front = "door" if f1 - f0 < 0.80 - 1e-9 else "doors"
        product = f"{kind} base unit {(f1 - f0) * 100:.0f}x{KITCHEN_BASE_DEPTH_M * 100:.0f} cm"
        # 26 Oct 2026: the hob unit of a full-depth run holds an oven (``oven`` hint), the fridge unit is the
        # under-counter fridge's appliance door; 29 Oct 2026 (K1): with the ovens in the tall unit the hob unit holds
        # pot drawers
        in_column = bool(rule and rule.get("tall_column")) and (oven_tower or bool(hints.get("oven_in_column")))
        if kind == "hob" and hints.get("oven") and not in_column and base_h >= KITCHEN_OVEN_H_M + 0.05:
            front, product = "oven", f"hob with a built-in oven {(f1 - f0) * 100:.0f} cm"
        elif kind == "hob" and in_column:
            front, product = "drawers", f"hob over pot drawers {(f1 - f0) * 100:.0f} cm (the ovens in the tall unit)"
        elif kind == "fridge" and column == (f0, f1):
            to_ceiling = col_top > KITCHEN_COLUMN_TOP_M + 1e-6
            units.append(_module("tall_unit", (f1 - f0, d, col_top - KITCHEN_PLINTH_M),
                                 ((f0 + f1) / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M, front="fridge_column",
                                 holds=kind, product=f"fridge-freezer column {(f1 - f0) * 100:.0f} cm, "
                                                     f"{col_top * 100:.0f} cm high",
                                 **({"column": True} if to_ceiling else {})))
            continue
        elif kind == "fridge":
            front, product = "fridge", f"under-counter fridge {(f1 - f0) * 100:.0f} cm"
        units.append(_module("base_unit", (f1 - f0, d, base_h), ((f0 + f1) / 2.0, 0.0), "front", z_m=KITCHEN_PLINTH_M,
                             front=front, holds=kind, product=product))
    for span in columns:                                  # 29 Oct 2026 (K1): the tall-unit column
        units.append(KD.tall_module(span, d, col_top, KITCHEN_PLINTH_M))
    units.sort(key=lambda m: m["pos_m"][0])
    modules += units
    for x0, x1 in stretches:
        modules.append(_module("worktop", (x1 - x0, d, KITCHEN_WORKTOP_M), ((x0 + x1) / 2.0, 0.0), "worktop",
                               z_m=worktop_z - KITCHEN_WORKTOP_M,
                               cutouts=[{"kind": k, "x_m": round((f0 + f1) / 2.0, 4), "w_m": round(f1 - f0, 4)}
                                        for f0, f1, k in fixed if k != "fridge"
                                        and x0 - 1e-6 <= (f0 + f1) / 2.0 <= x1 + 1e-6]))
    height = worktop_z
    if column is not None or columns:
        height = max(height, col_top)
    # 28 Oct 2026 (module docstring "Kitchen design"): every hob of the run gets its cooker hood above it
    hob_unit = next(((f0, f1) for f0, f1, k in fixed if k == "hob"), None)
    hood = None
    if hob_unit is not None and hints.get("hood") is not False:
        hood = hood_module(hob_unit, d, worktop_z, island, hints)
        notes += KD.island_hood_style(hood, rule, w, d)  # 29 Oct 2026 (K3): the island hood of the family
        modules.append(hood)
        notes.append(hood_note(hood))
    if hints.get("wall_units") and not island:
        # 27 Oct 2026: beside a fridge column the wall units run over the rest of the run only
        wa, wb = (-w / 2.0, w / 2.0) if column is None else \
            ((column[1], w / 2.0) if abs(column[0] + w / 2.0) < 1e-6 else (-w / 2.0, column[0]))
        if columns:                                       # 29 Oct 2026 (K1): nor over the tall-unit column
            c_lo, c_hi = min(c[0] for c in columns), max(c[1] for c in columns)
            wa, wb = (max(wa, c_hi), wb) if abs(c_lo + w / 2.0) < 1e-6 else (wa, min(wb, c_lo))
        # 28 Oct 2026: and never over the hood (the hood between them)
        stretches_w = [(wa, wb)] if hood is None or hood.get("hood") != "chimney" else [
            (a, b) for a, b in ((wa, min(wb, hood["pos_m"][0] - hood["size_m"][0] / 2.0)),
                                (max(wa, hood["pos_m"][0] + hood["size_m"][0] / 2.0), wb)) if b - a > 1e-6]
        for sa, sb in stretches_w:
            wall = compose_run(sb - sa, KITCHEN_WALL_WIDTHS_M, KITCHEN_FILLER_MAX_M)
            if wall is None:
                continue
            xx = sa + wall["filler_m"]
            for uw in wall["widths"]:
                modules.append(_module("wall_unit", (uw, KITCHEN_WALL_DEPTH_M, KITCHEN_WALL_TOP_M - KITCHEN_WALL_BOTTOM_M),
                                       (xx + uw / 2.0, d / 2.0 - KITCHEN_WALL_DEPTH_M / 2.0), "front",
                                       z_m=KITCHEN_WALL_BOTTOM_M, product=f"wall unit {uw * 100:.0f}x"
                                                                          f"{KITCHEN_WALL_DEPTH_M * 100:.0f} cm"))
                xx += uw
            height = KITCHEN_WALL_TOP_M
    products = [m["product"] for m in modules if m.get("product")]
    notes = [f"{len([m for m in modules if m['kind'] == 'base_unit'])} base units, worktop {KITCHEN_WORKTOP_M} m at "
             f"{worktop_z:.2f} m"] + notes
    if not fixed:
        notes.append("no sink or hob cutout: no place given (module_hints); the drawn sink and stove are their own pieces"
                     if not gaps else "no sink or hob cutout: no place given (module_hints)")
    if drawn_h is not None and abs(drawn_h - worktop_z) > 0.01:
        notes.append(f"the drawn height {drawn_h:.2f} m is not a counter height ({KITCHEN_WORKTOP_RANGE_M[0]:.2f}-"
                     f"{KITCHEN_WORKTOP_RANGE_M[1]:.2f} m): worktop at {worktop_z:.2f} m")
    plan = {"builder": "kitchen_run", "type": piece["type"], "modules": modules, "footprint_m": [w, d],
            "height_m": round(height, 4), "drawn_m": [w, d], "fit": _fit_record((w, d), (w, d)),
            "products": sorted(set(products), key=products.index), "island": island,
            "cutouts": [k for _f0, _f1, k in fixed if k != "fridge"], "notes": notes, "design": P.piece_design(piece),
            "worktop_m": round(worktop_z, 4)}           # 28 Oct 2026: the worktop line (the checks read it)
    if rule is not None:
        # 29 Oct 2026 (module docstring "Kitchen details"): what the family's rule gave the run, with the reasons
        blocked = [tuple(b) for b in hints.get("windows_m") or [] if isinstance(b, (list, tuple)) and len(b) == 2]
        rail = KD.rail_span(w, d, fixed + [(c0, c1, "tall") for c0, c1, _k in columns], blocked, rule, island)
        details = {"family": rule["family"], "why": rule["why"], "upper_fronts": rule.get("upper_fronts"),
                   "upper_handleless": bool(rule.get("upper_handleless")), "tap": "pull-down spray tap (K7)",
                   "applied": [], **({"seat_side": hints["seat_side"]} if hints.get("seat_side") else {})}
        for c0, c1, k in columns:
            details["applied"].append({"detail": "K1", "what": k, "x0_m": round(c0, 4), "x1_m": round(c1, 4),
                                       "source": "inferred", "reason": str(column_hint.get("why") or
                                                                           "a tall-unit column at a free run end")})
        if columns or (column is not None and col_top > KITCHEN_COLUMN_TOP_M + 1e-6):
            details["column_top_m"] = col_top
        if hints.get("fridge_why") and any(k == "fridge" for _f0, _f1, k in fixed):
            details["applied"].append({"detail": "K1", "what": "under-counter fridge", "source": "inferred",
                                       "reason": str(hints["fridge_why"])})
        if panels:
            details["waterfall_m"] = [[round(p0, 4), round(p1, 4)] for p0, p1, _k in panels]
            details["applied"].append({"detail": "K2", "what": "waterfall ends", "source": "inferred",
                                       "reason": f"the {rule['family']} family's island has its top down its ends"})
        if over:
            details["overhang_m"] = over["overhang"]
            details["applied"].append({"detail": "G3", "what": "knee space for the stools", "source": "inferred",
                                       "reason": "the stools stand at the island's back"})
        if hood is not None and hood.get("style"):
            details["applied"].append({"detail": "K3", "what": f"{hood['style']} island hood"
                                       + (" in a hanging shelf frame" if hood.get("frame") else ""),
                                       "source": "inferred", "reason": f"the {rule['family']} family's island hood"})
        if rail is not None:
            details["rail_m"] = list(rail)
            details["applied"].append({"detail": "G3", "what": "utensil rail", "source": "inferred",
                                       "reason": f"the {rule['family']} family's utensil rail beside the hob"})
            notes.append(f"a {rail[1] - rail[0]:.2f} m utensil rail with hanging utensils on the splashback beside "
                         "the hob (G3)")
        if rule.get("upper_fronts") or rule.get("upper_handleless"):
            details["applied"].append({"detail": "K4", "what": ("fluted " if rule.get("upper_fronts") == "fluted"
                                                                else "") + ("handle-less " if
                                                                            rule.get("upper_handleless") else "")
                                       + "upper fronts", "source": "inferred",
                                       "reason": f"the {rule['family']} family's wall units"})
        plan["details"] = details
    if hood is not None:
        plan["hood"] = hood_record(hood)
    if gaps:
        plan["gaps"] = gaps
    if built_in is not None:
        (s0, s1), shift, across = built_in
        record = {"id": str(sink_piece), "kind": "sink", "x_m": round((s0 + s1) / 2.0, 4), "w_m": round(s1 - s0, 4),
                  "drawn_x_m": round(float(sink_x), 4), "shift_m": round(shift, 4)}
        if sink_y is not None:                            # part 3: the offset across the run is recorded too
            record.update(drawn_y_m=round(float(sink_y), 4) + 0.0, shift_y_m=round(across, 4) + 0.0)
        plan["built_ins"] = [record]
        notes.append(f"the drawn sink {sink_piece} is built into the run: a {s1 - s0:.2f} m sink unit with the bowl "
                     "and the tap at its cutout" + (f", {abs(shift):.2f} m from the drawn centre (unit width, run end)"
                                                    if abs(shift) > 0.005 else "")
                     + (f"; {sink_across_text(across)}" if abs(across) > 0.005 else ""))
    # 26 Oct 2026: the hob (with its oven) and the under-counter fridge the completion built into the run: their units
    # hold them (``built_ins``: the fit gives the pieces the built-in asset, the scene does not build them again) when
    # the unit stands within KITCHEN_END_SHIFT_MAX_M of the piece's centre
    for kind, key, xv in (("hob", "hob_piece", hob_x), ("fridge", "fridge_piece", fridge_x)):
        pid = hints.get(key)
        if not pid or xv is None:
            continue
        unit = next(((f0, f1) for f0, f1, k in fixed if k == kind), None)
        shift = None if unit is None else (unit[0] + unit[1]) / 2.0 - float(xv)
        if shift is None or abs(shift) > KITCHEN_END_SHIFT_MAX_M + 1e-9:
            notes.append(f"the {kind} {pid} is not built in: " + ("no unit for it" if unit is None else
                                                                  f"its unit would stand {abs(shift):.2f} m off it"))
            continue
        record = {"id": str(pid), "kind": kind, "x_m": round((unit[0] + unit[1]) / 2.0, 4),
                  "w_m": round(unit[1] - unit[0], 4), "drawn_x_m": round(float(xv), 4), "shift_m": round(shift, 4)}
        if kind == "fridge" and column is not None and tuple(unit) == column:
            record["column"] = True
        if kind == "hob":
            record["oven"] = any(m.get("holds") == "hob" and m.get("front") == "oven" for m in modules)
            # 28 Oct 2026: a drawn hob at its drawn span; the hood over it
            if hob_span is not None and tuple(unit) == tuple(hob_span):
                record["drawn_span"] = True
            if hood is not None:
                record["hood"] = hood["hood"]
        plan.setdefault("built_ins", []).append(record)
        what = "hob" if kind == "hob" else ("fridge" if record.get("column") else "under-counter fridge")
        notes.append(f"the {what} {pid} is built into the run: a "
                     f"{unit[1] - unit[0]:.2f} m unit" + (" with the hob plate on the worktop" if kind == "hob" else
                                                          " standing as the fridge-freezer column" if record.get("column")
                                                          else " with an appliance door")
                     + (" and an oven under it" if record.get("oven") else ""))
    # 28 Oct 2026: a counter outline drawn inside the run (an outline drawn twice, a hob or sink block's outline) is
    # part of the run: no second run inside it (``fit.nested_counters``)
    for oid in hints.get("outlines") or []:
        plan.setdefault("built_ins", []).append({"id": str(oid), "kind": "outline"})
        notes.append(f"the counter outline {oid} drawn inside the run is part of it (not a second run)")
    return plan


def drawn_hob_span(w: float, span) -> Optional[tuple[float, float]]:
    """28 Oct 2026: the drawn hob's span ``[x0, x1]`` (the run's frame) clipped to a run of width ``w``, when its width
    is a hob's (``KITCHEN_HOB_SPAN_RANGE_M``), else None (then the nearest real unit width stands at its centre)."""
    try:
        x0, x1 = sorted((float(span[0]), float(span[1])))
    except (TypeError, ValueError, IndexError, KeyError):
        return None
    x0, x1 = max(x0, -w / 2.0), min(x1, w / 2.0)
    lo, hi = KITCHEN_HOB_SPAN_RANGE_M
    if not (lo - 1e-9 <= x1 - x0 <= hi + 1e-9):
        return None
    return (round(x0, 4), round(x1, 4))


def hob_plate_for(unit_w: float) -> float:
    """28 Oct 2026: the width of the real hob plate a hob unit of ``unit_w`` takes (``KITCHEN_HOB_PLATES_M``: the
    widest class at most 2 cm narrower than the unit; the smallest class in a narrower unit)."""
    fits = [p for p in KITCHEN_HOB_PLATES_M if p <= unit_w - 0.02 + 1e-9]
    return max(fits) if fits else min(KITCHEN_HOB_PLATES_M)


def hood_width_for(hob_w: float) -> float:
    """28 Oct 2026: the width of the cooker hood over a hob (unit) of ``hob_w``: the narrowest real hood
    (``HOOD_WIDTHS_M``) at least as wide as the hob (2 cm tolerance), the widest for a wider hob."""
    fits = [h for h in HOOD_WIDTHS_M if h >= hob_w - 0.02 - 1e-9]
    return min(fits) if fits else max(HOOD_WIDTHS_M)


def hood_kind_for(island: bool, hints: dict) -> str:
    """28 Oct 2026: ``island`` over an island (or a run the fit says stands free: ``hood_kind``), ``under_cabinet``
    when a wall cabinet hangs over the hob (the fit's ``hood_kind``: a drawn cabinet over it), else ``chimney``."""
    kind = hints.get("hood_kind")
    if island:
        return "island"
    return kind if kind in HOOD_KINDS else "chimney"


def hood_module(hob_unit: tuple[float, float], d: float, worktop_z: float, island: bool, hints: dict) -> dict:
    """28 Oct 2026 (module docstring "Kitchen design"): the cooker hood module over a hob unit ``(x0, x1)`` of a run
    ``d`` deep with its worktop at ``worktop_z``: ``size_m`` = (width, canopy depth, height from its bottom to the
    chimney's top), ``pos_m`` the canopy's centre (a chimney or under-cabinet hood with its back on the run's back
    edge, ``wall_gap_m`` beyond it; an island hood over the hob), ``z_m`` its bottom, ``hood`` the kind,
    ``chimney_top_m``, ``clear_m`` (bottom over the worktop), ``material`` ``handle`` (the style's metal finish: the
    handles' metal, ``finishes.CABINET_HANDLES``)."""
    x0, x1 = hob_unit
    kind = hood_kind_for(island, hints)
    hw = hood_width_for(x1 - x0)
    hd = min(HOOD_DEPTHS_M[kind], d)
    top = float(hints.get("hood_top_m") or HOOD_TOP_DEFAULT_M)
    if kind == "under_cabinet":
        bottom_cab = float(hints.get("hood_under_m") or KITCHEN_WALL_BOTTOM_M)
        z0 = bottom_cab - HOOD_UNDER_H_M
        size_h = HOOD_UNDER_H_M
        top = bottom_cab
    else:
        z0 = worktop_z + (HOOD_ISLAND_CLEAR_M if kind == "island" else HOOD_CLEAR_M)
        top = max(top, z0 + HOOD_CANOPY_M + 0.20)
        size_h = top - z0
    y = 0.0 if kind == "island" else d / 2.0 + float(hints.get("wall_gap_m") or 0.0) - hd / 2.0
    cls = {"chimney": "chimney hood", "island": "island hood", "under_cabinet": "under-cabinet hood"}[kind]
    return _module("hood", (hw, hd, size_h), ((x0 + x1) / 2.0, y), "handle", z_m=z0, hood=kind,
                   chimney_top_m=round(top, 4), clear_m=round(z0 - worktop_z, 4),
                   product=f"{cls} {hw * 100:.0f} cm")


def hood_record(hood: dict) -> dict:
    """The ``plan["hood"]`` record of a hood module (the checks and the report read it)."""
    rec = {"kind": hood["hood"], "x_m": hood["pos_m"][0], "w_m": hood["size_m"][0], "d_m": hood["size_m"][1],
           "z_m": hood["z_m"], "top_m": hood["chimney_top_m"], "clear_m": hood["clear_m"],
           "product": hood["product"]}
    if hood.get("style"):                             # 29 Oct 2026 (K3): the island hood's style and its shelf frame
        rec["style"] = hood["style"]
    if hood.get("frame"):
        rec["frame"] = dict(hood["frame"])
    return rec


def hood_note(hood: dict) -> str:
    text = (f"a {hood['product']} over the hob, its bottom {hood['clear_m']:.2f} m over the worktop"
            + (f", the chimney up to {hood['chimney_top_m']:.2f} m" if hood["hood"] != "under_cabinet" else
               " under the wall cabinet"))
    if hood["hood"] == "under_cabinet" and hood["clear_m"] < HOOD_UNDER_MIN_CLEAR_M - 1e-9:
        text += f" (only {hood['clear_m']:.2f} m over the hob: the drawn wall cabinet hangs low)"
    return text


def sink_across_text(shift_y: float) -> str:
    """The words for a built-in bowl's offset across the run (fix round after P3, part 3): ``shift_y`` is the bowl's
    local y (0, the run's centreline) minus the drawn sink centre's (front -Y); ``wenart.furniture.fit.built_in_fit``
    and ``fit_report`` say the same from ``built_ins[].shift_y_m``."""
    return (f"the bowl stands {abs(shift_y):.2f} m {'behind' if shift_y > 0 else 'in front of'} the drawn sink centre, "
            "on the run's centreline")


def _sink_off_reason(unit_w: float, shift: float, across: float) -> str:
    """Why a drawn sink is not built in (fix round after P3, parts 2 and 3): its bowl would stand farther than
    ``KITCHEN_END_SHIFT_MAX_M`` from the drawn centre, along the run (unit width, run end) and across it (the bowl on
    the run's centreline)."""
    if abs(across) <= 0.005:
        return (f"its {unit_w:.2f} m sink unit would stand {abs(shift):.2f} m from the drawn centre, more than "
                f"{KITCHEN_END_SHIFT_MAX_M:.2f} m (the drawn sink overhangs the run)")
    return (f"its bowl would stand {math.hypot(shift, across):.2f} m from the drawn centre ({abs(shift):.2f} m along "
            f"the run, at its {unit_w:.2f} m sink unit's centre; {abs(across):.2f} m across it, on the run's "
            f"centreline), more than {KITCHEN_END_SHIFT_MAX_M:.2f} m (the drawn sink lies toward the run's "
            f"{'front' if across > 0 else 'back'} edge)")


def _merge_spans(spans, lo: float, hi: float) -> list[tuple[float, float]]:
    """The spans clipped to ``[lo, hi]``, sorted and merged."""
    out: list[list[float]] = []
    for s in sorted((max(float(a), lo), min(float(b), hi)) for a, b in spans if float(b) > lo and float(a) < hi):
        if s[1] - s[0] <= 1e-6:
            continue
        if out and s[0] <= out[-1][1] + 1e-6:
            out[-1][1] = max(out[-1][1], s[1])
        else:
            out.append([s[0], s[1]])
    return [(a, b) for a, b in out]


def compose_aligned(a: float, b: float, joints: Sequence[float], end_a: str = "open", end_b: str = "open",
                    blind: float = KITCHEN_WALL_DEPTH_M + 0.05) -> dict:
    """28 Oct 2026 (module docstring "Kitchen design"): the wall units of the stretch ``[a, b]`` (pure). Units take
    the real widths ``WALL_RUN_WIDTHS_M`` (a span within ``WALL_RUN_TOL_M`` of one is that unit), side by side with no
    gap; their joints fall on the base joints ``joints`` where they can (a joint elsewhere costs ``0.05``); a hard end
    (``WALL_RUN_HARD_ENDS``: the hood, a wall, another run) is reached (a filler of at most ``WALL_RUN_FILLER_MAX_M``
    closes it), a soft end (a window, a door, an open end) may leave wall free; a ``corner_blind`` end starts with a
    blind corner unit (``blind`` of blind panel and a door of ``WALL_RUN_BLIND_DOOR_M``). A unit made to measure next
    to a hard end is the last resort. Returns ``{"units": [(x0, x1, kind)], "fillers": [(x0, x1)], "free": [(x0, x1)],
    "misaligned": n, "made_to_measure": n}``; no unit when the stretch is shorter than the smallest unit (never a
    lone box of odd width)."""
    tol = WALL_RUN_TOL_M
    widths = WALL_RUN_WIDTHS_M
    hard_a, hard_b = end_a in WALL_RUN_HARD_ENDS, end_b in WALL_RUN_HARD_ENDS
    empty = {"units": [], "fillers": [], "free": [(a, b)] if b - a > 1e-6 else [], "misaligned": 0,
             "made_to_measure": 0}
    if b - a < min(widths) - tol:
        return empty
    inner = sorted({round(float(j), 4) for j in joints if a + 0.02 < float(j) < b - 0.02})
    anchors = [a, b] + inner
    pts = set(round(v, 4) for v in anchors)
    for q in anchors:
        for s in widths:
            for v in (q - s, q + s):
                if a + 1e-6 < v < b - 1e-6:
                    pts.add(round(v, 4))
    if end_a == "corner_blind":
        for s in (blind + WALL_RUN_BLIND_DOOR_M[0], blind + WALL_RUN_BLIND_DOOR_M[1]):
            pts.add(round(min(b, a + s), 4))
    if end_b == "corner_blind":
        for s in (blind + WALL_RUN_BLIND_DOOR_M[0], blind + WALL_RUN_BLIND_DOOR_M[1]):
            pts.add(round(max(a, b - s), 4))
    pts = sorted(pts)
    aligned = [a, b] + inner

    def on_joint(v: float) -> bool:
        return any(abs(v - j) <= 0.01 for j in aligned)

    def unit_kind(x0: float, x1: float, first: bool, last: bool) -> Optional[tuple[str, float]]:
        span = x1 - x0
        if first and end_a == "corner_blind" and abs(x0 - a) < 1e-6:
            ok = blind + WALL_RUN_BLIND_DOOR_M[0] - tol <= span <= blind + WALL_RUN_BLIND_DOOR_M[1] + tol
            return ("corner_blind", 0.0) if ok else None
        if last and end_b == "corner_blind" and abs(x1 - b) < 1e-6:
            ok = blind + WALL_RUN_BLIND_DOOR_M[0] - tol <= span <= blind + WALL_RUN_BLIND_DOOR_M[1] + tol
            return ("corner_blind", 0.0) if ok else None
        if any(abs(span - s) <= tol for s in widths):
            return ("unit", 0.0)
        hard_next = (first and hard_a and x0 - a <= WALL_RUN_FILLER_MAX_M + 1e-6) or \
            (last and hard_b and b - x1 <= WALL_RUN_FILLER_MAX_M + 1e-6)
        if hard_next and min(widths) - tol <= span <= max(widths) + tol:
            return ("made_to_measure", 0.5)
        return None

    # one forward pass: dp[i] = (cost, start, path) of the best run ending at pts[i]; a start costs the wall it leaves
    # free (soft end, x2 per metre) or the filler it needs (hard end, at most WALL_RUN_FILLER_MAX_M, x1 per metre)
    longest = max(max(widths), blind + WALL_RUN_BLIND_DOOR_M[1]) + tol
    dp: dict[int, tuple[float, float, list]] = {}
    for i, p in enumerate(pts):
        if hard_a and p - a > WALL_RUN_FILLER_MAX_M + 1e-6:
            break
        if end_a == "corner_blind" and abs(p - a) > 1e-6:
            continue
        dp[i] = ((p - a) * (1.0 if hard_a else 2.0), p, [])
    best_total = None
    for i in range(len(pts)):
        if i not in dp:
            continue
        cost_i, start_i, path_i = dp[i]
        for j in range(i + 1, len(pts)):
            x0, x1 = pts[i], pts[j]
            if x1 - x0 > longest:
                break
            may_end = not hard_b or b - x1 <= WALL_RUN_FILLER_MAX_M + 1e-6
            got = unit_kind(x0, x1, not path_i, may_end)
            if got is None:
                continue
            kind, extra = got
            cost = cost_i + 0.01 + extra + (0.05 if path_i and not on_joint(x0) else 0.0)
            if j not in dp or cost < dp[j][0] - 1e-9:
                dp[j] = (cost, start_i, path_i + [(x0, x1, kind)])
        if path_i:
            e = pts[i]
            if (hard_b and b - e > WALL_RUN_FILLER_MAX_M + 1e-6) or (
                    end_b == "corner_blind" and path_i[-1][2] != "corner_blind"):
                continue
            total = cost_i + (b - e) * (1.0 if hard_b else 2.0)
            if best_total is None or total < best_total[0] - 1e-9:
                best_total = (total, start_i, e, path_i)
    if best_total is None:
        return empty
    _t, s, e, path = best_total
    fillers, free = [], []
    for (x0, x1), hard in (((a, s), hard_a), ((e, b), hard_b)):
        if x1 - x0 > 1e-4:
            (fillers if hard else free).append((round(x0, 4), round(x1, 4)))
    units = [(round(x0, 4), round(x1, 4), k) for x0, x1, k in path]
    misaligned = sum(1 for x0, _x1, _k in units[1:] if not on_joint(x0))
    return {"units": units, "fillers": fillers, "free": free, "misaligned": misaligned,
            "made_to_measure": sum(1 for u in units if u[2] == "made_to_measure")}


def plan_wall_run(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """28 Oct 2026 (module docstring "Kitchen design"; user on real04: the wall cabinets "hang as separate boxes of
    odd widths with gaps and do not line up with the base units or each other"): a wall cabinet the completion hung
    (one stretch of a wall run, ``rule.ends``) built of real wall units (``compose_aligned``): one carcass depth, one
    bottom and top line (the piece's height from its mount), joints on the base joints the fit gives
    (``module_hints["joints_m"]``, the wall cabinet's frame), a blind corner unit at a ``corner_blind`` end, fillers
    at hard ends, the build's window and glazed-door spans left free (``module_hints["blocked_m"]``). None when no
    unit fits (never a lone box of odd width)."""
    w, d, h = _piece_size(piece)
    if w < min(WALL_RUN_WIDTHS_M) - WALL_RUN_TOL_M or not (0.25 <= d <= 0.65) or h <= 0.2:
        return None
    hints = _hints(piece)
    rule = piece.get("rule") if isinstance(piece.get("rule"), dict) else {}
    ends = list(hints.get("ends") or rule.get("ends") or ["open", "open"])[:2]
    ends += ["open"] * (2 - len(ends))
    joints = [float(j) for j in hints.get("joints_m") or []]
    blind = float(hints.get("blind_m") or (KITCHEN_WALL_DEPTH_M + 0.05))
    blocked = _merge_spans(hints.get("blocked_m") or [], -w / 2.0, w / 2.0)
    stretches, x = [], -w / 2.0
    kind_a = ends[0]
    for b0, b1 in blocked:
        if b0 - x > 1e-6:
            stretches.append((x, b0, kind_a, "window"))
        x, kind_a = b1, "window"
    if w / 2.0 - x > 1e-6:
        stretches.append((x, w / 2.0, kind_a, ends[1]))
    modules, products, notes = [], [], []
    free: list = []
    misaligned = made = 0
    for a, b, ka, kb in stretches:
        comp = compose_aligned(a, b, joints, ka, kb, blind)
        free += comp["free"]
        misaligned += comp["misaligned"]
        made += comp["made_to_measure"]
        for x0, x1 in comp["fillers"]:
            modules.append(_module("filler", (x1 - x0, d, h), ((x0 + x1) / 2.0, 0.0), "front", z_m=0.0))
        for x0, x1, kind in comp["units"]:
            uw = x1 - x0
            if kind == "corner_blind":
                side = "left" if ka == "corner_blind" and abs(x0 - a) < 1e-6 else "right"
                product = f"blind corner wall unit {uw * 100:.0f}x{d * 100:.0f} cm"
                modules.append(_module("wall_unit", (uw, d, h), ((x0 + x1) / 2.0, 0.0), "front", z_m=0.0,
                                       corner="blind", blind_m=round(min(blind, uw - 0.25), 4), blind_side=side,
                                       product=product))
            else:
                product = f"wall unit {uw * 100:.0f}x{d * 100:.0f} cm" + (
                    " (made to measure)" if kind == "made_to_measure" else "")
                modules.append(_module("wall_unit", (uw, d, h), ((x0 + x1) / 2.0, 0.0), "front", z_m=0.0,
                                       doors=1 if uw < 0.60 - 1e-9 else 2, product=product))
            products.append(product)
    if not any(m["kind"] == "wall_unit" for m in modules):
        return None
    modules.sort(key=lambda m: m["pos_m"][0])
    units = [m for m in modules if m["kind"] == "wall_unit"]
    sizes = " + ".join("%.2f" % m["size_m"][0] for m in units)
    notes.append(f"{len(units)} wall unit(s) {sizes} m, {d:.2f} m deep, {h:.2f} m high; ends: {ends[0]} / {ends[1]}")
    if blocked:
        notes.append("left free at the window or glazed door of the wall (the building as built): "
                     + ", ".join(f"{b0:+.2f}..{b1:+.2f} m" for b0, b1 in blocked))
    if misaligned:
        notes.append(f"{misaligned} joint(s) off the base units' joints (no real width fits there)")
    if made:
        notes.append(f"{made} unit(s) made to measure next to a hard end")
    plan = {"builder": "wall_run", "type": piece["type"], "modules": modules, "footprint_m": [w, d],
            "height_m": round(h, 4), "drawn_m": [w, d], "fit": _fit_record((w, d), (w, d)),
            "products": sorted(set(products), key=products.index), "notes": notes, "design": P.piece_design(piece),
            "ends": ends, "units_m": [round(m["size_m"][0], 4) for m in units],
            "free_m": [[round(x0, 4), round(x1, 4)] for x0, x1 in free], "misaligned": misaligned,
            "made_to_measure": made, **({"blocked_m": [list(s) for s in blocked]} if blocked else {})}
    # 29 Oct 2026 (K4, module docstring "Kitchen details"): the family's uppers (fluted, handle-less)
    family = KD.family_from(style, hints, plan["design"])
    if family is not None:
        rule = KD.family_rule(family)
        plan["details"] = {"family": rule["family"], "upper_fronts": rule.get("upper_fronts"),
                           "upper_handleless": bool(rule.get("upper_handleless")), "applied": []}
        if rule.get("upper_fronts") or rule.get("upper_handleless"):
            what = (("fluted " if rule.get("upper_fronts") == "fluted" else "")
                    + ("handle-less " if rule.get("upper_handleless") else "") + "fronts")
            plan["details"]["applied"].append({"detail": "K4", "what": what, "source": "inferred",
                                               "reason": f"the {rule['family']} family's wall units"})
            notes.append(f"{what} (the {rule['family']} family's uppers; K4)")
    return plan


def _wall_run_parts(plan: dict) -> list[Part]:
    """28 Oct 2026: the parts of a wall run (``plan_wall_run``): per unit a carcass and its doors (handles low, on
    feet), a blind corner unit's blind panel on its corner side, fillers in the front colour."""
    design = plan.get("design") or {}
    parts: list[Part] = []
    inset = P.FRONT_GAP + P.FRONT_THICKNESS
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        face = y - d / 2.0 + inset
        if m["kind"] == "filler":
            parts.append(P._box(x, y + inset / 2.0, z0, w - 0.001, d - inset, h, "painted", "body"))
            parts += P._front_panel(x, face, z0 + 0.003, w - 0.002, h - 0.006, "flat")
            continue
        if m["kind"] != "wall_unit":
            continue
        parts.append(P._box(x, y + inset / 2.0, z0, w - 0.002, d - inset, h, "painted", "body"))
        if m.get("corner") == "blind":
            bw = float(m.get("blind_m") or 0.0)
            sign = -1.0 if m.get("blind_side") == "left" else 1.0
            bx = x + sign * (w / 2.0 - bw / 2.0)
            parts += P._front_panel(bx, face, z0 + 0.003, bw - 0.003, h - 0.006, "flat")
            dw = w - bw
            dx = x - sign * (w / 2.0 - dw / 2.0)
            fronts = P.cabinet_fronts(dw - 0.004, face, z0 + 0.003, z0 + h - 0.003, 1, 1, design, handle_at="bottom")
            parts += _rotate_parts(fronts, dx, 0.0, 0.0)
            continue
        doors = int(m.get("doors") or 1)
        # 29 Oct 2026 (K4): the family's fluted or handle-less uppers
        fronts = KD.upper_front_parts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, doors, design,
                                      plan.get("details")) \
            or P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 1, doors, design, handle_at="bottom")
        parts += _rotate_parts(fronts, x, 0.0, 0.0)
    return with_handle_posts(parts)


def wall_unit_blocks(piece: dict, building: dict, margin: float = WALL_RUN_WINDOW_MARGIN_M) -> list[dict]:
    """28 Oct 2026 (user on real06: "Why is this closing the window"; the architect moved a window into the wall
    behind two wall cabinets at build time): the windows and glazed doors of the building as built that a wall-hung
    cabinet would cover (pure, no geometry library: it runs inside Blender): every window, and every door with glass
    (``glazed``, a glazed operation or door style), of the piece's level whose wall line lies behind the cabinet
    (within its depth plus half the wall's thickness and 0.15 m), whose height range meets the cabinet's and whose
    width meets its span. ``[{"id", "x0_m", "x1_m"}]``: the opening's span in the cabinet's frame, widened by
    ``margin`` on each side."""
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else None
    if not fp or not fp.get("center") or not fp.get("size"):
        return []
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    w, d = float(fp["size"][0]), float(fp["size"][1])
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    cr, sr = math.cos(rot), math.sin(rot)
    try:
        from wenart.blender.proxies import mount_bottom
        z0 = float(mount_bottom(piece)[0])
    except Exception:  # noqa: BLE001 - the rule's bottom
        z0 = 1.45
    h = float(piece.get("height") or 0.7)
    walls = {x.get("id"): x for x in building.get("walls") or []}
    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != piece.get("level_id") or o.get("build") is False or not o.get("center"):
            continue
        glazed = o.get("type") == "window" or (o.get("type") == "door" and (
            o.get("glazed") or "glass" in str(o.get("door_style") or "") or o.get("operation") in (
                "sliding_glass", "french", "glazed")))
        if not glazed:
            continue
        wall = walls.get(o.get("wall_id"))
        if wall is None:
            continue
        (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-6:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        sill = float(o.get("sill_height") or 0.0) if o.get("type") == "window" else 0.0
        head = sill + float(o.get("height") or 2.1)
        if head <= z0 + 1e-3 or sill >= z0 + h - 1e-3:
            continue
        ox, oy = float(o["center"][0]), float(o["center"][1])
        half = float(o.get("width") or 0.9) / 2.0
        ends = [(ox - ux * half, oy - uy * half), (ox + ux * half, oy + uy * half)]
        local = [(cr * (px - cx) + sr * (py - cy), -sr * (px - cx) + cr * (py - cy)) for px, py in ends]
        thick = float(wall.get("thickness") or 0.2)
        if any(abs(ly) > d / 2.0 + thick / 2.0 + 0.15 or ly < -d / 2.0 + 1e-3 for _lx, ly in local):
            continue                                         # not in the wall behind the cabinet
        if abs(local[0][1] - local[1][1]) > 0.05:
            continue                                         # a wall across the cabinet, not behind it
        lo, hi = sorted((local[0][0], local[1][0]))
        lo, hi = lo - margin, hi + margin
        if hi <= -w / 2.0 or lo >= w / 2.0:
            continue
        out.append({"id": o.get("id"), "x0_m": round(lo, 4), "x1_m": round(hi, 4)})
    return out


def worktop_item_window(item: dict, host: dict, building: dict) -> Optional[str]:
    """28 Oct 2026: the window, glazed door or pass-through of the building as built that a kitchen worktop item
    (``decor.KITCHEN_DECOR_TYPES``) would stand in front of and reach (its top over the opening's sill), else None
    (pure: the build skips such an item; the architect may add or move a window after the decor stage)."""
    try:
        h = float(item["size"][2]) if len(item.get("size") or []) > 2 else 0.25
        top_z = float(host.get("height") or KITCHEN_WORKTOP_HEIGHT_M)
        if not (KITCHEN_WORKTOP_RANGE_M[0] <= top_z <= KITCHEN_WORKTOP_RANGE_M[1]):
            top_z = KITCHEN_WORKTOP_HEIGHT_M
        rot = float(item.get("rotation_deg") if item.get("rotation_deg") is not None else
                    host["footprint"].get("rotation_deg") or 0.0)
        probe = {"type": "wall_cabinet", "level_id": item.get("level_id") or host.get("level_id"),
                 "mount_bottom_m": top_z + 0.005, "height": max(h - 0.01, 0.005),
                 "footprint": {"center": list(item["center"][:2]),
                               "size": [float(item["size"][0]), float(item["size"][1])], "rotation_deg": rot}}
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    openings = [dict(o, type="window", sill_height=o.get("sill_height") or 0.0)
                if o.get("type") == "opening" else o for o in building.get("openings") or []]
    blocks = wall_unit_blocks(probe, dict(building, openings=openings), margin=0.0)
    return str(blocks[0]["id"]) if blocks else None


WORKTOP_SLIDE_STEP_M = 0.05
WORKTOP_HOB_CLEAR_M = 0.25           # = decor.WORKTOP_HOB_CLEAR_M (Blender's Python has no shapely: no import)
WORKTOP_SINK_CLEAR_M = 0.10          # = decor.WORKTOP_SINK_CLEAR_M
WORKTOP_ITEM_GAP_M = 0.10            # = decor.WORKTOP_ITEM_GAP_M


def slide_worktop_item(item: dict, host: dict, building: dict, taken: Sequence[dict] = ()) -> Optional[dict]:
    """28 Oct 2026: a worktop item the building as built puts in front of a window (``worktop_item_window``) slid
    along its host run to the nearest spot (``WORKTOP_SLIDE_STEP_M`` steps, its depth kept) that is off the hob and
    the sink of the run's plan (with their side gaps), off its tall units and gaps, off the other items ``taken``
    and in front of no window; None when no spot is left (pure: the build calls it)."""
    fp = host.get("footprint") or {}
    try:
        c = (float(fp["center"][0]), float(fp["center"][1]))
        rot = math.radians(float(fp.get("rotation_deg") or 0.0))
        w = float(fp["size"][0])
        iw = float(item["size"][0])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    plan = ((host.get("asset") or {}).get("module_plan") or {}) if isinstance(host.get("asset"), dict) else {}
    blocked: list[tuple[float, float]] = []
    for m in plan.get("modules") or []:
        if m.get("kind") == "worktop":
            for cut in m.get("cutouts") or []:
                clear = WORKTOP_HOB_CLEAR_M if cut.get("kind") == "hob" else WORKTOP_SINK_CLEAR_M
                x, cw = float(cut.get("x_m") or 0.0), float(cut.get("w_m") or 0.0)
                blocked.append((x - cw / 2.0 - clear, x + cw / 2.0 + clear))
        elif m.get("kind") == "tall_unit":
            blocked.append((float(m["pos_m"][0]) - float(m["size_m"][0]) / 2.0,
                            float(m["pos_m"][0]) + float(m["size_m"][0]) / 2.0))
    for g in plan.get("gaps") or []:
        blocked.append((float(g["x_m"]) - float(g["w_m"]) / 2.0, float(g["x_m"]) + float(g["w_m"]) / 2.0))

    def local(p):
        dx, dy = float(p[0]) - c[0], float(p[1]) - c[1]
        return math.cos(rot) * dx + math.sin(rot) * dy, -math.sin(rot) * dx + math.cos(rot) * dy

    for o in taken:
        if o is item or o.get("host_id") != host.get("id"):
            continue
        ox, _oy = local(o["center"])
        half = float(o["size"][0]) / 2.0 + WORKTOP_ITEM_GAP_M
        blocked.append((ox - half, ox + half))
    lx, ly = local(item["center"])
    lo, hi = -w / 2.0 + iw / 2.0 + 0.05, w / 2.0 - iw / 2.0 - 0.05
    n = int(max(0.0, hi - lo) / WORKTOP_SLIDE_STEP_M + 1e-6)
    xs = sorted({round(lo + k * WORKTOP_SLIDE_STEP_M, 4) for k in range(n + 1)} | {round(hi, 4)},
                key=lambda x: (abs(x - lx), x))
    for x in xs:
        if any(x - iw / 2.0 < b1 - 1e-6 and x + iw / 2.0 > b0 + 1e-6 for b0, b1 in blocked):
            continue
        wx, wy = c[0] + math.cos(rot) * x - math.sin(rot) * ly, c[1] + math.sin(rot) * x + math.cos(rot) * ly
        trial = dict(item, center=[round(wx, 4), round(wy, 4)])
        trial.pop("host_frame", None)
        if worktop_item_window(trial, host, building) is None:
            return trial
    return None


def clear_windows(piece: dict, building: dict) -> tuple[Optional[dict], Optional[dict]]:
    """28 Oct 2026 (user on real06: "Why is this closing the window"): a wall cabinet against the building as built
    (pure; the scene builder calls it before it builds the cabinet): ``(piece, record)``. No window or glazed door of
    its wall under it (``wall_unit_blocks``): the piece as it is and None. Else the piece re-planned as a wall run with
    those spans left free (``module_hints["blocked_m"]``, ``asset.method: module``; the record names the openings and
    the units left) or, when no wall unit fits beside them, ``(None, record)``: the cabinet is not built (never a
    cabinet over a window)."""
    if piece.get("type") != "wall_cabinet" or not isinstance(building, dict):
        return piece, None
    blocks = wall_unit_blocks(piece, building)
    if not blocks:
        return piece, None
    asset = dict(piece.get("asset") or {})
    hints = dict(asset.get("module_hints") or {})
    hints["blocked_m"] = [[b["x0_m"], b["x1_m"]] for b in blocks] + list(hints.get("blocked_m") or [])
    plan = module_plan(dict(piece, module_hints=hints))
    ids = sorted({str(b["id"]) for b in blocks})
    if plan is None:
        return None, {"id": piece.get("id"), "windows": ids, "built": False,
                      "reason": f"it would cover {', '.join(ids)} of the building as built (a window or glazed door "
                                "of its wall) and no wall unit fits beside it: not built"}
    asset.update(method=MODULE_METHOD, module_plan=plan, module_hints=hints,
                 asset_id=asset.get("asset_id") if str(asset.get("asset_id") or "").startswith("module:")
                 else f"module:{piece['type']}:wall_run")
    return dict(piece, asset=asset), {"id": piece.get("id"), "windows": ids, "built": True,
                                      "units_m": plan.get("units_m"),
                                      "reason": f"cut at {', '.join(ids)} of the building as built: the wall units "
                                                "stand beside the window, never over it"}


def plan_bath_set(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """A vanity with basin(s) and a mirror (washbasin at least 0.45 m deep) or a shower tray with its screen."""
    w, d, h = _piece_size(piece)
    ftype = piece.get("type")
    if ftype == "shower":
        tray = nearest_tray(w, d)
        if tray is None:
            return None
        tw, td = tray
        fit = _fit_record((w, d), (tw, td))
        if not fit["within_cap"]:
            return None
        modules = [_module("tray", (tw, td, P.SHOWER_TRAY_M), (0.0, 0.0), "ceramic", product=f"shower tray {tw * 100:.0f}x{td * 100:.0f} cm"),
                   _module("screen", (tw, td, h - P.SHOWER_TRAY_M), (0.0, 0.0), "glass", z_m=P.SHOWER_TRAY_M)]
        return {"builder": "bath_set", "type": ftype, "modules": modules, "footprint_m": [tw, td], "height_m": round(h, 4),
                "drawn_m": [w, d], "fit": fit, "products": [modules[0]["product"], "glass screen with a door, shower set"],
                "notes": [f"tray {tw:.2f} x {td:.2f} m (size table product nearest the drawn {w:.2f} x {d:.2f} m)"],
                "design": P.piece_design(piece)}
    if ftype != "washbasin":
        return None
    if d < VANITY_DEPTH_RANGE_M[0] - 1e-9 or not (VANITY_WIDTH_RANGE_M[0] - 1e-9 <= w <= VANITY_WIDTH_RANGE_M[1] + 1e-9):
        return None
    cab_d = min(d, VANITY_DEPTH_RANGE_M[1])
    fit = _fit_record((w, d), (w, cab_d))
    if not fit["within_cap"]:
        return None
    basins = 2 if w >= VANITY_DOUBLE_FROM_M - 1e-9 else 1
    top_t = 0.03
    cab_h = h - top_t - VANITY_BOTTOM_M
    if cab_h < VANITY_CABINET_MIN_H_M - 1e-9:
        return None
    modules = [_module("vanity", (w, cab_d, cab_h), (0.0, 0.0), "front", z_m=VANITY_BOTTOM_M,
                       drawers=2 if cab_h >= 0.40 else 1, product=f"vanity unit {w * 100:.0f}x{cab_d * 100:.0f} cm"),
               _module("top", (w, cab_d, top_t), (0.0, 0.0), "ceramic", z_m=h - top_t, basins=basins)]
    for k in range(basins):
        bx = 0.0 if basins == 1 else (-1 if k == 0 else 1) * w / 4.0
        bw = min(BASIN_M[0], w / basins - 0.12)
        modules.append(_module("basin", (bw, min(BASIN_M[1], cab_d - 0.12), BASIN_M[2]), (bx, 0.0), "ceramic",
                               z_m=h - BASIN_M[2]))
    mirror_bottom = max(VANITY_MIRROR_BOTTOM_MIN_M, h + 0.25)
    modules.append(_module("mirror", (w - 0.10, VANITY_MIRROR_DEPTH_M, VANITY_MIRROR_H_M),
                           (0.0, cab_d / 2.0 - VANITY_MIRROR_DEPTH_M / 2.0), "mirror", z_m=mirror_bottom))
    products = [modules[0]["product"], f"{basins} inset basin(s) with taps", f"framed mirror {w - 0.10:.2f} x {VANITY_MIRROR_H_M:.2f} m"]
    notes = [f"wall-hung vanity, {basins} basin(s)" + (" (double vanity from 1.10 m, assumed)" if basins == 2 else "")]
    return {"builder": "bath_set", "type": ftype, "modules": modules, "footprint_m": [w, cab_d],
            "height_m": round(mirror_bottom + VANITY_MIRROR_H_M, 4), "drawn_m": [w, d], "fit": fit, "products": products,
            "basins": basins, "notes": notes, "design": P.piece_design(piece)}


def nearest_tray(w: float, d: float) -> Optional[tuple[float, float]]:
    """The shower tray product nearest the drawn size (either orientation of the drawn box is tried, the tray's
    width stays along the piece's front)."""
    best = None
    for tw, td in SHOWER_TRAYS_M:
        for a, b in ((tw, td), (td, tw)):
            err = max(abs(a - w) / w, abs(b - d) / d)
            if best is None or err < best[0]:
                best = (err, (a, b))
    return None if best is None else best[1]


_PLANNERS = {"wardrobe_run": plan_wardrobe_run, "table_long": plan_table_long, "sofa_l": plan_sofa_l,
             "kitchen_run": plan_kitchen_run, "bath_set": plan_bath_set, "wall_run": plan_wall_run}


def gap_types() -> list[str]:
    """The furniture types built below the library level by neither a module builder nor a v2 family (the
    report's gap list, docs/milestone13.md §13.1 T2): every parametric type minus ``MODULE_BUILDERS`` and
    ``parametric.FAMILY_TYPES``. They keep their Milestone 4-12 builders (the by-design fixtures of
    ``catalog.BY_DESIGN_PARAMETRIC_TYPES`` among them)."""
    return sorted(t for t in P.PARAMETRIC_TYPES if t not in MODULE_BUILDERS and t not in P.FAMILY_TYPES)


def module_plan(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """The module plan of a drawn piece (docs/milestone13.md §13.2; pure): ``{builder, modules: [{kind, size_m:
    [w, d, h], pos_m: [x, y], rot_deg, material}], footprint_m, height_m, products}`` plus ``drawn_m``, ``fit``
    (the deviation from the drawn footprint, ``within_cap`` at ``MODULE_FIT_TOL``), ``notes`` and the builder's own
    records (``split`` of a table with chairs, ``cutouts`` of a kitchen run, ``chaise_side`` of an L sofa). None
    when the type has no builder (``MODULE_BUILDERS``), the piece has no usable footprint, or the modules cannot
    match the drawn footprint within the cap (then the parametric family builds it)."""
    fp = piece.get("footprint") if isinstance(piece, dict) else None
    builder = MODULE_BUILDERS.get(str((piece or {}).get("type")))
    if builder is None and isinstance(piece, dict) and piece.get("type") == "sofa" \
            and str(piece.get("shape") or "").upper() == "L":
        builder = "sofa_l"                        # a sofa drawn as an L (shape: L) is built like a corner sofa
    if builder is None or not isinstance(fp, dict) or len(fp.get("size") or []) < 2:
        return None
    try:
        w, d = float(fp["size"][0]), float(fp["size"][1])
    except (TypeError, ValueError):
        return None
    if not (w > 0 and d > 0):
        return None
    plan = _PLANNERS[builder](piece, style)
    if plan is None or not plan.get("fit", {}).get("within_cap", True):
        return None
    plan["method"] = MODULE_METHOD
    return plan


# --------------------------------------------------------------------------
# Parts (pure) from a plan
# --------------------------------------------------------------------------

def _rotate_parts(parts: list[Part], dx: float, dy: float, rot_deg: float) -> list[Part]:
    """Parts turned about Z by ``rot_deg`` and moved by ``(dx, dy)`` in the piece frame."""
    rad = math.radians(rot_deg)
    c, s = math.cos(rad), math.sin(rad)
    out = []
    for p in parts:
        verts = [(dx + c * x - s * y, dy + s * x + c * y, z) for x, y, z in p["verts"]]
        out.append(dict(p, verts=verts))
    return out


def _frame_parts(m: dict, design: dict, frame_top: float) -> list[Part]:
    """One wardrobe frame: a carcass box with its door(s) in the design's front style and vertical handles."""
    w, d, _h = m["size_m"]
    x, _y = m["pos_m"]
    z0 = float(m.get("z_m") or 0.0)
    inset = P.FRONT_GAP + P.FRONT_THICKNESS
    parts = [P._box(x, inset / 2.0, z0, w - 0.002, d - inset, frame_top - z0, "wood", "body")]
    face = -d / 2.0 + inset
    doors = int(m.get("doors") or 1)
    style = P.front_style_of(design)
    gap = 0.003
    dw = (w - gap * (doors + 1)) / doors
    for k in range(doors):
        cx = x - w / 2.0 + gap + dw / 2.0 + k * (dw + gap)
        parts += P._front_panel(cx, face, z0 + gap, dw, frame_top - z0 - 2 * gap, style)
        # the handle near the opening edge: a pair of doors opens in the middle, a single door on its hinge's far side
        if doors == 2:
            hx = cx + (dw / 2.0 - 0.05) * (1.0 if k == 0 else -1.0)
        else:
            hx = cx + (dw / 2.0 - 0.05) * (1.0 if m.get("hinge") == "left" else -1.0)
        parts.append(P._handle(hx, face, z0 + (frame_top - z0) * 0.5, vertical=True))
    return parts


def _wardrobe_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    parts: list[Part] = []
    top_z = plan["height_m"] - WARDROBE_TOP_M
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "plinth":
            parts.append(P._box(x, y, 0.0, w, d, h, "dark", "plinth"))
        elif m["kind"] == "frame":
            parts += _frame_parts(m, design, top_z)
        elif m["kind"] == "filler":
            parts.append(P._box(x, 0.0, z0, w, d, top_z - z0, "front", "front"))
        elif m["kind"] == "top":
            parts.append(P._box(x, y, z0, w, d, h, "wood", "top"))
    return parts


def _table_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    tags = design.get("material_tags") or ()
    top_key = next((P.TOP_TAG_KEYS[t] for t in tags if t in P.TOP_TAG_KEYS), "wood")
    leg_key = "steel" if "metal" in tags else "wood"
    parts: list[Part] = []
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "top":
            parts.append(P._box(x, y, z0, w, d, h, top_key, "top"))
            # an apron under the top for legged tables (slab-legged trestle tables take a stretcher instead);
            # FRONT_GAP (1 mm) under the top: no two parts share a face plane
            if m.get("support") == "legs":
                a = 0.08 - P.FRONT_GAP
                for sy in (-1, 1):
                    parts.append(P._box(x, y + sy * (d / 2.0 - 0.09), z0 - 0.08, w - 0.24, 0.03, a, leg_key, "apron"))
                for sx in (-1, 1):
                    parts.append(P._box(x + sx * (w / 2.0 - 0.09), y, z0 - 0.08, 0.03, d - 0.24, a, leg_key, "apron"))
            else:
                parts.append(P._box(x, y, z0 - 0.16, w - 1.0, 0.06, 0.10, leg_key, "stretcher"))
        elif m["kind"] == "leg":
            foot = 0.015
            parts.append(P._box(x, y, 0.0, w, d, foot, "steel", "foot"))
            parts.append(P._frustum_z(x, y, foot + P.FRONT_GAP, w * 0.35, d * 0.35, w / 2.0, d / 2.0,
                                      h - foot - 2 * P.FRONT_GAP, leg_key, "leg", n=16))
        elif m["kind"] == "trestle":
            foot = P.TABLE_FOOT_M
            parts.append(P._box(x, y, 0.0, w + 0.02, d, foot, "steel", "foot"))          # adjustable steel feet
            parts.append(P._box(x, y, foot + P.FRONT_GAP, w, d, h - foot - 2 * P.FRONT_GAP, leg_key, "trestle"))
        elif m["kind"] == "chair":
            chair = P.build_parts("chair", w, d, h)
            parts += _rotate_parts(chair, x, y, m["rot_deg"])
    return parts


def _cushion(cx: float, cy: float, z0: float, w: float, d: float, t: float, role: str = "cushion",
             tilt: float = 0.0) -> Part:
    return P._superellipsoid(cx, cy, z0, w, d, t, 0.25, 0.22, "fabric", role, n_eta=10, n_om=32, tilt_deg=tilt)


def _sofa_l_parts(plan: dict) -> list[Part]:
    h = plan["height_m"]
    seat_h = P.sofa_seat_height(h)
    parts: list[Part] = []
    leg = SOFA_LEG_M
    for m in plan["modules"]:
        w, d, mh = m["size_m"]
        x, y = m["pos_m"]
        if m["kind"] == "back":
            parts.append(P._box(x, y, leg, w, d, h - leg - 0.10, "fabric", "back"))
        elif m["kind"] == "arm":
            parts.append(P._box(x, y, leg, w, d, mh - leg, "fabric", "arm"))
        elif m["kind"] in ("seat_module", "chaise_module"):
            parts.append(P._box(x, y, leg, w, d, seat_h - SOFA_CUSHION_M - leg, "fabric", "body"))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    parts.append(P._frustum_z(x + sx * (w / 2.0 - 0.06), y + sy * (d / 2.0 - 0.06), 0.0, 0.02, 0.02,
                                              0.03, 0.03, leg - P.FRONT_GAP, "wood", "leg", n=12))
            parts.append(_cushion(x, y, seat_h - SOFA_CUSHION_M, w - 0.02, d - 0.03, SOFA_CUSHION_M))
            # the leaning back cushion's box turns with it: its height is chosen so the top meets h exactly
            lean = math.radians(P.BACK_CUSHION_LEAN_DEG)
            bt = P.BACK_CUSHION_T_M
            bh = max(0.10, (h - seat_h + 0.02 - bt * math.sin(lean)) / math.cos(lean))
            parts.append(_cushion(x, y + d / 2.0 - bt / 2.0 + 0.01, seat_h - 0.02, w - 0.04, bt, bh, "back_cushion",
                                  tilt=-P.BACK_CUSHION_LEAN_DEG))
    return parts


def _base_unit_parts(m: dict, design: dict, d_run: float) -> list[Part]:
    """One kitchen base unit: carcass, fronts (door, pair of doors or three drawers) with handles. Fix round after
    P3, part 2 (17 Oct 2026): the carcass of the sink unit (``holds: sink``) is hollow above the bowl's bottom
    (``parametric.open_carcass``: side and back boards up to the worktop); its solid body had filled the lower 14 cm
    of the bowl, which rendered as a 4 cm tray with a cabinet-paint floor."""
    w, d, h = m["size_m"]
    x, y = m["pos_m"]
    z0 = float(m.get("z_m") or 0.0)
    # 29 Oct 2026 (G3): the unit's own depth and centre across the run (an island's knee space behind its carcass);
    # a unit of the run's full depth on its centreline is the unit of before
    dc, yc = (float(d), float(y)) if abs(float(d) - float(d_run)) > 1e-6 or abs(float(y)) > 1e-6 else (d_run, 0.0)
    inset = P.FRONT_GAP + P.FRONT_THICKNESS + 0.015          # the worktop overhangs the fronts by 15 mm
    face = yc - dc / 2.0 + inset
    if m.get("holds") == "sink":
        # the bowl hangs KITCHEN_SINK_BOWL_M under the worktop's top face (``_worktop_parts``); the body ends under it
        bowl_bottom = z0 + h + KITCHEN_WORKTOP_M - KITCHEN_SINK_BOWL_M
        parts = P.open_carcass(x, yc + inset / 2.0, z0, w - 0.002, dc - inset, h, bowl_bottom - P.BASIN_CLEAR_M,
                               "painted")
    else:
        parts = [P._box(x, yc + inset / 2.0, z0, w - 0.002, dc - inset, h, "painted", "body")]
    kind = m.get("front") or "door"
    if kind in ("oven", "fridge"):
        return parts + _appliance_fronts(kind, x, w, face, z0, h, design)
    if kind == "drawers":
        fronts = P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 3, 1, design, doors=False)
    else:
        fronts = P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 1, 2 if kind == "doors" else 1, design)
    parts += _rotate_parts(fronts, x, 0.0, 0.0)
    return parts


def _appliance_fronts(kind: str, x: float, w: float, face: float, z0: float, h: float, design: dict) -> list[Part]:
    """26 Oct 2026: the front of a unit that holds an appliance (module docstring). ``oven``: a 59.5 cm built-in oven
    under the worktop (a steel control strip with two knobs, a black glass door with a steel bar handle, a glass
    window in it) over a drawer in the design's front style; ``fridge``: the under-counter fridge's steel door with a
    long bar handle at its top and a dark vent grille at its foot. Every part sits in front of the carcass face."""
    gap = 0.003
    fw = w - 0.004
    y_back = face - P.FRONT_GAP                         # the back of a front
    t = P.FRONT_THICKNESS
    cy = y_back - t / 2.0
    top = z0 + h - gap
    parts: list[Part] = []
    if kind == "oven":
        oven_z = top - KITCHEN_OVEN_H_M
        strip_z = top - KITCHEN_OVEN_STRIP_M
        # 28 Oct 2026: a 60 cm oven in a wider hob unit (a drawn 75 cm hob) has a front panel beside it on each side
        full = fw
        fw = min(full, KITCHEN_OVEN_W_M)
        side = (full - fw) / 2.0 - gap
        if side > 0.01:
            for sx in (-1.0, 1.0):
                parts += P._front_panel(x + sx * (fw / 2.0 + gap + side / 2.0), face, oven_z, side,
                                        top - oven_z, P.front_style_of(design))
        parts.append(P._box(x, cy, strip_z, fw, t, KITCHEN_OVEN_STRIP_M - gap, "steel", "front"))
        for sx in (-1.0, 1.0):                          # two control knobs on the strip
            parts.append(P._cylinder_y(x + sx * fw * 0.32, y_back - t - 0.022, strip_z + KITCHEN_OVEN_STRIP_M / 2.0,
                                       0.018, 0.018, 0.022, "dark", "handle", n=16))
        door_h = strip_z - oven_z - gap
        parts.append(P._box(x, cy, oven_z, fw, t, door_h, "dark", "front"))
        win_w, win_h = fw * 0.7, door_h * 0.45                   # the oven window, proud of the black glass
        parts.append(P._box(x, y_back - t - 0.0025, oven_z + door_h * 0.22, win_w, 0.003, win_h, "glass", "front"))
        parts.append(P._box(x, y_back - t - 0.03, oven_z + door_h - 0.055, fw * 0.8, 0.014, 0.016, "steel", "handle"))
        for sx in (-1.0, 1.0):                          # the handle's two posts
            parts.append(P._box(x + sx * fw * 0.38, y_back - t - 0.0125, oven_z + door_h - 0.053, 0.012, 0.023, 0.012,
                                "steel", "handle"))
        drawer_h = oven_z - z0 - 2 * gap
        if drawer_h > 0.06:
            parts += P._front_panel(x, face, z0 + gap, full, drawer_h, P.front_style_of(design))
            parts.append(P._handle(x, face, z0 + gap + drawer_h * 0.6, vertical=False))
        return parts
    if kind == "fridge_column":                       # 27 Oct 2026: the freezer door under the fridge door
        split = z0 + h * KITCHEN_COLUMN_FREEZER_SHARE
        for d0, d1 in ((z0 + gap, split - gap / 2.0), (split + gap / 2.0, top)):
            parts.append(P._box(x, cy, d0, fw, t, d1 - d0, "steel", "front"))
            hx = x + fw / 2.0 - 0.06                     # a long vertical bar handle near the opening edge
            hl = min(0.9, (d1 - d0) * 0.6)
            hz = d1 - hl - 0.08 if d1 <= split else d0 + 0.08     # near the doors' meeting line
            parts.append(P._box(hx, y_back - t - 0.03, hz, 0.016, 0.014, hl, "steel", "handle"))
            for sz in (hz + 0.02, hz + hl - 0.032):     # the handle's two posts
                parts.append(P._box(hx, y_back - t - 0.0125, sz, 0.012, 0.023, 0.012, "steel", "handle"))
        return parts
    door_h = top - z0 - gap
    vent = min(0.06, door_h * 0.1)
    parts.append(P._box(x, cy, z0 + gap + vent, fw, t, door_h - vent, "steel", "front"))
    parts.append(P._box(x, cy, z0 + gap, fw, t, vent - gap, "dark", "front"))
    parts.append(P._box(x, y_back - t - 0.03, top - 0.07, fw * 0.8, 0.014, 0.016, "steel", "handle"))
    for sx in (-1.0, 1.0):
        parts.append(P._box(x + sx * fw * 0.38, y_back - t - 0.0125, top - 0.068, 0.012, 0.023, 0.012, "steel",
                            "handle"))
    return parts


def _tall_unit_parts(m: dict, design: dict, d_run: float) -> list[Part]:
    """27 Oct 2026: a tall unit at a run end (the fridge-freezer column): its plinth (recessed at the front), the
    carcass up to the column's top, the fridge door over the freezer door in steel with long vertical bar handles."""
    w, d, h = m["size_m"]
    x, _y = m["pos_m"]
    z0 = float(m.get("z_m") or 0.0)
    inset = P.FRONT_GAP + P.FRONT_THICKNESS
    face = -d_run / 2.0 + inset
    parts = [P._box(x, KITCHEN_PLINTH_RECESS_M / 2.0, 0.0, w - 0.002, d - KITCHEN_PLINTH_RECESS_M, z0, "dark",
                    "plinth"),
             P._box(x, inset / 2.0, z0, w - 0.002, d_run - inset, h, "painted", "body")]
    if m.get("front") == "fridge_column":
        parts += _appliance_fronts("fridge_column", x, w, face, z0, h, design)
    else:
        fronts = P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 2, 1, design)
        parts += _rotate_parts(fronts, x, 0.0, 0.0)
    return parts


def _kitchen_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    parts: list[Part] = []
    w_run, d_run = plan["footprint_m"]
    island = bool(plan.get("island"))
    details = plan.get("details") if isinstance(plan.get("details"), dict) else None
    for m in plan["modules"]:
        w, d, h = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "plinth":
            parts.append(P._box(x, y, 0.0, w, d, h, "dark", "plinth"))
        elif m["kind"] == "base_unit":
            parts += _base_unit_parts(m, design, d_run)
        elif m["kind"] == "filler":
            parts.append(P._box(x, y, z0, w, d - 0.015, h, "front", "front"))
        elif m["kind"] == "worktop":
            parts += _worktop_parts(m, w_run, d_run)
        elif m["kind"] == "tall_unit" and m.get("column"):   # 29 Oct 2026 (K1): a column unit to the ceiling
            parts += KD.tall_parts(m, design, d_run, KITCHEN_PLINTH_RECESS_M)
        elif m["kind"] == "tall_unit":
            parts += _tall_unit_parts(m, design, d_run)
        elif m["kind"] == "waterfall":                      # 29 Oct 2026 (K2 / K15)
            parts += KD.waterfall_parts((x - w / 2.0, x + w / 2.0, "waterfall"), d, float(plan.get("worktop_m")
                                                                                        or KITCHEN_WORKTOP_HEIGHT_M))
        elif m["kind"] == "wall_unit":
            inset = P.FRONT_GAP + P.FRONT_THICKNESS
            parts.append(P._box(x, y + inset / 2.0, z0, w - 0.002, d - inset, h, "painted", "body"))
            face = y - d / 2.0 + inset
            cols = 1 if w < 0.60 - 1e-9 else 2
            # 29 Oct 2026 (K4): the family's fluted or handle-less uppers
            fronts = KD.upper_front_parts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, cols, design, details) \
                or P.cabinet_fronts(w - 0.004, face, z0 + 0.003, z0 + h - 0.003, 1, cols, design, handle_at="bottom")
            parts += _rotate_parts(fronts, x, 0.0, 0.0)
        elif m["kind"] == "hood":                          # 28 Oct 2026: the cooker hood over the hob
            parts += _hood_parts(m)
    if island:                                                # the back of an island shows a panel, not a carcass
        base_h = KITCHEN_WORKTOP_HEIGHT_M - KITCHEN_WORKTOP_M - KITCHEN_PLINTH_M
        # 29 Oct 2026 (G3): at the carcass's back (the knee space behind it), between the waterfall ends
        back = max((float(m["pos_m"][1]) + float(m["size_m"][1]) / 2.0 for m in plan["modules"]
                    if m["kind"] == "base_unit"), default=d_run / 2.0)
        ends = [tuple(s) for s in ((details or {}).get("waterfall_m") or [])]
        # one panel per worktop stretch: none across the gap of a drawn stove (fix round after P3)
        for m in plan["modules"]:
            if m["kind"] == "worktop":
                a = float(m["pos_m"][0]) - float(m["size_m"][0]) / 2.0
                b = float(m["pos_m"][0]) + float(m["size_m"][0]) / 2.0
                for e0, e1 in ends:
                    if e1 <= a + KD.WATERFALL_T_M + 1e-6 and e1 > a - 1e-6:
                        a = e1
                    if e0 >= b - KD.WATERFALL_T_M - 1e-6 and e0 < b + 1e-6:
                        b = e0
                if b - a > 1e-3:
                    parts.append(P._box((a + b) / 2.0, back - 0.009, KITCHEN_PLINTH_M, b - a, 0.018, base_h, "front",
                                        "panel"))
    parts += KD.run_detail_parts(plan)                       # 29 Oct 2026 (G3): the utensil rail
    return with_handle_posts(parts)


def _worktop_parts(m: dict, w_run: float, d_run: float) -> list[Part]:
    """The worktop slab with the sink bowl (steel basin and tap) and the hob plate at its cutouts. Fix round after
    P3: the slab lies at its own ``pos_m`` (a run with the gap of a drawn stove has one worktop per stretch); the
    cutouts' ``x_m`` are in the run's frame."""
    w, d, t = m["size_m"]
    z0 = float(m.get("z_m") or 0.0)
    xa, xb = float(m["pos_m"][0]) - w / 2.0, float(m["pos_m"][0]) + w / 2.0
    cutouts = m.get("cutouts") or []
    parts: list[Part] = []
    sink = next((c for c in cutouts if c["kind"] == "sink"), None)
    if sink is None:
        parts.append(P._box((xa + xb) / 2.0, 0.0, z0, w, d, t, "worktop", "top"))
    else:
        bw, bd = min(0.70, sink["w_m"] - 0.10), min(0.42, d - 0.16)
        sx = float(sink["x_m"])
        left, right = sx - bw / 2.0, sx + bw / 2.0
        strip = (d - bd) / 2.0
        parts += [P._box((xa + left) / 2.0, 0.0, z0, left - xa, d, t, "worktop", "top"),
                  P._box((right + xb) / 2.0, 0.0, z0, xb - right, d, t, "worktop", "top"),
                  P._box(sx, -d / 2.0 + strip / 2.0, z0, bw, strip, t, "worktop", "top"),
                  P._box(sx, d / 2.0 - strip / 2.0, z0, bw, strip, t, "worktop", "top")]
        parts += P._basin(sx, 0.0, z0 + t - KITCHEN_SINK_BOWL_M, bw, bd, KITCHEN_SINK_BOWL_M, 0.008, "steel")
        # 29 Oct 2026 (K7): a pull-down spray tap in the family's fixture finish (the handles' metal)
        parts += KD.tap_parts(sx, min(bd / 2.0 + 0.05, d / 2.0 - 0.03), z0 + t, "handle")
    hob = next((c for c in cutouts if c["kind"] == "hob"), None)
    if hob is not None:
        parts += hob_plate_parts(float(hob["x_m"]), float(hob["w_m"]), d, z0 + t)
    return parts


def hob_plate_parts(x: float, unit_w: float, d: float, z_top: float) -> list[Part]:
    """The hob plate on the worktop over a hob unit of ``unit_w`` (28 Oct 2026): the real plate class of the unit
    (``hob_plate_for``; before, every hob was a 58 cm plate), a black glass plate with a thin steel rim, four rings
    (five from ``KITCHEN_HOB_FIVE_FROM_M``: a wok ring in the middle) and a dark control strip at the front."""
    hw = hob_plate_for(unit_w)
    hd = min(KITCHEN_HOB_PLATE_D_M, d - 0.08)
    parts = [P._box(x, 0.0, z_top, hw, hd, 0.005, "dark", "hob"),
             P._box(x, -hd / 2.0 + 0.004, z_top, hw, 0.008, 0.006, "steel", "hob")]      # the front rim
    r = min(hw, hd) * 0.17
    five = hw >= KITCHEN_HOB_FIVE_FROM_M - 1e-9
    spots = [(sx * hw * (0.32 if five else 0.25), sy * hd * 0.22) for sx in (-1, 1) for sy in (-1, 1)]
    for px, py in spots:
        parts.append(P._cylinder_z(x + px, py + 0.02, z_top + 0.005, r * (0.85 if five else 1.0),
                                   r * (0.85 if five else 1.0), 0.0015, "steel", "ring", n=20))
    if five:
        parts.append(P._cylinder_z(x, 0.02, z_top + 0.005, r * 1.15, r * 1.15, 0.0015, "steel", "ring", n=24))
    parts.append(P._box(x, -hd / 2.0 + 0.035, z_top + 0.005, hw * 0.4, 0.03, 0.0008, "steel", "ring"))  # controls
    return parts


def _hood_parts(m: dict) -> list[Part]:
    """28 Oct 2026: a cooker hood module (``hood_module``) in the style's metal: the canopy (a slim box hood under a
    wall cabinet), the dark grease filter under it, a control strip at its front, and the chimney up to its top
    (against the wall behind a chimney hood, in the middle of an island hood)."""
    if m.get("style") == "cylinder":                  # 29 Oct 2026 (K3): the cylinder island hood (and its frame)
        return KD.cylinder_hood_parts(m) + KD.shelf_frame_parts(m)
    hw, hd, h = m["size_m"]
    x, y = m["pos_m"]
    z0 = float(m.get("z_m") or 0.0)
    kind = m.get("hood") or "chimney"
    canopy = HOOD_UNDER_H_M if kind == "under_cabinet" else HOOD_CANOPY_M
    parts = [P._box(x, y, z0, hw, hd, canopy, "handle", "hood"),
             P._box(x, y + 0.01, z0 - 0.002, hw - 0.04, hd - 0.06, 0.002, "dark", "filter"),
             P._box(x, y - hd / 2.0 - 0.0015, z0 + canopy * 0.25, hw * 0.3, 0.003, canopy * 0.5, "dark", "hood")]
    if kind == "under_cabinet":
        return parts
    cw, cd = HOOD_CHIMNEY_M
    cy = y if kind == "island" else y + hd / 2.0 - cd / 2.0
    top = float(m.get("chimney_top_m") or (z0 + h))
    if top - z0 - canopy > 0.01:
        parts.append(P._box(x, cy, z0 + canopy + P.FRONT_GAP, cw, cd, top - z0 - canopy - P.FRONT_GAP, "handle",
                            "chimney"))
    return parts + KD.shelf_frame_parts(m)            # 29 Oct 2026 (K3): a box island hood's shelf frame


def with_handle_posts(parts: list[Part]) -> list[Part]:
    """28 Oct 2026 (the user: the handles "look plain"): every bar handle of a kitchen module stands off its front on
    two feet (``HANDLE_POST_M``), as a real bar handle does; the bar keeps its role ``handle`` (one per front), the
    feet are ``handle_post`` parts in the handle's metal."""
    out: list[Part] = []
    post, stand = HANDLE_POST_M
    for p in parts:
        out.append(p)
        if p.get("role") != "handle" or p.get("key") != "handle" or len(p.get("verts") or []) != 8:
            continue
        xs = [v[0] for v in p["verts"]]
        ys = [v[1] for v in p["verts"]]
        zs = [v[2] for v in p["verts"]]
        w, d, h = max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)
        if d > 0.02:
            continue                                     # not a bar on a front (a knob, an oven handle)
        cx, cz = (max(xs) + min(xs)) / 2.0, (max(zs) + min(zs)) / 2.0
        back = max(ys)
        vertical = h > w
        length = h if vertical else w
        for s in (-1.0, 1.0):
            off = s * (length / 2.0 - post * 1.5)
            px, pz = (cx, cz + off) if vertical else (cx + off, cz)
            out.append(P._box(px, back - stand / 2.0, pz - post / 2.0, post, stand, post, "handle", "handle_post"))
        # the bar moves out by the stand-off, so the feet carry it
        out[-3] = dict(p, verts=[(vx, vy - stand, vz) for vx, vy, vz in p["verts"]])
    return out


def _bath_parts(plan: dict) -> list[Part]:
    design = plan.get("design") or {}
    parts: list[Part] = []
    w, d = plan["footprint_m"]
    if plan["type"] == "shower":
        return P._shower(w, d, plan["height_m"])
    for m in plan["modules"]:
        mw, md, mh = m["size_m"]
        x, y = m["pos_m"]
        z0 = float(m.get("z_m") or 0.0)
        if m["kind"] == "vanity":
            body, face = P._carcass(mw, md, z0, mh)
            basin_z = [float(b.get("z_m") or 0.0) for b in plan["modules"] if b["kind"] == "basin"]
            if basin_z:
                # fix round after P3, part 2 (17 Oct 2026): hollow above the bowls' bottom, as the kitchen sink unit
                inset = P.FRONT_GAP + P.FRONT_THICKNESS                  # the box of ``parametric._carcass``
                parts += P.open_carcass(0.0, inset / 2.0, z0, mw, md - inset, mh, min(basin_z) - P.BASIN_CLEAR_M,
                                        body["key"])
            else:
                parts.append(body)
            parts.append(P._box(0.0, md / 2.0 - 0.01, 0.0, mw * 0.3, 0.02, z0, "dark", "back"))
            parts += P.cabinet_fronts(mw - 0.004, face, z0 + 0.003, z0 + mh - 0.003, int(m.get("drawers") or 1), 1,
                                      design, doors=False)
        elif m["kind"] == "top":
            basins = [b for b in plan["modules"] if b["kind"] == "basin"]
            if not basins:
                parts.append(P._box(x, y, z0, mw, md, mh, "ceramic", "top"))
                continue
            # the top as strips around every bowl: front and back strips over the full width, side strips between
            bd = basins[0]["size_m"][1]
            strip = (md - bd) / 2.0
            parts += [P._box(0.0, -md / 2.0 + strip / 2.0, z0, mw, strip, mh, "ceramic", "top"),
                      P._box(0.0, md / 2.0 - strip / 2.0, z0, mw, strip, mh, "ceramic", "top")]
            edges = [-mw / 2.0] + sorted(v for b in basins for v in (b["pos_m"][0] - b["size_m"][0] / 2.0,
                                                                     b["pos_m"][0] + b["size_m"][0] / 2.0)) + [mw / 2.0]
            for k in range(0, len(edges) - 1, 2):
                x0, x1 = edges[k], edges[k + 1]
                if x1 - x0 > 1e-6:
                    parts.append(P._box((x0 + x1) / 2.0, 0.0, z0, x1 - x0, bd, mh, "ceramic", "top"))
        elif m["kind"] == "basin":
            parts += P._basin(x, y, z0, mw, md, mh, 0.012, "ceramic")
            parts.append(P._cylinder_z(x, md / 2.0 + 0.04, plan["modules"][1]["z_m"] + plan["modules"][1]["size_m"][2],
                                       0.012, 0.012, 0.15, "steel", "tap", n=12))
        elif m["kind"] == "mirror":
            f = 0.025
            parts.append(P._box(x, y + 0.002, z0, mw, md - 0.004, mh, "wood", "frame"))
            parts.append(P._box(x, y - md / 2.0 + 0.002, z0 + f, mw - 2 * f, 0.004, mh - 2 * f, "mirror", "glass"))
    return parts


_PART_BUILDERS = {"wardrobe_run": _wardrobe_parts, "table_long": _table_parts, "sofa_l": _sofa_l_parts,
                  "kitchen_run": _kitchen_parts, "bath_set": _bath_parts, "wall_run": _wall_run_parts}


def module_parts(plan: dict) -> list[Part]:
    """The parts of a module plan in the piece frame (pure): ``parametric`` part dicts with their material keys
    (``MATERIAL_KEYS``) and roles; ``KeyError`` for an unknown builder."""
    try:
        builder = _PART_BUILDERS[plan["builder"]]
    except KeyError:
        raise KeyError(f"no module builder {plan.get('builder')!r}") from None
    return builder(plan)


def plan_bbox(plan: dict) -> tuple[float, float, float]:
    """``(width, depth, height)`` of the plan's parts (the real box the planners read). Fix round after P3: a kitchen
    run with the gap of a drawn stove at one of its ends keeps the run's drawn width (the planners centre the box on
    the footprint, and the stove fills the gap)."""
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(module_parts(plan))
    if plan.get("gaps") and plan.get("footprint_m"):
        return (max(x1 - x0, float(plan["footprint_m"][0])), y1 - y0, z1 - z0)
    return (x1 - x0, y1 - y0, z1 - z0)


def material_keys(plan: dict) -> list[str]:
    """The distinct material keys of a plan's parts, in order of first use (the object's material slots)."""
    keys = [p["key"] for p in module_parts(plan)]
    return sorted(set(keys), key=keys.index)


def module_record(plan: dict) -> dict:
    """The compact record of a plan for the scene manifest (no parts)."""
    return {"builder": plan["builder"], "modules": len(plan["modules"]), "kinds": sorted({m["kind"] for m in plan["modules"]}),
            "products": list(plan.get("products") or []), "footprint_m": list(plan["footprint_m"]),
            "height_m": plan["height_m"], "drawn_m": list(plan.get("drawn_m") or plan["footprint_m"]),
            "fit": dict(plan.get("fit") or {}), "notes": list(plan.get("notes") or []),
            **({"split": plan["split"]} if plan.get("split") else {}),
            **({"cutouts": plan["cutouts"]} if plan.get("cutouts") else {}),
            # fix round after P3: the gaps of the drawn stoves and the drawn sink built into a kitchen run
            **({"gaps": plan["gaps"]} if plan.get("gaps") else {}),
            **({"built_ins": plan["built_ins"]} if plan.get("built_ins") else {}),
            # 28 Oct 2026: the worktop line, the hood and the wall run's units (the model review's M2 and M13 read them)
            **({k: plan[k] for k in ("worktop_m", "hood", "units_m", "ends", "free_m", "misaligned",
                                     "made_to_measure", "blocked_m") if plan.get(k) is not None}),
            # 29 Oct 2026: the kitchen details the family's rule gave the run (model review M27, Argus U31)
            **({"details": plan["details"]} if isinstance(plan.get("details"), dict) else {})}


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

class ModuleMaterials:
    """What ``build_module`` needs besides the plan and the piece: ``get(key)`` -> a Blender material for a part
    key (``furniture._Materials.get`` with the piece's design overrides), and where the object goes: ``collection``,
    ``floor_z`` (the room's floor), ``name``, ``status``. ``furniture.create_furniture`` fills it; a plain mapping
    ``{key: material}`` works too (scene collection, floor 0, name ``furn_<id>``)."""

    def __init__(self, get, collection=None, floor_z: float = 0.0, name: Optional[str] = None,
                 status: str = "verified", slugs=None):
        self._get = get
        self.collection = collection
        self.floor_z = float(floor_z)
        self.name = name
        self.status = status
        self._slugs = slugs

    def get(self, key: str):
        return self._get(key)

    def slug(self, key: str) -> Optional[str]:
        return self._slugs(key) if self._slugs else None


def build_module(plan: dict, piece: dict, materials):
    """Build the object of a module plan (``bpy``): the parts of ``module_parts`` placed on the drawn footprint
    (``piece["footprint"]``: centre, rotation) on ``materials.floor_z``, one material slot per part key from
    ``materials.get(key)`` (a ``ModuleMaterials`` or a mapping), the Bevel modifier of ``furniture.add_bevel``,
    smooth cushions, and the custom properties ``wenart_method = "module"``, ``wenart_module`` (the builder) and
    ``wenart_type``. Returns the object; its ``["wenart_module_record"]`` holds ``module_record(plan)`` as JSON.

    Fix round after P3, part 2 (17 Oct 2026): a plan without parts raises ``ValueError`` before anything is linked
    (an empty object named ``furn_<id>`` had taken the name, and the parametric fallback became ``furn_<id>.001``
    while the manifest still named the empty one)."""
    import json

    parts = module_parts(plan)
    if not parts:
        raise ValueError(f"the {plan.get('builder')} plan of {piece.get('id')} has no parts (nothing to build)")

    import bpy

    from wenart.blender import furniture as F

    fp = piece["footprint"]
    if isinstance(materials, dict):
        get = materials.__getitem__
        collection, floor_z, name, status = None, 0.0, None, piece.get("status") or "verified"
    else:
        get = materials.get
        collection = getattr(materials, "collection", None)
        floor_z = float(getattr(materials, "floor_z", 0.0) or 0.0)
        name = getattr(materials, "name", None)
        status = getattr(materials, "status", None) or piece.get("status") or "verified"
    collection = collection or bpy.context.scene.collection
    name = name or f"furn_{piece['id']}"
    verts, faces, keys = P.world_mesh(parts, fp["center"], float(fp.get("rotation_deg") or 0.0), floor_z)
    used = sorted(set(keys), key=keys.index)
    slots = [get(k) for k in used]
    ob = F._mesh_object(name, verts, faces, slots, [used.index(k) for k in keys], collection, piece["id"],
                        "furniture", status)
    bevel = F.add_bevel(ob, parts)
    ob["wenart_method"] = MODULE_METHOD
    ob["wenart_module"] = plan["builder"]
    ob["wenart_type"] = piece.get("type") or plan.get("type") or ""
    ob["wenart_module_record"] = json.dumps(module_record(plan))
    ob["wenart_bevel"] = json.dumps(bevel or {})
    return ob
