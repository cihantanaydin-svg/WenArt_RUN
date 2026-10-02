# Final report: synthetic-03

57 views: 20 polished, 37 Cycles (check_incomplete 1, gate 10, room 26). Stages: render run, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 57 |
| polished | 20 |
| Cycles | 37 (check_incomplete 1, gate 10, room 26) |
| confirmed mismatches on the final image | 2 in 2 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 3 |
| rooms mixing polished and Cycles | 3 |
| advisory | yes |
| advisory flags | 2 |
| exposure | -1.50 .. +8.00 EV (4 at a limit), modes auto |
| seconds: build / render / metering | 23.8 s / 2.7 min / 16.4 s |
| seconds: polish / gate / check | 14.4 min / 58.5 s / 11.5 min |
| brief polish | yes (default, not in brief.yaml) |

## Advisory flags and open items

- vision check advisory: insertion 0.1429 misses >= 0.6
- check target missed: insertion 0.143 (needs >= 0.6)

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L-1: [contact_L-1.jpg](contact_L-1.jpg)

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | check_incomplete | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | -0.33 | A1 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | gate | - | - | ok | - | - | +0.17 | A2 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_banyo_3 | r_L-1_banyo | L-1 | cycles | gate | - | - | info | - | - | -0.33 | A1 | 0 | no | [preview](cam_r_L-1_banyo_3_final_preview.jpg) [plan](cam_r_L-1_banyo_3_plan.jpg) |
| cam_r_L-1_hol_1 | r_L-1_hol | L-1 | cycles | room | - | - | info | - | - | +0.33 | D4 A2 | 0 | no | [preview](cam_r_L-1_hol_1_final_preview.jpg) [plan](cam_r_L-1_hol_1_plan.jpg) |
| cam_r_L-1_hol_2 | r_L-1_hol | L-1 | cycles | room | - | - | ok | - | - | -0.33 | D2 | 0 | no | [preview](cam_r_L-1_hol_2_final_preview.jpg) [plan](cam_r_L-1_hol_2_plan.jpg) |
| cam_r_L-1_hol_3 | r_L-1_hol | L-1 | cycles | gate | - | - | info | - | - | -1.33 | D1 | 0 | no | [preview](cam_r_L-1_hol_3_final_preview.jpg) [plan](cam_r_L-1_hol_3_plan.jpg) |
| cam_r_L-1_kiler_1 | r_L-1_kiler | L-1 | cycles | room | - | - | ok | - | - | +6.17 | - | 0 | no | [preview](cam_r_L-1_kiler_1_final_preview.jpg) [plan](cam_r_L-1_kiler_1_plan.jpg) |
| cam_r_L-1_kiler_2 | r_L-1_kiler | L-1 | cycles | room | - | - | ok | - | - | +8.00 (limit) | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_final_preview.jpg) [plan](cam_r_L-1_kiler_2_plan.jpg) |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | L-1 | cycles | room | - | - | ok | - | - | +6.33 | - | 0 | no | [preview](cam_r_L-1_kiler_2_1_final_preview.jpg) [plan](cam_r_L-1_kiler_2_1_plan.jpg) |
| cam_r_L-1_kiler_2_2 | r_L-1_kiler_2 | L-1 | cycles | room | - | - | ok | - | - | +8.00 (limit) | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_2_final_preview.jpg) [plan](cam_r_L-1_kiler_2_2_plan.jpg) |
| cam_r_L-1_kiler_2_3 | r_L-1_kiler_2 | L-1 | cycles | room | - | - | ok | - | - | +6.67 | D1 | 0 | no | [preview](cam_r_L-1_kiler_2_3_final_preview.jpg) [plan](cam_r_L-1_kiler_2_3_plan.jpg) |
| cam_r_L-1_kiler_3 | r_L-1_kiler | L-1 | cycles | room | - | - | ok | - | - | +6.50 | D1 | 0 | no | [preview](cam_r_L-1_kiler_3_final_preview.jpg) [plan](cam_r_L-1_kiler_3_plan.jpg) |
| cam_r_L-1_wc_1 | r_L-1_wc | L-1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | -0.33 | A1 | 0 | no | [preview](cam_r_L-1_wc_1_final_preview.jpg) [plan](cam_r_L-1_wc_1_plan.jpg) |
| cam_r_L-1_wc_2 | r_L-1_wc | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | preferred 3/4 | -0.17 | A1 | 0 | no | [preview](cam_r_L-1_wc_2_final_preview.jpg) [plan](cam_r_L-1_wc_2_plan.jpg) |
| cam_r_L-1_wc_3 | r_L-1_wc | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 2/4 | -0.50 | A1 | 0 | no | [preview](cam_r_L-1_wc_3_final_preview.jpg) [plan](cam_r_L-1_wc_3_plan.jpg) |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | L-1 | cycles | room | - | - | ok | - | - | +7.83 | D1 A2 | 0 | no | [preview](cam_r_L-1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_1_plan.jpg) |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | L-1 | cycles | room | - | - | info | - | - | +8.00 (limit) | A2 | 0 | no | [preview](cam_r_L-1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | L-1 | cycles | room | - | - | info | - | - | +8.00 (limit) | D2 A3 | 0 | no | [preview](cam_r_L-1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_3_plan.jpg) |
| cam_r_L0_antre_1 | r_L0_antre | L0 | cycles | room | - | - | ok | - | - | -0.17 | D1 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_antre_2 | r_L0_antre | L0 | cycles | room | - | - | info | - | - | +0.00 | D2 A1 | 0 | no | [preview](cam_r_L0_antre_2_final_preview.jpg) [plan](cam_r_L0_antre_2_plan.jpg) |
| cam_r_L0_antre_3 | r_L0_antre | L0 | cycles | room | - | - | ok | - | - | -0.33 | D1 | 0 | no | [preview](cam_r_L0_antre_3_final_preview.jpg) [plan](cam_r_L0_antre_3_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.33 | D3 A2 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | cycles | room | - | - | ok | - | - | -0.67 | D2 A1 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_hol_3 | r_L0_hol | L0 | cycles | gate | - | - | info | - | - | -1.50 | D1 | 0 | no | [preview](cam_r_L0_hol_3_final_preview.jpg) [plan](cam_r_L0_hol_3_plan.jpg) |
| cam_r_L0_kiler_1 | r_L0_kiler | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +3.33 | D1 | 1 | no | [preview](cam_r_L0_kiler_1_final_preview.jpg) [plan](cam_r_L0_kiler_1_plan.jpg) |
| cam_r_L0_kiler_2 | r_L0_kiler | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +2.83 | D1 | 1 | no | [preview](cam_r_L0_kiler_2_final_preview.jpg) [plan](cam_r_L0_kiler_2_plan.jpg) |
| cam_r_L0_kiler_3 | r_L0_kiler | L0 | cycles | gate | - | - | ok | - | - | +3.50 | D1 | 1 | no | [preview](cam_r_L0_kiler_3_final_preview.jpg) [plan](cam_r_L0_kiler_3_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | room | - | - | ok | - | - | +4.00 | D3 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | room | - | - | info | - | - | +4.83 | D6 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | room | - | - | info | - | - | +4.00 | D3 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | info | mismatch (1) | not preferred 0/4 | +4.50 | D3 A1 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | preferred 3/4 | +4.83 | D5 A1 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 2/4 | +5.17 | D5 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_wc_1 | r_L0_wc | L0 | cycles | room | - | - | info | - | - | +0.17 | D2 | 0 | no | [preview](cam_r_L0_wc_1_final_preview.jpg) [plan](cam_r_L0_wc_1_plan.jpg) |
| cam_r_L0_wc_2 | r_L0_wc | L0 | cycles | room | - | - | info | - | - | +0.33 | D2 | 0 | no | [preview](cam_r_L0_wc_2_final_preview.jpg) [plan](cam_r_L0_wc_2_plan.jpg) |
| cam_r_L0_wc_3 | r_L0_wc | L0 | cycles | gate | - | - | info | - | - | +0.17 | D1 | 0 | no | [preview](cam_r_L0_wc_3_final_preview.jpg) [plan](cam_r_L0_wc_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +6.33 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +6.50 | D3 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +6.50 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_balkon_1 | r_L1_balkon | L1 | cycles | room | - | - | ok | - | - | +3.83 | D1 | 0 | no | [preview](cam_r_L1_balkon_1_final_preview.jpg) [plan](cam_r_L1_balkon_1_plan.jpg) |
| cam_r_L1_balkon_2 | r_L1_balkon | L1 | cycles | room | - | - | ok | - | - | +3.67 | D1 | 0 | no | [preview](cam_r_L1_balkon_2_final_preview.jpg) [plan](cam_r_L1_balkon_2_plan.jpg) |
| cam_r_L1_balkon_3 | r_L1_balkon | L1 | cycles | room | - | - | ok | - | - | +4.17 | D1 | 0 | no | [preview](cam_r_L1_balkon_3_final_preview.jpg) [plan](cam_r_L1_balkon_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | gate | - | - | info | - | - | +5.33 | A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | cycles | gate | - | - | info | - | - | +4.50 | A1 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +6.33 | D1 A2 | 0 | yes | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +3.83 | A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.17 | D1 A4 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | +4.33 | D2 A2 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.17 | D1 A3 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.50 | D1 A4 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.67 | D1 A2 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +0.33 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | -0.67 | D2 A1 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | cycles | gate | - | - | ok | - | - | -1.33 | - | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | cycles | gate | - | - | info | - | - | +4.83 | D1 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.00 | D1 A2 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +5.00 | D2 A2 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

### Why Cycles

- cam_r_L-1_banyo_1: check_incomplete: Cycles image: unreliable pass (glm saw the decoy)
- cam_r_L-1_banyo_2: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L-1_banyo_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L-1_hol_1: room: polish: room
- cam_r_L-1_hol_2: room: polish: room
- cam_r_L-1_hol_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L-1_kiler_1: room: polish: room
- cam_r_L-1_kiler_2: room: polish: room
- cam_r_L-1_kiler_2_1: room: polish: room
- cam_r_L-1_kiler_2_2: room: polish: room
- cam_r_L-1_kiler_2_3: room: polish: room
- cam_r_L-1_kiler_3: room: polish: room
- cam_r_L-1_yatak_odasi_1: room: polish: room
- cam_r_L-1_yatak_odasi_2: room: polish: room
- cam_r_L-1_yatak_odasi_3: room: polish: room
- cam_r_L0_antre_1: room: polish: room
- cam_r_L0_antre_2: room: polish: room
- cam_r_L0_antre_3: room: polish: room
- cam_r_L0_hol_1: room: polish: room
- cam_r_L0_hol_2: room: polish: room
- cam_r_L0_hol_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L0_kiler_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L0_mutfak_1: room: polish: room
- cam_r_L0_mutfak_2: room: polish: room
- cam_r_L0_mutfak_3: room: polish: room
- cam_r_L0_wc_1: room: polish: room
- cam_r_L0_wc_2: room: polish: room
- cam_r_L0_wc_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L1_balkon_1: room: polish: room
- cam_r_L1_balkon_2: room: polish: room
- cam_r_L1_balkon_3: room: polish: room
- cam_r_L1_banyo_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L1_banyo_2: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L1_hol_1: room: polish: room
- cam_r_L1_hol_2: room: polish: room
- cam_r_L1_hol_3: gate: no ladder attempt passed the gate: a1 reject (depth, edges); a2 reject (depth); a3 reject (depth, edges)
- cam_r_L1_yatak_odasi_1: gate: no ladder attempt passed the gate: a1 reject (depth, edges); a2 reject (depth); a3 reject (depth)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | polished | disputed | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_3 | cycles | missing | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_hol_1 | cycles | missing | d_L-1_004 | door | optional | from_documents | kat_planlari.pdf p1 path:16 vector 1.00 | info | - |
| cam_r_L-1_hol_1 | cycles | missing | d_L-1_002 | door | optional | from_documents | kat_planlari.pdf p1 path:12 vector 1.00 | info | - |
| cam_r_L-1_hol_3 | cycles | missing | d_L-1_003 | door | optional | from_documents | kat_planlari.pdf p1 path:14 vector 1.00 | info | - |
| cam_r_L-1_wc_3 | cycles | disputed | f_L-1_007 | toilet | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_wc_3 | polished | disputed | f_L-1_007 | toilet | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_yatak_odasi_2 | cycles | missing | f_L-1_003 | bed_double | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_antre_2 | cycles | disputed | d_L0_003 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:118 KAPI_80 vector 1.00; kat_planlari.pdf p2 path:15 vector 1.00 | info | - |
| cam_r_L0_antre_2 | cycles | disputed | d_L0_002 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:116 KAPI_80 vector 1.00; kat_planlari.pdf p2 path:13 vector 1.00 | info | - |
| cam_r_L0_hol_1 | cycles | missing | d_L0_006 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11E KAPI_80 vector 1.00; kat_planlari.pdf p2 path:21 vector 1.00 | info | - |
| cam_r_L0_hol_3 | cycles | disputed | d_L0_005 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11C KAPI_90 vector 1.00; kat_planlari.pdf p2 path:19 vector 1.00 | info | - |
| cam_r_L0_mutfak_3 | cycles | disputed | f_L0_013 | chair | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:146 SANDALYE vector 1.00 | info | - |
| cam_r_L0_mutfak_3 | cycles | disputed | f_L0_011 | table_dining | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:142 YEMEK_MASASI vector 1.00 | info | - |
| cam_r_L0_salon_1 | cycles | disputed | f_L0_006 | bookshelf | required | from_documents | mobilya_plani.dxf MOBILYA INSERT:138 KITAPLIK vector 1.00 | info | - |
| cam_r_L0_salon_1 | polished | disputed | f_L0_006 | bookshelf | required | from_documents | mobilya_plani.dxf MOBILYA INSERT:138 KITAPLIK vector 1.00 | info | - |
| cam_r_L0_salon_1 | polished | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L0_wc_1 | cycles | disputed | d_L0_007 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:120 KAPI_80 vector 1.00; kat_planlari.pdf p2 path:23 vector 1.00 | info | - |
| cam_r_L0_wc_1 | cycles | missing | f_L0_019 | toilet | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:152 KLOZET vector 1.00 | info | - |
| cam_r_L0_wc_2 | cycles | missing | f_L0_020 | washbasin | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:154 LAVABO vector 1.00 | info | - |
| cam_r_L0_wc_3 | cycles | disputed | d_L0_007 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:120 KAPI_80 vector 1.00; kat_planlari.pdf p2 path:23 vector 1.00 | info | - |
| cam_r_L1_banyo_1 | cycles | missing | f_L1_016 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_2 | cycles | missing | f_L1_016 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | disputed | d_L1_004 | door | optional | from_documents | kat_planlari.pdf p3 path:16 vector 1.00 | info | - |
| cam_r_L1_banyo_3 | cycles | window count more | window | window | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_banyo_3 | polished | disputed | d_L1_004 | door | optional | from_documents | kat_planlari.pdf p3 path:16 vector 1.00 | info | - |
| cam_r_L1_banyo_3 | polished | window count more | window | window | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_ebeveyn_yatak_odasi_1 | polished | disputed | f_L1_002 | nightstand | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_1 | cycles | missing_or_changed | f_L1_010 | wardrobe | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_1 | cycles | missing | f_L1_007 | bed_double | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_2 | cycles | disputed | f_L1_007 | bed_double | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_2 | polished | disputed | f_L1_007 | bed_double | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_3 | cycles | missing | f_L1_007 | bed_double | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |

## Needs review

- cam_r_L1_banyo_3: window count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- f_L0_021

Unverified pieces in view:

- cam_r_L0_kiler_1: f_L0_021
- cam_r_L0_kiler_2: f_L0_021
- cam_r_L0_kiler_3: f_L0_021

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L0_salon | Label says 24,00 m², polygon gives 23,50 m² (2.1%) | within tolerance (3%), kept polygon from mobilya_plani.dxf |
| c_002 | dimension_vs_measured | w_L-1_004 | kat_planlari.pdf p1: dimension text 3,99 vs measured 3.80 m (5.0%) | kept measured geometry (vector PDF) |
| c_003 | count_mismatch | win_L0_004 | Zemin Kat: mobilya_plani.dxf has 6 windows, kat_planlari.pdf p2 has 5 | DXF wins over vector PDF, window kept |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L0_kiler | cam_r_L0_kiler_1, cam_r_L0_kiler_2 | cam_r_L0_kiler_3 (gate) | ok |
| r_L1_banyo | cam_r_L1_banyo_3 | cam_r_L1_banyo_1 (gate), cam_r_L1_banyo_2 (gate) | ok |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 | cam_r_L1_yatak_odasi_1 (gate) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_hol (rung None), r_L-1_kiler (rung None), r_L-1_kiler_2 (rung None), r_L-1_yatak_odasi (rung None), r_L0_antre (rung None), r_L0_hol (rung None), r_L0_mutfak (rung None), r_L0_wc (rung None), r_L1_balkon (rung None), r_L1_hol (rung None).

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

Assets: textures CC0 x 2; furniture/decor models CC0 x 31 (parametric meshes need no licence).

## Warnings

None.
