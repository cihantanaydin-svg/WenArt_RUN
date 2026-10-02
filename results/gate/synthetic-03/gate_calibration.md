# Change-gate calibration: synthetic-03

8 calibration views; benign 57/64 accepted (rate 0.8906); negatives 159/173 rejected (rate 0.9191, small negatives 0.8641); 4 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 139.2 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 7 | 1 | 0.875 |
| benign | exposure | -0.3 | 8 | 8 | 0 | 1 |
| benign | exposure | 0.3 | 8 | 8 | 0 | 1 |
| benign | jpeg | 75 | 8 | 5 | 3 | 0.625 |
| benign | local_contrast | 1.5 | 8 | 6 | 2 | 0.75 |
| benign | noise | 3 | 8 | 8 | 0 | 1 |
| benign | unsharp | 0.5 | 8 | 7 | 1 | 0.875 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 7 | 7 | 0 | 0 |
| negative | insertion | - | 7 | 0 | 7 | 1 |
| negative | paste | 0.906 | 1 | 0 | 1 | 1 |
| negative | paste | 0.9122 | 7 | 0 | 7 | 1 |
| negative | removal | - | 7 | 0 | 7 | 1 |
| negative | rotate | 2 | 16 | 2 | 14 | 0.875 |
| negative | scale | 1.04 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.08 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.15 | 16 | 0 | 16 | 1 |
| negative | shift | 12 | 16 | 0 | 16 | 1 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 0 | 16 | 1 |
| negative | wall_b | 10 | 8 | 1 | 7 | 0.875 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 2 | 6 | 0.75 |
| presumed_bad | presumed_bad | 0.75 | 4 | 0 | 4 | 1 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.95 | 0.9861 | 1 | 1 | no | - | - | 1 | 0.8156 |
| edges | region_min | >= | yes | 0.85 | 0.9352 | 1 | 1 | no | - | - | 1 | 0.922 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.0589 | yes | 0.0147 | no | 1 | 1 |
| depth | global_max | <= | yes | 0.02 | 0.02674 | 0.00081 | 0.00081 | no | - | - | 0.9688 | 0.2 |
| depth | region_max | <= | yes | 0.05 | 0.1193 | 0.00131 | 0.00131 | no | - | - | 0.9375 | 0.2667 |
| masks | region_min | >= | yes | 0.9 | 0.6714 | 0.9948 | 0.999 | no | - | - | 0.9688 | 0.461 |
| colour | global_max | <= | yes | 10 | 4.995 | 0.0599 | 0.0599 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 15 | 7.115 | 0 | 0 | no | - | - | 1 | 0 |
| neutral | region_max_dchroma | <= | yes | 5 | 1.519 | 2.664 | 2.664 | yes | 1.805 | no | 1 | 0.8571 |
| features | region_min | >= | no | 0.8 | 0.828 | 0.9746 | 0.9961 | no | - | - | 1 | 0.302 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, rotate:2.0, scale:1.15, shift:12, shift:25, shift:6; missed insertion, scale:1.04, scale:1.08; proposed_partial 0.985
- edges.region_min: caught erase, removal, rotate:2.0, scale:1.15, shift:12, shift:25, shift:6; missed insertion, scale:1.04, scale:1.08; proposed_partial 0.9304
- added_lines.region_max_len_frac: caught insertion, paste:0.906, paste:0.9122; missed -
- depth.global_max: caught -; missed erase, insertion, paste:0.906, paste:0.9122, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.906, paste:0.9122, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught wall_b:10.0; missed floor_L:-15.0, white_balance_strong:1.15,1,0.85; proposed_partial 5.05
- colour.region_max: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed floor_L:-15.0; proposed_partial 7.337
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:0.906, paste:0.9122, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 6 px (rejection rate by px: {"6": 1.0, "12": 1.0, "25": 1.0})
- scale: x1.15 (rejection rate by factor: {"1.04": 0.9375, "1.08": 0.9375, "1.15": 1.0})

## Benign controls rejected

- cam_r_L-1_yatak_odasi_3 jpeg:75: masks f_L-1_003 0.8241 >= 0.9
- cam_r_L1_cocuk_odasi_2 jpeg:75: depth f_L1_014 0.05664 <= 0.05
- cam_r_L1_hol_1 blur:1.0: masks d_L1_004 0.6714 >= 0.9
- cam_r_L0_antre_2 jpeg:75: depth global 0.0216 <= 0.02
- cam_r_L0_antre_2 unsharp:0.5: depth d_L0_002 0.05211 <= 0.05
- cam_r_L0_antre_2 local_contrast:1.5: depth global 0.02674 <= 0.02; depth d_L0_002 0.1193 <= 0.05; depth f_L0_024 0.05504 <= 0.05
- cam_r_L0_mutfak_2 local_contrast:1.5: depth f_L0_009 0.07528 <= 0.05

## Negative controls accepted

