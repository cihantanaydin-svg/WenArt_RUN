"""Type inference for drawn pieces the documents leave unclear (docs/milestone11.md §6, CLAUDE.md furniture rules,
contract §17.2): an unknown footprint that holds other pieces is a rug or a group outline; one that matches a
type's size table, room and position rule gets that type, marked ``inferred``. Pure; owner: track B.

What: ``infer_types(building) -> [proposal]`` looks at every built drawn piece of type ``unknown``;
``apply_inferences(building, proposals) -> building`` returns a copy with them applied. A proposal is
``{"piece_id", "type", "reason", "confidence", "evidence": {...}, "front_deg"?: float, "build"?: false}``.

Why: CLAUDE.md (9 Oct 2026): "Footprint clear but type unclear -> the AI infers the type from size, room and
neighbours, marks it inferred and lists it in the report. It never stays an unexplained box." real02 had 56 built
unknown boxes (U17): rug and zone outlines read as one 13 m² piece (U9), pieces the two AI passes disagreed on.

How (deterministic; the agent may confirm or change the type later on the plan crop):

1. **Outline**: an unknown footprint whose polygon holds the centre of at least one other piece of its room is a rug
   or zone outline drawn around a group. The furniture schema has no rug type, so it is not built (``build:
   false``, proposal type ``rug``); the decor rules lay rugs under the groups (``decor.rugs_for_room``).
1b. **Detail**: an unknown footprint drawn >= 60 % inside a larger typed piece (a sink bowl in a counter leg) is a
   detail of that piece: not built (proposal type ``detail``).
2. **One type**: the types the footprint can be are those whose product size range fits it (size table, +15 %,
   either way), that the room type allows (``schemas.allowed_types``, plus stand-alone lamps, plants and side
   tables) and whose position rule holds (``schemas.ORIENTATION_RULES``: a back-to-wall type has a side on a wall;
   a free piece has a side on a wall or a group partner near). Exactly one -> that type (confidence 0.6).
1c. **Mark** (real03): an unknown footprint that fits no type and is smaller than ``MARK_SIDE_M`` both ways or
   thinner than ``MARK_THIN_M`` is a drawn mark (a tap, a valve, a threshold line): not built (type ``detail``).
3. **One named**: several fit, but exactly one of them was named by an AI pass (``type_candidates``) -> that type
   (confidence 0.55).
4. The front of an inferred type with a front: the side opposite the only side on a wall; a seat faces its nearest
   partner; else none (the builder's side, listed as assumed).

Nothing else is guessed: an unknown piece with no single answer stays unknown and is listed.

Milestone 13 (docs/milestone13.md §1.4, §3.0 K3, §5.2, §13.2; track T3; CLAUDE.md "an untyped drawn footprint is
typed by code first"): **code-first typing**, ``type_by_code(building, piece) -> {"type", "method": twin | level |
block | group_member, "evidence", "confidence"} | None``, runs before any AI typing (step 0 of ``infer_types``, so
the ingest's inference step and the completion get it; ``code_types`` applies it in rounds so a twin of a piece typed
by another level is typed too):

0a. **twin**: the same footprint (sizes within ``SAME_FOOTPRINT_M``, the mirrored centre within ``SAME_CENTRE_M``) in
    the room's twin (``rooms[].twin_of`` / ``twin_transform``, the ingest's mirror; a mirror about the rooms'
    midline when no transform is recorded) carries a type: that type, the mirrored front (``ingest.twins``).
0b. **level**: a typed drawn piece on another level whose footprint lies at the same plan position (polygons within
    ``SAME_FOOTPRINT_M``, mirrored or turned allowed): real04's bathtub f_L-1_056 types the ARC cluster f_L0_043 one
    level up; the front is copied.
0c. **block**: a word of the piece's block name (``evidence[].block``, ``type_raw``; ``groups.yaml`` ``block_words``,
    folded to ASCII: YATAK, masa, klozet, evye ...) names exactly one type whose product range fits the footprint
    (``sizes.fits``, ``BLOCK_SIZE_TOL``) and that the room may hold.
0d. **group_member**: the room's drawn groups miss a member (``groups.group_members``: "shower|bathtub" of a bath
    set, the nightstands of a bed, the chairs of a table, the fridge of a run) or the room kind misses its anchor
    (``program.room_kind``: a bedroom without a bed) and exactly one of those types fits the footprint (the nearest
    product when two alternatives of one role fit): that type.

Every proposal carries ``type_method`` (the method), ``inferred: true`` with the evidence (the source piece or
block, the rule, the confidence: twin / level ``CONF_TWIN``, block ``CONF_BLOCK``, group member ``CONF_GROUP``). The
AI types the rest (the existing path). ``apply_code_types(building, proposal=False)`` applies the proposals and
returns the new building with them; ``proposal=True`` (the completion path, after the locked source was written)
records a ``type_proposal`` with ``drawn_type`` and keeps the footprint and status, as ``locked.check`` requires.

Fix round after P4a (17 Oct 2026; pod P4a, real02). What: a **group member** type (rule 0d) is given only when the
group that misses it really takes the piece in: the piece typed on a copy of the building must lower that type's
count in the room's missing lists (``groups.group_members`` and the unbuilt drawn groups), i.e. it stands within
the role's reach of that group's anchor and no other anchor is nearer (``_adopted``); else code leaves it to the AI
(the plan crop). The room kind's missing anchor ("the bedroom misses its bed") is kept as it was. Why: the rule
ignored where the footprint stands, so every small square of a room was "the only missing member" of the same
group: P4a typed 7 coffee tables in each basement salon (the group named in the reason, seating.2 of the 1.30 m
"sofa" f_L-1_061, never took any of them: they joined the corner sofa's group or none, so the coffee table stayed
missing for every later footprint), 2-3 in each L1 play room. The check is made from the building on every call,
so it holds across the reading's code passes, ``infer_types`` and the completion; two nightstands of one bed or the
chairs of one table are still typed one by one (each lowers the count).

- **Nightstand symbols** (``nightstand_symbols``, run first in ``infer_types``): a drawn ``floor_lamp`` or
  ``side_table`` of a nightstand's size (``plausibility.size_range("nightstand")``) standing at a drawn bed's head
  end, beside the bed (from inside a bed block that holds it up to ``groups.yaml`` ``nightstand_gap`` outside the
  bed's long side), with no nightstand on that side yet, is that bed's nightstand: type ``nightstand``, the bed's
  front, ``inferred`` with the reason and ``adjusted_by_ai`` (``by: code``, ``drawn_type`` and the drawn footprint and
  front kept, the plan crop of the reading's question as evidence when the piece has one). Why: real02's YATAK blocks
  draw a nightstand with a table lamp on each side of the bed; both VLMs read the round lamp and answered
  ``floor_lamp``, the lamps then held the nightstand places and r_L0_e_yatak_odasi and _2 got no nightstand.

Fix round after P4b (17 Oct 2026; pod P4b, real03). What: ``chaise_sides(building)`` proposes the chaise side of a
built drawn ``sofa_corner`` that carries no L from the drawing (no ``shape`` and no ``chaise_side``: typed by code,
not by the reading's L-outline rule) when a drawn coffee table of its room reaches into its footprint box: the side
whose chaise (``schemas.l_parts``, default seat depth and chaise width, in the piece's front frame) leaves the table
free while the other side's chaise covers it; nothing when both or neither do. ``apply_chaise_sides`` writes
``shape: L``, ``chaise_side``, ``chaise_depth`` and ``inferred`` with the evidence (rule ``CHAISE_RULE``, the table
ids); the completion runs it (``complete.complete_building``). Why: real03's f_L0_190 was typed by the group-member
rule and lost the drawn L; the fit took a right-chaise model and the chaise covered the drawn coffee table f_L0_191
(the agent could not fix it in 3 rounds). The pin: f_L0_190 left, f_L0_196 right (its table already sits in the open
corner of a right chaise). The drawing's own L (the ingest's ``l_outline``) always wins; this is the fallback when
the documents are silent.

Fix round after P5 (22 Oct 2026; pod P5, real04; user decisions of 22 Oct 2026). What:

- **The group-member rule waits for an untyped L outline** (``_l_outline_waits``): while an untyped drawn piece of the
  room carries the reader's L-outline note on its vector evidence (``L_OUTLINE_NOTE``; the reading's context rule
  will make it the corner sofa), the room does not "miss its seating anchor". The reading now types the drawn L
  corner sofas before the first code typing (``reading.corner_sofa_pass``), so this guard is for the other callers.
- **A seating partner only at its role's place** (``ROLE_PLACES``): the group-member rule gives ``table_coffee`` only to
  a footprint in front of a seating anchor (gap from the front edge to its near side within ``COFFEE_ZONE_GAP_M``,
  centre in the anchor's front-width band; for a corner sofa also its open corner, at most ``COFFEE_IN_BODY`` of it
  inside the drawn L; an anchor without a front is tried on both long sides) and ``tv_unit`` only to one on a wall,
  outside every sofa's box, at least ``TV_MIN_M`` in front of an anchor within ``TV_FACING_DEG``
  (``coffee_zone_anchor``, ``tv_place_anchor``). A footprint that fits such a role by size but stands elsewhere is
  left to the plan crop (AI), unless another role it fits stands where it should. Why: P5 typed the 1.30 x 0.63 m outline f_L-1_061 in the open
  corner of the corner sofa f_L-1_053 as "the living room's missing sofa" (the L was still an untyped box), then the
  0.59 m lamp symbols f_L-1_063/065 by the window as that phantom's coffee tables; real02 the same. On the run
  buildings in the reading's first-pass state: f_L-1_061/062 are no sofas and f_L-1_063/065 no coffee tables on
  real02 and real04, f_L1_033/035 (behind the oyun sofas) are no TV units (the AI passes said bench / sideboard);
  real03's f_L0_191/197 (the tables of the code-typed corner sofas) and real01's 9 group-member typings are unchanged.
- **Corner tables** (``corner_tables``, run in ``infer_types``; user decision (1) of 22 Oct 2026, CLAUDE.md "code may
  retype a drawn piece the vision models typed when its size, room and neighbours clearly say otherwise"): a drawn
  sofa / armchair / ottoman / chaise typed by the AI passes or the group-member rule (never by a block name or a
  reading rule) of a coffee table's size, standing in the open corner of a drawn L corner sofa of its room, is that
  sofa's coffee table: ``type_method: inferred``, ``adjusted_by_ai`` (``by: code``, ``rule: corner_table``, the reason,
  the changed type) with ``drawn_type`` and the plan crop of its question (``_apply_nightstand``). Run buildings:
  real04 f_L-1_061/062, real02 f_L-1_062.
- The nightstand symbols of the fix round after P4a are approved by the same user decision; their label already holds
  ``by: code``, ``drawn_type`` and the plan crop.

Fix round after P5 (22 Oct 2026), review:

- **An agreed ottoman stays an ottoman** (``CORNER_OTTOMAN_FROM``): ``corner_tables`` retypes a drawn ottoman only when
  the AI passes did not agree on it (the group-member rule or the tie-break / size inference typed it). An ottoman in
  a corner sofa's open corner is a normal design (``plausibility.EXTRA_EXEMPT`` allows it in front of a
  ``sofa_corner``), so the size, room and neighbours do not clearly say otherwise; every P5 case was a 'sofa'.
- **A second code correction keeps the first one's record** (``merge_code_label``, used by ``_apply_nightstand`` and
  ``generic.reading._code_label``): an earlier code record is merged, not replaced: the reasons joined, the earliest
  value of every changed field kept, ``rules`` listing every rule (``rule`` = the latest, as ``fit`` labels do), the
  first plan crop kept. An agent's (or the solver's) record stays under ``previous`` as ``edit_ops._label`` keeps it.
  Why: a desk whose short-side AI front ``long_side_fronts`` turned lost that record when ``desk_chairs`` split it, and
  a nightstand retype after a front correction recorded the corrected front as the drawn one.

Fix round after P6a (22-23 Oct 2026; pod P6a, real04; the decor track's ask on the look lens' minor "two drawn floor
lamps overlap"). What: **duplicate symbols** (``duplicate_symbols``, run in ``infer_types``): two built drawn pieces
of one free-standing type that never shares its floor (``DUPLICATE_SYMBOL_TYPES``: a floor lamp) in
one room whose footprints overlap by at least ``DUPLICATE_SYMBOL_SHARE`` of the smaller one are one piece drawn
twice: the larger stays (the first id on a tie), the other is not built (``build: false``, ``inferred_as: detail``,
``not_built_reason``) and labelled ``adjusted_by_ai`` by code (``rule`` ``DUPLICATE_SYMBOL_RULE``, ``not_furniture:
duplicate_symbol``, ``duplicate_of``, ``drawn_*`` kept, the plan crop of its own question as evidence). Seats (two
chairs at a table's corner overlap by design: real03's 8 %, real04's 18 %), tables, runs and every other type keep
the old rule. Why: real04's basement salons hold two pairs of overlapping lamp symbols each (f_L-1_059 / 060 and
f_L-1_063 / 064, mirrored f_L-1_057 / 058 and f_L-1_065 / 066: 17-33 % of the smaller inside the other, two lamp
blocks of different sizes typed floor_lamp by both AI passes); every render showed two lamps standing in each other
(four lamps in each salon). The reading types them, so the rule runs where the inference runs (``reading.infer`` and
``pipeline._infer_types``) and never on an AI piece.

Fix round after P6a (23 Oct 2026), review: the rule holds the floor lamp only (the measured case; potted plants
are drawn as overlapping corner groups: 0.60 / 0.45 / 0.40 m canopies 0.45 m apart are three plants, not one), and
a piece without the plan crop of its own question (``_crop_of``: a block-named symbol had none) is never left out.
Real04's four duplicate lamps (P6a) and real02's two keep their crops and their verdict.

Reading fixes of 26 Oct 2026 (user: "fix should be general, it is not a fix for real06, it must be a fix for the
project"; real06 is the test case, tests/test_reading_sense_20261026.py). What:

- **One block, one type** (``_same_block_type``, code method ``same_block`` after ``level``, in ``CODE_TYPE_METHODS``
  and the schema): an untyped drawn piece with the same footprint (``SAME_FOOTPRINT_M``) and the same block
  (``block_signature`` / ``same_block``: the block names, or the same stroke kinds with counts within
  ``SAME_BLOCK_COUNT_TOL``, and the same shape) as typed drawn pieces anywhere in the project, all of one type, gets
  that type (the twin / other-level rules extended to every room and level). Why: real06 draws one armchair block
  in the salon (typed armchair) and again in the master bedroom upstairs (f_L1_020: "the bedroom's missing wardrobe").
  real01: the second sofa (the reference's F15, "the same block as F14") and the second bed's nightstands.
- **A wall type typed by code needs its back on a wall** (``placeable``, ``back_wall_side``, ``side_on_wall``; used by
  the group-member rule, the size inference and the reading's tie-break): a type whose back stands on a wall
  (``needs_wall``: wardrobe, bookcase, dresser, sideboard, TV unit, kitchen run, bed ...) needs a side of the drawn
  footprint with ``WALL_BACK_SHARE`` of it within ``WALL_BACK_M`` of the room outline and parallel to it within
  ``WALL_BACK_DEG``; else the next type. A round piece is never a chair (``ROUND_NEVER``). Why: real06's f_L1_020
  (0.92 x 0.77 m at 60.5 deg) became a wardrobe standing diagonal in the room.
- **A round table ringed by seats** (``ringed_tables``, in ``infer_types``; CLAUDE.md "code may retype a drawn piece
  the vision models typed when its size, room and neighbours clearly say otherwise"): a drawn round lamp, side table,
  chair, ottoman or plant of a coffee table's size with at least ``RING_SEATS_MIN`` seats of its room around it
  (within ``RING_REACH_M``, facing it when they have a front, no gap of ``RING_OPEN_DEG`` between their bearings) is
  their coffee table: ``adjusted_by_ai`` by code with ``drawn_type`` and the plan crop. Why: real06's f_L0_028 (0.66 m,
  "floor lamp" by both passes) stands in the middle of four armchairs.

Furniture name texts of 26 Oct 2026 (the auditor Argus, source ledger check A6; ``wenart.furniture.names``; user:
"fix should be general"; real06 is the test case, tests/test_name_texts_20261026.py). What:

- **A name text types the footprint it names** (code method ``name_text``, after ``block`` in ``CODE_TYPE_METHODS``;
  ``_name_text``): an untyped drawn footprint with a furniture name text of the plan (``building["furniture_texts"]``,
  recorded by the reading) on it or within ``names.NAME_NEAR_M``, when the text names this piece (of the drawn pieces
  whose size fits the named type, it is the nearest: ``names.named_piece``), the type fits the size
  (``names.NAME_SIZE_TOL``, the block name's tolerance), the room may hold it and a wall type has a side on a wall
  (``_name_choice``); the nearer text wins. The evidence names the text (entity id, value, position). A text that is
  not used says why (``name_text_note``: the reading puts it in the piece's review entry).
- **A name text corrects an AI type** (``name_text_retypes``, in ``infer_types`` before the other retype rules;
  proposal method ``NAME_RETYPE_METHOD``, the piece's ``type_method`` becomes ``name_text``): a drawn piece typed by the
  AI passes or a weak code guess (``names.RETYPE_FROM``) with a name text of another type written on it (within
  ``names.NAME_RETYPE_M``) takes the named type when it fits the size and the room: ``adjusted_by_ai`` by code with
  ``drawn_type`` and the plan crop (``_apply_nightstand``). A block-named piece or one a reading rule typed is never
  changed.

- **A zone label types the anchor of its zone** (code method ``zone_label``, after ``name_text``; ``_zone_label_type``):
  a second label of a room naming a zone of another kind (``building["zone_labels"]``, ``names.zone_records``:
  "YEMEK BÖLÜMÜ" in a salon, Essbereich, salle à manger, zona pranzo, comedor) gives the zone's anchor (the dining
  table) to the untyped drawn footprint of its zone nearest the label whose size fits it (``names.fits_with_partners``:
  a table drawn with its chairs counts, ``names.partner_margin``), when the zone has no anchor yet and the room holds
  it. The group-member rule never gives the room kind's anchor to a footprint in a zone of another kind.
- **The member the room misses, named by the AI passes** (``ai_named_members``, in ``infer_types`` before the size
  inference; proposal method ``AI_MEMBER_METHOD``, ``type_method: inferred``): an untyped drawn footprint whose room
  misses a member of its groups (``_group_wants``: a bathroom set's "shower|bathtub") and whose passes named that
  member as their answer or in their reason (``names.mentioned_types``: "likely a bathtub or shower") gets it; a type
  the room may not hold (a bunk bed in a bathroom) is ignored and said; a drawn size outside the type's ranges takes
  the nearest real product inside the drawn footprint (``product_inside``; ``adjusted_by_ai`` by code, ``drawn_*``
  kept, the plan crop), the reading's ``fix_fixed`` then checks it like any fixed piece.
- **A wardrobe run the room's program needs** (``_wardrobe_run_type``, method ``group_member`` after the group-member
  rule): in a dressing room (``program.room_kind`` ``dressing`` / ``program.dressing_room``: wardrobe runs along its
  walls) every untyped drawn footprint with its long side on a wall, a wardrobe run's length (the size table, +15 %)
  and a depth in ``WARDROBE_DEPTH_M`` is a wardrobe; in a room whose required group has a wardrobe anchor and none is
  built (a bedroom's storage) only its one such footprint. A depth outside the wardrobe's range is snapped to the
  product depth with the back kept on its wall (``snapped``: ``drawn_*`` kept, ``adjusted_by_ai`` by code, rule
  ``WARDROBE_RULE``); an AI answer of another type the room holds that fits the size leaves it to the plan crop (a
  "stair" answer never counts: stairs come from the drawing). real06's dressing room f_L1_014 / f_L1_015 (2.27 x 0.85
  m, the passes: unknown / stair) were unbuilt and the completion would have added new runs beside them.

Why: real06 L1 writes "*SIFONIYER" on f_L1_007 (two passes: dresser / desk; the tie-break took desk) and on f_L1_019,
and "çamaşır mak." on the empty square f_L1_021 (two passes: washbasin); none of them was read. Rule 2 of ``names``
(a name text with no drawn piece adds the piece) runs in the pipeline after the last typing. real06's salon holds the
label "YEMEK BÖLÜMÜ" on its round dining table f_L0_011 (1.69 m with four chairs inside the outline), which the
group-member rule made "the living room's corner sofa"; its bathrooms' corner baths f_L0_010 / f_L1_011 (2.42 x 0.98
m, pass 1 "likely a bathtub or shower", pass 2 "bunk_bed") stayed untyped and the bathrooms had no bath.
"""
from __future__ import annotations

