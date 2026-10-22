# Final report: real04

49 views: 0 polished, 49 Cycles (gate_validation 6, not_run 43). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 49 |
| interior / exterior views | 43 / 6 |
| variant | base |
| polished | 0 |
| Cycles | 49 (gate_validation 6, not_run 43) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 12 |
| needs_review views | 5 |
| unverified pieces in view (sum over views) | 31 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 14 |
| exposure | -7.67 .. +2.67 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| window pull | 26 view(s), -5 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 1, m5 5, search 43 |
| camera score (min / mean / max) | 0.90 / 2.60 / 3.88 |
| rooms by number of views | 1 with 0, 1 with 1, 3 with 2, 12 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 5.4 min / 8.7 min / 84.1 s |
| seconds: polish / gate / check | - / - / 17.6 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 426.0 MB |
| [real04.glb](3d/real04.glb) | 1224.0 MB |

49 cameras; textures scaled to at most 1024 px (306 scaled) for the download.

## AI decor

112 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 26 rooms; 3 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- camera cam_r_L1_banyo_1: no free camera point in the room; camera at the room's inner point; moved to the nearest point with 0.3 m of headroom under the sloped ceiling (1.55 m high there)
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 28 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 11 proposal(s) refused, reverted or not placed (listed per room)

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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 2.04 | D3 A1 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.49 | D3 A1 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | -4 | search 3.11 | D6 A2 | 1 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 2.90 | D2 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.67 | -5 | search 2.42 | D8 A2 | 0 | no | [preview](cam_r_L-1_koridor_2_3_final_preview.jpg) [plan](cam_r_L-1_koridor_2_3_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -1 | search 3.44 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.17 | -1 | search 3.28 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -1 | search 3.27 | D4 A2 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | -4 | search 2.66 | D8 A2 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 2.58 | D9 A2 | 2 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.83 | -4 | search 2.54 | D12 A2 | 3 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.05 | D4 A1 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 1.73 | D2 A1 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.04 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 0.89 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -1 | search 3.88 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.81 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.77 | D5 A3 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.09 | D4 A1 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_koridor_2 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.97 | D5 | 0 | no | [preview](cam_r_L0_koridor_2_final_preview.jpg) [plan](cam_r_L0_koridor_2_plan.jpg) |
| cam_r_L0_koridor_3 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.95 | D3 | 0 | no | [preview](cam_r_L0_koridor_3_final_preview.jpg) [plan](cam_r_L0_koridor_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -3 | search 3.41 | D4 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -3 | search 2.95 | D2 A5 | 1 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -2 | search 2.90 | D5 A2 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_4_1 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.96 | D5 A2 | 2 | no | [preview](cam_r_L0_yatak_odasi_4_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_1_plan.jpg) |
| cam_r_L0_yatak_odasi_4_2 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.62 | D5 A2 | 2 | yes | [preview](cam_r_L0_yatak_odasi_4_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_2_plan.jpg) |
| cam_r_L0_yatak_odasi_4_3 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.17 | - | search 2.40 | D5 A2 | 3 | yes | [preview](cam_r_L0_yatak_odasi_4_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | -1.17 | - | search 1.64 | D2 A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.17 | - | search 3.02 | D3 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 2.64 | D4 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_koridor_2_1 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.17 | - | search 3.00 | D4 | 0 | no | [preview](cam_r_L1_koridor_2_1_final_preview.jpg) [plan](cam_r_L1_koridor_2_1_plan.jpg) |
| cam_r_L1_koridor_2_2 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 2.77 | D5 A1 | 0 | no | [preview](cam_r_L1_koridor_2_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_2_plan.jpg) |
| cam_r_L1_koridor_2_3 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.51 | D5 | 0 | no | [preview](cam_r_L1_koridor_2_3_final_preview.jpg) [plan](cam_r_L1_koridor_2_3_plan.jpg) |
| cam_r_L1_koridor_3 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.60 | D4 | 0 | no | [preview](cam_r_L1_koridor_3_final_preview.jpg) [plan](cam_r_L1_koridor_3_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.83 | -2 | search 3.04 | D3 A5 | 0 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.67 | -1 | search 2.91 | D6 A2 | 2 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.83 | -2 | search 2.84 | D5 A5 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.50 | 0 | search 2.54 | D4 A2 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.50 | 0 | search 2.46 | D1 A2 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_2_1 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -7.50 | 0 | search 2.60 | D3 A2 | 0 | no | [preview](cam_r_L1_teras_2_1_final_preview.jpg) [plan](cam_r_L1_teras_2_1_plan.jpg) |
| cam_r_L1_teras_2_2 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -7.67 | 0 | search 2.49 | D1 A2 | 0 | no | [preview](cam_r_L1_teras_2_2_final_preview.jpg) [plan](cam_r_L1_teras_2_2_plan.jpg) |
| cam_r_L1_teras_2_3 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -7.50 | 0 | search 2.25 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_2_3_final_preview.jpg) [plan](cam_r_L1_teras_2_3_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 2.21 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.00 | 0 | m5 blocked | D6 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D5 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 blocked | D2 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.00 | 0 | m5 | D9 | 0 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 | D5 | 0 | yes | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |
| ext_front_entrance | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.33 | - | agent | D2 | 0 | no | [preview](ext_front_entrance_final_preview.jpg) [plan](ext_front_entrance_plan.jpg) |

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
| r_L0_yatak_odasi_3 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_4 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_4_1, cam_r_L0_yatak_odasi_4_2, cam_r_L0_yatak_odasi_4_3 |
| r_L1_banyo | bathroom | L1 | 1 | 0 | 1 | cam_r_L1_banyo_1 |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 3 | 0 | 3 | cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3 |
| r_L1_koridor_2 | hall | L1 | 3 | 0 | 3 | cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_2, cam_r_L1_koridor_2_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | other | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 |
| r_L1_teras_2 | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_2_1, cam_r_L1_teras_2_2, cam_r_L1_teras_2_3 |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_banyo_2 (twin of r_L0_e_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_3 (twin of r_L0_yatak_odasi_4), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi).

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
- cam_r_L0_yatak_odasi_4_1: not_run: polish not run
- cam_r_L0_yatak_odasi_4_2: not_run: polish not run
- cam_r_L0_yatak_odasi_4_3: not_run: polish not run
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
- cam_r_L1_teras_2: not_run: polish not run
- cam_r_L1_teras_2_1: not_run: polish not run
- cam_r_L1_teras_2_2: not_run: polish not run
- cam_r_L1_teras_2_3: not_run: polish not run
- cam_r_L1_teras_3: not_run: polish not run
- ext_1: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_2: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_3: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_5: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_7: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_front_entrance: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:3A2AD/10,INSERT:3A2AD/11,INSERT:3A2AD/12,INSERT:3A2AD/13,INSERT:3A2AD/14,INSERT:3A2AD/15,INSERT:3A2AD/16,INSERT:3A2AD/17,INSERT:3A2AD/18,INSERT:3A2AD/19,INSERT:3A2AD/2,INSERT:3A2AD/20,INSERT:3A2AD/21,INSERT:3A2AD/22,INSERT:3A2AD/23,INSERT:3A2AD/24,INSERT:3A2AD/25,INSERT:3A2AD/26,INSERT:3A2AD/27,INSERT:3A2AD/28,INSERT:3A2AD/29,INSERT:3A2AD/30,INSERT:3A2AD/31,INSERT:3A2AD/32,INSERT:3A2AD/33,INSERT:3A2AD/4,INSERT:3A2AD/5,INSERT:3A2AD/6,INSERT:3A2AD/7,INSERT:3A2AD/8,INSERT:3A2AD/9 YATAK vector 0.90; deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 23 % of its pixels > 0.10 m outside the drawing, 570992 px |
| cam_r_L0_yatak_odasi_4_2 | cycles | cross-check misplaced | f_L0_009 | bed_double | - | from_documents | deneme1.dwg INSERT:3A67A/10,INSERT:3A67A/11,INSERT:3A67A/12,INSERT:3A67A/13,INSERT:3A67A/14,INSERT:3A67A/15,INSERT:3A67A/16,INSERT:3A67A/17,INSERT:3A67A/18,INSERT:3A67A/19,INSERT:3A67A/2,INSERT:3A67A/20,INSERT:3A67A/21,INSERT:3A67A/22,INSERT:3A67A/23,INSERT:3A67A/24,INSERT:3A67A/25,INSERT:3A67A/26,INSERT:3A67A/27,INSERT:3A67A/28,INSERT:3A67A/29,INSERT:3A67A/30,INSERT:3A67A/31,INSERT:3A67A/32,INSERT:3A67A/33,INSERT:3A67A/4,INSERT:3A67A/5,INSERT:3A67A/6,INSERT:3A67A/7,INSERT:3A67A/8,INSERT:3A67A/9 YATAK vector 0.90 | yes | 15 % of its pixels > 0.10 m outside the drawing, 638745 px |
| cam_r_L0_yatak_odasi_4_3 | cycles | cross-check misplaced | f_L0_009 | bed_double | - | from_documents | deneme1.dwg INSERT:3A67A/10,INSERT:3A67A/11,INSERT:3A67A/12,INSERT:3A67A/13,INSERT:3A67A/14,INSERT:3A67A/15,INSERT:3A67A/16,INSERT:3A67A/17,INSERT:3A67A/18,INSERT:3A67A/19,INSERT:3A67A/2,INSERT:3A67A/20,INSERT:3A67A/21,INSERT:3A67A/22,INSERT:3A67A/23,INSERT:3A67A/24,INSERT:3A67A/25,INSERT:3A67A/26,INSERT:3A67A/27,INSERT:3A67A/28,INSERT:3A67A/29,INSERT:3A67A/30,INSERT:3A67A/31,INSERT:3A67A/32,INSERT:3A67A/33,INSERT:3A67A/4,INSERT:3A67A/5,INSERT:3A67A/6,INSERT:3A67A/7,INSERT:3A67A/8,INSERT:3A67A/9 YATAK vector 0.90 | yes | 14 % of its pixels > 0.10 m outside the drawing, 218816 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90 | yes | 30 % of its pixels > 0.10 m outside the drawing, 21072 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 27 % of its pixels > 0.10 m outside the drawing, 9903 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:3A2C9,LWPOLYLINE:3A2CA vector 0.90; deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90 | yes | 65 % of its pixels > 0.10 m outside the drawing, 6921 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:3A2C6,LWPOLYLINE:3A2C7 vector 0.90; deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90 | yes | 57 % of its pixels > 0.10 m outside the drawing, 5845 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:3AAE0,LWPOLYLINE:3AAE1 vector 0.90; deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1667 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:3AAE3,LWPOLYLINE:3AAE4 vector 0.90; deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1311 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 973 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1086 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 55 % of its pixels > 0.10 m outside the drawing, 7167 px |

## Needs review

- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: f_L0_007
- cam_r_L0_yatak_odasi_4_2: json cross-check misplaced: f_L0_009
- cam_r_L0_yatak_odasi_4_3: json cross-check misplaced: f_L0_009
- ext_5: json cross-check misplaced: win_L-1_001; json cross-check misplaced: win_L-1_003; json cross-check misplaced: win_L0_001; json cross-check misplaced: win_L0_002; json cross-check misplaced: win_L0_003; json cross-check misplaced: win_L0_004
- ext_7: json cross-check misplaced: win_L-1_001; json cross-check misplaced: win_L-1_002; json cross-check misplaced: win_L-1_004

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
- f_L-1_061
- f_L-1_062
- f_L-1_069
- f_L-1_070
- f_L-1_071
- f_L-1_072
- f_L-1_073
- f_L-1_085
- f_L-1_086
- f_L-1_087
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
- f_L-1b_049
- f_L-1b_065
- f_L-1b_066
- f_L0_011
- f_L0_012
- f_L0_017
- f_L0_018
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
- f_L0_036
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
- f_L0_039
- f_L0_040
- f_L0_041
- f_L0_042

Unverified pieces in view:

- cam_r_L-1_banyo_2: f_L-1_056
- cam_r_L-1_koridor_2_1: f_L-1_053
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_070
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_071
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061, f_L-1_070
- cam_r_L0_banyo_1: f_L0_021
- cam_r_L0_e_yatak_odasi_1: f_L0_019
- cam_r_L0_e_yatak_odasi_2: f_L0_019
- cam_r_L0_e_yatak_odasi_3: f_L0_019
- cam_r_L0_yatak_odasi_1: f_L0_017, f_L0_026, f_L0_042
- cam_r_L0_yatak_odasi_2: f_L0_017
- cam_r_L0_yatak_odasi_3: f_L0_017, f_L0_028, f_L0_042
- cam_r_L0_yatak_odasi_4_1: f_L0_030, f_L0_036
- cam_r_L0_yatak_odasi_4_2: f_L0_030, f_L0_036
- cam_r_L0_yatak_odasi_4_3: f_L0_025, f_L0_030, f_L0_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_015, f_L1_034
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_034

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L-1_021 | untyped_piece | r_L-1_salon | drawn piece 5.54 x 0.60 m in r_L-1_salon has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1_022 | untyped_piece | r_L-1_salon_2 | drawn piece 5.54 x 0.60 m in r_L-1_salon_2 has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1b_001 | untyped_piece | r_L-1b_salon_2 | drawn piece 5.14 x 2.37 m in r_L-1b_salon_2 has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |

Drawn symbols read as not furniture (never built): dimension_outline 1, other 2.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L-1_025 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_026 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_051 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_052 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_090 | furniture | fridge | hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 | vision quality 2 (<= 2) |
| f_L-1_096 | furniture | fridge | hssd_cae4c60830bba615ff533dc23ffee6e6e5c7d14e | vision quality 2 (<= 2) |
| f_L0_003 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_004 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_005 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_006 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L0_008 | furniture | bed_double | hssd_02e22ed56270338bef5f8436e82023c36cd29104 | the vision check sees more than one object |
| f_L0_009 | furniture | bed_double | hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 | the vision check sees more than one object |
| f_L0_013 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_014 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_015 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_016 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_019 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L0_020 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L1_007 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_008 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_013 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_014 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_040 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_057 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L-1_salon | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_002 | area_label_vs_computed | r_L-1_salon_2 | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_003 | area_label_vs_computed | r_L-1_mutfak | Label says 14,50 m², polygon gives 13,63 m² (6.0%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_004 | area_label_vs_computed | r_L-1_mutfak_2 | Label says 14,50 m², polygon gives 13,62 m² (6.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_005 | area_label_vs_computed | r_L-1_koridor | Label says 7,00 m², polygon gives 11,92 m² minus the stair 5,64 m² = 6,28 m² (10.2%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_006 | area_label_vs_computed | r_L-1_koridor_2 | Label says 7,00 m², polygon gives 11,93 m² minus the stair 5,64 m² = 6,29 m² (10.2%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_007 | area_label_vs_computed | r_L-1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_008 | area_label_vs_computed | r_L-1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_009 | area_label_vs_computed | r_L-1b_salon | Label says 46,00 m², polygon gives 51,83 m² (12.7%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_010 | area_label_vs_computed | r_L-1b_salon_2 | Label says 46,00 m², polygon gives 51,83 m² (12.7%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_011 | area_label_vs_computed | r_L-1b_oda | Label says 13,00 m², polygon gives 13,14 m² (1.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_012 | area_label_vs_computed | r_L-1b_oda_2 | Label says 13,00 m², polygon gives 13,15 m² (1.2%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_013 | area_label_vs_computed | r_L-1b_koridor | Label says 7,00 m², polygon gives 11,50 m² minus the stair 5,64 m² = 5,86 m² (16.3%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_014 | area_label_vs_computed | r_L-1b_koridor_2 | Label says 7,00 m², polygon gives 11,50 m² minus the stair 5,64 m² = 5,86 m² (16.3%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_015 | area_label_vs_computed | r_L-1b_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.7%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_016 | area_label_vs_computed | r_L-1b_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_017 | area_label_vs_computed | r_L0_yatak_odasi | Label says 16,00 m², polygon gives 16,06 m² (0.4%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_018 | area_label_vs_computed | r_L0_e_yatak_odasi | Label says 17,00 m², polygon gives 16,85 m² (0.9%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_019 | area_label_vs_computed | r_L0_e_yatak_odasi_2 | Label says 17,00 m², polygon gives 16,86 m² (0.8%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_020 | area_label_vs_computed | r_L0_yatak_odasi_2 | Label says 16,00 m², polygon gives 16,05 m² (0.3%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_021 | area_label_vs_computed | r_L0_koridor | Label says 7,00 m², polygon gives 7,62 m² (8.8%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_022 | area_label_vs_computed | r_L0_koridor_2 | Label says 7,00 m², polygon gives 7,62 m² (8.8%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_023 | area_label_vs_computed | r_L0_yatak_odasi_3 | Label says 17,00 m², polygon gives 16,65 m² (2.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_024 | area_label_vs_computed | r_L0_yatak_odasi_4 | Label says 17,00 m², polygon gives 16,66 m² (2.0%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_025 | area_label_vs_computed | r_L0_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_026 | area_label_vs_computed | r_L0_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.7%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_027 | area_label_vs_computed | r_L1_teras | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_028 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_029 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_030 | area_label_vs_computed | r_L1_koridor | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_031 | area_label_vs_computed | r_L1_koridor_2 | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_032 | area_label_vs_computed | r_L1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_033 | area_label_vs_computed | r_L1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_034 | area_label_vs_computed | r_L1_teras_2 | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_035 | count_mismatch | w_L0_003, w_L0_004, w_L0_006, w_L0_007, w_L0_009, w_L0_010, w_L0_012, w_L0_019, w_L0_021, r_L0_yatak_odasi_4, r_L0_yatak_odasi_3 | Zemin Kat: deneme1.dwg has 21 walls, deneme1.dwg has 17 | DWG wins over DWG, wall kept; 5 extra from DWG not added (LWPOLYLINE:2DA94 (+2): it lies on the line of w_L0_003: the same wall drawn again; LWPOLYLINE:2DE3C (+2): it lies on the line of w_L0_004: the same wall drawn again; LWPOLYLINE:2DA7F (+15): it lies on the line of w_L0_009: the same wall drawn again; LWPOLYLINE:2DA7F (+6): the 2.60 m left after the trim on the line of w_L0_012 runs through the master's room(s) r_L0_yatak_odasi_4 (2.56 m): a wall through a room the master draws open; LWPOLYLINE:2DE27 (+6): the 2.60 m left after the trim on the line of w_L0_019 runs through the master's room(s) r_L0_yatak_odasi_3 (2.56 m): a wall through a room the master draws open) |
| c_036 | count_mismatch | d_L0_005, d_L0_006 | Zemin Kat: deneme1.dwg has 12 doors, deneme1.dwg has 12 | DWG wins over DWG, door kept; 2 extra from DWG not added (INSERT:2DE25/1 (+1): 0.16 m from the master's door d_L0_005 on wall w_L0_009: that door drawn again; INSERT:2E1CD/1 (+1): 0.16 m from the master's door d_L0_006 on wall w_L0_009: that door drawn again) |
| c_037 | count_mismatch | win_L0_005, win_L0_006 | Zemin Kat: deneme1.dwg has 6 windows, deneme1.dwg has 4 | DWG wins over DWG, window kept |
| c_038 | count_mismatch | f_L0_009, f_L0_010, f_L0_024, f_L0_025, f_L0_027, f_L0_028, f_L0_029, f_L0_030, f_L0_035, f_L0_036, f_L0_037, f_L0_038 | Zemin Kat: deneme1.dwg has 38 furniture pieces, deneme1.dwg has 34 | DWG wins over DWG, furniture kept; 8 extra from DWG not added (INSERT:2DDFC/0/0 (+60): it overlaps the master's unknown f_L0_030 by 98% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2DDFD/0/0 (+59): it overlaps the master's unknown f_L0_028 by 100% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A4/0/0 (+60): it overlaps the master's unknown f_L0_029 by 98% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A5/0/0 (+58): it overlaps the master's unknown f_L0_027 by 100% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2DDF9/0 (+21): it overlaps the master's bed_double f_L0_009 by 46% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A1/0 (+21): it overlaps the master's bed_double f_L0_010 by 46% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A6/0 (+15): the same unknown footprint 1.45 x 0.91 m as the master's f_L0_024 in r_L0_yatak_odasi_3, which the secondary page does not draw at its place: that piece drawn elsewhere; INSERT:2DDFE/0 (+15): the same unknown footprint 1.45 x 0.91 m as the master's f_L0_025 in r_L0_yatak_odasi_4, which the secondary page does not draw at its place: that piece drawn elsewhere) |
| c_039 | outline_mismatch | L0, L-1 | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.500 m (areas 166.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_040 | outline_mismatch | L0, L-1b | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.500 m (areas 166.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_041 | outline_mismatch | L0, L1 | Outer wall outline of Çatı Katı differs from Zemin Kat by up to 1.500 m (areas 166.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_042 | type_disagreement | f_L-1_067 | f_L-1_067: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_043 | type_disagreement | f_L-1_068 | f_L-1_068: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_044 | type_disagreement | f_L-1b_064 | f_L-1b_064: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_045 | type_disagreement | f_L-1b_069 | f_L-1b_069: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_046 | type_disagreement | f_L-1b_070 | f_L-1b_070: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_047 | type_disagreement | f_L1_021 | f_L1_021: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes) | typed table_coffee (trust order: vector geometry and block names > AI) |
| c_048 | type_disagreement | f_L1_024 | f_L1_024: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes) | typed table_coffee (trust order: vector geometry and block names > AI) |
| c_049 | symbol_type_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_053 | symbol_type_disagreement | f_L-1_073 | f_L-1_073: sym_L-1_021: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_054 | symbol_type_disagreement | f_L-1_087 | f_L-1_087: sym_L-1_035: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_055 | symbol_type_disagreement | f_L-1b_045 | f_L-1b_045: sym_L-1b_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_046 in the twin room r_L-1b_salon named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_056 | symbol_type_disagreement | f_L-1b_046 | f_L-1b_046: sym_L-1b_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_045 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_057 | symbol_type_disagreement | f_L-1b_047 | f_L-1b_047: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_058 | symbol_type_disagreement | f_L-1b_049 | f_L-1b_049: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_059 | symbol_type_disagreement | f_L-1b_065 | f_L-1b_065: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L-1b_066 | f_L-1b_066: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L0_023 | f_L0_023: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L0_024 | f_L0_024: sym_L0_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_063 | symbol_type_disagreement | f_L0_025 | f_L0_025: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_064 | symbol_type_disagreement | f_L0_026 | f_L0_026: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_065 | symbol_type_disagreement | f_L0_036 | f_L0_036: sym_L0_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) nightstand, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_066 | symbol_type_disagreement | f_L1_017 | f_L1_017: sym_L1_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_067 | symbol_type_disagreement | f_L1_018 | f_L1_018: sym_L1_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L1_027 | f_L1_027: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_069 | symbol_type_disagreement | f_L1_028 | f_L1_028: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_027 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_070 | symbol_type_disagreement | f_L1_029 | f_L1_029: sym_L1_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_071 | symbol_type_disagreement | f_L1_030 | f_L1_030: sym_L1_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_072 | symbol_type_disagreement | f_L1_034 | f_L1_034: sym_L1_x6881d71b: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the room misses it (the living room's living_storage group has no sideboard or bookshelf); inferred, listed in the report (reading.tie_break) |
| c_073 | symbol_type_disagreement | f_L1_035 | f_L1_035: sym_L1_x59e6f5f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sideboard, pass 2 (zai-org/GLM-4.6V-Flash) bench | unresolved: the drawn footprint is kept as unknown, unverified |
| c_074 | symbol_type_disagreement | f_L1_036 | f_L1_036: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the AI passes of its twin f_L1_034 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_075 | other | r_L-1b_salon | r_L-1b_salon: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_076 | other | r_L-1b_salon_2 | r_L-1b_salon_2: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_077 | symbol_front_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_078 | symbol_front_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_079 | symbol_front_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_080 | symbol_front_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_081 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_082 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L0_023 | f_L0_023: sym_L0_007: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L0_024 | f_L0_024: sym_L0_008: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L0_025 | f_L0_025: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L0_026 | f_L0_026: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L0_036 | f_L0_036: sym_L0_020: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L1_027 | f_L1_027: sym_L1_009: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | symbol_front_disagreement | f_L1_028 | f_L1_028: sym_L1_010: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_092 | symbol_front_disagreement | f_L1_029 | f_L1_029: sym_L1_011: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_093 | symbol_front_disagreement | f_L1_030 | f_L1_030: sym_L1_012: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_094 | unit_mismatch | r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21 | sheets.json sc_001: deneme1.dwg: $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_095 | registration_residual | r11, r5 | sheets.json sc_002: deneme1.dwg r11 (L-1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_096 | registration_residual | r15, r5 | sheets.json sc_003: deneme1.dwg r15 (L-1b) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_097 | registration_residual | r16, r5 | sheets.json sc_004: deneme1.dwg r16 (L0) registered onto r5 (L0) with an RMS outline distance of 0.247 m (492 of 550 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_098 | registration_residual | r18, r5 | sheets.json sc_005: deneme1.dwg r18 (L1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_099 | section_width_mismatch | r19 | sheets.json sc_006: section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 17.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 21 regions (use: exterior 1, heights 2, ignored 13, read 5). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | deneme1.dwg | floor_plan | ai (0.95) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r2 | deneme1.dwg | floor_plan | ai (0.95) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r3 | deneme1.dwg | title_block | ai (0.99) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r4 | deneme1.dwg | other | none (0.00) | unverified | - | - | ignored (no title and no geometry rule gives a class) |
| r5 | deneme1.dwg | floor_plan | title (0.99) | verified | L0 | base | read |
| r6 | deneme1.dwg | title_block | geometry (0.90) | verified | - | - | ignored (title block) |
| r7 | deneme1.dwg | title_block | geometry (0.90) | verified | - | - | ignored (title block) |
| r8 | deneme1.dwg | title_block | geometry (0.90) | verified | - | - | ignored (title block) |
| r9 | deneme1.dwg | title_block | geometry (0.90) | verified | - | - | ignored (title block) |
| r10 | deneme1.dwg | title_block | geometry (0.90) | verified | - | - | ignored (title block) |
| r11 | deneme1.dwg | floor_plan | title (0.99) | verified | L-1 | base | read |
| r12 | deneme1.dwg | site_plan | ai (0.95) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r13 | deneme1.dwg | site_plan | ai (0.95) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r14 | deneme1.dwg | site_plan | geometry (0.70) | verified | - | - | exterior |
| r15 | deneme1.dwg | alternative_floor_plan | title (0.99) | verified | L-1b | Açık mutfak | read |
| r16 | deneme1.dwg | floor_plan | title (0.99) | verified | L0 | base | read |
| r17 | deneme1.dwg | floor_plan | ai (0.99) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r18 | deneme1.dwg | floor_plan | title (0.99) | verified | L1 | base | read |
| r19 | deneme1.dwg | section | geometry (0.85) | verified | - | - | heights |
| r20 | deneme1.dwg | section | geometry (0.85) | verified | - | - | heights |
| r21 | deneme1.dwg | other | none (0.00) | unverified | - | - | ignored (no title and no geometry rule gives a class) |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | r11 | r15 Açık mutfak -> L-1b |
| L0 | Zemin Kat | floor | r5 | - |
| L1 | Çatı Katı | attic | r18 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r11, r5, r18 |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r15, r5, r18 |

Section regions (heights): r19.

Strays (entities far from every drawing, ignored): 7.

| entity | type | layer | distance (m) | reason |
|---|---|---|---|---|
| HATCH:5303 | HATCH | _P6_BT_Yesil_T | 206.6 | far outside the frame, 1 entity (0.01 % of the document) |
| HATCH:2AC24 | HATCH | 0 | 16.0 | far outside the frame, 4 entities (0.03 % of the document) |
| HATCH:2AC25 | HATCH | 0 | 16.0 | far outside the frame, 4 entities (0.03 % of the document) |
| LWPOLYLINE:2AC26 | LWPOLYLINE | _P2_D_4_Ç | 16.0 | far outside the frame, 4 entities (0.03 % of the document) |
| HATCH:2AC27 | HATCH | 0 | 16.0 | far outside the frame, 4 entities (0.03 % of the document) |
| LWPOLYLINE:2B018 | LWPOLYLINE | _P3_S_Duvar_Ç | 6.7 | far outside the frame, 2 entities (0.02 % of the document) |
| LWPOLYLINE:2B019 | LWPOLYLINE | _P3_S_Duvar_Ç | 6.7 | far outside the frame, 2 entities (0.02 % of the document) |

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| deneme1.dwg | dwg | 0.01 | unit_check | area_labels cm 1.00 (6); level_marks None 0.04 (53); door_widths cm 0.91 (43); wall_thickness None 0.43 (2951); text_height None - (201); dimensions None - (0) | $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used |

Conflicts:

| id | kind | description | resolution |
|---|---|---|---|
| sc_001 | unit_mismatch | deneme1.dwg: $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| sc_002 | registration_residual | deneme1.dwg r11 (L-1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_003 | registration_residual | deneme1.dwg r15 (L-1b) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_004 | registration_residual | deneme1.dwg r16 (L0) registered onto r5 (L0) with an RMS outline distance of 0.247 m (492 of 550 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_005 | registration_residual | deneme1.dwg r18 (L1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_006 | section_width_mismatch | section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 17.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/deneme1_dwg_s1.jpg](debug/deneme1_dwg_s1.jpg)

Sheet warnings:

- deneme1.dwg r1: class floor_plan from the two AI passes only: unverified, not read
- deneme1.dwg r2: class floor_plan from the two AI passes only: unverified, not read
- deneme1.dwg r3: class title_block from the two AI passes only: unverified, not read
- deneme1.dwg r4: the AI passes disagree (floor_plan / site_plan): no class
- deneme1.dwg r12: class site_plan from the two AI passes only: unverified, not read
- deneme1.dwg r13: class site_plan from the two AI passes only: unverified, not read
- deneme1.dwg r17: class floor_plan from the two AI passes only: unverified, not read
- deneme1.dwg r21: the AI passes disagree (other / detail): no class
- the largest drawn polylines of the plans differ in size: r5 (L0) LWPOLYLINE:39F34 on DBM_w_sld 7.59 x 10.50 m (open, ends 5.31 m apart); r11 (L-1) LWPOLYLINE:366F8 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r15 (L-1b) LWPOLYLINE:2C4A5 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r16 (L0) LWPOLYLINE:2DA7F on DBM_w_sld 7.59 x 10.50 m (open, ends 0.40 m apart); r18 (L1) LWPOLYLINE:2F87A on _P3_S_Duvar_Ç 11.77 x 8.60 m (closed); the registered outlines (all long strokes, columns included) give residuals r11 0.2477, r15 0.2477, r16 0.2467, r18 0.2477 m; each level is kept as drawn
- 2 sections: heights from r19; r20 not read for heights
- section r19: no cut line on the plans: the section's left end is taken as the building's min side along the cut axis (flipped unknown)
- section r19: the cut direction is unknown: the ground levels keep the section's left/right
- roof: the break line on r18 (LWPOLYLINE:2F87A) is 8.60 m wide along the cut, the section's slope changes 7.80 m apart (0.80 m); both kept as drawn
- site plan r14: 36 tree symbols in a row (25.6 m): read as the hedge hedge_001 (mid, 1.2 m assumed), not as trees
- site plan r14: 31 tree symbols in a row (21.7 m): read as the hedge hedge_002 (mid, 1.2 m assumed), not as trees
- site plan r14: 7 tree symbols in a row (4.8 m): read as the hedge hedge_003 (mid, 1.2 m assumed), not as trees
- site plan r14: 7 tree symbols in a row (4.8 m): read as the hedge hedge_004 (mid, 1.2 m assumed), not as trees
- site plan r14: 2 buildings on the plot (b1: turned 0.0 deg, dz +0.00 m, b2: turned 0.0 deg, dz +3.00 m)
- no elevation drawn: facade materials and outside openings are not drawn (facade empty)

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | -3,00 m (section) | 2,85 m (section) | base | r11 |
| L-1b | Bodrum Kat | basement | -3,00 m (section) | 2,85 m (section) | Açık mutfak | r15 |
| L0 | Zemin Kat | floor | 0,00 m (section) | 3,00 m (section) | base | r5 |
| L1 | Çatı Katı | attic | 3,15 m (section) | 2,45 m (section) | base | r18 |

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
| L1 ceiling height | 2,45 m | drawn | section | - |
| L1 floor level | 3,15 m | drawn | section | - |
| sl_L-1 thickness | 0,15 m | drawn | section | - |
| sl_L0 thickness | 0,15 m | drawn | section | - |
| sl_L1 thickness | 0,15 m | drawn | section | - |
| roof eaves height | 3,75 m | drawn | vector | 0.60 m above the top floor |
| roof ridge height | 5,80 m | drawn | vector | 2.66 m above the top floor |
| roof overhang | 0,50 m | drawn | vector | left 0.50 m, right 0.50 m |
| roof thickness | 0,20 m | drawn | vector | perpendicular to the first slope |
| roof knee wall | 0,92 m | drawn | vector | the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 0.68 m above the floor |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L-1 | L-1 | -3,00 m | 0,15 m | section | 0 | all | verified |
| sl_L0 | L0 | 0,00 m | 0,15 m | section | 2 | all | verified |
| sl_L1 | L1 | 3,15 m | 0,15 m | section | 2 | all | verified |

Roof:

- type mansard (plan_roof_lines)
- over level L1
- eaves 3,75 m (drawn)
- ridge 5,80 m (drawn)
- overhang 0,50 m (drawn)
- thickness 0,20 m (drawn)
- knee wall 0,92 m (drawn)
- pitch 32.5 deg (drawn), 11.3 deg (drawn)
- 0 planes, 2 opening(s)
- covering not drawn (outside look: see Exterior views)

Facade:

No facade face or elevation drawn: the outside look is resolved from the brief, the style or the defaults (see Exterior views).

Site:

- plot drawn
- 4 paving area(s), 0 grass, 1 parking built
- 0 boundary wall(s), 26 decor item(s) built
- 9 labelled area(s), 9 recorded only (label, not built)
- ground levels: left -3,15 m (drawn), right 0,00 m (drawn)
- terrain tin, 2 light well(s)

Levels and ground (Milestone 12):

- 16 level mark(s) read (ground_finished 16); 0 mark symbol(s) taken out of the furniture
- datum ±0.00 = 43.00 m (drawn)
- ground from: marks; terrain tin
- plinth top 0,00 m (inferred)

| Door | Threshold | Ground | Rise | Solution | Main |
|---|---|---|---|---|---|
| d_L0_005 | 0,00 m | 0,00 m | 0,00 m | none |  |
| d_L0_006 | 0,00 m | 0,00 m | 0,00 m | none | yes |

Inferred (listed, CLAUDE.md evidence rules):

- site.plinth: no SB. mark: the plinth up to the ground floor
- light_well win_L-1_003: window sill -2.10 m, ground outside -1.67 m: an open concrete light well 0.8 m deep, 4.56 m wide (no light well drawn)
- front_court win_L-1_004: window sill 1.18 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn)

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 29 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 1.00 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_059, f_L-1_060, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_073, f_L-1_075, f_L-1_077

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

### Salon (r_L-1b_salon, living): completed (nothing fits: kitchen_run: no candidate position fits the room; seating: no candidate position fits the room; dining: no candidate position fits the room; dining: no candidate position fits the room)

- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_042, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_056, f_L-1b_064, f_L-1b_068, f_L-1b_070

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

- added f_L0_045: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_046: nightstand 0.40 x 0.40 (confidence -, rule)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_017, f_L0_026, f_L0_028, f_L0_042

### E.yatak Odası (r_L0_e_yatak_odasi, bedroom): completed (nothing fits: work: no place passes the checks)

- not placed work: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_019, f_L0_031, f_L0_032

### E.yatak Odası (r_L0_e_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_e_yatak_odasi (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_008, f_L0_020, f_L0_033, f_L0_034

### Yatak Odası (r_L0_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_yatak_odasi (twin), not asked again)

- added f_L0_047: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_045)
- added f_L0_048: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_046)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_018, f_L0_023, f_L0_027, f_L0_039

### E.banyo (r_L0_e_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_011, f_L0_013

### E.banyo (r_L0_e_banyo_2, bathroom): mirrored (decisions of r_L0_e_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_012, f_L0_014

### Yatak Odası (r_L0_yatak_odasi_3, bedroom): mirrored (decisions of r_L0_yatak_odasi_4 (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_024, f_L0_029, f_L0_037, f_L0_038, f_L0_040

### Merdiven (r_L0_merdiven, hall): completed (no groups for this room (hall 5.7 m²: nothing))

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Merdiven (r_L0_merdiven_2, hall): mirrored (decisions of r_L0_merdiven (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): completed (nothing to add)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_009, f_L0_025, f_L0_030, f_L0_035, f_L0_036, f_L0_041

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_003, f_L0_016, f_L0_021

### Banyo (r_L0_banyo_2, bathroom): mirrored (decisions of r_L0_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_005, f_L0_015, f_L0_022

### Teras (r_L1_teras, balcony): completed

- added f_L1_040: table_dining 0.70 x 0.70 (confidence -, rule)
- added f_L1_041: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_042: chair 0.45 x 0.45 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_022

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi, other): completed

- added f_L1_043: table_dining 1.20 x 0.80 (confidence -, rule)
- added f_L1_044: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_045: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_046: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_047: chair 0.45 x 0.45 (confidence -, rule)
- added f_L1_048: bookshelf 0.80 x 0.30 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_009, f_L1_012, f_L1_033, f_L1_034

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_051: table_dining 1.20 x 0.80 (confidence -, rule, mirrored from f_L1_043)
- added f_L1_052: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_044)
- added f_L1_053: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_045)
- added f_L1_054: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_046)
- added f_L1_055: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_047)
- added f_L1_056: bookshelf 0.80 x 0.30 (confidence -, rule, mirrored from f_L1_048)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_006, f_L1_010, f_L1_011, f_L1_035, f_L1_036

### Koridor (r_L1_koridor, hall): completed

- added f_L1_049: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_021, f_L1_023

### Koridor (r_L1_koridor_2, hall): completed

- added f_L1_050: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_024, f_L1_025, f_L1_026

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_007, f_L1_013, f_L1_019

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_008, f_L1_014, f_L1_020

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 236 of 236 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 208 ok, 28 failed; 66 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_039 | chair (chair) | 0.13 | 0.00 | - | - |
| f_L-1_042 | chair (chair) | 0.19 | 0.00 | - | - |
| f_L-1_058 | floor_lamp (floor_lamp) | 0.30 | - | - | - |
| f_L-1_059 | floor_lamp (floor_lamp) | 0.25 | 0.00 | - | - |
| f_L-1_060 | floor_lamp (floor_lamp) | 1.11 | - | - | front missing on one side |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1b_053 | chair (chair) | 0.29 | 0.00 | - | - |
| f_L-1b_056 | chair (chair) | 0.29 | 0.00 | - | - |
| f_L-1b_059 | chair (chair) | 0.26 | 0.00 | - | - |
| f_L-1b_062 | chair (chair) | 0.26 | 0.00 | - | - |
| f_L0_029 | wardrobe (wardrobe) | 0.29 | 0.00 | no | no longer against wall w_L0_004 (now centre None) |
| f_L0_030 | wardrobe (wardrobe) | 0.29 | 0.00 | no | no longer against wall w_L0_003 (now centre None) |
| f_L0_032 | nightstand (floor_lamp) | 0.11 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.15 | 0.00 | yes | - |
| f_L0_036 | nightstand (floor_lamp) | 0.22 | 0.00 | yes | - |
| f_L0_038 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_011 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_012 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_021 | table_coffee (table_coffee) | 0.09 | - | - | - |
| f_L1_022 | chair (chair) | 0.12 | 0.00 | yes | - |
| f_L1_024 | table_coffee (table_coffee) | 0.10 | - | - | - |
| f_L1_025 | chair (chair) | 0.00 | 180.00 | - | - |
| f_L1_029 | armchair (armchair) | 0.25 | 0.00 | - | - |

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered; 2 dropped (no camera place worked).

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)
- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **not_validated** (exterior views stay the Cycles render): gate/gate_calibration.json missing: gate calibrate did not run or failed.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | no |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok | no |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | - | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | yes |
| ext_7 | aerial | - | - | cycles (gate_validation) | ok | right: unverified | yes |
| ext_front_entrance | agent | back | - | cycles (gate_validation) | ok | back: ok | no |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_4 | corner | left, back | 12.5 m from the building corner, 30 degrees off the back facade: 81% of the view of the building is blocked by trees, the plot wall or another building; 14.5 m from the building corner, 30 degrees off the back facade: 68% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m from the building corner, 30 degrees off the back facade: 54% of the view of the building is blocked by trees, the plot wall or another building; 11.0 m from the building corner, 30 degrees off the back facade: 91% of the view of the building is blocked by trees, the plot wall or another building; 18.5 m from the building corner, 30 degrees off the back facade: 48% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m from the building corner, 30 degrees off the back facade: the building fills 7% of the frame (< 8%); 24.5 m from the building corner, 30 degrees off the back facade: the building fills 6% of the frame (< 8%) |
| ext_6 | frontal | back | 18.0 m in front of the back (entrance) facade: inside the copy; 20.0 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 22.0 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m in front of the back (entrance) facade: inside the copy; 24.0 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 27.0 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 30.0 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building |

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

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof mismatch.

Roof heights: built eaves 3,75 m, ridge 6,01 m; drawn eaves 3,75 m (vector), ridge 5,80 m (vector); result mismatch.

## Variants

One building per drawn alternative plan: the base and, for each alternative, the same building with that level replaced. An alternative renders only the rooms it changes, and its exterior views only when its outside differs (otherwise the base views stand for it). Each alternative has its own report in its sub-output (paths below, relative to the project output).

| variant | label | rooms changed | outside | interior views | polished / Cycles | mismatches | report |
|---|---|---|---|---|---|---|---|
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_4_1, cam_r_L0_yatak_odasi_4_2, cam_r_L0_yatak_odasi_4_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_2, cam_r_L1_koridor_2_3, cam_r_L1_koridor_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_2_1, cam_r_L1_teras_2_2, cam_r_L1_teras_2_3, cam_r_L1_teras_3 | 0 / 49 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 6 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3 | 0 / 15 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| deneme1.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 23, block_name 56, group_member 8, inferred 14, level 3, nightstand_symbol 8, none 25, rule 88, twin 11. Recognition questions: 76; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L-1_057 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_058 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_059 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_060 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_063 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_064 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_065 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_066 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_069 | r_L-1_salon_2 | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_070 | r_L-1_salon | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_071 | r_L-1_salon | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_072 | r_L-1_salon_2 | armchair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_073 | r_L-1_salon | table_coffee | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.90 |
| f_L-1_074 | r_L-1_salon_2 | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.80 |
| f_L-1_075 | r_L-1_salon | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_076 | r_L-1_salon_2 | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_077 | r_L-1_salon | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_078 | r_L-1_salon_2 | ottoman | yes | verified | no (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_026_ctx.png) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_079 | r_L-1_salon_2 | ottoman | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_080 | r_L-1_salon | ottoman | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_085 | r_L-1_mutfak | unknown | no | unverified | no (both recognition passes call it not_furniture) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_086 | r_L-1_mutfak_2 | unknown | no | unverified | no (both recognition passes call it not_furniture) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_087 | r_L-1_salon | table_coffee | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1_088 | r_L-1_salon_2 | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1b_039 | r_L-1b_salon_2 | bar_stool | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_040 | r_L-1b_salon | bar_stool | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_045 | r_L-1b_salon_2 | sofa | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_046 | r_L-1b_salon | sofa | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_047 | r_L-1b_salon_2 | potted_plant | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_048 | r_L-1b_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1b_049 | r_L-1b_salon | potted_plant | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_050 | r_L-1b_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1b_065 | r_L-1b_salon_2 | unknown | no | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L-1b_066 | r_L-1b_salon | unknown | no | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L0_023 | r_L0_yatak_odasi_2 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_024 | r_L0_yatak_odasi_3 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_025 | r_L0_yatak_odasi_4 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_026 | r_L0_yatak_odasi | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_031 | r_L0_e_yatak_odasi | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_032 | r_L0_e_yatak_odasi | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_033 | r_L0_e_yatak_odasi_2 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_034 | r_L0_e_yatak_odasi_2 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_035 | r_L0_yatak_odasi_4 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_036 | r_L0_yatak_odasi_4 | nightstand | no (typed by nightstand_symbol) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_037 | r_L0_yatak_odasi_3 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_038 | r_L0_yatak_odasi_3 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | no (untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 1: The recognition crop shows a round table with two curved chairs around it, not a single 1.63x1.52 m object; the code's own passes already ruled out not_furniture and unknown, and no type fits the room, so it stays marked for review.) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | no (untyped (CLAUDE.md: no untyped piece is built); then marked not furniture (other) by Qwen/Qwen3.8-27B-FP8, round 1: The recognition crop shows an organic blob outline with two small arc marks (a landscape/plan symbol), not a furniture footprint; the untyped 1.63 x 1.52 m drawn piece is not furniture.) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_027 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_028 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_031 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_032 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_033 | r_L1_oyun_aktivite_ve_dinlenme_odasi | bench | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bench, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
| f_L1_034 | r_L1_oyun_aktivite_ve_dinlenme_odasi | bookshelf | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |
| f_L1_035 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | bench | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sideboard, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
| f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | bookshelf | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |

## Site

The plot, paving, grass, parking and boundary walls marked built are built in the 3D scene and show in the exterior views; an area that is only a label (not built) is recorded, not built.

| id | what | detail |
|---|---|---|
| sa_L0_otopark_alani | area 'Otopark alani' (parking) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_guneslenme_alani | area 'Güneşlenme alani' (terrace) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_24m2_havuz | area '24m2 havuz' (pool) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_24m2_havuz | area '24m2 havuz' (pool) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_guneslenme_alani | area 'Güneşlenme alani' (terrace) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_guneslenme_alani | area 'Güneşlenme alani' (terrace) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_guneslenme_alani | area 'Güneşlenme alani' (terrace) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_24m2_havuz | area '24m2 havuz' (pool) | label size -, measured - (-), no closed outline, recorded only (not built) |
| sa_L0_24m2_havuz | area '24m2 havuz' (pool) | label size -, measured - (-), no closed outline, recorded only (not built) |
| - | decor | other x 6, tree x 20 |

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
- front kept from the drawing although both AI passes answered 'none': 7 piece(s) (f_L-1_057, f_L-1_059, f_L-1_064, f_L-1_066, f_L-1_074, f_L-1_079 ...)
- door height 2,10 m: 26 opening(s) (d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L-1b_001, d_L-1b_002 ...)
- opening height 2,10 m: 3 opening(s) (o_L0_001, o_L0_002, o_L1_001)
- window height 1,20 m: 14 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1b_001, win_L-1b_002 ...)
- window sill height 0,90 m: 14 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1b_001, win_L-1b_002 ...)
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
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_merdiven_2 |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; the room's light rig (2 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_4: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_4 |
| area_light | 1 | r_L0_yatak_odasi_4: room has no window; the room's light rig (2 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L0_yatak_odasi_4 |
| area_light | 1 | r_L1_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo |
| area_light | 1 | r_L1_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo_2 |
| area_light | 1 | r_L1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor |
| area_light | 1 | r_L1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| area_light | 4 | r_L1_teras: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras, light_r_L1_teras_2, light_r_L1_teras_3 |
| area_light | 4 | r_L1_teras_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras_2.001, light_r_L1_teras_2_2, light_r_L1_teras_2_3 |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (+y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 2 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_007, dress_f_L0_010 |
| cabinet_fronts | 6 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L-1_091, furn_f_L-1_092, furn_f_L-1_093 |
| climate | 1 | the drawing's language (room and site labels) (inferred; the species of trees and hedges follow it): banyo, havuz, mutfak, oda, otopark, salon, teras, yatak | site |
| direction | 4 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 22 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1_001_handle, d_L-1_002_handle, d_L-1_003_handle |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade | 1 | style profile exterior.facade (assumed) | exterior |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| handrail | 4 | design detail on every flight side not against a wall; not in the documents | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| hedge | 1 | 31 tree symbols of radius 0.36 m at a pitch of 0.72 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_002 |
| hedge | 1 | 36 tree symbols of radius 0.36 m at a pitch of 0.73 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_001 |
| hedge | 2 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_003, hedge_004 |
| hedge:hedge_001 | 1 | 36 tree symbols of radius 0.36 m at a pitch of 0.73 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_001:fit | 1 | hedge hedge_001: its 0.72 m hull kept on its planting side of sp_003, sp_003_s1e14, sp_004_s2e8 (moved up to 0.50 m, narrowed to 0.66 m; a row drawn along a terrace edge or a wall is planted beside it, inferred) | site |
| hedge:hedge_002 | 1 | 31 tree symbols of radius 0.36 m at a pitch of 0.72 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_003 | 1 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_003:fit | 1 | hedge hedge_003: its 0.72 m hull kept on its planting side of sp_001 (moved up to 0.22 m; a row drawn along a terrace edge or a wall is planted beside it, inferred) | site |
| hedge:hedge_004 | 1 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_004:fit | 1 | hedge hedge_004: its 0.72 m hull kept on its planting side of sp_004 (moved up to 0.15 m; a row drawn along a terrace edge or a wall is planted beside it, inferred) | site |
| height | 22 | door height listed as assumed in the building JSON | d_L-1_001, d_L-1_002, d_L-1_003 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.06 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) | d_L1_004, d_L1_005 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.76 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_003, d_L1_006 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.85 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_001, d_L1_002 |
| height | 6 | no height in the JSON; type height for armchair | furn_f_L-1_049, furn_f_L-1_050, furn_f_L-1_069 |
| height | 4 | no height in the JSON; type height for bed_double | furn_f_L0_007, furn_f_L0_008, furn_f_L0_009 |
| height | 2 | no height in the JSON; type height for bench | furn_f_L1_033, furn_f_L1_035 |
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_023, furn_f_L0_024, furn_f_L0_025 |
| height | 8 | no height in the JSON; type height for floor_lamp | furn_f_L-1_057, furn_f_L-1_058, furn_f_L-1_059 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 8 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_039, furn_f_L0_040, furn_f_L0_041 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_011, furn_f_L0_012 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_009, furn_f_L1_010, furn_f_L1_011 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1_008, furn_f_L-1_017 |
| height | 6 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 2 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_013 |
| height | 2 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 12 | window height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| height | 2 | window height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.76 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | win_L1_001, win_L1_002 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.06 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L0_005_inside_sill, win_L0_006_inside_sill |
| inside_sill | 8 | design detail of the documented window: an inside sill 0.1 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L-1_001_inside_sill, win_L-1_002_inside_sill, win_L-1_003_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| level | 1 | parking spk_001: one level at +0.75 m (level marks lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred) | platform_spk_001 |
| level | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 0.61 m up), 5 (1 x 0.66 m down), 6 (1 x 0.91 m down), 7 (2 x 1.16 m down), 8 (2 x 1.06 m down), 9 (2 x 1.02 m down), 10 (2 x 0.93 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps) | platform_sp_001 |
| level | 1 | terrace sp_001_s1e10: step 1 of sp_001 at -3.92 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.25..-3.94 m under it; edge: retaining (inferred) | platform_sp_001_s1e10 |
| level | 1 | terrace sp_001_s1e2: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 2.12 m over the level along its edge 2, more than the 1.2 m retaining cap); ground -2.01..-0.88 m under it; edge: retaining (inferred) | platform_sp_001_s1e2 |
| level | 1 | terrace sp_001_s1e3: step 1 of sp_001 at -2.39 m (stepped terrace: the ground lies 1.22 m over the level along its edge 3, more than the 1.2 m retaining cap); ground -2.91..-1.78 m under it; edge: retaining (inferred) | platform_sp_001_s1e3 |
| level | 1 | terrace sp_001_s1e5: step 1 of sp_001 at -3.66 m (stepped terrace: the ground lies 1.31 m under the level along its edge 5, more than the 1.2 m retaining cap); ground -4.31..-3.42 m under it; edge: retaining (inferred) | platform_sp_001_s1e5 |
| level | 1 | terrace sp_001_s1e6: step 1 of sp_001 at -3.91 m (stepped terrace: the ground lies 1.81 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -4.81..-3.92 m under it; edge: retaining (inferred) | platform_sp_001_s1e6 |
| level | 1 | terrace sp_001_s1e7: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.52..-4.42 m under it; edge: retaining (inferred) | platform_sp_001_s1e7 |
| level | 1 | terrace sp_001_s1e8: step 1 of sp_001 at -4.06 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.52..-4.54 m under it; edge: retaining (inferred) | platform_sp_001_s1e8 |
| level | 1 | terrace sp_001_s1e9: step 1 of sp_001 at -4.02 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.25..-4.54 m under it; edge: retaining (inferred) | platform_sp_001_s1e9 |
| level | 1 | terrace sp_001_s2e10: step 2 of sp_001 at -4.85 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.95..-4.14 m under it; edge: retaining (inferred) | platform_sp_001_s2e10 |
| level | 1 | terrace sp_001_s2e7: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.92..-4.81 m under it; edge: retaining (inferred) | platform_sp_001_s2e7 |
| level | 1 | terrace sp_001_s2e8: step 2 of sp_001 at -5.12 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.92..-5.14 m under it; edge: retaining (inferred) | platform_sp_001_s2e8 |
| level | 1 | terrace sp_001_s2e9: step 2 of sp_001 at -5.04 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.95..-5.14 m under it; edge: retaining (inferred) | platform_sp_001_s2e9 |
| level | 1 | terrace sp_002: one level at -1.40 m (the mean ground under it); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 15 1.31 m (next to spk_001); stepped terraces on edges 13 (1 x 0.82 m down), 14 (1 x 0.79 m down) (retaining cap 1.2 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 15 after 0) | platform_sp_002 |
| level | 1 | terrace sp_002_s1e13: step 1 of sp_002 at -2.22 m (stepped terrace: the ground lies 1.65 m under the level along its edge 13, more than the 1.2 m retaining cap); ground -3.05..-2.75 m under it; edge: retaining (inferred) | platform_sp_002_s1e13 |
| level | 1 | terrace sp_002_s1e14: step 1 of sp_002 at -2.19 m (stepped terrace: the ground lies 1.57 m under the level along its edge 14, more than the 1.2 m retaining cap); ground -2.97..-2.71 m under it; edge: retaining (inferred) | platform_sp_002_s1e14 |
| level | 1 | terrace sp_003: one level at +1.55 m (the mean ground under it); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); stepped terraces on edges 13 (1 x 0.63 m down), 14 (1 x 0.63 m down) (retaining cap 1.2 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps) | platform_sp_003 |
| level | 1 | terrace sp_003_s1e13: step 1 of sp_003 at +0.92 m (stepped terrace: the ground lies 1.25 m under the level along its edge 13, more than the 1.2 m retaining cap); ground +0.29..+0.48 m under it; edge: retaining (inferred) | platform_sp_003_s1e13 |
| level | 1 | terrace sp_003_s1e14: step 1 of sp_003 at +0.92 m (stepped terrace: the ground lies 1.26 m under the level along its edge 14, more than the 1.2 m retaining cap); ground +0.29..+0.48 m under it; edge: retaining (inferred) | platform_sp_003_s1e14 |
| level | 1 | terrace sp_004: one level at -0.20 m (the mean ground under it); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.58 m (next to spk_001); stepped terraces on edges 6 (1 x 0.76 m down), 7 (2 x 1.03 m down), 8 (2 x 0.97 m down), 9 (1 x 0.93 m down), 10 (1 x 0.83 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0) | platform_sp_004 |
| level | 1 | terrace sp_004_s1e10: step 1 of sp_004 at -1.03 m (stepped terrace: the ground lies 1.66 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -2.22..-1.16 m under it; edge: retaining (inferred) | platform_sp_004_s1e10 |
| level | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -0.96 m (stepped terrace: the ground lies 1.53 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | platform_sp_004_s1e6 |
| level | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.23 m (stepped terrace: the ground lies 2.06 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | platform_sp_004_s1e7 |
| level | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.17 m (stepped terrace: the ground lies 1.94 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.46..-1.63 m under it; edge: retaining (inferred) | platform_sp_004_s1e8 |
| level | 1 | terrace sp_004_s1e9: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.86 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -2.24..-1.63 m under it; edge: retaining (inferred) | platform_sp_004_s1e9 |
| level | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.06 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | platform_sp_004_s2e7 |
| level | 1 | terrace sp_004_s2e8: step 2 of sp_004 at -2.14 m (stepped terrace: the ground lies 1.94 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.97..-2.15 m under it; edge: retaining (inferred) | platform_sp_004_s2e8 |
| light_well:win_L-1_003 | 1 | window sill -2.10 m, ground outside -1.67 m: an open concrete light well 0.8 m deep, 4.56 m wide (no light well drawn) | site |
| light_well:win_L-1_004 | 1 | window sill 1.18 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn) | site |
| modules | 12 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| parapet | 1 | roof terrace ro_001: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn | roof |
| parapet_height:ro_002 | 1 | not drawn | roof |
| path:d_L0_005 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path:d_L0_006 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| platform:sp_001 | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 0.61 m up), 5 (1 x 0.66 m down), 6 (1 x 0.91 m down), 7 (2 x 1.16 m down), 8 (2 x 1.06 m down), 9 (2 x 1.02 m down), 10 (2 x 0.93 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps) | site |
| platform:sp_001_s1e10 | 1 | terrace sp_001_s1e10: step 1 of sp_001 at -3.92 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.25..-3.94 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e2 | 1 | terrace sp_001_s1e2: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 2.12 m over the level along its edge 2, more than the 1.2 m retaining cap); ground -2.01..-0.88 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e3 | 1 | terrace sp_001_s1e3: step 1 of sp_001 at -2.39 m (stepped terrace: the ground lies 1.22 m over the level along its edge 3, more than the 1.2 m retaining cap); ground -2.91..-1.78 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e5 | 1 | terrace sp_001_s1e5: step 1 of sp_001 at -3.66 m (stepped terrace: the ground lies 1.31 m under the level along its edge 5, more than the 1.2 m retaining cap); ground -4.31..-3.42 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e6 | 1 | terrace sp_001_s1e6: step 1 of sp_001 at -3.91 m (stepped terrace: the ground lies 1.81 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -4.81..-3.92 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e7 | 1 | terrace sp_001_s1e7: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.52..-4.42 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e8 | 1 | terrace sp_001_s1e8: step 1 of sp_001 at -4.06 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.52..-4.54 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e9 | 1 | terrace sp_001_s1e9: step 1 of sp_001 at -4.02 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.25..-4.54 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e10 | 1 | terrace sp_001_s2e10: step 2 of sp_001 at -4.85 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.95..-4.14 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e7 | 1 | terrace sp_001_s2e7: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.92..-4.81 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e8 | 1 | terrace sp_001_s2e8: step 2 of sp_001 at -5.12 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.92..-5.14 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e9 | 1 | terrace sp_001_s2e9: step 2 of sp_001 at -5.04 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.95..-5.14 m under it; edge: retaining (inferred) | site |
| platform:sp_002 | 1 | terrace sp_002: one level at -1.40 m (the mean ground under it); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 15 1.31 m (next to spk_001); stepped terraces on edges 13 (1 x 0.82 m down), 14 (1 x 0.79 m down) (retaining cap 1.2 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 15 after 0) | site |
| platform:sp_002_s1e13 | 1 | terrace sp_002_s1e13: step 1 of sp_002 at -2.22 m (stepped terrace: the ground lies 1.65 m under the level along its edge 13, more than the 1.2 m retaining cap); ground -3.05..-2.75 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s1e14 | 1 | terrace sp_002_s1e14: step 1 of sp_002 at -2.19 m (stepped terrace: the ground lies 1.57 m under the level along its edge 14, more than the 1.2 m retaining cap); ground -2.97..-2.71 m under it; edge: retaining (inferred) | site |
| platform:sp_003 | 1 | terrace sp_003: one level at +1.55 m (the mean ground under it); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); stepped terraces on edges 13 (1 x 0.63 m down), 14 (1 x 0.63 m down) (retaining cap 1.2 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps) | site |
| platform:sp_003_s1e13 | 1 | terrace sp_003_s1e13: step 1 of sp_003 at +0.92 m (stepped terrace: the ground lies 1.25 m under the level along its edge 13, more than the 1.2 m retaining cap); ground +0.29..+0.48 m under it; edge: retaining (inferred) | site |
| platform:sp_003_s1e14 | 1 | terrace sp_003_s1e14: step 1 of sp_003 at +0.92 m (stepped terrace: the ground lies 1.26 m under the level along its edge 14, more than the 1.2 m retaining cap); ground +0.29..+0.48 m under it; edge: retaining (inferred) | site |
| platform:sp_004 | 1 | terrace sp_004: one level at -0.20 m (the mean ground under it); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.58 m (next to spk_001); stepped terraces on edges 6 (1 x 0.76 m down), 7 (2 x 1.03 m down), 8 (2 x 0.97 m down), 9 (1 x 0.93 m down), 10 (1 x 0.83 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0) | site |
| platform:sp_004_s1e10 | 1 | terrace sp_004_s1e10: step 1 of sp_004 at -1.03 m (stepped terrace: the ground lies 1.66 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -2.22..-1.16 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e6 | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -0.96 m (stepped terrace: the ground lies 1.53 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e7 | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.23 m (stepped terrace: the ground lies 2.06 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e8 | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.17 m (stepped terrace: the ground lies 1.94 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.46..-1.63 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e9 | 1 | terrace sp_004_s1e9: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.86 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -2.24..-1.63 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s2e7 | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.06 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s2e8 | 1 | terrace sp_004_s2e8: step 2 of sp_004 at -2.14 m (stepped terrace: the ground lies 1.94 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.97..-2.15 m under it; edge: retaining (inferred) | site |
| platform:spk_001 | 1 | parking spk_001: one level at +0.75 m (level marks lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred) | site |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: concrete_exposed (style family modern; not drawn) | facade |
| pool:pool_001:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_002:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_003:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_004:depth | 1 | no pool section drawn: the depth is assumed | site |
| rig_ceiling | 1 | ceiling fixture at (10.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_ceiling | 1 | ceiling fixture at (7.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | no ceiling over a fixture in r_L0_merdiven: its best spot (5.74, 9.71) is 0.02 m from the room's edge or a ceiling opening (stair, slab opening to the level above), the fixture needs 0.15 m: no ceiling fixture | rig_r_L0_merdiven |
| rig_ceiling | 1 | no ceiling over a fixture in r_L0_merdiven_2: its best spot (10.00, 9.71) is 0.02 m from the room's edge or a ceiling opening (stair, slab opening to the level above), the fixture needs 0.15 m: no ceiling fixture | rig_r_L0_merdiven_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_010; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_012; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_011 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
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
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_030; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_032; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_031 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_021; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_020 (top 2.41 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_034; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_033 (top 2.18 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside light in the shade of the table lamp dec_L0_015 on f_L0_031 beside the bed f_L0_007; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_016); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_039 on f_L0_033 beside the bed f_L0_008; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_040); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_045 beside the bed f_L0_017; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_017 (the top of the nightstand f_L0_046 is taken by the plant_small dec_L0_007); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_049 on f_L0_047 beside the bed f_L0_018; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_018 (the top of the nightstand f_L0_048 is taken by the plant_small dec_L0_050); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside lamp on the nightstand f_L0_038; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_057 on f_L0_037 beside the bed f_L0_010; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside lamp on the nightstand f_L0_036; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_025 on f_L0_035 beside the bed f_L0_009; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_mirror | 1 | mirror light over the washbasin f_L1_007: the mirror dec_L1_008 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo |
| rig_mirror | 1 | mirror light over the washbasin f_L1_008: the mirror dec_L1_009 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo_2 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 12 drawn risers | furn_f_L-1_019, furn_f_L-1_020 |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.150 m / 11 drawn risers | furn_f_L0_001 |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.150 m / 12 drawn risers | furn_f_L0_002 |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 2 | outside sill 2.2285 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill, win_L0_003_sill |
| sill | 2 | outside sill 2.7431 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill, win_L0_004_sill |
| sill | 2 | outside sill 4.2173 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_003_sill, win_L-1_004_sill |
| sill | 2 | outside sill 7.2461 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_001_sill, win_L-1_002_sill |
| sill_height | 12 | window sill_height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 20 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1_salon, skirting_r_L-1_salon_2, skirting_r_L-1_mutfak |
| slab_band | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067 (docs/milestone11.md §1.3 M2; not drawn) | splashback_r_L-1_mutfak |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_010, f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068 (docs/milestone11.md §1.3 M2; not drawn) | splashback_r_L-1_mutfak_2 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_002 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_002 (100% of the smaller footprint; slab opening sv_L1_002); read as its upper end, not built as a second flight | f_L1_001 |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| tree | 20 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| waist | 4 | the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_scandinavian_5_c7cc94ed [tool_nc], gen_plant_small_japandi_1_32d3b9fb [tool_nc], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc], hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 [non_commercial], hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_9b178a92887b9a23e8bb5d6dbbb158794b57c39b [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: yes
- cam_r_L-1_koridor_2_3: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_2: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_yatak_odasi_1: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_koridor_1: commercial-safe: no (flagged assets: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L0_koridor_2: commercial-safe: yes
- cam_r_L0_koridor_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L0_yatak_odasi_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_4_1: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L0_yatak_odasi_4_2: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L0_yatak_odasi_4_3: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_5_c7cc94ed [tool_nc], hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: yes
- cam_r_L1_koridor_2: commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial])
- cam_r_L1_koridor_2_1: commercial-safe: yes
- cam_r_L1_koridor_2_2: commercial-safe: no (flagged assets: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L1_koridor_2_3: commercial-safe: yes
- cam_r_L1_koridor_3: commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial])
- cam_r_L1_teras_2_1: commercial-safe: no (flagged assets: hssd_9b178a92887b9a23e8bb5d6dbbb158794b57c39b [non_commercial])
- cam_r_L1_teras_2_2: commercial-safe: no (flagged assets: hssd_9b178a92887b9a23e8bb5d6dbbb158794b57c39b [non_commercial])
- cam_r_L1_teras_2_3: commercial-safe: no (flagged assets: hssd_9b178a92887b9a23e8bb5d6dbbb158794b57c39b [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial])
- ext_7: commercial-safe: no (flagged assets: hssd_9b178a92887b9a23e8bb5d6dbbb158794b57c39b [non_commercial])
- ext_front_entrance: commercial-safe: yes

## Built below library level (Milestone 13)

46 furniture piece(s) built from a module builder or a parametric family instead of a library model: 6 library gap(s) to close with a real model, 40 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1b_063 | sink_kitchen | module | kitchen_run | r_L-1b_salon_2 | living | from_documents | no (by design) | - |
| f_L-1b_064 | sink_kitchen | module | kitchen_run | r_L-1b_salon | living | from_documents | no (by design) | - |
| f_L0_001 | stair | parametric | parametric:stair | r_L0_merdiven | hall | from_documents | no (by design) | - |
| f_L0_002 | stair | parametric | parametric:stair | r_L0_merdiven_2 | hall | from_documents | no (by design) | - |
| f_L0_011 | shower | parametric | parametric:shower | r_L0_e_banyo | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L0_012 | shower | parametric | parametric:shower | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L1_002 | stair | parametric | parametric:stair | r_L1_koridor | hall | from_documents | no (by design) | - |
| f_L1_023 | chair | parametric | parametric:chair | r_L1_koridor | hall | from_documents | yes | parametric family (built below the library level) |
| f_L1_025 | chair | parametric | parametric:chair | r_L1_koridor_2 | hall | from_documents | yes | parametric family (built below the library level) |
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

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 3), cam_r_L1_teras_3 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.7 degrees off the sun, sky pull k 3), ext_5 (5.4 degrees off the sun, sky pull k 6).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (76 of 76 answered); sheets/requests.json (8 of 8 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (76 of 76 answered); sheets/requests.json (8 of 8 answered) |

Assets: textures CC0 x 18; furniture/decor models CC-BY-4.0 x 174, CC-BY-NC-4.0 x 97, CC0 x 2, generated (TRELLIS.2-4B, MIT) x 18 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 49 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for f_L-1_051, f_L-1_052, f_L-1b_037, f_L-1b_038, f_L0_013, f_L0_014, f_L0_015, f_L0_016, f_L1_013, f_L1_014)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1b_020)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_002)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261022-135644-m13_p6-20261022T140316Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 66.8 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 2.4 min | 76 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| style | ok | 0.7 s | - |
| recognize | ok | 14.3 s | - |
| pipeline_final | ok | 3.3 min | answers applied |
| fit | ok | 10.9 s | - |
| layout | ok | 39.6 s | - |
| decor_ask | ok | 94.7 s | - |
| photos | reused | 0.6 s | - |
| assets | ok | 6.8 s | - |
| decor | ok | 13.1 s | - |
| agent_apply | ok | 37.0 s | - |
| refit | ok | 94.3 s | - |
| build | ok | 25.3 min | - |
| agent_previews | ok | 7.7 min | 7 view(s) |
| agent | ok | 36.7 min | 3 round(s), 34 finding(s) removed by 34 accepted edit(s) (measured; 35 predicted by the dry re-checks), 2 new, net 32, 150 rejected; stop: max rounds reached |
| render | ok | 12.3 min | - |
| export | ok | 2.2 min | - |
| controls | ok | 3.8 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 2.9 min | - |
| check | ok | 4.2 min | - |
| combine | ok | 90.0 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 34 edit(s) accepted, 150 rejected, 411 model calls (5683943 tokens), 45.0 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 5703): earlier runs of the appended log are left out (5702 events, 1849 model calls, 249 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 34 / 150 (18 % accepted) |
| rejected by reason | drawn_lock 36, acceptance 28, memory 20, score 13, snap 12 |
| rooms checked by code / vision / planner | 38 / 16 / 19 |
| rooms with fixable critical or major findings visited | 19 of 19 |
| critical before -> after | 4 -> 2 |
| major before -> after | 121 -> 87 |
| agent minutes; first accepted edit after | 36.77; 85.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 20; 69; 43 (31) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 40 measured; 42 predicted |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 6 new; net 34 |
| edits removing their finding | 30 of 33 |
| plans ok / empty / refused / default | 31 / 9 / 3 / 0 |

Library gaps reported by the agent: chair (No chair model within 10% non-uniform scale and 0.85..1.2 mean scale (closest abo_B0857JM2NC at 18.7% non-uniform); relaxed caps also yield no candidate, so the parametric build stands.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 4 | 121 | 79 | 1 | 19 | 65 | layout | 28 |
| 2 | 3 | 95 | 72 | 2 | 8 | 40 | refit | 14 |
| 3 | 2 | 89 | 72 | 2 | 7 | 45 | refit | 7 |
| 4 | 2 | 87 | 72 | 2 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D2 | 0 | 3 | 0 | 0 |
| F1 | 0 | 5 | 16 | 0 |
| F2 | 0 | 8 | 0 | 0 |
| F3 | 0 | 26 | 8 | 0 |
| F4 | 0 | 13 | 0 | 0 |
| F6 | 0 | 2 | 0 | 0 |
| F8 | 0 | 16 | 0 | 0 |
| F9 | 0 | 46 | 0 | 1 |
| G1 | 0 | 0 | 40 | 0 |
| G10 | 0 | 72 | 0 | 0 |
| G11 | 0 | 24 | 0 | 0 |
| G12 | 0 | 37 | 0 | 0 |
| G13 | 0 | 8 | 0 | 0 |
| G14 | 0 | 0 | 16 | 0 |
| G2 | 0 | 0 | 24 | 0 |
| G3 | 0 | 6 | 0 | 0 |
| G4 | 0 | 4 | 4 | 0 |
| G5 | 0 | 16 | 0 | 0 |
| G6 | 0 | 27 | 16 | 0 |
| G8 | 0 | 16 | 16 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 24 | 0 |
| NR | 0 | 15 | 0 | 0 |
| R3 | 0 | 0 | 40 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S2 | 0 | 10 | 43 | 0 |
| S5 | 0 | 0 | 8 | 0 |
| X2 | 11 | 15 | 8 | 2 |
| X3 | 0 | 8 | 0 | 4 |
| X6 | 0 | 3 | 1 | 0 |
| lighting_dark | 0 | 0 | 3 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 5968 | 1 | mark_not_furniture | f_L-1b_002 | adjusted_by_ai | 0.0 -> 0.0 | NR: the 5.14 x 2.37 m untyped cluster is a group of drawn pieces / zone outline, not a single piece of furniture. | ![](agent/r1_055_mark_not_furniture_before_r_L-1b_salon.png) | ![](agent/r1_056_mark_not_furniture_after_r_L-1b_salon.png) |
| 5970 | 1 | move_piece | f_L-1_058 | adjusted_by_ai | 7.0 -> 17.0 | Shift the floor lamp right along the wall (0.3 m) to clear the 0.06 m² overlap with lamp f_L-1_057. | ![](agent/r1_058_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_059_move_piece_after_r_L-1_salon_2.png) |
| 5973 | 1 | move_piece | f_L-1_039 | adjusted_by_ai | 17.0 -> 17.0 | Pull the chair out from the table edge to clear the 0.039 m cut with table f_L-1_038. | ![](agent/r1_062_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_063_move_piece_after_r_L-1_salon_2.png) |
| 5986 | 1 | move_piece | f_L1_012 | adjusted_by_ai | 68.0 -> 78.0 | Shift the sofa 0.3 m north to open the blocked free zone in front of it (F6, blocked by f_L1_009). | ![](agent/r1_075_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_076_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 5991 | 1 | move_piece | f_L0_036 | adjusted_by_ai | 67.0 -> 90.0 | Shift nightstand 0.22 m away from the bed's right side to clear the 0.06 m² overlap and the 0.043 m cut with the bed. | ![](agent/r1_081_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_082_move_piece_after_r_L0_yatak_odasi_4.png) |
| 5992 | 1 | move_piece | f_L1_048 | added_by_ai | 78.0 -> 78.0 | Slide the bookshelf 1 m south along the west wall, out of the sloped-ceiling zone (ceiling 0.82 m at its current spot), to clear both X2 findings. | ![](agent/r1_083_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_084_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 5998 | 1 | move_piece | f_L1_011 | adjusted_by_ai | 68.0 -> 78.0 | Shift the sofa 0.3 m up to clear the blocked free zone in front of it (F6, blocked by f_L1_010). | ![](agent/r1_090_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_092_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 6000 | 1 | mark_not_furniture | f_L1_018 | adjusted_by_ai | 78.0 -> 78.0 | The recognition crop shows an organic blob outline with two small arc marks (a landscape/plan symbol), not a furniture footprint; the untyped 1.63 x 1.52 m drawn piece is not furniture. | ![](agent/r1_094_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_095_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 6005 | 1 | mark_not_furniture | f_L1_017 | adjusted_by_ai | 78.0 -> 78.0 | The recognition crop shows a round table with two curved chairs around it, not a single 1.63x1.52 m object; the code's own passes already ruled out not_furniture and unknown, and no type fits the room, so it stays marked for review. | ![](agent/r1_102_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_103_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 6017 | 1 | move_piece | f_L0_038 | adjusted_by_ai | 67.0 -> 90.0 | Shift nightstand 0.12 m away from the bed side to clear the 0.06 m² overlap (F9) and satisfy the ≤0.30 m gap (G4). | ![](agent/r1_119_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_120_move_piece_after_r_L0_yatak_odasi_3.png) |
| 6029 | 1 | report_library_gap | f_L1_023 | library_gap | - | No chair model within 10% non-uniform scale and 0.85..1.2 mean scale (closest abo_B0857JM2NC at 18.7% non-uniform); relaxed caps also yield no candidate, so the parametric build stands. | - | - |
| 6040 | 1 | move_piece | f_L1_022 | adjusted_by_ai | 90.0 -> 100.0 | Move the drawn chair slightly inward away from wall w_L1_009 to clear the 0.05 m wall cut and the 0.12 m outline protrusion. | ![](agent/r1_129_move_piece_before_r_L1_teras.png) | ![](agent/r1_131_move_piece_after_r_L1_teras.png) |
| 6051 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. | ![](agent/r1_134_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_135_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 6053 | 1 | move_piece | f_L1_021 | adjusted_by_ai | 87.0 -> 97.0 | Nudge the drawn table 0.08 m away from wall w_L1_005 so it no longer cuts the wall (S2) or reaches through the room outline (F9). | ![](agent/r1_136_move_piece_before_r_L1_koridor.png) | ![](agent/r1_137_move_piece_after_r_L1_koridor.png) |
| 6056 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the balcony group as a unit so the inappropriate dining set can be replaced by a proper terrace arrangement, resolving F1. | ![](agent/r1_139_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_140_relayout_room_after_r_L1_teras_2.png) |
| 6064 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift the nightstand 0.11 m away from the bed side to clear the 0.06 m² overlap (F9) and bring it to a positive gap ≤ 0.30 m from the bed side (G4). | ![](agent/r1_148_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_149_move_piece_after_r_L0_e_yatak_odasi.png) |
| 6069 | 1 | swap_model | f_L-1_090 | added_by_ai | 71.0 -> 71.0 | Replace the mirror-like reflective fridge model with a standard classic fridge model to fix the physically incorrect reflective surface (v:r1-v2:1). | ![](agent/r1_152_swap_model_before_r_L-1_mutfak.png) | ![](agent/r1_153_swap_model_after_r_L-1_mutfak.png) |
| 6075 | 1 | swap_model | f_L0_003 | adjusted_by_ai | 77.0 -> 77.0 | washbasin rendered as a dresser/vanity; swap to a proper washbasin fixture model | ![](agent/r1_155_swap_model_before_r_L0_banyo.png) | ![](agent/r1_156_swap_model_after_r_L0_banyo.png) |
| 6076 | 1 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | toilet model crude and low-poly; swap to a standard toilet model | ![](agent/r1_157_swap_model_before_r_L0_banyo.png) | ![](agent/r1_158_swap_model_after_r_L0_banyo.png) |
| 6316 | 2 | move_piece | f_L-1_042 | adjusted_by_ai | 17.0 -> 17.0 | The chair cuts the table by 0.038 m; moving the chair slightly away from the table edge (outwards) resolves the minor collision. | ![](agent/r2_039_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_041_move_piece_after_r_L-1_salon_2.png) |
| 6317 | 2 | move_piece | f_L-1_060 | adjusted_by_ai | 7.0 -> 17.0 | Snap the floor lamp's back to the left wall to clear the window band and the overlap with f_L-1_059. | ![](agent/r2_042_move_piece_before_r_L-1_salon.png) | ![](agent/r2_043_move_piece_after_r_L-1_salon.png) |
| 6326 | 2 | move_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 0.0 | Move chair f_L-1b_053 away from f_L-1b_052 to resolve the 0.09 m² overlap (F9) and give it ≥0.81 m clearance behind (G6). | ![](agent/r2_053_move_piece_before_r_L-1b_salon.png) | ![](agent/r2_054_move_piece_after_r_L-1b_salon.png) |
| 6333 | 2 | move_piece | f_L-1b_056 | adjusted_by_ai | 0.0 -> 0.0 | Move chair f_L-1b_056 away from f_L-1b_055 to resolve the 0.09 m² overlap (F9) and give it ≥0.81 m clearance behind (G6). | ![](agent/r2_060_move_piece_before_r_L-1b_salon.png) | ![](agent/r2_061_move_piece_after_r_L-1b_salon.png) |
| 6334 | 2 | remove_piece | f_L1_056 | added_by_ai | 78.0 -> 78.0 | AI-added bookshelf stands under the sloped ceiling (0.82 m headroom) and pokes through the roof; all move attempts failed, so remove it. | ![](agent/r2_062_remove_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_063_remove_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 6358 | 2 | move_piece | f_L1_029 | adjusted_by_ai | 78.0 -> 88.0 | bring armchair within 2.5 m of the coffee table to clear G3 | ![](agent/r2_078_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_080_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 6361 | 2 | move_piece | f_L1_024 | adjusted_by_ai | 77.0 -> 87.0 | Move table 0.1m in -y to clear wall w_L1_006 and room outline collision. | ![](agent/r2_082_move_piece_before_r_L1_koridor_2.png) | ![](agent/r2_083_move_piece_after_r_L1_koridor_2.png) |
| 6364 | 2 | rotate_piece | f_L1_025 | adjusted_by_ai | 87.0 -> 97.0 | Rotate chair to face 0 degrees (+x direction) towards the table at x=13.61 to satisfy the group orientation check. | ![](agent/r2_087_rotate_piece_before_r_L1_koridor_2.png) | ![](agent/r2_088_rotate_piece_after_r_L1_koridor_2.png) |
| 6597 | 3 | move_piece | f_L-1_059 | adjusted_by_ai | 17.0 -> 27.0 | Move floor lamp f_L-1_059 0.25 m away from the window to unblock the opening (G12). | ![](agent/r3_034_move_piece_before_r_L-1_salon.png) | ![](agent/r3_035_move_piece_after_r_L-1_salon.png) |
| 6608 | 3 | move_piece | f_L-1b_059 | adjusted_by_ai | 0.0 -> 0.0 | Move chair f_L-1b_059 away from f_L-1b_058 to resolve overlap (F9) and clearance (G6) | ![](agent/r3_045_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_046_move_piece_after_r_L-1b_salon_2.png) |
| 6610 | 3 | move_piece | f_L-1b_062 | adjusted_by_ai | 0.0 -> 0.0 | Move chair f_L-1b_062 away from f_L-1b_061 to resolve overlap (F9) and clearance (G6) | ![](agent/r3_047_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_048_move_piece_after_r_L-1b_salon_2.png) |
| 6631 | 3 | move_piece | f_L-1_038 | adjusted_by_ai | 17.0 -> 17.0 | Table f_L-1_038 cuts chair f_L-1_042 by 0.033 m; shifting 0.03 m clears the S2 collision. | ![](agent/r3_062_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_064_move_piece_after_r_L-1_salon_2.png) |
| 6642 | 3 | move_piece | f_L0_030 | adjusted_by_ai | 90.0 -> 90.0 | Shift wardrobe 0.29 m (under the 0.3 m drawn_lock cap) away from window win_L0_005 to clear the G12 blocked-opening finding. | ![](agent/r3_071_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_072_move_piece_after_r_L0_yatak_odasi_4.png) |
| 6653 | 3 | move_piece | f_L0_029 | adjusted_by_ai | 90.0 -> 90.0 | Shift wardrobe 0.29 m north off the window band to clear G12 | ![](agent/r3_076_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_078_move_piece_after_r_L0_yatak_odasi_3.png) |
| 6668 | 3 | add_camera | ext_front_entrance | agent_override | - | Frontal exterior view of the +y entrance facade from the free stretch of the view line, eye height 1.6 m over the ground there. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 5941 | 1 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 7 more kept | Candidate 1 (score 9.39) re-solves the seating group and moves the floor lamps, resolving the G11 walkway, G12 window-blocking, F4 orientation and F9 collision findings while keeping the drawn anchors. |
| 5949 | 1 | move_piece | f_L-1b_041 | snap: f_L-1b_041: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | F3: sofa back 2.00 m off wall; snap its back to the left wall (span s4) at its drawn height to form the seating zone. |
| 5950 | 1 | move_piece | f_L-1b_041 | drawn_lock: f_L-1b_041: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.74 m) | F3: sofa back 2.00 m off wall; move it 0.3 m left so its back sits on the left wall (span s4) at its drawn height. |
| 5951 | 1 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [15.67, 4.27]): the size table and the room / zone give none | Untyped 5.54 x 0.60 m drawn piece is a long storage unit; sideboard fits its size and the living room, resolving the untyped finding. |
| 5952 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 7 -> -13 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Armchair faced the back of the sofa; turning it 180° makes it face the room and the seating group. |
| 5953 | 1 | move_piece | f_L-1_058 | drawn_lock: f_L-1_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.44 m) | Shift the floor lamp right along the wall to clear the 0.06 m² overlap with lamp f_L-1_057. |
| 5954 | 1 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | Shift the coffee table away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 5957 | 1 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | F3: sofa back 0.59 m off wall; snap its back onto the left wall (span s4) at its drawn height. |
| 5958 | 1 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.59 m) | F3: sofa back 0.59 m off wall; move it 0.59 m left so its back sits on the left wall (span s4) at its drawn height. |
| 5959 | 1 | move_piece | f_L-1b_042 | snap: f_L-1b_042: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | F3: put the sofa's back on the right wall (span s1) instead of 1.95 m off it. |
| 5960 | 1 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | F3: put the sofa's back on the right wall (span s1) instead of 0.59 m off it. |
| 5961 | 1 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 4.75 m) | F8+G12: move the plant off the window band and beside the sofa on the right wall. |
| 5962 | 1 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.85 m) | G12/F8: move the potted plant 0.85 m up off the window band and into the corner beside the floor lamp, next to the left wall. |
| 5963 | 1 | move_piece | f_L-1b_050 | drawn_lock: f_L-1b_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 5.56 m) | F8: move the floor lamp to the corner beside the sofa on the right wall. |
| 5964 | 1 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.81 m) | F9+G6: move the chair to the free side of table f_L-1b_051, clearing the overlap with f_L-1b_052 and giving 0.8 m behind. |
| 5965 | 1 | move_piece | f_L-1b_056 | drawn_lock: f_L-1b_056: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.81 m) | F9+G6: move the chair to the free side of table f_L-1b_054, clearing the overlap with f_L-1b_055 and giving 0.8 m behind. |
| 5966 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | G6: nudge the chair 3 cm so the clearance behind it reaches 0.81 m. |
| 5967 | 1 | complete_group | r_L-1b_salon_kitchen.kitchen_run | no_place: r_L-1b_salon_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | G9: add the missing fridge to the kitchen run. |
| 5969 | 1 | move_piece | f_L-1b_047 | snap: f_L-1b_047: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | G12/F8: snap the potted plant to the left wall (span s4) at 1.0 m, off the window band and beside the floor lamp. |
| 5971 | 1 | move_piece | f_L-1_074 | acceptance: finding F9:f_L-1_074 is still there after the edit (table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.23 m²) | Shift the coffee table right, away from armchair f_L-1_069, to clear the 0.12 m² overlap. |
| 5972 | 1 | move_piece | f_L-1b_047 | acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | G12: move the potted plant 0.3 m up so its top (1.0 m) clears the window sill (0.90 + 0.05). |
| 5974 | 1 | move_piece | f_L-1_042 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Pull the chair out from the table edge to clear the 0.038 m cut with table f_L-1_038. |
| 5976 | 1 | move_piece | f_L-1b_048 | acceptance: finding F8:f_L-1b_048 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | F8: move the floor lamp 0.3 m up, off the window band and into the corner beside the potted plant, next to the left wall. |
| 5977 | 1 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | no_place: r_L-1b_salon_2_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | G9: the kitchen run is missing its fridge; add it so the solver places it in the run. |
| 5978 | 1 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | F9/G6: move chair f_L-1b_059 0.31 m away from the table so it no longer overlaps f_L-1b_058 and gains seating clearance. |
| 5979 | 1 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | F9: move chair f_L-1b_059 0.3 m away from the table so it no longer overlaps f_L-1b_058. |
| 5982 | 1 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | Shift the coffee table left, away from armchair f_L-1_069, to clear the 0.12 m² overlap. |
| 5983 | 1 | move_piece | f_L-1_057 | acceptance: finding G12:f_L-1_057 is still there after the edit (floor_lamp f_L-1_057 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | Move the floor lamp right along the wall, away from the window centre, to clear the blocked opening G12. |
| 5984 | 1 | move_piece | f_L-1_065 | score: plausibility 17 -> 7 (F9 f_L-1_066: floor_lamp f_L-1_066 overlaps floor_lamp f_L-1_065 by 0.10 m²) | Move the floor lamp left along the wall, away from the window centre, to clear the blocked opening G12. |
| 5985 | 1 | move_piece | f_L1_048 | snap: f_L1_048: no free place on wall w_L1_001 (doors, windows) | Move the bookshelf off the sloped-ceiling zone (ceiling 0.82 m there) to the south wall where the ceiling is full height, clearing both X2 findings. |
| 5987 | 1 | rotate_piece | f_L1_029 | acceptance: finding G3:f_L1_029 is still there after the edit (armchair f_L1_029 is 0° off the table_coffee f_L1_015 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Turn the armchair to face the coffee table (G3: 12° off and 2.73 m away, needs ≤30° and ≤2.5 m). |
| 5988 | 1 | retype_piece | f_L1_017 | retype: table_coffee is no candidate for f_L1_017 (1.63 x 1.52 m at [3.81, 2.27]): the size table and the room / zone give sofa_corner, stair | The recognition crop shows a round table with two curved chairs around it, not a single 1.63x1.52 m object; type it as a coffee table to build it. |
| 5993 | 1 | move_piece | f_L1_029 | drawn_lock: f_L1_029: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the armchair 0.3 m south to bring it within 2.5 m of the coffee table (G3: 2.73 m, needs ≤ 2.5 m). |
| 5994 | 1 | retype_piece | f_L1_017 | room_type: sofa_corner is not a piece a other room may hold here | The recognition crop shows a round table with two curved chairs around it, not a single 1.63x1.52 m object; type it as a corner sofa to build it. |
| 5995 | 1 | retype_piece | f_L0_026 | score: plausibility 60 -> 30 (F8 f_L0_042: office_chair stands alone in the room (no wall, no desk within 1.0 m); F9 f_L0_042: office_chair f_L0_042 overlaps dresser f_L0_026 by 0.10 m²; G13 f_L0_026: dresser f_L0_026: 0.31 m free in front, needs ≥ 0.80 m) | Desk+office chair are not standard bedroom fixtures (F1); the 1.45x0.6 m drawn piece fits a dresser, which suits the bedroom. |
| 5996 | 1 | move_piece | f_L1_056 | acceptance: finding X2:f_L1_056 is still there after the edit (f_L1_056: bookshelf with its top 2.02 m above the floor stands where the sloped ceiling is 1.44 m high; it shows through the ceiling) | Move the bookshelf away from the sloped-ceiling corner (top 5.17 m pokes through the roof) to a spot with full headroom along the same wall. |
| 5997 | 1 | move_piece | f_L0_030 | snap: f_L0_030: no free place on wall w_L0_012 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe off the window band onto the free west wall span (2.06 m) so it no longer blocks window win_L0_005. |
| 5999 | 1 | rotate_piece | f_L1_030 | f_L1_030: clearance_ok, score: plausibility 78 -> 68 (F6 f_L1_030: armchair: the free zone in front of it is blocked by f_L1_027; G3 f_L1_030: armchair f_L1_030 is 41° off the sofa f_L1_010 (needs ≤ 30°) at 2.75 m (needs ≤ 2.50 m)) | Turn the armchair to face the coffee table f_L1_016 (G3: 12° off, needs ≤ 30°). |
| 6001 | 1 | retype_piece | f_L1_035 | retype: bench is no candidate for f_L1_035 (1.40 x 0.45 m at [10.07, 7.22]): the size table and the room / zone give bookshelf, console_table, desk, display_cabinet, sideboard, table_coffee, tv_unit | Confirm the bench type (a bench fits this activity/rest room) to clear the F1/G14 wrong-type findings. |
| 6002 | 1 | move_piece | f_L0_030 | drawn_lock: f_L0_030: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.50 m) | Shift the wardrobe 0.5 m north, off the window band, keeping its back on the south wall. |
| 6003 | 1 | move_piece | f_L1_029 | acceptance: finding G3:f_L1_029 is still there after the edit (armchair f_L1_029 is 23° off the table_coffee f_L1_015 (needs ≤ 30°) at 3.13 m (needs ≤ 2.50 m)) | Snap the armchair's back to the south wall at its drawn position (0.3 m allowance) to bring it within 2.5 m of the coffee table (G3: 2.73 m). |
| 6004 | 1 | move_piece | f_L0_030 | drawn_lock: f_L0_030: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the wardrobe 0.3 m north, off the window band, keeping its back on the south wall. |
| 6006 | 1 | move_piece | f_L0_030 | max_tries: f_L0_030 was edited 3 times in this round | Shift the wardrobe 0.29 m north, off the window band, keeping its back on the south wall. |
| 6007 | 1 | move_piece | f_L1_056 | score: plausibility 78 -> 68 (G6 f_L1_052: chair f_L1_052: 0.80 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the bookshelf to mid-wall where the ceiling is at full height, clearing the sloped-ceiling zone that made its top show through the roof. |
| 6008 | 1 | retype_piece | f_L1_035 | room_type: console_table is not a piece a other room may hold here | Retype the 1.40 x 0.45 m bench to a console table, a type that fits its size and this activity/rest room, clearing F1/G14. |
| 6009 | 1 | move_piece | f_L1_030 | drawn_lock: f_L1_030: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the armchair 0.3 m toward the coffee table to bring it within the 2.50 m reach required by G3. |
| 6012 | 1 | move_piece | f_L1_056 | acceptance: finding X2:f_L1_056 is still there after the edit (f_L1_056: bookshelf with its top 2.02 m above the floor stands where the sloped ceiling is 1.82 m high; it shows through the ceiling) | Move the bookshelf to mid-wall (clear of the sloped-ceiling corner and of the dining chairs) where the ceiling is at full height. |
| 6014 | 1 | retype_piece | f_L1_035 | room_type: sideboard is not a piece a other room may hold here | Retype the 1.40 x 0.45 m bench to a sideboard, a type that fits its size and this activity/rest room, clearing F1/G14. |
| 6019 | 1 | move_piece | f_L0_029 | snap: f_L0_029: no free place on wall w_L0_004 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe off the window band win_L0_006 onto the free wall span s0 (into the room, front facing 90°) to clear G12. |
| 6023 | 1 | move_piece | f_L0_029 | snap: f_L0_029: no free place on wall w_L0_019 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe off the window band win_L0_006 onto the free wall span s1 (front facing 180° into the room) to clear G12. |
| 6024 | 1 | move_piece | f_L0_029 | drawn_lock: f_L0_029: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Shift the wardrobe 0.31 m into the room so its back clears the window band win_L0_006 (sill 0.90 m + 0.05) to clear G12. |
| 6027 | 1 | move_piece | f_L1_024 | acceptance: finding F9:f_L1_024 is still there after the edit (table_coffee reaches 0.07 m² through the room outline, up to 0.060 m deep); 1 more kept | Shift table 0.06 m in +x to clear wall w_L1_006 and the room outline collision (F9, S2). |
| 6028 | 1 | rotate_piece | f_L1_025 | acceptance: finding F4:f_L1_025 is still there after the edit (chair does not face its group (f_L1_024)) | Turn the chair to face the table (90°) to satisfy the group orientation check F4. |
| 6030 | 1 | retype_piece | f_L1_021 | retype: side_table is no candidate for f_L1_021 (1.20 x 0.70 m at [3.56, 9.90]): the size table and the room / zone give none | Drawn table with a chair around it in a hall: table_coffee is not a hall piece (F1/G14) and the AI passes read it as bench (RC); side_table fits its 1.2x0.7 footprint and the hall, and the refit clears the wall cut (S2/F9). |
| 6031 | 1 | move_piece | f_L0_029 | max_tries: f_L0_029 was edited 3 times in this round | Shift the wardrobe 0.30 m into the room so its back clears the window band win_L0_006 (sill 0.90 m + 0.05) to clear G12. |
| 6041 | 1 | remove_piece | f_L1_037 | score: plausibility 100 -> 80 (F8 f_L1_038: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m); F8 f_L1_039: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m)) | Outdoor terrace (balcony) is not furnished with a dining table; removes the F1 wrong_type finding. |
| 6044 | 1 | remove_piece | f_L1_038 | score: plausibility 100 -> 97 (G6 f_L1_037: dining table f_L1_037 has 1 of 2 chairs) | Chair of the inappropriate dining set on an outdoor terrace (F1); removed before the table so no chair is left standing alone. |
| 6048 | 1 | remove_piece | f_L1_038 | memory: the same edit was rejected in round 1: score: plausibility 100 -> 97 (G6 f_L1_037: dining table f_L1_037 has 1 of 2 chairs) | Chair of the inappropriate dining set on an outdoor terrace (F1); both chairs go before the table so no incomplete group remains. |
| 6050 | 1 | remove_piece | f_L1_039 | score: plausibility 100 -> 97 (G6 f_L1_037: dining table f_L1_037 has 1 of 2 chairs) | Chair of the inappropriate dining set on an outdoor terrace (F1); removed together with its partner chair before the table so no incomplete group remains. |
| 6054 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free right side of the head. |
| 6058 | 1 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_008: re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free right side of the head. |
| 6061 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_008: re-solve the drawn sleeping_double group around the bed anchor with the bench option so a nightstand is placed on the free right side of the head. |
| 6063 | 1 | move_piece | f_L0_032 | acceptance: finding F9:f_L0_032 is still there after the edit (nightstand f_L0_032 overlaps bed_double f_L0_007 by 0.16 m²) | Shift the nightstand 0.22 m away from the bed side to clear the 0.06 m² overlap (F9) and bring it to a positive gap ≤ 0.30 m from the bed side (G4). |
| 6067 | 1 | retype_piece | f_L-1_090 | no_change: f_L-1_090 is already a fridge | Rebuild the fridge with a standard appliance material to fix the mirror-like reflective surface (v:r1-v2:1). |
| 6071 | 1 | fix_fixture | f_L0_003 | fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_009) | door d_L0_009 swings into the washbasin; let the code search for a valid spot within 0.5 m |
| 6304 | 2 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [1.50, 4.27]): the size table and the room / zone give none | Untyped 5.54 x 0.60 m drawn piece is a long low storage unit fitting the living room and free wall span s0. |
| 6305 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 7 -> -13 (F4 f_L-1_070: armchair faces a wall 0.11 m in front of it; F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 136° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn the armchair away from the sofa back so it no longer looks at the back of f_L-1_053. |
| 6308 | 2 | relayout_room | r_L-1b_salon | f_L-1b_042: clearance_ok | Candidate 1 re-solves the seating groups: sofas against walls (F3), plant and lamp near seating (F8), plant off the window (G12), and adds TV unit and coffee table (G1/G2). |
| 6309 | 2 | relayout_room | r_L-1b_salon | f_L-1b_042: clearance_ok | Candidate 2 re-solves the seating groups: sofas against walls (F3), plant and lamp near seating (F8), plant off the window (G12), and adds TV unit and coffee table (G1/G2). |
| 6310 | 2 | move_piece | f_L-1_060 | drawn_lock: f_L-1_060: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.56 m) | Move the floor lamp away from the window band and clear the 0.06 m² overlap with f_L-1_059. |
| 6311 | 2 | move_piece | f_L-1_059 | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.85 m) | Move the floor lamp away from the window band to unblock win_L-1_001. |
| 6312 | 2 | relayout_room | r_L-1b_salon | f_L-1b_042: clearance_ok | Candidate 3 re-solves the seating groups: sofas against walls (F3), plant and lamp near seating (F8), plant off the window (G12), and adds TV unit and coffee table (G1/G2). |
| 6313 | 2 | retype_piece | f_L-1_022 | memory: the same edit was rejected in round 1: retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [15.67, 4.27]): the size table and the room / zone give none | The untyped 5.54 x 0.60 m drawn piece is a long storage unit (sideboard) that fits the living room and the free wall span s0; retyping it resolves the untyped finding. |
| 6314 | 2 | move_piece | f_L-1_057 | drawn_lock: f_L-1_057: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.41 m) | The floor lamp blocks the window; moving it to the right along the wall, away from the window center, clears the blocked opening finding. |
| 6315 | 2 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.67 m) | The floor lamp blocks the window; moving it to the left along the wall, away from the window center, clears the blocked opening finding. |
| 6318 | 2 | move_piece | f_L-1_059 | snap: f_L-1_059: no free place on wall w_L-1_007 (doors, windows, at most 1.2 m from the drawn place) | Snap the floor lamp's back to the left wall to unblock win_L-1_001. |
| 6321 | 2 | move_piece | f_L-1_057 | f_L-1_057: no_overlap, f_L-1_058: no_overlap | The floor lamp blocks the window; moving it 0.11 m to the right along the wall, away from the window center, clears the blocked opening finding. |
| 6322 | 2 | move_piece | f_L-1_059 | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the floor lamp 0.3 m away from the window band to unblock win_L-1_001. |
| 6323 | 2 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the floor lamp 0.3 m away from the window band to unblock win_L-1_001. |
| 6324 | 2 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | The floor lamp blocks the window; moving it 0.07 m to the right along the wall, away from the window center, clears the blocked opening finding. |
| 6325 | 2 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Move chair f_L-1b_053 away from f_L-1b_052 to resolve the 0.09 m² overlap (F9) and give it ≥0.81 m clearance behind (G6). |
| 6327 | 2 | move_piece | f_L-1b_041 | snap: f_L-1b_041: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto left wall span s4 to fix F3 (back 2.00 m off wall) |
| 6328 | 2 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap second sofa back onto left wall span s4 to fix F3 (back 0.59 m off wall) |
| 6329 | 2 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 17 -> 7 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | The armchair stands behind the back of the sofa facing it; turning it 90° so its front faces into the room (towards the window side) resolves the orientation finding. |
| 6331 | 2 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.37 m) | The coffee table overlaps armchair f_L-1_069; moving the table 0.35 m away from the armchair (towards the center of the seating group) clears the collision. |
| 6332 | 2 | relayout_room | r_L-1_salon_2 | acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 2 more kept | The seating group (sofa and armchairs) is too close to the dining area, blocking the 0.60 m walkway from the door; relayouting the room with candidate 1 resolves the clearance findings. |
| 6335 | 2 | move_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1b_041: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.74 m) | Shift sofa 0.26 m left toward the left wall to reduce the F3 off-wall distance (snap to wall has no free place within 1.2 m) |
| 6336 | 2 | move_piece | f_L-1b_045 | acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)) | Shift second sofa 0.30 m left toward the left wall to reduce the F3 off-wall distance (snap to wall has no free place within 1.2 m) |
| 6337 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_033 slightly to increase clearance from table edge to wall from 0.78 m to ≥ 0.81 m (G6). |
| 6338 | 2 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | The coffee table overlaps armchair f_L-1_069; moving the table 0.3 m away from the armchair (towards the center of the seating group) clears the collision. |
| 6339 | 2 | relayout_room | r_L-1_salon_2 | candidate: candidate 2 does not exist: 1 usable candidate(s) | The seating group (sofa and armchairs) is too close to the dining area, blocking the 0.60 m walkway from the door; relayouting the room with candidate 2 resolves the clearance findings. |
| 6340 | 2 | move_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1b_041: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.74 m) | Shift sofa 0.26 m left toward the left wall to reduce the F3 off-wall distance (snap to wall has no free place within 1.2 m) |
| 6341 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 2: acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)) | Shift second sofa 0.30 m left toward the left wall to reduce the F3 off-wall distance (snap to wall has no free place within 1.2 m) |
| 6342 | 2 | move_piece | f_L-1b_042 | drawn_lock: f_L-1b_042: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.71 m) | Move sofa f_L-1b_042 to the right wall (w_L-1b_010) to fix F3 (back not on a wall, 1.95 m off). |
| 6344 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 2: acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)) | Shift second sofa 0.30 m left toward the left wall to reduce the F3 off-wall distance (snap to wall has no free place within 1.2 m) |
| 6345 | 2 | move_piece | f_L-1b_047 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move potted plant 0.30 m up off the window band to clear G12 (blocked opening) |
| 6346 | 2 | move_piece | f_L-1b_049 | acceptance: finding F8:f_L-1b_049 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move potted plant f_L-1b_049 away from window win_L-1b_001 (G12) and closer to sofa f_L-1b_046 (F8). |
| 6349 | 2 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Individual move_piece attempts for the wardrobe and bed were rejected last round; a full solver relayout repositions the storage and sleeping groups together to clear the window and bed side clearances. |
| 6350 | 2 | move_piece | f_L-1b_047 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move potted plant 0.30 m up off the window band to clear G12 (blocked opening) |
| 6351 | 2 | move_piece | f_L-1b_048 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_048 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Move floor lamp 0.30 m up off the window band toward the left wall to clear G12 and F8 |
| 6354 | 2 | move_piece | f_L1_024 | acceptance: finding F9:f_L1_024 is still there after the edit (table_coffee reaches 0.07 m² through the room outline, up to 0.060 m deep); 1 more kept | Move table 0.06m in -x away from wall w_L1_006 to clear the wall cut and room outline collision. |
| 6359 | 2 | relayout_room | r_L0_yatak_odasi_4 | no_place: r_L0_yatak_odasi_4 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room so the drawn wardrobe f_L0_030 leaves the window win_L0_005 band (G12), since direct move_piece attempts were rejected by drawn_lock. |
| 6363 | 2 | relayout_room | r_L0_yatak_odasi_3 | no_place: r_L0_yatak_odasi_3 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room so the wardrobe f_L0_029 leaves the window win_L0_006 band (G12), since direct snaps and a 0.31 m shift were rejected. |
| 6366 | 2 | retype_piece | f_L1_024 | retype: table_dining is no candidate for f_L1_024 (1.20 x 0.70 m at [13.61, 9.80]): the size table and the room / zone give none | Retype as table_dining: the RC finding confirms it is a table with chairs drawn around it, and a dining table fits a hall room better than a coffee table. |
| 6368 | 2 | move_piece | f_L1_049 | acceptance: finding X2:f_L1_049 is still there after the edit (f_L1_049: console_table with its top 0.84 m above the floor stands where the sloped ceiling is 0.82 m high; it shows through the ceiling) | Console table top (0.84 m) pokes through the sloped ceiling (0.82 m) at its current spot; move it along the free wall span s4 where the ceiling is higher. |
| 6586 | 3 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 17 -> 7 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair f_L-1_070 to face the seating area (90°) instead of the sofa back, resolving F4 orientation finding. |
| 6587 | 3 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Move coffee table f_L-1_073 slightly away from armchair f_L-1_071 to clear the 0.12 m² overlap (F9). |
| 6588 | 3 | retype_piece | f_L-1_022 | memory: the same edit was rejected in round 1: retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [15.67, 4.27]): the size table and the room / zone give none | Untyped 5.54 x 0.60 m drawn piece is a long storage unit (sideboard) fitting the living room; retyping resolves the untyped finding. |
| 6589 | 3 | rotate_piece | f_L-1_072 | memory: the same edit was rejected in round 1: f_L-1_072: clearance_ok; score: plausibility 7 -> -13 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤  | Armchair faces the back of the sofa; rotating 180° makes it face the room and the seating group, fixing F4. |
| 6590 | 3 | relayout_room | r_L-1b_salon | memory: the same edit was rejected in round 2: f_L-1b_042: clearance_ok | Re-solve seating groups: sofas against walls (F3), plant/lamp near seating (F8), plant out of window (G12), add TV/coffee tables (G1/G2). |
| 6591 | 3 | rotate_piece | f_L-1b_053 | acceptance: finding G6:f_L-1b_053 is still there after the edit (chair f_L-1b_053 is 120° off the table f_L-1b_051 (needs ≤ 45°)) | Face chair toward dining table f_L-1b_051 (fixes F4/G6 orientation). |
| 6592 | 3 | rotate_piece | f_L-1b_056 | score: plausibility -38 -> -48 (F4 f_L-1b_056: chair does not face its group (f_L-1b_054, f_L-1b_051); G6 f_L-1b_056: chair f_L-1b_056 is 120° off the table f_L-1b_054 (needs ≤ 45°)) | Face chair toward dining table f_L-1b_054 (fixes G6 orientation). |
| 6593 | 3 | move_piece | f_L-1_074 | score: plausibility 17 -> 7 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.08 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Coffee table overlaps armchair f_L-1_069; shifting 0.25 m toward the seating centre clears the collision within the 0.179 m allowance. |
| 6594 | 3 | move_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1b_041: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.74 m) | Move sofa f_L-1b_041 to left wall (s4) to satisfy back-on-wall constraint (F3) |
| 6595 | 3 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.38 m) | Move sofa f_L-1b_045 to left wall (s4) to satisfy back-on-wall constraint (F3) |
| 6596 | 3 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move coffee table f_L-1_073 0.28 m away from armchair f_L-1_071 to clear the 0.12 m² overlap (F9). |
| 6598 | 3 | move_piece | f_L-1_063 | f_L-1_053: no_overlap | Move floor lamp f_L-1_063 0.25 m away from the window to unblock the opening (G12). |
| 6599 | 3 | move_piece | f_L-1_057 | drawn_lock: f_L-1_057: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | Floor lamp blocks window win_L-1_002; moving it right along the wall toward the corner clears the blocked opening. |
| 6600 | 3 | relayout_room | r_L-1b_salon_2 | f_L-1b_041: clearance_ok, group checks: F4 f_L-1b_045: sofa does not face its group (f_L-1b_087) | Use solver candidate 1 to re-place AI pieces and resolve sofa back-on-wall, floating plant/lamp, and chair clearance issues |
| 6601 | 3 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 2: drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Floor lamp blocks window win_L-1_002; moving it left along the wall toward the corner clears the blocked opening. |
| 6602 | 3 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (chair does not face its group (f_L-1b_051, f_L-1b_054)); 1 more kept | Face chair toward dining table f_L-1b_051 (table is ~60° from +x; 120° is within 45° of it). |
| 6603 | 3 | rotate_piece | f_L-1b_056 | score: plausibility -38 -> -48 (F4 f_L-1b_056: chair does not face its group (f_L-1b_054, f_L-1b_051); G6 f_L-1b_056: chair f_L-1b_056 is 180° off the table f_L-1b_054 (needs ≤ 45°)) | Face chair toward dining table f_L-1b_054 (table is ~60° from +x; 120° is within 45° of it). |
| 6604 | 3 | move_piece | f_L-1b_055 | score: plausibility -38 -> -48 (F4 f_L-1b_055: chair does not face its group (f_L-1b_054, f_L-1b_051); G6 f_L-1b_055: chair f_L-1b_055 is 62° off the table f_L-1b_054 (needs ≤ 45°)) | Pull chair away from the wall behind it to reach the 0.81 m clearance needed behind the chair. |
| 6605 | 3 | move_piece | f_L-1_073 | score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.08 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table f_L-1_073 0.27 m away from armchair f_L-1_071 to clear the 0.12 m² overlap (F9). |
| 6606 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift chair slightly to gain the 0.81 m clearance behind it (was 0.78 m). |
| 6607 | 3 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.35 m) | Move floor lamp f_L-1_063 0.25 m right and away from the window to unblock the opening (G12) without overlapping the sofa. |
| 6609 | 3 | relayout_room | r_L-1_salon_2 | memory: the same edit was rejected in round 2: acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 2 more kept | Seating group blocks the 0.60 m walkway from the door; relayouting with candidate 1 resolves the G11 clearance findings. |
| 6611 | 3 | move_piece | f_L-1_050 | drawn_lock: f_L-1_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Armchair blocks the 0.60 m walkway from the door; moving it 0.3 m toward the sofa clears the G11 clearance finding. |
| 6612 | 3 | move_piece | f_L-1b_055 | drawn_lock: f_L-1b_055: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.39 m) | Pull chair away from the wall behind it to reach the 0.81 m clearance (was 0.09 m). |
| 6613 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift chair 0.1 m to gain the 0.81 m clearance behind it (was 0.78 m). |
| 6614 | 3 | relayout_room | r_L-1_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 7 more kept | Re-solve the room layout using candidate 1 to ensure 0.60 m walkways reach the front use zones of the seating group pieces (G11). |
| 6615 | 3 | move_piece | f_L-1_063 | f_L-1_053: no_overlap | Move floor lamp f_L-1_063 0.24 m away from the window to unblock the opening (G12). |
| 6616 | 3 | move_piece | f_L-1_050 | drawn_lock: f_L-1_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.33 m) | Armchair blocks the 0.60 m walkway from the door; moving it 0.27 m toward the sofa clears the G11 clearance finding. |
| 6617 | 3 | move_piece | f_L-1b_055 | score: plausibility -38 -> -48 (F4 f_L-1b_055: chair does not face its group (f_L-1b_054, f_L-1b_051); G6 f_L-1b_055: chair f_L-1b_055 is 61° off the table f_L-1b_054 (needs ≤ 45°)) | Pull chair 0.28 m away from the wall behind it to reach the 0.81 m clearance (was 0.09 m). |
| 6618 | 3 | move_piece | f_L-1b_047 | f_L-1b_047: inside_room | Move potted plant to corner near left wall to resolve floating (F8) and window blockage (G12) |
| 6619 | 3 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.84 m) | Move floor lamp to left wall corner to resolve floating (F8) |
| 6620 | 3 | move_piece | f_L-1_050 | f_L-1_050: no_overlap, f_L-1_054: clearance_ok, f_L-1_088: no_overlap, score: plausibility 17 -> -3 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050; F9 f_L-1_088: table_coffee f_L-1_088 overlaps armchair f_L-1_050 by 0.08 m²) | Armchair blocks the 0.60 m walkway from the door; moving it 0.25 m toward the sofa clears the G11 clearance finding. |
| 6621 | 3 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_024 slightly away from table to increase clearance from 0.78m to ≥0.81m (G6) |
| 6622 | 3 | move_piece | f_L-1b_055 | memory: the same edit was rejected in round 3: score: plausibility -38 -> -48 (F4 f_L-1b_055: chair does not face its group (f_L-1b_054, f_L-1b_051); G6 f_L-1b_055: chair f_L-1b_055 is 61° off the table f_L-1b_054 (needs ≤ 45°)) | Pull chair 0.28 m away from the wall behind it to reach the 0.81 m clearance (was 0.09 m). |
| 6624 | 3 | move_piece | f_L-1_063 | max_tries: f_L-1_063 was edited 3 times in this round | Move floor lamp f_L-1_063 0.23 m away from the window to unblock the opening (G12). |
| 6625 | 3 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Move coffee table f_L-1_073 0.25 m away from armchair f_L-1_071 to clear the 0.12 m² overlap (F9). |
| 6626 | 3 | move_piece | f_L-1_042 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Chair f_L-1_042 cuts table f_L-1_038 by 0.033 m; shifting 0.05 m clears the S2 collision. |
| 6629 | 3 | move_piece | f_L-1b_047 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move potted plant up slightly to clear the window sill (G12) while staying near left wall |
| 6630 | 3 | move_piece | f_L-1b_048 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_048 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Move floor lamp up 0.3m to be closer to sofa f_L-1b_041 (within 1.2m) to resolve floating (F8) |
| 6634 | 3 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.38 m) | Move potted plant closer to left wall and up to clear window (G12) and be near wall (F8) |
| 6645 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_011: clearance_ok | Solver candidate 1 re-solves the seating groups around the drawn sofas, fixing the armchair f_L1_030 orientation/distance to the coffee table (G3) and adding the missing coffee table for sofa f_L1_011 (G2). |
| 6649 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_011: clearance_ok | Solver candidate 2 re-solves the seating groups around the drawn sofas, fixing the armchair f_L1_030 orientation/distance to the coffee table (G3) and adding the missing coffee table for sofa f_L1_011 (G2). |
| 6656 | 3 | set_terrain | set_terrain | score: the level findings rise from 1 to 13, L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -2.74 m (3.26 m apart), L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -0.29 m (2.71 m apart), L4 lm_005: level mark '40.00' (lm_005, ground_finished) reads -3.00 m; the ground there is built at -2.60 m (0.40 m apart), L4 lm_006: level mark '43.00' (lm_006, ground_finished) reads +0.00 m; the ground there is built at -0.29 m (0.29 m apart), L4 lm_007: level mark '40.00' (lm_007, ground_finished) reads -3.00 m; the ground there is built at -1.57 m (1.43 m apart) | Flatten the site slope to bring it within the 1:3 limit, resolving the major terrain finding. |
| 6662 | 3 | add_camera | ext_front_entrance | the camera stands inside the building b2 (another building on the plot), eye height 0.43 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (8.5, 24) is at z 1.17 m: use z 2.67 to 2.87 for an eye-level view, free on the view line from the target: (8.50, 12.50) to (8.50, 18.20), 0.0-5.7 m from the target (a building stands beyond it); a camera there stands at eye height over the ground there, and the view keeps the 26 mm eye-level lens, level (the wider or tilted framing is for a long, low building only) | Add a frontal exterior view of the +y entrance facade (doors d_L0_005/d_L0_006) to resolve the missing frontal view finding. |
| 6665 | 3 | add_camera | ext_front_entrance | eye height 2.70 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (8.5, 17.5) is at z 0.00 m: use z 1.50 to 1.70 for an eye-level view | Frontal exterior view of the +y entrance facade from the free stretch of the view line (y up to 18.2), eye height over the ground there. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F9 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| F9 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| G8 | minor | f_L-1_067 | r_L-1_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_068 | r_L-1_mutfak_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_090 | r_L-1_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1_096 | r_L-1_mutfak_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_057 | r_L-1_salon_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_007 | r_L0_e_yatak_odasi | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_010 | r_L0_yatak_odasi_3 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_027 | r_L0_yatak_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_028 | r_L0_yatak_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_021 | r_L1_koridor | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_022 | r_L1_teras | - | within_tolerance | 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_024 | r_L1_koridor_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | critical | dec_L1_005 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X2 | critical | dec_L1_014 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| lighting_dark | minor | cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | - | lighting_within_step | 1, 2, 3 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon_2 | cut | 1 | 10428 | 32768 |
| 1 | r_L0_yatak_odasi | cut | 1 | 35442 | 32768 |
| 1 | building | cut | 1 | 40106 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 6985 | 32768 |
| 2 | building | cut | 1 | 40106 | 32768 |
| 3 | r_L-1b_salon | cut | 2 | 11993 | 32768 |
| 3 | r_L-1b_salon_2 | cut | 2 | 7388 | 32768 |

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
| f_L-1_038 | piece | table_dining | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Table f_L-1_038 cuts chair f_L-1_042 by 0.033 m; shifting 0.03 m clears the S2 collision. |
| f_L-1_039 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Pull the chair out from the table edge to clear the 0.039 m cut with table f_L-1_038. |
| f_L-1_042 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | The chair cuts the table by 0.038 m; moving the chair slightly away from the table edge (outwards) resolves the minor collision. |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred | - | - | front: faces the coffee table f_L-1_087 |
| f_L-1_050 | piece | armchair | r_L-1_salon_2 | inferred | - | - | front: faces the coffee table f_L-1_088 |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - | - | bathtub: r_L-1_banyo_2.bathroom_set (anchor f_L-1_052) misses shower\|bathtub, and the type's product range fits 1.83 x 0.80 m (the only missing member of that size); front: the free side facing the most room is the front |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L-1_055 in the twin room r_L-1_banyo_2 (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L-1_058 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | Qwen/Qwen3.8-27B-FP8 | Shift the floor lamp right along the wall (0.3 m) to clear the 0.06 m² overlap with lamp f_L-1_057. |
| f_L-1_059 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move floor lamp f_L-1_059 0.25 m away from the window to unblock the opening (G12). |
| f_L-1_060 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | Qwen/Qwen3.8-27B-FP8 | Snap the floor lamp's back to the left wall to clear the window band and the overlap with f_L-1_059. |
| f_L-1_061 | piece | table_coffee | r_L-1_salon | inferred | - | - | table_coffee: r_L-1_salon.seating (anchor f_L-1_053) misses table_coffee, and the type's product range fits 1.30 x 0.63 m (the only missing member of that size) |
| f_L-1_062 | piece | table_coffee | r_L-1_salon_2 | inferred | - | - | table_coffee: the same footprint (1.30 x 0.63 m) as f_L-1_061 in the twin room r_L-1_salon (mirrored centre within 0.02 m) |
| f_L-1_069 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_072 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai | size 0.56 x 0.56 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
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
| f_L-1_087 | piece | table_coffee | r_L-1_salon | inferred | - | - | type and front of f_L-1_088, its mirror twin in r_L-1_salon_2 (U16) |
| f_L-1b_002 | piece | unknown | r_L-1b_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | NR: the 5.14 x 2.37 m untyped cluster is a group of drawn pieces / zone outline, not a single piece of furniture. |
| f_L-1b_008 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_014 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_039 | piece | bar_stool | r_L-1b_salon_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_040 | piece | bar_stool | r_L-1b_salon | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_041 | piece | sofa | r_L-1b_salon_2 | inferred | - | - | sofa: the living room misses its seating anchor (sofa), and the type's product range fits 2.13 x 0.90 m (the only missing member of that size) |
| f_L-1b_042 | piece | sofa | r_L-1b_salon | inferred | - | - | sofa: the same footprint (2.13 x 0.90 m) as f_L-1b_041 in the twin room r_L-1b_salon_2 (mirrored centre within 0.02 m) |
| f_L-1b_043 | piece | bathtub | r_L-1b_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_055 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L-1b_044 | piece | bathtub | r_L-1b_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L-1b_043 in the twin room r_L-1b_banyo_2 (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L-1b_045 | piece | sofa | r_L-1b_salon_2 | inferred, adjusted_by_ai | - | code (reading.long_side_front) | a sofa faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: the long side facing the most room (5.83 m free); plan crop recognition/crops/sym_L-1b_007_ctx.png |
| f_L-1b_046 | piece | sofa | r_L-1b_salon | inferred, adjusted_by_ai | - | code (reading.long_side_front) | a sofa faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: the long side facing the most room (5.83 m free); plan crop recognition/crops/sym_L-1b_008_ctx.png |
| f_L-1b_047 | piece | potted_plant | r_L-1b_salon_2 | inferred | - | - | the two AI passes disagree (floor_lamp / potted_plant); both fit the drawn 0.59 x 0.59 m and the room: potted_plant, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L-1b_009_ctx.png |
| f_L-1b_048 | piece | floor_lamp | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_049 | piece | potted_plant | r_L-1b_salon | inferred | - | - | the two AI passes disagree (floor_lamp / potted_plant); both fit the drawn 0.59 x 0.59 m and the room: potted_plant, because the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; plan crop recognition/crops/sym_L-1b_011_ctx.png |
| f_L-1b_050 | piece | floor_lamp | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_051 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_052 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_053 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1b_053 away from f_L-1b_052 to resolve the 0.09 m² overlap (F9) and give it ≥0.81 m clearance behind (G6). |
| f_L-1b_054 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_055 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_056 | piece | chair | r_L-1b_salon | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1b_056 away from f_L-1b_055 to resolve the 0.09 m² overlap (F9) and give it ≥0.81 m clearance behind (G6). |
| f_L-1b_057 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_058 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_059 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1b_059 away from f_L-1b_058 to resolve overlap (F9) and clearance (G6) |
| f_L-1b_060 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.65 m -> 0.80 x 0.80 m | code (size_snap) | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_061 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | code (size_snap) | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_062 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size 0.71 x 0.45 m -> 0.50 x 0.50 m | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1b_062 away from f_L-1b_061 to resolve overlap (F9) and clearance (G6) |
| f_L-1b_065 | piece | unknown | r_L-1b_salon_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_066 | piece | unknown | r_L-1b_salon | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_067 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_068 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_069 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_070 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_003 | piece | washbasin | r_L0_banyo | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | washbasin rendered as a dresser/vanity; swap to a proper washbasin fixture model |
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_009 | piece | bed_double | r_L0_yatak_odasi_4 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_010 | piece | bed_double | r_L0_yatak_odasi_3 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_011 | piece | shower | r_L0_e_banyo | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_012 | piece | shower | r_L0_e_banyo_2 | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_016 | piece | toilet | r_L0_banyo | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | toilet model crude and low-poly; swap to a standard toilet model |
| f_L0_017 | piece | bed_double | r_L0_yatak_odasi | inferred | - | - | bed_double: the bedroom room misses its sleeping_double anchor (bed_double), and the type's product range fits 1.90 x 1.55 m (the only missing member of that size) |
| f_L0_018 | piece | bed_double | r_L0_yatak_odasi_2 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_017 in the twin room r_L0_yatak_odasi (mirrored centre within 0.02 m) |
| f_L0_019 | piece | wardrobe | r_L0_e_yatak_odasi | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 3.11 x 0.60 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_020 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - | - | wardrobe: the same footprint (3.11 x 0.60 m) as f_L0_019 in the twin room r_L0_e_yatak_odasi (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_021 | piece | bathtub | r_L0_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L0_022 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L0_021 in the twin room r_L0_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L0_023 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_039 stands in front; plan crop recognition/crops/sym_L0_007_ctx.png |
| f_L0_024 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_040 stands in front; plan crop recognition/crops/sym_L0_008_ctx.png |
| f_L0_025 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_041 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_026 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_042 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_027 | piece | wardrobe | r_L0_yatak_odasi_2 | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 2.09 x 0.60 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_028 | piece | wardrobe | r_L0_yatak_odasi | inferred | - | - | wardrobe: the same footprint (2.09 x 0.60 m) as f_L0_027 in the twin room r_L0_yatak_odasi_2 (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_029 | piece | wardrobe | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift wardrobe 0.29 m north off the window band to clear G12 |
| f_L0_030 | piece | wardrobe | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift wardrobe 0.29 m (under the 0.3 m drawn_lock cap) away from window win_L0_005 to clear the G12 blocked-opening finding. |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the nightstand 0.11 m away from the bed side to clear the 0.06 m² overlap (F9) and bring it to a positive gap ≤ 0.30 m from the bed side (G4). |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_017_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_018_ctx.png); then: Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. |
| f_L0_035 | piece | nightstand | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_009's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_019_ctx.png) |
| f_L0_036 | piece | nightstand | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_009's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_020_ctx.png); then: Shift nightstand 0.22 m away from the bed's right side to clear the 0.06 m² overlap and the 0.043 m cut with the bed. |
| f_L0_037 | piece | nightstand | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_010's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_021_ctx.png) |
| f_L0_038 | piece | nightstand | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_010's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_022_ctx.png); then: Shift nightstand 0.12 m away from the bed side to clear the 0.06 m² overlap (F9) and satisfy the ≤0.30 m gap (G4). |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_012, f_L1_015): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_011, f_L1_016): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_005 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_006 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_011 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the sofa 0.3 m up to clear the blocked free zone in front of it (F6, blocked by f_L1_010). |
| f_L1_012 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the sofa 0.3 m north to open the blocked free zone in front of it (F6, blocked by f_L1_009). |
| f_L1_015 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_009) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_012) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_016 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_015 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_017 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | The recognition crop shows a round table with two curved chairs around it, not a single 1.63x1.52 m object; the code's own passes already ruled out not_furniture and unknown, and no type fits the room, so it stays marked for review. |
| f_L1_018 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | The recognition crop shows an organic blob outline with two small arc marks (a landscape/plan symbol), not a furniture footprint; the untyped 1.63 x 1.52 m drawn piece is not furniture. |
| f_L1_019 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_020 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_019 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_021 | piece | table_coffee | r_L1_koridor | adjusted_by_ai | size 1.52 x 0.60 m -> 1.20 x 0.70 m | Qwen/Qwen3.8-27B-FP8 | Nudge the drawn table 0.08 m away from wall w_L1_005 so it no longer cuts the wall (S2) or reaches through the room outline (F9). |
| f_L1_022 | piece | chair | r_L1_teras | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move the drawn chair slightly inward away from wall w_L1_009 to clear the 0.05 m wall cut and the 0.12 m outline protrusion. |
| f_L1_024 | piece | table_coffee | r_L1_koridor_2 | adjusted_by_ai | size 1.52 x 0.60 m -> 1.20 x 0.70 m | Qwen/Qwen3.8-27B-FP8 | Move table 0.1m in -y to clear wall w_L1_006 and room outline collision. |
| f_L1_025 | piece | chair | r_L1_koridor_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Rotate chair to face 0 degrees (+x direction) towards the table at x=13.61 to satisfy the group orientation check. |
| f_L1_027 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_028 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_027 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_010_ctx.png |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | bring armchair within 2.5 m of the coffee table to clear G3 (plan crop recognition/crops/sym_L1_011_ctx.png) |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_012_ctx.png |
| f_L1_031 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_032 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_033 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x975ffc83_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_034 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (bookshelf / console_table); both fit the drawn 1.09 x 0.40 m and the room: bookshelf, because the room misses it (the living room's living_storage group has no sideboard or bookshelf); plan crop recognition/crops/sym_L1_x6881d71b_ctx.png; front: its back stands on the only side on a wall |
| f_L1_035 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_036 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (bookshelf / console_table); both fit the drawn 1.09 x 0.40 m and the room: bookshelf, because the AI passes of its twin f_L1_034 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png; front: its back stands on the only side on a wall |
| f_L0_039 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_023, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_007_ctx.png) |
| f_L0_040 | piece | office_chair | r_L0_yatak_odasi_3 | inferred | - | - | the chair of the desk f_L0_024, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_008_ctx.png) |
| f_L0_041 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_025, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_042 | piece | office_chair | r_L0_yatak_odasi | inferred | - | - | the chair of the desk f_L0_026, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L-1_090 | piece | fridge | r_L-1_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the mirror-like reflective fridge model with a standard classic fridge model to fix the physically incorrect reflective surface (v:r1-v2:1). |
| f_L1_048 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Slide the bookshelf 1 m south along the west wall, out of the sloped-ceiling zone (ceiling 0.82 m at its current spot), to clear both X2 findings. |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_mutfak_1 | ![](agent/r1_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_1_after.jpg) |
| 1 | cam_r_L-1_mutfak_2 | ![](agent/r1_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_2_after.jpg) |
| 1 | cam_r_L-1_mutfak_3 | ![](agent/r1_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_3_after.jpg) |
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_banyo_2 | ![](agent/r1_cam_r_L0_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_banyo_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 1 | cam_r_L1_koridor_1 | ![](agent/r1_cam_r_L1_koridor_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_1_after.jpg) |
| 1 | cam_r_L1_koridor_2 | ![](agent/r1_cam_r_L1_koridor_2_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_after.jpg) |
| 1 | cam_r_L1_koridor_3 | ![](agent/r1_cam_r_L1_koridor_3_before.jpg) | ![](agent/r1_cam_r_L1_koridor_3_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 1 | cam_r_L1_teras_2 | ![](agent/r1_cam_r_L1_teras_2_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_after.jpg) |
| 1 | cam_r_L1_teras_2_1 | ![](agent/r1_cam_r_L1_teras_2_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_1_after.jpg) |
| 1 | cam_r_L1_teras_2_2 | ![](agent/r1_cam_r_L1_teras_2_2_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_2_after.jpg) |
| 1 | cam_r_L1_teras_2_3 | ![](agent/r1_cam_r_L1_teras_2_3_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_3_after.jpg) |
| 1 | cam_r_L1_teras_3 | ![](agent/r1_cam_r_L1_teras_3_before.jpg) | ![](agent/r1_cam_r_L1_teras_3_after.jpg) |
| 1 | ext_1 | ![](agent/r1_ext_1_before.jpg) | ![](agent/r1_ext_1_after.jpg) |
| 1 | ext_2 | ![](agent/r1_ext_2_before.jpg) | ![](agent/r1_ext_2_after.jpg) |
| 1 | ext_3 | ![](agent/r1_ext_3_before.jpg) | ![](agent/r1_ext_3_after.jpg) |
| 1 | ext_5 | ![](agent/r1_ext_5_before.jpg) | ![](agent/r1_ext_5_after.jpg) |
| 1 | ext_7 | ![](agent/r1_ext_7_before.jpg) | ![](agent/r1_ext_7_after.jpg) |
| 2 | cam_r_L-1_salon_1 | ![](agent/r2_cam_r_L-1_salon_1_before.jpg) | ![](agent/r2_cam_r_L-1_salon_1_after.jpg) |
| 2 | cam_r_L-1_salon_2 | ![](agent/r2_cam_r_L-1_salon_2_before.jpg) | ![](agent/r2_cam_r_L-1_salon_2_after.jpg) |
| 2 | cam_r_L-1_salon_3 | ![](agent/r2_cam_r_L-1_salon_3_before.jpg) | ![](agent/r2_cam_r_L-1_salon_3_after.jpg) |
| 2 | cam_r_L1_koridor_2_1 | ![](agent/r2_cam_r_L1_koridor_2_1_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_1_after.jpg) |
| 2 | cam_r_L1_koridor_2_2 | ![](agent/r2_cam_r_L1_koridor_2_2_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_2_after.jpg) |
| 2 | cam_r_L1_koridor_2_3 | ![](agent/r2_cam_r_L1_koridor_2_3_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_3_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_5 | ![](agent/r2_ext_5_before.jpg) | ![](agent/r2_ext_5_after.jpg) |
| 2 | ext_7 | ![](agent/r2_ext_7_before.jpg) | ![](agent/r2_ext_7_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 3 | ext_front_entrance | - | ![](agent/r3_ext_front_entrance_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

None.
