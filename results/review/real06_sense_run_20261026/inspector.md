# What the AI inspector saw on the final renders: real06

Round 4 (the final round: every room and exterior view asked again on the final renders, with the visitor checks Q1-Q8). 14 vision finding(s) (4 visitor), 1 fixed in this round, 0 handed to the stage that owns them, 117 open, 3 dropped by code; the architect leaves 7 open point(s) (4 major).

Visitor checks: Q1 a door that makes no sense; Q2 a fixture at the wrong working height; Q3 a fall risk; Q4 a room that makes no sense; Q5 pieces that repeat or do not belong together; Q6 a piece placed the wrong way; Q7 doors and windows that do not fit the house or each other; Q8 rain water that makes no sense

| severity | check | where | target | what | outcome |
|---|---|---|---|---|---|
| critical | Q4 | r_L1_ebeveyn_y_odasi | r_L1_ebeveyn_y_odasi | The room is labeled as a bedroom but contains two dining tables and multiple chairs, which are not appropriate fixtures for a bedroom. | open: a tool exists (set_room_type) but no edit was accepted |
| critical | F7 | r_L0_salon | f_L0_018 | table_coffee blocks door o_L0_006 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | F7 | r_L0_salon | f_L0_035 | ottoman blocks door o_L0_003 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | G11 | r_L0_salon | d_L0_001 | no 0.60 m walkway from door d_L0_001 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | d_L0_002 | no 0.60 m walkway from door d_L0_002 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | d_L0_004 | no 0.60 m walkway from door d_L0_004 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | o_L0_003 | no 0.60 m walkway from door o_L0_003 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | o_L0_005 | no 0.60 m walkway from door o_L0_005 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | o_L0_006 | no 0.60 m walkway from door o_L0_006 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | F7 | r_L0_mutfak | f_L0_029 | sink_kitchen blocks door o_L0_004 | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| critical | F7 | r_L0_mutfak | f_L0_040 | kitchen_counter blocks door o_L0_001 | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| critical | F7 | r_L0_mutfak | f_L0_040 | kitchen_counter blocks door d_L0_002 | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| critical | G11 | r_L0_mutfak | d_L0_002 | no 0.60 m walkway from door d_L0_002 to door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_002 | no 0.60 m walkway from door d_L0_002 to door d_L0_005 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_002 | no 0.60 m walkway from door d_L0_002 to door d_L0_007 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_002 | no 0.60 m walkway from door d_L0_002 to door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_005 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_007 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_002 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | o_L0_004 | no 0.60 m walkway from door o_L0_004 to door d_L0_005 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | o_L0_004 | no 0.60 m walkway from door o_L0_004 to door d_L0_007 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | F3 | r_L1_ebeveyn_y_odasi | f_L1_012 | bed_double: the headboard stands in the room (0.06 m off) | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | F7 | r_L1_ebeveyn_y_odasi | f_L1_017 | table_dining blocks door d_L1_001 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | F7 | r_L1_ebeveyn_y_odasi | f_L1_019 | chair blocks door d_L1_001 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | F7 | r_L1_ebeveyn_y_odasi | f_L1_021 | chair blocks door d_L1_001 | fixed in the final round (an accepted edit on its target) |
| critical | F7 | r_L1_cocuk_odasi | f_L1_007 | desk blocks door d_L1_005 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | F7 | r_L1_cocuk_odasi | f_L1_009 | bed_double blocks door o_L1_001 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | G11 | r_L1_hol | d_L1_004 | no 0.60 m walkway from door d_L1_004 to door d_L1_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_hol | d_L1_004 | no 0.60 m walkway from door d_L1_004 to door d_L1_009 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_hol | d_L1_006 | no 0.60 m walkway from door d_L1_006 to door d_L1_009 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_hol | o_L1_002 | no 0.60 m walkway from door o_L1_002 to door d_L1_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_hol | o_L1_002 | no 0.60 m walkway from door o_L1_002 to door d_L1_009 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | F7 | r_L1_oda_2 | f_L1_013 | sofa blocks door o_L1_003 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | F7 | r_L1_oda_2 | f_L1_013 | sofa blocks door o_L1_005 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | F7 | r_L1_oda_2 | f_L1_031 | floor_lamp blocks door o_L1_003 | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| critical | G11 | r_L1_oda_2 | o_L1_003 | no 0.60 m walkway from door o_L1_003 to door o_L1_005 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_oda_2 | o_L1_005 | no 0.60 m walkway from door o_L1_005 to door d_L1_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | Q5 | r_L0_salon | f_L0_007 | A folding garden chair is placed indoors in the living room, which is inappropriate for the interior setting and clashes with the other furniture. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | Q5 | r_L1_ebeveyn_y_odasi | f_L1_017 | The dining table is accompanied by a mix of different chair models (white and wooden), which do not belong together as a cohesive set. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | Q5 | r_L1_ebeveyn_y_odasi | f_L1_020 | The second dining table is accompanied by a mix of different chair models (white and wooden), which do not belong together as a cohesive set. | open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accepted |
| major | D2 | r_L0_salon | f_L0_006 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | D2 | r_L0_salon | f_L0_019 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | D2 | r_L0_salon | f_L0_022 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | D2 | r_L0_salon | f_L0_025 | The object labeled as a dining table is rendered as a small side table, which is the wrong scale and type for a dining set. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | D2 | r_L0_banyo | f_L0_047 | The washbasin model is a crude, low-poly block with a simple rectangular cutout and a floating blue knob, lacking the detail and form of a real sink. | open: a tool exists (swap_model, report_library_gap) but no edit was accepted |
| major | D1 | r_L1_oda_2 | f_L1_016 | A white object (resembling a book or tray) is floating in mid-air above the sofa cushions, not resting on the seat or a table. | open: a tool exists (swap_model) but no edit was accepted |
| major | D1 | r_L1_oda_2 | f_L1_016 | A white object is floating in mid-air above the sofa cushions, not resting on the seat or a table. | open: a tool exists (swap_model) but no edit was accepted |
| major | F8 | r_L0_salon | f_L0_009 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F8 | r_L0_salon | f_L0_018 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_008 | chair f_L0_008 overlaps chair f_L0_007 by 0.07 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_035 | ottoman f_L0_035 overlaps sofa_corner f_L0_014 by 0.15 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_036 | ottoman f_L0_036 overlaps sofa_corner f_L0_014 by 0.24 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_037 | ottoman f_L0_037 overlaps sofa_corner f_L0_014 by 0.25 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_038 | ottoman f_L0_038 overlaps sofa_corner f_L0_014 by 0.25 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | G2 | r_L0_salon | f_L0_035 | coffee table f_L0_035 is not in front of the sofa and is 0.00 m from the sofa front, needs ≥ 0.30 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_007 | chair f_L0_007: 0.12 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_008 | chair f_L0_008: 0.45 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_010 | chair f_L0_010 is 180° off the table f_L0_006 (needs ≤ 45°) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_010 | chair f_L0_010: 0.45 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_011 | chair f_L0_011: 0.45 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_020 | chair f_L0_020 is 50° off the table f_L0_019 (needs ≤ 45°) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_020 | chair f_L0_020: 0.64 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_021 | chair f_L0_021: 0.37 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_023 | chair f_L0_023 is 50° off the table f_L0_022 (needs ≤ 45°) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_023 | chair f_L0_023: 0.69 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L0_salon | f_L0_026 | chair f_L0_026 is 50° off the table f_L0_025 (needs ≤ 45°) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_014 | sofa_corner f_L0_014: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_028 | armchair f_L0_028: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F3 | r_L0_mutfak | f_L0_029 | sink_kitchen: its back is not on a wall (0.08 m off) | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | F9 | r_L0_mutfak | f_L0_039 | kitchen_counter f_L0_039 overlaps kitchen_counter f_L0_002 by 0.44 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_mutfak | f_L0_039 | kitchen_counter reaches 0.18 m² through the room outline, up to 0.175 m deep | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | F9 | r_L0_mutfak | f_L0_040 | kitchen_counter reaches 0.06 m² through the room outline, up to 0.025 m deep | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | G8 | r_L0_mutfak | f_L0_002 | kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | G8 | r_L0_mutfak | f_L0_029 | sink f_L0_029: 0.00 m of counter beside it, needs ≥ 0.46 m on one side | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | G9 | r_L0_mutfak | r_L0_mutfak | kitchen r_L0_mutfak has no fridge (fridge) | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | G9 | r_L0_mutfak | r_L0_mutfak | kitchen r_L0_mutfak has no hob (stove) | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_002 | kitchen_counter f_L0_002: its front use zone is not reached by a 0.60 m walkway from door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_029 | sink_kitchen f_L0_029: its front use zone is not reached by a 0.60 m walkway from door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_039 | kitchen_counter f_L0_039: its front use zone is not reached by a 0.60 m walkway from door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_040 | kitchen_counter f_L0_040: its front use zone is not reached by a 0.60 m walkway from door o_L0_004 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G10 | r_L0_banyo | r_L0_banyo | bathroom without a washbasin | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | F4 | r_L1_ebeveyn_y_odasi | f_L1_018 | chair does not face its group (f_L1_017) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G6 | r_L1_ebeveyn_y_odasi | f_L1_018 | chair f_L1_018 is 50° off the table f_L1_017 (needs ≤ 45°) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G6 | r_L1_ebeveyn_y_odasi | f_L1_018 | chair f_L1_018: 0.69 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G6 | r_L1_ebeveyn_y_odasi | f_L1_019 | chair f_L1_019: 0.52 m from the table edge to the wall or piece behind, needs ≥ 0.81 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_ebeveyn_y_odasi | d_L1_001 | the main walkway from the entrance door is below 0.80 m between doors d_L1_001 and d_L1_002 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_ebeveyn_y_odasi | d_L1_001 | the main walkway from the entrance door is below 0.80 m between doors d_L1_001 and d_L1_007 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_ebeveyn_y_odasi | d_L1_001 | the main walkway from the entrance door is below 0.80 m between doors d_L1_001 and o_L1_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_ebeveyn_y_odasi | d_L1_001 | the main walkway from the entrance door is below 0.80 m between doors d_L1_001 and o_L1_007 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F3 | r_L1_cocuk_odasi | f_L1_007 | desk: its back is not on a wall (0.06 m off) | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | F9 | r_L1_cocuk_odasi | f_L1_007 | desk f_L1_007 overlaps bed_double f_L1_006 by 0.07 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L1_cocuk_odasi | f_L1_010 | nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | G4 | r_L1_cocuk_odasi | f_L1_010 | nightstand f_L1_010 of bed_double f_L1_009: -0.56 m from the bed side (needs ≤ 0.30 m) | open: a tool exists (move_group, relayout_room, move_piece) but no edit was accepted |
| major | G5 | r_L1_cocuk_odasi | f_L1_006 | bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G5 | r_L1_cocuk_odasi | f_L1_009 | bed_double f_L1_009: 0.10 m free along the left side, needs ≥ 0.60 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_cocuk_odasi | f_L1_006 | bed_double f_L1_006: its right use zone is not reached by a 0.60 m walkway from door o_L1_001 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_cocuk_odasi | f_L1_009 | bed_double f_L1_009: its left use zone is not reached by a 0.60 m walkway from door o_L1_001 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_cocuk_odasi | o_L1_001 | the main walkway from the entrance door is below 0.80 m between doors o_L1_001 and d_L1_005 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G10 | r_L1_dus | r_L1_dus | bathroom without a washbasin | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | G12 | r_L1_dus | f_L1_024 | shower f_L1_024 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05) | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F6 | r_L1_oda_2 | f_L1_013 | sofa: the free zone in front of it is blocked by f_L1_031 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F3 | r_L1_banyo | f_L1_029 | washbasin: its back is not on a wall (0.07 m off) | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G10 | r_L1_banyo | r_L1_banyo | bathroom without a washbasin | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | S2 | r_L0_mutfak | f_L0_039 | kitchen_counter f_L0_039 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece) | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | S2 | r_L0_salon | f_L0_006 | table_dining f_L0_006 and chair f_L0_007 cut each other by 0.224 m (allowed 0.010 m) | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | S2 | r_L0_salon | f_L0_006 | table_dining f_L0_006 and chair f_L0_008 cut each other by 0.181 m (allowed 0.010 m) | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | NR | r_L0_salon | f_L0_012 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/cr | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L0_salon | f_L0_015 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/cr | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L0_salon | f_L0_016 | untyped drawn piece left for review: drawn piece 0.21 x 0.20 m in r_L0_salon has no type (AI passes: potted_plant, unknown): not built (plan crop recognition/cr | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L1_cocuk_odasi | f_L1_002 | untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, no | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L1_soyunma_odasi | f_L1_014 | untyped drawn piece left for review: drawn piece 2.27 x 0.85 m in r_L1_soyunma_odasi has no type (AI passes: stair, unknown): not built (plan crop recognition/c | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L1_soyunma_odasi | f_L1_015 | untyped drawn piece left for review: drawn piece 2.27 x 0.85 m in r_L1_soyunma_odasi has no type (AI passes: stair, unknown): not built (plan crop recognition/c | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L1_oda_2 | f_L1_023 | untyped drawn piece left for review: drawn piece 1.20 x 0.55 m in r_L1_oda_2 has no type (AI passes: desk, dresser): not built (plan crop recognition/crops/sym_ | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |
| major | NR | r_L1_ebeveyn_y_odasi | f_L1_026 | untyped drawn piece left for review: drawn piece 0.58 x 0.58 m in r_L1_ebeveyn_y_odasi has no type (AI passes: floor_lamp, table_coffee): not built (plan crop r | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |

## The architect's open points (no safe default; the AI architect and you decide)

- **W2 windows to the outside** (major) win_L0_001: win_L0_001 sits in the wall between r_L0_mutfak (kitchen) and r_L0_salon (living)
- **W2 windows to the outside** (major) win_L1_004: win_L1_004 sits in the wall between r_L1_soyunma_odasi (dressing) and r_L1_dus (bathroom)
- **W2 windows to the outside** (major) win_L1_005: win_L1_005 sits in the wall between r_L1_soyunma_odasi (dressing) and r_L1_dus (bathroom)
- **W2 windows to the outside** (major) win_L1_008: win_L1_008 sits in the wall between r_L1_oda_2 (living) and r_L1_hol (hall) (the architect's default answered move_window_to_outer_wall ("the safe default"), but it could not be done: r_L1_oda_2 has no outer wall with 0.97 m free for win_L1_008)
- **F2 free doorways** (minor) d_L0_002: 80% of the doorway of d_L0_002 in r_L0_mutfak is taken by f_L0_040 (the architect's default answered move_piece ("the safe default"), but it could not be done: f_L0_040: no free place within the move limit clear of d_L0_002)
- **F3 free windows** (minor) o_L1_005: f_L1_013 stand(s) in front of 100% of o_L1_005 (the architect's default answered move_piece ("the safe default"), but it could not be done: f_L1_013: no free place within the move limit clear of o_L1_005)
- **F4 room to use** (minor) f_L1_025: only 20% of the 0.5 m in front of f_L1_025 (washbasin) is free (f_L1_028 in the way)

3 vision finding(s) dropped by code (in inspector.json with the reason).
