# Argus: the audit of real06

Argus checks everything a run makes, not only the looks: what the documents hold against the model (nothing lost between stages, every label and symbol used), the run itself (stages, warnings nobody acted on, tests, time), the model's sense, the inspector's and the judge's findings. Every finding has a kind (where such problems arise and the guards that catch them), an owner (the stage that caused it) and, where the run can carry it out, a fix.

Score **15.5** / 100 (100 = nothing open; 10 points per critical, 3 per major, 0.5 per minor). Open: 14 critical, 42 major, 15 minor; 23 notes.

## Lines

| line | findings | checked | note |
|---|---|---|---|
| conservation | 25 | {"reading": 238, "fit": 238, "layout": 244, "decor": 244, "agent": 244, "final": 244, "build": 243} |  |
| process | 29 | {"stages": 27, "warnings": 147, "test_reports": 1, "missing_records": []} |  |
| model | 0 | {"M1": 14, "M2": 8, "M6": 54, "M7": 8, "M3": 0, "M4": 4, "M5": 7, "M8": 4} |  |
| inspector | 68 | {"round": 4, "seen": 2, "visitor": 0, "fixed": 0, "handed": 0, "open": 68, "dropped": 2, "architect_open": 1, "architect_open_major": 0, "model_checks": {"M1":  |  |
| judge | 0 | {} | no rubric_per_view.json (the big loop did not measure) |
| sense | 0 | {"rooms": 12, "joins": 13, "reached": 12} |  |

## Problem kinds

| kind | critical | major | minor | with a fix | owners | arises | guards |
|---|---|---|---|---|---|---|---|
| geometry | 7 | 24 | 2 | 0 | scene, build, collision, orientation, clearance, drawn_layout | layout, agent | code critic (F*, G*), architect F-rules |
| no_sense | 6 | 1 | 0 | 1 | scene, facade | architect, build | sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*) |
| lost | 1 | 4 | 1 | 3 | agent, site, build, building, cameras | any stage boundary: reading -> building, fit, layout, build, render | ledger (A*), conservation (C*), plan_vs_model (B*), process (P*) |
| misread | 0 | 7 | 2 | 0 | building, scene, missing_member, fixture_clearance | reading | plan_vs_model (B*), the room-sense rules (G*, R*), model review M7 |
| process | 0 | 2 | 1 | 1 | building, tests, scheduler | scheduler | process (P*) |
| taste | 0 | 1 | 9 | 4 | building, scene, fit, drawn_layout | fit, decor, opening models | judge (J*), visitor checks Q5, Q7, the fit's matched sets |
| untyped | 0 | 1 | 0 | 1 | reading | reading | conservation C4, ledger, the reading's AI questions |
| silent | 0 | 1 | 0 | 0 | scene | any stage | process P2 (warnings that say something was left out) |
| other | 0 | 1 | 0 | 0 | untyped | - |  |

## geometry: pieces through walls or each other, blocked doors and windows, no walkway

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L0_001 | no 0.60 m walkway from door d_L0_001 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_005 | inspector:G11 | clearance |  |
| critical | d_L0_004 | no 0.60 m walkway from door d_L0_004 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | d_L1_006 | no 0.60 m walkway from door d_L1_006 to door d_L1_009 | inspector:G11 | clearance |  |
| critical | f_L0_032 | kitchen_counter blocks door o_L0_001 | inspector:F7, inspector:F9, inspector:G11 | drawn_layout |  |
| critical | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_006 | inspector:G11 | clearance |  |
| critical | o_L1_002 | no 0.60 m walkway from door o_L1_002 to door d_L1_009 | inspector:G11 | clearance |  |
| major | L0:S2 | scene check S2 on L0: 1 of 23 failed | process:P5 | build |  |
| major | f_L0_002 | kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m | inspector:G8, inspector:G11 | fixture_clearance |  |
| major | f_L0_007 | armchair f_L0_007 is 123° off the ottoman f_L0_030 (needs ≤ 30°) at 3.61 m (needs ≤ 2.50 m) | inspector:G3, inspector:G11 | orientation |  |
| major | f_L0_008 | armchair f_L0_008: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_016 | armchair f_L0_016: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_017 | armchair f_L0_017 is 87° off the ottoman f_L0_028 (needs ≤ 30°) at 5.05 m (needs ≤ 2.50 m) | inspector:G3, inspector:G11 | orientation |  |
| major | f_L0_018 | armchair f_L0_018 is 114° off the sofa_corner f_L0_011 (needs ≤ 30°) at 3.33 m (needs ≤ 2.50 m) | inspector:G3, inspector:G11 | orientation |  |
| major | f_L0_019 | armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_020 | sink_kitchen: its back is not on a wall (0.08 m off) | inspector:F3, inspector:G8, inspector:G11 | drawn_layout |  |
| major | f_L0_026 | washbasin: its back is not on a wall (0.07 m off) | inspector:F3 | off_wall |  |
| major | f_L0_027 | ottoman f_L0_027 overlaps sofa_corner f_L0_011 by 0.25 m² | inspector:F9, inspector:G2 | collision |  |
| major | f_L0_028 | ottoman f_L0_028 overlaps sofa_corner f_L0_011 by 0.25 m² | inspector:F9 | collision |  |
| major | f_L0_029 | ottoman f_L0_029 overlaps sofa_corner f_L0_011 by 0.25 m² | inspector:F9 | collision |  |
| major | f_L0_030 | ottoman f_L0_030 overlaps sofa_corner f_L0_011 by 0.25 m² | inspector:F9 | collision |  |
| major | f_L0_031 | kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m² | inspector:F9, inspector:G11 | collision |  |
| major | f_L1_006 | bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m | inspector:G5, inspector:G11 | clearance |  |
| major | f_L1_007 | desk: its back is not on a wall (0.06 m off) | inspector:F3, inspector:F9 | drawn_layout |  |
| major | f_L1_009 | bed_double f_L1_009: 0.10 m free along the left side, needs ≥ 0.60 m | inspector:G5, inspector:G11 | clearance |  |
| major | f_L1_010 | nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m² | inspector:F9, inspector:G4 | collision |  |
| major | f_L1_013 | sofa: the free zone in front of it is blocked by f_L1_027 | inspector:F6 | clearance |  |
| major | f_L1_018 | armchair: the free zone in front of it is blocked by f_L1_022 | inspector:F6 | clearance |  |
| major | f_L1_020 | shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05) | inspector:G12 | blocked_opening |  |
| major | f_L1_025 | washbasin: its back is not on a wall (0.07 m off) | inspector:F3 | off_wall |  |
| major | f_L1_027 | floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05) | inspector:G12 | blocked_opening |  |
| minor | dec_L0_009 | decor that could not rest on its host: decor cushion dec_L0_009 on f_L0_008: not rested (67% of the footprint over the support < 80%); not built | process:P2, process:P5 | scene |  |
| minor | dec_L1_017 | decor that could not rest on its host: decor plant_small dec_L1_017 on f_L1_030: not rested (no top found on the built host (attempt 2)); not built | process:P2, process:P5 | scene |  |

