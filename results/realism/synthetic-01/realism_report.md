# Realism A/B – synthetic-01

Pairwise forced choice per aspect, both orders, models Qwen (`Qwen/Qwen3-VL-8B-Instruct`), GLM (`zai-org/GLM-4.6V-Flash`) (docs/milestone6.md §6). W = B picked in both orders, L = A in both, T = the pick follows the position, NC = a call is missing or failed. No decision here: `realism-summary` decides over all A/B projects after the controls.

Pairs: 116 in 9 set(s); dropped cameras: 0; skipped pairs: 0.

## Calls

| Set | Model | Answered | Failed | Stale | Missing | Status |
|---|---|---|---|---|---|---|
| ctl_flat | Qwen | 16/16 | 0 | 0 | 0 | complete |
| ctl_flat | GLM | 16/16 | 0 | 0 | 0 | complete |
| ctl_proxy | Qwen | 16/16 | 0 | 0 | 0 | complete |
| ctl_proxy | GLM | 16/16 | 0 | 0 | 0 | complete |
| ctl_direct | Qwen | 16/16 | 0 | 0 | 0 | complete |
| ctl_direct | GLM | 16/16 | 0 | 0 | 0 | complete |
| ctl_lowspp | Qwen | 16/16 | 0 | 0 | 0 | complete |
| ctl_lowspp | GLM | 16/16 | 0 | 0 | 0 | complete |
| null_identical | Qwen | 16/16 | 0 | 0 | 0 | complete |
| null_identical | GLM | 16/16 | 0 | 0 | 0 | complete |
| null_reencode | Qwen | 16/16 | 0 | 0 | 0 | complete |
| null_reencode | GLM | 16/16 | 0 | 0 | 0 | complete |
| nuisance_ev | Qwen | 16/16 | 0 | 0 | 0 | complete |
| nuisance_ev | GLM | 16/16 | 0 | 0 | 0 | complete |
| m5_vs_m6 | Qwen | 60/60 | 0 | 0 | 0 | complete |
| m5_vs_m6 | GLM | 60/60 | 0 | 0 | 0 | complete |
| look_alt | Qwen | 60/60 | 0 | 0 | 0 | complete |
| look_alt | GLM | 60/60 | 0 | 0 | 0 | complete |

## ctl_flat (A = build --no-textures, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 8/0/0 (1.00) | 8/0/0 (1.00) | 8/0/0 | 1.00 (8/8) | 0.00781 | [+1.00, +1.00] | +4.00/+3.38 |
| lighting | 8/0/0 (1.00) | 8/0/0 (1.00) | 8/0/0 | 1.00 (8/8) | 0.00781 | [+1.00, +1.00] | +4.00/+3.38 |
| furniture | 8/0/0 (1.00) | 8/0/0 (1.00) | 8/0/0 | 1.00 (8/8) | 0.00781 | [+1.00, +1.00] | +2.25/+2.00 |
| photo | 8/0/0 (1.00) | 8/0/0 (1.00) | 8/0/0 | 1.00 (8/8) | 0.00781 | [+1.00, +1.00] | +4.00/+3.38 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.50 (64 picks), GLM 0.50 (64 picks).

Top decisive cues:
- materials: B wins: material_response (32), material_texture (32), imperfections (8), soft_textiles (5), contact_shadows (3)
- lighting: B wins: light_falloff (32), window_light (28), contact_shadows (18), exposure_colour (4)
- furniture: B wins: furniture_shape (28), soft_textiles (15), small_objects (4), imperfections (2)
- photo: B wins: fewer_artifacts (29), camera_look (13), imperfections (10), exposure_colour (6), material_texture (4)

Contact sheets: `contact_realism_ctl_flat_1.jpg`

## ctl_proxy (A = build --proxies, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 7/0/1 (0.88) | 7/0/1 (0.88) | 6/0/2 | 0.75 (6/8) | 0.0312 | [+0.43, +1.00] | +3.62/+3.12 |
| lighting | 7/0/1 (0.88) | 7/0/1 (0.88) | 6/0/2 | 0.75 (6/8) | 0.0312 | [+0.43, +1.00] | +3.50/+2.62 |
| furniture | 8/0/0 (1.00) | 7/0/1 (0.88) | 7/0/1 | 0.88 (7/8) | 0.0156 | [+0.50, +1.00] | +4.00/+3.38 |
| photo | 8/0/0 (1.00) | 7/0/1 (0.88) | 7/0/1 | 0.88 (7/8) | 0.0156 | [+0.50, +1.00] | +4.00/+3.38 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.53 (64 picks), GLM 0.56 (64 picks).

