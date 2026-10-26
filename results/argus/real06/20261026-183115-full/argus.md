# Argus: the audit of real06

Argus checks everything a run makes, not only the looks: what the documents hold against the model (nothing lost between stages, every label and symbol used), the run itself (stages, warnings nobody acted on, tests, time), the model's sense, the inspector's and the judge's findings. Every finding has a kind (where such problems arise and the guards that catch them), an owner (the stage that caused it) and, where the run can carry it out, a fix.

Score **7.4** / 100 (100 = nothing open; 10 points per critical, 3 per major, 0.5 per minor). Open: 27 critical, 109 major, 50 minor; 25 notes.

## Lines

| line | findings | checked | note |
|---|---|---|---|
| conservation | 27 | {"reading": 238, "fit": 238, "layout": 244, "decor": 244, "agent": 244, "final": 244, "build": 243} |  |
| process | 30 | {"stages": 27, "warnings": 147, "test_reports": 1, "missing_records": []} |  |
| model | 0 | {"M1": 14, "M2": 8, "M6": 54, "M7": 8, "M3": 0, "M4": 4, "M5": 7, "M8": 4} |  |
| inspector | 211 | {"round": 4, "seen": 145, "visitor": 77, "fixed": 1, "handed": 33, "open": 177, "dropped": 2, "architect_open": 1, "architect_open_major": 0, "model_checks": {" |  |
| judge | 173 | {"views": 34, "mean": 2.18} |  |
| sense | 0 | {"rooms": 12, "joins": 13, "reached": 12} |  |
| render_check | 11 | {"views": 34, "required_elements": 62, "drawn_pieces": 57, "elevations": 4} |  |
| ledger | 0 | {} | no source_items.json (the reading wrote no inventory) |

## Problem kinds

| kind | critical | major | minor | with a fix | owners | arises | guards |
|---|---|---|---|---|---|---|---|
| misread | 9 | 14 | 11 | 0 | building, scene, missing_member, fixture_clearance, wrong_type, empty_room | reading | plan_vs_model (B*), the room-sense rules (G*, R*), model review M7 |
| geometry | 7 | 28 | 12 | 0 | scene, build, collision, orientation, clearance, drawn_layout | layout, agent | code critic (F*, G*), architect F-rules |
| taste | 3 | 51 | 21 | 4 | building, scene, fit, drawn_layout, wrong_model, interior_camera | fit, decor, opening models | judge (J*), visitor checks Q5, Q7, the fit's matched sets |
| no_sense | 7 | 4 | 3 | 1 | scene, facade, wrong_model, guard, rain_water, entrance_layout | architect, build | sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*) |
| lost | 1 | 5 | 1 | 3 | agent, build, site, building, cameras, render | any stage boundary: reading -> building, fit, layout, build, render | ledger (A*), conservation (C*), plan_vs_model (B*), process (P*) |
| process | 0 | 4 | 2 | 2 | building, tests, scheduler, agent, check | scheduler | process (P*) |
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
| major | f_L0_033 | The 'wall cabinet' is rendered as a thin floating shelf with no doors or body, leaving the wall above the worktop empty. It does not read as storage and leaves the main run visually unfinished. | inspector:Q6, judge:Q6 | blocked_opening |  |
| major | f_L1_006 | bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m | inspector:G5, inspector:G11, inspector:D1, judge:D1 | clearance |  |
| major | f_L1_007 | desk: its back is not on a wall (0.06 m off) | inspector:F3, inspector:F9 | drawn_layout |  |
| major | f_L1_009 | bed_double f_L1_009: 0.10 m free along the left side, needs ≥ 0.60 m | inspector:G5, inspector:G11, inspector:D1, judge:D1 | clearance |  |
| major | f_L1_010 | nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m² | inspector:F9, inspector:G4 | collision |  |
| major | f_L1_013 | sofa: the free zone in front of it is blocked by f_L1_027 | inspector:F6 | clearance |  |
| major | f_L1_016 | The cushions on the grey sofa are broken: one pillow is a flat, crumpled sheet floating/sunk into the seat, and the others are misaligned and clipping. This is the most obvious defect in the frame. | inspector:D1, judge:D1 | decor_look |  |
| major | f_L1_018 | armchair: the free zone in front of it is blocked by f_L1_022 | inspector:F6 | clearance |  |
| major | f_L1_020 | shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05) | inspector:G12, inspector:Q6, judge:Q6 | blocked_opening |  |
| major | f_L1_025 | washbasin: its back is not on a wall (0.07 m off) | inspector:F3, inspector:Q6, judge:Q6 | off_wall |  |
| major | f_L1_027 | floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05) | inspector:G12, inspector:F9, judge:F9 | blocked_opening |  |
| major | o_L0_002 | The outdoor environment is completely empty and unconvincing. The 'garden' is a flat green texture, and the hedge is a simple, untextured box. There is no sense of place, scale, or landscaping, which is a major issue for an exterior presentation. | inspector:F9, judge:F9 | wrong_type |  |
| major | w_L0_001 | The entire environment is a 'flat outdoor' void. The ground is a single flat green texture with no horizon, no trees, and no context. This makes the house look like a toy in a vacuum and is embarrassing to show to a client. | inspector:F9, judge:F9 | wrong_type |  |
| minor | d_L1_002 | The walls are flat, untextured plaster with no skirting detail, art, lighting or hardware beyond the handle. The room looks like a grey-box stage rather than a styled interior. | inspector:F9, judge:F9 | wrong_type |  |
| minor | d_L1_003 | The door d_L1_003 on the right is cut off by the frame and shows only a sliver of leaf and handle, so the entrance reads as an accidental crop rather than a deliberate composition. | inspector:Q6, judge:Q6 | blocked_opening |  |
| minor | dec_L0_009 | decor that could not rest on its host: decor cushion dec_L0_009 on f_L0_008: not rested (67% of the footprint over the support < 80%); not built | process:P2, process:P5 | scene |  |
| minor | dec_L1_017 | decor that could not rest on its host: decor plant_small dec_L1_017 on f_L1_030: not rested (no top found on the built host (attempt 2)); not built | process:P2, process:P5 | scene |  |
| minor | f_L0_013 | The listed potted plant (f_L0_013) is not visible; the room lacks the softening greenery and decor a client would expect. | inspector:F9, judge:F9 | wrong_type |  |
| minor | f_L0_024 | Toilet is tucked into a tight corner niche with no clear approach space, making the layout feel cramped and poorly planned. | inspector:Q6, judge:Q6 | orientation |  |
| minor | f_L1_012 | The floral pillow on the bed looks like a flat texture pasted onto the surface rather than a soft, volumetric object. It lacks realistic depth and shadow. | inspector:D1, judge:D1 | decor_look |  |
| minor | f_L1_021 | The visible washbasin (f_L1_021) is a floating unit with no visible plumbing or support, which looks like a placeholder model rather than a finished installation. | inspector:F9, judge:F9 | floating |  |
| minor | f_L1_023 | The toilet f_L1_023 is a plain white box with no visible seat, lid, or flush plate, so it looks like a crude low-poly model rather than a real fixture. | inspector:Q6, judge:Q6 | orientation |  |
| minor | f_L1_024 | The toilet is pushed into the corner with almost no clearance to the basin, making the layout feel cramped and poorly planned. | inspector:Q6, judge:Q6 | orientation |  |
| minor | win_L1_006 | The windows at the end of the hall are very plain and the view outside is a flat, featureless sky. This contributes to the overall feeling of an unfinished, low-quality render. The window frames also look a bit thick and clunky. | inspector:F9, judge:F9 | wrong_type |  |
| minor | win_L1_007 | The view outside the window is a flat grey band with no horizon or context, which makes the render feel like a grey-box test rather than a real home. | inspector:F9, judge:F9 | wrong_type |  |

