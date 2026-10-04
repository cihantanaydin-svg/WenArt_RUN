# Realism A/B v2 – synthetic-01

Pairwise forced choice, one aspect per call, both orders (the question and the answer enum name the images in the order of the call), models Qwen (`Qwen/Qwen3-VL-8B-Instruct`), GLM (`zai-org/GLM-4.6V-Flash`) (docs/milestone7.md §8.2). W = B picked in both orders, L = A in both, T = the pick follows the position, NC = a call is missing or failed. No decision here: `realism2-summary` decides over all A/B projects after the controls.

Pairs: 56 in 7 set(s); dropped cameras: 0; skipped pairs: 0.

## Calls

| Set | Model | Answered | Failed | Stale | Missing | Status |
|---|---|---|---|---|---|---|
| ctl_flat | Qwen | 64/64 | 0 | 0 | 0 | complete |
| ctl_flat | GLM | 64/64 | 0 | 0 | 0 | complete |
| ctl_proxy | Qwen | 64/64 | 0 | 0 | 0 | complete |
| ctl_proxy | GLM | 64/64 | 0 | 0 | 0 | complete |
| ctl_direct | Qwen | 64/64 | 0 | 0 | 0 | complete |
| ctl_direct | GLM | 64/64 | 0 | 0 | 0 | complete |
| ctl_lowspp | Qwen | 64/64 | 0 | 0 | 0 | complete |
| ctl_lowspp | GLM | 64/64 | 0 | 0 | 0 | complete |
| null_identical | Qwen | 64/64 | 0 | 0 | 0 | complete |
| null_identical | GLM | 64/64 | 0 | 0 | 0 | complete |
| null_reencode | Qwen | 64/64 | 0 | 0 | 0 | complete |
| null_reencode | GLM | 64/64 | 0 | 0 | 0 | complete |
| nuisance_ev | Qwen | 64/64 | 0 | 0 | 0 | complete |
| nuisance_ev | GLM | 64/64 | 0 | 0 | 0 | complete |

## ctl_flat (A = build --no-textures, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 8/0/0 (1.00) | 8/0/0 (1.00) | 8/0/0 | 1.00 (8/8) | 0.00781 | [+1.00, +1.00] | +2.00/+2.00 |
| lighting | 7/0/1 (0.88) | 5/0/3 (0.62) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.17, +0.90] | +1.75/+1.25 |
| furniture | 7/0/1 (0.88) | 5/0/3 (0.62) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.17, +0.90] | +1.75/+1.25 |
| photo | 6/0/2 (0.75) | 8/0/0 (1.00) | 6/0/2 | 0.75 (6/8) | 0.0312 | [+0.40, +1.00] | +1.50/+2.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.44 (64 picks), GLM 0.41 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_ctl_flat_1.jpg`

## ctl_proxy (A = build --proxies, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 6/0/2 (0.75) | 6/1/1 (0.88) | 6/0/2 | 0.75 (6/8) | 0.0312 | [+0.43, +1.00] | +1.50/+1.25 |
| lighting | 5/1/2 (0.75) | 4/1/3 (0.62) | 3/0/5 | 0.38 (3/8) | 0.25 | [+0.00, +0.83] | +1.00/+0.75 |
| furniture | 7/0/1 (0.88) | 7/0/1 (0.88) | 6/0/2 | 0.75 (6/8) | 0.0312 | [+0.43, +1.00] | +1.75/+1.75 |
| photo | 5/1/2 (0.75) | 5/1/2 (0.75) | 4/0/4 | 0.50 (4/8) | 0.125 | [+0.12, +0.88] | +1.00/+1.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.39 (64 picks), GLM 0.42 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_ctl_proxy_1.jpg`