Top decisive cues:
- materials: B wins: material_response (24), material_texture (24), soft_textiles (8), contact_shadows (1), furniture_shape (1)
- lighting: B wins: light_falloff (24), window_light (22), contact_shadows (14)
- furniture: B wins: furniture_shape (28), soft_textiles (17), small_objects (15), imperfections (7)
- photo: B wins: fewer_artifacts (25), camera_look (15), material_texture (7), imperfections (6), contact_shadows (5)

Contact sheets: `contact_realism_ctl_proxy_1.jpg`

## ctl_direct (A = render --max-bounces 0, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 2/0/6 (0.25) | 7/0/1 (0.88) | 2/0/6 | 0.25 (2/8) | 0.5 | [+0.00, +0.57] | +1.00/+2.88 |
| lighting | 2/0/6 (0.25) | 7/0/1 (0.88) | 2/0/6 | 0.25 (2/8) | 0.5 | [+0.00, +0.57] | +1.00/+3.00 |
| furniture | 2/0/6 (0.25) | 7/0/1 (0.88) | 2/0/6 | 0.25 (2/8) | 0.5 | [+0.00, +0.57] | +0.88/+2.25 |
| photo | 2/0/6 (0.25) | 7/0/1 (0.88) | 2/0/6 | 0.25 (2/8) | 0.5 | [+0.00, +0.57] | +1.00/+3.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.88 (64 picks), GLM 0.44 (64 picks).

Top decisive cues:
- materials: B wins: material_response (8), material_texture (8), contact_shadows (3), fewer_artifacts (1)
- lighting: B wins: light_falloff (8), window_light (6), contact_shadows (3), exposure_colour (3)
- furniture: B wins: furniture_shape (8), small_objects (3), imperfections (2)
- photo: B wins: fewer_artifacts (7), camera_look (4), imperfections (1), light_falloff (1), material_texture (1)

Contact sheets: `contact_realism_ctl_direct_1.jpg`

## ctl_lowspp (A = render --samples 4 --no-denoise, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 8/0/0 (1.00) | 5/0/3 (0.62) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.33, +0.89] | +4.00/+2.38 |
| lighting | 8/0/0 (1.00) | 5/0/3 (0.62) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.33, +0.89] | +4.00/+2.38 |
| furniture | 8/0/0 (1.00) | 5/0/3 (0.62) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.33, +0.89] | +4.00/+2.12 |
| photo | 8/0/0 (1.00) | 5/0/3 (0.62) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.33, +0.89] | +4.00/+2.38 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.50 (64 picks), GLM 0.56 (64 picks).

Top decisive cues:
- materials: B wins: material_response (20), material_texture (20), fewer_artifacts (8), soft_textiles (2)
- lighting: B wins: light_falloff (20), window_light (17), contact_shadows (12), exposure_colour (1)
- furniture: B wins: furniture_shape (20), soft_textiles (12), small_objects (8), imperfections (4), material_texture (1)
- photo: B wins: fewer_artifacts (17), camera_look (14), exposure_colour (4), imperfections (4), light_falloff (2)

Contact sheets: `contact_realism_ctl_lowspp_1.jpg`

## null_identical (A and B = the same file)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/8 (0.00) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | -0.12/+0.00 |
| lighting | 0/0/8 (0.00) | 1/2/5 (0.38) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | -0.12/-0.25 |
| furniture | 0/0/8 (0.00) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.00 |
| photo | 0/0/8 (0.00) | 0/1/7 (0.12) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | -0.12/-0.25 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 1.00 (64 picks), GLM 0.53 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism_null_identical_1.jpg`

## null_reencode (A = the normal preview re-encoded as JPEG q70 (PIL), B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/8 (0.00) | 2/0/6 (0.25) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.50 |
| lighting | 0/0/8 (0.00) | 1/0/7 (0.12) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.25 |
| furniture | 0/0/8 (0.00) | 2/0/6 (0.25) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.50 |
| photo | 0/0/8 (0.00) | 1/0/7 (0.12) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.25 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 1.00 (64 picks), GLM 0.09 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism_null_reencode_1.jpg`

