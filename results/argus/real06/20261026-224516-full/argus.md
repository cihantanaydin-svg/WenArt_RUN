# Argus: the audit of real06

Argus checks everything a run makes, not only the looks: what the documents hold against the model (nothing lost between stages, every label and symbol used), the run itself (stages, warnings nobody acted on, tests, time), the model's sense, the inspector's and the judge's findings. Every finding has a kind (where such problems arise and the guards that catch them), an owner (the stage that caused it) and, where the run can carry it out, a fix.

Score **4.9** / 100 (100 = nothing open; 10 points per critical, 3 per major, 0.5 per minor). Open: 36 critical, 190 major, 63 minor; 29 notes. Argus's own edits this run: 0 of 94 accepted by code (add_camera 0/1, complete_group 0/1, correct_geometry 0/1, fix_fixture 0/5, mark_not_furniture 0/1, place_group 0/3, relayout_room 0/1, retype_piece 0/4, set_camera 0/52, set_entrance 0/1, set_exterior 0/6, set_material 0/3, set_room_type 0/1, swap_model 0/14).

## Lines

| line | findings | checked | note |
|---|---|---|---|
| conservation | 33 | {"reading": 243, "fit": 243, "layout": 256, "decor": 256, "agent": 256, "final": 256, "build": 255} |  |
| process | 40 | {"stages": 27, "warnings": 152, "test_reports": 1, "missing_records": []} |  |
| model | 0 | {"M1": 15, "M2": 8, "M6": 52, "M7": 8, "M3": 0, "M4": 6, "M5": 7, "M8": 4} |  |
| inspector | 348 | {"round": 4, "seen": 342, "visitor": 106, "fixed": 0, "handed": 30, "open": 318, "dropped": 63, "architect_open": 6, "architect_open_major": 4, "model_checks":  |  |
| judge | 155 | {"views": 28, "mean": 2.07} |  |
| sense | 0 | {"rooms": 12, "joins": 14, "reached": 12} |  |
| render_check | 11 | {"views": 28, "required_elements": 63, "drawn_pieces": 57, "elevations": 4} |  |
| consistency | 8 | {"critic_findings": 46} |  |
| ledger | 8 | {"by_kind": {"element:furniture": {"items": 57, "must": 57, "accounted": 57, "unaccounted": 0}, "element:openings": {"items": 36, "must": 36, "accounted": 36, " |  |
| plan_vs_model | 7 | {"levels": 2, "elevation_calls": 6, "plans": {"L0": "strokes", "L1": "strokes"}} |  |
| argus_ai | 40 | {} |  |

## Problem kinds

| kind | critical | major | minor | with a fix | owners | arises | guards |
|---|---|---|---|---|---|---|---|
| taste | 8 | 77 | 10 | 3 | building, scene, fit, drawn_layout, built_front, wrong_model | fit, decor, opening models | judge (J*), visitor checks Q5, Q7, the fit's matched sets |
| misread | 10 | 12 | 14 | 0 | building, fixture_clearance, wrong_type, interior_camera, empty_room, fit | reading | plan_vs_model (B*), the room-sense rules (G*, R*), model review M7 |
| geometry | 8 | 29 | 5 | 0 | scene, build, clearance, drawn_layout, collision, off_wall | layout, agent | code critic (F*, G*), architect F-rules |
| no_sense | 5 | 25 | 6 | 16 | architect, build, facade, guard, opening_sense, rain_water | architect, build | sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*) |
| stale | 3 | 5 | 0 | 8 | architect | agent loop, critics | the critics read the building as built, conservation C2, consistency (Y*: the critic and the architect's rule disagree about one element) |
| other | 2 | 6 | 4 | 5 | untyped, lighting_beyond_cap, room_type, reading, fit | - |  |
| lost | 0 | 19 | 19 | 23 | agent, build, building, cameras, wrong_type, exterior_camera | any stage boundary: reading -> building, fit, layout, build, render | ledger (A*), conservation (C*), plan_vs_model (B*), process (P*) |
| silent | 0 | 10 | 2 | 12 | agent | any stage | process P2 (warnings that say something was left out) |
| process | 0 | 7 | 3 | 3 | building, scene, tests, scheduler, agent, wrong_type | scheduler | process (P*) |

## geometry: pieces through walls or each other, blocked doors and windows, no walkway

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_005 | inspector:G11 | clearance |  |
| critical | d_L1_003 | no 0.60 m walkway from door d_L1_003 to door win_L1_003 | inspector:G11 | clearance |  |
| critical | d_L1_006 | no 0.60 m walkway from door d_L1_006 to door d_L1_009 | inspector:G11 | clearance |  |
| critical | f_L1_009 | bed_double blocks door d_L1_011 | inspector:F7, inspector:G5, inspector:G11 | blocked_opening |  |
| critical | f_L1_012 | bed_double: the headboard stands in the room (0.06 m off) | inspector:F3 | off_wall |  |
| critical | f_L1_014 | wardrobe blocks door win_L1_003 | inspector:F7, inspector:G11, inspector:G12 | blocked_opening |  |
| critical | f_L1_035 | The desk is rendered as a floating slab with no legs or support structure, hovering in mid-air. | inspector:F9 | floating |  |
| critical | o_L1_002 | no 0.60 m walkway from door o_L1_002 to door d_L1_009 | inspector:G11 | clearance |  |
| major | L0:S2 | scene check S2 on L0: 1 of 23 failed | process:P5 | build |  |
| major | L1:S2 | scene check S2 on L1: 2 of 24 failed | process:P5 | build |  |
| major | L1:S3 | scene check S3 on L1: 1 of 22 failed | process:P5 | build |  |
| major | d_L0_004 | the main walkway from the entrance door is below 0.80 m between doors d_L0_004 and d_L0_006 | inspector:G11 | clearance |  |
| major | d_L1_002 | the main walkway from the entrance door is below 0.80 m between doors d_L1_002 and d_L1_007 | inspector:G11 | clearance |  |
| major | d_L1_007 | the main walkway from the entrance door is below 0.80 m between doors d_L1_007 and win_L1_003 | inspector:G11 | clearance |  |
| major | f_L0_002 | kitchen_counter f_L0_002: its front use zone is not reached by a 0.60 m walkway from door d_L0_003 | inspector:G11, inspector:F9, judge:F9 | clearance |  |
| major | f_L0_010 | bathtub: its back is not on a wall (0.02 m off) | inspector:F3 | drawn_layout |  |
| major | f_L0_016 | armchair f_L0_016: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_019 | armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | inspector:G11 | clearance |  |
| major | f_L0_020 | sink_kitchen: its back is not on a wall (0.08 m off) | inspector:F3, inspector:G8, inspector:G11 | drawn_layout |  |
| major | f_L0_026 | washbasin: its back is not on a wall (0.07 m off) | inspector:F3, inspector:F9 | off_wall |  |
| major | f_L0_031 | kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m² | inspector:F9, inspector:G11 | collision |  |
| major | f_L0_032 | kitchen_counter reaches 0.06 m² through the room outline, up to 0.025 m deep | inspector:F9, inspector:G11 | drawn_layout |  |
| major | f_L1_006 | bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m | inspector:G5, inspector:G11, inspector:D1, judge:D1 | clearance |  |
| major | f_L1_007 | dresser: its back is not on a wall (0.06 m off) | inspector:F3, inspector:F9 | drawn_layout |  |
| major | f_L1_010 | nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m² | inspector:F9, inspector:G4 | collision |  |
| major | f_L1_011 | bathtub: its back is not on a wall (0.02 m off) | inspector:F3 | drawn_layout |  |
| major | f_L1_013 | sofa: the free zone in front of it is blocked by f_L1_027 | inspector:F6, inspector:D1, judge:D1 | clearance |  |
| major | f_L1_015 | wardrobe f_L1_015: its front use zone is not reached by a 0.60 m walkway from door win_L1_003 | inspector:G11, inspector:G12 | clearance |  |
| major | f_L1_018 | armchair: the free zone in front of it is blocked by f_L1_022 | inspector:F6 | clearance |  |
| major | f_L1_020 | shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05) | inspector:G12 | blocked_opening |  |
| major | f_L1_021 | washing_machine f_L1_021: its front use zone is not reached by a 0.60 m walkway from door d_L1_009 | inspector:G11 | clearance |  |
| major | f_L1_025 | washbasin: its back is not on a wall (0.07 m off) | inspector:F3, inspector:F9 | off_wall |  |
| major | f_L1_027 | floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05) | inspector:G12 | blocked_opening |  |
| major | o_L0_001 | Argus: The large opening in the wall is a raw, unframed hole with a floating horizontal bar, which looks like a broken model or a construction error rather than a designed feature. | inspector:F9 | geometry |  |
| major | r_L0_salon | Argus: The cream armchair is pushed flat against the wall under the window instead of being part of a seating arrangement; it looks staged, not designed. | inspector:Q6 | clearance |  |
| major | w_L0_001 | The entire exterior environment is a placeholder. The flat, untextured ground, the grey sky, and the crude, low-poly trees are the biggest issue. This is not a believable setting for a client presentation. | inspector:F9, judge:F9 | wrong_type |  |
| major | w_L1_001 | The surrounding site is a flat, featureless green plane with a hard horizon and a line of crude lollipop trees. This empty, artificial environment makes the house look like a model in a void rather than a believable, designed home. | inspector:F9, judge:F9 | wrong_type |  |
| minor | dec_L0_004 | decor that could not rest on its host: decor cushion dec_L0_004 on f_L0_016: not rested (penetration 0.041 m > 0.03 m); not built | process:P2, process:P5 | scene |  |
| minor | f_L0_008 | The cream armchair is pushed flat against the wall under the window instead of being part of a seating arrangement; it looks staged, not designed. | inspector:Q6, judge:Q6 | blocked_opening |  |
| minor | f_L0_033 | The sideboard is pushed into the corner with a large empty wall beside it, leaving the composition unbalanced. | inspector:Q6, judge:Q6 | orientation |  |
| minor | f_L1_029 | The washbasin is cut off at the bottom-left edge and its relationship to the wall/counter is unclear; it reads as a floating slab rather than a properly anchored basin. | inspector:F9, judge:F9 | floating |  |
| minor | w_L0_002 | The ground is a flat, untextured green plane with no grass, soil, or variation. It looks like a default 3D viewport floor. | inspector:F9, judge:F9 | wrong_type |  |

## lost: something the documents or an earlier stage hold is missing from the model (a labelled veranda, drawn site symbols, a room, an opening, a piece)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | TEXT:29ABD3 | the documents name a dresser ('*SIFONIYER') on L1; the model has f_L1_019 unknown (not built) within 1.2 m | ledger:A6 | reading | {'action': 'type_piece', 'element_id': 'f_L1_019', 'type': 'dresser', 'named_by': 'TEXT:29ABD3'} |
| major | TEXT:29AC25 | Argus: the documents name a dresser ('*SIFONIYER') on L1; the model has no piece within 1.2 m | inspector:A6, ledger:A6 | exterior_camera | {'action': 'add_piece', 'type': 'dresser', 'level_id': 'L1', 'anchor': [8.106, 4.909], 'named_by': 'TEXT:29AC25'} |
| major | d_L1_001 | Door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air). Same for d_L1_004, d_L1_005, d_L1_010. These are doors on L1 that are not connected to any stair or walkway. | argus_ai:AI1 | fit | rule_needed |
| major | f_L0_001 | The staircase (f_L0_001) is completely open with no handrails or balustrades on either side. This is a safety issue and a visual defect. | argus_ai:AI1 | fit | agent_round |
| major | f_L0_035 | f_L0_035 (stove, furniture) is planned to be built but the scene has no object for it | conservation:C3 | build |  |
| major | f_L0_039 | f_L0_039 (fridge, furniture) is planned to be built but the scene has no object for it | conservation:C3 | build |  |
| major | f_L1_001 | Argus: not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001) | inspector:C6 | fixture_place |  |
| major | f_L1_002 | Argus: not built: cluster larger than 4.5 m on a side: a group of drawn pieces, not built (f_L1_002) | inspector:C6, plan_vs_model:B8, argus_ai:AI2 | untyped | mark_not_furniture |
| major | f_L1_010 | left out for a reason that hides a loss: not built: architect F5: it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built (f_L1_010) (The nightstand is a necessary piece of furniture for a bedroom. It was not built due to a placement conflict. Moving it to a free spot next to the bed will resolve the conflict and allow it to be built.) | plan_vs_model:B8, argus_ai:AI2 | furniture | move_piece |
| major | f_L1_019 | Argus: the documents name a dresser ('*SIFONIYER') on L1; the model has f_L1_019 unknown (not built) within 1.2 m | inspector:A6, plan_vs_model:B8 | wrong_type |  |
| major | f_L1_030 | furniture f_L1_030 (shoe_cabinet) of the decor stage is missing after the agent stage and nothing there names it | conservation:C1 | agent |  |
| major | f_L1_031 | furniture f_L1_031 (desk) of the decor stage is missing after the agent stage and nothing there names it | conservation:C1, plan_vs_model:B8 | agent |  |
| major | f_L1_032 | furniture f_L1_032 (office_chair) of the decor stage is missing after the agent stage and nothing there names it | conservation:C1 | agent |  |
| major | r_L0_mutfak | The kitchen has a table_dining piece, but the salon also has a table_dining. The kitchen's dining table is redundant and the kitchen lacks a proper worktop arrangement; the judge scores the kitchen 1-2/5. The kitchen_counter is 'a row of identical blank boxes'. | argus_ai:AI1 | fit | agent_round |
| major | r_L0_mutfak:TEXT:294BCF | the documents name a space 'ANTRE m²' that is a second label of room r_L0_mutfak (Mutfak, kitchen): it is not a room of its own in the model | ledger:A3 | reading | {'action': 'split_room', 'room_id': 'r_L0_mutfak', 'label': 'ANTRE m²', 'anchor': [5.14, 10.809], 'area_m2': None} |
| major | r_L0_salon | Argus: the documents name a space 'YEMEK BÖLÜMÜ' (17.35 m²) that is a second label of room r_L0_salon (Salon, living): it is not a room of its own in the model | inspector:A3, argus_ai:AI1 | room_type | agent_round |
| major | r_L1_soyunma_odasi | The dressing room (soyunma odası) is 5.9 m2 with only a wardrobe. The judge scores the renders 1/5 with exposure problems (+9 EV wanted, capped at +3). The room is too dark and the single wardrobe does not fill the space. | argus_ai:AI1 | fit | agent_round |
| major | sa_L0_veranda | The documents label a VERANDA on L0; the model has no outline for it (not built). The image shows a large paved terrace with columns and railings at the north-west, but it is not registered as a site area, so it is not furnished, not checked, and not rendered as a defined space. | argus_ai:AI1 | site | rule_needed |
| major | sa_L1_balkon | The documents label a BALKON on L1; the model has no outline for it (not built). | argus_ai:AI1 | site | rule_needed |
| minor | 2 elements | left out for a reason that hides a loss: not built: untyped (CLAUDE.md: no untyped piece is built) (f_L0_009, f_L1_019) (f_L0_009 and f_L1_019 are untyped drawn pieces. Marking them as not furniture with their recognition crops records the decision and clears the finding.) | argus_ai:AI2 | reading | mark_not_furniture |
| minor | TEXT:294BCE | printed area '9,00 m²' of 'HOL' on L1 is not used: the area check of that space is lost | ledger:A4 | reading | {'action': 'check_area_label', 'label': 'HOL', 'text': '9,00 m²', 'anchor': [5.031, 9.884]} |
| minor | d_L0_001 | The main entrance door (d_L0_001) is barely legible: there is no clear door leaf, handle, canopy, or frame detail. It is a generic, flat white slab. | argus_ai:AI1 | fit | agent_round |
| minor | d_L0_003 | No 0.60 m walkway from door d_L0_003 to door d_L0_005. | argus_ai:AI1 | fit | agent_round |
| minor | entity types not read | source entities the reading did not read (the ledger checks what they hold): real06.dwg: entity types not read: ATTDEF x28 | process:P2 | building |  |
| minor | f_L0_002 | Kitchen counter f_L0_002: its front use zone is not reached by a 0.60 m walkway from door d_L0_001. | argus_ai:AI1 | fit | agent_round |
| minor | f_L0_012 | The tree visible through win_L0_001 is a crude low-poly 'lollipop' model with a wireframe. This is a visual defect in the render. | argus_ai:AI1 | fit | agent_round |
| minor | f_L0_015 | The bright honey-oak coffee table is a third, clashing wood tone against the pale floor. The agent tried 4 times to fix D3 on f_L0_015. | argus_ai:AI1 | fit | agent_round |
| minor | f_L0_016 | Four identical egg chairs (f_L0_016, f_L0_017, f_L0_018, f_L0_019) are the entire seating in the salon. This is monotonous and the front use zone is not reached by a 0.60 m walkway from door d_L0_001. | argus_ai:AI1 | fit | agent_round |
| minor | f_L0_019 | Armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_001. | argus_ai:AI1 | fit | agent_round |
| minor | f_L1_003 | The plan draws an unknown object (f_L1_003) in the children's room which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_004 | The plan draws an unknown object (f_L1_004) in the children's room which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | f_L1_008 | The plan draws an unknown object (f_L1_008) in the children's room which is not built in the model. | plan_vs_model:B8 | furniture |  |
| minor | r_L0_oda | The hall (oda) on L0 is 2.1 m2 with no pieces. It is a tiny corridor space, which is acceptable, but it has no door listed in the pieces. The doors d_L0_001 through d_L0_007 are on L0, but the hall's connectivity is unclear. | argus_ai:AI1 | fit | not_a_problem |
| minor | r_L0_salon:TEXT:295858 | the documents name a space 'YEMEK BÖLÜMÜ' (17.35 m²) that is a second label of room r_L0_salon (Salon, living): it is not a room of its own in the model | ledger:A3 | reading | {'action': 'split_room', 'room_id': 'r_L0_salon', 'label': 'YEMEK BÖLÜMÜ', 'anchor': [1.815, 6.334], 'area_m2': 17.35} |
| minor | site | items the reading found and no stage used: site: 42 decor read outside the walls of L1 not used (the site is the ground floor's, L0); 26 of them repeat the ground plan's symbols at the same place (site.decor_other_levels) | process:P2 | building |  |
| minor | warning:5 | the reading says: real06.dwg: walls drawn as face lines: layer 'SIVA' chosen by evidence (closes in 5 of 6 labelled rooms, 85% of its long strokes pair, widths 0.15, 0.25, 0.30, 0.35, 0.40, 0.45, 0.49, 0.50 m); runner-up 'DUVAR' (5 of 6); 6 other wall primitives off that layer left out | ledger:A7 | reading |  |
| minor | warning:6 | the reading says: real06.dwg: walls drawn as face lines: layer 'SIVA' chosen by evidence (closes in 7 of 8 labelled rooms, 84% of its long strokes pair, widths 0.15, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.54 m); runner-up 'DUVAR' (7 of 8); 64 other wall primitives off that layer left out | ledger:A7 | reading |  |
| minor | warning:7 | the reading says: site: 42 decor read outside the walls of L1 not used (the site is the ground floor's, L0); 26 of them repeat the ground plan's symbols at the same place (site.decor_other_levels) | ledger:A7 | site |  |
| info | 2 elements | not built: untyped (CLAUDE.md: no untyped piece is built) (f_L0_009, f_L1_019) | conservation:C6 | build |  |
| info | 2 elements | not built: drawn on 'AKS': a structural grid bubble (the axis label), drawing annotation; not built (sd_L0_006, sd_L0_037) | conservation:C6 | build |  |
| info | 2 elements | not built: drawn on 'KOLON': a column; built as a post of the veranda os_L0_veranda (sd_L0_009, sd_L0_010) | conservation:C6 | build |  |
| info | 2 elements | not built: drawn on 'kot': a level mark symbol; not built (sd_L0_015, sd_L0_025) | conservation:C6 | build |  |
| info | 2 elements | not built: exterior label: its surface is built from site.paving / parking / grass (sa_L0_veranda, sa_L1_balkon) | conservation:C6 | build |  |
| info | 26 elements | not built: drawn on 'AKS YAZI': a structural grid bubble (the axis label), drawing annotation; not built (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_007, sd_L0_008, sd_L0_012 ...) | conservation:C6 | build |  |
| info | 7 elements | not built: drawn on 'DENIZLIK': a window sill or coping line; not built (sd_L0_011, sd_L0_017, sd_L0_021, sd_L0_024, sd_L0_028, sd_L0_035, sd_L0_036) | conservation:C6 | build |  |
| info | dec_L0_009 | not built: the model of f_L0_007 has its own cushions/pillows (dec_L0_009) | conservation:C6 | build |  |
| info | dec_L1_012 | not built: its host f_L1_010 is not built (dec_L1_012) | conservation:C6 | build |  |
| info | f_L0_002 | not built: architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once (f_L0_002) | conservation:C6 | build |  |
| info | f_L0_003 | not built: drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) (f_L0_003) | conservation:C6 | build |  |
| info | f_L0_004 | not built: the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png (f_L0_004) | conservation:C6 | build |  |
| info | f_L0_005 | not built: outline 3.89 x 1.65 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_005) | conservation:C6 | build |  |
| info | f_L0_006 | not built: outline 2.12 x 0.78 m around 1 other piece(s) (f_L0_009): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_006) | conservation:C6 | build |  |
| info | f_L0_014 | not built: outline 1.52 x 0.78 m around 2 other piece(s) (f_L0_012, f_L0_013): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_014) | conservation:C6 | build |  |
| info | f_L0_036 | not built: the answer to AI.remove_piece:f_L0_036: not built (f_L0_036) | conservation:C6 | build |  |
| info | f_L0_037 | not built: the answer to AI.remove_piece:f_L0_037: not built (f_L0_037) | conservation:C6 | build |  |
| info | f_L0_038 | not built: the answer to AI.remove_piece:f_L0_038: not built (f_L0_038) | conservation:C6 | build |  |
| info | f_L1_001 | not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001) | conservation:C6 | build |  |
| info | f_L1_002 | not built: cluster larger than 4.5 m on a side: a group of drawn pieces, not built (f_L1_002) | conservation:C6 | build |  |
| info | f_L1_003 | not built: 2.25 x 0.18 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_003) | conservation:C6 | build |  |
| info | f_L1_004 | not built: 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_004) | conservation:C6 | build |  |
| info | f_L1_008 | not built: drawn inside bed_double f_L1_006 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) (f_L1_008) | conservation:C6 | build |  |
| info | f_L1_010 | not built: architect F5: it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built (f_L1_010) | conservation:C6 | build |  |
| info | o_L1_001 | o_L1_001 (opening) of the final stage is gone after the build stage, named in openings[38].evidence[2].text: one opening with o_L1_001 (read twice): 1.98 m wide | conservation:C1 | build |  |
| info | r_L0_oda | room Oda (2.1 m2) has no view: no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2) | process:P6 | cameras |  |
| info | sd_L0_014 | not built: drawn on 'KAPI': a door symbol; not built (sd_L0_014) | conservation:C6 | build |  |
| info | sd_L0_016 | not built: drawn on 'TARAMA': a hatch; not built (sd_L0_016) | conservation:C6 | build |  |
| info | sd_L0_018 | not built: drawn on 'BALKON': a detail of an outdoor space (its edge or steps); built with the veranda os_L0_veranda (its drawn steps or edge) (sd_L0_018) | conservation:C6 | build |  |

