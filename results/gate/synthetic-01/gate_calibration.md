# Change-gate calibration: synthetic-01

8 calibration views; benign 60/64 accepted (rate 0.9375); negatives 172/176 rejected (rate 0.9773, small negatives 0.9615); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 82.2 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 8 | 0 | 1 |
| benign | exposure | -0.3 | 8 | 7 | 1 | 0.875 |
| benign | exposure | 0.3 | 8 | 8 | 0 | 1 |
| benign | jpeg | 75 | 8 | 7 | 1 | 0.875 |
| benign | local_contrast | 1.5 | 8 | 8 | 0 | 1 |
| benign | noise | 3 | 8 | 7 | 1 | 0.875 |
| benign | unsharp | 0.5 | 8 | 7 | 1 | 0.875 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 8 | 0 | 8 | 1 |
| negative | insertion | - | 8 | 0 | 8 | 1 |
| negative | paste | 0.9818 | 1 | 0 | 1 | 1 |
| negative | paste | 1 | 7 | 0 | 7 | 1 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.04 | 16 | 0 | 16 | 1 |
| negative | scale | 1.08 | 16 | 0 | 16 | 1 |
| negative | scale | 1.15 | 16 | 0 | 16 | 1 |
| negative | shift | 12 | 16 | 0 | 16 | 1 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 1 | 15 | 0.9375 |
| negative | wall_b | 10 | 8 | 0 | 8 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 2 | 6 | 0.75 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9711 | 0.9971 | 1 | no | - | - | 1 | 0.6736 |
| edges | region_min | >= | yes | 0.87 | 0.8076 | 0.971 | 1 | no | - | - | 0.9531 | 0.9583 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.2684 | yes | 0.0671 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.06056 | 0.00086 | 0.00086 | no | - | - | 0.9844 | 0.0395 |
| depth | region_max | <= | yes | 0.14 | 0.3837 | 0.00162 | 0.00162 | no | - | - | 0.9844 | 0.0592 |
| masks | region_min | >= | yes | 0.62 | 0.3557 | 0.9991 | 0.9991 | no | - | - | 0.9844 | 0.1736 |
| colour | global_max | <= | yes | 7.5 | 5.787 | 0.5387 | 0.5387 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.634 | 7.367 | 7.367 | yes | 6.817 | no | 1 | 0.75 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.381 | 7.131 | 7.131 | yes | 2.818 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8441 | 0.975 | 0.996 | no | - | - | 1 | 0.3355 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught erase, removal, scale:1.15, shift:25; missed insertion, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:6
- added_lines.region_max_len_frac: caught insertion, paste:0.9818, paste:1.0; missed -
- depth.global_max: caught -; missed erase, insertion, paste:0.9818, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.9818, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.003
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:0.9818, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 12 px (rejection rate by px: {"6": 0.9375, "12": 1.0, "25": 1.0})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L0_salon_1 exposure:-0.3: edges win_L0_004 0.8326 >= 0.87
- cam_r_L0_yatak_odasi_1 unsharp:0.5: edges win_L0_003 0.8076 >= 0.87; masks f_L0_009 0.3557 >= 0.62
- cam_r_L0_yatak_odasi_1 noise:3.0: edges win_L0_003 0.8438 >= 0.87
- cam_r_L1_banyo_1 jpeg:75: depth global 0.06056 <= 0.05; depth f_L1_015 0.3837 <= 0.14

## Negative controls accepted

- cam_r_L0_banyo_1 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_mutfak_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_salon_1 rotate:2.0 on f_L0_005
- cam_r_L1_cocuk_odasi_1 shift:6 on win_L1_004

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9711 vs best small negative 0.9971; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.8076 vs best small negative 0.971; no proposal; misses insertion, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:6
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.2684; proposed 0.0671 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.06056 vs best small negative 0.00086; no proposal; misses erase, insertion, paste:0.9818, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.3837 vs best small negative 0.00162; no proposal; misses erase, insertion, paste:0.9818, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.3557 vs best small negative 0.9991; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.787 vs best small negative 0.5387; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.003 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 6.634 vs best small negative 7.367; proposed 6.817 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.381 vs best small negative 7.131; proposed 2.818 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8441 vs best small negative 0.975; no proposal; misses insertion, paste:0.9818, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign exposure:-0.3 on cam_r_L0_salon_1 rejected: edges win_L0_004 0.8326 (limit >= 0.87)
- benign unsharp:0.5 on cam_r_L0_yatak_odasi_1 rejected: edges win_L0_003 0.8076 (limit >= 0.87); masks f_L0_009 0.3557 (limit >= 0.62)
- benign noise:3.0 on cam_r_L0_yatak_odasi_1 rejected: edges win_L0_003 0.8438 (limit >= 0.87)
- benign jpeg:75 on cam_r_L1_banyo_1 rejected: depth global 0.06056 (limit <= 0.05); depth f_L1_015 0.38371 (limit <= 0.14)
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_banyo_1) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_mutfak_2) accepted
- negative rotate:2.0 on f_L0_005 (cam_r_L0_salon_1) accepted
- negative shift:6 on win_L1_004 (cam_r_L1_cocuk_odasi_1) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
