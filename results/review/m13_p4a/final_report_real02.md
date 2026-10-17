# Final report: real02

48 views: 0 polished, 48 Cycles (gate_validation 7, not_run 41). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 48 |
| interior / exterior views | 41 / 7 |
| variant | base |
| polished | 0 |
| Cycles | 48 (gate_validation 7, not_run 41) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 3 |
| needs_review views | 3 |
| unverified pieces in view (sum over views) | 34 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 14 |
| exposure | -7.67 .. +3.00 EV (2 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 2 (0 critical, 2 major) |
| window pull | 24 view(s), -3 .. 0 EV |
| camera policy | agent 1, m5 5, search 41, unknown 1 |
| camera score (min / mean / max) | 1.21 / 2.51 / 3.49 |
| rooms by number of views | 1 with 0, 2 with 1, 3 with 2, 11 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 3.5 min / 8.9 min / 107.3 s |
| seconds: polish / gate / check | - / - / 11.0 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real02.blend](3d/real02.blend) | 315.8 MB |
| [real02.glb](3d/real02.glb) | 818.4 MB |

48 cameras; textures scaled to at most 1024 px (245 scaled) for the download.

## AI decor

85 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 24 rooms; 3 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- camera cam_r_L1_banyo_1: no free camera point in the room; camera at the room's inner point
- 5 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L0_027, f_L0_028, f_L0_029, f_L0_030, f_L1_036
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- drawn-piece check: 7 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 12 proposal(s) refused, reverted or not placed (listed per room)
- 2 view(s) too dark for the EV cap (lighting_dark: 0 critical, 2 major): cam_r_L-1_salon_1 metered +3.42 EV, cam_r_L-1_salon_2 metered +3.07 EV; the agent's set_lighting raises the room's lights

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

Level L-1: [contact_L-1.jpg](contact_L-1.jpg)

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Side-by-side sheets (Cycles | polished)

