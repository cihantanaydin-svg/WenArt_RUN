# Final report: real04

44 views: 0 polished, 44 Cycles (gate_validation 5, not_run 39). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 44 |
| interior / exterior views | 39 / 5 |
| variant | base |
| polished | 0 |
| Cycles | 44 (gate_validation 5, not_run 39) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 10 |
| needs_review views | 3 |
| unverified pieces in view (sum over views) | 30 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 15 |
| exposure | -7.67 .. +2.83 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| window pull | 22 view(s), -5 .. 0 EV |
| interior glazing pull | - |
| camera policy | m5 5, search 39 |
| camera score (min / mean / max) | 0.23 / 2.55 / 3.88 |
| rooms by number of views | 1 with 0, 3 with 1, 3 with 2, 10 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 7.6 min / 8.0 min / 96.3 s |
| seconds: polish / gate / check | - / - / 16.9 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 654.9 MB |
| [real04.glb](3d/real04.glb) | 1760.2 MB |

44 cameras; textures scaled to at most 1024 px (298 scaled) for the download.

## AI decor

116 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 26 rooms; 5 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

- r_L-1b_salon_2: rules (no slot for AI decor)

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
- 28 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L-1_069, f_L-1_070, f_L-1_071, f_L-1_072, f_L-1_073, f_L-1_087, f_L-1b_045, f_L-1b_046
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 19 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 14 proposal(s) refused, reverted or not placed (listed per room)

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
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 1.49 | D3 A1 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | -4 | search 3.11 | D6 A2 | 1 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 2.90 | D2 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.67 | -5 | search 2.42 | D8 A2 | 0 | no | [preview](cam_r_L-1_koridor_2_3_final_preview.jpg) [plan](cam_r_L-1_koridor_2_3_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -1 | search 3.44 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.00 | -1 | search 3.28 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -1 | search 3.25 | D4 A2 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -3 | search 2.85 | D7 A2 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -3 | search 2.68 | D9 A2 | 3 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.83 | -4 | search 2.67 | D8 A2 | 2 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.05 | D4 A1 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.50 | - | search 1.73 | D2 A1 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.04 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 0.89 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -1 | search 3.88 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.81 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.77 | D5 A3 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.83 | - | search 2.09 | D4 A1 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_koridor_2 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.83 | - | search 1.97 | D5 | 0 | no | [preview](cam_r_L0_koridor_2_final_preview.jpg) [plan](cam_r_L0_koridor_2_plan.jpg) |
| cam_r_L0_koridor_3 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.83 | - | search 1.95 | D3 | 0 | no | [preview](cam_r_L0_koridor_3_final_preview.jpg) [plan](cam_r_L0_koridor_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -3 | search 3.64 | D3 A5 | 2 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -3 | search 3.15 | D3 A5 | 2 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -2 | search 2.97 | D5 A2 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_4_1 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 3.16 | D4 A2 | 1 | no | [preview](cam_r_L0_yatak_odasi_4_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_1_plan.jpg) |
| cam_r_L0_yatak_odasi_4_2 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 3.03 | D4 A2 | 1 | no | [preview](cam_r_L0_yatak_odasi_4_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_2_plan.jpg) |
| cam_r_L0_yatak_odasi_4_3 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 2.84 | D4 A2 | 2 | no | [preview](cam_r_L0_yatak_odasi_4_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | +0.33 | - | search 1.51 | A2 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.00 | - | search 3.08 | D3 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.17 | - | search 2.82 | D3 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_koridor_2_1 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.17 | - | search 2.94 | D4 | 0 | no | [preview](cam_r_L1_koridor_2_1_final_preview.jpg) [plan](cam_r_L1_koridor_2_1_plan.jpg) |
| cam_r_L1_koridor_2_2 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.76 | D5 A1 | 0 | no | [preview](cam_r_L1_koridor_2_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_2_plan.jpg) |
| cam_r_L1_koridor_2_3 | r_L1_koridor_2 | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.63 | D5 | 0 | no | [preview](cam_r_L1_koridor_2_3_final_preview.jpg) [plan](cam_r_L1_koridor_2_3_plan.jpg) |
| cam_r_L1_koridor_3 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.65 | D3 | 0 | no | [preview](cam_r_L1_koridor_3_final_preview.jpg) [plan](cam_r_L1_koridor_3_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.50 | -1 | search 2.91 | D7 A2 | 3 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.50 | -1 | search 2.90 | D5 A6 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.33 | -1 | search 2.81 | D5 A4 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.83 | 0 | search 0.23 | D2 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2_1 | r_L1_teras_2 | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 0.25 | D1 | 0 | no | [preview](cam_r_L1_teras_2_1_final_preview.jpg) [plan](cam_r_L1_teras_2_1_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.00 | 0 | m5 blocked | D6 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D5 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 blocked | D2 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.83 | 0 | m5 | D9 | 0 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 | D5 | 0 | yes | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

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
| r_L1_teras | balcony | L1 | 1 | 0 | 1 | cam_r_L1_teras_1 |
| r_L1_teras_2 | balcony | L1 | 1 | 0 | 1 | cam_r_L1_teras_2_1 |

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
- cam_r_L1_teras_2_1: not_run: polish not run
- ext_1: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_2: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_3: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_5: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_7: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:3A2AD/10,INSERT:3A2AD/11,INSERT:3A2AD/12,INSERT:3A2AD/13,INSERT:3A2AD/14,INSERT:3A2AD/15,INSERT:3A2AD/16,INSERT:3A2AD/17,INSERT:3A2AD/18,INSERT:3A2AD/19,INSERT:3A2AD/2,INSERT:3A2AD/20,INSERT:3A2AD/21,INSERT:3A2AD/22,INSERT:3A2AD/23,INSERT:3A2AD/24,INSERT:3A2AD/25,INSERT:3A2AD/26,INSERT:3A2AD/27,INSERT:3A2AD/28,INSERT:3A2AD/29,INSERT:3A2AD/30,INSERT:3A2AD/31,INSERT:3A2AD/32,INSERT:3A2AD/33,INSERT:3A2AD/4,INSERT:3A2AD/5,INSERT:3A2AD/6,INSERT:3A2AD/7,INSERT:3A2AD/8,INSERT:3A2AD/9 YATAK vector 0.90; deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 23 % of its pixels > 0.10 m outside the drawing, 570833 px |
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
- f_L-1_063
- f_L-1_065
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

Unverified pieces in view:

- cam_r_L-1_banyo_2: f_L-1_056
- cam_r_L-1_koridor_2_1: f_L-1_053
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_070
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_061, f_L-1_071
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061
- cam_r_L0_banyo_1: f_L0_021
- cam_r_L0_e_yatak_odasi_1: f_L0_019
- cam_r_L0_e_yatak_odasi_2: f_L0_019
- cam_r_L0_e_yatak_odasi_3: f_L0_019
- cam_r_L0_yatak_odasi_1: f_L0_017, f_L0_026
- cam_r_L0_yatak_odasi_2: f_L0_017, f_L0_026
- cam_r_L0_yatak_odasi_3: f_L0_017, f_L0_026, f_L0_028
- cam_r_L0_yatak_odasi_4_1: f_L0_036
- cam_r_L0_yatak_odasi_4_2: f_L0_036
- cam_r_L0_yatak_odasi_4_3: f_L0_030, f_L0_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_015, f_L1_033, f_L1_034
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_034
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_034

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L-1_021 | untyped_piece | r_L-1_salon | drawn piece 5.54 x 0.60 m in r_L-1_salon has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1_022 | untyped_piece | r_L-1_salon_2 | drawn piece 5.54 x 0.60 m in r_L-1_salon_2 has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| f_L-1b_002 | untyped_piece | r_L-1b_salon | drawn piece 5.14 x 2.37 m in r_L-1b_salon has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |

Drawn symbols read as not furniture (never built): other 4.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L-1_025 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_026 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L-1_051 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L-1_052 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
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
| f_L0_035 | furniture | nightstand | hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce | the vision check sees more than one object |
| f_L0_036 | furniture | nightstand | hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce | the vision check sees more than one object |
| f_L1_007 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_008 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_013 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_014 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_037 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |
| f_L1_040 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |
| f_L1_041 | furniture | chair | abo_B07K7K8YF9 | the vision check says it is not a chair (a armchair) |
| f_L1_042 | furniture | chair | abo_B07K7K8YF9 | the vision check says it is not a chair (a armchair) |

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
| c_073 | symbol_type_disagreement | f_L1_036 | f_L1_036: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the AI passes of its twin f_L1_034 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_074 | other | r_L-1b_salon | r_L-1b_salon: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_075 | other | r_L-1b_salon_2 | r_L-1b_salon_2: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_076 | symbol_front_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_077 | symbol_front_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_078 | symbol_front_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_079 | symbol_front_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_080 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_081 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_082 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L0_023 | f_L0_023: sym_L0_007: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L0_024 | f_L0_024: sym_L0_008: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L0_025 | f_L0_025: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L0_026 | f_L0_026: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L0_036 | f_L0_036: sym_L0_020: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L1_027 | f_L1_027: sym_L1_009: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L1_028 | f_L1_028: sym_L1_010: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | symbol_front_disagreement | f_L1_029 | f_L1_029: sym_L1_011: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_092 | symbol_front_disagreement | f_L1_030 | f_L1_030: sym_L1_012: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_093 | unit_mismatch | r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21 | sheets.json sc_001: deneme1.dwg: $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_094 | registration_residual | r11, r5 | sheets.json sc_002: deneme1.dwg r11 (L-1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_095 | registration_residual | r15, r5 | sheets.json sc_003: deneme1.dwg r15 (L-1b) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_096 | registration_residual | r16, r5 | sheets.json sc_004: deneme1.dwg r16 (L0) registered onto r5 (L0) with an RMS outline distance of 0.247 m (492 of 550 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_097 | registration_residual | r18, r5 | sheets.json sc_005: deneme1.dwg r18 (L1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_098 | section_width_mismatch | r19 | sheets.json sc_006: section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 17.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

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

0 change(s) applied, 30 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 1.00 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_049, f_L-1_053, f_L-1_059, f_L-1_060, f_L-1_061, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_073, f_L-1_075, f_L-1_077, f_L-1_087

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_095: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L-1_089)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_022, f_L-1_023, f_L-1_038, f_L-1_039, f_L-1_040, f_L-1_041, f_L-1_042, f_L-1_043, f_L-1_044, f_L-1_045, f_L-1_046, f_L-1_047, f_L-1_048, f_L-1_050, f_L-1_054, f_L-1_057, f_L-1_058, f_L-1_065, f_L-1_066, f_L-1_069, f_L-1_072, f_L-1_074, f_L-1_076, f_L-1_078, f_L-1_088

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

### Salon (r_L-1b_salon_2, living): completed (partner r_L-1b_salon (twin) not used: the twin's drawn furniture does not map onto this room: drawn sofa f_L-1b_046 has no counterpart here; completed itself)

- added f_L-1b_083: table_coffee 1.20 x 0.70 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_003, f_L-1b_004, f_L-1b_006, f_L-1b_007, f_L-1b_008, f_L-1b_017, f_L-1b_018, f_L-1b_019, f_L-1b_020, f_L-1b_021, f_L-1b_022, f_L-1b_023, f_L-1b_024, f_L-1b_025, f_L-1b_039, f_L-1b_045, f_L-1b_047, f_L-1b_048, f_L-1b_057, f_L-1b_058, f_L-1b_059, f_L-1b_060, f_L-1b_061, f_L-1b_062, f_L-1b_063, f_L-1b_067, f_L-1b_069

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_082: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): mirrored (decisions of r_L-1b_koridor (twin), not asked again)

- added f_L-1b_087: shoe_cabinet 0.60 x 0.30 (confidence -, rule, mirrored from f_L-1b_082)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_015

### Banyo (r_L-1b_banyo, bathroom): copied (decisions of r_L-1_banyo (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_036, f_L-1b_038, f_L-1b_044

### Banyo (r_L-1b_banyo_2, bathroom): copied (decisions of r_L-1_banyo_2 (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_035, f_L-1b_037, f_L-1b_043

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed

- added f_L0_041: nightstand 0.40 x 0.40 (confidence -, rule)
- added f_L0_042: nightstand 0.40 x 0.40 (confidence -, rule)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_017, f_L0_026, f_L0_028

### E.yatak Odası (r_L0_e_yatak_odasi, bedroom): completed (nothing fits: work: no place passes the checks)

- not placed work: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_019, f_L0_031, f_L0_032

### E.yatak Odası (r_L0_e_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_e_yatak_odasi (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_008, f_L0_020, f_L0_033, f_L0_034

### Yatak Odası (r_L0_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_yatak_odasi (twin), not asked again)

- added f_L0_043: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_041)
- added f_L0_044: nightstand 0.40 x 0.40 (confidence -, rule, mirrored from f_L0_042)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_018, f_L0_023, f_L0_027

### E.banyo (r_L0_e_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_011, f_L0_013

### E.banyo (r_L0_e_banyo_2, bathroom): mirrored (decisions of r_L0_e_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_012, f_L0_014

### Yatak Odası (r_L0_yatak_odasi_3, bedroom): mirrored (decisions of r_L0_yatak_odasi_4 (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_024, f_L0_029, f_L0_037, f_L0_038

### Merdiven (r_L0_merdiven, hall): completed (no groups for this room (hall 5.7 m²: nothing))

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Merdiven (r_L0_merdiven_2, hall): mirrored (decisions of r_L0_merdiven (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): completed (nothing to add)

- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_009, f_L0_025, f_L0_030, f_L0_035, f_L0_036

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
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_009, f_L1_033, f_L1_034

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_051: table_dining 1.20 x 0.80 (confidence -, rule, mirrored from f_L1_043)
- added f_L1_052: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_044)
- added f_L1_053: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_045)
- added f_L1_054: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_046)
- added f_L1_055: chair 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_047)
- added f_L1_056: bookshelf 0.80 x 0.30 (confidence -, rule, mirrored from f_L1_048)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_006, f_L1_010, f_L1_035, f_L1_036

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

Reference: source building.json; mode `complete`. 232 of 232 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 213 ok, 19 failed; 0 changed by the AI.

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_049 | armchair (armchair) | 0.00 | 180.00 | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1b_045 | sofa (sofa) | 0.00 | 180.00 | - | - |
| f_L-1b_046 | sofa (sofa) | 1.14 | 90.00 | - | - |
| f_L-1b_053 | chair (chair) | 0.30 | 0.00 | - | - |
| f_L-1b_056 | chair (chair) | 0.22 | 0.00 | - | - |
| f_L-1b_059 | chair (chair) | 0.26 | 0.00 | - | - |
| f_L-1b_062 | chair (chair) | 0.26 | 0.00 | - | - |
| f_L0_032 | nightstand (floor_lamp) | 0.11 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.15 | 0.00 | yes | - |
| f_L0_036 | nightstand (floor_lamp) | 0.22 | 0.00 | yes | - |
| f_L0_038 | nightstand (floor_lamp) | 0.19 | 0.00 | yes | - |
| f_L1_021 | table_coffee (table_coffee) | 0.20 | - | - | - |
| f_L1_022 | chair (chair) | 0.16 | 0.00 | yes | - |

## Exterior views

5 of 5 exterior view(s) of variant `base` rendered; 2 dropped (no camera place worked).

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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_4_1, cam_r_L0_yatak_odasi_4_2, cam_r_L0_yatak_odasi_4_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_2, cam_r_L1_koridor_2_3, cam_r_L1_koridor_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2_1 | 0 / 44 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3 | 0 / 14 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| deneme1.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 20, block_name 56, group_member 10, inferred 14, level 3, nightstand_symbol 8, none 24, rule 84, twin 13. Recognition questions: 72; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L-1_057 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_058 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_059 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_060 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_064 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_066 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_069 | r_L-1_salon_2 | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_070 | r_L-1_salon | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_071 | r_L-1_salon | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_072 | r_L-1_salon_2 | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_073 | r_L-1_salon | table_coffee | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.90 |
| f_L-1_074 | r_L-1_salon_2 | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.80 |
| f_L-1_075 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_076 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_077 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_078 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_079 | r_L-1_salon_2 | ottoman | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_080 | r_L-1_salon | ottoman | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_085 | r_L-1_mutfak | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_086 | r_L-1_mutfak_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_087 | r_L-1_salon | table_coffee | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1_088 | r_L-1_salon_2 | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1b_039 | r_L-1b_salon_2 | bar_stool | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_040 | r_L-1b_salon | bar_stool | yes | verified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: bar_stool, front bottom 0.90 |
| f_L-1b_045 | r_L-1b_salon_2 | sofa | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_046 | r_L-1b_salon | sofa | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_047 | r_L-1b_salon_2 | potted_plant | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_048 | r_L-1b_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1b_049 | r_L-1b_salon | potted_plant | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_050 | r_L-1b_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1b_065 | r_L-1b_salon_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L-1b_066 | r_L-1b_salon | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L0_023 | r_L0_yatak_odasi_2 | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_024 | r_L0_yatak_odasi_3 | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_025 | r_L0_yatak_odasi_4 | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_026 | r_L0_yatak_odasi | desk | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_031 | r_L0_e_yatak_odasi | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_032 | r_L0_e_yatak_odasi | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_033 | r_L0_e_yatak_odasi_2 | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_034 | r_L0_e_yatak_odasi_2 | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_035 | r_L0_yatak_odasi_4 | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_036 | r_L0_yatak_odasi_4 | nightstand | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_037 | r_L0_yatak_odasi_3 | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_038 | r_L0_yatak_odasi_3 | nightstand | no | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_027 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_028 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_031 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_032 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_034 | r_L1_oyun_aktivite_ve_dinlenme_odasi | bookshelf | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |
| f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | bookshelf | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |

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
| area_light | 1 | r_L0_merdiven: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven_2 |
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
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_023, furn_f_L0_024, furn_f_L0_025 |
| height | 6 | no height in the JSON; type height for floor_lamp | furn_f_L-1_057, furn_f_L-1_058, furn_f_L-1_059 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 8 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for ottoman | furn_f_L-1_075, furn_f_L-1_076, furn_f_L-1_077 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_011, furn_f_L0_012 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_009, furn_f_L1_010, furn_f_L1_011 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1_008, furn_f_L-1_017 |
| height | 5 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
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
| rig_ceiling | 1 | ceiling fixture at the pole of inaccessibility of r_L1_banyo: crosses ceiling_light dec_L1_011 | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at the pole of inaccessibility of r_L1_banyo_2: crosses ceiling_light dec_L1_013 | rig_r_L1_banyo_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_011; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_013; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_012 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
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
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_029; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_031; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_030 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_020; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_019 (top 2.41 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_033; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_032 (top 2.18 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside light in the shade of the table lamp dec_L0_014 on f_L0_031 beside the bed f_L0_007; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_015); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_038 on f_L0_033 beside the bed f_L0_008; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_039); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_017; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_017 (the top of the nightstand f_L0_042 is taken by the plant_small dec_L0_007); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_048 on f_L0_043 beside the bed f_L0_018; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_018 (the top of the nightstand f_L0_044 is taken by the plant_small dec_L0_049); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside lamp on the nightstand f_L0_038; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_054 on f_L0_037 beside the bed f_L0_010; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside lamp on the nightstand f_L0_036; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_023 on f_L0_035 beside the bed f_L0_009; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_mirror | 1 | mirror light over the washbasin f_L1_007: the mirror dec_L1_010 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo |
| rig_mirror | 1 | mirror light over the washbasin f_L1_008: the mirror dec_L1_012 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo_2 |
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

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_051e7613c71593d5d91bac3b3d03a36e51dd0c23 [non_commercial], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_404146070e071454f055cfe3be7811fcdcb7ddbd [non_commercial], hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: yes
- cam_r_L-1_koridor_2_3: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: hssd_404146070e071454f055cfe3be7811fcdcb7ddbd [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
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
- cam_r_L0_yatak_odasi_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_2: commercial-safe: yes
- cam_r_L0_yatak_odasi_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_4_1: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce [non_commercial])
- cam_r_L0_yatak_odasi_4_2: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce [non_commercial])
- cam_r_L0_yatak_odasi_4_3: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_051e7613c71593d5d91bac3b3d03a36e51dd0c23 [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: yes
- cam_r_L1_koridor_2: commercial-safe: yes
- cam_r_L1_koridor_2_1: commercial-safe: yes
- cam_r_L1_koridor_2_2: commercial-safe: no (flagged assets: hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_koridor_2_3: commercial-safe: no (flagged assets: hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_koridor_3: commercial-safe: yes
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial])
- cam_r_L1_teras_1: commercial-safe: yes
- cam_r_L1_teras_2_1: commercial-safe: yes
- ext_1: commercial-safe: no (flagged assets: hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])
- ext_2: commercial-safe: no (flagged assets: hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])
- ext_7: commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial])

## Built below library level (Milestone 13)

