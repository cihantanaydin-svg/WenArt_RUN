# Architect's review: real06

446 questions asked (46 rules x the elements they apply to), 68 change(s), 51 answered, 1 open point(s).

| rule | topic | asked | fine | changed | answered | open |
|---|---|---|---|---|---|---|
| B1 | arrival | 1 | 1 | 0 | 0 | 0 |
| B2 | parking | 0 | 0 | 0 | 0 | 0 |
| A2 | access | 0 | 0 | 0 | 0 | 0 |
| A5 | decks without a door | 0 | 0 | 0 | 0 | 0 |
| E1 | outside doors | 10 | 4 | 0 | 6 | 0 |
| O2 | gaps in the facade | 12 | 0 | 0 | 12 | 0 |
| C1 | circulation | 11 | 10 | 0 | 1 | 0 |
| C2 | kitchen | 1 | 1 | 0 | 0 | 0 |
| T1 | stairs | 0 | 0 | 0 | 0 | 0 |
| T2 | every floor reached | 2 | 2 | 0 | 0 | 0 |
| L1 | daylight | 5 | 4 | 0 | 1 | 0 |
| W2 | windows to the outside | 36 | 28 | 0 | 8 | 0 |
| L2 | fresh air | 4 | 4 | 0 | 0 | 0 |
| W3 | low sills | 18 | 18 | 0 | 0 | 0 |
| P1 | privacy | 3 | 2 | 0 | 1 | 0 |
| R1 | room size | 2 | 2 | 0 | 0 | 0 |
| R2 | use | 8 | 8 | 0 | 0 | 0 |
| R3 | ceiling height | 12 | 12 | 0 | 0 | 0 |
| R4 | room area | 8 | 8 | 0 | 0 | 0 |
| R5 | room type | 12 | 12 | 0 | 0 | 0 |
| O1 | openings in their walls | 49 | 48 | 0 | 1 | 0 |
| D1 | door widths | 16 | 10 | 0 | 6 | 0 |
| D2 | doors lead somewhere | 12 | 12 | 0 | 0 | 0 |
| D4 | doors on their floor | 12 | 12 | 0 | 0 | 0 |
| D5 | door types | 12 | 9 | 0 | 3 | 0 |
| D3 | doors to the terraces | 0 | 0 | 0 | 0 | 0 |
| X1 | outer walls | 15 | 15 | 0 | 0 | 0 |
| F5 | clashing furniture | 45 | 39 | 6 | 0 | 0 |
| F1 | pieces in their rooms | 43 | 42 | 0 | 1 | 0 |
| F2 | free doorways | 12 | 12 | 0 | 0 | 0 |
| F3 | free windows | 35 | 33 | 0 | 2 | 0 |
| F4 | room to use | 18 | 17 | 0 | 0 | 1 |
| H1 | working heights | 4 | 4 | 0 | 0 | 0 |
| U1 | outdoor furniture | 0 | 0 | 0 | 0 | 0 |
| S4 | complete furniture groups | 4 | 1 | 0 | 3 | 0 |
| S2 | furniture chosen together | 8 | 0 | 8 | 0 | 0 |
| S3 | styled rooms | 10 | 5 | 0 | 5 | 0 |
| K1 | stair details | 1 | 0 | 1 | 0 | 0 |
| K2 | guards | 1 | 0 | 1 | 0 | 0 |
| K3 | one balustrade language | 1 | 0 | 1 | 0 | 0 |
| S1 | falls | 0 | 0 | 0 | 0 | 0 |
| A3 | outside doors | 0 | 0 | 0 | 0 | 0 |
| A4 | light wells | 0 | 0 | 0 | 0 | 0 |
| A1 | rain water | 2 | 2 | 0 | 0 | 0 |
| G1 | trees | 0 | 0 | 0 | 0 | 0 |
| A0 | the AI architect's own decisions | 1 | 0 | 0 | 1 | 0 |

## The architect's questions for you

1. **F4 room to use** (minor): only 20% of the 0.5 m in front of f_L1_021 (washbasin) is free (f_L1_024 in the way). *Can f_L1_021 be used where it stands?* Answer key `F4:f_L1_021`; options `keep` (keep it as drawn (the question closes; nothing changes))