- cam_r_L-1_hol_1 scale:1.04 on d_L-1_002
- cam_r_L-1_hol_1 scale:1.08 on d_L-1_002
- cam_r_L-1_hol_1 floor_L:-15.0 on struct:floor
- cam_r_L0_hol_1 rotate:2.0 on f_L0_023
- cam_r_L0_hol_1 floor_L:-15.0 on struct:floor
- cam_r_L-1_yatak_odasi_3 wall_b:10.0 on struct:walls
- cam_r_L-1_yatak_odasi_3 floor_L:-15.0 on struct:floor
- cam_r_L0_salon_3 floor_L:-15.0 on struct:floor
- cam_r_L1_cocuk_odasi_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L1_cocuk_odasi_2 floor_L:-15.0 on struct:floor
- cam_r_L1_hol_1 rotate:2.0 on f_L1_006
- cam_r_L1_hol_1 floor_L:-15.0 on struct:floor
- cam_r_L0_mutfak_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_mutfak_2 floor_L:-15.0 on struct:floor

## Presumed-bad polish attempts (reported only)

| camera | attempt | strength | decision | failed checks |
|---|---|---|---|---|
| cam_r_L-1_hol_1 | 11 | 0.75 | reject | added_lines, depth, edges, masks |
| cam_r_L0_hol_1 | 11 | 0.75 | reject | added_lines, depth, edges, masks |
| cam_r_L-1_yatak_odasi_3 | 11 | 0.75 | reject | added_lines, depth, edges, masks |
| cam_r_L0_salon_3 | 11 | 0.75 | reject | added_lines, depth, edges, masks |

## Skipped controls

- cam_r_L0_antre_2 floor_L: no floor region

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9861 vs best small negative 1; no proposal; misses insertion, scale:1.04, scale:1.08; on the small negatives it catches (rotate:2.0, shift:12, shift:6) a threshold of 0.985 would sit 25 % into the gap (proposed_partial)
- edges.region_min does not separate every small negative: worst benign 0.9352 vs best small negative 1; no proposal; misses insertion, scale:1.04, scale:1.08; on the small negatives it catches (rotate:2.0, shift:12, shift:6) a threshold of 0.9304 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.0589; proposed 0.0147 (current 0.04)
- depth.global_max does not separate every small negative: worst benign 0.02674 vs best small negative 0.00081; no proposal; misses erase, insertion, paste:0.906, paste:0.9122, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.1193 vs best small negative 0.00131; no proposal; misses erase, insertion, paste:0.906, paste:0.9122, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.6714 vs best small negative 0.9948; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 4.995 vs best small negative 0.0599; no proposal; misses floor_L:-15.0, white_balance_strong:1.15,1,0.85; on the small negatives it catches (wall_b:10.0) a threshold of 5.05 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 7.115 vs best small negative 0; no proposal; misses floor_L:-15.0; on the small negatives it catches (wall_b:10.0, white_balance_strong:1.15,1,0.85) a threshold of 7.337 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma separates: worst benign 1.519 vs best small negative 2.664; proposed 1.805 (current 5)
- features.region_min does not separate every small negative: worst benign 0.828 vs best small negative 0.9746; no proposal; misses insertion, paste:0.906, paste:0.9122, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign jpeg:75 on cam_r_L-1_yatak_odasi_3 rejected: masks f_L-1_003 0.8241 (limit >= 0.9)
- benign jpeg:75 on cam_r_L1_cocuk_odasi_2 rejected: depth f_L1_014 0.05664 (limit <= 0.05)
- benign blur:1.0 on cam_r_L1_hol_1 rejected: masks d_L1_004 0.6714 (limit >= 0.9)
- benign jpeg:75 on cam_r_L0_antre_2 rejected: depth global 0.0216 (limit <= 0.02)
- benign unsharp:0.5 on cam_r_L0_antre_2 rejected: depth d_L0_002 0.05211 (limit <= 0.05)
- benign local_contrast:1.5 on cam_r_L0_antre_2 rejected: depth global 0.02674 (limit <= 0.02); depth d_L0_002 0.11932 (limit <= 0.05); depth f_L0_024 0.05504 (limit <= 0.05)
- benign local_contrast:1.5 on cam_r_L0_mutfak_2 rejected: depth f_L0_009 0.07528 (limit <= 0.05)
- negative scale:1.04 on d_L-1_002 (cam_r_L-1_hol_1) accepted
- negative scale:1.08 on d_L-1_002 (cam_r_L-1_hol_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L-1_hol_1) accepted
- negative rotate:2.0 on f_L0_023 (cam_r_L0_hol_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_hol_1) accepted
- negative wall_b:10.0 on struct:walls (cam_r_L-1_yatak_odasi_3) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L-1_yatak_odasi_3) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_salon_3) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L1_cocuk_odasi_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L1_cocuk_odasi_2) accepted
- negative rotate:2.0 on f_L1_006 (cam_r_L1_hol_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L1_hol_1) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_mutfak_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_mutfak_2) accepted

## Warnings

- none
