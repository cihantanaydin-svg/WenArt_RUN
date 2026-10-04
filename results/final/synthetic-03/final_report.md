# Final report: synthetic-03

44 views: 27 polished, 17 Cycles (gate 1, room 15, vision_check 1). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 44 |
| polished | 27 |
| Cycles | 17 (gate 1, room 15, vision_check 1) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 1 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 5 |
| exposure | -0.83 .. +6.83 EV (0 at a limit), modes auto |
| window pull | 18 view(s), -3 .. -1 EV |
| camera policy | search 44 |
| camera score (min / mean / max) | 1.40 / 2.96 / 3.93 |
| rooms by number of views | 5 with 1, 3 with 2, 11 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 44.5 s / 119.2 s / 15.5 s |
| seconds: polish / gate / check | 4.2 min / 9.2 min / 18.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 19 |

## Advisory flags and open items

- vision check advisory: removal_flagged 0.75 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.750 (needs >= 0.8)
- check target missed: removal_confirmed 0.500 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- the polish added an object in cam_r_L1_balkon_1: the Cycles render is final

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 98.4 % (limit 95 %), 64 comparisons |
| negative controls rejected | 96.6 % (limit 90 %), 176 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L-1: [contact_L-1.jpg](contact_L-1.jpg)

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- r_L-1_banyo: [contact_sbs_r_L-1_banyo.jpg](contact_sbs_r_L-1_banyo.jpg)

- r_L-1_hol: [contact_sbs_r_L-1_hol.jpg](contact_sbs_r_L-1_hol.jpg)

- r_L-1_kiler: [contact_sbs_r_L-1_kiler.jpg](contact_sbs_r_L-1_kiler.jpg)

- r_L-1_kiler_2: [contact_sbs_r_L-1_kiler_2.jpg](contact_sbs_r_L-1_kiler_2.jpg)

- r_L-1_wc: [contact_sbs_r_L-1_wc.jpg](contact_sbs_r_L-1_wc.jpg)

- r_L-1_yatak_odasi: [contact_sbs_r_L-1_yatak_odasi.jpg](contact_sbs_r_L-1_yatak_odasi.jpg)

- r_L0_antre: [contact_sbs_r_L0_antre.jpg](contact_sbs_r_L0_antre.jpg)

- r_L0_hol: [contact_sbs_r_L0_hol.jpg](contact_sbs_r_L0_hol.jpg)

- r_L0_kiler: [contact_sbs_r_L0_kiler.jpg](contact_sbs_r_L0_kiler.jpg)

- r_L0_mutfak: [contact_sbs_r_L0_mutfak.jpg](contact_sbs_r_L0_mutfak.jpg)

- r_L0_salon: [contact_sbs_r_L0_salon.jpg](contact_sbs_r_L0_salon.jpg)

- r_L0_wc: [contact_sbs_r_L0_wc.jpg](contact_sbs_r_L0_wc.jpg)

- r_L0_yatak_odasi: [contact_sbs_r_L0_yatak_odasi.jpg](contact_sbs_r_L0_yatak_odasi.jpg)

- r_L1_balkon: [contact_sbs_r_L1_balkon.jpg](contact_sbs_r_L1_balkon.jpg)

- r_L1_banyo: [contact_sbs_r_L1_banyo.jpg](contact_sbs_r_L1_banyo.jpg)

- r_L1_cocuk_odasi: [contact_sbs_r_L1_cocuk_odasi.jpg](contact_sbs_r_L1_cocuk_odasi.jpg)

- r_L1_ebeveyn_yatak_odasi: [contact_sbs_r_L1_ebeveyn_yatak_odasi.jpg](contact_sbs_r_L1_ebeveyn_yatak_odasi.jpg)

- r_L1_hol: [contact_sbs_r_L1_hol.jpg](contact_sbs_r_L1_hol.jpg)