None: the polish did not run in this run.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 2.17 | D3 A1 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.81 | D3 A1 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.50 | -1 | search 3.18 | D5 A2 | 1 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 2.49 | D2 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.17 | -1 | search 2.03 | D5 A2 | 1 | no | [preview](cam_r_L-1_koridor_2_3_final_preview.jpg) [plan](cam_r_L-1_koridor_2_3_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -2 | search 2.94 | D6 A5 | 0 | yes | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -1 | search 2.68 | D6 A4 | 0 | yes | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -2 | search 2.62 | D6 A4 | 0 | yes | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +3.00 (cap; metered +3.42) | -1 | search 2.64 | D11 A3 | 5 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +3.00 (cap; metered +3.07) | -1 | search 2.59 | D12 A3 | 4 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +2.67 | -1 | search 2.59 | D11 A3 | 4 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.17 | D3 A1 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 1.81 | D3 A1 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.35 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 1.21 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -1.17 | - | search 3.49 | D5 A1 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -1.17 | - | search 3.44 | D5 A3 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -1.00 | -1 | search 3.39 | D4 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.67 | - | search 2.71 | D4 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_koridor_2 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 2.61 | D3 | 0 | no | [preview](cam_r_L0_koridor_2_final_preview.jpg) [plan](cam_r_L0_koridor_2_plan.jpg) |
| cam_r_L0_koridor_3 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 2.11 | D2 | 0 | no | [preview](cam_r_L0_koridor_3_final_preview.jpg) [plan](cam_r_L0_koridor_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -0.83 | -1 | search 3.45 | D3 A1 | 2 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 3.11 | D3 | 1 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -0.67 | -1 | search 3.10 | D4 A1 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.55 | D3 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.44 | D4 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 2.37 | D2 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | +0.83 | - | search 1.61 | D3 A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 2.80 | D2 A1 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 2.60 | D3 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_koridor_2_1 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.98 | D4 | 0 | no | [preview](cam_r_L1_koridor_2_1_final_preview.jpg) [plan](cam_r_L1_koridor_2_1_plan.jpg) |
| cam_r_L1_koridor_2_2 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 2.76 | D5 A2 | 0 | no | [preview](cam_r_L1_koridor_2_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_2_plan.jpg) |
| cam_r_L1_koridor_2_3 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 2.61 | D5 A1 | 0 | no | [preview](cam_r_L1_koridor_2_3_final_preview.jpg) [plan](cam_r_L1_koridor_2_3_plan.jpg) |
| cam_r_L1_koridor_3 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 2.51 | D2 | 0 | no | [preview](cam_r_L1_koridor_3_final_preview.jpg) [plan](cam_r_L1_koridor_3_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.33 | -3 | search 3.37 | D6 A5 | 2 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.33 | -2 | search 3.23 | D5 A6 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.67 | -3 | search 3.21 | D4 A6 | 0 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 1.50 | D2 A1 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2_1 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -7.50 | 0 | search 1.77 | D2 A2 | 0 | no | [preview](cam_r_L1_teras_2_1_final_preview.jpg) [plan](cam_r_L1_teras_2_1_plan.jpg) |
| cam_r_L1_teras_2_2 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -5.17 | 0 | search 1.41 | D2 A2 | 0 | no | [preview](cam_r_L1_teras_2_2_final_preview.jpg) [plan](cam_r_L1_teras_2_2_plan.jpg) |
| cam_r_L1_teras_2_3 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -7.67 | 0 | search 1.38 | D1 | 0 | no | [preview](cam_r_L1_teras_2_3_final_preview.jpg) [plan](cam_r_L1_teras_2_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.00 | 0 | m5 | D4 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.33 | 0 | m5 | D4 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | 0 | m5 | D4 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.67 | 0 | m5 | D4 | 0 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.17 | 0 | m5 blocked | D6 | 0 | no | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | - | agent | D2 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |
| ext_6.001 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | 0 | - | D4 | 0 | no | [preview](ext_6.001_final_preview.jpg) [plan](ext_6.001_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 2 | 0 | 2 | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_banyo_2 | bathroom | L-1 | 0 | 0 | 0 | - |
| r_L-1_koridor | hall | L-1 | 0 | 0 | 0 | - |
| r_L-1_koridor_2 | hall | L-1 | 3 | 0 | 3 | cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3 |
| r_L-1_mutfak | kitchen | L-1 | 3 | 0 | 3 | cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3 |
| r_L-1_mutfak_2 | kitchen | L-1 | 0 | 0 | 0 | - |
| r_L-1_salon | living | L-1 | 3 | 0 | 3 | cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3 |
| r_L-1_salon_2 | living | L-1 | 0 | 0 | 0 | - |
| r_L0_banyo | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_banyo_1, cam_r_L0_banyo_2 |
| r_L0_banyo_2 | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_banyo | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2 |
| r_L0_e_banyo_2 | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3 |
| r_L0_e_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_koridor | hall | L0 | 3 | 0 | 3 | cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3 |
| r_L0_koridor_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_merdiven | hall | L0 | 0 | 0 | 0 | - |
| r_L0_merdiven_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L0_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_3 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3 |
| r_L0_yatak_odasi_4 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L1_banyo | bathroom | L1 | 1 | 0 | 1 | cam_r_L1_banyo_1 |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 3 | 0 | 3 | cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3 |
| r_L1_koridor_2 | hall | L1 | 3 | 0 | 3 | cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_2, cam_r_L1_koridor_2_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | other | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 1 | 0 | 1 | cam_r_L1_teras_1 |
| r_L1_teras_2 | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_2_1, cam_r_L1_teras_2_2, cam_r_L1_teras_2_3 |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_banyo_2 (twin of r_L0_e_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_4 (twin of r_L0_yatak_odasi_3), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi).

Rooms without a rendered view: r_L0_merdiven (stair core: the stair fills the room, its only camera point is inside the stair; the hall shows it (docs/milestone11.md §1.3 M5)).

### Why Cycles

- cam_r_L-1_banyo_1: not_run: polish not run
- cam_r_L-1_banyo_2: not_run: polish not run
- cam_r_L-1_koridor_2_1: not_run: polish not run
- cam_r_L-1_koridor_2_2: not_run: polish not run
- cam_r_L-1_koridor_2_3: not_run: polish not run
- cam_r_L-1_mutfak_1: not_run: polish not run
- cam_r_L-1_mutfak_2: not_run: polish not run
- cam_r_L-1_mutfak_3: not_run: polish not run
- cam_r_L-1_salon_1: not_run: polish not run
- cam_r_L-1_salon_2: not_run: polish not run
- cam_r_L-1_salon_3: not_run: polish not run
- cam_r_L0_banyo_1: not_run: polish not run
- cam_r_L0_banyo_2: not_run: polish not run
- cam_r_L0_e_banyo_1: not_run: polish not run
- cam_r_L0_e_banyo_2: not_run: polish not run
- cam_r_L0_e_yatak_odasi_1: not_run: polish not run
- cam_r_L0_e_yatak_odasi_2: not_run: polish not run
- cam_r_L0_e_yatak_odasi_3: not_run: polish not run
- cam_r_L0_koridor_1: not_run: polish not run
- cam_r_L0_koridor_2: not_run: polish not run
- cam_r_L0_koridor_3: not_run: polish not run
- cam_r_L0_yatak_odasi_1: not_run: polish not run
- cam_r_L0_yatak_odasi_2: not_run: polish not run
- cam_r_L0_yatak_odasi_3: not_run: polish not run
- cam_r_L0_yatak_odasi_3_1: not_run: polish not run
- cam_r_L0_yatak_odasi_3_2: not_run: polish not run
- cam_r_L0_yatak_odasi_3_3: not_run: polish not run
- cam_r_L1_banyo_1: not_run: polish not run
- cam_r_L1_koridor_1: not_run: polish not run
- cam_r_L1_koridor_2: not_run: polish not run
- cam_r_L1_koridor_2_1: not_run: polish not run
- cam_r_L1_koridor_2_2: not_run: polish not run
- cam_r_L1_koridor_2_3: not_run: polish not run
- cam_r_L1_koridor_3: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: not_run: polish not run
- cam_r_L1_teras_1: not_run: polish not run
- cam_r_L1_teras_2_1: not_run: polish not run
- cam_r_L1_teras_2_2: not_run: polish not run
- cam_r_L1_teras_2_3: not_run: polish not run
- ext_1: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_2: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_3: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_4: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_5: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_6: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_6.001: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_mutfak_1 | cycles | cross-check in_json_not_rendered | f_L-1_067 | sink_kitchen | - | from_documents | one_building.dwg INSERT:365F8/4,INSERT:365F8/9 tekil_villa_evye vector 0.90 | yes | visible 0.38, area 0.049 |
| cam_r_L-1_mutfak_2 | cycles | cross-check in_json_not_rendered | f_L-1_067 | sink_kitchen | - | from_documents | one_building.dwg INSERT:365F8/4,INSERT:365F8/9 tekil_villa_evye vector 0.90 | yes | visible 0.39, area 0.111 |
| cam_r_L-1_mutfak_3 | cycles | cross-check in_json_not_rendered | f_L-1_067 | sink_kitchen | - | from_documents | one_building.dwg INSERT:365F8/4,INSERT:365F8/9 tekil_villa_evye vector 0.90 | yes | visible 0.40, area 0.109 |

## Needs review

- cam_r_L-1_mutfak_1: json cross-check in_json_not_rendered: f_L-1_067
- cam_r_L-1_mutfak_2: json cross-check in_json_not_rendered: f_L-1_067
- cam_r_L-1_mutfak_3: json cross-check in_json_not_rendered: f_L-1_067

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- o_L0_001
- o_L0_002
- r_L-1_koridor
- r_L-1_koridor_2
- r_L-1b_salon
- r_L-1b_salon_2
- r_L-1b_koridor
- r_L-1b_koridor_2
- r_L0_koridor
- r_L0_koridor_2
- r_L0_yatak_odasi_3
- r_L0_yatak_odasi_4
- r_L0_merdiven
- r_L0_merdiven_2
- r_L1_teras
- r_L1_teras_2
- f_L-1_005
- f_L-1_006
- f_L-1_007
- f_L-1_009
- f_L-1_014
- f_L-1_015
- f_L-1_016
- f_L-1_018
- f_L-1_021
- f_L-1_022
- f_L-1_053
- f_L-1_054
- f_L-1_055
- f_L-1_056
- f_L-1_057
- f_L-1_058
- f_L-1_059
- f_L-1_060
- f_L-1_061
- f_L-1_062
- f_L-1_063
- f_L-1_065
- f_L-1_069
- f_L-1_070
- f_L-1_071
- f_L-1_072
- f_L-1_073
- f_L-1_074
- f_L-1_085
- f_L-1_086
- f_L-1_087
- f_L-1_088
- f_L-1b_001
- f_L-1b_002
- f_L-1b_006
- f_L-1b_008
- f_L-1b_012
- f_L-1b_014
- f_L-1b_041
- f_L-1b_042
- f_L-1b_043
- f_L-1b_044
- f_L-1b_045
- f_L-1b_046
- f_L-1b_047
- f_L-1b_048
- f_L-1b_049
- f_L-1b_050
- f_L-1b_065
- f_L-1b_066
- f_L0_013
- f_L0_014
- f_L0_019
- f_L0_020
- f_L0_021
- f_L0_022
- f_L0_023
- f_L0_024
- f_L0_025
- f_L0_026
- f_L0_027
- f_L0_028
- f_L0_029
- f_L0_030
- f_L1_003
- f_L1_004
- f_L1_005
- f_L1_006
- f_L1_015
- f_L1_016
- f_L1_017
- f_L1_018
- f_L1_019
- f_L1_020
- f_L1_027
- f_L1_028
- f_L1_029
- f_L1_030
- f_L1_031
- f_L1_032
- f_L1_033
- f_L1_034
- f_L1_035
- f_L1_036
- f_L1_037
- f_L1_038

Unverified pieces in view:

- cam_r_L-1_banyo_2: f_L-1_056
- cam_r_L-1_koridor_2_1: f_L-1_053
- cam_r_L-1_koridor_2_3: f_L-1_053
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_059, f_L-1_060, f_L-1_061, f_L-1_073
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_060, f_L-1_063, f_L-1_073
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_063, f_L-1_071, f_L-1_073
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_e_yatak_odasi_2: f_L0_023
- cam_r_L0_e_yatak_odasi_3: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030
- cam_r_L0_yatak_odasi_2: f_L0_030
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030
- cam_r_L0_yatak_odasi_3_1: f_L0_021, f_L0_029
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_015, f_L1_034
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_034

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L-1b_002 | untyped_piece | r_L-1b_salon | drawn piece 5.14 x 2.37 m in r_L-1b_salon has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1b_045 | untyped_piece | r_L-1b_salon_2 | drawn piece 0.82 x 1.64 m in r_L-1b_salon_2 has no type (AI passes: kitchen_island, sofa): not built | recognition/crops/sym_L-1b_007_ctx.png |
| f_L-1b_046 | untyped_piece | r_L-1b_salon | drawn piece 0.82 x 1.64 m in r_L-1b_salon has no type (AI passes: kitchen_island, sofa): not built | recognition/crops/sym_L-1b_008_ctx.png |

Drawn symbols read as not furniture (never built): dimension_outline 5, other 3.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L-1_023 | furniture | wardrobe | hssd_7094e30496b2735c235819e99c509769dc30502d | vision quality 2 (<= 2) |
| f_L-1_025 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_026 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_051 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_052 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_096 | furniture | fridge | hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 | vision quality 2 (<= 2) |
| f_L0_003 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_004 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_005 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_006 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_015 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_016 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_017 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_018 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_023 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L0_024 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L1_007 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_008 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_013 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_014 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_039 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |
| f_L1_042 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_043 | furniture | chair | abo_B07K7K8YF9 | the vision check says it is not a chair (a armchair) |
| f_L1_044 | furniture | chair | abo_B07K7K8YF9 | the vision check says it is not a chair (a armchair) |

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L-1_salon | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_002 | area_label_vs_computed | r_L-1_salon_2 | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_003 | area_label_vs_computed | r_L-1_mutfak | Label says 14,50 m², polygon gives 13,63 m² (6.0%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_004 | area_label_vs_computed | r_L-1_mutfak_2 | Label says 14,50 m², polygon gives 13,62 m² (6.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_005 | area_label_vs_computed | r_L-1_koridor | Label says 7,00 m², polygon gives 11,92 m² minus the stair 5,64 m² = 6,28 m² (10.2%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_006 | area_label_vs_computed | r_L-1_koridor_2 | Label says 7,00 m², polygon gives 11,93 m² minus the stair 5,64 m² = 6,29 m² (10.2%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_007 | area_label_vs_computed | r_L-1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_008 | area_label_vs_computed | r_L-1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_009 | area_label_vs_computed | r_L-1b_salon | Label says 46,00 m², polygon gives 51,83 m² (12.7%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_010 | area_label_vs_computed | r_L-1b_salon_2 | Label says 46,00 m², polygon gives 51,83 m² (12.7%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_011 | area_label_vs_computed | r_L-1b_oda | Label says 13,00 m², polygon gives 13,14 m² (1.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_012 | area_label_vs_computed | r_L-1b_oda_2 | Label says 13,00 m², polygon gives 13,15 m² (1.2%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_013 | area_label_vs_computed | r_L-1b_koridor | Label says 7,00 m², polygon gives 11,50 m² minus the stair 5,64 m² = 5,86 m² (16.3%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_014 | area_label_vs_computed | r_L-1b_koridor_2 | Label says 7,00 m², polygon gives 11,50 m² minus the stair 5,64 m² = 5,86 m² (16.3%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_015 | area_label_vs_computed | r_L-1b_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.7%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_016 | area_label_vs_computed | r_L-1b_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_017 | area_label_vs_computed | r_L0_yatak_odasi | Label says 16,00 m², polygon gives 16,13 m² (0.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_018 | area_label_vs_computed | r_L0_e_yatak_odasi | Label says 17,00 m², polygon gives 16,86 m² (0.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_019 | area_label_vs_computed | r_L0_e_yatak_odasi_2 | Label says 17,00 m², polygon gives 16,87 m² (0.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_020 | area_label_vs_computed | r_L0_yatak_odasi_2 | Label says 16,00 m², polygon gives 16,12 m² (0.7%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_021 | area_label_vs_computed | r_L0_koridor | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_022 | area_label_vs_computed | r_L0_koridor_2 | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_023 | area_label_vs_computed | r_L0_yatak_odasi_3 | Label says 17,00 m², polygon gives 14,05 m² (17.3%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_024 | area_label_vs_computed | r_L0_yatak_odasi_4 | Label says 17,00 m², polygon gives 14,04 m² (17.4%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_025 | area_label_vs_computed | r_L0_banyo | Label says 4,90 m², polygon gives 4,97 m² (1.5%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_026 | area_label_vs_computed | r_L0_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_027 | area_label_vs_computed | r_L1_teras | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_028 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_029 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_030 | area_label_vs_computed | r_L1_koridor | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_031 | area_label_vs_computed | r_L1_koridor_2 | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_032 | area_label_vs_computed | r_L1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_033 | area_label_vs_computed | r_L1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_034 | area_label_vs_computed | r_L1_teras_2 | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_035 | outline_mismatch | L0, L-1 | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_036 | outline_mismatch | L0, L-1b | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_037 | outline_mismatch | L0, L1 | Outer wall outline of Çatı Katı differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_038 | type_disagreement | f_L-1_067 | f_L-1_067: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_039 | type_disagreement | f_L-1_068 | f_L-1_068: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_040 | type_disagreement | f_L-1b_064 | f_L-1b_064: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_041 | type_disagreement | f_L-1b_069 | f_L-1b_069: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_042 | type_disagreement | f_L-1b_070 | f_L-1b_070: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_043 | type_disagreement | f_L1_024 | f_L1_024: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes) | typed table_coffee (trust order: vector geometry and block names > AI) |
| c_044 | symbol_type_disagreement | f_L-1b_045 | f_L-1b_045: sym_L-1b_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_045 | symbol_type_disagreement | f_L-1b_046 | f_L-1b_046: sym_L-1b_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_046 | symbol_type_disagreement | f_L-1b_065 | f_L-1b_065: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_047 | symbol_type_disagreement | f_L-1b_066 | f_L-1b_066: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_048 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_049 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L1_017 | f_L1_017: sym_L1_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_053 | symbol_type_disagreement | f_L1_018 | f_L1_018: sym_L1_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_054 | symbol_type_disagreement | f_L1_036 | f_L1_036: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | unresolved: the drawn footprint is kept as unknown, unverified |
| c_055 | other | r_L-1b_salon | r_L-1b_salon: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_056 | other | r_L-1b_salon_2 | r_L-1b_salon_2: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_057 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_058 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_059 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_060 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_061 | symbol_front_disagreement | f_L0_027 | f_L0_027: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_062 | symbol_front_disagreement | f_L0_028 | f_L0_028: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_063 | symbol_front_disagreement | f_L0_029 | f_L0_029: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_064 | symbol_front_disagreement | f_L0_030 | f_L0_030: sym_L0_012: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_065 | unit_mismatch | r1, r2, r3, r4, r5, r6 | sheets.json sc_001: one_building.dwg: $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_066 | level_mark_mismatch | r6 | sheets.json sc_002: section r6: the level mark 40.00 (MTEXT:304DD) gives -3.00 m but points at -3.15 m (the bottom of a slab) (0.15 m apart) | geometry wins: slab tops from the slab lines |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 6 regions (use: heights 1, ignored 1, read 4). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | one_building.dwg | title_block | geometry (0.90) | verified | - | - | ignored (title block) |
| r2 | one_building.dwg | floor_plan | title (0.99) | verified | L-1 | base | read |
| r3 | one_building.dwg | alternative_floor_plan | title (0.99) | verified | L-1b | Açık mutfak | read |
| r4 | one_building.dwg | floor_plan | title (0.99) | verified | L0 | base | read |
| r5 | one_building.dwg | floor_plan | title (0.99) | verified | L1 | base | read |
| r6 | one_building.dwg | section | geometry (0.85) | verified | - | - | heights |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | r2 | r3 Açık mutfak -> L-1b |
| L0 | Zemin Kat | floor | r4 | - |
| L1 | Çatı Katı | attic | r5 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r2, r4, r5 |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r3, r4, r5 |

Section regions (heights): r6.

Strays (entities far from every drawing, ignored): 3.

| entity | type | layer | distance (m) | reason |
|---|---|---|---|---|
| HATCH:6633 | HATCH | _P3_S_Duvar_T | 317.9 | far outside the frame, 1 entity (0.01 % of the document) |
| DIMENSION:34CEC | DIMENSION | Deko_Olcu Ic | 20.9 | far outside the frame; on a layer that is off or frozen (not drawn) |
| DIMENSION:34CF2 | DIMENSION | Deko_Olcu Ic | 21.0 | far outside the frame; on a layer that is off or frozen (not drawn) |

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| one_building.dwg | dwg | 0.01 | unit_check | area_labels cm 1.00 (4); level_marks cm 1.00 (1); door_widths cm 1.00 (26); wall_thickness None 0.57 (1514); text_height None - (40); dimensions None - (0) | $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used |

Conflicts:

| id | kind | description | resolution |
|---|---|---|---|
| sc_001 | unit_mismatch | one_building.dwg: $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| sc_002 | level_mark_mismatch | section r6: the level mark 40.00 (MTEXT:304DD) gives -3.00 m but points at -3.15 m (the bottom of a slab) (0.15 m apart) | geometry wins: slab tops from the slab lines |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/one_building_dwg_s1.jpg](debug/one_building_dwg_s1.jpg)

Sheet warnings:

- the largest drawn polylines of the plans differ in size: r2 (L-1) LWPOLYLINE:366F8 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r3 (L-1b) LWPOLYLINE:2C4A5 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r4 (L0) LWPOLYLINE:2DA7F on DBM_w_sld 7.59 x 10.50 m (open, ends 0.40 m apart); r5 (L1) LWPOLYLINE:2F87A on _P3_S_Duvar_Ç 11.77 x 8.60 m (closed); the registered outlines (all long strokes, columns included) give residuals r2 0.0001, r3 0.0001, r5 0.0001 m; each level is kept as drawn
- section r6: 2 horizontal lines outside the left wall; the upper one (+0.00 m) is read as the terrain, the others (-3.15 m (LWPOLYLINE:304DE)) are not
- section r6: 2 horizontal lines outside the right wall; the upper one (+0.00 m) is read as the terrain, the others (-3.15 m (LWPOLYLINE:304DF)) are not
- section r6: no cut line on the plans: the section's left end is taken as the building's min side along the cut axis (flipped unknown)
- roof: the break line on r5 (LWPOLYLINE:2F87A) is 11.77 m wide along the cut, the section's slope changes 12.17 m apart (0.40 m); both kept as drawn
- no elevation drawn: facade materials and outside openings are not drawn (facade empty)

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | -3,00 m (section) | 2,85 m (section) | base | r2 |
| L-1b | Bodrum Kat | basement | -3,00 m (section) | 2,85 m (section) | Açık mutfak | r3 |
| L0 | Zemin Kat | floor | 0,00 m (section) | 3,00 m (section) | base | r4 |
| L1 | Çatı Katı | attic | 3,15 m (section) | 3,43 m (section) | base | r5 |

Variants:

| variant | label | levels | rooms changed | outside changed |
|---|---|---|---|---|
| base | Base | L-1, L0, L1 | 0 | no |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | 6 | yes |

Heights (drawn = read from a document; assumed = a default, listed again under Assumed values):

| item | value | state | from | note |
|---|---|---|---|---|
| L-1 ceiling height | 2,85 m | drawn | section | - |
| L-1 floor level | -3,00 m | drawn | section | - |
| L-1 floor to floor | 3,00 m | drawn | vector | - |
| L-1b ceiling height | 2,85 m | drawn | section | - |
| L-1b floor level | -3,00 m | drawn | section | - |
| L-1b floor to floor | 3,00 m | drawn | vector | - |
| L0 ceiling height | 3,00 m | drawn | section | - |
| L0 floor level | 0,00 m | drawn | section | - |
| L0 floor to floor | 3,15 m | drawn | vector | - |
| L1 ceiling height | 3,43 m | drawn | section | - |
| L1 floor level | 3,15 m | drawn | section | - |
| sl_L-1 thickness | 0,15 m | drawn | section | - |
| sl_L0 thickness | 0,15 m | drawn | section | - |
| sl_L1 thickness | 0,15 m | drawn | section | - |
| roof eaves height | 3,65 m | drawn | vector | 0.50 m above the top floor |
| roof ridge height | 6,79 m | drawn | vector | 3.64 m above the top floor |
| roof overhang | 0,50 m | drawn | vector | left 0.50 m, right 0.50 m |
| roof thickness | 0,20 m | drawn | vector | perpendicular to the first slope |
| roof knee wall | 0,93 m | drawn | vector | the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 0.66 m above the floor |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L-1 | L-1 | -3,00 m | 0,15 m | section | 0 | all | verified |
| sl_L0 | L0 | 0,00 m | 0,15 m | section | 2 | all | verified |
| sl_L1 | L1 | 3,15 m | 0,15 m | section | 2 | all | verified |

Roof:

- type mansard (plan_roof_lines)
- over level L1
- eaves 3,65 m (drawn)
- ridge 6,79 m (drawn)
- overhang 0,50 m (drawn)
- thickness 0,20 m (drawn)
- knee wall 0,93 m (drawn)
- pitch 40.4 deg (drawn), 13.3 deg (drawn)
- 0 planes, 2 opening(s)
- covering not drawn (outside look: see Exterior views)

Facade:

No facade face or elevation drawn: the outside look is resolved from the brief, the style or the defaults (see Exterior views).

Site:

- plot not drawn
- 0 paving area(s), 0 grass, 0 parking built
- 0 boundary wall(s), 6 decor item(s) built
- 0 labelled area(s), 0 recorded only (label, not built)
- ground levels: left 0,00 m (drawn), right 0,00 m (drawn)
- terrain flat, 3 light well(s)

Levels and ground (Milestone 12):

- 2 level mark(s) read (slab_top 2); 0 mark symbol(s) taken out of the furniture
- datum ±0.00 = 43.00 m (drawn)
- ground from: section; terrain flat
- plinth top 0,00 m (inferred)

| Door | Threshold | Ground | Rise | Solution | Main |
|---|---|---|---|---|---|
| d_L0_011 | 0,00 m | 0,00 m | 0,00 m | none | yes |
| d_L0_012 | 0,00 m | 0,00 m | 0,00 m | none |  |

Inferred (listed, CLAUDE.md evidence rules):

- site.plinth: no SB. mark: the plinth up to the ground floor
- front_court win_L-1_001: window sill 2.10 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 8.39 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn); one court for win_L-1_001, win_L-1_002
- front_court win_L-1_003: window sill 2.10 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn)
- front_court win_L-1_004: window sill 2.10 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn)

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 26 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 1.00 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_049, f_L-1_053, f_L-1_059, f_L-1_060, f_L-1_061, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_075, f_L-1_077, f_L-1_087

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_095: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L-1_089)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_022, f_L-1_023, f_L-1_038, f_L-1_039, f_L-1_040, f_L-1_041, f_L-1_042, f_L-1_043, f_L-1_044, f_L-1_045, f_L-1_046, f_L-1_047, f_L-1_048, f_L-1_050, f_L-1_054, f_L-1_057, f_L-1_058, f_L-1_065, f_L-1_066, f_L-1_069, f_L-1_072, f_L-1_076, f_L-1_078, f_L-1_088

### Mutfak (r_L-1_mutfak, kitchen): completed

- added f_L-1_090: fridge 0.60 x 0.65 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_005, f_L-1_008, f_L-1_009, f_L-1_067, f_L-1_081, f_L-1_083, f_L-1_085

### Mutfak (r_L-1_mutfak_2, kitchen): completed (partner r_L-1_mutfak (twin) not used: 1 of 1 copied pieces fail a check here (fridge: the copy fails doors_free here); completed itself)

- added f_L-1_096: fridge 0.60 x 0.65 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_010, f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_014, f_L-1_017, f_L-1_018, f_L-1_068, f_L-1_082, f_L-1_084, f_L-1_086

### Koridor (r_L-1_koridor, hall): mirrored (decisions of r_L-1_koridor_2 (twin), not asked again)

- added f_L-1_100: shoe_cabinet 0.60 x 0.30 (confidence -, rule, mirrored from f_L-1_094)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_020

### Koridor (r_L-1_koridor_2, hall): completed

- added f_L-1_094: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_019

### Banyo (r_L-1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_026, f_L-1_051, f_L-1_056

### Banyo (r_L-1_banyo_2, bathroom): mirrored (decisions of r_L-1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_025, f_L-1_052, f_L-1_055

### Salon (r_L-1b_salon, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room; dining: no candidate position fits the room)

- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_042, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_056, f_L-1b_064, f_L-1b_068, f_L-1b_070

### Salon (r_L-1b_salon_2, living): completed (nothing fits: kitchen_run: no candidate position fits the room; dining: no candidate position fits the room; dining: no candidate position fits the room; partner r_L-1b_salon (twin) not used: the twin's drawn furniture does not map onto this room: drawn unknown f_L-1b_046 has no counterpart here; completed itself)

- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_003, f_L-1b_004, f_L-1b_006, f_L-1b_007, f_L-1b_008, f_L-1b_017, f_L-1b_018, f_L-1b_019, f_L-1b_020, f_L-1b_021, f_L-1b_022, f_L-1b_023, f_L-1b_024, f_L-1b_025, f_L-1b_039, f_L-1b_045, f_L-1b_047, f_L-1b_048, f_L-1b_057, f_L-1b_058, f_L-1b_059, f_L-1b_060, f_L-1b_061, f_L-1b_062, f_L-1b_063, f_L-1b_067, f_L-1b_069

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_082: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): mirrored (decisions of r_L-1b_koridor (twin), not asked again)

- added f_L-1b_086: shoe_cabinet 0.60 x 0.30 (confidence -, rule, mirrored from f_L-1b_082)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_015

### Banyo (r_L-1b_banyo, bathroom): copied (decisions of r_L-1_banyo (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_036, f_L-1b_038, f_L-1b_044

### Banyo (r_L-1b_banyo_2, bathroom): copied (decisions of r_L-1_banyo_2 (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_035, f_L-1b_037, f_L-1b_043

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_019, f_L0_030

### E.yatak Odası (r_L0_e_yatak_odasi, bedroom): completed (nothing to add)

- not placed work: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_023, f_L0_031, f_L0_032

### E.yatak Odası (r_L0_e_yatak_odasi_2, bedroom): completed (partner r_L0_e_yatak_odasi (twin) not used: it re-solved its drawn group (f_L0_007); completed itself)

- added f_L0_037: bench 1.20 x 0.40 (confidence -, rule)
- not placed work: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_008, f_L0_024, f_L0_033, f_L0_034

### Yatak Odası (r_L0_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_yatak_odasi (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_012, f_L0_020, f_L0_027

### E.banyo (r_L0_e_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_013, f_L0_015

### E.banyo (r_L0_e_banyo_2, bathroom): completed (nothing missing: the drawn groups are complete; partner r_L0_e_banyo (twin) not used: the twin's drawn furniture does not map onto this room: drawn shower f_L0_013 has no counterpart here; completed itself)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_014, f_L0_016

### Yatak Odası (r_L0_yatak_odasi_3, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_009, f_L0_021, f_L0_029

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): mirrored (decisions of r_L0_yatak_odasi_3 (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_011, f_L0_022, f_L0_028

### Merdiven (r_L0_merdiven, hall): completed (no groups for this room (hall 5.7 m²: nothing))

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Merdiven (r_L0_merdiven_2, hall): mirrored (decisions of r_L0_merdiven (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_003, f_L0_018, f_L0_025

### Banyo (r_L0_banyo_2, bathroom): mirrored (decisions of r_L0_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_005, f_L0_017, f_L0_026

### Teras (r_L1_teras, balcony): completed

- added f_L1_042: table_dining 0.70 x 0.70 (confidence -, rule)
- added f_L1_043: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_044: chair 0.45 x 0.45 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_022

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi, other): completed

- added f_L1_045: table_dining 1.20 x 0.80 (confidence -, rule)
- added f_L1_046: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_047: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_048: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_049: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_050: bookshelf 0.80 x 0.30 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_009, f_L1_033, f_L1_034

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_053: table_dining 1.20 x 0.80 (confidence -, rule, mirrored from f_L1_045)
- added f_L1_054: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_046)
- added f_L1_055: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_047)
- added f_L1_056: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_048)
- added f_L1_057: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_049)
- added f_L1_058: bookshelf 0.80 x 0.30 (confidence -, rule, mirrored from f_L1_050)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_006, f_L1_010, f_L1_035, f_L1_036

### Koridor (r_L1_koridor, hall): completed

- added f_L1_051: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_021, f_L1_023, f_L1_037, f_L1_038

### Koridor (r_L1_koridor_2, hall): completed

- added f_L1_052: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_024, f_L1_025, f_L1_026

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_007, f_L1_013, f_L1_019

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_008, f_L1_014, f_L1_020

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 230 of 230 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 223 ok, 7 failed; 0 changed by the AI.

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_038 | table_dining (table_dining) | 0.13 | - | - | - |
| f_L-1_050 | armchair (armchair) | 0.00 | 180.00 | - | - |
| f_L-1_053 | sofa_corner (sofa_corner) | 0.27 | - | - | - |
| f_L0_007 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_008 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L1_024 | table_coffee (table_coffee) | 0.11 | - | - | - |
| f_L1_025 | chair (chair) | 0.00 | 180.00 | - | - |

## Exterior views

7 of 7 exterior view(s) of variant `base` rendered.

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)
- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **not_validated** (exterior views stay the Cycles render): gate/gate_calibration.json missing: gate calibrate did not run or failed.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified | no |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok | no |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: unverified | no |
| ext_4 | corner | left, back | - | cycles (gate_validation) | ok | back: unverified | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: ok | no |
| ext_6 | frontal | back | - | cycles (gate_validation) | ok | back: ok | no |
| ext_6 | agent | right | - | cycles (gate_validation) | ok | back: ok | no |

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

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof ok.

Roof heights: built eaves 3,65 m, ridge 6,79 m; drawn eaves 3,65 m (vector), ridge 6,79 m (vector); result ok.

## Variants

One building per drawn alternative plan: the base and, for each alternative, the same building with that level replaced. An alternative renders only the rooms it changes, and its exterior views only when its outside differs (otherwise the base views stand for it). Each alternative has its own report in its sub-output (paths below, relative to the project output).

| variant | label | rooms changed | outside | interior views | polished / Cycles | mismatches | report |
|---|---|---|---|---|---|---|---|
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_2, cam_r_L1_koridor_2_3, cam_r_L1_koridor_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2_1, cam_r_L1_teras_2_2, cam_r_L1_teras_2_3 | 0 / 48 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 6 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3 | 0 / 15 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| one_building.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 17, block_name 58, group_member 17, level 3, none 37, rule 78, twin 20. Recognition questions: 54; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L-1_064 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_066 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_075 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_076 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_077 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_078 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_079 | r_L-1_salon_2 | ottoman | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_080 | r_L-1_salon | ottoman | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_085 | r_L-1_mutfak | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_086 | r_L-1_mutfak_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1b_039 | r_L-1b_salon_2 | bar_stool | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_040 | r_L-1b_salon | bar_stool | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_045 | r_L-1b_salon_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_046 | r_L-1b_salon | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_065 | r_L-1b_salon_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L-1b_066 | r_L-1b_salon | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L0_027 | r_L0_yatak_odasi_2 | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_028 | r_L0_yatak_odasi_4 | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_029 | r_L0_yatak_odasi_3 | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_030 | r_L0_yatak_odasi | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.85; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_031 | r_L0_e_yatak_odasi | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_032 | r_L0_e_yatak_odasi | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_033 | r_L0_e_yatak_odasi_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_034 | r_L0_e_yatak_odasi_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_031 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_032 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_034 | r_L1_oyun_aktivite_ve_dinlenme_odasi | console_table | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: console_table 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |
| f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | console_table | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |

## Site

Recorded, not built.

| id | what | detail |
|---|---|---|
| - | decor | other x 6 |

## Separators

Virtual lines that split an open-plan face where two room names share it (no geometry is built; the pipeline's report.md lists the candidates it dropped):

| id | level | length | status | reason |
|---|---|---|---|---|
| o_L-1_001 | L-1 | 1,38 m | verified | virtual separator (end-to-face, 1.38 m): two room names shared one face |
| o_L-1_002 | L-1 | 1,38 m | verified | virtual separator (end-to-face, 1.38 m): two room names shared one face |
| o_L-1b_001 | L-1b | 1,30 m | verified | virtual separator (end-to-wall, 1.30 m): two room names shared one face |
| o_L-1b_002 | L-1b | 1,30 m | verified | virtual separator (end-to-wall, 1.30 m): two room names shared one face |

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
- front kept from the drawing although both AI passes answered 'none': 9 piece(s) (f_L-1_064, f_L-1_066, f_L-1_079, f_L-1_080, f_L0_031, f_L0_032 ...)
- door height 2,10 m: 26 opening(s) (d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L-1b_001, d_L-1b_002 ...)
- opening height 2,10 m: 3 opening(s) (o_L0_001, o_L0_002, o_L1_001)
- window height 1,20 m: 12 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1b_001, win_L-1b_002 ...)
- window sill height 0,90 m: 12 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1b_001, win_L-1b_002 ...)
- f_L-1_019 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1_020 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1b_015 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1b_016 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
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
| area_light | 1 | r_L-1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo |
| area_light | 1 | r_L-1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo_2 |
| area_light | 1 | r_L-1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor |
| area_light | 1 | r_L-1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor_2 |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_e_yatak_odasi: agent: Room too dark for cam_r_L0_e_yatak_odasi_3 (wanted +3.30 EV vs +3.00 cap); finding specifies x1.74.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_e_yatak_odasi |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven_2 |
| area_light | 1 | r_L0_yatak_odasi: agent: Camera view is 0.35 stops over the EV cap; the finding specifies factor x1.8 to bring exposure within the cap.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; the room's light rig (2 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_4: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_4 |
| area_light | 1 | r_L1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_banyo |
| area_light | 1 | r_L1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_banyo_2 |
| area_light | 1 | r_L1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor |
| area_light | 1 | r_L1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| area_light | 4 | r_L1_teras: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras, light_r_L1_teras_2, light_r_L1_teras_3 |
| area_light | 4 | r_L1_teras_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras_2.001, light_r_L1_teras_2_2, light_r_L1_teras_2_3 |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (+y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 2 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_019, dress_f_L0_020 |
| boundary | 1 | no site plan: a low hedge on the inferred plot boundary (inferred) | site |
| cabinet_fronts | 6 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L-1_091, furn_f_L-1_092, furn_f_L-1_093 |
| climate | 1 | the drawing's language (room and site labels) (inferred; the species of trees and hedges follow it): banyo, mutfak, oda, salon, teras, yatak | site |
| direction | 4 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 22 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1_001_handle, d_L-1_002_handle, d_L-1_003_handle |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade | 1 | style profile exterior.facade (assumed) | exterior |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| ground:+y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| handrail | 4 | design detail on every flight side not against a wall; not in the documents | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| hedge | 6 | no site plan: a low hedge on the inferred plot boundary (inferred) | boundary_hedge_01, boundary_hedge_02, boundary_hedge_03 |
| height | 22 | door height listed as assumed in the building JSON | d_L-1_001, d_L-1_002, d_L-1_003 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) | d_L1_004, d_L1_005 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (2.04 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_003, d_L1_006 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (2.11 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_001, d_L1_002 |
| height | 2 | no height in the JSON; type height for armchair | furn_f_L-1_049, furn_f_L-1_050 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L0_007, furn_f_L0_008 |
| height | 23 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 2 | no height in the JSON; type height for console_table | furn_f_L1_034, furn_f_L1_036 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 6 | no height in the JSON; type height for floor_lamp | furn_f_L-1_064, furn_f_L-1_066, furn_f_L0_031 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 4 | no height in the JSON; type height for ottoman | furn_f_L-1_075, furn_f_L-1_076, furn_f_L-1_077 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_013, furn_f_L0_014 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_009, furn_f_L1_010, furn_f_L1_011 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1_008, furn_f_L-1_017 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L1_024 |
| height | 2 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 5 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L0_009, furn_f_L0_010 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 10 | window height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| height | 2 | window height not drawn: its top 2.10 m above the floor would reach over the roof underside (2.04 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | win_L1_001, win_L1_002 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
| inside_sill | 8 | design detail of the documented window: an inside sill 0.1 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L-1_001_inside_sill, win_L-1_002_inside_sill, win_L-1_003_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| light_well:win_L-1_001 | 1 | window sill 2.10 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 8.39 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn); one court for win_L-1_001, win_L-1_002 | site |
| light_well:win_L-1_003 | 1 | window sill 2.10 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn) | site |
| light_well:win_L-1_004 | 1 | window sill 2.10 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn) | site |
| mansard_ends | 1 | the section does not cut the two other sides: their lower slopes rise from the eaves to the plan's break line at the section's break height 5.350 m, the upper slopes from there at the pitch that reaches the section's ridge height (its upper pitch would stay under it) (docs/milestone11.md §1.1 E7) | roof |
| modules | 12 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| parapet | 1 | roof terrace ro_001: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn | roof |
| parapet_height:ro_002 | 1 | not drawn | roof |
| path:d_L0_011 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path:d_L0_012 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: concrete_exposed (style family modern; not drawn) | facade |
| plot | 1 | no site plan: the plot is the outline's rectangle + 6 m (inferred) | site |
| ridge_direction | 1 | read from one section profile (cut along x): the ridge runs across the cut through its highest point | roof |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_020 (no nightstand): the lamp would stand outside the room | rig_r_L0_yatak_odasi_2, rig_r_L0_yatak_odasi_2 |
| rig_bedside | 2 | bedside lamp beside the head of the bed f_L0_022 (no nightstand): the lamp would stand outside the room | rig_r_L0_yatak_odasi_4, rig_r_L0_yatak_odasi_4 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L-1_koridor: ceiling fixture at the pole of inaccessibility of r_L-1_koridor, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L-1_koridor_2, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinets along the counter f_L-1_001; 1777.8 lm -> 4.1389 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinets along the counter f_L-1_002; 1110.6 lm -> 3.1434 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_2_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinets along the counter f_L-1_003; 888.3 lm -> 2.4532 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_3_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinets along the counter f_L-1_004; 1040.4 lm -> 2.9889 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_4_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinets along the counter f_L-1_010; 1777.8 lm -> 4.1389 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinets along the counter f_L-1_011; 1110.7 lm -> 3.1435 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_2_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinets along the counter f_L-1_012; 888.3 lm -> 2.4532 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_3_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinets along the counter f_L-1_013; 1040.4 lm -> 2.9889 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_4_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_5_light |
| rig_light | 1 | r_L-1_salon: pendant over the dining table f_L-1_027; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: pendant over the dining table f_L-1_038; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 2 | r_L0_e_yatak_odasi: bedside lamp beside the head of the bed f_L0_007 (no nightstand); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light, rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 2 | r_L0_e_yatak_odasi_2: bedside lamp beside the head of the bed f_L0_008 (no nightstand); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light, rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 2 | r_L0_yatak_odasi: bedside lamp beside the head of the bed f_L0_019 (no nightstand); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light, rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 2 | r_L0_yatak_odasi_3: bedside lamp beside the head of the bed f_L0_021 (no nightstand); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light, rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L1_banyo: ceiling fixture at the pole of inaccessibility of r_L1_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_banyo_ceiling_2_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_007; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L1_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_008; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 12 drawn risers | furn_f_L-1_019, furn_f_L-1_020 |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.150 m / 11 drawn risers | furn_f_L0_001 |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.150 m / 12 drawn risers | furn_f_L0_002 |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 2 | outside sill 2.2285 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill, win_L0_003_sill |
| sill | 2 | outside sill 2.7431 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill, win_L0_004_sill |
| sill | 2 | outside sill 4.2173 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_003_sill, win_L-1_004_sill |
| sill | 2 | outside sill 7.2461 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_001_sill, win_L-1_002_sill |
| sill_height | 10 | window sill_height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 20 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1_salon, skirting_r_L-1_salon_2, skirting_r_L-1_mutfak |
| slab_band | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067 (docs/milestone11.md §1.3 M2; not drawn) | splashback_r_L-1_mutfak |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_010, f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068 (docs/milestone11.md §1.3 M2; not drawn) | splashback_r_L-1_mutfak_2 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_002 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_002 (100% of the smaller footprint; slab opening sv_L1_002); read as its upper end, not built as a second flight | f_L1_001 |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| tree | 2 | small tree: crown 3.5 m as drawn, 5.6 m tall (height by the crown class, assumed); species olive (inferred) | tree_tree_inferred_1, tree_tree_inferred_2 |
| tree:tree_inferred_1 | 1 | no site plan: a tree clear of the windows, the paths and the front garden (inferred, docs/milestone11.md §1.1 E11) | site |
| tree:tree_inferred_2 | 1 | no site plan: a tree clear of the windows, the paths and the front garden (inferred, docs/milestone11.md §1.1 E11) | site |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| waist | 4 | the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_fridge_mediterranean_3_e70ec886 [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial], hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_koridor_2_3: commercial-safe: no (flagged assets: hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: gen_fridge_mediterranean_3_e70ec886 [tool_nc], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_2: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: gen_plant_large_japandi_5_92708e0b [tool_nc])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: gen_plant_large_japandi_5_92708e0b [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: yes
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_koridor_2: commercial-safe: yes
- cam_r_L0_koridor_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L1_koridor_2: commercial-safe: yes
- cam_r_L1_koridor_2_1: commercial-safe: yes
- cam_r_L1_koridor_2_2: commercial-safe: no (flagged assets: hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L1_koridor_2_3: commercial-safe: no (flagged assets: hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial])
- cam_r_L1_koridor_3: commercial-safe: yes
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])
- cam_r_L1_teras_1: commercial-safe: yes
- cam_r_L1_teras_2_1: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial])
- cam_r_L1_teras_2_2: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial])
- cam_r_L1_teras_2_3: commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial])
- ext_1: commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial])
- ext_2: commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial])
- ext_3: commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial])
- ext_4: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial])
- ext_6: commercial-safe: yes
- ext_6.001: commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial])

