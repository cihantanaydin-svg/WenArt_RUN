# Realism A/B v2 summary

Pairwise forced choice, one aspect per call, both orders, two models (docs/milestone7.md §8.2). W = B picked in both orders, L = A in both, T = the pick follows the position, NC = a call failed. Decision rule: consensus `photo` W > L with sign p < 0.05, >= 30 decisive pairs from >= 10 rooms, room-level net-win interval above 0, no aspect significantly worse (better; swapped: worse); controls failing for every model: not_measurable; else no_detectable_difference.

Projects: synthetic-03. Controls: synthetic-01. Models: Qwen (`Qwen/Qwen3-VL-8B-Instruct`), GLM (`zai-org/GLM-4.6V-Flash`).
Signal: Qwen no, GLM no; consensus of Qwen, GLM.

| Set | Decision | Single model | Pairs | Rooms | Projects |
|---|---|---|---|---|---|
| look_alt | **not_measurable** | no | 32 | 18 | synthetic-03 |

## look_alt: not_measurable (A = AgX - Punchy (the M7 default look), B = look None)

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 7/0/25 (0.22) | 0/0/32 (0.00) | 0/0/32 | 0.00 (0/32) | 1 | [+0.00, +0.00] | +0.44/+0.00 |
| lighting | 21/0/11 (0.66) | 0/0/32 (0.00) | 0/0/32 | 0.00 (0/32) | 1 | [+0.00, +0.00] | +1.31/+0.00 |
| furniture | 9/0/23 (0.28) | 0/0/32 (0.00) | 0/0/32 | 0.00 (0/32) | 1 | [+0.00, +0.00] | +0.56/+0.00 |
| photo | 21/0/11 (0.66) | 1/0/31 (0.03) | 1/0/31 | 0.03 (1/32) | 1 | [+0.00, +0.10] | +1.31/+0.06 |

Per aspect: materials not_measurable, lighting not_measurable, furniture not_measurable, photo not_measurable.
Rooms (consensus per room W/L/T): materials 0/0/18 (p 1), lighting 0/0/18 (p 1), furniture 0/0/18 (p 1), photo 1/0/17 (p 1).

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.74 (256 picks), GLM 0.00 (256 picks).

Top decisive cues:
- no decisive pair

## Controls (synthetic-01)

Targets per model: correct >= 70% (consensus >= 60%), wrong <= 5%. A model has signal when it passes every ctl_* set and both null sets.

| Set | Target | Qwen correct/wrong/T (n) | GLM correct/wrong/T (n) | Consensus correct/wrong/T | Pass |
|---|---|---|---|---|---|
| ctl_flat | B wins materials (A = build --no-textures, B = normal) | 8/0/0 (8) 1.00 | 8/0/0 (8) 1.00 | 8/0/0 (8) | Qwen yes, GLM yes, consensus yes |
| ctl_proxy | B wins furniture (A = build --proxies, B = normal) | 7/0/1 (8) 0.88 | 7/0/1 (8) 0.88 | 6/0/2 (8) | Qwen yes, GLM yes, consensus yes |
| ctl_direct | B wins lighting (A = render --max-bounces 0, B = normal) | 6/0/2 (8) 0.75 | 2/0/6 (8) 0.25 | 1/0/7 (8) | Qwen yes, GLM no, consensus no |
| ctl_lowspp | B wins photo (A = render --samples 4 --no-denoise, B = normal) | 7/0/1 (8) 0.88 | 5/1/2 (8) 0.62 | 4/0/4 (8) | Qwen yes, GLM no, consensus no |

null_identical (8 pairs, target T >= 90% of pair-aspects): Qwen T 1.00 of 32 (pass), no flip; GLM T 1.00 of 32 (pass), no flip
null_reencode (8 pairs, target W <= 10%): Qwen W 0.69 of 32 (FAIL); GLM W 0.00 of 32 (pass)
nuisance_ev (8 pairs, measured dEV 0.12): brighter image wins Qwen 0.31 of 32; GLM 0.00 of 32 -> above 30%: A/B pairs with |dEV| > 0.3 are flagged
halo (non-target aspects following the target winner on ctl_*): Qwen 0.89 of 84 -> ask one aspect per call (M7); GLM 0.72 of 69
Signal: Qwen no, GLM no.

