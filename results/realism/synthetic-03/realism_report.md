# Realism A/B – synthetic-03

Pairwise forced choice per aspect, both orders, models Qwen (`Qwen/Qwen3-VL-8B-Instruct`), GLM (`zai-org/GLM-4.6V-Flash`) (docs/milestone6.md §6). W = B picked in both orders, L = A in both, T = the pick follows the position, NC = a call is missing or failed. No decision here: `realism-summary` decides over all A/B projects after the controls.

Pairs: 114 in 2 set(s); dropped cameras: 0; skipped pairs: 0.

## Calls

| Set | Model | Answered | Failed | Stale | Missing | Status |
|---|---|---|---|---|---|---|
| m5_vs_m6 | Qwen | 114/114 | 0 | 0 | 0 | complete |
| m5_vs_m6 | GLM | 114/114 | 0 | 0 | 0 | complete |
| look_alt | Qwen | 114/114 | 0 | 0 | 0 | complete |
| look_alt | GLM | 114/114 | 0 | 0 | 0 | complete |

## m5_vs_m6 (A = M5 look (a2adcef), B = M6 look)

57 pairs from 19 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 21/1/35 (0.39) | 27/4/26 (0.54) | 11/0/46 | 0.19 (11/57) | 0.000977 | [+0.11, +0.28] | +1.28/+1.09 |
| lighting | 22/1/34 (0.40) | 23/5/29 (0.49) | 11/0/46 | 0.19 (11/57) | 0.000977 | [+0.11, +0.28] | +1.39/+0.84 |
| furniture | 20/2/35 (0.39) | 27/4/26 (0.54) | 11/0/46 | 0.19 (11/57) | 0.000977 | [+0.11, +0.28] | +0.91/+0.84 |
| photo | 22/1/34 (0.40) | 25/4/28 (0.51) | 11/0/46 | 0.19 (11/57) | 0.000977 | [+0.11, +0.28] | +1.39/+0.98 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.80 (456 picks), GLM 0.42 (456 picks).

Top decisive cues:
- materials: B wins: material_response (42), material_texture (42), contact_shadows (9), soft_textiles (8), fewer_artifacts (2)
- lighting: B wins: light_falloff (44), window_light (33), contact_shadows (27), exposure_colour (3)
- furniture: B wins: furniture_shape (35), soft_textiles (17), small_objects (12), imperfections (6), material_texture (2)
- photo: B wins: fewer_artifacts (40), camera_look (19), imperfections (9), material_texture (6), exposure_colour (5)

Contact sheets: `contact_realism_m5_vs_m6_1.jpg`, `contact_realism_m5_vs_m6_2.jpg`, `contact_realism_m5_vs_m6_3.jpg`, `contact_realism_m5_vs_m6_4.jpg`, `contact_realism_m5_vs_m6_5.jpg`, `contact_realism_m5_vs_m6_6.jpg`

## look_alt (A = default look, B = AgX - Punchy)

