"""The pipeline's furniture reading step (docs/milestone12.md §4.1 D7, contract §13.2; owner: track R).

Contract (frozen 10 Oct 2026): ``read_furniture(build, works) -> None`` is called by ``pipeline.run_project`` after
``levels.apply_levels`` and before the type inference. It moves non-furniture symbols (room-number circles, north
arrows, axis bubbles, section marks, door-swing arcs, dimension outlines, text frames) from
``building["furniture"]`` to ``building["symbols"]`` with kind and evidence; types pieces by block names, cluster
splits and context rules; fixes misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026); and leaves no
untyped piece built (``build: false`` + ``needs_review`` list in the report).

What, in order (each step deterministic, every change logged in the piece's evidence and the warnings):

1. **Symbols**: pieces the generic core marked (``details["symbol"]``: a room-number tag, a north arrow, a door
   swing, a piece drawn on door, text, area, axis or view-line layers; ``symbols.whole_symbol``) leave the furniture
   for ``building["symbols"]`` (``former_piece_id``, reason, evidence, the plan crop of its question when it was
   asked). The drawing outranks the AI passes (CLAUDE.md trust order): a room-number circle both passes called a
   floor lamp is a symbol, and the disagreement is a ``type_disagreement`` conflict. A column or decor
   (``details["not_furniture"]``) stays as a not-built piece (``inferred_as``; a column is still an obstacle). The
   symbols the re-read found inside clusters (``ex.report["symbols"]``) are added. A level mark still among the
   pieces (track L's ``apply_levels`` moves them first) is moved too, as ``level_mark``. A type the core's re-read
   set against the AI passes is a ``type_disagreement`` conflict. Copies of one block drawing in other inserts of
   the block (``copy_keys``) share their type or their symbol.
2. **Code typing first** (Milestone 13, docs/milestone13.md §3.0 K3, CLAUDE.md "an untyped drawn footprint is
   typed by code first"; build round 3, lead decision): ``infer.code_types`` (``type_by_code``: the same footprint
   in the twin room or on another level, the block name, the room's missing group member) runs before the context
   rules and before any AI, on a piece whose question waits too (``code_first``); such a piece is typed
   (``type_method`` twin | level | block | group_member, ``inferred`` with the evidence) and its question is
   withdrawn (``withdraw_questions``: the key leaves the page's ``pending`` and is listed under
   ``report["typed_by_code"]`` with its method in ``report["typed_by_code_methods"]``, ``build.code_typed`` /
   ``build.code_typed_methods``; the pipeline leaves it out of ``recognition/requests.json``).
   **Context typing** (the Milestone 12 rules, on what code left, the open questions too): an L outline with
   seat-deep arms in a living room is a corner sofa; an unknown box drawn with a door swing beside the counter run
   (or closing it, proud of it) is a fridge; a 0.5-0.75 m deep strip along a wall holding a sink or hob is a
   counter; two small squares at a bed's head are nightstands; a table-sized piece with seats drawn around it on
   two sides is a dining table, and small pieces at a dining table are chairs facing it; a bowl with a drain in a
   bathroom is a washbasin and the counter under it its vanity; two equal seats across a coffee table are
   armchairs; a table in front of a sofa is a coffee table; a long low strip at a wall facing a sofa is a TV unit.
   A piece a context rule types is code typed as well (method ``context:<type>``, ``context:vanity`` for the
   counter under a basin): its question is withdrawn too. The code typing runs again after the context rules
   (chains: the missing member of a group whose anchor a context rule typed) and the context rules once more.
   Every step up to here holds the open questions the same way in every mode (``open_questions``: a block copy
   never decides one, no front for it yet), and a question asked and answered in this round is never withdrawn
   (``answered_keys``), so the question count is the same with ``--no-ai``, in the first plain run and in the run
   with the answers (the AI types only what neither code nor the drawing's context explains). A fixed piece drawn
   inside another of its type is drawn twice (not built).
3. **Inference** (``wenart.furniture.infer``: size, room and position) for what is still unknown; a piece whose
   AI question still waits for its answers is left to them (the size and position rules are weaker than a plan
   crop; the code methods above apply there as well and withdraw as above). The context rules then type the
   partners of the anchors the inference typed (Milestone 12 behaviour: open questions wait, nothing is withdrawn,
   because with ``--no-ai`` the size inference types pieces a plain run leaves to the AI).
4. **Misread fixed equipment** (user OK 1 of 10 Oct 2026): a fixed piece whose drawn size is more than 30 % outside
   its type's real range gets the nearest real product size (``sizes.product_size``), its back kept on its wall; a
   fixed piece through a wall or in a door swing moves up to 0.5 m to the nearest free spot. ``drawn_type``,
   ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height`` are kept; ``adjusted_by_ai`` holds the reason, the
   changed fields and the plan crop; the piece's evidence gets the rule's entry. 27 Oct 2026 (``fixture_seat``; user
   on real06 run 180412: "clashing sink and bath, also bath is not in proper place"): a drawn fixed piece standing in
   another drawn fixture (deeper than 3 cm; a piece built into a counter or vanity excepted) is a reading error as
   well: the one with the weaker reading gives way (``fixture_rivals``), sliding along its wall to the nearest free
   place within 0.5 m, else seated in its drawn outline; a misread outline that stands on no wall (a merged outline's
   box angle) is seated in it (``_fixed_place``). The record merges into an earlier code record of the piece.
5. **Fronts**: a drawn piece of a type with a front and none drawn gets one from the wall its back stands on or
   from its group (a chair faces its table, a nightstand the way its bed faces, a TV unit its sofa), ``inferred``.
5b. **Fixtures you can use** (29 Oct 2026, lessons UL92 / UL95 / UL96; ``fixture_use_fixes``, ``wenart.furniture.
   fixture_use``): after the fronts, a back parallel to its wall a drawing gap (0.055-0.15 m) off it goes back onto the
   wall with what is built into it; a door-fronted piece (a washer, a dishwasher, a cooker, a fridge, a nightstand)
   whose front a wall or a neighbour blocks turns to its free side with its back on a wall, else moves at most 0.5 m
   (real06's washer f_L1_019 got no front in its corner, faced the wall and was later turned onto the toilet); a basin
   under a window with its sill under 1.25 m moves at most 0.5 m to a solid stretch of wall (else the architect's H2
   asks). Each ``adjusted_by_ai`` by code with the reason and the plan crop, the drawn values kept.
6. **Open kitchens**: a room that is not a kitchen but holds kitchen fixtures gets a kitchen zone
   (``rooms[].zones``, contract §13.3) around them; the room-type rules apply per zone (track G).
7. **Never a box**: a piece still untyped is not built and listed in ``building["needs_review"]`` with its crop
   and reason (a piece whose question waits is not built and not listed: the pipeline lists the open questions).

Fix round after P3 (16-17 Oct 2026): only the questions of the pages the pipeline writes to ``requests.json`` (the
master of a level, a furniture plan that furnishes it) can be answered. A secondary page of a level (real04: the
second plan region r16 of the ground floor) numbers its candidates like the master (``sym_L0_001`` ...) and its
questions are never asked, so its report carries ``NOT_ASKED_KEY`` (set by ``pipeline._assemble_level``): nothing
waits for its questions (``_pending``, ``open_questions``), its items never stand for a piece the asked page drew
(``_items``: the asked page's item wins) and none of its keys is withdrawn (``withdraw_questions``). Before, a master
piece the second region drew too (f_L0_021, f_L0_024: both AI answers in the building) and the second region's own
pieces kept "waits for the answers" in the run with the answers, not built and missing from the review list.
``never_a_box`` also clears that reason on a piece that no longer waits (a building read again), so it is typed or
listed. A secondary page's crops live in its own folder (``details["crop_dir"]``, ``_crop``).

Fix round after P4b (17 Oct 2026; pod P4b, real03). What:

- **The code typing reads the first reading's building in every pass** (``code_first(build, reset)``). In the run with
  the answers, the pieces typed only because of this round's answers (``answer_typed``: an asked and answered
  question whose piece has a type when the reading starts, and the block copies ``copies`` typed from such a piece)
  are reset to ``unknown`` in a copy of the building before ``infer.code_types`` runs (``inferred_as: "answered"`` in
  that copy only, so code never types them). Only the proposals for pieces that are still untyped in the real
  building are applied: an AI type is never replaced by code, and a piece the AI left unknown is still typed by code
  as before. Without answers nothing is reset, so the first run and ``--no-ai`` are unchanged. Why: in P4b's run with
  the answers, the AI's bathtubs and showers filled the bath sets, so the rule "the bath set misses shower|bathtub"
  that typed six drawn symbols in the first reading (and withdrew their questions) no longer found the slot. The six
  stayed untyped, their questions were late (never asked), and the agent marked them as not furniture.
- **Type method of the context rules and the size inference**: a piece a context rule or a block copy types gets
  ``type_method: "rule"`` (a reading rule of the drawing; ``report["typed_by"]`` keeps ``context:<type>``); a piece
  the size inference types gets ``type_method: "inferred"`` (``mark_inferred``; ``pipeline._infer_types`` does the
  same). Both values are in the building schema. Before, both kept ``none``: P4b's 24 typed drawn pieces (6 corner
  sofas among them) counted as untyped in the final manifest.
- **A two-pass disagreement is decided by code** (``tie_break``, after the size inference): an untyped drawn piece
  whose two AI passes named two different furniture types, both fitting its drawn size and both allowed in its room,
  gets the one the room misses (``room_misses``: the missing members of its drawn groups and the anchors of its
  program's groups), else the one whose real product size is nearer. It is marked ``inferred`` with the reason and
  the plan crop (``type_method: "inferred"``, status ``unverified``), and the ``symbol_type_disagreement`` conflict
  stays in the report with this decision as its resolution. Why: real03's bedroom oda_01 draws a 1.5 x 0.6 m piece;
  Qwen said dresser, GLM said wardrobe, and the piece stayed an unbuilt unknown in a room with no storage (CLAUDE.md:
  the AI infers the type and marks it inferred; never an unexplained box).

Pass before P5 (17 Oct 2026). What: the tie-break decides twins together, and the code typing runs once more after
it. A disputed piece with the same footprint at the mirrored spot of a twin room (``_twins_of``: ``infer._twin_rooms``,
the centre within ``infer.SAME_CENTRE_M``, the size within ``infer.SAME_FOOTPRINT_M``) is decided with that twin,
when one of them at least could be decided alone (two answers that both fit; else they stay for review, as before):
when the AI passes of both name one type that fits the drawn size and both rooms, both get it (``TWIN_TIE_NOTE``);
else one of them is decided alone, so is a twin whose passes named that type, and the other twins wait for the twin
rule; a piece whose twin is already typed is left to the twin rule as well. Then, when the tie-break typed or left a
piece to its twin, ``code_first`` runs again (no reset: the AI's and the tie-break's types count) before the fronts and
the review list; ``withdraw_questions`` keeps a question asked and answered in this round listed and withdraws one
that was not (a late one), as ``pipeline._infer_types`` did right after this step before. Why: on P3's real04
building the tie-break typed f_L1_035 sideboard (sideboard / tv_unit) and left its mirror twin f_L1_033 (sideboard /
bench; a bench is not allowed in that room) untyped and listed for review until the pipeline's later inference; the
mirrored twins f_L1_034 (bookshelf / tv_unit) and f_L1_036 (bookshelf / console_table) got bookshelf and
console_table at the same drawn spot of the two mirrored flats. Now the tie-break types f_L1_033 sideboard and
f_L1_036 bookshelf (both twins named them); its 12 other decisions on that building are unchanged.

Fix round after P5 (22 Oct 2026; pod P5, real04; user decisions of 22 Oct 2026). What (counts: the P4a / P4b / P5 run
buildings of real02 / real03 / real04):

- **The drawn L corner sofas first** (``corner_sofa_pass``, the corner-sofa rule of ``context_types`` on its own):
  before the first code typing, so the code typing sees the room's seating anchor; the outline in its open corner is
  its coffee table (real02 / real04 f_L-1_061/062; ``infer`` module docstring for the role places).
- **A seat faces its coffee table** (``_front_of``): a sofa or armchair without a front faces the nearest coffee table
  within ``SEAT_TABLE_M`` (a sofa only along a long side). With the reader's bed-pillow rule kept to beds
  (``symbols``), this turns real02's and real04's oyun sofas f_L1_009/010/011/012 to 0 / 180 / 270 / 270 deg (they faced
  away) and the salon armchairs f_L-1_049/050 to their coffee tables (270 deg).
- **Long-side fronts** (``long_side_fronts``): an AI or tie-break front on the short side of a type that faces along
  a long side (``LONG_FRONT_TYPES``) is a reading error; the front goes to the long side the drawing gives
  (``_front_of``) or facing the most room, ``adjusted_by_ai`` by code with the drawn front kept. real04: the twin
  sofas f_L-1b_045/046 (0.82 x 1.64 m, built as a 0.82 m wide sofa, a false library gap).
- **Desk symbols that hold their chair** (``desk_chairs``; CLAUDE.md "a table footprint that includes its chairs"): a
  drawn desk with its back on a wall deeper than ``DESK_SPLIT_DEPTH_M`` keeps ``DESK_DEPTH_M`` at its wall
  (``adjusted_by_ai`` by code, ``drawn_footprint`` kept, the plan crop) and its chair becomes a drawn office chair in
  front of it (``type_method: rule``, the desk's vector evidence). real02 f_L0_027..030, real04 f_L0_023..026 (the
  crop sym_L0_007 shows a 0.6 m desk and the chair's back).
- **Seat cushions** (``seat_cushions``; CLAUDE.md "a cushion read as a sofa"): a drawn piece at most ``CUSHION_MAX_M``
  either way, at least ``CUSHION_INSIDE`` inside a larger drawn seat of its room, is not built (``inferred_as: detail``,
  ``adjusted_by_ai`` by code with ``not_furniture: seat_cushion`` and the plan crop). real04: the "ottomans"
  f_L-1_075..078 on the armchairs f_L-1_069..072 (85 % inside).
- **Baths and showers a few cm longer than their bay** (``bay_overrun`` / ``bay_fit`` / ``shrink_to_bay`` in
  ``fix_fixed``; user decision (3) of 22 Oct 2026, CLAUDE.md fixed equipment "a misread size"): a drawn bathtub or
  shower whose part outside its room lies in end strips only and runs ``BAY_OVERRUN_M`` (1-5 cm) past the walls is
  given the nearest real product (``sizes.products``, log distance) that fits the clear bay, its back kept on its wall,
  ``drawn_footprint`` kept, ``adjusted_by_ai`` by code (rule ``BAY_RULE``, "misread size", the plan crop).
  ``edit_ops.fix_fixture`` uses the same ``bay_fit``. real03: the tubs f_L0_184..187 (1.62 x 0.80 m -> 1.50 x 0.70 m),
  the showers f_L0_179/180 (0.90 x 0.97 -> 0.90 x 0.90), f_L0_054 (1.07 x 0.80 -> 1.00 x 0.80) and f_L0_145 (0.85 x
  1.02 -> 0.80 x 0.80); none on real02 or real04.

Fix round after P5 (22 Oct 2026), review of the steps above:

- **No short-side front from the wall rules** (``_front_of`` / ``_long_front``): a type that faces along a long side
  (``LONG_FRONT_TYPES``) never gets a front on its short side from the one-wall, corner or free-side rules (a sofa as a
  room divider with one arm on the wall faced along its length); the front is the free long side facing the most
  room. This covers the pieces ``long_side_fronts`` does not see (block-named pieces, fronts of the last
  ``infer_fronts``).
- **A desk is split only when its symbol holds the chair** (``desk_chairs``): deeper than ``DESK_SPLIT_DEPTH_M``
  (0.90 m, the top of the desk depth range: a real desk size is never cut; real02 / real04's 0.907 m desks still
  split) and no drawn seat (``DESK_SEATS``) between its cut line and ``DESK_SEAT_REACH_M`` in front of it (a drawn
  chair is never doubled by a second 'from_documents' one).
- **A corner sofa hosts a cushion only on its drawn L** (``seat_cushions``): a ``sofa_corner`` without ``shape: L``
  (typed by the group rule or the AI: its box holds the open corner) hosts none, so a pouf or side table drawn in its
  open corner stays.
- **A second code correction keeps the first one's record** (``_code_label`` -> ``infer.merge_code_label``).
- **A bath or shower shrunk without a question crop gets a plan crop** (``reading_crop``): a block-named piece (real03
  f_L0_054) has no recognition crop; the reading draws one in the layout of the question crops
  (``recognition.crops.draw_vector_ctx``) from the level's vector walls (grey), the other drawn pieces (light grey) and
  the piece's drawn footprint (black, dashed box) into ``<out>/READING_CROP_DIR/<piece id>_ctx.png`` and records it
  (``adjusted_by_ai["crop"]`` and the rule's evidence). The block's own strokes are not kept past the extraction, so
  the object is its drawn footprint. A misread fixed piece (``fix_fixed``) gets the same. A question's own crop still
  wins (a code-typed piece keeps the crop of its withdrawn question: real03 f_L0_145, sym_L0_053).

Reading fixes of 26 Oct 2026 (user: "fix should be general, it is not a fix for real06, it must be a fix for the
project"; real06 is the test case, tests/test_reading_sense_20261026.py). What, where in ``read_furniture``:

- **A room named only by a generic word** (``generic_rooms``, first): a room whose label is only "Oda" / "Room" and a
  number (``building.generic_room_label``) that the ingest typed by that word (bedroom, other or unknown) and that has
  no bed drawn takes the room type its drawn anchors name (``groups.yaml`` ``room_aliases.content``; a desk names none)
  when a block name or two agreeing AI passes typed them and they name one type (a living room's dining set counts as
  living); a kitchen only with a drawn sink or hob; never a bedroom whose furniture name texts name a bedroom piece (a
  dresser, a nightstand, a bed: 27 Oct 2026, text outranks the AI passes). ``corrected_by_ai`` keeps the reason, the anchors and the type before. Why:
  real06's r_L1_oda_2 "ODA" holds a sofa both passes agreed on and no bed: it was read as a bedroom (and got a kitchen
  zone from two false counters).
- **Nested outlines of one piece** (``nested_outlines``, before the code typing): drawn pieces whose footprints are
  nested (``NEST_INSIDE`` of the smaller inside the bigger, centres within ``NEST_CENTRE_M``, the smaller at least
  ``NEST_AREA_MIN`` of the bigger's area and ``NEST_LONG_MIN`` of its long side) are one piece; the strongest evidence
  stays (``NEST_RANK``: a block name > two agreeing passes > a reading rule > the rest; on a tie the outer outline),
  the others are not built (``inferred_as: detail``, ``merged_into``, ``adjusted_by_ai`` by code with the plan crop).
  Two fixed types are never merged (a sink in its counter; one fixed piece drawn twice stays ``duplicates``' rule), and
  a group with a piece whose question waits is left to its answers. Why: real06's wardrobe f_L1_018 (two passes) was
  drawn with two inner outlines read as a kitchen counter (f_L1_003) and a coffee table (f_L1_019), one centre.
- **Two answers of one run group** (``tie_break``, ``_one_group``, ``_holds_member``): when both AI answers are members
  of one run group (kitchen_counter and sink_kitchen: the kitchen run), the piece is the run holding the named member
  (``holds``; a sink or hob gets its place in ``module_hints`` for the kitchen run's module plan), and a run's depth
  outside its product range takes the product depth (0.60 m), its back kept on its wall, ``drawn_footprint`` kept,
  ``adjusted_by_ai`` by code (``RUN_DEPTH_RULE``). Why: real06's f_L0_027 (1.20 x 0.45 m, kitchen_counter /
  sink_kitchen) was "two fixed types the room does not miss" and stayed an unbuilt unknown.
- **A wall type needs its back on a wall** (``tie_break`` with ``infer.placeable``): an answer that is a wall type
  whose back cannot stand on a wall (no side within 0.10 m and 5 deg of the room outline), or a chair drawn round, is no
  choice: the other answer is taken. Why: real06's f_L0_016 (0.87 x 0.52 m at 135 deg, table_coffee / bookshelf)
  became a lone diagonal bookshelf in the salon "because the room misses it".
- **A round piece is never a chair** (the chairs rule of ``context_types``). Why: real06's round 0.58 m table
  f_L1_026 beside an armchair read as a dining table became a chair.
- **A kitchen run drawn as one outline** (``kitchen_outlines``, after the tie-break): an untyped piece in a kitchen,
  deeper than a counter both ways, holding a sink's drain or a hob's burners (``details["kitchen_signs"]`` of the
  extraction) is replaced by counter legs 0.60 m deep along each of its sides on a wall (the corner to the longer leg),
  drawn pieces with the outline as ``drawn_footprint`` and ``adjusted_by_ai`` by code; the outline is not built
  (``replaced_by``). Why: real06's f_L0_002 (3.99 x 2.40 m with sink and hob circles) "fits no size-table type" and
  was not built.

Furniture name texts of 26 Oct 2026 (the auditor Argus, source ledger A6; ``wenart.furniture.names``). What: the reading
first records every furniture name text of the read plan pages on the building (``furniture_texts``: the inventory's
text rows, ``names.furniture_name``; one warning each), so the code typing types an untyped footprint the text names
(``infer.type_by_code``, method ``name_text``, in ``code_pass`` before the context rules, the tie-break and the AI), the
inference corrects an AI type of another type the text is written on (``infer.name_text_retypes``), ``never_a_box``
says why a text near an untyped piece was not used (``infer.name_text_note``), and the pipeline adds the piece a text
names where no drawn piece stands (``names.add_named_pieces``, after ``_infer_types``). Why: real06 L1's "*SIFONIYER"
(f_L1_007 became a desk by the tie-break, f_L1_019 stayed unknown, the master bedroom's dresser was missing) and
"çamaşır mak." (the empty square f_L1_021 became a second washbasin) were not read. The reading also records the
zone labels of the rooms (``zone_labels``: a second label naming a zone of another kind, "YEMEK BÖLÜMÜ" in the salon,
with its zone), so the code typing gives the zone's anchor to the footprint drawn there (``infer`` method
``zone_label``; real06's round dining table f_L0_011 was "the living room's corner sofa"); the inference types the
member a room misses that the AI passes named (``infer.ai_named_members``: real06's corner baths); and the type
disagreement of a piece these rules typed gets the decision as its resolution (``resolve_named_conflicts``).
"""
from __future__ import annotations

import copy
import math
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G
from wenart.furniture import fixture_seat as FS

SYMBOL_RULE = "reading.symbols"
CONTEXT_RULE = "reading.context"
FIXED_RULE = "reading.fixed_equipment"
FRONT_RULE = "reading.front"
ZONE_RULE = "reading.kitchen_zone"
CROP_DIR = "recognition/crops"
WALL_SIDE_M = 0.10                 # a side this close to the room outline stands on a wall
NIGHTSTAND_M = (0.30, 0.65)        # a nightstand-sized square ...
NIGHTSTAND_GAP_M = 0.35            # ... beside a bed (gap to its long side) ...
NIGHTSTAND_HEAD_M = 0.70           # ... within this of the head edge
COFFEE_FRONT_M = (0.20, 1.60)      # a coffee table stands this far in front of a sofa ...
TV_DISTANCE_M = (0.9, 6.0)         # a TV unit this far from the sofa's front ...
TV_AXIS_DEG = 25.0                 # ... within this of the sofa's axis ...
TV_DEPTH_M = (0.20, 0.65)          # ... a strip this deep ...
TV_LENGTH_M = (0.90, 2.60)         # ... and this long
COUNTER_DEPTH_M = (0.50, 0.75)     # a counter strip along a wall
FRIDGE_REACH_M = 0.30              # a box with a door this close to the kitchen run is the fridge
DOOR_NEAR_M = 0.15                 # a door swing symbol this close to a box is its door
MISREAD_SHARE = 0.30               # a fixed piece more than 30 % outside its real size range is misread
MOVE_MAX_M = 0.50                  # ... and may move this far to the nearest valid spot
MOVE_STEP_M = 0.05
THROUGH_WALL_M = 0.05              # a fixed piece reaching more than 5 cm past its room's outline is through a wall
SWING_SHARE = 0.05                 # ... and one with more than 5 % of its area in a door swing stands in it
ZONE_AISLE_M = 1.0                 # a kitchen zone: the kitchen pieces and the 1 m in front of them
KITCHEN_ZONE_TYPES = ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge", "tall_cabinet",
                      "wall_cabinet")