import copy
import dataclasses
import math
import re
from typing import Optional

from shapely.geometry import Point

from wenart import geometry as G
from wenart.furniture import groups as GR
from wenart.furniture import placer, plausibility as PL, schemas

# Milestone 13 (T3): code-first typing. 26 Oct 2026: same_block (one block drawn again elsewhere in the project) and
# name_text (a furniture name written as a text of the plan, ``wenart.furniture.names``).
NAME_TEXT_METHOD = "name_text"
NAME_RETYPE_METHOD = "name_text_retype"   # the proposal's method of rule 1b; the piece's type_method becomes name_text
ZONE_LABEL_METHOD = "zone_label"          # 26 Oct 2026: a zone label of the room ("YEMEK BÖLÜMÜ") names its anchor
AI_MEMBER_METHOD = "ai_member"            # 26 Oct 2026: ai_named_members' proposal method (type_method inferred)
AI_MEMBER_RULE = "furniture.infer.ai_named_members"
INFER_METHOD_VALUE = "inferred"           # the schema's type_method of a piece typed by inference
# 26 Oct 2026 (wardrobe runs, method group_member): a drawn wardrobe run is this deep (its doors drawn in front, a
# block drawn deeper than the product); a depth outside the wardrobe's range is snapped to the product depth.
WARDROBE_DEPTH_M = (0.55, 0.90)
WARDROBE_ROOM = "dressing"                # the room kind whose program is wardrobe runs (program.room_kind)
WARDROBE_RULE = "wardrobe_run"
CODE_TYPE_METHODS = ("twin", "level", "same_block", "block", NAME_TEXT_METHOD, ZONE_LABEL_METHOD, "group_member")
SAME_FOOTPRINT_M = 0.01          # the same footprint: sizes (and, on another level, the polygon) within 1 cm
SAME_CENTRE_M = 0.02             # a twin's mirrored centre within this (ingest.twins.TOL: the transform is rounded)
CONF_TWIN = 0.8
CONF_BLOCK = 0.7
CONF_GROUP = 0.6
BLOCK_SIZE_TOL = 0.40            # a block-named type must fit the footprint within this (a misread YATAK block is 27 % out)
CODE_ROUNDS = 3                  # chains: a twin of a piece typed by another level

# Fix round after P4a (module docstring): a drawn lamp or side table of a nightstand's size at a bed's head is the
# bed's nightstand (a nightstand with its table lamp drawn from above).
NIGHTSTAND_METHOD = "nightstand_symbol"
NIGHTSTAND_SYMBOL_TYPES = ("floor_lamp", "side_table")
CONF_NIGHTSTAND = 0.7
NIGHTSTAND_SIDE_IN_M = 0.05       # the symbol's outer side reaches at least this close to the bed's side line
RECOGNITION_CROP = "recognition/crops/{key}_ctx.png"     # the reading's plan crop of a question (reading.CROP_DIR)

# Fix round after P5 (module docstring): the group-member rule waits for an untyped L outline (the room's corner sofa
# to be) and gives a seating partner only at its role's place.
L_OUTLINE_NOTE = re.compile(r"\bL outline\b")      # symbols.l_shape's note on the piece's vector evidence
COFFEE_ZONE_GAP_M = (-0.05, 1.60)  # sofa front edge to the coffee table's near side (reading.COFFEE_FRONT_M, drawn)
COFFEE_IN_BODY = 0.2               # at most this share of a coffee table inside the corner sofa's L (reading's notch)
TV_MIN_M = 0.90                    # a TV unit stands at least this far in front of the sofa (reading.TV_DISTANCE_M)
TV_FACING_DEG = 45.0               # ... within this of the sofa's front direction
# Fix round after P5 (user decision of 22 Oct 2026): a seat drawn in a corner sofa's open corner is its coffee table.
CORNER_TABLE_METHOD = "corner_table"    # the proposal's method; the piece's type_method becomes "inferred"
CORNER_TABLE_RULE = "furniture.infer.corner_tables"
CORNER_TABLE_FROM = ("sofa", "armchair", "ottoman", "chaise")
CORNER_OTTOMAN_FROM = ("group_member", "inferred")   # review: an ottoman only when the passes did not agree on it
CORNER_IN_BOX = 0.4                # at least this share of the piece inside the corner sofa's box (reading's notch)
CONF_CORNER_TABLE = 0.7

# Fix round after P6a (module docstring): two overlapping drawn symbols of one free-standing type are one piece.
DUPLICATE_SYMBOL_METHOD = "duplicate_symbol"     # the proposal's method (the piece keeps its type_method)
DUPLICATE_SYMBOL_RULE = "furniture.infer.duplicate_symbols"
# fix round after P6a (23 Oct 2026), review: the floor lamp only, the one measured case (a corner group of drawn
# plants overlaps by design: 0.60 / 0.45 / 0.40 m canopies 0.45 m apart are three plants)
DUPLICATE_SYMBOL_TYPES = ("floor_lamp",)
DUPLICATE_SYMBOL_SHARE = 0.10      # at least this share of the smaller footprint lies in the larger one
CONF_DUPLICATE = 0.7

# 26 Oct 2026 (module docstring "Reading fixes of 26 Oct 2026"): a wall type typed by code needs its back on a wall;
# a round piece is never a chair; one block drawn again elsewhere gets one type; a round table ringed by seats.
WALL_BACK_M = 0.10                # a side this close to the room outline ...
WALL_BACK_DEG = 5.0               # ... parallel to the nearest outline segment within this ...
WALL_BACK_SHARE = 0.6             # ... along at least this share of its length can be a wall type's back
ROUND_NEVER = ("chair",)          # user, 26 Oct 2026: "round shapes are never chairs"
SAME_BLOCK_METHOD = "same_block"
SAME_BLOCK_MIN_STROKES = 4        # a stroke pattern of fewer strokes says nothing (a plain box)
SAME_BLOCK_COUNT_TOL = 0.02       # the strokes of each kind agree within this share (real06's two copies of its
                                  # 0.92 x 0.77 m armchair block hold 301 and 306 lines: a few loose strokes joined)
RING_TABLE_METHOD = "ringed_table"
RING_TABLE_RULE = "furniture.infer.ringed_tables"
RING_TABLE_FROM = ("floor_lamp", "side_table", "chair", "ottoman", "potted_plant")
RING_SEATS = ("armchair", "sofa", "sofa_corner", "chaise", "chair", "ottoman", "bench")
RING_SEATS_MIN = 3                # at least this many seats stand around the round piece ...
RING_REACH_M = 0.8                # ... each within this of it ...
RING_FACING_DEG = 60.0            # ... facing it within this when it has a front ...
RING_OPEN_DEG = 180.0             # ... and no gap between their bearings as wide as this (it is surrounded)
CONF_RING = 0.7

OUTLINE_TYPE = "rug"              # what an outline holding other pieces is (a decor type, not a furniture type)
WALL_SIDE_M = 0.10                # a side this close to the room outline stands on a wall
CONF_ONE = 0.6
CONF_NAMED = 0.55
CONF_OUTLINE = 0.7
SKIP_TYPES = ("stair", "unknown", "wall_cabinet")


OUTLINE_MIN_M2 = 1.0              # an outline (rug, zone) is at least this large ...
HELD_INSIDE = 0.5                 # ... and holds >= half of each smaller piece it is drawn around


def outline_holds(poly, mates: list[dict]) -> list[str]:
    """Ids of the pieces an outline ``poly`` is drawn around: smaller pieces whose centre lies in it with at least
    ``HELD_INSIDE`` of their area (none when the outline is smaller than ``OUTLINE_MIN_M2``). 27 Oct 2026: a small
    mark (``small_mark``: a cushion or pillow symbol) is a detail of the outline, never a piece it is drawn around
    (real06's salon: two drawn sofas holding their cushion marks were "rug outlines")."""
    if poly.area < OUTLINE_MIN_M2:
        return []
    out = []
    for f in mates:
        if small_mark(f):
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area >= poly.area or not poly.contains(Point(f["footprint"]["center"])):
            continue
        if other.intersection(poly).area >= HELD_INSIDE * other.area:
            out.append(f["id"])
    return sorted(out)


DETAIL_TYPE = "detail"            # a drawn part inside a typed piece (not a furniture type: not built)
# real03 (10 Oct 2026): a symbol smaller than this both ways (a tap, a valve) or thinner than MARK_THIN_M (a
# threshold, a shelf line) that fits no type is a drawn mark, not a piece: not built (rule 1c).
MARK_SIDE_M = 0.30
MARK_THIN_M = 0.20
DETAIL_INSIDE = 0.6


def _host_of(poly, mates: list[dict]) -> Optional[dict]:
    """The built, typed (larger) piece that holds >= ``DETAIL_INSIDE`` of ``poly`` (real02: the sink bowls inside
    the counter legs, typed bar stools by one AI pass), else None."""
    for f in mates:
        if f.get("type") in ("unknown", "stair") or f.get("build") is False:
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area > poly.area and poly.intersection(other).area >= DETAIL_INSIDE * poly.area:
            return f
    return None


def small_mark(piece: dict) -> bool:
    """A drawn piece smaller than ``MARK_SIDE_M`` both ways (a cushion or pillow symbol, a tap, a plant mark): never a
    piece an outline is drawn around (27 Oct 2026, module docstring)."""
    try:
        return max(float(v) for v in piece["footprint"]["size"][:2]) < MARK_SIDE_M
    except (KeyError, TypeError, ValueError):
        return False


CUSHION_HOST_FACTOR = 4.0         # a drawn outline at least this many times a small mark's area holds it as a detail


def drawn_host_of(item: dict, poly, mates: list[dict]) -> Optional[dict]:
    """27 Oct 2026 (pod run 224516, real06's salon: the cushion marks of two drawn sofas were typed potted plants and
    made the sofas "rug outlines"): the drawn piece (typed or not, built or not, not a rug) that holds at least
    ``DETAIL_INSIDE`` of the small mark ``item`` (``small_mark``) and is ``CUSHION_HOST_FACTOR`` times its area or more:
    the mark is a detail drawn on it (a cushion, a pillow), not a piece; else None."""
    if not small_mark(item):
        return None
    for f in mates:
        if f.get("source") != "from_documents" or f.get("type") in ("stair", OUTLINE_TYPE) or small_mark(f):
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area >= CUSHION_HOST_FACTOR * poly.area and poly.intersection(other).area >= DETAIL_INSIDE * poly.area:
            return f
    return None


def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3}


def _sides(poly) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    c = list(poly.exterior.coords)
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


def _wall_sides(piece: placer.Piece, ring) -> list[int]:
    """Indices of the footprint's sides (local order: front, right, back, left) within ``WALL_SIDE_M`` of the room
    outline along most of their length."""
    out = []
    for k, (a, b) in enumerate(_sides(piece.polygon())):
        pts = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for t in (0.2, 0.5, 0.8)]
        if all(ring.distance(Point(p)) <= WALL_SIDE_M for p in pts):
            out.append(k)
    return out


