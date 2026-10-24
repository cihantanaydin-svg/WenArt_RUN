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
| JSON cross-check findings (Cycles render) | 12 |
| needs_review views | 5 |
| unverified pieces in view (sum over views) | 29 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 14 |
| exposure | -7.67 .. +2.67 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 22 view(s), -5 .. 0 EV |
| interior glazing pull | - |
| camera policy | m5 5, search 37 |
| camera score (min / mean / max) | 0.39 / 2.57 / 3.88 |
| rooms by number of views | 1 with 0, 1 with 1, 3 with 2, 10 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 5.8 min / 7.5 min / 67.8 s |
| seconds: polish / gate / check | - / - / 19.4 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 447.2 MB |
| [real04.glb](3d/real04.glb) | 1177.9 MB |

42 cameras; textures scaled to at most 1024 px (287 scaled) for the download.

## AI decor

94 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 24 rooms; 7 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

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
- camera cam_r_L1_banyo_1: no free camera point in the room; camera at the room's inner point; moved to the nearest point with 0.3 m of headroom under the sloped ceiling (1.55 m high there)
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate not_validated: the exterior views are the Cycles render (gate/gate_calibration.json missing: gate calibrate did not run or failed)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 16 piece(s) moved beyond the tolerance, 0 locked-rule violation(s)
- AI completion: 10 proposal(s) refused, reverted or not placed (listed per room)

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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.78 | D4 A1 | 1 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 1.33 | D2 A1 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | -4 | search 3.11 | D6 A2 | 1 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.33 | - | search 2.90 | D2 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | L-1 | cycles | not_run | - | - | info | - | - | +2.67 | -5 | search 2.42 | D8 A2 | 0 | no | [preview](cam_r_L-1_koridor_2_3_final_preview.jpg) [plan](cam_r_L-1_koridor_2_3_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.33 | -3 | search 3.44 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.00 | -3 | search 3.28 | D6 A4 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 3.27 | D4 A2 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | -4 | search 2.79 | D5 A2 | 2 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.50 | -4 | search 2.78 | D7 A2 | 2 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | not_run | - | - | info | - | - | +1.67 | -4 | search 2.70 | D5 A2 | 2 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 1.81 | D4 A1 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 1.43 | D2 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 0.64 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 0.39 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -1 | search 3.88 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 3.83 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.70 | D5 A3 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +1.83 | - | search 2.39 | D4 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_koridor_2 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.17 | - | search 1.96 | D3 | 0 | no | [preview](cam_r_L0_koridor_2_final_preview.jpg) [plan](cam_r_L0_koridor_2_plan.jpg) |
| cam_r_L0_koridor_3 | r_L0_koridor | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | search 1.95 | D3 | 0 | no | [preview](cam_r_L0_koridor_3_final_preview.jpg) [plan](cam_r_L0_koridor_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -4 | search 3.41 | D4 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.17 | -4 | search 2.95 | D2 A5 | 1 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | not_run | - | - | info | - | - | +2.33 | -4 | search 2.90 | D5 A2 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 2.74 | D4 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 2.55 | D5 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.43 | D3 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | -1.00 | - | search 1.64 | D2 A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 3.34 | D3 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.00 | - | search 2.84 | D3 A1 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_koridor_3 | r_L1_koridor | L1 | cycles | not_run | - | - | info | - | - | +1.33 | - | search 2.58 | D2 | 0 | no | [preview](cam_r_L1_koridor_3_final_preview.jpg) [plan](cam_r_L1_koridor_3_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.83 | - | search 3.21 | D5 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.67 | -3 | search 3.09 | D4 A1 | 0 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | not_run | - | - | info | - | - | +0.67 | -3 | search 3.08 | D6 A1 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 2.39 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 2.19 | D3 A4 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 2.02 | D1 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.67 | 0 | m5 blocked | D6 | 0 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D5 | 0 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
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
| r_L0_yatak_odasi_3 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3 |
| r_L0_yatak_odasi_4 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L1_banyo | bathroom | L1 | 1 | 0 | 1 | cam_r_L1_banyo_1 |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 3 | 0 | 3 | cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3 |
| r_L1_koridor_2 | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | other | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 |
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
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 23 % of its pixels > 0.10 m outside the drawing, 571812 px |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90 | yes | 22 % of its pixels > 0.10 m outside the drawing, 22780 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90 | yes | 21 % of its pixels > 0.10 m outside the drawing, 22802 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90 | yes | 33 % of its pixels > 0.10 m outside the drawing, 22022 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 27 % of its pixels > 0.10 m outside the drawing, 9937 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90 | yes | 65 % of its pixels > 0.10 m outside the drawing, 6959 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90 | yes | 57 % of its pixels > 0.10 m outside the drawing, 5849 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1669 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1316 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 973 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1086 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 55 % of its pixels > 0.10 m outside the drawing, 7167 px |

## Needs review

- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: f_L0_007
- ext_1: json cross-check misplaced: win_L0_001
- ext_2: json cross-check misplaced: win_L0_004
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
- f_L1_035
- f_L1_036
- f_L1_037
- f_L1_038
- f_L0_035
- f_L0_036
- f_L0_037
- f_L0_038

Unverified pieces in view:

- cam_r_L-1_banyo_1: f_L-1_056
- cam_r_L-1_koridor_2_1: f_L-1_053
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_071
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061
- cam_r_L0_banyo_1: f_L0_025
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_e_yatak_odasi_2: f_L0_023
- cam_r_L0_e_yatak_odasi_3: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_019
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_038
- cam_r_L0_yatak_odasi_3_1: f_L0_029, f_L0_037
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037
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
| f_L-1_053 | furniture | sofa_corner | 3dwh_fec63d27ea3695ada8319828 | the vision check sees more than one object |
| f_L-1_087 | furniture | table_coffee | 3dwh_f2d78684d4e41a5b93b167d0 | the vision check says it is not a table_coffee (a table_dining) |
| f_L-1_088 | furniture | table_coffee | 3dwh_f2d78684d4e41a5b93b167d0 | the vision check says it is not a table_coffee (a table_dining) |
| f_L-1_096 | furniture | fridge | hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 | vision quality 2 (<= 2) |
| f_L0_015 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_016 | furniture | toilet | objaverse_3446229dce1f47528fa871cc7669136c | vision quality 2 (<= 2) |
| f_L0_023 | furniture | wardrobe | 3dwh_e41345920f4dce2514160e34 | the vision check says it is not a wardrobe |
| f_L0_024 | furniture | wardrobe | abo_B015IPNVFW | vision quality 2 (<= 2) |
| f_L1_005 | furniture | table_dining | round_wooden_table_02 | the vision check says it is not a table_dining (a side_table) |
| f_L1_009 | furniture | table_dining | abo_B07M6PKC6B | the vision check says it is not a table_dining (a side_table) |
| f_L1_015 | furniture | washbasin | hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 | the vision check says it is not a washbasin (a dresser) |
| f_L1_028 | furniture | wardrobe | abo_B07GFSJ69T | vision quality 2 (<= 2) |
| f_L1_043 | furniture | table_dining | abo_B07ML7P94G | the vision check says it is not a table_dining (a side_table) |
| f_L1_052 | furniture | table_dining | 3dwh_61d3ec6b31b39c2256ef4df4 | the vision check says it is not a table_dining (a side_table) |

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
| c_017 | area_label_vs_computed | r_L0_yatak_odasi | Label says 16,00 m², polygon gives 16,13 m² (0.8%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_018 | area_label_vs_computed | r_L0_e_yatak_odasi | Label says 17,00 m², polygon gives 16,86 m² (0.8%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_019 | area_label_vs_computed | r_L0_e_yatak_odasi_2 | Label says 17,00 m², polygon gives 16,87 m² (0.8%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_020 | area_label_vs_computed | r_L0_yatak_odasi_2 | Label says 16,00 m², polygon gives 16,12 m² (0.7%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_021 | area_label_vs_computed | r_L0_koridor | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_022 | area_label_vs_computed | r_L0_koridor_2 | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_023 | area_label_vs_computed | r_L0_yatak_odasi_3 | Label says 17,00 m², polygon gives 14,05 m² (17.3%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_024 | area_label_vs_computed | r_L0_yatak_odasi_4 | Label says 17,00 m², polygon gives 14,04 m² (17.4%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_025 | area_label_vs_computed | r_L0_banyo | Label says 4,90 m², polygon gives 4,97 m² (1.5%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_026 | area_label_vs_computed | r_L0_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_027 | area_label_vs_computed | r_L1_teras | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_028 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_029 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_030 | area_label_vs_computed | r_L1_koridor | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_031 | area_label_vs_computed | r_L1_koridor_2 | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_032 | area_label_vs_computed | r_L1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_033 | area_label_vs_computed | r_L1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from deneme1.dwg |
| c_034 | area_label_vs_computed | r_L1_teras_2 | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from deneme1.dwg kept |
| c_035 | outline_mismatch | L0, L-1 | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_036 | outline_mismatch | L0, L-1b | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_037 | outline_mismatch | L0, L1 | Outer wall outline of Çatı Katı differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_038 | outline_mismatch | r16, r5 | sheets.json sc_002: level L0: 2 drawings in deneme1.dwg; r16 (15.17 x 12.00 m) matches r11 of level L-1 (15.17 x 12.00 m) and is read; r5 (17.17 x 12.00 m) not used | r16 read (its outline matches the adjacent level); r5 ignored |
| c_039 | type_disagreement | f_L-1_067 | f_L-1_067: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_040 | type_disagreement | f_L-1_068 | f_L-1_068: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_041 | type_disagreement | f_L-1b_064 | f_L-1b_064: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_042 | type_disagreement | f_L-1b_069 | f_L-1b_069: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_043 | type_disagreement | f_L-1b_070 | f_L-1b_070: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_044 | type_disagreement | f_L1_027 | f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes) | typed wardrobe (trust order: vector geometry and block names > AI) |
| c_045 | type_disagreement | f_L1_028 | f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes) | typed wardrobe (trust order: vector geometry and block names > AI) |
| c_046 | symbol_type_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_047 | symbol_type_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_048 | symbol_type_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_049 | symbol_type_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L-1_073 | f_L-1_073: sym_L-1_021: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L-1_087 | f_L-1_087: sym_L-1_035: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L-1b_045 | f_L-1b_045: sym_L-1b_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_046 in the twin room r_L-1b_salon named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_053 | symbol_type_disagreement | f_L-1b_046 | f_L-1b_046: sym_L-1b_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | typed sofa by code (not kitchen_island): the AI passes of its twin f_L-1b_045 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_054 | symbol_type_disagreement | f_L-1b_047 | f_L-1b_047: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_055 | symbol_type_disagreement | f_L-1b_049 | f_L-1b_049: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | typed potted_plant by code (not floor_lamp): the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_056 | symbol_type_disagreement | f_L-1b_065 | f_L-1b_065: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_057 | symbol_type_disagreement | f_L-1b_066 | f_L-1b_066: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_058 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L1_029 | f_L1_029: sym_L1_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the room misses it (the living room's reading_corner group has no armchair); inferred, listed in the report (reading.tie_break) |
| c_063 | symbol_type_disagreement | f_L1_030 | f_L1_030: sym_L1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_064 | symbol_type_disagreement | f_L1_031 | f_L1_031: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_065 | symbol_type_disagreement | f_L1_032 | f_L1_032: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_066 | symbol_type_disagreement | f_L1_036 | f_L1_036: sym_L1_x6881d71b: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the room misses it (the living room's living_storage group has no sideboard or bookshelf or display_cabinet); inferred, listed in the report (reading.tie_break) |
| c_067 | symbol_type_disagreement | f_L1_037 | f_L1_037: sym_L1_x59e6f5f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sideboard, pass 2 (zai-org/GLM-4.6V-Flash) bench | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L1_038 | f_L1_038: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed bookshelf by code (not console_table): the AI passes of its twin f_L1_036 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_069 | other | r_L-1b_salon | r_L-1b_salon: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_070 | other | r_L-1b_salon_2 | r_L-1b_salon_2: one face holds the room names 'Salon' and 'AÇIK MUTFAK' | unresolved: first label kept, room unverified |
| c_071 | symbol_front_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_072 | symbol_front_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_073 | symbol_front_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_074 | symbol_front_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_075 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_076 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_077 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_078 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_079 | symbol_front_disagreement | f_L0_027 | f_L0_027: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_080 | symbol_front_disagreement | f_L0_028 | f_L0_028: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_081 | symbol_front_disagreement | f_L0_029 | f_L0_029: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_082 | symbol_front_disagreement | f_L0_030 | f_L0_030: sym_L0_012: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L1_029 | f_L1_029: sym_L1_007: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L1_030 | f_L1_030: sym_L1_008: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L1_031 | f_L1_031: sym_L1_009: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L1_032 | f_L1_032: sym_L1_010: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | unit_mismatch | r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21 | sheets.json sc_001: deneme1.dwg: $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_088 | section_width_mismatch | r19 | sheets.json sc_003: section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 15.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 21 regions (use: exterior 1, heights 2, ignored 14, read 4). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | deneme1.dwg | floor_plan | ai (0.95) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r2 | deneme1.dwg | floor_plan | ai (0.95) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r3 | deneme1.dwg | title_block | ai (0.99) | unverified | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) |
| r4 | deneme1.dwg | other | none (0.00) | unverified | - | - | ignored (no title and no geometry rule gives a class) |
| r5 | deneme1.dwg | floor_plan | title (0.99) | verified | L0 | - | ignored (another drawing of level L0 whose outline (17.17 x 12.00 m) does not match the adjacent levels; r16 (15.17 x 12.00 m, as r11) is read) |
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
| L0 | Zemin Kat | floor | r16 | - |
| L1 | Çatı Katı | attic | r18 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r11, r16, r18 |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r15, r16, r18 |

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
| sc_002 | outline_mismatch | level L0: 2 drawings in deneme1.dwg; r16 (15.17 x 12.00 m) matches r11 of level L-1 (15.17 x 12.00 m) and is read; r5 (17.17 x 12.00 m) not used | r16 read (its outline matches the adjacent level); r5 ignored |
| sc_003 | section_width_mismatch | section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 15.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

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
- level L0: 2 drawings in deneme1.dwg; r16 (15.17 x 12.00 m) matches r11 of level L-1 (15.17 x 12.00 m) and is read; r5 (17.17 x 12.00 m) not used
- the largest drawn polylines of the plans differ in size: r11 (L-1) LWPOLYLINE:366F8 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r15 (L-1b) LWPOLYLINE:2C4A5 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r16 (L0) LWPOLYLINE:2DA7F on DBM_w_sld 7.59 x 10.50 m (open, ends 0.40 m apart); r18 (L1) LWPOLYLINE:2F87A on _P3_S_Duvar_Ç 11.77 x 8.60 m (closed); the registered outlines (all long strokes, columns included) give residuals r11 0.0001, r15 0.0001, r18 0.0001 m; each level is kept as drawn
- 2 sections: heights from r19; r20 not read for heights
- section r19: no cut line on the plans: the section's left end is taken as the building's min side along the cut axis (flipped unknown)
- section r19: the cut direction is unknown: the ground levels keep the section's left/right
- roof: the break line on r18 (LWPOLYLINE:2F87A) is 8.60 m wide along the cut, the section's slope changes 7.80 m apart (0.80 m); both kept as drawn
- site plan r14: 36 tree symbols in a row (25.6 m): read as the hedge hedge_001 (mid, 1.2 m assumed), not as trees
- site plan r14: 30 tree symbols in a row (20.9 m): read as the hedge hedge_002 (mid, 1.2 m assumed), not as trees
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
| L0 | Zemin Kat | floor | 0,00 m (section) | 3,00 m (section) | base | r16 |
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
- 0 boundary wall(s), 27 decor item(s) built
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
| d_L0_011 | 0,00 m | 0,00 m | 0,00 m | none | yes |
| d_L0_012 | 0,00 m | 0,00 m | 0,00 m | none |  |

Inferred (listed, CLAUDE.md evidence rules):

- site.plinth: no SB. mark: the plinth up to the ground floor
- light_well win_L-1_003: window sill -2.10 m, ground outside -1.67 m: an open concrete light well 0.8 m deep, 4.56 m wide (no light well drawn)
- front_court win_L-1_004: window sill 1.18 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn)

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 20 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_059, f_L-1_060, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_073, f_L-1_075, f_L-1_077

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_095: bookshelf 0.60 x 0.30 (confidence -, rule, mirrored from f_L-1_089)
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

- added f_L-1b_082: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): mirrored (decisions of r_L-1b_koridor (twin), not asked again)

- added f_L-1b_086: console_table 0.90 x 0.30 (confidence -, rule, mirrored from f_L-1b_082)
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

- added f_L1_046: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_047: potted_plant 0.45 x 0.45 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed seating: no free place passed the placer checks (no candidate position fits the room)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_006, f_L1_007, f_L1_013, f_L1_017, f_L1_020, f_L1_035, f_L1_036

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_049: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L1_046)
- added f_L1_050: potted_plant 0.45 x 0.45 (confidence -, rule, mirrored from f_L1_047)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_010, f_L1_011, f_L1_014, f_L1_018, f_L1_019, f_L1_037, f_L1_038

### Koridor (r_L1_koridor, hall): completed

- added f_L1_048: shoe_cabinet 0.60 x 0.25 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_027

### Koridor (r_L1_koridor_2, hall): mirrored (decisions of r_L1_koridor (twin), not asked again)

- added f_L1_051: shoe_cabinet 0.60 x 0.25 (confidence -, rule, mirrored from f_L1_048)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_028

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_021, f_L1_025

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_016, f_L1_022, f_L1_026

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 234 of 234 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 218 ok, 16 failed; 56 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_042 | chair (chair) | 0.14 | 0.00 | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.12 | 0.00 | - | - |
| f_L-1b_046 | sofa (sofa) | 1.15 | 0.00 | - | - |
| f_L-1b_050 | floor_lamp (floor_lamp) | 1.11 | - | - | front missing on one side |
| f_L0_010 | wardrobe (wardrobe) | 0.70 | 0.00 | yes | - |
| f_L0_032 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_019 | sofa (sofa) | 0.29 | 0.00 | - | - |
| f_L1_020 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_031 | armchair (armchair) | 0.29 | 0.00 | - | - |
| f_L1_032 | armchair (armchair) | 0.28 | 0.00 | - | - |

## Exterior views

5 of 5 exterior view(s) of variant `base` rendered; 2 dropped (no camera place worked).

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)
- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **not_validated** (exterior views stay the Cycles render): gate/gate_calibration.json missing: gate calibrate did not run or failed.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | yes |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok | yes |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | - | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: ok; left: unverified | yes |
| ext_7 | aerial | - | - | cycles (gate_validation) | ok | right: unverified | yes |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_4 | corner | left, back | 12.5 m from the building corner, 30 degrees off the back facade: 80% of the view of the building is blocked by trees, the plot wall or another building; 14.5 m from the building corner, 30 degrees off the back facade: 68% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m from the building corner, 30 degrees off the back facade: 53% of the view of the building is blocked by trees, the plot wall or another building; 11.0 m from the building corner, 30 degrees off the back facade: 91% of the view of the building is blocked by trees, the plot wall or another building; 18.5 m from the building corner, 30 degrees off the back facade: 46% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m from the building corner, 30 degrees off the back facade: the building fills 7% of the frame (< 8%); 24.5 m from the building corner, 30 degrees off the back facade: 35% of the view of the building is blocked by trees, the plot wall or another building |
| ext_6 | frontal | back | 17.5 m in front of the back (entrance) facade: inside the copy; 19.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 16.0 m in front of the back (entrance) facade: inside the copy; 23.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 26.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 29.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building |

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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_koridor_2_3, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_koridor_2, cam_r_L0_koridor_3, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_koridor_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 42 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3 | 0 / 14 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| deneme1.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 23, block_name 58, group_member 7, inferred 14, level 3, nightstand_symbol 4, none 25, rule 90, twin 10. Recognition questions: 70; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

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
| f_L0_027 | r_L0_yatak_odasi_2 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_028 | r_L0_yatak_odasi_4 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_029 | r_L0_yatak_odasi_3 | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_030 | r_L0_yatak_odasi | desk | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_031 | r_L0_e_yatak_odasi | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_032 | r_L0_e_yatak_odasi | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_033 | r_L0_e_yatak_odasi_2 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.80 |
| f_L0_034 | r_L0_e_yatak_odasi_2 | nightstand | no (typed by nightstand_symbol) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_031 | r_L1_oyun_aktivite_ve_dinlenme_odasi | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_032 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | armchair | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_033 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_034 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | verified | no (drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_035 | r_L1_oyun_aktivite_ve_dinlenme_odasi | console_table | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bench, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
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
| - | decor | other x 6, tree x 21 |

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
| area_light | 1 | r_L1_banyo_2: room has no window; the room's light rig (1 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L1_banyo_2 |
| area_light | 1 | r_L1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor |
| area_light | 1 | r_L1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| area_light | 4 | r_L1_teras: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras, light_r_L1_teras_2, light_r_L1_teras_3 |
| area_light | 4 | r_L1_teras_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras_2.001, light_r_L1_teras_2_2, light_r_L1_teras_2_3 |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (+y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 3 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_007, dress_f_L0_021, dress_f_L0_022 |
| cabinet_fronts | 6 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L-1_091, furn_f_L-1_092, furn_f_L-1_093 |
| climate | 1 | the drawing's language (room and site labels) (inferred; the species of trees and hedges follow it): banyo, havuz, mutfak, oda, otopark, salon, teras, yatak | site |
| direction | 4 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 22 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1_001_handle, d_L-1_002_handle, d_L-1_003_handle |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade | 1 | style profile exterior.facade (assumed) | exterior |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| handrail | 4 | design detail on every flight side not against a wall; not in the documents | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| hedge | 1 | 30 tree symbols of radius 0.36 m at a pitch of 0.72 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_002 |
| hedge | 1 | 36 tree symbols of radius 0.36 m at a pitch of 0.73 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_001 |
| hedge | 2 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_003, hedge_004 |
| hedge:hedge_001 | 1 | 36 tree symbols of radius 0.36 m at a pitch of 0.73 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_001:fit | 1 | hedge hedge_001: its 0.72 m hull kept on its planting side of sp_003, sp_003_s1e14, sp_004_s2e8 (moved up to 0.50 m, narrowed to 0.66 m; a row drawn along a terrace edge or a wall is planted beside it, inferred) | site |
| hedge:hedge_002 | 1 | 30 tree symbols of radius 0.36 m at a pitch of 0.72 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_003 | 1 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_003:fit | 1 | hedge hedge_003: its 0.72 m hull kept on its planting side of sp_001 (moved up to 0.22 m; a row drawn along a terrace edge or a wall is planted beside it, inferred) | site |
| hedge:hedge_004 | 1 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
| hedge:hedge_004:fit | 1 | hedge hedge_004: its 0.72 m hull kept on its planting side of sp_004 (moved up to 0.15 m; a row drawn along a terrace edge or a wall is planted beside it, inferred) | site |
| height | 22 | door height listed as assumed in the building JSON | d_L-1_001, d_L-1_002, d_L-1_003 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.06 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) | d_L1_004, d_L1_005 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.76 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_003, d_L1_006 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.85 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_001, d_L1_002 |
| height | 6 | no height in the JSON; type height for armchair | furn_f_L-1_049, furn_f_L-1_050, furn_f_L-1_069 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L0_007, furn_f_L0_008 |
| height | 1 | no height in the JSON; type height for bench | furn_f_L1_037 |
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 1 | no height in the JSON; type height for console_table | furn_f_L1_035 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L-1_058, furn_f_L-1_060, furn_f_L-1_063 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 4 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_035, furn_f_L0_036, furn_f_L0_037 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_013, furn_f_L0_014 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1_008, furn_f_L-1_017 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 8 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024, furn_f_L0_009 |
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
| modules | 10 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| parapet | 1 | roof terrace ro_001: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn | roof |
| parapet_height:ro_002 | 1 | not drawn | roof |
| path:d_L0_011 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path:d_L0_012 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
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
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_ceiling | 1 | no ceiling over a fixture in r_L0_merdiven: its best spot (4.74, 9.72) is 0.02 m from the room's edge or a ceiling opening (stair, slab opening to the level above), the fixture needs 0.15 m: no ceiling fixture | rig_r_L0_merdiven |
| rig_ceiling | 1 | no ceiling over a fixture in r_L0_merdiven_2: its best spot (9.00, 9.72) is 0.02 m from the room's edge or a ceiling opening (stair, slab opening to the level above), the fixture needs 0.15 m: no ceiling fixture | rig_r_L0_merdiven_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_009; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_011; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
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
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_025; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_027; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_026 (top 2.37 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_019; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_018 (top 2.53 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_021; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside lamp on the nightstand f_L0_032; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside light in the shade of the table lamp dec_L0_014 on f_L0_031 beside the bed f_L0_007; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside lamp on the nightstand f_L0_034; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_032 on f_L0_033 beside the bed f_L0_008; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the plant_small dec_L0_007); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_041 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the plant_small dec_L0_042); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside lamp on the nightstand f_L0_043; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside wall sconce on the head wall beside the bed f_L0_021 (no nightstand, no lamp); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside lamp on the nightstand f_L0_046; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside wall sconce on the head wall beside the bed f_L0_022 (no nightstand, no lamp); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_mirror | 1 | mirror light over the washbasin f_L1_015: the mirror dec_L1_008 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo |
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
| tree | 21 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| waist | 4 | the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_0aeba5bbe2589951a26b2cc9 [non_commercial], 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial], 3dwh_56d1c005237fa418b00eede5 [non_commercial], 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_9314d5619fde2de825a4a2a1 [non_commercial], 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_cf8a7127be5783e2fc5e61ae [non_commercial], 3dwh_dff7590ce6f78822c852419d [non_commercial], 3dwh_e41345920f4dce2514160e34 [non_commercial], 3dwh_fec63d27ea3695ada8319828 [non_commercial], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: 3dwh_0aeba5bbe2589951a26b2cc9 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial], 3dwh_9314d5619fde2de825a4a2a1 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: 3dwh_0aeba5bbe2589951a26b2cc9 [non_commercial], 3dwh_9314d5619fde2de825a4a2a1 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_fec63d27ea3695ada8319828 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: yes
- cam_r_L-1_koridor_2_3: commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: 3dwh_dff7590ce6f78822c852419d [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_fec63d27ea3695ada8319828 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_fec63d27ea3695ada8319828 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_fec63d27ea3695ada8319828 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: 3dwh_4799895b90ee49a1f4cd032a [non_commercial], 3dwh_9314d5619fde2de825a4a2a1 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: 3dwh_4799895b90ee49a1f4cd032a [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_9314d5619fde2de825a4a2a1 [non_commercial])
- cam_r_L0_e_banyo_2: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_9314d5619fde2de825a4a2a1 [non_commercial])
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_e41345920f4dce2514160e34 [non_commercial])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_56d1c005237fa418b00eede5 [non_commercial], 3dwh_e41345920f4dce2514160e34 [non_commercial], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_56d1c005237fa418b00eede5 [non_commercial], 3dwh_e41345920f4dce2514160e34 [non_commercial], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_koridor_2: commercial-safe: yes
- cam_r_L0_koridor_3: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_plant_small_japandi_1_32d3b9fb [tool_nc])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_plant_small_japandi_1_32d3b9fb [tool_nc])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_3_2: commercial-safe: yes
- cam_r_L0_yatak_odasi_3_3: commercial-safe: yes
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: yes
- cam_r_L1_koridor_2: commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial])
- cam_r_L1_koridor_3: commercial-safe: yes
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial])
- cam_r_L1_teras_3: commercial-safe: yes
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_cf8a7127be5783e2fc5e61ae [non_commercial])