## lost: something the documents or an earlier stage hold is missing from the model (a labelled veranda, drawn site symbols, a room, an opening, a piece)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | sa_L0_veranda | the documents label a site area 'VERANDA' and the model does not build it (open balcony outside the outer walls (no walls drawn around it)) | conservation:C5 | site | build_outdoor_space |
| major | BALKON | a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'BALKON' at (9138484.48, 5090593.07) m lies outside the outer walls: an open balcony, recorded in site, not a room | process:P2 | building | build_outdoor_space |
| major | VERANDA | a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'VERANDA' at (9138464.73, 5090593.37) m lies outside the outer walls: an open balcony, recorded in site, not a room | process:P2 | building | build_outdoor_space |
| major | f_L0_012 | f_L0_012 (potted_plant) was to be built after the decor stage and is not built after the agent stage, with no reason | conservation:C2 | agent |  |
| major | site | items the reading found and no stage used: site: 2 cases, e.g. site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0) | process:P2 | building |  |
| minor | entity types not read | source entities the reading did not read (the ledger checks what they hold): real06.dwg: entity types not read: ATTDEF x28 | process:P2 | building |  |
| info | 2 elements | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 1: The drawn 2.27 x 0.85 m flight sits in a 2.45 m wide room with no headroom, and retype to stair fails inside_room/doors_free/windows_free: it is a drawing symbol of the adjacent stair, not furniture of this room. (f_L1_014, f_L1_015) | conservation:C6 | build |  |
| info | 2 elements | not built: the model of f_L1_009 has its own cushions/pillows (dec_L1_009, dec_L1_010) | conservation:C6 | build |  |
| info | 42 elements | not built: site decor of kind 'other' is not built (no model) (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006, sd_L0_007, sd_L0_008 ...) | conservation:C6 | build |  |
| info | dec_L1_012 | not built: its host f_L1_010 is not built (dec_L1_012) | conservation:C6 | build |  |
| info | f_L0_002 | not built: architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once (f_L0_002) | conservation:C6 | build |  |
| info | f_L0_003 | not built: drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) (f_L0_003) | conservation:C6 | build |  |
| info | f_L0_004 | not built: the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png (f_L0_004) | conservation:C6 | build |  |
| info | f_L0_005 | not built: outline 3.89 x 1.65 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_005) | conservation:C6 | build |  |
| info | f_L0_006 | not built: outline 2.12 x 0.78 m around 1 other piece(s) (f_L0_009): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_006) | conservation:C6 | build |  |
| info | f_L0_009 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 3: Tiny 0.21x0.20 m drawn symbol identical to the door-strip mark already recorded as not furniture; retype to potted_plant was rejected (F8 stands alone). (f_L0_009) | conservation:C6 | build |  |
| info | f_L0_010 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 1: The 2.54 x 1.01 m drawn outline is the dashed dimension/outline band around the drawn washbasin and bathtub fixtures, not a separate furniture piece. (f_L0_010) | conservation:C6 | build |  |
| info | f_L0_012 | not built: potted_plant: named by an AI pass and the only named type that fits the size (0.21 x 0.20 m), the living + other room and the position (others fitting: floor_lamp); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 2: Tiny 0.21x0.20 m drawn symbol blocks door d_L0_001 (F7 critical); move_piece is exhausted (3 tries), so mark it as a non-furniture reading to clear the open | conservation:C6 | build |  |
| info | f_L0_014 | not built: outline 1.52 x 0.78 m around 2 other piece(s) (f_L0_012, f_L0_013): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_014) | conservation:C6 | build |  |
| info | f_L1_001 | not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001) | conservation:C6 | build |  |
| info | f_L1_002 | not built: cluster larger than 4.5 m on a side: a group of drawn pieces, not built (f_L1_002) | conservation:C6 | build |  |
| info | f_L1_003 | not built: 2.25 x 0.18 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_003) | conservation:C6 | build |  |
| info | f_L1_004 | not built: 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_004) | conservation:C6 | build |  |
| info | f_L1_008 | not built: drawn inside bed_double f_L1_006 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) (f_L1_008) | conservation:C6 | build |  |
| info | f_L1_010 | not built: architect F5: it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built (f_L1_010) | conservation:C6 | build |  |
| info | f_L1_011 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 1: The 2.42 x 0.98 m drawn outline is the dashed dimension/outline band around the drawn washbasin and bathtub fixtures, not a separate furniture piece. (f_L1_011) | conservation:C6 | build |  |
| info | f_L1_019 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 2: The recognition crop shows a simple rectangular outline with dashed border near a wall junction, consistent with a dimension or outline mark rather than a furniture piece; all retype attempts fail with inside_room confirming it is not a valid furniture placemen | conservation:C6 | build |  |
| info | r_L0_oda | room Oda (2.1 m2) has no view: no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2) | process:P6 | cameras |  |
| info | sa_L0_veranda | not built: exterior label: its surface is built from site.paving / parking / grass (sa_L0_veranda) | conservation:C6 | build |  |

