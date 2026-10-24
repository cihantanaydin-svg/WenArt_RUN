# Final report: real04

42 views: 0 polished, 42 Cycles (gate_validation 5, not_run 37). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 42 |
| interior / exterior views | 37 / 5 |
| variant | base |
| polished | 0 |
| Cycles | 42 (gate_validation 5, not_run 37) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 10 |
| needs_review views | 3 |
| unverified pieces in view (sum over views) | 27 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 14 |
| exposure | -7.67 .. +2.67 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 22 view(s), -5 .. 0 EV |
| interior glazing pull | - |
| camera policy | m5 5, search 37 |
| camera score (min / mean / max) | 0.90 / 2.76 / 3.88 |
| rooms by number of views | 1 with 0, 1 with 1, 3 with 2, 10 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 5.0 min / 7.6 min / 61.9 s |
| seconds: polish / gate / check | - / - / 18.8 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 410.6 MB |
| [real04.glb](3d/real04.glb) | 1163.0 MB |

42 cameras; textures scaled to at most 1024 px (314 scaled) for the download.

## AI decor

106 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 26 rooms; 3 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

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
- drawn-piece check: 13 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 2.04 | D3 A1 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.49 | D3 A1 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | -4 | search 3.11 | D6 A2 | 1 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 2.90 | D2 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.67 | -5 | search 2.42 | D8 A2 | 0 | no | [preview](cam_r_L-1_koridor_2_3_final_preview.jpg) [plan](cam_r_L-1_koridor_2_3_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -3 | search 3.44 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.17 | -3 | search 3.28 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 3.27 | D4 A2 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 2.84 | D6 A2 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | -4 | search 2.72 | D8 A2 | 3 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 2.72 | D7 A2 | 2 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 2.05 | D4 A1 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 1.73 | D2 A1 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.04 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 0.89 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.00 | -1 | search 3.88 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.81 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.77 | D5 A3 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 3.40 | D4 A1 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_koridor_2 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 3.15 | D2 A1 | 0 | no | [preview](cam_r_L0_koridor_2_final_preview.jpg) [plan](cam_r_L0_koridor_2_plan.jpg) |
| cam_r_L0_koridor_3 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 2.83 | D3 A1 | 0 | no | [preview](cam_r_L0_koridor_3_final_preview.jpg) [plan](cam_r_L0_koridor_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.50 | -5 | search 3.41 | D4 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -4 | search 2.95 | D2 A5 | 1 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -4 | search 2.90 | D5 A2 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_4_1 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.33 | - | search 3.08 | D4 A2 | 1 | no | [preview](cam_r_L0_yatak_odasi_4_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_1_plan.jpg) |
| cam_r_L0_yatak_odasi_4_2 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.33 | - | search 2.95 | D4 A2 | 1 | no | [preview](cam_r_L0_yatak_odasi_4_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_2_plan.jpg) |
| cam_r_L0_yatak_odasi_4_3 | r_L0_yatak_odasi_4 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 2.69 | D4 A2 | 2 | no | [preview](cam_r_L0_yatak_odasi_4_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_4_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | -1.17 | - | search 1.64 | D2 A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 3.22 | D2 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.17 | - | search 2.98 | D3 A1 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_koridor_3 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.58 | D2 | 0 | no | [preview](cam_r_L1_koridor_3_final_preview.jpg) [plan](cam_r_L1_koridor_3_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.83 | - | search 3.24 | D4 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.67 | -3 | search 3.11 | D4 A1 | 0 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.67 | -3 | search 3.09 | D5 A1 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.50 | 0 | search 2.69 | D3 A2 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.50 | 0 | search 2.52 | D1 A2 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 2.31 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.00 | 0 | m5 blocked | D6 | 0 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D5 | 0 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 blocked | D2 | 0 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.00 | 0 | m5 | D9 | 0 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
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
| r_L1_koridor_2 | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | other | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 |
| r_L1_teras_2 | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_banyo_2 (twin of r_L0_e_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_3 (twin of r_L0_yatak_odasi_4), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_koridor_2 (twin of r_L1_koridor), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi), r_L1_teras_2 (twin of r_L1_teras).

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
- cam_r_L1_koridor_3: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: not_run: polish not run
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: not_run: polish not run
- cam_r_L1_teras_1: not_run: polish not run
- cam_r_L1_teras_2: not_run: polish not run
- cam_r_L1_teras_3: not_run: polish not run
- ext_1: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_2: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_3: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_5: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- ext_7: gate_validation: exterior gate validation not_validated: the exterior views stay the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:3A2AD/10,INSERT:3A2AD/11,INSERT:3A2AD/12,INSERT:3A2AD/13,INSERT:3A2AD/14,INSERT:3A2AD/15,INSERT:3A2AD/16,INSERT:3A2AD/17,INSERT:3A2AD/18,INSERT:3A2AD/19,INSERT:3A2AD/2,INSERT:3A2AD/20,INSERT:3A2AD/21,INSERT:3A2AD/22,INSERT:3A2AD/23,INSERT:3A2AD/24,INSERT:3A2AD/25,INSERT:3A2AD/26,INSERT:3A2AD/27,INSERT:3A2AD/28,INSERT:3A2AD/29,INSERT:3A2AD/30,INSERT:3A2AD/31,INSERT:3A2AD/32,INSERT:3A2AD/33,INSERT:3A2AD/4,INSERT:3A2AD/5,INSERT:3A2AD/6,INSERT:3A2AD/7,INSERT:3A2AD/8,INSERT:3A2AD/9 YATAK vector 0.90; deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 23 % of its pixels > 0.10 m outside the drawing, 570992 px |
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
- f_L1_008
- f_L1_012
- f_L1_013
- f_L1_014
- f_L1_023
- f_L1_024
- f_L1_025
- f_L1_026
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
- f_L0_039
- f_L0_040
- f_L0_041
- f_L0_042

Unverified pieces in view:

- cam_r_L-1_banyo_2: f_L-1_056
- cam_r_L-1_koridor_2_1: f_L-1_053
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_070
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_061, f_L-1_070
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_071
- cam_r_L0_banyo_1: f_L0_021
- cam_r_L0_e_yatak_odasi_1: f_L0_019
- cam_r_L0_e_yatak_odasi_2: f_L0_019
- cam_r_L0_e_yatak_odasi_3: f_L0_019
- cam_r_L0_yatak_odasi_1: f_L0_017, f_L0_026, f_L0_042
- cam_r_L0_yatak_odasi_2: f_L0_017
- cam_r_L0_yatak_odasi_3: f_L0_017, f_L0_028, f_L0_042
- cam_r_L0_yatak_odasi_4_1: f_L0_036
- cam_r_L0_yatak_odasi_4_2: f_L0_036
- cam_r_L0_yatak_odasi_4_3: f_L0_030, f_L0_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_036

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
| f_L1_005 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_009 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |
| f_L1_015 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_016 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_021 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_022 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L1_028 | furniture | wardrobe | abo_B07GFSJ69T | vision quality 2 (<= 2) |
| f_L1_039 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_042 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |

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
| c_037 | count_mismatch | f_L0_009, f_L0_010, f_L0_024, f_L0_025, f_L0_027, f_L0_028, f_L0_029, f_L0_030, f_L0_035, f_L0_036, f_L0_037, f_L0_038 | Zemin Kat: deneme1.dwg has 38 furniture pieces, deneme1.dwg has 34 | DWG wins over DWG, furniture kept; 8 extra from DWG not added (INSERT:2DDFC/0/0 (+60): it overlaps the master's unknown f_L0_030 by 98% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2DDFD/0/0 (+59): it overlaps the master's unknown f_L0_028 by 100% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A4/0/0 (+60): it overlaps the master's unknown f_L0_029 by 98% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A5/0/0 (+58): it overlaps the master's unknown f_L0_027 by 100% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2DDF9/0 (+21): it overlaps the master's bed_double f_L0_009 by 46% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A1/0 (+21): it overlaps the master's bed_double f_L0_010 by 46% of the smaller footprint, which the page does not draw at its place: that piece drawn again; INSERT:2E1A6/0 (+15): the same unknown footprint 1.45 x 0.91 m as the master's f_L0_024 in r_L0_yatak_odasi_3, which the secondary page does not draw at its place: that piece drawn elsewhere; INSERT:2DDFE/0 (+15): the same unknown footprint 1.45 x 0.91 m as the master's f_L0_025 in r_L0_yatak_odasi_4, which the secondary page does not draw at its place: that piece drawn elsewhere) |
| c_038 | outline_mismatch | L0, L-1 | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.500 m (areas 166.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_039 | outline_mismatch | L0, L-1b | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.500 m (areas 166.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_040 | outline_mismatch | L0, L1 | Outer wall outline of Çatı Katı differs from Zemin Kat by up to 1.500 m (areas 166.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_041 | type_disagreement | f_L-1_067 | f_L-1_067: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_042 | type_disagreement | f_L-1_068 | f_L-1_068: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_043 | type_disagreement | f_L-1b_064 | f_L-1b_064: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_044 | type_disagreement | f_L-1b_069 | f_L-1b_069: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_045 | type_disagreement | f_L-1b_070 | f_L-1b_070: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_046 | type_disagreement | f_L1_027 | f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes) | typed wardrobe (trust order: vector geometry and block names > AI) |
| c_047 | type_disagreement | f_L1_028 | f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes) | typed wardrobe (trust order: vector geometry and block names > AI) |
| c_048 | symbol_type_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_049 | symbol_type_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L-1_073 | f_L-1_073: sym_L-1_021: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_053 | symbol_type_disagreement | f_L-1_087 | f_L-1_087: sym_L-1_035: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_054 | symbol_type_disagreement | f_L-1b_045 | f_L-1b_045: sym_L-1b_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_046 in the twin room r_L-1b_salon named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_055 | symbol_type_disagreement | f_L-1b_046 | f_L-1b_046: sym_L-1b_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_045 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_056 | symbol_type_disagreement | f_L-1b_047 | f_L-1b_047: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_057 | symbol_type_disagreement | f_L-1b_049 | f_L-1b_049: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_058 | symbol_type_disagreement | f_L-1b_065 | f_L-1b_065: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L-1b_066 | f_L-1b_066: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L0_023 | f_L0_023: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L0_024 | f_L0_024: sym_L0_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L0_025 | f_L0_025: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_063 | symbol_type_disagreement | f_L0_026 | f_L0_026: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_064 | symbol_type_disagreement | f_L0_036 | f_L0_036: sym_L0_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) nightstand, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_065 | symbol_type_disagreement | f_L1_029 | f_L1_029: sym_L1_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_066 | symbol_type_disagreement | f_L1_030 | f_L1_030: sym_L1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_067 | symbol_type_disagreement | f_L1_031 | f_L1_031: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_068 | symbol_type_disagreement | f_L1_032 | f_L1_032: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_069 | symbol_type_disagreement | f_L1_036 | f_L1_036: sym_L1_x6881d71b: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the room misses it (the living room's living_storage group has no sideboard or bookshelf); inferred, listed in the report (reading.tie_break) |
| c_070 | symbol_type_disagreement | f_L1_037 | f_L1_037: sym_L1_x59e6f5f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sideboard, pass 2 (zai-org/GLM-4.6V-Flash) bench | unresolved: the drawn footprint is kept as unknown, unverified |
| c_071 | symbol_type_disagreement | f_L1_038 | f_L1_038: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the AI passes of its twin f_L1_036 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_072 | other | r_L-1b_salon | r_L-1b_salon: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_073 | other | r_L-1b_salon_2 | r_L-1b_salon_2: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_074 | symbol_front_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_075 | symbol_front_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_076 | symbol_front_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_077 | symbol_front_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_078 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_079 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_080 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_081 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_082 | symbol_front_disagreement | f_L0_023 | f_L0_023: sym_L0_007: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L0_024 | f_L0_024: sym_L0_008: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L0_025 | f_L0_025: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L0_026 | f_L0_026: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L0_036 | f_L0_036: sym_L0_020: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L1_029 | f_L1_029: sym_L1_007: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L1_030 | f_L1_030: sym_L1_008: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L1_031 | f_L1_031: sym_L1_009: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L1_032 | f_L1_032: sym_L1_010: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | unit_mismatch | r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21 | sheets.json sc_001: deneme1.dwg: $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_092 | registration_residual | r11, r5 | sheets.json sc_002: deneme1.dwg r11 (L-1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_093 | registration_residual | r15, r5 | sheets.json sc_003: deneme1.dwg r15 (L-1b) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_094 | registration_residual | r16, r5 | sheets.json sc_004: deneme1.dwg r16 (L0) registered onto r5 (L0) with an RMS outline distance of 0.247 m (492 of 550 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_095 | registration_residual | r18, r5 | sheets.json sc_005: deneme1.dwg r18 (L1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| c_096 | section_width_mismatch | r19 | sheets.json sc_006: section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 17.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

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

0 change(s) applied, 16 piece(s) added, 12 wall cabinet run(s).

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

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_009, f_L0_025, f_L0_030, f_L0_035, f_L0_036, f_L0_041

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_003, f_L0_016, f_L0_021

### Banyo (r_L0_banyo_2, bathroom): mirrored (decisions of r_L0_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_005, f_L0_015, f_L0_022

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi, other): completed

- added f_L1_045: bookshelf 0.80 x 0.30 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_006, f_L1_007, f_L1_013, f_L1_017, f_L1_020, f_L1_035, f_L1_036

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_047: bookshelf 0.80 x 0.30 (confidence -, rule, mirrored from f_L1_045)
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

Reference: source building.json; mode `complete`. 238 of 238 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 225 ok, 13 failed; 55 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1b_046 | sofa (sofa) | 1.15 | 0.00 | - | - |
| f_L0_032 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L0_036 | nightstand (floor_lamp) | 0.22 | 0.00 | yes | - |
| f_L0_038 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_019 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_020 | sofa (sofa) | 0.29 | 0.00 | - | - |

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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_4_1, cam_r_L0_yatak_odasi_4_2, cam_r_L0_yatak_odasi_4_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 42 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3 | 0 / 14 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| deneme1.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 23, block_name 56, group_member 8, inferred 14, level 3, nightstand_symbol 8, none 25, rule 90, twin 11. Recognition questions: 74; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L-1_057 | r_L-1_salon_2 | floor_lamp | yes | verified | no (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays, f_L-1_057 is not built (plan crop recognition/crops/sym_L-1_005_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_058 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_059 | r_L-1_salon | floor_lamp | yes | verified | no (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays, f_L-1_059 is not built (plan crop recognition/crops/sym_L-1_007_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_060 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_063 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_064 | r_L-1_salon | floor_lamp | yes | verified | no (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_065 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_066 | r_L-1_salon_2 | floor_lamp | yes | verified | no (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
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
| f_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_031 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_032 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_033 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_034 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | unverified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_035 | r_L1_oyun_aktivite_ve_dinlenme_odasi | bench | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bench, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
| f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | bookshelf | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |
| f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | bench | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sideboard, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
| f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | bookshelf | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |

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
| height | 2 | no height in the JSON; type height for bench | furn_f_L1_035, furn_f_L1_037 |
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_023, furn_f_L0_024, furn_f_L0_025 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L-1_058, furn_f_L-1_060, furn_f_L-1_063 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 8 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_039, furn_f_L0_040, furn_f_L0_041 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_011, furn_f_L0_012 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1_008, furn_f_L-1_017 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_013 |
| height | 4 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024, furn_f_L1_027 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 10 | window height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| height | 2 | window height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.76 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | win_L1_001, win_L1_002 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
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
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_009; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_011; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_010 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
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
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_027; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_029; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_028 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_020; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_019 (top 2.41 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_031; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_030 (top 2.18 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside light in the shade of the table lamp dec_L0_014 on f_L0_031 beside the bed f_L0_007; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_015); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_036 on f_L0_033 beside the bed f_L0_008; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_037); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_045 beside the bed f_L0_017; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_017 (the top of the nightstand f_L0_046 is taken by the plant_small dec_L0_007); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_046 on f_L0_047 beside the bed f_L0_018; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_018 (the top of the nightstand f_L0_048 is taken by the plant_small dec_L0_047); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside lamp on the nightstand f_L0_038; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_053 on f_L0_037 beside the bed f_L0_010; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside lamp on the nightstand f_L0_036; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_024 on f_L0_035 beside the bed f_L0_009; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_mirror | 1 | mirror light over the washbasin f_L1_015: the mirror dec_L1_008 reaches 1.74 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo |
| rig_mirror | 1 | mirror light over the washbasin f_L1_016: the mirror dec_L1_009 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo_2 |
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
| tree | 20 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| waist | 4 | the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc], hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_088c257155d527517719972d29f363a438cfb4cd [non_commercial], hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: yes
- cam_r_L-1_koridor_2_3: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_banyo_2: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L0_e_yatak_odasi_1: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_koridor_2: commercial-safe: yes
- cam_r_L0_koridor_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L0_yatak_odasi_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_4_1: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L0_yatak_odasi_4_2: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L0_yatak_odasi_4_3: commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: yes
- cam_r_L1_koridor_2: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L1_koridor_3: commercial-safe: yes
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- ext_7: commercial-safe: no (flagged assets: hssd_088c257155d527517719972d29f363a438cfb4cd [non_commercial])

## Built below library level (Milestone 13)

44 furniture piece(s) built from a module builder or a parametric family instead of a library model: 4 library gap(s) to close with a real model, 40 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 3), cam_r_L1_teras_3 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.7 degrees off the sun, sky pull k 3), ext_5 (5.4 degrees off the sun, sky pull k 0).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (74 of 74 answered); sheets/requests.json (8 of 8 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (74 of 74 answered); sheets/requests.json (8 of 8 answered) |

Assets: textures CC0 x 18; furniture/decor models CC-BY-4.0 x 176, CC-BY-NC-4.0 x 85, CC0 x 1, generated (TRELLIS.2-4B, MIT) x 20 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 42 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for f_L-1_051, f_L-1_052, f_L-1b_037, f_L-1b_038, f_L0_013, f_L0_014, f_L0_015, f_L0_016, f_L1_021, f_L1_022)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1b_020)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_003)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261023-135954-full-20261023T140546Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 54.8 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 2.2 min | 74 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.8 s | - |
| style | ok | 0.5 s | - |
| pipeline_final | ok | 3.2 min | answers applied |
| fit | ok | 6.5 s | - |
| layout | ok | 28.9 s | - |
| decor_ask | ok | 81.3 s | - |
| photos | reused | 0.2 s | - |
| assets | ok | 4.5 s | - |
| decor | ok | 9.4 s | - |
| agent_apply | ok | 23.2 s | - |
| refit | ok | 50.3 s | - |
| build | ok | 22.3 min | - |
| agent_previews | ok | 4.6 min | 3 view(s) |
| agent | ok | 28.9 min | 4 round(s), 18 finding(s) removed by 18 accepted edit(s) (measured; 17 predicted by the dry re-checks), 4 new, net 14, 138 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 10.1 min | - |
| export | ok | 99.4 s | - |
| controls | ok | 2.4 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 109.4 s | - |
| check | ok | 3.1 min | - |
| combine | ok | 2.3 min | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 18 edit(s) accepted, 138 rejected, 326 model calls (4380276 tokens), 33.9 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 6859): earlier runs of the appended log are left out (6858 events, 2260 model calls, 283 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 18 / 138 (12 % accepted) |
| rejected by reason | drawn_lock 35, acceptance 28, memory 18, max_tries 13, score 9 |
| rooms checked by code / vision / planner | 38 / 14 / 16 |
| rooms with fixable critical or major findings visited | 16 of 16 |
| critical before -> after | 1 -> 1 |
| major before -> after | 102 -> 88 |
| agent minutes; first accepted edit after | 29.23; 34.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 18; 74; 42 (27) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 18 measured; 17 predicted |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 4 new; net 14 |
| edits removing their finding | 10 of 11 |
| plans ok / empty / refused / default | 27 / 14 / 1 / 0 |

Library gaps reported by the agent: wardrobe minimal (No audited library wardrobe model fits the drawn 3.11 x 0.60 m footprint (all candidates fail the fit rules: caps/height), so the crude box model remains; the D2 and F9 wrong-model findings stay open for review.), washbasin (The washbasin already uses the best available real product model (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551); the D2 crude low-poly appearance is a limitation of the current library asset, so the gap is recorded.), toilet (The toilet already uses the best available real product model (objaverse_3446229dce1f47528fa871cc7669136c); the D2 crude low-poly appearance is a limitation of the current library asset, so the gap is recorded.), washbasin (The only washbasin model that fits (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551) renders as a closed dresser/cabinet; the alternative hssd_6219ef05f4a7b56419749e45a45143df8af44495 fails the fit rules (caps, height), so no audited open-basin washbasin model exists.), toilet (The only toilet model that fits (objaverse_3446229dce1f47528fa871cc7669136c) is crude and low-poly; the alternative objaverse_24d1b493899d407780140688abae19bc was removed in audit (open parts), so no audited realistic toilet model exists.), washbasin (Current washbasin model renders as a closed cabinet without basin/faucet (D2); all swap_model attempts rejected (no_change or pin_refused), so no audited library model fits.), toilet (Current toilet model is crude/low-poly (D2); all swap_model attempts rejected (no_change or pin_refused audit), so no audited library model fits.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 102 | 73 | 2 | 8 | 59 | refit | 6 |
| 2 | 2 | 90 | 65 | 2 | 7 | 38 | refit | 3 |
| 3 | 1 | 89 | 65 | 2 | 3 | 41 | refit | 3 |
| 4 | 1 | 88 | 64 | 2 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D2 | 0 | 19 | 0 | 0 |
| F1 | 0 | 3 | 8 | 0 |
| F2 | 0 | 8 | 0 | 0 |
| F3 | 0 | 18 | 8 | 0 |
| F4 | 0 | 11 | 0 | 0 |
| F6 | 0 | 5 | 0 | 0 |
| F8 | 0 | 16 | 0 | 0 |
| F9 | 3 | 37 | 0 | 0 |
| G1 | 0 | 0 | 40 | 0 |
| G10 | 0 | 72 | 0 | 0 |
| G11 | 0 | 24 | 0 | 0 |
| G12 | 0 | 16 | 0 | 0 |
| G13 | 0 | 8 | 0 | 0 |
| G14 | 0 | 0 | 8 | 0 |
| G2 | 0 | 0 | 21 | 0 |
| G3 | 0 | 8 | 0 | 0 |
| G4 | 0 | 4 | 4 | 0 |
| G5 | 0 | 16 | 0 | 0 |
| G6 | 0 | 28 | 24 | 0 |
| G8 | 0 | 16 | 16 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 16 | 0 |
| NR | 0 | 16 | 0 | 0 |
| R3 | 0 | 0 | 40 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S2 | 0 | 12 | 31 | 0 |
| S5 | 2 | 0 | 12 | 0 |
| X2 | 0 | 8 | 8 | 0 |
| X3 | 0 | 8 | 0 | 8 |
| X6 | 0 | 4 | 0 | 0 |
| lighting_dark | 0 | 0 | 3 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 7069 | 1 | complete_group | r_L-1b_salon_2.seating | added_by_ai | 0.0 -> 0.0 | Sofa f_L-1b_041 back is 2.00 m off a wall; re-solve the drawn seating group around its anchor to seat it against a wall and add the missing TV unit and coffee table. | ![](agent/r1_025_complete_group_before_r_L-1b_salon_2.png) | ![](agent/r1_026_complete_group_after_r_L-1b_salon_2.png) |
| 7082 | 1 | move_piece | f_L-1_038 | adjusted_by_ai | 27.0 -> 27.0 | S2: nudge the dining table 0.05 m so it no longer cuts chairs f_L-1_039 and f_L-1_042 by ~0.04 m. | ![](agent/r1_041_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_042_move_piece_after_r_L-1_salon_2.png) |
| 7093 | 1 | move_piece | f_L-1b_046 | adjusted_by_ai | 0.0 -> 0.0 | Snap sofa back to top wall to fix off_wall finding | ![](agent/r1_049_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_051_move_piece_after_r_L-1b_salon.png) |
| 7122 | 1 | move_piece | f_L0_036 | adjusted_by_ai | 77.0 -> 100.0 | Move nightstand f_L0_036 away from the bed to resolve the overlap (F9/S2) and correct its distance from the bed side (G4). | ![](agent/r1_066_move_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_067_move_piece_after_r_L0_yatak_odasi_4.png) |
| 7128 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift the nightstand 0.16 m away from the bed side to clear the 0.06 m² overlap (F9) and bring it within 0.30 m of the bed side (G4). | ![](agent/r1_072_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_073_move_piece_after_r_L0_e_yatak_odasi.png) |
| 7137 | 1 | report_library_gap | f_L0_019 | library_gap | - | No audited library wardrobe model fits the drawn 3.11 x 0.60 m footprint (all candidates fail the fit rules: caps/height), so the crude box model remains; the D2 and F9 wrong-model findings stay open for review. | - | - |
| 7151 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Move nightstand f_L0_034 away from the bed to resolve the 0.06 m² overlap (F9) and correct its position relative to the bed side (G4). | ![](agent/r1_085_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_086_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 7153 | 1 | move_piece | f_L0_038 | adjusted_by_ai | 77.0 -> 100.0 | Move nightstand f_L0_038 away from the bed to resolve the 0.06 m² overlap (F9) and correct its position relative to the bed side (G4). | ![](agent/r1_088_move_piece_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_089_move_piece_after_r_L0_yatak_odasi_3.png) |
| 7381 | 2 | move_piece | f_L-1_038 | adjusted_by_ai | 27.0 -> 27.0 | Shift the dining table 0.04 m so it no longer cuts chair f_L-1_042 by 0.036 m (S2). | ![](agent/r2_045_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_046_move_piece_after_r_L-1_salon_2.png) |
| 7402 | 2 | move_piece | f_L1_019 | adjusted_by_ai | 65.0 -> 75.0 | Shift sofa f_L1_019 0.3 m away from f_L1_018 to clear the blocked free zone in front of it (F6). | ![](agent/r2_056_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_058_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 7442 | 2 | report_library_gap | f_L-1_026 | library_gap | - | The washbasin already uses the best available real product model (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551); the D2 crude low-poly appearance is a limitation of the current library asset, so the gap is recorded. | - | - |
| 7443 | 2 | report_library_gap | f_L-1_051 | library_gap | - | The toilet already uses the best available real product model (objaverse_3446229dce1f47528fa871cc7669136c); the D2 crude low-poly appearance is a limitation of the current library asset, so the gap is recorded. | - | - |
| 7447 | 2 | report_library_gap | f_L0_003 | library_gap | - | The only washbasin model that fits (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551) renders as a closed dresser/cabinet; the alternative hssd_6219ef05f4a7b56419749e45a45143df8af44495 fails the fit rules (caps, height), so no audited open-basin washbasin model exists. | - | - |
| 7449 | 2 | report_library_gap | f_L0_016 | library_gap | - | The only toilet model that fits (objaverse_3446229dce1f47528fa871cc7669136c) is crude and low-poly; the alternative objaverse_24d1b493899d407780140688abae19bc was removed in audit (open parts), so no audited realistic toilet model exists. | - | - |
| 7454 | 2 | swap_model | f_L0_043 | added_by_ai | 100.0 -> 100.0 | Replace the generic metal shelving render with a real 4-door shoe cabinet (0.52x0.26x1.63) that fits the 0.6x0.3 footprint and height cap | ![](agent/r2_074_swap_model_before_r_L0_koridor.png) | ![](agent/r2_075_swap_model_after_r_L0_koridor.png) |
| 7660 | 3 | move_piece | f_L1_020 | adjusted_by_ai | 55.0 -> 65.0 | Shift sofa f_L1_020 away from f_L1_017 to clear the blocked free zone in front of it (F6). | ![](agent/r3_038_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_039_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 7700 | 3 | report_library_gap | f_L0_003 | library_gap | - | Current washbasin model renders as a closed cabinet without basin/faucet (D2); all swap_model attempts rejected (no_change or pin_refused), so no audited library model fits. | - | - |
| 7701 | 3 | report_library_gap | f_L0_016 | library_gap | - | Current toilet model is crude/low-poly (D2); all swap_model attempts rejected (no_change or pin_refused audit), so no audited library model fits. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 7070 | 1 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa f_L-1b_045 back is 0.59 m off a wall; snap its back onto the west wall (span s4) at its current position. |
| 7073 | 1 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.48 m) | Sofa f_L-1b_045 back is 0.59 m off a wall; shift it 1.48 m west so its back sits on the west wall (span s4) at its drawn height. |
| 7074 | 1 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 6.25 m) | Potted plant f_L-1b_047 blocks window win_L-1b_002 and stands alone; move it into the NW corner against the west wall, next to the seating. |
| 7075 | 1 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 4.27 m) | Floor lamp f_L-1b_048 stands alone; move it against the west wall beside the seating group. |
| 7076 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_070: armchair faces a wall 0.11 m in front of it; F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 136° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn the armchair away from the sofa back so it faces the room/coffee table (F4). |
| 7077 | 1 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.37 m) | Shift the coffee table away from armchair f_L-1_071 to clear the 0.12 m² overlap (F9). |
| 7079 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | F4: armchair stood behind the back of the corner sofa looking at it; turn it to face the seating group (toward the sofa) instead. |
| 7080 | 1 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.37 m) | F9: shift the coffee table 0.35 m away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 7081 | 1 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | G12: pull the floor lamp off the window band (sill 0.90 m) so it no longer blocks window win_L-1_002. |
| 7084 | 1 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa f_L-1b_045 back is 0.59 m off a wall; snap its back onto the west wall (span s4) at its drawn height. |
| 7085 | 1 | move_piece | f_L-1b_047 | snap: f_L-1b_047: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Potted plant f_L-1b_047 blocks window win_L-1b_002 and stands alone; snap it against the west wall in the NW corner, next to the seating. |
| 7086 | 1 | move_piece | f_L-1b_048 | snap: f_L-1b_048: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Floor lamp f_L-1b_048 stands alone; snap it against the west wall beside the seating group. |
| 7087 | 1 | move_piece | f_L-1_073 | score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.08 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Shift the coffee table 0.25 m away from armchair f_L-1_071 to clear the 0.12 m² overlap (F9). |
| 7088 | 1 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.86 m) | Move the floor lamp away from the window band so it no longer blocks the opening (G12). |
| 7091 | 1 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift the coffee table 0.3 m away from armchair f_L-1_071 to fully clear the overlap (F9). |
| 7092 | 1 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the floor lamp 0.3 m into the room, off the window sill line, to stop blocking the opening (G12). |
| 7094 | 1 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | F9: shift the coffee table 0.3 m away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 7095 | 1 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | G12: nudge the floor lamp 0.3 m into the room, off the window band (sill 0.90 m), so it no longer blocks win_L-1_002. |
| 7096 | 1 | move_piece | f_L-1_050 | drawn_lock: f_L-1_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | G11: pull the armchair 0.3 m toward the door side so a 0.60 m walkway from door o_L-1_002 reaches its front use zone. |
| 7097 | 1 | move_piece | f_L-1_054 | f_L-1_054: clearance_ok, score: plausibility 27 -> 17 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050) | G11: shift the corner sofa 0.3 m toward the door side so a 0.60 m walkway from door o_L-1_002 reaches its front use zone. |
| 7098 | 1 | move_piece | f_L-1b_045 | max_tries: f_L-1b_045 was edited 3 times in this round | Sofa f_L-1b_045 back is 0.59 m off a wall; snap its back onto the north wall (span s3) near its drawn position. |
| 7099 | 1 | move_piece | f_L-1b_047 | snap: f_L-1b_047: no free place on wall w_L-1b_004 (doors, windows, at most 1.2 m from the drawn place) | Potted plant f_L-1b_047 blocks window win_L-1b_002 and stands alone; snap it against the north wall (span s3) near its drawn position. |
| 7100 | 1 | move_piece | f_L-1b_048 | snap: f_L-1b_048: no free place on wall w_L-1b_004 (doors, windows, at most 1.2 m from the drawn place) | Floor lamp f_L-1b_048 stands alone; snap it against the north wall (span s3) near its drawn position. |
| 7101 | 1 | move_piece | f_L-1_063 | f_L-1_053: no_overlap, f_L-1_063: no_overlap | Nudge the floor lamp 0.28 m into the room, off the window sill line, to stop blocking the opening (G12). |
| 7102 | 1 | move_piece | f_L-1_073 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift the coffee table 0.3 m away from armchair f_L-1_071 to fully clear the overlap (F9). |
| 7105 | 1 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | Chair f_L-1b_059 overlaps chair f_L-1b_058 by 0.09 m²; shift it 0.36 m south to clear the collision. |
| 7106 | 1 | move_piece | f_L-1_063 | max_tries: f_L-1_063 was edited 3 times in this round | Slide the floor lamp 0.3 m along the window to a clear spot away from the blocked opening (G12). |
| 7107 | 1 | move_piece | f_L-1_073 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift the coffee table 0.3 m away from armchair f_L-1_071 to fully clear the overlap (F9). |
| 7112 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017); 6 more kept | Candidate 1 (score 9.34) re-solves the drawn dining and seating groups as units to fix chair clearance (G6), armchair alignment/distance (G3) and sofa frontage blockage (F6), and attempts the missing TV units and coffee table. |
| 7120 | 1 | swap_model | f_L0_019 | acceptance: pin_refused: f_L0_019: hssd_db19f85684c964132250926f988da86ac513baa6: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the crude low-poly box wardrobe with a detailed 5-door wardrobe model (2.53 x 0.61 m, close to the drawn 3.11 x 0.60 m) to fix the D2 and F9 wrong-model findings. |
| 7121 | 1 | move_piece | f_L0_032 | acceptance: finding F9:f_L0_032 is still there after the edit (nightstand f_L0_032 overlaps bed_double f_L0_007 by 0.16 m²) | Shift the nightstand 0.24 m away from the bed side to clear the 0.06 m² overlap (F9) and bring it within 0.30 m of the bed side (G4). |
| 7123 | 1 | move_piece | f_L1_011 | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.40 m) | Move chair outward to clear the 0.341 m overlap with dining table f_L1_009 (S2). |
| 7124 | 1 | move_piece | f_L1_018 | drawn_lock: f_L1_018: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.42 m) | Shift sofa f_L1_018 away from sofa f_L1_019 to clear the blocked free zone in front of f_L1_019 (F6). |
| 7127 | 1 | swap_model | f_L0_019 | no_change: f_L0_019 already uses the model abo_B015IPNVFW | Swap the crude box wardrobe for the 3.0 m 6-door wardrobe model (0.58 m deep, close to the drawn 3.11 x 0.60 m) to fix the D2 and F9 wrong-model findings. |
| 7132 | 1 | move_piece | f_L1_011 | score: plausibility 65 -> 45 (F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_011: chair f_L1_011 is 58° off the table f_L1_009 (needs ≤ 45°)) | Move chair f_L1_011 outward (0.3 m) to clear the 0.341 m overlap with dining table f_L1_009 (S2). |
| 7133 | 1 | swap_model | f_L0_019 | acceptance: pin_refused: f_L0_019: hssd_7094e30496b2735c235819e99c509769dc30502d: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the crude box wardrobe for the Calypso 6-Door Wardrobe (2.66 x 0.61 m, close to the drawn 3.11 x 0.60 m) to fix the D2 and F9 wrong-model findings. |
| 7134 | 1 | move_piece | f_L1_018 | drawn_lock: f_L1_018: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift sofa f_L1_018 up 0.3 m away from sofa f_L1_019 to clear the blocked free zone in front of f_L1_019 (F6). |
| 7138 | 1 | move_group | r_L0_yatak_odasi.storage | drawn_lock: r_L0_yatak_odasi.storage: drawn pieces (f_L0_028) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move wardrobe to the right wall to free the top wall and give the bed side clearance |
| 7139 | 1 | move_piece | f_L1_018 | drawn_lock: f_L1_018: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift sofa f_L1_018 up 0.32 m (within cap) away from sofa f_L1_019 to clear the blocked free zone in front of f_L1_019 (F6). |
| 7140 | 1 | move_piece | f_L1_011 | score: plausibility 65 -> 55 (G6 f_L1_011: chair f_L1_011: 0.61 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L1_011 outward along the table's long side (0.3 m) to clear the 0.341 m overlap with table f_L1_009 while keeping it facing the table (S2). |
| 7142 | 1 | move_piece | f_L0_028 | snap: f_L0_028: no free place on wall w_L0_013 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe to the right wall to free the top wall and give the bed side clearance |
| 7144 | 1 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the room to fix bed side clearance and wardrobe front clearance |
| 7145 | 1 | move_piece | f_L1_018 | max_tries: f_L1_018 was edited 3 times in this round | Shift sofa f_L1_018 up 0.28 m (within 0.3 m cap) away from sofa f_L1_019 to clear the blocked free zone in front of f_L1_019 (F6). |
| 7146 | 1 | move_piece | f_L1_011 | max_tries: f_L1_011 was edited 3 times in this round | Move chair f_L1_011 toward the table's open side (0.3 m) to clear the 0.341 m overlap with table f_L1_009 while keeping it facing the table (S2). |
| 7148 | 1 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: the solver places nothing and leaves the drawn pieces as drawn (storage: no candidate position fits the room) | Re-solve the drawn groups as units to satisfy the bed side clearances (0.53/0.56 m vs 0.60 m) and the wardrobe front clearance (0.66 m vs 0.80 m). |
| 7154 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the sleeping_double group to ensure proper layout and address the missing nightstand on the right side of the head (G4 minor). |
| 7161 | 1 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_modern_1_833baa60: a generated model (units guessed) while a real product of the type fits within the caps (hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551): the real model stays; swap to a real model of the type or use another tool | Swap crude low-poly washbasin block for a detailed modern washbasin model to fix D2 visual finding. |
| 7162 | 1 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_1_42fdb46f: a generated model (units guessed) while a real product of the type fits within the caps (objaverse_3446229dce1f47528fa871cc7669136c): the real model stays; swap to a real model of the type or use another tool | Swap crude low-poly toilet block for a realistic japandi toilet model to fix D2 visual finding. |
| 7166 | 1 | retype_piece | f_L0_043 | no_change: f_L0_043 is already a shoe_cabinet | F1: the piece renders as a generic metal shelving unit; confirming shoe_cabinet type fits its 0.6x0.3 footprint and the hall entrance group. |
| 7167 | 1 | swap_model | f_L-1_026 | no_change: f_L-1_026 already uses the model hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | Swap crude low-poly washbasin block for the real product model the code named, to fix the D2 visual finding. |
| 7168 | 1 | swap_model | f_L-1_051 | no_change: f_L-1_051 already uses the model objaverse_3446229dce1f47528fa871cc7669136c | Swap crude low-poly toilet block for the real product model the code named, to fix the D2 visual finding. |
| 7172 | 1 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Door d_L-1_001 swings into the washbasin; nudge the fixture to clear the swing. |
| 7173 | 1 | swap_model | f_L0_043 | acceptance: pin_refused: f_L0_043: abo_B07K7YMBNY: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | F1: replace the generic metal shelving render with a real shoe cabinet model (0.8x0.4, close to the 0.6x0.3 footprint) so the entrance group shows a proper shoe cabinet. |
| 7175 | 1 | swap_model | f_L0_043 | acceptance: pin_refused: f_L0_043: abo_B07TVMZ5QP: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | F1: swap the generic metal shelving render for a real shoe rack model (0.35 m depth fits the 0.3 m footprint) so the entrance shows a proper shoe cabinet. |
| 7176 | 1 | swap_model | f_L0_043 | max_tries: f_L0_043 was edited 3 times in this round | F1: swap the generic metal shelving render for a real 1-door shoe cabinet model (0.23 m depth fits the 0.3 m footprint) so the entrance shows a proper shoe cabinet. |
| 7177 | 1 | swap_model | f_L0_003 | no_change: f_L0_003 already uses the model hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | The washbasin is rendered as a closed dresser/cabinet; swap to the real Aquazuro onderkast Avanti 90cm washbasin model which has an open basin. |
| 7178 | 1 | swap_model | f_L0_016 | no_change: f_L0_016 already uses the model objaverse_3446229dce1f47528fa871cc7669136c | The toilet model is crude and low-poly; swap to the realistic Toilet model from objaverse. |
| 7179 | 1 | swap_model | f_L0_003 | acceptance: pin_refused: f_L0_003: hssd_6219ef05f4a7b56419749e45a45143df8af44495: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The washbasin is rendered as a closed dresser/cabinet; swap to the Hudson Reed Sublime Vanity Unit & Basin which has a visible open basin and faucet. |
| 7180 | 1 | swap_model | f_L0_016 | acceptance: pin_refused: f_L0_016: objaverse_24d1b493899d407780140688abae19bc: audit: removed (a drawer, door or lid is open, or a part floats apart): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The toilet model is crude and low-poly; swap to a different realistic Toilet model from objaverse. |
| 7362 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 6 more kept | Solver candidate 1 re-solves the seating and living_storage groups to fix the G11 walkway clearances (sofa, both armchairs), the G12 window blockage by the floor lamp, the F4 armchair orientation, the F9 coffee-table/armchair collision, and adds the missing TV unit (G1). |
| 7366 | 2 | complete_group | r_L-1b_salon_kitchen.kitchen_run | no_place: r_L-1b_salon_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Add the missing fridge to the kitchen run to satisfy G9 missing member. |
| 7367 | 2 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 6.15 m) | Move the potted plant away from the window (clears the blocked opening) and into the corner near sofa f_L-1b_046 to fix the floating finding. |
| 7368 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back to left wall to fix off-wall finding and face the room |
| 7369 | 2 | move_piece | f_L-1b_047 | acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Shift plant 0.3 m off the window sill line to clear the window opening |
| 7372 | 2 | move_piece | f_L-1b_047 | acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)); 1 more kept | Restore plant to its drawn corner spot (previous shift was rejected) |
| 7373 | 2 | move_piece | f_L-1b_048 | score: plausibility -35 -> -45 (G11 f_L-1b_005: kitchen_island f_L-1b_005: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Shift floor lamp 0.3 m off the window sill line to clear the window opening |
| 7374 | 2 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift floor lamp 0.3 m off the window sill line to clear the window opening |
| 7375 | 2 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift chair 0.3 m away from f_L-1b_058 to clear the overlap and gain clearance behind |
| 7379 | 2 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the coffee table 0.28 m away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 7380 | 2 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the floor lamp 0.3 m off the window sill line so it no longer blocks window win_L-1_002 (G12). |
| 7383 | 2 | move_piece | f_L-1_050 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Pull the armchair 0.3 m off the sofa's front zone so a 0.60 m walkway from the door reaches it (G11). |
| 7384 | 2 | move_piece | f_L-1_054 | memory: the same edit was rejected in round 1: f_L-1_054: clearance_ok; score: plausibility 27 -> 17 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050) | Shift the corner sofa 0.3 m so its front use zone is reached by a 0.60 m walkway from the door (G11). |
| 7385 | 2 | move_piece | f_L-1_072 | drawn_lock: f_L-1_072: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift the armchair 0.3 m off the window wall so its front use zone is reached by a 0.60 m walkway from the door (G11). |
| 7387 | 2 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Shift floor lamp 0.31 m off the window sill line to clear the window opening |
| 7388 | 2 | move_piece | f_L-1b_059 | acceptance: finding G6:f_L-1b_058 is still there after the edit (chair f_L-1b_058: 0.09 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift chair 0.29 m away from f_L-1b_058 to clear the overlap and gain clearance behind |
| 7390 | 2 | move_piece | f_L-1b_058 | acceptance: finding G6:f_L-1b_058 is still there after the edit (chair f_L-1b_058 is 62° off the table f_L-1b_057 (needs ≤ 45°)) | Shift chair 0.29 m away from the table edge to gain the 0.81 m pullout clearance |
| 7391 | 2 | move_piece | f_L-1b_062 | acceptance: finding G6:f_L-1b_062 is still there after the edit (chair f_L-1b_062 is 62° off the table f_L-1b_060 (needs ≤ 45°)) | Shift chair 0.29 m away from the table edge to gain the 0.81 m pullout clearance |
| 7397 | 2 | move_piece | f_L-1b_058 | acceptance: finding G6:f_L-1b_058 is still there after the edit (chair f_L-1b_058: 0.09 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift chair 0.3 m along the table edge away from f_L-1b_059 to clear the overlap |
| 7400 | 2 | move_piece | f_L-1b_062 | drawn_lock: f_L-1b_062: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Shift chair 0.3 m along the table edge away from f_L-1b_061 to clear the overlap |
| 7403 | 2 | move_piece | f_L1_009 | drawn_lock: f_L1_009: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift dining table f_L1_009 0.3 m away from chair f_L1_011 to clear the 0.341 m overlap (S2). |
| 7404 | 2 | move_piece | f_L1_009 | score: plausibility 75 -> 55 (F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_011: chair f_L1_011 is 79° off the table f_L1_009 (needs ≤ 45°)) | Shift dining table f_L1_009 0.29 m away from chair f_L1_011 to clear the 0.341 m overlap (S2). |
| 7408 | 2 | move_piece | f_L1_009 | score: plausibility 75 -> 55 (F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_011: chair f_L1_011 is 79° off the table f_L1_009 (needs ≤ 45°)) | Shift dining table f_L1_009 0.22 m away from chair f_L1_011 to clear the 0.341 m overlap (S2) while keeping the chair facing the table. |
| 7409 | 2 | move_piece | f_L1_009 | max_tries: f_L1_009 was edited 3 times in this round | Shift dining table f_L1_009 0.17 m away from chair f_L1_011 to clear the 0.341 m overlap (S2) while keeping the chair facing the table. |
| 7410 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Re-place the seating group around drawn sofa f_L1_018 so armchair f_L1_032 aligns with coffee table f_L1_024 within 2.5 m (G3). |
| 7415 | 2 | move_piece | f_L1_032 | drawn_lock: f_L1_032: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.31 m) | Move armchair f_L1_032 0.25 m closer to coffee table f_L1_024 to bring it within 2.5 m (G3). |
| 7419 | 2 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 9° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.52 m (needs ≤ 2.50 m)) | Move armchair f_L1_032 0.28 m closer to coffee table f_L1_024 to bring it within 2.5 m (G3). |
| 7422 | 2 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 8° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.57 m (needs ≤ 2.50 m)) | Move armchair f_L1_032 0.3 m closer to coffee table f_L1_024 to bring it within 2.5 m (G3). |
| 7423 | 2 | move_piece | f_L0_027 | acceptance: finding G13:f_L0_027 is still there after the edit (wardrobe f_L0_027: 0.61 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.14 m toward the door end of the top wall to open the 0.80 m front clearance (G13). |
| 7426 | 2 | move_piece | f_L1_032 | max_tries: f_L1_032 was edited 3 times in this round | Move armchair f_L1_032 0.28 m closer to coffee table f_L1_024 to bring it within 2.5 m (G3). |
| 7427 | 2 | move_piece | f_L0_027 | memory: the same edit was rejected in round 2: acceptance: finding G13:f_L0_027 is still there after the edit (wardrobe f_L0_027: 0.61 m free in front, needs ≥ 0.80 m) | Return wardrobe to its drawn position after the rejected shift. |
| 7429 | 2 | move_piece | f_L0_027 | acceptance: finding G13:f_L0_027 is still there after the edit (wardrobe f_L0_027: 0.63 m free in front, needs ≥ 0.80 m) | Nudge wardrobe 2 cm back from the top wall to restore its drawn position after the rejected shift. |
| 7433 | 2 | move_piece | f_L0_027 | max_tries: f_L0_027 was edited 3 times in this round | Restore wardrobe to its exact drawn centre after the rejected nudge. |
| 7435 | 2 | move_piece | f_L0_018 | f_L0_018: no_overlap, f_L0_048: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_048: nightstand f_L0_048 overlaps bed_double f_L0_018 by 0.11 m²; G4 f_L0_018: bed_double f_L0_018: no nightstand on the free left side of the head (0.85 m free); G4 f_L0_047: nightstand f_L0_047 of bed_double f_L0_018: 0.32 m from the bed side (needs ≤ 0.30 m); G4 f_L0_048: nightstand f_L0_048 of bed_double f_L0_018: -0.12 m from the bed side (needs ≤ 0.30 m)) | Shift bed 0.30 m toward the window wall to open ≥0.60 m on both sides of the bed (G5). |
| 7438 | 2 | move_piece | f_L0_018 | acceptance: finding G5:f_L0_018 is still there after the edit (bed_double f_L0_018: 0.55 m free along the left side, needs ≥ 0.60 m) | Restore bed to its exact drawn centre after the rejected shift. |
| 7440 | 2 | move_piece | f_L0_018 | f_L0_018: no_overlap, f_L0_048: no_overlap, score: plausibility 70 -> 67 (G4 f_L0_018: bed_double f_L0_018: no nightstand on the free right side of the head (0.42 m free); G4 f_L0_048: nightstand f_L0_048 of bed_double f_L0_018: -0.09 m from the bed side (needs ≤ 0.30 m); G5 f_L0_018: bed_double f_L0_018: 0.42 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.11 m toward the window wall to open ≥0.60 m on both sides of the bed (G5). |
| 7444 | 2 | move_piece | f_L0_018 | max_tries: f_L0_018 was edited 3 times in this round | Shift bed 0.11 m toward the desk side to open ≥0.60 m on both sides of the bed (G5). |
| 7450 | 2 | fix_fixture | f_L0_003 | fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_009) | Door d_L0_009 swings into the washbasin on one hinge side; nudge the washbasin up to 0.5 m to clear the door swing. |
| 7634 | 3 | rotate_piece | f_L-1_072 | memory: the same edit was rejected in round 1: f_L-1_072: clearance_ok; score: plausibility 27 -> 7 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2 | Rotate armchair 180° so its front faces away from the sofa back, resolving F4 orientation finding. |
| 7635 | 3 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.10 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move coffee table 0.15m away from armchair f_L-1_069 to clear the 0.12m² overlap, within 0.179m allowance. |
| 7636 | 3 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Rotate armchair f_L-1_070 to face the seating area (270°) instead of the back of the sofa, fixing F4. |
| 7638 | 3 | move_piece | f_L-1_073 | score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.09 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move table_coffee f_L-1_073 to [7.0, 1.2] to resolve the 0.12 m² overlap with armchair f_L-1_071 within the 0.3 m allowance. |
| 7639 | 3 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back to left wall to fix off-wall finding and face the room |
| 7640 | 3 | move_piece | f_L-1b_047 | memory: the same edit was rejected in round 2: acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Move plant off the window sill line to clear the window opening |
| 7642 | 3 | move_piece | f_L-1b_049 | snap: f_L-1b_049: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Move the potted plant off the window band and into the corner by the right wall, next to sofa f_L-1b_046, to clear the window and end its floating. |
| 7643 | 3 | move_piece | f_L-1b_050 | snap: f_L-1b_050: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Move the floor lamp to the right wall beside sofa f_L-1b_046 so it is no longer floating. |
| 7644 | 3 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.44 m) | Move the chair away from the window wall and off chair f_L-1b_052 to fix the overlap and give the seat 0.81 m of clearance behind it. |
| 7645 | 3 | move_piece | f_L-1_074 | acceptance: finding F9:f_L-1_074 is still there after the edit (table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.11 m²) | Move coffee table 0.15m towards the window wall (away from armchair f_L-1_069) to clear the 0.12m² overlap, within 0.179m allowance. |
| 7646 | 3 | move_piece | f_L-1b_056 | drawn_lock: f_L-1b_056: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.44 m) | Move the chair away from the window wall and off chair f_L-1b_055 to fix the overlap and give the seat 0.81 m of clearance behind it. |
| 7647 | 3 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 17 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair to face 90° (towards the room center) so it no longer faces the sofa back, resolving F4. |
| 7648 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge the end chair 0.15 m away from the table so the clearance behind it reaches the required 0.81 m. |
| 7649 | 3 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | Move coffee table 0.18m left (away from armchair f_L-1_069) to clear the 0.12m² overlap, within 0.179m allowance. |
| 7650 | 3 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 90° off the table_coffee f_L-1_074 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Rotate armchair to face 270° (towards the window wall) so it no longer faces the sofa back, resolving F4. |
| 7652 | 3 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move coffee table 0.17m right (away from armchair f_L-1_069) to clear the 0.12m² overlap, within 0.179m allowance. |
| 7653 | 3 | rotate_piece | f_L-1_072 | max_tries: f_L-1_072 was edited 3 times in this round | Rotate armchair to face 45° (towards the room center/diagonal) so it no longer faces the sofa back, resolving F4. |
| 7655 | 3 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.20 m) | Slide the potted plant 1.2 m along the right wall, out of the window band and beside sofa f_L-1b_046, to clear the window and end its floating. |
| 7656 | 3 | move_piece | f_L-1b_050 | drawn_lock: f_L-1b_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.20 m) | Slide the floor lamp 1.2 m along the right wall, out of the window band and beside sofa f_L-1b_046, so it is no longer floating. |
| 7657 | 3 | move_piece | f_L-1b_053 | acceptance: swap: F4:f_L-1b_053 replaces F9:f_L-1b_053 on f_L-1b_053 (chair does not face its group (f_L-1b_051, f_L-1b_054)): the piece keeps as many critical / major findings, so nothing is removed | Move the chair 0.29 m away from the window wall and off chair f_L-1b_052 to fix the overlap and give the seat 0.81 m of clearance behind it. |
| 7658 | 3 | move_piece | f_L-1b_056 | acceptance: swap: G6:f_L-1b_056 replaces F9:f_L-1b_056 on f_L-1b_056 (chair f_L-1b_056 is 62° off the table f_L-1b_054 (needs ≤ 45°)): the piece keeps as many critical / major findings, so nothing is removed | Move the chair 0.29 m away from the window wall and off chair f_L-1b_055 to fix the overlap and give the seat 0.81 m of clearance behind it. |
| 7659 | 3 | move_piece | f_L-1b_033 | drawn_lock: f_L-1b_033: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Nudge the end chair 0.3 m away from the table so the clearance behind it reaches the required 0.81 m. |
| 7661 | 3 | move_piece | f_L1_031 | drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.39 m) | Move armchair f_L1_031 closer to table_coffee f_L1_023 to satisfy the 2.50 m distance requirement (G3). |
| 7663 | 3 | move_piece | f_L1_031 | drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.41 m) | Move armchair f_L1_031 closer to table_coffee f_L1_023 (within 0.3 m) to satisfy the 2.50 m distance requirement (G3). |
| 7665 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 2: acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Re-solve seating around drawn sofa f_L1_018 to bring armchair f_L1_032 within 2.5 m of the coffee table (G3). |
| 7666 | 3 | move_piece | f_L1_031 | drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.43 m) | Move armchair f_L1_031 closer to table_coffee f_L1_023 (within 0.3 m) to satisfy the 2.50 m distance requirement (G3). |
| 7667 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Try solver candidate 2 to re-solve seating and bring armchair f_L1_032 within 2.5 m of the coffee table (G3). |
| 7668 | 3 | move_piece | f_L1_031 | memory: the same edit was rejected in round 3: drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.43 m) | Move armchair f_L1_031 closer to table_coffee f_L1_023 (within 0.3 m) to satisfy the 2.50 m distance requirement (G3). |
| 7669 | 3 | move_piece | f_L1_032 | memory: the same edit was rejected in round 2: acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 9° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.52 m (needs ≤ 2.50 m)) | Nudge armchair f_L1_032 0.2 m toward the coffee table to bring it within 2.5 m (G3). |
| 7670 | 3 | move_piece | f_L1_031 | memory: the same edit was rejected in round 3: drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.43 m) | Move armchair f_L1_031 closer to table_coffee f_L1_023 (within 0.3 m) to satisfy the 2.50 m distance requirement (G3). |
| 7675 | 3 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 8° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.54 m (needs ≤ 2.50 m)) | Nudge armchair f_L1_032 0.22 m toward the coffee table to bring it within 2.5 m (G3). |
| 7676 | 3 | move_piece | f_L1_032 | memory: the same edit was rejected in round 2: acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 8° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.57 m (needs ≤ 2.50 m)) | Nudge armchair f_L1_032 0.25 m toward the coffee table to bring it within 2.5 m (G3). |
| 7677 | 3 | move_piece | f_L1_032 | max_tries: f_L1_032 was edited 3 times in this round | Nudge armchair f_L1_032 0.28 m toward the coffee table to bring it within 2.5 m (G3). |
| 7680 | 3 | move_piece | f_L0_028 | f_L0_028: clearance_ok, f_L0_028: inside_room (outline: wardrobe reaches 0.12 m² through the room outline, up to 0.136 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 60 (F9 f_L0_028: wardrobe reaches 0.12 m² through the room outline, up to 0.136 m deep; G13 f_L0_028: wardrobe f_L0_028: 0.65 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.14 m along wall w_L003 to increase front clearance from 0.66 m to the required 0.80 m, within the 0.3 m move allowance. |
| 7683 | 3 | move_piece | f_L0_028 | f_L0_028: doors_free | Shift wardrobe 0.14 m along wall w_L003 (away from the door swing) to increase front clearance from 0.66 m to the required 0.80 m, within the 0.3 m move allowance. |
| 7687 | 3 | fix_fixture | f_L-1_026 | memory: the same edit was rejected in round 1: fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Washbasin stands in door d_L-1_001's swing; move it to the nearest valid spot clear of the door. |
| 7688 | 3 | move_piece | f_L0_017 | score: plausibility 70 -> 40 (F3 f_L0_017: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_017: bed_double f_L0_017: 0.54 m free along the left side, needs ≥ 0.60 m; G5 f_L0_017: bed_double f_L0_017: 0.55 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.07 m toward room center to balance side clearances, increasing both left (0.53 m) and right (0.56 m) free space to meet the 0.60 m requirement, within the 0.3 m move allowance. |
| 7689 | 3 | move_piece | f_L0_017 | f_L0_017: inside_room (outline: bed_double reaches 0.11 m² through the room outline, up to 0.070 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 30 (F3 f_L0_017: bed_double: the headboard stands in the room (0.07 m off); F9 f_L0_017: bed_double reaches 0.11 m² through the room outline, up to 0.070 m deep; G5 f_L0_017: bed_double f_L0_017: 0.54 m free along the left side, needs ≥ 0.60 m; G5 f_L0_017: bed_double f_L0_017: 0.55 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.07 m toward the left wall to keep the headboard against the wall while increasing the right-side clearance from 0.56 m to 0.63 m (≥ 0.60 m), within the 0.3 m move allowance. |
| 7691 | 3 | move_piece | f_L0_017 | f_L0_017: no_overlap, f_L0_046: no_overlap, score: plausibility 70 -> 67 (G4 f_L0_017: bed_double f_L0_017: no nightstand on the free left side of the head (0.47 m free); G4 f_L0_046: nightstand f_L0_046 of bed_double f_L0_017: -0.05 m from the bed side (needs ≤ 0.30 m); G5 f_L0_017: bed_double f_L0_017: 0.47 m free along the left side, needs ≥ 0.60 m) | Shift bed 0.07 m toward the window wall to keep the headboard against the left wall while increasing the right-side clearance from 0.56 m to 0.63 m (≥ 0.60 m), within the 0.3 m move allowance. |
| 7695 | 3 | move_piece | f_L0_017 | max_tries: f_L0_017 was edited 3 times in this round | Shift bed 0.07 m toward the desk side to keep the headboard against the left wall while increasing the left-side clearance from 0.53 m to 0.60 m (≥ 0.60 m), within the 0.3 m move allowance. |
| 7703 | 3 | fix_fixture | f_L0_003 | memory: the same edit was rejected in round 2: fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_009) | Door d_L0_009 swings into the washbasin on one hinge side (R3); move it up to 0.5 m to clear the swing. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F1 | major | f_L0_003 | r_L0_banyo | review | drawn_type | 4 | the piece is drawn and its type is one the room's types hold (the code's room rules, aliases included): drawn furniture is kept (CLAUDE.md), and a vision opinion on its type is no reading error, so it is reported for review, not retyped |
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
| S2 | minor | f_L0_010 | r_L0_yatak_odasi_3 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_027 | r_L0_yatak_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_028 | r_L0_yatak_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | critical | dec_L1_007 | r_L1_koridor | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_046 | r_L1_koridor | decor | decor_rest | 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_048 | r_L1_koridor_2 | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| lighting_dark | minor | cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | - | lighting_within_step | 1, 2, 3 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon_2 | cut | 1 | 7636 | 32768 |
| 1 | building | cut | 1 | 40106 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 2 | 9704 | 32768 |
| 2 | building | cut | 1 | 40106 | 32768 |
| 3 | building | cut | 1 | 34378 | 32768 |

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
| f_L-1_038 | piece | table_dining | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the dining table 0.04 m so it no longer cuts chair f_L-1_042 by 0.036 m (S2). |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred | - | - | front: faces the coffee table f_L-1_087 |
| f_L-1_050 | piece | armchair | r_L-1_salon_2 | inferred | - | - | front: faces the coffee table f_L-1_088 |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - | - | bathtub: r_L-1_banyo_2.bathroom_set (anchor f_L-1_052) misses shower\|bathtub, and the type's product range fits 1.83 x 0.80 m (the only missing member of that size); front: the free side facing the most room is the front |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L-1_055 in the twin room r_L-1_banyo_2 (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L-1_057 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays, f_L-1_057 is not built (plan crop recognition/crops/sym_L-1_005_ctx.png) |
| f_L-1_058 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_059 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays, f_L-1_059 is not built (plan crop recognition/crops/sym_L-1_007_ctx.png) |
| f_L-1_060 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_061 | piece | table_coffee | r_L-1_salon | inferred | - | - | table_coffee: r_L-1_salon.seating (anchor f_L-1_053) misses table_coffee, and the type's product range fits 1.30 x 0.63 m (the only missing member of that size) |
| f_L-1_062 | piece | table_coffee | r_L-1_salon_2 | inferred | - | - | table_coffee: the same footprint (1.30 x 0.63 m) as f_L-1_061 in the twin room r_L-1_salon (mirrored centre within 0.02 m) |
| f_L-1_064 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png) |
| f_L-1_066 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png) |
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
| f_L-1b_008 | piece | sink_kitchen | r_L-1b_salon_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1b_063 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_014 | piece | sink_kitchen | r_L-1b_salon | inferred | - | - | drawn inside the sink_kitchen f_L-1b_064 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1b_039 | piece | bar_stool | r_L-1b_salon_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_040 | piece | bar_stool | r_L-1b_salon | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L-1b_041 | piece | sofa | r_L-1b_salon_2 | inferred | - | - | sofa: the living room misses its seating anchor (sofa), and the type's product range fits 2.13 x 0.90 m (the only missing member of that size) |
| f_L-1b_042 | piece | sofa | r_L-1b_salon | inferred | - | - | sofa: the same footprint (2.13 x 0.90 m) as f_L-1b_041 in the twin room r_L-1b_salon_2 (mirrored centre within 0.02 m) |
| f_L-1b_043 | piece | bathtub | r_L-1b_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_055 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L-1b_044 | piece | bathtub | r_L-1b_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L-1b_043 in the twin room r_L-1b_banyo_2 (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L-1b_045 | piece | sofa | r_L-1b_salon_2 | inferred, adjusted_by_ai | - | code (reading.long_side_front) | a sofa faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: the long side facing the most room (5.83 m free); plan crop recognition/crops/sym_L-1b_007_ctx.png |
| f_L-1b_046 | piece | sofa | r_L-1b_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 (reading.long_side_front) | Snap sofa back to top wall to fix off_wall finding (plan crop recognition/crops/sym_L-1b_008_ctx.png) |
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
| f_L0_009 | piece | bed_double | r_L0_yatak_odasi_4 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_010 | piece | bed_double | r_L0_yatak_odasi_3 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_011 | piece | shower | r_L0_e_banyo | inferred | - | - | front: the free side facing the most room is the front |
| f_L0_012 | piece | shower | r_L0_e_banyo_2 | inferred | - | - | front: the free side facing the most room is the front |
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
| f_L0_029 | piece | wardrobe | r_L0_yatak_odasi_3 | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 2.09 x 0.59 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_030 | piece | wardrobe | r_L0_yatak_odasi_4 | inferred | - | - | wardrobe: the same footprint (2.09 x 0.59 m) as f_L0_029 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the nightstand 0.16 m away from the bed side to clear the 0.06 m² overlap (F9) and bring it within 0.30 m of the bed side (G4). |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_017_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_018_ctx.png); then: Move nightstand f_L0_034 away from the bed to resolve the 0.06 m² overlap (F9) and correct its position relative to the bed side (G4). |
| f_L0_035 | piece | nightstand | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_009's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_019_ctx.png) |
| f_L0_036 | piece | nightstand | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_009's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_020_ctx.png); then: Move nightstand f_L0_036 away from the bed to resolve the overlap (F9/S2) and correct its distance from the bed side (G4). |
| f_L0_037 | piece | nightstand | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_010's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_021_ctx.png) |
| f_L0_038 | piece | nightstand | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_010's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_022_ctx.png); then: Move nightstand f_L0_038 away from the bed to resolve the 0.06 m² overlap (F9) and correct its position relative to the bed side (G4). |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift sofa f_L1_019 0.3 m away from f_L1_018 to clear the blocked free zone in front of it (F6). |
| f_L1_020 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift sofa f_L1_020 away from f_L1_017 to clear the blocked free zone in front of it (F6). |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_025 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_010_ctx.png |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x975ffc83_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_036 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (bookshelf / console_table); both fit the drawn 1.09 x 0.40 m and the room: bookshelf, because the room misses it (the living room's living_storage group has no sideboard or bookshelf); plan crop recognition/crops/sym_L1_x6881d71b_ctx.png; front: its back stands on the only side on a wall |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (bookshelf / console_table); both fit the drawn 1.09 x 0.40 m and the room: bookshelf, because the AI passes of its twin f_L1_036 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png; front: its back stands on the only side on a wall |
| f_L0_039 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_023, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_007_ctx.png) |
| f_L0_040 | piece | office_chair | r_L0_yatak_odasi_3 | inferred | - | - | the chair of the desk f_L0_024, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_008_ctx.png) |
| f_L0_041 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_025, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_042 | piece | office_chair | r_L0_yatak_odasi | inferred | - | - | the chair of the desk f_L0_026, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_043 | piece | shoe_cabinet | r_L0_koridor | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the generic metal shelving render with a real 4-door shoe cabinet (0.52x0.26x1.63) that fits the 0.6x0.3 footprint and height cap |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_1 | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_2 | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_4_3 | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_4_3_after.jpg) |
| 2 | cam_r_L0_koridor_1 | ![](agent/r2_cam_r_L0_koridor_1_before.jpg) | ![](agent/r2_cam_r_L0_koridor_1_after.jpg) |
| 2 | cam_r_L0_koridor_2 | ![](agent/r2_cam_r_L0_koridor_2_before.jpg) | ![](agent/r2_cam_r_L0_koridor_2_after.jpg) |
| 2 | cam_r_L0_koridor_3 | ![](agent/r2_cam_r_L0_koridor_3_before.jpg) | ![](agent/r2_cam_r_L0_koridor_3_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- final/cam_r_L1_koridor_2_1_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_1_final_preview.jpg
- final/cam_r_L1_koridor_2_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_2_final_preview.jpg
- final/cam_r_L1_koridor_2_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_3_final_preview.jpg
- final/cam_r_L1_teras_2_1_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_1_final_preview.jpg
- final/cam_r_L1_teras_2_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_2_final_preview_2.jpg
- final/cam_r_L1_teras_2_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_3_final_preview_2.jpg
- final/ext_front_entrance_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/ext_front_entrance_final_preview.jpg
- final/cam_r_L1_koridor_2_1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_1_plan.jpg
- final/cam_r_L1_koridor_2_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_2_plan.jpg
- final/cam_r_L1_koridor_2_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_3_plan.jpg
- final/cam_r_L1_teras_2_1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_1_plan.jpg
- final/cam_r_L1_teras_2_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_2_plan_2.jpg
- final/cam_r_L1_teras_2_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_2_3_plan_2.jpg
- final/ext_front_entrance_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/ext_front_entrance_plan.jpg
