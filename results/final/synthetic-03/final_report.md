# Final report: synthetic-03

44 views: 11 polished, 33 Cycles (gate 2, room 26, vision_check 5). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 44 |
| interior / exterior views | 44 / 0 |
| variant | base |
| polished | 11 |
| Cycles | 33 (gate 2, room 26, vision_check 5) |
| confirmed mismatches on the final image | 1 in 1 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 1 |
| rooms mixing polished and Cycles | 3 |
| advisory | yes |
| advisory flags | 6 |
| exposure | -0.17 .. +7.83 EV (0 at a limit), modes auto |
| window pull | 18 view(s), -4 .. -1 EV |
| camera policy | search 44 |
| camera score (min / mean / max) | 1.54 / 2.97 / 4.10 |
| rooms by number of views | 5 with 1, 3 with 2, 11 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 2.9 min / 103.8 s / 36.0 s |
| seconds: polish / gate / check | 5.0 min / 25.3 s / 14.4 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 19 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [synthetic-03.blend](3d/synthetic-03.blend) | 242.7 MB |
| [synthetic-03.glb](3d/synthetic-03.glb) | 671.5 MB |

44 cameras; textures scaled to at most 1024 px (247 scaled) for the download.

## AI decor

67 decor items chosen by the AI (Qwen/Qwen3-VL-8B-Instruct; both passes agreeing) in 15 rooms; 0 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check advisory: removal_flagged 0.75 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.750 (needs >= 0.8)
- check target missed: removal_confirmed 0.500 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- the polish added an object in cam_r_L-1_wc_1, cam_r_L0_mutfak_1, cam_r_L1_balkon_1, cam_r_L1_banyo_1, cam_r_L1_banyo_2: the Cycles render is final
- AI completion: 1 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 98.4 % (limit 95 %), 64 comparisons |
| negative controls rejected | 99.4 % (limit 90 %), 176 comparisons |
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
| r_L-1_banyo | cam_r_L-1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | ok | info | calibrated | polished |
| r_L-1_banyo | cam_r_L-1_banyo_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L-1_hol | cam_r_L-1_hol_1 | - | - | ok | - | - | cycles (room) |
| r_L-1_hol | cam_r_L-1_hol_2 | - | - | ok | - | - | cycles (room) |
| r_L-1_hol | cam_r_L-1_hol_3 | - | - | info | - | - | cycles (room) |
| r_L-1_kiler | cam_r_L-1_kiler_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_kiler_2 | cam_r_L-1_kiler_2_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_wc | cam_r_L-1_wc_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | added_by_polish | cycles (vision_check) |
| r_L-1_wc | cam_r_L-1_wc_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1_yatak_odasi | cam_r_L-1_yatak_odasi_1 | - | - | ok | - | - | cycles (room) |
| r_L-1_yatak_odasi | cam_r_L-1_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L-1_yatak_odasi | cam_r_L-1_yatak_odasi_3 | - | - | ok | - | - | cycles (room) |
| r_L0_antre | cam_r_L0_antre_1 | a1 s 0.375 geometry x0.8 | accept | info | ok | calibrated | polished |
| r_L0_antre | cam_r_L0_antre_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_hol | cam_r_L0_hol_1 | - | - | info | - | - | cycles (room) |
| r_L0_hol | cam_r_L0_hol_2 | - | - | ok | - | - | cycles (room) |
| r_L0_hol | cam_r_L0_hol_3 | - | - | info | - | - | cycles (room) |
| r_L0_kiler | cam_r_L0_kiler_1 | a2 s 0.25 canny x0.8 | accept | info | ok | calibrated | polished |
| r_L0_mutfak | cam_r_L0_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L0_mutfak | cam_r_L0_mutfak_2 | - | - | ok | - | - | cycles (gate) |
| r_L0_mutfak | cam_r_L0_mutfak_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_salon | cam_r_L0_salon_1 | - | - | ok | - | - | cycles (room) |
| r_L0_salon | cam_r_L0_salon_2 | - | - | info | - | - | cycles (room) |
| r_L0_salon | cam_r_L0_salon_3 | - | - | info | - | - | cycles (room) |
| r_L0_wc | cam_r_L0_wc_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_2 | - | - | info | - | - | cycles (gate) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L1_balkon | cam_r_L1_balkon_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | added_by_polish | cycles (vision_check) |
| r_L1_banyo | cam_r_L1_banyo_1 | a2 s 0.25 canny x0.8 | accept | mismatch (1) | mismatch (1) | added_by_polish | cycles (vision_check) |
| r_L1_banyo | cam_r_L1_banyo_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | added_by_polish | cycles (vision_check) |
| r_L1_banyo | cam_r_L1_banyo_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_ebeveyn_yatak_odasi | cam_r_L1_ebeveyn_yatak_odasi_3 | - | - | ok | - | - | cycles (room) |
| r_L1_hol | cam_r_L1_hol_1 | - | - | info | - | - | cycles (room) |
| r_L1_hol | cam_r_L1_hol_2 | - | - | info | - | - | cycles (room) |
| r_L1_hol | cam_r_L1_hol_3 | - | - | info | - | - | cycles (room) |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_2 | - | - | ok | - | - | cycles (room) |
| r_L1_yatak_odasi | cam_r_L1_yatak_odasi_3 | - | - | info | - | - | cycles (room) |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 1/4 | +0.17 | - | search 1.83 | D1 A1 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +0.17 | - | search 1.79 | D1 A4 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_hol_1 | r_L-1_hol | L-1 | cycles | room | - | - | ok | - | - | +0.67 | - | search 2.74 | D3 A3 | 0 | no | [preview](cam_r_L-1_hol_1_final_preview.jpg) [plan](cam_r_L-1_hol_1_plan.jpg) |
| cam_r_L-1_hol_2 | r_L-1_hol | L-1 | cycles | room | - | - | ok | - | - | +0.17 | - | search 2.62 | D3 A4 | 0 | no | [preview](cam_r_L-1_hol_2_final_preview.jpg) [plan](cam_r_L-1_hol_2_plan.jpg) |
| cam_r_L-1_hol_3 | r_L-1_hol | L-1 | cycles | room | - | - | info | - | - | +0.83 | - | search 2.62 | D4 A2 | 0 | no | [preview](cam_r_L-1_hol_3_final_preview.jpg) [plan](cam_r_L-1_hol_3_plan.jpg) |
| cam_r_L-1_kiler_1 | r_L-1_kiler | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | -1 | search 3.00 | D2 | 0 | no | [preview](cam_r_L-1_kiler_1_final_preview.jpg) [plan](cam_r_L-1_kiler_1_plan.jpg) |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.33 | -1 | search 3.00 | D2 | 0 | no | [preview](cam_r_L-1_kiler_2_1_final_preview.jpg) [plan](cam_r_L-1_kiler_2_1_plan.jpg) |
| cam_r_L-1_wc_1 | r_L-1_wc | L-1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 2.04 | D1 A1 | 0 | no | [preview](cam_r_L-1_wc_1_final_preview.jpg) [plan](cam_r_L-1_wc_1_plan.jpg) |
| cam_r_L-1_wc_2 | r_L-1_wc | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 1.90 | D1 A2 | 0 | no | [preview](cam_r_L-1_wc_2_final_preview.jpg) [plan](cam_r_L-1_wc_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | L-1 | cycles | room | - | - | ok | - | - | +0.00 | - | search 4.02 | D2 A5 | 0 | no | [preview](cam_r_L-1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_1_plan.jpg) |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | L-1 | cycles | room | - | - | info | - | - | +0.00 | - | search 3.87 | D2 A5 | 0 | no | [preview](cam_r_L-1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_2_plan.jpg) |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | L-1 | cycles | room | - | - | ok | - | - | +0.17 | - | search 3.78 | D2 A5 | 0 | no | [preview](cam_r_L-1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L-1_yatak_odasi_3_plan.jpg) |
| cam_r_L0_antre_1 | r_L0_antre | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | ok | not preferred 0/4 | +0.33 | - | search 3.82 | D2 A2 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_antre_2 | r_L0_antre | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 2.56 | D1 A2 | 0 | no | [preview](cam_r_L0_antre_2_final_preview.jpg) [plan](cam_r_L0_antre_2_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | -0.17 | - | search 2.60 | D2 A1 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | cycles | room | - | - | ok | - | - | +1.00 | - | search 2.58 | D3 A3 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_hol_3 | r_L0_hol | L0 | cycles | room | - | - | info | - | - | +0.50 | - | search 2.57 | D3 A3 | 0 | no | [preview](cam_r_L0_hol_3_final_preview.jpg) [plan](cam_r_L0_hol_3_plan.jpg) |
| cam_r_L0_kiler_1 | r_L0_kiler | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | ok | not preferred 0/4 | +5.33 | -2 | search 2.97 | D3 | 1 | no | [preview](cam_r_L0_kiler_1_final_preview.jpg) [plan](cam_r_L0_kiler_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.33 | -3 | search 2.57 | D6 A4 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | gate | - | - | ok | - | - | +5.50 | -3 | search 2.06 | D4 A3 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.50 | -1 | search 1.54 | D4 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | room | - | - | ok | - | - | +5.17 | - | search 3.51 | D5 A3 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | cycles | room | - | - | info | - | - | +5.17 | - | search 3.49 | D5 A4 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | cycles | room | - | - | info | - | - | +5.00 | -1 | search 3.44 | D6 A5 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_wc_1 | r_L0_wc | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +0.33 | - | search 2.02 | D3 | 0 | no | [preview](cam_r_L0_wc_1_final_preview.jpg) [plan](cam_r_L0_wc_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +6.17 | -1 | search 3.29 | D6 A2 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | gate | - | - | info | - | - | +6.33 | - | search 3.21 | D4 A4 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +6.83 | -2 | search 3.20 | D6 A5 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_balkon_1 | r_L1_balkon | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.17 | -1 | search 1.83 | D1 | 0 | no | [preview](cam_r_L1_balkon_1_final_preview.jpg) [plan](cam_r_L1_balkon_1_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | vision_check | a2 s 0.25 canny x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +7.83 | -4 | search 3.11 | D2 A3 | 0 | yes | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +6.67 | - | search 3.08 | D1 A3 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +7.67 | - | search 2.63 | D1 A3 | 0 | no | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +5.33 | -3 | search 3.93 | D2 A6 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +4.83 | -2 | search 3.71 | D2 A5 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +4.33 | -1 | search 3.63 | D2 A6 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | cycles | room | - | - | info | - | - | +4.83 | -3 | search 3.77 | D2 A8 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | cycles | room | - | - | info | - | - | +4.50 | -2 | search 3.40 | D2 A7 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | cycles | room | - | - | ok | - | - | +4.50 | - | search 3.35 | D1 A6 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | room | - | - | info | - | - | +0.67 | - | search 2.77 | D4 A3 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | cycles | room | - | - | info | - | - | +0.83 | - | search 2.54 | D2 A2 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | cycles | room | - | - | info | - | - | +0.67 | - | search 2.45 | D2 A1 | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | cycles | room | - | - | info | - | - | +6.17 | -1 | search 4.10 | D2 A7 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | cycles | room | - | - | ok | - | - | +5.67 | - | search 3.89 | D2 A4 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | cycles | room | - | - | info | - | - | +5.67 | -1 | search 3.87 | D2 A6 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 2 | 2 | 0 | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_hol | hall | L-1 | 3 | 0 | 3 | cam_r_L-1_hol_1, cam_r_L-1_hol_2, cam_r_L-1_hol_3 |
| r_L-1_kiler | storage | L-1 | 1 | 1 | 0 | cam_r_L-1_kiler_1 |
| r_L-1_kiler_2 | storage | L-1 | 1 | 1 | 0 | cam_r_L-1_kiler_2_1 |
| r_L-1_wc | wc | L-1 | 2 | 1 | 1 | cam_r_L-1_wc_1, cam_r_L-1_wc_2 |
| r_L-1_yatak_odasi | bedroom | L-1 | 3 | 0 | 3 | cam_r_L-1_yatak_odasi_1, cam_r_L-1_yatak_odasi_2, cam_r_L-1_yatak_odasi_3 |
| r_L0_antre | hall | L0 | 2 | 2 | 0 | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_hol | hall | L0 | 3 | 0 | 3 | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_kiler | storage | L0 | 1 | 1 | 0 | cam_r_L0_kiler_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 1 | 2 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 0 | 3 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_wc | wc | L0 | 1 | 1 | 0 | cam_r_L0_wc_1 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_balkon | balcony | L1 | 1 | 0 | 1 | cam_r_L1_balkon_1 |
| r_L1_banyo | bathroom | L1 | 3 | 1 | 2 | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | hall | L1 | 3 | 0 | 3 | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

### Why Cycles

- cam_r_L-1_hol_1: room: polish: room
- cam_r_L-1_hol_2: room: polish: room
- cam_r_L-1_hol_3: room: polish: room
- cam_r_L-1_wc_1: vision_check: added_by_polish furniture at [844.9, 358.7, 953.4, 455.9]
- cam_r_L-1_yatak_odasi_1: room: polish: room
- cam_r_L-1_yatak_odasi_2: room: polish: room
- cam_r_L-1_yatak_odasi_3: room: polish: room
- cam_r_L0_hol_1: room: polish: room
- cam_r_L0_hol_2: room: polish: room
- cam_r_L0_hol_3: room: polish: room
- cam_r_L0_mutfak_1: vision_check: added_by_polish furniture at [1471.0, 524.3, 1602.7, 580.8]
- cam_r_L0_mutfak_2: gate: no ladder attempt passed the gate: a1 reject (depth, edges); a2 reject (edges); a3 reject (edges)
- cam_r_L0_salon_1: room: polish: room
- cam_r_L0_salon_2: room: polish: room
- cam_r_L0_salon_3: room: polish: room
- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: gate: no ladder attempt passed the gate: a1 reject (edges, masks); a2 reject (masks); a3 reject (masks)
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L1_balkon_1: vision_check: added_by_polish furniture at [165.5, 682.4, 1484.3, 1076.1]; added_by_polish furniture at [165.5, 682.4, 1484.3, 1076.1]
- cam_r_L1_banyo_1: vision_check: added_by_polish furniture at [1523.2, 813.2, 1920.0, 1074.7]
- cam_r_L1_banyo_2: vision_check: added_by_polish furniture at [214.7, 0.0, 951.6, 1080.0]; added_by_polish furniture at [214.7, 0.0, 951.6, 1080.0]
- cam_r_L1_cocuk_odasi_1: room: polish: room
- cam_r_L1_cocuk_odasi_2: room: polish: room
- cam_r_L1_cocuk_odasi_3: room: polish: room
- cam_r_L1_ebeveyn_yatak_odasi_1: room: polish: room
- cam_r_L1_ebeveyn_yatak_odasi_2: room: polish: room
- cam_r_L1_ebeveyn_yatak_odasi_3: room: polish: room
- cam_r_L1_hol_1: room: polish: room
- cam_r_L1_hol_2: room: polish: room
- cam_r_L1_hol_3: room: polish: room
- cam_r_L1_yatak_odasi_1: room: polish: room
- cam_r_L1_yatak_odasi_2: room: polish: room
- cam_r_L1_yatak_odasi_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_2 | cycles | disputed | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L-1_banyo_2 | polished | disputed | d_L-1_005 | door | optional | from_documents | kat_planlari.pdf p1 path:18 vector 1.00 | info | - |
| cam_r_L-1_banyo_2 | polished | missing | f_L-1_009 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_hol_3 | cycles | missing | d_L0_006 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:11E KAPI_80 vector 1.00; kat_planlari.pdf p2 path:21 vector 1.00 | info | - |
| cam_r_L0_kiler_1 | cycles | disputed | d_L0_007 | door | optional | from_documents | mobilya_plani.dxf KAPI INSERT:120 KAPI_80 vector 1.00; kat_planlari.pdf p2 path:23 vector 1.00 | info | - |
| cam_r_L0_mutfak_1 | cycles | disputed | f_L0_010 | fridge | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:140 BUZDOLABI vector 1.00 | info | - |
| cam_r_L0_mutfak_1 | cycles | disputed | f_L0_013 | chair | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:146 SANDALYE vector 1.00 | info | - |
| cam_r_L0_mutfak_1 | polished | disputed | f_L0_010 | fridge | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:140 BUZDOLABI vector 1.00 | info | - |
| cam_r_L0_mutfak_1 | polished | disputed | f_L0_013 | chair | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:146 SANDALYE vector 1.00 | info | - |
| cam_r_L0_salon_3 | cycles | disputed | dec_L0_006 | blind | optional | added_by_ai | building.json ai 0.90; building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_yatak_odasi_1 | cycles | disputed | f_L0_014 | bed_double | optional | from_documents | mobilya_plani.dxf MOBILYA INSERT:148 YATAK_CIFT vector 1.00 | info | - |
| cam_r_L0_yatak_odasi_1 | cycles | disputed | dec_L0_020 | curtain | optional | added_by_ai | building.json ai 0.90; building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | cycles | missing | f_L1_018 | shower | required | added_by_ai | building.json ai 0.90 | yes | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | polished | missing | f_L1_018 | shower | required | added_by_ai | building.json ai 0.90 | yes | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | missing | f_L1_018 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | polished | disputed | f_L1_018 | shower | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_hol_1 | cycles | disputed | dec_L1_008 | mirror | optional | added_by_ai | building.json ai 0.90; building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_hol_3 | cycles | disputed | d_L1_002 | door | optional | from_documents | kat_planlari.pdf p3 path:12 vector 1.00 | info | - |
| cam_r_L1_hol_3 | cycles | disputed | d_L1_004 | door | optional | from_documents | kat_planlari.pdf p3 path:16 vector 1.00 | info | - |
| cam_r_L1_yatak_odasi_3 | cycles | disputed | dec_L1_016 | curtain | optional | added_by_ai | building.json ai 0.90; building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |

## Needs review

- cam_r_L1_banyo_1: f_L1_018 (shower, added_by_ai): missing

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

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 4 regions (use: read 4). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | kat_planlari.pdf | floor_plan | title (0.99) | verified | L-1 | base | read |
| r2 | kat_planlari.pdf | floor_plan | title (0.99) | verified | L0 | base | read |
| r3 | kat_planlari.pdf | floor_plan | title (0.99) | verified | L1 | base | read |
| r4 | mobilya_plani.dxf | furniture_plan | title (0.99) | verified | L0 | base | read |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | r1 | - |
| L0 | Zemin Kat | floor | r2 | - |
| L1 | 1. Kat | floor | r3 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r1, r2, r3 |

Strays (entities far from every drawing, ignored): 0.

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| kat_planlari.pdf | pdf | 0.04 | pdf_scale_text | - | - |
| mobilya_plani.dxf | dxf | 0.00 | dxf_insunits | area_labels None - (0); level_marks None - (0); door_widths mm 1.00 (7); wall_thickness None 0.52 (96); text_height mm 1.00 (8); dimensions None - (0) | - |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/kat_planlari_pdf_s1.jpg](debug/kat_planlari_pdf_s1.jpg)
- [debug/kat_planlari_pdf_s2.jpg](debug/kat_planlari_pdf_s2.jpg)
- [debug/kat_planlari_pdf_s3.jpg](debug/kat_planlari_pdf_s3.jpg)
- [debug/mobilya_plani_dxf_s1.jpg](debug/mobilya_plani_dxf_s1.jpg)

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 7 piece(s) added, 1 wall cabinet run(s).

### Salon (r_L0_salon, living): completed

- added f_L0_025: ottoman 0.60 x 0.60 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001, f_L0_003, f_L0_005

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed

- added f_L0_026: bench 1.40 x 0.45 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_014, f_L0_017

### Mutfak (r_L0_mutfak, kitchen): completed

- added f_L0_027: tall_cabinet 0.40 x 0.58 (confidence 0.90, ai)
- added f_L0_028: chair 0.45 x 0.45 (confidence 0.90, ai)
- added f_L0_029: chair 0.45 x 0.45 (confidence 0.90, ai)
- added f_L0_030: chair 0.45 x 0.45 (confidence 0.90, ai)
- added f_L0_031: chair 0.45 x 0.45 (confidence 0.90, ai)
- 1 wall cabinet run(s) over the drawn counter
- refused f_L0_011 -> table_dining: only pass 2 changes it (a drawn piece needs both passes)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_008, f_L0_009, f_L0_010, f_L0_011

### WC (r_L0_wc, wc): completed (nothing to ask: no changeable drawn piece and nothing the room may get)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_019, f_L0_020

### Kiler (r_L0_kiler, storage): skipped (room type storage: no furniture types to complete)

No change, no addition.

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 21 of 21 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 21 ok, 0 failed; 0 changed by the AI.

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

- style exterior facade render in charcoal, roof concrete_tiles in anthracite, window_frame as inside (painted_metal_white), door as inside (painted_wood_white), paving paving in grey, garden grass from style.exterior_fallback of wenart/defaults.yaml (no word for them in the brief)
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
| cabinet_fronts | 2 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_027, furn_f_L0_032 |
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
| sill_height | 16 | window sill_height not in the JSON; default | win_L-1_001, win_L-1_002, win_L-1_003 |
| skirting | 13 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1_kiler, skirting_r_L-1_hol, skirting_r_L-1_yatak_odasi |
| slab_thickness | 19 | slab between levels | w_L-1_001, w_L-1_002, w_L-1_003 |
| wood | 3 | style floor 'concrete_polished' is not wood; default veneer for furniture frames | furniture, furniture, furniture |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L-1_wc | cam_r_L-1_wc_2 | cam_r_L-1_wc_1 (vision_check) | ok |
| r_L0_mutfak | cam_r_L0_mutfak_3 | cam_r_L0_mutfak_1 (vision_check), cam_r_L0_mutfak_2 (gate) | ok |
| r_L1_banyo | cam_r_L1_banyo_3 | cam_r_L1_banyo_1 (vision_check), cam_r_L1_banyo_2 (vision_check) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_hol (rung None), r_L-1_yatak_odasi (rung None), r_L0_hol (rung None), r_L0_salon (rung None), r_L0_yatak_odasi (rung None), r_L1_cocuk_odasi (rung None), r_L1_ebeveyn_yatak_odasi (rung None), r_L1_hol (rung None), r_L1_yatak_odasi (rung None).

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

Assets: textures CC0 x 8; furniture/decor models CC-BY-4.0 x 106, CC-BY-SA-4.0 x 1, CC0 x 2, generated (TRELLIS.2-4B, MIT) x 12 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Memoirs Stately Close Coupled Toilet" by Yaiyeondurising (https://sketchfab.com/3d-models/4398bcb5976945b08f195816340247b8), CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1_007)
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_010)
- "Stove from Poly by Google" by IronEqual (https://sketchfab.com/3d-models/68e164f1a9414c29820ac2eaf6d8ac04), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_009)
- "JuiceMachine" by voxelpoint (https://sketchfab.com/3d-models/6b46b33bdff44269bf9391774bb8dd63), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L0_012, dec_L1_003, dec_L1_012, dec_L1_019)
- "Simple Tall Shelf" by Blender3D (https://sketchfab.com/3d-models/b46803ba0bc64e12b31f832fb761c4e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L1_004, f_L1_015)
- "Animated low poly toilet" by Gamedirection (https://sketchfab.com/3d-models/c901dfa120a0487a9f5c9a2d241f70ab), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_019, f_L-1_010, f_L1_020)
- "Bench with Cloth" by finemods (https://sketchfab.com/3d-models/eee70cb7980a4ca7aa0a2f86c492283e), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1_006)
- "Bathroom1" by neutralize (https://sketchfab.com/3d-models/f76c502218884914a27148f656a9b656), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_020, f_L-1_008, f_L-1_011, f_L1_019)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L-1_banyo_1 | calibrated | yes | no | - |
| cam_r_L-1_banyo_2 | calibrated | yes | no | - |
| cam_r_L-1_kiler_1 | calibrated | yes | no | - |
| cam_r_L-1_kiler_2_1 | calibrated | yes | no | - |
| cam_r_L-1_wc_1 | calibrated | yes | yes | furniture [844.9, 358.7, 953.4, 455.9] (score) |
| cam_r_L-1_wc_2 | calibrated | yes | no | - |
| cam_r_L0_antre_1 | calibrated | yes | no | - |
| cam_r_L0_antre_2 | calibrated | yes | no | - |
| cam_r_L0_kiler_1 | calibrated | yes | no | - |
| cam_r_L0_mutfak_1 | calibrated | yes | yes | furniture [1471.0, 524.3, 1602.7, 580.8] (score) |
| cam_r_L0_mutfak_3 | calibrated | yes | no | - |
| cam_r_L0_wc_1 | calibrated | yes | no | - |
| cam_r_L1_balkon_1 | calibrated | yes | yes | furniture [165.5, 682.4, 1484.3, 1076.1] (score); furniture [165.5, 682.4, 1484.3, 1076.1] (score) |
| cam_r_L1_banyo_1 | calibrated | yes | yes | furniture [1523.2, 813.2, 1920.0, 1074.7] (score) |
| cam_r_L1_banyo_2 | calibrated | yes | yes | furniture [214.7, 0.0, 951.6, 1080.0] (score); furniture [214.7, 0.0, 951.6, 1080.0] (score) |
| cam_r_L1_banyo_3 | calibrated | yes | no | - |

## Stages

This run (`20261009-092258-full-20261009T092915Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 4.9 s | - |
| pipeline | ok | 8.7 s | - |
| pipeline_final | skipped | 0.0 s | no questions |
| recognize | skipped | 0.0 s | no questions |
| fit | ok | 2.5 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.4 s | - |
| layout | ok | 86.0 s | - |
| decor_ask | ok | 102.1 s | - |
| assets | ok | 1.2 s | - |
| decor | ok | 4.7 s | - |
| refit | ok | 6.5 s | - |
| build | ok | 3.0 min | - |
| render | ok | 4.0 min | - |
| export | ok | 82.9 s | - |
| controls | ok | 78.4 s | - |
| gate | ok | 81.2 s | gate decision ok |
| polish | ok | 7.8 min | - |
| detect | ok | 10.3 s | - |
| expected | ok | 16.7 s | - |
| check | ok | 2.8 min | - |
| combine | ok | 27.3 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
