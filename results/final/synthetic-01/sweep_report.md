# Sweep report: synthetic-01

Polish sweep: 4 views, 11 settings, 44 attempts. Gate calibration: run. Vision-check calibration: run. Thresholds and the ladder are set by hand from these numbers and committed with them (§8.3); a threshold looser than §4.2 needs the user's OK.

## Polish sweep

| id | setting | k | views | gated | accepted | rate | failing checks | mean time | preferred | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | s 0.125 depth x0.8 | 1 | 4 | 4 | 0 | 0 % | depth 4, masks 1 | 3.0 s | - | 0 |
| S2 | s 0.25 depth x0.8 | 2 | 4 | 4 | 0 | 0 % | depth 3, masks 2 | 4.8 s | - | 0 |
| S3 | s 0.375 depth x0.8 | 3 | 4 | 4 | 0 | 0 % | depth 3, masks 3 | 6.7 s | - | 0 |
| S4 | s 0.5 depth x0.8 | 4 | 4 | 4 | 0 | 0 % | depth 4, edges 4, masks 3 | 8.6 s | - | 0 |
| S5 | s 0.25 canny x0.8 | 5 | 4 | 4 | 1 | 25 % | depth 3, masks 1 | 4.8 s | - | 0 |
| S6 | s 0.375 canny x0.8 | 6 | 4 | 4 | 0 | 0 % | depth 3, masks 3 | 6.7 s | - | 0 |
| S7 | s 0.25 geometry x0.8 | 7 | 4 | 4 | 1 | 25 % | depth 3, masks 1 | 4.8 s | - | 0 |
| S8 | s 0.375 geometry x0.8 | 8 | 4 | 4 | 2 | 50 % | depth 2, masks 1 | 6.7 s | 0/2 | 0 |
| S9 | s 0.375 depth x0.8 1536x864 | 9 | 4 | 4 | 2 | 50 % | depth 2, masks 2 | 3.7 s | 0/2 | 0 |
| S10 | s 0.375 depth x0.8 anchor | 10 | 4 | 4 | 3 | 75 % | depth 1 | 7.0 s | 0/2 | 0 |
| S11 | s 0.75 no control [presumed_bad] | 11 | 4 | 4 | 0 | 0 % | depth 4, edges 4, masks 4, added_lines 3, colour 2 | 7.4 s | - | 0 |

Median global gate metrics per setting:

| id | edges | added_lines | depth | masks | colour | neutral | features |
|---|---|---|---|---|---|---|---|
| S1 | 0.993 | 0.000 | 0.024 | - | 1.462 | - | 0.858 |
| S2 | 0.985 | 0.000 | 0.017 | - | 1.844 | - | 0.835 |
| S3 | 0.973 | 0.000 | 0.021 | - | 2.255 | - | 0.815 |
| S4 | 0.930 | 0.000 | 0.031 | - | 2.949 | - | 0.781 |
| S5 | 0.989 | 0.000 | 0.024 | - | 1.796 | - | 0.836 |
| S6 | 0.972 | 0.000 | 0.031 | - | 2.213 | - | 0.821 |
| S7 | 0.986 | 0.000 | 0.023 | - | 1.832 | - | 0.838 |
| S8 | 0.979 | 0.000 | 0.018 | - | 2.206 | - | 0.823 |
| S9 | 0.963 | 0.000 | 0.026 | - | 2.330 | - | 0.814 |
| S10 | 0.990 | 0.000 | 0.011 | - | 1.738 | - | 0.917 |
| S11 | 0.321 | 0.175 | 0.062 | - | 4.982 | - | 0.651 |

### Decisions per view

A accepted, R rejected (failing checks), err failed, - not gated.

| view | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L1_ebeveyn_yatak_odasi_2 | R (depth, masks) | R (depth, masks) | R (depth, masks) | R (depth, edges, masks) | R (depth, masks) | R (depth, masks) | R (depth, masks) | R (depth, masks) | R (depth, masks) | A | R (added_lines, colour, depth, edges, masks) |
| cam_r_L0_mutfak_2 | R (depth) | R (masks) | R (masks) | R (depth, edges, masks) | A | R (masks) | A | A | A | A | R (depth, edges, masks) |
| cam_r_L1_hol_1 | R (depth) | R (depth) | R (depth, masks) | R (depth, edges, masks) | R (depth) | R (depth, masks) | R (depth) | A | R (depth, masks) | A | R (added_lines, colour, depth, edges, masks) |
| cam_r_L0_hol_2 | R (depth) | R (depth) | R (depth) | R (depth, edges) | R (depth) | R (depth) | R (depth) | R (depth) | A | R (depth) | R (added_lines, depth, edges, masks) |

