# Final report: real06

29 views: 16 polished, 13 Cycles (gate 1, gate_validation 6, vision_check 6). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 29 |
| interior / exterior views | 23 / 6 |
| variant | base |
| polished | 16 |
| Cycles | 13 (gate 1, gate_validation 6, vision_check 6) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 2 |
| needs_review views | 2 |
| unverified pieces in view (sum over views) | 93 |
| rooms mixing polished and Cycles | 5 |
| advisory | yes |
| advisory flags | 12 |
| exposure | -7.67 .. +1.50 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 23 view(s), -3 .. 0 EV |
| interior glazing pull | 2 view(s) with interior glazing, 0 pulled, 0 still clipped over 1.0 % |
| camera policy | agent 8, m5 6, search 15 |
| camera score (min / mean / max) | 2.19 / 4.36 / 5.60 |
| rooms by number of views | 1 with 0, 4 with 1, 2 with 2, 5 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 3.7 min / 3.3 min / 73.3 s |
| seconds: polish / gate / check | 2.4 min / 27.4 s / 31.8 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 12 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real06.blend](3d/real06.blend) | 364.7 MB |
| [real06.glb](3d/real06.glb) | 663.5 MB |

29 cameras; textures scaled to at most 1024 px (138 scaled) for the download.

## AI decor

48 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 11 rooms; 4 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- the polish added an object in cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_salon_1, cam_r_L1_banyo_1, cam_r_L1_cocuk_odasi_1, cam_r_L1_ebeveyn_y_odasi_2: the Cycles render is final
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 4 piece(s) moved beyond the tolerance, 4 locked-rule violation(s)
- AI completion: 7 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 96.9 % (limit 95 %), 64 comparisons |
| negative controls rejected | 93.0 % (limit 90 %), 158 comparisons |
| effect | polish allowed |

### Exterior views

Exterior decision: **polish_disabled**. The exterior views are the Cycles render; the rooms are not affected.

| item | value |
|---|---|
| benign exterior comparisons accepted | 95.8 % (limit 95 %), 24 comparisons |
| negative exterior comparisons rejected | 68.3 % (limit 90 %), 60 comparisons |

Reasons:

- negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- exterior_base: [contact_sbs_exterior_base.jpg](contact_sbs_exterior_base.jpg)

- r_L0_banyo: [contact_sbs_r_L0_banyo.jpg](contact_sbs_r_L0_banyo.jpg)

- r_L0_mutfak: [contact_sbs_r_L0_mutfak.jpg](contact_sbs_r_L0_mutfak.jpg)

- r_L0_salon: [contact_sbs_r_L0_salon.jpg](contact_sbs_r_L0_salon.jpg)

- r_L1_banyo: [contact_sbs_r_L1_banyo.jpg](contact_sbs_r_L1_banyo.jpg)

- r_L1_cocuk_odasi: [contact_sbs_r_L1_cocuk_odasi.jpg](contact_sbs_r_L1_cocuk_odasi.jpg)

- r_L1_dus: [contact_sbs_r_L1_dus.jpg](contact_sbs_r_L1_dus.jpg)

- r_L1_ebeveyn_y_odasi: [contact_sbs_r_L1_ebeveyn_y_odasi.jpg](contact_sbs_r_L1_ebeveyn_y_odasi.jpg)

- r_L1_hol: [contact_sbs_r_L1_hol.jpg](contact_sbs_r_L1_hol.jpg)

- r_L1_oda: [contact_sbs_r_L1_oda.jpg](contact_sbs_r_L1_oda.jpg)

- r_L1_oda_2: [contact_sbs_r_L1_oda_2.jpg](contact_sbs_r_L1_oda_2.jpg)