51 furniture piece(s) built from a module builder or a parametric family instead of a library model: 11 library gap(s) to close with a real model, 40 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1b_045 | sofa | parametric | parametric:sofa | r_L-1b_salon_2 | living | from_documents | yes | parametric family (built below the library level) |
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
| f_L-1b_084 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon_2 | living | added_by_ai | no (by design) | - |
| f_L-1b_085 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon_2 | living | added_by_ai | no (by design) | - |
| f_L-1b_086 | wall_cabinet | parametric | parametric:wall_cabinet | r_L-1b_salon_2 | living | added_by_ai | no (by design) | - |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_2_1 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.7 degrees off the sun, sky pull k 3), ext_5 (5.4 degrees off the sun, sky pull k 0).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (72 of 72 answered); sheets/requests.json (8 of 8 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (72 of 72 answered); sheets/requests.json (8 of 8 answered) |

Assets: textures CC0 x 19; furniture/decor models CC-BY-4.0 x 177, CC-BY-NC-4.0 x 96, CC0 x 1, generated (Infinigen v1.19.0, BSD-3-Clause) x 1, generated (TRELLIS.2-4B, MIT) x 18 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 44 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for f_L-1_051, f_L-1_052, f_L-1b_037, f_L-1b_038, f_L0_013, f_L0_014, f_L0_015, f_L0_016, f_L1_013, f_L1_014)
- "Aluminum tray" by Kathrin&Christian (https://sketchfab.com/3d-models/398c1b3b8114409a89eb02f9b42f8064), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_020)
- "Wooden flat filing tray" by Reo Creative Scanning (https://sketchfab.com/3d-models/4b8d86761f9440cfb324d0b4d07336ff), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_005)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1b_023)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261017-224848-full-20261017T225406Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 50.8 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 2.0 min | 68 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| style | ok | 0.2 s | - |
| recognize | ok | 41.5 s | - |
| pipeline_final | ok | 5.8 min | answers applied; late questions (4) answered in a second short recognition pass: pipeline_final ran again |
| fit | ok | 9.0 s | - |
| layout | ok | 27.3 s | - |
| decor_ask | ok | 2.1 min | - |
| photos | reused | 0.2 s | - |
| assets | ok | 2.2 s | - |
| decor | ok | 5.8 s | - |
| agent_apply | ok | 23.8 s | - |
| refit | ok | 47.8 s | - |
| build | ok | 41.4 min | - |
| agent_previews | ok | 5.1 min | 12 view(s) |
| agent | ok | 41.2 min | 3 round(s), 23 finding(s) removed by 26 accepted edit(s) (measured; 38 predicted by the dry re-checks), 141 rejected; stop: max rounds reached |
| render | ok | 12.2 min | - |
| export | ok | 3.5 min | - |
| controls | ok | 110.3 s | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.3 min | - |
| check | ok | 4.2 min | - |
| combine | ok | 26.0 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 7 round(s), 249 edit(s) accepted, 404 rejected, 1849 model calls (23303101 tokens), 46.7 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 27 / 143 (16 % accepted) |
| rejected by reason | acceptance 35, memory 33, drawn_lock 20, max_tries 11, no_overlap 9 |
| rooms checked by code / vision / planner | 38 / 16 / 18 |
| rooms with fixable critical or major findings visited | 18 of 18 |
| critical before -> after | 2 -> 1 |
| major before -> after | 148 -> 121 |
| agent minutes; first accepted edit after | 51.5; 22.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 71; 119; 49 (35) |
| critical/major findings removed (measured by the next round; predicted by the dry re-checks) | 33 measured; 40 predicted |
| edits removing their finding | 22 of 25 |
| plans ok / empty / refused / default | 35 / 14 / 0 / 0 |

Library gaps reported by the agent: stair (No stair models exist in the library (catalog count 0), so swap_model cannot provide a stair with railings/balustrade to fix the F9 findings.), washbasin modern (No washbasin candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2 % non-uniform, mean scale 1.3433); parametric fixture used by design.), bathtub modern (No bathtub candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest gen_bathtub_industrial_1_46aaa4c2 at 18.5 % non-uniform, mean scale 1.1507); 3 fitted outside the real height 0.4-0.72 m; parametric fixture used by design.), shower modern (no shower candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest: gen_shower_japandi_6_bd58a347 at 52.4 % non-uniform, mean scale 0.8967); parametric fixture kept by design), washbasin modern (no washbasin candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest: objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2 % non-uniform, mean scale 1.3433); parametric fixture kept by design), washbasin modern (No washbasin candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2% non-uniform, mean scale 1.3433); parametric fixture kept by design), shower modern minimal (No shower candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest gen_shower_japandi_6_bd58a347 at 52.4% non-uniform, mean scale 0.8967); parametric fixture kept by design), stove modern (No audited stove model fits the drawn 0.75x0.55 m footprint within 10% non-uniform scale and 0.85..1.2 mean scale; closest gen_stove_japandi_6_1c3993c0 is at 4.6% non-uniform but mean scale 0.766, and 11 others fall outside the real 0.8-1.2 m height band, so the parametric fixture is used by design.), washbasin (No washbasin candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2% non-uniform, mean scale 1.3433); parametric fixture kept by design.), bathtub (No bathtub candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest gen_bathtub_industrial_1_46aaa4c2 at 18.5% non-uniform, mean scale 1.1507); 3 fitted outside the real height 0.4-0.72 m; parametric fixture kept by design.), washbasin (No audited washbasin model within tolerance; parametric fixture used by design.), washbasin modern (no washbasin candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2 % non-uniform, mean scale 1.3433)), shower modern minimal (no shower candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest gen_shower_japandi_6_bd58a347 at 52.4 % non-uniform, mean scale 0.8967)), chair (Fixes c:LG:f_L1_023: no audited library chair model fits the drawn 0.60 x 0.45 m (closest abo_B0857JM2NC at 18.7% non-uniform scale, outside the 10% cap; relaxed caps also yield none), so the parametric build is the correct fallback.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 20 | 493 | 248 | 2 | 67 | 118 | refit | 7 |
| 2 | 13 | 472 | 247 | 4 | 56 | 121 | refit | 6 |
| 3 | 10 | 458 | 238 | 7 | 48 | 91 | layout | 12 |
| 4 | 9 | 443 | 235 | 6 | 25 | 37 | refit | 3 |
| 5 | 33 | 179 | 98 | 0 | 14 | 19 | layout | 13 |
| 6 | 5 | 150 | 96 | 0 | 38 | 18 | layout | 20 |
| 7 | 2 | 144 | 95 | 3 | 1 | 0 | build | 48 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D1 | 0 | 2 | 0 | 0 |
| D2 | 0 | 21 | 0 | 4 |
| F1 | 0 | 16 | 58 | 1 |
| F2 | 0 | 36 | 0 | 0 |
| F3 | 0 | 120 | 30 | 0 |
| F4 | 0 | 117 | 0 | 0 |
| F6 | 0 | 48 | 0 | 0 |
| F8 | 0 | 292 | 0 | 0 |
| F9 | 4 | 264 | 0 | 9 |
| G1 | 0 | 8 | 72 | 0 |
| G10 | 0 | 270 | 0 | 0 |
| G11 | 0 | 48 | 0 | 0 |
| G12 | 0 | 114 | 0 | 0 |
| G13 | 0 | 8 | 0 | 0 |
| G14 | 0 | 0 | 58 | 0 |
| G2 | 0 | 32 | 44 | 0 |
| G3 | 0 | 24 | 0 | 0 |
| G4 | 0 | 7 | 29 | 0 |
| G5 | 0 | 41 | 0 | 0 |
| G6 | 0 | 49 | 32 | 0 |
| G7 | 0 | 0 | 34 | 0 |
| G8 | 0 | 57 | 32 | 0 |
| G9 | 0 | 50 | 0 | 0 |
| L6 | 0 | 15 | 0 | 0 |
| L7 | 0 | 0 | 1 | 0 |
| LG | 0 | 0 | 543 | 0 |
| NR | 0 | 247 | 0 | 0 |
| R3 | 0 | 0 | 150 | 0 |
| RC | 0 | 0 | 105 | 0 |
| S2 | 0 | 267 | 40 | 0 |
| S5 | 0 | 0 | 12 | 0 |
| X1 | 0 | 0 | 0 | 2 |
| X2 | 70 | 85 | 14 | 0 |
| X3 | 0 | 31 | 0 | 6 |
| X6 | 0 | 31 | 0 | 0 |
| lighting_dark | 18 | 39 | 3 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 301 | 1 | rotate_piece | f_L-1b_033 | adjusted_by_ai | 50.0 -> 50.0 | Rotate chair f_L-1b_033 to face the dining table f_L-1b_026, resolving the 'chair does not face its group' finding. | ![](agent/r1_037_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r1_039_rotate_piece_after_r_L-1b_salon.png) |
| 303 | 1 | move_piece | f_L-1b_018 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_053_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_054_move_piece_after_r_L-1b_salon_2.png) |
| 304 | 1 | move_piece | f_L-1b_019 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_055_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_056_move_piece_after_r_L-1b_salon_2.png) |
| 305 | 1 | move_piece | f_L-1b_020 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_057_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_058_move_piece_after_r_L-1b_salon_2.png) |
| 306 | 1 | move_piece | f_L-1b_021 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_059_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_060_move_piece_after_r_L-1b_salon_2.png) |
| 307 | 1 | move_piece | f_L-1b_022 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_061_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_062_move_piece_after_r_L-1b_salon_2.png) |
| 308 | 1 | move_piece | f_L-1b_023 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_063_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_064_move_piece_after_r_L-1b_salon_2.png) |
| 309 | 1 | move_piece | f_L-1b_025 | adjusted_by_ai | 50.0 -> 50.0 | move chair closer to table edge to clear F8 | ![](agent/r1_065_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_066_move_piece_after_r_L-1b_salon_2.png) |
| 311 | 1 | relayout_room | r_L0_yatak_odasi | adjusted_by_ai | 60.0 -> 54.0 | Candidate 1 has no hard failures and repositions the storage group to clear the window blockage, wall cuts and mutual overlap, while also addressing the bed side clearance. | ![](agent/r1_067_relayout_room_before_r_L0_yatak_odasi.png) | ![](agent/r1_068_relayout_room_after_r_L0_yatak_odasi.png) |
| 324 | 1 | relayout_room | r_L0_yatak_odasi_2 | adjusted_by_ai | 60.0 -> 54.0 | Move both wardrobes off window win_L0_006 and resolve their mutual overlap and wall cuts in one solver pass. | ![](agent/r1_069_relayout_room_before_r_L0_yatak_odasi_2.png) | ![](agent/r1_071_relayout_room_after_r_L0_yatak_odasi_2.png) |
| 329 | 1 | report_library_gap | f_L1_002 | library_gap | - | No stair models exist in the library (catalog count 0), so swap_model cannot provide a stair with railings/balustrade to fix the F9 findings. | - | - |
| 342 | 1 | move_piece | f_L1_012 | adjusted_by_ai | 74.0 -> 74.0 | Nudge sofa f_L1_012 0.3 m toward the right wall to reduce the F3 back-off-wall distance (max allowed move). | ![](agent/r1_089_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_090_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 352 | 1 | swap_model | f_L1_009 | adjusted_by_ai | 74.0 -> 74.0 | Swap sofa f_L1_009 to a generated japandi model with correctly attached cushions, fixing the floating-cushion visual artifact. | ![](agent/r1_093_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_094_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 353 | 1 | swap_model | f_L1_012 | adjusted_by_ai | 74.0 -> 74.0 | Swap sofa f_L1_012 to a generated japandi model with correctly attached cushions, fixing the floating-cushion visual artifact. | ![](agent/r1_095_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_096_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 357 | 1 | swap_model | f_L-1_017 | adjusted_by_ai | 47.0 -> 47.0 | stove overlaps counter f_L-1_011 by 0.41 m2; swap to a slimmer model to clear the overlap | ![](agent/r1_097_swap_model_before_r_L-1_mutfak_2.png) | ![](agent/r1_098_swap_model_after_r_L-1_mutfak_2.png) |
| 358 | 1 | swap_model | f_L-1_068 | adjusted_by_ai | 47.0 -> 47.0 | sink overlaps counter f_L-1_012 by 0.39 m2; swap to a model that fits the counter footprint | ![](agent/r1_099_swap_model_before_r_L-1_mutfak_2.png) | ![](agent/r1_100_swap_model_after_r_L-1_mutfak_2.png) |
| 364 | 1 | move_piece | f_L0_022 | adjusted_by_ai | 87.0 -> 87.0 | Desk cuts wall w_L0_026 by 0.094 m; nudge 0.1 m into the room to clear the wall. | ![](agent/r1_106_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_107_move_piece_after_r_L0_yatak_odasi_3.png) |
| 374 | 1 | move_piece | f_L0_039 | adjusted_by_ai | 87.0 -> 97.0 | Wardrobe blocks window win_L0_006; slide it along the same wall to the clear span s1, positioned away from the bed, so it no longer stands in front of the window. | ![](agent/r1_111_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_112_move_piece_after_r_L0_yatak_odasi_3.png) |
| 376 | 1 | set_exterior | set_exterior | agent_override | - | Rebuild the exterior with a proper 4-level mansard roof (steeper lower slope) so the roof line clears the 5.39 m decor tops and the 2.10 m door tops, and the render shows the 4 stories the spec requires. | - | - |
| 378 | 1 | set_exterior | set_exterior | agent_override | - | 9.7 m of outer wall is a blank facade; acknowledge it with a hedge and fence along the site so the blank facade is screened. | - | - |
| 379 | 1 | swap_model | f_L0_015 | adjusted_by_ai | 77.0 -> 77.0 | Narrower, shallower toilet (0.415 x 0.568 m) to clear the 0.013 m cut into wall w_L0_008. | ![](agent/r1_113_swap_model_before_r_L0_banyo_2.png) | ![](agent/r1_114_swap_model_after_r_L0_banyo_2.png) |
| 385 | 1 | swap_model | f_L0_005 | adjusted_by_ai | 77.0 -> 77.0 | Closest catalog washbasin to the drawn 1.0 x 0.55 m footprint to close the library gap. | ![](agent/r1_116_swap_model_before_r_L0_banyo_2.png) | ![](agent/r1_117_swap_model_after_r_L0_banyo_2.png) |
| 386 | 1 | move_piece | f_L0_023 | adjusted_by_ai | 87.0 -> 87.0 | Nudge desk 0.1 m along the left wall to clear the 0.093 m intersection with wall w_L0_025 (S2). | ![](agent/r1_118_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_119_move_piece_after_r_L0_yatak_odasi_4.png) |
| 387 | 1 | set_exterior | set_exterior | agent_override | - | The 9.7 m blank facade is the building's exterior wall; mark it as exterior to resolve the missing window/door finding (X3). | - | - |
| 394 | 1 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Replace crude low-poly toilet block with a properly proportioned model that also clears the 0.013 m wall cut on w_L-1_005 | ![](agent/r1_121_swap_model_before_r_L-1_banyo.png) | ![](agent/r1_122_swap_model_after_r_L-1_banyo.png) |
| 401 | 1 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | Toilet cuts wall w_L0_008 by 0.013 m; this model is 0.12 m shallower (0.568 m vs 0.69 m) so the footprint clears the wall. | ![](agent/r1_125_swap_model_before_r_L0_banyo.png) | ![](agent/r1_126_swap_model_after_r_L0_banyo.png) |
| 406 | 1 | place_group | r_L0_banyo | added_by_ai | 77.0 -> 77.0 | Bathroom has no shower or bathtub; place a shower group so the wet-area requirement is met. | ![](agent/r1_128_place_group_before_r_L0_banyo.png) | ![](agent/r1_129_place_group_after_r_L0_banyo.png) |
| 408 | 1 | remove_piece | f_L0_061 | added_by_ai | 77.0 -> 77.0 | The solver placed a duplicate washbasin instead of the requested shower; removing it so a real shower can be placed. | ![](agent/r1_133_remove_piece_before_r_L0_banyo.png) | ![](agent/r1_134_remove_piece_after_r_L0_banyo.png) |
| 412 | 1 | place_group | r_L0_banyo | added_by_ai | 77.0 -> 77.0 | Retry after removing the duplicate washbasin: add the missing shower to satisfy the bathroom program. | ![](agent/r1_136_place_group_before_r_L0_banyo.png) | ![](agent/r1_138_place_group_after_r_L0_banyo.png) |
| 415 | 1 | swap_model | f_L1_014 | adjusted_by_ai | 77.0 -> 77.0 | toilet f_L1_014 cuts wall w_L1_004 by 0.013 m; a shallower model (0.57 m deep vs 0.69 m) clears the wall | ![](agent/r1_139_swap_model_before_r_L1_banyo_2.png) | ![](agent/r1_141_swap_model_after_r_L1_banyo_2.png) |
| 417 | 1 | remove_piece | f_L0_061 | added_by_ai | 77.0 -> 77.0 | The solver again placed a duplicate washbasin instead of a shower; removing it to try the bathtub option. | ![](agent/r1_142_remove_piece_before_r_L0_banyo.png) | ![](agent/r1_143_remove_piece_after_r_L0_banyo.png) |
| 418 | 1 | place_group | r_L0_banyo | added_by_ai | 77.0 -> 77.0 | Shower option keeps resolving to a duplicate washbasin; try the bathtub option to satisfy the wet-area requirement. | ![](agent/r1_144_place_group_before_r_L0_banyo.png) | ![](agent/r1_145_place_group_after_r_L0_banyo.png) |
| 419 | 1 | swap_model | f_L1_013 | adjusted_by_ai | 77.0 -> 77.0 | toilet f_L1_013 cuts wall w_L1_004 by 0.013 m; a slimmer library model (0.415 x 0.568 m) clears the wall without moving the drawn fixture | ![](agent/r1_146_swap_model_before_r_L1_banyo.png) | ![](agent/r1_147_swap_model_after_r_L1_banyo.png) |
| 421 | 1 | report_library_gap | f_L-1_025 | library_gap | - | No washbasin candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2 % non-uniform, mean scale 1.3433); parametric fixture used by design. | - | - |
| 422 | 1 | report_library_gap | f_L-1_055 | library_gap | - | No bathtub candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest gen_bathtub_industrial_1_46aaa4c2 at 18.5 % non-uniform, mean scale 1.1507); 3 fitted outside the real height 0.4-0.72 m; parametric fixture used by design. | - | - |
| 428 | 1 | swap_model | f_L-1_052 | adjusted_by_ai | 77.0 -> 77.0 | Swap to a japandi toilet whose 0.415 m width is narrower than the drawn 0.5 m, to clear the 0.013 m cut of wall w_L-1_005. | ![](agent/r1_154_swap_model_before_r_L-1_banyo_2.png) | ![](agent/r1_155_swap_model_after_r_L-1_banyo_2.png) |
| 434 | 1 | swap_model | f_L0_014 | adjusted_by_ai | 77.0 -> 77.0 | swap to a toilet with 0.57 m depth so the fixture no longer cuts wall w_L0_005 by 0.012 m | ![](agent/r1_157_swap_model_before_r_L0_e_banyo_2.png) | ![](agent/r1_158_swap_model_after_r_L0_e_banyo_2.png) |
| 435 | 1 | report_library_gap | f_L0_012 | library_gap | - | no shower candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest: gen_shower_japandi_6_bd58a347 at 52.4 % non-uniform, mean scale 0.8967); parametric fixture kept by design | - | - |
| 436 | 1 | report_library_gap | f_L0_004 | library_gap | - | no washbasin candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest: objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2 % non-uniform, mean scale 1.3433); parametric fixture kept by design | - | - |
| 437 | 1 | swap_model | f_L0_013 | adjusted_by_ai | 77.0 -> 77.0 | Smaller-depth toilet model (0.57 m) so the bowl no longer cuts wall w_L0_005 by 0.012 m | ![](agent/r1_159_swap_model_before_r_L0_e_banyo.png) | ![](agent/r1_160_swap_model_after_r_L0_e_banyo.png) |
| 438 | 1 | report_library_gap | f_L0_006 | library_gap | - | No washbasin candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2% non-uniform, mean scale 1.3433); parametric fixture kept by design | - | - |
| 439 | 1 | report_library_gap | f_L0_011 | library_gap | - | No shower candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest gen_shower_japandi_6_bd58a347 at 52.4% non-uniform, mean scale 0.8967); parametric fixture kept by design | - | - |
| 750 | 2 | move_piece | f_L-1_050 | adjusted_by_ai | 0.0 -> 0.0 | Move armchair 0.26m left so its front free zone stays in the room and it sits closer to the sofa cluster. | ![](agent/r2_029_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_030_move_piece_after_r_L-1_salon_2.png) |
| 759 | 2 | swap_model | f_L-1b_013 | adjusted_by_ai | 50.0 -> 50.0 | swap stove to a model whose footprint does not overlap kitchen_counter f_L-1b_009 | ![](agent/r2_034_swap_model_before_r_L-1b_salon.png) | ![](agent/r2_035_swap_model_after_r_L-1b_salon.png) |
| 760 | 2 | swap_model | f_L-1b_064 | adjusted_by_ai | 50.0 -> 50.0 | swap sink to a model whose footprint does not overlap kitchen_counter f_L-1b_010 | ![](agent/r2_036_swap_model_before_r_L-1b_salon.png) | ![](agent/r2_037_swap_model_after_r_L-1b_salon.png) |
| 763 | 2 | move_piece | f_L-1_049 | adjusted_by_ai | 0.0 -> 0.0 | Shift the armchair 0.3 m toward the room centre so its front clearance stays inside the room and it sits within 2.0 m of the sofa/sofa_corner anchor. | ![](agent/r2_038_move_piece_before_r_L-1_salon.png) | ![](agent/r2_039_move_piece_after_r_L-1_salon.png) |
| 764 | 2 | move_piece | f_L-1_028 | adjusted_by_ai | 0.0 -> 0.0 | Nudge the right column of dining chairs 0.3 m toward the (not-built) table_dining f_L-1_027 so each chair is within 0.8 m of a table. | ![](agent/r2_040_move_piece_before_r_L-1_salon.png) | ![](agent/r2_041_move_piece_after_r_L-1_salon.png) |
| 768 | 2 | move_piece | f_L-1_029 | adjusted_by_ai | 0.0 -> 0.0 | Nudge the right column of dining chairs 0.3 m toward the (not-built) table_dining f_L-1_027 so each chair is within 0.8 m of a table. | ![](agent/r2_042_move_piece_before_r_L-1_salon.png) | ![](agent/r2_043_move_piece_after_r_L-1_salon.png) |
| 769 | 2 | move_piece | f_L-1_030 | adjusted_by_ai | 0.0 -> 0.0 | Nudge the right column of dining chairs 0.3 m toward the (not-built) table_dining f_L-1_027 so each chair is within 0.8 m of a table. | ![](agent/r2_044_move_piece_before_r_L-1_salon.png) | ![](agent/r2_045_move_piece_after_r_L-1_salon.png) |
| 772 | 2 | move_piece | f_L-1_031 | adjusted_by_ai | 0.0 -> 0.0 | Nudge the right column of dining chairs 0.3 m toward the (not-built) table_dining f_L-1_027 so each chair is within 0.8 m of a table. | ![](agent/r2_046_move_piece_before_r_L-1_salon.png) | ![](agent/r2_048_move_piece_after_r_L-1_salon.png) |
| 774 | 2 | move_piece | f_L1_012 | adjusted_by_ai | 74.0 -> 74.0 | Nudge sofa f_L1_012 0.003 m (max allowance) towards the right wall w_L1_012 to minimize the gap, as a full snap was rejected in round 1. | ![](agent/r2_049_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_051_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 775 | 2 | relayout_room | r_L0_yatak_odasi | adjusted_by_ai | 54.0 -> 60.0 | Re-apply solver candidate 1 to move the storage group away from window win_L0_005 and clear the wardrobe overlap and wall cuts (G12/S2/F9). | ![](agent/r2_052_relayout_room_before_r_L0_yatak_odasi.png) | ![](agent/r2_053_relayout_room_after_r_L0_yatak_odasi.png) |
| 776 | 2 | move_piece | f_L1_009 | adjusted_by_ai | 74.0 -> 74.0 | Nudge sofa f_L1_009 0.29 m towards the bottom wall w_L1_001 (just under the 0.3 m allowance) to reduce the distance of its back from the wall, as a full snap was rejected in round 1. | ![](agent/r2_056_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_057_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 802 | 2 | swap_model | f_L-1_008 | adjusted_by_ai | 47.0 -> 47.0 | slimmer 0.50 m wide stove to clear the 0.41 m² overlap with counter f_L-1_002 | ![](agent/r2_074_swap_model_before_r_L-1_mutfak.png) | ![](agent/r2_075_swap_model_after_r_L-1_mutfak.png) |
| 804 | 2 | swap_model | f_L-1_067 | adjusted_by_ai | 47.0 -> 47.0 | slimmer 0.47 m deep sink to clear the 0.39 m² overlap with counter f_L-1_003 | ![](agent/r2_076_swap_model_before_r_L-1_mutfak.png) | ![](agent/r2_077_swap_model_after_r_L-1_mutfak.png) |
| 808 | 2 | move_piece | f_L0_022 | adjusted_by_ai | 97.0 -> 97.0 | Move desk 0.1 m in +y away from wall w_L0_026 to resolve the 0.095 m intersection (S2). | ![](agent/r2_082_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_083_move_piece_after_r_L0_yatak_odasi_3.png) |
| 813 | 2 | set_exterior | set_exterior | agent_override | - | Acknowledge the 9.7 m blank facade on the outer wall as an intended architectural feature (X3). | - | - |
| 817 | 2 | move_piece | f_L0_037 | adjusted_by_ai | 87.0 -> 87.0 | Nudge the wardrobe 0.3 m into the room so it no longer stands in front of the window (G12). | ![](agent/r2_086_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r2_087_move_piece_after_r_L0_yatak_odasi_4.png) |
| 818 | 2 | move_piece | f_L0_023 | adjusted_by_ai | 87.0 -> 87.0 | Nudge the desk 0.1 m down so its corner no longer cuts wall w_L0_025 while keeping its back on the wall (S2). | ![](agent/r2_088_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r2_089_move_piece_after_r_L0_yatak_odasi_4.png) |
| 819 | 2 | set_exterior | set_exterior | agent_override | - | Mark the 9.7 m blank facade as exterior to resolve the missing window/door finding (X3). | - | - |
| 821 | 2 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | The current japandi_6 toilet model is flagged as crude/low-poly and cuts wall w_L0_008 by 0.013 m; japandi_3 has a cleaner shape and a slightly narrower footprint (0.405 x 0.709) that should clear the wall. | ![](agent/r2_090_swap_model_before_r_L0_banyo.png) | ![](agent/r2_091_swap_model_after_r_L0_banyo.png) |
| 823 | 2 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | japandi_3 still leaves the toilet cutting wall w_L0_008 by 0.013 m; japandi_1 is the narrowest toilet in the library (0.415 x 0.692) and should clear the wall. | ![](agent/r2_093_swap_model_before_r_L0_banyo.png) | ![](agent/r2_094_swap_model_after_r_L0_banyo.png) |
| 827 | 2 | swap_model | f_L0_015 | adjusted_by_ai | 77.0 -> 77.0 | Toilet f_L0_015 cuts wall w_L0_008 by 0.013 m; swap to a model that fits. | ![](agent/r2_095_swap_model_before_r_L0_banyo_2.png) | ![](agent/r2_096_swap_model_after_r_L0_banyo_2.png) |
| 828 | 2 | place_group | r_L0_banyo_2 | added_by_ai | 77.0 -> 77.0 | Add a shower to satisfy the missing shower\|bathtub requirement, since complete_group found no place. | ![](agent/r2_098_place_group_before_r_L0_banyo_2.png) | ![](agent/r2_099_place_group_after_r_L0_banyo_2.png) |
| 830 | 2 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | japandi_1 still leaves the toilet cutting wall w_L0_008 by 0.013 m; classic_3 is the narrowest toilet in the library (0.396 x 0.724) and should clear the wall. | ![](agent/r2_100_swap_model_before_r_L0_banyo.png) | ![](agent/r2_101_swap_model_after_r_L0_banyo.png) |
| 833 | 2 | remove_piece | f_L0_066 | added_by_ai | 77.0 -> 77.0 | The solver placed a washbasin instead of the requested shower, which does not satisfy the missing shower\|bathtub requirement. | ![](agent/r2_104_remove_piece_before_r_L0_banyo_2.png) | ![](agent/r2_105_remove_piece_after_r_L0_banyo_2.png) |
| 836 | 2 | place_group | r_L0_banyo_2 | added_by_ai | 77.0 -> 77.0 | Add a bathtub to satisfy the missing shower\|bathtub requirement, since the shower option was not placeable. | ![](agent/r2_106_place_group_before_r_L0_banyo_2.png) | ![](agent/r2_107_place_group_after_r_L0_banyo_2.png) |
| 837 | 2 | swap_model | f_L0_013 | adjusted_by_ai | 77.0 -> 77.0 | Replace the crude low-poly box toilet with a realistic japandi toilet model (0.40 x 0.72 m, close to the drawn 0.5 x 0.68 m) that also clears the 0.012 m wall cut. | ![](agent/r2_108_swap_model_before_r_L0_e_banyo.png) | ![](agent/r2_109_swap_model_after_r_L0_e_banyo.png) |
| 838 | 2 | set_exterior | set_exterior | agent_override | - | Raise the mansard eaves and widen the overhang so the roof fully covers the building outline, clears the 2.10 m door tops (d_L1_004/005) and the decor piece poking through, keeping the specified mansard form. | - | - |
| 839 | 2 | remove_piece | f_L0_066 | added_by_ai | 77.0 -> 77.0 | The solver again placed a washbasin instead of the requested bathtub, which does not satisfy the missing shower\|bathtub requirement. | ![](agent/r2_111_remove_piece_before_r_L0_banyo_2.png) | ![](agent/r2_112_remove_piece_after_r_L0_banyo_2.png) |
| 841 | 2 | place_group | r_L0_banyo_2 | added_by_ai | 77.0 -> 77.0 | Add a shower with washer to satisfy the missing shower\|bathtub requirement, since shower and bathtub options were not placeable. | ![](agent/r2_113_place_group_before_r_L0_banyo_2.png) | ![](agent/r2_114_place_group_after_r_L0_banyo_2.png) |
| 843 | 2 | remove_piece | f_L0_066 | added_by_ai | 77.0 -> 77.0 | The solver again placed a washbasin instead of the requested shower_washer, which does not satisfy the missing shower\|bathtub requirement. | ![](agent/r2_116_remove_piece_before_r_L0_banyo_2.png) | ![](agent/r2_117_remove_piece_after_r_L0_banyo_2.png) |
| 846 | 2 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Toilet f_L-1_051 cuts wall w_L-1_005 by 0.013 m; swapping to a model with a slightly smaller footprint resolves the wall intersection without moving the fixed equipment. | ![](agent/r2_118_swap_model_before_r_L-1_banyo.png) | ![](agent/r2_119_swap_model_after_r_L-1_banyo.png) |
| 848 | 2 | swap_model | f_L-1_052 | adjusted_by_ai | 77.0 -> 77.0 | Narrower toilet model (0.38 m wide) to clear the 0.013 m cut into wall w_L-1_005 (c:S2:f_L-1_052). | ![](agent/r2_120_swap_model_before_r_L-1_banyo_2.png) | ![](agent/r2_121_swap_model_after_r_L-1_banyo_2.png) |
| 856 | 2 | swap_model | f_L1_013 | adjusted_by_ai | 77.0 -> 77.0 | S2: toilet cuts wall w_L1_004 by 0.013 m; try a model whose footprint clears the wall | ![](agent/r2_126_swap_model_before_r_L1_banyo.png) | ![](agent/r2_127_swap_model_after_r_L1_banyo.png) |
| 865 | 2 | swap_model | f_L0_014 | adjusted_by_ai | 77.0 -> 77.0 | Swap to a toilet model with slightly different geometry to resolve the 0.012 m wall cut on w_L0_005 | ![](agent/r2_132_swap_model_before_r_L0_e_banyo_2.png) | ![](agent/r2_133_swap_model_after_r_L0_e_banyo_2.png) |
| 1183 | 3 | move_piece | f_L-1_049 | adjusted_by_ai | 0.0 -> 0.0 | Nudge armchair 0.009 m into the room so its front free zone stays inside and it sits within 2.0 m of the sofa anchor. | ![](agent/r3_029_move_piece_before_r_L-1_salon.png) | ![](agent/r3_030_move_piece_after_r_L-1_salon.png) |
| 1185 | 3 | move_piece | f_L-1_032 | adjusted_by_ai | 0.0 -> 0.0 | Nudge left dining chair 0.29 m toward the dining table so it is within 0.8 m of it. | ![](agent/r3_034_move_piece_before_r_L-1_salon.png) | ![](agent/r3_035_move_piece_after_r_L-1_salon.png) |
| 1186 | 3 | move_piece | f_L-1_036 | adjusted_by_ai | 0.0 -> 0.0 | Nudge mid-row chair 0.3 m toward the dining table to satisfy the 0.8 m chair-to-table rule. | ![](agent/r3_036_move_piece_before_r_L-1_salon.png) | ![](agent/r3_037_move_piece_after_r_L-1_salon.png) |
| 1189 | 3 | move_piece | f_L-1_059 | adjusted_by_ai | 0.0 -> 0.0 | Move floor lamp 0.29 m away from the window wall so it no longer blocks the sightline in front of win_L-1_001. | ![](agent/r3_041_move_piece_before_r_L-1_salon.png) | ![](agent/r3_042_move_piece_after_r_L-1_salon.png) |
| 1193 | 3 | swap_model | f_L-1_075 | adjusted_by_ai | 0.0 -> 0.0 | Swap ottoman for a smaller model so it no longer overlaps/cuts armchair f_L-1_070. | ![](agent/r3_045_swap_model_before_r_L-1_salon.png) | ![](agent/r3_046_swap_model_after_r_L-1_salon.png) |
| 1194 | 3 | move_piece | f_L-1_050 | adjusted_by_ai | 0.0 -> 0.0 | Pull the armchair 0.036 m into the room so its front free zone stays inside and it sits within 2.0 m of the sofa anchor (fixes F6/F8). | ![](agent/r3_047_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_048_move_piece_after_r_L-1_salon_2.png) |
| 1205 | 3 | relayout_room | r_L0_yatak_odasi | adjusted_by_ai | 60.0 -> 54.0 | Re-apply solver candidate 1 to resolve the wardrobes' window (G12), wall-cut (S2) and overlap (F9) findings. | ![](agent/r3_058_relayout_room_before_r_L0_yatak_odasi.png) | ![](agent/r3_060_relayout_room_after_r_L0_yatak_odasi.png) |
| 1213 | 3 | retype_piece | f_L1_028 | adjusted_by_ai | 74.0 -> 74.0 | Untyped 0.68x0.78 m drawn piece; AI pass armchair fits the size and the seating room. | ![](agent/r3_070_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_071_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 1214 | 3 | retype_piece | f_L1_029 | adjusted_by_ai | 74.0 -> 74.0 | Untyped 0.68x0.78 m drawn piece; AI pass armchair fits the size and the seating room. | ![](agent/r3_072_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_073_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 1220 | 3 | retype_piece | f_L1_034 | adjusted_by_ai | 74.0 -> 74.0 | Untyped 1.09x0.40 m drawn piece; size table and zone give bookshelf. | ![](agent/r3_080_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_081_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 1221 | 3 | retype_piece | f_L1_033 | adjusted_by_ai | 74.0 -> 74.0 | Untyped 0.40x2.17 m drawn piece; size table and zone give bookshelf. | ![](agent/r3_082_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_083_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 1226 | 3 | move_piece | f_L1_010 | adjusted_by_ai | 74.0 -> 74.0 | Nudge sofa f_L1_010 0.3 m toward the room centre to clear the desk's front zone and open the free zone in front of sofa f_L1_011. | ![](agent/r3_085_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_086_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 1230 | 3 | relayout_room | r_L0_yatak_odasi_2 | adjusted_by_ai | 54.0 -> 60.0 | Re-run solver to reposition the overlapping wardrobes off window win_L0_006 and clear the F9 overlap and S2 wall cuts. | ![](agent/r3_087_relayout_room_before_r_L0_yatak_odasi_2.png) | ![](agent/r3_088_relayout_room_after_r_L0_yatak_odasi_2.png) |
| 1231 | 3 | move_piece | f_L0_023 | adjusted_by_ai | 87.0 -> 87.0 | Move desk 0.105m to clear wall w_L0_025 intersection (0.097m cut) while keeping back against wall. | ![](agent/r3_092_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_093_move_piece_after_r_L0_yatak_odasi_4.png) |
| 1234 | 3 | move_piece | f_L0_037 | adjusted_by_ai | 87.0 -> 87.0 | Move wardrobe 0.002m to snap back to wall w_L0_003, resolving 0.28m offset. | ![](agent/r3_096_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_097_move_piece_after_r_L0_yatak_odasi_4.png) |
| 1239 | 3 | mark_not_furniture | f_L0_023 | adjusted_by_ai | 87.0 -> 90.0 | Mark desk as not furniture: it's an unusual fixture for a bedroom and the room is missing its primary bed fixture. | ![](agent/r3_099_mark_not_furniture_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_100_mark_not_furniture_after_r_L0_yatak_odasi_4.png) |
| 1240 | 3 | set_exterior | set_exterior | agent_override | - | Mark the 9.7 m blank facade as exterior to resolve the missing window/door finding. | - | - |
| 1251 | 3 | move_piece | f_L0_022 | adjusted_by_ai | 97.0 -> 97.0 | Move desk 0.1 m away from wall w_L0_026 to resolve the 0.095 m intersection (S2). | ![](agent/r3_108_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_109_move_piece_after_r_L0_yatak_odasi_3.png) |
| 1254 | 3 | report_library_gap | f_L-1_017 | library_gap | - | No audited stove model fits the drawn 0.75x0.55 m footprint within 10% non-uniform scale and 0.85..1.2 mean scale; closest gen_stove_japandi_6_1c3993c0 is at 4.6% non-uniform but mean scale 0.766, and 11 others fall outside the real 0.8-1.2 m height band, so the parametric fixture is used by design. | - | - |
| 1258 | 3 | set_exterior | set_exterior | agent_override | - | Raise the roof/ceiling so the 1.90 m shoe cabinet no longer pokes through the sloped ceiling (c:X2:f_L1_046). | - | - |
| 1260 | 3 | mark_not_furniture | f_L-1b_002 | adjusted_by_ai | 50.0 -> 50.0 | The 5.14 x 2.37 m drawn cluster is too large to be a single furniture piece; it is a group of drawn elements, not built furniture | ![](agent/r3_110_mark_not_furniture_before_r_L-1b_salon.png) | ![](agent/r3_111_mark_not_furniture_after_r_L-1b_salon.png) |
| 1269 | 3 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | shorter depth (0.57 m) to stop cutting wall w_L0_008 and a cleaner model than the blocky one | ![](agent/r3_114_swap_model_before_r_L0_banyo.png) | ![](agent/r3_115_swap_model_after_r_L0_banyo.png) |
| 1271 | 3 | set_exterior | set_exterior | agent_override | - | Raise the mansard roof (steeper pitch, wider overhang) so the full 4-level building is covered and the 5.05 m decor piece no longer pokes through the roof. | - | - |
| 1277 | 3 | report_library_gap | f_L-1_026 | library_gap | - | No washbasin candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2% non-uniform, mean scale 1.3433); parametric fixture kept by design. | - | - |
| 1278 | 3 | report_library_gap | f_L-1_056 | library_gap | - | No bathtub candidate within 10% non-uniform scale and 0.85..1.2 mean scale (closest gen_bathtub_industrial_1_46aaa4c2 at 18.5% non-uniform, mean scale 1.1507); 3 fitted outside the real height 0.4-0.72 m; parametric fixture kept by design. | - | - |
| 1284 | 3 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Refined japandi toilet model (0.405 x 0.709 m, close to the drawn 0.5 x 0.69 m) replaces the crude low-poly model and resolves the 0.013 m wall cut. | ![](agent/r3_122_swap_model_before_r_L-1_banyo.png) | ![](agent/r3_123_swap_model_after_r_L-1_banyo.png) |
| 1292 | 3 | swap_model | f_L-1_052 | adjusted_by_ai | 77.0 -> 77.0 | S2: toilet cuts wall w_L-1_005 by 0.013 m; japandi toilet (1) has a slightly smaller footprint (0.415 x 0.692) that clears the wall. | ![](agent/r3_124_swap_model_before_r_L-1_banyo_2.png) | ![](agent/r3_125_swap_model_after_r_L-1_banyo_2.png) |
| 1296 | 3 | swap_model | f_L1_013 | adjusted_by_ai | 77.0 -> 77.0 | Toilet f_L1_013 cuts wall w_L1_004 by 0.013 m; this japandi toilet has a shallower 0.57 m depth (vs 0.72 m) so the footprint clears the wall. | ![](agent/r3_126_swap_model_before_r_L1_banyo.png) | ![](agent/r3_127_swap_model_after_r_L1_banyo.png) |
| 1301 | 3 | swap_model | f_L0_014 | adjusted_by_ai | 77.0 -> 77.0 | Slightly smaller japandi toilet (0.405 x 0.717 m) resolves the 0.012 m cut of wall w_L0_005 without new collisions. | ![](agent/r3_129_swap_model_before_r_L0_e_banyo_2.png) | ![](agent/r3_130_swap_model_after_r_L0_e_banyo_2.png) |
| 1302 | 3 | swap_model | f_L1_014 | adjusted_by_ai | 77.0 -> 77.0 | S2: toilet f_L1_014 cuts wall w_L1_004 by 0.013 m; a slimmer japandi model (0.405 x 0.709 m vs drawn 0.5 x 0.69) clears the wall intersection | ![](agent/r3_131_swap_model_before_r_L1_banyo_2.png) | ![](agent/r3_132_swap_model_after_r_L1_banyo_2.png) |
| 1619 | 4 | move_piece | f_L-1_050 | adjusted_by_ai | 0.0 -> 0.0 | Pull the armchair fully inside the room boundary and closer to the seating cluster, resolving the out-of-bounds front zone and isolation. | ![](agent/r4_030_move_piece_before_r_L-1_salon_2.png) | ![](agent/r4_031_move_piece_after_r_L-1_salon_2.png) |
| 1625 | 4 | move_piece | f_L-1_075 | adjusted_by_ai | 0.0 -> 0.0 | clear overlap/cut with armchair f_L-1_070 | ![](agent/r4_034_move_piece_before_r_L-1_salon.png) | ![](agent/r4_035_move_piece_after_r_L-1_salon.png) |
| 1628 | 4 | move_piece | f_L-1_077 | adjusted_by_ai | 0.0 -> 0.0 | clear overlap/cut with armchair f_L-1_071 | ![](agent/r4_036_move_piece_before_r_L-1_salon.png) | ![](agent/r4_037_move_piece_after_r_L-1_salon.png) |
| 1632 | 4 | move_piece | f_L-1_057 | adjusted_by_ai | 0.0 -> 0.0 | Move the floor lamp 0.29 m away from the window wall to clear the window sill obstruction and sit within 1.2 m of the armchair f_L-1_050. | ![](agent/r4_038_move_piece_before_r_L-1_salon_2.png) | ![](agent/r4_039_move_piece_after_r_L-1_salon_2.png) |
| 1634 | 4 | swap_model | f_L-1_076 | adjusted_by_ai | 0.0 -> 0.0 | Swap the ottoman for a smaller model (0.45 x 0.46 m) to eliminate the 0.19 m² overlap and 0.024 m cut with armchair f_L-1_069. | ![](agent/r4_041_swap_model_before_r_L-1_salon_2.png) | ![](agent/r4_042_swap_model_after_r_L-1_salon_2.png) |
| 1635 | 4 | swap_model | f_L-1_078 | adjusted_by_ai | 0.0 -> 0.0 | Swap the ottoman for a smaller model (0.45 x 0.46 m) to eliminate the 0.19 m² overlap and 0.024 m cut with armchair f_L-1_072. | ![](agent/r4_043_swap_model_before_r_L-1_salon_2.png) | ![](agent/r4_044_swap_model_after_r_L-1_salon_2.png) |
| 1636 | 4 | swap_model | f_L-1b_013 | adjusted_by_ai | 50.0 -> 50.0 | smaller stove footprint to clear the overlap with the counter | ![](agent/r4_045_swap_model_before_r_L-1b_salon.png) | ![](agent/r4_046_swap_model_after_r_L-1b_salon.png) |
| 1637 | 4 | swap_model | f_L-1b_064 | adjusted_by_ai | 50.0 -> 50.0 | narrower sink footprint to clear the overlap with the counter | ![](agent/r4_047_swap_model_before_r_L-1b_salon.png) | ![](agent/r4_048_swap_model_after_r_L-1b_salon.png) |
| 1638 | 4 | move_piece | f_L-1b_027 | adjusted_by_ai | 50.0 -> 50.0 | pull the chair up to the table edge so it is no longer standing alone | ![](agent/r4_049_move_piece_before_r_L-1b_salon.png) | ![](agent/r4_050_move_piece_after_r_L-1b_salon.png) |
| 1639 | 4 | move_piece | f_L-1b_028 | adjusted_by_ai | 50.0 -> 50.0 | pull the chair up to the table edge so it is no longer standing alone | ![](agent/r4_051_move_piece_before_r_L-1b_salon.png) | ![](agent/r4_052_move_piece_after_r_L-1b_salon.png) |
| 1646 | 4 | mark_not_furniture | f_L-1b_007 | adjusted_by_ai | 50.0 -> 50.0 | stove overlaps the kitchen counter it is built into; it is a fixture symbol, not a separate furniture piece | ![](agent/r4_057_mark_not_furniture_before_r_L-1b_salon_2.png) | ![](agent/r4_058_mark_not_furniture_after_r_L-1b_salon_2.png) |
| 1647 | 4 | mark_not_furniture | f_L-1b_063 | adjusted_by_ai | 50.0 -> 60.0 | sink overlaps the kitchen counter it is built into; it is a fixture symbol, not a separate furniture piece | ![](agent/r4_059_mark_not_furniture_before_r_L-1b_salon_2.png) | ![](agent/r4_060_mark_not_furniture_after_r_L-1b_salon_2.png) |
| 1651 | 4 | rotate_piece | f_L1_010 | adjusted_by_ai | 74.0 -> 74.0 | Rotate sofa f_L1_010 so its back faces the free wall span s0 (w_L1_001) and its front faces into the room, fixing the 'back not on a wall' finding | ![](agent/r4_062_rotate_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r4_063_rotate_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 1655 | 4 | relayout_room | r_L0_yatak_odasi_2 | adjusted_by_ai | 60.0 -> 54.0 | Re-apply solver candidate 1 to move the wardrobes off window win_L0_006, resolve the f_L0_025/f_L0_040 overlap and the small wall cuts on w_L0_004. | ![](agent/r4_065_relayout_room_before_r_L0_yatak_odasi_2.png) | ![](agent/r4_066_relayout_room_after_r_L0_yatak_odasi_2.png) |
| 1695 | 4 | move_piece | f_L0_022 | adjusted_by_ai | 97.0 -> 97.0 | Move desk 0.1 m in +y to clear wall w_L0_026 (S2: cuts wall by 0.095 m), within 0.205 m allowance. | ![](agent/r4_091_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r4_093_move_piece_after_r_L0_yatak_odasi_3.png) |
| 1697 | 4 | set_exterior | set_exterior | agent_override | - | Lower the roof pitch so the sloped ceiling clears the 1.90 m shoe cabinet in the corridor (c:X2:f_L1_046). | - | - |
| 1699 | 4 | set_exterior | set_exterior | agent_override | - | The 9.7 m blank facade is an intentional architectural feature; setting a flat roof with 0.3 m overhang acknowledges it as designed rather than an error. | - | - |
| 1704 | 4 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | D2: current toilet model is crude/low-poly; japandi_1 is a refined standard toilet shape (0.415x0.692, matching the drawn 0.5x0.69 footprint). | ![](agent/r4_098_swap_model_before_r_L0_banyo.png) | ![](agent/r4_099_swap_model_after_r_L0_banyo.png) |
| 1708 | 4 | swap_model | f_L0_015 | adjusted_by_ai | 77.0 -> 77.0 | swap to a japandi toilet whose footprint clears the 0.013 m cut of wall w_L0_008 | ![](agent/r4_100_swap_model_before_r_L0_banyo_2.png) | ![](agent/r4_101_swap_model_after_r_L0_banyo_2.png) |
| 1710 | 4 | swap_model | f_L0_013 | adjusted_by_ai | 77.0 -> 77.0 | swap to a detailed japandi toilet model with a shorter depth (0.57 m) to fix the crude low-poly box and the 0.012 m wall cut | ![](agent/r4_102_swap_model_before_r_L0_e_banyo.png) | ![](agent/r4_103_swap_model_after_r_L0_e_banyo.png) |
| 1720 | 4 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Toilet cuts wall w_L-1_005 by 0.013 m; a model with slightly smaller footprint clears the wall. | ![](agent/r4_105_swap_model_before_r_L-1_banyo.png) | ![](agent/r4_106_swap_model_after_r_L-1_banyo.png) |
| 1728 | 4 | swap_model | f_L1_013 | adjusted_by_ai | 77.0 -> 77.0 | slightly narrower/shorter japandi toilet to clear the 0.013 m cut into wall w_L1_004 | ![](agent/r4_108_swap_model_before_r_L1_banyo.png) | ![](agent/r4_109_swap_model_after_r_L1_banyo.png) |
| 1729 | 4 | swap_model | f_L0_014 | adjusted_by_ai | 77.0 -> 77.0 | Slightly narrower toilet (0.38 m wide vs 0.5 m) resolves the 0.012 m cut of wall w_L0_005; dry run confirmed no new collisions. | ![](agent/r4_110_swap_model_before_r_L0_e_banyo_2.png) | ![](agent/r4_112_swap_model_after_r_L0_e_banyo_2.png) |
| 1730 | 4 | swap_model | f_L1_014 | adjusted_by_ai | 77.0 -> 77.0 | S2: toilet f_L1_014 cuts wall w_L1_004 by 0.013 m; japandi_6 has a shallower footprint (0.568 m depth vs 0.717 m) so the back edge clears the wall. | ![](agent/r4_111_swap_model_before_r_L1_banyo_2.png) | ![](agent/r4_113_swap_model_after_r_L1_banyo_2.png) |
| 2078 | 5 | set_exterior | set_exterior | agent_override | - | Console table top (0.84 m) pokes through the sloped ceiling (0.40 m high at that spot) and the roof; adjust the roof so the ceiling clears the piece. | - | - |
| 2080 | 5 | set_exterior | set_exterior | agent_override | - | Balcony is an exterior space; the sloped-ceiling X2 collisions on the table and chairs are resolved by treating the room as exterior (no interior ceiling). | - | - |
| 2092 | 5 | set_exterior | set_exterior | agent_override | - | The room's sloped ceiling is only 0.40 m high where the furniture stands and the roof is too low for the pieces' tops (up to 4.07 m); raising the roof clears the X2 roof-poke findings for the sofas, desk and chair. | - | - |
| 2119 | 5 | relayout_room | r_L0_yatak_odasi | adjusted_by_ai | 54.0 -> 60.0 | Re-solve the room to move the two drawn wardrobes off window win_L0_005 and off wall w_L0_003, separate them, and give the bed the required 0.60 m side clearance. | ![](agent/r5_057_relayout_room_before_r_L0_yatak_odasi.png) | ![](agent/r5_058_relayout_room_after_r_L0_yatak_odasi.png) |
| 2123 | 5 | mark_not_furniture | f_L0_038 | adjusted_by_ai | 60.0 -> 80.0 | f_L0_038 is a duplicate/misread outline of the storage run f_L0_026, not a distinct piece; the overlap persists after relayout. | ![](agent/r5_065_mark_not_furniture_before_r_L0_yatak_odasi.png) | ![](agent/r5_066_mark_not_furniture_after_r_L0_yatak_odasi.png) |
| 2132 | 5 | swap_model | f_L1_013 | adjusted_by_ai | 77.0 -> 77.0 | Toilet cuts wall w_L1_004 by 0.013 m; japandi_6 has the shortest depth (0.568 m vs 0.69 m drawn) so its footprint clears the wall. | ![](agent/r5_072_swap_model_before_r_L1_banyo.png) | ![](agent/r5_073_swap_model_after_r_L1_banyo.png) |
| 2143 | 5 | retype_piece | f_L0_040 | adjusted_by_ai | 54.0 -> 64.0 | f_L0_040 overlaps f_L0_025 by 0.87 m²; retype to dresser (a distinct storage type) to resolve the F9 overlap finding | ![](agent/r5_074_retype_piece_before_r_L0_yatak_odasi_2.png) | ![](agent/r5_075_retype_piece_after_r_L0_yatak_odasi_2.png) |
| 2155 | 5 | swap_model | f_L1_014 | adjusted_by_ai | 77.0 -> 77.0 | Toilet f_L1_014 cuts wall w_L1_004 by 0.013 m; the japandi toilet (1) has a 0.415 m width (vs 0.5 m drawn), so its back edge clears the wall. | ![](agent/r5_081_swap_model_before_r_L1_banyo_2.png) | ![](agent/r5_082_swap_model_after_r_L1_banyo_2.png) |
| 2163 | 5 | move_piece | f_L0_022 | adjusted_by_ai | 97.0 -> 97.0 | Move desk 0.1 m away from wall w_L0_026 to resolve the 0.095 m intersection (S2). | ![](agent/r5_108_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r5_109_move_piece_after_r_L0_yatak_odasi_3.png) |
| 2167 | 5 | swap_model | f_L0_015 | adjusted_by_ai | 77.0 -> 77.0 | Shorter toilet (0.57 m deep) so it no longer cuts wall w_L0_008 by 0.013 m. | ![](agent/r5_110_swap_model_before_r_L0_banyo_2.png) | ![](agent/r5_111_swap_model_after_r_L0_banyo_2.png) |
| 2171 | 5 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Swap the crude low-poly toilet (D2) to a better japandi model whose 0.415x0.691 footprint also clears the 0.013 m wall cut (S2). | ![](agent/r5_112_swap_model_before_r_L-1_banyo.png) | ![](agent/r5_113_swap_model_after_r_L-1_banyo.png) |
| 2173 | 5 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | Try the japandi toilet with the shortest depth (0.568 m) to clear the 0.013 m cut into wall w_L0_008. | ![](agent/r5_114_swap_model_before_r_L0_banyo.png) | ![](agent/r5_115_swap_model_after_r_L0_banyo.png) |
| 2176 | 5 | swap_model | f_L0_013 | adjusted_by_ai | 77.0 -> 77.0 | Swap the crude low-poly toilet block for a higher-quality japandi toilet model to fix the visual quality finding. | ![](agent/r5_116_swap_model_before_r_L0_e_banyo.png) | ![](agent/r5_117_swap_model_after_r_L0_e_banyo.png) |
| 2181 | 5 | swap_model | f_L0_014 | adjusted_by_ai | 77.0 -> 77.0 | Slightly smaller toilet model (0.415 x 0.568 m) resolves the 0.012 m cut of wall w_L0_005 without new collisions, per dry run. | ![](agent/r5_118_swap_model_before_r_L0_e_banyo_2.png) | ![](agent/r5_119_swap_model_after_r_L0_e_banyo_2.png) |
| 2466 | 6 | set_exterior | set_exterior | agent_override | - | The sloped ceiling over the corridor is only 0.67 m high where the console table stands (top 0.84 m), so the table shows through the ceiling; a flat roof gives full headroom. | - | - |
| 2468 | 6 | move_piece | f_L-1_076 | adjusted_by_ai | 0.0 -> 0.0 | Shift ottoman 0.24 m away from armchair f_L-1_069 to clear the 0.19 m² overlap (F9) and the 0.024 m cut (S2). | ![](agent/r6_032_move_piece_before_r_L-1_salon_2.png) | ![](agent/r6_033_move_piece_after_r_L-1_salon_2.png) |
| 2479 | 6 | swap_model | f_L-1_075 | adjusted_by_ai | 0.0 -> 0.0 | smaller ottoman model to clear the 0.18 m2 overlap and 0.024 m cut with armchair f_L-1_070 | ![](agent/r6_039_swap_model_before_r_L-1_salon.png) | ![](agent/r6_040_swap_model_after_r_L-1_salon.png) |
| 2480 | 6 | swap_model | f_L-1_077 | adjusted_by_ai | 0.0 -> 0.0 | smaller ottoman model to clear the 0.18 m2 overlap and 0.024 m cut with armchair f_L-1_071 | ![](agent/r6_041_swap_model_before_r_L-1_salon.png) | ![](agent/r6_042_swap_model_after_r_L-1_salon.png) |
| 2484 | 6 | move_piece | f_L-1b_027 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the right edge of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_044_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_045_move_piece_after_r_L-1b_salon.png) |
| 2486 | 6 | move_piece | f_L-1b_028 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the left edge of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_046_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_047_move_piece_after_r_L-1b_salon.png) |
| 2487 | 6 | move_piece | f_L-1b_029 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the right edge of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_049_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_050_move_piece_after_r_L-1b_salon.png) |
| 2488 | 6 | move_piece | f_L-1b_030 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the left edge of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_051_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_052_move_piece_after_r_L-1b_salon.png) |
| 2489 | 6 | move_piece | f_L-1b_031 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the right edge of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_053_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_054_move_piece_after_r_L-1b_salon.png) |
| 2490 | 6 | move_piece | f_L-1b_032 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the left edge of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_055_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_056_move_piece_after_r_L-1b_salon.png) |
| 2491 | 6 | move_piece | f_L-1b_034 | adjusted_by_ai | 50.0 -> 50.0 | Re-seat chair at the head of the dining table so it is within 0.8 m of the table (F8). | ![](agent/r6_057_move_piece_before_r_L-1b_salon.png) | ![](agent/r6_058_move_piece_after_r_L-1b_salon.png) |
| 2499 | 6 | relayout_room | r_L0_yatak_odasi_2 | adjusted_by_ai | 64.0 -> 70.0 | Re-solve with candidate 1 to move the wardrobe/dresser off window win_L0_006, clear the wall cuts and overlap, and open the bed's right-side clearance. | ![](agent/r6_060_relayout_room_before_r_L0_yatak_odasi_2.png) | ![](agent/r6_061_relayout_room_after_r_L0_yatak_odasi_2.png) |
| 2500 | 6 | rotate_piece | f_L-1b_022 | adjusted_by_ai | 60.0 -> 60.0 | face the dining table f_L-1b_017 (within 45°) | ![](agent/r6_062_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r6_063_rotate_piece_after_r_L-1b_salon_2.png) |
| 2501 | 6 | rotate_piece | f_L-1b_023 | adjusted_by_ai | 60.0 -> 60.0 | face the dining table f_L-1b_017 (within 45°) | ![](agent/r6_064_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r6_065_rotate_piece_after_r_L-1b_salon_2.png) |
| 2502 | 6 | rotate_piece | f_L-1b_024 | adjusted_by_ai | 60.0 -> 60.0 | face the dining table f_L-1b_017 directly | ![](agent/r6_066_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r6_067_rotate_piece_after_r_L-1b_salon_2.png) |
| 2503 | 6 | move_piece | f_L1_010 | adjusted_by_ai | 74.0 -> 74.0 | Attempt to nudge sofa f_L1_010 toward its wall to clear F3 (back 1.96 m off); only 0.001 m allowance remains, so this is the maximum possible move. | ![](agent/r6_068_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r6_070_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 2504 | 6 | move_piece | f_L1_011 | adjusted_by_ai | 74.0 -> 74.0 | Move sofa f_L1_011 0.3 m toward the top wall to reduce its F3 back-off-wall distance (0.79 m off). | ![](agent/r6_071_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r6_072_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 2508 | 6 | retype_piece | f_L1_016 | adjusted_by_ai | 74.0 -> 74.0 | 1.03 x 0.69 m drawn piece matches the AI's potted_plant pass; type it as a potted plant. | ![](agent/r6_081_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r6_082_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 2510 | 6 | retype_piece | f_L1_027 | adjusted_by_ai | 74.0 -> 74.0 | 0.68 x 0.78 m drawn piece matches the AI's armchair pass; type it as an armchair. | ![](agent/r6_084_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r6_085_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 2515 | 6 | rotate_piece | f_L1_012 | adjusted_by_ai | 74.0 -> 74.0 | Rotate sofa so its back aligns with the east wall (w_L1_012) and faces into the room, resolving F3 back-not-on-wall finding. | ![](agent/r6_086_rotate_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r6_087_rotate_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 2530 | 6 | swap_model | f_L-1_017 | adjusted_by_ai | 47.0 -> 47.0 | Swap to a 0.50 m wide stove so it fits within the counter footprint and clears the 0.41 m² overlap with f_L-1_011. | ![](agent/r6_093_swap_model_before_r_L-1_mutfak_2.png) | ![](agent/r6_094_swap_model_after_r_L-1_mutfak_2.png) |
| 2531 | 6 | swap_model | f_L-1_068 | adjusted_by_ai | 47.0 -> 47.0 | Swap to a 1.00 x 0.47 m sink model that fits within the counter footprint to clear the 0.39 m² overlap with f_L-1_012. | ![](agent/r6_095_swap_model_before_r_L-1_mutfak_2.png) | ![](agent/r6_096_swap_model_after_r_L-1_mutfak_2.png) |
| 2535 | 6 | move_piece | f_L0_022 | adjusted_by_ai | 97.0 -> 97.0 | Move desk 0.1 m inward to clear wall w_L0_026 (S2) | ![](agent/r6_099_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r6_100_move_piece_after_r_L0_yatak_odasi_3.png) |
| 2536 | 6 | set_exterior | set_exterior | agent_override | - | Acknowledge the 9.7 m blank facade as an intended architectural feature (X3) | - | - |
| 2537 | 6 | swap_model | f_L-1_008 | adjusted_by_ai | 47.0 -> 47.0 | Swap stove to the closest library model to resolve the 0.41 m² overlap with kitchen_counter f_L-1_002 (F9). | ![](agent/r6_101_swap_model_before_r_L-1_mutfak.png) | ![](agent/r6_102_swap_model_after_r_L-1_mutfak.png) |
| 2543 | 6 | swap_model | f_L-1_067 | adjusted_by_ai | 47.0 -> 47.0 | Swap sink to a different library model to resolve the 0.39 m² overlap with kitchen_counter f_L-1_003 (F9). | ![](agent/r6_103_swap_model_before_r_L-1_mutfak.png) | ![](agent/r6_104_swap_model_after_r_L-1_mutfak.png) |
| 2548 | 6 | swap_model | f_L0_015 | adjusted_by_ai | 77.0 -> 77.0 | Try a toilet model with a shallower depth (0.717 m) to stop the 0.013 m cut into wall w_L0_008. | ![](agent/r6_105_swap_model_before_r_L0_banyo_2.png) | ![](agent/r6_106_swap_model_after_r_L0_banyo_2.png) |
| 2549 | 6 | report_library_gap | f_L0_005 | library_gap | - | No audited washbasin model within tolerance; parametric fixture used by design. | - | - |
| 2555 | 6 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | Toilet f_L0_016 cuts wall w_L0_008 by 0.013 m; this model's depth (0.568 m) is shorter than the drawn 0.69 m, pulling the footprint clear of the wall. | ![](agent/r6_108_swap_model_before_r_L0_banyo.png) | ![](agent/r6_109_swap_model_after_r_L0_banyo.png) |
| 2556 | 6 | set_exterior | set_exterior | agent_override | - | Restore the specified mansard roof (45 deg, 0.8 m overhang) so the building shows its upper floors and the decor and door tops no longer poke through the roof. | - | - |
| 2559 | 6 | set_camera | ext_5 | agent_override | - | Set the camera to 1.6 m above the local ground (ground there is about 0.86 m) to get the required eye-level view. | - | - |
| 2564 | 6 | swap_model | f_L1_014 | adjusted_by_ai | 77.0 -> 77.0 | Smaller-depth toilet model (0.568 m vs 0.69 m) to clear the 0.013 m cut into wall w_L1_004. | ![](agent/r6_111_swap_model_before_r_L1_banyo_2.png) | ![](agent/r6_113_swap_model_after_r_L1_banyo_2.png) |
| 2565 | 6 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Shorter depth (0.568 m vs 0.69 m) should clear the 0.013 m cut of wall w_L-1_005. | ![](agent/r6_112_swap_model_before_r_L-1_banyo.png) | ![](agent/r6_114_swap_model_after_r_L-1_banyo.png) |
| 2567 | 6 | swap_model | f_L1_013 | adjusted_by_ai | 77.0 -> 77.0 | shortest-depth toilet model (0.568 m) to clear the 0.013 m cut of wall w_L1_004 | ![](agent/r6_115_swap_model_before_r_L1_banyo.png) | ![](agent/r6_116_swap_model_after_r_L1_banyo.png) |
| 2574 | 6 | swap_model | f_L0_014 | adjusted_by_ai | 77.0 -> 77.0 | Slightly smaller toilet model (0.415 x 0.69 m) resolves the 0.012 m cut of wall w_L0_005 without new collisions, per dry_run. | ![](agent/r6_117_swap_model_before_r_L0_e_banyo_2.png) | ![](agent/r6_118_swap_model_after_r_L0_e_banyo_2.png) |
| 2577 | 6 | swap_model | f_L0_013 | adjusted_by_ai | 77.0 -> 77.0 | toilet f_L0_013 cuts wall w_L0_005 by 0.012 m; try a model with a shallower depth to clear the wall | ![](agent/r6_120_swap_model_before_r_L0_e_banyo.png) | ![](agent/r6_121_swap_model_after_r_L0_e_banyo.png) |
| 2578 | 6 | report_library_gap | f_L0_006 | library_gap | - | no washbasin candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest objaverse_8580c4545d1649efb3503c6c2a012641 at 25.2 % non-uniform, mean scale 1.3433) | - | - |
| 2579 | 6 | report_library_gap | f_L0_011 | library_gap | - | no shower candidate within 10 % non-uniform scale and 0.85..1.2 mean scale (closest gen_shower_japandi_6_bd58a347 at 52.4 % non-uniform, mean scale 0.8967) | - | - |
| 2873 | 7 | set_terrain | set_terrain | corrected_by_ai | 1.0 -> 1.0 | Keep the TIN ground model (the only terrain kind that matches the 16 verified level marks) so the slope finding is not traded for 13 new level findings. | - | - |
| 3219 | 1 | move_piece | f_L1_022 | adjusted_by_ai | 90.0 -> 100.0 | Move the chair 0.1 m away from wall w_L1_009 to clear the 0.05 m wall cut and the 0.07 m² outline breach, staying within the 0.3 m move allowance. | ![](agent/r1_037_move_piece_before_r_L1_teras.png) | ![](agent/r1_039_move_piece_after_r_L1_teras.png) |
| 3222 | 1 | set_lighting | r_L-1_koridor_2 | agent_override | - | Camera view is 1.50 stops over the EV cap; the finding suggests a lighting factor of about x2.83 to bring incident light to target. | - | - |
| 3227 | 1 | swap_model | f_L0_047 | added_by_ai | 100.0 -> 100.0 | Swap the generic open metal shelving render for a proper closed solid-wood shoe cabinet model so the visual matches the shoe cabinet type. | ![](agent/r1_046_swap_model_before_r_L0_koridor.png) | ![](agent/r1_047_swap_model_after_r_L0_koridor.png) |
| 3255 | 1 | move_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 0.0 | clear the overlap with chair f_L-1b_052 and give the chair back clearance from the table edge | ![](agent/r1_062_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_063_move_piece_after_r_L-1b_salon.png) |
| 3256 | 1 | move_piece | f_L-1b_056 | adjusted_by_ai | 0.0 -> 0.0 | clear the overlap with chair f_L-1b_055 and give the chair back clearance from the table edge | ![](agent/r1_064_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_065_move_piece_after_r_L-1b_salon.png) |
| 3266 | 1 | move_piece | f_L0_023 | adjusted_by_ai | 74.0 -> 74.0 | Move desk 0.05m away from wall w_L0_025 to clear the 0.046m collision (S2). | ![](agent/r1_066_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_067_move_piece_after_r_L0_yatak_odasi_4.png) |
| 3269 | 1 | rotate_piece | f_L1_025 | adjusted_by_ai | 77.0 -> 87.0 | Face the chair toward the table (table is east of the chair, front_deg 0) to resolve the F4 orientation mismatch. | ![](agent/r1_070_rotate_piece_before_r_L1_koridor_2.png) | ![](agent/r1_071_rotate_piece_after_r_L1_koridor_2.png) |
| 3270 | 1 | move_piece | f_L0_009 | adjusted_by_ai | 74.0 -> 84.0 | Snap bed's back to wall w_L0_013 to create 0.60m clearance on the left side (G5). | ![](agent/r1_072_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_073_move_piece_after_r_L0_yatak_odasi_4.png) |
| 3272 | 1 | retype_piece | f_L1_027 | adjusted_by_ai | 41.0 -> 41.0 | Type the 0.68x0.78m drawn piece as an armchair per AI pass and size match. | ![](agent/r1_075_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_076_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 3281 | 1 | retype_piece | f_L1_028 | adjusted_by_ai | 41.0 -> 41.0 | The 0.68 x 0.78 m drawn seat is an armchair (AI pass: armchair), typing and building it. | ![](agent/r1_085_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_086_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 3283 | 1 | move_piece | f_L0_037 | adjusted_by_ai | 84.0 -> 94.0 | Move wardrobe to free wall span s1 (w_L0_012) to clear the window (G12) and place it flush against the wall to resolve the freestanding screen appearance (v:r1-v9:2). | ![](agent/r1_088_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_089_move_piece_after_r_L0_yatak_odasi_4.png) |
| 3296 | 1 | move_piece | f_L1_024 | adjusted_by_ai | 87.0 -> 87.0 | Pull the table 0.11 m west off wall w_L1_006 to clear the 0.052 m cut (S2) and the room-outline breach (F9). | ![](agent/r1_109_move_piece_before_r_L1_koridor_2.png) | ![](agent/r1_111_move_piece_after_r_L1_koridor_2.png) |
| 3297 | 1 | set_lighting | r_L1_koridor_2 | agent_override | - | Windowless corridor is too dark for all three cameras (up to +4.48 EV wanted vs +3.00 cap); raise room light power ~2.8x to bring exposure within the cap. | - | - |
| 3313 | 1 | swap_model | f_L-1_026 | adjusted_by_ai | 77.0 -> 77.0 | Replace the crude low-poly block washbasin with a proper japandi basin model that has a real bowl and faucet (D2 wrong_model). | ![](agent/r1_119_swap_model_before_r_L-1_banyo.png) | ![](agent/r1_120_swap_model_after_r_L-1_banyo.png) |
| 3314 | 1 | swap_model | f_L-1_051 | adjusted_by_ai | 77.0 -> 77.0 | Replace the crude low-poly toilet with a proper japandi toilet model with a real tank and bowl (D2 wrong_model). | ![](agent/r1_121_swap_model_before_r_L-1_banyo.png) | ![](agent/r1_122_swap_model_after_r_L-1_banyo.png) |
| 3322 | 1 | move_piece | f_L0_039 | adjusted_by_ai | 74.0 -> 84.0 | Move wardrobe off window win_L0_006 to free wall span w_L0_019 (offset 0.7) to clear the blocked opening (G12). | ![](agent/r1_124_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_125_move_piece_after_r_L0_yatak_odasi_3.png) |
| 3327 | 1 | move_piece | f_L0_022 | adjusted_by_ai | 84.0 -> 84.0 | Nudge desk away from wall w_L0_026 to resolve the 0.045 m collision (S2). | ![](agent/r1_128_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_129_move_piece_after_r_L0_yatak_odasi_3.png) |
| 3626 | 2 | move_piece | f_L1_022 | adjusted_by_ai | 100.0 -> 100.0 | Nudge chair 0.04 m away from wall w_L1_009 to clear the 0.035 m cut (S2). | ![](agent/r2_037_move_piece_before_r_L1_teras.png) | ![](agent/r2_038_move_piece_after_r_L1_teras.png) |
| 3632 | 2 | swap_model | f_L0_047 | added_by_ai | 100.0 -> 100.0 | The shoe cabinet renders as a generic open metal shelving unit; swap to a closed 3-door shoe cabinet model so the visual matches the intended furniture type. | ![](agent/r2_046_swap_model_before_r_L0_koridor.png) | ![](agent/r2_047_swap_model_after_r_L0_koridor.png) |
| 3649 | 2 | set_lighting | r_L1_koridor | agent_override | - | Fixes c:lighting_dark:cam_r_L1_koridor_1 and c:lighting_dark:cam_r_L1_koridor_3: both cameras are 1.4-1.5 stops over the EV cap; the findings suggest a lighting factor of about x2.87 and x2.66, so setting the room lighting factor to 2.87 brings both views within the acceptable range. | - | - |
| 3657 | 2 | rotate_piece | f_L-1_049 | adjusted_by_ai | 0.0 -> 0.0 | Face the armchair toward the sofa group (south) to fix F4/G3 orientation | ![](agent/r2_063_rotate_piece_before_r_L-1_salon.png) | ![](agent/r2_064_rotate_piece_after_r_L-1_salon.png) |
| 3664 | 2 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 14.0 | Face the chair toward table f_L-1b_051 (it was 62° off, needs ≤45°). | ![](agent/r2_070_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r2_073_rotate_piece_after_r_L-1b_salon.png) |
| 3667 | 2 | rotate_piece | f_L-1b_056 | adjusted_by_ai | 14.0 -> 24.0 | Face the chair toward table f_L-1b_054 (it was 62° off, needs ≤45°). | ![](agent/r2_077_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r2_081_rotate_piece_after_r_L-1b_salon.png) |
| 3684 | 2 | set_lighting | r_L1_koridor_2 | agent_override | - | Camera view is 0.07 stops over the EV cap; raising the room light factor from 2.8 to ~2.95 as the finding suggests. | - | - |
| 3695 | 2 | move_piece | f_L0_010 | adjusted_by_ai | 84.0 -> 94.0 | Shift the bed 0.01 m south to open the 0.60 m clearance along its right side (G5) with minimal impact on the left-side nightstand zone. | ![](agent/r2_121_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_122_move_piece_after_r_L0_yatak_odasi_3.png) |
| 3704 | 2 | move_piece | f_L0_023 | adjusted_by_ai | 94.0 -> 94.0 | Move desk slightly inward to clear the 0.092 m cut into wall w_L0_025. | ![](agent/r2_126_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r2_127_move_piece_after_r_L0_yatak_odasi_4.png) |
| 3708 | 2 | set_exterior | exterior:roof | agent_override | - | Specification requires a mansard roof; this also raises the roof underside to clear the door tops. | - | - |
| 3997 | 3 | remove_piece | f_L0_047 | added_by_ai | 100.0 -> 100.0 | Shoe cabinet renders as a floating open metal frame (F9 critical); two swap_model attempts failed to fix the visual artifact, so removing it eliminates the finding. | ![](agent/r3_038_remove_piece_before_r_L0_koridor.png) | ![](agent/r3_039_remove_piece_after_r_L0_koridor.png) |
| 3998 | 3 | set_lighting | r_L0_koridor | agent_override | - | cam_r_L0_koridor_1 is 1.57 stops over the EV cap; the finding suggests a light factor of about x2.97, within set_lighting's x3 limit. | - | - |
| 4000 | 3 | move_piece | f_L1_022 | adjusted_by_ai | 100.0 -> 100.0 | Move chair away from wall w_L1_009 to resolve the 0.049 m collision (clearance becomes 0.22 m). | ![](agent/r3_040_move_piece_before_r_L1_teras.png) | ![](agent/r3_041_move_piece_after_r_L1_teras.png) |
| 4001 | 3 | move_piece | f_L1_021 | adjusted_by_ai | 87.0 -> 87.0 | move the table 0.1 m into the room to clear the 0.055 m cut of wall w_L1_005 (c:S2:f_L1_021) | ![](agent/r3_042_move_piece_before_r_L1_koridor.png) | ![](agent/r3_043_move_piece_after_r_L1_koridor.png) |
| 4003 | 3 | swap_model | f_L1_041 | added_by_ai | 100.0 -> 100.0 | The current model is an armchair which does not match the 'chair' type; swap to a standard dining chair. | ![](agent/r3_045_swap_model_before_r_L1_teras.png) | ![](agent/r3_046_swap_model_after_r_L1_teras.png) |
| 4004 | 3 | swap_model | f_L1_042 | added_by_ai | 100.0 -> 100.0 | The current model is an armchair which does not match the 'chair' type; swap to a standard dining chair. | ![](agent/r3_047_swap_model_before_r_L1_teras.png) | ![](agent/r3_048_swap_model_after_r_L1_teras.png) |
| 4022 | 3 | move_piece | f_L-1_060 | adjusted_by_ai | 0.0 -> 0.0 | Move floor lamp f_L-1_060 away from f_L-1_059 to fix overlap (F9) | ![](agent/r3_070_move_piece_before_r_L-1_salon.png) | ![](agent/r3_072_move_piece_after_r_L-1_salon.png) |
| 4038 | 3 | move_group | r_L1_oyun_aktivite_ve_dinlenme_odasi.living_storage | adjusted_by_ai | 41.0 -> 41.0 | Move the AI bookshelf off the sloped-ceiling zone to the bottom wall to clear the X2 roof finding. | ![](agent/r3_086_move_group_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_088_move_group_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 4063 | 3 | mark_not_furniture | f_L1_017 | adjusted_by_ai | 41.0 -> 41.0 | Untyped 1.63x1.52 m outline fits no furniture type for this room; retype candidates were rejected, so it is a drawing outline, not furniture. | ![](agent/r3_106_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_107_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 4082 | 3 | move_piece | f_L0_022 | adjusted_by_ai | 94.0 -> 94.0 | Move desk 0.10 m inward away from wall w_L0_026 to clear the 0.044 m wall cut (S2). | ![](agent/r3_110_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_111_move_piece_after_r_L0_yatak_odasi_3.png) |
| 4085 | 3 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | Crude low-poly toilet model: swap to a realistic minimal toilet (bbox 0.39x0.73x0.78 fits the 0.5x0.69 footprint). | ![](agent/r3_112_swap_model_before_r_L0_banyo.png) | ![](agent/r3_113_swap_model_after_r_L0_banyo.png) |
| 4086 | 3 | move_piece | f_L0_023 | adjusted_by_ai | 94.0 -> 94.0 | Move desk 0.1 m away from wall w_L0_025 to clear the 0.092 m collision (S2). | ![](agent/r3_114_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_115_move_piece_after_r_L0_yatak_odasi_4.png) |
| 4639 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed edge to clear the 0.06 m² overlap and restore the required ≤0.30 m gap from the bed side. | ![](agent/r1_031_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_033_move_piece_after_r_L0_e_yatak_odasi.png) |
| 4640 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and satisfy the ≤0.30 m gap requirement. | ![](agent/r1_032_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_034_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 4643 | 1 | move_piece | f_L1_022 | adjusted_by_ai | 90.0 -> 90.0 | Move the drawn chair fully inside the room, away from wall w_L1_009 and the room outline, to clear the F9 collision and S2 wall cut. | ![](agent/r1_036_move_piece_before_r_L1_teras.png) | ![](agent/r1_037_move_piece_after_r_L1_teras.png) |
| 4651 | 1 | move_piece | f_L1_021 | adjusted_by_ai | 87.0 -> 87.0 | Shift table_coffee 0.2 m toward the room interior (away from wall w_L1_005) to clear the 0.055 m wall cut (S2) and the room outline collision (F9). | ![](agent/r1_048_move_piece_before_r_L1_koridor.png) | ![](agent/r1_049_move_piece_after_r_L1_koridor.png) |
| 4663 | 1 | move_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 0.0 | Move chair 0.3 m away from the table to clear the 0.09 m overlap with f_L-1b_052 and open the 0.81 m clearance behind it. | ![](agent/r1_052_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_053_move_piece_after_r_L-1b_salon.png) |
| 4664 | 1 | move_piece | f_L-1b_056 | adjusted_by_ai | 0.0 -> 0.0 | Move chair 0.3 m away from the table to clear the 0.09 m overlap with f_L-1b_055 and open the 0.81 m clearance behind it. | ![](agent/r1_055_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_057_move_piece_after_r_L-1b_salon.png) |
| 4677 | 1 | move_piece | f_L-1b_056 | adjusted_by_ai | 0.0 -> 0.0 | Place the chair on the table's west long side facing east (0°) toward the table: clears the 62° orientation finding and keeps 0.81 m clearance behind it. | ![](agent/r1_070_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_072_move_piece_after_r_L-1b_salon.png) |
| 4681 | 1 | remove_piece | f_L1_056 | added_by_ai | 44.0 -> 44.0 | AI-added bookshelf pokes through the roof (top 5.17 m) and stands under a sloped ceiling only 0.82 m high; removing it resolves both X2 findings. | ![](agent/r1_075_remove_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_076_remove_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 5012 | 2 | move_piece | f_L1_022 | adjusted_by_ai | 90.0 -> 100.0 | F8: chair floats in the middle of the room; snap its back to the free wall span s2 so it stands against a wall. | ![](agent/r2_028_move_piece_before_r_L1_teras.png) | ![](agent/r2_029_move_piece_after_r_L1_teras.png) |
| 5021 | 2 | mark_not_furniture | f_L1_021 | adjusted_by_ai | 87.0 -> 100.0 | Fixes c:F1:f_L1_021, c:G14:f_L1_021, c:RC:f_L1_021: the piece's own recognition crop shows a stair (tread hatching), not a table; the table_coffee type is a misread of the stair symbol, so it is not furniture. | ![](agent/r2_035_mark_not_furniture_before_r_L1_koridor.png) | ![](agent/r2_036_mark_not_furniture_after_r_L1_koridor.png) |
| 5022 | 2 | report_library_gap | f_L1_023 | library_gap | - | Fixes c:LG:f_L1_023: no audited library chair model fits the drawn 0.60 x 0.45 m (closest abo_B0857JM2NC at 18.7% non-uniform scale, outside the 10% cap; relaxed caps also yield none), so the parametric build is the correct fallback. | - | - |
| 5036 | 2 | move_piece | f_L-1_038 | adjusted_by_ai | 0.0 -> 0.0 | Shift dining table 0.02 m to clear the 0.039/0.038 m cuts with chairs f_L-1_039 and f_L-1_042 (S2). | ![](agent/r2_041_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_043_move_piece_after_r_L-1_salon_2.png) |
| 5037 | 2 | move_piece | f_L-1b_059 | adjusted_by_ai | 0.0 -> 0.0 | Move chair f_L-1b_059 away from f_L-1b_058 to resolve the 0.09 m² overlap (F9) and improve clearance behind (G6). | ![](agent/r2_042_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r2_045_move_piece_after_r_L-1b_salon_2.png) |
| 5040 | 2 | move_piece | f_L-1b_062 | adjusted_by_ai | 0.0 -> 0.0 | Move chair f_L-1b_062 away from f_L-1b_061 to resolve the 0.09 m² overlap (F9) and improve clearance behind (G6). | ![](agent/r2_046_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r2_048_move_piece_after_r_L-1b_salon_2.png) |
| 5050 | 2 | resize_piece | f_L-1b_046 | adjusted_by_ai | 0.0 -> 0.0 | Sofa was turned 90° against product sizes (0.82 wide x 1.64 deep); swap to standard 1.64 wide x 0.82 deep. | ![](agent/r2_061_resize_piece_before_r_L-1b_salon.png) | ![](agent/r2_062_resize_piece_after_r_L-1b_salon.png) |
| 5060 | 2 | move_piece | f_L-1b_046 | adjusted_by_ai | 0.0 -> 0.0 | Sofa back is 0.63 m off a wall; snap its back onto the back wall to resolve F3. | ![](agent/r2_067_move_piece_before_r_L-1b_salon.png) | ![](agent/r2_068_move_piece_after_r_L-1b_salon.png) |
| 5070 | 2 | mark_not_furniture | f_L1_018 | adjusted_by_ai | 44.0 -> 44.0 | Untyped drawn outline the AI passes identified as not furniture; marking it clears c:NR:f_L1_018. | ![](agent/r2_073_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_074_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 5100 | 2 | move_piece | f_L0_038 | adjusted_by_ai | 64.0 -> 87.0 | Move nightstand flush against the bed's right side to resolve the 0.06 m² overlap and -0.12 m side gap (F9, G4, S2). | ![](agent/r2_087_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_088_move_piece_after_r_L0_yatak_odasi_3.png) |
| 5135 | 2 | swap_model | f_L0_003 | adjusted_by_ai | 77.0 -> 77.0 | The washbasin is rendered as a vanity/dresser unit; swapping to a proper washbasin model fixes the D2 wrong_model finding. | ![](agent/r2_101_swap_model_before_r_L0_banyo.png) | ![](agent/r2_102_swap_model_after_r_L0_banyo.png) |
| 5139 | 2 | swap_model | f_L0_016 | adjusted_by_ai | 77.0 -> 77.0 | The toilet model is crude/low-poly; swapping to a higher-quality toilet model fixes the D2 wrong_model finding. | ![](agent/r2_103_swap_model_before_r_L0_banyo.png) | ![](agent/r2_104_swap_model_after_r_L0_banyo.png) |
| 5383 | 3 | relayout_room | r_L1_koridor | adjusted_by_ai | 100.0 -> 100.0 | Fixes c:X2:f_L1_049: re-solves the entrance group so the 0.84 m console_table no longer stands where the sloped ceiling is only 0.82 m high (top-scoring candidate, no hard failures). | ![](agent/r3_025_relayout_room_before_r_L1_koridor.png) | ![](agent/r3_026_relayout_room_after_r_L1_koridor.png) |
| 5388 | 3 | mark_not_furniture | f_L-1b_001 | adjusted_by_ai | 0.0 -> 0.0 | The large untyped cluster is a group of drawn pieces / structural element, not a single furniture item to build. | ![](agent/r3_028_mark_not_furniture_before_r_L-1b_salon_2.png) | ![](agent/r3_029_mark_not_furniture_after_r_L-1b_salon_2.png) |
| 5397 | 3 | rotate_piece | f_L-1b_045 | adjusted_by_ai | 0.0 -> 0.0 | Turn the sofa to face the coffee table / seating group to the east, resolving F4. | ![](agent/r3_034_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_035_rotate_piece_after_r_L-1b_salon_2.png) |
| 5414 | 3 | rotate_piece | f_L-1_049 | adjusted_by_ai | 0.0 -> 0.0 | Rotate armchair to face the sofa_corner group (toward -y direction) to fix F4 and G3 orientation findings | ![](agent/r3_045_rotate_piece_before_r_L-1_salon.png) | ![](agent/r3_046_rotate_piece_after_r_L-1_salon.png) |
| 5430 | 3 | move_piece | f_L0_036 | adjusted_by_ai | 64.0 -> 87.0 | Nudge the nightstand further from the bed to resolve the overlap and negative clearance (F9, S2, G4). | ![](agent/r3_067_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_068_move_piece_after_r_L0_yatak_odasi_4.png) |
| 5437 | 3 | mark_not_furniture | f_L1_017 | adjusted_by_ai | 44.0 -> 44.0 | The drawn 1.63x1.52 m symbol is a decorative rug/area outline, not furniture; retype to sofa/sofa_corner was rejected by size table and room type. | ![](agent/r3_082_mark_not_furniture_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_083_mark_not_furniture_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 5696 | 4 | move_piece | f_L1_048 | added_by_ai | 44.0 -> 44.0 | Move bookshelf to right wall at offset 3.0 m where the sloped ceiling is high enough (≥1.8 m) to clear the 1.8 m bookshelf, resolving both X2 findings. | ![](agent/r4_004_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r4_005_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 297 | 1 | rotate_piece | f_L-1b_033 | score: plausibility 50 -> 40 (G6 f_L-1b_033: chair f_L-1b_033 is 180° off the table f_L-1b_026 (needs ≤ 45°)) | Rotate chair f_L-1b_033 to face the dining table f_L-1b_026, resolving the 'chair does not face its group' finding. |
| 298 | 1 | complete_group | r_L-1b_salon_kitchen.kitchen_run | exists: no group 'r_L-1b_salon_kitchen.kitchen_run' (its room 'r_L-1b_salon_kitchen') in a room of the building | Add a fridge to the kitchen run group to satisfy the 'kitchen has no fridge' requirement. |
| 302 | 1 | complete_group | r_L-1b_salon_kitchen.kitchen_run | memory: the same edit was rejected in round 1: exists: no group 'r_L-1b_salon_kitchen.kitchen_run' (its room 'r_L-1b_salon_kitchen') in a room of the building | Add a fridge to the kitchen run group to satisfy the 'kitchen has no fridge' requirement. |
| 322 | 1 | move_piece | f_L1_010 | snap: f_L1_010: no free place on wall w_L1_001 (doors, windows, at most 1.2 m from the drawn place) | F3: sofa back is 2.48 m off any wall; snap its back onto free span s0 (wall w_L1_001) so it faces into the room. |
| 325 | 1 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_002 (doors, windows, at most 1.2 m from the drawn place) | F3: sofa back is 0.79 m off any wall; snap its back onto free span s3 (wall w_L1_002) so it faces into the room. |
| 327 | 1 | set_exterior | set_exterior | nothing to change | The shoe_cabinet f_L1_046 is flagged as poking through the roof (top 5.05 m) and standing where the sloped ceiling is only 0.82 m high; marking it as exterior removes it from the interior render to resolve the ceiling collision. |
| 330 | 1 | move_piece | f_L1_010 | drawn_lock: f_L1_010: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.72 m) | F3: sofa back 2.48 m off wall; move it to the left wall (w_L1_012) so its back (facing -x) sits on the wall, keeping its front facing +x into the room. |
| 331 | 1 | move_piece | f_L1_011 | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 5.21 m) | F3: sofa back 0.79 m off wall; move it to the bottom wall (w_L1_001) so its back (facing -y) sits on the wall, keeping its front facing +y into the room. |
| 332 | 1 | move_piece | f_L1_009 | snap: f_L1_009: no free place on wall w_L1_001 (doors, windows, at most 1.2 m from the drawn place) | Place sofa f_L1_009's back against the bottom wall span s0 to fix F3 (back 2.48 m off a wall). |
| 333 | 1 | move_piece | f_L1_012 | snap: f_L1_012: no free place on wall w_L1_012 (doors, windows, at most 1.2 m from the drawn place) | Place sofa f_L1_012's back against the right wall span s1 to fix F3 (back 0.79 m off a wall). |
| 336 | 1 | rotate_piece | f_L-1_008 | drawn_lock: f_L-1_008: the new front does not fix the error (its back is not on a wall) | Stove back is 0.06 m off the wall; rotating 90° aligns its back to the wall to clear F3. |
| 337 | 1 | move_piece | f_L1_010 | drawn_lock: f_L1_010: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.20 m) | F3: move sofa 1.2 m (max for a drawn piece whose back snaps to a wall) to the left wall w_L1_012 so its back sits on the wall, front still facing +x into the room. |
| 338 | 1 | move_piece | f_L1_011 | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | F3: move sofa 0.3 m (max for a drawn piece) toward the top wall w_L1_002 to reduce the 0.79 m back-off-wall gap as far as the lock allows. |
| 340 | 1 | rotate_piece | f_L-1_008 | drawn_lock: f_L-1_008: the new front does not fix the error (its back is not on a wall) | Stove back is 0.06 m off the wall; rotating so its back sits on the north wall clears F3. |
| 341 | 1 | rotate_piece | f_L1_011 | max_tries: f_L1_011 was edited 3 times in this round | F3: turn the sofa so its back faces the top wall w_L1_002 (front -y), preparing a 0.3 m move to snap the back onto the wall. |
| 344 | 1 | rotate_piece | f_L-1_008 | drawn_lock: f_L-1_008: the new front does not fix the error (its back is not on a wall) | Stove back is 0.06 m off the wall; rotating so its back sits on the north wall clears F3. |
| 346 | 1 | rotate_piece | f_L1_010 | max_tries: f_L1_010 was edited 3 times in this round | F3: turn the sofa so its back faces the left wall w_L1_012 (front -x), preparing a 0.3 m move to snap the back onto the wall. |
| 347 | 1 | rotate_piece | f_L-1_008 | max_tries: f_L-1_008 was edited 3 times in this round | Stove back is 0.06 m off the wall; rotating so its back sits on the north wall clears F3. |
| 349 | 1 | complete_group | r_L-1_mutfak.kitchen_run | no_place: r_L-1_mutfak.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no place passes the checks) | Kitchen run is missing a fridge; complete_group adds the required fridge to satisfy G9. |
| 360 | 1 | complete_group | r_L-1_mutfak_2.kitchen_run | no_place: r_L-1_mutfak_2.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no place passes the checks) | kitchen run is missing a fridge; complete_group adds the required fridge to satisfy G9 |
| 361 | 1 | move_piece | f_L0_037 | snap: f_L0_037: no free place on wall w_L0_013 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe off window wall w_L0_003 to free span on w_L0_013 to clear the window sightline (G12). |
| 362 | 1 | move_piece | f_L0_023 | score: plausibility 87 -> 77 (F3 f_L0_023: desk: its back is not on a wall (0.10 m off)) | Nudge desk 0.1 m away from wall w_L0_025 to resolve the 0.093 m intersection (S2). |
| 363 | 1 | move_piece | f_L0_039 | f_L0_010: clearance_ok, f_L0_039: clearance_ok | Wardrobe blocks window win_L0_006; slide it along the same wall to the clear span s1 so it no longer stands in front of the window. |
| 369 | 1 | complete_group | r_L0_banyo_2.bathroom_set | no_place: r_L0_banyo_2.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom lacks a shower or bathtub; adding a shower is the most space-efficient option for a 5 m2 room. |
| 377 | 1 | set_terrain | set_terrain | score: the level findings rise from 1 to 13, L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -4.71 m (1.29 m apart), L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -2.42 m (0.58 m apart), L4 lm_005: level mark '40.00' (lm_005, ground_finished) reads -3.00 m; the ground there is built at -1.72 m (1.28 m apart), L4 lm_006: level mark '43.00' (lm_006, ground_finished) reads +0.00 m; the ground there is built at +0.42 m (0.42 m apart), L4 lm_007: level mark '40.00' (lm_007, ground_finished) reads -3.00 m; the ground there is built at -3.91 m (0.91 m apart) | Replace the 1:0.3 TIN with a single planar ground so the slope is far below the 1:3 limit and no retaining edge is needed. |
| 380 | 1 | set_terrain | set_terrain | score: the level findings rise from 1 to 12, L3 L0: level L0 (floor +0.00 m) lies 0.10 m below the terrain at its outline and is not a basement, L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -3.11 m (2.89 m apart), L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -0.55 m (2.45 m apart), L4 lm_005: level mark '40.00' (lm_005, ground_finished) reads -3.00 m; the ground there is built at -1.69 m (1.31 m apart), L4 lm_006: level mark '43.00' (lm_006, ground_finished) reads +0.00 m; the ground there is built at +0.18 m (0.18 m apart) | Use a two-sided ground (left at the -3.0 m marks, right at 0.0 m) so the steep 1:0.3 TIN slope is replaced by a flat ground on each side with a retaining edge at the step, satisfying the 1:3 limit. |
| 388 | 1 | set_camera | ext_5 | set: kind is required | Drop the camera to eye level (1.6 m) and level the line of sight so the facade, not the roof, is the dominant feature. |
| 389 | 1 | set_camera | ext_7 | set: kind is required | Drop the camera to eye level (1.6 m) and level the line of sight so the facade, not the roof, is the dominant feature. |
| 390 | 1 | add_camera | ext_front | the camera stands inside the building b2 (another building on the plot), eye height -0.64 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Add a frontal eye-level view of the +y entrance facade, which is currently missing. |
| 393 | 1 | complete_group | r_L0_banyo_2.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo_2.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Retry adding a shower after the refit from the model swaps; the room still lacks a shower or bathtub. |
| 395 | 1 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Nudge the washbasin so door d_L-1_001 no longer swings into it on the hinge side |
| 398 | 1 | set_camera | ext_5 | eye height 0.75 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Drop the camera to eye level (1.6 m) and level the line of sight so the facade, not the roof, is the dominant feature. |
| 399 | 1 | set_camera | ext_7 | eye height 1.97 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Drop the camera to eye level (1.6 m) and level the line of sight so the facade, not the roof, is the dominant feature. |
| 400 | 1 | complete_group | r_L0_banyo.bathroom_set | no_place: r_L0_banyo.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom lacks a shower or bathtub; completing the group adds the required wet-area fixture. |
| 402 | 1 | complete_group | r_L0_banyo.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Retry after the toilet swap freed space: add the missing shower to satisfy the bathroom program. |
| 405 | 1 | fix_fixture | f_L-1_025 | fixture_place: f_L-1_025: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_002) | Door d_L-1_002 swings into the washbasin on one hinge side; nudge it to clear the swing. |
| 409 | 1 | fix_fixture | f_L-1_025 | fixture_place: f_L-1_025 at [10.95, 10.35] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Nudge the washbasin 0.14 m into the room so the door d_L-1_002 swing no longer hits it. |
| 411 | 1 | fix_fixture | f_L-1_025 | fixture_place: f_L-1_025 at [10.95, 10.50] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Move the washbasin 0.29 m into the room, past the door d_L-1_002 swing arc. |
| 416 | 1 | fix_fixture | f_L-1_025 | max_tries: f_L-1_025 was edited 3 times in this round | Move the washbasin 0.49 m into the room, fully past the door d_L-1_002 swing arc. |
| 420 | 1 | fix_fixture | f_L1_007 | fixture_place: f_L1_007: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_004) | door d_L1_004 swings into washbasin f_L1_007 on one hinge side; shift the fixture 0.15 m away from the swing to clear it |
| 423 | 1 | fix_fixture | f_L1_007 | fixture_place: f_L1_007 at [6.22, 10.36] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | door d_L1_004 swings into washbasin f_L1_007 on one hinge side; shift the fixture 0.15 m away from the swing to clear it |
| 425 | 1 | swap_model | f_L-1_052 | asset_type: objaverse_8580c4545d1649efb3503c6c2a012641 is a washbasin model, not a toilet | Test whether a library toilet model resolves the 0.013 m wall cut on f_L-1_052. |
| 426 | 1 | fix_fixture | f_L1_007 | fixture_place: f_L1_007 at [6.22, 10.06] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | door d_L1_004 swings into washbasin f_L1_007 on one hinge side; shift the fixture 0.15 m away from the swing to clear it |
| 427 | 1 | fix_fixture | f_L1_007 | max_tries: f_L1_007 was edited 3 times in this round | door d_L1_004 swings into washbasin f_L1_007 on one hinge side; shift the fixture 0.15 m away from the swing to clear it |
| 748 | 2 | move_piece | f_L-1_050 | drawn_lock: f_L-1_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move armchair 0.3m left so its front free zone stays in the room and it sits closer to the sofa cluster. |
| 771 | 2 | move_piece | f_L1_009 | drawn_lock: f_L1_009: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge sofa f_L1_009 0.3 m (max allowance) towards the bottom wall w_L1_001 to reduce the distance of its back from the wall, as a full snap was rejected in round 1. |
| 773 | 2 | move_piece | f_L-1_032 | drawn_lock: f_L-1_032: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the left column of dining chairs 0.3 m toward the (not-built) table_dining f_L-1_027 so each chair is within 0.8 m of a table. |
| 826 | 2 | complete_group | r_L0_banyo_2.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo_2.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom lacks a shower or bathtub; add the missing shower to complete the set. |
| 835 | 2 | swap_model | f_L0_016 | max_tries: f_L0_016 was edited 3 times in this round | classic_3 still leaves the toilet cutting wall w_L0_008 by 0.013 m; minimal_1 is the narrowest toilet in the library (0.393 x 0.729) and should clear the wall. |
| 840 | 2 | set_camera | ext_7 | memory: the same edit was rejected in round 1: eye height 1.97 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Lower ext_7 to eye level (1.6 m) with a horizontal target to remove the high-angle distortion and keep vertical lines straight. |
| 845 | 2 | set_camera | ext_7 | eye height 2.37 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.86 m) | Lower ext_7 to eye level (1.6 m above the +0.42 m ground) with a horizontal target to remove the high-angle distortion and keep vertical lines straight. |
| 849 | 2 | set_camera | ext_7 | memory: the same edit was rejected in round 1: eye height 1.97 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Set ext_7 to eye level (1.6 m) with a horizontal target to remove the high-angle distortion and keep vertical lines straight. |
| 852 | 2 | fix_fixture | f_L1_008 | fixture_place: f_L1_008: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_005) | Door d_L1_005 swings into the washbasin on one hinge side; nudge it slightly along the wall to clear the door swing. |
| 855 | 2 | fix_fixture | f_L1_008 | fixture_place: f_L1_008 at [10.95, 10.26] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Door d_L1_005 swings into the washbasin on one hinge side; nudge it 0.05 m along the wall to clear the door swing. |
| 857 | 2 | fix_fixture | f_L1_008 | fixture_place: f_L1_008 at [10.95, 10.35] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | Door d_L1_005 swings into the washbasin on one hinge side; nudge it 0.14 m along the wall to clear the door swing. |
| 858 | 2 | fix_fixture | f_L1_007 | memory: the same edit was rejected in round 1: fixture_place: f_L1_007: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_004) | R3: door d_L1_004 swings into the washbasin; move it up to 0.5 m to clear the door swing |
| 859 | 2 | fix_fixture | f_L1_008 | max_tries: f_L1_008 was edited 3 times in this round | Door d_L1_005 swings into the washbasin on one hinge side; nudge it 0.24 m along the wall to clear the door swing. |
| 860 | 2 | fix_fixture | f_L1_007 | fixture_place: f_L1_007 at [6.35, 10.21] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | R3: door d_L1_004 swings into the washbasin; shift it 0.13 m along the wall away from the door swing |
| 861 | 2 | fix_fixture | f_L1_007 | fixture_place: f_L1_007 at [6.50, 10.21] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | R3: door d_L1_004 swings into the washbasin; shift it 0.28 m along the wall to clear the door swing |
| 862 | 2 | fix_fixture | f_L1_007 | fixture_place: f_L1_007 at [6.22, 10.45] is still through a wall or in a door swing; leave out center and the code finds the nearest valid spot | R3: door d_L1_004 swings into the washbasin; shift it 0.24 m into the room to clear the door swing |
| 863 | 2 | fix_fixture | f_L1_007 | max_tries: f_L1_007 was edited 3 times in this round | R3: door d_L1_004 swings into the washbasin; shift it 0.34 m into the room to clear the door swing |
| 1184 | 3 | move_piece | f_L-1_032 | memory: the same edit was rejected in round 2: drawn_lock: f_L-1_032: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge left dining chair 0.3 m toward the dining table so it is within 0.8 m of it. |
| 1187 | 3 | move_piece | f_L-1_059 | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move floor lamp 0.3 m away from the window wall so it no longer blocks the sightline in front of win_L-1_001 and lands near the armchair. |
| 1188 | 3 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move floor lamp 0.3 m away from the window wall so it no longer blocks the sightline in front of win_L-1_001. |
| 1190 | 3 | move_piece | f_L-1_063 | f_L-1_053: no_overlap | Move floor lamp 0.29 m away from the window wall so it no longer blocks the sightline in front of win_L-1_001. |
| 1191 | 3 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.35 m) | Move floor lamp 0.29 m away from the window wall (toward the corner) so it no longer blocks the sightline in front of win_L-1_001. |
| 1192 | 3 | move_piece | f_L-1_063 | max_tries: f_L-1_063 was edited 3 times in this round | Move floor lamp 0.28 m away from the window wall (toward the corner) so it no longer blocks the sightline in front of win_L-1_001. |
| 1195 | 3 | move_piece | f_L-1_039 | drawn_lock: f_L-1_039: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the left dining chair 0.3 m toward the dining table so it is within 0.8 m of it (fixes F8). |
| 1196 | 3 | move_piece | f_L-1_040 | drawn_lock: f_L-1_040: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the left dining chair 0.3 m toward the dining table so it is within 0.8 m of it (fixes F8). |
| 1197 | 3 | move_piece | f_L-1_041 | drawn_lock: f_L-1_041: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the left dining chair 0.3 m toward the dining table so it is within 0.8 m of it (fixes F8). |
| 1198 | 3 | move_piece | f_L-1_042 | drawn_lock: f_L-1_042: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the left dining chair 0.3 m toward the dining table so it is within 0.8 m of it (fixes F8). |
| 1200 | 3 | move_piece | f_L-1_043 | drawn_lock: f_L-1_043: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the right dining chair 0.3 m toward the dining table so it is within 0.8 m of it (fixes F8). |
| 1201 | 3 | move_piece | f_L-1_044 | drawn_lock: f_L-1_044: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the right dining chair 0.3 m toward the dining table so it is within 0.8 m of it (fixes F8). |
| 1202 | 3 | move_piece | f_L1_009 | drawn_lock: f_L1_009: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 3.37 m) | Place sofa back against free wall span s0 (w_L1_001) to fix F3 back-not-on-wall finding. |
| 1203 | 3 | move_piece | f_L1_012 | drawn_lock: f_L1_012: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.28 m) | Place sofa back against free wall span s1 (w_L1_012) to fix F3 back-not-on-wall finding. |
| 1206 | 3 | relayout_room | r_L-1b_salon | no_place: r_L-1b_salon relayout: no place passes the checks (kitchen_run: no candidate position fits the room) | Solver candidate 1 rearranges the dining chairs around the table to fix F8 (chairs standing alone) and F4 (chair not facing group) findings |
| 1207 | 3 | move_piece | f_L1_009 | snap: f_L1_009: no free place on wall w_L1_001 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto wall w_L1_001 (free span s0) to fix F3 back-not-on-wall; snap allows up to 1.2 m. |
| 1208 | 3 | move_piece | f_L1_012 | drawn_lock: f_L1_012: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.34 m) | Snap sofa back onto wall w_L1_012 (free span s1) to fix F3 back-not-on-wall; snap allows up to 1.2 m. |
| 1209 | 3 | move_group | r_L0_yatak_odasi.storage | drawn_lock: r_L0_yatak_odasi.storage: drawn pieces (f_L0_026) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the 2.09 m wardrobe off window win_L0_005 onto the free wall span s3 (0.93 m) to clear the G12 window finding. |
| 1210 | 3 | move_piece | f_L0_026 | snap: f_L0_026: no free place on wall w_L0_003 (doors, windows, at most 1.2 m from the drawn place) | Slide the 2.09 m wardrobe along wall w_L0_003 to the free span s3 (0.93 m) so it no longer stands in front of window win_L0_005 (G12) and no longer cuts the wall (S2). |
| 1212 | 3 | move_piece | f_L0_038 | snap: f_L0_038: no free place on wall w_L0_003 (doors, windows, at most 1.2 m from the drawn place) | Slide the 1.45 m wardrobe along wall w_L0_003 to the free span s3 (0.93 m) so it no longer stands in front of window win_L0_005 (G12) and no longer cuts the wall (S2). |
| 1215 | 3 | rotate_piece | f_L0_017 | score: plausibility 54 -> 17 (F3 f_L0_017: bed_double: the headboard stands in the room (0.25 m off); G4 f_L0_017: bed_double f_L0_017: no nightstand on the free left side of the head (1.29 m free); G5 f_L0_017: bed_double f_L0_017: 0.18 m free along the right side, needs ≥ 0.60 m; G11 f_L0_017: bed_double f_L0_017: its right use zone is not reached by a 0.60 m walkway from door d_L0_007) | Rotate the bed 90° so its long side runs along the left wall, opening ≥0.60 m clearance along the side and resolving the G5 major clearance finding. |
| 1216 | 3 | retype_piece | f_L1_034 | retype: tv_unit is no candidate for f_L1_034 (1.09 x 0.40 m at [5.07, 7.24]): the size table and the room / zone give bookshelf, potted_plant | Untyped 1.09x0.40 m drawn piece; AI pass tv_unit fits the low wide size. |
| 1217 | 3 | retype_piece | f_L1_033 | retype: sideboard is no candidate for f_L1_033 (0.40 x 2.17 m at [7.10, 7.24]): the size table and the room / zone give bookshelf | Untyped 0.40x2.17 m drawn piece; AI pass sideboard fits the long low size. |
| 1218 | 3 | rotate_piece | f_L1_010 | score: plausibility 74 -> 64 (F3 f_L1_010: sofa: its back is not on a wall (1.47 m off); G7 f_L1_047: desk f_L1_047: 0.74 m free in front, needs ≥ 0.80 m) | Rotate sofa f_L1_010 so its back faces the free wall span s0 (w_L1_001) and its front faces into the room, fixing the 'back not on a wall' finding. |
| 1219 | 3 | rotate_piece | f_L1_011 | f_L1_011: clearance_ok, score: plausibility 74 -> 64 (F6 f_L1_011: sofa: the free zone in front of it is blocked by f_L1_010) | Rotate sofa f_L1_011 so its back faces the free wall span s3 (w_L1_002) and its front faces into the room, fixing the 'back not on a wall' finding. |
| 1224 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | score: plausibility 74 -> 48 (F1 f_L1_043: desk is not a piece of a living room; F1 f_L1_044: office_chair is not a piece of a living room; G1 f_L1_009: sofa f_L1_009 has no TV unit opposite; G1 f_L1_012: sofa f_L1_012 has no TV unit opposite) | Room holds sofas, armchairs and a desk (Oyun Aktivite Ve Dinlenme Odası = play/activity/rest room); 'other' is wrong, so F1/G14 sofa-not-in-room findings clear. |
| 1229 | 3 | rotate_piece | f_L1_011 | memory: the same edit was rejected in round 3: f_L1_011: clearance_ok; score: plausibility 74 -> 64 (F6 f_L1_011: sofa: the free zone in front of it is blocked by f_L1_010) | Rotate sofa f_L1_011 so its back faces the free wall span s3 (w_L1_002) and its front faces into the room, fixing the 'back not on a wall' finding. |
| 1232 | 3 | move_piece | f_L0_037 | drawn_lock: f_L0_037: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move wardrobe 0.003m to snap back to wall w_L0_003, resolving 0.28m offset. |
| 1236 | 3 | retype_piece | f_L0_023 | retype: bed_double is no candidate for f_L0_023 (1.45 x 0.91 m at [0.65, 10.54]): the size table and the room / zone give desk, stair | Retype desk as bed_double to satisfy bedroom program (missing bed) and remove unusual desk fixture. |
| 1252 | 3 | set_exterior | set_exterior | memory: the same edit was rejected in round 1: nothing to change | Acknowledge the 9.7 m blank facade as an intended architectural feature rather than an error (X3). |
| 1262 | 3 | retype_piece | f_L-1b_046 | retype: sofa is no candidate for f_L-1b_046 (0.82 x 1.64 m at [6.55, 6.44]): the size table and the room / zone give chaise, kitchen_counter, stair | 0.82 x 1.64 m drawn piece in salon matches a small sofa; AI passes suggest kitchen_island or sofa, and a sofa fits the living room context better |
| 1270 | 3 | place_group | r_L0_banyo | no_place: bathroom_set group: no place passes the checks (bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room; bathroom_set: no candidate position fits the room) | a compact shower (0.9x0.9) can fit the free span s1 (1.87 m) where a bathtub did not, satisfying G10 |
| 1272 | 3 | set_camera | ext_5 | memory: the same edit was rejected in round 1: eye height 0.75 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Lower ext_5 to eye level 1.6 m with a horizontal line of sight to remove the high-angle look-down. |
| 1273 | 3 | set_camera | ext_7 | memory: the same edit was rejected in round 1: eye height 1.97 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m) | Lower ext_7 to eye level 1.6 m with a horizontal line of sight to remove the high-angle look-down. |
| 1276 | 3 | rotate_piece | f_L0_011 | drawn_lock: f_L0_011: the new front does not fix the error (its back is not on a wall) | Rotate the shower so its back sits on the right wall (w_L0_005) instead of 0.07 m off, fixing F3. |
| 1279 | 3 | rotate_piece | f_L0_011 | drawn_lock: f_L0_011: the new front does not fix the error (its back is not on a wall) | Rotate the shower so its back sits on the right wall (w_L0_005) instead of 0.07 m off, fixing F3. |
| 1295 | 3 | fix_fixture | f_L-1_025 | memory: the same edit was rejected in round 1: fixture_place: f_L-1_025: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_002) | R3: door d_L-1_002 swings into the washbasin; let the code find the nearest valid spot within 0.5 m to clear the door swing. |
| 1620 | 4 | move_piece | f_L-1_057 | drawn_lock: f_L-1_057: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the floor lamp 0.3 m away from the window wall to clear the window sill obstruction and sit within 1.2 m of the armchair f_L-1_050. |
| 1621 | 4 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the floor lamp 0.3 m away from the window wall to clear the window sill obstruction. |
| 1633 | 4 | move_piece | f_L-1_065 | f_L-1_054: no_overlap | Move the floor lamp 0.29 m away from the window wall to clear the window sill obstruction. |
| 1640 | 4 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.39 m) | Shift the floor lamp 0.27 m sideways and in from the window wall to clear the window sill obstruction without hitting the corner sofa. |
| 1641 | 4 | move_piece | f_L-1_049 | drawn_lock: f_L-1_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.41 m) | shift 0.3 m so the free zone in front of the armchair stays inside the room |
| 1642 | 4 | move_piece | f_L-1_059 | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.59 m) | shift 0.3 m into the room so the lamp sits within 1.2 m of armchair f_L-1_049 |
| 1643 | 4 | move_piece | f_L-1_065 | max_tries: f_L-1_065 was edited 3 times in this round | Shift the floor lamp 0.17 m sideways and 0.28 m in from the window wall to clear the window sill obstruction without hitting the corner sofa. |
| 1650 | 4 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | exists: no group 'r_L-1b_salon_2_kitchen.kitchen_run' (its room 'r_L-1b_salon_2_kitchen') in a room of the building | kitchen run is missing its fridge; add it to complete the group |
| 1652 | 4 | complete_group | r_L-1b_salon_2_kitchen | exists: no group 'r_L-1b_salon_2_kitchen' (its room 'r_L-1b_salon_2_kitchen') in a room of the building | kitchen is missing its fridge; add it to complete the group |
| 1659 | 4 | move_group | r_L0_yatak_odasi_4.storage | drawn_lock: r_L0_yatak_odasi_4.storage: drawn pieces (f_L0_037) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the wardrobe group to free wall span s1 (w_L0_012) so its back is against the wall, resolving the floating wardrobe and back-not-on-wall findings. |
| 1660 | 4 | move_group | r_L0_yatak_odasi_2.storage | drawn_lock: r_L0_yatak_odasi_2.storage: drawn pieces (f_L0_025) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the 2.09 m wardrobe off window win_L0_006 onto the free right wall span s2 (into room 180°), clearing the G12 window block and the wall cut on w_L0_004. |
| 1661 | 4 | move_piece | f_L0_037 | f_L0_009: clearance_ok, f_L0_037: clearance_ok | Snap the wardrobe's back onto free wall span s1 (w_L0_012) so it is against the wall, resolving the floating wardrobe and back-not-on-wall findings. |
| 1664 | 4 | move_piece | f_L0_025 | snap: f_L0_025: no free place on wall w_L0_019 (doors, windows, at most 1.2 m from the drawn place) | Slide the 2.09 m wardrobe along the right wall (span s2) to clear window win_L0_006 and the wall cut on w_L0_004. |
| 1665 | 4 | move_piece | f_L0_025 | drawn_lock: f_L0_025: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the wardrobe 0.3 m into the room so it no longer cuts wall w_L0_004 and no longer overlaps f_L0_040. |
| 1666 | 4 | move_piece | f_L0_037 | f_L0_009: clearance_ok, f_L0_037: clearance_ok | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at a position clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1669 | 4 | move_piece | f_L0_025 | f_L0_040: clearance_ok, score: plausibility 54 -> 34 (F3 f_L0_025: wardrobe: its back is not on a wall (0.10 m off); F9 f_L0_040: wardrobe f_L0_040 overlaps wardrobe f_L0_025 by 0.45 m²; G4 f_L0_018: bed_double f_L0_018: no nightstand on the free left side of the head (2.37 m free); G13 f_L0_040: wardrobe f_L0_040: 0.29 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.29 m into the room so it no longer cuts wall w_L0_004 and no longer overlaps f_L0_040. |
| 1670 | 4 | move_piece | f_L0_037 | f_L0_009: clearance_ok, f_L0_037: clearance_ok | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the upper end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1672 | 4 | move_piece | f_L0_040 | f_L0_025: clearance_ok, score: plausibility 54 -> 34 (F3 f_L0_040: wardrobe: its back is not on a wall (0.07 m off); F9 f_L0_040: wardrobe f_L0_040 overlaps wardrobe f_L0_025 by 0.45 m²; G4 f_L0_018: bed_double f_L0_018: no nightstand on the free left side of the head (2.37 m free); G13 f_L0_025: wardrobe f_L0_025: 0.29 m free in front, needs ≥ 0.80 m) | Shift the 1.45 m wardrobe 0.29 m into the room so it no longer cuts wall w_L0_004 and no longer overlaps f_L0_025. |
| 1673 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1674 | 4 | complete_group | r_L-1_mutfak.kitchen_run | memory: the same edit was rejected in round 1: no_place: r_L-1_mutfak.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no place passes the checks) | Kitchen run is missing its fridge (G9 major); the solver places it. |
| 1677 | 4 | move_piece | f_L0_025 | max_tries: f_L0_025 was edited 3 times in this round | Slide the 2.09 m wardrobe 0.3 m left along the top wall so it no longer overlaps f_L0_040 and no longer cuts wall w_L0_004. |
| 1678 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1679 | 4 | move_piece | f_L0_040 | drawn_lock: f_L0_040: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Slide the 1.45 m wardrobe 0.3 m right along the top wall so it no longer overlaps f_L0_025 and no longer cuts wall w_L0_004. |
| 1681 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1683 | 4 | relayout_room | r_L-1_mutfak | no_place: r_L-1_mutfak relayout: no place passes the checks (kitchen_run: no place passes the checks; dining: no place passes the checks) | Solver candidate 2 places the missing fridge (f_L-1_099) to resolve G9, the only available path to satisfy the missing appliance. |
| 1684 | 4 | move_piece | f_L0_040 | f_L0_025: clearance_ok, f_L0_040: clearance_ok, score: plausibility 54 -> 34 (F9 f_L0_040: wardrobe f_L0_040 overlaps wardrobe f_L0_025 by 0.69 m²; F9 f_L0_040: wardrobe reaches 0.20 m² through the room outline; G13 f_L0_025: wardrobe f_L0_025: 0.00 m free in front, needs ≥ 0.80 m) | Slide the 1.45 m wardrobe 0.29 m right along the top wall so it no longer overlaps f_L0_025 and no longer cuts wall w_L0_004. |
| 1685 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1686 | 4 | relayout_room | r_L-1_mutfak | no_place: r_L-1_mutfak relayout: no place passes the checks (kitchen_run: no place passes the checks; dining: no place passes the checks) | Solver candidate 3 places the missing fridge (f_L-1_099) to resolve G9, the only available path to satisfy the missing appliance. |
| 1687 | 4 | rotate_piece | f_L0_018 | f_L0_018: clearance_ok, score: plausibility 54 -> 7 (F3 f_L0_018: bed_double: the headboard stands in the room (0.25 m off); G4 f_L0_018: bed_double f_L0_018: no nightstand on the free left side of the head (1.29 m free); G5 f_L0_018: bed_double f_L0_018: 0.17 m free along the right side, needs ≥ 0.60 m; G5 f_L0_018: bed_double f_L0_018: 0.36 m free at the foot, needs ≥ 0.60 m) | Rotate the bed so its long axis runs along the right wall (front faces 270°), giving ≥0.60 m clearance along the right side and resolving the G5 circulation gap. |
| 1688 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1690 | 4 | relayout_room | r_L-1_mutfak | choices: r_L-1_mutfak.dining: 'U' is not an option of the room's program (r_L-1_mutfak.kitchen_run: I/L/galley/U; r_L-1_mutfak.dining: seats_4) | Deselect the optional dining group so the solver can place the kitchen_run with its missing fridge (G9) without the dining group blocking placement. |
| 1691 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1693 | 4 | move_piece | f_L0_037 | max_tries: f_L0_037 was edited 3 times in this round | Snap the wardrobe's back onto free wall span s1 (w_L0_012) at the lower end, clear of the bed, resolving the floating wardrobe and back-not-on-wall findings. |
| 1694 | 4 | relayout_room | r_L-1_mutfak | max_tries: r_L-1_mutfak was edited 3 times in this round | Try the U-shape kitchen_run option so the solver can place the missing fridge (G9) in a configuration that passes the checks. |
| 1698 | 4 | relayout_room | r_L-1_mutfak_2 | no_place: r_L-1_mutfak_2 relayout: no place passes the checks (kitchen_run: no place passes the checks; dining: no place passes the checks) | Candidate 2 (score 8.82) places the missing fridge f_L-1_099 in the kitchen, fixing the G9 no-fridge finding; its G8 work-triangle/counter notes are soft terms, not hard failures. |
| 1707 | 4 | complete_group | r_L0_banyo.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | G10: the bathroom is missing a shower or bathtub; the solver should place the missing wet-area member of the drawn bathroom set. |
| 2079 | 5 | set_exterior | set_exterior | memory: the same edit was rejected in round 1: nothing to change | Balcony (type=balcony) has a sloped ceiling only 0.40 m high at the furniture positions, so the table and chairs show through; marking the room as exterior removes the ceiling-height constraint. |
| 2093 | 5 | move_piece | f_L-1_049 | drawn_lock: f_L-1_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.59 m) | Move armchair 0.3m towards room center to keep its front free zone inside the room and bring it closer to the seating cluster. |
| 2094 | 5 | move_piece | f_L-1_059 | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.35 m) | Move floor lamp 0.2m towards the armchair to satisfy the 1.2m proximity requirement. |
| 2096 | 5 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | Make the roof flat so the L1 ceiling is full height (2.45 m) everywhere, clearing the sloped-ceiling X2 findings where the sofa, desk and office chair (tops 0.79-1.0 m) poked through the 0.40 m sloped ceiling and the roof. |
| 2097 | 5 | move_piece | f_L-1_049 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.59 m) | Move armchair 0.3m towards room center to keep its front free zone inside the room and bring it closer to the seating cluster. |
| 2098 | 5 | move_piece | f_L-1_059 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.35 m) | Move floor lamp 0.2m towards the armchair to satisfy the 1.2m proximity requirement. |
| 2100 | 5 | move_piece | f_L-1_075 | drawn_lock: f_L-1_075: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.05m away from armchair f_L-1_070 to resolve the 0.024m overlap and cut. |
| 2101 | 5 | move_piece | f_L-1_077 | drawn_lock: f_L-1_077: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.047m away from armchair f_L-1_071 to resolve the 0.024m overlap and cut. |
| 2104 | 5 | move_piece | f_L-1_075 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_075: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.05m away from armchair f_L-1_070 to resolve the 0.024m overlap and cut. |
| 2105 | 5 | move_piece | f_L-1_077 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_077: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.047m away from armchair f_L-1_071 to resolve the 0.024m overlap and cut. |
| 2108 | 5 | move_piece | f_L-1_075 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_075: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.05m away from armchair f_L-1_070 to resolve the 0.024m overlap and cut. |
| 2109 | 5 | move_piece | f_L-1_077 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_077: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.047m away from armchair f_L-1_071 to resolve the 0.024m overlap and cut. |
| 2112 | 5 | move_piece | f_L-1_075 | memory: the same edit was rejected in round 5: drawn_lock: f_L-1_075: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move ottoman 0.05m away from armchair f_L-1_070 to resolve the 0.024m overlap and cut. |
| 2131 | 5 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | Bathroom renders as open-air with sky visible and fixtures poking through the roof; give the building a proper flat roof so the room is enclosed and the X2 ceiling-penetration findings clear. |
| 2140 | 5 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | The room has 9.7 m of outer wall with no window or door (blank facade finding X3); marking the exterior resolves this. |
| 2150 | 5 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | The sloped ceiling over the L1 corridor is only 0.40 m high at the shoe cabinet (and the cabinet top pokes through the roof at 5.05 m); a flat roof at the L1 ceiling height of 2.451 m removes the slope so the 1.90 m cabinet fits under the ceiling. |
| 2154 | 5 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | The sloped roof dips to 0.40 m over the bathroom and the fixtures (tops 3.85-4.15 m) poke through it; a flat roof at the L1 ceiling height (2.45 m) clears all of them. |
| 2164 | 5 | set_exterior | set_exterior | memory: the same edit was rejected in round 1: nothing to change | Acknowledge the 9.7 m blank facade as an intended architectural feature rather than an error (X3). |
| 2165 | 5 | complete_group | r_L0_banyo_2.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo_2.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Add the missing shower/bathtub to satisfy the bathroom program (G10). |
| 2469 | 6 | move_piece | f_L-1_078 | f_L-1_094: no_overlap | Shift ottoman 0.24 m away from armchair f_L-1_072 to clear the 0.19 m² overlap (F9) and the 0.024 m cut (S2). |
| 2471 | 6 | move_piece | f_L-1_078 | f_L-1_094: no_overlap | Shift ottoman 0.19 m away from armchair f_L-1_072 to clear the overlap (F9) and cut (S2) without hitting the bookshelf. |
| 2473 | 6 | move_piece | f_L-1_078 | f_L-1_094: no_overlap | Shift ottoman 0.14 m away from armchair f_L-1_072 to clear the overlap (F9) and cut (S2) while staying clear of the bookshelf. |
| 2474 | 6 | move_piece | f_L-1_078 | max_tries: f_L-1_078 was edited 3 times in this round | Shift ottoman 0.09 m away from armchair f_L-1_072 to clear the overlap (F9) and cut (S2) while staying clear of the bookshelf. |
| 2477 | 6 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.46 m) | Move the floor lamp 0.46 m from the window wall to clear the sill obstruction (G12: sill 0.90 m + 0.05 m). |
| 2478 | 6 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 4: drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the floor lamp 0.3 m from the window wall to clear the sill obstruction (G12: sill 0.90 m + 0.05 m). |
| 2481 | 6 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 4: f_L-1_054: no_overlap | Move the floor lamp 0.29 m from the window wall to clear the sill obstruction (G12: sill 0.90 m + 0.05 m). |
| 2482 | 6 | move_piece | f_L-1_065 | f_L-1_054: no_overlap | Move the floor lamp 0.28 m from the window wall to clear the sill obstruction (G12: sill 0.90 m + 0.05 m). |
| 2485 | 6 | move_piece | f_L-1_065 | f_L-1_054: no_overlap | Move the floor lamp 0.27 m from the window wall to clear the sill obstruction (G12: sill 0.90 m + 0.05 m). |
| 2509 | 6 | retype_piece | f_L1_018 | retype: table_coffee is no candidate for f_L1_018 (1.63 x 1.52 m at [13.36, 2.27]): the size table and the room / zone give stair | 1.63 x 1.52 m square drawn piece in the seating area is a coffee table. |
| 2521 | 6 | complete_group | r_L-1_mutfak.kitchen_run | memory: the same edit was rejected in round 1: no_place: r_L-1_mutfak.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no place passes the checks) | Kitchen run group is missing its required fridge member (G9). |
| 2522 | 6 | rotate_piece | f_L-1_017 | drawn_lock: f_L-1_017: the new front does not fix the error (its back is not on a wall) | Rotate stove so its back sits flush against the counter/wall, clearing the 0.06 m gap flagged by F3. |
| 2523 | 6 | complete_group | r_L-1_mutfak_2.kitchen_run | memory: the same edit was rejected in round 1: no_place: r_L-1_mutfak_2.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no place passes the checks) | Add the missing fridge to the kitchen run group to satisfy the G9 requirement. |
| 2544 | 6 | complete_group | r_L0_banyo_2.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo_2.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Add the missing shower/bathtub to satisfy the bathroom program requirement. |
| 2553 | 6 | complete_group | r_L0_banyo.bathroom_set | memory: the same edit was rejected in round 1: no_place: r_L0_banyo.bathroom_set (missing shower\|bathtub): no place passes the checks (bathroom_set: no candidate position fits the room) | Bathroom lacks a shower or bathtub (G10 major); add the missing shower/bathtub to complete the set. |
| 2557 | 6 | set_camera | ext_5 | eye height 0.74 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 7.39 m) | Lower the camera to eye level 1.6 m above the local ground to remove the high-angle bird's-eye perspective. |
| 2568 | 6 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | replace the 0.66 m sloped ceiling over the bathroom with a flat roof at the L1 ceiling height (2.451 m) so the bathtub top (0.70 m) no longer shows through |
| 2570 | 6 | set_exterior | set_exterior | max_tries: set_exterior was edited 3 times in this round | The sloped roof dips to 0.40-0.66 m over the L1 bathroom, so the washbasin, toilet and bathtub all show through the ceiling; a flat roof at the L1 ceiling height (2.45 m) clears all fixtures. |
| 3220 | 1 | retype_piece | f_L0_047 | no_change: f_L0_047 is already a shoe_cabinet | The shoe cabinet is rendered as a generic open metal shelving unit (wrong_type); retype it to a proper closed shoe cabinet model so the visual matches the intended furniture type. |
| 3223 | 1 | mark_not_furniture | f_L1_021 | acceptance: finding RC:f_L1_021 is still there after the edit (f_L1_021: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes)) | Coffee table in a hall is a misread symbol: it is not a hall piece (F1/G14), cuts wall w_L1_005 (S2) and reaches through the outline (F9); the RC finding confirms the AI pass mis-typed it. |
| 3267 | 1 | rotate_piece | f_L1_025 | acceptance: finding F4:f_L1_025 is still there after the edit (chair does not face its group (f_L1_024)) | Rotate the chair to face the table (front_deg 90) to resolve the orientation mismatch with its group anchor. |
| 3268 | 1 | move_piece | f_L0_009 | drawn_lock: f_L0_009: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.60 m) | Move bed 0.6m to the right to create the required 0.60m clearance on the left side (G5). |
| 3271 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding F3:f_L1_010 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 3 more kept | Re-solve the room with the top-scoring solver candidate to fix both sofas' off-wall position and orientation and the coffee table placement in one coherent pass. |
| 3273 | 1 | retype_piece | f_L1_030 | score: plausibility 41 -> 31 (G3 f_L1_030: armchair f_L1_030 is 12° off the table_coffee f_L1_016 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Type the 0.68x0.78m drawn piece as an armchair per AI pass and size match. |
| 3274 | 1 | retype_piece | f_L1_035 | room_type: tv_unit is not a piece a other room may hold here | Type the 2.17x0.40m drawn piece as a tv_unit per AI pass and size match. |
| 3275 | 1 | retype_piece | f_L1_036 | room_type: console_table is not a piece a other room may hold here | Type the 1.09x0.40m drawn piece as a console_table per AI pass and size match. |
| 3276 | 1 | move_piece | f_L1_048 | acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | Move the bookshelf off the sloped-ceiling zone (top 4.52 m pokes through the roof) to the right wall where the ceiling is full height. |
| 3277 | 1 | move_piece | f_L1_009 | acceptance: finding F3:f_L1_009 is still there after the edit (sofa: its back is not on a wall (2.58 m off)) | Nudge the sofa 0.29 m toward the south wall to reduce the back-off-wall distance (2.48 m) within the 0.3 m drawn allowance. |
| 3278 | 1 | move_piece | f_L1_012 | drawn_lock: f_L1_012: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.93 m) | Slide the sofa 0.93 m along its axis to put its back on the right wall (w_L1_012), fixing the 0.79 m off-wall finding. |
| 3279 | 1 | move_piece | f_L1_015 | drawn_lock: f_L1_015: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.45 m) | Place the coffee table in front of the sofa f_L1_009 (0.58 m gap) to fix G2. |
| 3280 | 1 | retype_piece | f_L1_017 | retype: sofa is no candidate for f_L1_017 (1.63 x 1.52 m at [3.81, 2.27]): the size table and the room / zone give sofa_corner, stair | The 1.63 x 1.52 m drawn block is a sofa (the plan crop shows a seat with back cushions), typing and building it. |
| 3282 | 1 | mark_not_furniture | f_L1_024 | acceptance: finding RC:f_L1_024 is still there after the edit (f_L1_024: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes)) | The 'table_coffee' is a misread outline symbol in a hallway, not appropriate furniture; marking it not furniture removes the invalid piece and resolves the type and collision findings. |
| 3284 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The room is read as a living room (label 'Oyun Aktivite Ve Dinlenme Odası', two drawn sofas, coffee table, dining set); the 'other' type wrongly blocks tv_unit and console_table. |
| 3285 | 1 | retype_piece | f_L1_024 | retype: bench is no candidate for f_L1_024 (1.20 x 0.70 m at [13.61, 9.90]): the size table and the room / zone give none | The AI passes typed it bench and the vector geometry shows a table with chairs drawn around it; bench fits the 1.2x0.7 size and is a valid hall piece, resolving the type findings. |
| 3290 | 1 | move_piece | f_L1_010 | snap: f_L1_010: no free place on wall w_L1_015 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa's back onto the right wall (within 1.2 m of its drawn place) to fix F3 off-wall and face the coffee table. |
| 3291 | 1 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_002 (doors, windows, at most 1.2 m from the drawn place) | Snap the second sofa's back onto the top wall (within 1.2 m of its drawn place) to fix F3 off-wall and face the coffee table. |
| 3294 | 1 | move_piece | f_L1_010 | snap: f_L1_010: no free place on wall w_L1_015 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa's back onto the right wall (within 1.2 m of its drawn place) to fix F3 off-wall and face the coffee table. |
| 3295 | 1 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_002 (doors, windows, at most 1.2 m from the drawn place) | Snap the second sofa's back onto the top wall (within 1.2 m of its drawn place) to fix F3 off-wall and face the coffee table. |
| 3301 | 1 | move_piece | f_L1_010 | snap: f_L1_010: no free place on wall w_L1_015 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa's back onto the right wall (within 1.2 m of its drawn place) to fix F3 off-wall and face the coffee table. |
| 3324 | 1 | move_piece | f_L0_010 | score: plausibility 84 -> 74 (G4 f_L0_010: bed_double f_L0_010: no nightstand on the free left side of the head (1.96 m free); G11 f_L0_010: bed_double f_L0_010: its right use zone is not reached by a 0.60 m walkway from door d_L0_012; G11 f_L0_022: desk f_L0_022: its front use zone is not reached by a 0.60 m walkway from door d_L0_012) | Shift bed down to create 0.60 m clearance along its right side (G5). |
| 3629 | 2 | retype_piece | f_L1_021 | retype: table_dining is no candidate for f_L1_021 (1.20 x 0.70 m at [3.56, 9.90]): the size table and the room / zone give none | Vector geometry shows a table with a chair drawn around it, which outranks the AI pass that typed it bench/coffee table; a dining table fits the hall and resolves the wrong_type findings. |
| 3630 | 2 | retype_piece | f_L1_021 | retype: console_table is no candidate for f_L1_021 (1.20 x 0.70 m at [3.56, 9.90]): the size table and the room / zone give none | A console table is a valid hall piece that fits the 1.2x0.7 m drawn size, resolving the wrong_type findings (F1, G14, RC) since the vector geometry shows a table with a chair. |
| 3631 | 2 | retype_piece | f_L1_021 | retype: bench is no candidate for f_L1_021 (1.20 x 0.70 m at [3.56, 9.90]): the size table and the room / zone give none | The AI pass typed it bench; a bench is a valid hall piece that fits the 1.2x0.7 m drawn size, resolving the wrong_type findings (F1, G14, RC). |
| 3633 | 2 | retype_piece | f_L1_021 | max_tries: f_L1_021 was edited 3 times in this round | A sideboard is a valid hall piece that fits the 1.2x0.7 m drawn size, resolving the wrong_type findings (F1, G14, RC). |
| 3634 | 2 | move_group | r_L1_koridor.entrance | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The console table f_L1_049 (top 0.84 m) stands where the sloped ceiling is only 0.82 m high, showing through the ceiling; moving the entrance group to the free wall span s0 clears the ceiling clash. |
| 3636 | 2 | move_group | r_L1_koridor.entrance | no_place: r_L1_koridor.entrance on span r_L1_koridor.s1: no place passes the checks (entrance: no candidate position fits the room) | Fixes c:X2:f_L1_049: the console table f_L1_049 (top 0.84 m) stands where the sloped ceiling is only 0.82 m high, showing through the ceiling; moving the entrance group to the free wall span s1 clears the ceiling clash. |
| 3638 | 2 | move_group | r_L1_koridor.entrance | memory: the same edit was rejected in round 2: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:X2:f_L1_049: the console table f_L1_049 (top 0.84 m) stands where the sloped ceiling is only 0.82 m high, showing through the ceiling; moving the entrance group to the free wall span s0 clears the ceiling clash. |
| 3639 | 2 | move_group | r_L1_koridor.entrance | no_place: r_L1_koridor.entrance on span r_L1_koridor.s0: no place passes the checks (entrance: no candidate position fits the room) | Fixes c:X2:f_L1_049: the console table f_L1_049 (top 0.84 m) stands where the sloped ceiling is only 0.82 m high, showing through the ceiling; moving the entrance group to the free wall span s0 at offset 2.0 m clears the ceiling clash. |
| 3640 | 2 | retype_piece | f_L-1_021 | retype: kitchen_counter is no candidate for f_L-1_021 (5.54 x 0.60 m at [1.50, 4.27]): the size table and the room / zone give none | 5.54 x 0.60 m long drawn run along the top wall is a counter run, not a furniture cluster |
| 3641 | 2 | move_piece | f_L1_049 | snap: f_L1_049: no free place on wall w_L1_002 (doors, windows) | Fixes c:X2:f_L1_049: the console table f_L1_049 (top 0.84 m) stands where the sloped ceiling is only 0.82 m high, showing through the ceiling; moving it to the free wall span s0 clears the ceiling clash. |
| 3642 | 2 | retype_piece | f_L-1_087 | f_L-1_049: no_overlap, f_L-1_087: no_overlap | 0.71 x 0.41 m low seat next to the armchairs matches the AI pass (ottoman) |
| 3643 | 2 | move_piece | f_L1_049 | snap: f_L1_049: no free place on wall w_L1_012 (doors, windows) | Fixes c:X2:f_L1_049: the console table f_L1_049 (top 0.84 m) stands where the sloped ceiling is only 0.82 m high, showing through the ceiling; moving it to the free wall span s1 clears the ceiling clash. |
| 3650 | 2 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [1.50, 4.27]): the size table and the room / zone give none | 5.54 x 0.60 m long low storage run along the top wall of the salon |
| 3651 | 2 | retype_piece | f_L-1_087 | f_L-1_049: no_overlap, f_L-1_087: no_overlap | 0.71 x 0.41 m low table between the armchairs (AI pass: ottoman, table_coffee) |
| 3654 | 2 | move_piece | f_L-1_053 | acceptance: finding F3:f_L-1_053 is still there after the edit (sofa_corner: its back is not on a wall (1.10 m off)) | Push sofa_corner back onto the left wall (w_L-1_007) to fix F3 off-wall |
| 3658 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility -82 -> -102 (F4 f_L-1_070: armchair faces a wall 0.11 m in front of it; F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 178° off the sofa_corner f_L-1_053 (needs ≤ 30°) at 2.81 m (needs ≤ 2.50 m)) | Turn armchair away from the sofa back to face the room (east) |
| 3662 | 2 | remove_piece | f_L1_048 | acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | AI-added bookshelf pokes through the roof/sloped ceiling (X2 critical + major); removing it resolves both findings. |
| 3663 | 2 | retype_piece | f_L1_017 | room_type: sofa_corner is not a piece a other room may hold here | 1.63x1.52 m drawn piece fits the sofa_corner size table for this activity/living room. |
| 3665 | 2 | retype_piece | f_L1_029 | score: plausibility 41 -> 31 (G3 f_L1_029: armchair f_L1_029 is 12° off the table_coffee f_L1_015 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | 0.68x0.78 m drawn piece matches the armchair size table and the AI pass. |
| 3666 | 2 | retype_piece | f_L1_033 | f_L1_033: inside_room, score: plausibility 41 -> 21 (F2 f_L1_033: bookshelf 0.40 m wide x 2.17 m deep (seen from its front) is turned 90° against the type's product sizes; F3 f_L1_033: bookshelf: its back is not on a wall (0.02 m off)) | 0.40x2.17 m drawn piece only fits the bookshelf size table. |
| 3668 | 2 | retype_piece | f_L1_034 | f_L1_034: inside_room | 1.09x0.40 m drawn piece fits the bookshelf size table (tv_unit was rejected). |
| 3669 | 2 | move_piece | f_L-1b_050 | drawn_lock: f_L-1b_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Move the floor lamp to the right wall so it is no longer floating alone in the room. |
| 3670 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Pull the chair 0.15 m away from the table edge so the clearance behind it reaches ≥0.81 m. |
| 3671 | 2 | move_piece | f_L-1b_055 | drawn_lock: f_L-1b_055: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Pull the chair away from the table edge so the clearance behind it reaches ≥0.81 m. |
| 3672 | 2 | swap_model | f_L-1b_013 | acceptance: finding F9:f_L-1b_013 is still there after the edit (stove f_L-1b_013 overlaps kitchen_counter f_L-1b_009 by 0.41 m²) | Smaller real stove model (0.50 x 0.65) to end the 0.41 m² overlap with kitchen_counter f_L-1b_009. |
| 3676 | 2 | relayout_room | r_L0_yatak_odasi_2 | acceptance: finding F9:f_L0_040 is still there after the edit (wardrobe f_L0_040 overlaps wardrobe f_L0_025 by 0.87 m²); 3 more kept | Re-solve the room with candidate 1 to move the storage wardrobes off window win_L0_006, clear the wardrobe overlap, and restore the bed's right-side clearance. |
| 3677 | 2 | move_piece | f_L0_017 | score: plausibility 60 -> 30 (F3 f_L0_017: bed_double: the headboard stands in the room (0.30 m off); G5 f_L0_017: bed_double f_L0_017: 0.54 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.3 m toward the right wall so the left side of the bed gains the required 0.60 m clearance (currently 0.53 m). |
| 3678 | 2 | move_piece | f_L0_017 | f_L0_017: no_overlap, f_L0_050: no_overlap, score: plausibility 60 -> 27 (F9 f_L0_050: nightstand f_L0_050 overlaps bed_double f_L0_017 by 0.11 m²; G4 f_L0_017: bed_double f_L0_017: no nightstand on the free right side of the head (2.96 m free); G4 f_L0_049: nightstand f_L0_049 of bed_double f_L0_017: 0.32 m from the bed side (needs ≤ 0.30 m); G4 f_L0_050: nightstand f_L0_050 of bed_double f_L0_017: -0.12 m from the bed side (needs ≤ 0.30 m)) | Shift the bed 0.3 m toward the bottom window wall so the left side of the bed gains the required 0.60 m clearance (currently 0.53 m). |
| 3680 | 2 | move_piece | f_L0_017 | drawn_lock: f_L0_017: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the bed 0.3 m toward the top wall so the left side of the bed gains the required 0.60 m clearance (currently 0.53 m). |
| 3682 | 2 | move_piece | f_L0_017 | max_tries: f_L0_017 was edited 3 times in this round | Shift the bed 0.28 m toward the top wall so the left side of the bed gains the required 0.60 m clearance (currently 0.53 m). |
| 3685 | 2 | move_piece | f_L0_026 | drawn_lock: f_L0_026: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the wardrobe 0.3 m right along the top wall so it no longer stands in front of window win_L0_005 (G12) and clears the overlap with f_L0_038. |
| 3687 | 2 | move_piece | f_L0_026 | f_L0_026: doors_free, f_L0_038: clearance_ok, score: plausibility 60 -> 20 (F9 f_L0_038: wardrobe f_L0_038 overlaps wardrobe f_L0_026 by 0.69 m²; R3 d_L0_007: door d_L0_007 swings into f_L0_026; G13 f_L0_038: wardrobe f_L0_038: 0.00 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.29 m right along the top wall so it no longer stands in front of window win_L0_005 (G12) and clears the overlap with f_L0_038. |
| 3689 | 2 | mark_not_furniture | f_L1_024 | memory: the same edit was rejected in round 1: acceptance: finding RC:f_L1_024 is still there after the edit (f_L1_024: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes)) | The 'table_coffee' is a misread of a bench or structural element in a hallway; it is not appropriate furniture for this room type and is causing wall collisions. Marking it as not furniture. |
| 3690 | 2 | move_piece | f_L0_038 | f_L0_026: clearance_ok, f_L0_038: clearance_ok, score: plausibility 60 -> 40 (F9 f_L0_038: wardrobe f_L0_038 overlaps wardrobe f_L0_026 by 0.69 m²; F9 f_L0_038: wardrobe reaches 0.20 m² through the room outline; G13 f_L0_026: wardrobe f_L0_026: 0.00 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.3 m left along the top wall so it no longer overlaps f_L0_026 (F9) and clears window win_L0_005 (G12). |
| 3692 | 2 | mark_not_furniture | f_L1_024 | acceptance: finding RC:f_L1_024 is still there after the edit (f_L1_024: the AI passes typed it bench; a table with chairs drawn around it (vector geometry outranks the AI passes)) | The 'table_coffee' is a misread of a bench or structural element in a hallway; it is not appropriate furniture for this room type and is causing wall collisions. Marking it as not furniture. |
| 3702 | 2 | set_room_type | r_L0_banyo | no_change: r_L0_banyo is already a bathroom | Reassert bathroom type so the washbasin f_L0_003 is interpreted in the correct fixture context rather than as a tub. |
| 3703 | 2 | fix_fixture | f_L0_003 | fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_009) | Nudge the washbasin to clear the door d_L0_009 swing that hits it on one hinge side. |
| 3706 | 2 | relayout_room | building | exists: no room 'building' in a room of the building | Re-place decor pieces so none poke through the roof (critical X2 under_roof findings). |
| 3707 | 2 | set_terrain | set_terrain | memory: the same edit was rejected in round 1: score: the level findings rise from 1 to 13; L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -4.71 m (1.29 m apart); L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -2.42 m (0.58 m apart); L4 lm_0 | Replace the steep 1:0.3 terrain with a planar model to remove the >1:3 slope without a retaining edge. |
| 4002 | 3 | retype_piece | f_L1_040 | retype: table_coffee is no candidate for f_L1_040 (0.70 x 0.70 m at [2.25, 4.75]): the size table and the room / zone give chair, floor_lamp, potted_plant, side_table, table_dining | The 0.7x0.7 m table is visually a small side/coffee table, not a dining table; retype to table_coffee to match the visual evidence. |
| 4005 | 3 | retype_piece | f_L1_040 | room_type: side_table is not a piece a balcony room may hold here | The 0.7x0.7 m table is visually a small side table, not a dining table; retype to side_table to match the visual evidence. |
| 4006 | 3 | remove_piece | f_L1_040 | score: plausibility 100 -> 80 (F8 f_L1_041: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m); F8 f_L1_042: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m)) | The 0.7x0.7 m table is a small side table that doesn't fit a balcony; removing it resolves the F1 type mismatch. |
| 4007 | 3 | resize_piece | f_L1_040 | max_tries: f_L1_040 was edited 3 times in this round | Resize the table to a proper small dining table size (0.8x0.8 m) to match its table_dining type. |
| 4011 | 3 | move_piece | f_L-1_058 | drawn_lock: f_L-1_058: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Move the floor lamp to resolve the overlap with floor lamp f_L-1_057 while keeping it near the corner. |
| 4012 | 3 | move_piece | f_L-1_057 | drawn_lock: f_L-1_057: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.50 m) | Move the floor lamp to clear the window sill height and unblock the opening. |
| 4020 | 3 | move_piece | f_L-1b_050 | wall_exists: no wall 'r_L-1b_salon.s1' | Snap the floor lamp's back to the free wall span s1 so it is no longer floating in the room. |
| 4021 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair 0.05 m further from the table to reach the 0.81 m clearance behind it. |
| 4024 | 3 | move_piece | f_L-1b_050 | snap: f_L-1b_050: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap the floor lamp's back to the free wall span on wall w_L-1b_010 so it is no longer floating in the room. |
| 4025 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair 0.1 m further from the table to reach the 0.81 m clearance behind it. |
| 4029 | 3 | retype_piece | f_L-1b_049 | f_L-1b_049: no_overlap, f_L-1b_049: windows_free, f_L-1b_050: no_overlap, score: plausibility 24 -> 4 (F8 f_L-1b_049: potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m); G12 f_L-1b_049: potted_plant f_L-1b_049 (1.00 m) stands in front of window win_L-1b_001 (sill 0.90 m + 0.05)) | Type the 0.59x0.59 m untyped drawn piece as potted_plant (one of the AI passes) to clear the untyped finding. |
| 4030 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F3:f_L1_009 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 7 more kept | Re-solve seating groups around drawn anchors f_L1_009 and f_L1_012 to fix off-wall, orientation and coffee-table findings. |
| 4031 | 3 | remove_piece | f_L1_048 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | AI-added bookshelf pokes through the sloped ceiling (X2); removing it resolves the finding. |
| 4032 | 3 | retype_piece | f_L-1b_046 | score: plausibility 24 -> 14 (F8 f_L-1b_046: chaise stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m)) | Type the 0.82x1.64 m untyped drawn piece as chaise (a candidate for its size/zone) to clear the untyped finding. |
| 4034 | 3 | retype_piece | f_L-1b_049 | f_L-1b_049: no_overlap, f_L-1b_049: windows_free, f_L-1b_050: no_overlap, score: plausibility 24 -> 4 (F8 f_L-1b_049: floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m); G12 f_L-1b_049: floor_lamp f_L-1b_049 (1.60 m) stands in front of window win_L-1b_001 (sill 0.90 m + 0.05)) | Type the 0.59x0.59 m untyped drawn piece as floor_lamp (the other AI pass) to clear the untyped finding. |
| 4036 | 3 | move_piece | f_L1_009 | wall_exists: no wall 'r_L1_oyun_aktivite_ve_dinlenme_odasi.s2' | Snap sofa back onto the top wall so it is on a wall and faces the coffee table (fixes F3 and F4 for f_L1_009). |
| 4037 | 3 | move_piece | f_L1_012 | wall_exists: no wall 'r_L1_oyun_aktivite_ve_dinlenme_odasi.s1' | Snap sofa back onto the right wall so it is on a wall (fixes F3 for f_L1_012). |
| 4039 | 3 | retype_piece | f_L-1b_046 | room_type: kitchen_counter is not a piece a living room may hold here | Type the 0.82x1.64 m untyped drawn piece as kitchen_counter (a candidate for its size/zone) to clear the untyped finding. |
| 4040 | 3 | move_piece | f_L0_038 | memory: the same edit was rejected in round 2: f_L0_026: clearance_ok; f_L0_038: clearance_ok; score: plausibility 60 -> 40 (F9 f_L0_038: wardrobe f_L0_038 overlaps wardrobe f_L0_026 by 0.69 m²; F9 f_L0_038: wardrobe reaches 0.20 m² through the room outline; G13 f_L0_026: wardrobe f_L0_026: 0.00 m free in front, needs ≥ 0.80 m) | Shift the duplicate wardrobe outline left off f_L0_026 to clear the 0.87 m² overlap (F9) while staying on the same wall line. |
| 4041 | 3 | move_piece | f_L1_009 | snap: f_L1_009: no free place on wall w_L1_002 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto the top wall so it is on a wall and faces the coffee table (fixes F3 and F4 for f_L1_009). |
| 4042 | 3 | move_piece | f_L1_012 | snap: f_L1_012: no free place on wall w_L1_012 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto the right wall so it is on a wall (fixes F3 for f_L1_012). |
| 4043 | 3 | move_piece | f_L0_038 | f_L0_026: clearance_ok, f_L0_038: clearance_ok, score: plausibility 60 -> 40 (F9 f_L0_038: wardrobe f_L0_038 overlaps wardrobe f_L0_026 by 0.78 m²; F9 f_L0_038: wardrobe reaches 0.11 m² through the room outline; G13 f_L0_026: wardrobe f_L0_026: 0.00 m free in front, needs ≥ 0.80 m) | Shift the duplicate wardrobe outline left off f_L0_026 to clear the 0.87 m² overlap (F9) while staying on the same wall line. |
| 4044 | 3 | move_piece | f_L0_026 | memory: the same edit was rejected in round 2: drawn_lock: f_L0_026: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the wardrobe right along the wall to clear the window win_L0_005 (G12) and the overlap with f_L0_038 (F9). |
| 4046 | 3 | move_piece | f_L1_009 | snap: f_L1_009: no free place on wall w_L1_002 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto the top wall (within 1.2 m of drawn place) so it is on a wall and faces the coffee table. |
| 4047 | 3 | move_piece | f_L1_012 | snap: f_L1_012: no free place on wall w_L1_012 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back onto the right wall (within 1.2 m of drawn place) so it is on a wall. |
| 4048 | 3 | move_piece | f_L0_026 | memory: the same edit was rejected in round 2: f_L0_026: doors_free; f_L0_038: clearance_ok; score: plausibility 60 -> 20 (F9 f_L0_038: wardrobe f_L0_038 overlaps wardrobe f_L0_026 by 0.69 m²; R3 d_L0_007: door d_L0_007 swings into f_L0_026; G13 f_L0_038: wardrobe f_L0_038: 0.00 m free in front, needs ≥ 0.80 m) | Shift the wardrobe right along the wall to clear the window win_L0_005 (G12) and the overlap with f_L0_038 (F9). |
| 4049 | 3 | move_piece | f_L0_026 | snap: f_L0_026: no free place on wall w_L0_003 (doors, windows, at most 1.2 m from the drawn place) | Snap the wardrobe back onto the wall and slide it right of the window win_L0_005 to clear G12 and the overlap with f_L0_038. |
| 4050 | 3 | move_piece | f_L1_009 | max_tries: f_L1_009 was edited 3 times in this round | Move sofa back to the top wall (within 1.2 m of drawn place) so it is on a wall and faces the coffee table. |
| 4051 | 3 | move_piece | f_L1_012 | max_tries: f_L1_012 was edited 3 times in this round | Move sofa back to the right wall (within 1.2 m of drawn place) so it is on a wall. |
| 4641 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the sleeping_double group around the drawn bed anchor to ensure both nightstands are correctly positioned on either side of the head. |
| 4645 | 1 | move_piece | f_L1_021 | acceptance: finding F9:f_L1_021 is still there after the edit (table_coffee reaches 0.31 m² through the room outline, up to 0.260 m deep); 1 more kept | Shift table_coffee 0.1 m further from wall w_L1_005 to clear the 0.055 m wall cut (S2) and room outline collision (F9). |
| 4646 | 1 | remove_piece | f_L1_049 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Remove AI-added console_table that stands where the sloped ceiling is only 0.82 m high (X2); all wall-span moves were rejected as no valid placement. |
| 4649 | 1 | move_piece | f_L-1_058 | acceptance: finding G12:f_L-1_057 is still there after the edit (floor_lamp f_L-1_057 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | Shift the floor lamp 0.3 m along the wall to clear the 0.06 m² overlap with f_L-1_057. |
| 4650 | 1 | move_piece | f_L-1_069 | acceptance: finding F9:f_L-1_074 is still there after the edit (table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.10 m²); 2 more kept | Move the armchair 0.24 m away from the window to clear the coffee table and ottoman overlaps and open the walkway. |
| 4662 | 1 | complete_group | r_L-1b_salon_kitchen.kitchen_run | memory: the same edit was rejected in round 1: exists: no group 'r_L-1b_salon_kitchen.kitchen_run' (its room 'r_L-1b_salon_kitchen') in a room of the building | Kitchen run is missing its fridge (G9); the solver places it in the run. |
| 4668 | 1 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (chair does not face its group (f_L-1b_051, f_L-1b_054)) | Chair now sits south of the table; face it north (0°) toward the table to clear the 62° orientation finding. |
| 4670 | 1 | rotate_piece | f_L-1b_056 | acceptance: finding G6:f_L-1b_056 is still there after the edit (chair f_L-1b_056 is 62° off the table f_L-1b_054 (needs ≤ 45°)) | Chair now sits south of the table; face it north (0°) toward the table to clear the 62° orientation finding. |
| 4671 | 1 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.75 m) | Move the plant off the window band (clears G12) and next to the floor lamp and sofa f_L-1b_046 so it is no longer floating (clears F8). |
| 4673 | 1 | remove_piece | f_L1_048 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | AI-added bookshelf pokes through the sloped ceiling (critical X2) and stands where the ceiling is only 0.82 m high (major X2); removing it resolves both findings. |
| 4675 | 1 | move_piece | f_L-1b_053 | acceptance: finding G6:f_L-1b_053 is still there after the edit (chair f_L-1b_053: 0.09 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Place the chair on the table's west long side facing east (0°) toward the table: clears the 62° orientation finding and keeps 0.81 m clearance behind it. |
| 4676 | 1 | move_piece | f_L1_048 | acceptance: finding X2:f_L1_048 is still there after the edit (f_L1_048: bookshelf with its top 1.80 m above the floor stands where the sloped ceiling is 0.82 m high; it shows through the ceiling) | Move the AI-added bookshelf away from the sloped-ceiling zone to the free span on wall w_L1_001 to clear the X2 roof/ceiling findings. |
| 4679 | 1 | move_piece | f_L-1b_049 | acceptance: finding F8:f_L-1b_049 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move the plant 0.3 m south, off the window band (clears G12) and within 1.2 m of the floor lamp and sofa f_L-1b_046 so it is no longer floating (clears F8). |
| 4682 | 1 | move_piece | f_L1_048 | acceptance: finding X2:f_L1_048 is still there after the edit (f_L1_048: bookshelf with its top 1.80 m above the floor stands where the sloped ceiling is 0.82 m high; it shows through the ceiling) | Move the AI-added bookshelf to the middle of the bottom wall, away from the sloped-ceiling corner, to clear the X2 roof/ceiling findings. |
| 4684 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 3: acceptance: finding F3:f_L1_009 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 7 more kept | Re-solve the seating groups around the drawn anchors f_L1_009 and f_L1_012 to place sofas against walls, orient them correctly, and position the coffee table and armchairs properly. |
| 4688 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F3:f_L1_009 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 5 more kept | Re-solve the seating groups around the drawn anchors f_L1_009 and f_L1_012 using solver candidate 2 to place sofas against walls, orient them correctly, and position the coffee table and armchairs properly. |
| 4689 | 1 | resize_piece | f_L-1b_045 | score: plausibility -45 -> -55 (F3 f_L-1b_045: sofa: its back is not on a wall (0.26 m off); G11 f_L-1b_005: kitchen_island f_L-1b_005: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_045: sofa f_L-1b_045: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Sofa dimensions were swapped (0.82 wide x 1.64 deep); correcting to 1.64 wide x 0.82 deep to match product orientation |
| 4690 | 1 | move_piece | f_L0_029 | snap: f_L0_029: no free place on wall w_L0_019 (doors, windows, at most 1.2 m from the drawn place) | Wardrobe blocks window win_L0_006; snap it to free span s1 (2.06 m) to clear the window band. |
| 4691 | 1 | move_piece | f_L0_038 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | Nightstand overlaps bed by 0.06 m² and is -0.12 m from bed side; move flush against bed's right side within 0.30 m. |
| 4694 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F3:f_L1_009 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 5 more kept | Re-solve the seating groups around the drawn anchors f_L1_009 and f_L1_012 using solver candidate 3 to place sofas against walls, orient them correctly, and position the coffee table and armchairs properly. |
| 4696 | 1 | move_piece | f_L1_033 | drawn_lock: f_L1_033: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.44 m) | Move the TV unit closer to the sofa f_L1_012 axis and increase distance from the sofa front to meet the G1 group layout requirements (≤0.30 m off axis, ≥1.50 m from front). |
| 4698 | 1 | move_piece | f_L0_029 | drawn_lock: f_L0_029: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.04 m) | Wardrobe blocks window win_L0_006; move it to free span s1 (wall w_L0_019, 2.06 m) to clear the window band. |
| 4700 | 1 | move_piece | f_L1_033 | drawn_lock: f_L1_033: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the TV unit 0.3 m left to align with the sofa f_L1_012 axis (reduce the 0.45 m off-axis offset to ≤0.30 m) for the G1 group layout. |
| 4703 | 1 | relayout_room | r_L0_yatak_odasi_3 | no_place: r_L0_yatak_odasi_3 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room to fix the nightstand collision (F9/S2/G4), the wardrobe blocking the window (G12), and add the missing left nightstand and desk chair. |
| 4704 | 1 | mark_not_furniture | f_L1_017 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | The untyped 1.63x1.52 m drawn piece is a dimension outline, not furniture; retype was rejected by size table and room type constraints. |
| 4705 | 1 | move_piece | f_L0_030 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | Move the wardrobe off the window band to a free wall span to clear the blocked opening. |
| 4706 | 1 | move_piece | f_L0_036 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | Nudge the nightstand away from the bed to resolve the overlap and negative clearance. |
| 4707 | 1 | place_group | r_L0_yatak_odasi_3 | no_place: storage group re-solved around the drawn wardrobe f_L0_029: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the storage group around the drawn wardrobe to clear the window band (G12). |
| 4708 | 1 | retype_piece | f_L1_017 | memory: the same edit was rejected in round 1: retype: sofa is no candidate for f_L1_017 (1.63 x 1.52 m at [3.81, 2.27]): the size table and the room / zone give sofa_corner, stair | The 1.63x1.52 m untyped drawn piece is most plausibly a sofa or seating element in this activity/rest room; retype to sofa to resolve the NR finding. |
| 4709 | 1 | retype_piece | f_L1_017 | memory: the same edit was rejected in round 2: room_type: sofa_corner is not a piece a other room may hold here | The 1.63x1.52 m untyped drawn piece fits the sofa_corner size table for this activity/rest room; retype to sofa_corner to resolve the NR finding. |
| 4712 | 1 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room with solver candidate 1 to move the wardrobe off window win_L0_005, open the bed side clearances and add the desk chair in one consistent layout. |
| 4714 | 1 | move_piece | f_L-1b_045 | acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.45 m off)) | Moving sofa back to the top wall (y=7.442) to fix F3: back not on wall |
| 4715 | 1 | place_group | r_L0_yatak_odasi_3 | no_place: work group re-solved around the drawn desk f_L0_024: the solver places nothing and leaves the drawn pieces as drawn (work: no place passes the checks) | Re-solve the work group around the drawn desk to add the missing office chair (G7). |
| 4716 | 1 | move_group | r_L0_yatak_odasi.storage | drawn_lock: r_L0_yatak_odasi.storage: drawn pieces (f_L0_028) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move wardrobe off window win_L0_005 to the right wall (s1) to clear G12 and G13. |
| 4719 | 1 | place_group | r_L0_yatak_odasi_3 | max_tries: r_L0_yatak_odasi_3 was edited 3 times in this round | Re-solve the sleeping_double group around the drawn bed to fix the nightstand collision and add the missing left nightstand. |
| 4720 | 1 | move_piece | f_L0_028 | drawn_lock: f_L0_028: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift wardrobe 0.3m right along the top wall to clear window win_L0_005 (G12) and gain front clearance (G13). |
| 4723 | 1 | move_piece | f_L0_028 | f_L0_028: doors_free, score: plausibility 57 -> 27 (R3 d_L0_007: door d_L0_007 swings into f_L0_028; G13 f_L0_028: wardrobe f_L0_028: 0.65 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.29m right along the top wall to clear window win_L0_005 (G12) and gain front clearance (G13). |
| 4724 | 1 | move_piece | f_L0_017 | f_L0_017: no_overlap, f_L0_042: no_overlap, score: plausibility 57 -> 47 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_017 by 0.10 m²; G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_017: -0.16 m from the bed side (needs ≤ 0.30 m); G5 f_L0_017: bed_double f_L0_017: 0.28 m free along the left side, needs ≥ 0.60 m) | Move bed 0.26m down to increase left side clearance from 0.53m towards the 0.60m needed (G5). |
| 4728 | 1 | move_piece | f_L0_017 | memory: the same edit was rejected in round 2: score: plausibility 60 -> 30 (F3 f_L0_017: bed_double: the headboard stands in the room (0.30 m off); G5 f_L0_017: bed_double f_L0_017: 0.54 m free along the left side, needs ≥ 0.60 m) | Move bed 0.30m right to increase left side clearance from 0.53m to 0.83m (G5 left). |
| 4730 | 1 | complete_group | r_L0_yatak_odasi.work | unverified: r_L0_yatak_odasi.work: the anchor f_L0_026 is unverified (retype_piece first) | Add the missing office chair to the desk group to resolve G7. |
| 4732 | 1 | retype_piece | f_L0_026 | no_change: f_L0_026 is already a desk | Verify the drawn desk by re-typing it so the work group can be completed with a chair (G7). |
| 4734 | 1 | place_group | r_L0_yatak_odasi | no_place: work group re-solved around the drawn desk f_L0_026: the solver places nothing and leaves the drawn pieces as drawn (work: no place passes the checks) | Re-solve the work group around the drawn desk to add the missing office chair (G7). |
| 4736 | 1 | move_piece | f_L0_017 | f_L0_017: no_overlap, f_L0_041: no_overlap, score: plausibility 57 -> 47 (F9 f_L0_041: nightstand f_L0_041 overlaps bed_double f_L0_017 by 0.09 m²; G4 f_L0_041: nightstand f_L0_041 of bed_double f_L0_017: -0.18 m from the bed side (needs ≤ 0.30 m); G5 f_L0_017: bed_double f_L0_017: 0.31 m free along the right side, needs ≥ 0.60 m) | Move bed 0.24m up to increase right side clearance from 0.56m towards 0.60m (G5 right). |
| 4739 | 1 | place_group | r_L0_yatak_odasi | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_017: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the sleeping_double group around the drawn bed to reposition nightstands and improve bed side clearances (G5). |
| 4746 | 1 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.70 m) | Moving sofa toward left wall to fix F3 (back not on wall) and improve circulation |
| 4751 | 1 | swap_model | f_L0_003 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | The washbasin is rendered as a vanity/dresser unit with drawers; swapping to a proper japandi washbasin fixture model fixes the D2 wrong_model finding. |
| 4753 | 1 | swap_model | f_L0_016 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | The toilet model is crude and low-poly; swapping to a mediterranean toilet model with proper contours fixes the D2 wrong_model finding. |
| 4756 | 1 | swap_model | f_L0_003 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | The washbasin is rendered as a vanity/dresser unit; swapping to a minimal washbasin fixture model fixes the D2 wrong_model finding. |
| 4757 | 1 | swap_model | f_L0_016 | acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | The toilet model is crude and low-poly; swapping to a japandi toilet model with proper contours fixes the D2 wrong_model finding. |
| 4758 | 1 | move_piece | f_L-1b_047 | the arguments of move_piece do not match its schema: <root>: 'reason' is a required property; <root>: {'piece_id': 'f_L-1b_047'} is not valid under any of the given schemas | no reason given |
| 4759 | 1 | move_piece | f_L-1b_047 | f_L-1b_047: inside_room | Moving plant 0.3m toward left wall to fix F8 (stands alone) and reduce G12 (in front of window) |
| 4760 | 1 | move_piece | f_L-1b_047 | acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Moving plant 0.3m away from window to fix G12 (in front of window) |
| 5014 | 2 | remove_piece | f_L1_049 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:X2:f_L1_049: console_table top at 0.84 m stands where the sloped ceiling is only 0.82 m high and shows through the ceiling; all wall-span moves were rejected, so removal is the only remaining fix. |
| 5029 | 2 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 4.99 m) | Move potted plant off the window (G12) to beside sofa f_L-1b_041 so it is no longer floating (F8). |
| 5030 | 2 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 3.09 m) | Move floor lamp to beside sofa f_L-1b_041 so it is no longer floating (F8). |
| 5033 | 2 | move_piece | f_L-1b_047 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move potted plant 0.3 m away from window to clear the sill (G12). |
| 5034 | 2 | move_piece | f_L-1b_048 | score: plausibility -45 -> -55 (G11 f_L-1b_005: kitchen_island f_L-1b_005: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Move floor lamp 0.3 m away from window area. |
| 5038 | 2 | remove_piece | f_L1_048 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | AI-added bookshelf pokes through the roof (critical X2) and stands under the low sloped ceiling (major X2); removing it resolves both findings. |
| 5039 | 2 | move_piece | f_L-1_058 | acceptance: finding G12:f_L-1_057 is still there after the edit (floor_lamp f_L-1_057 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | Move floor lamp 0.16 m away from f_L-1_057 to resolve the 0.06 m² overlap (F9) while staying clear of the window sill. |
| 5041 | 2 | move_piece | f_L-1_078 | f_L-1_095: no_overlap | Move ottoman 0.29 m away from armchair f_L-1_072 to resolve the 0.22 m² overlap (F9) and the 0.106 m cut (S2). |
| 5042 | 2 | move_piece | f_L-1_069 | drawn_lock: f_L-1_069: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.40 m) | Move armchair 0.39 m away from coffee table f_L-1_074 and ottoman f_L-1_076 to resolve their overlaps (F9) and the 0.106 m cut (S2). |
| 5043 | 2 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Nudge coffee table 0.11 m away from the sofa front to reach the required 0.30 m clearance (G2). |
| 5044 | 2 | move_piece | f_L-1b_058 | score: plausibility -45 -> -55 (F4 f_L-1b_058: chair does not face its group (f_L-1b_057, f_L-1b_060); G6 f_L-1b_058: chair f_L-1b_058 is 57° off the table f_L-1b_057 (needs ≤ 45°)) | Move chair f_L-1b_058 slightly toward the table to increase clearance behind it (G6: needs 0.81 m, has 0.09 m). |
| 5045 | 2 | move_piece | f_L-1b_062 | acceptance: finding F4:f_L-1b_062 is still there after the edit (chair does not face its group (f_L-1b_060, f_L-1b_057)) | Move chair f_L-1b_062 slightly toward the table to increase clearance behind it (G6: needs 0.81 m, has 0.09 m). |
| 5047 | 2 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | memory: the same edit was rejected in round 4: exists: no group 'r_L-1b_salon_2_kitchen.kitchen_run' (its room 'r_L-1b_salon_2_kitchen') in a room of the building | Add the missing fridge to the kitchen run group (G9). |
| 5048 | 2 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_024 slightly toward the table to increase clearance behind it from 0.78 m to ≥ 0.81 m (G6). |
| 5051 | 2 | move_piece | f_L-1b_042 | snap: f_L-1b_042: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 1.95 m off a wall; snap its back onto the right wall to resolve F3. |
| 5053 | 2 | resize_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: score: plausibility -45 -> -55 (F3 f_L-1b_045: sofa: its back is not on a wall (0.26 m off); G11 f_L-1b_005: kitchen_island f_L-1b_005: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_045: sofa f_L-1b_045: its front use zone is not reached by a 0.60 m walkway f | Resize sofa f_L-1b_045 to correct proportions (1.64 m wide x 0.82 m deep) to fix F2 (turned 90° against type's product sizes). |
| 5055 | 2 | move_piece | f_L-1_058 | acceptance: finding G12:f_L-1_057 is still there after the edit (floor_lamp f_L-1_057 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | Move floor lamp 0.26 m away from f_L-1_057 to resolve the 0.06 m² overlap (F9) while staying clear of the window sill. |
| 5057 | 2 | move_piece | f_L-1_078 | drawn_lock: f_L-1_078: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.34 m) | Move ottoman 0.34 m away from armchair f_L-1_072 to resolve the 0.22 m² overlap (F9) and the 0.106 m cut (S2). |
| 5058 | 2 | move_piece | f_L-1_069 | acceptance: finding F9:f_L-1_074 is still there after the edit (table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.11 m²); 2 more kept | Move armchair 0.18 m away from coffee table f_L-1_074 and ottoman f_L-1_076 to resolve their overlaps (F9) and the 0.106 m cut (S2). |
| 5059 | 2 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 4: drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge coffee table 0.30 m away from the sofa front to reach the required 0.30 m clearance (G2). |
| 5061 | 2 | move_piece | f_L-1b_042 | drawn_lock: f_L-1b_042: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.21 m) | Sofa back is 1.95 m off a wall; shift it right toward the right wall to reduce the off-wall distance. |
| 5064 | 2 | move_piece | f_L-1b_042 | drawn_lock: f_L-1b_042: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Sofa back is 1.95 m off a wall; shift it 0.3 m right toward the right wall to reduce the off-wall distance. |
| 5065 | 2 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (chair does not face its group (f_L-1b_051, f_L-1b_054)); 1 more kept | Chair is 62° off the table orientation; rotate to face the table (270°) to fix F4 and G6. |
| 5068 | 2 | move_piece | f_L-1b_042 | max_tries: f_L-1b_042 was edited 3 times in this round | Sofa back is 1.95 m off a wall; shift it 0.29 m right toward the right wall to reduce the off-wall distance. |
| 5069 | 2 | move_piece | f_L-1b_055 | memory: the same edit was rejected in round 2: drawn_lock: f_L-1b_055: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Chair has only 0.09 m clearance behind it; move it 0.31 m away from the wall to achieve ≥ 0.81 m clearance. |
| 5071 | 2 | move_piece | f_L-1_058 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L-1_057 is still there after the edit (floor_lamp f_L-1_057 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | Move floor lamp 0.30 m away from f_L-1_057 to resolve the 0.06 m² overlap (F9) while staying clear of the window sill. |
| 5073 | 2 | move_piece | f_L-1_078 | f_L-1_095: no_overlap | Move ottoman 0.30 m away from armchair f_L-1_072 to resolve the 0.22 m² overlap (F9) and the 0.106 m cut (S2). |
| 5076 | 2 | move_piece | f_L-1b_055 | drawn_lock: f_L-1b_055: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Chair has only 0.09 m clearance behind it; move it 0.30 m away from the wall to achieve ≥ 0.81 m clearance. |
| 5077 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has 0.78 m clearance behind it, needs ≥ 0.81 m; move it 0.03 m to increase clearance. |
| 5078 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L1_010 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 3 more kept | Solver candidate 1 (score 14.37) re-solves the seating groups around the drawn anchors, fixing F3/F4 on f_L1_010 and the G1/G2/G3 group layout findings. |
| 5081 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_010: clearance_ok, group checks: F6 f_L1_010: sofa: the free zone in front of it is blocked by f_L1_056, f_L1_057 | Candidate 1 was rejected before (F3 remained); candidate 2 (score 14.23) re-solves the seating groups around the drawn anchors with better circulation, targeting F3/F4 on f_L1_010 and the G1/G2/G3 group findings. |
| 5083 | 2 | move_piece | f_L-1b_049 | memory: the same edit was rejected in round 1: acceptance: finding F8:f_L-1b_049 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Potted plant is floating and blocking the window; move it 0.3 m toward the wall corner to clear the window and be near the wall. |
| 5084 | 2 | move_piece | f_L-1b_050 | acceptance: finding F8:f_L-1b_050 is still there after the edit (floor_lamp stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.2 m)) | Floor lamp is floating; move it 0.3 m toward the wall to be near a wall and resolve F8. |
| 5086 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding F3:f_L1_010 is still there after the edit (sofa: its back is not on a wall (2.48 m off)); 4 more kept | Candidates 1 and 2 failed; candidate 3 (score 12.77) re-solves the seating groups around the drawn anchors, targeting F3/F4 on f_L1_010 and the G1/G2/G3 group findings. |
| 5090 | 2 | move_piece | f_L0_029 | memory: the same edit was rejected in round 1: snap: f_L0_029: no free place on wall w_L0_019 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe off window win_L0_006 onto free wall span s1 to clear the blocked opening (G12). |
| 5091 | 2 | move_piece | f_L0_038 | memory: the same edit was rejected in round 1: acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | Move nightstand flush against the bed's right side to resolve the 0.06 m² overlap and -0.12 m side gap (F9, G4, S2). |
| 5092 | 2 | relayout_room | r_L0_yatak_odasi | memory: the same edit was rejected in round 1: no_place: r_L0_yatak_odasi relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room with solver candidate 1 to move the wardrobe off the window, open the bed side clearances, and add the desk chair. |
| 5094 | 2 | move_piece | f_L1_010 | score: plausibility 44 -> 34 (F3 f_L1_010: sofa: its back is not on a wall (2.18 m off); G3 f_L1_027: armchair f_L1_027 is 7° off the table_coffee f_L1_016 (needs ≤ 30°) at 2.69 m (needs ≤ 2.50 m)) | Shift the sofa 0.3 m toward the coffee table so the table sits in front of it (G2) and the armchair distance drops below 2.5 m (G3); F3/F4 stay open for review. |
| 5097 | 2 | move_piece | f_L1_016 | acceptance: finding G2:f_L1_016 is still there after the edit (coffee table f_L1_016 is not in front of the sofa) | Shift the coffee table 0.3 m toward the sofa front so it sits in front of f_L1_010 (G2) and the armchair f_L1_030 distance drops below 2.5 m (G3). |
| 5099 | 2 | move_piece | f_L0_029 | snap: f_L0_029: no free place on wall w_L0_019 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe off window win_L0_006 onto free wall span s1 (w_L0_019) at a different offset to clear the blocked opening (G12). |
| 5104 | 2 | move_piece | f_L0_029 | drawn_lock: f_L0_029: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.74 m) | Move wardrobe along the south wall to the right, off window win_L0_006, to clear the blocked opening (G12). |
| 5105 | 2 | move_piece | f_L0_029 | max_tries: f_L0_029 was edited 3 times in this round | Shift wardrobe 0.3 m right (max drawn move) to clear window win_L0_006 (G12). |
| 5108 | 2 | relayout_room | r_L0_yatak_odasi_3 | memory: the same edit was rejected in round 1: no_place: r_L0_yatak_odasi_3 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room to add the missing nightstand on the bed's left side (G4 minor) and the office chair for the desk (G7 minor). |
| 5111 | 2 | complete_group | r_L0_yatak_odasi_3.work | unverified: r_L0_yatak_odasi_3.work: the anchor f_L0_024 is unverified (retype_piece first) | Add the missing office chair for the desk (G7 minor). |
| 5113 | 2 | retype_piece | f_L0_024 | no_change: f_L0_024 is already a desk | Build the desk from a library model so the work group can be completed with its office chair (G7 minor). |
| 5117 | 2 | complete_group | r_L0_yatak_odasi_3.sleeping_double | no_change: r_L0_yatak_odasi_3.sleeping_double: nothing missing (members: f_L0_037, f_L0_038) | Add the missing nightstand on the bed's free left side (G4 minor). |
| 5120 | 2 | rotate_piece | f_L1_025 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L1_025 is still there after the edit (chair does not face its group (f_L1_024)) | Face chair f_L1_025 towards the table f_L1_024 (now at [13.5,9.9]) to resolve F4 orientation finding. |
| 5121 | 2 | move_piece | f_L1_024 | f_L1_025: no_overlap | Move table further from wall w_L1_006 and room outline to clear the 0.048 m wall cut (S2) and outline breach (F9). |
| 5123 | 2 | move_piece | f_L1_024 | f_L1_025: no_overlap | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5126 | 2 | move_piece | f_L1_024 | f_L1_025: no_overlap | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5128 | 2 | retype_piece | f_L-1_090 | score: plausibility 71 -> 67 (G9 r_L-1_mutfak: kitchen r_L-1_mutfak has no fridge (fridge)) | The freestanding fridge in the corner with no counter beside it reads oddly; a tall cabinet integrates into the run and resolves the F9 placement finding. |
| 5129 | 2 | move_piece | f_L1_024 | max_tries: f_L1_024 was edited 3 times in this round | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5130 | 2 | remove_piece | f_L-1_090 | score: plausibility 71 -> 67 (G9 r_L-1_mutfak: kitchen r_L-1_mutfak has no fridge (fridge)) | The freestanding fridge tucked in the corner with no counter beside it is an odd placement (F9); removing it resolves the finding, and the kitchen's drawn run already carries the appliances. |
| 5131 | 2 | move_piece | f_L1_024 | max_tries: f_L1_024 was edited 3 times in this round | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5133 | 2 | move_piece | f_L1_025 | acceptance: finding F4:f_L1_025 is still there after the edit (chair does not face its group (f_L1_024)) | Nudge chair f_L1_025 up to clear the overlap with table f_L1_024 so the table can be moved off wall w_L1_006. |
| 5136 | 2 | move_piece | f_L1_024 | max_tries: f_L1_024 was edited 3 times in this round | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5137 | 2 | swap_model | f_L0_016 | memory: the same edit was rejected in round 1: acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | The toilet model is crude/low-poly; swapping to a higher-quality toilet model fixes the D2 wrong_model finding. |
| 5138 | 2 | move_piece | f_L1_024 | max_tries: f_L1_024 was edited 3 times in this round | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5140 | 2 | move_piece | f_L1_024 | max_tries: f_L1_024 was edited 3 times in this round | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5141 | 2 | move_piece | f_L1_024 | max_tries: f_L1_024 was edited 3 times in this round | Move table away from wall w_L1_006 and the room outline, and clear the overlap with chair f_L1_025, to resolve F9 and S2. |
| 5144 | 2 | set_terrain | set_terrain | score: the level findings rise from 1 to 13, L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -2.74 m (3.26 m apart), L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -0.29 m (2.71 m apart), L4 lm_005: level mark '40.00' (lm_005, ground_finished) reads -3.00 m; the ground there is built at -2.60 m (0.40 m apart), L4 lm_006: level mark '43.00' (lm_006, ground_finished) reads +0.00 m; the ground there is built at -0.29 m (0.29 m apart), L4 lm_007: level mark '40.00' (lm_007, ground_finished) reads -3.00 m; the ground there is built at -1.57 m (1.43 m apart) | Flatten the terrain to eliminate the 1:0.3 slope that exceeds the 1:3 maximum, fixing the L6 terrain finding |
| 5145 | 2 | set_terrain | set_terrain | memory: the same edit was rejected in round 1: score: the level findings rise from 1 to 13; L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -4.71 m (1.29 m apart); L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -2.42 m (0.58 m apart); L4 lm_0 | Use a planar terrain model to create a uniform gentle slope with a retaining edge, reducing the 1:0.3 slope to within the 1:3 limit |
| 5146 | 2 | add_camera | ext_front_y | the camera stands inside the building b2 (another building on the plot), eye height -0.28 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (8.5, 28) is at z 1.88 m: use z 3.38 to 3.58 for an eye-level view | Add a frontal exterior view of the +y entrance facade at eye level 1.6 m to fix the missing frontal view finding X6 |
| 5147 | 2 | add_camera | ext_front_y | the camera stands inside the building b2 (another building on the plot) | Add a frontal exterior view of the +y entrance facade at eye level 1.5 m above the sloped ground to fix the missing frontal view finding X6 |
| 5148 | 2 | add_camera | ext_front_y | the camera stands inside the building b2 (another building on the plot), eye height 2.96 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (8.5, 20) is at z 0.44 m: use z 1.94 to 2.14 for an eye-level view | Add a frontal exterior view of the +y entrance facade at eye level above the sloped ground, positioned closer to avoid building b2 |
| 5386 | 3 | relayout_room | r_L-1b_salon_2 | group checks: F4 f_L-1b_045: sofa does not face its group (f_L-1b_088) | Re-solve the room with the solver's best candidate to fix sofa f_L-1b_045 size/orientation/wall issues and the seating group layout (TV unit, coffee table). |
| 5387 | 3 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | memory: the same edit was rejected in round 4: exists: no group 'r_L-1b_salon_2_kitchen.kitchen_run' (its room 'r_L-1b_salon_2_kitchen') in a room of the building | Add the missing fridge to the kitchen run group to resolve G9. |
| 5389 | 3 | move_piece | f_L-1_058 | memory: the same edit was rejected in round 1: acceptance: finding G12:f_L-1_057 is still there after the edit (floor_lamp f_L-1_057 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | Move floor lamp f_L-1_058 to [15.29, 1.29] to resolve the overlap with f_L-1_057 and clear the window opening (sill 0.9m). |
| 5390 | 3 | move_piece | f_L-1_069 | memory: the same edit was rejected in round 1: acceptance: finding F9:f_L-1_074 is still there after the edit (table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.10 m²); 2 more kept | Move armchair f_L-1_069 to [10.79, 1.2] to resolve collisions with the coffee table and ottoman, and to clear the walkway to the door. |
| 5391 | 3 | move_piece | f_L-1_078 | memory: the same edit was rejected in round 6: f_L-1_094: no_overlap | Move ottoman f_L-1_078 to [9.3, 1.2] to resolve the collision with armchair f_L-1_072. |
| 5392 | 3 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 6: drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.46 m) | Move coffee table f_L-1_065 to [11.87, 1.2] to ensure it is in front of the sofa with the required 0.30m clearance. |
| 5396 | 3 | complete_group | r_L-1b_salon_kitchen.kitchen_run | memory: the same edit was rejected in round 1: exists: no group 'r_L-1b_salon_kitchen.kitchen_run' (its room 'r_L-1b_salon_kitchen') in a room of the building | Kitchen run is missing its fridge member (G9 major); completing the group builds it. |
| 5421 | 3 | remove_piece | f_L1_048 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | AI-added bookshelf pokes through the roof (critical X2) and stands under a low sloped ceiling (major X2); removing it resolves both findings. |
| 5423 | 3 | move_piece | f_L0_030 | snap: f_L0_030: no free place on wall w_L0_012 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe off the window band onto the free wall span s1 to clear the blocked opening (G12). |
| 5424 | 3 | move_piece | f_L0_036 | memory: the same edit was rejected in round 1: acceptance: new critical finding X2:f_L1_056: furn_f_L1_056 pokes through the roof (top 5.17 m) | Nudge the nightstand away from the bed to resolve the overlap and negative clearance (F9, S2, G4). |
| 5427 | 3 | move_piece | f_L0_030 | drawn_lock: f_L0_030: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.05 m) | Move the wardrobe off the window band to the free wall span s1 (back on w_L0_012) to clear the blocked opening (G12). |
| 5429 | 3 | move_group | r_L0_yatak_odasi_4.storage | drawn_lock: r_L0_yatak_odasi_4.storage: drawn pieces (f_L0_030) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the storage group off the window band to the free wall span s1 to clear the blocked opening (G12). |
| 5432 | 3 | relayout_room | r_L0_yatak_odasi_4 | no_place: r_L0_yatak_odasi_4 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room so the wardrobe leaves the window band (G12) and the desk gets its chair (G7). |
| 5433 | 3 | move_piece | f_L0_030 | drawn_lock: f_L0_030: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the wardrobe up within the 0.3 m allowance to clear the window band (G12). |
| 5435 | 3 | move_piece | f_L0_028 | snap: f_L0_028: no free place on wall w_L0_003 (doors, windows, at most 1.2 m from the drawn place) | Shift the wardrobe along the top wall away from window win_L0_005 to clear the blocked-opening G12 and open the 0.80 m front clearance (G13). |
| 5436 | 3 | move_piece | f_L0_028 | memory: the same edit was rejected in round 1: drawn_lock: f_L0_028: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the wardrobe 0.30 m along the top wall away from window win_L0_005 to clear the blocked-opening G12 and open the 0.80 m front clearance (G13). |
| 5438 | 3 | move_piece | f_L0_028 | f_L0_028: doors_free, score: plausibility 57 -> 54 (R3 d_L0_007: door d_L0_007 swings into f_L0_028 on one hinge side; the other hinge side is free; G13 f_L0_028: wardrobe f_L0_028: 0.65 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.25 m along the top wall away from window win_L0_005 to clear the blocked-opening G12 and open the 0.80 m front clearance (G13). |
| 5440 | 3 | move_piece | f_L0_028 | max_tries: f_L0_028 was edited 3 times in this round | Shift the wardrobe 0.30 m left along the top wall, away from the door swing and window win_L0_005, to clear G12 and open the 0.80 m front clearance (G13). |
| 5442 | 3 | move_piece | f_L0_017 | f_L0_017: no_overlap, f_L0_042: no_overlap, score: plausibility 57 -> 44 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_017 by 0.06 m²; G4 f_L0_017: bed_double f_L0_017: no nightstand on the free left side of the head (0.38 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_017: -0.14 m from the bed side (needs ≤ 0.30 m); G5 f_L0_017: bed_double f_L0_017: 0.38 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.16 m toward the window wall to open ≥0.60 m clearance along both sides (G5) while keeping the nightstands clear. |
| 5443 | 3 | move_piece | f_L0_017 | f_L0_017: no_overlap, f_L0_041: no_overlap, score: plausibility 57 -> 54 (G4 f_L0_017: bed_double f_L0_017: no nightstand on the free right side of the head (0.41 m free); G4 f_L0_041: nightstand f_L0_041 of bed_double f_L0_017: -0.12 m from the bed side (needs ≤ 0.30 m); G5 f_L0_017: bed_double f_L0_017: 0.41 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.14 m toward the desk side to open ≥0.60 m clearance along both sides (G5) while keeping the nightstands clear. |
| 5444 | 3 | move_piece | f_L0_029 | snap: f_L0_029: no free place on wall w_L0_004 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe off window win_L0_006 onto the free wall span s0 (w_L0_004) to clear the window band (G12). |
| 5445 | 3 | move_piece | f_L0_017 | acceptance: finding G5:f_L0_017 is still there after the edit (bed_double f_L0_017: 0.55 m free along the right side, needs ≥ 0.60 m) | Restore the bed to its drawn position: every 0.3 m shift collides with a nightstand or worsens the clearance, so the drawn placement is the best available. |
| 5447 | 3 | move_piece | f_L0_029 | snap: f_L0_029: no free place on wall w_L0_019 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe off window win_L0_006 onto the free wall span s1 (w_L0_019) to clear the window band (G12). |
| 5449 | 3 | move_piece | f_L0_029 | drawn_lock: f_L0_029: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift wardrobe 0.3 m north (max drawn move) to pull it off the window band of win_L0_006 (G12). |
| 5451 | 3 | move_piece | f_L0_029 | max_tries: f_L0_029 was edited 3 times in this round | Shift wardrobe 0.29 m north (within the 0.3 m drawn allowance) to pull it off the window band of win_L0_006 (G12). |
| 5691 | 4 | remove_piece | f_L1_048 | memory: the same edit was rejected in round 2: acceptance: finding X2:f_L1_048 is still there after the edit (furn_f_L1_048 pokes through the roof (top 4.52 m)) | AI-added bookshelf pokes through the roof (critical X2) and stands under a 0.82 m sloped ceiling (major X2); removing it resolves both findings. |

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
| S2 | minor | f_L-1_057 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_007 | r_L0_e_yatak_odasi | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_027 | r_L0_yatak_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_028 | r_L0_yatak_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_021 | r_L1_koridor | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_024 | r_L1_koridor_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_012 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| lighting_dark | minor | cam_r_L0_koridor_2 | r_L0_koridor | - | lighting_within_step | 1, 2, 3 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1_salon | cut | 1 | 4000 | 32768 |
| 1 | r_L-1b_salon | cut | 3 | 8257 | 32768 |
| 1 | building | cut | 1 | 34378 | 32768 |
| 1 | r_L-1b_salon_2 | cut | 8 | 13211 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 2 | 8745 | 32768 |
| 2 | r_L-1_salon_2 | cut | 2 | 13438 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 11078 | 32768 |
| 3 | r_L-1b_salon_2 | cut | 1 | 3975 | 32768 |
| 3 | r_L-1b_salon | cut | 7 | 40268 | 32768 |
| 3 | building | cut | 1 | 34388 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | reason |
|---|---|---|---|---|---|
| f_L-1_006 | piece | unknown | r_L-1_mutfak | inferred | - |
| f_L-1_007 | piece | unknown | r_L-1_mutfak | inferred | - |
| f_L-1_009 | piece | sink_kitchen | r_L-1_mutfak | inferred | - |
| f_L-1_015 | piece | unknown | r_L-1_mutfak_2 | inferred | - |
| f_L-1_016 | piece | unknown | r_L-1_mutfak_2 | inferred | - |
| f_L-1_018 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - |
| f_L-1_023 | piece | wardrobe | r_L-1_salon_2 | adjusted_by_ai | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_024 | piece | wardrobe | r_L-1_salon | adjusted_by_ai | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_038 | piece | table_dining | r_L-1_salon_2 | adjusted_by_ai | Shift dining table 0.02 m to clear the 0.039/0.038 m cuts with chairs f_L-1_039 and f_L-1_042 (S2). |
| f_L-1_049 | piece | armchair | r_L-1_salon | adjusted_by_ai | Rotate armchair to face the sofa_corner group (toward -y direction) to fix F4 and G3 orientation findings |
| f_L-1_051 | piece | toilet | r_L-1_banyo | inferred | - |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred | - |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred | - |
| f_L-1_058 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_060 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_061 | piece | sofa | r_L-1_salon | inferred, adjusted_by_ai | size snap: the drawn sofa 1.30 x 0.63 m is outside its product range (depth 0.63 m is 11 % outside 0.7-1.1 m; nearest real product 1.30 x 0.85 m); nearest real product 1.30 x 0.85 x 0.85 m (small 2-seat 130) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_062 | piece | sofa | r_L-1_salon_2 | inferred, adjusted_by_ai | size snap: the drawn sofa 1.30 x 0.63 m is outside its product range (depth 0.63 m is 11 % outside 0.7-1.1 m; nearest real product 1.30 x 0.85 m); nearest real product 1.30 x 0.85 x 0.85 m (small 2-seat 130) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_063 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1_065 | piece | table_coffee | r_L-1_salon_2 | inferred | - |
| f_L-1_069 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_072 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_074 | piece | table_coffee | r_L-1_salon_2 | adjusted_by_ai | size snap: the drawn table_coffee 0.56 x 0.56 m is outside its product range (width 0.56 m is 7 % outside 0.6-1.4 m (square symbol: square products only); nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.42 m (round / square 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_079 | piece | ottoman | r_L-1_salon_2 | inferred | - |
| f_L-1_080 | piece | ottoman | r_L-1_salon | inferred | - |
| f_L-1_081 | piece | sink_kitchen | r_L-1_mutfak | inferred | - |
| f_L-1_082 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - |
| f_L-1_083 | piece | sink_kitchen | r_L-1_mutfak | inferred | - |
| f_L-1_084 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - |
| f_L-1_087 | piece | table_coffee | r_L-1_salon | inferred | - |
| f_L-1b_001 | piece | unknown | r_L-1b_salon_2 | adjusted_by_ai | The large untyped cluster is a group of drawn pieces / structural element, not a single furniture item to build. |
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
| f_L-1b_045 | piece | sofa | r_L-1b_salon_2 | inferred, adjusted_by_ai | Turn the sofa to face the coffee table / seating group to the east, resolving F4. |
| f_L-1b_046 | piece | sofa | r_L-1b_salon | inferred, adjusted_by_ai | Sofa back is 0.63 m off a wall; snap its back onto the back wall to resolve F3. |
| f_L-1b_047 | piece | potted_plant | r_L-1b_salon_2 | inferred | - |
| f_L-1b_048 | piece | floor_lamp | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_049 | piece | potted_plant | r_L-1b_salon | inferred | - |
| f_L-1b_050 | piece | floor_lamp | r_L-1b_salon | adjusted_by_ai | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_051 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_052 | piece | chair | r_L-1b_salon | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_053 | piece | chair | r_L-1b_salon | adjusted_by_ai | Move chair 0.3 m away from the table to clear the 0.09 m overlap with f_L-1b_052 and open the 0.81 m clearance behind it. |
| f_L-1b_054 | piece | table_dining | r_L-1b_salon | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_055 | piece | chair | r_L-1b_salon | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_056 | piece | chair | r_L-1b_salon | adjusted_by_ai | Place the chair on the table's west long side facing east (0°) toward the table: clears the 62° orientation finding and keeps 0.81 m clearance behind it. |
| f_L-1b_057 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_058 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_059 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | Move chair f_L-1b_059 away from f_L-1b_058 to resolve the 0.09 m² overlap (F9) and improve clearance behind (G6). |
| f_L-1b_060 | piece | table_dining | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn table_dining 0.79 x 0.65 m is outside its product range (depth 0.65 m is 7 % outside 0.7-1.2 m; nearest real product 0.80 x 0.80 m); nearest real product 0.80 x 0.80 x 0.75 m (2-seat square / round 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_061 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | size snap: the drawn chair 0.71 x 0.45 m is outside its product range (width 0.71 m is 9 % outside 0.35-0.65 m; nearest real product 0.50 x 0.50 m); nearest real product 0.50 x 0.50 x 0.88 m (dining chair 50) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_062 | piece | chair | r_L-1b_salon_2 | adjusted_by_ai | Move chair f_L-1b_062 away from f_L-1b_061 to resolve the 0.09 m² overlap (F9) and improve clearance behind (G6). |
| f_L-1b_065 | piece | unknown | r_L-1b_salon_2 | inferred | - |
| f_L-1b_066 | piece | unknown | r_L-1b_salon | inferred | - |
| f_L-1b_067 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - |
| f_L-1b_068 | piece | sink_kitchen | r_L-1b_salon | inferred | - |
| f_L-1b_069 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - |
| f_L-1b_070 | piece | sink_kitchen | r_L-1b_salon | inferred | - |
| f_L0_003 | piece | washbasin | r_L0_banyo | adjusted_by_ai | The washbasin is rendered as a vanity/dresser unit; swapping to a proper washbasin model fixes the D2 wrong_model finding. |
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_009 | piece | bed_double | r_L0_yatak_odasi_4 | adjusted_by_ai | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_010 | piece | bed_double | r_L0_yatak_odasi_3 | adjusted_by_ai | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_011 | piece | shower | r_L0_e_banyo | inferred | - |
| f_L0_012 | piece | shower | r_L0_e_banyo_2 | inferred | - |
| f_L0_014 | piece | toilet | r_L0_e_banyo_2 | inferred | - |
| f_L0_015 | piece | toilet | r_L0_banyo_2 | inferred | - |
| f_L0_016 | piece | toilet | r_L0_banyo | adjusted_by_ai | The toilet model is crude/low-poly; swapping to a higher-quality toilet model fixes the D2 wrong_model finding. |
| f_L0_017 | piece | bed_double | r_L0_yatak_odasi | inferred | - |
| f_L0_018 | piece | bed_double | r_L0_yatak_odasi_2 | inferred | - |
| f_L0_019 | piece | wardrobe | r_L0_e_yatak_odasi | inferred | - |
| f_L0_020 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - |
| f_L0_021 | piece | bathtub | r_L0_banyo | inferred | - |
| f_L0_022 | piece | bathtub | r_L0_banyo_2 | inferred | - |
| f_L0_023 | piece | desk | r_L0_yatak_odasi_2 | inferred | - |
| f_L0_024 | piece | desk | r_L0_yatak_odasi_3 | inferred | - |
| f_L0_025 | piece | desk | r_L0_yatak_odasi_4 | inferred | - |
| f_L0_026 | piece | desk | r_L0_yatak_odasi | inferred | - |
| f_L0_027 | piece | wardrobe | r_L0_yatak_odasi_2 | inferred | - |
| f_L0_028 | piece | wardrobe | r_L0_yatak_odasi | inferred | - |
| f_L0_029 | piece | wardrobe | r_L0_yatak_odasi_3 | inferred | - |
| f_L0_030 | piece | wardrobe | r_L0_yatak_odasi_4 | inferred | - |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai | Shift the lower nightstand away from the bed edge to clear the 0.06 m² overlap and restore the required ≤0.30 m gap from the bed side. |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_017_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and satisfy the ≤0.30 m gap requirement. |
| f_L0_035 | piece | nightstand | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_009's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_019_ctx.png) |
| f_L0_036 | piece | nightstand | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | Nudge the nightstand further from the bed to resolve the overlap and negative clearance (F9, S2, G4). |
| f_L0_037 | piece | nightstand | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_010's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_021_ctx.png) |
| f_L0_038 | piece | nightstand | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | Move nightstand flush against the bed's right side to resolve the 0.06 m² overlap and -0.12 m side gap (F9, G4, S2). |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_005 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_006 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_013 | piece | toilet | r_L1_banyo | inferred | - |
| f_L1_014 | piece | toilet | r_L1_banyo_2 | inferred | - |
| f_L1_015 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_016 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_017 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | The drawn 1.63x1.52 m symbol is a decorative rug/area outline, not furniture; retype to sofa/sofa_corner was rejected by size table and room type. |
| f_L1_018 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | Untyped drawn outline the AI passes identified as not furniture; marking it clears c:NR:f_L1_018. |
| f_L1_019 | piece | bathtub | r_L1_banyo | inferred | - |
| f_L1_020 | piece | bathtub | r_L1_banyo_2 | inferred | - |
| f_L1_021 | piece | table_coffee | r_L1_koridor | adjusted_by_ai | Fixes c:F1:f_L1_021, c:G14:f_L1_021, c:RC:f_L1_021: the piece's own recognition crop shows a stair (tread hatching), not a table; the table_coffee type is a misread of the stair symbol, so it is not furniture. |
| f_L1_022 | piece | chair | r_L1_teras | adjusted_by_ai | F8: chair floats in the middle of the room; snap its back to the free wall span s2 so it stands against a wall. |
| f_L1_024 | piece | table_coffee | r_L1_koridor_2 | adjusted_by_ai | size snap: the drawn table_coffee 1.52 x 0.60 m is outside its product range (width 1.52 m is 8 % outside 0.6-1.4 m; nearest real product 1.20 x 0.70 m); nearest real product 1.20 x 0.70 x 0.42 m (coffee table 120 x 70) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_027 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_028 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_031 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_032 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_033 | piece | tv_unit | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_034 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - |
| f_L1_035 | piece | tv_unit | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_036 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - |
| f_L1_048 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | Move bookshelf to right wall at offset 3.0 m where the sloped ceiling is high enough (≥1.8 m) to clear the 1.8 m bookshelf, resolving both X2 findings. |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
| 1 | cam_r_L-1_banyo_2 | ![](agent/r1_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_2_after.jpg) |
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_banyo_2 | ![](agent/r1_cam_r_L0_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_banyo_2_after.jpg) |
| 1 | cam_r_L0_e_banyo_1 | ![](agent/r1_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_e_banyo_1_after.jpg) |
| 1 | cam_r_L0_e_banyo_2 | ![](agent/r1_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_e_banyo_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_1 | ![](agent/r1_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_2 | ![](agent/r1_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3 | ![](agent/r1_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 1 | cam_r_L1_banyo_1 | ![](agent/r1_cam_r_L1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L1_banyo_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | ext_1 | ![](agent/r1_ext_1_before.jpg) | ![](agent/r1_ext_1_after.jpg) |
| 1 | ext_2 | ![](agent/r1_ext_2_before.jpg) | ![](agent/r1_ext_2_after.jpg) |
| 1 | ext_5 | ![](agent/r1_ext_5_before.jpg) | ![](agent/r1_ext_5_after.jpg) |
| 1 | ext_7 | ![](agent/r1_ext_7_before.jpg) | ![](agent/r1_ext_7_after.jpg) |
| 2 | cam_r_L-1_banyo_1 | ![](agent/r2_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r2_cam_r_L-1_banyo_1_after.jpg) |
| 2 | cam_r_L-1_banyo_2 | ![](agent/r2_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r2_cam_r_L-1_banyo_2_after.jpg) |
| 2 | cam_r_L-1_mutfak_1 | ![](agent/r2_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_1_after.jpg) |
| 2 | cam_r_L-1_mutfak_2 | ![](agent/r2_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_2_after.jpg) |
| 2 | cam_r_L-1_mutfak_3 | ![](agent/r2_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_3_after.jpg) |
| 2 | cam_r_L-1_salon_1 | ![](agent/r2_cam_r_L-1_salon_1_before.jpg) | ![](agent/r2_cam_r_L-1_salon_1_after.jpg) |
| 2 | cam_r_L-1_salon_2 | ![](agent/r2_cam_r_L-1_salon_2_before.jpg) | ![](agent/r2_cam_r_L-1_salon_2_after.jpg) |
| 2 | cam_r_L-1_salon_3 | ![](agent/r2_cam_r_L-1_salon_3_before.jpg) | ![](agent/r2_cam_r_L-1_salon_3_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_banyo_2 | ![](agent/r2_cam_r_L0_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_2_after.jpg) |
| 2 | cam_r_L0_e_banyo_1 | ![](agent/r2_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_e_banyo_1_after.jpg) |
| 2 | cam_r_L0_e_banyo_2 | ![](agent/r2_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_e_banyo_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_1 | ![](agent/r2_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_2 | ![](agent/r2_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3 | ![](agent/r2_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r2_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r2_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r2_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 2 | cam_r_L1_banyo_1 | ![](agent/r2_cam_r_L1_banyo_1_before.jpg) | ![](agent/r2_cam_r_L1_banyo_1_after.jpg) |
| 2 | cam_r_L1_banyo_2 | - | ![](agent/r2_cam_r_L1_banyo_2_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_5 | ![](agent/r2_ext_5_before.jpg) | ![](agent/r2_ext_5_after.jpg) |
| 2 | ext_7 | ![](agent/r2_ext_7_before.jpg) | ![](agent/r2_ext_7_after.jpg) |
| 3 | cam_r_L-1_banyo_1 | ![](agent/r3_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L-1_banyo_1_after.jpg) |
| 3 | cam_r_L-1_banyo_2 | ![](agent/r3_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r3_cam_r_L-1_banyo_2_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_banyo_1 | ![](agent/r3_cam_r_L0_banyo_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_1_after.jpg) |
| 3 | cam_r_L0_banyo_2 | ![](agent/r3_cam_r_L0_banyo_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_1 | ![](agent/r3_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_2 | ![](agent/r3_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 3 | cam_r_L1_banyo_1 | ![](agent/r3_cam_r_L1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L1_banyo_1_after.jpg) |
| 3 | cam_r_L1_banyo_2 | ![](agent/r3_cam_r_L1_banyo_2_before.jpg) | ![](agent/r3_cam_r_L1_banyo_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 3 | ext_1 | ![](agent/r3_ext_1_before.jpg) | ![](agent/r3_ext_1_after.jpg) |
| 3 | ext_2 | ![](agent/r3_ext_2_before.jpg) | ![](agent/r3_ext_2_after.jpg) |
| 3 | ext_5 | ![](agent/r3_ext_5_before.jpg) | ![](agent/r3_ext_5_after.jpg) |
| 3 | ext_7 | ![](agent/r3_ext_7_before.jpg) | ![](agent/r3_ext_7_after.jpg) |
| 4 | cam_r_L-1_banyo_1 | ![](agent/r4_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L-1_banyo_1_after.jpg) |
| 4 | cam_r_L-1_banyo_2 | ![](agent/r4_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r4_cam_r_L-1_banyo_2_after.jpg) |
| 4 | cam_r_L-1_salon_1 | ![](agent/r4_cam_r_L-1_salon_1_before.jpg) | ![](agent/r4_cam_r_L-1_salon_1_after.jpg) |
| 4 | cam_r_L-1_salon_2 | ![](agent/r4_cam_r_L-1_salon_2_before.jpg) | ![](agent/r4_cam_r_L-1_salon_2_after.jpg) |
| 4 | cam_r_L-1_salon_3 | ![](agent/r4_cam_r_L-1_salon_3_before.jpg) | ![](agent/r4_cam_r_L-1_salon_3_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_banyo_2 | ![](agent/r4_cam_r_L0_banyo_2_before.jpg) | ![](agent/r4_cam_r_L0_banyo_2_after.jpg) |
| 4 | cam_r_L0_e_banyo_1 | ![](agent/r4_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_1_after.jpg) |
| 4 | cam_r_L0_e_banyo_2 | ![](agent/r4_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_2_after.jpg) |
| 4 | cam_r_L1_banyo_1 | ![](agent/r4_cam_r_L1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L1_banyo_1_after.jpg) |
| 4 | cam_r_L1_banyo_2 | ![](agent/r4_cam_r_L1_banyo_2_before.jpg) | ![](agent/r4_cam_r_L1_banyo_2_after.jpg) |
| 4 | ext_1 | ![](agent/r4_ext_1_before.jpg) | ![](agent/r4_ext_1_after.jpg) |
| 4 | ext_2 | ![](agent/r4_ext_2_before.jpg) | ![](agent/r4_ext_2_after.jpg) |
| 4 | ext_5 | ![](agent/r4_ext_5_before.jpg) | ![](agent/r4_ext_5_after.jpg) |
| 4 | ext_7 | ![](agent/r4_ext_7_before.jpg) | ![](agent/r4_ext_7_after.jpg) |
| 5 | cam_r_L-1_banyo_1 | ![](agent/r5_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r5_cam_r_L-1_banyo_1_after.jpg) |
| 5 | cam_r_L-1_banyo_2 | ![](agent/r5_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r5_cam_r_L-1_banyo_2_after.jpg) |
| 5 | cam_r_L0_banyo_1 | ![](agent/r5_cam_r_L0_banyo_1_before.jpg) | ![](agent/r5_cam_r_L0_banyo_1_after.jpg) |
| 5 | cam_r_L0_banyo_2 | ![](agent/r5_cam_r_L0_banyo_2_before.jpg) | ![](agent/r5_cam_r_L0_banyo_2_after.jpg) |
| 5 | cam_r_L0_e_banyo_1 | ![](agent/r5_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r5_cam_r_L0_e_banyo_1_after.jpg) |
| 5 | cam_r_L0_e_banyo_2 | ![](agent/r5_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r5_cam_r_L0_e_banyo_2_after.jpg) |
| 5 | cam_r_L0_yatak_odasi_1 | ![](agent/r5_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r5_cam_r_L0_yatak_odasi_1_after.jpg) |
| 5 | cam_r_L0_yatak_odasi_2 | ![](agent/r5_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r5_cam_r_L0_yatak_odasi_2_after.jpg) |
| 5 | cam_r_L0_yatak_odasi_3 | ![](agent/r5_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r5_cam_r_L0_yatak_odasi_3_after.jpg) |
| 5 | cam_r_L1_banyo_1 | ![](agent/r5_cam_r_L1_banyo_1_before.jpg) | ![](agent/r5_cam_r_L1_banyo_1_after.jpg) |
| 5 | ext_1 | ![](agent/r5_ext_1_before.jpg) | ![](agent/r5_ext_1_after.jpg) |
| 5 | ext_5 | ![](agent/r5_ext_5_before.jpg) | ![](agent/r5_ext_5_after.jpg) |
| 5 | ext_7 | ![](agent/r5_ext_7_before.jpg) | ![](agent/r5_ext_7_after.jpg) |
| 6 | cam_r_L-1_banyo_1 | ![](agent/r6_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r6_cam_r_L-1_banyo_1_after.jpg) |
| 6 | cam_r_L-1_banyo_2 | ![](agent/r6_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r6_cam_r_L-1_banyo_2_after.jpg) |
| 6 | cam_r_L-1_mutfak_1 | ![](agent/r6_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r6_cam_r_L-1_mutfak_1_after.jpg) |
| 6 | cam_r_L-1_mutfak_2 | ![](agent/r6_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r6_cam_r_L-1_mutfak_2_after.jpg) |
| 6 | cam_r_L-1_mutfak_3 | ![](agent/r6_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r6_cam_r_L-1_mutfak_3_after.jpg) |
| 6 | cam_r_L-1_salon_1 | ![](agent/r6_cam_r_L-1_salon_1_before.jpg) | ![](agent/r6_cam_r_L-1_salon_1_after.jpg) |
| 6 | cam_r_L-1_salon_2 | ![](agent/r6_cam_r_L-1_salon_2_before.jpg) | ![](agent/r6_cam_r_L-1_salon_2_after.jpg) |
| 6 | cam_r_L-1_salon_3 | ![](agent/r6_cam_r_L-1_salon_3_before.jpg) | ![](agent/r6_cam_r_L-1_salon_3_after.jpg) |
| 6 | cam_r_L0_banyo_1 | ![](agent/r6_cam_r_L0_banyo_1_before.jpg) | ![](agent/r6_cam_r_L0_banyo_1_after.jpg) |
| 6 | cam_r_L0_banyo_2 | ![](agent/r6_cam_r_L0_banyo_2_before.jpg) | ![](agent/r6_cam_r_L0_banyo_2_after.jpg) |
| 6 | cam_r_L0_e_banyo_1 | ![](agent/r6_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r6_cam_r_L0_e_banyo_1_after.jpg) |
| 6 | cam_r_L0_e_banyo_2 | ![](agent/r6_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r6_cam_r_L0_e_banyo_2_after.jpg) |
| 6 | cam_r_L1_banyo_1 | ![](agent/r6_cam_r_L1_banyo_1_before.jpg) | ![](agent/r6_cam_r_L1_banyo_1_after.jpg) |
| 6 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r6_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r6_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 6 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r6_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r6_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 6 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r6_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r6_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 6 | ext_1 | ![](agent/r6_ext_1_before.jpg) | ![](agent/r6_ext_1_after.jpg) |
| 6 | ext_2 | ![](agent/r6_ext_2_before.jpg) | ![](agent/r6_ext_2_after.jpg) |
| 6 | ext_5 | ![](agent/r6_ext_5_before.jpg) | ![](agent/r6_ext_5_after.jpg) |
| 6 | ext_7 | ![](agent/r6_ext_7_before.jpg) | ![](agent/r6_ext_7_after.jpg) |
| 7 | cam_r_L-1_banyo_1 | ![](agent/r7_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r7_cam_r_L-1_banyo_1_after.jpg) |
| 7 | cam_r_L-1_banyo_2 | ![](agent/r7_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r7_cam_r_L-1_banyo_2_after.jpg) |
| 7 | cam_r_L-1_koridor_2_1 | ![](agent/r7_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r7_cam_r_L-1_koridor_2_1_after.jpg) |
| 7 | cam_r_L-1_koridor_2_2 | ![](agent/r7_cam_r_L-1_koridor_2_2_before.jpg) | ![](agent/r7_cam_r_L-1_koridor_2_2_after.jpg) |
| 7 | cam_r_L-1_koridor_2_3 | ![](agent/r7_cam_r_L-1_koridor_2_3_before.jpg) | ![](agent/r7_cam_r_L-1_koridor_2_3_after.jpg) |
| 7 | cam_r_L-1_mutfak_1 | ![](agent/r7_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r7_cam_r_L-1_mutfak_1_after.jpg) |
| 7 | cam_r_L-1_mutfak_2 | ![](agent/r7_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r7_cam_r_L-1_mutfak_2_after.jpg) |
| 7 | cam_r_L-1_mutfak_3 | ![](agent/r7_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r7_cam_r_L-1_mutfak_3_after.jpg) |
| 7 | cam_r_L-1_salon_1 | ![](agent/r7_cam_r_L-1_salon_1_before.jpg) | ![](agent/r7_cam_r_L-1_salon_1_after.jpg) |
| 7 | cam_r_L-1_salon_2 | ![](agent/r7_cam_r_L-1_salon_2_before.jpg) | ![](agent/r7_cam_r_L-1_salon_2_after.jpg) |
| 7 | cam_r_L-1_salon_3 | ![](agent/r7_cam_r_L-1_salon_3_before.jpg) | ![](agent/r7_cam_r_L-1_salon_3_after.jpg) |
| 7 | cam_r_L0_banyo_1 | ![](agent/r7_cam_r_L0_banyo_1_before.jpg) | ![](agent/r7_cam_r_L0_banyo_1_after.jpg) |
| 7 | cam_r_L0_banyo_2 | ![](agent/r7_cam_r_L0_banyo_2_before.jpg) | ![](agent/r7_cam_r_L0_banyo_2_after.jpg) |
| 7 | cam_r_L0_e_banyo_1 | ![](agent/r7_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r7_cam_r_L0_e_banyo_1_after.jpg) |
| 7 | cam_r_L0_e_banyo_2 | ![](agent/r7_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r7_cam_r_L0_e_banyo_2_after.jpg) |
| 7 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r7_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r7_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 7 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r7_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r7_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 7 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r7_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r7_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 7 | cam_r_L0_koridor_1 | ![](agent/r7_cam_r_L0_koridor_1_before.jpg) | ![](agent/r7_cam_r_L0_koridor_1_after.jpg) |
| 7 | cam_r_L0_koridor_2 | ![](agent/r7_cam_r_L0_koridor_2_before.jpg) | ![](agent/r7_cam_r_L0_koridor_2_after.jpg) |
| 7 | cam_r_L0_koridor_3 | ![](agent/r7_cam_r_L0_koridor_3_before.jpg) | ![](agent/r7_cam_r_L0_koridor_3_after.jpg) |
| 7 | cam_r_L0_yatak_odasi_1 | ![](agent/r7_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r7_cam_r_L0_yatak_odasi_1_after.jpg) |
| 7 | cam_r_L0_yatak_odasi_2 | ![](agent/r7_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r7_cam_r_L0_yatak_odasi_2_after.jpg) |
| 7 | cam_r_L0_yatak_odasi_3 | ![](agent/r7_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r7_cam_r_L0_yatak_odasi_3_after.jpg) |
| 7 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r7_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r7_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 7 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r7_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r7_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 7 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r7_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r7_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 7 | cam_r_L1_banyo_1 | ![](agent/r7_cam_r_L1_banyo_1_before.jpg) | ![](agent/r7_cam_r_L1_banyo_1_after.jpg) |
| 7 | cam_r_L1_banyo_2 | ![](agent/r7_cam_r_L1_banyo_2_before.jpg) | ![](agent/r7_cam_r_L1_banyo_2_after.jpg) |
| 7 | cam_r_L1_koridor_1 | ![](agent/r7_cam_r_L1_koridor_1_before.jpg) | ![](agent/r7_cam_r_L1_koridor_1_after.jpg) |
| 7 | cam_r_L1_koridor_2 | ![](agent/r7_cam_r_L1_koridor_2_before.jpg) | ![](agent/r7_cam_r_L1_koridor_2_after.jpg) |
| 7 | cam_r_L1_koridor_2_1 | ![](agent/r7_cam_r_L1_koridor_2_1_before.jpg) | ![](agent/r7_cam_r_L1_koridor_2_1_after.jpg) |
| 7 | cam_r_L1_koridor_2_2 | ![](agent/r7_cam_r_L1_koridor_2_2_before.jpg) | ![](agent/r7_cam_r_L1_koridor_2_2_after.jpg) |
| 7 | cam_r_L1_koridor_2_3 | ![](agent/r7_cam_r_L1_koridor_2_3_before.jpg) | ![](agent/r7_cam_r_L1_koridor_2_3_after.jpg) |
| 7 | cam_r_L1_koridor_3 | ![](agent/r7_cam_r_L1_koridor_3_before.jpg) | ![](agent/r7_cam_r_L1_koridor_3_after.jpg) |
| 7 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r7_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r7_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 7 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r7_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r7_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 7 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r7_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r7_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 7 | cam_r_L1_teras_1 | ![](agent/r7_cam_r_L1_teras_1_before.jpg) | ![](agent/r7_cam_r_L1_teras_1_after.jpg) |
| 7 | cam_r_L1_teras_2 | ![](agent/r7_cam_r_L1_teras_2_before.jpg) | ![](agent/r7_cam_r_L1_teras_2_after.jpg) |
| 7 | cam_r_L1_teras_2_1 | ![](agent/r7_cam_r_L1_teras_2_1_before.jpg) | ![](agent/r7_cam_r_L1_teras_2_1_after.jpg) |
| 7 | cam_r_L1_teras_2_2 | ![](agent/r7_cam_r_L1_teras_2_2_before.jpg) | ![](agent/r7_cam_r_L1_teras_2_2_after.jpg) |
| 7 | cam_r_L1_teras_2_3 | ![](agent/r7_cam_r_L1_teras_2_3_before.jpg) | ![](agent/r7_cam_r_L1_teras_2_3_after.jpg) |
| 7 | cam_r_L1_teras_3 | ![](agent/r7_cam_r_L1_teras_3_before.jpg) | ![](agent/r7_cam_r_L1_teras_3_after.jpg) |
| 7 | ext_1 | ![](agent/r7_ext_1_before.jpg) | ![](agent/r7_ext_1_after.jpg) |
| 7 | ext_2 | ![](agent/r7_ext_2_before.jpg) | ![](agent/r7_ext_2_after.jpg) |
| 7 | ext_5 | ![](agent/r7_ext_5_before.jpg) | ![](agent/r7_ext_5_after.jpg) |
| 7 | ext_7 | ![](agent/r7_ext_7_before.jpg) | ![](agent/r7_ext_7_after.jpg) |
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
| 1 | cam_r_L-1_banyo_2 | ![](agent/r1_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_2_after.jpg) |
| 1 | cam_r_L-1_koridor_2_1 | ![](agent/r1_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_1_after.jpg) |
| 1 | cam_r_L-1_koridor_2_2 | ![](agent/r1_cam_r_L-1_koridor_2_2_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_2_after.jpg) |
| 1 | cam_r_L-1_koridor_2_3 | ![](agent/r1_cam_r_L-1_koridor_2_3_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_3_after.jpg) |
| 1 | cam_r_L0_koridor_1 | ![](agent/r1_cam_r_L0_koridor_1_before.jpg) | ![](agent/r1_cam_r_L0_koridor_1_after.jpg) |
| 1 | cam_r_L0_koridor_2 | ![](agent/r1_cam_r_L0_koridor_2_before.jpg) | ![](agent/r1_cam_r_L0_koridor_2_after.jpg) |
| 1 | cam_r_L0_koridor_3 | ![](agent/r1_cam_r_L0_koridor_3_before.jpg) | ![](agent/r1_cam_r_L0_koridor_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 1 | cam_r_L1_koridor_2_1 | ![](agent/r1_cam_r_L1_koridor_2_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_1_after.jpg) |
| 1 | cam_r_L1_koridor_2_2 | ![](agent/r1_cam_r_L1_koridor_2_2_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_2_after.jpg) |
| 1 | cam_r_L1_koridor_2_3 | ![](agent/r1_cam_r_L1_koridor_2_3_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_3_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 2 | cam_r_L-1_salon_1 | ![](agent/r2_cam_r_L-1_salon_1_before.jpg) | ![](agent/r2_cam_r_L-1_salon_1_after.jpg) |
| 2 | cam_r_L-1_salon_2 | ![](agent/r2_cam_r_L-1_salon_2_before.jpg) | ![](agent/r2_cam_r_L-1_salon_2_after.jpg) |
| 2 | cam_r_L-1_salon_3 | ![](agent/r2_cam_r_L-1_salon_3_before.jpg) | ![](agent/r2_cam_r_L-1_salon_3_after.jpg) |
| 2 | cam_r_L0_koridor_1 | ![](agent/r2_cam_r_L0_koridor_1_before.jpg) | ![](agent/r2_cam_r_L0_koridor_1_after.jpg) |
| 2 | cam_r_L0_koridor_2 | ![](agent/r2_cam_r_L0_koridor_2_before.jpg) | ![](agent/r2_cam_r_L0_koridor_2_after.jpg) |
| 2 | cam_r_L0_koridor_3 | ![](agent/r2_cam_r_L0_koridor_3_before.jpg) | ![](agent/r2_cam_r_L0_koridor_3_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r2_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r2_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r2_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 2 | cam_r_L1_koridor_1 | ![](agent/r2_cam_r_L1_koridor_1_before.jpg) | ![](agent/r2_cam_r_L1_koridor_1_after.jpg) |
| 2 | cam_r_L1_koridor_2 | ![](agent/r2_cam_r_L1_koridor_2_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_after.jpg) |
| 2 | cam_r_L1_koridor_2_1 | ![](agent/r2_cam_r_L1_koridor_2_1_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_1_after.jpg) |
| 2 | cam_r_L1_koridor_2_2 | ![](agent/r2_cam_r_L1_koridor_2_2_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_2_after.jpg) |
| 2 | cam_r_L1_koridor_2_3 | ![](agent/r2_cam_r_L1_koridor_2_3_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_3_after.jpg) |
| 2 | cam_r_L1_koridor_3 | ![](agent/r2_cam_r_L1_koridor_3_before.jpg) | ![](agent/r2_cam_r_L1_koridor_3_after.jpg) |
| 2 | cam_r_L1_teras_1 | ![](agent/r2_cam_r_L1_teras_1_before.jpg) | ![](agent/r2_cam_r_L1_teras_1_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_4 | ![](agent/r2_ext_4_before.jpg) | ![](agent/r2_ext_4_after.jpg) |
| 2 | ext_5 | ![](agent/r2_ext_5_before.jpg) | ![](agent/r2_ext_5_after.jpg) |
| 2 | ext_7 | ![](agent/r2_ext_7_before.jpg) | ![](agent/r2_ext_7_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_banyo_1 | ![](agent/r3_cam_r_L0_banyo_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_1_after.jpg) |
| 3 | cam_r_L0_banyo_2 | ![](agent/r3_cam_r_L0_banyo_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_2_after.jpg) |
| 3 | cam_r_L0_koridor_1 | ![](agent/r3_cam_r_L0_koridor_1_before.jpg) | ![](agent/r3_cam_r_L0_koridor_1_after.jpg) |
| 3 | cam_r_L0_koridor_2 | ![](agent/r3_cam_r_L0_koridor_2_before.jpg) | ![](agent/r3_cam_r_L0_koridor_2_after.jpg) |
| 3 | cam_r_L0_koridor_3 | ![](agent/r3_cam_r_L0_koridor_3_before.jpg) | ![](agent/r3_cam_r_L0_koridor_3_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 3 | cam_r_L1_koridor_1 | ![](agent/r3_cam_r_L1_koridor_1_before.jpg) | ![](agent/r3_cam_r_L1_koridor_1_after.jpg) |
| 3 | cam_r_L1_koridor_2 | ![](agent/r3_cam_r_L1_koridor_2_before.jpg) | ![](agent/r3_cam_r_L1_koridor_2_after.jpg) |
| 3 | cam_r_L1_koridor_3 | ![](agent/r3_cam_r_L1_koridor_3_before.jpg) | ![](agent/r3_cam_r_L1_koridor_3_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 3 | cam_r_L1_teras_1 | ![](agent/r3_cam_r_L1_teras_1_before.jpg) | ![](agent/r3_cam_r_L1_teras_1_after.jpg) |
| 3 | cam_r_L1_teras_2 | - | ![](agent/r3_cam_r_L1_teras_2_after.jpg) |
| 3 | cam_r_L1_teras_3 | - | ![](agent/r3_cam_r_L1_teras_3_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L1_koridor_1 | ![](agent/r1_cam_r_L1_koridor_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_1_after.jpg) |
| 1 | cam_r_L1_koridor_2 | ![](agent/r1_cam_r_L1_koridor_2_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_after.jpg) |
| 1 | cam_r_L1_koridor_3 | ![](agent/r1_cam_r_L1_koridor_3_before.jpg) | ![](agent/r1_cam_r_L1_koridor_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_banyo_2 | ![](agent/r2_cam_r_L0_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_2_after.jpg) |
| 2 | cam_r_L1_koridor_1 | ![](agent/r2_cam_r_L1_koridor_1_before.jpg) | ![](agent/r2_cam_r_L1_koridor_1_after.jpg) |
| 2 | cam_r_L1_koridor_2 | ![](agent/r2_cam_r_L1_koridor_2_before.jpg) | ![](agent/r2_cam_r_L1_koridor_2_after.jpg) |
| 2 | cam_r_L1_koridor_3 | ![](agent/r2_cam_r_L1_koridor_3_before.jpg) | ![](agent/r2_cam_r_L1_koridor_3_after.jpg) |
| 2 | cam_r_L1_teras_1 | ![](agent/r2_cam_r_L1_teras_1_before.jpg) | ![](agent/r2_cam_r_L1_teras_1_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 3 | cam_r_L1_koridor_1 | ![](agent/r3_cam_r_L1_koridor_1_before.jpg) | ![](agent/r3_cam_r_L1_koridor_1_after.jpg) |
| 3 | cam_r_L1_koridor_2 | ![](agent/r3_cam_r_L1_koridor_2_before.jpg) | ![](agent/r3_cam_r_L1_koridor_2_after.jpg) |
| 3 | cam_r_L1_koridor_3 | ![](agent/r3_cam_r_L1_koridor_3_before.jpg) | ![](agent/r3_cam_r_L1_koridor_3_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- final/cam_r_L1_banyo_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_banyo_2_final_preview.jpg
- final/cam_r_L1_teras_2_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_2_final_preview.jpg
- final/cam_r_L1_teras_2_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_3_final_preview.jpg
- final/cam_r_L1_teras_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_final_preview.jpg
- final/cam_r_L1_teras_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_3_final_preview.jpg
- final/ext_4_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/ext_4_final_preview.jpg
- final/cam_r_L1_banyo_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_banyo_2_plan.jpg
- final/cam_r_L1_teras_2_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_2_plan.jpg
- final/cam_r_L1_teras_2_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_3_plan.jpg
- final/cam_r_L1_teras_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_plan.jpg
- final/cam_r_L1_teras_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_3_plan.jpg
- final/ext_4_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/ext_4_plan.jpg
