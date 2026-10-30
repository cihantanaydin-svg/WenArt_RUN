"""Fit a catalogue asset (or the parametric fallback) to every furniture piece.

Rule (docs/milestone4.md, conventions, plan section 4.8): among the catalogue
entries of the piece's type, try the candidates in order of aspect
closeness (``|ln(asset width/depth / footprint width/depth)|``); scale X and
Y to the footprint, Z by the mean of the two; a non-uniform scale
(``max(sx, sy, sz) / min(sx, sy, sz)``) above 15 % rejects the candidate;
no candidate within the cap, or no entry for the type, means the parametric
fallback (exact footprint, type height). Every decision is written into the
piece's ``asset`` dict so ``fit_report`` can list it; nothing else of the
piece changes (``footprint``, ``front_deg``, ``room_id``, ``type``,
``status``, ``evidence`` are untouched, checked by ``fit_building``).

``asset`` dict::

    {"library": "polyhaven" | "parametric", "asset_id": "sofa_02" | "parametric:sofa",
     "licence": "CC0" | "n/a", "license": <same>, "method": "library" | "parametric",
     "fit_scale": [sx, sy, sz], "bbox_m": [w, d, h] of the fitted piece, "aspect_error": float | null,
     "gltf": "models/<id>/<id>_1k.gltf" (library only), "front_axis", "up_axis", "origin_offset",
     "rotation_fix_deg" (library only), "candidates": [{"id", "aspect_error", "scale", "non_uniform", "accepted"}],
     "fallback_reason": str (parametric only), "cap": 1.15}

``license`` duplicates ``licence`` because the building schema names the
field ``license`` and the milestone text ``licence``.

CLI: ``python -m wenart.furniture.fit outputs/<p>/building.json --catalog wenart/furniture/catalog.json
--out outputs/<p>/building_fitted.json --assets assets`` downloads the fitted
models into ``assets/models`` (a failed download turns that fit into the
parametric fallback and the report says so).

Milestone 7 (docs/milestone7.md §6.3, user decision 7):

- Beds: a bed model without a mattress (``has_mattress`` not true) is never
  a candidate (reason ``no <type> model with a mattress`` when none is left).
- Style filter: ``fit_piece(..., style_family=F)`` takes only candidates
  whose ``styles`` contain ``F`` or ``neutral`` (every candidate when ``F``
  is None); none left -> parametric with the reason ``no model for style F``.
  Excluded candidates are listed under ``excluded`` with the reason. Only
  ``refit`` gets ``--style <out>/style.json`` (it runs after the final
  style); ``fit`` stays style-free, so its fits are provisional (layout and
  decor only read the footprints).
- Objaverse models (``source: objaverse``, CC0 or CC BY 4.0) are fitted like
  the Poly Haven ones; the asset dict carries ``glb``, ``sha256_glb``,
  ``uid`` and the credit fields (``title``, ``author``, ``source_url``,
  ``licence_url``, ``via``, ``attribution``) and ``unit_scale`` (raw GLB
  units -> metres, 1.0 when the entry has none; the scene builder applies
  it before ``fit_scale``); the report lists every CC BY credit line. Downloading an Objaverse model reads only the prep pod's
  cache (``wenart.assets.models.fetch_model``); a miss is a parametric
  fallback like any failed download.

Milestone 8 (docs/milestone8.md §1, §4): fit v2.

- Sources ``abo``, ``polyhaven``, ``objaverse``, ``generated``. After the
  style filter and the bed rule the candidates are tried in **rank order**
  (``rank_key``), the first one within the caps (non-uniform <= 15 %, mean
  scale in ``UNIFORM_RANGE``) wins:
  0. ``generated`` models last (used only when no other library model passes);
  1. real size: models whose box is in real metres (``units_known``: ABO and
     Poly Haven; Objaverse unless a ``unit_note`` says it was normalised by
     type; generated never) before the normalised ones, and among them the
     smallest mean ``|scale - 1|`` over the three fit scales, in
     ``SIZE_BUCKET`` (5 %) steps so that the judge quality decides between
     models whose real size fits about equally well;
  2. judge ``quality`` (mean photoreal quality 1-5, higher first; missing = 3);
  3. aspect error; 4. source order ``SOURCE_ORDER``; 5. the id.
  Every tried candidate records its rank inputs (``size_error``,
  ``size_bucket``, ``units_known``, ``quality``, ``source``, ``rank``) and
  the asset ``ranking`` says why the chosen model won; the report lists it.
- Beds: a bed model without a mattress is a candidate when it is a bed frame
  (``bed_frame: true`` with a positive ``deck_height_m``, metres in the Z-up
  model frame above the model's lowest point, after its unit scale); the
  asset carries ``bed_frame``, ``deck_height_m`` and ``bedding`` (mattress
  top = ``deck_height_m`` x the z fit scale + 0.20 m, the inner box) and
  ``bbox_m`` covers the bedding the scene builder adds
  (``wenart.blender.parametric.frame_bedding``).
- Library models from a GLB (every source but Poly Haven) carry ``glb``,
  ``sha256_glb``, ``uid``, the credit fields, ``unit_scale`` and the
  catalogue's ``licence_flag`` / ``generated`` record.
- Decor (``fit_decor_item``): cushion, plant, rug and wall art take a library
  decor model of the project's style family or ``neutral`` (a decor model
  without ``styles`` counts as neutral) from ``catalog.decor_candidates(type)``
  when the catalogue has the method (duck typing; else the ``kind: decor``
  entries of ``catalog.decor`` / ``catalog.entries``, plus the Poly Haven
  ``decor_plant`` models for plants), picked deterministically by the host id
  (``pick_index``); rugs are scaled to the rug size and kept flat, wall art
  to its width keeping the model's aspect, cushions and plants to the item
  box (refused above ``DECOR_NON_UNIFORM_CAP``). No model -> parametric
  (cushion, plant, book set, rug) or nothing (wall art).

Milestone 10 (docs/milestone10.md §4.5, §4.6, §1.6b rows 15, 16; track F):

- The piece's look (``furniture.design``, written by the layout stage, else ``style.json`` through
  ``wenart.blender.looks.design_for``; only with ``--style``) decides between the library models after the style
  filter: ``material_tags`` ("glass coffee table") keep only models whose judged ``material_tags`` hold every
  asked tag; an upholstered piece's ``fabric_colour`` (a non-upholstered piece's ``colour``) keeps models that can
  take it: ``recolourable_fabric`` models (their separable fabric slots get the colour: ``asset.recolour``, applied
  by the scene builder) or models whose judged fabric slots are already that colour (``colour_rgb`` within
  ``COLOUR_MATCH_DE`` in CIELAB, ``asset.colour_match``); models without the judged fields are skipped for such a
  brief (§4.5: "the fit picks another"), and with none left the parametric piece takes the look. The furniture
  wood (``design.wood``) is recoloured on ``recolourable_wood`` models and preferred, never a reason to skip one.
  Every skipped model is listed under ``excluded`` with the reason.
- The judged fields (``material_slots``, ``material_tags``, ``recolourable_fabric``, ``recolourable_wood``) and a
  plant's ``species`` and ``pot`` travel with the asset (``GLB_ASSET_FIELDS``).
- Decor: the 12 new types take library models like the Milestone 9 ones (tabletop pieces within their box, a clock
  like wall art, curtains, blinds, throws and large plants scaled to their box); a large plant prefers models of
  its ``species``.
- Refit: ``--source building.json [--completion completion.json]`` runs ``wenart.furniture.locked.check`` (mode
  and kept rooms from ``completion.json``) on the fitted building and exits 1 on a violation (the report lists
  them, the fitted building is not written).

Milestone 13 (docs/milestone13.md §3.0 K1, K2, K7, §12 D1, D3, D4, D5, §13.2, §13.3; track T1):

- What: (1) a licence mode: ``fit_piece(..., mode="commercial")`` and ``fit_building(..., mode=None)`` (None =
  ``project.licence_mode`` of the building, else ``catalog.licence_mode(brief)``: env ``WENART_LICENCE_MODE`` > brief
  ``library.licence_mode`` > ``commercial``); the fit writes ``project.licence_mode`` (and where it came from) and
  every asset carries ``licence``, ``licence_flag``, ``commercial_safe``, ``licence_mode``. (2) The ranking without
  the wood re-sort: real size (uniform scale to the drawn width), real product, known units, the design as a
  preference (material tags, fabric colour: models that show it first, the others still tried, ``design_not_shown``
  when one wins), the audit's vision quality, the texture maps, the judges' quality, the face count (tie-breaks, never
  gates: decision 1a of 11 Oct 2026), aspect error, source, id; a diversity penalty per room and per project
  (``ROOM_REUSE_MAX``, ``ROOM_REUSE_STEPS``, ``PROJECT_REUSE_STEP``: the n-th use of a model costs size steps; a
  matched set, ``SET_TYPES``, is never split within its room). (3)
  Uniform scaling: a model is scaled by the drawn width only (``scale_for``: sx = sy = sz); its depth may differ from
  the drawn depth by ``NON_UNIFORM_CAP`` (10 %; the layout absorbs the difference, ``asset.depth_abs_m``), its mean
  scale lies in ``UNIFORM_RANGE``, its height within 15 % of the real range; no mesh is stretched any more. (4) Pins
  skip the style filter (the agent's choice is the decision; the caps still apply). (5) The fabric colour of the brief
  reaches the asset (``asset.fabric_colour``, from ``design.fabric_colour`` or the style's ``furniture.by_type`` /
  ``furniture.fabric_colour``; B1 of §1.8). (6) The size snap before the fit (``apply_size_snap``,
  ``wenart.furniture.sizes.snap_size``): a drawn furniture size outside its type's product range becomes the nearest
  real product (``piece.size_snap``, ``adjusted_by_ai``, ``drawn_footprint`` kept; the back edge stays where it was
  when the depth changes); off with ``furnished_rooms: keep`` or ``furnished_rooms_keep_size``; fixed equipment is
  not snapped here (the ingest's fixed rule and the agent's ``fix_fixture`` do that). (7) The fallback ladder (D4): a
  piece with no library model within the caps tries, in order, step 1 the nearest audited model (the caps, then the
  relaxed M11 caps ``RELAXED_CAP`` / ``RELAXED_RANGE`` only while the fitted box stays inside the type's documented
  ranges; a related type for a piece its group needs), step 2 a module builder (``wenart.blender.modules.module_plan``,
  track T2; import guarded: absent or None means step 3), step 3 the parametric family (``method: parametric``).
  ``asset.ladder`` logs every step with its result and reason; ``piece.library_gap`` names the step used (``step``);
  ``method: none`` only for a piece that is not built (``build: false``: not furniture, removed). A drawn anchor is
  never left out.
- Why: §1.2-1.3 of the milestone: the wood re-sort put an Objaverse chair of unknown units in front of the real ABO
  chair 82 times; 43 drawn pieces of real04 (20 of 33 drawn anchors) were not built at all; half of the built library
  pieces were stretched by more than 5 %; the brief's fabric colour never arrived.
- How: ``fit_building`` snaps, resolves the mode, keeps the use counters and passes them into ``fit_piece``;
  ``fit_piece`` runs the library search (``_fit_family`` per style family with the preference order), the relaxed
  caps, then ``_no_model`` (related type, module, parametric); every result goes through ``_finish`` (licence
  fields, the ladder). ``fit_report`` lists the mode, the flagged assets, the snaps and the pieces built below the
  library level.
- Build round 2 (15 Oct 2026): ``SOURCE_ORDER`` ranks the HSSD layer (``hssd``, CC BY-NC 4.0, relaxed mode only) after
  Poly Haven and before GSO (real products at real size, declared by the publisher; the licence mode decides whether
  they are candidates at all, ``catalog.usable``). A module plan with a ``split`` (``wenart.blender.modules``: a drawn
  table footprint that includes its chairs, CLAUDE.md "a table footprint that includes its chairs") labels the piece
  ``adjusted_by_ai`` with the reason (``split_label`` on the asset, ``apply_split_label`` on the piece in
  ``fit_building``): the footprint stays as drawn (the modules sit inside it), ``drawn_footprint`` and the other
  ``drawn_*`` keys are kept, and the label names the table and the chairs built in it.
- Build round 3 (lead decision): the split decides BEFORE the size snap. ``fit_building`` asks the module plan first
  (``split_plan_first``: a ``table_dining`` footprint deeper than ``modules.TABLE_DEPTH_MAX_M``, 1.20 m, is a table
  with its chairs); such a piece is labelled ``module_split`` with ``drawn_footprint`` kept and only its table part
  is judged by the snap (``apply_split_then_snap`` -> ``apply_size_snap(part=...)``: the width and the height may
  take a real product, the drawn depth stays because it holds the chairs; ``size_snap.part``; the label keeps
  ``rule: module_split`` with ``rules = [module_split, size_snap]`` and a reason that names the built table and
  chairs, ``split_snap_reason``). Before, the snap ran first and took the drawn 1.8 m depth to a 1.0 m product
  depth, which erased the chairs (``project.size_snap.split_first`` lists the ids). No drawn table of the committed
  real02 / real03 / real04 buildings is deeper than 1.20 m (real04's 10-seat tables are drawn 3.35 x 1.00 m with
  their ten chairs as separate pieces), so their fit does not change. Review of round 3: a piece split first is
  built by its module plan even when a library table would fit the full footprint (``split_module_fit``: the split
  decides, the library pick is logged as ``split_over``); a footprint drawn with its long side as the depth is not
  split first (``plan_table_long`` has no orientation check); ``assert_only_assets_changed`` accepts the snap of a
  split table's part (the width only).
- Fix round after P3 (16-17 Oct 2026), kitchen runs. What: ``kitchen_built_ins`` (pure, before the per-piece fit)
  finds, per built kitchen counter or island, the built drawn sinks and stoves of its level and room with at least
  ``BUILT_IN_SHARE`` of their footprint inside it (``modules.member_in_run``). The largest sink is built into the run:
  the run's plan gets ``sink_pos_m`` / ``sink_w_m`` / ``sink_piece`` (a sink unit with the bowl and tap at its
  cutout, ``plan["built_ins"]``) and the sink's asset says ``built_in: <run id>`` (``method: module``, the run's
  ``asset_id``, by design; build, type and evidence unchanged, so the group checks and the metrics still see a
  sink); the scene does not build it again (``furniture.built_in_ids``). Each stove becomes a gap of the run
  (``ranges``: no base unit, plinth or worktop at its drawn span); the stove keeps its own model. Why: pod P3 built
  every drawn sink and stove inside full-depth base units under an uncut worktop (only a tap and a stove front
  showed). How: the hints reach the plan on a copy of the run (``dict(piece, module_hints=...)``) and are stored as
  ``asset.module_hints`` beside ``asset.module_plan``: the building piece itself never gets ``module_hints``, so
  ``FROZEN_KEYS`` and ``assert_only_assets_changed`` hold. A sink is made a built-in only when the run's plan holds
  it; otherwise it is fitted as before. A pinned sink (``asset_pin``, the agent's model) is never a built-in.
- Fix round after P3, part 2 (17 Oct 2026), kitchen runs. What: a pinned sink inside a run gets a gap of the run
  (``ranges`` entry ``type: sink_kitchen`` with its reason; it keeps its pinned model and stands as drawn); a sink the
  run's plan does not build in because its sink unit would stand more than ``modules.KITCHEN_END_SHIFT_MAX_M`` from
  the drawn centre gets a gap from the plan itself (``modules.plan_kitchen_run``); a built-in records the unit's
  ``shift_m`` from the drawn centre, which the sink's asset reason and the fit report's "Kitchen runs" section name.
  Why: a pinned sink inside a run was neither built in nor given a gap, so it stood buried in full-depth base units
  under an uncut worktop again (the P3 defect; only S2 reported it, and no agent tool clears that); a drawn sink
  overhanging the run's end was built in up to 0.4 of its width from where it is drawn, with no record (the CLAUDE.md
  fixed-equipment rule: as drawn). How: the gap goes through the run's hints like a stove's; nothing on the piece
  changes (``assert_only_assets_changed``).
- Fix round after P3, part 3 (17 Oct 2026), kitchen runs. What: the run's plan measures the drawn sink across the run
  too (``modules.plan_kitchen_run``: the bowl stands on the run's centreline; its centre within
  ``modules.KITCHEN_END_SHIFT_MAX_M`` of the drawn centre, both axes together, else no built-in and a gap at its
  drawn span with the reason); a built-in records ``shift_y_m`` (the bowl's y minus the drawn y) beside ``shift_m``,
  which the sink's asset (``module_plan.shift_y_m`` and its reason) and the fit report's "Kitchen runs" line name.
  Why: part 2 read only the position along the run, so a drawn sink overhanging the counter's front was built in on
  the run's centreline, up to about 0.25 m from where it is drawn, with no record. How: ``kitchen_built_ins`` already
  gives the sink's world centre (``sink_pos_m``); nothing on the piece changes.
- Fix round after P4a (17 Oct 2026; the library verifier's better_fix, applied at integration). What: (1) the audit's
  vision quality tie-break reads the quality the audit wrote into ``audit.vision_doubt`` ("vision quality 2 (<= 2)")
  when no numeric field is there (``vision_quality_of``); a "not a <type>" doubt is not read (the dining tables it
  names are real dining tables). (2) A pin (the agent's ``swap_model``) to a generated model (``source:
  generated``, units guessed) is refused while the normal ranking fits a real product of the type within the caps:
  the "generated last" rule applied to pins (``pin_refused`` names both). Why: (1) ``assets/audit/write.py`` writes
  only the doubt strings, so 0 of 2028 models had a numeric quality and doubtful models won exact ties (P4a: the
  wardrobe f_L-1_023 took ``hssd_7094e304``, the fridge f_L-1_096 ``hssd_78a02cbe``, each tied with doubt-free
  models); (2) P4a's agent pinned ``gen_fridge_mediterranean_3`` on f_L-1_090 ("a real compact fridge model") and it
  rendered as a faceted column, while the fit had a real fridge for the same footprint. Still no gate: a model alone
  within the caps is taken whatever its doubt (decision 1a of 11 Oct).
- Fix round after P6a (22-23 Oct 2026; pod P6a, real04; the agent verifier's better fix, part 2). What: under a
  sloped ceiling a library model stays ``CEILING_MARGIN_M`` (0.05 m, ``solver.HEADROOM_MARGIN_M``) under the ceiling
  over its footprint. ``fit_piece(..., ceiling=)`` / ``_fit_family`` refuse a model whose fitted height is above
  ``ceiling - CEILING_MARGIN_M`` like a model outside the real height range (the next one is tried; with none left
  the ladder builds the module or parametric piece at the piece's height); ``piece_ceiling(building, piece)`` is that
  ceiling: the lowest sloped ceiling over the footprint (``ceiling_planes_of``: the roof as the scene builder makes it,
  the rule of ``decor.ceiling_planes`` / ``decor.ceiling_over``, which the fit stage does not import; the layout and
  fit buildings carry no ``level["ceiling_planes"]``) less a wall cabinet's mount height, None on a flat level. ``fit_building`` passes it per piece; the agent's refits (``edit_ops._build_retyped``, the swap check
  and ``agent.loop.dry_fit``) pass the same. Why: the completion put the twin bookshelf f_L1_056 under a 1.44 m
  slope and the fit gave it a 2.02 m HSSD model (critical X2, through the roof, in every P6a round); real02's committed
  f_L1_035 has a 2.02 m model under a 2.07 m slope. On a flat level (no roof over it) nothing changes.
- Fix round after P6b (23 Oct 2026; pod P6b, real03; the library-data track's ask). What: ``fit_report``'s
  "Attribution (CC BY 4.0)" lines decode complete HTML entities (``credit_text``: ``&amp;`` -> ``&``, the rule of
  ``wenart.run.copy.plain_text``); the fitted asset and the catalogue keep their text. Why: P6b's real03
  building_fitted_report.md and building_final_report.md listed "... Knobs &amp; Faucet", "Hudson Reed Sublime Vanity
  Unit &amp; Basin" and "Cooke &amp; Lewis Deluvio ..." (HSSD titles stored HTML-escaped), while ATTRIBUTION.md
  already names the products as they are called.
- Fix round of 26 Oct 2026 (user: "fix should be general"; "there is no taste in the furniture selection"). What:
  (D) one model per role of a group: the members of one group (``group.group_id``) with the same ``ROLE_SET_TYPES``
  type (the chairs of a table, the nightstands of a bed, the armchairs of a seating group) are a role set
  (``role_sets``); the set's model is fitted once on the members' median drawn size (``median_size``) and used for
  every member within the caps on its own drawn size (``asset.role_set`` with ``used: true``); a member it does not
  fit is fitted on its own (``used: false`` and why); pinned pieces and the anchor are no members. (E) Taste rank
  rules, never gates: a misfit (``misfit_of``: folding, camping, an outdoor piece in a known indoor room, a bar or
  counter stool as a chair) ranks after every other model; a dining-group model (``STYLE_MIX_TYPES``) whose styles or
  title name a style outside the project family's compatible styles (``compatible_styles``, ``style_mix_of``) takes
  ``STYLE_MIX_STEPS`` size steps; a winner that still has either records ``taste_flags``. Why: real06's living room
  had a folding chair, Eames chairs and a turned-leg "Traditional ... Rustic" table at one Scandinavian dining group,
  and its four drawn chairs (0.37-0.54 m wide) took two different models.
- Kitchen design of 28 Oct 2026 (user on real04: "Kitchen design could have been a lot better this is terrible"; on
  real06: "What kind of a kitchen is this"; tests/test_kitchen_design_20261028.py). What: ``kitchen_built_ins`` makes a
  drawn stove in a run the run's hob (``hob_hints``: its drawn span, an oven in a full-depth run, the hood's kind and
  top under the ceiling), keeps a hob or fridge the completion built in inside its run whatever the agent pinned
  (``pins_not_used``; ``edit_ops`` refuses such a swap), claims a counter outline drawn inside a run
  (``nested_counters``: no second run), and says a fridge column never stands in front of a window or a
  pass-through (``openings_behind``); ``fit_building`` fits the wall cabinets after their run with its base joints
  (``wall_cabinet_run``, ``wall_run_hints``: the wall run of real units). Why: real04's drawn stove stood in a gap as
  a freestanding cooker under the worktop line; real06's pinned hob and fridge left their runs and its hob outline was
  built as a run inside a run. How: hints on a copy, ``asset.module_hints``; nothing on the pieces changes.
- Bathroom sense of 26 Oct 2026 (user: "fix should be general"; tests/test_bathroom_sense_20261026.py). What: a gate,
  not a rank rule (``use_misfit``, ``use_candidates`` in ``_fit_family``): a model made for another user or use than
  the piece is no candidate, listed under ``excluded`` with ``rule: fit.product_use`` and the reason: a children's
  product (``CHILD_PRODUCT_WORDS`` in its title or name) outside a child's room (``child_room`` on the fitted copy of
  the piece, from the room's ``room_subtype: child``: ``use_context``, set by ``fit_building`` and the agent's refit
  of a retyped piece); a fixture its title names for another room (``OTHER_USE_WORDS``: a washbasin named for a kitchen, a
  laundry, a utility, mop, bar or commercial sink; a kitchen sink named for a bathroom); a washbasin whose main
  material slot (``OTHER_USE_SHARE``) is named composite or granite (kitchen and utility sinks; a bathroom basin is
  glazed ceramic, as the audit's ``sanitary_finish`` says of a metal one). With none left the ladder builds the module
  or parametric piece. Why: real06's adult bathrooms got the HSSD "TODDLER SINK" (an orange child's vanity) and
  "Combo CEG-50BF" (a black composite utility basin); the catalogue keeps them (a child's room may take the toddler
  sink), the fit no longer chooses them for an adult bathroom.
- Kitchen completion of 26 Oct 2026 (user: "fix should be general"). What: ``kitchen_built_ins`` also takes the hob
  and the under-counter fridge the completion built into a counter (``built_in_module``: ``built_into`` names the
  run, ``built_in.kind`` hob | fridge) as the run's hints (``hob_pos_m`` / ``hob_w_m`` / ``hob_piece`` / ``oven``,
  ``fridge_pos_m`` / ``fridge_w_m`` / ``fridge_piece``; never as a stove's gap) and maps them in ``sinks`` (every
  built-in piece, deferred after its run); ``built_in_fit`` gives them the built-in asset of their kind. Why: real06's
  kitchen rendered "a bare base cabinet with an empty worktop": the hob must show on the worktop with its oven.
- Room rules and the lamp with its host, 30 Oct 2026 (user on real04 run 20261030-043021-full: "I did not like this
  lamp table combo", UL156; "I did not like these sofas here maybe used in another project but not here", UL161;
  tests/test_lamp_side_table_20261030.py). What: two more gates of ``use_candidates`` with the room's type on the fitted
  copy (``room_use_context``): a side table, nightstand or coffee table whose title names an office, swivel, star or
  rolling base is no candidate outside a study (``base_misfit``, ``rule: fit.stable_base``); a daybed is no sofa of a
  living-type room unless the piece asks for one in a family that seats a living room on a daybed (``daybed_misfit``,
  ``rule: fit.daybed_room``); the agent's pin and swap are refused with the rule (``room_rule_refusal``). A table lamp
  is fitted with its host (``fit_decor_item(host=...)``): its shade at most ``LAMP_SHADE_TOP_RATIO`` of the top's
  smaller side (``LIGHT_BASE_SHADE_RATIO`` on a light base), beside a seat or a bed ``LAMP_HEIGHT_RATIO`` of the host's
  height, never shrunk below ``LAMP_MIN_SCALE``; no novelty lamp and no work light beside a seat or a bed while
  another fits (``lamp_misfit``); ``asset.pairing`` records the limits and what held. Why: the open-kitchen variant's
  sofa side had a Nelson swivel 4-star end table under a big two-tone drum lamp, the bedrooms a 0.92 m lamp shrunk to
  63 %, and the play-and-rest room two HEMNES daybed frames as its sofas; the catalogue keeps every model.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Optional

from wenart.furniture import catalog as C

# Milestone 12 (docs/milestone12.md §4.8 D14): real proportions: a model is stretched by at most 10 % between its
# axes (was 15 %) and scaled by 0.85-1.20 on average (was 0.75-1.30); outside -> the next model.
# Milestone 13 (K2): the model is scaled uniformly by the drawn width; NON_UNIFORM_CAP is now the depth mismatch the
# layout absorbs (fitted depth / drawn depth, either way), UNIFORM_RANGE the range of that one scale.
NON_UNIFORM_CAP = 1.10
PARAMETRIC_LIBRARY = "parametric"
PARAMETRIC_LICENCE = "n/a"
# Milestone 13 (D4, ladder step 1b): the Milestone 11 caps, accepted only while the fitted box stays inside the type's
# documented ranges (wenart.furniture.sizes), so a near miss of the M12 caps is a real product and not a gap.
RELAXED_CAP = 1.15
RELAXED_RANGE = (0.75, 1.30)
# Milestone 13 (K2): the diversity penalty, in SIZE_BUCKET steps of the rank (a penalty, never a gate: the model is
# still taken when nothing else fits).
ROOM_REUSE_MAX = 2               # a model may be used this often in a room before the room penalty
ROOM_REUSE_STEPS = 4             # ... then it ranks as if its real-size error were 4 steps (20 %) larger
PROJECT_REUSE_STEP = 1           # every earlier use in another room of the project adds one step (5 %)
# Types a room holds as a matched set (the dining chairs round one table, the two nightstands of a bed, the stools
# at a counter): the room penalty does not split a set; the project penalty (other rooms) still varies the sets.
SET_TYPES: tuple[str, ...] = ("chair", "bar_stool", "office_chair", "nightstand", "side_table")
# Milestone 13 (K2): tie-breaks after the audit's vision quality (never gates, decision 1a of 11 Oct 2026).
FACES_LOW = 3000                 # below: low-poly (the audit's own threshold)
VISION_QUALITY_DEFAULT = 3.0     # an entry without an audited vision quality ranks as "plain" (the audit's 3)
MODULE_METHOD = "module"
METHODS: tuple[str, ...] = ("library", MODULE_METHOD, "parametric", "none")
LADDER_STEPS: tuple[str, ...] = ("library", MODULE_METHOD, "parametric")
FROZEN_KEYS = ("id", "level_id", "room_id", "type", "type_raw", "source", "footprint", "front_deg", "height",
               "status", "evidence", "build")
# The fields an Objaverse fit carries over from its catalogue entry (the file and the credit line).
OBJAVERSE_ASSET_FIELDS = ("glb", "sha256_glb", "uid", "title", "author", "source_url", "licence_url", "via",
                          "attribution")
# Milestone 8: what any GLB model (ABO, Objaverse, generated) carries over when its entry has it.
GLB_ASSET_FIELDS = OBJAVERSE_ASSET_FIELDS + ("licence_flag", "generated", "style_hint", "name",
                                             # 30 Oct 2026 (UL215, UL216): the audit's logo and open-part flags
                                             "logo_flag", "logo_reason", "open_parts",
                                             # Milestone 10 (track D's judged fields, docs/milestone10.md §4.5, §4.6)
                                             "material_slots", "material_tags", "recolourable_fabric",
                                             "recolourable_wood", "species", "pot",
                                             # Milestone 10 review (track D): the corner sofa's chaise side as the
                                             # viewer facing the front sees it, and a generated plant's attributes
                                             "chaise_side", "chaise_note", "attributes_status")
# Milestone 10: a judged fabric slot whose colour is within this CIELAB distance (Delta E 1976) of the brief's colour
# counts as that colour (designer value, assumed; about the difference between two named greys).
COLOUR_MATCH_DE = 15.0
RECOLOUR_MIN_SHARE = 0.05        # recolour only separable slots covering at least this share of the model
UPHOLSTERED_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "bed_single",
                                      "bed_double")

# Fit v2 ranking (docs/milestone8.md §1); Milestone 13 (K2): the design preference, the audit's vision quality, the
# texture maps, the face count and the diversity penalty join it; the wood re-sort is gone.
# gso: M12 pod P4 scans; hssd: M13 pod P2 (docs/milestone13.md §12 D2; CC BY-NC 4.0, candidates in relaxed mode only)
# 3dwh (23 Oct 2026): the 3D Warehouse models of the user's zip (uploads of mixed quality, fixed by
# wenart/assets/warehouse.py) rank after the curated sources and before Objaverse.
SOURCE_ORDER: tuple[str, ...] = ("abo", "polyhaven", "hssd", "gso", "3dwh", "objaverse", "generated")
GENERATED = "generated"
DEFAULT_QUALITY = 3.0
SIZE_BUCKET = 0.05           # real-size error steps: models within the same 5 % step are ranked by quality
RANKING_RULE = ("style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| of the "
                f"uniform scale to the drawn width in {round(SIZE_BUCKET * 100)} % steps, plus the diversity penalty: "
                f"{PROJECT_REUSE_STEP} step per earlier use in another room of the project, {ROOM_REUSE_STEPS} steps "
                f"from the {ROOM_REUSE_MAX + 1}. use in a room except for a matched set of "
                f"{', '.join(SET_TYPES)}; an upholstered model adds its quality grade's steps: 2 per point of a fair "
                f"one, 8 for a poor one, soft_seats.grade) -> real product -> design shown (tags, fabric colour) -> "
                f"no other audit "
                f"vision doubt (type, objects, real product) -> audit vision quality (missing = "
                f"{VISION_QUALITY_DEFAULT:g}) -> texture maps -> judge quality (missing = "
                f"{DEFAULT_QUALITY:g}) -> faces (< {FACES_LOW} last) -> aspect error -> source "
                f"({', '.join(SOURCE_ORDER)}) -> id")


# --------------------------------------------------------------------------
# Pure fitting
# --------------------------------------------------------------------------

def scale_for(entry: dict, width: float, depth: float) -> tuple[list[float], float]:
    """``([s, s, s], depth_ratio)`` for an entry on a ``width x depth`` footprint (Milestone 13, K2): one uniform
    scale ``s = width / model width`` (the model keeps its proportions), and the mismatch of its scaled depth against
    the drawn depth as a ratio >= 1 (the layout absorbs it up to ``NON_UNIFORM_CAP``)."""
    s = width / entry["bbox_m"][0]
    fitted_depth = entry["bbox_m"][1] * s
    ratio = max(fitted_depth, depth) / min(fitted_depth, depth) if depth > 0 and fitted_depth > 0 else math.inf
    return [round(s, 4)] * 3, round(ratio, 4)


def fitted_depth(entry: dict, width: float) -> float:
    """The depth a model has after the uniform scale to ``width``."""
    return round(entry["bbox_m"][1] * (width / entry["bbox_m"][0]), 4)


def parametric_box(piece: dict) -> list[float]:
    """The box Blender's parametric mesh will occupy: the piece's ``height`` when
    the JSON has one, else the proxy table height (the same rule as the scene
    builder), measured on the built parts when the type has a builder."""
    from wenart.blender import parametric as P   # pure Python (no bpy)

    width, depth = (float(v) for v in piece["footprint"]["size"])
    height, _ = P.proxy_height(piece["type"], piece.get("height"))
    if piece["type"] in P._BUILDERS:
        height = P.parametric_bbox(piece["type"], width, depth, height)[2]   # a headboard rises above the type height
    return [round(width, 4), round(depth, 4), round(height, 4)]


def parametric_fit(piece: dict, reason: str, candidates: Optional[list[dict]] = None,
                   excluded: Optional[list[dict]] = None, style_family: Optional[str] = None) -> dict:
    ftype = piece["type"]
    return {
        "library": PARAMETRIC_LIBRARY, "asset_id": f"parametric:{ftype}", "licence": PARAMETRIC_LICENCE,
        "license": PARAMETRIC_LICENCE, "method": "parametric", "fit_scale": [1.0, 1.0, 1.0],
        "bbox_m": parametric_box(piece), "aspect_error": None,
        "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
        "candidates": candidates or [], "fallback_reason": reason, "cap": NON_UNIFORM_CAP,
        "style_family": style_family, "excluded": list(excluded or []),
    }


def is_bed_frame(entry: dict) -> bool:
    """A bed model without a mattress that the scene builder can make up (docs/milestone8.md §2, §4):
    ``bed_frame: true`` with a positive, finite ``deck_height_m``."""
    deck = entry.get("deck_height_m")
    return (entry.get("type") in C.BED_TYPES and entry.get("bed_frame") is True
            and isinstance(deck, (int, float)) and not isinstance(deck, bool) and math.isfinite(deck) and deck > 0)


def bed_usable(entry: dict) -> bool:
    """The bed rule of fit v2: a model with a mattress (M7) or a bed frame with a deck (M8); other types always."""
    return C.has_mattress(entry) or is_bed_frame(entry)


def units_known(entry: dict) -> bool:
    """True when the entry's box is in real metres (docs/milestone8.md §2): an explicit ``units_known`` wins;
    generated models never are; a ``unit_note`` (a model normalised by type) means unknown; ABO, Poly Haven
    and the other Objaverse models are real metres."""
    if isinstance(entry.get("units_known"), bool):
        return entry["units_known"]
    if entry.get("source") == GENERATED:
        return False
    return not entry.get("unit_note")


def quality_of(entry: dict) -> float:
    """The judges' mean photoreal quality (1-5); ``DEFAULT_QUALITY`` when missing or not a number. Milestone 12
    (B1): the catalogue stores the two judges' answers as a list ``[q1, q2]``: its mean (the old code read only a
    number, so every model ranked at 3.0)."""
    q = entry.get("quality")
    if isinstance(q, (list, tuple)):
        vals = [float(v) for v in q if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)]
        return sum(vals) / len(vals) if vals else DEFAULT_QUALITY
    if isinstance(q, bool) or not isinstance(q, (int, float)) or not math.isfinite(q):
        return DEFAULT_QUALITY
    return float(q)


def source_rank(entry: dict) -> int:
    source = entry.get("source")
    return SOURCE_ORDER.index(source) if source in SOURCE_ORDER else len(SOURCE_ORDER)


def size_error(scales) -> float:
    """Mean ``|scale - 1|`` over the fit scales: 0 when the model's real size is the footprint."""
    return sum(abs(float(s) - 1.0) for s in scales) / len(scales)