def _outward_deg(piece: placer.Piece, side: tuple) -> float:
    mid = ((side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0)
    return math.degrees(math.atan2(mid[1] - piece.center[1], mid[0] - piece.center[0]))


def _snap_quarter(deg: float, rotation: float) -> float:
    """``deg`` snapped to the nearest of the footprint's four side normals."""
    base = G.front_direction_deg(rotation)
    k = round(G.normalise_angle(deg - base) / 90.0) % 4
    return round(G.normalise_angle(base + 90.0 * k), 3)


def _front_for(ftype: str, piece: placer.Piece, ring, partners: list[placer.Piece]) -> Optional[float]:
    if ftype in schemas.FRONTLESS_TYPES:
        return None
    rule = schemas.orientation_rule(ftype)
    if rule["back"] == "free" and partners:
        host = min(partners, key=lambda h: (round(h.polygon().distance(piece.polygon()), 6), h.index))
        target = host.polygon().centroid
        return _snap_quarter(math.degrees(math.atan2(target.y - piece.center[1], target.x - piece.center[0])),
                             piece.rotation_deg)
    sides = _sides(piece.polygon())
    near = _wall_sides(piece, ring)
    if len(near) == 1:
        return _snap_quarter(_outward_deg(piece, sides[near[0]]) + 180.0, piece.rotation_deg)
    return None


SQUARE_TYPES = ("potted_plant", "side_table", "floor_lamp", "bar_stool", "chair", "office_chair")
PARTNER_ONLY = ("chair", "bar_stool", "office_chair")   # a seat is placed by its table, never by a wall alone
SQUARE_ASPECT = 1.3               # these are about as wide as deep (a 1.03 x 0.69 m outline is no plant)


def _shape_ok(ftype: str, size) -> bool:
    a, b = sorted(float(v) for v in size)
    return ftype not in SQUARE_TYPES or b <= SQUARE_ASPECT * a + 1e-9


GROUP_SEATS = ("sofa", "sofa_corner", "armchair", "chaise")
GROUP_REACH_M = 2.0               # a seat this close to another seat or to what it faces stands in its group


def _position_ok(ftype: str, piece: placer.Piece, on_wall: bool, others: list[tuple[str, placer.Piece]]) -> bool:
    rule = schemas.orientation_rule(ftype)
    if rule["back"] == "wall_or_group":
        # 27 Oct 2026 (real06's salon: a drawn 1.52 m sofa 0.107 m off the wall beside its armchairs stayed untyped):
        # on a wall, or in its group (``schemas``: free when it faces its group): a seat or what it faces nearby
        if on_wall:
            return True
        poly = piece.polygon()
        mates = set(rule.get("front_to") or ()) | set(GROUP_SEATS)
        return any(t in mates and o.polygon().distance(poly) <= GROUP_REACH_M for t, o in others)
    if rule["back"] == "wall":
        return on_wall
    if rule["back"] == "free" and rule["partners"]:
        poly = piece.polygon()
        near = any(t in rule["partners"] and o.polygon().distance(poly) <= rule["partner_m"] for t, o in others)
        return near if ftype in PARTNER_ONLY else (on_wall or near)
    return True


def _evidence(item: dict, reason: str, confidence: float) -> dict:
    src = (item.get("evidence") or [{}])[0]
    ev = {"file": src.get("file") or "building.json", "method": "inferred", "confidence": confidence,
          "rule": "furniture.infer", "text": reason}
    for k in ("page", "entity", "region_id"):
        if src.get(k) is not None:
            ev[k] = src[k]
    return ev


# --------------------------------------------------------------------------
# Milestone 13 (T3): code-first typing (twin, level, block name, missing group member)
# --------------------------------------------------------------------------

def untyped_drawn(piece: dict) -> bool:
    """A drawn footprint code may type: ``unknown``, not recorded as something else (a rug outline, a detail, a
    column, not furniture) and either built or left unbuilt only because it is untyped."""
    if piece.get("type") != "unknown" or piece.get("source") != "from_documents" or not piece.get("footprint"):
        return False
    if piece.get("inferred_as") or piece.get("not_furniture"):
        return False
    if piece.get("build") is False and not str(piece.get("not_built_reason") or "").lower().startswith("untyped"):
        return False
    return True


def _typed_drawn(piece: dict) -> bool:
    """A drawn piece whose type code may copy: typed, with a footprint, not a mark and not marked not furniture."""
    return (piece.get("source") == "from_documents" and piece.get("type") not in (None, "unknown", "stair")
            and bool(piece.get("footprint")) and not piece.get("inferred_as") and not piece.get("not_furniture")
            and piece.get("build") is not False)


def _sorted_size(piece: dict) -> tuple[float, float]:
    a, b = sorted(float(v) for v in piece["footprint"]["size"])
    return a, b


def _same_size(a: dict, b: dict, tol: float = SAME_FOOTPRINT_M) -> bool:
    return all(abs(u - v) <= tol + 1e-9 for u, v in zip(_sorted_size(a), _sorted_size(b)))


def _mirror_affine_of(a: dict, b: dict) -> list[float]:
    """A mirror between two twin rooms without a recorded transform: about the vertical or horizontal line between
    their centroids (``ingest.twins.mirror_affine``)."""
    from shapely.geometry import Polygon

    from wenart.ingest import twins as TW

    ca, cb = Polygon(a["polygon"]).centroid, Polygon(b["polygon"]).centroid
    if abs(cb.x - ca.x) >= abs(cb.y - ca.y):
        return TW.mirror_affine(("x", (ca.x + cb.x) / 2.0))
    return TW.mirror_affine(("y", (ca.y + cb.y) / 2.0))


def _twin_rooms(building: dict, room: dict) -> list[tuple[dict, list[float]]]:
    """``(twin room, transform)`` pairs of a room (a mirror is its own inverse, so one transform serves both ways)."""
    rooms = _rooms(building)
    out = []
    first = rooms.get(room.get("twin_of") or "")
    if first is not None:
        t = room.get("twin_transform") or first.get("twin_transform") or _mirror_affine_of(first, room)
        out.append((first, list(t)))
    for r in rooms.values():
        if r.get("twin_of") == room.get("id") and r["id"] != room["id"]:
            t = r.get("twin_transform") or room.get("twin_transform") or _mirror_affine_of(room, r)
            out.append((r, list(t)))
    return out


def _evidence_code(item: dict, method: str, text: str, confidence: float, **extra) -> dict:
    ev = _evidence(item, text, confidence)
    ev["rule"] = f"furniture.infer.type_by_code:{method}"
    ev.update(extra)
    return ev


def _twin_type(building: dict, piece: dict, room: dict) -> Optional[dict]:
    from wenart.ingest import twins as TW

    furniture = building.get("furniture") or []
    for other, t in _twin_rooms(building, room):
        mapped = TW._apply(t, piece["footprint"]["center"])
        for f in furniture:
            if f.get("room_id") != other["id"] or not _typed_drawn(f) or f["id"] == piece["id"]:
                continue
            if G.distance(mapped, tuple(f["footprint"]["center"])) > SAME_CENTRE_M + 1e-9 or not _same_size(piece, f):
                continue
            fp, front = TW._mirror_footprint(f, piece, t)
            text = (f"{f['type']}: the same footprint ({_sorted_size(f)[1]:.2f} x {_sorted_size(f)[0]:.2f} m) as "
                    f"{f['id']} in the twin room {other['id']} (mirrored centre within {SAME_CENTRE_M:.2f} m)")
            return {"type": f["type"], "method": "twin", "confidence": CONF_TWIN, "reason": text,
                    "evidence": _evidence_code(piece, "twin", text, CONF_TWIN, source_id=f["id"], room_id=other["id"]),
                    "front_deg": front, "footprint": fp, "source_status": f.get("status")}
    return None


def _level_type(building: dict, piece: dict, room: Optional[dict]) -> Optional[dict]:
    furniture = building.get("furniture") or []
    rooms = _rooms(building)
    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    hits = []
    for f in furniture:
        if f.get("level_id") == piece.get("level_id") or not _typed_drawn(f) or not _same_size(piece, f):
            continue
        if G.distance(tuple(piece["footprint"]["center"]), tuple(f["footprint"]["center"])) > SAME_CENTRE_M + 1e-9:
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if poly.hausdorff_distance(other) > SAME_FOOTPRINT_M + 1e-9:
            continue
        r2 = rooms.get(f.get("room_id") or "")
        same_kind = 0 if room is not None and r2 is not None and r2.get("room_type") == room.get("room_type") else 1
        hits.append((same_kind, f.get("level_id") or "", f["id"], f))
    if not hits:
        return None
    hits.sort(key=lambda h: h[:3])
    f = hits[0][3]
    text = (f"{f['type']}: the same footprint ({_sorted_size(f)[1]:.2f} x {_sorted_size(f)[0]:.2f} m) at the same "
            f"plan position as {f['id']} on level {f.get('level_id')} (within {SAME_FOOTPRINT_M:.2f} m)")
    out = {"type": f["type"], "method": "level", "confidence": CONF_TWIN, "reason": text,
           "evidence": _evidence_code(piece, "level", text, CONF_TWIN, source_id=f["id"], level_id=f.get("level_id")),
           "source_status": f.get("status")}
    if f.get("front_deg") is not None and piece.get("front_deg") is None:
        out["front_deg"] = float(f["front_deg"])
    return out


def entity_counts(entity) -> dict[str, int]:
    """26 Oct 2026: the stroke count per entity kind of an evidence ``entity`` (``symbols.id_ranges`` text:
    ``LINE:295C60,LINE:295C61,ARC:298801-298804`` -> ``{"LINE": 2, "ARC": 4}``; a numeric range counts its ids)."""
    counts: dict[str, int] = {}
    for part in str(entity or "").split(","):
        part = part.strip()
        if not part or part.startswith(("recognition:", "derived-from:")):
            continue
        head, _, tail = part.partition(":")
        lo, dash, hi = tail.partition("-")
        n = int(hi) - int(lo) + 1 if dash and lo.isdigit() and hi.isdigit() and int(hi) >= int(lo) else 1
        counts[head] = counts.get(head, 0) + n
    return counts


def block_signature(piece: dict) -> Optional[tuple]:
    """26 Oct 2026 (module docstring): what a drawn piece's block is: ``(block names, stroke counts per kind, shape)``
    from its drawing evidence (``vector`` / ``raster`` entities), or None when it names no block and holds fewer than
    ``SAME_BLOCK_MIN_STROKES`` strokes (a plain box says nothing)."""
    names = tuple(sorted(set(_block_names(piece))))
    counts: dict[str, int] = {}
    for ev in piece.get("evidence") or []:
        if isinstance(ev, dict) and ev.get("method") in ("vector", "raster") and ev.get("entity"):
            counts = entity_counts(ev["entity"])
            break
    if not names and sum(counts.values()) < SAME_BLOCK_MIN_STROKES:
        return None
    return names, tuple(sorted(counts.items())), piece.get("shape") or None


def same_block(a: Optional[tuple], b: Optional[tuple]) -> bool:
    """26 Oct 2026: two ``block_signature``s name one block: the same block names (when either names one), the same
    shape, the same stroke kinds, and per kind counts within ``SAME_BLOCK_COUNT_TOL`` (at least one stroke)."""
    if a is None or b is None or a[0] != b[0] or a[2] != b[2]:
        return False
    if a[0]:
        return True
    ca, cb = dict(a[1]), dict(b[1])
    if set(ca) != set(cb):
        return False
    return all(abs(ca[k] - cb[k]) <= max(1.0, SAME_BLOCK_COUNT_TOL * max(ca[k], cb[k])) + 1e-9 for k in ca)


def _same_block_type(building: dict, piece: dict) -> Optional[dict]:
    """26 Oct 2026 (module docstring, user: "identical blocks get one type"): the type of the typed drawn pieces
    anywhere in the project (every room and level) with the same footprint (sizes within ``SAME_FOOTPRINT_M``) and the
    same block (``same_block``: block names, or the same strokes per kind, and shape), when they all have one type;
    else None."""
    sig = block_signature(piece)
    if sig is None:
        return None
    hits = []
    for f in building.get("furniture") or []:
        if f.get("id") == piece.get("id") or not _typed_drawn(f) or not _same_size(piece, f):
            continue
        if same_block(block_signature(f), sig):
            hits.append(f)
    types = sorted({f["type"] for f in hits})
    if len(types) != 1:
        return None
    src = sorted(hits, key=lambda f: (str(f.get("level_id") or ""), str(f["id"])))[0]
    what = f"block {sig[0][0]!r}" if sig[0] else "the same strokes (" + ", ".join(f"{n} {k}" for k, n in sig[1]) + \
        f" here, within {SAME_BLOCK_COUNT_TOL:.0%})"
    text = (f"{types[0]}: the same drawn block ({what}) and footprint ({_sorted_size(src)[1]:.2f} x "
            f"{_sorted_size(src)[0]:.2f} m, within {SAME_FOOTPRINT_M:.2f} m) as {', '.join(f['id'] for f in hits[:4])}"
            f" (typed {types[0]}): one block, one type")
    return {"type": types[0], "method": SAME_BLOCK_METHOD, "confidence": CONF_TWIN, "reason": text,
            "evidence": _evidence_code(piece, SAME_BLOCK_METHOD, text, CONF_TWIN, source_id=src["id"],
                                       copies=[f["id"] for f in hits]),
            "source_status": src.get("status")}


def needs_wall(ftype: str) -> bool:
    """26 Oct 2026: a type whose back stands on a wall (``schemas.ORIENTATION_RULES`` back ``wall``, not a minor
    one): a wardrobe, bookcase, dresser, sideboard, TV unit, kitchen run, bed, toilet ..."""
    rule = schemas.orientation_rule(ftype)
    return rule["back"] == "wall" and rule.get("back_severity") != "minor"


def _ring_angle(ring, point) -> float:
    """The direction (deg) of the room outline's segment nearest to ``point``."""
    from shapely.geometry import LineString

    c = list(ring.coords)
    best = min(range(len(c) - 1), key=lambda i: LineString([c[i], c[i + 1]]).distance(Point(point)))
    (x0, y0), (x1, y1) = c[best], c[best + 1]
    return math.degrees(math.atan2(y1 - y0, x1 - x0))


def back_wall_side(piece: dict, room: dict) -> Optional[int]:
    """26 Oct 2026 (module docstring): the index of a side of the drawn footprint (``placer.drawn_piece``) that can be
    the back of a wall type (``side_on_wall``), or None when no side can be. Which side is the front stays the
    front rules' business (``_front_for``, the reading's ``_front_of``)."""
    if len(room.get("polygon") or []) < 3:
        return None
    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    ring = _room_ring(room)
    for k, (a, b) in enumerate(_sides(poly)):
        if math.dist(a, b) > 1e-6 and side_on_wall(a, b, ring):
            return k
    return None


def side_on_wall(a, b, ring) -> bool:
    """26 Oct 2026: the segment ``a``-``b`` stands on the room outline ``ring``: at least ``WALL_BACK_SHARE`` of it
    within ``WALL_BACK_M`` and parallel to the nearest outline segment within ``WALL_BACK_DEG``."""
    pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in (0.05, 0.25, 0.5, 0.75, 0.95)]
    if sum(ring.distance(Point(q)) <= WALL_BACK_M + 1e-9 for q in pts) < WALL_BACK_SHARE * len(pts) - 1e-9:
        return False
    diff = abs((math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) - _ring_angle(ring, pts[2]) + 90.0) % 180.0 - 90.0)
    return diff <= WALL_BACK_DEG + 1e-9


def placeable(ftype: str, piece: dict, room: Optional[dict]) -> Optional[str]:
    """26 Oct 2026 (module docstring): why code may not give ``piece`` the type ``ftype``, else None: a wall type
    (``needs_wall``) with no side that can be its back on a wall (``back_wall_side``), or a chair drawn round."""
    if ftype in ROUND_NEVER and (piece.get("shape") == "round"):
        return f"a round piece is never a {ftype}"
    if room is not None and needs_wall(ftype) and back_wall_side(piece, room) is None:
        rot = float((piece.get("footprint") or {}).get("rotation_deg") or 0.0)
        return (f"a {ftype} needs its back on a wall (within {WALL_BACK_DEG:g} deg and {WALL_BACK_M:.2f} m); the drawn "
                f"piece (at {rot:g} deg) has no side there")
    return None