## lost: something the documents or an earlier stage hold is missing from the model (a labelled veranda, drawn site symbols, a room, an opening, a piece)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | sa_L0_veranda | the documents label a site area 'VERANDA' and the model does not build it (open balcony outside the outer walls (no walls drawn around it)) | conservation:C5 | site | build_outdoor_space |
| major | BALKON | a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'BALKON' at (9138484.48, 5090593.07) m lies outside the outer walls: an open balcony, recorded in site, not a room | process:P2 | building | build_outdoor_space |
| major | VERANDA | a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'VERANDA' at (9138464.73, 5090593.37) m lies outside the outer walls: an open balcony, recorded in site, not a room | process:P2 | building | build_outdoor_space |
| major | d_L0_004 | door d_L0_004 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L0_salon_1 | render:K1 | render |  |
| major | f_L0_012 | f_L0_012 (potted_plant) was to be built after the decor stage and is not built after the agent stage, with no reason | conservation:C2 | agent |  |
| major | site | items the reading found and no stage used: site: 2 cases, e.g. site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0) | process:P2 | building |  |
| minor | entity types not read | source entities the reading did not read (the ledger checks what they hold): real06.dwg: entity types not read: ATTDEF x28 | process:P2 | building |  |
| info | 2 elements | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 2: The recognition crop shows a drawn stair (tread lines with a central stringer and a landing), not furniture; the stair retype was rejected (doors_free/inside_room/windows_free), so it is recorded as a non-furniture symbol. (f_L1_014, f_L1_015) | conservation:C6 | build |  |
| info | 2 elements | not built: the model of f_L1_009 has its own cushions/pillows (dec_L1_009, dec_L1_010) | conservation:C6 | build |  |
| info | 42 elements | not built: site decor of kind 'other' is not built (no model) (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006, sd_L0_007, sd_L0_008 ...) | conservation:C6 | build |  |
| info | dec_L1_012 | not built: its host f_L1_010 is not built (dec_L1_012) | conservation:C6 | build |  |
| info | f_L0_002 | not built: architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once (f_L0_002) | conservation:C6 | build |  |
| info | f_L0_003 | not built: drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) (f_L0_003) | conservation:C6 | build |  |
| info | f_L0_004 | not built: the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png (f_L0_004) | conservation:C6 | build |  |
| info | f_L0_005 | not built: outline 3.89 x 1.65 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_005) | conservation:C6 | build |  |
| info | f_L0_006 | not built: outline 2.12 x 0.78 m around 1 other piece(s) (f_L0_009): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_006) | conservation:C6 | build |  |
| info | f_L0_009 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 3: The drawn 0.21x0.20 m symbol is a small scribble mark, not furniture (NR). (f_L0_009) | conservation:C6 | build |  |
| info | f_L0_010 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 1: The 2.54 x 1.01 m drawn outline is the dashed dimension/outline band around the washbasin and shower bay, not a furniture item. (f_L0_010) | conservation:C6 | build |  |
| info | f_L0_012 | not built: potted_plant: named by an AI pass and the only named type that fits the size (0.21 x 0.20 m), the living + other room and the position (others fitting: floor_lamp); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 2: Small drawn potted_plant blocks door d_L0_001 and move allowance is exhausted; removing it clears the blocked opening. (f_L0_012) | conservation:C6 | build |  |
| info | f_L0_014 | not built: outline 1.52 x 0.78 m around 2 other piece(s) (f_L0_012, f_L0_013): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) (f_L0_014) | conservation:C6 | build |  |
| info | f_L1_001 | not built: arrives from f_L0_001 (L0 -> L1): the drawn upper end of that stair; no level above, not built again (f_L1_001) | conservation:C6 | build |  |
| info | f_L1_002 | not built: cluster larger than 4.5 m on a side: a group of drawn pieces, not built (f_L1_002) | conservation:C6 | build |  |
| info | f_L1_003 | not built: 2.25 x 0.18 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_003) | conservation:C6 | build |  |
| info | f_L1_004 | not built: 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) (f_L1_004) | conservation:C6 | build |  |
| info | f_L1_008 | not built: drawn inside bed_double f_L1_006 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) (f_L1_008) | conservation:C6 | build |  |
| info | f_L1_010 | not built: architect F5: it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built (f_L1_010) | conservation:C6 | build |  |
| info | f_L1_011 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 1: The 2.42 x 0.98 m drawn symbol is the dashed outline enclosing the drawn washbasin and bathtub (a dimension/outline mark), not a separate piece of furniture; the code's size/zone table rejects bathtub and gives stair, which fits neither. (f_L1_011) | conservation:C6 | build |  |
| info | f_L1_019 | not built: untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (dimension_outline) by Qwen/Qwen3.8-27B-FP8, round 2: The recognition crop shows a plain rectangular outline sitting on the wall line with no furniture detail, a dimension/outline mark rather than a built piece. (f_L1_019) | conservation:C6 | build |  |
| info | f_L1_031 | not built: the answer to AI.remove_piece:f_L1_031: not built (f_L1_031) | conservation:C6 | build |  |
| info | o_L1_001 | o_L1_001 (opening) of the final stage is gone after the build stage, named in openings[38].evidence[3].text: one opening with o_L1_001 (read twice): 1.98 m wide | conservation:C1 | build |  |
| info | r_L0_oda | room Oda (2.1 m2) has no view: no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2) | process:P6 | cameras |  |
| info | sa_L0_veranda | not built: exterior label: its surface is built from site.paving / parking / grass (sa_L0_veranda) | conservation:C6 | build |  |

## misread: the reading typed, sized or placed something wrong (armchairs read as tables with chairs, a vanity read as a kitchen counter)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | f_L0_002 | The main counter run has no hob, cooktop or oven — a kitchen without its cooking anchor. The long worktop is empty and the wall above is bare, so the room does not function as a kitchen. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L0_024 | The toilet (f_L0_024) is completely missing from the room. A bathroom without a toilet is a fundamental failure. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L0_026 | Bathroom with no basin in frame: the washbasin (and shower) are not visible, so the room reads as a toilet closet rather than a complete bathroom. | inspector:G10, inspector:Q4, judge:Q4 | fixture_clearance |  |
| critical | f_L0_036 | The shower (f_L0_036) is missing. The room is listed as having a shower, but it is not visible in the render. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L1_020 | The shower (f_L1_020) is completely missing from the frame. A bathroom render that shows no shower, no toilet, and only a fragment of a basin reads as an empty, unfinished room. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L1_024 | The toilet (f_L1_024) is missing from the view. A bathroom render that shows no toilet or shower is not believable and fails the basic 'room makes sense' test. | inspector:G10, inspector:Q4, judge:Q4 | fixture_clearance |  |
| critical | f_L1_029 | Bathroom with no basin: the washbasin f_L1_029 is not visible anywhere in the frame, so the room is missing one of its three main pieces and reads as incomplete. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | f_L1_031 | The shower is listed for this bathroom but is not present in the render, so the room is missing one of its main fixtures and reads as an empty box. | inspector:Q4, judge:Q4 | wrong_type |  |
| critical | r_L1_soyunma_odasi | A dressing room (soyunma odası) with no furniture at all: no wardrobe, no bench, no mirror, no lighting. The room's entire purpose is missing, so it reads as an empty shell. | inspector:Q4, judge:Q4 | empty_room |  |
| major | derived ridge # m vs the drawn ridge height # m (# cm) | the model differs from the drawn section or elevation: derived ridge 8.530 m vs the drawn ridge height 7.770 m (+76 cm): the pitches are kept | process:P2 | scene |  |
| major | f_L0_015 | Room makes no sense as a finished salon: the listed coffee tables (f_L0_015, f_L0_021) and most armchairs are absent, leaving a 55 m2 living room that looks empty and incomplete. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L0_020 | The only sink is on a separate counter at the right edge, disconnected from the main run, so the primary work zone has no sink or tap and the layout does not read as a coherent kitchen. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L0_031 | The main worktop run has no hob or cooktop. A kitchen without a place to cook is a clear gap a client will point out immediately. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L0_033 | The wall_cabinet pieces are not visible above the main run, leaving a large empty wall and reinforcing the impression of an unfinished, incomplete kitchen. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L1_017 | The armchair (and its twin f_L1_018) is listed for this room but absent from the render, so the bedroom is missing a key piece and looks under-furnished. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L1_021 | washbasin f_L1_021: 0.11 m clear in front, needs ≥ 0.53 m | inspector:G10 | fixture_clearance |  |
| major | f_L1_022 | The floor lamp is in the room's furniture set but not present, leaving the corner by the bed bare and the room feeling empty. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L1_025 | washbasin f_L1_025: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m | inspector:G10, inspector:Q4, judge:Q4 | fixture_clearance |  |
| major | f_L1_027 | The floor lamp is listed for this room but is missing from the render, leaving the corner empty and the room feeling incomplete. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | f_L1_030 | The hall is essentially empty: the shoe cabinet is a tiny bench-like piece tucked into the corner, leaving the whole room bare. A 3.1 m2 entrance hall needs a proper anchor (full-height shoe cabinet, console, mirror) to feel designed. | inspector:Q4, judge:Q4 | wrong_type |  |
| major | r_L0_mutfak | kitchen r_L0_mutfak has no fridge (fridge) | inspector:G9 | missing_member |  |
| major | r_L1_hol | The hall is completely empty. There is no console table, no art, no lighting fixture, and no other decor to make it feel like a finished, stylish home. It looks like an unfinished construction site, not a client-ready render. | inspector:Q4, judge:Q4 | empty_room |  |
| major | roof vs the drawn section at s # m | the model differs from the drawn section or elevation: roof vs the drawn section at s # m: 11 cases, e.g. roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm) | process:P2 | scene |  |
| minor | d_L0_002 | window d_L0_002 looks like something else in 1 view(s): cam_r_L0_mutfak_1 (seen as other_object) | render:K2 | fit |  |
| minor | f_L0_013 | potted_plant f_L0_013 differs from the drawing (tolerance 0.05 m): 0.29 m from its drawn place | render:K3 | layout |  |
| minor | f_L0_027 | ottoman f_L0_027 differs from the drawing (tolerance 0.05 m): 0.86 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325] | render:K3 | layout |  |
| minor | f_L0_028 | ottoman f_L0_028 differs from the drawing (tolerance 0.05 m): 0.09 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325] | render:K3 | layout |  |
| minor | f_L0_029 | ottoman f_L0_029 differs from the drawing (tolerance 0.05 m): 0.63 m from its drawn place; size [0.5, 0.5] vs drawn [0.447, 0.325] | render:K3 | layout |  |
| minor | f_L0_030 | ottoman f_L0_030 differs from the drawing (tolerance 0.05 m): 0.07 m from its drawn place; size [0.5, 0.5] vs drawn [0.446, 0.325] | render:K3 | layout |  |
| minor | f_L1_007 | desk f_L1_007 differs from the drawing (tolerance 0.05 m): 0.15 m from its drawn place | render:K3 | layout |  |
| minor | f_L1_010 | The listed nightstand is not visible in the render; the bed stands alone with no bedside furniture, leaving the room incomplete. | inspector:Q4, judge:Q4 | wrong_type |  |
| minor | f_L1_016 | sofa f_L1_016 differs from the drawing (tolerance 0.05 m): 0.05 m from its drawn place | render:K3 | layout |  |
| minor | room '...' has more labels | one room outline holds the labels of two rooms (a wall not read?): room '...' has more labels: 2 cases, e.g. L0: room 'Salon' has more labels: YEMEK BÖLÜMÜ; the label with the largest printed area (else the first) kept | process:P2 | building |  |
| minor | sym_L1_008 | a piece whose type the room does not allow, kept unverified: sym_L1_008: sofa is not a type allowed in a bedroom room: kept, unverified | process:P2 | building |  |

