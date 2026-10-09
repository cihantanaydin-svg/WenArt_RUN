# Change-gate calibration: real02

8 calibration views (rooms); benign 64/64 accepted (rate 1); negatives 172/176 rejected (rate 0.9773, small negatives 0.9712); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 91.4 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Exterior views

5 exterior view(s) rendered, 3 calibrated (ext_1, ext_2, ext_5): benign 24/24 accepted (rate 1); negatives 44/52 rejected (rate 0.8462, small negatives 0.7647). They do not count in the rates above: the exterior views are validated apart, with the same limits (`validation.yaml`), and a failed exterior validation keeps them Cycles only.
- accepted negative: ext_1 rotate:2.0 on win_L0_001
- accepted negative: ext_1 scale:1.04 on win_L0_002
- accepted negative: ext_1 scale:1.08 on win_L0_002
- accepted negative: ext_1 rotate:2.0 on win_L0_002
- accepted negative: ext_2 rotate:2.0 on win_L0_004
- accepted negative: ext_2 scale:1.04 on win_L0_003
- accepted negative: ext_2 scale:1.08 on win_L0_003
- accepted negative: ext_2 rotate:2.0 on win_L0_003

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
| negative | paste | 1 | 8 | 1 | 7 | 0.875 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.04 | 16 | 1 | 15 | 0.9375 |
| negative | scale | 1.08 | 16 | 0 | 16 | 1 |
| negative | scale | 1.15 | 16 | 0 | 16 | 1 |
| negative | shift | 12 | 16 | 0 | 16 | 1 |
| negative | shift | 25 | 16 | 0 | 16 | 1 |
| negative | shift | 6 | 16 | 1 | 15 | 0.9375 |
| negative | wall_b | 10 | 8 | 0 | 8 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 8 | 0 | 8 | 1 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9849 | 0.9959 | 0.9959 | no | - | - | 1 | 0.6389 |
| edges | region_min | >= | yes | 0.87 | 0.9473 | 0.9394 | 0.9965 | yes | 0.9453 | no | 1 | 0.9375 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0 | no | - | - | 1 | 0.9375 |
| depth | global_max | <= | yes | 0.05 | 0.01901 | 0.00073 | 0.00073 | no | - | - | 1 | 0.0395 |
| depth | region_max | <= | yes | 0.14 | 0.06454 | 0.00081 | 0.00081 | no | - | - | 1 | 0.0592 |
| masks | region_min | >= | yes | 0.62 | 0.7737 | 0.9808 | 0.9982 | no | - | - | 1 | 0.1597 |
| colour | global_max | <= | yes | 7.5 | 5.931 | 1.016 | 1.016 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 7.255 | 7.339 | 7.339 | yes | 7.276 | no | 1 | 0.8333 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.423 | 5.18 | 5.18 | yes | 2.363 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8611 | 0.9806 | 0.995 | no | - | - | 1 | 0.3355 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, scale:1.08, scale:1.15, shift:25; missed insertion, rotate:2.0, scale:1.04, shift:12, shift:6; proposed_partial 0.9811
- edges.region_min: caught erase, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed insertion
- added_lines.region_max_len_frac: caught insertion; missed paste:1.0
- depth.global_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.003
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 12 px (rejection rate by px: {"6": 0.9375, "12": 1.0, "25": 1.0})
- scale: x1.08 (rejection rate by factor: {"1.04": 0.9375, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- none

## Negative controls accepted

- cam_r_L-1_koridor_2_3 scale:1.04 on d_L-1_003
- cam_r_L-1_koridor_2_3 paste:1.0 on win_L0_002
- cam_r_L-1_salon_1 shift:6 on f_L-1_024
- cam_r_L0_koridor_1 rotate:2.0 on f_L0_037

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9849 vs best small negative 0.9959; no proposal; misses insertion, rotate:2.0, scale:1.04, shift:12, shift:6; on the small negatives it catches (scale:1.08) a threshold of 0.9811 would sit 25 % into the gap (proposed_partial)
- edges.region_min separates: worst benign 0.9473 vs best small negative 0.9394; proposed 0.9453 (current 0.87)
- added_lines.region_max_len_frac does not separate every gross negative: worst benign 0 vs best gross negative 0; no proposal; misses paste:1.0
- depth.global_max does not separate every small negative: worst benign 0.01901 vs best small negative 0.00073; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.06454 vs best small negative 0.00081; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.7737 vs best small negative 0.9808; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.931 vs best small negative 1.016; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.003 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 7.255 vs best small negative 7.339; proposed 7.276 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.423 vs best small negative 5.18; proposed 2.363 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8611 vs best small negative 0.9806; no proposal; misses insertion, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- negative scale:1.04 on d_L-1_003 (cam_r_L-1_koridor_2_3) accepted
- negative paste:1.0 on win_L0_002 (cam_r_L-1_koridor_2_3) accepted
- negative shift:6 on f_L-1_024 (cam_r_L-1_salon_1) accepted
- negative rotate:2.0 on f_L0_037 (cam_r_L0_koridor_1) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
