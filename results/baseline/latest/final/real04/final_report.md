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
| JSON cross-check findings (Cycles render) | 23 |
| needs_review views | 11 |
| unverified pieces in view (sum over views) | 44 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.83 .. +2.33 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 1: cam_r_L1_banyo_1 |
| window pull | 24 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 8, m5 5, search 23 |
| camera score (min / mean / max) | 2.44 / 3.88 / 4.65 |
| rooms by number of views | 1 with 0, 4 with 1, 3 with 2, 7 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 4.7 min / 6.4 min / 91.2 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 34.2 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 15 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 729.2 MB |
| [real04.glb](3d/real04.glb) | 1652.8 MB |

36 cameras; textures scaled to at most 1024 px (341 scaled) for the download.

## AI decor

152 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 34 rooms; 333 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

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
- drawn-piece check: 16 piece(s) moved beyond the tolerance, 67 locked-rule violation(s)
- AI completion: 5 proposal(s) refused, reverted or not placed (listed per room)
- 1 view(s) blocked: a piece fills the frame or the image is black (listed under Replayed cameras the build changed, blocked views): cam_r_L1_banyo_1 (blocked)

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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.33 | - | search 3.01 | D3 A5 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.33 | - | agent | D2 A3 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.83 | - | agent | D2 A1 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.50 | -3 | search 4.60 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.83 | -3 | search 3.78 | D5 A1 | 0 | yes | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.17 | -1 | search 4.25 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.83 | -4 | search 3.65 | D7 A4 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.83 | -4 | search 3.63 | D11 A5 | 5 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.46 | D11 A6 | 2 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.33 | - | search 3.00 | D3 A5 | 0 | yes | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | agent | D2 A3 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.33 | - | agent | D2 A3 | 0 | yes | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.00 | - | agent | D2 A4 | 1 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -1.17 | - | search 4.61 | D7 A10 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -1.00 | -1 | search 4.47 | D4 A8 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.50 | - | search 3.90 | D4 A2 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.00 | - | agent | D2 A2 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.33 | -4 | search 4.64 | D4 A6 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.67 | -1 | search 4.07 | D5 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 4.37 | D4 A7 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | -1.33 | -1 | search 4.60 | D4 A5 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | -1.33 | -1 | search 4.54 | D5 A3 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | -1.17 | -1 | search 4.55 | D4 A6 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles, blocked | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.00 | - | agent | A1 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.33 | - | agent | D3 A1 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.17 | -2 | search 4.65 | D9 A5 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.17 | -2 | search 4.13 | D7 A3 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 3.99 | D9 A2 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -6.67 | 0 | search 2.47 | D1 A6 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -5.00 | 0 | search 2.44 | D2 A5 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -5.00 | 0 | search 2.45 | D1 A4 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.33 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.83 | 0 | m5 blocked | D6 | 1 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
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
| cam_r_L0_banyo_1 | cycles | cross-check in_json_not_rendered | f_L0_056 | shoe_cabinet | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | visible 0.55, area 0.018; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_banyo_1 | cycles | cross-check misplaced | f_L0_058 | nightstand | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 12455 px; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_e_banyo_1 | cycles | cross-check misplaced | d_L0_002 | door | - | from_documents | deneme1.dwg INSERT:2DDF1/1,INSERT:2DDF1/0,LWPOLYLINE:2DDF5 vector 0.95 | yes | 92 % of its pixels > 0.10 m outside the drawing, 628560 px |
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 71 % of its pixels > 0.10 m outside the drawing, 345167 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 65 % of its pixels > 0.10 m outside the drawing, 17604 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 64 % of its pixels > 0.10 m outside the drawing, 21064 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 64 % of its pixels > 0.10 m outside the drawing, 30810 px |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 24 % of its pixels > 0.10 m outside the drawing, 43606 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 16 % of its pixels > 0.10 m outside the drawing, 5636 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 23 % of its pixels > 0.10 m outside the drawing, 46291 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 15 % of its pixels > 0.10 m outside the drawing, 5723 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 33 % of its pixels > 0.10 m outside the drawing, 43013 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 27 % of its pixels > 0.10 m outside the drawing, 10292 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 72 % of its pixels > 0.10 m outside the drawing, 12346 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 65 % of its pixels > 0.10 m outside the drawing, 10069 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3079 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 2432 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 7116 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1519 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3331 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 52 % of its pixels > 0.10 m outside the drawing, 15703 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12221 px |

## Needs review

- cam_r_L-1_mutfak_2: json cross-check misplaced: d_L-1_003
- cam_r_L0_banyo_1: json cross-check in_json_not_rendered: f_L0_056; json cross-check misplaced: f_L0_058
- cam_r_L0_e_banyo_1: json cross-check misplaced: d_L0_002
- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: d_L0_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: json cross-check misplaced: d_L1_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: json cross-check misplaced: d_L1_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: json cross-check misplaced: d_L1_001
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
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_061, f_L-1_070, f_L-1_071, f_L-1_087
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_071
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_banyo_2: f_L0_013
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_e_yatak_odasi_3: f_L0_023
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

- added f_L1_046: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_047: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_048: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L1_049: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L1_050: ottoman 0.50 x 0.50 (confidence -, rule)
- not placed seating: no free place passed the placer checks (no place passes the checks)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_005, f_L1_006, f_L1_007, f_L1_013, f_L1_017, f_L1_020, f_L1_035, f_L1_036

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): completed (partner r_L1_oyun_aktivite_ve_dinlenme_odasi (twin) not used: 1 of 5 copied pieces fail a check here (floor_lamp: the copy fails wall_contact here); completed itself)

- added f_L1_052: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_053: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_054: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L1_055: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L1_056: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L1_057: ottoman 0.50 x 0.50 (confidence -, rule)
- not placed dining: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_010, f_L1_011, f_L1_014, f_L1_018, f_L1_019, f_L1_037, f_L1_038

### Koridor (r_L1_koridor, hall): completed

- added f_L1_051: shoe_cabinet 0.60 x 0.25 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_027

### Koridor (r_L1_koridor_2, hall): mirrored (decisions of r_L1_koridor (twin), not asked again)

- added f_L1_058: shoe_cabinet 0.60 x 0.25 (confidence -, rule, mirrored from f_L1_051)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_028

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_021, f_L1_025

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_016, f_L1_022, f_L1_026

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 148 ok, 16 failed; 52 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_027 | table_dining (table_dining) | 0.13 | - | - | - |
| f_L-1_042 | chair (chair) | 0.14 | 0.00 | - | - |
| f_L-1_063 | floor_lamp (floor_lamp) | 0.30 | - | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L0_007 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L1_005 | table_dining (table_dining) | 0.32 | - | - | - |
| f_L1_006 | chair (chair) | 0.14 | 90.00 | - | - |
| f_L1_007 | chair (chair) | 0.10 | 0.00 | - | - |
| f_L1_019 | sofa (sofa) | 0.29 | 0.00 | - | - |
| f_L1_032 | armchair (armchair) | 0.30 | 0.00 | - | - |

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
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: ok | no |
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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_banyo_2, cam_r_L-1_koridor_2_1, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 36 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L1_banyo_1, cam_r_L1_koridor_1 | 0 / 17 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