VISION_DOUBT_QUALITY = re.compile(r"vision quality (\d)")   # the audit's doubt text (assets/audit/decide.py)
# integration of the fix round after P5: a doubt text that is only the vision quality ("vision quality 2 (<= 2)")
VISION_QUALITY_ONLY = re.compile(r"^vision quality \d( \(<= \d\))?$")


def other_doubt_of(entry: dict) -> int:
    """Integration of the fix round after P5 (the P5 library finding, track D_data's ask): 1 when the audit's
    ``vision_doubt`` holds a doubt other than the vision quality text (not the type, more than one object, not a
    real product, ...), else 0. ``rank_key`` ranks a doubt-free model first within its size step, before the vision
    quality, so a doubtful model no longer wins a tie on a drawn anchor."""
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    doubts = audit.get("vision_doubt")
    texts = doubts if isinstance(doubts, list) else [doubts] if isinstance(doubts, str) else []
    return int(any(str(t).strip() and not VISION_QUALITY_ONLY.match(str(t).strip()) for t in texts))


def vision_quality_of(entry: dict) -> Optional[float]:
    """The audit's single-pass vision quality (1-5) when the catalogue records it (``audit.vision.quality`` or
    ``audit.vision_quality``; track T7 writes it for the new entries), else (fix round after P4a) the quality its
    ``audit.vision_doubt`` text names ("vision quality 2 (<= 2)"), else None."""
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    value = audit.get("vision_quality")
    if value is None and isinstance(audit.get("vision"), dict):
        value = audit["vision"].get("quality")
    if value is None:
        doubts = audit.get("vision_doubt")
        for text in (doubts if isinstance(doubts, list) else [doubts] if isinstance(doubts, str) else []):
            found = VISION_DOUBT_QUALITY.search(str(text))
            if found:
                return float(found.group(1))
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        return None
    return float(value)


def faces_of(entry: dict) -> Optional[int]:
    """The model's face count (``polycount``) when known."""
    n = entry.get("polycount")
    return int(n) if isinstance(n, (int, float)) and not isinstance(n, bool) and n > 0 else None


def faces_rank(entry: dict) -> int:
    """0 for a model with enough faces, 1 when the count is not known, 2 for a low-poly model (< ``FACES_LOW``)."""
    n = faces_of(entry)
    if n is None:
        return 1
    return 2 if n < FACES_LOW else 0


def texture_maps_of(entry: dict) -> Optional[dict]:
    """What the catalogue knows about a model's texture maps (Milestone 13: recorded per model, track T7 adds the PBR
    maps as ``texture_maps``): the entry's ``texture_maps`` record, else the audit's ``pbr_maps`` record (30 Oct 2026,
    UL131: the audit writes the maps under that name; 3,196 entries carry it and none ``texture_maps``, so every model
    ranked as "base colour only" and a sofa with normal and roughness maps never won its tie against a 256 px one),
    else ``{"base_colour": bool}`` from the Milestone 8 ``textured`` flag and the judged slots
    (``material_slots[].textured``); None when nothing is recorded."""
    maps = entry.get("texture_maps")
    if isinstance(maps, dict):
        return dict(maps)
    pbr = entry.get("pbr_maps")
    if isinstance(pbr, dict) and any(k in pbr for k in ("base_colour", "normal", "metallic_roughness")):
        return {k: v for k, v in pbr.items() if k in ("base_colour", "normal", "metallic_roughness", "occlusion",
                                                       "emissive", "roughness")}
    slots = [s for s in entry.get("material_slots") or [] if isinstance(s, dict)]
    textured = entry.get("textured")
    if not isinstance(textured, bool) and not slots:
        return None
    out: dict = {}
    if isinstance(textured, bool):
        out["base_colour"] = textured
    if slots:
        out["slots_textured"] = sum(1 for s in slots if s.get("textured") is True)
        out["slots"] = len(slots)
        out.setdefault("base_colour", out["slots_textured"] > 0)
    return out


def maps_rank(entry: dict) -> int:
    """0 for a model with normal or roughness maps recorded, 1 for base colour only (or unknown), 2 for flat colours."""
    maps = texture_maps_of(entry)
    if not maps:
        return 1
    if maps.get("normal") or maps.get("roughness") or maps.get("metallic_roughness"):
        return 0
    return 2 if maps.get("base_colour") is False else 1


def diversity_steps(asset_id: str, used: Optional[dict]) -> int:
    """The rank penalty (in ``SIZE_BUCKET`` steps) of using ``asset_id`` once more (Milestone 13, K2):
    ``PROJECT_REUSE_STEP`` per earlier use in another room of the project (``used["project"]`` minus
    ``used["room"]``: the n-th use in the project ranks n - 1 steps worse, so the next room gets another model when
    one of the same size step exists) plus ``ROOM_REUSE_STEPS`` once the room (``used["room"]``) holds it
    ``ROOM_REUSE_MAX`` times already, unless the piece's type (``used["type"]``) is a matched set (``SET_TYPES``: six
    dining chairs are one set, never three models). A penalty, never a gate: with nothing else in reach the model is
    used again."""
    if not used:
        return 0
    project = used.get("project") or {}
    room = used.get("room") or {}
    in_room = int(room.get(asset_id, 0) or 0)
    elsewhere = max(0, int(project.get(asset_id, 0) or 0) - in_room)
    steps = PROJECT_REUSE_STEP * elsewhere
    if in_room >= ROOM_REUSE_MAX and used.get("type") not in SET_TYPES:
        steps += ROOM_REUSE_STEPS
    return steps


# 25 Oct 2026 (user on real04's roof terrace): outdoor models first in open-air rooms (wenart/blender/outdoor.py, which
# the build's architect reads too); each grade adds OUTDOOR_STEPS size steps to the rank.
from wenart.blender.outdoor import OPEN_AIR_ROOMS, OUTDOOR_STEPS, outdoor_grade  # noqa: E402
from wenart.blender import outdoor as OD  # noqa: E402
# 30 Oct 2026 (lessons UL131, UL140; user on real04 run 20261029-201533-full: "I did not like these sofa models"): an
# upholstered model ranks by its quality grade (wenart/blender/soft_seats.py: a 256 px texture, flat colours, a
# double-sided export, a coarse mesh, a judged poor look): a fair model takes ``STEPS_PER_POINT`` size steps per point,
# a poor one ``POOR_STEPS`` (after every model within the caps); a ranking, never a gate
from wenart.blender import soft_seats as SS  # noqa: E402


def soft_steps(entry: dict) -> int:
    """The rank penalty (size steps) of an upholstered model's quality grade (``soft_seats.grade``); 0 for the other
    types."""
    return int(SS.grade(entry)["steps"]) if entry.get("type") in SS.SOFT_SEAT_TYPES else 0

# 28 Oct 2026 (user on real04 run 20261028-005318-full: "makes no sense to have that table with the carpet outside,
# that's outside area"; the roof terrace's table was the "Ravenna Home Traditional Dining Table", grade 1, because the
# ranking above was only a preference and no better-ranked model fitted the caps): an outdoor type
# (``outdoor.OUTDOOR_FURNITURE_TYPES``) in an open-air room takes only the models ``outdoor.outdoor_ready`` calls made
# for outside; the others are listed under ``excluded`` with the rule and the reason; none left -> the ladder, whose
# module and parametric steps build the piece in weather-proof materials (``outdoor.outdoor_asset``, a library gap).
OUTDOOR_ROOM_RULE = OD.OUTDOOR_RULE


def outdoor_candidates(piece: dict, candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    """``(kept, excluded)``: for a piece of an outdoor type in an open-air room (``open_air_room`` on the fitted
    copy), the candidates made for outside (``outdoor.outdoor_ready``), the others with the rule and the reason; every
    candidate for another piece."""
    ftype = str(piece.get("type") or "")
    if not piece.get("open_air_room") or ftype not in OD.OUTDOOR_FURNITURE_TYPES:
        return list(candidates), []
    kept, excluded = [], []
    for e in candidates:
        ready, why = OD.outdoor_ready(e, ftype)
        if ready:
            kept.append(e)
        else:
            excluded.append({"id": e["id"], "reason": f"not made for outside: {why}", "rule": OUTDOOR_ROOM_RULE})
    return kept, excluded


# 30 Oct 2026 (lesson UL178, user on real04 run 20261030-112241-full: "Table seems to be going through the chairs"; the
# play room's drawn round cafe table, a circle 0.79 m across with two chairs on its diagonal, was built as a square
# turned-leg library table whose corners and legs stood in the chairs): a round drawn table (``parametric
# .piece_is_round``) takes a round model (``parametric.model_is_round``: its title says so), else our round parametric
# table on a pedestal; a gate, not a rank, for the agent's pinned model too (``room_rule_refusal``)
ROUND_TABLE_TYPES: tuple[str, ...] = ("table_dining", "table_coffee", "side_table")
ROUND_TABLE_RULE = "round_table"


def round_misfit(entry: dict, piece: dict) -> Optional[str]:
    """UL178: why ``entry`` may not be the model of ``piece`` (None when it may): a round drawn table and a model
    whose title names no round shape."""
    from wenart.blender import parametric as P   # pure Python (no bpy)

    if str(piece.get("type") or "") not in ROUND_TABLE_TYPES or not P.piece_is_round(piece) or P.model_is_round(entry):
        return None
    return (f"the drawn {piece.get('type')} is round and the model is not (its title names no round shape): a square "
            f"table's corners and legs would stand in the chairs drawn round it (rule {ROUND_TABLE_RULE})")


def round_candidates(piece: dict, candidates: list[dict]) -> tuple[list[dict], list[dict]]:
    """UL178: ``(kept, excluded)``: for a round drawn table the round models (``round_misfit``), the others with the
    rule and the reason; every candidate for another piece."""
    kept, excluded = [], []
    for e in candidates:
        why = round_misfit(e, piece)
        if why is None:
            kept.append(e)
        else:
            excluded.append({"id": e["id"], "reason": why, "rule": ROUND_TABLE_RULE})
    return kept, excluded


# 26 Oct 2026 (fix E, user: "there is no taste in the furniture selection"; real06's Scandinavian living room got a
# folding chair at a turned-leg "Traditional ... Rustic" table with Eames chairs). Two rank rules, never gates:
# - a misfit (``misfit_of``): a model whose title, name or audit names a folding or camping piece, an outdoor piece in
#   an indoor room ("garden", "outdoor", "patio") or, for a dining chair, a bar or counter stool, ranks after every
#   other model (after the generated ones too); open-air rooms keep their outdoor ranking instead;
# - a style mix (``style_mix_of``, the dining group's table, chairs and bench): a model whose ``styles`` or title name a
#   style outside the project family's compatible styles (the family, its ``STYLE_FALLBACK``, a style whose fallback
#   is the family, ``neutral``) takes ``STYLE_MIX_STEPS`` size steps, so the table and the chairs come from
#   compatible styles whenever such models fit.
MISFIT_ANY = ("folding", "foldable", "camping")
MISFIT_INDOOR = ("garden", "outdoor", "patio")
MISFIT_CHAIR = ("bar", "barstool", "bar stool", "counter stool", "counterstool")
STYLE_MIX_TYPES: tuple[str, ...] = ("table_dining", "chair", "bench")
STYLE_MIX_STEPS = 5              # 25 %: more than the size steps two models inside the caps differ by
STYLE_WORDS: dict[str, tuple[str, ...]] = C.STYLE_WORDS     # title words that name a style (catalog)


def _words_in(text: str, words: tuple[str, ...]) -> list[str]:
    return [w for w in words if re.search(rf"\b{re.escape(w)}\b", text)]


def misfit_of(entry: dict, ftype: str, outdoor: Optional[bool] = False) -> Optional[str]:
    """26 Oct 2026 (fix E): why a model does not suit the piece (None when it does): its title, name or audit
    (notes, doubts, reasons) names a folding or camping piece, an outdoor piece in an indoor room, or, for a chair, a
    bar or counter stool. Open-air rooms (``outdoor`` True) are ranked by ``outdoor_grade`` instead; with the room
    unknown (``outdoor`` None: a single piece fitted outside ``fit_building``) the outdoor words are not read."""
    if outdoor:
        return None
    title = " ".join(str(entry.get(k) or "") for k in ("title", "name")).lower()
    audit = entry.get("audit") if isinstance(entry.get("audit"), dict) else {}
    text = title + " " + " ".join(str(x) for k in ("notes", "vision_doubt", "reasons")
                                  for x in (audit.get(k) or [])).lower()
    hits = _words_in(text, MISFIT_ANY) + (_words_in(text, MISFIT_INDOOR) if outdoor is False else [])
    if ftype == "chair":
        hits += _words_in(title, MISFIT_CHAIR)
    return f"names {', '.join(dict.fromkeys(hits))}: not for an indoor {ftype}" if hits else None


# 30 Oct 2026 (lesson UL163; user on real04 run 20261030-043021-full: "the headrest needs to be re-done I did not like the
# headrest": a "Full Saddle Back Upholstered Bed" with an arched camelback headboard in a modern bedroom): an arched,
# camelback, wingback, sleigh or scalloped headboard is a romantic or classic product; in any other family (or without a
# design that asks for it) such a bed ranks last, after every bed with a rectangular headboard (a panel, channel tufting,
# slats), and is used only when no other bed fits (designer rule, assumed; its title or its catalogue's
# ``headboard_form`` says the form).
HEADBOARD_ROMANTIC_WORDS: tuple[str, ...] = ("saddle back", "saddleback", "camelback", "camel back", "arched", "arch",
                                             "scalloped", "wingback", "wing back", "sleigh", "chesterfield")
HEADBOARD_ROMANTIC_FORMS: tuple[str, ...] = ("arched", "camelback", "wingback", "sleigh", "scalloped")
HEADBOARD_ROMANTIC_FAMILIES: tuple[str, ...] = ("classic", "romantic", "traditional")


def headboard_misfit(entry: dict, ftype: str, family: Optional[str], design: Optional[dict] = None) -> Optional[str]:
    """Why a bed model's headboard does not suit the family (None when it does; pure, UL163): an arched or camelback
    form (``HEADBOARD_ROMANTIC_WORDS`` in its title or name, or its ``headboard_form``) outside the romantic and
    classic families, unless the piece's design asks for that form (``design["headboard"]``)."""
    if ftype not in C.BED_TYPES:
        return None
    fam = str(family or "").lower()
    asked = str((design or {}).get("headboard") or "").lower()
    if fam in HEADBOARD_ROMANTIC_FAMILIES or asked in HEADBOARD_ROMANTIC_FORMS:
        return None
    title = " ".join(str(entry.get(k) or "") for k in ("title", "name")).lower()
    hits = _words_in(title, HEADBOARD_ROMANTIC_WORDS)
    form = str(entry.get("headboard_form") or "").lower()
    if form in HEADBOARD_ROMANTIC_FORMS:
        hits.append(form)
    if not hits:
        return None
    return (f"an arched or camelback headboard ({', '.join(dict.fromkeys(hits))}) is no {fam or 'modern'} bed's: a "
            f"rectangular headboard first (UL163)")


# Bathroom sense of 26 Oct 2026 (user: "fix should be general"; real06's adult bathrooms got a "TODDLER SINK" with an
# orange vanity and a "Combo CEG-50BF", a black composite utility basin): a model made for another user or another use
# than the piece is no candidate (a gate, never a rank rule: ``use_misfit``, ``excluded`` with the rule and the reason).
# - a children's product (``CHILD_PRODUCT_WORDS`` in its title or name) only in a child's room (``rooms[].room_subtype``
#   child, ``child_room`` on the fitted piece: ``use_context``);
# - a fixture of another room (``OTHER_USE_WORDS`` by type: a washbasin named for a kitchen, a laundry, a utility or
#   commercial sink, a mop or bar sink; a kitchen sink named for a bathroom);
# - a washbasin whose main material slot (``OTHER_USE_SHARE`` of the model) is named a composite or granite: the
#   material of kitchen and utility sinks (a bathroom basin is glazed ceramic; the audit's ``sanitary_finish`` does the
#   same for a metal one).
CHILD_PRODUCT_WORDS: tuple[str, ...] = ("toddler", "toddlers", "kid", "kids", "child", "children", "childrens",
                                        "baby", "babies", "nursery", "infant", "junior", "preschool", "kindergarten",
                                        "montessori", "cocuk", "bebek")
OTHER_USE_WORDS: dict[str, tuple[str, ...]] = {
    "washbasin": ("kitchen", "laundry", "utility", "mop", "janitor", "slop", "service sink", "bar sink", "commercial",
                  "sinkware", "catering", "spüle", "spule", "einbauspüle", "einbauspule", "küche", "kuche", "evye",
                  "cocina", "cuisine", "keuken", "cucina"),
    "sink_kitchen": ("bathroom", "vanity", "washbasin", "wash basin", "wash-basin", "lavabo", "lavatory", "cloakroom",
                     "waschbecken", "waschtisch", "wastafel"),
}
# 30 Oct 2026 (lesson UL176; the user on real04's f_L0_021 on 28 Oct, UL73, and again on run 20261030-112241-full: "I
# did not like this bed"): the "Komfi Adjustable Bed", a motorised care bed (a sectioned glossy black and chrome base in
# two flat materials, its top not one surface: the throw over our duvet tore on it), won the bedroom's double bed by size
# and taste in both runs. A care, hospital or motion bed is a product for another use, never a home's bed.
CARE_BED_WORDS: tuple[str, ...] = ("adjustable", "hospital", "nursing", "care bed", "medical", "motorised",
                                   "motorized", "electric bed", "massage", "profiling", "pflegebett", "zero gravity")
for _bed in C.BED_TYPES:
    OTHER_USE_WORDS[_bed] = OTHER_USE_WORDS.get(_bed, ()) + CARE_BED_WORDS
OTHER_USE_MATERIALS: dict[str, tuple[str, ...]] = {"washbasin": ("composite", "granite")}
# 26 Oct 2026 (the merge of the bathroom fixes: an "arancione glass sink" won a basin of a calm modern bathroom): sanitary
# ware and kitchen fixtures in a loud colour are an accent no style asks of them; the title's colour words (several
# languages) keep such a model out
LOUD_FIXTURE_TYPES: tuple[str, ...] = ("washbasin", "toilet", "bidet", "bathtub", "shower", "sink_kitchen")
LOUD_COLOUR_WORDS: tuple[str, ...] = ("orange", "arancione", "naranja", "red", "rosso", "rojo", "rouge", "green", "verde",
                                      "vert", "blue", "blu", "azul", "bleu", "yellow", "giallo", "amarillo", "jaune",
                                      "pink", "rosa", "purple", "viola", "violet", "lilac", "turquoise", "teal", "lime",
                                      "magenta", "fuchsia", "coral")
OTHER_USE_SHARE = 0.5
USE_RULE = "fit.product_use"


def _named(text: str, words: tuple[str, ...]) -> list[str]:
    """The ``words`` (or phrases) ``text`` names as whole words (letters of any script)."""
    return [w for w in words if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text)]


def use_misfit(entry: dict, ftype: str, child_room: Optional[bool] = False) -> Optional[str]:
    """Bathroom sense of 26 Oct 2026 (the comment above): why a library model is made for another user or use than a
    ``ftype`` piece (None when it is not): a children's product outside a child's room (``child_room`` not true), a
    fixture its title names for another room, a washbasin of a kitchen-sink material, a fixture whose title names a
    loud colour (``LOUD_COLOUR_WORDS``)."""
    title = html.unescape(" ".join(str(entry.get(k) or "") for k in ("title", "name"))).lower()
    kids = _named(title, CHILD_PRODUCT_WORDS)
    if kids and child_room is not True:
        return (f"names {', '.join(dict.fromkeys(kids))}: a children's product, not for a {ftype} outside a child's "
                f"room")
    other = _named(title, OTHER_USE_WORDS.get(ftype, ()))
    if other:
        return f"names {', '.join(dict.fromkeys(other))}: a product for another use, not a {ftype}"
    loud = _named(title, LOUD_COLOUR_WORDS) if ftype in LOUD_FIXTURE_TYPES else []
    if loud:
        return f"names {', '.join(dict.fromkeys(loud))}: a {ftype} in a loud colour (sanitary ware stays calm)"
    words = OTHER_USE_MATERIALS.get(ftype)
    if words:
        for slot in entry.get("material_slots") or []:
            if not isinstance(slot, dict) or float(slot.get("share") or 0.0) < OTHER_USE_SHARE:
                continue
            hit = _named(str(slot.get("name") or "").lower().replace("_", " "), words)
            if hit:
                return (f"its main material ({slot.get('name')}, {float(slot['share']):.0%}) is {hit[0]}: a kitchen "
                        f"or utility sink, not a {ftype}")
    return None


def use_context(building: Optional[dict], piece: dict) -> dict:
    """Bathroom sense of 26 Oct 2026: the keys ``use_misfit`` reads, for a fitted copy of ``piece``: ``child_room``
    (its room's ``room_subtype`` is child)."""
    room = next((r for r in (building or {}).get("rooms") or [] if r.get("id") == piece.get("room_id")), None)
    return {"child_room": bool(room and room.get("room_subtype") == "child")}


# 30 Oct 2026 (lesson UL156, user on real04 run 20261030-043021-full: "I did not like this lamp table combo": the open
# kitchen variant's living room had a Herman Miller Nelson end table, a thin top on a swivel 4-star base that reads as
# office furniture, under a two-tone drum lamp): a side table, a nightstand or a coffee table stands on a solid base. A
# model whose title names an office, swivel, star or rolling base (``OFFICE_BASE_WORDS``, the star-base products of
# ``STAR_BASE_PRODUCTS``) is no candidate outside a study or office room (``WORK_ROOM_TYPES``): a gate (``base_misfit``).
STABLE_BASE_TYPES: tuple[str, ...] = ("side_table", "nightstand", "table_coffee")
OFFICE_BASE_WORDS: tuple[str, ...] = ("swivel", "star base", "star-base", "4-star", "5-star", "five star", "office",
                                      "rolling", "go-cart", "castor", "castors", "caster", "casters", "wheels",
                                      "wheeled", "trolley")
STAR_BASE_PRODUCTS: tuple[str, ...] = ("nelson end table", "nelson small end table")
WORK_ROOM_TYPES: tuple[str, ...] = ("other",)      # the study, the home office (``names``: calisma, study, office)
BASE_RULE = "fit.stable_base"
# 30 Oct 2026 (lesson UL161, user on real04's play-and-rest room: "I did not like these sofas here maybe used in another
# project but not here": two white HEMNES daybed frames, drawers under a mattress seat and panelled ends, pinned by the
# agent as the room's sofas, facing each other): a daybed is a bed-like piece. It is no sofa of a living-type room
# (``LOUNGE_ROOM_TYPES``: the living, lounge, family and play-and-rest rooms are ``living``) unless the piece asks for
# one (its design form, raw type or label names a daybed: ``daybed_asked``) in a family that seats a living room on a
# daybed (``DAYBED_FAMILIES``); a bedroom (a guest or a child's room) and a study (``other``) keep it. The model stays in
# the library for those rooms and projects (a gate: ``daybed_misfit``, never an audit removal).
DAYBED_WORDS: tuple[str, ...] = ("daybed", "daybeds", "day bed", "day-bed", "trundle", "guest bed", "futon",
                                 "sofa bed frame")
DAYBED_SOFA_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "chaise")
LOUNGE_ROOM_TYPES: tuple[str, ...] = ("living", "dining", "hall", "balcony")
DAYBED_FAMILIES: tuple[str, ...] = ("cottage", "farmhouse", "scandinavian", "rustic", "coastal")
DAYBED_RULE = "fit.daybed_room"


def _title_of(entry: dict) -> str:
    return html.unescape(" ".join(str(entry.get(k) or "") for k in ("title", "name"))).lower()


def base_misfit(entry: dict, ftype: str, room_type: Optional[str]) -> Optional[str]:
    """UL156 (the comment above): why a side table, nightstand or coffee table model stands on a base that is no
    furniture of a living or sleeping room (None when it does not): its title names an office, swivel, star or rolling
    base, or a star-base product; a study or office room (``WORK_ROOM_TYPES``) keeps it."""
    if ftype not in STABLE_BASE_TYPES or room_type in WORK_ROOM_TYPES:
        return None
    title = _title_of(entry)
    hits = _named(title, OFFICE_BASE_WORDS) + _named(title, STAR_BASE_PRODUCTS)
    if not hits:
        return None
    return (f"names {', '.join(dict.fromkeys(hits))}: an office, swivel, star or rolling base, not a "
            f"{ftype.replace('_', ' ')} of a {room_type or 'living'} room (a solid base: UL156)")


def daybed_asked(piece: dict) -> bool:
    """UL161: whether the piece itself asks for a daybed: its design form, its raw type or its label names one."""
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    text = " ".join(str(v or "") for v in (design.get("form"), design.get("kind"), piece.get("type_raw"),
                                           piece.get("label"), piece.get("form"))).lower().replace("_", " ")
    return bool(_named(text, DAYBED_WORDS))                  # (a block name "DAYBED_200" names one too)


def daybed_misfit(entry: dict, ftype: str, room_type: Optional[str], family: Optional[str],
                  asked: bool = False) -> Optional[str]:
    """UL161 (the comment above): why a daybed model is no sofa of this room (None when it may be one)."""
    if ftype not in DAYBED_SOFA_TYPES or room_type not in LOUNGE_ROOM_TYPES:
        return None
    hits = _named(_title_of(entry), DAYBED_WORDS)
    if not hits:
        return None
    if asked and family in DAYBED_FAMILIES:
        return None
    why = ("the piece asks for a daybed but the " + (family or "project") + " family seats a living room on an "
           "upholstered sofa") if asked else "the piece does not ask for one"
    return (f"names {', '.join(dict.fromkeys(hits))}: a bed-like daybed, not the {ftype.replace('_', ' ')} of a "
            f"{room_type} room ({why}; a guest, child's or study room keeps it: UL161)")


def room_use_context(building: Optional[dict], piece: dict) -> dict:
    """UL156, UL161: the keys ``use_candidates`` reads beside ``use_context``, for a fitted copy of ``piece``:
    ``room_type`` (its room's, lower case; None when unknown) and ``daybed_asked``."""
    room = next((r for r in (building or {}).get("rooms") or [] if r.get("id") == piece.get("room_id")), None)
    rtype = str(room.get("room_type") or "").lower() or None if room else None
    return {"room_type": rtype, "daybed_asked": daybed_asked(piece)}


def use_candidates(piece: dict, candidates: list[dict], family: Optional[str] = None
                   ) -> tuple[list[dict], list[dict]]:
    """``(kept, excluded)``: the candidates ``use_misfit`` keeps for the piece, the others with the rule and the
    reason. 30 Oct 2026: also the base rule (``base_misfit``, UL156) and the daybed rule (``daybed_misfit``, UL161,
    the project's style ``family``) when the piece carries its room's type (``room_use_context``)."""
    kept, excluded = [], []
    ftype = str(piece.get("type") or "")
    room_type = piece.get("room_type")
    for e in candidates:
        why, rule = use_misfit(e, ftype, piece.get("child_room")), USE_RULE
        if why is None and room_type:
            why, rule = base_misfit(e, ftype, room_type), BASE_RULE
            if why is None:
                why, rule = daybed_misfit(e, ftype, room_type, family, bool(piece.get("daybed_asked"))), DAYBED_RULE
        if why is None:
            kept.append(e)
        else:
            excluded.append({"id": e["id"], "reason": why, "rule": rule})
    return kept, excluded


def room_rule_refusal(entry: dict, piece: dict, family: Optional[str]) -> Optional[str]:
    """UL156, UL161: why the room rules refuse a model the agent pinned (None when they keep it); the pin's refusal
    names it instead of the caps. UL178: a round drawn table refuses a model that is not round (``round_misfit``)."""
    shape = round_misfit(entry, piece)
    if shape:
        return shape
    room_type = piece.get("room_type")
    if not room_type:
        return None
    ftype = str(piece.get("type") or "")
    return base_misfit(entry, ftype, room_type) or daybed_misfit(entry, ftype, room_type, family,
                                                                bool(piece.get("daybed_asked")))


compatible_styles = C.compatible_styles


def style_mix_of(entry: dict, ftype: str, family: Optional[str]) -> list[str]:
    """26 Oct 2026 (fix E): the styles outside ``compatible_styles(family)`` a dining-group model carries
    (``STYLE_MIX_TYPES``): its ``styles`` tags and the styles its title words name (``STYLE_WORDS``); [] for other
    types or without a family."""
    allowed = compatible_styles(family)
    if allowed is None or ftype not in STYLE_MIX_TYPES:
        return []
    return sorted({str(s) for s in list(entry.get("styles") or []) + C.title_styles(entry)} - allowed)


def rank_key(entry: dict, width: float, depth: float, used: Optional[dict] = None,
             prefs: Optional[dict] = None, outdoor: bool = False, taste: Optional[dict] = None,
             misfit: bool = False, mix_steps: int = 0) -> tuple:
    """The order of a candidate on a ``width x depth`` footprint (lower first, docs/milestone8.md §1; Milestone 13
    K2): generated last, known units before normalised ones, the real-size step of the uniform scale plus the
    diversity penalty (``diversity_steps``), an audited real product (``real_product: true``) before the others of its
    step, the design preference (``prefs``: 0 shows the design, 1 does not), no other audit vision doubt
    (``other_doubt_of``; integration after P5), the audit's vision quality, the texture
    maps, the judges' quality, the face count, aspect error, source order and the id. The first three keys keep their
    Milestone 8 places (tests read ``rank_key(...)[2]`` as the size step). 26 Oct 2026 (fix E): a ``misfit`` ranks
    after every other model (the first key: 2 + generated), a style mix adds ``mix_steps`` size steps. 30 Oct 2026
    (UL131): an upholstered model adds the size steps of its quality grade (``soft_steps``). 30 Oct 2026 (UL215): a
    model with a maker's logo or print (``logo_flag``; relaxed mode only) ranks after a clean one of the same step, just
    after the vision doubt (a logo is no removal, the clean model is preferred)."""
    scales, _ = scale_for(entry, width, depth)
    known = units_known(entry)
    bucket = int(size_error(scales) / SIZE_BUCKET + 1e-9) if known else 0
    bucket += diversity_steps(entry["id"], used)
    if outdoor:
        bucket += OUTDOOR_STEPS * outdoor_grade(entry)
    if taste:                                    # 25 Oct 2026: the room's set (wenart/furniture/taste.py)
        from wenart.furniture.taste import TASTE_STEP
        bucket += TASTE_STEP * int(taste.get(entry["id"], 0))
    bucket += int(mix_steps)
    bucket += soft_steps(entry)                  # 30 Oct 2026 (UL131): an upholstered model's quality grade
    real = 0 if entry.get("real_product") is True else 1
    pref = int((prefs or {}).get(entry["id"], 0) or 0)
    vq = vision_quality_of(entry)
    return ((2 if misfit else 0) + (1 if entry.get("source") == GENERATED else 0), 0 if known else 1, bucket, real,
            pref, other_doubt_of(entry), int(C.logo_flagged(entry)), -(vq if vq is not None else VISION_QUALITY_DEFAULT),
            maps_rank(entry), -quality_of(entry), faces_rank(entry), round(C.aspect_error(entry, width, depth), 6),
            source_rank(entry), entry["id"])


