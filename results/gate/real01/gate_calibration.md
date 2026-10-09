# Change-gate calibration: real01

7 calibration views (rooms); benign 54/56 accepted (rate 0.9643); negatives 109/114 rejected (rate 0.9561, small negatives 0.9242); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 58.3 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Exterior views

The project rendered no exterior view.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 7 | 6 | 1 | 0.8571 |
| benign | exposure | -0.3 | 7 | 7 | 0 | 1 |
| benign | exposure | 0.3 | 7 | 6 | 1 | 0.8571 |
| benign | jpeg | 75 | 7 | 7 | 0 | 1 |
| benign | local_contrast | 1.5 | 7 | 7 | 0 | 1 |
| benign | noise | 3 | 7 | 7 | 0 | 1 |
| benign | unsharp | 0.5 | 7 | 7 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 7 | 7 | 0 | 1 |
| negative | erase | - | 9 | 0 | 9 | 1 |
| negative | floor_L | -15 | 7 | 1 | 6 | 0.8571 |
| negative | insertion | - | 7 | 0 | 7 | 1 |
| negative | paste | 1 | 7 | 0 | 7 | 1 |
| negative | removal | - | 7 | 0 | 7 | 1 |
| negative | rotate | 2 | 9 | 1 | 8 | 0.8889 |
| negative | scale | 1.04 | 9 | 1 | 8 | 0.8889 |
| negative | scale | 1.08 | 9 | 1 | 8 | 0.8889 |
| negative | scale | 1.15 | 9 | 0 | 9 | 1 |
| negative | shift | 12 | 9 | 0 | 9 | 1 |
| negative | shift | 25 | 9 | 0 | 9 | 1 |
| negative | shift | 6 | 9 | 0 | 9 | 1 |
| negative | wall_b | 10 | 7 | 0 | 7 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 7 | 1 | 6 | 0.8571 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9874 | 0.9989 | 0.9991 | no | - | - | 1 | 0.6512 |
| edges | region_min | >= | yes | 0.87 | 0.8136 | 0.9875 | 0.9927 | no | - | - | 0.9643 | 0.8953 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.048 | yes | 0.012 | no | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.0193 | 0.0005 | 0.0005 | no | - | - | 1 | 0.0645 |
| depth | region_max | <= | yes | 0.14 | 0.1183 | 0.0012 | 0.0012 | no | - | - | 1 | 0.0538 |
| masks | region_min | >= | yes | 0.62 | 0.6269 | 0.9693 | 0.9838 | no | - | - | 1 | 0.186 |
| colour | global_max | <= | yes | 7.5 | 5.725 | 0.113 | 0.113 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.964 | 0 | 0 | no | - | - | 1 | 0.6667 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.467 | 6.851 | 6.851 | yes | 2.813 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8974 | 0.9736 | 0.991 | no | - | - | 1 | 0.3763 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, insertion, removal, shift:25; missed rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:6
- edges.region_min: caught erase, shift:25; missed insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:6
- added_lines.region_max_len_frac: caught insertion, paste:1.0; missed -
- depth.global_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 5.766
- colour.region_max: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed floor_L:-15.0; proposed_partial 7.077
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 6 px (rejection rate by px: {"6": 1.0, "12": 1.0, "25": 1.0})
- scale: x1.15 (rejection rate by factor: {"1.04": 0.8889, "1.08": 0.8889, "1.15": 1.0})

## Benign controls rejected

- cam_r_L0_drawing_room_2 blur:1.0: edges win_L0_002 0.8562 >= 0.87
- cam_r_L0_dining_2 exposure:0.3: edges win_L0_005 0.8136 >= 0.87; edges dec_L0_032 0.8693 >= 0.87

## Negative controls accepted

- cam_r_L0_drawing_room_2 scale:1.04 on win_L0_002
- cam_r_L0_drawing_room_2 scale:1.08 on win_L0_002
- cam_r_L0_drawing_room_2 floor_L:-15.0 on struct:floor
- cam_r_L0_bed_room_2 rotate:2.0 on f_L0_009
- cam_r_L0_bath_toilet_1 white_balance_strong:1.15,1,0.85 on view

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9874 vs best small negative 0.9989; no proposal; misses rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:6
- edges.region_min does not separate every small negative: worst benign 0.8136 vs best small negative 0.9875; no proposal; misses insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:6
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.048; proposed 0.012 (current 0.04)
- depth.global_max does not separate every small negative: worst benign 0.0193 vs best small negative 0.0005; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.1183 vs best small negative 0.0012; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.6269 vs best small negative 0.9693; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.725 vs best small negative 0.113; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 5.766 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 6.964 vs best small negative 0; no proposal; misses floor_L:-15.0; on the small negatives it catches (wall_b:10.0, white_balance_strong:1.15,1,0.85) a threshold of 7.077 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma separates: worst benign 1.467 vs best small negative 6.851; proposed 2.813 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8974 vs best small negative 0.9736; no proposal; misses insertion, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign blur:1.0 on cam_r_L0_drawing_room_2 rejected: edges win_L0_002 0.8562 (limit >= 0.87)
- benign exposure:0.3 on cam_r_L0_dining_2 rejected: edges win_L0_005 0.8136 (limit >= 0.87); edges dec_L0_032 0.8693 (limit >= 0.87)
- negative scale:1.04 on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative scale:1.08 on win_L0_002 (cam_r_L0_drawing_room_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_drawing_room_2) accepted
- negative rotate:2.0 on f_L0_009 (cam_r_L0_bed_room_2) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_bath_toilet_1) accepted

## Warnings

- cam_r_L0_bath_toilet_1: no required element; no object negatives
- cam_r_L0_room_1: no required element; no object negatives
- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