## no_sense: the model makes no sense to a visitor (a door into the air, a basin at knee height, stairs running into each other, a railing across a door)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | d_L1_001 | door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_004 | door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2, inspector:Q1, judge:Q1 | facade |  |
| critical | d_L1_005 | door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_007 | door d_L1_007 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_010 | door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | d_L1_011 | door d_L1_011 is 3.50 m above the ground with nothing to reach it (a door into the air) | inspector:X3, inspector:L2 | facade |  |
| critical | f_L1_001 | The railing is placed on the landing floor, but the stair opening is on the other side of the wall. This is a fall risk and makes no sense; the guard is not protecting the actual edge. | inspector:Q3, inspector:Q9, judge:Q3, judge:Q9 | guard |  |
| major | d_L0_001 | The entrance area is a mess. There are railings on both sides of the steps that do not connect to anything and block the path, and the steps themselves look like a crude placeholder. A client would immediately ask why the handrails are floating and why the approach is so difficult. | inspector:Q9, judge:Q9 | entrance_layout |  |
| major | f_L0_026 | The washbasin (f_L0_026) appears to be installed at a height that is too low, closer to knee level than the standard hip height of ~0.85m. | inspector:Q2, judge:Q2 | wrong_model |  |
| major | f_L1_025 | The washbasin sits too low and is crammed against the toilet with exposed pipework and no vanity or mirror, so the wet zone looks broken and unusable. | inspector:Q2, judge:Q2 | wrong_model |  |
| major | o_L0_001 | an opening of the documents is not cut through its wall: o_L0_001: door ray hits splashback_r_L0_mutfak (splashback); the opening is not cut through its wall | process:P2, process:P5 | scene | clear_opening |
| minor | o_L0_002 | The downpipe (o_L0_002) is placed in the middle of the corner, not at the corner itself. It looks like it was placed arbitrarily and doesn't follow the roofline logic, making the drainage look illogical. | inspector:Q8, judge:Q8 | rain_water |  |
| minor | w_L0_001 | The downpipe runs straight down the corner and the gutter line is a simple black strip. There is no connection detail at the roof edge, making the rainwater system look like a crude line drawn on the model. | inspector:Q8, judge:Q8 | rain_water |  |
| minor | w_L1_001 | The downpipe runs straight down the corner and visually crosses in front of the window line on the right facade, making the gutter/pipework look like an afterthought rather than integrated. | inspector:Q8, judge:Q8 | rain_water |  |

## other: not classified yet: a new kind to name

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | f_L1_002 | untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | inspector:NR | untyped |  |

