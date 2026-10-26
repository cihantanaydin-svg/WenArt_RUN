# Argus: the audit of real06

Argus checks everything a run makes, not only the looks: what the documents hold against the model (nothing lost between stages, every label and symbol used), the run itself (stages, warnings nobody acted on, tests, time), the model's sense, the inspector's and the judge's findings. Every finding has a kind (where such problems arise and the guards that catch them), an owner (the stage that caused it) and, where the run can carry it out, a fix.

Score **9.5** / 100 (100 = nothing open; 10 points per critical, 3 per major, 0.5 per minor). Open: 28 critical, 63 major, 15 minor; 19 notes.

## Lines

| line | findings | checked | note |
|---|---|---|---|
| conservation | 21 | {"reading": 250, "fit": 250, "layout": 260, "decor": 260, "agent": 260, "final": 260, "build": 259} |  |
| process | 35 | {"stages": 27, "warnings": 144, "test_reports": 1, "missing_records": ["model_review"]} |  |
| model | 0 | {} | no model_review.json |
| inspector | 118 | {"round": 4, "seen": 14, "visitor": 4, "fixed": 1, "handed": 0, "open": 117, "dropped": 3, "architect_open": 7, "architect_open_major": 4} |  |
| judge | 0 | {} | no rubric_per_view.json (the big loop did not measure) |
| sense | 0 | {"rooms": 12, "joins": 13, "reached": 12} |  |

## Problem kinds

| kind | critical | major | minor | with a fix | owners | arises | guards |
|---|---|---|---|---|---|---|---|
| geometry | 26 | 25 | 1 | 0 | scene, build, blocked_opening, floating, collision, clearance | layout, agent | code critic (F*, G*), architect F-rules |
| misread | 1 | 6 | 2 | 0 | building, scene, missing_member, room_type | reading | plan_vs_model (B*), the room-sense rules (G*, R*), model review M7 |
| lost | 1 | 4 | 1 | 3 | agent, site, build, building, cameras | any stage boundary: reading -> building, fit, layout, build, render | ledger (A*), conservation (C*), plan_vs_model (B*), process (P*) |
| taste | 0 | 9 | 10 | 4 | building, scene, fit, drawn_layout, collision, wrong_model | fit, decor, opening models | judge (J*), visitor checks Q5, Q7, the fit's matched sets |
| other | 0 | 8 | 0 | 0 | untyped | - |  |
| no_sense | 0 | 6 | 0 | 2 | scene, architect | architect, build | sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*) |
| process | 0 | 3 | 1 | 1 | building, tests, scheduler | scheduler | process (P*) |
| untyped | 0 | 1 | 0 | 1 | reading | reading | conservation C4, ledger, the reading's AI questions |
| silent | 0 | 1 | 0 | 0 | scene | any stage | process P2 (warnings that say something was left out) |