## misread: the reading typed, sized or placed something wrong (armchairs read as tables with chairs, a vanity read as a kitchen counter)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | derived ridge # m vs the drawn ridge height # m (# cm) | the model differs from the drawn section or elevation: derived ridge 8.530 m vs the drawn ridge height 7.770 m (+76 cm): the pitches are kept | process:P2 | scene |  |
| major | f_L0_026 | washbasin f_L0_026: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_021 | washbasin f_L1_021: 0.11 m clear in front, needs ≥ 0.53 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_024 | toilet f_L1_024: centre 0.33 m from the side wall or fixture on its right, needs ≥ 0.38 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_025 | washbasin f_L1_025: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m | inspector:G10 | fixture_clearance |  |
| major | r_L0_mutfak | kitchen r_L0_mutfak has no fridge (fridge) | inspector:G9 | missing_member |  |
| major | roof vs the drawn section at s # m | the model differs from the drawn section or elevation: roof vs the drawn section at s # m: 11 cases, e.g. roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm) | process:P2 | scene |  |
| minor | room '...' has more labels | one room outline holds the labels of two rooms (a wall not read?): room '...' has more labels: 2 cases, e.g. L0: room 'Salon' has more labels: YEMEK BÖLÜMÜ; the label with the largest printed area (else the first) kept | process:P2 | building |  |
| minor | sym_L1_008 | a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified | process:P2 | building |  |