SEAT_TYPES = ("sofa", "sofa_corner")
# The back is a short side (a crib's front is a long side: track B's size table, the layout builds it so).
HEAD_TYPES = ("bed_double", "bed_single", "bunk_bed", "toilet")
CHAIR_SIDE_M = (0.30, 0.65)        # a chair (or its half-round back drawn alone) ...
CHAIR_REACH_M = 0.40               # ... this close to a dining table faces it
CHAIR_DEPTH_M = 0.45               # a chair drawn shallower (its back alone) reaches this deep towards the table
DINING_SEATS_MIN = 3               # a table-sized piece with this many seats around it (on two sides) is a dining table
ARMCHAIR_REACH_M = 0.60            # two equal seats this close to a coffee table, on opposite sides, are armchairs
VANITY_SHARE = 0.3                 # an unknown counter under >= 30 % of a washbasin is its vanity
DUPLICATE_SHARE = 0.6              # a fixed piece this much inside a block-named one of its type is drawn twice
L_SEAT_MIN_M = 0.65                # the arms of an L corner sofa are seat-deep (a counter's legs are 0.6 m)
EXPLAINED_AS = ("rug", "detail", "column", "decor")
# Fix round after P5 (module docstring).
BAY_TYPES = ("bathtub", "shower")
BAY_OVERRUN_M = (0.01, 0.05)       # a bath or shower 1-5 cm longer than its bay is a misread size (user, 22 Oct 2026)
BAY_SPAN = 0.6                     # the cut at an end spans at least this share of the side (else a corner or column)
BAY_RULE = "reading.bay_size"
LONG_FRONT_TYPES = ("sofa", "desk", "wardrobe", "tv_unit", "bench", "sideboard", "dresser", "bookshelf",
                    "console_table", "shoe_cabinet", "display_cabinet")
LONG_FRONT_RATIO = 1.25            # a front on a side this much shorter than the other is on a short side
LONG_FRONT_RULE = "reading.long_side_front"
SEAT_TABLE_M = 1.2                 # a sofa or armchair without a front faces the nearest coffee table this close
DESK_SPLIT_DEPTH_M = 0.90          # a desk symbol deeper than this holds its chair (CLAUDE.md: a table footprint ...;
#                                    review: the top of the desk depth range, so a real desk size is never cut)
DESK_SEATS = ("chair", "office_chair", "bar_stool", "armchair")   # review: a seat drawn in front ...
DESK_SEAT_REACH_M = 0.80           # ... between the cut line and this far in front of the desk: nothing to split
DESK_DEPTH_M = 0.60                # ... the desk keeps this depth at its wall ...
DESK_CHAIR_M = (0.50, 0.50)        # ... and its chair (width, depth) stands in front, tucked in
DESK_RULE = "reading.desk_chair"
CUSHION_MAX_M = 0.50               # a drawn piece this small ...
CUSHION_INSIDE = 0.75              # ... at least this much inside a larger drawn seat is its seat cushion
CUSHION_SEATS = ("sofa", "sofa_corner", "armchair", "chaise")
CUSHION_RULE = "reading.seat_cushion"
READING_CROP_DIR = "recognition/reading"   # review: plan crops the reading draws for pieces without a question crop
# Fix round after P3 (16-17 Oct 2026): the extraction report key of a page whose recognition questions are never asked
# (``pipeline._assemble_level`` sets it on a secondary page of a level; its value says why), and the reason a piece
# whose question waits is not built (``never_a_box``).
NOT_ASKED_KEY = "questions_not_asked"
WAITS_REASON = "untyped: its AI question waits for the answers"
# Fix round after P4b (17 Oct 2026, module docstring): the code typing's view of a piece typed by this round's answers
# (never written to the building), the type methods of the context rules and of the size inference (both in the
# building schema's enum), and the rule of the two-pass tie-break.
ANSWERED_AS = "answered"
CONTEXT_METHOD = "rule"
INFER_METHOD = "inferred"
TIE_RULE = "reading.tie_break"
# Pass before P5 (17 Oct 2026, module docstring): the reason of a type both twins' AI passes named.
TWIN_TIE_NOTE = "the AI passes of its twin {twin} in the twin room {room} named it too: the twins get one type"
# 26 Oct 2026 (module docstring "Reading fixes of 26 Oct 2026"): nested outlines of one piece, a generic room name,
# two answers of one functional group, a kitchen run drawn as one outline.
NEST_INSIDE = 0.8                  # >= 80 % of the smaller footprint inside the bigger one ...
NEST_CENTRE_M = 0.10               # ... the centres this close ...
NEST_AREA_MIN = 0.4                # ... the smaller at least this share of the bigger's area ...
NEST_LONG_MIN = 0.75               # ... and of its long side: two outlines of one piece (not a sink in its counter)
NEST_RANK = {"block_name": 4, "name_text": 4, "ai_two_pass": 3, "rule": 2, "twin": 2, "level": 2, "block": 2,
             "same_block": 2}
NAME_TEXT_SAME_M = 0.05            # one name text read on two pages of a level (the same type this close) is one text
NEST_RULE = "reading.nested_outlines"
GENERIC_ROOM_RULE = "reading.generic_room"
GENERIC_STRONG = ("ai_two_pass", "block_name")   # the anchors a generic room name follows
GENERIC_BEDS = ("bed_double", "bed_single", "bunk_bed", "crib")
BEDROOM_NAMED = ("dresser", "nightstand") + GENERIC_BEDS   # a name text of these in the room: the bedroom stands
GROUP_TIE_RULE = "reading.group_member_tie"
RUN_DEPTH_RULE = "reading.run_depth"
HOLDS_HINTS = {"sink_kitchen": "sink_pos_m", "stove": "hob_pos_m"}   # modules.plan_kitchen_run's hints
KITCHEN_OUTLINE_RULE = "reading.kitchen_outline"
KITCHEN_OUTLINE_MIN_M = 0.75       # a kitchen outline is deeper than a counter both ways
# 28 Oct 2026 (real06 run 154514: the outline stopped 0.58 m short of the west wall, where the sink stands under the
# window; the sink was built as a lone 0.45 m box beside two counter legs): an outline side this close to a wall, with a
# drawn kitchen fixture in the gap, is extended to the wall (the run reaches it: one more leg, the fixture built in)
KITCHEN_OUTLINE_GAP_M = 0.9
KITCHEN_GAP_TYPES = ("sink_kitchen", "stove", "fridge", "kitchen_counter")
KITCHEN_GAP_SHARE = 0.5            # the fixture's footprint share inside the gap
FIXED_SEAT_TYPES = FS.SEAT_TYPES   # 27 Oct 2026: the fixed pieces that stand on a wall on their own (fixture_seat)


# --------------------------------------------------------------------------
# Small geometry helpers (building frame)
# --------------------------------------------------------------------------

def rect(item: dict) -> Polygon:
    """The footprint rectangle of a building piece."""
    return rect_fp(item["footprint"])


def rect_fp(fp: dict) -> Polygon:
    """The rectangle of a footprint ``{center, size, rotation_deg}``."""
    cx, cy = (float(v) for v in fp["center"])
    w, d = (float(v) for v in fp["size"][:2])
    t = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(t), math.sin(t)
    pts = [(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2),
                                                                 (-w / 2, d / 2))]
    poly = Polygon(pts)
    return poly if poly.area > 0 else poly.buffer(1e-4)


def front_vec(front_deg: float) -> tuple[float, float]:
    return math.cos(math.radians(front_deg)), math.sin(math.radians(front_deg))


def snap_front(item: dict, deg: float) -> float:
    """``deg`` snapped to the nearest of the footprint's four side normals."""
    base = G.front_direction_deg(float(item["footprint"].get("rotation_deg") or 0.0))
    k = round(G.normalise_angle(deg - base) / 90.0) % 4
    return round(G.normalise_angle(base + 90.0 * k), 3)


def sides(poly: Polygon) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    c = list(poly.exterior.coords)
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


def wall_sides(item: dict, ring) -> list[int]:
    """Indices of the footprint sides lying on the room outline (within ``WALL_SIDE_M`` at 20 %, 50 %, 80 %)."""
    out = []
    for k, (a, b) in enumerate(sides(rect(item))):
        pts = [(a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t) for t in (0.2, 0.5, 0.8)]
        if all(ring.distance(Point(p)) <= WALL_SIDE_M for p in pts):
            out.append(k)
    return out


def outward_deg(item: dict, side) -> float:
    cx, cy = item["footprint"]["center"]
    mx, my = (side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0
    return math.degrees(math.atan2(my - cy, mx - cx)) % 360.0


def room_ring(room: dict):
    poly = Polygon(room["polygon"])
    poly = poly if poly.is_valid else poly.buffer(0)
    return poly.exterior if poly.geom_type == "Polygon" else max(poly.geoms, key=lambda g: g.area).exterior


def _ev(item: dict, rule: str, text: str, confidence: float = 0.7, method: str = "inferred") -> dict:
    src = (item.get("evidence") or [{}])[0]
    ev = B.evidence(src.get("file") or "building.json", method, confidence, rule=rule, text=text)
    for k in ("page", "entity", "region_id"):
        if src.get(k) is not None:
            ev[k] = src[k]
    return ev


def _crop(item_details: Optional[dict]) -> Optional[str]:
    """The plan crop of a piece's question (``recognition/crops/<key>_ctx.png``). Fix round after P3: a secondary
    page's crops are in its own folder (``details["crop_dir"]``, set by the pipeline), never the asked page's crop
    of the same key."""
    key = (item_details or {}).get("candidate_key")
    return f"{(item_details or {}).get('crop_dir') or CROP_DIR}/{key}_ctx.png" if key else None


def _not_asked(w) -> bool:
    """Fix round after P3: True for a page whose questions are never asked (``NOT_ASKED_KEY`` in its report)."""
    report = getattr(getattr(w, "extraction", None), "report", None)
    return isinstance(report, dict) and bool(report.get(NOT_ASKED_KEY))


def _works(build, works: dict, asked_only: bool = False) -> list:
    """The page works of a reading run, each once (``works`` and ``build.generic``). Fix round after P3: the pages whose
    questions are never asked come first (so an asked page's item wins in ``_items``), or are left out
    (``asked_only``)."""
    out, seen = [], set()
    for w in list((works or {}).values()) + list(getattr(build, "generic", []) or []):
        if id(w) in seen:
            continue
        seen.add(id(w))
        out.append(w)
    if asked_only:
        return [w for w in out if not _not_asked(w)]
    return sorted(out, key=lambda w: 0 if _not_asked(w) else 1)


def _items(build, works: dict, asked_only: bool = False) -> dict:
    """Building piece id -> the core's FurnitureItem (its ``details`` carry what the strokes said). Fix round after
    P3: a piece two pages drew maps to the item of the page whose questions are asked (the master), not to the
    secondary page's item of the same piece (another candidate key, another crop); ``asked_only`` leaves the
    secondary pages out."""
    out = {}
    for w in _works(build, works, asked_only):
        for f in getattr(w.extraction, "furniture", []) or []:
            if getattr(f, "element_id", None):
                out[f.element_id] = f
    return out


def _pending(build, works: dict) -> set[str]:
    """Pieces whose AI question still waits for its answers: nothing is decided for them before. A page that got
    answers in this round waits for none of its questions (a question without answers there was not asked in that
    round: the pipeline lists it as unanswered, nothing waits for it). Fix round after P3: a page whose questions
    are never asked (``NOT_ASKED_KEY``: a secondary page of its level) waits for none of them either."""
    out = set()
    for w in _works(build, works, asked_only=True):
        report = w.extraction.report or {}
        if report.get("answers_applied"):
            continue
        pending = set(report.get("pending") or [])
        for f in getattr(w.extraction, "furniture", []) or []:
            if f.details.get("candidate_key") in pending and getattr(f, "element_id", None):
                out.add(f.element_id)
    return out


def _next_symbol_id(b: dict, level_id: str) -> str:
    used = {s.get("id") for s in b.get("symbols") or []}
    n = sum(1 for s in b.get("symbols") or [] if s.get("level_id") == level_id) + 1
    while f"sy_{level_id}_{n:03d}" in used:
        n += 1
    return f"sy_{level_id}_{n:03d}"


def _room_at(b: dict, level_id: str, point) -> Optional[str]:
    pt = Point(point)
    for r in b.get("rooms") or []:
        if r.get("level_id") == level_id and len(r.get("polygon") or []) >= 3 and Polygon(r["polygon"]).contains(pt):
            return r["id"]
    return None


# --------------------------------------------------------------------------
# 1. Symbols
# --------------------------------------------------------------------------

def move_symbols(build, items: dict, works: dict) -> dict:
    """Step 1 (see the module docstring). Returns counts by kind."""
    from wenart.levels import marks as LM

    b = build.building
    b.setdefault("symbols", [])
    counts: dict[str, int] = {}
    keep = []
    for f in b["furniture"]:
        item = items.get(f["id"])
        det = item.details if item is not None else {}
        found = det.get("symbol")
        if found is None and f["type"] == "unknown" and _is_mark(f, det, LM):
            found = {"kind": "level_mark", "reason": "a level mark among the furniture (the level step did not take "
                                                    "it): never furniture"}
        nf = det.get("not_furniture")
        if found is None and nf is not None:
            keep.append(f)
            if f.get("build") is not False:
                f["build"] = False
                f["inferred"] = True
                f["inferred_as"] = nf["as"]
                f["inferred_reason"] = nf["reason"] + (" (kept as an obstacle, not built)" if nf["as"] == "column"
                                                       else " (the decor stage places decor)")
                f.setdefault("evidence", []).append(_ev(f, SYMBOL_RULE, f["inferred_reason"]))
                build.warn(f"{f['id']}: not furniture ({nf['as']}): {nf['reason']}; not built")
                counts[nf["as"]] = counts.get(nf["as"], 0) + 1
            continue
        if found is None:
            keep.append(f)
            continue
        sym_id = _next_symbol_id(b, f["level_id"])
        reason = found["reason"]
        if f["type"] != "unknown" and f.get("type_method") == "ai_two_pass":
            reason += f" (both AI passes said {f['type']}: the drawing outranks them)"
            build.conflict("type_disagreement", [sym_id],
                           f"{f['id']}: the AI passes typed it {f['type']}, the drawing shows a {found['kind']} "
                           f"({found['reason']})", "moved to building.symbols (trust order: vector geometry > AI)")
        b["symbols"].append({"id": sym_id, "kind": found["kind"], "level_id": f["level_id"],
                             "room_id": f.get("room_id"), "footprint": copy.deepcopy(f["footprint"]),
                             "former_piece_id": f["id"], "reason": reason, "crop": _crop(det),
                             "evidence": list(f.get("evidence") or []) + [_ev(f, SYMBOL_RULE, reason, 0.9)]})
        build.warn(f"{f['id']}: not furniture ({found['kind']}): {reason}; moved to the symbols ({sym_id})")
        counts[found["kind"]] = counts.get(found["kind"], 0) + 1
    b["furniture"] = keep
    for w in list(getattr(build, "furniture_works", []) or []):
        ex = w.extraction
        level_id = ex.level_id
        for sym in (ex.report or {}).get("symbols") or []:
            if sym.get("_moved"):
                continue
            sym["_moved"] = True
            sym_id = _next_symbol_id(b, level_id)
            b["symbols"].append({"id": sym_id, "kind": sym["kind"], "level_id": level_id,
                                 "room_id": _room_at(b, level_id, sym["center"]),
                                 "footprint": {"center": list(sym["center"]), "size": list(sym["size"]),
                                               "rotation_deg": sym["rotation_deg"]},
                                 "former_piece_id": None, "reason": sym["reason"], "crop": None,
                                 "evidence": list(sym["evidence"])})
            counts[sym["kind"]] = counts.get(sym["kind"], 0) + 1
    return counts


def log_overrides(build, items: dict) -> int:
    """The core's re-read typed a piece against the AI passes (a block name the M12 words read, a table with chairs
    drawn around it): a ``type_disagreement`` conflict, resolved for the drawing (CLAUDE.md trust order)."""
    n = 0
    for f in build.building["furniture"]:
        item = items.get(f["id"])
        over = (item.details.get("ai_overridden") if item is not None else None) or {}
        if not over:
            continue
        build.conflict("type_disagreement", [f["id"]],
                       f"{f['id']}: the AI passes typed it {over['type']}; {over['reason']}",
                       f"typed {f['type']} (trust order: vector geometry and block names > AI)")
        n += 1
    return n


def _is_mark(f: dict, det: dict, LM) -> bool:
    raw = f.get("type_raw") or ""
    if any(LM.parse_mark(part) for part in raw.split("/") if part):
        return True
    return False


# --------------------------------------------------------------------------
# 1b. Copies of one block drawing
# --------------------------------------------------------------------------

def copies(build, items: dict, pending=(), typed_from: Optional[dict] = None) -> int:
    """Pieces drawn by the same entities of the same block definition in different inserts of it (``copy_keys``:
    real03's four 1+1 B flats are one block inserted four times) are the same piece: an untyped copy takes the type
    its typed copies agree on, and a copy of symbols becomes a symbol too. Returns the number of pieces changed.
    Fix round after P4b: ``typed_from`` (a dict) receives ``{typed copy id: [the ids of the copies it took its type
    from]}`` (``code_first`` resets a copy of a piece the answers typed)."""
    b = build.building
    groups: dict[str, list[str]] = {}
    for pid, item in sorted(items.items()):
        for key in item.details.get("copy_keys") or []:
            groups.setdefault(key, []).append(pid)
    by_id = {f["id"]: f for f in b["furniture"]}
    sym_of = {s.get("former_piece_id"): s for s in b.get("symbols") or [] if s.get("former_piece_id")}
    changed = 0
    for key in sorted(groups):
        ids = groups[key]
        if len(ids) < 2:
            continue
        typed = [by_id[i] for i in ids if i in by_id and by_id[i]["type"] != "unknown"
                 and by_id[i].get("build") is not False]
        loose = [by_id[i] for i in ids if i in by_id and by_id[i]["type"] == "unknown"
                 and by_id[i].get("build") is not False and i not in pending]
        syms = [sym_of[i] for i in ids if i in sym_of]
        if not loose:
            continue
        if syms and not typed and len({s["kind"] for s in syms}) == 1:
            former = ", ".join(sorted(s["former_piece_id"] for s in syms))
            for f in loose:
                det = items[f["id"]].details
                det["symbol"] = {"kind": syms[0]["kind"],
                                 "reason": f"drawn by the same block entities as {former} ({syms[0]['kind']}): "
                                           f"{syms[0]['reason']}"}
                changed += 1
            continue
        kinds = {f["type"] for f in typed}
        if len(kinds) != 1:
            continue
        ftype = kinds.pop()
        mates = ", ".join(sorted(t["id"] for t in typed))
        for f in loose:
            if not _same_size(f, typed[0], 0.02):
                continue
            _set_type(build, f, ftype, f"drawn by the same block entities as {mates} (typed {ftype}): the same "
                      "piece in another insert of the block", confidence=0.8)
            if typed_from is not None:
                typed_from[f["id"]] = sorted(t["id"] for t in typed)
            changed += 1
    if changed:
        move_symbols(build, items, {})
    return changed


# --------------------------------------------------------------------------
# 2. Context typing
# --------------------------------------------------------------------------

def _set_type(build, f: dict, ftype: str, reason: str, front: Optional[float] = None,
              confidence: float = 0.75) -> None:
    from wenart.furniture import infer as INF

    # Typed from its neighbours: an inference (CLAUDE.md), so the piece keeps its ``status`` and carries ``inferred``
    # with its reason (listed in the report). Fix round after P4b: an untyped piece's ``type_method`` becomes
    # ``CONTEXT_METHOD`` (a reading rule of the drawing), so the rules keyed on the method see it typed.
    old = f["type"]
    f["type"] = ftype
    if f.get("type_method") in (None, "none"):
        f["type_method"] = CONTEXT_METHOD
    f["inferred"] = True
    f["inferred_reason"] = reason
    f.setdefault("evidence", []).append(_ev(f, CONTEXT_RULE, reason, confidence))
    if front is not None:
        INF.set_front(f, front)
    build.warn(f"{f['id']}: {old} -> {ftype} by context: {reason}")


def _unknowns(pieces: list[dict], pending=()) -> list[dict]:
    """The pieces a context rule may type: unknown, built, drawn, and not in ``pending``. Build round 3 (K3, lead
    decision): the passes of ``read_furniture`` before the size inference give no pending set: a context rule is
    code and types a piece whose AI question still waits as well (the question is then withdrawn,
    ``context_typed``); the last pass, after the size inference, keeps the Milestone 12 behaviour (``pending``
    waits, nothing is withdrawn)."""
    return [f for f in pieces if f["type"] == "unknown" and f.get("build") is not False
            and f.get("source", "from_documents") == "from_documents" and f["id"] not in pending]


def context_typed(build, before: dict) -> dict[str, str]:
    """Build round 3 (K3): the pieces a ``context_types`` pass typed, ``{piece id: "context:<type>"}``, from the
    unknown pieces ``before`` the pass (``unknown_ids``: id -> piece): a piece that now has a type, or that the pass
    recorded as a detail of another piece (the counter under a washbasin: ``context:vanity``). The caller withdraws
    their questions like the code-typed ones."""
    out = {}
    for f in build.building["furniture"]:
        if f["id"] not in before:
            continue
        if f.get("type") != "unknown":
            out[f["id"]] = f"context:{f['type']}"
        elif f.get("build") is False and f.get("inferred_as") == "detail":
            out[f["id"]] = "context:vanity"
    return out


def unknown_ids(build) -> dict[str, dict]:
    """The unknown drawn built pieces before a typing pass (for ``context_typed``)."""
    return {f["id"]: f for f in _unknowns(build.building["furniture"])}


def _facing(seat: dict, other: Polygon) -> Optional[tuple[float, float, float]]:
    """(distance from the seat's front edge, lateral offset, angle off the axis in deg) of ``other`` seen from the
    seat's front, or None when the seat has no front or ``other`` lies behind it."""
    if seat.get("front_deg") is None:
        return None
    fx, fy = front_vec(float(seat["front_deg"]))
    cx, cy = seat["footprint"]["center"]
    depth = float(seat["footprint"]["size"][1])
    o = other.centroid
    dx, dy = o.x - cx, o.y - cy
    along = dx * fx + dy * fy - depth / 2.0
    across = -dx * fy + dy * fx
    if along <= 0:
        return None
    return along, across, abs(math.degrees(math.atan2(across, along + depth / 2.0)))


def _corner_sofas(build, items: dict, room: dict, pieces: list[dict], pending=()) -> list[dict]:
    """The corner-sofa context rule on one room (an L outline with seat-deep arms in a living room, away from the
    kitchen run): the pieces it typed ``sofa_corner`` with their L. Fix round after P5: ``corner_sofa_pass`` runs it
    before the first code typing too."""
    from wenart.furniture import sizes

    built = [f for f in pieces if f.get("build") is not False]
    kitchen = [f for f in built if f["type"] in KITCHEN_ZONE_TYPES]
    out = []
    for f in _unknowns(pieces, pending):
        det = items[f["id"]].details if f["id"] in items else {}
        lo = det.get("l_outline")
        if lo and room.get("room_type") == "living" and sizes.fits("sofa_corner", tuple(f["footprint"]["size"])) \
                and min(lo["seat_depth"], lo["chaise_width"]) >= L_SEAT_MIN_M and not any(
                    rect(k).distance(rect(f)) <= 0.15 for k in kitchen):
            front = det.get("l_front")
            _set_type(build, f, "sofa_corner", "an L outline with 0.5-1.3 m deep arms in a living room (a corner "
                      "sofa; the open inner corner is its front)", float(front) if front is not None else None)
            f.update(shape="L", chaise_side=lo["chaise_side"], chaise_depth=lo["chaise_depth"],
                     seat_depth=lo["seat_depth"], chaise_width=lo["chaise_width"])
            out.append(f)
    return out


def corner_sofa_pass(build, items: dict) -> list[str]:
    """Fix round after P5 (module docstring): the corner-sofa rule of ``context_types`` on every room, before the
    first code typing, so the room's seating anchor is there when ``infer.code_types`` looks for missing members.
    Returns the typed ids."""
    b = build.building
    out = []
    for room in sorted((r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3), key=lambda r: r["id"]):
        pieces = [f for f in b["furniture"] if f.get("room_id") == room["id"]]
        out += [f["id"] for f in _corner_sofas(build, items, room, pieces)]
    return out


def context_types(build, items: dict, pending=()) -> dict:
    """Step 2 (see the module docstring). Returns counts by rule."""
    from wenart.furniture import sizes

    b = build.building
    counts: dict[str, int] = {}

    def bump(k):
        counts[k] = counts.get(k, 0) + 1

    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    for rid, room in sorted(rooms.items()):
        pieces = [f for f in b["furniture"] if f.get("room_id") == rid]
        if not pieces:
            continue
        ring = room_ring(room)
        built = [f for f in pieces if f.get("build") is not False]
        # Corner sofa: an L outline with seat-deep arms (0.65-1.3 m, generic core ``l_shape``) in a living room, not
        # touching the kitchen run (a counter is an L of 0.6 m deep legs).
        for _f in _corner_sofas(build, items, room, pieces, pending):
            bump("sofa_corner")
        # Fridge: a box drawn with its door swing beside the kitchen run.
        kitchen = [f for f in built if f["type"] in ("kitchen_counter", "sink_kitchen", "stove", "kitchen_island")]
        doors = [rect_fp(s["footprint"]) for s in b.get("symbols") or [] if s.get("kind") == "door_arc"
                 and s.get("room_id") == rid and s.get("footprint")]
        legs = [k for k in kitchen if k["type"] == "kitchen_counter"]
        for f in _unknowns(pieces, pending):
            det = items[f["id"]].details if f["id"] in items else {}
            poly = rect(f)
            if not (kitchen and sizes.fits("fridge", tuple(f["footprint"]["size"]))):
                continue
            door = det.get("door") or any(d.distance(poly) <= DOOR_NEAR_M for d in doors)
            depth = min(f["footprint"]["size"])
            proud = [k for k in legs if poly.distance(rect(k)) <= 0.10 and
                     depth >= min(k["footprint"]["size"]) + 0.05]
            why = None
            if door and min(poly.distance(rect(k)) for k in kitchen) <= FRIDGE_REACH_M:
                why = "a box drawn with its door swing beside the kitchen run (a fridge)"
            elif proud and wall_sides(f, ring):
                why = (f"a {depth:.2f} m deep box at a wall closing the counter run {proud[0]['id']} and standing "
                       "proud of it (a fridge)")
            if why:
                near = wall_sides(f, ring)
                front = (outward_deg(f, sides(poly)[near[0]]) + 180.0) % 360.0 if len(near) == 1 else None
                _set_type(build, f, "fridge", why, snap_front(f, front) if front is not None else None)
                bump("fridge")
        # Counter: a 0.5-0.75 m deep strip along a wall holding a sink or a hob.
        fixtures = [f for f in built if f["type"] in ("sink_kitchen", "stove")]
        for f in _unknowns(pieces, pending):
            w, d = sorted(f["footprint"]["size"], reverse=True)
            if not (COUNTER_DEPTH_M[0] <= d <= COUNTER_DEPTH_M[1] and w >= 0.9):
                continue
            near = wall_sides(f, ring)
            poly = rect(f)
            held = [x for x in fixtures if rect(x).intersection(poly).area >= 0.5 * rect(x).area]
            long_sides = [k for k in near if abs(math.dist(*sides(poly)[k]) - w) < 1e-3]
            if held and long_sides:
                front = (outward_deg(f, sides(poly)[long_sides[0]]) + 180.0) % 360.0
                _set_type(build, f, "kitchen_counter", f"a {d:.2f} m deep strip along the wall holding "
                          f"{', '.join(x['id'] for x in held)}: the counter run", snap_front(f, front))
                bump("kitchen_counter")
        # Nightstands: small squares beside a bed's head.
        beds = [f for f in built if f["type"] in ("bed_double", "bed_single") and f.get("front_deg") is not None]
        for f in _unknowns(pieces, pending):
            w, d = sorted(f["footprint"]["size"], reverse=True)
            if not (NIGHTSTAND_M[0] / 1.15 <= d and w <= NIGHTSTAND_M[1] * 1.15):
                continue
            for bed in beds:
                where = _beside_head(bed, rect(f))
                if where is not None:
                    _set_type(build, f, "nightstand", f"a {w:.2f} x {d:.2f} m square beside the head of {bed['id']}",
                              snap_front(f, float(bed["front_deg"])))
                    bump("nightstand")
                    break
        # Dining table: a table-sized piece with seat-sized pieces drawn around it on two or more of its sides
        # (docs/milestone12.md §4.1: "chairs around a rectangle -> dining table + chairs"; real01 --no-ai).
        for f in _unknowns(pieces, pending):
            if not sizes.fits("table_dining", tuple(f["footprint"]["size"])):
                continue
            poly = rect(f)
            seats = [g for g in _unknowns(pieces, pending) if g is not f and _seat_sized(g)
                     and rect(g).distance(poly) <= CHAIR_REACH_M]
            sides_hit = {_side_of(f, rect(g)) for g in seats}
            if len(seats) >= DINING_SEATS_MIN and len(sides_hit) >= 2:
                _set_type(build, f, "table_dining", f"a {f['footprint']['size'][0]:.2f} x "
                          f"{f['footprint']['size'][1]:.2f} m table with {len(seats)} seats drawn around it on "
                          f"{len(sides_hit)} sides: a dining table")
                bump("table_dining")
        built = [f for f in pieces if f.get("build") is not False]
        # Chairs: small pieces (a seat, or the half-round back drawn alone) around a dining table face it.
        tables = [f for f in built if f["type"] in ("table_dining", "kitchen_island")]
        for f in _unknowns(pieces, pending):
            w, d = sorted(f["footprint"]["size"], reverse=True)
            if not (CHAIR_SIDE_M[0] <= w <= CHAIR_SIDE_M[1] and d >= 0.12):
                continue
            det = items[f["id"]].details if f["id"] in items else {}
            if (f.get("shape") or det.get("shape")) == "round":
                continue            # 26 Oct 2026 (user): a round shape is never a chair (real06 f_L1_026, a table)
            poly = rect(f)
            near = [t for t in tables if rect(t).distance(poly) <= CHAIR_REACH_M]
            if not near:
                continue
            host = min(near, key=lambda t: (round(rect(t).distance(poly), 6), t["id"]))
            c = rect(host).centroid
            deg = math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x))
            _set_type(build, f, "chair", f"a {w:.2f} x {d:.2f} m seat {rect(host).distance(poly):.2f} m from the table "
                      f"{host['id']}, facing it", snap_front(f, deg))
            depth = float(f["footprint"]["size"][1])
            if depth < CHAIR_DEPTH_M:
                # The half-round back drawn alone: the seat reaches towards the table (as the M11 chair split).
                fx, fy = front_vec(float(f["front_deg"]))
                shift = (CHAIR_DEPTH_M - depth) / 2.0
                cx, cy = f["footprint"]["center"]
                f["footprint"] = dict(f["footprint"], center=[round(cx + fx * shift, 4), round(cy + fy * shift, 4)],
                                      size=[f["footprint"]["size"][0], CHAIR_DEPTH_M])
            bump("chair")
        # Washbasin: a bowl with its drain in a bathroom or WC; the counter (vanity) it stands on is part of it.
        if room.get("room_type") in ("bathroom", "wc"):
            for f in _unknowns(pieces, pending):
                det = items[f["id"]].details if f["id"] in items else {}
                if det.get("drain") and sizes.fits("washbasin", tuple(f["footprint"]["size"])):
                    _set_type(build, f, "washbasin", "a bowl with its drain in a bathroom: the washbasin")
                    bump("washbasin")
            basins = [f for f in pieces if f["type"] == "washbasin" and f.get("build") is not False]
            for f in _unknowns(pieces, pending):
                poly = rect(f)
                host = next((x for x in basins if poly.intersection(rect(x)).area >= VANITY_SHARE *
                             min(poly.area, rect(x).area)), None)
                w, d = sorted(f["footprint"]["size"], reverse=True)
                if host is not None and d <= 0.7:
                    reason = (f"the counter the washbasin {host['id']} stands on (a vanity): part of it, not a piece "
                              "of its own (not built)")
                    f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason)
                    f.setdefault("evidence", []).append(_ev(f, CONTEXT_RULE, reason))
                    build.warn(f"{f['id']}: {reason}")
                    bump("vanity")
        # Armchairs: two seat-sized pieces of one size on opposite sides of a coffee table face it.
        coffee = [f for f in pieces if f["type"] == "table_coffee" and f.get("build") is not False]
        for t in coffee:
            tp = rect(t)
            near = [f for f in _unknowns(pieces, pending) if sizes.fits("armchair", tuple(f["footprint"]["size"]))
                    and rect(f).distance(tp) <= ARMCHAIR_REACH_M]
            for f in near:
                c, fc = tp.centroid, rect(f).centroid
                mate = next((g for g in near if g is not f and _same_size(f, g) and
                             ((g["footprint"]["center"][0] - c.x) * (fc.x - c.x) +
                              (g["footprint"]["center"][1] - c.y) * (fc.y - c.y)) < 0), None)
                if mate is None or f["type"] != "unknown":
                    continue
                for g in (f, mate):
                    if g["type"] != "unknown":
                        continue
                    gc = rect(g).centroid
                    deg = math.degrees(math.atan2(c.y - gc.y, c.x - gc.x))
                    _set_type(build, g, "armchair", f"one of two {g['footprint']['size'][0]:.2f} x "
                              f"{g['footprint']['size'][1]:.2f} m seats on opposite sides of the coffee table "
                              f"{t['id']}, facing it", snap_front(g, deg))
                    bump("armchair")
        # Coffee table and TV unit: in front of a sofa (or in the open corner of an L sofa).
        seats = [f for f in built if f["type"] in SEAT_TYPES and f.get("front_deg") is not None]
        for f in _unknowns(pieces, pending):
            size = tuple(f["footprint"]["size"])
            poly = rect(f)
            notch = next((s for s in seats if s.get("shape") == "L" and sizes.fits("table_coffee", size) and
                          poly.intersection(rect(s)).area >= 0.4 * poly.area and
                          poly.intersection(_l_body(s)).area <= 0.2 * poly.area), None)
            if notch is not None:
                _set_type(build, f, "table_coffee", f"a {size[0]:.2f} x {size[1]:.2f} m table in the open corner of "
                          f"the L sofa {notch['id']}")
                bump("table_coffee")
                continue
            for seat in seats:
                rel = _facing(seat, poly)
                if rel is None:
                    continue
                along, across, angle = rel
                half = float(seat["footprint"]["size"][0]) / 2.0
                if sizes.fits("table_coffee", size) and COFFEE_FRONT_M[0] <= along - min(size) / 2 <= \
                        COFFEE_FRONT_M[1] and abs(across) <= half:
                    _set_type(build, f, "table_coffee", f"a {size[0]:.2f} x {size[1]:.2f} m table {along:.2f} m in "
                              f"front of {seat['id']}")
                    bump("table_coffee")
                    break
                w, d = sorted(size, reverse=True)
                near = wall_sides(f, ring)
                if (TV_DEPTH_M[0] <= d <= TV_DEPTH_M[1] and TV_LENGTH_M[0] <= w <= TV_LENGTH_M[1] and near and
                        TV_DISTANCE_M[0] <= along <= TV_DISTANCE_M[1] and angle <= TV_AXIS_DEG):
                    back = sides(poly)[near[0]]
                    front = (outward_deg(f, back) + 180.0) % 360.0
                    _set_type(build, f, "tv_unit", f"a {w:.2f} x {d:.2f} m strip at the wall facing {seat['id']} "
                              f"{along:.2f} m away", snap_front(f, front))
                    bump("tv_unit")
                    break
    return counts


