# Change-gate calibration: synthetic-01

8 calibration views; benign 56/64 accepted (rate 0.875); negatives 159/175 rejected (rate 0.9086, small negatives 0.8544); 4 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 144.0 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 7 | 1 | 0.875 |
| benign | exposure | -0.3 | 8 | 8 | 0 | 1 |
| benign | exposure | 0.3 | 8 | 7 | 1 | 0.875 |
| benign | jpeg | 75 | 8 | 5 | 3 | 0.625 |
| benign | local_contrast | 1.5 | 8 | 7 | 1 | 0.875 |
| benign | noise | 3 | 8 | 6 | 2 | 0.75 |
| benign | unsharp | 0.5 | 8 | 8 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 7 | 5 | 2 | 0.2857 |
| negative | insertion | - | 8 | 0 | 8 | 1 |
| negative | paste | 0.6265 | 1 | 0 | 1 | 1 |
| negative | paste | 1 | 7 | 0 | 7 | 1 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.04 | 16 | 3 | 13 | 0.8125 |
| negative | scale | 1.08 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.15 | 16 | 1 | 15 | 0.9375 |
| negative | shift | 12 | 16 | 2 | 14 | 0.875 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 1 | 15 | 0.9375 |
| negative | wall_b | 10 | 8 | 1 | 7 | 0.875 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 1 | 7 | 0.875 |
| presumed_bad | presumed_bad | 0.75 | 4 | 0 | 4 | 1 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.95 | 0.9445 | 1 | 1 | no | - | - | 0.9844 | 0.7343 |
| edges | region_min | >= | yes | 0.85 | 0.8879 | 1 | 1 | no | - | - | 1 | 0.7902 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.2906 | yes | 0.0727 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.02 | 0.04484 | 0.0006 | 0.0006 | no | - | - | 0.9531 | 0.2961 |
| depth | region_max | <= | yes | 0.05 | 0.1101 | 0.00095 | 0.00095 | no | - | - | 0.8906 | 0.3882 |
| masks | region_min | >= | yes | 0.9 | 0.8566 | 0.9998 | 0.9998 | no | - | - | 0.9844 | 0.3706 |
| colour | global_max | <= | yes | 10 | 6.508 | 0.041 | 0.041 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 15 | 7.051 | 0 | 0 | no | - | - | 1 | 0.0435 |
| neutral | region_max_dchroma | <= | yes | 5 | 1.692 | 0 | 0 | no | - | - | 1 | 0.9286 |
| features | region_min | >= | no | 0.8 | 0.7916 | 0.9835 | 0.9963 | no | - | - | 0.9844 | 0.2895 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac: caught insertion, paste:0.6265, paste:1.0; missed -
- depth.global_max: caught -; missed erase, insertion, paste:0.6265, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.6265, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.804
- colour.region_max: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed floor_L:-15.0; proposed_partial 7.369
- neutral.region_max_dchroma: caught white_balance_strong:1.15,1,0.85; missed wall_b:10.0; proposed_partial 3.052
- features.region_min: caught erase, removal; missed insertion, paste:0.6265, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 25 px (rejection rate by px: {"6": 0.9375, "12": 0.875, "25": 1.0})
- scale: x- (rejection rate by factor: {"1.04": 0.8125, "1.08": 0.9375, "1.15": 0.9375})

## Benign controls rejected

- cam_r_L1_ebeveyn_yatak_odasi_2 blur:1.0: edges global 0.9445 >= 0.95
- cam_r_L1_ebeveyn_yatak_odasi_2 jpeg:75: depth f_L1_004 0.05278 <= 0.05; masks f_L1_001 0.8662 >= 0.9; masks f_L1_002 0.8566 >= 0.9
- cam_r_L1_hol_1 jpeg:75: depth global 0.04484 <= 0.02; depth d_L1_004 0.1055 <= 0.05
- cam_r_L1_hol_1 noise:3.0: depth global 0.02982 <= 0.02; depth d_L1_004 0.07716 <= 0.05
- cam_r_L0_hol_2 jpeg:75: depth global 0.0208 <= 0.02; depth d_L0_005 0.1101 <= 0.05
- cam_r_L0_hol_2 noise:3.0: depth d_L0_005 0.102 <= 0.05
- cam_r_L0_yatak_odasi_1 exposure:0.3: depth f_L0_006 0.05053 <= 0.05
- cam_r_L0_yatak_odasi_1 local_contrast:1.5: depth f_L0_006 0.06417 <= 0.05

## Negative controls accepted