- r_L1_yatak_odasi: [contact_sbs_r_L1_yatak_odasi.jpg](contact_sbs_r_L1_yatak_odasi.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| r_L-1_banyo | cam_r_L-1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_banyo | cam_r_L-1_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_hol | cam_r_L-1_hol_1 | - | - | info | - | - | cycles (room) |
| r_L-1_hol | cam_r_L-1_hol_2 | - | - | ok | - | - | cycles (room) |
| r_L-1_hol | cam_r_L-1_hol_3 | - | - | info | - | - | cycles (room) |
| r_L-1_kiler | cam_r_L-1_kiler_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_kiler_2 | cam_r_L-1_kiler_2_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_wc | cam_r_L-1_wc_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_wc | cam_r_L-1_wc_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_yatak_odasi | cam_r_L-1_yatak_odasi_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_yatak_odasi | cam_r_L-1_yatak_odasi_2 | a2 s 0.25 canny x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_yatak_odasi | cam_r_L-1_yatak_odasi_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_antre | cam_r_L0_antre_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_antre | cam_r_L0_antre_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_hol | cam_r_L0_hol_1 | - | - | info | - | - | cycles (room) |
| r_L0_hol | cam_r_L0_hol_2 | - | - | ok | - | - | cycles (room) |
| r_L0_hol | cam_r_L0_hol_3 | - | - | info | - | - | cycles (room) |
| r_L0_kiler | cam_r_L0_kiler_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_2 | a1 s 0.375 geometry x0.8 | accept | info | ok | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_wc | cam_r_L0_wc_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_3 | - | - | ok | - | - | cycles (room) |
| r_L1_balkon | cam_r_L1_balkon_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | added_by_polish | cycles (vision_check) |
| r_L1_banyo | cam_r_L1_banyo_1 | - | - | ok | - | - | cycles (gate) |
| r_L1_banyo | cam_r_L1_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_banyo | cam_r_L1_banyo_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_3 | - | - | ok | - | - | cycles (room) |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_hol | cam_r_L1_hol_1 | - | - | ok | - | - | cycles (room) |
| r_L1_hol | cam_r_L1_hol_2 | - | - | ok | - | - | cycles (room) |
| r_L1_hol | cam_r_L1_hol_3 | - | - | info | - | - | cycles (room) |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_3 | a1 s 0.375 geometry x0.8 | accept | info | ok | calibrated | polished |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 2/4 | -0.67 | - | search 1.63 | D1 A1 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 2/4 | -0.83 | - | search 1.40 | A2 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_hol_1 | r_L-1_hol | L-1 | cycles | room | - | - | info | - | - | +0.50 | - | search 3.30 | D4 A2 | 0 | no | [preview](cam_r_L-1_hol_1_final_preview.jpg) [plan](cam_r_L-1_hol_1_plan.jpg) |
| cam_r_L-1_hol_2 | r_L-1_hol | L-1 | cycles | room | - | - | ok | - | - | -0.50 | - | search 2.80 | D2 A1 | 0 | no | [preview](cam_r_L-1_hol_2_final_preview.jpg) [plan](cam_r_L-1_hol_2_plan.jpg) |
| cam_r_L-1_hol_3 | r_L-1_hol | L-1 | cycles | room | - | - | info | - | - | +0.50 | - | search 2.79 | D3 A2 | 0 | no | [preview](cam_r_L-1_hol_3_final_preview.jpg) [plan](cam_r_L-1_hol_3_plan.jpg) |
| cam_r_L-1_kiler_1 | r_L-1_kiler | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | - | search 2.57 | D1 | 0 | no | [preview](cam_r_L-1_kiler_1_final_preview.jpg) [plan](cam_r_L-1_kiler_1_plan.jpg) |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | - | search 2.62 | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_1_final_preview.jpg) [plan](cam_r_L-1_kiler_2_1_plan.jpg) |
| cam_r_L-1_wc_1 | r_L-1_wc | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 2/4 | -0.83 | - | search 2.25 | D1 A1 | 0 | no | [preview](cam_r_L-1_wc_1_final_preview.jpg) [plan](cam_r_L-1_wc_1_plan.jpg) |
| cam_r_L-1_wc_2 | r_L-1_wc | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | - | search 1.71 | D1 A1 | 0 | no | [preview](cam_r_L-1_wc_2_final_preview.jpg) [plan](cam_r_L-1_wc_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 3.93 | D2 A3 | 0 | no | [preview](cam_r_L-1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_1_plan.jpg) |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | L-1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 3.88 | D2 A3 | 0 | no | [preview](cam_r_L-1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.00 | - | search 3.72 | D2 A2 | 0 | no | [preview](cam_r_L-1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_3_plan.jpg) |
| cam_r_L0_antre_1 | r_L0_antre | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 3.32 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_antre_2 | r_L0_antre | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 3.23 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_2_final_preview.jpg) [plan](cam_r_L0_antre_2_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.50 | - | search 3.30 | D4 A2 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | cycles | room | - | - | ok | - | - | -0.17 | - | search 3.07 | D2 A1 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_hol_3 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.50 | - | search 2.90 | D3 A2 | 0 | no | [preview](cam_r_L0_hol_3_final_preview.jpg) [plan](cam_r_L0_hol_3_plan.jpg) |
| cam_r_L0_kiler_1 | r_L0_kiler | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.83 | -2 | search 2.51 | D2 | 1 | no | [preview](cam_r_L0_kiler_1_final_preview.jpg) [plan](cam_r_L0_kiler_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.00 | -2 | search 3.05 | D7 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.83 | -2 | search 2.76 | D6 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.67 | -3 | search 2.52 | D6 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.00 | -1 | search 3.30 | D7 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | ok | not preferred 0/4 | +4.33 | -1 | search 3.27 | D4 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.00 | -3 | search 3.25 | D5 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_wc_1 | r_L0_wc | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | -0.50 | - | search 1.77 | D3 | 0 | no | [preview](cam_r_L0_wc_1_final_preview.jpg) [plan](cam_r_L0_wc_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +6.00 | - | search 3.78 | D5 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +5.83 | -1 | search 3.61 | D5 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +6.83 | -2 | search 3.42 | D5 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_balkon_1 | r_L1_balkon | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.83 | -1 | search 1.83 | D1 | 0 | no | [preview](cam_r_L1_balkon_1_final_preview.jpg) [plan](cam_r_L1_balkon_1_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | gate | - | - | ok | - | - | +5.33 | -2 | search 2.99 | D2 A2 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | +5.33 | - | search 2.70 | D1 A2 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +5.00 | -2 | search 2.05 | D2 A1 | 0 | no | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +5.00 | -3 | search 3.52 | D2 A4 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +4.33 | -1 | search 3.16 | D2 A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | ok | - | - | +5.33 | -2 | search 3.12 | D1 A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +4.17 | - | search 3.41 | D1 A2 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.33 | -1 | search 3.38 | D1 A4 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.17 | -2 | search 3.35 | D1 A4 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +0.50 | - | search 3.15 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +0.50 | - | search 2.94 | D2 A1 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | cycles | room | - | - | info | - | - | +0.33 | - | search 2.83 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.50 | - | search 3.45 | D2 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.67 | -1 | search 3.36 | D2 A4 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | ok | not preferred 0/4 | +5.50 | - | search 3.19 | D1 A5 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 2 | 2 | 0 | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_hol | hall | L-1 | 3 | 0 | 3 | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_kiler | storage | L-1 | 1 | 1 | 0 | cam_r_L-1_kiler_1 |
| r_L-1_kiler_2 | storage | L-1 | 1 | 1 | 0 | cam_r_L-1_kiler_2_1 |
| r_L-1_wc | wc | L-1 | 2 | 2 | 0 | cam_r_L-1_wc_1, cam_r_L-1_wc_2 |
| r_L-1_yatak_odasi | bedroom | L-1 | 3 | 3 | 0 | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | hall | L0 | 2 | 2 | 0 | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_hol | hall | L0 | 3 | 0 | 3 | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_kiler | storage | L0 | 1 | 1 | 0 | cam_r_L0_kiler_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 3 | 0 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 3 | 0 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | wc | L0 | 1 | 1 | 0 | cam_r_L0_wc_1 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | balcony | L1 | 1 | 0 | 1 | cam_r_L1_balkon_1 |
| r_L1_banyo | bathroom | L1 | 3 | 2 | 1 | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | hall | L1 | 3 | 0 | 3 | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

### Why Cycles

- cam_r_L-1_hol_1: room: polish: room
- cam_r_L-1_hol_2: room: polish: room
- cam_r_L-1_hol_3: room: polish: room
- cam_r_L0_hol_1: room: polish: room
- cam_r_L0_hol_2: room: polish: room
- cam_r_L0_hol_3: room: polish: room
- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: room: polish: room
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L1_balkon_1: vision_check: added_by_polish furniture at [12.2, 822.4, 1313.1, 1077.6]
- cam_r_L1_banyo_1: gate: no ladder attempt passed the gate: a1 reject (depth, edges); a2 reject (depth); a3 reject (depth)
- cam_r_L1_cocuk_odasi_1: room: polish: room
- cam_r_L1_cocuk_odasi_2: room: polish: room
- cam_r_L1_cocuk_odasi_3: room: polish: room
- cam_r_L1_hol_1: room: polish: room
- cam_r_L1_hol_2: room: polish: room
- cam_r_L1_hol_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | cycles | missing | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_1 | polished | missing | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_2 | cycles | missing | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_2 | polished | missing | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_hol_1 | cycles | disputed | d_L-1_003 | door | optional | from_documents | kat_planlari.pdf p1 path:14 vector 1.00 | info | - |
| cam_r_L-1_hol_3 | cycles | missing | d_L-1_004 | door | optional | from_documents | kat_planlari.pdf p1 path:16 vector 1.00 | info | - |
| cam_r_L0_hol_1 | cycles | disputed | d_L0_005 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11C KAPI_90 vector 1.00; kat_planlari.pdf p2 path:19 vector 1.00 | info | - |
| cam_r_L0_hol_3 | cycles | disputed | d_L0_005 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11C KAPI_90 vector 1.00; kat_planlari.pdf p2 path:19 vector 1.00 | info | - |
| cam_r_L0_salon_2 | cycles | disputed | d_L0_004 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11A KAPI_90 vector 1.00; kat_planlari.pdf p2 path:17 vector 1.00 | info | - |
| cam_r_L0_wc_1 | cycles | disputed | f_L0_020 | washbasin | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:154 LAVABO vector 1.00 | info | - |
| cam_r_L0_wc_1 | polished | disputed | f_L0_020 | washbasin | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:154 LAVABO vector 1.00 | info | - |
| cam_r_L0_yatak_odasi_1 | cycles | disputed | f_L0_018 | dresser | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:150 SIFONYER vector 1.00 | info | - |
| cam_r_L0_yatak_odasi_2 | cycles | disputed | f_L0_014 | bed_double | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:148 YATAK_CIFT vector 1.00 | info | - |
| cam_r_L1_banyo_2 | cycles | missing | f_L1_019 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_2 | polished | missing | f_L1_019 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | disputed | f_L1_019 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | polished | disputed | f_L1_019 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |

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

## Units

Project unit system: **metric** (not recorded in the building JSON: metric).

| document | unit system | source kind |
|---|---|---|
| kat_planlari.pdf | metric | cad_pdf |
| mobilya_plani.dxf | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: -. Recognition questions: -; answer files: none. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

## Site

Recorded, not built.

None.

## Separators

None.

## Assumed values

- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- L-1: ceiling height 2,70 m (assumed_default)
- L0: ceiling height 2,70 m (assumed_default)
- L1: ceiling height 2,70 m (assumed_default)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L-1_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_banyo |
| area_light | 1 | r_L-1_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_hol |
| area_light | 1 | r_L-1_kiler: room has little daylight (window/floor 0.051 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_kiler |
| area_light | 1 | r_L-1_kiler_2: room has little daylight (window/floor 0.049 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_kiler_2 |
| area_light | 1 | r_L-1_wc: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_wc |
| area_light | 1 | r_L-1_yatak_odasi: room has little daylight (window/floor 0.036 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_yatak_odasi |
| area_light | 1 | r_L0_antre: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_antre |
| area_light | 1 | r_L0_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_hol |
| area_light | 1 | r_L0_wc: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_wc |
| area_light | 1 | r_L1_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_hol |
| bedding | 1 | design detail of the bed (soft bedding inside the bed's own box); the documents show only the footprint | furn_f_L-1_003 |
| ceiling_height | 3 | building JSON: assumed_default | level_L-1, level_L0, level_L1 |
| counter_fronts | 1 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_007 |
| door_handles | 17 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1_001_handle, d_L-1_002_handle, d_L-1_003_handle |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| height | 17 | door height not in the JSON; default | d_L-1_001, d_L-1_002, d_L-1_003 |
| height | 1 | no height in the JSON; proxy table value for unknown | proxy_f_L0_021 |
| height | 2 | no height in the JSON; type height for armchair | furn_f_L0_002, furn_f_L0_003 |
| height | 1 | no height in the JSON; type height for bed_double | furn_f_L0_014 |
| height | 1 | no height in the JSON; type height for bookshelf | furn_f_L0_006 |
| height | 2 | no height in the JSON; type height for chair | furn_f_L0_012, furn_f_L0_013 |
| height | 1 | no height in the JSON; type height for dresser | furn_f_L0_018 |
| height | 1 | no height in the JSON; type height for fridge | furn_f_L0_010 |
| height | 1 | no height in the JSON; type height for kitchen_counter | furn_f_L0_007 |
| height | 2 | no height in the JSON; type height for nightstand | furn_f_L0_015, furn_f_L0_016 |
| height | 1 | no height in the JSON; type height for sink_kitchen | furn_f_L0_008 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L0_001 |
| height | 1 | no height in the JSON; type height for stove | furn_f_L0_009 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L0_004 |
| height | 1 | no height in the JSON; type height for table_dining | furn_f_L0_011 |
| height | 1 | no height in the JSON; type height for toilet | furn_f_L0_019 |
| height | 1 | no height in the JSON; type height for tv_unit | furn_f_L0_005 |
| height | 1 | no height in the JSON; type height for wardrobe | furn_f_L0_017 |
| height | 1 | no height in the JSON; type height for washbasin | furn_f_L0_020 |
| height | 16 | window height not in the JSON; default | win_L-1_001, win_L-1_002, win_L-1_003 |
| height_lift | 2 | footprint overlaps another piece of the same height; lifted so the top faces do not coincide | furn_f_L0_008, furn_f_L0_009 |
| sill_height | 16 | window sill_height not in the JSON; default | win_L-1_001, win_L-1_002, win_L-1_003 |
| skirting | 13 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1_kiler, skirting_r_L-1_hol, skirting_r_L-1_yatak_odasi |
| slab_thickness | 19 | slab between levels | w_L-1_001, w_L-1_002, w_L-1_003 |
| wood | 3 | style floor 'concrete_polished' is not wood; default veneer for furniture frames | furniture, furniture, furniture |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L1_banyo | cam_r_L1_banyo_2, cam_r_L1_banyo_3 | cam_r_L1_banyo_1 (gate) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_hol (rung None), r_L0_hol (rung None), r_L0_yatak_odasi (rung None), r_L1_cocuk_odasi (rung None), r_L1_hol (rung None).

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
| detector | google/owlv2-base-patch16-ensemble | cfd3195ba4ea9592eec887ded089f4c08eff231d | Apache-2.0 | check_manifest.json |

Assets: textures CC0 x 5; furniture/decor models CC-BY-4.0 x 22, CC0 x 14 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Bed For Vr" by olamii (https://sketchfab.com/3d-models/2bd3fcc82c9f43cfb0c8cf26c7d0107c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_014, f_L1_001, f_L1_008)
- "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_001)
- "Simple Book Shelf | [FREE] | Agustin Honnun" by Agustín Hönnun (https://sketchfab.com/3d-models/51d928b33e5549898cc86cbdaf966d83), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_006, f_L1_018)
- "Low Poly - Chair and Table" by tadeus (https://sketchfab.com/3d-models/5f235f066a9a416fb7177496a9117ec7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_011)
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_010)
- "Lowpoly Bed" by Mohamed199 (https://sketchfab.com/3d-models/6eb4212e70b941a3bd2db196a47828b9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L1_013)
- "Simple Tall Shelf" by Blender3D (https://sketchfab.com/3d-models/b46803ba0bc64e12b31f832fb761c4e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L1_004, f_L1_015)
- "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_020, f_L-1_008, f_L-1_011, f_L1_020)
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_012, f_L0_013, f_L-1_002, f_L0_023, f_L1_007, f_L1_012, f_L1_017)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence (here CC0 1.0 or CC BY 4.0), as declared by its uploader and not verified by WenArt_RUN: check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L-1_banyo_1 | calibrated | yes | no | - |
| cam_r_L-1_banyo_2 | calibrated | yes | no | - |
| cam_r_L-1_kiler_1 | calibrated | yes | no | - |
| cam_r_L-1_kiler_2_1 | calibrated | yes | no | - |
| cam_r_L-1_wc_1 | calibrated | yes | no | - |
| cam_r_L-1_wc_2 | calibrated | yes | no | - |
| cam_r_L-1_yatak_odasi_1 | calibrated | yes | no | - |
| cam_r_L-1_yatak_odasi_2 | calibrated | yes | no | - |
| cam_r_L-1_yatak_odasi_3 | calibrated | yes | no | - |
| cam_r_L0_antre_1 | calibrated | yes | no | - |
| cam_r_L0_antre_2 | calibrated | yes | no | - |
| cam_r_L0_kiler_1 | calibrated | yes | no | - |
| cam_r_L0_mutfak_1 | calibrated | yes | no | - |
| cam_r_L0_mutfak_2 | calibrated | yes | no | - |
| cam_r_L0_mutfak_3 | calibrated | yes | no | - |
| cam_r_L0_salon_1 | calibrated | yes | no | - |
| cam_r_L0_salon_2 | calibrated | yes | no | - |
| cam_r_L0_salon_3 | calibrated | yes | no | - |
| cam_r_L0_wc_1 | calibrated | yes | no | - |
| cam_r_L1_balkon_1 | calibrated | yes | yes | furniture [12.2, 822.4, 1313.1, 1077.6] (score) |
| cam_r_L1_banyo_2 | calibrated | yes | no | - |
| cam_r_L1_banyo_3 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | calibrated | yes | no | - |
| cam_r_L1_yatak_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_yatak_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_yatak_odasi_3 | calibrated | yes | no | - |

## Stages

This run (`20261004-013837-full-20261004T014240Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 9.6 s | - |
| pipeline_final | skipped | 0.0 s | no questions |
| recognize | skipped | 0.0 s | no questions |
| fit | ok | 1.7 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.2 s | - |
| layout | ok | 76.8 s | - |
| assets | ok | 0.8 s | - |
| decor | ok | 2.5 s | - |
| refit | ok | 1.4 s | - |
| build | ok | 53.9 s | - |
| render | ok | 4.0 min | - |
| controls | ok | 59.9 s | - |
| gate | ok | 84.6 s | gate decision ok |
| polish | ok | 20.6 min | - |
| detect | ok | 14.0 s | - |
| expected | ok | 16.9 s | - |
| ab_pairs | ok | 5.3 s | - |
| check | ok | 3.2 min | - |
| ab_realism | ok | 79.2 s | - |
| combine | ok | 30.1 s | - |
| ab_combine | ok | 8.4 s | - |

The report stage itself is recorded after this report.

Earlier runs: records of stages this run did not reach. They stay on the volume and are not part of this run's state or of this report's status:

| stage | status | seconds | note | run |
|---|---|---|---|---|
| ab_m5 | ok | 10.3 s | - | earlier run 20261003-030812-full-20261003T031435Z |
| ab_render | ok | 7.9 min | 57 camera(s) kept, 0 dropped | earlier run 20261003-030812-full-20261003T031435Z |
| ab_prepare | skipped | 0.0 s | not in this phase | earlier run 20261003-050627-full-20261003T051311Z |
| ab_look_alt | ok | 8.9 s | - | earlier run 20261003-050627-full-20261003T051311Z |

## Warnings

- final/cam_r_L-1_kiler_2_2_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_2_3_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_2_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_3_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L1_balkon_2_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L1_balkon_3_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_2_2_plan.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_2_3_plan.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_2_plan.jpg is from an earlier run (not part of this report)
- final/cam_r_L-1_kiler_3_plan.jpg is from an earlier run (not part of this report)
- final/cam_r_L1_balkon_2_plan.jpg is from an earlier run (not part of this report)
- final/cam_r_L1_balkon_3_plan.jpg is from an earlier run (not part of this report)
