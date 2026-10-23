# Final report: real02

41 views: 0 polished, 41 Cycles (gate_validation 6, not_run 35). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 41 |
| interior / exterior views | 35 / 6 |
| variant | base |
| polished | 0 |
| Cycles | 41 (gate_validation 6, not_run 35) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 1 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 20 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.50 .. +3.00 EV (1 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 1 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 20 view(s), -3 .. 0 EV |
| interior glazing pull | - |
| camera policy | m5 6, search 35 |
| camera score (min / mean / max) | 1.21 / 2.57 / 3.49 |
| rooms by number of views | 1 with 0, 2 with 1, 3 with 2, 9 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 5.6 min / 8.1 min / 2.2 min |
| seconds: polish / gate / check | - / - / 13.5 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real02.blend](3d/real02.blend) | 441.3 MB |
| [real02.glb](3d/real02.glb) | 1162.4 MB |

41 cameras; textures scaled to at most 1024 px (325 scaled) for the download.

## AI decor

110 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 24 rooms; 7 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

- r_L0_yatak_odasi_3: rules (no slot for AI decor)

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
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- drawn-piece check: 14 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 10 proposal(s) refused, reverted or not placed (listed per room)
- 1 view(s) too dark for the EV cap (lighting_dark: 0 critical, 0 major): cam_r_L0_e_yatak_odasi_3 metered +3.10 EV; the agent's set_lighting raises the room's lights

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
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.81 | D3 A1 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -1 | search 3.18 | D6 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.49 | D2 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -1 | search 2.03 | D7 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_3_final_preview.jpg) [plan](cam_r_L-1_koridor_2_3_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -2 | search 2.94 | D6 A5 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -1 | search 2.68 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -2 | search 2.62 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | -0.33 | 0 | search 2.64 | D6 A2 | 1 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | -0.67 | 0 | search 2.59 | D11 A2 | 2 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | -0.50 | 0 | search 2.59 | D9 A2 | 2 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 2.17 | D3 A1 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 1.81 | D3 A1 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.35 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.21 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 3.49 | D5 A2 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 3.44 | D5 A3 | 0 | yes | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +3.00 (cap; metered +3.10) | -3 | search 3.39 | D4 A1 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.71 | D4 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_koridor_2 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.61 | D3 | 0 | no | [preview](cam_r_L0_koridor_2_final_preview.jpg) [plan](cam_r_L0_koridor_2_plan.jpg) |
| cam_r_L0_koridor_3 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.11 | D2 A1 | 0 | no | [preview](cam_r_L0_koridor_3_final_preview.jpg) [plan](cam_r_L0_koridor_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -0.67 | 0 | search 3.45 | D4 A5 | 2 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 3.11 | D4 | 2 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | -0.67 | 0 | search 3.10 | D5 A2 | 1 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 2.55 | D4 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 2.44 | D5 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.37 | D3 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | -1.33 | - | search 1.61 | D3 A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.80 | D2 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 2.60 | D3 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_koridor_3 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.51 | D2 A1 | 0 | no | [preview](cam_r_L1_koridor_3_final_preview.jpg) [plan](cam_r_L1_koridor_3_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.17 | -1 | search 3.37 | D9 A1 | 2 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.00 | -1 | search 3.23 | D9 A1 | 2 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.17 | -1 | search 3.21 | D5 A1 | 0 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 1.50 | D2 A2 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D4 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D4 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | 0 | m5 | D4 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.67 | 0 | m5 | D4 | 0 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.33 | 0 | m5 blocked | D6 | 0 | no | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | - | m5 blocked | D2 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

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
| r_L1_koridor_2 | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | other | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 1 | 0 | 1 | cam_r_L1_teras_1 |
| r_L1_teras_2 | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_banyo_2 (twin of r_L0_e_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_4 (twin of r_L0_yatak_odasi_3), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_koridor_2 (twin of r_L1_koridor), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi), r_L1_teras_2 (twin of r_L1_teras).

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
- cam_r_L1_koridor_3: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: not_run: polish not run
- cam_r_L1_teras_1: not_run: polish not run
- ext_1: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_2: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_3: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_4: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_5: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_6: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_e_yatak_odasi_2 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | one_building.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 23 % of its pixels > 0.10 m outside the drawing, 571718 px |

## Needs review

- cam_r_L0_e_yatak_odasi_2: json cross-check misplaced: f_L0_007

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
- f_L-1_069
- f_L-1_070
- f_L-1_071
- f_L-1_072
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
- f_L-1b_042
- f_L-1b_045
- f_L-1b_046
- f_L-1b_047
- f_L-1b_049
- f_L-1b_065
- f_L-1b_066
- f_L0_013
- f_L0_014
- f_L0_027
- f_L0_028
- f_L0_029
- f_L0_030
- f_L1_003
- f_L1_004
- f_L1_008
- f_L1_012
- f_L1_013
- f_L1_014
- f_L1_023
- f_L1_024
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
- f_L0_035
- f_L0_036
- f_L0_037
- f_L0_038

Unverified pieces in view:

- cam_r_L-1_salon_1: f_L-1_070
- cam_r_L-1_salon_2: f_L-1_070, f_L-1_071
- cam_r_L-1_salon_3: f_L-1_070, f_L-1_071
- cam_r_L0_yatak_odasi_1: f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3: f_L0_038
- cam_r_L0_yatak_odasi_3_1: f_L0_029, f_L0_037
- cam_r_L0_yatak_odasi_3_2: f_L0_029, f_L0_037
- cam_r_L0_yatak_odasi_3_3: f_L0_029, f_L0_037
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_023, f_L1_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_023, f_L1_036

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L-1_021 | untyped_piece | r_L-1_salon | drawn piece 5.54 x 0.60 m in r_L-1_salon has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1_022 | untyped_piece | r_L-1_salon_2 | drawn piece 5.54 x 0.60 m in r_L-1_salon_2 has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1b_001 | untyped_piece | r_L-1b_salon_2 | drawn piece 5.14 x 2.37 m in r_L-1b_salon_2 has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1b_002 | untyped_piece | r_L-1b_salon | drawn piece 5.14 x 2.37 m in r_L-1b_salon has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |

Drawn symbols read as not furniture (never built): none.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L-1_025 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_026 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_051 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_052 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_090 | furniture | fridge | hssd_416c68a89eda39033eb729fa72f7058802555a9e | vision quality 2 (<= 2) |
| f_L-1_096 | furniture | fridge | hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 | vision quality 2 (<= 2) |
| f_L0_003 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_004 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_005 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_006 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_008 | furniture | bed_double | hssd_02e22ed56270338bef5f8436e82023c36cd29104 | the vision check sees more than one object |
| f_L0_015 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_016 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_017 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_018 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_023 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L0_024 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L1_005 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_009 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |
| f_L1_015 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_016 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_021 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_022 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_027 | furniture | wardrobe | hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e | the vision check says it is not a wardrobe (a tall_cabinet) |
| f_L1_039 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_042 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |

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
| c_043 | type_disagreement | f_L1_028 | f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes) | typed wardrobe (trust order: vector geometry and block names > AI) |
| c_044 | symbol_type_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_045 | symbol_type_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_046 | symbol_type_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_047 | symbol_type_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_048 | symbol_type_disagreement | f_L-1_087 | f_L-1_087: sym_L-1_035: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | typed ottoman by code (not table_coffee): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_049 | symbol_type_disagreement | f_L-1_088 | f_L-1_088: sym_L-1_036: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | typed ottoman by code (not table_coffee): the AI passes of its twin f_L-1_087 in the twin room r_L-1_salon named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_050 | symbol_type_disagreement | f_L-1b_042 | f_L-1b_042: sym_L-1b_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L-1b_045 | f_L-1b_045: sym_L-1b_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_046 in the twin room r_L-1b_salon named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_052 | symbol_type_disagreement | f_L-1b_046 | f_L-1b_046: sym_L-1b_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_045 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_053 | symbol_type_disagreement | f_L-1b_047 | f_L-1b_047: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_054 | symbol_type_disagreement | f_L-1b_049 | f_L-1b_049: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_055 | symbol_type_disagreement | f_L-1b_065 | f_L-1b_065: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_056 | symbol_type_disagreement | f_L-1b_066 | f_L-1b_066: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_057 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_058 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L1_023 | f_L1_023: sym_L1_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L1_024 | f_L1_024: sym_L1_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_063 | symbol_type_disagreement | f_L1_029 | f_L1_029: sym_L1_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_064 | symbol_type_disagreement | f_L1_030 | f_L1_030: sym_L1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_065 | symbol_type_disagreement | f_L1_031 | f_L1_031: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_066 | symbol_type_disagreement | f_L1_032 | f_L1_032: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_067 | symbol_type_disagreement | f_L1_037 | f_L1_037: sym_L1_x59e6f5f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sideboard, pass 2 (zai-org/GLM-4.6V-Flash) tv_unit | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L1_038 | f_L1_038: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | unresolved: the drawn footprint is kept as unknown, unverified |
| c_069 | other | r_L-1b_salon | r_L-1b_salon: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_070 | other | r_L-1b_salon_2 | r_L-1b_salon_2: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_071 | symbol_front_disagreement | f_L-1_053 | f_L-1_053: sym_L-1_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (L outline: the open inner corner is the front) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_072 | symbol_front_disagreement | f_L-1_054 | f_L-1_054: sym_L-1_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (L outline: the open inner corner is the front) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_073 | symbol_front_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_074 | symbol_front_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_075 | symbol_front_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_076 | symbol_front_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_077 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_078 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_079 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_080 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_081 | symbol_front_disagreement | f_L0_019 | f_L0_019: sym_L0_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_082 | symbol_front_disagreement | f_L0_020 | f_L0_020: sym_L0_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L0_021 | f_L0_021: sym_L0_003: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L0_022 | f_L0_022: sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L0_027 | f_L0_027: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L0_028 | f_L0_028: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L0_029 | f_L0_029: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L0_030 | f_L0_030: sym_L0_012: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L1_029 | f_L1_029: sym_L1_007: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L1_030 | f_L1_030: sym_L1_008: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | symbol_front_disagreement | f_L1_031 | f_L1_031: sym_L1_009: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_092 | symbol_front_disagreement | f_L1_032 | f_L1_032: sym_L1_010: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_093 | unit_mismatch | r1, r2, r3, r4, r5, r6 | sheets.json sc_001: one_building.dwg: $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_094 | level_mark_mismatch | r6 | sheets.json sc_002: section r6: the level mark 40.00 (MTEXT:304DD) gives -3.00 m but points at -3.15 m (the bottom of a slab) (0.15 m apart) | geometry wins: slab tops from the slab lines |

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

0 change(s) applied, 18 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 1.00 x 0.35 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_049, f_L-1_059, f_L-1_060, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_073, f_L-1_075, f_L-1_077

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_095: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L-1_089)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_022, f_L-1_023, f_L-1_038, f_L-1_039, f_L-1_040, f_L-1_041, f_L-1_042, f_L-1_043, f_L-1_044, f_L-1_045, f_L-1_046, f_L-1_047, f_L-1_048, f_L-1_057, f_L-1_058, f_L-1_065, f_L-1_066, f_L-1_069, f_L-1_072, f_L-1_074, f_L-1_076, f_L-1_078

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
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_056, f_L-1b_064, f_L-1b_068, f_L-1b_070

### Salon (r_L-1b_salon_2, living): mirrored (decisions of r_L-1b_salon (twin), not asked again)

- 3 wall cabinet run(s) over the drawn counter
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

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed

- added f_L0_041: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_042: nightstand 0.40 x 0.40 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_019, f_L0_030, f_L0_038

### E.yatak Odası (r_L0_e_yatak_odasi, bedroom): completed (nothing fits: work: no place passes the checks)

- not placed work: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_023, f_L0_031, f_L0_032

### E.yatak Odası (r_L0_e_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_e_yatak_odasi (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_008, f_L0_024, f_L0_033, f_L0_034

### Yatak Odası (r_L0_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_yatak_odasi (twin), not asked again)

- added f_L0_044: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_041)
- added f_L0_045: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_042)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_012, f_L0_020, f_L0_027, f_L0_035