## no_sense: the model makes no sense to a visitor (a door into the air, a basin at knee height, stairs running into each other, a railing across a door)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L1_001 | door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_004 | door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_005 | door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_007 | door d_L1_007 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_010 | door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_011 | door d_L1_011 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| major | o_L0_001 | an opening of the documents is not cut through its wall: o_L0_001: door ray hits splashback_r_L0_mutfak (splashback); the opening is not cut through its wall | process:P2, process:P5 | scene | clear_opening |

## other: not classified yet: a new kind to name

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | f_L1_002 | untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | inspector:NR | untyped |  |

## process: the run itself: a stage failed or was skipped, a test failed, time was left unused, a question stayed unanswered

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | run | the run ended 35 min before its deadline with 68 open major point(s): the time could have gone to more fix cycles | process:P8 | scheduler | more_cycles |
| major | test_sky_and_window_pulls_reach_their_targets[real06] | test tests.gpu.test_render::test_sky_and_window_pulls_reach_their_targets[real06] failure: AssertionError: real06: [('window panes', 'median pane saturation 0.0612 under 0.065: grey cards, not the sky', [('cam_r_L0_banyo_1', 0.0612), ('cam_r_L0_banyo_3', 0.0972), ('cam_r_L0_mutfak_1', 0.0673), ('cam_r_L0_mutfak_3', 0.0631), ('cam_r_L0_salon_1', 0.0288), ('cam_r_L0_salon_2', 0.0585), ('cam_r_L0_sal | process:P4 | tests |  |
| minor | elevation r# (all) | a check that could not run: elevation r# (all): 4 cases, e.g. elevation r1 (all): its openings are not checked against the plans (the side needs the north arrow) | process:P2 | building |  |

## silent: a stage noted a problem in a warning and nothing acted on it

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | inferred trees | a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 67, front 27; most by window; the first pass placed 0, the second pass with the window band narrowed to 4 m added 0) | process:P2 | scene |  |

## taste: the house does not look designed (pieces that do not match, plain or dated rooms, a garage door look)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | f_L0_031 | kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece) | inspector:S2 | drawn_layout |  |
| minor | f_L0_020 | sink_kitchen f_L0_020 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_033 | wall_cabinet f_L0_033 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_034 | wall_cabinet f_L0_034 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_035 | wall_cabinet f_L0_035 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | o_L0_002 | no library model: built parametric or not at all: opening o_L0_002: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |
| minor | r_L1_ebeveyn_y_odasi | a group the room should have found no place: r_L1_ebeveyn_y_odasi: completion added nothing, nothing fits: storage: no candidate position fits the room; work: no place passes the checks | process:P2 | building |  |
| minor | r_L1_hol | a group the room should have found no place: r_L1_hol: completion added nothing, nothing fits: entrance: no place passes the checks | process:P2 | building |  |
| minor | win_L0_006 | no library model: built parametric or not at all: opening win_L0_006: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |
| minor | win_L1_001 | no library model: built parametric or not at all: opening win_L1_001: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 0.95 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |

## untyped: a drawn element no rule or model typed, so nothing builds it ('other', 'unknown')

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | 42 site_symbols | 42 drawn site symbols (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006 ...) that no rule or model typed ('other'): nothing builds them and nothing explains them | conservation:C4 | reading | type_site_symbols |

## Prevention: the kinds to guard

Each open kind with the findings no fix of the run covers, or that came back from an earlier run: these need a new rule or check (a general one, for every project), not a one-off patch.

- **geometry** (33 open, 0 with a fix; arises: layout, agent; guards: code critic (F*, G*), architect F-rules)
  - RECURRING process:P5 L0:S2: scene check S2 on L0: 1 of 23 failed
  - inspector:F9 f_L0_027: ottoman f_L0_027 overlaps sofa_corner f_L0_011 by 0.25 m²
  - inspector:F9 f_L0_028: ottoman f_L0_028 overlaps sofa_corner f_L0_011 by 0.25 m²
  - inspector:F9 f_L0_029: ottoman f_L0_029 overlaps sofa_corner f_L0_011 by 0.25 m²
  - inspector:F9 f_L0_030: ottoman f_L0_030 overlaps sofa_corner f_L0_011 by 0.25 m²
  - inspector:G3 f_L0_007: armchair f_L0_007 is 123° off the ottoman f_L0_030 (needs ≤ 30°) at 3.61 m (needs ≤ 2.50 m)
  - inspector:G3 f_L0_017: armchair f_L0_017 is 87° off the ottoman f_L0_028 (needs ≤ 30°) at 5.05 m (needs ≤ 2.50 m)
  - inspector:G3 f_L0_018: armchair f_L0_018 is 114° off the sofa_corner f_L0_011 (needs ≤ 30°) at 3.33 m (needs ≤ 2.50 m)
  - RECURRING inspector:G11 d_L0_001: no 0.60 m walkway from door d_L0_001 to door d_L0_006
  - RECURRING inspector:G11 d_L0_004: no 0.60 m walkway from door d_L0_004 to door d_L0_006
  - inspector:G11 f_L0_008: armchair f_L0_008: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - inspector:G11 f_L0_016: armchair f_L0_016: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - inspector:G11 f_L0_019: armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - RECURRING inspector:G11 o_L0_001: no 0.60 m walkway from door o_L0_001 to door d_L0_006
  - inspector:F3 f_L0_020: sink_kitchen: its back is not on a wall (0.08 m off)
  - inspector:F7 f_L0_032: kitchen_counter blocks door o_L0_001
  - inspector:F9 f_L0_031: kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m²
  - RECURRING inspector:G8 f_L0_002: kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m
  - RECURRING inspector:G11 d_L0_003: no 0.60 m walkway from door d_L0_003 to door d_L0_005
  - inspector:F3 f_L0_026: washbasin: its back is not on a wall (0.07 m off)
  - inspector:F6 f_L1_018: armchair: the free zone in front of it is blocked by f_L1_022
  - inspector:F3 f_L1_007: desk: its back is not on a wall (0.06 m off)
  - RECURRING inspector:F9 f_L1_010: nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m²
  - RECURRING inspector:G5 f_L1_006: bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m
  - inspector:G5 f_L1_009: bed_double f_L1_009: 0.10 m free along the left side, needs ≥ 0.60 m
  - RECURRING inspector:G11 d_L1_006: no 0.60 m walkway from door d_L1_006 to door d_L1_009
  - RECURRING inspector:G11 o_L1_002: no 0.60 m walkway from door o_L1_002 to door d_L1_009
  - inspector:G12 f_L1_020: shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05)
  - inspector:F6 f_L1_013: sofa: the free zone in front of it is blocked by f_L1_027
  - inspector:G12 f_L1_027: floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05)
  - inspector:F3 f_L1_025: washbasin: its back is not on a wall (0.07 m off)
- **no_sense** (7 open, 1 with a fix; arises: architect, build; guards: sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*))
  - RECURRING process:P2 o_L0_001: an opening of the documents is not cut through its wall: o_L0_001: door ray hits splashback_r_L0_mutfak (splashback); the opening is not cut through its wall
  - inspector:X3 d_L1_001: door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:X3 d_L1_004: door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:X3 d_L1_005: door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:X3 d_L1_007: door d_L1_007 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:X3 d_L1_010: door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:X3 d_L1_011: door d_L1_011 is 3.50 m above the ground with nothing to reach it (a door into the air)