## ctl_direct (A = render --max-bounces 0, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 7/0/1 (0.88) | 5/0/3 (0.62) | 4/0/4 | 0.50 (4/8) | 0.125 | [+0.00, +0.89] | +1.75/+1.25 |
| lighting | 6/0/2 (0.75) | 2/0/6 (0.25) | 1/0/7 | 0.12 (1/8) | 1 | [+0.00, +0.33] | +1.50/+0.50 |
| furniture | 7/0/1 (0.88) | 5/0/3 (0.62) | 4/0/4 | 0.50 (4/8) | 0.125 | [+0.00, +0.89] | +1.75/+1.25 |
| photo | 7/0/1 (0.88) | 8/0/0 (1.00) | 7/0/1 | 0.88 (7/8) | 0.0156 | [+0.50, +1.00] | +1.75/+2.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.45 (64 picks), GLM 0.31 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_ctl_direct_1.jpg`

## ctl_lowspp (A = render --samples 4 --no-denoise, B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 8/0/0 (1.00) | 2/5/1 (0.88) | 2/0/6 | 0.25 (2/8) | 0.5 | [+0.00, +0.57] | +2.00/-0.75 |
| lighting | 8/0/0 (1.00) | 3/2/3 (0.62) | 3/0/5 | 0.38 (3/8) | 0.25 | [+0.00, +0.86] | +2.00/+0.25 |
| furniture | 8/0/0 (1.00) | 5/1/2 (0.75) | 5/0/3 | 0.62 (5/8) | 0.0625 | [+0.33, +0.89] | +2.00/+1.00 |
| photo | 7/0/1 (0.88) | 5/1/2 (0.75) | 4/0/4 | 0.50 (4/8) | 0.125 | [+0.17, +0.78] | +1.75/+1.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.48 (64 picks), GLM 0.47 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_ctl_lowspp_1.jpg`

## null_identical (A and B = the same file)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 0/0/8 (0.00) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.00 |
| lighting | 0/0/8 (0.00) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.00 |
| furniture | 0/0/8 (0.00) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.00 |
| photo | 0/0/8 (0.00) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.00/+0.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 1.00 (64 picks), GLM 0.00 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_null_identical_1.jpg`

## null_reencode (A = the normal preview re-encoded as JPEG q70 (PIL), B = normal)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 3/0/5 (0.38) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.75/+0.00 |
| lighting | 7/0/1 (0.88) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +1.75/+0.00 |
| furniture | 6/0/2 (0.75) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +1.50/+0.00 |
| photo | 6/0/2 (0.75) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +1.50/+0.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.56 (64 picks), GLM 0.00 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_null_reencode_1.jpg`

## nuisance_ev (A = normal, B = render --ev-offset 0.3)

8 pairs from 5 rooms; consensus of Qwen, GLM.

| Aspect | Qwen W/L/T (consistency) | GLM W/L/T (consistency) | Consensus W/L/T | Win rate W/N | Sign p | Net win 95 % (rooms) | Mean graded Qwen/GLM |
|---|---|---|---|---|---|---|---|
| materials | 1/0/7 (0.12) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.25/+0.00 |
| lighting | 3/0/5 (0.38) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.75/+0.00 |
| furniture | 3/0/5 (0.38) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.75/+0.00 |
| photo | 3/0/5 (0.38) | 0/0/8 (0.00) | 0/0/8 | 0.00 (0/8) | 1 | [+0.00, +0.00] | +0.75/+0.00 |

Position bias (share of image_1 picks, about 0.5 expected): Qwen 0.84 (64 picks), GLM 0.00 (64 picks).

Top decisive cues:
- no decisive pair

Contact sheets: `contact_realism2_nuisance_ev_1.jpg`

## Controls

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

## Pairs

