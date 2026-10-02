# Sweep report: synthetic-03

Polish sweep: 4 views, 11 settings, 44 attempts. Gate calibration: run. Vision-check calibration: not run. Thresholds and the ladder are set by hand from these numbers and committed with them (§8.3); a threshold looser than §4.2 needs the user's OK.

## Polish sweep

| id | setting | k | views | gated | accepted | rate | failing checks | mean time | preferred | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 | s 0.125 depth x0.8 | 1 | 4 | 4 | 3 | 75 % | masks 1 | 3.3 s | - | 0 |
| S2 | s 0.25 depth x0.8 | 2 | 4 | 4 | 2 | 50 % | depth 2, masks 1 | 5.4 s | - | 0 |
| S3 | s 0.375 depth x0.8 | 3 | 4 | 4 | 2 | 50 % | depth 2, edges 1 | 7.3 s | - | 0 |
| S4 | s 0.5 depth x0.8 | 4 | 4 | 4 | 0 | 0 % | depth 4, edges 3, masks 2 | 9.2 s | - | 0 |
| S5 | s 0.25 canny x0.8 | 5 | 4 | 4 | 2 | 50 % | depth 2, masks 1 | 5.1 s | - | 0 |
| S6 | s 0.375 canny x0.8 | 6 | 4 | 4 | 3 | 75 % | depth 1 | 7.5 s | - | 0 |
| S7 | s 0.25 geometry x0.8 | 7 | 4 | 4 | 4 | 100 % | - | 5.1 s | - | 0 |
| S8 | s 0.375 geometry x0.8 | 8 | 4 | 4 | 2 | 50 % | depth 1, masks 1 | 6.9 s | - | 0 |
| S9 | s 0.375 depth x0.8 1536x864 | 9 | 4 | 4 | 2 | 50 % | depth 2, edges 1, masks 1 | 3.7 s | - | 0 |
| S10 | s 0.375 depth x0.8 anchor | 10 | 4 | 4 | 4 | 100 % | - | 7.4 s | - | 0 |
| S11 | s 0.75 no control [presumed_bad] | 11 | 4 | 4 | 0 | 0 % | added_lines 4, depth 4, edges 4, masks 4 | 7.3 s | - | 0 |

Median global gate metrics per setting:

| id | edges | added_lines | depth | masks | colour | neutral | features |
|---|---|---|---|---|---|---|---|
| S1 | 0.994 | 0.000 | 0.005 | - | 1.588 | - | 0.849 |
| S2 | 0.985 | 0.000 | 0.006 | - | 1.830 | - | 0.828 |
| S3 | 0.981 | 0.000 | 0.008 | - | 2.175 | - | 0.813 |
| S4 | 0.924 | 0.000 | 0.014 | - | 2.695 | - | 0.795 |
| S5 | 0.993 | 0.000 | 0.009 | - | 1.871 | - | 0.829 |
| S6 | 0.987 | 0.000 | 0.009 | - | 2.212 | - | 0.821 |
| S7 | 0.993 | 0.000 | 0.008 | - | 1.842 | - | 0.834 |
| S8 | 0.986 | 0.000 | 0.008 | - | 2.135 | - | 0.820 |
| S9 | 0.971 | 0.000 | 0.009 | - | 2.340 | - | 0.824 |
| S10 | 0.996 | 0.000 | 0.004 | - | 2.351 | - | 0.914 |
| S11 | 0.370 | 0.475 | 0.028 | - | 5.793 | - | 0.697 |

### Decisions per view

A accepted, R rejected (failing checks), err failed, - not gated.

| view | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 | S11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_hol_1 | A | A | A | R (depth, masks) | A | A | A | A | A | A | R (added_lines, depth, edges, masks) |
| cam_r_L0_hol_1 | A | A | A | R (depth, edges) | A | A | A | A | A | A | R (added_lines, depth, edges, masks) |
| cam_r_L-1_yatak_odasi_3 | R (masks) | R (depth, masks) | R (depth) | R (depth, edges, masks) | R (depth, masks) | A | A | R (masks) | R (depth, masks) | A | R (added_lines, depth, edges, masks) |
| cam_r_L0_salon_3 | A | R (depth) | R (depth, edges) | R (depth, edges) | R (depth) | R (depth) | A | R (depth) | R (depth, edges) | A | R (added_lines, depth, edges, masks) |

### Settings accepted on every view (information for the ladder)

- S10: s 0.375 depth x0.8 anchor
- S7: s 0.25 geometry x0.8

Current ladder (polish.yaml): s 0.375 depth x0.8; s 0.25 depth x0.8; s 0.125 depth x0.8.

## Gate calibration

| rate | value |
|---|---|
| benign accepted | 89 % |
| negatives rejected | 92 % |

By control:

| control | value |
|---|---|
| benign:blur:1.0 | kind benign, control blur, magnitude 1.000, n 8, accepted 7, rejected 1, rate 0.875 |
| benign:exposure:-0.3 | kind benign, control exposure, magnitude -0.300, n 8, accepted 8, rejected 0, rate 1.000 |
| benign:exposure:0.3 | kind benign, control exposure, magnitude 0.300, n 8, accepted 8, rejected 0, rate 1.000 |
| benign:jpeg:75 | kind benign, control jpeg, magnitude 75, n 8, accepted 5, rejected 3, rate 0.625 |
| benign:local_contrast:1.5 | kind benign, control local_contrast, magnitude 1.500, n 8, accepted 6, rejected 2, rate 0.750 |
| benign:noise:3.0 | kind benign, control noise, magnitude 3.000, n 8, accepted 8, rejected 0, rate 1.000 |
| benign:unsharp:0.5 | kind benign, control unsharp, magnitude 0.500, n 8, accepted 7, rejected 1, rate 0.875 |
| benign:white_balance:1.03,1,0.97 | kind benign, control white_balance, magnitude 1.03,1,0.97, n 8, accepted 8, rejected 0, rate 1.000 |
| negative:erase | kind negative, control erase, magnitude -, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:floor_L:-15.0 | kind negative, control floor_L, magnitude -15.000, n 7, accepted 7, rejected 0, rate 0.000 |
| negative:insertion | kind negative, control insertion, magnitude -, n 7, accepted 0, rejected 7, rate 1.000 |
| negative:paste:0.906 | kind negative, control paste, magnitude 0.906, n 1, accepted 0, rejected 1, rate 1.000 |
| negative:paste:0.9122 | kind negative, control paste, magnitude 0.912, n 7, accepted 0, rejected 7, rate 1.000 |
| negative:removal | kind negative, control removal, magnitude -, n 7, accepted 0, rejected 7, rate 1.000 |
| negative:rotate:2.0 | kind negative, control rotate, magnitude 2.000, n 16, accepted 2, rejected 14, rate 0.875 |
| negative:scale:1.04 | kind negative, control scale, magnitude 1.040, n 16, accepted 1, rejected 15, rate 0.938 |
| negative:scale:1.08 | kind negative, control scale, magnitude 1.080, n 16, accepted 1, rejected 15, rate 0.938 |
| negative:scale:1.15 | kind negative, control scale, magnitude 1.150, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:shift:12 | kind negative, control shift, magnitude 12, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:shift:25 | kind negative, control shift, magnitude 25, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:shift:6 | kind negative, control shift, magnitude 6, n 16, accepted 0, rejected 16, rate 1.000 |
| negative:wall_b:10.0 | kind negative, control wall_b, magnitude 10.000, n 8, accepted 1, rejected 7, rate 0.875 |
| negative:white_balance_strong:1.15,1,0.85 | kind negative, control white_balance_strong, magnitude 1.15,1,0.85, n 8, accepted 2, rejected 6, rate 0.750 |
| presumed_bad:presumed_bad:0.75 | kind presumed_bad, control presumed_bad, magnitude 0.750, n 4, accepted 0, rejected 4, rate 1.000 |

Benign controls (must be accepted):

| control | n | accepted | rejected |
|---|---|---|---|
| exposure | 16 | 16 | 0 |
| white_balance | 8 | 8 | 0 |
| blur | 8 | 7 | 1 |
| jpeg | 8 | 5 | 3 |
| unsharp | 8 | 7 | 1 |
| local_contrast | 8 | 6 | 2 |
| noise | 8 | 8 | 0 |

Negative controls (must be rejected):

| control | n | accepted | rejected |
|---|---|---|---|
| shift | 48 | 0 | 48 |
| scale | 48 | 2 | 46 |
| rotate | 16 | 2 | 14 |
| erase | 16 | 0 | 16 |
| paste | 8 | 0 | 8 |
| white_balance_strong | 8 | 2 | 6 |
| wall_b | 8 | 1 | 7 |
| floor_L | 7 | 7 | 0 |
| removal | 7 | 0 | 7 |
| insertion | 7 | 0 | 7 |

Presumed-bad polish attempts (reported only):

| control | n | accepted | rejected |
|---|---|---|---|
| presumed_bad | 4 | 0 | 4 |

Misses (benign rejected, negative accepted):

- cam_r_L-1_yatak_odasi_3: jpeg 75 -> reject (masks)
- cam_r_L1_cocuk_odasi_2: jpeg 75 -> reject (depth)
- cam_r_L1_hol_1: blur 1.00 -> reject (masks)
- cam_r_L0_antre_2: jpeg 75 -> reject (depth)
- cam_r_L0_antre_2: unsharp 0.50 -> reject (depth)
- cam_r_L0_antre_2: local_contrast 1.50 -> reject (depth)
- cam_r_L0_mutfak_2: local_contrast 1.50 -> reject (depth)
- cam_r_L-1_hol_1: scale 1.04 -> accept
- cam_r_L-1_hol_1: scale 1.08 -> accept
- cam_r_L-1_hol_1: floor_L -15.00 -> accept
- cam_r_L0_hol_1: rotate 2.00 -> accept
- cam_r_L0_hol_1: floor_L -15.00 -> accept
- cam_r_L-1_yatak_odasi_3: wall_b 10.00 -> accept
- cam_r_L-1_yatak_odasi_3: floor_L -15.00 -> accept
- cam_r_L0_salon_3: floor_L -15.00 -> accept
- cam_r_L1_cocuk_odasi_2: white_balance_strong 1.15,1,0.85 -> accept
- cam_r_L1_cocuk_odasi_2: floor_L -15.00 -> accept
- cam_r_L1_hol_1: rotate 2.00 -> accept
- cam_r_L1_hol_1: floor_L -15.00 -> accept
- cam_r_L0_mutfak_2: white_balance_strong 1.15,1,0.85 -> accept
- cam_r_L0_mutfak_2: floor_L -15.00 -> accept

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

Smallest detected change: shift_px 6, scale 1.150, by_magnitude shift 6 1.000, 12 1.000, 25 1.000, scale 1.04 0.938, 1.08 0.938, 1.15 1.000.

Explanations:

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

## Vision-check calibration

Not run (check/check_calibration.json not found).

## Warnings

None.
