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
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 120 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 18 |
| exposure | -7.83 .. +2.67 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| window pull | 52 view(s), -3 .. 0 EV |
| interior glazing pull | 41 view(s) with interior glazing, 9 pulled (k 1 .. 2), 1 still clipped over 1.0 % |
| camera policy | m5 6, search 83 |
| camera score (min / mean / max) | 0.21 / 2.54 / 4.42 |
| rooms by number of views | 19 with 0, 8 with 1, 9 with 2, 19 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 5.4 min / 18.2 min / 5.9 min |
| seconds: polish / gate / check | - / - / 19.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real03.blend](3d/real03.blend) | 409.1 MB |
| [real03.glb](3d/real03.glb) | 1118.0 MB |

89 cameras; textures scaled to at most 1024 px (281 scaled) for the download.

## AI decor

98 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 22 rooms; 4 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

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
- camera ext_7: lens shift -0.72 limited to -0.35; the building does not fit the frame
- 1 exterior view(s) dropped, no camera place worked: ext_5
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- drawn-piece check: 6 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 19 proposal(s) refused, reverted or not placed (listed per room)

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
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.17 | 0 | search 0.55 | - | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2_1 | r_L0_banyo_2 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -1 | search 0.55 | - | 0 | no | [preview](cam_r_L0_banyo_2_1_final_preview.jpg) [plan](cam_r_L0_banyo_2_1_plan.jpg) |
| cam_r_L0_banyo_3_1 | r_L0_banyo_3 | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.91 | D4 | 0 | no | [preview](cam_r_L0_banyo_3_1_final_preview.jpg) [plan](cam_r_L0_banyo_3_1_plan.jpg) |
| cam_r_L0_banyo_4_1 | r_L0_banyo_4 | L0 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 2.43 | D3 | 1 | no | [preview](cam_r_L0_banyo_4_1_final_preview.jpg) [plan](cam_r_L0_banyo_4_1_plan.jpg) |
| cam_r_L0_banyo_4_2 | r_L0_banyo_4 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.11 | D3 | 1 | no | [preview](cam_r_L0_banyo_4_2_final_preview.jpg) [plan](cam_r_L0_banyo_4_2_plan.jpg) |
| cam_r_L0_banyo_5_1 | r_L0_banyo_5 | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 1.87 | D4 A1 | 2 | no | [preview](cam_r_L0_banyo_5_1_final_preview.jpg) [plan](cam_r_L0_banyo_5_1_plan.jpg) |
| cam_r_L0_banyo_5_2 | r_L0_banyo_5 | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.64 | D3 | 1 | no | [preview](cam_r_L0_banyo_5_2_final_preview.jpg) [plan](cam_r_L0_banyo_5_2_plan.jpg) |
| cam_r_L0_banyo_6_1 | r_L0_banyo_6 | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.08 | D2 | 1 | no | [preview](cam_r_L0_banyo_6_1_final_preview.jpg) [plan](cam_r_L0_banyo_6_1_plan.jpg) |
| cam_r_L0_banyo_6_2 | r_L0_banyo_6 | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 0.59 | D2 | 0 | no | [preview](cam_r_L0_banyo_6_2_final_preview.jpg) [plan](cam_r_L0_banyo_6_2_plan.jpg) |
| cam_r_L0_banyo_7_1 | r_L0_banyo_7 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 0.68 | D1 | 0 | no | [preview](cam_r_L0_banyo_7_1_final_preview.jpg) [plan](cam_r_L0_banyo_7_1_plan.jpg) |
| cam_r_L0_banyo_8_1 | r_L0_banyo_8 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 1.28 | D2 | 1 | no | [preview](cam_r_L0_banyo_8_1_final_preview.jpg) [plan](cam_r_L0_banyo_8_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_1 | r_L0_ebeveyn_odasi | L0 | cycles | not_run | - | - | info | - | - | +0.33 | -1 | search 3.34 | D3 A3 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2 | r_L0_ebeveyn_odasi | L0 | cycles | not_run | - | - | info | - | - | +0.50 | -1 | search 1.78 | D3 A2 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2_1 | r_L0_ebeveyn_odasi_2 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | - | search 3.04 | D3 A1 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_2_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2_2 | r_L0_ebeveyn_odasi_2 | L0 | cycles | not_run | - | - | info | - | - | +0.17 | - | search 2.97 | D3 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_2_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_2_3 | r_L0_ebeveyn_odasi_2 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | - | search 2.95 | D4 A2 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_2_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_2_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_3_1 | r_L0_ebeveyn_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | 0 | search 3.62 | D3 A3 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_3_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_3_2 | r_L0_ebeveyn_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 1.89 | D3 A2 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_3_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_4_1 | r_L0_ebeveyn_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.91 | D3 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_4_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_4_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_4_2 | r_L0_ebeveyn_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.17 | - | search 2.88 | D3 A1 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_4_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_4_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_4_3 | r_L0_ebeveyn_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | -1 | search 2.86 | D3 A1 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_4_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_4_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_5_1 | r_L0_ebeveyn_odasi_5 | L0 | cycles | not_run | - | - | info | - | - | +1.83 | -2 | search 3.46 | D3 A2 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_5_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_5_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_5_2 | r_L0_ebeveyn_odasi_5 | L0 | cycles | not_run | - | - | info | - | - | +1.83 | -2 | search 3.40 | D3 A2 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_5_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_5_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_5_3 | r_L0_ebeveyn_odasi_5 | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -3 | search 2.21 | D3 A1 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_5_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_5_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_6_1 | r_L0_ebeveyn_odasi_6 | L0 | cycles | not_run | - | - | info | - | - | +1.83 | -2 | search 3.16 | D3 A3 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_6_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_6_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_6_2 | r_L0_ebeveyn_odasi_6 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -3; interior k1, clip 2.9 % -> 0.1 % | search 1.68 | D3 A2 | 0 | no | [preview](cam_r_L0_ebeveyn_odasi_6_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_6_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_1 | r_L0_ebeveyn_odasi_m_k_a | L0 | cycles | not_run | - | - | info | - | - | +1.17 | -2 | search 2.84 | D5 A2 | 3 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2 | r_L0_ebeveyn_odasi_m_k_a | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -2 | search 2.66 | D4 A1 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_1 | r_L0_ebeveyn_odasi_m_k_a_2 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | -2 | search 3.02 | D5 A1 | 3 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_1_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_2 | r_L0_ebeveyn_odasi_m_k_a_2 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -2 | search 2.80 | D4 A1 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_2_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_3 | r_L0_ebeveyn_odasi_m_k_a_2 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | 0 | search 2.37 | D3 A2 | 1 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_2_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_2_3_plan.jpg) |
| cam_r_L0_ebeveyn_odasi_m_k_a_3 | r_L0_ebeveyn_odasi_m_k_a | L0 | cycles | not_run | - | - | info | - | - | +1.33 | 0 | search 2.01 | D4 A1 | 2 | no | [preview](cam_r_L0_ebeveyn_odasi_m_k_a_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_odasi_m_k_a_3_plan.jpg) |
| cam_r_L0_giris_holu_1 | r_L0_giris_holu | L0 | cycles | not_run | - | - | info | - | - | +2.17 | interior k1, clip 4.4 % -> 0.1 % | search 1.81 | D4 | 0 | no | [preview](cam_r_L0_giris_holu_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_1_plan.jpg) |
| cam_r_L0_giris_holu_2 | r_L0_giris_holu | L0 | cycles | not_run | - | - | info | - | - | +2.33 | interior k2, clip 3.8 % -> 0.0 % | search 1.41 | D2 | 0 | no | [preview](cam_r_L0_giris_holu_2_final_preview.jpg) [plan](cam_r_L0_giris_holu_2_plan.jpg) |
| cam_r_L0_giris_holu_2_1 | r_L0_giris_holu_2 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | interior k1, clip 3.9 % -> 0.0 % | search 1.85 | D3 | 0 | no | [preview](cam_r_L0_giris_holu_2_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_2_1_plan.jpg) |
| cam_r_L0_giris_holu_2_2 | r_L0_giris_holu_2 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 0.99 | D2 | 0 | no | [preview](cam_r_L0_giris_holu_2_2_final_preview.jpg) [plan](cam_r_L0_giris_holu_2_2_plan.jpg) |
| cam_r_L0_giris_holu_3_1 | r_L0_giris_holu_3 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | interior k1, clip 3.3 % -> 0.0 % | search 0.44 | D3 | 0 | no | [preview](cam_r_L0_giris_holu_3_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_3_1_plan.jpg) |
| cam_r_L0_giris_holu_4_1 | r_L0_giris_holu_4 | L0 | cycles | not_run | - | - | info | - | - | +2.33 | interior k2, clip 5.8 % -> 0.0 % | search 1.92 | D4 | 0 | no | [preview](cam_r_L0_giris_holu_4_1_final_preview.jpg) [plan](cam_r_L0_giris_holu_4_1_plan.jpg) |
| cam_r_L0_giris_holu_4_2 | r_L0_giris_holu_4 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | interior k2, clip 3.8 % -> 0.0 % | search 1.64 | D2 | 0 | no | [preview](cam_r_L0_giris_holu_4_2_final_preview.jpg) [plan](cam_r_L0_giris_holu_4_2_plan.jpg) |
| cam_r_L0_kat_holu_1 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -1 | search 2.16 | D1 | 0 | no | [preview](cam_r_L0_kat_holu_1_final_preview.jpg) [plan](cam_r_L0_kat_holu_1_plan.jpg) |
| cam_r_L0_kat_holu_2 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -1 | search 2.10 | D3 A1 | 0 | no | [preview](cam_r_L0_kat_holu_2_final_preview.jpg) [plan](cam_r_L0_kat_holu_2_plan.jpg) |
| cam_r_L0_kat_holu_3 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -1 | search 2.08 | D3 | 0 | no | [preview](cam_r_L0_kat_holu_3_final_preview.jpg) [plan](cam_r_L0_kat_holu_3_plan.jpg) |
| cam_r_L0_kat_merdiveni_1 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 3.98 | D3 | 1 | no | [preview](cam_r_L0_kat_merdiveni_1_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_1_plan.jpg) |
| cam_r_L0_kat_merdiveni_2 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 3.70 | D2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_2_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_2_plan.jpg) |
| cam_r_L0_kat_merdiveni_3 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.33 | interior k1, clip 9.5 % -> 0.0 % | search 3.29 | D2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_3_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_3_plan.jpg) |
| cam_r_L0_oda_01_1 | r_L0_oda_01 | L0 | cycles | not_run | - | - | info | - | - | -0.17 | - | search 3.24 | D3 A1 | 0 | no | [preview](cam_r_L0_oda_01_1_final_preview.jpg) [plan](cam_r_L0_oda_01_1_plan.jpg) |
| cam_r_L0_oda_01_2 | r_L0_oda_01 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 3.19 | D2 A2 | 0 | no | [preview](cam_r_L0_oda_01_2_final_preview.jpg) [plan](cam_r_L0_oda_01_2_plan.jpg) |
| cam_r_L0_oda_01_3 | r_L0_oda_01 | L0 | cycles | not_run | - | - | info | - | - | -0.17 | -1 | search 3.02 | D4 A2 | 0 | no | [preview](cam_r_L0_oda_01_3_final_preview.jpg) [plan](cam_r_L0_oda_01_3_plan.jpg) |
| cam_r_L0_oda_10_1 | r_L0_oda_10 | L0 | cycles | not_run | - | - | info | - | - | +2.50 | 0 | search 0.22 | - | 0 | no | [preview](cam_r_L0_oda_10_1_final_preview.jpg) [plan](cam_r_L0_oda_10_1_plan.jpg) |
| cam_r_L0_oda_19_1 | r_L0_oda_19 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.93 | D4 | 0 | no | [preview](cam_r_L0_oda_19_1_final_preview.jpg) [plan](cam_r_L0_oda_19_1_plan.jpg) |
| cam_r_L0_oda_19_2 | r_L0_oda_19 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.93 | D4 | 0 | no | [preview](cam_r_L0_oda_19_2_final_preview.jpg) [plan](cam_r_L0_oda_19_2_plan.jpg) |
| cam_r_L0_oda_19_3 | r_L0_oda_19 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.89 | D3 | 0 | no | [preview](cam_r_L0_oda_19_3_final_preview.jpg) [plan](cam_r_L0_oda_19_3_plan.jpg) |
| cam_r_L0_oda_7_1 | r_L0_oda_7 | L0 | cycles | not_run | - | - | info | - | - | +2.67 | 0; interior k1, clip 1.6 % -> 1.4 % | search 0.21 | D2 | 0 | no | [preview](cam_r_L0_oda_7_1_final_preview.jpg) [plan](cam_r_L0_oda_7_1_plan.jpg) |
| cam_r_L0_ruzgarlik_1 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | +1.00 | -2 | search 3.88 | D4 A1 | 0 | no | [preview](cam_r_L0_ruzgarlik_1_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_1_plan.jpg) |
| cam_r_L0_ruzgarlik_2 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | +1.00 | -2 | search 3.39 | D4 A1 | 0 | no | [preview](cam_r_L0_ruzgarlik_2_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_2_plan.jpg) |
| cam_r_L0_ruzgarlik_3 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | +0.83 | - | search 3.23 | D3 A1 | 0 | no | [preview](cam_r_L0_ruzgarlik_3_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_3_plan.jpg) |
| cam_r_L0_yangin_merdiveni_1 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 3.19 | D2 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_1_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_1_plan.jpg) |
| cam_r_L0_yangin_merdiveni_2 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +1.00 | - | search 2.20 | D2 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_2_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_2_plan.jpg) |
| cam_r_L0_yangin_merdiveni_3 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 1.78 | D1 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_3_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_3_plan.jpg) |
| cam_r_L0_yasama_1 | r_L0_yasama | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 3.45 | D12 A1 | 4 | no | [preview](cam_r_L0_yasama_1_final_preview.jpg) [plan](cam_r_L0_yasama_1_plan.jpg) |
| cam_r_L0_yasama_2 | r_L0_yasama | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 3.37 | D12 A1 | 4 | no | [preview](cam_r_L0_yasama_2_final_preview.jpg) [plan](cam_r_L0_yasama_2_plan.jpg) |
| cam_r_L0_yasama_2_1 | r_L0_yasama_2 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | -2 | search 3.16 | D13 A3 | 6 | no | [preview](cam_r_L0_yasama_2_1_final_preview.jpg) [plan](cam_r_L0_yasama_2_1_plan.jpg) |
| cam_r_L0_yasama_2_2 | r_L0_yasama_2 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -2 | search 3.09 | D8 A3 | 3 | no | [preview](cam_r_L0_yasama_2_2_final_preview.jpg) [plan](cam_r_L0_yasama_2_2_plan.jpg) |
| cam_r_L0_yasama_2_3 | r_L0_yasama_2 | L0 | cycles | not_run | - | - | info | - | - | +0.83 | -1 | search 3.07 | D11 A2 | 5 | no | [preview](cam_r_L0_yasama_2_3_final_preview.jpg) [plan](cam_r_L0_yasama_2_3_plan.jpg) |
| cam_r_L0_yasama_3 | r_L0_yasama | L0 | cycles | not_run | - | - | info | - | - | +1.17 | 0 | search 3.26 | D10 A1 | 2 | no | [preview](cam_r_L0_yasama_3_final_preview.jpg) [plan](cam_r_L0_yasama_3_plan.jpg) |
| cam_r_L0_yasama_3_1 | r_L0_yasama_3 | L0 | cycles | not_run | - | - | info | - | - | -0.17 | -1 | search 3.25 | D11 A4 | 5 | no | [preview](cam_r_L0_yasama_3_1_final_preview.jpg) [plan](cam_r_L0_yasama_3_1_plan.jpg) |
| cam_r_L0_yasama_3_2 | r_L0_yasama_3 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | - | search 3.24 | D1 | 1 | no | [preview](cam_r_L0_yasama_3_2_final_preview.jpg) [plan](cam_r_L0_yasama_3_2_plan.jpg) |
| cam_r_L0_yasama_3_3 | r_L0_yasama_3 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | 0 | search 3.05 | D13 A4 | 5 | no | [preview](cam_r_L0_yasama_3_3_final_preview.jpg) [plan](cam_r_L0_yasama_3_3_plan.jpg) |
| cam_r_L0_yasama_4_1 | r_L0_yasama_4 | L0 | cycles | not_run | - | - | info | - | - | +1.17 | 0 | search 4.42 | D8 A1 | 4 | no | [preview](cam_r_L0_yasama_4_1_final_preview.jpg) [plan](cam_r_L0_yasama_4_1_plan.jpg) |
| cam_r_L0_yasama_4_2 | r_L0_yasama_4 | L0 | cycles | not_run | - | - | info | - | - | +0.67 | 0 | search 4.08 | D11 | 4 | no | [preview](cam_r_L0_yasama_4_2_final_preview.jpg) [plan](cam_r_L0_yasama_4_2_plan.jpg) |
| cam_r_L0_yasama_4_3 | r_L0_yasama_4 | L0 | cycles | not_run | - | - | info | - | - | +0.33 | 0 | search 4.04 | D11 | 4 | no | [preview](cam_r_L0_yasama_4_3_final_preview.jpg) [plan](cam_r_L0_yasama_4_3_plan.jpg) |
| cam_r_L0_yasama_5_1 | r_L0_yasama_5 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | - | search 3.18 | D11 A2 | 4 | no | [preview](cam_r_L0_yasama_5_1_final_preview.jpg) [plan](cam_r_L0_yasama_5_1_plan.jpg) |
| cam_r_L0_yasama_5_2 | r_L0_yasama_5 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | - | search 3.08 | D1 | 1 | no | [preview](cam_r_L0_yasama_5_2_final_preview.jpg) [plan](cam_r_L0_yasama_5_2_plan.jpg) |
| cam_r_L0_yasama_5_3 | r_L0_yasama_5 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | -1 | search 2.83 | D12 A4 | 3 | no | [preview](cam_r_L0_yasama_5_3_final_preview.jpg) [plan](cam_r_L0_yasama_5_3_plan.jpg) |
| cam_r_L0_yasama_6_1 | r_L0_yasama_6 | L0 | cycles | not_run | - | - | info | - | - | +0.00 | - | search 2.99 | D1 | 1 | no | [preview](cam_r_L0_yasama_6_1_final_preview.jpg) [plan](cam_r_L0_yasama_6_1_plan.jpg) |
| cam_r_L0_yasama_6_2 | r_L0_yasama_6 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -2 | search 2.91 | D13 A4 | 6 | no | [preview](cam_r_L0_yasama_6_2_final_preview.jpg) [plan](cam_r_L0_yasama_6_2_plan.jpg) |
| cam_r_L0_yasama_6_3 | r_L0_yasama_6 | L0 | cycles | not_run | - | - | info | - | - | +1.33 | -2 | search 2.85 | D12 A3 | 5 | no | [preview](cam_r_L0_yasama_6_3_final_preview.jpg) [plan](cam_r_L0_yasama_6_3_plan.jpg) |
| cam_r_L0_yasama_7_1 | r_L0_yasama_7 | L0 | cycles | not_run | - | - | info | - | - | -1.67 | 0 | search 2.70 | D7 A2 | 4 | no | [preview](cam_r_L0_yasama_7_1_final_preview.jpg) [plan](cam_r_L0_yasama_7_1_plan.jpg) |
| cam_r_L0_yasama_7_2 | r_L0_yasama_7 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 2.59 | D5 A2 | 2 | no | [preview](cam_r_L0_yasama_7_2_final_preview.jpg) [plan](cam_r_L0_yasama_7_2_plan.jpg) |
| cam_r_L0_yasama_7_3 | r_L0_yasama_7 | L0 | cycles | not_run | - | - | info | - | - | -1.83 | - | search 2.50 | D6 A1 | 4 | no | [preview](cam_r_L0_yasama_7_3_final_preview.jpg) [plan](cam_r_L0_yasama_7_3_plan.jpg) |
| cam_r_L0_yasama_8_1 | r_L0_yasama_8 | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 2.72 | D5 A2 | 3 | no | [preview](cam_r_L0_yasama_8_1_final_preview.jpg) [plan](cam_r_L0_yasama_8_1_plan.jpg) |
| cam_r_L0_yasama_8_2 | r_L0_yasama_8 | L0 | cycles | not_run | - | - | info | - | - | -1.00 | 0 | search 2.63 | D4 A1 | 3 | no | [preview](cam_r_L0_yasama_8_2_final_preview.jpg) [plan](cam_r_L0_yasama_8_2_plan.jpg) |
| cam_r_L0_yasama_8_3 | r_L0_yasama_8 | L0 | cycles | not_run | - | - | info | - | - | -0.83 | 0 | search 2.57 | D6 A2 | 3 | no | [preview](cam_r_L0_yasama_8_3_final_preview.jpg) [plan](cam_r_L0_yasama_8_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | 0 | m5 | D13 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.50 | 0 | m5 | D12 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.00 | 0 | m5 blocked | D8 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.33 | 0 | m5 blocked | D6 | 0 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 | D12 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.83 | - | m5 | D2 | 0 | no | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

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
| r_L0_oda_19 | balcony | L0 | 3 | 0 | 3 | cam_r_L0_oda_19_1, cam_r_L0_oda_19_2, cam_r_L0_oda_19_3 |
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

None.

## Needs review

None.

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
- f_L0_179
- f_L0_180
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
- cam_r_L0_banyo_5_1: f_L0_149, f_L0_184
- cam_r_L0_banyo_5_2: f_L0_184
- cam_r_L0_banyo_6_1: f_L0_179
- cam_r_L0_banyo_8_1: f_L0_180
- cam_r_L0_ebeveyn_odasi_2_1: f_L0_099
- cam_r_L0_ebeveyn_odasi_2_2: f_L0_099
- cam_r_L0_ebeveyn_odasi_2_3: f_L0_099, f_L0_100
- cam_r_L0_ebeveyn_odasi_4_1: f_L0_136
- cam_r_L0_ebeveyn_odasi_4_3: f_L0_136
- cam_r_L0_ebeveyn_odasi_5_1: f_L0_130
- cam_r_L0_ebeveyn_odasi_5_2: f_L0_130
- cam_r_L0_ebeveyn_odasi_m_k_a_1: f_L0_132, f_L0_133, f_L0_143
- cam_r_L0_ebeveyn_odasi_m_k_a_2: f_L0_132, f_L0_133
- cam_r_L0_ebeveyn_odasi_m_k_a_2_1: f_L0_134, f_L0_135, f_L0_144
- cam_r_L0_ebeveyn_odasi_m_k_a_2_2: f_L0_134, f_L0_135
- cam_r_L0_ebeveyn_odasi_m_k_a_2_3: f_L0_144
- cam_r_L0_ebeveyn_odasi_m_k_a_3: f_L0_133, f_L0_143
- cam_r_L0_kat_merdiveni_1: f_L0_031
- cam_r_L0_kat_merdiveni_2: f_L0_031
- cam_r_L0_kat_merdiveni_3: f_L0_031
- cam_r_L0_yangin_merdiveni_1: f_L0_032
- cam_r_L0_yangin_merdiveni_2: f_L0_032
- cam_r_L0_yangin_merdiveni_3: f_L0_032
- cam_r_L0_yasama_1: f_L0_001, f_L0_002, f_L0_190, f_L0_191
- cam_r_L0_yasama_2: f_L0_001, f_L0_002, f_L0_189, f_L0_190
- cam_r_L0_yasama_2_1: f_L0_028, f_L0_029, f_L0_152, f_L0_206, f_L0_207, f_L0_211
- cam_r_L0_yasama_2_2: f_L0_029, f_L0_206, f_L0_207
- cam_r_L0_yasama_2_3: f_L0_125, f_L0_152, f_L0_206, f_L0_207, f_L0_211
- cam_r_L0_yasama_3: f_L0_001, f_L0_002
- cam_r_L0_yasama_3_1: f_L0_022, f_L0_023, f_L0_202, f_L0_203, f_L0_209
- cam_r_L0_yasama_3_2: f_L0_202
- cam_r_L0_yasama_3_3: f_L0_023, f_L0_114, f_L0_156, f_L0_203, f_L0_209
- cam_r_L0_yasama_4_1: d_L0_024, f_L0_010, f_L0_011, f_L0_194
- cam_r_L0_yasama_4_2: f_L0_010, f_L0_196, f_L0_197, f_L0_198
- cam_r_L0_yasama_4_3: f_L0_010, f_L0_196, f_L0_197, f_L0_198
- cam_r_L0_yasama_5_1: f_L0_019, f_L0_108, f_L0_200, f_L0_208
- cam_r_L0_yasama_5_2: f_L0_200
- cam_r_L0_yasama_5_3: f_L0_020, f_L0_108, f_L0_208
- cam_r_L0_yasama_6_1: f_L0_204
- cam_r_L0_yasama_6_2: f_L0_025, f_L0_026, f_L0_120, f_L0_204, f_L0_205, f_L0_210
- cam_r_L0_yasama_6_3: f_L0_025, f_L0_026, f_L0_204, f_L0_205, f_L0_210
- cam_r_L0_yasama_7_1: f_L0_085, f_L0_139, f_L0_155, f_L0_162
- cam_r_L0_yasama_7_2: f_L0_085, f_L0_212
- cam_r_L0_yasama_7_3: f_L0_085, f_L0_139, f_L0_155, f_L0_212
- cam_r_L0_yasama_8_1: f_L0_087, f_L0_138, f_L0_154
- cam_r_L0_yasama_8_2: f_L0_138, f_L0_154, f_L0_163
- cam_r_L0_yasama_8_3: f_L0_087, f_L0_138, f_L0_154

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

None.

Drawn symbols read as not furniture (never built): dimension_outline 3, door_arc 21, level_mark 1, other 32, room_number 8, text_frame 8.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L0_049 | furniture | stove | objaverse_68e164f1a9414c29820ac2eaf6d8ac04 | vision quality 2 (<= 2) |
| f_L0_050 | furniture | stove | objaverse_68e164f1a9414c29820ac2eaf6d8ac04 | vision quality 2 (<= 2) |
| f_L0_057 | furniture | washing_machine | hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 | the vision check says it is not a washing_machine |
| f_L0_075 | furniture | washing_machine | hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 | vision quality 2 (<= 2) |
| f_L0_150 | furniture | washbasin | hssd_6219ef05f4a7b56419749e45a45143df8af44495 | vision quality 2 (<= 2) |
| f_L0_187 | furniture | bathtub | hssd_08c7c4c8c580d00b822df4ff2bc9e885c136f99d | vision quality 2 (<= 2) |
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
| c_045 | symbol_type_disagreement | f_L0_103 | f_L0_103: sym_L0_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) dresser, pass 2 (zai-org/GLM-4.6V-Flash) wardrobe | typed wardrobe by code (not dresser): the room misses it (the bedroom room's storage group has no wardrobe); inferred, listed in the report (reading.tie_break) |
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

0 change(s) applied, 1 piece(s) added, 8 wall cabinet run(s).

### Ebeveyn Odası (r_L0_ebeveyn_odasi, bedroom): completed (nothing fits: sleeping_double: no candidate position fits the room; storage: no candidate position fits the room)

- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_071

### Ebeveyn Odası (r_L0_ebeveyn_odasi_2, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_058, f_L0_098, f_L0_099, f_L0_100

### Yaşama (r_L0_yasama, living): completed (nothing fits: dining: no candidate position fits the room)

- 2 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001, f_L0_002, f_L0_005, f_L0_006, f_L0_007, f_L0_008, f_L0_009, f_L0_055, f_L0_189, f_L0_190, f_L0_193

### Ebeveyn Odası (r_L0_ebeveyn_odasi_3, bedroom): completed (nothing fits: sleeping_double: no candidate position fits the room; storage: no candidate position fits the room)

- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_072

### Ebeveyn Odası (r_L0_ebeveyn_odasi_4, bedroom): completed

- added f_L0_218: nightstand 0.40 x 0.40 (confidence -, rule)
- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_070, f_L0_136, f_L0_141

### Yaşama (r_L0_yasama_2, living): completed (nothing fits: dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_028, f_L0_029, f_L0_030, f_L0_065, f_L0_122, f_L0_123, f_L0_124, f_L0_125, f_L0_206, f_L0_207, f_L0_211

### Oda-01 (r_L0_oda_01, bedroom): completed (nothing fits: sleeping_single: no candidate position fits the room)

- not placed sleeping_single: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_073, f_L0_103, f_L0_104, f_L0_183

### Yaşama (r_L0_yasama_3, living): completed (nothing fits: dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_022, f_L0_023, f_L0_024, f_L0_063, f_L0_111, f_L0_112, f_L0_113, f_L0_114, f_L0_202, f_L0_203, f_L0_209

### Yaşama (r_L0_yasama_4, living): completed (nothing fits: dining: no candidate position fits the room)

- 2 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_011, f_L0_014, f_L0_015, f_L0_016, f_L0_017, f_L0_018, f_L0_059, f_L0_196, f_L0_198

### Giriş Holü (r_L0_giris_holu, hall): completed (nothing fits: entrance: no place passes the checks)

- not placed entrance: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_074

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_042, f_L0_045, f_L0_081, f_L0_186

### Banyo (r_L0_banyo_2, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_044, f_L0_047, f_L0_079, f_L0_187

### Banyo (r_L0_banyo_3, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_037, f_L0_038, f_L0_054, f_L0_056, f_L0_188, f_L0_192

### Giriş Holü (r_L0_giris_holu_2, hall): completed (nothing fits: entrance: no place passes the checks)

- not placed entrance: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_077

### Banyo (r_L0_banyo_4, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_039, f_L0_040, f_L0_060, f_L0_061, f_L0_145, f_L0_195, f_L0_199

### Hava Bacası (r_L0_hava_bacasi, shaft): skipped (shaft room: never furnished by AI)

No change, no addition.

### Oda (r_L0_oda_5, unknown): skipped (room type unknown: no furniture types to complete)

No change, no addition.

### Yaşama (r_L0_yasama_5, living): completed (nothing fits: dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_019, f_L0_020, f_L0_021, f_L0_062, f_L0_105, f_L0_106, f_L0_107, f_L0_108, f_L0_200, f_L0_201, f_L0_208

### Yaşama (r_L0_yasama_6, living): completed (nothing fits: dining: no candidate position fits the room)

- 1 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_025, f_L0_026, f_L0_027, f_L0_064, f_L0_117, f_L0_118, f_L0_119, f_L0_120, f_L0_204, f_L0_205, f_L0_210

### Banyo (r_L0_banyo_5, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_041, f_L0_046, f_L0_080, f_L0_184

### Yangın Merdiveni (r_L0_yangin_merdiveni, stair): skipped (stair room: never furnished by AI)

No change, no addition.

### Banyo (r_L0_banyo_6, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_033, f_L0_036, f_L0_053, f_L0_179

### Kat Merdiveni (r_L0_kat_merdiveni, stair): skipped (stair room: never furnished by AI)

No change, no addition.

### Giriş Holü (r_L0_giris_holu_3, hall): completed (nothing fits: entrance: no place passes the checks)

- not placed entrance: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_076

### Banyo (r_L0_banyo_7, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_043, f_L0_048, f_L0_078, f_L0_185

### Giriş Holü (r_L0_giris_holu_4, hall): completed (nothing fits: entrance: no place passes the checks)

- not placed entrance: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_075

### Banyo (r_L0_banyo_8, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_034, f_L0_035, f_L0_082, f_L0_180

### Ebeveyn Odası (r_L0_ebeveyn_odasi_5, bedroom): completed (nothing fits: storage: no candidate position fits the room)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_067, f_L0_130, f_L0_131

### Ebeveyn Odası (r_L0_ebeveyn_odasi_6, bedroom): completed (nothing fits: storage: no candidate position fits the room)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_066, f_L0_128, f_L0_129

### Yaşama (r_L0_yasama_7, living): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_050, f_L0_085, f_L0_086, f_L0_139, f_L0_162, f_L0_182, f_L0_212

### Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_068, f_L0_132, f_L0_133, f_L0_143

### Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a_2, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_069, f_L0_134, f_L0_135, f_L0_144

### Yaşama (r_L0_yasama_8, living): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_049, f_L0_087, f_L0_088, f_L0_138, f_L0_163, f_L0_181, f_L0_213

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 171 of 171 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 165 ok, 6 failed; 30 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L0_074 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_092 (now centre None) |
| f_L0_076 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_148 (now back_edge w_L0_066) |
| f_L0_077 | washing_machine (washing_machine) | 0.42 | 90.00 | no | no longer against wall w_L0_147 (now centre None) |
| f_L0_098 | wardrobe (wardrobe) | 0.30 | 0.00 | no | no longer against wall w_L0_105 (now centre None) |
| f_L0_197 | table_coffee (table_coffee) | 0.10 | - | - | - |
| f_L0_204 | fridge (fridge) | 0.15 | 0.00 | yes | - |

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered; 1 dropped (no camera place worked).

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)