## misread: the reading typed, sized or placed something wrong (armchairs read as tables with chairs, a vanity read as a kitchen counter)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | f_L0_011 | A 55.6 m2 salon has no sofa or coffee table in frame; the room is anchored by a dining set, so the main living group is missing. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L0_015 | The salon has no sofa and no dining set; the only seating is four identical egg armchairs around a small coffee table. A 55 m2 living room with no anchor piece makes no sense. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L0_035 | The kitchen is missing its main functional pieces. The stove (f_L0_035), fridge (f_L0_039), and wall cabinets (f_L0_040, f_L0_041) are listed in the JSON but are not visible in the render. The room looks like an empty shell with one counter. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | r_L0_banyo | Argus: The washbasin is a main piece of the bathroom but is completely missing from the frame. A bathroom render that shows only a toilet and a door makes no sense to a client. | inspector:Q4 | interior_camera |  |
| critical | r_L0_mutfak | Argus: The kitchen is missing its main functional anchor: there is no hob or cooktop on the worktop, making the room feel incomplete and non-functional. | inspector:Q4 | interior_camera |  |
| critical | r_L0_salon | Argus: The salon has no sofa and no dining set; the only seating is four identical egg armchairs around a small coffee table. A 55 m2 living room with no anchor piece makes no sense. | inspector:Q4 | interior_camera |  |
| critical | r_L1_banyo | Argus: The toilet (f_L1_024) is missing from the render. A bathroom without a toilet is a fundamental, client-visible failure. | inspector:Q4 | interior_camera |  |
| critical | r_L1_dus | Argus: The shower is missing entirely; a bathroom with no shower/wet zone makes no sense. | inspector:Q4 | interior_camera |  |
| critical | r_L1_ebeveyn_y_odasi | Argus: The scheduled armchair (and its pair f_L1_018) is absent; the bedroom has no seating or reading corner, so the main group is just a bed and the room feels incomplete. | inspector:Q4 | interior_camera |  |
| critical | r_L1_soyunma_odasi | Argus: The dressing room (soyunma odasi) is completely empty. It has no wardrobe, bench, mirror, or any of the fixtures a dressing room requires. This is a missing-anchor failure: the room's entire purpose is absent. | inspector:Q4 | interior_camera |  |
| major | f_L0_010 | bathtub f_L0_010: 0.40 m clear in front, needs ≥ 0.53 m | inspector:G10 | fixture_clearance |  |
| major | f_L0_026 | washbasin f_L0_026: 0.09 m clear in front, needs ≥ 0.53 m | inspector:G10 | fixture_clearance |  |
| major | f_L0_036 | The room is 24.8 m2, which is large for a kitchen. The dining table (f_L0_036) and chairs (f_L0_037, f_L0_038) are listed in the JSON but are completely missing from the render, leaving a large, empty area that makes the room feel incomplete. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L0_039 | The refrigerator (f_L0_039) is listed in the JSON but is not visible in the render. A kitchen without a visible fridge is a major omission for a client presentation. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L0_040 | No wall cabinets are visible above the counter run. The upper wall is bare, leaving the kitchen looking empty and unbalanced. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L1_011 | bathtub f_L1_011: 0.33 m clear in front, needs ≥ 0.53 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_024 | toilet f_L1_024: centre 0.33 m from the side wall or fixture on its right, needs ≥ 0.38 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_025 | washbasin f_L1_025: 0.26 m clear in front, needs ≥ 0.53 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_027 | Argus: The room is missing its main anchor piece, the floor lamp (f_L1_027). A living room with only two mismatched sofas and no lighting or decor looks like an empty, unfinished space. | inspector:Q4 | wrong_type |  |
| major | f_L1_037 | The room appears empty. The only piece of furniture, the shoe cabinet, is mostly out of frame, leaving the visible area as a bare corner with no functional or decorative elements. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | r_L1_hol | Argus: The hall is completely empty and unfinished. There is no lighting, no skirting boards, no floor finish, and no decor. It looks like a grey-box construction site, not a livable space. | inspector:Q4 | interior_camera |  |
| major | r_L1_oda | Argus: The room is essentially empty. A 3.1 m2 hall should have some sense of purpose or at least be styled, but this is just a bare box with a door. | inspector:Q4 | empty_room |  |
| minor | f_L0_012 | potted_plant f_L0_012 differs from the drawing (tolerance 0.05 m): 0.29 m from its drawn place | render:K3 | layout |  |
| minor | f_L0_013 | potted_plant f_L0_013 differs from the drawing (tolerance 0.05 m): 0.29 m from its drawn place | render:K3 | layout |  |
| minor | f_L0_020 | sink_kitchen f_L0_020 differs from the drawing (tolerance 0.05 m): 0.44 m from its drawn place | render:K3 | layout |  |
| minor | f_L0_029 | chair f_L0_029 differs from the drawing (tolerance 0.05 m): 0.07 m from its drawn place | render:K3 | layout |  |
| minor | f_L0_030 | chair f_L0_030 differs from the drawing (tolerance 0.05 m): 0.08 m from its drawn place | render:K3 | layout |  |
| minor | f_L0_033 | The bookshelf (f_L0_033) and all potted plants (f_L0_012, f_L0_013, f_L0_034) are listed for this room but none are visible in the frame. The room feels empty and unfinished. | inspector:Q4, judge:Q4 | wrong_type |  |
| minor | f_L1_006 | bed_double f_L1_006 looks like something else in 1 view(s): cam_r_L1_cocuk_odasi_3 (seen as bed_single) | render:K2 | fit |  |
| minor | f_L1_007 | dresser f_L1_007 differs from the drawing (tolerance 0.05 m): 0.15 m from its drawn place | render:K3 | layout |  |
| minor | f_L1_016 | sofa f_L1_016 differs from the drawing (tolerance 0.05 m): 0.06 m from its drawn place | render:K3 | layout |  |
| minor | f_L1_021 | The washing machine (f_L1_021) listed for this room is not visible in the render. It is either missing or hidden, which is a discrepancy with the project spec. | inspector:Q4, judge:Q4 | wrong_type |  |
| minor | f_L1_022 | floor_lamp f_L1_022 differs from the drawing (tolerance 0.05 m): 0.30 m from its drawn place | render:K3 | layout |  |
| minor | f_L1_035 | The desk (f_L1_035) and office chair (f_L1_036) listed for this room are not visible in the render. A 23 m2 bedroom with a work zone should show it; its absence makes the room feel incomplete. | inspector:Q4, judge:Q4 | wrong_type |  |
| minor | room '...' has more labels | one room outline holds the labels of two rooms (a wall not read?): room '...' has more labels: 2 cases, e.g. L0: room 'Salon' has more labels: YEMEK BÖLÜMÜ; the label with the largest printed area (else the first) kept | process:P2 | building |  |
| minor | sym_L1_008 | a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified | process:P2 | building |  |

## no_sense: the model makes no sense to a visitor (a door into the air, a basin at knee height, stairs running into each other, a railing across a door)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L1_001 | door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2, inspector:Q3, inspector:Q1, judge:Q1, argus_ai:AI1 | facade | rule_needed |
| critical | d_L1_004 | door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2, inspector:Q3, argus_ai:AI1 | facade | rule_needed |
| critical | d_L1_005 | door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2, inspector:Q3, argus_ai:AI1 | facade | rule_needed |
| critical | d_L1_010 | door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2, inspector:Q3 | facade |  |
| critical | f_L0_001 | The staircase (f_L0_001) is completely open with no handrails or balustrades on either side, creating a significant fall risk. | inspector:Q3 | guard |  |
| major | F5:f_L0_010 | the architect's question F5 (clashing furniture) is open for f_L0_010: f_L0_010 (bathtub) and f_L0_026 still overlap 0.33 m: no free place within the move limits | process:P3 | architect |  |
| major | F5:f_L0_026 | the architect's question F5 (clashing furniture) is open for f_L0_026: f_L0_026 (washbasin) and f_L0_010 still overlap 0.33 m: no free place within the move limits | process:P3 | architect |  |
| major | F5:f_L1_011 | the architect's question F5 (clashing furniture) is open for f_L1_011: f_L1_011 (bathtub) and f_L1_025 still overlap 0.25 m: no free place within the move limits | process:P3 | architect |  |
| major | F5:f_L1_025 | the architect's question F5 (clashing furniture) is open for f_L1_025: f_L1_025 (washbasin) and f_L1_011 still overlap 0.25 m: no free place within the move limits | process:P3 | architect |  |
| major | d_L0_001 | The main entrance (d_L0_001) is barely legible: there is no clear door leaf, handle, canopy or step detail, and the small porch/landing is ambiguous. A client cannot tell where the front door actually is or how it is reached. | inspector:Q9, judge:Q9 | entrance_layout |  |
| major | d_L0_004 | Argus: door d_L0_004 looks like something else in 1 view(s): cam_r_L0_salon_1 (seen as wall_art) | inspector:K2 | wrong_model |  |
| major | d_L1_009 | Argus: The door opens directly into the basin/toilet cluster, blocking the approach to the fixtures. | inspector:Q9 | entrance_layout |  |
| major | f_L0_027 | Argus: ottoman f_L0_027 differs from the drawing (tolerance 0.05 m): 0.86 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325] | inspector:K3 | fixture_place |  |
| major | f_L0_028 | Argus: ottoman f_L0_028 differs from the drawing (tolerance 0.05 m): 0.09 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325] | inspector:K3 | fixture_place |  |
| major | f_L0_029 | Argus: ottoman f_L0_029 differs from the drawing (tolerance 0.05 m): 0.63 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325] | inspector:K3 | fixture_place |  |
| major | f_L0_030 | Argus: ottoman f_L0_030 differs from the drawing (tolerance 0.05 m): 0.07 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325] | inspector:K3 | fixture_place |  |
| major | f_L1_001 | Argus: The stair opening and landing edge have a flimsy, incomplete guard. The glass panel is a thin placeholder with a large open gap below it and no proper balustrade, which is a clear fall risk and looks broken. | inspector:Q3 | guard |  |
| major | f_L1_007 | Argus: desk f_L1_007 differs from the drawing (tolerance 0.05 m): 0.15 m from its drawn place | inspector:K3 | fixture_place |  |
| major | f_L1_025 | Argus: The washbasin sits too low and is wedged behind the toilet, so it is not at a usable working height and cannot be reached. | inspector:Q2 | wrong_model |  |
| major | o_L0_002 | Argus: The entrance area is poorly resolved. The steps and handrails are basic, untextured geometry. The large terrace slab to the left is a raw, floating concrete block with no finish, making the whole approach look unfinished and un-stylish. | inspector:Q9 | entrance_layout |  |
| major | o_L1_001 | The balcony on the left is a floating slab with a railing but no visible support structure or door leading to it. It looks like a piece of the model was deleted or it is simply floating in the air. | inspector:Q1, inspector:Q3, judge:Q1 | opening_sense |  |
| major | r_L0_mutfak | Argus: window win_L0_007 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L0_mutfak_3 | inspector:K1, argus_ai:AI1 | interior_camera | agent_round |
| major | r_L0_salon | Argus: door d_L0_004 looks like something else in 1 view(s): cam_r_L0_salon_1 (seen as wall_art) | inspector:K2, argus_ai:AI1 | interior_camera | agent_round |
| major | r_L1_ebeveyn_y_odasi | Argus: door d_L1_007 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L1_ebeveyn_y_odasi_2 | inspector:K1, inspector:K4, argus_ai:AI1 | interior_camera | agent_round |
| major | r_L1_hol | Argus: The door on the right is extremely close to the camera and fills the entire side of the frame. It's unclear if this is a door or a wall panel, and its proximity makes the space feel claustrophobic and confusing. | inspector:Q1, argus_ai:AI1 | interior_camera | agent_round |
| major | r_L1_soyunma_odasi | The L1 'Soyunma Odası' (storage/dressing room) is a 5.9 m2 room whose only piece is a wardrobe, and its two render views are scored 1/5 with a metered exposure of +9 EV (the room is effectively a dark, bare box). A dressing room with no mirror, no bench and no light reads as an unfinished storage closet, not a usable room. | argus_ai:AI1 | fit | agent_round |
| major | sa_L0_veranda | The documents label a VERANDA on L0, but the model has no outline for it (not built). A labelled veranda is a client-visible outdoor space; its absence is a loss of documented content. | argus_ai:AI1 | site | rule_needed |
| major | sa_L1_balkon | The documents label a BALKON on L1, but the model has no outline for it (not built). The L1 image shows a railed terrace on the north-west, so the balcony exists in the drawing but was not built as a site area. | argus_ai:AI1 | site | rule_needed |
| major | w_L0_003 | Argus: The downpipe on the corner is a simple black cylinder that looks like a placeholder. It lacks a proper gutter connection at the top and a splash block at the bottom. | inspector:Q8, judge:Q8 | rain_water |  |
| major | win_L1_003 | the ray through opening win_L1_003 hits furn_f_L1_014 (furniture): something blocks the way through | process:P5 | build | clear_opening |
| minor | d_L1_008 | The door on the right is extremely close to the camera and fills the entire side of the frame. It's unclear if this is a door or a wall panel, and its proximity makes the space feel claustrophobic and confusing. | inspector:Q1, judge:Q1 | opening_sense |  |
| minor | r_L0_banyo | The L0 bathroom (6.7 m2) holds a bathtub, a toilet and a washbasin, and its render is scored 2/5. The bathtub is bare with no shower head, no faucet and no bath mat, and the washbasin clashes with the bathtub; the bathroom reads as a bare, unfinished box, not a usable bathroom. | argus_ai:AI1 | fit | agent_round |
| minor | r_L1_banyo | The L1 'Banyo' (6.7 m2) holds a bathtub, a toilet, a washbasin and a washing machine, and its render is scored 2/5. The room is over-furnished for its size and the washing machine is not a typical bathroom fixture; the render should show the room, not a cluttered corner. | argus_ai:AI1 | fit | agent_round |
| minor | r_L1_cocuk_odasi | The L1 children's room (22.4 m2) holds a double bed, a dresser and a nightstand, and its three render views are all scored 2/5. A 22 m2 children's room with only a double bed, a dresser and a nightstand is under-furnished; it needs a desk, a chair and a rug to read as a child's room. | argus_ai:AI1 | fit | agent_round |
| minor | r_L1_dus | The L1 'Duş' (shower room, 4.5 m2) holds a shower, a toilet and a washbasin, and its render is scored 2/5 with the camera pressed against the fixtures. A 4.5 m2 bathroom with three fixtures is cramped; the camera should be set to show the room, not jammed against the basin. | argus_ai:AI1 | render | rerun_stage |
| minor | r_L1_oda_2 | The L1 room 'Oda 2' is typed as living (11.3 m2) but holds only a sofa and a floor lamp. A living room with no coffee table, no TV and no rug reads as a bare waiting corner, and its two render views are scored 2/5. | argus_ai:AI1 | fit | agent_round |

