# Change-gate calibration: synthetic-03

8 calibration views (rooms); benign 63/64 accepted (rate 0.9844); negatives 175/176 rejected (rate 0.9943, small negatives 0.9904); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 78.8 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Exterior views

The project rendered no exterior view.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 8 | 8 | 0 | 1 |
| benign | exposure | -0.3 | 8 | 8 | 0 | 1 |
| benign | exposure | 0.3 | 8 | 7 | 1 | 0.875 |
| benign | jpeg | 75 | 8 | 8 | 0 | 1 |
| benign | local_contrast | 1.5 | 8 | 8 | 0 | 1 |
| benign | noise | 3 | 8 | 8 | 0 | 1 |
| benign | unsharp | 0.5 | 8 | 8 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 8 | 8 | 0 | 1 |
| negative | erase | - | 16 | 0 | 16 | 1 |
| negative | floor_L | -15 | 8 | 1 | 7 | 0.875 |
| negative | insertion | - | 8 | 0 | 8 | 1 |
| negative | paste | 0.75 | 1 | 0 | 1 | 1 |
| negative | paste | 1 | 7 | 0 | 7 | 1 |
| negative | removal | - | 8 | 0 | 8 | 1 |
| negative | rotate | 2 | 16 | 0 | 16 | 1 |
| negative | scale | 1.04 | 16 | 0 | 16 | 1 |
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
| edges | global_min | >= | yes | 0.935 | 0.9859 | 0.9912 | 0.9949 | no | - | - | 1 | 0.6224 |
| edges | region_min | >= | yes | 0.87 | 0.8606 | 0.9889 | 0.9889 | no | - | - | 0.9844 | 0.979 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.0891 | yes | 0.0223 | no | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.00878 | 0.00065 | 0.00065 | no | - | - | 1 | 0.0461 |
| depth | region_max | <= | yes | 0.14 | 0.03224 | 0.00111 | 0.00111 | no | - | - | 1 | 0.0987 |
| masks | region_min | >= | yes | 0.62 | 0.7897 | 0.9859 | 0.9859 | no | - | - | 1 | 0.2431 |
| colour | global_max | <= | yes | 7.5 | 5 | 0.0462 | 0.0462 | no | - | - | 1 | 0 |
| colour | region_max | <= | yes | 8 | 6.629 | 0 | 0 | no | - | - | 1 | 0.9167 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.073 | 0.8818 | 0.8818 | no | - | - | 1 | 0.7857 |
| features | region_min | >= | no | 0.8 | 0.7698 | 0.9734 | 0.9986 | no | - | - | 0.9688 | 0.3684 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, scale:1.08, scale:1.15; missed insertion, rotate:2.0, scale:1.04, shift:12, shift:25, shift:6; proposed_partial 0.9856
- edges.region_min: caught erase, removal, rotate:2.0, scale:1.08, scale:1.15, shift:12, shift:25, shift:6; missed insertion, scale:1.04; proposed_partial 0.8574
- added_lines.region_max_len_frac: caught insertion, paste:0.75, paste:1.0; missed -
- depth.global_max: caught insertion, paste:0.75; missed erase, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught paste:0.75; missed erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught removal; missed erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 5.065
- colour.region_max: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed floor_L:-15.0; proposed_partial 6.778
- neutral.region_max_dchroma: caught wall_b:10.0; missed white_balance_strong:1.15,1,0.85; proposed_partial 1.516
- features.region_min: caught erase, removal; missed insertion, paste:0.75, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: 6 px (rejection rate by px: {"6": 1.0, "12": 1.0, "25": 1.0})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L0_mutfak_2 exposure:0.3: edges dec_L0_022 0.8606 >= 0.87

## Negative controls accepted

- cam_r_L0_mutfak_2 floor_L:-15.0 on struct:floor

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9859 vs best small negative 0.9912; no proposal; misses insertion, rotate:2.0, scale:1.04, shift:12, shift:25, shift:6; on the small negatives it catches (scale:1.08) a threshold of 0.9856 would sit 25 % into the gap (proposed_partial)
- edges.region_min does not separate every small negative: worst benign 0.8606 vs best small negative 0.9889; no proposal; misses insertion, scale:1.04; on the small negatives it catches (rotate:2.0, scale:1.08, shift:12, shift:6) a threshold of 0.8574 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.0891; proposed 0.0223 (current 0.04)
- depth.global_max does not separate every small negative: worst benign 0.00878 vs best small negative 0.00065; no proposal; misses erase, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.03224 vs best small negative 0.00111; no proposal; misses erase, insertion, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.7897 vs best small negative 0.9859; no proposal; misses erase, insertion, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5 vs best small negative 0.0462; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 5.065 would sit 25 % into the gap (proposed_partial)
- colour.region_max does not separate every small negative: worst benign 6.629 vs best small negative 0; no proposal; misses floor_L:-15.0; on the small negatives it catches (wall_b:10.0, white_balance_strong:1.15,1,0.85) a threshold of 6.778 would sit 25 % into the gap (proposed_partial)
- neutral.region_max_dchroma does not separate every small negative: worst benign 1.073 vs best small negative 0.8818; no proposal; misses white_balance_strong:1.15,1,0.85; on the small negatives it catches (wall_b:10.0) a threshold of 1.516 would sit 25 % into the gap (proposed_partial)
- features.region_min does not separate every small negative: worst benign 0.7698 vs best small negative 0.9734; no proposal; misses insertion, paste:0.75, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign exposure:0.3 on cam_r_L0_mutfak_2 rejected: edges dec_L0_022 0.8606 (limit >= 0.87)
- negative floor_L:-15.0 on struct:floor (cam_r_L0_mutfak_2) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