def _seat_sized(f: dict) -> bool:
    w, d = sorted(f["footprint"]["size"], reverse=True)
    return CHAIR_SIDE_M[0] <= w <= CHAIR_SIDE_M[1] and d >= 0.12


def _side_of(table: dict, poly: Polygon) -> int:
    """Which side of ``table`` (0 front -Y, 1 right +X, 2 back +Y, 3 left -X in its own frame) ``poly`` is at."""
    cx, cy = table["footprint"]["center"]
    w, d = (float(v) for v in table["footprint"]["size"][:2])
    t = math.radians(float(table["footprint"].get("rotation_deg") or 0.0))
    dx, dy = poly.centroid.x - cx, poly.centroid.y - cy
    lx, ly = dx * math.cos(t) + dy * math.sin(t), -dx * math.sin(t) + dy * math.cos(t)
    if abs(lx) / max(w / 2.0, 1e-6) >= abs(ly) / max(d / 2.0, 1e-6):
        return 1 if lx > 0 else 3
    return 2 if ly > 0 else 0


def _same_size(f: dict, g: dict, tol: float = 0.05) -> bool:
    a, b_ = sorted(f["footprint"]["size"]), sorted(g["footprint"]["size"])
    return all(abs(x - y) <= tol + 1e-9 for x, y in zip(a, b_))


def _l_body(seat: dict) -> Polygon:
    """The two arms of an L corner sofa (``schemas.l_parts``) as one polygon, building frame; its box without one."""
    from wenart.furniture import schemas

    fp = seat["footprint"]
    parts = schemas.l_parts(fp["size"], seat.get("chaise_side"), seat.get("chaise_depth"), seat.get("seat_depth"),
                            seat.get("chaise_width"))
    cx, cy = (float(v) for v in fp["center"])
    t = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(t), math.sin(t)
    polys = []
    for x0, x1, y0, y1 in parts:
        polys.append(Polygon([(cx + c * x - s * y, cy + s * x + c * y) for x, y in ((x0, y0), (x1, y0), (x1, y1),
                                                                                    (x0, y1))]))
    return unary_union(polys)


def _beside_head(bed: dict, poly: Polygon) -> Optional[str]:
    """'left' / 'right' when ``poly`` stands beside the bed's head (within ``NIGHTSTAND_GAP_M`` of a long side and
    ``NIGHTSTAND_HEAD_M`` of the head edge), else None."""
    fx, fy = front_vec(float(bed["front_deg"]))
    cx, cy = bed["footprint"]["center"]
    w, d = (float(v) for v in bed["footprint"]["size"][:2])
    o = poly.centroid
    dx, dy = o.x - cx, o.y - cy
    along = dx * fx + dy * fy              # + towards the foot
    across = -dx * fy + dy * fx
    head = -d / 2.0
    if not (head - 0.1 <= along <= head + NIGHTSTAND_HEAD_M):
        return None
    gap = abs(across) - w / 2.0
    if gap < -0.05 or gap > NIGHTSTAND_GAP_M + 0.35:
        return None
    if poly.distance(rect(bed)) > NIGHTSTAND_GAP_M:
        return None
    return "left" if across > 0 else "right"


def duplicates(build) -> int:
    """Two fixed pieces of one type where one lies >= 60 % inside the other are one piece drawn twice (real03: the hob
    inside the OCAK block, typed stove by both passes; the dishwasher block inside the counter leg): the one that
    goes is the smaller, or of two about equal ones (area within 30 %) the one not named by its block. Not built
    (``detail``). Returns the number of duplicates."""
    from wenart.furniture import schemas

    b = build.building
    pieces = [f for f in b["furniture"] if f.get("build") is not False and f["type"] in schemas.FIXED_TYPES
              and f["type"] != "stair"]
    n = 0
    for f in pieces:
        if f.get("build") is False:
            continue
        poly = rect(f)
        host = None
        for h in pieces:
            if h is f or h.get("build") is False or h["type"] != f["type"] or h.get("room_id") != f.get("room_id"):
                continue
            if poly.intersection(rect(h)).area < DUPLICATE_SHARE * poly.area:
                continue
            ha, fa = rect(h).area, poly.area
            similar = max(ha, fa) <= 1.3 * min(ha, fa)
            named_h = h.get("type_method") == "block_name"
            named_f = f.get("type_method") == "block_name"
            if (similar and named_h and not named_f) or (not similar and ha > fa) or \
                    (similar and named_h == named_f and h["id"] < f["id"]):
                host = h
                break
        if host is None:
            continue
        reason = (f"drawn inside the {host['type']} {host['id']} ({DUPLICATE_SHARE:.0%} or more of it): the same "
                  "piece drawn twice, or a part of it (not built)")
        f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason)
        f.setdefault("evidence", []).append(_ev(f, CONTEXT_RULE, reason, 0.8))
        build.warn(f"{f['id']}: {reason}")
        n += 1
    return n


# --------------------------------------------------------------------------
# 3. Inference
# --------------------------------------------------------------------------

def infer(build, pending: set[str]) -> tuple[int, list[str]]:
    """Step 3: ``wenart.furniture.infer`` on what is still unknown (the conflicts read so far count: a face holding
    two room names allows the types of both). Returns ``(proposals applied, ids typed by code)``.

    Milestone 13 (K3, "code first, the AI types the rest"): a code-typed proposal (``type_method`` in
    ``infer.CODE_TYPE_METHODS``) needs no AI answer, so it applies to a piece whose question still waits as well; the
    size / room / position rules keep waiting for the answers (``pending``). The caller withdraws the questions of
    the code-typed pieces (``withdraw_questions``)."""
    from wenart.furniture import infer as INF

    b = build.building
    view = dict(b, conflicts=list(b.get("conflicts") or []) + list(getattr(build, "raw_conflicts", []) or []))
    proposals = [p for p in INF.infer_types(view)
                 if p["piece_id"] not in pending or p.get("type_method") in INF.CODE_TYPE_METHODS]
    if not proposals:
        return 0, []
    b["furniture"] = INF.apply_inferences(b, proposals)["furniture"]
    mark_inferred(b, proposals)
    coded = []
    for p in proposals:
        if p.get("type_method") in INF.CODE_TYPE_METHODS:
            what = f"typed {p['type']} by code ({p['type_method']}, before any AI)"
            coded.append(p["piece_id"])
        else:
            what = "not built (rug or group outline)" if p.get("build") is False else f"inferred {p['type']}"
        build.warn(f"{p['piece_id']}: {what}: {p['reason']}")
    return len(proposals), coded


def mark_inferred(b: dict, proposals: list[dict]) -> int:
    """Fix round after P4b (module docstring): a piece the size inference typed (a proposal of
    ``infer.infer_types`` that is neither a code method nor a nightstand symbol, and that gave a furniture type)
    gets ``type_method: INFER_METHOD`` when it had none. Returns the number of pieces marked."""
    from wenart.furniture import infer as INF

    by_id = {f["id"]: f for f in b.get("furniture") or []}
    n = 0
    for p in proposals:
        if p.get("type_method") is not None or p.get("build") is False:
            continue
        f = by_id.get(p["piece_id"])
        if f is None or f.get("type") != p.get("type") or f.get("inferred_as"):
            continue
        if f.get("type_method") in (None, "none") and p.get("type") not in (None, "unknown", INF.OUTLINE_TYPE):
            f["type_method"] = INFER_METHOD
            n += 1
    return n


CODE_TYPED_KEY = "typed_by_code"      # the extraction report's list of question keys withdrawn by the code typing
CODE_METHODS_KEY = "typed_by_code_methods"   # ... and {key: method} (twin | level | block | group_member | context:<type>)
# Milestone 13 final pass (23 Oct 2026): the report's question keys without a full pair of answers, in every mode
# (``core._ask_and_apply``; ``pending`` is [] under --no-ai), subtracted by ``answered_keys``.
UNANSWERED_KEY = "unanswered"


def answer_typed(build, works: dict, items: dict, typed_from: Optional[dict] = None) -> set[str]:
    """Fix round after P4b (module docstring): the pieces typed only because of this round's answers: a piece of an
    asked page whose question was asked and answered in this round (``answered_keys``) and that has a type now, and
    (``typed_from``, from ``copies``) the block copies typed from such a piece. Empty without answers."""
    answered = answered_keys(build, works)
    if not answered:
        return set()
    by_id = {f["id"]: f for f in build.building.get("furniture") or []}
    asked = _items(build, works, asked_only=True)
    out = {pid for pid, item in asked.items() if str((item.details or {}).get("candidate_key")) in answered
           and (by_id.get(pid) or {}).get("type") not in (None, "unknown")}
    for pid, sources in sorted((typed_from or {}).items()):
        if set(sources) & out:
            out.add(pid)
    return out


def _first_reading_view(b: dict, reset) -> dict:
    """A copy of ``b`` where every piece in ``reset`` is untyped again, as the first reading saw it (``ANSWERED_AS``:
    code never types it in the copy)."""
    view = copy.deepcopy(b)
    for f in view.get("furniture") or []:
        if f.get("id") in reset:
            f.update(type="unknown", type_method="none", inferred_as=ANSWERED_AS)
    return view


def code_first(build, reset=()) -> tuple[list[str], dict[str, str]]:
    """Build round 3 (K3, lead decision): ``infer.code_types`` applied to the building before the context rules and
    before any AI (the twin room, another level, the block name, the room's missing group member), on every untyped
    drawn piece, the ones whose question waits included (code needs no answer). Returns the typed ids and
    ``{id: method}``; every typing is a warning.

    Fix round after P4b (module docstring): ``reset`` (``answer_typed``) are the pieces this round's answers typed;
    code reads a copy of the building where they are untyped again, as in the first reading, and only the proposals
    for pieces still untyped in the real building are applied (an AI type is never replaced)."""
    from wenart.furniture import infer as INF

    b = build.building
    view = dict(b, conflicts=list(b.get("conflicts") or []) + list(getattr(build, "raw_conflicts", []) or []))
    if reset:
        view = _first_reading_view(view, set(reset))
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    proposals = [p for p in INF.code_types(view) if p.get("type_method") in INF.CODE_TYPE_METHODS
                 and INF.untyped_drawn(by_id.get(p["piece_id"]) or {})]
    if not proposals:
        return [], {}
    b["furniture"] = INF.apply_inferences(b, proposals)["furniture"]
    methods = {}
    for p in proposals:
        methods[p["piece_id"]] = p["type_method"]
        build.warn(f"{p['piece_id']}: typed {p['type']} by code ({p['type_method']}, before the context rules and "
                   f"any AI): {p['reason']}")
    return list(methods), methods


def _reports(build, works: dict) -> list[dict]:
    """The page extraction reports of a reading run (each once). Fix round after P3: the reports of the pages whose
    questions are asked only (a secondary page's keys, never asked and numbered like the master's, decide nothing)."""
    out = []
    for w in _works(build, works, asked_only=True):
        report = getattr(w.extraction, "report", None)
        if isinstance(report, dict):
            out.append(report)
    return out


def answered_keys(build, works: dict) -> set[str]:
    """Build round 3 (K3): the question keys asked and answered in this round: on a page that got answers
    (``answers_applied``), its questions less the ones still without a complete pair (``pending``) and less the
    ones withdrawn (``typed_by_code``). ``withdraw_questions`` keeps these listed.

    Milestone 13 final pass (23 Oct 2026; pod P6c, verify:agent:0): also less the ones without a full pair of answers
    (``UNANSWERED_KEY``, which ``core._ask_and_apply`` records in every mode): with ``--answers --no-ai`` ``pending``
    is [], and every question of a page with answers counted as answered, so the --no-ai run kept the code-typed
    questions round 1 had withdrawn (real02's sofas f_L-1b_041 / 042 then took the late AI answers: kitchen island)."""
    out: set[str] = set()
    for report in _reports(build, works):
        if not report.get("answers_applied"):
            continue
        keys = {str(q.get("key")) for q in report.get("questions") or [] if q.get("key")}
        out |= keys - set(report.get("pending") or []) - set(report.get(CODE_TYPED_KEY) or []) \
            - {str(k) for k in report.get(UNANSWERED_KEY) or []}
    return out


