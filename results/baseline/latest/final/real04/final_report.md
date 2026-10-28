# Final report: real04

36 views: 12 polished, 24 Cycles (gate_validation 5, room 17, vision_check 2). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 36 |
| interior / exterior views | 31 / 5 |
| variant | base |
| polished | 12 |
| Cycles | 24 (gate_validation 5, room 17, vision_check 2) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 17 |
| needs_review views | 6 |
| unverified pieces in view (sum over views) | 41 |
| rooms mixing polished and Cycles | 2 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.83 .. +2.67 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 25 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 9, m5 5, search 22 |
| camera score (min / mean / max) | 2.07 / 4.09 / 5.28 |
| rooms by number of views | 1 with 0, 3 with 1, 5 with 2, 6 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 7.0 min / 4.0 min / 87.2 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 29.9 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 15 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 777.0 MB |
| [real04.glb](3d/real04.glb) | 1726.7 MB |

36 cameras; textures scaled to at most 1024 px (385 scaled) for the download.

## AI decor

151 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 34 rooms; 186 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- the polish added an object in cam_r_L-1_mutfak_1, cam_r_L1_koridor_1: the Cycles render is final
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 12 piece(s) moved beyond the tolerance, 67 locked-rule violation(s)
- AI completion: 5 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 100.0 % (limit 95 %), 64 comparisons |
| negative controls rejected | 97.0 % (limit 90 %), 167 comparisons |
| effect | polish allowed |

### Exterior views

Exterior decision: **polish_disabled**. The exterior views are the Cycles render; the rooms are not affected.

| item | value |
|---|---|
| benign exterior comparisons accepted | 95.8 % (limit 95 %), 24 comparisons |
| negative exterior comparisons rejected | 88.3 % (limit 90 %), 60 comparisons |

Reasons:

- negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L-1: [contact_L-1.jpg](contact_L-1.jpg)

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- exterior_base: [contact_sbs_exterior_base.jpg](contact_sbs_exterior_base.jpg)

- r_L-1_banyo: [contact_sbs_r_L-1_banyo.jpg](contact_sbs_r_L-1_banyo.jpg)

- r_L-1_koridor_2: [contact_sbs_r_L-1_koridor_2.jpg](contact_sbs_r_L-1_koridor_2.jpg)

- r_L-1_mutfak: [contact_sbs_r_L-1_mutfak.jpg](contact_sbs_r_L-1_mutfak.jpg)

- r_L-1_salon: [contact_sbs_r_L-1_salon.jpg](contact_sbs_r_L-1_salon.jpg)

- r_L0_banyo: [contact_sbs_r_L0_banyo.jpg](contact_sbs_r_L0_banyo.jpg)

- r_L0_e_banyo: [contact_sbs_r_L0_e_banyo.jpg](contact_sbs_r_L0_e_banyo.jpg)

- r_L0_e_yatak_odasi: [contact_sbs_r_L0_e_yatak_odasi.jpg](contact_sbs_r_L0_e_yatak_odasi.jpg)

- r_L0_koridor: [contact_sbs_r_L0_koridor.jpg](contact_sbs_r_L0_koridor.jpg)

- r_L0_yatak_odasi: [contact_sbs_r_L0_yatak_odasi.jpg](contact_sbs_r_L0_yatak_odasi.jpg)

- r_L0_yatak_odasi_3: [contact_sbs_r_L0_yatak_odasi_3.jpg](contact_sbs_r_L0_yatak_odasi_3.jpg)

- r_L1_banyo: [contact_sbs_r_L1_banyo.jpg](contact_sbs_r_L1_banyo.jpg)

- r_L1_koridor: [contact_sbs_r_L1_koridor.jpg](contact_sbs_r_L1_koridor.jpg)

- r_L1_oyun_aktivite_ve_dinlenme_odasi: [contact_sbs_r_L1_oyun_aktivite_ve_dinlenme_odasi.jpg](contact_sbs_r_L1_oyun_aktivite_ve_dinlenme_odasi.jpg)

- r_L1_teras: [contact_sbs_r_L1_teras.jpg](contact_sbs_r_L1_teras.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| exterior_base | ext_1 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_2 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_3 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_5 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_7 | - | - | info | - | - | cycles (gate_validation) |
| r_L-1_banyo | cam_r_L-1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_banyo | cam_r_L-1_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_koridor_2 | cam_r_L-1_koridor_2_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L-1_koridor_2 | cam_r_L-1_koridor_2_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_mutfak | cam_r_L-1_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L-1_mutfak | cam_r_L-1_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_mutfak | cam_r_L-1_mutfak_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1_salon | cam_r_L-1_salon_1 | - | - | info | - | - | cycles (room) |
| r_L-1_salon | cam_r_L-1_salon_2 | - | - | info | - | - | cycles (room) |
| r_L-1_salon | cam_r_L-1_salon_3 | - | - | info | - | - | cycles (room) |
| r_L0_banyo | cam_r_L0_banyo_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L0_banyo | cam_r_L0_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_e_banyo | cam_r_L0_e_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_e_yatak_odasi | cam_r_L0_e_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L0_e_yatak_odasi | cam_r_L0_e_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L0_e_yatak_odasi | cam_r_L0_e_yatak_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L0_koridor | cam_r_L0_koridor_1 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi_3 | cam_r_L0_yatak_odasi_3_1 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi_3 | cam_r_L0_yatak_odasi_3_2 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi_3 | cam_r_L0_yatak_odasi_3_3 | - | - | info | - | - | cycles (room) |
| r_L1_banyo | cam_r_L1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_koridor | cam_r_L1_koridor_1 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L1_koridor | cam_r_L1_koridor_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L1_teras | cam_r_L1_teras_1 | - | - | info | - | - | cycles (room) |
| r_L1_teras | cam_r_L1_teras_2 | - | - | info | - | - | cycles (room) |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +2.50 | - | agent | D3 A1 | 1 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +2.50 | - | agent | D2 A2 | 0 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 1/2 | +1.33 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +1.67 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_2_final_preview.jpg) [plan](cam_r_L-1_koridor_2_2_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | -1.00 | -1 | search 4.60 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/2 | -1.33 | -1 | search 3.79 | D4 A1 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/2 | -1.17 | 0 | search 4.25 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +0.67 | -3 | search 3.68 | D8 A2 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +0.83 | -3 | search 3.50 | D11 A7 | 2 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +0.83 | -3 | search 3.59 | D10 A3 | 3 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/2 | +2.17 | - | agent | D2 A2 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +2.17 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +2.33 | - | search 2.58 | D2 A1 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.67 | -3 | search 4.95 | D5 A4 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.17 | 0 | search 4.62 | D5 A2 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +0.83 | -1 | search 4.72 | D5 A4 | 0 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 1/2 | +2.67 | - | search 2.07 | D6 | 1 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.50 | -3 | search 4.68 | D4 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +0.67 | -1 | search 4.18 | D5 A4 | 3 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.83 | -4 | search 4.04 | D5 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.67 | -4 | search 5.28 | D4 A5 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +2.17 | -4 | search 4.57 | D5 A3 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +2.17 | -4 | search 4.59 | D5 A2 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | -0.33 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +1.50 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_koridor_2 | r_L1_koridor | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/2 | +1.50 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L1_koridor_2_final_preview.jpg) [plan](cam_r_L1_koridor_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 4.65 | D7 A3 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 4.12 | D5 A3 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | -0.17 | -2 | search 3.90 | D8 A3 | 1 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.67 | 0 | search 3.97 | D1 A3 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -5.17 | 0 | search 3.77 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.50 | 0 | m5 blocked | D7 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D7 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.83 | 0 | m5 blocked | D4 | 1 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.17 | 0 | m5 | D10 | 1 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.83 | 0 | m5 | D6 | 1 | yes | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 2 | 2 | 0 | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_banyo_2 | bathroom | L-1 | 0 | 0 | 0 | - |
| r_L-1_koridor | hall | L-1 | 0 | 0 | 0 | - |
| r_L-1_koridor_2 | hall | L-1 | 2 | 2 | 0 | cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2 |
| r_L-1_mutfak | kitchen | L-1 | 3 | 2 | 1 | cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3 |
| r_L-1_mutfak_2 | kitchen | L-1 | 0 | 0 | 0 | - |
| r_L-1_salon | living | L-1 | 3 | 0 | 3 | cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3 |
| r_L-1_salon_2 | living | L-1 | 0 | 0 | 0 | - |
| r_L0_banyo | bathroom | L0 | 2 | 2 | 0 | cam_r_L0_banyo_1, cam_r_L0_banyo_2 |
| r_L0_banyo_2 | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_banyo | bathroom | L0 | 1 | 1 | 0 | cam_r_L0_e_banyo_1 |
| r_L0_e_banyo_2 | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3 |
| r_L0_e_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_koridor | hall | L0 | 1 | 1 | 0 | cam_r_L0_koridor_1 |
| r_L0_koridor_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_merdiven | hall | L0 | 0 | 0 | 0 | - |
| r_L0_merdiven_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L0_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_3 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3 |
| r_L0_yatak_odasi_4 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L1_banyo | bathroom | L1 | 1 | 1 | 0 | cam_r_L1_banyo_1 |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 2 | 1 | 1 | cam_r_L1_koridor_1, cam_r_L1_koridor_2 |
| r_L1_koridor_2 | stair | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | living | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | living | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 2 | 0 | 2 | cam_r_L1_teras_1, cam_r_L1_teras_2 |
| r_L1_teras_2 | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_banyo_2 (twin of r_L0_e_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_4 (twin of r_L0_yatak_odasi_3), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_koridor_2 (twin of r_L1_koridor), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi), r_L1_teras_2 (twin of r_L1_teras).

Rooms without a rendered view: r_L0_merdiven (stair core: the stair fills the room, its only camera point is inside the stair; the hall shows it (docs/milestone11.md §1.3 M5)).

### Why Cycles

- cam_r_L-1_mutfak_1: vision_check: added_by_polish door at [901.8, 474.1, 985.2, 775.5]
- cam_r_L-1_salon_1: room: polish: room
- cam_r_L-1_salon_2: room: polish: room
- cam_r_L-1_salon_3: room: polish: room
- cam_r_L0_e_yatak_odasi_1: room: polish: room
- cam_r_L0_e_yatak_odasi_2: room: polish: room
- cam_r_L0_e_yatak_odasi_3: room: polish: room
- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: room: polish: room
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L0_yatak_odasi_3_1: room: polish: room
- cam_r_L0_yatak_odasi_3_2: room: polish: room
- cam_r_L0_yatak_odasi_3_3: room: polish: room
- cam_r_L1_koridor_1: vision_check: added_by_polish furniture at [1099.8, 916.0, 1447.9, 960.6]; added_by_polish window at [1066.9, 619.8, 1456.4, 963.2]; added_by_polish door at [1066.9, 619.8, 1456.4, 963.2]
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: room: polish: room
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room: polish: room
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: room: polish: room
- cam_r_L1_teras_1: room: polish: room
- cam_r_L1_teras_2: room: polish: room
- ext_1: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_2: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_3: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_5: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_7: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_e_yatak_odasi_1 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 49 % of its pixels > 0.10 m outside the drawing, 412128 px |
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 35 % of its pixels > 0.10 m outside the drawing, 509531 px |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 24 % of its pixels > 0.10 m outside the drawing, 42973 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 14 % of its pixels > 0.10 m outside the drawing, 5289 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 23 % of its pixels > 0.10 m outside the drawing, 45659 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 14 % of its pixels > 0.10 m outside the drawing, 5455 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 33 % of its pixels > 0.10 m outside the drawing, 42855 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 26 % of its pixels > 0.10 m outside the drawing, 10176 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 73 % of its pixels > 0.10 m outside the drawing, 12117 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 66 % of its pixels > 0.10 m outside the drawing, 9885 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3034 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 2597 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 6989 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1454 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3252 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 52 % of its pixels > 0.10 m outside the drawing, 15686 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12172 px |

## Needs review

- cam_r_L0_e_yatak_odasi_1: json cross-check misplaced: f_L0_007
- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: f_L0_007
- ext_1: json cross-check misplaced: win_L0_001; json cross-check misplaced: win_arch_r_L0_yatak_odasi_3_1
- ext_2: json cross-check misplaced: win_L0_004; json cross-check misplaced: win_arch_r_L0_yatak_odasi_4_1
- ext_5: json cross-check misplaced: win_L-1_001; json cross-check misplaced: win_L-1_003; json cross-check misplaced: win_L0_001; json cross-check misplaced: win_L0_002; json cross-check misplaced: win_L0_003; json cross-check misplaced: win_L0_004; json cross-check misplaced: win_arch_r_L0_yatak_odasi_3_1
- ext_7: json cross-check misplaced: win_L-1_001; json cross-check misplaced: win_L-1_002; json cross-check misplaced: win_L-1_004; json cross-check misplaced: win_arch_r_L0_yatak_odasi_4_1

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
- f_L-1b_057
- f_L-1b_058
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
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_071
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_071
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061, f_L-1_087
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_e_yatak_odasi_2: f_L0_023
- cam_r_L0_koridor_1: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3_1: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_023
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_023
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_023
- ext_1: win_arch_r_L0_yatak_odasi_3_1
- ext_2: win_arch_r_L0_yatak_odasi_4_1
- ext_3: win_arch_r_L0_yatak_odasi_4_1
- ext_5: win_arch_r_L0_yatak_odasi_3_1
- ext_7: win_arch_r_L0_yatak_odasi_4_1

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
| f_L1_036 | furniture | table_coffee | 3dwh_75ac3c7d6dc1da28c99a0ad6 | the vision check sees more than one object |
| f_L1_038 | furniture | table_coffee | 3dwh_75ac3c7d6dc1da28c99a0ad6 | the vision check sees more than one object |

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
| c_041 | type_disagreement | f_L-1b_056 | f_L-1b_056: the AI passes typed it fridge; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_042 | type_disagreement | f_L-1b_061 | f_L-1b_061: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
| c_043 | type_disagreement | f_L-1b_062 | f_L-1b_062: the AI passes typed it wall_cabinet; the block name says sink_kitchen | typed sink_kitchen (trust order: vector geometry and block names > AI) |
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
| c_054 | symbol_type_disagreement | f_L-1b_047 | f_L-1b_047: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_055 | symbol_type_disagreement | f_L-1b_049 | f_L-1b_049: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_056 | symbol_type_disagreement | f_L-1b_057 | f_L-1b_057: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_057 | symbol_type_disagreement | f_L-1b_058 | f_L-1b_058: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_058 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L1_029 | f_L1_029: sym_L1_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the room misses it (the living room's reading_corner group has no armchair); inferred, listed in the report (reading.tie_break) |
| c_063 | symbol_type_disagreement | f_L1_030 | f_L1_030: sym_L1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_064 | symbol_type_disagreement | f_L1_031 | f_L1_031: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): its real product size is the nearer one to the drawn size; inferred, listed in the report (reading.tie_break) |
| c_065 | symbol_type_disagreement | f_L1_032 | f_L1_032: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) armchair | typed armchair by code (not floor_lamp): the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; inferred, listed in the report (reading.tie_break) |
| c_066 | symbol_type_disagreement | f_L1_036 | f_L1_036: sym_L1_x6881d71b: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | unresolved: the drawn footprint is kept as unknown, unverified |
| c_067 | symbol_type_disagreement | f_L1_037 | f_L1_037: sym_L1_x59e6f5f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sideboard, pass 2 (zai-org/GLM-4.6V-Flash) bench | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L1_038 | f_L1_038: sym_L1_xf35ed8f5: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bookshelf, pass 2 (zai-org/GLM-4.6V-Flash) console_table | typed table_coffee by code (ai_member): table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recogni; inferred, listed in the report |
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

- site symbols: furniture: 6 drawn site symbol(s) typed furniture (a furniture symbol; not built): sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006
- site.plinth: no SB. mark: the plinth up to the ground floor
- light_well win_L-1_003: window sill -2.10 m, ground outside -1.67 m: an open concrete light well 0.8 m deep, 4.56 m wide (no light well drawn)
- front_court win_L-1_004: window sill 1.18 m below the ground outside (> 1 m): an inferred sunken front court 3 m deep, 5.36 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn)

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 33 piece(s) added, 12 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_089: bookshelf 1.00 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_021, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L-1_031, f_L-1_032, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_037, f_L-1_059, f_L-1_060, f_L-1_063, f_L-1_064, f_L-1_070, f_L-1_071, f_L-1_073, f_L-1_075, f_L-1_077

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_095: bookshelf 1.00 x 0.35 (confidence -, rule, mirrored from f_L-1_089)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_022, f_L-1_023, f_L-1_038, f_L-1_039, f_L-1_040, f_L-1_041, f_L-1_042, f_L-1_043, f_L-1_044, f_L-1_045, f_L-1_046, f_L-1_047, f_L-1_048, f_L-1_057, f_L-1_058, f_L-1_065, f_L-1_066, f_L-1_069, f_L-1_072, f_L-1_074, f_L-1_076, f_L-1_078

### Mutfak (r_L-1_mutfak, kitchen): completed

- added f_L-1_090: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- not placed dining: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_005, f_L-1_008, f_L-1_009, f_L-1_067, f_L-1_081, f_L-1_083, f_L-1_085

### Mutfak (r_L-1_mutfak_2, kitchen): mirrored (decisions of r_L-1_mutfak (twin), not asked again)

- added f_L-1_096: fridge 0.60 x 0.60 (confidence -, rule, mirrored from f_L-1_090)
- 3 wall cabinet run(s) over the drawn counter
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

### Salon (r_L-1b_salon, living): completed

- added f_L-1b_071: side_table 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_072: side_table 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_073: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L-1b_074: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_075: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_042, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_056, f_L-1b_060, f_L-1b_062

### Salon (r_L-1b_salon_2, living): completed (partner r_L-1b_salon (twin) not used: 2 of 5 copied pieces fail a check here (side_table: the copy fails doors_free, wall_contact here; side_table: the copy fails clearance_ok, wall_contact here); completed itself)

- added f_L-1b_080: side_table 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_081: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_082: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L-1b_083: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_084: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_003, f_L-1b_004, f_L-1b_006, f_L-1b_007, f_L-1b_008, f_L-1b_017, f_L-1b_018, f_L-1b_019, f_L-1b_020, f_L-1b_021, f_L-1b_022, f_L-1b_023, f_L-1b_024, f_L-1b_025, f_L-1b_039, f_L-1b_041, f_L-1b_045, f_L-1b_047, f_L-1b_048, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_059, f_L-1b_061

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_079: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): completed (partner r_L-1b_koridor (twin) not used: the twin's drawn furniture does not map onto this room: drawn stair f_L-1b_016 has no counterpart here; completed itself)

- added f_L-1b_088: console_table 0.90 x 0.30 (confidence -, rule)
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

- added f_L1_046: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_047: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_048: potted_plant 0.45 x 0.45 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no place passes the checks)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_006, f_L1_007, f_L1_013, f_L1_017, f_L1_020, f_L1_035, f_L1_036

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): completed (partner r_L1_oyun_aktivite_ve_dinlenme_odasi (twin) not used: 1 of 3 copied pieces fail a check here (floor_lamp: the copy fails wall_contact here); completed itself)

- added f_L1_050: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_051: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_052: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_053: potted_plant 0.45 x 0.45 (confidence -, rule)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_010, f_L1_011, f_L1_014, f_L1_018, f_L1_019, f_L1_037, f_L1_038

### Koridor (r_L1_koridor, hall): completed

- added f_L1_049: shoe_cabinet 0.60 x 0.25 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_027

### Koridor (r_L1_koridor_2, hall): mirrored (decisions of r_L1_koridor (twin), not asked again)

- added f_L1_054: shoe_cabinet 0.60 x 0.25 (confidence -, rule, mirrored from f_L1_049)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_028

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_021, f_L1_025

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_016, f_L1_022, f_L1_026

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 152 ok, 12 failed; 44 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_031 | chair (chair) | 0.19 | 0.00 | - | - |
| f_L-1_038 | table_dining (table_dining) | 0.08 | - | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.71 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L0_032 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_019 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_032 | armchair (armchair) | 0.30 | 0.00 | - | - |

Locked-rule violations:

- walls: must stay as drawn (byte-equal): removed w_L-1b_001, w_L-1b_002, w_L-1b_003, w_L-1b_004, w_L-1b_005, w_L-1b_006, w_L-1b_007, w_L-1b_008, w_L-1b_009, w_L-1b_010, w_L-1b_011, w_L-1b_012, w_L-1b_013
- openings: must stay as drawn (byte-equal): changed d_L0_011, d_L1_001, d_L1_002, d_L1_003, d_L1_004, d_L1_005, d_L1_006, win_L-1_001, win_L-1_002, win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L1_001, win_L1_002; removed d_L-1b_001, d_L-1b_002, d_L-1b_003, d_L-1b_004, o_L-1b_001, o_L-1b_002, win_L-1b_001, win_L-1b_002; added win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1
- rooms: must stay as drawn (byte-equal): changed r_L1_oyun_aktivite_ve_dinlenme_odasi; removed r_L-1b_banyo, r_L-1b_banyo_2, r_L-1b_koridor, r_L-1b_koridor_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_salon, r_L-1b_salon_2
- f_L-1_073: moved 0.709 m by the agent (> 0.3 m)
- f_L-1_074: moved 0.717 m by the agent (> 0.3 m)
- f_L-1b_001: drawn unknown removed
- f_L-1b_002: drawn unknown removed
- f_L-1b_003: drawn kitchen_counter removed
- f_L-1b_004: drawn kitchen_counter removed
- f_L-1b_005: drawn kitchen_island removed
- f_L-1b_006: drawn unknown removed
- f_L-1b_007: drawn stove removed
- f_L-1b_008: drawn sink_kitchen removed
- f_L-1b_009: drawn kitchen_counter removed
- f_L-1b_010: drawn kitchen_counter removed
- f_L-1b_011: drawn kitchen_island removed
- f_L-1b_012: drawn unknown removed
- f_L-1b_013: drawn stove removed
- f_L-1b_014: drawn sink_kitchen removed
- f_L-1b_015: drawn stair removed
- f_L-1b_016: drawn stair removed
- f_L-1b_017: drawn table_dining removed
- f_L-1b_018: drawn chair removed
- f_L-1b_019: drawn chair removed
- f_L-1b_020: drawn chair removed
- f_L-1b_021: drawn chair removed
- f_L-1b_022: drawn chair removed
- f_L-1b_023: drawn chair removed
- f_L-1b_024: drawn chair removed
- f_L-1b_025: drawn chair removed
- f_L-1b_026: drawn table_dining removed
- f_L-1b_027: drawn chair removed
- f_L-1b_028: drawn chair removed
- f_L-1b_029: drawn chair removed
- f_L-1b_030: drawn chair removed
- f_L-1b_031: drawn chair removed
- f_L-1b_032: drawn chair removed
- f_L-1b_033: drawn chair removed
- f_L-1b_034: drawn chair removed
- f_L-1b_035: drawn washbasin removed
- f_L-1b_036: drawn washbasin removed
- f_L-1b_037: drawn toilet removed
- f_L-1b_038: drawn toilet removed
- f_L-1b_039: drawn bar_stool removed
- f_L-1b_040: drawn bar_stool removed
- f_L-1b_041: drawn sofa removed
- f_L-1b_042: drawn sofa removed
- f_L-1b_043: drawn bathtub removed
- f_L-1b_044: drawn bathtub removed
- f_L-1b_045: drawn sofa removed
- f_L-1b_046: drawn sofa removed
- f_L-1b_047: drawn floor_lamp removed
- f_L-1b_048: drawn floor_lamp removed
- f_L-1b_049: drawn floor_lamp removed
- f_L-1b_050: drawn floor_lamp removed
- f_L-1b_051: drawn armchair removed
- f_L-1b_052: drawn armchair removed
- f_L-1b_053: drawn armchair removed
- f_L-1b_054: drawn armchair removed
- f_L-1b_055: drawn sink_kitchen removed
- f_L-1b_056: drawn sink_kitchen removed
- f_L-1b_057: drawn unknown removed
- f_L-1b_058: drawn unknown removed
- f_L-1b_059: drawn sink_kitchen removed
- f_L-1b_060: drawn sink_kitchen removed
- f_L-1b_061: drawn sink_kitchen removed
- f_L-1b_062: drawn sink_kitchen removed

## Exterior views

5 of 5 exterior view(s) of variant `base` rendered; 2 dropped (no camera place worked).

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)
- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **polish_disabled** (exterior views stay the Cycles render): negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: ok; left: unverified | yes |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok; right: ok | yes |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: ok; right: unverified | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | yes |
| ext_7 | aerial | - | - | cycles (gate_validation) | ok | right: unverified | yes |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_4 | corner | left, back | 12.5 m from the building corner, 30 degrees off the back facade: 81% of the view of the building is blocked by trees, the plot wall or another building; 14.5 m from the building corner, 30 degrees off the back facade: 75% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m from the building corner, 30 degrees off the back facade: 58% of the view of the building is blocked by trees, the plot wall or another building; 11.0 m from the building corner, 30 degrees off the back facade: 87% of the view of the building is blocked by trees, the plot wall or another building; 18.5 m from the building corner, 30 degrees off the back facade: 48% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m from the building corner, 30 degrees off the back facade: the building fills 6% of the frame (< 8%); 24.5 m from the building corner, 30 degrees off the back facade: 35% of the view of the building is blocked by trees, the plot wall or another building |
| ext_6 | frontal | back | 17.5 m in front of the back (entrance) facade: inside the copy; 19.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 16.0 m in front of the back (entrance) facade: inside the copy; 23.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 26.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 29.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | off white | fallback | yes | facade scheme (modern): render in off white (no drawing, brief or style names the facade) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | dark_bronze | - | style | no | style profile exterior.window_frame |
| door | wood_oak_light | - | fallback | yes | style profile exterior.door (assumed) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | agent | no | agent override (docs/milestone11.md §17.3) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | off white | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof mismatch.