def rank_candidates(candidates: list[dict], width: float, depth: float, used: Optional[dict] = None,
                    prefs: Optional[dict] = None, outdoor: bool = False, taste=None,
                    flags: Optional[dict] = None) -> list[dict]:
    """The candidates in rank order (``rank_key``). ``taste`` (25 Oct 2026): ``(cache, room set, target)`` of
    ``wenart.furniture.taste``: the first ``TASTE_POOL`` of the order are ranked again with their taste steps.
    ``flags`` (26 Oct 2026, fix E): ``{id: {"misfit": str | None, "style_mix": [styles]}}`` (``_fit_family``)."""
    flags = flags or {}

    def extra(e) -> dict:
        f = flags.get(e["id"]) or {}
        return {"misfit": bool(f.get("misfit")), "mix_steps": STYLE_MIX_STEPS if f.get("style_mix") else 0}

    ordered = sorted(candidates, key=lambda e: rank_key(e, width, depth, used, prefs, outdoor, **extra(e)))
    if not taste:
        return ordered
    from wenart.furniture import taste as T
    cache, room, target = taste
    head = ordered[:TASTE_POOL]
    pens = {e["id"]: T.steps(cache.get(e), room, target) for e in head}
    head = sorted(head, key=lambda e: rank_key(e, width, depth, used, prefs, outdoor, pens, **extra(e)))
    return head + ordered[TASTE_POOL:]


TASTE_POOL = 25                  # the candidates whose look is read (the cost of a first run is bounded)


def ranking_reasons(tried: list[dict], chosen: dict) -> dict:
    """Why the chosen candidate won (the asset's ``ranking`` record)."""
    i = next(n for n, t in enumerate(tried) if t["id"] == chosen["id"])
    size = (f"real size: mean |scale - 1| {chosen['size_error']:.3f} (step {chosen['size_bucket']})"
            if chosen["units_known"] else "units not known (normalised by type): ranked after the real-size models")
    why = [size, f"quality {chosen['quality']:g}", f"aspect error {chosen['aspect_error']:.3f}",
           f"source {chosen['source']}"]
    if chosen.get("diversity_steps"):
        why.insert(1, f"diversity penalty {chosen['diversity_steps']} step(s) (used before in the room or project)")
    if chosen.get("design_pref"):
        why.insert(1, "does not show the design (every model that shows it failed the caps)")
    if chosen.get("vision_quality") is not None:
        why.insert(2, f"audit vision quality {chosen['vision_quality']:g}")
    if chosen.get("upholstery"):                 # 30 Oct 2026 (UL131): an upholstered model's quality grade
        steps = chosen.get("upholstery_steps")
        why.insert(1, f"upholstery {chosen['upholstery']}" + (f" ({steps} size step(s) added)" if steps else ""))
    if chosen.get("faces") is not None:
        why.append(f"faces {chosen['faces']}")
    if chosen["source"] == GENERATED:
        why.insert(0, "generated: no other library model passed the caps")
    passed_over = [{"id": t["id"], "why": "outside the caps (non-uniform {:.1f} %, mean scale {}{})".format(
        (t["non_uniform"] - 1) * 100, t["mean_scale"], "" if t.get("height_ok", True) else
        ", too tall for the sloped ceiling" if t.get("under_ceiling") is False else ", height outside the range")}
        for t in tried[:i]]
    return {"rule": RANKING_RULE, "rank": chosen["rank"], "tried": len(tried), "reasons": why,
            "passed_over": passed_over}


def usable_candidates(ftype: str, candidates: list[dict], style_family: Optional[str]) -> tuple[list, list, Optional[str]]:
    """``(usable, excluded, reason)`` of the catalogue candidates of a type (docs/milestone7.md §6.3): beds
    without a mattress are dropped unless they are bed frames with a deck (docs/milestone8.md §4), then models
    whose ``styles`` hold neither ``style_family`` nor ``neutral`` (none when the family is None).
    ``excluded`` rows are ``{"id", "reason"}``; ``reason`` is the parametric fallback reason when nothing is
    usable, else None."""
    excluded = [{"id": e["id"], "reason": "bed model without a mattress"} for e in candidates if not bed_usable(e)]
    with_mattress = [e for e in candidates if bed_usable(e)]
    if not with_mattress:
        return [], excluded, f"no {ftype} model with a mattress"
    usable = []
    for e in with_mattress:
        if C.styles_match(e, style_family):
            usable.append(e)
        else:
            excluded.append({"id": e["id"], "reason": f"styles {e.get('styles') or []} include neither "
                                                      f"{style_family} nor {C.NEUTRAL}"})
    if not usable:
        return [], excluded, f"no model for style {style_family}"
    return usable, excluded, None


UNIFORM_RANGE = (0.85, 1.20)   # a model stretched more than this looks wrong (a 1.1 m tall sofa); M12: was 0.75-1.30


def _srgb_to_lab(rgb) -> tuple[float, float, float]:
    from wenart.style import colours as CL

    return CL.linear_to_lab(tuple(CL.srgb_to_linear(float(c) / 255.0) for c in rgb[:3]))


def colour_distance(srgb_255, colour: str) -> Optional[float]:
    """CIELAB Delta E (1976) between a judged slot colour (``colour_rgb``, sRGB 0-255) and a colour phrase of
    ``wenart/style/colours.py``; None when either is unknown."""
    from wenart.style import colours as CL

    if not srgb_255 or len(srgb_255) < 3:
        return None
    try:
        target = CL.linear_to_lab(CL.linear_rgb(colour))
    except (KeyError, ValueError):
        return None
    lab = _srgb_to_lab(srgb_255)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(lab, target)))


def _slots(entry: dict, material: str, separable: bool) -> list[dict]:
    return [s for s in entry.get("material_slots") or [] if isinstance(s, dict) and s.get("material") == material
            and (not separable or s.get("separable")) and float(s.get("share") or 0.0) >= RECOLOUR_MIN_SHARE]


def look_of(entry: dict, ftype: str, design: dict) -> tuple[Optional[dict], Optional[str]]:
    """``(look, why not)`` of one library model for a piece's design (pure, Milestone 10): ``look`` holds what the
    asset gets (``recolour`` of its fabric / wood slots, ``colour_match``, ``tags``), or None and the reason the
    model cannot show the design (asked material tags missing; the fabric colour neither recolourable nor
    matching; a model nobody judged)."""
    look: dict = {}
    tags = [t for t in design.get("material_tags") or [] if isinstance(t, str)]
    if tags:
        have = entry.get("material_tags")
        if have is None:
            return None, f"no judged material tags (the design asks for {', '.join(tags)})"
        missing = [t for t in tags if t not in have]
        if missing:
            return None, f"material tags {have} lack {', '.join(missing)}"
        look["tags"] = tags
    colour = design.get("fabric_colour") if ftype in UPHOLSTERED_TYPES else design.get("colour")
    if ftype in UPHOLSTERED_TYPES and not colour:
        colour = design.get("colour")
    if colour:
        material = "fabric" if ftype in UPHOLSTERED_TYPES else None
        if material and entry.get("recolourable_fabric") is True and _slots(entry, "fabric", True):
            look["recolour"] = {"fabric": {"colour": colour, "slots": [{"index": s["index"], "name": s.get("name")}
                                                                       for s in _slots(entry, "fabric", True)]}}
        else:
            judged = [s for s in entry.get("material_slots") or [] if isinstance(s, dict)
                      and (material is None or s.get("material") == material) and s.get("colour_rgb")]
            if not judged:
                return None, (f"cannot take the colour {colour}: no recolourable {material or 'judged'} slot and no "
                              "judged slot colour")
            dist = [d for d in (colour_distance(s["colour_rgb"], colour) for s in judged) if d is not None]
            if not dist or min(dist) > COLOUR_MATCH_DE:
                return None, (f"cannot take the colour {colour}: not recolourable and its "
                              f"{material or 'slot'} colour is {min(dist) if dist else float('nan'):.1f} Delta E away "
                              f"(> {COLOUR_MATCH_DE:g})")
            look["colour_match"] = {"colour": colour, "delta_e": round(min(dist), 2)}
    wood = design.get("wood")
    if wood and entry.get("recolourable_wood") is True and _slots(entry, "wood", True):
        from wenart.style import vocabulary as V

        flat = (V.FURNITURE_MATERIALS.get(wood) or {}).get("flat")
        if flat:
            look.setdefault("recolour", {})["wood"] = {
                "colour": wood, "rgb": [float(v) for v in flat],
                "slots": [{"index": s["index"], "name": s.get("name")} for s in _slots(entry, "wood", True)]}
    return look, None


def chaise_side_candidates(candidates: list[dict], side: Optional[str]) -> tuple[list[dict], list[dict], str]:
    """``(kept, excluded, side)`` for an L-shaped piece (``shape: L``; review finding 40): only models whose
    ``chaise_side`` (track D: left / right as a viewer facing the front sees it, measured from the footprint) is the
    piece's ``chaise_side`` (``right`` when the piece has none, as the scene builder assumes); a model without a
    side is excluded as "chaise side unknown", one with the other side too. Library models are never mirrored."""
    want = side if side in C.CHAISE_SIDES else "right"
    kept, excluded = [], []
    for e in candidates:
        has = e.get("chaise_side")
        if has is None:
            excluded.append({"id": e["id"], "reason": "chaise side unknown"})
        elif has != want:
            excluded.append({"id": e["id"], "reason": f"chaise on the {has}, the piece's on the {want} "
                                                      "(no mirroring)"})
        else:
            kept.append(e)
    return kept, excluded, want


class _OneModel:
    """A catalogue view with one library model (the agent's pinned ``asset_pin``, Milestone 11)."""

    def __init__(self, catalog, entry: dict):
        self._catalog = catalog
        self._entry = entry

    def candidates(self, ftype: str) -> list[dict]:
        return [self._entry] if self._entry.get("type") == ftype else []

    @property
    def parametric_types(self) -> list[str]:
        return self._catalog.parametric_types


def fit_piece(piece: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP,
              uniform_range: tuple[float, float] = UNIFORM_RANGE, style_family: Optional[str] = None,
              design: Optional[dict] = None, *, mode: str = "commercial", used: Optional[dict] = None,
              style: Optional[dict] = None, ceiling: Optional[float] = None) -> dict:
    """The ``asset`` dict for one piece (pure: the piece is not modified).

    A candidate is accepted when its uniform scale to the drawn width leaves its depth within ``cap`` of the drawn
    depth (Milestone 13: the layout absorbs the difference) and the scale within ``uniform_range``; otherwise the
    next candidate in rank order (``rank_key``) is tried, then the fallback ladder. Beds without a mattress (unless
    bed frames with a deck) and, with ``style_family``, models of another style are no candidates
    (``usable_candidates``). Milestone 10 / 13: ``design`` (the piece's look) is a preference: the models that show it
    (``look_of``) rank first, the others are still tried and a win of theirs records ``design_not_shown``. An L-shaped
    piece keeps only the models with its chaise side (``chaise_side_candidates``); none left -> the ladder (the
    parametric L builds the drawn side).

    Milestone 12 (docs/milestone12.md §4.8 D14, §6.4; track S) and Milestone 13 (docs/milestone13.md §13.2; track
    T1), in this order:

    1. only usable models in licence ``mode`` (``catalog.usable``: no audit ``removed`` / ``pending``; in
       ``commercial`` mode only commercial-safe entries, in ``relaxed`` mode everything but no-derivatives);
       refused ones are listed under ``excluded``;
    2. the style family, then its fallback chain (``STYLE_FALLBACK``, e.g. mediterranean -> rustic -> classic;
       ``neutral`` models count for every family); a model of a fallback family records ``style_fallback``; a pinned
       model (``asset_pin``, the agent's ``swap_model``) skips the style filter;
    3. the caps, then the relaxed caps (``RELAXED_CAP``, ``RELAXED_RANGE``) while the fitted box stays inside the
       type's documented ranges (``caps_relaxed`` on the asset);
    4. the by-design parametric types (``catalog.BY_DESIGN_PARAMETRIC_TYPES``) go parametric by design; a piece its
       group needs (``group_needs``) takes a model of the nearest related type (``RELATED_TYPES``) first;
    5. else the ladder's step 2, a module builder (``module_plan_for``, track T2: ``method: module``), then step 3,
       the parametric family (``method: parametric``); ``method: none`` only for a piece with ``build: false``.
    Every asset carries ``ladder``, ``licence``, ``licence_flag``, ``commercial_safe`` and ``licence_mode``
    (``_finish``); ``used`` (``{"project": Counter, "room": Counter}`` of asset ids) feeds the diversity penalty.
    Fix round after P6a (module docstring): ``ceiling`` (``piece_ceiling``; None on a flat level) is the height the
    piece has under a sloped ceiling: a model fitted taller than ``ceiling - CEILING_MARGIN_M`` is refused like one
    outside the real height range, a pinned one too (``pin_refused`` says so).
    """
    mode = C.check_mode(mode)
    ftype = piece["type"]
    if piece.get("build") is False and ftype != "unknown":
        # (an unknown piece keeps its parametric record below: no library search either.)
        # Milestone 13 (16 Oct 2026, found with the HSSD layer): a piece that is not built (not furniture, removed)
        # gets no model at all, not even one that fits: a library asset on it would be credited and counted although
        # nothing is built. Before the HSSD layer no model happened to fit the not-built pieces of the tests.
        why = "the piece is not built (build false): no model is searched"
        return _finish(gap_fit(piece, why, [], [], style_family), mode,
                       [_step("library", "not tried", why), _step(MODULE_METHOD, "not tried", why),
                        _step("parametric", "not tried", why)])
    width, depth = piece["footprint"]["size"]
    if not (width > 0 and depth > 0):
        asset = parametric_fit(piece, f"footprint size {piece['footprint']['size']} is not positive",
                               style_family=style_family)
        return _finish(asset, mode, [_step("parametric", "used", asset["fallback_reason"])])
    if C.scheme_form(piece) and not piece.get("asset_pin"):
        # 29 Oct 2026 (lesson UL119, docs/reference_details_20261029.md R17, R27, R33): the room's scheme asks a round
        # drum or a floating nightstand, or a floating corner desk; the catalogue holds no audited model of that form,
        # so our parametric product of real proportions is built by design (wenart.blender.detail_parts)
        why = (f"the room's scheme asks for a {piece['form']} {ftype.replace('_', ' ')} (UL119: a different solution "
               f"for each room): our parametric product by design (the catalogue holds no audited {piece['form']} "
               f"model)")
        asset = parametric_fit(piece, why, style_family=style_family)
        asset["by_design"] = True
        asset["scheme_form"] = piece["form"]
        return _finish(asset, mode, [_step("library", "not tried", why), _step(MODULE_METHOD, "not tried", why),
                                     _step("parametric", "used (by design)", why)])
    pin = piece.get("asset_pin")
    if pin:
        # Milestone 11 (edit_ops swap_model): the agent's model is tried alone first; Milestone 13: without the style
        # filter (the agent's choice is the decision), the caps and the licence mode still apply; when it fails them
        # the normal ranking decides and the asset says so.
        entry = next((e for e in catalog.candidates(ftype) if e.get("id") == pin), None)
        if entry is not None and C.usable(entry, mode) and entry.get("source") == GENERATED:
            # fix round after P4a (module docstring): no pin to a generated model while a real product fits
            ranked = fit_piece(dict(piece, asset_pin=None), catalog, cap, uniform_range, style_family, design,
                               mode=mode, used=used, style=style, ceiling=ceiling)
            chosen = next((e for e in catalog.candidates(ftype) if e.get("id") == ranked.get("asset_id")), None)
            if ranked.get("method") == "library" and chosen is not None and chosen.get("source") != GENERATED:
                ranked["pin_refused"] = (f"{pin}: a generated model (units guessed) while a real product of the "
                                         f"type fits within the caps ({chosen['id']})")
                return ranked
        room_refusal = room_rule_refusal(entry, piece, style_family) if entry is not None else None
        if room_refusal:
            # 30 Oct 2026 (UL156, UL161): the room rules hold for the agent's pin too (real04's play room: a daybed
            # pinned as its sofas); the normal ranking decides and the asset names the rule
            asset = fit_piece(dict(piece, asset_pin=None), catalog, cap, uniform_range, style_family, design,
                              mode=mode, used=used, style=style, ceiling=ceiling)
            asset["pin_refused"] = f"{pin}: {room_refusal}"
            return asset
        if entry is not None and C.usable(entry, mode):
            pinned = fit_piece(dict(piece, asset_pin=None), _OneModel(catalog, entry), cap, uniform_range, None,
                               design, mode=mode, used=used, style=style, ceiling=ceiling)
            if pinned.get("method") == "library":
                pinned["pinned"] = pin
                # 27 Oct 2026 (pod run 224516, GPU test test_refit_library_models_fit_the_style): the pin records the
                # family of the project's chain its model holds (a minimal model in a scandinavian house: minimal, a
                # style fallback), not the project's family it does not hold; ``pin_off_style`` when it holds none
                chain = style_chain(style_family)
                hit = next((fam for fam in chain if C.styles_match(entry, fam)), None)
                pinned["style_family"] = hit or style_family
                if hit is not None and hit != style_family:
                    pinned["style_fallback"] = {"wanted": style_family, "used": hit, "chain": list(chain),
                                                "why": f"the agent's pinned model {pin}"}
                elif hit is None:
                    pinned["pin_off_style"] = (f"{pin}: its styles {entry.get('styles') or []} hold no family of "
                                               f"{chain}")
                    if style_family:
                        # 27 Oct 2026 (pod run 091638, real06: a classic sofa pinned by the agent in a scandinavian
                        # house): a model of the chain that fits wins over an off-style pin; the pin stays only when
                        # the ranking would build the piece below the library level
                        ranked = fit_piece(dict(piece, asset_pin=None), catalog, cap, uniform_range, style_family,
                                           design, mode=mode, used=used, style=style, ceiling=ceiling)
                        if ranked.get("method") == "library":
                            ranked["pin_refused"] = (f"{pin}: off style ({pinned['pin_off_style'][len(pin) + 2:]}) "
                                                     f"while a model of the style fits ({ranked.get('asset_id')})")
                            return ranked
                pinned["pin_skips_style"] = True
                return pinned
        asset = fit_piece(dict(piece, asset_pin=None), catalog, cap, uniform_range, style_family, design, mode=mode,
                          used=used, style=style, ceiling=ceiling)
        asset["pin_refused"] = (f"{pin}: not a {ftype} model of the catalogue" if entry is None
                                else f"{pin}: {C.unusable_reason(entry, mode)}" if not C.usable(entry, mode)
                                else f"{pin}: fails the fit rules (caps, height"
                                     + (f", at most {ceiling - CEILING_MARGIN_M:.2f} m high under the sloped "
                                        f"ceiling)" if ceiling is not None else ")"))
        return asset
    made = bath_made_fit(piece, style_family, mode, style)
    if made is not None:                   # 29 Oct 2026 (UL114, UL123, UL124): the family's bathroom, made by design
        return made
    candidates = catalog.candidates(ftype)
    if not candidates:
        if ftype == "unknown":
            asset = parametric_fit(piece, f"type {ftype} is parametric in the catalogue", style_family=style_family)
            return _finish(asset, mode, [_step("parametric", "used", "an unknown piece: the parametric box (not built "
                                                                      "unless typed)")])
        if ftype in catalog.parametric_types:              # Milestone 12: parametric only by design (D14)
            reason = f"type {ftype} is parametric in the catalogue"
        else:
            reason = f"no catalogue entry for type {ftype}"
        return _no_model(piece, catalog, reason, [], [], cap, uniform_range, style_family, mode=mode, used=used,
                         style=style, ceiling=ceiling)
    usable, refused = split_usable(candidates, mode)
    if not usable:
        return _no_model(piece, catalog, f"no usable {ftype} model (audit or licence, {mode} mode)", [], refused, cap,
                         uniform_range, style_family, mode=mode, used=used, style=style, ceiling=ceiling)
    chain = style_chain(style_family)
    tried, excluded, reasons = [], list(refused), []
    used = dict(used, type=ftype) if used else used            # the diversity penalty knows the piece's type (sets)
    relaxed_caps = _relaxed_caps(cap, uniform_range)
    for relaxed in (False, True):
        if relaxed and (relaxed_caps is None or not tried):
            break               # the caller's caps hold (tightened, or already as loose); or no candidate was tried
        caps = relaxed_caps if relaxed else (cap, uniform_range)
        for fam in chain:
            got = _fit_family(piece, usable, fam, caps[0], caps[1], design, used=used, within_table=relaxed,
                              ceiling=ceiling, project_family=style_family)
            if got.get("method") == "library":
                got["excluded"] = excluded + got.get("excluded", [])
                # 26 Oct 2026 (fix E): a misfit or a style mix that still won (nothing better fitted) is recorded
                won = next((e for e in usable if e.get("id") == got.get("asset_id")), None)
                flag = taste_flags([won], ftype, piece.get("open_air_room"), style_family, design).get(
                    got.get("asset_id")) if won is not None else None
                if flag:
                    got["taste_flags"] = dict(flag, why="ranked last (misfit) or later (style mix); no better model "
                                                        "fitted the caps")
                if fam != style_family:
                    got["style_fallback"] = {"wanted": style_family, "used": fam, "chain": list(chain),
                                             "why": "; ".join(reasons)}
                if relaxed:
                    got["caps_relaxed"] = {"cap": caps[0], "uniform_range": list(caps[1]),
                                           "why": "no model within the caps; the relaxed caps hold inside the type's "
                                                  "documented ranges (docs/milestone13.md §13.2, ladder step 1)"}
                return _finish(got, mode, [_step("library", f"used {got['asset_id']}",
                                                 "relaxed caps inside the documented ranges" if relaxed else None)])
            if relaxed:          # the strict pass said it all: one short line for the relaxed pass
                why = (f"relaxed caps ({round((caps[0] - 1) * 100)} % non-uniform, {caps[1][0]}..{caps[1][1]} mean "
                       f"scale, inside the documented ranges): no {ftype} candidate either")
            else:
                why = got["fallback_reason"]
            reasons.append(why if fam is None else f"{fam}: {why}")
            seen = {t["id"] for t in tried}
            tried += [t for t in got.get("candidates") or [] if t["id"] not in seen]
            known = {x["id"] for x in excluded}
            excluded += [x for x in got.get("excluded") or [] if x["id"] not in known]
    return _no_model(piece, catalog, "; ".join(reasons) or f"no {ftype} model fits", tried, excluded, cap,
                     uniform_range, style_family, mode=mode, used=used, style=style, ceiling=ceiling)


def _relaxed_caps(cap: float, uniform_range: tuple[float, float]) -> Optional[tuple[float, tuple[float, float]]]:
    """Ladder step 1b (docs/milestone13.md §13.2): the relaxed caps a call may fall back to, ``(cap, range)`` from
    ``RELAXED_CAP`` / ``RELAXED_RANGE`` widened to the caller's where those are looser; None when the caller
    tightened a cap below the module defaults (its limit holds: a test or a tool asked for exactly that) or when the
    caller's caps are already as loose as the relaxed ones."""
    if (cap < NON_UNIFORM_CAP - 1e-9 or uniform_range[0] > UNIFORM_RANGE[0] + 1e-9
            or uniform_range[1] < UNIFORM_RANGE[1] - 1e-9):
        return None
    r_cap = max(cap, RELAXED_CAP)
    r_range = (min(uniform_range[0], RELAXED_RANGE[0]), max(uniform_range[1], RELAXED_RANGE[1]))
    if r_cap <= cap + 1e-9 and r_range[0] >= uniform_range[0] - 1e-9 and r_range[1] <= uniform_range[1] + 1e-9:
        return None
    return r_cap, r_range


# 30 Oct 2026 (lesson UL193, user on real04 run 20261030-112241-full: "I did not like the chair": a bedroom desk's black
# mesh "Physio Approved Ergonomic 2 Lever Office Chair"): a home's desk chair is a residential piece (an upholstered,
# leather or design swivel chair); a corporate task chair (its title: ergonomic, mesh, lever, executive, gaming, big &
# tall, computer, reception) ranks last and is used only when no other desk chair fits; a design classic (Eames, Vitra,
# Herman Miller, Humanscale, Knoll) keeps its rank
CORPORATE_CHAIR_WORDS: tuple[str, ...] = ("ergonomic", "physio", "lever", "mesh", "executive", "gaming", "racing",
                                          "big & tall", "big and tall", "computer", "reception", "guest", "kursi")
DESIGN_CHAIR_WORDS: tuple[str, ...] = ("eames", "vitra", "herman miller", "humanscale", "knoll")


def desk_chair_misfit(entry: dict, ftype: str) -> Optional[str]:
    """Why a desk chair model is a corporate task chair rather than a home's desk chair (None when it is not; UL193)."""
    if ftype != "office_chair":
        return None
    title = _title_of(entry)
    hits = _named(title, CORPORATE_CHAIR_WORDS)
    if not hits or _named(title, DESIGN_CHAIR_WORDS):
        return None
    return f"names {', '.join(dict.fromkeys(hits))}: a corporate task chair, not a home's desk chair (UL193)"


def taste_flags(candidates: list[dict], ftype: str, outdoor: Optional[bool], family: Optional[str],
                design: Optional[dict] = None) -> dict:
    """26 Oct 2026 (fix E): ``{id: {"misfit": reason, "style_mix": [styles]}}`` of the candidates that have either
    (``misfit_of``, ``style_mix_of``; 30 Oct 2026, UL163: a bed's arched headboard, ``headboard_misfit``); the rank
    order reads them (``rank_candidates``)."""
    out = {}
    for e in candidates:
        misfit, mix = misfit_of(e, ftype, outdoor), style_mix_of(e, ftype, family)
        misfit = misfit or headboard_misfit(e, ftype, family, design) or desk_chair_misfit(e, ftype)
        if misfit or mix:
            out[e["id"]] = {"misfit": misfit, "style_mix": mix}
    return out


def _fit_family(piece: dict, candidates: list[dict], style_family: Optional[str], cap: float,
                uniform_range: tuple[float, float], design: Optional[dict], *, used: Optional[dict] = None,
                within_table: bool = False, ceiling: Optional[float] = None, taste=None,
                project_family: Optional[str] = None) -> dict:
    """The fit of one style family on the usable candidates: the bed rule, the style filter, the chaise side, the
    design as a preference (Milestone 13: models that cannot show it are listed under ``excluded`` with the reason
    and still tried after the ones that can), the rank order (``rank_key`` with the diversity penalty ``used``) and
    the caps: the uniform scale to the drawn width within ``uniform_range``, the depth mismatch within ``cap``, the
    height within the real range; with ``within_table`` the fitted box must also lie inside the type's documented
    ranges (the relaxed caps of the ladder). Returns the library ``asset`` or a parametric record whose
    ``fallback_reason`` says why none fitted. Fix round after P6a: with ``ceiling`` the fitted height also stays
    ``CEILING_MARGIN_M`` under it (``under_ceiling``; the candidate records ``under_ceiling``)."""
    ftype = piece["type"]
    width, depth = piece["footprint"]["size"]
    candidates, excluded, reason = usable_candidates(ftype, candidates, style_family)
    if not candidates:
        return parametric_fit(piece, reason, excluded=excluded, style_family=style_family)
    # bathroom sense of 26 Oct 2026 (``use_misfit``): no children's product outside a child's room, no product of
    # another use (a kitchen or utility sink as a washbasin)
    candidates, use_excluded = use_candidates(piece, candidates, project_family or style_family)
    excluded += use_excluded
    if not candidates:
        return parametric_fit(piece, f"no {ftype} model for this room's use (every model is a children's product or "
                                     f"one of another use)", excluded=excluded, style_family=style_family)
    # 28 Oct 2026 (user on real04's roof terrace: "makes no sense to have that table with the carpet outside"): an
    # outdoor type in an open-air room takes only models made for outside (``outdoor_candidates``), a gate, not a rank
    candidates, outdoor_excluded = outdoor_candidates(piece, candidates)
    excluded += outdoor_excluded
    if not candidates:
        return parametric_fit(piece, f"no {ftype} model made for outside (rule {OUTDOOR_ROOM_RULE}: an open-air "
                                     f"room takes outdoor furniture; {len(outdoor_excluded)} indoor model(s) left out)",
                              excluded=excluded, style_family=style_family)
    candidates, round_excluded = round_candidates(piece, candidates)          # UL178
    excluded += round_excluded
    if not candidates:
        return parametric_fit(piece, f"no round {ftype} model (rule {ROUND_TABLE_RULE}: a round drawn table takes a "
                                     f"round model; {len(round_excluded)} other model(s) left out): our round table",
                              excluded=excluded, style_family=style_family)
    if piece.get("shape") == "L":
        candidates, side_excluded, side = chaise_side_candidates(candidates, piece.get("chaise_side"))
        excluded += side_excluded
        if not candidates:
            return parametric_fit(piece, f"no {ftype} model with its chaise on the {side} (library models are not "
                                         "mirrored)", excluded=excluded, style_family=style_family)
    looks: dict[str, dict] = {}
    prefs: dict[str, int] = {}
    if design:
        for e in candidates:
            look, why = look_of(e, ftype, design)
            if look is None:
                excluded.append({"id": e["id"], "reason": why, "preference": True})
                prefs[e["id"]] = 1
            else:
                looks[e["id"]] = look
    taste = taste or (used or {}).get("taste")
    # 26 Oct 2026 (fix E): misfits rank last, a style mix of a dining-group piece takes STYLE_MIX_STEPS (the style
    # family of the project, not the fallback family being tried: ``project_family``)
    flags = taste_flags(candidates, ftype, piece.get("open_air_room"), project_family or style_family, design)
    ordered = rank_candidates(candidates, width, depth, used, prefs, bool(piece.get("open_air_room")), taste, flags)
    tried = []
    heights = real_height_range(ftype)
    for rank, entry in enumerate(ordered, start=1):
        scales, depth_ratio = scale_for(entry, width, depth)
        err = round(C.aspect_error(entry, width, depth), 4)
        mean_scale = round(sum(scales) / 3.0, 4)
        height = round(float(entry["bbox_m"][2]) * scales[2], 4)
        fdepth = fitted_depth(entry, width)
        roof_ok = under_ceiling(height, ceiling)          # fix round after P6a: under a sloped ceiling
        height_ok = height_fits(height, heights) and working_height_ok(ftype, height) and roof_ok \
            and working_top_ok(ftype, height) and fixture_height_ok(ftype, height)
        accepted = (depth_ratio <= cap + 1e-9 and uniform_range[0] <= mean_scale <= uniform_range[1] and height_ok)
        if accepted and within_table:
            from wenart.furniture import sizes as SZ

            accepted = SZ.real_range(ftype) is not None and SZ.oriented_fits(ftype, [width, fdepth, height], 0.0)
        known = units_known(entry)
        size_err = round(size_error(scales), 4)
        tried.append({"id": entry["id"], "aspect_error": err, "scale": scales, "non_uniform": depth_ratio,
                      "depth_m": fdepth, "mean_scale": mean_scale, "accepted": accepted, "rank": rank,
                      "source": entry.get("source"), "units_known": known, "size_error": size_err,
                      "size_bucket": int(size_err / SIZE_BUCKET + 1e-9) if known else None,
                      "diversity_steps": diversity_steps(entry["id"], used), "design_pref": prefs.get(entry["id"], 0),
                      "quality": quality_of(entry), "vision_quality": vision_quality_of(entry),
                      "faces": faces_of(entry), "height_m": height, "height_ok": height_ok})
        if ceiling is not None:
            tried[-1]["under_ceiling"] = roof_ok
        if ftype in SS.SOFT_SEAT_TYPES:              # 30 Oct 2026 (UL131): the model's quality grade
            soft = SS.grade(entry)
            tried[-1]["upholstery"] = soft["grade"]
            if soft["steps"]:
                tried[-1]["upholstery_steps"] = soft["steps"]
        if accepted:
            asset = {
                "library": entry["source"], "asset_id": entry["id"], "licence": entry["licence"],
                "license": entry["licence"], "method": "library", "fit_scale": scales, "scaling": "uniform",
                "bbox_m": [round(width, 4), fdepth, round(entry["bbox_m"][2] * scales[2], 4)],
                "depth_abs_m": round(fdepth - depth, 4),
                "aspect_error": err, "front_axis": entry["front_axis"],
                "up_axis": entry["up_axis"], "origin_offset": list(entry["origin_offset"]),
                "rotation_fix_deg": C.reorient_rotation_deg(entry),
                "front_axis_confidence": entry["front_axis_confidence"], "candidates": tried, "cap": cap,
                "uniform_range": list(uniform_range),
                "styles": list(entry.get("styles") or []), "style_family": style_family, "excluded": excluded,
                "quality": entry.get("quality"), "units_known": known, "ranking": ranking_reasons(tried, tried[-1]),
            }
            if entry["source"] != "polyhaven" and entry.get("glb"):
                asset.update({k: entry[k] for k in GLB_ASSET_FIELDS if k in entry})
                # Catalogue boxes are metres = raw GLB box x unit_scale (the prep pod's unit guess); the
                # scene builder scales the imported mesh by it before fit_scale (blender/furniture.fit_vertices).
                asset["unit_scale"] = float(entry.get("unit_scale") or 1.0)
            else:
                asset["gltf"] = entry["gltf"]
            asset["licence_flag"] = C.licence_flag_of(entry)          # Milestone 13: the flag of the entry
            maps = texture_maps_of(entry)
            if maps is not None:
                asset["texture_maps"] = maps
            if faces_of(entry) is not None:
                asset["faces"] = faces_of(entry)
            for key in AUDIT_ASSET_FIELDS:                      # Milestone 12: the audit and its dressing flags
                if key in entry:
                    asset[key] = entry[key]
            if ftype in SS.SOFT_SEAT_TYPES:                     # 30 Oct 2026 (UL131): the build and M33 read it
                asset["upholstery"] = {k: v for k, v in SS.grade(entry).items() if k != "steps"}
                asset["has_scatter_cushions"] = C.has_scatter_cushions(entry)   # 30 Oct 2026 (UL180): rest.own_cushions
            if piece["type"] in C.BED_TYPES and not C.has_mattress(entry) and is_bed_frame(entry):
                asset.update(bed_frame_record(entry, width, depth, scales[2]))
                asset["bbox_m"][2] = max(asset["bbox_m"][2], asset["bedding"]["top_m"])
            look = looks.get(entry["id"]) or {}
            for key in ("recolour", "colour_match"):
                if look.get(key):
                    asset[key] = look[key]
            if look.get("tags"):
                asset["material_tags_asked"] = look["tags"]
            if design and prefs.get(entry["id"]):
                asset["design_not_shown"] = {k: design[k] for k in ("material_tags", "fabric_colour", "colour")
                                             if design.get(k)}
                asset["design_not_shown_why"] = next((x["reason"] for x in excluded if x["id"] == entry["id"]), None)
            return asset
    best = min(tried, key=lambda t: t["non_uniform"])
    reason = (f"no {ftype} candidate within {round((cap - 1) * 100)} % non-uniform scale (Milestone 13: the depth "
              f"mismatch of the uniform scale to the drawn width) and {uniform_range[0]}..{uniform_range[1]} mean "
              f"scale (closest: {best['id']} at {round((best['non_uniform'] - 1) * 100, 1)} % non-uniform, mean "
              f"scale {best['mean_scale']})")
    too_tall = [t["id"] for t in tried if not t["height_ok"]]
    if too_tall and heights:
        reason += (f"; {len(too_tall)} fitted outside the real height {heights[0]:g}-{heights[1]:g} m "
                   f"(+-{round(HEIGHT_TOLERANCE * 100)} %, wenart.furniture.sizes)")
        if ftype in WORKING_HEIGHT_TYPES:
            reason += f" or the working height (+-{round(WORKING_HEIGHT_TOL * 100)} % of the product height)"
    too_high = [t["id"] for t in tried if t.get("under_ceiling") is False]
    if too_high:
        reason += (f"; {len(too_high)} taller than the {float(ceiling) - CEILING_MARGIN_M:.2f} m the sloped ceiling "
                   f"leaves over the piece ({float(ceiling):.2f} m - {CEILING_MARGIN_M:g} m)")
    if within_table:
        reason += "; the relaxed caps hold only inside the documented ranges"
    return parametric_fit(piece, reason, tried, excluded=excluded, style_family=style_family)


