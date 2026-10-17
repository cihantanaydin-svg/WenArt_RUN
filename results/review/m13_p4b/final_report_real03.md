# Final report: real03

89 views: 0 polished, 89 Cycles (gate_validation 6, not_run 83). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 89 |
| interior / exterior views | 83 / 6 |
| variant | base |
| polished | 0 |
| Cycles | 89 (gate_validation 6, not_run 83) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 12 |
| needs_review views | 12 |
| unverified pieces in view (sum over views) | 129 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 18 |
| exposure | -7.17 .. +2.83 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| window pull | 75 view(s), -4 .. 0 EV |
| camera policy | agent 3, m5 3, search 83 |
| camera score (min / mean / max) | 0.21 / 2.54 / 4.42 |
| rooms by number of views | 19 with 0, 8 with 1, 9 with 2, 19 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 4.9 min / 17.3 min / 3.1 min |
| seconds: polish / gate / check | - / - / 19.1 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real03.blend](3d/real03.blend) | 292.4 MB |
| [real03.glb](3d/real03.glb) | 771.7 MB |

89 cameras; textures scaled to at most 1024 px (257 scaled) for the download.

## AI decor

80 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 22 rooms; 4 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

- r_L0_ebeveyn_odasi_4: rules (no slot for AI decor)

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- camera cam_r_L0_banyo_1: no free camera point in the room; room's inner point inside a tall proxy, camera at the nearest point clear of tall proxies
- camera cam_r_L0_banyo_2_1: no free camera point in the room; room's inner point inside a tall proxy, camera at the nearest point clear of tall proxies
- camera cam_r_L0_banyo_7_1: no free camera point in the room; room's inner point inside a tall proxy, camera at the nearest point clear of tall proxies
- camera cam_r_L0_oda_10_1: no free camera point in the room; camera at the room's inner point
- camera cam_r_L0_oda_7_1: no free camera point in the room; camera at the room's inner point
- 6 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L0_162, f_L0_163, f_L0_184, f_L0_203, f_L0_205, f_L0_207
- 2 exterior view(s) dropped, no camera place worked: ext_5, ext_6
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- drawn-piece check: 7 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 28 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

Not recorded: the gate calibration and validation did not run.

### Exterior views

Exterior decision: **not_validated**. The exterior views are the Cycles render; the rooms are not affected.

| item | value |
|---|---|
| benign exterior comparisons accepted | -, 0 comparisons |
| negative exterior comparisons rejected | -, 0 comparisons |

Reasons:

- gate/gate_calibration.json missing: gate calibrate did not run or failed

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Side-by-side sheets (Cycles | polished)