## geometry: pieces through walls or each other, blocked doors and windows, no walkway

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L0_001 | no 0.60 m walkway from door d_L0_001 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | d_L0_002 | no 0.60 m walkway from door d_L0_002 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_005 | inspector:G11 | clearance |  |
| critical | d_L0_004 | no 0.60 m walkway from door d_L0_004 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | d_L1_004 | no 0.60 m walkway from door d_L1_004 to door d_L1_006 | inspector:G11 | clearance |  |
| critical | d_L1_006 | no 0.60 m walkway from door d_L1_006 to door d_L1_009 | inspector:G11 | clearance |  |
| critical | f_L0_018 | table_coffee blocks door o_L0_006 | inspector:F7, inspector:F8 | blocked_opening |  |
| critical | f_L0_029 | sink_kitchen blocks door o_L0_004 | inspector:F3, inspector:F7, inspector:G8, inspector:G11 | drawn_layout |  |
| critical | f_L0_035 | ottoman blocks door o_L0_003 | inspector:F7, inspector:F9, inspector:G2 | blocked_opening |  |
| critical | f_L0_040 | kitchen_counter blocks door o_L0_001 | inspector:F7, inspector:F9, inspector:G11 | drawn_layout |  |
| critical | f_L1_007 | desk blocks door d_L1_005 | inspector:F3, inspector:F7, inspector:F9 | drawn_layout |  |
| critical | f_L1_009 | bed_double blocks door o_L1_001 | inspector:F7, inspector:G5, inspector:G11 | blocked_opening |  |
| critical | f_L1_012 | bed_double: the headboard stands in the room (0.06 m off) | inspector:F3 | off_wall |  |
| critical | f_L1_013 | sofa blocks door o_L1_003 | inspector:F6, inspector:F7 | clearance |  |
| critical | f_L1_017 | table_dining blocks door d_L1_001 | inspector:F7 | blocked_opening |  |
| critical | f_L1_019 | chair blocks door d_L1_001 | inspector:F7, inspector:G6 | blocked_opening |  |
| critical | f_L1_021 | chair blocks door d_L1_001 | inspector:F7 | blocked_opening |  |
| critical | f_L1_031 | floor_lamp blocks door o_L1_003 | inspector:F7 | blocked_opening |  |
| critical | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | o_L0_003 | no 0.60 m walkway from door o_L0_003 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | o_L0_004 | no 0.60 m walkway from door o_L0_004 to door d_L0_005 | inspector:G11 | clearance |  |
| critical | o_L0_005 | no 0.60 m walkway from door o_L0_005 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | o_L0_006 | no 0.60 m walkway from door o_L0_006 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | o_L1_002 | no 0.60 m walkway from door o_L1_002 to door d_L1_004 | inspector:G11 | clearance |  |
| critical | o_L1_003 | no 0.60 m walkway from door o_L1_003 to door o_L1_005 | inspector:G11 | clearance |  |
| critical | o_L1_005 | no 0.60 m walkway from door o_L1_005 to door d_L1_006 | inspector:G11 | clearance |  |
| major | L0:S2 | scene check S2 on L0: 5 of 41 failed | process:P5 | build |  |
| major | d_L1_001 | the main walkway from the entrance door is below 0.80 m between doors d_L1_001 and d_L1_002 | inspector:G11 | clearance |  |
| major | f_L0_002 | kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m | inspector:G8, inspector:G11 | fixture_clearance |  |
| major | f_L0_007 | chair f_L0_007: 0.12 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | inspector:G6 | clearance |  |
| major | f_L0_008 | chair f_L0_008 overlaps chair f_L0_007 by 0.07 m² | inspector:F9, inspector:G6 | collision |  |
| major | f_L0_009 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | inspector:F8 | floating |  |
| major | f_L0_010 | chair f_L0_010 is 180° off the table f_L0_006 (needs ≤ 45°) | inspector:G6 | orientation |  |
| major | f_L0_011 | chair f_L0_011: 0.45 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | inspector:G6 | clearance |  |
| major | f_L0_014 | sofa_corner f_L0_014: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_020 | chair f_L0_020 is 50° off the table f_L0_019 (needs ≤ 45°) | inspector:G6 | orientation |  |
| major | f_L0_021 | chair f_L0_021: 0.37 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | inspector:G6 | clearance |  |
| major | f_L0_023 | chair f_L0_023 is 50° off the table f_L0_022 (needs ≤ 45°) | inspector:G6 | orientation |  |
| major | f_L0_026 | chair f_L0_026 is 50° off the table f_L0_025 (needs ≤ 45°) | inspector:G6 | orientation |  |
| major | f_L0_028 | armchair f_L0_028: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_036 | ottoman f_L0_036 overlaps sofa_corner f_L0_014 by 0.24 m² | inspector:F9 | collision |  |
| major | f_L0_037 | ottoman f_L0_037 overlaps sofa_corner f_L0_014 by 0.25 m² | inspector:F9 | collision |  |
| major | f_L0_038 | ottoman f_L0_038 overlaps sofa_corner f_L0_014 by 0.25 m² | inspector:F9 | collision |  |
| major | f_L0_039 | kitchen_counter f_L0_039 overlaps kitchen_counter f_L0_002 by 0.44 m² | inspector:F9, inspector:G11 | collision |  |
| major | f_L1_006 | bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m | inspector:G5, inspector:G11 | clearance |  |
| major | f_L1_010 | nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m² | inspector:F9, inspector:G4 | collision |  |
| major | f_L1_016 | A white object (resembling a book or tray) is floating in mid-air above the sofa cushions, not resting on the seat or a table. | inspector:D1 | decor_look |  |
| major | f_L1_018 | chair does not face its group (f_L1_017) | inspector:F4, inspector:G6 | orientation |  |
| major | f_L1_024 | shower f_L1_024 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05) | inspector:G12 | blocked_opening |  |
| major | f_L1_029 | washbasin: its back is not on a wall (0.07 m off) | inspector:F3 | off_wall |  |
| major | o_L1_001 | the main walkway from the entrance door is below 0.80 m between doors o_L1_001 and d_L1_005 | inspector:G11 | clearance |  |
| minor | dec_L1_017 | decor that could not rest on its host: decor plant_small dec_L1_017 on f_L1_034: not rested (no top found on the built host (attempt 2)); not built | process:P2, process:P5 | scene |  |