def _step(step: str, result: str, reason: Optional[str] = None) -> dict:
    """One entry of ``asset.ladder`` (docs/milestone13.md §13.2): ``{step, result, reason}``."""
    return {"step": step, "result": result, "reason": reason}


def _finish(asset: dict, mode: str, ladder: list[dict]) -> dict:
    """Milestone 13: the licence fields and the ladder every asset carries (``asset.licence_flag``,
    ``commercial_safe``, ``licence_mode``, ``ladder``); a module or parametric piece is ours (licence ``n/a``, flag
    ``none``), a piece that is not built has nothing to flag."""
    asset["licence_mode"] = mode
    asset["ladder"] = list(asset.get("ladder") or []) + list(ladder)
    if asset.get("method") == "library":
        asset.setdefault("licence_flag", C.licence_flag_of(asset))
        asset["commercial_safe"] = C.commercial_safe(asset)
    else:
        asset.setdefault("licence", PARAMETRIC_LICENCE)
        asset.setdefault("license", PARAMETRIC_LICENCE)
        asset["licence_flag"] = C.NO_FLAG
        asset["commercial_safe"] = True
    return asset


def module_plan_for(piece: dict, style: Optional[dict] = None) -> tuple[Optional[dict], str]:
    """Ladder step 2 (docs/milestone13.md §13.2): ``wenart.blender.modules.module_plan(piece, style)`` (track T2,
    pure) when that module exists and knows a builder for the piece's type; ``(plan, "")`` or ``(None, why)``. The
    import is guarded (the module is built in parallel; a missing one means step 3), and so is a builder error (it
    must not stop the fit: the parametric family follows and the reason is logged)."""
    try:
        from wenart.blender import modules as MOD
    except ImportError as exc:
        return None, f"no module builder (wenart.blender.modules not importable: {exc})"
    fn = getattr(MOD, "module_plan", None)
    if not callable(fn):
        return None, "no module builder (wenart.blender.modules.module_plan missing)"
    try:
        plan = fn(piece, style) if style is not None else fn(piece)
    except Exception as exc:          # noqa: BLE001 - a builder bug is logged, never fatal for the fit
        return None, f"module_plan failed: {type(exc).__name__}: {exc}"
    if not isinstance(plan, dict) or not plan.get("builder"):
        return None, f"no module builder for {piece['type']} (module_plan returned None)"
    return plan, ""


# Fix round after P3 (16-17 Oct 2026, module docstring): the drawn kitchen pieces a kitchen run takes in.
KITCHEN_RUN_HOSTS: tuple[str, ...] = ("kitchen_counter", "kitchen_island")
BUILT_IN_SHARE = 0.60            # a drawn sink or stove with at least this share of its footprint inside a run
BUILT_IN_SINK_TYPES: tuple[str, ...] = ("sink_kitchen",)
RANGE_TYPES: tuple[str, ...] = ("stove",)
PINNED_SINK_GAP_REASON = ("the agent pinned a library model (asset_pin): it stands as drawn in a gap of the run, not "
                          "built in")                   # fix round after P3, part 2


BUILT_IN_MODULE_KINDS: tuple[str, ...] = ("hob", "fridge")   # 26 Oct 2026: solver.built_in_kitchen's modules


def built_in_module(piece: dict) -> Optional[str]:
    """26 Oct 2026: ``hob`` | ``fridge`` for a module the completion built into a kitchen counter
    (``solver.built_in_kitchen``: ``built_into`` names the counter, ``built_in.kind`` the module), else None."""
    rec = piece.get("built_in") if isinstance(piece.get("built_in"), dict) else {}
    kind = rec.get("kind")
    return kind if kind in BUILT_IN_MODULE_KINDS and piece.get("built_into") else None


def _usable_footprint(piece: dict) -> bool:
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else {}
    try:
        return float(fp["size"][0]) > 0 and float(fp["size"][1]) > 0 and len(fp["center"]) >= 2
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def _wall_cabinet_over(pieces: list, piece: dict) -> bool:
    """Whether a built wall cabinet of the piece's room overlaps its footprint in plan (27 Oct 2026: a fridge under
    one stays under the counter)."""
    try:
        from wenart.furniture import placer as PLC
        mine = PLC.drawn_piece(piece).polygon()
    except Exception:  # noqa: BLE001 - no footprint: say yes (the safe under-counter unit)
        return True
    for p in pieces:
        if p.get("type") != "wall_cabinet" or p.get("build", True) is False or p.get("room_id") != piece.get("room_id"):
            continue
        try:
            if PLC.drawn_piece(p).polygon().intersection(mine).area > 0.01:
                return True
        except Exception:  # noqa: BLE001
            continue
    return False


def _column_blocked(pieces: list, column: dict) -> bool:
    """30 Oct 2026 (lesson UL147, the P5 kitchen; real04 run 20261029-201533-full had no tall-unit column: the wall
    cabinets the completion hung over every free run end blocked it): whether the wall cabinets of the column's room
    keep a tall-unit column out. A drawn wall cabinet over it does (the documents decide); a cabinet the completion
    added (``added_by_ai``) does not when at least the narrowest real wall unit (``modules.WALL_RUN_WIDTHS_M``) of it
    stays beside the column: the wall run then stops at the column (``wall_run_hints``: ``column_m``)."""
    try:
        from wenart.furniture import placer as PLC
        from wenart.blender import modules as MOD
        mine = PLC.drawn_piece(column).polygon()
    except Exception:  # noqa: BLE001 - no footprint: blocked (the safe answer of before)
        return True
    for p in pieces:
        if p.get("type") != "wall_cabinet" or p.get("build", True) is False or p.get("room_id") != column.get("room_id"):
            continue
        try:
            poly = PLC.drawn_piece(p).polygon()
            if poly.intersection(mine).area <= 0.01:
                continue
            if p.get("source") == "from_documents":
                return True
            depth = float(p["footprint"]["size"][1]) or 0.35
            left = (poly.area - poly.intersection(mine).area) / depth
        except Exception:  # noqa: BLE001
            return True
        if left < min(MOD.WALL_RUN_WIDTHS_M) - 1e-6:
            return True
    return False


DOOR_SWING_EPS_M2 = 0.01        # 30 Oct 2026: a tall unit overlapping a door's swing or strip by more stands in it


def _in_door_swing(building: dict, piece: dict) -> bool:
    """30 Oct 2026 (UL147): whether a piece's footprint meets the swing or the strip of a door of its room by more
    than ``DOOR_SWING_EPS_M2`` (``placer.room_context`` doors; no room or no geometry: no)."""
    room = next((r for r in building.get("rooms") or [] if r.get("id") == piece.get("room_id")), None)
    if room is None:
        return False
    try:
        from wenart.furniture import placer as PLC
        ctx = PLC.room_context(building, room)
        poly = PLC.drawn_piece(piece).polygon()
    except Exception:  # noqa: BLE001
        return False
    for door in ctx.doors:
        for zone in (door.zone, door.swing):
            if zone is not None and poly.intersection(zone).area > DOOR_SWING_EPS_M2:
                return True
    return False


NESTED_SHARE = 0.90              # 28 Oct 2026: a counter outline this much inside a larger one is part of it


def nested_counters(building: dict) -> dict:
    """28 Oct 2026 (real06: a 0.90 x 0.48 m hob-block outline inside the drawn counter f_L0_031 was built as a second
    kitchen run inside it, with its own wall cabinet): ``{nested id: host id}`` of the built kitchen counters and islands
    whose footprint lies at least ``NESTED_SHARE`` inside a larger built counter or island of their room (an outline
    drawn twice, or a hob or sink outline read as a counter). Pure; without the module builders nothing."""
    try:
        from wenart.blender import modules as MOD
    except ImportError:
        return {}
    runs = [p for p in building.get("furniture") or [] if isinstance(p, dict) and p.get("type") in KITCHEN_RUN_HOSTS
            and p.get("build", True) is not False and _usable_footprint(p)]

    def area(p):
        return float(p["footprint"]["size"][0]) * float(p["footprint"]["size"][1])

    out: dict = {}
    for p in runs:
        hosts = [h for h in runs if h is not p and h.get("room_id") == p.get("room_id")
                 and h.get("level_id") == p.get("level_id") and area(h) > area(p) + 1e-6]
        best = None
        for h in sorted(hosts, key=lambda h: (-area(h), str(h.get("id")))):
            got = MOD.member_in_run(h, p)
            if got is not None and got["share"] >= NESTED_SHARE - 1e-9:
                best = h
                break
        if best is not None:
            out[p["id"]] = best["id"]
    for pid, hid in list(out.items()):        # a host nested in another host: the outermost one holds it
        seen = {pid}
        while hid in out and hid not in seen:
            seen.add(hid)
            hid = out[hid]
        out[pid] = hid
    return out


def kitchen_built_ins(building: dict) -> dict:
    """The kitchen pre-pass of ``fit_building`` (pure; fix round after P3, module docstring): ``{"hints": {run id:
    module hints}, "sinks": {sink id: run id}}``.

    For every kitchen counter or island with ``build`` not false, the pieces of its level and room with ``build``
    not false and at least ``BUILT_IN_SHARE`` of their footprint inside it (``modules.member_in_run``): the largest
    sink (``BUILT_IN_SINK_TYPES``; not one the agent pinned a model to) gives ``sink_pos_m`` (its centre),
    ``sink_w_m`` (its drawn width along the run) and ``sink_piece``; the stoves (``RANGE_TYPES``) give ``ranges``
    (``{id, type, x0_m, x1_m}``: their drawn span along the run). A piece belongs to one run at most. Without the
    module builders (import guarded, as ``module_plan_for``) nothing is found. Fix round after P3, part 2 (17 Oct
    2026): a pinned sink (``asset_pin``) gives a ``ranges`` entry too (``type: sink_kitchen``, ``reason``): the run
    leaves a gap at its drawn span, where its pinned model stands (it is never in ``sinks``). 29 Oct 2026:
    ``details`` holds the kitchen details' hints per run (``kitchen_details_hints``; ``run_hints`` merges them)."""
    out: dict = {"hints": {}, "sinks": {}}
    try:
        from wenart.blender import modules as MOD
    except ImportError:
        return out
    pieces = [p for p in building.get("furniture") or [] if isinstance(p, dict)]
    nested = nested_counters(building)          # 28 Oct 2026: an outline inside a run is part of it, not a run
    runs = [p for p in pieces if p.get("type") in KITCHEN_RUN_HOSTS and p.get("build", True) is not False
            and _usable_footprint(p) and p.get("id") not in nested]
    members = [p for p in pieces if (p.get("type") in BUILT_IN_SINK_TYPES + RANGE_TYPES or built_in_module(p))
               and p.get("build", True) is not False and _usable_footprint(p)]
    claimed: set = set()
    for run in runs:
        sinks, ranges, modules = [], [], []
        for m in members:
            if m.get("id") in claimed or m.get("level_id") != run.get("level_id") \
                    or m.get("room_id") != run.get("room_id"):
                continue
            kind = built_in_module(m)
            if kind and m.get("built_into") != run.get("id"):
                continue                        # 26 Oct 2026: a module the completion built into another run
            got = MOD.member_in_run(run, m)
            if got is None or got["share"] < BUILT_IN_SHARE - 1e-9:
                continue
            if kind:
                # 26 Oct 2026: a hob or an under-counter fridge built into the run; 28 Oct 2026: also when the agent
                # pinned a library model to it (a freestanding model in a run is the defect the user saw)
                modules.append((kind, m, got))
            elif m["type"] in RANGE_TYPES:
                modules.append(("hob", m, got))  # 28 Oct 2026: a drawn stove in a run is the run's hob
            elif m["type"] in BUILT_IN_SINK_TYPES and not m.get("asset_pin"):
                sinks.append((m, got))
            elif m["type"] in BUILT_IN_SINK_TYPES:
                ranges.append((m, got))         # a pinned sink (part 2): a gap, its own model in it
        hints: dict = {}
        for kind, m, got in modules:
            key = "hob" if kind == "hob" else "fridge"
            if f"{key}_piece" in hints:
                if m["type"] in RANGE_TYPES:
                    ranges.append((m, got))     # a second drawn stove in one run keeps the gap of before
                continue                        # one of each per run (the first in building order)
            hints.update({f"{key}_pos_m": [round(float(v), 4) for v in m["footprint"]["center"][:2]],
                          f"{key}_w_m": got["w_m"], f"{key}_piece": m["id"]})
            if kind == "hob":
                hints.update(hob_hints(building, run, m, got, pieces))
            else:
                # 27 Oct 2026: a fridge with no wall cabinet over it may stand as a tall column at a run end;
                # 28 Oct 2026: never in front of a window or a pass-through of the wall behind it
                # 30 Oct 2026 (UL147): a wall cabinet the completion added stops at the column (``_column_blocked``)
                hints["fridge_column"] = not _column_blocked(pieces, m) and not _opening_behind(building, m) \
                    and not _in_door_swing(building, m)
            if m.get("asset_pin"):
                hints.setdefault("pins_not_used", []).append(m["id"])
            out["sinks"][m["id"]] = run["id"]
            claimed.add(m["id"])
        if sinks:
            sink, got = max(sinks, key=lambda mg: (float(mg[0]["footprint"]["size"][0])
                                                   * float(mg[0]["footprint"]["size"][1]), str(mg[0]["id"])))
            hints.update(sink_pos_m=[round(float(v), 4) for v in sink["footprint"]["center"][:2]],
                         sink_w_m=got["w_m"], sink_piece=sink["id"])
            out["sinks"][sink["id"]] = run["id"]
            claimed.add(sink["id"])
        if ranges:
            hints["ranges"] = [dict({"id": m["id"], "type": m["type"], "x0_m": got["x0_m"], "x1_m": got["x1_m"]},
                                    **({"reason": PINNED_SINK_GAP_REASON} if m["type"] in BUILT_IN_SINK_TYPES else {}))
                               for m, got in sorted(ranges, key=lambda mg: (mg[1]["x0_m"], str(mg[0]["id"])))]
            claimed.update(m["id"] for m, _got in ranges)
        outlines = sorted(pid for pid, hid in nested.items() if hid == run.get("id"))
        if outlines:                            # 28 Oct 2026: the counter outlines drawn inside the run
            hints["outlines"] = outlines
            for pid in outlines:
                out["sinks"][pid] = run["id"]
        if hints:
            out["hints"][run["id"]] = hints
    # 29 Oct 2026 (wenart.blender.kitchen_details, K1 and G3): the tall-unit column of each kitchen, the stools' side
    # of each island, the windows behind each counter run (the utensil rail stays off them): ``details`` (merged into
    # a run's hints by ``run_hints``; the plan reads them only with a style)
    out["details"] = {}
    try:
        kitchen_details_hints(building, runs, pieces, out["hints"], out["details"])
    except Exception as exc:  # noqa: BLE001 - a detail that cannot be planned never stops the fit
        out["details_error"] = f"kitchen details not planned: {type(exc).__name__}: {exc}"
    return out


def run_hints(kitchen: dict, piece_id) -> Optional[dict]:
    """A piece's module hints from the kitchen pre-pass (``kitchen_built_ins``): its hints and its kitchen details'
    hints (29 Oct 2026), None when it has neither."""
    got = {**((kitchen.get("hints") or {}).get(piece_id) or {}), **((kitchen.get("details") or {}).get(piece_id) or {})}
    return got or None


# 29 Oct 2026 (wenart.blender.kitchen_details, K1): where a run's end stands
COLUMN_WALL_REACH_M = 0.15       # a wall this far beyond a run's end (its face): the end is against a wall
COLUMN_CORNER_REACH_M = 0.10     # another counter run this close to a run's end: the end is a corner
SEAT_REACH_M = 0.90              # a bar stool this close to an island is one of its seats


def _run_axes(run: dict) -> tuple[tuple[float, float], float, float, float]:
    fp = run["footprint"]
    return ((float(fp["center"][0]), float(fp["center"][1])), float(fp.get("rotation_deg") or 0.0),
            float(fp["size"][0]), float(fp["size"][1]))


def _to_world(c, rot: float, x: float, y: float) -> tuple[float, float]:
    r = math.radians(rot)
    return (c[0] + math.cos(r) * x - math.sin(r) * y, c[1] + math.sin(r) * x + math.cos(r) * y)


def _to_run(c, rot: float, p) -> tuple[float, float]:
    r = math.radians(rot)
    dx, dy = float(p[0]) - c[0], float(p[1]) - c[1]
    return (math.cos(r) * dx + math.sin(r) * dy, -math.sin(r) * dx + math.cos(r) * dy)


def run_end_kind(building: dict, run: dict, runs: list, side: str) -> str:
    """K1: ``corner`` (another counter run of the room meets the end), ``wall`` (a wall of the level runs across the
    end within ``COLUMN_WALL_REACH_M``) or ``open`` for the ``left`` (local -x) or ``right`` end of a run (pure)."""
    from wenart.blender import geom2d

    c, rot, w, d = _run_axes(run)
    sx = -1.0 if side == "left" else 1.0
    pts = [_to_world(c, rot, sx * w / 2.0, y) for y in (-d / 2.0 + 0.02, 0.0, d / 2.0 - 0.02)]
    for o in runs:
        if o is run or o.get("room_id") != run.get("room_id") or o.get("level_id") != run.get("level_id"):
            continue
        oc, orot, ow, od = _run_axes(o)
        if min(geom2d.distance_to_rect(p, oc, (ow, od), orot) for p in pts) <= COLUMN_CORNER_REACH_M + 1e-9:
            return "corner"
    ax = (math.cos(math.radians(rot)), math.sin(math.radians(rot)))
    mid = pts[1]
    for wall in building.get("walls") or []:
        if wall.get("level_id") != run.get("level_id"):
            continue
        (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-6 or abs(((x1 - x0) * ax[0] + (y1 - y0) * ax[1]) / length) > 0.5:
            continue                                     # the wall must run across the run's axis
        from wenart import geometry as G
        if G.point_segment_distance(mid, (x0, y0), (x1, y1)) <= float(wall.get("thickness") or 0.2) / 2.0 \
                + COLUMN_WALL_REACH_M:
            return "wall"
    return "open"


def run_end_meets(building: dict, run: dict, runs: list, side: str) -> str:
    """30 Oct 2026 (UL155, K16): ``run_end_kind`` with a ``corner`` whose other run goes on along the same line (a
    run drawn in two pieces) told apart as ``join`` (pure): a dishwasher's door may open at a join, not into a
    corner."""
    from wenart.blender import geom2d

    kind = run_end_kind(building, run, runs, side)
    if kind != "corner":
        return kind
    c, rot, w, d = _run_axes(run)
    sx = -1.0 if side == "left" else 1.0
    pts = [_to_world(c, rot, sx * w / 2.0, y) for y in (-d / 2.0 + 0.02, 0.0, d / 2.0 - 0.02)]
    for o in runs:
        if o is run or o.get("room_id") != run.get("room_id") or o.get("level_id") != run.get("level_id"):
            continue
        oc, orot, ow, od = _run_axes(o)
        if min(geom2d.distance_to_rect(p, oc, (ow, od), orot) for p in pts) <= COLUMN_CORNER_REACH_M + 1e-9 \
                and abs(math.sin(math.radians(orot - rot))) > 0.5:
            return "corner"
    return "join"


def _taken_spans(c, rot: float, hints: dict) -> list[tuple[float, float, str]]:
    """The spans a run's sink, hob, drawn stoves and fridge take (the run's frame, a unit's widest real width)."""
    out = []
    if hints.get("sink_pos_m"):
        x = _to_run(c, rot, hints["sink_pos_m"])[0]
        out.append((x - 0.45, x + 0.45, "sink"))
    if hints.get("hob_span_m"):
        out.append((float(hints["hob_span_m"][0]), float(hints["hob_span_m"][1]), "hob"))
    elif hints.get("hob_pos_m"):
        x = _to_run(c, rot, hints["hob_pos_m"])[0]
        out.append((x - 0.45, x + 0.45, "hob"))
    for r in hints.get("ranges") or []:
        out.append((float(r["x0_m"]), float(r["x1_m"]), "range"))
    if hints.get("fridge_pos_m"):
        x = _to_run(c, rot, hints["fridge_pos_m"])[0]
        out.append((x - 0.30, x + 0.30, "fridge"))
    return out


def kitchen_details_hints(building: dict, runs: list, pieces: list, hints_by_run: dict, details: dict) -> None:
    """29 Oct 2026 (wenart.blender.kitchen_details; in place on ``details``, ``{run id: hints}``, reading the runs'
    ``hints_by_run`` of the pre-pass): per kitchen (the runs of one room) the tall-unit column (K1): the counter run end
    that is no corner, has no window, door or pass-through by it (``openings_behind``), no drawn wall cabinet over it
    (an added one stops at the column, 30 Oct 2026: ``_column_blocked``) and
    room for the units beside the sink and the hob (a wall end first, the longer run first): ``column`` = ``{"end",
    "kinds", "top_m", "why", "trim_m"?}`` (an oven tower, and a fridge when the kitchen has no drawn or full-height one:
    a French-door fridge in a run from ``COLUMN["french_from_run_m"]``; 30 Oct 2026, UL187: an added under-counter or
    lone fridge moves into it, its run's fridge hints cleared (``fridge_moved``); a run end in a door swing stops
    ``trim_m`` short of it, ``_swing_trim``); with the ovens in the column the hob's run gets ``oven_in_column``; no end free and
    no fridge in the kitchen: an under-counter fridge (``fridge_x_m``, ``fridge_why``) in the longest run. Per island
    ``seat_side`` (``back`` / ``front``: the bar stools' side, G3); per counter run ``windows_m`` (the windows and
    pass-throughs behind it, the run's frame: the utensil rail stays off them) and ``end_kinds`` (30 Oct 2026, UL155:
    what meets each end, ``run_end_meets``; the dishwasher beside the sink never opens into a corner)."""
    from wenart.blender import kitchen_details as KD

    def mine(run_id: str) -> dict:
        return details.setdefault(run_id, {})

    def given(run_id: str) -> dict:
        return {**(hints_by_run.get(run_id) or {}), **(details.get(run_id) or {})}

    by_room: dict = {}
    for run in runs:
        by_room.setdefault((run.get("level_id"), run.get("room_id")), []).append(run)
    for (_lv, room_id), room_runs in sorted(by_room.items(), key=lambda kv: str(kv[0])):
        room_pieces = [p for p in pieces if p.get("room_id") == room_id and p.get("build", True) is not False]
        # 30 Oct 2026 (lesson UL187): the kitchen's full-size fridge. An under-counter fridge the completion built into a
        # run, or a lone fridge column it stood at a run end, is ours to move: the tall-unit column takes the fridge
        # (beside the oven tower) and the run's unit becomes a cupboard; a drawn fridge, or a full-height one standing
        # on its own, keeps its place
        movable = {str(given(r["id"]).get("fridge_piece")) for r in room_runs if given(r["id"]).get("fridge_piece")}
        movable = {pid for pid in movable if any(p.get("id") == pid and p.get("source") != "from_documents"
                                                 for p in room_pieces)}
        has_fridge = any(p.get("type") == "fridge" and p.get("id") not in movable
                         and (p.get("source") == "from_documents" or _fridge_full(p)) for p in room_pieces)
        for run in room_runs:                               # the windows behind a counter run, the stools' side
            c, rot, w, d = _run_axes(run)
            if run.get("type") == "kitchen_island":
                sides = []
                for s in room_pieces:
                    if s.get("type") != "bar_stool" or not s.get("footprint"):
                        continue
                    lx, ly = _to_run(c, rot, s["footprint"]["center"])
                    if abs(lx) <= w / 2.0 + 0.2 and d / 2.0 - 0.3 < abs(ly) <= d / 2.0 + SEAT_REACH_M:
                        sides.append("back" if ly > 0 else "front")
                if sides:
                    mine(run["id"])["seat_side"] = max(("back", "front"), key=sides.count)
                continue
            spans = []
            for o in openings_behind(building, run, ("window", "opening")):
                half = float(o.get("width") or 0.9) / 2.0
                x = _to_run(c, rot, o["center"])[0]
                spans.append([round(x - half - 0.05, 4), round(x + half + 0.05, 4)])
            if spans:
                mine(run["id"])["windows_m"] = spans
            # 30 Oct 2026 (UL155, K16): what meets each end (the dishwasher's side beside the sink: never a corner)
            if run.get("type") == "kitchen_counter":
                mine(run["id"])["end_kinds"] = {
                    side: run_end_meets(building, run, [r for r in room_runs if r.get("type") == "kitchen_counter"],
                                        side) for side in ("left", "right")}
        counters = [r for r in room_runs if r.get("type") == "kitchen_counter"]
        best = None
        kind_sets = ([["oven_tower"]] if has_fridge else [["fridge", "oven_tower"], ["fridge"], ["oven_tower"]])
        for run in counters:
            c, rot, w, d = _run_axes(run)
            h = given(run["id"])
            if h.get("fridge_column"):
                continue                                    # its fridge column (27 Oct 2026) stands at an end
            taken = _taken_spans(c, rot, h)
            for rank, kinds in enumerate(kind_sets):
                names = [("fridge_french" if w >= KD.COLUMN["french_from_run_m"] - 1e-9 else "fridge_column")
                         if k == "fridge" else k for k in kinds]
                tw = sum(wd for _k, wd in KD.column_widths(names))
                if w - tw < KD.COLUMN["rest_min_m"] - 1e-9:
                    continue
                for side in ("left", "right"):
                    end = run_end_kind(building, run, counters, side)
                    if end == "corner":
                        continue
                    lo, hi = (-w / 2.0, -w / 2.0 + tw) if side == "left" else (w / 2.0 - tw, w / 2.0)
                    if any(lo < t1 + KD.COLUMN["clear_m"] and hi > t0 - KD.COLUMN["clear_m"] for t0, t1, _k in taken):
                        continue
                    cx, cy = _to_world(c, rot, (lo + hi) / 2.0, 0.0)
                    col = {"id": f"{run['id']}#column", "type": "tall_cabinet", "level_id": run.get("level_id"),
                           "room_id": run.get("room_id"),
                           "footprint": {"center": [cx, cy], "size": [tw, d], "rotation_deg": rot}}
                    # 30 Oct 2026 (UL147): an added wall cabinet over the end stops at the column instead; a column
                    # never stands in a door's swing or its strip (real04's only free run end: the drawn counter's end
                    # lay 0.19 m2 in the door swing of d_L-1_003)
                    if openings_behind(building, col, ("window", "opening", "door")) or _column_blocked(pieces, col):
                        continue
                    trim = 0.0
                    if _in_door_swing(building, col):
                        # 30 Oct 2026 (UL187, user: "maybe by shortening the table"): a run end in a door swing is a
                        # drawing error the code may fix (CLAUDE.md: at most 0.5 m): the run stops short of the swing
                        # and the column stands at its new end
                        trim = _swing_trim(building, run, side, tw, w - KD.COLUMN["rest_min_m"], taken)
                        if trim is None:
                            continue
                    key = (rank, 0 if end == "wall" else 1, trim > 0.0, -w, str(run["id"]), side)
                    if best is None or key < best[0]:
                        best = (key, run, side, names, end, trim)
        fridge_in_column = False
        if best is not None:
            _key, run, side, names, end, trim = best
            top = _ceiling_over(building, run)
            why = (f"a tall-unit column at the {end} end of {run['id']} ({', '.join(n.replace('_', ' ') for n in names)}"
                   f"): the kitchen has room for it (K1, UL118)" + ("" if has_fridge else (
                       "; the kitchen's full-size fridge stands in it beside the oven tower, its under-counter or lone "
                       "fridge moved there (UL187)" if movable else "; the kitchen had no fridge")))
            if trim > 0.0:
                why += (f"; the run stops {trim:.2f} m short of its drawn {side} end, which lay in a door swing (the "
                        f"drawn footprint kept; UL187)")
            mine(run["id"])["column"] = {"end": side, "kinds": names, "why": why,
                                         **({"top_m": top} if top is not None else {}),
                                         **({"trim_m": round(trim, 4)} if trim > 0.0 else {})}
            fridge_in_column = any(n.startswith("fridge") for n in names)
            if fridge_in_column:
                for r in room_runs:                         # UL187: one full-size fridge per kitchen
                    rh = given(r["id"])
                    if str(rh.get("fridge_piece")) in movable:
                        mine(r["id"]).update(fridge_pos_m=None, fridge_x_m=None, fridge_column=False,
                                             fridge_moved=(f"the fridge {rh['fridge_piece']} stands in the tall-unit "
                                                           f"column of {run['id']} (UL187): its unit is a cupboard"))
            if "oven_tower" in names:
                for r in room_runs:
                    rh = given(r["id"])
                    if rh.get("hob_piece") or rh.get("hob_span_m"):
                        mine(r["id"])["oven_in_column"] = True
        for run in counters:                               # the 27 Oct fridge column: its fronts to the ceiling too
            h = given(run["id"])
            if h.get("fridge_column") and "column" not in h:
                top = _ceiling_over(building, run)
                if top is not None:
                    mine(run["id"])["column"] = {"end": None, "kinds": [], "top_m": top,
                                                 "why": "the fridge column's fronts to the ceiling (K1)"}
        if has_fridge or movable or fridge_in_column or not counters:
            continue
        # no fridge in the kitchen and no column end free: an under-counter fridge in the longest run (K1)
        for run in sorted(counters, key=lambda r: (-float(r["footprint"]["size"][0]), str(r["id"]))):
            c, rot, w, d = _run_axes(run)
            taken = _taken_spans(c, rot, given(run["id"]))
            spots = []
            for side in ("left", "right"):
                if run_end_kind(building, run, counters, side) == "corner":
                    continue
                for k in range(int(max(0.0, w - 0.6) / 0.05) + 1):
                    x = (-w / 2.0 + 0.30 + k * 0.05) if side == "left" else (w / 2.0 - 0.30 - k * 0.05)
                    if not any(x - 0.30 < t1 and x + 0.30 > t0 for t0, t1, _k in taken):
                        spots.append((k, side, x))
                        break
            if spots:
                _k, _side, x = min(spots)
                mine(run["id"]).update(fridge_x_m=round(x, 4), fridge_why=(
                    "an under-counter fridge built into the run: the kitchen had no fridge and no run end was free "
                    "for a fridge column (K1)"))
                break
    for rid in [k for k, v in details.items() if not v]:
        del details[rid]


# 30 Oct 2026 (lesson UL187): a fridge this tall is the kitchen's full-size fridge (an under-counter one is 0.82 m)
FRIDGE_FULL_M = 1.50
SWING_TRIM_MAX_M = 0.50          # CLAUDE.md: fixed equipment moves at most 0.5 m out of a door swing
SWING_TRIM_STEP_M = 0.05


def _fridge_full(piece: dict) -> bool:
    """Whether a fridge piece is a full-size fridge (UL187): its height, or its model's, from ``FRIDGE_FULL_M``."""
    h = piece.get("height")
    if not isinstance(h, (int, float)):
        asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
        bbox = asset.get("bbox_m")
        h = bbox[2] if isinstance(bbox, list) and len(bbox) > 2 else None
    return isinstance(h, (int, float)) and float(h) >= FRIDGE_FULL_M - 1e-9


def _swing_trim(building: dict, run: dict, side: str, tw: float, room_m: float, taken: list) -> Optional[float]:
    """UL187: how far a run's ``side`` end stops short (``SWING_TRIM_STEP_M`` steps up to ``SWING_TRIM_MAX_M``) so a
    column of width ``tw`` at its new end stands clear of every door swing and strip of its room, the column and the
    trim within ``room_m`` and ``COLUMN["clear_m"]`` off the taken spans; None when no such trim exists."""
    from wenart.blender import kitchen_details as KD

    c, rot, w, d = _run_axes(run)
    k = 1
    while k * SWING_TRIM_STEP_M <= SWING_TRIM_MAX_M + 1e-9:
        t = k * SWING_TRIM_STEP_M
        k += 1
        if tw + t > room_m + 1e-9:
            return None
        lo, hi = (-w / 2.0 + t, -w / 2.0 + t + tw) if side == "left" else (w / 2.0 - t - tw, w / 2.0 - t)
        if any(lo < t1 + KD.COLUMN["clear_m"] and hi > t0 - KD.COLUMN["clear_m"] for t0, t1, _k in taken):
            return None
        cx, cy = _to_world(c, rot, (lo + hi) / 2.0, 0.0)
        col = {"id": f"{run['id']}#column", "type": "tall_cabinet", "level_id": run.get("level_id"),
               "room_id": run.get("room_id"), "footprint": {"center": [cx, cy], "size": [tw, d], "rotation_deg": rot}}
        if not _in_door_swing(building, col):
            return round(t, 4)
    return None


def _opening_behind(building: dict, piece: dict) -> bool:
    """28 Oct 2026 (real06: the fridge beside the run under the 2.9 m pass-through): whether a window or a doorless
    opening of the piece's level stands in the wall behind it over its width (``_window_cap``'s rule: the wall line
    within ``WINDOW_FRONT_M``, overlapping it by ``WINDOW_OVERLAP_M``), so no tall unit may stand there."""
    try:
        return bool(openings_behind(building, piece, ("window", "opening")))
    except Exception:  # noqa: BLE001 - no geometry: say no
        return False


def _ceiling_over(building: dict, piece: dict) -> Optional[float]:
    """28 Oct 2026: the ceiling over a piece's floor (its level's ``ceiling_height`` less the room's floor offset; the
    sloped ceiling over its footprint when lower: ``piece_ceiling``), None when the level has none."""
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == piece.get("level_id")), None)
    room = next((r for r in building.get("rooms") or [] if r.get("id") == piece.get("room_id")), None)
    flat = None
    if level is not None and isinstance(level.get("ceiling_height"), (int, float)):
        flat = float(level["ceiling_height"]) - float((room or {}).get("floor_offset_m") or 0.0)
    try:
        slope = piece_ceiling(building, piece)
    except Exception:  # noqa: BLE001 - a roof that cannot be read: the flat ceiling
        slope = None
    vals = [v for v in (flat, slope) if v is not None]
    return round(min(vals), 4) if vals else None


