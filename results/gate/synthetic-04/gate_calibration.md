# Change-gate calibration: synthetic-04

5 calibration views; benign 39/40 accepted (rate 0.975); negatives 94/96 rejected (rate 0.9792, small negatives 0.9818); 0 presumed-bad polish attempts (reported only). Gate code m5.2; complete; 68.4 s. Proposals = worst benign value + 25 % of the gap to the best small negative; they are applied to thresholds.yaml by hand after review, and a looser one needs the user's OK.

## Rates by control

| set | control | magnitude | n | accepted | rejected | rate |
|---|---|---|---|---|---|---|
| benign | blur | 1 | 5 | 4 | 1 | 0.8 |
| benign | exposure | -0.3 | 5 | 5 | 0 | 1 |
| benign | exposure | 0.3 | 5 | 5 | 0 | 1 |
| benign | jpeg | 75 | 5 | 5 | 0 | 1 |
| benign | local_contrast | 1.5 | 5 | 5 | 0 | 1 |
| benign | noise | 3 | 5 | 5 | 0 | 1 |
| benign | unsharp | 0.5 | 5 | 5 | 0 | 1 |
| benign | white_balance | 1.03,1,0.97 | 5 | 5 | 0 | 1 |
| negative | erase | - | 8 | 0 | 8 | 1 |
| negative | floor_L | -15 | 5 | 0 | 5 | 1 |
| negative | insertion | - | 6 | 0 | 6 | 1 |
| negative | paste | 0.7105 | 4 | 0 | 4 | 1 |
| negative | paste | 1 | 1 | 0 | 1 | 1 |
| negative | removal | - | 6 | 0 | 6 | 1 |
| negative | rotate | 2 | 8 | 0 | 8 | 1 |
| negative | scale | 1.04 | 8 | 0 | 8 | 1 |
| negative | scale | 1.08 | 8 | 0 | 8 | 1 |
| negative | scale | 1.15 | 8 | 0 | 8 | 1 |
| negative | shift | 12 | 8 | 1 | 7 | 0.875 |
| negative | shift | 25 | 8 | 1 | 7 | 0.875 |
| negative | shift | 6 | 8 | 0 | 8 | 1 |
| negative | wall_b | 10 | 5 | 0 | 5 | 1 |
| negative | white_balance_strong | 1.15,1,0.85 | 5 | 0 | 5 | 1 |

## Per metric

| check | limit | op | hard | current | worst benign | best small negative | best negative | separates | proposed | looser | benign pass now | negatives fail now |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edges | global_min | >= | yes | 0.935 | 0.9823 | 0.9973 | 0.9977 | no | - | - | 1 | 0.8158 |
| edges | region_min | >= | yes | 0.87 | 0.7554 | 0.9699 | 1 | no | - | - | 0.975 | 0.9211 |
| added_lines | region_max_len_frac | <= | yes | 0.04 | 0 | - | 0.3452 | yes | 0.0863 | yes | 1 | 1 |
| depth | global_max | <= | yes | 0.05 | 0.01793 | 0.0009 | 0.0009 | no | - | - | 1 | 0.0617 |
| depth | region_max | <= | yes | 0.14 | 0.06609 | 0.00139 | 0.00139 | no | - | - | 1 | 0.0864 |
| masks | region_min | >= | yes | 0.62 | 0.6805 | 0.9997 | 0.9997 | no | - | - | 1 | 0.0789 |
| colour | global_max | <= | yes | 7.5 | 5.949 | 0.316 | 0.316 | no | - | - | 1 | 0.1333 |
| colour | region_max | <= | yes | 8 | 6.614 | 7.405 | 7.405 | yes | 6.812 | no | 1 | 0.8 |
| neutral | region_max_dchroma | <= | yes | 2 | 1.423 | 7.087 | 7.087 | yes | 2.839 | yes | 1 | 1 |
| features | region_min | >= | no | 0.8 | 0.8172 | 0.9733 | 0.9948 | no | - | - | 1 | 0.3333 |

## What each limit separates on its own

A control is caught when its value closest to passing is beyond the worst benign value. proposed_partial is the 25 % rule on the caught small negatives only (for review, not a proposal).