## other: not classified yet: a new kind to name

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | cam_r_L1_soyunma_odasi_1 | cam_r_L1_soyunma_odasi_1: the metered exposure wanted +9.08 EV, the cap is +3.00 EV (6.08 stops over); the room is too dark for the camera (incident p50 0.00166 at target 0.9); the room needs about x67.79 its light, set_lighting gives up to x3 | inspector:lighting_dark | lighting_beyond_cap |  |
| critical | cam_r_L1_soyunma_odasi_2 | cam_r_L1_soyunma_odasi_2: the metered exposure wanted +9.33 EV, the cap is +3.00 EV (6.33 stops over); the room is too dark for the camera (incident p50 0.00140 at target 0.9); the room needs about x80.24 its light, set_lighting gives up to x3 | inspector:lighting_dark | lighting_beyond_cap |  |
| major | TEXT:29AC25 | piece the documents name, not placed: the documents name a dresser ('*SIFONIYER' (TEXT:29AC25)) at (8.11, 4.91) m on L1 and no drawn dresser stands there: not added: the nearest place that passes every check in r_L1_ebeveyn_y_odasi is 1.47 m from the text (more than 1 m) | inspector:NR | untyped |  |
| major | f_L0_009 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_004_ctx.png) | inspector:NR | untyped |  |
| major | f_L1_002 | untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | inspector:NR | untyped |  |
| major | f_L1_019 | untyped drawn piece left for review: drawn piece 1.20 x 0.55 m in r_L1_oda_2 has no type (AI passes: desk, dresser); the documents name a dresser here ('*SIFONIYER' (TEXT:29ABD3), on the footprint): not used: a living room holds no dresser: not built (plan crop recognition/crops/sym_L1_014_ctx.png) | inspector:NR | untyped |  |
| major | levels | a warning no rule knows: levels: the ground floor (building z 0) is printed +0.50 in the section: every relative mark of the plans is read +0.50 m lower (one height frame) (The ground floor is being read 0.50 m lower than it should be. Setting the floor level to 0.00 m will correct the relative heights of all elements on L0.) | argus_ai:AI3 | reading | set_room_floor |
| major | r_L1_soyunma_odasi | Argus: The L1 'Soyunma Odası' (dressing room) is typed 'other' and holds only a wardrobe. A dressing room is a bedroom-adjacent room; it should be typed as a bedroom/dressing room and furnished as a set (wardrobe + mirror + seating), not left as a bare 'other' room with one piece. | inspector:AI1 | room_type |  |
| minor | f_L0_010 | a warning no rule knows: furniture clash left: f_L0_010 and f_L0_026 overlap 0.33 m (f_L0_010 overlaps f_L0_026 by 0.33 m; moving f_L0_010 to the nearest free place in its room will resolve the clash.) | argus_ai:AI3 | fit | move_piece |
| minor | f_L1_011 | a warning no rule knows: furniture clash left: f_L1_011 and f_L1_025 overlap 0.25 m (f_L1_011 overlaps f_L1_025 by 0.25 m; moving f_L1_011 to the nearest free place in its room will resolve the clash.) | argus_ai:AI3 | fit | move_piece |
| minor | r_L1_ebeveyn_y_odasi | a warning no rule knows: TEXT:29AC25: the documents name a dresser ('*SIFONIYER' (TEXT:29AC25)) at (8.11, 4.91) m on L1 and no drawn dresser stands there: not added: the nearest place that passes every check in r_L1_ebeveyn_y_odasi is 1.47 m from the text (more than 1 m) (The dresser label is 1.47 m from the nearest valid placement, and the room's program does not require a dresser; the label is l | argus_ai:AI3 | fit | rule_needed |
| minor | win_L1_003 | a warning no rule knows: win_L1_003: door ray hits furn_f_L1_014 (furniture); a furniture covers the opening (f_L1_014 covers the opening win_L1_003; moving it to the nearest free place in its room will clear the window.) | argus_ai:AI3 | fit | move_piece |

## process: the run itself: a stage failed or was skipped, a test failed, time was left unused, a question stayed unanswered

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | big_loop | the big loop did not raise the house score (first 26.3; 0 cycle(s); stop: cycle 1: no_edit) | process:P9 | agent | more_cycles |
| major | f_L0_022 | Argus: a warning no rule knows: levels: f_L0_022 moved to symbols (sym_f_L0_022): a level-mark symbol, not furniture (a small drawn piece around a level mark text: '+0,50'); drawn as unknown 0.88 x 0.34 m | inspector:P0, argus_ai:AI3 | untyped | mark_not_furniture |
| major | r_L1_soyunma_odasi | Argus: a group the room should have found no place: r_L1_soyunma_odasi: completion added nothing, nothing fits: dressing: no place passes the checks | inspector:P2 | missing_member |  |
| major | run | the run ended 16 min before its deadline with 303 open major point(s): the time could have gone to more fix cycles | process:P8 | scheduler | more_cycles |
| major | sym_L1_008 | Argus: a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified | inspector:P2 | wrong_type |  |
| major | test_refit_library_models_fit_the_style[real06] | test tests.gpu.test_furnish::test_refit_library_models_fit_the_style[real06] failure: AssertionError: real06: library models of another style or without a mattress: [('f_L0_007', 'abo_B072PZ4LQ2', ['modern minimal', 'minimal', 'modern'], None), ('f_L1_009', 'abo_B0154VUESC', ['modern minimal', 'minimal', 'modern'], True), ('f_L1_013', '3dwh_023ac37b6602f45d849aaa00', ['minimal', 'modern'], None),  | process:P4 | tests |  |
| major | views | 4 view(s) marked for review: cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3 | render:K4 | check |  |
| minor | elevation r# (all) | a check that could not run: elevation r# (all): 4 cases, e.g. elevation r1 (all): its openings are not checked against the plans (the side needs the north arrow) | process:P2 | building |  |
| minor | elevations | 4 elevation(s) could not be compared with the model (r1, r2, r7, r8): the elevation has neither a view bearing nor a side: nothing to compare | render:K4 | check |  |
| minor | the drawn section r# is not checked point by point against the roof | a check that could not run: the drawn section r5 is not checked point by point against the roof: its ends at s -0.50 / 16.80 m and the roof outline's at -0.28 / 15.03 m along y are up to 1.77 m apart (over 0.30 m: the section does not run one-to-one with the plan); its roof line drops 1.43 m at s 8.55 m on the way up to its highest point (trusses, trims or another roof drawn with it: not one roof  | process:P2 | scene |  |

## silent: a stage noted a problem in a warning and nothing acted on it

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | f_L0_015 | the agent tried 4 times to fix D3 on f_L0_015 (Argus: The bright honey-oak coffee table is a third, clashing wood tone against the pale floor and the muted upholstery;) with swap_model; code refused every try, most often: asset_exists: no catalogue model 'coffee_table_pale_wood' | process:P10 | agent | rule_needed |
| major | f_L1_012 | the agent tried 8 times to fix F3 on f_L1_012 (bed_double: the headboard stands in the room (0.06 m off)) with move_piece; code refused every try, most often: snap: f_L1_012: no free place on wall w_L1_027 (doors, windows, at most 1.2 m from the drawn place) | process:P10 | agent | rule_needed |
| major | f_L1_014 | the agent tried 8 times to fix F7 on f_L1_014 (wardrobe blocks door win_L1_003) with move_piece; code refused every try, most often: f_L1_014: clearance_ok | process:P10 | agent | rule_needed |
| major | f_L1_015 | the agent tried 7 times to fix G11 on f_L1_015 (wardrobe f_L1_015: its front use zone is not reached by a 0.60 m walkway from door win_L1_003) with move_piece; code refused every try, most often: f_L1_015: clearance_ok | process:P10 | agent | rule_needed |
| major | f_L1_019 | the agent tried 6 times to fix NR on f_L1_019 (untyped drawn piece left for review: drawn piece 1.20 x 0.55 m in r_L1_oda_2 has no type (AI passes: desk, dresser); the) with retype_piece; code refused every try, most often: retype: dresser is no candidate for f_L1_019 (1.20 x 0.55 m at [1.63, 9.64]): the size table and the room / zone give armchair, chaise, display_cabinet, sideboa | process:P10 | agent | rule_needed |
| major | f_L1_026 | the agent tried 4 times to fix Q5 on f_L1_026 (Argus: Only one nightstand is present while the schedule lists two (f_L1_026, f_L1_028); the bed is asymmetric with a la) with move_piece; code refused every try, most often: f_L1_026: inside_room; f_L1_026: inside_room (outline: nightstand reaches 0.06 m² through the room outline, up to 0.150 m deep; 0.00 m² up to 0.000 m deep befor | process:P10 | agent | rule_needed |
| major | r_L0_salon | the agent tried 8 times to fix Q4 on r_L0_salon (Argus: The coffee table (f_L0_015) is listed in the room data but is missing from the render. This leaves the seating ar) with place_group, set_camera; code refused every try, most often: the arguments of set_camera do not match its schema: kind: 'room' is not one of ['interior', 'exterior'] | process:P10 | agent | rule_needed |
| major | r_L1_banyo | the agent tried 16 times to fix Q4 on r_L1_banyo (Argus: The toilet (f_L1_024) is missing from the render. A bathroom without a toilet is a fundamental, client-visible fa) with set_camera; code refused every try, most often: the arguments of set_camera do not match its schema: kind: 'room' is not one of ['interior', 'exterior'] | process:P10 | agent | rule_needed |
| major | r_L1_dus | the agent tried 12 times to fix Q4 on r_L1_dus (Argus: The shower is missing entirely; a bathroom with no shower/wet zone makes no sense.) with set_camera; code refused every try, most often: the arguments of set_camera do not match its schema: kind: 'room' is not one of ['interior', 'exterior'] | process:P10 | agent | rule_needed |
| major | r_L1_soyunma_odasi | the agent tried 7 times to fix Q4 on r_L1_soyunma_odasi (Argus: The dressing room (soyunma odasi) is completely empty. It has no wardrobe, bench, mirror, or any of the fixtures ) with place_group, set_camera; code refused every try, most often: cam_r_L1_soyunma_odasi_1: eye height -1.50 m (wanted 1.2-1.6 m) | process:P10 | agent | rule_needed |
| minor | f_L1_028 | the agent tried 4 times to fix F3 on f_L1_028 (nightstand: its back is not on a wall (0.06 m off)) with move_piece; code refused every try, most often: snap: f_L1_028: no free place on wall w_L1_027 (doors, windows, at most 1.2 m from the drawn place) | process:P10 | agent | rule_needed |
| minor | facade | the agent tried 4 times to fix ? on facade (None) with set_material; code refused every try, most often: facade: look 'facade_stone_01' is not in the vocabulary | process:P10 | agent | rule_needed |

## stale: a stage acted on an older state than the one built (the critic reading doors the architect had made windows)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | F7: 2 elements | the critic finds F7 on 2 element(s) (d_L1_011, win_L1_003; e.g. bed_double blocks door d_L1_011) and the architect's rule F2 / F3 says they are fine: the rule needs these cases | consistency:Y2 | architect | rule_needed |
| critical | G11: 18 elements | the critic finds G11 on 18 element(s) (d_L0_004, f_L0_016, f_L0_019, d_L0_003, f_L0_002, f_L0_020 ...; e.g. the main walkway from the entrance door is below 0.80 m between doors d_L0_004 and d_L0_006) and the architect's rule C1 never asked about them: the rule needs these cases | consistency:Y1 | architect | rule_needed |
| critical | X3: 4 elements | the critic finds X3 on 4 element(s) (d_L1_001, d_L1_004, d_L1_005, d_L1_010; e.g. door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air)) and the architect's rule E1 never asked about them: the rule needs these cases | consistency:Y1 | architect | rule_needed |
| major | F9: 4 elements | the critic finds F9 on 4 element(s) (f_L0_031, f_L0_032, f_L1_007, f_L1_010; e.g. kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m²) and the architect's rule F5 says they are fine: the rule needs these cases | consistency:Y2 | architect | rule_needed |
| major | G10: 5 elements | the critic finds G10 on 5 element(s) (f_L0_010, f_L0_026, f_L1_011, f_L1_024, f_L1_025; e.g. bathtub f_L0_010: 0.40 m clear in front, needs ≥ 0.53 m) and the architect's rule S4 never asked about them: the rule needs these cases | consistency:Y1 | architect | rule_needed |
| major | G12: 4 elements | the critic finds G12 on 4 element(s) (win_L1_005, win_L1_004, win_L1_011, o_L1_003; e.g. wardrobe f_L1_014 (2.10 m) stands in front of window win_L1_005 (sill 1.80 m + 0.05)) and the architect's rule F3 says they are fine: the rule needs these cases | consistency:Y2 | architect | rule_needed |
| major | f_L1_013 | the critic finds F6 on 1 element(s) (f_L1_013; e.g. sofa: the free zone in front of it is blocked by f_L1_027) and the architect's rule F4 says they are fine: the rule needs these cases | consistency:Y2 | architect | rule_needed |
| major | f_L1_018 | the critic finds F6 on 1 element(s) (f_L1_018; e.g. armchair: the free zone in front of it is blocked by f_L1_022) and the architect's rule F4 never asked about them: the rule needs these cases | consistency:Y1 | architect | rule_needed |

## taste: the house does not look designed (pieces that do not match, plain or dated rooms, a garage door look)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L1_003 | The camera is jammed against the door/wardrobe corner: the frame is filled by a dark door leaf and a wall, with no eye-height view of the room or its main group. This is a bad_camera shot, not a presentation view. | inspector:V1, judge:V1 | interior_camera |  |
| critical | f_L0_001 | The camera is positioned so that a large blank wall/partition fills the entire right half of the frame. The main kitchen group is not in view. This is a bad camera angle that makes the render useless. | inspector:V1, judge:V1 | interior_camera |  |
| critical | f_L1_006 | The bed is a crude low-poly model: the mattress is a lumpy, distorted mesh, the 'duvet' is a crumpled sheet that falls off the side, and the frame is a thin wireframe that looks like a construction error. | inspector:D2, inspector:D3, judge:D2 | wrong_model |  |
| critical | f_L1_009 | Argus: The bedding on this bed is a crude, melted-looking blob. It does not look like a duvet or pillows; it looks like a failed simulation or a low-poly placeholder. This is the single most embarrassing element in the render. | inspector:Q5, inspector:D2, judge:Q5, judge:D2 | wrong_model |  |
| critical | f_L1_013 | Argus: The main sofa is a crude, low-poly white block. It has no texture, no realistic form, and looks like a placeholder model, not a piece of furniture. | inspector:D3, inspector:D2, judge:D3, judge:D2 | wrong_model |  |
| critical | f_L1_014 | Camera is pressed against a wall/cabinet face: the frame is a dark flat surface with a wood sliver, no room or furniture group visible. | inspector:S3, inspector:V1, judge:V1 | built_front |  |
| critical | f_L1_015 | Second wardrobe is not visible in frame; the main group of the room is missing from the shot. | inspector:V1, judge:V1 | interior_camera |  |
| critical | w_L0_001 | The trees in the background are low-poly 'lollipop' models with flat, textured discs for foliage. This is a placeholder asset that makes the entire render look like a video game level rather than a real house. | inspector:D2, inspector:Q7, inspector:D3, judge:D2, judge:Q7, judge:D3 | wrong_model |  |
| major | cam_r_L0_banyo_1 | the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The bathroom itself is a coherent, clean white set, but it is far from client-ready. The view out of the window is a crude, low-poly 'lollipop' landscape that instantly breaks the illusion of a real home. Inside, the room is completely bare: no mirror, no towel, no fixtures, no decor. It reads as an empty 3D model, not a fi | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_1 | the judge scores view cam_r_L0_mutfak_1 2/5 (a client would not accept it): The kitchen itself is a clean, minimal white set, but the render is not client-ready. The outdoor view is a crude, low-poly 'lollipop' landscape that makes the whole image look like a placeholder, and the room is missing the main pieces the client expects to see (dining set, fridge). | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_2 | the judge scores view cam_r_L0_mutfak_2 2/5 (a client would not accept it): The kitchen reads as a grey-box placeholder, not a finished interior. The main run is a row of blank, handle-less boxes with no hob, no cooktop, no wall cabinets and no visible fridge, so the room lacks its anchor appliances. The island is a plain slab with a shallow blue basin and a single tap, no cooktop or storage detai | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_3 | the judge scores view cam_r_L0_mutfak_3 1/5 (a client would not accept it): The camera is pressed against a blank wall that fills the right half of the frame, and the visible part of the kitchen is an empty shell: a single bare counter with a sink, no hob, no fridge, no cabinets, no dining set. The outdoor view is a crude flat-paste with lollipop trees. This is not client-ready. | judge:J1 | agent |  |
| major | cam_r_L0_salon_1 | the judge scores view cam_r_L0_salon_1 2/5 (a client would not accept it): A 55 m2 salon with no sofa and no dining set, just four identical egg chairs around a tiny table, reads as a waiting room, not a living room. The view outside the window is a crude low-poly 'lollipop' tree on a flat green plane, which breaks the illusion of a real home. The room is also bare: no rug, no art, no lighting, no | judge:J1 | agent |  |
| major | cam_r_L0_salon_2 | the judge scores view cam_r_L0_salon_2 2/5 (a client would not accept it): The render shows a dining corner, but the room is a 55.6 m2 salon whose main group (sofa, coffee table, armchairs) is absent, so the space reads as a dining room in the wrong room. The dining set itself is inconsistent: four chairs of two different models (f_L0_027/f_L0_028 vs f_L0_029/f_L0_030) around one table, and the sc | judge:J1 | agent |  |
| major | cam_r_L0_salon_3 | the judge scores view cam_r_L0_salon_3 2/5 (a client would not accept it): The salon reads as an empty shell with two mismatched chairs parked against a wall, not a designed living room. The main seating group, coffee table and bookshelf from the piece list are absent from frame, and the dining set visible through the opening is a different style (warm wood, sculptural base) from the two armchairs | judge:J1 | agent |  |
| major | cam_r_L1_banyo_1 | the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The room itself is a clean, coherent white bathroom, but the render is not client-ready. The view out of the window is a crude, low-poly 'lollipop' landscape that instantly breaks the illusion of a real home, and the room is completely bare (no mirror, no towel, no hardware, no decor), which reads as an unfinished grey-box  | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_1 | the judge scores view cam_r_L1_cocuk_odasi_1 2/5 (a client would not accept it): The room is bright and the camera is fine, but it is not client-ready. The outdoor trees are crude 'lollipop' meshes that ruin the view, the two beds are different models/scales that do not belong together, and the dresser is a plain, boxy piece that looks like a placeholder. A client would point at the trees and the  | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_2 | the judge scores view cam_r_L1_cocuk_odasi_2 2/5 (a client would not accept it): The room is bright and the camera is fine, but it does not read as a designed children's bedroom. The two beds are from different collections (a solid wood platform bed vs. a thin metal-frame bed with a boxy base), the dresser is a plain blocky box, and the bedding on the right bed is a crumpled, low-poly blob. The ov | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_3 | the judge scores view cam_r_L1_cocuk_odasi_3 2/5 (a client would not accept it): The room is a mess of placeholder geometry. The bed is a crude low-poly blob with a wireframe frame and a 'duvet' that looks like a crumpled sheet, and the dresser is a plain box with floating dots for handles. The two wood tones (floor vs. nightstand) and the generic white furniture make it look like a grey-box test, | judge:J1 | agent |  |
| major | cam_r_L1_dus_1 | the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The camera is pressed against the shower glass and a tiled wall, so the frame is mostly a blank corner; the actual room (basin, shower, toilet) is barely legible. The view outside the windows is a crude low-poly 'lollipop' landscape on a flat green plane, which reads as a broken placeholder, not a designed home. The interior  | judge:J1 | agent |  |
| major | cam_r_L1_ebeveyn_y_odasi_3 | the judge scores view cam_r_L1_ebeveyn_y_odasi_3 2/5 (a client would not accept it): The room is lit and the bed is placed, but it is not client-ready. The two lounge chairs are different models and colours (a white shell chair vs. a grey wing chair), which reads as a mistake, not a design choice. The floor lamp is oversized and its shade sits at head height, blocking the window view. The outdoor  | judge:J1 | agent |  |
| major | cam_r_L1_hol_1 | the judge scores view cam_r_L1_hol_1 2/5 (a client would not accept it): The hall itself is a bare, empty corner: a plain door, a small stair landing and two windows, with no shoe cabinet, no decor and no sense of a finished entrance. The biggest problem is the view outside: the windows show a crude, low-poly 'lollipop' tree and a flat green plane, which makes the whole render look like a placehol | judge:J1 | agent |  |
| major | cam_r_L1_oda_1 | the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): The render is a tight, tilted close-up of a corner that shows almost nothing of the room. The main piece, the shoe cabinet, is cut off at the bottom left and barely visible. The frame is dominated by a blank wall and two doors, making the space look unfinished and unstyled. It is not presentable to a client. | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_1 | the judge scores view cam_r_L1_oda_2_1 2/5 (a client would not accept it): The room is coherent and the camera is fine, but the furniture is a mismatched, dated set that a client would not accept for a stylish home. The olive sofa is plain and the dark, heavy carved bench is a completely different style and wood tone, so the two main pieces do not belong together. The pineapple print is a cheap, o | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_2 | the judge scores view cam_r_L1_oda_2_2 2/5 (a client would not accept it): The room itself is a plain, believable corner, but the render is not client-ready. The outdoor scene is a crude low-poly diorama (lollipop trees, flat green ground) that makes the whole image read as a broken placeholder, and the furniture is a mismatched, boxy set: a flat, backless green bench/sofa against a dark, heavy wo | judge:J1 | agent |  |
| major | cam_r_L1_soyunma_odasi_1 | the judge scores view cam_r_L1_soyunma_odasi_1 1/5 (a client would not accept it): The render is unusable for a client: it is a near-black, poorly lit close-up of a door and a wall corner, not a view of the room. The camera is pressed against the wardrobe/door, the lighting is almost off, and none of the room's function or furniture is visible. It reads as a broken camera shot, not a designed spac | judge:J1 | agent |  |
| major | cam_r_L1_soyunma_odasi_2 | the judge scores view cam_r_L1_soyunma_odasi_2 1/5 (a client would not accept it): The render is unusable for a client presentation. The camera is pressed flat against a wall or cabinet face, so the frame is filled with a dark, untextured surface and a sliver of wood trim; the room, the two wardrobes, and the windows are not visible. The lighting is near-black, so no material, joinery or style can | judge:J1 | agent |  |
| major | d_L0_001 | The main entrance door is a generic, flat white slab with no handle, texture, or frame detail. It looks unfinished and clashes with the modern style of the house. | inspector:Q7, judge:Q7 | opening_style |  |
| major | d_L1_002 | Argus: Second identical flat-slab door with no frame or hardware detail; two bare slabs side by side look like placeholders rather than finished doors. | inspector:Q7, judge:Q7 | opening_style |  |
| major | ext_1 | Argus: the judge scores view ext_1 2/5 (a client would not accept it): The render is not client-ready. The landscaping is a crude placeholder that destroys the realism of the scene, and the architectural details (like the floating balcony) are logically flawed. | inspector:J1, judge:J1 | site |  |
| major | ext_2 | Argus: the judge scores view ext_2 2/5 (a client would not accept it): The building model itself is a clean, coherent two-storey box, but the presentation is far from client-ready. The environment is a grey void with a flat white ground plane and crude, low-poly 'lollipop' trees that make the render look l | inspector:J1, judge:J1 | site |  |
| major | ext_4 | Argus: the judge scores view ext_4 2/5 (a client would not accept it): The render is not client-ready. The 'lollipop' trees and flat, untextured ground make the scene look like a low-poly video game rather than a real architectural visualization. The house itself looks unfinished with bare white surfaces a | inspector:J1, judge:J1 | site |  |
| major | ext_5 | Argus: the judge scores view ext_5 2/5 (a client would not accept it): The building model itself is a coherent, simple two-storey house, but the render is far from client-ready. The environment is a flat grey-green void with a hard horizon and a row of crude 'lollipop' trees, which makes the whole image lo | inspector:J1, judge:J1 | site |  |
| major | ext_6 | Argus: the judge scores view ext_6 2/5 (a client would not accept it): The render is not client-ready. The landscaping is a major failure, using crude 'lollipop' trees and a flat, untextured ground plane that makes the house look like a video game asset. The balcony railing is a thin, industrial metal tube | inspector:J1, judge:J1 | site |  |
| major | f_L0_002 | The base cabinet run is a row of identical blank boxes with no handles, no material variation and no appliance integration. It reads as a parametric placeholder, not a designed kitchen. | inspector:D2, judge:D2 | wrong_model |  |
| major | f_L0_007 | The dark ribbed armchair and the cream armchair are different models, colours and styles placed side by side; they do not form a set. | inspector:Q5, judge:Q5 | wrong_model |  |
| major | f_L0_008 | Argus: The beige armchair (f_L0_008) is a different style (tufted, blocky) from the sofa (f_L0_011) and the dark chair (f_L0_007). The three pieces do not form a cohesive set, making the room look like a collection of random furniture rather than a curated interior. | inspector:Q5 | wrong_model |  |
| major | f_L0_010 | The bathtub is also completely bare. There is no shower head, no faucet, no bath mat, and no caddy. It looks like an empty white box. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L0_011 | The dining table (f_L0_011) is a plain, boxy slab that clashes with the sculptural egg chairs and the warm wood floor. It looks like a placeholder, not part of a coherent set. | inspector:D3, inspector:Q5, judge:D3, judge:Q5 | wrong_model |  |
| major | f_L0_012 | The tree visible through win_L0_001 is a crude low-poly 'lollipop' model with a wireframe canopy. It is a placeholder that destroys the render's credibility. | inspector:D2, judge:D2 | wrong_model |  |
| major | f_L0_015 | Argus: The bright honey-oak coffee table is a third, clashing wood tone against the pale floor and the muted upholstery; it does not belong to the room's palette. | inspector:V1, inspector:D3, judge:V1 | interior_camera |  |
| major | f_L0_016 | Four identical egg chairs (f_L0_016, f_L0_017, f_L0_018, f_L0_019) are the entire seating group. The repetition looks like a showroom display, not a designed living room. | inspector:Q5, judge:Q5 | wrong_type |  |
| major | f_L0_024 | Argus: The toilet is a bulky, dated two-piece model. It does not match the clean, modern aesthetic suggested by the large-format tiles and the simple, modern door. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L0_026 | The washbasin is completely bare. There is no mirror, no faucet, no soap dispenser, and no towel. A bathroom without these basic elements looks unfinished and un-stylish. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L0_029 | Chairs of two different models are mixed at one table (f_L0_027/f_L0_028 vs f_L0_029/f_L0_030), which reads as a mismatched set. | inspector:Q5, judge:Q5 | wrong_model |  |
| major | f_L0_031 | kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.074 m (allowed 0.030 m for a fixture piece) | inspector:S2 | drawn_layout |  |
| major | f_L0_033 | Argus: The wall-cabinet run (and the whole kitchen set) is a flat, untextured white with no appliances, cooktop or styling; it reads as a plain placeholder, not a designed kitchen for the project's style. | inspector:D3 | wrong_model |  |
| major | f_L1_001 | Argus: The stair and its metal-and-glass railing are a plain, generic system that does not express the project's style; it looks like a default placeholder rather than a designed element. | inspector:V1, inspector:Q7, judge:V1 | interior_camera |  |
| major | f_L1_007 | The dresser is a plain white box with floating dots for handles; it has no drawer lines, no texture, and no top surface, making it look like a placeholder. | inspector:D3, inspector:D2, judge:D3, judge:D2 | wrong_model |  |
| major | f_L1_010 | The nightstand is a different, warmer wood tone than the floor and clashes with the plain white furniture; it also looks like a simple box with no detail. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L1_016 | The dark, heavy carved wooden bench is a different style and wood tone from the olive sofa; the two main pieces do not belong together. | inspector:Q5, inspector:D3, judge:Q5, judge:D3 | wrong_model |  |
| major | f_L1_017 | The two armchairs are mismatched: f_L1_017 is a white molded shell chair while f_L1_018 is a grey upholstered wing chair. They do not form a coherent pair and look like a random selection. | inspector:Q5, judge:Q5 | wrong_model |  |
| major | f_L1_018 | Argus: The brown armchair clashes with the pink one and the rest of the neutral room. Its style and color are inconsistent with the other furniture. | inspector:D3 | wrong_model |  |
| major | f_L1_020 | Camera is jammed against the shower glass and the adjacent tiled wall; the frame is dominated by a blank corner and the room's main group is not in view. This is not a presentable shot. | inspector:V1, inspector:D3, judge:V1, judge:D3 | interior_camera |  |
| major | f_L1_022 | The floor lamp is wrong in scale and proportion. The shade is too large and sits at head height, partially blocking the window and looking like a table lamp stretched into a floor lamp. | inspector:D2, judge:D2 | wrong_model |  |
| major | f_L1_023 | The toilet is a standard, unstyled model. While functional, it contributes to the 'hospital' or 'construction site' feel of the room rather than a designed home. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L1_025 | The room is completely bare: no mirror above the washbasin, no towel, no soap, no hardware, no decor. It reads as an empty grey-box, not a styled, livable bathroom. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L1_026 | Argus: Only one nightstand is present while the schedule lists two (f_L1_026, f_L1_028); the bed is asymmetric with a lamp on one side and nothing on the other. | inspector:D3, inspector:Q5, judge:D3 | wrong_model |  |
| major | f_L1_027 | Argus: The floor lamp is an ornate, turned-wood classic style that clashes with the otherwise neutral and modern feel of the room. It feels out of place. | inspector:D2, inspector:D3, judge:D2 | wrong_model |  |
| major | f_L1_029 | The washbasin is a plain, dated utility sink with exposed chrome pipes. It is the only 'design' element in the room and it clashes with the otherwise clean, modern aesthetic. It makes the whole bathroom look cheap and unfinished. | inspector:D3, inspector:D2, judge:D3 | wrong_model |  |
| major | f_L1_030 | Argus: The shoe cabinet is a crude, low-poly model. It looks like a placeholder box with a grid texture, not a finished piece of furniture. | inspector:D2 | wrong_model |  |
| major | f_L1_035 | The desk is a very plain, thin-topped table with simple legs. It feels like a placeholder and does not match the quality or style of a well-designed bedroom. | inspector:D3, inspector:Q5, judge:D3, judge:Q5 | wrong_model |  |
| major | f_L1_036 | The black office chair is a generic, utilitarian model that clashes with the otherwise soft, light-wood bedroom aesthetic. It makes the corner look like a temporary workspace rather than a designed part of the room. | inspector:D3, inspector:Q5, judge:D3, judge:Q5 | wrong_model |  |
| major | f_L1_037 | The camera is poorly framed. It is too close to the corner and tilted, cutting off the main piece of furniture (the shoe cabinet) and failing to show the room's layout or scale. | inspector:V1, judge:V1 | interior_camera |  |
| major | o_L0_002 | The trees in the background are crude, low-poly 'lollipop' models that look like placeholders and completely break the realism of the scene. | process:P2, inspector:D2, judge:D2 | scene |  |
| major | o_L0_003 | The ground is a flat, untextured green plane with no detail, contributing to the 'grey box' or video game aesthetic. | inspector:D2, judge:D2 | wrong_model |  |
| major | r_L0_banyo | Argus: the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The render is a near-empty bathroom: the camera is aimed at a blank tiled wall, the toilet is missing from view, and the only visible furniture is a small washbasin. It reads as a grey-box placeholder, not a finished, stylish | inspector:J1, inspector:V1 | interior_camera |  |
| major | r_L0_mutfak | Argus: The second counter f_L0_031 at the right edge is cut off and shows only a bare slab; it does not connect to the island or to any wall run, so the two pieces do not read as one coherent set. | inspector:D3 | clearance |  |
| major | r_L0_salon | Argus: The camera is pointed almost entirely at a blank wall (the opening o_L0_002 side). The main fixtures are pushed to the far right edge, so the shot does not present the room's main group. | inspector:V1, inspector:J1 | interior_camera |  |
| major | r_L1_banyo | Argus: the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation. The room is listed as a bathroom with a shower (f_L1_031), yet the shower is completely missing, leaving a large, empty, unexplained corner. The visible fixt | inspector:J1, inspector:V1 | interior_camera |  |
| major | r_L1_dus | Argus: the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation for a 4.5 m2 bathroom. The most serious issue is that the washbasin (f_L1_029) is completely absent from the frame, so the room reads as a toilet-and-shower box | inspector:J1, inspector:V1 | interior_camera |  |
| major | r_L1_hol | Argus: The hall is empty and undecorated: no shoe cabinet, no console, no lighting or styling, so it looks like a bare shell rather than a designed entrance. | inspector:V1, judge:V1 | interior_camera |  |
| major | r_L1_oda | Argus: the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): The render is a dead-end hallway shot, not a room. The camera is aimed straight at a door, so the frame is 80% wall and door leaf. The only furniture, the shoe cabinet, is a crude, low-poly slatted box cut off in the corner. Th | inspector:J1, inspector:V1 | interior_camera |  |
| major | r_L1_soyunma_odasi | Overall the image is an empty, near-black corner with no usable view of the 5.9 m2 room; it would be embarrassing to show to a client. | process:P2, inspector:V1, inspector:J1, judge:V1 | building |  |
| major | w_L1_001 | The window and door frames are a generic, flat grey that clashes with the white facade and the dark roof. The overall fenestration is plain and undifferentiated, making the house look like a basic prefab unit rather than a stylish, well-designed home. | inspector:Q7, judge:Q7 | opening_style |  |
| major | win_L0_001 | The view through the windows is a crude, low-poly 'lollipop' landscape (blobby trees, flat green ground). This is a placeholder asset that makes the entire render look unfinished and unprofessional. | inspector:D2, judge:D2 | wrong_model |  |
| major | win_L0_004 | The view outside the window is a crude, low-poly 'lollipop' landscape. This is a major flaw that makes the entire render look like a video game placeholder rather than a real house. | inspector:D2, judge:D2 | wrong_model |  |
| major | win_L1_001 | The view outside the windows is a flat, low-poly cartoon landscape with lollipop-style trees. This 'flat_outdoor' backdrop makes the otherwise decent interior look like a placeholder render. | process:P2, inspector:D3, inspector:V1, judge:D3, judge:V1 | scene |  |
| major | win_L1_002 | The trees seen through the window and door are crude low-poly 'lollipop' blobs (a green disc on a stick). This is a placeholder model that makes the whole view look like a test render, not a real garden. | inspector:D2, judge:D2 | wrong_model |  |
| major | win_L1_003 | Window not visible; no daylight or context in the render. | inspector:V1, judge:V1 | interior_camera |  |
| major | win_L1_004 | The outdoor scene is a crude low-poly 'lollipop' tree on a flat green plane. It looks like a placeholder and undermines the whole render. | inspector:D2, inspector:D3, inspector:V1, judge:D2, judge:D3, judge:V1 | wrong_model |  |
| major | win_L1_005 | Same broken outdoor placeholder visible through this window; the flat green field and blob trees read as an unfinished scene. | inspector:D2, judge:D2 | wrong_model |  |
| major | win_L1_006 | The window view shows a crude low-poly 'lollipop' tree and a flat green ground plane, which reads as a placeholder and breaks the illusion of a real house. | inspector:V1, judge:V1 | interior_camera |  |
| major | win_L1_007 | The scenery outside the window is a crude low-poly 'lollipop' landscape (blobby trees, flat green ground). This is a placeholder asset that a client would immediately flag as fake and unfinished. | inspector:D2, judge:D2 | wrong_model |  |
| major | win_L1_008 | Same flat, cartoonish outdoor scene (blob tree, flat lawn) visible through the second window, reinforcing the unfinished look. | inspector:V1, inspector:D2, judge:V1, judge:D2 | interior_camera |  |
| minor | d_L0_003 | The stone path leading to the entrance is a rough, untextured mesh with visible cracks and uneven geometry, looking like a placeholder. | inspector:D2, judge:D2 | wrong_model |  |
| minor | d_L1_004 | The door is a plain, flat slab with a basic handle; it looks cheap and generic for a stylish project. | inspector:V1, judge:V1 | interior_camera |  |
| minor | f_L0_020 | sink_kitchen f_L0_020 built below the library level: fitting chose the parametric mesh | process:P7, inspector:D3, judge:D3 | fit | library_gap |
| minor | f_L0_040 | wall_cabinet f_L0_040 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_041 | wall_cabinet f_L0_041 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L1_011 | The overall aesthetic is very plain and dated. The large, flat, untextured white tiles and the basic, unadorned fixtures give the room a cheap, institutional look rather than a stylish one. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_012 | The bed is a basic, low-profile platform with a simple wooden frame. While not wrong, it is very plain and lacks the styling (e.g., a more substantial headboard or frame) expected in a client-ready render. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_028 | The second nightstand is identical to the first and shares the same plain, boxy design, reinforcing the lack of a cohesive, high-end furniture set. | inspector:D3, judge:D3 | wrong_model |  |
| minor | w_L0_002 | The dark stone plinth and the flat white wall surfaces (around w_L0_002) are untextured and read as bare material. Combined with the plain roof, the house looks dated and cheap for a client presentation. | inspector:Q7, judge:Q7 | opening_style |  |
| minor | win_L0_006 | no library model: built parametric or not at all: opening win_L0_006: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |

## Prevention: the kinds to guard

Each open kind with the findings no fix of the run covers, or that came back from an earlier run: these need a new rule or check (a general one, for every project), not a one-off patch.

- **misread** (36 open, 0 with a fix; arises: reading; guards: plan_vs_model (B*), the room-sense rules (G*, R*), model review M7)
  - inspector:G10 f_L0_010: bathtub f_L0_010: 0.40 m clear in front, needs ≥ 0.53 m
  - RECURRING inspector:G10 f_L0_026: washbasin f_L0_026: 0.09 m clear in front, needs ≥ 0.53 m
  - inspector:G10 f_L1_011: bathtub f_L1_011: 0.33 m clear in front, needs ≥ 0.53 m
  - RECURRING inspector:G10 f_L1_024: toilet f_L1_024: centre 0.33 m from the side wall or fixture on its right, needs ≥ 0.38 m
  - RECURRING inspector:G10 f_L1_025: washbasin f_L1_025: 0.26 m clear in front, needs ≥ 0.53 m
  - RECURRING inspector:Q4 f_L0_036: The room is 24.8 m2, which is large for a kitchen. The dining table (f_L0_036) and chairs (f_L0_037, f_L0_038) are listed in the JSON but are completely missing from the render, leaving a large, empty
  - inspector:Q4 f_L0_039: The refrigerator (f_L0_039) is listed in the JSON but is not visible in the render. A kitchen without a visible fridge is a major omission for a client presentation.
  - inspector:Q4 f_L0_035: The kitchen is missing its main functional pieces. The stove (f_L0_035), fridge (f_L0_039), and wall cabinets (f_L0_040, f_L0_041) are listed in the JSON but are not visible in the render. The room lo
  - inspector:Q4 f_L0_040: No wall cabinets are visible above the counter run. The upper wall is bare, leaving the kitchen looking empty and unbalanced.
  - RECURRING inspector:Q4 f_L0_015: The salon has no sofa and no dining set; the only seating is four identical egg armchairs around a small coffee table. A 55 m2 living room with no anchor piece makes no sense.
  - inspector:Q4 f_L0_011: A 55.6 m2 salon has no sofa or coffee table in frame; the room is anchored by a dining set, so the main living group is missing.
  - inspector:Q4 f_L1_037: The room appears empty. The only piece of furniture, the shoe cabinet, is mostly out of frame, leaving the visible area as a bare corner with no functional or decorative elements.
  - inspector:Q4 r_L0_banyo: Argus: The washbasin is a main piece of the bathroom but is completely missing from the frame. A bathroom render that shows only a toilet and a door makes no sense to a client.
  - inspector:Q4 r_L0_mutfak: Argus: The kitchen is missing its main functional anchor: there is no hob or cooktop on the worktop, making the room feel incomplete and non-functional.
  - inspector:Q4 r_L1_dus: Argus: The shower is missing entirely; a bathroom with no shower/wet zone makes no sense.
  - inspector:Q4 r_L1_banyo: Argus: The toilet (f_L1_024) is missing from the render. A bathroom without a toilet is a fundamental, client-visible failure.
  - RECURRING inspector:Q4 r_L1_ebeveyn_y_odasi: Argus: The scheduled armchair (and its pair f_L1_018) is absent; the bedroom has no seating or reading corner, so the main group is just a bed and the room feels incomplete.
  - RECURRING inspector:Q4 r_L1_soyunma_odasi: Argus: The dressing room (soyunma odasi) is completely empty. It has no wardrobe, bench, mirror, or any of the fixtures a dressing room requires. This is a missing-anchor failure: the room's entire pu
  - inspector:Q4 r_L0_salon: Argus: The salon has no sofa and no dining set; the only seating is four identical egg armchairs around a small coffee table. A 55 m2 living room with no anchor piece makes no sense.
  - RECURRING inspector:Q4 r_L1_hol: Argus: The hall is completely empty and unfinished. There is no lighting, no skirting boards, no floor finish, and no decor. It looks like a grey-box construction site, not a livable space.
  - inspector:Q4 r_L1_oda: Argus: The room is essentially empty. A 3.1 m2 hall should have some sense of purpose or at least be styled, but this is just a bare box with a door.
  - RECURRING inspector:Q4 f_L1_027: Argus: The room is missing its main anchor piece, the floor lamp (f_L1_027). A living room with only two mismatched sofas and no lighting or decor looks like an empty, unfinished space.
  - rule proposed by Argus AI (1 run(s)): A room's listed functional pieces (stove, fridge, cabinets) must be built and visible; if the render shows an empty shell, the build stage failed to place them.
  - rule proposed by Argus AI (1 run(s)): A living room of this size must have a sofa and a coffee table as its anchor group; if missing, the agent must place the standard living group.
  - rule proposed by Argus AI (1 run(s)): When a piece's type is not allowed in its room (e.g. a sofa in a bedroom), the reading stage must flag it for re-typing or removal, rather than keeping it unverified.
  - rule proposed by Argus AI (1 run(s)): When a room outline holds the labels of two rooms, the reading must split the outline at the wall between the two labelled zones (or flag the missing wall) instead of keeping one label and dropping the other; a dining zone labelled inside a living room is a separate room or a sub-zone, not a lost label.
  - rule proposed by Argus AI (1 run(s)): When a room's main functional pieces are not visible in the render, the camera must be adjusted to include them in the frame, prioritizing a wide-angle lens and a position that captures the entire worktop and appliances.
  - rule proposed by Argus AI (1 run(s)): When a living room lacks a sofa or coffee table, the layout engine must add a living group (sofa, coffee table, armchairs) to anchor the space, prioritizing a sofa along the longest wall.
  - rule proposed by Argus AI (1 run(s)): When a bathroom's main pieces (toilet, washbasin, bathtub) are not visible in the render, the camera must be adjusted to include them in the frame, prioritizing a wide-angle lens and a position that captures the entire room.
  - rule proposed by Argus AI (1 run(s)): When a kitchen's main functional pieces (stove, fridge, wall cabinets) are not visible in the render, the camera must be adjusted to include them in the frame, prioritizing a wide-angle lens and a position that captures the entire worktop and appliances.
  - rule proposed by Argus AI (1 run(s)): When a bathroom's main pieces (shower, toilet, washbasin) are not visible in the render, the camera must be adjusted to include them in the frame, prioritizing a wide-angle lens and a position that captures the entire room.
  - rule proposed by Argus AI (1 run(s)): When a bedroom's main pieces (bed, armchair, desk) are not visible in the render, the camera must be adjusted to include them in the frame, prioritizing a wide-angle lens and a position that captures the entire room.
  - rule proposed by Argus AI (1 run(s)): A dressing room (soyunma odasi) of 4-8 m2 is a valid room type for the dressing group; the placement solver must not reject it as 'no place passes the checks' when the room contains a wardrobe and has at least 0.9 m of clear floor space.
  - rule proposed by Argus AI (1 run(s)): A piece whose type is not allowed in its room must be re-typed by the reading stage to a type the room allows (or removed if it is not furniture) before the build; it must never be kept unverified.
  - rule proposed by Argus AI (1 run(s)): When one room outline holds the labels of two rooms, the reading stage must split the outline at the missing wall so each room gets its own outline and label.