### E.banyo (r_L0_e_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_013, f_L0_015

### E.banyo (r_L0_e_banyo_2, bathroom): completed (nothing missing: the drawn groups are complete; partner r_L0_e_banyo (twin) not used: the twin's drawn furniture does not map onto this room: drawn shower f_L0_013 has no counterpart here; completed itself)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_014, f_L0_016

### Yatak Odası (r_L0_yatak_odasi_3, bedroom): completed

- added f_L0_043: nightstand 0.40 x 0.40 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_009, f_L0_021, f_L0_029, f_L0_037

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): mirrored (decisions of r_L0_yatak_odasi_3 (twin), not asked again)

- added f_L0_046: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_043)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_011, f_L0_022, f_L0_028, f_L0_036

### Merdiven (r_L0_merdiven, hall): completed (no groups for this room (hall 5.7 m²: nothing))

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Merdiven (r_L0_merdiven_2, hall): mirrored (decisions of r_L0_merdiven (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_003, f_L0_018, f_L0_025

### Banyo (r_L0_banyo_2, bathroom): mirrored (decisions of r_L0_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_005, f_L0_017, f_L0_026

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi, other): completed

- added f_L1_045: bookshelf 1.00 x 0.35 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_006, f_L1_007, f_L1_013, f_L1_017, f_L1_020, f_L1_035, f_L1_036

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_047: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L1_045)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_010, f_L1_011, f_L1_014, f_L1_018, f_L1_019, f_L1_037, f_L1_038

### Koridor (r_L1_koridor, hall): completed

- added f_L1_046: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_027

### Koridor (r_L1_koridor_2, hall): mirrored (decisions of r_L1_koridor (twin), not asked again)