def _block_names(piece: dict) -> list[str]:
    names = []
    for ev in piece.get("evidence") or []:
        for key in ("block", "block_name"):
            if ev.get(key):
                names.append(str(ev[key]))
    for key in ("type_raw", "block", "block_name"):
        if piece.get(key):
            names.append(str(piece[key]))
    return names


def _block_type(building: dict, piece: dict, room: Optional[dict]) -> Optional[dict]:
    from wenart import building as B
    from wenart.furniture import sizes as SZ

    names = _block_names(piece)
    if not names:
        return None
    words = []
    for name in names:
        words += [w for w in re.split(r"[^a-z0-9]+", B.fold_ascii(name)) if w]
    if not words:
        return None
    text = " " + " ".join(words) + " "
    hits = []
    for ftype, keys in GR.block_words().items():
        for key in keys:
            parts = key.split()
            if (len(parts) > 1 and f" {' '.join(parts)} " in text) or (len(parts) == 1 and any(
                    w.startswith(parts[0]) for w in words)):
                hits.append((ftype, key))
                break
    if not hits:
        return None
    size = [float(v) for v in piece["footprint"]["size"]]
    allowed = None
    if room is not None and not any(t in ("other", "unknown") for t in PL.room_types(building, room)):
        allowed = PL.allowed_in(building, room)
    fits = [(t, k) for t, k in hits if SZ.fits(t, size, BLOCK_SIZE_TOL) and (allowed is None or t in allowed)]
    if len(fits) != 1:
        return None
    ftype, key = fits[0]
    text = (f"{ftype}: the block name '{names[0]}' holds the word '{key}' (groups.yaml block_words) and the type's "
            f"product range fits {size[0]:.2f} x {size[1]:.2f} m within {BLOCK_SIZE_TOL:.0%}")
    return {"type": ftype, "method": "block", "confidence": CONF_BLOCK, "reason": text,
            "evidence": _evidence_code(piece, "block", text, CONF_BLOCK, block=names[0], word=key)}


def _name_choice(building: dict, piece: dict, room: Optional[dict], types, size, fit=None) -> tuple[Optional[str], str]:
    """26 Oct 2026 (``names`` rule 1 / 1b, zone labels): ``(type, "")`` of the types a name text names that fit the
    piece's size (``fit``, by default ``names.fits_size``: ``names.NAME_SIZE_TOL``), that its room may hold and whose
    position rule holds (``placeable``), the nearest product of two when one is clearly nearer; else ``(None, why
    not)``."""
    from wenart.furniture import names as NM

    fit = fit or NM.fits_size
    fits = [t for t in types if fit(t, piece)]
    if not fits:
        return None, f"its product range does not fit {size[0]:.2f} x {size[1]:.2f} m"
    if room is not None and not any(t in ("other", "unknown") for t in PL.room_types(building, room)):
        allowed = PL.allowed_in(building, room)
        ok = [t for t in fits if t in allowed]
        if not ok:
            return None, f"a {' + '.join(PL.room_types(building, room))} room holds no {' / '.join(fits)}"
        fits = ok
    whys = [placeable(t, piece, room) for t in fits]
    ok = [t for t, why in zip(fits, whys) if why is None]
    if not ok:
        return None, str(whys[0])
    if len(ok) > 1:
        ranked = sorted(ok, key=lambda t: (round(_product_distance(t, size), 4), t))
        if _product_distance(ranked[1], size) - _product_distance(ranked[0], size) < NM.PRODUCT_MARGIN:
            return None, f"{ranked[0]} and {ranked[1]} fit {size[0]:.2f} x {size[1]:.2f} m about equally"
        ok = ranked[:1]
    return ok[0], ""


def _name_evidence(piece: dict, text: dict, distance: float, reason: str, rule: str) -> dict:
    from wenart.furniture import names as NM

    ev = _evidence(piece, reason, NM.CONF_NAME_TEXT)
    ev.update({"entity": text.get("id"), "rule": rule,
               "name_text": {"id": text.get("id"), "text": text.get("text"), "pos": list(text.get("pos") or []),
                             "distance_m": round(float(distance), 3)}})
    if text.get("layer"):
        ev["layer"] = text["layer"]
    return ev


def _where(distance: float) -> str:
    return "on the footprint" if distance <= 1e-6 else f"{distance:.2f} m from it"


def _name_text(building: dict, piece: dict, room: Optional[dict]) -> tuple[Optional[dict], list[str]]:
    """26 Oct 2026 (``names`` rule 1): ``(proposal, notes)``: the type a furniture name text of the plan gives the
    untyped drawn ``piece`` (the text on or within ``names.NAME_NEAR_M`` of it, nearest first: it names this piece
    (``names.named_piece``), its type fits the size and the room (``_name_choice``)), else None with one note per
    text that was not used and why."""
    from wenart.furniture import names as NM

    near = NM.texts_near(building, piece)
    if not near:
        return None, []
    size = [float(v) for v in piece["footprint"]["size"]]
    notes = []
    for d, t in near:
        if any(f.get("id") != piece.get("id") for f in NM.used_by(building, t)):
            continue                                     # the text names another piece already (rule 1 or 1b)
        what = t.get("type") or f"{t.get('family')} ({' / '.join(t.get('types') or ())})"
        head = f"the documents name a {what} here ({NM.describe(t)}, {_where(d)})"
        if not any(NM.fits_size(x, piece) for x in t.get("types") or ()):
            notes.append(f"{head}: not used: its product range does not fit {size[0]:.2f} x {size[1]:.2f} m")
            continue
        owner = NM.named_piece(building, t)
        if owner is not None and owner.get("id") != piece.get("id"):
            notes.append(f"{head}: not used here: it names {owner['id']} (nearer to the text)")
            continue
        ftype, why = _name_choice(building, piece, room, list(t.get("types") or ()), size)
        if ftype is None:
            notes.append(f"{head}: not used: {why}")
            continue
        text = (f"{ftype}: the documents name it: the text {NM.describe(t)} stands {_where(d)} (within "
                f"{NM.NAME_NEAR_M:g} m, the nearest drawn piece of that size), and the type's product range fits "
                f"{size[0]:.2f} x {size[1]:.2f} m within {NM.NAME_SIZE_TOL:.0%}")
        return {"type": ftype, "method": NAME_TEXT_METHOD, "confidence": NM.CONF_NAME_TEXT, "reason": text,
                "evidence": _name_evidence(piece, t, d, text, NM.RULE_TYPE)}, notes
    return None, notes


def _zone_label_type(building: dict, piece: dict, room: Optional[dict]) -> Optional[dict]:
    """26 Oct 2026 (module docstring, zone labels): the anchor type of the zone label whose zone holds the untyped
    drawn ``piece`` ("YEMEK BÖLÜMÜ": the dining table), when the zone has no built anchor yet, the piece is the untyped
    drawn footprint of the zone nearest the label whose size fits an anchor (``names.fits_with_partners``: a table
    drawn with its chairs counts), and the type fits the room (``_name_choice``); else None."""
    from shapely.geometry import Point, Polygon

    from wenart.furniture import names as NM

    if room is None:
        return None
    zone = NM.zone_of(building, piece)
    if zone is None:
        return None
    cell = Polygon(zone["zone"]).buffer(1e-6)
    anchors = list(zone.get("anchors") or ())
    mine = [f for f in building.get("furniture") or [] if f.get("room_id") == room["id"] and f.get("footprint")
            and cell.contains(Point(*[float(v) for v in f["footprint"]["center"]]))]
    if any(f.get("type") in anchors and f.get("build") is not False for f in mine):
        return None                                      # the zone has its anchor
    label = Point(float(zone["pos"][0]), float(zone["pos"][1]))

    def key(f):
        try:
            d = placer.drawn_piece(f).polygon().distance(label)
        except (KeyError, TypeError, ValueError):
            d = 9e9
        return (round(d, 4), str(f.get("id")))

    cands = sorted((f for f in mine if untyped_drawn(f) and any(NM.fits_with_partners(t, f) for t in anchors)), key=key)
    if not cands or cands[0].get("id") != piece.get("id"):
        return None
    size = [float(v) for v in piece["footprint"]["size"]]
    ftype, _why = _name_choice(building, piece, room, anchors, size, fit=NM.fits_with_partners)
    if ftype is None:
        return None
    d = key(piece)[0]
    with_partners = not NM.fits_size(ftype, piece)
    text = (f"{ftype}: the documents name this zone of the room: the label {zone['text']!r} ({zone['id']}, a "
            f"{zone['kind']} zone of {room['id']}) stands {_where(d)}, the nearest untyped drawn footprint of its "
            f"zone; the {ftype}'s product range fits {size[0]:.2f} x {size[1]:.2f} m"
            + (f" drawn with its chairs ({NM.partner_margin(ftype):.2f} m around it)" if with_partners else "")
            + " and the room holds it")
    ev = _evidence_code(piece, ZONE_LABEL_METHOD, text, NM.CONF_NAME_TEXT)
    ev.update({"entity": zone["id"], "zone_label": {"id": zone["id"], "text": zone["text"], "kind": zone["kind"],
                                                    "pos": list(zone["pos"]), "distance_m": d}})
    return {"type": ftype, "method": ZONE_LABEL_METHOD, "confidence": NM.CONF_NAME_TEXT, "reason": text,
            "evidence": ev}


def name_text_note(building: dict, piece: dict) -> Optional[str]:
    """26 Oct 2026 (``names`` rule 1): why the furniture name texts near an untyped drawn piece did not type it ("the
    documents name a dresser here ('*SIFONIYER' (TEXT:29ABD3), on the footprint): not used: a living room holds no
    dresser"), or None when no name text stands near it or one types it. For the piece's review entry."""
    room = _rooms(building).get(piece.get("room_id") or "")
    try:
        found, notes = _name_text(building, piece, room)
    except (KeyError, TypeError, ValueError):
        return None
    return None if found is not None or not notes else "; ".join(notes)


def _code_front(building: dict, piece: dict, room: Optional[dict], ftype: str) -> Optional[float]:
    """The front rule 4 gives a piece typed ``ftype`` by code: the side opposite the only wall side, or towards the
    nearest partner (None without a room outline or a rule)."""
    if room is None or len(room.get("polygon") or []) < 3:
        return None
    mates = [f for f in building.get("furniture") or [] if f.get("room_id") == piece.get("room_id")
             and f["id"] != piece["id"]]
    others = [(f["type"], placer.drawn_piece(f, k)) for k, f in enumerate(mates)
              if f.get("type") != "unknown" and f.get("build") is not False and f.get("footprint")]
    partners = [o for t, o in others if t in schemas.orientation_rule(ftype)["partners"]]
    return _front_for(ftype, placer.drawn_piece(piece), _room_ring(room), partners)


def name_text_retypes(building: dict) -> list[dict]:
    """26 Oct 2026 (``names`` rule 1b; CLAUDE.md "code may retype a drawn piece that the vision models typed when its
    size, room and neighbours clearly say otherwise"): proposals ``{"piece_id", "type", "type_method":
    NAME_RETYPE_METHOD, "reason", "confidence", "evidence", "drawn_type", "crop", "front_deg"?}`` for the drawn pieces
    typed by the AI passes or a weak code guess (``names.RETYPE_FROM``) on which a furniture name text of another
    type is written (within ``names.NAME_RETYPE_M``; the text names this piece, no built piece of the named type
    stands near it and no piece uses it yet), when the named type fits the size and the room. Pure."""
    from wenart.furniture import names as NM

    rooms = _rooms(building)
    out: list[dict] = []
    done: set = set()
    for t in sorted(NM.texts_of(building), key=lambda t: (str(t.get("level_id")), str(t.get("id")))):
        if NM.used_by(building, t) or NM.named_near(building, t) is not None:
            continue
        owner = NM.named_piece(building, t)
        if owner is None or owner["id"] in done or owner.get("type") in (None, "unknown") \
                or owner.get("build") is False or owner.get("type_method") not in NM.RETYPE_FROM \
                or owner.get("type") in (t.get("types") or ()):
            continue
        d = NM.text_distance(t, owner)
        if d > NM.NAME_RETYPE_M + 1e-9:
            continue
        room = rooms.get(owner.get("room_id") or "")
        size = [float(v) for v in owner["footprint"]["size"]]
        ftype, _why = _name_choice(building, owner, room, list(t.get("types") or ()), size)
        if ftype is None:
            continue
        crop = _crop_of(owner)
        reason = (f"{ftype}: the documents name it: the text {NM.describe(t)} is written {_where(d)}; the "
                  f"{owner.get('type_method') or 'AI'} reading said {owner['type']}; the named type's product range "
                  f"fits {size[0]:.2f} x {size[1]:.2f} m and the room holds it (trust order: the documents' text "
                  f"before AI vision)" + (f"; plan crop {crop}" if crop else ""))
        prop = {"piece_id": owner["id"], "type": ftype, "type_method": NAME_RETYPE_METHOD, "reason": reason,
                "confidence": NM.CONF_NAME_TEXT, "drawn_type": owner["type"], "crop": crop,
                "evidence": _name_evidence(owner, t, d, reason, NM.RULE_RETYPE)}
        if owner.get("front_deg") is None:
            front = _code_front(building, owner, room, ftype)
            if front is not None:
                prop["front_deg"] = front
        out.append(prop)
        done.add(owner["id"])
    return out


def product_inside(ftype: str, size) -> Optional[tuple[float, list[float]]]:
    """26 Oct 2026 (``ai_named_members``): ``(log distance, size)`` of the drawn size itself when it lies inside the
    type's ranges (distance 0), else of the nearest real product (``sizes.products``) that fits inside the drawn
    footprint, in the drawn orientation (the long side along the drawn long side); None when none fits inside."""
    from wenart.furniture import sizes as SZ

    w, d = (float(v) for v in size[:2])
    if SZ.fits(ftype, [w, d], 0.0):
        return 0.0, [w, d]
    long_, short = max(w, d), min(w, d)
    best = None
    for prod in SZ.products(ftype):
        pl, ps = max(float(prod[0]), float(prod[1])), min(float(prod[0]), float(prod[1]))
        if pl > long_ + 1e-9 or ps > short + 1e-9:
            continue
        dist = max(abs(math.log(long_ / pl)), abs(math.log(short / ps)))
        if best is None or dist < best[0] - 1e-9:
            best = (dist, [pl, ps] if w >= d else [ps, pl])
    return best