- **taste** (95 open, 3 with a fix; arises: fit, decor, opening models; guards: judge (J*), visitor checks Q5, Q7, the fit's matched sets)
  - inspector:V1 r_L1_soyunma_odasi: Overall the image is an empty, near-black corner with no usable view of the 5.9 m2 room; it would be embarrassing to show to a client.
  - inspector:D2 o_L0_002: The trees in the background are crude, low-poly 'lollipop' models that look like placeholders and completely break the realism of the scene.
  - inspector:D3 win_L1_001: The view outside the windows is a flat, low-poly cartoon landscape with lollipop-style trees. This 'flat_outdoor' backdrop makes the otherwise decent interior look like a placeholder render.
  - RECURRING inspector:S2 f_L0_031: kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.074 m (allowed 0.030 m for a fixture piece)
  - inspector:V1 f_L1_014: Camera is pressed against a wall/cabinet face: the frame is a dark flat surface with a wood sliver, no room or furniture group visible.
  - inspector:D2 win_L0_004: The view outside the window is a crude, low-poly 'lollipop' landscape. This is a major flaw that makes the entire render look like a video game placeholder rather than a real house.
  - RECURRING inspector:D3 f_L0_026: The washbasin is completely bare. There is no mirror, no faucet, no soap dispenser, and no towel. A bathroom without these basic elements looks unfinished and un-stylish.
  - inspector:D3 f_L0_010: The bathtub is also completely bare. There is no shower head, no faucet, no bath mat, and no caddy. It looks like an empty white box.
  - RECURRING inspector:D3 f_L0_024: Argus: The toilet is a bulky, dated two-piece model. It does not match the clean, modern aesthetic suggested by the large-format tiles and the simple, modern door.
  - inspector:D2 win_L0_001: The view through the windows is a crude, low-poly 'lollipop' landscape (blobby trees, flat green ground). This is a placeholder asset that makes the entire render look unfinished and unprofessional.
  - RECURRING inspector:D2 f_L0_002: The base cabinet run is a row of identical blank boxes with no handles, no material variation and no appliance integration. It reads as a parametric placeholder, not a designed kitchen.
  - inspector:V1 f_L0_001: The camera is positioned so that a large blank wall/partition fills the entire right half of the frame. The main kitchen group is not in view. This is a bad camera angle that makes the render useless.
  - RECURRING inspector:Q5 f_L0_016: Four identical egg chairs (f_L0_016, f_L0_017, f_L0_018, f_L0_019) are the entire seating group. The repetition looks like a showroom display, not a designed living room.
  - inspector:D2 f_L0_012: The tree visible through win_L0_001 is a crude low-poly 'lollipop' model with a wireframe canopy. It is a placeholder that destroys the render's credibility.
  - inspector:D3 f_L0_011: The dining table (f_L0_011) is a plain, boxy slab that clashes with the sculptural egg chairs and the warm wood floor. It looks like a placeholder, not part of a coherent set.
  - inspector:D3 f_L0_015: Argus: The bright honey-oak coffee table is a third, clashing wood tone against the pale floor and the muted upholstery; it does not belong to the room's palette.
  - inspector:Q5 f_L0_029: Chairs of two different models are mixed at one table (f_L0_027/f_L0_028 vs f_L0_029/f_L0_030), which reads as a mismatched set.
  - RECURRING inspector:Q5 f_L0_007: The dark ribbed armchair and the cream armchair are different models, colours and styles placed side by side; they do not form a set.
  - inspector:D2 win_L1_007: The scenery outside the window is a crude low-poly 'lollipop' landscape (blobby trees, flat green ground). This is a placeholder asset that a client would immediately flag as fake and unfinished.
  - RECURRING inspector:D3 f_L1_025: The room is completely bare: no mirror above the washbasin, no towel, no soap, no hardware, no decor. It reads as an empty grey-box, not a styled, livable bathroom.
  - inspector:D2 win_L1_002: The trees seen through the window and door are crude low-poly 'lollipop' blobs (a green disc on a stick). This is a placeholder model that makes the whole view look like a test render, not a real gard
  - RECURRING inspector:D2 f_L1_009: Argus: The bedding on this bed is a crude, melted-looking blob. It does not look like a duvet or pillows; it looks like a failed simulation or a low-poly placeholder. This is the single most embarrass
  - inspector:D2 f_L1_007: The dresser is a plain white box with floating dots for handles; it has no drawer lines, no texture, and no top surface, making it look like a placeholder.
  - RECURRING inspector:D2 f_L1_006: The bed is a crude low-poly model: the mattress is a lumpy, distorted mesh, the 'duvet' is a crumpled sheet that falls off the side, and the frame is a thin wireframe that looks like a construction er
  - RECURRING inspector:D3 f_L1_010: The nightstand is a different, warmer wood tone than the floor and clashes with the plain white furniture; it also looks like a simple box with no detail.
  - inspector:V1 f_L1_020: Camera is jammed against the shower glass and the adjacent tiled wall; the frame is dominated by a blank corner and the room's main group is not in view. This is not a presentable shot.
  - inspector:D2 win_L1_004: The outdoor scene is a crude low-poly 'lollipop' tree on a flat green plane. It looks like a placeholder and undermines the whole render.
  - inspector:D2 win_L1_005: Same broken outdoor placeholder visible through this window; the flat green field and blob trees read as an unfinished scene.
  - inspector:D3 f_L1_023: The toilet is a standard, unstyled model. While functional, it contributes to the 'hospital' or 'construction site' feel of the room rather than a designed home.
  - inspector:D3 f_L1_029: The washbasin is a plain, dated utility sink with exposed chrome pipes. It is the only 'design' element in the room and it clashes with the otherwise clean, modern aesthetic. It makes the whole bathro
  - inspector:D3 f_L1_036: The black office chair is a generic, utilitarian model that clashes with the otherwise soft, light-wood bedroom aesthetic. It makes the corner look like a temporary workspace rather than a designed pa
  - inspector:D3 f_L1_035: The desk is a very plain, thin-topped table with simple legs. It feels like a placeholder and does not match the quality or style of a well-designed bedroom.
  - RECURRING inspector:Q5 f_L1_026: Argus: Only one nightstand is present while the schedule lists two (f_L1_026, f_L1_028); the bed is asymmetric with a lamp on one side and nothing on the other.
  - RECURRING inspector:Q5 f_L1_017: The two armchairs are mismatched: f_L1_017 is a white molded shell chair while f_L1_018 is a grey upholstered wing chair. They do not form a coherent pair and look like a random selection.
  - inspector:D2 f_L1_022: The floor lamp is wrong in scale and proportion. The shade is too large and sits at head height, partially blocking the window and looking like a table lamp stretched into a floor lamp.
  - inspector:V1 win_L1_006: The window view shows a crude low-poly 'lollipop' tree and a flat green ground plane, which reads as a placeholder and breaks the illusion of a real house.
  - inspector:V1 win_L1_008: Same flat, cartoonish outdoor scene (blob tree, flat lawn) visible through the second window, reinforcing the unfinished look.
  - RECURRING inspector:V1 r_L1_hol: Argus: The hall is empty and undecorated: no shoe cabinet, no console, no lighting or styling, so it looks like a bare shell rather than a designed entrance.
  - inspector:Q7 f_L1_001: Argus: The stair and its metal-and-glass railing are a plain, generic system that does not express the project's style; it looks like a default placeholder rather than a designed element.
  - inspector:V1 f_L1_037: The camera is poorly framed. It is too close to the corner and tilted, cutting off the main piece of furniture (the shoe cabinet) and failing to show the room's layout or scale.
  - inspector:Q7 d_L1_002: Argus: Second identical flat-slab door with no frame or hardware detail; two bare slabs side by side look like placeholders rather than finished doors.
  - inspector:Q5 f_L1_016: The dark, heavy carved wooden bench is a different style and wood tone from the olive sofa; the two main pieces do not belong together.
  - RECURRING inspector:D2 f_L1_013: Argus: The main sofa is a crude, low-poly white block. It has no texture, no realistic form, and looks like a placeholder model, not a piece of furniture.
  - inspector:D3 f_L1_027: Argus: The floor lamp is an ornate, turned-wood classic style that clashes with the otherwise neutral and modern feel of the room. It feels out of place.
  - RECURRING inspector:V1 d_L1_003: The camera is jammed against the door/wardrobe corner: the frame is filled by a dark door leaf and a wall, with no eye-height view of the room or its main group. This is a bad_camera shot, not a prese
  - inspector:V1 f_L1_015: Second wardrobe is not visible in frame; the main group of the room is missing from the shot.
  - inspector:V1 win_L1_003: Window not visible; no daylight or context in the render.
  - inspector:D2 w_L0_001: The trees in the background are low-poly 'lollipop' models with flat, textured discs for foliage. This is a placeholder asset that makes the entire render look like a video game level rather than a re
  - RECURRING inspector:Q7 d_L0_001: The main entrance door is a generic, flat white slab with no handle, texture, or frame detail. It looks unfinished and clashes with the modern style of the house.
  - RECURRING inspector:Q7 w_L1_001: The window and door frames are a generic, flat grey that clashes with the white facade and the dark roof. The overall fenestration is plain and undifferentiated, making the house look like a basic pre
  - inspector:D2 o_L0_003: The ground is a flat, untextured green plane with no detail, contributing to the 'grey box' or video game aesthetic.
  - inspector:V1 r_L0_salon: Argus: The camera is pointed almost entirely at a blank wall (the opening o_L0_002 side). The main fixtures are pushed to the far right edge, so the shot does not present the room's main group.
  - inspector:J1 r_L0_banyo: Argus: the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The render is a near-empty bathroom: the camera is aimed at a blank tiled wall, the toilet is missing from view, and t
  - inspector:D3 f_L0_033: Argus: The wall-cabinet run (and the whole kitchen set) is a flat, untextured white with no appliances, cooktop or styling; it reads as a plain placeholder, not a designed kitchen for the project's st
  - inspector:Q5 f_L0_008: Argus: The beige armchair (f_L0_008) is a different style (tufted, blocky) from the sofa (f_L0_011) and the dark chair (f_L0_007). The three pieces do not form a cohesive set, making the room look lik
  - inspector:J1 r_L1_banyo: Argus: the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation. The room is listed as a bathroom with a shower (f_
  - inspector:J1 r_L1_dus: Argus: the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation for a 4.5 m2 bathroom. The most serious issue is that
  - inspector:D3 f_L1_018: Argus: The brown armchair clashes with the pink one and the rest of the neutral room. Its style and color are inconsistent with the other furniture.
  - inspector:J1 r_L1_oda: Argus: the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): The render is a dead-end hallway shot, not a room. The camera is aimed straight at a door, so the frame is 80% wall and 
  - inspector:D2 f_L1_030: Argus: The shoe cabinet is a crude, low-poly model. It looks like a placeholder box with a grid texture, not a finished piece of furniture.
  - inspector:D3 r_L0_mutfak: Argus: The second counter f_L0_031 at the right edge is cut off and shows only a bare slab; it does not connect to the island or to any wall run, so the two pieces do not read as one coherent set.
  - inspector:J1 ext_1: Argus: the judge scores view ext_1 2/5 (a client would not accept it): The render is not client-ready. The landscaping is a crude placeholder that destroys the realism of the scene, and the architectu
  - inspector:J1 ext_2: Argus: the judge scores view ext_2 2/5 (a client would not accept it): The building model itself is a clean, coherent two-storey box, but the presentation is far from client-ready. The environment is 
  - inspector:J1 ext_4: Argus: the judge scores view ext_4 2/5 (a client would not accept it): The render is not client-ready. The 'lollipop' trees and flat, untextured ground make the scene look like a low-poly video game r
  - inspector:J1 ext_5: Argus: the judge scores view ext_5 2/5 (a client would not accept it): The building model itself is a coherent, simple two-storey house, but the render is far from client-ready. The environment is a f
  - inspector:J1 ext_6: Argus: the judge scores view ext_6 2/5 (a client would not accept it): The render is not client-ready. The landscaping is a major failure, using crude 'lollipop' trees and a flat, untextured ground pl
  - RECURRING judge:J1 cam_r_L0_banyo_1: the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The bathroom itself is a coherent, clean white set, but it is far from client-ready. The view out of the window is a crude, l
  - RECURRING judge:J1 cam_r_L0_mutfak_1: the judge scores view cam_r_L0_mutfak_1 2/5 (a client would not accept it): The kitchen itself is a clean, minimal white set, but the render is not client-ready. The outdoor view is a crude, low-poly 
  - RECURRING judge:J1 cam_r_L0_mutfak_2: the judge scores view cam_r_L0_mutfak_2 2/5 (a client would not accept it): The kitchen reads as a grey-box placeholder, not a finished interior. The main run is a row of blank, handle-less boxes with
  - judge:J1 cam_r_L0_mutfak_3: the judge scores view cam_r_L0_mutfak_3 1/5 (a client would not accept it): The camera is pressed against a blank wall that fills the right half of the frame, and the visible part of the kitchen is an
  - RECURRING judge:J1 cam_r_L0_salon_1: the judge scores view cam_r_L0_salon_1 2/5 (a client would not accept it): A 55 m2 salon with no sofa and no dining set, just four identical egg chairs around a tiny table, reads as a waiting room, no
  - RECURRING judge:J1 cam_r_L0_salon_2: the judge scores view cam_r_L0_salon_2 2/5 (a client would not accept it): The render shows a dining corner, but the room is a 55.6 m2 salon whose main group (sofa, coffee table, armchairs) is absent,
  - RECURRING judge:J1 cam_r_L0_salon_3: the judge scores view cam_r_L0_salon_3 2/5 (a client would not accept it): The salon reads as an empty shell with two mismatched chairs parked against a wall, not a designed living room. The main seat
  - RECURRING judge:J1 cam_r_L1_banyo_1: the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The room itself is a clean, coherent white bathroom, but the render is not client-ready. The view out of the window is a crud
  - RECURRING judge:J1 cam_r_L1_cocuk_odasi_1: the judge scores view cam_r_L1_cocuk_odasi_1 2/5 (a client would not accept it): The room is bright and the camera is fine, but it is not client-ready. The outdoor trees are crude 'lollipop' meshes th
  - RECURRING judge:J1 cam_r_L1_cocuk_odasi_2: the judge scores view cam_r_L1_cocuk_odasi_2 2/5 (a client would not accept it): The room is bright and the camera is fine, but it does not read as a designed children's bedroom. The two beds are from
  - RECURRING judge:J1 cam_r_L1_cocuk_odasi_3: the judge scores view cam_r_L1_cocuk_odasi_3 2/5 (a client would not accept it): The room is a mess of placeholder geometry. The bed is a crude low-poly blob with a wireframe frame and a 'duvet' that 
  - RECURRING judge:J1 cam_r_L1_dus_1: the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The camera is pressed against the shower glass and a tiled wall, so the frame is mostly a blank corner; the actual room (basin,
  - judge:J1 cam_r_L1_ebeveyn_y_odasi_3: the judge scores view cam_r_L1_ebeveyn_y_odasi_3 2/5 (a client would not accept it): The room is lit and the bed is placed, but it is not client-ready. The two lounge chairs are different models and c
  - judge:J1 cam_r_L1_hol_1: the judge scores view cam_r_L1_hol_1 2/5 (a client would not accept it): The hall itself is a bare, empty corner: a plain door, a small stair landing and two windows, with no shoe cabinet, no decor an
  - RECURRING judge:J1 cam_r_L1_oda_1: the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): The render is a tight, tilted close-up of a corner that shows almost nothing of the room. The main piece, the shoe cabinet, is 
  - RECURRING judge:J1 cam_r_L1_oda_2_1: the judge scores view cam_r_L1_oda_2_1 2/5 (a client would not accept it): The room is coherent and the camera is fine, but the furniture is a mismatched, dated set that a client would not accept for 
  - RECURRING judge:J1 cam_r_L1_oda_2_2: the judge scores view cam_r_L1_oda_2_2 2/5 (a client would not accept it): The room itself is a plain, believable corner, but the render is not client-ready. The outdoor scene is a crude low-poly dior
  - RECURRING judge:J1 cam_r_L1_soyunma_odasi_1: the judge scores view cam_r_L1_soyunma_odasi_1 1/5 (a client would not accept it): The render is unusable for a client: it is a near-black, poorly lit close-up of a door and a wall corner, not a view 
  - judge:J1 cam_r_L1_soyunma_odasi_2: the judge scores view cam_r_L1_soyunma_odasi_2 1/5 (a client would not accept it): The render is unusable for a client presentation. The camera is pressed flat against a wall or cabinet face, so the f
  - rule proposed by Argus AI (1 run(s)): Fixture models must be finished and detailed, and must match the room's specified material palette; plain boxes or exposed services are not acceptable unless explicitly specified.
  - rule proposed by Argus AI (1 run(s)): Fixture models must conceal plumbing or use a specified exposed-service finish; unexplained exposed pipes or mismatched service materials are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be selected from a coherent style set and must match the room's material palette; generic boxes that do not coordinate with the room are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Doors in the same architectural set must have consistent leaf height, width, and style; mismatched door leaves are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Paired furniture must use the same model and finish; a bed-side nightstand pair must be a matched set.
  - rule proposed by Argus AI (1 run(s)): Paired furniture must use the same model and finish; mismatched nightstands are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be scaled and detailed appropriately for the room and adjacent pieces; flimsy or out-of-scale models are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Window models must include appropriate joinery or trim and must match the architectural style; plain untrimmed uPVC is not acceptable in a styled project.
  - rule proposed by Argus AI (1 run(s)): Stair models must use finished materials consistent with the surrounding floor and wall finishes; raw concrete or exposed voids are not acceptable unless specified.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be finished, not low-detail placeholders; crude slat or box models are not acceptable in a furnished render.
  - rule proposed by Argus AI (1 run(s)): Door frames must use a finish that is part of the room's specified material palette; unexplained third materials are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Exterior glazing frames must be proportionate and stylistically consistent with the facade; heavy industrial frames are not acceptable on a light residential facade.
  - rule proposed by Argus AI (1 run(s)): A camera for a room must frame the room's main functional group, not a blank wall or partition.
  - rule proposed by Argus AI (1 run(s)): Under a sloped ceiling, the furniture agent must select a bed model with a maximum height that fits the clearance; if no library model fits, the build stage must generate a parametric bed that respects the ceiling height.
  - rule proposed by Argus AI (1 run(s)): A camera for a room must frame the room's main functional group, not a door or wall corner.
  - rule proposed by Argus AI (1 run(s)): A camera for a room must frame the room's main functional group, not a wall or cabinet face.
  - rule proposed by Argus AI (1 run(s)): Exterior site items (trees, ground) must use high-quality, photorealistic assets, not low-poly placeholders.
  - rule proposed by Argus AI (1 run(s)): The render stage must ensure that all rooms are furnished and lit before rendering, or the agent must place furniture and set a camera for empty rooms.
  - rule proposed by Argus AI (1 run(s)): The scene stage must use high-quality tree models that match the realism of the render, or the agent must replace low-poly tree models with better ones.
  - rule proposed by Argus AI (1 run(s)): The site stage must replace the default low-poly placeholder landscape with a photorealistic environment (HDRI or high-poly vegetation) that matches the project's render quality target; a flat cartoon backdrop is never acceptable for a client-ready render.
  - rule proposed by Argus AI (1 run(s)): A room's primary camera must frame the room's main functional group (seating, dining, bed) and not a bare wall or a single stray piece; if the group is out of frame, re-aim the camera before judging the room's furnishing.
  - rule proposed by Argus AI (1 run(s)): Two pieces of the same type placed as a pair in one room must be the same model and finish; the fit stage must not leave two different armchair models side by side.
  - rule proposed by Argus AI (1 run(s)): A bathroom camera must frame the room's fixtures, not a blank wall or a window whose outdoor scene is a placeholder; if the only window shows a placeholder, aim the camera away from it.
  - rule proposed by Argus AI (1 run(s)): The site stage must build a real exterior (trees, ground, sky) from the project's exterior library; a low-poly placeholder landscape is never acceptable in a client render.
  - rule proposed by Argus AI (1 run(s)): A bathroom's washbasin must be placed inside the room (not in a door swing) and the room must carry its standard decor set (mirror, towel, soap, hardware); the fit stage must not leave a bathroom as a bare grey-box.
  - rule proposed by Argus AI (1 run(s)): A bedroom camera must frame the bed group and main furniture, not a window whose outdoor scene is a placeholder; if the only window shows a placeholder, aim the camera away from it.
  - rule proposed by Argus AI (1 run(s)): Two beds of the same type in one room must be the same model and scale; the fit stage must not leave two different bed models in one room, and a bed must not block a door.
  - rule proposed by Argus AI (1 run(s)): A dresser must be a real product model with visible drawer lines, texture and a top surface; the fit stage must not leave a plain box with floating dots for handles, and the model must fit under any sloped ceiling.
  - rule proposed by Argus AI (1 run(s)): A children's bedroom's bed and dresser must be real product models that match each other and the floor finish; the fit stage must not leave placeholder geometry (low-poly blob bed, plain box dresser) in a client render.
  - rule proposed by Argus AI (1 run(s)): A nightstand must be a real product model that matches the room's floor and furniture finish, and it must be placed against a wall (not floating 0.34 m off); the fit stage must not leave a plain box with a clashing wood tone.
  - rule proposed by Argus AI (1 run(s)): A shower/bathroom camera must frame the room's fixtures (shower, basin, toilet), not a blank corner or a window whose outdoor scene is a placeholder; if the only window shows a placeholder, aim the camera away from it.
  - rule proposed by Argus AI (1 run(s)): A shower/bathroom camera must frame the room's fixtures (shower, basin, toilet), not a blank corner; the camera must not be jammed against the shower glass and a tiled wall.
  - rule proposed by Argus AI (1 run(s)): An interior camera must be placed at a standing eye height (1.5 m) in the middle of the room, looking at the room's center, with a wide lens (24-28 mm) to show the whole space; it must never be pressed against a wall or piece.
  - rule proposed by Argus AI (1 run(s)): Every window in the building must be visible in at least one render (either an interior view looking out, or an exterior view showing the facade); if a window is not visible in any current camera, a new camera must be added or an existing one adjusted to include it.
  - rule proposed by Argus AI (1 run(s)): Exterior renders must use a realistic ground model (planar or tin) and site items (trees, shrubs) that match the project's style; crude 'lollipop' trees and flat untextured ground are not acceptable for client presentation.
  - rule proposed by Argus AI (1 run(s)): Doors are not furniture pieces and cannot be swapped using swap_model; their appearance is controlled by the door model library or material slots. If a door looks generic, the door model must be selected from the library during the building stage, or the material slot for doors must be set to a realistic finish.
  - rule proposed by Argus AI (1 run(s)): Window and door frames must have a material that contrasts with the facade and matches the project's style; generic flat grey frames are not acceptable for a stylish home.
  - rule proposed by Argus AI (1 run(s)): Exterior renders must use a realistic ground model (planar or tin); a flat untextured green plane is not acceptable for client presentation.
  - rule proposed by Argus AI (1 run(s)): Kitchen counters must have a realistic countertop material (e.g., quartz, granite) and handles; a plain untextured white box is not acceptable for client presentation.
  - rule proposed by Argus AI (1 run(s)): Furniture should be placed to create balanced compositions; a sideboard pushed into a corner with a large empty wall beside it is not acceptable.
  - rule proposed by Argus AI (1 run(s)): Armchairs should be part of a seating arrangement, not pushed flat against a wall under a window; they should be angled towards the center of the room or the coffee table.
  - rule proposed by Argus AI (1 run(s)): Kitchen fittings (sink, wall cabinets) should be built at the library level (with proper textures and details) rather than falling back to parametric meshes when no library model is available.
  - rule proposed by Argus AI (1 run(s)): Toilet models in the library should include seat covers and basic decor (e.g., spare toilet paper) to avoid a sterile, incomplete appearance in renders.
  - rule proposed by Argus AI (1 run(s)): Bathroom fixtures and tiles should be selected from a higher-quality library set to avoid a cheap, institutional look in renders.
  - rule proposed by Argus AI (1 run(s)): Bed models in the library should include more substantial headboards and frames to avoid a plain, low-profile appearance in client-ready renders.
  - rule proposed by Argus AI (1 run(s)): Nightstand models in the library should be more stylish and cohesive with the room's furniture set to avoid a generic, unstyled appearance.
  - rule proposed by Argus AI (1 run(s)): Door models in the library should include more detailed handles and finishes to avoid a cheap, generic appearance in stylish projects.
  - rule proposed by Argus AI (1 run(s)): A stair or landing that is the only vertical circulation of a level must be built with a full parametric stair model (treads, risers, stringers and a proper balustrade), never as a bare platform with a glass guard; a platform-only representation is a defect, not a style choice.
  - rule proposed by Argus AI (1 run(s)): Interior doors must be built with a styled door model (panelled or flush with a proper frame and handle) matching the project's finish, never as a plain flat slab; a generic slab door is a defect in a client presentation.
  - rule proposed by Argus AI (1 run(s)): A floor lamp must be built with a proper library model (a real lamp with a shade and stem), never as a low-poly box placeholder; a placeholder lamp is a defect.
  - rule proposed by Argus AI (1 run(s)): Exterior wall surfaces and plinths must be built with textured materials (stone, render, brick) matching the project's finish, never as untextured flat surfaces; bare material is a defect in a client presentation.
  - rule proposed by Argus AI (1 run(s)): A stone path or paving leading to an entrance must be built with a textured paving model, never as a rough untextured mesh with visible cracks; a placeholder path is a defect.
  - rule proposed by Argus AI (1 run(s)): A sofa placed under a sloped ceiling must be fitted to the ceiling clearance at its position (max height = ceiling - 0.05 m); the fit check must reject any model whose height exceeds that clearance before the swap is accepted, and the catalogue must offer at least one sofa variant per room whose height fits the minimum ceiling clearance of the room's sloped zone.
  - rule proposed by Argus AI (1 run(s)): Site trees must use high-poly, photorealistic models from the library (not low-poly lollipop placeholders); the site stage must select tree models that match the project's render quality standard, and the catalogue must include at least one photorealistic tree variant per tree type used in the project.
  - rule proposed by Argus AI (1 run(s)): The exterior landscape must use a realistic terrain and tree model (not low-poly placeholder blobs) so that views through doors and windows read as a real site, not a placeholder.
  - rule proposed by Argus AI (1 run(s)): The site stage must reject low-poly placeholder vegetation (lollipop/blob trees) and only place library models that match the project's photorealistic render standard; a placeholder asset must never be built into the scene.
  - rule proposed by Argus AI (1 run(s)): The furniture agent must select coffee table models that match the room's color palette (pale/muted tones) and avoid clashing wood tones like bright honey-oak when the floor is pale.
  - rule proposed by Argus AI (1 run(s)): The site stage must reject low-poly placeholder vegetation and only place library models that match the project's photorealistic render standard.
  - rule proposed by Argus AI (1 run(s)): Furniture models assigned to pieces in finished rooms must meet a minimum visual fidelity standard appropriate to the project's style; placeholder or low-detail models are prohibited.
  - rule proposed by Argus AI (1 run(s)): Bed groups in bedrooms should be symmetric (nightstand on both sides) unless spatial constraints explicitly prevent it; the layout solver must verify this symmetry during placement.
  - rule proposed by Argus AI (1 run(s)): Paired furniture items (like armchairs) must use the same model or a visually coherent set to ensure stylistic consistency.
  - rule proposed by Argus AI (1 run(s)): Floor lamps must be selected with a scale appropriate to the room's ceiling height and must not obstruct window views or door swings; models with oversized shades or incorrect proportions are prohibited.
  - rule proposed by Argus AI (1 run(s)): Exterior environments visible through windows must use realistic, high-fidelity assets; low-poly or placeholder trees and ground planes are prohibited in final renders.
  - rule proposed by Argus AI (1 run(s)): Entrance halls must be furnished with appropriate items (shoe cabinet, console, lighting) to avoid looking like bare shells; the furniture agent must verify that all halls have a minimum set of decorative and functional pieces.
  - rule proposed by Argus AI (1 run(s)): Staircases and railings must be selected from a catalogue of styled models that match the project's design language; generic or default placeholder models are prohibited.
  - rule proposed by Argus AI (1 run(s)): Interior cameras must be positioned to show the room's layout and key furniture, avoiding close-up corner shots that cut off main pieces.
  - rule proposed by Argus AI (1 run(s)): All doors must be modeled with frames and hardware (handles, hinges) to appear finished; flat slab doors without details are prohibited.
  - rule proposed by Argus AI (1 run(s)): Furniture within a room must be stylistically coherent; the furniture agent must ensure that major pieces (sofa, bench, etc.) share a common style or material palette.
  - rule proposed by Argus AI (1 run(s)): Lighting fixtures must match the room's style; the furniture agent must select lamps that are stylistically consistent with the other furniture in the room.
  - rule proposed by Argus AI (1 run(s)): Interior cameras must be positioned to show key architectural features like windows and daylight sources.
  - rule proposed by Argus AI (1 run(s)): Main entrance doors must be modeled with full detail (handles, texture, frame) and must match the house's exterior style; generic flat slabs are prohibited.
  - rule proposed by Argus AI (1 run(s)): Window and door frames must be colored to match or complement the facade; generic flat grey frames are prohibited if they clash with the building's color scheme.
  - rule proposed by Argus AI (1 run(s)): Ground surfaces must have texture and detail to avoid a 'video game' aesthetic; flat untextured planes are prohibited in final renders.
  - rule proposed by Argus AI (1 run(s)): An interior camera must be placed inside its room, at eye height 1.2-1.6 m, at least 0.6 m from any door, and aimed at the room's main furniture group, not a blank wall.
  - rule proposed by Argus AI (1 run(s)): Kitchen counters and wall cabinets must be built with textured, styled models that include integrated appliances (cooktop, sink) and finishes matching the project's style, not flat untextured white placeholders.
  - rule proposed by Argus AI (1 run(s)): Furniture in a living room must be selected from a cohesive set or style family; if a piece clashes with the main sofa and other seating, it must be swapped for a model that matches the room's established style.
  - rule proposed by Argus AI (1 run(s)): Furniture in a bedroom or living space must be selected from a cohesive set or style family; if a piece clashes with the room's color palette and style, it must be swapped for a model that matches.
  - rule proposed by Argus AI (1 run(s)): Furniture models must be high-quality, finished assets; low-poly placeholder boxes with grid textures are not acceptable for client presentation.
  - rule proposed by Argus AI (1 run(s)): Kitchen counters must be connected to walls or islands to form a coherent set; isolated bare slabs are not acceptable.
  - rule proposed by Argus AI (1 run(s)): Exterior renders must use high-quality landscaping models (trees, ground) and accurate architectural details; crude 'lollipop' trees and flat untextured ground are not acceptable for client presentation.
  - rule proposed by Argus AI (1 run(s)): Exterior views from interior windows must show a high-quality landscape, not crude low-poly 'lollipop' trees.
  - rule proposed by Argus AI (1 run(s)): A kitchen render must show its anchor appliances (cooktop, fridge, wall cabinets) and the exterior visible through its windows must use the project's site model, not a placeholder landscape.
  - rule proposed by Argus AI (1 run(s)): An interior camera must be placed inside its room, aimed at the room's main furniture group, with a lens that frames the whole group, not a blank wall.
  - rule proposed by Argus AI (1 run(s)): A living room (salon) must contain its main seating group (sofa, coffee table, armchairs) and a dining set; the exterior visible through its windows must use the project's site model.
  - rule proposed by Argus AI (1 run(s)): A bathroom render must show its fixtures and accessories, and the exterior visible through its windows must use the project's site model, not a placeholder landscape.
  - rule proposed by Argus AI (1 run(s)): Furniture in a room must be from a coherent collection (matching style and scale); the exterior visible through its windows must use the project's site model.
  - rule proposed by Argus AI (1 run(s)): A hall/entrance must contain its functional pieces (shoe cabinet, etc.) and decor; the exterior visible through its windows must use the project's site model.
  - rule proposed by Argus AI (1 run(s)): Every interior camera must be placed inside its room's clear volume (at least 0.5 m from any wall or piece) and aimed at the room's centre, so the render shows the room's function, not a wall or a door face.
  - rule proposed by Argus AI (1 run(s)): A sideboard or console must be centred on its wall span (or paired with a companion piece) so the composition is balanced, not pushed into a corner with a bare wall beside it.
  - rule proposed by Argus AI (1 run(s)): A single armchair must be placed as part of a seating group (facing the coffee table or sofa), not flat against a wall under a window.
  - rule proposed by Argus AI (1 run(s)): The exterior ground must carry a real ground material (grass, soil, paving) rather than a flat untextured plane.
  - rule proposed by Argus AI (1 run(s)): When the fitting stage falls back to a parametric mesh for a kitchen fitting because no library model matches, the run must record a library_gap warning so the library can be extended, rather than silently building a below-library-level mesh.
  - rule proposed by Argus AI (1 run(s)): When the fitting stage falls back to a parametric mesh for a wall cabinet because no library model matches, the run must record a library_gap warning so the library can be extended, rather than silently building a below-library-level mesh.
  - rule proposed by Argus AI (1 run(s)): Bathroom fixtures (tiles, basins, etc.) must use library models with appropriate textures and finishes for client-ready renders; when only plain parametric meshes are available, the run must flag a library_gap rather than ship an institutional-looking fixture.
  - rule proposed by Argus AI (1 run(s)): Bed models in the library must include a substantial headboard or frame for client-ready renders; a basic low-profile platform without styling is below the quality bar and should be flagged as a library_gap.
  - rule proposed by Argus AI (1 run(s)): Nightstand models in the library must have a cohesive, high-end design that matches the room's furniture set; a plain boxy design that looks identical to a basic first nightstand is below the quality bar and should be flagged as a library_gap.
  - rule proposed by Argus AI (1 run(s)): Door models in the library must include styled handles and finishes appropriate for a stylish project; a plain flat slab with a basic handle is below the quality bar for client-ready renders and should be flagged as a library_gap.
  - rule proposed by Argus AI (1 run(s)): Exterior plinths and facade wall surfaces must carry a material look (stone, render, brick) matching the project style; bare untextured surfaces are not acceptable for a client presentation.
  - rule proposed by Argus AI (1 run(s)): Site paving and paths must use a textured material model, not a rough untextured mesh, to avoid a placeholder look in renders.
- **geometry** (42 open, 0 with a fix; arises: layout, agent; guards: code critic (F*, G*), architect F-rules)
  - RECURRING process:P5 L0:S2: scene check S2 on L0: 1 of 23 failed
  - process:P5 L1:S2: scene check S2 on L1: 2 of 24 failed
  - process:P5 L1:S3: scene check S3 on L1: 1 of 22 failed
  - RECURRING inspector:G11 d_L0_004: the main walkway from the entrance door is below 0.80 m between doors d_L0_004 and d_L0_006
  - RECURRING inspector:G11 f_L0_016: armchair f_L0_016: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - RECURRING inspector:G11 f_L0_019: armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - RECURRING inspector:F3 f_L0_020: sink_kitchen: its back is not on a wall (0.08 m off)
  - RECURRING inspector:F9 f_L0_031: kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m²
  - inspector:F9 f_L0_032: kitchen_counter reaches 0.06 m² through the room outline, up to 0.025 m deep
  - RECURRING inspector:G11 d_L0_003: no 0.60 m walkway from door d_L0_003 to door d_L0_005
  - inspector:G11 f_L0_002: kitchen_counter f_L0_002: its front use zone is not reached by a 0.60 m walkway from door d_L0_003
  - inspector:F3 f_L0_010: bathtub: its back is not on a wall (0.02 m off)
  - RECURRING inspector:F3 f_L0_026: washbasin: its back is not on a wall (0.07 m off)
  - RECURRING inspector:F3 f_L1_012: bed_double: the headboard stands in the room (0.06 m off)
  - RECURRING inspector:F6 f_L1_018: armchair: the free zone in front of it is blocked by f_L1_022
  - inspector:G11 d_L1_002: the main walkway from the entrance door is below 0.80 m between doors d_L1_002 and d_L1_007
  - inspector:G11 d_L1_007: the main walkway from the entrance door is below 0.80 m between doors d_L1_007 and win_L1_003
  - RECURRING inspector:F3 f_L1_007: dresser: its back is not on a wall (0.06 m off)
  - RECURRING inspector:F7 f_L1_009: bed_double blocks door d_L1_011
  - RECURRING inspector:F9 f_L1_010: nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m²
  - RECURRING inspector:G5 f_L1_006: bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m
  - inspector:F7 f_L1_014: wardrobe blocks door win_L1_003
  - inspector:G11 d_L1_003: no 0.60 m walkway from door d_L1_003 to door win_L1_003
  - inspector:G11 f_L1_015: wardrobe f_L1_015: its front use zone is not reached by a 0.60 m walkway from door win_L1_003
  - RECURRING inspector:G11 d_L1_006: no 0.60 m walkway from door d_L1_006 to door d_L1_009
  - RECURRING inspector:G11 o_L1_002: no 0.60 m walkway from door o_L1_002 to door d_L1_009
  - RECURRING inspector:G12 f_L1_020: shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05)
  - RECURRING inspector:F6 f_L1_013: sofa: the free zone in front of it is blocked by f_L1_027
  - RECURRING inspector:G12 f_L1_027: floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05)
  - inspector:F3 f_L1_011: bathtub: its back is not on a wall (0.02 m off)
  - RECURRING inspector:F3 f_L1_025: washbasin: its back is not on a wall (0.07 m off)
  - inspector:G11 f_L1_021: washing_machine f_L1_021: its front use zone is not reached by a 0.60 m walkway from door d_L1_009
  - inspector:F9 f_L1_035: The desk is rendered as a floating slab with no legs or support structure, hovering in mid-air.
  - RECURRING inspector:F9 w_L0_001: The entire exterior environment is a placeholder. The flat, untextured ground, the grey sky, and the crude, low-poly trees are the biggest issue. This is not a believable setting for a client presenta
  - inspector:F9 w_L1_001: The surrounding site is a flat, featureless green plane with a hard horizon and a line of crude lollipop trees. This empty, artificial environment makes the house look like a model in a void rather th
  - inspector:F9 o_L0_001: Argus: The large opening in the wall is a raw, unframed hole with a floating horizontal bar, which looks like a broken model or a construction error rather than a designed feature.
  - inspector:Q6 r_L0_salon: Argus: The cream armchair is pushed flat against the wall under the window instead of being part of a seating arrangement; it looks staged, not designed.
  - rule proposed by Argus AI (1 run(s)): Scene checks must pass; if a check fails, the build stage must be re-run to fix the geometry.
  - rule proposed by Argus AI (1 run(s)): The exterior ground must be textured and realistic, not a flat, untextured plane.
  - rule proposed by Argus AI (1 run(s)): null
  - rule proposed by Argus AI (1 run(s)): A wet-room fixture that reads as floating or cut off at a wall edge must be re-placed against its host wall or counter in the next agent round when its model is pinned and cannot be swapped.
  - rule proposed by Argus AI (1 run(s)): A decorative accent that clashes with the room's stated palette and whose model is pinned must be replaced in the next agent round with a model that passes the room's height and fit caps.
  - rule proposed by Argus AI (1 run(s)): The exterior ground plane must carry a textured material (grass, soil, or paver) rather than a flat untextured colour, so it does not read as a default viewport floor.
  - rule proposed by Argus AI (1 run(s)): When two openings on the same wall are separated by less than 1.20 m, the layout engine must verify that the intervening wall span can accommodate a 0.60 m clear walkway; if not, it must propose moving one of the openings or adjusting the room layout to create the required clearance.
  - rule proposed by Argus AI (1 run(s)): When a bed's headboard is not flush against a wall (offset > 0.02 m), the layout engine must snap it to the nearest wall if the move is within 0.30 m, or flag it for manual review if the move exceeds the drawn-lock tolerance.
  - rule proposed by Argus AI (1 run(s)): When a piece blocks a door swing, the layout engine must move the piece to the nearest free position that does not intersect the door's swing arc, prioritizing positions along the wall opposite the door.
  - rule proposed by Argus AI (1 run(s)): When a piece blocks a window, the layout engine must move the piece to the nearest free position that does not obstruct the window's view or access, prioritizing positions along the wall opposite the window.
  - rule proposed by Argus AI (1 run(s)): When a door and a window on the same wall are separated by less than 1.20 m, the layout engine must verify that the intervening wall span can accommodate a 0.60 m clear walkway; if not, it must propose moving one of the openings or adjusting the room layout to create the required clearance.
  - rule proposed by Argus AI (1 run(s)): When a desk is rendered as a floating slab, the render engine must verify that the model includes legs or support structure; if not, it must swap to a model that includes them.
  - rule proposed by Argus AI (1 run(s)): A piece's free zone in front of it must not be blocked by another piece; the furniture agent must re-place the blocking piece or the piece itself to restore the clearance.
  - rule proposed by Argus AI (1 run(s)): The main walkway from the entrance door must be at least 0.80 m wide; the furniture agent must re-place pieces to widen the path.
  - rule proposed by Argus AI (1 run(s)): A dresser's back must be on a wall; the furniture agent must re-place it to snap to the wall.
  - rule proposed by Argus AI (1 run(s)): A nightstand must not overlap a bed; the furniture agent must re-place it to clear the collision.
  - rule proposed by Argus AI (1 run(s)): A bed must have at least 0.60 m of clearance on its sides; the furniture agent must re-place it to restore the clearance.
  - rule proposed by Argus AI (1 run(s)): A wardrobe's front use zone must be reachable by a 0.60 m walkway; the furniture agent must re-place it to restore access.
  - rule proposed by Argus AI (1 run(s)): A shower must not stand in front of a window; the furniture agent must re-place it to clear the opening.
  - rule proposed by Argus AI (1 run(s)): A sofa's free zone in front of it must not be blocked by another piece; the furniture agent must re-place the blocking piece or the sofa itself to restore the clearance.
  - rule proposed by Argus AI (1 run(s)): A floor lamp must not stand in front of a window; the furniture agent must re-place it to clear the opening.
  - rule proposed by Argus AI (1 run(s)): A bathtub's back must be on a wall; the furniture agent must re-place it to snap to the wall.
  - rule proposed by Argus AI (1 run(s)): A washbasin's back must be on a wall; the furniture agent must re-place it to snap to the wall.
  - rule proposed by Argus AI (1 run(s)): A washing machine's front use zone must be reachable by a 0.60 m walkway; the furniture agent must re-place it to restore access.
  - rule proposed by Argus AI (1 run(s)): The exterior environment must be believable for a client presentation; the site must include textured ground, a realistic sky, and high-poly trees.
  - rule proposed by Argus AI (1 run(s)): An opening must have a proper frame; the correct_geometry tool can fix the opening frame.
  - rule proposed by Argus AI (1 run(s)): none
  - rule proposed by Argus AI (1 run(s)): A decor item that penetrates its host by more than 0.03 m must be re-seated (or removed) in the next furniture round rather than left unbuilt.
  - rule proposed by Argus AI (1 run(s)): A washbasin must be anchored to a counter or wall (its base resting on a surface), never floating; if the model reads as a floating slab, re-seat it in the next round.