- edges.global_min: caught erase, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:6; missed insertion, shift:12, shift:25; proposed_partial 0.981
- edges.region_min: caught erase, removal, scale:1.08, scale:1.15, shift:6; missed insertion, rotate:2.0, scale:1.04, shift:12, shift:25; proposed_partial 0.7539
- added_lines.region_max_len_frac: caught insertion, paste:0.7105, paste:1.0; missed -
- depth.global_max: caught paste:1.0; missed erase, insertion, paste:0.7105, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max: caught -; missed erase, insertion, paste:0.7105, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min: caught -; missed erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max: caught white_balance_strong:1.15,1,0.85; missed floor_L:-15.0, wall_b:10.0; proposed_partial 6.035
- colour.region_max: caught floor_L:-15.0, wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- neutral.region_max_dchroma: caught wall_b:10.0, white_balance_strong:1.15,1,0.85; missed -
- features.region_min: caught erase, removal; missed insertion, paste:0.7105, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6

## Smallest detected change

- shift: - px (rejection rate by px: {"6": 1.0, "12": 0.875, "25": 0.875})
- scale: x1.04 (rejection rate by factor: {"1.04": 1.0, "1.08": 1.0, "1.15": 1.0})

## Benign controls rejected

- cam_r_L3_yatak_odasi_3 blur:1.0: edges win_L3_010 0.7554 >= 0.87

## Negative controls accepted

- cam_r_L3_cocuk_odasi_1 shift:12 on win_L3_008
- cam_r_L3_cocuk_odasi_1 shift:25 on win_L3_008

## Presumed-bad polish attempts (reported only)

None.

## Skipped controls

- none

## Explanations

- edges.global_min does not separate every small negative: worst benign 0.9823 vs best small negative 0.9973; no proposal; misses insertion, shift:12, shift:25; on the small negatives it catches (rotate:2.0, scale:1.04, scale:1.08, shift:6) a threshold of 0.981 would sit 25 % into the gap (proposed_partial)
- edges.region_min does not separate every small negative: worst benign 0.7554 vs best small negative 0.9699; no proposal; misses insertion, rotate:2.0, scale:1.04, shift:12, shift:25; on the small negatives it catches (scale:1.08, shift:6) a threshold of 0.7539 would sit 25 % into the gap (proposed_partial)
- added_lines.region_max_len_frac separates: worst benign 0 vs best gross negative 0.3452; proposed 0.0863 (current 0.04, LOOSER: needs the user OK)
- depth.global_max does not separate every small negative: worst benign 0.01793 vs best small negative 0.0009; no proposal; misses erase, insertion, paste:0.7105, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- depth.region_max does not separate every small negative: worst benign 0.06609 vs best small negative 0.00139; no proposal; misses erase, insertion, paste:0.7105, paste:1.0, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- masks.region_min does not separate every small negative: worst benign 0.6805 vs best small negative 0.9997; no proposal; misses erase, insertion, removal, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- colour.global_max does not separate every small negative: worst benign 5.949 vs best small negative 0.316; no proposal; misses floor_L:-15.0, wall_b:10.0; on the small negatives it catches (white_balance_strong:1.15,1,0.85) a threshold of 6.035 would sit 25 % into the gap (proposed_partial)
- colour.region_max separates: worst benign 6.614 vs best small negative 7.405; proposed 6.812 (current 8)
- neutral.region_max_dchroma separates: worst benign 1.423 vs best small negative 7.087; proposed 2.839 (current 2, LOOSER: needs the user OK)
- features.region_min does not separate every small negative: worst benign 0.8172 vs best small negative 0.9733; no proposal; misses insertion, paste:0.7105, paste:1.0, rotate:2.0, scale:1.04, scale:1.08, scale:1.15, shift:12, shift:25, shift:6
- benign blur:1.0 on cam_r_L3_yatak_odasi_3 rejected: edges win_L3_010 0.7554 (limit >= 0.87)
- negative shift:12 on win_L3_008 (cam_r_L3_cocuk_odasi_1) accepted
- negative shift:25 on win_L3_008 (cam_r_L3_cocuk_odasi_1) accepted

## Warnings

- polish/sweep/polish_manifest.json not found: no presumed-bad attempts