- **lost** (6 open, 3 with a fix; arises: any stage boundary: reading -> building, fit, layout, build, render; guards: ledger (A*), conservation (C*), plan_vs_model (B*), process (P*))
  - conservation:C2 f_L0_012: f_L0_012 (potted_plant) was to be built after the decor stage and is not built after the agent stage, with no reason
  - RECURRING conservation:C5 sa_L0_veranda: the documents label a site area 'VERANDA' and the model does not build it (open balcony outside the outer walls (no walls drawn around it))
  - RECURRING process:P2 VERANDA: a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'VERANDA' at (9138464.73, 5090593.37) m lies outside the outer walls: an open balcony, recorded in s
  - RECURRING process:P2 BALKON: a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'BALKON' at (9138484.48, 5090593.07) m lies outside the outer walls: an open balcony, recorded in si
  - RECURRING process:P2 site: items the reading found and no stage used: site: 2 cases, e.g. site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0)
- **misread** (9 open, 0 with a fix; arises: reading; guards: plan_vs_model (B*), the room-sense rules (G*, R*), model review M7)
  - RECURRING process:P2 roof vs the drawn section at s # m: the model differs from the drawn section or elevation: roof vs the drawn section at s # m: 11 cases, e.g. roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm)
  - RECURRING process:P2 derived ridge # m vs the drawn ridge height # m (# cm): the model differs from the drawn section or elevation: derived ridge 8.530 m vs the drawn ridge height 7.770 m (+76 cm): the pitches are kept
  - RECURRING inspector:G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge)
  - inspector:G10 f_L0_026: washbasin f_L0_026: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m
  - inspector:G10 f_L1_021: washbasin f_L1_021: 0.11 m clear in front, needs ≥ 0.53 m
  - inspector:G10 f_L1_024: toilet f_L1_024: centre 0.33 m from the side wall or fixture on its right, needs ≥ 0.38 m
  - inspector:G10 f_L1_025: washbasin f_L1_025: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m