## lost: something the documents or an earlier stage hold is missing from the model (a labelled veranda, drawn site symbols, a room, an opening, a piece)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | sa_L0_veranda | the documents label a site area 'VERANDA' and the model does not build it (open balcony outside the outer walls (no walls drawn around it)) | conservation:C5 | site | build_outdoor_space |
| major | BALKON | a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'BALKON' at (9138484.48, 5090593.07) m lies outside the outer walls: an open balcony, recorded in site, not a room | process:P2 | building | build_outdoor_space |
| major | VERANDA | a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'VERANDA' at (9138464.73, 5090593.37) m lies outside the outer walls: an open balcony, recorded in site, not a room | process:P2 | building | build_outdoor_space |
| major | f_L0_044 | furniture f_L0_044 (shower) of the decor stage is missing after the agent stage and nothing there names it | conservation:C1 | agent |  |
| major | site | items the reading found and no stage used: site: 2 cases, e.g. site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0) | process:P2 | building |  |
| minor | entity types not read | source entities the reading did not read (the ledger checks what they hold): real06.dwg: entity types not read: ATTDEF x28 | process:P2 | building |  |
| info | 2 elements | not built: the model of f_L1_009 has its own cushions/pillows (dec_L1_009, dec_L1_010) | conservation:C6 | build |  |
| info | 42 elements | not built: site decor of kind 'other' is not built (no model) (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006, sd_L0_007, sd_L0_008 ...) | conservation:C6 | build |  |
| info | 7 elements | not built: untyped (CLAUDE.md: no untyped piece is built) (f_L0_012, f_L0_015, f_L0_016, f_L1_014, f_L1_015, f_L1_023, f_L1_026) | conservation:C6 | build |  |
| info | dec_L1_012 | not built: its host f_L1_010 is not built (dec_L1_012) | conservation:C6 | build |  |
| info | f_L0_002 | not built: architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_039 (kitchen_counter): one object read twice; built once (f_L0_002) | conservation:C6 | build |  |
| info | f_L0_003 | not built: drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) (f_L0_003) | conservation:C6 | build |  |
| info | f_L0_004 | not built: the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_039, f_L0_040 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png (f_L0_004) | conservation:C6 | build |  |
| info | f_L0_005 | not built: outline 3.89 x 2.12 m around 7 other piece(s) (f_L0_006, f_L0_007, f_L0_008, f_L0_009, f_L0_010, f_L0_011): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_005) | conservation:C6 | build |  |
| info | f_L0_013 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 2: Fixes c:NR:f_L0_013: the recognition crop shows a drawn bathtub + washbasin unit (the bathroom_set fixtures), not a separate 2.54 m furniture piece, so the untyped symbol is not furniture. (f_L0_013) | conservation:C6 | build |  |
| info | f_L0_017 | not built: outline 1.52 x 0.78 m around 2 other piece(s) (f_L0_015, f_L0_016): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_017) | conservation:C6 | build |  |
| info | f_L1_001 | not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001) | conservation:C6 | build |  |
| info | f_L1_002 | not built: cluster larger than 4.5 m on a side: a group of drawn pieces, not built (f_L1_002) | conservation:C6 | build |  |
| info | f_L1_003 | not built: 2.25 x 0.18 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_003) | conservation:C6 | build |  |
| info | f_L1_004 | not built: 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_004) | conservation:C6 | build |  |
| info | f_L1_008 | not built: drawn inside bed_double f_L1_006 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) (f_L1_008) | conservation:C6 | build |  |
| info | f_L1_010 | not built: architect F5: it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built (f_L1_010) | conservation:C6 | build |  |
| info | f_L1_011 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 1: The 2.42 x 0.98 m drawn outline is the dashed dimension/outline box around the drawn corner tub and washbasin, not a separate piece of furniture; the code's own size/zone table rejects bathtub and gives stair, so it is a misread outline. (f_L1_011) | conservation:C6 | build |  |
| info | r_L0_oda | room Oda (2.1 m2) has no view: no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2) | process:P6 | cameras |  |
| info | sa_L0_veranda | not built: exterior label: its surface is built from site.paving / parking / grass (sa_L0_veranda) | conservation:C6 | build |  |