## Built below library level (Milestone 13)

52 furniture piece(s) built from a module builder or a parametric family instead of a library model: 12 library gap(s) to close with a real model, 40 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

| id | type | method | builder | room | room type | source | gap | used |
|---|---|---|---|---|---|---|---|---|
| f_L-1_001 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_002 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_003 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_004 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_010 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_011 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_012 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_013 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_019 | stair | parametric | parametric:stair | r_L-1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L-1_020 | stair | parametric | parametric:stair | r_L-1_koridor | hall | from_documents | no (by design) | - |
| f_L-1_027 | table_dining | module | table_long | r_L-1_salon | living | from_documents | yes | module builder table_long (3 module(s): dining table 3.35 x 1.00 m on trestles) |
| f_L-1_038 | table_dining | module | table_long | r_L-1_salon_2 | living | from_documents | yes | module builder table_long (3 module(s): dining table 3.35 x 1.00 m on trestles) |
| f_L-1_053 | sofa_corner | module | sofa_l | r_L-1_salon | living | from_documents | yes | module builder sofa_l (6 module(s): sofa module 1.04 m, chaise module 1.00 x 1.75 m) |
| f_L-1_054 | sofa_corner | module | sofa_l | r_L-1_salon_2 | living | from_documents | yes | module builder sofa_l (6 module(s): sofa module 1.04 m, chaise module 1.00 x 1.75 m) |
| f_L-1_057 | table_coffee | parametric | parametric:table_coffee | r_L-1_salon_2 | living | from_documents | yes | parametric family (built below the library level) |
| f_L-1_059 | table_coffee | parametric | parametric:table_coffee | r_L-1_salon | living | from_documents | yes | parametric family (built below the library level) |
| f_L-1_063 | table_coffee | parametric | parametric:table_coffee | r_L-1_salon | living | from_documents | yes | parametric family (built below the library level) |
| f_L-1_065 | table_coffee | parametric | parametric:table_coffee | r_L-1_salon_2 | living | from_documents | yes | parametric family (built below the library level) |
| f_L-1_067 | sink_kitchen | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_068 | sink_kitchen | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1b_003 | kitchen_counter | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_004 | kitchen_counter | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_005 | kitchen_island | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_009 | kitchen_counter | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L-1b_010 | kitchen_counter | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L-1b_011 | kitchen_island | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L-1b_015 | stair | parametric | parametric:stair | r_L-1b_koridor_2 | hall | from_documents | no (by design) | - |
| f_L-1b_016 | stair | parametric | parametric:stair | r_L-1b_koridor | hall | from_documents | no (by design) | - |
| f_L-1b_063 | sink_kitchen | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_064 | sink_kitchen | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L0_001 | stair | parametric | parametric:stair | r_L0_merdiven | hall | from_documents | no (by design) | - |
| f_L0_002 | stair | parametric | parametric:stair | r_L0_merdiven_2 | hall | from_documents | no (by design) | - |
| f_L0_013 | shower | parametric | parametric:shower | r_L0_e_banyo | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L0_014 | shower | parametric | parametric:shower | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L1_002 | stair | parametric | parametric:stair | r_L1_koridor | hall | from_documents | no (by design) | - |
| f_L1_023 | chair | parametric | parametric:chair | r_L1_koridor | hall | from_documents | yes | parametric family (built below the library level) |
| f_L1_025 | chair | parametric | parametric:chair | r_L1_koridor_2 | hall | from_documents | yes | parametric family (built below the library level) |
| f_L1_033 | tv_unit | parametric | parametric:tv_unit | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | from_documents | yes | parametric family (built below the library level) |
| f_L1_035 | tv_unit | parametric | parametric:tv_unit | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | from_documents | yes | parametric family (built below the library level) |
| f_L-1_091 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_092 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_093 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1b_079 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon | living | added_by_ai | no (by design) | - |
| f_L-1b_080 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon | living | added_by_ai | no (by design) | - |
| f_L-1b_081 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon | living | added_by_ai | no (by design) | - |
| f_L-1_097 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_098 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_099 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1b_083 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon_2 | living | added_by_ai | no (by design) | - |
| f_L-1b_084 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon_2 | living | added_by_ai | no (by design) | - |
| f_L-1b_085 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon_2 | living | added_by_ai | no (by design) | - |