- **no_sense** (36 open, 16 with a fix; arises: architect, build; guards: sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*))
  - process:P3 F5:f_L0_010: the architect's question F5 (clashing furniture) is open for f_L0_010: f_L0_010 (bathtub) and f_L0_026 still overlap 0.33 m: no free place within the move limits
  - process:P3 F5:f_L0_026: the architect's question F5 (clashing furniture) is open for f_L0_026: f_L0_026 (washbasin) and f_L0_010 still overlap 0.33 m: no free place within the move limits
  - process:P3 F5:f_L1_011: the architect's question F5 (clashing furniture) is open for f_L1_011: f_L1_011 (bathtub) and f_L1_025 still overlap 0.25 m: no free place within the move limits
  - process:P3 F5:f_L1_025: the architect's question F5 (clashing furniture) is open for f_L1_025: f_L1_025 (washbasin) and f_L1_011 still overlap 0.25 m: no free place within the move limits
  - RECURRING inspector:X3 d_L1_001: door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_004: door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_005: door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_010: door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:Q3 f_L0_001: The staircase (f_L0_001) is completely open with no handrails or balustrades on either side, creating a significant fall risk.
  - inspector:Q1 o_L1_001: The balcony on the left is a floating slab with a railing but no visible support structure or door leading to it. It looks like a piece of the model was deleted or it is simply floating in the air.
  - inspector:Q8 w_L0_003: Argus: The downpipe on the corner is a simple black cylinder that looks like a placeholder. It lacks a proper gutter connection at the top and a splash block at the bottom.
  - RECURRING inspector:Q9 d_L0_001: The main entrance (d_L0_001) is barely legible: there is no clear door leaf, handle, canopy or step detail, and the small porch/landing is ambiguous. A client cannot tell where the front door actually
  - RECURRING inspector:Q2 f_L1_025: Argus: The washbasin sits too low and is wedged behind the toilet, so it is not at a usable working height and cannot be reached.
  - inspector:Q9 d_L1_009: Argus: The door opens directly into the basin/toilet cluster, blocking the approach to the fixtures.
  - RECURRING inspector:Q3 f_L1_001: Argus: The stair opening and landing edge have a flimsy, incomplete guard. The glass panel is a thin placeholder with a large open gap below it and no proper balustrade, which is a clear fall risk and
  - inspector:Q9 o_L0_002: Argus: The entrance area is poorly resolved. The steps and handrails are basic, untextured geometry. The large terrace slab to the left is a raw, floating concrete block with no finish, making the who
  - inspector:K2 d_L0_004: Argus: door d_L0_004 looks like something else in 1 view(s): cam_r_L0_salon_1 (seen as wall_art)
  - inspector:K3 f_L0_027: Argus: ottoman f_L0_027 differs from the drawing (tolerance 0.05 m): 0.86 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325]
  - inspector:K3 f_L0_028: Argus: ottoman f_L0_028 differs from the drawing (tolerance 0.05 m): 0.09 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325]
  - inspector:K3 f_L0_029: Argus: ottoman f_L0_029 differs from the drawing (tolerance 0.05 m): 0.63 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325]
  - inspector:K3 f_L0_030: Argus: ottoman f_L0_030 differs from the drawing (tolerance 0.05 m): 0.07 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325]
  - inspector:K3 f_L1_007: Argus: desk f_L1_007 differs from the drawing (tolerance 0.05 m): 0.15 m from its drawn place
  - rule proposed by Argus AI (1 run(s)): A hall/entry camera must frame the room's defining piece (shoe cabinet, stair) and its function, not a bare corner.
  - rule proposed by Argus AI (1 run(s)): A bathroom's wet fixtures (bathtub, washbasin, toilet) must not overlap; the fitter must find a non-clashing position before the run is accepted.
  - rule proposed by Argus AI (1 run(s)): No furniture may block the sightline or egress through a window opening.
  - rule proposed by Argus AI (1 run(s)): A labelled balcony/veranda must be built with its slab, railing, supports, and the door that accesses it; a floating slab with no access is a loss.
  - rule proposed by Argus AI (1 run(s)): A door on a balcony or veranda must be anchored in its frame and reach the floor of the space it opens to; a floating or mis-anchored door is a build error.
  - rule proposed by Argus AI (1 run(s)): A main entrance must have a legible door leaf, handle, and a clear approach (step, ramp, or canopy) so a client can identify and reach it.
  - rule proposed by Argus AI (1 run(s)): A dressing room (soyunma odası) adjacent to a bedroom must be typed as a bedroom/dressing room, not 'other', so its furniture set (wardrobe + mirror + seating) is validated and completed.
  - rule proposed by Argus AI (1 run(s)): A labelled veranda is a client-visible outdoor space; its absence from the model is a loss, not a good reason.
  - rule proposed by Argus AI (1 run(s)): A labelled balcony is a client-visible outdoor space; its absence from the model is a loss.
  - rule proposed by Argus AI (1 run(s)): A living room must hold a coherent furniture set (seating + table + anchor); a bare room with only a sofa and lamp is not acceptable.
  - rule proposed by Argus AI (1 run(s)): A labelled veranda, balcony or terrace in the documents must be built as a site area (floor slab, railing, and a door from the adjacent room) even when its outline is incomplete; an unbuildable outline is a reason to flag the drawing, not to silently drop the element.
  - rule proposed by Argus AI (1 run(s)): A room typed 'other' that the documents name as a dressing room (soyunma odası) must be furnished as a dressing room (mirror, bench or stool, wardrobe); the 'other' type must not suppress the completeness check for that room.
  - rule proposed by Argus AI (1 run(s)): A room typed 'living' must be furnished as a living room (seating plus a table and a focal point such as a TV or media unit); a sofa alone does not satisfy the type.
  - rule proposed by Argus AI (1 run(s)): Furniture must match the level it is placed on: a shoe cabinet belongs at the ground-floor entrance, not in an upper-floor hall, which should instead carry a console, coat hook or bench.
  - rule proposed by Argus AI (1 run(s)): Every open staircase (no solid wall on one or both sides) must be built with handrails and balustrades on all open sides to meet safety standards.
  - rule proposed by Argus AI (1 run(s)): A bathroom's wet fixtures (basin, toilet, tub/shower) must be placed so that no two overlap and each keeps its approach clearance; when the solver reports no free place, the room's layout must be re-solved before the run is accepted.
  - rule proposed by Argus AI (1 run(s)): No furniture may stand in the clear line of sight through a window or door opening; a piece that blocks an opening's ray must be moved out of the opening's path.
  - rule proposed by Argus AI (1 run(s)): A balcony or veranda slab drawn outside the outer walls must be built with its support structure (columns or cantilever) and a door from the interior; a slab with a railing but no support and no access door is an incomplete build and must not be left floating.
  - rule proposed by Argus AI (1 run(s)): A downpipe must be modelled with a gutter connection at its top and a splash block or drain at its base; a bare cylinder is a placeholder and is not an acceptable rain-water detail.
  - rule proposed by Argus AI (1 run(s)): The main entrance must be legible: a clear door leaf with handle, a canopy or header, and a defined step or landing; when steps already exist, the fix is to add the missing door-leaf/handle/canopy detail, not to re-set the entrance solution.
  - rule proposed by Argus AI (1 run(s)): Every interior camera of a room must frame the room's document openings (windows and doors); a camera that misses a required opening must be re-aimed to include it.
  - rule proposed by Argus AI (1 run(s)): A washbasin must be at a usable working height (rim ~0.85 m) and reachable; a generated placeholder model that is wedged behind another fixture must be replaced by a real product and re-placed in the room.
  - rule proposed by Argus AI (1 run(s)): A bathroom door must not open directly into the fixture cluster; the door swing and the fixtures' approach clearances must be resolved so the door does not block access to the basin or toilet.
  - rule proposed by Argus AI (1 run(s)): A stair opening and landing edge must have a complete guard (solid balustrade or glass with a proper handrail and no open gap below); a thin placeholder glass panel with a large open gap is a fall risk and is not an acceptable guard.
  - rule proposed by Argus AI (1 run(s)): The entrance approach (steps, handrails, terrace/landing slab) must be finished with proper materials and textures; raw, untextured concrete geometry and floating slabs are placeholders and are not an acceptable entrance finish.
  - rule proposed by Argus AI (1 run(s)): A door must be modelled as a door (leaf, frame, handle) and must not be rendered as a different object type (e.g. wall art); when a door is seen as another object in a camera view, the door model is wrong and must be corrected.
  - rule proposed by Argus AI (1 run(s)): A drawn piece must be built at its drawn size and position within tolerance (0.05 m); when the built size differs from the drawing, the piece must be resized to the drawn dimensions.
  - rule proposed by Argus AI (1 run(s)): fix_fixture must accept the string 'drawn' for center to snap a piece back to its documented footprint, or the inspector must emit the numeric drawn center so the tool can be called.
  - rule proposed by Argus AI (1 run(s)): set_camera must accept kind 'room' as an alias for 'interior' with a room_id, or the agent must be given the room's bounding box to compute a valid position/target.
  - rule proposed by Argus AI (1 run(s)): The furniture agent must add standard bathroom accessories (mirror, towel, soap, hardware) to every bathroom as part of its completion set, not just the fixtures.
  - rule proposed by Argus AI (1 run(s)): The furniture agent must add a dressing room set (bench, mirror, lighting) to every dressing room, not just a wardrobe.
  - rule proposed by Argus AI (1 run(s)): Labelled site areas (veranda, balcony, terrace) must be built with an outline, floor, and railing if the documents show them, not left as site records.
  - rule proposed by Argus AI (1 run(s)): A labelled outdoor area (veranda, balcony, terrace) in the documents must be built as a platform with a floor and a railing, even when the plan outline is faint; a 'no outline' reason is not a valid excuse to drop a labelled site area.
  - rule proposed by Argus AI (1 run(s)): A room typed as a dressing room or storage must be furnished with at least a mirror, a bench and a light source, and its render exposure must be within the cap; a single wardrobe in a dark box is not an acceptable dressing room.
  - rule proposed by Argus AI (1 run(s)): A room typed as living must be furnished with at least a sofa, a coffee table and a TV or media unit; a single sofa and lamp is not an acceptable living room.
  - rule proposed by Argus AI (1 run(s)): A hall or entrance room larger than 8 m2 must be furnished with at least a console, a mirror or a light fixture; a bare corridor with only a shoe cabinet and a stair is not an acceptable entrance hall.
  - rule proposed by Argus AI (1 run(s)): A bathroom camera must be positioned to show all fixtures with clearance; a camera jammed against the basin or toilet is not an acceptable bathroom view.
  - rule proposed by Argus AI (1 run(s)): A washing machine is not a typical bathroom fixture; it belongs in a utility or laundry area. A bathroom render must show all fixtures with clearance, not a cluttered corner.
  - rule proposed by Argus AI (1 run(s)): A master bedroom must not be furnished with an office set (desk + office chair); those belong in a study or office. A bedroom render must show the bed and the seating with clearance, not a cluttered office corner.
  - rule proposed by Argus AI (1 run(s)): A children's room larger than 15 m2 must be furnished with at least a bed, a desk, a chair and a rug; a single double bed, a dresser and a nightstand is not an acceptable children's room.
  - rule proposed by Argus AI (1 run(s)): A salon or living room larger than 30 m2 must be furnished with at least a sofa, a coffee table and a TV or media unit; a bare dining room with four identical armchairs is not an acceptable salon.
  - rule proposed by Argus AI (1 run(s)): A kitchen counter must have handles and material variation; a row of identical blank boxes is not an acceptable kitchen counter. A kitchen render must show the counter, the sink, the stove and the dining set with clearance, not a bare, unfinished box.
  - rule proposed by Argus AI (1 run(s)): A bathtub must have a shower head, a faucet and a bath mat; a bare bathtub is not an acceptable bathroom fixture. A bathroom render must show the bathtub, the toilet and the washbasin with clearance, not a bare, unfinished box.
  - rule proposed by Argus AI (1 run(s)): A door on an upper level must be reachable by a stair, a ramp or a balcony; a door 3.50 m above the ground with nothing to reach it is a door into the air and must not be built.