## misread: the reading typed, sized or placed something wrong (armchairs read as tables with chairs, a vanity read as a kitchen counter)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | r_L1_ebeveyn_y_odasi | The room is labeled as a bedroom but contains two dining tables and multiple chairs, which are not appropriate fixtures for a bedroom. | inspector:Q4 | room_type |  |
| major | derived ridge # m vs the drawn ridge height # m (# cm) | the model differs from the drawn section or elevation: derived ridge 8.530 m vs the drawn ridge height 7.770 m (+76 cm): the pitches are kept | process:P2 | scene |  |
| major | r_L0_banyo | bathroom without a washbasin | inspector:G10 | missing_member |  |
| major | r_L0_mutfak | kitchen r_L0_mutfak has no fridge (fridge) | inspector:G9 | missing_member |  |
| major | r_L1_banyo | bathroom without a washbasin | inspector:G10 | missing_member |  |
| major | r_L1_dus | bathroom without a washbasin | inspector:G10 | missing_member |  |
| major | roof vs the drawn section at s # m | the model differs from the drawn section or elevation: roof vs the drawn section at s # m: 11 cases, e.g. roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm) | process:P2 | scene |  |
| minor | room '...' has more labels | one room outline holds the labels of two rooms (a wall not read?): room '...' has more labels: 2 cases, e.g. L0: room 'Salon' has more labels: YEMEK BÖLÜMÜ; the label with the largest printed area (else the first) kept | process:P2 | building |  |
| minor | sym_L1_008 | a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified | process:P2 | building |  |

## no_sense: the model makes no sense to a visitor (a door into the air, a basin at knee height, stairs running into each other, a railing across a door)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | W2:win_L0_001 | the architect's question W2 (windows to the outside) is open for win_L0_001: win_L0_001 sits in the wall between r_L0_mutfak (kitchen) and r_L0_salon (living) | process:P3 | architect |  |
| major | W2:win_L1_004 | the architect's question W2 (windows to the outside) is open for win_L1_004: win_L1_004 sits in the wall between r_L1_soyunma_odasi (dressing) and r_L1_dus (bathroom) | process:P3 | architect |  |
| major | W2:win_L1_005 | the architect's question W2 (windows to the outside) is open for win_L1_005: win_L1_005 sits in the wall between r_L1_soyunma_odasi (dressing) and r_L1_dus (bathroom) | process:P3 | architect |  |
| major | W2:win_L1_008 | the architect's question W2 (windows to the outside) is open for win_L1_008: win_L1_008 sits in the wall between r_L1_oda_2 (living) and r_L1_hol (hall) | process:P3 | architect |  |
| major | d_L0_002 | an opening of the documents is not cut through its wall: d_L0_002: door ray hits splashback_r_L0_mutfak (splashback); the opening is not cut through its wall | process:P2, process:P5 | scene | clear_opening |
| major | o_L0_001 | an opening of the documents is not cut through its wall: o_L0_001: door ray hits splashback_r_L0_mutfak (splashback); the opening is not cut through its wall | process:P2, process:P5 | scene | clear_opening |

