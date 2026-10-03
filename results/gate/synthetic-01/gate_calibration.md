# Change-gate calibration: synthetic-01

8 calibration views; benign 62/64 accepted (rate 0.9688); negatives 160/166 rejected (rate 0.9639, small negatives 0.9596); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 143.8 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 7 | 1 | 0.875 |
| benign | exposure | -0.3 | 8 | 8 | 0 | 1 |
| benign | exposure | 0.3 | 8 | 8 | 0 | 1 |
| benign | jpeg | 75 | 8 | 8 | 0 | 1 |
| benign | local_contrast | 1.5 | 8 | 7 | 1 | 0.875 |
| benign | noise | 3 | 8 | 8 | 0 | 1 |
| benign | unsharp | 0.5 | 8 | 8 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 15 | 1 | 14 | 0.9333 |
| negative | floor_L | -15 | 8 | 0 | 8 | 1 |
| negative | insertion | - | 7 | 1 | 6 | 0.8571 |
| negative | paste | 0.4355 | 1 | 0 | 1 | 1 |
| negative | paste | 0.6532 | 1 | 0 | 1 | 1 |
| negative | paste | 0.8477 | 1 | 0 | 1 | 1 |
| negative | paste | 0.871 | 5 | 0 | 5 | 1 |
| negative | removal | - | 7 | 0 | 7 | 1 |
| negative | rotate | 2 | 15 | 1 | 14 | 0.9333 |
| negative | scale | 1.04 | 15 | 0 | 15 | 1 |
| negative | scale | 1.08 | 15 | 0 | 15 | 1 |
| negative | scale | 1.15 | 15 | 0 | 15 | 1 |
| negative | shift | 12 | 15 | 1 | 14 | 0.9333 |
| negative | shift | 25 | 15 | 0 | 15 | 1 |
| negative | shift | 6 | 15 | 1 | 14 | 0.9333 |
| negative | wall_b | 10 | 8 | 0 | 8 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 1 | 7 | 0.875 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.8926 | 0.9998 | 0.9999 | no | - | - | 0.9844 | 0.7463 |
| edges | region_min | >= | yes | 0.87 | 0.7543 | 0.9976 | 1 | no | - | - | 0.9844 | 0.9179 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0 | no | - | - | 1 | 0.8667 |
| depth | global_max | <= | yes | 0.05 | 0.02765 | 0.00057 | 0.00057 | no | - | - | 1 | 0.0282 |
| depth | region_max | <= | yes | 0.14 | 0.1938 | 0.00129 | 0.00129 | no | - | - | 0.9844 | 0.0915 |
| masks | region_min | >= | yes | 0.62 | 0.9182 | 0.9995 | 0.9997 | no | - | - | 1 | 0.1119 |
| colour | global_max | <= | yes | 7.5 | 6.397 | 0.3226 | 0.3226 | no | - | - | 1 | 0.2083 |
| colour | region_max | <= | yes | 8 | 7.168 | 7.636 | 7.636 | yes | 7.285 | no | 1 | 0.9583 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.635 | 7.939 | 7.939 | yes | 3.211 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8404 | 0.9722 | 0.9977 | no | - | - | 1 | 0.3028 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught removal, scale:1.15; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac: caught paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871; missed insertion
- depth.global_max: caught -; missed erase, insertion, paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.428
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 25 px (rejection rate by px: {"6": 0.9333, "12": 0.9333, "25": 1.0})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L0_banyo_1 local_contrast:1.5: depth f_L0_011 0.1938 <= 0.14
- cam_r_L1_banyo_3 blur:1.0: edges global 0.8926 >= 0.935; edges f_L1_012 0.7543 >= 0.87

## Negative controls accepted

- cam_r_L1_ebeveyn_yatak_odasi_1 shift:6 on win_L1_003
- cam_r_L1_ebeveyn_yatak_odasi_1 shift:12 on win_L1_003
- cam_r_L1_ebeveyn_yatak_odasi_1 erase on win_L1_003
- cam_r_L0_yatak_odasi_3 rotate:2.0 on f_L0_007
- cam_r_L0_mutfak_1 white_balance_strong:1.15,1,0.85 on view
- cam_r_L1_banyo_1 insertion on f_L1_013

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.8926 vs best small negative 0.9998; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.7543 vs best small negative 0.9976; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac does not separate every gross negative: worst benign 0 vs best gross negative 0; no proposal; misses insertion
- depth.global_max does not separate every small negative: worst benign 0.02765 vs best small negative 0.00057; no proposal; misses erase, insertion, paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.1938 vs best small negative 0.00129; no proposal; misses erase, insertion, paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.9182 vs best small negative 0.9995; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 6.397 vs best small negative 0.3226; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.428 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 7.168 vs best small negative 7.636; proposed 7.285 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.635 vs best small negative 7.939; proposed 3.211 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8404 vs best small negative 0.9722; no proposal; misses insertion, paste:0.4355, paste:0.6532, paste:0.8477, paste:0.871, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign local_contrast:1.5 on cam_r_L0_banyo_1 rejected: depth f_L0_011 0.19384 (limit <= 0.14)
- benign blur:1.0 on cam_r_L1_banyo_3 rejected: edges global 0.8926 (limit >= 0.935); edges f_L1_012 0.7543 (limit >= 0.87)
- negative shift:6 on win_L1_003 (cam_r_L1_ebeveyn_yatak_odasi_1) accepted
- negative shift:12 on win_L1_003 (cam_r_L1_ebeveyn_yatak_odasi_1) accepted
- negative erase on win_L1_003 (cam_r_L1_ebeveyn_yatak_odasi_1) accepted
- negative rotate:2.0 on f_L0_007 (cam_r_L0_yatak_odasi_3) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_mutfak_1) accepted
- negative insertion on f_L1_013 (cam_r_L1_banyo_1) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