## Views too dark for the EV cap (Milestone 13)

2 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 2 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

| view | room | severity | metered EV | EV used | cap | stops over | incident p50 | set_lighting |
|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_salon_1 | r_L-1_salon | major | +3.42 | +3.00 | +3.00 | 0.42 | 0.08435 | - |
| cam_r_L-1_salon_2 | r_L-1_salon | major | +3.07 | +3.00 | +3.00 | 0.07 | 0.10739 | - |

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |

Assets: textures CC0 x 18; furniture/decor models CC-BY-4.0 x 146, CC-BY-NC-4.0 x 91, CC0 x 2, generated (TRELLIS.2-4B, MIT) x 11 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1_051, f_L-1_052, f_L-1b_037, f_L-1b_038, f_L0_015, f_L0_016, f_L0_017, f_L0_018, f_L1_013, f_L1_014)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1b_020)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261017-072801-full-20261017T073330Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 41.9 s | earlier outputs without run records moved to /workspace/outputs-archive/real02-20261017T073330Z |
| pipeline | pending | 101.7 s | 48 recognition question(s) written (recognition/requests.json) |
| style | ok | 0.2 s | - |
| recognize | ok | 11.2 s | - |
| pipeline_final | ok | 105.2 s | answers applied |
| fit | ok | 4.5 s | - |
| layout | ok | 31.4 s | - |
| decor_ask | ok | 2.2 min | - |
| photos | ok | 3.4 s | - |
| assets | ok | 5.1 s | - |
| decor | ok | 5.6 s | - |
| refit | ok | 29.8 s | - |
| build | ok | 16.2 min | - |
| agent_previews | ok | 5.9 min | 4 view(s) |
| agent_apply | ok | 14.4 s | - |
| agent | ok | 28.4 min | 3 round(s), 24 finding(s) removed by 25 accepted edit(s) (measured; 32 predicted by the dry re-checks), 105 rejected; stop: max rounds reached |
| render | ok | 12.3 min | - |
| export | ok | 84.4 s | - |
| controls | ok | 2.5 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 98.0 s | - |
| check | ok | 3.4 min | - |
| combine | ok | 29.3 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 25 edit(s) accepted, 109 rejected, 440 model calls (5713776 tokens), 34.5 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 25 / 109 (19 % accepted) |
| rejected by reason | acceptance 38, drawn_lock 18, memory 17, retype 7, score 7 |
| rooms checked by code / vision / planner | 38 / 16 / 21 |
| rooms with fixable critical or major findings visited | 21 of 21 |
| critical before -> after | 2 -> 1 |
| major before -> after | 143 -> 122 |
| agent minutes; first accepted edit after | 29.19; 90.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 17; 149; 54 (29) |
| critical/major findings removed (measured by the next round; predicted by the dry re-checks) | 24 measured; 32 predicted |