def open_questions(build, works: dict, items: dict) -> set[str]:
    """Build round 3 (K3): the drawn pieces that are still unknown and carry a recognition question no answer of
    this round decided (``answered_keys``), in every mode: in a first plain run they are the pending ones; with
    --no-ai, and for the questions withdrawn in the first run when the answers come, nothing waits for them, but
    the steps before the size inference (the block copies, the first fronts) hold them like pending pieces, so
    what those steps type, and the questions the code and context typing withdraw, are the same in every mode."""
    keys: set[str] = set()
    for report in _reports(build, works):
        keys |= {str(q.get("key")) for q in report.get("questions") or [] if q.get("key")}
        keys |= {str(k) for k in report.get("pending") or []}
    keys -= answered_keys(build, works)
    by_id = {f["id"]: f for f in build.building.get("furniture") or []}
    # Fix round after P3: a piece only a secondary page drew has no asked question (its key may equal an asked one).
    asked = _items(build, works, asked_only=True)
    return {pid for pid, item in items.items()
            if pid in asked and str((item.details or {}).get("candidate_key")) in keys
            and (by_id.get(pid) or {}).get("type") == "unknown"}


def withdraw_questions(build, works: dict, items: dict, coded: list[str],
                       methods: Optional[dict] = None) -> dict[str, str]:
    """Milestone 13 (K3): the recognition questions of the pieces code typed (``coded``) are withdrawn: their keys
    leave every page report's ``pending`` (nothing waits for them) and go to ``report["typed_by_code"]`` and
    ``build.code_typed`` (key -> piece id), which the pipeline's ``_write_questions`` leaves out of
    ``recognition/requests.json``. Returns the withdrawn ``{key: piece id}`` (empty when no code-typed piece had a
    question, e.g. a piece typed from its block name at extraction time). Build round 3: ``methods`` (piece id ->
    ``twin | level | block | group_member | context:<type>``) is kept beside the keys in
    ``report["typed_by_code_methods"]`` and ``build.code_typed_methods`` (key -> method), so the report lists both
    kinds with their method; without ``methods`` the piece's ``type_method`` is used."""
    keys = {}
    answered = answered_keys(build, works)
    # Fix round after P3: a piece only a secondary page drew has no asked question to withdraw (its key, numbered like
    # the master's, would withdraw the master's question of another piece).
    asked = _items(build, works, asked_only=True)
    for pid in coded:
        key = (items[pid].details or {}).get("candidate_key") if pid in items and pid in asked else None
        if key and str(key) in answered:
            # Build round 3 (K3): a question asked and answered in this round stays listed (the code type stands
            # beside the AI's answer), so the run with the answers asks what the first run asked.
            build.warn(f"{pid}: recognition question {key} kept: it was asked and answered in this round (typed by "
                       "code as well)")
            continue
        if key:
            keys[str(key)] = pid
    if not keys:
        return {}
    by_id = {f["id"]: f for f in build.building.get("furniture") or []}
    how = {key: str((methods or {}).get(pid) or (by_id.get(pid) or {}).get("type_method") or "code")
           for key, pid in keys.items()}
    for w in _works(build, works, asked_only=True):
        report = w.extraction.report
        if report is None:
            continue
        asked = {q.get("key") for q in report.get("questions") or []} | set(report.get("pending") or [])
        mine = [k for k in keys if k in asked]
        if not mine:
            continue
        report["pending"] = [k for k in report.get("pending") or [] if k not in keys]
        report[CODE_TYPED_KEY] = sorted(set(report.get(CODE_TYPED_KEY) or []) | set(mine))
        report[CODE_METHODS_KEY] = dict(report.get(CODE_METHODS_KEY) or {}, **{k: how[k] for k in mine})
    store = getattr(build, "code_typed", None)
    if not isinstance(store, dict):
        store = build.code_typed = {}
    store.update(keys)
    store_how = getattr(build, "code_typed_methods", None)
    if not isinstance(store_how, dict):
        store_how = build.code_typed_methods = {}
    store_how.update(how)
    for key, pid in sorted(keys.items()):
        build.warn(f"{pid}: recognition question {key} withdrawn: typed by code before the AI ({how[key]}, K3)")
    return keys


# --------------------------------------------------------------------------
# 3b. Two AI passes that disagree (fix round after P4b)
# --------------------------------------------------------------------------

def room_misses(b: dict, room: dict) -> dict[str, str]:
    """Fix round after P4b (module docstring): ``{type: why}`` for the types ``room`` misses: the missing members of
    its drawn groups (``infer._group_wants``) and the anchors of its program's groups (``program._rows`` of the room
    kind, required or not) that no built piece of the room is."""
    from wenart.furniture import groups as GR, infer as INF, placer, program as PR

    out = {t: lines[0] for t, lines in sorted(INF._group_wants(b, room).items()) if lines}
    kind = PR.room_kind(b, room)
    present = {f.get("type") for f in b.get("furniture") or [] if f.get("room_id") == room["id"]
               and f.get("type") not in (None, "unknown") and f.get("build") is not False}
    templates = GR.load_groups()
    for group, _required, _opts in PR._rows(kind, PR._area(room), placer.room_context(b, room).polygon, b, room,
                                            room.get("room_subtype")):
        t = templates.get(group) or {}
        anchors = list((t.get("anchor") or {}).get("types") or []) if t.get("layout") == "anchored" else []
        if anchors and not set(anchors) & present:
            for a in anchors:
                out.setdefault(a, f"the {kind} room's {group} group has no {' or '.join(anchors)}")
    return out


def _named_types(f: dict) -> list[str]:
    """The different types the AI passes named for ``f`` (``type_candidates``), in pass order."""
    seen: list[str] = []
    for c in f.get("type_candidates") or []:
        t = c.get("type") if isinstance(c, dict) else None
        if t and t not in seen:
            seen.append(t)
    return seen


def _disagreeing_types(f: dict) -> list[str]:
    """The two different types the AI passes named for ``f`` (``type_candidates``), else []."""
    seen = _named_types(f)
    return seen if len(seen) == 2 else []


def _twins_of(view: dict, f: dict) -> list[tuple[dict, dict]]:
    """Pass before P5 (module docstring): ``(piece, its room)`` for the drawn pieces at ``f``'s spot in the twin rooms
    of ``f``'s room, typed or not: the twin rule's match (``infer._twin_type``: ``infer._twin_rooms``, the mirrored
    centre within ``infer.SAME_CENTRE_M``, the size within ``infer.SAME_FOOTPRINT_M``)."""
    from wenart.furniture import infer as INF
    from wenart.ingest import twins as TW

    room = INF._rooms(view).get(f.get("room_id") or "")
    if room is None or not f.get("footprint"):
        return []
    out = []
    for other, t in INF._twin_rooms(view, room):
        mapped = TW._apply(t, f["footprint"]["center"])
        for g in view.get("furniture") or []:
            if g.get("room_id") != other["id"] or g["id"] == f["id"] or g.get("source") != "from_documents" \
                    or not g.get("footprint"):
                continue
            if G.distance(mapped, tuple(g["footprint"]["center"])) <= INF.SAME_CENTRE_M + 1e-9 \
                    and INF._same_size(f, g):
                out.append((g, other))
    return out


def tie_break(build, items: dict, pending=(), deferred: Optional[set] = None) -> list[str]:
    """Fix round after P4b (module docstring): an untyped drawn piece whose two AI passes named two different
    furniture types, both fitting its drawn size (the size table, +15 %, and the type's shape) and both allowed in its
    room, is typed by code: the type the room misses (``room_misses``), else the one whose real product size is
    nearer (``infer._product_distance``; then the higher AI confidence, then the name). The piece is ``inferred``
    (``type_method: INFER_METHOD``, status kept), its evidence names the rule, both answers and the plan crop, and
    its ``symbol_type_disagreement`` conflict gets the decision as its resolution. Returns the typed ids.

    Pass before P5 (module docstring): twins are decided together (``_twins_of``). A piece whose twin is typed is left
    to the twin rule. With untyped twins, one of which at least the rule above could decide alone (two answers, both
    fitting; else all stay for review, as a single piece does), the one type that the passes of the piece and of
    every twin with answers named, that fits the drawn size and the room of each and that is no fixed type a room
    does not miss, goes to all of them (``TWIN_TIE_NOTE``); else the piece is decided as above (when it can be) and so
    is every twin whose passes named that type; the other twins are left to the twin rule.
    ``deferred`` (a set, filled when given) gets the ids left to the twin rule: the caller's ``code_first`` after this
    step types them."""
    from wenart.furniture import infer as INF, plausibility as PL, program as PR, schemas
    from wenart.furniture import sizes as SZ

    b = build.building
    raw = list(getattr(build, "raw_conflicts", []) or [])
    view = dict(b, conflicts=list(b.get("conflicts") or []) + raw)
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    later = deferred if deferred is not None else set()
    allowed: dict[str, set] = {}

    def fits(p: dict, t: str) -> bool:
        """``t`` fits the drawn size of ``p`` and is allowed in its room."""
        room = rooms.get(p.get("room_id") or "")
        if room is None or t not in schemas.SIZE_OPTIONS:
            return False
        if room["id"] not in allowed:
            allowed[room["id"]] = PL.allowed_in(view, room) | set(
                schemas.allowed_types(PR.room_kind(view, room), room.get("room_subtype")))
        size = [float(v) for v in p["footprint"]["size"]]
        return t in allowed[room["id"]] and SZ.fits(t, size, 0.15) and INF._shape_ok(t, size)

    def misses_of(p: dict) -> dict:
        """``room_misses`` of the room of ``p`` now (the pieces this step typed count)."""
        return room_misses(view, rooms[p["room_id"]])

    typed: list[str] = []
    for f in b["furniture"]:
        if f["id"] in pending or f["id"] in later or not INF.untyped_drawn(f) or f.get("room_id") not in rooms:
            continue
        pair = _disagreeing_types(f)
        if not pair:
            continue
        twins = [(g, r) for g, r in _twins_of(view, f) if g["id"] not in pending]
        if any(INF._typed_drawn(g) for g, _r in twins):
            later.add(f["id"])                  # pass before P5: its typed twin decides (the twin rule)
            continue
        twins = [(g, r) for g, r in twins if INF.untyped_drawn(g) and g.get("room_id") in rooms]
        answered = [(g, r) for g, r in twins if _named_types(g)]
        group = [f] + [g for g, _r in answered]
        # Only a group with a piece the rule below could decide alone (two answers, both fitting) is decided: twins
        # whose passes all name one type that fits besides one that does not stay for review, as a single piece does.
        deciders = {p["id"] for p in group if len(_named_types(p)) == 2 and all(fits(p, t) for t in _named_types(p))}
        if not deciders:
            continue
        shared = [t for t in pair if answered and all(t in _named_types(g) for g in group)
                  and all(fits(p, t) and (t not in schemas.FIXED_TYPES or t in misses_of(p))
                          and INF.placeable(t, p, rooms[p["room_id"]]) is None
                          for p in [f] + [g for g, _r in twins])]
        holds = None
        if len(shared) == 1:
            ftype = shared[0]
            why = TWIN_TIE_NOTE.format(twin=answered[0][0]["id"], room=answered[0][1]["id"])
        else:
            if f["id"] not in deciders:
                continue                        # a twin decides when its turn comes (its type reaches this piece)
            room = rooms[f["room_id"]]
            size = [float(v) for v in f["footprint"]["size"]]
            misses = misses_of(f)
            # 26 Oct 2026 (module docstring): a wall type whose back cannot stand on a wall here, or a round chair, is
            # no choice (real06 f_L0_016: a 0.87 x 0.52 m piece at 135 deg, table_coffee / bookshelf, became a lone
            # bookshelf in the middle of the salon "because the room misses it")
            blocked = {t: INF.placeable(t, f, room) for t in pair}
            ok = [t for t in pair if blocked[t] is None]
            missing = [t for t in ok if t in misses]
            # Fixed equipment is taken as drawn, never guessed (CLAUDE.md): a fixed type the room does not miss is no
            # choice (real02's salon sofa f_L-1b_045, kitchen_island / sofa, beside the open kitchen's own island).
            choices = [t for t in ok if t not in schemas.FIXED_TYPES or t in missing]
            conf = {c.get("type"): float(c.get("confidence") or 0.0) for c in f.get("type_candidates") or []
                    if isinstance(c, dict)}
            group = _one_group(pair, room)
            if len(missing) == 1:
                ftype = missing[0]
                why = f"the room misses it ({misses[ftype]})"
                other = [t for t in pair if t != ftype and blocked[t]]
                if other:
                    why += f"; not {other[0]}: {blocked[other[0]]}"
            elif len(choices) == 1:
                ftype = choices[0]
                other = next(t for t in pair if t != ftype)
                why = (f"the other answer is no choice: {blocked[other]}" if blocked[other] else
                       "the other answer is fixed equipment the room does not miss (taken as drawn, never guessed)")
            elif len(choices) == 2:
                ftype = min(pair, key=lambda t: (round(INF._product_distance(t, size), 4), -conf.get(t, 0.0), t))
                why = "its real product size is the nearer one to the drawn size" + \
                      (" (the room misses both)" if missing else "")
            elif group is not None and len(ok) == 2:
                # 26 Oct 2026 (module docstring): two fixed types of one functional group (kitchen_counter and
                # sink_kitchen, real06 f_L0_027): the piece is that group's run or anchor holding the named member,
                # never an unknown box
                ftype, holds = group[0], group[1]
                why = (f"both answers are members of the {group[2]} group: the {ftype} that holds the named "
                       f"{holds}")
            else:
                continue                        # two fixed types the room does not miss: the plan crop decides
            if group is not None and group[0] == ftype:
                holds = group[1]                # the run or anchor chosen holds the other answer's member
        _tie_type(build, f, ftype, why, items, raw, fits)
        if holds:
            _holds_member(build, f, holds, items)
        typed.append(f["id"])
        note = TWIN_TIE_NOTE.format(twin=f["id"], room=f["room_id"])
        for g, _r in twins:
            if ftype in _named_types(g) and fits(g, ftype):
                _tie_type(build, g, ftype, note, items, raw, fits)
                typed.append(g["id"])
            else:
                later.add(g["id"])              # the twin rule types it from ``f`` (code_first after this step)
    return typed


def _one_group(pair: list[str], room: dict) -> Optional[tuple[str, str, str]]:
    """26 Oct 2026 (module docstring): ``(the type to give, the member it holds, the group)`` when both AI answers
    ``pair`` are members of one functional run group (``groups.group_of_type``, ``layout: run``: kitchen_counter and
    sink_kitchen are the kitchen run) and the group's anchor type is one of them: the anchor holding the other.
    None otherwise."""
    from wenart.furniture import groups as GR

    rtype = room.get("room_type")
    names = {GR.group_of_type(t, rtype) for t in pair}
    if len(names) != 1 or None in names:
        return None
    name = names.pop()
    template = GR.load_groups().get(name) or {}
    if template.get("layout") != "run":
        return None                             # a set (bath, WC) holds separate fixtures: no piece holds another
    anchors = [t for t in pair if t in ((template.get("anchor") or {}).get("types") or [])]
    if len(anchors) != 1:
        return None
    member = next(t for t in pair if t != anchors[0])
    return anchors[0], member, name


def _holds_member(build, f: dict, member: str, items: dict) -> None:
    """26 Oct 2026 (module docstring): ``f`` (a run or anchor typed by ``tie_break``'s group rule) holds the named
    ``member``: ``holds`` lists it, a sink or hob gets its place at the drawn centre (``module_hints``: the kitchen
    run's module plan builds the sink unit or the hob gap there; a drawn sink or stove inside the run, which the fit
    finds, still wins), and a run's depth outside its product range takes the product depth with its back kept on
    its wall (``drawn_footprint`` kept, ``adjusted_by_ai`` by code, the plan crop)."""
    from wenart.furniture import sizes

    f["holds"] = sorted(set(f.get("holds") or []) | {member})
    hint = HOLDS_HINTS.get(member)
    if hint and f["type"] in ("kitchen_counter", "kitchen_island"):
        f["module_hints"] = dict(f.get("module_hints") or {}, **{hint: [round(float(v), 4) for v in
                                                                       f["footprint"]["center"]]})
    w, d = (float(v) for v in f["footprint"]["size"][:2])
    snap = sizes.snap_size(f["type"], (w, d))
    if not (snap["changed"] and sizes.is_run(f["type"])):
        return
    room = next((r for r in build.building.get("rooms") or [] if r.get("id") == f.get("room_id")), None)
    if room is None or len(room.get("polygon") or []) < 3:
        return
    det = items[f["id"]].details if f["id"] in items else {}
    crop = _crop(det) or reading_crop(build, f)
    before = copy.deepcopy(f["footprint"])
    new = _resized(f, room_ring(room), snap["footprint"])
    reason = (f"a drawn {f['type']} {w:.2f} x {d:.2f} m holding its {member}: {snap['reason']} "
              f"({snap['product']}), its back kept on its wall" + (f"; plan crop {crop}" if crop else ""))
    _code_label(f, RUN_DEPTH_RULE, reason, {"footprint": before}, crop)
    f["footprint"] = new["footprint"]
    if hint and "module_hints" in f:
        f["module_hints"][hint] = [round(float(v), 4) for v in f["footprint"]["center"]]
    f.setdefault("evidence", []).append(_ev(f, RUN_DEPTH_RULE, reason, 0.7))
    build.warn(f"{f['id']}: {reason}")


def _tie_type(build, f: dict, ftype: str, why: str, items: dict, raw: list, fits) -> None:
    """``tie_break``'s decision ``ftype`` (``why``) applied to ``f``: type, ``type_method: INFER_METHOD``, ``inferred``
    with the reason (both answers, the plan crop), built, the rule's evidence, the type's height, and its
    ``symbol_type_disagreement`` conflict resolved; a warning."""
    from wenart.furniture import schemas

    b = build.building
    named = _named_types(f)
    size = [float(v) for v in f["footprint"]["size"]]
    others = [t for t in named if t != ftype]
    det = items[f["id"]].details if f["id"] in items else {}
    crop = _crop(det)
    said = (f"the two AI passes disagree ({named[0]} / {named[1]})" if len(named) == 2
            else f"the AI passes named {' / '.join(named)}")
    reason = (f"{said}; {'both fit' if all(fits(f, t) for t in named) else ftype + ' fits'} the drawn "
              f"{size[0]:.2f} x {size[1]:.2f} m and the room: {ftype}, because {why}"
              + (f"; plan crop {crop}" if crop else ""))
    f["type"] = ftype
    f["type_method"] = INFER_METHOD
    f["inferred"] = True
    f["inferred_reason"] = reason
    if f.get("build") is False:
        f["build"] = True                       # unbuilt only because it was untyped (``infer.untyped_drawn``)
        f.pop("not_built_reason", None)
    f.setdefault("evidence", []).append(_ev(f, TIE_RULE, reason, 0.55))
    if f.get("height") is None and schemas.HEIGHTS.get(ftype) is not None:
        f["height"] = schemas.HEIGHTS[ftype]
    for c in raw + list(b.get("conflicts") or []):
        if c.get("kind") == "symbol_type_disagreement" and f["id"] in (c.get("element_ids") or []):
            c["resolution"] = (f"typed {ftype} by code (not {' or '.join(others) or 'another type'}): {why}; "
                               f"inferred, listed in the report ({TIE_RULE})")
    build.warn(f"{f['id']}: unknown -> {ftype} by code ({TIE_RULE}): {reason}")


# --------------------------------------------------------------------------
# 4. Misread fixed equipment (user OK 1 of 10 Oct 2026)
# --------------------------------------------------------------------------

def misread_share(ftype: str, size) -> float:
    """How far a footprint lies outside its type's real range (0 inside; 0.5 = 50 % beyond a bound), the better of
    both orientations."""
    a, b_ = (float(v) for v in size[:2])
    return min(oriented_share(ftype, (a, b_)), oriented_share(ftype, (b_, a)))


def oriented_share(ftype: str, size) -> float:
    """``misread_share`` with the first side as the width (across the front) and the second as the depth."""
    from wenart.furniture import sizes

    r = sizes.real_range(ftype)
    if not r:
        return 0.0
    e = 0.0
    for v, (lo, hi) in ((float(size[0]), r["width"]), (float(size[1]), r["depth"])):
        if v < lo:
            e = max(e, lo / max(v, 1e-6) - 1.0)
        elif v > hi:
            e = max(e, v / hi - 1.0)
    return e


def swing_polys(b: dict, room: dict) -> list[Polygon]:
    """The swings of the doors that open into ``room``: on the room side of the wall, the two quarter discs a leaf
    of the door's width sweeps hinged at either jamb (the hinge side is not read), within the opening's width. A
    piece beside the door frame is not in the swing (a half disc around the centre would reach half a leaf past
    each jamb: real02's washbasins beside their bathroom doors)."""
    walls = {w["id"]: w for w in b.get("walls") or []}
    room_poly = Polygon(room["polygon"])
    room_poly = room_poly if room_poly.is_valid else room_poly.buffer(0)
    out = []
    for o in b.get("openings") or []:
        if o.get("type") != "door" or o.get("swing_side") != room["id"] or o.get("operation") in ("sliding",
                                                                                                    "pocket"):
            continue
        w = walls.get(o.get("wall_id"))
        if w is None:
            continue
        (x0, y0), (x1, y1) = w["start"], w["end"]
        length = math.hypot(x1 - x0, y1 - y0) or 1.0
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        cx, cy = o["center"]
        width = float(o.get("width") or 0.9)
        half_t = float(w.get("thickness") or 0.1) / 2.0
        for sign in (1.0, -1.0):
            nx, ny = -uy * sign, ux * sign
            inner = (cx + nx * half_t, cy + ny * half_t)
            if not room_poly.buffer(0.01).contains(Point(inner[0] + nx * 0.05, inner[1] + ny * 0.05)):
                continue
            ja = (inner[0] - ux * width / 2, inner[1] - uy * width / 2)
            jb = (inner[0] + ux * width / 2, inner[1] + uy * width / 2)
            strip = Polygon([ja, jb, (jb[0] + nx * width, jb[1] + ny * width),
                             (ja[0] + nx * width, ja[1] + ny * width)])
            out.append(unary_union([Point(ja).buffer(width, 32), Point(jb).buffer(width, 32)]).intersection(strip))
            break
    return out


def problems(poly: Polygon, room_poly: Polygon, swings: list[Polygon], others: Optional[list] = None) -> list[str]:
    """What is wrong with a fixed piece where it stands (the cases of the user OK of 10 Oct 2026): through a wall
    (more than ``THROUGH_WALL_M`` past its room's outline) or in a door swing (more than ``SWING_SHARE`` of its
    area). ``others`` is accepted for callers that pass the room's pieces; overlaps are not this rule's business (a
    sink stands in its counter)."""
    out = []
    if poly.difference(room_poly.buffer(THROUGH_WALL_M, join_style=2)).area > 1e-4:
        out.append("through a wall")
    if any(poly.intersection(s).area > SWING_SHARE * poly.area for s in swings):
        out.append("in a door swing")
    return out


def _fits_room(poly: Polygon, room_poly: Polygon, swings: list[Polygon], others: list[Polygon]) -> bool:
    return not problems(poly, room_poly, swings, others)


def _placed(f: dict, size, centre) -> dict:
    out = copy.deepcopy(f)
    out["footprint"] = dict(out["footprint"], center=[round(centre[0], 4), round(centre[1], 4)],
                            size=[round(size[0], 4), round(size[1], 4)])
    return out