## process: the run itself: a stage failed or was skipped, a test failed, time was left unused, a question stayed unanswered

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | big_loop | the big loop did not raise the house score (first 31.84; 1 cycle(s); stop: cycle 1: no gain (under 0.5)) | process:P9 | agent | more_cycles |
| major | run | the run ended 32 min before its deadline with 147 open major point(s): the time could have gone to more fix cycles | process:P8 | scheduler | more_cycles |
| major | test_sky_and_window_pulls_reach_their_targets[real06] | test tests.gpu.test_render::test_sky_and_window_pulls_reach_their_targets[real06] failure: AssertionError: real06: [('window panes', 'median pane saturation 0.0631 under 0.065: grey cards, not the sky', [('cam_r_L0_banyo_1', 0.0612), ('cam_r_L0_banyo_3', 0.0972), ('cam_r_L0_mutfak_1', 0.0673), ('cam_r_L0_mutfak_3', 0.0631), ('cam_r_L0_salon_1', 0.0288), ('cam_r_L0_salon_2', 0.0588), ('cam_r_L0_sal | process:P4 | tests |  |
| major | views | 2 view(s) marked for review: cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3 | render:K4 | check |  |
| minor | elevation r# (all) | a check that could not run: elevation r# (all): 4 cases, e.g. elevation r1 (all): its openings are not checked against the plans (the side needs the north arrow) | process:P2 | building |  |
| minor | elevations | 4 elevation(s) could not be compared with the model (r1, r2, r7, r8): the elevation has neither a view bearing nor a side: nothing to compare | render:K4 | check |  |

## silent: a stage noted a problem in a warning and nothing acted on it

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | inferred trees | a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 67, front 27; most by window; the first pass placed 0, the second pass with the window band narrowed to 4 m added 0) | process:P2 | scene |  |

## taste: the house does not look designed (pieces that do not match, plain or dated rooms, a garage door look)

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| critical | f_L1_009 | The bedding on this bed is a crude, low-poly blob. It does not look like a duvet or pillows; it looks like a melted, untextured mass draped over the frame. | inspector:D3, inspector:D2, judge:D3, judge:D2 | wrong_model |  |
| critical | f_L1_013 | The white sofa is a crude low-poly / blocky placeholder (flat faceted surfaces, no fabric or cushion detail). It reads as a grey-box model, not a real sofa. | inspector:D2, inspector:Q5, inspector:V1, inspector:D3, judge:D2, judge:Q5, judge:V1, judge:D3 | wrong_model |  |
| critical | f_L1_017 | The two armchairs are a mismatched set. f_L1_017 is a low-poly, faceted chair in a pinkish tone, while f_L1_018 is a smooth, classic 'Egg' chair in brown. They are different models, styles, and colors, which is a major design flaw. | inspector:Q5, inspector:D2, judge:Q5, judge:D2 | wrong_type |  |
| major | cam_r_L0_banyo_1 | the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The render is not client-ready. It shows a nearly empty bathroom where the main fixtures are missing, and the camera is poorly framed, wasting most of the image on a blank wall. | judge:J1 | agent |  |
| major | cam_r_L0_banyo_2 | the judge scores view cam_r_L0_banyo_2 2/5 (a client would not accept it): The render is a dead-end corner: a toilet squeezed into a niche and a door that fills the right half of the frame. The room's main pieces (basin, shower) are not in view, so it reads as an unfinished toilet closet, not a 6.7 m2 bathroom. The wood door is a plain slab that clashes with the all-white tile scheme, and the came | judge:J1 | agent |  |
| major | cam_r_L0_banyo_3 | the judge scores view cam_r_L0_banyo_3 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation. The camera is poorly placed, the outdoor view is a flat void, and the room lacks any styling or texture, making it look like a raw grey-box model rather than a finished bathroom. | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_1 | the judge scores view cam_r_L0_mutfak_1 2/5 (a client would not accept it): The kitchen reads as a grey-box placeholder, not a finished project. The main run is a long, handle-less white slab with a dark plinth and a floating shelf, but there is no hob, no oven, no cooktop, and no upper cabinets above the worktop — a kitchen without its cooking anchor. The sink unit on the right is a separate, tal | judge:J1 | agent |  |
| major | cam_r_L0_mutfak_2 | the judge scores view cam_r_L0_mutfak_2 2/5 (a client would not accept it): The kitchen reads as a shell, not a finished, stylish space. The main run is a bare base cabinet with an empty worktop: no hob, no sink, no tap, no small appliances, no upper cabinets above it, and no decor. The only sink visible is on a separate counter at the right edge, so the primary work zone is incomplete. The walls  | judge:J1 | agent |  |
| major | cam_r_L0_salon_1 | Bad camera: a blank column/wall fills the center of the frame and the main seating group is off to the side, so the room reads as empty and the composition is unbalanced. | inspector:V1, judge:J1, judge:V1 | interior_camera |  |
| major | cam_r_L0_salon_2 | the judge scores view cam_r_L0_salon_2 2/5 (a client would not accept it): The room is a 55 m2 shell with no anchor: the corner sofa is pushed into a far corner and the four armchairs are scattered in two unrelated pairs, so the space reads as an empty showroom rather than a designed salon. The furniture is a mismatched set (a beige sofa, a tan armchair, and two dark-brown armchairs of different m | judge:J1 | agent |  |
| major | cam_r_L1_banyo_1 | the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The render is a near-empty white box: the shower (f_L1_031) is missing entirely, the basin is a crude black box, and the room has no decor, so it reads as a grey-box placeholder rather than a finished bathroom. | judge:J1 | agent |  |
| major | cam_r_L1_banyo_2 | the judge scores view cam_r_L1_banyo_2 2/5 (a client would not accept it): The render is a plain, unfinished-looking bathroom that a client would not accept. The most serious issue is that the shower (f_L1_031) is completely absent: the large tiled wall on the right is just an empty, featureless surface where a shower enclosure, glass panel or at least a drain and controls should be. The washbasin | judge:J1 | agent |  |
| major | cam_r_L1_banyo_3 | the judge scores view cam_r_L1_banyo_3 1/5 (a client would not accept it): The render is a near-empty corner of the bathroom. The camera is pointed at a blank tiled wall and the door, so the main fixtures (toilet, shower, second basin) are completely out of frame. The room reads as unfinished and absurd for a client presentation. | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_1 | the judge scores view cam_r_L1_cocuk_odasi_1 2/5 (a client would not accept it): A client would not accept this as a finished children's room. The two beds are from completely different design languages (a white ornate metal frame vs. a plain modern box), the walls are bare, untextured plaster, and the desk looks like a placeholder. It reads as a grey-box stage set, not a stylish home. | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_2 | the judge scores view cam_r_L1_cocuk_odasi_2 2/5 (a client would not accept it): The room fails on believability and style. The furniture is a clash of placeholder models: a white metal 'hospital' bed (f_L1_009) next to a white metal 'nursery' bed (f_L1_006), with a generic mid-century desk (f_L1_007) that fits neither. The bedding on f_L1_009 is a crude, low-poly blob that looks like a melted she | judge:J1 | agent |  |
| major | cam_r_L1_cocuk_odasi_3 | the judge scores view cam_r_L1_cocuk_odasi_3 2/5 (a client would not accept it): The room is a bedroom, but the furniture is a mismatched, dated set that does not read as a designed children's room. The white ornate metal bed (f_L1_006) is a classic/antique piece that clashes with the modern mid-century desk (f_L1_007) and the plain light-oak floor and bare plaster walls. The result looks like a p | judge:J1 | agent |  |
| major | cam_r_L1_dus_1 | the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation for a 4.5 m2 bathroom. The most serious issue is that the washbasin (f_L1_029) is completely absent from the frame, so the room reads as a toilet-and-shower box rather than a finished bathroom. Everything else is flat white tile with no vanity, mirror, towel,  | judge:J1 | agent |  |
| major | cam_r_L1_dus_2 | the judge scores view cam_r_L1_dus_2 2/5 (a client would not accept it): The render is a dead-end view of a tiled corner and a door; the shower (the room's namesake) is not in frame, and the visible washbasin is a crude, floating white blob. The client would see an unfinished, empty bathroom. | judge:J1 | agent |  |
| major | cam_r_L1_ebeveyn_y_odasi_1 | the judge scores view cam_r_L1_ebeveyn_y_odasi_1 2/5 (a client would not accept it): The render is a believable, clean bedroom, but it is not the bedroom the client booked. The furniture list for this room includes two armchairs and a floor lamp, and none of them are in the image; the room reads as half-furnished and plain. The two visible doors are also a mismatch: one is a tall, full-height slab | judge:J1 | agent |  |
| major | cam_r_L1_ebeveyn_y_odasi_2 | the judge scores view cam_r_L1_ebeveyn_y_odasi_2 2/5 (a client would not accept it): The room fails on basic coherence. The two armchairs are different models and colors, which is a glaring design error. The bed is cropped out of frame, making the render useless for showing the main piece. The walls are flat, untextured plaster, and the overall look is cheap and unfinished. | judge:J1 | agent |  |
| major | cam_r_L1_hol_2 | the judge scores view cam_r_L1_hol_2 2/5 (a client would not accept it): The render is a grey-box style view of a landing, but it has a serious logic error that a client would immediately point out. The main issue is the railing: it is placed on the landing floor, but the opening it is supposed to guard is on the other side of the wall, making the railing useless and confusing. The overall look is | judge:J1 | agent |  |
| major | cam_r_L1_hol_3 | the judge scores view cam_r_L1_hol_3 2/5 (a client would not accept it): The render is a confusing, low-value shot of a hall. The camera is placed at the top of the stairs looking down, but the framing is dominated by a glass railing that blocks the view of the room. The space itself is empty and unfinished, with bare plaster walls and no furniture or decor to suggest a finished home. The most gla | judge:J1 | agent |  |
| major | cam_r_L1_oda_1 | the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): A 3.1 m2 hall rendered as a bare corridor: the camera is aimed straight at the door leaf, the walls are flat and untextured, and the only furniture is a small bench shoved into the corner. It reads as an unfinished shell, not a designed entrance. | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_1 | the judge scores view cam_r_L1_oda_2_1 2/5 (a client would not accept it): The room is unshowable: the main seating is a blocky white placeholder, the two sofas are mismatched, and the cushions on the grey sofa are broken geometry. The harsh, blown-out light patches make it look like a test render, not a finished interior. | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_2 | the judge scores view cam_r_L1_oda_2_2 2/5 (a client would not accept it): The room is lit and the camera is fine, but the furniture set is incoherent and the decor is broken. The two sofas are completely different models and colours (a clean white box sofa vs. a grey slipcovered sofa), which reads as a mistake, not a design choice. On the grey sofa, the white pillows and the folded throw are floa | judge:J1 | agent |  |
| major | cam_r_L1_oda_2_3 | the judge scores view cam_r_L1_oda_2_3 2/5 (a client would not accept it): The room reads as a grey-box placeholder, not a finished living room. The main seating is a blocky, untextured white slab (f_L1_016) that looks like a 3D primitive, and it clashes with the grey armchair (f_L1_013). The listed floor lamp is missing, leaving the large left wall completely bare and the space feeling empty and  | judge:J1 | agent |  |
| major | cam_r_L1_soyunma_odasi_1 | Camera is pressed into the corner between the door and the wall; the frame is dominated by a door leaf and a blank wall instead of showing the room as a space. There is no main group to frame because none exists. | inspector:V1, judge:J1, judge:V1 | interior_camera |  |
| major | d_L0_001 | The entrance door is a plain flat slab with no handle, hardware or frame detail, and it sits in a recessed porch with a small canopy that does not read as a designed entry. It looks unfinished and cheap for a client presentation. | inspector:Q7, judge:Q7 | opening_style |  |
| major | d_L0_007 | Bad camera: the door leaf fills the entire right half of the frame and the view is a corner, so the room's main group is not shown. | inspector:V1, inspector:Q7, judge:V1, judge:Q7 | interior_camera |  |
| major | d_L1_002 | The camera is aimed dead-on at the door, so the leaf and frame fill the frame and the room itself is not shown. This is a bad camera angle for a client view. | inspector:V1, judge:V1 | interior_camera |  |
| major | d_L1_003 | The camera is poorly placed, pointing at a corner and a door leaf (d_L1_003) that fills the center of the frame. It fails to show the room's main group or its layout. | inspector:V1, inspector:Q7, judge:V1, judge:Q7 | interior_camera |  |
| major | d_L1_004 | The door is a plain, flat wood slab with a basic handle. It looks like a placeholder and does not match the style of a well-designed home. It also appears to be floating slightly above the floor. | inspector:Q7, judge:Q7 | opening_style |  |
| major | d_L1_009 | The door is a flat raw-wood slab with no frame and a visible gap at the floor; it does not match the modern white tile scheme and reads as an unfinished placeholder. | inspector:Q7, inspector:V1, judge:Q7, judge:V1 | opening_style |  |
| major | ext_4 | the judge scores view ext_4 2/5 (a client would not accept it): The architectural massing is decent, but the render is far from client-ready. The environment is a 'grey box' void with a flat green plane and no context, which makes the house look like a floating model. The materials are untextured and flat, and the entrance area is cluttered with illogical railings. | judge:J1 | agent |  |
| major | ext_5 | the judge scores view ext_5 2/5 (a client would not accept it): The building model itself is coherent, but the presentation is far from client-ready. The context is a void: a flat green plane, a single boxy hedge, and a grey sky. This makes the house look like a floating object in a video game rather than a home in a location. The materials are also very flat and untextured, which hurts the percei | judge:J1 | agent |  |
| major | ext_6 | the judge scores view ext_6 2/5 (a client would not accept it): This is a raw massing/grey-box render, not a client presentation. The building is a block of flat, untextured white surfaces with no materials, landscaping, or context. The windows are pitch black voids, and the overall look is that of a CAD model, not a stylish home. | judge:J1 | agent |  |
| major | f_L0_007 | Mismatched set: the dark ribbed armchair (f_L0_007) and the brown leather armchair (f_L0_016) do not go with the beige sectional (f_L0_011); three different styles/colors with no unifying group. | inspector:Q5, judge:Q5 | wrong_type |  |
| major | f_L0_011 | missing_anchor / empty_room: the corner sofa f_L0_011 is shoved into the far corner facing away from the main area, so the 55 m2 salon has no central seating group and reads as an empty room. | inspector:Q5, inspector:D3, judge:Q5, judge:D3 | wrong_model |  |
| major | f_L0_015 | floating_or_odd_placement: the coffee table f_L0_015 sits alone in the middle of the open floor with no sofa or chairs around it, so it has no reason to be there. | inspector:Q5, inspector:D3, judge:Q5, judge:D3 | wrong_model |  |
| major | f_L0_016 | mismatched_set: f_L0_016 (dark-brown armchair) and f_L0_017 are a different model and colour from f_L0_007 (tan) and the beige f_L0_011 sofa; four armchairs of two styles plus a sofa of a third tone do not form one coherent set. | inspector:D3, inspector:Q5, judge:D3, judge:Q5 | wrong_model |  |
| major | f_L0_024 | The entire room is completely devoid of styling. There are no towels, no accessories, no plants, and no textures on the walls or floor. It looks like a bare, untextured 3D model (grey_box) rather than a stylish, livable space. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L0_031 | kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece) | inspector:S2, inspector:Q5, inspector:D3, judge:Q5, judge:D3 | drawn_layout |  |
| major | f_L1_006 | The white metal bed frame is a crude, low-poly model. The thin, spindly bars look flimsy and the overall design is dated and cheap-looking, not suitable for a modern project. | inspector:D2, inspector:D3, judge:D2, judge:D3 | wrong_model |  |
| major | f_L1_007 | The desk is a generic, mid-century-style piece with wooden legs that does not match the style of either bed. It feels like a random placeholder dropped into the scene. | inspector:D3, judge:D3 | wrong_model |  |
| major | f_L1_012 | The camera is positioned so poorly that the main piece of a bedroom, the bed (f_L1_012), is almost entirely out of frame. A client cannot evaluate a bedroom render where the bed is not visible. | inspector:V1, judge:V1 | interior_camera |  |
| major | f_L1_016 | The main sofa is a crude, blocky white box with flat, untextured surfaces. It looks like a low-poly placeholder model, not a real piece of furniture. | inspector:D3, inspector:D2, judge:D3, judge:D2 | wrong_model |  |
| major | f_L1_021 | The washbasin is a crude black box with a thin rim and a tiny tap; it looks like a placeholder model, not a real basin, and clashes with the all-white scheme. | inspector:D2, judge:D2 | wrong_model |  |
| major | f_L1_029 | The washbasin (f_L1_029) in the bottom right is a crude, low-poly white shape that looks like a placeholder blob rather than a designed fixture. It also appears to float without a visible support or counter. | inspector:D2, judge:D2 | wrong_model |  |
| major | o_L0_002 | The camera angle is poor. It is pointed almost entirely at a large, empty tiled wall (o_L0_002), which makes the render look like a placeholder and fails to showcase the room's design. | process:P2, inspector:V1, inspector:Q7, judge:V1, judge:Q7 | scene |  |
| major | r_L1_hol | The camera angle is poor. It is positioned at the top of the stairs, looking down, but the framing is awkward and obstructed by the railing. It fails to show the hall as a usable space. A better shot would be from within the hall, looking towards the door or the windows, to show the room's character and scale. | process:P2, inspector:V1, judge:V1 | building |  |
| major | w_L0_001 | The windows (and the facade in general) are rendered as flat, untextured white boxes with dark voids. They lack depth, mullions, or any detail, making the house look like a low-poly placeholder rather than a finished design. | inspector:Q7, judge:Q7, judge:V2 | opening_style |  |
| major | w_L1_001 | The window arrangement on the upper floor is disjointed. The large horizontal band of windows (w_L1_001) is interrupted by a random, small vertical window (w_L1_003) that looks like a mistake or a leftover from a previous design iteration. It breaks the rhythm of the facade. | inspector:Q7, judge:Q7, judge:V2 | opening_style |  |
| major | win_L0_004 | The camera is positioned too close to the window and glass partition, causing the frame to be dominated by these elements. The main functional area of the bathroom (the toilet and shower) is pushed to the edge, and the composition feels cramped and unbalanced. | inspector:V1, judge:V1, judge:V2 | interior_camera |  |
| major | win_L1_004 | The windows (win_L1_004, win_L1_005, win_L1_011) look out onto a flat, empty horizon with no landscape, building, or sky gradient, which makes the whole scene feel like an unfinished placeholder. | inspector:Q7, judge:Q7 | opening_style |  |
| minor | d_L0_003 | The glass doors (d_L0_003) have very thick, dark frames that look heavy and industrial, clashing with the light, modern aesthetic of the white facade. They look more like a warehouse door than a residential entrance. | inspector:Q7, judge:Q7 | opening_style |  |
| minor | d_L1_001 | This door is a tall full-height slab that does not match the shorter, narrower leaf of the other door, so the two doors read as a mismatched set. | inspector:Q7, judge:Q7 | opening_style |  |
| minor | d_L1_006 | The light wood door frame on the left is a third distinct material that doesn't clearly tie the room's palette together, adding to the disjointed look. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L0_002 | The entire run is a parametric box: flat white fronts, no handles, no appliance cut-outs, no backsplash. It reads as a grey-box model rather than a styled kitchen. | inspector:D2, inspector:D3, judge:D2, judge:D3 | wrong_model |  |
| minor | f_L0_020 | sink_kitchen f_L0_020 built below the library level: fitting chose the parametric mesh | process:P7, inspector:D3, judge:D3 | fit | library_gap |
| minor | f_L0_026 | The room is extremely plain and lacks any styling. The large expanse of bare tile (bare_material) and the lack of any accessories or decor make it look unfinished and not stylish. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L0_033 | wall_cabinet f_L0_033 built below the library level: fitting chose the parametric mesh | process:P7, inspector:D3, judge:D3 | fit | library_gap |
| minor | f_L0_034 | wall_cabinet f_L0_034 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L0_035 | wall_cabinet f_L0_035 built below the library level: fitting chose the parametric mesh | process:P7 | fit | library_gap |
| minor | f_L1_001 | The stair treads and the exposed concrete soffit/void are a third, raw material tone that clashes with the warm oak floor and soft plaster walls, making the stairwell look unfinished. | inspector:D3, inspector:V1, judge:D3, judge:V1 | wrong_model |  |
| minor | f_L1_010 | The nightstand is a simple, generic box that does not coordinate with any of the other furniture pieces, adding to the disjointed feel of the room. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_022 | The floor lamp (f_L1_022) has a very thin, spindly tripod base that looks flimsy and out of scale with the large, heavy armchairs it is placed between. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_024 | The toilet is a plain white box with no visible seat detail or design; it looks unfinished next to the rest of the bare room. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_025 | The exposed beige/brass plumbing under the basin introduces a third, unexplained material tone that clashes with the otherwise monochrome white set. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_026 | The two nightstands are different models (a drawer unit vs. a plain box), so the bed-side set is not a matched pair. | inspector:Q5, judge:Q5 | wrong_type |  |
| minor | f_L1_028 | This plain box nightstand clashes with the drawer-style nightstand on the other side, breaking the otherwise coherent light-wood scheme. | inspector:D3, judge:D3 | wrong_model |  |
| minor | f_L1_030 | The bench/cabinet is a crude, low-detail wooden slat model that looks like a placeholder rather than a finished piece; it does not match the clean, modern look the door and floor suggest. | inspector:D3, judge:D3 | wrong_model |  |
| minor | r_L1_ebeveyn_y_odasi | a group the room should have found no place: r_L1_ebeveyn_y_odasi: completion added nothing, nothing fits: storage: no candidate position fits the room; work: no place passes the checks | process:P2 | building |  |
| minor | win_L0_006 | no library model: built parametric or not at all: opening win_L0_006: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2 | scene |  |
| minor | win_L1_001 | no library model: built parametric or not at all: opening win_L1_001: parametric in the style's finish (no model of the building's window family 'Single Casement Window' fits 0.95 x 1.20 m: the parametric opening in the style's finish keeps one door and window language) | process:P2, inspector:Q7, judge:Q7 | scene |  |
| minor | win_L1_006 | The window set (win_L1_006/008/009) is plain white uPVC with no visible joinery or trim detail, which looks dated/cheap against the warm oak and plaster and weakens the project's style. | inspector:Q7, inspector:D3, judge:Q7, judge:D3 | opening_style |  |

## untyped: a drawn element no rule or model typed, so nothing builds it ('other', 'unknown')

| severity | target | what | seen by | owner | fix |
|---|---|---|---|---|---|
| major | 42 site_symbols | 42 drawn site symbols (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006 ...) that no rule or model typed ('other'): nothing builds them and nothing explains them | conservation:C4 | reading | type_site_symbols |

## Prevention: the kinds to guard

Each open kind with the findings no fix of the run covers, or that came back from an earlier run: these need a new rule or check (a general one, for every project), not a one-off patch.

- **misread** (34 open, 0 with a fix; arises: reading; guards: plan_vs_model (B*), the room-sense rules (G*, R*), model review M7)
  - RECURRING process:P2 roof vs the drawn section at s # m: the model differs from the drawn section or elevation: roof vs the drawn section at s # m: 11 cases, e.g. roof vs the drawn section at s 1.51 m: 6.589 m built, 6.002 m drawn (+59 cm)
  - RECURRING process:P2 derived ridge # m vs the drawn ridge height # m (# cm): the model differs from the drawn section or elevation: derived ridge 8.530 m vs the drawn ridge height 7.770 m (+76 cm): the pitches are kept
  - RECURRING inspector:G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge)
  - inspector:Q4 f_L0_026: Bathroom with no basin in frame: the washbasin (and shower) are not visible, so the room reads as a toilet closet rather than a complete bathroom.
  - RECURRING inspector:G10 f_L1_021: washbasin f_L1_021: 0.11 m clear in front, needs ≥ 0.53 m
  - inspector:Q4 f_L1_024: The toilet (f_L1_024) is missing from the view. A bathroom render that shows no toilet or shower is not believable and fails the basic 'room makes sense' test.
  - RECURRING inspector:G10 f_L1_025: washbasin f_L1_025: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m
  - inspector:Q4 f_L0_024: The toilet (f_L0_024) is completely missing from the room. A bathroom without a toilet is a fundamental failure.
  - inspector:Q4 f_L0_036: The shower (f_L0_036) is missing. The room is listed as having a shower, but it is not visible in the render.
  - inspector:Q4 f_L0_002: The main counter run has no hob, cooktop or oven — a kitchen without its cooking anchor. The long worktop is empty and the wall above is bare, so the room does not function as a kitchen.
  - inspector:Q4 f_L0_020: The only sink is on a separate counter at the right edge, disconnected from the main run, so the primary work zone has no sink or tap and the layout does not read as a coherent kitchen.
  - inspector:Q4 f_L0_033: The wall_cabinet pieces are not visible above the main run, leaving a large empty wall and reinforcing the impression of an unfinished, incomplete kitchen.
  - inspector:Q4 f_L0_031: The main worktop run has no hob or cooktop. A kitchen without a place to cook is a clear gap a client will point out immediately.
  - inspector:Q4 f_L0_015: Room makes no sense as a finished salon: the listed coffee tables (f_L0_015, f_L0_021) and most armchairs are absent, leaving a 55 m2 living room that looks empty and incomplete.
  - inspector:Q4 f_L1_031: The shower is listed for this bathroom but is not present in the render, so the room is missing one of its main fixtures and reads as an empty box.
  - inspector:Q4 f_L1_029: Bathroom with no basin: the washbasin f_L1_029 is not visible anywhere in the frame, so the room is missing one of its three main pieces and reads as incomplete.
  - inspector:Q4 f_L1_020: The shower (f_L1_020) is completely missing from the frame. A bathroom render that shows no shower, no toilet, and only a fragment of a basin reads as an empty, unfinished room.
  - inspector:Q4 f_L1_017: The armchair (and its twin f_L1_018) is listed for this room but absent from the render, so the bedroom is missing a key piece and looks under-furnished.
  - inspector:Q4 f_L1_022: The floor lamp is in the room's furniture set but not present, leaving the corner by the bed bare and the room feeling empty.
  - inspector:Q4 r_L1_hol: The hall is completely empty. There is no console table, no art, no lighting fixture, and no other decor to make it feel like a finished, stylish home. It looks like an unfinished construction site, n
  - inspector:Q4 f_L1_030: The hall is essentially empty: the shoe cabinet is a tiny bench-like piece tucked into the corner, leaving the whole room bare. A 3.1 m2 entrance hall needs a proper anchor (full-height shoe cabinet, 
  - inspector:Q4 f_L1_027: The floor lamp is listed for this room but is missing from the render, leaving the corner empty and the room feeling incomplete.
  - inspector:Q4 r_L1_soyunma_odasi: A dressing room (soyunma odası) with no furniture at all: no wardrobe, no bench, no mirror, no lighting. The room's entire purpose is missing, so it reads as an empty shell.
- **geometry** (47 open, 0 with a fix; arises: layout, agent; guards: code critic (F*, G*), architect F-rules)
  - RECURRING process:P5 L0:S2: scene check S2 on L0: 1 of 23 failed
  - RECURRING inspector:F9 f_L0_027: ottoman f_L0_027 overlaps sofa_corner f_L0_011 by 0.25 m²
  - RECURRING inspector:F9 f_L0_028: ottoman f_L0_028 overlaps sofa_corner f_L0_011 by 0.25 m²
  - RECURRING inspector:F9 f_L0_029: ottoman f_L0_029 overlaps sofa_corner f_L0_011 by 0.25 m²
  - RECURRING inspector:F9 f_L0_030: ottoman f_L0_030 overlaps sofa_corner f_L0_011 by 0.25 m²
  - RECURRING inspector:G3 f_L0_007: armchair f_L0_007 is 123° off the ottoman f_L0_030 (needs ≤ 30°) at 3.61 m (needs ≤ 2.50 m)
  - RECURRING inspector:G3 f_L0_017: armchair f_L0_017 is 87° off the ottoman f_L0_028 (needs ≤ 30°) at 5.05 m (needs ≤ 2.50 m)
  - RECURRING inspector:G3 f_L0_018: armchair f_L0_018 is 114° off the sofa_corner f_L0_011 (needs ≤ 30°) at 3.33 m (needs ≤ 2.50 m)
  - RECURRING inspector:G11 d_L0_001: no 0.60 m walkway from door d_L0_001 to door d_L0_006
  - RECURRING inspector:G11 d_L0_004: no 0.60 m walkway from door d_L0_004 to door d_L0_006
  - RECURRING inspector:G11 f_L0_008: armchair f_L0_008: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - RECURRING inspector:G11 f_L0_016: armchair f_L0_016: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - RECURRING inspector:G11 f_L0_019: armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_006
  - RECURRING inspector:G11 o_L0_001: no 0.60 m walkway from door o_L0_001 to door d_L0_006
  - RECURRING inspector:F3 f_L0_020: sink_kitchen: its back is not on a wall (0.08 m off)
  - RECURRING inspector:F7 f_L0_032: kitchen_counter blocks door o_L0_001
  - RECURRING inspector:F9 f_L0_031: kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m²
  - RECURRING inspector:G8 f_L0_002: kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m
  - RECURRING inspector:G11 d_L0_003: no 0.60 m walkway from door d_L0_003 to door d_L0_005
  - RECURRING inspector:F3 f_L0_026: washbasin: its back is not on a wall (0.07 m off)
  - RECURRING inspector:F6 f_L1_018: armchair: the free zone in front of it is blocked by f_L1_022
  - RECURRING inspector:F3 f_L1_007: desk: its back is not on a wall (0.06 m off)
  - RECURRING inspector:F9 f_L1_010: nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m²
  - RECURRING inspector:G5 f_L1_006: bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m
  - RECURRING inspector:G5 f_L1_009: bed_double f_L1_009: 0.10 m free along the left side, needs ≥ 0.60 m
  - RECURRING inspector:G11 d_L1_006: no 0.60 m walkway from door d_L1_006 to door d_L1_009
  - RECURRING inspector:G11 o_L1_002: no 0.60 m walkway from door o_L1_002 to door d_L1_009
  - RECURRING inspector:G12 f_L1_020: shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05)
  - RECURRING inspector:F6 f_L1_013: sofa: the free zone in front of it is blocked by f_L1_027
  - RECURRING inspector:G12 f_L1_027: floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05)
  - RECURRING inspector:F3 f_L1_025: washbasin: its back is not on a wall (0.07 m off)
  - inspector:Q6 f_L0_033: The 'wall cabinet' is rendered as a thin floating shelf with no doors or body, leaving the wall above the worktop empty. It does not read as storage and leaves the main run visually unfinished.
  - RECURRING inspector:D1 f_L1_016: The cushions on the grey sofa are broken: one pillow is a flat, crumpled sheet floating/sunk into the seat, and the others are misaligned and clipping. This is the most obvious defect in the frame.
  - inspector:F9 w_L0_001: The entire environment is a 'flat outdoor' void. The ground is a single flat green texture with no horizon, no trees, and no context. This makes the house look like a toy in a vacuum and is embarrassi
  - inspector:F9 o_L0_002: The outdoor environment is completely empty and unconvincing. The 'garden' is a flat green texture, and the hedge is a simple, untextured box. There is no sense of place, scale, or landscaping, which 
- **no_sense** (14 open, 1 with a fix; arises: architect, build; guards: sense (N*: every room reached, no bathroom as a corridor, every level reached), model review (M*), architect rules, visitor checks (Q*))
  - RECURRING process:P2 o_L0_001: an opening of the documents is not cut through its wall: o_L0_001: door ray hits splashback_r_L0_mutfak (splashback); the opening is not cut through its wall
  - RECURRING inspector:X3 d_L1_001: door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_004: door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_005: door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_007: door d_L1_007 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_010: door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - RECURRING inspector:X3 d_L1_011: door d_L1_011 is 3.50 m above the ground with nothing to reach it (a door into the air)
  - inspector:Q2 f_L0_026: The washbasin (f_L0_026) appears to be installed at a height that is too low, closer to knee level than the standard hip height of ~0.85m.
  - inspector:Q2 f_L1_025: The washbasin sits too low and is crammed against the toilet with exposed pipework and no vanity or mirror, so the wet zone looks broken and unusable.
  - inspector:Q3 f_L1_001: The railing is placed on the landing floor, but the stair opening is on the other side of the wall. This is a fall risk and makes no sense; the guard is not protecting the actual edge.
  - inspector:Q9 d_L0_001: The entrance area is a mess. There are railings on both sides of the steps that do not connect to anything and block the path, and the steps themselves look like a crude placeholder. A client would im
- **taste** (75 open, 4 with a fix; arises: fit, decor, opening models; guards: judge (J*), visitor checks Q5, Q7, the fit's matched sets)
  - inspector:V1 r_L1_hol: The camera angle is poor. It is positioned at the top of the stairs, looking down, but the framing is awkward and obstructed by the railing. It fails to show the hall as a usable space. A better shot 
  - inspector:V1 o_L0_002: The camera angle is poor. It is pointed almost entirely at a large, empty tiled wall (o_L0_002), which makes the render look like a placeholder and fails to showcase the room's design.
  - RECURRING inspector:S2 f_L0_031: kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece)
  - inspector:V1 d_L0_007: Bad camera: the door leaf fills the entire right half of the frame and the view is a corner, so the room's main group is not shown.
  - inspector:V1 win_L0_004: The camera is positioned too close to the window and glass partition, causing the frame to be dominated by these elements. The main functional area of the bathroom (the toilet and shower) is pushed to
  - inspector:D3 f_L0_024: The entire room is completely devoid of styling. There are no towels, no accessories, no plants, and no textures on the walls or floor. It looks like a bare, untextured 3D model (grey_box) rather than
  - inspector:V1 cam_r_L0_salon_1: Bad camera: a blank column/wall fills the center of the frame and the main seating group is off to the side, so the room reads as empty and the composition is unbalanced.
  - RECURRING inspector:Q5 f_L0_007: Mismatched set: the dark ribbed armchair (f_L0_007) and the brown leather armchair (f_L0_016) do not go with the beige sectional (f_L0_011); three different styles/colors with no unifying group.
  - inspector:Q5 f_L0_016: mismatched_set: f_L0_016 (dark-brown armchair) and f_L0_017 are a different model and colour from f_L0_007 (tan) and the beige f_L0_011 sofa; four armchairs of two styles plus a sofa of a third tone d
  - inspector:Q5 f_L0_011: missing_anchor / empty_room: the corner sofa f_L0_011 is shoved into the far corner facing away from the main area, so the 55 m2 salon has no central seating group and reads as an empty room.
  - inspector:Q5 f_L0_015: floating_or_odd_placement: the coffee table f_L0_015 sits alone in the middle of the open floor with no sofa or chairs around it, so it has no reason to be there.
  - inspector:D2 f_L1_021: The washbasin is a crude black box with a thin rim and a tiny tap; it looks like a placeholder model, not a real basin, and clashes with the all-white scheme.
  - inspector:Q7 d_L1_009: The door is a flat raw-wood slab with no frame and a visible gap at the floor; it does not match the modern white tile scheme and reads as an unfinished placeholder.
  - inspector:D2 f_L1_009: The bedding on this bed is a crude, low-poly blob. It does not look like a duvet or pillows; it looks like a melted, untextured mass draped over the frame.
  - inspector:D3 f_L1_007: The desk is a generic, mid-century-style piece with wooden legs that does not match the style of either bed. It feels like a random placeholder dropped into the scene.
  - inspector:D2 f_L1_006: The white metal bed frame is a crude, low-poly model. The thin, spindly bars look flimsy and the overall design is dated and cheap-looking, not suitable for a modern project.
  - inspector:Q7 win_L1_004: The windows (win_L1_004, win_L1_005, win_L1_011) look out onto a flat, empty horizon with no landscape, building, or sky gradient, which makes the whole scene feel like an unfinished placeholder.
  - inspector:V1 d_L1_003: The camera is poorly placed, pointing at a corner and a door leaf (d_L1_003) that fills the center of the frame. It fails to show the room's main group or its layout.
  - inspector:D2 f_L1_029: The washbasin (f_L1_029) in the bottom right is a crude, low-poly white shape that looks like a placeholder blob rather than a designed fixture. It also appears to float without a visible support or c
  - RECURRING inspector:Q5 f_L1_017: The two armchairs are a mismatched set. f_L1_017 is a low-poly, faceted chair in a pinkish tone, while f_L1_018 is a smooth, classic 'Egg' chair in brown. They are different models, styles, and colors
  - inspector:V1 f_L1_012: The camera is positioned so poorly that the main piece of a bedroom, the bed (f_L1_012), is almost entirely out of frame. A client cannot evaluate a bedroom render where the bed is not visible.
  - inspector:Q7 d_L1_004: The door is a plain, flat wood slab with a basic handle. It looks like a placeholder and does not match the style of a well-designed home. It also appears to be floating slightly above the floor.
  - inspector:V1 d_L1_002: The camera is aimed dead-on at the door, so the leaf and frame fill the frame and the room itself is not shown. This is a bad camera angle for a client view.
  - inspector:D2 f_L1_013: The white sofa is a crude low-poly / blocky placeholder (flat faceted surfaces, no fabric or cushion detail). It reads as a grey-box model, not a real sofa.
  - inspector:D2 f_L1_016: The main sofa is a crude, blocky white box with flat, untextured surfaces. It looks like a low-poly placeholder model, not a real piece of furniture.
  - inspector:V1 cam_r_L1_soyunma_odasi_1: Camera is pressed into the corner between the door and the wall; the frame is dominated by a door leaf and a blank wall instead of showing the room as a space. There is no main group to frame because 
  - inspector:Q7 w_L0_001: The windows (and the facade in general) are rendered as flat, untextured white boxes with dark voids. They lack depth, mullions, or any detail, making the house look like a low-poly placeholder rather
  - inspector:Q7 d_L0_001: The entrance door is a plain flat slab with no handle, hardware or frame detail, and it sits in a recessed porch with a small canopy that does not read as a designed entry. It looks unfinished and che
  - inspector:Q7 w_L1_001: The window arrangement on the upper floor is disjointed. The large horizontal band of windows (w_L1_001) is interrupted by a random, small vertical window (w_L1_003) that looks like a mistake or a lef
  - judge:J1 cam_r_L0_banyo_1: the judge scores view cam_r_L0_banyo_1 2/5 (a client would not accept it): The render is not client-ready. It shows a nearly empty bathroom where the main fixtures are missing, and the camera is poorl
  - judge:J1 cam_r_L0_banyo_2: the judge scores view cam_r_L0_banyo_2 2/5 (a client would not accept it): The render is a dead-end corner: a toilet squeezed into a niche and a door that fills the right half of the frame. The room's
  - judge:J1 cam_r_L0_banyo_3: the judge scores view cam_r_L0_banyo_3 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation. The camera is poorly placed, the outdoor view is a flat v
  - judge:J1 cam_r_L0_mutfak_1: the judge scores view cam_r_L0_mutfak_1 2/5 (a client would not accept it): The kitchen reads as a grey-box placeholder, not a finished project. The main run is a long, handle-less white slab with a d
  - judge:J1 cam_r_L0_mutfak_2: the judge scores view cam_r_L0_mutfak_2 2/5 (a client would not accept it): The kitchen reads as a shell, not a finished, stylish space. The main run is a bare base cabinet with an empty worktop: no h
  - judge:J1 cam_r_L0_salon_2: the judge scores view cam_r_L0_salon_2 2/5 (a client would not accept it): The room is a 55 m2 shell with no anchor: the corner sofa is pushed into a far corner and the four armchairs are scattered in
  - judge:J1 cam_r_L1_banyo_1: the judge scores view cam_r_L1_banyo_1 2/5 (a client would not accept it): The render is a near-empty white box: the shower (f_L1_031) is missing entirely, the basin is a crude black box, and the room
  - judge:J1 cam_r_L1_banyo_2: the judge scores view cam_r_L1_banyo_2 2/5 (a client would not accept it): The render is a plain, unfinished-looking bathroom that a client would not accept. The most serious issue is that the shower 
  - judge:J1 cam_r_L1_banyo_3: the judge scores view cam_r_L1_banyo_3 1/5 (a client would not accept it): The render is a near-empty corner of the bathroom. The camera is pointed at a blank tiled wall and the door, so the main fixt
  - judge:J1 cam_r_L1_cocuk_odasi_1: the judge scores view cam_r_L1_cocuk_odasi_1 2/5 (a client would not accept it): A client would not accept this as a finished children's room. The two beds are from completely different design languag
  - judge:J1 cam_r_L1_cocuk_odasi_2: the judge scores view cam_r_L1_cocuk_odasi_2 2/5 (a client would not accept it): The room fails on believability and style. The furniture is a clash of placeholder models: a white metal 'hospital' bed
  - judge:J1 cam_r_L1_cocuk_odasi_3: the judge scores view cam_r_L1_cocuk_odasi_3 2/5 (a client would not accept it): The room is a bedroom, but the furniture is a mismatched, dated set that does not read as a designed children's room. T
  - judge:J1 cam_r_L1_dus_1: the judge scores view cam_r_L1_dus_1 2/5 (a client would not accept it): The render is technically clean but fails as a client presentation for a 4.5 m2 bathroom. The most serious issue is that the wa
  - judge:J1 cam_r_L1_dus_2: the judge scores view cam_r_L1_dus_2 2/5 (a client would not accept it): The render is a dead-end view of a tiled corner and a door; the shower (the room's namesake) is not in frame, and the visible w
  - judge:J1 cam_r_L1_ebeveyn_y_odasi_1: the judge scores view cam_r_L1_ebeveyn_y_odasi_1 2/5 (a client would not accept it): The render is a believable, clean bedroom, but it is not the bedroom the client booked. The furniture list for this
  - judge:J1 cam_r_L1_ebeveyn_y_odasi_2: the judge scores view cam_r_L1_ebeveyn_y_odasi_2 2/5 (a client would not accept it): The room fails on basic coherence. The two armchairs are different models and colors, which is a glaring design err
  - judge:J1 cam_r_L1_hol_2: the judge scores view cam_r_L1_hol_2 2/5 (a client would not accept it): The render is a grey-box style view of a landing, but it has a serious logic error that a client would immediately point out. T
  - judge:J1 cam_r_L1_hol_3: the judge scores view cam_r_L1_hol_3 2/5 (a client would not accept it): The render is a confusing, low-value shot of a hall. The camera is placed at the top of the stairs looking down, but the framin
  - judge:J1 cam_r_L1_oda_1: the judge scores view cam_r_L1_oda_1 2/5 (a client would not accept it): A 3.1 m2 hall rendered as a bare corridor: the camera is aimed straight at the door leaf, the walls are flat and untextured, an
  - judge:J1 cam_r_L1_oda_2_1: the judge scores view cam_r_L1_oda_2_1 2/5 (a client would not accept it): The room is unshowable: the main seating is a blocky white placeholder, the two sofas are mismatched, and the cushions on the
  - judge:J1 cam_r_L1_oda_2_2: the judge scores view cam_r_L1_oda_2_2 2/5 (a client would not accept it): The room is lit and the camera is fine, but the furniture set is incoherent and the decor is broken. The two sofas are comple
  - judge:J1 cam_r_L1_oda_2_3: the judge scores view cam_r_L1_oda_2_3 2/5 (a client would not accept it): The room reads as a grey-box placeholder, not a finished living room. The main seating is a blocky, untextured white slab (f_
  - judge:J1 ext_4: the judge scores view ext_4 2/5 (a client would not accept it): The architectural massing is decent, but the render is far from client-ready. The environment is a 'grey box' void with a flat green pla
  - judge:J1 ext_5: the judge scores view ext_5 2/5 (a client would not accept it): The building model itself is coherent, but the presentation is far from client-ready. The context is a void: a flat green plane, a singl
  - judge:J1 ext_6: the judge scores view ext_6 2/5 (a client would not accept it): This is a raw massing/grey-box render, not a client presentation. The building is a block of flat, untextured white surfaces with no mat
- **lost** (7 open, 3 with a fix; arises: any stage boundary: reading -> building, fit, layout, build, render; guards: ledger (A*), conservation (C*), plan_vs_model (B*), process (P*))
  - RECURRING conservation:C2 f_L0_012: f_L0_012 (potted_plant) was to be built after the decor stage and is not built after the agent stage, with no reason
  - RECURRING conservation:C5 sa_L0_veranda: the documents label a site area 'VERANDA' and the model does not build it (open balcony outside the outer walls (no walls drawn around it))
  - RECURRING process:P2 VERANDA: a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'VERANDA' at (9138464.73, 5090593.37) m lies outside the outer walls: an open balcony, recorded in s
  - RECURRING process:P2 BALKON: a labelled space outside the walls was kept as a site record: it must be built: real06.dwg: balcony 'BALKON' at (9138484.48, 5090593.07) m lies outside the outer walls: an open balcony, recorded in si
  - RECURRING process:P2 site: items the reading found and no stage used: site: 2 cases, e.g. site: 1 areas read outside the walls of L1 not used (the site is the ground floor's, L0)
  - render:K1 d_L0_004: door d_L0_004 (from_documents) is not seen in 1 of the 2 view(s) that must show it: cam_r_L0_salon_1
- **process** (6 open, 2 with a fix; arises: scheduler; guards: process (P*))
  - RECURRING process:P4 test_sky_and_window_pulls_reach_their_targets[real06]: test tests.gpu.test_render::test_sky_and_window_pulls_reach_their_targets[real06] failure: AssertionError: real06: [('window panes', 'median pane saturation 0.0631 under 0.065: grey cards, not the sky
  - RECURRING process:P8 run: the run ended 32 min before its deadline with 147 open major point(s): the time could have gone to more fix cycles
  - render:K4 views: 2 view(s) marked for review: cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3
- **untyped** (1 open, 1 with a fix; arises: reading; guards: conservation C4, ledger, the reading's AI questions)
  - RECURRING conservation:C4 42 site_symbols: 42 drawn site symbols (sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006 ...) that no rule or model typed ('other'): nothing builds them and nothing explains them
- **silent** (1 open, 0 with a fix; arises: any stage; guards: process P2 (warnings that say something was left out))
  - RECURRING process:P2 inferred trees: a stage placed fewer items than it planned: inferred trees: placed 0 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 67, front 27; most by window; the first pass placed 0, th
- **other** (1 open, 0 with a fix; arises: -; guards: none)
  - RECURRING inspector:NR f_L1_002: untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built

## Warnings by rule

Every warning of the reading, the build and the site, matched to a rule (``process.WARN_RULES``); 'other' = no rule yet.

assumed 50, read_by 24, drawn_mismatch 17, not_built 16, disagree 13, other 4, not_checked 4, no_model 3, outside_not_room 2, more_labels 2, no_label 2, not_used 2, nothing_fits 2, not_rested 2, not_read 1, not_allowed 1, shortfall 1, not_cut 1

Warnings no rule knows yet (Argus AI reads each one; a new rule in ``process.WARN_RULES`` when one keeps coming):

- building frame: the outer wall faces of the reference r3 start (+3.161, +3.975) m from the sheets outline corner; every region and the sheets coordinates move with them
- levels: the ground floor (building z 0) is printed +0.50 in the section: every relative mark of the plans is read +0.50 m lower (one height frame)
- levels: f_L0_022 moved to symbols (sym_f_L0_022): a level-mark symbol, not furniture (a small drawn piece around a level mark text: '+0,50'); drawn as unknown 0.88 x 0.34 m
- r_L0_oda: no AI furniture, no groups for this room (hall 2.1 m²: nothing)
