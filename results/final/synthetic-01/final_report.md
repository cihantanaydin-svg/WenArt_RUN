# Final report: synthetic-01

29 views: 19 polished, 10 Cycles (gate 1, room 9). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 29 |
| polished | 19 |
| Cycles | 10 (gate 1, room 9) |
| confirmed mismatches on the final image | 1 in 1 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 2 |
| exposure | -0.83 .. +6.50 EV (0 at a limit), modes auto |
| window pull | 15 view(s), -3 .. 0 EV |
| camera policy | search 29 |
| camera score (min / mean / max) | 2.06 / 3.07 / 3.71 |
| rooms by number of views | 1 with 2, 9 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 20.8 s / 99.0 s / 9.0 s |
| seconds: polish / gate / check | 3.3 min / 71.6 s / 12.2 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 10 |

## Advisory flags and open items

- vision check advisory: insertion 0.0 misses >= 0.6
- check target missed: insertion 0.000 (needs >= 0.6)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 95.3 % (limit 95 %), 64 comparisons |
| negative controls rejected | 95.3 % (limit 90 %), 172 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- r_L0_banyo: [contact_sbs_r_L0_banyo.jpg](contact_sbs_r_L0_banyo.jpg)

- r_L0_hol: [contact_sbs_r_L0_hol.jpg](contact_sbs_r_L0_hol.jpg)

- r_L0_mutfak: [contact_sbs_r_L0_mutfak.jpg](contact_sbs_r_L0_mutfak.jpg)

- r_L0_salon: [contact_sbs_r_L0_salon.jpg](contact_sbs_r_L0_salon.jpg)

- r_L0_yatak_odasi: [contact_sbs_r_L0_yatak_odasi.jpg](contact_sbs_r_L0_yatak_odasi.jpg)

- r_L1_banyo: [contact_sbs_r_L1_banyo.jpg](contact_sbs_r_L1_banyo.jpg)

- r_L1_cocuk_odasi: [contact_sbs_r_L1_cocuk_odasi.jpg](contact_sbs_r_L1_cocuk_odasi.jpg)

- r_L1_ebeveyn_yatak_odasi: [contact_sbs_r_L1_ebeveyn_yatak_odasi.jpg](contact_sbs_r_L1_ebeveyn_yatak_odasi.jpg)

- r_L1_hol: [contact_sbs_r_L1_hol.jpg](contact_sbs_r_L1_hol.jpg)