def hob_hints(building: dict, run: dict, hob: dict, got: dict, pieces: list) -> dict:
    """28 Oct 2026 (module docstring "Kitchen design"): the module hints of the hob a run holds: ``oven`` (the
    completion's record; a drawn hob: the run at least ``groups.yaml`` ``oven_min_depth`` deep), ``hob_span_m`` (a
    drawn hob keeps its drawn span along the run: the fixed-equipment rule), the cooker hood: ``hood_kind`` (an island
    hood over an island, an under-cabinet hood under a wall cabinet hung over the hob, else a chimney hood),
    ``hood_under_m`` (that cabinet's bottom), ``hood_top_m`` (the ceiling over the run, ``_ceiling_over``)."""
    out: dict = {}
    rec = hob.get("built_in") if isinstance(hob.get("built_in"), dict) else {}
    if built_in_module(hob):
        out["oven"] = bool(rec.get("oven"))
    else:
        depth = float(run["footprint"]["size"][1])
        try:
            from wenart.furniture import groups as GR
            need = float((((GR.load_groups().get("kitchen_run") or {}).get("run") or {}).get("built_in") or {})
                         .get("hob", {}).get("oven_min_depth") or 0.55)
        except Exception:  # noqa: BLE001 - the table's default
            need = 0.55
        out["oven"] = depth >= need - 1e-9
        out["hob_span_m"] = [got["x0_m"], got["x1_m"]]
    over = [p for p in pieces if p.get("type") == "wall_cabinet" and p.get("build", True) is not False
            and p.get("room_id") == hob.get("room_id") and _wall_cabinet_over([p], hob)]
    if run.get("type") == "kitchen_island":
        out["hood_kind"] = "island"
    elif over:
        out["hood_kind"] = "under_cabinet"
        try:
            from wenart.blender.proxies import mount_bottom
            out["hood_under_m"] = round(min(float(mount_bottom(p)[0]) for p in over), 4)
        except Exception:  # noqa: BLE001 - the rule's bottom
            out["hood_under_m"] = 1.45
    else:
        out["hood_kind"] = "chimney"
    top = _ceiling_over(building, run)
    if top is not None:
        out["hood_top_m"] = top
    return out


def wall_run_hints(cabinet: dict, run: Optional[dict], building: Optional[dict] = None) -> dict:
    """28 Oct 2026 (module docstring "Kitchen design"): the module hints of a wall cabinet hung over a fitted kitchen
    run: ``ends`` (the completion's ``rule.ends``), ``joints_m`` (the joints of the run's base units and fillers, its
    hob unit's sides among them, in the cabinet's own frame: ``modules.plan_wall_run`` lines the wall units up with
    them). Without the run's module plan only the ends. 30 Oct 2026 (lesson UL147, the P5 kitchen): ``column_m``, the
    spans of the run's tall units under the cabinet (the wall run stops at them: a hard end), and ``ceiling_m``, the
    ceiling over the cabinet (``_ceiling_over``; the uppers of the families with ``uppers_to_ceiling`` reach it)."""
    rule = cabinet.get("rule") if isinstance(cabinet.get("rule"), dict) else {}
    out: dict = {"ends": list(rule.get("ends") or ["open", "open"])}
    if building is not None:
        top = _ceiling_over(building, cabinet)
        if top is not None:
            out["ceiling_m"] = top
    plan = ((run or {}).get("asset") or {}).get("module_plan") or {}
    if plan.get("builder") != "kitchen_run":
        return out
    rfp, cfp = run["footprint"], cabinet["footprint"]
    rr, cr = math.radians(float(rfp.get("rotation_deg") or 0.0)), math.radians(float(cfp.get("rotation_deg") or 0.0))
    rc, cc = [float(v) for v in rfp["center"][:2]], [float(v) for v in cfp["center"][:2]]
    ux, uy = math.cos(cr), math.sin(cr)
    if abs(math.cos(rr) * ux + math.sin(rr) * uy) < 0.99:
        return out                                     # the cabinet does not run along this run
    joints = set()
    half = float(cfp["size"][0]) / 2.0
    columns = []
    for m in plan.get("modules") or []:
        if m.get("kind") not in ("base_unit", "filler", "tall_unit"):
            continue
        ends = []
        for x in (float(m["pos_m"][0]) - float(m["size_m"][0]) / 2.0, float(m["pos_m"][0]) + float(m["size_m"][0]) / 2.0):
            wx, wy = rc[0] + math.cos(rr) * x, rc[1] + math.sin(rr) * x
            ends.append(round((wx - cc[0]) * ux + (wy - cc[1]) * uy, 4))
            joints.add(ends[-1])
        lo, hi = min(ends), max(ends)
        if m.get("kind") == "tall_unit" and lo < half - 1e-6 and hi > -half + 1e-6:
            columns.append([round(max(lo, -half), 4), round(min(hi, half), 4)])
    out["joints_m"] = sorted(j for j in joints if -half - 0.01 <= j <= half + 0.01)
    if columns:
        out["column_m"] = sorted(columns)
    return out


def wall_cabinet_run(building: dict, cabinet: dict) -> Optional[dict]:
    """28 Oct 2026: the kitchen run a wall cabinet hangs over: the completion's ``rule.run``, else (a drawn cabinet)
    the built counter of its room whose footprint it overlaps most in plan; None without one."""
    pieces = [p for p in building.get("furniture") or [] if isinstance(p, dict)]
    named = (cabinet.get("rule") or {}).get("run") if isinstance(cabinet.get("rule"), dict) else None
    host = next((p for p in pieces if p.get("id") == named and p.get("type") in KITCHEN_RUN_HOSTS), None)
    if host is not None or not _usable_footprint(cabinet):
        return host
    try:
        from wenart.furniture import placer as PLC
        mine = PLC.drawn_piece(cabinet).polygon()
    except Exception:  # noqa: BLE001
        return None
    best = (0.01, None)
    for p in pieces:
        if p.get("type") not in KITCHEN_RUN_HOSTS or p.get("room_id") != cabinet.get("room_id") \
                or p.get("build", True) is False or not _usable_footprint(p):
            continue
        try:
            area = PLC.drawn_piece(p).polygon().intersection(mine).area
        except Exception:  # noqa: BLE001
            continue
        if area > best[0]:
            best = (area, p)
    return best[1]


def holds_built_in(run: Optional[dict], piece_id: str) -> bool:
    """True when ``run``'s fitted module plan builds ``piece_id`` into it (``plan["built_ins"]``)."""
    plan = ((run or {}).get("asset") or {}).get("module_plan") or {}
    return any(b.get("id") == piece_id for b in plan.get("built_ins") or [] if isinstance(b, dict))


def _bowl_across_text(shift_y: float) -> str:
    """The words for a built-in bowl's offset across its run (fix round after P3, part 3; as
    ``modules.sink_across_text``): ``shift_y`` is the bowl's local y (the run's centreline) minus the drawn centre's."""
    return (f"the bowl stands {abs(shift_y):.2f} m {'behind' if shift_y > 0 else 'in front of'} the drawn sink centre, "
            "on the run's centreline")


def built_in_fit(piece: dict, run: dict, mode: str, style_family: Optional[str] = None) -> dict:
    """The asset of a drawn sink built into a kitchen run (fix round after P3): ``method: module``, the run's
    ``asset_id`` (``module:<run type>:kitchen_run``), ``built_in: <run id>``, ours (licence ``n/a``, flag ``none``,
    commercial-safe), by design; ``module_plan`` is only the reference ``{builder, built_into, kind, x_m, w_m}`` (no
    modules: the run's plan builds it, ``parametric.piece_bbox`` keeps the sink's own box); the ladder ends at the
    module step. No library model is searched (none would be built). Fix round after P3, part 3 (17 Oct 2026): the
    reference also carries ``shift_m`` and ``shift_y_m`` (the bowl's offset along and across the run from the drawn
    centre, ``built_ins`` of the run's plan) and the reason names both when they are over 5 mm."""
    plan = (run.get("asset") or {}).get("module_plan") or {}
    record = next((b for b in plan.get("built_ins") or [] if b.get("id") == piece["id"]), {})
    builder = plan.get("builder") or "kitchen_run"
    shift = float(record.get("shift_m") or 0.0)
    across = float(record.get("shift_y_m") or 0.0)
    kind = record.get("kind") or "sink"
    if kind in BUILT_IN_MODULE_KINDS:
        # 26 Oct 2026: a hob (with its oven) or an under-counter fridge the completion built into the run;
        # 28 Oct 2026: a drawn stove in the run is its hob unit (at its drawn span), with the hood over it
        what = ("hob unit with the hob plate on the worktop" + (" and an oven under it" if record.get("oven") else "")
                + (f", a {record['hood'].replace('_', '-')} hood over it" if record.get("hood") else "")
                if kind == "hob" else "fridge-freezer column at the run's end" if record.get("column")
                else "under-counter fridge unit with an appliance door")
        how = ("the drawn stove stands in the counter run: a hob set into the worktop, never a freestanding cooker "
               "(kitchen design rule of 28 Oct 2026), at its drawn span" if built_in_module(piece) is None else
               "the completion built it into the counter: solver.built_in_kitchen")
        why = (f"built into the kitchen run {run['id']}: a {float(record.get('w_m') or 0.0):.2f} m {what} ({how})"
               + (f"; the unit stands {abs(shift):.2f} m from the piece's centre" if abs(shift) > 0.005 else "")
               + (f"; the pinned model {piece['asset_pin']} is not used (a freestanding model in a counter run)"
                  if piece.get("asset_pin") else ""))
        step = f"built into {run['id']} ({'hob unit' if kind == 'hob' else 'fridge unit'})"
    elif kind == "outline":
        # 28 Oct 2026: a counter outline drawn inside a larger run (``nested_counters``) is part of that run
        why = (f"part of the kitchen run {run['id']}: its outline lies inside that run (an outline drawn twice, or a hob "
               "or sink block's outline read as a counter); no second run is built inside it")
        step = f"part of {run['id']} (outline inside the run)"
    else:
        why = (f"built into the kitchen run {run['id']}: a {float(record.get('w_m') or 0.0):.2f} m sink unit with "
               "the bowl and the tap at its cutout (the drawn sink lies inside the drawn run)"
               # fix round after P3, part 2: a unit off the drawn centre (at most modules.KITCHEN_END_SHIFT_MAX_M)
               + (f"; the unit stands {abs(shift):.2f} m from the drawn sink centre (unit width, run end)"
                  if abs(shift) > 0.005 else "")
               # part 3: and the bowl's offset across the run (it stands on the run's centreline)
               + (f"; {_bowl_across_text(across)}" if abs(across) > 0.005 else ""))
        step = f"built into {run['id']} (sink unit and cutout)"
    asset = parametric_fit(piece, why, style_family=style_family)
    asset.update({"library": MODULE_METHOD, "method": MODULE_METHOD, "asset_id": f"module:{run['type']}:{builder}",
                  "built_in": run["id"], "by_design": True,
                  "module_plan": {"builder": builder, "built_into": run["id"], "kind": kind,
                                  "x_m": record.get("x_m"), "w_m": record.get("w_m"),
                                  "shift_m": round(shift, 4), "shift_y_m": round(across, 4) + 0.0}})
    return _finish(asset, mode, [_step("library", "not tried", why), _step(MODULE_METHOD, step, None)])


def bath_made_fit(piece: dict, style_family: Optional[str], mode: str, style: Optional[dict] = None
                  ) -> Optional[dict]:
    """29 Oct 2026 (lessons UL114, UL123, UL124; ``wenart.furniture.bath_details``): the asset of a bathroom piece the
    layout stage made to measure for its style family (``bath_look.made_to_measure``: a wall-hung WC, a floating
    vanity, an open lit niche column, a walk-in shower): built from code by design on its drawn footprint (a vanity
    or a shower by the bath set module, a WC or a column by the parametric builder), never a library model; it records
    a ``library_gap`` (no audited model of that design) so the report lists it. None for any other piece."""
    from wenart.blender import bath_parts as BT

    made = BT.made_to_measure(piece)
    if made is None:
        return None
    look = BT.bath_look(piece)
    what = {"wc": "wall-hung WC with its flush plate", "vanity": f"{look.get('vanity')} floating vanity",
            "column": "open lit niche column", "shower": "walk-in shower"}[made]
    reason = (f"the {look.get('family') or style_family or 'project'} family's bathroom (UL114): our {what}, made to "
              f"measure on the drawn footprint (bath_details); no library model is searched")
    ladder = [_step("library", "not tried", reason)]
    if made in ("vanity", "shower"):
        plan, why = module_plan_for(piece, style)
        if plan is not None:
            asset = module_fit(piece, plan, reason, [], [], style_family)
            asset["by_design"] = True
            asset["library_gap"] = {"type": piece["type"], "style": style_family, "step": MODULE_METHOD,
                                    "used": f"module builder bath_set ({what}, by design)", "reason": reason}
            asset["bath_made"] = made
            ladder.append(_step(MODULE_METHOD, f"used {plan['builder']} ({what})", None))
            return _finish(asset, mode, ladder)
        ladder.append(_step(MODULE_METHOD, "no module builder", why))
    asset = parametric_fit(piece, reason, [], [], style_family)
    asset["by_design"] = True
    asset["bath_made"] = made
    asset["library_gap"] = {"type": piece["type"], "style": style_family, "step": "parametric",
                            "used": f"our parametric {what} (by design)", "reason": reason}
    ladder.append(_step("parametric", "used (by design)", reason))
    return _finish(asset, mode, ladder)


def module_fit(piece: dict, plan: dict, reason: str, candidates: Optional[list] = None,
               excluded: Optional[list] = None, style_family: Optional[str] = None) -> dict:
    """Ladder step 2: the asset of a piece built from modules (``method: module``, ``module_plan`` for the scene
    builder's ``build_module``; the box from the plan's ``footprint_m`` / ``height_m``). A by-design type (a kitchen
    run, a vanity: ``catalog.BY_DESIGN_PARAMETRIC_TYPES``) is ``by_design`` and, as its parametric twin, a
    ``library_gap`` only when it is a fixture type or models were tried (a counter run is made to the drawing, never
    a gap); every other type is a gap at the module step (listed as built below the library level)."""
    ftype = piece["type"]
    base = parametric_fit(piece, reason, candidates, excluded, style_family)
    fp = plan.get("footprint_m") or piece["footprint"]["size"][:2]
    height = plan.get("height_m") or base["bbox_m"][2]
    products = [str(p) for p in plan.get("products") or []]
    base.update({"library": MODULE_METHOD, "asset_id": f"module:{ftype}:{plan['builder']}", "method": MODULE_METHOD,
                 "bbox_m": [round(float(fp[0]), 4), round(float(fp[1]), 4), round(float(height), 4)],
                 "module_plan": plan})
    by_design = ftype in C.BY_DESIGN_PARAMETRIC_TYPES
    if by_design:
        base["by_design"] = True
    label = split_label(piece, plan)
    if label is not None:
        base["adjusted_by_ai"] = label
    if not by_design or ftype in C.PARAMETRIC_FIXTURE_TYPES or candidates or excluded:
        base["library_gap"] = {"type": ftype, "style": style_family, "step": MODULE_METHOD,
                               "used": f"module builder {plan['builder']} ({len(plan.get('modules') or [])} "
                                       f"module(s){': ' + ', '.join(products) if products else ''})"
                                       + (" (by design)" if by_design else ""),
                               "reason": reason}
    return base


SPLIT_RULE = "module_split"


def split_label(piece: dict, plan: dict) -> Optional[dict]:
    """The ``adjusted_by_ai`` label of a module plan with a ``split`` (``wenart.blender.modules.plan_table_long``: a
    drawn footprint deeper than a real table includes its chairs; pure, None without a split): the reason names the
    drawing error, the table and the chairs built inside the drawn box; ``drawn_footprint`` holds the footprint as
    drawn (the piece's footprint is not changed: the modules sit inside it), ``changed`` is empty for that reason.
    ``fit_building`` copies it onto the piece (``apply_split_label``; CLAUDE.md furniture rules: every change keeps
    the ``drawn_*`` keys and is labelled ``adjusted_by_ai`` with the reason)."""
    split = plan.get("split") if isinstance(plan, dict) else None
    if not isinstance(split, dict):
        return None
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else {}
    size = [float(v) for v in (fp.get("size") or [])[:2]]
    table = [float(v) for v in (split.get("table_m") or size)[:2]]
    chairs = int(split.get("chairs") or 0)
    why = str(split.get("reason") or "the drawn footprint is deeper than a real table")
    reason = (f"module split: {why}; built as a {table[0]:.2f} x {table[1]:.2f} m table"
              + (f" with {chairs} chairs" if chairs else "")
              + f" inside the drawn {size[0]:.2f} x {size[1]:.2f} m footprint ({plan.get('builder')}); the footprint "
                "stays as drawn, drawn_footprint kept (CLAUDE.md: a table footprint that includes its chairs is a "
                "clear drawing error the AI may fix)")
    return {"reason": reason, "rule": SPLIT_RULE, "changed": {}, "drawn_footprint": copy.deepcopy(fp),
            "split": copy.deepcopy(split)}


def apply_split_label(piece: dict, asset: Optional[dict] = None) -> bool:
    """Label a piece whose fitted ``asset`` (default ``piece["asset"]``) carries a split (``split_label``) in place:
    ``adjusted_by_ai`` with the reason (an earlier label's reason is kept in front, its ``changed`` and bookkeeping
    keys stay), and the ``drawn_*`` keys of ``DRAWN_KEYS`` set where missing. Returns True when the piece was
    labelled. ``wenart.furniture.edit_ops`` may call it after a refit through ``fit_piece``."""
    asset = piece.get("asset") if asset is None else asset
    label = asset.get("adjusted_by_ai") if isinstance(asset, dict) else None
    if not isinstance(label, dict) or label.get("rule") != SPLIT_RULE:
        return False
    old = piece.get("adjusted_by_ai") if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    if old.get("rule") == SPLIT_RULE or SPLIT_RULE in str(old.get("rules") or ""):
        return False                                   # labelled by an earlier fit of the same plan
    for drawn_key, key in DRAWN_KEYS:
        if key in piece:
            piece.setdefault(drawn_key, copy.deepcopy(piece[key]))
    new = {"reason": label["reason"] if not old.get("reason") else f"{old['reason']}; {label['reason']}",
           "changed": dict(old.get("changed") or {}), "rule": SPLIT_RULE, "split": copy.deepcopy(label.get("split"))}
    if old.get("rule") and old["rule"] != SPLIT_RULE:
        new["rules"] = [old["rule"], SPLIT_RULE]       # e.g. a size snap and then the split
    for k in ("round", "log_seq", "model", "snapped_wall", "fix_fixture"):
        if old.get(k) is not None:
            new[k] = old[k]
    piece["adjusted_by_ai"] = new
    return True


HEIGHT_TOLERANCE = 0.15          # = sizes.fits' tolerance: a fitted height this far outside the real range refuses
# Milestone 13 (16 Oct 2026, found by the CPU fit of real04 on the HSSD layer): a uniform scale to the drawn width
# also scales the height. The size table's dining-table range is 0.65-0.92 m (widened by counter-height ABO tables)
# and HEIGHT_TOLERANCE widens it again, so a 2.9 m HSSD table scaled 1.155 to the drawn 3.35 m stood 0.88 m high
# (bar height) and passed. A dining table or a desk is used with chairs, so its working height is fixed: the fitted
# height must stay within WORKING_HEIGHT_TOL of the size table's product height (0.75 m / 0.76 m: 0.69-0.81 m /
# 0.70-0.82 m; common dining and desk heights are 0.72-0.78 m, ABO medians 0.76 / 0.78 m in size_table.yaml).
WORKING_HEIGHT_TYPES: tuple[str, ...] = ("table_dining", "desk")
WORKING_HEIGHT_TOL = 0.08


def working_height_ok(ftype: str, height: float, tol: float = WORKING_HEIGHT_TOL) -> bool:
    """True unless ``ftype`` has a fixed working height (``WORKING_HEIGHT_TYPES``) and ``height`` is more than ``tol``
    away from the size table's product height (always true without a product height)."""
    if ftype not in WORKING_HEIGHT_TYPES:
        return True
    from wenart.furniture import sizes as SZ

    product = (SZ.real_range(ftype) or {}).get("product")
    if not product or len(product) < 3 or not product[2]:
        return True
    return abs(float(height) / float(product[2]) - 1.0) <= tol + 1e-9


# 26 Oct 2026 (user: "why the sink is so low"): a fixture works at a fixed top height. The size table allows a
# washbasin 0.10-1.20 m tall (bowls, wall-hung basins, pedestals) and the build stood every model on the floor, so a
# wall-hung basin had its rim at 0.54 m and a 0.10 m bowl lay on the floor. A model is taken only when it can work:
# a floor model reaching the working top, or a wall-hung one hung so its top is there (``mount_for``); a bowl too
# shallow to hang alone (it needs a counter) is not taken.
WORKING_TOPS: dict[str, tuple[float, float, float, float]] = {
    # type: (shallowest model that can hang alone, lowest top, highest top, the top a hung model gets)
    "washbasin": (0.30, 0.78, 0.95, 0.85),
}


def working_top_ok(ftype: str, height: float) -> bool:
    """False for a fixture model that cannot work at its type's top (``WORKING_TOPS``): too shallow to hang alone (a
    taller model may carry its mirror or tap: the size table's height range bounds it); always true for other
    types."""
    rule = WORKING_TOPS.get(ftype)
    if rule is None:
        return True
    return float(height) >= rule[0] - 1e-9


# 28 Oct 2026 (user on real06's bathrooms: "What kind of a bath is this" / "this bath needs to make sense": a 0.37 m
# high library bath fitted at 0.375 m; the size table's 0.40-0.72 m with the 15 % tolerance let it pass): a fixture
# stands at its real height without the size table's tolerance: a bath's top (its rim) at 0.45-0.65 m. A model outside
# is not fitted; the next model or the parametric bath (rim, mixer, panels) is built. The box's top may reach 0.82 m:
# a freestanding or raised-end bath (a slipper bath) rises at its ends above its 0.60-0.65 m rim (12 of the 30
# usable library baths are 0.67-0.80 m high at their ends; merge review of 28 Oct 2026).
FIXTURE_HEIGHTS: dict[str, tuple[float, float]] = {"bathtub": (0.45, 0.82)}


def fixture_height_ok(ftype: str, height: float) -> bool:
    """False for a fixture model fitted outside its real height (``FIXTURE_HEIGHTS``, no tolerance); true for other
    types (the washbasin's working top: ``WORKING_TOPS`` and ``mount_for``)."""
    rng = FIXTURE_HEIGHTS.get(ftype)
    return rng is None or rng[0] - 1e-9 <= float(height) <= rng[1] + 1e-9


def mount_for(ftype: str, height: float) -> Optional[float]:
    """The ``mount_bottom_m`` that brings a fixture model's top to its type's working top (a wall-hung basin under
    the lowest top), None when it stands on the floor."""
    rule = WORKING_TOPS.get(ftype)
    if rule is None:
        return None
    shallow, low, _high, target = rule
    if shallow - 1e-9 <= float(height) < low:
        return round(target - float(height), 3)
    return None


def real_height_range(ftype: str) -> Optional[tuple[float, float]]:
    """The type's real height range of the one size table (``wenart.furniture.sizes.real_range``, D23); None when the
    table has no height for it."""
    from wenart.furniture import sizes as SZ

    rng = SZ.real_range(ftype)
    h = (rng or {}).get("height")
    return (float(h[0]), float(h[1])) if h else None


CEILING_MARGIN_M = 0.05          # fix round after P6a: a model stays this far under a sloped ceiling (= the solver's)


def under_ceiling(height: float, ceiling: Optional[float], margin: float = CEILING_MARGIN_M) -> bool:
    """Fix round after P6a (module docstring): the fitted ``height`` stays ``margin`` under ``ceiling`` (the room the
    piece has under a sloped ceiling, ``piece_ceiling``); always true without a ceiling (a flat level)."""
    return ceiling is None or float(height) <= float(ceiling) - margin + 1e-9


def ceiling_planes_of(building: Optional[dict], level_id: Optional[str]) -> list:
    """Fix round after P6a (module docstring): the sloped ceiling planes ``[a, b, c]`` (z = a x + b y + c, world) of
    ``level_id`` under the roof, as the scene builder makes them (``roof.roof_model`` + ``roof.ceiling_planes``, pure
    Python; the same rule as ``decor.ceiling_planes``, which the fit stage does not import: its fingerprint would then
    follow every decor change), or [] for a flat ceiling (no roof, a non-convex roof, another level)."""
    roof = (building or {}).get("roof") if isinstance(building, dict) else None
    if not isinstance(roof, dict) or not level_id:
        return []
    from wenart.blender import roof as R

    try:
        model = R.roof_model(roof, building)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return []
    if not model or not model.get("convex") or not model.get("equations") or model.get("over_level_id") != level_id:
        return []
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), None)
    if level is None or level.get("ceiling_height") is None:
        return []
    return [list(p) for p in R.ceiling_planes(model, level)]


# 27 Oct 2026 (user: "this in front of a window not making sense": a drawn dresser under a 0.90 m sill got
# a 1.44 m tall chest that covered the window): a floor piece standing in front of a window gets no model taller than
# the window's sill (less WINDOW_SILL_GAP_M), when its type has real products that low.
WINDOW_SILL_GAP_M = 0.02         # a piece's top stays this far under the sill of the window it stands in front of
WINDOW_FRONT_M = 0.45            # a piece this close to a window's wall line ...
WINDOW_OVERLAP_M = 0.10          # ... overlapping its width by this much along the wall stands in front of it


def window_front(building: Optional[dict], piece: dict) -> Optional[dict]:
    """``{"cap_m", "sill_m", "windows"}`` of a floor piece in front of windows (``window_cap``; pure), else None. The
    fit writes it on the piece (``window_cap``) so the model review reads it with no geometry library (inside
    Blender)."""
    cap, ids = _window_cap(building, piece)
    return None if cap is None else {"cap_m": cap, "sill_m": round(cap + WINDOW_SILL_GAP_M, 4), "windows": ids}


def window_cap(building: Optional[dict], piece: dict) -> Optional[float]:
    return _window_cap(building, piece)[0]


def _window_cap(building: Optional[dict], piece: dict) -> tuple[Optional[float], list]:
    """The height a floor piece in front of a window may reach (pure; module note above): the lowest sill of the
    windows of its level whose wall line lies within ``WINDOW_FRONT_M`` of its footprint and whose width it overlaps
    by ``WINDOW_OVERLAP_M`` along the wall, less ``WINDOW_SILL_GAP_M``; None when it stands in front of no window,
    hangs on a wall (a mount height), is fixed equipment (built as drawn), is no type whose back stands on a wall
    (``infer.needs_wall``: a chair or an armchair is not against the window), or its type has no real product that
    low (a wardrobe: the placement moves it)."""
    from wenart.blender import proxies as PX

    from wenart.furniture import infer as INF
    from wenart.furniture import schemas as SC

    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else None
    if not isinstance(building, dict) or not fp or not fp.get("center") or not fp.get("size"):
        return None, []
    ftype = str(piece.get("type") or "")
    if ftype in SC.FIXED_TYPES or not INF.needs_wall(ftype):      # built as drawn; a free-standing piece moves
        return None, []
    try:
        if PX.mount_bottom(piece)[0] > 0.0:
            return None, []
    except (KeyError, TypeError, ValueError, IndexError):
        return None, []
    caps = [(float(o["sill_height"]) - WINDOW_SILL_GAP_M, o.get("id")) for o in openings_behind(building, piece)
            if isinstance(o.get("sill_height"), (int, float))]
    if not caps:
        return None, []
    heights = real_height_range(str(piece.get("type") or ""))
    cap = round(min(c for c, _i in caps), 4)
    return (cap, sorted(i for _c, i in caps)) if heights is None or heights[0] <= cap else (None, [])


def openings_behind(building: Optional[dict], piece: dict, kinds: tuple[str, ...] = ("window",)) -> list[dict]:
    """The openings of ``kinds`` of the piece's level whose wall line lies within ``WINDOW_FRONT_M`` of its footprint
    and whose width it overlaps by ``WINDOW_OVERLAP_M`` along the wall (pure; the geometry of ``_window_cap``, shared
    since 28 Oct 2026: a fridge column never stands in front of a window or a pass-through)."""
    from shapely.geometry import LineString, Polygon

    from wenart import geometry as G

    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else None
    if not isinstance(building, dict) or not fp or not fp.get("center") or not fp.get("size"):
        return []
    try:
        poly = Polygon(G.rotated_rectangle((float(fp["center"][0]), float(fp["center"][1])),
                                           (float(fp["size"][0]), float(fp["size"][1])),
                                           float(fp.get("rotation_deg") or 0.0)))
    except (KeyError, TypeError, ValueError, IndexError):
        return []
    walls = {w.get("id"): w for w in building.get("walls") or []}
    out = []
    for o in building.get("openings") or []:
        if o.get("type") not in kinds or o.get("level_id") != piece.get("level_id") or o.get("build") is False:
            continue
        w = walls.get(o.get("wall_id"))
        if w is None or not o.get("center"):
            continue
        if o.get("type") == "window" and not isinstance(o.get("sill_height"), (int, float)):
            continue
        (x0, y0), (x1, y1) = w["start"][:2], w["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-6:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        cx, cy = float(o["center"][0]), float(o["center"][1])
        half = float(o.get("width") or 0.9) / 2.0
        line = LineString([(cx - ux * half, cy - uy * half), (cx + ux * half, cy + uy * half)])
        if poly.distance(line) > WINDOW_FRONT_M:
            continue
        ts = [(px - cx) * ux + (py - cy) * uy for px, py in poly.exterior.coords]
        if min(max(ts), half) - max(min(ts), -half) < WINDOW_OVERLAP_M:
            continue
        out.append(o)
    return out


def piece_ceiling(building: Optional[dict], piece: dict, planes: Optional[list] = None) -> Optional[float]:
    """Fix round after P6a (module docstring): the height a model of ``piece`` may reach under a sloped ceiling: the
    lowest ceiling over its footprint's corners and centre above the level's floor (``ceiling_planes_of``, ``planes``
    when the caller has them; = ``decor.ceiling_over``) less its mount height (``proxies.mount_bottom``: a wall cabinet
    hangs at 1.45 m); None on a flat level (no planes), without a building, a level or a footprint. 27 Oct 2026: and
    never above the sill of a window it stands in front of (``window_cap``; ``CEILING_MARGIN_M`` is added back)."""
    slope = _slope_ceiling(building, piece, planes)
    sill = window_cap(building, piece)
    if sill is not None:
        sill = round(sill + CEILING_MARGIN_M, 4)          # under_ceiling takes the margin off again
    caps = [c for c in (slope, sill) if c is not None]
    return min(caps) if caps else None


def _slope_ceiling(building: Optional[dict], piece: dict, planes: Optional[list] = None) -> Optional[float]:
    level_id = piece.get("level_id")
    fp = piece.get("footprint") if isinstance(piece.get("footprint"), dict) else None
    if not isinstance(building, dict) or not level_id or not fp or not fp.get("center") or not fp.get("size"):
        return None
    from wenart import geometry as G
    from wenart.blender import geom2d
    from wenart.blender import proxies as PX

    try:
        planes = ceiling_planes_of(building, level_id) if planes is None else planes
        if not planes:
            return None
        level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})
        cx, cy = float(fp["center"][0]), float(fp["center"][1])
        pts = list(G.rotated_rectangle((cx, cy), (float(fp["size"][0]), float(fp["size"][1])),
                                       float(fp.get("rotation_deg") or 0.0))) + [(cx, cy)]
        over = round(min(geom2d.surface_z(planes, x, y) for x, y in pts) - float(level.get("elevation") or 0.0), 4)
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError):
        return None
    return round(float(over) - PX.mount_bottom(piece)[0], 4)


def height_fits(height: float, heights: Optional[tuple[float, float]], tol: float = HEIGHT_TOLERANCE) -> bool:
    """Milestone 12 (§4.8, §6.3): the fitted model's height inside the type's real range (+- ``tol``); always true
    without a range (a bathtub fitted 0.89 m high, a stove 0.54 m: refused, the next model is tried)."""
    if not heights:
        return True
    return heights[0] / (1.0 + tol) - 1e-9 <= float(height) <= heights[1] * (1.0 + tol) + 1e-9