| Pair | Room | dEV | materials | lighting | furniture | photo |
|---|---|---|---|---|---|---|
| ctl_flat:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.52 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.71 | W (W/W) | T (W/T) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.44 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.47 | W (W/W) | W (W/W) | T (W/T) | T (T/W) |
| ctl_flat:cam_r_L1_banyo_1 | r_L1_banyo | -0.15 | W (W/W) | T (T/T) | T (T/T) | T (T/W) |
| ctl_flat:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.59 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.35 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_flat:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.67 | W (W/W) | T (W/T) | T (W/T) | W (W/W) |
| ctl_proxy:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.15 | W (W/W) | T (W/T) | W (W/W) | T (W/T) |
| ctl_proxy:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.15 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.12 | W (W/W) | T (T/W) | W (W/W) | T (T/W) |
| ctl_proxy:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.00 | W (W/W) | T (W/T) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L1_banyo_1 | r_L1_banyo | -0.36 | T (T/L) | T (T/L) | T (W/T) | T (T/L) |
| ctl_proxy:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.12 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_proxy:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.12 | T (T/T) | T (L/T) | T (T/W) | T (L/T) |
| ctl_proxy:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.02 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 1.09 | T (W/T) | T (W/T) | T (W/T) | W (W/W) |
| ctl_direct:cam_r_L0_mutfak_3 | r_L0_mutfak | 1.20 | W (W/W) | T (W/T) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 1.04 | W (W/W) | T (W/T) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 1.21 | T (W/T) | T (W/T) | T (W/T) | W (W/W) |
| ctl_direct:cam_r_L1_banyo_1 | r_L1_banyo | 0.86 | T (T/W) | T (T/W) | T (T/W) | T (T/W) |
| ctl_direct:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.69 | W (W/W) | T (T/T) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 1.32 | W (W/W) | W (W/W) | W (W/W) | W (W/W) |
| ctl_direct:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 1.33 | T (W/T) | T (W/T) | T (W/T) | W (W/W) |
| ctl_lowspp:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.64 | T (W/L) | W (W/W) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L0_mutfak_3 | r_L0_mutfak | 1.16 | T (W/L) | T (W/L) | T (W/L) | T (W/T) |
| ctl_lowspp:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.64 | T (W/T) | T (W/T) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.68 | T (W/L) | W (W/W) | T (W/T) | W (W/W) |
| ctl_lowspp:cam_r_L1_banyo_1 | r_L1_banyo | 0.05 | W (W/W) | W (W/W) | W (W/W) | T (T/W) |
| ctl_lowspp:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.81 | W (W/W) | T (W/T) | W (W/W) | W (W/W) |
| ctl_lowspp:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 0.76 | T (W/L) | T (W/T) | W (W/W) | T (W/T) |
| ctl_lowspp:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.96 | T (W/L) | T (W/L) | T (W/T) | T (W/L) |
| null_identical:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_mutfak_3 | r_L0_mutfak | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L1_banyo_1 | r_L1_banyo | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_identical:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | -0.00 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| null_reencode:cam_r_L0_mutfak_3 | r_L0_mutfak | -0.00 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| null_reencode:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | -0.00 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| null_reencode:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | -0.00 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| null_reencode:cam_r_L1_banyo_1 | r_L1_banyo | -0.00 | T (T/T) | T (W/T) | T (T/T) | T (T/T) |
| null_reencode:cam_r_L0_mutfak_2 | r_L0_mutfak | -0.00 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| null_reencode:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | -0.00 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| null_reencode:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | -0.00 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | 0.12 | T (T/T) | T (T/T) | T (W/T) | T (T/T) |
| nuisance_ev:cam_r_L0_mutfak_3 | r_L0_mutfak | 0.14 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | 0.11 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | 0.12 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_banyo_1 | r_L1_banyo | 0.14 | T (W/T) | T (W/T) | T (W/T) | T (W/T) |
| nuisance_ev:cam_r_L0_mutfak_2 | r_L0_mutfak | 0.10 | T (T/T) | T (W/T) | T (W/T) | T (W/T) |
| nuisance_ev:cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | 0.07 | T (T/T) | T (T/T) | T (T/T) | T (T/T) |
| nuisance_ev:cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | 0.14 | T (T/T) | T (W/T) | T (T/T) | T (W/T) |

## Warnings

- synthetic-05: 23 camera(s) without both previews (rendered without --alt-look?): not in the look_alt ranking