def ai_named_members(building: dict) -> list[dict]:
    """26 Oct 2026 (module docstring): proposals ``{"piece_id", "type", "type_method": AI_MEMBER_METHOD, "reason",
    "confidence", "evidence", "drawn_type", "crop", "footprint"?}`` for the untyped drawn footprints whose room misses a
    member of its groups (``_group_wants``: a bathroom set's "shower|bathtub") and whose AI passes named that member, as
    their answer or in their reason (``names.mentioned_types``: "likely a bathtub or shower"); a type the room may not
    hold (a bunk bed in a bathroom) is ignored and said. Of two named members the one whose real product lies nearer the
    drawn size wins (``product_inside``; about equal: nothing). A drawn size outside the type's ranges takes the nearest
    real product inside the drawn footprint (``footprint``, the centre and rotation kept). One piece per missing type
    and room. Pure."""
    from wenart.furniture import names as NM

    rooms = _rooms(building)
    furniture = building.get("furniture") or []
    out: list[dict] = []
    taken: dict[str, set] = {}
    for f in sorted(furniture, key=lambda f: str(f.get("id"))):
        cands = [c for c in f.get("type_candidates") or [] if isinstance(c, dict)]
        room = rooms.get(f.get("room_id") or "")
        if not cands or room is None or not untyped_drawn(f):
            continue
        try:
            poly = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        mates = [g for g in furniture if g.get("room_id") == f.get("room_id") and g["id"] != f["id"]]
        by_id = {g["id"]: g for g in mates}
        held = outline_holds(poly, mates)
        if any(by_id[h].get("type") not in schemas.FIXED_TYPES for h in held) or _host_of(poly, mates) is not None:
            continue          # a rug or zone outline around loose pieces, or a part of a piece (the box of a curved
            #                   bath may hold a basin beside it: fixed pieces held are no reason)
        wanted = _group_wants(building, room)
        if not wanted:
            continue
        allowed = None
        if not any(t in ("other", "unknown") for t in PL.room_types(building, room)):
            allowed = PL.allowed_in(building, room)
        named: dict[str, list[str]] = {}
        for c in cands:
            who = f"pass {c.get('pass')}" + (f" ({c['model_key']})" if c.get("model_key") else "")
            if c.get("type") in schemas.SIZE_OPTIONS:
                named.setdefault(c["type"], []).append(f"{who} answered {c['type']}")
            for t in NM.mentioned_types(c.get("reason") or ""):
                if t in schemas.SIZE_OPTIONS:
                    named.setdefault(t, []).append(f"{who}'s reason names {t}")
        ignored = sorted(t for t in named if allowed is not None and t not in allowed)
        options = [t for t in named if t in wanted and t not in ignored
                   and t not in taken.get(room["id"], set())]
        ranked = sorted((r[0], t, r[1]) for t in options for r in [product_inside(t, f["footprint"]["size"])] if r)
        if not ranked or (len(ranked) > 1 and ranked[1][0] - ranked[0][0] < NM.PRODUCT_MARGIN):
            continue
        dist, ftype, size = ranked[0]
        drawn = [float(v) for v in f["footprint"]["size"]]
        crop = _crop_of(f)
        resized = abs(size[0] - drawn[0]) > 1e-6 or abs(size[1] - drawn[1]) > 1e-6
        reason = (f"{ftype}: {room['id']} misses it ({'; '.join(wanted[ftype][:2])}) and the AI passes named it "
                  f"({'; '.join(named[ftype][:3])})"
                  + (f"; ignored: {', '.join(ignored)} (not a piece of a {' + '.join(PL.room_types(building, room))} "
                     f"room)" if ignored else "")
                  + (f"; the drawn {drawn[0]:.2f} x {drawn[1]:.2f} m is outside the {ftype}'s range: the nearest real "
                     f"product inside it, {size[0]:.2f} x {size[1]:.2f} m, centre and rotation kept (CLAUDE.md: a "
                     f"misread size), drawn_footprint kept" if resized else "")
                  + (f"; plan crop {crop}" if crop else ""))
        ev = _evidence(f, reason, CONF_GROUP)
        ev.update({"rule": AI_MEMBER_RULE, "missing": wanted[ftype][:3],
                   "ai_reasons": [str(c.get("reason") or "") for c in cands if c.get("reason")][:2]})
        prop = {"piece_id": f["id"], "type": ftype, "type_method": AI_MEMBER_METHOD, "reason": reason,
                "confidence": CONF_GROUP, "evidence": ev, "drawn_type": f.get("type"), "crop": crop}
        if resized:
            prop["footprint"] = dict(f["footprint"], size=[round(size[0], 4), round(size[1], 4)])
        out.append(prop)
        # the slot is taken, with the alternatives of its role ("shower|bathtub": one of them)
        lines = set(wanted[ftype])
        taken.setdefault(room["id"], set()).update(t for t, ls in wanted.items() if set(ls) & lines)
    return out


def _apply_ai_member(item: dict, prop: dict) -> None:
    """``ai_named_members``: the type (``type_method: inferred``, ``inferred`` with the reason and the evidence) and,
    for a drawn size outside the type's ranges, the real product size with ``adjusted_by_ai`` by code (``drawn_*``
    kept, the plan crop)."""
    item["type"] = prop["type"]
    item["type_method"] = INFER_METHOD_VALUE
    item["inferred"] = True
    item["inferred_reason"] = prop["reason"]
    item.setdefault("evidence", []).append(dict(prop["evidence"]))
    if item.get("build") is False and str(item.get("not_built_reason") or "").lower().startswith("untyped"):
        item["build"] = True
        item.pop("not_built_reason", None)
    if item.get("height") is None and schemas.HEIGHTS.get(prop["type"]) is not None:
        item["height"] = schemas.HEIGHTS[prop["type"]]
    if prop.get("footprint"):
        item.setdefault("drawn_type", prop.get("drawn_type"))
        item.setdefault("drawn_footprint", copy.deepcopy(item.get("footprint")))
        item.setdefault("drawn_front_deg", item.get("front_deg"))
        item.setdefault("drawn_height", None)
        before = copy.deepcopy(item.get("footprint"))
        item["footprint"] = dict(prop["footprint"])
        label = {"by": "code", "stage": "reading", "rule": AI_MEMBER_METHOD, "reason": prop["reason"],
                 "changed": {"type": prop.get("drawn_type"), "footprint": before}}
        if prop.get("crop"):
            label["crop"] = prop["crop"]
        merge_code_label(item, label)


def _product_distance(ftype: str, size) -> float:
    from wenart.furniture import sizes as SZ

    rng = SZ.real_range(ftype) or {}
    product = rng.get("product")
    if not product:
        return 9.0
    w, d = sorted(float(v) for v in size)
    pw, pd = sorted(float(v) for v in product[:2])
    return max(abs(math.log(max(w, 1e-3) / pw)), abs(math.log(max(d, 1e-3) / pd)))


def _group_wants(building: dict, room: dict) -> dict[str, list[str]]:
    """type -> one line per missing member of that type in the room's groups (``groups.group_members``) and in its
    unbuilt drawn groups (``groups.drawn_groups``, whose built anchor's group is in the first list already)."""
    wanted: dict[str, list[str]] = {}
    for g in GR.group_members(building, room["id"]):
        for miss in g.get("missing") or []:
            for t in str(miss).split("|"):
                wanted.setdefault(t, []).append(f"{g['group_id']} (anchor {g.get('anchor_id')}) misses {miss}")
    by_id = {f["id"]: f for f in building.get("furniture") or []}
    for g in GR.drawn_groups(building, room["id"]):        # drawn groups, built or not (an unbuilt sofa too)
        if g["built"].get(g["anchor_id"]):
            continue                                     # a built anchor's group is in group_members already
        anchor = by_id.get(g["anchor_id"])
        members = [by_id[m] for m in g["members"] if m in by_id]
        for miss in GR._expected_missing(g["template"], anchor, members, room, building):
            for t in str(miss).split("|"):
                wanted.setdefault(t, []).append(f"the drawn {g['template']} group of {g['anchor_id']} misses {miss}")
    return wanted


def _adopted(building: dict, piece: dict, room: dict, ftype: str, before: int) -> bool:
    """Fix round after P4a (module docstring): True when ``piece`` typed ``ftype`` (on a copy) lowers the count of
    ``ftype`` in the room's missing lists below ``before``: a group really takes it in."""
    trial_piece = dict(piece, type=ftype, type_method="group_member")
    if trial_piece.get("build") is False:
        trial_piece["build"] = True                     # untyped and unbuilt: built once typed (_apply_code_type)
        trial_piece.pop("not_built_reason", None)
    trial = dict(building, furniture=[trial_piece if f.get("id") == piece["id"] else f
                                      for f in building.get("furniture") or []])
    return len(_group_wants(trial, room).get(ftype, [])) < before


def _l_outline_waits(building: dict, piece: dict, room: dict) -> Optional[str]:
    """Fix round after P5 (module docstring): the id of an untyped drawn piece of ``room`` (not ``piece``) whose
    vector evidence notes the reader's L outline (``symbols.l_shape``: "L outline 4.38 x 1.97 m: main seat ..."): the
    context rule will make it the room's corner sofa, so the room does not miss its seating anchor. Else None."""
    for f in building.get("furniture") or []:
        if f.get("room_id") != room.get("id") or f.get("id") == piece.get("id") or not untyped_drawn(f):
            continue
        if any(isinstance(e, dict) and L_OUTLINE_NOTE.search(str(e.get("note") or ""))
               for e in f.get("evidence") or []):
            return str(f["id"])
    return None


def _seat_anchors(building: dict, room: dict) -> list[dict]:
    """The drawn or placed seating anchors (``groups.yaml`` seating anchor types) of ``room`` with a footprint."""
    types = set((GR.load_groups().get("seating") or {}).get("anchor", {}).get("types") or ("sofa", "sofa_corner"))
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room.get("id") and f.get("type") in types
            and f.get("footprint") and not f.get("inferred_as") and not f.get("not_furniture")]


PILLOW_FRONT_NOTE = "head = side with >= 2 small closed shapes"   # symbols.front_candidates' bed-pillow rule


def _anchor_frames(anchor: dict) -> list[placer.Piece]:
    """The anchor as placer pieces in the frame of its front; without a front, both long sides are tried. A seat
    fronted by the reader's bed-pillow rule (a building read before this round: ``symbols`` keeps that rule to beds
    now; real04's oyun sofas faced away from their table) counts as without a front."""
    p = placer.drawn_piece(anchor)
    pillow = any(isinstance(e, dict) and PILLOW_FRONT_NOTE in str(e.get("note") or "")
                 for e in anchor.get("evidence") or [])
    if anchor.get("front_deg") is not None and not pillow:
        return [p]
    base = G.front_direction_deg(p.rotation_deg)
    turn = 0.0 if p.size[0] >= p.size[1] else 90.0           # the long side faces -Y after the turn
    out = []
    for extra in (0.0, 180.0):
        fp = dict(anchor["footprint"])
        rot, size = placer.front_frame(fp, G.normalise_angle(base + turn + extra))
        out.append(dataclasses.replace(p, rotation_deg=rot, size=size))
    return out


def coffee_zone_anchor(building: dict, piece: dict, room: dict) -> Optional[str]:
    """Fix round after P5 (module docstring): the id of the seating anchor whose coffee-table place ``piece`` stands
    in, else None. A straight sofa's place: in front of its front edge (the gap from the edge to the piece's near side
    within ``COFFEE_ZONE_GAP_M``) with the piece's centre inside the sofa's front-width band. A corner sofa's place:
    that, or its open corner (the centre inside the footprint box, at most ``COFFEE_IN_BODY`` of the piece inside the
    drawn L)."""
    from wenart.furniture import group_checks as GC

    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    if poly.area <= 0:
        return None
    centre = (poly.centroid.x, poly.centroid.y)
    for anchor in _seat_anchors(building, room):
        if anchor.get("id") == piece.get("id"):
            continue
        try:
            frames = _anchor_frames(anchor)
        except (KeyError, TypeError, ValueError):
            continue
        for ap in frames:
            half_w, half_d = ap.size[0] / 2.0, ap.size[1] / 2.0
            x, y = GC.to_local(ap, centre)
            if abs(x) > half_w + 1e-9:
                continue                               # outside the anchor's front-width band
            if anchor.get("type") == "sofa_corner":
                # the open corner (inside the box, off the drawn L) or the strip in front of the box; a corner sofa
                # without its L (typed by code) holds its table in the box's open corner too (real03 f_L0_191)
                body = ap.polygon() if ap.shape == "L" else None
                if -half_d - COFFEE_ZONE_GAP_M[1] - 1e-9 <= y <= half_d + 1e-9 and (
                        body is None or poly.intersection(body).area <= COFFEE_IN_BODY * poly.area + 1e-9):
                    return str(anchor["id"])
                continue
            near = max(GC.to_local(ap, c)[1] for c in poly.exterior.coords)
            gap = -half_d - near                       # from the anchor's front edge to the piece's near side
            if COFFEE_ZONE_GAP_M[0] - 1e-9 <= gap <= COFFEE_ZONE_GAP_M[1] + 1e-9:
                return str(anchor["id"])
    return None


def tv_place_anchor(building: dict, piece: dict, room: dict) -> Optional[str]:
    """Fix round after P5 (module docstring): the id of the seating anchor that faces ``piece`` as its TV unit, else
    None: the piece has a side on a wall (``WALL_SIDE_M``), lies outside every seating anchor's box (at most
    ``COFFEE_IN_BODY`` of it inside), and stands in front of the anchor at least ``TV_MIN_M`` from its front edge,
    within ``TV_FACING_DEG`` of its front direction."""
    from wenart.furniture import group_checks as GC

    try:
        p = placer.drawn_piece(piece)
        poly = p.polygon()
    except (KeyError, TypeError, ValueError):
        return None
    if poly.area <= 0 or len(room.get("polygon") or []) < 3 or not _wall_sides(p, _room_ring(room)):
        return None
    anchors = _seat_anchors(building, room)
    for anchor in anchors:
        try:
            box = dataclasses.replace(placer.drawn_piece(anchor), shape=None).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if poly.intersection(box).area > COFFEE_IN_BODY * poly.area + 1e-9:
            return None                                # drawn inside a sofa's box: never its TV unit
    centre = (poly.centroid.x, poly.centroid.y)
    for anchor in anchors:
        if anchor.get("id") == piece.get("id"):
            continue
        try:
            frames = _anchor_frames(anchor)
        except (KeyError, TypeError, ValueError):
            continue
        for ap in frames:
            x, y = GC.to_local(ap, centre)
            along = -y - ap.size[1] / 2.0
            if along >= TV_MIN_M - 1e-9 and math.degrees(math.atan2(abs(x), -y)) <= TV_FACING_DEG + 1e-9:
                return str(anchor["id"])
    return None


ROLE_PLACES = {"table_coffee": coffee_zone_anchor, "tv_unit": tv_place_anchor}


def _role_place_ok(building: dict, piece: dict, room: dict, ftype: str) -> bool:
    """Fix round after P5 (module docstring): a seating partner typed by the group-member rule stands at its role's
    place (``ROLE_PLACES``: the coffee table in front of a seating anchor or in its open corner, the TV unit at a wall
    facing it); other types are not checked here (``_adopted`` checks that a group takes the piece in)."""
    check = ROLE_PLACES.get(ftype)
    return True if check is None else check(building, piece, room) is not None


def _needs_wardrobe(building: dict, room: dict) -> Optional[str]:
    """26 Oct 2026 (``_wardrobe_run_type``): why the room's program needs a wardrobe run, or None: a dressing room or
    walk-in closet (``program.room_kind`` ``dressing`` or ``program.dressing_room``: wardrobe runs along its walls), or
    a room kind whose required groups have a wardrobe anchor (a bedroom's storage) with no wardrobe built yet."""
    from wenart.furniture import program as PR

    kind = PR.room_kind(building, room)
    if kind == WARDROBE_ROOM or PR.dressing_room(building, room):
        return f"{room['id']} is a dressing room: its program puts wardrobe runs along its walls (groups.yaml dressing)"
    present = {f.get("type") for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
               and f.get("build") is not False}
    if "wardrobe" in present:
        return None
    required = {g for g, req, _opts in PR._rows(kind, PR._area(room), placer.room_context(building, room).polygon,
                                                 building, room, room.get("room_subtype")) if req}
    for name, template in GR.load_groups().items():
        if name in required and template["layout"] == "anchored" and "wardrobe" in template["anchor"]["types"]:
            return f"the {kind} room misses its {name} anchor (wardrobe)"
    return None


def _wardrobe_candidate(piece: dict, room: dict) -> Optional[tuple[float, float, int]]:
    """``(length, depth, wall side index)`` of an untyped drawn footprint that can be a wardrobe run: its long side on a
    wall (``side_on_wall``), its length in the wardrobe's width range (``sizes``, +15 %), its depth in
    ``WARDROBE_DEPTH_M``; else None."""
    from wenart.furniture import sizes as SZ

    if not untyped_drawn(piece) or len(room.get("polygon") or []) < 3:
        return None
    w, d = (float(v) for v in piece["footprint"]["size"][:2])
    length, depth = max(w, d), min(w, d)
    rng = SZ.real_range("wardrobe") or {}
    lo, hi = rng.get("width") or (0.8, 3.2)
    if not (lo / 1.15 <= length <= hi * 1.15 and WARDROBE_DEPTH_M[0] - 1e-9 <= depth <= WARDROBE_DEPTH_M[1] + 1e-9):
        return None
    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    ring = _room_ring(room)
    for k, (a, b) in enumerate(_sides(poly)):
        if abs(math.dist(a, b) - length) <= 0.02 and side_on_wall(a, b, ring):
            return length, depth, k
    return None


