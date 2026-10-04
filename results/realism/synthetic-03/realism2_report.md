# Realism A/B v2 – synthetic-03

Pairwise forced choice, one aspect per call, both orders (the question and the answer enum name the images in the order of the call), models Qwen (`Qwen/Qwen3-VL-8B-Instruct`), GLM (`zai-org/GLM-4.6V-Flash`) (docs/milestone7.md §8.2). W = B picked in both orders, L = A in both, T = the pick follows the position, NC = a call is missing or failed. No decision here: `realism2-summary` decides over all A/B projects after the controls.

Pairs: 32 in 1 set(s); dropped cameras: 0; skipped pairs: 0.

## Calls

| Set | Model | Answered | Failed | Stale | Missing | Status |
|---|---|---|---|---|---|---|
| look_alt | Qwen | 256/256 | 0 | 0 | 0 | complete |
| look_alt | GLM | 256/256 | 0 | 0 | 0 | complete |

## look_alt (A = AgX - Punchy (the M7 default look), B = look None)

32 pairs from 18 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 7/0/25 (0.22) | 0/0/32 (0.00) | 0/0/32 | 0.00 (0/32) | 1 | [+0.00, +0.00] | +0.44/+0.00 |
| lighting | 21/0/11 (0.66) | 0/0/32 (0.00) | 0/0/32 | 0.00 (0/32) | 1 | [+0.00, +0.00] | +1.31/+0.00 |
| furniture | 9/0/23 (0.28) | 0/0/32 (0.00) | 0/0/32 | 0.00 (0/32) | 1 | [+0.00, +0.00] | +0.56/+0.00 |
| photo | 21/0/11 (0.66) | 1/0/31 (0.03) | 1/0/31 | 0.03 (1/32) | 1 | [+0.00, +0.10] | +1.31/+0.06 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.74 (256 picks), GLM 0.00 (256 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_look_alt_1.jpg`, `contact_realism2_look_alt_2.jpg`, `contact_realism2_look_alt_3.jpg`, `contact_realism2_look_alt_4.jpg`

## Pairs

| Pair | Room | dEV | materials | lighting | furniture | photo |
|---|---|---|---|---|---|---|
| look_alt:cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | 0.35 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.35 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L0_mutfak_1 | r_L0_mutfak | 0.34 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.35 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_banyo_2 | r_L-1_banyo | 0.46 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.33 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.39 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | 0.33 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L0_salon_1 | r_L0_salon | 0.39 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L1_banyo_3 | r_L1_banyo | 0.36 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L1_banyo_2 | r_L1_banyo | 0.41 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | 0.48 | T (T/T) | T (W/T) | T (W/T) | T (T/T) |
| look_alt:cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | 0.32 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_banyo_1 | r_L-1_banyo | 0.45 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | 0.48 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.46 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L0_salon_3 | r_L0_salon | 0.45 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | 0.48 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L0_hol_1 | r_L0_hol | 0.48 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L0_antre_2 | r_L0_antre | 0.46 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L-1_wc_1 | r_L-1_wc | 0.42 | T (T/T) | T (W/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_antre_1 | r_L0_antre | 0.47 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_wc_2 | r_L-1_wc | 0.42 | T (W/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L0_kiler_1 | r_L0_kiler | 0.31 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_hol_1 | r_L1_hol | 0.50 | T (T/T) | T (T/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L-1_hol_1 | r_L-1_hol | 0.49 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L0_hol_2 | r_L0_hol | 0.45 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L1_hol_2 | r_L1_hol | 0.50 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L0_wc_1 | r_L0_wc | 0.41 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L-1_hol_2 | r_L-1_hol | 0.52 | T (T/T) | T (T/T) | T (T/T) | T (W/T) |
| look_alt:cam_r_L-1_kiler_1 | r_L-1_kiler | 0.60 | T (W/T) | T (W/T) | T (T/T) | W (W/W) |
| look_alt:cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | 0.58 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |

## Warnings

- synthetic-05: 23 camera(s) without both previews (rendered without --alt-look?): not in the look_alt ranking