- **stale** (8 open, 8 with a fix; arises: agent loop, critics; guards: the critics read the building as built, conservation C2, consistency (Y*: the critic and the architect's rule disagree about one element))
  - rule proposed by Argus AI (1 run(s)): The architect's rule C1 must include a check for walkway widths (G11) to ensure that main walkways from entrance doors are at least 0.80 m wide, and flag any walkway that is below this threshold.
  - rule proposed by Argus AI (1 run(s)): The architect's rule F2 / F3 must include a check for furniture blocking doors (F7) to ensure that no furniture blocks a door's swing or walkway, and flag any furniture that does.
  - rule proposed by Argus AI (1 run(s)): The architect's rule E1 must include a check for doors that are too high to reach (X3) to ensure that all doors are at a reachable height (e.g., 0.90-2.10 m above the floor), and flag any door that is above this range.
  - rule proposed by Argus AI (1 run(s)): A rule that approves overlapping fixed counters must treat any overlap beyond the 0.03 m cut tolerance as a defect, not a pass.
  - rule proposed by Argus AI (1 run(s)): A clearance rule for wet rooms must check the free zone in front of bathtubs, washbasins and toilets against the minimum approach width, not only the sides.
  - rule proposed by Argus AI (1 run(s)): A seating rule must verify the free zone in front of each chair or sofa is unobstructed, not only that the piece fits its room.
  - rule proposed by Argus AI (1 run(s)): A window rule must flag any tall piece (above the sill height) placed in front of a window, not only pieces that fully cover the glazing.
- **other** (12 open, 5 with a fix; arises: -; guards: none)
  - inspector:NR f_L0_009: untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/crops/sym_L0_004_ctx.png)
  - RECURRING inspector:NR f_L1_002: untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built
  - inspector:NR f_L1_019: untyped drawn piece left for review: drawn piece 1.20 x 0.55 m in r_L1_oda_2 has no type (AI passes: desk, dresser); the documents name a dresser here ('*SIFONIYER' (TEXT:29ABD3), on the footprint): n
  - inspector:NR TEXT:29AC25: piece the documents name, not placed: the documents name a dresser ('*SIFONIYER' (TEXT:29AC25)) at (8.11, 4.91) m on L1 and no drawn dresser stands there: not added: the nearest place that passes ever
  - inspector:lighting_dark cam_r_L1_soyunma_odasi_1: cam_r_L1_soyunma_odasi_1: the metered exposure wanted +9.08 EV, the cap is +3.00 EV (6.08 stops over); the room is too dark for the camera (incident p50 0.00166 at target 0.9); the room needs about x6
  - inspector:lighting_dark cam_r_L1_soyunma_odasi_2: cam_r_L1_soyunma_odasi_2: the metered exposure wanted +9.33 EV, the cap is +3.00 EV (6.33 stops over); the room is too dark for the camera (incident p50 0.00140 at target 0.9); the room needs about x8
  - inspector:AI1 r_L1_soyunma_odasi: Argus: The L1 'Soyunma Odası' (dressing room) is typed 'other' and holds only a wardrobe. A dressing room is a bedroom-adjacent room; it should be typed as a bedroom/dressing room and furnished as a s
  - rule proposed by Argus AI (1 run(s)): For rooms with no windows or very small windows (e.g., dressing rooms, closets), the lighting system must be able to increase light by up to x10, or the camera exposure cap must be raised to +6.00 EV to allow proper exposure.
  - rule proposed by Argus AI (1 run(s)): Small drawn pieces (0.21 x 0.20 m) that the AI identifies as potted_plant should be typed as potted_plant, not left untyped.
  - rule proposed by Argus AI (1 run(s)): Clusters of drawn pieces larger than 4.5 m on a side should be marked as not furniture (a group) and not built as a single piece.
  - rule proposed by Argus AI (1 run(s)): If the documents name a dresser in a room, the piece should be typed as a dresser, even if the room is a living room.
  - rule proposed by Argus AI (1 run(s)): If the documents name a dresser at a specific location, the furniture agent must place it there, even if the nearest free place is more than 1 m away.
  - rule proposed by Argus AI (1 run(s)): A dressing room should be typed as 'dressing_room', not 'other', and furnished as a set (wardrobe + mirror + seating).
  - rule proposed by Argus AI (1 run(s)): When two pieces in the same room overlap and one is a drawn piece locked in a doorway, the movable piece must be re-placed to a free spot in the room, not the locked one.
  - rule proposed by Argus AI (1 run(s)): A small drawn piece that sits around a level-mark text (e.g. '+0,50') is a level-mark symbol, not furniture: the reading must mark it as a symbol so the fit stage never places it.
  - rule proposed by Argus AI (1 run(s)): A drawn piece that ends up standing in a doorway (outside the room outline) must be moved to the nearest free place in its room, clear of the door swing, rather than left overlapping a neighbour.
  - rule proposed by Argus AI (1 run(s)): A furniture piece that covers a window opening (door ray hits the furniture) must be moved to the nearest free place in its room, clear of the window.
  - rule proposed by Argus AI (1 run(s)): When a furniture label in the documents names a piece type that is not in the room's program and no drawn piece of that type exists within 1 m of the label, the label is treated as an annotation and not enforced as a missing piece.
- **lost** (38 open, 23 with a fix; arises: any stage boundary: reading -> building, fit, layout, build, render; guards: ledger (A*), conservation (C*), plan_vs_model (B*), process (P*))
  - conservation:C1 f_L1_030: furniture f_L1_030 (shoe_cabinet) of the decor stage is missing after the agent stage and nothing there names it
  - conservation:C1 f_L1_031: furniture f_L1_031 (desk) of the decor stage is missing after the agent stage and nothing there names it
  - conservation:C1 f_L1_032: furniture f_L1_032 (office_chair) of the decor stage is missing after the agent stage and nothing there names it
  - conservation:C3 f_L0_035: f_L0_035 (stove, furniture) is planned to be built but the scene has no object for it
  - conservation:C3 f_L0_039: f_L0_039 (fridge, furniture) is planned to be built but the scene has no object for it
  - inspector:A6 f_L1_019: Argus: the documents name a dresser ('*SIFONIYER') on L1; the model has f_L1_019 unknown (not built) within 1.2 m
  - inspector:C6 f_L1_001: Argus: not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001)
  - RECURRING ledger:A3 r_L0_mutfak:TEXT:294BCF: the documents name a space 'ANTRE m²' that is a second label of room r_L0_mutfak (Mutfak, kitchen): it is not a room of its own in the model
  - RECURRING ledger:A6 TEXT:29ABD3: the documents name a dresser ('*SIFONIYER') on L1; the model has f_L1_019 unknown (not built) within 1.2 m
  - rule proposed by Argus AI (1 run(s)): Pieces placed by the decor stage must be preserved by the agent stage; if a piece is missing, the agent must re-place it.
  - rule proposed by Argus AI (1 run(s)): A drawn cluster larger than 4.5 m on a side in a room must be split into individual pieces or marked as a single built-in element, not left untyped.
  - rule proposed by Argus AI (1 run(s)): Outdoor site areas like balconies and verandas must have their edges and steps built as part of the site model, even if the main outline is not built.
  - rule proposed by Argus AI (1 run(s)): The DWG reading stage must parse ATTDEF entities and expose their attribute values to the ledger, so that labelled spaces, areas, and annotations carried in block attributes are not silently dropped.
  - rule proposed by Argus AI (1 run(s)): When site decor symbols are read on multiple levels, the site stage must deduplicate them (keeping the ground-floor set) and flag any that are not used, rather than leaving 42 untyped symbols unplaced.
  - rule proposed by Argus AI (1 run(s)): When a room outline holds two labels (e.g. 'Salon' and 'YEMEK BÖLÜMÜ'), the reading stage must split the outline into two rooms so each labelled space is its own room in the model.
  - rule proposed by Argus AI (1 run(s)): The reading stage must associate printed area labels with their corresponding room outlines so that area checks can be run against the model.
  - rule proposed by Argus AI (1 run(s)): When walls are drawn as face lines on multiple layers, the reading stage must include all wall primitives that close the labelled rooms, not just those on the single chosen layer, to avoid missing wall segments.
  - rule proposed by Argus AI (1 run(s)): When the plan draws an object in a room that is not built in the model, the furniture stage must identify the object's type and place it in the next agent round.
  - rule proposed by Argus AI (1 run(s)): When a decor item's host piece is not built, the decor must be deferred to the next agent round, after the host is re-placed.
  - rule proposed by Argus AI (1 run(s)): Untyped drawn pieces must be typed by the reading stage before the build stage; the build stage must not silently drop untyped pieces without a record.
  - rule proposed by Argus AI (1 run(s)): A labelled outdoor area (veranda, balcony, terrace) in the documents must be built as a site platform with its drawn outline, even when the outline is open or partially defined; 'no outline' is not a valid reason to drop a labelled site area.
  - rule proposed by Argus AI (1 run(s)): A labelled outdoor space (veranda, balcony, terrace) that the documents outline or label must be built as a site platform with its own floor and guard, even when it has no enclosing walls; a 'no outline' reason is a loss, not a valid skip.
  - rule proposed by Argus AI (1 run(s)): The DWG reader must read ATTDEF (attribute definition) entities and map them to the block/label they define, so attribute text is not silently dropped from the ledger.
  - rule proposed by Argus AI (1 run(s)): Site decor read on an upper level must be placed on that level's site (or explicitly suppressed with a reason), not silently dropped because the site is modelled at the ground floor.
  - rule proposed by Argus AI (1 run(s)): When a room outline holds two labels, the reading must split it into two rooms at the label boundary rather than keeping one label as a second name of the other room.
  - rule proposed by Argus AI (1 run(s)): Every printed area label in the documents must be matched to its room and used in the area check, so a printed area is never silently lost.
  - rule proposed by Argus AI (1 run(s)): When walls are drawn as face lines, the reader must also consider wall primitives on runner-up layers (e.g. DUVAR) and off-layer primitives, not only the chosen layer, so no wall segment is left out.
  - rule proposed by Argus AI (1 run(s)): A drawn object in a room that the plan shows must be typed and built; if it cannot be typed, it must be recorded with evidence rather than silently dropped.
  - rule proposed by Argus AI (1 run(s)): The reading stage must assign a type to every drawn piece in a furnished room before the build stage; a piece that cannot be typed from its crop is flagged for review and never silently dropped as 'unknown'.
  - rule proposed by Argus AI (1 run(s)): The reading stage must type all drawn pieces before the build stage; the build must never skip a piece on the grounds that it is untyped, but instead route it to a review queue so the loss is visible.
  - rule proposed by Argus AI (1 run(s)): Untyped drawn pieces must be marked as not furniture with evidence, not left unhandled.
  - rule proposed by Argus AI (1 run(s)): Labelled site areas (veranda, balcony) with drawn outlines must be built as site elements, not left as records only.
  - rule proposed by Argus AI (1 run(s)): A labelled outdoor area (veranda, terrace, balcony) in the documents must be built as a site platform with its own outline, floor and railings, and must be listed in the site areas of the level it belongs to.
  - rule proposed by Argus AI (1 run(s)): A room typed 'living' must contain a sofa (or equivalent primary seating) in addition to any dining set; a living room with only armchairs is incomplete.
  - rule proposed by Argus AI (1 run(s)): A kitchen must have a continuous worktop with visible handles and material variation; a row of identical blank boxes is not an acceptable kitchen counter.
  - rule proposed by Argus AI (1 run(s)): A dressing room must have adequate lighting and at least two pieces of furniture (e.g., wardrobe + bench or mirror) to be functional.
  - rule proposed by Argus AI (1 run(s)): A door on an upper level must be reachable by a stair, lift, or walkway; a door floating above the ground with no access is a critical error.
  - rule proposed by Argus AI (1 run(s)): A staircase must have handrails or balustrades on at least one side; an open staircase with no railings is a safety hazard.
  - rule proposed by Argus AI (1 run(s)): Outdoor vegetation visible through windows must use high-quality models, not low-poly wireframe placeholders.
  - rule proposed by Argus AI (1 run(s)): Furniture wood tones must be consistent within a room; a third clashing wood tone is a design error.
  - rule proposed by Argus AI (1 run(s)): A salon should have varied seating (sofa + armchairs), not four identical chairs; and all seating must be reachable by a 0.60 m walkway from the room's door.
  - rule proposed by Argus AI (1 run(s)): All seating must be reachable by a 0.60 m walkway from the room's door.
  - rule proposed by Argus AI (1 run(s)): All kitchen work surfaces must be reachable by a 0.60 m walkway from the room's door.
  - rule proposed by Argus AI (1 run(s)): A main entrance door must have visible hardware (handle, frame, leaf) and be legible in renders; a flat white slab is not an acceptable entrance.
  - rule proposed by Argus AI (1 run(s)): All doors must be connected by a 0.60 m walkway; a door that is not reachable by a walkway is a circulation error.
