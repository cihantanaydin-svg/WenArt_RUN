# Final report: real04

36 views: 0 polished, 36 Cycles (error 12, gate_validation 5, not_run 2, room 17). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 36 |
| interior / exterior views | 31 / 5 |
| variant | base |
| polished | 0 |
| Cycles | 36 (error 12, gate_validation 5, not_run 2, room 17) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 29 |
| needs_review views | 15 |
| unverified pieces in view (sum over views) | 43 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 12 |
| exposure | -7.83 .. +2.50 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 25 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 11, m5 5, search 20 |
| camera score (min / mean / max) | 1.47 / 3.90 / 4.78 |
| rooms by number of views | 1 with 0, 4 with 1, 3 with 2, 7 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 6.1 min / 6.6 min / 91.3 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 37.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 15 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 833.7 MB |
| [real04.glb](3d/real04.glb) | 1677.3 MB |

36 cameras; textures scaled to at most 1024 px (364 scaled) for the download.

## AI decor

138 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 35 rooms; 353 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 18 piece(s) moved beyond the tolerance, 69 locked-rule violation(s)
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
| r_L-1_banyo | cam_r_L-1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L-1_banyo | cam_r_L-1_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L-1_koridor_2 | cam_r_L-1_koridor_2_1 | a2 s 0.25 canny x0.8 | accept | info | - | - | cycles (error) |
| r_L-1_mutfak | cam_r_L-1_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L-1_mutfak | cam_r_L-1_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L-1_mutfak | cam_r_L-1_mutfak_3 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L-1_salon | cam_r_L-1_salon_1 | - | - | info | - | - | cycles (room) |
| r_L-1_salon | cam_r_L-1_salon_2 | - | - | info | - | - | cycles (room) |
| r_L-1_salon | cam_r_L-1_salon_3 | - | - | info | - | - | cycles (room) |
| r_L0_banyo | cam_r_L0_banyo_1 | a2 s 0.25 canny x0.8 | accept | info | - | - | cycles (error) |
| r_L0_banyo | cam_r_L0_banyo_2 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L0_e_banyo | cam_r_L0_e_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L0_e_banyo | cam_r_L0_e_banyo_2 | - | - | info | - | - | cycles (not_run) |
| r_L0_e_yatak_odasi | cam_r_L0_e_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L0_e_yatak_odasi | cam_r_L0_e_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L0_e_yatak_odasi | cam_r_L0_e_yatak_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L0_koridor | cam_r_L0_koridor_1 | a2 s 0.25 canny x0.8 | accept | info | - | - | cycles (error) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi | cam_r_L0_yatak_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi_3 | cam_r_L0_yatak_odasi_3_1 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi_3 | cam_r_L0_yatak_odasi_3_2 | - | - | info | - | - | cycles (room) |
| r_L0_yatak_odasi_3 | cam_r_L0_yatak_odasi_3_3 | - | - | info | - | - | cycles (room) |
| r_L1_banyo | cam_r_L1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L1_koridor | cam_r_L1_koridor_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L1_teras | cam_r_L1_teras_1 | - | - | info | - | - | cycles (room) |
| r_L1_teras | cam_r_L1_teras_2 | - | - | info | - | - | cycles (room) |
| r_L1_teras | cam_r_L1_teras_3 | - | - | info | - | - | cycles (not_run) |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.50 | - | search 3.76 | D3 A5 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | agent | D2 A1 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.50 | - | agent | D1 A3 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.67 | -3 | search 4.60 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.83 | -3 | search 3.79 | D5 A1 | 0 | yes | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.17 | -1 | search 4.23 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 3.65 | D7 A4 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +0.83 | -3 | search 3.64 | D10 A5 | 4 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.00 | -3 | search 3.48 | D12 A5 | 3 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.00 | - | agent | D3 A4 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.67 | - | agent | D2 A1 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | search 1.47 | D2 A4 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +1.00 | - | agent | D3 A2 | 1 | yes | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.67 | -1 | search 4.78 | D7 A5 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.17 | -1 | search 4.77 | D5 A8 | 0 | yes | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.50 | -3 | search 4.58 | D4 A7 | 0 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.00 | - | agent | D5 A4 | 1 | yes | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.17 | -4 | agent | D4 A7 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.33 | - | search 4.00 | D4 A4 | 2 | yes | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.17 | -4 | agent | D5 A9 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.50 | -4 | search 4.77 | D4 A4 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.50 | -4 | search 4.55 | D6 | 4 | yes | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 4.41 | D4 A5 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | -0.17 | - | agent | D2 | 1 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.67 | - | agent | D3 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.17 | -2 | search 2.94 | D5 A2 | 0 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 4.14 | D9 A2 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 4.21 | D7 A2 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.33 | 0 | agent | D3 A5 | 0 | yes | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.33 | 0 | search 3.14 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.33 | 0 | search 3.05 | D1 A5 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.83 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.83 | 0 | m5 blocked | D4 | 1 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.33 | 0 | m5 | D10 | 1 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.83 | 0 | m5 | D6 | 1 | yes | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 2 | 0 | 2 | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2 |
| r_L-1_banyo_2 | bathroom | L-1 | 0 | 0 | 0 | - |
| r_L-1_koridor | hall | L-1 | 0 | 0 | 0 | - |
| r_L-1_koridor_2 | hall | L-1 | 1 | 0 | 1 | cam_r_L-1_koridor_2_1 |
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
| r_L0_koridor | hall | L0 | 1 | 0 | 1 | cam_r_L0_koridor_1 |
| r_L0_koridor_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_merdiven | hall | L0 | 0 | 0 | 0 | - |
| r_L0_merdiven_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L0_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_3 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3 |
| r_L0_yatak_odasi_4 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L1_banyo | bathroom | L1 | 1 | 0 | 1 | cam_r_L1_banyo_1 |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 1 | 0 | 1 | cam_r_L1_koridor_1 |
| r_L1_koridor_2 | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | living | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | living | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 |
| r_L1_teras_2 | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_banyo_2 (twin of r_L0_e_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_4 (twin of r_L0_yatak_odasi_3), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_koridor_2 (twin of r_L1_koridor), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi), r_L1_teras_2 (twin of r_L1_teras).

Rooms without a rendered view: r_L0_merdiven (stair core: the stair fills the room, its only camera point is inside the stair; the hall shows it (docs/milestone11.md §1.3 M5)).

### Why Cycles

- cam_r_L-1_banyo_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L-1_banyo_2: error: polished from another render (source sha256 differs from the current render)
- cam_r_L-1_koridor_2_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L-1_mutfak_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L-1_mutfak_2: error: polished from another render (source sha256 differs from the current render)
- cam_r_L-1_mutfak_3: error: polished from another render (source sha256 differs from the current render)
- cam_r_L-1_salon_1: room: polish: room
- cam_r_L-1_salon_2: room: polish: room
- cam_r_L-1_salon_3: room: polish: room
- cam_r_L0_banyo_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_banyo_2: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_e_banyo_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_e_banyo_2: not_run: view not in the polish manifest
- cam_r_L0_e_yatak_odasi_1: room: polish: room
- cam_r_L0_e_yatak_odasi_2: room: polish: room
- cam_r_L0_e_yatak_odasi_3: room: polish: room
- cam_r_L0_koridor_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: room: polish: room
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L0_yatak_odasi_3_1: room: polish: room
- cam_r_L0_yatak_odasi_3_2: room: polish: room
- cam_r_L0_yatak_odasi_3_3: room: polish: room
- cam_r_L1_banyo_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_koridor_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: room: polish: room
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room: polish: room
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: room: polish: room
- cam_r_L1_teras_1: room: polish: room
- cam_r_L1_teras_2: room: polish: room
- cam_r_L1_teras_3: not_run: view not in the polish manifest
- ext_1: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_2: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_3: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_5: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_7: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_mutfak_2 | cycles | cross-check misplaced | d_L-1_003 | door | - | from_documents | deneme1.dwg INSERT:365E2/1,INSERT:365E2/0 vector 0.95 | yes | 97 % of its pixels > 0.10 m outside the drawing, 158957 px |
| cam_r_L0_e_banyo_2 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3260 px |
| cam_r_L0_e_banyo_2 | cycles | cross-check misplaced | d_L0_002 | door | - | from_documents | deneme1.dwg INSERT:2DDF1/1,INSERT:2DDF1/0,LWPOLYLINE:2DDF5 vector 0.95 | yes | 61 % of its pixels > 0.10 m outside the drawing, 614275 px |
| cam_r_L0_e_yatak_odasi_1 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 65 % of its pixels > 0.10 m outside the drawing, 55853 px |
| cam_r_L0_e_yatak_odasi_1 | cycles | cross-check misplaced | d_L0_002 | door | - | from_documents | deneme1.dwg INSERT:2DDF1/1,INSERT:2DDF1/0,LWPOLYLINE:2DDF5 vector 0.95 | yes | 40 % of its pixels > 0.10 m outside the drawing, 86248 px |
| cam_r_L0_e_yatak_odasi_1 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 51 % of its pixels > 0.10 m outside the drawing, 34119 px |
| cam_r_L0_e_yatak_odasi_2 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 43 % of its pixels > 0.10 m outside the drawing, 548513 px |
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 40 % of its pixels > 0.10 m outside the drawing, 581016 px |
| cam_r_L0_koridor_1 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 10 % of its pixels > 0.10 m outside the drawing, 15715 px |
| cam_r_L0_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 69 % of its pixels > 0.10 m outside the drawing, 114902 px |
| cam_r_L0_yatak_odasi_3_2 | cycles | cross-check misplaced | d_L0_006 | door | - | from_documents | deneme1.dwg INSERT:2DDE5/1,INSERT:2DDE5/0,LWPOLYLINE:2DE07 vector 0.95 | yes | 64 % of its pixels > 0.10 m outside the drawing, 246220 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 59 % of its pixels > 0.10 m outside the drawing, 25068 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 62 % of its pixels > 0.10 m outside the drawing, 23026 px |
| cam_r_L1_teras_1 | cycles | cross-check misplaced | f_L1_096 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 26 px; added_by_ai: render/polish issue, not a document conflict |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 24 % of its pixels > 0.10 m outside the drawing, 43606 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 16 % of its pixels > 0.10 m outside the drawing, 5636 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 23 % of its pixels > 0.10 m outside the drawing, 46282 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 15 % of its pixels > 0.10 m outside the drawing, 5723 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 33 % of its pixels > 0.10 m outside the drawing, 42677 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 27 % of its pixels > 0.10 m outside the drawing, 10292 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 72 % of its pixels > 0.10 m outside the drawing, 12346 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 65 % of its pixels > 0.10 m outside the drawing, 10069 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3079 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 2654 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 7116 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1556 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3294 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 46 % of its pixels > 0.10 m outside the drawing, 14797 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12221 px |

## Needs review

- cam_r_L-1_mutfak_2: json cross-check misplaced: d_L-1_003
- cam_r_L0_e_banyo_2: json cross-check misplaced: d_L0_001; json cross-check misplaced: d_L0_002
- cam_r_L0_e_yatak_odasi_1: json cross-check misplaced: d_L0_001; json cross-check misplaced: d_L0_002; json cross-check misplaced: d_L0_005
- cam_r_L0_e_yatak_odasi_2: json cross-check misplaced: f_L0_007
- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: f_L0_007
- cam_r_L0_koridor_1: json cross-check misplaced: d_L0_001
- cam_r_L0_yatak_odasi_2: json cross-check misplaced: d_L0_005
- cam_r_L0_yatak_odasi_3_2: json cross-check misplaced: d_L0_006
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: json cross-check misplaced: d_L1_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: json cross-check misplaced: d_L1_001
- cam_r_L1_teras_1: json cross-check misplaced: f_L1_096
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

- cam_r_L-1_banyo_2: f_L-1_056
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_071
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_061, f_L-1_070, f_L-1_087
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_071, f_L-1_073
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_banyo_2: f_L0_023
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_koridor_1: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3_1: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L1_banyo_1: f_L1_025
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

0 change(s) applied, 42 piece(s) added, 12 wall cabinet run(s).

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
- added f_L-1b_072: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_073: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L-1b_074: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_075: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L-1b_076: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L-1b_077: ottoman 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_078: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_042, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_056, f_L-1b_060, f_L-1b_062

### Salon (r_L-1b_salon_2, living): completed (partner r_L-1b_salon (twin) not used: 3 of 8 copied pieces fail a check here (ottoman: the copy fails clearance_ok here; potted_plant: the copy fails doors_free, wall_contact here; side_table: the copy fails clearance_ok, wall_contact here); completed itself)

- added f_L-1b_083: side_table 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_084: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_085: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L-1b_086: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_087: armchair 0.90 x 0.90 (confidence -, rule)
- added f_L-1b_088: ottoman 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_089: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_003, f_L-1b_004, f_L-1b_006, f_L-1b_007, f_L-1b_008, f_L-1b_017, f_L-1b_018, f_L-1b_019, f_L-1b_020, f_L-1b_021, f_L-1b_022, f_L-1b_023, f_L-1b_024, f_L-1b_025, f_L-1b_039, f_L-1b_041, f_L-1b_045, f_L-1b_047, f_L-1b_048, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_059, f_L-1b_061

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_082: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): completed (partner r_L-1b_koridor (twin) not used: the twin's drawn furniture does not map onto this room: drawn stair f_L-1b_016 has no counterpart here; completed itself)

- added f_L-1b_093: console_table 0.90 x 0.30 (confidence -, rule)
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

- added f_L1_049: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_050: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_051: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L1_052: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L1_053: ottoman 0.50 x 0.50 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no place passes the checks)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_006, f_L1_007, f_L1_013, f_L1_017, f_L1_020, f_L1_035, f_L1_036

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): completed (partner r_L1_oyun_aktivite_ve_dinlenme_odasi (twin) not used: 1 of 5 copied pieces fail a check here (floor_lamp: the copy fails wall_contact here); completed itself)

- added f_L1_055: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_056: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_057: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_058: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_059: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L1_060: ottoman 0.50 x 0.50 (confidence -, rule)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_010, f_L1_011, f_L1_014, f_L1_018, f_L1_019, f_L1_037, f_L1_038

### Koridor (r_L1_koridor, hall): completed

- added f_L1_054: shoe_cabinet 0.60 x 0.25 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_027

### Koridor (r_L1_koridor_2, hall): mirrored (decisions of r_L1_koridor (twin), not asked again)

- added f_L1_061: shoe_cabinet 0.60 x 0.25 (confidence -, rule, mirrored from f_L1_054)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_028

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_021, f_L1_025

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_016, f_L1_022, f_L1_026

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 146 ok, 18 failed; 52 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_031 | chair (chair) | 0.14 | 0.00 | - | - |
| f_L-1_039 | chair (chair) | 0.13 | 0.00 | - | - |
| f_L-1_042 | chair (chair) | 0.14 | 0.00 | - | - |
| f_L-1_063 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_065 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L0_009 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_010 | wardrobe (wardrobe) | 0.70 | 0.00 | yes | - |
| f_L0_011 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_032 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_019 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_031 | armchair (armchair) | 0.30 | 0.00 | - | - |

Locked-rule violations:

- walls: must stay as drawn (byte-equal): removed w_L-1b_001, w_L-1b_002, w_L-1b_003, w_L-1b_004, w_L-1b_005, w_L-1b_006, w_L-1b_007, w_L-1b_008, w_L-1b_009, w_L-1b_010, w_L-1b_011, w_L-1b_012, w_L-1b_013
- openings: must stay as drawn (byte-equal): changed d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_005, d_L0_006, d_L0_007, d_L0_008, d_L0_009, d_L0_010, d_L0_011, d_L0_012, d_L1_001, d_L1_002, d_L1_003, d_L1_004, d_L1_005, d_L1_006, win_L-1_001, win_L-1_002, win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L1_001, win_L1_002; removed d_L-1b_001, d_L-1b_002, d_L-1b_003, d_L-1b_004, o_L-1b_001, o_L-1b_002, win_L-1b_001, win_L-1b_002; added win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1
- rooms: must stay as drawn (byte-equal): changed r_L-1_salon, r_L-1_salon_2, r_L0_e_yatak_odasi, r_L0_e_yatak_odasi_2, r_L0_yatak_odasi, r_L0_yatak_odasi_2, r_L0_yatak_odasi_3, r_L0_yatak_odasi_4, r_L1_oyun_aktivite_ve_dinlenme_odasi, r_L1_oyun_aktivite_ve_dinlenme_odasi_2; removed r_L-1b_banyo, r_L-1b_banyo_2, r_L-1b_koridor, r_L-1b_koridor_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_salon, r_L-1b_salon_2
- f_L-1_073: moved 0.717 m by the agent (> 0.3 m)
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
- f_L0_009: moved 0.400 m by the agent (> 0.3 m)
- f_L0_011: moved 0.400 m by the agent (> 0.3 m)

## Exterior views

5 of 5 exterior view(s) of variant `base` rendered; 2 dropped (no camera place worked).

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)
- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **polish_disabled** (exterior views stay the Cycles render): negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: unverified | yes |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: unverified | yes |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: unverified | no |
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
| paving | paving_stone | - | agent | no | agent override (docs/milestone11.md §17.3) |
| garden | grass | - | agent | no | agent override (docs/milestone11.md §17.3) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | stone_wall_ashlar | - | agent | no | agent override (docs/milestone11.md §17.3) |
| plinth | stone_wall_ashlar | - | agent | no | agent override (docs/milestone11.md §17.3) |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof mismatch.

Roof heights: built eaves 3,75 m, ridge 6,01 m; drawn eaves 3,75 m (vector), ridge 5,80 m (vector); result mismatch.

## Variants

One building per drawn alternative plan: the base and, for each alternative, the same building with that level replaced. An alternative renders only the rooms it changes, and its exterior views only when its outside differs (otherwise the base views stand for it). Each alternative has its own report in its sub-output (paths below, relative to the project output).