- **process** (3 open, 1 with a fix; arises: scheduler; guards: process (P*))
  - process:P4 test_sky_and_window_pulls_reach_their_targets[real06]: test tests.gpu.test_render::test_sky_and_window_pulls_reach_their_targets[real06] failure: AssertionError: real06: [('window panes', 'median pane saturation 0.0612 under 0.065: grey cards, not the sky
  - RECURRING process:P8 run: the run ended 35 min before its deadline with 68 open major point(s): the time could have gone to more fix cycles
- **untyped** (1 open, 1 with a fix; arises: reading; guards: conservation C4, ledger, the reading's AI questions)
  - RECURRING conservation:C4 42 site_symbols: 42 drawn site symbols (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006 ...) that no rule or model typed ('other'): nothing builds them and nothing explains them
- **taste** (10 open, 4 with a fix; arises: fit, decor, opening models; guards: judge (J*), visitor checks Q5, Q7, the fit's matched sets)
  - inspector:S2 f_L0_031: kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece)
- **silent** (1 open, 0 with a fix; arises: any stage; guards: process P2 (warnings that say something was left out))
  - RECURRING process:P2 inferred trees: a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 67, front 27; most by window; the first pass placed 0, th
- **other** (1 open, 0 with a fix; arises: -; guards: none)
  - RECURRING inspector:NR f_L1_002: untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built

## Warnings by rule

Every warning of the reading, the build and the site, matched to a rule (``process.WARN_RULES``); 'other' = no rule yet.

assumed 50, read_by 24, drawn_mismatch 17, not_built 16, disagree 13, other 4, not_checked 4, no_model 3, outside_not_room 2, more_labels 2, no_label 2, not_used 2, nothing_fits 2, not_rested 2, not_read 1, not_allowed 1, shortfall 1, not_cut 1