def fix_fixed(build, items: Optional[dict] = None) -> list[str]:
    """Step 4 (see the module docstring). Returns the ids of the adjusted pieces. ``items`` (the core's items) give
    the plan crop of a piece that was asked (``adjusted_by_ai["crop"]``)."""
    from wenart.furniture import infer as INF
    from wenart.furniture import schemas

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    done = []
    for f in b["furniture"]:
        if f["type"] not in schemas.FIXED_TYPES or f["type"] in ("stair", "kitchen_counter") or \
                f.get("build") is False or f.get("source") != "from_documents":
            continue
        room = rooms.get(f.get("room_id"))
        if room is None:
            continue
        room_poly = Polygon(room["polygon"])
        room_poly = room_poly if room_poly.is_valid else room_poly.buffer(0)
        ring = room_ring(room)
        swings = swing_polys(b, room)
        mates = [o for o in b["furniture"] if o is not f and o.get("room_id") == f.get("room_id")
                 and o.get("build") is not False]
        others = [rect(o) for o in mates if o["type"] in schemas.FIXED_TYPES]
        before = copy.deepcopy(f["footprint"])
        drawn_front = f.get("front_deg")
        share = misread_share(f["type"], f["footprint"]["size"])
        found = problems(rect(f), room_poly, swings, others)
        if share <= MISREAD_SHARE and not found and not fixture_rivals(f, f, mates):
            # Fix round after P5 (user decision of 22 Oct 2026): a bath or shower a few cm longer than its bay. Review:
            # a piece without a question crop gets one drawn at the reading (``reading_crop``), only when it changes.
            item = (items or {}).get(f["id"])
            crop = _crop(item.details if item is not None else None)
            if bay_fit(f, room_poly) is not None and shrink_to_bay(build, f, room_poly, crop or reading_crop(build, f)):
                done.append(f["id"])
            continue
        reasons = []
        new = copy.deepcopy(f)
        if new.get("front_deg") is None and f["type"] not in schemas.FRONTLESS_TYPES:
            front, why = _front_of(new, room, mates)
            if front is not None:
                INF.set_front(new, front)
                reasons.append(f"front {new['front_deg']:g} deg inferred ({why})")
        if share > MISREAD_SHARE:
            size = _product(f["type"], new)
            new = _resized(new, ring, size)
            reasons.append(f"drawn {before['size'][0]:.2f} x {before['size'][1]:.2f} m is {share:.0%} outside the "
                           f"{f['type']} size range: set to the real product size {size[0]:.2f} x {size[1]:.2f} m "
                           f"(width x depth), its back kept on its wall")
        found = problems(rect(new), room_poly, swings, others)
        wall_problem = bool(found)
        # 27 Oct 2026 (``fixture_seat`` rule 3): a drawn fixed piece standing in another drawn fixture is a reading
        # error too; the one with the weaker reading gives way (real06: the merged bath outline over the basin)
        rivals = fixture_rivals(f, new, mates)
        if rivals:
            found.append("on " + " and ".join(f"{o['id']} ({o['type']})" for o in rivals))
        # the drawn outline (before an earlier resize, e.g. an AI-named member's product) decides whether it was misread:
        # an outline outside the type's ranges at all, or resized by code already, is no product where it stands
        outline = (f.get("drawn_footprint") or before).get("size") or before["size"]
        misread = share > MISREAD_SHARE or misread_share(f["type"], outline) > 0.0 or FS.resized(f)
        misread_off_wall = misread and f["type"] in FIXED_SEAT_TYPES and not wall_sides(new, ring)
        if found or misread_off_wall:
            moved, how = _fixed_place(f, new, room, room_poly, ring, swings, others, mates, misread, wall_problem)
            if moved is not None:
                reasons.append(f"{' and '.join(found) or 'a misread outline off every wall'}: {how}")
                new = moved
            elif not found:
                pass                                     # off the walls but nothing in the way: resized as before
            else:
                reasons.append(f"{' and '.join(found)}, no free spot within {MOVE_MAX_M:.2f} m: left as drawn")
                if share <= MISREAD_SHARE:
                    build.warn(f"{f['id']}: {f['type']} {' and '.join(found)}; no free spot within "
                               f"{MOVE_MAX_M:.2f} m (left as drawn)")
                    continue
        reason = "; ".join(reasons)
        f.setdefault("drawn_type", f["type"])
        f.setdefault("drawn_footprint", before)
        f.setdefault("drawn_front_deg", drawn_front)
        f.setdefault("drawn_height", f.get("height"))
        changed = {"footprint": before}
        if new.get("front_deg") != drawn_front:
            changed["front_deg"] = drawn_front
        item = (items or {}).get(f["id"])
        # fix round after P5, review: a piece without a question crop gets one drawn at the reading (its drawn place)
        crop = _crop(item.details if item is not None else None) or reading_crop(build, f)
        f["footprint"] = new["footprint"]
        f["front_deg"] = new.get("front_deg")
        # 27 Oct 2026: merged into an earlier code record (an AI-named member's product size), not over it
        INF.merge_code_label(f, {"by": "code", "reason": f"misread fixed equipment (CLAUDE.md, user OK of 10 Oct "
                                                         f"2026): {reason}",
                                 "changed": changed, "rule": FIXED_RULE, "crop": crop})
        if crop and crop not in reason:
            reason = f"{reason}; plan crop {crop}"
        f.setdefault("evidence", []).append(_ev(f, FIXED_RULE, reason, 0.8))
        build.warn(f"{f['id']}: {f['type']} adjusted at ingest: {reason}")
        done.append(f["id"])
    return done


def _product(ftype: str, f: dict) -> tuple[float, float]:
    """The real product footprint (width across the front, depth) nearest to the drawn one; without a front the
    drawn sides are read the way round that fits the type's range best."""
    from wenart.furniture import sizes

    w, d = (float(v) for v in f["footprint"]["size"][:2])
    if f.get("front_deg") is None and oriented_share(ftype, (d, w)) < oriented_share(ftype, (w, d)) - 1e-9:
        pw, pd = sizes.product_size(ftype, (d, w))
        return float(pd), float(pw)
    pw, pd = sizes.product_size(ftype, (w, d))
    return float(pw), float(pd)


def _resized(f: dict, ring, size) -> dict:
    """``f`` with the product ``size`` (width, depth in its frame), its back (or the side on a wall) kept in place."""
    w0, d0 = (float(v) for v in f["footprint"]["size"][:2])
    w1, d1 = float(size[0]), float(size[1])
    cx, cy = f["footprint"]["center"]
    rot = math.radians(float(f["footprint"].get("rotation_deg") or 0.0))
    ux, uy = math.cos(rot), math.sin(rot)              # local +X
    vx, vy = -math.sin(rot), math.cos(rot)             # local +Y (the back, the front faces -Y)
    near = wall_sides(f, ring)                          # local order: front (-Y), right (+X), back (+Y), left (-X)
    sx, sy = 0.0, 0.0
    if f.get("front_deg") is not None or 2 in near or 0 in near:
        back = 2 if (f.get("front_deg") is not None or 2 in near) else 0
        sy = (d0 - d1) / 2.0 * (1.0 if back == 2 else -1.0)
    if 1 in near and 3 not in near:
        sx = (w0 - w1) / 2.0
    elif 3 in near and 1 not in near:
        sx = -(w0 - w1) / 2.0
    centre = (cx + ux * sx + vx * sy, cy + uy * sx + vy * sy)
    return _placed(f, (w1, d1), centre)


def _nearest_valid(f: dict, room_poly: Polygon, swings: list, others: list,
                   avoid: Optional[list] = None) -> Optional[dict]:
    """The nearest position within ``MOVE_MAX_M`` (5 cm steps along both footprint axes, along first) where the
    piece lies in its room, clear of door swings and other fixed pieces; None when there is none. 27 Oct 2026:
    ``avoid`` (corner lists of the drawn fixtures it must not stand in, ``fixture_seat``) are cleared too."""
    cx, cy = f["footprint"]["center"]
    rot = math.radians(float(f["footprint"].get("rotation_deg") or 0.0))
    axes = [(math.cos(rot), math.sin(rot)), (-math.sin(rot), math.cos(rot))]
    steps = int(round(MOVE_MAX_M / MOVE_STEP_M))
    best = None
    for i in range(-steps, steps + 1):
        for j in range(-steps, steps + 1):
            dx = axes[0][0] * i * MOVE_STEP_M + axes[1][0] * j * MOVE_STEP_M
            dy = axes[0][1] * i * MOVE_STEP_M + axes[1][1] * j * MOVE_STEP_M
            d = math.hypot(dx, dy)
            if d > MOVE_MAX_M + 1e-9 or (best is not None and d >= best[0] - 1e-9):
                continue
            cand = _placed(f, f["footprint"]["size"], (cx + dx, cy + dy))
            if _fits_room(rect(cand), room_poly, swings, others) and not (avoid and any(
                    FS.cut_depth(FS.footprint_rect(cand["footprint"]), o) > FS.CUT_EPS_M for o in avoid)):
                best = (d, abs(j), cand)
    return best[2] if best else None


def fixture_rivals(f: dict, cur: dict, mates: list[dict]) -> list[dict]:
    """27 Oct 2026 (``fixture_seat`` rule 3): the drawn fixed pieces among ``mates`` that ``cur`` (``f`` where it
    stands or would stand) cuts deeper than ``fixture_seat.CLASH_M`` and that ``f`` gives way to (the weaker reading
    moves: real06's merged bath outline, unverified and resized, before the basin both AI passes agreed on). A piece
    built into a counter or a vanity is no rival of it."""
    out = []
    r = FS.footprint_rect(cur["footprint"])
    for o in mates:
        if o is f or o.get("build") is False or not o.get("footprint") or not FS.fixture_pair(f, o):
            continue
        if FS.cut_depth(r, FS.footprint_rect(o["footprint"])) > FS.CLASH_M and FS.gives_way(f, o) is f:
            out.append(o)
    return out


def _fixed_place(f: dict, new: dict, room: dict, room_poly: Polygon, ring, swings: list, others: list,
                 mates: list[dict], misread: bool, wall_problem: bool) -> tuple[Optional[dict], str]:
    """27 Oct 2026 (``fixture_seat``): where the fixed piece ``f`` (``new``: its fixed front and product size so far)
    goes when it stands through a wall, in a door swing or in another drawn fixture, or is a misread outline off every
    wall: ``(the piece moved, how)`` or ``(None, "")``. In order: a misread outline off every wall is seated in it
    (rule 1: neither its centre nor its box angle is the piece's); through a wall or in a swing it moves to the
    nearest valid spot (as before, now clear of the drawn fixtures of ``fixture_seat`` too); standing only in another
    fixture it slides along its wall (rule 2); then it is seated in its drawn outline (its drawn size when that is a
    product, else the type's products). It clears every other fixed piece but its host (a counter, a vanity) and a
    fixture it stands in that gives way to it (that one moves itself)."""
    from wenart.furniture import schemas

    cur = FS.footprint_rect(new["footprint"])
    kept = [o for o in mates if o.get("footprint") and o.get("type") in schemas.FIXED_TYPES
            and not FS.hosted_pair(f, o) and not (FS.fixture_pair(f, o) and FS.gives_way(f, o) is o
                                                  and FS.cut_depth(cur, FS.footprint_rect(o["footprint"])) > FS.CLASH_M)]
    fixtures = [FS.footprint_rect(o["footprint"]) for o in kept]
    drawn_fixtures = [FS.footprint_rect(o["footprint"]) for o in kept if FS.fixture_pair(f, o)]

    def blocked(r) -> bool:
        poly = Polygon(r)
        return any(poly.intersection(s).area > SWING_SHARE * poly.area for s in swings)

    def seated() -> tuple[Optional[dict], str]:
        if f["type"] not in FS.SEAT_TYPES:
            return None, ""
        from wenart.furniture import sizes

        drawn = f.get("drawn_footprint") or f["footprint"]
        size = tuple(float(v) for v in new["footprint"]["size"][:2])
        # its drawn size when that is a product of its type, else the type's products
        prods = [size] if not misread and sizes.fits(f["type"], size, 0.0) else FS.products_of(f["type"])
        got = FS.seat(f["type"], drawn, room["polygon"], fixtures, blocked=blocked if swings else None,
                      products=prods)
        if got is None:
            return None, ""
        out = copy.deepcopy(new)
        out["footprint"] = dict(got["footprint"])
        out["front_deg"] = got["front_deg"]
        return out, got["reason"]

    if misread and not wall_sides(new, ring):
        got = seated()
        if got[0] is not None:
            return got
    if wall_problem:
        moved = _nearest_valid(new, room_poly, swings, others, avoid=drawn_fixtures)
        if moved is not None:
            d = math.dist(moved["footprint"]["center"], new["footprint"]["center"])
            return moved, f"moved {d:.2f} m to the nearest free spot"
    else:
        step = FS.slide(new["footprint"], room["polygon"], fixtures, blocked=blocked if swings else None)
        if step is not None:
            dx, dy, d = step
            c = new["footprint"]["center"]
            return _placed(new, new["footprint"]["size"], (c[0] + dx, c[1] + dy)), \
                f"moved {d:.2f} m along its wall to the nearest free spot"
    return seated()


def _local_room(p, room_poly: Polygon):
    """``room_poly`` in the frame of the placer piece ``p`` (x along its front edge, y towards its back)."""
    from shapely import affinity

    moved = affinity.translate(room_poly, -p.center[0], -p.center[1])
    return affinity.rotate(moved, -p.rotation_deg, origin=(0.0, 0.0))


def bay_overrun(f: dict, room_poly: Polygon) -> Optional[dict]:
    """Fix round after P5 (user decision of 22 Oct 2026, CLAUDE.md fixed equipment): how far a drawn bathtub or shower
    runs past the walls of its bay. In the piece's front frame the part outside the room must lie in end strips only
    (a strip across the whole depth at a short end, or across the whole width at a long side; a corner or a column
    cut is no bay overrun), each axis overrun at most ``BAY_OVERRUN_M[1]`` and one of them more than
    ``BAY_OVERRUN_M[0]``. Returns ``{"cut": {"left", "right", "front", "back"}, "clear": (width, depth),
    "overrun_m"}`` (metres, the clear box between the cut ends) or None."""
    from shapely.geometry import box as sbox
    from wenart.furniture import placer

    if f.get("type") not in BAY_TYPES or not f.get("footprint"):
        return None
    try:
        p = placer.drawn_piece(f)
    except (KeyError, TypeError, ValueError):
        return None
    w, d = float(p.size[0]), float(p.size[1])
    local = _local_room(p, room_poly).buffer(1e-4, join_style=2)     # no float slivers along a wall face
    piece = sbox(-w / 2.0, -d / 2.0, w / 2.0, d / 2.0)
    out = piece.difference(local)
    if out.is_empty or out.area <= 1e-6:
        return None
    cut = {"left": 0.0, "right": 0.0, "front": 0.0, "back": 0.0}
    for g in getattr(out, "geoms", [out]):
        if g.area <= 1e-7:
            continue
        x0, y0, x1, y1 = g.bounds
        if (y1 - y0) >= BAY_SPAN * d and x0 <= -w / 2.0 + 1e-6 and x1 < 0.0:
            cut["left"] = max(cut["left"], x1 + w / 2.0)
        elif (y1 - y0) >= BAY_SPAN * d and x1 >= w / 2.0 - 1e-6 and x0 > 0.0:
            cut["right"] = max(cut["right"], w / 2.0 - x0)
        elif (x1 - x0) >= BAY_SPAN * w and y0 <= -d / 2.0 + 1e-6 and y1 < 0.0:
            cut["front"] = max(cut["front"], y1 + d / 2.0)
        elif (x1 - x0) >= BAY_SPAN * w and y1 >= d / 2.0 - 1e-6 and y0 > 0.0:
            cut["back"] = max(cut["back"], d / 2.0 - y0)
        else:
            return None                                  # a corner or column cut: no bay overrun
    over_x, over_y = cut["left"] + cut["right"], cut["front"] + cut["back"]
    if max(over_x, over_y) <= BAY_OVERRUN_M[0] + 1e-9 or max(over_x, over_y) > BAY_OVERRUN_M[1] + 1e-6:
        return None
    clear = sbox(-w / 2.0 + cut["left"], -d / 2.0 + cut["front"], w / 2.0 - cut["right"], d / 2.0 - cut["back"])
    if clear.difference(local).area > 1e-4:
        return None
    return {"cut": {k: round(v, 4) for k, v in cut.items()}, "clear": (round(w - over_x, 4), round(d - over_y, 4)),
            "overrun_m": round(max(over_x, over_y), 4)}


def bay_product(ftype: str, size, clear) -> Optional[tuple[float, float]]:
    """Fix round after P5: the real product (``sizes.products``, either way round) that fits the clear box
    ``clear`` (width, depth in the piece's front frame) and is nearest to the drawn ``size`` (log distance), else
    None."""
    from wenart.furniture import sizes

    w, d = float(size[0]), float(size[1])
    best = None
    for prod in sizes.products(ftype):
        for pw, pd in ((float(prod[0]), float(prod[1])), (float(prod[1]), float(prod[0]))):
            if pw > float(clear[0]) + 1e-9 or pd > float(clear[1]) + 1e-9:
                continue
            key = (round(abs(math.log(w / pw)) + abs(math.log(d / pd)), 6), -pw * pd)
            if best is None or key < best[0]:
                best = (key, (pw, pd))
    return best[1] if best else None


def bay_fit(f: dict, room_poly: Polygon) -> Optional[dict]:
    """Fix round after P5: the bay-overrun fix of a drawn bathtub or shower (``bay_overrun``): ``{"footprint", "size",
    "overrun", "reason"}`` with the nearest real product that fits the clear bay (``bay_product``), its back kept on its
    wall, an end kept on the wall it was cut at (centred between the walls when both ends were cut), else None. Pure:
    ``f`` is unchanged (``edit_ops.fix_fixture`` uses it too)."""
    from wenart.furniture import group_checks as GC
    from wenart.furniture import placer

    over = bay_overrun(f, room_poly)
    if over is None:
        return None
    p = placer.drawn_piece(f)
    w, d = float(p.size[0]), float(p.size[1])
    prod = bay_product(f["type"], (w, d), over["clear"])
    if prod is None:
        return None
    pw, pd = prod
    cut = over["cut"]
    x0, x1 = -w / 2.0 + cut["left"], w / 2.0 - cut["right"]
    y0, y1 = -d / 2.0 + cut["front"], d / 2.0 - cut["back"]
    if cut["left"] > 0 and cut["right"] > 0:
        cx = (x0 + x1) / 2.0
    elif cut["left"] > 0:
        cx = x0 + pw / 2.0
    elif cut["right"] > 0:
        cx = x1 - pw / 2.0
    else:
        cx = min(max(0.0, x0 + pw / 2.0), x1 - pw / 2.0)
    if f.get("front_deg") is not None:
        cy = y1 - pd / 2.0                               # the back (+y) stays on its wall
    elif cut["front"] > 0 and cut["back"] > 0:
        cy = (y0 + y1) / 2.0
    elif cut["front"] > 0:
        cy = y0 + pd / 2.0
    else:
        cy = y1 - pd / 2.0 if cut["back"] > 0 else min(max(0.0, y0 + pd / 2.0), y1 - pd / 2.0)
    centre = GC.to_world(p, (cx, cy))
    fp = {"center": [round(centre[0], 4), round(centre[1], 4)], "size": [round(pw, 4), round(pd, 4)],
          "rotation_deg": round(float(p.rotation_deg), 3)}
    reason = (f"misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn {f['type']} {w:.2f} x {d:.2f} m runs "
              f"{over['overrun_m'] * 100:.0f} cm past the walls of its bay (clear {over['clear'][0]:.2f} x "
              f"{over['clear'][1]:.2f} m): the nearest real product that fits, {pw:.2f} x {pd:.2f} m")
    return {"footprint": fp, "size": (pw, pd), "overrun": over, "reason": reason}


def shrink_to_bay(build, f: dict, room_poly: Polygon, crop: Optional[str] = None) -> bool:
    """Fix round after P5 (module docstring): ``bay_fit`` applied to a drawn bathtub or shower at the reading
    (before the fit): the product footprint, ``drawn_*`` kept, ``adjusted_by_ai`` (``by: code``, the reason, the
    changed footprint, the rule, the plan crop) and the rule's evidence entry. Returns True when it changed ``f``."""
    if f.get("source") != "from_documents" or f.get("build") is False:
        return False
    fix = bay_fit(f, room_poly)
    if fix is None:
        return False
    before = copy.deepcopy(f["footprint"])
    f.setdefault("drawn_type", f["type"])
    f.setdefault("drawn_footprint", before)
    f.setdefault("drawn_front_deg", f.get("front_deg"))
    f.setdefault("drawn_height", f.get("height"))
    f["footprint"] = fix["footprint"]
    f["adjusted_by_ai"] = {"by": "code", "reason": fix["reason"], "changed": {"footprint": before}, "rule": BAY_RULE,
                           "crop": crop}
    f.setdefault("evidence", []).append(_ev(f, BAY_RULE, fix["reason"] + (f"; plan crop {crop}" if crop else ""), 0.8))
    build.warn(f"{f['id']}: {f['type']} adjusted at ingest: {fix['reason']}")
    return True


def reading_crop(build, f: dict) -> Optional[str]:
    """Fix round after P5 (22 Oct 2026), review (module docstring): the plan crop of a drawn piece that has no
    question crop, drawn now in the layout of the question crops: the level's vector walls (grey), the other drawn
    pieces (light grey) and the piece's drawn footprint (black, dashed box), written to
    ``<out>/READING_CROP_DIR/<piece id>_ctx.png``. Returns that path relative to the output folder, or None without an
    output folder (a hand-made build) or when it cannot be drawn (a warning says why)."""
    from pathlib import Path

    out_dir = getattr(build, "out_dir", None)
    if out_dir is None or not f.get("footprint"):
        return None
    from wenart.recognition import crops as CR

    b = build.building
    level = f.get("level_id")
    poly = rect(f)
    walls = []
    for w in b.get("walls") or []:
        if w.get("level_id") != level or not w.get("start") or not w.get("end"):
            continue
        line = LineString([tuple(map(float, w["start"])), tuple(map(float, w["end"]))])
        if line.length > 1e-6:
            walls.append(line.buffer(max(float(w.get("thickness") or 0.1), 0.01) / 2.0, cap_style=2))
    others = [[list(pt) for pt in rect(o).exterior.coords] for o in b.get("furniture") or []
              if o is not f and o.get("level_id") == level and o.get("footprint")]
    x0, y0, x1, y1 = poly.bounds
    cand = {"key": str(f["id"]), "footprint": f["footprint"], "strokes": [[list(pt) for pt in poly.exterior.coords]],
            "bbox": [x0, y0, x1, y1]}
    rel = f"{READING_CROP_DIR}/{f['id']}_ctx.png"
    try:
        CR.save_png(CR.draw_vector_ctx(CR.vector_description(cand, {"walls": walls, "others": others})),
                    Path(out_dir) / rel)
    except (ValueError, OSError, ImportError) as exc:
        build.warn(f"{f['id']}: plan crop not drawn at the reading ({exc})")
        return None
    return rel


# --------------------------------------------------------------------------
# 4b. Fixtures you can use (29 Oct 2026, lessons UL92, UL95, UL96)
# --------------------------------------------------------------------------

USE_RULE = "reading.fixture_use"
SWING_TOUCH_M2 = 0.01              # a moved piece reaching this far into a door swing stands in it


