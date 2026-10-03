# Realism A/B summary

Pairwise forced choice per aspect, both orders, two models (docs/milestone6.md §6). W = B picked in both orders, L = A in both, T = the pick follows the position, NC = a call failed. Decision rule: consensus `photo` W > L with sign p < 0.05, >= 30 decisive pairs from >= 10 rooms, room-level net-win interval above 0, no aspect significantly worse (better; swapped: worse); controls failing for every model: not_measurable; else no_detectable_difference.

Projects: synthetic-01, synthetic-03. Controls: synthetic-01. Models: Qwen (`Qwen/Qwen3-VL-8B-Instruct`), GLM (`zai-org/GLM-4.6V-Flash`).
Signal: Qwen no, GLM no; consensus of Qwen, GLM.

| Set | Decision | Single model | Pairs | Rooms | Projects |
|---|---|---|---|---|---|
| m5_vs_m6 | **not_measurable** | no | 87 | 29 | synthetic-01, synthetic-03 |
| look_alt | **not_measurable** | no | 87 | 29 | synthetic-01, synthetic-03 |

## m5_vs_m6: not_measurable (A = M5 look (a2adcef), B = M6 look)

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 32/1/54 (0.38) | 50/4/33 (0.62) | 20/0/67 | 0.23 (20/87) | 1.91e-06 | [+0.14, +0.32] | +1.34/+1.49 |
| lighting | 35/1/51 (0.41) | 46/5/36 (0.59) | 22/0/65 | 0.25 (22/87) | 4.77e-07 | [+0.16, +0.36] | +1.49/+1.30 |
| furniture | 30/2/55 (0.37) | 50/4/33 (0.62) | 19/0/68 | 0.22 (19/87) | 3.81e-06 | [+0.13, +0.31] | +0.93/+1.08 |
| photo | 35/1/51 (0.41) | 48/4/35 (0.60) | 22/0/65 | 0.25 (22/87) | 4.77e-07 | [+0.16, +0.36] | +1.49/+1.44 |

Per aspect: materials not_measurable, lighting not_measurable, furniture not_measurable, photo not_measurable.
Rooms (consensus per room W/L/T): materials 16/0/13 (p 3.05e-05), lighting 16/0/13 (p 3.05e-05), furniture 15/0/14 (p 6.1e-05), photo 16/0/13 (p 3.05e-05).

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.80 (696 picks), GLM 0.43 (696 picks).

Top decisive cues:
- materials: B wins: material_response (78), material_texture (78), soft_textiles (13), contact_shadows (11), imperfections (6)
- lighting: B wins: light_falloff (88), window_light (67), contact_shadows (55), exposure_colour (6)
- furniture: B wins: furniture_shape (64), soft_textiles (32), small_objects (19), imperfections (6), material_texture (3)
- photo: B wins: fewer_artifacts (80), camera_look (36), imperfections (20), material_texture (12), contact_shadows (9)

## look_alt: not_measurable (A = default look, B = AgX - Punchy)

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/87 (0.00) | 8/35/44 (0.49) | 0/0/87 | 0.00 (0/87) | 1 | [+0.00, +0.00] | -0.06/-0.62 |
| lighting | 0/0/87 (0.00) | 8/35/44 (0.49) | 0/0/87 | 0.00 (0/87) | 1 | [+0.00, +0.00] | -0.09/-0.62 |
| furniture | 0/2/85 (0.02) | 8/35/44 (0.49) | 0/2/85 | 0.00 (0/87) | 0.5 | [-0.07, +0.00] | -0.09/-0.62 |
| photo | 0/0/87 (0.00) | 8/36/43 (0.51) | 0/0/87 | 0.00 (0/87) | 1 | [+0.00, +0.00] | -0.09/-0.64 |

Per aspect: materials not_measurable, lighting not_measurable, furniture not_measurable, photo not_measurable.
Rooms (consensus per room W/L/T): materials 0/0/29 (p 1), lighting 0/0/29 (p 1), furniture 0/1/28 (p 1), photo 0/0/29 (p 1).

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.99 (696 picks), GLM 0.35 (696 picks).

Top decisive cues:
- no decisive pair

## Controls (synthetic-01)

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

## Position bias

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.87 (1840 picks), GLM 0.39 (1840 picks).

## dEV flags

Not active (the nuisance control did not show a brightness preference above the target); 100 A/B pair(s) have |dEV| > 0.3.

## Calls

| Project | Set | Model | Answered | Failed | Stale | Missing | Status |
|---|---|---|---|---|---|---|---|
| synthetic-01 | ctl_flat | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_flat | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_proxy | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_proxy | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_direct | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_direct | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_lowspp | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | ctl_lowspp | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | null_identical | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | null_identical | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | null_reencode | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | null_reencode | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | nuisance_ev | Qwen | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | nuisance_ev | GLM | 16/16 | 0 | 0 | 0 | complete |
| synthetic-01 | m5_vs_m6 | Qwen | 60/60 | 0 | 0 | 0 | complete |
| synthetic-01 | m5_vs_m6 | GLM | 60/60 | 0 | 0 | 0 | complete |
| synthetic-01 | look_alt | Qwen | 60/60 | 0 | 0 | 0 | complete |
| synthetic-01 | look_alt | GLM | 60/60 | 0 | 0 | 0 | complete |
| synthetic-03 | m5_vs_m6 | Qwen | 114/114 | 0 | 0 | 0 | complete |
| synthetic-03 | m5_vs_m6 | GLM | 114/114 | 0 | 0 | 0 | complete |
| synthetic-03 | look_alt | Qwen | 114/114 | 0 | 0 | 0 | complete |
| synthetic-03 | look_alt | GLM | 114/114 | 0 | 0 | 0 | complete |

## Notes

- no signal from Qwen (fails ctl_direct)
- no signal from GLM (fails ctl_lowspp, null_identical, null_reencode)
- halo Qwen 0.97 > 0.80: ask one aspect per call (M7)
- halo GLM 1.00 > 0.80: ask one aspect per call (M7)
- not measurable: the controls fail for every model