- added f_L1_048: shoe_cabinet 0.60 x 0.30 (confidence -, rule, mirrored from f_L1_046)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_028

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_021, f_L1_025

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_016, f_L1_022, f_L1_026

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 234 of 234 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 220 ok, 14 failed; 54 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_038 | table_dining (table_dining) | 0.08 | - | - | - |
| f_L-1_039 | chair (chair) | 0.13 | 0.00 | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L0_010 | wardrobe (wardrobe) | 0.73 | 0.00 | yes | - |
| f_L0_032 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_019 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_020 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_032 | armchair (armchair) | 0.24 | 0.00 | - | - |

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered.

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)
- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **not_validated** (exterior views stay the Cycles render): gate/gate_calibration.json missing: gate calibrate did not run or failed.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified | no |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok | no |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: ok | no |
| ext_4 | corner | left, back | - | cycles (gate_validation) | ok | back: unverified | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: unverified | no |
| ext_6 | frontal | back | - | cycles (gate_validation) | ok | back: ok | no |

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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1 | 0 / 41 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 6 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3 | 0 / 15 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| one_building.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 41, block_name 58, group_member 1, inferred 17, nightstand_symbol 4, none 24, rule 88, twin 1. Recognition questions: 92; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L-1_053 | r_L-1_salon | sofa_corner | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa_corner, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa_corner, front left 1.00 |
| f_L-1_054 | r_L-1_salon_2 | sofa_corner | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa_corner, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa_corner, front left 1.00 |
| f_L-1_055 | r_L-1_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1_056 | r_L-1_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1_057 | r_L-1_salon_2 | floor_lamp | yes | verified | no (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays, f_L-1_057 is not built (plan crop recognition/crops/sym_L-1_005_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_058 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_059 | r_L-1_salon | floor_lamp | yes | verified | no (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays, f_L-1_059 is not built (plan crop recognition/crops/sym_L-1_007_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_060 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_061 | r_L-1_salon | table_coffee | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1_062 | r_L-1_salon_2 | table_coffee | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1_063 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_064 | r_L-1_salon | floor_lamp | yes | verified | no (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_065 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_066 | r_L-1_salon_2 | floor_lamp | yes | verified | no (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_069 | r_L-1_salon_2 | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_070 | r_L-1_salon | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_071 | r_L-1_salon | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_072 | r_L-1_salon_2 | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_073 | r_L-1_salon | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.90 |
| f_L-1_074 | r_L-1_salon_2 | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.80 |
| f_L-1_075 | r_L-1_salon | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_076 | r_L-1_salon_2 | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_077 | r_L-1_salon | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_078 | r_L-1_salon_2 | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_026_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_079 | r_L-1_salon_2 | ottoman | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_080 | r_L-1_salon | ottoman | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_085 | r_L-1_mutfak | unknown | no | unverified | no (both recognition passes call it not_furniture) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_086 | r_L-1_mutfak_2 | unknown | no | unverified | no (both recognition passes call it not_furniture) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_087 | r_L-1_salon | ottoman | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1_088 | r_L-1_salon_2 | ottoman | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1b_039 | r_L-1b_salon_2 | bar_stool | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_040 | r_L-1b_salon | bar_stool | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_041 | r_L-1b_salon_2 | kitchen_island | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: kitchen_island, front bottom 0.90 |
| f_L-1b_042 | r_L-1b_salon | kitchen_island | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front top 0.90 |
| f_L-1b_043 | r_L-1b_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1b_044 | r_L-1b_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1b_045 | r_L-1b_salon_2 | sofa | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_046 | r_L-1b_salon | sofa | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_047 | r_L-1b_salon_2 | potted_plant | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_048 | r_L-1b_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1b_049 | r_L-1b_salon | potted_plant | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_050 | r_L-1b_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1b_065 | r_L-1b_salon_2 | unknown | no | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L-1b_066 | r_L-1b_salon | unknown | no | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L0_019 | r_L0_yatak_odasi | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 1.00 |
| f_L0_020 | r_L0_yatak_odasi_2 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 0.90 |
| f_L0_021 | r_L0_yatak_odasi_3 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front right 0.90 |
| f_L0_022 | r_L0_yatak_odasi_4 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 0.90 |
| f_L0_023 | r_L0_e_yatak_odasi | wardrobe | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wardrobe, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front left 0.90 |
| f_L0_024 | r_L0_e_yatak_odasi_2 | wardrobe | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wardrobe, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front right 0.90 |
| f_L0_025 | r_L0_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L0_026 | r_L0_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L0_027 | r_L0_yatak_odasi_2 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_028 | r_L0_yatak_odasi_4 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_029 | r_L0_yatak_odasi_3 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_030 | r_L0_yatak_odasi | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.85; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_031 | r_L0_e_yatak_odasi | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_032 | r_L0_e_yatak_odasi | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_033 | r_L0_e_yatak_odasi_2 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_034 | r_L0_e_yatak_odasi_2 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_023 | r_L1_oyun_aktivite_ve_dinlenme_odasi | table_coffee | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L1_024 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | table_coffee | no (typed by twin) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L1_025 | r_L1_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L1_026 | r_L1_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_031 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_032 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_033 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_034 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_035 | r_L1_oyun_aktivite_ve_dinlenme_odasi | console_table | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bench, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
| f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | console_table | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: console_table 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |
| f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | console_table | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sideboard, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: tv_unit, front left 0.90 |
| f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | console_table | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |

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
- front kept from the drawing although both AI passes answered 'none': 11 piece(s) (f_L-1_057, f_L-1_059, f_L-1_064, f_L-1_066, f_L-1_073, f_L-1_074 ...)
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
| area_light | 1 | r_L-1_salon: agent: Raise room light power x2.7 so both dark cameras (cam_1, cam_2) meter within the +3.00 EV cap.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_salon |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_merdiven_2 |
| area_light | 1 | r_L0_yatak_odasi: agent: Room too dark for camera cam_r_L0_yatak_odasi_1 (exposure +3.24 EV vs +3.00 cap); finding names factor x1.67.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; the room's light rig (2 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_4: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_4 |
| area_light | 1 | r_L0_yatak_odasi_4: room has no window; the room's light rig (2 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L0_yatak_odasi_4 |
| area_light | 1 | r_L1_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo |
| area_light | 1 | r_L1_banyo: room has no window; the room's light rig (1 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L1_banyo |
| area_light | 1 | r_L1_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo_2 |
| area_light | 1 | r_L1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor |
| area_light | 1 | r_L1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| area_light | 4 | r_L1_teras: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras, light_r_L1_teras_2, light_r_L1_teras_3 |
| area_light | 4 | r_L1_teras_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras_2.001, light_r_L1_teras_2_2, light_r_L1_teras_2_3 |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (+y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 3 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_007, dress_f_L0_021, dress_f_L0_022 |
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
| height | 6 | no height in the JSON; type height for armchair | furn_f_L-1_049, furn_f_L-1_050, furn_f_L-1_069 |
| height | 6 | no height in the JSON; type height for bathtub | furn_f_L-1_055, furn_f_L-1_056, furn_f_L0_025 |
| height | 6 | no height in the JSON; type height for bed_double | furn_f_L0_007, furn_f_L0_008, furn_f_L0_019 |
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 4 | no height in the JSON; type height for console_table | furn_f_L1_035, furn_f_L1_036, furn_f_L1_037 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L-1_058, furn_f_L-1_060, furn_f_L-1_063 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 4 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_035, furn_f_L0_036, furn_f_L0_037 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_013, furn_f_L0_014 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1_008, furn_f_L-1_017 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_061, furn_f_L-1_062, furn_f_L-1_073 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 10 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024, furn_f_L0_009 |
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
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.41 m high, its bottom would be 1.30 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.41 m high, its bottom would be 1.30 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_ceiling | 1 | no ceiling over a fixture in r_L0_merdiven: its best spot (4.74, 9.72) is 0.02 m from the room's edge or a ceiling opening (stair, slab opening to the level above), the fixture needs 0.15 m: no ceiling fixture | rig_r_L0_merdiven |
| rig_ceiling | 1 | no ceiling over a fixture in r_L0_merdiven_2: its best spot (9.00, 9.72) is 0.02 m from the room's edge or a ceiling opening (stair, slab opening to the level above), the fixture needs 0.15 m: no ceiling fixture | rig_r_L0_merdiven_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_017; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_016 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
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
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_028; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_027 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_020; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_019 (top 2.41 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_022; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_021 (top 2.18 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside light in the shade of the table lamp dec_L0_014 on f_L0_031 beside the bed f_L0_007; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the plant_small dec_L0_015); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_033 on f_L0_033 beside the bed f_L0_008; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the plant_small dec_L0_034); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the plant_small dec_L0_007); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_043 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the plant_small dec_L0_044); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside lamp on the nightstand f_L0_043; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside wall sconce on the head wall beside the bed f_L0_021 (no nightstand, no lamp); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside lamp on the nightstand f_L0_046; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside wall sconce on the head wall beside the bed f_L0_022 (no nightstand, no lamp); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_mirror | 1 | mirror light over the washbasin f_L1_016: the mirror dec_L1_010 reaches 2.00 m and the ceiling is at 1.97 m, so the bar would cross it | rig_r_L1_banyo_2 |
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
| trees | 1 | inferred trees: placed 2 of 3 (82 candidates; removed by path 10, sightline 36, window 43, front 33; most by window) | site |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| waist | 4 | the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_small_modern_1_e1ff6032 [tool_nc], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc], gen_plant_small_scandinavian_5_02284d1a [tool_nc], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_416c68a89eda39033eb729fa72f7058802555a9e [non_commercial], hssd_5dd8390c22a92ae3613788ab5ab7f71ea0d39f91 [non_commercial], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial], hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b98286cc0fed6b814d3b5cf4afc825514ed51b54 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: no (flagged assets: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L-1_koridor_2_3: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: hssd_416c68a89eda39033eb729fa72f7058802555a9e [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_2: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: yes
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_koridor_2: commercial-safe: yes
- cam_r_L0_koridor_3: commercial-safe: no (flagged assets: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: hssd_5dd8390c22a92ae3613788ab5ab7f71ea0d39f91 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: yes
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: hssd_5dd8390c22a92ae3613788ab5ab7f71ea0d39f91 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_3_2: commercial-safe: yes
- cam_r_L0_yatak_odasi_3_3: commercial-safe: yes
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e [non_commercial])
- cam_r_L1_koridor_2: commercial-safe: no (flagged assets: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e [non_commercial])
- cam_r_L1_koridor_3: commercial-safe: no (flagged assets: gen_plant_small_scandinavian_5_02284d1a [tool_nc], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: gen_plant_small_modern_1_e1ff6032 [tool_nc], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_b98286cc0fed6b814d3b5cf4afc825514ed51b54 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: gen_plant_small_modern_1_e1ff6032 [tool_nc], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_b98286cc0fed6b814d3b5cf4afc825514ed51b54 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_4: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- ext_6: commercial-safe: yes

## Built below library level (Milestone 13)

46 furniture piece(s) built from a module builder or a parametric family instead of a library model: 4 library gap(s) to close with a real model, 42 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1b_041 | kitchen_island | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_042 | kitchen_island | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L-1b_063 | sink_kitchen | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_064 | sink_kitchen | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L0_001 | stair | parametric | parametric:stair | r_L0_merdiven | hall | from_documents | no (by design) | - |
| f_L0_002 | stair | parametric | parametric:stair | r_L0_merdiven_2 | hall | from_documents | no (by design) | - |
| f_L0_013 | shower | parametric | parametric:shower | r_L0_e_banyo | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L0_014 | shower | parametric | parametric:shower | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L1_002 | stair | parametric | parametric:stair | r_L1_koridor | hall | from_documents | no (by design) | - |
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

1 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

| view | room | severity | metered EV | EV used | cap | stops over | incident p50 | set_lighting |
|---|---|---|---|---|---|---|---|---|
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | minor | +3.10 | +3.00 | +3.00 | 0.10 | 0.10495 | - |

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_1 (6.0 degrees off the sun, sky pull k 2), ext_5 (5.5 degrees off the sun, sky pull k 0).

## Replayed cameras the build changed, blocked views

| camera | change | reason |
|---|---|---|
| ext_5 | re-pitched -30.0 -> -15.7 deg | CLAUDE.md: the sky, the sun and the horizon are always in the image; the replayed aerial's horizon lay at 1.31 of the frame height (at or above its top: no sky), so it is re-pitched about its target at the same distance to the planner's aerial pitch (exterior.AERIAL_HORIZON_FRAC, lens at most exterior.AERIAL_LENS_MM); the lead's decision of 17 Oct 2026 (fix round part 2) |

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (92 of 92 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (92 of 92 answered) |

Assets: textures CC0 x 18; furniture/decor models CC-BY-4.0 x 189, CC-BY-NC-4.0 x 85, CC0 x 1, generated (TRELLIS.2-4B, MIT) x 15 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 41 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for f_L-1_051, f_L-1_052, f_L-1b_037, f_L-1b_038, f_L0_015, f_L0_016, f_L0_017, f_L0_018, f_L1_021, f_L1_022)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1b_020)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_009)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261023-084914-m13_p6-20261023T085419Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 41.0 s | - |
| pipeline | pending | 105.7 s | 70 recognition question(s) written (recognition/requests.json) |
| style | ok | 0.3 s | - |
| recognize | warning | 18.6 s | recognition glm exit 2: its unanswered pieces stay unknown, unverified; recognition qwen exit 2: its unanswered pieces stay unknown, unverified |
| pipeline_final | ok | 3.8 min | answers applied; late questions (22) answered in a second short recognition pass: pipeline_final ran again |
| fit | ok | 12.1 s | - |
| layout | ok | 34.1 s | - |
| decor_ask | ok | 94.0 s | - |
| photos | reused | 0.3 s | - |
| assets | ok | 3.9 s | - |
| decor | ok | 8.1 s | - |
| agent_apply | ok | 21.5 s | - |
| refit | ok | 43.7 s | - |
| build | ok | 25.1 min | - |
| agent_previews | ok | 5.8 min | 6 view(s) |
| agent | ok | 30.5 min | 4 round(s), 17 finding(s) removed by 18 accepted edit(s) (measured; 17 predicted by the dry re-checks), 2 new, net 15, 135 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 12.2 min | - |
| export | ok | 105.6 s | - |
| controls | ok | 2.7 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 95.1 s | - |
| check | ok | 3.4 min | - |
| combine | ok | 33.3 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 18 edit(s) accepted, 135 rejected, 340 model calls (4708883 tokens), 36.7 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 1262): earlier runs of the appended log are left out (1261 events, 440 model calls, 25 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 18 / 135 (12 % accepted) |
| rejected by reason | acceptance 37, drawn_lock 26, memory 17, max_tries 7, retype 7 |
| rooms checked by code / vision / planner | 38 / 14 / 16 |
| rooms with fixable critical or major findings visited | 16 of 16 |
| critical before -> after | 2 -> 1 |
| major before -> after | 104 -> 90 |
| agent minutes; first accepted edit after | 30.56; 46.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 17; 67; 43 (23) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 17 measured; 17 predicted |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 2 new; net 15 |
| edits removing their finding | 11 of 15 |
| plans ok / empty / refused / default | 23 / 20 / 0 / 0 |

Library gaps reported by the agent: toilet (The only real product toilet model that fits the drawn 0.5x0.68 m footprint (objaverse_3446229dce1f47528fa871cc7669136c) is already in use and renders as a featureless block; all other catalog toilet models are generated and refused while a real product fits, so no swap_model fix exists for F9.), washbasin (The only real washbasin product that fits (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551, already in use) renders as a crude low-poly block; no better audited real model exists in the library.), toilet (The only real toilet product that fits (objaverse_3446229dce1f47528fa871cc7669136c, already in use) renders as a crude boxy placeholder; no better audited real model exists in the library.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 104 | 65 | 0 | 10 | 73 | refit | 12 |
| 2 | 2 | 93 | 56 | 0 | 4 | 38 | refit | 6 |
| 3 | 1 | 94 | 55 | 0 | 4 | 24 | refit | 0 |
| 4 | 1 | 90 | 57 | 0 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D2 | 0 | 6 | 0 | 0 |
| F1 | 0 | 4 | 2 | 0 |
| F2 | 0 | 8 | 0 | 0 |
| F3 | 0 | 16 | 4 | 0 |
| F4 | 0 | 16 | 0 | 0 |
| F6 | 0 | 6 | 0 | 0 |
| F8 | 0 | 16 | 0 | 0 |
| F9 | 2 | 44 | 0 | 0 |
| G1 | 0 | 0 | 32 | 0 |
| G10 | 0 | 72 | 0 | 0 |
| G11 | 0 | 24 | 0 | 0 |
| G12 | 0 | 16 | 0 | 0 |
| G13 | 0 | 13 | 0 | 0 |
| G14 | 0 | 0 | 2 | 0 |
| G2 | 0 | 0 | 14 | 0 |
| G3 | 0 | 11 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 32 | 0 | 0 |
| G6 | 0 | 28 | 24 | 0 |
| G8 | 0 | 16 | 16 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| LG | 0 | 0 | 16 | 0 |
| NR | 0 | 16 | 0 | 0 |
| R3 | 0 | 0 | 40 | 0 |
| RC | 0 | 0 | 24 | 0 |
| S2 | 0 | 8 | 26 | 0 |
| S5 | 4 | 0 | 12 | 0 |
| X2 | 0 | 8 | 8 | 0 |
| X3 | 0 | 8 | 0 | 0 |
| lighting_dark | 0 | 3 | 3 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 1467 | 1 | set_lighting | r_L-1_salon | agent_override | - | Raise room light power x2.7 so both dark cameras (cam_1, cam_2) meter within the +3.00 EV cap. | - | - |
| 1484 | 1 | move_piece | f_L-1_038 | adjusted_by_ai | 27.0 -> 27.0 | Nudge dining table to clear the 0.039/0.038 m cuts with chairs f_L-1_039 and f_L-1_042 (S2). | ![](agent/r1_037_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_039_move_piece_after_r_L-1_salon_2.png) |
| 1509 | 1 | set_lighting | r_L0_yatak_odasi | agent_override | - | Room too dark for camera cam_r_L0_yatak_odasi_1 (exposure +3.24 EV vs +3.00 cap); finding names factor x1.67. | - | - |
| 1514 | 1 | move_piece | f_L1_020 | adjusted_by_ai | 55.0 -> 65.0 | Shift sofa f_L1_020 up 0.3 m to clear the blocked zone in front of it caused by f_L1_017 (F6). | ![](agent/r1_062_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_063_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 1518 | 1 | move_piece | f_L1_019 | adjusted_by_ai | 65.0 -> 75.0 | Move sofa f_L1_019 0.3 m away from sofa f_L1_018 to open the free zone in front of it (c:F6:f_L1_019). | ![](agent/r1_065_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_066_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 1525 | 1 | move_piece | f_L0_010 | adjusted_by_ai | 70.0 -> 80.0 | Snap wardrobe back onto its wall to restore wall contact and open the 0.80 m front clearance (G13). | ![](agent/r1_072_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r1_074_move_piece_after_r_L0_yatak_odasi.png) |
| 1535 | 1 | retype_piece | f_L1_035 | adjusted_by_ai | 65.0 -> 68.0 | Retype bench f_L1_035 to console_table which fits its 1.40 x 0.45 m footprint and the 'other' room context (F1, G14). | ![](agent/r1_079_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_080_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 1544 | 1 | retype_piece | f_L1_037 | adjusted_by_ai | 75.0 -> 78.0 | Retype bench f_L1_037 to console_table which fits its 1.40x0.45 m footprint and is valid for this room (c:F1:f_L1_037, c:G14:f_L1_037). | ![](agent/r1_086_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_087_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 1552 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. | ![](agent/r1_091_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_094_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 1553 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed edge to clear the 0.06 m² overlap and restore the required ≤0.30 m gap from the bed side. | ![](agent/r1_092_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_095_move_piece_after_r_L0_e_yatak_odasi.png) |
| 1800 | 2 | swap_model | f_L0_010 | adjusted_by_ai | 80.0 -> 80.0 | The wardrobe renders as a transparent glass box; swap to a solid 3-door wardrobe model (1.29 x 0.51 m, close to the drawn 1.45 x 0.60 m) to fix the wrong_model finding. | ![](agent/r2_058_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_062_swap_model_after_r_L0_yatak_odasi.png) |
| 1814 | 2 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.f_L1_019 | added_by_ai | 78.0 -> 81.0 | Add the missing coffee table to the seating group of sofa f_L1_019 (G2). | ![](agent/r2_084_complete_group_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_085_complete_group_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 1821 | 2 | swap_model | f_L-1_090 | added_by_ai | 71.0 -> 71.0 | Fridge renders as a thin flat panel; swap to a real boxy fridge model (0.60 x 0.64 m, modern) that fits the 0.6 x 0.65 m footprint. | ![](agent/r2_089_swap_model_before_r_L-1_mutfak.png) | ![](agent/r2_090_swap_model_after_r_L-1_mutfak.png) |
| 1834 | 2 | report_library_gap | f_L0_015 | library_gap | - | The only real product toilet model that fits the drawn 0.5x0.68 m footprint (objaverse_3446229dce1f47528fa871cc7669136c) is already in use and renders as a featureless block; all other catalog toilet models are generated and refused while a real product fits, so no swap_model fix exists for F9. | - | - |
| 2019 | 3 | move_piece | f_L-1_039 | adjusted_by_ai | 27.0 -> 27.0 | shift chair f_L-1_039 away from table_dining f_L-1_038 to clear the 0.036 m cut | ![](agent/r3_026_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_027_move_piece_after_r_L-1_salon_2.png) |
| 2062 | 3 | move_piece | f_L1_032 | adjusted_by_ai | 81.0 -> 91.0 | Shift armchair 0.24 m toward the coffee table to bring it within the 2.50 m G3 radius (rotation alone cannot close the distance). | ![](agent/r3_044_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_045_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 2083 | 3 | report_library_gap | f_L-1_026 | library_gap | - | The only real washbasin product that fits (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551, already in use) renders as a crude low-poly block; no better audited real model exists in the library. | - | - |
| 2084 | 3 | report_library_gap | f_L-1_051 | library_gap | - | The only real toilet product that fits (objaverse_3446229dce1f47528fa871cc7669136c, already in use) renders as a crude boxy placeholder; no better audited real model exists in the library. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 1468 | 1 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Put the sofa's back on the right wall (span s1) to fix F3 off-wall and position it for a TV unit opposite. |
| 1469 | 1 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.86 m) | Move floor lamp away from window win_L-1_001 to unblock the opening (G12). |
| 1470 | 1 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.42 m) | Slide the sofa 1.42 m right so its back sits on the right wall (span s1), fixing F3 off-wall and facing the room for a TV unit opposite. |
| 1471 | 1 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.50 m) | Move floor lamp 0.5 m away from window win_L-1_001 to unblock the opening (G12). |
| 1472 | 1 | move_piece | f_L-1b_046 | acceptance: finding F3:f_L-1b_046 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Slide the sofa 0.3 m right toward the right wall to reduce the off-wall gap (F3) while staying within the drawn move allowance. |
| 1474 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the ottoman f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Armchair stood behind the back of the corner sofa looking at it; turning it to face -x puts its front on the sofa's front use zone (F4). |
| 1475 | 1 | move_piece | f_L-1_063 | f_L-1_053: no_overlap, f_L-1_063: no_overlap | Move floor lamp 0.3 m (max allowance) away from window win_L-1_001 to unblock the opening (G12). |
| 1478 | 1 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 5.15 m) | Move the potted plant out of the window band (G12) and next to the sofa (within 1.5 m) to fix F8 floating. |
| 1480 | 1 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.39 m) | Move chair f_L-1b_053 away from f_L-1b_052 (fix F9 overlap) and give it ≥0.81 m clearance behind (fix G6). |
| 1481 | 1 | move_piece | f_L-1_063 | max_tries: f_L-1_063 was edited 3 times in this round | Move floor lamp 0.3 m along the window to a clear spot away from the window band (G12). |
| 1482 | 1 | move_piece | f_L-1b_053 | acceptance: finding G6:f_L-1b_053 is still there after the edit (chair f_L-1b_053 is 62° off the table f_L-1b_051 (needs ≤ 45°)) | Move chair f_L-1b_053 0.29 m away from f_L-1b_052 to fix the F9 overlap. |
| 1483 | 1 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The untyped drawn piece (5.54 x 0.60 m) is a long low cabinet along the top wall: a sideboard fits its size and the living room. |
| 1485 | 1 | move_piece | f_L-1b_056 | acceptance: finding G6:f_L-1b_055 is still there after the edit (chair f_L-1b_055: 0.09 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_056 0.29 m away from f_L-1b_055 to fix the F9 overlap. |
| 1488 | 1 | retype_piece | f_L-1_021 | retype: tv_unit is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The untyped drawn piece (5.54 x 0.60 m) is a long low cabinet along the top wall: a TV unit fits its size and the living room. |
| 1489 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_033 0.3 m away from the table to raise its pullout clearance from 0.78 m to ≥0.81 m (G6). |
| 1490 | 1 | retype_piece | f_L-1_021 | retype: kitchen_counter is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The untyped drawn piece (5.54 x 0.60 m) is a long low run along the top wall: a kitchen counter fits its size. |
| 1491 | 1 | complete_group | r_L-1b_salon_kitchen.kitchen_run | no_place: r_L-1b_salon_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Add the missing fridge to complete the kitchen run group (G9). |
| 1494 | 1 | retype_piece | f_L-1_021 | max_tries: f_L-1_021 was edited 3 times in this round | The untyped drawn piece (5.54 x 0.60 m) is a long low cabinet along the top wall: a display cabinet fits its size and the living room. |
| 1495 | 1 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | F3: sofa back 0.59 m off the wall; snap its back onto the west wall (span s4) keeping its 270° front. |
| 1496 | 1 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 6.25 m) | F8+G12: plant floats in front of the window; move it into the NW corner by the wall, clear of the window band. |
| 1497 | 1 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 5.57 m) | F8: floor lamp floats alone; move it to the NW corner beside the sofa and the plant. |
| 1498 | 1 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | F9: chair overlaps f_L-1b_058 by 0.09 m²; shift it 0.36 m away from the table edge. |
| 1499 | 1 | move_piece | f_L-1b_062 | drawn_lock: f_L-1b_062: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | F9: chair overlaps f_L-1b_061 by 0.09 m²; shift it 0.36 m away from the table edge. |
| 1500 | 1 | mark_not_furniture | f_L-1b_002 | no_crop: f_L-1b_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The 5.14 x 2.37 m untyped cluster is the bounding outline of the drawn dining group, not a single furniture piece. |
| 1501 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | G6: only 0.78 m behind chair f_L-1b_024, needs ≥0.81 m; nudge it 0.14 m away from the table. |
| 1503 | 1 | rotate_piece | f_L-1_049 | f_L-1_049: no_overlap, f_L-1_087: no_overlap | Rotate armchair to face the sofa (front 180°) to fix F4 and G3 orientation findings. |
| 1504 | 1 | move_piece | f_L-1b_058 | drawn_lock: f_L-1b_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | G6: only 0.09 m behind chair f_L-1b_058, needs ≥0.81 m; shift it 0.36 m away from the table edge. |
| 1505 | 1 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | no_place: r_L-1b_salon_2_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | G9: the kitchen run is missing its fridge; let the solver place it. |
| 1511 | 1 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.52 m) | F3: sofa back 0.59 m off the west wall; shift it 1.52 m left so its back sits on wall w_L-1b_010 (span s4), front still 270°. |
| 1512 | 1 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | F8: plant floats alone; nudge it 0.3 m up against the west wall next to the floor lamp. |
| 1517 | 1 | move_piece | f_L1_011 | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.43 m) | Move chair 0.3 m away from table f_L1_009 to resolve the 0.341 m overlap (c:S2:f_L1_009). |
| 1519 | 1 | rotate_piece | f_L1_031 | f_L1_031: clearance_ok, score: plausibility 65 -> 35 (F4 f_L1_031: armchair does not face its group (f_L1_023, f_L1_017); F6 f_L1_031: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_031: armchair f_L1_031 is 112° off the sofa f_L1_017 (needs ≤ 30°) at 2.75 m (needs ≤ 2.50 m); G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Rotate armchair f_L1_031 to face the coffee table f_L1_023 (G3). |
| 1521 | 1 | move_piece | f_L1_007 | drawn_lock: f_L1_007: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair f_L1_007 up 0.3 m to increase clearance behind it to at least 0.81 m (G6). |
| 1522 | 1 | move_piece | f_L1_011 | score: plausibility 75 -> 55 (F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_011: chair f_L1_011 is 72° off the table f_L1_009 (needs ≤ 45°)) | Move chair f_L1_011 0.3 m away from table f_L1_009 to resolve the 0.341 m overlap (c:S2:f_L1_009). |
| 1524 | 1 | move_piece | f_L1_007 | score: plausibility 65 -> 55 (F4 f_L1_007: chair does not face its group (f_L1_005); G6 f_L1_007: chair f_L1_007 is 72° off the table f_L1_005 (needs ≤ 45°)) | Move chair f_L1_007 up 0.29 m to increase clearance behind it to at least 0.81 m (G6). |
| 1526 | 1 | move_piece | f_L1_011 | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair f_L1_011 0.3 m to the right (away from table) while keeping it facing the table to resolve the 0.341 m overlap (c:S2:f_L1_009). |
| 1527 | 1 | move_piece | f_L1_007 | drawn_lock: f_L1_007: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.33 m) | Move chair f_L1_007 up-right 0.29 m to increase clearance behind it to at least 0.81 m (G6). |
| 1528 | 1 | remove_piece | f_L0_043 | score: plausibility 67 -> 64 (G4 f_L0_021: bed_double f_L0_021: no nightstand on the free right side of the head (0.52 m free)) | AI-added nightstand is not part of the architect's drawn furniture groups (F9 v:r1-v9:1); the bed's side clearance is too tight to keep it. |
| 1529 | 1 | move_piece | f_L1_007 | max_tries: f_L1_007 was edited 3 times in this round | Move chair f_L1_007 up-right 0.29 m to increase clearance behind it to at least 0.81 m (G6). |
| 1530 | 1 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Move wardrobe to the free span s0 (wall w_L0_003) so its front faces into the room with ≥0.8 m clearance (G13). |
| 1531 | 1 | move_piece | f_L1_011 | max_tries: f_L1_011 was edited 3 times in this round | Move chair f_L1_011 0.28 m to the right (away from table) while keeping it facing the table to resolve the 0.341 m overlap (c:S2:f_L1_009). |
| 1533 | 1 | retype_piece | f_L1_035 | retype: bench is no candidate for f_L1_035 (1.40 x 0.45 m at [6.10, 7.22]): the size table and the room / zone give bookshelf, console_table, desk, display_cabinet, sideboard, table_coffee, tv_unit | Confirm bench f_L1_035 type (F1, G14). |
| 1534 | 1 | move_piece | f_L0_009 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Move wardrobe to the free span s0 (wall w_L0_003) so its front faces into the room with ≥0.8 m clearance (G13). |
| 1537 | 1 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Move wardrobe to the free span s0 (wall w_L0_003) so its front faces into the room with ≥0.8 m clearance (G13). |
| 1538 | 1 | retype_piece | f_L1_037 | retype: bench is no candidate for f_L1_037 (1.40 x 0.45 m at [9.07, 7.22]): the size table and the room / zone give bookshelf, console_table, desk, display_cabinet, sideboard, table_coffee, tv_unit | Confirm bench type for f_L1_037 - it is a valid piece for a living/activity room (c:F1:f_L1_037, c:G14:f_L1_037). |
| 1539 | 1 | rotate_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 23° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Rotate armchair f_L1_032 to face the coffee table f_L1_024 (c:G3:f_L1_032). |
| 1540 | 1 | move_piece | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | Move wardrobe to the free span s0 (wall w_L0_003) so its front faces into the room with ≥0.8 m clearance (G13). |
| 1541 | 1 | move_piece | f_L0_021 | score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Shift bed 0.3 m right so the left side gains ≥0.6 m clearance (G5 left). |
| 1543 | 1 | move_piece | f_L0_021 | memory: the same edit was rejected in round 1: score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Shift bed 0.3 m right so the left side gains ≥0.6 m clearance (G5 left). |
| 1545 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Use solver candidate 1 to fix G3 (armchair f_L1_032 distance to coffee table) and other group layout issues. |
| 1546 | 1 | move_piece | f_L0_021 | memory: the same edit was rejected in round 1: score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Shift bed 0.3 m right so the left side gains ≥0.6 m clearance (G5 left). |
| 1548 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Shift the wardrobe along its wall to increase the clearance in front from 0.66 m to the required 0.80 m. |
| 1550 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Shift the wardrobe along its wall to increase the clearance in front from 0.66 m to the required 0.80 m. |
| 1554 | 1 | move_piece | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Shift the bed to center it in the available space, increasing the clearance on both the left and right sides to the required 0.60 m. |
| 1556 | 1 | move_piece | f_L0_020 | memory: the same edit was rejected in round 1: acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Shift the bed to center it in the available space, increasing the clearance on both the left and right sides to the required 0.60 m. |
| 1557 | 1 | place_group | r_L0_e_yatak_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free left side of the head. |
| 1558 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is built on the free right side of the head. |
| 1559 | 1 | move_piece | f_L0_020 | memory: the same edit was rejected in round 1: acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Shift the bed to center it in the available space, increasing the clearance on both the left and right sides to the required 0.60 m. |
| 1561 | 1 | place_group | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_007 (G4 minor, bed f_L0_007): re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free left side of the head. |
| 1562 | 1 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008: no nightstand on the free right side of the head): re-solve the drawn sleeping_double group around the bed anchor so a nightstand is built on that side. |
| 1566 | 1 | place_group | r_L0_e_yatak_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_007 (G4 minor, bed f_L0_007): re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free left side of the head. |
| 1567 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008: no nightstand on the free right side of the head): re-solve the drawn sleeping_double group around the bed anchor with the bench option so a nightstand is built on that side. |
| 1570 | 1 | swap_model | f_L-1_090 | pin_refused: f_L-1_090: gen_fridge_classic_3_25281fe9: a generated model (units guessed) while a real product of the type fits within the caps (hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023): the real model stays; swap to a real model of the type or use another tool | The fridge renders as a thin flat panel; swap to a solid boxy generated fridge model (0.69x0.74x1.46 m) that fits the 0.6 m slot. |
| 1571 | 1 | fix_fixture | f_L-1_001 | fixture_place: f_L-1_001: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_003) | Door d_L-1_003 swings into the kitchen counter f_L-1_001 on one hinge side; nudge the counter up to 0.5 m to clear the door swing. |
| 1576 | 1 | move_piece | f_L0_028 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | shift desk 0.25 m north to clear the wardrobe's front zone (G13) |
| 1577 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall) | Shower faces a wall 0.10 m in front; turning it to face 270° (into the room) resolves the orientation error and opens the front use zone. |
| 1580 | 1 | move_piece | f_L0_011 | f_L0_011: no_overlap, f_L0_028: clearance_ok, score: plausibility 67 -> 47 (F3 f_L0_011: wardrobe: its back is not on a wall (0.27 m off); F9 f_L0_028: desk f_L0_028 overlaps wardrobe f_L0_011 by 0.05 m²; G13 f_L0_011: wardrobe f_L0_011: 0.35 m free in front, needs ≥ 0.80 m) | shift wardrobe 0.3 m north to open the 0.8 m clearance in front (G13) |
| 1581 | 1 | swap_model | f_L0_015 | pin_refused: f_L0_015: gen_toilet_japandi_6_1b5173e9: a generated model (units guessed) while a real product of the type fits within the caps (objaverse_3446229dce1f47528fa871cc7669136c): the real model stays; swap to a real model of the type or use another tool | The toilet renders as a featureless white block; swap to a proper toilet model with visible bowl, seat and lid (closest real size 0.42x0.57 vs drawn 0.5x0.68). |
| 1582 | 1 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_modern_1_833baa60: a generated model (units guessed) while a real product of the type fits within the caps (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551): the real model stays; swap to a real model of the type or use another tool | Replace the crude low-poly washbasin block with a detailed modern washbasin model (D2). |
| 1583 | 1 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_1_42fdb46f: a generated model (units guessed) while a real product of the type fits within the caps (objaverse_3446229dce1f47528fa871cc7669136c): the real model stays; swap to a real model of the type or use another tool | Replace the crude boxy toilet placeholder with a realistic japandi toilet model (D2). |
| 1584 | 1 | swap_model | f_L0_015 | no_change: f_L0_015 already uses the model objaverse_3446229dce1f47528fa871cc7669136c | The toilet renders as a featureless white block; swap to the real product model that fits the drawn footprint, giving a proper bowl, seat and lid. |
| 1585 | 1 | swap_model | f_L-1_026 | no_change: f_L-1_026 already uses the model hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | Swap the crude low-poly washbasin for the real Aquazuro Avanti 90cm vanity & basin model that fits the footprint (D2). |
| 1586 | 1 | swap_model | f_L-1_051 | no_change: f_L-1_051 already uses the model objaverse_3446229dce1f47528fa871cc7669136c | Swap the crude boxy toilet placeholder for the real Toilet model that fits the footprint (D2). |
| 1769 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_053 is still there after the edit (sofa_corner f_L-1_053: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 7 more kept | Re-solve the room layout to fix the seating group's clearance (G11), orientation (G3, F4) and collision (F9) findings and add the missing TV unit (G1). |
| 1770 | 2 | relayout_room | r_L-1_salon_2 | acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 6 more kept | Candidate 1 (score 9.4) re-solves the drawn groups around their anchors, resolving the G11 walkway clearances, G12 window blockage, F4 orientation, and F9/S2 collisions. |
| 1771 | 2 | relayout_room | r_L-1_salon | candidate: candidate 2 does not exist: 1 usable candidate(s) | Try the solver's second candidate to re-solve the seating group and clear the G11/G3/F4/F6/F9 findings and add the TV unit. |
| 1772 | 2 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.76 m) | Move floor lamp away from window win_L-1_002 to clear the G12 blocked opening finding. |
| 1774 | 2 | move_piece | f_L-1_063 | f_L-1_053: no_overlap, f_L-1_063: no_overlap | Move floor lamp 0.3 m into the room, away from the window, to unblock the opening (G12). |
| 1776 | 2 | move_piece | f_L-1_063 | acceptance: finding G12:f_L-1_063 is still there after the edit (floor_lamp f_L-1_063 (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m + 0.05)) | Shift floor lamp 0.3 m along the window to clear the blocked-opening zone (G12). |
| 1777 | 2 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto the right wall (span s1) to fix the off-wall finding and face the room for a TV unit opposite. |
| 1778 | 2 | move_piece | f_L-1_065 | f_L-1_054: no_overlap, f_L-1_065: no_overlap | Move floor lamp 0.3m away from window sill to clear G12 blocked opening. |
| 1779 | 2 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m untyped drawn piece is a long low storage unit (sideboard/credenza) fitting the living room and the free wall span s0. |
| 1780 | 2 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.43 m) | Slide sofa 0.43 m right so its back sits on the right wall (span s1), fixing the off-wall finding and facing the room. |
| 1781 | 2 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Move coffee table 0.3 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap (F9). |
| 1782 | 2 | move_piece | f_L-1b_046 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_046 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Slide sofa 0.3 m right toward the right wall to reduce the off-wall gap (F3) and face the room. |
| 1783 | 2 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move floor lamp 0.3m left along the window wall to clear G12 blocked opening without overlapping the sofa. |
| 1784 | 2 | retype_piece | f_L-1_022 | retype: tall_cabinet is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m untyped drawn piece is a long storage unit; tall_cabinet fits the 0.60m depth and living room context. |
| 1785 | 2 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move coffee table 0.28 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap (F9). |
| 1786 | 2 | move_piece | f_L-1b_046 | max_tries: f_L-1b_046 was edited 3 times in this round | Slide sofa 0.3 m toward the top-right corner (right wall + top wall) to bring its back onto a wall and face the room. |
| 1788 | 2 | move_piece | f_L-1_073 | score: plausibility 7 -> -3 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.08 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table 0.27 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap (F9). |
| 1789 | 2 | place_group | r_L-1_salon_2 | no_place: seating group re-solved around the drawn sofa_corner f_L-1_054: the solver places nothing and leaves the drawn pieces as drawn (seating: no candidate position fits the room) | Re-solve the seating group around the drawn sofa anchor to fix G11 walkway clearances, F4 orientation, and F9 collision. |
| 1790 | 2 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Move coffee table 0.3m away from armchair f_L-1_069 to clear the F9 overlap. |
| 1791 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 7 -> -13 (F4 f_L-1_070: armchair faces a wall 0.11 m in front of it; F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 136° off the ottoman f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair f_L-1_070 to face away from the sofa back (front_deg 0) to fix F4. |
| 1793 | 2 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move coffee table 0.28m away from armchair f_L-1_069 to clear the F9 overlap. |
| 1794 | 2 | move_piece | f_L-1_065 | max_tries: f_L-1_065 was edited 3 times in this round | Move floor lamp 0.29m left along window wall to clear G12 blocked opening. |
| 1795 | 2 | mark_not_furniture | f_L-1_021 | no_crop: f_L-1_021 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/cam_r_L-1_salon_1_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The untyped drawn piece (5.54 x 0.60 m) is a cluster larger than 4.5 m on a side, not a single furniture item; retype attempts (sideboard, tv_unit, kitchen_counter) all failed, so it is marked as not furniture. |
| 1799 | 2 | move_piece | f_L1_009 | drawn_lock: f_L1_009: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Move dining table ~0.3 m away from chair f_L1_011 to clear the 0.341 m overlap (S2). |
| 1802 | 2 | move_piece | f_L1_009 | score: plausibility 78 -> 38 (F4 f_L1_010: chair does not face its group (f_L1_009); F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_010: chair f_L1_010 is 62° off the table f_L1_009 (needs ≤ 45°); G6 f_L1_011: chair f_L1_011 is 48° off the table f_L1_009 (needs ≤ 45°)) | Move dining table ~0.29 m away from chair f_L1_011 to clear the 0.341 m overlap (S2), within the 0.3 m allowance. |
| 1803 | 2 | move_piece | f_L0_019 | score: plausibility 80 -> 50 (F3 f_L0_019: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Move the bed 0.07 m towards the room center (increasing x) to raise the left-side clearance from 0.53 m to 0.60 m and the right-side clearance from 0.56 m to 0.63 m, satisfying the G5 check (needs ≥ 0.60 m on both sides). |
| 1804 | 2 | move_piece | f_L0_019 | f_L0_019: no_overlap, f_L0_041: no_overlap, score: plausibility 80 -> 77 (G4 f_L0_019: bed_double f_L0_019: no nightstand on the free right side of the head (0.48 m free); G4 f_L0_041: nightstand f_L0_041 of bed_double f_L0_019: -0.05 m from the bed side (needs ≤ 0.30 m); G5 f_L0_019: bed_double f_L0_019: 0.48 m free along the right side, needs ≥ 0.60 m) | Move the bed 0.07 m along its length (y-axis) to see if the G5 clearance check is measured differently; the bed stays against the wall so no F3 headboard issue. |
| 1805 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Re-layout with solver candidate 1 to place TV units opposite the sofas, add the missing coffee table and dining chairs (G1, G2, G6). |
| 1806 | 2 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: no place passes the checks (no candidate position fits the room) | Re-place the AI pieces (nightstands) to resolve the G5 clearance issue on both sides of the bed (0.53 m and 0.56 m free, needs ≥ 0.60 m). |
| 1810 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding G1:f_L1_018 is still there after the edit (sofa f_L1_018 has no TV unit opposite); 2 more kept | Re-layout with solver candidate 2 to place TV units opposite the sofas, add the missing coffee table and dining chairs (G1, G2, G6). |
| 1811 | 2 | move_piece | f_L0_019 | snap: f_L0_019: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Move the bed to the right wall (w_L0_010) to increase clearance on both sides; the bed's 1.55 m width along the wall should fit within the 4.3 m span. |
| 1812 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding G1:f_L1_018 is still there after the edit (sofa f_L1_018 has no TV unit opposite); 2 more kept | Re-layout with solver candidate 3 to place TV units opposite the sofas, add the missing coffee table and dining chairs (G1, G2, G6). |
| 1813 | 2 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining | no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | Add the 2 missing chairs to the dining group so table f_L1_009 has 4 chairs (G6). |
| 1819 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve the room to fix the wardrobe front clearance (G13), both bed side clearances (G5) and add the missing right-side nightstand (G4). |
| 1820 | 2 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating | no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating (missing tv_unit): no place passes the checks (seating: no candidate position fits the room) | Add the missing TV unit opposite sofa f_L1_018 (G1). |
| 1823 | 2 | rotate_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 2° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Rotate armchair f_L1_032 to face the coffee table f_L1_024 directly (G3). |
| 1828 | 2 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Door d_L-1_001 swings into the washbasin on one hinge side; shift it up to 0.5 m to clear the swing. |
| 1829 | 2 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.50 m (needs ≤ 2.50 m)) | Move armchair f_L1_032 0.23 m toward the coffee table f_L1_024 to bring it within 2.50 m (G3). |
| 2008 | 3 | relayout_room | r_L-1_salon_2 | memory: the same edit was rejected in round 2: acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 6 more kept | Candidate 1 (score 9.4) resolves the G11 clearance findings for the seating group and the G12 window-blocking finding for floor lamp f_L-1_065. |
| 2014 | 3 | move_piece | f_L-1b_046 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_046 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Move sofa 0.3 m right toward wall w_L-1b_010 to reduce off-wall distance and position it for a TV unit opposite. |
| 2015 | 3 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move potted plant 0.3 m away from window win_L-1b_001 to clear the blocked opening and place it near the sofa to resolve floating. |
| 2016 | 3 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto the west wall to clear the off-wall finding F3. |
| 2017 | 3 | move_piece | f_L-1b_047 | f_L-1b_047: inside_room, f_L-1b_047: inside_room (outline: potted_plant reaches 0.09 m² through the room outline, up to 0.143 m deep; 0.00 m² up to 0.000 m deep before) | Shift plant 0.3 m left off the window band to clear the blocked opening and sit it by the sofa corner. |
| 2018 | 3 | move_piece | f_L-1b_048 | acceptance: finding F8:f_L-1b_048 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Shift floor lamp 0.3 m left to sit beside the sofa, clearing the floating finding. |
| 2021 | 3 | move_piece | f_L-1b_049 | acceptance: finding F8:f_L-1b_049 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move potted plant 0.29 m away from window win_L-1b_001 to clear the blocked opening and place it near the sofa to resolve floating. |
| 2022 | 3 | move_piece | f_L-1b_050 | acceptance: finding F8:f_L-1b_050 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Move floor lamp 0.3 m closer to the sofa to resolve the floating finding. |
| 2027 | 3 | move_piece | f_L-1b_045 | acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)) | Nudge sofa 0.3 m toward the west wall to reduce the off-wall gap. |
| 2029 | 3 | move_piece | f_L-1b_049 | acceptance: finding F8:f_L-1b_049 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)); 1 more kept | Revert potted plant to its drawn position; the 0.3 m move allowance cannot reach the sofa, so the floating finding stays open. |
| 2030 | 3 | move_piece | f_L-1b_050 | acceptance: finding F8:f_L-1b_050 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Revert floor lamp to its drawn position; the 0.3 m move allowance cannot reach the sofa, so the floating finding stays open. |
| 2037 | 3 | move_piece | f_L-1b_047 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift plant 0.3 m up off the window band to clear the blocked opening. |
| 2038 | 3 | move_piece | f_L-1b_048 | acceptance: finding F8:f_L-1b_048 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Shift floor lamp 0.3 m up toward the sofa to clear the floating finding. |
| 2039 | 3 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | memory: the same edit was rejected in round 1: no_place: r_L-1b_salon_2_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Add the missing fridge to the kitchen run. |
| 2040 | 3 | move_piece | f_L-1b_053 | memory: the same edit was rejected in round 1: acceptance: finding G6:f_L-1b_053 is still there after the edit (chair f_L-1b_053 is 62° off the table f_L-1b_051 (needs ≤ 45°)) | Move chair f_L-1b_053 0.29 m to resolve overlap with f_L-1b_052 and improve clearance from the table edge. |
| 2041 | 3 | move_piece | f_L-1b_056 | memory: the same edit was rejected in round 1: acceptance: finding G6:f_L-1b_055 is still there after the edit (chair f_L-1b_055: 0.09 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_056 0.29 m to resolve overlap with f_L-1b_055 and improve clearance for the adjacent chair. |
| 2045 | 3 | move_piece | f_L-1b_059 | acceptance: swap: G6:f_L-1b_059 replaces F9:f_L-1b_059 on f_L-1b_059 (chair f_L-1b_059 is 58° off the table f_L-1b_057 (needs ≤ 45°)): the piece keeps as many critical / major findings, so nothing is removed | Nudge chair 0.26 m away from f_L-1b_058 to clear the overlap and the wall clearance. |
| 2047 | 3 | move_piece | f_L-1b_062 | acceptance: swap: F4:f_L-1b_062 replaces F9:f_L-1b_062 on f_L-1b_062 (chair does not face its group (f_L-1b_060, f_L-1b_057, f_L-1b_041)): the piece keeps as many critical / major findings, so nothing is removed | Nudge chair 0.26 m away from f_L-1b_061 to clear the overlap and the wall clearance. |
| 2048 | 3 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge chair to gain the 0.81 m clearance behind it. |
| 2051 | 3 | set_front | f_L-1b_057 | acceptance: finding G6:f_L-1b_057 is still there after the edit (dining table f_L-1b_057 has 2 of 3 chairs) | Face the table toward its chairs to clear the 2-of-3 chairs orientation finding. |
| 2058 | 3 | retype_piece | f_L0_043 | no_change: f_L0_043 is already a nightstand | Confirm the AI-added nightstand's type so it is a verified member of the sleeping_double group (F9: rendered but not in drawn groups). |
| 2059 | 3 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 13° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.52 m (needs ≤ 2.50 m)) | Shift armchair 0.22 m toward the coffee table to bring it within the 2.50 m G3 radius (rotation alone cannot close the distance). |
| 2063 | 3 | move_piece | f_L1_009 | memory: the same edit was rejected in round 2: drawn_lock: f_L1_009: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Shift the dining table 0.3 m away from chair f_L1_011 to resolve the 0.341 m overlap (S2). |
| 2066 | 3 | move_piece | f_L1_009 | memory: the same edit was rejected in round 2: score: plausibility 78 -> 38 (F4 f_L1_010: chair does not face its group (f_L1_009); F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_010: chair f_L1_010 is 62° off the table f_L1_009 (needs ≤ 45°); G6 f_L1_011: chair f_L1_011 is 48° off the table f_L1_009 (needs ≤ 45°)) | Shift the dining table 0.29 m away from chair f_L1_011 to resolve the 0.341 m overlap (S2). |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F1 | major | f_L0_030 | r_L0_yatak_odasi | review | drawn_type | 3, 4 | the piece is drawn and its type is one the room's types hold (the code's room rules, aliases included): drawn furniture is kept (CLAUDE.md), and a vision opinion on its type is no reading error, so it is reported for review, not retyped |
| F1 | major | f_L0_038 | r_L0_yatak_odasi | review | drawn_type | 3, 4 | the piece is drawn and its type is one the room's types hold (the code's room rules, aliases included): drawn furniture is kept (CLAUDE.md), and a vision opinion on its type is no reading error, so it is reported for review, not retyped |
| F9 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| F9 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| G8 | minor | f_L-1_067 | r_L-1_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_068 | r_L-1_mutfak_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_090 | r_L-1_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_096 | r_L-1_mutfak_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_007 | r_L0_e_yatak_odasi | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | critical | dec_L1_008 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_048 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| lighting_dark | minor | cam_r_L-1_salon_3 | r_L-1_salon | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | minor | cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | - | lighting_within_step | 4 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | minor | cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon | cut | 1 | 9815 | 32768 |
| 2 | r_L-1_salon | cut | 1 | 10549 | 32768 |
| 3 | r_L-1b_salon_2 | cut | 3 | 12251 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | change | by (rule) | reason |
|---|---|---|---|---|---|---|---|
| f_L-1_006 | piece | unknown | r_L-1_mutfak | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_007 | piece | unknown | r_L-1_mutfak | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_009 | piece | sink_kitchen | r_L-1_mutfak | inferred | - | - | drawn inside the sink_kitchen f_L-1_067 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_015 | piece | unknown | r_L-1_mutfak_2 | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_016 | piece | unknown | r_L-1_mutfak_2 | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_018 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1_068 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_023 | piece | wardrobe | r_L-1_salon_2 | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | code (size_snap) | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_024 | piece | wardrobe | r_L-1_salon | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | code (size_snap) | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_038 | piece | table_dining | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge dining table to clear the 0.039/0.038 m cuts with chairs f_L-1_039 and f_L-1_042 (S2). |
| f_L-1_039 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | shift chair f_L-1_039 away from table_dining f_L-1_038 to clear the 0.036 m cut |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - | - | front: the free side facing the most room is the front |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred | - | - | front: the free side facing the most room is the front |
| f_L-1_057 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays, f_L-1_057 is not built (plan crop recognition/crops/sym_L-1_005_ctx.png) |
| f_L-1_058 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_059 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays, f_L-1_059 is not built (plan crop recognition/crops/sym_L-1_007_ctx.png) |
| f_L-1_060 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_061 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type sofa -> table_coffee | code (corner_table) | table_coffee: a drawn sofa (ai_two_pass) of a coffee table's size (1.30 x 0.63 m) in the open corner of the drawn corner sofa f_L-1_053 (0% of it inside the L): the sofa's coffee table, not a seat (plan crop recognition/crops/sym_L-1_009_ctx.png) |
| f_L-1_062 | piece | table_coffee | r_L-1_salon_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type sofa -> table_coffee | code (corner_table) | table_coffee: a drawn sofa (ai_two_pass) of a coffee table's size (1.30 x 0.63 m) in the open corner of the drawn corner sofa f_L-1_054 (0% of it inside the L): the sofa's coffee table, not a seat (plan crop recognition/crops/sym_L-1_010_ctx.png) |
| f_L-1_064 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png) |
| f_L-1_066 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png) |
| f_L-1_069 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_072 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | adjusted_by_ai | size 0.56 x 0.56 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_074 | piece | table_coffee | r_L-1_salon_2 | adjusted_by_ai | size 0.56 x 0.56 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_075 | piece | ottoman | r_L-1_salon | inferred, adjusted_by_ai | - | code (reading.seat_cushion) | a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png |
| f_L-1_076 | piece | ottoman | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (reading.seat_cushion) | a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png |
| f_L-1_077 | piece | ottoman | r_L-1_salon | inferred, adjusted_by_ai | - | code (reading.seat_cushion) | a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png |
| f_L-1_078 | piece | ottoman | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (reading.seat_cushion) | a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_026_ctx.png |
| f_L-1_079 | piece | ottoman | r_L-1_salon_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1_080 | piece | ottoman | r_L-1_salon | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1_081 | piece | sink_kitchen | r_L-1_mutfak | inferred | - | - | drawn inside the sink_kitchen f_L-1_067 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_082 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1_068 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_083 | piece | sink_kitchen | r_L-1_mutfak | inferred | - | - | drawn inside the sink_kitchen f_L-1_067 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_084 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1_068 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_087 | piece | ottoman | r_L-1_salon | inferred | - | - | the two AI passes disagree (ottoman / table_coffee); both fit the drawn 0.71 x 0.41 m and the room: ottoman, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L-1_035_ctx.png |
| f_L-1_088 | piece | ottoman | r_L-1_salon_2 | inferred | - | - | the two AI passes disagree (ottoman / table_coffee); both fit the drawn 0.71 x 0.41 m and the room: ottoman, because the AI passes of its twin f_L-1_087 in the twin room r_L-1_salon named it too: the twins get one type; plan crop recognition/crops/sym_L-1_036_ctx.png |
| f_L-1b_008 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_014 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_039 | piece | bar_stool | r_L-1b_salon_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_040 | piece | bar_stool | r_L-1b_salon | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_042 | piece | kitchen_island | r_L-1b_salon | inferred | - | - | type and front of f_L-1b_041, its mirror twin in r_L-1b_salon_2 (U16) |
| f_L-1b_043 | piece | bathtub | r_L-1b_banyo_2 | inferred | - | - | front: the free side facing the most room is the front |
| f_L-1b_044 | piece | bathtub | r_L-1b_banyo | inferred | - | - | front: the free side facing the most room is the front |
| f_L-1b_045 | piece | sofa | r_L-1b_salon_2 | inferred, adjusted_by_ai | - | code (reading.long_side_front) | a sofa faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: the long side facing the most room (5.83 m free); plan crop recognition/crops/sym_L-1b_007_ctx.png |
| f_L-1b_046 | piece | sofa | r_L-1b_salon | inferred, adjusted_by_ai | - | code (reading.long_side_front) | a sofa faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: the long side facing the most room (5.83 m free); plan crop recognition/crops/sym_L-1b_008_ctx.png |
| f_L-1b_047 | piece | potted_plant | r_L-1b_salon_2 | inferred | - | - | the two AI passes disagree (floor_lamp / potted_plant); both fit the drawn 0.59 x 0.59 m and the room: potted_plant, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L-1b_009_ctx.png |
| f_L-1b_048 | piece | floor_lamp | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_049 | piece | potted_plant | r_L-1b_salon | inferred | - | - | the two AI passes disagree (floor_lamp / potted_plant); both fit the drawn 0.59 x 0.59 m and the room: potted_plant, because the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; plan crop recognition/crops/sym_L-1b_011_ctx.png |
| f_L-1b_050 | piece | floor_lamp | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_051 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_052 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_053 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_054 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_055 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_056 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_057 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_058 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_059 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_060 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_061 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_062 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_065 | piece | unknown | r_L-1b_salon_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_066 | piece | unknown | r_L-1b_salon | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_067 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_068 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_069 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_070 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | The wardrobe renders as a transparent glass box; swap to a solid 3-door wardrobe model (1.29 x 0.51 m, close to the drawn 1.45 x 0.60 m) to fix the wrong_model finding. |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_035 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_036 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_037 stands in front; plan crop recognition/crops/sym_L0_011_ctx.png |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_038 stands in front; plan crop recognition/crops/sym_L0_012_ctx.png |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: Shift the lower nightstand away from the bed edge to clear the 0.06 m² overlap and restore the required ≤0.30 m gap from the bed side. |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move sofa f_L1_019 0.3 m away from sofa f_L1_018 to open the free zone in front of it (c:F6:f_L1_019). |
| f_L1_020 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift sofa f_L1_020 up 0.3 m to clear the blocked zone in front of it caused by f_L1_017 (F6). |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift armchair 0.24 m toward the coffee table to bring it within the 2.50 m G3 radius (rotation alone cannot close the distance). (plan crop recognition/crops/sym_L1_010_ctx.png) |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Retype bench f_L1_035 to console_table which fits its 1.40 x 0.45 m footprint and the 'other' room context (F1, G14). (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_037 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Retype bench f_L1_037 to console_table which fits its 1.40x0.45 m footprint and is valid for this room (c:F1:f_L1_037, c:G14:f_L1_037). (plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png) |
| f_L1_038 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | type and front of f_L1_036, its mirror twin in r_L1_oyun_aktivite_ve_dinlenme_odasi (U16) |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred | - | - | the chair of the desk f_L0_029, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred | - | - | the chair of the desk f_L0_030, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L-1_090 | piece | fridge | r_L-1_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Fridge renders as a thin flat panel; swap to a real boxy fridge model (0.60 x 0.64 m, modern) that fits the 0.6 x 0.65 m footprint. |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_salon_1 | ![](agent/r1_cam_r_L-1_salon_1_before.jpg) | ![](agent/r1_cam_r_L-1_salon_1_after.jpg) |
| 1 | cam_r_L-1_salon_2 | ![](agent/r1_cam_r_L-1_salon_2_before.jpg) | ![](agent/r1_cam_r_L-1_salon_2_after.jpg) |
| 1 | cam_r_L-1_salon_3 | ![](agent/r1_cam_r_L-1_salon_3_before.jpg) | ![](agent/r1_cam_r_L-1_salon_3_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_1 | ![](agent/r1_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_2 | ![](agent/r1_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3 | ![](agent/r1_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 2 | cam_r_L-1_mutfak_1 | ![](agent/r2_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_1_after.jpg) |
| 2 | cam_r_L-1_mutfak_2 | ![](agent/r2_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_2_after.jpg) |
| 2 | cam_r_L-1_mutfak_3 | ![](agent/r2_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_3_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_1 | ![](agent/r2_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_2 | ![](agent/r2_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3 | ![](agent/r2_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- final/cam_r_L1_koridor_2_1_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_1_final_preview.jpg
- final/cam_r_L1_koridor_2_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_2_final_preview.jpg
- final/cam_r_L1_koridor_2_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_3_final_preview.jpg
- final/cam_r_L1_teras_2_1_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_1_final_preview.jpg
- final/cam_r_L1_teras_2_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_2_final_preview.jpg
- final/cam_r_L1_teras_2_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_3_final_preview.jpg
- final/ext_6.001_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/ext_6.001_final_preview.jpg
- final/cam_r_L1_koridor_2_1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_1_plan.jpg
- final/cam_r_L1_koridor_2_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_2_plan.jpg
- final/cam_r_L1_koridor_2_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_3_plan.jpg
- final/cam_r_L1_teras_2_1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_1_plan.jpg
- final/cam_r_L1_teras_2_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_2_plan.jpg
- final/cam_r_L1_teras_2_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_3_plan.jpg
- final/ext_6.001_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/ext_6.001_plan.jpg