def fixture_use_fixes(build, items: Optional[dict] = None) -> dict:
    """29 Oct 2026 (``wenart.furniture.fixture_use``; the user on real06 run 20261028-154514-full: "This washing machine
    would not open", "this sink not making sense there", "There is a gap between wall and water faucet not looking
    good"): the clear reading errors of drawn pieces a visitor sees at once, fixed by code (CLAUDE.md furniture rules;
    ``adjusted_by_ai`` by code with the reason and the plan crop, ``drawn_*`` kept), after the fronts:

    1. ``backs``: a piece whose back belongs on a wall and stands parallel to it a drawing gap (0.055-0.15 m) off it goes
       back onto the wall, with the pieces built into it (``fixture_use.snap_back``; never into another piece);
    2. ``fronts``: a door-fronted piece (a washer, a dishwasher, a cooker, a fridge, a nightstand) whose front a wall or a
       neighbour blocks was read the wrong way round: it turns to its free side with its back on a wall, else it moves
       at most 0.5 m (``fixture_use.free_front``; never a piece of a kitchen run);
    3. ``basins``: a basin under a window with a low sill moves at most 0.5 m to a solid stretch of wall
       (``fixture_use.clear_basin``); when none is that close the architect asks (H2).

    Returns ``{"backs": [ids], "fronts": [ids], "basins": [ids]}``."""
    from wenart.furniture import fixture_use as FU

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    walls = {w["id"]: w for w in b.get("walls") or [] if w.get("id")}
    openings = list(b.get("openings") or [])
    out: dict = {"backs": [], "fronts": [], "basins": []}

    def mates(f: dict) -> list[dict]:
        return [o for o in b["furniture"] if o.get("room_id") == f.get("room_id") and o.get("build") is not False
                and o.get("footprint")]

    def blocker(room: dict):
        swings = swing_polys(b, room)

        def blocked(r) -> bool:
            poly = Polygon(r)
            return any(poly.intersection(s).area > SWING_TOUCH_M2 for s in swings)
        return blocked

    def crop_of(f: dict) -> Optional[str]:
        item = (items or {}).get(f["id"])
        return _crop(item.details if item is not None else None) or reading_crop(build, f)

    def apply(f: dict, footprint: dict, front, rule: str, reason: str, crop: Optional[str]) -> None:
        changed = {"footprint": copy.deepcopy(f["footprint"])}
        if front != f.get("front_deg"):
            changed["front_deg"] = f.get("front_deg")
        _code_label(f, rule, reason, changed, crop)       # the drawn values kept first
        f["footprint"] = dict(footprint)
        f["front_deg"] = front
        f.setdefault("evidence", []).append(_ev(f, USE_RULE, reason + (f"; plan crop {crop}" if crop else ""), 0.8))
        build.warn(f"{f['id']}: {f['type']} adjusted at ingest: {reason}")

    drawn = [f for f in b["furniture"] if f.get("source") == "from_documents" and f.get("build") is not False
             and f.get("footprint") and f.get("room_id") in rooms and str(f.get("type") or "unknown") != "unknown"]
    for f in drawn:
        room = rooms[f["room_id"]]
        got = FU.snap_back(f, room["polygon"], mates(f), blocked=blocker(room))
        if got is None:
            continue
        crop = crop_of(f)
        by_id = {o["id"]: o for o in b["furniture"]}
        for pid, fp in sorted(got["footprints"].items()):
            piece = by_id[pid]
            apply(piece, fp, piece.get("front_deg"), "back_gap", got["reason"] if pid == f["id"] else
                  f"built into {f['id']}, moved with it: {got['reason']}", crop)
            out["backs"].append(pid)
    for f in drawn:
        if str(f.get("type")) not in FU.ACCESS_M:
            continue
        room = rooms[f["room_id"]]
        got = FU.free_front(f, room["polygon"], mates(f), blocked=blocker(room))
        if got is None:
            continue
        apply(f, got["footprint"], got["front_deg"], "free_front", got["reason"], crop_of(f))
        f["front_inferred"] = got["reason"]
        out["fronts"].append(f["id"])
    for f in drawn:
        if str(f.get("type")) not in FU.BASINS:
            continue
        room = rooms[f["room_id"]]
        got = FU.clear_basin(f, room["polygon"], mates(f), openings, walls, blocked=blocker(room))
        if got is None:
            continue
        apply(f, got["footprint"], got["front_deg"], "basin_window", got["reason"], crop_of(f))
        out["basins"].append(f["id"])
    return out


# --------------------------------------------------------------------------
# 5. Fronts
# --------------------------------------------------------------------------

def infer_fronts(build, pending=()) -> int:
    """Step 5 (see the module docstring). Returns the number of fronts inferred."""
    from wenart.furniture import infer as INF
    from wenart.furniture import schemas

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    n = 0
    for f in b["furniture"]:
        if f.get("front_deg") is not None or f["type"] in schemas.FRONTLESS_TYPES or f.get("build") is False or \
                f.get("source") != "from_documents" or f["id"] in pending:
            continue
        room = rooms.get(f.get("room_id"))
        if room is None:
            continue
        front, why = _front_of(f, room, [o for o in b["furniture"] if o is not f and o.get("room_id") == room["id"]
                                         and o.get("build") is not False])
        if front is None:
            continue
        INF.set_front(f, front)
        f["inferred"] = True
        f["front_inferred"] = why
        f["inferred_reason"] = "; ".join(x for x in (f.get("inferred_reason"), f"front: {why}") if x)
        f.setdefault("evidence", []).append(_ev(f, FRONT_RULE, f"front {f['front_deg']:g} deg: {why}", 0.6))
        n += 1
    return n


def _front_of(f: dict, room: dict, mates: list[dict]) -> tuple[Optional[float], Optional[str]]:
    """The front the drawing gives a piece (``_front_rules``: its group, its wall, its corner, its free side). Fix round
    after P5 (22 Oct 2026), review: a type that faces along a long side (``LONG_FRONT_TYPES``) never gets a short-side
    front from these rules; the free long side facing the most room instead (``_long_front``)."""
    front, why = _front_rules(f, room, mates)
    if front is None or f.get("type") not in LONG_FRONT_TYPES or not _short_side_front(f["footprint"], front):
        return front, why
    return _long_front(f, room, front, why)


def _long_front(f: dict, room: dict, short: float, why: str) -> tuple[Optional[float], Optional[str]]:
    """Fix round after P5, review: the long side of ``f`` facing the most room (``_free_ray``) among the long sides
    not on a wall, instead of the short-side front ``short`` a rule gave (``why``); (None, None) without one."""
    ring = room_ring(room)
    ss = sides(rect(f))
    near = wall_sides(f, ring)
    longest = max(math.dist(*s) for s in ss)
    ranked = sorted(((_free_ray(f, s, ring), k) for k, s in enumerate(ss)
                     if k not in near and math.dist(*s) >= 0.999 * longest), key=lambda t: (-round(t[0], 3), t[1]))
    if not ranked:
        return None, None
    return (snap_front(f, outward_deg(f, ss[ranked[0][1]])),
            f"a {f['type']} faces along a long side ({why} gives the short side, {short:g} deg): the long side facing "
            f"the most room ({ranked[0][0]:.2f} m free)")


def _front_rules(f: dict, room: dict, mates: list[dict]) -> tuple[Optional[float], Optional[str]]:
    from wenart.furniture import schemas

    ring = room_ring(room)
    poly = rect(f)
    ss = sides(poly)
    near = wall_sides(f, ring)
    ftype = f["type"]
    rule = schemas.orientation_rule(ftype)
    by_type = lambda *ts: [m for m in mates if m["type"] in ts]      # noqa: E731
    if ftype in ("chair", "office_chair", "bar_stool"):
        hosts = by_type("table_dining", "table_coffee", "desk", "kitchen_island")
        if hosts:
            host = min(hosts, key=lambda h: (round(rect(h).distance(poly), 6), h["id"]))
            if rect(host).distance(poly) <= 0.8:
                c = rect(host).centroid
                deg = math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x))
                return snap_front(f, deg), f"faces its table {host['id']}"
    if ftype == "nightstand":
        for bed in by_type("bed_double", "bed_single", "bunk_bed"):
            if bed.get("front_deg") is not None and rect(bed).distance(poly) <= 0.4:
                return snap_front(f, float(bed["front_deg"])), f"faces the way its bed {bed['id']} faces"
    if ftype in ("sofa", "armchair"):
        # Fix round after P5 (module docstring): a seat without a front faces the nearest coffee table close by
        # (a sofa only along a long side).
        tables = by_type("table_coffee")
        if tables:
            host = min(tables, key=lambda h: (round(rect(h).distance(poly), 6), h["id"]))
            if rect(host).distance(poly) <= SEAT_TABLE_M + 1e-9:
                c = rect(host).centroid
                deg = snap_front(f, math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x)))
                if ftype != "sofa" or not _short_side_front(f["footprint"], deg):
                    return deg, f"faces the coffee table {host['id']}"
    if ftype == "tv_unit":
        for seat in by_type("sofa", "sofa_corner", "armchair"):
            c = rect(seat).centroid
            deg = math.degrees(math.atan2(c.y - poly.centroid.y, c.x - poly.centroid.x))
            if len(near) == 1 and abs(G.normalise_angle(deg - (outward_deg(f, ss[near[0]]) + 180.0))) <= 45.0:
                return snap_front(f, deg), f"faces the seat {seat['id']}"
    if len(near) == 1:
        back = ss[near[0]]
        long_side = math.dist(*back) >= 0.999 * max(math.dist(*s) for s in ss)
        if ftype in ("toilet", "bed_double", "bed_single", "bunk_bed", "bathtub") or long_side or \
                rule["back"] in ("wall", "wall_or_group"):
            return snap_front(f, outward_deg(f, back) + 180.0), "its back stands on the only side on a wall"
    if len(near) == 2 and (near[1] - near[0]) % 2 == 1:
        lengths = {k: math.dist(*ss[k]) for k in near}
        long_k, short_k = sorted(near, key=lambda k: -lengths[k])
        # Beds, toilets: the head (short side) is on the wall; cabinets, sofas, counters: the long side.
        k = short_k if ftype in HEAD_TYPES else long_k
        if lengths[long_k] > 1.1 * lengths[short_k]:
            return snap_front(f, outward_deg(f, ss[k]) + 180.0), "standing in a corner: its " + \
                ("short" if k == short_k else "long") + " side on the wall is the back"
    if near and rule["back"] in ("wall", "wall_or_group"):
        # Against two or three walls (a shower in its corner or niche, a washing machine in a corner): the front is
        # the free side facing the most room; a bed's front is one of its short sides.
        free = [k for k in range(4) if k not in near]
        if ftype in HEAD_TYPES:
            shortest = min(math.dist(*s) for s in ss)
            free = [k for k in free if math.dist(*ss[k]) <= 1.01 * shortest]
        ranked = sorted(((_free_ray(f, ss[k], ring), k) for k in free), key=lambda t: (-round(t[0], 3), t[1]))
        if len(ranked) == 1 or (len(ranked) > 1 and ranked[0][0] >= 1.25 * ranked[1][0]):
            k = ranked[0][1]
            return snap_front(f, outward_deg(f, ss[k])), "the free side facing the most room is the front"
    return None, None


def _free_ray(f: dict, side, ring) -> float:
    """How far the room reaches in front of a side (from its midpoint along its outward normal, up to 10 m)."""
    deg = math.radians(outward_deg(f, side))
    mx, my = (side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0
    ray = LineString([(mx + math.cos(deg) * 0.01, my + math.sin(deg) * 0.01),
                      (mx + math.cos(deg) * 10.0, my + math.sin(deg) * 10.0)])
    hit = ray.intersection(ring)
    if hit.is_empty:
        return 10.0
    pts = [hit] if hit.geom_type == "Point" else [g for g in getattr(hit, "geoms", []) if g.geom_type == "Point"]
    return min((math.dist((mx, my), (p.x, p.y)) for p in pts), default=10.0)


# --------------------------------------------------------------------------
# Fix round after P5: clear reading errors code corrects (CLAUDE.md, user decisions of 22 Oct 2026)
# --------------------------------------------------------------------------

def _short_side_front(footprint: dict, front_deg: float) -> bool:
    """True when ``front_deg`` puts the front on a short side of the footprint (the width across that front at
    least ``LONG_FRONT_RATIO`` times shorter than the depth)."""
    from wenart.furniture import placer

    _rot, (w, d) = placer.front_frame(footprint, front_deg)
    return w * LONG_FRONT_RATIO <= d + 1e-9


def _code_label(f: dict, rule: str, reason: str, changed: dict, crop: Optional[str]) -> None:
    """``drawn_*`` kept and ``adjusted_by_ai`` (``by: code``) for a correction the reading's code makes (CLAUDE.md:
    every change keeps the drawn values and is labelled with the reason; the plan crop as evidence)."""
    f.setdefault("drawn_type", f.get("type"))
    f.setdefault("drawn_footprint", copy.deepcopy(f.get("footprint")))
    f.setdefault("drawn_front_deg", f.get("front_deg"))
    f.setdefault("drawn_height", f.get("height"))
    from wenart.furniture import infer as INF

    # fix round after P5, review: an earlier code record of the piece (a turned front, then the desk split) is kept
    INF.merge_code_label(f, {"by": "code", "stage": "reading", "rule": rule, "reason": reason, "changed": changed,
                             "crop": crop})


def long_side_fronts(build, items: dict) -> list[str]:
    """Fix round after P5 (module docstring): a drawn piece of a type that faces along a long side
    (``LONG_FRONT_TYPES``: a sofa, a desk, a wardrobe ...) whose front stands on a short side (an AI front applied by
    turning the footprint: P5's twin sofa f_L-1b_045, 0.82 x 1.64 m, built as a 0.82 m wide sofa) gets the long side
    the drawing gives (``_front_of``: its wall, its coffee table), else the long side facing the most room
    (``_free_ray``). Block-named pieces are left to the reader's own rule. Returns the ids changed."""
    from wenart.furniture import infer as INF

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    done = []
    for f in b["furniture"]:
        if f.get("type") not in LONG_FRONT_TYPES or f.get("front_deg") is None or f.get("build") is False \
                or f.get("source") != "from_documents" or f.get("type_method") == "block_name":
            continue
        room = rooms.get(f.get("room_id"))
        if room is None or not _short_side_front(f["footprint"], float(f["front_deg"])):
            continue
        mates = [o for o in b["furniture"] if o is not f and o.get("room_id") == room["id"]
                 and o.get("build") is not False]
        bare = dict(f, front_deg=None)
        front, why = _front_of(bare, room, mates)
        if front is None or _short_side_front(f["footprint"], front):
            ring = room_ring(room)
            ss = sides(rect(f))
            longest = max(math.dist(*s) for s in ss)
            ranked = sorted(((_free_ray(f, s, ring), k) for k, s in enumerate(ss)
                             if math.dist(*s) >= 0.999 * longest), key=lambda t: (-round(t[0], 3), t[1]))
            if not ranked:
                continue
            front = snap_front(f, outward_deg(f, ss[ranked[0][1]]))
            why = f"the long side facing the most room ({ranked[0][0]:.2f} m free)"
        old = float(f["front_deg"])
        det = items[f["id"]].details if f["id"] in items else {}
        crop = _crop(det)
        reason = (f"a {f['type']} faces along a long side: the front {old:g} deg on its short side (an AI front) is a "
                  f"reading error; front {front:g} deg: {why}" + (f"; plan crop {crop}" if crop else ""))
        _code_label(f, LONG_FRONT_RULE, reason, {"front_deg": old, "footprint": copy.deepcopy(f["footprint"])}, crop)
        INF.set_front(f, front)
        f["inferred"] = True
        f["front_inferred"] = reason
        f.setdefault("evidence", []).append(_ev(f, LONG_FRONT_RULE, reason, 0.6))
        build.warn(f"{f['id']}: {reason}")
        done.append(f["id"])
    return done


def _next_piece_id(b: dict, level_id: str) -> str:
    """The next free ``f_<level>_NNN`` furniture id of a level."""
    prefix = f"f_{level_id}_"
    used = [int(str(f["id"])[len(prefix):]) for f in b.get("furniture") or []
            if str(f.get("id", "")).startswith(prefix) and str(f["id"])[len(prefix):].isdigit()]
    return f"{prefix}{max(used, default=0) + 1:03d}"


def desk_chairs(build, items: dict) -> list[str]:
    """Fix round after P5 (module docstring; CLAUDE.md "a table footprint that includes its chairs"): a drawn desk
    with a front whose back stands on a wall and that is deeper than ``DESK_SPLIT_DEPTH_M`` holds the chair drawn in
    front of it (P5 real04: four 1.45 x 0.91 m desks, crop sym_L0_007: a 0.6 m desk at the wall and a chair back in
    front). The desk keeps ``DESK_DEPTH_M`` at its wall (``adjusted_by_ai`` by code, ``drawn_footprint`` kept) and the
    chair becomes a drawn ``office_chair`` (``DESK_CHAIR_M``) in front of it, facing it, tucked in, with the desk's
    vector evidence. Fix round after P5, review: only deeper than any real desk (``DESK_SPLIT_DEPTH_M``) and with no
    drawn seat (``DESK_SEATS``) between the cut line and ``DESK_SEAT_REACH_M`` in front of the desk
    (``_seat_in_front``). Returns the ids of the new chairs."""
    from wenart.furniture import group_checks as GC
    from wenart.furniture import placer

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    made = []
    for f in list(b["furniture"]):
        if f.get("type") != "desk" or f.get("front_deg") is None or f.get("build") is False \
                or f.get("source") != "from_documents":
            continue
        room = rooms.get(f.get("room_id"))
        if room is None:
            continue
        p = placer.drawn_piece(f)
        w, d = float(p.size[0]), float(p.size[1])
        if d <= DESK_SPLIT_DEPTH_M + 1e-9 or w < DESK_CHAIR_M[0]:
            continue
        if 2 not in wall_sides(dict(f, footprint={"center": list(p.center), "size": [w, d],
                                                  "rotation_deg": p.rotation_deg}), room_ring(room)):
            continue                                    # its back is not on a wall: not the drawn desk + chair
        seat = _seat_in_front(b, f, p)
        if seat is not None:
            build.warn(f"{f['id']}: a {w:.2f} x {d:.2f} m desk with the drawn {seat['type']} {seat['id']} in front of "
                       "it: its symbol does not hold the chair, kept as drawn")
            continue
        det = items[f["id"]].details if f["id"] in items else {}
        crop = _crop(det)
        before = copy.deepcopy(f["footprint"])
        dc = GC.to_world(p, (0.0, d / 2.0 - DESK_DEPTH_M / 2.0))
        cw, cd = DESK_CHAIR_M
        cc = GC.to_world(p, (0.0, -d / 2.0 + cd / 2.0))
        cid = _next_piece_id(b, f["level_id"])
        reason = (f"a {w:.2f} x {d:.2f} m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table "
                  f"footprint that includes its chairs): the desk keeps {DESK_DEPTH_M:.2f} m at its wall, the chair "
                  f"{cid} stands in front" + (f"; plan crop {crop}" if crop else ""))
        _code_label(f, DESK_RULE, reason, {"footprint": before}, crop)
        f["footprint"] = {"center": [round(dc[0], 4), round(dc[1], 4)], "size": [round(w, 4), DESK_DEPTH_M],
                          "rotation_deg": round(float(p.rotation_deg), 3)}
        f.setdefault("evidence", []).append(_ev(f, DESK_RULE, reason, 0.7))
        src = next((e for e in f.get("evidence") or [] if isinstance(e, dict) and e.get("method") == "vector"), None)
        ev = dict(src or _ev(f, DESK_RULE, reason, 0.7))
        ev["note"] = f"chair drawn in front of the desk {f['id']} (its symbol held both; {DESK_RULE})"
        chair = {"id": cid, "level_id": f["level_id"], "room_id": f.get("room_id"), "type": "office_chair",
                 "type_raw": None, "source": "from_documents",
                 "footprint": {"center": [round(cc[0], 4), round(cc[1], 4)], "size": [cw, cd],
                               "rotation_deg": round(G.normalise_angle(float(p.rotation_deg) + 180.0), 3)},
                 "front_deg": round(G.normalise_angle(float(f["front_deg"]) + 180.0), 3), "height": None,
                 "asset": None, "status": "unverified", "evidence": [ev, _ev(f, DESK_RULE, reason, 0.7)],
                 "type_method": CONTEXT_METHOD, "type_candidates": [], "build": True, "inferred": True,
                 "inferred_reason": f"the chair of the desk {f['id']}, drawn in front of it in the desk symbol"}
        b["furniture"].append(chair)
        build.warn(f"{f['id']}: {reason}")
        made.append(cid)
    return made


def _seat_in_front(b: dict, f: dict, p) -> Optional[dict]:
    """Fix round after P5, review: a drawn seat (``DESK_SEATS``) of the desk's room whose outline meets the zone from
    the cut line (``DESK_DEPTH_M`` from the desk's back) to ``DESK_SEAT_REACH_M`` in front of its front edge, across
    its width; ``p`` is the desk in the frame of its front (``placer.drawn_piece``). None without one."""
    from wenart.furniture import group_checks as GC

    w, d = float(p.size[0]), float(p.size[1])
    front, cut = -d / 2.0 - DESK_SEAT_REACH_M, d / 2.0 - DESK_DEPTH_M
    zone = Polygon([GC.to_world(p, (x, y)) for x, y in ((-w / 2.0, front), (w / 2.0, front), (w / 2.0, cut),
                                                        (-w / 2.0, cut))])
    seats = [o for o in b.get("furniture") or [] if o is not f and o.get("type") in DESK_SEATS
             and o.get("room_id") == f.get("room_id") and o.get("source") == "from_documents"
             and o.get("build") is not False and o.get("footprint") and rect(o).intersection(zone).area > 1e-6]
    return min(seats, key=lambda o: (round(rect(o).distance(rect(f)), 6), str(o["id"]))) if seats else None


def seat_cushions(build, items: dict) -> list[str]:
    """Fix round after P5 (module docstring; CLAUDE.md "a cushion read as a sofa"): a drawn piece no larger than
    ``CUSHION_MAX_M`` either way that lies at least ``CUSHION_INSIDE`` inside a larger built drawn seat of its room
    (P5 real04: the 0.47 x 0.48 m "ottomans" f_L-1_075..078 on the seats of the armchairs f_L-1_069..072) is that
    seat's cushion: not built (``inferred_as: detail``), ``adjusted_by_ai`` by code with the plan crop. Returns the
    ids."""
    from wenart.furniture import placer, schemas

    b = build.building
    seats = [f for f in b["furniture"] if f.get("type") in CUSHION_SEATS and f.get("build") is not False
             and f.get("source") == "from_documents" and f.get("footprint")]
    done = []
    for f in b["furniture"]:
        if f.get("build") is False or f.get("source") != "from_documents" or not f.get("footprint") \
                or f.get("type") in schemas.FIXED_TYPES or f.get("type") in CUSHION_SEATS[:2]:
            continue
        if max(float(v) for v in f["footprint"]["size"]) > CUSHION_MAX_M + 1e-9:
            continue
        poly = rect(f)
        host = None
        for s in seats:
            if s is f or s.get("room_id") != f.get("room_id"):
                continue
            if s.get("type") == "sofa_corner" and s.get("shape") != "L":
                continue            # review: without its L the box holds the open corner, which is no seat
            try:
                sp = placer.drawn_piece(s).polygon()
            except (KeyError, TypeError, ValueError):
                continue
            if sp.area > poly.area * 1.2 and poly.intersection(sp).area >= CUSHION_INSIDE * poly.area - 1e-9:
                host = s
                break
        if host is None:
            continue
        det = items[f["id"]].details if f["id"] in items else {}
        crop = _crop(det)
        share = poly.intersection(placer.drawn_piece(host).polygon()).area / poly.area
        reason = (f"a {f['footprint']['size'][0]:.2f} x {f['footprint']['size'][1]:.2f} m {f['type']} drawn "
                  f"{share:.0%} inside the {host['type']} {host['id']}: its seat cushion, not a piece of its own "
                  f"(not built)" + (f"; plan crop {crop}" if crop else ""))
        _code_label(f, CUSHION_RULE, reason, {"build": True}, crop)
        f["adjusted_by_ai"]["not_furniture"] = "seat_cushion"
        f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason, not_built_reason=reason)
        f.setdefault("evidence", []).append(_ev(f, CUSHION_RULE, reason, 0.75))
        build.warn(f"{f['id']}: {reason}")
        done.append(f["id"])
    return done


# --------------------------------------------------------------------------
# 26 Oct 2026: reading fixes (module docstring "Reading fixes of 26 Oct 2026")
# --------------------------------------------------------------------------

def _rank(f: dict) -> int:
    """How strong the evidence of a drawn piece's type is (``NEST_RANK``): a block name, then two agreeing AI passes,
    then a reading rule or a copy, then any other type; 0 for an untyped piece."""
    if f.get("type") in (None, "unknown"):
        return 0
    return NEST_RANK.get(str(f.get("type_method") or ""), 1)