## other: not classified yet: a new kind to name

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | f_L0_012 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_003_ctx.png) | inspector:NR | untyped |  |
| major | f_L0_015 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_006_ctx.png) | inspector:NR | untyped |  |
| major | f_L0_016 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_007_ctx.png) | inspector:NR | untyped |  |
| major | f_L1_002 | untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | inspector:NR | untyped |  |
| major | f_L1_014 | untyped drawn piece left for review: drawn piece 2.27 x 0.85 m in r_L1_soyunma_odasi has no type (AI passes: stair, unknown): not built (plan crop recognition/crops/sym_L1_009_ctx.png) | inspector:NR | untyped |  |
| major | f_L1_015 | untyped drawn piece left for review: drawn piece 2.27 x 0.85 m in r_L1_soyunma_odasi has no type (AI passes: stair, unknown): not built (plan crop recognition/crops/sym_L1_010_ctx.png) | inspector:NR | untyped |  |
| major | f_L1_023 | untyped drawn piece left for review: drawn piece 1.20 x 0.55 m in r_L1_oda_2 has no type (AI passes: desk, dresser): not built (plan crop recognition/crops/sym_L1_014_ctx.png) | inspector:NR | untyped |  |
| major | f_L1_026 | untyped drawn piece left for review: drawn piece 0.58 x 0.58 m in r_L1_ebeveyn_y_odasi has no type (AI passes: floor_lamp, table_coffee): not built (plan crop recognition/crops/sym_L1_017_ctx.png) | inspector:NR | untyped |  |

## process: the run itself: a stage failed or was skipped, a test failed, time was left unused, a question stayed unanswered

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | run | the run ended 31 min before its deadline with 122 open major point(s): the time could have gone to more fix cycles | process:P8 | scheduler | more_cycles |
| major | test_index_pass_contains_every_visible_proxy[real06] | test tests.gpu.test_render::test_index_pass_contains_every_visible_proxy[real06] failure: AssertionError: real06: proxies planned in the frustum but absent from the index pass: [('cam_r_L0_banyo_3', ['f_L0_046']), ('cam_r_L1_banyo_3', ['f_L1_038'])] assert not [('cam_r_L0_banyo_3', ['f_L0_046']), ('cam_r_L1_banyo_3', ['f_L1_038'])] | process:P4 | tests |  |
| major | test_passes_exist_and_depth_is_plausible[real06] | test tests.gpu.test_render::test_passes_exist_and_depth_is_plausible[real06] failure: AssertionError: real06: views with missing files or an implausible depth pass: [('cam_r_L0_salon_2', 'depth not 0.1 < min < max < 60 m', {'min': 1.6010942459106445, 'max': 197.65771484375, 'mean': 3.4686529636383057, 'coverage': 0.9973885995370371})] assert not [('cam_r_L0_salon_2', 'depth not 0.1 < min < max < 6 | process:P4 | tests |  |
| minor | elevation r# (all) | a check that could not run: elevation r# (all): 4 cases, e.g. elevation r1 (all): its openings are not checked against the plans (the side needs the north arrow) | process:P2 | building |  |

## silent: a stage noted a problem in a warning and nothing acted on it

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | inferred trees | a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 20, sightline 36, window 67, front 27; most by window; the first pass placed 0, the second pass with the window band narrowed to 4 m added 0) | process:P2 | scene |  |

## taste: the house does not look designed (pieces that do not match, plain or dated rooms, a garage door look)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | f_L0_006 | table_dining f_L0_006 and chair f_L0_007 cut each other by 0.224 m (allowed 0.010 m) | inspector:S2, inspector:D2 | collision |  |
| major | f_L0_007 | A folding garden chair is placed indoors in the living room, which is inappropriate for the interior setting and clashes with the other furniture. | inspector:Q5 | wrong_model |  |
| major | f_L0_019 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | inspector:D2 | wrong_model |  |
| major | f_L0_022 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | inspector:D2 | wrong_model |  |
| major | f_L0_025 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | inspector:D2 | wrong_model |  |
| major | f_L0_039 | kitchen_counter f_L0_039 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece) | inspector:S2 | drawn_layout |  |
| major | f_L0_047 | The washbasin model is a crude, low-poly block with a simple rectangular cutout and a floating blue knob, lacking the detail and form of a real sink. | inspector:D2 | wrong_model |  |
| major | f_L1_017 | The dining table is accompanied by a mix of different chair models (white and wooden), which do not belong together as a cohesive set. | inspector:Q5 | wrong_model |  |
| major | f_L1_020 | The second dining table is accompanied by a mix of different chair models (white and wooden), which do not belong together as a cohesive set. | inspector:Q5 | wrong_type |  |
| minor | d_L0_006 | built parametric (library gap): opening d_L0_006: parametric in the style's finish (no library entrance fits 2.95 x 2.10 m: the parametric opening in the style's finish) | process:P2 | scene |  |
| minor | f_L0_029 | sink_kitchen f_L0_029 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_041 | wall_cabinet f_L0_041 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_042 | wall_cabinet f_L0_042 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_043 | wall_cabinet f_L0_043 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | o_L0_002 | no library model: built parametric or not at all: opening o_L0_002: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |
| minor | r_L1_dus | a group the room should have found no place: r_L1_dus: completion added nothing, nothing fits: bathroom_set: no place passes the checks | process:P2 | building |  |
| minor | r_L1_hol | a group the room should have found no place: r_L1_hol: completion added nothing, nothing fits: entrance: no place passes the checks | process:P2 | building |  |
| minor | win_L0_006 | no library model: built parametric or not at all: opening win_L0_006: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |
| minor | win_L1_001 | no library model: built parametric or not at all: opening win_L1_001: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 0.95 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |

## untyped: a drawn element no rule or model typed, so nothing builds it ('other', 'unknown')

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | 42 site_symbols | 42 drawn site symbols (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006 ...) that no rule or model typed ('other'): nothing builds them and nothing explains them | conservation:C4 | reading | type_site_symbols |

## Prevention: the kinds to guard

Each open kind with the findings no fix of the run covers, or that came back from an earlier run: these need a new rule or check (a general one, for every project), not a one-off patch.

- **geometry** (52 open, 0 with a fix; arises: layout, agent; guards: code critic (F*, G*), architect F-rules)
  - process:P5 L0:S2: scene check S2 on L0: 5 of 41 failed
  - inspector:F7 f_L0_018: table_coffee blocks door o_L0_006
  - inspector:F7 f_L0_035: ottoman blocks door o_L0_003
  - inspector:F8 f_L0_009: table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)
  - inspector:F9 f_L0_008: chair f_L0_008 overlaps chair f_L0_007 by 0.07 m²
  - inspector:F9 f_L0_036: ottoman f_L0_036 overlaps sofa_corner f_L0_014 by 0.24 m²
  - inspector:F9 f_L0_037: ottoman f_L0_037 overlaps sofa_corner f_L0_014 by 0.25 m²
  - inspector:F9 f_L0_038: ottoman f_L0_038 overlaps sofa_corner f_L0_014 by 0.25 m²
  - inspector:G6 f_L0_007: chair f_L0_007: 0.12 m from the table edge to the wall or piece behind, needs ≥ 0.81 m
  - inspector:G6 f_L0_010: chair f_L0_010 is 180° off the table f_L0_006 (needs ≤ 45°)
  - inspector:G6 f_L0_011: chair f_L0_011: 0.45 m from the table edge to the wall or piece behind, needs ≥ 0.81 m
  - inspector:G6 f_L0_020: chair f_L0_020 is 50° off the table f_L0_019 (needs ≤ 45°)
  - inspector:G6 f_L0_021: chair f_L0_021: 0.37 m from the table edge to the wall or piece behind, needs ≥ 0.81 m
  - inspector:G6 f_L0_023: chair f_L0_023 is 50° off the table f_L0_022 (needs ≤ 45°)
  - inspector:G6 f_L0_026: chair f_L0_026 is 50° off the table f_L0_025 (needs ≤ 45°)
  - inspector:G11 d_L0_001: no 0.60 m walkway from door d_L0_001 to door d_L0_006
  - inspector:G11 d_L0_002: no 0.60 m walkway from door d_L0_002 to door d_L0_006
  - inspector:G11 d_L0_004: no 0.60 m walkway from door d_L0_004 to door d_L0_006
  - inspector:G11 f_L0_014: sofa_corner f_L0_014: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - inspector:G11 f_L0_028: armchair f_L0_028: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - inspector:G11 o_L0_001: no 0.60 m walkway from door o_L0_001 to door d_L0_006
  - inspector:G11 o_L0_003: no 0.60 m walkway from door o_L0_003 to door d_L0_006
  - inspector:G11 o_L0_005: no 0.60 m walkway from door o_L0_005 to door d_L0_006
  - inspector:G11 o_L0_006: no 0.60 m walkway from door o_L0_006 to door d_L0_006
  - inspector:F7 f_L0_029: sink_kitchen blocks door o_L0_004
  - inspector:F7 f_L0_040: kitchen_counter blocks door o_L0_001
  - inspector:F9 f_L0_039: kitchen_counter f_L0_039 overlaps kitchen_counter f_L0_002 by 0.44 m²
  - inspector:G8 f_L0_002: kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m
  - inspector:G11 d_L0_003: no 0.60 m walkway from door d_L0_003 to door d_L0_005
  - inspector:G11 o_L0_004: no 0.60 m walkway from door o_L0_004 to door d_L0_005
  - inspector:F3 f_L1_012: bed_double: the headboard stands in the room (0.06 m off)
  - inspector:F4 f_L1_018: chair does not face its group (f_L1_017)
  - inspector:F7 f_L1_017: table_dining blocks door d_L1_001
  - inspector:F7 f_L1_019: chair blocks door d_L1_001
  - inspector:F7 f_L1_021: chair blocks door d_L1_001
  - inspector:G11 d_L1_001: the main walkway from the entrance door is below 0.80 m between doors d_L1_001 and d_L1_002
  - inspector:F7 f_L1_007: desk blocks door d_L1_005
  - inspector:F7 f_L1_009: bed_double blocks door o_L1_001
  - inspector:F9 f_L1_010: nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m²
  - inspector:G5 f_L1_006: bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m
  - inspector:G11 o_L1_001: the main walkway from the entrance door is below 0.80 m between doors o_L1_001 and d_L1_005
  - inspector:G11 d_L1_004: no 0.60 m walkway from door d_L1_004 to door d_L1_006
  - inspector:G11 d_L1_006: no 0.60 m walkway from door d_L1_006 to door d_L1_009
  - inspector:G11 o_L1_002: no 0.60 m walkway from door o_L1_002 to door d_L1_004
  - inspector:G12 f_L1_024: shower f_L1_024 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05)
  - inspector:F7 f_L1_013: sofa blocks door o_L1_003
  - inspector:F7 f_L1_031: floor_lamp blocks door o_L1_003
  - inspector:G11 o_L1_003: no 0.60 m walkway from door o_L1_003 to door o_L1_005
  - inspector:G11 o_L1_005: no 0.60 m walkway from door o_L1_005 to door d_L1_006
  - inspector:F3 f_L1_029: washbasin: its back is not on a wall (0.07 m off)
  - inspector:D1 f_L1_016: A white object (resembling a book or tray) is floating in mid-air above the sofa cushions, not resting on the seat or a table.
