# Change-gate calibration: synthetic-04

5 calibration views; benign 39/40 accepted (rate 0.975); negatives 88/90 rejected (rate 0.9778, small negatives 0.98); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 92.2 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 5 | 5 | 0 | 1 |
| benign | exposure | -0.3 | 5 | 5 | 0 | 1 |
| benign | exposure | 0.3 | 5 | 5 | 0 | 1 |
| benign | jpeg | 75 | 5 | 4 | 1 | 0.8 |
| benign | local_contrast | 1.5 | 5 | 5 | 0 | 1 |
| benign | noise | 3 | 5 | 5 | 0 | 1 |
| benign | unsharp | 0.5 | 5 | 5 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 5 | 5 | 0 | 1 |
| negative | erase | - | 7 | 0 | 7 | 1 |
| negative | floor_L | -15 | 5 | 0 | 5 | 1 |
| negative | insertion | - | 7 | 0 | 7 | 1 |
| negative | paste | 0.7105 | 4 | 0 | 4 | 1 |
| negative | paste | 1 | 1 | 0 | 1 | 1 |
| negative | removal | - | 7 | 0 | 7 | 1 |
| negative | rotate | 2 | 7 | 0 | 7 | 1 |
| negative | scale | 1.04 | 7 | 0 | 7 | 1 |
| negative | scale | 1.08 | 7 | 0 | 7 | 1 |
| negative | scale | 1.15 | 7 | 0 | 7 | 1 |
| negative | shift | 12 | 7 | 1 | 6 | 0.8571 |
| negative | shift | 25 | 7 | 1 | 6 | 0.8571 |
| negative | shift | 6 | 7 | 0 | 7 | 1 |
| negative | wall_b | 10 | 5 | 0 | 5 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 5 | 0 | 5 | 1 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9889 | 0.9979 | 0.9979 | no | - | - | 1 | 0.7 |
| edges | region_min | >= | yes | 0.87 | 0.9414 | 0.963 | 0.9938 | no | - | - | 1 | 0.8857 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.3337 | yes | 0.0834 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.00778 | 0.00094 | 0.00094 | no | - | - | 1 | 0.0667 |
| depth | region_max | <= | yes | 0.14 | 0.01798 | 0.0016 | 0.00153 | no | - | - | 1 | 0.0533 |
| masks | region_min | >= | yes | 0.62 | 0.3033 | 0.9815 | 0.9882 | no | - | - | 0.975 | 0.1286 |
| colour | global_max | <= | yes | 7.5 | 6.49 | 0.3338 | 0.3338 | no | - | - | 1 | 0.2 |
| colour | region_max | <= | yes | 8 | 7.05 | 8.123 | 8.123 | yes | 7.319 | no | 1 | 1 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.555 | 7.468 | 7.468 | yes | 3.033 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8578 | 0.9719 | 0.9937 | no | - | - | 1 | 0.36 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:6; missed insertion, shift:12, shift:25; proposed_partial 0.9869
- edges.region_min: caught erase, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:25, shift:6; missed insertion, removal, shift:12; proposed_partial 0.9177
- added_lines.region_max_len_frac: caught insertion, paste:0.7105, paste:1.0; missed -
- depth.global_max: caught insertion, paste:1.0, removal; missed erase, paste:0.7105, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught insertion, paste:1.0; missed erase, paste:0.7105, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.554
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal, scale:1.15; missed insertion, paste:0.7105, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6

## Smallest detected change

- shift: - px (rejection rate by px: {"6": 1.0, "12": 0.8571, "25": 0.8571})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L3_cocuk_odasi_1 jpeg:75: masks f_L3_023 0.3033 >= 0.62

## Negative controls accepted

- cam_r_L3_cocuk_odasi_1 shift:12 on win_L3_008
- cam_r_L3_cocuk_odasi_1 shift:25 on win_L3_008

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9889 vs best small negative 0.9979; no proposal; misses insertion, shift:12, shift:25; on the small negatives it catches (rotate:2.0, scale:1.04, scale:1.08, shift:6) a threshold of 0.9869 would sit 25 % into the gap (proposed_partial)
- edges.region_min does not separate every small negative: worst benign 0.9414 vs best small negative 0.963; no proposal; misses insertion, removal, shift:12; on the small negatives it catches (rotate:2.0, scale:1.04, scale:1.08, shift:6) a threshold of 0.9177 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.3337; proposed 0.0834 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.00778 vs best small negative 0.00094; no proposal; misses erase, paste:0.7105, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.01798 vs best small negative 0.0016; no proposal; misses erase, paste:0.7105, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.3033 vs best small negative 0.9815; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 6.49 vs best small negative 0.3338; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.554 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 7.05 vs best small negative 8.123; proposed 7.319 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.555 vs best small negative 7.468; proposed 3.033 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8578 vs best small negative 0.9719; no proposal; misses insertion, paste:0.7105, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, shift:12, shift:25, shift:6
- benign jpeg:75 on cam_r_L3_cocuk_odasi_1 rejected: masks f_L3_023 0.3033 (limit >= 0.62)
- negative shift:12 on win_L3_008 (cam_r_L3_cocuk_odasi_1) accepted
- negative shift:25 on win_L3_008 (cam_r_L3_cocuk_odasi_1) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