## Position bias

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.74 (256 picks), GLM 0.00 (256 picks).

## dEV flags

Active: the A/B pairs with |dEV| > 0.3 (B brighter when > 0):
- synthetic-03 look_alt:cam_r_L1_cocuk_odasi_3: dEV +0.35
- synthetic-03 look_alt:cam_r_L1_ebeveyn_yatak_odasi_3: dEV +0.35
- synthetic-03 look_alt:cam_r_L0_mutfak_1: dEV +0.34
- synthetic-03 look_alt:cam_r_L1_ebeveyn_yatak_odasi_2: dEV +0.35
- synthetic-03 look_alt:cam_r_L-1_banyo_2: dEV +0.46
- synthetic-03 look_alt:cam_r_L0_mutfak_2: dEV +0.33
- synthetic-03 look_alt:cam_r_L0_yatak_odasi_2: dEV +0.39
- synthetic-03 look_alt:cam_r_L1_cocuk_odasi_1: dEV +0.33
- synthetic-03 look_alt:cam_r_L0_salon_1: dEV +0.39
- synthetic-03 look_alt:cam_r_L1_banyo_3: dEV +0.36
- synthetic-03 look_alt:cam_r_L1_banyo_2: dEV +0.41
- synthetic-03 look_alt:cam_r_L-1_yatak_odasi_1: dEV +0.48
- synthetic-03 look_alt:cam_r_L0_yatak_odasi_3: dEV +0.32
- synthetic-03 look_alt:cam_r_L-1_banyo_1: dEV +0.45
- synthetic-03 look_alt:cam_r_L1_yatak_odasi_1: dEV +0.48
- synthetic-03 look_alt:cam_r_L1_yatak_odasi_3: dEV +0.46
- synthetic-03 look_alt:cam_r_L0_salon_3: dEV +0.45
- synthetic-03 look_alt:cam_r_L-1_yatak_odasi_2: dEV +0.48
- synthetic-03 look_alt:cam_r_L0_hol_1: dEV +0.48
- synthetic-03 look_alt:cam_r_L0_antre_2: dEV +0.46
- synthetic-03 look_alt:cam_r_L-1_wc_1: dEV +0.42
- synthetic-03 look_alt:cam_r_L0_antre_1: dEV +0.47
- synthetic-03 look_alt:cam_r_L-1_wc_2: dEV +0.42
- synthetic-03 look_alt:cam_r_L0_kiler_1: dEV +0.31
- synthetic-03 look_alt:cam_r_L1_hol_1: dEV +0.50
- synthetic-03 look_alt:cam_r_L-1_hol_1: dEV +0.49
- synthetic-03 look_alt:cam_r_L0_hol_2: dEV +0.45
- synthetic-03 look_alt:cam_r_L1_hol_2: dEV +0.50
- synthetic-03 look_alt:cam_r_L0_wc_1: dEV +0.41
- synthetic-03 look_alt:cam_r_L-1_hol_2: dEV +0.52
- synthetic-03 look_alt:cam_r_L-1_kiler_1: dEV +0.60
- synthetic-03 look_alt:cam_r_L-1_kiler_2_1: dEV +0.58

## Calls

| Project | Set | Model | Answered | Failed | Stale | Missing | Status |
|---|---|---|---|---|---|---|---|
| synthetic-03 | look_alt | Qwen | 256/256 | 0 | 0 | 0 | complete |
| synthetic-03 | look_alt | GLM | 256/256 | 0 | 0 | 0 | complete |

## Notes

- no signal from Qwen (fails null_reencode)
- no signal from GLM (fails ctl_direct, ctl_lowspp)
- halo Qwen 0.89 > 0.80: ask one aspect per call (M7)
- nuisance_ev: the brighter image wins more than 30% for Qwen: A/B pairs with |dEV| > 0.3 are flagged
- not measurable: the controls fail for every model