| variant | label | rooms changed | outside | interior views | polished / Cycles | mismatches | report |
|---|---|---|---|---|---|---|---|
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 36 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_2, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_teras_1 | 0 / 22 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

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
- brief media_wall: True (default, not in brief.yaml)
- brief tv_in_bedroom: master (default, not in brief.yaml)
- brief room_fill: True (default, not in brief.yaml)
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
- door height 1,00 m: 2 opening(s) (d_L1_004, d_L1_005)
- door height 1,71 m: 2 opening(s) (d_L1_003, d_L1_006)
- door height 1,80 m: 2 opening(s) (d_L1_001, d_L1_002)
- door height 2,10 m: 13 opening(s) (d_L-1_001, d_L-1_002, d_L0_001, d_L0_002, d_L0_003, d_L0_004 ...)
- door height 2,40 m: 1 opening(s) (d_L0_011)
- door height 2,85 m: 2 opening(s) (d_L-1_003, d_L-1_004)
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
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| apron:apron_L-1_1 | 1 | the paved strip at the foot of the glazed facade runs its whole glazing run (win_L-1_001, win_L-1_002): 6.94 m on from the light well of win_L-1_002, 0.8 m deep, on the ground (lesson UL142; inferred) | site |
| area_light | 1 | r_L-1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo |
| area_light | 1 | r_L-1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo_2 |
| area_light | 1 | r_L-1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor |
| area_light | 1 | r_L-1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor_2 |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (4 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven_2 |
| area_light | 1 | r_L1_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo |
| area_light | 1 | r_L1_banyo: room has no window; the room's light rig (1 fixtures) has no ceiling fixture, so it adds to the invisible ceiling light | rig_r_L1_banyo |
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
| bath_details | 13 | the bathroom details of the piece (UL114, UL123, UL124: LED strips, a flush plate, towels and toiletries, shower fittings) inside its own box, one mesh | furn_f_L-1_051, furn_f_L-1_052, furn_f_L-1_103 |
| bath_items | 8 | the floating vanity's styling (UL114 B3, UL123 B19): part of its one mesh | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| bay_lights | 1 | an LED strip at the top of every bay lights the contents so they read through the see-through front (UL135; a wardrobe LED profile, 1000 lm per metre (UL135)) | furn_f_L0_023 |
| bedding | 1 | its cover is flat (relief 0 mm, 135 vertices/m2 on top: under 6 mm or 50; 80% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_020 |
| bedding | 1 | its cover is flat (relief 88 mm, 37 vertices/m2 on top: under 6 mm or 50; 100% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_021 |
| bedding | 1 | its pillows lie flat (bump 0.13 m < 0.22 m: no euro shams, no standing pillows; UL137): our shams and pillows stand against its headboard, its duvet kept; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_008 |
| bedding | 2 | its pillows lie flat (bump 0.19 m < 0.22 m: no euro shams, no standing pillows; UL137): our shams and pillows stand against its headboard, its duvet kept; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_019, dress_f_L0_022 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_007 |
| car | 1 | library car 3dwh_53630bfe2d05103a88e1a270 ('Car') on the drawn parking spk_001 (parallel bay, 4.65 x 2.10 x 1.40 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_0 |
| car | 1 | library car 3dwh_867427c8bc03ecda3fbb809a ('CAR') on the drawn parking spk_001 (perpendicular bay, 4.75 x 2.10 x 1.45 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_1 |
| car | 1 | library car 3dwh_a21d4bbd6e7b27b084152ccd ('Sports Car - Porsche') on the drawn parking spk_001 (parallel bay, 4.90 x 2.02 x 1.42 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_2 |
| chimney | 1 | inferred chimney (modern family): the mirrored dwelling's own, over the twin room r_L-1_salon_2 of r_L-1_salon; top 6.70 m: 0.6 m over the roof within 3 m (its highest point there 6.01 m) and 0.9 m over where it leaves the roof (5.77 m), the 3-2-10 rule of thumb | chimney_2 |
| chimney | 1 | inferred chimney (modern family: a modern pitched-roof house keeps a fireplace or a stove in its living room); no fireplace or flue drawn; over the fireplace wall w_L-1_004 of the living room r_L-1_salon (a solid inner wall stretch of 2.8 m with no door or window); top 6.70 m: 0.6 m over the roof within 3 m (its highest point there 6.01 m) and 0.9 m over where it leaves the roof (5.77 m), the 3-2-10 rule of thumb | chimney_1 |
| climate | 1 | the drawing's language (tr): the climate most of its houses stand in (a guess) (inferred; the species of trees and hedges follow it): banyo, merdiven, mutfak, otopark, yatak | site |
| context | 1 | no context drawn: 159 trees of the mediterranean climate (stone_pine 57, olive 43, cypress 35, plane 24; species inferred) in groups around the site, 89-350 m from the building's centre (the exterior cameras stand within 89 m), with open fields between them so the horizon stays in view (inferred context) | site |
| direction | 1 | the plan of L0 draws the same stair (f_L0_001) with its landing at the east end: the half landing is there, 1.24 m deep | furn_f_L-1_019 |
| direction | 1 | the plan of L0 draws the same stair (f_L0_002) with its landing at the west end: the half landing is there, 1.19 m deep | furn_f_L-1_020 |
| direction | 1 | the plan of L1 draws the same stair (f_L1_001) with its landing at the west end: the half landing is there, 1.19 m deep | furn_f_L0_002 |
| direction | 1 | the plan of L1 draws the same stair (f_L1_002) with its landing at the east end: the half landing is there, 1.24 m deep | furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_frame | 1 | every door is framed (UL122): ours (the parametric door's frame round a bare leaf); architrave on the indoor face(s) [-1] | d_L0_012 |
| door_frame | 16 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1, 1] | d_L-1_001, d_L-1_002, d_L-1_003 |
| door_frame | 1 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1] | d_L0_011 |
| door_handles | 2 | design detail of the documented flush door (black handles on both faces and 3 hinges); not in the documents | d_L1_004_handle, d_L1_005_handle |
| door_handles | 2 | design detail of the documented glazed door (black handles on both faces and 3 hinges); not in the documents | d_L1_003_handle, d_L1_006_handle |
| door_product | 2 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light); not in the documents | d_L1_004, d_L1_005 |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; glazed: door d_L1_003 opens from r_L1_koridor to the open-air r_L1_teras: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_003 |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; glazed: door d_L1_006 opens from r_L1_koridor_2 to the open-air r_L1_teras_2: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_006 |
| door_size | 2 | D5 door sizes by role and family (day door, modern style): a full-height door to the ceiling between day rooms (modern style): 2.85 m high | d_L-1_003, d_L-1_004 |
| door_size | 2 | D5 door sizes by role and family (day door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size); a full-height door to the ceiling between day rooms (modern style): 1.80 m, its head room under the sloped ceiling at its wall | d_L1_001, d_L1_002 |
| door_size | 1 | D5 door sizes by role and family (entrance door, modern style): an entrance at least an entrance door set wide (1.00 m, a pivot door; drawn 0.82 m); a pivot entrance door: 2.40 m high | d_L0_011 |
| door_size | 2 | D5 door sizes by role and family (inside door, modern style): the nearest door set width 0.80 m (drawn 0.78 m: no product size) | d_L0_006, d_L0_010 |
| door_size | 4 | D5 door sizes by role and family (inside door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L0_001, d_L0_004, d_L0_005 |
| door_size | 6 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L-1_001, d_L-1_002, d_L0_002 |
| door_size | 2 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size); a standard door: 2.10 m; its head room at its wall is 1.00 m (the roof rule) | d_L1_004, d_L1_005 |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade | 1 | facade scheme (modern): render in off white (no drawing, brief or style names the facade) | exterior |
| facade_scheme | 1 | facade scheme (modern): stone_wall_ledgestone on the basement level L-1 (not drawn) | L-1 |
| facade_scheme | 1 | facade scheme (modern): wood_cladding framing the main entrance d_L0_011 (3.0 m wide; not drawn) | w_L0_007 |
| facade_scheme | 1 | facade scheme (modern): wood_cladding on the top storey L1 over the rendered floors below (not drawn) | L1 |
| fascia_material | 1 | pitched roof: the eaves and verge edges are a fascia board in the gutter's aluminium_anthracite (not drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet) | roof |
| feature_wall | 1 | headboard panel 2.62 m wide on accent wall of r_L0_yatak_odasi: the wall behind the bed double f_L0_019 (the room's scheme limewash:warm greige: a limewash texture all round (R34)): the room's scheme limewash:warm greige: a timber headboard panel wider than the bed, a ledge on top (R32); wall panelling in 50% of 8 reference photos of the space and style | feature_wall_r_L0_yatak_odasi |
| feature_wall | 1 | headboard panel 2.62 m wide on accent wall of r_L0_yatak_odasi_2: the wall behind the bed double f_L0_020 (the room's scheme limewash:warm greige: a limewash texture all round (R34)): the room's scheme limewash:warm greige: a timber headboard panel wider than the bed, a ledge on top (R32); wall panelling in 50% of 8 reference photos of the space and style | feature_wall_r_L0_yatak_odasi_2 |
| floor | 2 | large glossy porcelain tiles: the modern family's kitchen floor (K11) | r_L-1_mutfak_floor, r_L-1_mutfak_2_floor |
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
| height | 1 | no height in the JSON; type height for sideboard | furn_f_L1_065 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 2 | no height in the JSON; type height for tv_unit | furn_f_L-1_101, furn_f_L1_063 |
| height | 8 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024, furn_f_L0_009 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 10 | window height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door: a slim anthracite metal canopy with a deeper front fascia as its drip edge (the door is drawn; the canopy is not) (inferred) | facade |
| kit:canopy_rod | 1 | the entrance canopy's two tie rods to wall plates above it (not drawn) (inferred) | facade |
| kit:canopy_soffit | 1 | the entrance canopy's wood soffit (not drawn) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:guard_glass | 1 | glass guard in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:railing | 1 | guard's metal (rails, posts, bars or a glass channel) in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| leaf_state | 3 | an outside or terrace door stays closed (an open one reads as a mistake) | d_L0_012, d_L1_003, d_L1_006 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L-1_banyo_2) | d_L-1_002 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L0_banyo_2) | d_L0_008 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L0_e_banyo_2) | d_L0_003 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L1_banyo_2) | d_L1_005 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L-1_banyo) | d_L-1_001 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L0_banyo) | d_L0_007 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L0_e_banyo) | d_L0_002 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L1_banyo) | d_L1_004 |
| leaf_state | 1 | every interior door stands open by default (UL127; an inside door); hinged at the jamb by the wall beside it (left seen from r_L0_e_yatak_odasi) | d_L0_001 |
| leaf_state | 1 | every interior door stands open by default (UL127; an inside door); hinged at the jamb by the wall beside it (left seen from r_L0_yatak_odasi) | d_L0_005 |
| leaf_state | 1 | every interior door stands open by default (UL127; an inside door); hinged at the jamb by the wall beside it (left seen from r_L0_yatak_odasi_4) | d_L0_010 |
| leaf_state | 1 | every interior door stands open by default (UL127; an inside door); hinged at the jamb by the wall beside it (right seen from r_L0_e_yatak_odasi_2) | d_L0_004 |
| leaf_state | 1 | every interior door stands open by default (UL127; an inside door); hinged at the jamb by the wall beside it (right seen from r_L0_yatak_odasi_2) | d_L0_009 |
| leaf_state | 1 | every interior door stands open by default (UL127; an inside door); hinged at the jamb by the wall beside it (right seen from r_L0_yatak_odasi_3) | d_L0_006 |
| leaf_state | 1 | every interior door stands open by default (UL127; between day rooms); hinged at the jamb by the wall beside it (left seen from r_L-1_mutfak_2) | d_L-1_004 |
| leaf_state | 1 | every interior door stands open by default (UL127; between day rooms); hinged at the jamb by the wall beside it (left seen from r_L1_oyun_aktivite_ve_dinlenme_odasi) | d_L1_001 |
| leaf_state | 1 | every interior door stands open by default (UL127; between day rooms); hinged at the jamb by the wall beside it (right seen from r_L-1_mutfak) | d_L-1_003 |
| leaf_state | 1 | every interior door stands open by default (UL127; between day rooms); hinged at the jamb by the wall beside it (right seen from r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | d_L1_002 |
| leaf_state | 1 | the entrance door stays closed (an open front door reads as a mistake) | d_L0_011 |
| left_out:door | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the modern look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the modern look; hssd_3764-1: glazing bars (the audit): the modern look wants no or few bars; hssd_4076-9: glazing bars (the audit): the modern look wants no or few bars | openings |
| left_out:entrance | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the modern look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the modern look; hssd_3764-0: glazing bars (the audit): the modern look wants no or few bars; hssd_3764-1: glazing bars (the audit): the modern look wants no or few bars; hssd_4076-9: glazing bars (the audit): the modern look wants no or few bars | openings |
| left_out:inside_door:glazed | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_1f3c6cfcdfb2a7b701692f9d: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_31a4f763e80370fb618fd10d: made for a bathroom / wc (its title): 4 glazed door(s) open into none (d_L-1_003, d_L-1_004, d_L1_001, d_L1_002); 3dwh_3befa867f6b07c735086bba4: a sliding door for a swing door; 3dwh_4555ada4db4043a2400c0747: made for a bathroom / bedroom / wc (its title): 4 glazed door(s) open into none (d_L-1_003, d_L-1_004, d_L1_001, d_L1_002); 3dwh_4d20a064a680662a23924bec: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_50f8fafc2604c495a8f2ff6f: glass 0% of its face (< 15%): not a glazed leaf; 3dwh_54d07ce98f9345c95081fc1e: glass 0% of its face (< 15%): not a glazed leaf | openings |
| left_out:inside_door:solid | 1 | models out of the style's look: 3dwh_07b2214948fc287e2651d776: glass 100% of its face (> 8%): not a solid leaf; 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_31a4f763e80370fb618fd10d: made for a bathroom / wc (its title): 6 solid door(s) open into none (d_L0_001, d_L0_004, d_L0_005, d_L0_006); 3dwh_3befa867f6b07c735086bba4: a sliding door for a swing door; 3dwh_4555ada4db4043a2400c0747: audited styles ['classic', 'modern']: mostly classic, not the modern look; 3dwh_779ae72d1a217f8a883b35b7: glass 15% of its face (> 8%): not a solid leaf; 3dwh_80ecf1763916b0e5e2bd9147: a panelled leaf: not the modern look; 3dwh_8af4cac2bbaed9252628dfb7: made for a bathroom / wc (its title): 6 solid door(s) open into none (d_L0_001, d_L0_004, d_L0_005, d_L0_006) | openings |
| left_out:terrace_door | 1 | models out of the style's look: 3dwh_5b8d6e9c0eff7893f9fe2795: patterned glass (an image on its glass): the modern look wants clear glass; hssd_3764-0: glazing bars (the audit): the modern look wants no or few bars; hssd_3764-1: glazing bars (the audit): the modern look wants no or few bars; hssd_4076-9: glazing bars (the audit): the modern look wants no or few bars; hssd_4141-3: glass 18% of its face (< 45%); hssd_4141-9: glass 18% of its face (< 45%) | openings |
| left_out:window | 1 | models out of the style's look: 3dwh_008fc2b4ab59c1a67589cb97: no see-through glass; 3dwh_16c5fdb11c4ec7d95492a04b: glazing bars (12 lites, 3.0 per m2): the modern look wants no or few bars; 3dwh_2a2ec61614b5278cf6fe1011: no see-through glass; 3dwh_48bec799740fad36241c99d9: no see-through glass; 3dwh_4a7dc5974d3b797601e64e12: audited styles ['classic', 'rustic']: mostly classic, rustic, not the modern look; 3dwh_56f518dddfda5b3c284ddf47: no see-through glass; 3dwh_5c21a04d22581a3786ae9bef: no see-through glass; 3dwh_5faa67969eb7104b4adee381: its title says 'traditional': not the modern look | openings |
| level | 1 | parking spk_001: one level at +0.80 m (level marks lm_001, lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred); no kerb along 35.9 m of its edges where another surface abuts it (its wall, coping or paving is the edge there; inferred) | platform_spk_001 |
| level | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 1.06 m up), 5 (1 x 1.16 m down), 6 (1 x 1.16 m down), 7 (2 x 1.16 m down), 8 (2 x 1.16 m down), 9 (1 x 1.16 m down), 10 (1 x 1.16 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); a flight of 1 risers of 0.068 m, tread 0.45 m down 0.07 m from edge 4 to the ground at its foot (the count settled on the ground the last riser lands on); each tread a solid block on the one below, cheek walls holding the ground beside it, a landing at its foot, a hole in the lawn (inferred); its retaining wall stops at the building on edge 2 (0.00-0.27 m) (never through the house's wall, UL148) | platform_sp_001 |
| level | 1 | terrace sp_001_s1e10: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.25..-3.94 m under it; edge: retaining (inferred) | platform_sp_001_s1e10 |
| level | 1 | terrace sp_001_s1e2: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 2.12 m over the level along its edge 2, more than the 1.2 m retaining cap); ground -2.01..-0.88 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 3 (0.00-0.37 m) (never through the house's wall, UL148) | platform_sp_001_s1e2 |
| level | 1 | terrace sp_001_s1e3: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 1.22 m over the level along its edge 3, more than the 1.2 m retaining cap); ground -2.91..-1.78 m under it; edge: retaining (inferred) | platform_sp_001_s1e3 |
| level | 1 | terrace sp_001_s1e5: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.31 m under the level along its edge 5, more than the 1.2 m retaining cap); ground -4.31..-3.42 m under it; edge: retaining (inferred) | platform_sp_001_s1e5 |
| level | 1 | terrace sp_001_s1e6: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.81 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -4.81..-3.92 m under it; edge: retaining (inferred) | platform_sp_001_s1e6 |
| level | 1 | terrace sp_001_s1e7: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.52..-4.42 m under it; edge: retaining (inferred) | platform_sp_001_s1e7 |
| level | 1 | terrace sp_001_s1e8: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.52..-4.54 m under it; edge: retaining (inferred) | platform_sp_001_s1e8 |
| level | 1 | terrace sp_001_s1e9: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.25..-4.54 m under it; edge: retaining (inferred) | platform_sp_001_s1e9 |
| level | 1 | terrace sp_001_s2e7: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.92..-4.81 m under it; edge: retaining (inferred) | platform_sp_001_s2e7 |
| level | 1 | terrace sp_001_s2e8: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.92..-5.14 m under it; edge: retaining (inferred) | platform_sp_001_s2e8 |
| level | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 12 steps up out of it on edge 3 (2.23 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0); its retaining wall stops at the building on edge 5 (1.73-1.99 m) (never through the house's wall, UL148) | platform_sp_002 |
| level | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | platform_sp_002_s1e4 |
| level | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 1 (0.84-1.20 m) (never through the house's wall, UL148) | platform_sp_002_s1e5 |
| level | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | platform_sp_002_s2e4 |
| level | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | platform_sp_002_s2e5 |
| level | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 12 steps up out of it on edge 3 (2.04 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | platform_sp_003 |
| level | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); its retaining wall stops at the building on edge 2 (0.00-0.17 m) (never through the house's wall, UL148) | platform_sp_004 |
| level | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | platform_sp_004_s1e11 |
| level | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | platform_sp_004_s1e6 |
| level | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | platform_sp_004_s1e7 |
| level | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | platform_sp_004_s1e8 |
| level | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | platform_sp_004_s2e7 |
| library_model | 1 | library door 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.82 x 2.10 m (proportions off by 12 %; the documents draw the opening, not its product); the building's one door family; another family than the entrance's; modern look: audited styles ['modern'] name modern; its leaf not seen by the audit's opening question: after the doors it saw; frames in the style's finish | d_L0_012 |
| library_model | 1 | library entrance hssd_4141-3 ('HSSD door 4141-3 (0.91 x 2.13 m)') in 1 panel(s) of 1.00 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one entrance family; modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | d_L0_011 |
| library_model | 12 | library inside door hssd_200-5 ('HSSD door 200-5 (0.81 x 2.20 m)') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_001, d_L-1_002, d_L0_001 |
| library_model | 2 | library inside door hssd_204-6 ('HSSD door 204-6 (0.93 x 2.20 m)') in 1 panel(s) of 0.80 x 1.80 m (proportions off by 6 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L1_001, d_L1_002 |
| library_model | 2 | library inside door hssd_204-7 ('HSSD door 204-7 (0.86 x 2.40 m)') in 1 panel(s) of 0.81 x 2.85 m (proportions off by 26 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_003, d_L-1_004 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 3 panel(s) of 0.72 x 2.55 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_002, win_L0_003 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 4 panel(s) of 0.67 x 2.55 m (proportions off by 7 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_001, win_L0_004 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 8 panel(s) of 0.34 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1 |
| library_model | 2 | library window hssd_3753-30 ('HSSD window 3753-30 (1.18 x 1.70 m)') in 5 panel(s) of 0.83 x 1.20 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L-1_003, win_L-1_004 |
| library_model | 2 | library window hssd_3753-7 ('HSSD window 3753-7 (1.00 x 2.60 m)') in 8 panel(s) of 0.90 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L-1_001, win_L-1_002 |
| light_well:win_L-1_002 | 1 | window sill -2.80 m, ground outside -2.83 m: an open concrete light well 0.8 m deep, 7.59 m wide (no light well drawn) | site |
| light_well:win_L-1_003 | 1 | the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well | site |
| light_well:win_L-1_004 | 1 | the terrace sp_002 at -3.00 m lies under the sill -2.10 m: no light well | site |
| modules | 28 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| opening_model | 2 | no model of the house's solid inside door family 'HSSD door 200-5 (0.81 x 2.20 m)' fits 0.80 x 1.00 m: the parametric door keeps the house's door language | d_L1_004, d_L1_005 |
| parapet | 1 | roof terrace ro_001: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| parapet_height:ro_002 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| passage_lining | 3 | design detail of the documented passage: a lined reveal (jambs and head lining in the trim), no architrave (UL122); not in the documents | o_L0_001_lining, o_L0_002_lining, o_L1_001_lining |
| path:d_L0_011 | 1 | a paved path from the entrance to the front of building copy 1 (it never runs into a building) (inferred) | site |
| path:d_L0_012 | 1 | a paved path from the entrance to the front of building copy 1 (it never runs into a building) (inferred) | site |
| path_grading | 1 | a stepped path: 13 % along is steeper than 1:12, so 3 risers of 0.108 m in 1 flight(s) (3) with level landings, treads 0.36 m, level across, stone step edges (inferred) | path_access_spk_001_1 |
| path_grading | 1 | a stepped path: 15 % along is steeper than 1:12, so 1 risers of 0.146 m in 1 flight(s) (1) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_spk_001_0 |
| path_grading | 1 | a stepped path: 18 % along is steeper than 1:12, so 3 risers of 0.106 m in 1 flight(s) (3) with level landings, treads 0.37 m, level across, stone step edges (inferred) | path_access_sp_004_0 |
| path_grading | 1 | a stepped path: 19 % along is steeper than 1:12, so 4 risers of 0.127 m in 1 flight(s) (4) with level landings, treads 0.35 m, level across, stone step edges; a handrail on the flights over 0.45 m (inferred) | path_access_sp_001_0 |
| path_grading | 1 | a stepped path: 31 % along is steeper than 1:12, so 5 risers of 0.135 m in 2 flight(s) (3/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_011 |
| path_grading | 1 | a stepped path: 31 % along is steeper than 1:12, so 5 risers of 0.145 m in 2 flight(s) (3/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_012 |
| path_grading | 1 | a stepped path: 37 % along is steeper than 1:12, so 17 risers of 0.145 m in 4 flight(s) (5/4/4/4) with level landings, treads 0.35 m, level across, stone step edges; a handrail on the flights over 0.45 m (inferred) | path_access_sp_001_1 |
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
| plant:sp_004_s1e11_plant1 | 1 | planted terrace sp_004_s1e11: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e6_plant1 | 1 | planted terrace sp_004_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e6_plant2 | 1 | planted terrace sp_004_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e7_plant1 | 1 | planted terrace sp_004_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e7_plant2 | 1 | planted terrace sp_004_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e8_plant1 | 1 | planted terrace sp_004_s1e8: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant1 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant2 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant3 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| platform:sp_001 | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 1.06 m up), 5 (1 x 1.16 m down), 6 (1 x 1.16 m down), 7 (2 x 1.16 m down), 8 (2 x 1.16 m down), 9 (1 x 1.16 m down), 10 (1 x 1.16 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); a flight of 1 risers of 0.068 m, tread 0.45 m down 0.07 m from edge 4 to the ground at its foot (the count settled on the ground the last riser lands on); each tread a solid block on the one below, cheek walls holding the ground beside it, a landing at its foot, a hole in the lawn (inferred); its retaining wall stops at the building on edge 2 (0.00-0.27 m) (never through the house's wall, UL148) | site |
| platform:sp_001_s1e10 | 1 | terrace sp_001_s1e10: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.85 m under the level along its edge 10, more than the 1.2 m retaining cap); ground -5.25..-3.94 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e2 | 1 | terrace sp_001_s1e2: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 2.12 m over the level along its edge 2, more than the 1.2 m retaining cap); ground -2.01..-0.88 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 3 (0.00-0.37 m) (never through the house's wall, UL148) | site |
| platform:sp_001_s1e3 | 1 | terrace sp_001_s1e3: step 1 of sp_001 at -1.94 m (stepped terrace: the ground lies 1.22 m over the level along its edge 3, more than the 1.2 m retaining cap); ground -2.91..-1.78 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e5 | 1 | terrace sp_001_s1e5: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.31 m under the level along its edge 5, more than the 1.2 m retaining cap); ground -4.31..-3.42 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e6 | 1 | terrace sp_001_s1e6: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 1.81 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -4.81..-3.92 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e7 | 1 | terrace sp_001_s1e7: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.52..-4.42 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e8 | 1 | terrace sp_001_s1e8: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.52..-4.54 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s1e9 | 1 | terrace sp_001_s1e9: step 1 of sp_001 at -4.16 m (stepped terrace: the ground lies 2.04 m under the level along its edge 9, more than the 1.2 m retaining cap); ground -5.25..-4.54 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e7 | 1 | terrace sp_001_s2e7: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.31 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -5.92..-4.81 m under it; edge: retaining (inferred) | site |
| platform:sp_001_s2e8 | 1 | terrace sp_001_s2e8: step 2 of sp_001 at -5.31 m (stepped terrace: the ground lies 2.12 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -5.92..-5.14 m under it; edge: retaining (inferred) | site |
| platform:sp_002 | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 12 steps up out of it on edge 3 (2.23 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0); its retaining wall stops at the building on edge 5 (1.73-1.99 m) (never through the house's wall, UL148) | site |
| platform:sp_002_s1e4 | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s1e5 | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 1 (0.84-1.20 m) (never through the house's wall, UL148) | site |
| platform:sp_002_s2e4 | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s2e5 | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | site |
| platform:sp_003 | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 12 steps up out of it on edge 3 (2.04 m, onto spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | site |
| platform:sp_004 | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); its retaining wall stops at the building on edge 2 (0.00-0.17 m) (never through the house's wall, UL148) | site |
| platform:sp_004_s1e11 | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e6 | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e7 | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e8 | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s2e7 | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | site |
| platform:spk_001 | 1 | parking spk_001: one level at +0.80 m (level marks lm_001, lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred); no kerb along 35.9 m of its edges where another surface abuts it (its wall, coping or paving is the edge there; inferred) | site |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; agent override (docs/milestone11.md §17.3) | facade |
| pool:pool_001:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_002:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_003:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool:pool_004:depth | 1 | no pool section drawn: the depth is assumed | site |
| pool_ladder | 1 | a stainless steel pool ladder on the end (edge 2) of pool_004, 0.8 m from the corner nearest the house (the documents draw the pool, not its ladder; lesson UL143; inferred) | pool_004_ladder |
| pool_ladder | 1 | a stainless steel pool ladder on the long side (edge 1) of pool_002, 0.8 m from the corner nearest the house (the documents draw the pool, not its ladder; lesson UL143; inferred) | pool_002_ladder |
| pool_ladder | 1 | a stainless steel pool ladder on the long side (edge 3) of pool_001, 0.8 m from the corner nearest the house (the documents draw the pool, not its ladder; lesson UL143; inferred) | pool_001_ladder |
| pool_ladder | 1 | a stainless steel pool ladder on the long side (edge 3) of pool_003, 0.8 m from the corner nearest the house (the documents draw the pool, not its ladder; lesson UL143; inferred) | pool_003_ladder |
| pool_seat | 2 | two sun loungers and a side table along edge 2 of pool_001, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library gap: no audited sun lounger made for outside fits, the parametric one (a teak frame on brushed steel, outdoor cushions) | pool_001_sun_lounger_0, pool_001_sun_lounger_2 |
| pool_seat | 1 | two sun loungers and a side table along edge 2 of pool_001, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library hssd_d886d10e71a0365a725abcf139142223409f7b4f ('Accent Table With Glass Top 20", Rattan,', made for outside) | pool_001_side_table_1 |
| pool_seat | 2 | two sun loungers and a side table along edge 2 of pool_003, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library gap: no audited sun lounger made for outside fits, the parametric one (a teak frame on brushed steel, outdoor cushions) | pool_003_sun_lounger_0, pool_003_sun_lounger_2 |
| pool_seat | 1 | two sun loungers and a side table along edge 2 of pool_003, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library hssd_d886d10e71a0365a725abcf139142223409f7b4f ('Accent Table With Glass Top 20", Rattan,', made for outside) | pool_003_side_table_1 |
| ridge_caps | 1 | ridge and hip caps along the roof's ridges and hips (not drawn; a tiled roof has them) | roof_ridges |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_021 (no nightstand, no lamp): the wall sconce would cover the window win_arch_r_L0_yatak_odasi_3_1 | rig_r_L0_yatak_odasi_3 |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_022 (no nightstand, no lamp): the wall sconce would cover the window win_arch_r_L0_yatak_odasi_4_1 | rig_r_L0_yatak_odasi_4 |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the curtain dec_L0_002): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the curtain dec_L0_058): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi_2 |
| rig_ceiling | 1 | ceiling fixture at (1.66, 8.60) of r_L-1_mutfak not hung: the decor pendant dec_L-1_040 hangs 0.66 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L-1_mutfak |
| rig_ceiling | 1 | ceiling fixture at (11.21, 10.34) of r_L0_koridor_2 not hung: the decor pendant dec_L0_054 hangs 1.30 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor_2 |
| rig_ceiling | 1 | ceiling fixture at (11.21, 7.41) of r_L0_koridor_2 not hung: the decor pendant dec_L0_054 hangs 1.30 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor_2 |
| rig_ceiling | 1 | ceiling fixture at (13.51, 8.63) of r_L-1_mutfak_2 not hung: the decor pendant dec_L-1_074 hangs 0.64 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L-1_mutfak_2 |
| rig_ceiling | 1 | ceiling fixture at (3.97, 10.34) of r_L0_koridor not hung: the decor pendant dec_L0_022 hangs 1.41 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor |
| rig_ceiling | 1 | ceiling fixture at (3.97, 7.41) of r_L0_koridor not hung: the decor pendant dec_L0_022 hangs 1.41 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor |
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_058; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026, above the mirror dec_L-1_057 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_069; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_068 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L-1_koridor: ceiling fixture at the pole of inaccessibility of r_L-1_koridor, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_073); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L-1_koridor_2, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_067); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_091 over the counter f_L-1_001; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_092 over the counter f_L-1_002; 299.1 lm -> 0.785 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_2_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_093 over the counter f_L-1_002; 357.2 lm -> 0.9377 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_3_light |
| rig_light | 1 | r_L-1_mutfak: the ceiling light of the zone (spot(s) (1.66, 8.60)) in the decor pendant dec_L-1_040 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_097 over the counter f_L-1_010; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_098 over the counter f_L-1_011; 355.4 lm -> 0.9331 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_2_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_099 over the counter f_L-1_011; 298.6 lm -> 0.7837 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_3_light |
| rig_light | 1 | r_L-1_mutfak_2: the ceiling light of the zone (spot(s) (13.51, 8.63)) in the decor pendant dec_L-1_074 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_4_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027 under the decor pendant dec_L-1_139; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038 under the decor pendant dec_L-1_156; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_040; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003, above the mirror dec_L0_039 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_044; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_043 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_025 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_028; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_027 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_031 is taken by the vase dec_L0_111); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_020); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: the decor pendant dec_L0_016 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_pendant_3_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_033 is taken by the vase dec_L0_118); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_052); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: the decor pendant dec_L0_048 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_pendant_3_light |
| rig_light | 1 | r_L0_koridor: the ceiling light of the zone (spot(s) (3.97, 7.41); (3.97, 10.34)) in the decor pendant dec_L0_022 (UL170: the pendant is the zone's light), 4400 lm over its 4 bulb(s); bulb 1/4; 1100.0 lm -> 1.56 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light |
| rig_light | 1 | r_L0_koridor: the ceiling light of the zone (spot(s) (3.97, 7.41); (3.97, 10.34)) in the decor pendant dec_L0_022 (UL170: the pendant is the zone's light), 4400 lm over its 4 bulb(s); bulb 2/4; 1100.0 lm -> 1.56 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_2_light |
| rig_light | 1 | r_L0_koridor: the ceiling light of the zone (spot(s) (3.97, 7.41); (3.97, 10.34)) in the decor pendant dec_L0_022 (UL170: the pendant is the zone's light), 4400 lm over its 4 bulb(s); bulb 3/4; 1100.0 lm -> 1.56 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_3_light |
| rig_light | 1 | r_L0_koridor: the ceiling light of the zone (spot(s) (3.97, 7.41); (3.97, 10.34)) in the decor pendant dec_L0_022 (UL170: the pendant is the zone's light), 4400 lm over its 4 bulb(s); bulb 4/4; 1100.0 lm -> 1.56 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_4_light |
| rig_light | 1 | r_L0_koridor_2: the ceiling light of the zone (spot(s) (11.21, 7.41); (11.21, 10.34)) in the decor pendant dec_L0_054 (UL170: the pendant is the zone's light), 4400 lm over its 1 bulb(s); bulb 1/1; 4400.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 5 bulb(s); bulb 1/5; 220.0 lm -> 0.624 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 5 bulb(s); bulb 2/5; 220.0 lm -> 0.624 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_4_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 5 bulb(s); bulb 3/5; 220.0 lm -> 0.624 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_5_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 5 bulb(s); bulb 4/5; 220.0 lm -> 0.624 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_6_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 5 bulb(s); bulb 5/5; 220.0 lm -> 0.624 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_7_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_062 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: the decor pendant dec_L0_059 gives light (UL170: every pendant is a light), 1100 lm over its 3 bulb(s); bulb 1/3; 366.7 lm -> 1.04 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_2: the decor pendant dec_L0_059 gives light (UL170: every pendant is a light), 1100 lm over its 3 bulb(s); bulb 2/3; 366.7 lm -> 1.04 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_pendant_4_light |
| rig_light | 1 | r_L0_yatak_odasi_2: the decor pendant dec_L0_059 gives light (UL170: every pendant is a light), 1100 lm over its 3 bulb(s); bulb 3/3; 366.7 lm -> 1.04 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_pendant_5_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_032 on f_L0_043 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: the decor pendant dec_L0_031 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_pendant_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_073 on f_L0_046 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: the decor pendant dec_L0_072 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_pendant_2_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_031); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_035); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_015; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_046; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L-1_019, furn_f_L-1_020 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.150 m / 18 drawn risers | furn_f_L0_001, furn_f_L0_002 |
| road:road_link_spk_001_2 | 1 | the drive spk_001 ended at the lawn 5.0 m short of the plot's edge: it runs on in its paving to the edge (lesson UL162; inferred) | site |
| road:street_1 | 1 | the street outside the plot the drive joins, 6 m wide along the plot's edge (no road drawn; lesson UL162; inferred) | site |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| see_through | 1 | the master bedroom's wardrobe run (modern style): horizontal black slat sliding doors with its garments and an LED strip showing through (UL120); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_023 |
| sill | 2 | outside sill 2.2285 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill, win_L0_003_sill |
| sill | 2 | outside sill 2.743 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_arch_r_L0_yatak_odasi_3_1_sill, win_arch_r_L0_yatak_odasi_4_1_sill |
| sill | 2 | outside sill 2.7431 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill, win_L0_004_sill |
| sill | 2 | outside sill 4.2173 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_003_sill, win_L-1_004_sill |
| sill | 2 | outside sill 7.2461 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_001_sill, win_L-1_002_sill |
| sill_height | 10 | window sill_height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 20 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1_salon, skirting_r_L-1_salon_2, skirting_r_L-1_mutfak |
| slab_band | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_001, f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L-1_003 | splashback_r_L-1_mutfak |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_010, f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L-1_004 | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_003 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_004 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_012 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_013 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_067 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_068 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak_2 |
| splashback_look | 2 | the worktop's stone up the wall: the modern family's stone splashback (K5) | splashback_r_L-1_mutfak, splashback_r_L-1_mutfak_2 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_002 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_002 (100% of the smaller footprint; slab opening sv_L1_002); read as its upper end, not built as a second flight | f_L1_001 |
| stair_finishes | 4 | the house's style family (H8); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| suspension | 1 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L0_022_cord |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| terrace_railing | 1 | roof terrace ro_001: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_001 |
| terrace_railing | 1 | roof terrace ro_002: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_002 |
| tree | 27 | bush of the drawn size, 0.8 m tall (height assumed) | tree_sp_001_s1e2_plant1, tree_sp_001_s1e3_plant1, tree_sp_001_s1e5_plant1 |
| tree | 21 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 1 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001, furn_f_L0_002 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 5 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L-1_019, furn_f_L-1_020 |
| under_roof | 2 | its head room under the sloped ceiling is only 1.00 m (under 1.60 m) and no spot within 0.5 m along its wall leaves more: lowered to 1.00 m so nothing crosses the roof; it needs a dormer or a raised roof (review) | d_L1_004, d_L1_005 |
| under_roof | 2 | wardrobe 2.10 m high where the sloped ceiling over its footprint leaves 1.80 m: built 1.80 m high (UL128) | furn_f_L1_027, furn_f_L1_028 |
| void_guard | 1 | floor opening 0 of L0 (f_L-1_019 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.53 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L0_0 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.37 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| void_guard | 1 | floor opening 1 of L0 (f_L-1_020 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L0_1 |
| void_guard | 1 | floor opening 1 of L1 (f_L0_002 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_1 |
| waist | 4 | the house's style (modern: plate structure, glass panels under a steel handrail, steel strings (glass channel language of the house)); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_clear | 1 | covered by the wardrobe f_L0_009 in front of its wall, its top 1.94 m (build): a wall item stays clear of what stands in front of it (UL139); moved to another free wall of the room | dec_L0_035 |
| wall_clear | 1 | covered by the wardrobe f_L0_010 in front of its wall, its top 1.94 m (build): a wall item stays clear of what stands in front of it (UL139) | dec_L0_094 |
| wall_clear | 1 | covered by the wardrobe f_L0_011 in front of its wall, its top 1.96 m (build): a wall item stays clear of what stands in front of it (UL139); moved to another free wall of the room | dec_L0_076 |
| wall_clear | 1 | over the door d_L0_011 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_104 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_3_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_030 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_071 |
| wall_gap_m | 1 | the drawn shower reaches 0.1 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_014 |
| wall_gap_m | 1 | the drawn shower stands 2.1 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_013 |
| wall_gap_m | 5 | the drawn tall_cabinet stands 2.0 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L-1_103, furn_f_L-1_104, furn_f_L0_047 |
| wall_gap_m | 2 | the drawn toilet reaches 1.1 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_015, furn_f_L0_016 |
| wall_gap_m | 4 | the drawn toilet reaches 1.3 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L-1_051, furn_f_L-1_052, furn_f_L1_021 |
| wall_gap_m | 2 | the drawn toilet reaches 1.4 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_017, furn_f_L0_018 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_001 into r_L-1_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_001 into r_L-1_koridor_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_002 into r_L-1_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_002 into r_L-1_koridor, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_003 into r_L-1_koridor_2, on the latch side, assumed on the side with more free wall (3.56 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_003 into r_L-1_mutfak, on the latch side, assumed on the side with more free wall (0.22 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_mutfak_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_004 into r_L-1_koridor, on the latch side, assumed on the side with more free wall (3.56 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_004 into r_L-1_mutfak_2, on the latch side, assumed on the side with more free wall (0.22 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_mutfak_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_001 into r_L0_e_yatak_odasi, on the latch side, assumed on the side with more free wall (0.44 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_yatak_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_001 into r_L0_koridor, on the latch side, assumed on the side with more free wall (0.26 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_002 into r_L0_e_banyo, on the latch side, assumed on the side with more free wall (0.52 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_003 into r_L0_e_banyo_2, on the latch side, assumed on the side with more free wall (0.40 m against 0.02 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_003 into r_L0_e_yatak_odasi_2, on the latch side, assumed on the side with more free wall (1.67 m against 0.45 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_yatak_odasi_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_004 into r_L0_e_yatak_odasi_2, on the latch side, assumed on the side with more free wall (0.45 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_004 into r_L0_koridor_2, on the latch side, assumed on the side with more free wall (0.26 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_005 into r_L0_yatak_odasi, on the latch side, assumed on the side with more free wall (4.32 m against 0.04 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_006 into r_L0_yatak_odasi_3, on the latch side, assumed on the side with more free wall (3.62 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_3_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_007 into r_L0_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.31 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_008 into r_L0_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.31 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_009 into r_L0_yatak_odasi_2, on the latch side, assumed on the side with more free wall (4.32 m against 0.04 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_010 into r_L0_yatak_odasi_4, on the latch side, assumed on the side with more free wall (3.62 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_4_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_001 into r_L1_oyun_aktivite_ve_dinlenme_odasi, on the latch side, assumed on the side with more free wall (4.49 m against 0.09 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_002 into r_L1_oyun_aktivite_ve_dinlenme_odasi_2, on the latch side, assumed on the side with more free wall (4.49 m against 0.09 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_004 into r_L1_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_004 into r_L1_koridor, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_005 into r_L1_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_005 into r_L1_koridor_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the outside door d_L0_012 (solid), on the latch side, assumed on the side with more free wall (0.11 m against 0.00 m; the documents give no hinge side), its centre 0.10 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch beside the outside door d_L1_003 (solid), on the latch side, assumed on the side with more free wall (0.67 m against 0.34 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_01 |
| wall_plate | 1 | inferred: a light switch beside the outside door d_L1_006 (solid), on the latch side, assumed on the side with more free wall (0.67 m against 0.34 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch on the wall next to the open side o_L-1_001 (a separator line, no wall), the room's only way in, 0.47 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L-1_salon_01 |
| wall_plate | 1 | inferred: a light switch on the wall next to the open side o_L-1_002 (a separator line, no wall), the room's only way in, 0.27 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L-1_salon_2_01 |
| wall_plate | 1 | inferred: a light switch on the wall next to the outside door d_L0_011 (entrance), as beside it the intercom dec_L0_104, 0.08 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_01 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_027 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_028 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_029 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_030 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_04 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_057, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_068, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_039, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_043, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_028, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_032, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (left side) beside its nightstand f_L0_031, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (right side) beside its nightstand f_L0_032, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (left side) beside its nightstand f_L0_034, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (right side) beside its nightstand f_L0_033, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (left side) over its nightstand f_L0_041 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (right side) over its nightstand f_L0_042 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (left side) over its nightstand f_L0_045 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (right side) over its nightstand f_L0_044 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (left side) over its nightstand f_L0_043 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_3_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (right side) beside its desk f_L0_029, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (left side) beside its desk f_L0_028, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (right side) over its nightstand f_L0_046 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_4_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (1.55 m), 0.30 m over the floor | plate_r_L1_koridor_03, plate_r_L1_koridor_2_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (3.26 m), 0.30 m over the floor | plate_r_L-1_koridor_03, plate_r_L-1_koridor_2_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (3.63 m), 0.30 m over the floor | plate_r_L0_koridor_03, plate_r_L0_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.28 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.51 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_06 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.72 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.42 m, 0.30 m over the floor | plate_r_L-1_salon_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.87 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_02 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 2.98 m, 0.30 m over the floor | plate_r_L-1_salon_04, plate_r_L-1_salon_2_04 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 3.63 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_05, plate_r_L0_yatak_odasi_4_05 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.33 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_05, plate_r_L0_yatak_odasi_2_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 4.37 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 4.87 m, 0.30 m over the floor | plate_r_L-1_salon_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 4.95 m, 0.30 m over the floor | plate_r_L-1_salon_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 5.53 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_02 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 6.78 m, 0.30 m over the floor | plate_r_L-1_salon_2_02 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_025, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_02 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_027, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_101 beside it, 0.30 m over the floor | plate_r_L-1_salon_02 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_002 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_03 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_003 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_02 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_011 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_03 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_012 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_02 |
| wet_walls | 1 | the modern family's bathroom (FAMILY_BATH): large-format stone-look porcelain 60 x 120 cm in greige on the walls, floor to ceiling (UL114 B8; the brief names no wet-room tiles) | style |
| winders | 4 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_salon (rung None), r_L0_e_yatak_odasi (rung None), r_L0_yatak_odasi (rung None), r_L0_yatak_odasi_3 (rung None), r_L1_oyun_aktivite_ve_dinlenme_odasi (rung None), r_L1_teras (rung None).

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial], 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_56d1c005237fa418b00eede5 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_8e456b89888577abcc0a5025 [non_commercial], 3dwh_a4e1395f626c963c2082d2a3 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_classic_3_6a0eb8d8 [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], gen_potted_plant_modern_1_8fbfec3c [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_652536faa9c5028ed8be69780c120af78c141968 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial], hssd_d7c839146e84643d034b5eff9b1142e5445af7af [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_652536faa9c5028ed8be69780c120af78c141968 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: yes
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: gen_potted_plant_modern_1_8fbfec3c [tool_nc])
- cam_r_L-1_mutfak_3: commercial-safe: yes
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_a4e1395f626c963c2082d2a3 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_35f3b93046ba64bbe233ca01f9e59d01c1d4cad9 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: yes
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: yes
- cam_r_L0_e_banyo_2: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_1: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_56d1c005237fa418b00eede5 [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_56d1c005237fa418b00eede5 [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], gen_potted_plant_classic_3_6a0eb8d8 [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], gen_potted_plant_classic_3_6a0eb8d8 [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_d7c839146e84643d034b5eff9b1142e5445af7af [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: yes
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_8e456b89888577abcc0a5025 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_8e456b89888577abcc0a5025 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])

## Built below library level (Milestone 13)

64 furniture piece(s) built from a module builder or a parametric family instead of a library model: 4 library gap(s) to close with a real model, 60 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1_025 | washbasin | module | bath_set | r_L-1_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L-1_026 | washbasin | module | bath_set | r_L-1_banyo | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L-1_027 | table_dining | module | table_long | r_L-1_salon | living | from_documents | yes | module builder table_long (3 module(s): dining table 3.35 x 1.00 m on trestles) |
| f_L-1_038 | table_dining | module | table_long | r_L-1_salon_2 | living | from_documents | yes | module builder table_long (3 module(s): dining table 3.35 x 1.00 m on trestles) |
| f_L-1_051 | toilet | parametric | parametric:toilet | r_L-1_banyo | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L-1_052 | toilet | parametric | parametric:toilet | r_L-1_banyo_2 | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L-1_067 | sink_kitchen | module | kitchen_run | r_L-1_mutfak | kitchen | from_documents | no (by design) | - |
| f_L-1_068 | sink_kitchen | module | kitchen_run | r_L-1_mutfak_2 | kitchen | from_documents | no (by design) | - |
| f_L-1_073 | table_coffee | parametric | parametric:table_coffee | r_L-1_salon | living | from_documents | no (by design) | - |
| f_L-1_074 | table_coffee | parametric | parametric:table_coffee | r_L-1_salon_2 | living | from_documents | no (by design) | - |
| f_L0_001 | stair | parametric | parametric:stair | r_L0_merdiven | hall | from_documents | no (by design) | - |
| f_L0_002 | stair | parametric | parametric:stair | r_L0_merdiven_2 | hall | from_documents | no (by design) | - |
| f_L0_003 | washbasin | module | bath_set | r_L0_banyo | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L0_004 | washbasin | module | bath_set | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L0_005 | washbasin | module | bath_set | r_L0_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L0_006 | washbasin | module | bath_set | r_L0_e_banyo | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L0_013 | shower | module | bath_set | r_L0_e_banyo | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L0_014 | shower | module | bath_set | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L0_015 | toilet | parametric | parametric:toilet | r_L0_e_banyo | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L0_016 | toilet | parametric | parametric:toilet | r_L0_e_banyo_2 | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L0_017 | toilet | parametric | parametric:toilet | r_L0_banyo_2 | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L0_018 | toilet | parametric | parametric:toilet | r_L0_banyo | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L0_023 | wardrobe | module | module:wardrobe:wardrobe_run | r_L0_e_yatak_odasi | bedroom | from_documents | yes | module builder wardrobe_run (7 module(s): PAX frame 100x58x202 cm) |
| f_L0_024 | wardrobe | module | wardrobe_run | r_L0_e_yatak_odasi_2 | bedroom | from_documents | yes | module builder wardrobe_run (7 module(s): PAX frame 100x58x202 cm) |
| f_L0_031 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi | bedroom | from_documents | no (by design) | - |
| f_L0_032 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi | bedroom | from_documents | no (by design) | - |
| f_L0_033 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi_2 | bedroom | from_documents | no (by design) | - |
| f_L0_034 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi_2 | bedroom | from_documents | no (by design) | - |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L1_002 | stair | parametric | parametric:stair | r_L1_koridor | hall | from_documents | no (by design) | - |
| f_L1_015 | washbasin | module | bath_set | r_L1_banyo | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L1_016 | washbasin | module | bath_set | r_L1_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L1_021 | toilet | parametric | parametric:toilet | r_L1_banyo | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L1_022 | toilet | parametric | parametric:toilet | r_L1_banyo_2 | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L-1_090 | fridge | module | kitchen_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_091 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_092 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_093 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_041 | nightstand | parametric | parametric:nightstand | r_L0_yatak_odasi | bedroom | added_by_ai | no (by design) | - |
| f_L0_042 | nightstand | parametric | parametric:nightstand | r_L0_yatak_odasi | bedroom | added_by_ai | no (by design) | - |
| f_L-1_096 | fridge | module | kitchen_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_097 | wall_cabinet | module | wall_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_098 | wall_cabinet | module | wall_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L-1_099 | wall_cabinet | module | wall_run | r_L-1_mutfak_2 | kitchen | added_by_ai | no (by design) | - |
| f_L0_044 | nightstand | parametric | parametric:nightstand | r_L0_yatak_odasi_2 | bedroom | added_by_ai | no (by design) | - |
| f_L0_045 | nightstand | parametric | parametric:nightstand | r_L0_yatak_odasi_2 | bedroom | added_by_ai | no (by design) | - |
| f_L-1_101 | tv_unit | parametric | parametric:tv_unit | r_L-1_salon | living | added_by_ai | no (by design) | - |
| f_L-1_103 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L-1_104 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_047 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_e_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_048 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_049 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 3), cam_r_L1_teras_2 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.0 degrees off the sun, sky pull k 3), ext_5 (5.6 degrees off the sun, sky pull k 0).

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

Assets: textures CC0 x 46; furniture/decor models 3DWH-UNREVIEWED x 54, CC-BY-4.0 x 117, CC-BY-NC-4.0 x 54, CC0 x 1, generated (Infinigen v1.19.0, BSD-3-Clause) x 3, generated (TRELLIS.2-4B, MIT) x 24 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 36 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_119)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_048)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_005)
- "Candle" by deniska40k (https://sketchfab.com/3d-models/c408586d8c1547448c4ff47abb4fb981), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_035)
- "Candle light" by al0sral0 (https://sketchfab.com/3d-models/d9d5ed5de83b4d899ab93f55bdc3d0bc), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_122)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261030-112241-full-20261030T112730Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 50.0 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 108.7 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.4 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.6 min | answers applied |
| fit | ok | 10.7 s | - |
| layout | ok | 54.2 s | - |
| decor_ask | ok | 4.1 s | - |
| photos | reused | 0.2 s | - |
| assets | ok | 4.3 s | - |
| decor | ok | 11.2 s | - |
| agent_apply | ok | 48.6 s | - |
| refit | ok | 114.3 s | - |
| build | ok | 40.9 min | - |
| agent_previews | ok | 9.3 min | 36 view(s) |
| agent | ok | 69.5 min | 4 round(s), 30 finding(s) removed by 90 accepted edit(s) (measured; 213 predicted by the dry re-checks), 17 new, net 13, 291 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 19.7 min | - |
| export | ok | 6.8 min | - |
| controls | ok | 115.8 s | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.3 min | - |
| check | ok | 4.1 min | - |
| combine | ok | 24.9 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 90 edit(s) accepted, 291 rejected, 766 model calls (10469285 tokens), 79.7 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 23128): earlier runs of the appended log are left out (23127 events, 7697 model calls, 717 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 90 / 291 (24 % accepted) |
| rejected by reason | acceptance 70, memory 35, max_tries 25, score 25, no_change 21 |
| rooms checked by code / vision / planner | 38 / 14 / 30 |
| rooms with fixable critical or major findings visited | 30 of 30 |
| critical before -> after (after: round 4's critics, before its 11 accepted edit(s)) | 3 -> 3 |
| major before -> after (after: round 4's critics, before its 11 accepted edit(s)) | 343 -> 561 |
| agent minutes; first accepted edit after | 72.55; 6.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 35; 111; 98 (62) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 30 measured; 213 predicted (the last round's dry re-checks predicted 63 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 84 new; net -54 |
| edits removing their finding | 9 of 62 |
| plans ok / empty / refused / default | 62 / 27 / 6 / 3 |

### What the AI inspector saw on the final renders

541 vision finding(s) (59 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 62 fixed in the final round, 5 handed to the stage that owns them, 559 open; the architect leaves 0 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`.

Still open or handed on (critical and major):

- major D2 f_L0_009: The wardrobe has a large glass pane in its central door, which is an incorrect object for a standard wardrobe and looks like a window or mir (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major V1 f_L-1_056: bad_camera: The camera is positioned too close to the corner, framing only the edge of the bathtub and a blank wall. It fails to show the ro (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major Q12 f_L-1_056: a bathroom that is not designed: The visible portion of the bathtub is bare. There are no taps visible in the frame, no towel rail, and the  (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the reference has a styled coffee table and shelves; the render has a bare worktop with only a bowl of fruit (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the reference has a stylish ring light and warm ambient lighting; the render is lit by flat, cool daylight which  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the worktops are completely bare, lacking the kettles, jars, or decor seen in the reference) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the lighting is flat and cool, lacking the warm, inviting glow of the reference) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the lighting is flat and cool, lacking the warm ambient glow seen in the reference) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the counters are almost entirely bare, lacking the curated objects, plants, or textiles that make a kitchen  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L-1_053: missing layer: cohesive seating set - the white corner sofa, the dark blue sofa and the white armchair are three different styles and colour (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_053: missing layer: feature wall - the wall behind the seating is flat, untextured concrete with no fluted/slatted panelling, wainscot or accent, (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_061: missing layer: rug - there is no large rug under the seating group to anchor it; the reference shows a patterned area rug defining the zone (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_101: missing layer: styled surfaces - the TV unit, coffee table and shelves are essentially bare; the reference shows styled consoles with books, (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_053: missing layer: wall art - the large concrete walls are completely empty of frames or art, making the room feel unfinished versus the referen (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 win_L-1_001: missing layer: furnished outdoor terrace - the view through the glazing is a flat, empty lawn with no seating, planters, rug or lanterns, so (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L-1_087: missing layer: styled surfaces. The coffee table (f_L-1_087) and the dark side table in the foreground are nearly bare. The reference shows  (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_053: missing layer: rug. The seating group (f_L-1_053) sits directly on the wood floor. The reference uses a large patterned rug to anchor the sp (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_024: missing layer: feature wall. The wall behind the dining area and the main living wall are flat, untextured concrete/paint. The reference sty (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_027: mismatched_set: The room contains too many conflicting wood tones and styles. The dark walnut side table in the foreground clashes with the  (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_027: mismatched_set: The dining table and chairs (f_L-1_027 through f_L-1_037) are a generic, heavy, dark-wood set that clashes with the light, m (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 r_L-1_salon: missing layer: feature wall: The wall behind the sofa is a flat, untextured concrete/paint surface. The reference style calls for a feature  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 win_L-1_001: missing layer: layered curtains: The large window wall is completely bare. It lacks the full-height, two-layer curtains (sheer and drape) th (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L-1_061: missing layer: styled surfaces: The coffee table (f_L-1_061) and the sideboard area are empty. They need styling with books, vases, or art t (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major V1 d_L0_007: bad_camera: The camera is positioned too close to the door frame and vanity, cutting off the rest of the bathroom. The main pieces (bathtub, (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major Q4 f_L0_025: missing_anchor: The bathtub (f_L0_025) is a primary piece for a bathroom of this size but is completely absent from the frame, making the ro (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)

### Argus, the auditor

Score 3.6 / 100 (100 = nothing open): 12 critical, 388 major, 144 minor open. By kind (critical + major): lost 53, taste 112, misread 31, geometry 60, no_sense 54, other 26, process 23, silent 19, reference_missed 8, detached 7, stale 6, untyped 1. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- misread r_L1_teras: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- taste cam_r_L1_banyo_1: Argus: Argus: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. This is a failed rende
- lost MTEXT:2C809:0: the documents name a room 'SALON' (46 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80A:0: the documents name a room 'AÇIK MUTFAK' (8.5 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80B:0: the documents name a room 'BANYO' (4.9 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80C:0: the documents name a room 'KORİDOR' (7 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C813:0: the documents name a room 'ODA' (13 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F038:0: the documents name a room 'SALON' (46 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F039:0: the documents name a room 'AÇIK MUTFAK' (8.5 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F03A:0: the documents name a room 'BANYO' (4.9 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F03B:0: the documents name a room 'KORİDOR' (7 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F041:0: the documents name a room 'ODA' (13 m²) on L-1b; no room of the model uses it

Library gaps reported by the agent: kitchen_counter (No audited kitchen_counter library model exists to swap f_L-1_003 to a correct working height (M2: top at 1.18 m over 0.97 m); the piece is a module build of the kitchen run.), toilet (Toilet f_L1_021 built below library level (P7) and its swap_model was rejected (asset audited out); no usable library model exists for this toilet.), toilet modern minimal (No audited real toilet model with a width narrow enough (≤ ~0.45 m) to give the drawn 0.5 m-wide toilet the 0.38 m side clearance G10 needs; only generated models exist and pins to them are refused.), washbasin (No audited library model of washbasin fits the drawn 1.0x0.55 m footprint with a floor-sitting base; the current model floats 0.384 m above the floor (S1).), toilet (No audited library model of toilet fits the drawn 0.5x0.68 m footprint with a floor-sitting base; the current model floats 0.200 m above the floor (S1).), toilet (No audited toilet model passes the fit rules for the drawn 0.50 x 0.69 m footprint (generated models refused on caps/height; the one real candidate was audit-removed), so the S1 floating lowest point and G10 left clearance stay.), sofa (Record the library gap for the parametric sofa f_L-1b_042 so it is tracked and not re-attempted.), washbasin (Washbasin f_L1_015 floats +0.384 m above its floor (S1); as drawn fixed equipment it cannot be moved or resized, and no audited library model fits the 5 m2 bathroom bay.), toilet (Toilet f_L1_021 floats +0.200 m above its floor (S1), is built below library level (Q12) and has a 0.33 m side clearance (G10); as drawn fixed equipment it cannot be moved or resized, and no audited library model fits the 5 m2 bathroom bay.), kitchen_counter (No audited library model of kitchen_counter exists (catalog count 0), so the 1.18 m top of f_L-1_012 cannot be corrected by swap_model; the piece is a module build of the drawn kitchen run.), toilet (No audited library toilet model fits: all generated models fail the height/fit caps or are audit-removed, so the parametric mesh stays (a:F144, a:F259, c:S1:f_L1_022).), washbasin (No audited library washbasin model fits: all generated models fail the height/fit caps, so the floating model stays (c:S1:f_L1_016).), washbasin (Washbasin model floats 0.384 m above its floor (S1); all candidate swap assets were audit-removed, so no audited library model fixes the geometry.), toilet (Toilet model floats 0.200 m above its floor (S1) and fails the 0.38 m left clearance (G10); swap attempts were rejected (audit-removed or fit-rule failures) and the piece hit max tries, so no audited library model fixes it.), washbasin (Washbasin model floats 0.384 m above the floor (S1); all swap_model attempts were rejected (fit rules or audit-removed assets), so no valid floor-standing washbasin model exists in the current library.), toilet (Toilet model floats 0.200 m above the floor (S1); all swap_model attempts were rejected (fit rules or audit-removed assets), so no valid floor-standing toilet model exists in the current library.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 | 343 | 113 | 14 | 29 | 96 | layout | 36 |
| 2 | 3 | 329 | 107 | 14 | 33 | 111 | layout | 36 |
| 3 | 3 | 324 | 109 | 14 | 17 | 64 | layout | 36 |
| 4 | 3 | 561 | 166 | 29 | 11 | 20 | layout | 36 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A6 | 0 | 40 | 0 | 0 |
| AI1 | 0 | 45 | 0 | 16 |
| AI3 | 0 | 14 | 0 | 0 |
| AI5 | 0 | 38 | 0 | 0 |
| B8 | 0 | 0 | 0 | 10 |
| C1 | 0 | 0 | 0 | 7 |
| C7 | 0 | 40 | 0 | 0 |
| D2 | 0 | 5 | 0 | 0 |
| D3 | 0 | 182 | 55 | 0 |
| F1 | 0 | 0 | 5 | 0 |
| F2 | 0 | 36 | 0 | 0 |
| F3 | 0 | 50 | 0 | 0 |
| F4 | 0 | 92 | 0 | 0 |
| F6 | 0 | 46 | 0 | 0 |
| F9 | 0 | 31 | 0 | 0 |
| G1 | 0 | 0 | 26 | 0 |
| G10 | 0 | 140 | 0 | 0 |
| G11 | 0 | 48 | 0 | 0 |
| G12 | 0 | 25 | 0 | 0 |
| G13 | 0 | 34 | 0 | 0 |
| G14 | 0 | 0 | 5 | 0 |
| G2 | 0 | 18 | 16 | 0 |
| G3 | 0 | 27 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 52 | 0 | 0 |
| G6 | 0 | 26 | 8 | 0 |
| G8 | 0 | 18 | 8 | 0 |
| G9 | 0 | 8 | 0 | 0 |
| J1 | 0 | 73 | 0 | 28 |
| K1 | 0 | 13 | 0 | 0 |
| K3 | 0 | 8 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 24 | 0 |
| M13 | 0 | 0 | 12 | 0 |
| M17 | 0 | 0 | 8 | 0 |
| M18 | 0 | 8 | 0 | 0 |
| M2 | 0 | 8 | 0 | 0 |
| M21 | 0 | 2 | 18 | 0 |
| M22 | 0 | 8 | 0 | 0 |
| M23 | 0 | 8 | 8 | 0 |
| M26 | 0 | 0 | 20 | 0 |
| M28 | 0 | 6 | 16 | 0 |
| M30 | 0 | 0 | 16 | 0 |
| M31 | 0 | 8 | 0 | 0 |
| M33 | 0 | 25 | 4 | 0 |
| M34 | 0 | 0 | 16 | 0 |
| NR | 0 | 16 | 0 | 0 |
| P0 | 0 | 60 | 0 | 0 |
| P10 | 0 | 2 | 0 | 0 |
| P2 | 0 | 13 | 0 | 0 |
| P6 | 0 | 1 | 0 | 0 |
| P7 | 0 | 18 | 0 | 0 |
| P9 | 0 | 0 | 0 | 5 |
| Q10 | 0 | 29 | 1 | 0 |
| Q11 | 0 | 1 | 0 | 0 |
| Q12 | 0 | 45 | 2 | 0 |
| Q13 | 0 | 0 | 1 | 0 |
| Q14 | 0 | 17 | 5 | 0 |
| Q15 | 0 | 0 | 2 | 0 |
| Q4 | 8 | 26 | 0 | 0 |
| Q5 | 0 | 5 | 1 | 0 |
| Q7 | 0 | 0 | 2 | 0 |
| R3 | 0 | 0 | 32 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S1 | 0 | 64 | 0 | 0 |
| S2 | 0 | 9 | 32 | 0 |
| S4 | 0 | 0 | 2 | 0 |
| S5 | 0 | 0 | 42 | 0 |
| V1 | 4 | 33 | 3 | 0 |
| X2 | 0 | 2 | 8 | 0 |
| X3 | 0 | 3 | 0 | 5 |
| X5 | 0 | 0 | 55 | 0 |
| X6 | 0 | 12 | 0 | 0 |
| X9 | 0 | 5 | 0 | 0 |
| lighting_dark | 0 | 8 | 4 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 23632 | 1 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace is a furnished outdoor space; its program group is absent. (fixes a:F19) | ![](agent/r1_001_place_group_before_r_L1_teras.png) | ![](agent/r1_002_place_group_after_r_L1_teras.png) |
| 23633 | 1 | set_camera | r_L1_banyo | agent_override | - | Argus: The camera is mis-posed; re-aiming it at the bathroom's main pieces will produce a valid view. (fixes a:F28) | - | - |
| 23650 | 1 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The bed f_L0_019 is cut out of the frame. Setting the camera to show the bed (the code picks the free pose) fixes the render. This is the camera half of F146; the bed itself is fixed by the agent_round in F146. (fixes a:F149) | - | - |
| 23651 | 1 | set_camera | r_L0_banyo | agent_override | - | Argus: The render omits the washbasin, toilet and tall cabinet. swap_model was refused (fit rules), so the cause is the camera, not the model. Setting the camera to show the primary fixtures fixes the render. (fixes a:F150) | - | - |
| 23657 | 1 | set_material | plot_wall | agent_override | - | Argus: The retaining wall looks unfinished. Setting the material to a stone look will match the facade. (fixes a:F170) | - | - |
| 23661 | 1 | set_exterior | exterior:ground,site | agent_override | - | Argus: The outdoor setting is a flat untextured plane with faint floating trees; the site stage built a bare ground with too few trees. Setting a grass ground and a full hedge with 12 trees gives the terrace a real, designed outdoor context. (fixes a:F179) | - | - |
| 23663 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the terrace with the top solver candidate to build the missing seating group and planters and clear the armchair from the window. | ![](agent/r1_063_relayout_room_before_r_L1_teras.png) | ![](agent/r1_064_relayout_room_after_r_L1_teras.png) |
| 23677 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 1 relayout adds a proper terrace lounge set for the 19.7 m² balcony, moves the potted plants clear of window win_L1_002, and replaces the armchairs with a model without the 5.2 cm rest gap. | ![](agent/r1_078_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_079_relayout_room_after_r_L1_teras_2.png) |
| 23682 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 41.0 -> 41.0 | Label 'Oyun Aktivite Ve Dinlenme Odası' and furniture (sofas, tv_unit, dining) indicate a living/relaxation room, not 'other'. | ![](agent/r1_089_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_094_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 23689 | 1 | move_piece | f_L-1_039 | adjusted_by_ai | 30.0 -> 30.0 | Nudge chair f_L-1_039 off the table edge to clear the 0.034 m cut with table_dining f_L-1_038 (S2). | ![](agent/r1_098_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_100_move_piece_after_r_L-1_salon_2.png) |
| 23695 | 1 | move_piece | f_L-1b_045 | adjusted_by_ai | 0.0 -> 5.0 | Sofa f_L-1b_045 stands 0.59 m off the wall; snapping its back onto wall w_L-1b_004 (free span s3) puts it on the wall with its long side facing into the room. | ![](agent/r1_105_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_108_move_piece_after_r_L-1b_salon_2.png) |
| 23698 | 1 | move_piece | f_L1_019 | adjusted_by_ai | 21.0 -> 31.0 | Move sofa f_L1_019 slightly away from f_L1_018 to clear the blocked zone in front of it, fixing F6 clearance. | ![](agent/r1_109_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_112_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 23699 | 1 | move_piece | f_L-1_031 | adjusted_by_ai | 30.0 -> 30.0 | Move chair f_L-1_031 slightly outward (south) to resolve the 0.040 m cut with the dining table. | ![](agent/r1_110_move_piece_before_r_L-1_salon.png) | ![](agent/r1_113_move_piece_after_r_L-1_salon.png) |
| 23705 | 1 | retype_piece | f_L1_035 | adjusted_by_ai | 41.0 -> 44.0 | The 1.40 x 0.45 m bench against the south wall fits a console table, a valid living-room piece, resolving the wrong_type findings. | ![](agent/r1_115_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_117_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 23736 | 1 | resize_piece | f_L1_054 | added_by_ai | 100.0 -> 100.0 | Grow the AI-added piece to a real console-table size so it can be retyped to console_table for the upper-floor hall (a:F486, M28). | ![](agent/r1_153_resize_piece_before_r_L1_koridor.png) | ![](agent/r1_156_resize_piece_after_r_L1_koridor.png) |
| 23751 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift nightstand 0.12 m away from the bed side to clear the 0.06 m² overlap and satisfy the ≤ 0.30 m gap requirement. | ![](agent/r1_161_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_164_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 23756 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift nightstand f_L0_032 away from the bed edge to clear the 0.06 m² overlap (F9) and correct the -0.12 m gap to a valid ≤ 0.30 m distance (G4). | ![](agent/r1_165_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_170_move_piece_after_r_L0_e_yatak_odasi.png) |
| 23758 | 1 | report_library_gap | f_L-1_003 | library_gap | - | No audited kitchen_counter library model exists to swap f_L-1_003 to a correct working height (M2: top at 1.18 m over 0.97 m); the piece is a module build of the kitchen run. | - | - |
| 23761 | 1 | remove_piece | f_L1_067 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet stands where the sloped ceiling is only 0.82 m high (shows through the roof, X2) and its 0.80 m height is wrong for a tall_cabinet (S4); removing it clears both findings. | ![](agent/r1_174_remove_piece_before_r_L1_banyo_2.png) | ![](agent/r1_179_remove_piece_after_r_L1_banyo_2.png) |
| 23767 | 1 | set_lighting | r_L0_banyo | agent_override | - | Both camera views are over the EV cap; the finding names x1.94 on the room to cover headroom for both views. | - | - |
| 23771 | 1 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Reposition the entrance group per top solver candidate to open a free camera point blocked by the tall stair and shoe cabinet. | ![](agent/r1_192_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r1_195_relayout_room_after_r_L-1_koridor_2.png) |
| 23774 | 1 | remove_piece | f_L1_066 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet stands where the sloped ceiling is only 0.82 m high (X2) and its 0.80 m height is wrong for its type (S4); removing it resolves both. | ![](agent/r1_196_remove_piece_before_r_L1_banyo.png) | ![](agent/r1_197_remove_piece_after_r_L1_banyo.png) |
| 23777 | 1 | report_library_gap | f_L1_021 | library_gap | - | Toilet f_L1_021 built below library level (P7) and its swap_model was rejected (asset audited out); no usable library model exists for this toilet. | - | - |
| 23779 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | Both interior views are underexposed (incident p50 0.04-0.07 vs target 0.9); the worst view needs x2.92, so set the room light to x3 to cover both. | - | - |
| 23789 | 1 | report_library_gap | f_L-1b_038 | library_gap | - | No audited real toilet model with a width narrow enough (≤ ~0.45 m) to give the drawn 0.5 m-wide toilet the 0.38 m side clearance G10 needs; only generated models exist and pins to them are refused. | - | - |
| 23813 | 1 | set_camera | r_L1_banyo | agent_override | - | The frame is a black/empty failed render; re-pose the camera to show the bathroom's main group (bathtub, washbasin) at eye height. | - | - |
| 23814 | 1 | report_library_gap | f_L0_004 | library_gap | - | No audited library model of washbasin fits the drawn 1.0x0.55 m footprint with a floor-sitting base; the current model floats 0.384 m above the floor (S1). | - | - |
| 23818 | 1 | report_library_gap | f_L0_016 | library_gap | - | No audited library model of toilet fits the drawn 0.5x0.68 m footprint with a floor-sitting base; the current model floats 0.200 m above the floor (S1). | - | - |
| 23823 | 1 | report_library_gap | f_L0_017 | library_gap | - | No audited toilet model passes the fit rules for the drawn 0.50 x 0.69 m footprint (generated models refused on caps/height; the one real candidate was audit-removed), so the S1 floating lowest point and G10 left clearance stay. | - | - |
| 24360 | 2 | set_camera | r_L-1_banyo | agent_override | - | Argus: The bathtub is shown in isolation with no surrounding design elements; re-posing the bathroom camera to frame the bathtub with the washbasin and toilet shows the designed bathroom set. (fixes a:F189) | - | - |
| 24363 | 2 | set_camera | r_L-1_koridor_2 | agent_override | - | Argus: The hall camera looks at a bare wall and a closed door; re-aim it to show the hall's doors so the room reads as a furnished, open hall. (fixes a:F196) | - | - |
| 24364 | 2 | set_camera | r_L1_koridor | agent_override | - | Argus: The L1 hall camera is dominated by a bare wall and a closed wardrobe; re-aim it to show the hall's doors so an open, lit room is seen beyond. (fixes a:F200) | - | - |
| 24366 | 2 | correct_geometry | o_L1_001 | corrected_by_ai | - | Argus: The opening o_L1_001 is not cut through its wall w_L1_003; the door ray hits the wall. correct_geometry with fix_opening_on_wall puts the opening back on its wall and cuts it through. (fixes a:F249) | - | - |
| 24368 | 2 | set_material | floor | agent_override | - | Argus: The finding is a material/finish shortfall (floor not herringbone); relayout was refused (no candidate fits), and the floor look is a material slot, not a layout. (fixes a:F308) | - | - |
| 24372 | 2 | relayout_room | r_L-1_salon_2 | adjusted_by_ai | 30.0 -> 37.0 | Argus: table_dining f_L-1_038 and chair f_L-1_039 cut by 0.039 m; the model swaps were refused (fit-rule failure, audit-removed), so the collision is a layout placement issue to be fixed by relayout. (fixes a:F319) | ![](agent/r2_006_relayout_room_before_r_L-1_salon_2.png) | ![](agent/r2_007_relayout_room_after_r_L-1_salon_2.png) |
| 24373 | 2 | set_material | walls | agent_override | - | Argus: The wall behind the bed is a flat, untextured green paint; the reference style requires a feature wall with vertical fluted or slatted wood panelling to anchor the bed. (fixes a:F340) | - | - |
| 24374 | 2 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Argus: A black mesh office chair and a plain desk read as a home-office, not a bedroom; they clash with the bed and the project's calm, styled style. (fixes a:F344) | ![](agent/r2_008_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_009_swap_model_after_r_L0_yatak_odasi_3.png) |
| 24376 | 2 | swap_model | f_L1_005 | adjusted_by_ai | 44.0 -> 44.0 | Argus: The dining table and chairs are a different, lighter style from the heavy white bench seating, so the room's furniture does not read as one coherent set. (fixes a:F347) | ![](agent/r2_011_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_012_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 24377 | 2 | swap_model | f_L-1_070 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The brown leather armchair clashes with the white boxy sofa and the black lounge chair; the three seating pieces are of different styles and colors. (fixes a:F358) | ![](agent/r2_013_swap_model_before_r_L-1_salon.png) | ![](agent/r2_014_swap_model_after_r_L-1_salon.png) |
| 24378 | 2 | set_camera | r_L0_banyo | agent_override | - | Argus: The camera is pressed against a corner, framing a blank wall and a toilet roll instead of the room. (fixes a:F361) | - | - |
| 24379 | 2 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The render is a close-up that fails to show the room's layout or main fixtures, making it useless for a client presentation. (fixes a:F363) | - | - |
| 24380 | 2 | set_camera | r_L0_koridor | agent_override | - | Argus: The render is a tight, low-angle shot of a corner and a door, not a view of the hall; the space is empty and flat. (fixes a:F364) | - | - |
| 24381 | 2 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The black leather office chair is a corporate piece that clashes with the warm, residential bedroom style. (fixes a:F365) | ![](agent/r2_015_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_016_swap_model_after_r_L0_yatak_odasi.png) |
| 24382 | 2 | swap_model | f_L0_030 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The white Shaker-style desk with its raised panel drawers is a dated, traditional piece that does not go with the modern, minimalist wood bed and the project's style. (fixes a:F366) | ![](agent/r2_017_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_018_swap_model_after_r_L0_yatak_odasi.png) |
| 24385 | 2 | set_material | paving | agent_override | - | Argus: The terrace floor reads as a bare grey slab. Setting the paving slot to a stone-paving look gives the outdoor floor a designed finish. (fixes a:F371) | - | - |
| 24393 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 adds a second planter and a full 2-piece terrace pair, resolving the missing seating group and planter findings (F19, F20, N146, F378, F530, F181, F190). | ![](agent/r2_061_relayout_room_before_r_L1_teras.png) | ![](agent/r2_064_relayout_room_after_r_L1_teras.png) |
| 24407 | 2 | move_piece | f_L0_010 | adjusted_by_ai | 70.0 -> 80.0 | Shift the wardrobe along its wall to increase the clearance in front from 0.66 m to at least 0.80 m. | ![](agent/r2_072_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r2_079_move_piece_after_r_L0_yatak_odasi.png) |
| 24419 | 2 | swap_model | f_L1_017 | adjusted_by_ai | 44.0 -> 44.0 | Sofa f_L1_017 is a crude blocky white storage-bench model; swap to a proper modern 3-seat sofa to fix wrong_model. | ![](agent/r2_095_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_103_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 24431 | 2 | swap_model | f_L1_020 | adjusted_by_ai | 44.0 -> 44.0 | Sofa f_L1_020 is an identical clashing model to f_L1_017; swap to a different modern sofa to fix wrong_model. | ![](agent/r2_113_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_116_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 24436 | 2 | move_piece | f_L0_042 | added_by_ai | 80.0 -> 80.0 | Move the nightstand away from the window opening to clear the blocked opening finding. | ![](agent/r2_117_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r2_122_move_piece_after_r_L0_yatak_odasi.png) |
| 24439 | 2 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 gives a more complete terrace set (6 pieces, 2 planters + 2-piece pair) for the 19.7 m² balcony, addressing the under-furnished findings a:F488 and a:N147. | ![](agent/r2_120_relayout_room_before_r_L1_teras_2.png) | ![](agent/r2_121_relayout_room_after_r_L1_teras_2.png) |
| 24443 | 2 | relayout_room | r_L1_koridor | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the entrance group with the top solver candidate so the upper-floor hall gets a console instead of a shoe cabinet, satisfying the M28 decor need. | ![](agent/r2_124_relayout_room_before_r_L1_koridor.png) | ![](agent/r2_129_relayout_room_after_r_L1_koridor.png) |
| 24457 | 2 | report_library_gap | f_L-1b_042 | library_gap | - | Record the library gap for the parametric sofa f_L-1b_042 so it is tracked and not re-attempted. | - | - |
| 24467 | 2 | move_piece | f_L1_031 | adjusted_by_ai | 44.0 -> 54.0 | Move armchair f_L1_031 closer to coffee table f_L1_023 (2.73m > 2.50m) to fix the group layout distance. | ![](agent/r2_155_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_161_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 24472 | 2 | set_camera | r_L1_banyo | agent_override | - | Reposition camera to a central point with headroom to capture bathtub, toilet and washbasin, fixing the bad_camera and invisible-room findings. | - | - |
| 24476 | 2 | report_library_gap | f_L1_015 | library_gap | - | Washbasin f_L1_015 floats +0.384 m above its floor (S1); as drawn fixed equipment it cannot be moved or resized, and no audited library model fits the 5 m2 bathroom bay. | - | - |
| 24477 | 2 | report_library_gap | f_L1_021 | library_gap | - | Toilet f_L1_021 floats +0.200 m above its floor (S1), is built below library level (Q12) and has a 0.33 m side clearance (G10); as drawn fixed equipment it cannot be moved or resized, and no audited library model fits the 5 m2 bathroom bay. | - | - |
| 24485 | 2 | report_library_gap | f_L-1_012 | library_gap | - | No audited library model of kitchen_counter exists (catalog count 0), so the 1.18 m top of f_L-1_012 cannot be corrected by swap_model; the piece is a module build of the drawn kitchen run. | - | - |
| 24487 | 2 | move_piece | f_L-1_105 | added_by_ai | 100.0 -> 100.0 | a:F227: move the shoe cabinet off the camera's only free point in the hall, onto the long free span s4 | ![](agent/r2_185_move_piece_before_r_L-1_koridor_2.png) | ![](agent/r2_187_move_piece_after_r_L-1_koridor_2.png) |
| 24490 | 2 | set_lighting | r_L-1_banyo | agent_override | - | Both cameras are underexposed by ~0.2 EV; the finding names factor x1.63 to clear lighting_dark for both views. | - | - |
| 24532 | 2 | report_library_gap | f_L1_022 | library_gap | - | No audited library toilet model fits: all generated models fail the height/fit caps or are audit-removed, so the parametric mesh stays (a:F144, a:F259, c:S1:f_L1_022). | - | - |
| 24534 | 2 | report_library_gap | f_L1_016 | library_gap | - | No audited library washbasin model fits: all generated models fail the height/fit caps, so the floating model stays (c:S1:f_L1_016). | - | - |
| 25084 | 3 | set_material | plinth | agent_override | - | Argus: The stone cladding on the lower wall is a flat, repetitive texture. Setting the plinth slot to an ashlar stone look gives it the depth and variation the reference shows. (fixes a:F382) | - | - |
| 25085 | 3 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The judge says the bed is cut out of frame and the walls are bare concrete. Re-aiming the camera to show the bed, wardrobe and desk whole (the code picks a free pose) fixes the framing; the bare-wall styling is the agent's restyle. (fixes a:F388) | - | - |
| 25087 | 3 | place_group | r_L1_teras_2 | added_by_ai | 100.0 -> 100.0 | Argus: A 19.7 m2 balcony with only an armchair, plant and side_table is not furnished as a usable outdoor space; the terrace_lounge group completes it. (fixes a:F488) | ![](agent/r3_001_place_group_before_r_L1_teras_2.png) | ![](agent/r3_002_place_group_after_r_L1_teras_2.png) |
| 25088 | 3 | set_camera | r_L1_oyun_aktivite_ve_dinlenme_odasi | agent_override | - | Argus: The armchair is cut off by the camera frame; moving the camera to show the complete chair and the view fixes the composition without changing the piece. (fixes a:F490) | - | - |
| 25089 | 3 | set_material | ground | agent_override | - | Argus: The background is a flat untextured green plane; the ground slot has no real landscape look assigned, so the render stage shows a placeholder. (fixes a:F529) | - | - |
| 25106 | 3 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidates 1 and 2 were already tried; candidate 3 re-solves the balcony and terrace_pair groups to furnish the 19.7 m² terrace with a seating group and planters, addressing the missing-member and sparse-furnishing findings. | ![](agent/r3_054_relayout_room_before_r_L1_teras.png) | ![](agent/r3_060_relayout_room_after_r_L1_teras.png) |
| 25141 | 3 | move_piece | f_L-1_042 | adjusted_by_ai | 37.0 -> 37.0 | Nudge chair f_L-1_042 away from the table edge to clear the 0.034 m cut (S2). | ![](agent/r3_089_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_091_move_piece_after_r_L-1_salon_2.png) |
| 25144 | 3 | rotate_piece | f_L-1b_041 | adjusted_by_ai | 5.0 -> 5.0 | a:F212/a:F491/a:F242/a:F585: set the sofa's missing front to 270° towards its partner across the open floor | ![](agent/r3_092_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_096_rotate_piece_after_r_L-1b_salon_2.png) |
| 25182 | 3 | set_camera | r_L1_koridor | agent_override | - | Reframe from the north-west corner down the corridor so the open interior door d_L1_003 is seen open against its swing side and the lit stair hall beyond, instead of the bare wall and closed wardrobe. | - | - |
| 25183 | 3 | move_piece | f_L0_045 | added_by_ai | 70.0 -> 70.0 | Shift nightstand f_L0_045 along the wall to clear window win_L0_004 (G12) while keeping it beside the bed. | ![](agent/r3_114_move_piece_before_r_L0_yatak_odasi_2.png) | ![](agent/r3_117_move_piece_after_r_L0_yatak_odasi_2.png) |
| 25206 | 3 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | a:F227: tall proxies (stair, shoe_cabinet) block every free camera point; candidate 2 repositions the entrance group to open circulation and create a valid camera point | ![](agent/r3_129_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r3_130_relayout_room_after_r_L-1_koridor_2.png) |
| 25214 | 3 | set_lighting | r_L0_banyo | agent_override | - | View cam_r_L0_banyo_1 is 0.21 stops over the EV cap; the finding names a room factor of x3 (currently x1.94) to bring incident light to target. | - | - |
| 25217 | 3 | report_library_gap | f_L-1_025 | library_gap | - | Washbasin model floats 0.384 m above its floor (S1); all candidate swap assets were audit-removed, so no audited library model fixes the geometry. | - | - |
| 25219 | 3 | report_library_gap | f_L-1_052 | library_gap | - | Toilet model floats 0.200 m above its floor (S1) and fails the 0.38 m left clearance (G10); swap attempts were rejected (audit-removed or fit-rule failures) and the piece hit max tries, so no audited library model fixes it. | - | - |
| 25228 | 3 | report_library_gap | f_L-1_026 | library_gap | - | Washbasin model floats 0.384 m above the floor (S1); all swap_model attempts were rejected (fit rules or audit-removed assets), so no valid floor-standing washbasin model exists in the current library. | - | - |
| 25229 | 3 | set_camera | r_L1_banyo | agent_override | - | The frame was a black/empty wall; re-aim to show the bathroom's main fixtures (washbasin, toilet) as the room's anchor. | - | - |
| 25230 | 3 | report_library_gap | f_L-1_051 | library_gap | - | Toilet model floats 0.200 m above the floor (S1); all swap_model attempts were rejected (fit rules or audit-removed assets), so no valid floor-standing toilet model exists in the current library. | - | - |
| 26083 | 4 | swap_model | f_L1_100 | added_by_ai | 100.0 -> 100.0 | Argus: The terrace armchair's current model (3dwh_7c41f538b2d0873e672fe42f) is the same broken model that F30/F31 report as detached; swapping to a minimal/modern armchair of the same footprint fixes the missing-group look and the detached parts a (fixes a:F19) | ![](agent/r4_001_swap_model_before_r_L1_teras.png) | ![](agent/r4_002_swap_model_after_r_L1_teras.png) |
| 26084 | 4 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace has only one armchair, a plant and a side table; the drawn terrace group (armchairs + side table) is incomplete. place_group re-solves the drawn group around its drawn anchor instead of adding a second set, completing the missin (fixes a:F20) | ![](agent/r4_003_place_group_before_r_L1_teras.png) | ![](agent/r4_004_place_group_after_r_L1_teras.png) |
| 26094 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 54.0 -> 61.0 | Argus: The armchair f_L1_052 is placed behind the back of the sofa f_L1_017, looking at it, and rotating it in place was refused (it would face a wall or break the group). The seating group in this 40.5 m2 room is mis-arranged; re-solving the room (fixes a:F75) | ![](agent/r4_014_relayout_room_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r4_015_relayout_room_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 26099 | 4 | set_material | plot_wall | agent_override | - | Argus: The retaining wall is a bare concrete slab that clashes with the stone facade. Setting the plot_wall slot to a stone look ties it to the facade. (fixes a:F178) | - | - |
| 26105 | 4 | set_material | ground | agent_override | - | Argus: The outdoor setting is flat and empty with a single untextured green plane. Setting the ground slot to a textured grass look gives the scene depth. (fixes a:F187) | - | - |
| 26107 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: cam_r_L0_banyo_1 shows the bathtub barely in a corner against an unbroken tiled wall; the camera is re-posed to show the tub with its bathroom set. (fixes a:F196) | - | - |
| 26108 | 4 | set_camera | r_L-1_banyo | agent_override | - | Argus: cam_r_L-1_banyo_2 shows the bathtub in isolation with no surrounding design elements; the camera is re-posed to show the tub with its bathroom set. (fixes a:F197) | - | - |
| 26109 | 4 | set_camera | r_L1_teras | agent_override | - | Argus: cam_r_L1_teras_1 cuts off the foreground armchair; the camera is re-posed to show the complete chair and the terrace pieces. (fixes a:F200) | - | - |
| 26110 | 4 | set_camera | r_L-1_koridor_2 | agent_override | - | Argus: cam_r_L-1_koridor_2_1 looks straight at a large bare wall with a closed door; the camera is re-posed to show the hall with its doors. (fixes a:F202) | - | - |
| 26111 | 4 | set_camera | r_L1_koridor | agent_override | - | Argus: cam_r_L1_koridor_1 is dominated by a bare wall and a closed wardrobe; the camera is re-posed to show the hall with its doors. (fixes a:F206) | - | - |
| 26128 | 4 | set_camera | r_L1_banyo | agent_override | - | The current camera is pressed against a wall showing only a switch and vase (failed render); re-aim it to frame the bathroom's main group (basin, toilet, bathtub) as a valid view of the room. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 23634 | 1 | set_camera | r_L0_e_yatak_odasi | show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_3 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views; cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one | Argus: The door exists in the model; the single view that must show it does not frame it. Reposing the camera to include the door is the direct fix. (fixes a:F113) |
| 23635 | 1 | fix_fixture | f_L-1_056 | fixture_size: f_L-1_056: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The bathtub is 1.83 m in a 5.0 m2 bathroom, leaving only 0.28 m in front (needs 0.53 m). Retype was refused (drawn lock), so the size is the misread: a real 1.70 m tub fits the bay and restores the clearance. (fixes a:F129) |
| 23636 | 1 | swap_model | f_L-1_052 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The parametric toilet (0.50 m) sits 0.33 m from the left wall/fixture (needs 0.38 m). The 0.48 m objaverse model narrows the footprint enough to clear the side. (fixes a:F130) |
| 23637 | 1 | fix_fixture | f_L-1_055 | fixture_size: f_L-1_055: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 1.83 m tub in the twin bathroom r_L-1_banyo_2 with 0.28 m front clearance; resizing to 1.70 m restores the 0.53 m minimum. (fixes a:F131) |
| 23638 | 1 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: Shower 1.40 m in a 4.0 m2 bathroom leaves 0.05 m in front (needs 0.53 m). A 1.20 m shower fits the bay and restores the clearance. (fixes a:F136) |
| 23639 | 1 | fix_fixture | f_L0_014 | fixture_size: f_L0_014: the drawn 0.60 x 1.40 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: Shower 1.40 m leaves 0.10 m in front (needs 0.53 m); rotate was refused (front faces a wall). Resizing to 1.20 m restores the clearance. (fixes a:F137) |
| 23640 | 1 | swap_model | f_L0_018 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: Toilet 0.33 m from the right wall/fixture (needs 0.38 m). Prior swaps were refused (audit removed / fit rules / max tries); the 0.48 m objaverse model is a different, narrower asset that restores the side clearance. (fixes a:F138) |
| 23641 | 1 | fix_fixture | f_L0_025 | fixture_size: f_L0_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: 1.83 m tub in r_L0_banyo with 0.28 m front clearance; resize to 1.70 m. (fixes a:F139) |
| 23642 | 1 | swap_model | f_L0_017 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: Toilet 0.33 m from the left wall/fixture (needs 0.38 m); the 0.48 m model restores the side clearance. (fixes a:F140) |
| 23643 | 1 | fix_fixture | f_L0_026 | fixture_size: f_L0_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: 1.83 m tub in r_L0_banyo_2 with 0.28 m front clearance; resize to 1.70 m. (fixes a:F141) |
| 23644 | 1 | swap_model | f_L1_021 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: Toilet 0.33 m from the right wall/fixture (needs 0.38 m). Prior swaps were refused on height under the sloped ceiling; the 0.78 m objaverse model is a different asset that also narrows the footprint to restore the side clearance. (fixes a:F142) |
| 23645 | 1 | fix_fixture | f_L1_025 | fixture_size: f_L1_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: 1.83 m tub in r_L1_banyo with 0.28 m front clearance; resize to 1.70 m. (fixes a:F143) |
| 23646 | 1 | swap_model | f_L1_022 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: Toilet 0.33 m from the left wall/fixture (needs 0.38 m). Prior swaps were refused on height under the sloped ceiling; the 0.78 m objaverse model is a different asset that also narrows the footprint to restore the side clearance. (fixes a:F144) |
| 23647 | 1 | fix_fixture | f_L1_026 | fixture_size: f_L1_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The bathtub is 1.83 m long in a 5.0 m2 bathroom, leaving only 0.28 m in front (needs 0.53 m). Resizing to a real 1.80 m product and letting the code re-seat it is the fix of the cause (the misread size), not moving its neighbours. (fixes a:F145) |
| 23648 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: The kitchen run (anchor f_L-1_001, members f_L-1_002..f_L-1_004) has no fridge. place_group was refused as no_change because it saw the run as complete, but the run is missing its fridge member; re-running the group completes it. (fixes a:F147) |
| 23649 | 1 | place_group | r_L-1_mutfak_2 | no_change: r_L-1_mutfak_2 already has its kitchen_run r_L-1_mutfak_2.kitchen_run (anchor f_L-1_010, members f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068, f_L-1_096): nothing missing, never a second set | Argus: Twin of F147: the kitchen run (anchor f_L-1_010, members f_L-1_011..f_L-1_013) has no fridge. Re-running the group completes it. (fixes a:F148) |
| 23652 | 1 | set_camera | r_L0_e_banyo | show: none of the 3 best poses of r_L0_e_banyo that show f_L0_015 passes the camera checks: duplicate: cam_r_L0_e_banyo_1 would show the view cam_r_L0_e_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_banyo, or remove one of the two views | Argus: The toilet is not visible in the render. swap_model was refused (asset unusable), so the cause is the camera. Setting the camera to show the toilet fixes the render. (fixes a:F151) |
| 23653 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: swap: X3:r_L1_oyun_aktivite_ve_dinlenme_odasi_2 replaces AI1:r_L1_oyun_aktivite_ve_dinlenme_odasi_2 on r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (living): 5.6 m of outer wall with no window or door: a blank facade): the piece keeps as many critical / major findings, so nothing is removed | Argus: The room is typed 'other' but is identical in size and content to its twin r_L1_oyun_aktivite_ve_dinlenme_odasi which is correctly typed 'living'. The misread type prevents the room from being furnished as a living room. set_room_type was r (fixes a:F154) |
| 23654 | 1 | place_group | r_L1_banyo_2 | no_change: r_L1_banyo_2 already has its bathroom_set r_L1_banyo_2.bathroom_set (anchor f_L1_022, members f_L1_016, f_L1_026): nothing missing, never a second set | Argus: The bathroom set is missing a tall_cabinet. Re-running the group completes it. (fixes a:F156) |
| 23655 | 1 | correct_geometry | o_L1_001 | the opening already lies on the wall (0.000 m) | Argus: The opening o_L1_001 is not cut through its wall w_L1_003. correct_geometry with fix_opening_on_wall puts the opening back on its wall. (fixes a:F157) |
| 23656 | 1 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 1.90 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 20) is at z -0.40 m: use z 1.10 to 1.30 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: There is no frontal view of the entrance facade. Adding a camera is a direct fix. (fixes a:F167) |
| 23658 | 1 | place_group | r_L1_banyo | no_change: r_L1_banyo already has its bathroom_set r_L1_banyo.bathroom_set (anchor f_L1_021, members f_L1_015, f_L1_025): nothing missing, never a second set | Argus: The bathroom is missing a mirror and towel rail. The place_group tool can complete the bathroom set with the missing items. (fixes a:F171) |
| 23659 | 1 | place_group | r_L-1_banyo | no_change: r_L-1_banyo already has its bathroom_set r_L-1_banyo.bathroom_set (anchor f_L-1_051, members f_L-1_026, f_L-1_056): nothing missing, never a second set | Argus: The bathroom is missing a mirror and towel rail. The place_group tool can complete the bathroom set with the missing items. (fixes a:F173) |
| 23660 | 1 | place_group | r_L0_banyo | no_change: r_L0_banyo already has its bathroom_set r_L0_banyo.bathroom_set (anchor f_L0_018, members f_L0_003, f_L0_025): nothing missing, never a second set | Argus: The bathroom is missing a mirror and towel rail. The place_group tool can complete the bathroom set with the missing items. (fixes a:F175) |
| 23667 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Re-solve layout with candidate 1 to put the TV unit against a wall, the coffee table between sofa and TV, and align the armchairs with the coffee table. |
| 23670 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Re-solve layout with candidate 2 (seating group with 2 members) to place the TV unit against a wall, the coffee table in front of the sofa, and align the armchairs. |
| 23672 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Rotate armchair so its front faces the room center instead of the back of the sofa, resolving the F4 orientation conflict. |
| 23673 | 1 | rotate_piece | f_L-1_101 | f_L-1_101: inside_room, f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 30 -> 0 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F4 f_L-1_049: armchair stands behind the back of f_L-1_101, looking at it; F9 f_L-1_101: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; G1 f_L-1_101: TV unit f_L-1_101 90° off the line to the sofa, needs ≤ 10°) | Rotate TV unit so its front faces the seating area instead of the back of the armchair, resolving the F4 orientation conflict. |
| 23674 | 1 | retype_piece | f_L-1b_041 | retype: sofa is no candidate for f_L-1b_041 (0.90 x 2.13 m at [10.98, 4.48]): the size table and the room / zone give chaise, stair | Sofa drawn 0.90 wide x 2.13 deep is a 90°-rotated standard sofa; confirming sofa type refits it to real product size and sets its front into the room. |
| 23676 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | max_tries: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 was edited 3 times in this round | Re-solve layout with candidate 3 to place the TV unit against a wall, the coffee table in front of the sofa, and align the armchairs. |
| 23678 | 1 | resize_piece | f_L-1b_041 | score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.43 m (needs ≤ 2.50 m)) | Sofa was read 90° against its product sizes (0.90 wide x 2.13 deep); restoring the real 2.13 m front x 0.90 m depth fixes the F2 size finding. |
| 23679 | 1 | rotate_piece | f_L-1_070 | acceptance: finding F4:f_L-1_070 is still there after the edit (armchair stands behind the back of f_L-1_053, looking at it) | Rotate armchair to face south (toward the window wall) so it faces the coffee table and seating group instead of the sofa back. |
| 23680 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn armchair f_L-1_072 to face into the room (away from the back of sofa f_L-1_054), fixing F4 orientation. |
| 23683 | 1 | move_piece | f_L-1b_045 | wall_exists: no wall 'r_L-1b_salon_2.s3' | Sofa f_L-1b_045 stands 0.59 m off the wall; snapping its back onto the free span s3 puts it on the wall with its long side facing into the room. |
| 23684 | 1 | rotate_piece | f_L-1_101 | f_L-1_101: inside_room, f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 30 -> 10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F9 f_L-1_101: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; G1 f_L-1_101: TV unit f_L-1_101 90° off the line to the sofa, needs ≤ 10°) | Rotate TV unit to face north (toward the seating area) instead of the back of armchair f_L-1_071. |
| 23685 | 1 | rotate_piece | f_L-1_102 | score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of it) | Turn tv_unit f_L-1_102 to face the seating area (away from the back of armchair f_L-1_069), fixing F4 orientation. |
| 23686 | 1 | rotate_piece | f_L1_032 | f_L1_032: clearance_ok | Rotate armchair f_L1_032 to face the coffee table f_L1_024 (front 11.4°) instead of the back of the TV unit, fixing F4 orientation. |
| 23687 | 1 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Shift table_coffee f_L-1_074 away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 23690 | 1 | rotate_piece | f_L1_059 | acceptance: finding F4:f_L1_059 is still there after the edit (armchair stands behind the back of f_L1_018, looking at it) | Rotate reading corner armchair f_L1_059 to face into the room (180°) instead of the back of sofa f_L1_018, fixing F4 orientation. |
| 23692 | 1 | remove_piece | f_L0_045 | score: plausibility 70 -> 67 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free)) | AI-added nightstand stands in front of window win_L0_004 (G12); removing it clears the window obstruction, bed group keeps f_L0_044. |
| 23693 | 1 | retype_piece | f_L1_035 | retype: bench is no candidate for f_L1_035 (1.40 x 0.45 m at [6.10, 7.22]): the size table and the room / zone give bookshelf, console_table, display_cabinet, sideboard, table_coffee, tv_unit | Confirm the drawn bench type: benches are valid seating in a living room, resolving the wrong_type findings. |
| 23694 | 1 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Move coffee table slightly right to clear the 0.12 m² overlap with armchair f_L-1_071. |
| 23696 | 1 | move_piece | f_L-1_042 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Nudge chair f_L-1_042 off the table edge to clear the 0.034 m cut with table_dining f_L-1_038 (S2). |
| 23697 | 1 | rotate_piece | f_L1_052 | acceptance: finding F4:f_L1_052 is still there after the edit (armchair does not face its group (f_L1_017, f_L1_023)) | Turn the reading-corner armchair to face the room (away from the back of sofa f_L1_017) instead of looking at the sofa's back. |
| 23701 | 1 | move_piece | f_L-1b_084 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Potted plant f_L-1b_084 blocks the free zone in front of sofa f_L-1b_045; shifting it 0.7 m towards the wall clears the seating front. |
| 23704 | 1 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Severe clearance violations (wardrobe front 0.17m, bed sides 0.37m/0.52m) and missing nightstand; solver re-solves the drawn groups to restore clearances. |
| 23706 | 1 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.05 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Shift table_coffee f_L-1_074 further from armchair f_L-1_069 to fully clear the 0.12 m² overlap (F9). |
| 23709 | 1 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.10 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table slightly north to clear the 0.12 m² overlap with armchair f_L-1_071 while staying clear of f_L-1_070. |
| 23710 | 1 | move_piece | f_L1_063 | acceptance: swap: G1:f_L1_063 replaces F3:f_L1_063 on f_L1_063 (TV unit f_L1_063 1.49 m off the sofa axis, needs ≤ 0.30 m; 90° off the line to the sofa, needs ≤ 10°; 0.10 m from the so): the piece keeps as many critical / major findings, so nothing is removed | Snap TV unit f_L1_063 back onto wall w_L1_012 to fix F3 (back not on a wall, 1.01 m off). |
| 23711 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_024 has only 0.78 m behind it (needs 0.81 m); shifting it 0.16 m away from the table edge opens the required clearance. |
| 23712 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, f_L-1_072: inside_room, f_L-1_072: no_overlap, score: plausibility 30 -> 10 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F4 f_L-1_102: tv_unit stands behind the back of f_L-1_069, f_L-1_072, looking at it; F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 91° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn armchair f_L-1_072 to face the seating group (coffee table f_L-1_074 / sofa f_L-1_054) instead of the back of the sofa, fixing F4 orientation. |
| 23713 | 1 | rotate_piece | f_L1_052 | f_L1_052: clearance_ok, score: plausibility 44 -> 24 (F4 f_L1_052: armchair faces a wall 0.02 m in front of it; F4 f_L1_062: tv_unit stands behind the back of f_L1_052, looking at it; F6 f_L1_052: armchair: the free zone in front of it is reaches out of the room) | Turn the reading-corner armchair to face the seating group (sofa f_L1_017 / coffee table f_L1_023) instead of the sofa's back. |
| 23716 | 1 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Move coffee table further right to clear the overlap with armchair f_L-1_071 without hitting f_L-1_070. |
| 23718 | 1 | move_piece | f_L-1_102 | score: plausibility 30 -> 20 (G1 f_L-1_102: TV unit f_L-1_102 1.22 m off the sofa axis, needs ≤ 0.30 m) | Snap tv_unit f_L-1_102 back onto the right wall (span s2) so its back is on the wall and it faces the seating, fixing F4. |
| 23719 | 1 | mark_not_furniture | f_L-1b_001 | no_crop: f_L-1b_001 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The untyped 5.14 x 2.37 m drawn outline is a cluster of pieces / dimension outline, not a single piece of furniture; marking it not furniture clears the NR review finding. |
| 23722 | 1 | move_piece | f_L1_020 | score: plausibility 44 -> -16 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_035: console_table f_L1_035: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Shift sofa f_L1_020 0.3 m away from sofa f_L1_017 to clear the blocked free zone in front of it and make room for its coffee table. |
| 23723 | 1 | move_piece | f_L1_063 | acceptance: swap: G1:f_L1_063 replaces F3:f_L1_063 on f_L1_063 (TV unit f_L1_063 stands behind the sofa's front; 1.49 m off the sofa axis, needs ≤ 0.30 m; 90° off the line to the sofa,): the piece keeps as many critical / major findings, so nothing is removed | Snap TV unit f_L1_063 to wall w_L1_012 at offset 3.5m to align with sofa f_L1_019 axis, fixing F3 off-wall. |
| 23724 | 1 | move_piece | f_L1_031 | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 8° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.70 m (needs ≤ 2.50 m)) | Move armchair f_L1_031 0.72 m closer to the coffee table f_L1_023 to satisfy the seating group distance (needs ≤ 2.50 m). |
| 23726 | 1 | move_piece | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | shift bed 0.04 m toward room centre to raise the right-side clearance to 0.60 m (G5) |
| 23727 | 1 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Retype the untyped 5.54 x 0.60 m drawn piece as a sideboard, which fits its long narrow dimensions and the living room context. |
| 23728 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_024 has only 0.78 m behind it (needs 0.81 m); shifting it 0.3 m away from the table edge opens the required clearance. |
| 23729 | 1 | retype_piece | f_L1_054 | retype: console_table is no candidate for f_L1_054 (0.60 x 0.25 m at [4.07, 7.74]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet | Upper-floor hall: shoe_cabinet is wrong type; retype to console_table to match the L-1b hall and the room's decor need. |
| 23730 | 1 | move_piece | f_L1_031 | drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.70 m) | Move armchair f_L1_031 0.7 m towards the coffee table f_L1_023 to bring it within the 2.50 m seating-group distance. |
| 23731 | 1 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Move coffee table slightly south to clear the 0.12 m² overlap with armchair f_L-1_071. |
| 23733 | 1 | move_piece | f_L-1b_084 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Potted plant f_L-1b_084 blocks the free zone in front of sofa f_L-1b_045 (F6); shifting it 0.7 m towards the wall clears the seating front. |
| 23734 | 1 | move_piece | f_L1_007 | acceptance: finding G6:f_L1_007 is still there after the edit (chair f_L1_007: 0.65 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Shift dining chair f_L1_007 0.3 m away from the wall behind it to reach the 0.81 m clearance behind the chair. |
| 23735 | 1 | move_piece | f_L1_063 | snap: f_L1_063: no free place on wall w_L1_012 (doors, windows) | Snap TV unit f_L1_063 to wall w_L1_012 at offset 1.23m to align with sofa f_L1_019 at y=6.21, fixing F3 off-wall while keeping G1 alignment. |
| 23737 | 1 | move_piece | f_L-1b_084 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Potted plant f_L-1b_084 blocks the free zone in front of sofa f_L-1b_045 (F6); shifting it 0.62 m towards the wall clears the seating front. |
| 23738 | 1 | move_piece | f_L-1_101 | score: plausibility 30 -> 20 (G1 f_L-1_101: TV unit f_L-1_101 1.52 m off the sofa axis, needs ≤ 0.30 m) | Move TV unit to the left wall (w_L-1_007) so its back is on a wall and it faces the seating area, resolving the F4 orientation conflict. |
| 23741 | 1 | move_piece | f_L1_007 | score: plausibility 44 -> 34 (F4 f_L1_007: chair does not face its group (f_L1_005); G6 f_L1_007: chair f_L1_007 is 73° off the table f_L1_005 (needs ≤ 45°)) | Shift dining chair f_L1_007 0.3 m away from the wall behind it to reach the 0.81 m pull-out clearance. |
| 23742 | 1 | retype_piece | f_L1_054 | memory: the same edit was rejected in round 1: retype: console_table is no candidate for f_L1_054 (0.60 x 0.25 m at [4.07, 7.74]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet | Now at a real console size (1.2 x 0.35 m), retype the AI-added piece to console_table for the upper-floor hall, matching the L-1b hall and the M28 decor need. |
| 23743 | 1 | move_piece | f_L-1b_017 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Dining table f_L-1b_017: shifting it 0.15 m away from the window wall gives chair f_L-1b_024 the 0.81 m pull-out clearance it lacks (G6). |
| 23744 | 1 | rotate_piece | f_L1_006 | score: plausibility 44 -> 24 (F4 f_L1_006: chair does not face its group (f_L1_005); G6 f_L1_006: chair f_L1_006 is 101° off the table f_L1_005 (needs ≤ 45°)) | Turn dining chair f_L1_006 back to its drawn orientation (facing the table, 270°) to resolve the K3 orientation findings. |
| 23746 | 1 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve drawn groups to restore wardrobe front clearance, bed side clearances and add the missing right nightstand. |
| 23747 | 1 | move_piece | f_L1_063 | max_tries: f_L1_063 was edited 3 times in this round | Snap TV unit f_L1_063 to wall w_L1_002 (south wall) to fix F3 off-wall, positioning it near the sofa f_L1_019. |
| 23750 | 1 | resize_piece | f_L1_054 | max_tries: f_L1_054 was edited 3 times in this round | Match the piece to a real console-table product size (1.4 x 0.45 m) so it can be retyped to console_table for the upper-floor hall. |
| 23754 | 1 | rotate_piece | f_L1_029 | f_L1_029: clearance_ok, score: plausibility 31 -> 11 (F4 f_L1_029: armchair does not face its group (f_L1_063, f_L1_018, f_L1_024); F6 f_L1_029: armchair: the free zone in front of it is blocked by f_L1_032; G3 f_L1_029: armchair f_L1_029 is 83° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.69 m (needs ≤ 2.50 m)) | Rotate armchair f_L1_029 to face 180° (away from the TV unit back) to fix F4 orientation. |
| 23759 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the sleeping group around the drawn bed anchor to build the missing nightstand on the free right side of the head. |
| 23762 | 1 | place_group | r_L0_e_yatak_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the sleeping_double group around the drawn bed anchor to place a nightstand on the free left side of the head, resolving the missing member finding. |
| 23763 | 1 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008): re-solve the sleeping group around the drawn bed anchor to build the missing nightstand on the free right side of the head. |
| 23764 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008): re-solve the sleeping group around the drawn bed anchor to build the missing nightstand on the free right side of the head. |
| 23766 | 1 | place_group | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_007 (G4 minor: no nightstand on the free left side of the head): re-solve the sleeping_double group around the drawn bed anchor to place a nightstand on the free left side. |
| 23770 | 1 | place_group | r_L0_e_yatak_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_007 (G4 minor: no nightstand on the free left side of the head): re-solve the sleeping_double group around the drawn bed anchor with a bench option to place a nightstand on the free left side. |
| 23772 | 1 | fix_fixture | f_L0_003 | fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_007) | Door d_L0_007 swings into the washbasin on one hinge side; nudge the basin to clear the swing. |
| 23775 | 1 | place_group | r_L0_e_yatak_odasi_2 | max_tries: r_L0_e_yatak_odasi_2 was edited 3 times in this round | Fixes c:G4:f_L0_008 (G4 minor, bed f_L0_008): re-solve the sleeping group around the drawn bed anchor to build the missing nightstand on the free right side of the head. |
| 23778 | 1 | swap_model | f_L0_017 | pin_refused: f_L0_017: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Smaller, floor-seated toilet model to fix the S1 floating lowest point and the G10 left-side clearance (0.33 m vs 0.38 m needed). |
| 23782 | 1 | swap_model | f_L0_017 | asset_type: abo_B07H8PQFR2 is a tall_cabinet model, not a toilet | Try a real product model for the toilet to fix the S1 floating lowest point and the G10 left-side clearance. |
| 23785 | 1 | swap_model | f_L0_017 | max_tries: f_L0_017 was edited 3 times in this round | Try another toilet model to fix the S1 floating lowest point and the G10 left-side clearance. |
| 23786 | 1 | swap_model | f_L-1b_038 | pin_refused: f_L-1b_038: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Narrower toilet (0.415 m wide vs 0.5 m) to gain the 0.05 m side clearance the G10 check needs (0.33 m -> ~0.38 m). |
| 23787 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall); with the front at 180 deg its back is not on a wall | Shower front faces a wall 0.10 m ahead; turning it to face the room interior clears F4. |
| 23788 | 1 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Use a real library tall_cabinet model (0.40 x 0.57 x 1.85 m) instead of the parametric mesh to clear the below_library finding. |
| 23798 | 1 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Use a real library tall_cabinet model (0.52 x 0.25 x 1.63 m) that fits the 0.40 x 0.35 m footprint instead of the parametric mesh. |
| 23803 | 1 | swap_model | f_L0_004 | pin_refused: f_L0_004: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Washbasin model floats 0.384 m above floor; swap to a model whose footprint matches the drawn 1.0x0.55 and sits on the floor. |
| 23809 | 1 | swap_model | f_L0_016 | pin_refused: f_L0_016: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Toilet model floats 0.200 m above floor; swap to a model whose footprint matches the drawn 0.5x0.68 and sits on the floor. |
| 23810 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Use a floor-seated washbasin model to fix the S1 finding (lowest point +0.384 m above its floor). |
| 23812 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Try another washbasin model to fix the S1 finding (lowest point +0.384 m above its floor). |
| 24359 | 2 | set_camera | r_L-1_banyo | show: none of the 8 best poses of r_L-1_banyo that show f_L-1_056, f_L-1_026, f_L-1_051 passes the camera checks: duplicate: cam_r_L-1_banyo_1 would show the view cam_r_L-1_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_banyo, or remove one of the two views; cam_r_L-1_banyo_1: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one | Argus: The bathtub is shown in isolation with a bare surrounding; re-posing the bathroom camera to frame the bathtub together with the washbasin and toilet shows the designed bathroom set instead of a bare object. (fixes a:F187) |
| 24361 | 2 | rotate_piece | f_L1_006 | memory: the same edit was rejected in round 1: score: plausibility 44 -> 24 (F4 f_L1_006: chair does not face its group (f_L1_005); G6 f_L1_006: chair f_L1_006 is 101° off the table f_L1_005 (needs ≤ 45°)) | Argus: The chair is turned 90 deg from its drawn place; rotating it back to its drawn orientation (front 270 deg) restores the drawn position. (fixes a:F191) |
| 24362 | 2 | set_camera | r_L1_teras | show: no free camera point of r_L1_teras shows f_L1_041, f_L1_043, f_L1_042, f_L1_039, f_L1_040 (f_L1_041, f_L1_043, f_L1_042, f_L1_039, f_L1_040 not in r_L1_teras: name its pieces, doors or windows) | Argus: The foreground armchair is cut off by the camera; re-posing the terrace camera to frame the complete armchair with the side table and plants shows the finished, styled terrace. (fixes a:F192) |
| 24365 | 2 | relayout_room | r_L-1_koridor_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: The tall proxies block every camera pose; re-solving the room's layout frees a standing point. (fixes a:F227) |
| 24367 | 2 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: hssd_97162e912362bae3a0ca0d385f9dab8e43360108: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall_cabinet in r_L0_banyo_2 was built with the parametric mesh instead of a library model; the library has several tall_cabinet models of matching footprint (0.40 x 0.35 m drawn; hssd_97162e912362bae3a0ca0d385f9dab8e43360108 is 0.55 x  (fixes a:F257) |
| 24369 | 2 | place_group | r_L1_koridor | no_change: r_L1_koridor already has its entrance r_L1_koridor.entrance (anchor None, members f_L1_054): nothing missing, never a second set | Argus: r_L1_koridor (15.3 m2 hall) has shoe_cabinet, stair, wardrobe but no console/niche; the entrance group exists (anchor None) but is missing its console member, so the group must be completed. (fixes a:F313) |
| 24370 | 2 | swap_model | f_L1_017 | room_rule: f_L1_017: 3dwh_73a3f2fd339beec5aabd5ed6 names daybed: a bed-like daybed, not the sofa of a living room (the piece does not ask for one; a guest, child's or study room keeps it: UL161) | Argus: The current model abo_B075X4F5CS is a blocky white storage-bench; the only tried swap (gen_sofa_japandi_2) was refused as a generated model, so a real product of the type (3dwh_73a3f2fd339beec5aabd5ed6, 2.11x0.91, minimal/scandinavian) is t (fixes a:F315) |
| 24371 | 2 | swap_model | f_L-1_054 | asset_unusable: 3dwh_c7ebbb3791debf3dc433074c is not used: audit removed | Argus: The current model 3dwh_f87f9be475e69c941a20866f has parts 2.7 cm apart; the only tried swap (3dwh_e5f77d70d0615bd56772bf1f) was refused as audit-removed, so another real product of the type (3dwh_c7ebbb3791debf3dc433074c, 4.06x1.91, minimal (fixes a:F316) |
| 24375 | 2 | swap_model | f_L1_020 | pin_refused: f_L1_020: gen_sofa_japandi_2_98a7a89b: a generated model (units guessed) while a real product of the type fits within the caps (abo_B075X4F5CS): the real model stays; swap to a real model of the type or use another tool | Argus: This second sofa is an identical, clashing model to the first; having two of these boxy, white storage units makes the room look like a showroom for a single, un-styled product. (fixes a:F346) |
| 24383 | 2 | swap_model | f_L0_010 | lower_quality: f_L0_010: hssd_3033be75f2ac15885e8f4813dc55e168af09e91f is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The wardrobe is a raw, light wood that looks unfinished and clashes with the darker wood of the headboard and the grey walls. (fixes a:F367) |
| 24384 | 2 | set_exterior | exterior:ground,site | site front_court yes: a sunken front court with parapet walls is the documents' or the brief's decision, never an edit's (the paved light well and its strip along the glazing stay); leave front_court out or use auto | Argus: The terrace camera shows a flat, untextured lawn and no landscaping. Setting the site with a path, hedge, trees, and a front court, plus a grass ground, gives the environment the detail the judge found missing. (fixes a:F370) |
| 24386 | 2 | set_exterior | exterior:ground,site,sun | sun: azimuth 135 degrees (compass; 135 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Argus: The exterior render is flat and grey with generic landscaping. Setting the site, ground, and a warmer sun angle (SE, 45 deg elevation) gives the render the lighting and landscape detail the reference shows. (fixes a:F376) |
| 24387 | 2 | set_material | facade | facade: wood_cladding (wood) would clad every wall of the house; the modern facade scheme keeps the main walls rendered (render off white) over a stone_wall_ledgestone base with wood_cladding at the entrance (the base and the accent are no set_material slot: a texture problem of the base is the build's) | Argus: The exterior lacks material richness (wood cladding, varied textures). Setting the facade slot to wood cladding gives the house the styled finish the reference shows. (fixes a:F377) |
| 24388 | 2 | set_camera | ext_3 | eye height 2.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The camera is a close-up detail shot that cuts off the building. The previous attempt was refused because the eye height was 2.16 m (too high for an exterior view). Setting the eye height to 1.6 m (within the 1.5-1.7 m range for exterior vi (fixes a:F379) |
| 24390 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: swap: X3:r_L1_oyun_aktivite_ve_dinlenme_odasi_2 replaces AI1:r_L1_oyun_aktivite_ve_dinlenme_odasi_2 on r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (living): 5.6 m of outer wall with no window or door: a blank facade): the piece keeps as many critical /  | 40.5 m2 room with sofa, dining table, TV unit and bookshelf, identical to its twin typed 'living' (a:F154) |
| 24392 | 2 | move_piece | f_L1_063 | acceptance: finding F3:f_L1_063 is still there after the edit (tv_unit: its back is not on a wall (1.01 m off)) | Pull the tv_unit back to the wall so its back is on a wall (F3) while keeping it on the sofa axis (avoids the G1 swap that killed the wall-snap attempts) |
| 24395 | 2 | move_piece | f_L1_063 | acceptance: finding F3:f_L1_063 is still there after the edit (tv_unit: its back is not on a wall (1.01 m off)) | Restore the tv_unit to its original position: the 0.44 m pull-back did not clear the wall-distance check, so the move is a no-op that keeps the G1-free state |
| 24397 | 2 | move_piece | f_L0_010 | acceptance: finding G13:f_L0_010 is still there after the edit (wardrobe f_L0_010: 0.64 m free in front, needs ≥ 0.80 m) | Shift the wardrobe along its wall to increase the clearance in front from 0.66 m to at least 0.80 m. |
| 24399 | 2 | move_piece | f_L1_063 | memory: the same edit was rejected in round 2: acceptance: finding F3:f_L1_063 is still there after the edit (tv_unit: its back is not on a wall (1.01 m off)) | Restore the tv_unit to its original position: the 0.44 m pull-back did not clear the wall-distance check, so the move is a no-op that keeps the G1-free state |
| 24402 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair 90° clockwise so its front faces the room center instead of the back of the sofa, resolving the F4 orientation conflict. |
| 24403 | 2 | rotate_piece | f_L-1_101 | memory: the same edit was rejected in round 1: f_L-1_101: inside_room; f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before); score: plausibility 30 -> 0 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F4 f_L-1_049: armchair stands behind the back | Rotate TV unit 90° clockwise so its front faces the seating area instead of the back of the armchair, resolving the F4 orientation conflict. |
| 24404 | 2 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.07 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table to [6.0, 1.3] to clear the 0.12 m² overlap with armchair f_L-1_071 while maintaining distance from f_L-1_070. |
| 24406 | 2 | move_piece | f_L1_063 | memory: the same edit was rejected in round 2: acceptance: finding F3:f_L1_063 is still there after the edit (tv_unit: its back is not on a wall (1.01 m off)) | Restore the tv_unit to its original position: the 0.44 m pull-back did not clear the wall-distance check, so the move is a no-op that keeps the G1-free state |
| 24409 | 2 | retype_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: retype: sofa is no candidate for f_L-1b_041 (0.90 x 2.13 m at [10.98, 4.48]): the size table and the room / zone give chaise, stair | Fixes a:F212, a:F491, a:F242, a:F585, c:F2:f_L-1b_041, a:F61: the drawn 0.90x2.13 sofa is a 90-degree rotation of a standard 2.13x0.90 sofa; retype confirms the type and rebuilds it with the correct orientation and front. |
| 24410 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi is already a living | Room is furnished and named as a living/activity room; set to living to match documents and furniture. |
| 24411 | 2 | resize_piece | f_L-1b_042 | score: plausibility -15 -> -25 (F3 f_L-1b_042: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_051: armchair does not face its group (f_L-1b_042, f_L-1b_046); F4 f_L-1b_075: armchair does not face its group (f_L-1b_046, f_L-1b_042); G3 f_L-1b_051: armchair f_L-1b_051 is 65° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.57 m (needs ≤ 2.50 m)) | Sofa flagged as turned 90° against product sizes; swap to 2.13m wide x 0.90m deep to match its front-facing orientation. |
| 24412 | 2 | move_piece | f_L-1b_046 | acceptance: finding F3:f_L-1b_046 is still there after the edit (sofa: its back is not on a wall (0.59 m off)); 1 more kept | Move sofa 0.59m right so its back is on the wall and the free zone in front is no longer blocked by f_L-1b_071. |
| 24413 | 2 | move_piece | f_L0_019 | f_L0_019: no_overlap, f_L0_041: no_overlap, score: plausibility 80 -> 77 (G4 f_L0_019: bed_double f_L0_019: no nightstand on the free right side of the head (0.41 m free); G4 f_L0_041: nightstand f_L0_041 of bed_double f_L0_019: -0.12 m from the bed side (needs ≤ 0.30 m); G5 f_L0_019: bed_double f_L0_019: 0.41 m free along the right side, needs ≥ 0.60 m) | Center the bed against the wall to ensure at least 0.60 m of clearance on both the left and right sides. |
| 24415 | 2 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.05 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table further from both armchairs to clear the 0.12 m² overlap with f_L-1_071 while staying clear of f_L-1_070. |
| 24416 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_070: armchair faces a wall 0.11 m in front of it; F4 f_L-1_101: tv_unit stands behind the back of f_L-1_071, f_L-1_070, looking at it; F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 136° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair to face +x (toward the room center and the coffee table) instead of facing the back of the sofa, resolving the F4 orientation conflict. |
| 24417 | 2 | move_piece | f_L0_019 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 80 -> 67 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.06 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.38 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.14 m from the bed side (needs ≤ 0.30 m); G5 f_L0_019: bed_double f_L0_019: 0.38 m free along the left side, needs ≥ 0.60 m) | Center the bed against the wall to ensure at least 0.60 m of clearance on both the left and right sides. |
| 24418 | 2 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041)); 1 more kept | Fixes c:F4:f_L-1b_053, a:F4:f_L-1b_053, c:G3:f_L-1b_053, a:F246, a:F589: the armchair is 114° off the sofa; rotating it to face 180° (towards the sofa f_L-1b_041) resolves the orientation and group-alignment findings. |
| 24420 | 2 | move_piece | f_L0_042 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 80 -> 57 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.13 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.08 m from the bed side (needs ≤ 0.30 m)) | Move the nightstand away from the window opening to clear the blocked opening finding. |
| 24421 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 2 more kept | Use solver candidate 1 to re-layout the room, ensuring a 0.60 m walkway from the door reaches the front use zones of the seating group members (f_L-1_049, f_L-1_053, f_L-1_070). |
| 24422 | 2 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)); 1 more kept | Rotate armchair to face the sofa f_L-1b_042 (south) to clear F4 orientation and G3 group alignment findings. |
| 24423 | 2 | remove_piece | f_L0_045 | memory: the same edit was rejected in round 1: score: plausibility 70 -> 67 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free)) | Nightstand f_L0_045 (added_by_ai) blocks window win_L0_004 (G12); removing it clears the window obstruction, bed group keeps f_L0_044. |
| 24424 | 2 | move_piece | f_L0_012 | f_L0_012: inside_room (outline: wardrobe reaches 0.20 m² through the room outline, up to 0.136 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 50 (F3 f_L0_012: wardrobe: its back is not on a wall (0.14 m off); F9 f_L0_012: wardrobe reaches 0.20 m² through the room outline, up to 0.136 m deep; G13 f_L0_012: wardrobe f_L0_012: 0.79 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.14 m toward the wall to raise front clearance from 0.66 m to ≥0.80 m (G13). |
| 24426 | 2 | move_piece | f_L0_042 | f_L0_042: inside_room | Move the nightstand away from the window opening to clear the blocked opening finding. |
| 24427 | 2 | move_piece | f_L-1b_054 | acceptance: finding F6:f_L-1b_053 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_054); 1 more kept | Fixes c:F6:f_L-1b_053, c:F6:f_L-1b_054, a:F6:f_L-1b_054, c:G3:f_L-1b_054, a:F247, a:F590: the armchair blocks the free zone in front of f_L-1b_053 and is 33° off the sofa; shifting it 0.26 m away from f_L-1b_053 clears the path and improves alignment. |
| 24428 | 2 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Wardrobe front has only 0.17 m clearance (G13 needs 0.80 m); sliding it along the south wall toward the door end opens the front zone. |
| 24432 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge chair 0.03m to increase clearance from table edge to wall/piece behind to at least 0.81m. |
| 24433 | 2 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.71 m) | Move coffee table further from both armchairs to clear the 0.12 m² overlap with f_L-1_071 while staying clear of f_L-1_070. |
| 24437 | 2 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Slide the wardrobe to the far (door) end of the south wall so its front zone is clear of the door swing, giving the 0.80 m clearance G13 needs. |
| 24438 | 2 | move_piece | f_L-1b_054 | acceptance: finding F6:f_L-1b_053 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_054); 1 more kept | Fixes c:F6:f_L-1b_053, c:F6:f_L-1b_054, a:F6:f_L-1b_054, c:G3:f_L-1b_054, a:F247, a:F590: the armchair blocks the free zone in front of f_L-1b_053 and is 33° off the sofa; shifting it 0.36 m away from f_L-1b_053 clears the path and improves alignment. |
| 24440 | 2 | rotate_piece | f_L-1_070 | max_tries: f_L-1_070 was edited 3 times in this round | Rotate armchair 45° so its front faces diagonally toward the room center and the coffee table, resolving the F4 orientation conflict while maintaining clearance. |
| 24442 | 2 | move_piece | f_L-1b_051 | score: plausibility -15 -> -45 (G3 f_L-1b_051: armchair f_L-1b_051 is 41° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.69 m (needs ≤ 2.50 m); G11 f_L-1b_052: armchair f_L-1b_052: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_073: bookshelf f_L-1b_073: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_075: armchair f_L-1b_075: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Move armchair 0.4m south to open the blocked free zone in front of it and improve angle to sofa f_L-1b_042. |
| 24444 | 2 | rotate_piece | f_L1_052 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L1_052 is still there after the edit (armchair does not face its group (f_L1_017, f_L1_023)) | Armchair f_L1_052 stands behind the back of sofa f_L1_017 looking at it; rotate to face the room/coffee table to fix orientation. |
| 24445 | 2 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Move coffee table 0.18 m toward the window to clear the 0.12 m² overlap with armchair f_L-1_071 while staying within the 0.179 m move allowance. |
| 24446 | 2 | retype_piece | f_L-1_021 | retype: kitchen_counter is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m drawn piece is too long for a sideboard; a kitchen counter fits its dimensions and the living room context. |
| 24447 | 2 | swap_model | f_L0_010 | max_tries: f_L0_010 was edited 3 times in this round | Replace the raw light wood wardrobe with a model that matches the darker wood and refined finish of the room's style. |
| 24448 | 2 | rotate_piece | f_L1_052 | acceptance: finding F4:f_L1_052 is still there after the edit (armchair stands behind the back of f_L1_017, looking at it) | Armchair f_L1_052 stands behind the back of sofa f_L1_017; rotate to face the coffee table f_L1_023 to fix orientation. |
| 24449 | 2 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe to the west end of the south wall, away from the door swing, to open the 0.80 m front clearance G13 needs. |
| 24450 | 2 | move_piece | f_L-1b_054 | memory: the same edit was rejected in round 2: acceptance: finding F6:f_L-1b_053 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_054); 1 more kept | Fixes c:F6:f_L-1b_053, c:F6:f_L-1b_054, a:F6:f_L-1b_054, c:G3:f_L-1b_054, a:F247, a:F590: the armchair blocks the free zone in front of f_L-1b_053 and is 33° off the sofa; shifting it 0.36 m away from f_L-1b_053 clears the path and improves alignment. |
| 24452 | 2 | move_piece | f_L-1b_054 | max_tries: f_L-1b_054 was edited 3 times in this round | Fixes c:F6:f_L-1b_053, c:F6:f_L-1b_054, a:F6:f_L-1b_054, c:G3:f_L-1b_054, a:F247, a:F590: the armchair blocks the free zone in front of f_L-1b_053 and is 33° off the sofa; shifting it 0.46 m away from f_L-1b_053 clears the path and improves alignment. |
| 24453 | 2 | relayout_room | r_L-1b_salon | group checks: F6 f_L-1b_046: sofa: the free zone in front of it is blocked by f_L-1b_096; G9 r_L-1b_salon_kitchen: kitchen r_L-1b_salon_kitchen has no fridge (fridge) | Use solver candidate 1 to add missing TV units and coffee tables for both seating groups and improve overall seating layout. |
| 24456 | 2 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Confirm the drawn piece is a wardrobe (coat closet with hanging rail), resolving the AI-passes bench misread. |
| 24459 | 2 | move_piece | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | The south wall is only 0.97 m deep, so no position there gives the 0.80 m front clearance; move the wardrobe to the east wall (3.62 m span) where its front faces the open room. |
| 24460 | 2 | move_piece | f_L1_052 | f_L1_052: clearance_ok | Move reading-corner armchair f_L1_052 out of the back zone of sofa f_L1_017 so it no longer stands behind the sofa's back. |
| 24461 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Candidate 1 failed G13/G5 in round 1; candidate 2 has different partner/balance terms and may resolve the wardrobe front and bed side clearances plus the missing right nightstand. |
| 24462 | 2 | move_piece | f_L0_021 | score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Shift the bed 0.30 m east so the left side gains the 0.60 m clearance G5 needs (0.37 m free) while the right side keeps 0.52 m. |
| 24463 | 2 | set_room_type | r_L-1b_salon | acceptance: finding RC:f_L-1b_056 is still there after the edit (f_L-1b_056: the AI passes typed it fridge; the block name says sink_kitchen) | The room contains a full kitchen run with sink, stove, counters and island; setting type to kitchen makes the sink_kitchen reading consistent. |
| 24464 | 2 | move_piece | f_L1_031 | f_L1_030: clearance_ok, f_L1_030: no_overlap, f_L1_031: no_overlap | Move armchair f_L1_031 closer to coffee table f_L1_023 (2.73m > 2.50m) to fix the group layout distance. |
| 24466 | 2 | move_piece | f_L0_021 | score: plausibility 67 -> 37 (F3 f_L0_021: bed_double: the headboard stands in the room (0.15 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free); G5 f_L0_021: bed_double f_L0_021: 0.38 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.15 m east (headboard stays on the west wall) to open the left side to 0.52 m, easing the G5 side clearances. |
| 24468 | 2 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back to the right wall (w_L-1b_010) to clear F3 (back not on wall) and F6 (free zone blocked). |
| 24470 | 2 | move_piece | f_L0_021 | acceptance: finding G5:f_L0_021 is still there after the edit (bed_double f_L0_021: 0.23 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.15 m south (headboard stays on the west wall) to open the right side to 0.67 m, clearing the right-side G5. |
| 24471 | 2 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Shift the wardrobe along the south wall to open the 0.8 m front clearance the G13 check needs. |
| 24474 | 2 | move_piece | f_L-1b_071 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Move side table 0.5m south to clear the free zone in front of sofa f_L-1b_046 (F6). |
| 24475 | 2 | move_piece | f_L0_021 | max_tries: f_L0_021 was edited 3 times in this round | Shift the bed 0.15 m north (headboard stays on the west wall) to open the left side to 0.52 m, easing the left-side G5. |
| 24478 | 2 | move_piece | f_L0_028 | snap: f_L0_028: no free place on wall w_L0_016 (doors, windows, at most 1.2 m from the drawn place) | Shift the desk along the east wall to clear the wardrobe's front opening for the 0.8 m G13 clearance. |
| 24481 | 2 | move_piece | f_L0_028 | score: plausibility 67 -> 57 (F3 f_L0_028: desk: its back is not on a wall (0.15 m off)) | Shift the desk left to open the wardrobe's front opening for the 0.8 m G13 clearance. |
| 24484 | 2 | move_piece | f_L0_028 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift the desk up along the east wall to open the wardrobe's front opening for the 0.8 m G13 clearance. |
| 24489 | 2 | move_piece | f_L0_028 | max_tries: f_L0_028 was edited 3 times in this round | c:G13:f_L0_011 — shift the desk up along the east wall to open the wardrobe's front opening for the 0.8 m G13 clearance. |
| 24492 | 2 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.22 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | c:G5:f_L0_022 — shift the bed left to open the right-side clearance to ≥0.6 m. |
| 24493 | 2 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Toilet built below library level (parametric mesh) and 0.33 m from left wall; japandi toilet 0.415x0.568 m is the closest real-size model to the drawn 0.5x0.69 m, narrower to gain the 0.38 m clearance. |
| 24494 | 2 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | c:M28:r_L0_yatak_odasi_4 — swap to a mid-century louvered bed with a tall headboard to dress the bare wall behind the bed. |
| 24496 | 2 | swap_model | f_L1_022 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Toilet built below library level (parametric mesh); japandi toilet 0.415x0.692 m matches the drawn 0.5x0.69 m footprint closely, a library-level model. |
| 24497 | 2 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swapping to a floor-standing modern washbasin model to clear S1. |
| 24498 | 2 | set_camera | r_L-1_koridor_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | a:F196: reposition to a free point showing the hall open and furnished, not a bare wall with closed doors |
| 24502 | 2 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_classic_3_293965c2: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Toilet built below library level (parametric mesh); classic toilet 0.396x0.724 m is a library-level model close to the drawn 0.5x0.69 m. |
| 24503 | 2 | swap_model | f_L-1_052 | pin_refused: f_L-1_052: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Toilet model floats 0.20 m above floor and is too wide for the 0.33 m side clearance; this generated toilet matches the drawn 0.5x0.69 m footprint and sits on the floor. |
| 24505 | 2 | resize_piece | f_L-1_090 | score: plausibility 77 -> 67 (G12 f_L-1_090: fridge f_L-1_090 (1.80 m) stands in front of window win_L-1_003 (sill 0.90 m + 0.05)) | Resizing the fridge to a proper standard size (0.7m wide × 0.65m deep) so the G9 check recognizes it as a valid fridge |
| 24506 | 2 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Washbasin floats +0.384 m above its floor; japandi washbasin 0.633x0.487 m is a library-level model close to the drawn 1.0x0.55 m that sits on the floor. |
| 24507 | 2 | swap_model | f_L-1_026 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); swapping to a real floor-standing sink model to clear S1. |
| 24508 | 2 | swap_model | f_L-1_052 | acceptance: pin_refused: f_L-1_052: 3dwh_670407ad54a23fbdf5bbd2fe: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Toilet model floats 0.20 m above floor and is too wide for the 0.33 m side clearance; this real toilet (0.43 x 0.72 m) is narrower and sits on the floor. |
| 24509 | 2 | swap_model | f_L-1_051 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swapping to a real floor-standing toilet model to clear S1. |
| 24510 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current washbasin model floats 0.384 m above the floor; swap to a grounded modern washbasin model with correct base height. |
| 24511 | 2 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Washbasin floats +0.384 m above its floor; minimal washbasin 0.592x0.522 m is a library-level model close to the drawn 1.0x0.55 m. |
| 24512 | 2 | swap_model | f_L0_018 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | S1: current toilet model floats 0.200 m above the floor; swap to a grounded toilet model with correct base height. |
| 24517 | 2 | swap_model | f_L-1_052 | asset_unusable: objaverse_bd0f8d2bfba24376bec2b827a0cbbabe is not used: audit removed | Toilet model floats 0.20 m above floor and is too wide for the 0.33 m side clearance; this real toilet (0.42 x 0.67 m) is narrower and sits on the floor. |
| 24518 | 2 | swap_model | f_L1_022 | max_tries: f_L1_022 was edited 3 times in this round | Toilet built below library level (parametric mesh); japandi toilet 0.405x0.709 m is a library-level model close to the drawn 0.5x0.69 m. |
| 24519 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current washbasin model floats 0.384 m above the floor; swap to a grounded japandi washbasin model with correct base height. |
| 24520 | 2 | swap_model | f_L0_018 | pin_refused: f_L0_018: gen_toilet_classic_3_293965c2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current toilet model floats 0.200 m above the floor; swap to a grounded classic toilet model with correct base height. |
| 24521 | 2 | swap_model | f_L-1_026 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); swapping to a real floor-standing vanity unit model to clear S1. |
| 24522 | 2 | swap_model | f_L-1_051 | acceptance: pin_refused: f_L-1_051: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Current toilet model floats 0.200 m above the floor (S1); swapping to a real floor-standing toilet model to clear S1. |
| 24523 | 2 | swap_model | f_L-1_052 | max_tries: f_L-1_052 was edited 3 times in this round | Toilet model floats 0.20 m above floor and is too wide for the 0.33 m side clearance; this real toilet (0.45 x 0.63 m) is narrower and sits on the floor. |
| 24524 | 2 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Washbasin floats +0.384 m above its floor; modern washbasin 0.616x0.501 m is a library-level model close to the drawn 1.0x0.55 m. |
| 24527 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current washbasin model floats 0.384 m above the floor; swap to a grounded minimal washbasin model with correct base height. |
| 24529 | 2 | swap_model | f_L0_018 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | S1: current toilet model floats 0.200 m above the floor; swap to a grounded minimal toilet model with correct base height. |
| 24530 | 2 | swap_model | f_L0_018 | max_tries: f_L0_018 was edited 3 times in this round | S1: current toilet model floats 0.200 m above the floor; swap to a grounded japandi toilet model with correct base height. |
| 24531 | 2 | swap_model | f_L-1_025 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Washbasin model floats 0.384 m above its floor; this real sink (0.97 x 0.50 m) matches the drawn 1.0 x 0.55 m footprint and sits on the floor. |
| 24535 | 2 | swap_model | f_L-1_026 | max_tries: f_L-1_026 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor (S1); swapping to a real floor-standing Ikea sink model to clear S1. |
| 24536 | 2 | swap_model | f_L0_003 | max_tries: f_L0_003 was edited 3 times in this round | S1: current washbasin model floats 0.384 m above the floor; swap to a grounded mediterranean washbasin model with correct base height. |
| 24538 | 2 | swap_model | f_L-1_025 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Washbasin model floats 0.384 m above its floor; this real vanity unit (0.91 x 0.60 m) matches the drawn 1.0 x 0.55 m footprint and sits on the floor. |
| 24539 | 2 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Adding a proper 70cm fridge to the kitchen run to satisfy the G9 check for a missing fridge |
| 24543 | 2 | swap_model | f_L-1_025 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Washbasin model floats 0.384 m above its floor; this real sink (0.96 x 0.50 m) matches the drawn 1.0 x 0.55 m footprint and sits on the floor. |
| 24547 | 2 | set_camera | r_L1_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The frame is black/empty at z=4.4 under the sloped ceiling; re-aim at eye height to show the bathroom's main group (basin, toilet, tub). |
| 24550 | 2 | swap_model | f_L-1_090 | built_in: f_L-1_090: the fridge stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Swapping the small 0.6x0.6x0.82 fridge for a proper 0.75x0.68x1.68 fridge model so the G9 check recognizes it as a valid fridge |
| 24553 | 2 | set_camera | r_L1_banyo | memory: the same edit was rejected in round 2: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | a:F28 — the frame is black/empty at z=4.4 under the sloped ceiling; re-aim at eye height to show the bathroom's main group (basin, toilet, tub). |
| 24555 | 2 | relayout_room | r_L-1_mutfak | no_place: r_L-1_mutfak relayout: no place passes the checks (dining: no place passes the checks) | Trying the solver's best candidate to see if it resolves the G9 no-fridge finding by re-placing the AI pieces |
| 24556 | 2 | move_piece | f_L-1_090 | score: plausibility 77 -> 11 (G8 f_L-1_067: work triangle: fridge-sink 2.81 m, hob-fridge 3.45 m (legs 1.20-2.70 m, sum ≤ 7.90 m); G8 f_L-1_090: fridge f_L-1_090: 0.00 m of counter beside it, needs ≥ 0.38 m on one side; G11 f_L-1_001: kitchen_counter f_L-1_001: its front use zone is not reached by a 0.60 m walkway from door d_L-1_003; G11 f_L-1_002: kitchen_counter f_L-1_002: its front use zone is not reached by a 0.60 m walkway from door d_L-1_003) | Moving the fridge to the bottom wall to free up the left wall and see if the G9 check is satisfied |
| 24557 | 2 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Trying the I-shape option to see if it resolves the G9 no-fridge finding by re-solving the kitchen run |
| 25086 | 3 | retype_piece | f_L1_054 | exists: no piece 'f_L1_054' in a room of the building | Argus: A shoe_cabinet in an upper-floor hall is inappropriate; the L-1b hall correctly has a console_table, so the L1 hall's shoe_cabinet must be retyped to match. (fixes a:F486) |
| 25090 | 3 | place_group | r_L0_e_banyo_2 | no_change: r_L0_e_banyo_2 already has its bathroom_set r_L0_e_banyo_2.bathroom_set (anchor f_L0_014, members f_L0_004, f_L0_016): nothing missing, never a second set | Argus: The en-suite bathroom r_L0_e_banyo_2 has only shower, toilet, washbasin and is missing the tall_cabinet that its twin r_L0_e_banyo has, so the room's storage set is incomplete. (fixes a:N143) |
| 25091 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 2: no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi is already a living | Argus: The 40.5 m2 room is typed 'other' and furnished as a living room (sofa, tv_unit, table_dining, table_coffee, armchair, bookshelf, bench, ottoman, sideboard, floor_lamp, chair, potted_plant). The documents name it 'Oyun Aktivite Ve Dinlenme  (fixes a:N144) |
| 25092 | 3 | retype_piece | f_L1_018 | retype: console_table is no candidate for f_L1_018 (2.10 x 0.90 m at [10.96, 4.02]): the size table and the room / zone give chaise, desk, sofa, table_dining | Argus: The L1 hall (15.3 m2) contains a shoe_cabinet, a stair and a wardrobe. A shoe_cabinet in an upper-floor hall is unusual (shoe storage belongs at the entrance on L0 or L-1). The wardrobe in a 15.3 m2 hall is also questionable; it may be a mi (fixes a:N148) |
| 25093 | 3 | retype_piece | f_L-1_057 | no_change: f_L-1_057 is already a floor_lamp | the plan names it: Argus: Argus: drawn piece f_L-1_057 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_05 (fixes a:c7) |
| 25094 | 3 | retype_piece | f_L-1_059 | no_change: f_L-1_059 is already a floor_lamp | the plan names it: Argus: Argus: drawn piece f_L-1_059 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_06 (fixes a:c8) |
| 25095 | 3 | retype_piece | f_L-1_064 | no_change: f_L-1_064 is already a floor_lamp | the plan names it: Argus: Argus: drawn piece f_L-1_064 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_06 (fixes a:c9) |
| 25096 | 3 | retype_piece | f_L-1_066 | no_change: f_L-1_066 is already a floor_lamp | the plan names it: Argus: Argus: drawn piece f_L-1_066 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_06 (fixes a:c10) |
| 25097 | 3 | retype_piece | f_L-1_075 | no_change: f_L-1_075 is already a ottoman | the plan names it: Argus: Argus: drawn piece f_L-1_075 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png) although an AI pass named it ottoman, w (fixes a:c11) |
| 25098 | 3 | retype_piece | f_L-1_076 | no_change: f_L-1_076 is already a ottoman | the plan names it: Argus: Argus: drawn piece f_L-1_076 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png) although an AI pass named it ottoman, w (fixes a:c12) |
| 25099 | 3 | retype_piece | f_L-1_077 | no_change: f_L-1_077 is already a ottoman | the plan names it: Argus: Argus: drawn piece f_L-1_077 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png) although an AI pass named it ottoman, w (fixes a:c13) |
| 25100 | 3 | retype_piece | f_L-1_078 | no_change: f_L-1_078 is already a ottoman | the plan names it: Argus: Argus: drawn piece f_L-1_078 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_026_ctx.png) although an AI pass named it ottoman, w (fixes a:c14) |
| 25103 | 3 | resize_piece | f_L-1b_042 | memory: the same edit was rejected in round 2: score: plausibility -15 -> -25 (F3 f_L-1b_042: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_051: armchair does not face its group (f_L-1b_042, f_L-1b_046); F4 f_L-1b_075: armchair does not face its group (f_L-1b_046, f_L-1b_042); G3 f_L-1b_051: armchair f_L-1b_051 is 65° off the sofa f_L- | c:F2:f_L-1b_042: the drawn 0.90x2.13 m sofa is turned 90° against product sizes; swap to a 2.13 m wide x 0.90 m deep sofa footprint. |
| 25105 | 3 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.21 m) | c:F3:f_L-1b_046: shift the sofa 0.59 m right so its back sits on wall w_L-1b_010 (span s2) and its front zone clears f_L-1b_071. |
| 25108 | 3 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | c:F3:f_L-1b_046: snap the sofa's back onto wall w_L-1b_010 (span s2) so it is no longer 0.59 m off the wall. |
| 25109 | 3 | rotate_piece | f_L-1b_052 | memory: the same edit was rejected in round 2: acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)); 1 more kept | c:F4:f_L-1b_052: turn the armchair to face the seating group (towards the sofa f_L-1b_042) instead of away from it. |
| 25111 | 3 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.20 m) | c:F3:f_L-1b_046: shift the sofa 0.59 m right so its back sits on wall w_L-1b_010 (span s2) and its front zone clears f_L-1b_071. |
| 25113 | 3 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)) | c:F4:f_L-1b_052: turn the armchair to face the seating group (towards the sofa f_L-1b_042) instead of away from it. |
| 25116 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: swap: X3:r_L1_oyun_aktivite_ve_dinlenme_odasi_2 replaces AI1:r_L1_oyun_aktivite_ve_dinlenme_odasi_2 on r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (living): 5.6 m of outer wall with no window or door: a blank facade): the piece keeps as many critical /  | 40.5 m2 room with sofa, dining, TV unit and bookshelf, identical to its twin typed 'living'; fixes a:F154 and makes the bench a valid piece (F1, G14). |
| 25117 | 3 | rotate_piece | f_L-1_101 | score: plausibility 30 -> -10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_049: armchair stands behind the back of f_L-1_101, looking at it; F4 f_L-1_053: sofa_corner stands behind the back of f_L-1_101, looking at it; F4 f_L-1_101: tv_unit faces a wall 0.02 m in front of it) | Rotate the TV unit to face the seating area so it is no longer behind the back of armchair f_L-1_071. |
| 25118 | 3 | move_piece | f_L-1_073 | memory: the same edit was rejected in round 1: score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.10 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move the coffee table slightly to clear the 0.12 m² overlap with armchair f_L-1_071 while staying within the 0.179 m move allowance. |
| 25121 | 3 | move_piece | f_L-1b_046 | max_tries: f_L-1b_046 was edited 3 times in this round | c:F3:f_L-1b_046: shift the sofa 0.58 m right so its back sits on wall w_L-1b_010 (span s2) and its front zone clears f_L-1b_071. |
| 25122 | 3 | move_piece | f_L-1b_052 | score: plausibility -15 -> -25 (F6 f_L-1b_042: sofa: the free zone in front of it is blocked by f_L-1b_052; G3 f_L-1b_052: armchair f_L-1b_052 is 126° off the sofa f_L-1b_042 (needs ≤ 30°) at 0.64 m (needs ≤ 2.50 m)) | c:F6:f_L-1b_052: move the armchair 0.4 m away from f_L-1b_051 so the free zone in front of each chair is no longer blocked by the other. |
| 25123 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Snap the floating TV unit to the wall and reposition the seating groups so the coffee table sits between sofa and TV and the armchairs face the group, resolving F3, G2, G1, G3 and the sofa clearance. |
| 25127 | 3 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 37 -> 17 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Face the armchair towards the seating group/sofa instead of the window wall to fix F4 (standing behind the back of the sofa). |
| 25128 | 3 | move_piece | f_L-1_074 | score: plausibility 37 -> 27 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.09 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Shift the coffee table away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 25134 | 3 | remove_piece | f_L0_045 | memory: the same edit was rejected in round 1: score: plausibility 70 -> 67 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free)) | Nightstand f_L0_045 (added_by_ai) blocks window win_L0_004 (G12); removing it clears the window obstruction while the bed keeps nightstand f_L0_044. |
| 25135 | 3 | move_piece | f_L-1b_051 | acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052) | c:F6:f_L-1b_051: move the armchair 0.4 m away from f_L-1b_052 so the free zone in front of each chair is no longer blocked by the other. |
| 25142 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | c:G6:f_L-1b_033: nudge the chair 0.04 m so the clearance from the table edge to the piece behind reaches at least 0.81 m. |
| 25145 | 3 | relayout_room | r_L0_yatak_odasi_3 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve layout to fix wardrobe front clearance and bed side clearances and place the missing nightstand. |
| 25146 | 3 | swap_model | f_L1_089 | off_style: f_L1_089: ArmChair_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Swap the defective 3dwh armchair (back/arm 5.2 cm off the seat, M33) for a clean classic armchair model. |
| 25150 | 3 | swap_model | f_L1_091 | off_style: f_L1_091: ArmChair_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Swap the defective 3dwh armchair (back/arm 5.2 cm off the seat, M33) for a clean classic armchair model. |
| 25151 | 3 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Try the second solver candidate to fix wardrobe front clearance, bed side clearances and the missing nightstand. |
| 25153 | 3 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a sideboard: the long low storage unit matches its size and the living room. |
| 25155 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | c:G6:f_L-1b_033: nudge the chair 0.09 m so the clearance from the table edge to the piece behind reaches at least 0.81 m. |
| 25157 | 3 | swap_model | f_L1_089 | acceptance: pin_refused: f_L1_089: modern_arm_chair_01: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the defective 3dwh armchair (M33) for a modern armchair model matching the project's modern style chain. |
| 25158 | 3 | resize_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L- | c:F2:f_L-1b_041: the drawn 0.90 x 2.13 m sofa is turned 90° against product sizes; restore the real 2.13 m wide x 0.90 m deep sofa |
| 25160 | 3 | retype_piece | f_L-1_022 | retype: kitchen_counter is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m long run matches a counter run; typing it resolves the untyped finding. |
| 25161 | 3 | move_piece | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Bed f_L0_020 has 0.53m (right) and 0.56m (left) side clearance, needs 0.60m; re-centering toward the room centre to balance both sides. |
| 25162 | 3 | retype_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: retype: sofa is no candidate for f_L-1b_041 (0.90 x 2.13 m at [10.98, 4.48]): the size table and the room / zone give chaise, stair | a:F61: confirm the drawn sofa's type so it is fitted and built as a real sofa, resolving the 90°-turned size reading |
| 25163 | 3 | move_piece | f_L-1b_052 | max_tries: f_L-1b_052 was edited 3 times in this round | c:F6:f_L-1b_052: move the armchair 0.6 m away from f_L-1b_051 so the free zone in front of each chair is no longer blocked by the other. |
| 25168 | 3 | swap_model | f_L1_091 | acceptance: pin_refused: f_L1_091: modern_arm_chair_01: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the defective 3dwh armchair (M33) for a modern armchair model matching the project's modern style chain. |
| 25169 | 3 | retype_piece | f_L-1_022 | retype: display_cabinet is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | The 5.54 x 0.60 m long low unit matches a display cabinet run; typing it resolves the untyped finding. |
| 25173 | 3 | retype_piece | f_L-1_022 | max_tries: f_L-1_022 was edited 3 times in this round | The 5.54 x 0.60 m long unit matches a wall cabinet run; typing it resolves the untyped finding. |
| 25176 | 3 | swap_model | f_L1_089 | acceptance: pin_refused: f_L1_089: abo_B07124WN69: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the defective 3dwh armchair (M33) for a modern/scandinavian accent chair that fits the style chain and height caps. |
| 25177 | 3 | relayout_room | r_L-1_salon_2 | acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 2 more kept | Relayout with candidate 1 (circulation 0.98, recommended) to clear the G11 walkway findings for the seating group. |
| 25180 | 3 | swap_model | f_L0_021 | acceptance: finding G5:f_L0_021 is still there after the edit (bed_double f_L0_021: 0.52 m free along the right side, needs ≥ 0.60 m) | Swap to a modern minimal bed with a headboard panel and smooth modern bedding to address the bare wall behind the bed (M28) and the lumpy duvet / missing throw (M30). |
| 25184 | 3 | set_camera | r_L1_banyo | refused pose: cam_r_L1_banyo_1: eye height -1.45 m (wanted 1.2-1.6 m); the camera stands 0.01 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [6.02, 10.63]; the nearest searched pose is the one the view has, no_change: cam_r_L1_banyo_1 has this pose already (the accepted override (overrides.json seq 772)): position [6.0185, 10.635, 4.4], target [7.0185, 10.635, 4.4], lens 24.0 mm; nothing to change | a:N145: camera was at 4.4 m height showing only a blank wall; move to eye level in the free corner to frame the bathroom fixtures |
| 25185 | 3 | swap_model | f_L1_091 | acceptance: pin_refused: f_L1_091: abo_B07124WN69: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the defective 3dwh armchair (M33) for a modern/scandinavian accent chair that fits the style chain and height caps. |
| 25186 | 3 | move_piece | f_L0_011 | f_L0_011: no_overlap, f_L0_028: clearance_ok, score: plausibility 67 -> 47 (F3 f_L0_011: wardrobe: its back is not on a wall (0.27 m off); F9 f_L0_028: desk f_L0_028 overlaps wardrobe f_L0_011 by 0.05 m²; G13 f_L0_011: wardrobe f_L0_011: 0.35 m free in front, needs ≥ 0.80 m) | c:G13:f_L0_011: shift wardrobe 0.3 m off the south wall to open the 0.8 m front clearance |
| 25187 | 3 | relayout_room | r_L-1_salon_2 | candidate: candidate 2 does not exist: 1 usable candidate(s) | Try candidate 2 (circulation 1.0) to clear the G11 walkway findings for the seating group. |
| 25188 | 3 | relayout_room | r_L1_koridor | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-place the AI pieces with the solver's best candidate so the hall gains its console/wall-niche member (M28 H1, H4). |
| 25189 | 3 | set_camera | r_L1_banyo | memory: the same edit was rejected in round 3: refused pose: cam_r_L1_banyo_1: eye height -1.45 m (wanted 1.2-1.6 m); the camera stands 0.01 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [6.02, 10.63]; the nearest searched pose is the one the view has; no_change: cam_r_L1_banyo_1 has this pose a | a:N145: camera at 4.4 m height shows only a blank wall; move to eye level in the free corner to frame the bathroom fixtures |
| 25190 | 3 | move_piece | f_L0_022 | memory: the same edit was rejected in round 2: score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.22 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | c:G5:f_L0_022: shift bed 0.22 m left to open the right-side clearance to 0.6 m |
| 25193 | 3 | swap_model | f_L1_089 | max_tries: f_L1_089 was edited 3 times in this round | Swap the defective 3dwh armchair (M33) for a modern minimal accent chair that fits the style chain and height caps. |
| 25194 | 3 | set_camera | r_L1_banyo | memory: the same edit was rejected in round 3: refused pose: cam_r_L1_banyo_1: eye height -1.45 m (wanted 1.2-1.6 m); the camera stands 0.01 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [6.02, 10.63]; the nearest searched pose is the one the view has; no_change: cam_r_L1_banyo_1 has this pose a | a:N145: camera at 4.4 m height shows only a blank wall; move to eye level in the free corner to frame the bathroom fixtures |
| 25195 | 3 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.27 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | c:G5:f_L0_022: shift bed 0.27 m left to open the right-side clearance to 0.6 m |
| 25196 | 3 | swap_model | f_L1_091 | max_tries: f_L1_091 was edited 3 times in this round | Swap the defective 3dwh armchair (M33) for a modern minimal accent chair that fits the style chain and height caps. |
| 25197 | 3 | relayout_room | r_L1_koridor | memory: the same edit was rejected in round 3: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes a:F313 (M28, target r_L1_koridor): re-place the AI pieces with the solver's best candidate so the hall gains its console/wall-niche member (H1, H4). |
| 25200 | 3 | move_piece | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.16 m free along the right side, needs ≥ 0.60 m) | c:G5:f_L0_022#2: shift bed 0.22 m down to open the left-side clearance to 0.6 m |
| 25202 | 3 | move_piece | f_L-1_050 | f_L-1_050: no_overlap, f_L-1_054: clearance_ok, f_L-1_088: no_overlap, score: plausibility 37 -> 17 (F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_050; F9 f_L-1_088: table_coffee f_L-1_088 overlaps armchair f_L-1_050 by 0.09 m²) | Shift armchair f_L-1_050 away from the sofa to open a 0.60 m walkway to its front use zone (G11). |
| 25203 | 3 | relayout_room | r_L1_koridor | max_tries: r_L1_koridor was edited 3 times in this round | Fixes a:F313 (M28, target r_L1_koridor): re-place the AI pieces with solver candidate 2 so the hall gains its console/wall-niche member (H1, H4). |
| 25208 | 3 | move_piece | f_L0_022 | max_tries: f_L0_022 was edited 3 times in this round | c:G5:f_L0_022: shift bed 0.22 m left and 0.22 m down to open both side clearances to 0.6 m |
| 25218 | 3 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall); with the front at 0 deg its back is not on a wall | Shower front faces a wall at 90° with only 0.10 m clearance; turning it to 0° orients the front into the room interior. |
| 26085 | 4 | swap_model | f_L0_019 | acceptance: finding G5:f_L0_019 is still there after the edit (bed_double f_L0_019: 0.56 m free along the right side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves only 0.53 m on the left side (needs 0.60 m) in a 16.1 m2 room; the 1.45 m model frees 0.10 m, which meets the 0.60 m side clearance. Moving the bed was refused (it would break the nightstand pairing), so shrinking the  (fixes a:F66) |
| 26086 | 4 | swap_model | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves 0.53 m on the right side (needs 0.60 m); the 1.54 m model frees 0.01 m, which meets the 0.60 m side clearance. Moving the bed was refused (it would break the nightstand pairing), so shrinking the bed is the cause fix. (fixes a:F67) |
| 26087 | 4 | swap_model | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.66 m free in front, needs ≥ 0.80 m) | Argus: The 0.60 m-deep wardrobe leaves only 0.66 m in front (needs 0.80 m) and is already pushed against the wall (moving it out was refused as it would cross the room outline). The 0.51 m-deep model frees 0.09 m, giving 0.75 m; combined with the  (fixes a:F68) |
| 26088 | 4 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The drawn 1.40 x 0.60 m shower is outside the product range (depth 0.70-1.20 m); the 0.60 m depth is a misread of the bay. A 1.40 x 0.80 m shower is a real product size within range and fits the 4.0 m2 bathroom bay. (fixes a:F69) |
| 26089 | 4 | fix_fixture | f_L0_014 | fixture_size: f_L0_014: the drawn 0.60 x 1.40 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The drawn 0.60 x 1.40 m shower is outside the product range (width 0.70-1.60 m); the 0.60 m width is a misread of the bay. A 0.80 x 1.40 m shower is a real product size within range and fits the 4.0 m2 bathroom bay. (fixes a:F70) |
| 26090 | 4 | swap_model | f_L0_021 | acceptance: finding G5:f_L0_021 is still there after the edit (bed_double f_L0_021: 0.52 m free along the right side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves only 0.37 m on the left side (needs 0.60 m) in a 14.1 m2 room; the 1.45 m model frees 0.10 m, giving 0.47 m. Moving the bed was refused (it would break the nightstand pairing and push the headboard off the wall). The r (fixes a:F71) |
| 26091 | 4 | swap_model | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Argus: The 0.60 m-deep wardrobe leaves only 0.17 m in front (needs 0.80 m) and is already against the wall (moving it out was refused). The 0.57 m-deep model frees 0.03 m, giving 0.20 m. The room is too small for a 0.60 m wardrobe with 0.80 m clea (fixes a:F72) |
| 26092 | 4 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves only 0.37 m on the right side (needs 0.60 m) in a 14.0 m2 room; the 1.45 m model frees 0.10 m, giving 0.47 m. Moving the bed was refused (it would break the nightstand pairing and push the headboard off the wall). The  (fixes a:F73) |
| 26093 | 4 | swap_model | f_L0_011 | no_change: f_L0_011 already uses the model abo_B07B3XXD3P | Argus: The 0.60 m-deep wardrobe leaves only 0.17 m in front (needs 0.80 m) and is already against the wall (moving it out was refused). The 0.57 m-deep model frees 0.03 m, giving 0.20 m. The room is too small for a 0.60 m wardrobe with 0.80 m clea (fixes a:F74) |
| 26095 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Argus: The tv_unit f_L1_063 is 1.01 m off the wall and 1.49 m off the sofa axis; moving it was refused (no free wall span, and moving it would break the sofa axis). The TV unit is misplaced in the seating group; re-solving the room's AI pieces wil (fixes a:F79) |
| 26096 | 4 | add_camera | r_L0_merdiven | show: none of the 6 best poses of r_L0_merdiven that show f_L0_001 passes the camera checks: cam_r_L0_merdiven_1 stands inside f_L0_001 (stair) | Argus: r_L0_merdiven (5.7 m2) has no view because the stair fills the room and its only camera point is inside the stair; a camera must be added from a free point (e.g. the adjacent hall) to show the stair. (fixes a:F112) |
| 26097 | 4 | set_camera | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 1: show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one | Argus: The required view of r_L0_e_yatak_odasi does not show door d_L0_002; re-aim the interior camera to include it. (fixes a:F120) |
| 26098 | 4 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 0.19 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No exterior camera shows the +y facade; adding one fixes it. (fixes a:F175) |
| 26100 | 4 | place_group | r_L1_banyo | memory: the same edit was rejected in round 1: no_change: r_L1_banyo already has its bathroom_set r_L1_banyo.bathroom_set (anchor f_L1_021, members f_L1_015, f_L1_025): nothing missing, never a second set | Argus: The bathroom set in r_L1_banyo is missing the mirror and towel rail. place_group completes the set with what it misses. (fixes a:F179) |
| 26101 | 4 | place_group | r_L1_banyo_2 | memory: the same edit was rejected in round 1: no_change: r_L1_banyo_2 already has its bathroom_set r_L1_banyo_2.bathroom_set (anchor f_L1_022, members f_L1_016, f_L1_026): nothing missing, never a second set | Argus: The bathroom set in r_L1_banyo_2 is missing the mirror and towel rail. place_group completes the set with what it misses. (fixes a:F180) |
| 26102 | 4 | place_group | r_L-1_banyo | memory: the same edit was rejected in round 1: no_change: r_L-1_banyo already has its bathroom_set r_L-1_banyo.bathroom_set (anchor f_L-1_051, members f_L-1_026, f_L-1_056): nothing missing, never a second set | Argus: The washbasin f_L-1_026 has no mirror and the room reads as unfinished. Completing the bathroom set adds the missing mirror and rail. (fixes a:F181) |
| 26103 | 4 | place_group | r_L0_banyo | memory: the same edit was rejected in round 1: no_change: r_L0_banyo already has its bathroom_set r_L0_banyo.bathroom_set (anchor f_L0_018, members f_L0_003, f_L0_025): nothing missing, never a second set | Argus: The washbasin f_L0_003 has no mirror and the walls are bare. Completing the bathroom set adds the missing mirror and rail. (fixes a:F183) |
| 26104 | 4 | place_group | r_L0_e_banyo | no_change: r_L0_e_banyo already has its bathroom_set r_L0_e_banyo.bathroom_set (anchor f_L0_013, members f_L0_006, f_L0_015): nothing missing, never a second set | Argus: The washbasin f_L0_006 has no mirror above it. Completing the bathroom set adds the missing mirror. (fixes a:F185) |
| 26106 | 4 | set_camera | r_L-1_banyo | show: none of the 8 best poses of r_L-1_banyo that show f_L-1_051, f_L-1_026, f_L-1_056 passes the camera checks: cam_r_L-1_banyo_1: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L-1_banyo_1 would show the view cam_r_L-1_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_banyo, or remove one of the two views | Argus: cam_r_L-1_banyo_1 shows the bathtub partially with a bare area around it; the camera is re-posed to show the tub with its bathroom set members. (fixes a:F195) |
| 26112 | 4 | place_group | r_L0_e_banyo_2 | memory: the same edit was rejected in round 3: no_change: r_L0_e_banyo_2 already has its bathroom_set r_L0_e_banyo_2.bathroom_set (anchor f_L0_014, members f_L0_004, f_L0_016): nothing missing, never a second set | Argus: r_L0_e_banyo_2 is missing its tall_cabinet while its twin r_L0_e_banyo has it. place_group was refused as no_change because the set already exists, but re-running the bathroom_set completion is the cause-level fix: it adds the missing membe (fixes a:F216) |

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
| M17 | minor | r_L-1_salon | r_L-1_salon | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon_2 | r_L-1_salon_2 | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M18 | major | f_L-1_020 | r_L-1_koridor | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M18 | major | f_L0_002 | r_L0_merdiven_2 | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M21 | major | r_L-1_salon_2 | r_L-1_salon_2 | layout | room_use | 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_banyo_2 | r_L0_e_banyo_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo | r_L1_banyo | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo_2 | r_L1_banyo_2 | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M31 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| M31 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| Q11 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi | r_L1_oyun_aktivite_ve_dinlenme_odasi | lighting | light_fixture | 1 | the finding is about a light fixture (the room's lighting rig), not the piece it names: no agent tool changes a light's model, so it is reported to the lighting stage |
| Q7 | minor | d_L0_001 | r_L0_koridor | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | minor | d_L0_005 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L-1_049 | r_L-1_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_089 | r_L-1_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_105 | r_L-1_koridor_2 | decor | decor_rest | 2, 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_107 | r_L-1_koridor_2 | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_019 | r_L0_yatak_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_021 | r_L0_yatak_odasi_3 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_022 | r_L0_yatak_odasi_4 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_061 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | facade | 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L-1_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L-1_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
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
| X5 | minor | win_L1_001 | - | - | scale | 2, 3, 4 | storey and door sizes come from the drawings |
| lighting_dark | minor | cam_r_L-1_banyo_1 | r_L-1_banyo | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | minor | cam_r_L-1_banyo_2 | r_L-1_banyo | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | minor | cam_r_L0_banyo_1 | r_L0_banyo | - | lighting_within_step | 2 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | major | cam_r_L0_e_banyo_2 | r_L0_e_banyo | - | lighting_beyond_cap | 2 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |
| lighting_dark | minor | cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | - | lighting_within_step | 3 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon_2 | cut | 2 | 8237 | 32768 |
| 1 | building | cut | 2 | 17728 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 2 | 7835 | 32768 |
| 2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 1 | 13791 | 32768 |
| 2 | r_L-1b_salon | cut | 2 | 11141 | 32768 |
| 2 | r_L1_teras_2 | cut | 1 | 33187 | 32768 |
| 2 | building | cut | 7 | 44174 | 32768 |
| 3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 1 | 15805 | 32768 |
| 3 | r_L-1b_salon | cut | 4 | 8354 | 32768 |
| 3 | building | cut | 12 | 51570 | 32768 |

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
| f_L-1_031 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1_031 slightly outward (south) to resolve the 0.040 m cut with the dining table. |
| f_L-1_039 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge chair f_L-1_039 off the table edge to clear the 0.034 m cut with table_dining f_L-1_038 (S2). |
| f_L-1_042 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge chair f_L-1_042 away from the table edge to clear the 0.034 m cut (S2). |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred | - | - | front: faces the coffee table f_L-1_087 |
| f_L-1_050 | piece | armchair | r_L-1_salon_2 | inferred | - | - | front: faces the coffee table f_L-1_088 |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_055 | piece | bathtub | r_L-1_banyo_2 | inferred | - | - | bathtub: r_L-1_banyo_2.bathroom_set (anchor f_L-1_052) misses shower\|bathtub, and the type's product range fits 1.83 x 0.80 m (the only missing member of that size); front: the free side facing the most room is the front |
| f_L-1_056 | piece | bathtub | r_L-1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L-1_055 in the twin room r_L-1_banyo_2 (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L-1_057 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays, f_L-1_057 is not built (plan crop recognition/crops/sym_L-1_005_ctx.png) |
| f_L-1_058 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.79 x 0.79 m -> 0.40 x 0.40 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026); size snap: the drawn floor lamp 0.60 x 0.60 m is a plan symbol larger than the product (a floor lamp takes at most 0.45 m from above): fitted at the real product 0.40 x 0.40 m, centred where it is drawn (CLAUDE.md: a drawn size outside its type's real product range is snapped to a real product before the fit; user, 29 Oct 2026: "I did not like this light", lesson UL94) |
| f_L-1_059 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays, f_L-1_059 is not built (plan crop recognition/crops/sym_L-1_007_ctx.png) |
| f_L-1_060 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.79 x 0.79 m -> 0.40 x 0.40 m | code (size_snap) | size snap: the drawn floor_lamp 0.79 x 0.79 m is outside its product range (width 0.79 m is 13 % outside 0.2-0.7 m; depth 0.79 m is 13 % outside 0.2-0.7 m; nearest real product 0.60 x 0.60 m); nearest real product 0.60 x 0.60 x 1.60 m (wide floor lamp 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026); size snap: the drawn floor lamp 0.60 x 0.60 m is a plan symbol larger than the product (a floor lamp takes at most 0.45 m from above): fitted at the real product 0.40 x 0.40 m, centred where it is drawn (CLAUDE.md: a drawn size outside its type's real product range is snapped to a real product before the fit; user, 29 Oct 2026: "I did not like this light", lesson UL94) |
| f_L-1_061 | piece | table_coffee | r_L-1_salon | inferred | - | - | table_coffee: r_L-1_salon.seating (anchor f_L-1_053) misses table_coffee, and the type's product range fits 1.30 x 0.63 m (the only missing member of that size) |
| f_L-1_062 | piece | table_coffee | r_L-1_salon_2 | inferred | - | - | table_coffee: the same footprint (1.30 x 0.63 m) as f_L-1_061 in the twin room r_L-1_salon (mirrored centre within 0.02 m) |
| f_L-1_063 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.59 x 0.59 m -> 0.40 x 0.40 m | architect | moved 0.18 m clear of win_L-1_001 (the answer to AI.move_piece:f_L-1_063) |
| f_L-1_064 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png) |
| f_L-1_065 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.59 x 0.59 m -> 0.40 x 0.40 m | architect | moved 0.18 m clear of win_L-1_002 (the answer to AI.move_piece:f_L-1_065) |
| f_L-1_066 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png) |
| f_L-1_069 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Argus: The brown leather armchair clashes with the white boxy sofa and the black lounge chair; the three seating pieces are of different styles and colors. (fixes a:F358) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_072 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai | size 0.56 x 0.56 m -> 0.80 x 0.80 m | code (architect F5) | architect F5: f_L-1_073 (table_coffee) cut f_L-1_071 (armchair) by 0.18 m; f_L-1_073 (table_coffee) moved 0.71 m clear of it (inside its room, clear of the other pieces and the doorways) |
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
| f_L0_009 | piece | wardrobe | r_L0_yatak_odasi_3 | adjusted_by_ai | - | architect | wardrobe f_L0_009: 0.17 m free in front of its doors or drawers (f_L0_029 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the wardrobe along its wall to increase the clearance in front from 0.66 m to at least 0.80 m. |
| f_L0_011 | piece | wardrobe | r_L0_yatak_odasi_4 | adjusted_by_ai | - | architect | wardrobe f_L0_011: 0.17 m free in front of its doors or drawers (f_L0_028 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred, adjusted_by_ai | - | code (back_gap) | shower f_L0_013: its back stood 0.10 m off its wall, parallel to it (a drawing gap): moved 0.08 m back onto the wall (plan crop recognition/reading/f_L0_013_ctx.png) |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_001 (the answer to AI.move_piece:f_L0_019) |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_004 (the answer to AI.move_piece:f_L0_020) |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred | - | - | bed_double: the same drawn block (the same strokes (22 INSERT here, within 2%)) and footprint (1.90 x 1.55 m, within 0.01 m) as f_L0_019, f_L0_020 (typed bed_double): one block, one type; front: its back stands on the only side on a wall |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_021 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m); front: its back stands on the only side on a wall |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred | - | - | wardrobe: the bedroom room misses its storage anchor (wardrobe), and the type's product range fits 3.11 x 0.60 m (the only missing member of that size); front: standing in a corner: its long side on the wall is the back |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - | - | wardrobe: the same footprint (3.11 x 0.60 m) as f_L0_023 in the twin room r_L0_e_yatak_odasi (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L0_025 in the twin room r_L0_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_035 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_036 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_037 stands in front; plan crop recognition/crops/sym_L0_011_ctx.png |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | Qwen/Qwen3.8-27B-FP8 (reading.desk_chair) | Argus: The white Shaker-style desk with its raised panel drawers is a dated, traditional piece that does not go with the modern, minimalist wood bed and the project's style. (fixes a:F366) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: Shift nightstand f_L0_032 away from the bed edge to clear the 0.06 m² overlap (F9) and correct the -0.12 m gap to a valid ≤ 0.30 m distance (G4). |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift nightstand 0.12 m away from the bed side to clear the 0.06 m² overlap and satisfy the ≤ 0.30 m gap requirement. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_005 | piece | table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dining table and chairs are a different, lighter style from the heavy white bench seating, so the room's furniture does not read as one coherent set. (fixes a:F347) |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_017 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Sofa f_L1_017 is a crude blocky white storage-bench model; swap to a proper modern 3-seat sofa to fix wrong_model. |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move sofa f_L1_019 slightly away from f_L1_018 to clear the blocked zone in front of it, fixing F6 clearance. |
| f_L1_020 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Sofa f_L1_020 is an identical clashing model to f_L1_017; swap to a different modern sofa to fix wrong_model. |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_025 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move armchair f_L1_031 closer to coffee table f_L1_023 (2.73m > 2.50m) to fix the group layout distance. (plan crop recognition/crops/sym_L1_009_ctx.png) |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_010_ctx.png |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | The 1.40 x 0.45 m bench against the south wall fits a console table, a valid living-room piece, resolving the wrong_type findings. (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: the same footprint (1.09 x 0.40 m) as f_L1_038 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (mirrored centre within 0.02 m) |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: A black mesh office chair and a plain desk read as a home-office, not a bedroom; they clash with the bed and the project's calm, styled style. (fixes a:F344) (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black leather office chair is a corporate piece that clashes with the warm, residential bedroom style. (fixes a:F365) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_039 | piece | shoe_cabinet | r_L0_koridor | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_039: the piece is not built |
| f_L0_040 | piece | shoe_cabinet | r_L0_koridor_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_040: the piece is not built |
| f_L0_042 | piece | nightstand | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move the nightstand away from the window opening to clear the blocked opening finding. |
| f_L0_045 | piece | nightstand | r_L0_yatak_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift nightstand f_L0_045 along the wall to clear window win_L0_004 (G12) while keeping it beside the bed. |
| f_L1_086 | piece | potted_plant | r_L1_teras_2 | adjusted_by_ai | - | architect | the answer to F3:win_L1_002: the piece is not built |
| f_L1_095 | piece | potted_plant | r_L1_teras | adjusted_by_ai | - | architect | the answer to F3:win_L1_001: the piece is not built |
| f_L1_100 | piece | armchair | r_L1_teras | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The terrace armchair's current model (3dwh_7c41f538b2d0873e672fe42f) is the same broken model that F30/F31 report as detached; swapping to a minimal/modern armchair of the same footprint fixes the missing-group look and the detached parts a (fixes a:F19) |
| o_L1_001 | geometry | fix_opening_on_wall | - | corrected_by_ai, record_only | - | - | Argus: The opening o_L1_001 is not cut through its wall w_L1_003; the door ray hits the wall. correct_geometry with fix_opening_on_wall puts the opening back on its wall and cuts it through. (fixes a:F249) |

Geometry corrections are record-only in M11: the drawn geometry was not changed; they are open items for the next full run.

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
| 1 | cam_r_L-1_banyo_2 | ![](agent/r1_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_2_after.jpg) |
| 1 | cam_r_L-1_koridor_2_1 | ![](agent/r1_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_1_after.jpg) |
| 1 | cam_r_L-1_mutfak_1 | ![](agent/r1_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_1_after.jpg) |
| 1 | cam_r_L-1_mutfak_2 | ![](agent/r1_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_2_after.jpg) |
| 1 | cam_r_L-1_mutfak_3 | ![](agent/r1_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r1_cam_r_L-1_mutfak_3_after.jpg) |
| 1 | cam_r_L-1_salon_1 | ![](agent/r1_cam_r_L-1_salon_1_before.jpg) | ![](agent/r1_cam_r_L-1_salon_1_after.jpg) |
| 1 | cam_r_L-1_salon_2 | ![](agent/r1_cam_r_L-1_salon_2_before.jpg) | ![](agent/r1_cam_r_L-1_salon_2_after.jpg) |
| 1 | cam_r_L-1_salon_3 | ![](agent/r1_cam_r_L-1_salon_3_before.jpg) | ![](agent/r1_cam_r_L-1_salon_3_after.jpg) |
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_banyo_2 | ![](agent/r1_cam_r_L0_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_banyo_2_after.jpg) |
| 1 | cam_r_L0_e_banyo_1 | ![](agent/r1_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_e_banyo_1_after.jpg) |
| 1 | cam_r_L0_e_banyo_2 | ![](agent/r1_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r1_cam_r_L0_e_banyo_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_koridor_1 | ![](agent/r1_cam_r_L0_koridor_1_before.jpg) | ![](agent/r1_cam_r_L0_koridor_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_1 | ![](agent/r1_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_2 | ![](agent/r1_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3 | ![](agent/r1_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r1_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r1_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 1 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r1_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r1_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 1 | cam_r_L1_banyo_1 | ![](agent/r1_cam_r_L1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L1_banyo_1_after.jpg) |
| 1 | cam_r_L1_koridor_1 | ![](agent/r1_cam_r_L1_koridor_1_before.jpg) | ![](agent/r1_cam_r_L1_koridor_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 1 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 1 | cam_r_L1_teras_1 | ![](agent/r1_cam_r_L1_teras_1_before.jpg) | ![](agent/r1_cam_r_L1_teras_1_after.jpg) |
| 1 | cam_r_L1_teras_2 | ![](agent/r1_cam_r_L1_teras_2_before.jpg) | ![](agent/r1_cam_r_L1_teras_2_after.jpg) |
| 1 | cam_r_L1_teras_3 | ![](agent/r1_cam_r_L1_teras_3_before.jpg) | ![](agent/r1_cam_r_L1_teras_3_after.jpg) |
| 1 | ext_1 | ![](agent/r1_ext_1_before.jpg) | ![](agent/r1_ext_1_after.jpg) |
| 1 | ext_2 | ![](agent/r1_ext_2_before.jpg) | ![](agent/r1_ext_2_after.jpg) |
| 1 | ext_3 | ![](agent/r1_ext_3_before.jpg) | ![](agent/r1_ext_3_after.jpg) |
| 1 | ext_5 | ![](agent/r1_ext_5_before.jpg) | ![](agent/r1_ext_5_after.jpg) |
| 1 | ext_7 | ![](agent/r1_ext_7_before.jpg) | ![](agent/r1_ext_7_after.jpg) |
| 2 | cam_r_L-1_banyo_1 | ![](agent/r2_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r2_cam_r_L-1_banyo_1_after.jpg) |
| 2 | cam_r_L-1_banyo_2 | ![](agent/r2_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r2_cam_r_L-1_banyo_2_after.jpg) |
| 2 | cam_r_L-1_koridor_2_1 | ![](agent/r2_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r2_cam_r_L-1_koridor_2_1_after.jpg) |
| 2 | cam_r_L-1_mutfak_1 | ![](agent/r2_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_1_after.jpg) |
| 2 | cam_r_L-1_mutfak_2 | ![](agent/r2_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_2_after.jpg) |
| 2 | cam_r_L-1_mutfak_3 | ![](agent/r2_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r2_cam_r_L-1_mutfak_3_after.jpg) |
| 2 | cam_r_L-1_salon_1 | ![](agent/r2_cam_r_L-1_salon_1_before.jpg) | ![](agent/r2_cam_r_L-1_salon_1_after.jpg) |
| 2 | cam_r_L-1_salon_2 | ![](agent/r2_cam_r_L-1_salon_2_before.jpg) | ![](agent/r2_cam_r_L-1_salon_2_after.jpg) |
| 2 | cam_r_L-1_salon_3 | ![](agent/r2_cam_r_L-1_salon_3_before.jpg) | ![](agent/r2_cam_r_L-1_salon_3_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_banyo_2 | ![](agent/r2_cam_r_L0_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_banyo_2_after.jpg) |
| 2 | cam_r_L0_e_banyo_1 | ![](agent/r2_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_e_banyo_1_after.jpg) |
| 2 | cam_r_L0_e_banyo_2 | ![](agent/r2_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r2_cam_r_L0_e_banyo_2_after.jpg) |
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
| 2 | cam_r_L1_koridor_1 | ![](agent/r2_cam_r_L1_koridor_1_before.jpg) | ![](agent/r2_cam_r_L1_koridor_1_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 2 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 2 | cam_r_L1_teras_1 | ![](agent/r2_cam_r_L1_teras_1_before.jpg) | ![](agent/r2_cam_r_L1_teras_1_after.jpg) |
| 2 | cam_r_L1_teras_2 | ![](agent/r2_cam_r_L1_teras_2_before.jpg) | ![](agent/r2_cam_r_L1_teras_2_after.jpg) |
| 2 | cam_r_L1_teras_3 | ![](agent/r2_cam_r_L1_teras_3_before.jpg) | ![](agent/r2_cam_r_L1_teras_3_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_5 | ![](agent/r2_ext_5_before.jpg) | ![](agent/r2_ext_5_after.jpg) |
| 2 | ext_7 | ![](agent/r2_ext_7_before.jpg) | ![](agent/r2_ext_7_after.jpg) |
| 3 | cam_r_L-1_banyo_1 | ![](agent/r3_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L-1_banyo_1_after.jpg) |
| 3 | cam_r_L-1_banyo_2 | ![](agent/r3_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r3_cam_r_L-1_banyo_2_after.jpg) |
| 3 | cam_r_L-1_koridor_2_1 | ![](agent/r3_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r3_cam_r_L-1_koridor_2_1_after.jpg) |
| 3 | cam_r_L-1_mutfak_1 | ![](agent/r3_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_1_after.jpg) |
| 3 | cam_r_L-1_mutfak_2 | ![](agent/r3_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_2_after.jpg) |
| 3 | cam_r_L-1_mutfak_3 | ![](agent/r3_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_3_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_banyo_1 | ![](agent/r3_cam_r_L0_banyo_1_before.jpg) | ![](agent/r3_cam_r_L0_banyo_1_after.jpg) |
| 3 | cam_r_L0_banyo_2 | ![](agent/r3_cam_r_L0_banyo_2_before.jpg) | ![](agent/r3_cam_r_L0_banyo_2_after.jpg) |
| 3 | cam_r_L0_e_banyo_1 | ![](agent/r3_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r3_cam_r_L0_e_banyo_1_after.jpg) |
| 3 | cam_r_L0_e_banyo_2 | ![](agent/r3_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r3_cam_r_L0_e_banyo_2_after.jpg) |
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
| 4 | cam_r_L-1_koridor_2_1 | ![](agent/r4_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r4_cam_r_L-1_koridor_2_1_after.jpg) |
| 4 | cam_r_L-1_mutfak_1 | ![](agent/r4_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r4_cam_r_L-1_mutfak_1_after.jpg) |
| 4 | cam_r_L-1_mutfak_2 | ![](agent/r4_cam_r_L-1_mutfak_2_before.jpg) | ![](agent/r4_cam_r_L-1_mutfak_2_after.jpg) |
| 4 | cam_r_L-1_mutfak_3 | ![](agent/r4_cam_r_L-1_mutfak_3_before.jpg) | ![](agent/r4_cam_r_L-1_mutfak_3_after.jpg) |
| 4 | cam_r_L-1_salon_1 | ![](agent/r4_cam_r_L-1_salon_1_before.jpg) | ![](agent/r4_cam_r_L-1_salon_1_after.jpg) |
| 4 | cam_r_L-1_salon_2 | ![](agent/r4_cam_r_L-1_salon_2_before.jpg) | ![](agent/r4_cam_r_L-1_salon_2_after.jpg) |
| 4 | cam_r_L-1_salon_3 | ![](agent/r4_cam_r_L-1_salon_3_before.jpg) | ![](agent/r4_cam_r_L-1_salon_3_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_banyo_2 | ![](agent/r4_cam_r_L0_banyo_2_before.jpg) | ![](agent/r4_cam_r_L0_banyo_2_after.jpg) |
| 4 | cam_r_L0_e_banyo_1 | ![](agent/r4_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_1_after.jpg) |
| 4 | cam_r_L0_e_banyo_2 | ![](agent/r4_cam_r_L0_e_banyo_2_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_2_after.jpg) |
| 4 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r4_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 4 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r4_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r4_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 4 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r4_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r4_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 4 | cam_r_L0_koridor_1 | ![](agent/r4_cam_r_L0_koridor_1_before.jpg) | ![](agent/r4_cam_r_L0_koridor_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_1 | ![](agent/r4_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_2 | ![](agent/r4_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_2_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3 | ![](agent/r4_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r4_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r4_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r4_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 4 | cam_r_L1_banyo_1 | ![](agent/r4_cam_r_L1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L1_banyo_1_after.jpg) |
| 4 | cam_r_L1_koridor_1 | ![](agent/r4_cam_r_L1_koridor_1_before.jpg) | ![](agent/r4_cam_r_L1_koridor_1_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 4 | cam_r_L1_teras_1 | ![](agent/r4_cam_r_L1_teras_1_before.jpg) | ![](agent/r4_cam_r_L1_teras_1_after.jpg) |
| 4 | cam_r_L1_teras_2 | ![](agent/r4_cam_r_L1_teras_2_before.jpg) | ![](agent/r4_cam_r_L1_teras_2_after.jpg) |
| 4 | cam_r_L1_teras_3 | ![](agent/r4_cam_r_L1_teras_3_before.jpg) | ![](agent/r4_cam_r_L1_teras_3_after.jpg) |
| 4 | ext_1 | ![](agent/r4_ext_1_before.jpg) | ![](agent/r4_ext_1_after.jpg) |
| 4 | ext_2 | ![](agent/r4_ext_2_before.jpg) | ![](agent/r4_ext_2_after.jpg) |
| 4 | ext_3 | ![](agent/r4_ext_3_before.jpg) | ![](agent/r4_ext_3_after.jpg) |
| 4 | ext_5 | ![](agent/r4_ext_5_before.jpg) | ![](agent/r4_ext_5_after.jpg) |
| 4 | ext_7 | ![](agent/r4_ext_7_before.jpg) | ![](agent/r4_ext_7_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- cam_r_L-1_koridor_2_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L1_koridor_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- final/top_L-1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L-1_plan_4.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_4.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_4.jpg
