# Change-gate calibration: real01

7 calibration views; benign 56/56 accepted (rate 1); negatives 92/106 rejected (rate 0.8679, small negatives 0.8197); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 113.9 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 7 | 7 | 0 | 1 |
| benign | exposure | -0.3 | 7 | 7 | 0 | 1 |
| benign | exposure | 0.3 | 7 | 7 | 0 | 1 |
| benign | jpeg | 75 | 7 | 7 | 0 | 1 |
| benign | local_contrast | 1.5 | 7 | 7 | 0 | 1 |
| benign | noise | 3 | 7 | 7 | 0 | 1 |
| benign | unsharp | 0.5 | 7 | 7 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 7 | 7 | 0 | 1 |
| negative | erase | - | 8 | 1 | 7 | 0.875 |
| negative | floor_L | -15 | 7 | 0 | 7 | 1 |
| negative | insertion | - | 7 | 0 | 7 | 1 |
| negative | paste | 1 | 7 | 0 | 7 | 1 |
| negative | removal | - | 7 | 0 | 7 | 1 |
| negative | rotate | 2 | 8 | 1 | 7 | 0.875 |
| negative | scale | 1.04 | 8 | 3 | 5 | 0.625 |
| negative | scale | 1.08 | 8 | 0 | 8 | 1 |
| negative | scale | 1.15 | 8 | 0 | 8 | 1 |
| negative | shift | 12 | 8 | 3 | 5 | 0.625 |
| negative | shift | 25 | 8 | 2 | 6 | 0.75 |
| negative | shift | 6 | 8 | 2 | 6 | 0.75 |
| negative | wall_b | 10 | 7 | 0 | 7 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 7 | 2 | 5 | 0.7143 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9855 | 1 | 1 | no | - | - | 1 | 0.6154 |
| edges | region_min | >= | yes | 0.87 | 0.9706 | 1 | 1 | no | - | - | 1 | 0.6795 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0 | no | - | - | 1 | 0.9286 |
| depth | global_max | <= | yes | 0.05 | 0.01133 | 0.00048 | 0.00048 | no | - | - | 1 | 0.0941 |
| depth | region_max | <= | yes | 0.14 | 0.0508 | 0.00071 | 0.00071 | no | - | - | 1 | 0.0353 |
| masks | region_min | >= | yes | 0.62 | 0.6596 | 0.9902 | 0.9921 | no | - | - | 1 | 0.141 |
| colour | global_max | <= | yes | 7.5 | 5.648 | 0.3973 | 0.3973 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.935 | 7.444 | 7.444 | yes | 7.062 | no | 1 | 0.6667 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.458 | 6.842 | 6.842 | yes | 2.804 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8518 | 0.9755 | 0.987 | no | - | - | 1 | 0.3647 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac: caught paste:1.0; missed insertion
- depth.global_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 5.884
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal, scale:1.08, scale:1.15; missed insertion, paste:1.0, rotate:2.0, scale:1.04, shift:12, shift:25, shift:6; proposed_partial 0.8487

## Smallest detected change

- shift: - px (rejection rate by px: {"6": 0.75, "12": 0.625, "25": 0.75})
- scale: x1.08 (rejection rate by factor: {"1.04": 0.625, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- none

## Negative controls accepted

- cam_r_L0_drawing_room_2 shift:6 on win_L0_002
- cam_r_L0_drawing_room_2 shift:12 on win_L0_002
- cam_r_L0_drawing_room_2 scale:1.04 on win_L0_002
- cam_r_L0_drawing_room_2 rotate:2.0 on win_L0_002
- cam_r_L0_drawing_room_2 erase on win_L0_002
- cam_r_L0_bed_room_2 shift:6 on win_L0_001
- cam_r_L0_bed_room_2 shift:12 on win_L0_001
- cam_r_L0_bed_room_2 shift:25 on win_L0_001
- cam_r_L0_bed_room_2 scale:1.04 on win_L0_001
- cam_r_L0_bed_room_2_2 shift:12 on win_L0_004
- cam_r_L0_bed_room_2_2 shift:25 on win_L0_004
- cam_r_L0_bed_room_2_2 scale:1.04 on win_L0_004
- cam_r_L0_kitchen_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_bath_toilet_1 white_balance_strong:1.15,1,0.85 on view

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9855 vs best small negative 1; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.9706 vs best small negative 1; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac does not separate every gross negative: worst benign 0 vs best gross negative 0; no proposal; misses insertion
- depth.global_max does not separate every small negative: worst benign 0.01133 vs best small negative 0.00048; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.0508 vs best small negative 0.00071; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.6596 vs best small negative 0.9902; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.648 vs best small negative 0.3973; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 5.884 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 6.935 vs best small negative 7.444; proposed 7.062 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.458 vs best small negative 6.842; proposed 2.804 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8518 vs best small negative 0.9755; no proposal; misses insertion, paste:1.0, rotate:2.0, scale:1.04, shift:12, shift:25, shift:6; on the small negatives it catches (scale:1.08) a threshold of 0.8487 would sit 25 % into the gap (proposed_partial)
- negative shift:6 on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative shift:12 on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative scale:1.04 on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative rotate:2.0 on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative erase on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative shift:6 on win_L0_001 (cam_r_L0_bed_room_2) accepted
- negative shift:12 on win_L0_001 (cam_r_L0_bed_room_2) accepted
- negative shift:25 on win_L0_001 (cam_r_L0_bed_room_2) accepted
- negative scale:1.04 on win_L0_001 (cam_r_L0_bed_room_2) accepted
- negative shift:12 on win_L0_004 (cam_r_L0_bed_room_2_2) accepted
- negative shift:25 on win_L0_004 (cam_r_L0_bed_room_2_2) accepted
- negative scale:1.04 on win_L0_004 (cam_r_L0_bed_room_2_2) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_kitchen_2) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_bath_toilet_1) accepted

## Warnings

- cam_r_L0_bath_toilet_1: no required element; no object negatives
- cam_r_L0_dining_1: no required element; no object negatives
- cam_r_L0_room_1: no required element; no object negatives
- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