### Settings accepted on every view (information for the ladder)

None: no grid setting passed the gate on every view.

Current ladder (polish.yaml): s 0.375 depth x0.8; s 0.25 depth x0.8; s 0.125 depth x0.8.

## Gate calibration

| rate | value |
|---|---|
| benign accepted | 88 % |
| negatives rejected | 91 % |

By control:

| control | value |
|---|---|
| benign:blur:1.0 | kind benign, control blur, magnitude 1.000, n 8, accepted 7, rejected 1, rate 0.875 |
| benign:exposure:-0.3 | kind benign, control exposure, magnitude -0.300, n 8, accepted 8, rejected 0, rate 1.000 |
| benign:exposure:0.3 | kind benign, control exposure, magnitude 0.300, n 8, accepted 7, rejected 1, rate 0.875 |
| benign:jpeg:75 | kind benign, control jpeg, magnitude 75, n 8, accepted 5, rejected 3, rate 0.625 |
| benign:local_contrast:1.5 | kind benign, control local_contrast, magnitude 1.500, n 8, accepted 7, rejected 1, rate 0.875 |
| benign:noise:3.0 | kind benign, control noise, magnitude 3.000, n 8, accepted 6, rejected 2, rate 0.750 |
| benign:unsharp:0.5 | kind benign, control unsharp, magnitude 0.500, n 8, accepted 8, rejected 0, rate 1.000 |
| benign:white_balance:1.03,1,0.97 | kind benign, control white_balance, magnitude 1.03,1,0.97, n 8, accepted 8, rejected 0, rate 1.000 |
| negative:erase | kind negative, control erase, magnitude -, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:floor_L:-15.0 | kind negative, control floor_L, magnitude -15.000, n 7, accepted 5, rejected 2, rate 0.286 |
| negative:insertion | kind negative, control insertion, magnitude -, n 8, accepted 0, rejected 8, rate 1.000 |
| negative:paste:0.6265 | kind negative, control paste, magnitude 0.626, n 1, accepted 0, rejected 1, rate 1.000 |
| negative:paste:1.0 | kind negative, control paste, magnitude 1.000, n 7, accepted 0, rejected 7, rate 1.000 |
| negative:removal | kind negative, control removal, magnitude -, n 8, accepted 0, rejected 8, rate 1.000 |
| negative:rotate:2.0 | kind negative, control rotate, magnitude 2.000, n 16, accepted 1, rejected 15, rate 0.938 |
| negative:scale:1.04 | kind negative, control scale, magnitude 1.040, n 16, accepted 3, rejected 13, rate 0.812 |
| negative:scale:1.08 | kind negative, control scale, magnitude 1.080, n 16, accepted 1, rejected 15, rate 0.938 |
| negative:scale:1.15 | kind negative, control scale, magnitude 1.150, n 16, accepted 1, rejected 15, rate 0.938 |
| negative:shift:12 | kind negative, control shift, magnitude 12, n 16, accepted 2, rejected 14, rate 0.875 |
| negative:shift:25 | kind negative, control shift, magnitude 25, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:shift:6 | kind negative, control shift, magnitude 6, n 16, accepted 1, rejected 15, rate 0.938 |
| negative:wall_b:10.0 | kind negative, control wall_b, magnitude 10.000, n 8, accepted 1, rejected 7, rate 0.875 |
| negative:white_balance_strong:1.15,1,0.85 | kind negative, control white_balance_strong, magnitude 1.15,1,0.85, n 8, accepted 1, rejected 7, rate 0.875 |
| presumed_bad:presumed_bad:0.75 | kind presumed_bad, control presumed_bad, magnitude 0.750, n 4, accepted 0, rejected 4, rate 1.000 |

Benign controls (must be accepted):

| control | n | accepted | rejected |
|---|---|---|---|
| exposure | 16 | 15 | 1 |
| white_balance | 8 | 8 | 0 |
| blur | 8 | 7 | 1 |
| jpeg | 8 | 5 | 3 |
| unsharp | 8 | 8 | 0 |
| local_contrast | 8 | 7 | 1 |
| noise | 8 | 6 | 2 |

Negative controls (must be rejected):

| control | n | accepted | rejected |
|---|---|---|---|
| shift | 48 | 3 | 45 |
| scale | 48 | 5 | 43 |
| rotate | 16 | 1 | 15 |
| erase | 16 | 0 | 16 |
| paste | 8 | 0 | 8 |
| white_balance_strong | 8 | 1 | 7 |
| wall_b | 8 | 1 | 7 |
| floor_L | 7 | 5 | 2 |
| removal | 8 | 0 | 8 |
| insertion | 8 | 0 | 8 |