- r_L1_yatak_odasi: [contact_sbs_r_L1_yatak_odasi.jpg](contact_sbs_r_L1_yatak_odasi.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| r_L0_banyo | cam_r_L0_banyo_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L0_banyo | cam_r_L0_banyo_2 | a3 s 0.125 depth x0.8 | accept | mismatch (1) | mismatch (1) | calibrated | polished |
| r_L0_banyo | cam_r_L0_banyo_3 | a3 s 0.125 depth x0.8 | accept | info | info | calibrated | polished |
| r_L0_hol | cam_r_L0_hol_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_hol | cam_r_L0_hol_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_1 | - | - | info | - | - | cycles (room) |
| r_L0_mutfak | cam_r_L0_mutfak_2 | - | - | info | - | - | cycles (room) |
| r_L0_mutfak | cam_r_L0_mutfak_3 | - | - | ok | - | - | cycles (room) |
| r_L0_salon | cam_r_L0_salon_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_1 | - | - | ok | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_2 | - | - | ok | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_3 | - | - | ok | - | - | cycles (room) |
| r_L1_banyo | cam_r_L1_banyo_1 | - | - | info | - | - | cycles (gate) |
| r_L1_banyo | cam_r_L1_banyo_2 | a3 s 0.125 depth x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_banyo | cam_r_L1_banyo_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2 | - | - | ok | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_3 | - | - | ok | - | - | cycles (room) |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_hol | cam_r_L1_hol_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_hol | cam_r_L1_hol_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_hol | cam_r_L1_hol_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +6.50 | -2 | search 2.81 | D5 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +6.33 | -3 | search 2.58 | D5 | 0 | yes | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_banyo_3 | r_L0_banyo | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | info | info | not preferred 0/4 | +6.17 | - | search 2.06 | D2 | 0 | no | [preview](cam_r_L0_banyo_3_final_preview.jpg) [plan](cam_r_L0_banyo_3_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | - | search 3.10 | D1 A1 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | - | search 3.02 | D2 A1 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | room | - | - | info | - | - | +4.83 | -2 | search 3.04 | D1 A5 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | room | - | - | info | - | - | +5.67 | -3 | search 2.51 | D1 A5 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | room | - | - | ok | - | - | +5.50 | - | search 2.06 | D1 A1 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.33 | -1 | search 3.52 | D5 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.33 | -1 | search 3.40 | D6 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.17 | -2 | search 3.30 | D6 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +4.00 | - | search 3.71 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +3.33 | -1 | search 3.67 | D3 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +3.67 | - | search 3.61 | D5 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | gate | - | - | info | - | - | +0.00 | 0 | search 3.24 | D2 A3 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | polished | - | a3 s 0.125 depth x0.8 | accept | ok | ok | not preferred 0/4 | -0.17 | - | search 2.65 | D1 A3 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | -0.17 | - | search 2.41 | D1 A2 | 0 | no | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +5.83 | -2 | search 3.33 | D2 A5 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | ok | - | - | +5.67 | -2 | search 3.07 | D1 A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | ok | - | - | +5.83 | -2 | search 2.76 | D1 A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.00 | - | search 3.41 | D1 A2 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +3.33 | -2 | search 3.31 | D1 A3 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.17 | -2 | search 3.31 | D1 A4 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | 0 | search 3.12 | D4 A2 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 2.94 | D2 A1 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +0.17 | - | search 2.89 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.67 | - | search 3.51 | D1 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +3.67 | - | search 3.42 | D1 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.83 | - | search 3.40 | D1 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_banyo | bathroom | L0 | 3 | 3 | 0 | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_hol | hall | L0 | 2 | 2 | 0 | cam_r_L0_hol_1, cam_r_L0_hol_2 |
| r_L0_mutfak | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 3 | 0 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_banyo | bathroom | L1 | 3 | 2 | 1 | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | hall | L1 | 3 | 3 | 0 | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

### Why Cycles

- cam_r_L0_mutfak_1: room: polish: room
- cam_r_L0_mutfak_2: room: polish: room
- cam_r_L0_mutfak_3: room: polish: room
- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: room: polish: room
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L1_banyo_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L1_cocuk_odasi_1: room: polish: room
- cam_r_L1_cocuk_odasi_2: room: polish: room
- cam_r_L1_cocuk_odasi_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_2 | cycles | missing | f_L0_012 | shower | required | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | yes | - |
| cam_r_L0_banyo_2 | cycles | disputed | f_L0_013 | washing_machine | required | from_documents | zemin_kat.dxf MOBILYA INSERT:122 CAMASIR_MAK vector 1.00 | info | - |
| cam_r_L0_banyo_2 | cycles | disputed | f_L0_011 | washbasin | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector 1.00 | info | - |
| cam_r_L0_banyo_2 | polished | missing | f_L0_012 | shower | required | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | yes | - |
| cam_r_L0_banyo_2 | polished | disputed | f_L0_013 | washing_machine | required | from_documents | zemin_kat.dxf MOBILYA INSERT:122 CAMASIR_MAK vector 1.00 | info | - |
| cam_r_L0_banyo_2 | polished | disputed | f_L0_011 | washbasin | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector 1.00 | info | - |
| cam_r_L0_banyo_3 | cycles | missing | f_L0_012 | shower | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | info | - |
| cam_r_L0_banyo_3 | polished | missing | f_L0_012 | shower | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | info | - |
| cam_r_L0_mutfak_1 | cycles | missing | f_L0_016 | sink_kitchen | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_cocuk_odasi_1 | cycles | disputed | f_L1_020 | bookshelf | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_cocuk_odasi_1 | cycles | disputed | f_L1_016 | bed_single | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |

## Needs review

- cam_r_L0_banyo_2: f_L0_012 (shower, from_documents): missing

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Units

Project unit system: **metric** (not recorded in the building JSON: metric).

| document | unit system | source kind |
|---|---|---|
| 1_kat.pdf | metric | cad_pdf |
| 1_kat_scan.png | metric | raster_scan |
| zemin_kat.dxf | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: -. Recognition questions: -; answer files: none. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

Raster pages (scans and photos):

| file | page | kind | class | level | rectified image | skip reason |
|---|---|---|---|---|---|---|
| 1_kat_scan.png | 1 | scan | floor_plan | L1 | rectified/1_kat_scan_png_p1.png | - |

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
- L0: ceiling height 2,70 m (assumed_default)
- L1: ceiling height 2,70 m (assumed_default)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_hol |
| area_light | 1 | r_L1_banyo: room has little daylight (window/floor 0.075 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo |
| area_light | 1 | r_L1_hol: room has little daylight (window/floor 0.067 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_hol |
| bedding | 3 | design detail of the bed (soft bedding inside the bed's own box); the documents show only the footprint | furn_f_L0_006, furn_f_L1_001, furn_f_L1_008 |
| ceiling_height | 2 | building JSON: assumed_default | level_L0, level_L1 |
| counter_fronts | 1 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_015 |
| door_handles | 9 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| fabric | 2 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture |
| height | 9 | door height not in the JSON; default | d_L0_001, d_L0_002, d_L0_003 |
| height | 1 | no height in the JSON; type height for armchair | furn_f_L0_004 |
| height | 1 | no height in the JSON; type height for bed_double | furn_f_L0_006 |
| height | 1 | no height in the JSON; type height for bookshelf | furn_f_L0_005 |
| height | 2 | no height in the JSON; type height for nightstand | furn_f_L0_007, furn_f_L0_008 |
| height | 1 | no height in the JSON; type height for shower | furn_f_L0_012 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L0_001 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L0_002 |
| height | 1 | no height in the JSON; type height for toilet | furn_f_L0_010 |
| height | 1 | no height in the JSON; type height for tv_unit | furn_f_L0_003 |
| height | 1 | no height in the JSON; type height for wardrobe | furn_f_L0_009 |
| height | 1 | no height in the JSON; type height for washbasin | furn_f_L0_011 |
| height | 1 | no height in the JSON; type height for washing_machine | furn_f_L0_013 |
| height | 12 | window height not in the JSON; default | win_L0_001, win_L0_002, win_L0_003 |
| sill_height | 12 | window sill_height not in the JSON; default | win_L0_001, win_L0_002, win_L0_003 |
| skirting | 7 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_salon, skirting_r_L0_yatak_odasi, skirting_r_L0_hol |
| slab_thickness | 8 | slab between levels | w_L0_001, w_L0_002, w_L0_003 |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L1_banyo | cam_r_L1_banyo_2, cam_r_L1_banyo_3 | cam_r_L1_banyo_1 (gate) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L0_mutfak (rung None), r_L0_yatak_odasi (rung None), r_L1_cocuk_odasi (rung None).

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

Assets: textures CC0 x 6; furniture/decor models CC-BY-4.0 x 6, CC0 x 12 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Lowpoly Bed" by Mohamed199 (https://sketchfab.com/3d-models/6eb4212e70b941a3bd2db196a47828b9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L1_016)
- "Simple Tall Shelf" by Blender3D (https://sketchfab.com/3d-models/b46803ba0bc64e12b31f832fb761c4e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L1_004, f_L1_018)
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L1_007, f_L1_011, f_L1_019)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence (here CC0 1.0 or CC BY 4.0), as declared by its uploader and not verified by WenArt_RUN: check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L0_banyo_1 | calibrated | yes | no | - |
| cam_r_L0_banyo_2 | calibrated | yes | no | - |
| cam_r_L0_banyo_3 | calibrated | yes | no | - |
| cam_r_L0_hol_1 | calibrated | yes | no | - |
| cam_r_L0_hol_2 | calibrated | yes | no | - |
| cam_r_L0_salon_1 | calibrated | yes | no | - |
| cam_r_L0_salon_2 | calibrated | yes | no | - |
| cam_r_L0_salon_3 | calibrated | yes | no | - |
| cam_r_L1_banyo_2 | calibrated | yes | no | - |
| cam_r_L1_banyo_3 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | calibrated | yes | no | - |
| cam_r_L1_hol_1 | calibrated | yes | no | - |
| cam_r_L1_hol_2 | calibrated | yes | no | - |
| cam_r_L1_hol_3 | calibrated | yes | no | - |
| cam_r_L1_yatak_odasi_1 | calibrated | yes | no | - |
| cam_r_L1_yatak_odasi_2 | calibrated | yes | no | - |
| cam_r_L1_yatak_odasi_3 | calibrated | yes | no | - |

## Stages

This run (`20261004-000052-full-20261004T000516Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 46.6 s | - |
| pipeline_final | skipped | 0.0 s | no questions |
| recognize | skipped | 0.0 s | no questions |
| fit | ok | 1.6 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.2 s | - |
| layout | ok | 61.7 s | - |
| assets | ok | 0.5 s | - |
| decor | ok | 1.7 s | - |
| refit | ok | 1.2 s | - |
| build | ok | 30.2 s | - |
| render | ok | 2.9 min | - |
| controls | ok | 3.2 min | - |
| gate | ok | 82.0 s | gate decision ok |
| polish | ok | 8.6 min | - |
| detect | ok | 12.0 s | - |
| expected | ok | 22.0 s | - |
| check | ok | 2.6 min | - |
| combine | ok | 80.4 s | - |

The report stage itself is recorded after this report.

Earlier runs: records of stages this run did not reach. They stay on the volume and are not part of this run's state or of this report's status:

| stage | status | seconds | note | run |
|---|---|---|---|---|
| ab_m5 | ok | 6.7 s | - | earlier run 20261003-030812-full-20261003T031435Z |
| ab_render | ok | 5.2 min | 30 camera(s) kept, 0 dropped | earlier run 20261003-030812-full-20261003T031435Z |
| ab_controls | ok | 6.7 min | 8 control view(s) | earlier run 20261003-030812-full-20261003T031435Z |
| ab_pairs | reused | 0.0 s | ab/pairs.json of the render pod (116 pairs, controls) | earlier run 20261003-050627-full-20261003T051311Z |
| ab_prepare | skipped | 0.0 s | not in this phase | earlier run 20261003-050627-full-20261003T051311Z |
| ab_realism | ok | 13.0 s | - | earlier run 20261003-050627-full-20261003T051311Z |
| ab_look_alt | ok | 6.7 s | - | earlier run 20261003-050627-full-20261003T051311Z |
| ab_combine | ok | 18.2 s | - | earlier run 20261003-050627-full-20261003T051311Z |

## Warnings

None.