def _wardrobe_run_type(building: dict, piece: dict, room: dict) -> Optional[dict]:
    """26 Oct 2026 (module docstring, wardrobe runs; method ``group_member``): an untyped drawn footprint along a wall
    of a room whose program needs a wardrobe run (``_needs_wardrobe``), with a wardrobe run's length and a depth near a
    wardrobe's (``_wardrobe_candidate``), is a wardrobe: in a dressing room every such footprint, elsewhere only the
    room's one candidate. A depth outside the wardrobe's range is snapped to the product depth, the back kept on its
    wall (``snapped``: ``drawn_footprint`` kept, ``adjusted_by_ai`` by code); the front faces the room. An AI answer of
    another type the room holds and the size fits leaves it to the plan crop."""
    from wenart.furniture import sizes as SZ

    found = _wardrobe_candidate(piece, room)
    if found is None:
        return None
    why = _needs_wardrobe(building, room)
    if why is None:
        return None
    dressing = why.endswith("(groups.yaml dressing)")
    if not dressing:
        others = [f for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
                  and f["id"] != piece["id"] and _wardrobe_candidate(f, room) is not None]
        if others:
            return None                                  # two candidates: the plan crop decides (AI)
    size = [float(v) for v in piece["footprint"]["size"]]
    allowed = PL.allowed_in(building, room) | {"wardrobe"}
    answers = {c.get("type") for c in piece.get("type_candidates") or [] if c.get("type")}
    # (a stair is typed by the stair rule from the drawing, never by an AI answer alone: hanger lines read as treads)
    if any(a not in (None, "unknown", "wardrobe", "stair") and a in allowed and SZ.fits(a, size, 0.15)
           for a in answers):
        return None
    length, depth, k = found
    rng = SZ.real_range("wardrobe") or {}
    dlo, dhi = rng.get("depth") or (0.5, 0.7)
    poly = placer.drawn_piece(piece).polygon()
    a, b = _sides(poly)[k]
    mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
    c = poly.centroid
    ux, uy = c.x - mid[0], c.y - mid[1]
    n = math.hypot(ux, uy) or 1.0
    ux, uy = ux / n, uy / n
    front = round(G.normalise_angle(math.degrees(math.atan2(uy, ux))), 3)
    out_depth = depth if dlo - 1e-9 <= depth <= dhi + 1e-9 else float((rng.get("product") or (1.2, 0.6))[1])
    text = (f"wardrobe: {why}; the drawn {length:.2f} x {depth:.2f} m stands with its long side on a wall, its length "
            f"fits a wardrobe run ({_span_text(rng.get('width') or (0.8, 3.2))}) and its depth is a wardrobe's "
            f"({WARDROBE_DEPTH_M[0]:.2f}-{WARDROBE_DEPTH_M[1]:.2f} m drawn)")
    out = {"type": "wardrobe", "method": "group_member", "confidence": CONF_GROUP, "front_deg": front}
    if abs(out_depth - depth) > 1e-6:
        text += (f"; the depth is outside the wardrobe's range ({dlo:.2f}-{dhi:.2f} m): {out_depth:.2f} m, the back "
                 f"kept on its wall, drawn_footprint kept (CLAUDE.md: a real product size)")
        cx, cy = mid[0] + ux * out_depth / 2.0, mid[1] + uy * out_depth / 2.0
        w0, d0 = size
        new_size = [w0, out_depth] if w0 >= d0 else [out_depth, d0]
        out["footprint"] = {"center": [round(cx, 4), round(cy, 4)], "size": [round(new_size[0], 4),
                                                                              round(new_size[1], 4)],
                            "rotation_deg": piece["footprint"]["rotation_deg"]}
        out["snapped"] = True
    out["reason"] = text
    out["evidence"] = _evidence_code(piece, "group_member", text, CONF_GROUP, missing=[why], rule_detail=WARDROBE_RULE)
    return out


def _span_text(pair) -> str:
    return f"{float(pair[0]):.2f}-{float(pair[1]):.2f} m"


def _group_member_type(building: dict, piece: dict, room: dict) -> Optional[dict]:
    from wenart.furniture import program as PR
    from wenart.furniture import sizes as SZ

    wanted = _group_wants(building, room)
    by_group = {t: len(v) for t, v in wanted.items()}   # fix round after P4a: the groups' own count per type
    kind = PR.room_kind(building, room)
    present = {f.get("type") for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
               and f.get("type") not in (None, "unknown") and f.get("build") is not False}
    required = {g for g, req, _opts in PR._rows(kind, PR._area(room), placer.room_context(building, room).polygon,
                                                 building, room, room.get("room_subtype")) if req}
    # Fix round after P5 (module docstring): an untyped L outline of the room is its corner sofa to be (the context
    # rule types it): the room does not miss its seating anchor, and no other footprint stands in for it.
    l_waits = _l_outline_waits(building, piece, room)
    # 26 Oct 2026 (zone labels): a footprint in a labelled zone of another kind ("YEMEK BÖLÜMÜ" in a salon) is never
    # the room kind's missing anchor (real06 f_L0_011, the round dining table, was "the living room's corner sofa")
    from wenart.furniture import names as NM

    zone = NM.zone_of(building, piece)
    foreign_zone = zone is not None and zone.get("kind") != kind
    for name, template in GR.load_groups().items():
        # Only the anchor of a group the room kind requires (a bedroom's bed, a living room's sofa): an optional
        # group's anchor (a dining table in a living room) is no evidence for a lone footprint.
        if name not in required or template["layout"] != "anchored" or foreign_zone:
            continue
        if l_waits is not None and "sofa_corner" in template["anchor"]["types"]:
            continue
        for t in template["anchor"]["types"]:
            if t not in present and not (set(template["anchor"]["types"]) & present):
                wanted.setdefault(t, []).append(f"the {kind} room misses its {name} anchor ({t})")
    if not wanted:
        return None
    size = [float(v) for v in piece["footprint"]["size"]]
    allowed = PL.allowed_in(building, room) | set(schemas.allowed_types(kind, room.get("room_subtype")))
    fits = sorted(t for t in wanted if t in allowed and SZ.fits(t, size, 0.15))
    # 26 Oct 2026 (module docstring): a wall type needs its back on a wall, a round piece is no chair: else the next
    # type (real06: the 0.92 x 0.77 m armchair f_L1_020, drawn at 60.5 deg, was "the bedroom's missing wardrobe")
    fits = [t for t in fits if placeable(t, piece, room) is None]
    if not fits:
        return None
    # Fix round after P5 (module docstring): a coffee table or TV unit only where its role stands. A footprint that
    # fits such a role by size but stands elsewhere is left to the plan crop (AI), unless another role it fits by
    # size stands where it should (a table in front of the sofa that is also TV-unit sized); never another member.
    placed = [t for t in fits if _role_place_ok(building, piece, room, t)]
    if len(placed) < len(fits):
        if not any(t in ROLE_PLACES for t in placed):
            return None
        fits = placed
    # An AI pass named another type that fits the size and the shape (real02's sofa / kitchen_island): the plan
    # crop decides, not the group rule.
    answers = {c.get("type") for c in piece.get("type_candidates") or [] if c.get("type")}
    if any(a not in fits and a in schemas.SIZE_OPTIONS and SZ.fits(a, size, 0.15) and _shape_ok(a, size)
           for a in answers):
        return None
    if len(fits) > 1:
        ranked = sorted(fits, key=lambda t: (round(_product_distance(t, size), 4), t))
        best, second = ranked[0], ranked[1]
        if _product_distance(second, size) - _product_distance(best, size) < 0.15:
            return None                         # two members fit about equally: the plan crop decides (AI)
        fits = [best]
    ftype = fits[0]
    if by_group.get(ftype) and not _adopted(building, piece, room, ftype, by_group[ftype]):
        # fix round after P4a (module docstring): no group takes this footprint in (too far from the anchor that
        # misses the type, or nearer another one): the plan crop decides (AI), never one more member of that type
        return None
    text = (f"{ftype}: {'; '.join(wanted[ftype][:2])}, and the type's product range fits {size[0]:.2f} x "
            f"{size[1]:.2f} m (the only missing member of that size)")
    return {"type": ftype, "method": "group_member", "confidence": CONF_GROUP, "reason": text,
            "evidence": _evidence_code(piece, "group_member", text, CONF_GROUP, missing=wanted[ftype][:3])}


def type_by_code(building: dict, piece: dict) -> Optional[dict]:
    """Milestone 13 (§13.2): ``{"type", "method": twin | level | same_block | block | name_text | group_member,
    "evidence", "confidence", "reason", "front_deg"?, "footprint"?}`` for an untyped drawn footprint, or None when
    code cannot tell (the AI types it from the plan crop). The methods are tried in that order (the module
    docstring)."""
    if not untyped_drawn(piece):
        return None
    room = _rooms(building).get(piece.get("room_id") or "")
    if room is not None:
        found = _twin_type(building, piece, room)
        if found is not None:
            return found
    found = _level_type(building, piece, room)
    if found is not None:
        return found
    found = _same_block_type(building, piece)          # 26 Oct 2026: one block drawn again elsewhere, one type
    if found is not None:
        return found
    # An outline drawn around other pieces (a rug, a zone, a counter run) or a part inside a typed piece is no
    # furniture of its own: rules 1 and 1b of ``infer_types`` decide those, not a block word or a missing member.
    try:
        poly = placer.drawn_piece(piece).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    mates = [f for f in building.get("furniture") or [] if f.get("room_id") == piece.get("room_id")
             and f["id"] != piece["id"]]
    if outline_holds(poly, mates) or _host_of(poly, mates) is not None:
        return None
    found = _block_type(building, piece, room)
    if found is None:
        found = _name_text(building, piece, room)[0]      # 26 Oct 2026: a furniture name written beside it
    if found is None:
        found = _zone_label_type(building, piece, room)   # 26 Oct 2026: a zone label of its room ("YEMEK BÖLÜMÜ")
    if found is None and room is not None:
        found = _group_member_type(building, piece, room)
    if found is None and room is not None:
        found = _wardrobe_run_type(building, piece, room)  # 26 Oct 2026: a wardrobe run the room's program needs
    if found is None:
        return None
    if room is not None and piece.get("front_deg") is None and found.get("front_deg") is None \
            and len(room.get("polygon") or []) >= 3:
        # The front as rule 4 gives it: the side opposite the only wall side, or towards the nearest partner.
        front = _code_front(building, piece, room, found["type"])
        if front is not None:
            found["front_deg"] = front
    return found


def code_types(building: dict) -> list[dict]:
    """Every untyped drawn piece code can type (``type_by_code``), as proposals ``{"piece_id", "type",
    "type_method", "reason", "confidence", "evidence", ...}``; applied in rounds on a working copy so chains resolve
    (a twin of a piece typed by another level). The building is unchanged."""
    work = copy.deepcopy(building)
    out: list[dict] = []
    for _round in range(CODE_ROUNDS):
        found = 0
        for f in work.get("furniture") or []:
            if not untyped_drawn(f):
                continue
            prop = type_by_code(work, f)
            if prop is None:
                continue
            prop = dict(prop, piece_id=f["id"], type_method=prop["method"])
            _apply_code_type(f, prop, proposal=False)     # at once: a missing member is missing only once
            out.append(prop)
            found += 1
        if not found:
            break
    return out


def _apply_code_type(item: dict, prop: dict, proposal: bool) -> None:
    before = {"type": item.get("type"), "footprint": copy.deepcopy(item.get("footprint")),
              "front_deg": item.get("front_deg"), "height": item.get("height")}
    item["type"] = prop["type"]
    item["type_method"] = prop["type_method"]
    item["inferred"] = True
    item["inferred_reason"] = prop["reason"]
    item.setdefault("evidence", []).append(dict(prop["evidence"]))
    if item.get("build") is False and str(item.get("not_built_reason") or "").lower().startswith("untyped"):
        item["build"] = True
        item.pop("not_built_reason", None)
    if item.get("height") is None and schemas.HEIGHTS.get(prop["type"]) is not None:
        item["height"] = schemas.HEIGHTS[prop["type"]]
    if proposal:
        # The completion path: the locked check allows a typed unknown piece with its drawn footprint and status
        # as a validated change (``adjusted_by_ai`` with the reason and ``drawn_type``, ``locked._agent_problems``:
        # "a drawn unknown that was not built may be typed"); ``type_proposal`` keeps the Milestone 10 rule too.
        item["type_proposal"] = True
        if item.get("drawn_type") is None:
            item["drawn_type"] = "unknown"
        item["adjusted_by_ai"] = {"by": "code", "stage": "layout", "typed_by_code": prop["type_method"],
                                  "reason": f"typed {prop['type']} by code ({prop['type_method']}): {prop['reason']}"}
        return
    if prop["type_method"] in ("twin", "level", SAME_BLOCK_METHOD) and prop.get("source_status"):
        item["status"] = prop["source_status"]      # the same drawing as an agreed piece: its status
    if prop.get("footprint") and prop.get("snapped"):
        # 26 Oct 2026 (wardrobe runs): the drawn depth outside the type's range snapped to a real product's, the
        # drawn values kept (CLAUDE.md: a drawn size outside the product range ... ``adjusted_by_ai``)
        for key in ("type", "footprint", "front_deg", "height"):
            item.setdefault(f"drawn_{key}", before[key])
        merge_code_label(item, {"by": "code", "stage": "reading", "rule": WARDROBE_RULE, "reason": prop["reason"],
                                "changed": {"type": before["type"], "footprint": before["footprint"]}})
        item["front_deg"] = None                     # the snapped footprint's front (below)
    if prop.get("footprint"):
        item["footprint"] = dict(prop["footprint"])
    if prop.get("front_deg") is not None and item.get("front_deg") is None:
        if prop.get("footprint"):
            item["front_deg"] = round(float(prop["front_deg"]), 3)
        else:
            set_front(item, float(prop["front_deg"]))


def apply_code_types(building: dict, proposal: bool = False) -> tuple[dict, list[dict]]:
    """A copy of the building with ``code_types`` applied (``type_method`` the method, ``inferred`` with the
    evidence) and the proposals; ``proposal=True`` for the completion path (see the module docstring)."""
    props = code_types(building)
    b = copy.deepcopy(building)
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    for prop in props:
        if prop["piece_id"] in by_id:
            _apply_code_type(by_id[prop["piece_id"]], prop, proposal)
    return b, props


