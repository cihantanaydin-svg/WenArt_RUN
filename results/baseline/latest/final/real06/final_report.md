# Final report: real06

31 views: 19 polished, 12 Cycles (check_incomplete 1, gate 4, gate_validation 6, vision_check 1). Stages: render run, gate validation flagged, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 31 |
| interior / exterior views | 25 / 6 |
| variant | base |
| polished | 19 |
| Cycles | 12 (check_incomplete 1, gate 4, gate_validation 6, vision_check 1) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 10 |
| needs_review views | 8 |
| unverified pieces in view (sum over views) | 93 |
| rooms mixing polished and Cycles | 4 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.50 .. +1.17 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 26 view(s), -3 .. 0 EV |
| interior glazing pull | 4 view(s) with interior glazing, 0 pulled, 0 still clipped over 1.0 % |
| camera policy | agent 10, m5 6, search 15 |
| camera score (min / mean / max) | 2.46 / 4.38 / 5.60 |
| rooms by number of views | 1 with 0, 3 with 1, 3 with 2, 4 with 3, 1 with 4 |
| gate validation | flagged |
| seconds: build / render / metering | 4.0 min / 3.6 min / 83.3 s |
| seconds: polish / gate / check | 2.5 min / 14.1 s / 34.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 12 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real06.blend](3d/real06.blend) | 393.9 MB |
| [real06.glb](3d/real06.glb) | 705.8 MB |

31 cameras; textures scaled to at most 1024 px (165 scaled) for the download.

## AI decor

54 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 11 rooms; 5 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- gate validation flagged: polish ran; flagged: the gate also rejects some harmless edits, so more views may stay Cycles (benign controls accepted 0.938 < 0.95 (64 comparisons): the gate also rejects harmless edits)
- the polish added an object in cam_r_L1_ebeveyn_y_odasi_1: the Cycles render is final
- exterior gate polish_disabled: the exterior views are the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 6 piece(s) moved beyond the tolerance, 7 locked-rule violation(s)
- AI completion: 7 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | flagged |
| benign controls accepted | 93.8 % (limit 95 %), 64 comparisons |
| negative controls rejected | 92.6 % (limit 90 %), 176 comparisons |
| effect | polish ran; flagged: the gate also rejects some harmless edits, so more views may stay Cycles |

Reasons:

- benign controls accepted 0.938 < 0.95 (64 comparisons): the gate also rejects harmless edits

### Exterior views

Exterior decision: **polish_disabled**. The exterior views are the Cycles render; the rooms are not affected.

| item | value |
|---|---|
| benign exterior comparisons accepted | 91.7 % (limit 95 %), 24 comparisons |
| negative exterior comparisons rejected | 65.0 % (limit 90 %), 60 comparisons |

Reasons:

- benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits
- negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through

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
| r_L0_banyo | cam_r_L0_banyo_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L0_banyo | cam_r_L0_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_1 | a3 s 0.125 depth x0.8 | accept | info | info | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_2 | a3 s 0.125 depth x0.8 | accept | info | info | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_3 | - | - | info | - | - | cycles (gate) |
| r_L0_salon | cam_r_L0_salon_1 | - | - | info | - | - | cycles (gate) |
| r_L0_salon | cam_r_L0_salon_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_3 | a3 s 0.125 depth x0.8 | accept | info | info | calibrated | polished |
| r_L1_banyo | cam_r_L1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_L1_dresser_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_dus | cam_r_L1_dus_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_dus | cam_r_L1_dus_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_hol | cam_r_L1_hol_1 | - | - | info | - | - | cycles (gate) |
| r_L1_oda | cam_r_L1_oda_1 | - | - | info | - | - | cycles (gate) |
| r_L1_oda_2 | cam_r_L1_oda_2_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_oda_2 | cam_r_L1_oda_2_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | cycles (check_incomplete) |
| r_L1_oda_2 | cam_r_L1_oda_2_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_soyunma_odasi | cam_r_L1_soyunma_odasi_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_soyunma_odasi | cam_r_L1_soyunma_odasi_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_L1_dresser_1 | r_L1_cocuk_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.67 | -1 | agent | D6 A4 | 1 | yes | [preview](cam_L1_dresser_1_final_preview.jpg) [plan](cam_L1_dresser_1_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +0.00 | -2 | agent | D4 | 2 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.17 | -2 | agent | D4 | 2 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | info | info | not preferred 0/2 | +0.50 | -3 | search 4.91 | D6 A3 | 4 | yes | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | info | info | not preferred 0/2 | +0.17 | -2 | search 4.73 | D5 A4 | 3 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | gate | - | - | info | - | - | +0.67 | -3 | search 4.71 | D6 A2 | 3 | yes | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | gate | - | - | info | - | - | -0.17 | -2 | search 4.04 | D8 A4 | 5 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.17 | -2 | search 3.91 | D9 A3 | 4 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | info | info | not preferred 0/2 | -1.00 | -1 | search 3.79 | D12 A5 | 8 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.00 | -2 | search 4.88 | D5 A1 | 2 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.83 | -1 | agent | D6 A2 | 1 | yes | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.83 | -1 | agent | D6 A2 | 1 | yes | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/2 | -0.67 | -1 | search 5.31 | D4 A1 | 1 | yes | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_dus_1 | r_L1_dus | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.17 | - | agent | D2 | 0 | no | [preview](cam_r_L1_dus_1_final_preview.jpg) [plan](cam_r_L1_dus_1_plan.jpg) |
| cam_r_L1_dus_2 | r_L1_dus | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 1/2 | +0.17 | - | search 2.46 | D4 A1 | 1 | no | [preview](cam_r_L1_dus_2_final_preview.jpg) [plan](cam_r_L1_dus_2_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_1 | r_L1_ebeveyn_y_odasi | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | -0.50 | -1 | agent | D8 A2 | 4 | yes | [preview](cam_r_L1_ebeveyn_y_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_2 | r_L1_ebeveyn_y_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.50 | -1 | search 5.60 | D7 A3 | 4 | yes | [preview](cam_r_L1_ebeveyn_y_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_3 | r_L1_ebeveyn_y_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | -0.50 | -1 | search 5.10 | D6 A2 | 3 | no | [preview](cam_r_L1_ebeveyn_y_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | gate | - | - | info | - | - | +0.67 | -2 | search 2.75 | D8 A1 | 1 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_oda_1 | r_L1_oda | L1 | cycles | gate | - | - | info | - | - | +1.17 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L1_oda_1_final_preview.jpg) [plan](cam_r_L1_oda_1_plan.jpg) |
| cam_r_L1_oda_2_1 | r_L1_oda_2 | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +0.00 | -2 | search 5.24 | D5 A1 | 5 | no | [preview](cam_r_L1_oda_2_1_final_preview.jpg) [plan](cam_r_L1_oda_2_1_plan.jpg) |
| cam_r_L1_oda_2_2 | r_L1_oda_2 | L1 | cycles | check_incomplete | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | -0.50 | -1 | search 4.39 | D4 A1 | 4 | no | [preview](cam_r_L1_oda_2_2_final_preview.jpg) [plan](cam_r_L1_oda_2_2_plan.jpg) |
| cam_r_L1_oda_2_3 | r_L1_oda_2 | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.00 | -2 | search 3.94 | D4 A1 | 4 | no | [preview](cam_r_L1_oda_2_3_final_preview.jpg) [plan](cam_r_L1_oda_2_3_plan.jpg) |
| cam_r_L1_soyunma_odasi_1 | r_L1_soyunma_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.33 | - | agent | D5 | 2 | no | [preview](cam_r_L1_soyunma_odasi_1_final_preview.jpg) [plan](cam_r_L1_soyunma_odasi_1_plan.jpg) |
| cam_r_L1_soyunma_odasi_2 | r_L1_soyunma_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +0.33 | - | agent | D5 | 2 | no | [preview](cam_r_L1_soyunma_odasi_2_final_preview.jpg) [plan](cam_r_L1_soyunma_odasi_2_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D12 | 5 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.83 | 0 | m5 | D18 | 8 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D17 | 6 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.50 | 0 | m5 | D12 | 1 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.33 | 0 | m5 | D16 | 6 | no | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.67 | 0 | m5 | D5 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_banyo | bathroom | L0 | 2 | 2 | 0 | cam_r_L0_banyo_1, cam_r_L0_banyo_2 |
| r_L0_mutfak | kitchen | L0 | 3 | 2 | 1 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_oda | other | L0 | 0 | 0 | 0 | - |
| r_L0_salon | living | L0 | 3 | 2 | 1 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L1_banyo | bathroom | L1 | 1 | 1 | 0 | cam_r_L1_banyo_1 |
| r_L1_cocuk_odasi | bedroom | L1 | 4 | 4 | 0 | cam_L1_dresser_1, cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_dus | bathroom | L1 | 2 | 2 | 0 | cam_r_L1_dus_1, cam_r_L1_dus_2 |
| r_L1_ebeveyn_y_odasi | bedroom | L1 | 3 | 2 | 1 | cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_2, cam_r_L1_ebeveyn_y_odasi_3 |
| r_L1_hol | hall | L1 | 1 | 0 | 1 | cam_r_L1_hol_1 |
| r_L1_oda | hall | L1 | 1 | 0 | 1 | cam_r_L1_oda_1 |
| r_L1_oda_2 | bedroom | L1 | 3 | 2 | 1 | cam_r_L1_oda_2_1, cam_r_L1_oda_2_2, cam_r_L1_oda_2_3 |
| r_L1_soyunma_odasi | storage | L1 | 2 | 2 | 0 | cam_r_L1_soyunma_odasi_1, cam_r_L1_soyunma_odasi_2 |

Rooms without a rendered view: r_L0_oda (no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)).

### Why Cycles

- cam_r_L0_mutfak_3: gate: no ladder attempt passed the gate: a1 reject (edges, neutral); a2 reject (neutral); a3 reject (neutral)
- cam_r_L0_salon_1: gate: no ladder attempt passed the gate: a1 reject (masks); a2 reject (masks); a3 reject (masks)
- cam_r_L1_ebeveyn_y_odasi_1: vision_check: added_by_polish furniture at [1216.4, 28.5, 1278.0, 228.8]
- cam_r_L1_hol_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth, edges, masks); a3 reject (masks)
- cam_r_L1_oda_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L1_oda_2_2: check_incomplete: Cycles image: unreliable pass (agent saw the decoy)
- ext_1: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_2: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_3: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_4: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_5: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_6: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_L1_dresser_1 | cycles | cross-check misplaced | f_L1_007 | bed_double | - | from_documents | real06.dwg ARC:297260-297261,ARC:297270,ARC:297306,LINE:297267-297269,LINE:297271-297305,LINE:297307-297761,ARC:29725B,ARC:29725E,ARC:29725F,ARC:29726F,ARC:29735D,LINE:293E9B,LINE:29726A,LINE:29726B,LINE:29726C,LINE:29726D,LINE:29726E,LINE:29727A,LINE:29727B,LINE:29727C,LINE:29727D,LINE:29727E,LINE:29727F,LINE:29728A,LINE:29728B,LINE:29728C,LINE:29728D,LINE:29728E,LINE:29728F,LINE:29729A,LINE:29729B,LINE:29729C,LINE:29729D,LINE:29729E,LINE:29729F,LINE:2972A0,LINE:2972A1,LINE:2972A2,LINE:2972A3,LINE:2972A4,LINE:2972A5,LINE:2972A6,LINE:2972A7,LINE:2972A8,LINE:2972A9,LINE:2972AA,LINE:2972AB,LINE:2972AC,LINE:2972AD,LINE:2972AE,LINE:2972AF,LINE:2972B0,LINE:2972B1,LINE:2972B2,LINE:2972B3,LINE:2972B4,LINE:2972B5,LINE:2972B6,LINE:2972B7,LINE:2972B8,LINE:2972B9,LINE:2972BA,LINE:2972BB,LINE:2972BC,LINE:2972BD,LINE:2972BE,LINE:2972BF,LINE:2972C0,LINE:2972C1,LINE:2972C2,LINE:2972C3,LINE:2972C4,LINE:2972C5,LINE:2972C6,LINE:2972C7,LINE:2972C8,LINE:2972C9,LINE:2972CA,LINE:2972CB,LINE:2972CC,LINE:2972CD,LINE:2972CE,LINE:2972CF,LINE:2972D0,LINE:2972D1,LINE:2972D2,LINE:2972D3,LINE:2972D4,LINE:2972D5,LINE:2972D6,LINE:2972D7,LINE:2972D8,LINE:2972D9,LINE:2972DA,LINE:2972DB,LINE:2972DC,LINE:2972DD,LINE:2972DE,LINE:2972DF,LINE:2972E0,LINE:2972E1,LINE:2972E2,LINE:2972E3,LINE:2972E4,LINE:2972E5,LINE:2972E6,LINE:2972E7,LINE:2972E8,LINE:2972E9,LINE:2972EA,LINE:2972EB,LINE:2972EC,LINE:2972ED,LINE:2972EE,LINE:2972EF,LINE:2972F0,LINE:2972F1,LINE:2972F2,LINE:2972F3,LINE:2972F4,LINE:2972F5,LINE:2972F6,LINE:2972F7,LINE:2972F8,LINE:2972F9,LINE:2972FA,LINE:2972FB,LINE:2972FC,LINE:2972FD,LINE:2972FE,LINE:2972FF,LINE:29730A,LINE:29730B,LINE:29730C,LINE:29730D,LINE:29730E,LINE:29730F,LINE:29731A,LINE:29731B,LINE:29731C,LINE:29731D,LINE:29731E,LINE:29731F,LINE:29732A,LINE:29732B,LINE:29732C,LINE:29732D,LINE:29732E,LINE:29732F,LINE:29733A,LINE:29733B,LINE:29733C,LINE:29733D,LINE:29733E,LINE:29733F,LINE:29734A,LINE:29734B,LINE:29734C,LINE:29734D,LINE:29734E,LINE:29734F,LINE:29735A,LINE:29735B,LINE:29735C,LINE:29735E,LINE:29736A,LINE:29736B,LINE:29736C,LINE:29736D,LINE:29736E,LINE:29736F,LINE:29737A,LINE:29737B,LINE:29737C,LINE:29737D,LINE:29737E,LINE:29737F,LINE:29738A,LINE:29738B,LINE:29738C,LINE:29738D,LINE:29738E,LINE:29738F,LINE:29739A,LINE:29739B,LINE:29739C,LINE:29739D,LINE:29739E,LINE:29739F,LINE:2973A0,LINE:2973A1,LINE:2973A2,LINE:2973A3,LINE:2973A4,LINE:2973A5,LINE:2973A6,LINE:2973A7,LINE:2973A8,LINE:2973A9,LINE:2973AA,LINE:2973AB,LINE:2973AC,LINE:2973AD,LINE:2973AE,LINE:2973AF,LINE:2973B0,LINE:2973B1,LINE:2973B2,LINE:2973B3,LINE:2973B4,LINE:2973B5,LINE:2973B6,LINE:2973B7,LINE:2973B8,LINE:2973B9,LINE:2973BA,LINE:2973BB,LINE:2973BC,LINE:2973BD,LINE:2973BE,LINE:2973BF,LINE:2973C0,LINE:2973C1,LINE:2973C2,LINE:2973C3,LINE:2973C4,LINE:2973C5,LINE:2973C6,LINE:2973C7,LINE:2973C8,LINE:2973C9,LINE:2973CA,LINE:2973CB,LINE:2973CC,LINE:2973CD,LINE:2973CE,LINE:2973CF,LINE:2973D0,LINE:2973D1,LINE:2973D2,LINE:2973D3,LINE:2973D4,LINE:2973D5,LINE:2973D6,LINE:2973D7,LINE:2973D8,LINE:2973D9,LINE:2973DA,LINE:2973DB,LINE:2973DC,LINE:2973DD,LINE:2973DE,LINE:2973DF,LINE:2973E0,LINE:2973E1,LINE:2973E2,LINE:2973E3,LINE:2973E4,LINE:2973E5,LINE:2973E6,LINE:2973E7,LINE:2973E8,LINE:2973E9,LINE:2973EA,LINE:2973EB,LINE:2973EC,LINE:2973ED,LINE:2973EE,LINE:2973EF,LINE:2973F0,LINE:2973F1,LINE:2973F2,LINE:2973F3,LINE:2973F4,LINE:2973F5,LINE:2973F6,LINE:2973F7,LINE:2973F8,LINE:2973F9,LINE:2973FA,LINE:2973FB,LINE:2973FC,LINE:2973FD,LINE:2973FE,LINE:2973FF,LINE:29740A,LINE:29740B,LINE:29740C,LINE:29740D,LINE:29740E,LINE:29740F,LINE:29741A,LINE:29741B,LINE:29741C,LINE:29741D,LINE:29741E,LINE:29741F,LINE:29742A,LINE:29742B,LINE:29742C,LINE:29742D,LINE:29742E,LINE:29742F,LINE:29743A,LINE:29743B,LINE:29743C,LINE:29743D,LINE:29743E,LINE:29743F,LINE:29744A,LINE:29744B,LINE:29744C,LINE:29744D,LINE:29744E,LINE:29744F,LINE:29745A,LINE:29745B,LINE:29745C,LINE:29745D,LINE:29745E,LINE:29745F,LINE:29746A,LINE:29746B,LINE:29746C,LINE:29746D,LINE:29746E,LINE:29746F,LINE:29747A,LINE:29747B,LINE:29747C,LINE:29747D,LINE:29747E,LINE:29747F,LINE:29748A,LINE:29748B,LINE:29748C,LINE:29748D,LINE:29748E,LINE:29748F,LINE:29749A,LINE:29749B,LINE:29749C,LINE:29749D,LINE:29749E,LINE:29749F,LINE:2974A0,LINE:2974A1,LINE:2974A2,LINE:2974A3,LINE:2974A4,LINE:2974A5,LINE:2974A6,LINE:2974A7,LINE:2974A8,LINE:2974A9,LINE:2974AA,LINE:2974AB,LINE:2974AC,LINE:2974AD,LINE:2974AE,LINE:2974AF,LINE:2974B0,LINE:2974B1,LINE:2974B2,LINE:2974B3,LINE:2974B4,LINE:2974B5,LINE:2974B6,LINE:2974B7,LINE:2974B8,LINE:2974B9,LINE:2974BA,LINE:2974BB,LINE:2974BC,LINE:2974BD,LINE:2974BE,LINE:2974BF,LINE:2974C0,LINE:2974C1,LINE:2974C2,LINE:2974C3,LINE:2974C4,LINE:2974C5,LINE:2974C6,LINE:2974C7,LINE:2974C8,LINE:2974C9,LINE:2974CA,LINE:2974CB,LINE:2974CC,LINE:2974CD,LINE:2974CE,LINE:2974CF,LINE:2974D0,LINE:2974D1,LINE:2974D2,LINE:2974D3,LINE:2974D4,LINE:2974D5,LINE:2974D6,LINE:2974D7,LINE:2974D8,LINE:2974D9,LINE:2974DA,LINE:2974DB,LINE:2974DC,LINE:2974DD,LINE:2974DE,LINE:2974DF,LINE:2974E0,LINE:2974E1,LINE:2974E2,LINE:2974E3,LINE:2974E4,LINE:2974E5,LINE:2974E6,LINE:2974E7,LINE:2974E8,LINE:2974E9,LINE:2974EA,LINE:2974EB,LINE:2974EC,LINE:2974ED,LINE:2974EE,LINE:2974EF,LINE:2974F0,LINE:2974F1,LINE:2974F2,LINE:2974F3,LINE:2974F4,LINE:2974F5,LINE:2974F6,LINE:2974F7,LINE:2974F8,LINE:2974F9,LINE:2974FA,LINE:2974FB,LINE:2974FC,LINE:2974FD,LINE:2974FE,LINE:2974FF,LINE:29750A,LINE:29750B,LINE:29750C,LINE:29750D,LINE:29750E,LINE:29750F,LINE:29751A,LINE:29751B,LINE:29751C,LINE:29751D,LINE:29751E,LINE:29751F,LINE:29752A,LINE:29752B,LINE:29752C,LINE:29752D,LINE:29752E,LINE:29752F,LINE:29753A,LINE:29753B,LINE:29753C,LINE:29753D,LINE:29753E,LINE:29753F,LINE:29754A,LINE:29754B,LINE:29754C,LINE:29754D,LINE:29754E,LINE:29754F,LINE:29755A,LINE:29755B,LINE:29755C,LINE:29755D,LINE:29755E,LINE:29755F,LINE:29756A,LINE:29756B,LINE:29756C,LINE:29756D,LINE:29756E,LINE:29756F,LINE:29757A,LINE:29757B,LINE:29757C,LINE:29757D,LINE:29757E,LINE:29757F,LINE:29758A,LINE:29758B,LINE:29758C,LINE:29758D,LINE:29758E,LINE:29758F,LINE:29759A,LINE:29759B,LINE:29759C,LINE:29759D,LINE:29759E,LINE:29759F,LINE:2975A0,LINE:2975A1,LINE:2975A2,LINE:2975A3,LINE:2975A4,LINE:2975A5,LINE:2975A6,LINE:2975A7,LINE:2975A8,LINE:2975A9,LINE:2975AA,LINE:2975AB,LINE:2975AC,LINE:2975AD,LINE:2975AE,LINE:2975AF,LINE:2975B0,LINE:2975B1,LINE:2975B2,LINE:2975B3,LINE:2975B4,LINE:2975B5,LINE:2975B6,LINE:2975B7,LINE:2975B8,LINE:2975B9,LINE:2975BA,LINE:2975BB,LINE:2975BC,LINE:2975BD,LINE:2975BE,LINE:2975BF,LINE:2975C0,LINE:2975C1,LINE:2975C2,LINE:2975C3,LINE:2975C4,LINE:2975C5,LINE:2975C6,LINE:2975C7,LINE:2975C8,LINE:2975C9,LINE:2975CA,LINE:2975CB,LINE:2975CC,LINE:2975CD,LINE:2975CE,LINE:2975CF,LINE:2975D0,LINE:2975D1,LINE:2975D2,LINE:2975D3,LINE:2975D4,LINE:2975D5,LINE:2975D6,LINE:2975D7,LINE:2975D8,LINE:2975D9,LINE:2975DA,LINE:2975DB,LINE:2975DC,LINE:2975DD,LINE:2975DE,LINE:2975DF,LINE:2975E0,LINE:2975E1,LINE:2975E2,LINE:2975E3,LINE:2975E4,LINE:2975E5,LINE:2975E6,LINE:2975E7,LINE:2975E8,LINE:2975E9,LINE:2975EA,LINE:2975EB,LINE:2975EC,LINE:2975ED,LINE:2975EE,LINE:2975EF,LINE:2975F0,LINE:2975F1,LINE:2975F2,LINE:2975F3,LINE:2975F4,LINE:2975F5,LINE:2975F6,LINE:2975F7,LINE:2975F8,LINE:2975F9,LINE:2975FA,LINE:2975FB,LINE:2975FC,LINE:2975FD,LINE:2975FE,LINE:2975FF,LINE:29760A,LINE:29760B,LINE:29760C,LINE:29760D,LINE:29760E,LINE:29760F,LINE:29761A,LINE:29761B,LINE:29761C,LINE:29761D,LINE:29761E,LINE:29761F,LINE:29762A,LINE:29762B,LINE:29762C,LINE:29762D,LINE:29762E,LINE:29762F,LINE:29763A,LINE:29763B,LINE:29763C,LINE:29763D,LINE:29763E,LINE:29763F,LINE:29764A,LINE:29764B,LINE:29764C,LINE:29764D,LINE:29764E,LINE:29764F,LINE:29765A,LINE:29765B,LINE:29765C,LINE:29765D,LINE:29765E,LINE:29765F,LINE:29766A,LINE:29766B,LINE:29766C,LINE:29766D,LINE:29766E,LINE:29766F,LINE:29767A,LINE:29767B,LINE:29767C,LINE:29767D,LINE:29767E,LINE:29767F,LINE:29768A,LINE:29768B,LINE:29768C,LINE:29768D,LINE:29768E,LINE:29768F,LINE:29769A,LINE:29769B,LINE:29769C,LINE:29769D,LINE:29769E,LINE:29769F,LINE:2976A0,LINE:2976A1,LINE:2976A2,LINE:2976A3,LINE:2976A4,LINE:2976A5,LINE:2976A6,LINE:2976A7,LINE:2976A8,LINE:2976A9,LINE:2976AA,LINE:2976AB,LINE:2976AC,LINE:2976AD,LINE:2976AE,LINE:2976AF,LINE:2976B0,LINE:2976B1,LINE:2976B2,LINE:2976B3,LINE:2976B4,LINE:2976B5,LINE:2976B6,LINE:2976B7,LINE:2976B8,LINE:2976B9,LINE:2976BA,LINE:2976BB,LINE:2976BC,LINE:2976BD,LINE:2976BE,LINE:2976BF,LINE:2976C0,LINE:2976C1,LINE:2976C2,LINE:2976C3,LINE:2976C4,LINE:2976C5,LINE:2976C6,LINE:2976C7,LINE:2976C8,LINE:2976C9,LINE:2976CA,LINE:2976CB,LINE:2976CC,LINE:2976CD,LINE:2976CE,LINE:2976CF,LINE:2976D0,LINE:2976D1,LINE:2976D2,LINE:2976D3,LINE:2976D4,LINE:2976D5,LINE:2976D6,LINE:2976D7,LINE:2976D8,LINE:2976D9,LINE:2976DA,LINE:2976DB,LINE:2976DC,LINE:2976DD,LINE:2976DE,LINE:2976DF,LINE:2976E0,LINE:2976E1,LINE:2976E2,LINE:2976E3,LINE:2976E4,LINE:2976E5,LINE:2976E6,LINE:2976E7,LINE:2976E8,LINE:2976E9,LINE:2976EA,LINE:2976EB,LINE:2976EC,LINE:2976F2,LINE:2976F3,LINE:2976F4,LINE:2976F5,LINE:2976F6,LINE:2976F7,LINE:2976F8,LINE:2976F9,LINE:2976FA,LINE:2976FB,LINE:2976FC,LINE:2976FD,LINE:2976FE,LINE:2976FF,LINE:29770A,LINE:29770B,LINE:29770C,LINE:29770D,LINE:29770E,LINE:29770F,LINE:29771A,LINE:29771B,LINE:29771C,LINE:29771D,LINE:29771E,LINE:29771F,LINE:29772A,LINE:29772B,LINE:29772C,LINE:29772D,LINE:29772E,LINE:29772F,LINE:29773A,LINE:29773B,LINE:29773C,LINE:29773D,LINE:29773E,LINE:29773F,LINE:29774A,LINE:29774B,LINE:29774C,LINE:29774D,LINE:29774E,LINE:29774F,LINE:29775A,LINE:29775B,LINE:29775C,LINE:29775D,LINE:29775E,LINE:29775F vector 0.90; real06.dwg recognition:sym_L1_004 ai 0.95; +2 more | yes | 22 % of its pixels > 0.10 m outside the drawing, 119120 px |
| cam_r_L0_mutfak_1 | cycles | cross-check in_json_not_rendered | o_L0_001 | window | - | from_documents | real06.dwg gap:LINE:294815,LINE:294819,LINE:2947C5,LINE:2947C9 derived 0.50; orchestrator/architect_answers.json inferred 0.60 | yes | visible 0.79, area 0.187 |
| cam_r_L0_mutfak_1 | cycles | cross-check in_json_not_rendered | d_L0_002 | window | - | from_documents | real06.dwg LINE:2574F5,LINE:2574F7,LINE:2574F6,LINE:2574FF,LINE:2574FE,LINE:2574FD vector 0.85; orchestrator/architect_answers.json inferred 0.60; +3 more | yes | visible 0.88, area 0.116 |
| cam_r_L0_mutfak_3 | cycles | cross-check in_json_not_rendered | o_L0_001 | window | - | from_documents | real06.dwg gap:LINE:294815,LINE:294819,LINE:2947C5,LINE:2947C9 derived 0.50; orchestrator/architect_answers.json inferred 0.60 | yes | visible 0.78, area 0.149 |
| cam_r_L0_mutfak_3 | cycles | cross-check in_json_not_rendered | d_L0_002 | window | - | from_documents | real06.dwg LINE:2574F5,LINE:2574F7,LINE:2574F6,LINE:2574FF,LINE:2574FE,LINE:2574FD vector 0.85; orchestrator/architect_answers.json inferred 0.60; +3 more | yes | visible 0.85, area 0.102 |
| cam_r_L1_cocuk_odasi_1 | cycles | cross-check misplaced | f_L1_007 | bed_double | - | from_documents | real06.dwg ARC:297260-297261,ARC:297270,ARC:297306,LINE:297267-297269,LINE:297271-297305,LINE:297307-297761,ARC:29725B,ARC:29725E,ARC:29725F,ARC:29726F,ARC:29735D,LINE:293E9B,LINE:29726A,LINE:29726B,LINE:29726C,LINE:29726D,LINE:29726E,LINE:29727A,LINE:29727B,LINE:29727C,LINE:29727D,LINE:29727E,LINE:29727F,LINE:29728A,LINE:29728B,LINE:29728C,LINE:29728D,LINE:29728E,LINE:29728F,LINE:29729A,LINE:29729B,LINE:29729C,LINE:29729D,LINE:29729E,LINE:29729F,LINE:2972A0,LINE:2972A1,LINE:2972A2,LINE:2972A3,LINE:2972A4,LINE:2972A5,LINE:2972A6,LINE:2972A7,LINE:2972A8,LINE:2972A9,LINE:2972AA,LINE:2972AB,LINE:2972AC,LINE:2972AD,LINE:2972AE,LINE:2972AF,LINE:2972B0,LINE:2972B1,LINE:2972B2,LINE:2972B3,LINE:2972B4,LINE:2972B5,LINE:2972B6,LINE:2972B7,LINE:2972B8,LINE:2972B9,LINE:2972BA,LINE:2972BB,LINE:2972BC,LINE:2972BD,LINE:2972BE,LINE:2972BF,LINE:2972C0,LINE:2972C1,LINE:2972C2,LINE:2972C3,LINE:2972C4,LINE:2972C5,LINE:2972C6,LINE:2972C7,LINE:2972C8,LINE:2972C9,LINE:2972CA,LINE:2972CB,LINE:2972CC,LINE:2972CD,LINE:2972CE,LINE:2972CF,LINE:2972D0,LINE:2972D1,LINE:2972D2,LINE:2972D3,LINE:2972D4,LINE:2972D5,LINE:2972D6,LINE:2972D7,LINE:2972D8,LINE:2972D9,LINE:2972DA,LINE:2972DB,LINE:2972DC,LINE:2972DD,LINE:2972DE,LINE:2972DF,LINE:2972E0,LINE:2972E1,LINE:2972E2,LINE:2972E3,LINE:2972E4,LINE:2972E5,LINE:2972E6,LINE:2972E7,LINE:2972E8,LINE:2972E9,LINE:2972EA,LINE:2972EB,LINE:2972EC,LINE:2972ED,LINE:2972EE,LINE:2972EF,LINE:2972F0,LINE:2972F1,LINE:2972F2,LINE:2972F3,LINE:2972F4,LINE:2972F5,LINE:2972F6,LINE:2972F7,LINE:2972F8,LINE:2972F9,LINE:2972FA,LINE:2972FB,LINE:2972FC,LINE:2972FD,LINE:2972FE,LINE:2972FF,LINE:29730A,LINE:29730B,LINE:29730C,LINE:29730D,LINE:29730E,LINE:29730F,LINE:29731A,LINE:29731B,LINE:29731C,LINE:29731D,LINE:29731E,LINE:29731F,LINE:29732A,LINE:29732B,LINE:29732C,LINE:29732D,LINE:29732E,LINE:29732F,LINE:29733A,LINE:29733B,LINE:29733C,LINE:29733D,LINE:29733E,LINE:29733F,LINE:29734A,LINE:29734B,LINE:29734C,LINE:29734D,LINE:29734E,LINE:29734F,LINE:29735A,LINE:29735B,LINE:29735C,LINE:29735E,LINE:29736A,LINE:29736B,LINE:29736C,LINE:29736D,LINE:29736E,LINE:29736F,LINE:29737A,LINE:29737B,LINE:29737C,LINE:29737D,LINE:29737E,LINE:29737F,LINE:29738A,LINE:29738B,LINE:29738C,LINE:29738D,LINE:29738E,LINE:29738F,LINE:29739A,LINE:29739B,LINE:29739C,LINE:29739D,LINE:29739E,LINE:29739F,LINE:2973A0,LINE:2973A1,LINE:2973A2,LINE:2973A3,LINE:2973A4,LINE:2973A5,LINE:2973A6,LINE:2973A7,LINE:2973A8,LINE:2973A9,LINE:2973AA,LINE:2973AB,LINE:2973AC,LINE:2973AD,LINE:2973AE,LINE:2973AF,LINE:2973B0,LINE:2973B1,LINE:2973B2,LINE:2973B3,LINE:2973B4,LINE:2973B5,LINE:2973B6,LINE:2973B7,LINE:2973B8,LINE:2973B9,LINE:2973BA,LINE:2973BB,LINE:2973BC,LINE:2973BD,LINE:2973BE,LINE:2973BF,LINE:2973C0,LINE:2973C1,LINE:2973C2,LINE:2973C3,LINE:2973C4,LINE:2973C5,LINE:2973C6,LINE:2973C7,LINE:2973C8,LINE:2973C9,LINE:2973CA,LINE:2973CB,LINE:2973CC,LINE:2973CD,LINE:2973CE,LINE:2973CF,LINE:2973D0,LINE:2973D1,LINE:2973D2,LINE:2973D3,LINE:2973D4,LINE:2973D5,LINE:2973D6,LINE:2973D7,LINE:2973D8,LINE:2973D9,LINE:2973DA,LINE:2973DB,LINE:2973DC,LINE:2973DD,LINE:2973DE,LINE:2973DF,LINE:2973E0,LINE:2973E1,LINE:2973E2,LINE:2973E3,LINE:2973E4,LINE:2973E5,LINE:2973E6,LINE:2973E7,LINE:2973E8,LINE:2973E9,LINE:2973EA,LINE:2973EB,LINE:2973EC,LINE:2973ED,LINE:2973EE,LINE:2973EF,LINE:2973F0,LINE:2973F1,LINE:2973F2,LINE:2973F3,LINE:2973F4,LINE:2973F5,LINE:2973F6,LINE:2973F7,LINE:2973F8,LINE:2973F9,LINE:2973FA,LINE:2973FB,LINE:2973FC,LINE:2973FD,LINE:2973FE,LINE:2973FF,LINE:29740A,LINE:29740B,LINE:29740C,LINE:29740D,LINE:29740E,LINE:29740F,LINE:29741A,LINE:29741B,LINE:29741C,LINE:29741D,LINE:29741E,LINE:29741F,LINE:29742A,LINE:29742B,LINE:29742C,LINE:29742D,LINE:29742E,LINE:29742F,LINE:29743A,LINE:29743B,LINE:29743C,LINE:29743D,LINE:29743E,LINE:29743F,LINE:29744A,LINE:29744B,LINE:29744C,LINE:29744D,LINE:29744E,LINE:29744F,LINE:29745A,LINE:29745B,LINE:29745C,LINE:29745D,LINE:29745E,LINE:29745F,LINE:29746A,LINE:29746B,LINE:29746C,LINE:29746D,LINE:29746E,LINE:29746F,LINE:29747A,LINE:29747B,LINE:29747C,LINE:29747D,LINE:29747E,LINE:29747F,LINE:29748A,LINE:29748B,LINE:29748C,LINE:29748D,LINE:29748E,LINE:29748F,LINE:29749A,LINE:29749B,LINE:29749C,LINE:29749D,LINE:29749E,LINE:29749F,LINE:2974A0,LINE:2974A1,LINE:2974A2,LINE:2974A3,LINE:2974A4,LINE:2974A5,LINE:2974A6,LINE:2974A7,LINE:2974A8,LINE:2974A9,LINE:2974AA,LINE:2974AB,LINE:2974AC,LINE:2974AD,LINE:2974AE,LINE:2974AF,LINE:2974B0,LINE:2974B1,LINE:2974B2,LINE:2974B3,LINE:2974B4,LINE:2974B5,LINE:2974B6,LINE:2974B7,LINE:2974B8,LINE:2974B9,LINE:2974BA,LINE:2974BB,LINE:2974BC,LINE:2974BD,LINE:2974BE,LINE:2974BF,LINE:2974C0,LINE:2974C1,LINE:2974C2,LINE:2974C3,LINE:2974C4,LINE:2974C5,LINE:2974C6,LINE:2974C7,LINE:2974C8,LINE:2974C9,LINE:2974CA,LINE:2974CB,LINE:2974CC,LINE:2974CD,LINE:2974CE,LINE:2974CF,LINE:2974D0,LINE:2974D1,LINE:2974D2,LINE:2974D3,LINE:2974D4,LINE:2974D5,LINE:2974D6,LINE:2974D7,LINE:2974D8,LINE:2974D9,LINE:2974DA,LINE:2974DB,LINE:2974DC,LINE:2974DD,LINE:2974DE,LINE:2974DF,LINE:2974E0,LINE:2974E1,LINE:2974E2,LINE:2974E3,LINE:2974E4,LINE:2974E5,LINE:2974E6,LINE:2974E7,LINE:2974E8,LINE:2974E9,LINE:2974EA,LINE:2974EB,LINE:2974EC,LINE:2974ED,LINE:2974EE,LINE:2974EF,LINE:2974F0,LINE:2974F1,LINE:2974F2,LINE:2974F3,LINE:2974F4,LINE:2974F5,LINE:2974F6,LINE:2974F7,LINE:2974F8,LINE:2974F9,LINE:2974FA,LINE:2974FB,LINE:2974FC,LINE:2974FD,LINE:2974FE,LINE:2974FF,LINE:29750A,LINE:29750B,LINE:29750C,LINE:29750D,LINE:29750E,LINE:29750F,LINE:29751A,LINE:29751B,LINE:29751C,LINE:29751D,LINE:29751E,LINE:29751F,LINE:29752A,LINE:29752B,LINE:29752C,LINE:29752D,LINE:29752E,LINE:29752F,LINE:29753A,LINE:29753B,LINE:29753C,LINE:29753D,LINE:29753E,LINE:29753F,LINE:29754A,LINE:29754B,LINE:29754C,LINE:29754D,LINE:29754E,LINE:29754F,LINE:29755A,LINE:29755B,LINE:29755C,LINE:29755D,LINE:29755E,LINE:29755F,LINE:29756A,LINE:29756B,LINE:29756C,LINE:29756D,LINE:29756E,LINE:29756F,LINE:29757A,LINE:29757B,LINE:29757C,LINE:29757D,LINE:29757E,LINE:29757F,LINE:29758A,LINE:29758B,LINE:29758C,LINE:29758D,LINE:29758E,LINE:29758F,LINE:29759A,LINE:29759B,LINE:29759C,LINE:29759D,LINE:29759E,LINE:29759F,LINE:2975A0,LINE:2975A1,LINE:2975A2,LINE:2975A3,LINE:2975A4,LINE:2975A5,LINE:2975A6,LINE:2975A7,LINE:2975A8,LINE:2975A9,LINE:2975AA,LINE:2975AB,LINE:2975AC,LINE:2975AD,LINE:2975AE,LINE:2975AF,LINE:2975B0,LINE:2975B1,LINE:2975B2,LINE:2975B3,LINE:2975B4,LINE:2975B5,LINE:2975B6,LINE:2975B7,LINE:2975B8,LINE:2975B9,LINE:2975BA,LINE:2975BB,LINE:2975BC,LINE:2975BD,LINE:2975BE,LINE:2975BF,LINE:2975C0,LINE:2975C1,LINE:2975C2,LINE:2975C3,LINE:2975C4,LINE:2975C5,LINE:2975C6,LINE:2975C7,LINE:2975C8,LINE:2975C9,LINE:2975CA,LINE:2975CB,LINE:2975CC,LINE:2975CD,LINE:2975CE,LINE:2975CF,LINE:2975D0,LINE:2975D1,LINE:2975D2,LINE:2975D3,LINE:2975D4,LINE:2975D5,LINE:2975D6,LINE:2975D7,LINE:2975D8,LINE:2975D9,LINE:2975DA,LINE:2975DB,LINE:2975DC,LINE:2975DD,LINE:2975DE,LINE:2975DF,LINE:2975E0,LINE:2975E1,LINE:2975E2,LINE:2975E3,LINE:2975E4,LINE:2975E5,LINE:2975E6,LINE:2975E7,LINE:2975E8,LINE:2975E9,LINE:2975EA,LINE:2975EB,LINE:2975EC,LINE:2975ED,LINE:2975EE,LINE:2975EF,LINE:2975F0,LINE:2975F1,LINE:2975F2,LINE:2975F3,LINE:2975F4,LINE:2975F5,LINE:2975F6,LINE:2975F7,LINE:2975F8,LINE:2975F9,LINE:2975FA,LINE:2975FB,LINE:2975FC,LINE:2975FD,LINE:2975FE,LINE:2975FF,LINE:29760A,LINE:29760B,LINE:29760C,LINE:29760D,LINE:29760E,LINE:29760F,LINE:29761A,LINE:29761B,LINE:29761C,LINE:29761D,LINE:29761E,LINE:29761F,LINE:29762A,LINE:29762B,LINE:29762C,LINE:29762D,LINE:29762E,LINE:29762F,LINE:29763A,LINE:29763B,LINE:29763C,LINE:29763D,LINE:29763E,LINE:29763F,LINE:29764A,LINE:29764B,LINE:29764C,LINE:29764D,LINE:29764E,LINE:29764F,LINE:29765A,LINE:29765B,LINE:29765C,LINE:29765D,LINE:29765E,LINE:29765F,LINE:29766A,LINE:29766B,LINE:29766C,LINE:29766D,LINE:29766E,LINE:29766F,LINE:29767A,LINE:29767B,LINE:29767C,LINE:29767D,LINE:29767E,LINE:29767F,LINE:29768A,LINE:29768B,LINE:29768C,LINE:29768D,LINE:29768E,LINE:29768F,LINE:29769A,LINE:29769B,LINE:29769C,LINE:29769D,LINE:29769E,LINE:29769F,LINE:2976A0,LINE:2976A1,LINE:2976A2,LINE:2976A3,LINE:2976A4,LINE:2976A5,LINE:2976A6,LINE:2976A7,LINE:2976A8,LINE:2976A9,LINE:2976AA,LINE:2976AB,LINE:2976AC,LINE:2976AD,LINE:2976AE,LINE:2976AF,LINE:2976B0,LINE:2976B1,LINE:2976B2,LINE:2976B3,LINE:2976B4,LINE:2976B5,LINE:2976B6,LINE:2976B7,LINE:2976B8,LINE:2976B9,LINE:2976BA,LINE:2976BB,LINE:2976BC,LINE:2976BD,LINE:2976BE,LINE:2976BF,LINE:2976C0,LINE:2976C1,LINE:2976C2,LINE:2976C3,LINE:2976C4,LINE:2976C5,LINE:2976C6,LINE:2976C7,LINE:2976C8,LINE:2976C9,LINE:2976CA,LINE:2976CB,LINE:2976CC,LINE:2976CD,LINE:2976CE,LINE:2976CF,LINE:2976D0,LINE:2976D1,LINE:2976D2,LINE:2976D3,LINE:2976D4,LINE:2976D5,LINE:2976D6,LINE:2976D7,LINE:2976D8,LINE:2976D9,LINE:2976DA,LINE:2976DB,LINE:2976DC,LINE:2976DD,LINE:2976DE,LINE:2976DF,LINE:2976E0,LINE:2976E1,LINE:2976E2,LINE:2976E3,LINE:2976E4,LINE:2976E5,LINE:2976E6,LINE:2976E7,LINE:2976E8,LINE:2976E9,LINE:2976EA,LINE:2976EB,LINE:2976EC,LINE:2976F2,LINE:2976F3,LINE:2976F4,LINE:2976F5,LINE:2976F6,LINE:2976F7,LINE:2976F8,LINE:2976F9,LINE:2976FA,LINE:2976FB,LINE:2976FC,LINE:2976FD,LINE:2976FE,LINE:2976FF,LINE:29770A,LINE:29770B,LINE:29770C,LINE:29770D,LINE:29770E,LINE:29770F,LINE:29771A,LINE:29771B,LINE:29771C,LINE:29771D,LINE:29771E,LINE:29771F,LINE:29772A,LINE:29772B,LINE:29772C,LINE:29772D,LINE:29772E,LINE:29772F,LINE:29773A,LINE:29773B,LINE:29773C,LINE:29773D,LINE:29773E,LINE:29773F,LINE:29774A,LINE:29774B,LINE:29774C,LINE:29774D,LINE:29774E,LINE:29774F,LINE:29775A,LINE:29775B,LINE:29775C,LINE:29775D,LINE:29775E,LINE:29775F vector 0.90; real06.dwg recognition:sym_L1_004 ai 0.95; +2 more | yes | 20 % of its pixels > 0.10 m outside the drawing, 147935 px |
| cam_r_L1_cocuk_odasi_2 | cycles | cross-check misplaced | f_L1_007 | bed_double | - | from_documents | real06.dwg ARC:297260-297261,ARC:297270,ARC:297306,LINE:297267-297269,LINE:297271-297305,LINE:297307-297761,ARC:29725B,ARC:29725E,ARC:29725F,ARC:29726F,ARC:29735D,LINE:293E9B,LINE:29726A,LINE:29726B,LINE:29726C,LINE:29726D,LINE:29726E,LINE:29727A,LINE:29727B,LINE:29727C,LINE:29727D,LINE:29727E,LINE:29727F,LINE:29728A,LINE:29728B,LINE:29728C,LINE:29728D,LINE:29728E,LINE:29728F,LINE:29729A,LINE:29729B,LINE:29729C,LINE:29729D,LINE:29729E,LINE:29729F,LINE:2972A0,LINE:2972A1,LINE:2972A2,LINE:2972A3,LINE:2972A4,LINE:2972A5,LINE:2972A6,LINE:2972A7,LINE:2972A8,LINE:2972A9,LINE:2972AA,LINE:2972AB,LINE:2972AC,LINE:2972AD,LINE:2972AE,LINE:2972AF,LINE:2972B0,LINE:2972B1,LINE:2972B2,LINE:2972B3,LINE:2972B4,LINE:2972B5,LINE:2972B6,LINE:2972B7,LINE:2972B8,LINE:2972B9,LINE:2972BA,LINE:2972BB,LINE:2972BC,LINE:2972BD,LINE:2972BE,LINE:2972BF,LINE:2972C0,LINE:2972C1,LINE:2972C2,LINE:2972C3,LINE:2972C4,LINE:2972C5,LINE:2972C6,LINE:2972C7,LINE:2972C8,LINE:2972C9,LINE:2972CA,LINE:2972CB,LINE:2972CC,LINE:2972CD,LINE:2972CE,LINE:2972CF,LINE:2972D0,LINE:2972D1,LINE:2972D2,LINE:2972D3,LINE:2972D4,LINE:2972D5,LINE:2972D6,LINE:2972D7,LINE:2972D8,LINE:2972D9,LINE:2972DA,LINE:2972DB,LINE:2972DC,LINE:2972DD,LINE:2972DE,LINE:2972DF,LINE:2972E0,LINE:2972E1,LINE:2972E2,LINE:2972E3,LINE:2972E4,LINE:2972E5,LINE:2972E6,LINE:2972E7,LINE:2972E8,LINE:2972E9,LINE:2972EA,LINE:2972EB,LINE:2972EC,LINE:2972ED,LINE:2972EE,LINE:2972EF,LINE:2972F0,LINE:2972F1,LINE:2972F2,LINE:2972F3,LINE:2972F4,LINE:2972F5,LINE:2972F6,LINE:2972F7,LINE:2972F8,LINE:2972F9,LINE:2972FA,LINE:2972FB,LINE:2972FC,LINE:2972FD,LINE:2972FE,LINE:2972FF,LINE:29730A,LINE:29730B,LINE:29730C,LINE:29730D,LINE:29730E,LINE:29730F,LINE:29731A,LINE:29731B,LINE:29731C,LINE:29731D,LINE:29731E,LINE:29731F,LINE:29732A,LINE:29732B,LINE:29732C,LINE:29732D,LINE:29732E,LINE:29732F,LINE:29733A,LINE:29733B,LINE:29733C,LINE:29733D,LINE:29733E,LINE:29733F,LINE:29734A,LINE:29734B,LINE:29734C,LINE:29734D,LINE:29734E,LINE:29734F,LINE:29735A,LINE:29735B,LINE:29735C,LINE:29735E,LINE:29736A,LINE:29736B,LINE:29736C,LINE:29736D,LINE:29736E,LINE:29736F,LINE:29737A,LINE:29737B,LINE:29737C,LINE:29737D,LINE:29737E,LINE:29737F,LINE:29738A,LINE:29738B,LINE:29738C,LINE:29738D,LINE:29738E,LINE:29738F,LINE:29739A,LINE:29739B,LINE:29739C,LINE:29739D,LINE:29739E,LINE:29739F,LINE:2973A0,LINE:2973A1,LINE:2973A2,LINE:2973A3,LINE:2973A4,LINE:2973A5,LINE:2973A6,LINE:2973A7,LINE:2973A8,LINE:2973A9,LINE:2973AA,LINE:2973AB,LINE:2973AC,LINE:2973AD,LINE:2973AE,LINE:2973AF,LINE:2973B0,LINE:2973B1,LINE:2973B2,LINE:2973B3,LINE:2973B4,LINE:2973B5,LINE:2973B6,LINE:2973B7,LINE:2973B8,LINE:2973B9,LINE:2973BA,LINE:2973BB,LINE:2973BC,LINE:2973BD,LINE:2973BE,LINE:2973BF,LINE:2973C0,LINE:2973C1,LINE:2973C2,LINE:2973C3,LINE:2973C4,LINE:2973C5,LINE:2973C6,LINE:2973C7,LINE:2973C8,LINE:2973C9,LINE:2973CA,LINE:2973CB,LINE:2973CC,LINE:2973CD,LINE:2973CE,LINE:2973CF,LINE:2973D0,LINE:2973D1,LINE:2973D2,LINE:2973D3,LINE:2973D4,LINE:2973D5,LINE:2973D6,LINE:2973D7,LINE:2973D8,LINE:2973D9,LINE:2973DA,LINE:2973DB,LINE:2973DC,LINE:2973DD,LINE:2973DE,LINE:2973DF,LINE:2973E0,LINE:2973E1,LINE:2973E2,LINE:2973E3,LINE:2973E4,LINE:2973E5,LINE:2973E6,LINE:2973E7,LINE:2973E8,LINE:2973E9,LINE:2973EA,LINE:2973EB,LINE:2973EC,LINE:2973ED,LINE:2973EE,LINE:2973EF,LINE:2973F0,LINE:2973F1,LINE:2973F2,LINE:2973F3,LINE:2973F4,LINE:2973F5,LINE:2973F6,LINE:2973F7,LINE:2973F8,LINE:2973F9,LINE:2973FA,LINE:2973FB,LINE:2973FC,LINE:2973FD,LINE:2973FE,LINE:2973FF,LINE:29740A,LINE:29740B,LINE:29740C,LINE:29740D,LINE:29740E,LINE:29740F,LINE:29741A,LINE:29741B,LINE:29741C,LINE:29741D,LINE:29741E,LINE:29741F,LINE:29742A,LINE:29742B,LINE:29742C,LINE:29742D,LINE:29742E,LINE:29742F,LINE:29743A,LINE:29743B,LINE:29743C,LINE:29743D,LINE:29743E,LINE:29743F,LINE:29744A,LINE:29744B,LINE:29744C,LINE:29744D,LINE:29744E,LINE:29744F,LINE:29745A,LINE:29745B,LINE:29745C,LINE:29745D,LINE:29745E,LINE:29745F,LINE:29746A,LINE:29746B,LINE:29746C,LINE:29746D,LINE:29746E,LINE:29746F,LINE:29747A,LINE:29747B,LINE:29747C,LINE:29747D,LINE:29747E,LINE:29747F,LINE:29748A,LINE:29748B,LINE:29748C,LINE:29748D,LINE:29748E,LINE:29748F,LINE:29749A,LINE:29749B,LINE:29749C,LINE:29749D,LINE:29749E,LINE:29749F,LINE:2974A0,LINE:2974A1,LINE:2974A2,LINE:2974A3,LINE:2974A4,LINE:2974A5,LINE:2974A6,LINE:2974A7,LINE:2974A8,LINE:2974A9,LINE:2974AA,LINE:2974AB,LINE:2974AC,LINE:2974AD,LINE:2974AE,LINE:2974AF,LINE:2974B0,LINE:2974B1,LINE:2974B2,LINE:2974B3,LINE:2974B4,LINE:2974B5,LINE:2974B6,LINE:2974B7,LINE:2974B8,LINE:2974B9,LINE:2974BA,LINE:2974BB,LINE:2974BC,LINE:2974BD,LINE:2974BE,LINE:2974BF,LINE:2974C0,LINE:2974C1,LINE:2974C2,LINE:2974C3,LINE:2974C4,LINE:2974C5,LINE:2974C6,LINE:2974C7,LINE:2974C8,LINE:2974C9,LINE:2974CA,LINE:2974CB,LINE:2974CC,LINE:2974CD,LINE:2974CE,LINE:2974CF,LINE:2974D0,LINE:2974D1,LINE:2974D2,LINE:2974D3,LINE:2974D4,LINE:2974D5,LINE:2974D6,LINE:2974D7,LINE:2974D8,LINE:2974D9,LINE:2974DA,LINE:2974DB,LINE:2974DC,LINE:2974DD,LINE:2974DE,LINE:2974DF,LINE:2974E0,LINE:2974E1,LINE:2974E2,LINE:2974E3,LINE:2974E4,LINE:2974E5,LINE:2974E6,LINE:2974E7,LINE:2974E8,LINE:2974E9,LINE:2974EA,LINE:2974EB,LINE:2974EC,LINE:2974ED,LINE:2974EE,LINE:2974EF,LINE:2974F0,LINE:2974F1,LINE:2974F2,LINE:2974F3,LINE:2974F4,LINE:2974F5,LINE:2974F6,LINE:2974F7,LINE:2974F8,LINE:2974F9,LINE:2974FA,LINE:2974FB,LINE:2974FC,LINE:2974FD,LINE:2974FE,LINE:2974FF,LINE:29750A,LINE:29750B,LINE:29750C,LINE:29750D,LINE:29750E,LINE:29750F,LINE:29751A,LINE:29751B,LINE:29751C,LINE:29751D,LINE:29751E,LINE:29751F,LINE:29752A,LINE:29752B,LINE:29752C,LINE:29752D,LINE:29752E,LINE:29752F,LINE:29753A,LINE:29753B,LINE:29753C,LINE:29753D,LINE:29753E,LINE:29753F,LINE:29754A,LINE:29754B,LINE:29754C,LINE:29754D,LINE:29754E,LINE:29754F,LINE:29755A,LINE:29755B,LINE:29755C,LINE:29755D,LINE:29755E,LINE:29755F,LINE:29756A,LINE:29756B,LINE:29756C,LINE:29756D,LINE:29756E,LINE:29756F,LINE:29757A,LINE:29757B,LINE:29757C,LINE:29757D,LINE:29757E,LINE:29757F,LINE:29758A,LINE:29758B,LINE:29758C,LINE:29758D,LINE:29758E,LINE:29758F,LINE:29759A,LINE:29759B,LINE:29759C,LINE:29759D,LINE:29759E,LINE:29759F,LINE:2975A0,LINE:2975A1,LINE:2975A2,LINE:2975A3,LINE:2975A4,LINE:2975A5,LINE:2975A6,LINE:2975A7,LINE:2975A8,LINE:2975A9,LINE:2975AA,LINE:2975AB,LINE:2975AC,LINE:2975AD,LINE:2975AE,LINE:2975AF,LINE:2975B0,LINE:2975B1,LINE:2975B2,LINE:2975B3,LINE:2975B4,LINE:2975B5,LINE:2975B6,LINE:2975B7,LINE:2975B8,LINE:2975B9,LINE:2975BA,LINE:2975BB,LINE:2975BC,LINE:2975BD,LINE:2975BE,LINE:2975BF,LINE:2975C0,LINE:2975C1,LINE:2975C2,LINE:2975C3,LINE:2975C4,LINE:2975C5,LINE:2975C6,LINE:2975C7,LINE:2975C8,LINE:2975C9,LINE:2975CA,LINE:2975CB,LINE:2975CC,LINE:2975CD,LINE:2975CE,LINE:2975CF,LINE:2975D0,LINE:2975D1,LINE:2975D2,LINE:2975D3,LINE:2975D4,LINE:2975D5,LINE:2975D6,LINE:2975D7,LINE:2975D8,LINE:2975D9,LINE:2975DA,LINE:2975DB,LINE:2975DC,LINE:2975DD,LINE:2975DE,LINE:2975DF,LINE:2975E0,LINE:2975E1,LINE:2975E2,LINE:2975E3,LINE:2975E4,LINE:2975E5,LINE:2975E6,LINE:2975E7,LINE:2975E8,LINE:2975E9,LINE:2975EA,LINE:2975EB,LINE:2975EC,LINE:2975ED,LINE:2975EE,LINE:2975EF,LINE:2975F0,LINE:2975F1,LINE:2975F2,LINE:2975F3,LINE:2975F4,LINE:2975F5,LINE:2975F6,LINE:2975F7,LINE:2975F8,LINE:2975F9,LINE:2975FA,LINE:2975FB,LINE:2975FC,LINE:2975FD,LINE:2975FE,LINE:2975FF,LINE:29760A,LINE:29760B,LINE:29760C,LINE:29760D,LINE:29760E,LINE:29760F,LINE:29761A,LINE:29761B,LINE:29761C,LINE:29761D,LINE:29761E,LINE:29761F,LINE:29762A,LINE:29762B,LINE:29762C,LINE:29762D,LINE:29762E,LINE:29762F,LINE:29763A,LINE:29763B,LINE:29763C,LINE:29763D,LINE:29763E,LINE:29763F,LINE:29764A,LINE:29764B,LINE:29764C,LINE:29764D,LINE:29764E,LINE:29764F,LINE:29765A,LINE:29765B,LINE:29765C,LINE:29765D,LINE:29765E,LINE:29765F,LINE:29766A,LINE:29766B,LINE:29766C,LINE:29766D,LINE:29766E,LINE:29766F,LINE:29767A,LINE:29767B,LINE:29767C,LINE:29767D,LINE:29767E,LINE:29767F,LINE:29768A,LINE:29768B,LINE:29768C,LINE:29768D,LINE:29768E,LINE:29768F,LINE:29769A,LINE:29769B,LINE:29769C,LINE:29769D,LINE:29769E,LINE:29769F,LINE:2976A0,LINE:2976A1,LINE:2976A2,LINE:2976A3,LINE:2976A4,LINE:2976A5,LINE:2976A6,LINE:2976A7,LINE:2976A8,LINE:2976A9,LINE:2976AA,LINE:2976AB,LINE:2976AC,LINE:2976AD,LINE:2976AE,LINE:2976AF,LINE:2976B0,LINE:2976B1,LINE:2976B2,LINE:2976B3,LINE:2976B4,LINE:2976B5,LINE:2976B6,LINE:2976B7,LINE:2976B8,LINE:2976B9,LINE:2976BA,LINE:2976BB,LINE:2976BC,LINE:2976BD,LINE:2976BE,LINE:2976BF,LINE:2976C0,LINE:2976C1,LINE:2976C2,LINE:2976C3,LINE:2976C4,LINE:2976C5,LINE:2976C6,LINE:2976C7,LINE:2976C8,LINE:2976C9,LINE:2976CA,LINE:2976CB,LINE:2976CC,LINE:2976CD,LINE:2976CE,LINE:2976CF,LINE:2976D0,LINE:2976D1,LINE:2976D2,LINE:2976D3,LINE:2976D4,LINE:2976D5,LINE:2976D6,LINE:2976D7,LINE:2976D8,LINE:2976D9,LINE:2976DA,LINE:2976DB,LINE:2976DC,LINE:2976DD,LINE:2976DE,LINE:2976DF,LINE:2976E0,LINE:2976E1,LINE:2976E2,LINE:2976E3,LINE:2976E4,LINE:2976E5,LINE:2976E6,LINE:2976E7,LINE:2976E8,LINE:2976E9,LINE:2976EA,LINE:2976EB,LINE:2976EC,LINE:2976F2,LINE:2976F3,LINE:2976F4,LINE:2976F5,LINE:2976F6,LINE:2976F7,LINE:2976F8,LINE:2976F9,LINE:2976FA,LINE:2976FB,LINE:2976FC,LINE:2976FD,LINE:2976FE,LINE:2976FF,LINE:29770A,LINE:29770B,LINE:29770C,LINE:29770D,LINE:29770E,LINE:29770F,LINE:29771A,LINE:29771B,LINE:29771C,LINE:29771D,LINE:29771E,LINE:29771F,LINE:29772A,LINE:29772B,LINE:29772C,LINE:29772D,LINE:29772E,LINE:29772F,LINE:29773A,LINE:29773B,LINE:29773C,LINE:29773D,LINE:29773E,LINE:29773F,LINE:29774A,LINE:29774B,LINE:29774C,LINE:29774D,LINE:29774E,LINE:29774F,LINE:29775A,LINE:29775B,LINE:29775C,LINE:29775D,LINE:29775E,LINE:29775F vector 0.90; real06.dwg recognition:sym_L1_004 ai 0.95; +2 more | yes | 20 % of its pixels > 0.10 m outside the drawing, 147935 px |
| cam_r_L1_cocuk_odasi_3 | cycles | cross-check misplaced | f_L1_007 | bed_double | - | from_documents | real06.dwg ARC:297260-297261,ARC:297270,ARC:297306,LINE:297267-297269,LINE:297271-297305,LINE:297307-297761,ARC:29725B,ARC:29725E,ARC:29725F,ARC:29726F,ARC:29735D,LINE:293E9B,LINE:29726A,LINE:29726B,LINE:29726C,LINE:29726D,LINE:29726E,LINE:29727A,LINE:29727B,LINE:29727C,LINE:29727D,LINE:29727E,LINE:29727F,LINE:29728A,LINE:29728B,LINE:29728C,LINE:29728D,LINE:29728E,LINE:29728F,LINE:29729A,LINE:29729B,LINE:29729C,LINE:29729D,LINE:29729E,LINE:29729F,LINE:2972A0,LINE:2972A1,LINE:2972A2,LINE:2972A3,LINE:2972A4,LINE:2972A5,LINE:2972A6,LINE:2972A7,LINE:2972A8,LINE:2972A9,LINE:2972AA,LINE:2972AB,LINE:2972AC,LINE:2972AD,LINE:2972AE,LINE:2972AF,LINE:2972B0,LINE:2972B1,LINE:2972B2,LINE:2972B3,LINE:2972B4,LINE:2972B5,LINE:2972B6,LINE:2972B7,LINE:2972B8,LINE:2972B9,LINE:2972BA,LINE:2972BB,LINE:2972BC,LINE:2972BD,LINE:2972BE,LINE:2972BF,LINE:2972C0,LINE:2972C1,LINE:2972C2,LINE:2972C3,LINE:2972C4,LINE:2972C5,LINE:2972C6,LINE:2972C7,LINE:2972C8,LINE:2972C9,LINE:2972CA,LINE:2972CB,LINE:2972CC,LINE:2972CD,LINE:2972CE,LINE:2972CF,LINE:2972D0,LINE:2972D1,LINE:2972D2,LINE:2972D3,LINE:2972D4,LINE:2972D5,LINE:2972D6,LINE:2972D7,LINE:2972D8,LINE:2972D9,LINE:2972DA,LINE:2972DB,LINE:2972DC,LINE:2972DD,LINE:2972DE,LINE:2972DF,LINE:2972E0,LINE:2972E1,LINE:2972E2,LINE:2972E3,LINE:2972E4,LINE:2972E5,LINE:2972E6,LINE:2972E7,LINE:2972E8,LINE:2972E9,LINE:2972EA,LINE:2972EB,LINE:2972EC,LINE:2972ED,LINE:2972EE,LINE:2972EF,LINE:2972F0,LINE:2972F1,LINE:2972F2,LINE:2972F3,LINE:2972F4,LINE:2972F5,LINE:2972F6,LINE:2972F7,LINE:2972F8,LINE:2972F9,LINE:2972FA,LINE:2972FB,LINE:2972FC,LINE:2972FD,LINE:2972FE,LINE:2972FF,LINE:29730A,LINE:29730B,LINE:29730C,LINE:29730D,LINE:29730E,LINE:29730F,LINE:29731A,LINE:29731B,LINE:29731C,LINE:29731D,LINE:29731E,LINE:29731F,LINE:29732A,LINE:29732B,LINE:29732C,LINE:29732D,LINE:29732E,LINE:29732F,LINE:29733A,LINE:29733B,LINE:29733C,LINE:29733D,LINE:29733E,LINE:29733F,LINE:29734A,LINE:29734B,LINE:29734C,LINE:29734D,LINE:29734E,LINE:29734F,LINE:29735A,LINE:29735B,LINE:29735C,LINE:29735E,LINE:29736A,LINE:29736B,LINE:29736C,LINE:29736D,LINE:29736E,LINE:29736F,LINE:29737A,LINE:29737B,LINE:29737C,LINE:29737D,LINE:29737E,LINE:29737F,LINE:29738A,LINE:29738B,LINE:29738C,LINE:29738D,LINE:29738E,LINE:29738F,LINE:29739A,LINE:29739B,LINE:29739C,LINE:29739D,LINE:29739E,LINE:29739F,LINE:2973A0,LINE:2973A1,LINE:2973A2,LINE:2973A3,LINE:2973A4,LINE:2973A5,LINE:2973A6,LINE:2973A7,LINE:2973A8,LINE:2973A9,LINE:2973AA,LINE:2973AB,LINE:2973AC,LINE:2973AD,LINE:2973AE,LINE:2973AF,LINE:2973B0,LINE:2973B1,LINE:2973B2,LINE:2973B3,LINE:2973B4,LINE:2973B5,LINE:2973B6,LINE:2973B7,LINE:2973B8,LINE:2973B9,LINE:2973BA,LINE:2973BB,LINE:2973BC,LINE:2973BD,LINE:2973BE,LINE:2973BF,LINE:2973C0,LINE:2973C1,LINE:2973C2,LINE:2973C3,LINE:2973C4,LINE:2973C5,LINE:2973C6,LINE:2973C7,LINE:2973C8,LINE:2973C9,LINE:2973CA,LINE:2973CB,LINE:2973CC,LINE:2973CD,LINE:2973CE,LINE:2973CF,LINE:2973D0,LINE:2973D1,LINE:2973D2,LINE:2973D3,LINE:2973D4,LINE:2973D5,LINE:2973D6,LINE:2973D7,LINE:2973D8,LINE:2973D9,LINE:2973DA,LINE:2973DB,LINE:2973DC,LINE:2973DD,LINE:2973DE,LINE:2973DF,LINE:2973E0,LINE:2973E1,LINE:2973E2,LINE:2973E3,LINE:2973E4,LINE:2973E5,LINE:2973E6,LINE:2973E7,LINE:2973E8,LINE:2973E9,LINE:2973EA,LINE:2973EB,LINE:2973EC,LINE:2973ED,LINE:2973EE,LINE:2973EF,LINE:2973F0,LINE:2973F1,LINE:2973F2,LINE:2973F3,LINE:2973F4,LINE:2973F5,LINE:2973F6,LINE:2973F7,LINE:2973F8,LINE:2973F9,LINE:2973FA,LINE:2973FB,LINE:2973FC,LINE:2973FD,LINE:2973FE,LINE:2973FF,LINE:29740A,LINE:29740B,LINE:29740C,LINE:29740D,LINE:29740E,LINE:29740F,LINE:29741A,LINE:29741B,LINE:29741C,LINE:29741D,LINE:29741E,LINE:29741F,LINE:29742A,LINE:29742B,LINE:29742C,LINE:29742D,LINE:29742E,LINE:29742F,LINE:29743A,LINE:29743B,LINE:29743C,LINE:29743D,LINE:29743E,LINE:29743F,LINE:29744A,LINE:29744B,LINE:29744C,LINE:29744D,LINE:29744E,LINE:29744F,LINE:29745A,LINE:29745B,LINE:29745C,LINE:29745D,LINE:29745E,LINE:29745F,LINE:29746A,LINE:29746B,LINE:29746C,LINE:29746D,LINE:29746E,LINE:29746F,LINE:29747A,LINE:29747B,LINE:29747C,LINE:29747D,LINE:29747E,LINE:29747F,LINE:29748A,LINE:29748B,LINE:29748C,LINE:29748D,LINE:29748E,LINE:29748F,LINE:29749A,LINE:29749B,LINE:29749C,LINE:29749D,LINE:29749E,LINE:29749F,LINE:2974A0,LINE:2974A1,LINE:2974A2,LINE:2974A3,LINE:2974A4,LINE:2974A5,LINE:2974A6,LINE:2974A7,LINE:2974A8,LINE:2974A9,LINE:2974AA,LINE:2974AB,LINE:2974AC,LINE:2974AD,LINE:2974AE,LINE:2974AF,LINE:2974B0,LINE:2974B1,LINE:2974B2,LINE:2974B3,LINE:2974B4,LINE:2974B5,LINE:2974B6,LINE:2974B7,LINE:2974B8,LINE:2974B9,LINE:2974BA,LINE:2974BB,LINE:2974BC,LINE:2974BD,LINE:2974BE,LINE:2974BF,LINE:2974C0,LINE:2974C1,LINE:2974C2,LINE:2974C3,LINE:2974C4,LINE:2974C5,LINE:2974C6,LINE:2974C7,LINE:2974C8,LINE:2974C9,LINE:2974CA,LINE:2974CB,LINE:2974CC,LINE:2974CD,LINE:2974CE,LINE:2974CF,LINE:2974D0,LINE:2974D1,LINE:2974D2,LINE:2974D3,LINE:2974D4,LINE:2974D5,LINE:2974D6,LINE:2974D7,LINE:2974D8,LINE:2974D9,LINE:2974DA,LINE:2974DB,LINE:2974DC,LINE:2974DD,LINE:2974DE,LINE:2974DF,LINE:2974E0,LINE:2974E1,LINE:2974E2,LINE:2974E3,LINE:2974E4,LINE:2974E5,LINE:2974E6,LINE:2974E7,LINE:2974E8,LINE:2974E9,LINE:2974EA,LINE:2974EB,LINE:2974EC,LINE:2974ED,LINE:2974EE,LINE:2974EF,LINE:2974F0,LINE:2974F1,LINE:2974F2,LINE:2974F3,LINE:2974F4,LINE:2974F5,LINE:2974F6,LINE:2974F7,LINE:2974F8,LINE:2974F9,LINE:2974FA,LINE:2974FB,LINE:2974FC,LINE:2974FD,LINE:2974FE,LINE:2974FF,LINE:29750A,LINE:29750B,LINE:29750C,LINE:29750D,LINE:29750E,LINE:29750F,LINE:29751A,LINE:29751B,LINE:29751C,LINE:29751D,LINE:29751E,LINE:29751F,LINE:29752A,LINE:29752B,LINE:29752C,LINE:29752D,LINE:29752E,LINE:29752F,LINE:29753A,LINE:29753B,LINE:29753C,LINE:29753D,LINE:29753E,LINE:29753F,LINE:29754A,LINE:29754B,LINE:29754C,LINE:29754D,LINE:29754E,LINE:29754F,LINE:29755A,LINE:29755B,LINE:29755C,LINE:29755D,LINE:29755E,LINE:29755F,LINE:29756A,LINE:29756B,LINE:29756C,LINE:29756D,LINE:29756E,LINE:29756F,LINE:29757A,LINE:29757B,LINE:29757C,LINE:29757D,LINE:29757E,LINE:29757F,LINE:29758A,LINE:29758B,LINE:29758C,LINE:29758D,LINE:29758E,LINE:29758F,LINE:29759A,LINE:29759B,LINE:29759C,LINE:29759D,LINE:29759E,LINE:29759F,LINE:2975A0,LINE:2975A1,LINE:2975A2,LINE:2975A3,LINE:2975A4,LINE:2975A5,LINE:2975A6,LINE:2975A7,LINE:2975A8,LINE:2975A9,LINE:2975AA,LINE:2975AB,LINE:2975AC,LINE:2975AD,LINE:2975AE,LINE:2975AF,LINE:2975B0,LINE:2975B1,LINE:2975B2,LINE:2975B3,LINE:2975B4,LINE:2975B5,LINE:2975B6,LINE:2975B7,LINE:2975B8,LINE:2975B9,LINE:2975BA,LINE:2975BB,LINE:2975BC,LINE:2975BD,LINE:2975BE,LINE:2975BF,LINE:2975C0,LINE:2975C1,LINE:2975C2,LINE:2975C3,LINE:2975C4,LINE:2975C5,LINE:2975C6,LINE:2975C7,LINE:2975C8,LINE:2975C9,LINE:2975CA,LINE:2975CB,LINE:2975CC,LINE:2975CD,LINE:2975CE,LINE:2975CF,LINE:2975D0,LINE:2975D1,LINE:2975D2,LINE:2975D3,LINE:2975D4,LINE:2975D5,LINE:2975D6,LINE:2975D7,LINE:2975D8,LINE:2975D9,LINE:2975DA,LINE:2975DB,LINE:2975DC,LINE:2975DD,LINE:2975DE,LINE:2975DF,LINE:2975E0,LINE:2975E1,LINE:2975E2,LINE:2975E3,LINE:2975E4,LINE:2975E5,LINE:2975E6,LINE:2975E7,LINE:2975E8,LINE:2975E9,LINE:2975EA,LINE:2975EB,LINE:2975EC,LINE:2975ED,LINE:2975EE,LINE:2975EF,LINE:2975F0,LINE:2975F1,LINE:2975F2,LINE:2975F3,LINE:2975F4,LINE:2975F5,LINE:2975F6,LINE:2975F7,LINE:2975F8,LINE:2975F9,LINE:2975FA,LINE:2975FB,LINE:2975FC,LINE:2975FD,LINE:2975FE,LINE:2975FF,LINE:29760A,LINE:29760B,LINE:29760C,LINE:29760D,LINE:29760E,LINE:29760F,LINE:29761A,LINE:29761B,LINE:29761C,LINE:29761D,LINE:29761E,LINE:29761F,LINE:29762A,LINE:29762B,LINE:29762C,LINE:29762D,LINE:29762E,LINE:29762F,LINE:29763A,LINE:29763B,LINE:29763C,LINE:29763D,LINE:29763E,LINE:29763F,LINE:29764A,LINE:29764B,LINE:29764C,LINE:29764D,LINE:29764E,LINE:29764F,LINE:29765A,LINE:29765B,LINE:29765C,LINE:29765D,LINE:29765E,LINE:29765F,LINE:29766A,LINE:29766B,LINE:29766C,LINE:29766D,LINE:29766E,LINE:29766F,LINE:29767A,LINE:29767B,LINE:29767C,LINE:29767D,LINE:29767E,LINE:29767F,LINE:29768A,LINE:29768B,LINE:29768C,LINE:29768D,LINE:29768E,LINE:29768F,LINE:29769A,LINE:29769B,LINE:29769C,LINE:29769D,LINE:29769E,LINE:29769F,LINE:2976A0,LINE:2976A1,LINE:2976A2,LINE:2976A3,LINE:2976A4,LINE:2976A5,LINE:2976A6,LINE:2976A7,LINE:2976A8,LINE:2976A9,LINE:2976AA,LINE:2976AB,LINE:2976AC,LINE:2976AD,LINE:2976AE,LINE:2976AF,LINE:2976B0,LINE:2976B1,LINE:2976B2,LINE:2976B3,LINE:2976B4,LINE:2976B5,LINE:2976B6,LINE:2976B7,LINE:2976B8,LINE:2976B9,LINE:2976BA,LINE:2976BB,LINE:2976BC,LINE:2976BD,LINE:2976BE,LINE:2976BF,LINE:2976C0,LINE:2976C1,LINE:2976C2,LINE:2976C3,LINE:2976C4,LINE:2976C5,LINE:2976C6,LINE:2976C7,LINE:2976C8,LINE:2976C9,LINE:2976CA,LINE:2976CB,LINE:2976CC,LINE:2976CD,LINE:2976CE,LINE:2976CF,LINE:2976D0,LINE:2976D1,LINE:2976D2,LINE:2976D3,LINE:2976D4,LINE:2976D5,LINE:2976D6,LINE:2976D7,LINE:2976D8,LINE:2976D9,LINE:2976DA,LINE:2976DB,LINE:2976DC,LINE:2976DD,LINE:2976DE,LINE:2976DF,LINE:2976E0,LINE:2976E1,LINE:2976E2,LINE:2976E3,LINE:2976E4,LINE:2976E5,LINE:2976E6,LINE:2976E7,LINE:2976E8,LINE:2976E9,LINE:2976EA,LINE:2976EB,LINE:2976EC,LINE:2976F2,LINE:2976F3,LINE:2976F4,LINE:2976F5,LINE:2976F6,LINE:2976F7,LINE:2976F8,LINE:2976F9,LINE:2976FA,LINE:2976FB,LINE:2976FC,LINE:2976FD,LINE:2976FE,LINE:2976FF,LINE:29770A,LINE:29770B,LINE:29770C,LINE:29770D,LINE:29770E,LINE:29770F,LINE:29771A,LINE:29771B,LINE:29771C,LINE:29771D,LINE:29771E,LINE:29771F,LINE:29772A,LINE:29772B,LINE:29772C,LINE:29772D,LINE:29772E,LINE:29772F,LINE:29773A,LINE:29773B,LINE:29773C,LINE:29773D,LINE:29773E,LINE:29773F,LINE:29774A,LINE:29774B,LINE:29774C,LINE:29774D,LINE:29774E,LINE:29774F,LINE:29775A,LINE:29775B,LINE:29775C,LINE:29775D,LINE:29775E,LINE:29775F vector 0.90; real06.dwg recognition:sym_L1_004 ai 0.95; +2 more | yes | 22 % of its pixels > 0.10 m outside the drawing, 302398 px |
| cam_r_L1_ebeveyn_y_odasi_1 | cycles | cross-check misplaced | f_L1_010 | bed_double | - | from_documents | real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF vector 0.90; real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF inferred 0.60 | yes | 18 % of its pixels > 0.10 m outside the drawing, 207724 px |
| cam_r_L1_ebeveyn_y_odasi_2 | cycles | cross-check misplaced | f_L1_010 | bed_double | - | from_documents | real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF vector 0.90; real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF inferred 0.60 | yes | 13 % of its pixels > 0.10 m outside the drawing, 248052 px |

## Needs review

- cam_L1_dresser_1: json cross-check misplaced: f_L1_007
- cam_r_L0_mutfak_1: json cross-check in_json_not_rendered: o_L0_001; json cross-check in_json_not_rendered: d_L0_002
- cam_r_L0_mutfak_3: json cross-check in_json_not_rendered: o_L0_001; json cross-check in_json_not_rendered: d_L0_002
- cam_r_L1_cocuk_odasi_1: json cross-check misplaced: f_L1_007
- cam_r_L1_cocuk_odasi_2: json cross-check misplaced: f_L1_007
- cam_r_L1_cocuk_odasi_3: json cross-check misplaced: f_L1_007
- cam_r_L1_ebeveyn_y_odasi_1: json cross-check misplaced: f_L1_010
- cam_r_L1_ebeveyn_y_odasi_2: json cross-check misplaced: f_L1_010

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

- cam_L1_dresser_1: f_L1_005
- cam_r_L0_banyo_1: f_L0_010, o_L0_002
- cam_r_L0_banyo_2: f_L0_010, o_L0_002
- cam_r_L0_mutfak_1: f_L0_020, f_L0_032, o_L0_003, o_L0_004
- cam_r_L0_mutfak_2: f_L0_020, f_L0_031, o_L0_004
- cam_r_L0_mutfak_3: f_L0_020, f_L0_032, o_L0_004
- cam_r_L0_salon_1: f_L0_006, f_L0_014, f_L0_015, o_L0_005, o_L0_006
- cam_r_L0_salon_2: f_L0_006, f_L0_015, o_L0_005, o_L0_006
- cam_r_L0_salon_3: f_L0_006, f_L0_011, f_L0_014, f_L0_027, f_L0_029, f_L0_030, o_L0_003, o_L0_005
- cam_r_L1_banyo_1: f_L1_009, o_L1_004
- cam_r_L1_cocuk_odasi_1: f_L1_005
- cam_r_L1_cocuk_odasi_2: f_L1_005
- cam_r_L1_cocuk_odasi_3: f_L1_005
- cam_r_L1_dus_2: f_L1_027
- cam_r_L1_ebeveyn_y_odasi_1: f_L1_010, f_L1_020, f_L1_024, f_L1_026
- cam_r_L1_ebeveyn_y_odasi_2: f_L1_010, f_L1_024, f_L1_026, o_L1_007
- cam_r_L1_ebeveyn_y_odasi_3: f_L1_010, f_L1_024, f_L1_026
- cam_r_L1_hol_1: f_L0_001
- cam_r_L1_oda_2_1: f_L1_013, f_L1_014, f_L1_025, o_L1_003, o_L1_005
- cam_r_L1_oda_2_2: f_L1_013, f_L1_014, f_L1_025, o_L1_003
- cam_r_L1_oda_2_3: f_L1_013, f_L1_025, o_L1_003, o_L1_005
- cam_r_L1_soyunma_odasi_1: f_L1_011, f_L1_012
- cam_r_L1_soyunma_odasi_2: f_L1_011, f_L1_012
- ext_1: o_L0_005, o_L0_006, o_L0_007, o_L1_006, o_L1_007
- ext_2: o_L0_002, o_L0_005, o_L0_006, o_L0_007, o_L1_003, o_L1_004, o_L1_006, o_L1_007
- ext_3: o_L0_002, o_L0_003, o_L0_004, o_L1_003, o_L1_004, o_L1_005
- ext_4: o_L0_003
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
| f_L0_027 | furniture | chair | 3dwh_040dd50cd138cbc316c9caec | the vision check says it is not a chair (a bar_stool) |
| f_L0_029 | furniture | chair | 3dwh_040dd50cd138cbc316c9caec | the vision check says it is not a chair (a bar_stool) |
| f_L0_030 | furniture | chair | 3dwh_040dd50cd138cbc316c9caec | the vision check says it is not a chair (a bar_stool) |
| f_L1_004 | furniture | bed_double | 3dwh_118ff62672cee88c43642f77 | the vision check sees more than one object |
| f_L1_007 | furniture | bed_double | hssd_02e22ed56270338bef5f8436e82023c36cd29104 | the vision check sees more than one object |
| f_L1_009 | furniture | bathtub | 3dwh_1fab322fe57d8d05759235ad | vision quality 2 (<= 2) |
| f_L1_016 | furniture | armchair | 3dwh_f6bd91f124d68b40f2957392 | the vision check says it is not a armchair (a chair) |
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
| c_305 | symbol_type_disagreement | f_L1_009 | f_L1_009: sym_L1_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | typed bathtub by code (ai_member): bathtub: r_L1_banyo misses it (r_L1_banyo.bathroom_set (anchor f_L1_022) misses shower\|bathtub) and the AI passes named it (pass 1 (qwen)'s reason names bathtub); the drawn 2.42 x 0.98 m is outside the bathtub's range: the drawn outline 2.4; inferred, listed in the report |
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

- outdoor space os_L0_veranda: veranda 'VERANDA' on L0: 22.84 m² (stated 22.80 m²), strokes; floor +0.00 m (the level mark(s) +0,50 inside it); doors d_L0_004, d_L0_006 open onto it (it is their landing); its edge and steps down to the ground -0.50 m (the drawn steps); light roof over 7.11 m², top +3.00 m; 4 post(s) (2 drawn column(s)) (inferred)
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

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_024

### Ebeveyn Y.odası (r_L1_ebeveyn_y_odasi, bedroom): completed

- added f_L1_029: desk 1.00 x 0.50 (confidence -, rule)
- added f_L1_030: office_chair 0.60 x 0.60 (confidence -, rule)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_016

### Çocuk Odası (r_L1_cocuk_odasi, bedroom): completed

- added f_L1_031: wardrobe 1.20 x 0.50 (confidence -, rule)
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

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_019, f_L1_022

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 56 of 56 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 50 ok, 6 failed; 28 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L0_006 | sofa (sofa) | 0.74 | 0.00 | - | - |
| f_L0_014 | sofa (sofa) | 0.41 | 0.00 | - | - |
| f_L0_026 | washbasin (washbasin) | 0.07 | 0.00 | - | - |
| f_L0_029 | chair (chair) | 0.07 | 0.00 | - | - |
| f_L0_030 | chair (chair) | 0.08 | 0.00 | - | - |
| f_L1_005 | dresser (dresser) | 0.49 | 0.00 | - | - |

Locked-rule violations:

- openings: must stay as drawn (byte-equal): changed d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_006, d_L1_001, d_L1_004, d_L1_005, d_L1_007, d_L1_010, d_L1_011, o_L0_001, o_L0_003, o_L0_005, o_L0_006, o_L0_007, o_L1_003, o_L1_005, o_L1_006, o_L1_007, win_L0_001, win_L0_005, win_L0_006, win_L0_007, win_L1_001, win_L1_003, win_L1_004, win_L1_005, win_L1_008; removed o_L1_001
- f_L0_002: fixed equipment removed
- f_L0_006: moved 0.741 m by the agent (> 0.3 m)
- f_L0_014: moved 0.413 m by the agent (> 0.3 m)
- f_L0_026: fixed equipment moved or resized (only the orientation may change)
- f_L1_005: moved 0.485 m by the agent (> 0.3 m)
- f_L1_023: fixed equipment moved or resized (only the orientation may change)

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered.

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)

Gate for the exterior polish: **polish_disabled** (exterior views stay the Cycles render): benign controls accepted 0.917 < 0.95 (24 comparisons): the gate also rejects harmless edits; negative controls rejected 0.650 < 0.90 (60 comparisons): the gate lets geometry changes through.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | front, right | - | cycles (gate_validation) | not_in_view | front: ok; right: unverified | no |
| ext_2 | corner | back, right | - | cycles (gate_validation) | not_in_view | back: unverified; right: unverified | no |
| ext_3 | corner | back, left | - | cycles (gate_validation) | not_in_view | back: unverified; left: unverified | no |
| ext_4 | corner | front, left | - | cycles (gate_validation) | ok | front: unverified; left: unverified | no |
| ext_5 | aerial | back, left | - | cycles (gate_validation) | ok | back: unverified; left: unverified | no |
| ext_6 | frontal | front | - | cycles (gate_validation) | ok | front: unverified | no |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | wood_cladding | - | agent | no | agent override (docs/milestone11.md §17.3) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | painted_metal_white | - | fallback | yes | style profile exterior.window_frame (assumed) |
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
| plot_wall | render | white | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: building.json facade.elevations. 4 facade(s): 0 ok, 0 mismatch, 4 not checked; roof mismatch.

| elevation | side | drawn win/door | built win/door | result | notes |
|---|---|---|---|---|---|
| r1 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r2 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r7 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r8 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |

Roof heights: built eaves 6,00 m, ridge 7,55 m; drawn eaves 6,00 m (vector), ridge 7,77 m (vector); result mismatch.

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
- door height 2,10 m: 12 opening(s) (d_L0_004, d_L0_005, d_L0_006, d_L0_007, d_L1_002, d_L1_003 ...)
- door sill height -: 1 opening(s) (win_L1_003)
- opening height 2,10 m: 1 opening(s) (o_L1_002)
- window height 0,30 m: 2 opening(s) (win_L1_004, win_L1_005)
- window height 1,15 m: 2 opening(s) (o_L0_001, d_L0_002)
- window height 1,20 m: 22 opening(s) (win_L0_001, d_L0_003, o_L0_002, o_L0_004, o_L0_007, win_L0_002 ...)
- window height 2,40 m: 10 opening(s) (d_L0_001, o_L0_003, o_L0_005, o_L0_006, win_L0_005, win_L0_006 ...)
- window sill height 0,20 m: 2 opening(s) (win_L0_005, win_L0_006)
- window sill height 0,90 m: 13 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_007, win_L1_001 ...)
- window sill height 1,80 m: 2 opening(s) (win_L1_004, win_L1_005)
- f_L0_001 (stair): void assumed (the plan of L1 draws the same stair (f_L1_001) with its landing at the north end: the half landing is there, 1.22 m deep; it draws only the flight at (4.08, 12.33): that flight arrives on L1)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- roof covering: not drawn (the outside look decides, see below)
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
- outside look window_frame: painted_metal_white (fallback: style profile exterior.window_frame (assumed))
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
- outside look plot_wall: render in white (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L1_oda: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_oda |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (-y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| bedding | 2 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L1_010, dress_f_L1_013 |
| boundary | 1 | no site plan: a low hedge on the inferred plot boundary (inferred) | site |
| cabinet_fronts | 2 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_041, furn_f_L0_042 |
| climate | 1 | the drawing's language (tr): the climate most of its houses stand in (a guess) (inferred; the species of trees and hedges follow it): banyo, cocuk, ebeveyn, mutfak | site |
| context | 1 | no context drawn: 137 trees of the mediterranean climate (stone_pine 52, olive 37, plane 25, cypress 23; species inferred) in groups around the site, 54-350 m from the building's centre (the exterior cameras stand within 54 m), with open fields between them so the horizon stays in view (inferred context) | site |
| cut_through | 1 | the wall overlaps w_L0_009 at its opening o_L0_001: cut through both (a facade line drawn over a thicker wall) | w_L0_010 |
| cut_through | 1 | the wall overlaps w_L0_019 at its opening win_L0_007: cut through both (a facade line drawn over a thicker wall) | w_L0_017 |
| cut_through | 1 | the wall overlaps w_L0_029 at its opening win_L0_006: cut through both (a facade line drawn over a thicker wall) | w_L0_028 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 8 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_005_handle, d_L0_007_handle, d_L1_002_handle |
| fabric | 2 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture |
| fascia_material | 1 | pitched roof: the eaves and verge edges are a fascia board in the gutter's aluminium_anthracite (not drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet) | roof |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| ground:+y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-x | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| handrail | 1 | design detail on every flight side not against a wall; not in the documents | furn_f_L0_001 |
| hedge | 7 | no site plan: a low hedge on the inferred plot boundary (inferred) | boundary_hedge_01, boundary_hedge_02, boundary_hedge_03 |
| height | 12 | door height listed as assumed in the building JSON | d_L0_004, d_L0_005, d_L0_006 |
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
| height | 36 | window height listed as assumed in the building JSON | d_L0_001, o_L0_001, d_L0_002 |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:guard_glass | 1 | glass guard in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:railing | 1 | guard's metal (rails, posts, bars or a glass channel) in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| left_out:door | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the scandinavian look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the scandinavian look | openings |
| left_out:entrance | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the scandinavian look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the scandinavian look | openings |
| left_out:glazed_door | 1 | models out of the style's look: 3dwh_2e37507915a83b263b0434e8: glass 8% of its face (< 45%); 3dwh_5b8d6e9c0eff7893f9fe2795: patterned glass (an image on its glass): the scandinavian look wants clear glass; 3dwh_5e2175bedf4e725cd2760f52: glazing bars (16 lites, 4.1 per m2): the scandinavian look wants no or few bars; 3dwh_689987c4c4892159f3c0aaad: no see-through glass; 3dwh_73ccc78df8b9b5ec4219d9b8: no see-through glass; 3dwh_7f96e3f969b6e73f397ec14c: audited styles ['classic', 'modern']: mostly classic, not the scandinavian look; 3dwh_9498c2997722ddf3aef205a7: its title says 'arch': not the scandinavian look; 3dwh_a5392fea8c223c7b149f9f68: audited styles ['classic', 'rustic']: mostly classic, rustic, not the scandinavian look | openings |
| left_out:window | 1 | models out of the style's look: 3dwh_008fc2b4ab59c1a67589cb97: no see-through glass; 3dwh_16c5fdb11c4ec7d95492a04b: glazing bars (12 lites, 3.0 per m2): the scandinavian look wants no or few bars; 3dwh_2a2ec61614b5278cf6fe1011: no see-through glass; 3dwh_48bec799740fad36241c99d9: no see-through glass; 3dwh_4a7dc5974d3b797601e64e12: audited styles ['classic', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_56f518dddfda5b3c284ddf47: no see-through glass; 3dwh_5c21a04d22581a3786ae9bef: no see-through glass; 3dwh_5faa67969eb7104b4adee381: its title says 'traditional': not the scandinavian look | openings |
| level | 1 | terrace os_L0_veranda: one level at +0.00 m (the level mark(s) +0,50 inside it); ground -0.50..-0.50 m under it; edge: steps (inferred); the labelled veranda 'VERANDA' of L0, the landing of d_L0_004, d_L0_006; the drawn steps on edge 7; edges 0, 1, 2, 3, 4, 5, 14 face the building (its walls retain there: no wall, band or steps) | platform_os_L0_veranda |
| level | 1 | terrace os_L1_balkon: one level at +3.00 m (the level mark(s) +3,50 inside it); ground -0.50..-0.50 m under it; edge: none (inferred); the labelled balcony 'BALKON' of L1, the landing of d_L1_007, d_L1_011; elevated: a slab with a guard on its open edges | platform_os_L1_balkon |
| library_model | 1 | library door 3dwh_31a4f763e80370fb618fd10d ('bathroom door') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 15 %; the documents draw the opening, not its product); the building's one door family; scandinavian look: audited styles ['minimal', 'modern'] suit the scandinavian look; frames in the style's finish | d_L1_007 |
| library_model | 1 | library entrance 3dwh_da205d770ecb7e7afcce6e06 ('Front Door') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 25 %; the documents draw the opening, not its product); the building's one entrance family; scandinavian look: audited styles ['industrial', 'modern'] suit the scandinavian look; frames in the style's finish | d_L0_004 |
| library_model | 1 | library glazed door 3dwh_75228caa20a20065078e6c23 ('Valdi - Folding Sliding Door - 4 Door Ti') in 1 panel(s) of 2.95 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one glazed door family; scandinavian look: audited styles ['industrial', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L0_006 |
| library_model | 1 | library glazed door 3dwh_963661fa9b8487c9c0440cf1 ('Valdi - Folding Sliding Door - 3 Door Ti') in 1 panel(s) of 1.98 x 2.10 m (proportions off by 18 %; the documents draw the opening, not its product); the building's one glazed door family; scandinavian look: audited styles ['industrial', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L1_011 |
| library_model | 2 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.68 x 1.20 m (proportions off by 7 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_003, win_L1_006 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.72 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_002 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.75 x 1.20 m (proportions off by 4 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_010 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.77 x 1.20 m (proportions off by 8 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_007 |
| library_model | 3 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 0.80 x 1.20 m (proportions off by 11 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L0_003, d_L1_004, d_L1_010 |
| library_model | 5 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 1 panel(s) of 1.55 x 2.40 m (proportions off by 8 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_005, o_L0_006, d_L1_005 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.57 x 1.20 m (proportions off by 25 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L1_004 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.60 x 1.20 m (proportions off by 20 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_009 |
| library_model | 3 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.72 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_004, o_L1_005, win_L1_011 |
| library_model | 2 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.79 x 1.20 m (proportions off by 9 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_004, win_L1_007 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 2 panel(s) of 0.85 x 1.20 m (proportions off by 18 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_002 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 3 panel(s) of 0.62 x 1.20 m (proportions off by 17 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_007 |
| library_model | 1 | library window 3dwh_9bd7797c74dc5eab0c310771 ('Single Casement Window') in 3 panel(s) of 0.65 x 1.20 m (proportions off by 11 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L1_003 |
| modules | 2 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L0_031, furn_f_L0_032 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| opening_model | 1 | no model of the building's window family 'Single Casement Window' fits 0.70 x 2.40 m: the parametric opening in the style's finish keeps one door and window language | win_L0_005 |
| opening_model | 1 | no model of the building's window family 'Single Casement Window' fits 0.95 x 1.20 m: the parametric opening in the style's finish keeps one door and window language | win_L1_001 |
| opening_model | 1 | no model of the building's window family 'Single Casement Window' fits 1.10 x 1.20 m: the parametric opening in the style's finish keeps one door and window language | o_L0_002 |
| opening_model | 1 | no model of the building's window family 'Single Casement Window' fits 1.10 x 2.40 m: the parametric opening in the style's finish keeps one door and window language | win_L0_006 |
| opening_model | 3 | no model of the building's window family 'Single Casement Window' fits 2.15 x 2.40 m: the parametric opening in the style's finish keeps one door and window language | d_L0_001, o_L0_003, d_L1_001 |
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
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L1_010 (the top of the nightstand f_L1_026 is taken by the candle dec_L1_008): the wall sconce would cover the window win_L1_010 | rig_r_L1_ebeveyn_y_odasi |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L1_013 (no nightstand, no lamp): the wall sconce would run past the end of the head wall | rig_r_L1_oda_2 |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_018; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_mutfak: LED strip under the wall cabinet f_L0_041 over the counter f_L0_002; 400.0 lm -> 1.05 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L0_mutfak_strip_1_light |
| rig_light | 1 | r_L0_mutfak: LED strip under the wall cabinet f_L0_042 over the counter f_L0_031; 245.0 lm -> 0.6431 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L0_mutfak_strip_2_light |
| rig_light | 1 | r_L0_mutfak: ceiling fixture at the pole of inaccessibility of r_L0_mutfak; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_mutfak_ceiling_3_light |
| rig_light | 1 | r_L0_oda: ceiling fixture at the pole of inaccessibility of r_L0_oda, 1 x 1100 lm bulbs for 450 lm/m2 over 2.1 m2 and 1 fixture(s); 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L0_oda_ceiling_1_light |
| rig_light | 1 | r_L0_salon: pendant light over the dining table f_L0_011 under the decor pendant dec_L0_013; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_salon_pendant_1_light |
| rig_light | 1 | r_L1_banyo: ceiling fixture at the pole of inaccessibility of r_L1_banyo; its light under the decor ceiling light dec_L1_036; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_banyo_ceiling_2_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_023; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_dus: ceiling fixture at the pole of inaccessibility of r_L1_dus; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_dus_ceiling_2_light |
| rig_light | 1 | r_L1_dus: mirror light over the washbasin f_L1_027; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_dus_mirror_1_light |
| rig_light | 1 | r_L1_ebeveyn_y_odasi: bedside light in the shade of the table lamp dec_L1_007 on f_L1_024 beside the bed f_L1_010; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L1_ebeveyn_y_odasi_bedside_1_light |
| rig_light | 1 | r_L1_hol: ceiling fixture at the pole of inaccessibility of r_L1_hol, 5 x 1100 lm bulbs for 450 lm/m2 over 11.0 m2 and 1 fixture(s); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_hol_ceiling_1_light |
| rig_light | 1 | r_L1_oda: ceiling fixture at the pole of inaccessibility of r_L1_oda, 2 x 1100 lm bulbs for 450 lm/m2 over 3.1 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_021; 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_oda_ceiling_1_light |
| rig_light | 1 | r_L1_oda_2: bedside light in the shade of the table lamp dec_L1_033 on f_L1_025 beside the bed f_L1_013; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L1_oda_2_bedside_1_light |
| rig_light | 1 | r_L1_soyunma_odasi: ceiling fixture at the pole of inaccessibility of r_L1_soyunma_odasi, 3 x 1100 lm bulbs for 450 lm/m2 over 5.9 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_024; 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_soyunma_odasi_ceiling_1_light |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L0_001 |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 1 | outside sill 0.7357 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_006_sill |
| sill | 1 | outside sill 0.7359 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_003_sill |
| sill | 1 | outside sill 0.76 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_005_sill |
| sill | 1 | outside sill 0.7841 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill |
| sill | 1 | outside sill 0.81 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_010_sill |
| sill | 1 | outside sill 0.8348 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_007_sill |
| sill | 3 | outside sill 0.86 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | d_L0_003_sill, d_L1_004_sill, d_L1_010_sill |
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
| sill_height | 17 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
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
| tree | 1 | medium tree: crown 5.0 m as drawn, 8.0 m tall (height by the crown class, assumed); species stone_pine (inferred) | tree_tree_inferred_3 |
| tree | 2 | small tree: crown 3.5 m as drawn, 5.6 m tall (height by the crown class, assumed); species olive (inferred) | tree_tree_inferred_1, tree_tree_inferred_2 |
| tree:tree_inferred_1 | 1 | no site plan: a tree that frames the windows' view (seen from 5 window(s) (d_L1_005, o_L0_003, o_L0_004, o_L1_005, ...), 5.9 m from the nearest); its crown keeps 2.5 m clear of every window and off their straight view within 6 m; the strict pass placed 0 of 3 (inferred, docs/milestone11.md §1.1 E11; 26 Oct 2026) | site |
| tree:tree_inferred_2 | 1 | no site plan: a tree that frames the windows' view (seen from 4 window(s) (d_L1_010, o_L0_007, win_L1_001, win_L1_011), 6.0 m from the nearest); its crown keeps 2.5 m clear of every window and off their straight view within 6 m; the strict pass placed 0 of 3 (inferred, docs/milestone11.md §1.1 E11; 26 Oct 2026) | site |
| tree:tree_inferred_3 | 1 | the plot leaves no room for 3 trees: a neighbour's tree just beyond the plot edge (seen from 11 window(s) (d_L0_003, d_L1_004, o_L0_002, o_L1_003, ...), 9.1 m from the nearest; inferred context, 26 Oct 2026) | site |
| trees | 1 | inferred trees: placed 3 of 3 (74 candidates; removed by building 1, path 15, sightline 36, window 66, front 27; most by window; the framing pass (the window rule near the facade only) placed 2 of 500 candidates (removed by building 314, path 83, sightline 200, window 347, front 140); the beyond-plot pass (a neighbour's garden) placed 1 of 252 candidates (removed by path 32, sightline 124, front 104); seen from 20 of 30 windows) | site |
| under | 1 | the space under the stair lower than 2.00 m is closed by 4 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass posts balustrade on its 2 free edge(s), 1.49 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| waist | 1 | the documents show the stair in plan only | furn_f_L0_001 |
| winders | 1 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L0_001 |
| window_frame | 1 | style profile exterior.window_frame (assumed) | exterior |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L0_mutfak | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2 | cam_r_L0_mutfak_3 (gate) | ok |
| r_L0_salon | cam_r_L0_salon_2, cam_r_L0_salon_3 | cam_r_L0_salon_1 (gate) | ok |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_2, cam_r_L1_ebeveyn_y_odasi_3 | cam_r_L1_ebeveyn_y_odasi_1 (vision_check) | ok |
| r_L1_oda_2 | cam_r_L1_oda_2_1, cam_r_L1_oda_2_3 | cam_r_L1_oda_2_2 (check_incomplete) | ok |

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_118ff62672cee88c43642f77 [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_1fab322fe57d8d05759235ad [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_330fd9c05ebcf8149e82cc78 [non_commercial], 3dwh_5d52596ee79cd202260f50b9 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_71191a82a44949fded365f4d [non_commercial], 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_a3b30a6264b8d9933f9cbb94 [non_commercial], 3dwh_befa49bcf2992bd57e966593 [non_commercial], 3dwh_c00b0c0f7e1ace04e940a84a [non_commercial], 3dwh_c1bd83916c957dba2a9e90dc [non_commercial], 3dwh_cb38065c6b0c0109cdddd59e [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], 3dwh_dff7590ce6f78822c852419d [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial], 3dwh_f6bd91f124d68b40f2957392 [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_10ddf3cfd25c0ec86ac74e4e3567bcd11bf03549 [non_commercial], hssd_3f0778f68a489d3995e2e3f13d13e4a90fb500a8 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial], hssd_4f1b086633e1b160f09b24a9aad0ec9d1ccb56c0 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_c8a430c096719c94051b441a026620df1bcb42d5 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_L1_dresser_1: commercial-safe: no (flagged assets: 3dwh_118ff62672cee88c43642f77 [non_commercial], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: 3dwh_1fab322fe57d8d05759235ad [non_commercial], hssd_4f1b086633e1b160f09b24a9aad0ec9d1ccb56c0 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: 3dwh_1fab322fe57d8d05759235ad [non_commercial], hssd_4f1b086633e1b160f09b24a9aad0ec9d1ccb56c0 [non_commercial])
- cam_r_L0_mutfak_1: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_dff7590ce6f78822c852419d [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial])
- cam_r_L0_mutfak_2: commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial])
- cam_r_L0_mutfak_3: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_330fd9c05ebcf8149e82cc78 [non_commercial], 3dwh_dff7590ce6f78822c852419d [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial])
- cam_r_L0_salon_1: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_330fd9c05ebcf8149e82cc78 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial])
- cam_r_L0_salon_2: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_5d52596ee79cd202260f50b9 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial])
- cam_r_L0_salon_3: commercial-safe: no (flagged assets: 3dwh_038a2f938697cf94f0635b35 [non_commercial], 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_1c9dbdb1c1d98b0c5c633595 [non_commercial], 3dwh_330fd9c05ebcf8149e82cc78 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: 3dwh_1fab322fe57d8d05759235ad [non_commercial], 3dwh_c1bd83916c957dba2a9e90dc [non_commercial], hssd_4f1b086633e1b160f09b24a9aad0ec9d1ccb56c0 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L1_cocuk_odasi_1: commercial-safe: no (flagged assets: 3dwh_118ff62672cee88c43642f77 [non_commercial], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial])
- cam_r_L1_cocuk_odasi_2: commercial-safe: no (flagged assets: 3dwh_118ff62672cee88c43642f77 [non_commercial], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial])
- cam_r_L1_cocuk_odasi_3: commercial-safe: no (flagged assets: hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial])
- cam_r_L1_dus_1: commercial-safe: no (flagged assets: hssd_c8a430c096719c94051b441a026620df1bcb42d5 [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L1_dus_2: commercial-safe: no (flagged assets: 3dwh_cb38065c6b0c0109cdddd59e [non_commercial], hssd_3f0778f68a489d3995e2e3f13d13e4a90fb500a8 [non_commercial], hssd_c8a430c096719c94051b441a026620df1bcb42d5 [non_commercial], hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4 [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_1: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_c00b0c0f7e1ace04e940a84a [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial], 3dwh_f6bd91f124d68b40f2957392 [non_commercial], hssd_10ddf3cfd25c0ec86ac74e4e3567bcd11bf03549 [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_2: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a3b30a6264b8d9933f9cbb94 [non_commercial], 3dwh_c00b0c0f7e1ace04e940a84a [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_3: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial])
- cam_r_L1_hol_1: commercial-safe: yes
- cam_r_L1_oda_1: commercial-safe: yes
- cam_r_L1_oda_2_1: commercial-safe: no (flagged assets: 3dwh_befa49bcf2992bd57e966593 [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_oda_2_2: commercial-safe: no (flagged assets: 3dwh_d5d094598fcac16b93a39700 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_oda_2_3: commercial-safe: no (flagged assets: 3dwh_befa49bcf2992bd57e966593 [non_commercial], 3dwh_d5d094598fcac16b93a39700 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_soyunma_odasi_1: commercial-safe: yes
- cam_r_L1_soyunma_odasi_2: commercial-safe: yes
- ext_1: commercial-safe: no (flagged assets: 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: no (flagged assets: 3dwh_71191a82a44949fded365f4d [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_4: commercial-safe: no (flagged assets: 3dwh_71191a82a44949fded365f4d [non_commercial], 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_5: commercial-safe: no (flagged assets: 3dwh_71191a82a44949fded365f4d [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])
- ext_6: commercial-safe: no (flagged assets: 3dwh_71191a82a44949fded365f4d [non_commercial], 3dwh_89b423a3a3890b2b6f806687 [non_commercial], 3dwh_e96c9c82ce7f23a6794062e2 [non_commercial])

## Built below library level (Milestone 13)

7 furniture piece(s) built from a module builder or a parametric family instead of a library model: 0 library gap(s) to close with a real model, 7 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

| id | type | method | builder | room | room type | source | gap | used |
|---|---|---|---|---|---|---|---|---|
| f_L0_001 | stair | parametric | parametric:stair | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_020 | sink_kitchen | parametric | parametric:sink_kitchen | r_L0_mutfak | kitchen | from_documents | no (by design) | our parametric fixture (by design) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_hol | hall | from_documents | no (by design) | - |
| f_L0_031 | kitchen_counter | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_032 | kitchen_counter | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_041 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_042 | wall_cabinet | parametric | parametric:wall_cabinet | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_2 (10.4 degrees off the sun, sky pull k 3).

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

Assets: textures CC0 x 25; furniture/decor models 3DWH-UNREVIEWED x 40, CC-BY-4.0 x 34, CC-BY-NC-4.0 x 24, generated (TRELLIS.2-4B, MIT) x 7 (parametric meshes need no licence).

## Attribution

No CC BY or Objaverse model in this project (Poly Haven CC0 models and parametric meshes need no credit).

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_L1_dresser_1 | calibrated | yes | no | - |
| cam_r_L0_banyo_1 | calibrated | yes | no | - |
| cam_r_L0_banyo_2 | calibrated | yes | no | - |
| cam_r_L0_mutfak_1 | calibrated | yes | no | - |
| cam_r_L0_mutfak_2 | calibrated | yes | no | - |
| cam_r_L0_salon_2 | calibrated | yes | no | - |
| cam_r_L0_salon_3 | calibrated | yes | no | - |
| cam_r_L1_banyo_1 | calibrated | yes | no | - |
| cam_r_L1_cocuk_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_cocuk_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_cocuk_odasi_3 | calibrated | yes | no | - |
| cam_r_L1_dus_1 | calibrated | yes | no | - |
| cam_r_L1_dus_2 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_y_odasi_1 | calibrated | yes | yes | furniture [1216.4, 28.5, 1278.0, 228.8] (score, vlm:agent) |
| cam_r_L1_ebeveyn_y_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_y_odasi_3 | calibrated | yes | no | - |
| cam_r_L1_oda_2_1 | calibrated | yes | no | - |
| cam_r_L1_oda_2_2 | calibrated | yes | no | - |
| cam_r_L1_oda_2_3 | calibrated | yes | no | - |
| cam_r_L1_soyunma_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_soyunma_odasi_2 | calibrated | yes | no | - |

## Stages

This run (`20261027-222248-full-20261027T222733Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 26.7 s | - |
| pipeline | pending | 36.7 s | 31 recognition question(s) written (recognition/requests.json) |
| recognize | reused | 1.7 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.3 s | - |
| pipeline_final | ok | 37.5 s | answers applied |
| fit | ok | 5.2 s | - |
| layout | ok | 21.4 s | - |
| decor_ask | ok | 12.2 s | - |
| assets | ok | 2.2 s | - |
| decor | ok | 13.2 s | - |
| agent_apply | ok | 21.6 s | - |
| refit | ok | 36.8 s | - |
| build | ok | 26.0 min | - |
| agent_previews | ok | 6.3 min | 6 view(s) |
| agent | ok | 38.7 min | 4 round(s), 10 finding(s) removed by 61 accepted edit(s) (measured; 56 predicted by the dry re-checks), 12 new, net -2, 117 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 12.1 min | - |
| export | ok | 4.1 min | - |
| controls | ok | 95.6 s | - |
| gate | ok | 3.3 min | gate decision flagged |
| polish | ok | 8.1 min | - |
| detect | ok | 21.5 s | - |
| expected | ok | 92.2 s | - |
| check | ok | 9.3 min | - |
| combine | ok | 30.2 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 61 edit(s) accepted, 117 rejected, 387 model calls (4511521 tokens), 45.3 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 7908): earlier runs of the appended log are left out (7907 events, 2466 model calls, 176 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 61 / 117 (34 % accepted) |
| rejected by reason | acceptance 35, no_change 15, memory 14, lower_quality 7, pin_refused 7 |
| rooms checked by code / vision / planner | 12 / 11 / 12 |
| rooms with fixable critical or major findings visited | 12 of 13 |
| critical before -> after (after: round 4's critics, before its 19 accepted edit(s)) | 14 -> 17 |
| major before -> after (after: round 4's critics, before its 19 accepted edit(s)) | 118 -> 285 |
| agent minutes; first accepted edit after | 41.82; 3.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 14; 62; 34 (27) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 10 measured; 56 predicted (the last round's dry re-checks predicted 44 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 51 new; net -41 |
| edits removing their finding | 2 of 33 |
| plans ok / empty / refused / default | 27 / 7 / 0 / 0 |

### What the AI inspector saw on the final renders

0 vision finding(s) (0 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 0 fixed in the final round, 0 handed to the stage that owns them, 0 open; the architect leaves 4 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`. The final round did not start (time): these are the last round's findings on the previews.

### Argus, the auditor

Score 12.6 / 100 (100 = nothing open): 1 critical, 104 major, 47 minor open. By kind (critical + major): misread 6, taste 54, other 14, lost 11, no_sense 10, silent 5, geometry 3, process 2. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- misread r_L1_cocuk_odasi: The room is missing its main functional pieces for a children's room: the desk (f_L1_032), office chair (f_L1_033), and wardrobe (f_L1_031) are not visible, mak

Library gaps reported by the agent: sink_kitchen (Sink f_L0_020 built below library level (parametric) because no audited sink_kitchen model fits the drawn size within tolerance; the gap is already recorded.), table_dining scandinavian (No audited scandinavian table_dining model fits the small 0.80 x 0.70 m bistro footprint within the fit rules, so the dining set stays as placeholder primitives.), wall_art (The room's walls are bare and the reference style calls for framed pictures, but no wall-art model exists in the audited library.), sofa modern grey (No audited library model of a modern grey sofa rated high enough matches the orange leather sofa's size; previous swap was rejected for lower quality.), armchair modern neutral (No audited library model of a modern neutral armchair rated high enough replaces the red egg chair; previous swap was rejected for lower quality.), sofa modern light scandinavian (No audited library model of a modern light Scandinavian sofa rated high enough matches the bulky orange sofa; the accepted swap still leaves a style mismatch.), armchair modern neutral (No audited library model of a modern neutral armchair rated high enough replaces the dark red egg chair; previous swap was rejected for lower quality.), shoe_cabinet (Every audited shoe_cabinet library model fails the fit rules (height caps) for the 0.6x0.25x1.0 piece, so swap_model changes nothing and the piece renders invisible; documenting the library gap.), outdoor_furniture outdoor (Covered terrace lacks outdoor seating; no audited library model of an outdoor furniture set exists to place (a:D3:o_L0_002).).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 14 | 118 | 31 | 18 | 19 | 46 | layout | 31 |
| 2 | 15 | 120 | 31 | 18 | 18 | 44 | layout | 31 |
| 3 | 15 | 118 | 31 | 18 | 5 | 16 | refit | 6 |
| 4 | 17 | 285 | 68 | 35 | 19 | 11 | refit | 31 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A6 | 0 | 4 | 0 | 0 |
| AI1 | 0 | 38 | 0 | 0 |
| AI2 | 0 | 12 | 0 | 0 |
| C1 | 0 | 0 | 0 | 2 |
| C3 | 0 | 8 | 0 | 0 |
| C6 | 0 | 2 | 0 | 0 |
| C7 | 0 | 4 | 0 | 0 |
| D2 | 0 | 10 | 1 | 0 |
| D3 | 0 | 212 | 33 | 0 |
| F1 | 0 | 0 | 8 | 0 |
| F3 | 4 | 18 | 12 | 0 |
| F4 | 0 | 5 | 0 | 0 |
| F6 | 0 | 4 | 0 | 0 |
| F7 | 8 | 0 | 0 | 0 |
| F9 | 1 | 29 | 0 | 2 |
| G1 | 0 | 0 | 8 | 0 |
| G10 | 0 | 12 | 0 | 0 |
| G11 | 16 | 35 | 0 | 0 |
| G12 | 0 | 51 | 0 | 0 |
| G14 | 0 | 0 | 8 | 0 |
| G2 | 0 | 4 | 4 | 0 |
| G3 | 0 | 16 | 0 | 0 |
| G4 | 0 | 4 | 12 | 0 |
| G5 | 0 | 12 | 0 | 0 |
| G6 | 0 | 0 | 4 | 0 |
| G8 | 0 | 4 | 4 | 0 |
| J1 | 0 | 29 | 0 | 76 |
| K3 | 0 | 16 | 0 | 0 |
| K4 | 0 | 1 | 0 | 4 |
| L2 | 0 | 16 | 0 | 0 |
| M2 | 0 | 7 | 0 | 0 |
| NR | 0 | 8 | 0 | 0 |
| P0 | 0 | 4 | 0 | 0 |
| P7 | 0 | 5 | 0 | 0 |
| P9 | 0 | 0 | 0 | 5 |
| Q3 | 2 | 4 | 0 | 0 |
| Q4 | 6 | 22 | 0 | 0 |
| Q5 | 0 | 10 | 0 | 0 |
| Q7 | 0 | 1 | 3 | 0 |
| Q9 | 0 | 4 | 0 | 0 |
| RC | 0 | 0 | 4 | 0 |
| S2 | 0 | 14 | 4 | 0 |
| S3 | 0 | 4 | 0 | 0 |
| S5 | 0 | 0 | 16 | 0 |
| V1 | 8 | 12 | 0 | 0 |
| X3 | 16 | 0 | 0 | 0 |
| X5 | 0 | 0 | 40 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 8119 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The camera is too close to the wardrobe and door, filling the frame with a wall. Re-aiming it to show the wardrobe from a free point reveals the room. (fixes a:F2) | - | - |
| 8120 | 1 | set_camera | r_L1_oda | agent_override | - | Argus: The frame is filled by a wall corner and a louvered panel; the hall, doors and shoe cabinet are not visible. Re-aiming to show the shoe cabinet from a free point makes the room judgeable. (fixes a:F3) | - | - |
| 8123 | 1 | add_camera | r_L1_cocuk_odasi | agent_override | - | Argus: The documents name a dresser ('*SIFONIYER') on L1 at (8.106, 4.909), but the model has no piece within 1.2 m. The add_piece action is not available as a tool; the closest fix is to ensure the piece is built. However, since the piece is not  (fixes a:F12) | - | - |
| 8131 | 1 | set_material | wet_walls | agent_override | - | Argus: The reference defines the project's style with natural materials, but the render is a flat, untextured white box. (fixes a:F58) | - | - |
| 8132 | 1 | swap_model | f_L0_037 | added_by_ai | 0.0 -> 0.0 | Argus: The dining table is a simple oval slab that clashes with the light, airy Scandinavian style of the rest of the house. (fixes a:F63) | ![](agent/r1_010_swap_model_before_r_L0_mutfak.png) | ![](agent/r1_011_swap_model_after_r_L0_mutfak.png) |
| 8135 | 1 | swap_model | f_L0_014 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The orange sofa is dated and bulky; the proposed model is modern/scandinavian and fits the 1.52 x 0.78 m footprint. (fixes a:F69) | ![](agent/r1_014_swap_model_before_r_L0_salon.png) | ![](agent/r1_015_swap_model_after_r_L0_salon.png) |
| 8138 | 1 | set_camera | r_L1_cocuk_odasi | agent_override | - | Argus: The view is blocked by a white railing; moving the camera to a free point that shows the beds and wardrobe resolves the issue. (fixes a:F77) | - | - |
| 8139 | 1 | swap_model | f_L1_004 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The bed is a crude, blocky model; the proposed model is minimal/modern/scandinavian and fits the 1.94 x 1.90 m footprint. (fixes a:F78) | ![](agent/r1_018_swap_model_before_r_L1_cocuk_odasi.png) | ![](agent/r1_019_swap_model_after_r_L1_cocuk_odasi.png) |
| 8140 | 1 | set_camera | r_L1_dus | agent_override | - | Argus: The view is pressed against the wall and cuts off the main fixtures; moving the camera to a free point that shows the basin, shower, and toilet resolves the issue. (fixes a:F80) | - | - |
| 8141 | 1 | swap_model | f_L1_015 | adjusted_by_ai | 44.0 -> 44.0 | Argus: The white sculptural armchair clashes with the rustic pine nightstand and modern grey armchair in the same room. (fixes a:F83) | ![](agent/r1_020_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r1_021_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 8143 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The render is a close-up of a wall and a door frame; it does not show the room, its furniture, or the design. (fixes a:F91) | - | - |
| 8144 | 1 | set_material | facade | agent_override | - | Argus: The entire facade is a flat, untextured white/grey, missing the rich material palette shown in the reference. (fixes a:F93) | - | - |
| 8146 | 1 | swap_model | f_L0_029 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The chair f_L0_029 is 0.07 m from its drawn place, exceeding the 0.05 m tolerance. Swapping to a model with a slightly different footprint (0.46 x 0.45 m vs 0.45 x 0.45 m) may help it fit the drawn position better. (fixes a:F117) | ![](agent/r1_024_swap_model_before_r_L0_salon.png) | ![](agent/r1_025_swap_model_after_r_L0_salon.png) |
| 8147 | 1 | swap_model | f_L0_030 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The chair f_L0_030 is 0.08 m from its drawn place, exceeding the 0.05 m tolerance. Swapping to a model with a slightly different footprint (0.46 x 0.45 m vs 0.45 x 0.45 m) may help it fit the drawn position better. (fixes a:F118) | ![](agent/r1_026_swap_model_before_r_L0_salon.png) | ![](agent/r1_027_swap_model_after_r_L0_salon.png) |
| 8174 | 1 | move_piece | f_L0_006 | adjusted_by_ai | 0.0 -> 0.0 | Snap sofa back onto the right wall to clear window o_L0_005 and fix F3 off-wall | ![](agent/r1_070_move_piece_before_r_L0_salon.png) | ![](agent/r1_071_move_piece_after_r_L0_salon.png) |
| 8196 | 1 | set_front | f_L1_019 | adjusted_by_ai | 50.0 -> 60.0 | Washing machine front faced a wall at 270°; its front should face into the room (90°) so the door is usable. | ![](agent/r1_086_set_front_before_r_L1_banyo.png) | ![](agent/r1_087_set_front_after_r_L1_banyo.png) |
| 8208 | 1 | set_camera | r_L1_oda | agent_override | - | The current view is blocked by a wall corner and louvered panel; reposition to show the shoe cabinet and the hall's doors. | - | - |
| 8218 | 1 | swap_model | f_L1_013 | adjusted_by_ai | 0.0 -> 0.0 | Swap to a scandinavian/japandi bed with more texture and layering to address the plain white bedding finding (a:F141) | ![](agent/r1_095_swap_model_before_r_L1_oda_2.png) | ![](agent/r1_096_swap_model_after_r_L1_oda_2.png) |
| 8223 | 1 | set_room_type | r_L0_oda | adjusted_by_ai | 100.0 -> 100.0 | 2.1 m² entrance/foyer space with a 1.85 m opening; 'hall' is too large a designation, 'other' better fits a small transitional entry. | ![](agent/r1_099_set_room_type_before_r_L0_oda.png) | ![](agent/r1_100_set_room_type_after_r_L0_oda.png) |
| 8478 | 2 | set_material | kitchen_walls | agent_override | - | Argus: The judge notes the worktop and backsplash are flat and untextured, contributing to a grey-box feel; setting the kitchen_walls slot to a stone look adds the material richness the reference shows. (fixes a:F133) | - | - |
| 8479 | 2 | swap_model | f_L0_011 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The glass dining table with an ornate base feels out of place in a modern minimalist salon; abo_B0853Q71J6 is a scandinavian/japandi/modern minimal table of matching size (0.99 x 0.99 x 0.75 m). (fixes a:F134) | ![](agent/r2_003_swap_model_before_r_L0_salon.png) | ![](agent/r2_004_swap_model_after_r_L0_salon.png) |
| 8483 | 2 | swap_model | f_L1_016 | adjusted_by_ai | 44.0 -> 44.0 | Argus: The grey quilted armchair does not match the white armchair or the rustic wood elements; 3dwh_f6bd91f124d68b40f2957392 is a minimal/modern/scandinavian armchair of matching size (0.86 x 0.76 x 0.76 m) that unifies the set. (fixes a:F139) | ![](agent/r2_008_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r2_009_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 8489 | 2 | set_room_type | r_L1_soyunma_odasi | adjusted_by_ai | 70.0 -> 70.0 | Argus: The 'Soyunma Odası' (dressing room) is typed 'other' and contains only a wardrobe; it is not connected to the master bedroom or bathroom it should serve, and its type does not match its function. (fixes a:N51) | ![](agent/r2_014_set_room_type_before_r_L1_soyunma_odasi.png) | ![](agent/r2_015_set_room_type_after_r_L1_soyunma_odasi.png) |
| 8505 | 2 | report_library_gap | f_L0_020 | library_gap | - | Sink f_L0_020 built below library level (parametric) because no audited sink_kitchen model fits the drawn size within tolerance; the gap is already recorded. | - | - |
| 8510 | 2 | report_library_gap | f_L0_037 | library_gap | - | No audited scandinavian table_dining model fits the small 0.80 x 0.70 m bistro footprint within the fit rules, so the dining set stays as placeholder primitives. | - | - |
| 8511 | 2 | report_library_gap | report_library_gap | library_gap | - | The room's walls are bare and the reference style calls for framed pictures, but no wall-art model exists in the audited library. | - | - |
| 8524 | 2 | remove_piece | f_L0_034 | added_by_ai | 0.0 -> 0.0 | Bookshelf was already removed by an AI decision but remains in the piece list, causing the 'not built' finding; removing it resolves the inconsistency. | ![](agent/r2_057_remove_piece_before_r_L0_salon.png) | ![](agent/r2_058_remove_piece_after_r_L0_salon.png) |
| 8525 | 2 | remove_piece | f_L0_035 | added_by_ai | 0.0 -> 0.0 | Potted plant was already removed by an AI decision but remains in the piece list, causing the 'not built' finding; removing it resolves the inconsistency. | ![](agent/r2_059_remove_piece_before_r_L0_salon.png) | ![](agent/r2_061_remove_piece_after_r_L0_salon.png) |
| 8528 | 2 | report_library_gap | f_L0_006 | library_gap | - | No audited library model of a modern grey sofa rated high enough matches the orange leather sofa's size; previous swap was rejected for lower quality. | - | - |
| 8529 | 2 | report_library_gap | f_L0_007 | library_gap | - | No audited library model of a modern neutral armchair rated high enough replaces the red egg chair; previous swap was rejected for lower quality. | - | - |
| 8530 | 2 | report_library_gap | f_L0_014 | library_gap | - | No audited library model of a modern light Scandinavian sofa rated high enough matches the bulky orange sofa; the accepted swap still leaves a style mismatch. | - | - |
| 8531 | 2 | report_library_gap | f_L0_016 | library_gap | - | No audited library model of a modern neutral armchair rated high enough replaces the dark red egg chair; previous swap was rejected for lower quality. | - | - |
| 8547 | 2 | set_camera | r_L1_oda | agent_override | - | Re-aim the blocked interior camera to a free pose showing the shoe cabinet and both doors, resolving the bad_camera finding. | - | - |
| 8548 | 2 | report_library_gap | f_L1_028 | library_gap | - | Every audited shoe_cabinet library model fails the fit rules (height caps) for the 0.6x0.25x1.0 piece, so swap_model changes nothing and the piece renders invisible; documenting the library gap. | - | - |
| 8560 | 2 | set_material | facade | agent_override | - | Replace the flat white/grey facade with warm timber cladding to match the reference material palette (a:F93). | - | - |
| 8561 | 2 | report_library_gap | o_L0_002 | library_gap | - | Covered terrace lacks outdoor seating; no audited library model of an outdoor furniture set exists to place (a:D3:o_L0_002). | - | - |
| 8562 | 2 | set_camera | r_L1_dus | agent_override | - | Camera is pressed against the wall showing only a tiled corner and glass partition; reposition to a free point that frames the washbasin and shower (a:F80, a:F81). | - | - |
| 8825 | 3 | swap_model | f_L0_040 | added_by_ai | 0.0 -> 0.0 | a:F9: the fridge is planned but not visible; use the real product model the code says fits so it renders. | ![](agent/r3_030_swap_model_before_r_L0_mutfak.png) | ![](agent/r3_032_swap_model_after_r_L0_mutfak.png) |
| 8832 | 3 | swap_model | f_L0_036 | added_by_ai | 0.0 -> 0.0 | a:F8: the stove is planned but not visible; use the real product model the code says fits so it renders. | ![](agent/r3_037_swap_model_before_r_L0_mutfak.png) | ![](agent/r3_038_swap_model_after_r_L0_mutfak.png) |
| 8842 | 3 | set_camera | r_L1_oda | agent_override | - | The current interior camera is blocked by a wall corner and louvered panel, hiding the hall, doors and shoe cabinet. Re-aim the interior camera to a free point with headroom so the room, its doors and the shoe cabinet are visible. | - | - |
| 8847 | 3 | set_camera | r_L1_soyunma_odasi | agent_override | - | Camera is too close to the wardrobe and door, filling the frame with a wall; reposition to a free interior point with headroom showing the room's main group and layout. | - | - |
| 8862 | 3 | swap_model | f_L1_023 | adjusted_by_ai | 60.0 -> 60.0 | swap the crude black floating washbasin for a real modern minimal washbasin that fits the drawn 0.53x0.34 footprint | ![](agent/r3_072_swap_model_before_r_L1_banyo.png) | ![](agent/r3_073_swap_model_after_r_L1_banyo.png) |
| 9312 | 4 | swap_model | f_L0_036 | added_by_ai | 0.0 -> 0.0 | Argus: The stove is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F27) | ![](agent/r4_002_swap_model_before_r_L0_mutfak.png) | ![](agent/r4_003_swap_model_after_r_L0_mutfak.png) |
| 9313 | 4 | swap_model | f_L0_037 | added_by_ai | 0.0 -> 0.0 | Argus: The dining table is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F28) | ![](agent/r4_004_swap_model_before_r_L0_mutfak.png) | ![](agent/r4_005_swap_model_after_r_L0_mutfak.png) |
| 9315 | 4 | swap_model | f_L1_032 | added_by_ai | 0.0 -> 0.0 | Argus: The desk is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F31) | ![](agent/r4_007_swap_model_before_r_L1_cocuk_odasi.png) | ![](agent/r4_008_swap_model_after_r_L1_cocuk_odasi.png) |
| 9317 | 4 | set_camera | r_L1_ebeveyn_y_odasi | agent_override | - | Argus: The view is flagged for review because it does not show the room's content; re-posing it to show the bed and surrounding pieces resolves the check. (fixes a:F49) | - | - |
| 9319 | 4 | set_camera | r_L1_cocuk_odasi | agent_override | - | Argus: The render shows a generic, empty master bedroom, not the 22.4 m2 children's room (r_L1_cocuk_odasi) it is supposed to be. It is missing the room's main pieces (wardrobe, desk, office chair) and all the styling layers the reference sets (ru (fixes a:F58) | - | - |
| 9320 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The render is a bare, unstyled shell that fails to meet the standard set by the reference. It lacks the warm wood textures, functional accessories (towel warmer, mirror), and general 'lived-in' feel of the project style. (fixes a:F62) | - | - |
| 9321 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The render is a bare, unstyled shell that fails the project's standard. The washbasin (f_L0_026) is completely missing, leaving the room without a primary fixture. The surfaces are flat and untextured, and the space lacks all the styling la (fixes a:F64) | - | - |
| 9324 | 4 | swap_model | f_L0_027 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The dining chairs are a mismatched set of at least four different models. Swapping f_L0_027 to a modern/scandinavian chair (3dwh_040dd50cd138cbc316c9caec) is the first step toward unifying the set. The other chairs (f_L0_028, f_L0_029, f_L0 (fixes a:F75) | ![](agent/r4_012_swap_model_before_r_L0_salon.png) | ![](agent/r4_013_swap_model_after_r_L0_salon.png) |
| 9325 | 4 | set_material | wet_walls | agent_override | - | Argus: The judge flags that the bathroom walls and floor are flat and untextured. Setting the wet walls to a large porcelain tile will add the warm, finished look the reference shows. (fixes a:F77) | - | - |
| 9326 | 4 | set_camera | r_L1_cocuk_odasi | agent_override | - | Argus: The judge says the camera is badly placed, dominated by a dark wardrobe slab, and the room looks like a generic adult bedroom. Moving the camera to show the bed and desk (the main groups) will frame the room properly. The piece ids f_L1_028 (fixes a:F78) | - | - |
| 9327 | 4 | set_camera | r_L1_dus | agent_override | - | Argus: The camera is a close-up of a corner and glass partition, failing to show the washbasin or the layout. Moving it to show the main group fixes the framing. (fixes a:F82) | - | - |
| 9328 | 4 | swap_model | f_L1_018 | adjusted_by_ai | 90.0 -> 90.0 | Argus: The current shower model looks like a broken model. Swapping to a minimal/modern glass partition fixes the visual mess. (fixes a:F85) | ![](agent/r4_014_swap_model_before_r_L1_dus.png) | ![](agent/r4_015_swap_model_after_r_L1_dus.png) |
| 9329 | 4 | swap_model | f_L1_015 | adjusted_by_ai | 44.0 -> 44.0 | Argus: The two wooden armchairs and the white wire chair are three different styles. Swapping the armchair to a modern/scandinavian model that matches the minimalist bed creates a cohesive set. (fixes a:F86) | ![](agent/r4_016_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r4_017_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 9331 | 4 | set_camera | r_L1_oda | agent_override | - | Argus: The camera is a close-up of a corner and a door, failing to show the room or its furniture. Moving it to show the shoe cabinet fixes the framing. (fixes a:F91) | - | - |
| 9332 | 4 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The camera is pressed against the wardrobe, so the frame is 80% white paneling and a door leaf. Moving it to show the wardrobe and the room's space fixes the framing. (fixes a:F95) | - | - |
| 9333 | 4 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The judge says the camera is pressed against the wardrobe showing a wall and a door; the room's only furniture is the wardrobe, so the camera must be moved to show it. (fixes a:F97) | - | - |
| 9336 | 4 | swap_model | f_L0_029 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The 0.07 m offset is a fit issue, not a placement error; a matching-footprint model lets the solver place it exactly. (fixes a:F119) | ![](agent/r4_019_swap_model_before_r_L0_salon.png) | ![](agent/r4_020_swap_model_after_r_L0_salon.png) |
| 9337 | 4 | swap_model | f_L0_030 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The 0.08 m offset is a fit issue; a matching-footprint model lets the solver place it exactly. (fixes a:F120) | ![](agent/r4_021_swap_model_before_r_L0_salon.png) | ![](agent/r4_022_swap_model_after_r_L0_salon.png) |
| 9340 | 4 | set_material | kitchen_walls | agent_override | - | Argus: The kitchen counter and cabinetry are a plain, flat white. Setting the kitchen_walls material to wood_oak_light adds the warmth and texture seen in the reference. (fixes a:F136) | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 8118 | 1 | place_group | r_L1_soyunma_odasi | no_place: dressing group: no place passes the checks (dressing: no place passes the checks) | Argus: The room is typed 'other' and holds only a wardrobe; the judge sees no functional dressing setup. Placing the dressing group gives the room its program. (fixes a:F1) |
| 8121 | 1 | retype_piece | f_L0_036 | no_change: f_L0_036 is already a stove | Argus: The stove is planned but has no object in the scene. Retyping it as a stove rebuilds it with a valid model from the available options. (fixes a:F8) |
| 8122 | 1 | retype_piece | f_L0_040 | no_change: f_L0_040 is already a fridge | Argus: The fridge is planned but has no object in the scene. Retyping it as a fridge rebuilds it with a valid model from the available options. (fixes a:F9) |
| 8124 | 1 | retype_piece | f_L0_034 | no_change: f_L0_034 is already a bookshelf | Argus: The bookshelf f_L0_034 was removed by an AI decision but the salon's piece list still includes a bookshelf. Retyping it ensures it is rebuilt with a valid model from the available options. (fixes a:F13) |
| 8125 | 1 | retype_piece | f_L1_008 | no_change: f_L1_008 is already a nightstand | Argus: The nightstand f_L1_008 was not built because it cut the bed f_L1_007 by 0.40 m and no free place was found within 1.0 m. Retyping it allows the solver to re-fit it with a valid model and position. (fixes a:F14) |
| 8126 | 1 | retype_piece | f_L1_004 | retype: bunk_bed is no candidate for f_L1_004 (1.94 x 1.90 m at [1.43, 8.12]): the size table and the room / zone give stair | Argus: The room is a children's room but is furnished with a standard double bed; a bunk bed is the correct anchor for this room type. (fixes a:F33) |
| 8127 | 1 | swap_model | f_L1_028 | acceptance: pin_refused: f_L1_028: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The shoe cabinet in the hall is not built, leaving the room empty in the render. Swapping to a valid model ensures it is built and visible. (fixes a:F34) |
| 8128 | 1 | fix_fixture | f_L0_032 | fixture_size: f_L0_032: the drawn 2.40 x 0.60 m is within 30 % of the real kitchen_counter range (width 0.60-5.00 m, depth 0.50-0.75 m): its size stays as drawn | Argus: The kitchen counter is built at 2.10 m, which is too high. Fixing the fixture size should correct its height to the standard working level. (fixes a:F36) |
| 8129 | 1 | swap_model | f_L1_005 | acceptance: pin_refused: f_L1_005: hssd_68b22165ccec115439ff5bca2a28bd2ebf1fdb9d: fails the fit rules (caps, height, at most 0.88 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The dresser model includes a white railing that floats in the room, creating a nonsensical hazard. Swapping to a clean dresser model will remove the railing. (fixes a:F38) |
| 8130 | 1 | set_entrance | d_L0_001 | no_change: d_L0_001 has steps already | Argus: The entrance handrail does not connect to the steps, and the canopy floats. Setting the entrance solution to 'steps' should ensure proper handrail and canopy support. (fixes a:F39) |
| 8133 | 1 | swap_model | f_L0_016 | lower_quality: f_L0_016: 3dwh_d1ed36390489612fbb2a5baa is rated 3.0 against 5.0 of the current model abo_B075X4N3GM: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Argus: The dark red egg chair clashes with the neutral Scandinavian set; the proposed model is minimal/modern/scandinavian and fits the 0.92 x 0.77 m footprint. (fixes a:F65) |
| 8134 | 1 | swap_model | f_L0_006 | lower_quality: f_L0_006: hssd_4364e0d4faa0006a6e447b9293fdfbe3c415cfa7 is rated 3.0 against 4.5 of the current model abo_B072555T67: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Argus: The orange leather sofa is a different style and colour family from the grey sofa; the proposed model is modern/scandinavian and fits the 2.12 x 0.78 m footprint. (fixes a:F66) |
| 8136 | 1 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: hssd_4d4709a41a152773f55c745958f1af7670dc59b7: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The black washbasin is a crude placeholder; the proposed model is minimal/scandinavian and fits the 0.53 x 0.34 m footprint. (fixes a:F72) |
| 8137 | 1 | retype_piece | f_L1_007 | retype: bed_single is no candidate for f_L1_007 (1.90 x 2.09 m at [1.44, 4.55]): the size table and the room / zone give stair | Argus: Two full double beds in a 22m2 room are illogical; retyping the second bed to a single bed resolves the cluttered, hotel-like feel. (fixes a:F75) |
| 8142 | 1 | swap_model | f_L1_024 | acceptance: pin_refused: f_L1_024: abo_B084MYDTKM: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The rustic pine nightstand and its neon-style lamp clash with the modern minimalist bed and chairs. (fixes a:F84) |
| 8145 | 1 | retype_piece | f_L0_035 | no_change: f_L0_035 is already a potted_plant | Argus: The salon's piece list includes a potted_plant, but the AI removed it. Retyping it ensures it is rebuilt with a valid model, restoring the intended furnishing. (fixes a:F115) |
| 8150 | 1 | relayout_room | r_L0_mutfak | group checks: G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge); G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove) | Re-solve kitchen_run and dining with the solver's best candidate so the stove, fridge, sink and chairs are all built and correctly placed (fixes a:N47, a:F8, a:F9, c:G6). |
| 8151 | 1 | move_piece | f_L1_016 | drawn_lock: f_L1_016: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.62 m) | Move armchair off window d_L1_001 (G12) and clear the floor lamp f_L1_020 from its front zone (F6). |
| 8152 | 1 | move_piece | f_L1_016 | acceptance: finding G12:f_L1_016 is still there after the edit (armchair f_L1_016 (0.85 m) stands in front of window d_L1_001 (sill 0.20 m + 0.05)) | Snap armchair back to the south wall (window d_L1_001) to clear the floor lamp f_L1_020 from its front zone (F6) and reposition it away from the window band (G12). |
| 8153 | 1 | move_piece | f_L1_016 | acceptance: finding G12:f_L1_016 is still there after the edit (armchair f_L1_016 (0.85 m) stands in front of window d_L1_001 (sill 0.20 m + 0.05)) | Snap armchair back to the south wall at the left end of the window band (offset 0.5 m from span start) so it clears the window d_L1_001 (G12) and the floor lamp f_L1_020 (F6). |
| 8156 | 1 | move_piece | f_L1_016 | max_tries: f_L1_016 was edited 3 times in this round | Snap armchair back to the south wall at the very left end of the window band (offset 0.3 m from span start) so it clears the window d_L1_001 (G12) and the floor lamp f_L1_020 (F6). |
| 8157 | 1 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Full relayout to clear the critical G11 walkway between doors d_L0_004 and d_L0_006 and the G12 window blockages of the seating groups. |
| 8158 | 1 | move_piece | f_L1_010 | snap: f_L1_010: no free place on wall w_L1_027 (doors, windows, at most 1.2 m from the drawn place) | Snap the bed's headboard back onto the west wall (w_L1_027) to clear the 0.06 m off-wall gap (F3/G5). |
| 8159 | 1 | move_piece | f_L1_005 | acceptance: finding G12:f_L1_005 is still there after the edit (dresser f_L1_005 (0.80 m) stands in front of window d_L1_005 (sill 0.20 m + 0.05)) | Snap the dresser's back onto wall w_L1_022 (fixes F3 off-wall) and shift it down to clear the window d_L1_005 (G12) and the overlap with bed f_L1_004 (F9). |
| 8160 | 1 | move_piece | f_L1_010 | f_L1_010: inside_room | Nudge the bed 0.06 m west so the headboard sits flush on the west wall (F3/G5). |
| 8161 | 1 | fix_fixture | f_L0_032 | fixture_place: f_L0_032: no valid spot within 0.50 m (it stands 0.06 m² outside the room, in door o_L0_001) | Counter top is at 2.10 m, over working height; reset to a real counter height. |
| 8162 | 1 | move_piece | f_L1_010 | acceptance: finding F3:f_L1_010 is still there after the edit (bed_double: the headboard stands in the room (0.12 m off)) | Nudge the bed 0.06 m east so the headboard sits flush on the west wall (F3/G5). |
| 8164 | 1 | move_piece | f_L1_010 | memory: the same edit was rejected in round 1: f_L1_010: inside_room | Nudge the bed 0.06 m west so the headboard sits flush on the west wall (F3/G5). |
| 8166 | 1 | swap_model | f_L0_038 | acceptance: pin_refused: f_L0_038: dining_chair_02: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the heavy block chair with a light modern dining chair to match the airy style (a:F63). |
| 8167 | 1 | move_piece | f_L1_024 | f_L1_024: inside_room | Nudge the nightstand 0.06 m west so its back sits flush on the west wall (F3). |
| 8172 | 1 | move_piece | f_L1_024 | acceptance: finding F3:f_L1_024 is still there after the edit (nightstand: its back is not on a wall (0.12 m off)) | Nudge the nightstand 0.06 m east so its back sits flush on the west wall (F3). |
| 8173 | 1 | swap_model | f_L0_038 | acceptance: pin_refused: f_L0_038: SchoolChair_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the heavy block chair with a light minimal chair to match the airy style (a:F63). |
| 8187 | 1 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_008 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe off the door swing and windows to the south wall span to clear F7/G11/G12 |
| 8190 | 1 | move_piece | f_L1_011 | f_L1_011: clearance_ok | Shift wardrobe 0.174 m south to clear the door swing and window win_L1_003 (F7/G11) |
| 8192 | 1 | move_piece | f_L1_011 | f_L1_011: inside_room (outline: wardrobe reaches 0.39 m² through the room outline, up to 0.173 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 50 (F3 f_L1_011: wardrobe: its back is not on a wall (0.17 m off); F9 f_L1_011: wardrobe reaches 0.39 m² through the room outline, up to 0.173 m deep) | Shift wardrobe 0.174 m east to clear the door swing and window win_L1_003 (F7/G11) |
| 8193 | 1 | move_piece | f_L1_011 | max_tries: f_L1_011 was edited 3 times in this round | Shift wardrobe 0.174 m north to clear the door swing and window win_L1_003 (F7/G11) |
| 8195 | 1 | move_piece | f_L1_012 | f_L1_012: clearance_ok | Shift wardrobe 0.174 m south to clear window win_L1_004 (G12) and improve the walkway from the door |
| 8197 | 1 | move_piece | f_L1_012 | f_L1_012: inside_room (outline: wardrobe reaches 0.35 m² through the room outline, up to 0.154 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 50 (F3 f_L1_012: wardrobe: its back is not on a wall (0.15 m off); F9 f_L1_012: wardrobe reaches 0.35 m² through the room outline, up to 0.154 m deep) | Shift wardrobe 0.174 m west to clear window win_L1_004 (G12) and improve the walkway from the door |
| 8199 | 1 | move_piece | f_L1_012 | f_L1_012: clearance_ok, f_L1_012: inside_room (outline: wardrobe reaches 0.06 m² through the room outline, up to 0.102 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 60 (F9 f_L1_012: wardrobe reaches 0.06 m² through the room outline, up to 0.102 m deep) | Shift wardrobe 0.174 m north to clear window win_L1_004 (G12) and improve the walkway from the door |
| 8200 | 1 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: 3dwh_6154347ab8ff886fbcf80494: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The current black boxy placeholder clashes with the white tile and modern style; this minimalist rectangle sink (0.53x0.33 m) matches the drawn footprint and the room's modern look. |
| 8204 | 1 | set_room_type | r_L1_oda | no_change: r_L1_oda is already a hall | 3.1 m² room with a shoe cabinet and entrance doors is a foyer/entrance, not a hall. |
| 8205 | 1 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: hssd_7b5d656c72b56ae0e8200132ec92a1ae03869b93: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The current black boxy placeholder clashes with the white tile and modern style; this minimal modern sink (0.57x0.33 m) matches the drawn footprint and the room's light modern look. |
| 8209 | 1 | swap_model | f_L1_023 | max_tries: f_L1_023 was edited 3 times in this round | The current black boxy placeholder clashes with the white tile and modern style; this minimal modern wash-basin (0.60x0.35 m) matches the drawn footprint and the room's light modern look. |
| 8217 | 1 | set_room_type | r_L0_oda | no_change: r_L0_oda is already a hall | Confirming hall: 2.1 m² entrance/foyer with a 1.85 m opening, no pieces needed. |
| 8220 | 1 | swap_model | f_L1_014 | no_change: f_L1_014 already uses the model abo_B07GFS1VB6 | Swap to a scandinavian sliding 2-door wardrobe (180x61x197cm) to address the massive flat block finding (a:F140) and the drawing difference (a:F120) |
| 8222 | 1 | swap_model | f_L1_014 | lower_quality: f_L1_014: abo_B07H8JN9QF is rated 4.0 against 5.0 of the current model abo_B07GFS1VB6: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Swap to a 4-door 2-drawer wardrobe with mirrors (200x59x212cm) to address the massive flat block finding (a:F140) |
| 8476 | 2 | swap_model | f_L1_014 | pin_refused: f_L1_014: gen_wardrobe_rustic_1_97c119f6: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07GFS1VB6): the real model stays; swap to a real model of the type or use another tool | Argus: The wardrobe f_L1_014 is 0.39 m from its drawn place, exceeding the 0.05 m tolerance. Swapping to a model with a different footprint (1.25 x 0.81 m vs 1.81 x 0.68 m) may help it fit the drawn position better. (fixes a:F120) |
| 8477 | 2 | swap_model | f_L0_020 | acceptance: pin_refused: f_L0_020: 3dwh_c40a2fac663a4c615676d8e5: audit: removed (1.26 x 0.47 x 0.58 m fits a sink_kitchen only with another axis up: the model lies on its side; an anchor (sink_kitchen) of units guessed (x1.0): the Milestone 13 gate needs known units for anchors; the vision check says it is not a sink_kitchen; vision quality 1 (<= 2)): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The sink_kitchen was built as a parametric mesh; a neutral library model of 1.26 x 0.47 x 0.58 m fits the drawn 1.20 x 0.45 m piece and raises it to library quality. (fixes a:F130) |
| 8480 | 2 | swap_model | f_L0_007 | lower_quality: f_L0_007: 3dwh_d1ed36390489612fbb2a5baa is rated 3.0 against 5.0 of the current model abo_B075X4N3GM: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Argus: The red egg chair is a dated statement piece that does not fit the modern style; 3dwh_d1ed36390489612fbb2a5baa is a minimal/modern/scandinavian armchair of matching size (0.91 x 0.76 x 0.55 m). (fixes a:F135) |
| 8481 | 2 | swap_model | f_L1_031 | acceptance: pin_refused: f_L1_031: abo_B07GFRKNR1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The flat white wardrobe clashes with the warm wood tones; abo_B07GFRKNR1 is a scandinavian/modern minimal wardrobe of matching size (0.99 x 0.58 x 1.81 m) that fits the room's style. (fixes a:F137) |
| 8482 | 2 | swap_model | f_L1_010 | acceptance: pin_refused: f_L1_010: abo_B071FJR4FW: fails the fit rules (caps, height, at most 0.88 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The bedding is a single flat white sheet; abo_B071FJR4FW is a scandinavian/japandi/modern minimal bed of matching size (1.63 x 2.11 x 1.42 m) that includes layered bedding. (fixes a:F138) |
| 8484 | 2 | swap_model | f_L1_013 | pin_refused: f_L1_013: gen_bed_single_rustic_3_20248be5: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07H8V14CZ): the real model stays; swap to a real model of the type or use another tool | Argus: The bedding is plain white and lacks texture; gen_bed_single_rustic_3_20248be5 is a scandinavian/japandi/modern minimal single bed (1.10 x 1.82 x 0.86 m) that includes layered bedding. (fixes a:F141) |
| 8485 | 2 | set_room_type | r_L0_oda | memory: the same edit was rejected in round 1: no_change: r_L0_oda is already a hall | Argus: The room 'Oda' (hall) on L0 is only 2.1 m2 and has no pieces. It is too small to be a functional hall and lacks the shoe cabinet listed in the room's program. (fixes a:N46) |
| 8486 | 2 | place_group | r_L0_mutfak | no_change: r_L0_mutfak already has its kitchen_run r_L0_mutfak.kitchen_run (anchor f_L0_002, members f_L0_020, f_L0_031, f_L0_032, f_L0_036, f_L0_040): nothing missing, never a second set | Argus: The kitchen is functionally empty. The counters are bare white boxes with no sink, no hob, and the fridge and stove are listed but not visible in the scene. (fixes a:N47) |
| 8487 | 2 | place_group | r_L0_salon | no_place: dining group re-solved around the drawn table_dining f_L0_011: the solver places nothing and leaves the drawn pieces as drawn (no place within 0.5 m of the drawn centre) | Argus: The salon is missing its dining set. The room is defined as having a dining table and chairs, but they are completely missing from the scene. (fixes a:N48) |
| 8488 | 2 | place_group | r_L1_dus | room_type: a wc_set group does not belong in a bathroom room (groups.yaml room types: wc) | Argus: The shower room is missing its main piece, the washing machine (f_L1_019), which is listed in the room's program. (fixes a:N50) |
| 8490 | 2 | set_room_type | r_L1_oda | memory: the same edit was rejected in round 1: no_change: r_L1_oda is already a hall | Argus: The 'Oda' on L1 is typed 'hall' but is 3.1 m2 and contains a shoe cabinet; it is a small entrance/foyer, not a hall. (fixes a:N52) |
| 8491 | 2 | retype_piece | f_L1_006 | f_L1_006: no_overlap, score: plausibility -45 -> -55 (F9 f_L1_006: floor_lamp f_L1_006 overlaps bed_double f_L1_004 by 0.16 m²) | the plan names it: drawn piece f_L1_006 (0.40 x 0.40 m) left out as a detail (drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)) although an AI pass named it floor_lamp / nightstand, which fits its size: (fixes a:c4) |
| 8495 | 2 | complete_group | r_L0_mutfak.kitchen_run | no_change: r_L0_mutfak.kitchen_run: nothing missing (members: f_L0_020, f_L0_031, f_L0_032, f_L0_036, f_L0_040) | Build the missing visible appliances (stove, fridge) of the drawn kitchen run to resolve the 'functionally empty' and missing-object findings. |
| 8496 | 2 | fix_fixture | f_L0_031 | fixture_place: f_L0_031: no valid spot within 0.50 m (it stands 0.18 m² outside the room) | Resolve the 0.44 m² overlap between kitchen_counter f_L0_031 and f_L0_002 by nudging the drawn counter to a valid spot. |
| 8498 | 2 | swap_model | f_L0_037 | off_style: f_L0_037: abo_B075Z9QB7N is of the styles ['industrial'], none of the project's chain scandinavian -> minimal -> modern: choose a model of the style | Replace the placeholder oval slab table with a real small round dining table (0.885 m) matching the light modern style. |
| 8499 | 2 | swap_model | f_L0_038 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Replace the heavy block chair with a real modern armless accent chair (0.52 m) matching the light airy style. |
| 8501 | 2 | move_piece | f_L1_005 | snap: f_L1_005: no free place on wall w_L1_012 (doors, windows, at most 1.2 m from the drawn place) | Snap the dresser's back to the free north wall span s5 (clear of the window d_L1_005 and bed f_L1_004) to fix F3 off-wall, F9 overlap and G12 window blockage. |
| 8502 | 2 | swap_model | f_L0_037 | acceptance: pin_refused: f_L0_037: abo_B075YMXWZC: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the placeholder oval slab table with a real scandinavian oak dining table matching the project's light airy style. |
| 8504 | 2 | move_piece | f_L1_005 | snap: f_L1_005: no free place on wall w_L1_029 (doors, windows, at most 1.2 m from the drawn place) | Snap the dresser's back to the free east wall span s2 (clear of the window d_L1_005 and bed f_L1_004) to fix F3 off-wall, F9 overlap and G12 window blockage. |
| 8506 | 2 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_012 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe off the door win_L1_003 and the windows to the free span s1 (below win_L1_005) to clear the door blockage and walkway. |
| 8507 | 2 | move_piece | f_L1_005 | f_L1_005: inside_room | Nudge the dresser 0.06 m east so its back sits on wall w_L1_022 (fixes F3 off-wall) and it clears bed f_L1_004 (fixes F9 overlap); it stays below the window sill. |
| 8508 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 has no hard failures and high circulation (0.97) to clear the critical d_L0_004→d_L0_006 walkway and the G12 window blockages. |
| 8509 | 2 | complete_group | r_L0_salon.dining | no_change: r_L0_salon.dining: nothing missing (members: f_L0_027, f_L0_028, f_L0_029, f_L0_030) | Argus reports the dining set missing from the scene; completing the group ensures the drawn dining set is registered and built. |
| 8512 | 2 | move_piece | f_L1_011 | f_L1_011: clearance_ok, f_L1_011: inside_room (outline: wardrobe reaches 0.06 m² through the room outline, up to 0.102 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 60 (F9 f_L1_011: wardrobe reaches 0.06 m² through the room outline, up to 0.102 m deep) | Nudge the wardrobe 0.174 m toward the north wall to clear the door win_L1_003 and the 0.60 m walkway from d_L1_003. |
| 8513 | 2 | move_piece | f_L1_005 | memory: the same edit was rejected in round 2: f_L1_005: inside_room | Nudge the dresser 0.06 m east so its back sits on wall w_L1_022 (fixes F3 off-wall) and it clears bed f_L1_004 (fixes F9 overlap); it stays below the window sill. |
| 8514 | 2 | move_piece | f_L1_011 | acceptance: finding F7:f_L1_011 is still there after the edit (wardrobe blocks door win_L1_003) | Restore the wardrobe to its drawn position after the rejected northward nudge. |
| 8515 | 2 | move_piece | f_L1_005 | memory: the same edit was rejected in round 2: f_L1_005: inside_room | Nudge the dresser 0.06 m east so its back sits on wall w_L1_022 (fixes F3 off-wall) and it clears bed f_L1_004 (fixes F9 overlap); it stays below the window sill. |
| 8517 | 2 | move_piece | f_L1_011 | memory: the same edit was rejected in round 2: acceptance: finding F7:f_L1_011 is still there after the edit (wardrobe blocks door win_L1_003) | Restore the wardrobe to its drawn position after the rejected northward nudge. |
| 8518 | 2 | retype_piece | f_L0_036 | memory: the same edit was rejected in round 1: no_change: f_L0_036 is already a stove | Confirm the stove type so the added appliance is built and visible in the scene, resolving the missing-object finding. |
| 8519 | 2 | retype_piece | f_L0_040 | memory: the same edit was rejected in round 1: no_change: f_L0_040 is already a fridge | Confirm the fridge type so the added appliance is built and visible in the scene, resolving the missing-object finding. |
| 8521 | 2 | move_piece | f_L1_011 | memory: the same edit was rejected in round 2: acceptance: finding F7:f_L1_011 is still there after the edit (wardrobe blocks door win_L1_003) | Restore the wardrobe to its drawn position after the rejected northward nudge. |
| 8526 | 2 | relayout_room | r_L1_hol | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 1 more kept | Reposition the entrance group (shoe cabinet) to open the 0.60 m walkways from d_L1_006 and o_L1_002 to d_L1_009; candidate 1 has the best score and circulation. |
| 8533 | 2 | relayout_room | r_L1_hol | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 1 more kept | Candidate 2 has better circulation (0.85 vs 0.83); try repositioning the entrance group to open the 0.60 m walkways from d_L1_006 and o_L1_002 to d_L1_009. |
| 8534 | 2 | swap_model | f_L1_019 | pin_refused: f_L1_019: gen_washing_machine_modern_1_f4bdd46e: a generated model (units guessed) while a real product of the type fits within the caps (hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29): the real model stays; swap to a real model of the type or use another tool | The washing machine renders as a flat white panel (rug-like); swap to a proper 3D modern washing machine model. |
| 8537 | 2 | swap_model | f_L1_019 | lower_quality: f_L1_019: hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 is rated 1.0 against 3.0 of the current model hssd_31609de54bc7b3cceb58cff41b88b69d7f7db9ec: a swap never takes a lower-rated model; choose one rated at least 2.8, or fix the view (camera, light) instead | The washing machine renders as a flat white panel (rug-like); swap to the real 3D washing machine model the code confirms fits. |
| 8538 | 2 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s3: no place passes the checks (entrance: no candidate position fits the room) | Move the shoe cabinet away from door d_L1_009 to the free wall span s3 to open the 0.60 m walkways from d_L1_006 and o_L1_002 to d_L1_009. |
| 8540 | 2 | swap_model | f_L1_019 | acceptance: pin_refused: f_L1_019: hssd_031024e00569909d466d87df9fead90355ba29e5: audit: removed (a maker's logo or brand name on the model: the SAMSUNG logo is readable on the control panel; seen in P4b real03 cam_r_L0_banyo_4_2; trademarks are not licensed (docs/milestone13.md §2.6)): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The washing machine renders as a flat white panel (rug-like); swap to the real Samsung 3D washing machine model. |
| 8543 | 2 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s2: no place passes the checks (entrance: no candidate position fits the room) | Move the shoe cabinet to span s2 (same wall, further from d_L1_009) to open the 0.60 m walkways. |
| 8545 | 2 | move_piece | f_L1_034 | f_L1_001: no_overlap, f_L1_034: doors_free, f_L1_034: no_overlap, score: plausibility 40 -> 0 (F7 f_L1_034: shoe_cabinet blocks door d_L1_009; F9 f_L1_034: shoe_cabinet f_L1_034 overlaps stair f_L1_001 by 0.23 m²) | Move the shoe cabinet up the right wall away from door d_L1_009 to open the 0.60 m walkways from d_L1_006 and o_L1_002 to d_L1_009. |
| 8546 | 2 | swap_model | f_L1_019 | max_tries: f_L1_019 was edited 3 times in this round | The washing machine renders as a flat white panel (rug-like); swap to the real generic 3D washing machine model. |
| 8551 | 2 | move_piece | f_L1_034 | f_L1_001: no_overlap, f_L1_034: inside_room, f_L1_034: no_overlap, f_L1_034: windows_free, score: plausibility 40 -> 10 (F3 f_L1_034: shoe_cabinet: its back is not on a wall (0.26 m off); F4 f_L1_034: shoe_cabinet faces a wall 0.00 m in front of it; G12 f_L1_034: shoe_cabinet f_L1_034 (1.00 m) stands in front of window win_L1_008 (sill 0.90 m + 0.05)) | Move the shoe cabinet to the left wall (span s7 area) away from all three doors to open the 0.60 m walkways. |
| 8552 | 2 | set_room_type | r_L0_oda | no_change: r_L0_oda is already a other | 2.1 m² room with no pieces is a small entrance/foyer, not a functional hall; 'other' matches its actual use. |
| 8554 | 2 | remove_piece | f_L1_034 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Remove the shoe cabinet to clear the 0.60 m walkways from d_L1_006 and o_L1_002 to d_L1_009; the entrance group is optional (required: false). |
| 8556 | 2 | move_piece | f_L1_034 | max_tries: f_L1_034 was edited 3 times in this round | Move the shoe cabinet to the bottom wall (span s1) away from d_L1_009 to open the 0.60 m walkways from d_L1_006 and o_L1_002 to d_L1_009. |
| 8810 | 3 | relayout_room | r_L0_mutfak | memory: the same edit was rejected in round 1: group checks: G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge); G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove) | Re-solve the kitchen run and dining groups so the stove and fridge are actually built and visible and the dining set is replaced with a coherent model (a:F8, a:F9, a:N47). |
| 8812 | 3 | relayout_room | r_L0_mutfak | group checks: G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge); G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove) | Re-solve the kitchen run and dining groups with the second solver candidate so the stove and fridge are built and visible and the dining set is coherent (a:F8, a:F9, a:N47). |
| 8813 | 3 | relayout_room | r_L0_mutfak | group checks: G9 r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge); G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove) | Re-solve the kitchen run and dining groups with the third solver candidate so the stove and fridge are built and visible and the dining set is coherent (a:F8, a:F9, a:N47). |
| 8815 | 3 | swap_model | f_L0_036 | acceptance: pin_refused: f_L0_036: electric_stove: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:F8: the stove is planned but not visible in the scene; give it a real library model so it renders. |
| 8819 | 3 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 has no hard failures and high circulation (0.97), addressing the critical d_L0_004→d_L0_006 walkway and moving pieces off the windows they block. |
| 8821 | 3 | swap_model | f_L0_040 | pin_refused: f_L0_040: gen_fridge_japandi_3_38a9d0f8: a generated model (units guessed) while a real product of the type fits within the caps (3dwh_dff7590ce6f78822c852419d): the real model stays; swap to a real model of the type or use another tool | a:F9: the fridge is planned but not visible in the scene; give it a real library model so it renders. |
| 8823 | 3 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 6 more kept | Candidate 2 has no hard failures and high circulation (0.97), addressing the critical d_L0_004→d_L0_006 walkway and moving pieces off the windows they block. |
| 8826 | 3 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 6 more kept | Candidate 3 has no hard failures and high circulation (0.97), addressing the critical d_L0_004→d_L0_006 walkway and moving pieces off the windows they block. |
| 8830 | 3 | swap_model | f_L0_036 | pin_refused: f_L0_036: gen_stove_japandi_1_2c35be6c: a generated model (units guessed) while a real product of the type fits within the caps (3dwh_7fe10c8c3ab049f57787ba5f): the real model stays; swap to a real model of the type or use another tool | a:F8: the stove is planned but not visible; give it a real library model so it renders. |
| 8837 | 3 | move_piece | f_L1_014 | acceptance: finding G12:f_L1_014 is still there after the edit (wardrobe f_L1_014 (2.10 m) stands in front of window win_L1_008 (sill 0.90 m + 0.05)) | Shift wardrobe 0.05 m off wall w_L1_024 to clear the wall cut (S2) and room outline collision (F9), and out of the window band (G12). |
| 8844 | 3 | set_room_type | r_L1_oda | memory: the same edit was rejected in round 1: no_change: r_L1_oda is already a hall | The 3.1 m² room with a shoe cabinet is functionally an entrance/foyer, not a hall. Retype it to 'entrance' to match its actual use and contents. |
| 8845 | 3 | place_group | r_L1_soyunma_odasi | no_place: dressing group: no place passes the checks (dressing: no place passes the checks) | Room is a dressing room (Soyunma Odası) but lacks functional dressing furniture; placing the required dressing group resolves the empty_room finding. |
| 8855 | 3 | set_room_type | r_L0_oda | memory: the same edit was rejected in round 1: no_change: r_L0_oda is already a hall | 2.1 m² entrance/foyer with a door and window; hall is the closest valid type for this small entry space. |
| 8856 | 3 | rotate_piece | f_L1_011 | f_L1_011: clearance_ok, score: plausibility 70 -> 40 (F3 f_L1_011: wardrobe: its back is not on a wall (0.18 m off); F4 f_L1_011: wardrobe faces a wall 0.00 m in front of it; G13 f_L1_011: wardrobe f_L1_011: 0.00 m free in front, needs ≥ 0.80 m) | S3 finding: built front is 0 deg but planned 180 deg; rotating to face 0 deg (toward +X, away from the wall) aligns the built front with the actual orientation. |
| 8861 | 3 | swap_model | f_L1_011 | no_change: f_L1_011 already uses the model 3dwh_11916ad11dca0c0b94c659f6 | S3 finding: built front is 0° but planned 180°; swapping to a wardrobe model with correct front orientation to resolve the 180° front mismatch. |
| 8863 | 3 | swap_model | f_L1_011 | lower_quality: f_L1_011: hssd_3bc24e0ea79ade13d4703ca23ece1e4019f9b70b is rated 1.0 against 3.0 of the current model 3dwh_11916ad11dca0c0b94c659f6: a swap never takes a lower-rated model; choose one rated at least 2.8, or fix the view (camera, light) instead | S3 finding: built front is 0° but planned 180°; swapping to a different wardrobe model (Aspen 5-door) that may have correct front orientation to resolve the 180° front mismatch. |
| 9311 | 4 | swap_model | f_L0_026 | acceptance: pin_refused: f_L0_026: hssd_3f0778f68a489d3995e2e3f13d13e4a90fb500a8: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The washbasin is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F26) |
| 9314 | 4 | swap_model | f_L1_019 | acceptance: pin_refused: f_L1_019: hssd_16c33cffd5b62d0d5df5ed6dd607f690ce2ee7c7: audit: removed (a maker's logo or brand name on the model: the SAMSUNG logo on the control panel, part of the texture set this mesh family shares with the WF8704RSW (this model was not in any committed view yet); the same mesh family as hssd_031024e00569909d466d87df9fead90355ba29e5 (3853 faces, 3779 vertices, box 0.60 x 0.61 x 0.90 m; faces and vertices within 1%, two box sides within 1 cm, the third within 10%) with the same texture set (5 materials, 2 with a base colour, 4 images), whose render shows it; trademarks are not licensed (docs/milestone13.md §2.6)): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The washing machine is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F29) |
| 9316 | 4 | swap_model | f_L1_028 | acceptance: pin_refused: f_L1_028: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The shoe cabinet is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F32) |
| 9318 | 4 | set_exterior | exterior:site | acceptance: finding D3:d_L0_001 is still there after the edit (the edit does not change what the finding is about (the override sets site; the cause wrong_model needs no exterior slot); missing layer: a believable outdoor s) | Argus: The view is a flat, empty green field with no depth, planters, or detail, which makes the large windows look like they open onto a void. Adding a path, hedge, trees, and front court will create a believable outdoor scene. (fixes a:F56) |
| 9322 | 4 | swap_model | f_L0_007 | lower_quality: f_L0_007: 3dwh_a4a23730e4f99f069784415b is rated 3.0 against 5.0 of the current model abo_B075X4N3GM: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Argus: The armchair f_L0_007 is a 1970s rust-orange leather piece that clashes with the mid-century and modern pieces in the salon. The previous swap to 3dwh_d1ed36390489612fbb2a5baa was refused for lower quality (3.0 vs 5.0). The model 3dwh_a4a23 (fixes a:F70) |
| 9323 | 4 | swap_model | f_L0_014 | no_change: f_L0_014 already uses the model hssd_d3aaaa4c5f6f4c0f8ac9acffa625b527bf1ddc89 | Argus: The sofa f_L0_014 is a blocky tan leather piece that clashes with the mid-century egg chairs. The model hssd_d3aaaa4c5f6f4c0f8ac9acffa625b527bf1ddc89 is modern/scandinavian, which will harmonize with the rest of the room's furniture. (fixes a:F73) |
| 9330 | 4 | swap_model | f_L1_020 | pin_refused: f_L1_020: gen_floor_lamp_japandi_2_ef5fd39d: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07B4ZK8BR): the real model stays; swap to a real model of the type or use another tool | Argus: The current floor lamp is a generic modern tripod. Swapping to a japandi floor lamp with a paper-lantern style matches the reference's warm lighting. (fixes a:F87) |
| 9334 | 4 | set_exterior | exterior:ground,site,sun | acceptance: finding D3:d_L0_001 is still there after the edit (the edit does not change what the finding is about (the override sets ground, site, sun; the cause wrong_model needs no exterior slot); missing layer: a believa) | Argus: The judge calls ext_2 a grey-box massing study with flat overcast lighting, a single green plane and crude lollipop trees; the exterior needs sun, ground and site items. (fixes a:F99) |
| 9335 | 4 | set_exterior | exterior:sun | acceptance: finding D3:d_L0_001 is still there after the edit (the edit does not change what the finding is about (the override sets sun; the cause site needs site or ground); Argus: missing layer: a believable outdoor scen) | Argus: The judge says the windows are dark and flat, lacking inviting interior lighting; a sun in the scene will give the windows light and reflection. (fixes a:F101) |
| 9338 | 4 | swap_model | f_L0_020 | pin_refused: f_L0_020: gen_sink_kitchen_japandi_1_a61d924d: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Argus: The current parametric mesh is below library quality. The tried swap was refused for size mismatch (1.26 x 0.47 x 0.58 m does not fit a sink_kitchen). The model gen_sink_kitchen_japandi_1_a61d924d (1.06 x 0.49 x 0.80 m) is a real product th (fixes a:F132) |
| 9339 | 4 | swap_model | f_L0_026 | acceptance: pin_refused: f_L0_026: hssd_4d4709a41a152773f55c745958f1af7670dc59b7: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current model is a basic white bowl. The model hssd_4d4709a41a152773f55c745958f1af7670dc59b7 (0.46 x 0.35 x 0.59 m, minimal/scandinavian) is a real product that fits the 0.50 x 0.40 m footprint and matches the warm, high-end aesthetic. (fixes a:F135) |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F3 | minor | f_L1_025 | r_L1_oda_2 | - | drawn_layout | 1, 2, 3, 4 | the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall, and no free wall place (doors, windows, the other pieces) or partner lies within that reach, so no move clears the finding; the drawn layout is reported (CLAUDE.md: drawn furniture is kept) |
| F9 | major | f_L0_031 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| F9 | major | f_L0_032 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| G8 | minor | f_L0_020 | r_L0_mutfak | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| Q3 | critical | d_L1_001 | - | architect | guard | 3 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L1_hol | r_L1_hol | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q7 | minor | d_L1_003 | r_L1_soyunma_odasi | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | minor | f_L1_001 | r_L1_hol | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| RC | minor | sy_L0_002 | - | - | resolved_by_code | 1, 2, 3, 4 | a reading conflict the code already resolved (the drawing won, the item was moved to the symbols): it names no furniture piece or room, so there is nothing to edit; reported |
| S2 | major | f_L0_031 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| S2 | minor | f_L1_011 | r_L1_soyunma_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L0_006 | r_L0_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_007 | r_L0_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_016 | r_L0_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_015 | r_L1_ebeveyn_y_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | critical | d_L1_001 | - | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | critical | d_L1_004 | - | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | critical | d_L1_005 | - | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | critical | d_L1_010 | - | - | facade | 1, 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L0_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_005 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | o_L0_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | o_L0_005 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | o_L0_006 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | o_L1_006 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | o_L1_007 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_005 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_006 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | building | cut | 1 | 34418 | 32768 |
| 3 | r_L0_salon | cut | 1 | 11069 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | change | by (rule) | reason |
|---|---|---|---|---|---|---|---|
| f_L0_001 | piece | stair | r_L0_mutfak | adjusted_by_ai | size 2.20 x 2.15 m -> 2.20 x 2.73 m | architect (architect K1) | a riser of 0.214 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L0_002 | piece | kitchen_counter | r_L0_mutfak | adjusted_by_ai | - | code (architect F5) | architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_031 (kitchen_counter): one object read twice; built once |
| f_L0_003 | piece | kitchen_counter | r_L0_mutfak | inferred | - | - | drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_004 | piece | unknown | r_L0_mutfak | inferred, adjusted_by_ai | - | code (reading.kitchen_outline) | the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_005 | piece | unknown | r_L0_salon | inferred | - | - | outline 3.89 x 1.42 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L0_006 | piece | sofa | r_L0_salon | inferred, adjusted_by_ai | - | architect | moved 0.50 m clear of o_L0_005 (the answer to F3:o_L0_005) |
| f_L0_007 | piece | armchair | r_L0_salon | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_009 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside sofa f_L0_006 (2.12 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_010 | piece | bathtub | r_L0_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | type unknown -> bathtub; size 2.54 x 1.01 m -> 1.55 x 0.75 m | architect | the drawn outline 2.54 x 1.01 m at 161.5 deg is no bathtub where it stands (a misread or merged outline): the real product 1.55 x 0.75 m seated in it, its back on a wall of the room and along it, in a corner, 94% of it on the drawn outline, clear of the other drawn fixtures and the door swings, clear of f_L0_026 (the answer to AI.move_piece:f_L0_010) (plan crop recognition/crops/sym_L0_005_ctx.png) |
| f_L0_011 | piece | table_dining | r_L0_salon | inferred, adjusted_by_ai | size 1.69 x 1.69 m -> 1.00 x 1.00 m | Qwen/Qwen3.8-27B-FP8 | Argus: The glass dining table with an ornate base feels out of place in a modern minimalist salon; abo_B0853Q71J6 is a scandinavian/japandi/modern minimal table of matching size (0.99 x 0.99 x 0.75 m). (fixes a:F134) |
| f_L0_012 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_013 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_014 | piece | sofa | r_L0_salon | inferred, adjusted_by_ai | - | architect | moved 0.41 m clear of d_L0_001 (the answer to F3:d_L0_001) |
| f_L0_015 | piece | table_coffee | r_L0_salon | inferred | - | - | table_coffee: r_L0_salon misses it (r_L0_salon.seating (anchor f_L0_006) misses table_coffee) and the AI passes named it (pass 1 (qwen) answered table_coffee; pass 1 (qwen)'s reason names table_coffee); plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_016 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_017 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_018 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_019 | piece | armchair | r_L0_salon | inferred | - | - | armchair: the same drawn block (the same strokes (301 LINE here, within 2%)) and footprint (0.92 x 0.77 m, within 0.01 m) as f_L0_007, f_L0_016, f_L0_017, f_L0_018 (typed armchair): one block, one type; front: faces the coffee table f_L0_021 |
| f_L0_020 | piece | sink_kitchen | r_L0_mutfak | inferred | - | - | sink_kitchen: r_L0_mutfak.kitchen_run (anchor f_L0_002) misses sink_kitchen, and the type's product range fits 1.20 x 0.45 m (the only missing member of that size) |
| f_L0_021 | piece | table_coffee | r_L0_salon | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> table_coffee | code (ringed_table) | table_coffee: a drawn round floor_lamp (ai_two_pass) 0.66 m across with 4 seats around it (f_L0_016, f_L0_017, f_L0_018, f_L0_019) facing it: the table of the seating group, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png) |
| f_L0_024 | piece | toilet | r_L0_banyo | inferred | - | - | toilet: the same footprint (0.70 x 0.45 m) at the same plan position as f_L1_022 on level L1 (within 0.01 m) |
| f_L0_026 | piece | washbasin | r_L0_banyo | adjusted_by_ai | size 0.53 x 0.34 m -> 0.50 x 0.40 m | architect | the drawn outline 0.53 x 0.34 m at 0.0 deg is no washbasin where it stands (a misread or merged outline): the real product 0.50 x 0.40 m seated in it, its back on a wall of the room and along it, in a corner, 74% of it on the drawn outline, clear of the other drawn fixtures and the door swings, clear of f_L0_010 (the answer to AI.move_piece:f_L0_026) |
| f_L0_027 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dining chairs are a mismatched set of at least four different models. Swapping f_L0_027 to a modern/scandinavian chair (3dwh_040dd50cd138cbc316c9caec) is the first step toward unifying the set. The other chairs (f_L0_028, f_L0_029, f_L0 (fixes a:F75) |
| f_L0_028 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.04 m |
| f_L0_029 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The 0.07 m offset is a fit issue, not a placement error; a matching-footprint model lets the solver place it exactly. (fixes a:F119) |
| f_L0_030 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The 0.08 m offset is a fit issue; a matching-footprint model lets the solver place it exactly. (fixes a:F120) |
| f_L1_003 | piece | unknown | r_L1_hol | inferred | - | - | 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L1_004 | piece | bed_double | r_L1_cocuk_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The bed is a crude, blocky model; the proposed model is minimal/modern/scandinavian and fits the 1.94 x 1.90 m footprint. (fixes a:F78) |
| f_L1_005 | piece | dresser | r_L1_cocuk_odasi | inferred, adjusted_by_ai | - | architect | moved 0.46 m clear of d_L1_005 (the answer to AI.move_piece:f_L1_005) |
| f_L1_006 | piece | unknown | r_L1_cocuk_odasi | inferred | - | - | drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L1_007 | piece | bed_double | r_L1_cocuk_odasi | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_008 | piece | nightstand | r_L1_cocuk_odasi | adjusted_by_ai | - | code (architect F5) | architect F5: it cut f_L1_007 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built |
| f_L1_009 | piece | bathtub | r_L1_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | type unknown -> bathtub; size 2.42 x 0.98 m -> 1.55 x 0.75 m | architect | the drawn outline 2.42 x 0.98 m at 158.3 deg is no bathtub where it stands (a misread or merged outline): the real product 1.55 x 0.75 m seated in it, its back on a wall of the room and along it, in a corner, 93% of it on the drawn outline, clear of the other drawn fixtures and the door swings, clear of f_L1_023 (the answer to AI.move_piece:f_L1_009) (plan crop recognition/crops/sym_L1_006_ctx.png) |
| f_L1_010 | piece | bed_double | r_L1_ebeveyn_y_odasi | inferred | - | - | bed_double: the bedroom room misses its sleeping_double anchor (bed_double); the bedroom room misses its anchor (bed_double \| bed_single), and the type's product range fits 1.90 x 1.50 m (the only missing member of that size) |
| f_L1_011 | piece | wardrobe | r_L1_soyunma_odasi | inferred, adjusted_by_ai | type unknown -> wardrobe; size 2.27 x 0.85 m -> 2.27 x 0.60 m | code (wardrobe_run) | wardrobe: r_L1_soyunma_odasi is a dressing room: its program puts wardrobe runs along its walls (groups.yaml dressing); the drawn 2.27 x 0.85 m stands with its long side on a wall, its length fits a wardrobe run (0.80-3.20 m) and its depth is a wardrobe's (0.55-0.90 m drawn); the depth is outside the wardrobe's range (0.50-0.70 m): 0.60 m, the back kept on its wall, drawn_footprint kept (CLAUDE.md: a real product size) |
| f_L1_012 | piece | wardrobe | r_L1_soyunma_odasi | inferred, adjusted_by_ai | type unknown -> wardrobe; size 2.27 x 0.85 m -> 2.27 x 0.60 m | code (wardrobe_run) | wardrobe: r_L1_soyunma_odasi is a dressing room: its program puts wardrobe runs along its walls (groups.yaml dressing); the drawn 2.27 x 0.85 m stands with its long side on a wall, its length fits a wardrobe run (0.80-3.20 m) and its depth is a wardrobe's (0.55-0.90 m drawn); the depth is outside the wardrobe's range (0.50-0.70 m): 0.60 m, the back kept on its wall, drawn_footprint kept (CLAUDE.md: a real product size) |
| f_L1_013 | piece | bed_single | r_L1_oda_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Swap to a scandinavian/japandi bed with more texture and layering to address the plain white bedding finding (a:F141) |
| f_L1_014 | piece | wardrobe | r_L1_oda_2 | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 1.81 x 0.68 m (the only missing member of that size) |
| f_L1_015 | piece | armchair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The two wooden armchairs and the white wire chair are three different styles. Swapping the armchair to a modern/scandinavian model that matches the minimalist bed creates a cohesive set. (fixes a:F86) |
| f_L1_016 | piece | armchair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The grey quilted armchair does not match the white armchair or the rustic wood elements; 3dwh_f6bd91f124d68b40f2957392 is a minimal/modern/scandinavian armchair of matching size (0.86 x 0.76 x 0.76 m) that unifies the set. (fixes a:F139) |
| f_L1_017 | piece | dresser | r_L1_oda_2 | inferred | - | - | dresser: the documents name it: the text '*SIFONIYER' (TEXT:29ABD3) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.55 m within 40% |
| f_L1_018 | piece | shower | r_L1_dus | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current shower model looks like a broken model. Swapping to a minimal/modern glass partition fixes the visual mess. (fixes a:F85) |
| f_L1_019 | piece | washing_machine | r_L1_banyo | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type washbasin -> washing_machine | code, then Qwen/Qwen3.8-27B-FP8 (name_text) | washing_machine: the documents name it: the text 'çamaşır mak.' (TEXT:2772EB) is written 0.01 m from it; the ai_two_pass reading said washbasin; the named type's product range fits 0.60 x 0.60 m and the room holds it (trust order: the documents' text before AI vision); plan crop recognition/crops/sym_L1_016_ctx.png; then: Washing machine front faced a wall at 270°; its front should face into the room (90°) so the door is usable. |
| f_L1_020 | piece | floor_lamp | r_L1_ebeveyn_y_odasi | inferred | - | - | floor_lamp: named by an AI pass and the only named type that fits the size (0.58 x 0.58 m), the bedroom room and the position (others fitting: armchair, ottoman, potted_plant, side_table) |
| f_L1_023 | piece | washbasin | r_L1_banyo | adjusted_by_ai | size 0.53 x 0.34 m -> 0.60 x 0.45 m | architect | the drawn outline 0.53 x 0.34 m at 0.0 deg is no washbasin where it stands (a misread or merged outline): the real product 0.60 x 0.45 m seated in it, its back on a wall of the room and along it, in a corner, 67% of it on the drawn outline, clear of the other drawn fixtures and the door swings, clear of f_L1_009 (the answer to AI.move_piece:f_L1_023) |
| f_L1_024 | piece | nightstand | r_L1_ebeveyn_y_odasi | inferred | - | - | nightstand: r_L1_ebeveyn_y_odasi.sleeping_double (anchor f_L1_010) misses nightstand; r_L1_ebeveyn_y_odasi.sleeping_double (anchor f_L1_010) misses nightstand, and the type's product range fits 0.42 x 0.40 m (the only missing member of that size) |
| f_L1_025 | piece | nightstand | r_L1_oda_2 | inferred | - | - | nightstand: the same drawn block (the same strokes (1 CIRCLE, 14 LINE here, within 2%)) and footprint (0.42 x 0.40 m, within 0.01 m) as f_L1_024 (typed nightstand): one block, one type; front: faces the way its bed f_L1_013 faces |
| f_L1_026 | piece | nightstand | r_L1_ebeveyn_y_odasi | inferred | - | - | nightstand: the same drawn block (the same strokes (1 CIRCLE, 14 LINE here, within 2%)) and footprint (0.42 x 0.40 m, within 0.01 m) as f_L1_024, f_L1_025 (typed nightstand): one block, one type; front: faces the way its bed f_L1_010 faces |
| f_L1_027 | piece | washbasin | r_L1_dus | inferred, adjusted_by_ai | - | code (reading.fixed_equipment) | misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026): through a wall: moved 0.05 m to the nearest free spot (plan crop recognition/crops/sym_L1_024_ctx.png) |
| f_L0_031 | piece | kitchen_counter | r_L0_mutfak | inferred, adjusted_by_ai | type unknown -> kitchen_counter; size 3.99 x 2.40 m -> 2.40 x 0.60 m | code (reading.kitchen_outline) | the kitchen run drawn as one 3.99 x 2.40 m outline f_L0_004 with its fixtures (sink: 8 circles) in the kitchen: a counter leg 2.40 x 0.60 m along its wall side, facing the room (inferred); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_032 | piece | kitchen_counter | r_L0_mutfak | inferred, adjusted_by_ai | type unknown -> kitchen_counter; size 3.99 x 2.40 m -> 2.40 x 0.60 m | code (reading.kitchen_outline) | the kitchen run drawn as one 3.99 x 2.40 m outline f_L0_004 with its fixtures (sink: 8 circles) in the kitchen: a counter leg 2.40 x 0.60 m along its wall side, facing the room (inferred); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L1_028 | piece | shoe_cabinet | r_L1_oda | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_028: the piece is not built |
| f_L0_036 | piece | stove | r_L0_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The stove is missing from the render. Swapping to a different model may resolve the visibility issue. (fixes a:F27) |
| f_L0_037 | piece | table_dining | r_L0_mutfak | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_037: the piece is not built |
| f_L0_038 | piece | chair | r_L0_mutfak | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_038: the piece is not built |
| f_L0_039 | piece | chair | r_L0_mutfak | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_039: the piece is not built |
| f_L0_040 | piece | fridge | r_L0_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | a:F9: the fridge is planned but not visible; use the real product model the code says fits so it renders. |
| f_L1_029 | piece | desk | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_029: the piece is not built |
| f_L1_030 | piece | office_chair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_030: the piece is not built |
| f_L1_032 | piece | desk | r_L1_cocuk_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_032: the piece is not built |
| f_L1_033 | piece | office_chair | r_L1_cocuk_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_033: the piece is not built |
| f_L1_034 | piece | shoe_cabinet | r_L1_hol | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_034: the piece is not built |
| f_L0_043 | piece | sofa | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (2 reference photos)) |
| f_L0_044 | piece | table_coffee | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (2 reference photos)) |
| f_L0_045 | piece | armchair | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (2 reference photos)) |
| f_L0_046 | piece | armchair | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots, a rug and a lantern (2 reference photos)) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_L1_dresser_1 | - | ![](agent/r1_cam_L1_dresser_1_after.jpg) |
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_banyo_2 | ![](agent/r1_cam_r_L0_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_banyo_2_after.jpg) |
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
| 1 | cam_r_L1_dus_2 | ![](agent/r1_cam_r_L1_dus_2_before.jpg) | ![](agent/r1_cam_r_L1_dus_2_after.jpg) |
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
| 2 | cam_L1_dresser_1 | ![](agent/r2_cam_L1_dresser_1_before.jpg) | ![](agent/r2_cam_L1_dresser_1_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_banyo_2 | ![](agent/r2_cam_r_L0_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_2_after.jpg) |
| 2 | cam_r_L0_mutfak_1 | ![](agent/r2_cam_r_L0_mutfak_1_before.jpg) | ![](agent/r2_cam_r_L0_mutfak_1_after.jpg) |
| 2 | cam_r_L0_mutfak_2 | ![](agent/r2_cam_r_L0_mutfak_2_before.jpg) | ![](agent/r2_cam_r_L0_mutfak_2_after.jpg) |
| 2 | cam_r_L0_mutfak_3 | ![](agent/r2_cam_r_L0_mutfak_3_before.jpg) | ![](agent/r2_cam_r_L0_mutfak_3_after.jpg) |
| 2 | cam_r_L0_salon_1 | ![](agent/r2_cam_r_L0_salon_1_before.jpg) | ![](agent/r2_cam_r_L0_salon_1_after.jpg) |
| 2 | cam_r_L0_salon_2 | ![](agent/r2_cam_r_L0_salon_2_before.jpg) | ![](agent/r2_cam_r_L0_salon_2_after.jpg) |
| 2 | cam_r_L0_salon_3 | ![](agent/r2_cam_r_L0_salon_3_before.jpg) | ![](agent/r2_cam_r_L0_salon_3_after.jpg) |
| 2 | cam_r_L1_banyo_1 | ![](agent/r2_cam_r_L1_banyo_1_before.jpg) | ![](agent/r2_cam_r_L1_banyo_1_after.jpg) |
| 2 | cam_r_L1_cocuk_odasi_1 | ![](agent/r2_cam_r_L1_cocuk_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_cocuk_odasi_1_after.jpg) |
| 2 | cam_r_L1_cocuk_odasi_2 | ![](agent/r2_cam_r_L1_cocuk_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_cocuk_odasi_2_after.jpg) |
| 2 | cam_r_L1_cocuk_odasi_3 | ![](agent/r2_cam_r_L1_cocuk_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_cocuk_odasi_3_after.jpg) |
| 2 | cam_r_L1_dus_1 | ![](agent/r2_cam_r_L1_dus_1_before.jpg) | ![](agent/r2_cam_r_L1_dus_1_after.jpg) |
| 2 | cam_r_L1_dus_2 | ![](agent/r2_cam_r_L1_dus_2_before.jpg) | ![](agent/r2_cam_r_L1_dus_2_after.jpg) |
| 2 | cam_r_L1_ebeveyn_y_odasi_1 | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_1_after.jpg) |
| 2 | cam_r_L1_ebeveyn_y_odasi_2 | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_2_after.jpg) |
| 2 | cam_r_L1_ebeveyn_y_odasi_3 | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_3_after.jpg) |
| 2 | cam_r_L1_hol_1 | ![](agent/r2_cam_r_L1_hol_1_before.jpg) | ![](agent/r2_cam_r_L1_hol_1_after.jpg) |
| 2 | cam_r_L1_oda_1 | ![](agent/r2_cam_r_L1_oda_1_before.jpg) | ![](agent/r2_cam_r_L1_oda_1_after.jpg) |
| 2 | cam_r_L1_oda_2_1 | ![](agent/r2_cam_r_L1_oda_2_1_before.jpg) | ![](agent/r2_cam_r_L1_oda_2_1_after.jpg) |
| 2 | cam_r_L1_oda_2_2 | ![](agent/r2_cam_r_L1_oda_2_2_before.jpg) | ![](agent/r2_cam_r_L1_oda_2_2_after.jpg) |
| 2 | cam_r_L1_oda_2_3 | ![](agent/r2_cam_r_L1_oda_2_3_before.jpg) | ![](agent/r2_cam_r_L1_oda_2_3_after.jpg) |
| 2 | cam_r_L1_soyunma_odasi_1 | ![](agent/r2_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 2 | cam_r_L1_soyunma_odasi_2 | ![](agent/r2_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_4 | ![](agent/r2_ext_4_before.jpg) | ![](agent/r2_ext_4_after.jpg) |
| 2 | ext_5 | ![](agent/r2_ext_5_before.jpg) | ![](agent/r2_ext_5_after.jpg) |
| 2 | ext_6 | ![](agent/r2_ext_6_before.jpg) | ![](agent/r2_ext_6_after.jpg) |
| 3 | cam_r_L0_mutfak_1 | ![](agent/r3_cam_r_L0_mutfak_1_before.jpg) | ![](agent/r3_cam_r_L0_mutfak_1_after.jpg) |
| 3 | cam_r_L0_mutfak_2 | ![](agent/r3_cam_r_L0_mutfak_2_before.jpg) | ![](agent/r3_cam_r_L0_mutfak_2_after.jpg) |
| 3 | cam_r_L0_mutfak_3 | ![](agent/r3_cam_r_L0_mutfak_3_before.jpg) | ![](agent/r3_cam_r_L0_mutfak_3_after.jpg) |
| 3 | cam_r_L1_banyo_1 | ![](agent/r3_cam_r_L1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L1_banyo_1_after.jpg) |
| 3 | cam_r_L1_oda_1 | ![](agent/r3_cam_r_L1_oda_1_before.jpg) | ![](agent/r3_cam_r_L1_oda_1_after.jpg) |
| 3 | cam_r_L1_soyunma_odasi_1 | ![](agent/r3_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 4 | cam_L1_dresser_1 | ![](agent/r4_cam_L1_dresser_1_before.jpg) | ![](agent/r4_cam_L1_dresser_1_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_banyo_2 | ![](agent/r4_cam_r_L0_banyo_2_before.jpg) | ![](agent/r4_cam_r_L0_banyo_2_after.jpg) |
| 4 | cam_r_L0_mutfak_1 | ![](agent/r4_cam_r_L0_mutfak_1_before.jpg) | ![](agent/r4_cam_r_L0_mutfak_1_after.jpg) |
| 4 | cam_r_L0_mutfak_2 | ![](agent/r4_cam_r_L0_mutfak_2_before.jpg) | ![](agent/r4_cam_r_L0_mutfak_2_after.jpg) |
| 4 | cam_r_L0_mutfak_3 | ![](agent/r4_cam_r_L0_mutfak_3_before.jpg) | ![](agent/r4_cam_r_L0_mutfak_3_after.jpg) |
| 4 | cam_r_L0_salon_1 | ![](agent/r4_cam_r_L0_salon_1_before.jpg) | ![](agent/r4_cam_r_L0_salon_1_after.jpg) |
| 4 | cam_r_L0_salon_2 | ![](agent/r4_cam_r_L0_salon_2_before.jpg) | ![](agent/r4_cam_r_L0_salon_2_after.jpg) |
| 4 | cam_r_L0_salon_3 | ![](agent/r4_cam_r_L0_salon_3_before.jpg) | ![](agent/r4_cam_r_L0_salon_3_after.jpg) |
| 4 | cam_r_L1_banyo_1 | ![](agent/r4_cam_r_L1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L1_banyo_1_after.jpg) |
| 4 | cam_r_L1_cocuk_odasi_1 | ![](agent/r4_cam_r_L1_cocuk_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_cocuk_odasi_1_after.jpg) |
| 4 | cam_r_L1_cocuk_odasi_2 | ![](agent/r4_cam_r_L1_cocuk_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_cocuk_odasi_2_after.jpg) |
| 4 | cam_r_L1_cocuk_odasi_3 | ![](agent/r4_cam_r_L1_cocuk_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_cocuk_odasi_3_after.jpg) |
| 4 | cam_r_L1_dus_1 | ![](agent/r4_cam_r_L1_dus_1_before.jpg) | ![](agent/r4_cam_r_L1_dus_1_after.jpg) |
| 4 | cam_r_L1_dus_2 | ![](agent/r4_cam_r_L1_dus_2_before.jpg) | ![](agent/r4_cam_r_L1_dus_2_after.jpg) |
| 4 | cam_r_L1_ebeveyn_y_odasi_1 | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_1_after.jpg) |
| 4 | cam_r_L1_ebeveyn_y_odasi_2 | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_2_after.jpg) |
| 4 | cam_r_L1_ebeveyn_y_odasi_3 | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_3_after.jpg) |
| 4 | cam_r_L1_hol_1 | ![](agent/r4_cam_r_L1_hol_1_before.jpg) | ![](agent/r4_cam_r_L1_hol_1_after.jpg) |
| 4 | cam_r_L1_oda_1 | ![](agent/r4_cam_r_L1_oda_1_before.jpg) | ![](agent/r4_cam_r_L1_oda_1_after.jpg) |
| 4 | cam_r_L1_oda_2_1 | ![](agent/r4_cam_r_L1_oda_2_1_before.jpg) | ![](agent/r4_cam_r_L1_oda_2_1_after.jpg) |
| 4 | cam_r_L1_oda_2_2 | ![](agent/r4_cam_r_L1_oda_2_2_before.jpg) | ![](agent/r4_cam_r_L1_oda_2_2_after.jpg) |
| 4 | cam_r_L1_oda_2_3 | ![](agent/r4_cam_r_L1_oda_2_3_before.jpg) | ![](agent/r4_cam_r_L1_oda_2_3_after.jpg) |
| 4 | cam_r_L1_soyunma_odasi_1 | ![](agent/r4_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 4 | cam_r_L1_soyunma_odasi_2 | ![](agent/r4_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 4 | ext_1 | ![](agent/r4_ext_1_before.jpg) | ![](agent/r4_ext_1_after.jpg) |
| 4 | ext_2 | ![](agent/r4_ext_2_before.jpg) | ![](agent/r4_ext_2_after.jpg) |
| 4 | ext_3 | ![](agent/r4_ext_3_before.jpg) | ![](agent/r4_ext_3_after.jpg) |
| 4 | ext_4 | ![](agent/r4_ext_4_before.jpg) | ![](agent/r4_ext_4_after.jpg) |
| 4 | ext_5 | ![](agent/r4_ext_5_before.jpg) | ![](agent/r4_ext_5_after.jpg) |
| 4 | ext_6 | ![](agent/r4_ext_6_before.jpg) | ![](agent/r4_ext_6_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- no brief.yaml in /workspace/repo/projects/real06: every brief value is a default