Gate for the exterior polish: **not_validated** (exterior views stay the Cycles render): gate/gate_calibration.json missing: gate calibrate did not run or failed.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | no |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok; right: ok | no |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: ok; right: ok | no |
| ext_4 | corner | left, back | - | cycles (gate_validation) | ok | back: ok; left: unverified | no |
| ext_6 | frontal | front | - | cycles (gate_validation) | ok | front: unverified | no |
| ext_7 | entrance | front | - | cycles (gate_validation) | not_in_view | front: ok | no |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_5 | aerial | left, front | flat_cut roof (upper floors not drawn): no aerial view |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | warm greige | fallback | yes | style profile exterior.facade (assumed) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | dark_bronze | - | style | no | style profile exterior.window_frame |
| door | wood_oak_light | - | fallback | yes | style profile exterior.door (assumed) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | fallback | yes | style profile exterior.garden (assumed) |
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

Furniture type methods: ai_two_pass 7, block_name 34, group_member 33, inferred 1, none 24, rule 72. Recognition questions: 64; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_103 | r_L0_oda_01 | wardrobe | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: dresser, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front right 0.90 |
| f_L0_104 | r_L0_oda_01 | unknown | no | unverified | no (untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (door_arc) by Qwen/Qwen3.8-27B-FP8, round 1: The 0.40 x 0.20 m drawn symbol is a door swing arc (dashed rectangle with a quarter-circle arc), not furniture; AI passes returned floor_lamp/unknown.) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_141 | r_L0_ebeveyn_odasi_4 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front top 0.90 |
| f_L0_162 | r_L0_yasama_7 | tv_unit | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: bookshelf, front bottom 0.90 |
| f_L0_163 | r_L0_yasama_8 | tv_unit | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: bookshelf, front top 0.90 |
| f_L0_181 | r_L0_yasama_8 | stove | yes | unverified | no (drawn inside the stove f_L0_049 (60% or more of it): the same piece drawn twice, or a part of it (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: stove, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove, front right 0.90 |
| f_L0_182 | r_L0_yasama_7 | stove | yes | unverified | no (drawn inside the stove f_L0_050 (60% or more of it): the same piece drawn twice, or a part of it (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: stove, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove, front left 0.90 |
| f_L0_183 | r_L0_oda_01 | unknown | no | unverified | no (drawn inside bed_single f_L0_073 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front left 0.90 |
| f_L0_184 | r_L0_banyo_5 | bathtub | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front right 0.90 |
| f_L0_185 | r_L0_banyo_7 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front right 0.90 |
| f_L0_186 | r_L0_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front left 0.90 |
| f_L0_187 | r_L0_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front right 0.90 |
| f_L0_201 | r_L0_yasama_5 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_203 | r_L0_yasama_3 | floor_lamp | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_205 | r_L0_yasama_6 | floor_lamp | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_207 | r_L0_yasama_2 | floor_lamp | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |

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
- outside look garden: grass (fallback: style profile exterior.garden (assumed))
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
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_banyo_3: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_3 |
| area_light | 1 | r_L0_banyo_4: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_4 |
| area_light | 1 | r_L0_banyo_5: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_5 |
| area_light | 1 | r_L0_banyo_6: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_6 |
| area_light | 1 | r_L0_banyo_7: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_7 |
| area_light | 1 | r_L0_banyo_8: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_8 |
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
| area_light | 1 | r_L0_yasama_7: agent: View cam_r_L0_yasama_7_2 is 1.31 stops over the EV cap; the finding names set_lighting factor x3 on the room (headroom covers non-scaling light).; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yasama_7 |
| area_light | 1 | r_L0_yasama_8: agent: Room too dark for cam_r_L0_yasama_8_3 (0.17 stops over EV cap); raise lighting factor x1.58 as the finding names.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yasama_8 |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (-y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 3 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_068, dress_f_L0_069, dress_f_L0_073 |
| boundary | 1 | no site plan: a low hedge on the inferred plot boundary (inferred) | site |
| cabinet_fronts | 6 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_217, furn_f_L0_219, furn_f_L0_220 |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
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
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| ground:all | 1 | D3a: nothing about the ground is drawn: the ground floor stands 0.15 m above it (one inferred step) | site |
| handrail | 2 | design detail on every flight side not against a wall; not in the documents | furn_f_L0_031, furn_f_L0_032 |
| hedge | 5 | no site plan: a low hedge on the inferred plot boundary (inferred) | boundary_hedge_01, boundary_hedge_02, boundary_hedge_03 |
| height | 25 | door height listed as assumed in the building JSON | d_L0_001, d_L0_002, d_L0_003 |
| height | 4 | no height in the JSON; type height for bathtub | furn_f_L0_184, furn_f_L0_185, furn_f_L0_186 |
| height | 9 | no height in the JSON; type height for bed_double | furn_f_L0_058, furn_f_L0_066, furn_f_L0_067 |
| height | 1 | no height in the JSON; type height for bed_single | furn_f_L0_073 |
| height | 14 | no height in the JSON; type height for chair | furn_f_L0_007, furn_f_L0_008, furn_f_L0_009 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L0_201, furn_f_L0_203, furn_f_L0_205 |
| height | 8 | no height in the JSON; type height for fridge | furn_f_L0_189, furn_f_L0_194, furn_f_L0_200 |
| height | 14 | no height in the JSON; type height for kitchen_counter | furn_f_L0_001, furn_f_L0_002, furn_f_L0_010 |
| height | 1 | no height in the JSON; type height for shower | furn_f_L0_054 |
| height | 8 | no height in the JSON; type height for sofa_corner | furn_f_L0_138, furn_f_L0_139, furn_f_L0_190 |
| height | 8 | no height in the JSON; type height for stove | furn_f_L0_049, furn_f_L0_050, furn_f_L0_055 |
| height | 6 | no height in the JSON; type height for table_dining | furn_f_L0_006, furn_f_L0_015, furn_f_L0_105 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L0_051, furn_f_L0_052, furn_f_L0_056 |
| height | 8 | no height in the JSON; type height for tv_unit | furn_f_L0_108, furn_f_L0_114, furn_f_L0_120 |
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
| modules | 16 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L0_001, furn_f_L0_002, furn_f_L0_010 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| outline | 1 | no roof outline drawn: the walls' outline (wall_union) grown by the overhang 0.60 m | roof |
| parapet_material | 1 | flat_cut roof: the slab edge and the 0.30 m parapet are walling finished like the facade (render), with the coping on top, not the roof covering (concrete_tiles) | roof |
| path:d_L0_019,d_L0_020 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: concrete_exposed (style family modern; not drawn) | facade |
| plot | 1 | no site plan: the plot is the outline's rectangle + 6 m (inferred) | site |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_058 (the top of the nightstand f_L0_100 is taken by the plant_small dec_L0_010): the wall sconce would cover the window win_L0_056 | rig_r_L0_ebeveyn_odasi_2 |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_070 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L0_ebeveyn_odasi_4 |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_071 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L0_ebeveyn_odasi, rig_r_L0_ebeveyn_odasi |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_072 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L0_ebeveyn_odasi_3, rig_r_L0_ebeveyn_odasi_3 |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_073 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L0_oda_01, rig_r_L0_oda_01 |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_150; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_3: ceiling fixture at the pole of inaccessibility of r_L0_banyo_3; its light under the decor ceiling light dec_L0_041; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_3_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_3: mirror light over the washbasin f_L0_188; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_3_mirror_1_light |
| rig_light | 1 | r_L0_banyo_4: ceiling fixture at the pole of inaccessibility of r_L0_banyo_4; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_4_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_4: mirror light over the washbasin f_L0_195; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_4_mirror_1_light |
| rig_light | 1 | r_L0_banyo_5: ceiling fixture at the pole of inaccessibility of r_L0_banyo_5; its light under the decor ceiling light dec_L0_054; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_5_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_5: mirror light over the washbasin f_L0_149, above the mirror dec_L0_053 (top 2.20 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_5_mirror_1_light |
| rig_light | 1 | r_L0_banyo_6: ceiling fixture at the pole of inaccessibility of r_L0_banyo_6; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_6_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_7: ceiling fixture at the pole of inaccessibility of r_L0_banyo_7; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_7_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_7: mirror light over the washbasin f_L0_147, above the mirror dec_L0_057 (top 2.20 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_7_mirror_1_light |
| rig_light | 1 | r_L0_banyo_8: ceiling fixture at the pole of inaccessibility of r_L0_banyo_8; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_8_ceiling_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_2: bedside light in the shade of the table lamp dec_L0_009 on f_L0_099 beside the bed f_L0_058; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_4: bedside lamp on the nightstand f_L0_136; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_5: bedside light in the shade of the table lamp dec_L0_063 on f_L0_130 beside the bed f_L0_067; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_5_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_5: bedside wall sconce on the head wall beside the bed f_L0_067 (the top of the nightstand f_L0_131 is taken by the plant_small dec_L0_064); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_5_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_6: bedside lamp on the nightstand f_L0_129; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_6_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_6: bedside light in the shade of the table lamp dec_L0_072 on f_L0_128 beside the bed f_L0_066; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_6_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a: bedside lamp on the nightstand f_L0_133; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a: bedside light in the shade of the table lamp dec_L0_084 on f_L0_132 beside the bed f_L0_068; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_bedside_1_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a_2: bedside light in the shade of the table lamp dec_L0_092 on f_L0_134 beside the bed f_L0_069; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_2_bedside_2_light |
| rig_light | 1 | r_L0_ebeveyn_odasi_m_k_a_2: bedside wall sconce on the head wall beside the bed f_L0_069 (the top of the nightstand f_L0_135 is taken by the plant_small dec_L0_093); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_ebeveyn_odasi_m_k_a_2_bedside_1_light |
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
| rig_mirror | 1 | mirror light over the washbasin f_L0_089: the mirror dec_L0_055 reaches 2.60 m and the ceiling is at 2.70 m, so the bar would cross it | rig_r_L0_banyo_6 |
| rig_mirror | 1 | mirror light over the washbasin f_L0_090: the mirror dec_L0_059 reaches 2.60 m and the ceiling is at 2.70 m, so the bar would cross it | rig_r_L0_banyo_8 |
| rig_mirror | 1 | mirror light over the washbasin f_L0_148: the mirror dec_L0_039 reaches 2.57 m and the ceiling is at 2.70 m, so the bar would cross it | rig_r_L0_banyo_2 |
| rise_m | 2 | on the top level with no level above and not over a stair of the level below: the stair stops under the roof underside; no roof opening is drawn, none is cut | furn_f_L0_031, furn_f_L0_032 |
| riser_m | 2 | limited by the roof underside (no level above, assumed): 2.694 m / 24 drawn risers | furn_f_L0_031, furn_f_L0_032 |
| roof | 1 | listed as assumed in the building JSON | roof |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 20 | outside sill 1.66 x 0.084 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_031_sill, win_L0_032_sill, win_L0_033_sill |
| sill | 1 | outside sill 2.61 x 0.234 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill |
| sill | 1 | outside sill 2.96 x 0.234 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill |
| sill_height | 64 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 46 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_ebeveyn_odasi, skirting_r_L0_ebeveyn_odasi_2, skirting_r_L0_yasama |
| slab | 1 | thickness 0.2 m assumed in the building JSON | sl_L0 |
| steps:d_L0_019 | 1 | entrance door 0.15 m above the ground: a landing and 0 steps of 0.150 m (inferred) | site |
| steps:d_L0_020 | 1 | entrance door 0.15 m above the ground: a landing and 0 steps of 0.150 m (inferred) | site |
| thickness | 1 | flat_cut: a flat roof slab (assumed) | roof |
| tree | 2 | small tree: crown 3.5 m as drawn, 5.6 m tall (height by the crown class, assumed); species olive (inferred) | tree_tree_inferred_1, tree_tree_inferred_2 |
| tree:tree_inferred_1 | 1 | no site plan: a tree clear of the paths and the front garden; the window band narrowed to 4 m out and 1 m on each side because the first pass placed 0 of 3 (inferred, docs/milestone11.md §1.1 E11; fix round after P4b) | site |
| tree:tree_inferred_2 | 1 | no site plan: a tree clear of the paths and the front garden; the window band narrowed to 4 m out and 1 m on each side because the first pass placed 0 of 3 (inferred, docs/milestone11.md §1.1 E11; fix round after P4b) | site |
| trees | 1 | inferred trees: placed 2 of 3 (122 candidates; removed by path 6, sightline 36, window 108, front 51; most by window; the first pass placed 0, the second pass with the window band narrowed to 4 m added 2) | site |
| turn | 2 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L0_031, furn_f_L0_032 |
| waist | 2 | the documents show the stair in plan only | furn_f_L0_031, furn_f_L0_032 |
| wall_joint | 2 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L0_031, furn_f_L0_032 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_rustic_4_694dfd55 [tool_nc], gen_potted_plant_industrial_3_23920a8f [tool_nc], hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_31609de54bc7b3cceb58cff41b88b69d7f7db9ec [non_commercial], hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_43fa24cb165eb3bfde976d070bfd615f41c78028 [non_commercial], hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_52e54d4aedff229ec50eefe25bd168c60141c37f [non_commercial], hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial], hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial], hssd_6b6d600719446182c0a798676eb807c0ea4ec772 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_762d42fce4ff28d319112e66bde33c3f4329c175 [non_commercial], hssd_7835135c9a3abefa43deca495710555800d8aeca [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial], hssd_b74cfc2ae648ddcf1375088e23d9643b7c5ed736 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial], hssd_ead365ee0f62fd7ab510ffb80417061b626087b7 [non_commercial], hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial], hssd_xxxxbeae246cx5cbcx482dx81faxd6e6f844d62d [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L0_banyo_1: commercial-safe: yes
- cam_r_L0_banyo_2_1: commercial-safe: yes
- cam_r_L0_banyo_3_1: commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_7835135c9a3abefa43deca495710555800d8aeca [non_commercial])
- cam_r_L0_banyo_4_1: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_762d42fce4ff28d319112e66bde33c3f4329c175 [non_commercial])
- cam_r_L0_banyo_4_2: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_762d42fce4ff28d319112e66bde33c3f4329c175 [non_commercial])
- cam_r_L0_banyo_5_1: commercial-safe: no (flagged assets: hssd_43fa24cb165eb3bfde976d070bfd615f41c78028 [non_commercial], hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial])
- cam_r_L0_banyo_5_2: commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial])
- cam_r_L0_banyo_6_1: commercial-safe: no (flagged assets: hssd_6b6d600719446182c0a798676eb807c0ea4ec772 [non_commercial])
- cam_r_L0_banyo_6_2: commercial-safe: no (flagged assets: hssd_31609de54bc7b3cceb58cff41b88b69d7f7db9ec [non_commercial])
- cam_r_L0_banyo_7_1: commercial-safe: no (flagged assets: hssd_ead365ee0f62fd7ab510ffb80417061b626087b7 [non_commercial])
- cam_r_L0_banyo_8_1: commercial-safe: no (flagged assets: hssd_b74cfc2ae648ddcf1375088e23d9643b7c5ed736 [non_commercial])
- cam_r_L0_ebeveyn_odasi_1: commercial-safe: no (flagged assets: hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_ebeveyn_odasi_2: commercial-safe: no (flagged assets: hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_ebeveyn_odasi_2_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_2_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_2_3: commercial-safe: no (flagged assets: hssd_52e54d4aedff229ec50eefe25bd168c60141c37f [non_commercial])
- cam_r_L0_ebeveyn_odasi_3_1: commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial])
- cam_r_L0_ebeveyn_odasi_3_2: commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial])
- cam_r_L0_ebeveyn_odasi_4_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_4_2: commercial-safe: no (flagged assets: hssd_xxxxbeae246cx5cbcx482dx81faxd6e6f844d62d [non_commercial])
- cam_r_L0_ebeveyn_odasi_4_3: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_5_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_5_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_5_3: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_6_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_6_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_m_k_a_1: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_m_k_a_2: commercial-safe: yes
- cam_r_L0_ebeveyn_odasi_m_k_a_2_1: commercial-safe: no (flagged assets: gen_plant_small_rustic_4_694dfd55 [tool_nc])
- cam_r_L0_ebeveyn_odasi_m_k_a_2_2: commercial-safe: no (flagged assets: gen_plant_small_rustic_4_694dfd55 [tool_nc])
- cam_r_L0_ebeveyn_odasi_m_k_a_2_3: commercial-safe: no (flagged assets: gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], gen_plant_small_rustic_4_694dfd55 [tool_nc])
- cam_r_L0_ebeveyn_odasi_m_k_a_3: commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_giris_holu_1: commercial-safe: no (flagged assets: hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial])
- cam_r_L0_giris_holu_2: commercial-safe: no (flagged assets: hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial])
- cam_r_L0_giris_holu_2_1: commercial-safe: no (flagged assets: hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial])
- cam_r_L0_giris_holu_2_2: commercial-safe: yes
- cam_r_L0_giris_holu_3_1: commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial])
- cam_r_L0_giris_holu_4_1: commercial-safe: no (flagged assets: hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial])
- cam_r_L0_giris_holu_4_2: commercial-safe: no (flagged assets: hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial])
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
- cam_r_L0_yasama_2: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_2_1: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_2_2: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_2_3: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_3: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial])
- cam_r_L0_yasama_3_1: commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_3_2: commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_3_3: commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial])
- cam_r_L0_yasama_4_1: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_4_2: commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_4_3: commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_5_1: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_5_2: commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_5_3: commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial])
- cam_r_L0_yasama_6_1: commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_6_2: commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_6_3: commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_7_1: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc])
- cam_r_L0_yasama_7_2: commercial-safe: no (flagged assets: gen_potted_plant_industrial_3_23920a8f [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_7_3: commercial-safe: no (flagged assets: gen_potted_plant_industrial_3_23920a8f [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_8_1: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L0_yasama_8_2: commercial-safe: yes
- cam_r_L0_yasama_8_3: commercial-safe: yes
- ext_1: commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial])
- ext_2: commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial])
- ext_3: commercial-safe: yes
- ext_4: commercial-safe: yes
- ext_6: commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial])
- ext_7: commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial])

