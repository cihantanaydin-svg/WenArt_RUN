# Change-gate calibration: synthetic-03

8 calibration views; benign 63/64 accepted (rate 0.9844); negatives 174/176 rejected (rate 0.9886, small negatives 0.9808); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 145.1 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 8 | 0 | 1 |
| benign | exposure | -0.3 | 8 | 8 | 0 | 1 |
| benign | exposure | 0.3 | 8 | 8 | 0 | 1 |
| benign | jpeg | 75 | 8 | 8 | 0 | 1 |
| benign | local_contrast | 1.5 | 8 | 7 | 1 | 0.875 |
| benign | noise | 3 | 8 | 8 | 0 | 1 |
| benign | unsharp | 0.5 | 8 | 8 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 8 | 0 | 8 | 1 |
| negative | insertion | - | 8 | 0 | 8 | 1 |
| negative | paste | 0.7258 | 1 | 0 | 1 | 1 |
| negative | paste | 1 | 7 | 0 | 7 | 1 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.04 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.08 | 16 | 0 | 16 | 1 |
| negative | scale | 1.15 | 16 | 0 | 16 | 1 |
| negative | shift | 12 | 16 | 0 | 16 | 1 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 0 | 16 | 1 |
| negative | wall_b | 10 | 8 | 0 | 8 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 0 | 8 | 1 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9834 | 0.9985 | 0.9985 | no | - | - | 1 | 0.6597 |
| edges | region_min | >= | yes | 0.87 | 0.9667 | 0.9882 | 0.9967 | no | - | - | 1 | 0.9441 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.3208 | yes | 0.0802 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.01928 | 0.00048 | 0.00048 | no | - | - | 1 | 0.0197 |
| depth | region_max | <= | yes | 0.14 | 0.04227 | 0.00128 | 0.00128 | no | - | - | 1 | 0.0395 |
| masks | region_min | >= | yes | 0.62 | 0.2825 | 0.9869 | 0.9973 | no | - | - | 0.9844 | 0.1119 |
| colour | global_max | <= | yes | 7.5 | 5.252 | 1.438 | 1.438 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 7.112 | 7.957 | 7.957 | yes | 7.323 | no | 1 | 0.9167 |
| neutral | region_max_dchroma | <= | yes | 2 | 0.8929 | 0.0756 | 0.0756 | no | - | - | 1 | 0.8125 |
| features | region_min | >= | no | 0.8 | 0.7851 | 0.9833 | 0.9952 | no | - | - | 0.9844 | 0.3179 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, scale:1.08, scale:1.15, shift:6; missed insertion, rotate:2.0, scale:1.04, shift:12, shift:25; proposed_partial 0.9829
- edges.region_min: caught erase, removal, rotate:2.0, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed insertion, scale:1.04; proposed_partial 0.9465
- added_lines.region_max_len_frac: caught insertion, paste:0.7258, paste:1.0; missed -
- depth.global_max: caught -; missed erase, insertion, paste:0.7258, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.7258, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught -; missed floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0; missed white_balance_strong:1.15,1,0.85; proposed_partial 1.298
- features.region_min: caught erase, removal; missed insertion, paste:0.7258, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 6 px (rejection rate by px: {"6": 1.0, "12": 1.0, "25": 1.0})
- scale: x1.08 (rejection rate by factor: {"1.04": 0.9375, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L1_yatak_odasi_3 local_contrast:1.5: masks f_L1_012 0.2825 >= 0.62

## Negative controls accepted

- cam_r_L1_hol_3 scale:1.04 on f_L1_007
- cam_r_L1_hol_3 rotate:2.0 on f_L1_008

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9834 vs best small negative 0.9985; no proposal; misses insertion, rotate:2.0, scale:1.04, shift:12, shift:25; on the small negatives it catches (scale:1.08, shift:6) a threshold of 0.9829 would sit 25 % into the gap (proposed_partial)
- edges.region_min does not separate every small negative: worst benign 0.9667 vs best small negative 0.9882; no proposal; misses insertion, scale:1.04; on the small negatives it catches (rotate:2.0, scale:1.08, shift:12, shift:6) a threshold of 0.9465 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.3208; proposed 0.0802 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.01928 vs best small negative 0.00048; no proposal; misses erase, insertion, paste:0.7258, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.04227 vs best small negative 0.00128; no proposal; misses erase, insertion, paste:0.7258, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.2825 vs best small negative 0.9869; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.252 vs best small negative 1.438; no proposal; misses floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85
- colour.region_max separates: worst benign 7.112 vs best small negative 7.957; proposed 7.323 (current 8)
- neutral.region_max_dchroma does not separate every small negative: worst benign 0.8929 vs best small negative 0.0756; no proposal; misses white_balance_strong:1.15,1,0.85; on the small negatives it catches (wall_b:10.0) a threshold of 1.298 would sit 25 % into the gap (proposed_partial)
- features.region_min does not separate every small negative: worst benign 0.7851 vs best small negative 0.9833; no proposal; misses insertion, paste:0.7258, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign local_contrast:1.5 on cam_r_L1_yatak_odasi_3 rejected: masks f_L1_012 0.2825 (limit >= 0.62)
- negative scale:1.04 on f_L1_007 (cam_r_L1_hol_3) accepted
- negative rotate:2.0 on f_L1_008 (cam_r_L1_hol_3) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