- l-1b-acik-mutfak: interior views: [contact_variant_l-1b-acik-mutfak.jpg](contact_variant_l-1b-acik-mutfak.jpg)

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| deneme1.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 19, block_name 44, group_member 5, inferred 10, level 2, nightstand_symbol 4, none 18, rule 52, same_block 1, twin 9. Recognition questions: 70; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

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
| f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | console_table | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sideboard, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
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
- door height 1,71 m: 2 opening(s) (d_L1_003, d_L1_006)
- door height 2,10 m: 17 opening(s) (d_L-1_001, d_L-1_002, d_L0_001, d_L0_002, d_L0_003, d_L0_004 ...)
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
| area_light | 1 | r_L-1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo |
| area_light | 1 | r_L-1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo_2 |
| area_light | 1 | r_L-1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor |
| area_light | 1 | r_L-1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor_2 |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_e_yatak_odasi: agent: View cam_r_L0_e_yatak_odasi_3 is 1.02 stops over the EV cap; the finding names x2.87 for the room.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_e_yatak_odasi |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven_2 |
| area_light | 1 | r_L0_yatak_odasi_3: agent: Room too dark for cameras (needs x2.39 to x3.0); set to max factor to fix both dark views.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_3 |
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
| bank:sp_004:3 | 1 | sp_004 edge 3: a planted bank of 1:2 up to the ground 2.5 m out (the ground 0.78 m over the level; a landscape architect grades the ground to the terrace where it can, no retaining wall; inferred) | site |
| bath_details | 13 | the bathroom details of the piece (UL114, UL123, UL124: LED strips, a flush plate, towels and toiletries, shower fittings) inside its own box, one mesh | furn_f_L-1_051, furn_f_L-1_052, furn_f_L-1_103 |
| bath_items | 8 | the floating vanity's styling (UL114 B3, UL123 B19): part of its one mesh | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| bedding | 1 | its cover is flat (relief 70 mm, 3 vertices/m2 on top: under 6 mm or 50): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_021 |
| bedding | 2 | its duvet has folds (relief 111 mm) but no pillows (bump 0.49 m < 0.06 m at the head): our pillow set on it, its duvet kept; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_019, dress_f_L0_022 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_008 |
| car | 1 | library car 3dwh_867427c8bc03ecda3fbb809a ('CAR') on the drawn parking spk_001 (perpendicular bay; the documents draw the parking, not a car) | car_spk_001_0 |
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
| door_frame | 18 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1, 1] | d_L-1_001, d_L-1_002, d_L-1_003 |
| door_frame | 1 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1] | d_L0_011 |
| door_handles | 2 | design detail of the documented glazed door (black handles on both faces and 3 hinges); not in the documents | d_L1_003_handle, d_L1_006_handle |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; glazed: door d_L1_003 opens from r_L1_koridor to the open-air r_L1_teras: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_003 |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; glazed: door d_L1_006 opens from r_L1_koridor_2 to the open-air r_L1_teras_2: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_006 |
| door_size | 2 | D5 door sizes by role and family (day door, modern style): a full-height door to the ceiling between day rooms (modern style): 2.85 m high | d_L-1_003, d_L-1_004 |
| door_size | 2 | D5 door sizes by role and family (day door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size); a sloped ceiling over the level: 2.10 m kept | d_L1_001, d_L1_002 |
| door_size | 1 | D5 door sizes by role and family (entrance door, modern style): an entrance at least an entrance door set wide (1.00 m, a pivot door; drawn 0.82 m); a pivot entrance door: 2.40 m high | d_L0_011 |
| door_size | 2 | D5 door sizes by role and family (inside door, modern style): the nearest door set width 0.80 m (drawn 0.78 m: no product size) | d_L0_006, d_L0_010 |
| door_size | 4 | D5 door sizes by role and family (inside door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L0_001, d_L0_004, d_L0_005 |
| door_size | 6 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L-1_001, d_L-1_002, d_L0_002 |
| door_size | 2 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size); a sloped ceiling over the level: 2.10 m kept | d_L1_004, d_L1_005 |
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
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 2 | no height in the JSON; type height for console_table | furn_f_L1_035, furn_f_L1_037 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L-1_058, furn_f_L-1_060, furn_f_L-1_063 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 4 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_035, furn_f_L0_036, furn_f_L0_037 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_013, furn_f_L0_014 |
| height | 1 | no height in the JSON; type height for sideboard | furn_f_L1_062 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 3 | no height in the JSON; type height for tv_unit | furn_f_L-1_101, furn_f_L-1_102, furn_f_L1_060 |
| height | 8 | no height in the JSON; type height for wardrobe | furn_f_L-1_023, furn_f_L-1_024, furn_f_L0_009 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 10 | window height listed as assumed in the building JSON | win_L-1_001, win_L-1_002, win_L-1_003 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door (the door is drawn; the canopy is not) (inferred) | facade |
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
| library_model | 1 | library door 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.82 x 2.10 m (proportions off by 12 %; the documents draw the opening, not its product); the building's one door family; another family than the entrance's; modern look: audited styles ['modern'] name modern; its leaf not seen by the audit's opening question: after the doors it saw; frames in the style's finish | d_L0_012 |
| library_model | 1 | library entrance hssd_4141-3 ('HSSD door 4141-3 (0.91 x 2.13 m)') in 1 panel(s) of 1.00 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one entrance family; modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | d_L0_011 |
| library_model | 14 | library inside door hssd_200-5 ('HSSD door 200-5 (0.81 x 2.20 m)') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_001, d_L-1_002, d_L0_001 |
| library_model | 2 | library inside door hssd_204-7 ('HSSD door 204-7 (0.86 x 2.40 m)') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 6 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L1_001, d_L1_002 |
| library_model | 2 | library inside door hssd_204-7 ('HSSD door 204-7 (0.86 x 2.40 m)') in 1 panel(s) of 0.81 x 2.85 m (proportions off by 26 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_003, d_L-1_004 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 3 panel(s) of 0.72 x 2.55 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_002, win_L0_003 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 4 panel(s) of 0.67 x 2.55 m (proportions off by 7 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_001, win_L0_004 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 8 panel(s) of 0.34 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1 |
| library_model | 2 | library window hssd_3753-30 ('HSSD window 3753-30 (1.18 x 1.70 m)') in 5 panel(s) of 0.83 x 1.20 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L-1_003, win_L-1_004 |
| library_model | 2 | library window hssd_3753-7 ('HSSD window 3753-7 (1.00 x 2.60 m)') in 8 panel(s) of 0.90 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L-1_001, win_L-1_002 |
| light_well:win_L-1_002 | 1 | window sill -2.80 m, ground outside -2.83 m: an open concrete light well 0.8 m deep, 7.59 m wide (no light well drawn) | site |
| light_well:win_L-1_003 | 1 | the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well | site |
| light_well:win_L-1_004 | 1 | the terrace sp_002 at -3.00 m lies under the sill -2.10 m: no light well | site |
| modules | 30 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| parapet | 1 | roof terrace ro_001: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| parapet_height:ro_002 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| passage_lining | 3 | design detail of the documented passage: a lined reveal (jambs and head lining in the trim), no architrave (UL122); not in the documents | o_L0_001_lining, o_L0_002_lining, o_L1_001_lining |
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
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the books dec_L0_009): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the books dec_L0_062): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi_2 |
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_056; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026, above the mirror dec_L-1_055 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_067; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_066 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L-1_koridor: ceiling fixture at the pole of inaccessibility of r_L-1_koridor, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_071); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L-1_koridor_2, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_065); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_091 over the counter f_L-1_001; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_092 over the counter f_L-1_002; 299.1 lm -> 0.785 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_2_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_093 over the counter f_L-1_002; 357.2 lm -> 0.9377 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_3_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/3 of its light under each decor ceiling light of the room (dec_L-1_039); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/3 of its light under each decor ceiling light of the room (dec_L-1_063); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/3 of its light under each decor ceiling light of the room (dec_L-1_064); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_6_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_097 over the counter f_L-1_010; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_098 over the counter f_L-1_011; 355.4 lm -> 0.9331 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_2_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_099 over the counter f_L-1_011; 298.6 lm -> 0.7837 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_3_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/3 of its light under each decor ceiling light of the room (dec_L-1_072); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/3 of its light under each decor ceiling light of the room (dec_L-1_085); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/3 of its light under each decor ceiling light of the room (dec_L-1_086); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_6_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_057); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_058); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_2_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_059); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_3_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027, 1/4 of it under each decor pendant of the row (dec_L-1_060); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_4_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_124); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_125); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_2_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_126); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_3_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038, 1/4 of it under each decor pendant of the row (dec_L-1_127); 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_4_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_036; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003, above the mirror dec_L0_035 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_040; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_039 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_024; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_023 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_025 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_031 is taken by the vase dec_L0_103); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_018); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_033 is taken by the vase dec_L0_110); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_049); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_007 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_060 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_031 on f_L0_057 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_068 on f_L0_058 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_030); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_034); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_001; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_035; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L-1_019, furn_f_L-1_020 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.150 m / 18 drawn risers | furn_f_L0_001, furn_f_L0_002 |
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
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_001, f_L-1_002, f_L-1_004, f_L-1_008 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L-1_003 | splashback_r_L-1_mutfak |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L-1_010, f_L-1_011, f_L-1_013, f_L-1_017 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) win_L-1_004 | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_003 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_004 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_012 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_013 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L-1_mutfak_2 |
| splashback_cut | 1 | the splashback behind f_L-1_067 is cut at the opening(s) win_L-1_003 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak |
| splashback_cut | 1 | the splashback behind f_L-1_068 is cut at the opening(s) win_L-1_004 of its wall (a wall finish never covers an opening): nothing left, the openings cover it | splashback_r_L-1_mutfak_2 |
| splashback_look | 2 | the worktop's stone up the wall: the modern family's stone splashback (K5) | splashback_r_L-1_mutfak, splashback_r_L-1_mutfak_2 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_002 |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_002 (100% of the smaller footprint; slab opening sv_L1_002); read as its upper end, not built as a second flight | f_L1_001 |
| stair_finishes | 4 | the house's style family (H8); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| suspension | 12 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L-1_057_cord, decor_dec_L-1_058_cord, decor_dec_L-1_059_cord |
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
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_001 into r_L-1_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_001 into r_L-1_koridor_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_002 into r_L-1_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_002 into r_L-1_koridor, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_003 into r_L-1_koridor_2, on the latch side, assumed on the side with more free wall (3.56 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_003 into r_L-1_mutfak, on the latch side, assumed on the side with more free wall (3.56 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_mutfak_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_004 into r_L-1_koridor, on the latch side, assumed on the side with more free wall (3.56 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_004 into r_L-1_mutfak_2, on the latch side, assumed on the side with more free wall (3.56 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_mutfak_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_001 into r_L0_e_yatak_odasi, on the latch side, assumed on the side with more free wall (0.44 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_yatak_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_001 into r_L0_koridor, on the latch side, assumed on the side with more free wall (0.26 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_002 into r_L0_e_banyo, on the latch side, assumed on the side with more free wall (0.52 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_003 into r_L0_e_banyo_2, on the latch side, assumed on the side with more free wall (0.40 m against 0.02 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_003 into r_L0_e_yatak_odasi_2, on the latch side, assumed on the side with more free wall (1.67 m against 0.45 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_yatak_odasi_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_004 into r_L0_e_yatak_odasi_2, on the latch side, assumed on the side with more free wall (0.45 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_e_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_004 into r_L0_koridor_2, on the latch side, assumed on the side with more free wall (0.26 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_005 into r_L0_yatak_odasi, on the latch side, assumed on the side with more free wall (4.32 m against 0.04 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_006 into r_L0_yatak_odasi_3, on the latch side, assumed on the side with more free wall (1.03 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_3_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_007 into r_L0_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.31 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_008 into r_L0_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.31 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_009 into r_L0_yatak_odasi_2, on the latch side, assumed on the side with more free wall (4.32 m against 0.04 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_010 into r_L0_yatak_odasi_4, on the latch side, assumed on the side with more free wall (1.03 m against 0.05 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_yatak_odasi_4_01 |
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
| wall_plate | 1 | inferred: a light switch on the wall next to the outside door d_L0_011 (entrance), as beside it the intercom dec_L0_099, 0.08 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_01 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_027 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_028 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_029 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_030 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_04 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_055, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_066, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_035, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_039, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_027, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_031, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (left side) beside its nightstand f_L0_031, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (right side) beside its nightstand f_L0_032, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (left side) beside its nightstand f_L0_034, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (right side) beside its nightstand f_L0_033, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (left side) over its nightstand f_L0_041 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (right side) over its nightstand f_L0_042 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (left side) over its nightstand f_L0_045 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (right side) over its nightstand f_L0_044 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (left side) over its nightstand f_L0_057 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_3_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (right side) beside its desk f_L0_029, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (left side) beside its desk f_L0_028, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (right side) over its nightstand f_L0_058 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_4_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (1.55 m), 0.30 m over the floor | plate_r_L1_koridor_03, plate_r_L1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (1.60 m), 0.30 m over the floor | plate_r_L0_koridor_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (3.26 m), 0.30 m over the floor | plate_r_L-1_koridor_03, plate_r_L-1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (3.63 m), 0.30 m over the floor | plate_r_L0_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.28 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_04 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 1.31 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_06, plate_r_L0_yatak_odasi_4_06 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 1.51 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_06, plate_r_L0_yatak_odasi_2_06 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.72 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.30 m, 0.30 m over the floor | plate_r_L-1_salon_2_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.42 m, 0.30 m over the floor | plate_r_L-1_salon_05 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 2.98 m, 0.30 m over the floor | plate_r_L-1_salon_04, plate_r_L-1_salon_2_04 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 3.63 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_05, plate_r_L0_yatak_odasi_4_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 3.95 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_02 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.33 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_05, plate_r_L0_yatak_odasi_2_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 4.37 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_03 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.87 m, 0.30 m over the floor | plate_r_L-1_salon_03, plate_r_L-1_salon_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 5.53 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_02 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_023, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_02 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_025, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_101 beside it, 0.30 m over the floor | plate_r_L-1_salon_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_102 beside it, 0.30 m over the floor | plate_r_L-1_salon_2_02 |
| wall_plate | 2 | inferred: a socket pair over the worktop f_L-1_002 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_03, plate_r_L-1_mutfak_04 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_003 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_02 |
| wall_plate | 3 | inferred: a socket pair over the worktop f_L-1_010 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_03, plate_r_L-1_mutfak_2_04, plate_r_L-1_mutfak_2_05 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_012 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_02 |
| wet_walls | 1 | the modern family's bathroom (FAMILY_BATH): large-format stone-look porcelain 60 x 120 cm in greige on the walls, floor to ceiling (UL114 B8; the brief names no wet-room tiles) | style |
| winders | 4 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

None.

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_salon (rung None), r_L0_e_yatak_odasi (rung None), r_L0_yatak_odasi (rung None), r_L0_yatak_odasi_3 (rung None), r_L1_oyun_aktivite_ve_dinlenme_odasi (rung None), r_L1_teras (rung None).

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_01bdde06bbd897acf61296f1 [non_commercial], 3dwh_0fe8cd77a0e74202f9f12142 [non_commercial], 3dwh_12309fdb2fb284320ed634a7 [non_commercial], 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_291de1594f740b645143a321 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_58b8165e8b3d3414bf5f13a8 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_878ba8fda4c76a59ebca493e [non_commercial], 3dwh_a4e1395f626c963c2082d2a3 [non_commercial], 3dwh_a5c7a54e4232c509c4e12d8d [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 [non_commercial], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_652536faa9c5028ed8be69780c120af78c141968 [non_commercial], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial], hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial], hssd_a72d7403a0ea8133a89bff0bfc266d443613420a [non_commercial], hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: 3dwh_878ba8fda4c76a59ebca493e [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_652536faa9c5028ed8be69780c120af78c141968 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_878ba8fda4c76a59ebca493e [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: yes
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: 3dwh_a5c7a54e4232c509c4e12d8d [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: yes
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_58b8165e8b3d3414bf5f13a8 [non_commercial], 3dwh_a4e1395f626c963c2082d2a3 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_58b8165e8b3d3414bf5f13a8 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 [non_commercial], hssd_a72d7403a0ea8133a89bff0bfc266d443613420a [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_58b8165e8b3d3414bf5f13a8 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_0e8f7683353124120fc3d0c2c23f128eaa992b11 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: yes
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: yes
- cam_r_L0_e_banyo_2: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_01bdde06bbd897acf61296f1 [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial], hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_01bdde06bbd897acf61296f1 [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L0_koridor_1: commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial])
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_ba5b8da5b7298d1ee5838b5a [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], hssd_7cdeb790eb0a2a35f1bd5a29588c1b251dc0a3e4 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_0c22fc3147a2787e85cedfbf231aa45cdc08e25e [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: yes
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: gen_plant_large_modern_minimal_1_06ccb749 [tool_nc])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_12309fdb2fb284320ed634a7 [non_commercial], 3dwh_291de1594f740b645143a321 [non_commercial], 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_12309fdb2fb284320ed634a7 [non_commercial], 3dwh_291de1594f740b645143a321 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_291de1594f740b645143a321 [non_commercial], 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_8512ac158d0f8579041a1fc2 [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: 3dwh_8512ac158d0f8579041a1fc2 [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_0fe8cd77a0e74202f9f12142 [non_commercial])

## Built below library level (Milestone 13)

64 furniture piece(s) built from a module builder or a parametric family instead of a library model: 7 library gap(s) to close with a real model, 57 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1_103 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L-1_104 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_047 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_e_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_048 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_049 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L1_078 | table_dining | module | table_long | r_L1_teras | balcony | added_by_ai | yes | module family in weather-proof materials (a teak top on brushed steel legs) |
| f_L1_082 | table_dining | module | table_long | r_L1_teras | balcony | added_by_ai | yes | module family in weather-proof materials (a teak top on brushed steel legs) |
| f_L1_091 | table_dining | parametric | parametric:table_dining | r_L1_teras_2 | balcony | added_by_ai | yes | parametric family in weather-proof materials (a teak top on brushed steel legs) |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_1 (6.0 degrees off the sun, sky pull k 3), ext_5 (5.6 degrees off the sun, sky pull k 0).

## Replayed cameras the build changed, blocked views


Blocked views (the final image shows a piece filling the frame, or black):

- cam_r_L1_banyo_1: blocked: its meter found no room surface (no interior block to meter: EV 0 used): the frame is inside or against a piece

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

Assets: textures CC0 x 44; furniture/decor models 3DWH-UNREVIEWED x 46, CC-BY-4.0 x 144, CC-BY-NC-4.0 x 44, CC0 x 1, generated (Infinigen v1.19.0, BSD-3-Clause) x 3, generated (TRELLIS.2-4B, MIT) x 20 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 36 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_116)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_048)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_005)
- "Candle" by deniska40k (https://sketchfab.com/3d-models/c408586d8c1547448c4ff47abb4fb981), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_034)
- "Доработка дно пирожницы h=23 l=75 без рёбер" by Александр (https://sketchfab.com/3d-models/e736a1e7cdcb48a5a4f2ca4100d52d28), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_014, dec_L1_047)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261029-201533-full-20261029T202018Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 50.6 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 111.2 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.5 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.7 min | answers applied |
| fit | ok | 11.9 s | - |
| layout | ok | 55.8 s | - |
| decor_ask | ok | 3.8 s | - |
| photos | reused | 0.2 s | - |
| assets | ok | 2.4 s | - |
| decor | ok | 9.5 s | - |
| agent_apply | ok | 83.7 s | - |
| refit | ok | 118.1 s | - |
| build | ok | 32.0 min | - |
| agent_previews | ok | 7.5 min | 15 view(s) |
| agent | ok | 58.5 min | 4 round(s), 31 finding(s) removed by 97 accepted edit(s) (measured; 183 predicted by the dry re-checks), 15 new, net 16, 269 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 14.1 min | - |
| export | ok | 6.4 min | - |
| controls | ok | 114.0 s | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.2 min | - |
| check | ok | 3.3 min | - |
| combine | ok | 24.5 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 97 edit(s) accepted, 269 rejected, 809 model calls (10783049 tokens), 67.5 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 17369): earlier runs of the appended log are left out (17368 events, 6189 model calls, 535 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 97 / 269 (26 % accepted) |
| rejected by reason | acceptance 54, asset_unusable 34, max_tries 25, memory 24, pin_refused 22 |
| rooms checked by code / vision / planner | 38 / 14 / 29 |
| rooms with fixable critical or major findings visited | 29 of 29 |
| critical before -> after (after: round 4's critics, before its 11 accepted edit(s)) | 18 -> 25 |
| major before -> after (after: round 4's critics, before its 11 accepted edit(s)) | 300 -> 530 |
| agent minutes; first accepted edit after | 56.56; 5.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 24; 155; 103 (53) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 31 measured; 183 predicted (the last round's dry re-checks predicted 32 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 88 new; net -57 |
| edits removing their finding | 16 of 68 |
| plans ok / empty / refused / default | 53 / 43 / 6 / 1 |

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

Score 4.1 / 100 (100 = nothing open): 23 critical, 296 major, 128 minor open. By kind (critical + major): lost 69, no_sense 25, taste 77, detached 9, misread 30, geometry 55, silent 24, other 12, process 6, stale 6, reference_missed 5, untyped 1. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- lost sa_L0_otopark_alani: the documents label a site area 'Otopark alani' and the model does not build it (no outline, no reason)
- lost sa_L0_guneslenme_alani: the documents label a site area 'Güneşlenme alani' and the model does not build it (no outline, no reason)
- lost sa_L0_24m2_havuz: the documents label a site area '24m2 havuz' and the model does not build it (no outline, no reason)
- taste r_L1_banyo: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. This is a failed render, not a view 
- no_sense f_L0_009: wardrobe f_L0_009: 0.17 m free in front of it (f_L0_029 in the way); its door or drawers cannot open (needs 0.50 m to open, 0.50 m to use)
- no_sense f_L0_011: wardrobe f_L0_011: 0.17 m free in front of it (f_L0_028 in the way); its door or drawers cannot open (needs 0.50 m to open, 0.50 m to use)
- no_sense dec_L1_013: decor_dec_L1_013 pokes through the roof (top 5.32 m)
- detached dec_L0_011: cushion dec_L0_011 on bed_double f_L0_007: penetration 0.049 m > 0.03 m
- detached dec_L0_012: cushion dec_L0_012 on bed_double f_L0_007: penetration 0.049 m > 0.03 m
- no_sense f_L-1_019: The staircase has no safety railing or guard on the open side, creating a fall risk.
- taste f_L0_023: The object labeled as a wardrobe (f_L0_023) is rendered as a dark, flat wall panel with a window frame embedded in it, rather than a functional storage unit wit
- no_sense r_L0_koridor: The stair opening on the right side of the corridor lacks a safety railing or guard, creating a fall risk.
- misread f_L1_015: The room makes no sense as a bathroom because none of its fixtures are visible: the washbasin, toilet, and bathtub are all absent from the frame.
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

Library gaps reported by the agent: wall_cabinet (No audited library model of wall_cabinet exists (catalog count 0), so the crude low-poly grey block of f_L-1_093 cannot be swapped to a better model (a:F80).), kitchen_counter (f_L-1_003 is a module-built kitchen run segment whose top sits at 1.18 m over the 0.97 m working height; no library model can replace a module-built run segment, so the M2 height finding stays for the fit (a:F159).), toilet (No audited library toilet model fits the drawn 0.50x0.69 m footprint (only generated models, all refused by the fit rules), so the parametric build stays.), washbasin (No audited library washbasin model fits the drawn 1.00x0.55 m footprint (only generated models, all refused by the fit rules), so the parametric build stays.), tall_cabinet (No audited library tall cabinet fits the 0.40x0.35 m footprint (real models are 0.45-1.4 m wide and fail the fit rules; the one 0.45 m model was audit-removed), so the parametric build stays.), entrance_canopy (a:D3:d_L0_005: reference shows an entrance canopy with overhang and exterior lights; no audited library model exists for it.), door (a:D3:d_L0_007: raw oak door clashes with the cool minimalist bathroom; no audited library model of a matching door style exists.), rug (a:D3:f_L0_043: reference shows a soft rug anchoring the bed; no audited library model of a rug exists.), interior_lighting (a:D3:w_L0_001: reference shows a warm interior glow from the windows; no audited library model of interior lighting exists.), outdoor_styling (a:D3:win_L-1_001: view outside the window is a flat green plane; no audited library model of outdoor planters/seating exists.), outdoor_styling (a:D3:win_L-1_003: view through the window is a flat untextured green plane; no audited library model of a believable outdoor view exists.), toilet (No real library toilet model fits the drawn 0.50 x 0.68 m footprint (only generated models exist and they fail the fit/height rules), so the parametric build stays below library level (P7) and floats +0.200 m (S1).), washbasin (No real library washbasin model fits the drawn 1.00 x 0.55 m footprint (only generated models exist and they fail the fit/height rules), so the build floats +0.384 m (S1).), kitchen_counter (a:F160: f_L-1_012's top is at 1.18 m over its 0.97 m working height, but the library has no kitchen_counter models to swap to, so the wrong-model height cannot be fixed by swap_model.), wardrobe (No audited wardrobe model fits the drawn 3.11x0.60 run (closest candidate 19.8% non-uniform, mean scale 1.20); previous swap rejected as audit pending, so the flat-panel render stays for review.), rug (The reference anchors the bed on a large patterned rug but no rug piece exists in the room and no audited rug model is available to add one; the missing-layer finding stays for review.), wall_cabinet (Catalog has 0 wall_cabinet models; no swap_model target for the crude low-poly block f_L-1_093 (a:F80).), kitchen_counter (Catalog has 0 kitchen_counter models; no swap_model target for the module-built run segment f_L-1_003 whose top sits at 1.18 m (a:F159).), wardrobe (Wardrobe f_L0_023 renders as a flat panel: no audited library model fits the 3.11 m x 0.60 m footprint (previous swap attempts all rejected as audit-pending or audit-removed), so the module build is the best available and the gap is recorded for review.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 18 | 300 | 95 | 29 | 44 | 105 | layout | 31 |
| 2 | 16 | 279 | 98 | 29 | 27 | 88 | layout | 36 |
| 3 | 17 | 271 | 94 | 29 | 15 | 50 | layout | 15 |
| 4 | 25 | 530 | 136 | 80 | 11 | 26 | layout | 17 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A1 | 0 | 0 | 0 | 10 |
| A2 | 0 | 8 | 0 | 0 |
| A6 | 0 | 32 | 0 | 0 |
| AI1 | 0 | 50 | 0 | 20 |
| AI3 | 0 | 4 | 0 | 0 |
| AI5 | 0 | 8 | 0 | 0 |
| C1 | 0 | 0 | 0 | 13 |
| C5 | 0 | 0 | 0 | 3 |
| C7 | 0 | 40 | 0 | 0 |
| D1 | 0 | 2 | 0 | 0 |
| D2 | 4 | 9 | 0 | 0 |
| D3 | 0 | 256 | 37 | 0 |
| F1 | 0 | 0 | 4 | 0 |
| F2 | 0 | 22 | 0 | 0 |
| F3 | 0 | 31 | 0 | 0 |
| F4 | 0 | 71 | 0 | 0 |
| F6 | 0 | 33 | 0 | 0 |
| F8 | 0 | 1 | 0 | 0 |
| F9 | 0 | 34 | 0 | 0 |
| G1 | 0 | 0 | 27 | 0 |
| G10 | 0 | 95 | 0 | 0 |
| G11 | 0 | 48 | 0 | 0 |
| G12 | 0 | 20 | 0 | 0 |
| G13 | 0 | 32 | 0 | 0 |
| G14 | 0 | 0 | 4 | 0 |
| G2 | 0 | 16 | 16 | 0 |
| G3 | 0 | 32 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 48 | 0 | 0 |
| G6 | 0 | 25 | 8 | 0 |
| G8 | 0 | 17 | 8 | 0 |
| G9 | 0 | 1 | 0 | 0 |
| J1 | 0 | 29 | 0 | 92 |
| K1 | 0 | 5 | 0 | 0 |
| K3 | 0 | 32 | 0 | 0 |
| K4 | 0 | 0 | 0 | 5 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 31 | 0 |
| M13 | 0 | 0 | 12 | 0 |
| M14 | 0 | 24 | 0 | 0 |
| M18 | 0 | 8 | 0 | 0 |
| M19 | 13 | 0 | 0 | 0 |
| M2 | 0 | 10 | 0 | 0 |
| M21 | 0 | 5 | 30 | 0 |
| M22 | 0 | 8 | 0 | 0 |
| M23 | 0 | 12 | 8 | 0 |
| M26 | 0 | 0 | 4 | 0 |
| M28 | 0 | 0 | 8 | 0 |
| M30 | 0 | 0 | 11 | 0 |
| NR | 0 | 16 | 0 | 0 |
| P0 | 0 | 34 | 0 | 0 |
| P1 | 0 | 0 | 0 | 5 |
| P2 | 0 | 8 | 0 | 17 |
| P6 | 0 | 4 | 0 | 0 |
| P7 | 0 | 60 | 0 | 0 |
| P9 | 0 | 0 | 0 | 1 |
| Q10 | 0 | 2 | 0 | 0 |
| Q12 | 0 | 3 | 3 | 0 |
| Q13 | 0 | 9 | 1 | 0 |
| Q14 | 0 | 19 | 8 | 0 |
| Q15 | 0 | 0 | 2 | 0 |
| Q3 | 6 | 0 | 0 | 0 |
| Q4 | 0 | 4 | 0 | 0 |
| Q5 | 0 | 2 | 0 | 0 |
| Q7 | 0 | 4 | 3 | 0 |
| Q9 | 0 | 4 | 0 | 0 |
| R3 | 0 | 0 | 32 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S1 | 0 | 64 | 0 | 0 |
| S2 | 0 | 12 | 38 | 0 |
| S5 | 26 | 0 | 37 | 0 |
| V1 | 0 | 29 | 2 | 0 |
| V2 | 0 | 0 | 0 | 1 |
| X2 | 26 | 11 | 8 | 0 |
| X3 | 0 | 3 | 0 | 0 |
| X5 | 0 | 0 | 39 | 0 |
| X6 | 0 | 9 | 0 | 0 |
| camera_blocked | 1 | 0 | 0 | 0 |
| lighting_dark | 0 | 9 | 4 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 17844 | 1 | relayout_room | r_L0_yatak_odasi_3 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The bed_double f_L0_021 has only 0.37 m free along its left side (needs 0.60 m). A model swap was refused because the alternative is lower quality. The room is 14.1 m2, so a re-layout can place the bed with proper clearance. (fixes a:F66) | ![](agent/r1_003_relayout_room_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_004_relayout_room_after_r_L0_yatak_odasi_3.png) |
| 17845 | 1 | relayout_room | r_L0_yatak_odasi_4 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The bed_double f_L0_022 has only 0.37 m free along its right side (needs 0.60 m). A model swap was refused (lower quality), a move was refused (inside room), and another swap was refused (finding persisted). The room is 14.0 m2, so a re-lay (fixes a:F68) | ![](agent/r1_005_relayout_room_before_r_L0_yatak_odasi_4.png) | ![](agent/r1_006_relayout_room_after_r_L0_yatak_odasi_4.png) |
| 17846 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 41.0 -> 48.0 | Argus: The sofa f_L1_020's front zone is blocked by f_L1_017. A model swap was refused (lower quality), a move was refused (score dropped), and another move was refused (finding persisted). The room is 40.5 m2, so a re-layout can place the seating (fixes a:F70) | ![](agent/r1_007_relayout_room_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_008_relayout_room_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 17861 | 1 | set_camera | r_L-1_banyo | agent_override | - | Argus: The camera is too close and too low, cutting off the top of the mirror and the context of the space. It should be moved to a free point with headroom that shows the vanity and surrounding fixtures. (fixes a:F223) | - | - |
| 17862 | 1 | swap_model | f_L-1_070 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The armchair is a bulky, dark brown piece that clashes with the light, minimalist sofa. The tried rotate_piece was refused (plausibility dropped) and swap_model was refused for 3dwh_49c89838e523cdc64ffa7de1 (audit removed). The model hssd_0 (fixes a:F233) | ![](agent/r1_020_swap_model_before_r_L-1_salon.png) | ![](agent/r1_021_swap_model_after_r_L-1_salon.png) |
| 17864 | 1 | swap_model | f_L-1_028 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The dining chairs are a chaotic mix of at least three different models. The piece f_L-1_028 is a chair with model abo_B0856G7YXQ. The model hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 is modern/scandinavian, 0.48 x 0.47 x 0.79 m, which fi (fixes a:F237) | ![](agent/r1_023_swap_model_before_r_L-1_salon.png) | ![](agent/r1_024_swap_model_after_r_L-1_salon.png) |
| 17867 | 1 | set_camera | r_L0_banyo | agent_override | - | Argus: The view is a close-up of a blank wall and vanity corner; it must show the room's layout and the bathtub. (fixes a:F242) | - | - |
| 17868 | 1 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The view is a tight low-angle crop of a corner that fails to show the room as a whole. (fixes a:F243) | - | - |
| 17869 | 1 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The camera is too close and at a low angle, framing only a corner; it must show the basin, shower and toilet coherently. (fixes a:F244) | - | - |
| 17871 | 1 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The black mesh office chair is a corporate item that clashes with the soft, residential style of the bedroom. (fixes a:F248) | ![](agent/r1_027_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r1_028_swap_model_after_r_L0_yatak_odasi.png) |
| 17874 | 1 | set_lighting | r_L0_yatak_odasi_3 | agent_override | - | Room too dark for cameras (needs x2.39 to x3.0); set to max factor to fix both dark views. | - | - |
| 17886 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | 21.0 -> 21.0 | Room is furnished as a living room (sofas, coffee tables, TV unit, dining) though typed 'other'. | ![](agent/r1_084_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_086_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 17908 | 1 | move_piece | f_L-1b_045 | adjusted_by_ai | 0.0 -> 5.0 | Sofa back is 0.59 m off the wall and its front zone is blocked; snapping its back to the free span s3 puts it on the wall with a clear front. | ![](agent/r1_113_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_116_move_piece_after_r_L-1b_salon_2.png) |
| 17911 | 1 | move_piece | f_L-1b_046 | adjusted_by_ai | 0.0 -> 5.0 | Sofa back is 0.59 m off the wall; snap its back onto the back wall to satisfy F3 off-wall check. | ![](agent/r1_117_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_120_move_piece_after_r_L-1b_salon.png) |
| 17912 | 1 | relayout_room | r_L0_yatak_odasi_3 | adjusted_by_ai | 67.0 -> 67.0 | Re-solve the sleeping group with solver candidate 2 to improve bed side clearances and nightstand placement. | ![](agent/r1_119_relayout_room_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_125_relayout_room_after_r_L0_yatak_odasi_3.png) |
| 17914 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Move nightstand f_L0_032 to [7.16, 4.96] to resolve the 0.06 m² overlap with the bed and correct the -0.12 m gap to a valid 0.0 m gap (within the 0.3 m move allowance). | ![](agent/r1_123_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_128_move_piece_after_r_L0_e_yatak_odasi.png) |
| 17921 | 1 | place_group | r_L0_e_yatak_odasi | added_by_ai | 100.0 -> 100.0 | Re-solve the sleeping_double group around the drawn bed anchor to build the missing nightstand on the free left side of the head (1.13 m free). | ![](agent/r1_137_place_group_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_141_place_group_after_r_L0_e_yatak_odasi.png) |
| 17925 | 1 | swap_model | f_L-1_031 | adjusted_by_ai | 30.0 -> 30.0 | Dining chairs are a chaotic mix of models; give f_L-1_031 the same model as f_L-1_028 to unify the set (a:F237, a:F349). | ![](agent/r1_140_swap_model_before_r_L-1_salon.png) | ![](agent/r1_144_swap_model_after_r_L-1_salon.png) |
| 17928 | 1 | swap_model | f_L-1_071 | adjusted_by_ai | 30.0 -> 30.0 | Give f_L-1_071 the same light armchair model as f_L-1_070 so the pair matches the drawing and the seating set (a:F353). | ![](agent/r1_145_swap_model_before_r_L-1_salon.png) | ![](agent/r1_147_swap_model_after_r_L-1_salon.png) |
| 17934 | 1 | swap_model | f_L-1_073 | adjusted_by_ai | 30.0 -> 30.0 | The 0.8x0.8 table differs from the drawn 0.559x0.559; the 0.84x0.84 Chinese Tea Table is the closest real size and a japandi/minimal style that fits the room (a:F355). | ![](agent/r1_150_swap_model_before_r_L-1_salon.png) | ![](agent/r1_152_swap_model_after_r_L-1_salon.png) |
| 17942 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift nightstand away from bed edge to clear the 0.06 m² overlap and satisfy the ≤ 0.30 m gap requirement. | ![](agent/r1_156_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_158_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 17950 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Relayout the balcony group with the table_2_chairs_plant option to add the missing potted_plant and complete the outdoor set to match the twin balcony. | ![](agent/r1_161_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_167_relayout_room_after_r_L1_teras_2.png) |
| 17952 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 90.0 -> 100.0 | Candidate 2 re-solves the balcony group with the plant anchored near the seating, fixing the floating plant and completing the terrace set. | ![](agent/r1_163_relayout_room_before_r_L1_teras.png) | ![](agent/r1_169_relayout_room_after_r_L1_teras.png) |
| 17955 | 1 | rotate_piece | f_L-1b_041 | adjusted_by_ai | 5.0 -> 5.0 | Sofa f_L-1b_041 had no front; the warning names 270° (towards its partner into the open floor) as the correct direction. | ![](agent/r1_166_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_168_rotate_piece_after_r_L-1b_salon_2.png) |
| 17957 | 1 | report_library_gap | f_L-1_093 | library_gap | - | No audited library model of wall_cabinet exists (catalog count 0), so the crude low-poly grey block of f_L-1_093 cannot be swapped to a better model (a:F80). | - | - |
| 17960 | 1 | report_library_gap | f_L-1_003 | library_gap | - | f_L-1_003 is a module-built kitchen run segment whose top sits at 1.18 m over the 0.97 m working height; no library model can replace a module-built run segment, so the M2 height finding stays for the fit (a:F159). | - | - |
| 17970 | 1 | remove_piece | f_L1_063 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet pokes through the sloped roof (top 4.75 m) and stands where the ceiling is only 0.82 m; not drawn and not required, so removal clears both X2 findings. | ![](agent/r1_179_remove_piece_before_r_L1_banyo.png) | ![](agent/r1_181_remove_piece_after_r_L1_banyo.png) |
| 17971 | 1 | remove_piece | f_L1_064 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet pokes through the roof (top 4.75 m) and stands where the sloped ceiling is only 0.82 m high; it is not drawn and cannot be placed validly, so it is removed. | ![](agent/r1_180_remove_piece_before_r_L1_banyo_2.png) | ![](agent/r1_182_remove_piece_after_r_L1_banyo_2.png) |
| 17976 | 1 | set_lighting | r_L0_banyo | agent_override | - | Both interior views are 0.37-0.43 stops over the EV cap; the finding prescribes x1.9 on the room to cover the views' needs plus headroom. | - | - |
| 18010 | 1 | report_library_gap | f_L-1_051 | library_gap | - | No audited library toilet model fits the drawn 0.50x0.69 m footprint (only generated models, all refused by the fit rules), so the parametric build stays. | - | - |
| 18011 | 1 | report_library_gap | f_L-1_026 | library_gap | - | No audited library washbasin model fits the drawn 1.00x0.55 m footprint (only generated models, all refused by the fit rules), so the parametric build stays. | - | - |
| 18012 | 1 | report_library_gap | f_L-1_103 | library_gap | - | No audited library tall cabinet fits the 0.40x0.35 m footprint (real models are 0.45-1.4 m wide and fail the fit rules; the one 0.45 m model was audit-removed), so the parametric build stays. | - | - |
| 18016 | 1 | report_library_gap | d_L0_005 | library_gap | - | a:D3:d_L0_005: reference shows an entrance canopy with overhang and exterior lights; no audited library model exists for it. | - | - |
| 18017 | 1 | report_library_gap | d_L0_007 | library_gap | - | a:D3:d_L0_007: raw oak door clashes with the cool minimalist bathroom; no audited library model of a matching door style exists. | - | - |
| 18018 | 1 | report_library_gap | f_L0_043 | library_gap | - | a:D3:f_L0_043: reference shows a soft rug anchoring the bed; no audited library model of a rug exists. | - | - |
| 18019 | 1 | report_library_gap | w_L0_001 | library_gap | - | a:D3:w_L0_001: reference shows a warm interior glow from the windows; no audited library model of interior lighting exists. | - | - |
| 18020 | 1 | report_library_gap | win_L-1_001 | library_gap | - | a:D3:win_L-1_001: view outside the window is a flat green plane; no audited library model of outdoor planters/seating exists. | - | - |
| 18021 | 1 | report_library_gap | win_L-1_003 | library_gap | - | a:D3:win_L-1_003: view through the window is a flat untextured green plane; no audited library model of a believable outdoor view exists. | - | - |
| 18027 | 1 | set_lighting | r_L0_koridor | agent_override | - | View cam_r_L0_koridor_1 is 0.33 stops over the EV cap; the finding names x1.78 on the room to bring exposure within limits. | - | - |
| 18029 | 1 | report_library_gap | f_L0_016 | library_gap | - | No real library toilet model fits the drawn 0.50 x 0.68 m footprint (only generated models exist and they fail the fit/height rules), so the parametric build stays below library level (P7) and floats +0.200 m (S1). | - | - |
| 18030 | 1 | report_library_gap | f_L0_004 | library_gap | - | No real library washbasin model fits the drawn 1.00 x 0.55 m footprint (only generated models exist and they fail the fit/height rules), so the build floats +0.384 m (S1). | - | - |
| 18043 | 1 | report_library_gap | f_L-1_012 | library_gap | - | a:F160: f_L-1_012's top is at 1.18 m over its 0.97 m working height, but the library has no kitchen_counter models to swap to, so the wrong-model height cannot be fixed by swap_model. | - | - |
| 18048 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | Room too dark for cam_r_L0_e_banyo_1 (needs +4.03 EV vs +3.00 cap); finding names factor x2.88. | - | - |
| 18050 | 1 | swap_model | f_L-1_094 | added_by_ai | 100.0 -> 100.0 | Replace the generic blocky grey shoe cabinet with a minimal/modern extending shoe rack (0.62x0.30x0.45, matching the 0.6x0.3 footprint) to fix the placeholder look (a:F406). | ![](agent/r1_213_swap_model_before_r_L-1_koridor_2.png) | ![](agent/r1_214_swap_model_after_r_L-1_koridor_2.png) |
| 18550 | 2 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The black high-back office chair is a corporate piece that clashes with the light wood, blue and neutral palette of the bedroom. (fixes a:F249) | ![](agent/r2_001_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_002_swap_model_after_r_L0_yatak_odasi_3.png) |
| 18552 | 2 | set_camera | r_L1_banyo | agent_override | - | Argus: The render is a close-up crop that fails to show the room's layout or the other fixtures (bathtub, toilet). (fixes a:F255) | - | - |
| 18553 | 2 | set_camera | r_L1_koridor | agent_override | - | Argus: The view is a tight corner showing a wall, the stair opening and a plant; the hall's main group and doors are not in frame. The earlier set_camera was refused only because it did not name the finding; naming F258 and giving the pieces to sh (fixes a:F258) | - | - |
| 18554 | 2 | swap_model | f_L1_023 | adjusted_by_ai | 48.0 -> 48.0 | Argus: The coffee table is a generic block that clashes with the modern dining set. The current model hssd_7025cd14a948f491902ef12724f0fe6e4ce672af is the one to replace; abo_B07K7M4YT4 (1.10 x 0.69 x 0.44 m, minimal/modern/scandinavian) fits the  (fixes a:F261) | ![](agent/r2_004_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_005_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 18555 | 2 | swap_model | f_L1_005 | adjusted_by_ai | 48.0 -> 48.0 | Argus: The dining set is a stark, modern piece that feels out of place in the otherwise neutral living area. The current model hssd_e9393fb84e42e59d93ba261275daf119df0cde2e is the one to replace; abo_B07ML7P94G (0.75 x 0.75 x 0.74 m, scandinavian/ (fixes a:F263) | ![](agent/r2_006_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_007_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 18556 | 2 | set_material | floor | agent_override | - | Argus: The balcony floor is a flat, untextured grey material with visible construction seams. The refused relayout, set_camera and place_group edits do not address the material; the fix is to set the floor look to a warm decking finish. (fixes a:F265) | - | - |
| 18560 | 2 | swap_model | f_L-1_069 | adjusted_by_ai | 30.0 -> 30.0 | Argus: A 0.12 m offset and a size mismatch are outside the 0.05 m tolerance; swapping to a model with a closer footprint reduces the offset and improves the match to the drawing. (fixes a:F351) | ![](agent/r2_010_swap_model_before_r_L-1_salon_2.png) | ![](agent/r2_011_swap_model_after_r_L-1_salon_2.png) |
| 18564 | 2 | swap_model | f_L-1_073 | adjusted_by_ai | 30.0 -> 30.0 | Argus: Drawn 0.559 x 0.559 m vs a 0.80 x 0.80 m model; the move was refused by drawn_lock (0.80 m > 0.3 m), so the oversized model is the cause and a smaller model (0.79 x 0.79) is the fix. (fixes a:F355) | ![](agent/r2_015_swap_model_before_r_L-1_salon.png) | ![](agent/r2_016_swap_model_after_r_L-1_salon.png) |
| 18565 | 2 | swap_model | f_L-1_074 | adjusted_by_ai | 30.0 -> 30.0 | Argus: Drawn 0.559 x 0.559 m vs a 0.80 x 0.80 m model; moves were refused (overlap with the armchair), so the oversized model is the cause and a smaller model is the fix. (fixes a:F356) | ![](agent/r2_017_swap_model_before_r_L-1_salon_2.png) | ![](agent/r2_018_swap_model_after_r_L-1_salon_2.png) |
| 18577 | 2 | set_material | floor | agent_override | - | Argus: The finding is a finish gap, not a layout one: the room's wood floor is laid in plain planks. Setting the floor look to a herringbone parquet satisfies the professional bar (UL106) for this room. (fixes a:F401) | - | - |
| 18579 | 2 | swap_model | f_L-1_049 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The grey armchair clashes with the sofa. Swapping to a modern/neutral armchair of a similar footprint (0.93 x 0.84 m) makes the seating group cohesive. (fixes a:F410) | ![](agent/r2_028_swap_model_before_r_L-1_salon.png) | ![](agent/r2_029_swap_model_after_r_L-1_salon.png) |
| 18594 | 2 | retype_piece | f_L1_035 | adjusted_by_ai | 48.0 -> 51.0 | Retype the drawn bench to a console table, which fits its 1.40 x 0.45 m footprint and a living room, resolving F1/G14. | ![](agent/r2_099_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_108_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 18602 | 2 | retype_piece | f_L-1b_042 | adjusted_by_ai | 5.0 -> 25.0 | c:F2:f_L-1b_042: the 0.90 x 2.13 m footprint is a chaise, not a sofa turned 90°; retype to the type that fits its size and the living room | ![](agent/r2_126_retype_piece_before_r_L-1b_salon.png) | ![](agent/r2_131_retype_piece_after_r_L-1b_salon.png) |
| 18624 | 2 | move_piece | f_L-1_027 | adjusted_by_ai | 30.0 -> 30.0 | Nudge the dining table away from chairs f_L-1_028 and f_L-1_031 to clear the 0.038/0.039 m cuts (c:S2:f_L-1_027, c:S2:f_L-1_027#2). | ![](agent/r2_149_move_piece_before_r_L-1_salon.png) | ![](agent/r2_151_move_piece_after_r_L-1_salon.png) |
| 18626 | 2 | set_lighting | r_L0_e_yatak_odasi | agent_override | - | View cam_r_L0_e_yatak_odasi_3 is 1.02 stops over the EV cap; the finding names x2.87 for the room. | - | - |
| 18630 | 2 | report_library_gap | f_L0_023 | library_gap | - | No audited wardrobe model fits the drawn 3.11x0.60 run (closest candidate 19.8% non-uniform, mean scale 1.20); previous swap rejected as audit pending, so the flat-panel render stays for review. | - | - |
| 18634 | 2 | swap_model | f_L0_007 | adjusted_by_ai | 100.0 -> 100.0 | Replace the flat white slab bed with a modern upholstered bed that carries pillows, duvet and throw, addressing the missing bedding layers (D3) and the missing throw (M30). | ![](agent/r2_153_swap_model_before_r_L0_e_yatak_odasi.png) | ![](agent/r2_155_swap_model_after_r_L0_e_yatak_odasi.png) |
| 18635 | 2 | retype_piece | f_L1_037 | adjusted_by_ai | 21.0 -> 24.0 | Bench f_L1_037 is not a piece of a living room; retype it to a console_table which fits its 1.4 x 0.45 m size and the living room zone. | ![](agent/r2_154_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_157_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 18641 | 2 | report_library_gap | report_library_gap | library_gap | - | The reference anchors the bed on a large patterned rug but no rug piece exists in the room and no audited rug model is available to add one; the missing-layer finding stays for review. | - | - |
| 18643 | 2 | report_library_gap | f_L-1_093 | library_gap | - | Catalog has 0 wall_cabinet models; no swap_model target for the crude low-poly block f_L-1_093 (a:F80). | - | - |
| 18644 | 2 | report_library_gap | f_L-1_003 | library_gap | - | Catalog has 0 kitchen_counter models; no swap_model target for the module-built run segment f_L-1_003 whose top sits at 1.18 m (a:F159). | - | - |
| 18647 | 2 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Relayout the balcony set with the solver candidate so the table_2_chairs_plant option is complete with its potted plant, matching the twin balcony. | ![](agent/r2_159_relayout_room_before_r_L1_teras_2.png) | ![](agent/r2_160_relayout_room_after_r_L1_teras_2.png) |
| 18661 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the balcony with candidate 3 to build the full terrace set (table + 2 chairs + plant) as one group, fixing the missing-member finding a:N101. | ![](agent/r2_161_relayout_room_before_r_L1_teras.png) | ![](agent/r2_165_relayout_room_after_r_L1_teras.png) |
| 18664 | 2 | set_lighting | r_L-1_banyo | agent_override | - | cam_r_L-1_banyo_2 is 0.24 stops over the EV cap; the finding names x1.67 for the room to bring incident light within the cap. | - | - |
| 18674 | 2 | swap_model | f_L0_030 | adjusted_by_ai | 70.0 -> 70.0 | Swap plain white boxy desk for a light brown oak-effect writing desk with door and drawer to add warmth and detail. | ![](agent/r2_169_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_174_swap_model_after_r_L0_yatak_odasi.png) |
| 18710 | 2 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Fixes a:F247 (D3): adds the missing place to sit (bench/stool) in the hall per the reference; candidate 1 is the recommended highest-score layout. | ![](agent/r2_190_relayout_room_before_r_L0_koridor.png) | ![](agent/r2_191_relayout_room_after_r_L0_koridor.png) |
| 18732 | 2 | swap_model | f_L-1_094 | added_by_ai | 100.0 -> 100.0 | Replace the generic blocky grey shoe cabinet with a modern minimal shoe cubby for a cohesive, stylish entrance. | ![](agent/r2_205_swap_model_before_r_L-1_koridor_2.png) | ![](agent/r2_206_swap_model_after_r_L-1_koridor_2.png) |
| 19232 | 3 | swap_model | f_L0_030 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The plain white boxy desk gives an office feel. Swapping to a minimal/modern/scandinavian desk of the same footprint (1.45 x 0.69 m) adds warmth and detail. (fixes a:F411) | ![](agent/r3_001_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r3_002_swap_model_after_r_L0_yatak_odasi.png) |
| 19233 | 3 | set_camera | r_L-1_koridor_2 | agent_override | - | Argus: The camera is inside a proxy; moving it to a free point that shows the room's key pieces fixes the view. (fixes a:F489) | - | - |
| 19239 | 3 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The balcony (19.7 m2) has only a chair and a dining table; the drawn terrace set is incomplete (no seating pair, no plant on this unit). (fixes a:N101) | ![](agent/r3_004_place_group_before_r_L1_teras.png) | ![](agent/r3_005_place_group_after_r_L1_teras.png) |
| 19240 | 3 | place_group | r_L1_teras_2 | added_by_ai | 100.0 -> 100.0 | Argus: Twin balcony with only a chair and a dining table; incomplete outdoor set. (fixes a:N102) | ![](agent/r3_006_place_group_before_r_L1_teras_2.png) | ![](agent/r3_007_place_group_after_r_L1_teras_2.png) |
| 19268 | 3 | move_piece | f_L-1_065 | adjusted_by_ai | 30.0 -> 30.0 | Move floor_lamp f_L-1_065 away from window win_L-1_002 to clear the blocked opening (G12). | ![](agent/r3_080_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_082_move_piece_after_r_L-1_salon_2.png) |
| 19274 | 3 | move_piece | f_L1_019 | adjusted_by_ai | 24.0 -> 34.0 | Sofa f_L1_019's free zone in front is blocked by f_L1_018; shift it 0.29 m toward the north wall to open the clearance. | ![](agent/r3_087_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_090_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 19278 | 3 | move_piece | f_L-1_063 | adjusted_by_ai | 30.0 -> 30.0 | Move the floor lamp 0.3 m away from the window wall so it no longer blocks window win_L-1_001 (G12). | ![](agent/r3_091_move_piece_before_r_L-1_salon.png) | ![](agent/r3_096_move_piece_after_r_L-1_salon.png) |
| 19283 | 3 | move_piece | f_L-1_042 | adjusted_by_ai | 30.0 -> 30.0 | Move chair f_L-1_042 slightly to resolve the 0.034 m cut with table_dining f_L-1_038 (S2). | ![](agent/r3_097_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_099_move_piece_after_r_L-1_salon_2.png) |
| 19284 | 3 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 5.0 -> 35.0 | c:F4:f_L-1b_053, a:F477, c:G3:f_L-1b_053: armchair faces 180° (towards f_L-1b_054); turn to 90° to face the sofa f_L-1b_041 | ![](agent/r3_098_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_102_rotate_piece_after_r_L-1b_salon_2.png) |
| 19303 | 3 | move_piece | f_L1_032 | adjusted_by_ai | 34.0 -> 44.0 | Armchair f_L1_032 is 2.73 m from the coffee table f_L1_024 (needs ≤ 2.50 m); shift it 0.3 m toward the table to close the gap. | ![](agent/r3_107_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_117_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 19307 | 3 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi | added_by_ai | 51.0 -> 61.0 | re-solve the dining group around the drawn table so chair f_L1_007 gets the 0.81 m clearance behind it | ![](agent/r3_115_place_group_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_119_place_group_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 19326 | 3 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the balcony group so the set is complete with a potted plant, matching the twin balcony (a:N97, a:N102). | ![](agent/r3_132_relayout_room_before_r_L1_teras_2.png) | ![](agent/r3_133_relayout_room_after_r_L1_teras_2.png) |
| 19331 | 3 | relayout_room | r_L0_yatak_odasi_4 | adjusted_by_ai | 67.0 -> 67.0 | Try solver candidate 2 to reposition the desk and create wardrobe clearance | ![](agent/r3_136_relayout_room_before_r_L0_yatak_odasi_4.png) | ![](agent/r3_137_relayout_room_after_r_L0_yatak_odasi_4.png) |
| 19337 | 3 | set_camera | r_L1_banyo | agent_override | - | Move the blocked camera to a free point with headroom so the lens clears the surface 0.066 m away, keeping the bathroom fixtures in view. | - | - |
| 19377 | 3 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Fixes a:F247 (D3): candidate 2 re-solves the hall layout to add the missing place to sit (bench/stool) that the reference hall anchors the wall with. | ![](agent/r3_153_relayout_room_before_r_L0_koridor.png) | ![](agent/r3_154_relayout_room_after_r_L0_koridor.png) |
| 20225 | 4 | relayout_room | r_L0_yatak_odasi_3 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The bed has only 0.37 m on its left side (needs 0.60 m); individual moves were refused because they worsened headboard or other clearance findings, so a full room re-layout is needed. (fixes a:F67) | ![](agent/r4_003_relayout_room_before_r_L0_yatak_odasi_3.png) | ![](agent/r4_004_relayout_room_after_r_L0_yatak_odasi_3.png) |
| 20226 | 4 | relayout_room | r_L0_yatak_odasi_4 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The bed has only 0.37 m on its right side (needs 0.60 m); a room re-layout is the appropriate fix. (fixes a:F69) | ![](agent/r4_005_relayout_room_before_r_L0_yatak_odasi_4.png) | ![](agent/r4_006_relayout_room_after_r_L0_yatak_odasi_4.png) |
| 20229 | 4 | set_camera | r_L0_koridor | agent_override | - | Argus: The stair fills r_L0_merdiven so its only camera point is inside the stair; the hall (r_L0_koridor) is the correct vantage. Point the hall camera at the stair. (fixes a:F107) | - | - |
| 20238 | 4 | swap_model | f_L1_078 | added_by_ai | 100.0 -> 100.0 | Argus: The table f_L1_078 is a heavy, indoor-style dining table. It is not appropriate for an outdoor terrace. The abo_B07ML7P94G model is a lighter, scandinavian/japandi/minimal/modern/rustic table that is more suitable for outdoor use. (fixes a:F176) | ![](agent/r4_012_swap_model_before_r_L1_teras.png) | ![](agent/r4_013_swap_model_after_r_L1_teras.png) |
| 20242 | 4 | swap_model | f_L0_053 | added_by_ai | 100.0 -> 100.0 | Argus: The dark, heavy wood bench clashes with the light, upholstered bed and light-wood nightstand; swapping to a japandi/modern minimal bench of the same footprint (1.20 x 0.40 m) matches the room's style. (fixes a:F274) | ![](agent/r4_016_swap_model_before_r_L0_e_yatak_odasi.png) | ![](agent/r4_017_swap_model_after_r_L0_e_yatak_odasi.png) |
| 20245 | 4 | set_camera | r_L1_banyo | agent_override | - | Argus: The render is a completely black, empty frame showing no architecture, light, or furniture; the camera must be moved to a free point with headroom that shows the bathroom fixtures. (fixes a:F288) | - | - |
| 20246 | 4 | set_camera | r_L1_koridor | agent_override | - | Argus: The judge says the camera is pressed against a wall showing an empty corner; re-posing it to show the hall's openings and furniture fixes the view. (fixes a:F289) | - | - |
| 20250 | 4 | set_exterior | exterior:ground,site | agent_override | - | Argus: The world around the balcony is a grey-box placeholder with flat green field and low-poly trees; setting proper ground and site items fixes it. (fixes a:F299) | - | - |
| 20251 | 4 | swap_model | f_L1_081 | added_by_ai | 100.0 -> 100.0 | Argus: The current potted plant is a crude low-poly clump; swapping to a more realistic model fixes it. (fixes a:F301) | ![](agent/r4_023_swap_model_before_r_L1_teras.png) | ![](agent/r4_024_swap_model_after_r_L1_teras.png) |
| 20255 | 4 | set_camera | r_L1_koridor | agent_override | - | The view is blocked by the wardrobe panel on the left; re-aim to show the stair and the open corridor so the framing shows the room's potential. | - | - |
| 20261 | 4 | report_library_gap | f_L0_023 | library_gap | - | Wardrobe f_L0_023 renders as a flat panel: no audited library model fits the 3.11 m x 0.60 m footprint (previous swap attempts all rejected as audit-pending or audit-removed), so the module build is the best available and the gap is recorded for review. | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 17842 | 1 | swap_model | f_L0_023 | asset_unusable: 3dwh_75dde6e0870fc3f2c6c9e738 is not used: audit pending | Argus: The wardrobe is rendered as a dark, flat wall panel with a window frame, not a functional storage unit. The tried_and_refused list shows that 3dwh_e41345920f4dce2514160e34 is 'audit pending', abo_B015IPNVFW is 'audit removed', and hssd_7094 (fixes a:F21) |
| 17843 | 1 | fix_fixture | f_L0_014 | fixture_size: f_L0_014: the drawn 0.60 x 1.40 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The drawn 0.60 x 1.40 m shower is outside the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m); the code already refused a model swap and a rotate, so the drawn size itself is the error. The room is 4.0 m2, so a 0.70 x 1.20 m shower (fixes a:F65) |
| 17847 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Argus: The sofa f_L1_019's front zone is blocked by f_L1_018. A move was refused (score dropped). The room is 40.5 m2, so a re-layout can place the seating group with a clear front zone. (fixes a:F74) |
| 17848 | 1 | set_camera | r_L0_koridor | show: no free camera point of r_L0_koridor shows stair (stair not in r_L0_koridor: name its pieces, doors or windows) | Argus: The stair room r_L0_merdiven has no camera because the stair fills the room; the adjacent hall r_L0_koridor has a camera (cam_r_L0_koridor_1) that can be set to show the stair, satisfying the requirement that the hall shows the stair core. (fixes a:F93) |
| 17849 | 1 | retype_piece | f_L-1_085 | f_L-1_001: no_overlap, f_L-1_085: inside_room, f_L-1_085: no_overlap, score: plausibility 77 -> 67 (F9 f_L-1_085: floor_lamp f_L-1_085 overlaps kitchen_counter f_L-1_001 by 0.06 m²) | Argus: The 0.30 x 0.20 m piece in r_L-1_mutfak is drawn but unbuilt; the code's own size/room table gives floor_lamp (sideboard was refused as not a candidate), so it should be typed floor_lamp and built. (fixes a:F103) |
| 17850 | 1 | retype_piece | f_L-1_086 | f_L-1_010: no_overlap, f_L-1_086: inside_room, f_L-1_086: no_overlap, score: plausibility 77 -> 67 (F9 f_L-1_086: floor_lamp f_L-1_086 overlaps kitchen_counter f_L-1_010 by 0.06 m²) | Argus: The 0.30 x 0.20 m piece in r_L-1_mutfak_2 is drawn but unbuilt; the code's own size/room table gives floor_lamp, so it should be typed floor_lamp and built. (fixes a:F104) |
| 17851 | 1 | fix_fixture | f_L0_026 | fixture_size: f_L0_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The 1.83 m tub leaves only 0.28 m in front of a 5.0 m2 bathroom; a real 1.50 m tub fits the bay and restores the 0.53 m clearance. The size fix was refused only because 1.83 m is within 30% of the range, but the clearance proves the drawn l (fixes a:F145) |
| 17852 | 1 | fix_fixture | f_L1_021 | fixture_size: f_L1_021: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m wide toilet sits 0.33 m from the wall on its right; a 0.40 m real toilet with a code reposition restores the 0.38 m centre clearance. (fixes a:F146) |
| 17853 | 1 | fix_fixture | f_L1_025 | fixture_size: f_L1_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 1.83 m tub in the 5.0 m2 r_L1_banyo with 0.28 m in front; a 1.50 m tub restores the 0.53 m clearance. (fixes a:F147) |
| 17854 | 1 | fix_fixture | f_L1_022 | fixture_size: f_L1_022: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m toilet in r_L1_banyo_2 is 0.33 m from the wall on its left; a 0.40 m real toilet with a code reposition restores the 0.38 m centre clearance. (fixes a:F148) |
| 17855 | 1 | fix_fixture | f_L1_026 | fixture_size: f_L1_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: Same 1.83 m tub in r_L1_banyo_2 with 0.28 m in front; a 1.50 m tub restores the 0.53 m clearance. (fixes a:F149) |
| 17856 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | Argus: The room is labelled and furnished as a living room; its 'other' type is a misread. The earlier refusal was a score drop from a different finding (a bedroom), not a rejection of living. (fixes a:F150) |
| 17857 | 1 | set_room_type | r_L1_koridor | no_change: r_L1_koridor is already a hall | Argus: The room is labelled 'hall' and holds a wardrobe and shoe cabinet; 'stair' is a misread. It is already hall, so this confirms the correct type. (fixes a:F151) |
| 17858 | 1 | set_room_type | r_L1_koridor_2 | no_change: r_L1_koridor_2 is already a hall | Argus: The room is labelled 'stair' but holds a shoe cabinet and wardrobe; it is a hall with a stair. It is already hall, so this confirms the correct type. (fixes a:F152) |
| 17859 | 1 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 0.29 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No camera shows the +y entrance facade; a square-on exterior view is added. (fixes a:F157) |
| 17860 | 1 | set_camera | r_L-1_banyo | show: none of the 8 best poses of r_L-1_banyo that show f_L-1_056, f_L-1_051, f_L-1_026 passes the camera checks: duplicate: cam_r_L-1_banyo_1 would show the view cam_r_L-1_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_banyo, or remove one of the two views | Argus: The camera is a tight, low-angle crop of a corner that shows almost nothing of the room. It should be moved to a free point with headroom that shows the main bathroom fixtures. (fixes a:F221) |
| 17863 | 1 | swap_model | f_L-1_053 | asset_unusable: 3dwh_def9a8f7409863460c32b9d9 is not used: audit removed | Argus: The sofa is a crude, blocky model with flat, untextured surfaces. The tried swap_model was refused for 3dwh_e5f77d70d0615bd56772bf1f (audit removed). The model 3dwh_def9a8f7409863460c32b9d9 is modern/scandinavian, 4.30 x 1.68 x 1.44 m, whic (fixes a:F234) |
| 17865 | 1 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_018, f_L0_003, f_L0_025 passes the camera checks: duplicate: cam_r_L0_banyo_1 would show the view cam_r_L0_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views | Argus: The camera is too close and at a low angle, cropping the mirror and the top of the door. The tried set_camera was refused because it did not name the finding it fixes. This set_camera names the finding (F239, target r_L0_banyo) and shows th (fixes a:F239) |
| 17866 | 1 | swap_model | f_L0_003 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The current model (industrial/modern, 1.07 m tall) clashes with the clean concrete basin; the minimal/modern 0.96x0.50x0.18 m model fits the set and the room. (fixes a:F241) |
| 17870 | 1 | place_group | r_L0_koridor | no_change: r_L0_koridor already has its entrance r_L0_koridor.entrance (anchor None, members f_L0_039): nothing missing, never a second set | Argus: The corridor is missing a place to sit (bench or stool) that the reference hall anchors the wall with. (fixes a:F247) |
| 17875 | 1 | swap_model | f_L0_030 | acceptance: pin_refused: f_L0_030: abo_B07GF5DCK2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the plain white boxy desk with a warm mid-century wood desk to match the residential style (a:F411). |
| 17876 | 1 | swap_model | f_L0_041 | acceptance: pin_refused: f_L0_041: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric-mesh nightstand with a library scandinavian side table (a:F383). |
| 17878 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric-mesh nightstand with a library scandinavian side table (a:F384). |
| 17880 | 1 | swap_model | f_L0_019 | lower_quality: f_L0_019: abo_B0154VUESC is rated 4.0 against 4.5 of the current model abo_B07GFDZW5W: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Swap the bed to a modern minimal model that carries the modern bedding with a throw across its foot (c:M30). |
| 17883 | 1 | move_piece | f_L0_009 | snap: f_L0_009: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe to free wall span s0 (right wall) to clear the desk in front and provide the required 0.80 m opening clearance. |
| 17884 | 1 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining | no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | Add the two missing dining chairs (and the potted plant the twin has) to complete the living set. |
| 17885 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | group checks: F4 f_L1_070: armchair stands behind the back of f_L1_017, looking at it | Re-solve the room layout to fix the major clearance and group layout issues: the armchair behind the sofa, the blocked free zone in front of the second sofa, the coffee table not in front of the sofa, the armchair misalignment/distance from the coffee table, and the chair clearance behind the dining |
| 17888 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F4 f_L-1_102: tv_unit stands behind the back of f_L-1_069, f_L-1_072, looking at it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn armchair f_L-1_072 to face away from the back of sofa f_L-1_054 (front 180°) to fix F4 orientation and improve walkway access G11. |
| 17889 | 1 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Move wardrobe to free wall span s0 (wall w_L0_003) to clear the desk in front and provide the required 0.80 m opening clearance. |
| 17890 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | max_tries: r_L1_oyun_aktivite_ve_dinlenme_odasi was edited 3 times in this round | Try the third solver candidate to clear the armchair-behind-sofa F4 while fixing the clearance and group layout issues |
| 17891 | 1 | swap_model | f_L0_030 | asset_unusable: WoodenTable_01 is not used: audit removed | Replace the plain white boxy desk with a warm rustic wooden table to match the residential style (a:F411). |
| 17892 | 1 | swap_model | f_L0_041 | off_style: f_L0_041: painted_wooden_nightstand is of the styles ['rustic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric-mesh nightstand with a library rustic wooden nightstand (a:F383). |
| 17893 | 1 | swap_model | f_L0_042 | off_style: f_L0_042: painted_wooden_nightstand is of the styles ['rustic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric-mesh nightstand with a library rustic wooden nightstand (a:F384). |
| 17894 | 1 | mark_not_furniture | f_L-1b_001 | no_crop: f_L-1b_001 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | Untyped drawn cluster larger than 4.5 m on a side is a group outline, not a single furniture piece. |
| 17896 | 1 | move_piece | f_L1_060 | snap: f_L1_060: no free place on wall w_L1_001 (doors, windows) | Snap the tv_unit's back onto the south wall (free span s0) so it is wall-mounted and opposite the sofa. |
| 17897 | 1 | resize_piece | f_L-1b_041 | score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.43 m (needs ≤ 2.50 m)) | Sofa was read 0.90 wide x 2.13 deep, turned 90° against product sizes; 2.13 x 0.90 matches a standard sofa and its front at 270°. |
| 17898 | 1 | move_piece | f_L0_009 | snap: f_L0_009: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe to free wall span s1 (right wall w_L0_010) to clear the desk and provide the required 0.80 m front clearance. |
| 17899 | 1 | swap_model | f_L0_041 | acceptance: pin_refused: f_L0_041: abo_B079VKDKC1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric-mesh nightstand with a modern-minimal library bedside cabinet (a:F383). |
| 17900 | 1 | move_piece | f_L1_060 | snap: f_L1_060: no free place on wall w_L1_012 (doors, windows) | Snap the tv_unit's back onto the west wall (free span s7) so it is wall-mounted. |
| 17901 | 1 | move_piece | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | Move wardrobe to the right wall (span s1) to clear the desk and provide the required 0.80 m front clearance. |
| 17902 | 1 | resize_piece | f_L-1b_042 | score: plausibility -15 -> -25 (F3 f_L-1b_042: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_051: armchair does not face its group (f_L-1b_042, f_L-1b_046); F4 f_L-1b_075: armchair does not face its group (f_L-1b_046, f_L-1b_042); G3 f_L-1b_051: armchair f_L-1b_051 is 65° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.57 m (needs ≤ 2.50 m)) | Sofa was flagged as turned 90° against product sizes; swap width/depth to a standard 2.13m wide x 0.90m deep sofa keeping the drawn footprint. |
| 17903 | 1 | move_piece | f_L-1b_046 | acceptance: finding F3:f_L-1b_046 is still there after the edit (sofa: its back is not on a wall (0.29 m off)) | Sofa back is 0.59 m off the wall; shift it toward the back wall to satisfy F3 off-wall check. |
| 17904 | 1 | move_piece | f_L1_060 | f_L1_029: no_overlap, f_L1_032: no_overlap, f_L1_060: inside_room, f_L1_060: no_overlap | Place the tv_unit against the south wall so its back is on the wall and it faces the sofa. |
| 17905 | 1 | move_piece | f_L0_021 | score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Move bed toward room center to gain the required 0.60 m clearance on both sides and allow a nightstand on the free left side. |
| 17906 | 1 | move_piece | f_L1_060 | max_tries: f_L1_060 was edited 3 times in this round | Place the tv_unit against the west wall (free span s7) so its back is on the wall. |
| 17907 | 1 | move_piece | f_L0_021 | score: plausibility 67 -> 37 (F3 f_L0_021: bed_double: the headboard stands in the room (0.15 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free); G5 f_L0_021: bed_double f_L0_021: 0.38 m free along the left side, needs ≥ 0.60 m) | Shift bed slightly toward room center to gain the required 0.60 m clearance on the right side while keeping the headboard against the wall. |
| 17909 | 1 | rotate_piece | f_L1_029 | f_L1_029: clearance_ok, score: plausibility 21 -> -9 (F4 f_L1_029: armchair faces a wall 0.23 m in front of it; F6 f_L1_029: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_029: armchair f_L1_029 is 160° off the sofa f_L1_018 (needs ≤ 30°) at 2.29 m (needs ≤ 2.50 m); G11 f_L1_029: armchair f_L1_029: its front use zone is not reached by a 0.60 m walkway from door d_L1_002) | Turn the armchair to face the seating area (away from the tv_unit's back) instead of looking at the TV's back. |
| 17913 | 1 | rotate_piece | f_L1_029 | acceptance: finding F4:f_L1_029 is still there after the edit (armchair stands behind the back of f_L1_060, looking at it) | Turn the armchair to face the sofa/coffee table (north) so it is part of the seating group, not looking at the TV's back. |
| 17916 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_024 has only 0.78 m behind it (needs 0.81 m); shifting it 0.14 m away from the table opens the clearance. |
| 17917 | 1 | swap_model | f_L-1_049 | no_change: f_L-1_049 already uses the model abo_B072PZ4LQ2 | Grey armchair clashes with the light minimalist sofa; the ecru Rivet Emerly matches the light seating set (a:F410). |
| 17918 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042)); 1 more kept | Armchair is 114° off the sofa and does not face its group; rotate to face the sofa (270°) to fix F4 and G3. |
| 17919 | 1 | swap_model | f_L-1_053 | acceptance: pin_refused: f_L-1_053: abo_B07BW8MJQT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The parametric boxy corner sofa looks like a placeholder; the beige Rivet Edgewest L-sectional is a designed modern minimal model (a:F234). |
| 17920 | 1 | rotate_piece | f_L-1b_051 | acceptance: finding F4:f_L-1b_051 is still there after the edit (armchair does not face its group (f_L-1b_042)); 1 more kept | Armchair is 33° off the sofa and does not face its group; rotate to face the sofa (270°) to fix F4 and G3. |
| 17922 | 1 | rotate_piece | f_L1_032 | acceptance: finding F4:f_L1_032 is still there after the edit (armchair stands behind the back of f_L1_060, looking at it) | Turn the armchair to face the sofa/coffee table (north) so it joins the seating group instead of looking at the TV's back. |
| 17923 | 1 | move_piece | f_L-1b_017 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shifting the dining table 0.15 m south opens the 0.78 m pullout behind chair f_L-1b_024 to the required 0.81 m. |
| 17926 | 1 | relayout_room | r_L-1b_salon | group checks: G9 r_L-1b_salon_kitchen: kitchen r_L-1b_salon_kitchen has no fridge (fridge) | Re-solve the seating group so the armchairs face the sofa at a proper distance, fixing F4/G3 orientation findings. |
| 17929 | 1 | rotate_piece | f_L1_056 | acceptance: finding F4:f_L1_056 is still there after the edit (armchair stands behind the back of f_L1_060, looking at it) | Turn the reading-corner armchair to face into the room (north) instead of looking at the sofa's back. |
| 17931 | 1 | relayout_room | r_L-1b_salon | group checks: G9 r_L-1b_salon_kitchen: kitchen r_L-1b_salon_kitchen has no fridge (fridge) | Re-solve the seating group with candidate 2 so the armchairs face the sofa at a proper distance, fixing F4/G3 orientation findings. |
| 17932 | 1 | relayout_room | r_L-1b_salon_2 | group checks: G9 r_L-1b_salon_2_kitchen: kitchen r_L-1b_salon_2_kitchen has no fridge (fridge) | Solver candidate 1 re-solves the seating and dining groups to clear the G6 pullout behind chair f_L-1b_024 and the armchair orientation findings. |
| 17936 | 1 | retype_piece | f_L1_037 | retype: bench is no candidate for f_L1_037 (1.40 x 0.45 m at [9.07, 7.22]): the size table and the room / zone give bookshelf, console_table, display_cabinet, sideboard, table_coffee, tv_unit | Confirm the bench type; it is a valid low seat in a living room, so the wrong-type finding is a misread. |
| 17938 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | The armchair stands behind the back of the sofa looking at it; turn it to face +x into the room so its front use zone opens (c:F4, a:F4). |
| 17944 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has only 0.78 m clearance behind it, needs 0.81 m; nudge it 0.03 m away from the piece behind to satisfy G6. |
| 17946 | 1 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041)) | Armchair f_L-1b_053 is 114° off the sofa f_L-1b_041; turning its front to 270° faces it into the seating group. |
| 17948 | 1 | relayout_room | r_L1_teras | group checks: F8 f_L1_070: potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | Re-solve the balcony group with the top candidate to complete the terrace set (seating pair + plant) and remove the floating plant. |
| 17951 | 1 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace parametric mesh with a library nightstand model (scandinavian/modern, 0.55x0.45m) to resolve the below-library level finding. |
| 17953 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Complete the kitchen run with the missing worktop styling/small appliances so the worktop is no longer bare (a:N95, a:N103, a:Q13:f_L-1_001, a:D3). |
| 17954 | 1 | move_piece | f_L-1b_071 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Side table blocks the free zone in front of sofa f_L-1b_046; move it to the side of the sofa to clear the front path (F6). |
| 17959 | 1 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace parametric mesh with a library nightstand model (scandinavian/modern, 0.55x0.45m) to resolve the below-library level finding. |
| 17962 | 1 | rotate_piece | f_L-1b_054 | acceptance: finding F4:f_L-1b_054 is still there after the edit (armchair does not face its group (f_L-1b_041)) | Armchair f_L-1b_054 is 33° off the sofa f_L-1b_041 (needs ≤30°); turning its front to 270° faces it into the seating group. |
| 17963 | 1 | place_group | r_L-1_mutfak | no_place: dining group: no place passes the checks (dining: no place passes the checks) | Add the missing dining group (a small bistro set) to furnish the empty kitchen space and give the worktop area a styled, used look (a:N95, a:N103, a:Q13:f_L-1_001, a:D3). |
| 17965 | 1 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace parametric mesh with a library nightstand model (modern minimal, 0.40x0.36m) to resolve the below-library level finding. |
| 17968 | 1 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace parametric mesh with a library nightstand model (modern minimal, 0.40x0.36m) to resolve the below-library level finding. |
| 17969 | 1 | place_group | r_L-1_mutfak | no_place: dining group: no place passes the checks (dining: no place passes the checks) | Add a small square bistro dining set to furnish the empty kitchen space (a:N95, a:N103, a:Q13:f_L-1_001, a:D3). |
| 17974 | 1 | swap_model | f_L0_033 | off_style: f_L0_033: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace parametric mesh with a classic nightstand model (0.57x0.42m, 0.7m height) to resolve the below-library level finding. |
| 17975 | 1 | swap_model | f_L0_034 | max_tries: f_L0_034 was edited 3 times in this round | Replace parametric mesh with a classic nightstand model (0.57x0.42m, 0.7m height) to resolve the below-library level finding. |
| 17977 | 1 | swap_model | f_L0_033 | max_tries: f_L0_033 was edited 3 times in this round | Replace parametric mesh with a modern minimal nightstand model (0.40x0.36m, 0.47m height) to resolve the below-library level finding. |
| 17979 | 1 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Toilet built below library level (parametric mesh) and floating 0.20 m; swap to a library model that sits on the floor. |
| 17984 | 1 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Tall cabinet built below library level (parametric mesh); swap to a real 0.40 m wide library model. |
| 17987 | 1 | swap_model | f_L0_003 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Replace the concrete basin with its ornate bronze mirror frame (D3 style clash) and the floating mesh (S1 +0.384 m) with a clean modern minimal sink that fits the 1.0 x 0.55 footprint. |
| 17988 | 1 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Washbasin floats 0.384 m above its floor; swap to a library model that sits on the floor. |
| 17991 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall); with the front at 270 deg its back is not on a wall | Shower front faced 90° into a wall 0.10 m away; turning it 180° puts its back on the free wall span s0 and its front into the room, clearing F4. |
| 17996 | 1 | swap_model | f_L0_003 | asset_unusable: 3dwh_2a2928a83cea9dbe8fbc006f is not used: audit removed | Replace the concrete basin with its ornate bronze mirror frame (D3) and floating mesh (S1) with a clean modern single lav vanity fitting the 1.0 x 0.55 footprint. |
| 17997 | 1 | swap_model | f_L-1_103 | asset_unusable: abo_B07LC9HXSF is not used: audit removed | Tall cabinet built below library level; try the narrowest real 0.45 m wide library model. |
| 18000 | 1 | swap_model | f_L0_003 | max_tries: f_L0_003 was edited 3 times in this round | Replace the concrete basin with its ornate bronze mirror frame (D3) and floating mesh (S1) with a clean modern minimal vanity unit and basin fitting the 1.0 x 0.55 footprint. |
| 18003 | 1 | swap_model | f_L-1_052 | pin_refused: f_L-1_052: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Toilet f_L-1_052 was built as a parametric mesh (P7) and floats 0.20 m above its floor (S1); swapping to a library toilet model restores a grounded, library-level build. |
| 18006 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Tall cabinet f_L-1_104 was built as a parametric mesh (P7); swapping to the 0.40 m wide library model (Marca Amazon Movian Moselle) restores a library-level build that fits its 0.40 m footprint. |
| 18008 | 1 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Washbasin f_L-1_025 floats 0.384 m above its floor (S1); swapping to a library washbasin model restores a grounded, library-level build. |
| 18014 | 1 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | The drawn vector geometry (hanging rail with hangers) reads as a coat closet/wardrobe, not a bench; confirming the wardrobe type fixes the wrong_type finding. |
| 18025 | 1 | retype_piece | f_L1_027 | acceptance: finding RC:f_L1_027 is still there after the edit (f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | The recognition crop shows a hanging rail with hangers (coat closet); the size table allows dresser for 1.52 x 0.60 m in a hall, which is the closest valid type to a coat closet. |
| 18026 | 1 | retype_piece | f_L1_028 | retype: wardrobe is no candidate for f_L1_028 (1.52 x 0.60 m at [12.61, 9.90]): the size table and the room / zone give bench, dresser | Vector geometry (hanging rail with hangers) reads it as a coat closet/wardrobe, outranking the AI passes' bench reading; confirming its type as wardrobe. |
| 18031 | 1 | retype_piece | f_L1_028 | acceptance: finding RC:f_L1_028 is still there after the edit (f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | Vector geometry reads a hanging rail with hangers (coat closet); dresser is the size-table candidate closest to a coat closet for 1.52 x 0.60 m, resolving the bench-vs-coat-closet doubt. |
| 18033 | 1 | swap_model | f_L-1_052 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Toilet f_L-1_052 was built as a parametric mesh (P7) and floats 0.20 m above its floor (S1); swapping to the real Qualitas toilet (0.48x0.68 m, close to the drawn 0.50x0.69 m) restores a grounded, library-level build. |
| 18034 | 1 | relayout_room | r_L0_koridor | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Apply the best solver candidate (score 9.2, best balance) to anchor the corridor wall with a bench, resolving the missing place to sit. |
| 18035 | 1 | swap_model | f_L0_017 | pin_refused: f_L0_017: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Toilet f_L0_017 was built below library level (parametric mesh) and floats 0.20 m above its floor; swap to a library model that sits on the floor. |
| 18036 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Tall cabinet f_L-1_104 was built as a parametric mesh (P7); swapping to the real Movian Argenton bathroom column (0.30x0.27x1.40 m) restores a library-level build that fits its 0.40x0.35 m footprint. |
| 18037 | 1 | swap_model | f_L-1_025 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Washbasin f_L-1_025 floats 0.384 m above its floor (S1); swapping to the real 0.97x0.50 m sink (close to the drawn 1.00x0.55 m) restores a grounded, library-level build. |
| 18038 | 1 | relayout_room | r_L0_koridor | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes a:F247 (D3, target r_L0_koridor): apply the best solver candidate (score 9.2) to anchor the corridor wall with a bench, resolving the missing place to sit. |
| 18040 | 1 | relayout_room | r_L0_koridor | max_tries: r_L0_koridor was edited 3 times in this round | Fixes a:F247 (D3, target r_L0_koridor): apply solver candidate 2 to anchor the corridor wall with a bench, resolving the missing place to sit. |
| 18042 | 1 | swap_model | f_L0_017 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Toilet f_L0_017 was built below library level (parametric mesh) and floats 0.20 m above its floor; swap to the real Qualitas toilet model (0.48 x 0.68 m, close to the drawn 0.50 x 0.69 m) that sits on the floor. |
| 18046 | 1 | swap_model | f_L0_017 | acceptance: pin_refused: f_L0_017: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Toilet f_L0_017 was built below library level (parametric mesh) and floats 0.20 m above its floor; swap to the real Caesar Toilet C1348 (0.46 x 0.72 m) that sits on the floor. |
| 18047 | 1 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the generic blocky grey shoe cabinet with a walnut japandi/minimal shoe rack (0.70x0.27x0.40, close to the 0.6x0.3 footprint) to fix the placeholder look (a:F406). |
| 18049 | 1 | swap_model | f_L0_017 | max_tries: f_L0_017 was edited 3 times in this round | Toilet f_L0_017 was built below library level (parametric mesh) and floats 0.20 m above its floor; swap to the real ConDoc 5 Toilet (0.44 x 0.72 m) that sits on the floor. |
| 18053 | 1 | swap_model | f_L0_005 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Washbasin f_L0_005 floats 0.384 m above its floor; swap to the real Sink model (0.965 x 0.5 m, close to the drawn 1.0 x 0.55 m) that sits on the floor. |
| 18054 | 1 | swap_model | f_L0_005 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Washbasin f_L0_005 floats 0.384 m above its floor; swap to the real Ikea Boholmen Sink (0.96 x 0.5 m, close to the drawn 1.0 x 0.55 m) that sits on the floor. |
| 18057 | 1 | swap_model | f_L0_005 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Washbasin f_L0_005 floats 0.384 m above its floor; swap to the real Hudson Reed Sublime Vanity Unit & Basin (0.91 x 0.60 m, close to the drawn 1.0 x 0.55 m) that sits on the floor. |
| 18551 | 2 | swap_model | f_L0_021 | no_change: f_L0_021 already uses the model abo_B086TGFT35 | Argus: The very dark, boxy storage bed frame is heavy and dated, clashing with the light wood floor and desk; the scandinavian/japandi model matches the reference. (fixes a:F250) |
| 18557 | 2 | set_camera | ext_3 | eye height 2.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The judge scores the view 2/5: a strange, low angle that crops the building awkwardly, with flat grey lighting. The earlier set_camera was refused because the eye height was 5.56 m above the ground; the new pose is at 1.6 m, within the allo (fixes a:F271) |
| 18558 | 2 | swap_model | f_L-1_031 | no_change: f_L-1_031 already uses the model hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 | Argus: A 0.19 m offset is outside the 0.05 m tolerance; swapping to a model with a closer footprint reduces the offset and improves the match to the drawing. (fixes a:F349) |
| 18559 | 2 | swap_model | f_L-1_038 | asset_unusable: 3dwh_b27bb152311c2c1b3f509195 is not used: audit removed | Argus: A 0.08 m offset is outside the 0.05 m tolerance; swapping to a model with a closer footprint reduces the offset and improves the match to the drawing. (fixes a:F350) |
| 18561 | 2 | swap_model | f_L-1_070 | no_change: f_L-1_070 already uses the model abo_B071J7Q9WN | Argus: A 0.12 m offset and a size mismatch are outside the 0.05 m tolerance; swapping to a model with a closer footprint reduces the offset and improves the match to the drawing. (fixes a:F352) |
| 18562 | 2 | swap_model | f_L-1_071 | asset_unusable: 3dwh_49c89838e523cdc64ffa7de1 is not used: audit removed | Argus: The drawn armchair is 0.642 x 0.569 m but the built model is 0.65 x 0.80 m; the 0.23 m depth is a model mismatch, not a placement error, so the fix is a model swap to a 0.64 x 0.79 footprint. (fixes a:F353) |
| 18563 | 2 | swap_model | f_L-1_072 | asset_unusable: 3dwh_49c89838e523cdc64ffa7de1 is not used: audit removed | Argus: Same drawn size 0.642 x 0.569 m vs a 0.65 x 0.80 m model; rotation was refused (it breaks the facing group), so the size mismatch is the cause and a model swap answers it. (fixes a:F354) |
| 18566 | 2 | swap_model | f_L-1_051 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The toilet was built with a parametric mesh below the library level; a real library model of matching size (0.48 x 0.68 m) is available. (fixes a:F374) |
| 18567 | 2 | swap_model | f_L-1_052 | memory: the same edit was rejected in round 1: asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The toilet was built with a parametric mesh below the library level; a real library model of matching size (0.48 x 0.68 m) is available. (fixes a:F375) |
| 18568 | 2 | swap_model | f_L-1_103 | memory: the same edit was rejected in round 1: asset_unusable: abo_B07LC9HXSF is not used: audit removed | Argus: The tall_cabinet was built with a parametric mesh below the library level; a real library model of matching size (0.45 x 0.42 m) is available. (fixes a:F376) |
| 18569 | 2 | swap_model | f_L-1_104 | asset_unusable: abo_B07LC9HXSF is not used: audit removed | Argus: The tall_cabinet was built with a parametric mesh below the library level; a real library model of matching size (0.45 x 0.42 m) is available. (fixes a:F377) |
| 18570 | 2 | swap_model | f_L0_016 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The toilet was built with a parametric mesh below the library level; a real library model of matching size (0.48 x 0.68 m) is available. (fixes a:F378) |
| 18571 | 2 | swap_model | f_L0_017 | memory: the same edit was rejected in round 1: asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The toilet was built with a parametric mesh below the library level; a real library model of matching size (0.48 x 0.68 m) is available. (fixes a:F379) |
| 18572 | 2 | swap_model | f_L0_018 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The toilet was built with a parametric mesh below the library level; previous swap attempts were refused (asset_unusable, max_tries), but objaverse_5b18711616054a44b025d9272b745a6a was not among the refused assets and matches the drawn size (fixes a:F380) |
| 18573 | 2 | swap_model | f_L0_033 | no_change: f_L0_033 already uses the model abo_B07DBB7831 | Argus: The nightstand was built with a parametric mesh below the library level; a real library model of matching size (0.51 x 0.46 m) is available. (fixes a:F381) |
| 18574 | 2 | swap_model | f_L0_034 | no_change: f_L0_034 already uses the model abo_B07DBB7831 | Argus: The nightstand was built with a parametric mesh below the library level; a real library model of matching size (0.51 x 0.46 m) is available. (fixes a:F382) |
| 18575 | 2 | swap_model | f_L0_041 | acceptance: pin_refused: f_L0_041: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The nightstand was built with a parametric mesh below the library level; a real library model of matching size (0.40 x 0.40 m) is available. (fixes a:F383) |
| 18576 | 2 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The nightstand was built with a parametric mesh below the library level; a real library model of matching size (0.40 x 0.40 m) is available. (fixes a:F384) |
| 18578 | 2 | swap_model | f_L-1_094 | no_change: f_L-1_094 already uses the model hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 | Argus: The current model is a generic blocky grey box. Swapping to a minimal/modern shoe cabinet of the same footprint (0.62 x 0.30 m) removes the placeholder look. (fixes a:F406) |
| 18582 | 2 | move_piece | f_L0_010 | f_L0_010: clearance_ok, score: plausibility 70 -> 60 (F3 f_L0_010: wardrobe: its back is not on a wall (0.08 m off); G13 f_L0_010: wardrobe f_L0_010: 0.51 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.14m away from the wall to increase front clearance from 0.66m to the required 0.80m. |
| 18583 | 2 | move_piece | f_L0_019 | score: plausibility 70 -> 40 (F3 f_L0_019: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Shift bed 0.07m to the right to increase left-side clearance to 0.60m and right-side clearance to 0.63m, satisfying the 0.60m minimum on both sides. |
| 18585 | 2 | move_piece | f_L0_042 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.11 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.13 m from the bed side (needs ≤ 0.30 m)) | Move nightstand away from the window sill to clear the blocked opening finding. |
| 18587 | 2 | relayout_room | r_L1_oyun_oyun_aktivite_ve_dinlenme_odasi_2 | exists: no room 'r_L1_oyun_oyun_aktivite_ve_dinlenme_odasi_2' in a room of the building | placeholder |
| 18588 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Reposition the floating TV unit f_L1_060 against a wall and re-solve the seating groups so the armchairs, sofa clearance and coffee table placement are fixed together. |
| 18590 | 2 | retype_piece | f_L1_035 | retype: bench is no candidate for f_L1_035 (1.40 x 0.45 m at [6.10, 7.22]): the size table and the room / zone give bookshelf, console_table, desk, display_cabinet, sideboard, table_coffee, tv_unit | Confirm the drawn bench's type so the room can be retyped to living without the bench being a wrong-type piece. |
| 18591 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Reposition the floating TV unit f_L1_060 against a wall and re-solve the seating groups so the armchairs, sofa clearance and coffee table placement are fixed together. |
| 18596 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Reposition the floating TV unit f_L1_060 against a wall and re-solve the seating groups so the armchairs, sofa clearance and coffee table placement are fixed together. |
| 18597 | 2 | retype_piece | f_L-1b_042 | retype: sofa is no candidate for f_L-1b_042 (0.90 x 2.13 m at [4.19, 4.48]): the size table and the room / zone give chaise, stair | c:F2:f_L-1b_042: confirm the drawn sofa type to clear the 90°-turned product-size flag without resizing (resize was rejected in round 1) |
| 18598 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | The room is furnished as a living room (sofas, armchairs, coffee tables, dining set) and its twin is typed living; the bench is now a console table so no piece is wrong-typed. |
| 18599 | 2 | rotate_piece | f_L-1_101 | score: plausibility 30 -> -10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_049: armchair stands behind the back of f_L-1_101, looking at it; F4 f_L-1_053: sofa_corner stands behind the back of f_L-1_101, looking at it; F4 f_L-1_101: tv_unit faces a wall 0.02 m in front of it) | Turn the tv_unit away from the back of armchair f_L-1_071 so it faces the seating group (c:F4:f_L-1_101). |
| 18600 | 2 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.07 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Shift the coffee table away from armchair f_L-1_071 to clear the 0.12 m² overlap (c:F9/a:F9:f_L-1_073). |
| 18603 | 2 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: no place passes the checks (no candidate position fits the room) | The bed and wardrobe have clearance issues (G5, G13) that cannot be fixed by small moves due to wall constraints; the solver can find a better arrangement. |
| 18604 | 2 | rotate_piece | f_L-1b_052 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042)); 1 more kept | c:F4:f_L-1b_052 / c:G3:f_L-1b_052: turn the armchair to face the sofa f_L-1b_042 (front 270°) so it faces its group and aligns within 30° |
| 18608 | 2 | move_piece | f_L-1b_051 | score: plausibility 25 -> 5 (G3 f_L-1b_051: armchair f_L-1b_051 is 41° off the chaise f_L-1b_042 (needs ≤ 30°) at 1.69 m (needs ≤ 2.50 m); G11 f_L-1b_052: armchair f_L-1b_052: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_073: bookshelf f_L-1b_073: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | c:F6:f_L-1b_051 / c:F6:f_L-1b_052: shift the armchair 0.4 m along the row to open the blocked free zone in front of both armchairs |
| 18610 | 2 | move_piece | f_L-1b_033 | memory: the same edit was rejected in round 1: acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | c:G6:f_L-1b_033: move the chair 0.03 m away from the piece behind to reach the 0.81 m minimum clearance |
| 18612 | 2 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall into the free span s0 so its front (facing +y into the room) has the full 0.8 m clearance instead of 0.17 m blocked by the desk. |
| 18616 | 2 | move_piece | f_L-1b_051 | score: plausibility 25 -> 5 (G3 f_L-1b_051: armchair f_L-1b_051 is 40° off the chaise f_L-1b_042 (needs ≤ 30°) at 1.66 m (needs ≤ 2.50 m); G11 f_L-1b_052: armchair f_L-1b_052: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_073: bookshelf f_L-1b_073: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | c:F6:f_L-1b_051 / c:F6:f_L-1b_052: shift the armchair 0.25 m along the row to open the blocked free zone in front of both armchairs |
| 18617 | 2 | move_piece | f_L0_011 | memory: the same edit was rejected in round 2: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall into the free span s0 so its front (facing +y into the room) has the full 0.8 m clearance instead of 0.17 m blocked by the desk. |
| 18618 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | c:G6:f_L-1b_033: move the chair 0.06 m away from the piece behind to reach the 0.81 m minimum clearance |
| 18620 | 2 | move_piece | f_L0_011 | memory: the same edit was rejected in round 2: acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall into the free span s0 so its front (facing +y into the room) has the full 0.8 m clearance instead of 0.17 m blocked by the desk. |
| 18625 | 2 | move_piece | f_L-1b_051 | acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052); 1 more kept | c:F6:f_L-1b_051 / c:F6:f_L-1b_052: shift the armchair 0.25 m along the row away from f_L-1b_052 to open the blocked free zone in front of both armchairs |
| 18629 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | c:G6:f_L-1b_033: move the chair 0.09 m away from the piece behind to reach the 0.81 m minimum clearance |
| 18636 | 2 | remove_piece | f_L0_042 | score: plausibility 70 -> 67 (G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free)) | AI-added nightstand blocks the window (G12) and cannot be repositioned without overlapping the bed; removing it clears the window while f_L0_041 remains as the other nightstand. |
| 18637 | 2 | move_piece | f_L-1b_051 | max_tries: f_L-1b_051 was edited 3 times in this round | c:F6:f_L-1b_051 / c:F6:f_L-1b_052: shift the armchair 0.5 m along the row away from f_L-1b_052 to open the blocked free zone in front of both armchairs |
| 18638 | 2 | move_piece | f_L-1b_033 | max_tries: f_L-1b_033 was edited 3 times in this round | c:G6:f_L-1b_033: move the chair 0.14 m away from the piece behind to reach the 0.81 m minimum clearance |
| 18662 | 2 | swap_model | f_L0_030 | acceptance: pin_refused: f_L0_030: abo_B075ZBVZST: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap plain white boxy desk for a walnut mid-century curved wood desk to add warmth and match the residential style. |
| 18666 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_modern_minimal_1_d5536003: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Replace the ornate bronze-framed mirror model with a clean modern minimal washbasin matching the concrete basin (a:F241) and a mesh that sits on the floor (c:S1:f_L0_003). |
| 18667 | 2 | swap_model | f_L-1_052 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Toilet built below library level (P7) and floating +0.20 m (S1); swap to a real library toilet model that fits the drawn 0.5x0.69 footprint. |
| 18669 | 2 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Door d_L-1_001 swings into the washbasin on one hinge side; nudge it up to 0.5 m to clear the swing. |
| 18671 | 2 | swap_model | f_L0_018 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Replace the parametric mesh with a library-level japandi toilet model (a:F380) whose footprint matches the drawn 0.5x0.69 and sits on the floor (c:S1:f_L0_018). |
| 18672 | 2 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Washbasin floats +0.384 m above its floor (S1); swap to a real library washbasin model that sits on the floor. |
| 18676 | 2 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: drawer_cabinet: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Tall cabinet built below library level (P7); swap to a real library tall cabinet model. |
| 18677 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Clean minimal washbasin model to replace the ornate bronze-framed one (a:F241) and fix the floating mesh (c:S1:f_L0_003). |
| 18682 | 2 | swap_model | f_L0_041 | acceptance: pin_refused: f_L0_041: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap parametric nightstand for a real Movian High Gloss 2 Drawer Bedside Cabinet in Black and Walnut to match the modern minimal style. |
| 18684 | 2 | swap_model | f_L0_018 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Library-level minimal toilet model to replace the parametric mesh (a:F380) and fix the floating mesh (c:S1:f_L0_018). |
| 18688 | 2 | swap_model | f_L-1_052 | pin_refused: f_L-1_052: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Toilet built below library level (P7) and floating +0.20 m (S1); try another real library toilet model that fits the drawn 0.5x0.69 footprint. |
| 18691 | 2 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_japandi_3_fc4e0710: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Washbasin floats +0.384 m above its floor (S1); try another real library washbasin model that sits on the floor. |
| 18692 | 2 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Tall cabinet built below library level (P7); try a real library tall cabinet model (0.52x0.25x1.63) that fits the 0.4x0.35 footprint. |
| 18694 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Modern washbasin model to replace the ornate bronze-framed one (a:F241) and fix the floating mesh (c:S1:f_L0_003). |
| 18695 | 2 | swap_model | f_L0_018 | max_tries: f_L0_018 was edited 3 times in this round | Library-level japandi toilet model to replace the parametric mesh (a:F380) and fix the floating mesh (c:S1:f_L0_018). |
| 18699 | 2 | swap_model | f_L0_003 | max_tries: f_L0_003 was edited 3 times in this round | Clean japandi washbasin model to replace the ornate bronze-framed one (a:F241) and fix the floating mesh (c:S1:f_L0_003). |
| 18705 | 2 | swap_model | f_L-1_052 | max_tries: f_L-1_052 was edited 3 times in this round | Toilet built below library level (P7) and floating +0.20 m (S1); try a classic library toilet model that fits the drawn 0.5x0.69 footprint. |
| 18706 | 2 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Washbasin floats +0.384 m above its floor (S1); try a minimal library washbasin model that sits on the floor. |
| 18708 | 2 | swap_model | f_L-1_104 | max_tries: f_L-1_104 was edited 3 times in this round | Tall cabinet built below library level (P7); try a real library tall cabinet model (0.51x0.45x1.96) that fits the 0.4x0.35 footprint. |
| 18713 | 2 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18714 | 2 | swap_model | f_L1_021 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18715 | 2 | swap_model | f_L0_006 | pin_refused: f_L0_006: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Swap floating washbasin model (0.384 m above floor) for one with a correct base height to fix S1. |
| 18717 | 2 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating washbasin model (lowest point +0.384 m) for a floor-sitting model to clear the S1 clearance error. |
| 18719 | 2 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating toilet model (lowest point +0.200 m) for a floor-sitting model to clear the S1 clearance error. |
| 18720 | 2 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18721 | 2 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18723 | 2 | swap_model | f_L0_006 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Swap floating washbasin model (0.384 m above floor) for a real product model with a correct base height to fix S1. |
| 18725 | 2 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18727 | 2 | swap_model | f_L0_006 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Swap floating washbasin model (0.384 m above floor) for a real product model with a correct base height to fix S1. |
| 18729 | 2 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18730 | 2 | swap_model | f_L1_016 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Swap the floating washbasin model (lowest point +0.384 m) for a real floor-sitting sink model to clear the S1 clearance error. |
| 18731 | 2 | swap_model | f_L1_022 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Swap the floating toilet model (lowest point +0.200 m) for a real floor-sitting toilet model to clear the S1 clearance error. |
| 18734 | 2 | swap_model | f_L0_006 | max_tries: f_L0_006 was edited 3 times in this round | Swap floating washbasin model (0.384 m above floor) for a real product model with a correct base height to fix S1. |
| 18735 | 2 | swap_model | f_L1_015 | max_tries: f_L1_015 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18736 | 2 | swap_model | f_L1_021 | max_tries: f_L1_021 was edited 3 times in this round | Current toilet model floats 0.200 m above the floor (S1); swap to a floor-standing model to clear the vertical offset. |
| 18738 | 2 | swap_model | f_L1_016 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Swap the floating washbasin model (lowest point +0.384 m) for a real floor-sitting vanity model to clear the S1 clearance error. |
| 18739 | 2 | swap_model | f_L1_022 | acceptance: pin_refused: f_L1_022: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the floating toilet model (lowest point +0.200 m) for a real floor-sitting toilet model to clear the S1 clearance error. |
| 18740 | 2 | swap_model | f_L0_015 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Swap floating toilet model (0.200 m above floor) for a real product model with correct base height and integrated paper holder to fix S1 and M26. |
| 18743 | 2 | swap_model | f_L0_015 | acceptance: pin_refused: f_L0_015: hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap floating toilet model (0.200 m above floor) for a real product model with correct base height and integrated paper holder to fix S1 and M26. |
| 18745 | 2 | swap_model | f_L0_015 | acceptance: pin_refused: f_L0_015: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap floating toilet model (0.200 m above floor) for a real product model with correct base height and integrated paper holder to fix S1 and M26. |
| 18746 | 2 | swap_model | f_L1_016 | max_tries: f_L1_016 was edited 3 times in this round | Swap the floating washbasin model (lowest point +0.384 m) for a real floor-sitting sink model to clear the S1 clearance error. |
| 18747 | 2 | swap_model | f_L1_022 | max_tries: f_L1_022 was edited 3 times in this round | Swap the floating toilet model (lowest point +0.200 m) for a real floor-sitting toilet model to clear the S1 clearance error. |
| 18749 | 2 | swap_model | f_L0_015 | max_tries: f_L0_015 was edited 3 times in this round | Swap floating toilet model (0.200 m above floor) for a real product model with correct base height and integrated paper holder to fix S1 and M26. |
| 19234 | 3 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: The kitchen is not designed. The worktop is completely empty, lacking any of the small appliances (kettle, toaster, etc.) that a furnished kitchen should have. (fixes a:N95) |
| 19235 | 3 | complete_group | r_L0_e_banyo_2 | group_exists: no group 'r_L0_e_banyo_2' in r_L0_e_banyo_2 (groups: r_L0_e_banyo_2.bathroom_set) | Argus: r_L0_e_banyo_2 has shower, toilet, washbasin but no tall_cabinet, while its twin r_L0_e_banyo has one. The bathroom set is incomplete. (fixes a:N96) |
| 19236 | 3 | complete_group | r_L1_teras_2 | group_exists: no group 'r_L1_teras_2' in r_L1_teras_2 (groups: r_L1_teras_2.balcony) | Argus: r_L1_teras_2 has chair and table_dining but no potted_plant, while its twin r_L1_teras has one. The balcony set is incomplete. (fixes a:N97) |
| 19237 | 3 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group_exists: no group 'r_L1_oyun_aktivite_ve_dinlenme_odasi_2' in r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (groups: r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining, r_L1_oyun_aktivite_ve_dinlenme_odasi_2.living_storage, r_L1_oyun_aktivite_ve_dinlenme_odasi_2.living_storage.dining, r_L1_oyun_aktivite_ve_dinlenme_odasi_2.reading_corner, r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating, r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.f_L1_019) | Argus: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 is missing potted_plant compared to its twin. The living set is incomplete. (fixes a:N98) |
| 19238 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 is already a living | Argus: Twin of the same misread: typed 'other' but furnished as a living room. (fixes a:N100) |
| 19241 | 3 | retype_piece | f_L-1_057 | no_change: f_L-1_057 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_057 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays (fixes a:c10) |
| 19242 | 3 | retype_piece | f_L-1_059 | no_change: f_L-1_059 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_059 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays (fixes a:c11) |
| 19243 | 3 | retype_piece | f_L-1_064 | no_change: f_L-1_064 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_064 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays (fixes a:c12) |
| 19244 | 3 | retype_piece | f_L-1_066 | no_change: f_L-1_066 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_066 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays (fixes a:c13) |
| 19245 | 3 | retype_piece | f_L-1_075 | no_change: f_L-1_075 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_075 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c14) |
| 19246 | 3 | retype_piece | f_L-1_076 | no_change: f_L-1_076 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_076 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c15) |
| 19247 | 3 | retype_piece | f_L-1_077 | no_change: f_L-1_077 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_077 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c16) |
| 19248 | 3 | retype_piece | f_L-1_078 | no_change: f_L-1_078 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_078 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_026_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c17) |
| 19250 | 3 | move_piece | f_L0_010 | memory: the same edit was rejected in round 2: f_L0_010: clearance_ok; score: plausibility 70 -> 60 (F3 f_L0_010: wardrobe: its back is not on a wall (0.08 m off); G13 f_L0_010: wardrobe f_L0_010: 0.51 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.14m away from the wall to increase front clearance from 0.66m to the required 0.80m. |
| 19253 | 3 | move_piece | f_L0_010 | f_L0_010: clearance_ok, score: plausibility 70 -> 60 (F3 f_L0_010: wardrobe: its back is not on a wall (0.08 m off); G13 f_L0_010: wardrobe f_L0_010: 0.46 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.19m away from the wall to increase front clearance to the required 0.80m. |
| 19254 | 3 | rotate_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Rotate wardrobe to face free wall span s0, clearing the desk from its front to fix M19 door swing blockage and G13 clearance. |
| 19256 | 3 | move_piece | f_L0_010 | acceptance: finding G13:f_L0_010 is still there after the edit (wardrobe f_L0_010: 0.64 m free in front, needs ≥ 0.80 m) | Snap wardrobe back to wall and shift along it to find a position with 0.80m front clearance. |
| 19258 | 3 | move_piece | f_L1_060 | snap: f_L1_060: no free place on wall w_L1_001 (doors, windows) | TV unit f_L1_060 floats 1.01 m off the wall; snap its back to the south wall span s0 so the armchairs face it properly. |
| 19260 | 3 | resize_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L- | c:F2:f_L-1b_041: sofa drawn 0.90 wide x 2.13 deep is a 90° rotation of product proportions; resize to 2.13 x 0.90 |
| 19261 | 3 | move_piece | f_L0_019 | memory: the same edit was rejected in round 2: score: plausibility 70 -> 40 (F3 f_L0_019: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Shift bed 0.07m to the right to increase left-side clearance to 0.60m and right-side clearance to 0.63m. |
| 19262 | 3 | move_piece | f_L1_060 | memory: the same edit was rejected in round 1: f_L1_029: no_overlap; f_L1_032: no_overlap; f_L1_060: inside_room; f_L1_060: no_overlap | TV unit f_L1_060 floats 1.01 m off the wall; move its back onto the south wall (span s0) so the armchairs face it. |
| 19265 | 3 | move_piece | f_L1_060 | f_L1_029: no_overlap, f_L1_032: no_overlap, f_L1_060: no_overlap | TV unit f_L1_060 floats 1.01 m off the wall; move its back onto the south wall (span s0) so the armchairs face it. |
| 19266 | 3 | move_piece | f_L0_019 | score: plausibility 70 -> 40 (F3 f_L0_019: bed_double: the headboard stands in the room (0.10 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Shift bed 0.10m to the right to increase left-side clearance to 0.63m and right-side clearance to 0.60m. |
| 19267 | 3 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move table_coffee f_L-1_074 away from armchair f_L-1_069 to resolve the 0.12 m² overlap (F9) and closer to its drawn position (K3). |
| 19269 | 3 | move_piece | f_L1_060 | max_tries: f_L1_060 was edited 3 times in this round | TV unit f_L1_060 floats 1.01 m off the wall; move its back onto the south wall (span s0), shifted right to clear the armchairs. |
| 19270 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | Room is furnished as a living room (sofas, armchairs, coffee table, dining) and its twin is 'living'; the blocking bench f_L1_035 is now a console table, so the round-1 rejection no longer applies. |
| 19271 | 3 | move_piece | f_L0_042 | memory: the same edit was rejected in round 2: f_L0_019: no_overlap; f_L0_042: no_overlap; score: plausibility 70 -> 47 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.11 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019 | Move nightstand away from the window sill to clear the blocked opening finding. |
| 19273 | 3 | move_piece | f_L0_042 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.16 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.07 m from the bed side (needs ≤ 0.30 m)) | Move nightstand further from the window sill to clear the blocked opening finding. |
| 19276 | 3 | rotate_piece | f_L-1_070 | memory: the same edit was rejected in round 1: f_L-1_070: clearance_ok; score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m ( | Face the armchair into the room centre instead of the back of sofa f_L-1_053 (F4). |
| 19277 | 3 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Shift the coffee table 0.15 m right to clear the 0.12 m² overlap with armchair f_L-1_071 (F9). |
| 19279 | 3 | move_piece | f_L0_042 | score: plausibility 70 -> 44 (F3 f_L0_042: nightstand: its back is not on a wall (0.13 m off); G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: its back 1.60 m from the headboard line (needs ≤ 0.30 m); G11 f_L0_019: bed_double f_L0_019: its left use zone is not reached by a 0.60 m walkway from door d_L0_005) | Move nightstand to the right side of the bed, away from the window, to clear the blocked opening finding. |
| 19280 | 3 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | Move table_coffee f_L-1_074 further from armchair f_L-1_069 to fully resolve the 0.12 m² overlap (F9) and closer to its drawn position (K3). |
| 19282 | 3 | move_piece | f_L1_038 | drawn_lock: f_L1_038: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.51 m) | Coffee table f_L1_038 is not between sofa f_L1_019 and its TV; move it into the zone in front of the sofa. |
| 19285 | 3 | move_piece | f_L1_038 | acceptance: finding G2:f_L1_038 is still there after the edit (coffee table f_L1_038 is not between the sofa and its TV and is 0.09 m from the sofa front, needs ≥ 0.30 m) | Coffee table f_L1_038 is not between sofa f_L1_019 and its TV; shift it 0.3 m toward the sofa to sit in front of it. |
| 19286 | 3 | move_piece | f_L0_042 | max_tries: f_L0_042 was edited 3 times in this round | Move nightstand slightly away from the window sill to clear the blocked opening finding while staying near the bed. |
| 19289 | 3 | rotate_piece | f_L-1b_054 | acceptance: finding F4:f_L-1b_054 is still there after the edit (armchair does not face its group (f_L-1b_041)); 1 more kept | a:F4:f_L-1b_054, a:F478, c:G3:f_L-1b_054: armchair faces 0° (towards f_L-1b_053); turn to 90° to face the sofa f_L-1b_041 |
| 19293 | 3 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.08 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move table_coffee f_L-1_074 0.25m away from armchair f_L-1_069 to resolve the 0.12 m² overlap (F9) within the 0.3m move limit. |
| 19294 | 3 | move_piece | f_L1_038 | acceptance: finding G2:f_L1_038 is still there after the edit (coffee table f_L1_038 is not between the sofa and its TV and is 0.27 m from the sofa front, needs ≥ 0.30 m) | Coffee table f_L1_038 is not between sofa f_L1_019 and its TV; shift it 0.3 m toward the sofa's axis to sit in front of it. |
| 19298 | 3 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Retype untyped drawn piece f_L-1_022 (5.54 x 0.60 m) as a sideboard to resolve the NR finding; it is a large drawn storage element in a living room. |
| 19306 | 3 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move table_coffee f_L-1_074 left and slightly up to clear the overlap with armchair f_L-1_069 (F9) within the 0.3m move limit. |
| 19308 | 3 | retype_piece | f_L-1_022 | retype: kitchen_counter is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Retype untyped drawn piece f_L-1_022 (5.54 x 0.60 m) as a kitchen_counter to resolve the NR finding; the long narrow shape fits a counter run. |
| 19315 | 3 | retype_piece | f_L-1_022 | retype: display_cabinet is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Retype untyped drawn piece f_L-1_022 (5.54 x 0.60 m) as a display_cabinet to resolve the NR finding; the long narrow shape fits a display cabinet in a living room. |
| 19317 | 3 | retype_piece | f_L-1_022 | max_tries: f_L-1_022 was edited 3 times in this round | Retype untyped drawn piece f_L-1_022 (5.54 x 0.60 m) as a tall_cabinet to resolve the NR finding; the long narrow shape fits a tall storage unit in a living room. |
| 19324 | 3 | swap_model | f_L0_023 | asset_unusable: 3dwh_e41345920f4dce2514160e34 is not used: audit pending | Replace the flat-panel module wardrobe with a real 3.15m wardrobe model that has doors and handles, fixing a:F21 and c:LG:f_L0_023. |
| 19328 | 3 | swap_model | f_L0_023 | asset_unusable: abo_B015IPNVFW is not used: audit removed | Replace the flat-panel module wardrobe with an audited CC-BY 3.0m 6-door wardrobe that has doors and handles, fixing a:F21 and c:LG:f_L0_023. |
| 19330 | 3 | swap_model | f_L0_023 | asset_unusable: hssd_7094e30496b2735c235819e99c509769dc30502d is not used: audit removed | Replace the flat-panel module wardrobe with an audited CC-BY-NC 2.66m 6-door Calypso wardrobe that has doors and handles, fixing a:F21 and c:LG:f_L0_023. |
| 19338 | 3 | swap_model | f_L0_023 | max_tries: f_L0_023 was edited 3 times in this round | Replace the flat-panel module wardrobe with an audited CC-BY-NC 2.71m 3-door sliding wardrobe with mirror, fixing a:F21 and c:LG:f_L0_023. |
| 19351 | 3 | fix_fixture | f_L-1_025 | fixture_place: f_L-1_025: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_002) | Door d_L-1_002 swings into the washbasin on one hinge side; shift it up to 0.5 m to clear the swing. |
| 19354 | 3 | relayout_room | r_L1_teras | memory: the same edit was rejected in round 1: group checks: F8 f_L1_070: potted_plant stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) | Re-solve the balcony group so the terrace set is complete (seating pair plus plant) per finding a:N101; candidate 1 is the solver's best and its plant sits beside the table, not isolated. |
| 19368 | 3 | fix_fixture | f_L0_005 | fixture_place: f_L0_005: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_008) | Door d_L0_008 swings into the washbasin on one hinge side; let the solver nudge it up to 0.5 m out of the swing. |
| 20223 | 4 | swap_model | f_L0_013 | acceptance: pin_refused: f_L0_013: hssd_72807de315ae7f20a846e137cf5e755f909a398f: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The drawn 1.40 x 0.60 m shower is outside the product sizes of module:shower:bath_set; the 1.20 x 0.80 m model is the closest real product that fits the bay. (fixes a:F65) |
| 20224 | 4 | swap_model | f_L0_014 | acceptance: pin_refused: f_L0_014: hssd_9368052ddb2713527a9be87ab3483ffd1f2c2a65: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The 0.60 x 1.40 m drawn shower is within 30% of the real range, so fix_fixture was refused; the 0.80 x 1.23 m model is the closest real product that fits the bay and the room. (fixes a:F66) |
| 20227 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | group checks: F4 f_L1_098: armchair stands behind the back of f_L1_017, looking at it | Argus: The sofa's front zone is blocked by f_L1_017; a room re-layout will reposition the blocking piece or the sofa to clear the zone. (fixes a:F71) |
| 20228 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Argus: The sofa's front zone is blocked by f_L1_018; a room re-layout will fix the arrangement. (fixes a:F75) |
| 20230 | 4 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: The kitchen is missing its fridge; placing the kitchen_run group will add the missing member. (fixes a:F144) |
| 20231 | 4 | fix_fixture | f_L1_025 | fixture_size: f_L1_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The drawn 1.83 m tub is within 30% of the real range, so the size is right; the 0.28 m front clearance is a placement problem. fix_fixture without center moves it to the nearest valid spot. (fixes a:F161) |
| 20232 | 4 | fix_fixture | f_L1_022 | fixture_size: f_L1_022: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The drawn 0.50 x 0.69 m toilet is within 30% of the real range, so the size is right; the 0.33 m side clearance is a placement problem. fix_fixture without center moves it to the nearest valid spot. (fixes a:F162) |
| 20233 | 4 | fix_fixture | f_L1_026 | fixture_size: f_L1_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The drawn 1.83 m tub is within 30% of the real range, so the size is right; the 0.28 m front clearance is a placement problem. fix_fixture without center moves it to the nearest valid spot. (fixes a:F163) |
| 20234 | 4 | swap_model | f_L1_015 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The current module washbasin and the three gen_ washbasins all failed the height cap under the sloped ceiling. The 3dwh_9314d5619fde2de825a4a2a1 model is 0.39 m high, well under the 1.60 m cap, and fits the 1.00 x 0.55 m footprint. (fixes a:F164) |
| 20235 | 4 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | Argus: The room is 40.5 m2, furnished as a living room, and its twin is typed 'living'. The image labels it 'living'. The previous set_room_type was refused because of a bench (f_L1_035) that is not a piece of a living room; the bench should be re (fixes a:F165) |
| 20236 | 4 | correct_geometry | o_L1_001 | the opening already lies on the wall (0.000 m) | Argus: The opening o_L1_001 is not cut through its wall w_L1_003. correct_geometry with kind fix_opening_on_wall will put the opening back on its wall. (fixes a:F169) |
| 20237 | 4 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 1.90 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 20) is at z -0.40 m: use z 1.10 to 1.30 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: There is no frontal view of the entrance (+y) facade. add_camera with kind exterior and a position in front of the entrance will add the missing view. (fixes a:F172) |
| 20239 | 4 | set_entrance | d_L0_009 | exists: 'd_L0_009' is no outside door of site.entrances | Argus: The entrance door is set into a blank wall with no path or steps; set_entrance adds the steps that make the door reachable. (fixes a:F178) |
| 20240 | 4 | set_front | f_L1_035 | has_front: f_L1_035 faces 270° already: rotate_piece turns it | Argus: The check says the AI front (180 deg, short side) is a reading error and the correct front is 270 deg (back on the only wall side); retype was refused (bench is not a candidate), so set_front is the fix. (fixes a:F197) |
| 20241 | 4 | set_front | f_L1_037 | has_front: f_L1_037 faces 270° already: rotate_piece turns it | Argus: The check says the AI front (0 deg, short side) is a reading error and the correct front is 270 deg (back on the only wall side); retype was refused, so set_front is the fix. (fixes a:F198) |
| 20243 | 4 | swap_model | f_L0_038 | acceptance: pin_refused: f_L0_038: abo_B081HMS8YK: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The black leather office chair is a corporate piece that clashes with the warm, residential bedroom style; swapping to a modern minimal chair matches the bed and desk. (fixes a:F280) |
| 20244 | 4 | swap_model | f_L0_010 | acceptance: pin_refused: f_L0_010: abo_B07GFS1VB6: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The wardrobe is a raw, light wood that looks unfinished and clashes with the darker wood of the headboard and the grey walls; swapping to a scandinavian/modern minimal wardrobe with a refined finish matches the room's style. (fixes a:F284) |
| 20247 | 4 | swap_model | f_L1_017 | pin_refused: f_L1_017: gen_sofa_japandi_2_98a7a89b: a generated model (units guessed) while a real product of the type fits within the caps (abo_B072555T67): the real model stays; swap to a real model of the type or use another tool | Argus: The current sofa model is a blocky placeholder; swapping to a japandi/modern model fixes the style mismatch. (fixes a:F292) |
| 20248 | 4 | swap_model | f_L1_005 | no_change: f_L1_005 already uses the model abo_B07M6PKC6B | Argus: The current dining table is dark and traditional, clashing with the modern room; swapping to a scandinavian/minimal model fixes it. (fixes a:F293) |
| 20249 | 4 | swap_model | f_L1_020 | pin_refused: f_L1_020: gen_sofa_japandi_2_98a7a89b: a generated model (units guessed) while a real product of the type fits within the caps (abo_B072555T67): the real model stays; swap to a real model of the type or use another tool | Argus: The second sofa is a bare boxy model; swapping to the same japandi model as the first sofa creates a coherent set. (fixes a:F294) |
| 20252 | 4 | swap_model | f_L1_079 | acceptance: pin_refused: f_L1_079: 3dwh_040dd50cd138cbc316c9caec: fails the fit rules (caps, height, at most 0.93 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The chairs are white plastic garden chairs mismatched with the industrial table; swapping to modern/scandinavian chairs fixes the set. (fixes a:F303) |
| 20267 | 4 | set_camera | r_L0_banyo | cam_r_L0_banyo_2 is 0.35 m from the door d_L0_007 (at least 0.6 m) | Re-aim the corner close-up so the bathtub, washbasin and toilet are all in frame instead of a blank wall and the toilet paper roll. |
| 20271 | 4 | set_camera | r_L0_banyo | cam_r_L0_banyo_2 is 0.30 m from the door d_L0_007 (at least 0.6 m) | Re-aim from the far corner so the bathtub, washbasin and toilet are all in frame instead of a blank wall and the toilet paper roll. |
| 20272 | 4 | set_camera | r_L0_banyo | cam_r_L0_banyo_2 is 0.39 m from the door d_L0_007 (at least 0.6 m) | Re-aim from the far corner so the bathtub, washbasin and toilet are all in frame instead of a blank wall and the toilet paper roll. |
| 20273 | 4 | set_camera | r_L0_banyo | memory: the same edit was rejected in round 4: cam_r_L0_banyo_2 is 0.39 m from the door d_L0_007 (at least 0.6 m) | Re-aim from the far corner so the bathtub, washbasin and toilet are all in frame instead of a blank wall and the toilet paper roll. |
| 20275 | 4 | set_camera | r_L0_banyo | memory: the same edit was rejected in round 4: cam_r_L0_banyo_2 is 0.39 m from the door d_L0_007 (at least 0.6 m) | Re-aim from the far corner so the bathtub, washbasin and toilet are all in frame instead of a blank wall and the toilet paper roll. |

Rolled back (the refit refused them): #611 move_piece (locked check: f_L-1_065: moved 0.300 m by the agent (> 0.3 m)), #615 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0).

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
| M14 | major | dec_L1_028 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_030 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_034 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_051 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M18 | major | f_L-1_020 | r_L-1_koridor | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M18 | major | f_L0_002 | r_L0_merdiven_2 | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M21 | minor | r_L0_e_banyo_2 | r_L0_e_banyo_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo | r_L1_banyo | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo_2 | r_L1_banyo_2 | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_oyun_aktivite_ve_dinlenme_odasi | r_L1_oyun_aktivite_ve_dinlenme_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| Q3 | critical | r_L-1_koridor | r_L-1_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_koridor_2 | r_L-1_koridor_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_mutfak | r_L-1_mutfak | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_mutfak_2 | r_L-1_mutfak_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_salon | r_L-1_salon | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_salon_2 | r_L-1_salon_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q7 | minor | d_L0_001 | r_L0_koridor | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | minor | d_L0_005 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | major | w_L0_001 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | minor | w_L0_008 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q9 | major | d_L0_009 | - | site | entrance_layout | 4 | the landings, steps, ramps and handrails in front of the doors are laid out by code for all the entrances together (site.entrance_layout: doors whose steps would meet share one platform with one flight, a ramp and the handrails keep clear of the other doors); no agent tool moves them, so the finding is reported to the site stage |
| Q9 | major | w_L0_001 | - | site | entrance_layout | 4 | the landings, steps, ramps and handrails in front of the doors are laid out by code for all the entrances together (site.entrance_layout: doors whose steps would meet share one platform with one flight, a ramp and the handrails keep clear of the other doors); no agent tool moves them, so the finding is reported to the site stage |
| Q9 | major | w_L0_015 | - | site | entrance_layout | 4 | the landings, steps, ramps and handrails in front of the doors are laid out by code for all the entrances together (site.entrance_layout: doors whose steps would meet share one platform with one flight, a ramp and the handrails keep clear of the other doors); no agent tool moves them, so the finding is reported to the site stage |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_005 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 3 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_009 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | critical | dec_L0_011 | - | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L0_012 | - | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_028 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_030 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_034 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_051 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_050 | r_L-1_salon_2 | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_007 | r_L0_e_yatak_odasi | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_019 | r_L0_yatak_odasi | decor | decor_rest | 1, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_022 | r_L0_yatak_odasi_4 | decor | decor_rest | 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_056 | r_L0_koridor | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_051 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| X2 | critical | dec_L1_066 | r_L1_banyo | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X2 | critical | dec_L1_067 | r_L1_banyo | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X2 | critical | dec_L1_068 | r_L1_banyo | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X2 | critical | dec_L1_076 | r_L1_banyo_2 | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X2 | critical | dec_L1_077 | r_L1_banyo_2 | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X2 | critical | dec_L1_078 | r_L1_banyo_2 | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | facade | 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L-1_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L-1_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_006 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L1_002 | - | - | scale | 2, 3, 4 | storey and door sizes come from the drawings |
| lighting_dark | minor | cam_r_L-1_banyo_1 | r_L-1_banyo | - | lighting_within_step | 1, 2 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | minor | cam_r_L-1_banyo_2 | r_L-1_banyo | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | major | cam_r_L0_e_banyo_2 | r_L0_e_banyo | - | lighting_beyond_cap | 1, 2 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon | cut | 2 | 12220 | 32768 |
| 1 | r_L-1b_salon_2 | cut | 2 | 11282 | 32768 |
| 2 | r_L-1_salon_2 | cut | 2 | 22936 | 32768 |
| 2 | r_L-1b_salon | cut | 3 | 11093 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 3 | 17345 | 32768 |
| 3 | r_L-1b_salon_2 | cut | 5 | 21848 | 32768 |
| 3 | building | cut | 3 | 51592 | 32768 |

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
| f_L-1_027 | piece | table_dining | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge the dining table away from chairs f_L-1_028 and f_L-1_031 to clear the 0.038/0.039 m cuts (c:S2:f_L-1_027, c:S2:f_L-1_027#2). |
| f_L-1_028 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dining chairs are a chaotic mix of at least three different models. The piece f_L-1_028 is a chair with model abo_B0856G7YXQ. The model hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 is modern/scandinavian, 0.48 x 0.47 x 0.79 m, which fi (fixes a:F237) |
| f_L-1_031 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Dining chairs are a chaotic mix of models; give f_L-1_031 the same model as f_L-1_028 to unify the set (a:F237, a:F349). |
| f_L-1_042 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1_042 slightly to resolve the 0.034 m cut with table_dining f_L-1_038 (S2). |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The grey armchair clashes with the sofa. Swapping to a modern/neutral armchair of a similar footprint (0.93 x 0.84 m) makes the seating group cohesive. (fixes a:F410) |
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
| f_L-1_063 | piece | floor_lamp | r_L-1_salon | adjusted_by_ai | size 0.59 x 0.59 m -> 0.40 x 0.40 m | Qwen/Qwen3.8-27B-FP8 | Move the floor lamp 0.3 m away from the window wall so it no longer blocks window win_L-1_001 (G12). |
| f_L-1_064 | piece | floor_lamp | r_L-1_salon | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays, f_L-1_064 is not built (plan crop recognition/crops/sym_L-1_012_ctx.png) |
| f_L-1_065 | piece | floor_lamp | r_L-1_salon_2 | adjusted_by_ai | size 0.59 x 0.59 m -> 0.40 x 0.40 m | code (size_snap) | size snap: the drawn floor lamp 0.59 x 0.59 m is a plan symbol larger than the product (a floor lamp takes at most 0.45 m from above): fitted at the real product 0.40 x 0.40 m, centred where it is drawn (CLAUDE.md: a drawn size outside its type's real product range is snapped to a real product before the fit; user, 29 Oct 2026: "I did not like this light", lesson UL94) |
| f_L-1_066 | piece | floor_lamp | r_L-1_salon_2 | inferred, adjusted_by_ai | - | code (furniture.infer.duplicate_symbols) | floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays, f_L-1_066 is not built (plan crop recognition/crops/sym_L-1_014_ctx.png) |
| f_L-1_069 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Argus: A 0.12 m offset and a size mismatch are outside the 0.05 m tolerance; swapping to a model with a closer footprint reduces the offset and improves the match to the drawing. (fixes a:F351) |
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Argus: The armchair is a bulky, dark brown piece that clashes with the light, minimalist sofa. The tried rotate_piece was refused (plausibility dropped) and swap_model was refused for 3dwh_49c89838e523cdc64ffa7de1 (audit removed). The model hssd_0 (fixes a:F233) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Give f_L-1_071 the same light armchair model as f_L-1_070 so the pair matches the drawing and the seating set (a:F353). |
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
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size 2.55 x 2.00 m -> 1.60 x 2.00 m | Qwen/Qwen3.8-27B-FP8 | Replace the flat white slab bed with a modern upholstered bed that carries pillows, duvet and throw, addressing the missing bedding layers (D3) and the missing throw (M30). |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
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
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | Qwen/Qwen3.8-27B-FP8 (reading.desk_chair) | Argus: The plain white boxy desk gives an office feel. Swapping to a minimal/modern/scandinavian desk of the same footprint (1.45 x 0.69 m) adds warmth and detail. (fixes a:F411) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png); then: the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.01 m |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.05 m |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift nightstand away from bed edge to clear the 0.06 m² overlap and satisfy the ≤ 0.30 m gap requirement. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_005 | piece | table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (anchor); moved 0.32 m |
| f_L1_006 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.14 m |
| f_L1_007 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.10 m |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Sofa f_L1_019's free zone in front is blocked by f_L1_018; shift it 0.29 m toward the north wall to open the clearance. |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The coffee table is a generic block that clashes with the modern dining set. The current model hssd_7025cd14a948f491902ef12724f0fe6e4ce672af is the one to replace; abo_B07K7M4YT4 (1.10 x 0.69 x 0.44 m, minimal/modern/scandinavian) fits the  (fixes a:F261) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_025 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Armchair f_L1_032 is 2.73 m from the coffee table f_L1_024 (needs ≤ 2.50 m); shift it 0.3 m toward the table to close the gap. (plan crop recognition/crops/sym_L1_010_ctx.png) |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Retype the drawn bench to a console table, which fits its 1.40 x 0.45 m footprint and a living room, resolving F1/G14. (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: the same footprint (1.09 x 0.40 m) as f_L1_038 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (mirrored centre within 0.02 m) |
| f_L1_037 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Bench f_L1_037 is not a piece of a living room; retype it to a console_table which fits its 1.4 x 0.45 m size and the living room zone. (plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black high-back office chair is a corporate piece that clashes with the light wood, blue and neutral palette of the bedroom. (fixes a:F249) (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black mesh office chair is a corporate item that clashes with the soft, residential style of the bedroom. (fixes a:F248) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_040 | piece | shoe_cabinet | r_L0_koridor_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_040: the piece is not built |
| f_L-1_094 | piece | shoe_cabinet | r_L-1_koridor_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the generic blocky grey shoe cabinet with a modern minimal shoe cubby for a cohesive, stylish entrance. |
| f_L1_054 | piece | bookshelf | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_054: the piece is not built |
| f_L0_053 | piece | bench | r_L0_e_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dark, heavy wood bench clashes with the light, upholstered bed and light-wood nightstand; swapping to a japandi/modern minimal bench of the same footprint (1.20 x 0.40 m) matches the room's style. (fixes a:F274) |
| f_L1_078 | piece | table_dining | r_L1_teras | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The table f_L1_078 is a heavy, indoor-style dining table. It is not appropriate for an outdoor terrace. The abo_B07ML7P94G model is a lighter, scandinavian/japandi/minimal/modern/rustic table that is more suitable for outdoor use. (fixes a:F176) |
| f_L1_081 | piece | potted_plant | r_L1_teras | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current potted plant is a crude low-poly clump; swapping to a more realistic model fixes it. (fixes a:F301) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_2 | ![](agent/r1_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_2_after.jpg) |
| 1 | cam_r_L-1_koridor_2_1 | ![](agent/r1_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r1_cam_r_L-1_koridor_2_1_after.jpg) |
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
| 3 | cam_r_L-1_koridor_2_1 | ![](agent/r3_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r3_cam_r_L-1_koridor_2_1_after.jpg) |
| 3 | cam_r_L-1_salon_1 | ![](agent/r3_cam_r_L-1_salon_1_before.jpg) | ![](agent/r3_cam_r_L-1_salon_1_after.jpg) |
| 3 | cam_r_L-1_salon_2 | ![](agent/r3_cam_r_L-1_salon_2_before.jpg) | ![](agent/r3_cam_r_L-1_salon_2_after.jpg) |
| 3 | cam_r_L-1_salon_3 | ![](agent/r3_cam_r_L-1_salon_3_before.jpg) | ![](agent/r3_cam_r_L-1_salon_3_after.jpg) |
| 3 | cam_r_L0_koridor_1 | ![](agent/r3_cam_r_L0_koridor_1_before.jpg) | ![](agent/r3_cam_r_L0_koridor_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_1 | ![](agent/r3_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_2 | ![](agent/r3_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L1_banyo_1 | ![](agent/r3_cam_r_L1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L1_banyo_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 3 | cam_r_L1_teras_1 | ![](agent/r3_cam_r_L1_teras_1_before.jpg) | ![](agent/r3_cam_r_L1_teras_1_after.jpg) |
| 3 | cam_r_L1_teras_2 | ![](agent/r3_cam_r_L1_teras_2_before.jpg) | ![](agent/r3_cam_r_L1_teras_2_after.jpg) |
| 3 | cam_r_L1_teras_3 | ![](agent/r3_cam_r_L1_teras_3_before.jpg) | ![](agent/r3_cam_r_L1_teras_3_after.jpg) |
| 4 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r4_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 4 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r4_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r4_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 4 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r4_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r4_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 4 | cam_r_L0_koridor_1 | ![](agent/r4_cam_r_L0_koridor_1_before.jpg) | ![](agent/r4_cam_r_L0_koridor_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r4_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r4_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r4_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 4 | cam_r_L1_banyo_1 | ![](agent/r4_cam_r_L1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L1_banyo_1_after.jpg) |
| 4 | cam_r_L1_koridor_1 | ![](agent/r4_cam_r_L1_koridor_1_before.jpg) | ![](agent/r4_cam_r_L1_koridor_1_after.jpg) |
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
- final/cam_r_L-1_koridor_2_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L-1_koridor_2_2_final_preview.jpg
- final/cam_r_L1_koridor_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_final_preview.jpg
- final/cam_r_L-1_koridor_2_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L-1_koridor_2_2_plan.jpg
- final/cam_r_L1_koridor_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_koridor_2_plan.jpg
- final/top_L-1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L-1_plan_2.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_2.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_2.jpg