57 pairs from 19 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/57 (0.00) | 2/33/22 (0.61) | 0/0/57 | 0.00 (0/57) | 1 | [+0.00, +0.00] | -0.07/-1.09 |
| lighting | 0/0/57 (0.00) | 2/32/23 (0.60) | 0/0/57 | 0.00 (0/57) | 1 | [+0.00, +0.00] | -0.10/-1.05 |
| furniture | 0/2/55 (0.04) | 2/33/22 (0.61) | 0/2/55 | 0.00 (0/57) | 0.5 | [-0.11, +0.00] | -0.10/-1.09 |
| photo | 0/0/57 (0.00) | 2/34/21 (0.63) | 0/0/57 | 0.00 (0/57) | 1 | [+0.00, +0.00] | -0.10/-1.12 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.99 (456 picks), GLM 0.43 (456 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism_look_alt_1.jpg`, `contact_realism_look_alt_2.jpg`, `contact_realism_look_alt_3.jpg`, `contact_realism_look_alt_4.jpg`, `contact_realism_look_alt_5.jpg`, `contact_realism_look_alt_6.jpg`

## Pairs

| Pair | Room | dEV | materials | lighting | furniture | photo |
|---|---|---|---|---|---|---|
| m5_vs_m6:cam_r_L-1_banyo_1 | r_L-1_banyo | 2.75 | T (L/W) | T (L/W) | T (L/W) | T (L/W) |
| m5_vs_m6:cam_r_L-1_banyo_2 | r_L-1_banyo | 1.55 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L-1_banyo_3 | r_L-1_banyo | 2.20 | T (W/T) | T (W/T) | T (T/T) | T (W/T) |
| m5_vs_m6:cam_r_L-1_hol_1 | r_L-1_hol | 0.03 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L-1_hol_2 | r_L-1_hol | 0.04 | T (T/T) | T (T/T) | T (L/T) | T (T/T) |
| m5_vs_m6:cam_r_L-1_hol_3 | r_L-1_hol | -0.18 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L-1_kiler_1 | r_L-1_kiler | -0.36 | T (T/T) | T (T/T) | T (W/T) | T (T/T) |
| m5_vs_m6:cam_r_L-1_kiler_2 | r_L-1_kiler | -1.17 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | -0.41 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L-1_kiler_2_2 | r_L-1_kiler_2 | -1.03 | T (T/L) | T (T/T) | T (T/L) | T (T/L) |
| m5_vs_m6:cam_r_L-1_kiler_2_3 | r_L-1_kiler_2 | -0.20 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L-1_kiler_3 | r_L-1_kiler | -0.13 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L-1_wc_1 | r_L-1_wc | 0.02 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L-1_wc_2 | r_L-1_wc | 0.09 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L-1_wc_3 | r_L-1_wc | 0.08 | T (W/T) | T (W/T) | T (T/T) | T (W/T) |
| m5_vs_m6:cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | -0.02 | T (T/W) | T (T/T) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | 0.23 | T (T/T) | T (T/L) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | 0.07 | T (T/W) | T (T/T) | T (T/W) | T (T/T) |
| m5_vs_m6:cam_r_L0_antre_1 | r_L0_antre | -0.39 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_antre_2 | r_L0_antre | -1.22 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_antre_3 | r_L0_antre | -0.02 | T (W/L) | T (W/L) | T (W/L) | T (W/L) |
| m5_vs_m6:cam_r_L0_hol_1 | r_L0_hol | 0.04 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_hol_2 | r_L0_hol | 0.06 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_hol_3 | r_L0_hol | 0.01 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_kiler_1 | r_L0_kiler | 0.31 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_kiler_2 | r_L0_kiler | 0.31 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_kiler_3 | r_L0_kiler | 0.07 | T (T/W) | T (T/L) | T (T/W) | T (T/T) |
| m5_vs_m6:cam_r_L0_mutfak_1 | r_L0_mutfak | 0.21 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_mutfak_2 | r_L0_mutfak | 1.04 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.00 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_salon_1 | r_L0_salon | -0.03 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_salon_2 | r_L0_salon | -0.04 | T (T/W) | T (T/T) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_salon_3 | r_L0_salon | -0.06 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_wc_1 | r_L0_wc | 0.16 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L0_wc_2 | r_L0_wc | -0.06 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_wc_3 | r_L0_wc | -0.00 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.05 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.06 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | 0.01 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L1_balkon_1 | r_L1_balkon | -0.16 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_balkon_2 | r_L1_balkon | -0.09 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_balkon_3 | r_L1_balkon | 0.00 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| m5_vs_m6:cam_r_L1_banyo_1 | r_L1_banyo | 0.14 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_banyo_2 | r_L1_banyo | 0.01 | T (W/L) | T (W/L) | T (T/L) | T (W/L) |
| m5_vs_m6:cam_r_L1_banyo_3 | r_L1_banyo | 0.74 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | -0.02 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | -0.10 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | -0.06 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | -0.04 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.02 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.04 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_hol_1 | r_L1_hol | 0.03 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L1_hol_2 | r_L1_hol | -0.12 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_hol_3 | r_L1_hol | -0.18 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | 0.10 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | 0.13 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.05 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| look_alt:cam_r_L-1_banyo_1 | r_L-1_banyo | -0.49 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_banyo_2 | r_L-1_banyo | -0.42 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_banyo_3 | r_L-1_banyo | -0.48 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_hol_1 | r_L-1_hol | -0.66 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_hol_2 | r_L-1_hol | -0.84 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_hol_3 | r_L-1_hol | -1.17 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_kiler_1 | r_L-1_kiler | -0.91 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_kiler_2 | r_L-1_kiler | -0.74 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | -0.87 | T (T/L) | T (T/L) | L (L/L) | T (T/L) |
| look_alt:cam_r_L-1_kiler_2_2 | r_L-1_kiler_2 | -0.72 | T (T/L) | T (T/L) | L (L/L) | T (T/L) |
| look_alt:cam_r_L-1_kiler_2_3 | r_L-1_kiler_2 | -0.62 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_kiler_3 | r_L-1_kiler | -0.64 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_wc_1 | r_L-1_wc | -0.43 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_wc_2 | r_L-1_wc | -0.42 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L-1_wc_3 | r_L-1_wc | -0.41 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | -0.67 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | -0.73 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | -0.53 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_antre_1 | r_L0_antre | -0.47 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_antre_2 | r_L0_antre | -0.62 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_antre_3 | r_L0_antre | -0.43 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_hol_1 | r_L0_hol | -0.66 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_hol_2 | r_L0_hol | -0.94 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_hol_3 | r_L0_hol | -1.16 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_kiler_1 | r_L0_kiler | -0.82 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_kiler_2 | r_L0_kiler | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_kiler_3 | r_L0_kiler | -0.88 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_mutfak_1 | r_L0_mutfak | -0.44 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.45 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.46 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_salon_1 | r_L0_salon | -0.35 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_salon_2 | r_L0_salon | -0.43 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_salon_3 | r_L0_salon | -0.53 | T (T/L) | T (T/T) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_wc_1 | r_L0_wc | -0.42 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_wc_2 | r_L0_wc | -0.42 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_wc_3 | r_L0_wc | -0.41 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.40 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.34 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | -0.55 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_balkon_1 | r_L1_balkon | -0.50 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_balkon_2 | r_L1_balkon | -0.34 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_balkon_3 | r_L1_balkon | -0.61 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_banyo_1 | r_L1_banyo | -0.43 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_banyo_2 | r_L1_banyo | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_banyo_3 | r_L1_banyo | -0.36 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | -0.84 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | -0.44 | T (T/T) | T (T/L) | T (T/T) | T (T/L) |
| look_alt:cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | -0.34 | T (T/T) | T (T/T) | T (T/T) | T (T/L) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.43 | T (T/L) | T (T/T) | T (T/L) | T (T/T) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.53 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_hol_1 | r_L1_hol | -0.56 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_hol_2 | r_L1_hol | -0.92 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_hol_3 | r_L1_hol | -1.22 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | -0.53 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | -0.58 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.43 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