## nuisance_ev (A = normal, B = render --ev-offset 0.3)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/8 (0.00) | 1/1/6 (0.25) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.12/+0.00 |
| lighting | 0/0/8 (0.00) | 0/1/7 (0.12) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/-0.25 |
| furniture | 0/0/8 (0.00) | 1/1/6 (0.25) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | -0.12/+0.00 |
| photo | 0/0/8 (0.00) | 1/1/6 (0.25) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 1.00 (64 picks), GLM 0.11 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism_nuisance_ev_1.jpg`

## m5_vs_m6 (A = M5 look (a2adcef), B = M6 look)

30 pairs from 10 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 11/0/19 (0.37) | 23/0/7 (0.77) | 9/0/21 | 0.30 (9/30) | 0.00391 | [+0.13, +0.50] | +1.47/+2.27 |
| lighting | 13/0/17 (0.43) | 23/0/7 (0.77) | 11/0/19 | 0.37 (11/30) | 0.000977 | [+0.17, +0.60] | +1.70/+2.17 |
| furniture | 10/0/20 (0.33) | 23/0/7 (0.77) | 8/0/22 | 0.27 (8/30) | 0.00781 | [+0.10, +0.43] | +0.97/+1.53 |
| photo | 13/0/17 (0.43) | 23/0/7 (0.77) | 11/0/19 | 0.37 (11/30) | 0.000977 | [+0.17, +0.60] | +1.70/+2.30 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.80 (240 picks), GLM 0.45 (240 picks).

Top decisive cues:
- materials: B wins: material_response (36), material_texture (36), soft_textiles (5), imperfections (4), window_light (4)
- lighting: B wins: light_falloff (44), window_light (34), contact_shadows (28), exposure_colour (3)
- furniture: B wins: furniture_shape (29), soft_textiles (15), small_objects (7), material_texture (1)
- photo: B wins: fewer_artifacts (40), camera_look (17), imperfections (11), material_texture (6), contact_shadows (5)

Contact sheets: `contact_realism_m5_vs_m6_1.jpg`, `contact_realism_m5_vs_m6_2.jpg`, `contact_realism_m5_vs_m6_3.jpg`

## look_alt (A = default look, B = AgX - Punchy)

30 pairs from 10 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/30 (0.00) | 6/2/22 (0.27) | 0/0/30 | 0.00 (0/30) | 1 | [+0.00, +0.00] | -0.03/+0.27 |
| lighting | 0/0/30 (0.00) | 6/3/21 (0.30) | 0/0/30 | 0.00 (0/30) | 1 | [+0.00, +0.00] | -0.07/+0.20 |
| furniture | 0/0/30 (0.00) | 6/2/22 (0.27) | 0/0/30 | 0.00 (0/30) | 1 | [+0.00, +0.00] | -0.07/+0.27 |
| photo | 0/0/30 (0.00) | 6/2/22 (0.27) | 0/0/30 | 0.00 (0/30) | 1 | [+0.00, +0.00] | -0.07/+0.27 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 1.00 (240 picks), GLM 0.20 (240 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism_look_alt_1.jpg`, `contact_realism_look_alt_2.jpg`, `contact_realism_look_alt_3.jpg`

## Controls

Targets per model: correct >= 70% (consensus >= 60%), wrong <= 5%. A model has signal when it passes every ctl_* set and both null sets.

| Set | Target | Qwen correct/wrong/T (n) | GLM correct/wrong/T (n) | Consensus correct/wrong/T | Pass |
|---|---|---|---|---|---|
| ctl_flat | B wins materials (A = build --no-textures, B = normal) | 8/0/0 (8) 1.00 | 8/0/0 (8) 1.00 | 8/0/0 (8) | Qwen yes, GLM yes, consensus yes |
| ctl_proxy | B wins furniture (A = build --proxies, B = normal) | 8/0/0 (8) 1.00 | 7/0/1 (8) 0.88 | 7/0/1 (8) | Qwen yes, GLM yes, consensus yes |
| ctl_direct | B wins lighting (A = render --max-bounces 0, B = normal) | 2/0/6 (8) 0.25 | 7/0/1 (8) 0.88 | 2/0/6 (8) | Qwen no, GLM yes, consensus no |
| ctl_lowspp | B wins photo (A = render --samples 4 --no-denoise, B = normal) | 8/0/0 (8) 1.00 | 5/0/3 (8) 0.62 | 5/0/3 (8) | Qwen yes, GLM no, consensus yes |

null_identical (8 pairs, target T >= 90% of pair-aspects): Qwen T 1.00 of 32 (pass), no flip; GLM T 0.88 of 32 (FAIL), flips: null_identical:cam_r_L0_mutfak_3/lighting: L, null_identical:cam_r_L0_yatak_odasi_2/lighting: L, null_identical:cam_r_L0_yatak_odasi_2/photo: L, null_identical:cam_r_L1_banyo_1/lighting: W
null_reencode (8 pairs, target W <= 10%): Qwen W 0.00 of 32 (pass); GLM W 0.19 of 32 (FAIL)
nuisance_ev (8 pairs, measured dEV 0.12): brighter image wins Qwen 0.00 of 32; GLM 0.09 of 32 (flag above 30%)
halo (non-target aspects following the target winner on ctl_*): Qwen 0.97 of 78 -> ask one aspect per call (M7); GLM 1.00 of 81 -> ask one aspect per call (M7)
Signal: Qwen no, GLM no.