None: the polish did not run in this run.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.67 | -1 | search 0.55 | D1 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2_1 | r_L0_banyo_2 | L0 | cycles | not_run | - | - | info | - | - | +2.67 | -1 | search 0.55 | - | 0 | no | [preview](cam_r_L0_banyo_2_1_final_preview.jpg) [plan](cam_r_L0_banyo_2_1_plan.jpg) |
| cam_r_L0_banyo_3_1 | r_L0_banyo_3 | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 1.91 | D4 | 0 | no | [preview](cam_r_L0_banyo_3_1_final_preview.jpg) [plan](cam_r_L0_banyo_3_1_plan.jpg) |
| cam_r_L0_banyo_4_1 | r_L0_banyo_4 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | - | search 2.43 | D3 | 1 | no | [preview](cam_r_L0_banyo_4_1_final_preview.jpg) [plan](cam_r_L0_banyo_4_1_plan.jpg) |
| cam_r_L0_banyo_4_2 | r_L0_banyo_4 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.11 | D3 | 1 | no | [preview](cam_r_L0_banyo_4_2_final_preview.jpg) [plan](cam_r_L0_banyo_4_2_plan.jpg) |
| cam_r_L0_banyo_5_1 | r_L0_banyo_5 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 1.87 | D3 | 1 | no | [preview](cam_r_L0_banyo_5_1_final_preview.jpg) [plan](cam_r_L0_banyo_5_1_plan.jpg) |
| cam_r_L0_banyo_5_2 | r_L0_banyo_5 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 1.64 | D3 | 1 | no | [preview](cam_r_L0_banyo_5_2_final_preview.jpg) [plan](cam_r_L0_banyo_5_2_plan.jpg) |
| cam_r_L0_banyo_6_1 | r_L0_banyo_6 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 1.08 | D2 | 0 | no | [preview](cam_r_L0_banyo_6_1_final_preview.jpg) [plan](cam_r_L0_banyo_6_1_plan.jpg) |
| cam_r_L0_banyo_6_2 | r_L0_banyo_6 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 0.59 | D2 | 0 | no | [preview](cam_r_L0_banyo_6_2_final_preview.jpg) [plan](cam_r_L0_banyo_6_2_plan.jpg) |
| cam_r_L0_banyo_7_1 | r_L0_banyo_7 | L0 | cycles | not_run | - | - | info | - | - | +2.67 | - | search 0.68 | D1 | 0 | no | [preview](cam_r_L0_banyo_7_1_final_preview.jpg) [plan](cam_r_L0_banyo_7_1_plan.jpg) |
| cam_r_L0_banyo_8_1 | r_L0_banyo_8 | L0 | cycles | not_run | - | - | info | - | - | +2.83 | - | search 1.28 | D2 | 0 | no | [preview](cam_r_L0_banyo_8_1_final_preview.jpg) [plan](cam_r_L0_banyo_8_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_1 | r_L0_ebeveyn_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.00 | -3 | search 3.34 | D3 A3 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2 | r_L0_ebeveyn_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.17 | -1 | search 1.78 | D3 A2 | 0 | yes | [preview](cam_r_L0_ebeveyn_odasi_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2_1 | r_L0_ebeveyn_odasi_2 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 3.04 | D3 A1 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_2_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2_2 | r_L0_ebeveyn_odasi_2 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 2.97 | D3 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_2_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2_3 | r_L0_ebeveyn_odasi_2 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 2.95 | D4 A2 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_2_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_3_1 | r_L0_ebeveyn_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | +0.83 | -3 | search 3.62 | D3 A3 | 0 | yes | [preview](cam_r_L0_ebeveyn_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_3_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_3_2 | r_L0_ebeveyn_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | -1 | search 1.89 | D3 A1 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_3_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_4_1 | r_L0_ebeveyn_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | +0.17 | -2 | search 2.91 | D3 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_4_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_4_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_4_2 | r_L0_ebeveyn_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | +0.33 | - | search 2.88 | D4 A1 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_4_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_4_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_4_3 | r_L0_ebeveyn_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | -2 | search 2.86 | D3 A1 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_4_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_4_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_5_1 | r_L0_ebeveyn_odasi_5 | L0 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 3.46 | D2 A2 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_5_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_5_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_5_2 | r_L0_ebeveyn_odasi_5 | L0 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 3.40 | D2 A2 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_5_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_5_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_5_3 | r_L0_ebeveyn_odasi_5 | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -1 | search 2.21 | D3 A1 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_5_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_5_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_6_1 | r_L0_ebeveyn_odasi_6 | L0 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 3.16 | D2 A3 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_6_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_6_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_6_2 | r_L0_ebeveyn_odasi_6 | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -1 | search 1.68 | D3 A2 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_6_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_6_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_1 | r_L0_ebeveyn_odasi_m_k_a | L0 | cycles | not_run | - | - | info | - | - | +1.00 | -3 | search 2.84 | D5 A2 | 3 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2 | r_L0_ebeveyn_odasi_m_k_a | L0 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 2.66 | D4 A1 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_1 | r_L0_ebeveyn_odasi_m_k_a_2 | L0 | cycles | not_run | - | - | info | - | - | +1.00 | -3 | search 3.02 | D5 A2 | 3 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_2 | r_L0_ebeveyn_odasi_m_k_a_2 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -3 | search 2.80 | D3 A1 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_3 | r_L0_ebeveyn_odasi_m_k_a_2 | L0 | cycles | not_run | - | - | info | - | - | +1.00 | 0 | search 2.37 | D3 A2 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_3 | r_L0_ebeveyn_odasi_m_k_a | L0 | cycles | not_run | - | - | info | - | - | +1.33 | 0 | search 2.01 | D4 A1 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_3_plan.jpg) |
| cam_r_L0_giris_holu_1 | r_L0_giris_holu | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -2 | search 1.81 | D4 A1 | 0 | no | [preview](cam_r_L0_giris_holu_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_1_plan.jpg) |
| cam_r_L0_giris_holu_2 | r_L0_giris_holu | L0 | cycles | not_run | - | - | info | - | - | +2.67 | -2 | search 1.41 | D2 A1 | 0 | no | [preview](cam_r_L0_giris_holu_2_final_preview.jpg) [plan](cam_r_L0_giris_holu_2_plan.jpg) |
| cam_r_L0_giris_holu_2_1 | r_L0_giris_holu_2 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 1.85 | D3 A1 | 0 | no | [preview](cam_r_L0_giris_holu_2_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_2_1_plan.jpg) |
| cam_r_L0_giris_holu_2_2 | r_L0_giris_holu_2 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | - | search 0.99 | D2 | 0 | no | [preview](cam_r_L0_giris_holu_2_2_final_preview.jpg) [plan](cam_r_L0_giris_holu_2_2_plan.jpg) |
| cam_r_L0_giris_holu_3_1 | r_L0_giris_holu_3 | L0 | cycles | not_run | - | - | info | - | - | +2.67 | -1 | search 0.44 | D3 A1 | 0 | no | [preview](cam_r_L0_giris_holu_3_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_3_1_plan.jpg) |
| cam_r_L0_giris_holu_4_1 | r_L0_giris_holu_4 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | 0 | search 1.92 | D4 A1 | 0 | no | [preview](cam_r_L0_giris_holu_4_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_4_1_plan.jpg) |
| cam_r_L0_giris_holu_4_2 | r_L0_giris_holu_4 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | 0 | search 1.64 | D2 A1 | 0 | no | [preview](cam_r_L0_giris_holu_4_2_final_preview.jpg) [plan](cam_r_L0_giris_holu_4_2_plan.jpg) |
| cam_r_L0_kat_holu_1 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -1 | search 2.16 | D1 | 0 | no | [preview](cam_r_L0_kat_holu_1_final_preview.jpg) [plan](cam_r_L0_kat_holu_1_plan.jpg) |
| cam_r_L0_kat_holu_2 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -1 | search 2.10 | D3 A1 | 0 | no | [preview](cam_r_L0_kat_holu_2_final_preview.jpg) [plan](cam_r_L0_kat_holu_2_plan.jpg) |
| cam_r_L0_kat_holu_3 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -1 | search 2.08 | D3 | 0 | no | [preview](cam_r_L0_kat_holu_3_final_preview.jpg) [plan](cam_r_L0_kat_holu_3_plan.jpg) |
| cam_r_L0_kat_merdiveni_1 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -1 | search 3.98 | D3 | 1 | no | [preview](cam_r_L0_kat_merdiveni_1_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_1_plan.jpg) |
| cam_r_L0_kat_merdiveni_2 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -2 | search 3.70 | D2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_2_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_2_plan.jpg) |
| cam_r_L0_kat_merdiveni_3 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -2 | search 3.29 | D2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_3_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_3_plan.jpg) |
| cam_r_L0_oda_01_1 | r_L0_oda_01 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | - | search 3.24 | D2 A1 | 0 | no | [preview](cam_r_L0_oda_01_1_final_preview.jpg) [plan](cam_r_L0_oda_01_1_plan.jpg) |
| cam_r_L0_oda_01_2 | r_L0_oda_01 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | -1 | search 3.19 | D2 A2 | 0 | no | [preview](cam_r_L0_oda_01_2_final_preview.jpg) [plan](cam_r_L0_oda_01_2_plan.jpg) |
| cam_r_L0_oda_01_3 | r_L0_oda_01 | L0 | cycles | not_run | - | - | info | - | - | +0.83 | -3 | search 3.02 | D3 A2 | 0 | no | [preview](cam_r_L0_oda_01_3_final_preview.jpg) [plan](cam_r_L0_oda_01_3_plan.jpg) |
| cam_r_L0_oda_10_1 | r_L0_oda_10 | L0 | cycles | not_run | - | - | info | - | - | +2.67 | -1 | search 0.22 | - | 0 | no | [preview](cam_r_L0_oda_10_1_final_preview.jpg) [plan](cam_r_L0_oda_10_1_plan.jpg) |
| cam_r_L0_oda_19_1 | r_L0_oda_19 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | 0 | search 2.93 | D4 | 0 | no | [preview](cam_r_L0_oda_19_1_final_preview.jpg) [plan](cam_r_L0_oda_19_1_plan.jpg) |
| cam_r_L0_oda_19_2 | r_L0_oda_19 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | 0 | search 2.93 | D4 | 0 | no | [preview](cam_r_L0_oda_19_2_final_preview.jpg) [plan](cam_r_L0_oda_19_2_plan.jpg) |
| cam_r_L0_oda_19_3 | r_L0_oda_19 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.89 | D3 | 0 | no | [preview](cam_r_L0_oda_19_3_final_preview.jpg) [plan](cam_r_L0_oda_19_3_plan.jpg) |
| cam_r_L0_oda_7_1 | r_L0_oda_7 | L0 | cycles | not_run | - | - | info | - | - | +2.83 | 0 | search 0.21 | D2 | 0 | no | [preview](cam_r_L0_oda_7_1_final_preview.jpg) [plan](cam_r_L0_oda_7_1_plan.jpg) |
| cam_r_L0_ruzgarlik_1 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | +1.50 | -2 | search 3.88 | D4 A1 | 0 | no | [preview](cam_r_L0_ruzgarlik_1_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_1_plan.jpg) |
| cam_r_L0_ruzgarlik_2 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | +1.50 | 0 | search 3.39 | D4 A1 | 0 | no | [preview](cam_r_L0_ruzgarlik_2_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_2_plan.jpg) |
| cam_r_L0_ruzgarlik_3 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 3.23 | D3 A1 | 0 | no | [preview](cam_r_L0_ruzgarlik_3_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_3_plan.jpg) |
| cam_r_L0_yangin_merdiveni_1 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.83 | -1 | search 3.19 | D2 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_1_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_1_plan.jpg) |
| cam_r_L0_yangin_merdiveni_2 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +1.33 | 0 | search 2.20 | D2 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_2_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_2_plan.jpg) |
| cam_r_L0_yangin_merdiveni_3 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 1.78 | D1 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_3_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_3_plan.jpg) |
| cam_r_L0_yasama_1 | r_L0_yasama | L0 | cycles | not_run | - | - | info | - | - | +1.33 | 0 | search 3.45 | D12 A1 | 4 | yes | [preview](cam_r_L0_yasama_1_final_preview.jpg) [plan](cam_r_L0_yasama_1_plan.jpg) |
| cam_r_L0_yasama_2 | r_L0_yasama | L0 | cycles | not_run | - | - | info | - | - | +1.33 | 0 | search 3.37 | D11 A1 | 3 | yes | [preview](cam_r_L0_yasama_2_final_preview.jpg) [plan](cam_r_L0_yasama_2_plan.jpg) |
| cam_r_L0_yasama_2_1 | r_L0_yasama_2 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | -3 | search 3.16 | D13 A4 | 6 | yes | [preview](cam_r_L0_yasama_2_1_final_preview.jpg) [plan](cam_r_L0_yasama_2_1_plan.jpg) |
| cam_r_L0_yasama_2_2 | r_L0_yasama_2 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | -3 | search 3.09 | D13 A4 | 5 | no | [preview](cam_r_L0_yasama_2_2_final_preview.jpg) [plan](cam_r_L0_yasama_2_2_plan.jpg) |
| cam_r_L0_yasama_2_3 | r_L0_yasama_2 | L0 | cycles | not_run | - | - | info | - | - | +0.83 | -1 | search 3.07 | D11 A2 | 5 | no | [preview](cam_r_L0_yasama_2_3_final_preview.jpg) [plan](cam_r_L0_yasama_2_3_plan.jpg) |
| cam_r_L0_yasama_3 | r_L0_yasama | L0 | cycles | not_run | - | - | info | - | - | +1.83 | 0 | search 3.26 | D10 A1 | 2 | yes | [preview](cam_r_L0_yasama_3_final_preview.jpg) [plan](cam_r_L0_yasama_3_plan.jpg) |
| cam_r_L0_yasama_3_1 | r_L0_yasama_3 | L0 | cycles | not_run | - | - | info | - | - | +0.83 | -3 | search 3.25 | D11 A5 | 5 | yes | [preview](cam_r_L0_yasama_3_1_final_preview.jpg) [plan](cam_r_L0_yasama_3_1_plan.jpg) |
| cam_r_L0_yasama_3_2 | r_L0_yasama_3 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | -3 | search 3.24 | D12 A4 | 5 | no | [preview](cam_r_L0_yasama_3_2_final_preview.jpg) [plan](cam_r_L0_yasama_3_2_plan.jpg) |
| cam_r_L0_yasama_3_3 | r_L0_yasama_3 | L0 | cycles | not_run | - | - | info | - | - | +0.33 | -2 | search 3.05 | D13 A4 | 5 | no | [preview](cam_r_L0_yasama_3_3_final_preview.jpg) [plan](cam_r_L0_yasama_3_3_plan.jpg) |
| cam_r_L0_yasama_4_1 | r_L0_yasama_4 | L0 | cycles | not_run | - | - | info | - | - | +2.00 | 0 | search 4.42 | D8 A1 | 4 | yes | [preview](cam_r_L0_yasama_4_1_final_preview.jpg) [plan](cam_r_L0_yasama_4_1_plan.jpg) |
| cam_r_L0_yasama_4_2 | r_L0_yasama_4 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | 0 | search 4.08 | D11 | 4 | no | [preview](cam_r_L0_yasama_4_2_final_preview.jpg) [plan](cam_r_L0_yasama_4_2_plan.jpg) |
| cam_r_L0_yasama_4_3 | r_L0_yasama_4 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | 0 | search 4.04 | D11 | 4 | no | [preview](cam_r_L0_yasama_4_3_final_preview.jpg) [plan](cam_r_L0_yasama_4_3_plan.jpg) |
| cam_r_L0_yasama_5_1 | r_L0_yasama_5 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | 0 | search 3.18 | D11 A3 | 5 | no | [preview](cam_r_L0_yasama_5_1_final_preview.jpg) [plan](cam_r_L0_yasama_5_1_plan.jpg) |
| cam_r_L0_yasama_5_2 | r_L0_yasama_5 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | -3 | search 3.08 | D12 A4 | 4 | no | [preview](cam_r_L0_yasama_5_2_final_preview.jpg) [plan](cam_r_L0_yasama_5_2_plan.jpg) |
| cam_r_L0_yasama_5_3 | r_L0_yasama_5 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | -3 | search 2.83 | D12 A4 | 4 | no | [preview](cam_r_L0_yasama_5_3_final_preview.jpg) [plan](cam_r_L0_yasama_5_3_plan.jpg) |
| cam_r_L0_yasama_6_1 | r_L0_yasama_6 | L0 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 2.99 | D13 A4 | 5 | no | [preview](cam_r_L0_yasama_6_1_final_preview.jpg) [plan](cam_r_L0_yasama_6_1_plan.jpg) |
| cam_r_L0_yasama_6_2 | r_L0_yasama_6 | L0 | cycles | not_run | - | - | info | - | - | +1.50 | 0 | search 2.91 | D13 A4 | 6 | no | [preview](cam_r_L0_yasama_6_2_final_preview.jpg) [plan](cam_r_L0_yasama_6_2_plan.jpg) |
| cam_r_L0_yasama_6_3 | r_L0_yasama_6 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -3 | search 2.85 | D13 A4 | 5 | yes | [preview](cam_r_L0_yasama_6_3_final_preview.jpg) [plan](cam_r_L0_yasama_6_3_plan.jpg) |
| cam_r_L0_yasama_7_1 | r_L0_yasama_7 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.70 | D7 A1 | 4 | no | [preview](cam_r_L0_yasama_7_1_final_preview.jpg) [plan](cam_r_L0_yasama_7_1_plan.jpg) |
| cam_r_L0_yasama_7_2 | r_L0_yasama_7 | L0 | cycles | not_run | - | - | info | - | - | +0.50 | 0 | search 2.59 | D5 A1 | 2 | yes | [preview](cam_r_L0_yasama_7_2_final_preview.jpg) [plan](cam_r_L0_yasama_7_2_plan.jpg) |
| cam_r_L0_yasama_7_3 | r_L0_yasama_7 | L0 | cycles | not_run | - | - | info | - | - | -0.83 | 0 | search 2.50 | D6 | 4 | yes | [preview](cam_r_L0_yasama_7_3_final_preview.jpg) [plan](cam_r_L0_yasama_7_3_plan.jpg) |
| cam_r_L0_yasama_8_1 | r_L0_yasama_8 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | 0 | search 2.72 | D5 A1 | 3 | yes | [preview](cam_r_L0_yasama_8_1_final_preview.jpg) [plan](cam_r_L0_yasama_8_1_plan.jpg) |
| cam_r_L0_yasama_8_2 | r_L0_yasama_8 | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -4 | search 2.63 | D4 A1 | 3 | no | [preview](cam_r_L0_yasama_8_2_final_preview.jpg) [plan](cam_r_L0_yasama_8_2_plan.jpg) |
| cam_r_L0_yasama_8_3 | r_L0_yasama_8 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -1 | search 2.57 | D6 A1 | 3 | no | [preview](cam_r_L0_yasama_8_3_final_preview.jpg) [plan](cam_r_L0_yasama_8_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.83 | 0 | m5 blocked | D13 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.50 | 0 | agent | D12 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.33 | 0 | m5 blocked | D8 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.67 | 0 | m5 blocked | D8 | 0 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.00 | 0 | agent | D12 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.17 | 0 | agent | D12 | 0 | no | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_banyo | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_1 |
| r_L0_banyo_2 | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_2_1 |
| r_L0_banyo_3 | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_3_1 |
| r_L0_banyo_4 | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_banyo_4_1, cam_r_L0_banyo_4_2 |
| r_L0_banyo_5 | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_banyo_5_1, cam_r_L0_banyo_5_2 |
| r_L0_banyo_6 | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_banyo_6_1, cam_r_L0_banyo_6_2 |
| r_L0_banyo_7 | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_7_1 |
| r_L0_banyo_8 | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_8_1 |
| r_L0_ebeveyn_odasi | bedroom | L0 | 2 | 0 | 2 | cam_r_L0_ebeveyn_odasi_1, cam_r_L0_ebeveyn_odasi_2 |
| r_L0_ebeveyn_odasi_2 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_odasi_2_1, cam_r_L0_ebeveyn_odasi_2_2, cam_r_L0_ebeveyn_odasi_2_3 |
| r_L0_ebeveyn_odasi_3 | bedroom | L0 | 2 | 0 | 2 | cam_r_L0_ebeveyn_odasi_3_1, cam_r_L0_ebeveyn_odasi_3_2 |
| r_L0_ebeveyn_odasi_4 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_odasi_4_1, cam_r_L0_ebeveyn_odasi_4_2, cam_r_L0_ebeveyn_odasi_4_3 |
| r_L0_ebeveyn_odasi_5 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_odasi_5_1, cam_r_L0_ebeveyn_odasi_5_2, cam_r_L0_ebeveyn_odasi_5_3 |
| r_L0_ebeveyn_odasi_6 | bedroom | L0 | 2 | 0 | 2 | cam_r_L0_ebeveyn_odasi_6_1, cam_r_L0_ebeveyn_odasi_6_2 |
| r_L0_ebeveyn_odasi_m_k_a | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_odasi_m_k_a_1, cam_r_L0_ebeveyn_odasi_m_k_a_2, cam_r_L0_ebeveyn_odasi_m_k_a_3 |
| r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_odasi_m_k_a_2_1, cam_r_L0_ebeveyn_odasi_m_k_a_2_2, cam_r_L0_ebeveyn_odasi_m_k_a_2_3 |
| r_L0_giris_holu | hall | L0 | 2 | 0 | 2 | cam_r_L0_giris_holu_1, cam_r_L0_giris_holu_2 |
| r_L0_giris_holu_2 | hall | L0 | 2 | 0 | 2 | cam_r_L0_giris_holu_2_1, cam_r_L0_giris_holu_2_2 |
| r_L0_giris_holu_3 | hall | L0 | 1 | 0 | 1 | cam_r_L0_giris_holu_3_1 |
| r_L0_giris_holu_4 | hall | L0 | 2 | 0 | 2 | cam_r_L0_giris_holu_4_1, cam_r_L0_giris_holu_4_2 |
| r_L0_hava_bacasi | shaft | L0 | 0 | 0 | 0 | - |
| r_L0_kat_holu | hall | L0 | 3 | 0 | 3 | cam_r_L0_kat_holu_1, cam_r_L0_kat_holu_2, cam_r_L0_kat_holu_3 |
| r_L0_kat_merdiveni | stair | L0 | 3 | 0 | 3 | cam_r_L0_kat_merdiveni_1, cam_r_L0_kat_merdiveni_2, cam_r_L0_kat_merdiveni_3 |
| r_L0_oda | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_01 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_oda_01_1, cam_r_L0_oda_01_2, cam_r_L0_oda_01_3 |
| r_L0_oda_10 | hall | L0 | 1 | 0 | 1 | cam_r_L0_oda_10_1 |
| r_L0_oda_11 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_12 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_13 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_14 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_15 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_16 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_17 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_18 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_19 | unknown | L0 | 3 | 0 | 3 | cam_r_L0_oda_19_1, cam_r_L0_oda_19_2, cam_r_L0_oda_19_3 |
| r_L0_oda_2 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_20 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_21 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_3 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_4 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_5 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_6 | unknown | L0 | 0 | 0 | 0 | - |
| r_L0_oda_7 | hall | L0 | 1 | 0 | 1 | cam_r_L0_oda_7_1 |
| r_L0_oda_8 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_oda_9 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_ruzgarlik | hall | L0 | 3 | 0 | 3 | cam_r_L0_ruzgarlik_1, cam_r_L0_ruzgarlik_2, cam_r_L0_ruzgarlik_3 |
| r_L0_yangin_merdiveni | stair | L0 | 3 | 0 | 3 | cam_r_L0_yangin_merdiveni_1, cam_r_L0_yangin_merdiveni_2, cam_r_L0_yangin_merdiveni_3 |
| r_L0_yasama | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_1, cam_r_L0_yasama_2, cam_r_L0_yasama_3 |
| r_L0_yasama_2 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_2_1, cam_r_L0_yasama_2_2, cam_r_L0_yasama_2_3 |
| r_L0_yasama_3 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_3_1, cam_r_L0_yasama_3_2, cam_r_L0_yasama_3_3 |
| r_L0_yasama_4 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_4_1, cam_r_L0_yasama_4_2, cam_r_L0_yasama_4_3 |
| r_L0_yasama_5 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_5_1, cam_r_L0_yasama_5_2, cam_r_L0_yasama_5_3 |
| r_L0_yasama_6 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_6_1, cam_r_L0_yasama_6_2, cam_r_L0_yasama_6_3 |
| r_L0_yasama_7 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_7_1, cam_r_L0_yasama_7_2, cam_r_L0_yasama_7_3 |
| r_L0_yasama_8 | living | L0 | 3 | 0 | 3 | cam_r_L0_yasama_8_1, cam_r_L0_yasama_8_2, cam_r_L0_yasama_8_3 |

Rooms without a rendered view: r_L0_hava_bacasi (no furniture after layout and decor and 0.32 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda (no furniture after layout and decor and 0.35 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_11 (no furniture after layout and decor and 0.04 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_12 (no furniture after layout and decor and 0.04 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_13 (no furniture after layout and decor and 0.05 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_14 (no furniture after layout and decor and 0.04 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_15 (no furniture after layout and decor and 0.35 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_16 (no furniture after layout and decor and 0.07 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_17 (no furniture after layout and decor and 0.07 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_18 (no furniture after layout and decor and 0.35 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_2 (no furniture after layout and decor and 0.25 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_20 (no furniture after layout and decor and 0.33 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_21 (no furniture after layout and decor and 0.33 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_3 (no furniture after layout and decor and 0.35 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_4 (no furniture after layout and decor and 0.09 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_5 (no furniture after layout and decor and 0.07 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_6 (no furniture after layout and decor and 0.10 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_8 (no furniture after layout and decor and 1.40 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)), r_L0_oda_9 (no furniture after layout and decor and 1.40 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)).

### Why Cycles

- cam_r_L0_banyo_1: not_run: polish not run
- cam_r_L0_banyo_2_1: not_run: polish not run
- cam_r_L0_banyo_3_1: not_run: polish not run
- cam_r_L0_banyo_4_1: not_run: polish not run
- cam_r_L0_banyo_4_2: not_run: polish not run
- cam_r_L0_banyo_5_1: not_run: polish not run
- cam_r_L0_banyo_5_2: not_run: polish not run
- cam_r_L0_banyo_6_1: not_run: polish not run
- cam_r_L0_banyo_6_2: not_run: polish not run
- cam_r_L0_banyo_7_1: not_run: polish not run
- cam_r_L0_banyo_8_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_2_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_2_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_2_3: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_3_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_3_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_4_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_4_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_4_3: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_5_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_5_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_5_3: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_6_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_6_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_m_k_a_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_m_k_a_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_m_k_a_2_1: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_m_k_a_2_2: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_m_k_a_2_3: not_run: polish not run
- cam_r_L0_ebeveyn_odasi_m_k_a_3: not_run: polish not run
- cam_r_L0_giris_holu_1: not_run: polish not run
- cam_r_L0_giris_holu_2: not_run: polish not run
- cam_r_L0_giris_holu_2_1: not_run: polish not run
- cam_r_L0_giris_holu_2_2: not_run: polish not run
- cam_r_L0_giris_holu_3_1: not_run: polish not run
- cam_r_L0_giris_holu_4_1: not_run: polish not run
- cam_r_L0_giris_holu_4_2: not_run: polish not run
- cam_r_L0_kat_holu_1: not_run: polish not run
- cam_r_L0_kat_holu_2: not_run: polish not run
- cam_r_L0_kat_holu_3: not_run: polish not run
- cam_r_L0_kat_merdiveni_1: not_run: polish not run
- cam_r_L0_kat_merdiveni_2: not_run: polish not run
- cam_r_L0_kat_merdiveni_3: not_run: polish not run
- cam_r_L0_oda_01_1: not_run: polish not run
- cam_r_L0_oda_01_2: not_run: polish not run
- cam_r_L0_oda_01_3: not_run: polish not run
- cam_r_L0_oda_10_1: not_run: polish not run
- cam_r_L0_oda_19_1: not_run: polish not run
- cam_r_L0_oda_19_2: not_run: polish not run
- cam_r_L0_oda_19_3: not_run: polish not run
- cam_r_L0_oda_7_1: not_run: polish not run
- cam_r_L0_ruzgarlik_1: not_run: polish not run
- cam_r_L0_ruzgarlik_2: not_run: polish not run
- cam_r_L0_ruzgarlik_3: not_run: polish not run
- cam_r_L0_yangin_merdiveni_1: not_run: polish not run
- cam_r_L0_yangin_merdiveni_2: not_run: polish not run
- cam_r_L0_yangin_merdiveni_3: not_run: polish not run
- cam_r_L0_yasama_1: not_run: polish not run
- cam_r_L0_yasama_2: not_run: polish not run
- cam_r_L0_yasama_2_1: not_run: polish not run
- cam_r_L0_yasama_2_2: not_run: polish not run
- cam_r_L0_yasama_2_3: not_run: polish not run
- cam_r_L0_yasama_3: not_run: polish not run
- cam_r_L0_yasama_3_1: not_run: polish not run
- cam_r_L0_yasama_3_2: not_run: polish not run
- cam_r_L0_yasama_3_3: not_run: polish not run
- cam_r_L0_yasama_4_1: not_run: polish not run
- cam_r_L0_yasama_4_2: not_run: polish not run
- cam_r_L0_yasama_4_3: not_run: polish not run
- cam_r_L0_yasama_5_1: not_run: polish not run
- cam_r_L0_yasama_5_2: not_run: polish not run
- cam_r_L0_yasama_5_3: not_run: polish not run
- cam_r_L0_yasama_6_1: not_run: polish not run
- cam_r_L0_yasama_6_2: not_run: polish not run
- cam_r_L0_yasama_6_3: not_run: polish not run
- cam_r_L0_yasama_7_1: not_run: polish not run
- cam_r_L0_yasama_7_2: not_run: polish not run
- cam_r_L0_yasama_7_3: not_run: polish not run
- cam_r_L0_yasama_8_1: not_run: polish not run
- cam_r_L0_yasama_8_2: not_run: polish not run
- cam_r_L0_yasama_8_3: not_run: polish not run
- ext_1: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_2: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_3: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_4: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_6: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_7: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_ebeveyn_odasi_2 | cycles | cross-check misplaced | f_L0_071 | bed_double | - | from_documents | tekkat.dwg INSERT:7C9C9/3/47/0,INSERT:7C9C9/3/47/1,INSERT:7C9C9/3/47/2,INSERT:7C9C9/3/47/3,INSERT:7C9C9/3/47/4,INSERT:7C9C9/3/47/5,INSERT:7C9C9/3/47/6 D BLOK_ZK/xref_1+1_B_PLAN/xref_1+1_B_PLAN$0$yatak 160x200 vector 0.90 | yes | 31 % of its pixels > 0.10 m outside the drawing, 132806 px |
| cam_r_L0_ebeveyn_odasi_3_1 | cycles | cross-check misplaced | f_L0_072 | bed_double | - | from_documents | tekkat.dwg INSERT:7C9C9/5/47/0,INSERT:7C9C9/5/47/1,INSERT:7C9C9/5/47/2,INSERT:7C9C9/5/47/3,INSERT:7C9C9/5/47/4,INSERT:7C9C9/5/47/5,INSERT:7C9C9/5/47/6 D BLOK_ZK/xref_1+1_B_PLAN/xref_1+1_B_PLAN$0$yatak 160x200 vector 0.90 | yes | 10 % of its pixels > 0.10 m outside the drawing, 798837 px |
| cam_r_L0_yasama_1 | cycles | cross-check in_json_not_rendered | f_L0_005 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/10/147/8/0,INSERT:7C9C9/10/147/8/1,INSERT:7C9C9/10/147/8/2,INSERT:7C9C9/10/147/8/3,INSERT:7C9C9/10/147/8/4,INSERT:7C9C9/10/147/8/5,INSERT:7C9C9/10/147/8/6,INSERT:7C9C9/10/147/8/7,INSERT:7C9C9/10/147/8/8 vector 0.85 | yes | visible 0.42, area 0.026 |
| cam_r_L0_yasama_2 | cycles | cross-check in_json_not_rendered | f_L0_005 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/10/147/8/0,INSERT:7C9C9/10/147/8/1,INSERT:7C9C9/10/147/8/2,INSERT:7C9C9/10/147/8/3,INSERT:7C9C9/10/147/8/4,INSERT:7C9C9/10/147/8/5,INSERT:7C9C9/10/147/8/6,INSERT:7C9C9/10/147/8/7,INSERT:7C9C9/10/147/8/8 vector 0.85 | yes | visible 0.47, area 0.026 |
| cam_r_L0_yasama_2_1 | cycles | cross-check in_json_not_rendered | f_L0_030 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/5/20/0,INSERT:7C9C9/5/20/1,INSERT:7C9C9/5/20/2,INSERT:7C9C9/5/20/3,INSERT:7C9C9/5/20/4,INSERT:7C9C9/5/20/5,INSERT:7C9C9/5/20/6,INSERT:7C9C9/5/20/7,INSERT:7C9C9/5/20/8 vector 0.85 | yes | visible 0.76, area 0.039 |
| cam_r_L0_yasama_3 | cycles | cross-check in_json_not_rendered | f_L0_005 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/10/147/8/0,INSERT:7C9C9/10/147/8/1,INSERT:7C9C9/10/147/8/2,INSERT:7C9C9/10/147/8/3,INSERT:7C9C9/10/147/8/4,INSERT:7C9C9/10/147/8/5,INSERT:7C9C9/10/147/8/6,INSERT:7C9C9/10/147/8/7,INSERT:7C9C9/10/147/8/8 vector 0.85 | yes | visible 0.41, area 0.041 |
| cam_r_L0_yasama_3_1 | cycles | cross-check in_json_not_rendered | f_L0_024 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/3/20/0,INSERT:7C9C9/3/20/1,INSERT:7C9C9/3/20/2,INSERT:7C9C9/3/20/3,INSERT:7C9C9/3/20/4,INSERT:7C9C9/3/20/5,INSERT:7C9C9/3/20/6,INSERT:7C9C9/3/20/7,INSERT:7C9C9/3/20/8 vector 0.85 | yes | visible 0.76, area 0.039 |
| cam_r_L0_yasama_4_1 | cycles | cross-check in_json_not_rendered | f_L0_014 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/18/54/0,INSERT:7C9C9/18/54/1,INSERT:7C9C9/18/54/2,INSERT:7C9C9/18/54/3,INSERT:7C9C9/18/54/4,INSERT:7C9C9/18/54/5,INSERT:7C9C9/18/54/6,INSERT:7C9C9/18/54/7,INSERT:7C9C9/18/54/8 vector 0.85 | yes | visible 0.48, area 0.045 |
| cam_r_L0_yasama_6_3 | cycles | cross-check in_json_not_rendered | f_L0_027 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/4/20/0,INSERT:7C9C9/4/20/1,INSERT:7C9C9/4/20/2,INSERT:7C9C9/4/20/3,INSERT:7C9C9/4/20/4,INSERT:7C9C9/4/20/5,INSERT:7C9C9/4/20/6,INSERT:7C9C9/4/20/7,INSERT:7C9C9/4/20/8 vector 0.85 | yes | visible 0.77, area 0.035 |
| cam_r_L0_yasama_7_2 | cycles | cross-check in_json_not_rendered | f_L0_086 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/8/52/0,INSERT:7C9C9/8/52/1,INSERT:7C9C9/8/52/2,INSERT:7C9C9/8/52/3,INSERT:7C9C9/8/52/4,INSERT:7C9C9/8/52/5,INSERT:7C9C9/8/52/6,INSERT:7C9C9/8/52/7,INSERT:7C9C9/8/52/8 vector 0.85 | yes | visible 0.43, area 0.095 |
| cam_r_L0_yasama_7_3 | cycles | cross-check in_json_not_rendered | f_L0_086 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/8/52/0,INSERT:7C9C9/8/52/1,INSERT:7C9C9/8/52/2,INSERT:7C9C9/8/52/3,INSERT:7C9C9/8/52/4,INSERT:7C9C9/8/52/5,INSERT:7C9C9/8/52/6,INSERT:7C9C9/8/52/7,INSERT:7C9C9/8/52/8 vector 0.85 | yes | visible 0.43, area 0.042 |
| cam_r_L0_yasama_8_1 | cycles | cross-check in_json_not_rendered | f_L0_088 | sink_kitchen | - | from_documents | tekkat.dwg INSERT:7C9C9/7/52/0,INSERT:7C9C9/7/52/1,INSERT:7C9C9/7/52/2,INSERT:7C9C9/7/52/3,INSERT:7C9C9/7/52/4,INSERT:7C9C9/7/52/5,INSERT:7C9C9/7/52/6,INSERT:7C9C9/7/52/7,INSERT:7C9C9/7/52/8 vector 0.85 | yes | visible 0.78, area 0.099 |

## Needs review

- cam_r_L0_ebeveyn_odasi_2: json cross-check misplaced: f_L0_071
- cam_r_L0_ebeveyn_odasi_3_1: json cross-check misplaced: f_L0_072
- cam_r_L0_yasama_1: json cross-check in_json_not_rendered: f_L0_005
- cam_r_L0_yasama_2: json cross-check in_json_not_rendered: f_L0_005
- cam_r_L0_yasama_2_1: json cross-check in_json_not_rendered: f_L0_030
- cam_r_L0_yasama_3: json cross-check in_json_not_rendered: f_L0_005
- cam_r_L0_yasama_3_1: json cross-check in_json_not_rendered: f_L0_024
- cam_r_L0_yasama_4_1: json cross-check in_json_not_rendered: f_L0_014
- cam_r_L0_yasama_6_3: json cross-check in_json_not_rendered: f_L0_027
- cam_r_L0_yasama_7_2: json cross-check in_json_not_rendered: f_L0_086
- cam_r_L0_yasama_7_3: json cross-check in_json_not_rendered: f_L0_086
- cam_r_L0_yasama_8_1: json cross-check in_json_not_rendered: f_L0_088

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- o_L0_001
- o_L0_002
- o_L0_003
- o_L0_004
- o_L0_005
- o_L0_006
- o_L0_007
- o_L0_008
- o_L0_009
- o_L0_010
- o_L0_011
- o_L0_012
- o_L0_013
- o_L0_014
- o_L0_015
- o_L0_016
- o_L0_017
- o_L0_018
- o_L0_019
- o_L0_020
- o_L0_021
- o_L0_022
- d_L0_024
- r_L0_yasama
- r_L0_ruzgarlik
- r_L0_ebeveyn_odasi_4
- r_L0_yasama_4
- r_L0_giris_holu
- r_L0_giris_holu_2
- r_L0_oda
- r_L0_oda_2
- r_L0_oda_3
- r_L0_oda_4
- r_L0_oda_5
- r_L0_oda_6
- r_L0_oda_7
- r_L0_oda_8
- r_L0_kat_holu
- r_L0_oda_9
- r_L0_oda_10
- r_L0_oda_11
- r_L0_oda_12
- r_L0_oda_13
- r_L0_oda_14
- r_L0_oda_15
- r_L0_yangin_merdiveni
- r_L0_oda_16
- r_L0_oda_17
- r_L0_kat_merdiveni
- r_L0_oda_18
- r_L0_giris_holu_3
- r_L0_oda_19
- r_L0_oda_20
- r_L0_oda_21
- r_L0_giris_holu_4
- f_L0_001
- f_L0_002
- f_L0_003
- f_L0_004
- f_L0_010
- f_L0_011
- f_L0_012
- f_L0_013
- f_L0_019
- f_L0_020
- f_L0_022
- f_L0_023
- f_L0_025
- f_L0_026
- f_L0_028
- f_L0_029
- f_L0_031
- f_L0_032
- f_L0_033
- f_L0_034
- f_L0_035
- f_L0_036
- f_L0_037
- f_L0_038
- f_L0_039
- f_L0_040
- f_L0_041
- f_L0_042
- f_L0_043
- f_L0_044
- f_L0_045
- f_L0_046
- f_L0_047
- f_L0_048
- f_L0_085
- f_L0_087
- f_L0_089
- f_L0_090
- f_L0_098
- f_L0_099
- f_L0_100
- f_L0_103
- f_L0_104
- f_L0_108
- f_L0_114
- f_L0_120
- f_L0_125
- f_L0_128
- f_L0_129
- f_L0_130
- f_L0_131
- f_L0_132
- f_L0_133
- f_L0_134
- f_L0_135
- f_L0_136
- f_L0_138
- f_L0_139
- f_L0_143
- f_L0_144
- f_L0_145
- f_L0_147
- f_L0_148
- f_L0_149
- f_L0_150
- f_L0_151
- f_L0_152
- f_L0_153
- f_L0_154
- f_L0_155
- f_L0_156
- f_L0_162
- f_L0_163
- f_L0_181
- f_L0_182
- f_L0_183
- f_L0_184
- f_L0_188
- f_L0_189
- f_L0_190
- f_L0_191
- f_L0_192
- f_L0_193
- f_L0_194
- f_L0_195
- f_L0_196
- f_L0_197
- f_L0_198
- f_L0_199
- f_L0_200
- f_L0_202
- f_L0_203
- f_L0_204
- f_L0_205
- f_L0_206
- f_L0_207
- f_L0_208
- f_L0_209
- f_L0_210
- f_L0_211
- f_L0_212
- f_L0_213

Unverified pieces in view:

- cam_r_L0_banyo_4_1: f_L0_145
- cam_r_L0_banyo_4_2: f_L0_145
- cam_r_L0_banyo_5_1: f_L0_184
- cam_r_L0_banyo_5_2: f_L0_184
- cam_r_L0_ebeveyn_odasi_2_1: f_L0_099
- cam_r_L0_ebeveyn_odasi_2_2: f_L0_099
- cam_r_L0_ebeveyn_odasi_2_3: f_L0_099, f_L0_100
- cam_r_L0_ebeveyn_odasi_4_1: f_L0_136
- cam_r_L0_ebeveyn_odasi_4_2: f_L0_136
- cam_r_L0_ebeveyn_odasi_4_3: f_L0_136
- cam_r_L0_ebeveyn_odasi_m_k_a_1: f_L0_132, f_L0_133, f_L0_143
- cam_r_L0_ebeveyn_odasi_m_k_a_2: f_L0_132, f_L0_133
- cam_r_L0_ebeveyn_odasi_m_k_a_2_1: f_L0_134, f_L0_135, f_L0_144
- cam_r_L0_ebeveyn_odasi_m_k_a_2_2: f_L0_135
- cam_r_L0_ebeveyn_odasi_m_k_a_2_3: f_L0_144
- cam_r_L0_ebeveyn_odasi_m_k_a_3: f_L0_133, f_L0_143
- cam_r_L0_kat_merdiveni_1: f_L0_031
- cam_r_L0_kat_merdiveni_2: f_L0_031
- cam_r_L0_kat_merdiveni_3: f_L0_031
- cam_r_L0_yangin_merdiveni_1: f_L0_032
- cam_r_L0_yangin_merdiveni_2: f_L0_032
- cam_r_L0_yangin_merdiveni_3: f_L0_032
- cam_r_L0_yasama_1: f_L0_001, f_L0_002, f_L0_190, f_L0_191
- cam_r_L0_yasama_2: f_L0_001, f_L0_002, f_L0_190
- cam_r_L0_yasama_2_1: f_L0_028, f_L0_029, f_L0_152, f_L0_206, f_L0_207, f_L0_211
- cam_r_L0_yasama_2_2: f_L0_029, f_L0_125, f_L0_152, f_L0_207, f_L0_211
- cam_r_L0_yasama_2_3: f_L0_125, f_L0_152, f_L0_206, f_L0_207, f_L0_211
- cam_r_L0_yasama_3: f_L0_001, f_L0_002
- cam_r_L0_yasama_3_1: f_L0_022, f_L0_023, f_L0_202, f_L0_203, f_L0_209
- cam_r_L0_yasama_3_2: f_L0_023, f_L0_114, f_L0_156, f_L0_203, f_L0_209
- cam_r_L0_yasama_3_3: f_L0_023, f_L0_114, f_L0_156, f_L0_203, f_L0_209
- cam_r_L0_yasama_4_1: d_L0_024, f_L0_010, f_L0_011, f_L0_194
- cam_r_L0_yasama_4_2: f_L0_010, f_L0_196, f_L0_197, f_L0_198
- cam_r_L0_yasama_4_3: f_L0_010, f_L0_196, f_L0_197, f_L0_198
- cam_r_L0_yasama_5_1: f_L0_019, f_L0_108, f_L0_153, f_L0_200, f_L0_208
- cam_r_L0_yasama_5_2: f_L0_020, f_L0_108, f_L0_153, f_L0_208
- cam_r_L0_yasama_5_3: f_L0_020, f_L0_108, f_L0_153, f_L0_208
- cam_r_L0_yasama_6_1: f_L0_026, f_L0_120, f_L0_151, f_L0_205, f_L0_210
- cam_r_L0_yasama_6_2: f_L0_025, f_L0_026, f_L0_120, f_L0_204, f_L0_205, f_L0_210
- cam_r_L0_yasama_6_3: f_L0_025, f_L0_026, f_L0_204, f_L0_205, f_L0_210
- cam_r_L0_yasama_7_1: f_L0_085, f_L0_139, f_L0_155, f_L0_162
- cam_r_L0_yasama_7_2: f_L0_085, f_L0_212
- cam_r_L0_yasama_7_3: f_L0_085, f_L0_139, f_L0_155, f_L0_212
- cam_r_L0_yasama_8_1: f_L0_087, f_L0_138, f_L0_154
- cam_r_L0_yasama_8_2: f_L0_138, f_L0_154, f_L0_163
- cam_r_L0_yasama_8_3: f_L0_087, f_L0_138, f_L0_154

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L0_103 | untyped_piece | r_L0_oda_01 | drawn piece 1.50 x 0.60 m in r_L0_oda_01 has no type (AI passes: dresser, wardrobe): not built | recognition/crops/sym_L0_019_ctx.png |
| f_L0_104 | untyped_piece | r_L0_oda_01 | drawn piece 0.40 x 0.20 m in r_L0_oda_01 has no type (AI passes: floor_lamp, unknown): not built | recognition/crops/sym_L0_020_ctx.png |

Drawn symbols read as not furniture (never built): dimension_outline 5, door_arc 20, level_mark 1, other 36, room_number 8, text_frame 8.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L0_049 | furniture | stove | objaverse_68e164f1a9414c29820ac2eaf6d8ac04 | vision quality 2 (<= 2) |
| f_L0_050 | furniture | stove | objaverse_68e164f1a9414c29820ac2eaf6d8ac04 | vision quality 2 (<= 2) |
| f_L0_057 | furniture | washing_machine | hssd_856317b238f6a70ae6f0afffed1f6d5e3ab7b80c | vision quality 2 (<= 2) |
| f_L0_069 | furniture | bed_double | abo_B084ZBDPG5 | vision quality 2 (<= 2) |
| f_L0_076 | furniture | washing_machine | hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 | vision quality 2 (<= 2) |
| f_L0_185 | furniture | bathtub | hssd_94f82d1154b9db0d56038b183832b0dfceff8819 | vision quality 2 (<= 2) |
| f_L0_188 | furniture | washbasin | infinigen_bathroom_sink_0 | vision quality 2 (<= 2) |
| f_L0_195 | furniture | washbasin | infinigen_bathroom_sink_0 | vision quality 2 (<= 2) |

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L0_ebeveyn_odasi | Label says 11,27 m², polygon gives 10,61 m² (5.9%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_002 | area_label_vs_computed | r_L0_ebeveyn_odasi_2 | Label says 10,17 m², polygon gives 10,12 m² (0.5%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_003 | area_label_vs_computed | r_L0_yasama | Label says 16,72 m², polygon gives 19,11 m² (14.3%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_004 | area_label_vs_computed | r_L0_ebeveyn_odasi_3 | Label says 11,27 m², polygon gives 10,59 m² (6.0%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_005 | area_label_vs_computed | r_L0_ruzgarlik | Label says 9,64 m², polygon gives 15,97 m² (65.7%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_006 | area_label_vs_computed | r_L0_ebeveyn_odasi_4 | Label says 14,53 m², polygon gives 13,21 m² (9.1%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_007 | area_label_vs_computed | r_L0_yasama_2 | Label says 15,64 m², polygon gives 15,56 m² (0.5%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_008 | area_label_vs_computed | r_L0_oda_01 | Label says 9,06 m², polygon gives 8,38 m² (7.5%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_009 | area_label_vs_computed | r_L0_yasama_3 | Label says 15,64 m², polygon gives 15,62 m² (0.1%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_010 | area_label_vs_computed | r_L0_yasama_4 | Label says 16,68 m², polygon gives 22,05 m² (32.2%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_011 | area_label_vs_computed | r_L0_giris_holu | Label says 3,59 m², polygon gives 3,27 m² (8.9%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_012 | area_label_vs_computed | r_L0_giris_holu_2 | Label says 3,59 m², polygon gives 3,28 m² (8.7%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_013 | area_label_vs_computed | r_L0_kat_holu | Label says 46,94 m², polygon gives 30,05 m² (36.0%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_014 | area_label_vs_computed | r_L0_yasama_6 | Label says 15,64 m², polygon gives 15,59 m² (0.4%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_015 | area_label_vs_computed | r_L0_yangin_merdiveni | Label says 14,17 m², polygon gives 17,46 m² (23.2%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_016 | area_label_vs_computed | r_L0_kat_merdiveni | Label says 14,17 m², polygon gives 17,78 m² (25.5%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_017 | area_label_vs_computed | r_L0_giris_holu_3 | Label says 3,59 m², polygon gives 3,28 m² (8.6%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_018 | area_label_vs_computed | r_L0_giris_holu_4 | Label says 3,59 m², polygon gives 3,28 m² (8.7%) | over 8%: room marked unverified, polygon from tekkat.dwg kept |
| c_019 | area_label_vs_computed | r_L0_ebeveyn_odasi_5 | Label says 11,32 m², polygon gives 10,96 m² (3.2%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_020 | area_label_vs_computed | r_L0_ebeveyn_odasi_6 | Label says 11,32 m², polygon gives 10,96 m² (3.2%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_021 | area_label_vs_computed | r_L0_yasama_7 | Label says 18,33 m², polygon gives 18,00 m² (1.8%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_022 | area_label_vs_computed | r_L0_ebeveyn_odasi_m_k_a | Label says 10,22 m², polygon gives 10,14 m² (0.7%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_023 | area_label_vs_computed | r_L0_ebeveyn_odasi_m_k_a_2 | Label says 10,22 m², polygon gives 10,15 m² (0.7%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_024 | area_label_vs_computed | r_L0_yasama_8 | Label says 18,33 m², polygon gives 18,07 m² (1.4%) | within tolerance (8%), kept polygon from tekkat.dwg |
| c_025 | type_disagreement | sy_L0_004 | f_L0_091: the AI passes typed it armchair, the drawing shows a door_arc (1 quarter arc(s) of 0.74 m with its leaf from the hinge: a door swing) | moved to building.symbols (trust order: vector geometry > AI) |
| c_026 | type_disagreement | sy_L0_005 | f_L0_092: the AI passes typed it floor_lamp, the drawing shows a room_number (circle 0.50 m across with the number '5' inside: a room-number tag) | moved to building.symbols (trust order: vector geometry > AI) |
| c_027 | type_disagreement | sy_L0_009 | f_L0_096: the AI passes typed it side_table, the drawing shows a other (drawn on the 'MYD - GOR-ARKA' layer(s): other, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_028 | type_disagreement | sy_L0_011 | f_L0_101: the AI passes typed it console_table, the drawing shows a door_arc (drawn on the 'MYD - KAPI' layer(s): door, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_029 | type_disagreement | sy_L0_019 | f_L0_127: the AI passes typed it floor_lamp, the drawing shows a room_number (circle 0.50 m across with the number '7' inside: a room-number tag) | moved to building.symbols (trust order: vector geometry > AI) |
| c_030 | type_disagreement | sy_L0_022 | f_L0_142: the AI passes typed it stair, the drawing shows a other (drawn on the 'MYD - IZ-1' layer(s): other, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_031 | type_disagreement | sy_L0_029 | f_L0_165: the AI passes typed it floor_lamp, the drawing shows a room_number (circle 0.50 m across with the number '6' inside: a room-number tag) | moved to building.symbols (trust order: vector geometry > AI) |
| c_032 | type_disagreement | sy_L0_030 | f_L0_166: the AI passes typed it floor_lamp, the drawing shows a door_arc (drawn on the 'MYD - KAPI' layer(s): door, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_033 | type_disagreement | sy_L0_032 | f_L0_168: the AI passes typed it console_table, the drawing shows a door_arc (drawn on the 'MYD - KAPI' layer(s): door, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_034 | type_disagreement | sy_L0_033 | f_L0_169: the AI passes typed it console_table, the drawing shows a door_arc (drawn on the 'MYD - KAPI' layer(s): door, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_035 | type_disagreement | sy_L0_034 | f_L0_170: the AI passes typed it console_table, the drawing shows a door_arc (drawn on the 'MYD - KAPI' layer(s): door, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_036 | type_disagreement | f_L0_111 | f_L0_111: the AI passes typed it sofa; a table with chairs drawn around it (vector geometry outranks the AI passes) | typed table_dining (trust order: vector geometry and block names > AI) |
| c_037 | type_disagreement | f_L0_122 | f_L0_122: the AI passes typed it sofa; a table with chairs drawn around it (vector geometry outranks the AI passes) | typed table_dining (trust order: vector geometry and block names > AI) |
| c_038 | symbol_type_disagreement | f_L0_083 | f_L0_083: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bed_double | unresolved: the drawn footprint is kept as unknown, unverified |
| c_039 | symbol_type_disagreement | f_L0_084 | f_L0_084: sym_L0_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bed_double | unresolved: the drawn footprint is kept as unknown, unverified |
| c_040 | symbol_type_disagreement | f_L0_093 | f_L0_093: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) ottoman | unresolved: the drawn footprint is kept as unknown, unverified |
| c_041 | symbol_type_disagreement | f_L0_094 | f_L0_094: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_042 | symbol_type_disagreement | f_L0_095 | f_L0_095: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_043 | symbol_type_disagreement | f_L0_097 | f_L0_097: sym_L0_013: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) side_table, pass 2 (zai-org/GLM-4.6V-Flash) wall_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_044 | symbol_type_disagreement | f_L0_102 | f_L0_102: sym_L0_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_045 | symbol_type_disagreement | f_L0_103 | f_L0_103: sym_L0_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) dresser, pass 2 (zai-org/GLM-4.6V-Flash) wardrobe | unresolved: the drawn footprint is kept as unknown, unverified |
| c_046 | symbol_type_disagreement | f_L0_104 | f_L0_104: sym_L0_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_047 | symbol_type_disagreement | f_L0_109 | f_L0_109: sym_L0_023: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_048 | symbol_type_disagreement | f_L0_110 | f_L0_110: sym_L0_024: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_049 | symbol_type_disagreement | f_L0_115 | f_L0_115: sym_L0_027: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L0_116 | f_L0_116: sym_L0_028: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) ottoman | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L0_121 | f_L0_121: sym_L0_031: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L0_126 | f_L0_126: sym_L0_034: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_053 | symbol_type_disagreement | f_L0_137 | f_L0_137: sym_L0_045: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) toilet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_054 | symbol_type_disagreement | f_L0_140 | f_L0_140: sym_L0_048: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sofa, pass 2 (zai-org/GLM-4.6V-Flash) table_dining | unresolved: the drawn footprint is kept as unknown, unverified |
| c_055 | symbol_type_disagreement | f_L0_146 | f_L0_146: sym_L0_054: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_056 | symbol_type_disagreement | f_L0_157 | f_L0_157: sym_L0_065: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) shoe_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_057 | symbol_type_disagreement | f_L0_158 | f_L0_158: sym_L0_066: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) shoe_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_058 | symbol_type_disagreement | f_L0_159 | f_L0_159: sym_L0_067: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) shoe_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L0_160 | f_L0_160: sym_L0_068: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) shoe_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L0_161 | f_L0_161: sym_L0_069: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L0_162 | f_L0_162: sym_L0_070: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bookshelf | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L0_163 | f_L0_163: sym_L0_071: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bookshelf | unresolved: the drawn footprint is kept as unknown, unverified |
| c_063 | symbol_type_disagreement | f_L0_164 | f_L0_164: sym_L0_072: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) console_table | unresolved: the drawn footprint is kept as unknown, unverified |
| c_064 | symbol_type_disagreement | f_L0_167 | f_L0_167: sym_L0_075: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) toilet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_065 | symbol_type_disagreement | f_L0_171 | f_L0_171: sym_L0_079: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_066 | symbol_type_disagreement | f_L0_172 | f_L0_172: sym_L0_080: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_067 | symbol_type_disagreement | f_L0_173 | f_L0_173: sym_L0_081: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L0_174 | f_L0_174: sym_L0_082: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_069 | symbol_type_disagreement | f_L0_175 | f_L0_175: sym_L0_083: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_070 | symbol_type_disagreement | f_L0_176 | f_L0_176: sym_L0_084: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_071 | symbol_type_disagreement | f_L0_177 | f_L0_177: sym_L0_085: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_072 | symbol_type_disagreement | f_L0_178 | f_L0_178: sym_L0_086: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_073 | symbol_type_disagreement | f_L0_183 | f_L0_183: sym_L0_091: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) nightstand, pass 2 (zai-org/GLM-4.6V-Flash) wardrobe | unresolved: the drawn footprint is kept as unknown, unverified |
| c_074 | symbol_type_disagreement | f_L0_184 | f_L0_184: sym_L0_092: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) shower, pass 2 (zai-org/GLM-4.6V-Flash) bathtub | unresolved: the drawn footprint is kept as unknown, unverified |
| c_075 | symbol_type_disagreement | f_L0_203 | f_L0_203: sym_L0_x86019e75: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_076 | symbol_type_disagreement | f_L0_205 | f_L0_205: sym_L0_xa48d1258: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_077 | symbol_type_disagreement | f_L0_207 | f_L0_207: sym_L0_x57171dd6: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_078 | other | r_L0_yasama | r_L0_yasama: one face holds the room names 'Yaşama' and 'GİRİŞ HOLÜ' | unresolved: first label kept, room unverified |
| c_079 | other | r_L0_yasama_4 | r_L0_yasama_4: one face holds the room names 'Yaşama' and 'GİRİŞ HOLÜ', 'HOL' | unresolved: first label kept, room unverified |
| c_080 | other | r_L0_giris_holu | r_L0_giris_holu: one face holds the room names 'Giriş Holü' and 'İŞLİK' | unresolved: first label kept, room unverified |
| c_081 | other | r_L0_giris_holu_2 | r_L0_giris_holu_2: one face holds the room names 'Giriş Holü' and 'İŞLİK' | unresolved: first label kept, room unverified |
| c_082 | other | r_L0_yangin_merdiveni | r_L0_yangin_merdiveni: one face holds the room names 'Yangın Merdiveni' and 'GÜVENLİK HOLÜ' | unresolved: first label kept, room unverified |
| c_083 | other | r_L0_giris_holu_3 | r_L0_giris_holu_3: one face holds the room names 'Giriş Holü' and 'İŞLİK' | unresolved: first label kept, room unverified |
| c_084 | other | r_L0_giris_holu_4 | r_L0_giris_holu_4: one face holds the room names 'Giriş Holü' and 'İŞLİK' | unresolved: first label kept, room unverified |
| c_085 | symbol_front_disagreement | f_L0_140 | f_L0_140: sym_L0_048: AI front [0.0, 90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L0_158 | f_L0_158: sym_L0_066: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L0_162 | f_L0_162: sym_L0_070: AI front [270.0] (pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L0_163 | f_L0_163: sym_L0_071: AI front [90.0] (pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L0_166 | f_L0_166: sym_L0_074: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 270 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L0_167 | f_L0_167: sym_L0_075: AI front [90.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | symbol_front_disagreement | f_L0_169 | f_L0_169: sym_L0_077: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 1 regions (use: read 1). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | tekkat.dwg | floor_plan | title (0.99) | verified | L0 | base | read |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L0 | Zemin Kat | floor | r1 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L0 | r1 |

Strays (entities far from every drawing, ignored): 0.

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| tekkat.dwg | dwg | 0.01 | dxf_insunits | area_labels cm 0.86 (50); level_marks None - (0); door_widths cm 1.00 (40); wall_thickness None 0.57 (1045); text_height None - (302); dimensions None - (0) | - |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/tekkat_dwg_s1.jpg](debug/tekkat_dwg_s1.jpg)

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L0 | Ground floor | - | 0,00 m (level_mark) | 2,70 m (assumed_default) | - | - |

Heights (drawn = read from a document; assumed = a default, listed again under Assumed values):

| item | value | state | from | note |
|---|---|---|---|---|
| L0 ceiling height | 2,70 m | assumed | assumed_default | - |
| L0 floor level | 0,00 m | drawn | level_mark | - |
| sl_L0 thickness | 0,20 m | assumed | assumed_default | - |
| roof overhang | 0,00 m | assumed | assumed | flat_cut: the roof ends at the outer wall face |
| roof thickness | 0,30 m | assumed | assumed | flat_cut: a flat roof slab (assumed) |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L0 | L0 | 0,00 m | 0,20 m | assumed_default | 0 | all | assumed |

Roof:

- type flat (assumed)
- over level L0
- overhang 0,00 m (assumed)
- thickness 0,30 m (assumed)
- 0 planes, 0 opening(s)
- covering not drawn (outside look: see Exterior views)

Assumed for the roof: upper floors not drawn: a flat roof slab with a 0.30 m parapet over L0 (flat_cut, inferred).

Facade:

No facade face or elevation drawn: the outside look is resolved from the brief, the style or the defaults (see Exterior views).

Site:

- plot not drawn
- 0 paving area(s), 0 grass, 0 parking built
- 0 boundary wall(s), 66 decor item(s) built
- 8 labelled area(s), 8 recorded only (label, not built)
- ground levels: all -0,15 m (assumed)
- terrain flat, 0 light well(s)

Levels and ground (Milestone 12):

- 2 level mark(s) read (floor 2); 1 mark symbol(s) taken out of the furniture
- datum ±0.00 = 93.20 m (drawn)
- ground from: D3a; terrain flat
- plinth top 0,00 m (inferred)

| Door | Threshold | Ground | Rise | Solution | Main |
|---|---|---|---|---|---|
| d_L0_019 | 0,00 m | -0,15 m | 0,15 m | steps (1 x 0.150 m) | yes |
| d_L0_020 | 0,00 m | -0,15 m | 0,15 m | steps (1 x 0.150 m) |  |

Inferred (listed, CLAUDE.md evidence rules):

- slabs: a single drawn ground floor (user decision of 10 Oct 2026): the building ends at that floor; upper floors not drawn
- roof: a single drawn ground floor (user decision of 10 Oct 2026): the building ends at that floor; upper floors not drawn
- site: a single drawn ground floor (user decision of 10 Oct 2026): the building ends at that floor; upper floors not drawn
- site.ground: D3a: no ground drawn: 0.15 m under L0
- entrance d_L0_019: 0.15 m above the ground (terrain (flat)): a landing and 1 riser(s) of 0.150 m, tread 0.30 m (inferred)
- entrance d_L0_020: 0.15 m above the ground (terrain (flat)): a landing and 1 riser(s) of 0.150 m, tread 0.30 m (inferred)
- site.plinth: no SB. mark: the plinth up to the ground floor

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 5 piece(s) added, 8 wall cabinet run(s).

### Ebeveyn Odası (r_L0_ebeveyn_odasi, bedroom): completed (nothing fits: sleeping_double: no candidate position fits the room; storage: no candidate position fits the room)

- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_071

### Ebeveyn Odası (r_L0_ebeveyn_odasi_2, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_058, f_L0_098, f_L0_099, f_L0_100

### Yaşama (r_L0_yasama, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room)

- 2 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001, f_L0_002, f_L0_005, f_L0_006, f_L0_007, f_L0_008, f_L0_009, f_L0_055, f_L0_189, f_L0_190, f_L0_191, f_L0_193

### Ebeveyn Odası (r_L0_ebeveyn_odasi_3, bedroom): completed (nothing fits: sleeping_double: no candidate position fits the room; storage: no candidate position fits the room)

- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_072

### Ebeveyn Odası (r_L0_ebeveyn_odasi_4, bedroom): completed

- added f_L0_218: nightstand 0.40 x 0.40 (confidence -, rule)
- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_070, f_L0_136, f_L0_141

### Yaşama (r_L0_yasama_2, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_028, f_L0_029, f_L0_030, f_L0_065, f_L0_122, f_L0_123, f_L0_124, f_L0_125, f_L0_206, f_L0_207, f_L0_211

### Oda-01 (r_L0_oda_01, bedroom): completed (nothing fits: sleeping_single: no candidate position fits the room; storage: no candidate position fits the room)

- not placed sleeping_single: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_073, f_L0_103, f_L0_104, f_L0_183

### Yaşama (r_L0_yasama_3, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_022, f_L0_023, f_L0_024, f_L0_063, f_L0_111, f_L0_112, f_L0_113, f_L0_114, f_L0_202, f_L0_203, f_L0_209

### Yaşama (r_L0_yasama_4, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room)

- 2 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_011, f_L0_014, f_L0_015, f_L0_016, f_L0_017, f_L0_018, f_L0_059, f_L0_196, f_L0_197, f_L0_198

### Giriş Holü (r_L0_giris_holu, hall): completed

- added f_L0_223: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_074

### Banyo (r_L0_banyo, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_042, f_L0_045, f_L0_081, f_L0_150, f_L0_186

### Banyo (r_L0_banyo_2, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_044, f_L0_047, f_L0_079, f_L0_148, f_L0_187

### Banyo (r_L0_banyo_3, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_037, f_L0_038, f_L0_054, f_L0_056, f_L0_188, f_L0_192

### Giriş Holü (r_L0_giris_holu_2, hall): completed

- added f_L0_224: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_077

### Banyo (r_L0_banyo_4, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_039, f_L0_040, f_L0_060, f_L0_061, f_L0_145, f_L0_195, f_L0_199

### Hava Bacası (r_L0_hava_bacasi, shaft): skipped (shaft room: never furnished by AI)

No change, no addition.

### Oda (r_L0_oda_5, unknown): skipped (room type unknown: no furniture types to complete)

No change, no addition.

### Yaşama (r_L0_yasama_5, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_019, f_L0_020, f_L0_021, f_L0_062, f_L0_105, f_L0_106, f_L0_107, f_L0_108, f_L0_200, f_L0_201, f_L0_208

### Yaşama (r_L0_yasama_6, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_025, f_L0_026, f_L0_027, f_L0_064, f_L0_117, f_L0_118, f_L0_119, f_L0_120, f_L0_204, f_L0_205, f_L0_210

### Banyo (r_L0_banyo_5, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_041, f_L0_046, f_L0_080, f_L0_149, f_L0_184

### Yangın Merdiveni (r_L0_yangin_merdiveni, stair): skipped (stair room: never furnished by AI)

No change, no addition.

### Banyo (r_L0_banyo_6, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_033, f_L0_036, f_L0_053, f_L0_089, f_L0_179

### Kat Merdiveni (r_L0_kat_merdiveni, stair): skipped (stair room: never furnished by AI)

No change, no addition.

### Giriş Holü (r_L0_giris_holu_3, hall): completed

- added f_L0_227: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_076

### Banyo (r_L0_banyo_7, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_043, f_L0_048, f_L0_078, f_L0_147, f_L0_185

### Giriş Holü (r_L0_giris_holu_4, hall): completed

- added f_L0_228: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_075

### Banyo (r_L0_banyo_8, bathroom): completed (nothing fits: bathroom_set: no candidate position fits the room)

- not placed bathroom_set: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_034, f_L0_035, f_L0_082, f_L0_090, f_L0_180

### Ebeveyn Odası (r_L0_ebeveyn_odasi_5, bedroom): completed (nothing fits: storage: no candidate position fits the room)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_067, f_L0_130, f_L0_131

### Ebeveyn Odası (r_L0_ebeveyn_odasi_6, bedroom): completed (nothing fits: storage: no candidate position fits the room)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_066, f_L0_128, f_L0_129

### Yaşama (r_L0_yasama_7, living): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_050, f_L0_085, f_L0_086, f_L0_139, f_L0_155, f_L0_162, f_L0_182, f_L0_212

### Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_068, f_L0_132, f_L0_133, f_L0_143

### Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a_2, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_069, f_L0_134, f_L0_135, f_L0_144

### Yaşama (r_L0_yasama_8, living): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_049, f_L0_087, f_L0_088, f_L0_138, f_L0_163, f_L0_181, f_L0_213

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 171 of 171 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 164 ok, 7 failed; 0 changed by the AI.

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L0_053 | washing_machine (washing_machine) | 0.45 | 0.00 | yes | - |
| f_L0_074 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_092 (now centre None) |
| f_L0_075 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_093 (now back_edge w_L0_065) |
| f_L0_076 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_148 (now back_edge w_L0_066) |
| f_L0_077 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_147 (now centre None) |
| f_L0_133 | nightstand (nightstand) | 0.10 | 0.00 | yes | - |
| f_L0_141 | bed_double (bed_double) | 0.27 | - | - | front missing on one side |

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered; 2 dropped (no camera place worked).

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)

Gate for the exterior polish: **not_validated** (exterior views stay the Cycles render): gate/gate_calibration.json missing: gate calibrate did not run or failed.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | no |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: unverified | no |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: ok; right: ok | no |
| ext_4 | corner | left, back | - | cycles (gate_validation) | ok | back: ok; left: unverified | no |
| ext_7 | entrance | front | - | cycles (gate_validation) | ok | front: unverified | no |
| ext_6 | agent | front | - | cycles (gate_validation) | ok | front: unverified | no |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_5 | aerial | left, front | flat_cut roof (upper floors not drawn): no aerial view |
| ext_6 | frontal | front | 35.0 m in front of the front (entrance) facade: the building fills 8% of the frame (< 8%); 37.0 m in front of the front (entrance) facade: the building fills 7% of the frame (< 8%); 39.0 m in front of the front (entrance) facade: the building fills 7% of the frame (< 8%); 33.5 m in front of the front (entrance) facade: the building fills 8% of the frame (< 8%); 41.0 m in front of the front (entrance) facade: the building fills 6% of the frame (< 8%); 44.0 m in front of the front (entrance) facade: 44% of the view of the building is blocked by trees, the plot wall or another building; 47.0 m in front of the front (entrance) facade: the building fills 6% of the frame (< 8%) |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | warm greige | fallback | yes | style profile exterior.facade (assumed) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | dark_bronze | - | style | no | style profile exterior.window_frame |
| door | wood_oak_light | - | fallback | yes | style profile exterior.door (assumed) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | agent | no | agent override (docs/milestone11.md §17.3) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | warm greige | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof not_checked.

Roof heights: built eaves 3,00 m, ridge 3,00 m; drawn -; result not_checked.
- no eaves or ridge height in sheets.json or the building JSON

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| tekkat.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 9, block_name 34, group_member 29, none 55, rule 44. Recognition questions: 72; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_103 | r_L0_oda_01 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: dresser, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front right 0.90 |
| f_L0_104 | r_L0_oda_01 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_141 | r_L0_ebeveyn_odasi_4 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front top 0.90 |
| f_L0_162 | r_L0_yasama_7 | bookshelf | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: bookshelf, front bottom 0.90 |
| f_L0_163 | r_L0_yasama_8 | bookshelf | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: bookshelf, front top 0.90 |
| f_L0_179 | r_L0_banyo_6 | shower | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: shower, front bottom 0.90 |
| f_L0_180 | r_L0_banyo_8 | shower | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: shower, front bottom 0.90 |
| f_L0_181 | r_L0_yasama_8 | stove | yes | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: stove, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove, front right 0.90 |
| f_L0_182 | r_L0_yasama_7 | stove | yes | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: stove, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove, front left 0.90 |
| f_L0_183 | r_L0_oda_01 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front left 0.90 |
| f_L0_184 | r_L0_banyo_5 | bathtub | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front right 0.90 |
| f_L0_185 | r_L0_banyo_7 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front right 0.90 |
| f_L0_186 | r_L0_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front left 0.90 |
| f_L0_187 | r_L0_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front right 0.90 |
| f_L0_201 | r_L0_yasama_5 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_203 | r_L0_yasama_3 | floor_lamp | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_205 | r_L0_yasama_6 | floor_lamp | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_207 | r_L0_yasama_2 | floor_lamp | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |

## Site

The plot, paving, grass, parking and boundary walls marked built are built in the 3D scene and show in the exterior views; an area that is only a label (not built) is recorded, not built.

| id | what | detail |
|---|---|---|
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_balkon | area 'BALKON' (other) | label size -, measured - (-), no closed outline, recorded only (not built) |
| - | decor | other x 66 |

## Separators

None.

## Assumed values

- style exterior facade render in warm greige, roof concrete_tiles in anthracite, door as inside (wood_oak_light), paving paving in grey, garden grass from style.exterior_fallback of wenart/defaults.yaml (no word for them in the brief)
- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief slab_thickness: 0.2 (default, not in brief.yaml)
- brief furnished_rooms: complete (default, not in brief.yaml)
- brief furnished_rooms_keep: [] (default, not in brief.yaml)
- brief furnished_rooms_keep_size: False (default, not in brief.yaml)
- brief variants: all (default, not in brief.yaml)
- brief failed_levels: leave_out (default, not in brief.yaml)
- brief site: full (default, not in brief.yaml)
- brief exterior.facade:  (default, not in brief.yaml)
- brief exterior.roof:  (default, not in brief.yaml)
- brief exterior.window_frame:  (default, not in brief.yaml)
- brief exterior.door:  (default, not in brief.yaml)
- brief exterior.paving:  (default, not in brief.yaml)
- brief exterior.garden:  (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- brief render.lens_mm: auto (default, not in brief.yaml)
- brief render.exterior_views: True (default, not in brief.yaml)
- brief render.twin_rooms: one (default, not in brief.yaml)
- brief markers_in_final: False (default, not in brief.yaml)
- brief roof_terraces: auto (default, not in brief.yaml)
- brief site_options.front_court: auto (default, not in brief.yaml)
- brief levels.ground_rise: 0.15 (default, not in brief.yaml)
- brief levels.accessible_entrance: False (default, not in brief.yaml)
- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2,70 m (assumed_default)
- front kept from the drawing although both AI passes answered 'none': 1 piece(s) (f_L0_201)
- door height 2,10 m: 25 opening(s) (d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_005, d_L0_006 ...)
- opening height 2,10 m: 22 opening(s) (o_L0_001, o_L0_002, o_L0_003, o_L0_004, o_L0_005, o_L0_006 ...)
- window height 1,20 m: 64 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- window sill height 0,90 m: 64 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- f_L0_031 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_032 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- sl_L0 thickness: 0,20 m (assumed_default)
- roof overhang: 0,00 m (assumed; flat_cut: the roof ends at the outer wall face)
- roof thickness: 0,30 m (assumed; flat_cut: a flat roof slab (assumed))
- roof: upper floors not drawn: a flat roof slab with a 0.30 m parapet over L0 (flat_cut, inferred) assumed
- roof covering: not drawn (the outside look decides, see below)
- outside look facade: render in warm greige (fallback: style profile exterior.facade (assumed))
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
- outside look door: wood_oak_light (fallback: style profile exterior.door (assumed))
- outside look paving: paving in grey (fallback: style profile exterior.paving (assumed))
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))
- outside look plot_wall: render in warm greige (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_banyo_3: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_3 |
| area_light | 1 | r_L0_banyo_4: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_4 |
| area_light | 1 | r_L0_banyo_5: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_5 |
| area_light | 1 | r_L0_banyo_6: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_6 |
| area_light | 1 | r_L0_banyo_7: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_7 |
| area_light | 1 | r_L0_banyo_8: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_8 |
| area_light | 1 | r_L0_giris_holu_2: agent: The room is too dark for the camera view (exposure cap exceeded by 0.01 stops); applying the suggested lighting factor of 1.43 will brighten the scene to meet exposure requirements.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_giris_holu_2 |
| area_light | 1 | r_L0_giris_holu_4: agent: View cam_r_L0_giris_holu_4_2 is 0.04 stops over the EV cap; finding specifies x1.46 room light factor.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_giris_holu_4 |
| area_light | 1 | r_L0_hava_bacasi: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_hava_bacasi |
| area_light | 1 | r_L0_kat_holu: room has no window; the room's light rig (7 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_kat_holu |
| area_light | 1 | r_L0_kat_merdiveni: room has no window; the room's light rig (3 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_kat_merdiveni |
| area_light | 1 | r_L0_oda: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda |
| area_light | 1 | r_L0_oda_10: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_oda_10 |
| area_light | 1 | r_L0_oda_15: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_15 |
| area_light | 1 | r_L0_oda_16: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_16 |
| area_light | 1 | r_L0_oda_17: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_17 |
| area_light | 1 | r_L0_oda_18: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_18 |
| area_light | 1 | r_L0_oda_19: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_19 |
| area_light | 1 | r_L0_oda_20: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_20 |
| area_light | 1 | r_L0_oda_21: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_21 |
| area_light | 1 | r_L0_oda_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_2 |
| area_light | 1 | r_L0_oda_3: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_3 |
| area_light | 1 | r_L0_oda_4: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_4 |
| area_light | 1 | r_L0_oda_5: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_5 |
| area_light | 1 | r_L0_oda_6: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_6 |
| area_light | 1 | r_L0_oda_7: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_oda_7 |
| area_light | 1 | r_L0_oda_8: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_oda_8 |
| area_light | 1 | r_L0_oda_9: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_oda_9 |
| area_light | 1 | r_L0_yangin_merdiveni: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_yangin_merdiveni |
| area_light | 1 | r_L0_yasama_7: agent: Raise room light so cam_r_L0_yasama_7_1 exposure fits the +3.00 EV cap (finding asks x1.46).; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yasama_7 |
| bedding | 3 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_069, dress_f_L0_071, dress_f_L0_073 |
| boundary | 1 | no site plan: a low fence on the inferred plot boundary (inferred) | site |
| cabinet_fronts | 6 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_217, furn_f_L0_219, furn_f_L0_220 |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
| chaise_side | 2 | corner sofa without chaise_side: the chaise on the right (assumed) | furn_f_L0_190, furn_f_L0_196 |
| climate | 1 | the drawing's language (room and site labels) (inferred; the species of trees and hedges follow it): banyo, hol, kat, oda | site |
| coping | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| cut_through | 2 | the wall overlaps w_L0_005 at its opening win_L0_002: cut through both (a facade line drawn over a thicker wall) | w_L0_002, w_L0_006 |
| cut_through | 1 | the wall overlaps w_L0_088 at its opening win_L0_007: cut through both (a facade line drawn over a thicker wall) | w_L0_087 |
| cut_through | 3 | the wall overlaps w_L0_088 at its opening win_L0_008: cut through both (a facade line drawn over a thicker wall) | w_L0_087, w_L0_089, w_L0_091 |
| cut_through | 1 | the wall overlaps w_L0_088 at its opening win_L0_009: cut through both (a facade line drawn over a thicker wall) | w_L0_090 |
| cut_through | 1 | the wall overlaps w_L0_088 at its opening win_L0_010: cut through both (a facade line drawn over a thicker wall) | w_L0_090 |
| cut_through | 3 | the wall overlaps w_L0_088 at its opening win_L0_011: cut through both (a facade line drawn over a thicker wall) | w_L0_087, w_L0_089, w_L0_091 |
| cut_through | 1 | the wall overlaps w_L0_088 at its opening win_L0_012: cut through both (a facade line drawn over a thicker wall) | w_L0_087 |
| cut_through | 4 | the wall overlaps w_L0_089 at its opening win_L0_052: cut through both (a facade line drawn over a thicker wall) | w_L0_087, w_L0_088, w_L0_090 |
| cut_through | 4 | the wall overlaps w_L0_089 at its opening win_L0_053: cut through both (a facade line drawn over a thicker wall) | w_L0_087, w_L0_088, w_L0_090 |
| cut_through | 1 | the wall overlaps w_L0_111 at its opening win_L0_056: cut through both (a facade line drawn over a thicker wall) | w_L0_113 |
| cut_through | 1 | the wall overlaps w_L0_116 at its opening win_L0_018: cut through both (a facade line drawn over a thicker wall) | w_L0_115 |
| cut_through | 1 | the wall overlaps w_L0_119 at its opening win_L0_019: cut through both (a facade line drawn over a thicker wall) | w_L0_120 |
| cut_through | 1 | the wall overlaps w_L0_149 at its opening win_L0_020: cut through both (a facade line drawn over a thicker wall) | w_L0_150 |
| cut_through | 1 | the wall overlaps w_L0_149 at its opening win_L0_021: cut through both (a facade line drawn over a thicker wall) | w_L0_150 |
| cut_through | 4 | the wall overlaps w_L0_151 at its opening win_L0_061: cut through both (a facade line drawn over a thicker wall) | w_L0_149, w_L0_150, w_L0_152 |
| cut_through | 4 | the wall overlaps w_L0_151 at its opening win_L0_062: cut through both (a facade line drawn over a thicker wall) | w_L0_149, w_L0_150, w_L0_152 |
| cut_through | 1 | the wall overlaps w_L0_152 at its opening win_L0_024: cut through both (a facade line drawn over a thicker wall) | w_L0_153 |
| cut_through | 3 | the wall overlaps w_L0_152 at its opening win_L0_025: cut through both (a facade line drawn over a thicker wall) | w_L0_149, w_L0_151, w_L0_153 |
| cut_through | 3 | the wall overlaps w_L0_152 at its opening win_L0_028: cut through both (a facade line drawn over a thicker wall) | w_L0_149, w_L0_151, w_L0_153 |
| cut_through | 1 | the wall overlaps w_L0_152 at its opening win_L0_029: cut through both (a facade line drawn over a thicker wall) | w_L0_153 |
| direction | 2 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L0_031, furn_f_L0_032 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 25 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| eaves_height | 1 | flat roof without a height: the top level's ceiling + an assumed 0.3 m roof slab | roof |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| facade | 1 | style profile exterior.facade (assumed) | exterior |
| flat_cut | 1 | upper floors not drawn | roof |
| ground:all | 1 | D3a: nothing about the ground is drawn: the ground floor stands 0.15 m above it (one inferred step) | site |
| handrail | 2 | design detail on every flight side not against a wall; not in the documents | furn_f_L0_031, furn_f_L0_032 |
| height | 25 | door height listed as assumed in the building JSON | d_L0_001, d_L0_002, d_L0_003 |
| height | 4 | no height in the JSON; type height for bathtub | furn_f_L0_184, furn_f_L0_185, furn_f_L0_186 |
| height | 9 | no height in the JSON; type height for bed_double | furn_f_L0_058, furn_f_L0_066, furn_f_L0_067 |
| height | 1 | no height in the JSON; type height for bed_single | furn_f_L0_073 |
| height | 2 | no height in the JSON; type height for bookshelf | furn_f_L0_162, furn_f_L0_163 |
| height | 14 | no height in the JSON; type height for chair | furn_f_L0_007, furn_f_L0_008, furn_f_L0_009 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L0_201, furn_f_L0_203, furn_f_L0_205 |
| height | 2 | no height in the JSON; type height for fridge | furn_f_L0_212, furn_f_L0_213 |
| height | 14 | no height in the JSON; type height for kitchen_counter | furn_f_L0_001, furn_f_L0_002, furn_f_L0_010 |
| height | 3 | no height in the JSON; type height for shower | furn_f_L0_054, furn_f_L0_179, furn_f_L0_180 |
| height | 6 | no height in the JSON; type height for sofa_corner | furn_f_L0_138, furn_f_L0_139, furn_f_L0_208 |
| height | 8 | no height in the JSON; type height for stove | furn_f_L0_049, furn_f_L0_050, furn_f_L0_055 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L0_151, furn_f_L0_152, furn_f_L0_153 |
| height | 6 | no height in the JSON; type height for table_dining | furn_f_L0_006, furn_f_L0_015, furn_f_L0_105 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L0_051, furn_f_L0_052, furn_f_L0_056 |
| height | 6 | no height in the JSON; type height for tv_unit | furn_f_L0_108, furn_f_L0_114, furn_f_L0_120 |
| height | 8 | no height in the JSON; type height for washing_machine | furn_f_L0_053, furn_f_L0_057, furn_f_L0_061 |
| height | 22 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L0_003 |
| height | 64 | window height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| inside_sill | 1 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_057_inside_sill |
| inside_sill | 20 | design detail of the documented window: an inside sill 0.075 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_031_inside_sill, win_L0_032_inside_sill, win_L0_033_inside_sill |
| inside_sill | 5 | design detail of the documented window: an inside sill 0.075 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_003_inside_sill, win_L0_004_inside_sill, win_L0_005_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.125 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_054_inside_sill, win_L0_060_inside_sill |
| inside_sill | 5 | design detail of the documented window: an inside sill 0.15 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_009_inside_sill, win_L0_010_inside_sill, win_L0_018_inside_sill |
| inside_sill | 4 | design detail of the documented window: an inside sill 0.15 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_007_inside_sill, win_L0_008_inside_sill, win_L0_011_inside_sill |
| inside_sill | 1 | design detail of the documented window: an inside sill 0.155 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_017_inside_sill |
| inside_sill | 1 | design detail of the documented window: an inside sill 0.155 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_056_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.1575 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_026_inside_sill, win_L0_027_inside_sill |
| inside_sill | 4 | design detail of the documented window: an inside sill 0.1575 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_024_inside_sill, win_L0_025_inside_sill, win_L0_028_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.205 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_015_inside_sill, win_L0_016_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.215 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_020_inside_sill, win_L0_021_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.225 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_001_inside_sill, win_L0_002_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.225 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_055_inside_sill, win_L0_059_inside_sill |
| inside_sill | 4 | design detail of the documented window: an inside sill 0.2675 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_022_inside_sill, win_L0_023_inside_sill, win_L0_061_inside_sill |
| inside_sill | 4 | design detail of the documented window: an inside sill 0.27 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L0_013_inside_sill, win_L0_014_inside_sill, win_L0_052_inside_sill |
| inside_sill | 1 | design detail of the documented window: an inside sill 0.2775 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_040_inside_sill |
| inside_sill | 1 | design detail of the documented window: an inside sill 0.28 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_039_inside_sill |
| inside_sill | 1 | design detail of the documented window: an inside sill 0.335 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_058_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| modules | 14 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L0_001, furn_f_L0_002, furn_f_L0_010 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| outline | 1 | no roof outline drawn: the walls' outline (wall_union) grown by the overhang 0.50 m | roof |
| path:d_L0_019,d_L0_020 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: concrete_exposed (style family modern; not drawn) | facade |
| plot | 1 | no site plan: the plot is the outline's rectangle + 6 m (inferred) | site |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_070 (no nightstand): the lamp would stand outside the room | rig_r_L0_ebeveyn_odasi_4 |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_071 (no nightstand): the lamp would stand outside the room | rig_r_L0_ebeveyn_odasi, rig_r_L0_ebeveyn_odasi |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_072 (no nightstand): the lamp would stand outside the room | rig_r_L0_ebeveyn_odasi_3, rig_r_L0_ebeveyn_odasi_3 |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_073 (no nightstand): the lamp would stand outside the room | rig_r_L0_oda_01, rig_r_L0_oda_01 |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_3: ceiling fixture at the pole of inaccessibility of r_L0_banyo_3; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_3_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_3: mirror light over the washbasin f_L0_188; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_3_mirror_1_light |
| rig_light | 1 | r_L0_banyo_4: ceiling fixture at the pole of inaccessibility of r_L0_banyo_4; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_4_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_4: mirror light over the washbasin f_L0_195; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_4_mirror_1_light |
| rig_light | 1 | r_L0_banyo_5: ceiling fixture at the pole of inaccessibility of r_L0_banyo_5; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_5_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_6: ceiling fixture at the pole of inaccessibility of r_L0_banyo_6; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_6_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_7: ceiling fixture at the pole of inaccessibility of r_L0_banyo_7; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_7_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_8: ceiling fixture at the pole of inaccessibility of r_L0_banyo_8; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_8_ceiling_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_2: bedside lamp on the nightstand f_L0_099; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_2: bedside lamp on the nightstand f_L0_100; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_4: bedside lamp on the nightstand f_L0_136; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_5: bedside lamp on the nightstand f_L0_130; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_5_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_5: bedside lamp on the nightstand f_L0_131; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_5_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_6: bedside lamp on the nightstand f_L0_128; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_6_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_6: bedside lamp on the nightstand f_L0_129; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_6_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a: bedside lamp on the nightstand f_L0_132; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a: bedside lamp on the nightstand f_L0_133; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a_2: bedside lamp on the nightstand f_L0_134; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_2_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a_2: bedside lamp on the nightstand f_L0_135; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_2_bedside_1_light |
| rig_light | 1 | r_L0_giris_holu: ceiling fixture at the pole of inaccessibility of r_L0_giris_holu, 2 x 1100 lm bulbs for 450 lm/m2 over 3.3 m2 and 1 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_giris_holu_ceiling_1_light |
| rig_light | 1 | r_L0_giris_holu_2: ceiling fixture at the pole of inaccessibility of r_L0_giris_holu_2, 2 x 1100 lm bulbs for 450 lm/m2 over 3.3 m2 and 1 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_giris_holu_2_ceiling_1_light |
| rig_light | 1 | r_L0_giris_holu_3: ceiling fixture at the pole of inaccessibility of r_L0_giris_holu_3, 2 x 1100 lm bulbs for 450 lm/m2 over 3.3 m2 and 1 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_giris_holu_3_ceiling_1_light |
| rig_light | 1 | r_L0_giris_holu_4: ceiling fixture at the pole of inaccessibility of r_L0_giris_holu_4, 2 x 1100 lm bulbs for 450 lm/m2 over 3.3 m2 and 1 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_giris_holu_4_ceiling_1_light |
| rig_light | 7 | r_L0_kat_holu: ceiling fixture at the pole of inaccessibility of r_L0_kat_holu, 2 x 1100 lm bulbs for 450 lm/m2 over 30.1 m2 and 7 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_kat_holu_ceiling_1_light, rig_r_L0_kat_holu_ceiling_2_light, rig_r_L0_kat_holu_ceiling_3_light |
| rig_light | 3 | r_L0_kat_merdiveni: ceiling fixture at the pole of inaccessibility of r_L0_kat_merdiveni, 3 x 1100 lm bulbs for 450 lm/m2 over 17.8 m2 and 3 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_kat_merdiveni_ceiling_1_light, rig_r_L0_kat_merdiveni_ceiling_2_light, rig_r_L0_kat_merdiveni_ceiling_3_light |
| rig_light | 1 | r_L0_oda_10: ceiling fixture at the pole of inaccessibility of r_L0_oda_10, 1 x 1100 lm bulbs for 450 lm/m2 over 1.9 m2 and 1 fixture(s); 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_oda_10_ceiling_1_light |
| rig_light | 1 | r_L0_oda_7: ceiling fixture at the pole of inaccessibility of r_L0_oda_7, 1 x 1100 lm bulbs for 450 lm/m2 over 1.9 m2 and 1 fixture(s); 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_oda_7_ceiling_1_light |
| rig_light | 1 | r_L0_oda_8: ceiling fixture at the pole of inaccessibility of r_L0_oda_8, 1 x 1100 lm bulbs for 450 lm/m2 over 1.4 m2 and 1 fixture(s); 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_oda_8_ceiling_1_light |
| rig_light | 1 | r_L0_oda_9: ceiling fixture at the pole of inaccessibility of r_L0_oda_9, 1 x 1100 lm bulbs for 450 lm/m2 over 1.4 m2 and 1 fixture(s); 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_oda_9_ceiling_1_light |
| rig_light | 1 | r_L0_ruzgarlik: ceiling fixture at the pole of inaccessibility of r_L0_ruzgarlik, 7 x 1100 lm bulbs for 450 lm/m2 over 16.0 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_ruzgarlik_ceiling_1_light |
| rig_light | 2 | r_L0_yangin_merdiveni: ceiling fixture at the pole of inaccessibility of r_L0_yangin_merdiveni, 4 x 1100 lm bulbs for 450 lm/m2 over 17.5 m2 and 2 fixture(s); 4400.0 lm -> 12.48 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_yangin_merdiveni_ceiling_1_light, rig_r_L0_yangin_merdiveni_ceiling_2_light |
| rig_light | 1 | r_L0_yasama: pendant over the dining table f_L0_006; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_yasama_pendant_1_light |
| rig_light | 1 | r_L0_yasama_2: pendant over the dining table f_L0_122; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_yasama_2_pendant_1_light |
| rig_light | 1 | r_L0_yasama_3: pendant over the dining table f_L0_111; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_yasama_3_pendant_1_light |
| rig_light | 1 | r_L0_yasama_4: pendant over the dining table f_L0_015; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_yasama_4_pendant_1_light |
| rig_light | 1 | r_L0_yasama_5: pendant over the dining table f_L0_105; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_yasama_5_pendant_1_light |
| rig_light | 1 | r_L0_yasama_6: pendant over the dining table f_L0_117; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_yasama_6_pendant_1_light |
| rig_mirror | 1 | no washbasin in r_L0_banyo: no mirror light | rig_r_L0_banyo |
| rig_mirror | 1 | no washbasin in r_L0_banyo_2: no mirror light | rig_r_L0_banyo_2 |
| rig_mirror | 1 | no washbasin in r_L0_banyo_5: no mirror light | rig_r_L0_banyo_5 |
| rig_mirror | 1 | no washbasin in r_L0_banyo_6: no mirror light | rig_r_L0_banyo_6 |
| rig_mirror | 1 | no washbasin in r_L0_banyo_7: no mirror light | rig_r_L0_banyo_7 |
| rig_mirror | 1 | no washbasin in r_L0_banyo_8: no mirror light | rig_r_L0_banyo_8 |
| rise_m | 2 | on the top level with no level above and not over a stair of the level below: the stair stops under the roof underside; no roof opening is drawn, none is cut | furn_f_L0_031, furn_f_L0_032 |
| riser_m | 2 | limited by the roof underside (no level above, assumed): 2.694 m / 24 drawn risers | furn_f_L0_031, furn_f_L0_032 |
| roof | 1 | listed as assumed in the building JSON | roof |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 20 | outside sill 1.66 x 0.084 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_031_sill, win_L0_032_sill, win_L0_033_sill |
| sill | 1 | outside sill 2.61 x 0.234 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill |
| sill | 1 | outside sill 2.96 x 0.234 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill |
| sill_height | 64 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 47 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_ebeveyn_odasi, skirting_r_L0_ebeveyn_odasi_2, skirting_r_L0_yasama |
| slab | 1 | thickness 0.2 m assumed in the building JSON | sl_L0 |
| steps:d_L0_019 | 1 | entrance door 0.15 m above the ground: a landing and 0 steps of 0.150 m (inferred) | site |
| steps:d_L0_020 | 1 | entrance door 0.15 m above the ground: a landing and 0 steps of 0.150 m (inferred) | site |
| thickness | 1 | flat_cut: a flat roof slab (assumed) | roof |
| turn | 2 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L0_031, furn_f_L0_032 |
| waist | 2 | the documents show the stair in plan only | furn_f_L0_031, furn_f_L0_032 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_plant_large_minimal_4_71886746 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_potted_plant_industrial_2_eb3d21f5 [tool_nc], gen_shower_scandinavian_1_0ae4a37a [tool_nc], gen_washing_machine_classic_1_dffff7e0 [tool_nc], gen_washing_machine_modern_1_f4bdd46e [tool_nc], hssd_01a976d8dd0f7a1f35b01709c20fca6683b94311 [non_commercial], hssd_031024e00569909d466d87df9fead90355ba29e5 [non_commercial], hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_2c2b2914fc526f6e8bbe65511ecf58bba0027ec0 [non_commercial], hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_333fbf609c0f0877768188c43a0a812cc46e26ae [non_commercial], hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial], hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_7835135c9a3abefa43deca495710555800d8aeca [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_81222d2540321a5f3bab53c38a4605b0990b5800 [non_commercial], hssd_856317b238f6a70ae6f0afffed1f6d5e3ab7b80c [non_commercial], hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial], hssd_94f82d1154b9db0d56038b183832b0dfceff8819 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial], hssd_e00975f6de5015107944634171269d8700c136a7 [non_commercial], hssd_xxxxbeae246cx5cbcx482dx81faxd6e6f844d62d [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_e00975f6de5015107944634171269d8700c136a7 [non_commercial])
- cam_r_L0_banyo_2_1: commercial-safe: yes
- cam_r_L0_banyo_3_1: commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_7835135c9a3abefa43deca495710555800d8aeca [non_commercial], hssd_856317b238f6a70ae6f0afffed1f6d5e3ab7b80c [non_commercial])
- cam_r_L0_banyo_4_1: commercial-safe: no (flagged assets: hssd_031024e00569909d466d87df9fead90355ba29e5 [non_commercial], hssd_81222d2540321a5f3bab53c38a4605b0990b5800 [non_commercial])
- cam_r_L0_banyo_4_2: commercial-safe: no (flagged assets: hssd_031024e00569909d466d87df9fead90355ba29e5 [non_commercial], hssd_81222d2540321a5f3bab53c38a4605b0990b5800 [non_commercial])
- cam_r_L0_banyo_5_1: commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial])
- cam_r_L0_banyo_5_2: commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial])
- cam_r_L0_banyo_6_1: commercial-safe: no (flagged assets: hssd_01a976d8dd0f7a1f35b01709c20fca6683b94311 [non_commercial])
- cam_r_L0_banyo_6_2: commercial-safe: no (flagged assets: gen_washing_machine_modern_1_f4bdd46e [tool_nc])
- cam_r_L0_banyo_7_1: commercial-safe: no (flagged assets: hssd_94f82d1154b9db0d56038b183832b0dfceff8819 [non_commercial])
- cam_r_L0_banyo_8_1: commercial-safe: no (flagged assets: gen_shower_scandinavian_1_0ae4a37a [tool_nc])
- cam_r_L0_ebeveyn_odasi_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_2_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_2_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_2_3: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_3_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_3_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_4_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_4_2: commercial-safe: no (flagged assets: hssd_xxxxbeae246cx5cbcx482dx81faxd6e6f844d62d [non_commercial])
- cam_r_L0_ebeveyn_odasi_4_3: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_5_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_5_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_5_3: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_6_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_6_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_m_k_a_1: commercial-safe: no (flagged assets: hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L0_ebeveyn_odasi_m_k_a_2: commercial-safe: no (flagged assets: hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L0_ebeveyn_odasi_m_k_a_2_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_m_k_a_2_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_m_k_a_2_3: commercial-safe: no (flagged assets: gen_plant_large_minimal_4_71886746 [tool_nc])
- cam_r_L0_ebeveyn_odasi_m_k_a_3: commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L0_giris_holu_1: commercial-safe: no (flagged assets: hssd_2c2b2914fc526f6e8bbe65511ecf58bba0027ec0 [non_commercial])
- cam_r_L0_giris_holu_2: commercial-safe: no (flagged assets: hssd_2c2b2914fc526f6e8bbe65511ecf58bba0027ec0 [non_commercial])
- cam_r_L0_giris_holu_2_1: commercial-safe: no (flagged assets: gen_washing_machine_classic_1_dffff7e0 [tool_nc])
- cam_r_L0_giris_holu_2_2: commercial-safe: yes
- cam_r_L0_giris_holu_3_1: commercial-safe: no (flagged assets: hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial])
- cam_r_L0_giris_holu_4_1: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial])
- cam_r_L0_giris_holu_4_2: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial])
- cam_r_L0_kat_holu_1: commercial-safe: yes
- cam_r_L0_kat_holu_2: commercial-safe: yes
- cam_r_L0_kat_holu_3: commercial-safe: yes
- cam_r_L0_kat_merdiveni_1: commercial-safe: yes
- cam_r_L0_kat_merdiveni_2: commercial-safe: yes
- cam_r_L0_kat_merdiveni_3: commercial-safe: yes
- cam_r_L0_oda_01_1: commercial-safe: yes
- cam_r_L0_oda_01_2: commercial-safe: yes
- cam_r_L0_oda_01_3: commercial-safe: yes
- cam_r_L0_oda_10_1: commercial-safe: yes
- cam_r_L0_oda_19_1: commercial-safe: yes
- cam_r_L0_oda_19_2: commercial-safe: yes
- cam_r_L0_oda_19_3: commercial-safe: yes
- cam_r_L0_oda_7_1: commercial-safe: yes
- cam_r_L0_ruzgarlik_1: commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial])
- cam_r_L0_ruzgarlik_2: commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial])
- cam_r_L0_ruzgarlik_3: commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial])
- cam_r_L0_yangin_merdiveni_1: commercial-safe: yes
- cam_r_L0_yangin_merdiveni_2: commercial-safe: yes
- cam_r_L0_yangin_merdiveni_3: commercial-safe: yes
- cam_r_L0_yasama_1: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_2: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_2_1: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial])
- cam_r_L0_yasama_2_2: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial])
- cam_r_L0_yasama_2_3: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial])
- cam_r_L0_yasama_3: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_3_1: commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_3_2: commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_3_3: commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_4_1: commercial-safe: no (flagged assets: hssd_333fbf609c0f0877768188c43a0a812cc46e26ae [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_4_2: commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_4_3: commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_5_1: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_5_2: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_5_3: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_6_1: commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_6_2: commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_6_3: commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_7_1: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc])
- cam_r_L0_yasama_7_2: commercial-safe: no (flagged assets: gen_potted_plant_industrial_2_eb3d21f5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_7_3: commercial-safe: no (flagged assets: gen_potted_plant_industrial_2_eb3d21f5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_8_1: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_8_2: commercial-safe: yes
- cam_r_L0_yasama_8_3: commercial-safe: yes
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_4: commercial-safe: yes
- ext_6: commercial-safe: yes
- ext_7: commercial-safe: yes

## Built below library level (Milestone 13)

36 furniture piece(s) built from a module builder or a parametric family instead of a library model: 6 library gap(s) to close with a real model, 30 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

| id | type | method | builder | room | room type | source | gap | used |
|---|---|---|---|---|---|---|---|---|
| f_L0_001 | kitchen_counter | module | kitchen_run | r_L0_yasama | living | from_documents | no (by design) | - |
| f_L0_002 | kitchen_counter | module | kitchen_run | r_L0_yasama | living | from_documents | no (by design) | - |
| f_L0_005 | sink_kitchen | module | kitchen_run | r_L0_yasama | living | from_documents | no (by design) | - |
| f_L0_010 | kitchen_counter | module | kitchen_run | r_L0_yasama_4 | living | from_documents | no (by design) | - |
| f_L0_011 | kitchen_counter | module | kitchen_run | r_L0_yasama_4 | living | from_documents | no (by design) | - |
| f_L0_014 | sink_kitchen | module | kitchen_run | r_L0_yasama_4 | living | from_documents | no (by design) | - |
| f_L0_019 | kitchen_counter | module | kitchen_run | r_L0_yasama_5 | living | from_documents | no (by design) | - |
| f_L0_020 | kitchen_counter | module | kitchen_run | r_L0_yasama_5 | living | from_documents | no (by design) | - |
| f_L0_021 | sink_kitchen | module | kitchen_run | r_L0_yasama_5 | living | from_documents | no (by design) | - |
| f_L0_022 | kitchen_counter | module | kitchen_run | r_L0_yasama_3 | living | from_documents | no (by design) | - |
| f_L0_023 | kitchen_counter | module | kitchen_run | r_L0_yasama_3 | living | from_documents | no (by design) | - |
| f_L0_024 | sink_kitchen | module | kitchen_run | r_L0_yasama_3 | living | from_documents | no (by design) | - |
| f_L0_025 | kitchen_counter | module | kitchen_run | r_L0_yasama_6 | living | from_documents | no (by design) | - |
| f_L0_026 | kitchen_counter | module | kitchen_run | r_L0_yasama_6 | living | from_documents | no (by design) | - |
| f_L0_027 | sink_kitchen | module | kitchen_run | r_L0_yasama_6 | living | from_documents | no (by design) | - |
| f_L0_028 | kitchen_counter | module | kitchen_run | r_L0_yasama_2 | living | from_documents | no (by design) | - |
| f_L0_029 | kitchen_counter | module | kitchen_run | r_L0_yasama_2 | living | from_documents | no (by design) | - |
| f_L0_030 | sink_kitchen | module | kitchen_run | r_L0_yasama_2 | living | from_documents | no (by design) | - |
| f_L0_031 | stair | parametric | parametric:stair | r_L0_kat_merdiveni | stair | from_documents | no (by design) | - |
| f_L0_032 | stair | parametric | parametric:stair | r_L0_yangin_merdiveni | stair | from_documents | no (by design) | - |
| f_L0_085 | kitchen_counter | module | kitchen_run | r_L0_yasama_7 | living | from_documents | no (by design) | - |
| f_L0_086 | sink_kitchen | module | kitchen_run | r_L0_yasama_7 | living | from_documents | no (by design) | - |
| f_L0_087 | kitchen_counter | module | kitchen_run | r_L0_yasama_8 | living | from_documents | no (by design) | - |
| f_L0_088 | sink_kitchen | module | kitchen_run | r_L0_yasama_8 | living | from_documents | no (by design) | - |
| f_L0_162 | bookshelf | parametric | parametric:bookshelf | r_L0_yasama_7 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_163 | bookshelf | parametric | parametric:bookshelf | r_L0_yasama_8 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_201 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_5 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_203 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_3 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_205 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_6 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_207 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_2 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_217 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama | living | added_by_ai | no (by design) | - |
| f_L0_219 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_2 | living | added_by_ai | no (by design) | - |
| f_L0_220 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_3 | living | added_by_ai | no (by design) | - |
| f_L0_222 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_4 | living | added_by_ai | no (by design) | - |
| f_L0_225 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_5 | living | added_by_ai | no (by design) | - |
| f_L0_226 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_6 | living | added_by_ai | no (by design) | - |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |

Assets: textures CC0 x 18; furniture/decor models CC-BY-4.0 x 99, CC-BY-NC-4.0 x 50, CC0 x 4, generated (Infinigen v1.19.0, BSD-3-Clause) x 2, generated (TRELLIS.2-4B, MIT) x 11 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Stove from Poly by Google" by IronEqual (https://sketchfab.com/3d-models/68e164f1a9414c29820ac2eaf6d8ac04), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_049, f_L0_050)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261017-091212-full-20261017T091758Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 28.4 s | earlier outputs without run records moved to /workspace/outputs-archive/real03-20261017T091758Z |
| pipeline | pending | 87.2 s | 66 recognition question(s) written (recognition/requests.json) |
| style | ok | 0.2 s | - |
| recognize | ok | 15.6 s | - |
| pipeline_final | ok | 86.0 s | answers applied |
| fit | ok | 6.0 s | - |
| layout | ok | 16.9 s | - |
| decor_ask | ok | 4.5 min | - |
| photos | ok | 3.4 s | - |
| assets | ok | 2.2 s | - |
| decor | ok | 15.0 s | - |
| refit | ok | 39.2 s | - |
| build | ok | 26.0 min | - |
| agent_previews | ok | 10.1 min | 14 view(s) |
| agent_apply | ok | 21.0 s | - |
| agent | ok | 41.8 min | 3 round(s), 36 finding(s) removed by 47 accepted edit(s) (measured; 55 predicted by the dry re-checks), 183 rejected; stop: max rounds reached |
| render | ok | 28.7 min | - |
| export | ok | 2.9 min | - |
| controls | ok | 2.9 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 2.3 min | - |
| check | ok | 6.5 min | - |
| combine | ok | 64.0 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 48 edit(s) accepted, 186 rejected, 782 model calls (8413629 tokens), 52.3 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 48 / 186 (20 % accepted) |
| rejected by reason | fixture_place 34, acceptance 27, drawn_lock 24, max_tries 20, no_overlap 14 |
| rooms checked by code / vision / planner | 55 / 36 / 31 |
| rooms with fixable critical or major findings visited | 31 of 31 |
| critical before -> after | 2 -> 1 |
| major before -> after | 179 -> 149 |
| agent minutes; first accepted edit after | 49.66; 31.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 13; 249; 84 (51) |
| critical/major findings removed (measured by the next round; predicted by the dry re-checks) | 44 measured; 56 predicted |

Library gaps reported by the agent: bookshelf (No audited bookshelf model fits the drawn 1.8 x 0.25 m footprint within tolerance; the parametric build is the correct fallback.), kitchen_counter (No audited library model of type kitchen_counter exists (catalog count 0), so the F9 overlap with stove f_L0_050 cannot be fixed by swap_model; the counter is a module build of the drawn run.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 179 | 44 | 4 | 21 | 87 | refit | 38 |
| 2 | 1 | 164 | 43 | 4 | 14 | 49 | refit | 19 |
| 3 | 1 | 156 | 41 | 2 | 12 | 47 | refit | 14 |
| 4 | 1 | 149 | 41 | 2 | 1 | 3 | refit | 3 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D1 | 0 | 0 | 0 | 1 |
| D2 | 0 | 5 | 0 | 0 |
| F1 | 0 | 21 | 0 | 0 |
| F3 | 4 | 44 | 4 | 0 |
| F4 | 0 | 19 | 0 | 0 |
| F9 | 0 | 105 | 0 | 4 |
| G1 | 0 | 8 | 8 | 0 |
| G10 | 0 | 47 | 0 | 0 |
| G11 | 0 | 23 | 0 | 0 |
| G12 | 0 | 60 | 0 | 0 |
| G13 | 0 | 12 | 0 | 0 |
| G14 | 0 | 16 | 0 | 0 |
| G2 | 0 | 12 | 0 | 0 |
| G4 | 0 | 0 | 12 | 0 |
| G5 | 0 | 28 | 0 | 0 |
| G6 | 0 | 32 | 0 | 0 |
| G8 | 0 | 56 | 0 | 0 |
| G9 | 0 | 24 | 0 | 0 |
| LG | 0 | 0 | 24 | 0 |
| NR | 0 | 23 | 0 | 0 |
| R3 | 0 | 0 | 30 | 0 |
| RC | 0 | 0 | 52 | 0 |
| S2 | 0 | 75 | 0 | 0 |
| S5 | 0 | 0 | 38 | 0 |
| X2 | 0 | 1 | 0 | 0 |
| X3 | 0 | 0 | 0 | 7 |
| X4 | 0 | 8 | 0 | 0 |
| X6 | 0 | 10 | 1 | 0 |
| X7 | 0 | 2 | 0 | 0 |
| lighting_dark | 1 | 17 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 284 | 1 | set_lighting | r_L0_yasama_7 | agent_override | - | Raise room light so cam_r_L0_yasama_7_1 exposure fits the +3.00 EV cap (finding asks x1.46). | - | - |
| 287 | 1 | remove_piece | f_L0_216 | added_by_ai | 0.0 -> 0.0 | AI-added wall_cabinet is not a piece of a living room; not required by the program, so removing it clears the wrong_type finding. | ![](agent/r1_029_remove_piece_before_r_L0_yasama.png) | ![](agent/r1_031_remove_piece_after_r_L0_yasama.png) |
| 288 | 1 | remove_piece | f_L0_221 | added_by_ai | 0.0 -> 0.0 | wall_cabinet added_by_ai is not a piece of a living room (F1 wrong_type) | ![](agent/r1_030_remove_piece_before_r_L0_yasama_4.png) | ![](agent/r1_032_remove_piece_after_r_L0_yasama_4.png) |
| 330 | 1 | set_lighting | r_L0_kat_merdiveni | agent_override | - | All three cameras report the room too dark (exposure over the +3.00 EV cap); applying the maximum required factor x1.71 so every view meets the cap. | - | - |
| 332 | 1 | report_library_gap | f_L0_163 | library_gap | - | No audited bookshelf model fits the drawn 1.8 x 0.25 m footprint within tolerance; the parametric build is the correct fallback. | - | - |
| 338 | 1 | set_lighting | r_L0_yangin_merdiveni | agent_override | - | Both cameras are under-exposed (+4.29 EV and +3.85 EV vs +3.00 cap); x3 covers the worst case (x2.44 needed) plus headroom for non-scaling light, fixing both dark views. | - | - |
| 394 | 1 | fix_fixture | f_L0_179 | adjusted_by_ai | 87.0 -> 87.0 | Shower cuts wall w_L0_048 by 0.041 m (tolerance 0.030 m); nudge it to clear the wall. | ![](agent/r1_104_fix_fixture_before_r_L0_banyo_6.png) | ![](agent/r1_106_fix_fixture_after_r_L0_banyo_6.png) |
| 401 | 1 | rotate_piece | f_L0_077 | adjusted_by_ai | 70.0 -> 80.0 | Washing machine faces 0° (East) into a wall; rotating to 90° (North) orients the front into the room space, resolving F4. | ![](agent/r1_110_rotate_piece_before_r_L0_giris_holu_2.png) | ![](agent/r1_111_rotate_piece_after_r_L0_giris_holu_2.png) |
| 404 | 1 | set_lighting | r_L0_giris_holu_2 | agent_override | - | The room is too dark for the camera view (exposure cap exceeded by 0.01 stops); applying the suggested lighting factor of 1.43 will brighten the scene to meet exposure requirements. | - | - |
| 410 | 1 | move_piece | f_L0_133 | adjusted_by_ai | 80.0 -> 80.0 | Shift nightstand f_L0_133 0.1 m toward -y to create space for the bed to move and improve G5 clearance. | ![](agent/r1_115_move_piece_before_r_L0_ebeveyn_odasi_m_k_a.png) | ![](agent/r1_116_move_piece_after_r_L0_ebeveyn_odasi_m_k_a.png) |
| 416 | 1 | swap_model | f_L0_053 | adjusted_by_ai | 87.0 -> 87.0 | Replace the crude low-poly box with a proper modern washing machine model (0.60 x 0.65 m, matching the drawn size). | ![](agent/r1_121_swap_model_before_r_L0_banyo_6.png) | ![](agent/r1_122_swap_model_after_r_L0_banyo_6.png) |
| 434 | 1 | rotate_piece | f_L0_074 | adjusted_by_ai | 70.0 -> 80.0 | Try facing 90° (toward the room interior) since 0° and 180° both face walls in this corner. | ![](agent/r1_137_rotate_piece_before_r_L0_giris_holu.png) | ![](agent/r1_139_rotate_piece_after_r_L0_giris_holu.png) |
| 437 | 1 | rotate_piece | f_L0_076 | adjusted_by_ai | 70.0 -> 80.0 | Turn the washing machine front away from the wall it faces into the room, resolving F4. | ![](agent/r1_140_rotate_piece_before_r_L0_giris_holu_3.png) | ![](agent/r1_143_rotate_piece_after_r_L0_giris_holu_3.png) |
| 439 | 1 | rotate_piece | f_L0_075 | adjusted_by_ai | 70.0 -> 80.0 | The washing machine at the top of the room should face 270° (-Y) into the room, away from the wall it currently faces. | ![](agent/r1_142_rotate_piece_before_r_L0_giris_holu_4.png) | ![](agent/r1_144_rotate_piece_after_r_L0_giris_holu_4.png) |
| 463 | 1 | swap_model | f_L0_130 | adjusted_by_ai | 100.0 -> 100.0 | F9: nightstand missing from render; swap to a larger classic nightstand model so it is visible next to the bed | ![](agent/r1_153_swap_model_before_r_L0_ebeveyn_odasi_5.png) | ![](agent/r1_154_swap_model_after_r_L0_ebeveyn_odasi_5.png) |
| 482 | 1 | set_exterior | exterior:roof | agent_override | - | Roof overhang was 0 m (flush with wall face); setting 0.5 m to meet the required 0.3-0.8 m overhang. | - | - |
| 486 | 1 | set_exterior | exterior:site | agent_override | - | Adding a path to the entrance door and a fence to define the plot boundary, addressing the missing access route and untextured uniform ground. | - | - |
| 492 | 1 | set_lighting | r_L0_oda_10 | agent_override | - | Raise room light power x1.48 so the dark hall's incident light reaches the camera target (exposure was +3.06 EV vs the +3.00 EV cap). | - | - |
| 494 | 1 | set_camera | ext_6 | agent_override | - | Moving ext_6 from a frontal view to a 3/4 corner position so two facades are visible. | - | - |
| 496 | 1 | set_lighting | r_L0_oda_7 | agent_override | - | Room too dark for camera (exposure +3.20 EV vs +3.00 cap); finding specifies x1.63 to bring incident light into range. | - | - |
| 497 | 1 | set_camera | ext_7 | agent_override | - | Pulling ext_7 back and re-aiming at the building center so the whole building fits in the frame at 60-80% of frame width. | - | - |
| 847 | 2 | swap_model | f_L0_068 | adjusted_by_ai | 80.0 -> 80.0 | Replace the crude low-poly bed with a refined upholstered saddle-back model to resolve the D2 visual quality findings. | ![](agent/r2_074_swap_model_before_r_L0_ebeveyn_odasi_m_k_a.png) | ![](agent/r2_075_swap_model_after_r_L0_ebeveyn_odasi_m_k_a.png) |
| 877 | 2 | set_lighting | r_L0_banyo_5 | agent_override | - | Both cameras report the room too dark (exposure over +3.00 EV cap); x1.84 is the higher suggested factor covering both views. | - | - |
| 881 | 2 | set_lighting | r_L0_giris_holu_4 | agent_override | - | View cam_r_L0_giris_holu_4_2 is 0.04 stops over the EV cap; finding specifies x1.46 room light factor. | - | - |
| 894 | 2 | swap_model | f_L0_184 | adjusted_by_ai | 87.0 -> 87.0 | Drawn 1.62 m tub cannot fit the ~1.6 m bay (cuts wall w_L0_094 and the door swing); a 1.33 m model fits the bay width. | ![](agent/r2_090_swap_model_before_r_L0_banyo_5.png) | ![](agent/r2_092_swap_model_after_r_L0_banyo_5.png) |
| 899 | 2 | mark_not_furniture | f_L0_149 | adjusted_by_ai | 87.0 -> 87.0 | A 0.85 m square in a 3.5 m2 bathroom is not a plausible fixture (washbasin/shower both rejected); it is a misread symbol/mark, not furniture. | ![](agent/r2_096_mark_not_furniture_before_r_L0_banyo_5.png) | ![](agent/r2_097_mark_not_furniture_after_r_L0_banyo_5.png) |
| 903 | 2 | swap_model | f_L0_075 | adjusted_by_ai | 80.0 -> 80.0 | Smaller width (0.585m vs 0.65m) to reduce wall w_L0_088 collision from 0.142m to within tolerance. | ![](agent/r2_099_swap_model_before_r_L0_giris_holu_4.png) | ![](agent/r2_100_swap_model_after_r_L0_giris_holu_4.png) |
| 924 | 2 | fix_fixture | f_L0_053 | adjusted_by_ai | 87.0 -> 90.0 | Door d_L0_013 swings into the washing machine on one hinge side; nudge it to clear the swing. | ![](agent/r2_116_fix_fixture_before_r_L0_banyo_6.png) | ![](agent/r2_117_fix_fixture_after_r_L0_banyo_6.png) |
| 925 | 2 | swap_model | f_L0_077 | adjusted_by_ai | 80.0 -> 80.0 | Swap to a slightly smaller washing machine model (0.6424 x 0.6081) to reduce the wall cut from 0.136 m to within the 0.030 m tolerance, fixing S2 | ![](agent/r2_118_swap_model_before_r_L0_giris_holu_2.png) | ![](agent/r2_119_swap_model_after_r_L0_giris_holu_2.png) |
| 947 | 2 | mark_not_furniture | f_L0_148 | adjusted_by_ai | 87.0 -> 87.0 | The 0.85x0.80 m drawn piece cannot be validly typed as a shower in this tight bathroom (Round 1 retype rejected: F9 through outline, G10 clearance, G11 walkway), so it is marked as not furniture to clear the untyped finding. | ![](agent/r2_128_mark_not_furniture_before_r_L0_banyo_2.png) | ![](agent/r2_129_mark_not_furniture_after_r_L0_banyo_2.png) |
| 948 | 2 | mark_not_furniture | f_L0_150 | adjusted_by_ai | 87.0 -> 87.0 | The 0.83 x 0.80 m drawn symbol pokes through the room outline and no candidate type (shower, potted_plant) fits inside the room; it is a dimension outline or wall detail, not furniture. | ![](agent/r2_130_mark_not_furniture_before_r_L0_banyo.png) | ![](agent/r2_131_mark_not_furniture_after_r_L0_banyo.png) |
| 951 | 2 | set_exterior | exterior:ground | agent_override | - | Give the site a textured ground surface so the path and front-court paving read against it, addressing the X4 findings that only grass is visible in front of the entrance doors. | - | - |
| 952 | 2 | set_camera | ext_6 | agent_override | - | Reframe ext_6 to a frontal view of the -y facade so the entrance and its path are seen head-on, addressing the X6 no-frontal-view finding. | - | - |
| 953 | 2 | set_camera | ext_7 | agent_override | - | Reframe ext_7 to a frontal view of the -y facade so the entrance and its path are seen head-on, addressing the X4 path finding and the X6 no-frontal-view finding. | - | - |
| 954 | 2 | set_camera | ext_2 | agent_override | - | Reframe ext_2 to a frontal view of the -y facade so the entrance door and its path are seen head-on, addressing the X4 path finding and the X6 no-frontal-view finding. | - | - |
| 1202 | 3 | report_library_gap | f_L0_085 | library_gap | - | No audited library model of type kitchen_counter exists (catalog count 0), so the F9 overlap with stove f_L0_050 cannot be fixed by swap_model; the counter is a module build of the drawn run. | - | - |
| 1301 | 3 | swap_model | f_L0_180 | adjusted_by_ai | 77.0 -> 77.0 | Swap to a 1.94 m shower to clear the window sill (G12: shower 2.00 m blocks window win_L0_057 sill 0.90 m + 0.05) | ![](agent/r3_060_swap_model_before_r_L0_banyo_8.png) | ![](agent/r3_061_swap_model_after_r_L0_banyo_8.png) |
| 1302 | 3 | mark_not_furniture | f_L0_147 | adjusted_by_ai | 87.0 -> 87.0 | The 0.85x0.80 m square symbol is a structural column/wall segment, not furniture; retype to shower already failed clearance checks. | ![](agent/r3_062_mark_not_furniture_before_r_L0_banyo_7.png) | ![](agent/r3_063_mark_not_furniture_after_r_L0_banyo_7.png) |
| 1304 | 3 | set_lighting | r_L0_banyo_7 | agent_override | - | Room is too dark for the camera (wanted +3.50 EV, cap +3.00 EV); the finding names factor x2.01. | - | - |
| 1308 | 3 | mark_not_furniture | f_L0_090 | adjusted_by_ai | 77.0 -> 77.0 | The 1.00 x 0.85 m drawn piece is a dimension outline or annotation, not a real fixture; it overlaps the shower and has no plausible bathroom type | ![](agent/r3_066_mark_not_furniture_before_r_L0_banyo_8.png) | ![](agent/r3_070_mark_not_furniture_after_r_L0_banyo_8.png) |
| 1338 | 3 | mark_not_furniture | f_L0_089 | adjusted_by_ai | 90.0 -> 90.0 | All retype candidates (bathtub, shower, potted_plant) were rejected due to overlap with the washing machine and the room boundary; the symbol is not buildable furniture. | ![](agent/r3_089_mark_not_furniture_before_r_L0_banyo_6.png) | ![](agent/r3_090_mark_not_furniture_after_r_L0_banyo_6.png) |
| 1344 | 3 | set_front | f_L0_195 | adjusted_by_ai | 37.0 -> 67.0 | Washbasin front was inferred at 50.5° facing a wall 0.22 m away; 230.5° (rotation+90°) aligns the front with the actual opening direction, fixing F4. | ![](agent/r3_091_set_front_before_r_L0_banyo_4.png) | ![](agent/r3_093_set_front_after_r_L0_banyo_4.png) |
| 1355 | 3 | swap_model | f_L0_184 | adjusted_by_ai | 87.0 -> 87.0 | Narrower 1.32 m bathtub model fits the 1.6 m room width, resolving the S2 wall cut (0.049 m > 0.030 m tolerance). | ![](agent/r3_100_swap_model_before_r_L0_banyo_5.png) | ![](agent/r3_101_swap_model_after_r_L0_banyo_5.png) |
| 1357 | 3 | set_exterior | exterior:sun | agent_override | - | Raise the sun elevation to 55° so the exterior is not washed out by a low sun and shadows become visible. | - | - |
| 1364 | 3 | set_camera | ext_2 | agent_override | - | Reframe ext_2 as a 3/4 corner view showing the -y facade and the +x end facade at eye level 1.45 m. | - | - |
| 1366 | 3 | set_camera | ext_6 | agent_override | - | Move ext_6 to a 3/4 corner at standard eye level 1.45 m so two facades are visible. | - | - |
| 1367 | 3 | set_camera | ext_7 | agent_override | - | Move ext_7 to a 3/4 corner at standard eye level 1.45 m showing the -y and -x facades. | - | - |
| 1604 | 4 | move_piece | f_L0_141 | adjusted_by_ai | 17.0 -> 24.0 | Snap the headboard of f_L0_141 onto the free wall span s5 (w_L0_121) to fix the headboard-off-wall critical and open the foot clearance. | ![](agent/r4_008_move_piece_before_r_L0_ebeveyn_odasi_4.png) | ![](agent/r4_009_move_piece_after_r_L0_ebeveyn_odasi_4.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 289 | 1 | set_room_type | r_L0_yasama | acceptance: finding F9:f_L0_001 is still there after the edit (kitchen_counter reaches 0.32 m² through the room outline) | Room contains a full drawn kitchen run (counters, sink, stove); acknowledging it as a kitchen resolves the kitchen_counter wrong_type/outline finding. |
| 290 | 1 | set_room_type | r_L0_yasama_4 | acceptance: finding F9:f_L0_010 is still there after the edit (kitchen_counter reaches 0.29 m² through the room outline) | Room contains a full drawn kitchen run (counters, sink, stove) reaching through the outline; type should accept the kitchen fixtures |
| 298 | 1 | move_piece | f_L0_197 | drawn_lock: f_L0_197: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.50 m) | Move coffee table away from the sofa front to clear the 0.26 m² overlap and the 0.00 m G2 clearance |
| 299 | 1 | move_piece | f_L0_198 | drawn_lock: f_L0_198: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.42 m) | Move TV unit further from the sofa front to reach the 1.50 m viewing distance |
| 301 | 1 | move_piece | f_L0_197 | drawn_lock: f_L0_197: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move coffee table 0.3 m away from the sofa front to clear the overlap and G2 clearance |
| 305 | 1 | move_piece | f_L0_198 | score: plausibility -30 -> -50 (F3 f_L0_198: tv_unit: its back is not on a wall (0.29 m off); F9 f_L0_198: tv_unit reaches 0.45 m² through the room outline; G1 f_L0_198: TV unit f_L0_198 1.32 m from the sofa front, needs ≥ 1.50 m) | Move TV unit 0.3 m further from the sofa front toward the 1.50 m viewing distance |
| 307 | 1 | move_piece | f_L0_197 | acceptance: finding F9:f_L0_197 is still there after the edit (table_coffee f_L0_197 overlaps sofa_corner f_L0_196 by 0.06 m²); 1 more kept | Move coffee table 0.25 m away from the sofa front to clear the overlap and G2 clearance |
| 311 | 1 | swap_model | f_L0_024 | acceptance: finding F9:f_L0_024 is still there after the edit (sink_kitchen f_L0_024 overlaps kitchen_counter f_L0_022 by 0.40 m²) | Sink overlaps the counter it sits in; swap to a model that fits the counter footprint. |
| 312 | 1 | move_piece | f_L0_197 | memory: the same edit was rejected in round 1: drawn_lock: f_L0_197: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move coffee table the full 0.3 m allowance away from the sofa front to clear the overlap and G2 clearance |
| 313 | 1 | swap_model | f_L0_063 | acceptance: finding F9:f_L0_063 is still there after the edit (stove f_L0_063 overlaps kitchen_counter f_L0_023 by 0.34 m²) | Stove overlaps the counter it sits in; swap to a model that fits the counter footprint. |
| 314 | 1 | move_piece | f_L0_197 | max_tries: f_L0_197 was edited 3 times in this round | Move coffee table diagonally 0.35 m from the sofa corner to clear the overlap and G2 clearance |
| 316 | 1 | move_piece | f_L0_114 | drawn_lock: f_L0_114: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.12 m) | TV unit blocks two windows; slide it along the wall to a clear span. |
| 317 | 1 | move_piece | f_L0_203 | drawn_lock: f_L0_203: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.42 m) | Floor lamp blocks window win_L0_050; move it to a clear spot. |
| 318 | 1 | move_piece | f_L0_113 | f_L0_209: no_overlap | Chair lacks 0.81 m clearance behind; nudge it away from the wall. |
| 319 | 1 | complete_group | r_L0_yasama_3_kitchen.kitchen_run | unverified: r_L0_yasama_3_kitchen.kitchen_run: the anchor f_L0_022 is unverified (retype_piece first) | Kitchen run is missing a fridge; complete the group to add one. |
| 321 | 1 | relayout_room | r_L0_ebeveyn_odasi_4 | acceptance: finding F3:f_L0_141 is still there after the edit (bed_double: the headboard stands in the room (0.08 m off)); 3 more kept | Re-solve the room with the best solver candidate to push bed f_L0_141 flush to a wall (fixes headboard off-wall and front-facing-wall), open the foot and right-side clearances, restore the 0.60 m walkway from the door, seat nightstand f_L0_218 against a wall, and open the 0.60 m left-side clearance of bed f_L0_070. |
| 323 | 1 | move_piece | f_L0_114 | snap: f_L0_114: no free place on wall w_L0_087 (doors, windows, at most 1.2 m from the drawn place) | TV unit blocks two windows; slide it along the wall to a clear span. |
| 324 | 1 | move_piece | f_L0_203 | f_L0_203: no_overlap, f_L0_209: no_overlap | Floor lamp blocks window win_L0_050; move it 0.3 m to a clear spot. |
| 325 | 1 | move_piece | f_L0_113 | score: plausibility 10 -> -10 (F4 f_L0_113: chair does not face its group (f_L0_111, f_L0_156); G6 f_L0_113: chair f_L0_113 is 54° off the table f_L0_111 (needs ≤ 45°)) | Chair lacks 0.81 m clearance behind; nudge it 0.11 m away from the wall. |
| 326 | 1 | swap_model | f_L0_027 | acceptance: finding F9:f_L0_027 is still there after the edit (sink_kitchen f_L0_027 overlaps kitchen_counter f_L0_025 by 0.40 m²) | Smaller sink model (1.00x0.47 m) to resolve the 0.40 m² overlap with kitchen_counter f_L0_025. |
| 327 | 1 | relayout_room | r_L0_ebeveyn_odasi_4 | acceptance: finding F3:f_L0_141 is still there after the edit (bed_double: the headboard stands in the room (0.08 m off)); 3 more kept | Try the second solver candidate to push bed f_L0_141 flush to a wall, open its foot and right-side clearances, restore the 0.60 m walkway from the door, seat nightstand f_L0_218 against a wall, and open the 0.60 m left-side clearance of bed f_L0_070. |
| 328 | 1 | swap_model | f_L0_064 | acceptance: finding F9:f_L0_064 is still there after the edit (stove f_L0_064 overlaps kitchen_counter f_L0_026 by 0.34 m²) | Smaller stove model (0.50x0.65 m) to resolve the 0.34 m² overlap with kitchen_counter f_L0_026. |
| 331 | 1 | fix_fixture | f_L0_213 | fixture_place: f_L0_213: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_014) | Fridge stands in front of window win_L0_055 (G12); move it up to 0.5 m to clear the window sill obstruction. |
| 333 | 1 | move_piece | f_L0_120 | snap: f_L0_120: no free place on wall w_L0_158 (doors, windows, at most 1.2 m from the drawn place) | Move tv_unit off windows win_L0_028/win_L0_029 onto the free right wall span s1 (2.92 m) to clear both blocked openings. |
| 334 | 1 | move_piece | f_L0_205 | drawn_lock: f_L0_205: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | Shift floor_lamp away from window win_L0_064 to clear the blocked opening. |
| 335 | 1 | fix_fixture | f_L0_213 | fixture_move: f_L0_213: the move is 0.50 m, at most 0.50 m | Fridge stands in front of window win_L0_055 (G12); shift it 0.5 m along the kitchen run to clear the window sill obstruction. |
| 337 | 1 | fix_fixture | f_L0_213 | f_L0_213: no_overlap, score: plausibility 37 -> 17 (F9 f_L0_213: fridge f_L0_213 overlaps kitchen_counter f_L0_087 by 0.30 m²; G8 f_L0_088: work triangle: fridge-sink 0.84 m (legs 1.20-2.70 m, sum ≤ 7.90 m)) | Fridge stands in front of window win_L0_055 (G12); shift it 0.49 m along the kitchen run to clear the window sill obstruction. |
| 339 | 1 | move_piece | f_L0_120 | snap: f_L0_120: no free place on wall w_L0_075 (doors, windows, at most 1.2 m from the drawn place) | Move tv_unit off windows win_L0_028/win_L0_029 onto the free top wall span s3 (2.74 m) to clear both blocked openings. |
| 340 | 1 | move_piece | f_L0_205 | f_L0_205: no_overlap | Shift floor_lamp 0.3 m left, away from window win_L0_064, to clear the blocked opening. |
| 343 | 1 | move_piece | f_L0_205 | drawn_lock: f_L0_205: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift floor_lamp 0.3 m down, away from window win_L0_064, to clear the blocked opening. |
| 344 | 1 | move_piece | f_L0_119 | drawn_lock: f_L0_119: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair 0.3 m away from the wall behind to provide the required 0.81 m clearance. |
| 345 | 1 | move_piece | f_L0_058 | f_L0_058: doors_free, f_L0_058: no_overlap, f_L0_099: no_overlap, score: plausibility 70 -> 7 (F7 f_L0_058: bed_double blocks door o_L0_003; F9 f_L0_099: nightstand f_L0_099 overlaps bed_double f_L0_058 by 0.11 m²; G4 f_L0_058: bed_double f_L0_058: no nightstand on the free left side of the head (0.57 m free); G4 f_L0_099: nightstand f_L0_099 of bed_double f_L0_058: -0.10 m from the bed side (needs ≤ 0.30 m)) | Shift the bed 0.3 m toward the head wall to open the foot clearance to ≥0.60 m and bring the right use zone within a 0.60 m walkway from the door. |
| 346 | 1 | move_piece | f_L0_058 | drawn_lock: f_L0_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the bed 0.3 m toward the foot wall to open the foot clearance to ≥0.60 m and bring the right use zone within a 0.60 m walkway from the door. |
| 347 | 1 | move_piece | f_L0_205 | max_tries: f_L0_205 was edited 3 times in this round | Shift floor_lamp 0.28 m down, away from window win_L0_064, to clear the blocked opening. |
| 349 | 1 | move_piece | f_L0_058 | f_L0_058: no_overlap, f_L0_100: no_overlap, score: plausibility 70 -> 40 (F9 f_L0_100: nightstand f_L0_100 overlaps bed_double f_L0_058 by 0.11 m²; G4 f_L0_100: nightstand f_L0_100 of bed_double f_L0_058: -0.10 m from the bed side (needs ≤ 0.30 m); G5 f_L0_058: bed_double f_L0_058: 0.48 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.29 m toward the foot wall to open the foot clearance to ≥0.60 m and bring the right use zone within a 0.60 m walkway from the door. |
| 352 | 1 | move_piece | f_L0_098 | drawn_lock: f_L0_098: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Slide the wardrobe 0.3 m along its wall to clear ≥0.80 m in front of the doors. |
| 353 | 1 | retype_piece | f_L0_103 | f_L0_103: inside_room, score: plausibility 87 -> 67 (F3 f_L0_103: dresser: its back is not on a wall (0.08 m off); F4 f_L0_103: dresser faces a wall 0.00 m in front of it) | 1.50 x 0.60 m drawn piece matches a dresser; builds the storage element and resolves the untyped finding. |
| 354 | 1 | retype_piece | f_L0_104 | f_L0_104: inside_room, f_L0_104: windows_free, score: plausibility 87 -> 77 (G12 f_L0_104: floor_lamp f_L0_104 (1.60 m) stands in front of window win_L0_058 (sill 0.90 m + 0.05)) | 0.40 x 0.20 m drawn piece matches a floor lamp; builds the lighting element and resolves the untyped finding. |
| 355 | 1 | move_piece | f_L0_098 | acceptance: finding G13:f_L0_098 is still there after the edit (wardrobe f_L0_098: 0.43 m free in front, needs ≥ 0.80 m) | Slide the wardrobe 0.29 m along its wall to clear ≥0.80 m in front of the doors. |
| 357 | 1 | move_piece | f_L0_098 | acceptance: finding G13:f_L0_098 is still there after the edit (wardrobe f_L0_098: 0.42 m free in front, needs ≥ 0.80 m) | Slide the wardrobe 0.28 m along its wall to clear ≥0.80 m in front of the doors. |
| 362 | 1 | complete_group | r_L0_banyo_5.bathroom_set | no_place: r_L0_banyo_5.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom set is missing a washbasin (G10); completing the group places one in a free wall span. |
| 367 | 1 | move_piece | f_L0_144 | drawn_lock: f_L0_144: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move wardrobe 0.3 m away from the wall to increase front clearance from 0.14 m toward the required 0.80 m (G13). |
| 368 | 1 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_134: no_overlap, score: plausibility 80 -> 50 (F3 f_L0_069: bed_double: the headboard stands in the room (0.30 m off); G5 f_L0_069: bed_double f_L0_069: 0.55 m free along the left side, needs ≥ 0.60 m) | Move bed 0.3 m to the right to increase left-side clearance from 0.54 m toward the required 0.60 m (G5). |
| 371 | 1 | retype_piece | f_L0_149 | retype: washbasin is no candidate for f_L0_149 (0.85 x 0.80 m at [6.53, 8.77]): the size table and the room / zone give potted_plant, shower | 0.85x0.80 m drawn piece in a bathroom is a washbasin/vanity; retype resolves the untyped NR finding and supplies the missing washbasin for G10. |
| 374 | 1 | retype_piece | f_L0_149 | f_L0_149: inside_room, score: plausibility 87 -> 44 (F3 f_L0_149: shower: its back is not on a wall (0.06 m off); F4 f_L0_149: shower faces a wall 0.02 m in front of it; F9 f_L0_149: shower reaches 0.12 m² through the room outline; G10 f_L0_149: shower f_L0_149: 0.02 m clear in front, needs ≥ 0.53 m) | 0.85x0.80 m drawn piece in a bathroom matches the size table for a shower; retype resolves the untyped NR finding. |
| 381 | 1 | move_piece | f_L0_143 | drawn_lock: f_L0_143: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift wardrobe 0.3 m toward the wall to open front clearance (G13 needs 0.80 m, has 0.14 m). |
| 382 | 1 | move_piece | f_L0_068 | f_L0_068: no_overlap, f_L0_133: no_overlap, score: plausibility 80 -> 60 (F9 f_L0_133: nightstand f_L0_133 overlaps bed_double f_L0_068 by 0.11 m²; G4 f_L0_133: nightstand f_L0_133 of bed_double f_L0_068: -0.10 m from the bed side (needs ≤ 0.30 m); G5 f_L0_068: bed_double f_L0_068: 0.25 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.3 m toward the wall to open right-side clearance (G5 needs 0.60 m, has 0.54 m). |
| 386 | 1 | set_room_type | r_L0_giris_holu_2 | score: plausibility 70 -> 50 (G10 r_L0_giris_holu_2: bathroom without a shower or a bathtub; G10 r_L0_giris_holu_2: bathroom without a toilet; G10 r_L0_giris_holu_2: bathroom without a washbasin) | Room contains a drawn washing machine and is programmed as a bathroom_set, so it is a utility/bathroom space mislabeled as a hall; this resolves F1, F9 and G14 for f_L0_077. |
| 388 | 1 | complete_group | r_L0_giris_holu_2.bathroom_set | no_place: r_L0_giris_holu_2.bathroom_set (missing toilet, washbasin, shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room) | Complete the bathroom_set with toilet, washbasin, and shower so the room can be re-typed as a bathroom without triggering G10 findings. |
| 392 | 1 | rotate_piece | f_L0_077 | drawn_lock: f_L0_077: the new front does not fix the error (its front faces a wall) | Washing machine faces 0° (East) into a wall; rotating to 180° (West) orients the front into the room space, resolving F4. |
| 393 | 1 | complete_group | r_L0_banyo_6.bathroom_set | no_place: r_L0_banyo_6.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom set is missing its washbasin (G10); complete the group so the program is satisfied. |
| 397 | 1 | fix_fixture | f_L0_077 | fixture_place: f_L0_077: no valid spot within 0.50 m (it stands 0.11 m² outside the room) | Washing machine cuts wall w_L0_152 by 0.150 m; fix_fixture will move it to the nearest valid spot to resolve the S2 collision. |
| 399 | 1 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_134: no_overlap, score: plausibility 80 -> 70 (G4 f_L0_134: nightstand f_L0_134 of bed_double f_L0_069: -0.06 m from the bed side (needs ≤ 0.30 m); G5 f_L0_069: bed_double f_L0_069: 0.58 m free along the right side, needs ≥ 0.60 m) | Move bed 0.06 m up (toward window wall) to increase left-side clearance from 0.54 m to 0.60 m (G5). |
| 408 | 1 | complete_group | r_L0_banyo_8.bathroom_set | no_place: r_L0_banyo_8.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom set is missing its required washbasin member (G10); complete_group will build it into a free span. |
| 409 | 1 | fix_fixture | f_L0_180 | acceptance: finding G12:f_L0_180 is still there after the edit (shower f_L0_180 (2.00 m) stands in front of window win_L0_057 (sill 0.90 m + 0.05)) | Shower cuts wall w_L0_049 by 0.041 m (S2) and stands in front of window win_L0_057 (G12); nudge it to clear the wall and free the window sightline. |
| 411 | 1 | set_room_type | r_L0_giris_holu_2 | memory: the same edit was rejected in round 1: score: plausibility 70 -> 50 (G10 r_L0_giris_holu_2: bathroom without a shower or a bathtub; G10 r_L0_giris_holu_2: bathroom without a toilet; G10 r_L0_giris_holu_2: bathroom without a washbasin) | Room contains a drawn washing machine and is programmed as a bathroom_set, indicating it is a utility/bathroom space mislabeled as a hall; this resolves F1, F9 and G14 for f_L0_077. |
| 413 | 1 | relayout_room | r_L0_giris_holu_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Using the solver's best candidate to re-place the entrance group and potentially resolve the washing machine type/collision findings. |
| 414 | 1 | retype_piece | f_L0_090 | retype: bathtub is no candidate for f_L0_090 (1.00 x 0.85 m at [19.56, 10.18]): the size table and the room / zone give potted_plant, shower | 1.00 x 0.85 m drawn piece in a bathroom matches a bathtub footprint; typing it builds it and clears the untyped review finding. |
| 417 | 1 | fix_fixture | f_L0_077 | memory: the same edit was rejected in round 1: fixture_place: f_L0_077: no valid spot within 0.50 m (it stands 0.11 m² outside the room) | Washing machine reaches 0.12 m² through the room outline; fix_fixture will move it to the nearest valid spot to resolve F9. |
| 418 | 1 | retype_piece | f_L0_090 | f_L0_090: inside_room, score: plausibility 77 -> 67 (F9 f_L0_090: potted_plant reaches 0.15 m² through the room outline) | Size table allows potted_plant for this 1.00 x 0.85 m footprint; a plant is a plausible bathroom accent and clears the untyped review finding. |
| 420 | 1 | retype_piece | f_L0_090 | f_L0_090: inside_room, score: plausibility 77 -> 54 (F3 f_L0_090: shower: its back is not on a wall (0.15 m off); F9 f_L0_090: shower reaches 0.15 m² through the room outline; G10 f_L0_090: shower f_L0_090: 0.26 m clear in front, needs ≥ 0.53 m) | Size table allows shower for this 1.00 x 0.85 m footprint; a second shower stall is plausible in a bathroom and clears the untyped review finding. |
| 424 | 1 | set_room_type | r_L0_giris_holu | score: plausibility 70 -> 50 (G10 r_L0_giris_holu: bathroom without a shower or a bathtub; G10 r_L0_giris_holu: bathroom without a toilet; G10 r_L0_giris_holu: bathroom without a washbasin) | Room contains a drawn washing machine and a bathroom_set group, so it is a bathroom/utility room, not a hall; resolves F1, F9, G14. |
| 425 | 1 | set_room_type | r_L0_giris_holu_4 | score: plausibility 70 -> 50 (G10 r_L0_giris_holu_4: bathroom without a shower or a bathtub; G10 r_L0_giris_holu_4: bathroom without a toilet; G10 r_L0_giris_holu_4: bathroom without a washbasin) | Room contains a drawn washing machine and a bathroom_set group, so it is a bathroom/utility room mislabeled as a hall; this resolves F1, F9 and G14 for f_L0_075. |
| 426 | 1 | mark_not_furniture | f_L0_090 | max_tries: f_L0_090 was edited 3 times in this round | The 1.00 x 0.85 m drawn piece reaches through the room outline and no valid furniture type (potted_plant, shower) fits inside the room; it is a dimension outline or wall marking, not furniture. |
| 427 | 1 | complete_group | r_L0_giris_holu.bathroom_set | no_place: r_L0_giris_holu.bathroom_set (missing toilet, washbasin, shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room) | Add the missing toilet, washbasin and shower so the bathroom_set is complete and the room can be typed as a bathroom. |
| 428 | 1 | set_room_type | r_L0_giris_holu_3 | score: plausibility 70 -> 50 (G10 r_L0_giris_holu_3: bathroom without a shower or a bathtub; G10 r_L0_giris_holu_3: bathroom without a toilet; G10 r_L0_giris_holu_3: bathroom without a washbasin) | Room contains a drawn washing machine and a bathroom_set group, so it is a bathroom/utility room, not a hall; resolves F1, G14 and the type-driven F9. |
| 429 | 1 | complete_group | r_L0_giris_holu_4.bathroom_set | no_place: r_L0_giris_holu_4.bathroom_set (missing toilet, washbasin, shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room) | Add the missing toilet, washbasin and shower so the bathroom_set is complete and the room can be typed as a bathroom. |
| 430 | 1 | fix_fixture | f_L0_082 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Door d_L0_015 swings into the washing machine on one hinge side (R3); nudge it up to 0.5 m to clear the door swing. |
| 432 | 1 | rotate_piece | f_L0_074 | drawn_lock: f_L0_074: the new front does not fix the error (its front faces a wall) | Washing machine faces 180° into the wall; rotate to face 0° into the room to resolve F4. |
| 433 | 1 | rotate_piece | f_L0_075 | drawn_lock: f_L0_075: the new front does not fix the error (its front faces a wall) | The washing machine faces 180° (into the wall); rotating to 0° faces it into the room, resolving F4. |
| 435 | 1 | rotate_piece | f_L0_075 | drawn_lock: f_L0_075: the new front does not fix the error (its front faces a wall) | The washing machine at the top of the room should face 90° (+Y) into the room, away from the wall it currently faces. |
| 438 | 1 | fix_fixture | f_L0_074 | fixture_place: f_L0_074: no valid spot within 0.50 m (it stands 0.12 m² outside the room) | Washing machine cuts wall w_L0_088 by 0.149 m; move it to the nearest valid spot inside the room to resolve S2. |
| 441 | 1 | fix_fixture | f_L0_075 | max_tries: f_L0_075 was edited 3 times in this round | The washing machine cuts wall w_L0_088 by 0.150 m; fix_fixture moves it to the nearest valid spot to resolve the collision. |
| 443 | 1 | fix_fixture | f_L0_074 | max_tries: f_L0_074 was edited 3 times in this round | Move the washing machine slightly into the room interior to clear wall w_L0_088 and the room outline (S2, F9). |
| 444 | 1 | complete_group | r_L0_banyo_7.bathroom_set | no_place: r_L0_banyo_7.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom set is missing its washbasin (G10); build the missing member. |
| 446 | 1 | set_room_type | r_L0_giris_holu_4 | memory: the same edit was rejected in round 1: score: plausibility 70 -> 50 (G10 r_L0_giris_holu_4: bathroom without a shower or a bathtub; G10 r_L0_giris_holu_4: bathroom without a toilet; G10 r_L0_giris_holu_4: bathroom without a washbasin) | The room contains a drawn washing machine and a bathroom_set group, indicating it is a bathroom/utility room mislabeled as a hall; this resolves F1, F9 and G14 for f_L0_075. |
| 448 | 1 | fix_fixture | f_L0_074 | max_tries: f_L0_074 was edited 3 times in this round | Nudge the washing machine into the room interior to clear wall w_L0_088 (S2) and the room outline (F9). |
| 465 | 1 | complete_group | r_L0_banyo.bathroom_set | no_place: r_L0_banyo.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom set is missing its washbasin (G10); complete the group so the program is satisfied. |
| 469 | 1 | fix_fixture | f_L0_186 | fixture_place: f_L0_186 at [5.97, 3.90] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Bathtub's left edge stands through wall w_L0_094 and its corner sits in the door swing; nudge 0.13 m right to clear both. |
| 471 | 1 | fix_fixture | f_L0_186 | fixture_place: f_L0_186: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_005) | Bathtub stands through wall w_L0_094 and in the door swing; let the code find the nearest valid spot. |
| 472 | 1 | complete_group | r_L0_banyo_2.bathroom_set | no_place: r_L0_banyo_2.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom set is missing its required washbasin member (G10); complete_group builds it around the drawn anchor. |
| 474 | 1 | fix_fixture | f_L0_186 | fixture_size: f_L0_186: the drawn 1.62 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Drawn bathtub 1.62 m is wider than the 1.6 m room; a real 1.50 m tub fits the room and clears the door swing. |
| 476 | 1 | fix_fixture | f_L0_186 | max_tries: f_L0_186 was edited 3 times in this round | Nudge the bathtub 0.18 m right and 0.18 m up so its left edge clears wall w_L0_094 and its corner clears the door swing. |
| 479 | 1 | fix_fixture | f_L0_186 | max_tries: f_L0_186 was edited 3 times in this round | Nudge the bathtub 0.18 m right and 0.18 m up so its left edge clears wall w_L0_094 and its corner clears the door swing. |
| 484 | 1 | retype_piece | f_L0_148 | f_L0_148: inside_room, score: plausibility 87 -> 47 (F9 f_L0_148: shower reaches 0.12 m² through the room outline; G10 f_L0_148: shower f_L0_148: 0.06 m clear in front, needs ≥ 0.53 m; G10 f_L0_187: bathtub f_L0_187: 0.06 m clear in front, needs ≥ 0.53 m; G11 f_L0_148: shower f_L0_148: its front use zone is not reached by a 0.60 m walkway from door d_L0_011) | 0.85 x 0.80 m untyped drawn piece in a bathroom strongly suggests a shower stall; retyping resolves the untyped finding. |
| 485 | 1 | fix_fixture | f_L0_187 | fixture_place: f_L0_187: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_011) | Bathtub f_L0_187 is partially in the door swing of d_L0_011; fix_fixture moves it up to 0.5 m to clear the swing. |
| 491 | 1 | set_camera | ext_6 | set: kind is required | Moving ext_6 from a frontal view to a 3/4 corner position so two facades are visible. |
| 785 | 2 | fix_fixture | f_L0_010 | fixture_place: f_L0_010: no valid spot within 0.50 m (it stands 0.29 m² outside the room) | Nudge the kitchen counter back from the wall to stop it cutting the outline and to open the 0.9m aisle. |
| 787 | 2 | fix_fixture | f_L0_001 | fixture_place: f_L0_001: no valid spot within 0.50 m (it stands 0.32 m² outside the room) | Kitchen counter cuts wall w_L0_098 by 0.200 m and reaches 0.32 m² through the room outline; move it to the nearest valid spot inside the room. |
| 798 | 2 | swap_model | f_L0_021 | acceptance: finding F9:f_L0_021 is still there after the edit (sink_kitchen f_L0_021 overlaps kitchen_counter f_L0_019 by 0.40 m²) | Smaller modern sink (1.00x0.47) to clear the 0.40 m² overlap with kitchen_counter f_L0_019 (F9). |
| 799 | 2 | move_piece | f_L0_141 | snap: f_L0_141: no free place on wall w_L0_122 (doors, windows, at most 1.2 m from the drawn place) | Push bed f_L0_141 flush against the right wall (w_L0_122) to fix the headboard off-wall (F3), the front-facing-wall (F4), and open the foot and right-side clearances (G5). |
| 800 | 2 | swap_model | f_L0_062 | acceptance: finding F9:f_L0_062 is still there after the edit (stove f_L0_062 overlaps kitchen_counter f_L0_020 by 0.34 m²) | Smaller CC0 electric stove (0.50x0.65) to clear the 0.34 m² overlap with kitchen_counter f_L0_020 (F9). |
| 802 | 2 | move_piece | f_L0_141 | drawn_lock: f_L0_141: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.47 m) | Push bed f_L0_141 flush against the right wall (w_L0_122) to fix the headboard off-wall (F3), the front-facing-wall (F4), and open the foot and right-side clearances (G5). |
| 805 | 2 | complete_group | r_L0_yasama_6_kitchen.kitchen_run | unverified: r_L0_yasama_6_kitchen.kitchen_run: the anchor f_L0_025 is unverified (retype_piece first) | Kitchen group is missing its required fridge member (G9). |
| 806 | 2 | move_piece | f_L0_141 | f_L0_141: doors_free, f_L0_141: inside_room, score: plausibility 17 -> 4 (F3 f_L0_141: bed_double: the headboard stands in the room (0.36 m off); F4 f_L0_141: bed_double faces a wall 0.00 m in front of it; F9 f_L0_141: bed_double reaches 0.29 m² through the room outline; R3 d_L0_023: door d_L0_023 swings into f_L0_141 on one hinge side; the other hinge side is free) | Push bed f_L0_141 flush against the right wall (w_L0_122) to fix the headboard off-wall (F3), the front-facing-wall (F4), and open the foot and right-side clearances (G5). |
| 808 | 2 | move_piece | f_L0_108 | drawn_lock: f_L0_108: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.59 m) | Shift tv_unit 0.59 m south so its 1.30 m front clears both windows win_L0_011 and win_L0_012 (G12 x2). |
| 809 | 2 | move_piece | f_L0_141 | max_tries: f_L0_141 was edited 3 times in this round | Push bed f_L0_141 flush against the right wall (w_L0_122) to fix the headboard off-wall (F3), the front-facing-wall (F4), and open the foot and right-side clearances (G5). |
| 811 | 2 | move_piece | f_L0_201 | drawn_lock: f_L0_201: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.42 m) | Shift floor_lamp 0.42 m south so its 1.60 m height clears window win_L0_051 (G12). |
| 812 | 2 | move_piece | f_L0_107 | f_L0_208: no_overlap | Shift chair 0.29 m north to give 0.81 m clearance behind it (G6). |
| 813 | 2 | complete_group | r_L0_yasama_5_kitchen.kitchen_run | unverified: r_L0_yasama_5_kitchen.kitchen_run: the anchor f_L0_019 is unverified (retype_piece first) | Add the missing fridge to complete the kitchen run (G9). |
| 814 | 2 | move_piece | f_L0_070 | f_L0_070: clearance_ok, score: plausibility 17 -> -33 (F3 f_L0_070: bed_double: the headboard stands in the room (0.08 m off); G5 f_L0_070: bed_double f_L0_070: 0.39 m free at the foot, needs ≥ 0.60 m; G11 f_L0_070: bed_double f_L0_070: its left use zone is not reached by a 0.60 m walkway from door d_L0_023) | Shift bed f_L0_070 slightly to the right to open the 0.60 m clearance along the left side (G5). |
| 815 | 2 | move_piece | f_L0_120 | drawn_lock: f_L0_120: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.59 m) | Shift the tv_unit 0.59 m south along the windowed wall so it no longer stands in front of windows win_L0_028 and win_L0_029 (G12). |
| 816 | 2 | move_piece | f_L0_205 | memory: the same edit was rejected in round 1: drawn_lock: f_L0_205: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the floor_lamp 0.3 m south off window win_L0_064 (G12), staying within the drawn move allowance. |
| 817 | 2 | move_piece | f_L0_119 | score: plausibility 10 -> -10 (F4 f_L0_119: chair does not face its group (f_L0_117, f_L0_151); G6 f_L0_119: chair f_L0_119 is 47° off the table f_L0_117 (needs ≤ 45°)) | Nudge the chair 0.05 m away from the wall behind it to gain the 0.81 m clearance required by G6. |
| 818 | 2 | move_piece | f_L0_070 | f_L0_070: no_overlap, f_L0_136: no_overlap, score: plausibility 17 -> -6 (F9 f_L0_136: nightstand f_L0_136 overlaps bed_double f_L0_070 by 0.11 m²; G4 f_L0_070: bed_double f_L0_070: no nightstand on the free right side of the head (1.30 m free); G4 f_L0_136: nightstand f_L0_136 of bed_double f_L0_070: -0.10 m from the bed side (needs ≤ 0.30 m); G5 f_L0_070: bed_double f_L0_070: 0.56 m free along the left side, needs ≥ 0.60 m) | Shift bed f_L0_070 slightly to the right to open the 0.60 m clearance along the left side (G5). |
| 821 | 2 | move_piece | f_L0_070 | drawn_lock: f_L0_070: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift bed f_L0_070 slightly to the right to open the 0.60 m clearance along the left side (G5). |
| 822 | 2 | move_piece | f_L0_070 | memory: the same edit was rejected in round 2: f_L0_070: no_overlap; f_L0_136: no_overlap; score: plausibility 17 -> -6 (F9 f_L0_136: nightstand f_L0_136 overlaps bed_double f_L0_070 by 0.11 m²; G4 f_L0_070: bed_double f_L0_070: no nightstand on the free right side of the head (1.30 m free); G4 f_L0_136: nightstand f_L0_136 of bed_double f_L0_07 | Shift bed f_L0_070 slightly to the right to open the 0.60 m clearance along the left side (G5). |
| 823 | 2 | move_piece | f_L0_120 | acceptance: finding G12:f_L0_120 is still there after the edit (tv_unit f_L0_120 (1.30 m) stands in front of window win_L0_029 (sill 0.90 m + 0.05)) | Shift the tv_unit 0.29 m south along the windowed wall, the maximum drawn allowance, to clear windows win_L0_028 and win_L0_029 (G12). |
| 824 | 2 | move_piece | f_L0_108 | acceptance: finding G12:f_L0_108 is still there after the edit (tv_unit f_L0_108 (1.30 m) stands in front of window win_L0_012 (sill 0.90 m + 0.05)) | Snap tv_unit back to wall w_L0_087 (1.2 m allowance) so its 1.30 m front clears windows win_L0_011 and win_L0_012 (G12 x2). |
| 825 | 2 | move_piece | f_L0_205 | f_L0_205: no_overlap, score: plausibility 10 -> 0 (F9 f_L0_205: floor_lamp f_L0_205 overlaps table_dining f_L0_117 by 0.08 m²) | Shift the floor_lamp 0.28 m south, just inside the drawn allowance, off window win_L0_064 (G12). |
| 826 | 2 | move_piece | f_L0_070 | max_tries: f_L0_070 was edited 3 times in this round | Shift bed f_L0_070 slightly to the right to open the 0.60 m clearance along the left side (G5). |
| 827 | 2 | move_piece | f_L0_119 | score: plausibility 10 -> -10 (F4 f_L0_119: chair does not face its group (f_L0_117, f_L0_151); G6 f_L0_119: chair f_L0_119 is 48° off the table f_L0_117 (needs ≤ 45°)) | Nudge the chair 0.04 m away from the wall behind it to gain the 0.81 m clearance required by G6 while keeping it facing the table. |
| 829 | 2 | move_piece | f_L0_119 | score: plausibility 10 -> -10 (F4 f_L0_119: chair does not face its group (f_L0_117, f_L0_151); G6 f_L0_119: chair f_L0_119 is 45° off the table f_L0_117 (needs ≤ 45°)) | Nudge the chair 0.03 m away from the wall behind it to gain the 0.81 m clearance required by G6 while keeping it facing the table. |
| 852 | 2 | move_piece | f_L0_143 | acceptance: finding G13:f_L0_143 is still there after the edit (wardrobe f_L0_143: 0.04 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.29 m toward the wall to open front clearance (G13 needs 0.80 m). |
| 853 | 2 | place_group | r_L0_oda_01 | no_place: sleeping_single group re-solved around the drawn bed_single f_L0_073: the solver places nothing and leaves the drawn pieces as drawn (sleeping_single: no candidate position fits the room) | Re-solve the drawn sleeping_single group around the bed anchor to build the missing nightstand (G4). |
| 855 | 2 | move_piece | f_L0_073 | f_L0_073: clearance_ok | Shift the bed 0.3 m away from the left wall to raise the side clearance from 0.47 m to the required 0.60 m (G5). |
| 857 | 2 | move_piece | f_L0_068 | acceptance: finding G5:f_L0_068 is still there after the edit (bed_double f_L0_068: 0.45 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.10 m toward the window wall to open the right-side clearance to 0.64 m (G5 needs 0.60 m). |
| 876 | 2 | fix_fixture | f_L0_184 | fixture_place: f_L0_184: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_002) | Bathtub cuts wall w_L0_094 by 0.049 m (tolerance 0.030 m); move to nearest valid spot to clear the wall. |
| 882 | 2 | fix_fixture | f_L0_075 | fixture_place: f_L0_075: no valid spot within 0.50 m (it stands 0.12 m² outside the room) | Washing machine cuts wall w_L0_088 by 0.142 m; move it to the nearest valid spot to clear the wall. |
| 889 | 2 | fix_fixture | f_L0_184 | fixture_place: f_L0_184 at [6.02, 9.63] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shift bathtub right 0.05 m so its left edge clears wall w_L0_094 (was cutting by 0.049 m, tolerance 0.030 m). |
| 896 | 2 | retype_piece | f_L0_147 | f_L0_147: inside_room, score: plausibility 87 -> 44 (F3 f_L0_147: shower: its back is not on a wall (0.06 m off); F4 f_L0_147: shower faces a wall 0.02 m in front of it; F9 f_L0_147: shower reaches 0.12 m² through the room outline; G10 f_L0_147: shower f_L0_147: 0.02 m clear in front, needs ≥ 0.53 m) | 0.85x0.80m untyped drawn piece in a bathroom is a shower stall; typing it resolves the NR finding and gives the bathroom_set its shower member. |
| 906 | 2 | fix_fixture | f_L0_076 | fixture_place: f_L0_076: no valid spot within 0.50 m (it stands 0.12 m² outside the room) | Washing machine cuts wall w_L0_152 by 0.153 m; move it slightly into the room to clear the wall boundary. |
| 909 | 2 | fix_fixture | f_L0_076 | fixture_place: f_L0_076 at [29.62, 9.70] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washing machine cuts wall w_L0_152 by 0.153 m and stands 0.12 m² outside the room; move it 0.15 m into the room to clear the wall boundary. |
| 910 | 2 | fix_fixture | f_L0_074 | memory: the same edit was rejected in round 1: fixture_place: f_L0_074: no valid spot within 0.50 m (it stands 0.12 m² outside the room) | Washing machine cuts wall w_L0_088 by 0.149 m and reaches 0.12 m² outside the room outline; nudge it to the nearest valid spot inside the room. |
| 911 | 2 | fix_fixture | f_L0_076 | fixture_place: f_L0_076 at [29.55, 9.70] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washing machine cuts wall w_L0_152 by 0.153 m and stands 0.12 m² outside the room; move it 0.15 m into the room (left of the wall) to clear the wall boundary. |
| 912 | 2 | fix_fixture | f_L0_074 | fixture_place: f_L0_074 at [3.62, 3.55] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washing machine cuts wall w_L0_088 by 0.149 m and reaches 0.12 m² outside the room outline; nudge it 0.03 m east so its footprint sits fully inside the room. |
| 913 | 2 | fix_fixture | f_L0_076 | max_tries: f_L0_076 was edited 3 times in this round | Washing machine cuts wall w_L0_152 by 0.153 m and stands 0.12 m² outside the room; move it 0.07 m left (into the room, away from the wall) to clear the wall boundary. |
| 914 | 2 | fix_fixture | f_L0_074 | fixture_place: f_L0_074 at [3.62, 3.58] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washing machine cuts wall w_L0_088 by 0.149 m and reaches 0.12 m² outside the room outline; nudge it 0.03 m east and 0.03 m north so its footprint sits fully inside the room. |
| 917 | 2 | fix_fixture | f_L0_074 | fixture_place: f_L0_074 at [3.62, 3.62] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washing machine cuts wall w_L0_088 by 0.149 m and reaches 0.12 m² outside the room outline; nudge it 0.03 m east and 0.07 m north so its footprint sits fully inside the room. |
| 918 | 2 | fix_fixture | f_L0_074 | max_tries: f_L0_074 was edited 3 times in this round | Washing machine cuts wall w_L0_088 by 0.149 m and reaches 0.12 m² outside the room outline; nudge it 0.03 m east and 0.10 m north so its footprint sits fully inside the room. |
| 923 | 2 | retype_piece | f_L0_089 | retype: bathtub is no candidate for f_L0_089 (1.00 x 0.85 m at [13.65, 10.18]): the size table and the room / zone give potted_plant, shower | Untyped drawn piece 1.00 x 0.85 m in a bathroom matches a bathtub footprint; retype resolves the NR finding. |
| 926 | 2 | retype_piece | f_L0_089 | f_L0_053: no_overlap, f_L0_089: inside_room, f_L0_089: no_overlap, score: plausibility 90 -> 57 (F3 f_L0_089: shower: its back is not on a wall (0.15 m off); F9 f_L0_089: shower f_L0_089 overlaps washing_machine f_L0_053 by 0.28 m²; F9 f_L0_089: shower reaches 0.15 m² through the room outline; G10 f_L0_089: shower f_L0_089: 0.26 m clear in front, needs ≥ 0.53 m) | Untyped drawn piece 1.00 x 0.85 m in a bathroom; the size table and zone allow shower, so retype as shower to resolve the NR finding. |
| 930 | 2 | retype_piece | f_L0_150 | f_L0_150: inside_room, score: plausibility 87 -> 47 (F9 f_L0_150: shower reaches 0.11 m² through the room outline; G10 f_L0_150: shower f_L0_150: 0.06 m clear in front, needs ≥ 0.53 m; G10 f_L0_186: bathtub f_L0_186: 0.06 m clear in front, needs ≥ 0.53 m; G11 f_L0_150: shower f_L0_150: its front use zone is not reached by a 0.60 m walkway from door d_L0_005) | 0.83 x 0.80 m square drawn piece in a bathroom is a shower stall; retype builds it and clears the NR finding. |
| 934 | 2 | retype_piece | f_L0_089 | f_L0_053: no_overlap, f_L0_089: inside_room, f_L0_089: no_overlap, score: plausibility 90 -> 70 (F9 f_L0_089: potted_plant f_L0_089 overlaps washing_machine f_L0_053 by 0.28 m²; F9 f_L0_089: potted_plant reaches 0.15 m² through the room outline) | Untyped drawn piece 1.00 x 0.85 m; the size table and zone allow potted_plant, so retype to resolve the NR finding. |
| 939 | 2 | mark_not_furniture | f_L0_089 | max_tries: f_L0_089 was edited 3 times in this round | The 1.00 x 0.85 m drawn piece overlaps the washing machine and extends outside the room boundary; it is a dimension outline or drawing artifact, not furniture. |
| 950 | 2 | set_exterior | exterior:site | no_change: the exterior already has these values ({"site": {"fence": "fence", "front_court": "yes", "path": true}}): nothing to change | Reinforce the site: a visible path and front-court paving to the entrance doors, plus a fence marking the plot boundary, to clear the X4 path findings on ext_1, ext_2, ext_6 and ext_7. |
| 1214 | 3 | complete_group | r_L0_yasama_4_kitchen.kitchen_run | unverified: r_L0_yasama_4_kitchen.kitchen_run: the anchor f_L0_010 is unverified (retype_piece first) | Kitchen run is missing its required fridge member (G9). |
| 1215 | 3 | move_piece | f_L0_197 | acceptance: finding F9:f_L0_197 is still there after the edit (table_coffee f_L0_197 overlaps sofa_corner f_L0_196 by 0.26 m²) | Move coffee table 0.30 m from the sofa front to clear the overlap and meet the 0.30 m clearance. |
| 1216 | 3 | move_piece | f_L0_198 | acceptance: finding G1:f_L0_198 is still there after the edit (TV unit f_L0_198 1.02 m from the sofa front, needs ≥ 1.50 m) | Nudge TV unit 0.22 m further from the sofa front toward the 1.50 m viewing distance. |
| 1217 | 3 | move_piece | f_L0_017 | drawn_lock: f_L0_017: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair 0.30 m from the table edge to open the 0.81 m clearance behind it. |
| 1218 | 3 | move_piece | f_L0_018 | drawn_lock: f_L0_018: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair 0.30 m from the table edge to open the 0.81 m clearance behind it. |
| 1230 | 3 | swap_model | f_L0_005 | acceptance: finding F9:f_L0_005 is still there after the edit (sink_kitchen f_L0_005 overlaps kitchen_counter f_L0_002 by 0.40 m²) | swap sink to a 1.00x0.47 model that fits within the counter footprint to resolve the 0.40 m² overlap with f_L0_002 |
| 1250 | 3 | move_piece | f_L0_108 | acceptance: finding G12:f_L0_108 is still there after the edit (tv_unit f_L0_108 (1.30 m) stands in front of window win_L0_012 (sill 0.90 m + 0.05)) | move tv_unit down along wall w_L0_087 to clear both win_L0_011 and win_L0_012 (G12) |
| 1262 | 3 | move_piece | f_L0_058 | f_L0_058: no_overlap, f_L0_100: no_overlap, score: plausibility 70 -> 40 (F9 f_L0_100: nightstand f_L0_100 overlaps bed_double f_L0_058 by 0.10 m²; G4 f_L0_100: nightstand f_L0_100 of bed_double f_L0_058: -0.14 m from the bed side (needs ≤ 0.30 m); G5 f_L0_058: bed_double f_L0_058: 0.53 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.25 m toward the head wall to open foot clearance to 0.68 m (≥0.60 m) and bring the right use zone within a 0.60 m walkway from the door. |
| 1264 | 3 | move_piece | f_L0_098 | f_L0_098: windows_free, score: plausibility 70 -> 40 (F3 f_L0_098: wardrobe: its back is not on a wall (0.07 m off); G5 f_L0_058: bed_double f_L0_058: 0.18 m free at the foot, needs ≥ 0.60 m; G11 f_L0_098: wardrobe f_L0_098: its front use zone is not reached by a 0.60 m walkway from door o_L0_003; G12 f_L0_098: wardrobe f_L0_098 (2.10 m) stands in front of window win_L0_033 (sill 0.90 m + 0.05)) | Slide the wardrobe 0.25 m along the wall to clear 0.83 m in front of the doors (≥0.80 m). |
| 1266 | 3 | fix_fixture | f_L0_054 | acceptance: finding G10:f_L0_054 is still there after the edit (shower f_L0_054: 0.01 m clear in front, needs ≥ 0.53 m) | Shower cuts wall w_L0_111 by 0.047 m and has only 0.01 m clear in front; nudge it off the wall into the room. |
| 1268 | 3 | fix_fixture | f_L0_054 | fixture_size: f_L0_054: the drawn 1.07 x 0.80 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Shower drawn 1.07 m wide cuts wall w_L0_111 by 0.047 m; a real 1.0 m shower tray fits the 1.05 m bay and clears the wall. |
| 1271 | 3 | fix_fixture | f_L0_054 | fixture_place: f_L0_054 at [12.77, 4.05] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shower cuts wall w_L0_111 by 0.047 m; nudge 0.08 m into the room so it clears the wall (within the 0.5 m allowance). |
| 1272 | 3 | fix_fixture | f_L0_054 | max_tries: f_L0_054 was edited 3 times in this round | Shower cuts wall w_L0_111 by 0.047 m; nudge 0.13 m into the room so it clears the wall (within the 0.5 m allowance). |
| 1274 | 3 | fix_fixture | f_L0_056 | fixture_place: f_L0_056 at [11.91, 3.90] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Toilet centre is 0.37 m from the side wall/fixture on its left, needs 0.38 m; nudge it 0.05 m right to clear the spacing. |
| 1275 | 3 | move_piece | f_L0_108 | snap: f_L0_108: no free place on wall w_L0_074 (doors, windows, at most 1.2 m from the drawn place) | move tv_unit to top wall w_L0_074 clear span to clear win_L0_011 and win_L0_012 (G12) |
| 1276 | 3 | fix_fixture | f_L0_056 | f_L0_056: inside_room | Toilet centre is 0.37 m from the side wall/fixture on its left, needs 0.38 m; let the code find the nearest valid spot that clears the spacing. |
| 1281 | 3 | fix_fixture | f_L0_188 | fixture_place: f_L0_188 at [11.97, 5.44] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washbasin cuts wall w_L0_037 by 0.073 m and faces a wall 0.00 m in front; nudge it 0.15 m into the room to clear the wall and open its front. |
| 1283 | 3 | fix_fixture | f_L0_188 | fixture_place: f_L0_188: no valid spot within 0.50 m (it stands 0.05 m² outside the room, in door d_L0_017) | Washbasin cuts wall w_L0_037 by 0.073 m and faces a wall 0.00 m in front; let the code find the nearest valid spot that clears the wall and opens its front. |
| 1284 | 3 | fix_fixture | f_L0_188 | fixture_place: f_L0_188 at [12.00, 5.45] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Washbasin stands 0.05 m² outside the room outline and in door d_L0_017; nudge it 0.15 m into the room to clear the outline and the door swing. |
| 1303 | 3 | fix_fixture | f_L0_185 | fixture_place: f_L0_185: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_008) | Bathtub cuts wall w_L0_146 by 0.038 m (tolerance 0.030 m); nudge it to the nearest valid spot to clear the wall. |
| 1309 | 3 | fix_fixture | f_L0_185 | fixture_place: f_L0_185 at [27.20, 9.67] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Nudge the bathtub 0.04 m up and 0.04 m left so its corner clears wall w_L0_146 (S2 cut 0.038 m) and the door d_L0_008 swing. |
| 1310 | 3 | fix_fixture | f_L0_185 | fixture_place: f_L0_185 at [27.18, 9.70] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Nudge the bathtub 0.06 m left and 0.07 m up so its corner clears wall w_L0_146 and the door d_L0_008 swing. |
| 1312 | 3 | fix_fixture | f_L0_185 | max_tries: f_L0_185 was edited 3 times in this round | Nudge the bathtub 0.09 m left and 0.09 m up so its corner clears wall w_L0_146 and the door d_L0_008 swing. |
| 1313 | 3 | move_piece | f_L0_201 | drawn_lock: f_L0_201: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.22 m) | move floor_lamp north and slightly west to clear win_L0_051 (G12) while avoiding the sofa |
| 1325 | 3 | move_piece | f_L0_201 | snap: f_L0_201: no free place on wall w_L0_082 (doors, windows, at most 1.2 m from the drawn place) | snap floor_lamp to left wall w_L0_082 just north of win_L0_051 to clear the window (G12) |
| 1328 | 3 | fix_fixture | f_L0_075 | fixture_place: f_L0_075 at [3.59, 9.75] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shift the washing machine 0.10 m into the room so its footprint no longer cuts wall w_L0_088 (S2) or reaches 0.12 m² through the room outline (F9). |
| 1330 | 3 | fix_fixture | f_L0_075 | fixture_place: f_L0_075 at [3.59, 9.70] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shift the washing machine 0.15 m into the room so its footprint no longer cuts wall w_L0_088 (S2) or reaches 0.12 m² through the room outline (F9). |
| 1332 | 3 | fix_fixture | f_L0_075 | fixture_place: f_L0_075 at [3.59, 9.60] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shift the washing machine 0.25 m into the room so its footprint no longer cuts wall w_L0_088 (S2) or reaches 0.12 m² through the room outline (F9). |
| 1333 | 3 | complete_group | r_L0_yasama_5_kitchen.kitchen_run | memory: the same edit was rejected in round 2: unverified: r_L0_yasama_5_kitchen.kitchen_run: the anchor f_L0_019 is unverified (retype_piece first) | add missing fridge to complete the kitchen_run group (G9) |
| 1336 | 3 | fix_fixture | f_L0_075 | max_tries: f_L0_075 was edited 3 times in this round | Shift the washing machine 0.35 m into the room so its footprint no longer cuts wall w_L0_088 (S2) or reaches 0.12 m² through the room outline (F9). |
| 1343 | 3 | complete_group | r_L0_banyo.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Add the missing washbasin to resolve G10 (bathroom without a washbasin). |
| 1345 | 3 | fix_fixture | f_L0_145 | fixture_place: f_L0_145: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_022) | Shower cuts wall w_L0_121 by 0.049 m (tolerance 0.030 m); nudge it to clear the wall and the door swing path. |
| 1346 | 3 | complete_group | r_L0_banyo_5.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo_5.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Add the missing washbasin to resolve G10 (bathroom without a washbasin). |
| 1347 | 3 | fix_fixture | f_L0_184 | memory: the same edit was rejected in round 2: fixture_place: f_L0_184: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_002) | Bathtub cuts wall w_L0_094 by 0.049 m (tolerance 0.030 m); let the code find the nearest valid spot within 0.5 m. |
| 1348 | 3 | fix_fixture | f_L0_145 | fixture_place: f_L0_145 at [19.52, 4.70] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shower cuts wall w_L0_121 by 0.049 m and sits in door d_L0_022's swing; nudge 0.1 m into the room to clear both. |
| 1350 | 3 | fix_fixture | f_L0_145 | fixture_place: f_L0_145 at [19.52, 4.80] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Shower cuts wall w_L0_121 by 0.049 m and sits in door d_L0_022's swing; nudge 0.2 m into the room to clear both. |
| 1353 | 3 | fix_fixture | f_L0_145 | max_tries: f_L0_145 was edited 3 times in this round | Shower cuts wall w_L0_121 by 0.049 m and sits in door d_L0_022's swing; nudge 0.08 m right into the room to clear both. |
| 1358 | 3 | set_camera | ext_2 | eye height 1.75 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 3.00 m) | Reframe ext_2 as a 3/4 corner view showing the -y facade and the +x end facade at eye level. |
| 1359 | 3 | set_camera | ext_6 | eye height 1.75 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 3.00 m) | Move ext_6 to a 3/4 corner at standard eye level 1.6 m so two facades are visible. |
| 1360 | 3 | set_camera | ext_7 | eye height 1.75 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 3.00 m) | Move ext_7 to a 3/4 corner at standard eye level 1.6 m showing the -y and -x facades. |
| 1361 | 3 | fix_fixture | f_L0_187 | memory: the same edit was rejected in round 1: fixture_place: f_L0_187: no valid spot within 0.50 m (it stands 0.04 m² outside the room, in door d_L0_011) | Bathtub stands 0.04 m² outside the room and in door d_L0_011's swing; nudge it fully inside the room to clear the door swing (R3) and free the wall for the washbasin (G10). |
| 1362 | 3 | fix_fixture | f_L0_187 | fixture_place: f_L0_187 at [27.20, 3.77] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Bathtub stands 0.04 m² outside the room and in door d_L0_011's swing; nudge it 0.04 m left so its right edge sits on the wall, clearing the door swing (R3) and freeing the right wall for the washbasin (G10). |
| 1363 | 3 | fix_fixture | f_L0_187 | fixture_place: f_L0_187 at [27.20, 3.70] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Bathtub stands 0.04 m² outside the room and in door d_L0_011's swing; nudge it left and down so its right edge sits on the wall and its top edge clears the door swing (R3), freeing the right wall for the washbasin (G10). |
| 1365 | 3 | fix_fixture | f_L0_187 | fixture_place: f_L0_187 at [27.20, 3.60] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Bathtub stands 0.04 m² outside the room and in door d_L0_011's swing; nudge it left and down so its right edge sits on the wall and its top edge clears the door swing (R3), freeing the right wall for the washbasin (G10). |
| 1368 | 3 | fix_fixture | f_L0_187 | max_tries: f_L0_187 was edited 3 times in this round | Bathtub stands 0.04 m² outside the room and in door d_L0_011's swing; nudge it left and down so its right edge sits on the wall and its top edge clears the door swing (R3), freeing the right wall for the washbasin (G10). |
| 1369 | 3 | complete_group | r_L0_banyo_2.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo_2.bathroom_set (missing washbasin): no place passes the checks (bathroom_set: no candidate position fits the room) | Add the missing washbasin to complete the bathroom set (G10: bathroom without a washbasin). |
| 1370 | 3 | fix_fixture | f_L0_187 | max_tries: f_L0_187 was edited 3 times in this round | Bathtub stands 0.04 m² outside the room and in door d_L0_011's swing; nudge it left and down so its right edge sits on the wall and its top edge clears the door swing (R3), freeing the right wall for the washbasin (G10). |
| 1605 | 4 | move_piece | f_L0_141 | acceptance: finding G11:f_L0_141 is still there after the edit (bed_double f_L0_141: its left use zone is not reached by a 0.60 m walkway from door d_L0_023) | Slide f_L0_141 along the same wall so its headboard sits at the wall's end, opening the 0.60 m foot clearance and the walkway to the door. |
| 1606 | 4 | move_piece | f_L0_141 | acceptance: finding G11:f_L0_141 is still there after the edit (bed_double f_L0_141: its left use zone is not reached by a 0.60 m walkway from door d_L0_023) | Slide f_L0_141 along the wall toward the door side so the 0.60 m walkway from d_L0_023 reaches its use zones. |
| 1607 | 4 | move_piece | f_L0_141 | max_tries: f_L0_141 was edited 3 times in this round | Slide f_L0_141 along the wall to the middle so the 0.60 m walkway from d_L0_023 reaches its foot and side use zones. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| S2 | major | f_L0_007 | r_L0_yasama | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L0_071 | r_L0_ebeveyn_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L0_072 | r_L0_ebeveyn_odasi_3 | - | within_tolerance | 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L0_132 | r_L0_ebeveyn_odasi_m_k_a | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L0_133 | r_L0_ebeveyn_odasi_m_k_a | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L0_068 | r_L0_ebeveyn_odasi_m_k_a | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_069 | r_L0_ebeveyn_odasi_m_k_a_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_070 | r_L0_ebeveyn_odasi_4 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_071 | r_L0_ebeveyn_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_073 | r_L0_oda_01 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_141 | r_L0_ebeveyn_odasi_4 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| lighting_dark | critical | cam_r_L0_yasama_7_2 | r_L0_yasama_7 | - | lighting_beyond_cap | 1 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |

### Inferred and AI-changed items

| id | kind | type | room | labels | reason |
|---|---|---|---|---|---|
| f_L0_003 | piece | unknown | - | inferred | - |
| f_L0_004 | piece | unknown | r_L0_hava_bacasi | inferred | - |
| f_L0_012 | piece | unknown | r_L0_oda_5 | inferred | - |
| f_L0_013 | piece | unknown | - | inferred | - |
| f_L0_033 | piece | unknown | r_L0_banyo_6 | inferred | - |
| f_L0_034 | piece | unknown | r_L0_banyo_8 | inferred | - |
| f_L0_035 | piece | unknown | r_L0_banyo_8 | inferred | - |
| f_L0_036 | piece | unknown | r_L0_banyo_6 | inferred | - |
| f_L0_037 | piece | unknown | r_L0_banyo_3 | inferred | - |
| f_L0_038 | piece | unknown | r_L0_banyo_3 | inferred | - |
| f_L0_039 | piece | unknown | r_L0_banyo_4 | inferred | - |
| f_L0_040 | piece | unknown | r_L0_banyo_4 | inferred | - |
| f_L0_041 | piece | unknown | r_L0_banyo_5 | inferred | - |
| f_L0_042 | piece | unknown | r_L0_banyo | inferred | - |
| f_L0_043 | piece | unknown | r_L0_banyo_7 | inferred | - |
| f_L0_044 | piece | unknown | r_L0_banyo_2 | inferred | - |
| f_L0_045 | piece | unknown | r_L0_banyo | inferred | - |
| f_L0_046 | piece | unknown | r_L0_banyo_5 | inferred | - |
| f_L0_047 | piece | unknown | r_L0_banyo_2 | inferred | - |
| f_L0_048 | piece | unknown | r_L0_banyo_7 | inferred | - |
| f_L0_053 | piece | washing_machine | r_L0_banyo_6 | inferred, adjusted_by_ai | Door d_L0_013 swings into the washing machine on one hinge side; nudge it to clear the swing. |
| f_L0_054 | piece | shower | r_L0_banyo_3 | inferred | - |
| f_L0_056 | piece | toilet | r_L0_banyo_3 | inferred | - |
| f_L0_057 | piece | washing_machine | r_L0_banyo_3 | inferred | - |
| f_L0_060 | piece | toilet | r_L0_banyo_4 | inferred | - |
| f_L0_068 | piece | bed_double | r_L0_ebeveyn_odasi_m_k_a | adjusted_by_ai | Replace the crude low-poly bed with a refined upholstered saddle-back model to resolve the D2 visual quality findings. |
| f_L0_073 | piece | bed_single | r_L0_oda_01 | inferred | - |
| f_L0_074 | piece | washing_machine | r_L0_giris_holu | inferred, adjusted_by_ai | Try facing 90° (toward the room interior) since 0° and 180° both face walls in this corner. |
| f_L0_075 | piece | washing_machine | r_L0_giris_holu_4 | inferred, adjusted_by_ai | Smaller width (0.585m vs 0.65m) to reduce wall w_L0_088 collision from 0.142m to within tolerance. |
| f_L0_076 | piece | washing_machine | r_L0_giris_holu_3 | inferred, adjusted_by_ai | Turn the washing machine front away from the wall it faces into the room, resolving F4. |
| f_L0_077 | piece | washing_machine | r_L0_giris_holu_2 | inferred, adjusted_by_ai | Swap to a slightly smaller washing machine model (0.6424 x 0.6081) to reduce the wall cut from 0.136 m to within the 0.030 m tolerance, fixing S2 |
| f_L0_082 | piece | washing_machine | r_L0_banyo_8 | inferred | - |
| f_L0_089 | piece | unknown | r_L0_banyo_6 | adjusted_by_ai | All retype candidates (bathtub, shower, potted_plant) were rejected due to overlap with the washing machine and the room boundary; the symbol is not buildable furniture. |
| f_L0_090 | piece | unknown | r_L0_banyo_8 | adjusted_by_ai | The 1.00 x 0.85 m drawn piece is a dimension outline or annotation, not a real fixture; it overlaps the shower and has no plausible bathroom type |
| f_L0_098 | piece | wardrobe | r_L0_ebeveyn_odasi_2 | inferred | - |
| f_L0_099 | piece | nightstand | r_L0_ebeveyn_odasi_2 | inferred | - |
| f_L0_100 | piece | nightstand | r_L0_ebeveyn_odasi_2 | inferred | - |
| f_L0_108 | piece | tv_unit | r_L0_yasama_5 | inferred, adjusted_by_ai | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_114 | piece | tv_unit | r_L0_yasama_3 | inferred, adjusted_by_ai | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_120 | piece | tv_unit | r_L0_yasama_6 | inferred, adjusted_by_ai | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_125 | piece | tv_unit | r_L0_yasama_2 | inferred, adjusted_by_ai | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_128 | piece | nightstand | r_L0_ebeveyn_odasi_6 | inferred | - |
| f_L0_129 | piece | nightstand | r_L0_ebeveyn_odasi_6 | inferred | - |
| f_L0_130 | piece | nightstand | r_L0_ebeveyn_odasi_5 | inferred, adjusted_by_ai | F9: nightstand missing from render; swap to a larger classic nightstand model so it is visible next to the bed |
| f_L0_131 | piece | nightstand | r_L0_ebeveyn_odasi_5 | inferred | - |
| f_L0_132 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a | inferred | - |
| f_L0_133 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a | inferred, adjusted_by_ai | Shift nightstand f_L0_133 0.1 m toward -y to create space for the bed to move and improve G5 clearance. |
| f_L0_134 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a_2 | inferred | - |
| f_L0_135 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a_2 | inferred | - |
| f_L0_136 | piece | nightstand | r_L0_ebeveyn_odasi_4 | inferred | - |
| f_L0_138 | piece | sofa_corner | r_L0_yasama_8 | inferred | - |
| f_L0_139 | piece | sofa_corner | r_L0_yasama_7 | inferred | - |
| f_L0_141 | piece | bed_double | r_L0_ebeveyn_odasi_4 | adjusted_by_ai | Snap the headboard of f_L0_141 onto the free wall span s5 (w_L0_121) to fix the headboard-off-wall critical and open the foot clearance. |
| f_L0_143 | piece | wardrobe | r_L0_ebeveyn_odasi_m_k_a | inferred | - |
| f_L0_144 | piece | wardrobe | r_L0_ebeveyn_odasi_m_k_a_2 | inferred | - |
| f_L0_145 | piece | shower | r_L0_banyo_4 | inferred | - |
| f_L0_147 | piece | unknown | r_L0_banyo_7 | adjusted_by_ai | The 0.85x0.80 m square symbol is a structural column/wall segment, not furniture; retype to shower already failed clearance checks. |
| f_L0_148 | piece | unknown | r_L0_banyo_2 | adjusted_by_ai | The 0.85x0.80 m drawn piece cannot be validly typed as a shower in this tight bathroom (Round 1 retype rejected: F9 through outline, G10 clearance, G11 walkway), so it is marked as not furniture to clear the untyped finding. |
| f_L0_149 | piece | unknown | r_L0_banyo_5 | adjusted_by_ai | A 0.85 m square in a 3.5 m2 bathroom is not a plausible fixture (washbasin/shower both rejected); it is a misread symbol/mark, not furniture. |
| f_L0_150 | piece | unknown | r_L0_banyo | adjusted_by_ai | The 0.83 x 0.80 m drawn symbol pokes through the room outline and no candidate type (shower, potted_plant) fits inside the room; it is a dimension outline or wall detail, not furniture. |
| f_L0_151 | piece | table_coffee | r_L0_yasama_6 | inferred | - |
| f_L0_152 | piece | table_coffee | r_L0_yasama_2 | inferred | - |
| f_L0_153 | piece | table_coffee | r_L0_yasama_5 | inferred | - |
| f_L0_154 | piece | table_coffee | r_L0_yasama_8 | inferred | - |
| f_L0_155 | piece | table_coffee | r_L0_yasama_7 | inferred | - |
| f_L0_156 | piece | table_coffee | r_L0_yasama_3 | inferred | - |
| f_L0_162 | piece | bookshelf | r_L0_yasama_7 | inferred | - |
| f_L0_163 | piece | bookshelf | r_L0_yasama_8 | inferred | - |
| f_L0_179 | piece | shower | r_L0_banyo_6 | inferred, adjusted_by_ai | Shower cuts wall w_L0_048 by 0.041 m (tolerance 0.030 m); nudge it to clear the wall. |
| f_L0_180 | piece | shower | r_L0_banyo_8 | inferred, adjusted_by_ai | Swap to a 1.94 m shower to clear the window sill (G12: shower 2.00 m blocks window win_L0_057 sill 0.90 m + 0.05) |
| f_L0_181 | piece | stove | r_L0_yasama_8 | inferred | - |
| f_L0_182 | piece | stove | r_L0_yasama_7 | inferred | - |
| f_L0_183 | piece | unknown | r_L0_oda_01 | inferred | - |
| f_L0_184 | piece | bathtub | r_L0_banyo_5 | inferred, adjusted_by_ai | Narrower 1.32 m bathtub model fits the 1.6 m room width, resolving the S2 wall cut (0.049 m > 0.030 m tolerance). |
| f_L0_185 | piece | bathtub | r_L0_banyo_7 | inferred | - |
| f_L0_186 | piece | bathtub | r_L0_banyo | inferred | - |
| f_L0_187 | piece | bathtub | r_L0_banyo_2 | inferred | - |
| f_L0_188 | piece | washbasin | r_L0_banyo_3 | inferred | - |
| f_L0_189 | piece | chair | r_L0_yasama | inferred, adjusted_by_ai | size snap: the drawn chair 0.74 x 0.68 m is outside its product range (width 0.74 m is 14 % outside 0.35-0.65 m; nearest real product 0.50 x 0.55 m); nearest real product 0.50 x 0.55 x 0.98 m (dining chair 50 x 55) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_190 | piece | sofa_corner | r_L0_yasama | inferred | - |
| f_L0_191 | piece | table_coffee | r_L0_yasama | inferred | - |
| f_L0_192 | piece | unknown | r_L0_banyo_3 | inferred | - |
| f_L0_193 | piece | tv_unit | r_L0_yasama | inferred, adjusted_by_ai | size snap: the drawn tv_unit 1.51 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.51 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_194 | piece | chair | r_L0_yasama_4 | inferred, adjusted_by_ai | size snap: the drawn chair 0.74 x 0.74 m is outside its product range (width 0.74 m is 14 % outside 0.35-0.65 m; depth 0.74 m is 14 % outside 0.35-0.65 m (square symbol: square products only); nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_195 | piece | washbasin | r_L0_banyo_4 | inferred, adjusted_by_ai | Washbasin front was inferred at 50.5° facing a wall 0.22 m away; 230.5° (rotation+90°) aligns the front with the actual opening direction, fixing F4. |
| f_L0_196 | piece | sofa_corner | r_L0_yasama_4 | inferred | - |
| f_L0_197 | piece | table_coffee | r_L0_yasama_4 | inferred | - |
| f_L0_198 | piece | tv_unit | r_L0_yasama_4 | inferred, adjusted_by_ai | size snap: the drawn tv_unit 1.51 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.51 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_199 | piece | unknown | r_L0_banyo_4 | inferred | - |
| f_L0_200 | piece | chair | r_L0_yasama_5 | inferred, adjusted_by_ai | size snap: the drawn chair 0.74 x 0.69 m is outside its product range (width 0.74 m is 14 % outside 0.35-0.65 m; depth 0.69 m is 6 % outside 0.35-0.65 m; nearest real product 0.50 x 0.55 m); nearest real product 0.50 x 0.55 x 0.98 m (dining chair 50 x 55) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_202 | piece | chair | r_L0_yasama_3 | inferred, adjusted_by_ai | size snap: the drawn chair 0.74 x 0.69 m is outside its product range (width 0.74 m is 14 % outside 0.35-0.65 m; depth 0.69 m is 6 % outside 0.35-0.65 m; nearest real product 0.50 x 0.55 m); nearest real product 0.50 x 0.55 x 0.98 m (dining chair 50 x 55) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_203 | piece | floor_lamp | r_L0_yasama_3 | inferred | - |
| f_L0_204 | piece | chair | r_L0_yasama_6 | inferred, adjusted_by_ai | size snap: the drawn chair 0.74 x 0.69 m is outside its product range (width 0.74 m is 14 % outside 0.35-0.65 m; depth 0.69 m is 6 % outside 0.35-0.65 m; nearest real product 0.50 x 0.55 m); nearest real product 0.50 x 0.55 x 0.98 m (dining chair 50 x 55) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_205 | piece | floor_lamp | r_L0_yasama_6 | inferred | - |
| f_L0_206 | piece | chair | r_L0_yasama_2 | inferred, adjusted_by_ai | size snap: the drawn chair 0.74 x 0.69 m is outside its product range (width 0.74 m is 14 % outside 0.35-0.65 m; depth 0.69 m is 6 % outside 0.35-0.65 m; nearest real product 0.50 x 0.55 m); nearest real product 0.50 x 0.55 x 0.98 m (dining chair 50 x 55) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_207 | piece | floor_lamp | r_L0_yasama_2 | inferred | - |
| f_L0_208 | piece | sofa_corner | r_L0_yasama_5 | inferred | - |
| f_L0_209 | piece | sofa_corner | r_L0_yasama_3 | inferred | - |
| f_L0_210 | piece | sofa_corner | r_L0_yasama_6 | inferred | - |
| f_L0_211 | piece | sofa_corner | r_L0_yasama_2 | inferred | - |
| f_L0_212 | piece | fridge | r_L0_yasama_7 | inferred | - |
| f_L0_213 | piece | fridge | r_L0_yasama_8 | inferred | - |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_banyo_6_1 | ![](agent/r1_cam_r_L0_banyo_6_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_6_1_after.jpg) |
| 1 | cam_r_L0_banyo_6_2 | ![](agent/r1_cam_r_L0_banyo_6_2_before.jpg) | ![](agent/r1_cam_r_L0_banyo_6_2_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_5_1 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_1_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_1_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_5_2 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_2_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_2_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_5_3 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_3_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_3_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_m_k_a_1 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_m_k_a_1_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_m_k_a_1_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_m_k_a_2 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_m_k_a_2_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_m_k_a_2_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_m_k_a_3 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_m_k_a_3_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_m_k_a_3_after.jpg) |
| 1 | cam_r_L0_giris_holu_1 | ![](agent/r1_cam_r_L0_giris_holu_1_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_1_after.jpg) |
| 1 | cam_r_L0_giris_holu_2 | ![](agent/r1_cam_r_L0_giris_holu_2_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_2_after.jpg) |
| 1 | cam_r_L0_giris_holu_2_1 | ![](agent/r1_cam_r_L0_giris_holu_2_1_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_2_1_after.jpg) |
| 1 | cam_r_L0_giris_holu_2_2 | ![](agent/r1_cam_r_L0_giris_holu_2_2_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_2_2_after.jpg) |
| 1 | cam_r_L0_giris_holu_3_1 | ![](agent/r1_cam_r_L0_giris_holu_3_1_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_3_1_after.jpg) |
| 1 | cam_r_L0_giris_holu_4_1 | ![](agent/r1_cam_r_L0_giris_holu_4_1_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_4_1_after.jpg) |
| 1 | cam_r_L0_giris_holu_4_2 | ![](agent/r1_cam_r_L0_giris_holu_4_2_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_4_2_after.jpg) |
| 1 | cam_r_L0_kat_merdiveni_1 | ![](agent/r1_cam_r_L0_kat_merdiveni_1_before.jpg) | ![](agent/r1_cam_r_L0_kat_merdiveni_1_after.jpg) |
| 1 | cam_r_L0_kat_merdiveni_2 | ![](agent/r1_cam_r_L0_kat_merdiveni_2_before.jpg) | ![](agent/r1_cam_r_L0_kat_merdiveni_2_after.jpg) |
| 1 | cam_r_L0_kat_merdiveni_3 | ![](agent/r1_cam_r_L0_kat_merdiveni_3_before.jpg) | ![](agent/r1_cam_r_L0_kat_merdiveni_3_after.jpg) |
| 1 | cam_r_L0_oda_10_1 | ![](agent/r1_cam_r_L0_oda_10_1_before.jpg) | ![](agent/r1_cam_r_L0_oda_10_1_after.jpg) |
| 1 | cam_r_L0_oda_7_1 | ![](agent/r1_cam_r_L0_oda_7_1_before.jpg) | ![](agent/r1_cam_r_L0_oda_7_1_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_1 | ![](agent/r1_cam_r_L0_yangin_merdiveni_1_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_1_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_2 | ![](agent/r1_cam_r_L0_yangin_merdiveni_2_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_2_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_3 | ![](agent/r1_cam_r_L0_yangin_merdiveni_3_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_3_after.jpg) |
| 1 | cam_r_L0_yasama_1 | ![](agent/r1_cam_r_L0_yasama_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_1_after.jpg) |
| 1 | cam_r_L0_yasama_2 | ![](agent/r1_cam_r_L0_yasama_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_2_after.jpg) |
| 1 | cam_r_L0_yasama_3 | ![](agent/r1_cam_r_L0_yasama_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_3_after.jpg) |
| 1 | cam_r_L0_yasama_4_1 | ![](agent/r1_cam_r_L0_yasama_4_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_4_1_after.jpg) |
| 1 | cam_r_L0_yasama_4_2 | ![](agent/r1_cam_r_L0_yasama_4_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_4_2_after.jpg) |
| 1 | cam_r_L0_yasama_4_3 | ![](agent/r1_cam_r_L0_yasama_4_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_4_3_after.jpg) |
| 1 | cam_r_L0_yasama_7_1 | ![](agent/r1_cam_r_L0_yasama_7_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_7_1_after.jpg) |
| 1 | cam_r_L0_yasama_7_2 | ![](agent/r1_cam_r_L0_yasama_7_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_7_2_after.jpg) |
| 1 | cam_r_L0_yasama_7_3 | ![](agent/r1_cam_r_L0_yasama_7_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_7_3_after.jpg) |
| 1 | ext_1 | ![](agent/r1_ext_1_before.jpg) | ![](agent/r1_ext_1_after.jpg) |
| 1 | ext_2 | ![](agent/r1_ext_2_before.jpg) | ![](agent/r1_ext_2_after.jpg) |
| 1 | ext_3 | ![](agent/r1_ext_3_before.jpg) | ![](agent/r1_ext_3_after.jpg) |
| 1 | ext_4 | ![](agent/r1_ext_4_before.jpg) | ![](agent/r1_ext_4_after.jpg) |
| 1 | ext_6 | ![](agent/r1_ext_6_before.jpg) | ![](agent/r1_ext_6_after.jpg) |
| 1 | ext_7 | ![](agent/r1_ext_7_before.jpg) | ![](agent/r1_ext_7_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_banyo_2_1 | ![](agent/r2_cam_r_L0_banyo_2_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_2_1_after.jpg) |
| 2 | cam_r_L0_banyo_5_1 | ![](agent/r2_cam_r_L0_banyo_5_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_5_1_after.jpg) |
| 2 | cam_r_L0_banyo_5_2 | ![](agent/r2_cam_r_L0_banyo_5_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_5_2_after.jpg) |
| 2 | cam_r_L0_banyo_6_1 | ![](agent/r2_cam_r_L0_banyo_6_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_6_1_after.jpg) |
| 2 | cam_r_L0_banyo_6_2 | ![](agent/r2_cam_r_L0_banyo_6_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_6_2_after.jpg) |
| 2 | cam_r_L0_ebeveyn_odasi_m_k_a_1 | ![](agent/r2_cam_r_L0_ebeveyn_odasi_m_k_a_1_before.jpg) | ![](agent/r2_cam_r_L0_ebeveyn_odasi_m_k_a_1_after.jpg) |
| 2 | cam_r_L0_ebeveyn_odasi_m_k_a_2 | ![](agent/r2_cam_r_L0_ebeveyn_odasi_m_k_a_2_before.jpg) | ![](agent/r2_cam_r_L0_ebeveyn_odasi_m_k_a_2_after.jpg) |
| 2 | cam_r_L0_ebeveyn_odasi_m_k_a_3 | ![](agent/r2_cam_r_L0_ebeveyn_odasi_m_k_a_3_before.jpg) | ![](agent/r2_cam_r_L0_ebeveyn_odasi_m_k_a_3_after.jpg) |
| 2 | cam_r_L0_giris_holu_2_1 | ![](agent/r2_cam_r_L0_giris_holu_2_1_before.jpg) | ![](agent/r2_cam_r_L0_giris_holu_2_1_after.jpg) |
| 2 | cam_r_L0_giris_holu_2_2 | ![](agent/r2_cam_r_L0_giris_holu_2_2_before.jpg) | ![](agent/r2_cam_r_L0_giris_holu_2_2_after.jpg) |
| 2 | cam_r_L0_giris_holu_4_1 | ![](agent/r2_cam_r_L0_giris_holu_4_1_before.jpg) | ![](agent/r2_cam_r_L0_giris_holu_4_1_after.jpg) |
| 2 | cam_r_L0_giris_holu_4_2 | ![](agent/r2_cam_r_L0_giris_holu_4_2_before.jpg) | ![](agent/r2_cam_r_L0_giris_holu_4_2_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_4 | ![](agent/r2_ext_4_before.jpg) | ![](agent/r2_ext_4_after.jpg) |
| 2 | ext_6 | ![](agent/r2_ext_6_before.jpg) | ![](agent/r2_ext_6_after.jpg) |
| 2 | ext_7 | ![](agent/r2_ext_7_before.jpg) | ![](agent/r2_ext_7_after.jpg) |
| 3 | cam_r_L0_banyo_4_1 | ![](agent/r3_cam_r_L0_banyo_4_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_4_1_after.jpg) |
| 3 | cam_r_L0_banyo_4_2 | ![](agent/r3_cam_r_L0_banyo_4_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_4_2_after.jpg) |
| 3 | cam_r_L0_banyo_5_1 | ![](agent/r3_cam_r_L0_banyo_5_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_5_1_after.jpg) |
| 3 | cam_r_L0_banyo_5_2 | ![](agent/r3_cam_r_L0_banyo_5_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_5_2_after.jpg) |
| 3 | cam_r_L0_banyo_6_1 | ![](agent/r3_cam_r_L0_banyo_6_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_6_1_after.jpg) |
| 3 | cam_r_L0_banyo_6_2 | ![](agent/r3_cam_r_L0_banyo_6_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_6_2_after.jpg) |
| 3 | cam_r_L0_banyo_7_1 | ![](agent/r3_cam_r_L0_banyo_7_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_7_1_after.jpg) |
| 3 | cam_r_L0_banyo_8_1 | ![](agent/r3_cam_r_L0_banyo_8_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_8_1_after.jpg) |
| 3 | ext_1 | ![](agent/r3_ext_1_before.jpg) | ![](agent/r3_ext_1_after.jpg) |
| 3 | ext_2 | ![](agent/r3_ext_2_before.jpg) | ![](agent/r3_ext_2_after.jpg) |
| 3 | ext_3 | ![](agent/r3_ext_3_before.jpg) | ![](agent/r3_ext_3_after.jpg) |
| 3 | ext_4 | ![](agent/r3_ext_4_before.jpg) | ![](agent/r3_ext_4_after.jpg) |
| 3 | ext_6 | ![](agent/r3_ext_6_before.jpg) | ![](agent/r3_ext_6_after.jpg) |
| 3 | ext_7 | ![](agent/r3_ext_7_before.jpg) | ![](agent/r3_ext_7_after.jpg) |
| 4 | cam_r_L0_ebeveyn_odasi_4_1 | ![](agent/r4_cam_r_L0_ebeveyn_odasi_4_1_before.jpg) | ![](agent/r4_cam_r_L0_ebeveyn_odasi_4_1_after.jpg) |
| 4 | cam_r_L0_ebeveyn_odasi_4_2 | ![](agent/r4_cam_r_L0_ebeveyn_odasi_4_2_before.jpg) | ![](agent/r4_cam_r_L0_ebeveyn_odasi_4_2_after.jpg) |
| 4 | cam_r_L0_ebeveyn_odasi_4_3 | ![](agent/r4_cam_r_L0_ebeveyn_odasi_4_3_before.jpg) | ![](agent/r4_cam_r_L0_ebeveyn_odasi_4_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

None.
