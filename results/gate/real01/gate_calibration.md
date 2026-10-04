# Change-gate calibration: real01

7 calibration views; benign 53/56 accepted (rate 0.9464); negatives 97/101 rejected (rate 0.9604, small negatives 0.9333); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 88.3 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 7 | 5 | 2 | 0.7143 |
| benign | exposure | -0.3 | 7 | 7 | 0 | 1 |
| benign | exposure | 0.3 | 7 | 7 | 0 | 1 |
| benign | jpeg | 75 | 7 | 7 | 0 | 1 |
| benign | local_contrast | 1.5 | 7 | 7 | 0 | 1 |
| benign | noise | 3 | 7 | 6 | 1 | 0.8571 |
| benign | unsharp | 0.5 | 7 | 7 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 7 | 7 | 0 | 1 |
| negative | erase | - | 8 | 0 | 8 | 1 |
| negative | floor_L | -15 | 6 | 2 | 4 | 0.6667 |
| negative | insertion | - | 5 | 0 | 5 | 1 |
| negative | paste | 0.75 | 2 | 0 | 2 | 1 |
| negative | paste | 1 | 5 | 0 | 5 | 1 |
| negative | removal | - | 5 | 0 | 5 | 1 |
| negative | rotate | 2 | 8 | 0 | 8 | 1 |
| negative | scale | 1.04 | 8 | 0 | 8 | 1 |
| negative | scale | 1.08 | 8 | 0 | 8 | 1 |
| negative | scale | 1.15 | 8 | 0 | 8 | 1 |
| negative | shift | 12 | 8 | 1 | 7 | 0.875 |
| negative | shift | 25 | 8 | 0 | 8 | 1 |
| negative | shift | 6 | 8 | 0 | 8 | 1 |
| negative | wall_b | 10 | 7 | 0 | 7 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 7 | 1 | 6 | 0.8571 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9638 | 0.9994 | 0.9994 | no | - | - | 1 | 0.7973 |
| edges | region_min | >= | yes | 0.87 | 0.844 | 0.9906 | 0.9935 | no | - | - | 0.9643 | 0.9459 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0 | no | - | - | 1 | 0.9167 |
| depth | global_max | <= | yes | 0.05 | 0.00925 | 0.00076 | 0.00076 | no | - | - | 1 | 0.0988 |
| depth | region_max | <= | yes | 0.14 | 0.01651 | 0.00119 | 0.00119 | no | - | - | 1 | 0.0988 |
| masks | region_min | >= | yes | 0.62 | 0.1387 | 0.9941 | 0.9941 | no | - | - | 0.9821 | 0.1216 |
| colour | global_max | <= | yes | 7.5 | 6.007 | 0.1711 | 0.1711 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.637 | 0 | 0 | no | - | - | 1 | 0.65 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.397 | 6.547 | 6.547 | yes | 2.684 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8327 | 0.9769 | 0.9905 | no | - | - | 1 | 0.321 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught erase, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:25, shift:6; missed insertion, removal, shift:12; proposed_partial 0.8375
- added_lines.region_max_len_frac: caught paste:0.75, paste:1.0; missed insertion
- depth.global_max: caught insertion, paste:1.0, removal, scale:1.15; missed erase, paste:0.75, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- depth.region_max: caught erase, insertion, paste:1.0, removal; missed paste:0.75, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.255
- colour.region_max: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed floor_L:-15.0; proposed_partial 6.829
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal, scale:1.15; missed insertion, paste:0.75, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 25 px (rejection rate by px: {"6": 1.0, "12": 0.875, "25": 1.0})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L0_bed_room_3 blur:1.0: edges win_L0_001 0.852 >= 0.87
- cam_r_L0_bed_room_3 noise:3.0: masks f_L0_007 0.1387 >= 0.62
- cam_r_L0_kitchen_1 blur:1.0: edges win_L0_006 0.844 >= 0.87

## Negative controls accepted

- cam_r_L0_drawing_room_1 shift:12 on win_L0_002
- cam_r_L0_bed_room_2_3 floor_L:-15.0 on struct:floor
- cam_r_L0_bed_room_3 floor_L:-15.0 on struct:floor
- cam_r_L0_kitchen_1 white_balance_strong:1.15,1,0.85 on view

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- cam_r_L0_bath_toilet_1 floor_L: no floor region

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9638 vs best small negative 0.9994; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.844 vs best small negative 0.9906; no proposal; misses insertion, removal, shift:12; on the small negatives it catches (rotate:2.0, scale:1.04, scale:1.08, shift:6) a threshold of 0.8375 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac does not separate every gross negative: worst benign 0 vs best gross negative 0; no proposal; misses insertion
- depth.global_max does not separate every small negative: worst benign 0.00925 vs best small negative 0.00076; no proposal; misses erase, paste:0.75, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.01651 vs best small negative 0.00119; no proposal; misses paste:0.75, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.1387 vs best small negative 0.9941; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 6.007 vs best small negative 0.1711; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.255 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 6.637 vs best small negative 0; no proposal; misses floor_L:-15.0; on the small negatives it catches (wall_b:10.0, white_balance_strong:1.15,1,0.85) a threshold of 6.829 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma separates: worst benign 1.397 vs best small negative 6.547; proposed 2.684 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8327 vs best small negative 0.9769; no proposal; misses insertion, paste:0.75, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- benign blur:1.0 on cam_r_L0_bed_room_3 rejected: edges win_L0_001 0.852 (limit >= 0.87)
- benign noise:3.0 on cam_r_L0_bed_room_3 rejected: masks f_L0_007 0.1387 (limit >= 0.62)
- benign blur:1.0 on cam_r_L0_kitchen_1 rejected: edges win_L0_006 0.844 (limit >= 0.87)
- negative shift:12 on win_L0_002 (cam_r_L0_drawing_room_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_bed_room_2_3) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_bed_room_3) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_kitchen_1) accepted

## Warnings

- cam_r_L0_bath_toilet_1: no required element; no object negatives
- cam_r_L0_room_1: no required element; no object negatives
- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