Roof heights: built eaves 3,75 m, ridge 6,01 m; drawn eaves 3,75 m (vector), ridge 5,80 m (vector); result mismatch.

## Variants

One building per drawn alternative plan: the base and, for each alternative, the same building with that level replaced. An alternative renders only the rooms it changes, and its exterior views only when its outside differs (otherwise the base views stand for it). Each alternative has its own report in its sub-output (paths below, relative to the project output).

| variant | label | rooms changed | outside | interior views | polished / Cycles | mismatches | report |
|---|---|---|---|---|---|---|---|
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_koridor_2_2, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2 | 12 / 24 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_koridor_2 | 6 / 12 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| deneme1.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 19, block_name 44, group_member 5, inferred 9, level 2, nightstand_symbol 4, none 19, rule 52, same_block 1, twin 9. Recognition questions: 70; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

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
| f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | table_coffee | no (typed by twin) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |
| f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | bench | no (typed by none) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sideboard, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
| f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | table_coffee | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bookshelf 0.95; pass 2 zai-org/GLM-4.6V-Flash: console_table 0.90 |

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
- door height 1,01 m: 2 opening(s) (d_L1_004, d_L1_005)
- door height 1,71 m: 2 opening(s) (d_L1_003, d_L1_006)
- door height 1,80 m: 2 opening(s) (d_L1_001, d_L1_002)
- door height 2,10 m: 16 opening(s) (d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L0_001, d_L0_002 ...)
- opening height 2,10 m: 3 opening(s) (o_L0_001, o_L0_002, o_L1_001)
- window height 1,20 m: 2 opening(s) (win_L-1_003, win_L-1_004)
- window height 1,51 m: 2 opening(s) (win_L1_001, win_L1_002)
- window height 2,40 m: 2 opening(s) (win_L-1_001, win_L-1_002)
- window height 2,55 m: 4 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004)
- window sill height 0,20 m: 8 opening(s) (win_L-1_001, win_L-1_002, win_L0_001, win_L0_002, win_L0_003, win_L0_004 ...)
- window sill height 0,90 m: 2 opening(s) (win_L-1_003, win_L-1_004)
- f_L-1_019 (stair): direction, turn, void assumed (the plan of L0 draws the same stair (f_L0_001) with its landing at the east end: the half landing is there, 1.24 m deep)
- f_L-1_020 (stair): direction, turn, void assumed (the plan of L0 draws the same stair (f_L0_002) with its landing at the west end: the half landing is there, 1.19 m deep)
- f_L0_001 (stair): direction, turn, void assumed (the plan of L1 draws the same stair (f_L1_002) with its landing at the east end: the half landing is there, 1.24 m deep)
- f_L0_002 (stair): direction, turn, void assumed (the plan of L1 draws the same stair (f_L1_001) with its landing at the west end: the half landing is there, 1.19 m deep)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- roof covering: not drawn (the outside look decides, see below)
- outside look facade: render in off white (fallback: facade scheme (modern): render in off white (no drawing, brief or style names the facade))
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
- outside look door: wood_oak_light (fallback: style profile exterior.door (assumed))
- outside look paving: paving in grey (fallback: style profile exterior.paving (assumed))
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))
- outside look plot_wall: render in off white (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L-1_banyo: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo |
| area_light | 1 | r_L-1_banyo_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo_2 |
| area_light | 1 | r_L-1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor |
| area_light | 1 | r_L-1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor_2 |
| area_light | 1 | r_L-1_mutfak: agent: Add a warm layered light layer to the flat generic daylight (a:D3:r_L-1_mutfak).; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1_mutfak |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven_2 |
| area_light | 1 | r_L1_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo |
| area_light | 1 | r_L1_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo_2 |
| area_light | 1 | r_L1_banyo_2: room has no window; the room's light rig (1 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L1_banyo_2 |
| area_light | 1 | r_L1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor |
| area_light | 1 | r_L1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_koridor_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has no window; the room's light rig (1 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has no window; the room's light rig (1 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| area_light | 4 | r_L1_teras: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras, light_r_L1_teras_2, light_r_L1_teras_3 |
| area_light | 4 | r_L1_teras_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_teras_2.001, light_r_L1_teras_2_2, light_r_L1_teras_2_3 |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (+y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| balustrade | 4 | one continuous balustrade per open side with newels at its turns (not drawn: assumed; modern: plate structure, glass panels under a steel handrail, steel strings (glass channel language of the house)) | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| bank:sp_004:3 | 1 | sp_004 edge 3: a planted bank of 1:2 up to the ground 2.5 m out (the ground 0.78 m over the level; a landscape architect grades the ground to the terrace where it can, no retaining wall; inferred) | site |
| bedding | 2 | the bed model has no bedding (docs/milestone12.md §4.7): our cloth on its mattress | dress_f_L0_007, dress_f_L0_019 |
| car | 1 | library car 3dwh_867427c8bc03ecda3fbb809a ('CAR') on the drawn parking spk_001 (perpendicular bay; the documents draw the parking, not a car) | car_spk_001_0 |
| climate | 1 | the drawing's language (tr): the climate most of its houses stand in (a guess) (inferred; the species of trees and hedges follow it): banyo, merdiven, mutfak, otopark, yatak | site |
| context | 1 | no context drawn: 159 trees of the mediterranean climate (stone_pine 57, olive 43, cypress 35, plane 24; species inferred) in groups around the site, 89-350 m from the building's centre (the exterior cameras stand within 89 m), with open fields between them so the horizon stays in view (inferred context) | site |
| direction | 1 | the plan of L0 draws the same stair (f_L0_001) with its landing at the east end: the half landing is there, 1.24 m deep | furn_f_L-1_019 |
| direction | 1 | the plan of L0 draws the same stair (f_L0_002) with its landing at the west end: the half landing is there, 1.19 m deep | furn_f_L-1_020 |
| direction | 1 | the plan of L1 draws the same stair (f_L1_001) with its landing at the west end: the half landing is there, 1.19 m deep | furn_f_L0_002 |
| direction | 1 | the plan of L1 draws the same stair (f_L1_002) with its landing at the east end: the half landing is there, 1.24 m deep | furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 8 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1_003_handle, d_L-1_004_handle, d_L1_001_handle |
| door_handles | 1 | design detail of the documented entrance door (brushed_steel handles on both faces); not in the documents | d_L0_011_handle |
| door_hinge_side | 12 | the drawing gives no hinge side: the model's own hinge side (assumed) | d_L-1_001, d_L-1_002, d_L0_001 |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade | 1 | facade scheme (modern): render in off white (no drawing, brief or style names the facade) | exterior |
| facade_scheme | 1 | facade scheme (modern): stone_wall_ledgestone on the basement level L-1 (not drawn) | L-1 |
| facade_scheme | 1 | facade scheme (modern): wood_cladding framing the main entrance d_L0_011 (2.8 m wide; not drawn) | w_L0_007 |
| fascia_material | 1 | pitched roof: the eaves and verge edges are a fascia board in the gutter's aluminium_anthracite (not drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet) | roof |
| handrail | 4 | design detail on every stair side not against a wall; not in the documents | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| hedge | 1 | 30 tree symbols of radius 0.36 m at a pitch of 0.72 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_002 |
| hedge | 1 | 36 tree symbols of radius 0.36 m at a pitch of 0.73 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_001 |
| hedge | 2 | 7 tree symbols of radius 0.36 m at a pitch of 0.80 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn) | hedge_003, hedge_004 |
| hedge:hedge_001 | 1 | 36 tree symbols of radius 0.36 m at a pitch of 0.73 m in one row: a mid hedge 1.2 m high (height assumed; species not drawn); species cherry_laurel (inferred) | site |
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
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 8 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024, furn_f_L0_009 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 10 | window height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
| inside_sill | 10 | design detail of the documented window: an inside sill 0.1 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L-1_001_inside_sill, win_L-1_002_inside_sill, win_L-1_003_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:guard_glass | 1 | glass guard in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:railing | 1 | guard's metal (rails, posts, bars or a glass channel) in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| left_out:door | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the modern look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the modern look; hssd_3764-1: glazing bars (the audit): the modern look wants no or few bars; hssd_4076-9: glazing bars (the audit): the modern look wants no or few bars | openings |
| left_out:entrance | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the modern look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the modern look; hssd_3764-0: glazing bars (the audit): the modern look wants no or few bars; hssd_3764-1: glazing bars (the audit): the modern look wants no or few bars; hssd_4076-9: glazing bars (the audit): the modern look wants no or few bars | openings |
| left_out:inside_door:glazed | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_1f3c6cfcdfb2a7b701692f9d: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_31a4f763e80370fb618fd10d: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_3befa867f6b07c735086bba4: a sliding door for a swing door; 3dwh_4555ada4db4043a2400c0747: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_4d20a064a680662a23924bec: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_50f8fafc2604c495a8f2ff6f: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_54d07ce98f9345c95081fc1e: glass 0% of its face (< 15%): not a glazed leaf | openings |
| left_out:inside_door:solid | 1 | models out of the style's look: 3dwh_07b2214948fc287e2651d776: glass 100% of its face (> 8%): not a solid leaf; 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_3befa867f6b07c735086bba4: a sliding door for a swing door; 3dwh_4555ada4db4043a2400c0747: audited styles ['classic', 'modern']: mostly classic, not the modern look; 3dwh_779ae72d1a217f8a883b35b7: glass 15% of its face (> 8%): not a solid leaf; 3dwh_80ecf1763916b0e5e2bd9147: a panelled leaf: not the modern look; hssd_201-2: a panelled leaf: not the modern look; hssd_201-71: a panelled leaf: not the modern look | openings |
| left_out:terrace_door | 1 | models out of the style's look: 3dwh_5b8d6e9c0eff7893f9fe2795: patterned glass (an image on its glass): the modern look wants clear glass; hssd_3764-0: glazing bars (the audit): the modern look wants no or few bars; hssd_3764-1: glazing bars (the audit): the modern look wants no or few bars; hssd_4076-9: glazing bars (the audit): the modern look wants no or few bars; hssd_4141-3: glass 18% of its face (< 45%); hssd_4141-9: glass 18% of its face (< 45%) | openings |
| left_out:window | 1 | models out of the style's look: 3dwh_008fc2b4ab59c1a67589cb97: no see-through glass; 3dwh_16c5fdb11c4ec7d95492a04b: glazing bars (12 lites, 3.0 per m2): the modern look wants no or few bars; 3dwh_2a2ec61614b5278cf6fe1011: no see-through glass; 3dwh_48bec799740fad36241c99d9: no see-through glass; 3dwh_4a7dc5974d3b797601e64e12: audited styles ['classic', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_56f518dddfda5b3c284ddf47: no see-through glass; 3dwh_5c21a04d22581a3786ae9bef: no see-through glass; 3dwh_5faa67969eb7104b4adee381: its title says 'traditional': not the modern look | openings |
| level | 1 | parking spk_001: one level at +0.75 m (level marks lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred) | platform_spk_001 |
| level | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 1.06 m up), 5 (1 x 1.16 m down), 6 (1 x 1.16 m down), 7 (2 x 1.16 m down), 8 (2 x 1.16 m down), 9 (1 x 1.16 m down), 10 (1 x 1.16 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); a flight of 1 risers of 0.068 m, tread 0.45 m down 0.07 m from edge 4 to the ground at its foot (the count settled on the ground the last riser lands on); each tread a solid block on the one below, cheek walls holding the ground beside it, a landing at its foot, a hole in the lawn (inferred) | platform_sp_001 |
| level | 1 | terrace sp_001_s1e10: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.25..-3.94 m under it; edge: retaining (inferred) | platform_sp_001_s1e10 |
| level | 1 | terrace sp_001_s1e2: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 2.12 m over the level along its edge 2, more than the 1.2 m retaining cap); ground -2.01..-0.88 m under it; edge: retaining (inferred) | platform_sp_001_s1e2 |
| level | 1 | terrace sp_001_s1e3: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 1.22 m over the level along its edge 3, more than the 1.2 m retaining cap); ground -2.91..-1.78 m under it; edge: retaining (inferred) | platform_sp_001_s1e3 |
| level | 1 | terrace sp_001_s1e5: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.31 m under the level along its edge 5, more than the 1.2 m retaining cap); ground -4.31..-3.42 m under it; edge: retaining (inferred) | platform_sp_001_s1e5 |
| level | 1 | terrace sp_001_s1e6: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.81 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -4.81..-3.92 m under it; edge: retaining (inferred) | platform_sp_001_s1e6 |
| level | 1 | terrace sp_001_s1e7: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.52..-4.42 m under it; edge: retaining (inferred) | platform_sp_001_s1e7 |
| level | 1 | terrace sp_001_s1e8: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.52..-4.54 m under it; edge: retaining (inferred) | platform_sp_001_s1e8 |
| level | 1 | terrace sp_001_s1e9: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.25..-4.54 m under it; edge: retaining (inferred) | platform_sp_001_s1e9 |
| level | 1 | terrace sp_001_s2e7: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.92..-4.81 m under it; edge: retaining (inferred) | platform_sp_001_s2e7 |
| level | 1 | terrace sp_001_s2e8: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.92..-5.14 m under it; edge: retaining (inferred) | platform_sp_001_s2e8 |
| level | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 5 steps up out of it on edge 0 (0.70 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0) | platform_sp_002 |
| level | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | platform_sp_002_s1e4 |
| level | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred) | platform_sp_002_s1e5 |
| level | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | platform_sp_002_s2e4 |
| level | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | platform_sp_002_s2e5 |
| level | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 5 steps up out of it on edge 0 (0.79 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | platform_sp_003 |
| level | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); sp_004 edge 3: a planted bank of 1:2 up to the ground 2.5 m out (the ground 0.78 m over the level; a landscape architect grades the ground to the terrace where it can, no retaining wall; inferred) | platform_sp_004 |
| level | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | platform_sp_004_s1e11 |
| level | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | platform_sp_004_s1e6 |
| level | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | platform_sp_004_s1e7 |
| level | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | platform_sp_004_s1e8 |
| level | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | platform_sp_004_s2e7 |
| library_model | 1 | library door 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.82 x 2.10 m (proportions off by 12 %; the documents draw the opening, not its product); the building's one door family; another family than the entrance's; modern look: audited styles ['modern'] name modern; frames in the style's finish | d_L0_012 |
| library_model | 2 | library inside door 3dwh_31a4f763e80370fb618fd10d ('bathroom door') in 1 panel(s) of 0.78 x 2.10 m (proportions off by 19 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L0_006, d_L0_010 |
| library_model | 10 | library inside door 3dwh_31a4f763e80370fb618fd10d ('bathroom door') in 1 panel(s) of 0.82 x 2.10 m (proportions off by 12 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_001, d_L-1_002, d_L0_001 |
| light_well:win_L-1_002 | 1 | window sill -2.80 m, ground outside -2.83 m: an open concrete light well 0.8 m deep, 7.59 m wide (no light well drawn) | site |
| light_well:win_L-1_003 | 1 | the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well | site |
| light_well:win_L-1_004 | 1 | the terrace sp_002 at -3.00 m lies under the sill -2.10 m: no light well | site |
| modules | 19 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| opening_model | 2 | no model of the house's solid inside door family 'bathroom door' fits 0.82 x 1.01 m: the parametric door keeps the house's door language | d_L1_004, d_L1_005 |
| parapet | 1 | roof terrace ro_001: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| parapet_height:ro_002 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| path:d_L0_011 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path:d_L0_012 | 1 | a paved path from the plot edge to the entrance (inferred) | site |
| path_grading | 1 | a stepped path: 18 % along is steeper than 1:12, so 7 risers of 0.132 m in 3 flight(s) (3/2/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_sp_004_0 |
| path_grading | 1 | a stepped path: 19 % along is steeper than 1:12, so 5 risers of 0.132 m in 2 flight(s) (3/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_sp_001_0 |
| path_grading | 1 | a stepped path: 25 % along is steeper than 1:12, so 16 risers of 0.143 m in 4 flight(s) (4/4/4/4) with level landings, treads 0.35 m, level across, stone step edges; a handrail on the flights over 0.45 m (inferred) | path_access_sp_004_1 |
| path_grading | 1 | a stepped path: 31 % along is steeper than 1:12, so 24 risers of 0.147 m in 8 flight(s) (3/3/3/3/3/3/3/3) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_012 |
| path_grading | 1 | a stepped path: 34 % along is steeper than 1:12, so 24 risers of 0.144 m in 8 flight(s) (3/3/3/3/3/3/3/3) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_011 |
| path_grading | 1 | a stepped path: 37 % along is steeper than 1:12, so 17 risers of 0.145 m in 4 flight(s) (5/4/4/4) with level landings, treads 0.35 m, level across, stone step edges; a handrail on the flights over 0.45 m (inferred) | path_access_sp_001_1 |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| plant:sp_001_s1e10_plant1 | 1 | planted terrace sp_001_s1e10: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e2_plant1 | 1 | planted terrace sp_001_s1e2: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e3_plant1 | 1 | planted terrace sp_001_s1e3: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e5_plant1 | 1 | planted terrace sp_001_s1e5: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e5_plant2 | 1 | planted terrace sp_001_s1e5: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e6_plant1 | 1 | planted terrace sp_001_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e6_plant2 | 1 | planted terrace sp_001_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e7_plant1 | 1 | planted terrace sp_001_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e7_plant2 | 1 | planted terrace sp_001_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s1e8_plant2 | 1 | planted terrace sp_001_s1e8: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s2e7_plant1 | 1 | planted terrace sp_001_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s2e7_plant2 | 1 | planted terrace sp_001_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s2e7_plant3 | 1 | planted terrace sp_001_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_001_s2e8_plant1 | 1 | planted terrace sp_001_s2e8: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_002_s1e4_plant1 | 1 | planted terrace sp_002_s1e4: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_002_s1e5_plant1 | 1 | planted terrace sp_002_s1e5: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_002_s2e4_plant1 | 1 | planted terrace sp_002_s2e4: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_002_s2e5_plant1 | 1 | planted terrace sp_002_s2e5: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_bank0_plant1 | 1 | planted bank sp_004_bank0: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e11_plant1 | 1 | planted terrace sp_004_s1e11: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e6_plant1 | 1 | planted terrace sp_004_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e6_plant2 | 1 | planted terrace sp_004_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e7_plant1 | 1 | planted terrace sp_004_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e7_plant2 | 1 | planted terrace sp_004_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e8_plant1 | 1 | planted terrace sp_004_s1e8: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant1 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant2 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant3 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| platform:sp_001 | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 1.06 m up), 5 (1 x 1.16 m down), 6 (1 x 1.16 m down), 7 (2 x 1.16 m down), 8 (2 x 1.16 m down), 9 (1 x 1.16 m down), 10 (1 x 1.16 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); a flight of 1 risers of 0.068 m, tread 0.45 m down 0.07 m from edge 4 to the ground at its foot (the count settled on the ground the last riser lands on); each tread a solid block on the one below, cheek walls holding the ground beside it, a landing at its foot, a hole in the lawn (inferred) | site |
| platform:sp_001_s1e10 | 1 | terrace sp_001_s1e10: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.25..-3.94 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e2 | 1 | terrace sp_001_s1e2: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 2.12 m over the level along its edge 2, more than the 1.2 m retaining cap); ground -2.01..-0.88 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e3 | 1 | terrace sp_001_s1e3: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 1.22 m over the level along its edge 3, more than the 1.2 m retaining cap); ground -2.91..-1.78 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e5 | 1 | terrace sp_001_s1e5: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.31 m under the level along its edge 5, more than the 1.2 m retaining cap); ground -4.31..-3.42 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e6 | 1 | terrace sp_001_s1e6: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.81 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -4.81..-3.92 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e7 | 1 | terrace sp_001_s1e7: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.52..-4.42 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e8 | 1 | terrace sp_001_s1e8: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.52..-4.54 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e9 | 1 | terrace sp_001_s1e9: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.25..-4.54 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e7 | 1 | terrace sp_001_s2e7: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.92..-4.81 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e8 | 1 | terrace sp_001_s2e8: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.92..-5.14 m under it; edge: retaining (inferred) | site |
| platform:sp_002 | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 5 steps up out of it on edge 0 (0.70 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0) | site |
| platform:sp_002_s1e4 | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s1e5 | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s2e4 | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s2e5 | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | site |
| platform:sp_003 | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 5 steps up out of it on edge 0 (0.79 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | site |
| platform:sp_004 | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); sp_004 edge 3: a planted bank of 1:2 up to the ground 2.5 m out (the ground 0.78 m over the level; a landscape architect grades the ground to the terrace where it can, no retaining wall; inferred) | site |
| platform:sp_004_s1e11 | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e6 | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e7 | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e8 | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s2e7 | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | site |
| platform:spk_001 | 1 | parking spk_001: one level at +0.75 m (level marks lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred) | site |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: stone_wall_ledgestone (style family modern; not drawn) | facade |
| pool:pool_001:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_002:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_003:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_004:depth | 1 | no pool section drawn: the depth is assumed | site |
| ridge_caps | 1 | ridge and hip caps along the roof's ridges and hips (not drawn; a tiled roof has them) | roof_ridges |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_021 (no nightstand, no lamp): the wall sconce would cover the window win_arch_r_L0_yatak_odasi_3_1 | rig_r_L0_yatak_odasi_3 |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_022 (no nightstand, no lamp): the wall sconce would cover the window win_arch_r_L0_yatak_odasi_4_1 | rig_r_L0_yatak_odasi_4 |
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_045; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_057; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor: ceiling fixture at the pole of inaccessibility of r_L-1_koridor, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_061); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L-1_koridor_2, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_055); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_091 over the counter f_L-1_001; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_1_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/4 of its light under each decor ceiling light of the room (dec_L-1_034); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/4 of its light under each decor ceiling light of the room (dec_L-1_052); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/4 of its light under each decor ceiling light of the room (dec_L-1_053); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_6_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/4 of its light under each decor ceiling light of the room (dec_L-1_054); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_7_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_097 over the counter f_L-1_010; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/4 of its light under each decor ceiling light of the room (dec_L-1_062); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/4 of its light under each decor ceiling light of the room (dec_L-1_069); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/4 of its light under each decor ceiling light of the room (dec_L-1_070); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_6_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/4 of its light under each decor ceiling light of the room (dec_L-1_071); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_7_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_046); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_047); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_2_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_048); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_3_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_049); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_4_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_104); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_105); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_2_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_106); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_3_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_107); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_4_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_036; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_042; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_041 (top 1.95 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_024; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside light in the shade of the table lamp dec_L0_013 on f_L0_031 beside the bed f_L0_007; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_018); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_047 on f_L0_033 beside the bed f_L0_008; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_052); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_007 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the curtain dec_L0_002); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_064 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the books dec_L0_066); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_031 on f_L0_043 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_072 on f_L0_046 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_020); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_025); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_009; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_034; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
| rig_mirror | 1 | mirror light over the washbasin f_L-1_025: the mirror dec_L-1_056 reaches 2.75 m and the ceiling is at 2.85 m, so the bar would cross it | rig_r_L-1_banyo_2 |
| rig_mirror | 1 | mirror light over the washbasin f_L-1_026: the mirror dec_L-1_044 reaches 2.75 m and the ceiling is at 2.85 m, so the bar would cross it | rig_r_L-1_banyo |
| rig_mirror | 1 | mirror light over the washbasin f_L0_003: the mirror dec_L0_035 reaches 2.90 m and the ceiling is at 3.00 m, so the bar would cross it | rig_r_L0_banyo |
| rig_mirror | 1 | mirror light over the washbasin f_L0_004: the mirror dec_L0_025 reaches 2.90 m and the ceiling is at 3.00 m, so the bar would cross it | rig_r_L0_e_banyo_2 |
| rig_mirror | 1 | mirror light over the washbasin f_L0_006: the mirror dec_L0_023 reaches 2.90 m and the ceiling is at 3.00 m, so the bar would cross it | rig_r_L0_e_banyo |
| rig_mirror | 1 | mirror light over the washbasin f_L1_015: the mirror dec_L1_016 reaches 1.76 m and the ceiling is at 1.78 m, so the bar would cross it | rig_r_L1_banyo |
| rig_strip | 1 | LED strip under the wall cabinet f_L-1_092 over the counter f_L-1_002: crosses kitchen_counter f_L-1_002 | rig_r_L-1_mutfak |
| rig_strip | 1 | LED strip under the wall cabinet f_L-1_093 over the counter f_L-1_002: crosses kitchen_counter f_L-1_002 | rig_r_L-1_mutfak |
| rig_strip | 1 | LED strip under the wall cabinet f_L-1_098 over the counter f_L-1_011: crosses kitchen_counter f_L-1_011 | rig_r_L-1_mutfak_2 |
| rig_strip | 1 | LED strip under the wall cabinet f_L-1_099 over the counter f_L-1_011: crosses kitchen_counter f_L-1_011 | rig_r_L-1_mutfak_2 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L-1_019, furn_f_L-1_020 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.150 m / 18 drawn risers | furn_f_L0_001, furn_f_L0_002 |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 2 | outside sill 2.2285 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill, win_L0_003_sill |
| sill | 2 | outside sill 2.743 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_arch_r_L0_yatak_odasi_3_1_sill, win_arch_r_L0_yatak_odasi_4_1_sill |
| sill | 2 | outside sill 2.7431 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill, win_L0_004_sill |
| sill | 2 | outside sill 4.2173 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_003_sill, win_L-1_004_sill |
| sill | 2 | outside sill 7.2461 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_001_sill, win_L-1_002_sill |
| sill_height | 10 | window sill_height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 20 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1_salon, skirting_r_L-1_salon_2, skirting_r_L-1_mutfak |
| slab_band | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_001, f_L-1_002, f_L-1_004, f_L-1_008 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L-1_003 | splashback_r_L-1_mutfak |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_010, f_L-1_011, f_L-1_013, f_L-1_017 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L-1_004 | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_003 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_004 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_012 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_013 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_067 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_068 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak_2 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_002 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_002 (100% of the smaller footprint; slab opening sv_L1_002); read as its upper end, not built as a second flight | f_L1_001 |
| suspension | 12 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L-1_046_cord, decor_dec_L-1_047_cord, decor_dec_L-1_048_cord |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| terrace_railing | 1 | roof terrace ro_001: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_001 |
| terrace_railing | 1 | roof terrace ro_002: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_002 |
| tree | 28 | bush of the drawn size, 0.8 m tall (height assumed) | tree_sp_004_bank0_plant1, tree_sp_001_s1e2_plant1, tree_sp_001_s1e3_plant1 |
| tree | 21 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 1 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001, furn_f_L0_002 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 5 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L-1_019, furn_f_L-1_020 |
| void_guard | 1 | floor opening 0 of L0 (f_L-1_019 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.53 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L0_0 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.37 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| void_guard | 1 | floor opening 1 of L0 (f_L-1_020 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L0_1 |
| void_guard | 1 | floor opening 1 of L1 (f_L0_002 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_1 |
| waist | 4 | the house's style (modern: plate structure, glass panels under a steel handrail, steel strings (glass channel language of the house)); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| winders | 4 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L-1_mutfak | cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3 | cam_r_L-1_mutfak_1 (vision_check) | ok |
| r_L1_koridor | cam_r_L1_koridor_2 | cam_r_L1_koridor_1 (vision_check) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_salon (rung None), r_L0_e_yatak_odasi (rung None), r_L0_yatak_odasi (rung None), r_L0_yatak_odasi_3 (rung None), r_L1_oyun_aktivite_ve_dinlenme_odasi (rung None), r_L1_teras (rung None).

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4146a4ba279f8c3a7cea9c4e [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial], 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_a6cc115440aa25caec12b416 [non_commercial], 3dwh_a9d28630641767154cebf661 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_dad0bbfc0250ff575c5bc83b [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_scandinavian_5_c7cc94ed [tool_nc], gen_potted_plant_modern_minimal_1_6b4ad5f1 [tool_nc], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_051e7613c71593d5d91bac3b3d03a36e51dd0c23 [non_commercial], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial], hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial], hssd_a72d7403a0ea8133a89bff0bfc266d443613420a [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial], hssd_f1472cfab8e5e70a0112813a8379743200bf5347 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial], hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_koridor_2_2: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: yes
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: gen_potted_plant_modern_minimal_1_6b4ad5f1 [tool_nc])
- cam_r_L-1_mutfak_3: commercial-safe: yes
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_051e7613c71593d5d91bac3b3d03a36e51dd0c23 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_a6cc115440aa25caec12b416 [non_commercial], 3dwh_a9d28630641767154cebf661 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_a6cc115440aa25caec12b416 [non_commercial], 3dwh_a9d28630641767154cebf661 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_a72d7403a0ea8133a89bff0bfc266d443613420a [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial])
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_4146a4ba279f8c3a7cea9c4e [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_25468a5fe0e85110daefcb0f [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_4146a4ba279f8c3a7cea9c4e [non_commercial], 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial])
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_f1472cfab8e5e70a0112813a8379743200bf5347 [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_f1472cfab8e5e70a0112813a8379743200bf5347 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: 3dwh_4736e8ccac82f4d690680828 [non_commercial], 3dwh_4799895b90ee49a1f4cd032a [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_5_c7cc94ed [tool_nc])
- cam_r_L1_koridor_2: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_5_c7cc94ed [tool_nc])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_dad0bbfc0250ff575c5bc83b [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_7025cd14a948f491902ef12724f0fe6e4ce672af [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial])
- cam_r_L1_teras_1: commercial-safe: yes
- cam_r_L1_teras_2: commercial-safe: yes
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: yes
- ext_7: commercial-safe: yes

