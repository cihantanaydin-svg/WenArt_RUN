# Final report: synthetic-03

50 views: 36 polished, 14 Cycles (gate 2, room 12). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 50 |
| polished | 36 |
| Cycles | 14 (gate 2, room 12) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 1 |
| rooms mixing polished and Cycles | 2 |
| advisory | yes |
| advisory flags | 4 |
| exposure | -0.83 .. +7.17 EV (0 at a limit), modes auto |
| window pull | 20 view(s), -4 .. -1 EV |
| camera policy | search 50 |
| camera score (min / mean / max) | 1.45 / 2.95 / 4.51 |
| rooms by number of views | 2 with 1, 3 with 2, 14 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 37.4 s / 3.4 min / 25.2 s |
| seconds: polish / gate / check | 9.8 min / 43.0 s / 11.4 min |
| brief polish | yes (default, not in brief.yaml) |

## Advisory flags and open items

- vision check advisory: removal_flagged None misses >= 0.8 (no data); removal_confirmed None misses >= 0.6 (no data); insertion None misses >= 0.6 (no data)
- check target missed: removal_flagged - (needs >= 0.8), no data
- check target missed: removal_confirmed - (needs >= 0.6), no data
- check target missed: insertion - (needs >= 0.6), no data

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 98.4 % (limit 95 %), 64 comparisons |
| negative controls rejected | 98.9 % (limit 90 %), 176 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L-1: [contact_L-1.jpg](contact_L-1.jpg)

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | -0.83 | - | search 1.48 | A3 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | -0.83 | - | search 1.45 | D1 A2 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_hol_1 | r_L-1_hol | L-1 | cycles | room | - | - | ok | - | - | +0.33 | - | search 3.65 | D4 A2 | 0 | no | [preview](cam_r_L-1_hol_1_final_preview.jpg) [plan](cam_r_L-1_hol_1_plan.jpg) |
| cam_r_L-1_hol_2 | r_L-1_hol | L-1 | cycles | room | - | - | info | - | - | +0.17 | - | search 2.83 | D2 A2 | 0 | no | [preview](cam_r_L-1_hol_2_final_preview.jpg) [plan](cam_r_L-1_hol_2_plan.jpg) |
| cam_r_L-1_hol_3 | r_L-1_hol | L-1 | cycles | room | - | - | info | - | - | +0.50 | - | search 2.82 | D2 A1 | 0 | no | [preview](cam_r_L-1_hol_3_final_preview.jpg) [plan](cam_r_L-1_hol_3_plan.jpg) |
| cam_r_L-1_kiler_1 | r_L-1_kiler | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | - | search 2.57 | D1 | 0 | no | [preview](cam_r_L-1_kiler_1_final_preview.jpg) [plan](cam_r_L-1_kiler_1_plan.jpg) |
| cam_r_L-1_kiler_2 | r_L-1_kiler | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +0.33 | - | search 2.57 | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_final_preview.jpg) [plan](cam_r_L-1_kiler_2_plan.jpg) |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | - | search 2.62 | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_1_final_preview.jpg) [plan](cam_r_L-1_kiler_2_1_plan.jpg) |
| cam_r_L-1_kiler_2_2 | r_L-1_kiler_2 | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | - | search 2.61 | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_2_final_preview.jpg) [plan](cam_r_L-1_kiler_2_2_plan.jpg) |
| cam_r_L-1_kiler_2_3 | r_L-1_kiler_2 | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +0.17 | - | search 2.56 | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_3_final_preview.jpg) [plan](cam_r_L-1_kiler_2_3_plan.jpg) |
| cam_r_L-1_kiler_3 | r_L-1_kiler | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.50 | - | search 2.53 | D1 | 0 | no | [preview](cam_r_L-1_kiler_3_final_preview.jpg) [plan](cam_r_L-1_kiler_3_plan.jpg) |
| cam_r_L-1_wc_1 | r_L-1_wc | L-1 | cycles | gate | - | - | info | - | - | -0.83 | - | search 2.35 | D1 A1 | 0 | no | [preview](cam_r_L-1_wc_1_final_preview.jpg) [plan](cam_r_L-1_wc_1_plan.jpg) |
| cam_r_L-1_wc_2 | r_L-1_wc | L-1 | polished | - | a3 s 0.125 depth x0.8 | accept | info | info | not preferred 0/4 | -0.67 | - | search 2.33 | D1 A1 | 0 | no | [preview](cam_r_L-1_wc_2_final_preview.jpg) [plan](cam_r_L-1_wc_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 0/4 | +0.00 | -1 | search 4.51 | D2 A2 | 0 | no | [preview](cam_r_L-1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_1_plan.jpg) |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | -1 | search 4.42 | D2 A2 | 0 | no | [preview](cam_r_L-1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.17 | -1 | search 4.01 | D2 A1 | 0 | no | [preview](cam_r_L-1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_3_plan.jpg) |
| cam_r_L0_antre_1 | r_L0_antre | L0 | cycles | gate | - | - | ok | - | - | +0.17 | - | search 3.78 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_antre_2 | r_L0_antre | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 3.74 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_2_final_preview.jpg) [plan](cam_r_L0_antre_2_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.33 | - | search 3.77 | D4 A2 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.67 | - | search 2.92 | D3 A2 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_hol_3 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.67 | - | search 2.88 | D3 A2 | 0 | no | [preview](cam_r_L0_hol_3_final_preview.jpg) [plan](cam_r_L0_hol_3_plan.jpg) |
| cam_r_L0_kiler_1 | r_L0_kiler | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.83 | -2 | search 2.51 | D2 | 1 | no | [preview](cam_r_L0_kiler_1_final_preview.jpg) [plan](cam_r_L0_kiler_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +5.00 | -3 | search 2.98 | D7 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.67 | -3 | search 2.90 | D6 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.50 | -3 | search 2.01 | D5 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 2/4 | +5.17 | -4 | search 3.38 | D5 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 2/4 | +5.00 | - | search 3.38 | D5 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +5.00 | - | search 3.28 | D4 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_wc_1 | r_L0_wc | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | -0.67 | - | search 2.48 | D3 | 0 | no | [preview](cam_r_L0_wc_1_final_preview.jpg) [plan](cam_r_L0_wc_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +6.17 | - | search 4.24 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +7.17 | -3 | search 3.42 | D5 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | +5.67 | - | search 3.04 | D2 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_balkon_1 | r_L1_balkon | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.83 | -1 | search 1.83 | D1 | 0 | no | [preview](cam_r_L1_balkon_1_final_preview.jpg) [plan](cam_r_L1_balkon_1_plan.jpg) |
| cam_r_L1_balkon_2 | r_L1_balkon | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.67 | -2 | search 1.83 | D1 | 0 | no | [preview](cam_r_L1_balkon_2_final_preview.jpg) [plan](cam_r_L1_balkon_2_plan.jpg) |
| cam_r_L1_balkon_3 | r_L1_balkon | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.17 | - | search 1.76 | D1 | 0 | no | [preview](cam_r_L1_balkon_3_final_preview.jpg) [plan](cam_r_L1_balkon_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | +5.33 | - | search 2.75 | D1 A3 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +5.67 | - | search 2.08 | D1 A2 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.83 | -2 | search 1.94 | D2 A1 | 0 | no | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.33 | -3 | search 3.74 | D2 A5 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.67 | -1 | search 3.19 | D1 A4 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.67 | -1 | search 3.16 | D1 A4 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +4.50 | -3 | search 3.64 | D1 A6 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.33 | -2 | search 3.33 | D2 A6 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.67 | -3 | search 3.10 | D2 A6 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +0.50 | - | search 3.61 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +0.50 | - | search 2.99 | D1 A1 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +0.50 | - | search 2.96 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | cycles | room | - | - | ok | - | - | +5.83 | - | search 3.43 | D1 A4 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | cycles | room | - | - | info | - | - | +6.00 | -2 | search 3.07 | D2 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | cycles | room | - | - | ok | - | - | +6.17 | -2 | search 3.06 | D2 A4 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 2 | 2 | 0 | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_hol | hall | L-1 | 3 | 0 | 3 | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_kiler | storage | L-1 | 3 | 3 | 0 | cam_r_L-1_kiler_1, cam_r_L-1_kiler_2, cam_r_L-1_kiler_3 |
| r_L-1_kiler_2 | storage | L-1 | 3 | 3 | 0 | cam_r_L-1_kiler_2_1, cam_r_L-1_kiler_2_2, cam_r_L-1_kiler_2_3 |
| r_L-1_wc | wc | L-1 | 2 | 1 | 1 | cam_r_L-1_wc_1, cam_r_L-1_wc_2 |
| r_L-1_yatak_odasi | bedroom | L-1 | 3 | 3 | 0 | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | hall | L0 | 2 | 1 | 1 | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_hol | hall | L0 | 3 | 0 | 3 | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_kiler | storage | L0 | 1 | 1 | 0 | cam_r_L0_kiler_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 3 | 0 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 3 | 0 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | wc | L0 | 1 | 1 | 0 | cam_r_L0_wc_1 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 3 | 0 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | balcony | L1 | 3 | 3 | 0 | cam_r_L1_balkon_1, cam_r_L1_balkon_2, cam_r_L1_balkon_3 |
| r_L1_banyo | bathroom | L1 | 3 | 3 | 0 | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | hall | L1 | 3 | 0 | 3 | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

### Why Cycles

- cam_r_L-1_hol_1: room: polish: room
- cam_r_L-1_hol_2: room: polish: room
- cam_r_L-1_hol_3: room: polish: room
- cam_r_L-1_wc_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L0_antre_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L0_hol_1: room: polish: room
- cam_r_L0_hol_2: room: polish: room
- cam_r_L0_hol_3: room: polish: room
- cam_r_L1_hol_1: room: polish: room
- cam_r_L1_hol_2: room: polish: room
- cam_r_L1_hol_3: room: polish: room
- cam_r_L1_yatak_odasi_1: room: polish: room
- cam_r_L1_yatak_odasi_2: room: polish: room
- cam_r_L1_yatak_odasi_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | cycles | disputed | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_1 | cycles | disputed | f_L-1_010 | toilet | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_1 | cycles | missing | f_L-1_011 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_1 | polished | disputed | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_1 | polished | missing | f_L-1_011 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_2 | cycles | missing | f_L-1_010 | toilet | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_2 | polished | missing | f_L-1_010 | toilet | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_hol_2 | cycles | missing | d_L-1_002 | door | optional | from_documents | kat_planlari.pdf p1 path:12 vector 1.00 | info | - |
| cam_r_L-1_hol_3 | cycles | missing | d_L-1_003 | door | optional | from_documents | kat_planlari.pdf p1 path:14 vector 1.00 | info | - |
| cam_r_L-1_wc_1 | cycles | disputed | d_L-1_004 | door | optional | from_documents | kat_planlari.pdf p1 path:16 vector 1.00 | info | - |
| cam_r_L-1_wc_2 | cycles | disputed | f_L-1_008 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_wc_2 | polished | disputed | f_L-1_008 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_hol_1 | cycles | missing | d_L0_005 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11C KAPI_90 vector 1.00; kat_planlari.pdf p2 path:19 vector 1.00 | info | - |
| cam_r_L0_hol_2 | cycles | disputed | d_L0_005 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11C KAPI_90 vector 1.00; kat_planlari.pdf p2 path:19 vector 1.00 | info | - |
| cam_r_L0_hol_3 | cycles | missing | d_L0_006 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11E KAPI_80 vector 1.00; kat_planlari.pdf p2 path:21 vector 1.00 | info | - |
| cam_r_L0_yatak_odasi_1 | cycles | disputed | f_L0_018 | dresser | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:150 SIFONYER vector 1.00 | info | - |
| cam_r_L0_yatak_odasi_1 | polished | disputed | f_L0_018 | dresser | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:150 SIFONYER vector 1.00 | info | - |
| cam_r_L0_yatak_odasi_3 | cycles | disputed | f_L0_014 | bed_double | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:148 YATAK_CIFT vector 1.00 | info | - |
| cam_r_L1_banyo_1 | cycles | disputed | f_L1_020 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | polished | missing | f_L1_020 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_2 | cycles | disputed | f_L1_020 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_2 | polished | disputed | f_L1_020 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | disputed | f_L1_020 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | polished | disputed | f_L1_020 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | polished | disputed | f_L1_003 | nightstand | required | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_3 | cycles | missing | f_L1_003 | nightstand | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_3 | cycles | disputed | dec_L1_004 | plant | optional | added_by_ai | rule: potted plant in a free corner | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_3 | polished | disputed | f_L1_001 | bed_double | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_3 | polished | disputed | f_L1_003 | nightstand | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_3 | polished | disputed | dec_L1_004 | plant | optional | added_by_ai | rule: potted plant in a free corner | info | added_by_ai: render/polish issue, not a document conflict |

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- f_L0_021

Unverified pieces in view:

- cam_r_L0_kiler_1: f_L0_021

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L0_salon | Label says 24,00 m², polygon gives 23,50 m² (2.1%) | within tolerance (3%), kept polygon from mobilya_plani.dxf |
| c_002 | dimension_vs_measured | w_L-1_004 | kat_planlari.pdf p1: dimension text 3,99 vs measured 3.80 m (5.0%) | kept measured geometry (vector PDF) |
| c_003 | count_mismatch | win_L0_004 | Zemin Kat: mobilya_plani.dxf has 6 windows, kat_planlari.pdf p2 has 5 | DXF wins over vector PDF, window kept |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L-1_wc | cam_r_L-1_wc_2 | cam_r_L-1_wc_1 (gate) | ok |
| r_L0_antre | cam_r_L0_antre_2 | cam_r_L0_antre_1 (gate) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_hol (rung None), r_L0_hol (rung None), r_L1_hol (rung None), r_L1_yatak_odasi (rung None).

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| polish base | Tongyi-MAI/Z-Image-Turbo | f332072aa78be7aecdf3ee76d5c247082da564a6 | Apache-2.0 | polish_manifest.json |
| polish controlnet | alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 | 5155fc56d17821007d6f62ac192c09e0f0e72016 | Apache-2.0 | polish_manifest.json |
| gate depth | depth-anything/Depth-Anything-V2-Small-hf | 5426e4f0f36572d16453bbda7a8389317b1bef99 | Apache-2.0 | polish_manifest.json |
| gate sam | facebook/sam2.1-hiera-large | 665f8e2ad61cf5f53d65644ff27c8ee525124610 | Apache-2.0 | polish_manifest.json |
| gate dino | facebook/dinov2-base | f9e44c814b77203eaa57a6bdbbd535f21ede1415 | Apache-2.0 | polish_manifest.json |
| check qwen | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | check_manifest.json |
| check glm | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | check_manifest.json |

Assets: textures CC0 x 5; furniture/decor models CC0 x 34 (parametric meshes need no licence).

## Stages

This run (`20261003-014522-full-20261003T015157Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 10.6 s | earlier outputs without run records moved to /workspace/outputs-archive/synthetic-03-20261003T015157Z |
| fit | ok | 2.2 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.5 s | - |
| layout | ok | 81.9 s | - |
| assets | ok | 1.0 s | - |
| decor | ok | 2.0 s | - |
| refit | ok | 2.2 s | - |
| build | ok | 52.1 s | - |
| render | ok | 5.9 min | - |
| controls | ok | 82.5 s | - |
| gate | ok | 2.5 min | gate decision ok |
| polish | ok | 14.1 min | - |
| expected | ok | 26.6 s | - |
| check | ok | 9.2 min | - |
| combine | ok | 43.5 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