- **misread** (9 open, 0 with a fix; arises: reading; guards: plan_vs_model (B*), the room-sense rules (G*, R*), model review M7)
  - process:P2 roof vs the drawn section at s # m: the model differs from the drawn section or elevation: roof vs the drawn section at s # m: 11 cases, e.g. roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm)
  - process:P2 derived ridge # m vs the drawn ridge height # m (# cm): the model differs from the drawn section or elevation: derived ridge 8.530 m vs the drawn ridge height 7.770 m (+76 cm): the pitches are kept
  - inspector:G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge)
  - inspector:G10 r_L0_banyo: bathroom without a washbasin
  - inspector:G10 r_L1_dus: bathroom without a washbasin
  - inspector:G10 r_L1_banyo: bathroom without a washbasin
  - inspector:Q4 r_L1_ebeveyn_y_odasi: The room is labeled as a bedroom but contains two dining tables and multiple chairs, which are not appropriate fixtures for a bedroom.
- **lost** (6 open, 3 with a fix; arises: any stage boundary: reading -> building, fit, layout, build, render; guards: ledger (A*), conservation (C*), plan_vs_model (B*), process (P*))
  - conservation:C1 f_L0_044: furniture f_L0_044 (shower) of the decor stage is missing after the agent stage and nothing there names it
  - process:P2 site: items the reading found and no stage used: site: 2 cases, e.g. site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0)
- **taste** (19 open, 4 with a fix; arises: fit, decor, opening models; guards: judge (J*), visitor checks Q5, Q7, the fit's matched sets)
  - inspector:S2 f_L0_039: kitchen_counter f_L0_039 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece)
  - inspector:S2 f_L0_006: table_dining f_L0_006 and chair f_L0_007 cut each other by 0.224 m (allowed 0.010 m)
  - inspector:Q5 f_L0_007: A folding garden chair is placed indoors in the living room, which is inappropriate for the interior setting and clashes with the other furniture.
  - inspector:D2 f_L0_019: The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set.
  - inspector:D2 f_L0_022: The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set.
  - inspector:D2 f_L0_025: The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set.
  - inspector:D2 f_L0_047: The washbasin model is a crude, low-poly block with a simple rectangular cutout and a floating blue knob, lacking the detail and form of a real sink.
  - inspector:Q5 f_L1_017: The dining table is accompanied by a mix of different chair models (white and wooden), which do not belong together as a cohesive set.
  - inspector:Q5 f_L1_020: The second dining table is accompanied by a mix of different chair models (white and wooden), which do not belong together as a cohesive set.