def nested_outlines(build, items: dict, pending=()) -> list[str]:
    """26 Oct 2026 (module docstring): drawn pieces whose footprints are nested outlines of one piece (at least
    ``NEST_INSIDE`` of the smaller inside the bigger, centres within ``NEST_CENTRE_M``, the smaller at least
    ``NEST_AREA_MIN`` of the bigger's area and ``NEST_LONG_MIN`` of its long side) are one piece. The one with the
    strongest evidence stays (``_rank``: a block name > two agreeing AI passes > a reading rule > one pass or none; on
    a tie the outer outline); each other is merged into it: not built (``inferred_as: detail``, ``merged_into``),
    labelled ``adjusted_by_ai`` by code with the reason, the drawn values and the plan crop. Two fixed types are never
    merged here (a sink in its counter is two pieces; one fixed piece drawn twice is ``duplicates``' rule), nor an
    outline that holds other pieces too (a rug under a table with its chairs); a group with a piece whose question
    waits is left to the answers. Returns the ids merged."""
    from wenart.furniture import infer as INF
    from wenart.furniture import schemas

    b = build.building
    cands = [f for f in b["furniture"] if f.get("source") == "from_documents" and f.get("footprint")
             and f.get("type") != "stair" and not f.get("inferred_as") and not f.get("not_furniture")
             and (f.get("build") is not False or INF.untyped_drawn(f))]
    polys = {f["id"]: rect(f) for f in cands}
    parent = {f["id"]: f["id"] for f in cands}

    def root(k: str) -> str:
        while parent[k] != k:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k

    def nested(small: Polygon, big: Polygon) -> bool:
        """``small`` is a nested outline of ``big`` (the thresholds of the docstring)."""
        if small.area <= 0 or small.area > big.area or small.intersection(big).area < NEST_INSIDE * small.area - 1e-9:
            return False
        if small.centroid.distance(big.centroid) > NEST_CENTRE_M + 1e-9 or small.area < NEST_AREA_MIN * big.area:
            return False
        return max(sides_len(small)) >= NEST_LONG_MIN * max(sides_len(big)) - 1e-9

    pairs = []
    for i, a in enumerate(cands):
        for c in cands[i + 1:]:
            if a.get("level_id") != c.get("level_id"):
                continue
            small, big = (a, c) if polys[a["id"]].area <= polys[c["id"]].area else (c, a)
            if not nested(polys[small["id"]], polys[big["id"]]):
                continue
            if a["type"] in schemas.FIXED_TYPES and c["type"] in schemas.FIXED_TYPES:
                continue                        # a sink or hob in its counter (two pieces); one fixed type drawn
                                                # twice is ``duplicates``' business
            pairs.append((small, big))
    for small, big in pairs:
        pb = polys[big["id"]]
        # an outline that also holds other pieces of its own (a rug under a table and its chairs) is a group outline
        if any(o is not small and o is not big and o.get("level_id") == big.get("level_id")
               and pb.contains(polys[o["id"]].centroid) and not nested(polys[o["id"]], pb) for o in cands):
            continue
        parent[root(small["id"])] = root(big["id"])
    groups: dict[str, list[dict]] = {}
    for f in cands:
        groups.setdefault(root(f["id"]), []).append(f)
    merged = []
    for members in groups.values():
        if len(members) < 2 or any(f["id"] in pending for f in members):
            continue
        keep = max(members, key=lambda f: (_rank(f), round(polys[f["id"]].area, 6), [-ord(ch) for ch in f["id"]]))
        kw, kd = keep["footprint"]["size"][:2]
        for f in sorted(members, key=lambda g: g["id"]):
            if f is keep:
                continue
            p = polys[f["id"]]
            share = p.intersection(polys[keep["id"]]).area / p.area if p.area > 0 else 0.0
            det = items[f["id"]].details if f["id"] in items else {}
            crop = _crop(det) or reading_crop(build, f)
            w, d = f["footprint"]["size"][:2]
            reason = (f"nested outline: {f['id']} ({float(w):.2f} x {float(d):.2f} m, {f['type']}, "
                      f"{f.get('type_method') or 'none'}) and {keep['id']} ({float(kw):.2f} x {float(kd):.2f} m, "
                      f"{keep['type']}, {keep.get('type_method') or 'none'}) share their centre "
                      f"({p.centroid.distance(polys[keep['id']].centroid):.2f} m) and {share:.0%} of {f['id']} lies "
                      f"inside the other: two outlines of one piece; {keep['id']} has the stronger evidence and stays, "
                      f"{f['id']} is merged into it (not built)" + (f"; plan crop {crop}" if crop else ""))
            _code_label(f, NEST_RULE, reason, {"build": f.get("build") is not False, "type": f["type"]}, crop)
            f["adjusted_by_ai"].update(not_furniture="nested_outline", merged_into=keep["id"])
            f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason, not_built_reason=reason,
                     merged_into=keep["id"])
            f.setdefault("evidence", []).append(_ev(f, NEST_RULE, reason, 0.75))
            keep["merged_outlines"] = sorted(set(keep.get("merged_outlines") or []) | {f["id"]})
            build.warn(f"{f['id']}: {reason}")
            merged.append(f["id"])
        if keep.get("merged_outlines"):
            keep.setdefault("evidence", []).append(_ev(keep, NEST_RULE, f"holds the nested outlines "
                                                       f"{', '.join(keep['merged_outlines'])} (one piece)", 0.75))
    return merged


def sides_len(poly: Polygon) -> list[float]:
    """The side lengths of a footprint polygon."""
    return [math.dist(a, b) for a, b in sides(poly)]


def generic_rooms(build) -> list[str]:
    """26 Oct 2026 (module docstring): a room named only by a generic word (``building.generic_room_label``: "ODA",
    "Oda 2", "Room") that the ingest typed by that word (bedroom, or other / unknown) and that has no bed drawn takes
    the room type its drawn anchors name (``groups.yaml`` ``room_aliases.content``; a desk, at home in a bedroom too,
    names none), when they are typed by a block name or two agreeing AI passes (``GENERIC_STRONG``) and all name one
    type (a living room's dining table is no second type); a kitchen only with a drawn sink or hob. Logged
    ``corrected_by_ai`` with the reason, the anchors as evidence and the type before. Returns the ids changed."""
    from wenart.furniture import groups as GR

    b = build.building
    content = dict(GR.room_aliases().get("content") or {})
    changed = []
    for room in b.get("rooms") or []:
        label = room.get("label_raw") or room.get("label") or ""
        if not B.generic_room_label(label) or room.get("room_type") not in ("bedroom", "other", "unknown"):
            continue
        mine = [f for f in b.get("furniture") or [] if f.get("room_id") == room.get("id")
                and f.get("source") == "from_documents" and f.get("build") is not False]
        if any(f.get("type") in GENERIC_BEDS for f in mine):
            continue                            # a bed is drawn: the generic word's bedroom stands
        # 27 Oct 2026 (real06's r_L1_oda_2: "*SIFONIYER" written in it, as in the two other bedrooms of the floor):
        # a furniture name text of a bedroom piece in the room keeps the bedroom (text outranks the AI passes)
        if room.get("room_type") == "bedroom" and any(
                t.get("room_id") == room.get("id") and t.get("type") in BEDROOM_NAMED
                for t in b.get("furniture_texts") or [] if isinstance(t, dict)):
            continue
        anchors = [f for f in mine if f.get("type_method") in GENERIC_STRONG and f.get("type") in content
                   and content[f["type"]] not in ("other", "bedroom")]     # a desk is at home in a bedroom too
        kinds = {content[f["type"]] for f in anchors}
        if "kitchen" in kinds and not any(f.get("type") in ("sink_kitchen", "stove") for f in mine):
            kinds.discard("kitchen")            # a counter alone does not make a kitchen
        if "living" in kinds and kinds <= {"living", "dining"}:
            kinds = {"living"}                  # a living room holds a dining set too
        if len(kinds) != 1:
            continue
        kind = kinds.pop()
        if kind == room.get("room_type"):
            continue
        ids = sorted(f["id"] for f in anchors if content[f["type"]] == kind)
        reason = (f"the room is named only by the generic word {label!r} (read as {room.get('room_type')}); no bed is "
                  f"drawn and its drawn anchors {', '.join(ids)} ("
                  + ", ".join(sorted({f['type'] for f in anchors if f['id'] in ids}))
                  + f", typed by a block name or two agreeing AI passes) name a {kind} room")
        room["corrected_by_ai"] = {"reason": reason, "rule": GENERIC_ROOM_RULE,
                                   "evidence": {"pieces": ids, "label": label},
                                   "before": {"room_type": room.get("room_type")}}
        room["room_type"] = kind
        room.setdefault("evidence", []).append({"file": (room.get("evidence") or [{}])[0].get("file") or
                                                "building.json", "method": "inferred", "confidence": 0.7,
                                                "rule": GENERIC_ROOM_RULE, "text": reason})
        build.warn(f"{room['id']}: room type {room['corrected_by_ai']['before']['room_type']} -> {kind} "
                   f"({GENERIC_ROOM_RULE}): {reason}")
        changed.append(room["id"])
    return changed


PASSAGE_TYPES = ("door", "opening")
PASSAGE_SIDE_SHARE = 0.5          # a side this much along a door or an open passage is no wall side


PASSAGE_APPROACH_M = 0.9          # a door's approach kept clear in front of it (a counter stops short of it)
PASSAGE_REACH_M = 0.15            # ... and this far past its jambs (a counter may end this close to a door frame)
LEG_MIN_M = 0.6                   # a counter leg shorter than this after the cut is no leg