## Built below library level (Milestone 13)

34 furniture piece(s) built from a module builder or a parametric family instead of a library model: 6 library gap(s) to close with a real model, 28 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

| id | type | method | builder | room | room type | source | gap | used |
|---|---|---|---|---|---|---|---|---|
| f_L-1_001 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_002 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_003 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_004 | kitchen_counter | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_008 | stove | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_010 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_011 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_012 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_013 | kitchen_counter | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_017 | stove | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_019 | stair | parametric | parametric:stair | r_L-1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L-1_020 | stair | parametric | parametric:stair | r_L-1_koridor | hall | from_documents | no (by design) | - |
| f_L-1_027 | table_dining | module | table_long | r_L-1_salon | living | from_documents | yes | module builder table_long (3 module(s): dining table 3.35 x 1.00 m on trestles) |
| f_L-1_038 | table_dining | module | table_long | r_L-1_salon_2 | living | from_documents | yes | module builder table_long (3 module(s): dining table 3.35 x 1.00 m on trestles) |
| f_L-1_067 | sink_kitchen | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_068 | sink_kitchen | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L0_001 | stair | parametric | parametric:stair | r_L0_merdiven | hall | from_documents | no (by design) | - |
| f_L0_002 | stair | parametric | parametric:stair | r_L0_merdiven_2 | hall | from_documents | no (by design) | - |
| f_L0_013 | shower | parametric | parametric:shower | r_L0_e_banyo | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L0_014 | shower | parametric | parametric:shower | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | our parametric fixture (by design) |
| f_L0_023 | wardrobe | module | wardrobe_run | r_L0_e_yatak_odasi | bedroom | from_documents | yes | module builder wardrobe_run (7 module(s): PAX frame 100x58x202 cm) |
| f_L0_024 | wardrobe | module | wardrobe_run | r_L0_e_yatak_odasi_2 | bedroom | from_documents | yes | module builder wardrobe_run (7 module(s): PAX frame 100x58x202 cm) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_koridor_2 | stair | from_documents | no (by design) | - |
| f_L1_002 | stair | parametric | parametric:stair | r_L1_koridor | hall | from_documents | no (by design) | - |
| f_L1_043 | table_dining | parametric | parametric:table_dining | r_L1_teras_2 | balcony | added_by_ai | yes | parametric family in weather-proof materials (a teak top on brushed steel legs) |
| f_L-1_090 | fridge | module | kitchen_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_091 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_092 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_093 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_096 | fridge | module | kitchen_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_097 | wall_cabinet | module | wall_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_098 | wall_cabinet | module | wall_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_099 | wall_cabinet | module | wall_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L1_070 | table_dining | module | table_long | r_L1_teras | balcony | added_by_ai | yes | module family in weather-proof materials (a teak top on brushed steel legs) |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_1 (6.0 degrees off the sun, sky pull k 3), ext_5 (5.6 degrees off the sun, sky pull k 0).

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
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (70 of 70 answered); sheets/requests.json (8 of 8 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (70 of 70 answered); sheets/requests.json (8 of 8 answered) |

Assets: textures CC0 x 25; furniture/decor models 3DWH-UNREVIEWED x 85, CC-BY-4.0 x 126, CC-BY-NC-4.0 x 49, CC0 x 3, generated (Infinigen v1.19.0, BSD-3-Clause) x 3, generated (TRELLIS.2-4B, MIT) x 24 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "IKEA FLÅDIS Seagrass basket - iPhone 3d scan" by Jacek Jaskólski (https://sketchfab.com/3d-models/2cd59181404c4aaa995a0ea55f89e212), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L1_022)
- "Candles" by rhcreations (https://sketchfab.com/3d-models/4058a3ed739e4f9f89f49323c7db4b4c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L0_019)
- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1_100)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L1_037)
- "Bread In Basket" by InReality Solutions (https://sketchfab.com/3d-models/be0b7e93e66a4d4c84c2d0a13fe1852a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L1_017)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1_004)
- "Candle" by deniska40k (https://sketchfab.com/3d-models/c408586d8c1547448c4ff47abb4fb981), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L-1_033)
- "Доработка дно пирожницы h=23 l=75 без рёбер" by Александр (https://sketchfab.com/3d-models/e736a1e7cdcb48a5a4f2ca4100d52d28), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L1_011, dec_L1_036)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L-1_banyo_1 | calibrated | yes | no | - |
| cam_r_L-1_banyo_2 | calibrated | yes | no | - |
| cam_r_L-1_koridor_2_1 | calibrated | yes | no | - |
| cam_r_L-1_koridor_2_2 | calibrated | yes | no | - |
| cam_r_L-1_mutfak_1 | calibrated | yes | yes | door [901.8, 474.1, 985.2, 775.5] (score) |
| cam_r_L-1_mutfak_2 | calibrated | yes | no | - |
| cam_r_L-1_mutfak_3 | calibrated | yes | no | - |
| cam_r_L0_banyo_1 | calibrated | yes | no | - |
| cam_r_L0_banyo_2 | calibrated | yes | no | - |
| cam_r_L0_e_banyo_1 | calibrated | yes | no | - |
| cam_r_L0_koridor_1 | calibrated | yes | no | - |
| cam_r_L1_banyo_1 | calibrated | yes | no | - |
| cam_r_L1_koridor_1 | calibrated | yes | yes | furniture [1099.8, 916.0, 1447.9, 960.6] (score); window [1066.9, 619.8, 1456.4, 963.2] (vlm:agent); door [1066.9, 619.8, 1456.4, 963.2] (vlm:agent) |
| cam_r_L1_koridor_2 | calibrated | yes | no | - |

## Stages

This run (`20261028-183611-full-20261028T184049Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 50.7 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 110.3 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.5 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.7 min | answers applied |
| fit | ok | 19.2 s | - |
| layout | ok | 45.0 s | - |
| decor_ask | ok | 111.7 s | - |
| photos | reused | 0.2 s | - |
| assets | ok | 2.6 s | - |
| decor | ok | 8.5 s | - |
| agent_apply | ok | 60.5 s | - |
| refit | ok | 2.1 min | - |
| build | ok | 51.3 min | - |
| agent_previews | ok | 7.4 min | 36 view(s) |
| agent | ok | 68.4 min | 4 round(s), 27 finding(s) removed by 89 accepted edit(s) (measured; 168 predicted by the dry re-checks), 24 new, net 3, 292 rejected; stop: max rounds reached; final round for critical findings not started (time budget) |
| render | ok | 9.7 min | - |
| export | ok | 6.5 min | - |
| controls | ok | 2.1 min | - |
| gate | ok | 3.7 min | gate decision ok |
| polish | ok | 8.8 min | - |
| detect | ok | 16.4 s | - |
| expected | ok | 3.4 min | - |
| check | ok | 6.4 min | - |
| combine | ok | 29.6 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 5 round(s), 89 edit(s) accepted, 292 rejected, 636 model calls (8428245 tokens), 76.8 min. Stop: time budget: the final stages need the time left before the deadline - 20 min. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 14833): earlier runs of the appended log are left out (14832 events, 5553 model calls, 446 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 89 / 292 (23 % accepted) |
| rejected by reason | acceptance 63, memory 29, no_change 26, asset_unusable 25, max_tries 16 |
| rooms checked by code / vision / planner | 38 / 14 / 26 |
| rooms with fixable critical or major findings visited | 26 of 26 |
| critical before -> after (after: round 4's critics, before its 6 accepted edit(s)) | 8 -> 12 |
| major before -> after (after: round 4's critics, before its 6 accepted edit(s)) | 272 -> 429 |
| agent minutes; first accepted edit after | 62.73; 15.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 29; 54; 74 (44) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 27 measured; 168 predicted (the last round's dry re-checks predicted 23 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 59 new; net -32 |
| edits removing their finding | 11 of 55 |
| plans ok / empty / refused / default | 44 / 27 / 3 / 0 |

### What the AI inspector saw on the final renders

43 vision finding(s) (2 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 0 fixed in the final round, 5 handed to the stage that owns them, 114 open; the architect leaves 0 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`. The final round did not start (time): these are the last round's findings on the previews.

Still open or handed on (critical and major):

- major F9 f_L-1_093: The shoe cabinet is rendered as a crude, low-poly grey block with a repetitive grid pattern, lacking realistic material or detail. (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- critical Q3 f_L-1_019: The staircase has no safety railing or guard on the open side, creating a fall risk. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical D2 f_L0_023: The object labeled as a wardrobe (f_L0_023) is rendered as a dark, flat wall panel with a window frame embedded in it, rather than a functio (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- critical Q3 r_L0_koridor: The stair opening on the right side of the corridor lacks a safety railing or guard, creating a fall risk. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- major D2 f_L0_015: The toilet model is a crude, low-poly white box with a simple button, lacking the realistic shape and details of a standard toilet cistern. (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D2 f_L0_006: The washbasin is a crude, low-poly model with a flat, unrefined surface and a simple rectangular basin, lacking the typical curved shape of  (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major C7 f_L-1_075: Argus: drawn piece f_L-1_075 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C7 f_L-1_076: Argus: drawn piece f_L-1_076 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C7 f_L-1_077: Argus: drawn piece f_L-1_077 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C7 f_L-1_078: Argus: drawn piece f_L-1_078 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_045: Argus: f_L-1b_045 (sofa) of the final stage is gone after the build stage, named in conflicts[51].element_ids[0]: f_L-1b_045 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_046: Argus: f_L-1b_046 (sofa) of the final stage is gone after the build stage, named in conflicts[51].resolution: typed sofa by code (not kitche (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_047: Argus: f_L-1b_047 (floor_lamp) of the final stage is gone after the build stage, named in conflicts[53].element_ids[0]: f_L-1b_047 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_049: Argus: f_L-1b_049 (floor_lamp) of the final stage is gone after the build stage, named in conflicts[54].element_ids[0]: f_L-1b_049 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_056: Argus: f_L-1b_056 (sink_kitchen) of the final stage is gone after the build stage, named in conflicts[40].element_ids[0]: f_L-1b_056 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_057: Argus: f_L-1b_057 (unknown) of the final stage is gone after the build stage, named in conflicts[55].element_ids[0]: f_L-1b_057 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_058: Argus: f_L-1b_058 (unknown) of the final stage is gone after the build stage, named in conflicts[56].element_ids[0]: f_L-1b_058 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_061: Argus: f_L-1b_061 (sink_kitchen) of the final stage is gone after the build stage, named in conflicts[41].element_ids[0]: f_L-1b_061 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C1 f_L-1b_062: Argus: f_L-1b_062 (sink_kitchen) of the final stage is gone after the build stage, named in conflicts[42].element_ids[0]: f_L-1b_062 (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major AI1 r_L1_oyun_aktivite_ve_dinlenme_odasi: Argus: The L1 room 'Oyun Aktivite Ve Dinlenme Odasi' (40.5 m2) is typed 'other' and furnished as a living room (sofa, armchairs, coffee tabl (open: a tool exists (set_room_type) but no edit was accepted)
- major AI1 r_L1_oyun_aktivite_ve_dinlenme_odasi_2: Argus: Same issue as the twin room: typed 'other' with a living-room furniture set. Should be 'living'. (open: a tool exists (set_room_type) but no edit was accepted)
- major C7 f_L-1_057: Argus: drawn piece f_L-1_057 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C7 f_L-1_059: Argus: drawn piece f_L-1_059 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C7 f_L-1_064: Argus: drawn piece f_L-1_064 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major C7 f_L-1_066: Argus: drawn piece f_L-1_066 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)

### Argus, the auditor

Score 3.5 / 100 (100 = nothing open): 41 critical, 302 major, 113 minor open. By kind (critical + major): lost 138, no_sense 19, detached 9, taste 68, misread 25, geometry 50, silent 11, other 10, process 6, stale 6, untyped 1. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- lost w_L-1b_001: wall w_L-1b_001 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_002: wall w_L-1b_002 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_003: wall w_L-1b_003 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_004: wall w_L-1b_004 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_005: wall w_L-1b_005 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_006: wall w_L-1b_006 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_007: wall w_L-1b_007 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_008: wall w_L-1b_008 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_009: wall w_L-1b_009 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_010: wall w_L-1b_010 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_011: wall w_L-1b_011 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_012: wall w_L-1b_012 (None) of the final stage is missing after the build stage and nothing there names it
- lost w_L-1b_013: wall w_L-1b_013 (None) of the final stage is missing after the build stage and nothing there names it
- lost d_L-1b_001: opening d_L-1b_001 (door) of the final stage is missing after the build stage and nothing there names it
- lost d_L-1b_002: opening d_L-1b_002 (door) of the final stage is missing after the build stage and nothing there names it
- lost d_L-1b_003: opening d_L-1b_003 (door) of the final stage is missing after the build stage and nothing there names it
- lost d_L-1b_004: opening d_L-1b_004 (door) of the final stage is missing after the build stage and nothing there names it
- lost win_L-1b_001: opening win_L-1b_001 (window) of the final stage is missing after the build stage and nothing there names it
- lost win_L-1b_002: opening win_L-1b_002 (window) of the final stage is missing after the build stage and nothing there names it
- lost o_L-1b_001: opening o_L-1b_001 (opening) of the final stage is missing after the build stage and nothing there names it
- lost o_L-1b_002: opening o_L-1b_002 (opening) of the final stage is missing after the build stage and nothing there names it
- lost sa_L0_otopark_alani: the documents label a site area 'Otopark alani' and the model does not build it (no outline, no reason)
- lost sa_L0_guneslenme_alani: the documents label a site area 'Güneşlenme alani' and the model does not build it (no outline, no reason)
- lost sa_L0_24m2_havuz: the documents label a site area '24m2 havuz' and the model does not build it (no outline, no reason)
- no_sense dec_L1_013: decor_dec_L1_013 pokes through the roof (top 5.32 m)

Library gaps reported by the agent: stove (The stove is built into the counter run (hob in worktop, oven below); no library model may replace it, so the crude low-poly look (a:F265, a:F286) stays for review.), kitchen_counter (f_L-1_003 is a module of the code-designed kitchen run with its top at 1.18 m (a:F234); no library model replaces a run module, so the height finding stays for review.), sink_kitchen (No audited library sink model passes the fit rules for the drawn 0.79x0.50 m sink, so the bright blue model (a:F289) stays for review.), kitchen_counter (F235: f_L-1_012 top at 1.18 m over working height 0.97 m; the kitchen_counter catalogue is empty (0 models), so no audited model can replace the too-tall module build.), shoe_cabinet modern minimal (No audited shoe_cabinet model passes the fit rules (caps, height) for the 0.6 x 0.25 m, 1.0 m tall piece: three real models (0.5x0.23x1.79, 0.8x0.4x1.0, 0.75x0.25x1.28) were all pin_refused, so the crude placeholder model stays.), hall (The hall lacks the warm layered lighting layer (chandelier, wall sconces) seen in the reference; no library model provides it, so the D3 warm-light finding stays for review.), wall_art modern (The room is missing wall art and has a broken sunburst fixture that clashes with the modern style; no audited library model for integrated wall art/decor exists for this bathroom.), washbasin modern minimal (All audited washbasin models matching the drawn 1.0x0.55m footprint were audit-removed; no usable sleek integrated sink model exists in the library for this piece.), potted_plant (Potted plant f_L1_042 is a crude low-poly placeholder; no audited library model of a real potted plant exists (a:F449).), dining_table modern (Dining table f_L1_039 is a dated traditional turned-leg model that does not fit the modern balcony; no audited modern dining table model exists (a:F273, a:F338).), chair modern (Chair f_L1_041 is an all-black model clashing with the set; no audited modern chair model exists (a:F451, a:F339).), chair modern (Chair f_L1_040 is plain black molded plastic clashing with the traditional table; no audited modern chair model exists (a:F337).), washbasin modern (Argus flags the washbasin model as a style clash against the modern reference; the only real product of the type (3dwh_4736e8ccac82f4d690680828) is already in use and the alternative real model was audit-removed, so no audited modern model exists to swap to.), toilet modern (Argus flags the toilet as a basic unstyled white box clashing with the reference; both generated candidates were audit-removed and no other real product is available, so the library gap is recorded for review.), shower (No audited real-product shower model fits the drawn 0.60 x 1.40 m footprint (closest hssd_9368052ddb2713527a9be87ab3483ffd1f2c2a65 at 52.5% non-uniform scale, mean 0.7473; relaxed caps also fail), so the parametric build is by design and the F2/P7 findings stay for review.), wardrobe (Wardrobe f_L0_023 is a module build (wardrobe_run) with no audited library model within tolerance; all swap_model candidates were rejected (lower quality or audit-removed), so the module build is kept and the gap is recorded for review.), nightstand (Nightstand f_L0_031's current model (abo_B07DVRLW48, rated 4.0) is the best available; every swap candidate in memory was rejected as lower quality (3.0), so the style mismatch and visibility findings stay open due to library constraints.), nightstand (Nightstand f_L0_032's current model (abo_B07DVRLW48, rated 4.0) is the best available; every swap candidate in memory was rejected as lower quality (3.0), so the style mismatch and visibility findings stay open due to library constraints.), curtain (Room flagged for missing curtains (a:D3:r_L0_yatak_odasi_3); no curtain model exists in the library to add the soft layering the reference shows.), potted_plant (a:F449: the potted plant is a crude low-poly placeholder; no audited library model of a real potted plant exists.), dining_table modern (a:F273: the dining table is a dated traditional turned-leg model that does not fit the modern balcony; no audited modern dining table model exists.), chair modern (a:F451: the all-black chair clashes with the set; no audited modern chair model exists to replace it.), washbasin modern minimal (All three candidate washbasin models were audit-removed and fix_fixture found no valid spot; no usable library model remains for the generic floating-box sink (a:F441).), bathtub modern (The accepted round-1 model still reads as a plain untextured block and the round-3 swap candidate was audit-removed; no further usable bathtub model remains (a:F440).), wall_art modern (Room-level D3 flags a broken sunburst fixture / missing wall-art layer with no corresponding piece to swap; the decorative layer has no audited library model (a:D3:r_L-1_banyo).), washbasin modern (No audited modern washbasin model exists that reads as a bathroom basin; the current real model is the best available and all generated/other candidates were rejected.), toilet modern (No audited modern toilet model is usable; all generated and objaverse candidates were rejected as audit-removed, leaving the basic white box as the only available model.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 8 | 272 | 84 | 36 | 31 | 123 | layout | 20 |
| 2 | 7 | 256 | 80 | 36 | 24 | 63 | layout | 20 |
| 3 | 7 | 264 | 80 | 36 | 28 | 82 | layout | 37 |
| 4 | 12 | 429 | 131 | 60 | 6 | 24 | refit | 10 |
| 6 | 0 | 0 | 0 | 0 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A1 | 0 | 0 | 0 | 30 |
| A6 | 0 | 0 | 0 | 40 |
| AI1 | 0 | 36 | 0 | 0 |
| AI5 | 0 | 8 | 0 | 0 |
| C1 | 0 | 0 | 0 | 7 |
| C3 | 0 | 4 | 0 | 0 |
| C4 | 0 | 4 | 0 | 0 |
| C5 | 0 | 0 | 0 | 15 |
| C7 | 0 | 40 | 0 | 0 |
| D2 | 4 | 15 | 2 | 0 |
| D3 | 0 | 243 | 38 | 0 |
| F1 | 0 | 0 | 5 | 0 |
| F2 | 0 | 18 | 0 | 0 |
| F3 | 0 | 40 | 4 | 0 |
| F4 | 0 | 52 | 0 | 0 |
| F6 | 0 | 37 | 0 | 0 |
| F8 | 0 | 1 | 0 | 0 |
| F9 | 1 | 35 | 0 | 0 |
| G1 | 0 | 0 | 40 | 0 |
| G10 | 0 | 148 | 0 | 0 |
| G11 | 0 | 50 | 0 | 0 |
| G12 | 0 | 18 | 0 | 0 |
| G13 | 0 | 32 | 0 | 0 |
| G14 | 0 | 0 | 5 | 0 |
| G2 | 0 | 16 | 16 | 0 |
| G3 | 0 | 31 | 0 | 0 |
| G4 | 0 | 3 | 11 | 0 |
| G5 | 0 | 47 | 0 | 0 |
| G6 | 0 | 24 | 8 | 0 |
| G8 | 0 | 16 | 8 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| J1 | 0 | 61 | 0 | 63 |
| K1 | 0 | 4 | 0 | 0 |
| K4 | 0 | 0 | 0 | 4 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 28 | 0 |
| M13 | 0 | 0 | 12 | 0 |
| M14 | 0 | 24 | 0 | 0 |
| M18 | 0 | 16 | 0 | 0 |
| M2 | 0 | 8 | 0 | 0 |
| NR | 0 | 16 | 0 | 0 |
| P0 | 0 | 12 | 0 | 0 |
| P1 | 0 | 0 | 0 | 4 |
| P2 | 0 | 20 | 0 | 0 |
| P7 | 0 | 12 | 0 | 0 |
| P9 | 0 | 0 | 0 | 5 |
| Q10 | 0 | 8 | 0 | 0 |
| Q11 | 0 | 6 | 0 | 0 |
| Q12 | 0 | 14 | 4 | 0 |
| Q13 | 0 | 7 | 2 | 0 |
| Q14 | 0 | 3 | 5 | 0 |
| Q15 | 0 | 0 | 3 | 0 |
| Q3 | 5 | 0 | 0 | 0 |
| Q4 | 0 | 12 | 0 | 0 |
| Q5 | 0 | 8 | 0 | 0 |
| Q6 | 0 | 5 | 0 | 0 |
| Q7 | 0 | 0 | 1 | 0 |
| Q9 | 0 | 0 | 1 | 0 |
| R3 | 0 | 0 | 32 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S2 | 0 | 13 | 39 | 0 |
| S4 | 0 | 0 | 2 | 0 |
| S5 | 24 | 0 | 29 | 0 |
| V1 | 0 | 27 | 1 | 0 |
| X2 | 0 | 0 | 8 | 0 |
| X3 | 0 | 3 | 0 | 0 |
| X5 | 0 | 0 | 43 | 0 |
| X6 | 0 | 8 | 0 | 0 |
| lighting_dark | 0 | 4 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 15276 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 48.0 -> 48.0 | Argus: The sofa's front is blocked by f_L1_017. Relayouting the room will re-place the AI pieces to clear the blockage. (fixes a:F88) | ![](agent/r1_013_relayout_room_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_014_relayout_room_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 15277 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | 58.0 -> 58.0 | Argus: The sofa's front is blocked by f_L1_018. Relayouting the room will re-place the AI pieces to clear the blockage. (fixes a:F92) | ![](agent/r1_015_relayout_room_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_016_relayout_room_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 15298 | 1 | move_piece | f_L-1_038 | adjusted_by_ai | 27.0 -> 27.0 | S2: table cut chairs f_L-1_039 and f_L-1_042 by 0.034 m; shift the table 0.08 m so the cut drops below the 0.010 m allowance. | ![](agent/r1_080_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_081_move_piece_after_r_L-1_salon_2.png) |
| 15305 | 1 | resize_piece | f_L-1b_041 | adjusted_by_ai | 0.0 -> 0.0 | Sofa footprint is rotated 90° against product sizes; correct to 2.13 m wide x 0.90 m deep to match the drawn orientation (back on left wall, facing right). | ![](agent/r1_087_resize_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_089_resize_piece_after_r_L-1b_salon_2.png) |
| 15309 | 1 | move_piece | f_L-1_031 | adjusted_by_ai | 27.0 -> 27.0 | Nudge chair f_L-1_031 away from the table edge to clear the 0.040 m cut with table f_L-1_027. | ![](agent/r1_092_move_piece_before_r_L-1_salon.png) | ![](agent/r1_094_move_piece_after_r_L-1_salon.png) |
| 15315 | 1 | resize_piece | f_L-1b_042 | adjusted_by_ai | 0.0 -> 0.0 | Sofa was read 90° against product sizes; swap to 2.13m wide x 0.90m deep to match a real sofa aspect ratio. | ![](agent/r1_101_resize_piece_before_r_L-1b_salon.png) | ![](agent/r1_104_resize_piece_after_r_L-1b_salon.png) |
| 15328 | 1 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 15.0 | Armchair must face the sofa f_L-1b_041 which is to its north (+y); rotating to face 90° aligns it with the seating group and clears the front zone blocked by f_L-1b_054. | ![](agent/r1_113_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_114_rotate_piece_after_r_L-1b_salon_2.png) |
| 15332 | 1 | rotate_piece | f_L-1b_054 | adjusted_by_ai | 15.0 -> 45.0 | Armchair must face the sofa f_L-1b_041 which is to its north (+y); rotating to face 90° aligns it with the seating group and clears the front zone blocked by f_L-1b_053. | ![](agent/r1_117_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_120_rotate_piece_after_r_L-1b_salon_2.png) |
| 15333 | 1 | rotate_piece | f_L1_035 | adjusted_by_ai | 48.0 -> 48.0 | Bench front was read on its short side; its back stands on the wall so the front must face 270° into the room. | ![](agent/r1_118_rotate_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_119_rotate_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 15335 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | 58.0 -> 58.0 | Room is a game/activity/relaxation room with sofas, coffee tables and dining; 'other' is wrong, living fits its area, fixtures and doors. | ![](agent/r1_121_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_123_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 15343 | 1 | move_piece | f_L1_019 | adjusted_by_ai | 58.0 -> 68.0 | Shift sofa f_L1_019 north away from f_L1_018 to clear the blocked free zone in front of it (F6) without breaking the walkway. | ![](agent/r1_130_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_132_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 15346 | 1 | retype_piece | f_L1_035 | adjusted_by_ai | 48.0 -> 51.0 | bench is invalid in a living room; a 1.4x0.45 console table fits its size and its position against the wall. | ![](agent/r1_133_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_134_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 15361 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 90.0 -> 100.0 | Second solver candidate re-scales the balcony set to fit the 19.7 m² terrace, resolving the plant's wall collision, floating and size findings. | ![](agent/r1_145_relayout_room_before_r_L1_teras.png) | ![](agent/r1_146_relayout_room_after_r_L1_teras.png) |
| 15375 | 1 | set_lighting | r_L-1_mutfak | agent_override | - | Add a warm layered light layer to the flat generic daylight (a:D3:r_L-1_mutfak). | - | - |
| 15377 | 1 | retype_piece | f_L1_049 | added_by_ai | 100.0 -> 100.0 | A shoe cabinet is unusual in a top-floor hall; a potted plant is a valid size candidate that suits the hall context and clears the AI1 wrong_type finding. | ![](agent/r1_158_retype_piece_before_r_L1_koridor.png) | ![](agent/r1_159_retype_piece_after_r_L1_koridor.png) |
| 15379 | 1 | report_library_gap | f_L-1_008 | library_gap | - | The stove is built into the counter run (hob in worktop, oven below); no library model may replace it, so the crude low-poly look (a:F265, a:F286) stays for review. | - | - |
| 15380 | 1 | report_library_gap | f_L-1_003 | library_gap | - | f_L-1_003 is a module of the code-designed kitchen run with its top at 1.18 m (a:F234); no library model replaces a run module, so the height finding stays for review. | - | - |
| 15383 | 1 | report_library_gap | f_L-1_067 | library_gap | - | No audited library sink model passes the fit rules for the drawn 0.79x0.50 m sink, so the bright blue model (a:F289) stays for review. | - | - |
| 15393 | 1 | move_piece | f_L0_045 | added_by_ai | 70.0 -> 70.0 | Nightstand f_L0_045 stands in front of window win_L0_004 (F80); snapping its back to the right wall and shifting it 0.1 m up clears the window line while keeping it at the bed's head. | ![](agent/r1_179_move_piece_before_r_L0_yatak_odasi_2.png) | ![](agent/r1_181_move_piece_after_r_L0_yatak_odasi_2.png) |
| 15399 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. | ![](agent/r1_190_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_191_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 15413 | 1 | report_library_gap | f_L-1_012 | library_gap | - | F235: f_L-1_012 top at 1.18 m over working height 0.97 m; the kitchen_counter catalogue is empty (0 models), so no audited model can replace the too-tall module build. | - | - |
| 15414 | 1 | set_lighting | r_L0_koridor | agent_override | - | Camera view is 0.24 stops over the EV cap; the finding names factor x1.67 on the room to bring exposure within the cap. | - | - |
| 15416 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | View cam_r_L0_e_banyo_1 is 0.86 stops over the EV cap; the finding names a room lighting factor of x2.57. | - | - |
| 15422 | 1 | swap_model | f_L1_043 | added_by_ai | 100.0 -> 100.0 | Replace the parametric mesh with a real library dining table (0.747 m, modern) that fits the 0.7 m drawn footprint, resolving the below-library build and the library gap. | ![](agent/r1_213_swap_model_before_r_L1_teras_2.png) | ![](agent/r1_214_swap_model_after_r_L1_teras_2.png) |
| 15423 | 1 | set_lighting | r_L0_banyo | agent_override | - | Both cameras are over the EV cap (room too dark); the findings ask for x1.67/x1.8 on the room, so set the higher factor to clear both lighting_dark findings. | - | - |
| 15425 | 1 | report_library_gap | f_L0_039 | library_gap | - | No audited shoe_cabinet model passes the fit rules (caps, height) for the 0.6 x 0.25 m, 1.0 m tall piece: three real models (0.5x0.23x1.79, 0.8x0.4x1.0, 0.75x0.25x1.28) were all pin_refused, so the crude placeholder model stays. | - | - |
| 15426 | 1 | report_library_gap | report_library_gap | library_gap | - | The hall lacks the warm layered lighting layer (chandelier, wall sconces) seen in the reference; no library model provides it, so the D3 warm-light finding stays for review. | - | - |
| 15435 | 1 | swap_model | f_L-1_056 | adjusted_by_ai | 77.0 -> 77.0 | Swap plain untextured white block bathtub for a premium Kaldewei CLASSIC DUO 180x80cm bathtub with proper styling to match the reference. | ![](agent/r1_243_swap_model_before_r_L-1_banyo.png) | ![](agent/r1_248_swap_model_after_r_L-1_banyo.png) |
| 15438 | 1 | report_library_gap | report_library_gap | library_gap | - | The room is missing wall art and has a broken sunburst fixture that clashes with the modern style; no audited library model for integrated wall art/decor exists for this bathroom. | - | - |
| 15439 | 1 | set_camera | cam_r_L1_banyo_1 | agent_override | - | The current camera is a close-up of the bathtub corner; re-aim it to a free pose with headroom that shows the whole room including the washbasin and toilet. | - | - |
| 15447 | 1 | report_library_gap | f_L-1_026 | library_gap | - | All audited washbasin models matching the drawn 1.0x0.55m footprint were audit-removed; no usable sleek integrated sink model exists in the library for this piece. | - | - |
| 15873 | 2 | correct_geometry | o_L1_001 | corrected_by_ai | - | Argus: The opening o_L1_001 is not cut through its wall w_L1_003; the door ray hits the wall. (fixes a:F229) | - | - |
| 15884 | 2 | set_camera | r_L-1_koridor_2 | agent_override | - | Argus: The camera is positioned too close to a corner, showing only a wall and a piece of furniture. It should frame the hall's main functional areas. (fixes a:F279) | - | - |
| 15885 | 2 | set_camera | r_L-1_koridor_2 | agent_override | - | Argus: The render is a flat, unlit corner of the hall. The camera should be repositioned to show the hall's main functional areas. (fixes a:F282) | - | - |
| 15887 | 2 | swap_model | f_L-1_070 | adjusted_by_ai | 27.0 -> 27.0 | Argus: The dark brown armchair clashes with the light beige sofa and white dining chairs. Swapping to a modern/scandinavian model with a lighter, cohesive finish resolves the mismatch. (fixes a:F290) | ![](agent/r2_011_swap_model_before_r_L-1_salon.png) | ![](agent/r2_012_swap_model_after_r_L-1_salon.png) |
| 15889 | 2 | swap_model | f_L-1_028 | adjusted_by_ai | 27.0 -> 27.0 | Argus: The dining chairs are a generic, repetitive dark model that feels mass-produced and clashes with the room's style. Swapping to a modern/scandinavian model resolves the mismatch. (fixes a:F293) | ![](agent/r2_014_swap_model_before_r_L-1_salon.png) | ![](agent/r2_015_swap_model_after_r_L-1_salon.png) |
| 15890 | 2 | set_camera | r_L0_banyo | agent_override | - | Argus: The render is a tight, low-angle crop of a corner that fails to show the room's main group. Setting the camera to frame the main functional group resolves the issue. (fixes a:F297) | - | - |
| 15892 | 2 | set_camera | r_L0_banyo | agent_override | - | Argus: The render is a stark, unfinished utility space with a decorative grille that looks like a prison bar. Setting the camera to frame the main group and resolving the grille issue resolves the problem. (fixes a:F300) | - | - |
| 15896 | 2 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The current office_chair is a utilitarian, ergonomic model with a blue mesh back that clashes with the warm, residential aesthetic of the bedroom; swapping to a modern minimal chair of the same footprint restores a coherent set. (fixes a:F310) | ![](agent/r2_019_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_020_swap_model_after_r_L0_yatak_odasi.png) |
| 15898 | 2 | swap_model | f_L0_030 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The current desk is a dark metal and wood piece that looks like a generic office or industrial piece; swapping to a minimal/modern/scandinavian desk of the same footprint restores a coherent set. (fixes a:F314) | ![](agent/r2_022_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_023_swap_model_after_r_L0_yatak_odasi.png) |
| 15899 | 2 | swap_model | f_L0_019 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The current bed is styled with only a bare white sheet and two pillows, lacking the textured throw and layered bedding seen in the reference; swapping to a scandinavian/japandi bed model that includes styled bedding restores the layered loo (fixes a:F315) | ![](agent/r2_024_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_025_swap_model_after_r_L0_yatak_odasi.png) |
| 15900 | 2 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The current office_chair is a bright blue, utilitarian model that is a severe clash; swapping to a modern minimal chair of the same footprint restores a coherent set. (fixes a:F317) | ![](agent/r2_026_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_027_swap_model_after_r_L0_yatak_odasi_3.png) |
| 15925 | 2 | move_piece | f_L-1_073 | adjusted_by_ai | 27.0 -> 27.0 | shift coffee table up (away from window) to clear the 0.12 m2 overlap with armchair f_L-1_071 | ![](agent/r2_091_move_piece_before_r_L-1_salon.png) | ![](agent/r2_092_move_piece_after_r_L-1_salon.png) |
| 15938 | 2 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift nightstand f_L0_032 slightly away from the bed to resolve the 0.06 m² overlap (F9) and correct the -0.12 m gap to a valid distance (G4). | ![](agent/r2_118_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r2_120_move_piece_after_r_L0_e_yatak_odasi.png) |
| 15955 | 2 | move_piece | f_L0_042 | added_by_ai | 70.0 -> 70.0 | Slide nightstand f_L0_042 0.06 m along the window wall to clear the window win_L0_001 (sill 0.20 m) while staying beside the bed. | ![](agent/r2_139_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r2_140_move_piece_after_r_L0_yatak_odasi.png) |
| 15980 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 3 gives a larger, better-balanced terrace set for the 19.7 m² outdoor living space (candidate 1 was rejected for the lone plant, candidate 2 already tried). | ![](agent/r2_165_relayout_room_before_r_L1_teras.png) | ![](agent/r2_166_relayout_room_after_r_L1_teras.png) |
| 15994 | 2 | report_library_gap | f_L1_042 | library_gap | - | Potted plant f_L1_042 is a crude low-poly placeholder; no audited library model of a real potted plant exists (a:F449). | - | - |
| 15995 | 2 | report_library_gap | f_L1_039 | library_gap | - | Dining table f_L1_039 is a dated traditional turned-leg model that does not fit the modern balcony; no audited modern dining table model exists (a:F273, a:F338). | - | - |
| 15996 | 2 | report_library_gap | f_L1_041 | library_gap | - | Chair f_L1_041 is an all-black model clashing with the set; no audited modern chair model exists (a:F451, a:F339). | - | - |
| 15997 | 2 | report_library_gap | f_L1_040 | library_gap | - | Chair f_L1_040 is plain black molded plastic clashing with the traditional table; no audited modern chair model exists (a:F337). | - | - |
| 16010 | 2 | swap_model | f_L0_039 | added_by_ai | 100.0 -> 100.0 | Swap the crude low-poly placeholder shoe cabinet (with green pot) for a real japandi minimal Walnut Wooden Shoe Rack model that fits the 0.6m width and 1.0m height, resolving the visual clash with the neutral palette. | ![](agent/r2_180_swap_model_before_r_L0_koridor.png) | ![](agent/r2_181_swap_model_after_r_L0_koridor.png) |
| 16014 | 2 | set_camera | r_L1_banyo | agent_override | - | The current camera is too close to the bathtub, filling the frame with a corner and the tub rim; a free pose with headroom showing all three fixtures will let the room be evaluated. | - | - |
| 16016 | 2 | report_library_gap | f_L0_003 | library_gap | - | Argus flags the washbasin model as a style clash against the modern reference; the only real product of the type (3dwh_4736e8ccac82f4d690680828) is already in use and the alternative real model was audit-removed, so no audited modern model exists to swap to. | - | - |
| 16017 | 2 | report_library_gap | f_L0_018 | library_gap | - | Argus flags the toilet as a basic unstyled white box clashing with the reference; both generated candidates were audit-removed and no other real product is available, so the library gap is recorded for review. | - | - |
| 16018 | 2 | report_library_gap | f_L0_014 | library_gap | - | No audited real-product shower model fits the drawn 0.60 x 1.40 m footprint (closest hssd_9368052ddb2713527a9be87ab3483ffd1f2c2a65 at 52.5% non-uniform scale, mean 0.7473; relaxed caps also fail), so the parametric build is by design and the F2/P7 findings stay for review. | - | - |
| 16455 | 3 | set_camera | r_L1_banyo | agent_override | - | Argus: The view is a 1/5 close-up of a corner and the tub rim; the room and its other fixtures are not visible. Re-aiming the existing camera at the full set is the direct fix. (fixes a:F321) | - | - |
| 16456 | 3 | set_material | wet_walls | agent_override | - | Argus: The render shows flat untextured grey walls and floor; the wet_walls slot is the cause. A styled hard finish restores the missing layer. (fixes a:F323) | - | - |
| 16457 | 3 | set_camera | r_L1_koridor | agent_override | - | Argus: The view is a 1/5 bare, unlit shell. Re-aiming the camera at the hall's defining pieces is the direct fix. (fixes a:F324) | - | - |
| 16466 | 3 | set_exterior | exterior:ground,site | agent_override | - | Argus: The outdoor environment is a flat untextured plane with low-poly trees; setting a textured ground and a proper tree count upgrades the site. (fixes a:F360) | - | - |
| 16492 | 3 | rotate_piece | f_L-1b_051 | adjusted_by_ai | 0.0 -> 15.0 | Armchair f_L-1b_051 is 65° off the sofa axis and its front zone is blocked by f_L-1b_052; rotating it to face the sofa (front_deg 90) aligns it with the group and clears the mutual block. | ![](agent/r3_064_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r3_065_rotate_piece_after_r_L-1b_salon.png) |
| 16493 | 3 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 15.0 -> 45.0 | Armchair f_L-1b_052 is 90° off the sofa axis and its front zone is blocked by f_L-1b_051; rotating it to face the sofa (front_deg 90) aligns it with the group and clears the mutual block. | ![](agent/r3_067_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r3_069_rotate_piece_after_r_L-1b_salon.png) |
| 16507 | 3 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 15.0 | Face the armchair toward the sofa f_L-1b_041 (G3/F4). | ![](agent/r3_082_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_083_rotate_piece_after_r_L-1b_salon_2.png) |
| 16510 | 3 | rotate_piece | f_L-1b_054 | adjusted_by_ai | 15.0 -> 45.0 | Face the armchair toward the sofa f_L-1b_041 (G3/F4). | ![](agent/r3_085_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_090_rotate_piece_after_r_L-1b_salon_2.png) |
| 16527 | 3 | move_piece | f_L1_032 | adjusted_by_ai | 68.0 -> 78.0 | Nudge the armchair 0.1 m closer to the coffee table (2.73 m -> ~2.63 m) to clear G3/F94. | ![](agent/r3_101_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_103_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 16528 | 3 | report_library_gap | f_L0_023 | library_gap | - | Wardrobe f_L0_023 is a module build (wardrobe_run) with no audited library model within tolerance; all swap_model candidates were rejected (lower quality or audit-removed), so the module build is kept and the gap is recorded for review. | - | - |
| 16530 | 3 | report_library_gap | f_L0_031 | library_gap | - | Nightstand f_L0_031's current model (abo_B07DVRLW48, rated 4.0) is the best available; every swap candidate in memory was rejected as lower quality (3.0), so the style mismatch and visibility findings stay open due to library constraints. | - | - |
| 16531 | 3 | report_library_gap | f_L0_032 | library_gap | - | Nightstand f_L0_032's current model (abo_B07DVRLW48, rated 4.0) is the best available; every swap candidate in memory was rejected as lower quality (3.0), so the style mismatch and visibility findings stay open due to library constraints. | - | - |
| 16539 | 3 | move_piece | f_L0_045 | added_by_ai | 70.0 -> 70.0 | a:F80: move nightstand f_L0_045 off window win_L0_004 onto wall w_L0_016 to clear the window | ![](agent/r3_109_move_piece_before_r_L0_yatak_odasi_2.png) | ![](agent/r3_110_move_piece_after_r_L0_yatak_odasi_2.png) |
| 16541 | 3 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Replace the bright blue office chair with a neutral black modern-minimal chair to remove the color/style clash (a:F317). | ![](agent/r3_111_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_113_swap_model_after_r_L0_yatak_odasi_3.png) |
| 16543 | 3 | report_library_gap | report_library_gap | library_gap | - | Room flagged for missing curtains (a:D3:r_L0_yatak_odasi_3); no curtain model exists in the library to add the soft layering the reference shows. | - | - |
| 16567 | 3 | set_camera | r_L1_koridor | agent_override | - | a:F326: the view is a close-up of a corner and the wardrobe, not a view of the hall; re-aim it to show the whole hall with the plant, stair and wardrobe. | - | - |
| 16569 | 3 | remove_piece | f_L1_049 | added_by_ai | 100.0 -> 100.0 | a:F428: the entrance group's piece is read as a shoe cabinet, which is unusual for a top-floor hall; removing the AI-added piece leaves the hall without it (the entrance group is optional). | ![](agent/r3_131_remove_piece_before_r_L1_koridor.png) | ![](agent/r3_133_remove_piece_after_r_L1_koridor.png) |
| 16576 | 3 | set_room_type | r_L1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | The 15.3 m2 top-floor hall is dominated by a drawn stair (2.71x2.1 m) and is a stair hall, not an entrance hall, so the shoe cabinet and wardrobe findings stem from the wrong room type. | ![](agent/r3_136_set_room_type_before_r_L1_koridor_2.png) | ![](agent/r3_137_set_room_type_after_r_L1_koridor_2.png) |
| 16581 | 3 | move_piece | f_L0_030 | adjusted_by_ai | 70.0 -> 80.0 | Move desk 0.05m in +y to increase bed right side clearance from 0.56m to 0.61m, satisfying G5 >= 0.60m | ![](agent/r3_141_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r3_142_move_piece_after_r_L0_yatak_odasi.png) |
| 16588 | 3 | report_library_gap | f_L1_042 | library_gap | - | a:F449: the potted plant is a crude low-poly placeholder; no audited library model of a real potted plant exists. | - | - |
| 16589 | 3 | report_library_gap | f_L1_039 | library_gap | - | a:F273: the dining table is a dated traditional turned-leg model that does not fit the modern balcony; no audited modern dining table model exists. | - | - |
| 16590 | 3 | report_library_gap | f_L1_041 | library_gap | - | a:F451: the all-black chair clashes with the set; no audited modern chair model exists to replace it. | - | - |
| 16591 | 3 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | The 19.7 m² terrace needs a properly sized outdoor set; relayout with the large table option instead of the too-small dining set. | ![](agent/r3_150_relayout_room_before_r_L1_teras.png) | ![](agent/r3_151_relayout_room_after_r_L1_teras.png) |
| 16599 | 3 | report_library_gap | f_L-1_026 | library_gap | - | All three candidate washbasin models were audit-removed and fix_fixture found no valid spot; no usable library model remains for the generic floating-box sink (a:F441). | - | - |
| 16600 | 3 | report_library_gap | f_L-1_056 | library_gap | - | The accepted round-1 model still reads as a plain untextured block and the round-3 swap candidate was audit-removed; no further usable bathtub model remains (a:F440). | - | - |
| 16601 | 3 | report_library_gap | report_library_gap | library_gap | - | Room-level D3 flags a broken sunburst fixture / missing wall-art layer with no corresponding piece to swap; the decorative layer has no audited library model (a:D3:r_L-1_banyo). | - | - |
| 16606 | 3 | report_library_gap | f_L0_003 | library_gap | - | No audited modern washbasin model exists that reads as a bathroom basin; the current real model is the best available and all generated/other candidates were rejected. | - | - |
| 16607 | 3 | report_library_gap | f_L0_018 | library_gap | - | No audited modern toilet model is usable; all generated and objaverse candidates were rejected as audit-removed, leaving the basic white box as the only available model. | - | - |
| 17321 | 4 | swap_model | f_L0_010 | adjusted_by_ai | 80.0 -> 80.0 | Argus: The wardrobe has only 0.66 m in front; swapping to the 0.51 m deep model (abo_B07GFS1R5B) will free up the needed clearance. (fixes a:F78) | ![](agent/r4_003_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r4_004_swap_model_after_r_L0_yatak_odasi.png) |
| 17338 | 4 | set_camera | r_L-1_banyo | agent_override | - | Argus: The current camera is too close and too low, cutting off the top of the toilet and the mirror; setting the camera to show the main fixtures should fix it. (fixes a:F285) | - | - |
| 17339 | 4 | set_camera | r_L-1_banyo | agent_override | - | Argus: The current camera is cramped and unstyled, missing the reference's standard; setting the camera to show the main fixtures should fix it. (fixes a:F288) | - | - |
| 17341 | 4 | set_camera | r_L-1_koridor_2 | agent_override | - | Argus: The camera is pressed against a blank corner; the hall's defining pieces are not in frame. (fixes a:F291) | - | - |
| 17346 | 4 | swap_model | f_L-1_028 | adjusted_by_ai | 27.0 -> 27.0 | Argus: The dining chairs are a random mix of models and finishes; swapping to a single minimal/modern model coordinates the dining set. (fixes a:F302) | ![](agent/r4_021_swap_model_before_r_L-1_salon.png) | ![](agent/r4_022_swap_model_after_r_L-1_salon.png) |
| 17347 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The render is a close-up of a corner and the top of a bathtub; the camera must frame the room's main functional group. (fixes a:F304) | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 15264 | 1 | swap_model | f_L0_023 | asset_unusable: 3dwh_e41345920f4dce2514160e34 is not used: audit pending | Argus: The wardrobe f_L0_023 is rendered as a dark, flat wall panel with a window frame embedded in it, rather than a functional storage unit. Swapping to a proper wardrobe model (3dwh_e41345920f4dce2514160e34, 3.15 x 0.64 x 2.59 m, modern) fixes  (fixes a:F41) |
| 15265 | 1 | relayout_room | r_L-1_mutfak | no_place: r_L-1_mutfak relayout: no place passes the checks (dining: no place passes the checks) | Argus: The counter is placed so the aisle is only 0.55 m; re-solving the kitchen run in the room will find a placement with the required clearance. (fixes a:F65) |
| 15266 | 1 | relayout_room | r_L-1_mutfak_2 | no_place: r_L-1_mutfak_2 relayout: no place passes the checks (dining: no place passes the checks) | Argus: The stove is 0.06 m off the wall; re-solving the kitchen run will snap it to the wall. (fixes a:F66) |
| 15267 | 1 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: no place passes the checks (no candidate position fits the room) | Argus: The bed has only 0.53 m on the left; re-solving the bedroom group will find a placement with the required clearance. (fixes a:F76) |
| 15268 | 1 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Argus: The bed has only 0.53 m on the right; re-solving the bedroom group will find a placement with the required clearance. (fixes a:F79) |
| 15269 | 1 | swap_model | f_L0_012 | lower_quality: f_L0_012: hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The room is too tight for the current 0.60 m-deep wardrobe to have 0.80 m in front; a shallower 0.57 m model (abo_B07B3XXD3P) or the 0.61 m one with a different placement is needed. Since move was refused, swapping to a shallower model is t (fixes a:F81) |
| 15270 | 1 | swap_model | f_L0_013 | acceptance: pin_refused: f_L0_013: hssd_72807de315ae7f20a846e137cf5e755f909a398f: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric shower is 1.40 x 0.60 m, which is not a standard product size. Swapping to a 1.20 x 0.80 m model (hssd_72807de315ae7f20a846e137cf5e755f909a398f) gives a valid product size that fits the 4.0 m2 bathroom. (fixes a:F82) |
| 15271 | 1 | swap_model | f_L0_014 | acceptance: pin_refused: f_L0_014: hssd_9368052ddb2713527a9be87ab3483ffd1f2c2a65: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric shower is 0.60 x 1.40 m, which is not a standard product size. Swapping to a 0.80 x 1.23 m model (hssd_9368052ddb2713527a9be87ab3483ffd1f2c2a65) gives a valid product size. (fixes a:F83) |
| 15272 | 1 | swap_model | f_L0_021 | lower_quality: f_L0_021: abo_B07GFRH5ZS is rated 3.0 against 4.5 of the current model abo_B086TGFT35: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Argus: The bed is 1.55 m wide and only 0.37 m is free on the left. A 1.49 m wide bed (abo_B07GFRH5ZS) would give more clearance. Move was refused due to drawn_lock and max_tries. (fixes a:F84) |
| 15273 | 1 | swap_model | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Argus: The wardrobe has only 0.17 m in front. A shallower 0.57 m model (abo_B07B3XXD3P) would help. Move was refused because the finding persisted. (fixes a:F85) |
| 15274 | 1 | swap_model | f_L0_022 | lower_quality: f_L0_022: abo_B07GFRH5ZS is rated 3.0 against 4.0 of the current model abo_B07L1DDXLR: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The bed is 1.55 m wide and only 0.37 m is free on the right. A 1.49 m wide bed (abo_B07GFRH5ZS) would give more clearance. Move was refused due to drawn_lock and max_tries. (fixes a:F86) |
| 15275 | 1 | swap_model | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m) | Argus: The wardrobe has only 0.17 m in front. A shallower 0.57 m model (abo_B07B3XXD3P) would help. Move was refused due to max_tries. (fixes a:F87) |
| 15278 | 1 | swap_model | f_L1_027 | pin_refused: f_L1_027: gen_wardrobe_rustic_1_97c119f6: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07GFS1VB6): the real model stays; swap to a real model of the type or use another tool | Argus: The current wardrobe model is too large for the narrow corridor. Swapping to a smaller, more appropriate model will improve the space. (fixes a:F99) |
| 15279 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: The kitchen is missing a fridge, which is a required member of the kitchen_run group. The place_group tool will add the missing member. (fixes a:F205) |
| 15280 | 1 | place_group | r_L-1_mutfak_2 | no_change: r_L-1_mutfak_2 already has its kitchen_run r_L-1_mutfak_2.kitchen_run (anchor f_L-1_010, members f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068, f_L-1_096): nothing missing, never a second set | Argus: The kitchen is missing a fridge, which is a required member of the kitchen_run group. The place_group tool will add the missing member. (fixes a:F206) |
| 15281 | 1 | fix_fixture | f_L-1_051 | no_change: f_L-1_051: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is too close to the side wall/fixture. The fix_fixture tool will move it to the nearest valid spot that satisfies the clearance requirement. (fixes a:F207) |
| 15282 | 1 | fix_fixture | f_L-1_056 | no_change: f_L-1_056: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The bathtub does not have enough clearance in front. The fix_fixture tool will move it to the nearest valid spot that satisfies the clearance requirement. (fixes a:F208) |
| 15283 | 1 | fix_fixture | f_L-1_052 | fixture_size: f_L-1_052: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m wide toilet leaves only 0.33 m to the side wall; a 0.41 m model (gen_toilet_japandi_6_1b5173e9) restores the required 0.38 m clearance. (fixes a:F209) |
| 15284 | 1 | fix_fixture | f_L-1_055 | fixture_size: f_L-1_055: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The 0.80 m deep tub leaves only 0.28 m in front; a 0.77 m deep model (hssd_b403849fe16897c7d53d2578edaa859c46164e71) frees the required 0.53 m. (fixes a:F210) |
| 15285 | 1 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The 0.60 m deep shower leaves only 0.27 m in front; a 0.84 m deep model (gen_shower_japandi_6_bd58a347) is oriented so its 1.29 m side runs along the wall, freeing the required 0.53 m front clearance. (fixes a:F215) |
| 15286 | 1 | fix_fixture | f_L0_014 | fixture_size: f_L0_014: the drawn 0.60 x 1.40 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The 0.60 m deep shower leaves only 0.10 m in front and rotation was refused (front faces a wall); a 0.80 m deep model (hssd_9368052ddb2713527a9be87ab3483ffd1f2c2a65) with its 1.23 m side along the wall frees the required 0.53 m. (fixes a:F216) |
| 15287 | 1 | fix_fixture | f_L0_018 | fixture_size: f_L0_018: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: Same 0.33 m side clearance; a 0.41 m wide model restores the 0.38 m minimum. (fixes a:F217) |
| 15288 | 1 | fix_fixture | f_L0_025 | fixture_size: f_L0_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 0.28 m front clearance; a 0.77 m deep model frees the required 0.53 m. (fixes a:F218) |
| 15289 | 1 | fix_fixture | f_L0_017 | fixture_size: f_L0_017: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: Same 0.33 m side clearance; a 0.41 m wide model restores the 0.38 m minimum. (fixes a:F219) |
| 15290 | 1 | fix_fixture | f_L0_026 | fixture_size: f_L0_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 0.28 m front clearance; a 0.77 m deep model frees the required 0.53 m. (fixes a:F220) |
| 15291 | 1 | fix_fixture | f_L1_021 | fixture_size: f_L1_021: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: Same 0.33 m side clearance; a 0.41 m wide model restores the 0.38 m minimum. (fixes a:F221) |
| 15292 | 1 | fix_fixture | f_L1_025 | fixture_size: f_L1_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 0.28 m front clearance; a 0.77 m deep model frees the required 0.53 m. (fixes a:F222) |
| 15293 | 1 | fix_fixture | f_L1_022 | fixture_size: f_L1_022: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: Same 0.33 m side clearance; a 0.41 m wide model restores the 0.38 m minimum. (fixes a:F223) |
| 15295 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 27 -> 17 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | F4: armchair stood behind the back of sofa f_L-1_054 looking at it; turn it to face the seating area (toward the sofa) instead. |
| 15296 | 1 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | F9: table_coffee overlapped armchair f_L-1_069 by 0.12 m²; shift it 0.23 m left to clear the chair. |
| 15297 | 1 | move_piece | f_L-1_065 | drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | G12: floor_lamp stood in front of window win_L-1_002; move it 0.61 m into the room, clear of the window band. |
| 15301 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 27 -> 17 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn the armchair to face into the room (away from the sofa back) so it no longer stands behind the sofa looking at it. |
| 15302 | 1 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Shift the coffee table right to clear the 0.12 m² overlap with armchair f_L-1_071. |
| 15303 | 1 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.08 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | F9: table_coffee overlapped armchair f_L-1_069 by 0.12 m²; shift it 0.25 m into the room to clear the chair. |
| 15304 | 1 | move_piece | f_L-1_065 | f_L-1_054: no_overlap, f_L-1_065: no_overlap | G12: floor_lamp stood in front of window win_L-1_002; nudge it 0.30 m into the room, clear of the window band. |
| 15306 | 1 | move_piece | f_L-1_050 | f_L-1_050: no_overlap, f_L-1_054: clearance_ok, f_L-1_088: no_overlap, score: plausibility 27 -> 7 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050; F9 f_L-1_088: table_coffee f_L-1_088 overlaps armchair f_L-1_050 by 0.09 m²) | G11: armchair's front use zone was not reached by a 0.60 m walkway from the door; shift it 0.30 m toward the door to open the walkway. |
| 15307 | 1 | move_piece | f_L-1_054 | f_L-1_054: clearance_ok, score: plausibility 27 -> 17 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050) | G11: sofa_corner's front use zone was not reached by a 0.60 m walkway from the door; shift it 0.30 m toward the door to open the walkway. |
| 15308 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 27 -> 7 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Turn the armchair to face the window side, away from the sofa back, resolving the orientation finding. |
| 15310 | 1 | move_piece | f_L-1_073 | score: plausibility 27 -> 17 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.08 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Shift the coffee table toward the window to clear the 0.12 m² overlap with armchair f_L-1_071. |
| 15311 | 1 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m drawn piece along the top wall is a long low storage unit; type it as a sideboard to resolve the untyped finding. |
| 15313 | 1 | move_piece | f_L-1_074 | score: plausibility 27 -> 17 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | F9: table_coffee overlapped armchair f_L-1_069 by 0.12 m²; shift it 0.35 m into the room to clear the chair. |
| 15314 | 1 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 1: f_L-1_054: no_overlap; f_L-1_065: no_overlap | G12: floor_lamp stood in front of window win_L-1_002; nudge it 0.30 m into the room, clear of the window band. |
| 15316 | 1 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Shift the coffee table toward the window corner to clear the overlap with armchair f_L-1_071. |
| 15317 | 1 | retype_piece | f_L-1_021 | retype: kitchen_counter is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m drawn run along the top wall is a long counter; type it as a kitchen counter to resolve the untyped finding. |
| 15318 | 1 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 0.59 m off the wall and its front is blocked by a plant; snapping its back to the left wall (span s4) clears the front zone and resolves the off-wall and orientation findings. |
| 15319 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)); 1 more kept | Armchair is 114° off the sofa axis; rotate to face the sofa (270°) to align with the seating group. |
| 15320 | 1 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041, f_L-1b_045)); 1 more kept | Armchair is 114° off the sofa axis and its front is blocked by the other armchair; rotating to face 270° (towards the sofa) aligns it with the seating group and clears the front zone. |
| 15321 | 1 | rotate_piece | f_L-1b_054 | acceptance: finding G3:f_L-1b_054 is still there after the edit (armchair f_L-1b_054 is 155° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.57 m (needs ≤ 2.50 m)) | Armchair is 33° off the sofa axis (needs ≤30°) and its front is blocked by the other armchair; rotating to face 270° (towards the sofa) aligns it with the seating group and clears the front zone. |
| 15322 | 1 | retype_piece | f_L-1_021 | retype: display_cabinet is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m drawn run along the top wall is a long low cabinet; type it as a display cabinet to resolve the untyped finding. |
| 15323 | 1 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Shift the coffee table toward the window to clear the overlap with armchair f_L-1_071. |
| 15324 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)); 1 more kept | Armchair must face the sofa f_L-1b_042 which is to its west (180°); 270° was rejected as not facing the group. |
| 15325 | 1 | rotate_piece | f_L-1b_051 | acceptance: finding G3:f_L-1b_051 is still there after the edit (armchair f_L-1b_051 is 155° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.57 m (needs ≤ 2.50 m)) | Armchair is 33° off the sofa axis; rotate to face the sofa (270°) to align with the seating group. |
| 15327 | 1 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.42 m) | Moving sofa 0.59 m left to put its back on the left wall (x=7.79), clearing the off-wall finding and the plant blocking its front zone. |
| 15329 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room); 1 more kept | 40.5 m2 top-floor leisure room furnished as a living space; typing it 'living' resolves the room_type findings and makes the bench a valid piece. |
| 15330 | 1 | rotate_piece | f_L-1b_052 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)); 1 more kept | After sofa resize, sofa front is at 180°; armchair must align its front to the sofa's front axis (180°) to satisfy G3 ≤30°. |
| 15331 | 1 | rotate_piece | f_L-1b_051 | acceptance: finding G3:f_L-1b_051 is still there after the edit (armchair f_L-1b_051 is 65° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.57 m (needs ≤ 2.50 m)) | After sofa resize, sofa front is at 180°; armchair must align its front to the sofa's front axis (180°) to satisfy G3 ≤30°. |
| 15336 | 1 | move_piece | f_L-1b_045 | acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Moving sofa 0.3 m left (max drawn allowance) to reduce the off-wall gap from 0.59 m and clear the plant blocking its front zone. |
| 15337 | 1 | relayout_room | r_L-1b_salon | group checks: G9 r_L-1b_salon_kitchen: kitchen r_L-1b_salon_kitchen has no fridge (fridge) | Solver candidate 1 re-solves the seating group to fix armchair orientations (G3, F4) and the sofa back-on-wall issues (F3) in one pass. |
| 15339 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_033 has only 0.78m clearance behind (needs ≥0.81m); moving it 0.16m away from the wall behind increases clearance. |
| 15341 | 1 | move_piece | f_L1_019 | score: plausibility 58 -> 28 (G11 f_L1_018: sofa f_L1_018: its front use zone is not reached by a 0.60 m walkway from door d_L1_002; G11 f_L1_029: armchair f_L1_029: its front use zone is not reached by a 0.60 m walkway from door d_L1_002; G11 f_L1_032: armchair f_L1_032: its front use zone is not reached by a 0.60 m walkway from door d_L1_002; G11 f_L1_060: bookshelf f_L1_060: its front use zone is not reached by a 0.60 m walkway from door d_L1_002) | Shift sofa f_L1_019 left away from f_L1_018 to clear the blocked free zone in front of it (F6). |
| 15344 | 1 | move_piece | f_L-1b_071 | f_L-1b_042: no_overlap, f_L-1b_071: no_overlap | Side table f_L-1b_071 blocks the free zone in front of sofa f_L-1b_046; moving it 0.5m south clears the obstruction. |
| 15347 | 1 | move_piece | f_L1_038 | acceptance: finding G2:f_L1_038 is still there after the edit (coffee table f_L1_038 is not in front of the sofa and is 0.08 m from the sofa front, needs ≥ 0.30 m) | Move coffee table f_L1_038 south into the front zone of sofa f_L1_019 (G2: not in front of the sofa). |
| 15348 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room); 1 more kept | 40.5 m2 top-floor leisure room furnished as a living space; typing it 'living' resolves the room_type findings. |
| 15349 | 1 | move_piece | f_L-1b_071 | acceptance: finding F6:f_L-1b_046 is still there after the edit (sofa: the free zone in front of it is blocked by f_L-1b_071) | Side table f_L-1b_071 blocks the free zone in front of sofa f_L-1b_046; moving it east to [5.5,5.3] clears the sofa's front path without overlapping other pieces. |
| 15350 | 1 | move_piece | f_L1_038 | drawn_lock: f_L1_038: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.61 m) | Move coffee table f_L1_038 to the front zone of sofa f_L1_019, centered on its axis (G2). |
| 15352 | 1 | move_piece | f_L1_031 | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 8° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.70 m (needs ≤ 2.50 m)) | Move armchair f_L1_031 closer to the coffee table f_L1_023 to satisfy the G3 distance requirement (<= 2.50 m). |
| 15353 | 1 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | no_place: seating group re-solved around the drawn sofa f_L1_018: the solver places nothing and leaves the drawn pieces as drawn (seating: no candidate position fits the room) | Re-solve the drawn seating group around sofa f_L1_019 so the coffee table f_L1_038 lands in front of the sofa (G2). |
| 15355 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | max_tries: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 was edited 3 times in this round | Re-place AI pieces with solver candidate 2 to fix the coffee table in front of the sofa (G2) and the armchair alignment (G3). |
| 15357 | 1 | swap_model | f_L0_023 | asset_unusable: abo_B015IPNVFW is not used: audit removed | F41: the module-built wardrobe renders as a flat dark panel; swap to a real 6-door wardrobe model with visible doors (3.0x0.58x2.36, modern/minimal). |
| 15358 | 1 | swap_model | f_L0_031 | lower_quality: f_L0_031: abo_B07L1DX1LH is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | F304/F302: the ornate mid-century nightstand clashes with the modern room; swap to a minimal modern bedside table (0.49x0.43x0.49). |
| 15359 | 1 | swap_model | f_L0_032 | lower_quality: f_L0_032: abo_B07L1DX1LH is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | F306: the rustic distressed nightstand clashes with the modern room; swap to the same minimal modern bedside table as its pair. |
| 15360 | 1 | relayout_room | r_L1_teras | group checks: F8 f_L1_065: potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | Top-scored solver candidate re-scales the balcony set to fit the 19.7 m² terrace, resolving the plant's wall collision, floating and size findings. |
| 15362 | 1 | swap_model | f_L0_023 | asset_unusable: hssd_7094e30496b2735c235819e99c509769dc30502d is not used: audit removed | F41: the module-built wardrobe renders as a flat dark panel; swap to the Calypso 6-door wardrobe (2.66x0.61x2.23, minimal/modern) with visible doors. |
| 15363 | 1 | swap_model | f_L0_031 | lower_quality: f_L0_031: hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | F304/F302: the ornate mid-century nightstand clashes with the modern room; swap to the minimal modern Helen night stand (0.49x0.41x0.50). |
| 15364 | 1 | swap_model | f_L0_032 | lower_quality: f_L0_032: hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | F306: the rustic distressed nightstand clashes with the modern room; swap to the same minimal modern Helen night stand as its pair. |
| 15367 | 1 | swap_model | f_L0_023 | max_tries: f_L0_023 was edited 3 times in this round | F41: the module-built wardrobe renders as a flat dark panel; swap to the Mini Bar Open Wardrobe (3.0x0.61x2.37, industrial/modern) with visible doors and handles. |
| 15368 | 1 | swap_model | f_L0_031 | lower_quality: f_L0_031: abo_B07DBB7831 is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | F304/F302: the ornate mid-century nightstand clashes with the modern room; swap to the modern turned-leg nightstand (0.51x0.46x0.55, modern/scandinavian). |
| 15369 | 1 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Confirm the drawn coat closet as a wardrobe (vector geometry outranks AI bench reading); gives it a proper wall-hugging wardrobe form to clear F9/Q6/RC. |
| 15370 | 1 | swap_model | f_L0_032 | lower_quality: f_L0_032: abo_B07DBB7831 is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | F306: the rustic distressed nightstand clashes with the modern room; swap to the same modern turned-leg nightstand as its pair. |
| 15371 | 1 | retype_piece | f_L1_049 | retype: console_table is no candidate for f_L1_049 (0.60 x 0.25 m at [4.07, 7.74]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet | A shoe cabinet is unusual in a top-floor hall; a console table fits the hall context and clears the AI1 wrong_type finding. |
| 15372 | 1 | move_piece | f_L0_032 | max_tries: f_L0_032 was edited 3 times in this round | F9/G4: shift the nightstand 0.12 m away from the bed side to clear the 0.06 m² overlap and bring the gap to 0.0 m (≤ 0.30 m). |
| 15373 | 1 | swap_model | f_L-1_008 | built_in: f_L-1_008: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Replace the crude low-poly white box stove with a real detailed electric stove model (a:F265, a:F286). |
| 15374 | 1 | swap_model | f_L-1_067 | asset_unusable: gen_sink_kitchen_modern_2_b348b4dc is not used: audit removed | Replace the loud bright blue sink with a neutral modern sink that fits the wood/stone palette (a:F289). |
| 15376 | 1 | retype_piece | f_L1_027 | acceptance: finding RC:f_L1_027 is still there after the edit (f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | The drawn coat closet (hanging rail) is a wall-hugging storage piece; dresser is the size-table candidate that fits its 1.52x0.60 footprint and the hall, clearing F9/Q6/RC. |
| 15378 | 1 | swap_model | f_L-1_067 | pin_refused: f_L-1_067: gen_sink_kitchen_japandi_1_a61d924d: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Replace the loud bright blue sink with a neutral japandi sink that fits the wood/stone palette (a:F289). |
| 15382 | 1 | swap_model | f_L-1_067 | asset_unusable: gen_sink_kitchen_mediterranean_3_f6d72c7b is not used: audit removed | Replace the loud bright blue sink with a neutral mediterranean sink that fits the wood/stone palette (a:F289). |
| 15384 | 1 | place_group | r_L-1_mutfak | max_tries: r_L-1_mutfak was edited 3 times in this round | Re-solve the kitchen run with the I_fridge70 option so the fridge is a proper tall appliance instead of a flat panel in the run (a:F205, v:r1-v2:1/2/3). |
| 15385 | 1 | swap_model | f_L1_027 | max_tries: f_L1_027 was edited 3 times in this round | The current wardrobe renders as a massive blocky box dominating the narrow corridor; the Movian Indre 3-door (129x51x191cm) is a slimmer, lighter real product that fits the 1.52x0.60 footprint and reads as proper storage, clearing the wrong_model finding. |
| 15386 | 1 | swap_model | f_L0_029 | lower_quality: f_L0_029: abo_B07GF5DCK2 is rated 4.0 against 4.5 of the current model abo_B07JXXR83F: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Replace the crude trestle-leg desk with a scandinavian mid-century desk to match the room's design language (a:F320). |
| 15387 | 1 | swap_model | f_L0_037 | acceptance: pin_refused: f_L0_037: abo_B00XBC3J84: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the bright blue office chair with a neutral black low-back swivel chair that fits a stylish bedroom (a:F317). |
| 15390 | 1 | swap_model | f_L0_029 | acceptance: pin_refused: f_L0_029: abo_B01FK3FWNG: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the crude trestle-leg desk with a scandinavian/japandi retro desk to match the room's design language (a:F320). |
| 15391 | 1 | move_piece | f_L0_045 | score: plausibility 70 -> 54 (F3 f_L0_045: nightstand: its back is not on a wall (0.13 m off); G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: its back 0.32 m from the headboard line (needs ≤ 0.30 m)) | Nightstand f_L0_045 stands in front of window win_L0_004 (F80); shifting it 0.3 m left clears the window line. |
| 15392 | 1 | swap_model | f_L0_037 | asset_unusable: chinese_armchair is not used: audit pending | Replace the bright blue office chair with a neutral japandi armchair that fits a stylish bedroom (a:F317). |
| 15394 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Wardrobe f_L0_012 has only 0.66 m free in front (G13, needs ≥ 0.80 m); snapping its back flush to the top wall and shifting 0.2 m along it gains the missing front clearance. |
| 15395 | 1 | swap_model | f_L0_029 | acceptance: pin_refused: f_L0_029: abo_B075ZBVZST: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the crude trestle-leg desk with a scandinavian mid-century curved-wood desk to match the room's design language (a:F320). |
| 15396 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Wardrobe f_L0_012 has only 0.66 m free in front (G13, needs ≥ 0.80 m); snapping its back flush to the top wall and shifting 0.05 m along it gains the missing front clearance. |
| 15398 | 1 | move_piece | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Bed f_L0_020 has 0.53 m free on the right (G5, needs ≥ 0.60 m); shifting it 0.05 m toward the left wall gains the missing right-side clearance. |
| 15401 | 1 | move_piece | f_L0_020 | memory: the same edit was rejected in round 1: acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Bed f_L0_020 has 0.53 m free on the right (G5, needs ≥ 0.60 m); shifting it 0.05 m toward the left wall gains the missing right-side clearance. |
| 15402 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is built on the free right side of the head. |
| 15404 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.10 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Bed f_L0_020 has 0.53 m free on the right (G5, needs ≥ 0.60 m); shifting it 0.10 m toward the left wall gains the missing right-side clearance. |
| 15405 | 1 | set_room_type | r_L1_koridor_2 | no_change: r_L1_koridor_2 is already a hall | Re-assert as a top-floor circulation hall (stair, 15.3 m2, no entrance function) so the storage/entrance furniture is re-evaluated against a circulation hall, not an entrance hall. |
| 15406 | 1 | retype_piece | f_L1_028 | retype: wardrobe is no candidate for f_L1_028 (1.52 x 0.60 m at [12.61, 9.90]): the size table and the room / zone give bench, dresser | Confirm the drawn type: vector geometry (hanging rail with hangers) reads it as a coat closet/wardrobe, which fits its 1.52 x 0.60 m footprint and the hall context. |
| 15407 | 1 | retype_piece | f_L1_028 | acceptance: finding RC:f_L1_028 is still there after the edit (f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | The size table and hall zone give bench or dresser for 1.52 x 0.60 m; a dresser (coat closet with hanging rail) fits the drawn footprint and the circulation-hall context. |
| 15408 | 1 | move_piece | f_L0_020 | max_tries: f_L0_020 was edited 3 times in this round | Bed f_L0_020 has 0.53 m free on the right (G5, needs ≥ 0.60 m); snapping its headboard flush to the left wall gains the missing right-side clearance. |
| 15409 | 1 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008): re-solve the drawn sleeping_double group around the bed anchor so a nightstand is built on the free right side of the head. |
| 15410 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008): re-solve the drawn sleeping_double group around the bed anchor so a nightstand is built on the free right side of the head. |
| 15411 | 1 | swap_model | f_L-1_012 | asset_exists: no catalogue model 'kitchen_counter_090' | F235: f_L-1_012 top at 1.18 m over working height 0.97 m; swap to a standard 0.9 m worktop model. |
| 15417 | 1 | swap_model | f_L0_039 | acceptance: pin_refused: f_L0_039: abo_B07GFF11HV: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the crude low-poly placeholder with a generic green pot by a proper modern-minimal dark grey shoe cabinet (0.5 x 0.23 m, close to the 0.6 x 0.25 m footprint) that fits the neutral palette. |
| 15418 | 1 | swap_model | f_L0_039 | acceptance: pin_refused: f_L0_039: abo_B07K7YMBNY: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the crude low-poly placeholder with a green pot for a real solid-wood wild oak shoe cabinet (0.8 x 0.4 m, 1.0 m tall) that fits the neutral palette and the piece's 1.0 m height. |
| 15420 | 1 | swap_model | f_L0_039 | acceptance: pin_refused: f_L0_039: abo_B07GFDZWMS: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the crude low-poly placeholder with a green pot for a real dark grey 3-door shoe cabinet (0.75 x 0.25 m, 1.28 m tall) that fits the neutral palette. |
| 15428 | 1 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_modern_minimal_1_d5536003: a generated model (units guessed) while a real product of the type fits within the caps (3dwh_4736e8ccac82f4d690680828): the real model stays; swap to a real model of the type or use another tool | Argus flags the ornate bronze washbasin as a style clash with the modern reference; swap to a modern minimal model matching the clean-line palette. |
| 15429 | 1 | swap_model | f_L0_018 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Argus flags the toilet as a basic unstyled white box; swap to a sleek modern minimal model for the integrated look of the reference. |
| 15431 | 1 | move_group | r_L1_banyo.bathroom_set | drawn_lock: r_L1_banyo.bathroom_set: drawn pieces (f_L1_015, f_L1_021, f_L1_025) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the drawn bathroom set to the long free wall span s1 to clear the door swing at the washbasin (R3) and improve the tight clearances (AI1). |
| 15432 | 1 | swap_model | f_L0_003 | no_change: f_L0_003 already uses the model 3dwh_4736e8ccac82f4d690680828 | Code names this real washbasin product as fitting; swap the ornate bronze model to it to match the modern reference palette. |
| 15433 | 1 | swap_model | f_L0_018 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Swap the basic unstyled white-box toilet to a sleek modern minimal model for the integrated look of the reference. |
| 15434 | 1 | swap_model | f_L-1_026 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Swap generic floating white box washbasin for a sleek integrated modern sink (0.965x0.5m) to match the reference design. |
| 15436 | 1 | relayout_room | r_L1_banyo | no_place: r_L1_banyo relayout: no place passes the checks (no candidate position fits the room) | Re-solve the bathroom layout to clear the door swing at the washbasin (R3) and improve the tight clearances (AI1). |
| 15440 | 1 | swap_model | f_L0_018 | max_tries: f_L0_018 was edited 3 times in this round | Swap the basic unstyled white-box toilet to the sleek modern Caesar C1348 for the integrated look of the reference. |
| 15441 | 1 | swap_model | f_L-1_026 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Swap generic floating white box washbasin for a sleek Hudson Reed Sublime Vanity Unit & Basin (0.91x0.60m, minimal modern) to match the reference integrated design. |
| 15443 | 1 | fix_fixture | f_L1_015 | fixture_place: f_L1_015: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_004) | The door d_L1_004 swings into the washbasin on one hinge side (R3); move it up to 0.5 m to clear the swing. |
| 15444 | 1 | swap_model | f_L-1_026 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Swap generic floating white box washbasin for an Ikea Boholmen sink (0.96x0.50m, modern scandinavian) for a sleek integrated look matching the reference. |
| 15445 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall) | Shower faces a wall 0.10 m in front; turning it 180° to face 270° orients it into the room, resolving the orientation error. |
| 15446 | 1 | swap_model | f_L-1_026 | max_tries: f_L-1_026 was edited 3 times in this round | Swap generic floating white box washbasin for a generated modern minimal washbasin (0.64x0.48m) with a sleek integrated look to match the reference design. |
| 15872 | 2 | fix_fixture | f_L1_026 | fixture_size: f_L1_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 0.28 m front clearance; a 0.77 m deep model frees the required 0.53 m. (fixes a:F224) |
| 15874 | 2 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 2.00 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 20) is at z -0.40 m: use z 1.10 to 1.30 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: There is no frontal view of the entrance (+y) facade. (fixes a:F232) |
| 15875 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | score: plausibility 51 -> 39 (F1 f_L1_005: table_dining is not a piece of a bedroom room; F1 f_L1_017: sofa is not a piece of a bedroom room; F1 f_L1_020: sofa is not a piece of a bedroom room; F1 f_L1_023: table_coffee is not a piece of a bedroom room) | Argus: The top floor (L1) has no bedroom; the large room is typed 'other' but should be a bedroom. (fixes a:F237) |
| 15876 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | score: plausibility 68 -> 62 (F1 f_L1_009: table_dining is not a piece of a bedroom room; F1 f_L1_018: sofa is not a piece of a bedroom room; F1 f_L1_019: sofa is not a piece of a bedroom room; F1 f_L1_024: table_coffee is not a piece of a bedroom room) | Argus: Same as F237 for the second unit: the top floor room is typed 'other' and the floor has no bedroom. (fixes a:F238) |
| 15877 | 2 | set_front | f_L1_035 | has_front: f_L1_035 faces 270° already: rotate_piece turns it | Argus: The bench f_L1_035's front was read as 180 deg on its short side (an AI front error); the correct front is 270 deg, so its back stands on the wall and its front faces the room. (fixes a:F251) |
| 15878 | 2 | set_front | f_L1_037 | has_front: f_L1_037 faces 270° already: rotate_piece turns it | Argus: The bench f_L1_037's front was read as 0 deg on its short side (an AI front error); the correct front is 270 deg, so its back stands on the wall and its front faces the room. (fixes a:F252) |
| 15879 | 2 | swap_model | f_L-1_008 | built_in: f_L-1_008: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: The L-1 stove is a crude low-poly white box and its back is 0.06 m off the wall; swapping to a real appliance model fixes both the look and the gap. (fixes a:F265) |
| 15880 | 2 | swap_model | f_L1_039 | exists: no piece 'f_L1_039' in a room of the building | Argus: The current parametric model is a dated traditional table that clashes with the modern balcony setting; the suggested minimal/modern model fits the 0.70x0.70 m footprint and the outdoor context. (fixes a:F273) |
| 15881 | 2 | swap_model | f_L-1_038 | acceptance: pin_refused: f_L-1_038: 3dwh_1d0462a9ad318f16338f8396: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The table and chair cut each other by 0.034 m. Swapping to a slightly smaller, modern model (3.01 x 1.05 m) reduces the footprint and should resolve the collision with the adjacent chair. (fixes a:F274) |
| 15882 | 2 | swap_model | f_L0_015 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The current toilet model is a crude, low-poly box. The suggested model is a modern, detailed toilet that fits the 0.50 x 0.68 m footprint. (fixes a:F275) |
| 15883 | 2 | swap_model | f_L0_006 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The current washbasin is a crude, low-poly model. The suggested model is a modern, curved washbasin that fits the 1.00 x 0.55 m footprint. (fixes a:F276) |
| 15886 | 2 | swap_model | f_L-1_067 | acceptance: pin_refused: f_L-1_067: 3dwh_f7b6a98720563577a93662a2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The bright blue sink clashes with the neutral wood and stone palette of the kitchen. Swapping to a minimal/modern model with a neutral finish resolves the color clash. (fixes a:F289) |
| 15888 | 2 | swap_model | f_L-1_027 | asset_unusable: 3dwh_b27bb152311c2c1b3f509195 is not used: audit removed | Argus: The dining table is a plain, untextured slab that looks like a placeholder. Swapping to a neutral model with a realistic finish resolves the issue. (fixes a:F292) |
| 15891 | 2 | swap_model | f_L0_003 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The washbasin area has an ornate, bronze-colored grille that clashes with the modern bathroom style. Swapping to a minimal/modern model resolves the style clash. (fixes a:F299) |
| 15893 | 2 | swap_model | f_L0_031 | memory: the same edit was rejected in round 1: lower_quality: f_L0_031: abo_B07DBB7831 is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The washbasin is a kitchen-style utility sink with a built-in draining board, which is absurd for a bathroom. Swapping to a proper bathroom model resolves the issue. (fixes a:F302) |
| 15894 | 2 | swap_model | f_L0_032 | lower_quality: f_L0_032: hssd_xxxx562932e4x443cx47f7xaf2dxe60cabe20c9e is rated 3.0 against 4.0 of the current model abo_B07DVRLW48: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The current nightstand is a rustic, distressed piece that does not match the modern style of the room; swapping to a minimal/modern/scandinavian model of the same footprint restores a coherent set. (fixes a:F306) |
| 15895 | 2 | swap_model | f_L0_039 | acceptance: pin_refused: f_L0_039: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current shoe_cabinet is a crude, low-poly wooden stand with a generic green pot that looks like a placeholder; swapping to a minimal/modern shoe cabinet of the same footprint restores a functional, stylish piece. (fixes a:F309) |
| 15897 | 2 | swap_model | f_L0_010 | pin_refused: f_L0_010: gen_wardrobe_scandinavian_1_d0aa2dad: a generated model (units guessed) while a real product of the type fits within the caps (abo_B07B3XXD3P): the real model stays; swap to a real model of the type or use another tool | Argus: The current wardrobe is a pale, raw-wood piece that does not belong to a single coherent design language; swapping to a scandinavian/modern minimal wardrobe of a similar footprint restores a coherent set. (fixes a:F313) |
| 15901 | 2 | swap_model | f_L0_029 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L0_029: abo_B075ZBVZST: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current desk is a trestle-leg, utilitarian piece that looks like a placeholder; swapping to a scandinavian/japandi/modern minimal desk of a similar footprint restores a coherent set. (fixes a:F320) |
| 15904 | 2 | rotate_piece | f_L-1_072 | memory: the same edit was rejected in round 1: f_L-1_072: clearance_ok; score: plausibility 27 -> 17 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m ( | Turn the armchair to face into the room (90°) instead of the back of sofa f_L-1_054 (F4). |
| 15905 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back to left wall span s4 to fix F3 (back off wall) and clear the front zone blocked by plant f_L-1b_081 (F6) |
| 15908 | 2 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back to left wall span s4 (further along, away from the door) to fix F3 (back off wall) and clear the front zone blocked by plant f_L-1b_081 (F6) |
| 15909 | 2 | complete_group | r_L-1b_salon.seating | acceptance: finding G1:f_L-1b_042 is still there after the edit (sofa f_L-1b_042 has no TV unit opposite) | Sofa f_L-1b_042 is 2.24 m off a wall and missing its coffee table/TV unit; completing the seating group re-solves the anchor against a wall and adds the missing members. |
| 15910 | 2 | rotate_piece | f_L-1_072 | f_L-1_072: inside_room, f_L-1_072: no_overlap | Turn the armchair 45° so it faces the seating group and coffee table f_L-1_074 instead of the back of sofa f_L-1_054 (F4). |
| 15912 | 2 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.53 m) | Move sofa f_L-1b_045 to the left wall (span s4) to place its back on the wall (fixing F3) and clear the front zone blocked by plant f_L-1b_081 (fixing F6) |
| 15914 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Move sofa f_L-1b_045 to the left wall (span s4) to place its back on the wall (fixing F3) and clear the front zone blocked by plant f_L-1b_081 (fixing F6) |
| 15915 | 2 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, f_L-1_072: inside_room, f_L-1_072: no_overlap, score: plausibility 27 -> 7 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 91° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn the armchair 135° so it faces the seating group and coffee table f_L-1_074 instead of the back of sofa f_L-1_054 (F4). |
| 15917 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Move sofa f_L-1b_045 to the left wall (span s4) to place its back on the wall (fixing F3) and clear the front zone blocked by plant f_L-1b_081 (fixing F6) |
| 15920 | 2 | move_piece | f_L-1_074 | memory: the same edit was rejected in round 1: f_L-1_072: no_overlap | Move the coffee table left to clear the 0.12 m² overlap with armchair f_L-1_069 (F9). |
| 15922 | 2 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | Move the coffee table left and toward the window to clear the 0.12 m² overlap with armchair f_L-1_069 (F9). |
| 15924 | 2 | move_piece | f_L-1_074 | acceptance: finding F9:f_L-1_074 is still there after the edit (table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.11 m²) | Move the coffee table toward the window to clear the 0.12 m² overlap with armchair f_L-1_069 (F9). |
| 15926 | 2 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move the coffee table right, away from armchair f_L-1_069, to clear the 0.12 m² overlap (F9). |
| 15927 | 2 | mark_not_furniture | f_L-1_021 | no_crop: f_L-1_021 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/cam_r_L-1_salon_1_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | the 5.54 m long thin strip is a wall cut / dimension outline, not furniture: no standard furniture type fits its dimensions in a salon |
| 15929 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017); 3 more kept | Re-solve seating and dining groups to fix sofa clearance blockage, coffee table alignment, armchair distance/angle, and dining chair clearance. |
| 15930 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017); 3 more kept | Try solver candidate 2 to re-solve seating and dining groups, fixing sofa clearance, coffee table alignment, armchair distance, and dining chair clearance. |
| 15931 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | max_tries: r_L1_oyun_aktivite_ve_dinlenme_odasi was edited 3 times in this round | Try solver candidate 3 to re-solve seating and dining groups, fixing sofa clearance, coffee table alignment, armchair distance, and dining chair clearance. |
| 15935 | 2 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Reposition drawn groups (bed, wardrobe, desk) to clear the G13 wardrobe front clearance and G5 bed-side clearances that small moves cannot fix. |
| 15939 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 is already a living | Room is a game/activity/relaxation room with sofas, dining and coffee tables: living fits its area, furniture and doors (a:F238). |
| 15940 | 2 | rotate_piece | f_L1_037 | score: plausibility 68 -> 58 (F4 f_L1_037: bench faces a wall 0.00 m in front of it) | Bench's back stands on the wall at y=7.44, so its front must face into the room (90°), not along the long side (a:F252). |
| 15944 | 2 | move_piece | f_L1_037 | score: plausibility 68 -> 58 (F8 f_L1_037: bench stands alone in the room (no wall, no bed_double / bed_single / bunk_bed within 0.8 m)) | Pull the bench off the wall so its front (270°) faces open floor instead of the wall, keeping it in its drawn spot (a:F252). |
| 15945 | 2 | retype_piece | f_L1_037 | max_tries: f_L1_037 was edited 3 times in this round | A 1.4×0.45 m low table against the wall fits a console_table, which is a valid living-room piece (closes F1/G14 and the bench's F8/F4 orientation conflict, a:F252). |
| 15949 | 2 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 9° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.52 m (needs ≤ 2.50 m)) | Bring the armchair closer to the coffee table (2.73 m → ~2.5 m) and align its front with the table to clear G3 (c:G3:f_L1_032, a:F94). |
| 15951 | 2 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 10° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.53 m (needs ≤ 2.50 m)) | Nudge the armchair 5 cm closer so it sits within 2.50 m of the coffee table, clearing G3 (c:G3:f_L1_032, a:F94). |
| 15953 | 2 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | G9 says kitchen has no fridge; the I_fridge70 option should place a proper tall fridge unit in the run |
| 15954 | 2 | move_piece | f_L1_032 | acceptance: finding G3:f_L1_032 is still there after the edit (armchair f_L1_032 is 11° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.54 m (needs ≤ 2.50 m)) | Move the armchair to 2.45 m from the coffee table (≤ 2.50 m) to clear G3 (c:G3:f_L1_032, a:F94). |
| 15956 | 2 | swap_model | f_L-1_067 | pin_refused: f_L-1_067: gen_sink_kitchen_japandi_6_2ccc7ce8: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | The bright blue sink clashes with the neutral wood and stone palette; japandi style with minimal/modern tags should match the kitchen's neutral palette |
| 15957 | 2 | swap_model | f_L-1_008 | built_in: f_L-1_008: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | The crude low-poly white box stove needs a proper modern cooktop model with burners and detail |
| 15959 | 2 | move_group | r_L-1_mutfak.kitchen_run | drawn_lock: r_L-1_mutfak.kitchen_run: drawn pieces (f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | G8: kitchen aisle 0.55m in front of f_L-1_002 needs ≥0.90m; moving the run to the bottom wall span s0 (2.94m) should give proper clearance |
| 15962 | 2 | relayout_room | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_place: r_L-1_mutfak relayout: no place passes the checks (dining: no place passes the checks) | G8 aisle 0.55m needs ≥0.90m; solver candidate 1 should re-place AI pieces to fix clearance |
| 15963 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve the sleeping_double and storage groups around their drawn anchors to open the wardrobe front clearance (0.17 m) and the bed side clearances (0.37/0.52 m). |
| 15964 | 2 | fix_fixture | f_L-1_001 | fixture_place: f_L-1_001: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_003) | Door d_L-1_003 swings into f_L-1_001 on one hinge side; need to move the counter slightly to clear the door swing |
| 15968 | 2 | swap_model | f_L-1_067 | asset_unusable: gen_sink_kitchen_modern_1_5b97156d is not used: audit removed | The bright blue sink clashes with the neutral palette; modern minimal style should match the kitchen's wood and stone tones |
| 15976 | 2 | swap_model | f_L1_027 | no_change: f_L1_027 already uses the model abo_B07GFS1VB6 | Replace the blocky placeholder wardrobe with the real Movian Kolva sliding 2-door wardrobe (1.80x0.61x1.97 m, light oak) to address the wrong_model finding. |
| 15978 | 2 | move_piece | f_L0_045 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | slide nightstand up the right wall to clear the window band (sill 0.20 m) while staying beside the bed head |
| 15986 | 2 | swap_model | f_L1_043 | acceptance: pin_refused: f_L1_043: hssd_e9393fb84e42e59d93ba261275daf119df0cde2e: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Round-1 swap to abo_B07M6PKC6B left the P7 below-library finding; try the Band Dining Table (0.797x0.797, minimal/modern) which fits the 0.7x0.7 outdoor table footprint within tolerance. |
| 15989 | 2 | swap_model | f_L1_043 | asset_unusable: round_wooden_table_02 is not used: audit pending | hssd Band table failed the fit rules; try polyhaven Round Wooden Table 02 (0.796x0.796, CC0) which fits the 0.7x0.7 outdoor table footprint. |
| 15993 | 2 | swap_model | f_L1_043 | acceptance: pin_refused: f_L1_043: 3dwh_61d3ec6b31b39c2256ef4df4: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Try IKEA GAMLARED (0.85x0.85, modern/scandinavian) for the 0.7x0.7 outdoor table; prior abo and hssd models failed the fit rules. |
| 15998 | 2 | set_exterior | exterior:ground,site,sun | sun: azimuth 200 degrees (compass; 200 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Add warm sun, landscaping (hedge, trees, path) and lawn to replace the flat grey overcast massing study (a:F341, a:F340, a:F344, a:F345). |
| 15999 | 2 | set_terrain | set_terrain | score: the level findings rise from 1 to 13, L4 lm_002: level mark '37.00' (lm_002, ground_finished) reads -6.00 m; the ground there is built at -4.71 m (1.29 m apart), L4 lm_003: level mark '40.00' (lm_003, ground_finished) reads -3.00 m; the ground there is built at -2.42 m (0.58 m apart), L4 lm_005: level mark '40.00' (lm_005, ground_finished) reads -3.00 m; the ground there is built at -1.72 m (1.28 m apart), L4 lm_006: level mark '43.00' (lm_006, ground_finished) reads +0.00 m; the ground there is built at +0.42 m (0.42 m apart), L4 lm_007: level mark '40.00' (lm_007, ground_finished) reads -3.00 m; the ground there is built at -3.91 m (0.91 m apart) | Replace the steep 1:0.3 slope with a planar terrain model so no slope steeper than 1:3 remains (c:L6:terrain). |
| 16003 | 2 | swap_model | f_L1_043 | max_tries: f_L1_043 was edited 3 times in this round | Try Rivet Federal Mid-Century Modern Drop Leaf table (0.843x0.812, minimal/modern) for the 0.7x0.7 outdoor table; prior abo/hssd/3dwh models failed the fit rules. |
| 16006 | 2 | set_exterior | exterior:sun | sun: azimuth 180 degrees (compass; 180 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Add warm sun on the main (+y) facade side to replace the flat grey overcast lighting (a:F341, a:F340, a:F344, a:F345). |
| 16009 | 2 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Door d_L-1_001 swings into the washbasin on one hinge side; nudge the fixture to clear the door swing. |
| 16011 | 2 | set_exterior | exterior:sun | acceptance: finding D3:w_L0_001 is still there after the edit (the edit does not change what the finding is about (the override sets sun; the cause site needs site or ground); Argus: missing layer: warm light. The entire fa) | Add warm sun on the main (+y) facade side to replace the flat grey overcast lighting (a:F341, a:F340, a:F344, a:F345). |
| 16458 | 3 | set_camera | r_L1_koridor | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: The view is a 1/5 close-up of a corner and a wardrobe. Re-aiming the camera at the hall's defining pieces is the direct fix. (fixes a:F326) |
| 16459 | 3 | swap_model | f_L1_023 | asset_unusable: hssd_24948d656ee551402efa257e451d587431a972b3 is not used: audit removed | Argus: The dark-wood coffee table is a third, clashing material. Swapping it for a light minimal/modern model (1.03 x 0.62 m, close to the current 1.03 x 0.69 m) removes the clash. (fixes a:F328) |
| 16460 | 3 | swap_model | f_L1_040 | exists: no piece 'f_L1_040' in a room of the building | Argus: The black molded plastic chair clashes with the traditional wooden table; swapping to a scandinavian chair model coordinates the set. (fixes a:F337) |
| 16461 | 3 | swap_model | f_L1_041 | exists: no piece 'f_L1_041' in a room of the building | Argus: The two chairs are completely different models; swapping the second to match the first creates a coherent set. (fixes a:F339) |
| 16462 | 3 | set_exterior | exterior:sun | sun: azimuth 135 degrees (compass; 135 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Argus: The render is a flat, grey-box massing study with dead, overcast lighting; setting a warm sun angle fixes the lighting. (fixes a:F340) |
| 16463 | 3 | set_camera | ext_3 | eye height 5.56 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The view is a tight, low-angle crop that hides the main facade; repositioning the camera to frame the house as a whole fixes the composition. (fixes a:F342) |
| 16464 | 3 | retype_piece | f_L-1_085 | retype: sideboard is no candidate for f_L-1_085 (0.30 x 0.20 m at [2.97, 11.70]): the size table and the room / zone give floor_lamp, potted_plant | Argus: Two drawn furniture pieces are untyped; retyping them to a known model (sideboard) allows them to be built. (fixes a:F347) |
| 16465 | 3 | set_camera | r_L1_teras | show: no free camera point of r_L1_teras shows f_L1_042 (f_L1_042 not in r_L1_teras: name its pieces, doors or windows) | Argus: The potted plant is listed for the balcony but not visible; pointing the balcony camera at it frames the room's content. (fixes a:F359) |
| 16467 | 3 | swap_model | f_L1_043 | no_change: f_L1_043 already uses the model abo_B07M6PKC6B | Argus: The piece is 0.70 x 0.70 m. The model abo_B07M6PKC6B is 0.75 x 0.75 m, a very close library fit, replacing the parametric mesh. (fixes a:F436) |
| 16468 | 3 | swap_model | f_L-1_056 | asset_unusable: hssd_df8abd46ef3dd6017f6863558381655f1510d275 is not used: audit removed | Argus: The current model is a plain white block. The suggested model hssd_df8abd46ef3dd6017f6863558381655f1510d275 is a minimal/modern bathtub of similar size (1.81 x 0.80 m) that should have better detailing. (fixes a:F440) |
| 16469 | 3 | swap_model | f_L-1_026 | memory: the same edit was rejected in round 1: asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The current model is a generic floating white box. The suggested model 3dwh_9314d5619fde2de825a4a2a1 is a minimal/modern washbasin of similar size (0.96 x 0.50 m) that should look more integrated. (fixes a:F441) |
| 16470 | 3 | swap_model | f_L0_018 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The current model is a basic unstyled white box. The suggested model objaverse_5b18711616054a44b025d9272b745a6a is a modern minimal toilet of similar size (0.48 x 0.68 m) that should look more integrated. (fixes a:F447) |
| 16471 | 3 | swap_model | f_L1_042 | exists: no piece 'f_L1_042' in a room of the building | Argus: The current model is a crude placeholder; the suggested minimal/modern model at 0.86 m is a better fit for a balcony. (fixes a:F449) |
| 16472 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room); 1 more kept | Argus: The top-floor room is typed 'other' (40.5 m2) and furnished as a living room (sofa, armchairs, coffee table, dining table, bookshelf). The documents label it 'Oyun Aktivite Ve Dinlenme Odası' (game/activity/relaxation room). A 40 m2 room on (fixes a:N123) |
| 16473 | 3 | place_group | r_L1_teras | room_type: a seating group does not belong in a balcony room (groups.yaml room types: living) | Argus: The top-floor balcony (19.7 m2) is furnished with a dining table and chairs, i.e. an outdoor dining set. A 19.7 m2 terrace is a proper outdoor living space; the documents draw it as a full terrace, not a narrow balcony. The furniture set is (fixes a:N124) |
| 16474 | 3 | retype_piece | f_L1_001 | retype: console_table is no candidate for f_L1_001 (2.71 x 2.10 m at [9.11, 8.64]): the size table and the room / zone give stair | Argus: The top-floor hall (15.3 m2) contains a shoe_cabinet and a wardrobe. A 15.3 m2 hall on the top floor is not an entrance hall; shoe cabinets belong at the entrance (ground floor). The wardrobe in a hall is also unusual. The hall is oversized (fixes a:N125) |
| 16475 | 3 | relayout_room | r_L1_banyo | no_place: r_L1_banyo relayout: no place passes the checks (no candidate position fits the room) | Argus: The top-floor bathroom (5.0 m2) contains a bathtub, toilet and washbasin. A 5.0 m2 bathroom with a bathtub is tight but possible. However, the render (cam_r_L1_banyo_1) scores 1/5, suggesting the layout is poor. The bathroom is also duplica (fixes a:N126) |
| 16476 | 3 | set_material | wet_walls | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: lesson (lesson:UL66:L0): The bathroom walls are a flat, unaccented white tile with no muted accent and no magazine-style design; the only feature is a decorative grille window, not a colour scheme. (fixes a:N127) |
| 16477 | 3 | place_group | r_L0_banyo | no_change: r_L0_banyo already has its bathroom_set r_L0_banyo.bathroom_set (anchor f_L0_018, members f_L0_003, f_L0_025): nothing missing, never a second set | Argus: lesson (lesson:UL68:L0): In cam_r_L0_banyo_1 the washbasin has no mirror over or beside it (only the decorative grille window); the e_banyo does have a mirror, so the main banyo is missing one. (fixes a:N128) |
| 16478 | 3 | retype_piece | f_L-1_057 | no_change: f_L-1_057 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_057 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays (fixes a:c128) |
| 16479 | 3 | retype_piece | f_L-1_059 | no_change: f_L-1_059 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_059 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays (fixes a:c129) |
| 16480 | 3 | retype_piece | f_L-1_064 | no_change: f_L-1_064 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_064 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays (fixes a:c130) |
| 16481 | 3 | retype_piece | f_L-1_066 | no_change: f_L-1_066 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_066 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays (fixes a:c131) |
| 16482 | 3 | retype_piece | f_L-1_075 | no_change: f_L-1_075 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_075 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c132) |
| 16483 | 3 | retype_piece | f_L-1_076 | no_change: f_L-1_076 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_076 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c133) |
| 16484 | 3 | retype_piece | f_L-1_077 | no_change: f_L-1_077 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_077 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c134) |
| 16487 | 3 | complete_group | r_L-1b_salon.seating | memory: the same edit was rejected in round 2: acceptance: finding G1:f_L-1b_042 is still there after the edit (sofa f_L-1b_042 has no TV unit opposite) | Sofa f_L-1b_042 is 2.24 m off a wall and missing its coffee table/TV unit; completing the seating group re-solves the anchor against a wall and adds the missing members. |
| 16490 | 3 | complete_group | r_L-1b_salon_2.seating | acceptance: finding G3:f_L-1b_053 is still there after the edit (armchair f_L-1b_053 is 90° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.43 m (needs ≤ 2.50 m)); 3 more kept | Complete the seating group around the drawn sofa f_L-1b_041: adds the missing coffee table (G2) and re-solves the armchairs so they face the sofa (G3/F4) with clear front zones (F6), and seats the sofa against a wall (F3). |
| 16491 | 3 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.80 m) | Move the coffee table 0.5 m away from armchair f_L-1_071 to resolve the 0.12 m² overlap collision. |
| 16494 | 3 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 1: drawn_lock: f_L-1_065: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | G12: pull the floor lamp 0.6 m off the window wall so it no longer stands in front of window win_L-1_002. |
| 16495 | 3 | move_piece | f_L-1_050 | drawn_lock: f_L-1_050: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.60 m) | G11: shift the armchair 0.6 m toward the door side so a 0.60 m walkway from door o_L-1_002 reaches its front use zone. |
| 16497 | 3 | move_piece | f_L-1_065 | memory: the same edit was rejected in round 1: f_L-1_054: no_overlap; f_L-1_065: no_overlap | G12: nudge the floor lamp 0.3 m off the window wall (max drawn allowance) so it no longer stands in front of window win_L-1_002. |
| 16498 | 3 | move_piece | f_L-1_050 | memory: the same edit was rejected in round 1: f_L-1_050: no_overlap; f_L-1_054: clearance_ok; f_L-1_088: no_overlap; score: plausibility 27 -> 7 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050; F9 f_L-1_088: table_coffee f_L-1_088 overlaps armchair f_L-1_050 by 0.09 m²) | G11: shift the armchair 0.3 m toward the door side (max drawn allowance) to open a 0.60 m walkway from door o_L-1_002 to its front use zone. |
| 16500 | 3 | relayout_room | r_L-1b_salon_2 | group checks: G9 r_L-1b_salon_2_kitchen: kitchen r_L-1b_salon_2_kitchen has no fridge (fridge) | Re-solve the seating group around the drawn sofa anchor so the armchairs face the sofa (G3/F4) with clear front zones (F6) and the sofa seats against a wall (F3). |
| 16502 | 3 | move_piece | f_L-1b_071 | acceptance: finding F6:f_L-1b_046 is still there after the edit (sofa: the free zone in front of it is blocked by f_L-1b_071) | Side table f_L-1b_071 blocks the free zone in front of sofa f_L-1b_046; moving it to the side of the sofa clears the obstruction. |
| 16504 | 3 | move_piece | f_L-1b_071 | f_L-1b_046: no_overlap, f_L-1b_071: no_overlap | Side table f_L-1b_071 still blocks the free zone in front of sofa f_L-1b_046; moving it further to the side of the sofa clears the obstruction. |
| 16506 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_033 has only 0.78 m behind it (needs ≥ 0.81 m); moving it slightly away from the piece behind increases the clearance. |
| 16508 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_033 has only 0.78 m behind it (needs ≥ 0.81 m); moving it further away from the table increases the pullout clearance. |
| 16512 | 3 | move_piece | f_L-1b_026 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The dining table is too close to the wall behind chair f_L-1b_033 (0.78 m pullout, needs 0.81 m); moving the table slightly away from that wall increases the clearance. |
| 16514 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room); 1 more kept | 40.5 m2 top-floor leisure room furnished as a living room (sofas, dining, bookshelf); 'other' is wrong (a:F237, a:N123). |
| 16516 | 3 | move_piece | f_L1_038 | acceptance: finding G2:f_L1_038 is still there after the edit (coffee table f_L1_038 is not in front of the sofa and is 0.14 m from the sofa front, needs ≥ 0.30 m) | Pull the coffee table off the wall (it cut w_L1_002) and into the open zone in front of sofa f_L1_019 to clear G2/F93. |
| 16517 | 3 | move_piece | f_L1_038 | drawn_lock: f_L1_038: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.88 m) | Place the coffee table in the open zone in front of sofa f_L1_019 (≥0.3 m from its front, on its axis) to clear G2/F93. |
| 16518 | 3 | swap_model | f_L1_005 | lower_quality: f_L1_005: 3dwh_61d3ec6b31b39c2256ef4df4 is rated 3.0 against 4.0 of the current model abo_B07M6PKC6B: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Dining table absent from render (a:D3:f_L1_005): swap to a real round dining table model of matching 0.85 m size. |
| 16519 | 3 | swap_model | f_L1_023 | no_change: f_L1_023 already uses the model hssd_7025cd14a948f491902ef12724f0fe6e4ce672af | Heavy dark-wood coffee table clashes with light floor and brown sofas (a:F328): swap to a lighter mid-century modern coffee table of matching size. |
| 16520 | 3 | swap_model | f_L1_020 | lower_quality: f_L1_020: 3dwh_73a3f2fd339beec5aabd5ed6 is rated 3.0 against 5.0 of the current model abo_B07BWJCBY2: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | Two sofas are different models (a:Q5:f_L1_020): swap to a matching 2.1 m minimal scandinavian sofa to coordinate the set. |
| 16521 | 3 | move_piece | f_L1_038 | acceptance: finding G2:f_L1_038 is still there after the edit (coffee table f_L1_038 is not in front of the sofa) | Snap the coffee table's back to the wall span in front of sofa f_L1_019 (wall snap allows up to 1.2 m) so it sits in front of the sofa and clears G2/F93. |
| 16523 | 3 | move_piece | f_L1_020 | score: plausibility 51 -> 11 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_035: console_table f_L1_035: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Sofa f_L1_020's free zone in front is blocked by f_L1_017 (c:F6:f_L1_020): shift 0.3 m away to open the front zone. |
| 16524 | 3 | move_piece | f_L1_020 | acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017) | Revert the rejected 0.3 m shift of sofa f_L1_020 back to its drawn position. |
| 16525 | 3 | move_piece | f_L1_038 | max_tries: f_L1_038 was edited 3 times in this round | Snap the coffee table's back to the wall span directly in front of sofa f_L1_019 (offset 0.3 m from the span start, on the sofa's axis) so it sits in front of the sofa and clears G2/F93. |
| 16529 | 3 | move_piece | f_L1_036 | drawn_lock: f_L1_036: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.50 m) | Coffee table f_L1_036 is not in front of sofa f_L1_020 (c:G2:f_L1_036): move it 0.6 m into the sofa's front zone. |
| 16532 | 3 | move_piece | f_L0_010 | f_L0_010: inside_room (outline: wardrobe reaches 0.21 m² through the room outline, up to 0.146 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 60 (F3 f_L0_010: wardrobe: its back is not on a wall (0.15 m off); F9 f_L0_010: wardrobe reaches 0.21 m² through the room outline, up to 0.146 m deep) | Move wardrobe 0.15m towards the wall (y+) to increase front clearance from 0.66m to 0.81m, satisfying G13 >= 0.80m. |
| 16533 | 3 | move_piece | f_L0_019 | acceptance: finding G5:f_L0_019 is still there after the edit (bed_double f_L0_019: 0.56 m free along the right side, needs ≥ 0.60 m) | Move bed 0.05m towards the right wall (x+) to increase left side clearance from 0.53m to 0.58m and right side clearance from 0.56m to 0.61m, satisfying G5 >= 0.60m on the right and improving the left. |
| 16534 | 3 | move_piece | f_L1_036 | acceptance: finding G2:f_L1_036 is still there after the edit (coffee table f_L1_036 is not in front of the sofa) | Coffee table f_L1_036 is not in front of sofa f_L1_020 (c:G2:f_L1_036): shift 0.3 m along the wall toward the sofa's front zone. |
| 16535 | 3 | move_piece | f_L1_007 | score: plausibility 51 -> 41 (F4 f_L1_007: chair does not face its group (f_L1_005); G6 f_L1_007: chair f_L1_007 is 73° off the table f_L1_005 (needs ≤ 45°)) | Chair f_L1_007 has only 0.71 m behind it, needs 0.81 m (c:G6:f_L1_007): shift 0.3 m away from the wall behind. |
| 16540 | 3 | swap_model | f_L0_029 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L0_029: abo_B01FK3FWNG: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the crude trestle-leg desk with a scandinavian/japandi desk to match the room's design language (a:F320). |
| 16542 | 3 | move_piece | f_L0_012 | snap: f_L0_012: no free place on wall w_L0_015 (doors, windows, at most 1.2 m from the drawn place) | c:G13:f_L0_012, a:F81: move wardrobe f_L0_012 to wall w_L0_015 to gain ≥0.80 m clearance in front |
| 16544 | 3 | swap_model | f_L-1_008 | memory: the same edit was rejected in round 1: built_in: f_L-1_008: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Real CC0 electric stove model replaces the crude low-poly white box so the stove reads as a real appliance (a:F265, a:F286). |
| 16545 | 3 | swap_model | f_L-1_067 | memory: the same edit was rejected in round 1: asset_unusable: gen_sink_kitchen_modern_2_b348b4dc is not used: audit removed | Neutral modern sink model replaces the loud bright blue sink that clashes with the wood/stone palette (a:F289). |
| 16546 | 3 | swap_model | f_L-1_003 | asset_type: electric_stove is a stove model, not a kitchen_counter | Test whether any library model can bring the counter top down to working height (a:F234). |
| 16547 | 3 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 2: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Kitchen has no fridge (a:F205); complete the run with a 70 cm fridge. |
| 16548 | 3 | move_group | r_L-1_mutfak.kitchen_run | memory: the same edit was rejected in round 2: drawn_lock: r_L-1_mutfak.kitchen_run: drawn pieces (f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Widen the 0.55 m aisle in front of f_L-1_002 to the required 0.90 m (a:F65). |
| 16550 | 3 | swap_model | f_L0_029 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L0_029: abo_B075ZBVZST: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the crude trestle-leg desk with a scandinavian/japandi mid-century desk to match the room's design language (a:F320). |
| 16553 | 3 | swap_model | f_L0_029 | memory: the same edit was rejected in round 1: lower_quality: f_L0_029: abo_B07GF5DCK2 is rated 4.0 against 4.5 of the current model abo_B07JXXR83F: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Replace the crude trestle-leg desk with a scandinavian mid-century desk to match the room's design language (a:F320). |
| 16555 | 3 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | c:G13:f_L0_012, a:F81: move wardrobe f_L0_012 to wall w_L0_004 to gain ≥0.80 m clearance in front |
| 16558 | 3 | move_piece | f_L0_011 | snap: f_L0_011: no free place on wall w_L0_016 (doors, windows, at most 1.2 m from the drawn place) | Slide the wardrobe along the right wall toward the corner to open the 0.80 m front clearance blocked by the desk group (G13). |
| 16559 | 3 | move_piece | f_L0_020 | score: plausibility 70 -> 54 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free left side of the head (0.93 m free); G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (2.86 m free); G4 f_L0_044: nightstand f_L0_044 of bed_double f_L0_020: its back 2.57 m from the headboard line (needs ≤ 0.30 m); its front 180° off the bed's front; G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: 0.42 m from the bed side (needs ≤ 0.30 m); its back 2.57 m from the headboard line (needs ≤ 0.30 m); its front 180° off the bed's front) | c:G5:f_L0_020, c:G5:f_L0_020#2, a:F79: move bed f_L0_020 to wall w_L0_015 to gain ≥0.60 m clearance on both sides |
| 16562 | 3 | move_piece | f_L0_020 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 57 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.06 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.38 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.14 m from the bed side (needs ≤ 0.30 m); G5 f_L0_020: bed_double f_L0_020: 0.38 m free along the right side, needs ≥ 0.60 m) | c:G5:f_L0_020, c:G5:f_L0_020#2, a:F79: shift bed f_L0_020 toward the window to gain ≥0.60 m clearance on both sides |
| 16563 | 3 | move_piece | f_L0_011 | drawn_lock: f_L0_011: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.75 m) | Slide the wardrobe along the bottom wall toward the corner to open the 0.80 m front clearance blocked by the desk group (G13). |
| 16564 | 3 | move_piece | f_L0_020 | score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.12 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | c:G5:f_L0_020, c:G5:f_L0_020#2, a:F79: shift bed f_L0_020 toward the left wall to gain ≥0.60 m clearance on the right side |
| 16565 | 3 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Slide the bed 0.3 m toward the left wall to open the right-side clearance to 0.60 m and room for a nightstand (G5, G4). |
| 16566 | 3 | swap_model | f_L1_027 | lower_quality: f_L1_027: hssd_3033be75f2ac15885e8f4813dc55e168af09e91f is rated 3.0 against 5.0 of the current model abo_B07GFS1VB6: a swap never takes a lower-rated model; choose one rated at least 4.8, or fix the view (camera, light) instead | a:F99: the current wardrobe model reads as a massive blocky box; the Oscar 3-door wardrobe (1.52 x 0.623 m, modern/minimal) matches the drawn footprint and gives a refined, panelled front instead of a plain box. |
| 16568 | 3 | move_piece | f_L0_012 | snap: f_L0_012: no free place on wall w_L0_016 (doors, windows, at most 1.2 m from the drawn place) | c:G13:f_L0_012, a:F81: move wardrobe f_L0_012 to wall w_L0_016 to gain ≥0.80 m clearance in front |
| 16570 | 3 | move_piece | f_L0_012 | max_tries: f_L0_012 was edited 3 times in this round | c:G13:f_L0_012, a:F81: shift wardrobe f_L0_012 left along its wall to clear the front from the desk cluster |
| 16571 | 3 | move_group | r_L0_yatak_odasi_4.work | drawn_lock: r_L0_yatak_odasi_4.work: drawn pieces (f_L0_028, f_L0_036) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Move the desk group to the free left wall span to clear the wardrobe's front (G13) and free the right side of the bed. |
| 16573 | 3 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m) | Slide the wardrobe 0.3 m along the bottom wall toward the corner to open the front clearance blocked by the desk (G13). |
| 16574 | 3 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | Swap to a narrower 1.45 m bed frame to open the bed's side clearances (G5, F86). |
| 16577 | 3 | move_piece | f_L0_022 | f_L0_022: inside_room (outline: bed_double reaches 0.46 m² through the room outline, up to 0.298 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 67 -> 14 (F3 f_L0_022: bed_double: the headboard stands in the room (0.30 m off); F9 f_L0_022: bed_double reaches 0.46 m² through the room outline, up to 0.298 m deep; G4 f_L0_022: bed_double f_L0_022: no nightstand on the free left side of the head (0.52 m free); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Slide the bed 0.3 m toward the right wall to open the left-side clearance to 0.60 m (G5). |
| 16579 | 3 | move_piece | f_L0_011 | memory: the same edit was rejected in round 3: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m) | Slide the wardrobe 0.3 m along the bottom wall toward the corner to open the front clearance blocked by the desk (G13). |
| 16585 | 3 | relayout_room | r_L1_teras | memory: the same edit was rejected in round 1: group checks: F8 f_L1_065: potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | Relayout with the best-scored candidate to give the 19.7 m² terrace a properly sized outdoor set instead of the too-small dining set. |
| 16598 | 3 | set_camera | r_L1_banyo | cam_r_L1_banyo_1 is 0.35 m from the door d_L1_004 (at least 0.6 m), cam_r_L1_banyo_1: eye height -1.45 m (wanted 1.2-1.6 m) | The camera is stuck high (4.4 m) and close to the tub rim; a low eye-level pose from the far corner with a 24 mm lens shows the whole room and all three fixtures. |
| 16602 | 3 | set_camera | r_L1_banyo | max_tries: r_L1_banyo was edited 3 times in this round | Low eye-level pose from the far corner with a 24 mm lens to show the whole room and all three fixtures instead of the tub rim close-up. |
| 16609 | 3 | fix_fixture | f_L0_003 | fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_007) | Move the washbasin out of the door d_L0_007 swing that intrudes on one hinge side. |
| 17319 | 4 | relayout_room | r_L-1_mutfak_2 | no_place: r_L-1_mutfak_2 relayout: no place passes the checks (dining: no place passes the checks) | Argus: Same kitchen aisle problem as F65 in the duplicate room instance. (fixes a:F67) |
| 17320 | 4 | swap_model | f_L0_019 | no_change: f_L0_019 already uses the model abo_B086TGFT35 | Argus: The bed has only 0.53 m on the left side; swapping to the 1.54 m wide model (abo_B086TGFT35) will free up the needed clearance. (fixes a:F76) |
| 17322 | 4 | swap_model | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Argus: The bed has only 0.53 m on the right side; swapping to the 1.54 m wide model (abo_B086TGFT35) will free up the needed clearance. (fixes a:F79) |
| 17323 | 4 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The drawn shower depth of 0.60 m is below the real product minimum of 0.70 m; the width 1.40 m is in range. Resizing the depth to 0.80 m brings it within the product range and the fit rules. (fixes a:F82) |
| 17324 | 4 | fix_fixture | f_L0_014 | fixture_size: f_L0_014: the drawn 0.60 x 1.40 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The drawn shower width of 0.60 m is below the real product minimum of 0.70 m; the depth 1.40 m is in range. Resizing the width to 0.80 m brings it within the product range. (fixes a:F83) |
| 17325 | 4 | swap_model | f_L-1_008 | built_in: f_L-1_008: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: The stove is planned but the scene has no object for it; the earlier swap was refused because the code treated it as built into the counter run. Swapping to a standalone range model (0.76 x 0.45 x 0.42 m) forces the build stage to place a v (fixes a:F157) |
| 17326 | 4 | swap_model | f_L-1_017 | built_in: f_L-1_017: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: Same cause as F157: the stove in the duplicate kitchen r_L-1_mutfak_2 is planned but has no object in the scene; swapping to a standalone range model forces a visible appliance object. (fixes a:F158) |
| 17327 | 4 | swap_model | f_L-1_067 | asset_unusable: hssd_e0ca9afd51fbf04f53db66069f7085e327daacd0 is not used: audit removed | Argus: The sink is planned but the scene has no object for it; earlier swaps were refused for fit-rule failures (caps, height) or audit removal. The hssd_e0ca9afd51fbf04f53db66069f7085e327daacd0 model (0.84 x 0.51 x 0.40 m, minimal/modern) is a lo (fixes a:F159) |
| 17328 | 4 | swap_model | f_L-1_068 | asset_unusable: hssd_e0ca9afd51fbf04f53db66069f7085e327daacd0 is not used: audit removed | Argus: Same cause as F159: the sink in the duplicate kitchen r_L-1_mutfak_2 is planned but has no object in the scene; swapping to a low-profile undermount sink model forces a visible fixture object. (fixes a:F160) |
| 17329 | 4 | fix_fixture | f_L0_026 | no_change: f_L0_026: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The tub is correctly sized (1.83 x 0.80 m, within the drawn bay) but is placed with only 0.28 m in front. The size edit was refused because the size is right; the fix is to move it to the nearest valid spot with the required clearance. (fixes a:F225) |
| 17330 | 4 | fix_fixture | f_L1_021 | no_change: f_L1_021: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is correctly sized (0.50 x 0.69 m) but sits 0.33 m from the side wall/fixture on its right. The size edit was refused because the size is right; the fix is to move it to the nearest valid spot. (fixes a:F226) |
| 17331 | 4 | fix_fixture | f_L1_025 | no_change: f_L1_025: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The tub is correctly sized (1.83 x 0.80 m) but is placed with only 0.28 m in front. The size edit was refused because the size is right; the fix is to move it to the nearest valid spot with the required clearance. (fixes a:F227) |
| 17332 | 4 | fix_fixture | f_L1_022 | no_change: f_L1_022: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is correctly sized (0.50 x 0.69 m) but sits 0.33 m from the side wall/fixture on its left. The size edit was refused because the size is right; the fix is to move it to the nearest valid spot. (fixes a:F228) |
| 17333 | 4 | fix_fixture | f_L1_026 | no_change: f_L1_026: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The tub is correctly sized (1.83 x 0.80 m) but is placed with only 0.28 m in front. The size edit was refused because the size is right; the fix is to move it to the nearest valid spot with the required clearance. (fixes a:F229) |
| 17334 | 4 | correct_geometry | o_L1_001 | the opening already lies on the wall (0.000 m) | Argus: The opening o_L1_001 is not cut through its wall; the door ray hits w_L1_003. The code_fix is clear_opening, which maps to correct_geometry with kind fix_opening_on_wall. (fixes a:F232) |
| 17335 | 4 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 0.29 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: There is no frontal view of the entrance (+y) facade. The existing exterior cameras (ext_1, ext_2, ext_3, ext_5, ext_7) do not include a frontal entrance view. Adding a new exterior camera facing the +y facade will fix this. (fixes a:F235) |
| 17336 | 4 | swap_model | f_L0_015 | acceptance: pin_refused: f_L0_015: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current toilet model is a crude low-poly box; swapping to a more detailed model (3dwh_36adbef7518af3145f49b210) should fix it. The previously refused model (objaverse_5b18711616054a44b025d9272b745a6a) was removed by audit, so a differen (fixes a:F283) |
| 17337 | 4 | swap_model | f_L0_006 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The current washbasin model is a crude low-poly box; swapping to a more detailed model (3dwh_6597c60d5f0b3aa5ee0c0169) should fix it. The previously refused model (3dwh_9314d5619fde2de825a4a2a1) was removed by audit, so a different model is (fixes a:F284) |
| 17340 | 4 | set_camera | r_L-1_koridor_2 | show: none of the 8 best poses of r_L-1_koridor_2 that show f_L-1_094, f_L-1_019 passes the camera checks: duplicate: cam_r_L-1_koridor_2_1 would show the view cam_r_L-1_koridor_2_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_koridor_2, or remove one of the two views | Argus: The camera is pointed at a blank corner and wall, wasting the frame; the hall's function (shoe cabinet, stair, doors) is not shown. (fixes a:F289) |
| 17342 | 4 | set_camera | r_L-1_mutfak | show: none of the 8 best poses of r_L-1_mutfak that show f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067 passes the camera checks: duplicate: cam_r_L-1_mutfak_2 would show the view cam_r_L-1_mutfak_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_mutfak, or remove one of the two views; duplicate: cam_r_L-1_mutfak_2 would show the view cam_r_L-1_mutfak_3 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_mutfak, or remove one of the two views | Argus: The render is a bare, unfinished shell; the camera does not frame the kitchen's functional group. (fixes a:F294) |
| 17343 | 4 | set_exterior | exterior:ground | no_change: the exterior already has these values ({"ground": "grass"}): nothing to change | Argus: The view through win_L-1_003 is a flat, untextured green plane; the ground/site model needs a real landscape. (fixes a:F295) |
| 17344 | 4 | swap_model | f_L-1_070 | asset_unusable: 3dwh_49c89838e523cdc64ffa7de1 is not used: audit removed | Argus: The taupe armchair is a different style and colour from the cream sofa and white lounge chair; swapping to a modern/scandinavian model coordinates the seating set. (fixes a:F297) |
| 17345 | 4 | swap_model | f_L-1_053 | asset_unusable: 3dwh_e5f77d70d0615bd56772bf1f is not used: audit removed | Argus: The blocky, low-poly white sofa is a generic placeholder that clashes with the modern, warm style; swapping to a modern/scandinavian model fixes the set. (fixes a:F301) |
| 17348 | 4 | set_camera | r_L0_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: Same root cause as F305: the second camera of the same room is a close-up of a blank wall and vanity corner; re-aiming it at the fixture group fixes it. (fixes a:F306) |