- r_L1_soyunma_odasi: [contact_sbs_r_L1_soyunma_odasi.jpg](contact_sbs_r_L1_soyunma_odasi.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| exterior_base | ext_1 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_2 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_3 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_4 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_5 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_6 | - | - | info | - | - | cycles (gate_validation) |
| r_L0_banyo | cam_r_L0_banyo_1 | - | - | info | - | - | cycles (gate) |
| r_L0_mutfak | cam_r_L0_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L0_mutfak | cam_r_L0_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L0_mutfak | cam_r_L0_mutfak_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_1 | a2 s 0.25 canny x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L0_salon | cam_r_L0_salon_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_banyo | cam_r_L1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L1_banyo | cam_r_L1_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_dus | cam_r_L1_dus_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_2 | a2 s 0.25 canny x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_hol | cam_r_L1_hol_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_oda | cam_r_L1_oda_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_oda_2 | cam_r_L1_oda_2_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_oda_2 | cam_r_L1_oda_2_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_oda_2 | cam_r_L1_oda_2_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_soyunma_odasi | cam_r_L1_soyunma_odasi_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_soyunma_odasi | cam_r_L1_soyunma_odasi_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | gate | - | - | info | - | - | +0.17 | -2 | agent | D3 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/2 | +0.67 | - | agent | D6 A3 | 3 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.33 | -2 | agent | D5 A4 | 3 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +1.50 | -3 | search 4.09 | D7 A4 | 5 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | vision_check | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.33 | -1 | agent | D13 A4 | 9 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +0.67 | -3 | search 4.11 | D6 A4 | 5 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.17 | -2 | search 3.80 | D13 A4 | 9 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.17 | -2 | search 4.33 | D5 | 2 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.17 | -2 | search 3.15 | D4 | 1 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/2 | -0.50 | -2 | search 4.79 | D4 A5 | 1 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +0.00 | - | search 4.13 | D4 A5 | 1 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | -0.33 | -2 | search 4.52 | D6 A8 | 1 | yes | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_dus_1 | r_L1_dus | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.67 | - | agent | D2 | 0 | no | [preview](cam_r_L1_dus_1_final_preview.jpg) [plan](cam_r_L1_dus_1_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_1 | r_L1_ebeveyn_y_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.17 | -3 | search 5.60 | D6 A3 | 3 | yes | [preview](cam_r_L1_ebeveyn_y_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_2 | r_L1_ebeveyn_y_odasi | L1 | cycles | vision_check | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.33 | -2 | search 5.45 | D9 A4 | 4 | no | [preview](cam_r_L1_ebeveyn_y_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_3 | r_L1_ebeveyn_y_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.17 | -3 | search 5.10 | D5 A3 | 2 | no | [preview](cam_r_L1_ebeveyn_y_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +0.67 | -3 | search 2.19 | D6 | 1 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_oda_1 | r_L1_oda | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.83 | - | agent | D2 | 0 | no | [preview](cam_r_L1_oda_1_final_preview.jpg) [plan](cam_r_L1_oda_1_plan.jpg) |
| cam_r_L1_oda_2_1 | r_L1_oda_2 | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +0.17 | -2 | search 5.34 | D5 A1 | 5 | no | [preview](cam_r_L1_oda_2_1_final_preview.jpg) [plan](cam_r_L1_oda_2_1_plan.jpg) |
| cam_r_L1_oda_2_2 | r_L1_oda_2 | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | -0.17 | -2 | search 4.77 | D5 A1 | 4 | no | [preview](cam_r_L1_oda_2_2_final_preview.jpg) [plan](cam_r_L1_oda_2_2_plan.jpg) |
| cam_r_L1_oda_2_3 | r_L1_oda_2 | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.17 | -2 | search 3.94 | D4 A1 | 4 | no | [preview](cam_r_L1_oda_2_3_final_preview.jpg) [plan](cam_r_L1_oda_2_3_plan.jpg) |
| cam_r_L1_soyunma_odasi_1 | r_L1_soyunma_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 1/2 | +0.33 | - | agent | D5 | 2 | no | [preview](cam_r_L1_soyunma_odasi_1_final_preview.jpg) [plan](cam_r_L1_soyunma_odasi_1_plan.jpg) |
| cam_r_L1_soyunma_odasi_2 | r_L1_soyunma_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 1/2 | +0.33 | - | agent | D5 | 2 | no | [preview](cam_r_L1_soyunma_odasi_2_final_preview.jpg) [plan](cam_r_L1_soyunma_odasi_2_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.67 | 0 | m5 | D12 | 5 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.00 | 0 | m5 | D16 | 6 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.33 | 0 | m5 | D16 | 6 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 | D12 | 2 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.00 | 0 | m5 | D16 | 6 | no | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.33 | 0 | m5 | D5 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_banyo | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 1 | 2 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_oda | hall | L0 | 0 | 0 | 0 | - |
| r_L0_salon | living | L0 | 3 | 2 | 1 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L1_banyo | bathroom | L1 | 2 | 1 | 1 | cam_r_L1_banyo_1, cam_r_L1_banyo_2 |
| r_L1_cocuk_odasi | bedroom | L1 | 3 | 2 | 1 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_dus | bathroom | L1 | 1 | 1 | 0 | cam_r_L1_dus_1 |
| r_L1_ebeveyn_y_odasi | bedroom | L1 | 3 | 2 | 1 | cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_2, cam_r_L1_ebeveyn_y_odasi_3 |
| r_L1_hol | hall | L1 | 1 | 1 | 0 | cam_r_L1_hol_1 |
| r_L1_oda | hall | L1 | 1 | 1 | 0 | cam_r_L1_oda_1 |
| r_L1_oda_2 | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_oda_2_1, cam_r_L1_oda_2_2, cam_r_L1_oda_2_3 |
| r_L1_soyunma_odasi | storage | L1 | 2 | 2 | 0 | cam_r_L1_soyunma_odasi_1, cam_r_L1_soyunma_odasi_2 |

Rooms without a rendered view: r_L0_oda (no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)).

### Why Cycles

- cam_r_L0_banyo_1: gate: no ladder attempt passed the gate: a1 reject (depth, edges); a2 reject (depth); a3 reject (depth)
- cam_r_L0_mutfak_1: vision_check: added_by_polish furniture at [378.4, 454.5, 411.3, 481.2]; added_by_polish furniture at [1136.5, 338.5, 1204.8, 614.3]
- cam_r_L0_mutfak_2: vision_check: added_by_polish furniture at [1556.9, 456.6, 1729.1, 696.6]; added_by_polish furniture at [1266.8, 457.1, 1555.1, 668.6]; added_by_polish furniture at [891.3, 302.2, 1109.0, 458.0]
- cam_r_L0_salon_1: vision_check: added_by_polish furniture at [1297.6, 825.3, 1768.1, 1009.6]
- cam_r_L1_banyo_1: vision_check: added_by_polish fixture at [1.3, 190.9, 60.0, 342.5]
- cam_r_L1_cocuk_odasi_1: vision_check: added_by_polish furniture at [1094.3, 531.2, 1110.8, 553.7]
- cam_r_L1_ebeveyn_y_odasi_2: vision_check: added_by_polish furniture at [1096.9, 506.8, 1113.2, 541.6]
- ext_1: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_2: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_3: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_4: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_5: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_6: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L1_cocuk_odasi_3 | cycles | cross-check misplaced | f_L1_004 | bed_double | - | from_documents | real06.dwg ARC:297764,ARC:297767-297769,ARC:297778-297779,ARC:297866,LINE:297770,LINE:297772-297777,LINE:297780-297789,LINE:297792-297795,LINE:297797-297865,LINE:297867-297999,ARC:29776A,ARC:29780F,LINE:293EA7,LINE:29777A,LINE:29777B,LINE:29777C,LINE:29777D,LINE:29777E,LINE:29777F,LINE:29778A,LINE:29778B,LINE:29778C,LINE:29778D,LINE:29778F,LINE:29779A,LINE:29779B,LINE:29779C,LINE:29779D,LINE:29779E,LINE:29779F,LINE:2977A0,LINE:2977A1,LINE:2977A2,LINE:2977A3,LINE:2977A4,LINE:2977A5,LINE:2977A6,LINE:2977A7,LINE:2977A8,LINE:2977A9,LINE:2977AA,LINE:2977AB,LINE:2977AC,LINE:2977AD,LINE:2977AE,LINE:2977AF,LINE:2977B0,LINE:2977B1,LINE:2977B2,LINE:2977B3,LINE:2977B4,LINE:2977B5,LINE:2977B6,LINE:2977B7,LINE:2977B8,LINE:2977B9,LINE:2977BA,LINE:2977BB,LINE:2977BC,LINE:2977BD,LINE:2977BE,LINE:2977BF,LINE:2977C0,LINE:2977C1,LINE:2977C2,LINE:2977C3,LINE:2977C4,LINE:2977C5,LINE:2977C6,LINE:2977C7,LINE:2977C8,LINE:2977C9,LINE:2977CA,LINE:2977CB,LINE:2977CC,LINE:2977CD,LINE:2977CE,LINE:2977CF,LINE:2977D0,LINE:2977D1,LINE:2977D2,LINE:2977D3,LINE:2977D4,LINE:2977D5,LINE:2977D6,LINE:2977D7,LINE:2977D8,LINE:2977D9,LINE:2977DA,LINE:2977DB,LINE:2977DC,LINE:2977DD,LINE:2977DE,LINE:2977DF,LINE:2977E0,LINE:2977E1,LINE:2977E2,LINE:2977E3,LINE:2977E4,LINE:2977EA,LINE:2977EB,LINE:2977EC,LINE:2977ED,LINE:2977EE,LINE:2977EF,LINE:2977F0,LINE:2977F1,LINE:2977F2,LINE:2977F3,LINE:2977F4,LINE:2977F5,LINE:2977F6,LINE:2977F7,LINE:2977F8,LINE:2977F9,LINE:2977FA,LINE:2977FB,LINE:2977FC,LINE:2977FD,LINE:2977FE,LINE:2977FF,LINE:29780A,LINE:29780B,LINE:29780C,LINE:29780D,LINE:29780E,LINE:29781A,LINE:29781B,LINE:29781C,LINE:29781D,LINE:29781E,LINE:29781F,LINE:29782A,LINE:29782B,LINE:29782C,LINE:29782D,LINE:29782E,LINE:29782F,LINE:29783A,LINE:29783B,LINE:29783C,LINE:29783D,LINE:29783E,LINE:29783F,LINE:29784B,LINE:29784C,LINE:29784D,LINE:29784E,LINE:29784F,LINE:29785B,LINE:29785C,LINE:29785D,LINE:29785E,LINE:29785F,LINE:29786A,LINE:29786B,LINE:29786C,LINE:29786D,LINE:29786E,LINE:29786F,LINE:29787A,LINE:29787B,LINE:29787C,LINE:29787D,LINE:29787E,LINE:29787F,LINE:29788A,LINE:29788B,LINE:29788C,LINE:29788D,LINE:29788E,LINE:29788F,LINE:29789A,LINE:29789B,LINE:29789C,LINE:29789D,LINE:29789E,LINE:29789F,LINE:2978A0,LINE:2978A1,LINE:2978A2,LINE:2978A3,LINE:2978A4,LINE:2978A5,LINE:2978A6,LINE:2978A7,LINE:2978A8,LINE:2978A9,LINE:2978AA,LINE:2978AB,LINE:2978AC,LINE:2978AD,LINE:2978AE,LINE:2978AF,LINE:2978B0,LINE:2978B1,LINE:2978B2,LINE:2978B3,LINE:2978B4,LINE:2978B5,LINE:2978B6,LINE:2978B7,LINE:2978B8,LINE:2978B9,LINE:2978BA,LINE:2978BB,LINE:2978BC,LINE:2978BD,LINE:2978BE,LINE:2978BF,LINE:2978C0,LINE:2978C1,LINE:2978C2,LINE:2978C3,LINE:2978C4,LINE:2978C5,LINE:2978C6,LINE:2978C7,LINE:2978C8,LINE:2978C9,LINE:2978CA,LINE:2978CB,LINE:2978CC,LINE:2978CD,LINE:2978CE,LINE:2978CF,LINE:2978D0,LINE:2978D1,LINE:2978D2,LINE:2978D3,LINE:2978D4,LINE:2978D5,LINE:2978D6,LINE:2978D7,LINE:2978D8,LINE:2978D9,LINE:2978DA,LINE:2978DB,LINE:2978DC,LINE:2978DD,LINE:2978DE,LINE:2978DF,LINE:2978E0,LINE:2978E1,LINE:2978E2,LINE:2978E3,LINE:2978E4,LINE:2978E5,LINE:2978E6,LINE:2978E7,LINE:2978E8,LINE:2978E9,LINE:2978EA,LINE:2978EB,LINE:2978EC,LINE:2978ED,LINE:2978EE,LINE:2978EF,LINE:2978F0,LINE:2978F1,LINE:2978F2,LINE:2978F3,LINE:2978F4,LINE:2978F5,LINE:2978F6,LINE:2978F7,LINE:2978F8,LINE:2978F9,LINE:2978FA,LINE:2978FB,LINE:2978FC,LINE:2978FD,LINE:2978FE,LINE:2978FF,LINE:29790A,LINE:29790B,LINE:29790C,LINE:29790D,LINE:29790E,LINE:29790F,LINE:29791A,LINE:29791B,LINE:29791C,LINE:29791D,LINE:29791E,LINE:29791F,LINE:29792A,LINE:29792B,LINE:29792C,LINE:29792D,LINE:29792E,LINE:29792F,LINE:29793A,LINE:29793B,LINE:29793C,LINE:29793D,LINE:29793E,LINE:29793F,LINE:29794A,LINE:29794B,LINE:29794C,LINE:29794D,LINE:29794E,LINE:29794F,LINE:29795A,LINE:29795B,LINE:29795C,LINE:29795D,LINE:29795E,LINE:29795F,LINE:29796A,LINE:29796B,LINE:29796C,LINE:29796D,LINE:29796E,LINE:29796F,LINE:29797A,LINE:29797B,LINE:29797C,LINE:29797D,LINE:29797E,LINE:29797F,LINE:29798A,LINE:29798B,LINE:29798C,LINE:29798D,LINE:29798E,LINE:29798F,LINE:29799A,LINE:29799B,LINE:29799C,LINE:29799D,LINE:29799E,LINE:29799F,LINE:2979A0,LINE:2979A1,LINE:2979A2,LINE:2979A3,LINE:2979A4,LINE:2979A5,LINE:2979A6,LINE:2979A7,LINE:2979A8,LINE:2979A9,LINE:2979AA,LINE:2979AB,LINE:2979AC,LINE:2979AD,LINE:2979AE,LINE:2979AF,LINE:2979B0,LINE:2979B1,LINE:2979B2,LINE:2979B3,LINE:2979B4,LINE:2979B5,LINE:2979B6,LINE:2979B7,LINE:2979B8,LINE:2979B9,LINE:2979BA,LINE:2979BB,LINE:2979BC,LINE:2979BD,LINE:2979BE,LINE:2979BF,LINE:2979C0,LINE:2979C1,LINE:2979C2,LINE:2979C3,LINE:2979C4,LINE:2979C5,LINE:2979C6,LINE:2979C7,LINE:2979C8,LINE:2979C9,LINE:2979CA,LINE:2979CB,LINE:2979CC,LINE:2979CD,LINE:2979CE,LINE:2979CF,LINE:2979D0,LINE:2979D1,LINE:2979D2,LINE:2979D3,LINE:2979D4,LINE:2979D5,LINE:2979D6,LINE:2979D7,LINE:2979D8,LINE:2979D9,LINE:2979DA,LINE:2979DB,LINE:2979DC,LINE:2979DD,LINE:2979DE,LINE:2979DF,LINE:2979E0,LINE:2979E1,LINE:2979E2,LINE:2979E3,LINE:2979E4,LINE:2979E5,LINE:2979E6,LINE:2979E7,LINE:2979E8,LINE:2979E9,LINE:2979EA,LINE:2979EB,LINE:2979EC,LINE:2979ED,LINE:2979EE,LINE:2979EF,LINE:2979F0,LINE:2979F1,LINE:2979F2,LINE:2979F3,LINE:2979F4,LINE:2979F5,LINE:2979F6,LINE:2979F7,LINE:2979F8,LINE:2979F9,LINE:2979FA,LINE:2979FB,LINE:2979FC,LINE:2979FD,LINE:2979FE,LINE:2979FF,LINE:297A00,LINE:297A01,LINE:297A02,LINE:297A03,LINE:297A04,LINE:297A05,LINE:297A06,LINE:297A07,LINE:297A08,LINE:297A09,LINE:297A0A,LINE:297A0B,LINE:297A0C,LINE:297A0D,LINE:297A0E,LINE:297A0F,LINE:297A10,LINE:297A11,LINE:297A12,LINE:297A13,LINE:297A14,LINE:297A15,LINE:297A16,LINE:297A17,LINE:297A18,LINE:297A19,LINE:297A1A,LINE:297A1B,LINE:297A1C,LINE:297A1D,LINE:297A1E,LINE:297A1F,LINE:297A20,LINE:297A21,LINE:297A22,LINE:297A23,LINE:297A24,LINE:297A25,LINE:297A26,LINE:297A27,LINE:297A28,LINE:297A29,LINE:297A2A,LINE:297A2B,LINE:297A2C,LINE:297A2D,LINE:297A2E,LINE:297A2F,LINE:297A30,LINE:297A31,LINE:297A32,LINE:297A33,LINE:297A34,LINE:297A35,LINE:297A36,LINE:297A37,LINE:297A38,LINE:297A39,LINE:297A3A,LINE:297A3B,LINE:297A3C,LINE:297A3D,LINE:297A3E,LINE:297A3F,LINE:297A40,LINE:297A41,LINE:297A42,LINE:297A43,LINE:297A44,LINE:297A45,LINE:297A46,LINE:297A47,LINE:297A48,LINE:297A49,LINE:297A4A,LINE:297A4B,LINE:297A4C,LINE:297A4D,LINE:297A4E,LINE:297A4F,LINE:297A50,LINE:297A51,LINE:297A52,LINE:297A53,LINE:297A54,LINE:297A55,LINE:297A56,LINE:297A57,LINE:297A58,LINE:297A59,LINE:297A5A,LINE:297A5B,LINE:297A5C,LINE:297A5D,LINE:297A5E,LINE:297A5F,LINE:297A60,LINE:297A61,LINE:297A62,LINE:297A63,LINE:297A64,LINE:297A65,LINE:297A66,LINE:297A67,LINE:297A68,LINE:297A69,LINE:297A6A,LINE:297A6B,LINE:297A6C,LINE:297A6D,LINE:297A6E,LINE:297A6F,LINE:297A70,LINE:297A71,LINE:297A72,LINE:297A73,LINE:297A74,LINE:297A75,LINE:297A76,LINE:297A77,LINE:297A78,LINE:297A79,LINE:297A7A,LINE:297A7B,LINE:297A7C,LINE:297A7D,LINE:297A7E,LINE:297A7F,LINE:297A80,LINE:297A81,LINE:297A82,LINE:297A83,LINE:297A84,LINE:297A85,LINE:297A86,LINE:297A87,LINE:297A88,LINE:297A89,LINE:297A8A,LINE:297A8B,LINE:297A8C,LINE:297A8D,LINE:297A8E,LINE:297A8F,LINE:297A90,LINE:297A91,LINE:297A92,LINE:297A93,LINE:297A94,LINE:297A95,LINE:297A96,LINE:297A97,LINE:297A98,LINE:297A99,LINE:297A9A,LINE:297A9B,LINE:297A9C,LINE:297A9D,LINE:297A9E,LINE:297A9F,LINE:297AA0,LINE:297AA1,LINE:297AA2,LINE:297AA3,LINE:297AA4,LINE:297AA5,LINE:297AA6,LINE:297AA7,LINE:297AA8,LINE:297AA9,LINE:297AAA,LINE:297AAB,LINE:297AAC,LINE:297AAD,LINE:297AAE,LINE:297AAF,LINE:297AB0,LINE:297AB1,LINE:297AB2,LINE:297AB3,LINE:297AB4,LINE:297AB5,LINE:297AB6,LINE:297AB7,LINE:297AB8,LINE:297AB9,LINE:297ABA,LINE:297ABB,LINE:297ABC,LINE:297ABD,LINE:297ABE,LINE:297ABF,LINE:297AC0,LINE:297AC1,LINE:297AC2,LINE:297AC3,LINE:297AC4,LINE:297AC5,LINE:297AC6,LINE:297AC7,LINE:297AC8,LINE:297AC9,LINE:297ACA,LINE:297ACB,LINE:297ACC,LINE:297ACD,LINE:297ACE,LINE:297ACF,LINE:297AD0,LINE:297AD1,LINE:297AD2,LINE:297AD3,LINE:297AD4,LINE:297AD5,LINE:297AD6,LINE:297AD7,LINE:297AD8,LINE:297AD9,LINE:297ADA,LINE:297ADB,LINE:297ADC,LINE:297ADD,LINE:297ADE,LINE:297ADF,LINE:297AE0,LINE:297AE1,LINE:297AE2,LINE:297AE3,LINE:297AE4,LINE:297AE5,LINE:297AE6,LINE:297AE7,LINE:297AE8,LINE:297AE9,LINE:297AEA,LINE:297AEB,LINE:297AEC,LINE:297AED,LINE:297AEE,LINE:297AEF,LINE:297AF0,LINE:297AF1,LINE:297AF2,LINE:297AF3,LINE:297AF4,LINE:297AF5,LINE:297AF6,LINE:297AF7,LINE:297AF8,LINE:297AF9,LINE:297AFA,LINE:297AFB,LINE:297AFC,LINE:297AFD,LINE:297AFE,LINE:297AFF,LINE:297B00,LINE:297B01,LINE:297B02,LINE:297B03,LINE:297B04,LINE:297B05,LINE:297B06,LINE:297B07,LINE:297B08,LINE:297B09,LINE:297B0A,LINE:297B0B,LINE:297B0C,LINE:297B0D,LINE:297B0E,LINE:297B0F,LINE:297B10,LINE:297B11,LINE:297B12,LINE:297B13,LINE:297B14,LINE:297B15,LINE:297B16,LINE:297B17,LINE:297B18,LINE:297B19,LINE:297B1A,LINE:297B1B,LINE:297B1C,LINE:297B1D,LINE:297B1E,LINE:297B1F,LINE:297B20,LINE:297B21,LINE:297B22,LINE:297B23,LINE:297B24,LINE:297B25,LINE:297B26,LINE:297B27,LINE:297B28,LINE:297B29,LINE:297B2A,LINE:297B2B,LINE:297B2C,LINE:297B2D,LINE:297B2E,LINE:297B2F,LINE:297B30,LINE:297B31,LINE:297B32,LINE:297B33,LINE:297B34,LINE:297B35,LINE:297B36,LINE:297B37,LINE:297B38,LINE:297B39,LINE:297B3A,LINE:297B3B,LINE:297B3C,LINE:297B3D,LINE:297B3E,LINE:297B3F,LINE:297B40,LINE:297B41,LINE:297B42,LINE:297B43,LINE:297B44,LINE:297B45,LINE:297B46,LINE:297B47,LINE:297B48,LINE:297B49,LINE:297B4A,LINE:297B4B,LINE:297B4C,LINE:297B4D,LINE:297B4E,LINE:297B4F,LINE:297B50,LINE:297B51,LINE:297B52,LINE:297B53,LINE:297B54,LINE:297B55,LINE:297B56,LINE:297B57,LINE:297B58,LINE:297B59,LINE:297B5A,LINE:297B5B,LINE:297B5C,LINE:297B5D,LINE:297B5E,LINE:297B5F,LINE:297B60,LINE:297B61,LINE:297B62,LINE:297B63,LINE:297B64,LINE:297B65,LINE:297B66,LINE:297B67,LINE:297B68,LINE:297B69,LINE:297B6A,LINE:297B6B,LINE:297B6C,LINE:297B6D,LINE:297B6E,LINE:297B6F,LINE:297B70,LINE:297B71,LINE:297B72,LINE:297B73,LINE:297B74,LINE:297B75,LINE:297B76,LINE:297B77,LINE:297B78,LINE:297B79,LINE:297B7A,LINE:297B7B,LINE:297B7C,LINE:297B7D,LINE:297B7E,LINE:297B7F,LINE:297B80,LINE:297B81,LINE:297B82,LINE:297B83,LINE:297B84,LINE:297B85,LINE:297B86,LINE:297B87,LINE:297B88,LINE:297B89,LINE:297B8A,LINE:297B8B,LINE:297B8C,LINE:297B8D,LINE:297B8E,LINE:297B8F,LINE:297B90,LINE:297B91,LINE:297B92,LINE:297B93,LINE:297B94,LINE:297B95,LINE:297B96,LINE:297B97,LINE:297B98,LINE:297B99,LINE:297B9A,LINE:297B9B,LINE:297B9C,LINE:297B9D,LINE:297B9E,LINE:297B9F,LINE:297BA0,LINE:297BA1,LINE:297BA2,LINE:297BA3,LINE:297BA4,LINE:297BA5,LINE:297BA6,LINE:297BA7,LINE:297BA8,LINE:297BA9,LINE:297BAA,LINE:297BAB,LINE:297BAC,LINE:297BAD,LINE:297BAE,LINE:297BAF,LINE:297BB0,LINE:297BB1,LINE:297BB2,LINE:297BB3,LINE:297BB4,LINE:297BB5,LINE:297BB6,LINE:297BB7,LINE:297BB8,LINE:297BB9,LINE:297BBA,LINE:297BBB,LINE:297BBC,LINE:297BBD,LINE:297BBE,LINE:297BBF,LINE:297BC0,LINE:297BC1,LINE:297BC2,LINE:297BC3,LINE:297BC4,LINE:297BC5,LINE:297BC6,LINE:297BC7,LINE:297BC8,LINE:297BC9,LINE:297BCA,LINE:297BCB,LINE:297BCC,LINE:297BCD,LINE:297BCE,LINE:297BCF,LINE:297BD0,LINE:297BD1,LINE:297BD2,LINE:297BD3,LINE:297BD4,LINE:297BD5,LINE:297BD6,LINE:297BD7,LINE:297BD8,LINE:297BD9,LINE:297BDA,LINE:297BDB,LINE:297BDC,LINE:297BDD,LINE:297BDE,LINE:297BDF,LINE:297BE0,LINE:297BE1,LINE:297BE2,LINE:297BE3,LINE:297BE4,LINE:297BE5,LINE:297BE6,LINE:297BE7,LINE:297BE8,LINE:297BE9,LINE:297BEA,LINE:297BEB,LINE:297BEC,LINE:297BED,LINE:297BEE,LINE:297BEF,LINE:297BF0,LINE:297BF1,LINE:297BF2,LINE:297BF3,LINE:297BF4,LINE:297BF5,LINE:297BF6,LINE:297BF9,LINE:297BFA,LINE:297BFB,LINE:297BFC,LINE:297BFD,LINE:297BFE,LINE:297BFF,LINE:297C00,LINE:297C01,LINE:297C02,LINE:297C03,LINE:297C04,LINE:297C05,LINE:297C06,LINE:297C07,LINE:297C08,LINE:297C09,LINE:297C0A,LINE:297C0B,LINE:297C0C,LINE:297C0D,LINE:297C0E,LINE:297C0F,LINE:297C10,LINE:297C11,LINE:297C12,LINE:297C13,LINE:297C14,LINE:297C15,LINE:297C16,LINE:297C17,LINE:297C18,LINE:297C19,LINE:297C1A,LINE:297C1B,LINE:297C1C,LINE:297C1D,LINE:297C1E,LINE:297C1F,LINE:297C20,LINE:297C21,LINE:297C22,LINE:297C23,LINE:297C24,LINE:297C25,LINE:297C26,LINE:297C27,LINE:297C28,LINE:297C29,LINE:297C2A,LINE:297C2B,LINE:297C2C,LINE:297C2D,LINE:297C2E,LINE:297C2F,LINE:297C30,LINE:297C31,LINE:297C32,LINE:297C33,LINE:297C34,LINE:297C35,LINE:297C36,LINE:297C37,LINE:297C38,LINE:297C39,LINE:297C3A,LINE:297C3B,LINE:297C3C,LINE:297C60,LINE:297C61,LINE:297C62,LINE:297C63,LINE:297C64,LINE:297C65,LINE:297C67,LINE:297C68,LINE:297C69,LINE:297C6A vector 0.90; real06.dwg recognition:sym_L1_001 ai 0.95; +2 more | yes | 30 % of its pixels > 0.10 m outside the drawing, 465725 px |
| cam_r_L1_ebeveyn_y_odasi_1 | cycles | cross-check misplaced | f_L1_010 | bed_double | - | from_documents | real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF vector 0.90; real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF inferred 0.60 | yes | 13 % of its pixels > 0.10 m outside the drawing, 251831 px |

## Needs review

- cam_r_L1_cocuk_odasi_3: json cross-check misplaced: f_L1_004
- cam_r_L1_ebeveyn_y_odasi_1: json cross-check misplaced: f_L1_010

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
- o_L1_001
- o_L1_002
- o_L1_003
- o_L1_004
- o_L1_005
- o_L1_006
- o_L1_007
- r_L0_salon
- r_L0_mutfak
- r_L0_oda
- r_L1_oda
- r_L1_dus
- f_L0_001
- f_L0_004
- f_L0_005
- f_L0_006
- f_L0_009
- f_L0_010
- f_L0_011
- f_L0_012
- f_L0_013
- f_L0_014
- f_L0_015
- f_L0_020
- f_L0_027
- f_L0_028
- f_L0_029
- f_L0_030
- f_L1_002
- f_L1_003
- f_L1_005
- f_L1_006
- f_L1_009
- f_L1_010
- f_L1_011
- f_L1_012
- f_L1_013
- f_L1_014
- f_L1_017
- f_L1_020
- f_L1_024
- f_L1_025
- f_L1_026
- f_L1_027
- f_L0_031
- f_L0_032

Unverified pieces in view:

- cam_r_L0_banyo_1: f_L0_010
- cam_r_L0_mutfak_1: f_L0_020, f_L0_032, o_L0_001
- cam_r_L0_mutfak_2: f_L0_020, f_L0_031, o_L0_004
- cam_r_L0_mutfak_3: f_L0_001, f_L0_020, f_L0_032, o_L0_001, o_L0_004
- cam_r_L0_salon_1: f_L0_006, f_L0_011, f_L0_014, f_L0_027, f_L0_028, f_L0_029, f_L0_030, o_L0_003, o_L0_005
- cam_r_L0_salon_2: f_L0_006, f_L0_014, f_L0_015, o_L0_005, o_L0_006
- cam_r_L0_salon_3: f_L0_006, f_L0_011, f_L0_014, f_L0_027, f_L0_028, f_L0_029, f_L0_030, o_L0_003, o_L0_005
- cam_r_L1_banyo_1: f_L1_009, o_L1_004
- cam_r_L1_banyo_2: f_L1_009
- cam_r_L1_cocuk_odasi_1: f_L1_005
- cam_r_L1_cocuk_odasi_2: f_L1_005
- cam_r_L1_cocuk_odasi_3: f_L1_005
- cam_r_L1_ebeveyn_y_odasi_1: f_L1_010, f_L1_026, o_L1_007
- cam_r_L1_ebeveyn_y_odasi_2: f_L1_010, f_L1_020, f_L1_024, o_L1_006
- cam_r_L1_ebeveyn_y_odasi_3: f_L1_010, f_L1_026
- cam_r_L1_hol_1: f_L0_001
- cam_r_L1_oda_2_1: f_L1_013, f_L1_014, f_L1_025, o_L1_003, o_L1_005
- cam_r_L1_oda_2_2: f_L1_013, f_L1_014, f_L1_025, o_L1_003
- cam_r_L1_oda_2_3: f_L1_013, f_L1_025, o_L1_003, o_L1_005
- cam_r_L1_soyunma_odasi_1: f_L1_011, f_L1_012
- cam_r_L1_soyunma_odasi_2: f_L1_011, f_L1_012
- ext_1: o_L0_005, o_L0_006, o_L0_007, o_L1_006, o_L1_007
- ext_2: o_L0_002, o_L0_006, o_L0_007, o_L1_003, o_L1_004, o_L1_007
- ext_3: o_L0_002, o_L0_003, o_L0_004, o_L1_003, o_L1_004, o_L1_005
- ext_4: o_L0_003, o_L0_004
- ext_5: o_L0_002, o_L0_003, o_L0_004, o_L1_003, o_L1_004, o_L1_005

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L1_002 | untyped_piece | r_L1_cocuk_odasi | drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| TEXT:29AC25 | named_piece | r_L1_ebeveyn_y_odasi | the documents name a dresser ('*SIFONIYER' (TEXT:29AC25)) at (8.11, 4.91) m on L1 and no drawn dresser stands there: not added: the nearest place that passes every check in r_L1_ebeveyn_y_odasi is 1.47 m from the text (more than 1 m) | - |

Drawn symbols read as not furniture (never built): door_arc 1, level_mark 2.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L0_008 | furniture | armchair | 3dwh_1c9dbdb1c1d98b0c5c633595 | vision quality 2 (<= 2) |
| f_L0_010 | furniture | bathtub | 3dwh_1fab322fe57d8d05759235ad | vision quality 2 (<= 2) |
| f_L0_037 | furniture | table_dining | 3dwh_61d3ec6b31b39c2256ef4df4 | the vision check says it is not a table_dining (a side_table) |
| f_L0_038 | furniture | chair | 3dwh_040dd50cd138cbc316c9caec | the vision check says it is not a chair (a bar_stool) |
| f_L1_004 | furniture | bed_double | 3dwh_118ff62672cee88c43642f77 | the vision check sees more than one object |
| f_L1_019 | furniture | washing_machine | hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 | the vision check says it is not a washing_machine |

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L0_salon | Label says 39,15 m², polygon gives 55,58 m² (42.0%) | over 8%: room marked unverified, polygon from real06.dwg kept |
| c_002 | area_label_vs_computed | r_L0_mutfak | Label says 12,00 m², polygon gives 24,81 m² minus the stair 4,62 m² = 20,19 m² (68.3%) | over 8%: room marked unverified, polygon from real06.dwg kept |
| c_003 | area_label_vs_computed | r_L0_banyo | Label says 7,25 m², polygon gives 6,67 m² (8.0%) | within tolerance (8%), kept polygon from real06.dwg |
| c_004 | area_label_vs_computed | r_L1_ebeveyn_y_odasi | Label says 23,90 m², polygon gives 23,32 m² (2.4%) | within tolerance (8%), kept polygon from real06.dwg |
| c_005 | area_label_vs_computed | r_L1_cocuk_odasi | Label says 23,10 m², polygon gives 22,39 m² (3.1%) | within tolerance (8%), kept polygon from real06.dwg |
| c_006 | area_label_vs_computed | r_L1_soyunma_odasi | Label says 6,25 m², polygon gives 5,88 m² (5.9%) | within tolerance (8%), kept polygon from real06.dwg |
| c_007 | area_label_vs_computed | r_L1_dus | Label says 5,00 m², polygon gives 4,53 m² (9.4%) | over 8%: room marked unverified, polygon from real06.dwg kept |
| c_008 | area_label_vs_computed | r_L1_oda_2 | Label says 12,00 m², polygon gives 11,34 m² (5.5%) | within tolerance (8%), kept polygon from real06.dwg |
| c_009 | area_label_vs_computed | r_L1_banyo | Label says 7,25 m², polygon gives 6,67 m² (8.0%) | within tolerance (8%), kept polygon from real06.dwg |
| c_010 | dimension_vs_measured | L0 | real06.dwg: dimension text 1 vs measured 0.70 m (42.9%) | kept measured geometry (DWG) |
| c_011 | dimension_vs_measured | L0 | real06.dwg: dimension text 1 vs measured 0.50 m (100.0%) | kept measured geometry (DWG) |
| c_012 | dimension_vs_measured | L0 | real06.dwg: dimension text 3 vs measured 1.40 m (114.3%) | kept measured geometry (DWG) |
| c_013 | dimension_vs_measured | w_L0_012 | real06.dwg: dimension text 2 vs measured 1.00 m (100.0%) | kept measured geometry (DWG) |
| c_014 | dimension_vs_measured | w_L0_021, w_L0_012 | real06.dwg: dimension text 3 vs measured 1.00 m (200.0%) | kept measured geometry (DWG) |
| c_015 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 4 vs measured 1.00 m (300.0%) | kept measured geometry (DWG) |
| c_016 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 5 vs measured 1.00 m (400.0%) | kept measured geometry (DWG) |
| c_017 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 6 vs measured 1.00 m (500.0%) | kept measured geometry (DWG) |
| c_018 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 7 vs measured 1.00 m (600.0%) | kept measured geometry (DWG) |
| c_019 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 8 vs measured 1.00 m (700.0%) | kept measured geometry (DWG) |
| c_020 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 9 vs measured 1.00 m (800.0%) | kept measured geometry (DWG) |
| c_021 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 10 vs measured 1.00 m (900.0%) | kept measured geometry (DWG) |
| c_022 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 11 vs measured 1.00 m (1000.0%) | kept measured geometry (DWG) |
| c_023 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 12 vs measured 0.48 m (2390.1%) | kept measured geometry (DWG) |
| c_024 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 13 vs measured 1.00 m (1200.0%) | kept measured geometry (DWG) |
| c_025 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 14 vs measured 1.00 m (1300.0%) | kept measured geometry (DWG) |
| c_026 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 15 vs measured 1.00 m (1400.0%) | kept measured geometry (DWG) |
| c_027 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 16 vs measured 1.00 m (1500.0%) | kept measured geometry (DWG) |
| c_028 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 17 vs measured 1.00 m (1600.0%) | kept measured geometry (DWG) |
| c_029 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 18 vs measured 0.58 m (3012.0%) | kept measured geometry (DWG) |
| c_030 | dimension_vs_measured | L0 | real06.dwg: dimension text 7,20 vs measured 6.60 m (9.1%) | kept measured geometry (DWG) |
| c_031 | dimension_vs_measured | w_L0_019 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_032 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 70 vs measured 0.70 m (9900.0%) | kept measured geometry (DWG) |
| c_033 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 70 vs measured 1.15 m (5987.0%) | kept measured geometry (DWG) |
| c_034 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 70 vs measured 0.70 m (9900.0%) | kept measured geometry (DWG) |
| c_035 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_036 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 35 vs measured 0.19 m (18321.1%) | kept measured geometry (DWG) |
| c_037 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 50 vs measured 0.50 m (9916.0%) | kept measured geometry (DWG) |
| c_038 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 155 vs measured 1.55 m (9894.8%) | kept measured geometry (DWG) |
| c_039 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.24 m (10104.1%) | kept measured geometry (DWG) |
| c_040 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_041 | dimension_vs_measured | L0 | real06.dwg: dimension text 295 vs measured 2.95 m (9900.0%) | kept measured geometry (DWG) |
| c_042 | dimension_vs_measured | w_L0_019 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_043 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_044 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_045 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_046 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_047 | dimension_vs_measured | L0 | real06.dwg: dimension text 245 vs measured 2.45 m (9900.0%) | kept measured geometry (DWG) |
| c_048 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_049 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_050 | dimension_vs_measured | L0 | real06.dwg: dimension text 155 vs measured 1.55 m (9900.0%) | kept measured geometry (DWG) |
| c_051 | dimension_vs_measured | w_L0_015 | real06.dwg: dimension text 80 vs measured 0.80 m (9903.8%) | kept measured geometry (DWG) |
| c_052 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 10 vs measured 0.10 m (9870.1%) | kept measured geometry (DWG) |
| c_053 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_054 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.03 m (70322.5%) | kept measured geometry (DWG) |
| c_055 | dimension_vs_measured | w_L0_014 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_056 | dimension_vs_measured | L0 | real06.dwg: dimension text 140 vs measured 1.40 m (9900.0%) | kept measured geometry (DWG) |
| c_057 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_058 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_059 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_060 | dimension_vs_measured | L0 | real06.dwg: dimension text 85 vs measured 0.85 m (9909.4%) | kept measured geometry (DWG) |
| c_061 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 200 vs measured 2.00 m (9896.0%) | kept measured geometry (DWG) |
| c_062 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_063 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_064 | dimension_vs_measured | L0 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_065 | dimension_vs_measured | w_L0_012 | real06.dwg: dimension text 200 vs measured 1.84 m (10764.3%) | kept measured geometry (DWG) |
| c_066 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 180 vs measured 1.07 m (16666.0%) | kept measured geometry (DWG) |
| c_067 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_068 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_069 | dimension_vs_measured | L0 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_070 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_071 | dimension_vs_measured | L0 | real06.dwg: dimension text 480 vs measured 2.46 m (19441.6%) | kept measured geometry (DWG) |
| c_072 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_073 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 25 vs measured 0.24 m (10209.3%) | kept measured geometry (DWG) |
| c_074 | dimension_vs_measured | w_L0_004 | real06.dwg: dimension text 5 vs measured 0.05 m (9900.0%) | kept measured geometry (DWG) |
| c_075 | dimension_vs_measured | w_L0_004 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_076 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 95 vs measured 0.95 m (9900.0%) | kept measured geometry (DWG) |
| c_077 | dimension_vs_measured | L0 | real06.dwg: dimension text 385 vs measured 3.85 m (9900.0%) | kept measured geometry (DWG) |
| c_078 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.03 m (58551.0%) | kept measured geometry (DWG) |
| c_079 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_080 | dimension_vs_measured | L0 | real06.dwg: dimension text 465 vs measured 4.65 m (9900.0%) | kept measured geometry (DWG) |
| c_081 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_082 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 385 vs measured 0.46 m (83723.2%) | kept measured geometry (DWG) |
| c_083 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.94 m (2025.6%) | kept measured geometry (DWG) |
| c_084 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_085 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 65 vs measured 0.65 m (9901.5%) | kept measured geometry (DWG) |
| c_086 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 220 vs measured 0.82 m (26696.6%) | kept measured geometry (DWG) |
| c_087 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 95 vs measured 0.95 m (9900.0%) | kept measured geometry (DWG) |
| c_088 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.24 m (10116.6%) | kept measured geometry (DWG) |
| c_089 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_090 | dimension_vs_measured | L0 | real06.dwg: dimension text 465 vs measured 4.65 m (9900.0%) | kept measured geometry (DWG) |
| c_091 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_092 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 25 vs measured 0.28 m (8990.9%) | kept measured geometry (DWG) |
| c_093 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 150 vs measured 0.83 m (17985.4%) | kept measured geometry (DWG) |
| c_094 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 125 vs measured 1.25 m (9900.0%) | kept measured geometry (DWG) |
| c_095 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_096 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 125 vs measured 1.25 m (9898.4%) | kept measured geometry (DWG) |
| c_097 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 220 vs measured 2.20 m (9900.9%) | kept measured geometry (DWG) |
| c_098 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_099 | dimension_vs_measured | w_L0_023 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_100 | dimension_vs_measured | L0 | real06.dwg: dimension text 490 vs measured 4.90 m (9900.0%) | kept measured geometry (DWG) |
| c_101 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_102 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_103 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 400 vs measured 4.00 m (9900.0%) | kept measured geometry (DWG) |
| c_104 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_105 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 560 vs measured 5.60 m (9900.0%) | kept measured geometry (DWG) |
| c_106 | dimension_vs_measured | w_L0_023 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_107 | dimension_vs_measured | w_L0_025 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_108 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 100 vs measured 2.50 m (3900.0%) | kept measured geometry (DWG) |
| c_109 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_110 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_111 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_112 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 80 vs measured 0.80 m (9900.0%) | kept measured geometry (DWG) |
| c_113 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 370 vs measured 3.70 m (9899.2%) | kept measured geometry (DWG) |
| c_114 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 110 vs measured 1.10 m (9902.7%) | kept measured geometry (DWG) |
| c_115 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_116 | dimension_vs_measured | L0 | real06.dwg: dimension text 490 vs measured 4.90 m (9900.0%) | kept measured geometry (DWG) |
| c_117 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_118 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 20 vs measured 0.05 m (37707.2%) | kept measured geometry (DWG) |
| c_119 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 300 vs measured 3.00 m (9900.0%) | kept measured geometry (DWG) |
| c_120 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_121 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_122 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 570 vs measured 5.70 m (9900.0%) | kept measured geometry (DWG) |
| c_123 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 215 vs measured 2.15 m (9900.9%) | kept measured geometry (DWG) |
| c_124 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 80 vs measured 0.80 m (9897.5%) | kept measured geometry (DWG) |
| c_125 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 15 vs measured 0.15 m (9900.0%) | kept measured geometry (DWG) |
| c_126 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_127 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 20 vs measured 0.41 m (4755.5%) | kept measured geometry (DWG) |
| c_128 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 290 vs measured 2.90 m (9900.0%) | kept measured geometry (DWG) |
| c_129 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_130 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_131 | dimension_vs_measured | w_L0_033 | real06.dwg: dimension text 100 vs measured 1.00 m (9857.2%) | kept measured geometry (DWG) |
| c_132 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (10349.3%) | kept measured geometry (DWG) |
| c_133 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_134 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 880 vs measured 5.83 m (14987.1%) | kept measured geometry (DWG) |
| c_135 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9915.0%) | kept measured geometry (DWG) |
| c_136 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_137 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_138 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_139 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 360 vs measured 1.07 m (33633.1%) | kept measured geometry (DWG) |
| c_140 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.60 m (9896.3%) | kept measured geometry (DWG) |
| c_141 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 80 vs measured 0.47 m (17008.6%) | kept measured geometry (DWG) |
| c_142 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.47 m (10754.8%) | kept measured geometry (DWG) |
| c_143 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 110 vs measured 1.10 m (9876.4%) | kept measured geometry (DWG) |
| c_144 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_145 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 330 vs measured 3.30 m (9900.0%) | kept measured geometry (DWG) |
| c_146 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 80 vs measured 0.80 m (9900.0%) | kept measured geometry (DWG) |
| c_147 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_148 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_149 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 360 vs measured 3.60 m (9900.0%) | kept measured geometry (DWG) |
| c_150 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_151 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.60 m (9900.0%) | kept measured geometry (DWG) |
| c_152 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_153 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 40 vs measured 0.40 m (9900.0%) | kept measured geometry (DWG) |
| c_154 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_155 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.60 m (9900.0%) | kept measured geometry (DWG) |
| c_156 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_157 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 110 vs measured 1.10 m (9900.0%) | kept measured geometry (DWG) |
| c_158 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_159 | dimension_vs_measured | L0 | real06.dwg: dimension text 180 vs measured 1.80 m (9900.0%) | kept measured geometry (DWG) |
| c_160 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_161 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 910 vs measured 9.10 m (9900.0%) | kept measured geometry (DWG) |
| c_162 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_163 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 330 vs measured 3.30 m (9900.0%) | kept measured geometry (DWG) |
| c_164 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_165 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 125 vs measured 1.25 m (9900.0%) | kept measured geometry (DWG) |
| c_166 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_167 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 150 vs measured 1.50 m (9900.0%) | kept measured geometry (DWG) |
| c_168 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_169 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 235 vs measured 2.35 m (9900.0%) | kept measured geometry (DWG) |
| c_170 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_171 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 220 vs measured 2.20 m (9900.0%) | kept measured geometry (DWG) |
| c_172 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_173 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_174 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 195 vs measured 1.95 m (9900.0%) | kept measured geometry (DWG) |
| c_175 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 80 vs measured 0.80 m (9900.0%) | kept measured geometry (DWG) |
| c_176 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 35 vs measured 0.35 m (9900.0%) | kept measured geometry (DWG) |
| c_177 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_178 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_179 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 1020 vs measured 10.20 m (9900.0%) | kept measured geometry (DWG) |
| c_180 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_181 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_182 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_183 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_184 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_185 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 260 vs measured 2.60 m (9900.0%) | kept measured geometry (DWG) |
| c_186 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 320 vs measured 3.20 m (9900.0%) | kept measured geometry (DWG) |
| c_187 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_188 | dimension_vs_measured | L0 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_189 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_190 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_191 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 1430 vs measured 14.30 m (9900.0%) | kept measured geometry (DWG) |
| c_192 | dimension_vs_measured | w_L0_025 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_193 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_194 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_195 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_196 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 260 vs measured 2.60 m (9900.0%) | kept measured geometry (DWG) |
| c_197 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 320 vs measured 3.20 m (9900.0%) | kept measured geometry (DWG) |
| c_198 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_199 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 1430 vs measured 14.30 m (9900.0%) | kept measured geometry (DWG) |
| c_200 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_201 | dimension_vs_measured | L0 | real06.dwg: dimension text 315 vs measured 3.15 m (9900.0%) | kept measured geometry (DWG) |
| c_202 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 95 vs measured 0.95 m (9900.0%) | kept measured geometry (DWG) |
| c_203 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 70 vs measured 0.70 m (9900.0%) | kept measured geometry (DWG) |
| c_204 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 130 vs measured 1.30 m (9900.0%) | kept measured geometry (DWG) |
| c_205 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 50 vs measured 0.50 m (9900.0%) | kept measured geometry (DWG) |
| c_206 | dimension_vs_measured | L0 | real06.dwg: dimension text 180 vs measured 1.80 m (9900.0%) | kept measured geometry (DWG) |
| c_207 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_208 | dimension_vs_measured | L0 | real06.dwg: dimension text 315 vs measured 3.15 m (9900.0%) | kept measured geometry (DWG) |
| c_209 | dimension_vs_measured | L0 | real06.dwg: dimension text 525 vs measured 5.25 m (9900.0%) | kept measured geometry (DWG) |
| c_210 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.30 m (3233.3%) | kept measured geometry (DWG) |
| c_211 | dimension_vs_measured | L0 | real06.dwg: dimension text 165 vs measured 1.65 m (9900.0%) | kept measured geometry (DWG) |
| c_212 | dimension_vs_measured | w_L0_019 | real06.dwg: dimension text 150 vs measured 1.50 m (9900.0%) | kept measured geometry (DWG) |
| c_213 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_214 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_215 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 140 vs measured 1.40 m (9900.0%) | kept measured geometry (DWG) |
| c_216 | dimension_vs_measured | L0 | real06.dwg: dimension text 265 vs measured 2.65 m (9900.0%) | kept measured geometry (DWG) |
| c_217 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_218 | dimension_vs_measured | L0 | real06.dwg: dimension text 840 vs measured 8.40 m (9900.0%) | kept measured geometry (DWG) |
| c_219 | dimension_vs_measured | L0 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_220 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_221 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_222 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 300 vs measured 3.00 m (9900.0%) | kept measured geometry (DWG) |
| c_223 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_224 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 65 vs measured 0.65 m (9900.0%) | kept measured geometry (DWG) |
| c_225 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_226 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 220 vs measured 2.20 m (9900.0%) | kept measured geometry (DWG) |
| c_227 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_228 | dimension_vs_measured | L0 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_229 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_230 | dimension_vs_measured | L0 | real06.dwg: dimension text 120 vs measured 1.20 m (9900.0%) | kept measured geometry (DWG) |
| c_231 | dimension_vs_measured | L0 | real06.dwg: dimension text 415 vs measured 4.15 m (9900.0%) | kept measured geometry (DWG) |
| c_232 | dimension_vs_measured | L0 | real06.dwg: dimension text 425 vs measured 4.25 m (9900.0%) | kept measured geometry (DWG) |
| c_233 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.30 m (3233.3%) | kept measured geometry (DWG) |
| c_234 | dimension_vs_measured | L0 | real06.dwg: dimension text 165 vs measured 1.65 m (9900.0%) | kept measured geometry (DWG) |
| c_235 | dimension_vs_measured | w_L0_004 | real06.dwg: dimension text 150 vs measured 1.50 m (9900.0%) | kept measured geometry (DWG) |
| c_236 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_237 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_238 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 140 vs measured 1.40 m (9900.0%) | kept measured geometry (DWG) |
| c_239 | dimension_vs_measured | L0 | real06.dwg: dimension text 265 vs measured 2.65 m (9900.0%) | kept measured geometry (DWG) |
| c_240 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_241 | dimension_vs_measured | L0 | real06.dwg: dimension text 840 vs measured 8.40 m (9900.0%) | kept measured geometry (DWG) |
| c_242 | dimension_vs_measured | L0 | real06.dwg: dimension text 180 vs measured 1.80 m (9900.0%) | kept measured geometry (DWG) |
| c_243 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_244 | dimension_vs_measured | L0 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_245 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_246 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_247 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 6 vs measured 1.00 m (94.0%) | kept measured geometry (DWG) |
| c_248 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 7 vs measured 1.00 m (93.0%) | kept measured geometry (DWG) |
| c_249 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 8 vs measured 1.00 m (92.0%) | kept measured geometry (DWG) |
| c_250 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 9 vs measured 1.00 m (91.0%) | kept measured geometry (DWG) |
| c_251 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 10 vs measured 1.00 m (90.0%) | kept measured geometry (DWG) |
| c_252 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 11 vs measured 1.00 m (89.0%) | kept measured geometry (DWG) |
| c_253 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 12 vs measured 0.48 m (75.1%) | kept measured geometry (DWG) |
| c_254 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 13 vs measured 1.00 m (87.0%) | kept measured geometry (DWG) |
| c_255 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 14 vs measured 1.00 m (86.0%) | kept measured geometry (DWG) |
| c_256 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 15 vs measured 1.00 m (85.0%) | kept measured geometry (DWG) |
| c_257 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 16 vs measured 1.00 m (84.0%) | kept measured geometry (DWG) |
| c_258 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 17 vs measured 1.00 m (83.0%) | kept measured geometry (DWG) |
| c_259 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 18 vs measured 0.85 m (78.8%) | kept measured geometry (DWG) |
| c_260 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 25 vs measured 0.20 m (24.3%) | kept measured geometry (DWG) |
| c_261 | dimension_vs_measured | w_L1_020 | real06.dwg: dimension text 30 vs measured 0.33 m (7.7%) | kept measured geometry (DWG) |
| c_262 | dimension_vs_measured | w_L1_020 | real06.dwg: dimension text 35 vs measured 0.15 m (133.3%) | kept measured geometry (DWG) |
| c_263 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 20 vs measured 0.09 m (130.9%) | kept measured geometry (DWG) |
| c_264 | dimension_vs_measured | w_L1_038 | real06.dwg: dimension text 20 vs measured 0.41 m (51.5%) | kept measured geometry (DWG) |
| c_265 | dimension_vs_measured | L1 | real06.dwg: dimension text 25 vs measured 0.17 m (44.5%) | kept measured geometry (DWG) |
| c_266 | dimension_vs_measured | L1 | real06.dwg: dimension text 20 vs measured 0.05 m (300.0%) | kept measured geometry (DWG) |
| c_267 | dimension_vs_measured | w_L1_028 | real06.dwg: dimension text 275 vs measured 0.82 m (235.4%) | kept measured geometry (DWG) |
| c_268 | dimension_vs_measured | L1 | real06.dwg: dimension text 25 vs measured 0.23 m (11.1%) | kept measured geometry (DWG) |
| c_269 | dimension_vs_measured | w_L1_001 | real06.dwg: dimension text 95 vs measured 0.74 m (28.3%) | kept measured geometry (DWG) |
| c_270 | dimension_vs_measured | w_L1_001 | real06.dwg: dimension text 220 vs measured 1.27 m (72.8%) | kept measured geometry (DWG) |
| c_271 | dimension_vs_measured | w_L1_022 | real06.dwg: dimension text 190 vs measured 0.36 m (427.8%) | kept measured geometry (DWG) |
| c_272 | dimension_vs_measured | w_L1_022 | real06.dwg: dimension text 205 vs measured 0.36 m (469.4%) | kept measured geometry (DWG) |
| c_273 | dimension_vs_measured | w_L1_019 | real06.dwg: dimension text 20 vs measured 0.64 m (68.9%) | kept measured geometry (DWG) |
| c_274 | dimension_vs_measured | w_L1_004 | real06.dwg: dimension text 20 vs measured 0.03 m (604.2%) | kept measured geometry (DWG) |
| c_275 | dimension_vs_measured | w_L1_033 | real06.dwg: dimension text 25 vs measured 0.20 m (22.8%) | kept measured geometry (DWG) |
| c_276 | dimension_vs_measured | w_L1_033 | real06.dwg: dimension text 5 vs measured 0.29 m (82.8%) | kept measured geometry (DWG) |
| c_277 | dimension_vs_measured | w_L1_029 | real06.dwg: dimension text 460 vs measured 1.79 m (156.8%) | kept measured geometry (DWG) |
| c_278 | dimension_vs_measured | w_L1_032 | real06.dwg: dimension text 190 vs measured 1.40 m (35.7%) | kept measured geometry (DWG) |
| c_279 | dimension_vs_measured | L1 | real06.dwg: dimension text 15 vs measured 0.82 m (81.8%) | kept measured geometry (DWG) |
| c_280 | dimension_vs_measured | L1 | real06.dwg: dimension text 20 vs measured 0.33 m (38.5%) | kept measured geometry (DWG) |
| c_281 | dimension_vs_measured | L1 | real06.dwg: dimension text 20 vs measured 0.15 m (33.4%) | kept measured geometry (DWG) |
| c_282 | dimension_vs_measured | w_L1_038 | real06.dwg: dimension text 250 vs measured 2.22 m (12.7%) | kept measured geometry (DWG) |
| c_283 | dimension_vs_measured | w_L1_038 | real06.dwg: dimension text 110 vs measured 1.20 m (8.3%) | kept measured geometry (DWG) |
| c_284 | dimension_vs_measured | L1 | real06.dwg: dimension text 10 vs measured 0.30 m (66.7%) | kept measured geometry (DWG) |
| c_285 | dimension_vs_measured | L1 | real06.dwg: dimension text 10 vs measured 0.30 m (66.7%) | kept measured geometry (DWG) |
| c_286 | outline_mismatch | L0, L1 | Outer wall outline of Level 1 differs from Ground floor by up to 0.201 m (areas 105.78 / 105.77 m²) | unresolved: each level kept as drawn |
| c_287 | type_disagreement | sy_L0_002 | f_L0_023: the AI passes typed it wall_cabinet, the drawing shows a level_mark (drawn on the 'kot' layer(s): level_mark, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_288 | symbol_type_disagreement | f_L0_006 | f_L0_006: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_289 | symbol_type_disagreement | f_L0_009 | f_L0_009: sym_L0_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_290 | symbol_type_disagreement | f_L0_010 | f_L0_010: sym_L0_005: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | typed bathtub by code (ai_member): bathtub: r_L0_banyo misses it (r_L0_banyo.bathroom_set (anchor f_L0_024) misses shower\|bathtub) and the AI passes named it (pass 1 (qwen)'s reason names bathtub; pass 2 (glm)'s reason names bathtub); the drawn 2.54 x 1.01 m is outside the b; inferred, listed in the report |
| c_291 | symbol_type_disagreement | f_L0_012 | f_L0_012: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_292 | symbol_type_disagreement | f_L0_013 | f_L0_013: sym_L0_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_293 | symbol_type_disagreement | f_L0_014 | f_L0_014: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_dining, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_294 | symbol_type_disagreement | f_L0_015 | f_L0_015: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) bookshelf | typed table_coffee by code (ai_member): table_coffee: r_L0_salon misses it (r_L0_salon.seating (anchor f_L0_006) misses table_coffee) and the AI passes named it (pass 1 (qwen) answered table_coffee; pass 1 (qwen)'s reason names table_coffee); plan crop recognition/crops/sym_L0_01; inferred, listed in the report |
| c_295 | symbol_type_disagreement | f_L0_019 | f_L0_019: sym_L0_014: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_296 | symbol_type_disagreement | f_L0_022 | f_L0_022: sym_L0_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) washbasin | unresolved: the drawn footprint is kept as unknown, unverified |
| c_297 | symbol_type_disagreement | f_L0_024 | f_L0_024: sym_L0_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) washbasin, pass 2 (zai-org/GLM-4.6V-Flash) toilet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_298 | symbol_type_disagreement | f_L0_025 | f_L0_025: sym_L0_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sink_kitchen, pass 2 (zai-org/GLM-4.6V-Flash) wall_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_299 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_022: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_300 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_023: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_301 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_024: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_302 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_025: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_303 | symbol_type_disagreement | f_L1_005 | f_L1_005: sym_L1_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) dresser, pass 2 (zai-org/GLM-4.6V-Flash) desk | typed dresser by code (name_text): dresser: the documents name it: the text '*SIFONIYER' (TEXT:29AC0C) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.56 m within 40%; inferred, listed in the report |
| c_304 | symbol_type_disagreement | f_L1_006 | f_L1_006: sym_L1_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) nightstand, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_305 | symbol_type_disagreement | f_L1_009 | f_L1_009: sym_L1_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | typed bathtub by code (ai_member): bathtub: r_L1_banyo misses it (r_L1_banyo.bathroom_set (anchor f_L1_022) misses shower\|bathtub) and the AI passes named it (pass 1 (qwen)'s reason names bathtub); the drawn 2.42 x 0.98 m is outside the bathtub's range: the nearest real prod; inferred, listed in the report |
| c_306 | symbol_type_disagreement | f_L1_011 | f_L1_011: sym_L1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) stair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_307 | symbol_type_disagreement | f_L1_012 | f_L1_012: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) stair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_308 | symbol_type_disagreement | f_L1_017 | f_L1_017: sym_L1_014: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) dresser, pass 2 (zai-org/GLM-4.6V-Flash) desk | typed dresser by code (name_text): dresser: the documents name it: the text '*SIFONIYER' (TEXT:29ABD3) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.55 m within 40%; inferred, listed in the report |
| c_309 | symbol_type_disagreement | f_L1_020 | f_L1_020: sym_L1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_310 | symbol_type_disagreement | f_L1_027 | f_L1_027: sym_L1_024: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) washbasin | typed washbasin by code (ai_member): washbasin: r_L1_dus misses it (r_L1_dus.bathroom_set (anchor f_L1_018) misses washbasin) and the AI passes named it (pass 2 (glm) answered washbasin; pass 2 (glm)'s reason names washbasin); plan crop recognition/crops/sym_L1_024_ctx.png; inferred, listed in the report |
| c_311 | other | r_L0_salon | r_L0_salon: one face holds the room names 'Salon' and 'YEMEK BÖLÜMÜ' | unresolved: first label kept, room unverified |
| c_312 | other | r_L0_mutfak | r_L0_mutfak: one face holds the room names 'Mutfak' and 'ANTRE m²' | unresolved: first label kept, room unverified |
| c_313 | symbol_front_disagreement | f_L0_006 | f_L0_006: sym_L0_001: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_314 | symbol_front_disagreement | f_L0_014 | f_L0_014: sym_L0_009: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_315 | symbol_front_disagreement | f_L0_024 | f_L0_024: sym_L0_019: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_316 | symbol_front_disagreement | f_L0_025 | f_L0_025: sym_L0_020: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_317 | symbol_front_disagreement | f_L1_005 | f_L1_005: sym_L1_002: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_318 | symbol_front_disagreement | f_L1_008 | f_L1_008: sym_L1_005: AI front [0.0, 90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_319 | symbol_front_disagreement | f_L1_017 | f_L1_017: sym_L1_014: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_320 | symbol_front_disagreement | f_L1_021 | f_L1_021: sym_L1_018: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_321 | symbol_front_disagreement | f_L1_022 | f_L1_022: sym_L1_019: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_322 | registration_residual | r4, r3 | sheets.json sc_001: real06.dwg r4 (L1) registered onto r3 (L0) with an RMS outline distance of 0.130 m (826 of 1016 outline points within 5 cm; outlines 14.17 x 20.70 m vs 14.47 x 20.70 m) | unresolved: each level is built as drawn |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 9 regions (use: exterior 5, heights 2, read 2). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r2 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r3 | real06.dwg | floor_plan | geometry (0.70) | verified | L0 (assumed) | base | read |
| r4 | real06.dwg | floor_plan | geometry (0.70) | verified | L1 (assumed) | base | read |
| r5 | real06.dwg | section | geometry (0.85) | verified | - | - | heights |
| r6 | real06.dwg | roof_plan | geometry (0.60) | verified | - | - | exterior |
| r7 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r8 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r9 | real06.dwg | section | geometry (0.85) | verified | - | - | heights |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L0 | Ground floor | floor | r3 | - |
| L1 | Level 1 | floor | r4 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L0, L1 | r3, r4 |

Section regions (heights): r5.

Strays (entities far from every drawing, ignored): 0.

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| real06.dwg | dwg | 50.00 | unit_check | area_labels None 0.00 (3); level_marks m 1:50 0.98 (164); door_widths m 1:50 1.00 (10); wall_thickness None 0.00 (2468); text_height m 1:50 1.00 (803); dimensions None - (0); dimension_texts None - (565) | - |

Conflicts:

| id | kind | description | resolution |
|---|---|---|---|
| sc_001 | registration_residual | real06.dwg r4 (L1) registered onto r3 (L0) with an RMS outline distance of 0.130 m (826 of 1016 outline points within 5 cm; outlines 14.17 x 20.70 m vs 14.47 x 20.70 m) | unresolved: each level is built as drawn |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/real06_dwg_s1.jpg](debug/real06_dwg_s1.jpg)

Sheet warnings:

- real06.dwg: $INSUNITS 0 names no unit; the drawing is scaled: drawn in m at 1:50 (50 m per unit), inferred from 3 agreeing checks (level_marks 98%, door_widths 100%, text_height 100%); no plain unit fits
- real06.dwg r1: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r2: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r7: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r8: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r3: plan without a level title: level L0 'Ground floor' inferred from its floor mark +0.50 m (2 untitled plans ordered by their floor marks)
- real06.dwg r4: plan without a level title: level L1 'Level 1' inferred from its floor mark +3.50 m (2 untitled plans ordered by their floor marks)
- registration: r3 (L0): stairs drawn on this level only
- registration: r4 (L1): stairs drawn on the level next to it only
- 2 sections: heights from r5; r9 not read for heights
- section r5: 16.32 m wide, no outline extent fits; the cut line on r3 gives the axis y
- roof: the roof plan r6 gives a hip roof at 33 %; the section's profile reads as gambrel (its outline also draws trusses and trims): the roof plan wins
- elevation r1: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r2: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r7: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r8: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L0 | Ground floor | floor | 0,00 m (section) | 2,85 m (section) | base | r3 |
| L1 | Level 1 | floor | 3,00 m (section) | 2,85 m (section) | base | r4 |

Variants:

| variant | label | levels | rooms changed | outside changed |
|---|---|---|---|---|
| base | Base | L0, L1 | 0 | no |

Heights (drawn = read from a document; assumed = a default, listed again under Assumed values):

| item | value | state | from | note |
|---|---|---|---|---|
| L0 ceiling height | 2,85 m | drawn | section | - |
| L0 floor level | 0,00 m | drawn | section | - |
| L0 floor to floor | 3,00 m | drawn | vector | - |
| L1 ceiling height | 2,85 m | drawn | section | - |
| L1 floor level | 3,00 m | drawn | section | - |
| L1 floor to floor | 3,00 m | drawn | vector | - |
| sl_L0 thickness | 0,15 m | drawn | section | - |
| sl_L1 thickness | 0,15 m | drawn | section | - |
| roof eaves height | 6,00 m | drawn | vector | 3.00 m above the top floor |
| roof ridge height | 7,77 m | drawn | vector | 4.77 m above the top floor |
| roof overhang | 0,47 m | drawn | vector | left 0.50 m, right 0.48 m |
| roof knee wall | 3,00 m | drawn | vector | the roof's top surface at the outer face of the outer wall above the top floor (a cross-check) |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L0 | L0 | 0,00 m | 0,15 m | section | 0 | all | verified |
| sl_L1 | L1 | 3,00 m | 0,15 m | section | 1 | all | verified |

Roof:

- type hip (roof_plan)
- over level L1
- eaves 6,00 m (drawn)
- ridge 7,77 m (drawn)
- overhang 0,47 m (drawn)
- knee wall 3,00 m (drawn)
- pitch 18.3 deg (drawn)
- 0 planes, 0 opening(s)
- covering not drawn (outside look: see Exterior views)

Assumed for the roof: outline (the outer walls + overhang).

Facade:

| elevation | title | side | windows | doors | plan check |
|---|---|---|---|---|---|
| r1 | - | all | 0 | 0 | - |
| r2 | - | all | 0 | 0 | - |
| r7 | - | all | 0 | 0 | - |
| r8 | - | all | 0 | 0 | - |

Site:

- plot not drawn
- 0 paving area(s), 0 grass, 0 parking built
- 0 boundary wall(s), 35 decor item(s) built
- 2 labelled area(s), 2 recorded only (label, not built)
- ground levels: right -0,50 m (drawn)
- terrain flat, 0 light well(s)

Levels and ground (Milestone 12):

- 7 level mark(s) read (floor 2, ground_finished 1, slab_top 2, threshold 2); 2 mark symbol(s) taken out of the furniture
- datum ±0.00 = 0.50 m (drawn)
- ground from: marks; terrain flat
- plinth top 0,00 m (inferred)

| Door | Threshold | Ground | Rise | Solution | Main |
|---|---|---|---|---|---|
| d_L0_001 | 0,00 m | -0,50 m | 0,50 m | steps (4 x 0.125 m) |  |
| d_L0_003 | 0,00 m | -0,50 m | 0,50 m | steps (4 x 0.125 m) |  |
| d_L0_004 | 0,00 m | -0,50 m | 0,50 m | none | yes |
| d_L0_006 | 0,00 m | -0,50 m | 0,50 m | none |  |
| d_L1_001 | 3,00 m | -0,50 m | 3,50 m | none - door into the air (L2) |  |
| d_L1_004 | 3,00 m | -0,50 m | 3,50 m | none - door into the air (L2) |  |
| d_L1_005 | 3,00 m | -0,50 m | 3,50 m | none - door into the air (L2) |  |
| d_L1_007 | 3,00 m | -0,50 m | 3,50 m | none |  |
| d_L1_011 | 3,00 m | -0,50 m | 3,50 m | none |  |

Inferred (listed, CLAUDE.md evidence rules):

- outdoor space os_L0_veranda: veranda 'VERANDA' on L0: 22.84 m² (stated 22.80 m²), strokes; floor +0.00 m (the level mark(s) +0,50 inside it); doors d_L0_004, d_L0_006 open onto it (it is their landing); its edge and steps down to the ground -0.50 m (the drawn steps); light roof over 11.21 m², top +3.00 m; 3 post(s) (2 drawn column(s)) (inferred)
- outdoor space os_L1_balkon: balcony 'BALKON' on L1: 11.60 m² (stated 11.80 m²), strokes; floor +3.00 m (the level mark(s) +3,50 inside it); doors d_L1_007, d_L1_011 open onto it (it is their landing); a slab with a guard on its open edges (inferred)
- site symbols: axis_bubble: 28 drawn site symbol(s) typed axis_bubble (a structural grid bubble (the axis label), drawing annotation; not built): sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006, sd_L0_007, sd_L0_008 ...
- site symbols: column: 2 drawn site symbol(s) typed column (a column; built with os_L0_veranda): sd_L0_009, sd_L0_010
- site symbols: door_symbol: 1 drawn site symbol(s) typed door_symbol (a door symbol; not built): sd_L0_013
- site symbols: hatch: 1 drawn site symbol(s) typed hatch (a hatch; not built): sd_L0_015
- site symbols: level_mark: 2 drawn site symbol(s) typed level_mark (a level mark symbol; not built): sd_L0_014, sd_L0_021
- site symbols: outdoor_space_detail: 1 drawn site symbol(s) typed outdoor_space_detail (a detail of an outdoor space (its edge or steps); built with os_L0_veranda): sd_L0_016
- entrance d_L0_001: 0.50 m above the ground (terrain (flat)): a landing and 4 riser(s) of 0.125 m, tread 0.33 m (inferred)
- entrance d_L0_003: 0.50 m above the ground (terrain (flat)): a landing and 4 riser(s) of 0.125 m, tread 0.33 m (inferred)
- site.plinth: no SB. mark: the plinth up to the ground floor

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 14 piece(s) added, 2 wall cabinet run(s).

### Salon (r_L0_salon, living): completed

- added f_L0_033: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L0_034: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L0_035: potted_plant 0.35 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_009, f_L0_011, f_L0_012, f_L0_013, f_L0_014, f_L0_016, f_L0_027, f_L0_028, f_L0_029, f_L0_030

### Mutfak (r_L0_mutfak, kitchen): completed

- added f_L0_036: stove 0.60 x 0.60 (confidence -, rule)
- added f_L0_037: table_dining 0.80 x 0.70 (confidence -, rule)
- added f_L0_038: chair 0.45 x 0.45 (confidence -, rule)
- added f_L0_039: chair 0.45 x 0.45 (confidence -, rule)
- added f_L0_040: fridge 0.60 x 0.60 (confidence -, rule)
- 2 wall cabinet run(s) over the drawn counter
- not placed island: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001, f_L0_002, f_L0_003, f_L0_004, f_L0_031, f_L0_032

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_024, f_L0_026

### Ebeveyn Y.odası (r_L1_ebeveyn_y_odasi, bedroom): completed

- added f_L1_029: desk 1.00 x 0.50 (confidence -, rule)
- added f_L1_030: office_chair 0.60 x 0.60 (confidence -, rule)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_016

### Çocuk Odası (r_L1_cocuk_odasi, bedroom): completed

- added f_L1_031: wardrobe 1.20 x 0.60 (confidence -, rule)
- added f_L1_032: desk 1.00 x 0.50 (confidence -, rule)
- added f_L1_033: office_chair 0.60 x 0.60 (confidence -, rule)
- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_004, f_L1_005, f_L1_006, f_L1_007, f_L1_008

### Soyunma Odası (r_L1_soyunma_odasi, other): completed (nothing fits: dressing: no place passes the checks)

- not placed dressing: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_011, f_L1_012

### Hol (r_L1_hol, hall): completed

- added f_L1_034: shoe_cabinet 1.00 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_003

### Duş (r_L1_dus, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_018, f_L1_021, f_L1_027

### Oda (r_L1_oda_2, bedroom): completed (nothing to add)

- not placed sleeping_single: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_013, f_L1_014, f_L1_017, f_L1_025

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_019, f_L1_022, f_L1_023

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 56 of 56 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 52 ok, 4 failed; 20 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L0_029 | chair (chair) | 0.07 | 0.00 | - | - |
| f_L0_030 | chair (chair) | 0.08 | 0.00 | - | - |
| f_L1_005 | dresser (dresser) | 0.20 | 0.00 | - | - |
| f_L1_014 | wardrobe (wardrobe) | 0.39 | 0.00 | yes | - |

Locked-rule violations:

- openings: must stay as drawn (byte-equal): changed d_L0_002, d_L0_003, d_L0_004, d_L0_006, d_L1_004, d_L1_007, d_L1_010, d_L1_011, o_L0_001, o_L0_003, o_L0_007, o_L1_002, o_L1_003, o_L1_005, o_L1_006, o_L1_007, win_L0_001, win_L0_006, win_L0_007, win_L1_001, win_L1_003, win_L1_004, win_L1_005, win_L1_008; removed o_L1_001
- rooms: must stay as drawn (byte-equal): changed r_L1_soyunma_odasi
- f_L0_002: fixed equipment removed
- f_L1_014: moved 0.389 m by the agent (> 0.3 m)

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered.

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)