Answers go into `projects/<project>/architect_answers.json` as `{"answers": {"<key>": {"option": "<option>", "answer": "<your words>"}}}`; the next run carries them out and does not ask again. The AI architect on the pod answers the rest it can settle (checked by code).

## What the architect changed or settled

- **E1 d_L1_001**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> d_L1_001 (door, 2.15 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **E1 d_L1_004**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> d_L1_004 (door, 0.65 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **E1 d_L1_005**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> d_L1_005 (door, 1.55 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **E1 d_L1_007**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> d_L1_007 (door, 0.75 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **E1 d_L1_010**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> d_L1_010 (door, 0.45 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **E1 d_L1_011**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> d_L1_011 (door, 0.70 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L0_002**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L0_002 (opening, 1.10 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L0_003**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L0_003 (opening, 2.15 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L0_004**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L0_004 (opening, 1.45 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L0_005**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L0_005 (opening, 1.55 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L0_006**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L0_006 (opening, 1.55 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L0_007**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L0_007 (opening, 1.85 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L1_001**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L1_001 (opening, 1.95 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L1_003**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L1_003 (opening, 1.95 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L1_004**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L1_004 (opening, 1.15 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L1_005**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L1_005 (opening, 1.45 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L1_006**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L1_006 (opening, 1.55 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **O2 o_L1_007**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: nothing is outside this door or gap: a window at the floor's sill (same width and head) -> o_L1_007 (opening, 1.55 m) opens onto nothing outside: read as a window, sill 0.90 m, head 2.10 m (the floor's windows)
- **C1 r_L1_soyunma_odasi**: settled by its answer -> answered by the AI architect ("The room is a small 5.9 m2 dressing room that cannot be reached from the entrance through any door, opening or stair."): the room is another type (params: room_type) -> r_L1_soyunma_odasi is a storage
- **L1 r_L0_mutfak**: glass 1/5 of the floor -> answered by the AI architect ("The kitchen is a habitable room with only 1/11 of its floor in glass, below the 1/10 daylight requirement."): r_L0_mutfak already has 4.26 m2 of glass (1/6)
- **W2 win_L0_001**: a clear borrowed-light window between r_L0_mutfak and r_L0_salon (decided) -> answered by the architect's default ("the safe default"): win_L0_001: a borrowed-light window between r_L0_mutfak and r_L0_salon
- **W2 win_L0_006**: to the outside -> answered by the AI architect ("The window sits in a wall between two living rooms, which is a reading error that should be moved to the outer wall."): win_L0_006 sat in the inside wall w_L0_026 between two rooms; moved to the outer wall w_L0_029 of r_L0_salon (same size), at 4.48, 2.60
- **W2 win_L0_007**: to the outside -> answered by the AI architect ("The window sits in the wall between the kitchen and the hall, which is a reading error for the dark kitchen."): win_L0_007 sat in the inside wall w_L0_033 between two rooms; moved to the outer wall w_L0_019 of r_L0_mutfak (same size), at 2.66, 13.43
- **W2 win_L1_001**: to the outside -> answered by the AI architect ("The window sits in the wall between the dressing room and the bedroom, which is a reading error for the dark dressing room."): win_L1_001 sat in the inside wall w_L1_008 between two rooms; moved to the outer wall w_L1_038 of r_L1_soyunma_odasi (same size), at 8.53, 7.60
- **W2 win_L1_004**: a high borrowed-light window between r_L1_dus and r_L1_soyunma_odasi (decided) -> answered by the architect's default ("the safe default"): win_L1_004: a high window, sill 0.90 -> 1.80 m
- **W2 win_L1_005**: a high borrowed-light window between r_L1_dus and r_L1_soyunma_odasi (decided) -> answered by the architect's default ("the safe default"): win_L1_005: a high window, sill 0.90 -> 1.80 m
- **W2 win_L1_008**: a clear borrowed-light window between r_L1_oda_2 and r_L1_hol (decided) -> answered by the architect's default ("the next safe fix (move_window_to_outer_wall could not be done)"): win_L1_008: a borrowed-light window between r_L1_oda_2 and r_L1_hol
- **W2 win_L1_003**: settled by its answer -> answered by the architect's default ("the safe default"): a reading error: the room has no door, this opening between two rooms is its door -> win_L1_003 between r_L1_soyunma_odasi and r_L1_ebeveyn_y_odasi: the door of the room no door reached
- **P1 d_L0_007**: the bathroom door d_L0_007 opens into r_L0_mutfak -> answered by the AI architect ("The only available choice is to keep the guest WC by the living room."): keep it as drawn (the question closes; nothing changes)
- **O1 d_L1_011**: fits w_L1_004 -> answered by the architect's default ("the safe default"): d_L1_011 and o_L1_001 merged (1.98 m)
- **D1 d_L0_003**: 0.80 m -> answered by the AI architect ("A 0.65 m door to the outside is too narrow for furniture or a wheelchair."): d_L0_003 0.65 -> 0.80 m wide
- **D1 d_L0_004**: 0.80 m -> answered by the AI architect ("A 0.75 m door to the outside is too narrow for furniture or a wheelchair."): d_L0_004 0.75 -> 0.80 m wide
- **D1 d_L1_004**: settled by its answer -> answered by the AI architect ("A 0.65 m door to the outside is too narrow for furniture or a wheelchair."): widen the door to 0.80 m (0.70 m for a WC) where the wall allows -> d_L1_004 0.65 -> 0.80 m wide
- **D1 d_L1_007**: settled by its answer -> answered by the AI architect ("A 0.75 m door to the outside is too narrow for furniture or a wheelchair."): widen the door to 0.80 m (0.70 m for a WC) where the wall allows -> d_L1_007 0.75 -> 0.80 m wide
- **D1 d_L1_010**: settled by its answer -> answered by the AI architect ("A 0.45 m door to the outside is too narrow for furniture or a wheelchair."): widen the door to 0.80 m (0.70 m for a WC) where the wall allows -> d_L1_010 0.45 -> 0.80 m wide
- **D1 d_L1_011**: settled by its answer -> answered by the AI architect ("A 0.70 m door to the outside is too narrow for furniture or a wheelchair."): widen the door to 0.80 m (0.70 m for a WC) where the wall allows -> d_L1_011 0.70 -> 0.80 m wide
- **D5 d_L0_001**: 2.15 m: a glazed sliding door: glazed panels of at most 1.2 m in the frame, one fixed -> answered by the architect's default ("the safe default"): d_L0_001 (2.15 m, an outside door): a glazed sliding door: glazed panels of at most 1.2 m in the frame, one fixed, 2 panels
- **D5 d_L0_004**: 0.80 m: the entrance door: one entrance leaf, glazed side lights where the opening is wider -> answered by the architect's default ("the safe default"): d_L0_004 (0.80 m, an outside door): the entrance door: one entrance leaf, glazed side lights where the opening is wider
- **D5 d_L0_006**: 2.95 m: a glazed sliding door: glazed panels of at most 1.2 m in the frame, one fixed -> answered by the architect's default ("the safe default"): d_L0_006 (2.95 m, an outside door): a glazed sliding door: glazed panels of at most 1.2 m in the frame, one fixed, 3 panels
- **F5 f_L0_002**: kitchen_counter clashed with f_L0_031 -> f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once
- **F5 f_L0_027**: ottoman clashed with f_L0_011 -> f_L0_027 (ottoman) cut f_L0_011 (sofa_corner) by 0.50 m; f_L0_027 (ottoman) moved 0.86 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L0_029**: ottoman clashed with f_L0_011 -> f_L0_029 (ottoman) cut f_L0_011 (sofa_corner) by 0.50 m; f_L0_029 (ottoman) moved 0.63 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L0_030**: ottoman clashed with f_L0_011 -> f_L0_030 (ottoman) cut f_L0_011 (sofa_corner) by 0.05 m; f_L0_030 (ottoman) moved 0.07 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L1_007**: desk clashed with f_L1_006 -> f_L1_007 (desk) cut f_L1_006 (bed_double) by 0.13 m; f_L1_007 (desk) moved 0.15 m clear of it (inside its room, clear of the other pieces and the doorways)
- **F5 f_L1_010**: nightstand clashed with f_L1_009 -> it cut f_L1_009 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built
- **F1 f_L0_035**: f_L0_035 (wall_cabinet) stands 68% outside r_L0_mutfak -> answered by the AI architect ("A wall cabinet is a wall-mounted fixture, so its footprint extending beyond the room's floor boundary is a plausible drawing convention rather than a placement error."): keep it as drawn (the question closes; nothing changes)
- **F3 o_L1_005**: f_L1_013 stand(s) in front of 100% of o_L1_005 -> answered by the AI architect ("The only available choice is keep, and the move was already tried and refused because no free place exists within the move limit."): keep it as drawn (the question closes; nothing changes)
- **F3 win_L1_002**: f_L1_009 stand(s) in front of 100% of win_L1_002 -> answered by the AI architect ("The only available choice is to keep the drawing as is."): keep it as drawn (the question closes; nothing changes)
- **S4 r_L0_salon**: r_L0_salon (living) misses side_table or floor_lamp, a rug -> answered by the AI architect ("The living room is a major space that will be fully styled with a rug and complete furniture group during the build phase."): keep it as drawn (the question closes; nothing changes)
- **S4 r_L1_cocuk_odasi**: r_L1_cocuk_odasi (bedroom) misses 2 nightstand(s) -> answered by the AI architect ("The children's room is a habitable space that will be fully styled with a bed group and nightstands during the build phase."): keep it as drawn (the question closes; nothing changes)
- **S4 r_L1_oda_2**: r_L1_oda_2 (living) misses table_coffee or ottoman, a rug -> answered by the AI architect ("The drawing is plausible as it is, and the missing items are not a structural error."): keep it as drawn (the question closes; nothing changes)
- **S2 r_L0_salon**: r_L0_salon: wood medium, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L0_banyo**: r_L0_banyo: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_ebeveyn_y_odasi**: r_L1_ebeveyn_y_odasi: wood -, metal brass -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_cocuk_odasi**: r_L1_cocuk_odasi: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_oda**: r_L1_oda: wood light, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_dus**: r_L1_dus: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_oda_2**: r_L1_oda_2: wood -, metal - -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S2 r_L1_banyo**: r_L1_banyo: wood -, metal silver -> chosen as a set by the fit (one wood tone and a contrast, one metal)
- **S3 r_L0_banyo**: r_L0_banyo (bathroom) holds 1 decor item(s), a styled bathroom 2 -> answered by the AI architect ("The only available choice is to keep the bathroom as drawn."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_hol**: r_L1_hol (hall) holds 0 decor item(s), a styled hall 2 -> answered by the AI architect ("The hall is a circulation space where the drawn windows and layout are sufficient for a plausible render."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_dus**: r_L1_dus (bathroom) holds 1 decor item(s), a styled bathroom 2 -> answered by the AI architect ("The shower room is a small utility space where the fixtures are sufficient for a plausible render."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_oda_2**: r_L1_oda_2 (living) holds 3 decor item(s), a styled living 9 -> answered by the AI architect ("The bedroom is a habitable space that will be fully styled with a bed group, nightstands, and decor during the build phase."): keep it as drawn (the question closes; nothing changes)
- **S3 r_L1_banyo**: r_L1_banyo (bathroom) holds 1 decor item(s), a styled bathroom 2 -> answered by the AI architect ("The bathroom is a small utility space where the fixtures and the single decor item are sufficient for a plausible render."): keep it as drawn (the question closes; nothing changes)
- **K1 f_L0_001**: stair f_L0_001: drawn with too few treads for its storey -> winders: riser 0.176 m, going 0.25 m, 2R+G 0.60 m; built with 3 winders in the half landing, tread plates with nosings over painted risers, a glass posts balustrade on 2 open side(s)
- **K2 void_L1_0**: stair void of L1: 3.31 m of free edge -> a 1.00 m glass posts balustrade along it (the stair arrives from f_L0_001)
- **K3 house**: balustrades: stairs 1 -> one kind for the house: glass posts (from the style)
- **A0 d_L0_002**: settled by its answer -> answered by the AI architect ("The kitchen and living room are both dry rooms, so the wide doorway between them becomes a serving window over the counter."): a serving window over the drawn counter: the doorway becomes a window at counter height between the two rooms (the counter stays) -> d_L0_002: a serving window over the counter, sill 0.95 m

## The questions

- **B1 arrival** (major, ok): *Where do I come in? Is there a path from the street to the main entrance door?* Why: a front door nobody can find or reach on foot is the first thing a visitor notices. Asked of 1 element(s).
- **B2 parking** (minor, ok): *Where do I leave the car, and how do I walk from it to the front door?* Why: a parking with no path to the entrance makes people cross the lawn or the driveway's kerb. Asked of 0 element(s).
- **A2 access** (major, ok): *How do people get to each terrace and pool deck? From the house through a door at its level, or from the garden by steps that no railing closes.* Why: a terrace or pool nobody can walk to is useless and unsafe. Asked of 0 element(s).
- **A5 decks without a door** (minor, ok): *This terrace lies at the floor level of the rooms beside it, right outside their windows, and no door opens onto it: can people still reach it from outside? (The drawn windows stay windows; only when no outside way exists does the architect ask you about a door.)* Why: a deck at the floor's level begs for a door; the drawings decide it. Asked of 0 element(s).
- **E1 outside doors** (major, ok): *Does every outside door open onto something: the ground, a terrace, a balcony or steps?* Why: a door into the air or below the ground is a drawing or level error. Asked of 10 element(s).
- **O2 gaps in the facade** (major, ok): *Is every gap in an outer wall a door or a window (never a bare hole in the facade)?* Why: a gap with no door and no glass reads as a hole; on an upper floor nothing stops a fall. Asked of 12 element(s).
- **C1 circulation** (major, ok): *Can I reach every room from the entrance, and without walking through somebody's bedroom?* Why: a room you can only reach through a bedroom is a planning fault (an en-suite bathroom or dressing room is the exception). Asked of 11 element(s).
- **C2 kitchen** (minor, ok): *Is the kitchen next to where people eat and sit (a door or an opening to the living or dining space)?* Why: carrying plates through a hall or another room every day is a sign the plan is not working. Asked of 1 element(s).
- **T1 stairs** (major, ok): *Does every stair lead to another floor?* Why: a stair that ends nowhere is a reading error of the level or the stair room. Asked of 0 element(s).
- **T2 every floor reached** (major, ok): *Can I reach every floor from the entrance?* Why: a floor without a stair or a door from outside cannot be used. Asked of 2 element(s).
- **L1 daylight** (major, ok): *Does every bedroom, living room and kitchen get daylight: a window with glass of at least a tenth of its floor?* Why: a habitable room without enough daylight feels like a cellar; building codes ask for about 1/10. Asked of 5 element(s).
- **W2 windows to the outside** (major, ok): *Does every window look outside (or onto a terrace)?* Why: a window between two rooms is usually a reading error: the dark room needs it on its outer wall. Asked of 36 element(s).
- **L2 fresh air** (minor, ok): *Can every bathroom and kitchen be aired: a window, else a mechanical extract?* Why: steam and cooking smells need a way out. Asked of 4 element(s).
- **W3 low sills** (major, ok): *Where a window lies more than a metre over the ground, is its sill at least 0.85 m high?* Why: a low sill over a drop is a fall risk (or the window needs a guard). Asked of 18 element(s).
- **P1 privacy** (minor, answered): *Does a bathroom door open straight into the living room, the dining space or the kitchen?* Why: a toilet door in the room where people eat or receive guests is uncomfortable for everybody. Asked of 3 element(s).
- **R1 room size** (minor, ok): *Is every bedroom wide enough for its bed with room to walk around it?* Why: a bedroom narrower than about 2.4 m leaves no passage beside a bed. Asked of 2 element(s).
- **R2 use** (minor, ok): *Is every room furnished for what it is (a bed in each bedroom, a sofa in the living room, a table where people eat, a WC and a basin in each bathroom)?* Why: a room without its main piece reads as unfinished in the renders. Asked of 8 element(s).
- **R3 ceiling height** (minor, ok): *Is every room high enough: 2.40 m for a habitable room, 2.10 m for the others?* Why: a low ceiling feels oppressive and breaks most building codes. Asked of 12 element(s).
- **R4 room area** (minor, ok): *Is every room big enough for what it is (a bedroom 6.5 m2, a living room 10 m2, a kitchen 4 m2, a bathroom 2 m2)?* Why: a room smaller than any room of its type is usually a misread type or size. Asked of 8 element(s).
- **R5 room type** (minor, ok): *Do I know what every room is for?* Why: an untyped room cannot be furnished or lit for its use. Asked of 12 element(s).
- **O1 openings in their walls** (major, ok): *Does every door and window fit in its wall: within its length, clear of the other openings, under the ceiling?* Why: an opening past the wall's end or over another one is a drawing or reading error. Asked of 49 element(s).
- **D1 door widths** (minor, ok): *Is every door wide enough: 0.70 m inside (0.60 m to a WC), 0.80 m to the outside?* Why: a narrow door cannot take furniture or a wheelchair; often a misread width. Asked of 16 element(s).
- **D2 doors lead somewhere** (major, ok): *Does every door join two rooms, or a room and the outside?* Why: a door with the same room or nothing on both sides is on the wrong wall. Asked of 12 element(s).
- **D4 doors on their floor** (major, ok): *Does every door stand on the floor of the rooms it joins (no door raised over both floors)?* Why: a door that starts half a metre over the floor is the first thing a visitor sees; it is a level error. Asked of 12 element(s).
- **D5 door types** (major, ok): *What kind of door is every outside door and every wide door: French doors or a glazed sliding door into a room, the entrance door at the front, a sectional door to the garage, and never one leaf much wider than 1.2 m?* Why: a 3 m flat wooden leaf in a facade reads as a garage door on a house that has none; a living room opens to the garden through glass. Asked of 12 element(s).
- **D3 doors to the terraces** (minor, ok): *Is every door to a terrace or balcony a glazed door, 0.80 m wide or more, in the windows' finish?* Why: a terrace door is part of the facade: a solid inside door there reads wrong and darkens the room. Asked of 0 element(s).
- **X1 outer walls** (minor, ok): *Is every outer wall thick enough for a facade (0.15 m or more)?* Why: a thin outer wall is usually a partition read as the facade, or a glass wall. Asked of 15 element(s).
- **F5 clashing furniture** (major, fixed): *Does any piece cut another (a side table in a sofa, a lamp in a bed, a chair through its table)?* Why: two pieces through each other are the first thing a client sees in a render. Asked of 45 element(s).
- **F1 pieces in their rooms** (minor, answered): *Does every piece of furniture stand inside its room?* Why: a piece through a wall is a placement error. Asked of 43 element(s).
- **F2 free doorways** (minor, ok): *Can every door open and be walked through without furniture in the way?* Why: a wardrobe in front of a door is the first thing a visitor bumps into. Asked of 12 element(s).
- **F3 free windows** (minor, answered): *Is every window free of tall furniture standing in front of it?* Why: a wardrobe against a window blocks the light and looks wrong from outside. Asked of 35 element(s).
- **F4 room to use** (minor, open): *Is there room in front of every bed, sofa, wardrobe, WC and counter to use it (0.5 m)?* Why: a piece you cannot reach or open is not usable. Asked of 18 element(s).
- **H1 working heights** (major, ok): *Is every fixture at its working height (a washbasin's rim at 0.80-0.90 m)?* Why: a basin at knee height looks like a toy and cannot be used. Asked of 4 element(s).
- **U1 outdoor furniture** (minor, ok): *Is every piece on a balcony, terrace or patio a piece one puts outside, of a model made for outside?* Why: an indoor table with a drawer or upholstered chairs on a terrace look wrong and would not last a winter. Asked of 0 element(s).
- **S4 complete furniture groups** (minor, answered): *Is every furniture group complete: a sofa with a coffee table, an end table or a lamp and a rug; a double bed with two nightstands; a dining table with four chairs or more?* Why: a sofa alone or a bed with one nightstand looks half furnished. Asked of 4 element(s).
- **S2 furniture chosen together** (minor, fixed): *Does the furniture of every room look chosen together: one or two wood tones, one metal finish, loud colours only from the style's palette?* Why: a walnut table, a white oak bed and a pine chair with brass and chrome read as a second-hand shop. Asked of 8 element(s).
- **S3 styled rooms** (minor, answered): *Is every room styled with enough decor (a living room 9 items, a bedroom 7, a dining room 4)?* Why: a room without lamps, plants, art, cushions and a rug looks unfinished in a render. Asked of 10 element(s).
- **K1 stair details** (minor, fixed): *Is every stair comfortable and finished: risers 0.15-0.19 m, goings 0.25 m+, 2R+G 0.60-0.65 m, 0.80 m wide, treads with nosings, a balustrade on the open side, a handrail?* Why: a steep or narrow stair is unsafe; a stair without nosings, balusters or a handrail looks unfinished. Asked of 1 element(s).
- **K2 guards** (major, fixed): *Does every edge over a drop (a balcony, a roof terrace, a terrace over the garden) have a guard of 1.00 m whose gaps a child cannot pass, and every parapet a coping?* Why: a fall of over a metre needs a guard; a bare parapet top stains the facade. Asked of 1 element(s).
- **K3 one balustrade language** (minor, fixed): *Do the balustrades of the house (stairs, balconies, terraces, parapets) speak one language?* Why: glass on one side and steel bars on the other look like two houses. Asked of 1 element(s).
- **S1 falls** (major, ok): *Where could somebody fall more than half a metre: is every such terrace, pool deck and roof terrace edge guarded?* Why: an unguarded drop is the first safety question of every design review. Asked of 0 element(s).
- **A3 outside doors** (minor, ok): *Which doors open to the open air? A door to a terrace or balcony is an outside door: glazed, weather-tight, never the bedroom door of the inside.* Why: an inside door on the open air leaks and looks wrong from outside. Asked of 0 element(s).
- **A4 light wells** (minor, ok): *Why does this basement window have a light well? Only where the ground outside stands above its sill; a terrace below the sill lights it on its own.* Why: a light well where none is needed is a concrete box in the garden. Asked of 0 element(s).
- **A1 rain water** (minor, ok): *Where does the rain go? Every gutter must drain into a downpipe fixed to a wall all the way down to the ground: no pipe in front of a loggia, across a window or in the air.* Why: rain running down a facade stains it and a pipe in the air looks like a mistake. Asked of 2 element(s).
- **G1 trees** (minor, ok): *Does every tree and shrub stand on open ground, clear of the house, the pools, the paths and the terraces?* Why: a tree through a terrace or in front of a door is a reading or placement error. Asked of 0 element(s).
- **A0 the AI architect's own decisions** (minor, answered): *What did the AI architect decide on its own?* Why: it looked at each floor of the model and changed what it judged wrong; code checked every change. Asked of 1 element(s).

## What the user taught me

36 lessons from the user's requests and corrections (wenart/blender/architect_lessons.json); each is checked on every project.

| Lesson | What I check | Here |
|---|---|---|
| UL01 | Every outer wall carries a facade finish (render, stone, cladding) with a plinth, slab bands, copings and window surrounds; never bare concrete. | build |
| UL02 | Nothing sticks out of the facade unless drawn: a basement window gets a light well or a court only when the ground outside is above its sill, never on a terrace that lies below it. | build, B1 ok |
| UL03 | Outer doors and windows are real products from the library with see-through glass; a door to a terrace is mostly glass, in the windows' frame finish. | D3 ok, build |
| UL04 | The site is furnished like a real garden: trees, shrubs, hedges, lawn, cars on the parking, from the library. | build, G1 ok |
| UL05 | Gutters run along every eave and downpipes run down solid walls to the ground; nothing hangs in the air. | build |
| UL06 | The roof is closed and real: no gaps, eaves with a fascia, ridges and hips, its form following the plan. | build |
| UL07 | Every terrace and pool deck can be reached: from a door at its level or by steps and a path from the site's paths. | A2 ok, A5 ok |
| UL08 | The architect asks every rule of every element (thousands of questions), fixes what code can fix safely, asks the user the rest with options, and the AI on the pod answers the open ones. | build |
| UL09 | The top-down views look from the north-east at about 35 degrees with the walls cut at 0.6 m and the windows marked. | build |
| UL10 | Reach a terrace from outside (steps and a path) before turning a drawn window into a door: drawn openings stay as drawn (26 Oct 2026: except a window between two rooms where one has no door at all: that is its misread door, architect W2). | A5 ok, A2 ok |
| UL11 | A window between two rooms is a reading error: it moves to the dark room's outer wall. | W2 ok |
| UL12 | A habitable room gets glass of at least a tenth of its floor; too little glass: the windows are enlarged. | L1 ok |
| UL13 | A separate kitchen may be meant: the architect asks before joining rooms and keeps the answer. | C2 ok |
| UL14 | No two pieces of furniture cut each other in any render; clashes are planned apart before the build. | F5 fixed |
| UL15 | A terrace beside the house sits at the floor its doors and windows serve, never half way between floors; no pit is cut into a terrace; mirrored twins match; walls over 1.2 m step back as planted terraces or carry a guard. | build, A2 ok, K2 fixed |
| UL16 | The furniture of a room and of the house is one coherent set: one design language, one or two wood tones, one metal finish, a colour palette from the style (60-30-10), real proportions, and one statement piece per room. | S2 fixed |
| UL17 | Rooms are styled like a magazine shoot: every table, console, shelf and nightstand carries a small group of decor, walls carry art, every living room and bedroom has plants, lamps, a rug, cushions and a throw. | S3 answered |
| UL18 | Every room is complete for its use: a sofa with a coffee table, side tables, a floor lamp and a rug; a bed with two nightstands and lamps (and a bench in a large room); a dining table with its chairs, a pendant and a sideboard. | S4 answered |
| UL19 | Cushions and pillows rest on and lean against their seat or headboard and sink a little into it; no cushion on a model that has its own. | build |
| UL20 | A terrace is furnished with outdoor pieces (metal, teak, rattan, stone; no indoor desks or upholstery) and reached through a glazed door. | U1 ok, D3 ok |
| UL21 | Details are built like real products: stairs with comfortable risers, tread plates with nosings, a balustrade and a handrail; guards of 1 m with gaps under 0.11 m; a coping on every parapet; one balustrade language for the house. | K1 fixed, K2 fixed, K3 fixed |
| UL22 | Every fix is a general rule with a test, never a patch for one project. | process |
| UL23 | Library models are chosen for the look of the render (fitting together, carrying the style), not for their licence (licence_mode relaxed). | process |
| UL24 | A reading problem is fixed in the reader, so the pod handles the next drawing of that kind alone. | process |
| UL25 | Every new request or correction of the user becomes a lesson here (python -m wenart.agent.lessons add); open lessons are checked by the AI architect on every run until a rule checks them. | process |
| UL26 | Every before / after compares the new run with the project's latest run before it (never a milestone run); the new run then becomes the latest. | process |
| UL27 | Every fix is a general rule of the pipeline for every project; the project that showed the problem is only the test case. | process |
| UL28 | Gutters run straight along each facade under the eaves (facade jogs shallower than 0.6 m are closed under the roof); downpipes stand only at the building's corners, at least 3 m apart, about one per 50 m2 of roof. | A1 ok |
| UL29 | Every fixture works at its working height: a washbasin's rim at 0.80-0.90 m (a wall-hung model hangs there; a bowl too shallow to hang needs a counter and is not taken alone). | H1 ok |
| UL30 | Every door stands on the floor of the rooms it joins; the plans' level marks are read in the section's height frame (the ground floor's printed mark is building z 0). | D4 ok |
| UL31 | No opening on an upper floor reaches the floor without a real guard: a door or bare gap with nothing outside is a window at the floor's sill; a French window gets a full-width glass guard 1.10 m high; every stair void edge gets a balustrade. | E1 ok, O2 ok, W3 ok, K2 fixed |
| UL32 | The house reads as one design: one door and window language in the house's style (clear glass, no panelled doors in a modern house), one model per role in a group, one dining set per room, no folding or garden chairs indoors, no piece with its back to the room. | S2 fixed, S3 answered |
| UL33 | The architect settles every open point that has a safe fix by itself (its default); the AI architect answers the rest; the AI inspector asks a visitor's questions (Q1-Q8) of every render, sends each finding to its fix and reports what is left before the user looks. | process |
| UL34 | Review the 3D model itself first: every element of the model as built is measured (doors on their floors, working heights, guards, doors into the air, rain water, one opening language, rooms that make sense), on every floor, before any render; the vision model looks at the model's floors from above (every room) and the renders only for the look. | process |
| UL35 | The architect decides: every open point ends with a decision (the next safe fix when one cannot be done); a refused AI pick is asked again with the reason; the AI looks at each floor of the model, may change a default or decide on its own from typed actions; code keeps a decision only when nothing new breaks. | process |
| UL36 | Entrances make sense: doors whose landings or flights touch share one platform with one flight; a handrail or ramp never crosses in front of a door; the front door is a normal entrance door, not the widest garden door; a wide outside door of a living room is glazed (French or sliding), never one flat slab that reads as a garage door (D5; the model check M8; the visitor check Q9). | D5 ok, build |