Library gaps reported by the agent: shower (No audited library shower model fits the drawn 0.6×1.4 m footprint within tolerance; the parametric fixture is used by design.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 143 | 67 | 5 | 15 | 67 | refit | 23 |
| 2 | 2 | 126 | 65 | 3 | 8 | 17 | refit | 13 |
| 3 | 1 | 121 | 64 | 3 | 2 | 21 | refit | 4 |
| 4 | 1 | 122 | 64 | 1 | 0 | 4 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D1 | 0 | 0 | 2 | 0 |
| D2 | 0 | 4 | 0 | 1 |
| F1 | 0 | 13 | 11 | 2 |
| F2 | 0 | 8 | 0 | 0 |
| F3 | 0 | 32 | 4 | 0 |
| F4 | 0 | 26 | 0 | 0 |
| F6 | 0 | 13 | 0 | 0 |
| F8 | 0 | 36 | 0 | 0 |
| F9 | 0 | 82 | 0 | 5 |
| G1 | 0 | 8 | 32 | 0 |
| G10 | 0 | 72 | 0 | 0 |
| G11 | 0 | 12 | 0 | 0 |
| G13 | 0 | 16 | 0 | 0 |
| G14 | 0 | 0 | 11 | 0 |
| G2 | 0 | 16 | 24 | 0 |
| G3 | 0 | 8 | 0 | 0 |
| G6 | 0 | 24 | 16 | 0 |
| G7 | 0 | 0 | 16 | 0 |
| G8 | 0 | 16 | 16 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| LG | 0 | 0 | 56 | 0 |
| NR | 0 | 19 | 0 | 0 |
| R3 | 0 | 0 | 40 | 0 |
| RC | 0 | 0 | 24 | 0 |
| S2 | 0 | 57 | 0 | 0 |
| X2 | 4 | 14 | 8 | 0 |
| X3 | 0 | 8 | 0 | 4 |
| X6 | 0 | 7 | 0 | 0 |
| lighting_dark | 2 | 13 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 264 | 1 | mark_not_furniture | f_L-1_022 | adjusted_by_ai | 0.0 -> 0.0 | A 5.54 m long, 0.60 m deep band along the wall is a wall/outline element, not furniture. | ![](agent/r1_048_mark_not_furniture_before_r_L-1_salon_2.png) | ![](agent/r1_051_mark_not_furniture_after_r_L-1_salon_2.png) |
| 270 | 1 | rotate_piece | f_L-1_050 | adjusted_by_ai | 0.0 -> 0.0 | Turn the armchair to face the sofa group (currently 140° off the sofa_corner). | ![](agent/r1_055_rotate_piece_before_r_L-1_salon_2.png) | ![](agent/r1_057_rotate_piece_after_r_L-1_salon_2.png) |
| 276 | 1 | mark_not_furniture | f_L-1b_001 | adjusted_by_ai | 0.0 -> 0.0 | The 5.14 x 2.37 m cluster is larger than 4.5 m on a side and covers several drawn pieces; it is a group outline, not a single furniture item. | ![](agent/r1_061_mark_not_furniture_before_r_L-1b_salon_2.png) | ![](agent/r1_062_mark_not_furniture_after_r_L-1b_salon_2.png) |
| 295 | 1 | mark_not_furniture | f_L1_017 | adjusted_by_ai | 34.0 -> 34.0 | The 1.63x1.52m untyped drawn piece is a rug/play mat in a children's activity room, not furniture. | ![](agent/r1_078_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_079_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 316 | 1 | rotate_piece | f_L1_025 | adjusted_by_ai | 77.0 -> 87.0 | The chair at [11.65,9.9] should face the table at [12.61,9.9] which is in the +x direction (0°), not 180° away from it. | ![](agent/r1_087_rotate_piece_before_r_L1_koridor_2.png) | ![](agent/r1_088_rotate_piece_after_r_L1_koridor_2.png) |
| 331 | 1 | mark_not_furniture | f_L1_022 | adjusted_by_ai | 90.0 -> 100.0 | A 0.58×0.45 m chair cannot legitimately sit half through the wall on a 19.7 m² balcony; it is a misread symbol/mark, not furniture. | ![](agent/r1_093_mark_not_furniture_before_r_L1_teras.png) | ![](agent/r1_095_mark_not_furniture_after_r_L1_teras.png) |
| 332 | 1 | move_piece | f_L1_024 | adjusted_by_ai | 87.0 -> 87.0 | Move the table 0.11 m left to clear wall w_L1_006 (currently cuts by 0.052 m) and resolve the outline breach. | ![](agent/r1_096_move_piece_before_r_L1_koridor_2.png) | ![](agent/r1_097_move_piece_after_r_L1_koridor_2.png) |
| 338 | 1 | set_lighting | r_L0_yatak_odasi | agent_override | - | Camera view is 0.35 stops over the EV cap; the finding specifies factor x1.8 to bring exposure within the cap. | - | - |
| 350 | 1 | mark_not_furniture | f_L1_021 | adjusted_by_ai | 87.0 -> 100.0 | A coffee table is not a standard hall fixture; it cuts a wall and pokes through the outline, so it is a misread symbol, not furniture. | ![](agent/r1_107_mark_not_furniture_before_r_L1_koridor.png) | ![](agent/r1_108_mark_not_furniture_after_r_L1_koridor.png) |
| 355 | 1 | set_lighting | r_L0_koridor | agent_override | - | All three cameras report the room too dark (exposure over the +3.00 EV cap); x3 is the maximum required factor and satisfies all three views. | - | - |
| 357 | 1 | set_lighting | r_L-1_koridor_2 | agent_override | - | Both corridor cameras are under-exposed (+3.46/+3.42 EV vs +3.00 cap); x1.94 covers the darker view's x1.37 need plus headroom. | - | - |
| 360 | 1 | remove_piece | f_L0_035 | added_by_ai | 100.0 -> 100.0 | AI-added piece rendered as a low bench with cushion, wrong type for shoe_cabinet; bench is not a valid retype candidate for this size/zone, and the entrance group is optional, so remove it. | ![](agent/r1_111_remove_piece_before_r_L0_koridor.png) | ![](agent/r1_112_remove_piece_after_r_L0_koridor.png) |
| 362 | 1 | set_lighting | r_L0_e_yatak_odasi | agent_override | - | Room too dark for cam_r_L0_e_yatak_odasi_3 (wanted +3.30 EV vs +3.00 cap); finding specifies x1.74. | - | - |
| 387 | 1 | report_library_gap | f_L0_014 | library_gap | - | No audited library shower model fits the drawn 0.6×1.4 m footprint within tolerance; the parametric fixture is used by design. | - | - |
| 389 | 1 | set_camera | ext_6 | agent_override | - | Reposition ext_6 from a direct frontal single-facade shot to a 3/4 corner view so two facades (front and right side) are visible, per the X6 checklist requirement. | - | - |
| 647 | 2 | mark_not_furniture | f_L-1_024 | adjusted_by_ai | 0.0 -> 0.0 | The 2.57m x 0.6m strip is a misread wall/built-in detail, not a freestanding wardrobe; marking it not furniture removes the F9/F1/G14 findings. | ![](agent/r2_028_mark_not_furniture_before_r_L-1_salon.png) | ![](agent/r2_030_mark_not_furniture_after_r_L-1_salon.png) |
| 649 | 2 | mark_not_furniture | f_L-1_021 | adjusted_by_ai | 0.0 -> 0.0 | The 5.54m x 0.6m untyped strip is a built-in/wall element, not furniture; marking it not furniture resolves the untyped NR finding. | ![](agent/r2_031_mark_not_furniture_before_r_L-1_salon.png) | ![](agent/r2_032_mark_not_furniture_after_r_L-1_salon.png) |
| 663 | 2 | move_piece | f_L-1_038 | adjusted_by_ai | 0.0 -> 0.0 | nudge the dining table 0.13 m to clear the 0.039 m cuts with chairs f_L-1_039 and f_L-1_042 | ![](agent/r2_036_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_037_move_piece_after_r_L-1_salon_2.png) |
| 666 | 2 | mark_not_furniture | f_L1_018 | adjusted_by_ai | 34.0 -> 34.0 | Untyped 1.63x1.52 m drawn symbol was already passed as not furniture by the AI; marking it not furniture resolves the untyped review finding. | ![](agent/r2_040_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_041_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 692 | 2 | swap_model | f_L0_029 | adjusted_by_ai | 87.0 -> 87.0 | Replace the crude flat rectangular box model with a proper mid-century wood desk model to resolve the D2 wrong-model finding. | ![](agent/r2_067_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_068_swap_model_after_r_L0_yatak_odasi_3.png) |
| 695 | 2 | move_piece | f_L1_050 | added_by_ai | 34.0 -> 34.0 | move the bookshelf away from the sloped-ceiling corner so its 1.8 m top no longer shows through the roof | ![](agent/r2_069_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_071_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 709 | 2 | swap_model | f_L-1_090 | added_by_ai | 51.0 -> 51.0 | The AI fridge renders as a thin flat panel; swap to a real compact fridge model (0.49x0.59x1.0 m) that fits the 0.6 m slot and reads as a functional refrigerator. | ![](agent/r2_079_swap_model_before_r_L-1_mutfak.png) | ![](agent/r2_080_swap_model_after_r_L-1_mutfak.png) |
| 727 | 2 | set_camera | ext_6 | agent_override | - | Move ext_6 from a direct frontal angle to a 3/4 corner position so two facades (front and right side) are visible, satisfying the X6 checklist requirement. | - | - |
| 979 | 3 | move_piece | f_L-1_053 | adjusted_by_ai | 0.0 -> 0.0 | Move the sofa_corner right by 0.27m to clear the 0.108m cut with the sofa f_L-1_061. | ![](agent/r3_050_move_piece_before_r_L-1_salon.png) | ![](agent/r3_051_move_piece_after_r_L-1_salon.png) |
| 1040 | 3 | set_camera | ext_6 | agent_override | - | Move to a 3/4 corner angle so two facades are visible instead of a direct frontal view. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 253 | 1 | retype_piece | f_L-1_024 | acceptance: finding F9:f_L-1_024 is still there after the edit (sideboard reaches 0.05 m² through the room outline) | The 2.57m x 0.6m piece is a sideboard, not a wardrobe; it is a valid living room piece and re-typing resolves the room-type and wall-penetration findings. |
| 254 | 1 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The 5.54m x 0.6m untyped drawn piece is a long sideboard/storage unit, appropriate for a salon. |
| 255 | 1 | move_piece | f_L-1b_042 | snap: f_L-1b_042: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 1.95 m off the wall; snap its back onto the right wall (span s1) so it rests on the wall. |
| 256 | 1 | swap_model | f_L-1b_013 | acceptance: finding F9:f_L-1b_013 is still there after the edit (stove f_L-1b_013 overlaps kitchen_counter f_L-1b_009 by 0.41 m²) | Stove overlaps the kitchen counter by 0.41 m²; swap to a 0.50 m model that fits the counter slot without collision. |
| 258 | 1 | swap_model | f_L-1b_064 | acceptance: finding F9:f_L-1b_064 is still there after the edit (sink_kitchen f_L-1b_064 overlaps kitchen_counter f_L-1b_010 by 0.39 m²) | Sink overlaps the kitchen counter by 0.39 m²; swap to a 0.47 m deep model that fits the counter slot without collision. |
| 259 | 1 | move_piece | f_L-1_061 | drawn_lock: f_L-1_061: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.87 m) | Move the sofa away from the sofa_corner to resolve the 0.83m² overlap and the blocked clearance in front of it. |
| 260 | 1 | move_piece | f_L-1_060 | drawn_lock: f_L-1_060: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.51 m) | Move the overlapping coffee table to clear the collision with f_L-1_059 and help position the seating group correctly. |
| 261 | 1 | move_piece | f_L-1_061 | snap: f_L-1_061: no free place on wall w_L-1_007 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa's back to the west wall to clear the 0.83m² overlap with the sofa_corner and free its front clearance. |
| 262 | 1 | move_piece | f_L-1_060 | acceptance: finding G2:f_L-1_059 is still there after the edit (coffee table f_L-1_059 is not in front of the sofa) | Move the overlapping coffee table 0.26m to clear the collision with f_L-1_059. |
| 263 | 1 | retype_piece | f_L-1_023 | retype: tall_cabinet is no candidate for f_L-1_023 (2.57 x 0.60 m at [9.27, 7.14]): the size table and the room / zone give sideboard, tv_unit | Wardrobe is not a living-room piece and pokes 0.05 m² through the outline; a tall cabinet is a valid living-room storage piece of the same 2.57x0.60 footprint. |
| 265 | 1 | move_piece | f_L-1b_041 | snap: f_L-1b_041: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 2.00 m off the west wall; snap its back onto free span s4 (wall w_L-1b_010) at its drawn height so it rests on the wall. |
| 266 | 1 | move_piece | f_L-1b_042 | drawn_lock: f_L-1b_042: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.75 m) | Sofa back is 1.95 m off the wall; slide it 1.2 m right so its back rests on the right wall (span s1). |
| 267 | 1 | move_piece | f_L-1_061 | drawn_lock: f_L-1_061: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the sofa 0.3m away from the sofa_corner to reduce the 0.83m² overlap and free its front clearance. |
| 268 | 1 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.39 m) | Chair overlaps f_L-1b_052 and has only 0.09 m behind; shift it 0.39 m away from the table to clear the neighbour and gain the 0.81 m pull-out space. |
| 269 | 1 | swap_model | f_L-1b_007 | acceptance: finding F9:f_L-1b_007 is still there after the edit (stove f_L-1b_007 overlaps kitchen_counter f_L-1b_003 by 0.41 m²) | Stove overlaps kitchen_counter f_L-1b_003 by 0.41 m²; the 0.50 m-wide electric stove fits the drawn 0.75 m slot without collision. |
| 271 | 1 | move_piece | f_L-1_060 | memory: the same edit was rejected in round 1: acceptance: finding G2:f_L-1_059 is still there after the edit (coffee table f_L-1_059 is not in front of the sofa) | Move the overlapping coffee table 0.26m to clear the collision with f_L-1_059. |
| 272 | 1 | move_piece | f_L-1b_056 | drawn_lock: f_L-1b_056: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.39 m) | Chair overlaps f_L-1b_055 and f_L-1b_055 has only 0.09 m behind; shift f_L-1b_056 0.39 m away from the table to clear the neighbour and open the 0.81 m pull-out space for f_L-1b_055. |
| 273 | 1 | swap_model | f_L-1b_063 | acceptance: finding F9:f_L-1b_063 is still there after the edit (sink_kitchen f_L-1b_063 overlaps kitchen_counter f_L-1b_004 by 0.39 m²) | Sink overlaps kitchen_counter f_L-1b_004 by 0.39 m²; the 0.47 m-deep modern sink fits the drawn 0.5 m slot without collision. |
| 274 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_024 has 0.78 m behind it, needs ≥ 0.81 m; nudge 0.03 m away from the table to meet the clearance. |
| 275 | 1 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | no_place: r_L-1b_salon_2_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Kitchen run is missing its fridge (G9); complete the group so the solver places one. |
| 277 | 1 | move_piece | f_L-1_061 | max_tries: f_L-1_061 was edited 3 times in this round | Move the sofa 0.29m away from the sofa_corner to reduce the 0.83m² overlap and free its front clearance. |
| 278 | 1 | move_piece | f_L-1_060 | acceptance: finding G2:f_L-1_059 is still there after the edit (coffee table f_L-1_059 is not in front of the sofa) | Move the overlapping coffee table 0.29m to clear the collision with f_L-1_059. |
| 279 | 1 | retype_piece | f_L-1_023 | acceptance: finding F9:f_L-1_023 is still there after the edit (sideboard reaches 0.05 m² through the room outline) | Wardrobe is not a living-room piece and pokes 0.05 m² through the outline; a sideboard is a valid living-room storage piece of the same 2.57x0.60 footprint. |
| 281 | 1 | move_piece | f_L-1_023 | score: plausibility -42 -> -52 (F3 f_L-1_023: wardrobe: its back is not on a wall (0.22 m off); G13 f_L-1_023: wardrobe f_L-1_023: 0.70 m free in front, needs ≥ 0.80 m) | Pull the wardrobe 0.24 m off the top wall so it no longer reaches 0.05 m² through the room outline. |
| 282 | 1 | relayout_room | r_L-1_salon_2 | acceptance: finding F3:f_L-1_054 is still there after the edit (sofa_corner: its back is not on a wall (1.10 m off)) | Use the solver's best candidate to re-place the AI seating pieces so the sofas get wall backs, walkway access and the coffee tables sit in front. |
| 283 | 1 | retype_piece | f_L1_039 | retype: table_coffee is no candidate for f_L1_039 (0.70 x 0.70 m at [13.90, 5.75]): the size table and the room / zone give chair, floor_lamp, potted_plant, side_table, table_dining | 0.7x0.7 m table is a small side/coffee table, not a dining table, on a terrace. |
| 284 | 1 | retype_piece | f_L1_040 | retype: armchair is no candidate for f_L1_040 (0.45 x 0.45 m at [13.90, 5.13]): the size table and the room / zone give chair, floor_lamp, potted_plant, side_table | Chair on a terrace is a lounge armchair, not part of a dining set. |
| 285 | 1 | retype_piece | f_L1_041 | retype: armchair is no candidate for f_L1_041 (0.45 x 0.45 m at [13.90, 6.38]): the size table and the room / zone give chair, floor_lamp, potted_plant, side_table | Chair on a terrace is a lounge armchair, not part of a dining set. |
| 286 | 1 | retype_piece | f_L1_039 | room_type: side_table is not a piece a balcony room may hold here | 0.7x0.7 m table is a small side table, not a dining table, on a terrace. |
| 287 | 1 | remove_piece | f_L1_040 | score: plausibility 100 -> 97 (G6 f_L1_039: dining table f_L1_039 has 1 of 2 chairs) | AI-added chair not part of a functional dining set on the terrace; removing it resolves the F1 finding. |
| 288 | 1 | remove_piece | f_L1_041 | score: plausibility 100 -> 97 (G6 f_L1_039: dining table f_L1_039 has 1 of 2 chairs) | AI-added chair not part of a functional dining set on the terrace; removing it resolves the F1 finding. |
| 290 | 1 | remove_piece | f_L1_039 | score: plausibility 100 -> 80 (F8 f_L1_040: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m); F8 f_L1_041: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m)) | AI-added 0.7x0.7 m table is a small side table, not a dining table, on a terrace; removing it resolves the F1 finding and the orphaned chairs. |
| 293 | 1 | remove_piece | f_L1_040 | memory: the same edit was rejected in round 1: score: plausibility 100 -> 97 (G6 f_L1_039: dining table f_L1_039 has 1 of 2 chairs) | AI-added chair not part of a functional dining set on the terrace; removing it resolves the F1 finding. |
| 294 | 1 | remove_piece | f_L1_041 | memory: the same edit was rejected in round 1: score: plausibility 100 -> 97 (G6 f_L1_039: dining table f_L1_039 has 1 of 2 chairs) | AI-added chair not part of a functional dining set on the terrace; removing it resolves the F1 finding. |
| 298 | 1 | retype_piece | f_L1_040 | room_type: potted_plant is not a piece a balcony room may hold here | 0.45x0.45 m piece on a terrace is a potted plant, not a chair of a dining set. |
| 299 | 1 | retype_piece | f_L1_041 | room_type: potted_plant is not a piece a balcony room may hold here | 0.45x0.45 m piece on a terrace is a potted plant, not a chair of a dining set. |
| 300 | 1 | rotate_piece | f_L1_025 | acceptance: finding F4:f_L1_025 is still there after the edit (chair does not face its group (f_L1_024)) | Rotate the chair to face the table (front_deg 90) to resolve the orientation mismatch with its group anchor. |
| 301 | 1 | mark_not_furniture | f_L1_024 | acceptance: finding RC:f_L1_024 is still there after the edit (f_L1_024: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes)) | The piece is a misread symbol (AI typed it as bench, but it is a table with chairs in a hall). Marking it as not furniture removes the collision, outline breach, and type errors. |
| 302 | 1 | retype_piece | f_L1_040 | max_tries: f_L1_040 was edited 3 times in this round | 0.45x0.45 m piece on a terrace is a floor lamp, not a chair of a dining set. |
| 317 | 1 | retype_piece | f_L1_024 | retype: console_table is no candidate for f_L1_024 (1.20 x 0.70 m at [12.61, 9.90]): the size table and the room / zone give none | A table_coffee is not appropriate for a hall; a console_table fits the hall context and resolves F1, G14, and RC findings. |
| 337 | 1 | move_piece | f_L0_010 | score: plausibility 87 -> 67 (F3 f_L0_010: wardrobe: its back is not on a wall (0.14 m off); F9 f_L0_010: wardrobe reaches 0.20 m² through the room outline; G13 f_L0_010: wardrobe f_L0_010: 0.79 m free in front, needs ≥ 0.80 m) | Increase front clearance from 0.66 m to 0.80 m by shifting wardrobe 0.14 m away from the front wall. |
| 339 | 1 | swap_model | f_L-1_008 | acceptance: finding F9:f_L-1_008 is still there after the edit (stove f_L-1_008 overlaps kitchen_counter f_L-1_002 by 0.41 m²) | Swap the stove to the CC0 electric stove (0.50x0.65) so its footprint no longer overlaps kitchen_counter f_L-1_002 (F9, 0.41 m²). |
| 342 | 1 | swap_model | f_L-1_067 | acceptance: finding F9:f_L-1_067 is still there after the edit (sink_kitchen f_L-1_067 overlaps kitchen_counter f_L-1_003 by 0.39 m²) | Swap the sink to a 1.00x0.47 model so its footprint no longer overlaps kitchen_counter f_L-1_003 (F9, 0.39 m²). |
| 343 | 1 | remove_piece | f_L-1_090 | score: plausibility 51 -> 47 (G9 r_L-1_mutfak: kitchen r_L-1_mutfak has no fridge (fridge)) | The AI-added fridge renders as a thin flat panel, not a recognizable refrigerator (v:r1-v2:1 wrong_type); removing it clears the visual error. |
| 344 | 1 | fix_fixture | f_L-1_001 | fixture_place: f_L-1_001: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_003) | Nudge the drawn counter out of door d_L-1_003's swing so the door opens fully (R3 blocked opening on one hinge side). |
| 348 | 1 | move_piece | f_L0_010 | acceptance: finding G13:f_L0_010 is still there after the edit (wardrobe f_L0_010: 0.64 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.3 m along the top wall toward the door to increase front clearance from 0.66 m to 0.80 m while keeping its back on the wall. |
| 352 | 1 | move_piece | f_L0_010 | acceptance: finding G13:f_L0_010 is still there after the edit (wardrobe f_L0_010: 0.64 m free in front, needs ≥ 0.80 m) | Move wardrobe to the far end of the top wall (away from the door swing) to increase front clearance to 0.80 m. |
| 354 | 1 | retype_piece | f_L0_035 | retype: bench is no candidate for f_L0_035 (0.60 x 0.30 m at [3.49, 9.06]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet, side_table | Rendered as a low bench with a cushion, not a shoe cabinet; retype to bench to match the visual evidence. |
| 356 | 1 | move_piece | f_L0_010 | max_tries: f_L0_010 was edited 3 times in this round | Move wardrobe to the right wall (s1) near the top corner where the front faces into open room space, giving 0.80 m+ clearance. |
| 364 | 1 | move_piece | f_L0_011 | drawn_lock: f_L0_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift wardrobe 0.3 m toward the wall to open the required 0.80 m front clearance (G13). |
| 365 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.3 m along its wall to open the 0.80 m clearance in front (currently 0.66 m). |
| 369 | 1 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 370 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.3 m the other way along its wall (toward the corner) to open the 0.80 m clearance in front (currently 0.66 m). |
| 371 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall) | Shower front faced 90° into a wall 0.10 m away; turning it to face 270° (into the room) clears the F4 orientation error and opens the front use zone. |
| 372 | 1 | move_piece | f_L0_012 | drawn_lock: f_L0_012: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Pull the wardrobe 0.3 m off the wall into the room to open the 0.80 m clearance in front (currently 0.66 m). |
| 373 | 1 | move_piece | f_L0_012 | max_tries: f_L0_012 was edited 3 times in this round | Pull the wardrobe 0.29 m off the wall into the room to open the 0.80 m clearance in front (currently 0.66 m). |
| 374 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 375 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 378 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 380 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 382 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 384 | 1 | swap_model | f_L0_014 | acceptance: finding LG:f_L0_014 is still there after the edit (library gap for shower: reason no shower candidate within 10 % non-uniform scale (Milestone 13: the depth mismatch of the uniform scale to the drawn width) and ) | The parametric shower (0.6×1.4) is too deep for the 1.5 m room; trying a generated model with a more balanced footprint to see if it resolves the F4 orientation error. |
| 386 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 388 | 1 | move_piece | f_L0_011 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Snap wardrobe back onto wall w_L0_004 to open the required 0.80 m front clearance (G13). |
| 391 | 1 | set_exterior | exterior:roof | acceptance: finding X2:d_L1_004 is still there after the edit (door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.17 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.) | Replace the mansard roof (knee wall 0.925 m, underside only 1.10 m above the L1 floor) with a gable roof of the same 40.4° pitch so the roof underside clears the 2.10 m door tops at d_L1_004 and d_L1_005, providing the dormer-equivalent headroom the finding requires. |
| 392 | 1 | set_exterior | exterior:roof | acceptance: finding X2:d_L1_004 is still there after the edit (door height not drawn: its top 2.10 m above the floor would reach over the roof underside (0.30 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.) | Try a flat roof so the roof underside sits at the top-floor ceiling (3.433 m above the L1 floor) instead of the mansard knee wall (1.10 m), clearing the 2.10 m door tops at d_L1_004 and d_L1_005. |
| 393 | 1 | set_exterior | exterior:roof | a gable roof at 70 degrees (5-60) | Test whether a steeper gable (70 deg) raises the roof underside at the wall enough to clear the 2.10 m door tops at d_L1_004 and d_L1_005, since the 40.4 deg gable only reached 1.17 m. |
| 652 | 2 | move_piece | f_L-1_061 | acceptance: finding F9:f_L-1_061 is still there after the edit (sofa f_L-1_061 overlaps sofa_corner f_L-1_053 by 0.44 m²); 1 more kept | Move the sofa 0.3 m left to clear the 0.83 m² overlap with the sofa_corner and unblock its front clearance zone. |
| 657 | 2 | move_piece | f_L-1_061 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1_061: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the sofa 0.3 m down to clear the overlap with the sofa_corner's chaise and unblock its front clearance zone. |
| 660 | 2 | move_piece | f_L-1_061 | acceptance: finding F9:f_L-1_061 is still there after the edit (sofa f_L-1_061 overlaps sofa_corner f_L-1_053 by 0.56 m²); 1 more kept | Move the sofa diagonally 0.3 m (left and down) to clear the overlap with the sofa_corner's chaise and unblock its front clearance. |
| 664 | 2 | move_piece | f_L-1_060 | acceptance: finding G2:f_L-1_059 is still there after the edit (coffee table f_L-1_059 is not in front of the sofa) | Move the coffee table 0.3 m up to clear the 0.12 m² overlap with f_L-1_059. |
| 665 | 2 | remove_piece | f_L1_058 | acceptance: finding X2:f_L1_058 is still there after the edit (furn_f_L1_058 pokes through the roof (top 5.17 m)) | AI-added bookshelf pokes through the sloped ceiling (top 5.17 m vs 0.80 m ceiling); removing it resolves the critical roof penetration and ceiling show-through. |
| 668 | 2 | move_piece | f_L-1_059 | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the coffee table 0.3 m up toward the sofa's front to place it in front of the sofa and clear the overlap with f_L-1_060. |
| 669 | 2 | move_piece | f_L-1_059 | acceptance: finding G2:f_L-1_059 is still there after the edit (coffee table f_L-1_059 is not in front of the sofa) | Move the coffee table 0.29 m up toward the sofa's front to place it in front of the sofa. |
| 673 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F3:f_L1_009 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 5 more kept | Re-solve the drawn seating groups so the sofa f_L1_009 sits back-on-wall facing its coffee tables and the TV unit f_L1_033 aligns with sofa f_L1_012's axis with a coffee table added. |
| 674 | 2 | move_piece | f_L-1_070 | drawn_lock: f_L-1_070: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.49 m) | Move the floating coffee table 0.49 m left to associate it with the seating area and clear the 0.076 m cut with the ottoman. |
| 676 | 2 | move_piece | f_L-1_070 | f_L-1_073: no_overlap, score: plausibility -9 -> -19 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps table_coffee f_L-1_070 by 0.07 m²) | Move the floating coffee table 0.3 m left to associate it with the seating area and reduce the cut with the ottoman. |
| 679 | 2 | move_piece | f_L-1_073 | f_L-1_073: no_overlap, score: plausibility -9 -> -19 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps table_coffee f_L-1_071 by 0.09 m²) | Move the floating coffee table 0.3 m left to associate it with the seating area and resolve the floating finding. |
| 681 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding F3:f_L1_010 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 4 more kept | Re-solve the seating groups around the drawn anchors to fix the off-wall/mis-oriented sofa, the coffee table not in front of the sofa, the floating coffee tables and the TV unit off-axis. |
| 691 | 2 | swap_model | f_L0_029 | asset_type: gen_potted_plant_japandi_2_9a3effd1 is a potted_plant model, not a desk | The crude flat rectangular box next to the desk is a misread wall lamp; a small potted plant is the plausible object at that spot and removes the D2 wrong-model finding. |
| 699 | 2 | swap_model | f_L-1_008 | acceptance: finding F9:f_L-1_008 is still there after the edit (stove f_L-1_008 overlaps kitchen_counter f_L-1_002 by 0.41 m²) | Swap the stove to a model whose footprint fits the drawn 0.75 m slot so it no longer overlaps counter f_L-1_002 (electric_stove was rejected: still 0.41 m² overlap). |
| 704 | 2 | swap_model | f_L-1_067 | acceptance: finding F9:f_L-1_067 is still there after the edit (sink_kitchen f_L-1_067 overlaps kitchen_counter f_L-1_003 by 0.39 m²) | Swap the sink to a model whose footprint fits the drawn 0.79 m slot so it no longer overlaps counter f_L-1_003 (modern_2 was rejected: still 0.39 m² overlap). |
| 711 | 2 | fix_fixture | f_L-1_001 | memory: the same edit was rejected in round 1: fixture_place: f_L-1_001: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_003) | Door d_L-1_003 swings into the counter on one hinge side; nudge the counter to the nearest valid spot to clear the swing. |
| 713 | 2 | fix_fixture | f_L-1_001 | fixture_place: f_L-1_001 at [2.82, 10.20] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Door d_L-1_003 swings into the counter on one hinge side; shift the counter 0.23 m along its wall to clear the swing (code auto-move found no valid spot, so give an explicit in-room centre). |
| 955 | 3 | rotate_piece | f_L-1_049 | score: plausibility -9 -> -19 (G3 f_L-1_049: armchair f_L-1_049 is 99° off the table_coffee f_L-1_087 (needs ≤ 30°) at 0.53 m (needs ≤ 2.50 m); G11 f_L-1_049: armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Face the armchair toward the coffee table f_L-1_087 and the sofa group to fix F4 and G3 orientation findings. |
| 956 | 3 | move_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: snap: f_L-1b_041: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 2.00 m off a wall; snap its back onto the free left wall span w_L-1b_010 (into_room 0°) so it faces the room. |
| 958 | 3 | rotate_piece | f_L-1_049 | acceptance: finding F4:f_L-1_049 is still there after the edit (armchair does not face its group (f_L-1_087, f_L-1_053, f_L-1_061)) | Face the armchair north toward the coffee table f_L-1_087 and the sofa group to fix F4 and G3 orientation findings. |
| 959 | 3 | move_piece | f_L-1b_041 | drawn_lock: f_L-1b_041: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.74 m) | Sofa back is 2.00 m off a wall; slide it 0.3 m left so its back sits on the free left wall span w_L-1b_010 (into_room 0°), within the 0.3 m move allowance. |
| 960 | 3 | rotate_piece | f_L-1_049 | memory: the same edit was rejected in round 3: score: plausibility -9 -> -19 (G3 f_L-1_049: armchair f_L-1_049 is 99° off the table_coffee f_L-1_087 (needs ≤ 30°) at 0.53 m (needs ≤ 2.50 m); G11 f_L-1_049: armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Face the armchair NW toward the coffee table f_L-1_087 and the sofa group to fix F4 and G3 orientation findings. |
| 961 | 3 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | Chair f_L-1b_059 overlaps f_L-1b_058 and f_L-1b_058 has only 0.09 m clearance behind; nudge f_L-1b_059 0.36 m away from f_L-1b_058 to clear the collision and open the 0.81 m clearance for f_L-1b_058. |
| 963 | 3 | rotate_piece | f_L-1_049 | acceptance: finding F4:f_L-1_049 is still there after the edit (armchair does not face its group (f_L-1_087, f_L-1_053, f_L-1_061)) | Face the armchair NNW toward the coffee table f_L-1_087 and the sofa group to fix F4 and G3 orientation findings. |
| 965 | 3 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Chair f_L-1b_059 overlaps f_L-1b_058 and f_L-1b_058 has only 0.09 m clearance behind; nudge f_L-1b_059 0.3 m away from f_L-1b_058 to clear the collision and open the 0.81 m clearance for f_L-1b_058. |
| 966 | 3 | rotate_piece | f_L-1_049 | max_tries: f_L-1_049 was edited 3 times in this round | Face the armchair NNE toward the coffee table f_L-1_087 and the sofa group to fix F4 and G3 orientation findings. |
| 969 | 3 | move_piece | f_L-1_061 | drawn_lock: f_L-1_061: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.51 m) | Move the sofa left to clear the 0.83m² overlap with the sofa_corner f_L-1_053 and unblock its front clearance zone. |
| 970 | 3 | move_piece | f_L-1b_059 | acceptance: finding G6:f_L-1b_058 is still there after the edit (chair f_L-1b_058: 0.09 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_059 overlaps f_L-1b_058 and f_L-1b_058 has only 0.09 m clearance behind; nudge f_L-1b_059 0.29 m away from f_L-1b_058 to clear the collision and open the 0.81 m clearance for f_L-1b_058. |
| 971 | 3 | remove_piece | f_L1_058 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_058 is still there after the edit (furn_f_L1_058 pokes through the roof (top 5.17 m)) | AI-added bookshelf pokes through the sloped ceiling (0.80 m high at its location); removing it clears the critical roof-penetration and under-roof findings. |
| 973 | 3 | move_piece | f_L-1_061 | snap: f_L-1_061: no free place on wall w_L-1_007 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa to the left wall to clear the 0.83m² overlap with the sofa_corner f_L-1_053 and unblock its front clearance zone. |
| 974 | 3 | move_piece | f_L-1b_058 | drawn_lock: f_L-1b_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Chair f_L-1b_058 has only 0.09 m clearance behind (needs 0.81 m) and overlaps f_L-1b_059; nudge it 0.31 m away from the table edge to open the 0.81 m clearance and clear the collision. |
| 976 | 3 | move_piece | f_L-1_053 | drawn_lock: f_L-1_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the sofa_corner right by 0.3m to clear the 0.108m cut with the sofa f_L-1_061. |
| 977 | 3 | move_piece | f_L-1b_058 | drawn_lock: f_L-1b_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Chair f_L-1b_058 has only 0.09 m clearance behind (needs 0.81 m) and overlaps f_L-1b_059; nudge it 0.3 m away from the table edge to open the 0.81 m clearance and clear the collision. |
| 980 | 3 | move_piece | f_L-1b_058 | acceptance: finding G6:f_L-1b_058 is still there after the edit (chair f_L-1b_058 is 60° off the table f_L-1b_057 (needs ≤ 45°)) | Chair f_L-1b_058 has only 0.09 m clearance behind (needs 0.81 m) and overlaps f_L-1b_059; nudge it 0.29 m away from the table edge to open the 0.81 m clearance and clear the collision. |
| 982 | 3 | move_piece | f_L-1_070 | f_L-1_073: no_overlap, score: plausibility -9 -> -19 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps table_coffee f_L-1_070 by 0.07 m²) | Move the floating coffee table left to associate it with the seating area and clear the 0.076m cut with the ottoman f_L-1_075. |
| 986 | 3 | move_piece | f_L-1_070 | f_L-1_070: inside_room | Move the floating coffee table right to associate it with the seating area and clear the 0.076m cut with the ottoman f_L-1_075. |
| 1043 | 3 | set_exterior | exterior:roof | acceptance: finding X2:d_L1_004 is still there after the edit (door height not drawn: its top 2.10 m above the floor would reach over the roof underside (0.90 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.) | Raise the roof underside at the L1 terrace wall so the 2.10 m doors d_L1_004/005 fit under it (a gable keeps the eaves high along the full wall, unlike the mansard knee wall that clips the door tops). |
| 1044 | 3 | set_exterior | exterior:roof | acceptance: finding X2:d_L1_004 is still there after the edit (door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.19 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.) | Restore the drawn mansard roof (the gable attempt lowered the underside to 0.90 m and added new ceiling findings); the mansard is the plan-drawn roof and the door issue needs a dormer, which is a review item. |
| 1254 | 4 | remove_piece | f_L1_058 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_058 is still there after the edit (furn_f_L1_058 pokes through the roof (top 5.17 m)) | AI-added bookshelf pokes through the sloped ceiling (0.80 m high at its location); removing it clears the roof penetration. |
| 1257 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 2: acceptance: finding F3:f_L1_010 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 4 more kept | Re-solve seating groups to put the sofa against a wall, orient it, place the coffee table in front, align the TV unit, and re-place the bookshelf to a full-height spot. |
| 1258 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding F3:f_L1_010 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 7 more kept | Re-solve seating groups (candidate 3) to put the sofa against a wall, orient it, place the coffee table in front, and align the TV unit. |
| 1259 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_010: clearance_ok, group checks: F6 f_L1_010: sofa: the free zone in front of it is blocked by f_L1_059, f_L1_060 | Re-solve seating groups (candidate 2) to put the sofa against a wall, orient it, place the coffee table in front, and align the TV unit. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| G8 | minor | f_L-1_067 | r_L-1_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_068 | r_L-1_mutfak_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_090 | r_L-1_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_096 | r_L-1_mutfak_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| S2 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L1_021 | r_L1_koridor | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | major | f_L1_024 | r_L1_koridor_2 | - | within_tolerance | 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| lighting_dark | critical | cam_r_L-1_salon_1 | r_L-1_salon | - | lighting_beyond_cap | 1, 2, 3 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |
| lighting_dark | major | cam_r_L-1_salon_2 | r_L-1_salon | - | lighting_beyond_cap | 1, 2 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1_salon_2 | cut | 1 | 10847 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 16452 | 32768 |
| 2 | r_L-1_salon | cut | 1 | 12102 | 32768 |
| 3 | r_L-1b_salon | cut | 1 | 16452 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | reason |
|---|---|---|---|---|---|
| f_L-1_006 | piece | unknown | r_L-1_mutfak | inferred | - |
| f_L-1_007 | piece | unknown | r_L-1_mutfak | inferred | - |
| f_L-1_009 | piece | sink_kitchen | r_L-1_mutfak | inferred | - |
| f_L-1_015 | piece | unknown | r_L-1_mutfak_2 | inferred | - |
| f_L-1_016 | piece | unknown | r_L-1_mutfak_2 | inferred | - |
| f_L-1_018 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - |
| f_L-1_021 | piece | unknown | r_L-1_salon | adjusted_by_ai | The 5.54m x 0.6m untyped strip is a built-in/wall element, not furniture; marking it not furniture resolves the untyped NR finding. |
| f_L-1_022 | piece | unknown | r_L-1_salon_2 | adjusted_by_ai | A 5.54 m long, 0.60 m deep band along the wall is a wall/outline element, not furniture. |
| f_L-1_023 | piece | wardrobe | r_L-1_salon_2 | adjusted_by_ai | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_024 | piece | wardrobe | r_L-1_salon | adjusted_by_ai | The 2.57m x 0.6m strip is a misread wall/built-in detail, not a freestanding wardrobe; marking it not furniture removes the F9/F1/G14 findings. |
| f_L-1_038 | piece | table_dining | r_L-1_salon_2 | adjusted_by_ai | nudge the dining table 0.13 m to clear the 0.039 m cuts with chairs f_L-1_039 and f_L-1_042 |
| f_L-1_050 | piece | armchair | r_L-1_salon_2 | adjusted_by_ai | Turn the armchair to face the sofa group (currently 140° off the sofa_corner). |
| f_L-1_051 | piece | toilet | r_L-1_banyo | inferred | - |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred, adjusted_by_ai | Move the sofa_corner right by 0.27m to clear the 0.108m cut with the sofa f_L-1_061. |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred | - |
| f_L-1_057 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1_058 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1_059 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_060 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_061 | piece | sofa | r_L-1_salon | inferred, adjusted_by_ai | size snap: the drawn sofa 1.30 x 0.63 m is outside its product range (depth 0.63 m is 11 % outside 0.7-1.1 m; nearest real product 1.30 x 0.85 m); nearest real product 1.30 x 0.85 x 0.85 m (small 2-seat 130) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_062 | piece | sofa | r_L-1_salon_2 | inferred, adjusted_by_ai | size snap: the drawn sofa 1.30 x 0.63 m is outside its product range (depth 0.63 m is 11 % outside 0.7-1.1 m; nearest real product 1.30 x 0.85 m); nearest real product 1.30 x 0.85 x 0.85 m (small 2-seat 130) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_063 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_065 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1_069 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1_070 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_071 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_072 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_074 | piece | table_coffee | r_L-1_salon_2 | inferred, adjusted_by_ai | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_079 | piece | ottoman | r_L-1_salon_2 | inferred | - |
| f_L-1_080 | piece | ottoman | r_L-1_salon | inferred | - |
| f_L-1_081 | piece | sink_kitchen | r_L-1_mutfak | inferred | - |
| f_L-1_082 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - |
| f_L-1_083 | piece | sink_kitchen | r_L-1_mutfak | inferred | - |
| f_L-1_084 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - |
| f_L-1_087 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_088 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1b_001 | piece | unknown | r_L-1b_salon_2 | adjusted_by_ai | The 5.14 x 2.37 m cluster is larger than 4.5 m on a side and covers several drawn pieces; it is a group outline, not a single furniture item. |
| f_L-1b_008 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - |
| f_L-1b_014 | piece | sink_kitchen | r_L-1b_salon | inferred | - |
| f_L-1b_037 | piece | toilet | r_L-1b_banyo_2 | inferred | - |
| f_L-1b_038 | piece | toilet | r_L-1b_banyo | inferred | - |
| f_L-1b_039 | piece | bar_stool | r_L-1b_salon_2 | inferred | - |
| f_L-1b_040 | piece | bar_stool | r_L-1b_salon | inferred | - |
| f_L-1b_041 | piece | sofa | r_L-1b_salon_2 | inferred | - |
| f_L-1b_042 | piece | sofa | r_L-1b_salon | inferred | - |
| f_L-1b_043 | piece | bathtub | r_L-1b_banyo_2 | inferred | - |
| f_L-1b_044 | piece | bathtub | r_L-1b_banyo | inferred | - |
| f_L-1b_047 | piece | chair | r_L-1b_salon_2 | inferred | - |
| f_L-1b_048 | piece | table_dining | r_L-1b_salon_2 | inferred | - |
| f_L-1b_049 | piece | chair | r_L-1b_salon | inferred | - |
| f_L-1b_050 | piece | table_dining | r_L-1b_salon | inferred | - |
| f_L-1b_051 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_052 | piece | chair | r_L-1b_salon | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_053 | piece | chair | r_L-1b_salon | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_054 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_055 | piece | chair | r_L-1b_salon | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_056 | piece | chair | r_L-1b_salon | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_057 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_058 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_059 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_060 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_061 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_062 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_065 | piece | unknown | r_L-1b_salon_2 | inferred | - |
| f_L-1b_066 | piece | unknown | r_L-1b_salon | inferred | - |
| f_L-1b_067 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - |
| f_L-1b_068 | piece | sink_kitchen | r_L-1b_salon | inferred | - |
| f_L-1b_069 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - |
| f_L-1b_070 | piece | sink_kitchen | r_L-1b_salon | inferred | - |
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | the drawn bed_double f_L0_007 overlaps floor_lamp f_L0_032 by 0.06 m² (outside its group): re-solved with its sleeping_double group as one unit around the drawn anchor (anchor); moved 0.10 m, sized 1.80 x 2.00 m -> 1.60 x 2.00 m (a real product size) |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | the drawn bed_double f_L0_008 overlaps floor_lamp f_L0_034 by 0.06 m² (outside its group): re-solved with its sleeping_double group as one unit around the drawn anchor (anchor); moved 0.10 m, sized 1.80 x 2.00 m -> 1.60 x 2.00 m (a real product size) |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred | - |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred | - |
| f_L0_016 | piece | toilet | r_L0_e_banyo_2 | inferred | - |
| f_L0_017 | piece | toilet | r_L0_banyo_2 | inferred | - |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred | - |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred | - |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred | - |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred | - |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred | - |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred | - |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | Replace the crude flat rectangular box model with a proper mid-century wood desk model to resolve the D2 wrong-model finding. |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred | - |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_005 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_006 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_013 | piece | toilet | r_L1_banyo | inferred | - |
| f_L1_014 | piece | toilet | r_L1_banyo_2 | inferred | - |
| f_L1_015 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_016 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_017 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | The 1.63x1.52m untyped drawn piece is a rug/play mat in a children's activity room, not furniture. |
| f_L1_018 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | Untyped 1.63x1.52 m drawn symbol was already passed as not furniture by the AI; marking it not furniture resolves the untyped review finding. |
| f_L1_019 | piece | bathtub | r_L1_banyo | inferred | - |
| f_L1_020 | piece | bathtub | r_L1_banyo_2 | inferred | - |
| f_L1_021 | piece | table_coffee | r_L1_koridor | adjusted_by_ai | A coffee table is not a standard hall fixture; it cuts a wall and pokes through the outline, so it is a misread symbol, not furniture. |
| f_L1_022 | piece | chair | r_L1_teras | adjusted_by_ai | A 0.58×0.45 m chair cannot legitimately sit half through the wall on a 19.7 m² balcony; it is a misread symbol/mark, not furniture. |
| f_L1_024 | piece | table_coffee | r_L1_koridor_2 | adjusted_by_ai | Move the table 0.11 m left to clear wall w_L1_006 (currently cuts by 0.052 m) and resolve the outline breach. |
| f_L1_025 | piece | chair | r_L1_koridor_2 | adjusted_by_ai | The chair at [11.65,9.9] should face the table at [12.61,9.9] which is in the +x direction (0°), not 180° away from it. |
| f_L1_027 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_028 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_029 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_030 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_031 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_032 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_033 | piece | tv_unit | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_035 | piece | tv_unit | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_036 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_037 | piece | unknown | r_L1_koridor | inferred | - |
| f_L1_038 | piece | unknown | r_L1_koridor | inferred | - |
| f_L-1_090 | piece | fridge | r_L-1_mutfak | adjusted_by_ai | The AI fridge renders as a thin flat panel; swap to a real compact fridge model (0.49x0.59x1.0 m) that fits the 0.6 m slot and reads as a functional refrigerator. |
| f_L1_050 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | move the bookshelf away from the sloped-ceiling corner so its 1.8 m top no longer shows through the roof |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_koridor_2_1 | ![](agent/r1_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_1_after.jpg) |
| 1 | cam_r_L-1_koridor_2_2 | ![](agent/r1_cam_r_L-1_koridor_2_2_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_2_after.jpg) |
| 1 | cam_r_L-1_koridor_2_3 | ![](agent/r1_cam_r_L-1_koridor_2_3_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_3_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_koridor_1 | ![](agent/r1_cam_r_L0_koridor_1_before.jpg) | ![](agent/r1_cam_r_L0_koridor_1_after.jpg) |
| 1 | cam_r_L0_koridor_2 | ![](agent/r1_cam_r_L0_koridor_2_before.jpg) | ![](agent/r1_cam_r_L0_koridor_2_after.jpg) |
| 1 | cam_r_L0_koridor_3 | ![](agent/r1_cam_r_L0_koridor_3_before.jpg) | ![](agent/r1_cam_r_L0_koridor_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_1 | ![](agent/r1_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_2 | ![](agent/r1_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3 | ![](agent/r1_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L1_koridor_1 | ![](agent/r1_cam_r_L1_koridor_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_1_after.jpg) |
| 1 | cam_r_L1_koridor_2 | ![](agent/r1_cam_r_L1_koridor_2_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_after.jpg) |
| 1 | cam_r_L1_koridor_2_1 | ![](agent/r1_cam_r_L1_koridor_2_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_1_after.jpg) |
| 1 | cam_r_L1_koridor_2_2 | ![](agent/r1_cam_r_L1_koridor_2_2_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_2_after.jpg) |
| 1 | cam_r_L1_koridor_2_3 | ![](agent/r1_cam_r_L1_koridor_2_3_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_3_after.jpg) |
| 1 | cam_r_L1_koridor_3 | ![](agent/r1_cam_r_L1_koridor_3_before.jpg) | ![](agent/r1_cam_r_L1_koridor_3_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 1 | ext_6 | ![](agent/r1_ext_6_before.jpg) | ![](agent/r1_ext_6_after.jpg) |
| 2 | cam_r_L-1_mutfak_1 | ![](agent/r2_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_1_after.jpg) |
| 2 | cam_r_L-1_mutfak_2 | ![](agent/r2_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_2_after.jpg) |
| 2 | cam_r_L-1_mutfak_3 | ![](agent/r2_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_3_after.jpg) |
| 2 | cam_r_L-1_salon_1 | ![](agent/r2_cam_r_L-1_salon_1_before.jpg) | ![](agent/r2_cam_r_L-1_salon_1_after.jpg) |
| 2 | cam_r_L-1_salon_2 | ![](agent/r2_cam_r_L-1_salon_2_before.jpg) | ![](agent/r2_cam_r_L-1_salon_2_after.jpg) |
| 2 | cam_r_L-1_salon_3 | ![](agent/r2_cam_r_L-1_salon_3_before.jpg) | ![](agent/r2_cam_r_L-1_salon_3_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r2_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r2_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r2_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 2 | ext_6 | ![](agent/r2_ext_6_before.jpg) | ![](agent/r2_ext_6_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | ext_6 | ![](agent/r3_ext_6_before.jpg) | ![](agent/r3_ext_6_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- ext_6.001: JSON cross-check not computed (camera not in the scene manifest)