## Built below library level (Milestone 13)

36 furniture piece(s) built from a module builder or a parametric family instead of a library model: 4 library gap(s) to close with a real model, 32 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L0_089 | washbasin | module | bath_set | r_L0_banyo_6 | bathroom | from_documents | no (by design) | module builder bath_set (4 module(s): vanity unit 100x50 cm, 1 inset basin(s) with taps, framed mirror 0.90 x 0.80 m) (by design) |
| f_L0_090 | washbasin | module | bath_set | r_L0_banyo_8 | bathroom | from_documents | no (by design) | module builder bath_set (4 module(s): vanity unit 100x50 cm, 1 inset basin(s) with taps, framed mirror 0.90 x 0.80 m) (by design) |
| f_L0_201 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_5 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_203 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_3 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_205 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_6 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_207 | floor_lamp | parametric | parametric:floor_lamp | r_L0_yasama_2 | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_217 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama | living | added_by_ai | no (by design) | - |
| f_L0_219 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_2 | living | added_by_ai | no (by design) | - |
| f_L0_220 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_3 | living | added_by_ai | no (by design) | - |
| f_L0_222 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_4 | living | added_by_ai | no (by design) | - |
| f_L0_223 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_5 | living | added_by_ai | no (by design) | - |
| f_L0_224 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_yasama_6 | living | added_by_ai | no (by design) | - |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_3 (3.6 degrees off the sun, sky pull k 3).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (64 of 64 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (64 of 64 answered) |

Assets: textures CC0 x 19; furniture/decor models CC-BY-4.0 x 109, CC-BY-NC-4.0 x 62, CC0 x 4, generated (Infinigen v1.19.0, BSD-3-Clause) x 2, generated (TRELLIS.2-4B, MIT) x 11 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 89 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Pia Texturizada por Wellington Marques" by mendesviana (https://sketchfab.com/3d-models/3a406e651e69409e87323ab42a214874), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L0_036, dec_L0_101)
- "Dinner Tray" by c_irby_paint (https://sketchfab.com/3d-models/3e7747b1db4b44a4952d6d94488ee16e), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L0_026)
- "Stove from Poly by Google" by IronEqual (https://sketchfab.com/3d-models/68e164f1a9414c29820ac2eaf6d8ac04), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for f_L0_049, f_L0_050)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261022-165510-full-20261022T170113Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 33.9 s | - |
| pipeline | pending | 105.9 s | 58 recognition question(s) written (recognition/requests.json) |
| recognize | reused | 2.0 s | - |
| style | ok | 0.6 s | - |
| pipeline_final | ok | 102.9 s | answers applied |
| fit | ok | 8.7 s | - |
| layout | ok | 24.1 s | - |
| decor_ask | ok | 5.5 min | - |
| photos | reused | 0.3 s | - |
| assets | ok | 6.3 s | - |
| decor | ok | 29.1 s | - |
| agent_apply | ok | 30.2 s | - |
| refit | ok | 52.7 s | - |
| build | ok | 25.2 min | - |
| agent_previews | ok | 13.8 min | 11 view(s) |
| agent | ok | 40.5 min | 3 round(s), 24 finding(s) removed by 24 accepted edit(s) (measured; 23 predicted by the dry re-checks), 6 new, net 18, 178 rejected; stop: max rounds reached |
| render | ok | 33.8 min | - |
| export | ok | 3.0 min | - |
| controls | ok | 5.0 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 2.7 min | - |
| check | ok | 6.4 min | - |
| combine | ok | 2.8 min | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 24 edit(s) accepted, 195 rejected, 599 model calls (6781658 tokens), 54.9 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 1614): earlier runs of the appended log are left out (1613 events, 782 model calls, 48 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 24 / 195 (11 % accepted) |
| rejected by reason | memory 33, drawn_lock 31, no_overlap 30, acceptance 28, fixture_place 15 |
| rooms checked by code / vision / planner | 55 / 36 / 28 |
| rooms with fixable critical or major findings visited | 28 of 28 |
| critical before -> after | 9 -> 4 |
| major before -> after | 130 -> 112 |
| agent minutes; first accepted edit after | 41.66; 40.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 33; 100; 75 (46) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 29 measured; 28 predicted |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 8 new; net 21 |
| edits removing their finding | 21 of 24 |
| plans ok / empty / refused / default | 46 / 25 / 4 / 0 |

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 9 | 130 | 35 | 2 | 16 | 70 | layout | 41 |
| 2 | 5 | 118 | 34 | 3 | 4 | 56 | layout | 15 |
| 3 | 4 | 115 | 36 | 3 | 4 | 52 | refit | 11 |
| 4 | 4 | 112 | 34 | 2 | 0 | 17 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D2 | 0 | 1 | 0 | 0 |
| F1 | 2 | 5 | 0 | 0 |
| F3 | 4 | 40 | 1 | 0 |
| F4 | 0 | 21 | 0 | 0 |
| F7 | 13 | 0 | 0 | 0 |
| F9 | 1 | 42 | 0 | 0 |
| G10 | 0 | 44 | 0 | 0 |
| G11 | 0 | 20 | 0 | 0 |
| G12 | 0 | 79 | 0 | 0 |
| G13 | 0 | 11 | 0 | 0 |
| G2 | 0 | 1 | 0 | 0 |
| G4 | 0 | 0 | 12 | 0 |
| G5 | 0 | 27 | 0 | 0 |
| G6 | 0 | 32 | 0 | 0 |
| G8 | 0 | 93 | 0 | 0 |
| LG | 0 | 0 | 16 | 0 |
| NR | 0 | 1 | 0 | 0 |
| R3 | 0 | 0 | 36 | 0 |
| RC | 0 | 0 | 52 | 0 |
| S2 | 0 | 32 | 12 | 0 |
| S5 | 0 | 0 | 8 | 0 |
| X2 | 2 | 2 | 0 | 0 |
| X3 | 0 | 0 | 0 | 10 |
| X4 | 0 | 3 | 2 | 0 |
| X6 | 0 | 1 | 0 | 0 |
| camera_blocked | 0 | 16 | 0 | 0 |
| lighting_dark | 0 | 4 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 1848 | 1 | fix_fixture | f_L0_204 | adjusted_by_ai | 0.0 -> 10.0 | Fridge blocks door o_L0_019; move it to the nearest valid spot off the door swing. | ![](agent/r1_019_fix_fixture_before_r_L0_yasama_6.png) | ![](agent/r1_022_fix_fixture_after_r_L0_yasama_6.png) |
| 1877 | 1 | remove_piece | f_L0_221 | added_by_ai | 0.0 -> 10.0 | added_by_ai wall_cabinet is not a piece of a living room (F1 wrong_type); not drawn, not required by program | ![](agent/r1_060_remove_piece_before_r_L0_yasama_4.png) | ![](agent/r1_063_remove_piece_after_r_L0_yasama_4.png) |
| 1889 | 1 | set_lighting | r_L0_yasama_8 | agent_override | - | Room too dark for cam_r_L0_yasama_8_3 (0.17 stops over EV cap); raise lighting factor x1.58 as the finding names. | - | - |
| 1892 | 1 | remove_piece | f_L0_216 | added_by_ai | 7.0 -> 17.0 | AI-added wall_cabinet is not a piece of a living room (F1); removing it clears the wrong-type finding. | ![](agent/r1_073_remove_piece_before_r_L0_yasama.png) | ![](agent/r1_074_remove_piece_after_r_L0_yasama.png) |
| 1897 | 1 | move_piece | f_L0_218 | added_by_ai | 17.0 -> 20.0 | Snap the nightstand's back edge onto the left wall (w_L0_118) so its back is on a wall. | ![](agent/r1_078_move_piece_before_r_L0_ebeveyn_odasi_4.png) | ![](agent/r1_081_move_piece_after_r_L0_ebeveyn_odasi_4.png) |
| 1898 | 1 | move_piece | f_L0_197 | adjusted_by_ai | 10.0 -> 20.0 | coffee table 0.29 m from sofa front, needs >= 0.30 m; shift 0.1 m away from the sofa front | ![](agent/r1_080_move_piece_before_r_L0_yasama_4.png) | ![](agent/r1_083_move_piece_after_r_L0_yasama_4.png) |
| 1899 | 1 | set_lighting | r_L0_yangin_merdiveni | agent_override | - | Both cameras are under-exposed (+3.98 EV and +3.28 EV vs +3.00 cap); the larger suggested factor x2.79 lifts incident light enough to bring both views under the EV cap. | - | - |
| 1905 | 1 | set_room_type | r_L0_oda_19 | adjusted_by_ai | 100.0 -> 100.0 | Room read as 'unknown' and flagged empty; label 'Oda' and program infer a bedroom, so set the type to let the solver place the required sleeping_double and storage groups. | ![](agent/r1_090_set_room_type_before_r_L0_oda_19.png) | ![](agent/r1_093_set_room_type_after_r_L0_oda_19.png) |
| 1914 | 1 | retype_piece | f_L0_128 | adjusted_by_ai | 100.0 -> 100.0 | Confirm the drawn nightstand next to the bed so it is built as a nightstand instead of rendering as a bare lamp (F1 v:r1-v32:1). | ![](agent/r1_101_retype_piece_before_r_L0_ebeveyn_odasi_6.png) | ![](agent/r1_105_retype_piece_after_r_L0_ebeveyn_odasi_6.png) |
| 1917 | 1 | retype_piece | f_L0_129 | adjusted_by_ai | 100.0 -> 100.0 | Confirm the second drawn nightstand on the other side of the bed so it is built (F1 v:r1-v32:2). | ![](agent/r1_106_retype_piece_before_r_L0_ebeveyn_odasi_6.png) | ![](agent/r1_107_retype_piece_after_r_L0_ebeveyn_odasi_6.png) |
| 1929 | 1 | set_lighting | r_L0_yasama_7 | agent_override | - | View cam_r_L0_yasama_7_2 is 1.31 stops over the EV cap; the finding names set_lighting factor x3 on the room (headroom covers non-scaling light). | - | - |
| 1952 | 1 | mark_not_furniture | f_L0_104 | adjusted_by_ai | 87.0 -> 87.0 | The 0.40 x 0.20 m drawn symbol is a door swing arc (dashed rectangle with a quarter-circle arc), not furniture; AI passes returned floor_lamp/unknown. | ![](agent/r1_114_mark_not_furniture_before_r_L0_oda_01.png) | ![](agent/r1_116_mark_not_furniture_after_r_L0_oda_01.png) |
| 1954 | 1 | retype_piece | f_L0_131 | adjusted_by_ai | 100.0 -> 100.0 | Confirm the second nightstand's type so it is built in the render, matching the drawn nightstand on both sides of the bed. | ![](agent/r1_115_retype_piece_before_r_L0_ebeveyn_odasi_5.png) | ![](agent/r1_118_retype_piece_after_r_L0_ebeveyn_odasi_5.png) |
| 1969 | 1 | rotate_piece | f_L0_076 | adjusted_by_ai | 80.0 -> 90.0 | Front faced the wall at x≈29.75 (0°); turning 270° (south) faces it into the room, fixing F4. | ![](agent/r1_134_rotate_piece_before_r_L0_giris_holu_3.png) | ![](agent/r1_138_rotate_piece_after_r_L0_giris_holu_3.png) |
| 1971 | 1 | rotate_piece | f_L0_074 | adjusted_by_ai | 80.0 -> 90.0 | Front at 180° faced wall w_L0_088 0.00 m ahead; 0° also faces a wall; rotate to 90° so the front faces into the room toward the free span s0 (into_room_deg 90°) to clear F4. | ![](agent/r1_147_rotate_piece_before_r_L0_giris_holu.png) | ![](agent/r1_149_rotate_piece_after_r_L0_giris_holu.png) |
| 1978 | 1 | set_exterior | exterior:roof | agent_override | - | Add the missing flat roof with a 0.5 m overhang to close the open top and match the specified 0.3-0.8 m overhang. | - | - |
| 2252 | 2 | retype_piece | f_L0_153 | adjusted_by_ai | 0.0 -> 0.0 | Rebuild the coffee table from a standard library model to remove the circular hole rendering error on its top. | ![](agent/r2_049_retype_piece_before_r_L0_yasama_5.png) | ![](agent/r2_051_retype_piece_after_r_L0_yasama_5.png) |
| 2277 | 2 | set_room_type | r_L0_oda_19 | adjusted_by_ai | 100.0 -> 100.0 | The plan shows a railing, a glass door and outdoor lounge chairs — this is a balcony/terrace, not a bedroom; the bedroom program (bed+wardrobe) cannot fit the 4.2x2.6 m space. | ![](agent/r2_063_set_room_type_before_r_L0_oda_19.png) | ![](agent/r2_064_set_room_type_after_r_L0_oda_19.png) |
| 2283 | 2 | retype_piece | f_L0_103 | adjusted_by_ai | 87.0 -> 87.0 | Confirm the drawn wardrobe type: the source shows a large closed wardrobe, not a small open-topped cabinet. | ![](agent/r2_066_retype_piece_before_r_L0_oda_01.png) | ![](agent/r2_067_retype_piece_after_r_L0_oda_01.png) |
| 2334 | 2 | set_exterior | exterior:site | agent_override | - | Add a paved walkway and entrance steps so the door is accessible from the foreground, clearing the hedge setback. | - | - |
| 2588 | 3 | move_piece | f_L0_098 | adjusted_by_ai | 70.0 -> 80.0 | Shift the wardrobe 0.30 m toward its wall to open 0.73 m in front, approaching the 0.80 m needed (G13). | ![](agent/r3_054_move_piece_before_r_L0_ebeveyn_odasi_2.png) | ![](agent/r3_055_move_piece_after_r_L0_ebeveyn_odasi_2.png) |
| 2637 | 3 | rotate_piece | f_L0_077 | adjusted_by_ai | 80.0 -> 90.0 | Face the washing machine north into the open room space, away from the east wall it is embedded in, clearing F4. | ![](agent/r3_071_rotate_piece_before_r_L0_giris_holu_2.png) | ![](agent/r3_072_rotate_piece_after_r_L0_giris_holu_2.png) |
| 2639 | 3 | set_exterior | exterior:roof | agent_override | - | Increase roof overhang to 0.6 m so the roof edge visibly projects from the wall face within the 0.3-0.8 m spec. | - | - |
| 2640 | 3 | set_exterior | exterior:site | agent_override | - | Add a paved path to the entrance door and a hedge plot boundary to resolve missing site access and undefined plot edge. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 1844 | 1 | fix_fixture | f_L0_200 | acceptance: finding G12:f_L0_200 is still there after the edit (fridge f_L0_200 (1.80 m) stands in front of window win_L0_053 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_010 and stands in front of window win_L0_011 with no counter beside it; move it to the nearest valid spot off the door swing and window. |
| 1849 | 1 | fix_fixture | f_L0_206 | acceptance: finding G12:f_L0_206 is still there after the edit (fridge f_L0_206 (1.80 m) stands in front of window win_L0_061 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_016 (F7), stands in front of window win_L0_025 (G12) and lacks counter clearance (G8); reposition up to 0.5 m to a valid spot. |
| 1850 | 1 | fix_fixture | f_L0_202 | acceptance: finding G12:f_L0_202 is still there after the edit (fridge f_L0_202 (1.80 m) stands in front of window win_L0_052 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_007 and stands in front of window win_L0_008; move it to the nearest valid spot within the kitchen run. |
| 1851 | 1 | retype_piece | f_L0_111 | no_change: f_L0_111 is already a table_dining | Confirm the drawn table_dining (vector geometry shows a table with chairs around it); resolves the AI-passes sofa misread and the hole-in-top visual finding. |
| 1852 | 1 | move_piece | f_L0_120 | drawn_lock: f_L0_120: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.47 m) | Shift tv_unit up the west wall to clear windows win_L0_028 and win_L0_029 (G12). |
| 1853 | 1 | fix_fixture | f_L0_206 | fixture_place: f_L0_206 at [30.41, 4.90] is still through a wall or in a door swing; without center the code searches every spot within 0.50 m: when that search found no valid spot, none exists, do not try centres; the finding stays for review | Move fridge 0.35 m down the west wall to clear door o_L0_016 (F7) and window win_L0_025 (G12), landing between the windows. |
| 1854 | 1 | move_piece | f_L0_120 | acceptance: finding G12:f_L0_120 is still there after the edit (tv_unit f_L0_120 (1.30 m) stands in front of window win_L0_029 (sill 0.90 m + 0.05)) | Shift tv_unit up the west wall 0.26 m to clear windows win_L0_028 and win_L0_029 (G12). |
| 1855 | 1 | fix_fixture | f_L0_202 | f_L0_202: no_overlap | Move fridge down along the right wall to clear door o_L0_007 and windows win_L0_008/win_L0_052. |
| 1856 | 1 | move_piece | f_L0_125 | snap: f_L0_125: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Move tv_unit off windows win_L0_024/win_L0_025 onto the south wall span s0 (below sill, facing into the room) to clear both G12 findings. |
| 1857 | 1 | fix_fixture | f_L0_202 | fixture_move: f_L0_202: the move is 0.65 m, at most 0.50 m | Move fridge up along the right wall into the gap between windows win_L0_052 and win_L0_008 to clear the door and windows. |
| 1858 | 1 | move_piece | f_L0_125 | drawn_lock: f_L0_125: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.24 m) | Move tv_unit into the open floor near the south wall, away from windows win_L0_024/win_L0_025, to clear both G12 findings. |
| 1859 | 1 | move_piece | f_L0_205 | drawn_lock: f_L0_205: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.42 m) | Move floor lamp down the east wall to clear window win_L0_064 (G12). |
| 1860 | 1 | move_piece | f_L0_119 | drawn_lock: f_L0_119: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.34 m) | Move chair f_L0_119 away from the table to give ≥0.81 m clearance behind it (G6). |
| 1861 | 1 | fix_fixture | f_L0_202 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_202 is still there after the edit (fridge f_L0_202 (1.80 m) stands in front of window win_L0_052 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_007 and stands in front of windows; find the nearest valid spot within the kitchen run. |
| 1862 | 1 | move_piece | f_L0_207 | drawn_lock: f_L0_207: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.35 m) | Move floor lamp 0.35 m away from window win_L0_063 into the open floor to clear the G12 finding. |
| 1863 | 1 | move_piece | f_L0_114 | snap: f_L0_114: no free place on wall w_L0_083 (doors, windows, at most 1.2 m from the drawn place) | Move TV unit off the right wall (windows win_L0_007/win_L0_008) to the free left wall span to clear both windows. |
| 1864 | 1 | move_piece | f_L0_207 | f_L0_207: no_overlap | Move floor lamp 0.3 m away from window win_L0_063 into the open floor to clear the G12 finding. |
| 1865 | 1 | move_piece | f_L0_205 | f_L0_205: no_overlap, f_L0_210: no_overlap | Move floor lamp down the east wall 0.27 m to clear window win_L0_064 (G12). |
| 1866 | 1 | move_piece | f_L0_119 | f_L0_210: no_overlap | Move chair f_L0_119 down 0.29 m to give ≥0.81 m clearance behind it (G6). |
| 1867 | 1 | move_piece | f_L0_114 | drawn_lock: f_L0_114: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.09 m) | Shift TV unit up along the right wall into the gap between windows win_L0_008 and win_L0_007 to clear both. |
| 1868 | 1 | move_piece | f_L0_207 | f_L0_207: no_overlap, f_L0_211: no_overlap | Move floor lamp 0.3 m south, away from window win_L0_063, into open floor to clear the G12 finding. |
| 1869 | 1 | move_piece | f_L0_119 | score: plausibility 10 -> 0 (F4 f_L0_119: chair does not face its group (f_L0_117, f_L0_151); G6 f_L0_119: chair f_L0_119 is 61° off the table f_L0_117 (needs ≤ 45°)) | Move chair f_L0_119 left 0.29 m away from the sofa to give ≥0.81 m clearance behind it (G6). |
| 1870 | 1 | move_piece | f_L0_205 | f_L0_205: no_overlap, f_L0_210: no_overlap | Move floor lamp down 0.25 m to clear window win_L0_064 (G12). |
| 1871 | 1 | move_piece | f_L0_124 | drawn_lock: f_L0_124: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.33 m) | Move chair f_L0_124 to the table's south side, clearing the collision with f_L0_123 (S2) and giving ≥0.81 m behind it (G6). |
| 1872 | 1 | move_piece | f_L0_203 | drawn_lock: f_L0_203: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.38 m) | Move floor lamp away from window win_L0_050 to clear the window band. |
| 1873 | 1 | move_piece | f_L0_113 | drawn_lock: f_L0_113: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.34 m) | Move chair f_L0_113 away from the wall behind it to give the required 0.81 m clearance. |
| 1875 | 1 | fix_fixture | f_L0_204 | no_change: f_L0_204: nothing to fix (size within the real range, inside the room and off the doors) | Fridge still stands in front of windows win_L0_028 and win_L0_062 (G12); move it to the nearest valid spot off the windows. |
| 1876 | 1 | move_piece | f_L0_124 | score: plausibility -20 -> -40 (F4 f_L0_124: chair does not face its group (f_L0_122, f_L0_152); F9 f_L0_124: chair f_L0_124 overlaps chair f_L0_123 by 0.06 m²; G6 f_L0_124: chair f_L0_124 is 85° off the table f_L0_122 (needs ≤ 45°)) | Move chair f_L0_124 0.3 m south to clear the collision with f_L0_123 (S2) and improve clearance behind it (G6). |
| 1878 | 1 | move_piece | f_L0_203 | f_L0_203: no_overlap, score: plausibility -20 -> -30 (F9 f_L0_203: floor_lamp f_L0_203 overlaps table_dining f_L0_111 by 0.08 m²) | Move floor lamp 0.28 m away from window win_L0_050 to clear the window band. |
| 1879 | 1 | move_piece | f_L0_124 | drawn_lock: f_L0_124: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair f_L0_124 0.3 m east, away from f_L0_123, to clear the S2 collision while keeping it facing the table. |
| 1880 | 1 | fix_fixture | f_L0_010 | fixture_place: f_L0_010: no valid spot within 0.50 m (it stands 0.29 m² outside the room) | kitchen_counter cuts the room outline/wall (F9, S2) and leaves a 0.06 m aisle (G8); let the code find the nearest valid spot |
| 1882 | 1 | retype_piece | f_L0_122 | no_change: f_L0_122 is already a table_dining | Confirm f_L0_122 as table_dining: chairs are drawn around it (vector geometry outranks the AI passes that typed it sofa). |
| 1883 | 1 | move_piece | f_L0_141 | f_L0_141: doors_free, f_L0_141: no_overlap, f_L0_218: no_overlap, score: plausibility 17 -> 1 (G4 f_L0_141: bed_double f_L0_141: no nightstand on the free left side of the head (1.51 m free); G4 f_L0_141: bed_double f_L0_141: no nightstand on the free right side of the head (0.37 m free); G4 f_L0_218: nightstand f_L0_218 of bed_double f_L0_141: -0.06 m from the bed side (needs ≤ 0.30 m); G5 f_L0_141: bed_double f_L0_141: 0.37 m free along the right side, needs ≥ 0.60 m) | Slide the second bed 0.08 m against the right wall so the headboard sits on the wall, the foot clears the wall, and the right use zone opens to the door walkway. |
| 1884 | 1 | move_piece | f_L0_197 | acceptance: finding G2:f_L0_197 is still there after the edit (coffee table f_L0_197 is 0.29 m from the sofa front, needs ≥ 0.30 m) | coffee table 0.29 m from sofa front, needs >= 0.30 m; shift 0.1 m away from the sofa |
| 1886 | 1 | move_piece | f_L0_141 | acceptance: finding F4:f_L0_141 is still there after the edit (bed_double faces a wall 0.13 m in front of it); 2 more kept | Snap the second bed's back edge onto the right wall (w_L0_121) so the headboard sits on the wall and the foot clears the wall. |
| 1887 | 1 | move_piece | f_L0_017 | acceptance: finding G6:f_L0_017 is still there after the edit (chair f_L0_017: 0.46 m from the table edge to the wall or piece behind, needs ≥ 0.81 m); 1 more kept | chair f_L0_017 has 0.46 m behind it, needs >= 0.81 m; shift 0.1 m away from the piece behind |
| 1890 | 1 | move_piece | f_L0_018 | acceptance: finding G6:f_L0_018 is still there after the edit (chair f_L0_018: 0.46 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | chair f_L0_018 has 0.46 m behind it, needs >= 0.81 m; shift 0.1 m away from the piece behind |
| 1891 | 1 | fix_fixture | f_L0_213 | fixture_place: f_L0_213: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_014) | Fridge stands in front of window win_L0_055 (G12); reposition up to 0.5 m off the window. |
| 1893 | 1 | move_piece | f_L0_141 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L0_141 is still there after the edit (bed_double faces a wall 0.13 m in front of it); 2 more kept | Snap the second bed's back edge onto the right wall (w_L0_121) so the headboard sits on the wall and the foot clears the wall. |
| 1894 | 1 | fix_fixture | f_L0_001 | fixture_place: f_L0_001: no valid spot within 0.50 m (it stands 0.32 m² outside the room) | kitchen_counter f_L0_001 reaches 0.32 m² through the room outline and cuts wall w_L0_098 by 0.200 m; move it up to 0.5 m to clear the wall. |
| 1895 | 1 | move_piece | f_L0_141 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L0_141 is still there after the edit (bed_double faces a wall 0.13 m in front of it); 2 more kept | Snap the second bed's back edge onto the right wall (w_L0_121) so the headboard sits on the wall and the foot clears the wall. |
| 1900 | 1 | move_piece | f_L0_017 | score: plausibility 20 -> 0 (F4 f_L0_017: chair does not face its group (f_L0_015, f_L0_197); G6 f_L0_017: chair f_L0_017 is 53° off the table f_L0_015 (needs ≤ 45°)) | chair f_L0_017 has 0.46 m behind it, needs >= 0.81 m; shift 0.1 m away from the piece behind |
| 1901 | 1 | move_piece | f_L0_018 | score: plausibility 20 -> 0 (F4 f_L0_018: chair does not face its group (f_L0_015, f_L0_197); G6 f_L0_018: chair f_L0_018 is 54° off the table f_L0_015 (needs ≤ 45°)) | chair f_L0_018 has 0.46 m behind it, needs >= 0.81 m; shift 0.1 m away from the piece behind |
| 1902 | 1 | move_piece | f_L0_070 | drawn_lock: f_L0_070: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.34 m) | Nudge the first bed 0.34 m toward the left wall to open the 0.60 m side clearance. |
| 1904 | 1 | move_piece | f_L0_070 | snap: f_L0_070: no free place on wall w_L0_118 (doors, windows, at most 1.2 m from the drawn place) | Snap the first bed's back edge onto the left wall (w_L0_118) to open the 0.60 m side clearance. |
| 1906 | 1 | move_piece | f_L0_017 | acceptance: finding G6:f_L0_017 is still there after the edit (chair f_L0_017: 0.46 m from the table edge to the wall or piece behind, needs ≥ 0.81 m); 1 more kept | chair f_L0_017 has 0.46 m behind it, needs >= 0.81 m; shift 0.1 m away from the piece behind |
| 1907 | 1 | move_piece | f_L0_070 | drawn_lock: f_L0_070: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the first bed 0.30 m toward the left wall to open the 0.60 m side clearance. |
| 1908 | 1 | move_piece | f_L0_018 | acceptance: finding G6:f_L0_018 is still there after the edit (chair f_L0_018: 0.46 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | chair f_L0_018 has 0.46 m behind it, needs >= 0.81 m; shift 0.1 m away from the piece behind |
| 1909 | 1 | move_piece | f_L0_070 | max_tries: f_L0_070 was edited 3 times in this round | Nudge the first bed 0.29 m toward the left wall to open the 0.60 m side clearance. |
| 1912 | 1 | move_piece | f_L0_058 | drawn_lock: f_L0_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the bed 0.30 m toward the left wall to open ≥0.60 m at the foot (G5) and let a 0.60 m walkway from door o_L0_003 reach the right use zone (G11). |
| 1916 | 1 | move_piece | f_L0_058 | snap: f_L0_058: no free place on wall w_L0_017 (doors, windows, at most 1.2 m from the drawn place) | Snap the bed's back onto the left wall (w_L0_017) at its drawn centre height to open ≥0.60 m at the foot (G5) and let a 0.60 m walkway from door o_L0_003 reach the right use zone (G11). |
| 1918 | 1 | move_piece | f_L0_058 | memory: the same edit was rejected in round 1: drawn_lock: f_L0_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the bed 0.30 m toward the left wall to open ≥0.60 m at the foot (G5) and let a 0.60 m walkway from door o_L0_003 reach the right use zone (G11). |
| 1921 | 1 | move_piece | f_L0_058 | max_tries: f_L0_058 was edited 3 times in this round | Shift the bed 0.29 m toward the left wall to open ≥0.60 m at the foot (G5) and let a 0.60 m walkway from door o_L0_003 reach the right use zone (G11). |
| 1925 | 1 | move_piece | f_L0_098 | snap: f_L0_098: no free place on wall w_L0_017 (doors, windows, at most 1.2 m from the drawn place) | Slide the wardrobe along the left wall toward the top to free ≥0.80 m in front of it (G13). |
| 1927 | 1 | move_piece | f_L0_098 | drawn_lock: f_L0_098: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Slide the wardrobe 0.30 m along the left wall to free ≥0.80 m in front of it (G13). |
| 1932 | 1 | move_piece | f_L0_098 | acceptance: finding G13:f_L0_098 is still there after the edit (wardrobe f_L0_098: 0.43 m free in front, needs ≥ 0.80 m) | Slide the wardrobe 0.29 m along the left wall to free ≥0.80 m in front of it (G13). |
| 1951 | 1 | move_piece | f_L0_073 | f_L0_073: clearance_ok | Shift bed 0.30 m toward the north wall to open ≥0.60 m clearance along its best (south) side, currently 0.47 m. |
| 1956 | 1 | rotate_piece | f_L0_076 | drawn_lock: f_L0_076: the new front does not fix the error (its front faces a wall) | Front faced the wall at x≈29.75 (0°); turning 180° faces it into the room, fixing F4. |
| 1958 | 1 | move_piece | f_L0_073 | drawn_lock: f_L0_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift bed 0.30 m west so its east side gains 0.77 m of free space (≥0.60 m needed), keeping the 0.30 m head clearance at the north wall. |
| 1960 | 1 | move_piece | f_L0_073 | score: plausibility 87 -> 47 (F3 f_L0_073: bed_single: the headboard stands in the room (0.28 m off); F9 f_L0_073: bed_single reaches 0.27 m² through the room outline, up to 0.279 m deep; G5 f_L0_073: bed_single f_L0_073: 0.46 m free along its best side, needs ≥ 0.60 m on one side) | Shift bed 0.29 m west so its east side gains 0.76 m of free space (≥0.60 m needed), keeping the 0.31 m head clearance at the north wall. |
| 1961 | 1 | rotate_piece | f_L0_077 | drawn_lock: f_L0_077: the new front does not fix the error (its front faces a wall) | Front faced the wall it is against; turning it 180° faces the front into the room, clearing F4. |
| 1962 | 1 | move_piece | f_L0_073 | max_tries: f_L0_073 was edited 3 times in this round | Shift bed 0.29 m north so its south side gains 0.76 m of free space (≥0.60 m needed), keeping the 0.20 m head clearance at the north wall. |
| 1964 | 1 | rotate_piece | f_L0_075 | drawn_lock: f_L0_075: the new front does not fix the error (its front faces a wall) | Front faced a wall 0.00 m ahead; turn it to face into the room (0°) to clear F4. |
| 1968 | 1 | rotate_piece | f_L0_074 | drawn_lock: f_L0_074: the new front does not fix the error (its front faces a wall) | Front faced a wall 0.00 m ahead; turn it to face into the room (toward free span s4, into_room_deg 0°) to clear F4. |
| 1970 | 1 | fix_fixture | f_L0_076 | fixture_place: f_L0_076: no valid spot within 0.50 m (it stands 0.12 m² outside the room) | Washing machine cuts wall w_L0_152 by 0.157 m and reaches 0.11 m² through the room outline; nudge it to clear the wall. |
| 1973 | 1 | fix_fixture | f_L0_074 | fixture_place: f_L0_074: no valid spot within 0.50 m (it stands 0.12 m² outside the room) | Machine cuts wall w_L0_088 by 0.150 m and reaches 0.11 m² through the room outline; nudge it up to 0.5 m to a valid spot that clears the wall and outline. |
| 1979 | 1 | fix_fixture | f_L0_187 | fixture_place: f_L0_187: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_011) | Bathtub has only 0.10 m clear in front, needs ≥ 0.53 m; reposition/resize to satisfy clearance. |
| 1980 | 1 | fix_fixture | f_L0_186 | fixture_place: f_L0_186: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_005) | Bathtub has only 0.10 m clear in front, needs ≥ 0.53 m; let the code find a valid spot or shrink to a real product size that fits the bay. |
| 1982 | 1 | fix_fixture | f_L0_184 | fixture_place: f_L0_184: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_002) | Bathtub drawn 1.55 m long in a 0.9 m bay; shrink to nearest real product size that fits, restoring the 0.53 m front clearance (G10). |
| 1984 | 1 | fix_fixture | f_L0_185 | fixture_place: f_L0_185: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_008) | Bathtub has only 0.10 m clear in front (needs ≥ 0.53 m); reposition to a valid spot satisfying front clearance. |
| 2220 | 2 | fix_fixture | f_L0_206 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_206 is still there after the edit (fridge f_L0_206 (1.80 m) stands in front of window win_L0_061 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_016 (F7), stands in front of window win_L0_025 (G12) and lacks counter clearance (G8); let the code find the nearest valid spot. |
| 2223 | 2 | fix_fixture | f_L0_206 | fixture_move: f_L0_206: the move is 0.50 m, at most 0.50 m | Shift fridge 0.5 m along the west wall away from door o_L0_016 and window win_L0_025 to clear F7 and G12. |
| 2224 | 2 | fix_fixture | f_L0_200 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_200 is still there after the edit (fridge f_L0_200 (1.80 m) stands in front of window win_L0_053 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_010 and stands in front of window win_L0_011; reposition up to 0.5 m to clear the door swing and window. |
| 2225 | 2 | fix_fixture | f_L0_202 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_202 is still there after the edit (fridge f_L0_202 (1.80 m) stands in front of window win_L0_052 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_007 and stands in front of window win_L0_008; let the code find the nearest valid spot within 0.5 m. |
| 2226 | 2 | fix_fixture | f_L0_206 | f_L0_206: no_overlap | Shift fridge 0.45 m along the west wall away from door o_L0_016 and window win_L0_025 to clear F7 and G12. |
| 2227 | 2 | fix_fixture | f_L0_202 | fixture_move: f_L0_202: the move is 0.50 m, at most 0.50 m | Shift fridge 0.5 m away from the door swing and window win_L0_008 to clear the blocked opening. |
| 2228 | 2 | fix_fixture | f_L0_206 | max_tries: f_L0_206 was edited 3 times in this round | Shift fridge 0.35 m along the west wall away from door o_L0_016 and window win_L0_025 to clear F7 and G12. |
| 2229 | 2 | fix_fixture | f_L0_202 | f_L0_202: no_overlap | Shift fridge 0.45 m away from the door swing and window win_L0_008 to clear the blocked opening. |
| 2231 | 2 | move_piece | f_L0_125 | snap: f_L0_125: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Snap tv_unit back onto the south wall span s0, centred between the windows, to clear G12 on win_L0_024 and win_L0_025. |
| 2232 | 2 | fix_fixture | f_L0_202 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_202 is still there after the edit (fridge f_L0_202 (1.80 m) stands in front of window win_L0_052 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_007 and stands in front of window win_L0_008; let the code find the nearest valid spot within 0.5 m. |
| 2233 | 2 | move_piece | f_L0_125 | acceptance: finding G12:f_L0_125 is still there after the edit (tv_unit f_L0_125 (1.30 m) stands in front of window win_L0_024 (sill 0.90 m + 0.05)) | Nudge tv_unit 0.22 m south to clear the window win_L0_024/win_L0_025 band (G12) while staying within its 0.223 m allowance. |
| 2235 | 2 | move_piece | f_L0_207 | memory: the same edit was rejected in round 1: f_L0_207: no_overlap; f_L0_211: no_overlap | Move floor_lamp 0.3 m south away from window win_L0_063 to clear G12. |
| 2236 | 2 | move_piece | f_L0_114 | acceptance: finding G12:f_L0_114 is still there after the edit (tv_unit f_L0_114 (1.30 m) stands in front of window win_L0_008 (sill 0.90 m + 0.05)) | Shift TV unit 0.29 m away from windows win_L0_007 and win_L0_008 to clear the blocked openings. |
| 2237 | 2 | move_piece | f_L0_207 | f_L0_207: no_overlap | Move floor_lamp 0.2 m west away from window win_L0_063 to clear G12. |
| 2238 | 2 | move_piece | f_L0_203 | memory: the same edit was rejected in round 1: f_L0_203: no_overlap; score: plausibility -20 -> -30 (F9 f_L0_203: floor_lamp f_L0_203 overlaps table_dining f_L0_111 by 0.08 m²) | Shift floor lamp 0.28 m away from window win_L0_050 to clear the blocked opening. |
| 2239 | 2 | move_piece | f_L0_113 | score: plausibility -20 -> -40 (F4 f_L0_113: chair does not face its group (f_L0_111, f_L0_156); G6 f_L0_113: chair f_L0_113 is 45° off the table f_L0_111 (needs ≤ 45°)) | Shift chair 0.03 m to improve clearance behind it (needs ≥ 0.81 m). |
| 2240 | 2 | move_piece | f_L0_207 | acceptance: finding G12:f_L0_207 is still there after the edit (floor_lamp f_L0_207 (1.60 m) stands in front of window win_L0_063 (sill 0.90 m + 0.05)) | Move floor_lamp 0.22 m south away from window win_L0_063 to clear G12. |
| 2242 | 2 | move_piece | f_L0_201 | f_L0_201: no_overlap, f_L0_208: no_overlap | Move floor lamp 0.3 m away from window win_L0_051 to clear the window sill. |
| 2243 | 2 | fix_fixture | f_L0_010 | memory: the same edit was rejected in round 1: fixture_place: f_L0_010: no valid spot within 0.50 m (it stands 0.29 m² outside the room) | Retry the only allowed tool for the kitchen counter's G8 aisle / F9 / S2 findings; the code will find the nearest valid spot within 0.5 m. |
| 2244 | 2 | move_piece | f_L0_201 | drawn_lock: f_L0_201: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move floor lamp 0.3 m down along the left wall, away from window win_L0_051, to clear the window sill. |
| 2245 | 2 | move_piece | f_L0_124 | memory: the same edit was rejected in round 1: drawn_lock: f_L0_124: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair f_L0_124 0.3 m east to the table's east side: clears the 0.045 m overlap with f_L0_123 (S2) and gives 0.81 m+ clearance behind it (G6). |
| 2246 | 2 | move_piece | f_L0_114 | acceptance: finding G12:f_L0_114 is still there after the edit (tv_unit f_L0_114 (1.30 m) stands in front of window win_L0_007 (sill 0.90 m + 0.05)) | Shift TV unit 0.26 m toward the wall to clear windows win_L0_007 and win_L0_008. |
| 2247 | 2 | move_piece | f_L0_203 | f_L0_203: no_overlap, score: plausibility -20 -> -30 (F9 f_L0_203: floor_lamp f_L0_203 overlaps table_dining f_L0_111 by 0.08 m²) | Shift floor lamp 0.23 m away from window win_L0_050 to clear the blocked opening. |
| 2248 | 2 | move_piece | f_L0_113 | memory: the same edit was rejected in round 2: score: plausibility -20 -> -40 (F4 f_L0_113: chair does not face its group (f_L0_111, f_L0_156); G6 f_L0_113: chair f_L0_113 is 45° off the table f_L0_111 (needs ≤ 45°)) | Shift chair 0.03 m to improve clearance behind it (needs ≥ 0.81 m). |
| 2249 | 2 | move_piece | f_L0_124 | f_L0_207: no_overlap | Move chair f_L0_124 0.26 m east to the table's east side: clears the 0.045 m overlap with f_L0_123 (S2) and gives 0.81 m+ clearance behind it (G6). |
| 2250 | 2 | move_piece | f_L0_107 | drawn_lock: f_L0_107: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair 0.3 m to increase clearance behind it (0.43 m -> 0.73 m) towards the required 0.81 m. |
| 2251 | 2 | move_piece | f_L0_124 | drawn_lock: f_L0_124: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Move chair f_L0_124 0.24 m east to the table's east side: clears the 0.045 m overlap with f_L0_123 (S2) and gives 0.81 m+ clearance behind it (G6). |
| 2253 | 2 | move_piece | f_L0_114 | acceptance: finding G12:f_L0_114 is still there after the edit (tv_unit f_L0_114 (1.30 m) stands in front of window win_L0_007 (sill 0.90 m + 0.05)) | Shift TV unit 0.22 m toward the wall to clear windows win_L0_007 and win_L0_008. |
| 2260 | 2 | move_piece | f_L0_008 | score: plausibility 17 -> -3 (F4 f_L0_008: chair does not face its group (f_L0_006, f_L0_191); G6 f_L0_008: chair f_L0_008 is 57° off the table f_L0_006 (needs ≤ 45°)) | Shift chair 0.13 m away from the window wall behind to restore the 0.81 m clearance behind it (G6). |
| 2261 | 2 | move_piece | f_L0_009 | score: plausibility 17 -> -3 (F4 f_L0_009: chair does not face its group (f_L0_006); G6 f_L0_009: chair f_L0_009 is 58° off the table f_L0_006 (needs ≤ 45°)) | Shift chair 0.13 m away from the window wall behind to restore the 0.81 m clearance behind it (G6). |
| 2263 | 2 | place_group | r_L0_oda_19 | no_place: sleeping_double group: no place passes the checks (sleeping_double: no candidate position fits the room) | Build the required bed group so the bedroom is no longer empty (F1). |
| 2265 | 2 | move_piece | f_L0_008 | memory: the same edit was rejected in round 2: score: plausibility 17 -> -3 (F4 f_L0_008: chair does not face its group (f_L0_006, f_L0_191); G6 f_L0_008: chair f_L0_008 is 57° off the table f_L0_006 (needs ≤ 45°)) | Shift chair 0.13 m away from the window wall behind to restore the 0.81 m clearance behind it (G6). |
| 2267 | 2 | move_piece | f_L0_009 | memory: the same edit was rejected in round 2: score: plausibility 17 -> -3 (F4 f_L0_009: chair does not face its group (f_L0_006); G6 f_L0_009: chair f_L0_009 is 58° off the table f_L0_006 (needs ≤ 45°)) | Shift chair 0.13 m away from the window wall behind to restore the 0.81 m clearance behind it (G6). |
| 2268 | 2 | place_group | r_L0_oda_19 | no_place: storage group: no place passes the checks (storage: no candidate position fits the room) | Build the required storage group so the bedroom is no longer empty (F1). |
| 2270 | 2 | move_piece | f_L0_008 | score: plausibility 17 -> -3 (F4 f_L0_008: chair does not face its group (f_L0_006, f_L0_191); G6 f_L0_008: chair f_L0_008 is 64° off the table f_L0_006 (needs ≤ 45°)) | Shift chair 0.18 m away from the window wall behind to restore the 0.81 m clearance behind it (G6). |
| 2271 | 2 | move_piece | f_L0_009 | score: plausibility 17 -> -3 (F4 f_L0_009: chair does not face its group (f_L0_006); G6 f_L0_009: chair f_L0_009 is 65° off the table f_L0_006 (needs ≤ 45°)) | Shift chair 0.18 m away from the window wall behind to restore the 0.81 m clearance behind it (G6). |
| 2274 | 2 | move_piece | f_L0_008 | max_tries: f_L0_008 was edited 3 times in this round | Shift chair 0.08 m away from the window wall behind to restore the 0.81 m clearance behind it (G6) while keeping it within 45° of the table. |
| 2275 | 2 | move_piece | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | Shift chair 0.08 m away from the window wall behind to restore the 0.81 m clearance behind it (G6) while keeping it within 45° of the table. |
| 2280 | 2 | retype_piece | f_L0_073 | retype: bed_double is no candidate for f_L0_073 (0.95 x 1.95 m at [20.64, 2.36]): the size table and the room / zone give bed_single, desk, stair | Source drawing shows a double bed; the single bunk rendering is inconsistent with the drawing and the room's area. |
| 2286 | 2 | move_piece | f_L0_144 | acceptance: finding G13:f_L0_144 is still there after the edit (wardrobe f_L0_144: 0.13 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along its wall to open the 0.80 m front clearance (G13). |
| 2289 | 2 | retype_piece | f_L0_073 | no_change: f_L0_073 is already a bed_single | The drawing's own label reads bed_single and the size table only allows bed_single for this 0.95x1.95 footprint; confirming the type verifies the anchor and closes the misread F9. |
| 2290 | 2 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_134: no_overlap, score: plausibility 80 -> 70 (G4 f_L0_134: nightstand f_L0_134 of bed_double f_L0_069: -0.06 m from the bed side (needs ≤ 0.30 m); G5 f_L0_069: bed_double f_L0_069: 0.58 m free along the right side, needs ≥ 0.60 m) | Nudge the bed 0.06 m toward the window wall to gain the missing 0.06 m of left-side clearance (G5). |
| 2292 | 2 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_135: no_overlap, score: plausibility 80 -> 67 (G4 f_L0_069: bed_double f_L0_069: no nightstand on the free left side of the head (0.49 m free); G4 f_L0_135: nightstand f_L0_135 of bed_double f_L0_069: -0.06 m from the bed side (needs ≤ 0.30 m); G5 f_L0_069: bed_double f_L0_069: 0.49 m free along the left side, needs ≥ 0.60 m) | Nudge the bed 0.06 m toward the wardrobe wall to gain the missing 0.06 m of left-side clearance (G5). |
| 2294 | 2 | move_piece | f_L0_144 | acceptance: finding G13:f_L0_144 is still there after the edit (wardrobe f_L0_144: 0.13 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along its wall to open the 0.80 m front clearance (G13). |
| 2308 | 2 | fix_fixture | f_L0_188 | fixture_place: f_L0_188: no valid spot within 0.50 m (it stands 0.05 m² outside the room, in door d_L0_017) | Washbasin is drawn through wall w_L0_037 (S2) and into door d_L0_017's swing (R3); move it up to 0.5 m to the nearest valid spot inside the room, which also resolves its orientation (F4) and clearance (G10) issues. |
| 2313 | 2 | fix_fixture | f_L0_077 | fixture_place: f_L0_077: no valid spot within 0.50 m (it stands 0.11 m² outside the room) | Machine cuts wall w_L0_152 by 0.15 m and reaches 0.11 m² through the outline; nudge it to a valid spot inside the room. |
| 2320 | 2 | set_front | f_L0_195 | acceptance: finding F4:f_L0_195 is still there after the edit (washbasin faces a wall 0.22 m in front of it) | Washbasin front faces a wall 0.22 m ahead; its back is on the wall at 230.5°, so the front must face the open room at 50.5° to clear the F4 orientation error. |
| 2323 | 2 | fix_fixture | f_L0_186 | memory: the same edit was rejected in round 1: fixture_place: f_L0_186: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_005) | Bathtub f_L0_186 has only 0.10 m clear in front (needs ≥ 0.53 m); shrink to a real product size that fits the bay to restore the clearance. |
| 2325 | 2 | fix_fixture | f_L0_186 | fixture_size: f_L0_186: the drawn 1.55 x 0.75 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Bathtub f_L0_186 has only 0.10 m clear in front (needs ≥ 0.53 m); shrink to a real 1.50×0.70 product size that fits the bay to restore the clearance. |
| 2326 | 2 | fix_fixture | f_L0_184 | memory: the same edit was rejected in round 1: fixture_place: f_L0_184: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_002) | Bathtub drawn 1.55 m long in a 0.9 m bay (w_L0_094); shrink to the nearest real product size that fits the bay to restore the 0.53 m front clearance (G10) and clear the door swing (R3). |
| 2327 | 2 | fix_fixture | f_L0_186 | no_spot: f_L0_186: the code searched every spot within 0.5 m and found none (fixture_place: f_L0_186: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_005) (round 1)); do not try centres: the finding stays for review | Bathtub f_L0_186 has only 0.10 m clear in front (needs ≥ 0.53 m); nudge 0.20 m toward the bottom wall to open the front clearance. |
| 2329 | 2 | fix_fixture | f_L0_184 | fixture_size: f_L0_184: the drawn 1.55 x 0.75 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Bathtub drawn 1.55 m long in a 0.9 m bay (w_L0_094); shrink to a real 1.50×0.70 product size that fits the bay to restore the 0.53 m front clearance (G10) and clear the door swing (R3). |
| 2330 | 2 | fix_fixture | f_L0_184 | no_spot: f_L0_184: the code searched every spot within 0.5 m and found none (fixture_place: f_L0_184: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_002) (round 1)); do not try centres: the finding stays for review | Nudge the bathtub 0.20 m toward the far wall (within the 0.5 m allowance) to open the 0.53 m front clearance (G10) and clear the door d_L0_002 swing (R3). |
| 2331 | 2 | fix_fixture | f_L0_185 | memory: the same edit was rejected in round 1: fixture_place: f_L0_185: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_008) | Bathtub f_L0_185 has only 0.10 m clear in front (needs ≥ 0.53 m); shrink to a real product size that fits the bay. |
| 2332 | 2 | fix_fixture | f_L0_185 | fixture_size: f_L0_185: the drawn 1.55 x 0.75 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Bathtub f_L0_185 has only 0.10 m clear in front (needs ≥ 0.53 m); shrink to a real product size that fits the bay. |
| 2335 | 2 | set_entrance | ext_6 | exists: 'ext_6' is no outside door of site.entrances | Add steps at the entrance door so the path connects the ground level to the door. |
| 2533 | 3 | relayout_room | r_L0_ebeveyn_odasi_4 | acceptance: finding F3:f_L0_141 is still there after the edit (bed_double: the headboard stands in the room (0.08 m off)); 3 more kept | Re-solve the room around the drawn sleeping_double group anchored on f_L0_141 so the headboard sits on a wall, the bed faces away from the wall, and the right use zone gains a 0.60 m walkway from the door. |
| 2535 | 3 | relayout_room | r_L0_ebeveyn_odasi_4 | acceptance: finding F3:f_L0_141 is still there after the edit (bed_double: the headboard stands in the room (0.08 m off)); 3 more kept | Try the second solver candidate to re-solve the room around the drawn sleeping_double group anchored on f_L0_141 so the headboard sits on a wall, the bed faces away from the wall, and the right use zone gains a 0.60 m walkway from the door. |
| 2537 | 3 | fix_fixture | f_L0_206 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_206 is still there after the edit (fridge f_L0_206 (1.80 m) stands in front of window win_L0_061 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_016 (F7) and stands in front of window win_L0_025 (G12); let the code find the nearest valid spot. |
| 2539 | 3 | fix_fixture | f_L0_200 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_200 is still there after the edit (fridge f_L0_200 (1.80 m) stands in front of window win_L0_053 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_010 and stands in front of window win_L0_011; reposition up to 0.5 m to clear the door swing and window. |
| 2540 | 3 | fix_fixture | f_L0_206 | f_L0_206: no_overlap | Nudge fridge 0.35 m away from door o_L0_016 (F7) and off window win_L0_025 (G12); a different spot than the previously rejected ones. |
| 2541 | 3 | fix_fixture | f_L0_202 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_202 is still there after the edit (fridge f_L0_202 (1.80 m) stands in front of window win_L0_052 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_007 and stands in front of window win_L0_008; let the code find the nearest valid spot within 0.5 m. |
| 2542 | 3 | retype_piece | f_L0_111 | memory: the same edit was rejected in round 1: no_change: f_L0_111 is already a table_dining | Vector geometry shows a table with chairs drawn around it; the 'hole in the center' and AI's sofa reading are a misread, confirming table_dining. |
| 2543 | 3 | fix_fixture | f_L0_200 | fixture_place: f_L0_200 at [2.80, 8.55] is still through a wall or in a door swing; without center the code searches every spot within 0.50 m: when that search found no valid spot, none exists, do not try centres; the finding stays for review | Shift fridge 0.4 m along the wall away from door o_L0_010 to clear the door swing and the window band. |
| 2544 | 3 | fix_fixture | f_L0_206 | f_L0_206: no_overlap | Nudge fridge 0.3 m down along the left wall, away from door o_L0_016 (F7) and off window win_L0_025 (G12); a spot not tried before. |
| 2545 | 3 | move_piece | f_L0_108 | acceptance: finding G12:f_L0_108 is still there after the edit (tv_unit f_L0_108 (1.30 m) stands in front of window win_L0_012 (sill 0.90 m + 0.05)) | Shift TV unit 0.22 m along the wall toward the corner to clear windows win_L0_011 and win_L0_012. |
| 2547 | 3 | fix_fixture | f_L0_206 | max_tries: f_L0_206 was edited 3 times in this round | Nudge fridge 0.2 m down along the left wall, away from door o_L0_016 (F7) and off window win_L0_025 (G12); a spot not tried before. |
| 2548 | 3 | move_piece | f_L0_114 | snap: f_L0_114: no free place on wall w_L0_082 (doors, windows, at most 1.2 m from the drawn place) | Move the TV unit off the window line onto the left wall span s5, clearing windows win_L0_007 and win_L0_008. |
| 2549 | 3 | move_piece | f_L0_203 | drawn_lock: f_L0_203: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Move the floor lamp away from window win_L0_050 line to clear the G12 finding. |
| 2550 | 3 | move_piece | f_L0_125 | drawn_lock: f_L0_125: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.62 m) | Slide tv_unit 0.61 m down along the left wall to clear windows win_L0_024 and win_L0_025 (G12 x2). |
| 2551 | 3 | move_piece | f_L0_108 | acceptance: finding G12:f_L0_108 is still there after the edit (tv_unit f_L0_108 (1.30 m) stands in front of window win_L0_012 (sill 0.90 m + 0.05)) | Snap TV unit back onto the wall and shift it along the wall toward the corner to clear windows win_L0_011 and win_L0_012 (wall-snap allowance 1.2 m). |
| 2552 | 3 | move_piece | f_L0_203 | f_L0_203: no_overlap, f_L0_209: no_overlap | Move the floor lamp 0.3 m away from window win_L0_050 line to clear the G12 finding. |
| 2553 | 3 | move_piece | f_L0_113 | f_L0_209: no_overlap | Move the chair 0.29 m away from the wall behind to give the required 0.81 m clearance. |
| 2554 | 3 | move_piece | f_L0_125 | memory: the same edit was rejected in round 2: snap: f_L0_125: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Snap tv_unit back onto the south wall (span s0) to clear windows win_L0_024 and win_L0_025 (G12 x2); wall snap allows up to 1.2 m. |
| 2555 | 3 | fix_fixture | f_L0_010 | memory: the same edit was rejected in round 1: fixture_place: f_L0_010: no valid spot within 0.50 m (it stands 0.29 m² outside the room) | Kitchen aisle in front of the counter is 0.06 m (needs ≥ 0.90 m); the counter also cuts wall w_L0_142 and reaches 0.29 m² outside the room outline, so it must be pulled back to a valid spot. |
| 2556 | 3 | move_piece | f_L0_108 | acceptance: finding G12:f_L0_108 is still there after the edit (tv_unit f_L0_108 (1.30 m) stands in front of window win_L0_012 (sill 0.90 m + 0.05)) | Snap TV unit onto the wall and shift it further along toward the corner (offset 2.6 m) to clear windows win_L0_011 and win_L0_012. |
| 2557 | 3 | move_piece | f_L0_125 | snap: f_L0_125: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Snap tv_unit back onto the south wall (span s0, offset 0.9 m) to clear windows win_L0_024 and win_L0_025 (G12 x2); a different offset than the rejected 1.35 m. |
| 2558 | 3 | move_piece | f_L0_113 | f_L0_209: no_overlap | Move the chair 0.24 m away from the wall behind to give the required 0.81 m clearance. |
| 2559 | 3 | move_piece | f_L0_203 | acceptance: finding G12:f_L0_203 is still there after the edit (floor_lamp f_L0_203 (1.60 m) stands in front of window win_L0_050 (sill 0.90 m + 0.05)) | Move the floor lamp 0.22 m away from window win_L0_050 line to clear the G12 finding. |
| 2560 | 3 | move_piece | f_L0_108 | max_tries: f_L0_108 was edited 3 times in this round | Snap TV unit onto the wall and shift it along toward the lower end (offset 1.8 m) to clear windows win_L0_011 and win_L0_012. |
| 2561 | 3 | move_piece | f_L0_125 | max_tries: f_L0_125 was edited 3 times in this round | Slide tv_unit 0.31 m down along the left wall to clear windows win_L0_024 and win_L0_025 (G12 x2); within the 0.223 m allowance plus wall snap. |
| 2562 | 3 | move_piece | f_L0_201 | f_L0_201: no_overlap, score: plausibility -20 -> -30 (F9 f_L0_201: floor_lamp f_L0_201 overlaps table_dining f_L0_105 by 0.08 m²) | Move floor lamp 0.28 m away from window win_L0_051 to clear the window band. |
| 2563 | 3 | move_piece | f_L0_207 | drawn_lock: f_L0_207: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Slide floor_lamp 0.32 m down along the right wall to clear window win_L0_063 (G12); within the 0.3 m allowance. |
| 2564 | 3 | move_piece | f_L0_113 | acceptance: finding G6:f_L0_113 is still there after the edit (chair f_L0_113: 0.43 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair 0.14 m away from the wall behind to give the required 0.81 m clearance. |
| 2565 | 3 | move_piece | f_L0_203 | max_tries: f_L0_203 was edited 3 times in this round | Move the floor lamp 0.27 m away from window win_L0_050 line to clear the G12 finding. |
| 2566 | 3 | move_piece | f_L0_201 | f_L0_201: no_overlap, score: plausibility -20 -> -30 (F9 f_L0_201: floor_lamp f_L0_201 overlaps table_dining f_L0_105 by 0.07 m²) | Move floor lamp 0.18 m away from window win_L0_051 to clear the window band without overlapping the dining table. |
| 2567 | 3 | move_piece | f_L0_207 | memory: the same edit was rejected in round 1: f_L0_207: no_overlap; f_L0_211: no_overlap | Slide floor_lamp 0.3 m down along the right wall to clear window win_L0_063 (G12); within the 0.3 m allowance. |
| 2569 | 3 | move_piece | f_L0_201 | acceptance: finding G12:f_L0_201 is still there after the edit (floor_lamp f_L0_201 (1.60 m) stands in front of window win_L0_051 (sill 0.90 m + 0.05)) | Move floor lamp 0.17 m away from window win_L0_051 to clear the window band without overlapping the dining table. |
| 2570 | 3 | move_piece | f_L0_207 | f_L0_207: no_overlap, f_L0_211: no_overlap | Slide floor_lamp 0.27 m down along the right wall to clear window win_L0_063 (G12); a spot not tried before. |
| 2571 | 3 | move_piece | f_L0_107 | score: plausibility -20 -> -40 (F4 f_L0_107: chair does not face its group (f_L0_105, f_L0_153); G6 f_L0_107: chair f_L0_107 is 48° off the table f_L0_105 (needs ≤ 45°)) | Move chair 0.06 m away from the wall behind to increase clearance from 0.43 m toward the required 0.81 m. |
| 2573 | 3 | move_piece | f_L0_107 | score: plausibility -20 -> -40 (F4 f_L0_107: chair does not face its group (f_L0_105, f_L0_153); G6 f_L0_107: chair f_L0_107 is 54° off the table f_L0_105 (needs ≤ 45°)) | Move chair 0.11 m away from the wall behind to increase clearance from 0.43 m toward the required 0.81 m while keeping it facing the table. |
| 2580 | 3 | move_group | r_L0_ebeveyn_odasi_m_k_a_2.storage | drawn_lock: r_L0_ebeveyn_odasi_m_k_a_2.storage: drawn pieces (f_L0_144) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the wardrobe to the opposite free wall span s3 so its front faces open room space, clearing the 0.80 m G13 clearance that the w_L0_067 wall cannot provide. |
| 2582 | 3 | move_piece | f_L0_058 | drawn_lock: f_L0_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the bed 0.30 m toward the foot wall to open the right use zone for a 0.60 m walkway from door o_L0_003 (G11). |
| 2585 | 3 | move_piece | f_L0_144 | f_L0_135: no_overlap, f_L0_144: no_overlap, score: plausibility 80 -> 60 (F3 f_L0_144: wardrobe: its back is not on a wall (0.10 m off); F9 f_L0_144: wardrobe f_L0_144 overlaps nightstand f_L0_135 by 0.06 m²; G5 f_L0_069: bed_double f_L0_069: 0.25 m free along the left side, needs ≥ 0.60 m; G13 f_L0_144: wardrobe f_L0_144: 0.25 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.29 m away from the bed to open the 0.80 m front clearance required by G13. |
| 2586 | 3 | move_piece | f_L0_058 | f_L0_058: no_overlap, f_L0_100: no_overlap, score: plausibility 70 -> 40 (F9 f_L0_100: nightstand f_L0_100 overlaps bed_double f_L0_058 by 0.11 m²; G4 f_L0_100: nightstand f_L0_100 of bed_double f_L0_058: -0.10 m from the bed side (needs ≤ 0.30 m); G5 f_L0_058: bed_double f_L0_058: 0.48 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.29 m toward the foot wall to open the right use zone for a 0.60 m walkway from door o_L0_003 (G11). |
| 2587 | 3 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_134: no_overlap, score: plausibility 80 -> 50 (F3 f_L0_069: bed_double: the headboard stands in the room (0.06 m off); G5 f_L0_069: bed_double f_L0_069: 0.55 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.06 m right to open the left-side clearance from 0.54 m to ≥ 0.60 m for G5. |
| 2590 | 3 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_134: no_overlap, score: plausibility 80 -> 50 (F3 f_L0_069: bed_double: the headboard stands in the room (0.10 m off); G5 f_L0_069: bed_double f_L0_069: 0.55 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.10 m right to open the left-side clearance from 0.54 m to ≥ 0.60 m for G5. |
| 2592 | 3 | move_piece | f_L0_058 | memory: the same edit was rejected in round 3: f_L0_058: no_overlap; f_L0_100: no_overlap; score: plausibility 70 -> 40 (F9 f_L0_100: nightstand f_L0_100 overlaps bed_double f_L0_058 by 0.11 m²; G4 f_L0_100: nightstand f_L0_100 of bed_double f_L0_058: -0.10 m from the bed side (needs ≤ 0.30 m); G5 f_L0_058: bed_double f_L0_058: 0.48 m free along | Shift the bed 0.29 m toward the foot wall to open the right use zone for a 0.60 m walkway from door o_L0_003 (G11). |
| 2593 | 3 | move_piece | f_L0_069 | f_L0_069: no_overlap, f_L0_134: no_overlap, score: plausibility 80 -> 50 (F3 f_L0_069: bed_double: the headboard stands in the room (0.14 m off); G5 f_L0_069: bed_double f_L0_069: 0.55 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.14 m right to open the left-side clearance from 0.54 m to ≥ 0.60 m for G5. |
| 2595 | 3 | move_piece | f_L0_069 | max_tries: f_L0_069 was edited 3 times in this round | Shift the bed 0.19 m right to open the left-side clearance from 0.54 m to ≥ 0.60 m for G5. |
| 2596 | 3 | move_piece | f_L0_058 | max_tries: f_L0_058 was edited 3 times in this round | Shift the bed 0.28 m toward the foot wall to open the right use zone for a 0.60 m walkway from door o_L0_003 (G11). |
| 2626 | 3 | fix_fixture | f_L0_187 | memory: the same edit was rejected in round 1: fixture_place: f_L0_187: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_011) | Drawn bathtub is 1.55 m long but the room's bay is only ~1.45 m; shrink to the nearest real product size that fits the bay to restore the 0.53 m front clearance and clear the door swing. |
| 2627 | 3 | fix_fixture | f_L0_186 | no_spot: f_L0_186: the code searched every spot within 0.5 m and found none (fixture_place: f_L0_186: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_005) (round 1)); do not try centres: the finding stays for review | Shift the bathtub 0.15 m toward its back wall to clear the door d_L0_005 swing (R3) and gain front clearance toward the 0.53 m needed (G10). |
| 2628 | 3 | fix_fixture | f_L0_187 | fixture_size: f_L0_187: the drawn 1.55 x 0.75 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Shrink the drawn 1.55 m bathtub to a real 1.40 m product size that fits the ~1.45 m bay, restoring the 0.53 m front clearance and clearing the door swing. |
| 2631 | 3 | fix_fixture | f_L0_187 | no_spot: f_L0_187: the code searched every spot within 0.5 m and found none (fixture_place: f_L0_187: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_011) (round 1)); do not try centres: the finding stays for review | Nudge the bathtub 0.15 m down (away from the door swing at its top-right corner) to clear the door d_L0_011 swing zone. |
| 2632 | 3 | fix_fixture | f_L0_184 | memory: the same edit was rejected in round 1: fixture_place: f_L0_184: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_002) | Bathtub drawn 1.55 m long in a 0.9 m bay (w_L0_094) and overlapping the door swing; shrink to the nearest real product size that fits the bay. |
| 2634 | 3 | fix_fixture | f_L0_184 | fixture_size: f_L0_184: the drawn 1.55 x 0.75 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Shrink bathtub to a real product size (1.40 x 0.70 m) that fits the 0.9 m bay and clears the door swing. |
| 2635 | 3 | rotate_piece | f_L0_077 | drawn_lock: f_L0_077: the new front does not fix the error (its front faces a wall) | Face the washing machine south into the room instead of east into wall w_L0_152, clearing F4. |
| 2833 | 4 | fix_fixture | f_L0_200 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_200 is still there after the edit (fridge f_L0_200 (1.80 m) stands in front of window win_L0_053 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_010 (F7) and stands in front of window win_L0_011 (G12); reposition up to 0.5 m to clear both. |
| 2834 | 4 | move_piece | f_L0_141 | acceptance: finding F4:f_L0_141 is still there after the edit (bed_double faces a wall 0.13 m in front of it); 2 more kept | Snap the bed's headboard onto free wall span s5 so the headboard sits on the wall (F3), the front faces into the room (F4), and foot/right clearance and door walkway improve (G5, G11). |
| 2835 | 4 | fix_fixture | f_L0_200 | f_L0_200: no_overlap | Fridge blocks door o_L0_010 (F7) and stands in front of window win_L0_011 (G12); shift 0.3 m toward the room to clear the door swing and window. |
| 2838 | 4 | fix_fixture | f_L0_200 | fixture_place: f_L0_200 at [2.80, 8.45] is still through a wall or in a door swing; without center the code searches every spot within 0.50 m: when that search found no valid spot, none exists, do not try centres; the finding stays for review | Fridge blocks door o_L0_010 (F7) and stands in front of window win_L0_011 (G12); shift 0.3 m the other way to clear the door swing and window. |
| 2839 | 4 | fix_fixture | f_L0_206 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_206 is still there after the edit (fridge f_L0_206 (1.80 m) stands in front of window win_L0_061 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_016; let the code find the nearest valid spot off the door swing. |
| 2840 | 4 | fix_fixture | f_L0_202 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L0_202 is still there after the edit (fridge f_L0_202 (1.80 m) stands in front of window win_L0_052 (sill 0.90 m + 0.05)) | Fridge blocks door o_L0_007; let the code find the nearest valid spot within 0.5 m. |
| 2841 | 4 | move_piece | f_L0_141 | drawn_lock: f_L0_141: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.37 m) | Shift the bed 0.37 m right so its headboard back sits on wall w_L0_121 (F3) and its right side gains clearance toward the door walkway (G5, G11). |
| 2842 | 4 | move_piece | f_L0_201 | drawn_lock: f_L0_201: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Floor lamp blocks window win_L0_051 (G12); move it 0.32 m away from the window into the room, clear of the dining table. |
| 2843 | 4 | fix_fixture | f_L0_202 | fixture_place: f_L0_202 at [2.80, 4.90] is still through a wall or in a door swing; without center the code searches every spot within 0.50 m: when that search found no valid spot, none exists, do not try centres; the finding stays for review | Shift fridge 0.35 m away from door o_L0_007 to clear the opening, staying within the 0.5 m allowance. |
| 2844 | 4 | move_piece | f_L0_201 | f_L0_201: no_overlap, f_L0_208: no_overlap | Floor lamp blocks window win_L0_051 (G12); move it 0.27 m away from the window into the room, clear of the dining table. |
| 2845 | 4 | move_piece | f_L0_141 | f_L0_141: doors_free, f_L0_141: inside_room, score: plausibility 20 -> -6 (F3 f_L0_141: bed_double: the headboard stands in the room (0.36 m off); F4 f_L0_141: bed_double faces a wall 0.00 m in front of it; F9 f_L0_141: bed_double reaches 0.29 m² through the room outline, up to 0.226 m deep; R3 d_L0_023: door d_L0_023 swings into f_L0_141 on one hinge side; the other hinge side is free) | Shift the bed 0.3 m right so its headboard back sits on wall w_L0_121 (F3) and its right side gains clearance toward the door walkway (G5, G11). |
| 2846 | 4 | move_piece | f_L0_201 | drawn_lock: f_L0_201: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.33 m) | Floor lamp blocks window win_L0_051 (G12); move it 0.33 m... no, 0.33 m is over; try 0.3 m south into the room, clear of the dining table. |
| 2847 | 4 | move_piece | f_L0_141 | max_tries: f_L0_141 was edited 3 times in this round | Snap the bed's headboard onto the free south wall span s6 (w_L0_036) so the headboard sits on the wall (F3), the front faces north into the room (F4), and the foot/right clearance and door walkway improve (G5, G11). |
| 2848 | 4 | move_piece | f_L0_201 | memory: the same edit was rejected in round 2: drawn_lock: f_L0_201: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Floor lamp blocks window win_L0_051 (G12); move it 0.3 m south into the room, clear of the dining table. |
| 2849 | 4 | move_piece | f_L0_201 | max_tries: f_L0_201 was edited 3 times in this round | Floor lamp blocks window win_L0_051 (G12); move it 0.29 m south into the room, clear of the dining table. |
| 2850 | 4 | move_piece | f_L0_070 | f_L0_070: clearance_ok, score: plausibility 20 -> -30 (F3 f_L0_070: bed_double: the headboard stands in the room (0.08 m off); G5 f_L0_070: bed_double f_L0_070: 0.39 m free at the foot, needs ≥ 0.60 m; G11 f_L0_070: bed_double f_L0_070: its left use zone is not reached by a 0.60 m walkway from door d_L0_023) | Nudge the drawn bed 0.3 m toward the right wall to open ≥0.60 m along its left side for the nightstand and walkway (G5). |
| 2851 | 4 | relayout_room | r_L0_ebeveyn_odasi_4 | memory: the same edit was rejected in round 3: acceptance: finding F3:f_L0_141 is still there after the edit (bed_double: the headboard stands in the room (0.08 m off)); 3 more kept | Re-solve the room around the drawn sleeping_double group anchored on f_L0_141 so the headboard sits on a wall and the bed is oriented away from it, improving foot/right clearance and the door walkway. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| S2 | minor | f_L0_007 | r_L0_yasama | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_132 | r_L0_ebeveyn_odasi_m_k_a | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_133 | r_L0_ebeveyn_odasi_m_k_a | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L0_068 | r_L0_ebeveyn_odasi_m_k_a | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_073 | r_L0_oda_01 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| camera_blocked | major | cam_r_L0_yasama_2_2 | r_L0_yasama_2 | cameras | replayed_camera | 1, 2, 3, 4 | the camera is replayed from the baseline run (set 1): its pose is frozen for the before/after comparison (docs/milestone13.md §7, decision of 17 Oct 2026), so set_camera and remove_camera are refused for it; the finding is reported (add_camera with a new view id may add another view) |
| camera_blocked | major | cam_r_L0_yasama_3_2 | r_L0_yasama_3 | cameras | replayed_camera | 1, 2, 3, 4 | the camera is replayed from the baseline run (set 1): its pose is frozen for the before/after comparison (docs/milestone13.md §7, decision of 17 Oct 2026), so set_camera and remove_camera are refused for it; the finding is reported (add_camera with a new view id may add another view) |
| camera_blocked | major | cam_r_L0_yasama_5_2 | r_L0_yasama_5 | cameras | replayed_camera | 1, 2, 3, 4 | the camera is replayed from the baseline run (set 1): its pose is frozen for the before/after comparison (docs/milestone13.md §7, decision of 17 Oct 2026), so set_camera and remove_camera are refused for it; the finding is reported (add_camera with a new view id may add another view) |
| camera_blocked | major | cam_r_L0_yasama_6_1 | r_L0_yasama_6 | cameras | replayed_camera | 1, 2, 3, 4 | the camera is replayed from the baseline run (set 1): its pose is frozen for the before/after comparison (docs/milestone13.md §7, decision of 17 Oct 2026), so set_camera and remove_camera are refused for it; the finding is reported (add_camera with a new view id may add another view) |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 2 | building | cut | 1 | 35332 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | change | by (rule) | reason |
|---|---|---|---|---|---|---|---|
| f_L0_003 | piece | unknown | - | inferred | - | - | drawn on the 'MYD - BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L0_004 | piece | unknown | r_L0_hava_bacasi | inferred | - | - | drawn on the 'MYD - BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L0_012 | piece | unknown | r_L0_oda_5 | inferred | - | - | drawn on the 'MYD - BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L0_013 | piece | unknown | - | inferred | - | - | drawn on the 'MYD - BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L0_033 | piece | unknown | r_L0_banyo_6 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_034 | piece | unknown | r_L0_banyo_8 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_035 | piece | unknown | r_L0_banyo_8 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_036 | piece | unknown | r_L0_banyo_6 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_037 | piece | unknown | r_L0_banyo_3 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_038 | piece | unknown | r_L0_banyo_3 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_039 | piece | unknown | r_L0_banyo_4 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_040 | piece | unknown | r_L0_banyo_4 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_041 | piece | unknown | r_L0_banyo_5 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_042 | piece | unknown | r_L0_banyo | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_043 | piece | unknown | r_L0_banyo_7 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_044 | piece | unknown | r_L0_banyo_2 | inferred | - | - | 0.25 x 0.12 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_045 | piece | unknown | r_L0_banyo | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_046 | piece | unknown | r_L0_banyo_5 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_047 | piece | unknown | r_L0_banyo_2 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_048 | piece | unknown | r_L0_banyo_7 | inferred | - | - | 0.25 x 0.08 m fits no type and is smaller than 0.3 m both ways: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L0_053 | piece | washing_machine | r_L0_banyo_6 | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_054 | piece | shower | r_L0_banyo_3 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 1.07 x 0.80 m -> 1.00 x 0.80 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn shower 1.07 x 0.80 m runs 5 cm past the walls of its bay (clear 1.02 x 0.80 m): the nearest real product that fits, 1.00 x 0.80 m (plan crop recognition/reading/f_L0_054_ctx.png) |
| f_L0_056 | piece | toilet | r_L0_banyo_3 | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_057 | piece | washing_machine | r_L0_banyo_3 | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_060 | piece | toilet | r_L0_banyo_4 | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_073 | piece | bed_single | r_L0_oda_01 | inferred | - | - | front: standing in a corner: its short side on the wall is the back |
| f_L0_074 | piece | washing_machine | r_L0_giris_holu | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Front at 180° faced wall w_L0_088 0.00 m ahead; 0° also faces a wall; rotate to 90° so the front faces into the room toward the free span s0 (into_room_deg 90°) to clear F4. |
| f_L0_075 | piece | washing_machine | r_L0_giris_holu_4 | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_076 | piece | washing_machine | r_L0_giris_holu_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Front faced the wall at x≈29.75 (0°); turning 270° (south) faces it into the room, fixing F4. |
| f_L0_077 | piece | washing_machine | r_L0_giris_holu_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Face the washing machine north into the open room space, away from the east wall it is embedded in, clearing F4. |
| f_L0_082 | piece | washing_machine | r_L0_banyo_8 | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_089 | piece | washbasin | r_L0_banyo_6 | inferred | - | - | washbasin: r_L0_banyo_6.bathroom_set (anchor f_L0_051) misses washbasin, and the type's product range fits 1.00 x 0.50 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_090 | piece | washbasin | r_L0_banyo_8 | inferred | - | - | washbasin: r_L0_banyo_8.bathroom_set (anchor f_L0_052) misses washbasin, and the type's product range fits 1.00 x 0.50 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_098 | piece | wardrobe | r_L0_ebeveyn_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the wardrobe 0.30 m toward its wall to open 0.73 m in front, approaching the 0.80 m needed (G13). |
| f_L0_099 | piece | nightstand | r_L0_ebeveyn_odasi_2 | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_2.sleeping_double (anchor f_L0_058) misses nightstand; r_L0_ebeveyn_odasi_2.sleeping_double (anchor f_L0_058) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_100 | piece | nightstand | r_L0_ebeveyn_odasi_2 | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_2.sleeping_double (anchor f_L0_058) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_103 | piece | wardrobe | r_L0_oda_01 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Confirm the drawn wardrobe type: the source shows a large closed wardrobe, not a small open-topped cabinet. (plan crop recognition/crops/sym_L0_019_ctx.png) |
| f_L0_104 | piece | unknown | r_L0_oda_01 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | The 0.40 x 0.20 m drawn symbol is a door swing arc (dashed rectangle with a quarter-circle arc), not furniture; AI passes returned floor_lamp/unknown. |
| f_L0_108 | piece | tv_unit | r_L0_yasama_5 | inferred, adjusted_by_ai | size 1.80 x 0.25 m -> 1.80 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_114 | piece | tv_unit | r_L0_yasama_3 | inferred, adjusted_by_ai | size 1.80 x 0.25 m -> 1.80 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_120 | piece | tv_unit | r_L0_yasama_6 | inferred, adjusted_by_ai | size 1.80 x 0.25 m -> 1.80 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_125 | piece | tv_unit | r_L0_yasama_2 | inferred, adjusted_by_ai | size 1.80 x 0.25 m -> 1.80 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_128 | piece | nightstand | r_L0_ebeveyn_odasi_6 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Confirm the drawn nightstand next to the bed so it is built as a nightstand instead of rendering as a bare lamp (F1 v:r1-v32:1). |
| f_L0_129 | piece | nightstand | r_L0_ebeveyn_odasi_6 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Confirm the second drawn nightstand on the other side of the bed so it is built (F1 v:r1-v32:2). |
| f_L0_130 | piece | nightstand | r_L0_ebeveyn_odasi_5 | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_5.sleeping_double (anchor f_L0_067) misses nightstand; r_L0_ebeveyn_odasi_5.sleeping_double (anchor f_L0_067) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_131 | piece | nightstand | r_L0_ebeveyn_odasi_5 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Confirm the second nightstand's type so it is built in the render, matching the drawn nightstand on both sides of the bed. |
| f_L0_132 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_m_k_a.sleeping_double (anchor f_L0_068) misses nightstand; r_L0_ebeveyn_odasi_m_k_a.sleeping_double (anchor f_L0_068) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_133 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_m_k_a.sleeping_double (anchor f_L0_068) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_134 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a_2 | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_m_k_a_2.sleeping_double (anchor f_L0_069) misses nightstand; r_L0_ebeveyn_odasi_m_k_a_2.sleeping_double (anchor f_L0_069) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_135 | piece | nightstand | r_L0_ebeveyn_odasi_m_k_a_2 | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_m_k_a_2.sleeping_double (anchor f_L0_069) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_136 | piece | nightstand | r_L0_ebeveyn_odasi_4 | inferred | - | - | nightstand: r_L0_ebeveyn_odasi_4.sleeping_double (anchor f_L0_070) misses nightstand; r_L0_ebeveyn_odasi_4.sleeping_double (anchor f_L0_070) misses nightstand, and the type's product range fits 0.40 x 0.38 m (the only missing member of that size) |
| f_L0_138 | piece | sofa_corner | r_L0_yasama_8 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_139 | piece | sofa_corner | r_L0_yasama_7 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_141 | piece | bed_double | r_L0_ebeveyn_odasi_4 | adjusted_by_ai | size 1.22 x 2.13 m -> 1.40 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 1.22 x 2.13 m is outside its product range (width 1.22 m is 10 % outside 1.35-2 m; nearest real product 1.40 x 2.00 m); nearest real product 1.40 x 2.00 x 1.00 m (double 140 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_143 | piece | wardrobe | r_L0_ebeveyn_odasi_m_k_a | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 1.90 x 0.60 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_144 | piece | wardrobe | r_L0_ebeveyn_odasi_m_k_a_2 | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 1.90 x 0.60 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_145 | piece | shower | r_L0_banyo_4 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 0.85 x 1.02 m -> 0.80 x 0.90 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn shower 0.85 x 1.02 m runs 5 cm past the walls of its bay (clear 0.85 x 0.97 m): the nearest real product that fits, 0.80 x 0.90 m (plan crop recognition/crops/sym_L0_053_ctx.png) |
| f_L0_147 | piece | washbasin | r_L0_banyo_7 | inferred | - | - | washbasin: r_L0_banyo_7.bathroom_set (anchor f_L0_078) misses washbasin, and the type's product range fits 0.80 x 0.50 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_148 | piece | washbasin | r_L0_banyo_2 | inferred | - | - | washbasin: r_L0_banyo_2.bathroom_set (anchor f_L0_079) misses washbasin, and the type's product range fits 0.80 x 0.50 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_149 | piece | washbasin | r_L0_banyo_5 | inferred | - | - | washbasin: r_L0_banyo_5.bathroom_set (anchor f_L0_080) misses washbasin, and the type's product range fits 0.80 x 0.50 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_150 | piece | washbasin | r_L0_banyo | inferred | - | - | washbasin: r_L0_banyo.bathroom_set (anchor f_L0_081) misses washbasin, and the type's product range fits 0.80 x 0.50 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_151 | piece | table_coffee | r_L0_yasama_6 | inferred | - | - | table_coffee: r_L0_yasama_6.seating (anchor f_L0_210) misses table_coffee, and the type's product range fits 0.80 x 0.80 m (the only missing member of that size) |
| f_L0_152 | piece | table_coffee | r_L0_yasama_2 | inferred | - | - | table_coffee: r_L0_yasama_2.seating (anchor f_L0_211) misses table_coffee, and the type's product range fits 0.80 x 0.80 m (the only missing member of that size) |
| f_L0_153 | piece | table_coffee | r_L0_yasama_5 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Rebuild the coffee table from a standard library model to remove the circular hole rendering error on its top. |
| f_L0_154 | piece | table_coffee | r_L0_yasama_8 | inferred | - | - | table_coffee: r_L0_yasama_8.seating (anchor f_L0_138) misses table_coffee, and the type's product range fits 0.80 x 0.80 m (the only missing member of that size) |
| f_L0_155 | piece | table_coffee | r_L0_yasama_7 | inferred | - | - | table_coffee: r_L0_yasama_7.seating (anchor f_L0_139) misses table_coffee, and the type's product range fits 0.80 x 0.80 m (the only missing member of that size) |
| f_L0_156 | piece | table_coffee | r_L0_yasama_3 | inferred | - | - | table_coffee: r_L0_yasama_3.seating (anchor f_L0_209) misses table_coffee, and the type's product range fits 0.80 x 0.80 m (the only missing member of that size) |
| f_L0_162 | piece | tv_unit | r_L0_yasama_7 | inferred, adjusted_by_ai | size 1.80 x 0.25 m -> 1.80 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_163 | piece | tv_unit | r_L0_yasama_8 | inferred, adjusted_by_ai | size 1.80 x 0.25 m -> 1.80 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.80 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.80 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_179 | piece | shower | r_L0_banyo_6 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 0.90 x 0.97 m -> 0.90 x 0.90 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn shower 0.90 x 0.97 m runs 4 cm past the walls of its bay (clear 0.90 x 0.93 m): the nearest real product that fits, 0.90 x 0.90 m (plan crop recognition/crops/sym_L0_087_ctx.png) |
| f_L0_180 | piece | shower | r_L0_banyo_8 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 0.90 x 0.97 m -> 0.90 x 0.90 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn shower 0.90 x 0.97 m runs 4 cm past the walls of its bay (clear 0.90 x 0.93 m): the nearest real product that fits, 0.90 x 0.90 m (plan crop recognition/crops/sym_L0_088_ctx.png) |
| f_L0_181 | piece | stove | r_L0_yasama_8 | inferred | - | - | drawn inside the stove f_L0_049 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_182 | piece | stove | r_L0_yasama_7 | inferred | - | - | drawn inside the stove f_L0_050 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_183 | piece | unknown | r_L0_oda_01 | inferred | - | - | drawn inside bed_single f_L0_073 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L0_184 | piece | bathtub | r_L0_banyo_5 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 1.62 x 0.80 m -> 1.55 x 0.75 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn bathtub 1.62 x 0.80 m runs 5 cm past the walls of its bay (clear 1.57 x 0.80 m): the nearest real product that fits, 1.55 x 0.75 m (plan crop recognition/crops/sym_L0_092_ctx.png) |
| f_L0_185 | piece | bathtub | r_L0_banyo_7 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 1.62 x 0.80 m -> 1.55 x 0.75 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn bathtub 1.62 x 0.80 m runs 5 cm past the walls of its bay (clear 1.57 x 0.80 m): the nearest real product that fits, 1.55 x 0.75 m (plan crop recognition/crops/sym_L0_093_ctx.png) |
| f_L0_186 | piece | bathtub | r_L0_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 1.62 x 0.80 m -> 1.55 x 0.75 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn bathtub 1.62 x 0.80 m runs 5 cm past the walls of its bay (clear 1.57 x 0.80 m): the nearest real product that fits, 1.55 x 0.75 m (plan crop recognition/crops/sym_L0_094_ctx.png) |
| f_L0_187 | piece | bathtub | r_L0_banyo_2 | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | size 1.62 x 0.80 m -> 1.55 x 0.75 m | code (reading.bay_size) | misread size (CLAUDE.md, user OK of 22 Oct 2026): the drawn bathtub 1.62 x 0.80 m runs 5 cm past the walls of its bay (clear 1.57 x 0.80 m): the nearest real product that fits, 1.55 x 0.75 m (plan crop recognition/crops/sym_L0_095_ctx.png) |
| f_L0_188 | piece | washbasin | r_L0_banyo_3 | inferred | - | - | washbasin: r_L0_banyo_3.bathroom_set (anchor f_L0_054) misses washbasin, and the type's product range fits 0.70 x 0.68 m (the only missing member of that size) |
| f_L0_189 | piece | fridge | r_L0_yasama | inferred | - | - | a 0.68 m deep box at a wall closing the counter run f_L0_002 and standing proud of it (a fridge) |
| f_L0_190 | piece | sofa_corner | r_L0_yasama | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_191 | piece | table_coffee | r_L0_yasama | inferred | - | - | table_coffee: r_L0_yasama.seating (anchor f_L0_190) misses table_coffee, and the type's product range fits 0.80 x 0.80 m (the only missing member of that size) |
| f_L0_192 | piece | unknown | r_L0_banyo_3 | inferred | - | - | the counter the washbasin f_L0_188 stands on (a vanity): part of it, not a piece of its own (not built) |
| f_L0_193 | piece | tv_unit | r_L0_yasama | inferred, adjusted_by_ai | size 1.51 x 0.25 m -> 1.51 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.51 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.51 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_194 | piece | fridge | r_L0_yasama_4 | inferred | - | - | a box drawn with its door swing beside the kitchen run (a fridge); front: the free side facing the most room is the front |
| f_L0_195 | piece | washbasin | r_L0_banyo_4 | inferred, adjusted_by_ai | - | code (reading.fixed_equipment) | misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026): through a wall: moved 0.14 m to the nearest free spot (plan crop recognition/crops/sym_L0_xb48a6c92_ctx.png) |
| f_L0_196 | piece | sofa_corner | r_L0_yasama_4 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_197 | piece | table_coffee | r_L0_yasama_4 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | coffee table 0.29 m from sofa front, needs >= 0.30 m; shift 0.1 m away from the sofa front |
| f_L0_198 | piece | tv_unit | r_L0_yasama_4 | inferred, adjusted_by_ai | size 1.51 x 0.25 m -> 1.51 x 0.40 m | code (size_snap) | size snap: the drawn tv_unit 1.51 x 0.25 m is outside its product range (depth 0.25 m is 22 % outside 0.3-0.6 m; a long piece keeps its length and takes the product depth); nearest real product 1.51 m long x 0.40 m deep (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_199 | piece | unknown | r_L0_banyo_4 | inferred | - | - | the counter the washbasin f_L0_195 stands on (a vanity): part of it, not a piece of its own (not built) |
| f_L0_200 | piece | fridge | r_L0_yasama_5 | inferred | - | - | a box drawn with its door swing beside the kitchen run (a fridge) |
| f_L0_202 | piece | fridge | r_L0_yasama_3 | inferred | - | - | a box drawn with its door swing beside the kitchen run (a fridge) |
| f_L0_203 | piece | floor_lamp | r_L0_yasama_3 | inferred | - | - | drawn by the same block entities as f_L0_201 (typed floor_lamp): the same piece in another insert of the block |
| f_L0_204 | piece | fridge | r_L0_yasama_6 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Fridge blocks door o_L0_019; move it to the nearest valid spot off the door swing. |
| f_L0_205 | piece | floor_lamp | r_L0_yasama_6 | inferred | - | - | drawn by the same block entities as f_L0_201 (typed floor_lamp): the same piece in another insert of the block |
| f_L0_206 | piece | fridge | r_L0_yasama_2 | inferred | - | - | a box drawn with its door swing beside the kitchen run (a fridge) |
| f_L0_207 | piece | floor_lamp | r_L0_yasama_2 | inferred | - | - | drawn by the same block entities as f_L0_201 (typed floor_lamp): the same piece in another insert of the block |
| f_L0_208 | piece | sofa_corner | r_L0_yasama_5 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_209 | piece | sofa_corner | r_L0_yasama_3 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_210 | piece | sofa_corner | r_L0_yasama_6 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_211 | piece | sofa_corner | r_L0_yasama_2 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L0_212 | piece | fridge | r_L0_yasama_7 | inferred | - | - | a box drawn with its door swing beside the kitchen run (a fridge) |
| f_L0_213 | piece | fridge | r_L0_yasama_8 | inferred | - | - | a box drawn with its door swing beside the kitchen run (a fridge) |
| f_L0_218 | piece | nightstand | r_L0_ebeveyn_odasi_4 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Snap the nightstand's back edge onto the left wall (w_L0_118) so its back is on a wall. |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_ebeveyn_odasi_4_1 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_4_1_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_4_1_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_4_2 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_4_2_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_4_2_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_4_3 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_4_3_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_4_3_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_5_1 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_1_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_1_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_5_2 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_2_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_2_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_5_3 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_3_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_5_3_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_6_1 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_6_1_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_6_1_after.jpg) |
| 1 | cam_r_L0_ebeveyn_odasi_6_2 | ![](agent/r1_cam_r_L0_ebeveyn_odasi_6_2_before.jpg) | ![](agent/r1_cam_r_L0_ebeveyn_odasi_6_2_after.jpg) |
| 1 | cam_r_L0_giris_holu_1 | ![](agent/r1_cam_r_L0_giris_holu_1_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_1_after.jpg) |
| 1 | cam_r_L0_giris_holu_2 | ![](agent/r1_cam_r_L0_giris_holu_2_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_2_after.jpg) |
| 1 | cam_r_L0_giris_holu_3_1 | ![](agent/r1_cam_r_L0_giris_holu_3_1_before.jpg) | ![](agent/r1_cam_r_L0_giris_holu_3_1_after.jpg) |
| 1 | cam_r_L0_oda_01_1 | ![](agent/r1_cam_r_L0_oda_01_1_before.jpg) | ![](agent/r1_cam_r_L0_oda_01_1_after.jpg) |
| 1 | cam_r_L0_oda_01_2 | ![](agent/r1_cam_r_L0_oda_01_2_before.jpg) | ![](agent/r1_cam_r_L0_oda_01_2_after.jpg) |
| 1 | cam_r_L0_oda_01_3 | ![](agent/r1_cam_r_L0_oda_01_3_before.jpg) | ![](agent/r1_cam_r_L0_oda_01_3_after.jpg) |
| 1 | cam_r_L0_oda_19_1 | ![](agent/r1_cam_r_L0_oda_19_1_before.jpg) | ![](agent/r1_cam_r_L0_oda_19_1_after.jpg) |
| 1 | cam_r_L0_oda_19_2 | ![](agent/r1_cam_r_L0_oda_19_2_before.jpg) | ![](agent/r1_cam_r_L0_oda_19_2_after.jpg) |
| 1 | cam_r_L0_oda_19_3 | ![](agent/r1_cam_r_L0_oda_19_3_before.jpg) | ![](agent/r1_cam_r_L0_oda_19_3_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_1 | ![](agent/r1_cam_r_L0_yangin_merdiveni_1_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_1_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_2 | ![](agent/r1_cam_r_L0_yangin_merdiveni_2_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_2_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_3 | ![](agent/r1_cam_r_L0_yangin_merdiveni_3_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_3_after.jpg) |
| 1 | cam_r_L0_yasama_1 | ![](agent/r1_cam_r_L0_yasama_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_1_after.jpg) |
| 1 | cam_r_L0_yasama_2 | ![](agent/r1_cam_r_L0_yasama_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_2_after.jpg) |
| 1 | cam_r_L0_yasama_3 | ![](agent/r1_cam_r_L0_yasama_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_3_after.jpg) |
| 1 | cam_r_L0_yasama_4_1 | ![](agent/r1_cam_r_L0_yasama_4_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_4_1_after.jpg) |
| 1 | cam_r_L0_yasama_4_2 | ![](agent/r1_cam_r_L0_yasama_4_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_4_2_after.jpg) |
| 1 | cam_r_L0_yasama_4_3 | ![](agent/r1_cam_r_L0_yasama_4_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_4_3_after.jpg) |
| 1 | cam_r_L0_yasama_6_1 | ![](agent/r1_cam_r_L0_yasama_6_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_6_1_after.jpg) |
| 1 | cam_r_L0_yasama_6_2 | ![](agent/r1_cam_r_L0_yasama_6_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_6_2_after.jpg) |
| 1 | cam_r_L0_yasama_6_3 | ![](agent/r1_cam_r_L0_yasama_6_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_6_3_after.jpg) |
| 1 | cam_r_L0_yasama_7_1 | ![](agent/r1_cam_r_L0_yasama_7_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_7_1_after.jpg) |
| 1 | cam_r_L0_yasama_7_2 | ![](agent/r1_cam_r_L0_yasama_7_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_7_2_after.jpg) |
| 1 | cam_r_L0_yasama_7_3 | ![](agent/r1_cam_r_L0_yasama_7_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_7_3_after.jpg) |
| 1 | cam_r_L0_yasama_8_1 | ![](agent/r1_cam_r_L0_yasama_8_1_before.jpg) | ![](agent/r1_cam_r_L0_yasama_8_1_after.jpg) |
| 1 | cam_r_L0_yasama_8_2 | ![](agent/r1_cam_r_L0_yasama_8_2_before.jpg) | ![](agent/r1_cam_r_L0_yasama_8_2_after.jpg) |
| 1 | cam_r_L0_yasama_8_3 | ![](agent/r1_cam_r_L0_yasama_8_3_before.jpg) | ![](agent/r1_cam_r_L0_yasama_8_3_after.jpg) |
| 1 | ext_1 | ![](agent/r1_ext_1_before.jpg) | ![](agent/r1_ext_1_after.jpg) |
| 1 | ext_2 | ![](agent/r1_ext_2_before.jpg) | ![](agent/r1_ext_2_after.jpg) |
| 1 | ext_3 | ![](agent/r1_ext_3_before.jpg) | ![](agent/r1_ext_3_after.jpg) |
| 1 | ext_4 | ![](agent/r1_ext_4_before.jpg) | ![](agent/r1_ext_4_after.jpg) |
| 1 | ext_6 | ![](agent/r1_ext_6_before.jpg) | ![](agent/r1_ext_6_after.jpg) |
| 1 | ext_7 | ![](agent/r1_ext_7_before.jpg) | ![](agent/r1_ext_7_after.jpg) |
| 2 | cam_r_L0_oda_01_1 | ![](agent/r2_cam_r_L0_oda_01_1_before.jpg) | ![](agent/r2_cam_r_L0_oda_01_1_after.jpg) |
| 2 | cam_r_L0_oda_01_2 | ![](agent/r2_cam_r_L0_oda_01_2_before.jpg) | ![](agent/r2_cam_r_L0_oda_01_2_after.jpg) |
| 2 | cam_r_L0_oda_01_3 | ![](agent/r2_cam_r_L0_oda_01_3_before.jpg) | ![](agent/r2_cam_r_L0_oda_01_3_after.jpg) |
| 2 | cam_r_L0_oda_19_1 | ![](agent/r2_cam_r_L0_oda_19_1_before.jpg) | ![](agent/r2_cam_r_L0_oda_19_1_after.jpg) |
| 2 | cam_r_L0_oda_19_2 | ![](agent/r2_cam_r_L0_oda_19_2_before.jpg) | ![](agent/r2_cam_r_L0_oda_19_2_after.jpg) |
| 2 | cam_r_L0_oda_19_3 | ![](agent/r2_cam_r_L0_oda_19_3_before.jpg) | ![](agent/r2_cam_r_L0_oda_19_3_after.jpg) |
| 2 | cam_r_L0_yasama_5_1 | ![](agent/r2_cam_r_L0_yasama_5_1_before.jpg) | ![](agent/r2_cam_r_L0_yasama_5_1_after.jpg) |
| 2 | cam_r_L0_yasama_5_2 | ![](agent/r2_cam_r_L0_yasama_5_2_before.jpg) | ![](agent/r2_cam_r_L0_yasama_5_2_after.jpg) |
| 2 | cam_r_L0_yasama_5_3 | ![](agent/r2_cam_r_L0_yasama_5_3_before.jpg) | ![](agent/r2_cam_r_L0_yasama_5_3_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_4 | ![](agent/r2_ext_4_before.jpg) | ![](agent/r2_ext_4_after.jpg) |
| 2 | ext_6 | ![](agent/r2_ext_6_before.jpg) | ![](agent/r2_ext_6_after.jpg) |
| 2 | ext_7 | ![](agent/r2_ext_7_before.jpg) | ![](agent/r2_ext_7_after.jpg) |
| 3 | cam_r_L0_ebeveyn_odasi_2_1 | ![](agent/r3_cam_r_L0_ebeveyn_odasi_2_1_before.jpg) | ![](agent/r3_cam_r_L0_ebeveyn_odasi_2_1_after.jpg) |
| 3 | cam_r_L0_ebeveyn_odasi_2_2 | ![](agent/r3_cam_r_L0_ebeveyn_odasi_2_2_before.jpg) | ![](agent/r3_cam_r_L0_ebeveyn_odasi_2_2_after.jpg) |
| 3 | cam_r_L0_ebeveyn_odasi_2_3 | ![](agent/r3_cam_r_L0_ebeveyn_odasi_2_3_before.jpg) | ![](agent/r3_cam_r_L0_ebeveyn_odasi_2_3_after.jpg) |
| 3 | cam_r_L0_giris_holu_2_1 | ![](agent/r3_cam_r_L0_giris_holu_2_1_before.jpg) | ![](agent/r3_cam_r_L0_giris_holu_2_1_after.jpg) |
| 3 | cam_r_L0_giris_holu_2_2 | ![](agent/r3_cam_r_L0_giris_holu_2_2_before.jpg) | ![](agent/r3_cam_r_L0_giris_holu_2_2_after.jpg) |
| 3 | ext_1 | ![](agent/r3_ext_1_before.jpg) | ![](agent/r3_ext_1_after.jpg) |
| 3 | ext_2 | ![](agent/r3_ext_2_before.jpg) | ![](agent/r3_ext_2_after.jpg) |
| 3 | ext_3 | ![](agent/r3_ext_3_before.jpg) | ![](agent/r3_ext_3_after.jpg) |
| 3 | ext_4 | ![](agent/r3_ext_4_before.jpg) | ![](agent/r3_ext_4_after.jpg) |
| 3 | ext_6 | ![](agent/r3_ext_6_before.jpg) | ![](agent/r3_ext_6_after.jpg) |
| 3 | ext_7 | ![](agent/r3_ext_7_before.jpg) | ![](agent/r3_ext_7_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

None.