# Milestone 12 (docs/milestone12.md §4.8 D14): the style family fallback chain (each step also takes ``neutral``
# models: ``catalog.styles_match``); logged as ``style_fallback`` on the asset.
STYLE_FALLBACK: dict[str, tuple[str, ...]] = C.STYLE_FALLBACK
# The nearest related type a group may use when its own type has no usable model (§4.8: "a lounge chair for a
# missing armchair"); never for sofas, beds, tables and the bath and kitchen fixtures (a gap instead).
RELATED_TYPES: dict[str, tuple[str, ...]] = {
    "armchair": ("chair",), "chaise": ("armchair",), "ottoman": ("bench",), "bench": ("ottoman",),
    "side_table": ("nightstand",), "nightstand": ("side_table",), "tv_unit": ("sideboard", "dresser"),
    "sideboard": ("tv_unit", "dresser"), "dresser": ("sideboard", "tv_unit"), "console_table": ("sideboard",),
    "shoe_cabinet": ("sideboard", "dresser"), "bookshelf": ("display_cabinet", "tall_cabinet"),
    "display_cabinet": ("bookshelf", "tall_cabinet"), "tall_cabinet": ("wardrobe", "display_cabinet"),
    "wardrobe": ("tall_cabinet",), "bar_stool": ("chair",), "office_chair": ("chair",), "desk": ("console_table",),
    "bunk_bed": ("bed_single",),
}
# Audit fields (track B, contract §13.3) a fitted asset carries: the S6 check and the scene builder read them.
AUDIT_ASSET_FIELDS: tuple[str, ...] = ("audit", "real_product", "has_bedding", "has_cushions", "has_pillows",
                                       "has_mattress", "contact")
NOT_BUILT_METHOD = "none"


def style_chain(style_family: Optional[str]) -> list[Optional[str]]:
    """The families the fit tries in order: the project's, then its ``STYLE_FALLBACK`` chain ([None] without a
    family: every model)."""
    if style_family is None:
        return [None]
    return [style_family] + [f for f in STYLE_FALLBACK.get(style_family, ()) if f != style_family]


def split_usable(candidates: list[dict], mode: str = "commercial") -> tuple[list[dict], list[dict]]:
    """``(usable entries with their audit fixes applied, excluded rows)`` (``catalog.usable`` in licence ``mode``)."""
    usable, refused = [], []
    for e in candidates:
        if C.usable(e, mode):
            usable.append(e)                       # an audit fix is in the fields already
        else:
            refused.append({"id": e["id"], "reason": C.unusable_reason(e, mode)})
    return usable, refused


def group_needs(piece: dict) -> bool:
    """A piece its group needs (§4.8): a member of a functional group (``furniture[].group``, track G) or a piece
    drawn in the documents (CLAUDE.md: drawn furniture is kept)."""
    return bool(isinstance(piece.get("group"), dict) and piece["group"].get("group_id")) or \
        piece.get("source") == "from_documents"


def gap_fit(piece: dict, reason: str, candidates: Optional[list] = None, excluded: Optional[list] = None,
            style_family: Optional[str] = None) -> dict:
    """A piece that is not built (Milestone 13: only one with ``build: false``, not furniture or removed) and has no
    model: ``method: "none"`` and ``library_gap`` (copied onto the piece by ``fit_building``); the parametric box
    stays as ``bbox_m`` for the planners."""
    asset = parametric_fit(piece, reason, candidates, excluded, style_family)
    asset.update({"library": NOT_BUILT_METHOD, "asset_id": f"none:{piece['type']}", "method": NOT_BUILT_METHOD,
                  "library_gap": {"type": piece["type"], "style": style_family, "step": NOT_BUILT_METHOD,
                                  "used": "nothing (not built)", "reason": reason}})
    return asset


def _no_model(piece: dict, catalog, reason: str, tried: list, excluded: list, cap: float,
              uniform_range: tuple[float, float], style_family: Optional[str], *, mode: str = "commercial",
              used: Optional[dict] = None, style: Optional[dict] = None, ceiling: Optional[float] = None) -> dict:
    """The fallback ladder (docs/milestone13.md §12 D4, §13.2) when no usable model of the piece's type fits:
    step 1 a model of the nearest related type for a piece its group needs (``RELATED_TYPES``); a piece that is not
    built (``build: false``) stops here with ``method: none``; step 2 a module builder (``module_plan_for``, track
    T2); step 3 the parametric family (our parametric fixture for the by-design types, docs/milestone12.md §6.4).
    ``asset.ladder`` logs every step; ``library_gap.step`` names the one used. A drawn anchor is never left out."""
    ftype = piece["type"]
    ladder = [_step("library", "no model", reason)]
    if group_needs(piece):
        for rt in RELATED_TYPES.get(ftype, ()):
            usable, _refused = split_usable(catalog.candidates(rt), mode)
            for fam in style_chain(style_family):
                got = _fit_family(dict(piece, type=rt), usable, fam, cap, uniform_range, None, used=used,
                                  ceiling=ceiling)
                if got.get("method") == "library":
                    got["related_type"] = rt
                    got["excluded"] = list(excluded) + got.get("excluded", [])
                    got["library_gap"] = {"type": ftype, "style": style_family, "step": "library",
                                          "used": f"related type {rt}: {got['asset_id']}"
                                                  + (f" ({fam} style)" if fam != style_family else ""),
                                          "reason": reason}
                    ladder[-1] = _step("library", f"related type {rt}: {got['asset_id']}", reason)
                    return _finish(got, mode, ladder)
    if piece.get("build") is False:
        asset = gap_fit(piece, reason, tried, excluded, style_family)
        ladder.append(_step(MODULE_METHOD, "not tried", "the piece is not built (build false)"))
        ladder.append(_step("parametric", "not tried", "the piece is not built (build false)"))
        return _finish(asset, mode, ladder)
    plan, why = module_plan_for(piece, style)
    if plan is not None:
        asset = module_fit(piece, plan, reason, tried, excluded, style_family)
        ladder.append(_step(MODULE_METHOD, f"used {plan['builder']}", None))
        return _finish(asset, mode, ladder)
    ladder.append(_step(MODULE_METHOD, "no module builder", why))
    by_design = ftype in C.BY_DESIGN_PARAMETRIC_TYPES
    if by_design:
        fixture = ftype in C.PARAMETRIC_FIXTURE_TYPES or bool(tried or excluded)
        why = (f"{reason}; our parametric {ftype.replace('_', ' ')} (by design, docs/milestone12.md §6.4)"
               if fixture else reason)                        # a counter, island, wall cabinet or stair: as always
        asset = parametric_fit(piece, why, tried, excluded, style_family)
        asset["by_design"] = True
        if fixture:
            asset["library_gap"] = {"type": ftype, "style": style_family, "step": "parametric",
                                    "used": "our parametric fixture (by design)", "reason": reason}
        ladder.append(_step("parametric", "used (by design)", "docs/milestone12.md §6.4: made to the drawing"))
        return _finish(asset, mode, ladder)
    asset = parametric_fit(piece, f"{reason}; the parametric family (ladder step 3, docs/milestone13.md §13.2)",
                           tried, excluded, style_family)
    asset["library_gap"] = {"type": ftype, "style": style_family, "step": "parametric",
                            "used": "parametric family (built below the library level)", "reason": reason}
    ladder.append(_step("parametric", "used", "no library model within the caps and no module builder"))
    return _finish(asset, mode, ladder)


def bed_frame_record(entry: dict, width: float, depth: float, z_scale: float) -> dict:
    """The bed-frame fields of a fitted asset (docs/milestone8.md §4): ``bed_frame``, the catalogue
    ``deck_height_m`` and ``bedding`` (``wenart.blender.parametric.frame_bedding_info``: deck and mattress
    top in the piece frame, deck = ``deck_height_m`` x the z fit scale, the inner box, the bedding top)."""
    from wenart.blender import parametric as P   # pure Python (no bpy)

    deck = float(entry["deck_height_m"])
    return {"bed_frame": True, "deck_height_m": deck,
            "bedding": P.frame_bedding_info(width, depth, deck * float(z_scale))}


# Decor (docs/milestone8.md §4): types that may use a library decor model; book sets stay parametric.
DECOR_LIBRARY_TYPES: tuple[str, ...] = ("cushion", "plant", "rug", "wall_art",
                                        "vase", "bowl", "plant_small", "table_lamp", "mirror",   # Milestone 9
                                        # Milestone 10 (docs/milestone10.md §4.6); Milestone 12 (§4.7, §6.4, B7):
                                        # throws, curtains and blinds are our procedural textiles, never a model
                                        "books", "candle", "basket", "tray", "clock",
                                        "sculpture", "plant_large", "pendant_light", "ceiling_light")
PROCEDURAL_DECOR_TYPES: tuple[str, ...] = ("throw", "curtain", "blind")   # wenart.blender.textiles
# Milestone 12 (§4.7, B7): a cushion model keeps its real proportions: scaled uniformly to the cushion's width and
# height (their scales may differ by at most this), its thickness then in CUSHION_THICKNESS_M.
CUSHION_PROPORTION_CAP = 1.10
CUSHION_THICKNESS_M = (0.06, 0.28)
# Milestone 9 (docs/milestone9.md §3, §5): wall decor hangs like wall art (its width, the model's aspect); tabletop
# decor keeps the model's proportions and real size, scaled down (never up) to fit the item's box ("within").
WALL_DECOR_TYPES: tuple[str, ...] = ("wall_art", "mirror", "clock")
SURFACE_DECOR_TYPES: tuple[str, ...] = ("vase", "bowl", "plant_small", "table_lamp",
                                        # Milestone 10: tabletop and hanging pieces keep their real proportions
                                        "candle", "tray", "books", "sculpture", "basket", "pendant_light",
                                        "ceiling_light")
# Furniture models that serve a decor type too (the same object): a floor plant may be a potted_plant model.
DECOR_FROM_FURNITURE: dict[str, tuple[str, ...]] = {"plant": ("potted_plant",)}
# Decor models of catalog.json (Poly Haven, M4) by their old ``type``: the potted plants. The pillow model
# (``decor_cushion``: two loose pillows lying flat) stays out: squashed to a standing cushion it looks wrong.
LEGACY_DECOR_TYPES: dict[str, str] = {"decor_plant": "plant"}
DECOR_NON_UNIFORM_CAP = 1.5      # cushion / plant / rug footprint stretch (max/min of the x, y scales) above: refused
RUG_MAX_THICKNESS_M = 0.03       # a rug model is kept flat: its height is capped here
SURFACE_DECOR_MIN_M = 0.04       # a tabletop model scaled below this footprint side is refused (Milestone 9)
# 30 Oct 2026 (UL151): the floor pieces whose model must read as one (``rest.floor_class_problem``); none left: ours
FLOOR_CLASS_FIT_TYPES: tuple[str, ...] = ("plant", "plant_large", "floor_vase", "sculpture")
WALL_ART_MIN_WIDTH_M = 0.3       # a wall art model that would end narrower (ceiling room) is refused
_TURN_90 = {"-Y": "-X", "-X": "+Y", "+Y": "+X", "+X": "-Y"}   # the claimed front that turns a model by +90 degrees


def decor_type_of(entry: dict) -> Optional[str]:
    """The decor type of a catalogue entry: ``decor_type`` of a ``kind: decor`` entry (Milestone 8), or the
    Poly Haven ``decor_plant`` models of catalog.json; None for anything else."""
    if entry.get("kind") == "decor" and entry.get("decor_type"):
        return str(entry["decor_type"])
    return LEGACY_DECOR_TYPES.get(str(entry.get("type")))


def decor_entries(catalog, dtype: str, mode: str = "commercial") -> list[dict]:
    """The catalogue's decor models of ``dtype``, sorted by id: ``catalog.decor_candidates(dtype)`` when the
    catalogue has that method (Milestone 8 library), plus the decor entries of ``catalog.decor`` and
    ``catalog.entries`` of that type (``decor_type_of``); duplicates by id once; only the ones usable in licence
    ``mode`` (Milestone 13)."""
    found: list[dict] = []
    method = getattr(catalog, "decor_candidates", None)
    if callable(method):
        found += [e for e in (method(dtype) or []) if isinstance(e, dict)]
    for e in list(getattr(catalog, "decor", None) or []) + list(getattr(catalog, "entries", None) or []):
        if isinstance(e, dict) and decor_type_of(e) == dtype:
            found.append(e)
    furniture_types = DECOR_FROM_FURNITURE.get(dtype, ())
    for e in list(getattr(catalog, "entries", None) or []):    # Milestone 9: e.g. potted_plant models as plants
        if isinstance(e, dict) and e.get("type") in furniture_types and e.get("source") in C.LIBRARY_SOURCES:
            found.append(e)
    out: dict[str, dict] = {}
    for e in found:
        if e.get("id") and not e.get("parametric") and (e.get("gltf") or e.get("glb")) and e.get("bbox_m") \
                and C.usable(e, mode):                            # Milestone 12 / 13: audited, usable in the mode
            out.setdefault(str(e["id"]), e)
    return [out[k] for k in sorted(out)]


def decor_styles_match(entry: dict, family: Optional[str]) -> bool:
    """The M7 style rule for decor; a decor model without ``styles`` (the Poly Haven plants) is neutral; its title
    may not name a style the family may not carry either (UL174)."""
    return (not entry.get("styles") or C.styles_match(entry, family)) and not C.title_style_clash(entry, family)


def pick_index(key: str, n: int) -> int:
    """Deterministic pick of one of ``n`` models by a host id (the same host always gets the same model,
    different hosts spread over the models)."""
    return int(hashlib.sha256(str(key).encode("utf-8")).hexdigest()[:12], 16) % n if n else 0


# 28 Oct 2026 (real06 run 154514: the living room's five ceiling lights came in three models): the decor of these types
# matches across its room, one model per room and type
ROOM_MATCHED_DECOR_TYPES: tuple[str, ...] = ("ceiling_light", "pendant_light")


def decor_pick_key(item: dict) -> str:
    """The id the library pick hangs on: the room and the type for ``ROOM_MATCHED_DECOR_TYPES`` (one model for the
    room's lights), else the host piece, else the first anchor piece (rug, wall art), else the item itself (a floor
    plant)."""
    if item.get("type") in ROOM_MATCHED_DECOR_TYPES and item.get("room_id"):
        role = item.get("fixture") if item.get("fixture") in FIXTURE_ROLES else None   # 29 Oct 2026 (UL106)
        return f"{item['room_id']}:{item['type']}" + (f":{role}" if role else "")
    anchors = item.get("anchor_ids") or []
    return str(item.get("host_id") or (anchors[0] if anchors else None) or item.get("id") or item.get("type"))


# 29 Oct 2026 (UL106; the professional reference: a black multi-arm chandelier with glass globes over the bed, slim
# pendants hanging low beside the nightstands, small recessed downlights): the light's role in the room
# (``item["fixture"]``, wenart.furniture.dressing) narrows the model pool; a downlight is our parametric recessed fixture.
FIXTURE_ROLES: tuple[str, ...] = ("statement", "bedside", "downlight")
STATEMENT_WORDS: tuple[str, ...] = ("chandelier", "chandeliers", "globe", "globes", "multi light", "multi-light",
                                    "branch", "arms", "sputnik", "cluster", "3-light", "4-light", "5-light", "6-light",
                                    "8-light")
SLIM_ASPECT = 1.6                # a bedside pendant's model is at least this much taller than wide (a slim drop)


STATEMENT_STYLE_WORDS: dict[str, tuple[str, ...]] = {
    "globe": ("globe", "globes", "sputnik", "branch", "branching", "bubble", "orb", "orbs"),
    "linear": ("linear", "bar", "island", "blade", "line", "rectangular", "trestle"),
    "cluster": ("cluster", "multi light", "multi-light", "3-light", "5-light", "pendants", "cascade")}