Rolled back (the refit refused them): #453 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #455 rotate_piece (locked check: f_L-1b_054: drawn_front_deg None != the drawn front 0.0), #506 rotate_piece (locked check: f_L-1b_051: drawn_front_deg None != the drawn front 180.0), #507 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0), #508 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #509 rotate_piece (locked check: f_L-1b_054: drawn_front_deg None != the drawn front 0.0).

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F9 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| F9 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| G8 | minor | f_L-1b_055 | r_L-1b_salon_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1b_056 | r_L-1b_salon | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| M13 | minor | f_L-1_091 | r_L-1_mutfak | fit | kitchen_design | 1, 2, 3, 4 | the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit composes them of real units on the base joints (modules.plan_wall_run); the build cuts them at the windows of the building as built. No agent tool builds a hood or splits a wall cabinet, so the finding is reported to the fit |
| M13 | minor | f_L-1_097 | r_L-1_mutfak_2 | fit | kitchen_design | 1, 2, 3, 4 | the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit composes them of real units on the base joints (modules.plan_wall_run); the build cuts them at the windows of the building as built. No agent tool builds a hood or splits a wall cabinet, so the finding is reported to the fit |
| M13 | minor | f_L-1_099 | r_L-1_mutfak_2 | fit | kitchen_design | 1, 2, 3, 4 | the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit composes them of real units on the base joints (modules.plan_wall_run); the build cuts them at the windows of the building as built. No agent tool builds a hood or splits a wall cabinet, so the finding is reported to the fit |
| M14 | major | dec_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_019 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_020 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_025 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_039 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_040 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M18 | major | f_L-1_020 | r_L-1_koridor | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M18 | major | f_L0_002 | r_L0_merdiven_2 | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| Q11 | major | f_L-1_060 | r_L-1_salon | lighting | light_fixture | 1 | the finding is about a light fixture (the room's lighting rig), not the piece it names: no agent tool changes a light's model, so it is reported to the lighting stage |
| Q11 | major | f_L-1_063 | r_L-1_salon | lighting | light_fixture | 1 | the finding is about a light fixture (the room's lighting rig), not the piece it names: no agent tool changes a light's model, so it is reported to the lighting stage |
| Q11 | major | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | lighting | light_fixture | 1, 2 | the finding is about a light fixture (the room's lighting rig), not the piece it names: no agent tool changes a light's model, so it is reported to the lighting stage |
| Q3 | critical | r_L-1_koridor | r_L-1_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_koridor_2 | r_L-1_koridor_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L0_koridor | r_L0_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L1_koridor | r_L1_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L1_koridor_2 | r_L1_koridor_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q7 | minor | d_L1_003 | r_L1_teras | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q9 | minor | d_L0_005 | - | site | entrance_layout | 4 | the landings, steps, ramps and handrails in front of the doors are laid out by code for all the entrances together (site.entrance_layout: doors whose steps would meet share one platform with one flight, a ramp and the handrails keep clear of the other doors); no agent tool moves them, so the finding is reported to the site stage |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L0_029 | r_L0_yatak_odasi_3 | - | within_tolerance | 3 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_009 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | critical | dec_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_019 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_020 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_025 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_039 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_040 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_050 | r_L-1_salon_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_019 | r_L0_yatak_odasi | decor | decor_rest | 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_022 | r_L0_yatak_odasi_4 | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | facade | 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L1_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_005 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_006 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L1_002 | - | - | scale | 2, 3, 4 | storey and door sizes come from the drawings |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon_2 | cut | 3 | 15095 | 32768 |
| 1 | r_L-1b_salon | cut | 2 | 11864 | 32768 |
| 1 | building | cut | 1 | 34396 | 32768 |
| 2 | r_L-1b_salon | cut | 9 | 48812 | 32768 |
| 3 | r_L-1b_salon | cut | 3 | 17817 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | change | by (rule) | reason |
|---|---|---|---|---|---|---|---|
| f_L-1_006 | piece | unknown | r_L-1_mutfak | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_007 | piece | unknown | r_L-1_mutfak | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_009 | piece | sink_kitchen | r_L-1_mutfak | inferred | - | - | drawn inside the sink_kitchen f_L-1_067 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_015 | piece | unknown | r_L-1_mutfak_2 | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_016 | piece | unknown | r_L-1_mutfak_2 | inferred | - | - | drawn on the 'Deko_Ahsap01' layer(s): decor, not furniture (the decor stage places decor) |
| f_L-1_018 | piece | sink_kitchen | r_L-1_mutfak_2 | inferred | - | - | drawn inside the sink_kitchen f_L-1_068 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L-1_019 | piece | stair | r_L-1_koridor_2 | adjusted_by_ai | size 2.71 x 2.10 m -> 2.65 x 2.10 m | architect (architect K1) | a riser of 0.250 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L-1_020 | piece | stair | r_L-1_koridor | adjusted_by_ai | size 2.71 x 2.10 m -> 2.60 x 2.10 m | architect (architect K1) | a riser of 0.250 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L-1_023 | piece | wardrobe | r_L-1_salon_2 | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | code (size_snap) | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_024 | piece | wardrobe | r_L-1_salon | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | code (size_snap) | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_028 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dining chairs are a random mix of models and finishes; swapping to a single minimal/modern model coordinates the dining set. (fixes a:F302) |
| f_L-1_031 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge chair f_L-1_031 away from the table edge to clear the 0.040 m cut with table f_L-1_027. |
| f_L-1_038 | piece | table_dining | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | S2: table cut chairs f_L-1_039 and f_L-1_042 by 0.034 m; shift the table 0.08 m so the cut drops below the 0.010 m allowance. |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred | - | - | front: faces the coffee table f_L-1_087 |
| f_L-1_050 | piece | armchair | r_L-1_salon_2 | inferred | - | - | front: faces the coffee table f_L-1_088 |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - | - | bathtub: r_L-1_banyo_2.bathroom_set (anchor f_L-1_052) misses shower\|bathtub, and the type's product range fits 1.83 x 0.80 m (the only missing member of that size); front: the free side facing the most room is the front |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Swap plain untextured white block bathtub for a premium Kaldewei CLASSIC DUO 180x80cm bathtub with proper styling to match the reference. |
| f_L-1_057 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays, f_L-1_057 is not built (plan crop recognition/crops/sym_L-1_005_ctx.png) |
| f_L-1_058 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_059 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays, f_L-1_059 is not built (plan crop recognition/crops/sym_L-1_007_ctx.png) |
| f_L-1_060 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.60 x 0.60 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_061 | piece | table_coffee | r_L-1_salon | inferred | - | - | table_coffee: r_L-1_salon.seating (anchor f_L-1_053) misses table_coffee, and the type's product range fits 1.30 x 0.63 m (the only missing member of that size) |
| f_L-1_062 | piece | table_coffee | r_L-1_salon_2 | inferred | - | - | table_coffee: the same footprint (1.30 x 0.63 m) as f_L-1_061 in the twin room r_L-1_salon (mirrored centre within 0.02 m) |
| f_L-1_064 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png) |
| f_L-1_066 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png) |
| f_L-1_069 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Argus: The dark brown armchair clashes with the light beige sofa and white dining chairs. Swapping to a modern/scandinavian model with a lighter, cohesive finish resolves the mismatch. (fixes a:F290) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_072 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai | size 0.56 x 0.56 m -> 0.80 x 0.80 m | code (architect F5) | architect F5: f_L-1_073 (table_coffee) cut f_L-1_071 (armchair) by 0.13 m; f_L-1_073 (table_coffee) moved 0.41 m clear of it (inside its room, clear of the other pieces and the doorways) |
| f_L-1_074 | piece | table_coffee | r_L-1_salon_2 | adjusted_by_ai | size 0.56 x 0.56 m -> 0.80 x 0.80 m | code (architect F5) | architect F5: f_L-1_074 (table_coffee) cut f_L-1_069 (armchair) by 0.18 m; f_L-1_074 (table_coffee) moved 0.71 m clear of it (inside its room, clear of the other pieces and the doorways) |
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
| f_L0_001 | piece | stair | r_L0_merdiven | adjusted_by_ai | size 2.71 x 2.10 m -> 2.64 x 2.10 m | architect (architect K1) | a riser of 0.286 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L0_002 | piece | stair | r_L0_merdiven_2 | adjusted_by_ai | size 2.71 x 2.10 m -> 2.60 x 2.10 m | architect (architect K1) | a riser of 0.263 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The wardrobe has only 0.66 m in front; swapping to the 0.51 m deep model (abo_B07GFS1R5B) will free up the needed clearance. (fixes a:F78) |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current bed is styled with only a bare white sheet and two pillows, lacking the textured throw and layered bedding seen in the reference; swapping to a scandinavian/japandi bed model that includes styled bedding restores the layered loo (fixes a:F315) |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_019 in the twin room r_L0_yatak_odasi (mirrored centre within 0.02 m) |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred | - | - | bed_double: the same drawn block (the same strokes (22 INSERT here, within 2%)) and footprint (1.90 x 1.55 m, within 0.01 m) as f_L0_019, f_L0_020 (typed bed_double): one block, one type; front: its back stands on the only side on a wall |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_021 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m); front: its back stands on the only side on a wall |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 3.11 x 0.60 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - | - | wardrobe: the same footprint (3.11 x 0.60 m) as f_L0_023 in the twin room r_L0_e_yatak_odasi (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L0_025 in the twin room r_L0_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_035 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_036 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_037 stands in front; plan crop recognition/crops/sym_L0_011_ctx.png |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | Qwen/Qwen3.8-27B-FP8 (reading.desk_chair) | Move desk 0.05m in +y to increase bed right side clearance from 0.56m to 0.61m, satisfying G5 >= 0.60m (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: Shift nightstand f_L0_032 slightly away from the bed to resolve the 0.06 m² overlap (F9) and correct the -0.12 m gap to a valid distance (G4). |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift sofa f_L1_019 north away from f_L1_018 to clear the blocked free zone in front of it (F6) without breaking the walkway. |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_025 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge the armchair 0.1 m closer to the coffee table (2.73 m -> ~2.63 m) to clear G3/F94. (plan crop recognition/crops/sym_L1_010_ctx.png) |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | bench is invalid in a living room; a 1.4x0.45 console table fits its size and its position against the wall. (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: the same footprint (1.09 x 0.40 m) as f_L1_038 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (mirrored centre within 0.02 m) |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the bright blue office chair with a neutral black modern-minimal chair to remove the color/style clash (a:F317). (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current office_chair is a utilitarian, ergonomic model with a blue mesh back that clashes with the warm, residential aesthetic of the bedroom; swapping to a modern minimal chair of the same footprint restores a coherent set. (fixes a:F310) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_039 | piece | shoe_cabinet | r_L0_koridor | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_039: the piece is not built |
| f_L0_040 | piece | shoe_cabinet | r_L0_koridor_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_040: the piece is not built |
| f_L1_043 | piece | table_dining | r_L1_teras_2 | adjusted_by_ai | - | architect | moved 0.44 m clear of win_L1_002 (the answer to AI.move_piece:f_L1_043) |
| f_L1_044 | piece | chair | r_L1_teras_2 | adjusted_by_ai | - | architect | moved 0.31 m clear of win_L1_002 (the answer to AI.move_piece:f_L1_044) |
| f_L1_045 | piece | chair | r_L1_teras_2 | adjusted_by_ai | - | architect | moved 0.31 m clear of win_L1_002 (the answer to AI.move_piece:f_L1_045) |
| f_L0_042 | piece | nightstand | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Slide nightstand f_L0_042 0.06 m along the window wall to clear the window win_L0_001 (sill 0.20 m) while staying beside the bed. |
| f_L0_045 | piece | nightstand | r_L0_yatak_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | a:F80: move nightstand f_L0_045 off window win_L0_004 onto wall w_L0_016 to clear the window |
| f_L1_054 | piece | shoe_cabinet | r_L1_koridor_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_054: the piece is not built |
| o_L1_001 | geometry | fix_opening_on_wall | - | corrected_by_ai, record_only | - | - | Argus: The opening o_L1_001 is not cut through its wall w_L1_003; the door ray hits the wall. (fixes a:F229) |

Geometry corrections are record-only in M11: the drawn geometry was not changed; they are open items for the next full run.

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
| 1 | cam_r_L-1_mutfak_1 | ![](agent/r1_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_1_after.jpg) |
| 1 | cam_r_L-1_mutfak_2 | ![](agent/r1_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_2_after.jpg) |
| 1 | cam_r_L-1_mutfak_3 | ![](agent/r1_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_3_after.jpg) |
| 1 | cam_r_L-1_salon_1 | ![](agent/r1_cam_r_L-1_salon_1_before.jpg) | ![](agent/r1_cam_r_L-1_salon_1_after.jpg) |
| 1 | cam_r_L-1_salon_2 | ![](agent/r1_cam_r_L-1_salon_2_before.jpg) | ![](agent/r1_cam_r_L-1_salon_2_after.jpg) |
| 1 | cam_r_L-1_salon_3 | ![](agent/r1_cam_r_L-1_salon_3_before.jpg) | ![](agent/r1_cam_r_L-1_salon_3_after.jpg) |
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_banyo_2 | ![](agent/r1_cam_r_L0_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_banyo_2_after.jpg) |
| 1 | cam_r_L0_e_banyo_1 | ![](agent/r1_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_e_banyo_1_after.jpg) |
| 1 | cam_r_L0_koridor_1 | ![](agent/r1_cam_r_L0_koridor_1_before.jpg) | ![](agent/r1_cam_r_L0_koridor_1_after.jpg) |
| 1 | cam_r_L1_banyo_1 | ![](agent/r1_cam_r_L1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L1_banyo_1_after.jpg) |
| 1 | cam_r_L1_koridor_1 | ![](agent/r1_cam_r_L1_koridor_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_1_after.jpg) |
| 1 | cam_r_L1_koridor_2 | ![](agent/r1_cam_r_L1_koridor_2_before.jpg) | ![](agent/r1_cam_r_L1_koridor_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 1 | cam_r_L1_teras_2 | ![](agent/r1_cam_r_L1_teras_2_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_after.jpg) |
| 1 | cam_r_L1_teras_3 | ![](agent/r1_cam_r_L1_teras_3_before.jpg) | ![](agent/r1_cam_r_L1_teras_3_after.jpg) |
| 2 | cam_r_L-1_koridor_2_1 | ![](agent/r2_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r2_cam_r_L-1_koridor_2_1_after.jpg) |
| 2 | cam_r_L-1_koridor_2_2 | ![](agent/r2_cam_r_L-1_koridor_2_2_before.jpg) | ![](agent/r2_cam_r_L-1_koridor_2_2_after.jpg) |
| 2 | cam_r_L-1_salon_1 | ![](agent/r2_cam_r_L-1_salon_1_before.jpg) | ![](agent/r2_cam_r_L-1_salon_1_after.jpg) |
| 2 | cam_r_L-1_salon_2 | ![](agent/r2_cam_r_L-1_salon_2_before.jpg) | ![](agent/r2_cam_r_L-1_salon_2_after.jpg) |
| 2 | cam_r_L-1_salon_3 | ![](agent/r2_cam_r_L-1_salon_3_before.jpg) | ![](agent/r2_cam_r_L-1_salon_3_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_banyo_2 | ![](agent/r2_cam_r_L0_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_2_after.jpg) |
| 2 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r2_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r2_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 2 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r2_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r2_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 2 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r2_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r2_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 2 | cam_r_L0_koridor_1 | ![](agent/r2_cam_r_L0_koridor_1_before.jpg) | ![](agent/r2_cam_r_L0_koridor_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_1 | ![](agent/r2_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_2 | ![](agent/r2_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3 | ![](agent/r2_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r2_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r2_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 2 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r2_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r2_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 2 | cam_r_L1_banyo_1 | ![](agent/r2_cam_r_L1_banyo_1_before.jpg) | ![](agent/r2_cam_r_L1_banyo_1_after.jpg) |
| 2 | cam_r_L1_teras_1 | ![](agent/r2_cam_r_L1_teras_1_before.jpg) | ![](agent/r2_cam_r_L1_teras_1_after.jpg) |
| 2 | cam_r_L1_teras_2 | ![](agent/r2_cam_r_L1_teras_2_before.jpg) | ![](agent/r2_cam_r_L1_teras_2_after.jpg) |
| 3 | cam_r_L-1_banyo_1 | ![](agent/r3_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L-1_banyo_1_after.jpg) |
| 3 | cam_r_L-1_banyo_2 | ![](agent/r3_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r3_cam_r_L-1_banyo_2_after.jpg) |
| 3 | cam_r_L-1_koridor_2_1 | ![](agent/r3_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r3_cam_r_L-1_koridor_2_1_after.jpg) |
| 3 | cam_r_L-1_koridor_2_2 | ![](agent/r3_cam_r_L-1_koridor_2_2_before.jpg) | ![](agent/r3_cam_r_L-1_koridor_2_2_after.jpg) |
| 3 | cam_r_L-1_mutfak_1 | ![](agent/r3_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_1_after.jpg) |
| 3 | cam_r_L-1_mutfak_2 | ![](agent/r3_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_2_after.jpg) |
| 3 | cam_r_L-1_mutfak_3 | ![](agent/r3_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_3_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_banyo_1 | ![](agent/r3_cam_r_L0_banyo_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_1_after.jpg) |
| 3 | cam_r_L0_banyo_2 | ![](agent/r3_cam_r_L0_banyo_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_2_after.jpg) |
| 3 | cam_r_L0_e_banyo_1 | ![](agent/r3_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r3_cam_r_L0_e_banyo_1_after.jpg) |
| 3 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r3_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r3_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r3_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L0_koridor_1 | ![](agent/r3_cam_r_L0_koridor_1_before.jpg) | ![](agent/r3_cam_r_L0_koridor_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_1 | ![](agent/r3_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_2 | ![](agent/r3_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r3_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r3_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 3 | cam_r_L1_banyo_1 | ![](agent/r3_cam_r_L1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L1_banyo_1_after.jpg) |
| 3 | cam_r_L1_koridor_1 | ![](agent/r3_cam_r_L1_koridor_1_before.jpg) | ![](agent/r3_cam_r_L1_koridor_1_after.jpg) |
| 3 | cam_r_L1_koridor_2 | ![](agent/r3_cam_r_L1_koridor_2_before.jpg) | ![](agent/r3_cam_r_L1_koridor_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 3 | cam_r_L1_teras_1 | ![](agent/r3_cam_r_L1_teras_1_before.jpg) | ![](agent/r3_cam_r_L1_teras_1_after.jpg) |
| 3 | cam_r_L1_teras_2 | ![](agent/r3_cam_r_L1_teras_2_before.jpg) | ![](agent/r3_cam_r_L1_teras_2_after.jpg) |
| 3 | cam_r_L1_teras_3 | ![](agent/r3_cam_r_L1_teras_3_before.jpg) | ![](agent/r3_cam_r_L1_teras_3_after.jpg) |
| 3 | ext_1 | ![](agent/r3_ext_1_before.jpg) | ![](agent/r3_ext_1_after.jpg) |
| 3 | ext_2 | ![](agent/r3_ext_2_before.jpg) | ![](agent/r3_ext_2_after.jpg) |
| 3 | ext_3 | ![](agent/r3_ext_3_before.jpg) | ![](agent/r3_ext_3_after.jpg) |
| 3 | ext_5 | ![](agent/r3_ext_5_before.jpg) | ![](agent/r3_ext_5_after.jpg) |
| 3 | ext_7 | ![](agent/r3_ext_7_before.jpg) | ![](agent/r3_ext_7_after.jpg) |
| 4 | cam_r_L-1_banyo_1 | ![](agent/r4_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L-1_banyo_1_after.jpg) |
| 4 | cam_r_L-1_banyo_2 | ![](agent/r4_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r4_cam_r_L-1_banyo_2_after.jpg) |
| 4 | cam_r_L-1_koridor_2_2 | ![](agent/r4_cam_r_L-1_koridor_2_2_before.jpg) | ![](agent/r4_cam_r_L-1_koridor_2_2_after.jpg) |
| 4 | cam_r_L-1_salon_1 | ![](agent/r4_cam_r_L-1_salon_1_before.jpg) | ![](agent/r4_cam_r_L-1_salon_1_after.jpg) |
| 4 | cam_r_L-1_salon_2 | ![](agent/r4_cam_r_L-1_salon_2_before.jpg) | ![](agent/r4_cam_r_L-1_salon_2_after.jpg) |
| 4 | cam_r_L-1_salon_3 | ![](agent/r4_cam_r_L-1_salon_3_before.jpg) | ![](agent/r4_cam_r_L-1_salon_3_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_1 | ![](agent/r4_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_2 | ![](agent/r4_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_2_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3 | ![](agent/r4_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- final/cam_r_L1_teras_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_3_final_preview_2.jpg
- final/cam_r_L1_teras_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_teras_3_plan_2.jpg
