# Change-gate calibration: synthetic-02

5 calibration views; benign 40/40 accepted (rate 1); negatives 48/58 rejected (rate 0.8276, small negatives 0.7429); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 38.7 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 5 | 5 | 0 | 1 |
| benign | exposure | -0.3 | 5 | 5 | 0 | 1 |
| benign | exposure | 0.3 | 5 | 5 | 0 | 1 |
| benign | jpeg | 75 | 5 | 5 | 0 | 1 |
| benign | local_contrast | 1.5 | 5 | 5 | 0 | 1 |
| benign | noise | 3 | 5 | 5 | 0 | 1 |
| benign | unsharp | 0.5 | 5 | 5 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 5 | 5 | 0 | 1 |
| negative | erase | - | 4 | 0 | 4 | 1 |
| negative | floor_L | -15 | 5 | 3 | 2 | 0.4 |
| negative | insertion | - | 3 | 0 | 3 | 1 |
| negative | paste | 0.6767 | 1 | 0 | 1 | 1 |
| negative | paste | 1 | 4 | 0 | 4 | 1 |
| negative | removal | - | 3 | 0 | 3 | 1 |
| negative | rotate | 2 | 4 | 1 | 3 | 0.75 |
| negative | scale | 1.04 | 4 | 1 | 3 | 0.75 |
| negative | scale | 1.08 | 4 | 0 | 4 | 1 |
| negative | scale | 1.15 | 4 | 1 | 3 | 0.75 |
| negative | shift | 12 | 4 | 1 | 3 | 0.75 |
| negative | shift | 25 | 4 | 0 | 4 | 1 |
| negative | shift | 6 | 4 | 2 | 2 | 0.5 |
| negative | wall_b | 10 | 5 | 0 | 5 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 5 | 1 | 4 | 0.8 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.98 | 1 | 1 | no | - | - | 1 | 0.6842 |
| edges | region_min | >= | yes | 0.87 | 0.9321 | 1 | 1 | no | - | - | 1 | 0.7368 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.323 | yes | 0.0808 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.03726 | 0.00069 | 0.00069 | no | - | - | 1 | 0.0698 |
| depth | region_max | <= | yes | 0.14 | 0.1166 | 0.00108 | 0.00108 | no | - | - | 1 | 0.0698 |
| masks | region_min | >= | yes | 0.62 | 0.9366 | 0.9781 | 0.9894 | no | - | - | 1 | 0.1316 |
| colour | global_max | <= | yes | 7.5 | 6.674 | 0.0034 | 0.0034 | no | - | - | 1 | 0.1333 |
| colour | region_max | <= | yes | 8 | 7.354 | 0 | 0 | no | - | - | 1 | 0.5333 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.382 | 7.179 | 7.179 | yes | 2.832 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8756 | 0.9657 | 0.9918 | no | - | - | 1 | 0.3488 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac: caught insertion, paste:0.6767, paste:1.0; missed -
- depth.global_max: caught -; missed erase, insertion, paste:0.6767, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.6767, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught scale:1.08, scale:1.15, shift:25; missed erase, insertion, removal, rotate:2.0, scale:1.04, shift:12, shift:6; proposed_partial 0.9269
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.744
- colour.region_max: caught wall_b:10.0; missed floor_L:-15.0, white_balance_strong:1.15,1,0.85; proposed_partial 7.989
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal, scale:1.15; missed insertion, paste:0.6767, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 25 px (rejection rate by px: {"6": 0.5, "12": 0.75, "25": 1.0})
- scale: x- (rejection rate by factor: {"1.04": 0.75, "1.08": 1.0, "1.15": 0.75})

## Benign controls rejected

- none

## Negative controls accepted

- cam_r_L0_yatak_odasi_2 shift:6 on d_L0_004
- cam_r_L0_yatak_odasi_2 shift:6 on win_L0_004
- cam_r_L0_yatak_odasi_2 shift:12 on win_L0_004
- cam_r_L0_yatak_odasi_2 scale:1.04 on win_L0_004
- cam_r_L0_yatak_odasi_2 scale:1.15 on win_L0_004
- cam_r_L0_yatak_odasi_2 rotate:2.0 on win_L0_004
- cam_r_L0_antre_1 floor_L:-15.0 on struct:floor
- cam_r_L0_banyo_1 white_balance_strong:1.15,1,0.85 on view
- cam_r_L0_banyo_1 floor_L:-15.0 on struct:floor
- cam_r_L0_mutfak_1 floor_L:-15.0 on struct:floor

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.98 vs best small negative 1; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.9321 vs best small negative 1; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.323; proposed 0.0808 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.03726 vs best small negative 0.00069; no proposal; misses erase, insertion, paste:0.6767, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.1166 vs best small negative 0.00108; no proposal; misses erase, insertion, paste:0.6767, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.9366 vs best small negative 0.9781; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, shift:12, shift:6; on the small negatives it catches (scale:1.08) a threshold of 0.9269 would sit 25 % into the gap (proposed_partial)
- colour.global_max does not separate every small negative: worst benign 6.674 vs best small negative 0.0034; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.744 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 7.354 vs best small negative 0; no proposal; misses floor_L:-15.0, white_balance_strong:1.15,1,0.85; on the small negatives it catches (wall_b:10.0) a threshold of 7.989 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma separates: worst benign 1.382 vs best small negative 7.179; proposed 2.832 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8756 vs best small negative 0.9657; no proposal; misses insertion, paste:0.6767, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- negative shift:6 on d_L0_004 (cam_r_L0_yatak_odasi_2) accepted
- negative shift:6 on win_L0_004 (cam_r_L0_yatak_odasi_2) accepted
- negative shift:12 on win_L0_004 (cam_r_L0_yatak_odasi_2) accepted
- negative scale:1.04 on win_L0_004 (cam_r_L0_yatak_odasi_2) accepted
- negative scale:1.15 on win_L0_004 (cam_r_L0_yatak_odasi_2) accepted
- negative rotate:2.0 on win_L0_004 (cam_r_L0_yatak_odasi_2) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_antre_1) accepted
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L0_banyo_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_banyo_1) accepted
- negative floor_L:-15.0 on struct:floor (cam_r_L0_mutfak_1) accepted

## Warnings

- cam_r_L0_antre_1: no required element; no object negatives
- cam_r_L0_banyo_1: no required element; no object negatives
- cam_r_L0_mutfak_1: no required element; no object negatives
- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