Gate for the exterior polish: **polish_disabled** (exterior views stay the Cycles render): negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | front, right | - | cycles (gate_validation) | ok | front: unverified; right: unverified | no |
| ext_2 | corner | back, right | - | cycles (gate_validation) | ok | back: unverified; right: unverified | no |
| ext_3 | corner | back, left | - | cycles (gate_validation) | partial | back: unverified | no |
| ext_4 | corner | front, left | - | cycles (gate_validation) | partial | front: unverified; left: unverified | no |
| ext_5 | aerial | back, left | - | cycles (gate_validation) | ok | back: unverified | no |
| ext_6 | frontal | front | - | cycles (gate_validation) | partial | front: unverified | no |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | white | fallback | yes | facade scheme (scandinavian): render in white (no drawing, brief or style names the facade) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | painted_metal_white | - | fallback | yes | style profile exterior.window_frame (assumed) |
| door | wood_oak_light | - | agent | no | agent override (docs/milestone11.md §17.3) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | agent | no | agent override (docs/milestone11.md §17.3) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | white | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: building.json facade.elevations. 4 facade(s): 0 ok, 0 mismatch, 4 not checked; roof mismatch.

| elevation | side | drawn win/door | built win/door | result | notes |
|---|---|---|---|---|---|
| r1 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r2 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r7 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r8 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |

Roof heights: built eaves 6,00 m, ridge 7,61 m; drawn eaves 6,00 m (vector), ridge 7,77 m (vector); result mismatch.

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| real06.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 8, group_member 8, inferred 9, level 1, name_text 3, none 8, rule 15, same_block 3, zone_label 1. Recognition questions: 41; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_006 | r_L0_salon | sofa | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.85; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 1.00 |
| f_L0_009 | r_L0_salon | unknown | no | unverified | no (drawn inside sofa f_L0_006 (2.12 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.80 |
| f_L0_010 | r_L0_banyo | bathtub | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L0_012 | r_L0_salon | unknown | no | unverified | no (drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.80 |
| f_L0_013 | r_L0_salon | unknown | no | unverified | no (drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.80 |
| f_L0_014 | r_L0_salon | sofa | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_dining 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_015 | r_L0_salon | table_coffee | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: bookshelf, front right 0.90 |
| f_L0_019 | r_L0_salon | armchair | no (typed by same_block) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.85; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L0_021 | r_L0_salon | table_coffee | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_024 | r_L0_banyo | toilet | no (typed by level) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: toilet, front right 1.00 |
| f_L0_026 | r_L0_banyo | washbasin | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front bottom 0.90 |
| f_L0_027 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L0_028 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front bottom 0.90 |
| f_L0_029 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L0_030 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L1_004 | r_L1_cocuk_odasi | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front top 0.90 |
| f_L1_005 | r_L1_cocuk_odasi | dresser | no (typed by name_text) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: dresser, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: desk, front left 0.90 |
| f_L1_006 | r_L1_cocuk_odasi | unknown | no | unverified | no (drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_007 | r_L1_cocuk_odasi | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 0.90 |
| f_L1_008 | r_L1_cocuk_odasi | nightstand | yes | verified | no (architect F5: it cut f_L1_007 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: nightstand, front right 0.90 |
| f_L1_009 | r_L1_banyo | bathtub | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_011 | r_L1_soyunma_odasi | wardrobe | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front left 0.85; pass 2 zai-org/GLM-4.6V-Flash: stair, front right 0.90 |
| f_L1_012 | r_L1_soyunma_odasi | wardrobe | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.85; pass 2 zai-org/GLM-4.6V-Flash: stair, front left 0.90 |
| f_L1_017 | r_L1_oda_2 | dresser | no (typed by name_text) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: dresser, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: desk, front left 0.80 |
| f_L1_018 | r_L1_dus | shower | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: shower, front right 1.00 |
| f_L1_019 | r_L1_banyo | washing_machine | no (typed by name_text) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin 0.90 |
| f_L1_020 | r_L1_ebeveyn_y_odasi | floor_lamp | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.90 |
| f_L1_021 | r_L1_dus | toilet | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: toilet, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: toilet, front top 1.00 |
| f_L1_022 | r_L1_banyo | toilet | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: toilet, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: toilet, front right 1.00 |
| f_L1_023 | r_L1_banyo | washbasin | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front bottom 0.90 |
| f_L1_027 | r_L1_dus | washbasin | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front right 0.90 |

## Site

The plot, paving, grass, parking and boundary walls marked built are built in the 3D scene and show in the exterior views; an area that is only a label (not built) is recorded, not built.

| id | what | detail |
|---|---|---|
| sa_L0_veranda | area 'VERANDA' (other) | label size -, measured - (-), built as the outdoor space os_L0_veranda (inferred) |
| sa_L1_balkon | area 'BALKON' (other) | label size -, measured - (-), built as the outdoor space os_L1_balkon (inferred) |
| - | decor | other x 35 |

## Separators

None.

## Assumed values

- style: default text "Scandinavian, light oak floor, white walls, linen textiles, warm daylight" (no style in brief.yaml; wenart/defaults.yaml)
- style exterior facade render in white, roof concrete_tiles in anthracite, window_frame as inside (painted_metal_white), door as inside (wood_oak_light), paving paving in grey, garden grass from style.exterior_fallback of wenart/defaults.yaml (no word for them in the brief)
- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
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
- brief library.licence_mode: relaxed (default, not in brief.yaml)
- L0: level 'Ground floor' assumed (no level title on the page)
- L1: level 'Level 1' assumed (no level title on the page)
- front kept from the drawing although both AI passes answered 'none': 2 piece(s) (f_L0_026, f_L1_023)
- door height 2,10 m: 16 opening(s) (d_L0_003, d_L0_004, d_L0_005, d_L0_006, d_L0_007, d_L1_002 ...)
- door sill height -: 4 opening(s) (win_L1_003, win_L1_004, win_L1_005, win_L1_008)
- opening height 2,10 m: 1 opening(s) (o_L1_002)
- window height 1,15 m: 2 opening(s) (o_L0_001, d_L0_002)
- window height 1,20 m: 30 opening(s) (d_L0_001, win_L0_001, o_L0_002, o_L0_003, o_L0_004, o_L0_005 ...)
- window sill height 0,90 m: 14 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- f_L0_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- roof: outline (the outer walls + overhang) assumed
- roof covering: not drawn (the outside look decides, see below)
- outside look facade: render in white (fallback: facade scheme (scandinavian): render in white (no drawing, brief or style names the facade))
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
- outside look window_frame: painted_metal_white (fallback: style profile exterior.window_frame (assumed))
- outside look paving: paving in grey (fallback: style profile exterior.paving (assumed))
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))
- outside look plot_wall: render in white (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L1_oda: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_oda |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (-y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 2 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L1_010, dress_f_L1_013 |
| boundary | 1 | no site plan: a low hedge on the inferred plot boundary (inferred) | site |
| cabinet_fronts | 2 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_041, furn_f_L0_042 |
| climate | 1 | the drawing's language (room and site labels) (inferred; the species of trees and hedges follow it): banyo, hol, mutfak, oda, salon | site |
| context | 1 | no context drawn: 137 trees of the mediterranean climate (stone_pine 52, olive 37, plane 25, cypress 23; species inferred) in groups around the site, 54-350 m from the building's centre (the exterior cameras stand within 54 m), with open fields between them so the horizon stays in view (inferred context) | site |
| cut_through | 1 | the wall overlaps w_L0_009 at its opening o_L0_001: cut through both (a facade line drawn over a thicker wall) | w_L0_010 |
| cut_through | 1 | the wall overlaps w_L0_019 at its opening win_L0_007: cut through both (a facade line drawn over a thicker wall) | w_L0_017 |
| cut_through | 1 | the wall overlaps w_L0_029 at its opening win_L0_006: cut through both (a facade line drawn over a thicker wall) | w_L0_028 |
| direction | 1 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L0_001 |
| door_handles | 11 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_005_handle, d_L0_007_handle, d_L1_002_handle |
| fabric | 2 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture |
| facade | 1 | facade scheme (scandinavian): render in white (no drawing, brief or style names the facade) | exterior |
| facade_scheme | 1 | facade scheme (scandinavian): wood_cladding framing the main entrance d_L0_004 (1.9 m wide; not drawn) | w_L0_029 |
| fascia_material | 1 | pitched roof: the eaves and verge edges are a fascia board in the gutter's aluminium_anthracite (not drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet) | roof |
| ground:+y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-x | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| handrail | 1 | design detail on every flight side not against a wall; not in the documents | furn_f_L0_001 |
| hedge | 7 | no site plan: a low hedge on the inferred plot boundary (inferred) | boundary_hedge_01, boundary_hedge_02, boundary_hedge_03 |
| height | 16 | door height listed as assumed in the building JSON | d_L0_003, d_L0_004, d_L0_005 |
| height | 9 | no height in the JSON; type height for armchair | furn_f_L0_007, furn_f_L0_008, furn_f_L0_016 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L1_004, furn_f_L1_007 |
| height | 4 | no height in the JSON; type height for chair | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 1 | no height in the JSON; type height for floor_lamp | furn_f_L1_020 |
| height | 2 | no height in the JSON; type height for kitchen_counter | furn_f_L0_031, furn_f_L0_032 |
| height | 1 | no height in the JSON; type height for shower | furn_f_L1_018 |
| height | 2 | no height in the JSON; type height for sofa | furn_f_L0_014, furn_f_L0_043 |
| height | 2 | no height in the JSON; type height for table_coffee | furn_f_L0_021, furn_f_L0_044 |
| height | 2 | no height in the JSON; type height for toilet | furn_f_L1_021, furn_f_L1_022 |
| height | 2 | no height in the JSON; type height for washbasin | furn_f_L0_026, furn_f_L1_023 |
| height | 1 | no height in the JSON; type height for washing_machine | furn_f_L1_019 |
| height | 1 | opening height listed as assumed in the building JSON | o_L1_002 |
| height | 32 | window height listed as assumed in the building JSON | d_L0_001, o_L0_001, d_L0_002 |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:guard_glass | 1 | glass guard in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:railing | 1 | glass guard's channel and cap rail in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| left_out:door | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the scandinavian look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the scandinavian look | openings |
| left_out:entrance | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the scandinavian look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the scandinavian look | openings |
| left_out:glazed_door | 1 | models out of the style's look: 3dwh_2e37507915a83b263b0434e8: glass 8% of its face (< 45%); 3dwh_5b8d6e9c0eff7893f9fe2795: patterned glass (an image on its glass): the scandinavian look wants clear glass; 3dwh_5e2175bedf4e725cd2760f52: glazing bars (16 lites, 4.1 per m2): the scandinavian look wants no or few bars; 3dwh_73ccc78df8b9b5ec4219d9b8: no see-through glass; 3dwh_7f96e3f969b6e73f397ec14c: audited styles ['classic', 'modern']: mostly classic, not the scandinavian look; 3dwh_a5392fea8c223c7b149f9f68: audited styles ['classic', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_bbf790ecbd3bd2698a6f094a: glass 6% of its face (< 45%); 3dwh_c1e3fe2b7d627b3c019dac27: glass 16% of its face (< 45%) | openings |
| left_out:window | 1 | models out of the style's look: 3dwh_008fc2b4ab59c1a67589cb97: no see-through glass; 3dwh_2a2ec61614b5278cf6fe1011: no see-through glass; 3dwh_48bec799740fad36241c99d9: no see-through glass; 3dwh_4a7dc5974d3b797601e64e12: audited styles ['classic', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_56f518dddfda5b3c284ddf47: no see-through glass; 3dwh_5c21a04d22581a3786ae9bef: no see-through glass; 3dwh_5faa67969eb7104b4adee381: its title says 'traditional': not the scandinavian look; 3dwh_664d1626592cdaebecbdb5cb: no see-through glass | openings |
| level | 1 | terrace os_L0_veranda: one level at +0.00 m (the level mark(s) +0,50 inside it); ground -0.50..-0.50 m under it; edge: steps (inferred); the labelled veranda 'VERANDA' of L0, the landing of d_L0_004, d_L0_006; the drawn steps on edge 7; edges 0, 1, 2, 3, 4, 5, 14 face the building (its walls retain there: no wall, band or steps) | platform_os_L0_veranda |
| level | 1 | terrace os_L1_balkon: one level at +3.00 m (the level mark(s) +3,50 inside it); ground -0.50..-0.50 m under it; edge: none (inferred); the labelled balcony 'BALKON' of L1, the landing of d_L1_007, d_L1_011; elevated: a slab with a guard on its open edges | platform_os_L1_balkon |
| library_model | 2 | library door 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 15 %; the documents draw the opening, not its product); the building's one door family; scandinavian look: audited styles ['modern'] suit the scandinavian look; frames in the style's finish | d_L0_003, d_L1_007 |
| library_model | 1 | library entrance 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 15 %; the documents draw the opening, not its product); the building's one entrance family; scandinavian look: audited styles ['modern'] suit the scandinavian look; frames in the style's finish | d_L0_004 |
| library_model | 1 | library glazed door 3dwh_75228caa20a20065078e6c23 ('Valdi - Folding Sliding Door - 4 Door Ti') in 1 panel(s) of 2.95 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one glazed door family; scandinavian look: audited styles ['industrial', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L0_006 |
| library_model | 1 | library glazed door 3dwh_963661fa9b8487c9c0440cf1 ('Valdi - Folding Sliding Door - 3 Door Ti') in 1 panel(s) of 1.98 x 2.10 m (proportions off by 18 %; the documents draw the opening, not its product); the building's one glazed door family; scandinavian look: audited styles ['industrial', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L1_011 |
| library_model | 2 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.68 x 1.20 m (proportions off by 7 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_003, win_L1_006 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.70 x 1.20 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_005 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.72 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_002 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.75 x 1.20 m (proportions off by 4 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_010 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.77 x 1.20 m (proportions off by 8 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_007 |
| library_model | 2 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.80 x 1.20 m (proportions off by 11 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L1_004, d_L1_010 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.57 x 1.20 m (proportions off by 25 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L1_004 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.60 x 1.20 m (proportions off by 20 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_009 |
| library_model | 3 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.72 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_004, o_L1_005, win_L1_011 |
| library_model | 5 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.78 x 1.20 m (proportions off by 8 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_005, o_L0_006, d_L1_005 |
| library_model | 2 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.79 x 1.20 m (proportions off by 9 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_004, win_L1_007 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.85 x 1.20 m (proportions off by 18 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_002 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 3 panel(s) of 0.62 x 1.20 m (proportions off by 17 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_007 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 3 panel(s) of 0.65 x 1.20 m (proportions off by 11 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L1_003 |
| library_model | 3 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 3 panel(s) of 0.72 x 1.20 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L0_001, o_L0_003, d_L1_001 |
| modules | 2 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L0_031, furn_f_L0_032 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| opening_model | 1 | no model of the building's window family 'Single Casement Window' fits 0.95 x 1.20 m: the parametric opening in the style's finish keeps one door and window language | win_L1_001 |
| opening_model | 2 | no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language | o_L0_002, win_L0_006 |
| outline | 1 | no roof outline drawn: the walls' outline (wall_union) grown by the overhang 0.47 m; 20 facade jog(s) shallower than 0.60 m closed under the eaves (one eaves line per facade) | roof |
| outline_rectangle | 1 | the 8-point outline is not a rectangle: the hip planes are derived on its smallest enclosing rectangle and cut to the outline | roof |
| path:d_L0_001 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path:d_L0_003 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path:d_L0_004,d_L0_006 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| platform:os_L0_veranda | 1 | terrace os_L0_veranda: one level at +0.00 m (the level mark(s) +0,50 inside it); ground -0.50..-0.50 m under it; edge: steps (inferred); the labelled veranda 'VERANDA' of L0, the landing of d_L0_004, d_L0_006; the drawn steps on edge 7; edges 0, 1, 2, 3, 4, 5, 14 face the building (its walls retain there: no wall, band or steps) | site |
| platform:os_L1_balkon | 1 | terrace os_L1_balkon: one level at +3.00 m (the level mark(s) +3,50 inside it); ground -0.50..-0.50 m under it; edge: none (inferred); the labelled balcony 'BALKON' of L1, the landing of d_L1_007, d_L1_011; elevated: a slab with a guard on its open edges | site |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: stone_wall_ledgestone (style family scandinavian; not drawn) | facade |
| plot | 1 | no site plan: the plot is the outline's rectangle + 6 m (inferred) | site |
| ridge_caps | 1 | ridge and hip caps along the roof's ridges and hips (not drawn; a tiled roof has them) | roof_ridges |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L1_004 (no nightstand, no lamp): the wall sconce would cover the window d_L1_005 | rig_r_L1_cocuk_odasi |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L1_004 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L1_cocuk_odasi |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L1_010 (the top of the nightstand f_L1_026 is taken by the plant_small dec_L1_007): the wall sconce would cover the window win_L1_010 | rig_r_L1_ebeveyn_y_odasi |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L1_013 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L1_oda_2 |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_014; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_mutfak: LED strip under the wall cabinet f_L0_041 over the counter f_L0_002; 400.0 lm -> 1.05 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L0_mutfak_strip_1_light |
| rig_light | 1 | r_L0_mutfak: LED strip under the wall cabinet f_L0_042 over the counter f_L0_031; 245.0 lm -> 0.6431 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L0_mutfak_strip_2_light |
| rig_light | 1 | r_L0_mutfak: ceiling fixture at the pole of inaccessibility of r_L0_mutfak; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_mutfak_ceiling_3_light |
| rig_light | 1 | r_L0_oda: ceiling fixture at the pole of inaccessibility of r_L0_oda, 1 x 1100 lm bulbs for 450 lm/m2 over 2.1 m2 and 1 fixture(s); 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_oda_ceiling_1_light |
| rig_light | 1 | r_L0_salon: pendant light over the dining table f_L0_011 under the decor pendant dec_L0_004; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_salon_pendant_1_light |
| rig_light | 1 | r_L1_banyo: ceiling fixture at the pole of inaccessibility of r_L1_banyo; its light under the decor ceiling light dec_L1_035; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_banyo_ceiling_2_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_023; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_dus: ceiling fixture at the pole of inaccessibility of r_L1_dus; its light under the decor ceiling light dec_L1_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_dus_ceiling_2_light |
| rig_light | 1 | r_L1_dus: mirror light over the washbasin f_L1_027; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_dus_mirror_1_light |
| rig_light | 1 | r_L1_ebeveyn_y_odasi: bedside light in the shade of the table lamp dec_L1_006 on f_L1_024 beside the bed f_L1_010; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L1_ebeveyn_y_odasi_bedside_1_light |
| rig_light | 1 | r_L1_hol: ceiling fixture at the pole of inaccessibility of r_L1_hol, 5 x 1100 lm bulbs for 450 lm/m2 over 11.0 m2 and 1 fixture(s); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_hol_ceiling_1_light |
| rig_light | 1 | r_L1_oda: ceiling fixture at the pole of inaccessibility of r_L1_oda, 2 x 1100 lm bulbs for 450 lm/m2 over 3.1 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_022; 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_oda_ceiling_1_light |
| rig_light | 1 | r_L1_oda_2: bedside light in the shade of the table lamp dec_L1_034 on f_L1_025 beside the bed f_L1_013; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L1_oda_2_bedside_1_light |
| rig_light | 1 | r_L1_soyunma_odasi: ceiling fixture at the pole of inaccessibility of r_L1_soyunma_odasi, 3 x 1100 lm bulbs for 450 lm/m2 over 5.9 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_024; 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_soyunma_odasi_ceiling_1_light |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L0_001 |
| roof | 1 | listed as assumed in the building JSON | roof |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 1 | outside sill 0.7357 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_006_sill |
| sill | 1 | outside sill 0.7359 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_003_sill |
| sill | 1 | outside sill 0.76 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_005_sill |
| sill | 1 | outside sill 0.7841 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill |
| sill | 1 | outside sill 0.81 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_010_sill |
| sill | 1 | outside sill 0.8348 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_007_sill |
| sill | 2 | outside sill 0.86 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | d_L1_004_sill, d_L1_010_sill |
| sill | 1 | outside sill 1.01 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_001_sill |
| sill | 2 | outside sill 1.16 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_002_sill, win_L0_006_sill |
| sill | 1 | outside sill 1.21 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L1_004_sill |
| sill | 1 | outside sill 1.26 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_009_sill |
| sill | 3 | outside sill 1.51 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_004_sill, o_L1_005_sill, win_L1_011_sill |
| sill | 5 | outside sill 1.61 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_005_sill, o_L0_006_sill, d_L1_005_sill |
| sill | 2 | outside sill 1.635 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_004_sill, win_L1_007_sill |
| sill | 1 | outside sill 1.76 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_002_sill |
| sill | 1 | outside sill 1.91 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_007_sill |
| sill | 1 | outside sill 2.01 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L1_003_sill |
| sill | 3 | outside sill 2.21 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | d_L0_001_sill, o_L0_003_sill, d_L1_001_sill |
| sill_height | 14 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 9 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_salon, skirting_r_L0_mutfak, skirting_r_L0_oda |
| slab_band | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L0_031, f_L0_036 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L0_007 | splashback_r_L0_mutfak |
| splashback_cut | 1 | the splashback behind f_L0_020 is cut at the opening(s) o_L0_004 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L0_mutfak |
| splashback_cut | 1 | the splashback behind f_L0_031 is cut at the opening(s) win_L0_007 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L0_mutfak |
| splashback_cut | 1 | the splashback behind f_L0_032 is cut at the opening(s) o_L0_001, d_L0_002 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L0_mutfak |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_001 |
| steps:d_L0_001 | 1 | entrance door 0.50 m above the ground: a landing and 3 steps of 0.125 m (inferred) | site |
| steps:d_L0_003 | 1 | entrance door 0.50 m above the ground: a landing and 3 steps of 0.125 m (inferred) | site |
| thickness | 1 | roof thickness not drawn | roof |
| top_apron | 1 | the floor's drawn opening goes on 0.30 m past the top step: an apron in the tread finish meets the floor's edge (not drawn: assumed) | furn_f_L0_001 |
| tree | 8 | medium tree: crown 5.0 m as drawn, 8.0 m tall (height by the crown class, assumed); species stone_pine (inferred) | tree_tree_inferred_3, tree_tree_inferred_4, tree_tree_inferred_5 |
| tree | 2 | small tree: crown 3.5 m as drawn, 5.6 m tall (height by the crown class, assumed); species olive (inferred) | tree_tree_inferred_1, tree_tree_inferred_2 |
| tree:tree_inferred_1 | 1 | no site plan: a tree that frames the windows' view (seen from 5 window(s) (d_L1_005, o_L0_003, o_L0_004, o_L1_005, ...), 5.9 m from the nearest); its crown keeps 2.5 m clear of every window and off their straight view within 6 m; the strict pass placed 0 of 10 (inferred, docs/milestone11.md §1.1 E11; 26 Oct 2026) | site |
| tree:tree_inferred_10 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 7 window(s) (d_L1_004, o_L0_002, o_L0_007, o_L1_004, ...), 16.6 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_2 | 1 | no site plan: a tree that frames the windows' view (seen from 4 window(s) (d_L1_010, o_L0_007, win_L1_001, win_L1_011), 6.0 m from the nearest); its crown keeps 2.5 m clear of every window and off their straight view within 6 m; the strict pass placed 0 of 10 (inferred, docs/milestone11.md §1.1 E11; 26 Oct 2026) | site |
| tree:tree_inferred_3 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 10 window(s) (d_L1_004, o_L0_002, o_L1_003, o_L1_004, ...), 9.1 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_4 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 8 window(s) (d_L1_010, o_L0_005, o_L0_006, o_L0_007, ...), 9.3 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_5 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 6 window(s) (d_L1_005, o_L0_003, o_L0_004, o_L1_005, ...), 11.3 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_6 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 10 window(s) (d_L1_004, o_L0_002, o_L1_003, o_L1_004, ...), 9.3 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_7 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 8 window(s) (d_L1_010, o_L0_005, o_L0_006, o_L0_007, ...), 9.3 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_8 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 8 window(s) (d_L1_010, o_L0_005, o_L0_006, o_L0_007, ...), 12.2 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_9 | 1 | the plot leaves no room for 10 trees: a neighbour's tree just beyond the plot edge (seen from 8 window(s) (o_L0_004, o_L1_003, o_L1_005, win_L0_002, ...), 16.8 m from the nearest; inferred context, 26 Oct 2026) | site |
| trees | 1 | inferred trees: placed 10 of 10 (74 candidates; removed by building 1, path 15, sightline 36, window 66, front 27; most by window; the framing pass (the window rule near the facade only) placed 2 of 500 candidates (removed by building 314, path 83, sightline 200, window 347, front 140); the beyond-plot pass (a neighbour's garden) placed 8 of 252 candidates (removed by path 32, sightline 124, front 104); seen from 24 of 29 windows) | site |
| turn | 1 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L0_001 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass posts balustrade on its 2 free edge(s), 3.31 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| waist | 1 | the documents show the stair in plan only | furn_f_L0_001 |
| winders | 1 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L0_001 |
| window_frame | 1 | style profile exterior.window_frame (assumed) | exterior |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L0_mutfak | cam_r_L0_mutfak_3 | cam_r_L0_mutfak_1 (vision_check), cam_r_L0_mutfak_2 (vision_check) | ok |
| r_L0_salon | cam_r_L0_salon_2, cam_r_L0_salon_3 | cam_r_L0_salon_1 (vision_check) | ok |
| r_L1_banyo | cam_r_L1_banyo_2 | cam_r_L1_banyo_1 (vision_check) | ok |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 | cam_r_L1_cocuk_odasi_1 (vision_check) | ok |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_3 | cam_r_L1_ebeveyn_y_odasi_2 (vision_check) | ok |

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_118ff62672cee88c43642f77 [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_1fab322fe57d8d05759235ad [non_commercial], 3dwh_2be96519caebb57579ea6e05 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_54891d8373ecc8558b585381 [non_commercial], 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_69e0e4f94b6b077f277e88c8 [non_commercial], 3dwh_7ca53d7f2631ae80e57db78f [non_commercial], 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_b17f872496115c534b21fd29 [non_commercial], 3dwh_bb9c3a4a718e6fc6a3b25e10 [non_commercial], 3dwh_befa49bcf2992bd57e966593 [non_commercial], 3dwh_c00b0c0f7e1ace04e940a84a [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], 3dwh_daa02f605bd71896b2572ce8 [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc], hssd_10ddf3cfd25c0ec86ac74e4e3567bcd11bf03549 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_3362008b68ae3e3f0be50057fa895cdacbfad401 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_5cf876c569c3225eab848d4269c7baa489f85014 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_afd66133d43789d6e42da81cefaf3d0a27c90180 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial], hssd_d3aaaa4c5f6f4c0f8ac9acffa625b527bf1ddc89 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: 3dwh_1fab322fe57d8d05759235ad [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L0_mutfak_1: commercial-safe: no (flagged assets: 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_c00b0c0f7e1ace04e940a84a [non_commercial])
- cam_r_L0_mutfak_2: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial])
- cam_r_L0_mutfak_3: commercial-safe: no (flagged assets: 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_c00b0c0f7e1ace04e940a84a [non_commercial])
- cam_r_L0_salon_1: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], hssd_d3aaaa4c5f6f4c0f8ac9acffa625b527bf1ddc89 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial])
- cam_r_L0_salon_2: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], hssd_d3aaaa4c5f6f4c0f8ac9acffa625b527bf1ddc89 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial])
- cam_r_L0_salon_3: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], hssd_d3aaaa4c5f6f4c0f8ac9acffa625b527bf1ddc89 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_3362008b68ae3e3f0be50057fa895cdacbfad401 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L1_banyo_2: commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L1_cocuk_odasi_1: commercial-safe: no (flagged assets: 3dwh_2be96519caebb57579ea6e05 [non_commercial], 3dwh_54891d8373ecc8558b585381 [non_commercial], 3dwh_7ca53d7f2631ae80e57db78f [non_commercial], hssd_5cf876c569c3225eab848d4269c7baa489f85014 [non_commercial])
- cam_r_L1_cocuk_odasi_2: commercial-safe: no (flagged assets: 3dwh_118ff62672cee88c43642f77 [non_commercial], 3dwh_2be96519caebb57579ea6e05 [non_commercial], 3dwh_54891d8373ecc8558b585381 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_7ca53d7f2631ae80e57db78f [non_commercial])
- cam_r_L1_cocuk_odasi_3: commercial-safe: no (flagged assets: 3dwh_118ff62672cee88c43642f77 [non_commercial], 3dwh_2be96519caebb57579ea6e05 [non_commercial], 3dwh_54891d8373ecc8558b585381 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_7ca53d7f2631ae80e57db78f [non_commercial], 3dwh_b17f872496115c534b21fd29 [non_commercial], hssd_5cf876c569c3225eab848d4269c7baa489f85014 [non_commercial])
- cam_r_L1_dus_1: commercial-safe: no (flagged assets: hssd_afd66133d43789d6e42da81cefaf3d0a27c90180 [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_1: commercial-safe: no (flagged assets: 3dwh_7ca53d7f2631ae80e57db78f [non_commercial], 3dwh_daa02f605bd71896b2572ce8 [non_commercial], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L1_ebeveyn_y_odasi_2: commercial-safe: no (flagged assets: 3dwh_69e0e4f94b6b077f277e88c8 [non_commercial], 3dwh_daa02f605bd71896b2572ce8 [non_commercial], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc], hssd_10ddf3cfd25c0ec86ac74e4e3567bcd11bf03549 [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_3: commercial-safe: no (flagged assets: 3dwh_54891d8373ecc8558b585381 [non_commercial], 3dwh_7ca53d7f2631ae80e57db78f [non_commercial], 3dwh_daa02f605bd71896b2572ce8 [non_commercial], gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc])
- cam_r_L1_hol_1: commercial-safe: yes
- cam_r_L1_oda_1: commercial-safe: yes
- cam_r_L1_oda_2_1: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_befa49bcf2992bd57e966593 [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_oda_2_2: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_oda_2_3: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_befa49bcf2992bd57e966593 [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_soyunma_odasi_1: commercial-safe: yes
- cam_r_L1_soyunma_odasi_2: commercial-safe: yes
- ext_1: commercial-safe: no (flagged assets: 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_bb9c3a4a718e6fc6a3b25e10 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: no (flagged assets: 3dwh_bb9c3a4a718e6fc6a3b25e10 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_4: commercial-safe: no (flagged assets: 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_bb9c3a4a718e6fc6a3b25e10 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_5: commercial-safe: no (flagged assets: 3dwh_bb9c3a4a718e6fc6a3b25e10 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_6: commercial-safe: no (flagged assets: 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_bb9c3a4a718e6fc6a3b25e10 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])

## Built below library level (Milestone 13)

8 furniture piece(s) built from a module builder or a parametric family instead of a library model: 0 library gap(s) to close with a real model, 8 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

| id | type | method | builder | room | room type | source | gap | used |
|---|---|---|---|---|---|---|---|---|
| f_L0_001 | stair | parametric | parametric:stair | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_020 | sink_kitchen | parametric | parametric:sink_kitchen | r_L0_mutfak | kitchen | from_documents | no (by design) | our parametric fixture (by design) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_hol | hall | from_documents | no (by design) | - |
| f_L0_031 | kitchen_counter | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_032 | kitchen_counter | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_040 | fridge | module | kitchen_run | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_041 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_042 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_2 (10.1 degrees off the sun, sky pull k 3).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| polish base | Tongyi-MAI/Z-Image-Turbo | f332072aa78be7aecdf3ee76d5c247082da564a6 | Apache-2.0 | polish_manifest.json |
| polish controlnet | alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 | 5155fc56d17821007d6f62ac192c09e0f0e72016 | Apache-2.0 | polish_manifest.json |
| gate depth | depth-anything/Depth-Anything-V2-Small-hf | 5426e4f0f36572d16453bbda7a8389317b1bef99 | Apache-2.0 | polish_manifest.json |
| gate sam | facebook/sam2.1-hiera-large | 665f8e2ad61cf5f53d65644ff27c8ee525124610 | Apache-2.0 | polish_manifest.json |
| gate dino | facebook/dinov2-base | f9e44c814b77203eaa57a6bdbbd535f21ede1415 | Apache-2.0 | polish_manifest.json |
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |
| detector | google/owlv2-base-patch16-ensemble | cfd3195ba4ea9592eec887ded089f4c08eff231d | Apache-2.0 | check_manifest.json |
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (41 of 41 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (41 of 41 answered) |

Assets: textures CC0 x 21; furniture/decor models 3DWH-UNREVIEWED x 36, CC-BY-4.0 x 37, CC-BY-NC-4.0 x 19, generated (TRELLIS.2-4B, MIT) x 5 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L1_033)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L0_mutfak_1 | calibrated | yes | yes | furniture [378.4, 454.5, 411.3, 481.2] (score); furniture [1136.5, 338.5, 1204.8, 614.3] (score) |
| cam_r_L0_mutfak_2 | calibrated | yes | yes | furniture [1556.9, 456.6, 1729.1, 696.6] (score); furniture [1266.8, 457.1, 1555.1, 668.6] (score); furniture [891.3, 302.2, 1109.0, 458.0] (vlm:agent) |
| cam_r_L0_mutfak_3 | calibrated | yes | no | - |
| cam_r_L0_salon_1 | calibrated | yes | yes | furniture [1297.6, 825.3, 1768.1, 1009.6] (score) |
| cam_r_L0_salon_2 | calibrated | yes | no | - |
| cam_r_L0_salon_3 | calibrated | yes | no | - |
| cam_r_L1_banyo_1 | calibrated | yes | yes | fixture [1.3, 190.9, 60.0, 342.5] (score) |
| cam_r_L1_banyo_2 | calibrated | yes | no | - |
| cam_r_L1_cocuk_odasi_1 | calibrated | yes | yes | furniture [1094.3, 531.2, 1110.8, 553.7] (score) |
| cam_r_L1_cocuk_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_cocuk_odasi_3 | calibrated | yes | no | - |
| cam_r_L1_dus_1 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_y_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_y_odasi_2 | calibrated | yes | yes | furniture [1096.9, 506.8, 1113.2, 541.6] (score) |
| cam_r_L1_ebeveyn_y_odasi_3 | calibrated | yes | no | - |
| cam_r_L1_hol_1 | calibrated | yes | no | - |
| cam_r_L1_oda_1 | calibrated | yes | no | - |
| cam_r_L1_oda_2_1 | calibrated | yes | no | - |
| cam_r_L1_oda_2_2 | calibrated | yes | no | - |
| cam_r_L1_oda_2_3 | calibrated | yes | no | - |
| cam_r_L1_soyunma_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_soyunma_odasi_2 | calibrated | yes | no | - |

## Stages

This run (`20261027-160846-full-20261027T161857Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 26.2 s | - |
| pipeline | pending | 36.5 s | 31 recognition question(s) written (recognition/requests.json) |
| recognize | reused | 1.9 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.3 s | - |
| pipeline_final | ok | 39.3 s | answers applied |
| fit | ok | 5.1 s | - |
| layout | ok | 20.8 s | - |
| decor_ask | ok | 3.8 min | - |
| assets | ok | 3.7 s | - |
| decor | ok | 6.8 s | - |
| agent_apply | ok | 7.0 s | - |
| refit | ok | 14.1 s | - |
| build | ok | 10.3 min | - |
| agent_previews | ok | 3.4 min | 28 view(s) |
| agent | ok | 23.9 min | 2 round(s), 8 finding(s) removed by 40 accepted edit(s) (measured; 57 predicted by the dry re-checks), 4 new, net 4, 92 rejected; stop: time budget: the final stages need the time left before the deadline - 20 min; final round for critical findings not started (time budget) |
| render | ok | 5.8 min | - |
| export | ok | 2.0 min | - |
| controls | ok | 96.6 s | - |
| gate | ok | 94.2 s | gate decision ok |
| polish | ok | 4.6 min | - |
| detect | ok | 11.5 s | - |
| expected | ok | 44.4 s | - |
| check | ok | 4.5 min | - |
| combine | ok | 26.8 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 3 round(s), 40 edit(s) accepted, 92 rejected, 240 model calls (2826661 tokens), 27.4 min. Stop: time budget: the final stages need the time left before the deadline - 20 min. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 7090): earlier runs of the appended log are left out (7089 events, 2198 model calls, 136 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 40 / 92 (30 % accepted) |
| rejected by reason | acceptance 26, no_place 12, max_tries 11, drawn_lock 8, no_change 8 |
| rooms checked by code / vision / planner | 12 / 11 / 12 |
| rooms with fixable critical or major findings visited | 12 of 12 |
| critical before -> after (after: round 2's critics, before its 15 accepted edit(s)) | 33 -> 36 |
| major before -> after (after: round 2's critics, before its 15 accepted edit(s)) | 179 -> 171 |
| agent minutes; first accepted edit after | 15.12; 3.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 3; 41; 24 (18) |
| critical/major findings removed in round 1 (measured by the next round; predicted by the dry re-checks of the same rounds) | 8 measured; 57 predicted (the last round's dry re-checks predicted 26 more, not measured) |
| new critical/major findings in round 1; net removed (gone - new) | 4 new; net 4 |
| edits removing their finding | 2 of 23 |
| plans ok / empty / refused / default | 18 / 5 / 1 / 0 |

### What the AI inspector saw on the final renders

0 vision finding(s) (0 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 0 fixed in the final round, 0 handed to the stage that owns them, 0 open; the architect leaves 4 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`. The final round did not start (time): these are the last round's findings on the previews.

### Argus, the auditor

Score 11.3 / 100 (100 = nothing open): 0 critical, 121 major, 57 minor open. By kind (critical + major): taste 58, lost 22, other 13, no_sense 10, misread 6, geometry 5, silent 5, process 2. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Library gaps reported by the agent: sofa mixed (No single library style unifies the caramel leather sofa f_L0_006 and beige fabric sofa f_L0_014; both are drawn at real sizes and the room has no higher-rated alternative models to swap in.), armchair mixed (No single library style unifies the black armchair f_L0_007, red egg-chair f_L0_016 and other seating; all are drawn at real sizes and no higher-rated alternative models exist to swap in.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 33 | 179 | 23 | 26 | 25 | 50 | layout | 28 |
| 2 | 36 | 171 | 23 | 22 | 15 | 42 | layout | 29 |
| 3 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A6 | 0 | 0 | 0 | 2 |
| AI1 | 0 | 36 | 0 | 2 |
| AI2 | 0 | 0 | 0 | 12 |
| AI3 | 0 | 0 | 0 | 2 |
| C3 | 0 | 4 | 0 | 0 |
| C7 | 0 | 2 | 0 | 0 |
| D1 | 0 | 4 | 0 | 0 |
| D2 | 4 | 34 | 0 | 3 |
| D3 | 0 | 36 | 0 | 0 |
| F1 | 0 | 0 | 4 | 0 |
| F3 | 2 | 14 | 6 | 0 |
| F4 | 0 | 6 | 0 | 0 |
| F6 | 0 | 2 | 0 | 0 |
| F7 | 12 | 0 | 0 | 0 |
| F9 | 4 | 42 | 0 | 1 |
| G1 | 0 | 0 | 4 | 0 |
| G10 | 0 | 14 | 0 | 0 |
| G11 | 24 | 27 | 4 | 0 |
| G12 | 0 | 4 | 0 | 0 |
| G14 | 0 | 0 | 4 | 0 |
| G2 | 0 | 2 | 2 | 0 |
| G3 | 0 | 8 | 0 | 0 |
| G4 | 0 | 2 | 5 | 0 |
| G5 | 0 | 7 | 0 | 0 |
| G6 | 0 | 0 | 2 | 0 |
| G8 | 0 | 2 | 2 | 0 |
| J1 | 0 | 36 | 0 | 16 |
| K1 | 0 | 2 | 0 | 0 |
| K2 | 0 | 2 | 0 | 0 |
| K4 | 0 | 0 | 0 | 2 |
| L2 | 0 | 8 | 0 | 0 |
| M2 | 0 | 2 | 0 | 0 |
| NR | 0 | 4 | 0 | 0 |
| P0 | 0 | 4 | 0 | 0 |
| P2 | 0 | 2 | 0 | 0 |
| P3 | 0 | 0 | 0 | 8 |
| P7 | 0 | 6 | 0 | 0 |
| Q3 | 3 | 0 | 0 | 0 |
| Q4 | 6 | 12 | 0 | 0 |
| Q5 | 2 | 10 | 0 | 0 |
| Q6 | 0 | 4 | 0 | 0 |
| Q7 | 0 | 2 | 0 | 0 |
| RC | 0 | 0 | 2 | 0 |
| S2 | 0 | 6 | 3 | 0 |
| S3 | 0 | 2 | 0 | 0 |
| S5 | 0 | 0 | 6 | 0 |
| V1 | 4 | 2 | 0 | 0 |
| X2 | 0 | 0 | 2 | 0 |
| X3 | 8 | 0 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 7381 | 1 | set_exterior | exterior:ground,site | agent_override | - | Argus: The judge calls the view through o_L0_002 a crude low-poly landscape; the site has no real ground or trees, so the render shows a placeholder. (fixes a:F5) | - | - |
| 7382 | 1 | set_camera | r_L1_oda | agent_override | - | Argus: The judge sees a corridor shot dominated by a wall and door; the shoe cabinet (the room's only piece) is not in frame. (fixes a:F8) | - | - |
| 7383 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The judge sees a flat grey surface and a wood strip; the wardrobe is the room's main piece but the camera is too close and mis-aimed. (fixes a:F9) | - | - |
| 7384 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The judge sees a large flat grey area; the camera is mis-aimed at a bare surface instead of the wardrobe. (fixes a:F15) | - | - |
| 7385 | 1 | set_exterior | exterior:ground,site | agent_override | - | Argus: The judge flagged the landscape as a placeholder. The set_exterior tool with a valid ground look and site object (trees, fence, path) will replace the default placeholder site with a believable one. (fixes a:F17) | - | - |
| 7386 | 1 | swap_model | f_L0_036 | added_by_ai | 0.0 -> 0.0 | Argus: The stove is planned but missing from the scene. It was assigned a kitchen_counter module model which likely failed to build as a distinct object. Swapping to a dedicated stove model from the catalogue will ensure it is built. (fixes a:F18) | ![](agent/r1_002_swap_model_before_r_L0_mutfak.png) | ![](agent/r1_003_swap_model_after_r_L0_mutfak.png) |
| 7388 | 1 | set_camera | r_L0_banyo | agent_override | - | Argus: The toilet f_L0_024 is built in r_L0_banyo (the room's piece list holds it); the judge's 2/5 view is a camera that misses it. The fix is to point the camera at the piece, not to rebuild it. (fixes a:F33) | - | - |
| 7389 | 1 | set_camera | r_L0_mutfak | agent_override | - | Argus: The dining table f_L0_037 and its chairs are built in r_L0_mutfak; the judge's 2/5 view is a camera that misses them. The fix is to point the camera at the piece, not to rebuild it. (fixes a:F34) | - | - |
| 7390 | 1 | set_camera | r_L0_mutfak | agent_override | - | Argus: The wall cabinet f_L0_041 is built in r_L0_mutfak; the judge's 2/5 view is a camera that misses it. The fix is to point the camera at the piece, not to rebuild it. (fixes a:F35) | - | - |
| 7391 | 1 | set_camera | r_L0_salon | agent_override | - | Argus: The dining table f_L0_011 and its chairs are built in r_L0_salon; the judge's 2/5 view is a camera that misses them. The fix is to point the camera at the piece, not to rebuild it. (fixes a:F36) | - | - |
| 7394 | 1 | set_exterior | exterior:ground,site | agent_override | - | Argus: The judge flags the view through the windows as a crude low-poly placeholder; the site stage left the default lollipop trees and flat ground. A richer site (more trees, hedge, grass) is the cause-level fix. (fixes a:F65) | - | - |
| 7395 | 1 | swap_model | f_L0_038 | added_by_ai | 0.0 -> 0.0 | Argus: The dark heavy wooden chair clashes with the light minimalist kitchen. Swapping to a modern/scandinavian chair matches the room's style. (fixes a:F70) | ![](agent/r1_006_swap_model_before_r_L0_mutfak.png) | ![](agent/r1_007_swap_model_after_r_L0_mutfak.png) |
| 7399 | 1 | swap_model | f_L0_011 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The wooden bench (table_dining) is a third clashing style. Swapping to a scandinavian/japandi table matches the light minimalist room. (fixes a:F77) | ![](agent/r1_011_swap_model_before_r_L0_salon.png) | ![](agent/r1_012_swap_model_after_r_L0_salon.png) |
| 7401 | 1 | swap_model | f_L1_009 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The judge flags the bathtub as a basic 3D primitive; swapping to a classic/minimal/modern model with detail resolves the issue. (fixes a:F82) | ![](agent/r1_014_swap_model_before_r_L1_banyo.png) | ![](agent/r1_015_swap_model_after_r_L1_banyo.png) |
| 7404 | 1 | swap_model | f_L1_004 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The judge flags the bed and dresser as a mismatched set; swapping f_L1_004 to a minimal/modern/scandinavian bed matches the dresser's style. (fixes a:F87) | ![](agent/r1_018_swap_model_before_r_L1_cocuk_odasi.png) | ![](agent/r1_019_swap_model_after_r_L1_cocuk_odasi.png) |
| 7405 | 1 | set_camera | r_L1_dus | agent_override | - | Argus: The judge flags the camera as framing a wall and a door handle, with the view blocked by the shower screen; setting the camera to show the room's contents resolves the issue. (fixes a:F89) | - | - |
| 7406 | 1 | set_material | door | agent_override | - | Argus: The judge flags the door as a darker, rawer wood that clashes with the light-oak set; setting the door material to wood_oak_light resolves the issue. (fixes a:F94) | - | - |
| 7420 | 1 | move_piece | f_L1_005 | adjusted_by_ai | 0.0 -> 0.0 | Snap the dresser's back onto the left wall (it was 0.06 m off) and shift it up the wall to clear the 0.07 m² overlap with bed f_L1_004 and the railing. | ![](agent/r1_055_move_piece_before_r_L1_cocuk_odasi.png) | ![](agent/r1_056_move_piece_after_r_L1_cocuk_odasi.png) |
| 7423 | 1 | report_library_gap | f_L0_014 | library_gap | - | No single library style unifies the caramel leather sofa f_L0_006 and beige fabric sofa f_L0_014; both are drawn at real sizes and the room has no higher-rated alternative models to swap in. | - | - |
| 7427 | 1 | report_library_gap | f_L0_007 | library_gap | - | No single library style unifies the black armchair f_L0_007, red egg-chair f_L0_016 and other seating; all are drawn at real sizes and no higher-rated alternative models exist to swap in. | - | - |
| 7443 | 1 | relayout_room | r_L1_cocuk_odasi | adjusted_by_ai | 0.0 -> 0.0 | Re-place the AI pieces with the solver's best candidate to fix the group clearance and walkway findings (G4, G5, G11) that single-piece moves cannot reach. | ![](agent/r1_076_relayout_room_before_r_L1_cocuk_odasi.png) | ![](agent/r1_077_relayout_room_after_r_L1_cocuk_odasi.png) |
| 7463 | 1 | set_exterior | exterior:site | agent_override | - | Add more trees and a front court to replace the crude lollipop placeholder landscape with a believable site visible through windows and exterior views. | - | - |
| 7468 | 1 | set_camera | r_L1_oda | agent_override | - | Reposition the hall camera to frame the shoe cabinet instead of the dead-end corridor and door leaf. | - | - |
| 7482 | 1 | rotate_piece | f_L1_019 | adjusted_by_ai | 0.0 -> 10.0 | washing machine front faces a wall 0.00 m ahead; turn it to face into the room | ![](agent/r1_097_rotate_piece_before_r_L1_banyo.png) | ![](agent/r1_098_rotate_piece_after_r_L1_banyo.png) |
| 7487 | 1 | set_front | f_L0_010 | adjusted_by_ai | 20.0 -> 40.0 | bathtub front faces the open room (SE), away from the wall its head end is against | ![](agent/r1_101_set_front_before_r_L0_banyo.png) | ![](agent/r1_104_set_front_after_r_L0_banyo.png) |
| 7819 | 2 | set_exterior | exterior:ground,site | agent_override | - | Argus: The judge flags the raw grey-box site (lollipop trees, flat green plane) as the reason the exterior is not client-ready; the site stage left the placeholder environment in place. (fixes a:F113) | - | - |
| 7822 | 2 | swap_model | f_L1_010 | adjusted_by_ai | 44.0 -> 44.0 | Argus: The master bed is a bare white duvet; a library model with layered pillows and a throw makes it read as a finished bedroom. (fixes a:F123) | ![](agent/r2_003_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r2_004_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 7823 | 2 | set_camera | r_L1_oda_2 | agent_override | - | Argus: The wardrobe and dresser are not visible in the view, making the room feel empty; the camera must be re-posed to include them. (fixes a:F125) | - | - |
| 7824 | 2 | set_material | facade | agent_override | - | Argus: The wall surface is flat untextured white with a thin stone plinth; a real stone cladding look fixes the model-like appearance. (fixes a:F127) | - | - |
| 7825 | 2 | set_material | plinth | agent_override | - | Argus: The stone cladding at the base looks like a decal; a real stone wall look fixes it. (fixes a:F128) | - | - |
| 7828 | 2 | swap_model | f_L0_037 | added_by_ai | 0.0 -> 0.0 | Argus: The dining table is a simple, untextured cylinder that looks like a low-poly asset. Swapping to a library model (hssd_e9393fb84e42e59d93ba261275daf119df0cde2e, 0.80 x 0.80 x 0.75 m, minimal/modern) will improve the visual quality. (fixes a:F169) | ![](agent/r2_007_swap_model_before_r_L0_mutfak.png) | ![](agent/r2_008_swap_model_after_r_L0_mutfak.png) |
| 7829 | 2 | swap_model | f_L1_022 | adjusted_by_ai | 10.0 -> 10.0 | Argus: The toilet is a very basic, generic model that contributes to the overall cheap and unfinished feel of the bathroom. Swapping to a library model (3dwh_5ec28d91d89a3a8e94ae233c, 0.44 x 0.72 x 0.76 m, minimal/modern) will improve the visual q (fixes a:F171) | ![](agent/r2_009_swap_model_before_r_L1_banyo.png) | ![](agent/r2_010_swap_model_after_r_L1_banyo.png) |
| 7830 | 2 | set_material | wet_walls | agent_override | - | Argus: The walls are a flat, untextured white, which makes the surfaces look like a 'grey box' render. Setting the wet walls to a tile texture (tiles_light) will add material detail and improve the visual quality. (fixes a:F172) | - | - |
| 7831 | 2 | set_exterior | exterior:site | agent_override | - | Argus: The outdoor scene is a flat, washed-out placeholder with lollipop-style trees, which does not sell the home and looks unfinished. Adding realistic trees, a hedge, and a front court will improve the visual quality of the exterior. (fixes a:F173) | - | - |
| 7832 | 2 | swap_model | f_L1_016 | adjusted_by_ai | 44.0 -> 44.0 | Argus: The two armchairs are different models and materials; swapping one to a minimal/scandinavian model that can pair with the other coordinates the corner. (fixes a:F178) | ![](agent/r2_011_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r2_012_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 7835 | 2 | swap_model | f_L1_025 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The nightstand is a plain open box that does not match the room's calm style; the japandi model from the allowed list fits the 0.40x0.42 m footprint and the room's palette. (fixes a:F182) | ![](agent/r2_014_swap_model_before_r_L1_oda_2.png) | ![](agent/r2_015_swap_model_after_r_L1_oda_2.png) |
| 7884 | 2 | set_front | f_L1_009 | adjusted_by_ai | 10.0 -> 30.0 | Bathtub front currently faces a wall 0.30 m away; flipping to 248.3° orients it into the room. | ![](agent/r2_081_set_front_before_r_L1_banyo.png) | ![](agent/r2_082_set_front_after_r_L1_banyo.png) |
| 7889 | 2 | remove_piece | f_L1_028 | added_by_ai | 100.0 -> 100.0 | AI-added shoe cabinet is invisible in the view and makes the hall read as an empty corridor; retype to dresser was rejected as size-incompatible, so remove it to clear Q4. | ![](agent/r2_085_remove_piece_before_r_L1_oda.png) | ![](agent/r2_086_remove_piece_after_r_L1_oda.png) |
| 7891 | 2 | relayout_room | r_L1_oda | adjusted_by_ai | 100.0 -> 100.0 | Documents name a dresser (SIFONIYER) on L1; solver candidate 1 (score 8.73, recommended) re-places the entrance group to supply the room's furniture. | ![](agent/r2_088_relayout_room_before_r_L1_oda.png) | ![](agent/r2_089_relayout_room_after_r_L1_oda.png) |
| 7897 | 2 | swap_model | f_L0_010 | adjusted_by_ai | 40.0 -> 40.0 | Replace the plain white box bathtub with a Stone Bath model (1.8x0.79x0.63) that has realistic texture and design detail, addressing the wrong_model finding. | ![](agent/r2_096_swap_model_before_r_L0_banyo.png) | ![](agent/r2_097_swap_model_after_r_L0_banyo.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 7380 | 1 | place_group | r_L0_mutfak | no_change: r_L0_mutfak already has its kitchen_run r_L0_mutfak.kitchen_run (anchor f_L0_002, members f_L0_020, f_L0_031, f_L0_032, f_L0_036, f_L0_040): nothing missing, never a second set | Argus: The room lists stove and wall_cabinet but the counter piece is 'not built' and the judge sees no cooking zone or upper storage; the run was not assembled. (fixes a:F2) |
| 7387 | 1 | swap_model | f_L0_040 | acceptance: pin_refused: f_L0_040: hssd_821a2d741626ea190a2ed794c681a51dbcda48fa: audit: removed (44 triangles (< 3000): crude unless the vision quality is high; vision quality 1; vision quality 1 (<= 2)): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The fridge is planned but missing from the scene. It was assigned a kitchen_counter module model which likely failed to build as a distinct object. Swapping to a dedicated fridge model from the catalogue will ensure it is built. (fixes a:F19) |
| 7392 | 1 | set_camera | r_L1_hol | show: no free camera point of r_L1_hol shows f_L1_001 | Argus: The shoe cabinet f_L1_034 is built in r_L1_hol; the judge's 2/5 view is a camera that misses it. The fix is to point the camera at the piece, not to rebuild it. (fixes a:F37) |
| 7393 | 1 | swap_model | f_L0_026 | acceptance: pin_refused: f_L0_026: hssd_ad635dc49d8e6113fffb33d691c948159b71fc56: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current washbasin model is a basic, generic shape that looks cheap; swapping to a more detailed minimal/modern model (0.60 x 0.35 x 0.26 m) improves the room's finish. (fixes a:F63) |
| 7396 | 1 | swap_model | f_L0_016 | lower_quality: f_L0_016: 3dwh_d1ed36390489612fbb2a5baa is rated 3.0 against 5.0 of the current model abo_B075X4N3GM: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Argus: The red egg-chair is a loud mid-century piece clashing with the other seating. Swapping to a minimal/modern/scandinavian armchair unifies the room. (fixes a:F73) |
| 7397 | 1 | swap_model | f_L0_007 | lower_quality: f_L0_007: 3dwh_d1ed36390489612fbb2a5baa is rated 3.0 against 5.0 of the current model abo_B075X4N3GM: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Argus: The black armchair (same egg-chair model) is a different style from the other seating. Swapping to a minimal/modern/scandinavian armchair unifies the room. (fixes a:F74) |
| 7398 | 1 | swap_model | f_L0_006 | lower_quality: f_L0_006: hssd_4364e0d4faa0006a6e447b9293fdfbe3c415cfa7 is rated 3.0 against 4.5 of the current model abo_B072555T67: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Argus: The long low orange sofa clashes with the white sofa and the dark red egg chair. Swapping to a modern/scandinavian sofa unifies the seating group. (fixes a:F75) |
| 7400 | 1 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: hssd_3f0778f68a489d3995e2e3f13d13e4a90fb500a8: fails the fit rules (caps, height, at most 2.38 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The judge flags the black basin as a clash in a monochromatic white room; swapping to a minimal/modern white basin resolves the style mismatch. (fixes a:F81) |
| 7402 | 1 | swap_model | f_L1_007 | lower_quality: f_L1_007: 3dwh_118ff62672cee88c43642f77 is rated 3.0 against 4.0 of the current model abo_B08FTN8KHY: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The judge flags the two beds as a mismatched set; swapping f_L1_007 to a minimal/modern/scandinavian bed matches the other bed's style. (fixes a:F84) |
| 7403 | 1 | swap_model | f_L1_031 | acceptance: pin_refused: f_L1_031: 3dwh_7853f58c2986fd3b3b4aaaa1: audit: removed (2244 triangles (< 3000): crude unless the vision quality is high; vision quality 3): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The judge flags the wardrobe as a flat slab with no visible doors; swapping to a minimal/modern/scandinavian model with detail resolves the issue. (fixes a:F85) |
| 7407 | 1 | set_exterior | exterior:ground,site | no_change: the exterior already has these values ({"ground": "grass", "site": {"fence": "hedge", "trees": 8}}): nothing to change | Argus: The window view shows crude low-poly lollipop trees and flat green ground. (fixes a:F98) |
| 7408 | 1 | swap_model | f_L1_013 | pin_refused: f_L1_013: gen_bed_single_scandinavian_1_8060783a: audit: removed (proportions 1.24 x 1.62 x 0.72 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6))): the real model stays; swap to a real model of the type or use another tool | Argus: The bed is a plain white slab with no bedding or texture. (fixes a:F101) |
| 7409 | 1 | swap_model | f_L1_014 | pin_refused: f_L1_014: gen_wardrobe_rustic_1_97c119f6: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07GFS1VB6): the real model stays; swap to a real model of the type or use another tool | Argus: The wardrobe is a flat, handle-less, seam-less wood slab. (fixes a:F103) |
| 7412 | 1 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Re-solve seating around drawn sofa f_L0_006 to fix off-wall back, orientation, coffee table placement, armchair alignment and the d_L0_004→d_L0_006 walkway. |
| 7413 | 1 | move_piece | f_L1_020 | drawn_lock: f_L1_020: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.44 m) | Shift the floor lamp out of the free zone in front of armchair f_L116 to restore its clearance (F6). |
| 7414 | 1 | move_piece | f_L1_015 | drawn_lock: f_L1_015: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.37 m) | Move the armchair away from the entrance walkway between doors d_L1_002 and d_L1_007 to restore the 0.80 m main circulation (G11). |
| 7416 | 1 | move_piece | f_L1_020 | drawn_lock: f_L1_020: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the floor lamp 0.3 m out of the free zone in front of armchair f_L1_016 to restore its clearance (F6). |
| 7417 | 1 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Try candidate 2 to clear the d_L0_004→d_L0_006 walkway and fix seating group orientation issues. |
| 7418 | 1 | move_piece | f_L1_015 | f_L1_015: doors_free, score: plausibility 44 -> 14 (F7 f_L1_015: armchair blocks door o_L1_006) | Move the armchair 0.3 m away from the entrance walkway between doors d_L1_002 and d_L1_007 to restore the 0.80 m main circulation (G11). |
| 7419 | 1 | relayout_room | r_L0_salon | max_tries: r_L0_salon was edited 3 times in this round | Try candidate 3 to clear the d_L0_004→d_L0_006 walkway and fix seating group orientation issues. |
| 7422 | 1 | move_piece | f_L1_020 | acceptance: finding F6:f_L1_016 is still there after the edit (armchair: the free zone in front of it is blocked by f_L1_020) | Shift the floor lamp 0.29 m out of the free zone in front of armchair f_L1_016 to restore its clearance (F6). |
| 7424 | 1 | move_piece | f_L1_015 | drawn_lock: f_L1_015: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Move the armchair 0.3 m left, away from the entrance walkway between doors d_L1_002 and d_L1_007, to restore the 0.80 m main circulation (G11). |
| 7425 | 1 | fix_fixture | f_L0_032 | fixture_place: f_L0_032: no valid spot within 0.50 m (it stands 0.06 m² outside the room, in door o_L0_001) | Counter reported at 2.10 m top, a misread of working height; correct to a real product size. |
| 7426 | 1 | fix_fixture | f_L0_031 | fixture_place: f_L0_031: no valid spot within 0.50 m (it stands 0.18 m² outside the room) | Counter overlaps f_L0_002 by 0.44 m²; nudge to resolve the collision. |
| 7428 | 1 | move_piece | f_L1_020 | max_tries: f_L1_020 was edited 3 times in this round | Shift the floor lamp 0.34 m out of the free zone in front of armchair f_L1_016 to restore its clearance (F6). |
| 7429 | 1 | move_piece | f_L1_015 | max_tries: f_L1_015 was edited 3 times in this round | Move the armchair 0.29 m left, away from the entrance walkway between doors d_L1_002 and d_L1_007, to restore the 0.80 m main circulation (G11). |
| 7431 | 1 | complete_group | r_L1_cocuk_odasi.storage | no_change: r_L1_cocuk_odasi.storage: nothing missing (members: none) | The documents name a dresser/wardrobe on L1; complete the storage group so the room's primary storage is fully built. |
| 7432 | 1 | complete_group | r_L1_cocuk_odasi.sleeping_double.f_L1_007 | no_place: r_L1_cocuk_odasi.sleeping_double.f_L1_007 (missing nightstand), re-solved as one unit around the drawn bed_double f_L1_007: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | The second bed's nightstand was left unbuilt (it cut the bed); complete the group so the second bed in the child's room is fully built with its partner. |
| 7433 | 1 | relayout_room | r_L0_mutfak | max_tries: r_L0_mutfak was edited 3 times in this round | Reposition the dining group to open the 0.60 m walkway from door d_L0_003 to the other doors and the kitchen front use zones. |
| 7434 | 1 | mark_not_furniture | f_L1_002 | no_crop: f_L1_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/cam_r_L1_cocuk_odasi_1_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The 4.64 m long, 0.68 m thin cluster is a wall element/railing band, not a piece of furniture; marking it clears the untyped finding. |
| 7436 | 1 | move_piece | f_L1_007 | acceptance: finding F7:f_L1_007 is still there after the edit (bed_double blocks door d_L1_011) | Nudge the second bed off wall w_L1_004 (it cut it by 0.038 m) and clear door d_L1_011's swing, which the bed blocks. |
| 7437 | 1 | move_piece | f_L1_007 | drawn_lock: f_L1_007: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.30 m) | Shift the second bed further up (0.3 m allowance) to clear door d_L1_011's swing, which the bed still blocks. |
| 7440 | 1 | move_piece | f_L1_007 | max_tries: f_L1_007 was edited 3 times in this round | Snap the second bed's back onto its wall (drawn pieces may move 1.2 m when snapping) and shift it along the wall to clear door d_L1_011's swing. |
| 7441 | 1 | move_piece | f_L1_008 | snap: f_L1_008: no free place on wall w_L1_022 (doors, windows, at most 1.2 m from the drawn place) | Move the nightstand to the head of bed f_L1_007 (back within 0.30 m of the headboard line, front facing the bed) instead of 0.99 m away. |
| 7442 | 1 | move_piece | f_L1_008 | drawn_lock: f_L1_008: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | Move the nightstand up to the head of bed f_L1_007 (back within 0.30 m of the headboard line) instead of 0.99 m away at the foot. |
| 7450 | 1 | move_group | r_L1_soyunma_odasi.storage | drawn_lock: r_L1_soyunma_odasi.storage: drawn pieces (f_L1_011) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Wardrobe f_L1_011 blocks windows win_L1_003/win_L1_005 and breaks the 0.60 m walkways; re-solve the drawn storage group onto the free south wall span (front faces into the room, away from the windows). |
| 7451 | 1 | move_group | r_L1_soyunma_odasi.storage.f_L1_012 | drawn_lock: r_L1_soyunma_odasi.storage.f_L1_012: drawn pieces (f_L1_012) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Wardrobe f_L1_012 blocks window win_L1_004 and breaks the 0.60 m walkways; re-solve the drawn storage group onto the free south wall span (front faces into the room, away from the windows). |
| 7454 | 1 | relayout_room | r_L1_soyunma_odasi | no_place: r_L1_soyunma_odasi relayout: no place passes the checks (dressing: no place passes the checks) | Re-solve the room so the two drawn wardrobes leave the window bays (win_L1_003/004/005) and the 0.60 m walkways from door d_L1_003 to all windows are restored. |
| 7456 | 1 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_008 (doors, windows, at most 1.2 m from the drawn place) | Wardrobe f_L1_011 blocks windows win_L1_003/win_L1_005 and breaks the 0.60 m walkways; snap it to the free south wall span (front faces into the room, away from the windows). |
| 7458 | 1 | move_piece | f_L1_011 | f_L1_011: clearance_ok | Shift wardrobe f_L1_011 0.174 m off the north wall (its full move allowance) to clear the window bays win_L1_003/win_L1_005 and restore the 0.60 m walkways. |
| 7459 | 1 | move_piece | f_L1_011 | acceptance: finding F7:f_L1_011 is still there after the edit (wardrobe blocks door win_L1_005) | Restore wardrobe f_L1_011 to its drawn position after the rejected move (no valid spot exists within its 0.174 m allowance). |
| 7464 | 1 | set_material | facade | facade: look 'render_stucco_warm_white' is not in the vocabulary | Give the facade a textured stucco finish to remove the flat untextured white grey-box look. |
| 7467 | 1 | move_piece | f_L1_034 | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009) | Move shoe cabinet to right wall span s2 to clear walkway between doors d_L1_006 and d_L1_009 (c:G11:d_L1_006) |
| 7469 | 1 | set_camera | r_L1_soyunma_odasi | max_tries: r_L1_soyunma_odasi was edited 3 times in this round | Move the dressing room camera away from the wardrobe face to a pose that shows the two wardrobes as a coherent group. |
| 7470 | 1 | fix_fixture | f_L1_001 | fixture_place: f_L1_001: no valid spot within 0.50 m (it stands 0.51 m² outside the room, in door d_L1_009) | Check if stair is blocking walkway or door swing (G11 findings) |
| 7473 | 1 | set_camera | r_L1_dus | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Reposition the bathroom camera to a clear angle showing the toilet, washbasin and shower without the glass screen or door frame blocking the frame. |
| 7477 | 1 | set_camera | r_L1_hol | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Reposition the hall camera to frame the shoe cabinet and landing instead of a blank wall and door. |
| 7481 | 1 | retype_piece | f_L1_028 | retype: dresser is no candidate for f_L1_028 (0.60 x 0.25 m at [4.75, 7.67]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet | Documents name a dresser (SIFONIYER) on L1; the 0.6x0.25 piece is too small to read as a shoe cabinet and the hall's primary furniture should be the dresser. |
| 7488 | 1 | fix_fixture | f_L1_027 | acceptance: finding F7:f_L1_027 is still there after the edit (washbasin blocks door win_L1_004) | Washbasin blocks the opening of window win_L1_004; nudge it off the opening (code picks the nearest valid spot). |
| 7492 | 1 | fix_fixture | f_L1_027 | score: plausibility 90 -> 80 (G10 f_L1_027: washbasin f_L1_027: 0.19 m clear in front, needs ≥ 0.53 m) | Nudge washbasin 0.45 m up the left wall, clear of window win_L1_004 (sill 0.9 m) and into the free span s4, to unblock the opening. |
| 7818 | 2 | swap_model | f_L1_012 | acceptance: pin_refused: f_L1_012: abo_B07H8JN9QF: fails the fit rules (caps, height, at most 2.80 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: f_L1_012 (flat oak slab, grey handle) clashes with f_L1_011 (white shaker, wood handles). (fixes a:F106) |
| 7820 | 2 | swap_model | f_L0_010 | no_change: f_L0_010 already uses the model hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed | Argus: The bathtub is a plain white box contributing to the grey-box feel; a textured library model of the same 1.80 x 0.80 m footprint fixes it. (fixes a:F118) |
| 7821 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Argus: The egg-chair f_L0_016 is tight against the right wall with no companion; re-solving the salon layout gives it space and a seating arrangement. (fixes a:F121) |
| 7826 | 2 | place_group | r_L1_soyunma_odasi | no_place: dressing group: no place passes the checks (dressing: no place passes the checks) | Argus: The room is typed as 'other' but is named 'Soyunma Odası' (dressing room) and already has a wardrobe. The dressing group could not be placed because the room is too small (5.9 m²) and the existing wardrobe blocks the space. Placing the dres (fixes a:F163) |
| 7827 | 2 | swap_model | f_L0_020 | acceptance: pin_refused: f_L0_020: 3dwh_c40a2fac663a4c615676d8e5: audit: removed (1.26 x 0.47 x 0.58 m fits a sink_kitchen only with another axis up: the model lies on its side; an anchor (sink_kitchen) of units guessed (x1.0): the Milestone 13 gate needs known units for anchors; the vision check says it is not a sink_kitchen; vision quality 1 (<= 2)): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The sink is built parametrically because the fitting chose the parametric mesh. Swapping to a library model (3dwh_c40a2fac663a4c615676d8e5, 1.26 x 0.47 x 0.58 m, neutral) will improve the visual quality and match the room's style. (fixes a:F166) |
| 7833 | 2 | swap_model | f_L1_020 | pin_refused: f_L1_020: gen_floor_lamp_japandi_2_ef5fd39d: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07B4ZK8BR): the real model stays; swap to a real model of the type or use another tool | Argus: The tripod lamp is too tall and slender for the low armchairs; the 1.20 m japandi lamp from the allowed list matches the room's scale and palette. (fixes a:F179) |
| 7834 | 2 | complete_group | r_L1_ebeveyn_y_odasi | group_exists: no group 'r_L1_ebeveyn_y_odasi' in r_L1_ebeveyn_y_odasi (groups: r_L1_ebeveyn_y_odasi.sleeping_double, r_L1_ebeveyn_y_odasi.work) | Argus: Only one nightstand is shown while the bed is flanked by empty wall; completing the sleeping group adds the second nightstand. (fixes a:F180) |
| 7836 | 2 | fix_fixture | f_L0_010 | no_change: f_L0_010: nothing to fix (size within the real range, inside the room and off the doors) | Argus: f_L0_010 (bathtub 1.80 x 0.80 m in r_L0_banyo) overlaps f_L0_026 by 0.33 m. The bathtub is a drawn fixed piece; the overlap is a misread size or position. fix_fixture without center lets the code move it to the nearest valid spot. The model (fixes a:F243) |
| 7837 | 2 | fix_fixture | f_L1_009 | no_change: f_L1_009: nothing to fix (size within the real range, inside the room and off the doors) | Argus: f_L1_009 (bathtub 1.80 x 0.80 m in r_L1_banyo) overlaps f_L1_023 by 0.25 m. Same cause as F243: the bathtub is a drawn fixed piece whose position or size causes a clash. fix_fixture without center moves it to the nearest valid spot. (fixes a:F244) |
| 7838 | 2 | place_group | r_L0_mutfak | no_place: dining group: no place passes the checks (dining: no place passes the checks) | Argus: The kitchen is missing its main anchor. The dining table (f_L0_037) and chairs (f_L0_038, f_L0_039, f_L0_040) are listed in the room's pieces but are not visible in the render. The stove (f_L0_036) is also planned but not built. (fixes a:N92) |
| 7839 | 2 | place_group | r_L0_banyo | no_change: r_L0_banyo already has its bathroom_set r_L0_banyo.bathroom_set (anchor f_L0_010, members f_L0_024, f_L0_026): nothing missing, never a second set | Argus: The bathroom is missing its main piece, the toilet. A bathroom without a toilet is incomplete. (fixes a:N93) |
| 7840 | 2 | place_group | r_L1_cocuk_odasi | no_place: bedroom_chest group: no place passes the checks (bedroom_chest: no place passes the checks) | Argus: The documents name a dresser ('*SIFONIYER') on L1, but the model has no piece within 1.2 m. The child's room is missing its dresser. (fixes a:N94) |
| 7841 | 2 | place_group | r_L1_oda_2 | no_place: bedroom_chest group: no place passes the checks (bedroom_chest: no candidate position fits the room) | Argus: The documents name a dresser ('*SIFONIYER') on L1, but the model has no piece within 1.2 m. The second bedroom is missing its dresser. (fixes a:N95) |
| 7842 | 2 | fix_fixture | f_L0_032 | fixture_size: f_L0_032: the drawn 2.40 x 0.60 m is within 30 % of the real kitchen_counter range (width 0.60-5.00 m, depth 0.50-0.75 m): its size stays as drawn | Argus: f_L0_032 (kitchen_counter) has its top at 2.10 m over the floor, over its working height. This is a misread of the kitchen counter's height. (fixes a:N96) |
| 7843 | 2 | place_group | r_L1_cocuk_odasi | no_place: sleeping_double group re-solved around the drawn bed_double f_L1_004: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Argus: f_L1_008 (bed_double) is left out for a reason that hides a loss: not built: architect F5: it cut f_L1_007 (bed_double). The second bed in the child's room is missing. (fixes a:N100) |
| 7844 | 2 | place_group | r_L1_ebeveyn_y_odasi | no_place: storage group: no place passes the checks (storage: no candidate position fits the room) | Argus: f_L1_002 (wardrobe) is left out for a reason that hides a loss: not built: cluster larger than 4.5 m on a side. The wardrobe in the parent's room is missing. (fixes a:N101) |
| 7845 | 2 | place_group | r_L1_oda | room_type: a storage group does not belong in a hall room (groups.yaml room types: bedroom) | Argus: The documents name a dresser ('*SIFONIYER') on L1, but the model has no piece within 1.2 m. The room 'Oda' (hall) is missing its primary furniture. (fixes a:N107) |
| 7846 | 2 | place_group | r_L1_ebeveyn_y_odasi | no_place: bedroom_chest group: no place passes the checks (bedroom_chest: no candidate position fits the room) | Argus: The documents name a dresser ('*SIFONIYER') on L1, but the model has no piece within 1.2 m. The room 'Ebeveyn Y.odası' (master bedroom) is missing its primary furniture. (fixes a:N108) |
| 7847 | 2 | retype_piece | f_L1_006 | f_L1_004: no_overlap, f_L1_006: no_overlap, score: plausibility -32 -> -42 (F9 f_L1_006: floor_lamp f_L1_006 overlaps bed_double f_L1_004 by 0.16 m²) | the plan names it: drawn piece f_L1_006 (0.40 x 0.40 m) left out as a detail (drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)) although an AI pass named it floor_lamp / nightstand, which fits its size: (fixes a:c4) |
| 7849 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Re-solve the seating group around drawn anchor f_L0_006 to fix the sofa's off-wall and orientation, place the coffee table in front, and clear the walkway between doors d_L0_004 and d_L0_006. |
| 7852 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Re-solve the seating group around drawn anchor f_L0_006 (candidate 2) to fix the sofa's off-wall and orientation, place the coffee table in front, and clear the walkway between doors d_L0_004 and d_L0_006. |
| 7855 | 2 | relayout_room | r_L1_ebeveyn_y_odasi | max_tries: r_L1_ebeveyn_y_odasi was edited 3 times in this round | Candidate 3 has the best circulation score (0.93) and no hard failures; it re-solves the room to fix the bed headboard off-wall (F3), the nightstand off-wall (F3), the blocked armchair clearance (F6), and the narrow walkway between doors (G11) by moving the sleeping group and seating corner to valid positions. |
| 7856 | 2 | relayout_room | r_L1_cocuk_odasi | acceptance: finding F7:f_L1_007 is still there after the edit (bed_double blocks door d_L1_011); 6 more kept | Re-solve layout to move bed f_L1_007 off door d_L1_011 and the room outline, and fix nightstand f_L1_008 group layout and clearances. |
| 7857 | 2 | move_piece | f_L0_037 | score: plausibility -272 -> -352 (F4 f_L0_038: chair does not face its group (f_L0_037); G6 f_L0_038: chair f_L0_038 is 75° off the table f_L0_037 (needs ≤ 45°); G11 o_L0_001: no 0.60 m walkway from door o_L0_001 to door d_L0_005; G11 o_L0_001: no 0.60 m walkway from door o_L0_001 to door d_L0_007) | Shift the dining table off the main circulation path between the kitchen and the entrance (v:r2-v2:1) and clear the door d_L0_003 walkway (c:G11:d_L0_003, c:G11:d_L0_003#2). |
| 7859 | 2 | move_piece | f_L1_014 | acceptance: finding F7:f_L1_014 is still there after the edit (wardrobe blocks door win_L1_008); 2 more kept | Shift wardrobe 0.05 m off wall w_L1_025 to clear the door swing, room outline collision and wall cut. |
| 7860 | 2 | move_group | r_L0_mutfak.dining | no_place: r_L0_mutfak.dining on span r_L0_mutfak.s3: no place passes the checks (dining: no candidate position fits the room) | Move the whole dining group (table + chairs) to the free wall span s3 so the table no longer blocks the main circulation path (v:r2-v2:1) and the door d_L0_003 walkway is restored (c:G11:d_L0_003, c:G11:d_L0_003#2). |
| 7862 | 2 | move_group | r_L0_mutfak.dining | no_place: r_L0_mutfak.dining on span r_L0_mutfak.s1: the places that pass the checks are elsewhere (candidate 1: table_dining at [5.25, 10.75]) | Move the whole dining group to the free wall span s1 (below the window) so the table no longer blocks the main circulation path (v:r2-v2:1) and the door d_L0_003 walkway is restored (c:G11:d_L0_003, c:G11:d_L0_003#2). |
| 7864 | 2 | move_group | r_L0_mutfak.dining | no_place: r_L0_mutfak.dining on span r_L0_mutfak.s1: the places that pass the checks are elsewhere (candidate 1: table_dining at [5.15, 9.85]; candidate 2: table_dining at [4.65, 10.75]) | Move the whole dining group to the free wall span s1 (below the window) so the table no longer blocks the main circulation path (v:r2-v2:1) and the door d_L0_003 walkway is restored (c:G11:d_L0_003, c:G11:d_L0_003#2). |
| 7867 | 2 | move_group | r_L0_mutfak.dining | max_tries: r_L0_mutfak.dining was edited 3 times in this round | Move the whole dining group to the free wall span s1 (below the window) so the table no longer blocks the main circulation path (v:r2-v2:1) and the door d_L0_003 walkway is restored (c:G11:d_L0_003, c:G11:d_L0_003#2). |
| 7869 | 2 | complete_group | r_L0_mutfak.dining | max_tries: r_L0_mutfak.dining was edited 3 times in this round | Add the missing third chair to the dining group (G6 minor: 2 of 3 chairs; a:N104: chair f_L0_039 left out). |
| 7875 | 2 | relayout_room | r_L1_hol | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 2 more kept | Re-place the entrance group with the best solver candidate to restore the 0.60 m walkways between doors d_L1_006, d_L1_009, o_L1_002 and the stair (G11 critical). |
| 7877 | 2 | relayout_room | r_L1_hol | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 2 more kept | Try the second solver candidate (best circulation 0.85) to restore the 0.60 m walkways between doors d_L1_006, d_L1_009, o_L1_002 and the stair (G11 critical). |
| 7880 | 2 | remove_piece | f_L1_034 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The entrance shoe cabinet blocks the 0.60 m walkways between doors d_L1_006, d_L1_009 and o_L1_002 (G11 critical); the entrance group is optional and the room is a tight 11 m² hall, so removing it restores the circulation. |
| 7887 | 2 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: hssd_ad635dc49d8e6113fffb33d691c948159b71fc56: fails the fit rules (caps, height, at most 2.38 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the stark glossy black box washbasin with a minimal modern white wash-basin that fits the 0.53x0.34 footprint and the monochromatic white room. |
| 7888 | 2 | swap_model | f_L0_026 | acceptance: pin_refused: f_L0_026: 3dwh_6154347ab8ff886fbcf80494: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the generic washbasin with a minimalist rectangle sink that fits the 0.53x0.34 footprint, addressing the wrong_model finding and the collision with the bathtub. |
| 7890 | 2 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: 3dwh_6154347ab8ff886fbcf80494: fails the fit rules (caps, height, at most 2.38 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the stark glossy black box washbasin with a minimalist rectangle sink (0.53x0.33, low profile) that fits the footprint and the white room. |
| 7892 | 2 | swap_model | f_L0_026 | acceptance: pin_refused: f_L0_026: hssd_62a760c87eede6f17cd28daa5e0ff4ed7510e02f: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the generic washbasin with a proper wash-basin model (0.448x0.448x0.466) that has standard height and design detail, addressing the wrong_model finding. |
| 7893 | 2 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: hssd_7b5d656c72b56ae0e8200132ec92a1ae03869b93: fails the fit rules (caps, height, at most 2.38 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the stark glossy black box washbasin with a minimal modern white sink (0.57x0.33) that fits the footprint and the white room. |
| 7894 | 2 | swap_model | f_L1_023 | max_tries: f_L1_023 was edited 3 times in this round | Replace the stark glossy black box washbasin with a minimal modern white wash-basin (0.45x0.45) that fits the footprint and the white room. |
| 7895 | 2 | set_camera | r_L1_oda | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-aim the dead-end hallway view to frame the entrance shoe cabinet so the room reads as furnished rather than an empty corridor. |
| 7896 | 2 | swap_model | f_L0_026 | no_change: f_L0_026 already uses the model hssd_4f1b086633e1b160f09b24a9aad0ec9d1ccb56c0 | Replace the generic washbasin with a Cooke & Lewis Lanzo Square Cloakroom Basin (0.449x0.322x0.469) with proper design detail and standard height. |
| 7898 | 2 | swap_model | f_L0_026 | max_tries: f_L0_026 was edited 3 times in this round | Replace the current washbasin with a ProCasa Cinque basin (0.498x0.399x0.540) with more design detail to address the generic-model finding. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F3 | minor | f_L1_025 | r_L1_oda_2 | - | drawn_layout | 1, 2 | the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall, and no free wall place (doors, windows, the other pieces) or partner lies within that reach, so no move clears the finding; the drawn layout is reported (CLAUDE.md: drawn furniture is kept) |
| F9 | major | f_L0_031 | r_L0_mutfak | - | drawn_layout | 1, 2 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| F9 | major | f_L0_032 | r_L0_mutfak | - | drawn_layout | 1, 2 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| G8 | minor | f_L0_020 | r_L0_mutfak | - | soft_minimum | 1, 2 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| Q3 | critical | d_L1_001 | - | architect | guard | 1, 2 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's glass guard); reported to the architect |
| RC | minor | sy_L0_002 | - | - | resolved_by_code | 1, 2 | a reading conflict the code already resolved (the drawing won, the item was moved to the symbols): it names no furniture piece or room, so there is nothing to edit; reported |
| S2 | major | f_L0_031 | r_L0_mutfak | - | drawn_layout | 1, 2 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| S2 | minor | f_L0_037 | r_L0_mutfak | - | within_tolerance | 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_011 | r_L1_soyunma_odasi | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L0_007 | r_L0_salon | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_016 | r_L0_salon | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_015 | r_L1_ebeveyn_y_odasi | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | critical | d_L1_001 | - | - | facade | 1, 2 | the facade openings come from the drawings; no agent tool |
| X3 | critical | d_L1_004 | - | - | facade | 1, 2 | the facade openings come from the drawings; no agent tool |
| X3 | critical | d_L1_005 | - | - | facade | 1, 2 | the facade openings come from the drawings; no agent tool |
| X3 | critical | d_L1_010 | - | - | facade | 1, 2 | the facade openings come from the drawings; no agent tool |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L0_salon | cut | 1 | 11163 | 32768 |
| 1 | building | cut | 1 | 18697 | 32768 |
| 2 | r_L0_mutfak | cut | 1 | 10303 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | change | by (rule) | reason |
|---|---|---|---|---|---|---|---|
| f_L0_001 | piece | stair | r_L0_mutfak | adjusted_by_ai | - | architect (architect K1) | a riser of 0.214 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L0_002 | piece | kitchen_counter | r_L0_mutfak | adjusted_by_ai | - | code (architect F5) | architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once |
| f_L0_003 | piece | kitchen_counter | r_L0_mutfak | inferred | - | - | drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_004 | piece | unknown | r_L0_mutfak | inferred, adjusted_by_ai | - | code (reading.kitchen_outline) | the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_005 | piece | unknown | r_L0_salon | inferred | - | - | outline 3.89 x 1.42 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L0_006 | piece | sofa | r_L0_salon | inferred | - | - | sofa: the living room misses its seating anchor (sofa); the living room misses its anchor (sofa \| sofa_corner), and the type's product range fits 2.12 x 0.78 m (the only missing member of that size) |
| f_L0_007 | piece | armchair | r_L0_salon | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_009 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside sofa f_L0_006 (2.12 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_010 | piece | bathtub | r_L0_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | type unknown -> bathtub; size 2.54 x 1.01 m -> 1.80 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | through a wall: moved 0.21 m to the nearest free spot; plan crop recognition/crops/sym_L0_005_ctx.png; then: bathtub front faces the open room (SE), away from the wall its head end is against |
| f_L0_011 | piece | table_dining | r_L0_salon | inferred, adjusted_by_ai | size 1.69 x 1.69 m -> 1.00 x 1.00 m | Qwen/Qwen3.8-27B-FP8 | Argus: The wooden bench (table_dining) is a third clashing style. Swapping to a scandinavian/japandi table matches the light minimalist room. (fixes a:F77) |
| f_L0_012 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_013 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_014 | piece | sofa | r_L0_salon | inferred | - | - | sofa: named by an AI pass and the only named type that fits the size (1.52 x 0.78 m), the living + other room and the position (others fitting: chaise, table_coffee) |
| f_L0_015 | piece | table_coffee | r_L0_salon | inferred | - | - | table_coffee: r_L0_salon misses it (r_L0_salon.seating (anchor f_L0_006) misses table_coffee) and the AI passes named it (pass 1 (qwen) answered table_coffee; pass 1 (qwen)'s reason names table_coffee); plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_016 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_017 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_018 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_019 | piece | armchair | r_L0_salon | inferred | - | - | armchair: the same drawn block (the same strokes (301 LINE here, within 2%)) and footprint (0.92 x 0.77 m, within 0.01 m) as f_L0_007, f_L0_016, f_L0_017, f_L0_018 (typed armchair): one block, one type; front: faces the coffee table f_L0_021 |
| f_L0_020 | piece | sink_kitchen | r_L0_mutfak | inferred | - | - | sink_kitchen: r_L0_mutfak.kitchen_run (anchor f_L0_002) misses sink_kitchen, and the type's product range fits 1.20 x 0.45 m (the only missing member of that size) |
| f_L0_021 | piece | table_coffee | r_L0_salon | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> table_coffee | code (ringed_table) | table_coffee: a drawn round floor_lamp (ai_two_pass) 0.66 m across with 4 seats around it (f_L0_016, f_L0_017, f_L0_018, f_L0_019) facing it: the table of the seating group, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png) |
| f_L0_024 | piece | toilet | r_L0_banyo | inferred | - | - | toilet: the same footprint (0.70 x 0.45 m) at the same plan position as f_L1_022 on level L1 (within 0.01 m) |
| f_L0_027 | piece | chair | r_L0_salon | inferred | - | - | a 0.45 x 0.32 m seat 0.00 m from the table f_L0_011, facing it |
| f_L0_028 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.04 m |
| f_L0_029 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.07 m |
| f_L0_030 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.08 m |
| f_L1_003 | piece | unknown | r_L1_hol | inferred | - | - | 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L1_004 | piece | bed_double | r_L1_cocuk_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The judge flags the bed and dresser as a mismatched set; swapping f_L1_004 to a minimal/modern/scandinavian bed matches the dresser's style. (fixes a:F87) |
| f_L1_005 | piece | dresser | r_L1_cocuk_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Snap the dresser's back onto the left wall (it was 0.06 m off) and shift it up the wall to clear the 0.07 m² overlap with bed f_L1_004 and the railing. |
| f_L1_006 | piece | unknown | r_L1_cocuk_odasi | inferred | - | - | drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L1_007 | piece | bed_double | r_L1_cocuk_odasi | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_008 | piece | nightstand | r_L1_cocuk_odasi | adjusted_by_ai | - | code (architect F5) | architect F5: it cut f_L1_007 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built |
| f_L1_009 | piece | bathtub | r_L1_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | type unknown -> bathtub; size 2.42 x 0.98 m -> 1.80 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | through a wall: moved 0.25 m to the nearest free spot; plan crop recognition/crops/sym_L1_006_ctx.png; then: Argus: The judge flags the bathtub as a basic 3D primitive; swapping to a classic/minimal/modern model with detail resolves the issue. (fixes a:F82) |
| f_L1_010 | piece | bed_double | r_L1_ebeveyn_y_odasi | inferred | - | - | bed_double: the bedroom room misses its sleeping_double anchor (bed_double); the bedroom room misses its anchor (bed_double \| bed_single), and the type's product range fits 1.90 x 1.50 m (the only missing member of that size) |
| f_L1_011 | piece | wardrobe | r_L1_soyunma_odasi | inferred, adjusted_by_ai | type unknown -> wardrobe; size 2.27 x 0.85 m -> 2.27 x 0.60 m | code (wardrobe_run) | wardrobe: r_L1_soyunma_odasi is a dressing room: its program puts wardrobe runs along its walls (groups.yaml dressing); the drawn 2.27 x 0.85 m stands with its long side on a wall, its length fits a wardrobe run (0.80-3.20 m) and its depth is a wardrobe's (0.55-0.90 m drawn); the depth is outside the wardrobe's range (0.50-0.70 m): 0.60 m, the back kept on its wall, drawn_footprint kept (CLAUDE.md: a real product size) |
| f_L1_012 | piece | wardrobe | r_L1_soyunma_odasi | inferred, adjusted_by_ai | type unknown -> wardrobe; size 2.27 x 0.85 m -> 2.27 x 0.60 m | code (wardrobe_run) | wardrobe: r_L1_soyunma_odasi is a dressing room: its program puts wardrobe runs along its walls (groups.yaml dressing); the drawn 2.27 x 0.85 m stands with its long side on a wall, its length fits a wardrobe run (0.80-3.20 m) and its depth is a wardrobe's (0.55-0.90 m drawn); the depth is outside the wardrobe's range (0.50-0.70 m): 0.60 m, the back kept on its wall, drawn_footprint kept (CLAUDE.md: a real product size) |
| f_L1_013 | piece | bed_single | r_L1_oda_2 | inferred | - | - | bed_single: the bedroom room misses its anchor (bed_double \| bed_single), and the type's product range fits 1.90 x 0.90 m (the only missing member of that size); front: standing in a corner: its short side on the wall is the back |
| f_L1_014 | piece | wardrobe | r_L1_oda_2 | inferred, adjusted_by_ai | - | architect | moved 0.39 m clear of win_L1_008 (the answer to F2:win_L1_008) |
| f_L1_017 | piece | dresser | r_L1_oda_2 | inferred | - | - | dresser: the documents name it: the text '*SIFONIYER' (TEXT:29ABD3) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.55 m within 40% |
| f_L1_018 | piece | shower | r_L1_dus | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_019 | piece | washing_machine | r_L1_banyo | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type washbasin -> washing_machine | code, then Qwen/Qwen3.8-27B-FP8 (name_text) | washing_machine: the documents name it: the text 'çamaşır mak.' (TEXT:2772EB) is written 0.01 m from it; the ai_two_pass reading said washbasin; the named type's product range fits 0.60 x 0.60 m and the room holds it (trust order: the documents' text before AI vision); plan crop recognition/crops/sym_L1_016_ctx.png; then: washing machine front faces a wall 0.00 m ahead; turn it to face into the room |
| f_L1_020 | piece | floor_lamp | r_L1_ebeveyn_y_odasi | inferred | - | - | floor_lamp: named by an AI pass and the only named type that fits the size (0.58 x 0.58 m), the bedroom room and the position (others fitting: armchair, ottoman, potted_plant, side_table) |
| f_L1_024 | piece | nightstand | r_L1_ebeveyn_y_odasi | inferred | - | - | nightstand: r_L1_ebeveyn_y_odasi.sleeping_double (anchor f_L1_010) misses nightstand; r_L1_ebeveyn_y_odasi.sleeping_double (anchor f_L1_010) misses nightstand, and the type's product range fits 0.42 x 0.40 m (the only missing member of that size) |
| f_L1_025 | piece | nightstand | r_L1_oda_2 | inferred | - | - | nightstand: the same drawn block (the same strokes (1 CIRCLE, 14 LINE here, within 2%)) and footprint (0.42 x 0.40 m, within 0.01 m) as f_L1_024 (typed nightstand): one block, one type; front: faces the way its bed f_L1_013 faces |
| f_L1_026 | piece | nightstand | r_L1_ebeveyn_y_odasi | inferred | - | - | nightstand: the same drawn block (the same strokes (1 CIRCLE, 14 LINE here, within 2%)) and footprint (0.42 x 0.40 m, within 0.01 m) as f_L1_024, f_L1_025 (typed nightstand): one block, one type; front: faces the way its bed f_L1_010 faces |
| f_L1_027 | piece | washbasin | r_L1_dus | inferred, adjusted_by_ai | - | code (reading.fixed_equipment) | misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026): through a wall: moved 0.05 m to the nearest free spot (plan crop recognition/crops/sym_L1_024_ctx.png) |
| f_L0_031 | piece | kitchen_counter | r_L0_mutfak | inferred, adjusted_by_ai | type unknown -> kitchen_counter; size 3.99 x 2.40 m -> 2.40 x 0.60 m | code (reading.kitchen_outline) | the kitchen run drawn as one 3.99 x 2.40 m outline f_L0_004 with its fixtures (sink: 8 circles) in the kitchen: a counter leg 2.40 x 0.60 m along its wall side, facing the room (inferred); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_032 | piece | kitchen_counter | r_L0_mutfak | inferred, adjusted_by_ai | type unknown -> kitchen_counter; size 3.99 x 2.40 m -> 2.40 x 0.60 m | code (reading.kitchen_outline) | the kitchen run drawn as one 3.99 x 2.40 m outline f_L0_004 with its fixtures (sink: 8 circles) in the kitchen: a counter leg 2.40 x 0.60 m along its wall side, facing the room (inferred); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L1_028 | piece | shoe_cabinet | r_L1_oda | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_028: the piece is not built |
| f_L0_034 | piece | bookshelf | r_L0_salon | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_034: the piece is not built |
| f_L0_035 | piece | potted_plant | r_L0_salon | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_035: the piece is not built |
| f_L0_036 | piece | stove | r_L0_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The stove is planned but missing from the scene. It was assigned a kitchen_counter module model which likely failed to build as a distinct object. Swapping to a dedicated stove model from the catalogue will ensure it is built. (fixes a:F18) |
| f_L0_038 | piece | chair | r_L0_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dark heavy wooden chair clashes with the light minimalist kitchen. Swapping to a modern/scandinavian chair matches the room's style. (fixes a:F70) |
| f_L0_039 | piece | chair | r_L0_mutfak | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_039: the piece is not built |
| f_L1_029 | piece | desk | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_029: the piece is not built |
| f_L1_030 | piece | office_chair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_030: the piece is not built |
| f_L1_034 | piece | shoe_cabinet | r_L1_hol | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_034: the piece is not built |
| f_L0_043 | piece | sofa | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (1 reference photos)) |
| f_L0_044 | piece | table_coffee | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (1 reference photos)) |
| f_L0_045 | piece | armchair | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (1 reference photos)) |
| f_L0_046 | piece | armchair | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (1 reference photos)) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_mutfak_1 | ![](agent/r1_cam_r_L0_mutfak_1_before.jpg) | ![](agent/r1_cam_r_L0_mutfak_1_after.jpg) |
| 1 | cam_r_L0_mutfak_2 | ![](agent/r1_cam_r_L0_mutfak_2_before.jpg) | ![](agent/r1_cam_r_L0_mutfak_2_after.jpg) |
| 1 | cam_r_L0_mutfak_3 | ![](agent/r1_cam_r_L0_mutfak_3_before.jpg) | ![](agent/r1_cam_r_L0_mutfak_3_after.jpg) |
| 1 | cam_r_L0_salon_1 | ![](agent/r1_cam_r_L0_salon_1_before.jpg) | ![](agent/r1_cam_r_L0_salon_1_after.jpg) |
| 1 | cam_r_L0_salon_2 | ![](agent/r1_cam_r_L0_salon_2_before.jpg) | ![](agent/r1_cam_r_L0_salon_2_after.jpg) |
| 1 | cam_r_L0_salon_3 | ![](agent/r1_cam_r_L0_salon_3_before.jpg) | ![](agent/r1_cam_r_L0_salon_3_after.jpg) |
| 1 | cam_r_L1_banyo_1 | ![](agent/r1_cam_r_L1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L1_banyo_1_after.jpg) |
| 1 | cam_r_L1_cocuk_odasi_1 | ![](agent/r1_cam_r_L1_cocuk_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_cocuk_odasi_1_after.jpg) |
| 1 | cam_r_L1_cocuk_odasi_2 | ![](agent/r1_cam_r_L1_cocuk_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_cocuk_odasi_2_after.jpg) |
| 1 | cam_r_L1_cocuk_odasi_3 | ![](agent/r1_cam_r_L1_cocuk_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_cocuk_odasi_3_after.jpg) |
| 1 | cam_r_L1_dus_1 | ![](agent/r1_cam_r_L1_dus_1_before.jpg) | ![](agent/r1_cam_r_L1_dus_1_after.jpg) |
| 1 | cam_r_L1_ebeveyn_y_odasi_1 | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_1_after.jpg) |
| 1 | cam_r_L1_ebeveyn_y_odasi_2 | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_2_after.jpg) |
| 1 | cam_r_L1_ebeveyn_y_odasi_3 | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_3_after.jpg) |
| 1 | cam_r_L1_hol_1 | ![](agent/r1_cam_r_L1_hol_1_before.jpg) | ![](agent/r1_cam_r_L1_hol_1_after.jpg) |
| 1 | cam_r_L1_oda_1 | ![](agent/r1_cam_r_L1_oda_1_before.jpg) | ![](agent/r1_cam_r_L1_oda_1_after.jpg) |
| 1 | cam_r_L1_oda_2_1 | ![](agent/r1_cam_r_L1_oda_2_1_before.jpg) | ![](agent/r1_cam_r_L1_oda_2_1_after.jpg) |
| 1 | cam_r_L1_oda_2_2 | ![](agent/r1_cam_r_L1_oda_2_2_before.jpg) | ![](agent/r1_cam_r_L1_oda_2_2_after.jpg) |
| 1 | cam_r_L1_oda_2_3 | ![](agent/r1_cam_r_L1_oda_2_3_before.jpg) | ![](agent/r1_cam_r_L1_oda_2_3_after.jpg) |
| 1 | cam_r_L1_soyunma_odasi_1 | ![](agent/r1_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 1 | cam_r_L1_soyunma_odasi_2 | ![](agent/r1_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 1 | ext_1 | ![](agent/r1_ext_1_before.jpg) | ![](agent/r1_ext_1_after.jpg) |
| 1 | ext_2 | ![](agent/r1_ext_2_before.jpg) | ![](agent/r1_ext_2_after.jpg) |
| 1 | ext_3 | ![](agent/r1_ext_3_before.jpg) | ![](agent/r1_ext_3_after.jpg) |
| 1 | ext_4 | ![](agent/r1_ext_4_before.jpg) | ![](agent/r1_ext_4_after.jpg) |
| 1 | ext_5 | ![](agent/r1_ext_5_before.jpg) | ![](agent/r1_ext_5_after.jpg) |
| 1 | ext_6 | ![](agent/r1_ext_6_before.jpg) | ![](agent/r1_ext_6_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- no brief.yaml in /workspace/repo/projects/real06: every brief value is a default