def passage_spans(b: dict, level_id: Optional[str] = None) -> list:
    """The spans (``LineString``s on their walls' centre lines) of the doors and open passages of ``level_id`` (pure;
    29 Oct 2026, ``passage_share``): an untyped gap counts only between two rooms (in an outer wall the reading makes it
    a window)."""
    walls = {w["id"]: w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")}
    rooms = [r for r in b.get("rooms") or [] if isinstance(r, dict) and len(r.get("polygon") or []) >= 3]
    spans = []
    for o in b.get("openings") or []:
        if not isinstance(o, dict) or o.get("type") not in PASSAGE_TYPES or not o.get("center"):
            continue
        if level_id is not None and o.get("level_id") not in (None, level_id):
            continue
        w = walls.get(o.get("wall_id"))
        if w is None:
            continue
        (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
        length = math.dist((x0, y0), (x1, y1))
        if length <= 1e-6:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        cx, cy = (float(v) for v in o["center"][:2])
        if o.get("type") == "opening":
            off = float(w.get("thickness") or 0.2) / 2.0 + 0.3
            sides_in = [any(Polygon(r["polygon"]).buffer(0).contains(Point(cx + nx * off, cy + ny * off))
                            for r in rooms if r.get("level_id") in (None, o.get("level_id")))
                        for nx, ny in ((-uy, ux), (uy, -ux))]
            if not all(sides_in):
                continue
        h = float(o.get("width") or 0.0) / 2.0
        spans.append(LineString([(cx - ux * h, cy - uy * h), (cx + ux * h, cy + uy * h)]))
    return spans


def passage_zone(b: dict, level_id: Optional[str] = None, reach: float = PASSAGE_REACH_M):
    """The floor kept clear in front of the doors and passages of ``level_id`` (pure; 29 Oct 2026): each span
    lengthened by ``reach`` at both ends and ``PASSAGE_APPROACH_M`` deep on both sides; None without a passage."""
    from shapely.ops import unary_union

    zones = []
    for sp in passage_spans(b, level_id):
        (ax, ay), (cx, cy) = sp.coords[0], sp.coords[-1]
        length = math.dist((ax, ay), (cx, cy))
        if length <= 1e-6:
            continue
        ux, uy = (cx - ax) / length, (cy - ay) / length
        line = LineString([(ax - ux * reach, ay - uy * reach), (cx + ux * reach, cy + uy * reach)])
        zones.append(line.buffer(PASSAGE_APPROACH_M, cap_style=2))
    return unary_union(zones) if zones else None


def passage_share(a, c, b: dict, level_id: Optional[str] = None, reach: float = 0.35) -> float:
    """The share of the segment ``a``-``c`` that runs along a door or an open passage of the building (pure; 29 Oct
    2026, real06: the kitchen outline's south side lay along the kitchen's 2.9 m open entrance from the living room
    and got a counter leg; the architect then made the doorway a serving hatch and the AI a door behind the counter):
    sampled at 21 points, a point counts when it lies within ``reach`` of the span of a ``PASSAGE_TYPES`` opening on its
    wall."""
    spans = passage_spans(b, level_id)
    if not spans:
        return 0.0
    near = 0
    for k in range(21):
        t = k / 20.0
        q = Point(a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t)
        if any(sp.distance(q) <= reach for sp in spans):
            near += 1
    return near / 21.0


def outline_to_walls(poly: Polygon, ring, room_id: str, pieces: list,
                     building: Optional[dict] = None) -> tuple[Polygon, list[str]]:
    """``(polygon, notes)``: a kitchen outline with every side that stands short of a wall extended to it (pure; 28 Oct
    2026, ``KITCHEN_OUTLINE_GAP_M``): a side not on a wall whose outward gap to the room outline is at most that, the far
    edge of the gap on a wall, and a built drawn kitchen fixture of the room (``KITCHEN_GAP_TYPES``) with at least
    ``KITCHEN_GAP_SHARE`` of its footprint in the gap."""
    from wenart.furniture import infer as INF

    notes = []
    centre = poly.centroid
    for a, c in list(sides(poly)):
        if INF.side_on_wall(a, c, ring):
            continue
        length = math.dist(a, c)
        if length <= 1e-6:
            continue
        ux, uy = (c[0] - a[0]) / length, (c[1] - a[1]) / length
        nx, ny = uy, -ux
        mx, my = (a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0
        if (mx - centre.x) * nx + (my - centre.y) * ny < 0:
            nx, ny = -nx, -ny                                       # outward, away from the outline
        ray = LineString([(mx + nx * 0.01, my + ny * 0.01), (mx + nx * KITCHEN_OUTLINE_GAP_M, my + ny * KITCHEN_OUTLINE_GAP_M)])
        hit = ray.intersection(ring)
        if hit.is_empty:
            continue
        pts = [g for g in getattr(hit, "geoms", [hit]) if g.geom_type == "Point"]
        if not pts:
            continue
        gap = min(math.dist((mx, my), (q.x, q.y)) for q in pts)
        far = ((a[0] + nx * gap, a[1] + ny * gap), (c[0] + nx * gap, c[1] + ny * gap))
        if not INF.side_on_wall(far[0], far[1], ring):
            continue
        if building is not None and passage_share(far[0], far[1], building) >= PASSAGE_SIDE_SHARE:
            continue                                                # the way in, not a wall to reach
        band = Polygon([a, c, far[1], far[0]])
        held = []
        for f in pieces:
            if f.get("room_id") != room_id or f.get("type") not in KITCHEN_GAP_TYPES or f.get("build") is False:
                continue
            fp = rect(f)
            if fp.area > 0 and fp.intersection(band).area >= KITCHEN_GAP_SHARE * fp.area - 1e-9:
                held.append(f["id"])
        if not held:
            continue
        poly = poly.union(band).buffer(0)
        poly = Polygon(poly.minimum_rotated_rectangle.exterior.coords) if poly.geom_type != "Polygon" else poly
        notes.append(f"the outline stopped {gap:.2f} m short of the wall behind {', '.join(sorted(held))}: the run "
                     f"reaches that wall")
    return poly, notes


def kitchen_outlines(build, items: dict, pending=()) -> list[str]:
    """26 Oct 2026 (module docstring): an untyped drawn piece in a kitchen that is deeper than a counter both ways
    (``KITCHEN_OUTLINE_MIN_M``) and holds a sink's drain or a hob's burners (the extraction's
    ``details["kitchen_signs"]``) is the kitchen run drawn as one outline: one counter leg 0.60 m deep (the kitchen
    run's depth, ``groups.yaml``) along each of its sides that stands on a wall (``infer.back_wall_side``'s test),
    the corner square to the longer leg; the legs are drawn pieces (``type_method: inferred``, ``drawn_footprint``
    the outline, ``adjusted_by_ai`` by code, its vector evidence, the plan crop) facing into the room, and the outline
    is not built (``inferred_as: detail``, ``replaced_by``). An outline with no side on a wall is left for review.
    Returns the ids of the new legs."""
    from wenart.furniture import groups as GR
    from wenart.furniture import infer as INF

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    depth = float(((GR.load_groups().get("kitchen_run") or {}).get("run") or {}).get("depth") or 0.60)
    made = []
    for f in list(b["furniture"]):
        room = rooms.get(f.get("room_id") or "")
        det = items[f["id"]].details if f["id"] in items else {}
        signs = det.get("kitchen_signs") or {}
        if room is None or f["id"] in pending or not INF.untyped_drawn(f) or not signs:
            continue
        if room.get("room_type") != "kitchen" and not ("sink" in signs and "hob" in signs):
            continue
        if min(float(v) for v in f["footprint"]["size"][:2]) <= KITCHEN_OUTLINE_MIN_M:
            continue
        poly = rect(f)
        ring = room_ring(room)
        poly, reached = outline_to_walls(poly, ring, room["id"], b["furniture"], b)
        if reached:      # the union's float noise (-2e-16) made GEOS keep the corner in a leg: snapped to 1 micrometre
            poly = Polygon([(round(x, 6) + 0.0, round(y, 6) + 0.0) for x, y in poly.exterior.coords]).simplify(1e-6)
        ss = sides(poly)
        on_wall = [k for k, (a, c) in enumerate(ss) if INF.side_on_wall(a, c, ring)]
        if not on_wall:
            continue
        strips = []
        for k in on_wall:
            a, c = ss[k]
            ux, uy = (c[0] - a[0]) / math.dist(a, c), (c[1] - a[1]) / math.dist(a, c)
            centre = poly.centroid
            mx, my = (a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0
            nx, ny = -uy, ux                                        # one normal; turn it into the outline
            if (centre.x - mx) * nx + (centre.y - my) * ny < 0:
                nx, ny = -nx, -ny
            strip = Polygon([a, c, (c[0] + nx * depth, c[1] + ny * depth), (a[0] + nx * depth, a[1] + ny * depth)])
            strips.append((math.dist(a, c), k, strip.intersection(poly), (ux, uy), (nx, ny)))
        strips.sort(key=lambda s: (-s[0], s[1]))
        taken = None
        legs = []
        for _length, _k, strip, axis, normal in strips:
            part = strip if taken is None else strip.difference(taken)   # the corner square goes to the longer leg
            part = max(getattr(part, "geoms", [part]), key=lambda g: g.area) if not part.is_empty else part
            if part.is_empty or part.area < 0.3 * depth:
                continue
            taken = strip if taken is None else taken.union(strip)
            legs.append((part, axis, normal))
        if not legs:
            continue
        det_crop = _crop(det) or reading_crop(build, f)
        src = next((e for e in f.get("evidence") or [] if isinstance(e, dict) and e.get("method") == "vector"), None)
        what = ", ".join(f"{k}: {v} circles" for k, v in sorted(signs.items()))
        ids = []
        # 29 Oct 2026: a leg stops short of a door or an open passage (its approach stays clear); what is left under
        # LEG_MIN_M is no leg (real06: the outline's south side lay along the kitchen's 2.9 m open entrance)
        zone = passage_zone(b, f.get("level_id"))
        trimmed = []
        for part, (ux, uy), (nx, ny) in legs:
            pts = list(part.exterior.coords)
            us, ns = [p[0] * ux + p[1] * uy for p in pts], [p[0] * nx + p[1] * ny for p in pts]
            u0, u1, n0, n1 = min(us), max(us), min(ns), max(ns)
            if zone is not None and not zone.is_empty:
                steps = max(2, int(math.ceil((u1 - u0) / 0.05)))
                free = []
                for k in range(steps + 1):
                    u = u0 + (u1 - u0) * k / steps
                    cross = LineString([(u * ux + n0 * nx, u * uy + n0 * ny), (u * ux + n1 * nx, u * uy + n1 * ny)])
                    free.append(not zone.intersects(cross))
                best, run = None, None
                for k, ok in enumerate(free + [False]):
                    if ok and run is None:
                        run = k
                    elif not ok and run is not None:
                        if best is None or k - run > best[1] - best[0]:
                            best = (run, k - 1)
                        run = None
                if best is None:
                    continue
                a0, a1 = u0 + (u1 - u0) * best[0] / steps, u0 + (u1 - u0) * best[1] / steps
                if a1 - a0 < LEG_MIN_M - 1e-9:
                    continue
                if a1 - a0 < u1 - u0 - 1e-6:
                    part = Polygon([(a0 * ux + n0 * nx, a0 * uy + n0 * ny), (a1 * ux + n0 * nx, a1 * uy + n0 * ny),
                                    (a1 * ux + n1 * nx, a1 * uy + n1 * ny), (a0 * ux + n1 * nx, a0 * uy + n1 * ny)])
            trimmed.append((part, (ux, uy), (nx, ny)))
        if not trimmed:
            continue
        for part, (ux, uy), (nx, ny) in trimmed:
            pts = list(part.exterior.coords)
            us, ns = [p[0] * ux + p[1] * uy for p in pts], [p[0] * nx + p[1] * ny for p in pts]
            mu, mn = (min(us) + max(us)) / 2.0, (min(ns) + max(ns)) / 2.0
            c = Point(mu * ux + mn * nx, mu * uy + mn * ny)
            e0, e1 = max(us) - min(us), max(ns) - min(ns)
            front = round(math.degrees(math.atan2(ny, nx)) % 360.0, 3)
            lid = _next_piece_id(b, f["level_id"])
            reason = (f"the kitchen run drawn as one {float(f['footprint']['size'][0]):.2f} x "
                      f"{float(f['footprint']['size'][1]):.2f} m outline {f['id']} with its fixtures ({what}) in "
                      f"the kitchen: a counter leg {e0:.2f} x {e1:.2f} m along its wall side, facing the "
                      f"room (inferred)" + "".join(f"; {n}" for n in reached)
                      + (f"; plan crop {det_crop}" if det_crop else ""))
            ev = dict(src or _ev(f, KITCHEN_OUTLINE_RULE, reason, 0.6))
            ev["note"] = f"counter leg of the kitchen outline {f['id']} ({KITCHEN_OUTLINE_RULE})"
            # the leg: its long side along the wall, the front into the room (rotation = front + 90, the -Y front)
            leg = {"id": lid, "level_id": f["level_id"], "room_id": f.get("room_id"), "type": "kitchen_counter",
                   "type_raw": None, "source": "from_documents",
                   "footprint": {"center": [round(c.x, 4), round(c.y, 4)], "size": [round(e0, 4), round(e1, 4)],
                                 "rotation_deg": round((front + 90.0) % 360.0, 3)},
                   "front_deg": front, "height": None, "asset": None, "status": "unverified",
                   "evidence": [ev, _ev(f, KITCHEN_OUTLINE_RULE, reason, 0.6)], "type_method": INFER_METHOD,
                   "type_candidates": [], "build": True, "inferred": True, "inferred_reason": reason,
                   "drawn_type": "unknown", "drawn_footprint": copy.deepcopy(f["footprint"]),
                   "drawn_front_deg": f.get("front_deg"), "drawn_height": f.get("height"),
                   "adjusted_by_ai": {"by": "code", "stage": "reading", "rule": KITCHEN_OUTLINE_RULE,
                                      "reason": reason, "changed": {"type": "unknown",
                                                                     "footprint": copy.deepcopy(f["footprint"])},
                                      "crop": det_crop}}
            b["furniture"].append(leg)
            ids.append(lid)
        reason = (f"the kitchen run drawn as one outline with its fixtures ({what}): replaced by its counter legs "
                  f"{', '.join(ids)} along the walls (not built)" + (f"; plan crop {det_crop}" if det_crop else ""))
        _code_label(f, KITCHEN_OUTLINE_RULE, reason, {"build": f.get("build") is not False}, det_crop)
        f["adjusted_by_ai"]["not_furniture"] = "kitchen_outline"
        f.update(build=False, inferred=True, inferred_as="detail", inferred_reason=reason, not_built_reason=reason,
                 replaced_by=ids)
        f.setdefault("evidence", []).append(_ev(f, KITCHEN_OUTLINE_RULE, reason, 0.6))
        build.warn(f"{f['id']}: {reason}")
        made += ids
    return made


# --------------------------------------------------------------------------
# 6. Kitchen zones of open plans
# --------------------------------------------------------------------------

WET_ROOM_TYPES = ("bathroom", "wc", "toilet", "shower")
VANITY_RULE = "reading.wet_room_vanity"


def wet_room_vanities(build) -> list[str]:
    """26 Oct 2026 (full suite with LibreDWG: real03's bathroom vanities with their basin's drain were read as a kitchen
    counter and a kitchen sink, and each bathroom got an "open kitchen"): in a bathroom, WC or shower room a counter or
    a kitchen sink the code typed (not the AI) is the vanity: the counter becomes the washbasin (a vanity unit, its
    footprint kept), a sink inside it is its basin (not built, ``replaced_by``), a sink alone is the washbasin. The
    drawn type stays (``drawn_type``), ``adjusted_by_ai`` (by code) with the reason. A kitchen's sink cabinet is drawn
    the same way, so only the room tells them apart. Returns the ids of the changed pieces."""
    b = build.building
    wet = {r["id"] for r in b.get("rooms") or [] if str(r.get("room_type") or "") in WET_ROOM_TYPES}
    changed = []
    by_room: dict = {}
    for f in b.get("furniture") or []:
        if f.get("room_id") in wet and f.get("build") is not False and f.get("type_method") in ("rule", "inferred") \
                and f.get("type") in ("kitchen_counter", "sink_kitchen"):
            by_room.setdefault(f["room_id"], []).append(f)
    for rid, pieces in sorted(by_room.items()):
        counters = [f for f in pieces if f["type"] == "kitchen_counter"]
        for f in pieces:
            host = next((c for c in counters if c is not f and rect(c).buffer(0.05).contains(rect(f).centroid)), None) \
                if f["type"] == "sink_kitchen" else None
            f.setdefault("drawn_type", f["type"])
            if host is not None:
                why = f"the basin of the vanity {host['id']} in the {rid} wet room, not a kitchen sink"
                f.update(build=False, inferred_as="detail", replaced_by=host["id"], not_built_reason=why)
            else:
                why = (f"a {f['type'].replace('_', ' ')} read in the wet room {rid}: its vanity with the basin, a "
                       f"washbasin")
                f["type"] = "washbasin"
            f["adjusted_by_ai"] = {"by": "code", "rule": VANITY_RULE, "reason": why}
            f.setdefault("evidence", []).append(_ev(f, VANITY_RULE, why, 0.8))
            build.warn(f"{f['id']}: {why}")
            changed.append(f["id"])
    return changed


def kitchen_zones(build) -> int:
    """Step 6 (see the module docstring; contract §13.3). Returns the number of zones."""
    b = build.building
    n = 0
    for room in b.get("rooms") or []:
        # 26 Oct 2026: never an open kitchen in a bathroom, WC or shower room (a vanity read as a counter there)
        if room.get("room_type") in ("kitchen", "bathroom", "wc", "toilet", "shower") or \
                len(room.get("polygon") or []) < 3:
            continue
        pieces = [f for f in b["furniture"] if f.get("room_id") == room["id"] and f["type"] in KITCHEN_ZONE_TYPES
                  and f.get("build") is not False]
        if not any(f["type"] in ("kitchen_counter", "sink_kitchen", "stove", "fridge", "kitchen_island")
                   for f in pieces):
            continue
        room_poly = Polygon(room["polygon"])
        room_poly = room_poly if room_poly.is_valid else room_poly.buffer(0)
        zone = unary_union([rect(f).buffer(ZONE_AISLE_M, join_style=2) for f in pieces]).intersection(room_poly)
        zone = zone.convex_hull.intersection(room_poly)
        if zone.is_empty:
            continue
        geom = zone if zone.geom_type == "Polygon" else max(getattr(zone, "geoms", [zone]), key=lambda g: g.area)
        if geom.geom_type != "Polygon":
            continue
        geom = geom.simplify(0.01)
        ids = sorted(f["id"] for f in pieces)
        text = (f"kitchen fixtures {', '.join(ids)} in a {room.get('room_type')} room: an open kitchen; the zone is "
                f"them and the {ZONE_AISLE_M:.1f} m in front of them")
        room["zones"] = [z for z in room.get("zones") or [] if z.get("kind") != "kitchen"] + [{
            "zone_id": f"{room['id']}_kitchen", "kind": "kitchen",
            "polygon": [[round(x, 4), round(y, 4)] for x, y in list(geom.exterior.coords)[:-1]],
            "piece_ids": ids, "evidence": [_ev(pieces[0], ZONE_RULE, text, 0.8)]}]
        build.warn(f"{room['id']}: kitchen zone ({len(ids)} pieces): {text}")
        n += 1
    return n


# --------------------------------------------------------------------------
# 7. Never a box
# --------------------------------------------------------------------------

def never_a_box(build, items: dict, pending: Optional[set] = None) -> int:
    """Step 7: every piece still ``unknown`` is not built and listed in ``building["needs_review"]`` (its crop and
    reason); outlines, details, columns and decor (``inferred_as``) are explained and not listed. A piece whose AI
    question waits for its answers is not built either, but not listed (the pipeline lists the open questions).

    Fix round after P3 (16-17 Oct 2026): a piece that carries the waiting reason (``WAITS_REASON``) from an earlier
    pass but no longer waits (not in ``pending``) gets its build flag and reason back and goes through the rule like
    any untyped piece (listed in ``needs_review``): the reason never outlives the wait (CLAUDE.md: no untyped piece
    is left unexplained).

    26 Oct 2026: a furniture name text near the piece that did not type it says why in the reason
    (``infer.name_text_note``)."""
    from wenart.furniture import infer as INF

    b = build.building
    b.setdefault("needs_review", [])
    listed = {n["id"] for n in b["needs_review"]}
    n = 0
    for f in b["furniture"]:
        if f["type"] != "unknown" or f.get("inferred_as") in EXPLAINED_AS or f["id"] in listed:
            continue
        if f["id"] in (pending or set()):
            if f.get("build") is not False:
                f["build"] = False
                f["not_built_reason"] = WAITS_REASON
            continue
        if f.get("not_built_reason") == WAITS_REASON:
            # The wait is over (fix round after P3): the flag and the reason were the wait's alone.
            f.pop("not_built_reason", None)
            f["build"] = True
        det = items[f["id"]].details if f["id"] in items else {}
        if f.get("build") is False and not det.get("oversize"):
            # Already not built for a reason (both AI passes: not furniture; a detail of a counter leg): the
            # building says which, so no unexplained box is left.
            why = det.get("reason") or (f.get("evidence") or [{}])[0].get("note")
            if why and not (f.get("not_built_reason") or f.get("inferred_reason")):
                f["not_built_reason"] = why
            continue
        if f.get("build") is not False:
            f["build"] = False
            f["not_built_reason"] = "untyped (CLAUDE.md: no untyped piece is built)"   # the reason, not a source
        elif not f.get("not_built_reason"):
            f["not_built_reason"] = det.get("reason") or "a drawn cluster larger than 4.5 m that the re-read could " \
                                                         "not split (CLAUDE.md: no untyped piece is built)"
        cands = sorted({c.get("type") for c in f.get("type_candidates") or [] if c.get("type")})
        size = " x ".join(f"{v:.2f}" for v in f["footprint"]["size"])
        named = INF.name_text_note(b, f)              # 26 Oct 2026: a furniture name text near it, and why not used
        reason = (f"drawn piece {size} m in {f.get('room_id') or 'no room'} has no type"
                  + (f" (AI passes: {', '.join(cands)})" if cands else "")
                  + (f"; {det.get('reason') or det.get('note')}" if det.get("reason") or det.get("note") else "")
                  + (f"; {named}" if named else "")
                  + ": not built")
        b["needs_review"].append({"id": f["id"], "kind": "untyped_piece", "reason": reason, "crop": _crop(det),
                                  "room_id": f.get("room_id"), "level_id": f["level_id"]})
        n += 1
    return n


def _refresh_rooms(b: dict) -> None:
    """A room whose only drawn pieces were symbols has no documented furniture."""
    with_pieces = {f.get("room_id") for f in b["furniture"] if f.get("source") == "from_documents"}
    for r in b.get("rooms") or []:
        if r.get("has_documented_furniture") and r["id"] not in with_pieces:
            r["has_documented_furniture"] = False


# --------------------------------------------------------------------------
# The hook
# --------------------------------------------------------------------------

def furniture_texts(build, works: dict) -> list[dict]:
    """26 Oct 2026 (``wenart.furniture.names``, module docstring): every furniture name text of the read plan pages
    (``names.furniture_name`` on the inventory's text rows, ``source_items.text_rows``): ``{"id", "level_id",
    "room_id", "text", "type", "types", "family", "word", "pos", "layer", "file", "page", "method"}``, the page whose
    questions are asked first; the same name on two pages of a level (``NAME_TEXT_SAME_M``) once."""
    from wenart.furniture import names as NM
    from wenart.ingest import source_items as SI

    b = build.building
    out: list[dict] = []
    seen_ids: set = set()
    for w in sorted(_works(build, works), key=lambda w: 1 if _not_asked(w) else 0):
        ex = getattr(w, "extraction", None)
        record = getattr(w, "record", None)
        if ex is None or record is None or not ex.transform_to_building:
            continue
        level = record.level_id
        for row in SI.text_rows(ex, "", list(ex.transform_to_building)):
            hit = NM.furniture_name(row)
            if hit is None or row["id"] in seen_ids:
                continue
            pos = [float(row["pos"][0]), float(row["pos"][1])]
            if any(t["level_id"] == level and (t["type"], t["family"]) == (hit["type"], hit["family"])
                   and math.dist(t["pos"], pos) <= NAME_TEXT_SAME_M for t in out):
                continue
            seen_ids.add(row["id"])
            out.append({"id": row["id"], "level_id": level, "room_id": NM.room_of_point(b, level, pos),
                        "text": row["text"],
                        "type": hit["type"], "types": list(hit["types"]), "family": hit["family"],
                        "word": hit["word"], "pos": pos, "layer": row.get("layer"), "file": record.file,
                        "page": record.page if record.format == "pdf" else None,
                        "method": row.get("method") or "vector"})
    return sorted(out, key=lambda t: (str(t["level_id"]), str(t["id"])))


def zone_labels(build, works: dict) -> list[dict]:
    """26 Oct 2026 (``names.zone_records``): the zone labels of the rooms: every label block (its first name run of the
    inventory's text rows) standing in a room whose zone kind differs from the room's type ("YEMEK BÖLÜMÜ" in the
    salon: a dining zone), with its zone (the part of the room nearer to it than to the room's other labels) and the
    zone's anchors (the dining table); the page whose questions are asked first."""
    from wenart.furniture import names as NM
    from wenart.ingest import source_items as SI

    b = build.building
    rooms = {r["id"]: r for r in b.get("rooms") or [] if len(r.get("polygon") or []) >= 3}
    by_room: dict[str, list[dict]] = {}
    files: dict[str, str] = {}
    for w in sorted(_works(build, works), key=lambda w: 1 if _not_asked(w) else 0):
        ex = getattr(w, "extraction", None)
        record = getattr(w, "record", None)
        if ex is None or record is None or not ex.transform_to_building:
            continue
        for row in SI.text_rows(ex, "", list(ex.transform_to_building)):
            if row.get("label_part") != "name" or row.get("label_id") not in (None, row["id"]):
                continue
            rid = NM.room_of_point(b, record.level_id, row["pos"])
            if rid is None or rid not in rooms:
                continue
            by_room.setdefault(rid, []).append(row)
            files.setdefault(rid, record.file)
    out: list[dict] = []
    for rid in sorted(by_room):
        out += NM.zone_records(b, rooms[rid], by_room[rid], file=files.get(rid))
    return out


def chimney_texts(build, works: dict) -> list[dict]:
    """29 Oct 2026 (lesson UL109, ``wenart.blender.chimney``; the readings knew no fireplace: a "ŞÖMİNE" or "BACA"
    text that is no room label was read by nothing): every text of the read plan pages that names a fireplace, a wood
    stove, a flue or a boiler room (``chimney.source_word``: Turkish, English, German, French, Italian and Spanish
    words; never an air, light or lift shaft or a cooker hood), the page whose questions are asked first: ``{"id",
    "level_id", "room_id", "text", "kind", "word", "pos", "layer", "file", "page", "method"}``. The chimney rule builds
    their stack through the roof (``chimney.drawn_sources``); a room label is also kept here (the rule takes one stack
    per room)."""
    from wenart.blender import chimney as CH
    from wenart.furniture import names as NM
    from wenart.ingest import source_items as SI

    b = build.building
    out: list[dict] = []
    seen_ids: set = set()
    for w in sorted(_works(build, works), key=lambda w: 1 if _not_asked(w) else 0):
        ex = getattr(w, "extraction", None)
        record = getattr(w, "record", None)
        if ex is None or record is None or not ex.transform_to_building:
            continue
        level = record.level_id
        for row in SI.text_rows(ex, "", list(ex.transform_to_building)):
            hit = CH.source_word(row["text"])
            if hit is None or row["id"] in seen_ids:
                continue
            seen_ids.add(row["id"])
            pos = [float(row["pos"][0]), float(row["pos"][1])]
            out.append({"id": row["id"], "level_id": level, "room_id": NM.room_of_point(b, level, pos),
                        "text": row["text"], "kind": hit[0], "word": hit[1], "pos": pos, "layer": row.get("layer"),
                        "file": record.file, "page": record.page if record.format == "pdf" else None,
                        "method": row.get("method") or "vector"})
    return sorted(out, key=lambda t: (str(t["level_id"]), str(t["id"])))


def resolve_named_conflicts(build) -> int:
    """26 Oct 2026: the ``symbol_type_disagreement`` conflict of a piece typed by a furniture name text, a zone label or
    the missing member the AI passes named (``infer`` name_text / zone_label / ai_named_members) gets that decision as
    its resolution (it said "unresolved: ... kept as unknown"). Returns the number of conflicts resolved."""
    from wenart.furniture import infer as INF

    b = build.building
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    n = 0
    for c in list(getattr(build, "raw_conflicts", []) or []) + list(b.get("conflicts") or []):
        if c.get("kind") != "symbol_type_disagreement" or not str(c.get("resolution") or "").startswith("unresolved"):
            continue
        f = next((by_id[i] for i in c.get("element_ids") or [] if i in by_id), None)
        if f is None or f.get("type") in (None, "unknown"):
            continue
        rules = {str(e.get("rule") or "") for e in f.get("evidence") or [] if isinstance(e, dict)}
        if f.get("type_method") not in (INF.NAME_TEXT_METHOD, INF.ZONE_LABEL_METHOD) and INF.AI_MEMBER_RULE not in rules:
            continue
        how = f.get("type_method") if f.get("type_method") != "inferred" else INF.AI_MEMBER_METHOD
        c["resolution"] = (f"typed {f['type']} by code ({how}): {str(f.get('inferred_reason') or '')[:240]}; "
                           f"inferred, listed in the report")
        n += 1
    return n


def read_furniture(build, works: dict) -> None:
    b = build.building
    # 26 Oct 2026 (``furniture_texts``): the furniture names written as texts of the plan, for the code typing
    # (``infer.type_by_code`` method name_text, ``infer.name_text_retypes``) and the pipeline's named pieces
    b["furniture_texts"] = furniture_texts(build, works)
    for t in b["furniture_texts"]:
        build.warn(f"{t['id']}: furniture name text {t['text']!r} on {t['level_id']} at ({t['pos'][0]:.2f}, "
                   f"{t['pos'][1]:.2f}) m in {t['room_id'] or 'no room'} names a "
                   f"{t['type'] or t['family'] + ' (' + ' / '.join(t['types']) + ')'}")
    # 26 Oct 2026 (``zone_labels``): a second label of a room names a zone of it and the anchor drawn there
    b["zone_labels"] = zone_labels(build, works)
    for z in b["zone_labels"]:
        build.warn(f"{z['id']}: zone label {z['text']!r} in {z['room_id']}: a {z['kind']} zone "
                   f"({', '.join(z['anchors'])}) of {len(z['zone'])} corners around ({z['pos'][0]:.2f}, "
                   f"{z['pos'][1]:.2f}) m")
    # 29 Oct 2026 (lesson UL109, ``chimney_texts``): a fireplace, stove, flue or boiler-room text of the plan, for the
    # chimney rule (written only when the plans hold one)
    texts = chimney_texts(build, works)
    if texts:
        b["chimney_texts"] = texts
    for t in texts:
        build.warn(f"{t['id']}: {t['kind'].replace('_', ' ')} text {t['text']!r} on {t['level_id']} at "
                   f"({t['pos'][0]:.2f}, {t['pos'][1]:.2f}) m in {t['room_id'] or 'no room'}: the chimney rule builds "
                   f"its stack through the roof")
    items = _items(build, works)
    pending = _pending(build, works)
    symbols = move_symbols(build, items, works)
    log_overrides(build, items)
    # 26 Oct 2026 (module docstring): a room named only "Oda" takes the type its agreed drawn anchors name
    rooms_retyped = generic_rooms(build)
    # Build round 3 (K3): the open questions are held in every mode by the steps before the size inference (a block
    # copy never decides one: the code typing below does, and withdraws it, or the AI does).
    held = set(pending) | open_questions(build, works, items)
    # Fix round after P4b (module docstring): the pieces this round's answers typed (and their block copies) are
    # untyped again in the code typing's view of the building, as in the first reading.
    copied_from: dict[str, list[str]] = {}
    copied = copies(build, items, held, copied_from)
    from_answers = answer_typed(build, works, items, copied_from)
    # 26 Oct 2026 (module docstring): nested outlines of one piece are one piece, before any typing
    nested = nested_outlines(build, items, held)
    # Milestone 13 (K3), build round 3 (lead decision): code first, in every run. ``infer.code_types`` runs before
    # the context rules (the twin room, another level, the block name, the missing group member), on the open
    # questions too; then the context rules type what code left, on the open questions too; both kinds withdraw
    # their questions (``withdraw_questions`` with the method). Every step up to the size inference treats a piece
    # with an open question the same way in every mode (``open_questions``: no front for it yet), so the AI is asked
    # the same questions with --no-ai, in the first plain run and in the run with the answers.
    typed_by: dict[str, str] = {}
    withdrawn: dict[str, str] = {}
    context: dict[str, int] = {}
    pending = set(pending)

    def code_pass() -> list[str]:
        """``code_first`` on every untyped piece; the typed ones withdraw their questions."""
        coded, methods = code_first(build, from_answers)
        if coded:
            typed_by.update(methods)
            withdrawn.update(withdraw_questions(build, works, items, coded, methods))
            pending.difference_update(coded)
            held.difference_update(coded)
        return coded

    def context_pass(corner_only: bool = False) -> None:
        """One pass of the context rules on every unknown piece, open questions included; the typed ones withdraw
        their questions. Fix round after P5: ``corner_only`` runs the corner-sofa rule alone (``corner_sofa_pass``)."""
        before = unknown_ids(build)
        if corner_only:
            n = len(corner_sofa_pass(build, items))
            if n:
                context["sofa_corner"] = context.get("sofa_corner", 0) + n
        else:
            for k, v in context_types(build, items).items():
                context[k] = context.get(k, 0) + v
        typed = context_typed(build, before)
        if typed:
            typed_by.update(typed)
            withdrawn.update(withdraw_questions(build, works, items, list(typed), typed))
            pending.difference_update(typed)
            held.difference_update(typed)

    # Fix round after P5 (module docstring): the drawn L corner sofas first, so the code typing sees the room's
    # seating anchor (P5: the 1.30 m outline f_L-1_061 in the L's open corner became "the missing sofa").
    context_pass(corner_only=True)
    code_pass()
    context_pass()
    fronts = infer_fronts(build, held)
    context_pass()                                   # the seats have their fronts now (coffee table, TV unit)
    if code_pass():                                  # chains: a missing member of a group the context rules typed
        fronts += infer_fronts(build, held)
        context_pass()
    if copied:
        context["copies"] = copied
    twice = duplicates(build)
    if twice:
        context["drawn_twice"] = twice
    inferred, coded2 = infer(build, pending)
    # Milestone 13 (K3): a code-typed piece waits for no AI answer: its question is withdrawn, it gets its front
    # and its partners like every typed piece below (``infer_types`` runs the code methods first, on the same
    # building in every mode; normally nothing is left for them after the passes above).
    by_id = {f["id"]: f for f in b["furniture"]}
    methods2 = {pid: str((by_id.get(pid) or {}).get("type_method") or "code") for pid in coded2}
    typed_by.update(methods2)
    withdrawn.update(withdraw_questions(build, works, items, coded2, methods2))
    pending = pending - set(coded2)
    to_twin: set[str] = set()
    tied = tie_break(build, items, pending, to_twin)  # fix round after P4b: two passes that disagree
    if tied or to_twin:
        # Pass before P5 (module docstring): the code typing once more, so a twin of a decided piece gets its type
        # (the twin rule) before the fronts and the review list. No reset: the AI's and the tie-break's types count.
        # A question asked and answered in this round stays listed (``withdraw_questions``); one that was not (a late
        # one) is withdrawn, as ``pipeline._infer_types`` withdrew it right after this step before.
        coded3, methods3 = code_first(build)
        if coded3:
            typed_by.update(methods3)
            withdrawn.update(withdraw_questions(build, works, items, coded3, methods3))
            pending = pending - set(coded3)
    # 26 Oct 2026 (module docstring): a kitchen run drawn as one outline with its sink or hob becomes its legs
    outline_legs = kitchen_outlines(build, items, pending)
    # Fix round after P5 (module docstring): clear reading errors of typed pieces, before the fronts and the fit
    flipped = long_side_fronts(build, items)
    desks = desk_chairs(build, items)
    cushions = seat_cushions(build, items)
    fixed = fix_fixed(build, items)
    fronts += infer_fronts(build, pending)
    # Partners of the anchors the inference typed (real01 --no-ai: the chaise by its size): the Milestone 12 rules on
    # what does not wait for answers, and no question is withdrawn here: with --no-ai the size inference types
    # pieces a plain run leaves to the AI, so a withdrawal here would make the question count depend on the mode.
    for k, v in context_types(build, items, pending).items():
        context[k] = context.get(k, 0) + v
    fronts += infer_fronts(build, pending)
    # 29 Oct 2026 (lessons UL92, UL95, UL96): backs on their walls, fronts that open, basins under a solid wall
    use_fixes = fixture_use_fixes(build, items)
    vanities = wet_room_vanities(build)          # 26 Oct 2026: never a kitchen counter in a bathroom
    zones = kitchen_zones(build)
    review = never_a_box(build, items, pending)
    _refresh_rooms(b)
    b.setdefault("symbols", [])
    b.setdefault("needs_review", [])
    build.reading = {"symbols": symbols, "context": context, "inferred": inferred, "fixed": fixed,
                     "fronts": fronts, "zones": zones, "needs_review": review, "tie_break": sorted(tied),
                     "answer_typed": sorted(from_answers), "long_side_fronts": flipped, "desk_chairs": desks,
                     "seat_cushions": cushions, "rooms_retyped": rooms_retyped, "nested_outlines": nested,
                     "kitchen_outline_legs": outline_legs, "wet_room_vanities": vanities, "fixture_use": use_fixes,
                     "code_typed": sorted(typed_by), "questions_withdrawn": sorted(withdrawn),
                     "typed_by": dict(sorted(typed_by.items())),
                     "furniture_texts": [t["id"] for t in b.get("furniture_texts") or []],
                     "zone_labels": [z["id"] for z in b.get("zone_labels") or []]}
