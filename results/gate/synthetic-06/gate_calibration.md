# Change-gate calibration: synthetic-06

6 calibration views; benign 46/48 accepted (rate 0.9583); negatives 70/72 rejected (rate 0.9722, small negatives 0.9535); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 44.7 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 6 | 5 | 1 | 0.8333 |
| benign | exposure | -0.3 | 6 | 6 | 0 | 1 |
| benign | exposure | 0.3 | 6 | 6 | 0 | 1 |
| benign | jpeg | 75 | 6 | 5 | 1 | 0.8333 |
| benign | local_contrast | 1.5 | 6 | 6 | 0 | 1 |
| benign | noise | 3 | 6 | 6 | 0 | 1 |
| benign | unsharp | 0.5 | 6 | 6 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 6 | 6 | 0 | 1 |
| negative | erase | - | 5 | 0 | 5 | 1 |
| negative | floor_L | -15 | 6 | 1 | 5 | 0.8333 |
| negative | insertion | - | 4 | 0 | 4 | 1 |
| negative | paste | 0.75 | 2 | 0 | 2 | 1 |
| negative | paste | 1 | 4 | 0 | 4 | 1 |
| negative | removal | - | 4 | 0 | 4 | 1 |
| negative | rotate | 2 | 5 | 0 | 5 | 1 |
| negative | scale | 1.04 | 5 | 0 | 5 | 1 |
| negative | scale | 1.08 | 5 | 0 | 5 | 1 |
| negative | scale | 1.15 | 5 | 0 | 5 | 1 |
| negative | shift | 12 | 5 | 0 | 5 | 1 |
| negative | shift | 25 | 5 | 0 | 5 | 1 |
| negative | shift | 6 | 5 | 0 | 5 | 1 |
| negative | wall_b | 10 | 6 | 0 | 6 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 6 | 1 | 5 | 0.8333 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.983 | 0.9725 | 0.9912 | yes | 0.9804 | no | 1 | 0.9167 |
| edges | region_min | >= | yes | 0.87 | 0.8276 | 0.9832 | 0.9987 | no | - | - | 0.9792 | 0.8958 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0 | no | - | - | 1 | 0.9 |
| depth | global_max | <= | yes | 0.05 | 0.01208 | 0.00108 | 0.00108 | no | - | - | 1 | 0.1296 |
| depth | region_max | <= | yes | 0.14 | 0.09511 | 0.00245 | 0.00167 | no | - | - | 1 | 0.1111 |
| masks | region_min | >= | yes | 0.62 | 0.0168 | 0.999 | 0.999 | no | - | - | 0.9792 | 0.0833 |
| colour | global_max | <= | yes | 7.5 | 5.876 | 0.0313 | 0.0313 | no | - | - | 1 | 0.1111 |
| colour | region_max | <= | yes | 8 | 6.389 | 0 | 0 | no | - | - | 1 | 0.6667 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.43 | 7.106 | 7.106 | yes | 2.849 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8425 | 0.9704 | 0.99 | no | - | - | 1 | 0.3333 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed insertion
- edges.region_min: caught erase, removal, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed insertion, rotate:2.0, scale:1.04; proposed_partial 0.8259
- added_lines.region_max_len_frac: caught paste:0.75, paste:1.0; missed insertion
- depth.global_max: caught paste:0.75, paste:1.0; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught paste:1.0; missed erase, insertion, paste:0.75, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.064
- colour.region_max: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed floor_L:-15.0; proposed_partial 6.649
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal, scale:1.08, scale:1.15; missed insertion, paste:0.75, paste:1.0, rotate:2.0, scale:1.04, shift:12, shift:25, shift:6; proposed_partial 0.8408

## Smallest detected change

- shift: 6 px (rejection rate by px: {"6": 1.0, "12": 1.0, "25": 1.0})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L0_living_room_1 blur:1.0: edges win_L0_007 0.8276 >= 0.87
- cam_r_L0_bed_room_1 jpeg:75: masks f_L0_013 0.0168 >= 0.62

## Negative controls accepted

- cam_r_L0_bath_1 floor_L:-15.0 on struct:floor
- cam_r_L0_kitchen_1 white_balance_strong:1.15,1,0.85 on view

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min separates: worst benign 0.983 vs best small negative 0.9725; proposed 0.9804 (current 0.935)
- edges.region_min does not separate every small negative: worst benign 0.8276 vs best small negative 0.9832; no proposal; misses insertion, rotate:2.0, scale:1.04; on the small negatives it catches (scale:1.08, shift:12, shift:6) a threshold of 0.8259 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac does not separate every gross negative: worst benign 0 vs best gross negative 0; no proposal; misses insertion
- depth.global_max does not separate every small negative: worst benign 0.01208 vs best small negative 0.00108; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.09511 vs best small negative 0.00245; no proposal; misses erase, insertion, paste:0.75, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.0168 vs best small negative 0.999; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.876 vs best small negative 0.0313; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.064 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 6.389 vs best small negative 0; no proposal; misses floor_L:-15.0; on the small negatives it catches (wall_b:10.0, white_balance_strong:1.15,1,0.85) a threshold of 6.649 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma separates: worst benign 1.43 vs best small negative 7.106; proposed 2.849 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8425 vs best small negative 0.9704; no proposal; misses insertion, paste:0.75, paste:1.0, rotate:2.0, scale:1.04, shift:12, shift:25, shift:6; on the small negatives it catches (scale:1.08) a threshold of 0.8408 would sit 25 % into the gap (proposed_partial)
- benign blur:1.0 on cam_r_L0_living_room_1 rejected: edges win_L0_007 0.8276 (limit >= 0.87)
- benign jpeg:75 on cam_r_L0_bed_room_1 rejected: masks f_L0_013 0.0168 (limit >= 0.62)
- negative floor_L:-15.0 on struct:floor (cam_r_L0_bath_1) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_kitchen_1) accepted

## Warnings

- cam_r_L0_bath_1: no required element; no object negatives
- cam_r_L0_kitchen_1: no required element; no object negatives
- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
