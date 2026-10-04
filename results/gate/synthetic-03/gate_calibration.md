# Change-gate calibration: synthetic-03

8 calibration views; benign 63/64 accepted (rate 0.9844); negatives 170/176 rejected (rate 0.9659, small negatives 0.9519); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 82.2 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 7 | 1 | 0.875 |
| benign | exposure | -0.3 | 8 | 8 | 0 | 1 |
| benign | exposure | 0.3 | 8 | 8 | 0 | 1 |
| benign | jpeg | 75 | 8 | 8 | 0 | 1 |
| benign | local_contrast | 1.5 | 8 | 8 | 0 | 1 |
| benign | noise | 3 | 8 | 8 | 0 | 1 |
| benign | unsharp | 0.5 | 8 | 8 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 8 | 0 | 8 | 1 |
| negative | insertion | - | 8 | 0 | 8 | 1 |
| negative | paste | 0.973 | 7 | 1 | 6 | 0.8571 |
| negative | paste | 1 | 1 | 0 | 1 | 1 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.04 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.08 | 16 | 0 | 16 | 1 |
| negative | scale | 1.15 | 16 | 0 | 16 | 1 |
| negative | shift | 12 | 16 | 0 | 16 | 1 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 0 | 16 | 1 |
| negative | wall_b | 10 | 8 | 0 | 8 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 3 | 5 | 0.625 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9852 | 0.9933 | 0.9933 | no | - | - | 1 | 0.7431 |
| edges | region_min | >= | yes | 0.87 | 0.9116 | 0.9338 | 0.9639 | no | - | - | 1 | 0.9514 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0 | no | - | - | 1 | 0.9375 |
| depth | global_max | <= | yes | 0.05 | 0.01481 | 0.00042 | 0.00042 | no | - | - | 1 | 0.0197 |
| depth | region_max | <= | yes | 0.14 | 0.06722 | 0.00069 | 0.00069 | no | - | - | 1 | 0.0921 |
| masks | region_min | >= | yes | 0.62 | 0.4015 | 0.9973 | 0.9973 | no | - | - | 0.9844 | 0.0903 |
| colour | global_max | <= | yes | 7.5 | 5.738 | 0.2072 | 0.2072 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.793 | 7.526 | 7.526 | yes | 6.977 | no | 1 | 0.875 |
| neutral | region_max_dchroma | <= | yes | 2 | 0.7774 | 0.1042 | 0.1042 | no | - | - | 1 | 0.5 |
| features | region_min | >= | no | 0.8 | 0.7001 | 0.9787 | 0.9947 | no | - | - | 0.9688 | 0.3224 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, insertion, removal, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed rotate:2.0, scale:1.04; proposed_partial 0.9831
- edges.region_min: caught erase, removal, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed insertion, rotate:2.0, scale:1.04; proposed_partial 0.8801
- added_lines.region_max_len_frac: caught insertion, paste:1.0; missed paste:0.973
- depth.global_max: caught insertion; missed erase, paste:0.973, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.973, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught -; missed floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0; missed white_balance_strong:1.15,1,0.85; proposed_partial 1.657
- features.region_min: caught erase, removal; missed insertion, paste:0.973, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 6 px (rejection rate by px: {"6": 1.0, "12": 1.0, "25": 1.0})
- scale: x1.08 (rejection rate by factor: {"1.04": 0.9375, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L-1_yatak_odasi_2 blur:1.0: masks f_L-1_003 0.4015 >= 0.62

## Negative controls accepted

- cam_r_L1_cocuk_odasi_1 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_mutfak_1 paste:0.973 on d_L0_004
- cam_r_L1_ebeveyn_yatak_odasi_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L1_hol_3 rotate:2.0 on f_L1_006
- cam_r_L1_hol_3 scale:1.04 on d_L1_003
- cam_r_L1_hol_3 white_balance_strong:1.15,1,0.85 on view

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9852 vs best small negative 0.9933; no proposal; misses rotate:2.0, scale:1.04; on the small negatives it catches (scale:1.08, shift:12, shift:6) a threshold of 0.9831 would sit 25 % into the gap (proposed_partial)
- edges.region_min does not separate every small negative: worst benign 0.9116 vs best small negative 0.9338; no proposal; misses insertion, rotate:2.0, scale:1.04; on the small negatives it catches (scale:1.08, shift:12, shift:6) a threshold of 0.8801 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac does not separate every gross negative: worst benign 0 vs best gross negative 0; no proposal; misses paste:0.973
- depth.global_max does not separate every small negative: worst benign 0.01481 vs best small negative 0.00042; no proposal; misses erase, paste:0.973, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.06722 vs best small negative 0.00069; no proposal; misses erase, insertion, paste:0.973, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.4015 vs best small negative 0.9973; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.738 vs best small negative 0.2072; no proposal; misses floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85
- colour.region_max separates: worst benign 6.793 vs best small negative 7.526; proposed 6.977 (current 8)
- neutral.region_max_dchroma does not separate every small negative: worst benign 0.7774 vs best small negative 0.1042; no proposal; misses white_balance_strong:1.15,1,0.85; on the small negatives it catches (wall_b:10.0) a threshold of 1.657 would sit 25 % into the gap (proposed_partial)
- features.region_min does not separate every small negative: worst benign 0.7001 vs best small negative 0.9787; no proposal; misses insertion, paste:0.973, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign blur:1.0 on cam_r_L-1_yatak_odasi_2 rejected: masks f_L-1_003 0.4015 (limit >= 0.62)
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L1_cocuk_odasi_1) accepted
- negative paste:0.973 on d_L0_004 (cam_r_L0_mutfak_1) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L1_ebeveyn_yatak_odasi_2) accepted
- negative rotate:2.0 on f_L1_006 (cam_r_L1_hol_3) accepted
- negative scale:1.04 on d_L1_003 (cam_r_L1_hol_3) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L1_hol_3) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