- **silent** (12 open, 12 with a fix; arises: any stage; guards: process P2 (warnings that say something was left out))
  - rule proposed by Argus AI (1 run(s)): When a nightstand cannot be snapped to a wall due to doors/windows blocking all free places within 1.2 m, the fitting stage should allow a small offset (up to 0.10 m) from the wall or place it freestanding next to the bed, rather than refusing all moves.
  - rule proposed by Argus AI (1 run(s)): The agent must only use material look IDs that exist in the project's vocabulary; the vocabulary should be exposed to the agent in its context so it does not guess look names.
  - rule proposed by Argus AI (1 run(s)): The set_camera tool must accept 'room' as a valid kind for interior cameras; the schema should be updated to include 'room' as an option for kind.
  - rule proposed by Argus AI (1 run(s)): A drawn piece that is 0.06 m off the wall should be allowed to snap to the wall if the move is within 0.1 m; the drawn_lock rule should permit small adjustments for drawn pieces.
  - rule proposed by Argus AI (1 run(s)): A wardrobe that blocks a window should be moved to a free wall span; the clearance_ok rule should not refuse a move if the new position is clear of the window.
  - rule proposed by Argus AI (1 run(s)): A wardrobe whose front use zone is not reached by a 0.60 m walkway should be moved to a free wall span; the clearance_ok rule should not refuse a move if the new position is clear.
  - rule proposed by Argus AI (1 run(s)): An untyped drawn piece of 1.20 x 0.55 m in a living room should be retyped to a type that fits its size and room (e.g., sideboard or console); the retype_piece tool should allow this.
  - rule proposed by Argus AI (1 run(s)): A nightstand that reaches 0.06 m² through the room outline should be allowed to be moved to a free spot in the room; the inside_room rule should not refuse a move if the new position is inside the room.
  - rule proposed by Argus AI (1 run(s)): A coffee table that clashes with the room's wood tones should be swapped to a model that fits the room's palette; the swap_model tool should allow a model that passes the fit rules.
  - rule proposed by Argus AI (1 run(s)): When a nightstand's drawn position is 0.06 m off the wall and no free wall span exists within 1.2 m of the drawn place (blocked by doors/windows), the fit stage must accept the drawn position as-is rather than loop on refused moves.
  - rule proposed by Argus AI (1 run(s)): The agent must only propose facade material look-ids that exist in the project's material vocabulary; before calling set_material it must query the available looks and pick one from that list.
- **process** (10 open, 3 with a fix; arises: scheduler; guards: process (P*))
  - process:P4 test_refit_library_models_fit_the_style[real06]: test tests.gpu.test_furnish::test_refit_library_models_fit_the_style[real06] failure: AssertionError: real06: library models of another style or without a mattress: [('f_L0_007', 'abo_B072PZ4LQ2', ['m
  - RECURRING process:P8 run: the run ended 16 min before its deadline with 303 open major point(s): the time could have gone to more fix cycles
  - RECURRING process:P9 big_loop: the big loop did not raise the house score (first 26.3; 0 cycle(s); stop: cycle 1: no_edit)
  - inspector:P2 sym_L1_008: Argus: a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified
  - inspector:P2 r_L1_soyunma_odasi: Argus: a group the room should have found no place: r_L1_soyunma_odasi: completion added nothing, nothing fits: dressing: no place passes the checks
  - RECURRING render:K4 views: 4 view(s) marked for review: cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3
  - rule proposed by Argus AI (1 run(s)): The big loop must run enough cycles to raise the house score; stopping with 0 cycles and 147 open major points is a process failure.
  - rule proposed by Argus AI (1 run(s)): A bedroom camera must frame the bed and the room's primary function; a view marked for review indicates the framing is inadequate.
  - rule proposed by Argus AI (1 run(s)): When a section prints the ground floor at a non-zero datum (e.g. +0.50), the reading stage must detect the offset and re-anchor all relative level marks to the true ground floor (z=0) before any downstream stage uses them.
  - rule proposed by Argus AI (1 run(s)): When a document label names a piece type at a position where no piece stands, the fit stage must place that piece type in the room at the nearest valid spot, rather than leaving the label unverified.
  - rule proposed by Argus AI (1 run(s)): Furniture pieces must not overlap; the fit stage must resolve clashes by moving one piece to a valid spot within the room.
  - rule proposed by Argus AI (1 run(s)): Furniture must not block windows or doors; the fit stage must move pieces clear of openings.
  - rule proposed by Argus AI (1 run(s)): The set_camera tool must accept 'room' as a valid kind for interior views, or the agent must use 'interior' with correct position and target parameters to frame the room.
  - rule proposed by Argus AI (1 run(s)): When a bed's headboard is slightly off the wall (e.g., 0.06 m), the move_piece tool should allow a small snap correction to the wall if no other valid spot exists, or the fit stage should place the bed flush with the wall initially.
  - rule proposed by Argus AI (1 run(s)): When a wardrobe blocks a window, the move_piece tool should allow moving it to a different wall span if the current wall has no free space, or the fit stage should avoid placing wardrobes in front of windows.
  - rule proposed by Argus AI (1 run(s)): The place_group tool should have a valid 'dressing' group definition that can fit in a 5.9 m2 room, or the fit stage should place a wardrobe and mirror in the dressing room.
  - rule proposed by Argus AI (1 run(s)): When a wardrobe's front use zone is not reached by a 0.60 m walkway, the move_piece tool should allow moving it to a different wall span if the current wall has no free space, or the fit stage should ensure walkways are clear.
  - rule proposed by Argus AI (1 run(s)): When a drawn piece is untyped and the AI suggests a type (e.g., desk, dresser), the retype_piece tool should allow the type if it fits the size and room, or the fit stage should type the piece correctly.
  - rule proposed by Argus AI (1 run(s)): When a bed has only one nightstand but the schedule lists two, the move_piece tool should allow placing the second nightstand on the other side of the bed if space allows, or the fit stage should place both nightstands.
  - rule proposed by Argus AI (1 run(s)): The swap_model tool should have a catalogue model for a pale wood coffee table, or the fit stage should choose a model that matches the room's palette.
  - rule proposed by Argus AI (1 run(s)): When an elevation's openings cannot be checked against the plans because the north arrow is missing, the reading must infer the orientation from the plan's north arrow or the site context, and flag the elevation as 'orientation unverified' rather than skipping the check entirely.
  - rule proposed by Argus AI (1 run(s)): A drawn section whose ends do not align with the roof outline (offset > 0.30 m) or whose roof line is non-monotonic must be flagged as a non-corresponding section and excluded from point-by-point roof checks, rather than failing the check silently.
  - rule proposed by Argus AI (1 run(s)): Elevations without a view bearing or side must be assigned a default orientation based on their position relative to the plan, or flagged as uncheckable with a clear reason, rather than silently failing the comparison.
  - rule proposed by Argus AI (1 run(s)): The big loop must run at least 2 fix cycles when the initial score is below 30 and no cycle has been attempted.
  - rule proposed by Argus AI (1 run(s)): A sofa drawn in a bedroom is a reading error; the piece should be retyped to a type allowed in a bedroom (e.g., armchair or chaise) or removed if it does not fit the room's program.
  - rule proposed by Argus AI (1 run(s)): A dressing room (soyunma odasi) of 5.9 m² must have a dressing group (wardrobe, bench, mirror) placed; if no place passes the checks, the room type should be reconsidered or the room enlarged.
  - rule proposed by Argus AI (1 run(s)): A small drawn piece around a level mark text is a level-mark symbol, not furniture; it should be marked as not furniture.
  - rule proposed by Argus AI (1 run(s)): Cameras marked for review must be re-set with the correct kind (interior or exterior) and valid position/target.
  - rule proposed by Argus AI (1 run(s)): Elevation-to-plan opening checks require a north arrow (view bearing) on the elevation sheet; when the drawing has none, the check must be skipped with a recorded reason rather than left as an open failure.
  - rule proposed by Argus AI (1 run(s)): A drawn section whose ends do not run one-to-one with the plan (offset > 0.30 m) cannot be checked point-by-point against the roof; the check must be skipped with a recorded reason instead of forcing a mismatch.
  - rule proposed by Argus AI (1 run(s)): An elevation that has neither a view bearing nor a side label cannot be compared with the model; the render check must skip it with a recorded reason rather than report it as a failure.

## Warnings by rule

Every warning of the reading, the build and the site, matched to a rule (``process.WARN_RULES``); 'other' = no rule yet.

assumed 53, read_by 35, other 17, not_built 16, disagree 11, not_checked 5, no_model 3, outside_built 2, more_labels 2, no_label 2, not_read 1, not_allowed 1, not_used 1, nothing_fits 1, drawn_mismatch 1, not_rested 1

Warnings no rule knows yet (Argus AI reads each one; a new rule in ``process.WARN_RULES`` when one keeps coming):

- building frame: the outer wall faces of the reference r3 start (+3.161, +3.975) m from the sheets outline corner; every region and the sheets coordinates move with them
- levels: the ground floor (building z 0) is printed +0.50 in the section: every relative mark of the plans is read +0.50 m lower (one height frame)
- levels: f_L0_022 moved to symbols (sym_f_L0_022): a level-mark symbol, not furniture (a small drawn piece around a level mark text: '+0,50'); drawn as unknown 0.88 x 0.34 m
- TEXT:2772EB: furniture name text 'çamaşır mak.' on L1 at (7.98, 12.11) m in r_L1_banyo names a washing_machine
- TEXT:29ABD3: furniture name text '*SIFONIYER' on L1 at (1.08, 9.63) m in r_L1_oda_2 names a dresser
- TEXT:29AC0C: furniture name text '*SIFONIYER' on L1 at (0.81, 7.23) m in r_L1_cocuk_odasi names a dresser
- TEXT:29AC25: furniture name text '*SIFONIYER' on L1 at (8.11, 4.91) m in r_L1_ebeveyn_y_odasi names a dresser
- TEXT:295858: zone label 'YEMEK BÖLÜMÜ' in r_L0_salon: a dining zone (table_dining) of 15 corners around (1.81, 6.33) m
- f_L0_027: unknown -> chair by context: a 0.45 x 0.32 m seat 0.00 m from the table f_L0_011, facing it
- f_L0_028: unknown -> chair by context: a 0.45 x 0.32 m seat 0.00 m from the table f_L0_011, facing it
- f_L0_029: unknown -> chair by context: a 0.45 x 0.32 m seat 0.00 m from the table f_L0_011, facing it
- f_L0_030: unknown -> chair by context: a 0.45 x 0.32 m seat 0.00 m from the table f_L0_011, facing it
- TEXT:29AC25: the documents name a dresser ('*SIFONIYER' (TEXT:29AC25)) at (8.11, 4.91) m on L1 and no drawn dresser stands there: not added: the nearest place that passes every check in r_L1_ebeveyn_y_odasi is 1.47 m from the text (more than 1 m)
- r_L0_oda: no AI furniture, no groups for this room (hall 2.1 m²: nothing)
- furniture clash left: f_L0_010 and f_L0_026 overlap 0.33 m
- furniture clash left: f_L1_011 and f_L1_025 overlap 0.25 m
- win_L1_003: door ray hits furn_f_L1_014 (furniture); a furniture covers the opening