## Built below library level (Milestone 13)

42 furniture piece(s) built from a module builder or a parametric family instead of a library model: 2 library gap(s) to close with a real model, 40 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 4), cam_r_L1_teras_2 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.0 degrees off the sun, sky pull k 2), ext_5 (5.6 degrees off the sun, sky pull k 0).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (70 of 70 answered); sheets/requests.json (8 of 8 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (70 of 70 answered); sheets/requests.json (8 of 8 answered) |

Assets: textures CC0 x 17; furniture/decor models 3DWH-UNREVIEWED x 62, CC-BY-4.0 x 142, CC-BY-NC-4.0 x 62, CC0 x 1, generated (Infinigen v1.19.0, BSD-3-Clause) x 2, generated (TRELLIS.2-4B, MIT) x 10 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 42 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for f_L0_015, f_L0_016)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_003)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261023-222215-full-20261023T222740Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 54.8 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 2.0 min | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| style | ok | 0.4 s | - |
| recognize | ok | 12.4 s | - |
| pipeline_final | ok | 2.9 min | answers applied |
| fit | ok | 9.6 s | - |
| layout | ok | 38.4 s | - |
| decor_ask | ok | 2.1 min | - |
| photos | reused | 0.3 s | - |
| assets | ok | 4.1 s | - |
| decor | ok | 8.7 s | - |
| agent_apply | ok | 28.5 s | - |
| refit | ok | 56.2 s | - |
| build | ok | 25.1 min | - |
| agent_previews | ok | 4.4 min | 6 view(s) |
| agent | ok | 33.9 min | 4 round(s), 23 finding(s) removed by 20 accepted edit(s) (measured; 28 predicted by the dry re-checks), 8 new, net 15, 162 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 10.3 min | - |
| export | ok | 99.1 s | - |
| controls | ok | 2.5 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 104.7 s | - |
| check | ok | 2.9 min | - |
| combine | ok | 30.1 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 20 edit(s) accepted, 162 rejected, 432 model calls (6807589 tokens), 38.7 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 7883): earlier runs of the appended log are left out (7882 events, 2586 model calls, 301 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 20 / 162 (11 % accepted) |
| rejected by reason | acceptance 40, drawn_lock 30, score 20, max_tries 14, memory 13 |
| rooms checked by code / vision / planner | 38 / 14 / 16 |
| rooms with fixable critical or major findings visited | 16 of 16 |
| critical before -> after | 2 -> 3 |
| major before -> after | 111 -> 95 |
| agent minutes; first accepted edit after | 34.48; 72.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 13; 60; 46 (31) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 23 measured; 28 predicted |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 8 new; net 15 |
| edits removing their finding | 14 of 19 |
| plans ok / empty / refused / default | 31 / 14 / 1 / 0 |

Library gaps reported by the agent: wardrobe (The current wardrobe model (abo_B07GFS1VB6) renders as a solid opaque block blocking the corridor (F9 wrong_model); the only alternative tried (abo_B07H8V7P3H) fails the fit rules under the sloped ceiling, so no audited library model of a functional wardrobe fits this 1.52 x 0.60 m slot.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 2 | 111 | 67 | 2 | 9 | 66 | layout | 9 |
| 2 | 3 | 99 | 63 | 2 | 4 | 56 | refit | 0 |
| 3 | 3 | 99 | 63 | 2 | 7 | 36 | refit | 6 |
| 4 | 3 | 95 | 62 | 2 | 0 | 4 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| D2 | 0 | 10 | 0 | 0 |
| F1 | 0 | 4 | 7 | 0 |
| F2 | 0 | 8 | 0 | 0 |
| F3 | 0 | 20 | 4 | 0 |
| F4 | 0 | 15 | 0 | 0 |
| F6 | 0 | 2 | 0 | 0 |
| F8 | 0 | 15 | 0 | 0 |
| F9 | 11 | 36 | 0 | 0 |
| G1 | 0 | 0 | 40 | 0 |
| G10 | 0 | 72 | 0 | 0 |
| G11 | 0 | 28 | 0 | 0 |
| G12 | 0 | 16 | 0 | 0 |
| G13 | 0 | 15 | 0 | 0 |
| G14 | 0 | 0 | 7 | 0 |
| G2 | 0 | 0 | 21 | 0 |
| G3 | 0 | 4 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 32 | 0 | 0 |
| G6 | 0 | 30 | 24 | 0 |
| G8 | 0 | 16 | 16 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 8 | 0 |
| NR | 0 | 16 | 0 | 0 |
| R3 | 0 | 0 | 40 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S2 | 0 | 31 | 22 | 0 |
| S4 | 0 | 0 | 4 | 0 |
| S5 | 0 | 0 | 16 | 0 |
| X2 | 0 | 8 | 8 | 0 |
| X3 | 0 | 8 | 0 | 8 |
| X6 | 0 | 4 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 8110 | 1 | relayout_room | r_L-1b_salon_2 | adjusted_by_ai | 0.0 -> 0.0 | Re-place AI pieces so the kitchen run can take its missing fridge and the seating group gets its TV unit and coffee table. | ![](agent/r1_044_relayout_room_before_r_L-1b_salon_2.png) | ![](agent/r1_047_relayout_room_after_r_L-1b_salon_2.png) |
| 8138 | 1 | move_piece | f_L1_019 | adjusted_by_ai | 65.0 -> 75.0 | Shift sofa f_L1_019 away from f_L1_018 to clear the blocked free zone in front of it (F6). | ![](agent/r1_067_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_068_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 8144 | 1 | move_piece | f_L1_032 | adjusted_by_ai | 75.0 -> 85.0 | Nudge armchair f_L1_032 toward the coffee table to bring it within 2.5 m (G3). | ![](agent/r1_073_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_074_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 8146 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 90.0 -> 100.0 | Try solver candidate 2 (score 10.14) which may place the plant closer to a wall or seating, fixing F8 while also fixing the F1 dining-type findings. | ![](agent/r1_077_relayout_room_before_r_L1_teras.png) | ![](agent/r1_079_relayout_room_after_r_L1_teras.png) |
| 8151 | 1 | swap_model | f_L1_005 | adjusted_by_ai | 55.0 -> 55.0 | The dining table renders as a low flat surface; swap to a proper round dining table model (0.80 m, matches the drawn 0.78 m) to fix the wrong_model visual. | ![](agent/r1_081_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_083_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 8154 | 1 | move_piece | f_L1_020 | adjusted_by_ai | 55.0 -> 65.0 | Shift sofa f_L1_020 0.3 m away from f_L1_017 to clear the blocked free zone in front of it (F6). | ![](agent/r1_084_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_085_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 8158 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift the right nightstand away from the bed edge to clear the 0.06 m² overlap and satisfy the ≤0.30 m side gap. | ![](agent/r1_090_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_092_move_piece_after_r_L0_e_yatak_odasi.png) |
| 8168 | 1 | swap_model | f_L0_023 | adjusted_by_ai | 100.0 -> 100.0 | Replace the crude, flat low-poly wardrobe model with a detailed 3.15 m modern wardrobe matching the drawn 3.11 m footprint. | ![](agent/r1_099_swap_model_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_100_swap_model_after_r_L0_e_yatak_odasi.png) |
| 8198 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. | ![](agent/r1_116_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_117_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 8416 | 2 | move_piece | f_L-1_039 | adjusted_by_ai | 27.0 -> 27.0 | Shift the chair 0.03 m away from the table edge to clear the 0.039 m cut with table f_L-1_038. | ![](agent/r2_035_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_037_move_piece_after_r_L-1_salon_2.png) |
| 8447 | 2 | move_piece | f_L-1b_050 | adjusted_by_ai | 0.0 -> 0.0 | Snap the floor lamp's back to the right wall (w_L-1b_010) at its drawn position so it is no longer floating (F8). | ![](agent/r2_067_move_piece_before_r_L-1b_salon.png) | ![](agent/r2_068_move_piece_after_r_L-1b_salon.png) |
| 8456 | 2 | report_library_gap | f_L1_027 | library_gap | - | The current wardrobe model (abo_B07GFS1VB6) renders as a solid opaque block blocking the corridor (F9 wrong_model); the only alternative tried (abo_B07H8V7P3H) fails the fit rules under the sloped ceiling, so no audited library model of a functional wardrobe fits this 1.52 x 0.60 m slot. | - | - |
| 8457 | 2 | move_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.living_storage | adjusted_by_ai | 85.0 -> 85.0 | Move bookshelf+plant group to the free west wall span to clear the bookshelf-plant overlap, the plant-wall cut and the plant size anomaly (c:S2:f_L1_049, c:S2:f_L1_050, c:S4:f_L1_050). | ![](agent/r2_077_move_group_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_079_move_group_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 8696 | 3 | move_piece | f_L-1b_046 | adjusted_by_ai | 0.0 -> 0.0 | Sofa f_L-1b_046 is 0.59 m off the wall (F3); snap its back to the free span of wall w_L-1b_004 (s3) to put it on a wall. | ![](agent/r3_035_move_piece_before_r_L-1b_salon.png) | ![](agent/r3_036_move_piece_after_r_L-1b_salon.png) |
| 8709 | 3 | move_piece | f_L-1_042 | adjusted_by_ai | 27.0 -> 27.0 | c:S2:f_L-1_038#2: move chair f_L-1_042 0.14 m away from the dining table to clear the 0.038 m cut. | ![](agent/r3_045_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_047_move_piece_after_r_L-1_salon_2.png) |
| 8720 | 3 | move_piece | f_L1_031 | adjusted_by_ai | 65.0 -> 75.0 | Bring armchair within 2.50 m of the coffee table to fix G3. | ![](agent/r3_054_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_055_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 8724 | 3 | retype_piece | f_L1_035 | adjusted_by_ai | 75.0 -> 78.0 | Bench is not a valid piece for this room (F1/G14); a console table fits its 1.4m x 0.45m footprint and the room. | ![](agent/r3_056_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_058_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 8726 | 3 | move_piece | f_L1_009 | adjusted_by_ai | 85.0 -> 85.0 | Re-solve the dining group around the drawn table so the two chairs stop cutting the table (S2 x2). | ![](agent/r3_060_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_061_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 8733 | 3 | move_piece | f_L1_057 | added_by_ai | 85.0 -> 85.0 | Move the potted plant away from the bookshelf and out of wall w_L1_012, keeping the sofa's front zone clear (S2 x2). | ![](agent/r3_069_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_071_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 8758 | 3 | move_piece | f_L0_010 | adjusted_by_ai | 70.0 -> 80.0 | Shift the wardrobe along its wall to open the 0.80 m front clearance (currently 0.66 m). | ![](agent/r3_082_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r3_083_move_piece_after_r_L0_yatak_odasi.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 8097 | 1 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_053 is still there after the edit (sofa_corner f_L-1_053: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 4 more kept | Re-solve seating and living storage with solver candidate 1 to fix G11 walkway clearance for sofa and armchairs, the sofa/coffee-table S2 collision, the armchair F4 orientation, and add the missing TV unit (G1). |
| 8098 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn the armchair away from the sofa back so it faces into the room, fixing F4 orientation. |
| 8099 | 1 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.37 m) | Shift the coffee table away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 8101 | 1 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the coffee table 0.28 m away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 8102 | 1 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.08 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Shift the coffee table 0.27 m away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 8103 | 1 | complete_group | r_L-1b_salon_2.seating | acceptance: finding G1:f_L-1b_041 is still there after the edit (sofa f_L-1b_041 has no TV unit opposite) | Sofa f_L-1b_041 is floating 2.00 m off the wall and missing its TV unit and coffee table; completing the group snaps it to a wall and adds the missing members. |
| 8104 | 1 | complete_group | r_L-1b_salon_2_kitchen.kitchen_run | no_place: r_L-1b_salon_2_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Kitchen run is missing its fridge (G9); completing the group adds the missing appliance. |
| 8105 | 1 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Shift the coffee table 0.25 m away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 8106 | 1 | relayout_room | r_L-1_salon_2 | acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 4 more kept | Use solver candidate 1 to re-layout the room, addressing the walkway clearance issues for the seating group, the floor lamp blocking the window, and the missing TV unit. |
| 8107 | 1 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.56 m) | Move the floor lamp away from the window band to clear the G12 blocked-opening finding. |
| 8109 | 1 | swap_model | f_L-1_087 | acceptance: pin_refused: f_L-1_087: chinese_tea_table: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | f_L-1_087 is a small 0.71x0.41 m coffee table rendered as a dining table; the Chinese Tea Table (0.84x0.84, low 0.50 m) is a proper low coffee table that fits its small footprint. |
| 8111 | 1 | move_piece | f_L-1_065 | f_L-1_054: no_overlap, f_L-1_065: no_overlap | Move the floor lamp 0.3 m away from the window band to clear the G12 blocked-opening finding. |
| 8112 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 27 -> 17 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Armchair f_L-1_070 stands behind the back of the corner sofa facing it (F4); turning its front to face +X (into the room, away from the sofa) resolves the orientation. |
| 8113 | 1 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.56 m) | Floor lamp f_L-1_063 (1.60 m) stands in front of window win_L-1_001 (G12); moving it 0.56 m into the room clears the window sightline. |
| 8114 | 1 | complete_group | r_L-1b_salon.seating | acceptance: finding F3:f_L-1b_042 is still there after the edit (sofa: its back is not on a wall (1.95 m off)); 2 more kept | Sofa f_L-1b_042 floats 1.95 m off the wall and lacks TV unit and coffee table; completing the seating group snaps it to a wall and adds the missing members. |
| 8115 | 1 | complete_group | r_L-1b_salon_kitchen.kitchen_run | no_place: r_L-1b_salon_kitchen.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Kitchen run is missing its fridge (G9); completing the group adds the missing fridge. |
| 8116 | 1 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the floor lamp 0.3 m along the window band to clear the G12 blocked-opening finding. |
| 8117 | 1 | move_piece | f_L-1_065 | max_tries: f_L-1_065 was edited 3 times in this round | Move the floor lamp 0.31 m along the window band to clear the G12 blocked-opening finding. |
| 8118 | 1 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 6.25 m) | Move the potted plant out of the window band (G12) and into the corner by the left wall so it is anchored (F8). |
| 8119 | 1 | move_piece | f_L-1b_048 | drawn_lock: f_L-1b_048: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 4.27 m) | Move the floor lamp to the left wall beside the sofa so it is anchored (F8). |
| 8120 | 1 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.46 m) | Floor lamp f_L-1_063 (1.60 m) stands in front of window win_L-1_001 (G12); moving it 0.46 m into the room clears the window sightline. |
| 8121 | 1 | swap_model | f_L-1_087 | acceptance: pin_refused: f_L-1_087: small_wooden_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | f_L-1_087 is a small 0.71x0.41 m coffee table rendered as a dining table; the Small Wooden Table 01 (0.92x0.44, low 0.53 m) is a proper low coffee table matching its narrow footprint. |
| 8124 | 1 | move_piece | f_L-1b_047 | snap: f_L-1b_047: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap the potted plant to the left wall in the top-left corner, clearing the window band (G12) and anchoring it (F8). |
| 8125 | 1 | move_piece | f_L-1b_048 | snap: f_L-1b_048: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap the floor lamp to the left wall beside the sofa to anchor it (F8). |
| 8126 | 1 | move_piece | f_L-1_063 | f_L-1_053: no_overlap, f_L-1_063: no_overlap | Floor lamp f_L-1_063 (1.60 m) stands in front of window win_L-1_001 (G12); moving it 0.3 m into the room is the maximum drawn allowance to clear the window sightline. |
| 8129 | 1 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | Shift chair f_L-1b_059 away from f_L-1b_058 to clear the 0.09 m² overlap (F9) and give it ≥0.81 m behind (G6). |
| 8130 | 1 | move_piece | f_L-1b_062 | drawn_lock: f_L-1b_062: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | Shift chair f_L-1b_062 away from f_L-1b_061 to clear the 0.09 m² overlap (F9) and give it ≥0.81 m behind (G6). |
| 8137 | 1 | swap_model | f_L1_027 | no_change: f_L1_027 already uses the model abo_B07GFS1VB6 | The current model renders as a solid opaque block; the Movian Kolva sliding 2-door wardrobe (1.78 x 0.63 m, close to the drawn 1.52 x 0.60) is a functional wardrobe with doors that fits the corridor. |
| 8141 | 1 | swap_model | f_L1_027 | acceptance: pin_refused: f_L1_027: abo_B07H8V7P3H: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The current model renders as a solid opaque block; the Movian Moselle 2-door wardrobe (1.0 x 0.60 m) is a functional wardrobe with visible doors that fits the corridor. |
| 8142 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 12° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)) | Re-place AI pieces with the solver's best candidate to fix the armchair f_L1_032 angle/distance to the coffee table (G3). |
| 8143 | 1 | relayout_room | r_L1_teras | group checks: F8 f_L1_055: potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | Re-solve the balcony group with the top solver candidate to replace indoor dining types with outdoor-appropriate furniture and anchor the plant, fixing F1 (x3) and F8. |
| 8145 | 1 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Confirms the drawn piece's type as wardrobe (coat closet with hanging rail per vector geometry), resolving the recognition conflict where the AI passes typed it bench. |
| 8147 | 1 | move_piece | f_L1_009 | score: plausibility 85 -> 55 (F4 f_L1_010: chair does not face its group (f_L1_009); G6 f_L1_010: chair f_L1_010 is 79° off the table f_L1_009 (needs ≤ 45°); G6 f_L1_011: chair f_L1_011: 0.63 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift dining table f_L1_009 away from chair f_L1_010 to clear the 0.41 m overlap (S2). |
| 8148 | 1 | retype_piece | f_L1_027 | max_tries: f_L1_027 was edited 3 times in this round | The 1.52 x 0.60 m drawn piece fits the dresser size table for a hall; retyping to dresser resolves the recognition conflict (AI passes typed bench) with a type that fits its footprint and room. |
| 8149 | 1 | move_piece | f_L1_010 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Move chair f_L1_010 away from the table edge to clear the 0.41 m overlap (S2). |
| 8153 | 1 | move_piece | f_L1_009 | score: plausibility 85 -> 55 (F4 f_L1_010: chair does not face its group (f_L1_009); G6 f_L1_010: chair f_L1_010 is 79° off the table f_L1_009 (needs ≤ 45°); G6 f_L1_011: chair f_L1_011: 0.62 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift dining table f_L1_009 slightly to clear the 0.41 m overlap with chair f_L1_010 (S2). |
| 8155 | 1 | move_piece | f_L1_036 | snap: f_L1_036: no free place on wall w_L1_002 (doors, windows, at most 1.2 m from the drawn place) | Snap the bookshelf's back to the south wall so it is no longer floating in the room (F9 visual artifact). |
| 8156 | 1 | move_piece | f_L1_031 | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 10° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.51 m (needs ≤ 2.50 m)) | Move armchair f_L1_031 0.27 m closer to the coffee table to satisfy the G3 seating distance (needs ≤ 2.50 m). |
| 8157 | 1 | move_piece | f_L1_007 | drawn_lock: f_L1_007: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair f_L1_007 0.3 m away from the wall behind to give the required ≥ 0.81 m clearance (G6). |
| 8159 | 1 | move_piece | f_L1_009 | score: plausibility 85 -> 65 (F4 f_L1_011: chair does not face its group (f_L1_009); G6 f_L1_011: chair f_L1_011 is 79° off the table f_L1_009 (needs ≤ 45°)) | Shift dining table f_L1_009 toward the wall to clear the 0.41 m overlap with chair f_L1_010 (S2). |
| 8160 | 1 | move_piece | f_L1_009 | max_tries: f_L1_009 was edited 3 times in this round | Shift dining table f_L1_009 left to clear the 0.41 m overlap with chair f_L1_010 (S2). |
| 8161 | 1 | move_piece | f_L1_049 | f_L1_049: inside_room | Shift bookshelf f_L1_049 away from potted_plant f_L1_050 to clear the 0.296 m overlap (S2). |
| 8164 | 1 | move_piece | f_L1_036 | score: plausibility 65 -> 55 (F3 f_L1_036: bookshelf: its back is not on a wall (0.20 m off)) | Nudge the bookshelf 0.2 m off the wall line so it is no longer floating in the room (F9 visual artifact). |
| 8165 | 1 | move_piece | f_L1_031 | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 9° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.52 m (needs ≤ 2.50 m)) | Move armchair f_L1_031 0.29 m closer to the coffee table to satisfy the G3 seating distance (needs ≤ 2.50 m). |
| 8166 | 1 | move_piece | f_L1_050 | f_L1_032: clearance_ok, score: plausibility 85 -> 75 (F6 f_L1_032: armchair: the free zone in front of it is blocked by f_L1_050) | Move potted_plant f_L1_050 away from wall w_L1_012 to clear the 0.193 m cut (S2). |
| 8167 | 1 | move_piece | f_L1_007 | score: plausibility 65 -> 55 (F4 f_L1_007: chair does not face its group (f_L1_005); G6 f_L1_007: chair f_L1_007 is 72° off the table f_L1_005 (needs ≤ 45°)) | Move chair f_L1_007 0.29 m away from the wall behind to give the required ≥ 0.81 m clearance (G6). |
| 8169 | 1 | move_piece | f_L1_050 | f_L1_049: no_overlap, f_L1_050: inside_room, f_L1_050: no_overlap, score: plausibility 85 -> 75 (F9 f_L1_050: potted_plant f_L1_050 overlaps bookshelf f_L1_049 by 0.07 m²) | Move potted_plant f_L1_050 away from wall w_L1_012 to clear the 0.193 m cut (S2). |
| 8170 | 1 | move_piece | f_L1_031 | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 9° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.54 m (needs ≤ 2.50 m)) | Move armchair f_L1_031 0.3 m closer to the coffee table to satisfy the G3 seating distance (needs ≤ 2.50 m). |
| 8171 | 1 | place_group | r_L0_e_yatak_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor to add the missing left nightstand. |
| 8173 | 1 | move_piece | f_L1_007 | score: plausibility 65 -> 55 (F4 f_L1_007: chair does not face its group (f_L1_005); G6 f_L1_007: chair f_L1_007 is 71° off the table f_L1_005 (needs ≤ 45°)) | Move chair f_L1_007 0.28 m away from the wall behind to give the required ≥ 0.81 m clearance (G6). |
| 8186 | 1 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall to the free span s0 so its front (facing into the room) has the 0.80 m clearance G13 needs. |
| 8189 | 1 | move_piece | f_L0_011 | snap: f_L0_011: no free place on wall w_L0_015 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe to the free west wall span s4 (3.62 m) so its front faces into the open room with the 0.80 m clearance G13 needs. |
| 8192 | 1 | move_piece | f_L0_011 | snap: f_L0_011: no free place on wall w_L0_016 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe to the free east wall span s1 (0.77 m) so its front faces into the open room with the 0.80 m clearance G13 needs. |
| 8194 | 1 | move_piece | f_L0_022 | drawn_lock: f_L0_022: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the bed 0.30 m west so the left side gains the 0.60 m clearance G5 needs (0.52 → 0.82 m). |
| 8197 | 1 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.29 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift the bed 0.29 m west so the left side gains the 0.60 m clearance G5 needs (0.52 → 0.81 m). |
| 8200 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free right side of the head. |
| 8201 | 1 | move_piece | f_L0_022 | snap: f_L0_022: no free place on wall w_L0_007 (doors, windows, at most 1.2 m from the drawn place) | Snap the bed's headboard back onto the north wall (span s3) and slide it 0.29 m west so the left side gains the 0.60 m clearance G5 needs (0.52 → 0.81 m). |
| 8202 | 1 | move_piece | f_L0_022 | max_tries: f_L0_022 was edited 3 times in this round | Shift the bed 0.28 m west so the left side gains the 0.60 m clearance G5 needs (0.52 → 0.80 m). |
| 8203 | 1 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_008 (G4 minor, bed f_L0_008): re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free right side of the head. |
| 8204 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.65 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.3 m left along the top wall to increase front clearance past the desk, targeting ≥0.80 m for G13. |
| 8206 | 1 | move_piece | f_L0_027 | f_L0_044: no_overlap | Move desk 0.147 m down (away from wardrobe) to increase wardrobe front clearance from 0.66 m to ≥0.80 m for G13. |
| 8207 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall) | Shower faces a wall 0.10 m in front; turning it to face 270° orients it into the open room space. |
| 8211 | 1 | move_piece | f_L0_044 | f_L0_020: no_overlap, f_L0_044: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_044: nightstand f_L0_044 overlaps bed_double f_L0_020 by 0.11 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free left side of the head (0.56 m free); G4 f_L0_044: nightstand f_L0_044 of bed_double f_L0_020: -0.12 m from the bed side (needs ≤ 0.30 m)) | Move nightstand 0.3 m down to clear the path for moving the desk down, which will free wardrobe front clearance for G13. |
| 8212 | 1 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Re-solve the bedroom layout to fix G5 bed side clearances (0.53/0.56 m, need 0.60 m) and G13 wardrobe front clearance (0.66 m, need 0.80 m) by repositioning the bed and desk/nightstand cluster. |
| 8213 | 1 | move_piece | f_L0_020 | drawn_lock: f_L0_020: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move bed 0.3 m left to increase side clearances for G5, freeing space on the right for the nightstand and desk cluster. |
| 8214 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 50 (F3 f_L0_020: bed_double: the headboard stands in the room (0.29 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Move bed 0.29 m left to increase side clearances for G5, freeing space on the right for the nightstand and desk cluster. |
| 8408 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 4 more kept | Re-solve seating and living storage with candidate 2 (candidate 1 was rejected in round 1) to open the 0.60 m walkway to the sofa and armchair front zones, fix the sofa/coffee-table collision and armchair orientation. |
| 8410 | 2 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | 5.54 x 0.60 m drawn piece along the window wall is a long storage unit; sideboard fits the living room and resolves the untyped finding. |
| 8411 | 2 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 17 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 76° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn the armchair to face the seating cluster/coffee table instead of the sofa back, fixing the F4 orientation finding. |
| 8412 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 4 more kept | Candidate 3 re-solves seating and living storage with a different placement to open the 0.60 m walkway to the sofa and armchair front zones and fix the sofa/coffee-table collision. |
| 8413 | 2 | move_piece | f_L-1_063 | acceptance: finding G12:f_L-1_063 is still there after the edit (floor_lamp f_L-1_063 (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m + 0.05)) | Move the floor lamp 0.3 m along the wall to clear the window sightline (G12) while staying within the 0.3 m move allowance. |
| 8415 | 2 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.10 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Nudge the coffee table 0.15 m toward the window to clear the 0.12 m² overlap with armchair f_L-1_069 while staying within the 0.179 m move allowance. |
| 8418 | 2 | move_piece | f_L-1_063 | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the floor lamp 0.3 m toward the corner, away from the window band, to clear the window sightline (G12). |
| 8419 | 2 | move_piece | f_L-1_073 | score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.10 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Nudge the coffee table 0.15 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap (F9). |
| 8420 | 2 | move_piece | f_L-1_069 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift the armchair 0.18 m along the window wall to clear the 0.12 m² overlap with coffee table f_L-1_074, within its 0.184 m allowance. |
| 8421 | 2 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 1: f_L-1_054: no_overlap; f_L-1_065: no_overlap | Move the floor lamp 0.30 m into the room, past the window sill line, to stop it blocking window win_L-1_002. |
| 8422 | 2 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a sideboard to clear the NR finding; it fits the long storage profile in the salon. |
| 8423 | 2 | move_piece | f_L-1_069 | memory: the same edit was rejected in round 2: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift the armchair 0.18 m along the window wall to clear the 0.12 m² overlap with coffee table f_L-1_074 (F9 f_L-1_074), within its 0.184 m allowance. |
| 8424 | 2 | move_piece | f_L-1_065 | f_L-1_054: no_overlap, f_L-1_065: no_overlap | Move the floor lamp 0.26 m into the room, past the window sill line, to stop it blocking window win_L-1_002 (G12 f_L-1_065). |
| 8426 | 2 | retype_piece | f_L-1_021 | retype: display_cabinet is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a display cabinet to clear the NR finding; it fits the long low storage profile in the salon. |
| 8427 | 2 | move_piece | f_L-1b_046 | wall_exists: no wall 'r_L-1b_salon.s1' | Snap the sofa's back to the right wall (s1) to fix F3 (back 0.59 m off the wall) and keep it facing the room for a TV unit opposite. |
| 8428 | 2 | move_piece | f_L-1b_049 | drawn_lock: f_L-1b_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 6.25 m) | Move the potted plant into the top-right corner against the walls, clearing the window (G12) and ending its floating state (F8). |
| 8429 | 2 | move_piece | f_L-1b_050 | drawn_lock: f_L-1b_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 4.56 m) | Move the floor lamp to the right wall beside sofa f_L-1b_046 so it is no longer floating (F8). |
| 8430 | 2 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.66 m) | Move the chair to the free side of table f_L-1b_051, resolving the overlap with f_L-1b_052 (F9) and giving ≥0.81 m clearance behind (G6). |
| 8431 | 2 | move_piece | f_L-1b_056 | drawn_lock: f_L-1b_056: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.66 m) | Move the chair to the free side of table f_L-1b_054, resolving the overlap with f_L-1b_055 (F9) and giving ≥0.81 m clearance behind (G6). |
| 8432 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge the chair 3 cm away from the table so the clearance behind reaches ≥0.81 m (G6). |
| 8433 | 2 | mark_not_furniture | f_L-1_021 | no_crop: f_L-1_021 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/cam_r_L-1_salon_1_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The 5.54 x 0.60 m drawn piece is too long for any single storage type (sideboard, display_cabinet both rejected); it is a dimension outline or wall element, not furniture. |
| 8435 | 2 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Anchor sofa f_L-1b_045 to the left wall (F3: back 0.59 m off wall) within the 1.2 m snap allowance. |
| 8436 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Rotate armchair f_L-1_070 to face 270° (toward the room center) to fix F4 (it was facing the back of the sofa). |
| 8437 | 2 | move_piece | f_L-1b_047 | drawn_lock: f_L-1b_047: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift plant 0.3 m away from the window band to clear win_L-1b_002 (G12) while keeping it anchored by the wall (F8). |
| 8438 | 2 | move_piece | f_L-1b_048 | score: plausibility -35 -> -45 (G11 f_L-1b_005: kitchen_island f_L-1b_005: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Shift floor lamp 0.3 m off the window band and toward the sofa to anchor it (F8). |
| 8439 | 2 | move_piece | f_L-1b_059 | drawn_lock: f_L-1b_059: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair 0.3 m away from the table to end the 0.09 m² overlap with f_L-1b_058 (F9) and gain seating clearance (G6). |
| 8440 | 2 | move_piece | f_L-1b_062 | drawn_lock: f_L-1b_062: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move chair 0.3 m away from the table to end the 0.09 m² overlap with f_L-1b_061 (F9) and gain seating clearance (G6). |
| 8441 | 2 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair 0.1 m away from the table to reach the 0.81 m seating clearance (G6: 0.78 m). |
| 8442 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 12° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)); 5 more kept | Re-solve layout to fix seating G3 distance/angle, dining G6 clearance, S2 table-chair collisions, and missing G1/G2 group members in one coherent pass. |
| 8443 | 2 | move_piece | f_L-1_061 | drawn_lock: f_L-1_061: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.33 m) | Move the coffee table 0.33 m away from the sofa to resolve the S2 collision (0.621 m cut). |
| 8445 | 2 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa's back to the right wall (w_L-1b_010) to fix F3 (back 0.59 m off the wall) and keep it facing the room for a TV unit opposite. |
| 8446 | 2 | move_piece | f_L-1b_049 | snap: f_L-1b_049: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap the potted plant's back to the right wall (w_L-1b_010) at its drawn position: it leaves the window band (G12) and is no longer floating (F8). |
| 8448 | 2 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.36 m) | Move the chair 0.36 m to the free side of table f_L-1b_051, resolving the overlap with f_L-1b_052 (F9) and giving ≥0.81 m clearance behind (G6). |
| 8450 | 2 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.53 m) | Slide sofa 0.59 m to the left wall so its back sits on the wall (F3) and its front faces the coffee table (F4). |
| 8451 | 2 | move_piece | f_L-1b_047 | acceptance: finding F8:f_L-1b_047 is still there after the edit (potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m)) | Nudge plant 0.29 m off the window band to clear win_L-1b_002 (G12) while staying wall-anchored (F8). |
| 8458 | 2 | swap_model | f_L0_023 | no_change: f_L0_023 already uses the model abo_B015IPNVFW | Fixes v:r2-v1:1 and v:r2-v1:2: the current 3DWH model renders as a dark abstract panel; the CC-BY 6-door wardrobe (3.0 x 0.58 m) matches the drawn 3.11 x 0.6 m run and is a realistic functional wardrobe. |
| 8459 | 2 | retype_piece | f_L1_037 | score: plausibility 85 -> 68 (G11 f_L1_037: sideboard f_L1_037: its front use zone is not reached by a 0.60 m walkway from door d_L1_002; G13 f_L1_037: sideboard f_L1_037: 0.34 m free in front, needs ≥ 0.80 m) | Bench is not a piece of an 'other' room; a 1.4 x 0.45 m sideboard fits the footprint and the room (c:F1:f_L1_037, c:G14:f_L1_037). |
| 8461 | 2 | move_piece | f_L1_037 | drawn_lock: f_L1_037: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.34 m) | Pull the bench 0.32 m off the south wall so a sideboard retype has the 0.80 m front clearance it needs (prep for c:F1:f_L1_037, c:G14:f_L1_037). |
| 8462 | 2 | swap_model | f_L0_023 | acceptance: pin_refused: f_L0_023: hssd_0486ae7dd0b011240a162dc0ff1d96e2cac23dca: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes v:r2-v1:1 and v:r2-v1:2: the current model renders as a dark abstract panel with an embedded window; the Xena 3-door sliding wardrobe (2.71 x 0.66 m, modern/scandinavian) is a realistic functional wardrobe close to the drawn 3.11 x 0.6 m run. |
| 8463 | 2 | move_piece | f_L1_037 | drawn_lock: f_L1_037: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | Pull the bench 0.3 m off the south wall so a sideboard retype has the 0.80 m front clearance it needs (prep for c:F1:f_L1_037, c:G14:f_L1_037). |
| 8464 | 2 | swap_model | f_L0_023 | acceptance: pin_refused: f_L0_023: hssd_7094e30496b2735c235819e99c509769dc30502d: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes v:r2-v1:1 and v:r2-v1:2: the current model renders as a dark abstract panel with an embedded window; the Calypso 6-door wardrobe (2.66 x 0.61 m, minimal/modern) is a realistic functional wardrobe close to the drawn 3.11 x 0.6 m run. |
| 8465 | 2 | move_piece | f_L1_037 | max_tries: f_L1_037 was edited 3 times in this round | Pull the bench 0.29 m off the south wall so a sideboard retype has the 0.80 m front clearance it needs (prep for c:F1:f_L1_037, c:G14:f_L1_037). |
| 8468 | 2 | swap_model | f_L0_023 | max_tries: f_L0_023 was edited 3 times in this round | Fixes v:r2-v1:1 and v:r2-v1:2: the current model renders as a dark abstract panel with an embedded window; the Olivieri sliding-door wardrobe (2.91 x 0.69 m, minimal/modern) is a realistic functional wardrobe close to the drawn 3.11 x 0.6 m run. |
| 8476 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Individual moves were rejected by wall-snap and plausibility limits; let the solver re-place the drawn groups as units to clear the wardrobe front clearance and bed side clearances. |
| 8480 | 2 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding X3:r_L0_yatak_odasi_3 is still there after the edit (r_L0_yatak_odasi_3 (bedroom): 7.7 m of outer wall with no window or door: a blank facade) | Direct move_piece on the wardrobe and bed was rejected in round 1; the solver re-solves all three drawn groups (bed, wardrobe, desk) together to recover the 0.80 m wardrobe clearance and 0.60 m bed side clearances. |
| 8483 | 2 | move_piece | f_L0_011 | drawn_lock: f_L0_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.50 m) | Slide the wardrobe along the south wall toward the door to open the 0.8 m front clearance blocked by the desk. |
| 8484 | 2 | move_piece | f_L0_009 | f_L0_009: inside_room (outline: wardrobe reaches 0.44 m² through the room outline, up to 0.300 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 67 -> 47 (F3 f_L0_009: wardrobe: its back is not on a wall (0.30 m off); F9 f_L0_009: wardrobe reaches 0.44 m² through the room outline, up to 0.300 m deep; G13 f_L0_009: wardrobe f_L0_009: 0.47 m free in front, needs ≥ 0.80 m) | Snap the wardrobe's back edge to the bottom wall (w_L0_003) to open the 0.80 m front clearance required by G13. |
| 8485 | 2 | move_piece | f_L0_022 | memory: the same edit was rejected in round 1: drawn_lock: f_L0_022: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Slide the bed 0.3 m left toward the west wall to open the right side (nightstand side) and the left side to the required 0.6 m. |
| 8486 | 2 | move_piece | f_L0_012 | f_L0_012: inside_room (outline: wardrobe reaches 0.29 m² through the room outline, up to 0.196 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 60 (F3 f_L0_012: wardrobe: its back is not on a wall (0.20 m off); F9 f_L0_012: wardrobe reaches 0.29 m² through the room outline, up to 0.196 m deep) | slide wardrobe 0.2 m along the top wall to open 0.86 m in front (needs 0.80) |
| 8488 | 2 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.28 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Slide the bed 0.28 m left toward the west wall to open the right side (nightstand side) toward the required 0.6 m. |
| 8490 | 2 | move_piece | f_L0_046 | f_L0_022: no_overlap, f_L0_046: no_overlap, score: plausibility 67 -> 44 (F9 f_L0_046: nightstand f_L0_046 overlaps bed_double f_L0_022 by 0.16 m²; G4 f_L0_022: bed_double f_L0_022: no nightstand on the free left side of the head (0.52 m free); G4 f_L0_046: nightstand f_L0_046 of bed_double f_L0_022: -0.08 m from the bed side (needs ≤ 0.30 m)) | Move the nightstand to the right side of the bed head to satisfy G4 (no nightstand on the free right side of the head). |
| 8492 | 2 | move_piece | f_L0_028 | score: plausibility 67 -> 57 (F3 f_L0_028: desk: its back is not on a wall (0.15 m off)) | Slide the desk 0.14 m left toward the door to open the wardrobe's front clearance (G13). |
| 8493 | 2 | move_piece | f_L0_036 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Move the office chair 0.3 m toward the door to open the wardrobe's front clearance (G13). |
| 8494 | 2 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m) | Slide the wardrobe 0.3 m left along the south wall to open the front clearance (G13). |
| 8496 | 2 | move_piece | f_L0_022 | f_L0_022: inside_room (outline: bed_double reaches 0.46 m² through the room outline, up to 0.298 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 67 -> 14 (F3 f_L0_022: bed_double: the headboard stands in the room (0.30 m off); F9 f_L0_022: bed_double reaches 0.46 m² through the room outline, up to 0.298 m deep; G4 f_L0_022: bed_double f_L0_022: no nightstand on the free left side of the head (0.52 m free); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Slide the bed 0.3 m right toward the east wall to open the left side to the required 0.6 m (G5#2). |
| 8497 | 2 | move_piece | f_L0_046 | score: plausibility 67 -> 41 (F3 f_L0_046: nightstand: its back is not on a wall (0.12 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free left side of the head (0.52 m free); G4 f_L0_046: nightstand f_L0_046 of bed_double f_L0_022: its back 1.52 m from the headboard line (needs ≤ 0.30 m); G11 f_L0_022: bed_double f_L0_022: its left use zone is not reached by a 0.60 m walkway from door d_L0_010) | Move the nightstand to the left side of the bed head (0.52 m free) to satisfy G4. |
| 8681 | 3 | relayout_room | r_L-1_salon_2 | memory: the same edit was rejected in round 1: acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 4 more kept | Solver candidate 1 re-lays the seating group to restore the 0.60 m walkway from door o_L-1_002 (G11 x3) and clears the floor lamp from the window (G12). |
| 8683 | 3 | relayout_room | r_L-1_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:f_L-1_053 is still there after the edit (sofa_corner f_L-1_053: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 4 more kept | Re-solve the seating group around drawn sofa f_L-1_053 to open a 0.60 m walkway from the door to the front use zones, fix the sofa/coffee-table collision and armchair f_L-1_070 orientation. |
| 8684 | 3 | relayout_room | r_L-1_salon_2 | acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 3 more kept | Candidate 2 re-lays the seating group to restore the 0.60 m walkway from door o_L-1_002 (G11 x3) and clear the floor lamp from the window (G12). |
| 8685 | 3 | swap_model | f_L-1_087 | asset_exists: no catalogue model 'table_coffee' | The coffee table f_L-1_087 is rendered as a dining table; swap to a proper coffee table model. |
| 8686 | 3 | relayout_room | r_L-1_salon | memory: the same edit was rejected in round 2: acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 4 more kept | Re-solve the seating group around drawn sofa f_L-1_053 (candidate 2) to open a 0.60 m walkway from the door to the front use zones, fix the sofa/coffee-table collision and armchair f_L-1_070 orientation. |
| 8687 | 3 | move_piece | f_L-1_065 | acceptance: finding G12:f_L-1_065 is still there after the edit (floor_lamp f_L-1_065 (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m + 0.05)) | c:G12:f_L-1_065: shift the floor lamp 0.05 m back from the window sill line so it no longer stands in front of window win_L-1_002. |
| 8690 | 3 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | c:G12:f_L-1_065: shift the floor lamp 0.30 m back from the window so it no longer stands in front of window win_L-1_002. |
| 8691 | 3 | swap_model | f_L-1_087 | acceptance: pin_refused: f_L-1_087: modern_coffee_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The coffee table f_L-1_087 is rendered as a dining table; swap to a proper modern coffee table model. |
| 8692 | 3 | move_piece | f_L-1_073 | memory: the same edit was rejected in round 2: score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.10 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Nudge the coffee table 0.15 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap (F9). |
| 8694 | 3 | move_piece | f_L-1_065 | f_L-1_065: inside_room | c:G12:f_L-1_065: shift the floor lamp 0.29 m back from the window so it no longer stands in front of window win_L-1_002. |
| 8695 | 3 | complete_group | r_L-1b_salon.seating | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_042 is still there after the edit (sofa: its back is not on a wall (1.95 m off)); 2 more kept | Sofa f_L-1b_042 is floating off the wall (F3) and missing TV unit and coffee table (G1, G2); completing the group re-solves the seating arrangement around the drawn anchor. |
| 8697 | 3 | move_piece | f_L-1_065 | max_tries: f_L-1_065 was edited 3 times in this round | c:G12:f_L-1_065: shift the floor lamp 0.24 m back from the window so it no longer stands in front of window win_L-1_002. |
| 8698 | 3 | swap_model | f_L-1_087 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L-1_087: chinese_tea_table: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The coffee table f_L-1_087 is rendered as a dining table; swap to a small square coffee table model that fits its 0.71 x 0.41 m footprint. |
| 8699 | 3 | move_piece | f_L-1_073 | score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.09 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Nudge the coffee table 0.2 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap (F9) without worsening the armchair's walkway. |
| 8702 | 3 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.32 m) | c:F9:f_L-1_074: move the coffee table 0.30 m away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 8704 | 3 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.08 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | c:F9:f_L-1_074: move the coffee table 0.25 m away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 8705 | 3 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.09 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | c:F9:f_L-1_074: move the coffee table 0.20 m away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 8707 | 3 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | c:F9:f_L-1_074: move the coffee table 0.10 m away from armchair f_L-1_069 to clear the 0.12 m² overlap. |
| 8713 | 3 | retype_piece | f_L1_035 | score: plausibility 65 -> 58 (G13 f_L1_035: sideboard f_L1_035: 0.33 m free in front, needs ≥ 0.80 m) | Bench is not a valid piece for this room (F1/G14); a sideboard fits its 1.4m x 0.45m footprint and the room. |
| 8728 | 3 | move_piece | f_L1_057 | f_L1_019: clearance_ok, f_L1_019: no_overlap, f_L1_056: no_overlap, f_L1_057: no_overlap, score: plausibility 85 -> 75 (F6 f_L1_019: sofa: the free zone in front of it is blocked by f_L1_057) | Move the potted plant away from the bookshelf and out of wall w_L1_012 (S2 x2). |
| 8729 | 3 | swap_model | f_L1_027 | acceptance: pin_refused: f_L1_027: hssd_3033be75f2ac15885e8f4813dc55e168af09e91f: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the opaque solid-block wardrobe for the Oscar 3-door wardrobe (1.52 x 0.62 x 2.08 m, doors visible) to fix the F9 critical finding that the piece renders as a solid block blocking the corridor. |
| 8730 | 3 | swap_model | f_L0_023 | acceptance: pin_refused: f_L0_023: 3dwh_76239dbd025ede9f6e8610c3: audit: removed (an anchor (wardrobe) of units guessed (x1.0): the Milestone 13 gate needs known units for anchors): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes v:r2-v1:1 and v:r2-v1:2: the current model renders as a dark abstract panel; swap to a real 2.99x0.72x3.22 m wardrobe model that fits the 3.11 m run. |
| 8731 | 3 | move_piece | f_L1_057 | f_L1_056: no_overlap, f_L1_057: no_overlap | Move the potted plant away from the bookshelf and out of wall w_L1_012, keeping the sofa's front zone clear (S2 x2). |
| 8732 | 3 | swap_model | f_L1_027 | acceptance: pin_refused: f_L1_027: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the opaque solid-block wardrobe for the Cream Triple Wardrobe (1.47 x 0.55 x 1.75 m, under the 1.77 m sloped-ceiling cap, doors visible) to fix the F9 critical finding. |
| 8734 | 3 | swap_model | f_L0_023 | acceptance: pin_refused: f_L0_023: hssd_f19f4eb60204eef42a4dc3b073ef9006916a2c0b: audit: removed (1616 triangles (< 3000): crude unless the vision quality is high; vision quality 2; vision quality 2 (<= 2)): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes v:r2-v1:1 and v:r2-v1:2: swap the glitched abstract-panel model for the Betrib wardrobe (2.66x0.62x2.2 m, minimal/modern), a real wardrobe model that fits the 3.11 m run. |
| 8737 | 3 | swap_model | f_L1_027 | acceptance: pin_refused: f_L1_027: hssd_5f1c51116d658b454806329a7be495f18190e7d1: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the opaque solid-block wardrobe for the Black wardrobe (1.50 x 0.50 x 1.90 m, under the 1.77 m sloped-ceiling cap, doors visible) to fix the F9 critical finding. |
| 8738 | 3 | move_piece | f_L1_057 | max_tries: f_L1_057 was edited 3 times in this round | Move the potted plant further from the bookshelf to clear the remaining S2 overlap. |
| 8740 | 3 | move_piece | f_L1_056 | f_L1_056: inside_room, f_L1_056: no_overlap, f_L1_057: no_overlap | Shift the bookshelf along the wall to clear the remaining S2 overlap with the potted plant. |
| 8741 | 3 | swap_model | f_L0_023 | acceptance: pin_refused: f_L0_023: hssd_2e32ff526dbeb03092164450a309d084a99879cd: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes v:r2-v1:1 and v:r2-v1:2: swap the glitched abstract-panel model for the Adele 6-door wardrobe (2.58x0.60x2.33 m, classic/minimal/modern), a real wardrobe model that fits the 3.11 m run. |
| 8742 | 3 | swap_model | f_L1_027 | max_tries: f_L1_027 was edited 3 times in this round | Swap the opaque solid-block wardrobe for the Vida Designs Corona 3-door solid-pine wardrobe (1.50 x 0.57 x 1.87 m, doors visible) to fix the F9 critical finding. |
| 8744 | 3 | move_piece | f_L1_056 | f_L1_056: no_overlap, f_L1_057: no_overlap | Shift the bookshelf along the wall to clear the remaining S2 overlap with the potted plant. |
| 8746 | 3 | move_piece | f_L1_056 | f_L1_056: no_overlap, f_L1_057: no_overlap | Shift the bookshelf along the wall to clear the remaining S2 overlap with the potted plant. |
| 8747 | 3 | swap_model | f_L0_023 | max_tries: f_L0_023 was edited 3 times in this round | Fixes v:r2-v1:1 and v:r2-v1:2: swap the glitched abstract-panel model for the Majestic 6-drawer wardrobe (2.6x0.63x2.28 m, minimal/modern), a real wardrobe model that fits the 3.11 m run. |
| 8749 | 3 | move_piece | f_L1_056 | max_tries: f_L1_056 was edited 3 times in this round | Shift the bookshelf along the wall to clear the remaining S2 overlap with the potted plant. |
| 8752 | 3 | move_piece | f_L0_012 | f_L0_012: clearance_ok, score: plausibility 70 -> 60 (F3 f_L0_012: wardrobe: its back is not on a wall (0.07 m off); G13 f_L0_012: wardrobe f_L0_012: 0.51 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.14 m toward wall w_L0_004 to open front clearance from 0.66 m to ~0.80 m (G13). |
| 8756 | 3 | relayout_room | r_L0_yatak_odasi_4 | memory: the same edit was rejected in round 2: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve the drawn groups as units to fix wardrobe front clearance (G13), bed side clearances (G5) and add the missing nightstand (G4). |
| 8948 | 4 | swap_model | f_L1_027 | memory: the same edit was rejected in round 3: acceptance: pin_refused: f_L1_027: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap to a wardrobe model with visible doors/structure that fits the 1.52m width and stays under the 1.77m height cap to resolve the F9 critical findings about the opaque block. |
| 8949 | 4 | swap_model | f_L1_027 | acceptance: pin_refused: f_L1_027: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap to the Leon Wardrobe (1.478 x 0.61 x 1.993 m) which has visible doors and structure, fits the 1.52m width, and stays under the 1.77m height cap to resolve the F9 critical findings. |
| 8950 | 4 | swap_model | f_L1_027 | memory: the same edit was rejected in round 3: acceptance: pin_refused: f_L1_027: hssd_5f1c51116d658b454806329a7be495f18190e7d1: fails the fit rules (caps, height, at most 1.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap to the Black wardrobe (1.4999 x 0.5021 x 1.8978 m) which has visible doors and structure, fits the 1.52m width, and stays under the 1.77m height cap to resolve the F9 critical findings. |
| 8951 | 4 | swap_model | f_L1_027 | max_tries: f_L1_027 was edited 3 times in this round | Swap to the Newport Three-plus Door Wardrobe (1.4994 x 0.6134 x 1.9995 m) which has visible doors and structure, fits the 1.52m width, and stays under the 1.77m height cap to resolve the F9 critical findings. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F1 | major | f_L1_005 | r_L1_oyun_aktivite_ve_dinlenme_odasi | review | drawn_type | 4 | the piece is drawn and its type is one the room's types hold (the code's room rules, aliases included): drawn furniture is kept (CLAUDE.md), and a vision opinion on its type is no reading error, so it is reported for review, not retyped |
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
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_022 | r_L0_yatak_odasi_4 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_019 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_020 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1_salon | cut | 1 | 6114 | 32768 |
| 1 | r_L-1b_salon_2 | cut | 1 | 7337 | 32768 |
| 1 | r_L-1b_salon | cut | 2 | 10498 | 32768 |
| 1 | building | cut | 1 | 40106 | 32768 |
| 2 | r_L-1_salon | cut | 1 | 10589 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 866 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 2 | 6552 | 32768 |
| 2 | building | cut | 1 | 40106 | 32768 |
| 3 | r_L-1b_salon | cut | 5 | 23815 | 32768 |
| 3 | building | cut | 1 | 40106 | 32768 |

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
| f_L-1_039 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the chair 0.03 m away from the table edge to clear the 0.039 m cut with table f_L-1_038. |
| f_L-1_042 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | c:S2:f_L-1_038#2: move chair f_L-1_042 0.14 m away from the dining table to clear the 0.038 m cut. |
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
| f_L-1b_046 | piece | sofa | r_L-1b_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 (reading.long_side_front) | Sofa f_L-1b_046 is 0.59 m off the wall (F3); snap its back to the free span of wall w_L-1b_004 (s3) to put it on a wall. (plan crop recognition/crops/sym_L-1b_008_ctx.png) |
| f_L-1b_047 | piece | potted_plant | r_L-1b_salon_2 | inferred | - | - | the two AI passes disagree (floor_lamp / potted_plant); both fit the drawn 0.59 x 0.59 m and the room: potted_plant, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L-1b_009_ctx.png |
| f_L-1b_048 | piece | floor_lamp | r_L-1b_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1b_049 | piece | potted_plant | r_L-1b_salon | inferred | - | - | the two AI passes disagree (floor_lamp / potted_plant); both fit the drawn 0.59 x 0.59 m and the room: potted_plant, because the AI passes of its twin f_L-1b_047 in the twin room r_L-1b_salon_2 named it too: the twins get one type; plan crop recognition/crops/sym_L-1b_011_ctx.png |
| f_L-1b_050 | piece | floor_lamp | r_L-1b_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | Qwen/Qwen3.8-27B-FP8 | Snap the floor lamp's back to the right wall (w_L-1b_010) at its drawn position so it is no longer floating (F8). |
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
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the wardrobe along its wall to open the 0.80 m front clearance (currently 0.66 m). |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred | - | - | bed_double: the bedroom room misses its sleeping_double anchor (bed_double), and the type's product range fits 1.90 x 1.55 m (the only missing member of that size) |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_019 in the twin room r_L0_yatak_odasi (mirrored centre within 0.02 m) |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred | - | - | bed_double: the bedroom room misses its sleeping_double anchor (bed_double), and the type's product range fits 1.90 x 1.55 m (the only missing member of that size) |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_021 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m) |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the crude, flat low-poly wardrobe model with a detailed 3.15 m modern wardrobe matching the drawn 3.11 m footprint. |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - | - | wardrobe: the same footprint (3.11 x 0.60 m) as f_L0_023 in the twin room r_L0_e_yatak_odasi (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L0_025 in the twin room r_L0_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_035 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_036 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_037 stands in front; plan crop recognition/crops/sym_L0_011_ctx.png |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_038 stands in front; plan crop recognition/crops/sym_L0_012_ctx.png |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: Shift the right nightstand away from the bed edge to clear the 0.06 m² overlap and satisfy the ≤0.30 m side gap. |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_005 | piece | table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | The dining table renders as a low flat surface; swap to a proper round dining table model (0.80 m, matches the drawn 0.78 m) to fix the wrong_model visual. |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_009 | piece | table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Re-solve the dining group around the drawn table so the two chairs stop cutting the table (S2 x2). |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift sofa f_L1_019 away from f_L1_018 to clear the blocked free zone in front of it (F6). |
| f_L1_020 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift sofa f_L1_020 0.3 m away from f_L1_017 to clear the blocked free zone in front of it (F6). |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_025 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Bring armchair within 2.50 m of the coffee table to fix G3. (plan crop recognition/crops/sym_L1_009_ctx.png) |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge armchair f_L1_032 toward the coffee table to bring it within 2.5 m (G3). (plan crop recognition/crops/sym_L1_010_ctx.png) |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Bench is not a valid piece for this room (F1/G14); a console table fits its 1.4m x 0.45m footprint and the room. (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (bookshelf / console_table); both fit the drawn 1.09 x 0.40 m and the room: bookshelf, because the room misses it (the living room's living_storage group has no sideboard or bookshelf or display_cabinet); plan crop recognition/crops/sym_L1_x6881d71b_ctx.png; front: its back stands on the only side on a wall |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (bookshelf / console_table); both fit the drawn 1.09 x 0.40 m and the room: bookshelf, because the AI passes of its twin f_L1_036 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png; front: its back stands on the only side on a wall |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred | - | - | the chair of the desk f_L0_029, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred | - | - | the chair of the desk f_L0_030, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L1_057 | piece | potted_plant | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move the potted plant away from the bookshelf and out of wall w_L1_012, keeping the sofa's front zone clear (S2 x2). |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 1 | cam_r_L1_teras_2 | ![](agent/r1_cam_r_L1_teras_2_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_after.jpg) |
| 1 | cam_r_L1_teras_3 | ![](agent/r1_cam_r_L1_teras_3_before.jpg) | ![](agent/r1_cam_r_L1_teras_3_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_1 | ![](agent/r3_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_2 | ![](agent/r3_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- final/cam_r_L0_yatak_odasi_4_1_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_yatak_odasi_4_1_final_preview.jpg
- final/cam_r_L0_yatak_odasi_4_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_yatak_odasi_4_2_final_preview.jpg
- final/cam_r_L0_yatak_odasi_4_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_yatak_odasi_4_3_final_preview.jpg
- final/cam_r_L0_yatak_odasi_4_1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_yatak_odasi_4_1_plan.jpg
- final/cam_r_L0_yatak_odasi_4_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_yatak_odasi_4_2_plan.jpg
- final/cam_r_L0_yatak_odasi_4_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_yatak_odasi_4_3_plan.jpg