- cam_r_L1_ebeveyn_yatak_odasi_2 floor_L:-15.0 on struct:floor
- cam_r_L0_mutfak_2 wall_b:10.0 on struct:walls
- cam_r_L0_mutfak_2 floor_L:-15.0 on struct:floor
- cam_r_L1_hol_1 shift:6 on d_L1_004
- cam_r_L1_hol_1 scale:1.04 on d_L1_004
- cam_r_L1_hol_1 rotate:2.0 on f_L1_008
- cam_r_L1_hol_1 floor_L:-15.0 on struct:floor
- cam_r_L0_hol_2 shift:12 on d_L0_005
- cam_r_L0_hol_2 scale:1.04 on d_L0_005
- cam_r_L0_hol_2 scale:1.08 on d_L0_005
- cam_r_L0_hol_2 scale:1.15 on d_L0_005
- cam_r_L0_hol_2 floor_L:-15.0 on struct:floor
- cam_r_L0_salon_1 shift:12 on win_L0_002
- cam_r_L0_banyo_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_yatak_odasi_1 floor_L:-15.0 on struct:floor
- cam_r_L1_yatak_odasi_3 scale:1.04 on d_L1_003

## Presumed-bad polish attempts (reported only)

| camera | attempt | strength | decision | failed checks |
|---|---|---|---|---|
| cam_r_L1_ebeveyn_yatak_odasi_2 | 11 | 0.75 | reject | added_lines, colour, depth, edges, masks |
| cam_r_L0_mutfak_2 | 11 | 0.75 | reject | depth, edges, masks |
| cam_r_L1_hol_1 | 11 | 0.75 | reject | added_lines, colour, depth, edges, masks |
| cam_r_L0_hol_2 | 11 | 0.75 | reject | added_lines, depth, edges, masks |

## Skipped controls

- cam_r_L0_banyo_2 floor_L: no floor region

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9445 vs best small negative 1; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.8879 vs best small negative 1; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.2906; proposed 0.0727 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.04484 vs best small negative 0.0006; no proposal; misses erase, insertion, paste:0.6265, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.1101 vs best small negative 0.00095; no proposal; misses erase, insertion, paste:0.6265, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.8566 vs best small negative 0.9998; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 6.508 vs best small negative 0.041; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.804 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 7.051 vs best small negative 0; no proposal; misses floor_L:-15.0; on the small negatives it catches (wall_b:10.0, white_balance_strong:1.15,1,0.85) a threshold of 7.369 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma does not separate every small negative: worst benign 1.692 vs best small negative 0; no proposal; misses wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 3.052 would sit 25 % into the gap (proposed_partial)
- features.region_min does not separate every small negative: worst benign 0.7916 vs best small negative 0.9835; no proposal; misses insertion, paste:0.6265, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign blur:1.0 on cam_r_L1_ebeveyn_yatak_odasi_2 rejected: edges global 0.9445 (limit >= 0.95)
- benign jpeg:75 on cam_r_L1_ebeveyn_yatak_odasi_2 rejected: depth f_L1_004 0.05278 (limit <= 0.05); masks f_L1_001 0.8662 (limit >= 0.9); masks f_L1_002 0.8566 (limit >= 0.9)
- benign jpeg:75 on cam_r_L1_hol_1 rejected: depth global 0.04484 (limit <= 0.02); depth d_L1_004 0.1055 (limit <= 0.05)
- benign noise:3.0 on cam_r_L1_hol_1 rejected: depth global 0.02982 (limit <= 0.02); depth d_L1_004 0.07716 (limit <= 0.05)
- benign jpeg:75 on cam_r_L0_hol_2 rejected: depth global 0.0208 (limit <= 0.02); depth d_L0_005 0.11008 (limit <= 0.05)
- benign noise:3.0 on cam_r_L0_hol_2 rejected: depth d_L0_005 0.10201 (limit <= 0.05)
- benign exposure:0.3 on cam_r_L0_yatak_odasi_1 rejected: depth f_L0_006 0.05053 (limit <= 0.05)
- benign local_contrast:1.5 on cam_r_L0_yatak_odasi_1 rejected: depth f_L0_006 0.06417 (limit <= 0.05)
- negative floor_L:-15.0 on struct:floor (cam_r_L1_ebeveyn_yatak_odasi_2) accepted
- negative wall_b:10.0 on struct:walls (cam_r_L0_mutfak_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_mutfak_2) accepted
- negative shift:6 on d_L1_004 (cam_r_L1_hol_1) accepted
- negative scale:1.04 on d_L1_004 (cam_r_L1_hol_1) accepted
- negative rotate:2.0 on f_L1_008 (cam_r_L1_hol_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L1_hol_1) accepted
- negative shift:12 on d_L0_005 (cam_r_L0_hol_2) accepted
- negative scale:1.04 on d_L0_005 (cam_r_L0_hol_2) accepted
- negative scale:1.08 on d_L0_005 (cam_r_L0_hol_2) accepted
- negative scale:1.15 on d_L0_005 (cam_r_L0_hol_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_hol_2) accepted
- negative shift:12 on win_L0_002 (cam_r_L0_salon_1) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_banyo_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_yatak_odasi_1) accepted
- negative scale:1.04 on d_L1_003 (cam_r_L1_yatak_odasi_3) accepted

## Warnings

- none