def infer_types(building: dict) -> list[dict]:
    """``[{"piece_id", "type", "reason", "confidence", "evidence": {...}}]`` (proposals; the building is unchanged).
    Milestone 13: the code-typed pieces (``code_types``: ``type_method`` twin / level / block / group_member) come
    first; the rules below see the building with them applied."""
    coded = code_types(building)
    out = list(coded)
    if coded:
        building = apply_code_types(building)[0]
    # 26 Oct 2026: the member the room misses, named by the AI passes (answer or reason), before the size inference
    out += ai_named_members(building)
    done = {p["piece_id"] for p in out}
    rooms = _rooms(building)
    furniture = building.get("furniture") or []
    for item in furniture:
        if item["id"] in done:
            continue
        if item.get("type") != "unknown" or item.get("source") != "from_documents" or item.get("build") is False:
            continue
        room = rooms.get(item.get("room_id"))
        if room is None:
            continue
        piece = placer.drawn_piece(item)
        poly = piece.polygon()
        mates = [f for f in furniture if f.get("room_id") == room["id"] and f["id"] != item["id"]]
        # 27 Oct 2026: the small marks an outline holds (its cushions) never make it a rug; a small mark drawn on a
        # larger drawn outline is a detail of it, before any type fits its size (a 0.21 m "potted plant")
        held = outline_holds(poly, mates)
        drawn_host = drawn_host_of(item, poly, mates)
        if drawn_host is not None:
            reason = (f"drawn inside {drawn_host['type']} {drawn_host['id']} "
                      f"({_sorted_size(drawn_host)[1]:.2f} x {_sorted_size(drawn_host)[0]:.2f} m): a cushion, pillow or "
                      f"detail drawn on that piece, not a piece of its own (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        if held and not any(f["type"] in schemas.FIXED_TYPES for f in mates if f["id"] in held):
            reason = (f"outline {piece.size[0]:.2f} x {piece.size[1]:.2f} m around {len(held)} other piece(s) "
                      f"({', '.join(held[:6])}): a rug or zone outline, not a piece (not built; the decor rules lay "
                      f"rugs under the groups)")
            out.append({"piece_id": item["id"], "type": OUTLINE_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        ring = _room_ring(room)
        on_wall = bool(_wall_sides(piece, ring))
        others = [(f["type"], placer.drawn_piece(f, k)) for k, f in enumerate(mates)
                  if f.get("type") != "unknown" and f.get("build") is not False]
        if held:
            continue                       # an outline around fixed equipment: a counter run (split at ingest)
        host = _host_of(poly, mates)
        if host is not None:
            reason = (f"drawn inside {host['type']} {host['id']} ({DETAIL_INSIDE:.0%} or more of it): a detail of that "
                      f"piece (a sink bowl, an appliance front), not a piece of its own (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        size_now = sorted(float(v) for v in item["footprint"]["size"])
        if (size_now[1] < MARK_SIDE_M or size_now[0] < MARK_THIN_M) and not any(
                PL._fits(t, size_now) for t in PL._size_table() if t not in SKIP_TYPES):
            reason = (f"{size_now[1]:.2f} x {size_now[0]:.2f} m fits no type and is "
                      + (f"smaller than {MARK_SIDE_M} m both ways" if size_now[1] < MARK_SIDE_M
                         else f"thinner than {MARK_THIN_M} m")
                      + ": a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        types = PL.room_types(building, room)
        rtype = " + ".join(types)
        if any(t in ("other", "unknown") for t in types):
            # A room of no known purpose (real02's play and rest room is "other") says nothing about its pieces: the
            # room rule does not narrow the types there.
            allowed = {t for t in schemas.SIZE_OPTIONS if t not in schemas.CHILD_ONLY_TYPES}
        else:
            allowed = PL.allowed_in(building, room)
        size = [float(v) for v in item["footprint"]["size"]]
        # 27 Oct 2026: a type whose labelled zone of the room lies elsewhere is not this piece's (names module)
        from wenart.furniture import names as NM
        elsewhere = NM.zone_types_elsewhere(building, item)
        sized = [t for t in allowed if t not in SKIP_TYPES and t in PL._size_table() and PL._fits(t, size)
                 and _shape_ok(t, size) and t not in elsewhere]
        # 26 Oct 2026 (module docstring): a wall type's back on a wall (within 5 deg), never a round chair
        fits = sorted(t for t in sized if _position_ok(t, piece, on_wall, others) and placeable(t, item, room) is None)
        answers = {c.get("type") for c in item.get("type_candidates") or []} - elsewhere
        named = sorted(answers & set(fits))
        # An AI pass named another type that fits the size and the room: the piece is ambiguous (real02's sofas in
        # the open kitchen: kitchen_island / sofa); the agent decides on the plan crop, nothing is inferred.
        rivals = sorted((answers & set(sized)) - set(fits[:1] if len(fits) == 1 else named[:1]))
        if rivals:
            continue
        if len(fits) == 1:
            ftype, conf = fits[0], CONF_ONE
            reason = (f"{ftype}: the only type whose size range fits {size[0]:.2f} x {size[1]:.2f} m, that a "
                      f"{rtype} room holds and whose position rule holds here")
        elif len(named) == 1:
            ftype, conf = named[0], CONF_NAMED
            reason = (f"{ftype}: named by an AI pass and the only named type that fits the size ({size[0]:.2f} x "
                      f"{size[1]:.2f} m), the {rtype} room and the position (others fitting: "
                      f"{', '.join(t for t in fits if t != ftype)})")
        else:
            continue
        partners = [o for t, o in others if t in schemas.orientation_rule(ftype)["partners"]]
        prop = {"piece_id": item["id"], "type": ftype, "reason": reason, "confidence": conf,
                "evidence": _evidence(item, reason, conf)}
        if item.get("front_deg") is None:
            front = _front_for(ftype, piece, ring, partners)
            if front is not None:
                prop["front_deg"] = front
        out.append(prop)
    # 26 Oct 2026 (names rule 1b): a furniture name text written on a piece the AI typed otherwise names it
    done = {p["piece_id"] for p in out}
    out += [p for p in name_text_retypes(building) if p["piece_id"] not in done]
    done = {p["piece_id"] for p in out}
    # fix round after P4a: the drawn nightstand-with-lamp symbols at a bed's head (module docstring)
    out += [p for p in nightstand_symbols(building) if p["piece_id"] not in done]
    # fix round after P5 (user decision of 22 Oct 2026): a seat drawn in a corner sofa's open corner is its table
    out += [p for p in corner_tables(building) if p["piece_id"] not in done]
    # 26 Oct 2026: a round "lamp" in the middle of three seats facing it is their table
    done = {p["piece_id"] for p in out}
    out += [p for p in ringed_tables(building) if p["piece_id"] not in done]
    # fix round after P6a: two overlapping drawn lamp (plant) symbols are one lamp (plant) drawn twice
    done = {p["piece_id"] for p in out}
    out += [p for p in duplicate_symbols(building) if p["piece_id"] not in done and p["kept_id"] not in done]
    return out


def _nightstand_size(size) -> bool:
    rng = PL.size_range("nightstand")
    if rng is None:
        return False
    (w0, w1), (d0, d1) = rng
    w, d = (float(v) for v in size)
    return (w0 <= w <= w1 and d0 <= d <= d1) or (w0 <= d <= w1 and d0 <= w <= d1)


def _crop_of(item: dict) -> Optional[str]:
    """The reading's plan crop of the piece's question (an AI evidence entry ``recognition:<key>``), else None."""
    for e in item.get("evidence") or []:
        entity = str((e or {}).get("entity") or "") if isinstance(e, dict) else ""
        if entity.startswith("recognition:") and len(entity) > len("recognition:"):
            return RECOGNITION_CROP.format(key=entity.split(":", 1)[1])
    return None


def nightstand_symbols(building: dict) -> list[dict]:
    """Fix round after P4a (module docstring): proposals ``{"piece_id", "type": "nightstand", "type_method":
    NIGHTSTAND_METHOD, "reason", "confidence", "evidence", "front_deg", "drawn_type", "bed_id", "side", "crop"}``
    for the drawn ``floor_lamp`` / ``side_table`` pieces of a nightstand's size standing beside a drawn bed's head
    (``group_checks.nightstand_place``: the back within ``nightstand_gap`` of the headboard line; the symbol from inside
    the bed block up to ``nightstand_gap`` outside the long side), one per free side and at most the bed's
    nightstands (``schemas.NIGHTSTANDS_PER_BED``); nearest first. Pure; the building is unchanged."""
    from wenart.furniture import group_checks as GC

    gap_max = float(GR.rule("nightstand_gap")["max"])
    furniture = building.get("furniture") or []
    out: list[dict] = []
    taken: set = set()
    for room in building.get("rooms") or []:
        items = [f for f in furniture if f.get("room_id") == room.get("id") and f.get("source") == "from_documents"
                 and f.get("build") is not False and f.get("footprint")]
        beds = sorted((f for f in items if schemas.NIGHTSTANDS_PER_BED.get(f.get("type"), 0) > 0),
                      key=lambda f: str(f["id"]))
        cands = [f for f in items if f.get("type") in NIGHTSTAND_SYMBOL_TYPES
                 and _nightstand_size(f["footprint"]["size"])]
        if not beds or not cands:
            continue
        stands = [f for f in items if f.get("type") == "nightstand"]
        for bed in beds:
            try:
                bp = placer.drawn_piece(bed)
            except (KeyError, TypeError, ValueError):
                continue
            half = bp.size[0] / 2.0

            def beside(f) -> Optional[dict]:
                try:
                    piece = placer.drawn_piece(f)
                except (KeyError, TypeError, ValueError):
                    return None
                xs = [abs(GC.to_local(bp, c)[0]) for c in piece.polygon().exterior.coords]
                if max(xs) < half - NIGHTSTAND_SIDE_IN_M or min(xs) > half + gap_max + 1e-9:
                    return None                     # not at the bed's long side (the middle of the bed, or too far)
                place = GC.nightstand_place(bp, piece)
                return place if place["head_offset_m"] <= gap_max + 1e-9 else None

            have = {pl["side"] for pl in (beside(f) for f in stands) if pl is not None}
            best: dict[str, tuple] = {}
            for f in cands:
                if f["id"] in taken:
                    continue
                pl = beside(f)
                if pl is None or pl["side"] in have:
                    continue
                key = (round(pl["head_offset_m"] + abs(pl["side_gap_m"]), 4), str(f["id"]))
                if pl["side"] not in best or key < best[pl["side"]][0]:
                    best[pl["side"]] = (key, f, pl)
            want = schemas.NIGHTSTANDS_PER_BED[bed["type"]] - len(have)
            front = bed.get("front_deg")
            if front is None:
                front = G.front_direction_deg(bp.rotation_deg)
            for side, (_key, f, pl) in sorted(best.items(), key=lambda kv: kv[1][0])[:max(0, want)]:
                taken.add(f["id"])
                w, d = (float(v) for v in f["footprint"]["size"])
                crop = _crop_of(f)
                text = (f"nightstand: a drawn {f['type']} of a nightstand's size ({w:.2f} x {d:.2f} m) at the {side} "
                        f"side of the drawn {bed['type']} {bed['id']}'s head (back {pl['head_offset_m']:.2f} m from "
                        f"the headboard line, {pl['side_gap_m']:.2f} m from the bed side; nightstand_gap "
                        f"{gap_max:.2f} m): the bed's nightstand drawn with its table lamp, not a floor lamp"
                        + (f" (plan crop {crop})" if crop else ""))
                ev = _evidence_code(f, NIGHTSTAND_METHOD, text, CONF_NIGHTSTAND, bed=bed["id"], side=side,
                                    drawn_type=f["type"])
                ev["rule"] = "furniture.infer.nightstand_symbols"
                if crop:
                    ev["crop"] = crop
                out.append({"piece_id": f["id"], "type": "nightstand", "type_method": NIGHTSTAND_METHOD,
                            "reason": text, "confidence": CONF_NIGHTSTAND, "evidence": ev,
                            "front_deg": round(float(front) % 360.0, 3), "drawn_type": f["type"], "bed_id": bed["id"],
                            "side": side, "crop": crop})
    return out


def _apply_nightstand(item: dict, prop: dict) -> None:
    """A nightstand symbol (``nightstand_symbols``): the type, the bed's front, ``inferred`` with the reason and
    ``adjusted_by_ai`` (``by: code``) with the drawn values kept (CLAUDE.md: every change keeps ``drawn_type``,
    ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height`` and is labelled with the reason)."""
    item.setdefault("drawn_type", item.get("type"))
    item.setdefault("drawn_footprint", copy.deepcopy(item.get("footprint")))
    item.setdefault("drawn_front_deg", item.get("front_deg"))
    item.setdefault("drawn_height", item.get("height"))
    changed = {"type": item.get("type"), "front_deg": item.get("front_deg")}
    item["type"] = prop["type"]
    item["type_method"] = prop["type_method"]
    item["inferred"] = True
    item["inferred_reason"] = prop["reason"]
    item.setdefault("evidence", []).append(dict(prop["evidence"]))
    if prop.get("front_deg") is not None and (item.get("front_deg") is None or G.angle_difference_deg(
            float(item["front_deg"]), float(prop["front_deg"])) > 1.0):
        set_front(item, float(prop["front_deg"]))
    if isinstance(item.get("assumed"), list) and item.get("front_deg") is not None:
        item["assumed"] = [a for a in item["assumed"] if a != "front_deg"]
    label = {"by": "code", "stage": "reading", "rule": prop["type_method"], "reason": prop["reason"],
             "changed": changed}
    if prop.get("crop"):
        label["crop"] = prop["crop"]
    merge_code_label(item, label)           # fix round after P5, review: an earlier code record is kept


LABEL_MERGED_KEYS = ("reason", "changed", "rule", "rules", "crop", "by")


def merge_code_label(item: dict, label: dict) -> dict:
    """Fix round after P5 (22 Oct 2026), review (module docstring): ``label`` (a code record: ``by: code``, ``rule``,
    ``reason``, ``changed``, optional ``crop``) as the piece's ``adjusted_by_ai``, merged into an earlier code record
    instead of replacing it: the reasons joined ("<earlier>; <this>"), ``changed`` keeps the earliest value of every
    field, ``rules`` lists every rule in order, ``rule`` is this one, the earlier record's crop and other keys stay. An
    earlier record of an agent (``model``) or of another author (``by`` not code) is kept under ``previous`` (oldest
    first, as ``edit_ops._label`` keeps them). Returns the record set."""
    old = item.get("adjusted_by_ai") if isinstance(item.get("adjusted_by_ai"), dict) else None
    if not old:
        item["adjusted_by_ai"] = label
        return label
    if old.get("model") or old.get("by") not in (None, "code"):
        new = dict(label)
        previous = [copy.deepcopy(r) for r in old.get("previous") or [] if isinstance(r, dict)]
        previous.append({k: copy.deepcopy(v) for k, v in old.items() if k != "previous"})
        new["previous"] = previous
        item["adjusted_by_ai"] = new
        return new
    new = copy.deepcopy(old)
    new["by"] = "code"
    for k, v in label.items():
        if k not in LABEL_MERGED_KEYS:
            new.setdefault(k, copy.deepcopy(v))
    reasons = [r for r in (old.get("reason"), label.get("reason")) if r]
    if len(reasons) == 2 and reasons[0] == reasons[1]:
        reasons = reasons[:1]
    new["reason"] = "; ".join(str(r) for r in reasons)
    changed = dict(old.get("changed") or {})
    for k, v in (label.get("changed") or {}).items():
        changed.setdefault(k, copy.deepcopy(v))
    new["changed"] = changed
    rules = list(old.get("rules") or ([old["rule"]] if old.get("rule") else []))
    if label.get("rule") and label["rule"] not in rules:
        rules.append(label["rule"])
    if rules:
        new["rules"] = rules
    new["rule"] = label.get("rule") or old.get("rule")
    if not new.get("crop") and label.get("crop"):
        new["crop"] = label["crop"]
    item["adjusted_by_ai"] = new
    return new


def corner_tables(building: dict) -> list[dict]:
    """Fix round after P5 (module docstring; user decision of 22 Oct 2026): proposals ``{"piece_id", "type":
    "table_coffee", "type_method": CORNER_TABLE_METHOD, "reason", "confidence", "evidence", "drawn_type", "crop"}`` for
    the drawn seats (``CORNER_TABLE_FROM``, typed by the AI passes or by the group-member rule, never by a block name or
    a reading rule of the drawing) of a coffee table's size (``sizes.fits``, +15 %) that stand in the open corner of a
    built drawn L corner sofa of their room: the centre inside the sofa's box, at least ``CORNER_IN_BOX`` of the piece
    inside the box and at most ``COFFEE_IN_BODY`` inside the drawn L (the reading's notch rule). A seat cannot stand in
    another sofa's open corner. Fix round after P5, review: an ottoman only when the passes did not agree on it
    (``CORNER_OTTOMAN_FROM``). Pure; the building is unchanged."""
    from wenart.furniture import sizes as SZ

    furniture = building.get("furniture") or []
    out: list[dict] = []
    for f in furniture:
        if f.get("type") not in CORNER_TABLE_FROM or f.get("source") != "from_documents" or f.get("build") is False \
                or not f.get("footprint") or f.get("type_method") in ("block_name", "rule"):
            continue
        if f.get("type") == "ottoman" and f.get("type_method") not in CORNER_OTTOMAN_FROM:
            continue                    # fix round after P5, review: an agreed ottoman there is a normal design
        if not SZ.fits("table_coffee", [float(v) for v in f["footprint"]["size"]], 0.15):
            continue
        try:
            poly = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if poly.area <= 0:
            continue
        for s in furniture:
            if s.get("type") != "sofa_corner" or s.get("shape") != "L" or s.get("room_id") != f.get("room_id") \
                    or s.get("source") != "from_documents" or s.get("build") is False or not s.get("footprint"):
                continue
            try:
                sp = placer.drawn_piece(s)
            except (KeyError, TypeError, ValueError):
                continue
            box, body = dataclasses.replace(sp, shape=None).polygon(), sp.polygon()
            if not box.contains(poly.centroid) or poly.intersection(box).area < CORNER_IN_BOX * poly.area - 1e-9 \
                    or poly.intersection(body).area > COFFEE_IN_BODY * poly.area + 1e-9:
                continue
            crop = _crop_of(f)
            w, d = (float(v) for v in f["footprint"]["size"])
            text = (f"table_coffee: a drawn {f['type']} ({f.get('type_method')}) of a coffee table's size ({w:.2f} x "
                    f"{d:.2f} m) in the open corner of the drawn corner sofa {s['id']} "
                    f"({poly.intersection(body).area / poly.area:.0%} of it inside the L): the sofa's coffee table, "
                    f"not a seat" + (f" (plan crop {crop})" if crop else ""))
            ev = _evidence_code(f, CORNER_TABLE_METHOD, text, CONF_CORNER_TABLE, sofa=s["id"], drawn_type=f["type"])
            ev["rule"] = CORNER_TABLE_RULE
            if crop:
                ev["crop"] = crop
            out.append({"piece_id": f["id"], "type": "table_coffee", "type_method": CORNER_TABLE_METHOD,
                        "reason": text, "confidence": CONF_CORNER_TABLE, "evidence": ev, "drawn_type": f["type"],
                        "crop": crop})
            break
    return out


def ringed_tables(building: dict) -> list[dict]:
    """26 Oct 2026 (module docstring; CLAUDE.md "code may retype a drawn piece the vision models typed when its size,
    room and neighbours clearly say otherwise"): proposals ``{"piece_id", "type": "table_coffee", "type_method":
    RING_TABLE_METHOD, "reason", "confidence", "evidence", "drawn_type", "crop"}`` for a built drawn round piece
    (``shape: round``) of a coffee table's size typed as a lamp, side table, chair, ottoman or plant
    (``RING_TABLE_FROM``; never by a block name) with at least ``RING_SEATS_MIN`` drawn seats of its room around it:
    each within ``RING_REACH_M``, facing it within ``RING_FACING_DEG`` when it has a front, and no gap of
    ``RING_OPEN_DEG`` or more between their bearings (it stands in their middle). A lamp stands beside a seat, never
    in the middle of three. Pure; the building is unchanged."""
    from wenart.furniture import sizes as SZ

    furniture = building.get("furniture") or []
    out: list[dict] = []
    for f in furniture:
        if f.get("type") not in RING_TABLE_FROM or f.get("shape") != "round" or f.get("source") != "from_documents" \
                or f.get("build") is False or not f.get("footprint") or f.get("type_method") == "block_name":
            continue
        if not SZ.fits("table_coffee", [float(v) for v in f["footprint"]["size"]], 0.15):
            continue
        try:
            poly = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        c = poly.centroid
        seats = []
        for s in furniture:
            if s is f or s.get("room_id") != f.get("room_id") or s.get("type") not in RING_SEATS \
                    or s.get("build") is False or not s.get("footprint"):
                continue
            try:
                sp = placer.drawn_piece(s).polygon()
            except (KeyError, TypeError, ValueError):
                continue
            if sp.distance(poly) > RING_REACH_M + 1e-9:
                continue
            sc = sp.centroid
            to_table = math.degrees(math.atan2(c.y - sc.y, c.x - sc.x))
            if s.get("front_deg") is not None and \
                    G.angle_difference_deg(float(s["front_deg"]), to_table) > RING_FACING_DEG + 1e-9:
                continue
            seats.append((math.degrees(math.atan2(sc.y - c.y, sc.x - c.x)) % 360.0, str(s["id"])))
        if len(seats) < RING_SEATS_MIN:
            continue
        bearings = sorted(b for b, _sid in seats)
        gaps = [(bearings[(i + 1) % len(bearings)] - bearings[i]) % 360.0 for i in range(len(bearings))]
        if max(gaps) >= RING_OPEN_DEG - 1e-9:
            continue
        crop = _crop_of(f)
        ids = sorted(sid for _b, sid in seats)
        r = float((f.get("circle_fit") or {}).get("radius") or max(float(v) for v in f["footprint"]["size"]) / 2.0)
        text = (f"table_coffee: a drawn round {f['type']} ({f.get('type_method')}) {2 * r:.2f} m across with "
                f"{len(ids)} seats around it ({', '.join(ids)}) facing it: the table of the seating group, not a "
                f"{f['type'].replace('_', ' ')}" + (f" (plan crop {crop})" if crop else ""))
        ev = _evidence_code(f, RING_TABLE_METHOD, text, CONF_RING, seats=ids, drawn_type=f["type"])
        ev["rule"] = RING_TABLE_RULE
        if crop:
            ev["crop"] = crop
        out.append({"piece_id": f["id"], "type": "table_coffee", "type_method": RING_TABLE_METHOD, "reason": text,
                    "confidence": CONF_RING, "evidence": ev, "drawn_type": f["type"], "crop": crop})
    return out


CHAISE_RULE = "furniture.infer.chaise_sides"
CONF_CHAISE = 0.6


def chaise_sides(building: dict) -> list[dict]:
    """Fix round after P4b (module docstring): ``{"piece_id", "chaise_side", "chaise_depth", "reason", "evidence"}``
    for every built drawn ``sofa_corner`` without the drawing's L (no ``shape``, no ``chaise_side``) whose footprint
    box a drawn coffee table of its room reaches into, when the chaise on one side (``schemas.l_parts`` with the
    default seat depth and chaise width, in the piece's front frame) covers the table and the chaise on the other
    side leaves it free: that other side. Pure; the building is unchanged."""
    import dataclasses

    furniture = building.get("furniture") or []
    out: list[dict] = []
    for f in furniture:
        if f.get("type") != "sofa_corner" or f.get("source") != "from_documents" or f.get("build") is False:
            continue
        if f.get("shape") or f.get("chaise_side") or not f.get("footprint"):
            continue                                    # the drawing's L (reading.context_types) decides
        try:
            p = placer.drawn_piece(f)
        except (KeyError, TypeError, ValueError):
            continue
        box = p.polygon()
        tables = []
        for t in furniture:
            if t.get("room_id") != f.get("room_id") or t.get("type") != "table_coffee" or not t.get("footprint") \
                    or t.get("source") != "from_documents" or t.get("build") is False:
                continue
            try:
                tp = placer.drawn_piece(t).polygon()
            except (KeyError, TypeError, ValueError):
                continue
            if tp.intersection(box).area > placer.AREA_EPS:
                tables.append((str(t["id"]), tp))
        if not tables:
            continue
        cover = {}
        for side in ("right", "left"):
            lp = dataclasses.replace(p, shape="L", chaise_side=side, chaise_depth=p.size[1], seat_depth=None,
                                     chaise_width=None).polygon()
            cover[side] = sum(lp.intersection(tp).area for _tid, tp in tables)
        free = [side for side in ("right", "left") if cover[side] <= placer.AREA_EPS]
        if len(free) != 1:
            continue                                    # both sides free or both cover it: the documents decide
        side = free[0]
        other = "left" if side == "right" else "right"
        ids = ", ".join(tid for tid, _tp in tables)
        text = (f"chaise on the {side}: the drawing gives no L outline for {f['id']}, and a chaise on the {other} "
                f"would cover {cover[other]:.2f} m² of the drawn coffee table {ids}, which stands in the sofa's open "
                f"corner with the chaise on the {side}")
        ev = _evidence_code(f, "chaise_side", text, CONF_CHAISE, tables=[tid for tid, _tp in tables])
        ev["rule"] = CHAISE_RULE
        out.append({"piece_id": f["id"], "chaise_side": side, "chaise_depth": round(float(p.size[1]), 4),
                    "reason": text, "evidence": ev})
    return out


def apply_chaise_sides(building: dict, proposals: list[dict]) -> None:
    """Fix round after P4b: write ``chaise_sides`` proposals in place: ``shape: L``, ``chaise_side``, ``chaise_depth``
    (the footprint depth; seat depth and chaise width stay the schema defaults), ``inferred: true`` and the evidence
    (CLAUDE.md: where the documents are silent the AI infers and marks it ``inferred``)."""
    by_id = {f["id"]: f for f in building.get("furniture") or []}
    for prop in proposals:
        item = by_id.get(prop["piece_id"])
        if item is None or item.get("shape") or item.get("chaise_side"):
            continue
        item["shape"] = "L"
        item["chaise_side"] = prop["chaise_side"]
        item["chaise_depth"] = prop["chaise_depth"]
        item["inferred"] = True
        item.setdefault("evidence", []).append(dict(prop["evidence"]))


def _room_ring(room: dict):
    """The room outline as a shapely ring (CCW)."""
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient

    poly = orient(Polygon(room["polygon"]), 1.0)
    return (poly if poly.is_valid else poly.buffer(0)).exterior


def duplicate_symbols(building: dict) -> list[dict]:
    """Fix round after P6a (module docstring): proposals ``{"piece_id", "type", "type_method":
    DUPLICATE_SYMBOL_METHOD, "build": False, "reason", "confidence", "evidence", "kept_id", "share", "crop"}`` for the
    built drawn pieces of a ``DUPLICATE_SYMBOL_TYPES`` type that lie at least ``DUPLICATE_SYMBOL_SHARE`` (of their own
    footprint, the smaller one) inside a larger built drawn piece of the same type and room (largest first, ties by
    id; a piece left out keeps no other piece out). Pure; the building is unchanged. Fix round after P6a (23 Oct 2026),
    review: a piece without its plan crop (``_crop_of``: a block-named symbol had no question) is never proposed, so
    no drawn piece is left out without the crop as evidence (CLAUDE.md)."""
    furniture = building.get("furniture") or []
    groups: dict = {}
    for f in furniture:
        if f.get("type") not in DUPLICATE_SYMBOL_TYPES or f.get("source") != "from_documents" \
                or f.get("build") is False or not f.get("footprint") or not f.get("room_id"):
            continue
        try:
            poly = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if poly.area > 0:
            groups.setdefault((f["room_id"], f["type"]), []).append((f, poly))
    out: list[dict] = []
    for (_room, ftype), items in sorted(groups.items()):
        items.sort(key=lambda fp: (-round(fp[1].area, 6), str(fp[0]["id"])))
        dropped: set = set()
        for i, (keep, kp) in enumerate(items):
            if keep["id"] in dropped:
                continue
            for other, op in items[i + 1:]:
                if other["id"] in dropped:
                    continue
                share = op.intersection(kp).area / op.area
                if share < DUPLICATE_SYMBOL_SHARE - 1e-9:
                    continue
                crop = _crop_of(other)
                if not crop:
                    continue                    # fix round after P6a, review: no removal without the plan crop
                dropped.add(other["id"])
                w, d = (float(v) for v in other["footprint"]["size"])
                kw, kd = (float(v) for v in keep["footprint"]["size"])
                text = (f"{ftype} {other['id']} ({w:.2f} x {d:.2f} m) is drawn {share:.0%} inside the larger "
                        f"{ftype} {keep['id']} ({kw:.2f} x {kd:.2f} m) of its room: one {ftype.replace('_', ' ')} "
                        f"drawn twice, not two (two {ftype.replace('_', ' ')}s never stand in each other); "
                        f"{keep['id']} stays, {other['id']} is not built" + (f" (plan crop {crop})" if crop else ""))
                ev = _evidence_code(other, DUPLICATE_SYMBOL_METHOD, text, CONF_DUPLICATE, kept=keep["id"],
                                    share=round(share, 3))
                ev["rule"] = DUPLICATE_SYMBOL_RULE
                if crop:
                    ev["crop"] = crop
                out.append({"piece_id": other["id"], "type": ftype, "type_method": DUPLICATE_SYMBOL_METHOD,
                            "build": False, "reason": text, "confidence": CONF_DUPLICATE, "evidence": ev,
                            "kept_id": keep["id"], "share": round(share, 3), "crop": crop})
    return out


def _apply_duplicate(item: dict, prop: dict) -> None:
    """A duplicate symbol (``duplicate_symbols``): not built, explained (``inferred_as: detail``), labelled
    ``adjusted_by_ai`` by code with the drawn values kept and the plan crop as evidence (CLAUDE.md: a drawn piece is
    removed only with its plan crop; every change keeps ``drawn_*`` and names its reason)."""
    item.setdefault("drawn_type", item.get("type"))
    item.setdefault("drawn_footprint", copy.deepcopy(item.get("footprint")))
    item.setdefault("drawn_front_deg", item.get("front_deg"))
    item.setdefault("drawn_height", item.get("height"))
    label = {"by": "code", "stage": "reading", "rule": DUPLICATE_SYMBOL_RULE, "reason": prop["reason"],
             "changed": {"build": True}, "not_furniture": "duplicate_symbol", "duplicate_of": prop["kept_id"]}
    if prop.get("crop"):
        label["crop"] = prop["crop"]
    merge_code_label(item, label)
    item.update(build=False, inferred=True, inferred_as=DETAIL_TYPE, inferred_reason=prop["reason"],
                not_built_reason=prop["reason"])
    item.setdefault("evidence", []).append(dict(prop["evidence"]))


def set_front(item: dict, front_deg: float) -> None:
    """Give a piece a front: the footprint turned by whole quarter turns so its local -Y faces ``front_deg``
    (``placer.front_frame``: same rectangle, size swapped on an odd turn)."""
    rot, size = placer.front_frame(item["footprint"], front_deg)
    item["footprint"] = dict(item["footprint"], rotation_deg=round(rot, 3), size=[round(size[0], 4),
                                                                                   round(size[1], 4)])
    item["front_deg"] = round(G.normalise_angle(front_deg), 3)


def apply_inferences(building: dict, proposals: list[dict]) -> dict:
    """A copy of the building with the proposals applied (``inferred: true``, evidence method ``inferred``)."""
    b = copy.deepcopy(building)
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    for prop in proposals:
        item = by_id.get(prop["piece_id"])
        if item is None:
            continue
        if prop.get("type_method") in CODE_TYPE_METHODS:          # Milestone 13: typed by code
            _apply_code_type(item, prop, proposal=False)
            continue
        if prop.get("type_method") == NIGHTSTAND_METHOD:          # fix round after P4a: a nightstand symbol
            _apply_nightstand(item, prop)
            continue
        if prop.get("type_method") == NAME_RETYPE_METHOD:        # 26 Oct 2026: the name text written on it
            _apply_nightstand(item, dict(prop, type_method=NAME_TEXT_METHOD))
            continue
        if prop.get("type_method") == AI_MEMBER_METHOD:          # 26 Oct 2026: the missing member the AI named
            _apply_ai_member(item, prop)
            continue
        if prop.get("type_method") in (CORNER_TABLE_METHOD, RING_TABLE_METHOD):   # a seating group's drawn table
            _apply_nightstand(item, prop)
            item["type_method"] = "inferred"                      # a schema value; the label names the rule
            continue
        if prop.get("type_method") == DUPLICATE_SYMBOL_METHOD:    # fix round after P6a: one symbol drawn twice
            _apply_duplicate(item, prop)
            continue
        ev = dict(prop.get("evidence") or _evidence(item, prop["reason"], float(prop.get("confidence", 0.5))))
        item.setdefault("evidence", []).append(ev)
        item["inferred"] = True
        item["inferred_reason"] = prop["reason"]
        if prop.get("build") is False or prop["type"] not in schemas.SIZE_OPTIONS:
            item["build"] = False
            item["inferred_as"] = prop["type"]
            continue
        item["type"] = prop["type"]
        if prop.get("front_deg") is not None and item.get("front_deg") is None:
            set_front(item, float(prop["front_deg"]))
    return b