def _title_has(title: str, words) -> bool:
    import re

    text = str(title or "").casefold()
    return any(re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", text) for w in words)


def is_statement_title(title: str) -> bool:
    """A model title that names a statement fixture (pure): a whole word or phrase of ``STATEMENT_WORDS``."""
    import re

    text = str(title or "").casefold()
    return any(re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", text) for w in STATEMENT_WORDS)


def fixture_pool(fits: list, item: dict) -> tuple[list, Optional[str]]:
    """``(pool, why)``: the fitting models a light of its role takes first (pure): a ``statement`` fixture the
    models whose title names a chandelier, globes or several arms (``STATEMENT_WORDS``), a ``bedside`` pendant the
    slim ones (``SLIM_ASPECT``); the whole ``fits`` when none matches or the light has no role."""
    role = item.get("fixture")
    if role == "statement":
        # 29 Oct 2026 (UL119, R3, R4, R15, R30): the room's scheme names the statement's style (globe, linear,
        # cluster); the models whose title names it first
        words = STATEMENT_STYLE_WORDS.get(str(item.get("statement_style") or ""))
        if words:
            styled = [(e, f) for e, f in fits if _title_has(e.get("title") or e.get("name") or "", words)]
            if styled:
                return styled, f"statement fixture: a {item['statement_style']} model (the room's scheme)"
        pool = [(e, f) for e, f in fits if is_statement_title(e.get("title") or e.get("name") or "")]
        return (pool, "statement fixture: a chandelier or multi-globe model") if pool else (fits, None)
    if role == "bedside":
        pool = [(e, f) for e, f in fits if float(e["bbox_m"][2]) >= SLIM_ASPECT * max(float(e["bbox_m"][0]),
                                                                                       float(e["bbox_m"][1]))]
        return (pool, "bedside pendant: a slim model") if pool else (fits, None)
    return fits, None


def _decor_fit(entry: dict, item: dict, dtype: str) -> Optional[dict]:
    """Scale, box and orientation of one decor model on ``item``, or None when it does not fit
    (``DECOR_NON_UNIFORM_CAP``, a wall art that would be narrower than ``WALL_ART_MIN_WIDTH_M``)."""
    width, depth = (float(v) for v in item["size"][:2])
    bw, bd, bh = (float(v) for v in entry["bbox_m"][:3])
    front = entry["front_axis"]
    if dtype == "cushion":                        # Milestone 12 (B7): real proportions, never stretched
        if len(item["size"]) < 3 or not item["size"][2]:
            return None                           # a lying cushion (ottoman, bench): the procedural one
        height = float(item["size"][2])
        sw, sh = width / bw, height / bh
        if max(sw, sh) / min(sw, sh) > CUSHION_PROPORTION_CAP + 1e-9:
            return None
        s = (sw + sh) / 2.0
        if not CUSHION_THICKNESS_M[0] - 1e-9 <= bd * s <= CUSHION_THICKNESS_M[1] + 1e-9:
            return None
        return {"fit_scale": [round(s, 4)] * 3, "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)],
                "front_axis": front, "turned_deg": 0.0, "target": "within", "non_uniform": round(max(sw, sh)
                                                                                                 / min(sw, sh), 4)}
    if dtype in SURFACE_DECOR_TYPES:              # Milestone 9: real size, scaled down to the item box, never up
        height = float(item["size"][2]) if len(item["size"]) > 2 and item["size"][2] else None
        limits = [width / bw, depth / bd] + ([height / bh] if height else [])
        s = min([1.0] + limits)
        if min(bw * s, bd * s) < SURFACE_DECOR_MIN_M - 1e-9:
            return None
        return {"fit_scale": [round(s, 4)] * 3, "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)],
                "front_axis": front, "turned_deg": 0.0, "target": "within", "non_uniform": 1.0}
    if dtype in WALL_DECOR_TYPES:                 # its width, the model's aspect; the height the wall allows
        s = width / bw
        max_h = item.get("max_height_m")
        if isinstance(max_h, (int, float)) and max_h > 0 and bh * s > float(max_h):
            s = float(max_h) / bh
        if bw * s < WALL_ART_MIN_WIDTH_M - 1e-9:
            return None
        return {"fit_scale": [round(s, 4)] * 3, "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)],
                "front_axis": front, "turned_deg": 0.0, "target": "wall_art", "non_uniform": 1.0}
    turned = 0.0
    if dtype == "rug" and C.aspect_error({"bbox_m": [bd, bw, bh]}, width, depth) < C.aspect_error(entry, width, depth):
        bw, bd, front, turned = bd, bw, _TURN_90[front], 90.0      # a rug has no front: turn it to its long side
    sx, sy = width / bw, depth / bd
    non_uniform = max(sx, sy) / min(sx, sy)
    if non_uniform > DECOR_NON_UNIFORM_CAP + 1e-9:
        return None
    if dtype == "rug":                            # flat: scaled to the rug size, its thickness kept (capped)
        h = min(bh, RUG_MAX_THICKNESS_M)
        return {"fit_scale": [round(sx, 4), round(sy, 4), round(h / bh, 4)],
                "bbox_m": [round(width, 4), round(depth, 4), round(h, 4)], "front_axis": front,
                "turned_deg": turned, "target": "rug", "non_uniform": round(non_uniform, 4)}
    sz = (sx + sy) / 2.0                          # cushion, plant: the item box, height by the mean scale
    return {"fit_scale": [round(sx, 4), round(sy, 4), round(sz, 4)],
            "bbox_m": [round(width, 4), round(depth, 4), round(bh * sz, 4)], "front_axis": front,
            "turned_deg": 0.0, "target": "size", "non_uniform": round(non_uniform, 4)}


# 30 Oct 2026 (lesson UL156, user: "I did not like this lamp table combo"): a table lamp is chosen with its host. Its
# shade (the model's widest side) takes at most ``LAMP_SHADE_TOP_RATIO`` of the host top's smaller side, at most
# ``LIGHT_BASE_SHADE_RATIO`` on a host of light visual weight (a pedestal, tripod, hairpin or wire base:
# ``LIGHT_BASE_WORDS`` in its model's title); beside a seat or a bed (``EYE_LEVEL_HOSTS``) the lamp is
# ``LAMP_HEIGHT_RATIO`` of the host's height, so the shade's lower edge sits near seated eye level; a real product is
# never shrunk below ``LAMP_MIN_SCALE`` of its size (a 0.9 m lamp at 63 % reads as a toy). The rules pick among the
# lamps that fit; when none does, the shade rule holds (never a shade wider than ``LAMP_SHADE_HARD_RATIO`` of the
# top) and the height and scale rules are relaxed in that order (``asset.pairing`` records the limits and what held).
LAMP_SHADE_TOP_RATIO = 0.60
LIGHT_BASE_SHADE_RATIO = 0.50
LAMP_SHADE_HARD_RATIO = 0.75
LAMP_HEIGHT_RATIO = (0.75, 1.15)
LAMP_MIN_SCALE = 0.85
EYE_LEVEL_HOSTS: tuple[str, ...] = ("side_table", "nightstand")
LIGHT_BASE_WORDS: tuple[str, ...] = ("pedestal", "tripod", "hairpin", "wire", "hoop", "platner", "tulip", "swivel",
                                     "star base", "spindle")
# ... and the pair reads as one design: a novelty lamp (an animal, a figure, a neon sign) comes only when no other fits
NOVELTY_LAMP_WORDS: tuple[str, ...] = ("deer", "animal", "animals", "neon", "palm tree", "elvis", "presley", "skull",
                                       "unicorn", "cartoon", "novelty", "bird", "birds", "owl", "dog", "cat", "horse")
# ... and beside a seat or a bed a shaded table lamp, not a work light: a task, desk, banker's or swing-arm lamp, a
# wall sconce (a title naming a desk lamp without a table lamp) comes only when no other fits
TASK_LAMP_WORDS: tuple[str, ...] = ("task", "banker", "bankers", "architect", "clamp", "swing arm", "swing-arm",
                                    "sconce", "sconces", "downbridge", "wall lamp", "usb port", "reading arm")


def lamp_misfit(entry: dict, host_type: Optional[str]) -> Optional[str]:
    """UL156: why a lamp model does not pair with its host (None when it does): a novelty lamp anywhere; a work light
    beside a seat or a bed (``EYE_LEVEL_HOSTS``)."""
    title = _title_of(entry)
    hits = _named(title, NOVELTY_LAMP_WORDS)
    if hits:
        return f"a novelty lamp ({', '.join(dict.fromkeys(hits))})"
    if host_type in EYE_LEVEL_HOSTS:
        work = _named(title, TASK_LAMP_WORDS)
        if not work and _named(title, ("desk lamp",)) and not _named(title, ("table lamp", "table desk lamp")):
            work = ["desk lamp"]
        if work:
            return f"a work light ({', '.join(dict.fromkeys(work))}) beside a {str(host_type).replace('_', ' ')}"
    return None
PAIRING_RULE = "fit.lamp_host"


def host_top(host: dict, catalog=None) -> tuple[Optional[float], Optional[float], bool, str]:
    """``(top's smaller side m, height m, light_base, title)`` of a lamp's host piece (pure but for the catalogue's
    title): its fitted model's box (``asset.bbox_m``), else its footprint and height; ``light_base`` when the model's
    title names a light base (``LIGHT_BASE_WORDS``)."""
    asset = host.get("asset") if isinstance(host.get("asset"), dict) else {}
    box = asset.get("bbox_m") if isinstance(asset.get("bbox_m"), list) and len(asset.get("bbox_m")) > 2 else None
    size = (host.get("footprint") or {}).get("size") or []
    side = min(float(box[0]), float(box[1])) if box else (min(float(size[0]), float(size[1])) if len(size) > 1
                                                          else None)
    height = float(box[2]) if box else (float(host["height"]) if isinstance(host.get("height"), (int, float))
                                        else None)
    title = str(asset.get("title") or "")
    if not title and catalog is not None and asset.get("asset_id"):
        entry = getattr(catalog, "entry", lambda _i: None)(asset["asset_id"]) or {}
        title = str(entry.get("title") or entry.get("name") or "")
    light = bool(_named(html.unescape(title).lower(), LIGHT_BASE_WORDS))
    return side, height, light, title


def lamp_limits(host: Optional[dict], catalog=None) -> Optional[dict]:
    """UL156 (the comment above): the limits a table lamp on ``host`` keeps (None without a host or its size)."""
    if not isinstance(host, dict):
        return None
    side, height, light, title = host_top(host, catalog)
    if not side or side <= 0:
        return None
    ratio = LIGHT_BASE_SHADE_RATIO if light else LAMP_SHADE_TOP_RATIO
    out = {"host_id": host.get("id"), "host_type": host.get("type"), "host_top_m": round(side, 4),
           "host_height_m": round(height, 4) if height else None, "light_base": light,
           "shade_max_m": round(side * ratio, 4), "shade_hard_m": round(side * LAMP_SHADE_HARD_RATIO, 4),
           "min_scale": LAMP_MIN_SCALE, "rule": PAIRING_RULE}
    if height and host.get("type") in EYE_LEVEL_HOSTS:
        out["height_range_m"] = [round(height * LAMP_HEIGHT_RATIO[0], 4), round(height * LAMP_HEIGHT_RATIO[1], 4)]
    return out


def lamp_pairing(fits: list, item: dict, limits: dict) -> tuple[list, dict]:
    """``(pool, record)``: the lamp models of ``fits`` (``(entry, fit)`` pairs, fitted to the item's box) that keep the
    host's ``limits`` (``lamp_limits``): the shade, the height range and the scale; when none keeps all, the shade and
    the height, then the shade alone (never wider than ``shade_hard_m``); an empty pool when no model keeps that."""
    def shade(f):
        return max(float(f["bbox_m"][0]), float(f["bbox_m"][1]))

    def tall_ok(f):
        rng = limits.get("height_range_m")
        return rng is None or rng[0] - 1e-9 <= float(f["bbox_m"][2]) <= rng[1] + 1e-9

    def scale_ok(f):
        return float(f["fit_scale"][0]) >= limits["min_scale"] - 1e-9

    steps = (("shade, height and real size", lambda f: shade(f) <= limits["shade_max_m"] + 1e-9 and tall_ok(f)
              and scale_ok(f)),
             ("shade and height (the lamp scaled below its real size)",
              lambda f: shade(f) <= limits["shade_max_m"] + 1e-9 and tall_ok(f)),
             ("shade (no lamp of the eye-level height fits)", lambda f: shade(f) <= limits["shade_max_m"] + 1e-9),
             ("the hard shade limit only", lambda f: shade(f) <= limits["shade_hard_m"] + 1e-9))
    record = dict(limits, refused=[e["id"] for e, f in fits if shade(f) > limits["shade_hard_m"] + 1e-9])
    for name, ok in steps:
        pool = [(e, f) for e, f in fits if ok(f)]
        if pool:
            record["held"] = name
            misfits = {e["id"]: why for e, _f in pool for why in [lamp_misfit(e, limits.get("host_type"))] if why}
            plain = [(e, f) for e, f in pool if e["id"] not in misfits]
            if plain and misfits:
                record["misfits_dropped"] = dict(sorted(misfits.items()))
                pool = plain
            return pool, record
    record["held"] = "none: no lamp model keeps the shade under the host's top (the parametric lamp)"
    return [], record


# 30 Oct 2026 (lesson UL215, user: "Library models if exist and better than procedural generation should be used"): the
# decor types we also build procedurally take an audited library model of their type (the catalogue's extras: the 3D
# Warehouse objects) when one is better than the procedural build: vision quality at least LIBRARY_FIRST_MIN_QUALITY,
# a real product, the style family's (``decor_styles_match``), usable in the licence mode (a logo-flagged model in
# relaxed mode only), its size inside the type's real product range after uniform scaling and at most
# LIBRARY_FIRST_BOX_SLACK past the box the decor stage reserved. Else the procedural model, with a ``library_gap`` note
# on the item (none audited, none better, none fits) that the fit report lists. Per type: the extras type and the real
# (width, depth, height) ranges in metres; a TV is scaled to the panel width the media wall asked for.
LIBRARY_FIRST: dict[str, tuple[str, tuple[tuple[float, float], tuple[float, float], tuple[float, float]]]] = {
    "laptop": ("laptop", ((0.28, 0.42), (0.18, 0.42), (0.15, 0.32))),         # open: the lid stands up
    "monitor": ("monitor", ((0.45, 0.85), (0.12, 0.30), (0.30, 0.65))),
    "microwave": ("microwave", ((0.40, 0.62), (0.30, 0.48), (0.24, 0.38))),
    "tv": ("tv", ((0.80, 1.70), (0.05, 0.35), (0.45, 1.10))),                  # with its stand
}
LIBRARY_FIRST_MIN_QUALITY = 4
LIBRARY_FIRST_BOX_SLACK = 1.25


def _library_first_scale(entry: dict, item: dict, dtype: str) -> Optional[float]:
    """The uniform scale that puts ``entry`` inside its type's real range (a TV: the item's panel width), None when no
    uniform scale does or the result runs past the item's box by more than ``LIBRARY_FIRST_BOX_SLACK``."""
    (w0, w1), (d0, d1), (h0, h1) = LIBRARY_FIRST[dtype][1]
    bw, bd, bh = (float(v) for v in entry["bbox_m"][:3])
    if min(bw, bd, bh) <= 0:
        return None
    if dtype == "tv":
        s = float(item["size"][0]) / bw if item.get("size") else 1.0
    else:
        s = 1.0 if w0 <= bw <= w1 else min(max(bw, w0), w1) / bw
    w, d, h = bw * s, bd * s, bh * s
    if not (w0 - 1e-6 <= w <= w1 + 1e-6 and d0 - 1e-6 <= d <= d1 + 1e-6 and h0 - 1e-6 <= h <= h1 + 1e-6):
        return None
    size = [float(v) for v in (item.get("size") or [])[:2]]
    if len(size) == 2 and (w > size[0] * LIBRARY_FIRST_BOX_SLACK + 1e-6 or d > size[1] * LIBRARY_FIRST_BOX_SLACK + 1e-6):
        return None
    return round(s, 4)


def library_first_item(item: dict, catalog, style_family: Optional[str], mode: str) -> Optional[dict]:
    """The library asset for a decor item of a ``LIBRARY_FIRST`` type, or None (procedural; the item's
    ``library_gap`` says why). The best of the passing models: the highest vision quality, then no logo, then the size
    nearest the reserved box, then the id (deterministic)."""
    dtype = item.get("type", "")
    etype = LIBRARY_FIRST[dtype][0]
    pool = [e for e in getattr(catalog, "extras", None) or [] if e.get("type") == etype]
    if not pool:
        item["library_gap"] = {"type": dtype, "why": f"no audited {etype} model in the library"}
        return None
    usable = [e for e in pool if e.get("glb") and e.get("bbox_m") and C.usable(e, mode)]
    better = [e for e in usable if (vision_quality_of(e) or 0) >= LIBRARY_FIRST_MIN_QUALITY
              and e.get("real_product") is not False and decor_styles_match(e, style_family)]
    fits = [(e, s) for e in better for s in [_library_first_scale(e, item, dtype)] if s is not None]
    if not fits:
        why = (f"none of {len(usable)} usable {etype} model(s) in {mode} mode rates {LIBRARY_FIRST_MIN_QUALITY} or "
               "more (the procedural one is better)" if not better else
               f"none of the {len(better)} better {etype} model(s) fits the real size or the reserved box")
        item["library_gap"] = {"type": dtype, "why": why, "candidates": len(pool)}
        return None
    size = [float(v) for v in (item.get("size") or [0.0, 0.0])[:2]] + [0.0, 0.0]

    def rank(pair):
        e, s = pair
        bw, bd = float(e["bbox_m"][0]) * s, float(e["bbox_m"][1]) * s
        return (-(vision_quality_of(e) or 0), bool(C.logo_flagged(e)),
                round(abs(bw - size[0]) + abs(bd - size[1]), 4), str(e["id"]))

    entry, s = sorted(fits, key=rank)[0]
    bw, bd, bh = (float(v) for v in entry["bbox_m"][:3])
    asset = {
        "library": entry.get("source") or "3dwh", "asset_id": entry["id"], "licence": entry.get("licence"),
        "license": entry.get("licence"), "method": "library", "decor_type": dtype, "fit_scale": [s, s, s],
        "bbox_m": [round(bw * s, 4), round(bd * s, 4), round(bh * s, 4)], "target": "within", "turned_deg": 0.0,
        "front_axis": entry.get("front_axis", "-Y"), "up_axis": entry.get("up_axis", "+Z"),
        "origin_offset": list(entry.get("origin_offset") or [0.0, 0.0, 0.0]),
        "front_axis_confidence": entry.get("front_axis_confidence"), "styles": list(entry.get("styles") or []),
        "style_family": style_family, "quality": vision_quality_of(entry),
        "pick": {"rule": "library_first (UL215)", "ids": [e["id"] for e, _s in sorted(fits, key=rank)],
                 "of_type": len(pool), "usable": len(usable), "better": len(better)},
    }
    asset.update({k: entry[k] for k in GLB_ASSET_FIELDS if k in entry})
    asset["unit_scale"] = float(entry.get("unit_scale") or 1.0)
    asset["licence_flag"] = C.licence_flag_of(entry)
    item.pop("library_gap", None)
    return _finish(asset, mode, [_step("library", f"used {entry['id']} (library first, UL215)", None)])


def fit_decor_item(item: dict, catalog, style_family: Optional[str] = None, *,
                   mode: str = "commercial", host: Optional[dict] = None) -> Optional[dict]:
    """``asset`` for a decor item (docs/milestone8.md §4): one of the catalogue's decor models of its type
    and of the style family or neutral (``decor_entries``, ``decor_styles_match``) that fits the item
    (``_decor_fit``), picked deterministically by the host id (``pick_index`` of ``decor_pick_key``); None
    (parametric decor; no wall art) when there is none. Blender scales the model to ``bbox_m``. Milestone 13:
    only models usable in licence ``mode``; the asset carries the licence fields (``_finish``)."""
    mode = C.check_mode(mode)
    dtype = item.get("type", "")
    if dtype in LIBRARY_FIRST and not (item.get("tv") or {}).get("mount") == "wall":
        return library_first_item(item, catalog, style_family, mode)          # UL215: the library first
    if dtype not in DECOR_LIBRARY_TYPES or not item.get("size") or len(item["size"]) < 2:
        return None
    if item.get("fixture") == "downlight":            # 29 Oct 2026 (UL106): our recessed downlight (parametric)
        return None
    if item.get("fixture") in ("led_mirror", "backlit_mirror", "round_mirror"):
        return None                                   # 29 Oct 2026 (UL114, UL123, UL124): the bathroom's own mirrors
    if item.get("fixture") == "track" or item.get("shape") in ("round", "arch") or item.get("stems") \
            or (item.get("tv") or {}).get("mount") == "wall":
        return None      # 29 Oct 2026 (UL113, UL115): our track light, round mirror or rug, a vase with pampas
    if item.get("fixture") in ("linear_pendant", "track_pendants") or item.get("set") == "centrepiece":
        return None      # 30 Oct 2026 (P16, UL153): our dining fixture and centrepiece set (salon_parts), by design
    styled = [e for e in decor_entries(catalog, dtype, mode) if decor_styles_match(e, style_family)
              and C.contact_fits(e, dtype)]               # Milestone 12: the audited contact suits the type
    limits = lamp_limits(host, catalog) if dtype == "table_lamp" else None
    box_item = item
    if limits:                                        # 30 Oct 2026 (UL156): the lamp in proportion to its host
        size = [float(v) if v else None for v in item["size"][:3]] + [None] * (3 - len(item["size"][:3]))
        rng = limits.get("height_range_m")
        size[0], size[1] = min(size[0], limits["shade_hard_m"]), min(size[1], limits["shade_hard_m"])
        if rng:
            size[2] = min(size[2], rng[1]) if size[2] else rng[1]
        box_item = dict(item, size=size)
    fits = [(e, f) for e in styled for f in [_decor_fit(e, box_item, dtype)] if f is not None]
    pairing = None
    if limits:
        fits, pairing = lamp_pairing(fits, box_item, limits)
    if dtype in FLOOR_CLASS_FIT_TYPES and not item.get("host_id"):
        # 30 Oct 2026 (lesson UL151, user: "this vase on the floor not making sense"): a floor piece's model is tall
        # enough and no table piece (real04's kitchen plant was "Flowers (Plants)", a vase of flowers, 0.54 m)
        from wenart.blender import rest as RS

        fits = [(e, f) for e, f in fits
                if RS.floor_class_problem(dtype, f["bbox_m"][2], e.get("title") or e.get("name")) is None]
    if not fits:
        return None
    # Milestone 10: a large plant of the brief's species takes models of that species first.
    species = item.get("species")
    if dtype == "plant_large" and species:
        same = [(e, f) for e, f in fits if e.get("species") == species]
        fits = same or fits
    # Milestone 9: an AI decor item names a colour; models whose name holds it come first (the pick stays
    # deterministic by the host id inside the chosen group).
    all_fits = fits
    fits, role_why = fixture_pool(fits, item)          # 29 Oct 2026 (UL106): the light's role in the room
    colour = str(item.get("colour") or "").strip().casefold()
    coloured = [(e, f) for e, f in fits if colour and colour in str(e.get("name") or e.get("title") or "").casefold()]
    pool = coloured or fits
    key = decor_pick_key(item)
    i = pick_index(key, len(pool))
    entry, f = pool[i]
    width, depth = (float(v) for v in item["size"][:2])
    asset = {
        "library": entry.get("source") or "polyhaven", "asset_id": entry["id"], "licence": entry.get("licence"),
        "license": entry.get("licence"), "method": "library", "decor_type": dtype, "fit_scale": f["fit_scale"],
        "bbox_m": f["bbox_m"], "aspect_error": round(C.aspect_error(entry, width, depth), 4),
        "front_axis": f["front_axis"], "up_axis": entry.get("up_axis", "+Z"),
        "origin_offset": list(entry.get("origin_offset") or [0.0, 0.0, 0.0]),
        "front_axis_confidence": entry.get("front_axis_confidence"), "target": f["target"],
        "turned_deg": f["turned_deg"], "styles": list(entry.get("styles") or []), "style_family": style_family,
        "quality": entry.get("quality"),
        "pick": {"key": key, "index": i, "of": len(pool), "ids": [e["id"] for e, _f in pool],
                 "colour": colour or None, "colour_matches": len(coloured),
                 "not_fitting": [e["id"] for e in styled if e["id"] not in {x["id"] for x, _f in all_fits}],
                 "other_style": len(decor_entries(catalog, dtype, mode)) - len(styled)},
    }
    if role_why:
        asset["pick"]["fixture"] = role_why
    if pairing:
        asset["pairing"] = pairing                    # UL156: the host's limits and which of them held
    if asset["library"] != "polyhaven" and entry.get("glb"):
        asset.update({k: entry[k] for k in GLB_ASSET_FIELDS if k in entry})
        asset["unit_scale"] = float(entry.get("unit_scale") or 1.0)
    else:
        asset["gltf"] = entry["gltf"]
    asset["licence_flag"] = C.licence_flag_of(entry)
    return _finish(asset, mode, [_step("library", f"used {entry['id']}", None)])


def fabric_colour_of(piece: dict, style: Optional[dict]) -> tuple[Optional[str], Optional[str]]:
    """``(colour, where it came from)`` of an upholstered piece (Milestone 13, B1 of docs/milestone13.md §1.8): its
    ``design.fabric_colour`` (layout stage), else the style's ``furniture.by_type[type].fabric_colour``, else
    ``furniture.fabric_colour``; ``(None, None)`` for other types or without a colour. The completion stage writes
    ``design.material_tags`` only, so the brief's "light grey fabric sofa" reaches the fit through this."""
    if piece.get("type") not in UPHOLSTERED_TYPES:
        return None, None
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    if design.get("fabric_colour"):
        return str(design["fabric_colour"]), "furniture.design (layout stage)"
    profile = style[0] if isinstance(style, list) and style else style
    furniture = (profile or {}).get("furniture") if isinstance(profile, dict) else None
    furniture = furniture if isinstance(furniture, dict) else {}
    by_type = (furniture.get("by_type") or {}).get(piece.get("type")) or {}
    if isinstance(by_type, dict) and by_type.get("fabric_colour"):
        return str(by_type["fabric_colour"]), f"style.json furniture.by_type.{piece.get('type')}"
    if furniture.get("fabric_colour"):
        return str(furniture["fabric_colour"]), "style.json furniture.fabric_colour"
    return None, None


def design_of(piece: dict, style: Optional[dict]) -> dict:
    """The look the fit honours for a piece (Milestone 10): its ``furniture.design`` (layout stage), else the
    ``style.json`` fallback of ``wenart.blender.looks.design_for``; {} without a style. Milestone 13: an upholstered
    piece whose design lacks the fabric colour gets the style's (``fabric_colour_of``), so the brief's colour is a
    preference of the fit and travels to the asset."""
    if style is None and not isinstance(piece.get("design"), dict):
        return {}
    from wenart.blender import looks as LK

    design = dict(LK.design_for(piece, style or {})[0])
    colour, source = fabric_colour_of(piece, style)
    if colour and not design.get("fabric_colour"):
        design["fabric_colour"] = colour
        design["fabric_colour_source"] = source
    return design


# --------------------------------------------------------------------------
# Milestone 13 (K1, D5): the size snap before the fit
# --------------------------------------------------------------------------

SNAP_RULE = "size_snap"
DRAWN_KEYS = (("drawn_type", "type"), ("drawn_footprint", "footprint"), ("drawn_front_deg", "front_deg"),
              ("drawn_height", "height"))


def snap_allowed(settings) -> tuple[bool, str]:
    """Whether the size snap runs under the brief's furnished-room settings (``wenart.furniture.complete.Settings``
    or a dict with ``furnished_rooms`` / ``furnished_rooms_keep_size``): off with ``keep`` or ``keep_size`` (user OK
    D5 of 12 Oct 2026); on without settings (the defaults: complete)."""
    if settings is None:
        return True, "no brief: furnished_rooms complete (default), size snap on"
    mode = getattr(settings, "mode", None)
    keep_size = getattr(settings, "keep_size", None)
    if isinstance(settings, dict):
        mode = settings.get("furnished_rooms", mode)
        keep_size = settings.get("furnished_rooms_keep_size", keep_size)
    if str(mode or "complete") == "keep":
        return False, "furnished_rooms: keep: drawn sizes stay as drawn (size snap off)"
    if keep_size:
        return False, "furnished_rooms_keep_size: drawn sizes stay as drawn (size snap off)"
    return True, f"furnished_rooms: {mode or 'complete'}, size snap on"


def snap_candidate(piece: dict) -> Optional[str]:
    """Why a piece is not snapped (None when it is): only drawn furniture that is built, with a type the size table
    knows, and no fixed equipment (the ingest's fixed rule and the agent's ``fix_fixture`` resize those)."""
    if piece.get("source") != "from_documents":
        return "not drawn"
    if piece.get("build") is False:
        return "not built"
    ftype = piece.get("type")
    if ftype in (None, "unknown"):
        return "no type"
    if C.by_design_parametric(piece):
        return "fixed equipment or a by-design type (the ingest rule and fix_fixture resize those)"
    from wenart.furniture import sizes as SZ

    if SZ.real_range(ftype) is None:
        return f"no size row for {ftype}"
    return None


def apply_size_snap(piece: dict, part: Optional[tuple] = None) -> Optional[dict]:
    """Snap a drawn piece's footprint to the nearest real product when it lies outside its type's product range
    (``wenart.furniture.sizes.snap_size``), in place; returns the ``size_snap`` record or None when nothing changed.
    The width change keeps the centre; a depth change keeps the back edge where it was (the piece stays against its
    wall; without a front the centre stays). The piece keeps ``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``,
    ``drawn_height`` and is labelled ``adjusted_by_ai`` with the reason (CLAUDE.md furniture rules).

    ``part`` (build round 3, the split before the snap): the ``(w, d)`` the snap judges instead of the footprint,
    the table part of a drawn footprint that includes its chairs (``split_plan_first``); then only the width and
    the height of the piece may change, the drawn depth stays (it holds the chairs) and the record says ``part``."""
    from wenart.furniture import sizes as SZ

    if snap_candidate(piece) is not None:
        return None
    fp = piece["footprint"]
    w, d = (float(v) for v in fp["size"][:2])
    height = piece.get("height") if isinstance(piece.get("height"), (int, float)) else None
    judged = (w, d) if part is None else (float(part[0]), float(part[1]))
    snap = SZ.snap_size(piece["type"], judged, height)
    symbol = False
    if not snap["changed"] and part is None:
        # 29 Oct 2026 (UL94): a plan symbol drawn larger than its product (a floor lamp's 0.58 m circle) takes the
        # type's real product, centred where it is drawn (``sizes.symbol_snap``)
        sym = SZ.symbol_snap(piece["type"], judged)
        if sym["changed"]:
            snap, symbol = dict(sym, height=None), True
    if not snap["changed"]:
        return None
    before = copy.deepcopy(fp)
    nw, nd = (round(float(v), 4) for v in snap["footprint"])
    if part is not None:
        nd = round(d, 4)                     # the drawn depth stays: the chairs are in it (the split's business)
    cx, cy = (float(v) for v in fp["center"])
    front = piece.get("front_deg")
    if abs(nd - d) > 1e-9 and isinstance(front, (int, float)) and not symbol:
        shift = (nd - d) / 2.0
        cx += shift * math.cos(math.radians(float(front)))
        cy += shift * math.sin(math.radians(float(front)))
    piece["footprint"] = dict(fp, center=[round(cx, 4), round(cy, 4)], size=[nw, nd])
    changed = {"footprint": before}
    if snap["height"] is not None and height is not None and abs(float(snap["height"]) - height) > 1e-9:
        changed["height"] = piece.get("height")
        piece["height"] = round(float(snap["height"]), 4)
    for drawn_key, key in DRAWN_KEYS:
        # the values before the snap (review fix of 15 Oct 2026: the footprint and the height were replaced above, so
        # the drawn height must come from ``changed``, not from the piece, or it would hold the product height)
        value = before if key == "footprint" else changed["height"] if key == "height" and "height" in changed \
            else piece.get(key)
        piece.setdefault(drawn_key, copy.deepcopy(value))
    old = piece.get("adjusted_by_ai") if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    merged_changed = dict(old.get("changed") or {})
    for k, v in changed.items():
        merged_changed.setdefault(k, v)
    if symbol:
        reason = (f"size snap: {snap['reason']} (CLAUDE.md: a drawn size outside its type's real product range is "
                  "snapped to a real product before the fit; user, 29 Oct 2026: \"I did not like this light\", "
                  "lesson UL94)")
    elif part is None:
        reason = (f"size snap: the drawn {piece['type']} {w:.2f} x {d:.2f} m is outside its product range "
                  f"({snap['reason']}); nearest real product {snap['product']} (CLAUDE.md: a drawn size outside its "
                  "type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct "
                  "2026)")
    else:
        reason = (f"size snap of the table part: the {piece['type']} {judged[0]:.2f} x {judged[1]:.2f} m inside the "
                  f"drawn {w:.2f} x {d:.2f} m footprint is outside its product range ({snap['reason']}); nearest real "
                  f"product {snap['product']}; the drawn depth stays, it holds the chairs (CLAUDE.md: a drawn size "
                  "outside its type's product range is snapped to the nearest real product before the fit; user OK "
                  "D5 of 12 Oct 2026; the split decides first, build round 3)")
    label = {"reason": reason if not old.get("reason") else f"{old['reason']}; {reason}", "changed": merged_changed,
             "rule": SNAP_RULE}
    if old.get("rule") and old["rule"] != SNAP_RULE:
        label["rules"] = list(old.get("rules") or [old["rule"]]) + [SNAP_RULE]   # e.g. the split, then the snap
    for k in ("round", "log_seq", "model", "snapped_wall", "fix_fixture", "split"):
        if old.get(k) is not None:
            label[k] = copy.deepcopy(old[k])
    piece["adjusted_by_ai"] = label
    record = {"drawn": [w, d] + ([height] if height is not None else []),
              "snapped": [nw, nd] + ([piece["height"]] if "height" in changed else ([height] if height is not None
                                                                                     else [])),
              "product": snap["product"], "reason": snap["reason"]}
    if part is not None:
        record["part"] = [round(judged[0], 4), round(judged[1], 4)]
    if symbol:
        record["symbol"] = True               # 29 Oct 2026 (UL94): a plan symbol fitted at its real product
    piece["size_snap"] = record
    return record


def split_plan_first(piece: dict, style: Optional[dict] = None) -> Optional[dict]:
    """Build round 3 (lead decision on the K1 / T2 leftover): the module plan with a ``split`` of a drawn table whose
    footprint is deeper than a real table (``wenart.blender.modules.plan_table_long``: deeper than
    ``TABLE_DEPTH_MAX_M``, 1.20 m, the footprint includes its chairs), decided BEFORE the size snap; None for every
    other piece (no snap candidate, no module builder, no split). The size snap must not snap such a footprint to a
    product depth first: that would erase the chairs.

    A footprint whose depth is its long side (``size[1] > size[0]``) is not split first: ``plan_table_long`` reads
    ``size[1]`` as the depth with no orientation check (``wenart.blender.modules``, owner T2), so a long table drawn
    turned would be taken for a short table with its chairs; such a piece keeps the round-2 order (the snap, then
    the ladder). None of the 131 dining tables of the committed buildings is drawn so (checked 16 Oct 2026)."""
    if snap_candidate(piece) is not None:
        return None
    size = (piece.get("footprint") or {}).get("size") or []
    if len(size) < 2 or float(size[1]) > float(size[0]) + 1e-9:
        return None
    plan, _why = module_plan_for(piece, style)
    if not isinstance(plan, dict) or not isinstance(plan.get("split"), dict):
        return None
    return plan


def apply_split_then_snap(piece: dict, style: Optional[dict] = None) -> Optional[tuple[dict, Optional[dict]]]:
    """The split-before-snap order of build round 3 for one drawn piece, in place: when ``split_plan_first`` finds a
    split, the piece is labelled ``adjusted_by_ai`` (rule ``module_split``, ``drawn_footprint`` and the other
    ``drawn_*`` keys kept, the footprint unchanged) and only then the table part is judged by the size snap
    (``apply_size_snap(part=...)``: the width and the height may take a real product, the depth stays as drawn).
    After such a snap the plan is made again on the snapped piece; the label keeps ``rule: module_split`` (the
    split is why the piece changed) with ``rules = [module_split, size_snap]``, its ``split`` is the new plan's and
    its reason says what is built (``split_snap_reason``), after any earlier label's reason. Returns ``(plan,
    size_snap record or None)``, or None when the piece has no split (the caller snaps as usual)."""
    plan = split_plan_first(piece, style)
    if plan is None:
        return None
    prior = copy.deepcopy(piece.get("adjusted_by_ai")) if isinstance(piece.get("adjusted_by_ai"), dict) else {}
    apply_split_label(piece, {"adjusted_by_ai": split_label(piece, plan)})
    table = plan["split"].get("table_m") or piece["footprint"]["size"][:2]
    drawn_fp = copy.deepcopy(piece["footprint"])
    record = apply_size_snap(piece, part=(float(table[0]), float(table[1])))
    if record is None:
        return plan, None
    again, _why = module_plan_for(piece, style)
    if isinstance(again, dict) and isinstance(again.get("split"), dict):
        plan = again
    label = piece["adjusted_by_ai"]
    label["rule"] = SPLIT_RULE
    label["rules"] = [r for r in (prior.get("rules") or ([prior["rule"]] if prior.get("rule") else []))
                      if r not in (SPLIT_RULE, SNAP_RULE)] + [SPLIT_RULE, SNAP_RULE]
    label["split"] = copy.deepcopy(plan["split"])
    text = split_snap_reason(drawn_fp, piece, plan, record)
    label["reason"] = text if not prior.get("reason") else f"{prior['reason']}; {text}"
    return plan, record


def split_module_fit(piece: dict, fitted: dict, style: Optional[dict], style_family: Optional[str],
                     mode: str) -> dict:
    """Build round 3 (review of item 2): the asset of a piece the split labelled first (``apply_split_then_snap``)
    when the fit picked something other than its module plan with the split. Why: the label says the module builder
    makes the table and its chairs inside the drawn footprint, and the lead decision is that the split decides; a
    library table at the full footprint depth (a square table model scaled to a deep square footprint, a deep
    model from a later catalogue) would build the table alone, erase the chairs and contradict the label (the fit
    CLI's ``assert_only_assets_changed`` refuses a split label without the plan's split). Today's catalogue never
    gets here (no library table reaches a footprint deeper than 1.35 m within the caps, checked on 16 Oct 2026 over
    1.2-3.6 m widths and 1.25-2.2 m depths); the guard keeps it so when the catalogue grows. Returns ``fitted``
    unchanged when it already carries the split or when the module plan no longer splits."""
    if ((fitted.get("module_plan") or {}).get("split")) or fitted.get("method") == "none":
        return fitted
    plan, _why = module_plan_for(piece, style)
    if not isinstance(plan, dict) or not isinstance(plan.get("split"), dict):
        return fitted
    picked = fitted.get("asset_id") or fitted.get("method") or "the fit"
    reason = (f"the drawn footprint holds the table and its chairs (module split, decided before the size snap, "
              f"build round 3): {picked} would build the table alone at the full footprint depth")
    asset = module_fit(piece, plan, reason, fitted.get("candidates") or [], fitted.get("excluded") or [],
                       style_family)
    asset["split_over"] = picked
    return _finish(asset, mode, [_step("library", f"not used: {picked}", reason),
                                 _step(MODULE_METHOD, f"used {plan['builder']}", "the module split decides")])


def split_snap_reason(drawn_fp: dict, piece: dict, plan: dict, record: dict) -> str:
    """The ``adjusted_by_ai`` reason of a drawn table split first and then snapped (``apply_split_then_snap``): the
    drawing error (the footprint holds the chairs), the table part outside the product range and the product it
    took, the footprint that results (the drawn depth kept) and what the module builder makes in it."""
    split = plan.get("split") or {}
    dw, dd = (float(v) for v in drawn_fp["size"][:2])
    nw, nd = (float(v) for v in piece["footprint"]["size"][:2])
    part = record.get("part") or [dw, dd]
    table = [float(v) for v in (split.get("table_m") or [nw, nd])[:2]]
    chairs = int(split.get("chairs") or 0)
    why = str(split.get("reason") or "the drawn footprint is deeper than a real table")
    return (f"module split, then the size snap of the table part: {why}; the table part {part[0]:.2f} x "
            f"{part[1]:.2f} m is outside its product range ({record['reason']}; the product: "
            f"{record['product']}), so the footprint is {nw:.2f} x {nd:.2f} m (drawn {dw:.2f} x {dd:.2f} m; the depth "
            f"stays, it holds the chairs); built as a {table[0]:.2f} x {table[1]:.2f} m table"
            + (f" with {chairs} chairs" if chairs else "")
            + f" inside it ({plan.get('builder')}); drawn_footprint kept (CLAUDE.md: a table footprint that includes "
              "its chairs is a clear drawing error the AI may fix, and a drawn size outside its type's product range "
              "is snapped to the nearest real product; user OK D5 of 12 Oct 2026; the split decides first, build "
              "round 3)")


def resolve_mode(building: dict, brief: Optional[dict], mode: Optional[str]) -> tuple[str, str]:
    """``(mode, source)`` of a fit run: the given ``mode``, else the building's ``project.licence_mode`` (a later
    stage never reads the brief), else ``catalog.licence_mode_from(brief)`` (env > brief > commercial)."""
    if mode is not None:
        return C.check_mode(mode), "given to the fit"
    project = building.get("project") if isinstance(building.get("project"), dict) else {}
    if project.get("licence_mode") in C.LICENCE_MODES:
        return str(project["licence_mode"]), "building project.licence_mode"
    return C.licence_mode_from(brief)


def fit_building(building: dict, catalog: C.Catalog, cap: float = NON_UNIFORM_CAP,
                 style_family: Optional[str] = None, style: Optional[dict] = None, *, mode: Optional[str] = None,
                 brief: Optional[dict] = None, settings=None, snap: Optional[bool] = None,
                 assets_dir: Optional[Path] = None) -> dict:
    """A deep copy of ``building`` with ``asset`` set on every furniture piece and on every decor item (a library
    decor model, or None: parametric decor, no wall art). ``style_family`` (refit only): the library style filter of
    ``fit_piece`` and ``fit_decor_item``; ``style`` (refit only, Milestone 10): the profile whose looks the fit
    honours (``design_of``).

    Milestone 13: ``mode`` None = ``project.licence_mode`` of the building, else the brief's (``resolve_mode``); the
    fit writes ``project.licence_mode`` and ``project.licence_mode_source``. Before the fit the drawn sizes outside
    their product range are snapped (``apply_size_snap``; ``snap`` None = by the brief's furnished-room settings,
    ``settings`` a ``complete.Settings`` or the ``brief``'s values; off with keep / keep_size). The use counters of
    the diversity penalty run over the pieces in file order (per room and per project). Nothing else changes
    (``assert_only_assets_changed``). Fix round after P6a (module docstring): a piece under a sloped ceiling is fitted
    with its ``piece_ceiling`` (the level's ``ceiling_planes_of``, made once per level; none on a flat level)."""
    mode, mode_source = resolve_mode(building, brief, mode)
    fitted = copy.deepcopy(building)
    project = fitted.get("project") if isinstance(fitted.get("project"), dict) else None
    if project is None:
        project = fitted["project"] = {}
    project["licence_mode"] = mode
    project["licence_mode_source"] = mode_source
    if settings is None and brief is not None and "values" in brief:
        # the two keys of wenart.furniture.complete.Settings the snap needs, read from the brief here so that the fit
        # stage's import closure stays free of the layout code (wenart/run/stages.py FIT_CODE)
        from wenart import brief as BR

        settings = {"furnished_rooms": BR.value(brief, "furnished_rooms", "complete"),
                    "furnished_rooms_keep_size": BR.value(brief, "furnished_rooms_keep_size", False)}
    snap_on, snap_why = (snap, "given to the fit") if snap is not None else snap_allowed(settings)
    project["size_snap"] = {"on": bool(snap_on), "why": snap_why}
    snapped = []
    split_first = []
    if snap_on:
        for piece in fitted.get("furniture", []):
            # Build round 3 (lead decision): a drawn table footprint deeper than a real table is a table with its
            # chairs (the module plan's split decides, ``split_plan_first``); it is labelled first and only its
            # table part is judged by the snap, so the snap never erases the chairs.
            split = apply_split_then_snap(piece, style)
            if split is not None:
                split_first.append(piece["id"])
                record = split[1]
            else:
                record = apply_size_snap(piece)
            if record is not None:
                snapped.append(piece["id"])
        if split_first:
            project["size_snap"]["split_first"] = split_first
    used_project: Counter = Counter()
    used_rooms: dict[str, Counter] = {}
    # fix round after P3 (module docstring): the drawn sinks and stoves inside the kitchen runs
    kitchen = kitchen_built_ins(fitted)
    by_id = {p.get("id"): p for p in fitted.get("furniture", [])}
    room_types = {r.get("id"): str(r.get("room_type") or "").lower() for r in fitted.get("rooms") or []}
    open_rooms = OD.open_air_room_ids(fitted)        # 28 Oct 2026: the rooms that are outside (type or open to the sky)
    from wenart.furniture import taste as T
    taste_cache = T.TasteCache(assets_dir) if assets_dir is not None else None
    taste_target = T.targets(style) if taste_cache is not None else {}
    taste_rooms: dict[str, dict] = {}
    planes_of: dict = {}             # fix round after P6a: the sloped ceiling of each level (made once per level)

    def ceiling_of(piece: dict) -> Optional[float]:
        level_id = piece.get("level_id")
        if level_id not in planes_of:
            planes_of[level_id] = ceiling_planes_of(fitted, level_id)
        front = window_front(fitted, piece)          # 27 Oct 2026: a window's sill caps it too; the record is the
        if front is not None:                        # model review's (M2), read with no geometry library in Blender
            piece["window_cap"] = front
        else:
            piece.pop("window_cap", None)
        return piece_ceiling(fitted, piece, planes_of[level_id])

    # 26 Oct 2026 (fix D): the role sets of the groups (the chairs of a table, the nightstands of a bed, the armchairs
    # of a seating group) and the one model each set takes (``role_set_fit``)
    sets = role_sets(fitted)
    set_of = {pid: key for key, ids in sets.items() for pid in ids}
    set_models: dict = {}

    def role_set_fit(piece: dict, target: dict, design: Optional[dict], used: dict) -> Optional[dict]:
        """The asset of a role-set member: the set's model (fitted once on the members' median drawn size, the
        first time a member is fitted) on this piece's own drawn size within the caps; None when the set has no
        library model or the model fails the caps here (the caller fits the piece on its own)."""
        key = set_of[piece["id"]]
        if key not in set_models:
            members = [by_id[i] for i in sets[key] if i in by_id]
            size = median_size(members)
            rep = fit_piece(dict(target, footprint=dict(target["footprint"], size=size)), catalog, cap=cap,
                            style_family=style_family, design=design or None, mode=mode, used=used, style=style,
                            ceiling=ceiling_of(piece))
            set_models[key] = None if rep.get("method") != "library" else {
                "group_id": key[0], "type": key[1], "members": list(sets[key]), "median_size": size,
                "asset_id": rep["asset_id"],
                "rule": "one model per role of a group: fitted once on the members' median drawn size, used for "
                        "every member within the caps (26 Oct 2026)"}
        model = set_models[key]
        entry = next((e for e in catalog.candidates(key[1]) if e.get("id") == model["asset_id"]), None) \
            if model is not None else None
        if entry is None:
            return None
        asset = fit_piece(target, _OneModel(catalog, entry), cap=cap, style_family=None, design=design or None,
                          mode=mode, used=used, style=style, ceiling=ceiling_of(piece))
        if asset.get("method") != "library":
            return None
        asset["style_family"] = style_family
        asset["role_set"] = dict(model, used=True)
        return asset

    def fit_one(piece: dict, built_into: Optional[dict] = None, extra_hints: Optional[dict] = None) -> None:
        frozen = {k: copy.deepcopy(piece.get(k)) for k in FROZEN_KEYS}
        room = str(piece.get("room_id") or "")
        used = {"project": used_project, "room": used_rooms.setdefault(room, Counter())}
        if taste_cache is not None:          # 25 Oct 2026: the room's set of wood tones and metal (taste.py)
            used["taste"] = (taste_cache, taste_rooms.setdefault(room, {}), taste_target)
        if built_into is not None:
            asset = built_in_fit(piece, built_into, mode, style_family)
        else:
            design = design_of(piece, style) if (style is not None or piece.get("design")) else None
            hints = run_hints(kitchen, piece.get("id"))     # 29 Oct 2026: with the kitchen details' hints
            if extra_hints:                  # 28 Oct 2026: a wall cabinet's ends and its run's joints
                hints = {**(hints or {}), **extra_hints}
            # the run's hints reach its plan on a copy: the building piece never gets module_hints (FROZEN_KEYS,
            # assert_only_assets_changed); the asset keeps them beside the plan (furniture.module_plan_of)
            target = dict(piece, module_hints={**(piece.get("module_hints") or {}), **hints}) if hints else piece
            if piece.get("room_id") in open_rooms or piece.get("open_air") or piece.get("outdoor_space"):
                target = dict(target, open_air_room=True)     # outdoor models only (a copy: the piece stays)
            elif room_types.get(piece.get("room_id")):
                target = dict(target, open_air_room=False)    # 26 Oct 2026 (fix E): a known indoor room
            target = dict(target, **use_context(fitted, piece))   # bathroom sense of 26 Oct 2026: a child's room
            target = dict(target, **room_use_context(fitted, piece))   # 30 Oct 2026 (UL156, UL161): the room's type
            # 26 Oct 2026 (fix D): a member of a role set takes the set's one model (role_set_fit), else its own fit
            asset = role_set_fit(piece, target, design, used) if piece.get("id") in set_of else None
            if asset is None:
                asset = fit_piece(target, catalog, cap=cap, style_family=style_family, design=design or None,
                                  mode=mode, used=used, style=style, ceiling=ceiling_of(piece))
                if piece.get("id") in set_of and set_models.get(set_of[piece["id"]]) is not None:
                    asset["role_set"] = dict(set_models[set_of[piece["id"]]], used=False, why=(
                        "the set's model fails the caps on this piece's drawn size: fitted on its own"))
            if target.get("open_air_room"):
                entry = catalog.entry(asset.get("asset_id")) if asset.get("method") == "library" else None
                if asset.get("method") == "library":
                    asset["outdoor_grade"] = outdoor_grade(entry or {})
                # 28 Oct 2026: the outdoor record (``outdoor``), and for a module or parametric piece the weather-proof
                # design and the library gap (``outdoor.outdoor_asset``)
                OD.outdoor_asset(asset, str(piece.get("type") or ""), entry, style_family)
            if hints and asset.get("method") == MODULE_METHOD:
                asset["module_hints"] = copy.deepcopy(hints)
            if piece.get("id") in split_first:
                # review of build round 3 item 2: a piece the split labelled is built by its module plan (the split
                # decides; a library table at the full depth would erase the chairs the label names)
                asset = split_module_fit(piece, asset, style, style_family, mode)
            colour, source = fabric_colour_of(piece, style)
            if colour:
                asset["fabric_colour"] = colour
                asset["fabric_colour_source"] = source
        piece["asset"] = asset
        if piece.get("type") == "bathtub" and asset.get("method") != "library":
            # 28 Oct 2026 (user: "this bath needs to make sense"): a bath built from code knows its walls
            from wenart.furniture import fixture_seat as FS
            asset["bath_walls"] = FS.bath_walls(fitted, piece)
        # 26 Oct 2026: a wall-hung fixture model hangs at its working top (the build honours mount_bottom_m)
        mount = mount_for(str(piece.get("type") or ""), float((asset.get("bbox_m") or [0, 0, 0])[2] or 0.0)) \
            if asset.get("method") == "library" else None
        if mount is not None:
            piece["mount_bottom_m"] = mount
            piece["mount_source"] = "fit: a wall-hung model at its working top"
        elif piece.get("mount_source", "").startswith("fit:"):
            piece.pop("mount_bottom_m", None)
            piece.pop("mount_source", None)
        apply_split_label(piece, asset)                 # a table footprint split into table + chairs (modules)
        if asset.get("method") == "library":
            used_project[asset["asset_id"]] += 1
            used["room"][asset["asset_id"]] += 1
            if taste_cache is not None:
                attrs = taste_cache.get(catalog.entry(asset["asset_id"]) or {})
                if attrs:
                    asset["taste"] = {k: attrs[k] for k in ("wood_tone", "metal", "loud", "main") if k in attrs}
                    T.note(taste_rooms.setdefault(room, {}), attrs)
        # Milestone 12 (§4.8, §6.4): the library gap (type, style, what was used instead) is a finding on the piece
        if asset.get("library_gap"):
            piece["library_gap"] = dict(asset["library_gap"])
        else:
            piece.pop("library_gap", None)
        for key in FROZEN_KEYS:
            if frozen.get(key) != piece.get(key):  # cannot happen; guards future edits
                raise RuntimeError(f"fit changed {key} of {piece['id']}")

    deferred = []
    order = list(fitted.get("furniture", []))
    if taste_cache is not None:              # the anchors of a room first: the partners follow their look
        order.sort(key=lambda p: (str(p.get("room_id") or ""), T.anchor_rank(str(p.get("type") or ""))))
    walls_after = []
    for piece in order:
        if piece.get("id") in kitchen["sinks"]:
            deferred.append(piece)             # after its run: built in only when the run's plan holds it
            continue
        if piece.get("type") == "wall_cabinet":
            walls_after.append(piece)          # 28 Oct 2026: after its run, in line with its base units
            continue
        fit_one(piece)
    for piece in deferred:
        run = by_id.get(kitchen["sinks"][piece["id"]])
        fit_one(piece, run if holds_built_in(run, piece["id"]) else None)
    for piece in walls_after:
        fit_one(piece, extra_hints=wall_run_hints(piece, wall_cabinet_run(fitted, piece), fitted))
    for item in fitted.get("decor") or []:
        item["asset"] = fit_decor_item(item, catalog, style_family=style_family, mode=mode,
                                       host=by_id.get(item.get("host_id")))     # UL156: a lamp with its host
    if taste_cache is not None:
        taste_cache.save()
        project["taste"] = {"target": {k: v for k, v in taste_target.items() if k != "palette"},
                            "rooms": {r: dict(v) for r, v in sorted(taste_rooms.items()) if v}}
    return fitted


# 26 Oct 2026 (fix D, user: "fix should be general"): the piece types a group holds several of as one set (the chairs
# of a table, the nightstands of a bed, the armchairs and poufs of a seating group, the stools of an island). Each
# drawn chair was fitted to its own drawn width (real06: 0.37-0.54 m), so different chair models won at one table;
# SET_TYPES only lifted the room's reuse penalty. Now the members of one group with the same type take one model.
ROLE_SET_TYPES: tuple[str, ...] = ("chair", "nightstand", "armchair", "bar_stool", "office_chair", "ottoman",
                                   "side_table", "bench")


def role_sets(building: dict) -> dict:
    """26 Oct 2026 (fix D): ``{(group_id, type): [piece ids]}`` of the groups with two or more members of one
    ``ROLE_SET_TYPES`` type (the ``group`` field the layout writes; not the anchor, not a piece that is not built, not
    a piece the agent pinned to a model: its pin decides).

    26 Oct 2026 (the big loop's first finding: real06's living room held a grey dining armchair, brown leather ones
    and a red egg chair, all drawn and in no group): drawn pieces of one ``ROLE_SET_TYPES`` type in one room outside a
    group, of about one drawn size (``LOOSE_SET_TOL_M`` both ways), are a set too: ``("room:<room id>", type)``."""
    out: dict = {}
    loose: dict = {}
    for f in building.get("furniture") or []:
        if f.get("type") not in ROLE_SET_TYPES or f.get("build") is False or f.get("asset_pin") \
                or not (f.get("footprint") or {}).get("size"):
            continue
        g = f.get("group")
        if isinstance(g, dict) and g.get("group_id"):
            if g.get("role") != "anchor":
                out.setdefault((str(g["group_id"]), f["type"]), []).append(f["id"])
            continue
        if f.get("source") == "from_documents" and f.get("room_id"):
            loose.setdefault((f"room:{f['room_id']}", f["type"]), []).append(f)
    by_id = {f.get("id"): f for f in building.get("furniture") or []}

    def close(pieces: list) -> bool:
        sizes = [sorted(float(v) for v in q["footprint"]["size"][:2]) for q in pieces]
        return all(max(s[i] for s in sizes) - min(s[i] for s in sizes) <= LOOSE_SET_TOL_M + 1e-9 for i in (0, 1))

    for (room_key, ftype), pieces in sorted(loose.items()):
        room = room_key.split(":", 1)[1]
        # the room's group set of the same type takes them when they are of its size (one model for the room)
        host = next((k for k, ids in sorted(out.items()) if k[1] == ftype and not k[0].startswith("room:")
                     and ids and (by_id.get(ids[0]) or {}).get("room_id") == room
                     and close([by_id[i] for i in ids if i in by_id] + pieces)), None)
        if host is not None:
            out[host] = out[host] + [q["id"] for q in pieces]
        elif len(pieces) >= 2 and close(pieces):
            out[(room_key, ftype)] = [q["id"] for q in pieces]
    return {k: sorted(v) for k, v in sorted(out.items()) if len(v) >= 2}


LOOSE_SET_TOL_M = 0.25          # drawn pieces of one type in one room within this of each other are one set (the
#                                 set model still fits each piece within its caps, else the piece takes its own)


def median_size(pieces: list[dict]) -> list[float]:
    """26 Oct 2026 (fix D): the median drawn width and depth of a role set's members (``footprint.size``)."""
    import statistics

    ws = [float(p["footprint"]["size"][0]) for p in pieces]
    ds = [float(p["footprint"]["size"][1]) for p in pieces]
    return [round(statistics.median(ws), 4), round(statistics.median(ds), 4)]


PROJECT_FIT_KEYS = ("licence_mode", "licence_mode_source", "size_snap", "taste")
SNAP_PIECE_KEYS = ("size_snap", "adjusted_by_ai", "footprint", "height") + tuple(k for k, _ in DRAWN_KEYS)


def assert_only_assets_changed(before: dict, after: dict) -> None:
    """Raise AssertionError unless ``after`` equals ``before`` except for ``furniture[].asset`` and
    ``decor[].asset`` (Milestone 12: and ``furniture[].library_gap``, UL215: ``decor[].library_gap``; Milestone 13:
    the fit's ``project`` keys and, on a piece with a ``size_snap``, the snapped footprint and height with their
    labels, checked here: the snapped size is the footprint's, the drawn footprint is the one before; a module split
    keeps the footprint, and, split first in build round 3, the snap of its table part changes the width only)."""
    a, b = copy.deepcopy(before), copy.deepcopy(after)
    for piece_a, piece_b in zip(a.get("furniture", []), b.get("furniture", [])):
        label = piece_b.get("adjusted_by_ai") if isinstance(piece_b.get("adjusted_by_ai"), dict) else {}
        split = label.get("rule") == SPLIT_RULE and label != piece_a.get("adjusted_by_ai")
        snap = piece_b.get("size_snap")
        new_snap = bool(snap) and snap != piece_a.get("size_snap")
        if split:
            # a module split (build round 2): the footprint is unchanged, the label and the drawn_* keys are new.
            # Build round 3 (split before the snap): the snap of the table part (``size_snap.part``) may change the
            # width only; the drawn depth (it holds the chairs), the centre and the rotation stay.
            fa, fb = piece_a.get("footprint") or {}, piece_b.get("footprint") or {}
            if new_snap and snap.get("part"):
                if (round(float(fb["size"][1]), 4) != round(float(fa["size"][1]), 4)
                        or fb.get("center") != fa.get("center") or fb.get("rotation_deg") != fa.get("rotation_deg")):
                    raise AssertionError(f"{piece_b.get('id')}: the snap of a split table's part may change its "
                                         "width only (the drawn depth holds the chairs)")
            elif fb != fa:
                raise AssertionError(f"{piece_b.get('id')}: a module split must not change the footprint")
            if piece_b.get("drawn_footprint") != piece_a.get("drawn_footprint", piece_a.get("footprint")):
                raise AssertionError(f"{piece_b.get('id')}: drawn_footprint does not hold the drawn footprint")
            if not label.get("reason") or not ((piece_b.get("asset") or {}).get("module_plan") or {}).get("split"):
                raise AssertionError(f"{piece_b.get('id')}: a split piece needs adjusted_by_ai with a reason and the "
                                     "plan's split")
        if split and not new_snap:
            for key in ("adjusted_by_ai",) + tuple(k for k, _ in DRAWN_KEYS):
                piece_a.pop(key, None)
                piece_b.pop(key, None)
        if new_snap:
            if [round(float(v), 4) for v in piece_b["footprint"]["size"][:2]] != [round(float(v), 4)
                                                                                 for v in snap["snapped"][:2]]:
                raise AssertionError(f"{piece_b.get('id')}: size_snap.snapped is not the footprint size")
            if piece_b.get("drawn_footprint") != piece_a.get("drawn_footprint", piece_a.get("footprint")):
                raise AssertionError(f"{piece_b.get('id')}: drawn_footprint does not hold the footprint before the snap")
            if not (piece_b.get("adjusted_by_ai") or {}).get("reason"):
                raise AssertionError(f"{piece_b.get('id')}: a snapped piece needs adjusted_by_ai with a reason")
            for key in SNAP_PIECE_KEYS:
                piece_a.pop(key, None)
                piece_b.pop(key, None)
    for doc in (a, b):
        for piece in doc.get("furniture", []):
            piece.pop("asset", None)
            piece.pop("library_gap", None)
            if str(piece.get("mount_source") or "").startswith("fit:"):
                piece.pop("mount_bottom_m", None)      # 26 Oct 2026: a wall-hung fixture's height is the fit's
                piece.pop("mount_source", None)
            piece.pop("window_cap", None)              # 27 Oct 2026: the fit's record of a window in front (M2)
        for item in doc.get("decor") or []:
            item.pop("asset", None)
            item.pop("library_gap", None)              # 30 Oct 2026 (UL215): the library-first decor note
        project = doc.get("project")
        if isinstance(project, dict):
            for key in PROJECT_FIT_KEYS:
                project.pop(key, None)
            if not project and "project" not in before:
                doc.pop("project")
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        raise AssertionError("fit changed something other than furniture[].asset, decor[].asset, the size snaps, "
                             "furniture[].window_cap and project.licence_mode")


def style_family_of(profile) -> tuple[Optional[str], str]:
    """``(family, how)`` of a style profile (``style.json``; a list of profiles -> the first, as the scene
    builder renders): its ``family`` field (Milestone 7, None allowed), or for an older profile without the
    field the family keyword of its ``source_text`` (``wenart.style.profile.match_text``, the same rule)."""
    if isinstance(profile, list):
        profile = profile[0] if profile else {}
    profile = profile if isinstance(profile, dict) else {}
    if "family" in profile:
        return profile["family"], "the profile's family"
    from wenart.style.profile import match_text

    text = profile.get("source_text")
    family = match_text(text)["family"] if isinstance(text, str) and text.strip() else None
    return family, "no family field: matched in source_text"


# --------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------

def _fmt_scale(scales) -> str:
    return " / ".join(f"{s:.3f}" for s in scales)


# Fix round after P6b (module docstring): a complete HTML entity (the rule of ``wenart.run.copy.HTML_ENTITY``).
HTML_ENTITY = re.compile(r"&(?:#[0-9]+|#[xX][0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]*);")


def credit_text(asset: dict) -> str:
    """Fix round after P6b (module docstring): the report's credit line of a fitted asset: its ``attribution`` with
    complete HTML entities decoded (``&amp;`` -> ``&``), else "(no attribution recorded)"; a text without an entity
    is unchanged."""
    text = asset.get("attribution") or "(no attribution recorded)"
    return HTML_ENTITY.sub(lambda m: html.unescape(m.group(0)), str(text))


def fit_report(building: dict, title: Optional[str] = None, style_note: Optional[str] = None) -> str:
    """Markdown: one row per piece (asset, licence, scale, aspect error, method), fallbacks, licences,
    the style filter (``style_note``: the family and where it came from), the fit v2 ranking of every library
    fit (Milestone 8), bed frames and their bedding, licence flags and the CC BY credit lines."""
    pieces = building.get("furniture", [])
    rows = []
    fallbacks, licences, missing = [], Counter(), []
    credits: dict[str, str] = {}
    excluded: list[tuple[str, str, str]] = []
    ranking: list[str] = []
    frames: list[str] = []
    flags: dict[str, str] = {}
    gaps: list[str] = []
    style_fallbacks: list[str] = []
    for piece in pieces:
        asset = piece.get("asset")
        if not asset:
            missing.append(piece["id"])
            continue
        fp = piece["footprint"]
        err = "-" if asset.get("aspect_error") is None else f"{asset['aspect_error']:.3f}"
        rows.append(f"| {piece['id']} | {piece.get('room_id') or '-'} | {piece['type']} | {piece['source']} | "
                    f"{piece['status']} | {fp['size'][0]:.2f} x {fp['size'][1]:.2f} | {asset['method']} | "
                    f"{asset['asset_id']} | {asset['licence']} | {_fmt_scale(asset['fit_scale'])} | {err} | "
                    f"{asset['bbox_m'][2]:.2f} |")
        if asset.get("library_gap"):                                  # Milestone 12 (§6.4)
            gaps.append(f"- {piece['id']} ({piece['type']}, style {asset['library_gap'].get('style')}): "
                        f"{asset['library_gap'].get('used')}; {asset['library_gap'].get('reason')}")
        if asset.get("style_fallback"):
            sf = asset["style_fallback"]
            style_fallbacks.append(f"- {piece['id']} ({piece['type']}): {asset['asset_id']} of style {sf['used']} "
                                   f"(wanted {sf['wanted']}; chain {' -> '.join(str(f) for f in sf['chain'])})")
        if asset["method"] == NOT_BUILT_METHOD:
            pass
        elif asset["method"] in ("parametric", MODULE_METHOD):
            fallbacks.append((piece["id"], piece["type"], asset.get("fallback_reason", "")))
        else:
            licences[(asset["library"], asset["asset_id"], asset["licence"])] += 1
            if str(asset["licence"]).upper().startswith("CC-BY"):
                credits[asset["asset_id"]] = credit_text(asset)
            if asset.get("licence_flag"):
                flags[asset["asset_id"]] = f"{asset['licence']} ({asset['licence_flag']})"
            rank = asset.get("ranking")
            if rank:
                ranking.append(f"- {piece['id']} ({piece['type']}): {asset['asset_id']} ({asset['library']}), rank "
                               f"{rank['rank']} of {rank['tried']} tried: {'; '.join(rank['reasons'])}"
                               + (f"; passed over {', '.join(x['id'] for x in rank['passed_over'])} (caps)"
                                  if rank.get("passed_over") else ""))
            if asset.get("bed_frame"):
                bed = asset["bedding"]
                frames.append(f"- {piece['id']}: {asset['asset_id']} is a bed frame (deck {asset['deck_height_m']:.3f} m "
                              f"in the model, {bed['deck_z_m']:.3f} m fitted): parametric mattress top "
                              f"{bed['mattress_top_m']:.3f} m, inner box {bed['inner_box_m'][0]:.2f} x "
                              f"{bed['inner_box_m'][1]:.2f} m, duvet and pillows")
        excluded += [(piece["id"], x["id"], x["reason"]) for x in asset.get("excluded") or []]
    lines = [f"# Furniture fit report{': ' + title if title else ''}", ""]
    project = building.get("project")
    project_id = project.get("id", "?") if isinstance(project, dict) else str(project or "?")
    not_built = sum(1 for p in pieces if (p.get("asset") or {}).get("method") == NOT_BUILT_METHOD)
    lines.append(f"Project: {project_id}; {len(pieces)} pieces, "
                 f"{len(pieces) - len(fallbacks) - len(missing) - not_built} library fits, {len(fallbacks)} parametric "
                 f"fallbacks" + (f", {not_built} library gaps (not built)" if not_built else "") +
                 f"{', ' + str(len(missing)) + ' without fit' if missing else ''}. "
                 f"Non-uniform scale cap {round((NON_UNIFORM_CAP - 1) * 100)} %. Footprints, types, rotations, rooms "
                 f"and statuses are as in the building JSON (fitting never changes them).")
    if style_note:
        lines += ["", f"Library style filter: {style_note}"]
    if isinstance(project, dict) and project.get("licence_mode"):
        lines += ["", f"Licence mode (Milestone 13): {project['licence_mode']} "
                      f"({project.get('licence_mode_source') or 'source not recorded'}); "
                      f"{'commercial-safe entries only' if project['licence_mode'] == 'commercial' else 'non-commercial, share-alike, research-only, regional and tool_nc entries allowed (no-derivatives never)'}"]
    def flag_word(a: dict) -> str:                    # UL215: a logo-flagged asset says so
        flag = a.get("licence_flag")
        return "logo" if (flag in (None, C.NO_FLAG) and C.logo_flagged(a)) else str(flag)

    flagged_assets = sorted({(p["asset"]["asset_id"], flag_word(p["asset"]))
                             for p in pieces if p.get("asset") and p["asset"].get("method") == "library"
                             and p["asset"].get("commercial_safe") is False}
                            | {(d["asset"]["asset_id"], flag_word(d["asset"]))
                               for d in building.get("decor") or [] if d.get("asset")
                               and d["asset"].get("commercial_safe") is False})
    lines += ["", f"commercial-safe: {'yes' if not flagged_assets else 'no (flagged assets: ' + ', '.join(f'{a} [{f}]' for a, f in flagged_assets) + ')'}"]
    decor_gaps: dict = {}                             # UL215: the decor built procedurally although a type has models
    for d in building.get("decor") or []:
        g = d.get("library_gap")
        if isinstance(g, dict):
            decor_gaps.setdefault((g.get("type"), g.get("why")), []).append(str(d.get("id")))
    if decor_gaps:
        lines += ["", "## Decor library gaps (UL215: the library first; built procedurally because)", ""]
        lines += [f"- {t}: {why} ({len(ids)} item(s): {', '.join(ids[:6])}{' ...' if len(ids) > 6 else ''})"
                  for (t, why), ids in sorted(decor_gaps.items(), key=lambda kv: str(kv[0]))]
    lines += ["", "| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | "
              "scale x / y / z | aspect err | height (m) |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"] + rows
    snaps = [p for p in pieces if p.get("size_snap")]
    if snaps:
        lines += ["", "## Size snaps (Milestone 13: drawn sizes outside the product range, adjusted_by_ai)", ""]
        lines += [f"- {p['id']} ({p['type']}): {' x '.join(f'{v:.2f}' for v in p['size_snap']['drawn'][:2])} -> "
                  f"{' x '.join(f'{v:.2f}' for v in p['size_snap']['snapped'][:2])} m, {p['size_snap']['product']}; "
                  + (f"the table part {' x '.join(f'{v:.2f}' for v in p['size_snap']['part'])} m of a footprint "
                     "split into table + chairs (the depth stays); " if p['size_snap'].get('part') else "")
                  + f"{p['size_snap']['reason']}" for p in snaps]
    below = [(p["id"], p["type"], p["asset"]["method"], (p.get("library_gap") or {}).get("used"))
             for p in pieces if p.get("asset") and p["asset"].get("method") in (MODULE_METHOD, "parametric")
             and p["type"] not in C.BY_DESIGN_PARAMETRIC_TYPES + ("unknown",) and not p["asset"].get("by_design")]
    if below:
        lines += ["", "## Built below the library level (Milestone 13 ladder: module or parametric family; close "
                      "the gap with a real model)", ""]
        lines += [f"- {pid} ({ftype}): {method}: {used}" for pid, ftype, method, used in below]
    built_ins = [(p["id"], p["type"], p["asset"]["built_in"], float((p["asset"].get("module_plan") or {}).get("shift_m")
                                                                     or 0.0),
                  float((p["asset"].get("module_plan") or {}).get("shift_y_m") or 0.0))    # part 3: across the run
                 for p in pieces if (p.get("asset") or {}).get("built_in")]
    run_gaps = [(p["id"], g) for p in pieces for g in ((p.get("asset") or {}).get("module_plan") or {}).get("gaps") or []]
    if built_ins or run_gaps:                         # fix round after P3 (module docstring; part 2: shifts, reasons)
        lines += ["", "## Kitchen runs (drawn sinks built in, gaps for drawn stoves and sinks)", ""]
        lines += [f"- {pid} ({ftype}): built into the kitchen run {rid} (its sink unit, bowl and tap; not built "
                  "again)" + (f"; the sink unit stands {abs(shift):.2f} m from the drawn centre" if abs(shift) > 0.005
                              else "")
                  + (f"; {_bowl_across_text(across)}" if abs(across) > 0.005 else "")
                  for pid, ftype, rid, shift, across in built_ins]
        lines += [f"- {rid}: a {float(g.get('w_m') or 0.0):.2f} m gap for the drawn {g.get('type') or 'stove'} "
                  f"{g.get('id')} (no base unit, plinth or worktop there"
                  + (f"; {g['reason']}" if g.get("reason") else "") + ")" for rid, g in run_gaps]
    lines += ["", "## Parametric fallbacks", "", "(Milestone 13: the module builders of the ladder's step 2 are "
              "listed here too; the method column says which)"]
    if fallbacks:
        lines += [f"- {pid} ({ftype}): {reason}" for pid, ftype, reason in fallbacks]
    else:
        lines.append("- none")
    if gaps:
        lines += ["", "## Library gaps (docs/milestone12.md §6.4: no audited model; what was used instead)", ""] + gaps
    if style_fallbacks:
        lines += ["", "## Style fallbacks (§4.8)", ""] + style_fallbacks
    lines += ["", "## Library assets and licences", ""]
    if licences:
        lines += [f"- {aid} ({lib}, {lic}) x {n}" for (lib, aid, lic), n in sorted(licences.items())]
    else:
        lines.append("- none")
    # 28 Oct 2026 (user on real04: a 2.4 m table set read in feet as a coffee table, a kitchen sink as a washbasin):
    # a fitted model whose own names disagree with it (check LT, wenart/furniture/model_title.py)
    from wenart.furniture import model_title as MT
    lines += ["", f"## Library models their names or audit refuse ({MT.CHECK}: stated size, set, type or use, "
                  "audit doubt)", ""]
    lines += [f"- {v['target']}: {v['message']}" for v in MT.fitted_findings(building)] or ["- none"]
    if ranking:
        lines += ["", "## Ranking (fit v2)", "", f"Rule: {RANKING_RULE}.", ""] + ranking
    if frames:
        lines += ["", "## Bed frames with bedding", ""] + frames
    looks = [(p["id"], p["asset"]) for p in pieces if (p.get("asset") or {}).get("recolour")
             or (p.get("asset") or {}).get("colour_match")]
    if looks:
        lines += ["", "## Recolour and colour matches (Milestone 10)", ""]
        for pid, asset in looks:
            for part, spec in sorted((asset.get("recolour") or {}).items()):
                lines.append(f"- {pid}: {asset['asset_id']} {part} slots "
                             f"{[s.get('index') for s in spec.get('slots') or []]} recoloured {spec.get('colour')}")
            if asset.get("colour_match"):
                cm = asset["colour_match"]
                lines.append(f"- {pid}: {asset['asset_id']} already {cm['colour']} (Delta E {cm['delta_e']})")
    if excluded:
        lines += ["", "## Models not taken (mattress rule, style filter, design)", ""]
        lines += [f"- {pid}: {aid}: {why}" for pid, aid, why in excluded]
    for item in building.get("decor") or []:              # Milestone 8: library decor models credit too
        asset = item.get("asset") or {}
        if asset.get("method") != "library":
            continue
        if str(asset.get("licence") or "").upper().startswith("CC-BY"):
            credits[asset["asset_id"]] = credit_text(asset)
        if asset.get("licence_flag"):
            flags[asset["asset_id"]] = f"{asset['licence']} ({asset['licence_flag']})"
    if flags:
        lines += ["", "## Licence flags (recorded, not filtered: docs/milestone8.md §2)", ""]
        lines += [f"- {aid}: {text}" for aid, text in sorted(flags.items())]
    if credits:
        lines += ["", "## Attribution (CC BY 4.0)", ""] + [f"- {aid}: {text}" for aid, text in sorted(credits.items())]
    if missing:
        lines += ["", "## Pieces without a fit", ""] + [f"- {pid}" for pid in missing]
    decor = building.get("decor") or []
    if decor:
        by_kind = Counter((d["type"], (d.get("asset") or {}).get("asset_id")
                           or ("none (not built)" if d["type"] == "wall_art" else "parametric")) for d in decor)
        lines += ["", "## Decor", ""]
        lines += [f"- {kind}: {aid} x {n}" for (kind, aid), n in sorted(by_kind.items())]
        lines.append("- books are parametric by design; cushions, plants and rugs without a library decor model of "
                     "the style family (or neutral) are parametric, wall art without one is not built")
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def polyhaven_size_of(asset: dict, default: str = "1k") -> str:
    """The Poly Haven file size a fitted asset needs (Milestone 13 round 3, A1's ask): the size of the ``.gltf`` the
    scene builder loads (``asset["gltf"]`` = the catalogue entry's ``models/<id>/<id>_<size>.gltf``; pod P2 relinked
    87 entries to ``2k``), else the asset's ``resolution``, else ``default`` (the Milestone 4-12 ``1k``). A fetch at
    any other size would rewrite the asset manifest entry away from the file the build loads."""
    name = Path(str(asset.get("gltf") or "")).name
    stem = name[:-len(".gltf")] if name.endswith(".gltf") else ""
    size = stem.rsplit("_", 1)[-1] if "_" in stem else ""
    if size[:-1].isdigit() and size.endswith("k"):
        return size
    return str(asset.get("resolution") or default)


def download_fitted(building: dict, assets_dir: Path, log=print) -> dict:
    """Fetch every library asset used in ``building`` into ``assets_dir``.

    A piece whose model cannot be downloaded (offline, blocked host, unknown
    id) is re-fitted as parametric with the error in ``fallback_reason``.
    Returns ``{"fetched": [ids], "failed": {id: reason}}``.
    """
    from wenart.assets import models as M
    from wenart.assets import fetch, web

    result = {"fetched": [], "failed": {}}
    cache: dict[str, Optional[str]] = {}
    for piece in list(building.get("furniture", [])) + list(building.get("decor") or []):
        asset = piece.get("asset") or {}
        if asset.get("method") != "library":
            continue
        asset_id = asset["asset_id"]
        if asset_id not in cache:
            # Objaverse (and, Milestone 8, ABO and generated) models come only from the prep pod's cache,
            # checked against the catalogue sha256: the fetcher gets the fit's asset dict.
            extra = {"meta": asset} if asset["library"] != "polyhaven" else {}
            try:
                size = polyhaven_size_of(asset) if asset["library"] == "polyhaven" else "1k"
                M.fetch_model(asset_id, assets_dir, size=size, source=asset["library"], licence=asset["licence"],
                              **extra)
                cache[asset_id] = None
                result["fetched"].append(asset_id)
                log(f"model {asset_id:<28} ok")
            except (web.NetworkError, web.HTTPStatusError, fetch.AssetNotFound, fetch.LicenceError, KeyError,
                    RuntimeError) as exc:
                cache[asset_id] = f"{type(exc).__name__}: {exc}"
                result["failed"][asset_id] = cache[asset_id]
                log(f"model {asset_id:<28} FAILED: {exc}")
        if cache[asset_id] is not None:
            if piece.get("kind") == "decor":
                piece["asset"] = None            # decor: the parametric mesh, reason in the log above
            else:
                piece["asset"] = parametric_fit(
                    piece, f"download of {asset_id} failed ({cache[asset_id]}); parametric fallback",
                    candidates=asset.get("candidates"), excluded=asset.get("excluded"),
                    style_family=asset.get("style_family"))
    return result


def locked_check(source_path: Path, fitted: dict, completion_path: Optional[Path] = None) -> tuple[list[str], str]:
    """``(violations, how)``: ``wenart.furniture.locked.check`` of the drawn furniture of ``source_path`` (the
    building before the layout) against the fitted building, mode and kept rooms from ``completion.json``
    (``complete`` and none when it is not given)."""
    from wenart import building as B
    from wenart.furniture import locked

    completion = json.loads(completion_path.read_text(encoding="utf-8")) if completion_path else None
    mode, keep = locked.mode_of(completion), locked.keep_rooms_of(completion)
    problems = locked.check(B.load(source_path), fitted, mode, keep_rooms=keep)
    how = (f"source {source_path}, mode {mode}" + (f", kept rooms {', '.join(keep)}" if keep else "")
           + (f" (from {completion_path})" if completion_path else " (no completion.json: complete)"))
    return problems, how


def project_dir_of(building: dict, given: Optional[str] = None) -> Optional[Path]:
    """The project folder whose ``brief.yaml`` the fit reads: ``given`` (``--project``), else the building's
    ``project.source_folder`` when that folder exists (relative to the working directory, as the jobs run), else
    None (no brief: the defaults)."""
    if given:
        return Path(given)
    project = building.get("project") if isinstance(building.get("project"), dict) else {}
    folder = project.get("source_folder")
    if isinstance(folder, str) and folder.strip() and Path(folder).is_dir():
        return Path(folder)
    return None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="fit catalogue assets to the furniture of a building JSON")
    parser.add_argument("building", help="building.json from the ingest pipeline (or the layout step)")
    parser.add_argument("--catalog", default=str(C.CATALOG_PATH), help="catalog.json (default: the package one)")
    parser.add_argument("--out", required=True, help="where to write the fitted building JSON")
    parser.add_argument("--assets", default=None, help="assets folder; when given, the fitted models are downloaded")
    parser.add_argument("--report", default=None, help="markdown report path (default: <out stem>_report.md)")
    parser.add_argument("--no-download", action="store_true", help="do not download even when --assets is given")
    parser.add_argument("--style", default=None,
                        help="style.json (refit only): library models only of its style family or neutral")
    parser.add_argument("--source", default=None,
                        help="building.json before the layout (refit only): run the locked check of the drawn "
                             "furniture; a violation exits 1 (docs/milestone10.md §2.7)")
    parser.add_argument("--completion", default=None,
                        help="completion.json of the layout stage (the check's mode and kept rooms)")
    parser.add_argument("--licence-mode", default=None, choices=list(C.LICENCE_MODES),
                        help="Milestone 13: the library licence mode (default: the building's project.licence_mode, "
                             "else env WENART_LICENCE_MODE, else the brief's library.licence_mode, else commercial)")
    parser.add_argument("--project", default=None,
                        help="the project folder with brief.yaml (default: the building's project.source_folder when "
                             "it exists): the licence mode and the furnished_rooms settings of the size snap")
    args = parser.parse_args(argv)

    from wenart import brief as BR
    from wenart import building as B

    building = B.load(args.building)
    catalog = C.load(Path(args.catalog))
    family, style_note, profile = None, None, None
    if args.style:
        profile = json.loads(Path(args.style).read_text(encoding="utf-8"))
        family, how = style_family_of(profile)
        style_note = (f"family {family!r} ({how}, {args.style}): library models only when their styles hold "
                      f"{family!r} or {C.NEUTRAL!r}" if family else
                      f"no style family ({how}, {args.style}): every library model may be used")
        print(f"style filter: {style_note}")
    if isinstance(profile, list):
        profile = profile[0] if profile else None
    project_dir = project_dir_of(building, args.project)
    brief = BR.load_brief(project_dir) if project_dir is not None else None
    fitted = fit_building(building, catalog, style_family=family, style=profile if isinstance(profile, dict) else None,
                          assets_dir=Path(args.assets) if args.assets and os.environ.get("WENART_TASTE", "1") != "0"
                          else None,
                          mode=args.licence_mode, brief=brief)
    project = fitted.get("project") or {}
    print(f"licence mode: {project.get('licence_mode')} ({project.get('licence_mode_source')}); size snap "
          f"{'on' if (project.get('size_snap') or {}).get('on') else 'off'} ({(project.get('size_snap') or {}).get('why')}"
          f"{'; brief ' + str(project_dir) if project_dir is not None else '; no brief'})")
    if args.assets and not args.no_download:
        result = download_fitted(fitted, Path(args.assets))
        if result["failed"]:
            print(f"{len(result['failed'])} model download(s) failed; those pieces use the parametric fallback")
    assert_only_assets_changed(building, fitted)
    out = Path(args.out)
    report_path = Path(args.report) if args.report else out.with_name(out.stem + "_report.md")
    report = fit_report(fitted, title=out.stem, style_note=style_note)
    if args.source:
        problems, how = locked_check(Path(args.source), fitted, Path(args.completion) if args.completion else None)
        report += "\n## Locked check (docs/milestone10.md §2.7)\n\n" + how + "\n\n" + (
            "\n".join(f"- {p}" for p in problems) if problems else "- pass") + "\n"
        if problems:
            report_path.write_text(report, encoding="utf-8")
            print(f"locked check: {len(problems)} violation(s); {out} not written (report {report_path})",
                  file=sys.stderr)
            for line in problems:
                print(f"  {line}", file=sys.stderr)
            return 1
    B.save(fitted, out)
    report_path.write_text(report, encoding="utf-8")
    methods = Counter(p["asset"]["method"] for p in fitted.get("furniture", []))
    print(f"{len(fitted.get('furniture', []))} pieces: {methods.get('library', 0)} library, "
          f"{methods.get('parametric', 0)} parametric -> {out} (report {report_path})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