Presumed-bad polish attempts (reported only):

| control | n | accepted | rejected |
|---|---|---|---|
| presumed_bad | 4 | 0 | 4 |

Misses (benign rejected, negative accepted):

- cam_r_L1_ebeveyn_yatak_odasi_2: blur 1.00 -> reject (edges)
- cam_r_L1_ebeveyn_yatak_odasi_2: jpeg 75 -> reject (depth, masks)
- cam_r_L1_hol_1: jpeg 75 -> reject (depth)
- cam_r_L1_hol_1: noise 3.00 -> reject (depth)
- cam_r_L0_hol_2: jpeg 75 -> reject (depth)
- cam_r_L0_hol_2: noise 3.00 -> reject (depth)
- cam_r_L0_yatak_odasi_1: exposure 0.30 -> reject (depth)
- cam_r_L0_yatak_odasi_1: local_contrast 1.50 -> reject (depth)
- cam_r_L1_ebeveyn_yatak_odasi_2: floor_L -15.00 -> accept
- cam_r_L0_mutfak_2: wall_b 10.00 -> accept
- cam_r_L0_mutfak_2: floor_L -15.00 -> accept
- cam_r_L1_hol_1: shift 6 -> accept
- cam_r_L1_hol_1: scale 1.04 -> accept
- cam_r_L1_hol_1: rotate 2.00 -> accept
- cam_r_L1_hol_1: floor_L -15.00 -> accept
- cam_r_L0_hol_2: shift 12 -> accept
- cam_r_L0_hol_2: scale 1.04 -> accept
- cam_r_L0_hol_2: scale 1.08 -> accept
- cam_r_L0_hol_2: scale 1.15 -> accept
- cam_r_L0_hol_2: floor_L -15.00 -> accept
- cam_r_L0_salon_1: shift 12 -> accept
- cam_r_L0_banyo_2: white_balance_strong 1.15,1,0.85 -> accept
- cam_r_L0_yatak_odasi_1: floor_L -15.00 -> accept
- cam_r_L1_yatak_odasi_3: scale 1.04 -> accept

Per metric (proposal = worst benign + 25 % of the gap to the best small negative):

| check | worst benign | best small negative | best negative | separates | proposed | current |
|---|---|---|---|---|---|---|
| edges | - | - | - | - | - | global_min 0.950, region_min 0.850, region_min_ref_px 200, radius_px 3, canny sigma 1.500, low 25, high 75 |
| added_lines | - | - | - | - | - | region_max_len_frac 0.040, min_len_frac 0.040, unmatched_frac 0.700 |
| depth | - | - | - | - | - | global_max 0.020, region_max 0.050, region_min_frac 0.010 |
| masks | - | - | - | - | - | region_min 0.900, region_min_frac 0.005, sam_reliable_min 0.700 |
| colour | - | - | - | - | - | global_max 10.000, region_max 15.000, region_min_frac 0.010 |
| neutral | - | - | - | - | - | region_max_dchroma 5.000 |
| features | - | - | - | - | - | region_min 0.800, region_min_frac 0.010 |

Smallest detected change: shift_px 25, scale -, by_magnitude shift 6 0.938, 12 0.875, 25 1.000, scale 1.04 0.812, 1.08 0.938, 1.15 0.938.

Explanations:

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

## Vision-check calibration

| metric | value | target | result |
|---|---|---|---|
| fa_missing | 0.091 | <= 0.05 | MISSED |
| fa_extra | 0.000 | <= 0.1 | met |
| removal_flagged | 1.000 | >= 0.8 | met |
| removal_confirmed | 0.625 | >= 0.6 | met |
| insertion | 0.000 | >= 0.6 | MISSED |
| decoy_accept | qwen 0.000, glm 0.000 | <= 0.1 | met |

Advisory: yes (fa_missing 0.0909 misses <= 0.05; insertion 0.0 misses >= 0.6).

Per model (Cycles views):

| model | answer rate | decoy accepted | false missing (single pass) |
|---|---|---|---|
| qwen | 100 % | 0 % | 19 % |
| glm | 100 % | 0 % | 9 % |

Plan A/B: not adopted: source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
| metric | value |
|---|---|
| fa_missing_without | 0.051 |
| fa_missing_with | 0.077 |
| fa_extra_without | 0.000 |
| fa_extra_with | 0.000 |
| removal_confirmed_without | 0.625 |
| removal_confirmed_with | 0.750 |

## Warnings

None.