## Pairs

| Pair | Room | dEV | materials | lighting | furniture | photo |
|---|---|---|---|---|---|---|
| ctl_flat:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.52 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.71 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.44 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.47 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L1_banyo_1 | r_L1_banyo | -0.15 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.59 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.35 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.67 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.15 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.15 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.12 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.00 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L1_banyo_1 | r_L1_banyo | -0.36 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| ctl_proxy:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.12 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.12 | T (T/W) | T (T/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.02 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 1.09 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| ctl_direct:cam_r_L0_mutfak_3 | r_L0_mutfak | 1.20 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 1.04 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| ctl_direct:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 1.21 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| ctl_direct:cam_r_L1_banyo_1 | r_L1_banyo | 0.86 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.69 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| ctl_direct:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 1.32 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| ctl_direct:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 1.33 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| ctl_lowspp:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.64 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L0_mutfak_3 | r_L0_mutfak | 1.16 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| ctl_lowspp:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.64 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.68 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L1_banyo_1 | r_L1_banyo | 0.05 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.81 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 0.76 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| ctl_lowspp:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.96 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| null_identical:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_mutfak_3 | r_L0_mutfak | 0.00 | T (T/T) | T (T/L) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.00 | T (T/T) | T (T/L) | T (T/T) | T (T/L) |
| null_identical:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L1_banyo_1 | r_L1_banyo | 0.00 | T (T/T) | T (T/W) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.00 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| null_reencode:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.00 | T (T/W) | T (T/T) | T (T/W) | T (T/T) |
| null_reencode:cam_r_L1_banyo_1 | r_L1_banyo | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.12 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L0_mutfak_3 | r_L0_mutfak | 0.14 | T (T/W) | T (T/T) | T (T/W) | T (T/W) |
| nuisance_ev:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.11 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.12 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| nuisance_ev:cam_r_L1_banyo_1 | r_L1_banyo | 0.14 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.10 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 0.07 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.14 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_banyo_1 | r_L0_banyo | -0.05 | W (W/W) | W (W/W) | T (T/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_banyo_2 | r_L0_banyo | 0.03 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_banyo_3 | r_L0_banyo | -0.04 | W (W/W) | W (W/W) | T (T/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_hol_1 | r_L0_hol | -0.00 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_hol_2 | r_L0_hol | -0.00 | W (W/W) | W (W/W) | T (T/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_hol_3 | r_L0_hol | -0.01 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_mutfak_1 | r_L0_mutfak | 0.00 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.11 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_mutfak_3 | r_L0_mutfak | 0.03 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_salon_1 | r_L0_salon | -0.03 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_salon_2 | r_L0_salon | -0.05 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L0_salon_3 | r_L0_salon | 0.00 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.03 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.10 | T (T/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | -0.00 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_banyo_1 | r_L1_banyo | 0.02 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_banyo_2 | r_L1_banyo | -0.04 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_banyo_3 | r_L1_banyo | -0.03 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| m5_vs_m6:cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | -0.02 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | -0.08 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | -0.01 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| m5_vs_m6:cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | 0.01 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.09 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.05 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_hol_1 | r_L1_hol | 0.07 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_hol_2 | r_L1_hol | -0.26 | T (T/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_hol_3 | r_L1_hol | 0.13 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | -0.04 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| m5_vs_m6:cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | -0.04 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| m5_vs_m6:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.04 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| look_alt:cam_r_L0_banyo_1 | r_L0_banyo | -0.40 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_banyo_2 | r_L0_banyo | -0.39 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_banyo_3 | r_L0_banyo | -0.44 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_hol_1 | r_L0_hol | -0.45 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L0_hol_2 | r_L0_hol | -0.47 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_hol_3 | r_L0_hol | -0.48 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L0_mutfak_1 | r_L0_mutfak | -0.42 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.39 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.43 | T (T/T) | T (T/L) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_salon_1 | r_L0_salon | -0.37 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_salon_2 | r_L0_salon | -0.37 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_salon_3 | r_L0_salon | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.32 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.34 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | -0.44 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_banyo_1 | r_L1_banyo | -0.44 | T (T/L) | T (T/L) | T (T/L) | T (T/L) |
| look_alt:cam_r_L1_banyo_2 | r_L1_banyo | -0.45 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_banyo_3 | r_L1_banyo | -0.45 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | -0.42 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | -0.42 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | -0.36 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.39 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.39 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_hol_1 | r_L1_hol | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_hol_2 | r_L1_hol | -0.43 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_hol_3 | r_L1_hol | -0.41 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | -0.39 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| look_alt:cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | -0.40 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| look_alt:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.44 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
