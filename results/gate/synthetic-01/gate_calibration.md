# Change-gate calibration: synthetic-01

8 calibration views; benign 61/64 accepted (rate 0.9531); negatives 164/172 rejected (rate 0.9535, small negatives 0.9327); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 79.4 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 7 | 1 | 0.875 |
| benign | exposure | -0.3 | 8 | 7 | 1 | 0.875 |
| benign | exposure | 0.3 | 8 | 8 | 0 | 1 |
| benign | jpeg | 75 | 8 | 8 | 0 | 1 |
| benign | local_contrast | 1.5 | 8 | 7 | 1 | 0.875 |
| benign | noise | 3 | 8 | 8 | 0 | 1 |
| benign | unsharp | 0.5 | 8 | 8 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 8 | 0 | 8 | 1 |
| negative | insertion | - | 6 | 0 | 6 | 1 |
| negative | paste | 0.5 | 1 | 0 | 1 | 1 |
| negative | paste | 0.6941 | 1 | 0 | 1 | 1 |
| negative | paste | 1 | 6 | 0 | 6 | 1 |
| negative | removal | - | 6 | 0 | 6 | 1 |
| negative | rotate | 2 | 16 | 2 | 14 | 0.875 |
| negative | scale | 1.04 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.08 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.15 | 16 | 1 | 15 | 0.9375 |
| negative | shift | 12 | 16 | 1 | 15 | 0.9375 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 1 | 15 | 0.9375 |
| negative | wall_b | 10 | 8 | 0 | 8 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 1 | 7 | 0.875 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9268 | 1 | 1 | no | - | - | 0.9688 | 0.6786 |
| edges | region_min | >= | yes | 0.87 | 0.8987 | 1 | 1 | no | - | - | 1 | 0.8929 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.3934 | yes | 0.0984 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.0448 | 0.00043 | 0.00043 | no | - | - | 1 | 0.0405 |
| depth | region_max | <= | yes | 0.14 | 0.2018 | 0.00088 | 0.00088 | no | - | - | 0.9844 | 0.0676 |
| masks | region_min | >= | yes | 0.62 | 0.8294 | 0.9977 | 0.9977 | no | - | - | 1 | 0.0571 |
| colour | global_max | <= | yes | 7.5 | 5.891 | 0.3079 | 0.3079 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.835 | 7.512 | 7.512 | yes | 7.004 | no | 1 | 0.875 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.506 | 7.117 | 7.117 | yes | 2.909 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.7708 | 0.9743 | 0.9939 | no | - | - | 0.9844 | 0.3176 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac: caught insertion, paste:0.5, paste:0.6941, paste:1.0; missed -
- depth.global_max: caught -; missed erase, insertion, paste:0.5, paste:0.6941, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.5, paste:0.6941, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.147
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:0.5, paste:0.6941, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 25 px (rejection rate by px: {"6": 0.9375, "12": 0.9375, "25": 1.0})
- scale: x- (rejection rate by factor: {"1.04": 0.9375, "1.08": 0.9375, "1.15": 0.9375})

## Benign controls rejected

- cam_r_L0_banyo_1 local_contrast:1.5: depth f_L0_011 0.2018 <= 0.14
- cam_r_L1_hol_1 exposure:-0.3: edges global 0.9301 >= 0.935
- cam_r_L1_hol_1 blur:1.0: edges global 0.9268 >= 0.935

## Negative controls accepted

- cam_r_L0_mutfak_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L1_hol_1 shift:6 on win_L1_005
- cam_r_L1_hol_1 shift:12 on win_L1_005
- cam_r_L1_hol_1 scale:1.04 on win_L1_005
- cam_r_L1_hol_1 scale:1.08 on win_L1_005
- cam_r_L1_hol_1 scale:1.15 on win_L1_005
- cam_r_L1_hol_1 rotate:2.0 on win_L1_005
- cam_r_L1_yatak_odasi_3 rotate:2.0 on f_L1_010

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9268 vs best small negative 1; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.8987 vs best small negative 1; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.3934; proposed 0.0984 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.0448 vs best small negative 0.00043; no proposal; misses erase, insertion, paste:0.5, paste:0.6941, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.2018 vs best small negative 0.00088; no proposal; misses erase, insertion, paste:0.5, paste:0.6941, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.8294 vs best small negative 0.9977; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.891 vs best small negative 0.3079; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.147 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 6.835 vs best small negative 7.512; proposed 7.004 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.506 vs best small negative 7.117; proposed 2.909 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.7708 vs best small negative 0.9743; no proposal; misses insertion, paste:0.5, paste:0.6941, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign local_contrast:1.5 on cam_r_L0_banyo_1 rejected: depth f_L0_011 0.20183 (limit <= 0.14)
- benign exposure:-0.3 on cam_r_L1_hol_1 rejected: edges global 0.9301 (limit >= 0.935)
- benign blur:1.0 on cam_r_L1_hol_1 rejected: edges global 0.9268 (limit >= 0.935)
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_mutfak_2) accepted
- negative shift:6 on win_L1_005 (cam_r_L1_hol_1) accepted
- negative shift:12 on win_L1_005 (cam_r_L1_hol_1) accepted
- negative scale:1.04 on win_L1_005 (cam_r_L1_hol_1) accepted
- negative scale:1.08 on win_L1_005 (cam_r_L1_hol_1) accepted
- negative scale:1.15 on win_L1_005 (cam_r_L1_hol_1) accepted
- negative rotate:2.0 on win_L1_005 (cam_r_L1_hol_1) accepted
- negative rotate:2.0 on f_L1_010 (cam_r_L1_yatak_odasi_3) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
