# What the AI inspector saw on the final renders: real06

Round 4 (the final round: every room and exterior view asked again on the final renders, with the visitor checks Q1-Q9). 2 vision finding(s) (0 visitor), 0 fixed in this round, 0 handed to the stage that owns them, 68 open, 2 dropped by code; the architect leaves 1 open point(s) (0 major).

Visitor checks: Q1 a door that makes no sense; Q2 a fixture at the wrong working height; Q3 a fall risk; Q4 a room that makes no sense; Q5 pieces that repeat or do not belong together; Q6 a piece placed the wrong way; Q7 doors and windows that do not fit the house or each other; Q8 rain water that makes no sense; Q9 an entrance that makes no sense

## The 3D model, measured (every element, every floor)

M1: 14 checked, 0 failed; M2: 8 checked, 0 failed; M3: 0 checked, 0 failed; M4: 4 checked, 0 failed; M5: 7 checked, 0 failed; M6: 54 checked, 0 failed; M7: 8 checked, 0 failed; M8: 4 checked, 0 failed (M1 doors on their floors, M2 working heights, M3 guards, M4 doors into the air, M5 rain water, M6 one door and window language, M7 rooms that make sense, M8 entrances that make sense; `scene/model_review.md`).

| severity | check | where | target | what | outcome |
|---|---|---|---|---|---|
| critical | G11 | r_L0_salon | d_L0_001 | no 0.60 m walkway from door d_L0_001 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | d_L0_004 | no 0.60 m walkway from door d_L0_004 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_salon | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | F7 | r_L0_mutfak | f_L0_032 | kitchen_counter blocks door o_L0_001 | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| critical | G11 | r_L0_mutfak | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_005 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | d_L0_003 | no 0.60 m walkway from door d_L0_003 to door d_L0_007 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L0_mutfak | o_L0_001 | no 0.60 m walkway from door o_L0_001 to door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_hol | d_L1_006 | no 0.60 m walkway from door d_L1_006 to door d_L1_009 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | G11 | r_L1_hol | o_L1_002 | no 0.60 m walkway from door o_L1_002 to door d_L1_009 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| critical | X3 |  | d_L1_001 | door d_L1_001 is 3.50 m above the ground with nothing to reach it (a door into the air) | open: the facade openings come from the drawings; no agent tool |
| critical | X3 |  | d_L1_004 | door d_L1_004 is 3.50 m above the ground with nothing to reach it (a door into the air) | open: the facade openings come from the drawings; no agent tool |
| critical | X3 |  | d_L1_005 | door d_L1_005 is 3.50 m above the ground with nothing to reach it (a door into the air) | open: the facade openings come from the drawings; no agent tool |
| critical | X3 |  | d_L1_007 | door d_L1_007 is 3.50 m above the ground with nothing to reach it (a door into the air) | open: the facade openings come from the drawings; no agent tool |
| critical | X3 |  | d_L1_010 | door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air) | open: the facade openings come from the drawings; no agent tool |
| critical | X3 |  | d_L1_011 | door d_L1_011 is 3.50 m above the ground with nothing to reach it (a door into the air) | open: the facade openings come from the drawings; no agent tool |
| major | F9 | r_L0_salon | f_L0_027 | ottoman f_L0_027 overlaps sofa_corner f_L0_011 by 0.25 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_028 | ottoman f_L0_028 overlaps sofa_corner f_L0_011 by 0.25 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_029 | ottoman f_L0_029 overlaps sofa_corner f_L0_011 by 0.25 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_salon | f_L0_030 | ottoman f_L0_030 overlaps sofa_corner f_L0_011 by 0.25 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | G2 | r_L0_salon | f_L0_027 | coffee table f_L0_027 is not in front of the sofa and is 0.00 m from the sofa front, needs ≥ 0.30 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G3 | r_L0_salon | f_L0_007 | armchair f_L0_007 is 123° off the ottoman f_L0_030 (needs ≤ 30°) at 3.61 m (needs ≤ 2.50 m) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G3 | r_L0_salon | f_L0_017 | armchair f_L0_017 is 87° off the ottoman f_L0_028 (needs ≤ 30°) at 5.05 m (needs ≤ 2.50 m) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G3 | r_L0_salon | f_L0_018 | armchair f_L0_018 is 114° off the sofa_corner f_L0_011 (needs ≤ 30°) at 3.33 m (needs ≤ 2.50 m) | open: a tool exists (rotate_piece, set_front, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_007 | armchair f_L0_007: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_008 | armchair f_L0_008: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_016 | armchair f_L0_016: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_017 | armchair f_L0_017: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_018 | armchair f_L0_018: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_salon | f_L0_019 | armchair f_L0_019: its front use zone is not reached by a 0.60 m walkway from door d_L0_006 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F3 | r_L0_mutfak | f_L0_020 | sink_kitchen: its back is not on a wall (0.08 m off) | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | F9 | r_L0_mutfak | f_L0_031 | kitchen_counter f_L0_031 overlaps kitchen_counter f_L0_002 by 0.44 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L0_mutfak | f_L0_031 | kitchen_counter reaches 0.18 m² through the room outline, up to 0.175 m deep | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | F9 | r_L0_mutfak | f_L0_032 | kitchen_counter reaches 0.06 m² through the room outline, up to 0.025 m deep | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | G8 | r_L0_mutfak | f_L0_002 | kitchen aisle 0.10 m in front of kitchen_counter f_L0_002, needs ≥ 0.90 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | G8 | r_L0_mutfak | f_L0_020 | sink f_L0_020: 0.00 m of counter beside it, needs ≥ 0.46 m on one side | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | G9 | r_L0_mutfak | r_L0_mutfak | kitchen r_L0_mutfak has no fridge (fridge) | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | G9 | r_L0_mutfak | r_L0_mutfak | kitchen r_L0_mutfak has no hob (stove) | open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_002 | kitchen_counter f_L0_002: its front use zone is not reached by a 0.60 m walkway from door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_020 | sink_kitchen f_L0_020: its front use zone is not reached by a 0.60 m walkway from door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_031 | kitchen_counter f_L0_031: its front use zone is not reached by a 0.60 m walkway from door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L0_mutfak | f_L0_032 | kitchen_counter f_L0_032: its front use zone is not reached by a 0.60 m walkway from door d_L0_003 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F3 | r_L0_banyo | f_L0_026 | washbasin: its back is not on a wall (0.07 m off) | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G10 | r_L0_banyo | f_L0_026 | washbasin f_L0_026: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | F6 | r_L1_ebeveyn_y_odasi | f_L1_018 | armchair: the free zone in front of it is blocked by f_L1_022 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | F3 | r_L1_cocuk_odasi | f_L1_007 | desk: its back is not on a wall (0.06 m off) | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | F9 | r_L1_cocuk_odasi | f_L1_007 | desk f_L1_007 overlaps bed_double f_L1_006 by 0.07 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F9 | r_L1_cocuk_odasi | f_L1_010 | nightstand f_L1_010 overlaps bed_double f_L1_009 by 0.17 m² | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | G4 | r_L1_cocuk_odasi | f_L1_010 | nightstand f_L1_010 of bed_double f_L1_009: -0.56 m from the bed side (needs ≤ 0.30 m) | open: a tool exists (move_group, relayout_room, move_piece) but no edit was accepted |
| major | G5 | r_L1_cocuk_odasi | f_L1_006 | bed_double f_L1_006: 0.10 m free along the right side, needs ≥ 0.60 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G5 | r_L1_cocuk_odasi | f_L1_009 | bed_double f_L1_009: 0.10 m free along the left side, needs ≥ 0.60 m | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_cocuk_odasi | f_L1_006 | bed_double f_L1_006: its right use zone is not reached by a 0.60 m walkway from door d_L1_008 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G11 | r_L1_cocuk_odasi | f_L1_009 | bed_double f_L1_009: its left use zone is not reached by a 0.60 m walkway from door d_L1_008 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G12 | r_L1_dus | f_L1_020 | shower f_L1_020 (2.00 m) stands in front of window win_L1_011 (sill 0.90 m + 0.05) | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F6 | r_L1_oda_2 | f_L1_013 | sofa: the free zone in front of it is blocked by f_L1_027 | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G12 | r_L1_oda_2 | f_L1_027 | floor_lamp f_L1_027 (1.60 m) stands in front of window o_L1_003 (sill 0.90 m + 0.05) | open: a tool exists (move_piece, move_group, fix_fixture) but no edit was accepted |
| major | F3 | r_L1_banyo | f_L1_025 | washbasin: its back is not on a wall (0.07 m off) | open: a tool exists (move_piece, move_group, relayout_room) but no edit was accepted |
| major | G10 | r_L1_banyo | f_L1_021 | washbasin f_L1_021: 0.11 m clear in front, needs ≥ 0.53 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | G10 | r_L1_banyo | f_L1_021 | washbasin f_L1_021: centre 0.30 m from the side wall on its left, needs ≥ 0.38 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | G10 | r_L1_banyo | f_L1_024 | toilet f_L1_024: centre 0.33 m from the side wall or fixture on its right, needs ≥ 0.38 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | G10 | r_L1_banyo | f_L1_025 | washbasin f_L1_025: centre 0.31 m from the side wall on its left, needs ≥ 0.38 m | open: a tool exists (fix_fixture) but no edit was accepted |
| major | L2 |  | d_L1_001 | door d_L1_001 is 3.50 m above the ground with no steps or ramp: a door into the air (an outside stair, or no entrance); on an upper floor (a French balcony?) | open: a tool exists (set_entrance, set_ground_point) but no edit was accepted |
| major | L2 |  | d_L1_004 | door d_L1_004 is 3.50 m above the ground with no steps or ramp: a door into the air (an outside stair, or no entrance); on an upper floor (a French balcony?) | open: a tool exists (set_entrance, set_ground_point) but no edit was accepted |
| major | L2 |  | d_L1_005 | door d_L1_005 is 3.50 m above the ground with no steps or ramp: a door into the air (an outside stair, or no entrance); on an upper floor (a French balcony?) | open: a tool exists (set_entrance, set_ground_point) but no edit was accepted |
| major | L2 |  | d_L1_007 | door d_L1_007 is 3.50 m above the ground with no steps or ramp: a door into the air (an outside stair, or no entrance); on an upper floor (a French balcony?) | open: a tool exists (set_entrance, set_ground_point) but no edit was accepted |
| major | L2 |  | d_L1_010 | door d_L1_010 is 3.50 m above the ground with no steps or ramp: a door into the air (an outside stair, or no entrance); on an upper floor (a French balcony?) | open: a tool exists (set_entrance, set_ground_point) but no edit was accepted |
| major | L2 |  | d_L1_011 | door d_L1_011 is 3.50 m above the ground with no steps or ramp: a door into the air (an outside stair, or no entrance); on an upper floor (a French balcony?) | open: a tool exists (set_entrance, set_ground_point) but no edit was accepted |
| major | S2 | r_L0_mutfak | f_L0_031 | kitchen_counter f_L0_031 cuts wall w_L0_024 by 0.075 m (allowed 0.030 m for a fixture piece) | open: the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall,  |
| major | NR | r_L1_cocuk_odasi | f_L1_002 | untyped drawn piece left for review: drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, no | open: a tool exists (retype_piece, mark_not_furniture) but no edit was accepted |

## The architect's open points (no safe default; the AI architect and you decide)

- **F4 room to use** (minor) f_L1_021: only 20% of the 0.5 m in front of f_L1_021 (washbasin) is free (f_L1_024 in the way)

2 vision finding(s) dropped by code (in inspector.json with the reason).