- **other** (8 open, 0 with a fix; arises: -; guards: none)
  - inspector:NR f_L0_012: untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_003_ctx.png)
  - inspector:NR f_L0_015: untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_006_ctx.png)
  - inspector:NR f_L0_016: untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_007_ctx.png)
  - inspector:NR f_L1_002: untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built
  - inspector:NR f_L1_014: untyped drawn piece left for review: drawn piece 2.27 x 0.85 m in r_L1_soyunma_odasi has no type (AI passes: stair, unknown): not built (plan crop recognition/crops/sym_L1_009_ctx.png)
  - inspector:NR f_L1_015: untyped drawn piece left for review: drawn piece 2.27 x 0.85 m in r_L1_soyunma_odasi has no type (AI passes: stair, unknown): not built (plan crop recognition/crops/sym_L1_010_ctx.png)
  - inspector:NR f_L1_023: untyped drawn piece left for review: drawn piece 1.20 x 0.55 m in r_L1_oda_2 has no type (AI passes: desk, dresser): not built (plan crop recognition/crops/sym_L1_014_ctx.png)
  - inspector:NR f_L1_026: untyped drawn piece left for review: drawn piece 0.58 x 0.58 m in r_L1_ebeveyn_y_odasi has no type (AI passes: floor_lamp, table_coffee): not built (plan crop recognition/crops/sym_L1_017_ctx.png)
- **no_sense** (6 open, 2 with a fix; arises: architect, build; guards: sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*))
  - process:P3 W2:win_L0_001: the architect's question W2 (windows to the outside) is open for win_L0_001: win_L0_001 sits in the wall between r_L0_mutfak (kitchen) and r_L0_salon (living)
  - process:P3 W2:win_L1_004: the architect's question W2 (windows to the outside) is open for win_L1_004: win_L1_004 sits in the wall between r_L1_soyunma_odasi (dressing) and r_L1_dus (bathroom)
  - process:P3 W2:win_L1_005: the architect's question W2 (windows to the outside) is open for win_L1_005: win_L1_005 sits in the wall between r_L1_soyunma_odasi (dressing) and r_L1_dus (bathroom)
  - process:P3 W2:win_L1_008: the architect's question W2 (windows to the outside) is open for win_L1_008: win_L1_008 sits in the wall between r_L1_oda_2 (living) and r_L1_hol (hall)
- **process** (4 open, 1 with a fix; arises: scheduler; guards: process (P*))
  - process:P4 test_passes_exist_and_depth_is_plausible[real06]: test tests.gpu.test_render::test_passes_exist_and_depth_is_plausible[real06] failure: AssertionError: real06: views with missing files or an implausible depth pass: [('cam_r_L0_salon_2', 'depth not 0.
  - process:P4 test_index_pass_contains_every_visible_proxy[real06]: test tests.gpu.test_render::test_index_pass_contains_every_visible_proxy[real06] failure: AssertionError: real06: proxies planned in the frustum but absent from the index pass: [('cam_r_L0_banyo_3', [
- **untyped** (1 open, 1 with a fix; arises: reading; guards: conservation C4, ledger, the reading's AI questions)
- **silent** (1 open, 0 with a fix; arises: any stage; guards: process P2 (warnings that say something was left out))
  - process:P2 inferred trees: a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 20, sightline 36, window 67, front 27; most by window; the first pass placed 0, th

## Warnings by rule

Every warning of the reading, the build and the site, matched to a rule (``process.WARN_RULES``); 'other' = no rule yet.

assumed 45, read_by 21, drawn_mismatch 17, not_built 15, disagree 14, other 8, not_checked 4, no_model 3, outside_not_room 2, more_labels 2, no_label 2, not_used 2, nothing_fits 2, not_cut 2, not_read 1, not_allowed 1, shortfall 1, parametric 1, not_rested 1

Records Argus could not read: model_review.
