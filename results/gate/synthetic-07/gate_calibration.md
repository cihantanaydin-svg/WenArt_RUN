# Change-gate calibration: synthetic-07

8 calibration views (rooms); benign 64/64 accepted (rate 1); negatives 172/176 rejected (rate 0.9773, small negatives 0.9615); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 89.6 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Exterior views

5 exterior view(s) rendered, 3 calibrated (ext_2, ext_5, ext_6): benign 24/24 accepted (rate 1); negatives 43/60 rejected (rate 0.7167, small negatives 0.641). They do not count in the rates above: the exterior views are validated apart, with the same limits (`validation.yaml`), and a failed exterior validation keeps them Cycles only.
- accepted negative: ext_2 scale:1.04 on win_L0_006
- accepted negative: ext_2 scale:1.08 on win_L0_006
- accepted negative: ext_2 scale:1.15 on win_L0_006
- accepted negative: ext_2 rotate:2.0 on win_L0_006
- accepted negative: ext_2 scale:1.04 on win_L0_002
- accepted negative: ext_2 scale:1.08 on win_L0_002
- accepted negative: ext_2 scale:1.15 on win_L0_002
- accepted negative: ext_2 rotate:2.0 on win_L0_002
- accepted negative: ext_2 paste:1.0 on win_L1_001
- accepted negative: ext_5 scale:1.04 on win_L1_001
- accepted negative: ext_5 scale:1.08 on win_L1_001
- accepted negative: ext_5 rotate:2.0 on win_L1_001
- accepted negative: ext_5 scale:1.04 on win_L0_001
- accepted negative: ext_5 rotate:2.0 on win_L0_001
- accepted negative: ext_6 rotate:2.0 on win_L0_001
- accepted negative: ext_6 rotate:2.0 on d_L0_001
- accepted negative: ext_6 floor_L:-15.0 on struct:floor

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 8 | 0 | 1 |
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
| negative | paste | 1 | 8 | 0 | 8 | 1 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.04 | 16 | 0 | 16 | 1 |
| negative | scale | 1.08 | 16 | 0 | 16 | 1 |
| negative | scale | 1.15 | 16 | 0 | 16 | 1 |
| negative | shift | 12 | 16 | 1 | 15 | 0.9375 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 0 | 16 | 1 |
| negative | wall_b | 10 | 8 | 1 | 7 | 0.875 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 1 | 7 | 0.875 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9806 | 0.9999 | 0.9999 | no | - | - | 1 | 0.625 |
| edges | region_min | >= | yes | 0.87 | 0.955 | 0.9911 | 0.999 | no | - | - | 1 | 0.9375 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.159 | yes | 0.0398 | no | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.01093 | 0.00033 | 0.00033 | no | - | - | 1 | 0.0526 |
| depth | region_max | <= | yes | 0.14 | 0.05188 | 0.00042 | 0.00042 | no | - | - | 1 | 0.1053 |
| masks | region_min | >= | yes | 0.62 | 0.8291 | 0.99 | 0.9953 | no | - | - | 1 | 0.1389 |
| colour | global_max | <= | yes | 7.5 | 5.641 | 1.163 | 1.163 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.168 | 4.638 | 4.638 | no | - | - | 1 | 0.625 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.421 | 6.853 | 6.853 | yes | 2.779 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.845 | 0.9822 | 0.9907 | no | - | - | 1 | 0.3026 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min: caught erase, removal, rotate:2.0, scale:1.04, scale:1.15, shift:25, shift:6; missed insertion, scale:1.08, shift:12; proposed_partial 0.9393
- added_lines.region_max_len_frac: caught insertion, paste:1.0; missed -
- depth.global_max: caught insertion; missed erase, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught -; missed floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85
- colour.region_max: caught floor_L:-15.0; missed wall_b:10.0, white_balance_strong:1.15,1,0.85; proposed_partial 6.208
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 25 px (rejection rate by px: {"6": 1.0, "12": 0.9375, "25": 1.0})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- none

## Negative controls accepted

- cam_r_L-1_mutfak_2 white_balance_strong:1.15,1,0.85 on view
- cam_r_L-1_mutfak_2 wall_b:10.0 on struct:walls
- cam_r_L0_yatak_odasi_1 shift:12 on win_L0_004
- cam_r_L0_yatak_odasi_1 rotate:2.0 on win_L0_004

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9806 vs best small negative 0.9999; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- edges.region_min does not separate every small negative: worst benign 0.955 vs best small negative 0.9911; no proposal; misses insertion, scale:1.08, shift:12; on the small negatives it catches (rotate:2.0, scale:1.04, shift:6) a threshold of 0.9393 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.159; proposed 0.0398 (current 0.04)
- depth.global_max does not separate every small negative: worst benign 0.01093 vs best small negative 0.00033; no proposal; misses erase, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.05188 vs best small negative 0.00042; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.8291 vs best small negative 0.99; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.641 vs best small negative 1.163; no proposal; misses floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85
- colour.region_max does not separate every small negative: worst benign 6.168 vs best small negative 4.638; no proposal; misses wall_b:10.0, white_balance_strong:1.15,1,0.85; on the small negatives it catches (floor_L:-15.0) a threshold of 6.208 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma separates: worst benign 1.421 vs best small negative 6.853; proposed 2.779 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.845 vs best small negative 0.9822; no proposal; misses insertion, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- negative white_balance_strong:1.15,1,0.85 on view (cam_r_L-1_mutfak_2) accepted
- negative wall_b:10.0 on struct:walls (cam_r_L-1_mutfak_2) accepted
- negative shift:12 on win_L0_004 (cam_r_L0_yatak_odasi_1) accepted
- negative rotate:2.0 on win_L0_004 (cam_r_L0_yatak_odasi_1) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
