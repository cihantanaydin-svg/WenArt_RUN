# Final report: real04

35 views: 0 polished, 35 Cycles (error 11, gate_validation 5, not_run 2, room 17). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 35 |
| interior / exterior views | 30 / 5 |
| variant | base |
| polished | 0 |
| Cycles | 35 (error 11, gate_validation 5, not_run 2, room 17) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 27 |
| needs_review views | 14 |
| unverified pieces in view (sum over views) | 45 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.67 .. +3.00 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 23 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 9, m5 5, search 21 |
| camera score (min / mean / max) | 0.09 / 3.62 / 4.69 |
| rooms by number of views | 1 with 0, 5 with 1, 2 with 2, 7 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 7.5 min / 6.6 min / 95.8 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 41.4 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 15 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 900.6 MB |
| [real04.glb](3d/real04.glb) | 1970.0 MB |

35 cameras; textures scaled to at most 1024 px (417 scaled) for the download.

## AI decor

162 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 35 rooms; 383 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- camera cam_r_L1_banyo_1: no free camera point in the room; camera at the room's inner point; moved to the nearest point with 0.3 m of headroom under the sloped ceiling (1.55 m high there); blocked unavoidable
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 21 piece(s) moved beyond the tolerance, 69 locked-rule violation(s)
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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.50 | - | agent | D3 A3 | 1 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.83 | - | agent | D2 A2 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.00 | -3 | search 4.61 | D5 A2 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.50 | -1 | search 4.50 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.17 | -3 | search 3.75 | D5 A1 | 0 | yes | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.65 | D9 A7 | 3 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.48 | D11 A7 | 2 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.17 | -4 | search 3.63 | D8 A6 | 4 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.67 | - | agent | D2 A4 | 0 | yes | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | agent | D2 A1 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.83 | - | agent | D2 A4 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +3.00 | - | search 0.09 | D2 A2 | 1 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.17 | -1 | search 4.66 | D5 A8 | 0 | yes | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.50 | 0 | search 4.62 | D7 A6 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.67 | -4 | search 4.56 | D3 A7 | 0 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.83 | - | agent | A1 | 0 | no | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.83 | -4 | agent | D4 A7 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.83 | - | search 4.02 | D4 A3 | 2 | yes | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.67 | -4 | search 4.53 | D3 A7 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +0.83 | -3 | search 4.69 | D3 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.33 | -3 | search 4.44 | D7 A2 | 4 | yes | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 4.53 | D4 A5 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.33 | - | search 1.19 blocked | D2 A2 | 0 | yes | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.33 | - | agent | D3 A1 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.67 | - | agent | D6 A4 | 4 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.33 | - | search 3.70 | D7 A1 | 2 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.17 | -2 | search 3.88 | D11 A3 | 3 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.50 | 0 | search 3.21 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.67 | 0 | search 1.57 | D1 A5 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.50 | 0 | search 2.72 | D1 A5 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.17 | 0 | m5 blocked | D7 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D7 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 blocked | D4 | 1 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.67 | 0 | m5 | D10 | 1 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 | D6 | 1 | yes | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1_banyo | bathroom | L-1 | 1 | 0 | 1 | cam_r_L-1_banyo_1 |
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
| cam_r_L-1_mutfak_3 | cycles | cross-check misplaced | d_L-1_003 | door | - | from_documents | deneme1.dwg INSERT:365E2/1,INSERT:365E2/0 vector 0.95 | yes | 100 % of its pixels > 0.10 m outside the drawing, 75023 px |
| cam_r_L0_banyo_1 | cycles | cross-check misplaced | d_L0_007 | door | - | from_documents | deneme1.dwg INSERT:2DDDE/1,INSERT:2DDDE/0 vector 0.95 | yes | 36 % of its pixels > 0.10 m outside the drawing, 223777 px |
| cam_r_L0_e_yatak_odasi_1 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 23 % of its pixels > 0.10 m outside the drawing, 555887 px |
| cam_r_L0_e_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 65 % of its pixels > 0.10 m outside the drawing, 56249 px |
| cam_r_L0_e_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_002 | door | - | from_documents | deneme1.dwg INSERT:2DDF1/1,INSERT:2DDF1/0,LWPOLYLINE:2DDF5 vector 0.95 | yes | 41 % of its pixels > 0.10 m outside the drawing, 85776 px |
| cam_r_L0_e_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 52 % of its pixels > 0.10 m outside the drawing, 33693 px |
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_007 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDFA/10,INSERT:2DDFA/11,INSERT:2DDFA/12,INSERT:2DDFA/13,INSERT:2DDFA/14,INSERT:2DDFA/15,INSERT:2DDFA/16,INSERT:2DDFA/17,INSERT:2DDFA/18,INSERT:2DDFA/19,INSERT:2DDFA/2,INSERT:2DDFA/20,INSERT:2DDFA/21,INSERT:2DDFA/22,INSERT:2DDFA/23,INSERT:2DDFA/24,INSERT:2DDFA/25,INSERT:2DDFA/26,INSERT:2DDFA/27,INSERT:2DDFA/28,INSERT:2DDFA/29,INSERT:2DDFA/30,INSERT:2DDFA/31,INSERT:2DDFA/32,INSERT:2DDFA/33,INSERT:2DDFA/4,INSERT:2DDFA/5,INSERT:2DDFA/6,INSERT:2DDFA/7,INSERT:2DDFA/8,INSERT:2DDFA/9 YATAK vector 0.90 | yes | 20 % of its pixels > 0.10 m outside the drawing, 642333 px |
| cam_r_L0_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 70 % of its pixels > 0.10 m outside the drawing, 113659 px |
| cam_r_L0_yatak_odasi_3_2 | cycles | cross-check misplaced | d_L0_006 | door | - | from_documents | deneme1.dwg INSERT:2DDE5/1,INSERT:2DDE5/0,LWPOLYLINE:2DE07 vector 0.95 | yes | 64 % of its pixels > 0.10 m outside the drawing, 244951 px |
| cam_r_L1_banyo_1 | cycles | cross-check misplaced | d_L1_004 | door | - | from_documents | deneme1.dwg INSERT:2F799/1,INSERT:2F799/0 vector 0.95; dormers inferred 0.70 | yes | 75 % of its pixels > 0.10 m outside the drawing, 427608 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 48 % of its pixels > 0.10 m outside the drawing, 90519 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 62 % of its pixels > 0.10 m outside the drawing, 27900 px |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 22 % of its pixels > 0.10 m outside the drawing, 44195 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 16 % of its pixels > 0.10 m outside the drawing, 5636 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 21 % of its pixels > 0.10 m outside the drawing, 46968 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 15 % of its pixels > 0.10 m outside the drawing, 5723 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 32 % of its pixels > 0.10 m outside the drawing, 41012 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90; building.json inferred 0.70 | yes | 27 % of its pixels > 0.10 m outside the drawing, 10328 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 71 % of its pixels > 0.10 m outside the drawing, 13052 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 65 % of its pixels > 0.10 m outside the drawing, 10069 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3109 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 1849 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 7116 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 1885 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 3113 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90; building.json inferred 0.70 | yes | 47 % of its pixels > 0.10 m outside the drawing, 14496 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12221 px |

## Needs review

- cam_r_L-1_mutfak_3: json cross-check misplaced: d_L-1_003
- cam_r_L0_banyo_1: json cross-check misplaced: d_L0_007
- cam_r_L0_e_yatak_odasi_1: json cross-check misplaced: f_L0_007
- cam_r_L0_e_yatak_odasi_2: json cross-check misplaced: d_L0_001; json cross-check misplaced: d_L0_002; json cross-check misplaced: d_L0_005
- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: f_L0_007
- cam_r_L0_yatak_odasi_2: json cross-check misplaced: d_L0_005
- cam_r_L0_yatak_odasi_3_2: json cross-check misplaced: d_L0_006
- cam_r_L1_banyo_1: json cross-check misplaced: d_L1_004
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

- cam_r_L-1_banyo_1: f_L-1_056
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_087
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_071
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061, f_L-1_071, f_L-1_087
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_banyo_2: f_L0_013
- cam_r_L0_e_yatak_odasi_2: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030
- cam_r_L0_yatak_odasi_3_1: f_L0_021, f_L0_029, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_023, f_L1_030, f_L1_031, f_L1_035
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_035, f_L1_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_023, f_L1_035, f_L1_036
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
| f_L1_010 | furniture | ottoman | 3dwh_3c7789b0688d2438ea319f73 | the vision check sees more than one object |
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

0 change(s) applied, 39 piece(s) added, 12 wall cabinet run(s).

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

- added f_L-1b_071: table_coffee 1.20 x 0.70 (confidence -, rule)
- added f_L-1b_072: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L-1b_073: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_074: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L-1b_075: ottoman 0.50 x 0.50 (confidence -, rule)
- added f_L-1b_076: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_009, f_L-1b_010, f_L-1b_012, f_L-1b_013, f_L-1b_014, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_032, f_L-1b_033, f_L-1b_034, f_L-1b_040, f_L-1b_042, f_L-1b_046, f_L-1b_049, f_L-1b_050, f_L-1b_051, f_L-1b_052, f_L-1b_056, f_L-1b_060, f_L-1b_062

### Salon (r_L-1b_salon_2, living): completed (partner r_L-1b_salon (twin) not used: 2 of 6 copied pieces fail a check here (ottoman: the copy fails clearance_ok here; table_coffee: the copy fails clearance_ok here); completed itself)

- added f_L-1b_081: table_coffee 1.20 x 0.70 (confidence -, rule)
- added f_L-1b_082: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L-1b_083: potted_plant 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_084: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L-1b_085: side_table 0.45 x 0.45 (confidence -, rule)
- added f_L-1b_086: fridge 0.60 x 0.60 (confidence -, rule)
- 3 wall cabinet run(s) over the drawn counter
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_003, f_L-1b_004, f_L-1b_006, f_L-1b_007, f_L-1b_008, f_L-1b_017, f_L-1b_018, f_L-1b_019, f_L-1b_020, f_L-1b_021, f_L-1b_022, f_L-1b_023, f_L-1b_024, f_L-1b_025, f_L-1b_039, f_L-1b_041, f_L-1b_045, f_L-1b_047, f_L-1b_048, f_L-1b_053, f_L-1b_054, f_L-1b_055, f_L-1b_059, f_L-1b_061

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_080: console_table 0.90 x 0.30 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_016

### Koridor (r_L-1b_koridor_2, hall): completed (partner r_L-1b_koridor (twin) not used: the twin's drawn furniture does not map onto this room: drawn stair f_L-1b_016 has no counterpart here; completed itself)

- added f_L-1b_090: console_table 0.90 x 0.30 (confidence -, rule)
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

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 143 ok, 21 failed; 62 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_031 | chair (chair) | 0.14 | 0.00 | - | - |
| f_L-1_063 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_065 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.23 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.23 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.23 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.60 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L0_009 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_010 | wardrobe (wardrobe) | 0.72 | 0.00 | yes | - |
| f_L0_011 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_014 | shower (shower) | 0.76 | 90.00 | no | no longer against wall w_L0_002 (now centre None) |
| f_L0_032 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.16 | 0.00 | yes | - |
| f_L1_005 | table_dining (table_dining) | 0.28 | - | - | - |
| f_L1_006 | chair (chair) | 0.25 | 0.00 | - | - |
| f_L1_007 | chair (chair) | 0.28 | 90.00 | - | - |
| f_L1_010 | ottoman (chair) | 0.28 | 0.00 | - | - |
| f_L1_019 | sofa (sofa) | 0.30 | 0.00 | - | - |
| f_L1_032 | armchair (armchair) | 0.30 | 0.00 | - | - |

Locked-rule violations:

- walls: must stay as drawn (byte-equal): removed w_L-1b_001, w_L-1b_002, w_L-1b_003, w_L-1b_004, w_L-1b_005, w_L-1b_006, w_L-1b_007, w_L-1b_008, w_L-1b_009, w_L-1b_010, w_L-1b_011, w_L-1b_012, w_L-1b_013
- openings: must stay as drawn (byte-equal): changed d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_005, d_L0_006, d_L0_007, d_L0_008, d_L0_009, d_L0_010, d_L0_011, d_L0_012, d_L1_001, d_L1_002, d_L1_003, d_L1_004, d_L1_005, d_L1_006, win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L1_001, win_L1_002; removed d_L-1b_001, d_L-1b_002, d_L-1b_003, d_L-1b_004, o_L-1b_001, o_L-1b_002, win_L-1b_001, win_L-1b_002; added win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1
- rooms: must stay as drawn (byte-equal): changed r_L-1_salon, r_L-1_salon_2, r_L0_e_yatak_odasi, r_L0_e_yatak_odasi_2, r_L0_yatak_odasi, r_L0_yatak_odasi_2, r_L0_yatak_odasi_3, r_L0_yatak_odasi_4, r_L1_oyun_aktivite_ve_dinlenme_odasi, r_L1_oyun_aktivite_ve_dinlenme_odasi_2; removed r_L-1b_banyo, r_L-1b_banyo_2, r_L-1b_koridor, r_L-1b_koridor_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_salon, r_L-1b_salon_2
- f_L-1_073: moved 0.598 m by the agent (> 0.3 m)
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
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: unverified | yes |
| ext_7 | aerial | - | - | cycles (gate_validation) | ok | right: unverified | yes |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_4 | corner | left, back | 12.5 m from the building corner, 30 degrees off the back facade: 81% of the view of the building is blocked by trees, the plot wall or another building; 14.5 m from the building corner, 30 degrees off the back facade: 75% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m from the building corner, 30 degrees off the back facade: 57% of the view of the building is blocked by trees, the plot wall or another building; 11.0 m from the building corner, 30 degrees off the back facade: 87% of the view of the building is blocked by trees, the plot wall or another building; 18.5 m from the building corner, 30 degrees off the back facade: 48% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m from the building corner, 30 degrees off the back facade: the building fills 6% of the frame (< 8%); 24.5 m from the building corner, 30 degrees off the back facade: 36% of the view of the building is blocked by trees, the plot wall or another building |
| ext_6 | frontal | back | 17.5 m in front of the back (entrance) facade: inside the copy; 19.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 16.0 m in front of the back (entrance) facade: inside the copy; 23.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 26.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 29.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | - | agent | no | agent override (docs/milestone11.md §17.3) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | dark_bronze | - | style | no | style profile exterior.window_frame |
| door | wood_oak_light | - | fallback | yes | style profile exterior.door (assumed) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | paving_stone | - | agent | no | agent override (docs/milestone11.md §17.3) |
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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_koridor_2_1, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 35 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_teras_2 | 0 / 20 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

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
| f_L1_035 | r_L1_oyun_aktivite_ve_dinlenme_odasi | bench | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bench, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.80 |
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
- door height 1,71 m: 2 opening(s) (d_L1_003, d_L1_006)
- door height 1,80 m: 2 opening(s) (d_L1_001, d_L1_002)
- door height 2,10 m: 15 opening(s) (d_L-1_001, d_L-1_002, d_L0_001, d_L0_002, d_L0_003, d_L0_004 ...)
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
| apron:apron_L-1_1 | 1 | the paved strip at the foot of the glazed facade runs its whole glazing run (win_L-1_001, win_L-1_002): 7.06 m on from the light well of win_L-1_002, 0.8 m deep, on the ground (lesson UL142; inferred) | site |
| area_light | 1 | r_L-1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo |
| area_light | 1 | r_L-1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo_2 |
| area_light | 1 | r_L-1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor |
| area_light | 1 | r_L-1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor_2 |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
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
| bath_details | 14 | the bathroom details of the piece (UL114, UL123, UL124: LED strips, a flush plate, towels and toiletries, shower fittings) inside its own box, one mesh | furn_f_L-1_051, furn_f_L-1_052, furn_f_L-1_103 |
| bath_items | 8 | the floating vanity's styling (UL114 B3, UL123 B19): part of its one mesh | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| bay_lights | 2 | an LED strip at the top of every bay lights the contents so they read through the see-through front (UL135; a wardrobe LED profile, 800 lm per metre (UL135)) | furn_f_L0_023, furn_f_L0_024 |
| bedding | 2 | its cover is flat (relief 110 mm, 5230 vertices/m2 on top: under 6 mm or 50; 26% of the middle on the top: under 50%): poorer than our duvet; a washed greige linen duvet under a crisp white sheet, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photos' set) | dress_f_L0_007, dress_f_L0_008 |
| bedding | 2 | its duvet has folds (relief 70 mm) but no pillows (bump 0.00 m < 0.06 m at the head): our pillow set on it, its duvet kept; a washed greige linen duvet under a crisp white sheet, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photos' set) | dress_f_L0_019, dress_f_L0_020 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); a washed greige linen duvet under a crisp white sheet, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photos' set) | dress_f_L0_022 |
| built_in | 1 | no built-in run here: neither end stands against a wall (gaps 0.73 m, 0.84 m): a built-in goes from wall to wall or from a wall, never floats mid-wall; the fit's free-standing wardrobe stays | furn_f_L0_010 |
| built_in | 1 | the house has 2 of its 2 rooms of built-in runs (r_L0_e_yatak_odasi, r_L0_e_yatak_odasi_2) and this room's unit needs 1: a free-standing wardrobe (a built-in is an option for some rooms, not every bedroom's) | furn_f_L0_012 |
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
| door_frame | 18 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1, 1] | d_L-1_001, d_L-1_002, d_L-1_003 |
| door_frame | 1 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1] | d_L0_011 |
| door_handles | 2 | design detail of the documented glazed door (black handles on both faces and 3 hinges); not in the documents | d_L1_003_handle, d_L1_006_handle |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; glazed: door d_L1_003 opens from r_L1_koridor to the open-air r_L1_teras: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_003 |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; glazed: door d_L1_006 opens from r_L1_koridor_2 to the open-air r_L1_teras_2: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_006 |
| door_size | 2 | D5 door sizes by role and family (day door, modern style): a full-height door to the ceiling between day rooms (modern style): 2.85 m high | d_L-1_003, d_L-1_004 |
| door_size | 2 | D5 door sizes by role and family (day door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size); a full-height door to the ceiling between day rooms (modern style): 1.80 m, its head room under the sloped ceiling at its wall | d_L1_001, d_L1_002 |
| door_size | 1 | D5 door sizes by role and family (entrance door, modern style): an entrance at least an entrance door set wide (1.00 m, a pivot door; drawn 0.82 m); a pivot entrance door: 2.40 m high | d_L0_011 |
| door_size | 2 | D5 door sizes by role and family (inside door, modern style): the nearest door set width 0.80 m (drawn 0.78 m: no product size) | d_L0_006, d_L0_010 |
| door_size | 4 | D5 door sizes by role and family (inside door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L0_001, d_L0_004, d_L0_005 |
| door_size | 8 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L-1_001, d_L-1_002, d_L0_002 |
| dormer | 1 | a shed dormer over the drawn door d_L1_004 (d_L1_004: the roof leaves it 1.00 m of head room (a door needs 1.60 m at least) and no spot within 0.5 m along its wall leaves more): the drawn opening is source evidence that it fits at its full height, the roof is inferred; 1.84 m wide, 3.57 m deep, a flat roof, its front on the facade (the facade wall rises to it), its ceiling 2.17 m over the floor at the opening (rule of 31 Oct 2026: a drawn door under the roof gets a dormer, never a hatch) | dormer_d_L1_004 |
| dormer | 1 | a shed dormer over the drawn door d_L1_005 (d_L1_005: the roof leaves it 1.00 m of head room (a door needs 1.60 m at least) and no spot within 0.5 m along its wall leaves more): the drawn opening is source evidence that it fits at its full height, the roof is inferred; 1.84 m wide, 3.57 m deep, a flat roof, its front on the facade (the facade wall rises to it), its ceiling 2.17 m over the floor at the opening (rule of 31 Oct 2026: a drawn door under the roof gets a dormer, never a hatch) | dormer_d_L1_005 |
| dormer_looks | 2 | a low-pitched or flat dormer roof clad in standing-seam metal (tiles need a steeper fall; not drawn); the dormer's cheeks and front in the house's facade look; the dormer's flashings along its cheeks and its back (not drawn) | dormer_d_L1_004, dormer_d_L1_005 |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
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
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.76 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_003, d_L1_006 |
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.85 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_001, d_L1_002 |
| height | 6 | no height in the JSON; type height for armchair | furn_f_L-1_049, furn_f_L-1_050, furn_f_L-1_069 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L0_007, furn_f_L0_008 |
| height | 2 | no height in the JSON; type height for bench | furn_f_L1_035, furn_f_L1_037 |
| height | 23 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L-1_058, furn_f_L-1_060, furn_f_L-1_063 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 4 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_035, furn_f_L0_036, furn_f_L0_037 |
| height | 1 | no height in the JSON; type height for ottoman | furn_f_L1_010 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_013, furn_f_L0_014 |
| height | 2 | no height in the JSON; type height for sideboard | furn_f_L1_064, furn_f_L1_070 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 3 | no height in the JSON; type height for tv_unit | furn_f_L-1_101, furn_f_L-1_102, furn_f_L1_069 |
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
| level | 1 | parking spk_001: one level at +0.80 m (level marks lm_001, lm_003, lm_006, lm_012, lm_016); ground -3.53..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred); no kerb along 46.0 m of its edges where another surface abuts it (its wall, coping or paving is the edge there; inferred) | platform_spk_001 |
| level | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 1.06 m up), 5 (1 x 1.16 m down), 6 (1 x 1.16 m down), 7 (2 x 1.16 m down), 8 (2 x 1.16 m down), 9 (1 x 1.16 m down), 10 (1 x 1.16 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); a flight of 1 risers of 0.068 m, tread 0.45 m down 0.07 m from edge 4 to the ground at its foot (the count settled on the ground the last riser lands on); one low step under the outdoor minimum riser, no cheek walls, a landing at its foot open on every side (inferred); its retaining wall stops at the building on edge 2 (0.00-0.27 m) (never through the house's wall, UL148) | platform_sp_001 |
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
| level | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 1 steps up out of it on edge 13 (0.17 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0); its retaining wall stops at the building on edge 5 (1.73-1.99 m) (never through the house's wall, UL148) | platform_sp_002 |
| level | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | platform_sp_002_s1e4 |
| level | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 1 (0.84-1.20 m) (never through the house's wall, UL148) | platform_sp_002_s1e5 |
| level | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | platform_sp_002_s2e4 |
| level | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | platform_sp_002_s2e5 |
| level | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 3 steps up out of it on edge 13 (0.34 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | platform_sp_003 |
| level | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); its retaining wall stops at the building on edge 2 (0.00-0.17 m) (never through the house's wall, UL148) | platform_sp_004 |
| level | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | platform_sp_004_s1e11 |
| level | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | platform_sp_004_s1e6 |
| level | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | platform_sp_004_s1e7 |
| level | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | platform_sp_004_s1e8 |
| level | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | platform_sp_004_s2e7 |
| library_model | 1 | library door 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.82 x 2.10 m (proportions off by 12 %; the documents draw the opening, not its product); the building's one door family; another family than the entrance's; modern look: audited styles ['modern'] name modern; its leaf not seen by the audit's opening question: after the doors it saw; frames in the style's finish | d_L0_012 |
| library_model | 1 | library entrance hssd_4141-3 ('HSSD door 4141-3 (0.91 x 2.13 m)') in 1 panel(s) of 1.00 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one entrance family; modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | d_L0_011 |
| library_model | 14 | library inside door hssd_200-5 ('HSSD door 200-5 (0.81 x 2.20 m)') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_001, d_L-1_002, d_L0_001 |
| library_model | 2 | library inside door hssd_204-6 ('HSSD door 204-6 (0.93 x 2.20 m)') in 1 panel(s) of 0.80 x 1.80 m (proportions off by 6 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L1_001, d_L1_002 |
| library_model | 2 | library inside door hssd_204-7 ('HSSD door 204-7 (0.86 x 2.40 m)') in 1 panel(s) of 0.81 x 2.85 m (proportions off by 26 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_003, d_L-1_004 |
| library_model | 2 | library window hssd_3758-4 ('HSSD window 3758-4 (1.18 x 2.03 m)') in 4 panel(s) of 0.67 x 1.20 m (proportions off by 4 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1 |
| library_model | 1 | library window hssd_3758-4 ('HSSD window 3758-4 (1.18 x 2.03 m)') in 5 panel(s) of 1.39 x 2.40 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | win_L-1_002 |
| library_model | 1 | library window hssd_3758-4 ('HSSD window 3758-4 (1.18 x 2.03 m)') in 5 panel(s) of 1.44 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | win_L-1_001 |
| library_model | 2 | library window hssd_3758-4 ('HSSD window 3758-4 (1.18 x 2.03 m)') in 6 panel(s) of 0.69 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['industrial', 'modern'] name modern; frames in the style's finish | win_L-1_003, win_L-1_004 |
| library_model | 2 | library window hssd_3758-5 ('HSSD window 3758-5 (0.95 x 2.03 m)') in 2 panel(s) of 1.08 x 2.55 m (proportions off by 10 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_002, win_L0_003 |
| library_model | 2 | library window hssd_3758-5 ('HSSD window 3758-5 (0.95 x 2.03 m)') in 2 panel(s) of 1.31 x 2.55 m (proportions off by 10 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_001, win_L0_004 |
| light_well:win_L-1_002 | 1 | window sill -2.80 m, ground outside -2.84 m: an open concrete light well 0.8 m deep, 7.33 m wide (no light well drawn) | site |
| light_well:win_L-1_003 | 1 | the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well | site |
| light_well:win_L-1_004 | 1 | the terrace sp_002 at -3.00 m lies under the sill -2.10 m: no light well | site |
| modules | 32 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| parapet | 1 | roof terrace ro_001: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| parapet_height:ro_002 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| passage_lining | 3 | design detail of the documented passage: a lined reveal (jambs and head lining in the trim), no architrave (UL122); not in the documents | o_L0_001_lining, o_L0_002_lining, o_L1_001_lining |
| path:d_L0_011 | 1 | a paved path from the entrance to the front of building copy 1 (it never runs into a building) (inferred) | site |
| path:d_L0_012 | 1 | a paved path from the entrance to the front of building copy 1 (it never runs into a building) (inferred) | site |
| path_grading | 1 | a sloped walk: 0.0 % along (at most 1:12), laid level across (0.3 % of cross fall taken by its edges; inferred) | path_access_spk_001_c0 |
| path_grading | 1 | a sloped walk: 0.0 % along (at most 1:12), laid level across (37.4 % of cross fall taken by its edges; inferred) | path_access_sp_001_c0 |
| path_grading | 1 | a sloped walk: 3.2 % along (at most 1:12), laid level across (41.6 % of cross fall taken by its edges; inferred) | path_access_sp_002_0 |
| path_grading | 1 | a stepped path: 12 % along is steeper than 1:12, so 2 risers of 0.078 m in 1 flight(s) (2) with level landings, treads 0.42 m, level across, stone step edges (inferred) | path_d_L0_011 |
| path_grading | 1 | a stepped path: 13 % along is steeper than 1:12, so 2 risers of 0.087 m in 1 flight(s) (2) with level landings, treads 0.41 m, level across, stone step edges (inferred) | path_access_spk_001_1 |
| path_grading | 1 | a stepped path: 17 % along is steeper than 1:12, so 2 risers of 0.135 m in 1 flight(s) (2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_012 |
| path_grading | 1 | a stepped path: 27 % along is steeper than 1:12, so 3 risers of 0.129 m in 1 flight(s) (3) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_sp_004_0 |
| path_grading | 1 | a stepped path: 32 % along is steeper than 1:12, so 3 risers of 0.107 m in 1 flight(s) (3) with level landings, treads 0.37 m, level across, stone step edges (inferred) | path_access_sp_003_0 |
| path_grading | 1 | a stepped path: 36 % along is steeper than 1:12, so 3 risers of 0.111 m in 1 flight(s) (3) with level landings, treads 0.36 m, level across, stone step edges (inferred) | path_access_sp_001_0 |
| path_grading | 1 | a stepped path: 86 % along is steeper than 1:12, so 18 risers of 0.144 m in 2 flight(s) (9/9) with level landings, treads 0.30 m, level across, stone step edges; a handrail on the flights over 1 m (inferred) | path_access_sp_001_1 |
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
| plant:sp_004_s1e11_plant1 | 1 | planted terrace sp_004_s1e11: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e6_plant1 | 1 | planted terrace sp_004_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e6_plant2 | 1 | planted terrace sp_004_s1e6: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e7_plant1 | 1 | planted terrace sp_004_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e7_plant2 | 1 | planted terrace sp_004_s1e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s1e8_plant1 | 1 | planted terrace sp_004_s1e8: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant1 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant2 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| plant:sp_004_s2e7_plant3 | 1 | planted terrace sp_004_s2e7: a shrub every 1.4 m along its middle (a landscape architect plants every tier and bank; species by the climate; inferred, nothing drawn) | site |
| platform:sp_001 | 1 | terrace sp_001: one level at -3.00 m (level marks lm_014); ground -4.92..-1.11 m under it; edge: steps; pools pool_001 in the deck (inferred); stepped terraces on edges 2 (1 x 1.06 m up), 3 (1 x 1.06 m up), 5 (1 x 1.16 m down), 6 (1 x 1.16 m down), 7 (2 x 1.16 m down), 8 (2 x 1.16 m down), 9 (1 x 1.16 m down), 10 (1 x 1.16 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); a flight of 1 risers of 0.068 m, tread 0.45 m down 0.07 m from edge 4 to the ground at its foot (the count settled on the ground the last riser lands on); one low step under the outdoor minimum riser, no cheek walls, a landing at its foot open on every side (inferred); its retaining wall stops at the building on edge 2 (0.00-0.27 m) (never through the house's wall, UL148) | site |
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
| platform:sp_002 | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 1 steps up out of it on edge 13 (0.17 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0); its retaining wall stops at the building on edge 5 (1.73-1.99 m) (never through the house's wall, UL148) | site |
| platform:sp_002_s1e4 | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s1e5 | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 1 (0.84-1.20 m) (never through the house's wall, UL148) | site |
| platform:sp_002_s2e4 | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s2e5 | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | site |
| platform:sp_003 | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 3 steps up out of it on edge 13 (0.34 m); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | site |
| platform:sp_004 | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); its retaining wall stops at the building on edge 2 (0.00-0.17 m) (never through the house's wall, UL148) | site |
| platform:sp_004_s1e11 | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e6 | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e7 | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e8 | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s2e7 | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | site |
| platform:spk_001 | 1 | parking spk_001: one level at +0.80 m (level marks lm_001, lm_003, lm_006, lm_012, lm_016); ground -3.53..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred); no kerb along 46.0 m of its edges where another surface abuts it (its wall, coping or paving is the edge there; inferred) | site |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: stone_wall_ledgestone (style family modern; not drawn) | facade |
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
| pool_seat | 2 | two sun loungers and a side table along edge 2 of pool_002, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library gap: no audited sun lounger made for outside fits, the parametric one (a teak frame on brushed steel, outdoor cushions) | pool_002_sun_lounger_0, pool_002_sun_lounger_2 |
| pool_seat | 1 | two sun loungers and a side table along edge 2 of pool_002, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library hssd_d886d10e71a0365a725abcf139142223409f7b4f ('Accent Table With Glass Top 20", Rattan,', made for outside) | pool_002_side_table_1 |
| pool_seat | 2 | two sun loungers and a side table along edge 2 of pool_003, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library gap: no audited sun lounger made for outside fits, the parametric one (a teak frame on brushed steel, outdoor cushions) | pool_003_sun_lounger_0, pool_003_sun_lounger_2 |
| pool_seat | 1 | two sun loungers and a side table along edge 2 of pool_003, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library hssd_d886d10e71a0365a725abcf139142223409f7b4f ('Accent Table With Glass Top 20", Rattan,', made for outside) | pool_003_side_table_1 |
| pool_seat | 2 | two sun loungers and a side table along edge 2 of pool_004, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library gap: no audited sun lounger made for outside fits, the parametric one (a teak frame on brushed steel, outdoor cushions) | pool_004_sun_lounger_0, pool_004_sun_lounger_2 |
| pool_seat | 1 | two sun loungers and a side table along edge 2 of pool_004, facing the water, 1.0 m of deck kept free along the coping (lesson UL143; added_by_ai; inferred); library hssd_d886d10e71a0365a725abcf139142223409f7b4f ('Accent Table With Glass Top 20", Rattan,', made for outside) | pool_004_side_table_1 |
| ridge_caps | 1 | ridge and hip caps along the roof's ridges and hips (not drawn; a tiled roof has them) | roof_ridges |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the candle dec_L0_007): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the candle dec_L0_064): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi_2 |
| rig_ceiling | 1 | ceiling fixture at (1.66, 8.60) of r_L-1_mutfak not hung: the decor pendant dec_L-1_049 hangs 0.73 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L-1_mutfak |
| rig_ceiling | 1 | ceiling fixture at (11.21, 10.34) of r_L0_koridor_2 not hung: the decor pendant dec_L0_055 hangs 1.30 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor_2 |
| rig_ceiling | 1 | ceiling fixture at (11.21, 7.41) of r_L0_koridor_2 not hung: the decor pendant dec_L0_055 hangs 1.30 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor_2 |
| rig_ceiling | 1 | ceiling fixture at (13.51, 8.63) of r_L-1_mutfak_2 not hung: the decor pendant dec_L-1_085 hangs 0.64 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L-1_mutfak_2 |
| rig_ceiling | 1 | ceiling fixture at (3.97, 10.34) of r_L0_koridor not hung: the decor pendant dec_L0_022 hangs 1.29 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor |
| rig_ceiling | 1 | ceiling fixture at (3.97, 7.41) of r_L0_koridor not hung: the decor pendant dec_L0_022 hangs 1.29 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor |
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_068; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026, above the mirror dec_L-1_067 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_080; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_079 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L-1_koridor: ceiling fixture at the pole of inaccessibility of r_L-1_koridor, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_084); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L-1_koridor_2, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_078); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_091 over the counter f_L-1_001; 852.8 lm -> 2.3112 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_092 over the counter f_L-1_002; 299.1 lm -> 0.785 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_2_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_093 over the counter f_L-1_002; 357.2 lm -> 0.9377 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_3_light |
| rig_light | 1 | r_L-1_mutfak: the ceiling light of the zone (spot(s) (1.66, 8.60)) in the decor pendant dec_L-1_049 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_097 over the counter f_L-1_010; 852.8 lm -> 2.3112 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_098 over the counter f_L-1_011; 355.4 lm -> 0.9331 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_2_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_099 over the counter f_L-1_011; 298.6 lm -> 0.7837 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_3_light |
| rig_light | 1 | r_L-1_mutfak_2: the ceiling light of the zone (spot(s) (13.51, 8.63)) in the decor pendant dec_L-1_085 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_4_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027 under the decor pendant dec_L-1_161; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038 under the decor pendant dec_L-1_180; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_042; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003, above the mirror dec_L0_041 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_045; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_044 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_025 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_028; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_027 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_031 is taken by the vase dec_L0_117); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_020); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: the decor pendant dec_L0_016 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_pendant_3_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_033 is taken by the vase dec_L0_124); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_053); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: the decor pendant dec_L0_049 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_pendant_3_light |
| rig_light | 1 | r_L0_koridor: the ceiling light of the zone (spot(s) (3.97, 7.41); (3.97, 10.34)) in the decor pendant dec_L0_022 (UL170: the pendant is the zone's light), 4400 lm over its 1 bulb(s); bulb 1/1; 4400.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light |
| rig_light | 1 | r_L0_koridor_2: the ceiling light of the zone (spot(s) (11.21, 7.41); (11.21, 10.34)) in the decor pendant dec_L0_055 (UL170: the pendant is the zone's light), 4400 lm over its 1 bulb(s); bulb 1/1; 4400.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_063 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: the decor pendant dec_L0_060 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_034 on f_L0_050 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_040 on f_L0_029 beside the bed f_L0_021; moved 0.13 m down by the ray check (z 1.00 -> 0.87 m): no ray left the model decor_f_L0_029_36 at the in-shade spot, so the light sits under its closed shade or bulb; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: the decor pendant dec_L0_037 gives light (UL170: every pendant is a light), 1100 lm over its 3 bulb(s); bulb 1/3; 366.7 lm -> 1.04 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_3: the decor pendant dec_L0_037 gives light (UL170: every pendant is a light), 1100 lm over its 3 bulb(s); bulb 2/3; 366.7 lm -> 1.04 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_pendant_4_light |
| rig_light | 1 | r_L0_yatak_odasi_3: the decor pendant dec_L0_037 gives light (UL170: every pendant is a light), 1100 lm over its 3 bulb(s); bulb 3/3; 366.7 lm -> 1.04 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_pendant_5_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_075 on f_L0_046 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_081 on f_L0_028 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: the decor pendant dec_L0_078 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_pendant_3_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_037); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_041); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_005; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_043; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
| rig_light_escape | 1 | r_L0_yatak_odasi_3: the rig light of rig_r_L0_yatak_odasi_3_bedside_1 was enclosed by its host dec_L0_040 (decor_f_L0_029_36) at the in-shade spot, z 1.00 m; moved 0.13 m down to z 0.87 m, where it gets out | rig_r_L0_yatak_odasi_3_bedside_1_light |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L-1_019, furn_f_L-1_020 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.150 m / 18 drawn risers | furn_f_L0_001, furn_f_L0_002 |
| road:pavement_1 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_2 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_3 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_4 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_5 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_6 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_7 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:pavement_8 | 1 | the street's pavement: 1.8 m of paving slabs behind a concrete kerb (no street drawn; lesson UL196; inferred) | site |
| road:road_link_spk_001_1 | 1 | the drive spk_001 ended 0.0 m short of the plot's edge: it runs on in its paving to the edge and across the 1.8 m pavement to the carriageway (the crossover, the kerb dropped; lessons UL162, UL196, UL198; inferred) | site |
| road:road_link_spk_001_2 | 1 | the drive spk_001 ended 5.0 m short of the plot's edge: it runs on in its paving to the edge and across the 1.8 m pavement to the carriageway (the crossover, the kerb dropped; lessons UL162, UL196, UL198; inferred) | site |
| road:street_1 | 1 | the street outside the plot the drive joins: 6 m of carriageway between kerbs, set back 1.8 m for its pavement (no road drawn; lessons UL162, UL196; inferred) | site |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| see_through | 1 | the bedroom's wardrobe run (modern style): sliding doors of horizontal wood slats in slim metal frames with its garments and an LED strip showing through, as its twin room r_L0_e_yatak_odasi (UL120, UL182; a built-in in 2 of at most 2 rooms, from the wall at one end to the middle of the wall); a top box to the ceiling (0.90 m of lidded boxes and baskets over the hanging bays); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_024 |
| see_through | 1 | the master bedroom's wardrobe run (modern style): sliding doors of horizontal wood slats in slim metal frames with its garments and an LED strip showing through, the modern family's own front (UL120, UL182; a built-in in 1 of at most 2 rooms, from the wall at one end to the middle of the wall); a top box to the ceiling (0.90 m of lidded boxes and baskets over the hanging bays); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_023 |
| sill | 2 | outside sill 2.2285 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill, win_L0_003_sill |
| sill | 1 | outside sill 2.6824 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_004_sill |
| sill | 1 | outside sill 2.6835 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill |
| sill | 2 | outside sill 2.743 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_arch_r_L0_yatak_odasi_3_1_sill, win_arch_r_L0_yatak_odasi_4_1_sill |
| sill | 2 | outside sill 4.2173 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_003_sill, win_L-1_004_sill |
| sill | 1 | outside sill 6.9855 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_002_sill |
| sill | 1 | outside sill 7.2461 x 0.099 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1_001_sill |
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
| suspension | 5 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L-1_049_cord, decor_dec_L0_003_cord, decor_dec_L0_016_cord |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| terrace_railing | 1 | roof terrace ro_001: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_001 |
| terrace_railing | 1 | roof terrace ro_002: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_002 |
| threshold:d_L0_011 | 1 | d_L0_011 is flush with the ground outside and the documents give no level at its landing: one step of 0.15 m up into the house (the levels' riser), its landing 0.15 m under the floor with a stone threshold at the door, the ground graded down to the landing and falling away from it 6 % (lesson UL203; inferred) | site |
| threshold:d_L0_012 | 1 | d_L0_012 is flush with the ground outside and the documents give no level at its landing: one step of 0.15 m up into the house (the levels' riser), its landing 0.15 m under the floor with a stone threshold at the door, the ground graded down to the landing and falling away from it 6 % (lesson UL203; inferred) | site |
| tree | 27 | bush of the drawn size, 0.8 m tall (height assumed) | tree_sp_001_s1e2_plant1, tree_sp_001_s1e3_plant1, tree_sp_001_s1e5_plant1 |
| tree | 21 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| type | 1 | f_L1_025: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200) | furn_f_L1_025 |
| type | 1 | f_L1_026: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200) | furn_f_L1_026 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 1 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001, furn_f_L0_002 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 5 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L-1_019, furn_f_L-1_020 |
| under_roof | 1 | tall_cabinet 1.60 m high where the sloped ceiling over its footprint leaves 0.80 m: built 0.80 m high (UL128) | furn_f_L1_066 |
| under_roof | 2 | wardrobe 2.10 m high where the sloped ceiling over its footprint leaves 1.80 m: built 1.80 m high (UL128) | furn_f_L1_027, furn_f_L1_028 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.37 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| void_guard | 1 | floor opening 1 of L1 (f_L0_002 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_1 |
| waist | 4 | the house's style (modern: plate structure, glass panels under a steel handrail, steel strings (glass channel language of the house)); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_clear | 1 | over the door d_L0_011 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_112 |
| wall_clear | 2 | over the window win_arch_r_L0_yatak_odasi_3_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_103, dec_L0_104 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_133 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_134 |
| wall_gap_m | 1 | the drawn shower stands 2.1 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_013 |
| wall_gap_m | 6 | the drawn tall_cabinet stands 2.0 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L-1_103, furn_f_L-1_104, furn_f_L0_047 |
| wall_gap_m | 2 | the drawn toilet reaches 1.1 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_015, furn_f_L0_016 |
| wall_gap_m | 4 | the drawn toilet reaches 1.3 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L-1_051, furn_f_L-1_052, furn_f_L1_021 |
| wall_gap_m | 2 | the drawn toilet reaches 1.4 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_017, furn_f_L0_018 |
| wall_joint | 4 | a flight side or landing edge within 5 cm of a wall face meets it (a gap lets the light through as a slit); the drawn footprint is kept | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_001 into r_L-1_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_001 into r_L-1_koridor_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_002 into r_L-1_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_002 into r_L-1_koridor, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_003 into r_L-1_koridor_2, on the latch side, assumed on the side with more free wall (3.25 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_003 into r_L-1_mutfak, on the latch side, assumed on the side with more free wall (0.27 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_mutfak_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_004 into r_L-1_koridor, on the latch side, assumed on the side with more free wall (3.56 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L-1_004 into r_L-1_mutfak_2, on the latch side, assumed on the side with more free wall (0.27 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L-1_mutfak_2_01 |
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
| wall_plate | 1 | inferred: a light switch on the wall next to the outside door d_L0_011 (entrance), as beside it the intercom dec_L0_112, 0.08 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_01 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_027 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_028 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_029 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_030 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_04 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_067, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_079, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_027, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_041, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_044, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_034, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_038, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (left side) beside its nightstand f_L0_031, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (right side) beside its nightstand f_L0_032, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (left side) beside its nightstand f_L0_034, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (right side) beside its nightstand f_L0_033, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (left side) over its nightstand f_L0_041 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (right side) over its nightstand f_L0_042 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (left side) over its nightstand f_L0_045 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (right side) over its nightstand f_L0_044 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (left side) over its nightstand f_L0_050 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_3_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (right side) beside its desk f_L0_029, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (left side) beside its desk f_L0_028, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (right side) over its nightstand f_L0_046 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_4_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (1.55 m), 0.30 m over the floor | plate_r_L1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (1.85 m), 0.30 m over the floor | plate_r_L1_koridor_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (3.26 m), 0.30 m over the floor | plate_r_L-1_koridor_03, plate_r_L-1_koridor_2_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (3.63 m), 0.30 m over the floor | plate_r_L0_koridor_03, plate_r_L0_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.10 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.51 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_06 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.72 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.25 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_04 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.30 m, 0.30 m over the floor | plate_r_L-1_salon_2_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.42 m, 0.30 m over the floor | plate_r_L-1_salon_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.87 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_02 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 2.98 m, 0.30 m over the floor | plate_r_L-1_salon_04, plate_r_L-1_salon_2_04 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 3.63 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_05, plate_r_L0_yatak_odasi_4_05 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.33 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_05, plate_r_L0_yatak_odasi_2_05 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.87 m, 0.30 m over the floor | plate_r_L-1_salon_03, plate_r_L-1_salon_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 5.53 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_03 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_025, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_02 |
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_003 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_02 |
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_010 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_03 |
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_012 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_101 beside it, 0.30 m over the floor | plate_r_L-1_salon_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_102 beside it, 0.30 m over the floor | plate_r_L-1_salon_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L1_069 beside it, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_02 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_002 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_03 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_011 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_04 |
| wet_walls | 1 | the modern family's bathroom (FAMILY_BATH): large-format stone-look porcelain 60 x 120 cm in greige on the walls, floor to ceiling (UL114 B8; the brief names no wet-room tiles) | style |
| winders | 4 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| window_fit | 1 | fitted again to its window win_L0_001 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 2.72 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_098 |
| window_fit | 1 | fitted again to its window win_L0_001 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 3.02 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_002 |
| window_fit | 1 | fitted again to its window win_L0_004 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 2.72 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_130 |
| window_fit | 1 | fitted again to its window win_L0_004 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 3.02 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_059 |
| window_fit | 1 | fitted again to its window win_L1_001 as built: 4.00 m wide, sill 0.20 m, head 1.71 m: a 4.40 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L1_015 |
| window_fit | 1 | fitted again to its window win_L1_002 as built: 4.00 m wide, sill 0.20 m, head 1.71 m: a 4.40 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L1_053 |
| window_fit | 1 | its window win_L-1_001 as built: 7.19 m wide, sill 0.20 m, head 2.60 m leaves no room for the blind (doors, wall ends) (UL181) | dec_L-1_012 |
| window_handles | 2 | design detail of the documented window: a slider window of 2 pane(s), handles on the opening one(s) [1] (a 4.00 m glazing over 2.4 m with no drawn bars: 2 lift-and-slide panes on its low sill of at most 2 m (real products, UL181)); not in the documents | win_L1_001_handle, win_L1_002_handle |
| window_pier | 1 | win_L-1_001: its frame stood 0.14 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.26 m along its wall away from the corner (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L-1_001 |
| window_pier | 1 | win_L-1_002: its frame stood 0.14 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): narrowed from the corner side to 6.93 m (the far jamb kept: another opening within 0.10 m) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L-1_002 |
| window_pier | 1 | win_L-1_003: its frame stood 0.34 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.06 m along its wall away from the corner (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L-1_003 |
| window_pier | 1 | win_L-1_004: its frame stood 0.34 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.06 m along its wall away from the corner (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L-1_004 |
| window_pier | 1 | win_L0_001: its frame stood 0.24 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.10 m away from the corner and narrowed from its side to 2.62 m (a longer move: another room or no outside along the new place) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L0_001 |
| window_pier | 1 | win_L0_004: its frame stood 0.24 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.10 m away from the corner and narrowed from its side to 2.62 m (a longer move: another room or no outside along the new place) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L0_004 |
| worktop_slide | 1 | slid along f_L-1_001: it would stand in the tall unit of f_L-1_001 (fridge_french); as its compact form, a coffee machine | dec_L-1_052 |
| worktop_slide | 1 | slid along f_L-1_010: it would stand in the tall unit of f_L-1_010 (fridge_french); as its compact form, a coffee machine | dec_L-1_088 |

## Rooms mixing polished and Cycles views

None.

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_salon (rung None), r_L0_e_yatak_odasi (rung None), r_L0_yatak_odasi (rung None), r_L0_yatak_odasi_3 (rung None), r_L1_oyun_aktivite_ve_dinlenme_odasi (rung None), r_L1_teras (rung None).

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_1640cba5fd553782ad05455c [non_commercial], 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_31697dcef5ea93fa6932e582 [non_commercial], 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_3ca51944db9df428d5f09afc [non_commercial], 3dwh_4bb1b0bfa01eefe9079d94b0 [non_commercial], 3dwh_4d053f976db6e628c7ca5635 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_52f33bb92da2aee9f4cc12bb [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_730bffda88163748fe87804f [non_commercial], 3dwh_73836b83e2bfb367cacfc7ee [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cc9a735781c180a72cf558ce [non_commercial], 3dwh_cd89c6a8109b82ff0562c56f [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_d438658982ef759573afb333 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_industrial_5_effc724b [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_mediterranean_3_068971b6 [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_4652661588c3e25396b891901da281f41f7a140c [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_xxxx2c997418xa75dx4644x91ebx792fb54da87d [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: yes
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: yes
- cam_r_L-1_mutfak_2: commercial-safe: yes
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: gen_potted_plant_mediterranean_3_068971b6 [tool_nc])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_4d053f976db6e628c7ca5635 [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_d438658982ef759573afb333 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_4d053f976db6e628c7ca5635 [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_d438658982ef759573afb333 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: yes
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: yes
- cam_r_L0_e_banyo_2: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_31697dcef5ea93fa6932e582 [non_commercial], 3dwh_73836b83e2bfb367cacfc7ee [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_73836b83e2bfb367cacfc7ee [non_commercial])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_31697dcef5ea93fa6932e582 [non_commercial], 3dwh_73836b83e2bfb367cacfc7ee [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc])
- cam_r_L0_koridor_1: commercial-safe: yes
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_730bffda88163748fe87804f [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_industrial_5_effc724b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_industrial_5_effc724b [tool_nc], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_small_industrial_5_effc724b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_cd89c6a8109b82ff0562c56f [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_cd89c6a8109b82ff0562c56f [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: yes
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: gen_plant_large_modern_minimal_1_06ccb749 [tool_nc])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_3ca51944db9df428d5f09afc [non_commercial], 3dwh_cc9a735781c180a72cf558ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_xxxx2c997418xa75dx4644x91ebx792fb54da87d [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_4bb1b0bfa01eefe9079d94b0 [non_commercial], 3dwh_cc9a735781c180a72cf558ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], hssd_xxxx2c997418xa75dx4644x91ebx792fb54da87d [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_4bb1b0bfa01eefe9079d94b0 [non_commercial], 3dwh_52f33bb92da2aee9f4cc12bb [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_4652661588c3e25396b891901da281f41f7a140c [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_xxxx2c997418xa75dx4644x91ebx792fb54da87d [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial], hssd_xxxx2c997418xa75dx4644x91ebx792fb54da87d [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])

## Built below library level (Milestone 13)

72 furniture piece(s) built from a module builder or a parametric family instead of a library model: 6 library gap(s) to close with a real model, 66 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1_055 | shower | module | bath_set | r_L-1_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L-1_056 | shower | module | bath_set | r_L-1_banyo | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
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
| f_L0_024 | wardrobe | module | module:wardrobe:wardrobe_run | r_L0_e_yatak_odasi_2 | bedroom | from_documents | yes | module builder wardrobe_run (7 module(s): PAX frame 100x58x202 cm) |
| f_L0_031 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi | bedroom | from_documents | no (by design) | - |
| f_L0_032 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi | bedroom | from_documents | no (by design) | - |
| f_L0_033 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi_2 | bedroom | from_documents | no (by design) | - |
| f_L0_034 | nightstand | parametric | parametric:nightstand | r_L0_e_yatak_odasi_2 | bedroom | from_documents | no (by design) | - |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_koridor_2 | hall | from_documents | no (by design) | - |
| f_L1_002 | stair | parametric | parametric:stair | r_L1_koridor | hall | from_documents | no (by design) | - |
| f_L1_005 | table_dining | parametric | parametric:table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi | living | from_documents | yes | parametric family (built below the library level) |
| f_L1_009 | table_dining | parametric | parametric:table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | living | from_documents | yes | parametric family (built below the library level) |
| f_L1_015 | washbasin | module | bath_set | r_L1_banyo | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L1_016 | washbasin | module | bath_set | r_L1_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (fluted floating vanity, by design) |
| f_L1_021 | toilet | parametric | parametric:toilet | r_L1_banyo | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L1_022 | toilet | parametric | parametric:toilet | r_L1_banyo_2 | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L1_025 | bathtub | module | bath_set | r_L1_banyo | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L1_026 | bathtub | module | bath_set | r_L1_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
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
| f_L-1_102 | tv_unit | parametric | parametric:tv_unit | r_L-1_salon_2 | living | added_by_ai | no (by design) | - |
| f_L-1_103 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L-1_104 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_047 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_e_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_048 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_049 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L1_066 | tall_cabinet | parametric | parametric:tall_cabinet | r_L1_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 3), ext_1 (6.0 degrees off the sun, sky pull k 4), ext_5 (5.6 degrees off the sun, sky pull k 0).

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

Assets: textures CC0 x 87; furniture/decor models 3DWH-UNREVIEWED x 75, CC-BY-4.0 x 128, CC-BY-NC-4.0 x 39, CC0 x 1, generated (Infinigen v1.19.0, BSD-3-Clause) x 1, generated (TRELLIS.2-4B, MIT) x 26 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 35 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_136)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_059)
- "Three candles and a golden candlestick" by Leon_dp (https://sketchfab.com/3d-models/9d46daabbefe4b4eab74d9da349dd015), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_009)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_037)
- "Candle" by deniska40k (https://sketchfab.com/3d-models/c408586d8c1547448c4ff47abb4fb981), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_044, dec_L0_007)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261031-194116-full-20261031T194610Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 49.4 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 110.2 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.4 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.7 min | answers applied |
| fit | ok | 11.4 s | - |
| layout | ok | 54.2 s | - |
| decor_ask | ok | 2.1 min | - |
| photos | reused | 0.1 s | - |
| assets | ok | 5.2 s | - |
| decor | ok | 14.3 s | - |
| agent_apply | ok | 89.0 s | - |
| refit | ok | 2.0 min | - |
| build | ok | 49.9 min | - |
| agent_previews | ok | 9.1 min | 35 view(s) |
| agent | ok | 87.7 min | 5 round(s), 118 finding(s) removed by 94 accepted edit(s) (measured; 257 predicted by the dry re-checks), 21 new, net 97, 346 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 11.5 min | - |
| controls | ok | 2.3 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.3 min | - |
| check | ok | 3.0 min | - |
| export | ok | 3.5 min | - |
| combine | ok | 24.3 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 5 round(s), 94 edit(s) accepted, 346 rejected, 823 model calls (11598447 tokens), 98.3 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 29412): earlier runs of the appended log are left out (29411 events, 9234 model calls, 924 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 94 / 346 (21 % accepted) |
| rejected by reason | acceptance 74, no_change 29, asset_unusable 28, memory 28, pin_refused 24 |
| rooms checked by code / vision / planner | 38 / 14 / 29 |
| rooms with fixable critical or major findings visited | 29 of 29 |
| critical before -> after | 11 -> 17 |
| major before -> after | 365 -> 473 |
| agent minutes; first accepted edit after | 84.55; 39.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 28; 69; 89 (53) |
| critical/major findings removed in rounds 1-4 (measured by the next round; predicted by the dry re-checks of the same rounds) | 118 measured; 257 predicted |
| new critical/major findings in rounds 1-4; net removed (gone - new) | 136 new; net -18 |
| edits removing their finding | 8 of 76 |
| plans ok / empty / refused / default | 53 / 29 / 5 / 2 |

### What the AI inspector saw on the final renders

477 vision finding(s) (71 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 0 fixed in the final round, 4 handed to the stage that owns them, 549 open; the architect leaves 0 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`.

Still open or handed on (critical and major):

- major D2 f_L0_010: The wardrobe has a large glass pane in its central door, which is an incorrect object for a standard wardrobe and looks like a window or mir (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major V1 cam_r_L0_koridor_1: The camera view is extremely close to the wall, showing only a framed picture and a small section of the wall, failing to capture the room's (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major F9 r_L1_oyun_aktivite_ve_dinlenme_odasi: A flat, 2D image of a coffee table is standing on the floor against the wall, which is a rendering error and not a real piece of furniture. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major F9 r_L1_oyun_aktivite_ve_dinlenme_odasi: A flat, 2D image of a coffee table is standing on the floor against the wall, which is a rendering error and not a real piece of furniture. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major V1 r_L-1_banyo: bad_camera: The camera is too close and poorly framed, cutting off the top of the mirror and the shower head. It does not show the room's ma (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major D3 f_L-1_026: mismatched_set: The combination of a dark stone vessel basin, a cork countertop, and a fluted wood cabinet is a disjointed mix of materials  (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_056: bare_material: The shower screen is a flat, opaque, featureless grey slab. It lacks the transparency of glass or the texture of a proper pan (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major V1 r_L-1_koridor_2: bad_camera: The camera is aimed at a blank corner and a large, featureless wall. It fails to show the room's layout, the doors, or any poten (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: wall art. The large, blank wall in the center of the frame is completely devoid of any decoration, which is a major flaw for  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: lamps. The hallway is lit by a flat, generic light. It lacks the warm, layered lighting (like a chandelier or wall sconces) t (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: a place to sit. A hallway of this size (11.9 m2) could benefit from a small bench or console table to make it functional and  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the reference shows a styled kitchen with a toaster, utensils, and a pot; the render is completely bare) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the reference has a warm, inviting glow; the render is lit with flat, cold daylight) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the lighting is flat and clinical, lacking the warm ambient glow seen in the reference) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the counters are almost entirely bare, lacking the curated objects, plants, or warm textures that make a kit (open: a tool exists (swap_model) but no edit was accepted)
- major Q13 f_L-1_091: missing layer: wall_cabinet. The kitchen is missing all upper cabinetry, leaving a large, empty expanse of wall that makes the room look unf (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major Q13 f_L-1_001: missing layer: styled surfaces. The worktop is completely bare. A designed kitchen needs small appliances (kettle, coffee machine) or decor  (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major V1 f_L-1_090: bad_camera. The camera is positioned too close to the left wall, cutting off the refrigerator and stove. This framing makes the kitchen look (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major D3 f_L-1_049: mismatched_set: the dark, sculptural lounge chair in the foreground is a different design language from the low, blocky white sofa and the m (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_027: mismatched_set: the dining set (table and chairs) is a dark, heavy mid-century model that does not go with the light, minimalist living grou (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_053: missing layer: feature wall: the wall behind the sofa is a flat, untextured concrete surface; the style calls for a feature wall (fluted or  (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 win_L-1_001: missing layer: layered curtains: the full-height window is completely bare; it needs full-height curtains (a sheer behind a heavier drape) t (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L-1_027: mismatched_set: the long, formal dining table with its bank of identical black chairs (f_L-1_028..037) clashes with the casual, low lounge g (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_053: missing layer: feature wall: the wall behind the sofa is a flat, untextured surface; the style calls for a feature wall (fluted or slatted w (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_061: missing layer: styled surfaces: the coffee table is completely bare. The reference shows a styled surface with books, a vase, and decor; thi (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)

### Argus, the auditor

Score 3.4 / 100 (100 = nothing open): 23 critical, 374 major, 129 minor open. By kind (critical + major): lost 52, misread 36, geometry 58, no_sense 44, other 34, taste 100, process 34, silent 18, reference_missed 9, stale 6, detached 5, untyped 1. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- geometry f_L1_025: bathtub f_L1_025 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: noth
- geometry f_L1_026: bathtub f_L1_026 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: noth
- no_sense f_L1_025: furn_f_L1_025 pokes through the roof (top 5.23 m)
- no_sense f_L1_026: furn_f_L1_026 pokes through the roof (top 5.23 m)
- other f_L1_025: bathtub f_L1_025 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: noth
- other f_L1_026: bathtub f_L1_026 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: noth
- misread f_L0_019: missing anchor: the double bed is not in the room, so the bedroom has no bed; the wardrobe mirror even reflects a bed that is not present, which makes the rende
- misread f_L0_041: missing anchor: the nightstands (f_L0_041, f_L0_042) and the window win_L0_001 are absent, leaving a bare corner with only a desk and a wardrobe.
- misread cam_r_L1_teras_1: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- misread r_L1_teras: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- taste cam_r_L1_banyo_1: Argus: Argus: Argus: Argus: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. This is 
- misread cam_r_L1_teras_2: Argus: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- misread f_L1_108: Argus: The main furniture group (armchairs and side table) is missing from the balcony, leaving the room empty and without its primary function.
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

Library gaps reported by the agent: nightstand (Nightstands f_L0_044 and f_L0_045 are built below library level (parametric mesh); swap_model attempts were refused 4 times by the fit rules. No audited library model of a nightstand fits the 0.4x0.4m footprint at the required height.), potted_plant (No audited library model for counter decor (plants, kettle, small appliances) exists to style the bare kitchen worktop (a:D3, a:Q13).), washbasin modern minimal (No audited real washbasin model fits the sloped-ceiling height cap; all generated candidates fail the fit rules, so the S1 floor-clearance finding cannot be fixed by swap.), toilet modern minimal (No audited real toilet model fits the sloped-ceiling height cap; generated candidates fail the fit rules or were audit-removed, so the S1 floor-clearance finding cannot be fixed by swap.), tall_cabinet modern minimal (No audited library tall_cabinet fits the 0.40×0.35×1.6 m footprint (three real models failed the fit rules: caps, height), so the parametric build stays for a:F554.), toilet (No audited toilet model passes the fit rules (caps, height) for the drawn 0.50x0.69 m footprint; every generated candidate is pin_refused, so the S1 (model floats 0.20 m above the floor) cannot be cleared by swap_model), washbasin (No audited washbasin model passes the fit rules (caps, height) for the drawn 1.00x0.55 m footprint; every generated candidate is pin_refused, so the S1 (model floats 0.384 m above the floor) cannot be cleared by swap_model), nightstand (Nightstand f_L0_045 is built below the library level (parametric mesh); no audited library model fits, same as f_L0_044.), fridge modern minimal (The fridge is built into the counter run (integrated in the run's fronts); no library model can replace it, so the crude white-box look cannot be fixed by swap_model (a:F378).), wardrobe (c:LG:f_L0_023: record the wardrobe library gap for review (no candidate within 10% non-uniform scale and 0.85..1.2 mean scale; relaxed caps also failed).), toilet (No audited real-product toilet model passes the fit rules (caps, height) to fix the S1 float (+0.200 m above floor); all generated candidates are either audit-removed or fail the fit rules.), washbasin (No audited real-product washbasin model passes the fit rules (caps, height) to fix the S1 float (+0.384 m above floor); all generated candidates are either audit-removed or fail the fit rules.), toilet (No audited real toilet model fits f_L1_022: the generated candidates fail the fit rules (height caps under the sloped ceiling) and the one real candidate was audit-removed, so the parametric mesh stays (a:F289, c:S1).), tall_cabinet (Current model is a heavy, dark industrial open shelving unit clashing with the light minimalist bathroom style; previous swap (abo_B07GFFY4WT) failed the fit rules, so no audited library model fits the 0.3x0.3 footprint and height.), washbasin (Washbasin floats 0.384 m above the floor (S1); previous swap (gen_washbasin_minimal_1_9dc765fb) was refused by the fit rules, so no audited library model corrects the vertical placement.), toilet (Toilet floats 0.200 m above the floor (S1) and has no paper holder (M26); multiple swap attempts were rejected (audit removed, fit rules), so no audited library model sits correctly and includes the accessory.), shoe_cabinet minimal (No audited shoe cabinet model fits the 0.6x0.3 footprint within the height caps: the walnut rack and 3dwh display cabinet fail the fit rules (caps, height) and the cedar rack was audit-removed, so the bare parametric grid stays for review.), nightstand modern minimal (No library nightstand model passes the fit rules (caps, height) for the drawn 0.50 x 0.45 m footprint: side_table_01, abo_B079VK52WZ, abo_B07K7K7GTZ all pin_refused, so the parametric mesh stays and P7 remains for review.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 11 | 365 | 115 | 6 | 31 | 140 | layout | 30 |
| 2 | 11 | 352 | 120 | 6 | 34 | 92 | layout | 35 |
| 3 | 11 | 347 | 119 | 6 | 24 | 89 | layout | 35 |
| 4 | 19 | 581 | 177 | 20 | 5 | 25 | refit | 4 |
| 6 | 17 | 473 | 174 | 30 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| AI1 | 0 | 179 | 0 | 0 |
| AI2 | 0 | 2 | 0 | 0 |
| AI3 | 0 | 8 | 0 | 0 |
| AI5 | 0 | 38 | 0 | 0 |
| C1 | 0 | 0 | 0 | 39 |
| C3 | 0 | 24 | 0 | 0 |
| C6 | 0 | 4 | 0 | 0 |
| C7 | 0 | 48 | 0 | 0 |
| D1 | 0 | 0 | 2 | 0 |
| D2 | 0 | 24 | 2 | 0 |
| D3 | 0 | 309 | 116 | 0 |
| F1 | 0 | 0 | 10 | 0 |
| F2 | 0 | 20 | 0 | 0 |
| F3 | 0 | 33 | 5 | 0 |
| F4 | 0 | 95 | 0 | 0 |
| F6 | 0 | 49 | 0 | 0 |
| F9 | 0 | 34 | 0 | 0 |
| G1 | 0 | 0 | 35 | 0 |
| G10 | 0 | 134 | 0 | 0 |
| G11 | 0 | 39 | 0 | 0 |
| G13 | 0 | 20 | 0 | 0 |
| G14 | 0 | 0 | 10 | 0 |
| G2 | 0 | 22 | 10 | 0 |
| G3 | 0 | 33 | 0 | 0 |
| G4 | 0 | 2 | 12 | 0 |
| G5 | 0 | 50 | 0 | 0 |
| G6 | 0 | 22 | 10 | 0 |
| G8 | 0 | 14 | 10 | 0 |
| J1 | 0 | 53 | 0 | 27 |
| K1 | 0 | 18 | 0 | 0 |
| K3 | 0 | 33 | 0 | 0 |
| L6 | 0 | 5 | 0 | 0 |
| LG | 0 | 0 | 30 | 0 |
| M13 | 0 | 0 | 5 | 0 |
| M15 | 0 | 0 | 5 | 0 |
| M17 | 0 | 10 | 10 | 0 |
| M2 | 0 | 2 | 0 | 0 |
| M21 | 0 | 0 | 47 | 0 |
| M22 | 0 | 27 | 0 | 0 |
| M23 | 0 | 0 | 10 | 0 |
| M26 | 0 | 0 | 25 | 0 |
| M28 | 0 | 9 | 10 | 0 |
| M30 | 0 | 0 | 30 | 0 |
| M31 | 18 | 0 | 0 | 0 |
| M33 | 0 | 45 | 10 | 0 |
| M34 | 0 | 0 | 20 | 0 |
| NR | 0 | 20 | 0 | 0 |
| P0 | 0 | 58 | 0 | 0 |
| P10 | 0 | 20 | 0 | 0 |
| P2 | 0 | 6 | 0 | 0 |
| P6 | 0 | 4 | 0 | 0 |
| P7 | 0 | 104 | 0 | 0 |
| P9 | 0 | 0 | 0 | 2 |
| Q10 | 0 | 79 | 3 | 0 |
| Q12 | 0 | 42 | 3 | 0 |
| Q13 | 0 | 13 | 0 | 0 |
| Q14 | 0 | 20 | 3 | 0 |
| Q15 | 0 | 7 | 0 | 0 |
| Q3 | 0 | 0 | 2 | 0 |
| Q4 | 26 | 73 | 0 | 0 |
| Q5 | 0 | 4 | 0 | 0 |
| Q7 | 0 | 5 | 0 | 0 |
| Q9 | 0 | 2 | 0 | 0 |
| R3 | 0 | 0 | 40 | 0 |
| RC | 0 | 0 | 35 | 0 |
| S1 | 0 | 96 | 0 | 0 |
| S2 | 0 | 21 | 31 | 0 |
| S4 | 0 | 0 | 16 | 0 |
| S5 | 0 | 0 | 67 | 0 |
| V1 | 7 | 81 | 8 | 0 |
| X2 | 18 | 17 | 10 | 0 |
| X3 | 0 | 8 | 0 | 0 |
| X5 | 0 | 0 | 63 | 0 |
| X6 | 0 | 19 | 0 | 0 |
| X9 | 0 | 7 | 0 | 0 |
| lighting_dark | 0 | 7 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 29946 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 41.0 -> 51.0 | Argus: The armchair stands behind the back of f_L1_017; a room relayout re-orients the seating. (fixes a:F87) | ![](agent/r1_004_relayout_room_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_005_relayout_room_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 29961 | 1 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The washbasin, shower and toilet are not visible in the render; the camera is re-posed to show them. (fixes a:F140) | - | - |
| 29962 | 1 | relayout_room | r_L0_yatak_odasi_3 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The bed is standing in the room (headboard 0.30 m off) and the side clearance is below 0.60 m; the room is re-laid out so the bed rests on a wall with proper clearance. (fixes a:F141) | ![](agent/r1_020_relayout_room_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_021_relayout_room_after_r_L0_yatak_odasi_3.png) |
| 29963 | 1 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The bed f_L0_019 is cut out of the frame, leaving the bedroom with no visible main piece. Reposing the camera to include the bed restores the anchor. (fixes a:F146) | - | - |
| 29972 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Top solver candidate (score 16.87, 5 pieces, no hard failures) rebuilds the balcony planters and terrace_pair into a proper seating set, addressing the sparse-furnishing and missing-member findings. | ![](agent/r1_067_relayout_room_before_r_L1_teras.png) | ![](agent/r1_069_relayout_room_after_r_L1_teras.png) |
| 29973 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Terrace is under-furnished (single chair, bare wall); candidate 2 gives a proper seating group with 2 planters and 2 chairs for the 19.7 m² terrace. | ![](agent/r1_068_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_071_relayout_room_after_r_L1_teras_2.png) |
| 29977 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 51.0 -> 51.0 | Room is furnished as a living room (sofas, TV unit, dining, coffee tables) and the name means game/activity/relaxation room; 'other' is wrong. | ![](agent/r1_072_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_080_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 29980 | 1 | resize_piece | f_L-1b_042 | adjusted_by_ai | 28.0 -> 28.0 | Sofa was misread as 0.90m wide x 2.13m deep; correct product size is 2.13m wide x 0.90m deep, fixing the F2 size error and the inferred front warning. | ![](agent/r1_081_resize_piece_before_r_L-1b_salon.png) | ![](agent/r1_084_resize_piece_after_r_L-1b_salon.png) |
| 29989 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | 48.0 -> 48.0 | 40.5 m2 room with sofa, dining table, bookshelf; name means game/activity/rest room; twin room is typed living (a:F216, a:N196) | ![](agent/r1_095_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_106_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 30000 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. | ![](agent/r1_110_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_115_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 30003 | 1 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Rotate the armchair to face 90° towards the coffee table and seating group, resolving the orientation and G3 group-alignment findings. | ![](agent/r1_121_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_140_rotate_piece_after_r_L-1b_salon_2.png) |
| 30008 | 1 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Replace the corporate black mesh office chair with a leather-padded residential desk chair to match the warm bedroom aesthetic (F416). | ![](agent/r1_139_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_146_swap_model_after_r_L0_yatak_odasi_3.png) |
| 30012 | 1 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 28.0 -> 58.0 | Armchair needs to face the coffee table (f_L-1b_071) which is to its north; rotating to 90° (facing +Y) aligns it with the group and fixes F4/G3. | ![](agent/r1_149_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r1_164_rotate_piece_after_r_L-1b_salon.png) |
| 30016 | 1 | resize_piece | f_L-1_070 | adjusted_by_ai | 30.0 -> 30.0 | Resize armchair to match the drawn dimensions [0.642, 0.569] | ![](agent/r1_166_resize_piece_before_r_L-1_salon.png) | ![](agent/r1_169_resize_piece_after_r_L-1_salon.png) |
| 30023 | 1 | move_piece | f_L-1_031 | adjusted_by_ai | 30.0 -> 30.0 | Nudge chair f_L-1_031 to resolve the 0.040 m cut with the dining table | ![](agent/r1_173_move_piece_before_r_L-1_salon.png) | ![](agent/r1_176_move_piece_after_r_L-1_salon.png) |
| 30027 | 1 | report_library_gap | f_L0_044 | library_gap | - | Nightstands f_L0_044 and f_L0_045 are built below library level (parametric mesh); swap_model attempts were refused 4 times by the fit rules. No audited library model of a nightstand fits the 0.4x0.4m footprint at the required height. | - | - |
| 30030 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift the right nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the required ≤0.30 m. | ![](agent/r1_177_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_180_move_piece_after_r_L0_e_yatak_odasi.png) |
| 30043 | 1 | report_library_gap | report_library_gap | library_gap | - | No audited library model for counter decor (plants, kettle, small appliances) exists to style the bare kitchen worktop (a:D3, a:Q13). | - | - |
| 30062 | 1 | move_piece | f_L0_010 | adjusted_by_ai | 70.0 -> 80.0 | Center the wardrobe on the free wall span to open the 0.80 m front clearance. | ![](agent/r1_200_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r1_213_move_piece_after_r_L0_yatak_odasi.png) |
| 30070 | 1 | remove_piece | f_L1_065 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet pokes through the sloped ceiling (X2) and has wrong height (S4); removing it clears a:F660, c:X2:f_L1_065, c:S4:f_L1_065. | ![](agent/r1_221_remove_piece_before_r_L1_banyo.png) | ![](agent/r1_230_remove_piece_after_r_L1_banyo.png) |
| 30077 | 1 | resize_piece | f_L0_023 | adjusted_by_ai | 100.0 -> 100.0 | Fix c:S4:f_L0_023: bring the wardrobe height into the 1.50-2.45 m range (it was built at 2.99 m). | ![](agent/r1_229_resize_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_234_resize_piece_after_r_L0_e_yatak_odasi.png) |
| 30078 | 1 | set_lighting | r_L-1_banyo | agent_override | - | View cam_r_L-1_banyo_1 is 0.40 stops over the EV cap; finding names x1.87 for the room. | - | - |
| 30086 | 1 | set_lighting | r_L0_banyo | agent_override | - | Both interior views are underexposed (0.44 and 0.32 stops over the EV cap); x1.92 is the higher suggested factor and covers both. | - | - |
| 30093 | 1 | swap_model | f_L0_038 | adjusted_by_ai | 80.0 -> 80.0 | Replace the corporate black leather office chair with a low-back upholstered mesh chair that fits the calm bedroom palette. | ![](agent/r1_247_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r1_249_swap_model_after_r_L0_yatak_odasi.png) |
| 30110 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | View cam_r_L0_e_banyo_1 is 0.91 stops over the EV cap; the finding names x2.66 for the room. | - | - |
| 30114 | 1 | report_library_gap | f_L1_015 | library_gap | - | No audited real washbasin model fits the sloped-ceiling height cap; all generated candidates fail the fit rules, so the S1 floor-clearance finding cannot be fixed by swap. | - | - |
| 30119 | 1 | report_library_gap | f_L1_021 | library_gap | - | No audited real toilet model fits the sloped-ceiling height cap; generated candidates fail the fit rules or were audit-removed, so the S1 floor-clearance finding cannot be fixed by swap. | - | - |
| 30134 | 1 | set_camera | r_L0_koridor | agent_override | - | Move camera to a free point in the corridor looking towards the shoe cabinet, away from the door leaf. | - | - |
| 30142 | 1 | report_library_gap | f_L-1_104 | library_gap | - | No audited library tall_cabinet fits the 0.40×0.35×1.6 m footprint (three real models failed the fit rules: caps, height), so the parametric build stays for a:F554. | - | - |
| 30147 | 1 | report_library_gap | f_L0_017 | library_gap | - | No audited toilet model passes the fit rules (caps, height) for the drawn 0.50x0.69 m footprint; every generated candidate is pin_refused, so the S1 (model floats 0.20 m above the floor) cannot be cleared by swap_model | - | - |
| 30149 | 1 | report_library_gap | f_L0_005 | library_gap | - | No audited washbasin model passes the fit rules (caps, height) for the drawn 1.00x0.55 m footprint; every generated candidate is pin_refused, so the S1 (model floats 0.384 m above the floor) cannot be cleared by swap_model | - | - |
| 30706 | 2 | swap_model | f_L1_030 | adjusted_by_ai | 51.0 -> 51.0 | Argus: An upholstered indoor armchair (3dwh_826f2d90cfd567a923e3dc8c) is on the outdoor terrace. Swap to a minimal/modern outdoor-appropriate model. (fixes a:F172) | ![](agent/r2_003_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_004_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 30707 | 2 | swap_model | f_L1_031 | adjusted_by_ai | 51.0 -> 51.0 | Argus: An upholstered indoor armchair (3dwh_826f2d90cfd567a923e3dc8c) is on the outdoor terrace. move_piece was refused (drawn_lock: 0.89 m > 0.3 m). Swap the model instead. (fixes a:F173) | ![](agent/r2_005_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_006_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 30708 | 2 | swap_model | f_L1_035 | adjusted_by_ai | 51.0 -> 51.0 | Argus: An indoor console table/bench (abo_B075QDV39B) is on the outdoor terrace. retype_piece was refused (bench not a candidate). Swap to a japandi/modern outdoor-appropriate model. (fixes a:F174) | ![](agent/r2_007_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_008_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 30709 | 2 | swap_model | f_L1_036 | adjusted_by_ai | 51.0 -> 51.0 | Argus: An indoor coffee table (3dwh_75ac3c7d6dc1da28c99a0ad6) is on the outdoor terrace. move_piece was refused multiple times (drawn_lock, score, acceptance). Swap to an industrial/modern outdoor-appropriate model. (fixes a:F175) | ![](agent/r2_009_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_010_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 30712 | 2 | set_camera | r_L-1_banyo | agent_override | - | Argus: The camera does not show the washbasin; re-posing it to show f_L-1_056 (the shower/bathtub) fixes the finding. (fixes a:F191) | - | - |
| 30713 | 2 | set_material | ground | agent_override | - | Argus: The render shows a single untextured green plane; the ground slot has no real material assigned, so the terrace reads as a void. (fixes a:F193) | - | - |
| 30714 | 2 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace holds only two plants and a single armchair; the terrace_lounge group is missing, so it looks bare and undesigned. (fixes a:F195) | ![](agent/r2_011_place_group_before_r_L1_teras.png) | ![](agent/r2_012_place_group_after_r_L1_teras.png) |
| 30715 | 2 | set_camera | r_L1_oyun_aktivite_ve_dinlenme_odasi | agent_override | - | Argus: The armchair is cut off by the frame; re-aiming to show the complete chair and the seating group fixes it. (fixes a:F201) | - | - |
| 30720 | 2 | set_camera | r_L1_koridor | agent_override | - | Argus: The L1 hall view is dominated by a closed door; reframing on the open door to the living space and the hall's wardrobe shows the furnished room beyond. (fixes a:F214) | - | - |
| 30721 | 2 | set_material | facade | agent_override | - | Argus: The whole facade is clad in stone to the eaves; the family scheme requires white render over the stone base, so the facade slot must be a white render, not stone. (fixes a:F215) | - | - |
| 30730 | 2 | place_group | r_L1_teras_2 | added_by_ai | 100.0 -> 100.0 | Argus: Twin of F249 on the second unit; the terrace needs a seating set. (fixes a:F250) | ![](agent/r2_021_place_group_before_r_L1_teras_2.png) | ![](agent/r2_022_place_group_after_r_L1_teras_2.png) |
| 30731 | 2 | set_material | facade | agent_override | - | Argus: The whole facade is clad in stone; the facade slot must be render to match the scheme. (fixes a:F254) | - | - |
| 30735 | 2 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 1 (best score) gives a proper seating group with balanced layout for the 19.7 m2 terrace, addressing the single-chair and bare-terrace findings. | ![](agent/r2_068_relayout_room_before_r_L1_teras_2.png) | ![](agent/r2_070_relayout_room_after_r_L1_teras_2.png) |
| 30738 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 adds a second member to both the balcony and terrace_pair groups (6 pieces), giving the 19.7 m² terrace a proper seating set and more styling to clear the missing_member findings. | ![](agent/r2_069_relayout_room_before_r_L1_teras.png) | ![](agent/r2_073_relayout_room_after_r_L1_teras.png) |
| 30743 | 2 | move_piece | f_L-1b_046 | adjusted_by_ai | 28.0 -> 28.0 | Sofa's back is 0.59 m off the wall; shifting it 0.35 m north puts its back on the top wall, fixing the off-wall finding. | ![](agent/r2_081_move_piece_before_r_L-1b_salon.png) | ![](agent/r2_085_move_piece_after_r_L-1b_salon.png) |
| 30747 | 2 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Rotate armchair to face 90° toward the coffee table and sofa group, fixing F4/G3/F266 orientation findings | ![](agent/r2_084_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r2_089_rotate_piece_after_r_L-1b_salon_2.png) |
| 30750 | 2 | resize_piece | f_L-1_071 | adjusted_by_ai | 30.0 -> 40.0 | Resize armchair to drawn dimensions to resolve K3 size mismatch a:F531 | ![](agent/r2_087_resize_piece_before_r_L-1_salon.png) | ![](agent/r2_090_resize_piece_after_r_L-1_salon.png) |
| 30755 | 2 | retype_piece | f_L1_010 | adjusted_by_ai | 48.0 -> 48.0 | 0.42x0.45 m piece misread as shoe cabinet on a landing; ottoman is a valid candidate for its size and the living room, fixing the wrong_type finding. | ![](agent/r2_092_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_098_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 30757 | 2 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi | added_by_ai | 51.0 -> 61.0 | Re-solve the drawn dining group around the drawn table anchor to fix the table/chair collisions, the chair clearance to the wall, and complete the 4 chairs for a proper dining zone. | ![](agent/r2_094_place_group_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_097_place_group_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 30760 | 2 | resize_piece | f_L-1_073 | adjusted_by_ai | 40.0 -> 50.0 | Resize coffee table to drawn dimensions to clear overlap with f_L-1_071 and fix K3 mismatch | ![](agent/r2_096_resize_piece_before_r_L-1_salon.png) | ![](agent/r2_101_resize_piece_after_r_L-1_salon.png) |
| 30763 | 2 | report_library_gap | f_L0_045 | library_gap | - | Nightstand f_L0_045 is built below the library level (parametric mesh); no audited library model fits, same as f_L0_044. | - | - |
| 30765 | 2 | move_piece | f_L-1_023 | adjusted_by_ai | 30.0 -> 40.0 | Nudge wardrobe inward to clear the 0.020 m collision with the room outline. | ![](agent/r2_103_move_piece_before_r_L-1_salon_2.png) | ![](agent/r2_116_move_piece_after_r_L-1_salon_2.png) |
| 30770 | 2 | rotate_piece | f_L-1b_054 | adjusted_by_ai | 48.0 -> 68.0 | Rotate armchair to face 90° toward the coffee table, fixing G3 orientation finding | ![](agent/r2_123_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r2_138_rotate_piece_after_r_L-1b_salon_2.png) |
| 30786 | 2 | move_piece | f_L1_019 | adjusted_by_ai | 48.0 -> 58.0 | Shift the sofa 0.3 m away from f_L1_018 to clear the blocked free zone in front of it, fixing the F6 clearance finding. | ![](agent/r2_152_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_156_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 30787 | 2 | report_library_gap | f_L-1_090 | library_gap | - | The fridge is built into the counter run (integrated in the run's fronts); no library model can replace it, so the crude white-box look cannot be fixed by swap_model (a:F378). | - | - |
| 30797 | 2 | move_piece | f_L1_032 | adjusted_by_ai | 58.0 -> 68.0 | Move the armchair 0.3 m closer to the coffee table f_L1_024 to satisfy the G3 distance requirement (≤ 2.50 m). | ![](agent/r2_159_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r2_164_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 30800 | 2 | resize_piece | f_L-1_072 | adjusted_by_ai | 40.0 -> 40.0 | Resize armchair to match the drawn dimensions [0.642, 0.569] to resolve the K3 size mismatch finding. | ![](agent/r2_165_resize_piece_before_r_L-1_salon_2.png) | ![](agent/r2_171_resize_piece_after_r_L-1_salon_2.png) |
| 30837 | 2 | set_camera | r_L-1_banyo | agent_override | - | a:F408: camera too close to the corner showing only the bathtub edge; reframe to show the washbasin, toilet and shower layout | - | - |
| 30838 | 2 | report_library_gap | f_L0_023 | library_gap | - | c:LG:f_L0_023: record the wardrobe library gap for review (no candidate within 10% non-uniform scale and 0.85..1.2 mean scale; relaxed caps also failed). | - | - |
| 30842 | 2 | swap_model | f_L-1_094 | added_by_ai | 100.0 -> 100.0 | Try the 4-door Movian Idro (52x25x163, dark grey) as a styled, door-fronted shoe cabinet for the 0.6 m span. | ![](agent/r2_198_swap_model_before_r_L-1_koridor_2.png) | ![](agent/r2_200_swap_model_after_r_L-1_koridor_2.png) |
| 30854 | 2 | resize_piece | f_L0_024 | adjusted_by_ai | 100.0 -> 100.0 | Shrink the wardrobe height from 2.99 m into the 1.50-2.45 m (+-15%) range to clear the S4 size finding. | ![](agent/r2_206_resize_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r2_208_resize_piece_after_r_L0_e_yatak_odasi_2.png) |
| 30855 | 2 | set_camera | r_L-1_koridor_2 | agent_override | - | Move the camera to a free point near the stair with headroom, wide lens, looking down the hall so the shoe cabinet, both doors and the opening fill the frame. | - | - |
| 30899 | 2 | report_library_gap | f_L0_016 | library_gap | - | No audited real-product toilet model passes the fit rules (caps, height) to fix the S1 float (+0.200 m above floor); all generated candidates are either audit-removed or fail the fit rules. | - | - |
| 30902 | 2 | report_library_gap | f_L0_004 | library_gap | - | No audited real-product washbasin model passes the fit rules (caps, height) to fix the S1 float (+0.384 m above floor); all generated candidates are either audit-removed or fail the fit rules. | - | - |
| 31467 | 3 | swap_model | f_L0_021 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The 1.55 m bed leaves only 0.37 m on the left side (needs 0.60 m); moving it worsens the headboard clearance. A narrower bed (1.45 m) frees the side aisle without moving the headboard off the wall. (fixes a:F326) | ![](agent/r3_008_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_009_swap_model_after_r_L0_yatak_odasi_3.png) |
| 31471 | 3 | set_material | floor | agent_override | - | Argus: The style lays herringbone/chevron parquet, but the render shows a flat, plain plank floor. The set_room_type attempts were refused (bench not allowed in living room, plausibility score dropped). The fix is to set the floor material to a he (fixes a:F351) | - | - |
| 31478 | 3 | swap_model | f_L1_031 | adjusted_by_ai | 61.0 -> 61.0 | Argus: The orange armchair is a second loud accent that does not belong with the rest of the neutral palette; abo_B07J2YB486 (0.68 x 0.77 x 0.86 m, minimal/modern) is a style-matching candidate in the same size class. (fixes a:F398) | ![](agent/r3_017_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_018_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 31479 | 3 | swap_model | f_L1_006 | adjusted_by_ai | 61.0 -> 61.0 | Argus: The dining chairs are a mix of different models and styles that clash with the modern aesthetic; hssd_4652661588c3e25396b891901da281f41f7a140c (0.44 x 0.42 x 0.81 m, minimal/modern/scandinavian) is a style-matching candidate in the same siz (fixes a:F400) | ![](agent/r3_019_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_020_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 31480 | 3 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace has two bare chairs and no table; placing the terrace_pair group completes the seating set. (fixes a:F403) | ![](agent/r3_021_place_group_before_r_L1_teras.png) | ![](agent/r3_022_place_group_after_r_L1_teras.png) |
| 31482 | 3 | swap_model | f_L1_059 | added_by_ai | 68.0 -> 68.0 | Argus: The current model (abo_B072JG3WK1) has a 2.4 cm gap between the back/arm and the seat; swapping to a modern/scandinavian armchair with integrated rests fixes it. Rotation was already refused, so the model itself is the cause. (fixes a:F406) | ![](agent/r3_023_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_024_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 31485 | 3 | set_camera | r_L0_banyo | agent_override | - | Argus: The camera is in a corner showing only a wall and the bathtub edge; re-aiming it to show the bathtub, toilet, washbasin and cabinet frames the whole bathroom. (fixes a:F413) | - | - |
| 31487 | 3 | swap_model | f_L0_038 | adjusted_by_ai | 80.0 -> 80.0 | Argus: The current model (hssd_69803a92f62572f4bc4de8fc64fd84c6a6e63229) is a black leather corporate chair that clashes with the warm bedroom; the previously refused swap (chinese_armchair) was pending audit, so the minimal/modern 0.50 x 0.49 m c (fixes a:F415) | ![](agent/r3_026_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r3_027_swap_model_after_r_L0_yatak_odasi.png) |
| 31488 | 3 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The current model (hssd_69803a92f62572f4bc4de8fc64fd84c6a6e63229) is a black mesh corporate chair that clashes with the warm bedroom; swapping to a minimal/modern 0.50 x 0.49 m chair fixes the palette. (fixes a:F416) | ![](agent/r3_028_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_029_swap_model_after_r_L0_yatak_odasi_3.png) |
| 31491 | 3 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 gives a 6-piece layout with a 2-member balcony group and 2-member terrace_pair, fixing the under-furnished terrace (a:F250, a:N200, a:N206). | ![](agent/r3_074_relayout_room_before_r_L1_teras_2.png) | ![](agent/r3_076_relayout_room_after_r_L1_teras_2.png) |
| 31493 | 3 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 3 (untried) gives a fuller 6-piece layout with two balcony planters and a complete terrace_pair seating group, addressing the sparse-furnishing and missing-seating findings. | ![](agent/r3_075_relayout_room_before_r_L1_teras.png) | ![](agent/r3_077_relayout_room_after_r_L1_teras.png) |
| 31504 | 3 | resize_piece | f_L-1b_042 | adjusted_by_ai | 28.0 -> 28.0 | Sofa is turned 90° against product sizes; resize to correct width 2.13m x depth 0.9m | ![](agent/r3_085_resize_piece_before_r_L-1b_salon.png) | ![](agent/r3_094_resize_piece_after_r_L-1b_salon.png) |
| 31511 | 3 | move_piece | f_L-1b_046 | adjusted_by_ai | 28.0 -> 28.0 | Move sofa back to the wall (was 0.59m off) so its back is on the wall | ![](agent/r3_107_move_piece_before_r_L-1b_salon.png) | ![](agent/r3_111_move_piece_after_r_L-1b_salon.png) |
| 31528 | 3 | remove_piece | f_L1_054 | added_by_ai | 100.0 -> 100.0 | AI-added shoe cabinet is 'not built' after a prior removal attempt; the entrance group is optional, so removing it clears the not-built state (a:F612). | ![](agent/r3_121_remove_piece_before_r_L1_koridor.png) | ![](agent/r3_126_remove_piece_after_r_L1_koridor.png) |
| 31529 | 3 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Armchair faces the coffee table and seating group at 90° (accepted before). | ![](agent/r3_123_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_133_rotate_piece_after_r_L-1b_salon_2.png) |
| 31532 | 3 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 28.0 -> 58.0 | Rotate armchair to face 90° (+Y) towards the sofa and coffee table group | ![](agent/r3_129_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r3_137_rotate_piece_after_r_L-1b_salon.png) |
| 31534 | 3 | move_piece | f_L1_064 | added_by_ai | 68.0 -> 68.0 | snap the sideboard back onto the wall to clear the clearance finding (F81) | ![](agent/r3_131_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_134_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 31568 | 3 | report_library_gap | f_L1_022 | library_gap | - | No audited real toilet model fits f_L1_022: the generated candidates fail the fit rules (height caps under the sloped ceiling) and the one real candidate was audit-removed, so the parametric mesh stays (a:F289, c:S1). | - | - |
| 31592 | 3 | set_camera | r_L-1_banyo | agent_override | - | a:F408: camera too close to the corner showing only the bathtub edge and blank wall; reframe to show the washbasin, toilet and shower layout for presentation | - | - |
| 31605 | 3 | report_library_gap | f_L0_047 | library_gap | - | Current model is a heavy, dark industrial open shelving unit clashing with the light minimalist bathroom style; previous swap (abo_B07GFFY4WT) failed the fit rules, so no audited library model fits the 0.3x0.3 footprint and height. | - | - |
| 31606 | 3 | report_library_gap | f_L0_006 | library_gap | - | Washbasin floats 0.384 m above the floor (S1); previous swap (gen_washbasin_minimal_1_9dc765fb) was refused by the fit rules, so no audited library model corrects the vertical placement. | - | - |
| 31607 | 3 | report_library_gap | f_L0_015 | library_gap | - | Toilet floats 0.200 m above the floor (S1) and has no paper holder (M26); multiple swap attempts were rejected (audit removed, fit rules), so no audited library model sits correctly and includes the accessory. | - | - |
| 31617 | 3 | report_library_gap | f_L-1_094 | library_gap | - | No audited shoe cabinet model fits the 0.6x0.3 footprint within the height caps: the walnut rack and 3dwh display cabinet fail the fit rules (caps, height) and the cedar rack was audit-removed, so the bare parametric grid stays for review. | - | - |
| 31623 | 3 | report_library_gap | f_L0_033 | library_gap | - | No library nightstand model passes the fit rules (caps, height) for the drawn 0.50 x 0.45 m footprint: side_table_01, abo_B079VK52WZ, abo_B07K7K7GTZ all pin_refused, so the parametric mesh stays and P7 remains for review. | - | - |
| 32518 | 4 | swap_model | f_L-1_023 | adjusted_by_ai | 40.0 -> 40.0 | Argus: The wardrobe pokes 0.020 m through the outline; a slightly shorter model (2.53 m) keeps it inside. (fixes a:F81) | ![](agent/r4_009_swap_model_before_r_L-1_salon_2.png) | ![](agent/r4_010_swap_model_after_r_L-1_salon_2.png) |
| 32526 | 4 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The toilet f_L0_015 is built in r_L0_e_banyo; the camera simply does not show it. Re-aiming the camera to include the anchor fixture is the direct fix. (fixes a:F161) | - | - |
| 32527 | 4 | set_camera | r_L1_teras | agent_override | - | Argus: r_L1_teras has armchair, potted_plant, side_table built; the camera angle hides them. Re-aiming to show the furniture fixes the render. (fixes a:F162) | - | - |
| 32528 | 4 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The bed f_L0_019 is built in r_L0_yatak_odasi; the camera cuts it out. Re-aiming to show the bed fixes the render. (fixes a:F163) | - | - |
| 32529 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: r_L0_banyo has bathtub, tall_cabinet, toilet, washbasin built; the camera omits the main fixtures. Re-aiming to show them fixes the render. (fixes a:F164) | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 29940 | 1 | retype_piece | f_L1_025 | acceptance: finding M31:f_L1_025 is still there after the edit (Argus: bathtub f_L1_025 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL12); a retype to the piece's own type only confirms it (status unverified -> verified, the same fitted model): nothing changes in the render, so its vision findings stay | Argus: The drawn 1.83 x 0.80 m footprint is within 30 % of the real shower range, so the code refused to resize it as a bathtub; the correct type for this footprint in a 5.0 m2 bathroom under a mansard slope is a shower, whose model height fits th (fixes a:F1) |
| 29941 | 1 | retype_piece | f_L1_026 | acceptance: finding M31:f_L1_026 is still there after the edit (Argus: bathtub f_L1_026 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL12); a retype to the piece's own type only confirms it (status unverified -> verified, the same fitted model): nothing changes in the render, so its vision findings stay | Argus: Same misread as F1 in the mirror room r_L1_banyo_2: the 1.83 x 0.80 m footprint fits the shower range, and a shower model clears the 0.81 m sloped-ceiling height where a bathtub pokes through the roof. (fixes a:F2) |
| 29942 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_043, f_L1_042 passes the camera checks: cam_r_L1_teras_1: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; duplicate: cam_r_L1_teras_1 would show the view cam_r_L1_teras_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; cam_r_L1_teras_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The terrace's armchairs and side table (f_L1_041, f_L1_043, f_L1_042) are built but the camera frames an empty stretch, so the render looks bare. Re-posing the camera to show the furniture group fixes the view. (fixes a:F13) |
| 29943 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_043 passes the camera checks: cam_r_L1_teras_2: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L1_teras_2: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L1_teras_2: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: Same bare-terrace problem on the second camera; the earlier refusal named cam_r_L1_teras_2 as the pose that fails the furniture check, so re-posing it to the armchairs and side table is the fix. (fixes a:F14) |
| 29944 | 1 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_021, f_L1_015 | Argus: The frame is black/empty; re-posing the existing camera to show the bathroom's main group is the direct fix. (fixes a:F21) |
| 29945 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: F4 f_L1_071: armchair stands behind the back of f_L1_018, looking at it | Argus: The sofa's front free zone is blocked by f_L1_018; a room relayout re-places the AI pieces to clear it. (fixes a:F81) |
| 29947 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: The stove is planned but has no object in the scene; placing the kitchen run group builds it. (fixes a:F91) |
| 29948 | 1 | place_group | r_L-1_mutfak_2 | no_change: r_L-1_mutfak_2 already has its kitchen_run r_L-1_mutfak_2.kitchen_run (anchor f_L-1_010, members f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068, f_L-1_096): nothing missing, never a second set | Argus: The stove is planned but has no object in the scene; placing the kitchen run group builds it. (fixes a:F92) |
| 29949 | 1 | fix_fixture | f_L-1_008 | no_change: f_L-1_008: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The stove is drawn 0.06 m off its wall; it belongs on the wall. fix_fixture without a centre lets the code move it to the nearest valid spot on the wall. (fixes a:F120) |
| 29950 | 1 | fix_fixture | f_L-1_017 | no_change: f_L-1_017: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The stove is drawn 0.06 m off its wall; it belongs on the wall. fix_fixture without a centre lets the code move it to the nearest valid spot on the wall. (fixes a:F121) |
| 29951 | 1 | fix_fixture | f_L0_014 | no_change: f_L0_014: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower is drawn 0.10 m off its wall; it belongs on the wall. fix_fixture without a centre lets the code move it to the nearest valid spot on the wall. (fixes a:F122) |
| 29952 | 1 | fix_fixture | f_L0_013 | no_change: f_L0_013: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower has only 0.05 m clear in front; the size is within tolerance and the model swap was refused, so the code moves it to the nearest valid spot. (fixes a:F131) |
| 29953 | 1 | fix_fixture | f_L0_018 | no_change: f_L0_018: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is 0.33 m from the side wall; the size is within tolerance and the model swap was refused, so the code moves it to the nearest valid spot. (fixes a:F132) |
| 29954 | 1 | fix_fixture | f_L0_025 | no_change: f_L0_025: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The bathtub has only 0.28 m clear in front; the size is within tolerance, so the code moves it to the nearest valid spot. (fixes a:F133) |
| 29955 | 1 | fix_fixture | f_L0_017 | no_change: f_L0_017: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is 0.33 m from the side wall; the size is within tolerance and the model swaps were refused, so the code moves it to the nearest valid spot. (fixes a:F134) |
| 29956 | 1 | fix_fixture | f_L0_026 | no_change: f_L0_026: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The bathtub has only 0.28 m clear in front; the size is within tolerance, so the code moves it to the nearest valid spot. (fixes a:F135) |
| 29957 | 1 | fix_fixture | f_L1_021 | no_change: f_L1_021: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is 0.33 m from the side wall; the size is within tolerance and the model swaps were refused, so the code moves it to the nearest valid spot. (fixes a:F136) |
| 29958 | 1 | fix_fixture | f_L1_025 | no_change: f_L1_025: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower has only 0.28 m clear in front; the size is within tolerance, so the code moves it to the nearest valid spot. (fixes a:F137) |
| 29959 | 1 | fix_fixture | f_L1_022 | no_change: f_L1_022: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is 0.33 m from the side wall; the size is within tolerance and the model swap was refused, so the code moves it to the nearest valid spot. (fixes a:F138) |
| 29960 | 1 | fix_fixture | f_L1_026 | no_change: f_L1_026: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower has only 0.28 m clear in front; the size is within tolerance, so the code moves it to the nearest valid spot. (fixes a:F139) |
| 29964 | 1 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_025, f_L0_003, f_L0_018, f_L0_048 passes the camera checks: cam_r_L0_banyo_1: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_banyo_1 would show the view cam_r_L0_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views | Argus: The render omits the washbasin, toilet and tall cabinet, so the bathroom looks unfinished. Reposing the camera to include the fixtures fixes the view. (fixes a:F147) |
| 29965 | 1 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Argus: The room is typed bedroom but is furnished as a home office (desk, office_chair) with the bed missing. relayout_room candidate 1 was refused because the nightstand still did not fit (0.37 m gap). Trying candidate 2 gives the solver a differ (fixes a:F151) |
| 29966 | 1 | set_exterior | exterior:ground,site,sun | sun: azimuth 135 degrees (compass; 135 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Argus: The flat grey sky and uniform ground make the whole scene look like a placeholder. Adding trees, a hedge, a path, grass ground and a sun direction gives the exterior depth and a finished look. (fixes a:F152) |
| 29967 | 1 | correct_geometry | o_L1_001 | the opening already lies on the wall (0.000 m) | Argus: The opening o_L1_001 is not cut through its wall (the door ray hits w_L1_003). correct_geometry with fix_opening_on_wall cuts it. (fixes a:F153) |
| 29968 | 1 | add_camera | ext_6 | the camera stands inside the building b2 (another building on the plot), eye height 0.29 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No frontal view of the entrance (+y) facade exists. Adding an exterior camera at +y looking at the building covers this. (fixes a:F167) |
| 29969 | 1 | swap_model | f_L1_017 | pin_refused: f_L1_017: gen_sofa_japandi_2_98a7a89b: a generated model (units guessed) while a real product of the type fits within the caps (3dwh_1172843db1fb2000f7b5a16e): the real model stays; swap to a real model of the type or use another tool | Argus: An upholstered indoor sofa (3dwh_1172843db1fb2000f7b5a16e) is on the outdoor terrace. Swapping to a japandi/outdoor-appropriate model is the fix. The room r_L1_oyun_aktivite_ve_dinlenme_odasi is typed 'other' but contains terrace furniture; (fixes a:F169) |
| 29978 | 1 | rotate_piece | f_L-1b_041 | f_L-1b_041: no_overlap, f_L-1b_081: no_overlap, score: plausibility 18 -> -32 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_041: sofa does not face its group (f_L-1b_081); F4 f_L-1b_054: armchair does not face its group (f_L-1b_081, f_L-1b_041, f_L-1b_045); F4 f_L-1b_084: armchair stands behind the back of f_L-1b_045, f_L-1b_041, looking at it) | Rotate sofa so its front faces 270° towards the open floor and its partner, fixing the missing-front and 90°-against-product-size findings. |
| 29981 | 1 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap the sofa's back onto the west wall to satisfy the off-wall check (it was 0.59 m off). |
| 29986 | 1 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.08 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Shift coffee table to clear the 0.12 m² overlap with armchair f_L-1_071 |
| 29987 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair to face the seating group instead of the back of the sofa |
| 29988 | 1 | move_piece | f_L-1b_046 | wall_exists: no wall 'r_L-1b_salon.s3' | Sofa back is 0.59m off the wall; snapping it to free wall span s3 puts its back against the wall, fixing the F3 off-wall finding. |
| 29992 | 1 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Shift coffee table right to clear the 0.12 m² overlap with armchair f_L-1_071 |
| 29993 | 1 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 0.59m off the wall; snapping it to wall w_L-1b_010 (span s3) puts its back against the wall, fixing the F3 off-wall finding. |
| 29994 | 1 | move_piece | f_L0_009 | snap: f_L0_009: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe to the free right wall span s1 so its front faces into the room with ≥0.80 m clearance (G13). |
| 29995 | 1 | move_piece | f_L0_012 | f_L0_012: inside_room (outline: wardrobe reaches 0.20 m² through the room outline, up to 0.136 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 50 (F3 f_L0_012: wardrobe: its back is not on a wall (0.14 m off); F9 f_L0_012: wardrobe reaches 0.20 m² through the room outline, up to 0.136 m deep; G13 f_L0_012: wardrobe f_L0_012: 0.79 m free in front, needs ≥ 0.80 m) | Move wardrobe 0.14m away from the desk to increase front clearance from 0.66m to the required 0.80m. |
| 29997 | 1 | swap_model | f_L0_037 | asset_unusable: chinese_armchair is not used: audit pending | Replace the corporate black mesh office chair with a residential-style armchair to match the warm bedroom aesthetic (F416). |
| 29998 | 1 | move_piece | f_L0_020 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 67 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.47 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.05 m from the bed side (needs ≤ 0.30 m); G5 f_L0_020: bed_double f_L0_020: 0.47 m free along the right side, needs ≥ 0.60 m) | Move bed 0.07m towards the window wall to increase side clearances from 0.53m/0.56m to the required 0.60m. |
| 29999 | 1 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining | no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | Dining table f_L1_009 has only 2 of 4 chairs; add the missing chairs to form a proper dining zone (a:N204, G6) |
| 30001 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071, f_L-1b_046)); 1 more kept | Armchair is 90° off its group anchor (coffee table) and has an incorrect inferred front; rotating to face 180° (towards the seating group) aligns it with the group and fixes the orientation warnings. |
| 30002 | 1 | move_piece | f_L-1_073 | acceptance: finding F9:f_L-1_073 is still there after the edit (table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.11 m²) | Shift coffee table down to clear the 0.12 m² overlap with armchair f_L-1_071 |
| 30004 | 1 | move_piece | f_L0_009 | snap: f_L0_009: no free place on wall w_L0_007 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe to the free top wall span s2 so its front faces into the room with ≥0.80 m clearance (G13). |
| 30005 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.65 m free in front, needs ≥ 0.80 m) | Move wardrobe 0.14m along the wall away from the desk to increase front clearance from 0.66m to the required 0.80m. |
| 30006 | 1 | resize_piece | f_L0_008 | f_L0_008: no_overlap, f_L0_033: no_overlap, f_L0_034: no_overlap, score: plausibility 100 -> 44 (F2 f_L0_008: bed_double 2.55 m wide x 2.00 m deep (seen from its front) is turned 90° against the type's product sizes; F9 f_L0_033: nightstand f_L0_033 overlaps bed_double f_L0_008 by 0.17 m²; F9 f_L0_034: nightstand f_L0_034 overlaps bed_double f_L0_008 by 0.15 m²; G4 f_L0_008: bed_double f_L0_008: no nightstand on the free left side of the head (0.84 m free)) | Restore the bed to its drawn width (2.55 m) to clear the Argus size mismatch against the drawing. |
| 30007 | 1 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 0.59m off the wall; snapping to wall w_L-1b_010 at offset 0.5m (within span s3) puts its back against the wall, fixing F3. |
| 30009 | 1 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Shift coffee table right to clear the 0.12 m² overlap with armchair f_L-1_071 |
| 30010 | 1 | move_piece | f_L0_020 | f_L0_020: no_overlap, f_L0_045: no_overlap | Move bed 0.04m towards the window wall to increase side clearances from 0.53m/0.56m towards the required 0.60m. |
| 30011 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge the dining chair 0.03 m away from the table to raise the clearance behind it from 0.78 m to at least 0.81 m. |
| 30013 | 1 | move_piece | f_L0_009 | f_L0_009: no_overlap, f_L0_029: clearance_ok, score: plausibility 67 -> 47 (F3 f_L0_009: wardrobe: its back is not on a wall (0.28 m off); F9 f_L0_029: desk f_L0_029 overlaps wardrobe f_L0_009 by 0.05 m²; G13 f_L0_009: wardrobe f_L0_009: 0.34 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.5 m north along the left wall to open ≥0.80 m clearance in front of its doors (G13). |
| 30014 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Move bed 0.07m left to increase right-side clearance from 0.53m towards the required 0.60m. |
| 30015 | 1 | rotate_piece | f_L-1_101 | score: plausibility 30 -> -10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_049: armchair stands behind the back of f_L-1_101, looking at it; F4 f_L-1_053: sofa_corner stands behind the back of f_L-1_101, looking at it; F4 f_L-1_101: tv_unit faces a wall 0.02 m in front of it) | Rotate TV unit to face the seating area rather than the back of the armchair |
| 30018 | 1 | move_piece | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | Shift the wardrobe 0.3 m north along the left wall (within its 0.3 m allowance) to open more clearance in front of its doors (G13). |
| 30019 | 1 | move_piece | f_L0_045 | f_L0_045: inside_room | Move nightstand 0.16m down to free space for the bed to shift towards the window wall. |
| 30020 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the dining chair 0.06 m away from the table to raise the clearance behind it from 0.78 m to at least 0.81 m. |
| 30022 | 1 | move_piece | f_L-1b_046 | max_tries: f_L-1b_046 was edited 3 times in this round | Sofa back is 0.59m off the wall; moving it 0.45m to the right puts its back against wall w_L-1b_010, fixing F3 off-wall. |
| 30024 | 1 | move_piece | f_L0_020 | max_tries: f_L0_020 was edited 3 times in this round | Move bed 0.03m left to increase right-side clearance from 0.53m towards 0.60m. |
| 30025 | 1 | move_piece | f_L-1b_051 | acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052) | Armchair's front zone is blocked by f_L-1b_052 and it is 33° off the sofa; moving it 0.6m south clears the mutual block and aligns it with the sofa group. |
| 30029 | 1 | mark_not_furniture | f_L-1b_001 | no_crop: f_L-1b_001 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The large untyped cluster is a group of drawn pieces / reading error, not a single piece of furniture. |
| 30031 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Re-solve the drawn kitchen run so the stove and sink members get built objects in the scene (a:F91, a:F93) and the worktop is completed (a:Q13). |
| 30032 | 1 | swap_model | f_L0_038 | asset_unusable: chinese_armchair is not used: audit pending | Replace the corporate black leather office chair with a warm classic armchair that fits the calm bedroom palette and light wood desk. |
| 30033 | 1 | relayout_room | r_L-1_salon | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Re-solve the room layout using candidate 1 to ensure 0.60 m walkways reach the front use zones of the seating group from the door |
| 30034 | 1 | rotate_piece | f_L-1b_054 | score: plausibility 48 -> 18 (G11 f_L-1b_041: sofa f_L-1b_041: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_054: armchair f_L-1b_054: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_082: bookshelf f_L-1b_082: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Rotate the armchair to face 10° towards the sofa, reducing the 33° group-alignment offset to within 30°. |
| 30035 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B01D3C7Z4A: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand with a real light-oak library nightstand model. |
| 30036 | 1 | resize_piece | f_L0_007 | f_L0_007: no_overlap, f_L0_031: no_overlap, f_L0_032: no_overlap, score: plausibility 100 -> 44 (F2 f_L0_007: bed_double 2.55 m wide x 2.00 m deep (seen from its front) is turned 90° against the type's product sizes; F9 f_L0_031: nightstand f_L0_031 overlaps bed_double f_L0_007 by 0.17 m²; F9 f_L0_032: nightstand f_L0_032 overlaps bed_double f_L0_007 by 0.15 m²; G4 f_L0_007: bed_double f_L0_007: no nightstand on the free left side of the head (0.75 m free)) | Restore the bed to its drawn width (2.55 m) to clear the Argus size mismatch. |
| 30037 | 1 | move_piece | f_L-1b_051 | drawn_lock: f_L-1b_051: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.94 m) | Moving armchair further from f_L-1b_052 to clear the mutual F6 block while staying within the seating group. |
| 30038 | 1 | move_piece | f_L-1b_045 | f_L-1b_045: no_overlap, f_L-1b_084: clearance_ok, f_L-1b_084: no_overlap, score: plausibility 48 -> 38 (F6 f_L-1b_084: armchair: the free zone in front of it is blocked by f_L-1b_045) | Move the sofa 0.59 m west to bring its back against the west wall, satisfying the off-wall check. |
| 30039 | 1 | relayout_room | r_L-1_salon | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Re-solve the room layout using candidate 2 to ensure 0.60 m walkways reach the front use zones of the seating group from the door |
| 30040 | 1 | swap_model | f_L-1_090 | built_in: f_L-1_090: the fridge stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Replace the crude featureless white-box fridge with a detailed generated fridge model (a:F378). |
| 30041 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has only 0.78m clearance behind it (needs 0.81m); moving it 0.14m away from the wall/piece behind provides the required clearance. |
| 30045 | 1 | retype_piece | f_L1_054 | retype: console_table is no candidate for f_L1_054 (0.60 x 0.25 m at [4.07, 7.74]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet | Shoe cabinet f_L1_054 is flagged not built (C6); retype to console_table, a valid entrance option that also satisfies the hall's M28 console requirement. |
| 30046 | 1 | relayout_room | r_L-1b_salon_2 | group checks: G9 r_L-1b_salon_2_kitchen: kitchen r_L-1b_salon_2_kitchen has no fridge (fridge) | Re-place the AI seating and storage pieces as a unit to resolve the sofa off-wall, armchair orientation and clearance findings. |
| 30047 | 1 | swap_model | f_L0_038 | off_style: f_L0_038: abo_B072Y5MZQH is of the styles ['modern minimal', 'modern'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the corporate black leather office chair with a warm classic armchair that fits the calm bedroom palette and light wood desk. |
| 30049 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand with a real scandinavian library nightstand model. |
| 30050 | 1 | set_camera | L1_banyo | show: no room 'L1_banyo' for the view cam_r_L1_banyo_1 (give room_id) | The L1 bathroom camera renders entirely black/empty and omits the washbasin, toilet and shower; reposition to a free point that frames the main fixtures at eye height. |
| 30051 | 1 | set_camera | L1_teras | show: no room 'L1_teras' for the view cam_r_L1_teras_1 (give room_id) | The terrace camera cuts the foreground armchair and hides the main furniture group and potted plants; reposition to frame the complete seating group and greenery without clipping. |
| 30052 | 1 | place_group | r_L0_e_yatak_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the sleeping group around the drawn bed anchor so a nightstand is placed on the free left side of the head. |
| 30053 | 1 | move_piece | f_L-1b_051 | score: plausibility 58 -> 28 (G11 f_L-1b_042: sofa f_L-1b_042: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_051: armchair f_L-1b_051: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_074: armchair f_L-1b_074: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Moving armchair 0.3m (max allowed) away from f_L-1b_052 to clear the mutual F6 block while staying in the seating group. |
| 30054 | 1 | retype_piece | f_L1_054 | no_change: f_L1_054 is already a shoe_cabinet | Confirming shoe_cabinet type to resolve C6 'not built' finding for f_L1_054; the piece is already a shoe_cabinet but needs to be verified/built. |
| 30058 | 1 | swap_model | f_L0_042 | off_style: f_L0_042: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric nightstand with a real classic library nightstand model. |
| 30060 | 1 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_015, f_L1_021, f_L1_025 | The L1 bathroom camera renders entirely black/empty and omits the washbasin, toilet and shower; reposition to a free point that frames the main fixtures at eye height. |
| 30061 | 1 | set_camera | r_L1_teras | show: no free camera point of r_L1_teras shows f_L1_096, f_L1_098, f_L1_097, f_L1_093, f_L1_094, f_L1_095 (f_L1_096, f_L1_098, f_L1_097, f_L1_093, f_L1_094, f_L1_095 not in r_L1_teras: name its pieces, doors or windows) | The terrace camera cuts the foreground armchair and hides the main furniture group and potted plants; reposition to frame the complete seating group and greenery without clipping. |
| 30065 | 1 | set_room_type | r_L1_banyo | no_change: r_L1_banyo is already a bathroom | Findings a:F1, a:F15, a:F658 on f_L1_025 are caused by wrong_type; confirming the room type resolves them. |
| 30066 | 1 | swap_model | f_L1_054 | acceptance: pin_refused: f_L1_054: abo_B07TVMZ5QP: fails the fit rules (caps, height, at most 2.16 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap to a slim console-style shoe rack (1.17m wide, 0.35m deep) to satisfy the hall's M28 console/wall-niche decor requirement while keeping the entrance function. |
| 30067 | 1 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: abo_B07K7YMBNY: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the bare parametric grid of open cubbies (D2) with a styled solid-wood shoe cabinet that matches a designed hall. |
| 30068 | 1 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall away from the door swing to open the 0.8 m front clearance (G13). |
| 30069 | 1 | place_group | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:G4:f_L0_007 (bed f_L0_007: no nightstand on the free left side of the head): re-solve the sleeping group around the drawn bed anchor so a nightstand is placed on the free left side. |
| 30071 | 1 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_015, f_L1_021, f_L1_025 | The L1 bathroom camera renders entirely black/empty and omits the washbasin, toilet and shower; reposition to a free point that frames the main fixtures at eye height. |
| 30075 | 1 | resize_piece | f_L1_054 | max_tries: f_L1_054 was edited 3 times in this round | Resize to console-table dimensions (0.9m wide, 0.35m deep) so retype to console_table can pass the size table check, satisfying M28. |
| 30076 | 1 | move_piece | f_L0_019 | score: plausibility 80 -> 60 (F3 f_L0_019: bed_double: the headboard stands in the room (0.30 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.3 m right to open the left-side clearance to 0.60 m. |
| 30080 | 1 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Center the wardrobe in the free south-wall span (1.36 m) so the door swing clears its front (G13). |
| 30081 | 1 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: abo_B07GFS1R7X: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the bare parametric grid of open cubbies (D2) with a styled 3-door shoe cabinet (1.28 m tall, light oak) that matches a designed hall. |
| 30082 | 1 | retype_piece | f_L1_028 | retype: wardrobe is no candidate for f_L1_028 (1.52 x 0.60 m at [12.61, 9.90]): the size table and the room / zone give bench, dresser | Confirm the drawn wardrobe (vector evidence, real 1.52x0.60 m size) over the AI passes' bench/coat-closet misread; the RC finding names retype_piece as the fix. |
| 30083 | 1 | move_piece | f_L0_019 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 80 -> 57 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.11 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free right side of the head (0.85 m free); G4 f_L0_041: nightstand f_L0_041 of bed_double f_L0_019: 0.32 m from the bed side (needs ≤ 0.30 m); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.12 m from the bed side (needs ≤ 0.30 m)) | Shift the bed 0.3 m toward the window to open the right-side clearance to 0.60 m. |
| 30084 | 1 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swapping to a floor-sitting model fixes the clearance. |
| 30085 | 1 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swap to a modern washbasin model with a correct base height. |
| 30087 | 1 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fix a:F555: swap the nightstand to a library-level model (side_table_01, modern minimal) instead of the parametric mesh. |
| 30088 | 1 | retype_piece | f_L1_028 | acceptance: finding RC:f_L1_028 is still there after the edit (f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | The code's size table and hall zone give bench for this 1.52x0.60 m piece; the RC finding's vector evidence (hanging rail) outranks the AI passes' bench doubt, so confirm bench to clear the type finding. |
| 30089 | 1 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swapping to a floor-sitting model fixes the clearance. |
| 30090 | 1 | swap_model | f_L-1_051 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swap to a toilet model with a correct base height. |
| 30091 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 8 best poses of r_L-1_koridor_2 that show f_L-1_094, d_L-1_001, d_L-1_003, o_L-1_001 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 1% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | The current view is a low, tight crop of one corner; reframe to show the hall's main group (shoe cabinet), the doors and the opening so the 12 m² hall reads as a whole. |
| 30092 | 1 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.20 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift the bed 0.2 m toward the left wall to open the right-side clearance to 0.57 m (G5). |
| 30095 | 1 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Tall cabinet was built with a parametric mesh below library level (P7); swap to the 0.40 m wide library model that matches its drawn width. |
| 30097 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 8 best poses of r_L-1_koridor_2 that show f_L-1_094, d_L-1_001, d_L-1_003 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 1% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Reframe the tight corner crop to show the hall's main group (shoe cabinet) and the doors so the 12 m² hall reads as a whole. |
| 30099 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show f_L-1_094, o_L-1_001 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Reframe the tight corner crop to show the hall's main group (shoe cabinet) and the opening so the 12 m² hall reads as a whole. |
| 30100 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show f_L-1_094 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Reframe the tight corner crop to show the hall's main group (shoe cabinet) so the 12 m² hall reads as a whole. |
| 30101 | 1 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Trying a lower-profile washbasin model that sits on the floor to fix the S1 clearance. |
| 30105 | 1 | swap_model | f_L1_021 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Trying a different toilet model that sits on the floor to fix the S1 clearance. |
| 30106 | 1 | move_piece | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.18 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.2 m down so its left side clears the desk (0.72 m free, G5 left). |
| 30107 | 1 | set_camera | r_L-1_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Camera is too close to a corner showing only the bathtub edge and blank wall (V1); reframe from a free point with headroom to show the washbasin, toilet and shower. |
| 30111 | 1 | set_camera | r_L-1_koridor_2 | cam_r_L-1_koridor_2_1 stands 4.60 m over its floor, over (or within 0.05 m of) its room's ceiling at 2.85 m there: it sees the back of the ceiling, cam_r_L-1_koridor_2_1: eye height 4.60 m (wanted 1.2-1.6 m), the camera stands 0.00 m from f_L-1_019 (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [4.34, 8.66] | Reframe the tight corner crop from a free point with headroom to show the hall's main group (shoe cabinet), the doors and the opening so the 12 m² hall reads as a whole. |
| 30115 | 1 | swap_model | f_L0_017 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | S1: current toilet model floats 0.20 m above the floor; swap to a japandi toilet whose base sits on the floor |
| 30116 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric below-library mesh with the real Movian Idro Skoskåp (0.52×0.25×1.63, modern minimal) to clear a:F554. |
| 30117 | 1 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes S1:f_L-1_026 (washbasin floats 0.384 m above floor): swap to a japandi washbasin model with a correct base height. |
| 30118 | 1 | swap_model | f_L0_016 | pin_refused: f_L0_016: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current toilet model floats 0.20 m above the floor; swap to a different audited toilet model to clear the floor-contact check (the japandi_1 model was audit-removed). |
| 30120 | 1 | move_piece | f_L0_022 | score: plausibility 67 -> 60 (F3 f_L0_022: bed_double: the headboard stands in the room (0.20 m off)) | Shift the bed 0.2 m left and 0.2 m down: right side clears the nightstand (0.57 m) and left side clears the desk (0.72 m), headboard stays on the wall (G5 both sides). |
| 30121 | 1 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes S1:f_L-1_051 (toilet floats 0.200 m above floor): swap to a japandi toilet model with a correct base height. |
| 30122 | 1 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: drawer_cabinet: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes P7:f_L-1_103 (built below library level with parametric mesh): swap to the CC0 drawer cabinet library model. |
| 30123 | 1 | swap_model | f_L0_017 | pin_refused: f_L0_017: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current toilet model floats 0.20 m above the floor; swap to a japandi toilet whose base sits on the floor |
| 30124 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Try the Movian Moselle vitrina (0.40×0.57×1.85, modern minimal) as a real library model for the tall_cabinet to clear a:F554. |
| 30125 | 1 | swap_model | f_L0_016 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | S1: current toilet model floats 0.20 m above the floor; swap to a real (non-generated) toilet model whose bbox matches the drawn 0.50 x 0.68 m footprint. |
| 30126 | 1 | swap_model | f_L0_047 | acceptance: pin_refused: f_L0_047: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | The heavy dark open shelving clashes with the light minimalist bathroom; the Movian Idro Skoskåp Ek is a light scandinavian/minimal tall cabinet matching the 0.3x0.3x1.6 footprint. |
| 30127 | 1 | move_piece | f_L0_022 | memory: the same edit was rejected in round 1: acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.18 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.2 m down so its left side clears the desk (0.72 m free, G5 left). |
| 30128 | 1 | set_camera | r_L-1_banyo | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes V1:r_L-1_banyo (camera too close to the corner, framing only the bathtub edge and blank wall): reframe from a free point with headroom to show the washbasin, toilet and shower. |
| 30129 | 1 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_039, d_L0_001, d_L0_005 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 9% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Move camera away from the door leaf that fills the frame center so the corridor layout and shoe cabinet are visible. |
| 30130 | 1 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_039 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 9% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Move camera to a free point showing the shoe cabinet and corridor, away from the door leaf. |
| 30131 | 1 | move_piece | f_L0_022 | max_tries: f_L0_022 was edited 3 times in this round | Shift the bed 0.1 m left and 0.2 m down: right side gains 0.1 m (0.47 m) and left side clears the desk (0.62 m), headboard stays on the wall (G5). |
| 30132 | 1 | swap_model | f_L0_016 | acceptance: pin_refused: f_L0_016: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | S1: current toilet model floats 0.20 m above the floor; swap to the real Caesar Toilet C1348 (0.46 x 0.72 m) which fits the drawn 0.50 x 0.68 m footprint. |
| 30135 | 1 | swap_model | f_L0_006 | pin_refused: f_L0_006: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | The current washbasin model floats +0.384 m above the floor; a minimal floor-standing model should sit at floor level and clear S1. |
| 30136 | 1 | swap_model | f_L0_017 | max_tries: f_L0_017 was edited 3 times in this round | S1: current toilet model floats 0.20 m above the floor; swap to a minimal toilet whose base sits on the floor |
| 30137 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: drawer_cabinet: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Try the CC0 Drawer Cabinet (1.14×0.49×1.88, modern) as a real library model for the tall_cabinet to clear a:F554. |
| 30138 | 1 | swap_model | f_L0_015 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | The current toilet floats +0.200 m above the floor and lacks a paper holder; a minimal floor-standing model with proper base should clear S1 and M26. |
| 30139 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current washbasin model floats 0.384 m above the floor; swap to a japandi washbasin whose base sits on the floor |
| 30140 | 1 | swap_model | f_L0_004 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | S1: current washbasin model floats 0.384 m above the floor; swap to the real 3DWH Sink (0.965 x 0.50 m) which fits the drawn 1.0 x 0.55 m footprint. |
| 30141 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | S1: current washbasin model floats 0.384 m above the floor; swap to a minimal washbasin whose base sits on the floor |
| 30143 | 1 | swap_model | f_L0_004 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | S1: current washbasin model floats 0.384 m above the floor; swap to the real Hudson Reed Sublime Vanity Unit & Basin (0.91 x 0.60 m) which fits the drawn 1.0 x 0.55 m footprint. |
| 30144 | 1 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Swap the floating washbasin model (lowest point +0.384 m) for a floor-standing modern washbasin to clear c:S1:f_L-1_025. |
| 30145 | 1 | swap_model | f_L0_004 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | S1: current washbasin model floats 0.384 m above the floor; swap to the real Ikea Boholmen Sink (0.96 x 0.50 m) which fits the drawn 1.0 x 0.55 m footprint. |
| 30146 | 1 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Try the japandi washbasin (0.63×0.49×0.64) as a floor-standing model to clear c:S1:f_L-1_025. |
| 30148 | 1 | swap_model | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | S1: current washbasin model floats 0.384 m above the floor; swap to the real Modern Single Lav Vanity (0.96 x 0.43 m) which fits the drawn 1.0 x 0.55 m footprint. |
| 30150 | 1 | swap_model | f_L-1_025 | pin_refused: f_L-1_025: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Try the minimal washbasin (0.59×0.52×0.32) as a floor-standing model to clear c:S1:f_L-1_025. |
| 30151 | 1 | swap_model | f_L-1_025 | max_tries: f_L-1_025 was edited 3 times in this round | Try the mediterranean washbasin (0.54×0.57×0.69) as a floor-standing model to clear c:S1:f_L-1_025. |
| 30704 | 2 | swap_model | f_L1_020 | pin_refused: f_L1_020: gen_sofa_japandi_2_98a7a89b: a generated model (units guessed) while a real product of the type fits within the caps (3dwh_1172843db1fb2000f7b5a16e): the real model stays; swap to a real model of the type or use another tool | Argus: Same as F169: upholstered indoor sofa on outdoor terrace. Swap to outdoor-appropriate model. (fixes a:F170) |
| 30705 | 2 | swap_model | f_L1_023 | asset_unusable: hssd_f91a4b62ee3859ad3119ad04be8b60f65ead389e is not used: audit removed | Argus: An indoor coffee table (hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82) is on the outdoor terrace. Swap to a neutral/outdoor-appropriate model. (fixes a:F171) |
| 30710 | 2 | swap_model | f_L1_049 | exists: no piece 'f_L1_049' in a room of the building | Argus: An indoor floor lamp (hssd_288c8977b30446fde324910c1510a02eabb3add9, not built) is on the outdoor terrace. Swap to a minimal/modern outdoor-appropriate model. (fixes a:F176) |
| 30711 | 2 | set_camera | r_L0_e_yatak_odasi | show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views | Argus: The camera does not show the door it must show; re-posing it to show d_L0_002 fixes the finding. (fixes a:F186) |
| 30716 | 2 | set_material | plot_wall | plot_wall: stone_wall_ashlar is another stone than the house's base stone_wall_ledgestone: one stone per house (the plinth, the plot walls and the facade's base match; UL204) | Argus: The retaining wall is a bare concrete slab that clashes with the stone facade; giving it a stone look matches the building. (fixes a:F202) |
| 30717 | 2 | set_camera | ext_7 | role: ext_7 is the site view the camera policy allows and keeps its role (docs/milestone13.md D8 and the site view rule): an aerial view stands at least 1 m above the ridge (z 7.01 m or more; the ridge is at 6.01 m) and looks down at least 5 degrees; this pose stands at z 0.00 m, below that line (the camera validator and code X6 judge it as an eye-level view) and looks 0.0 degrees down, less than the 5 degrees (the next build would make it an eye-level view); its height above eye level and its downward pitch are by design, not a finding; add_camera with a new view id for an eye-level view | Argus: win_L-1_002 is not seen in ext_7; re-aiming the exterior view to include it fixes the coverage. (fixes a:F203) |
| 30718 | 2 | add_camera | ext_9 | the target is the position, the camera stands inside the building (level L-1), the camera stands under the roof, eye height 3.34 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 0) is at z -3.34 m: use z -1.84 to -1.64 for an eye-level view | Argus: There is no frontal view of the entrance facade; adding one covers it. (fixes a:F205) |
| 30719 | 2 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show d_L-1_001, f_L-1_094 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The hall view currently shows a closed door and bare wall; pointing it at the open door to the salon and the hall's shoe_cabinet shows a room worth showing. (fixes a:F213) |
| 30722 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 is already a living | Argus: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 is identical in size and content to its twin (typed living) but is typed 'other'; its fixtures make it a living room. (fixes a:F216) |
| 30723 | 2 | place_group | r_L1_banyo_2 | no_change: r_L1_banyo_2 already has its bathroom_set r_L1_banyo_2.bathroom_set (anchor f_L1_022, members f_L1_016, f_L1_026): nothing missing, never a second set | Argus: r_L1_banyo_2 is missing the tall_cabinet its twin and the L-1/L-1b/L0 bathrooms all have; the bathroom set must be completed with it. (fixes a:F217) |
| 30724 | 2 | place_group | r_L0_e_banyo_2 | no_change: r_L0_e_banyo_2 already has its bathroom_set r_L0_e_banyo_2.bathroom_set (anchor f_L0_014, members f_L0_004, f_L0_016): nothing missing, never a second set | Argus: r_L0_e_banyo_2 is missing the tall_cabinet its twin r_L0_e_banyo has; the bathroom set must be completed with it. (fixes a:F221) |
| 30725 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi is already a living | Argus: The 40.5 m2 room is furnished as a living room (sofa, tv_unit, table_dining, table_coffee, armchair, bookshelf) but typed 'other'; its fixtures make it a living room. (fixes a:F222) |
| 30726 | 2 | retype_piece | f_L1_001 | retype: bathtub is no candidate for f_L1_001 (2.71 x 2.10 m at [9.11, 8.64]): the size table and the room / zone give stair | Argus: The documents draw a bathtub for this level; the shower is the wrong fixture for the set. (fixes a:F245) |
| 30727 | 2 | retype_piece | f_L1_002 | retype: bathtub is no candidate for f_L1_002 (2.71 x 2.10 m at [6.06, 8.64]): the size table and the room / zone give stair | Argus: Twin of F245 on the second unit; the shower is the wrong fixture for the drawn tub set. (fixes a:F246) |
| 30728 | 2 | retype_piece | f_L1_010 | retype: console_table is no candidate for f_L1_010 (0.42 x 0.45 m at [11.97, 2.04]): the size table and the room / zone give chair, display_cabinet, floor_lamp, ottoman, potted_plant, side_table | Argus: A shoe cabinet on a top-floor landing is the wrong type for the space. (fixes a:F247) |
| 30729 | 2 | retype_piece | f_L1_011 | retype: console_table is no candidate for f_L1_011 (0.43 x 0.45 m at [12.67, 2.68]): the size table and the room / zone give chair, display_cabinet, floor_lamp, ottoman, potted_plant, side_table | Argus: Twin of F247 on the second unit; shoe cabinet is wrong for a top-floor landing. (fixes a:F248) |
| 30732 | 2 | swap_model | f_L-1_073 | no_change: f_L-1_073 already uses the model abo_B07GDSF3MR | Argus: The table_coffee was built with a parametric mesh below the library level. swap_model to a library model (abo_B07GDSF3MR, 0.80 x 0.80 x 0.36 m) will fix it. move_piece was refused (overlap, max_tries). (fixes a:F269) |
| 30733 | 2 | swap_model | f_L-1_074 | acceptance: pin_refused: f_L-1_074: abo_B07GDSF3MR: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The table_coffee was built with a parametric mesh below the library level. swap_model to a library model (abo_B07GDSF3MR, 0.80 x 0.80 x 0.36 m) will fix it. move_piece was refused (overlap, max_tries). (fixes a:F270) |
| 30740 | 2 | rotate_piece | f_L-1b_042 | f_L-1b_042: no_overlap, f_L-1b_071: no_overlap, score: plausibility 28 -> -22 (F3 f_L-1b_042: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_042: sofa does not face its group (f_L-1b_071); F4 f_L-1b_051: armchair does not face its group (f_L-1b_071, f_L-1b_042, f_L-1b_046); F9 f_L-1b_071: table_coffee f_L-1b_071 overlaps sofa f_L-1b_042 by 0.25 m²) | Sofa is turned 90° against its product size and has no front; rotating to face 270° aligns its long side with the wall and gives it a proper front into the room. |
| 30742 | 2 | rotate_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: f_L-1b_041: no_overlap; f_L-1b_081: no_overlap; score: plausibility 18 -> -32 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_041: sofa does not face its group (f_L-1b_081); F4 f_L-1b_054: armchair does not face its group (f_L-1b_081, f_L-1b_041, f_L-1b_045); F4 f_L-1b_084: a | Rotate sofa 90° so its front faces 270° toward the coffee table and open floor, fixing F218/F89/F262 orientation findings |
| 30746 | 2 | retype_piece | f_L1_010 | room_type: side_table is not a piece a living room may hold here | Dining chair 0.42x0.45 m misread as shoe cabinet on a landing; side_table fits its size and the living room, fixing the wrong_type finding. |
| 30748 | 2 | retype_piece | f_L1_011 | room_type: side_table is not a piece a living room may hold here | Twin of the above: 0.43x0.45 m piece misread as shoe cabinet; side_table fits its size and the living room, fixing the wrong_type finding. |
| 30751 | 2 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F4 f_L-1_102: tv_unit stands behind the back of f_L-1_069, f_L-1_072, looking at it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair to face away from the sofa back, resolving the F4 orientation conflict where it stands behind f_L-1_054. |
| 30754 | 2 | swap_model | f_L0_037 | no_change: f_L0_037 already uses the model abo_B00IFHPVEU | Replace the corporate black mesh office chair with a residential bedroom-appropriate chair to resolve the D3 style clash. |
| 30756 | 2 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Snap wardrobe back to the wall and shift it away from the desk to restore the 0.80 m front clearance (G13). |
| 30758 | 2 | rotate_piece | f_L-1b_052 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071, f_L-1b_046)); 1 more kept | Armchair is 90° off the coffee table and does not face its group; rotating to face 180° (toward the sofa/coffee table) fixes orientation and front. |
| 30759 | 2 | rotate_piece | f_L-1_102 | score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of it) | Rotate TV unit to face the seating area, resolving the F4 orientation conflict where it stands behind the back of armchair f_L-1_069. |
| 30761 | 2 | move_piece | f_L-1b_051 | acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052) | Armchair's front zone is blocked by f_L-1b_052 and it is 33° off the sofa; shifting it 0.24 m east clears the other armchair and aligns it with the sofa. |
| 30762 | 2 | rotate_piece | f_L-1b_054 | acceptance: finding G3:f_L-1b_054 is still there after the edit (armchair f_L-1b_054 is 100° off the table_coffee f_L-1b_081 (needs ≤ 30°) at 1.30 m (needs ≤ 2.50 m)) | Rotate armchair to face 180° toward the sofa, fixing G3/F4/F267 orientation findings |
| 30764 | 2 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve the room layout with candidate 1 to maximize clearance around the bed and wardrobe, ensuring the bed is the primary anchor. |
| 30766 | 2 | retype_piece | f_L1_011 | score: plausibility 48 -> 31 (F8 f_L1_009: table_dining stands alone in the room (no wall, no chair / bench / bar_stool within 1.0 m); G6 f_L1_009: dining table f_L1_009 has no chairs (needs 0)) | Twin of the above: 0.43x0.45 m piece misread as shoe cabinet; ottoman is a valid candidate for its size and the living room, fixing the wrong_type finding. |
| 30767 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 50 -> 20 (F4 f_L-1_070: armchair faces a wall 0.23 m in front of it; F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 136° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m); G11 f_L-1_070: armchair f_L-1_070: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Rotate armchair to face the seating group instead of the back of the sofa |
| 30768 | 2 | move_piece | f_L-1_074 | score: plausibility 40 -> 30 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move coffee table to eliminate the 0.12 m² overlap with armchair f_L-1_069. |
| 30769 | 2 | move_piece | f_L-1b_051 | acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052) | Armchair's front zone is blocked by f_L-1b_052 and it is 33° off the sofa; shifting it 0.3 m east clears the other armchair and aligns it with the sofa. |
| 30772 | 2 | rotate_piece | f_L-1_070 | score: plausibility 50 -> 30 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.60 m (needs ≤ 2.50 m); G11 f_L-1_070: armchair f_L-1_070: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Rotate armchair to face the seating group (toward the sofa) instead of the back of the sofa |
| 30773 | 2 | rotate_piece | f_L1_029 | f_L1_029: clearance_ok, score: plausibility 48 -> 8 (F4 f_L1_029: armchair faces a wall 0.23 m in front of it; F6 f_L1_029: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_029: armchair f_L1_029 is 160° off the sofa f_L1_018 (needs ≤ 30°) at 2.29 m (needs ≤ 2.50 m); G11 f_L1_029: armchair f_L1_029: its front use zone is not reached by a 0.60 m walkway from door d_L1_002) | Turn the armchair to face the coffee table f_L1_024 instead of standing behind the back of f_L1_063, fixing the orientation finding. |
| 30774 | 2 | relayout_room | r_L-1_salon_2 | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_069, looking at it | Use solver candidate 1 to re-solve the seating group layout, ensuring a 0.60 m walkway from the door reaches the front use zones of the sofa and armchairs. |
| 30775 | 2 | rotate_piece | f_L1_032 | f_L1_032: clearance_ok, score: plausibility 48 -> 28 (F4 f_L1_032: armchair faces a wall 0.23 m in front of it; F6 f_L1_032: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_032: armchair f_L1_032 is 142° off the sofa f_L1_018 (needs ≤ 30°) at 2.75 m (needs ≤ 2.50 m)) | Turn the armchair to face the coffee table f_L1_024 instead of standing behind the back of f_L1_063, fixing the orientation finding. |
| 30776 | 2 | rotate_piece | f_L1_059 | acceptance: finding F4:f_L1_059 is still there after the edit (armchair does not face its group (f_L1_018, f_L1_024)) | Turn the reading corner armchair to face into the room (away from the back of sofa f_L1_018), fixing the orientation finding. |
| 30777 | 2 | move_piece | f_L-1b_052 | acceptance: finding F6:f_L-1b_052 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_051) | Armchair f_L-1b_052 blocks the front zone of f_L-1b_051; shifting it 0.3 m west clears the other armchair's front zone. |
| 30778 | 2 | rotate_piece | f_L-1_070 | score: plausibility 50 -> 40 (G3 f_L-1_070: armchair f_L-1_070 is 1° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair diagonally toward the seating group and coffee table |
| 30779 | 2 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 68 -> 48 (F4 f_L-1b_084: armchair faces a wall 0.02 m in front of it; F6 f_L-1b_084: armchair: the free zone in front of it is reaches out of the room; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Rotate reading corner armchair to face 90° away from the sofa back, fixing F4 finding |
| 30780 | 2 | move_piece | f_L-1_102 | score: plausibility 40 -> 30 (G1 f_L-1_102: TV unit f_L-1_102 1.22 m off the sofa axis, needs ≤ 0.30 m) | Move TV unit to the right wall (w_L-1_015) so its back is on the wall and it faces the seating area, resolving the F4 orientation conflict. |
| 30781 | 2 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Re-solve the drawn kitchen run so the planned stove and sink members are actually built in the scene (a:F91, a:F93). |
| 30782 | 2 | swap_model | f_L-1_090 | built_in: f_L-1_090: the fridge stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Replace the crude featureless white-box fridge with a detailed generated fridge model (a:F378). |
| 30784 | 2 | move_piece | f_L-1_074 | score: plausibility 40 -> 30 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.05 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move coffee table further from armchair f_L-1_069 to eliminate the 0.12 m² overlap. |
| 30785 | 2 | rotate_piece | f_L-1_070 | max_tries: f_L-1_070 was edited 3 times in this round | Rotate armchair to face the window wall and seating area |
| 30789 | 2 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 68 -> 58 (F6 f_L-1b_084: armchair: the free zone in front of it is blocked by f_L-1b_045; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Rotate reading corner armchair to face 0° into the room, away from the sofa back, fixing F4 finding |
| 30790 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has only 0.78 m clearance behind it, needing 0.81 m; moving it 0.13 m away from the piece behind provides the required clearance. |
| 30791 | 2 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move coffee table further from armchair f_L-1_069 to eliminate the overlap. |
| 30792 | 2 | move_piece | f_L-1_102 | score: plausibility 40 -> 30 (G1 f_L-1_102: TV unit f_L-1_102 0.52 m off the sofa axis, needs ≤ 0.30 m) | Move TV unit closer to the sofa axis on the right wall to satisfy the G1 axis constraint while keeping its back on the wall. |
| 30795 | 2 | move_piece | f_L1_038 | drawn_lock: f_L1_038: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.71 m) | Place the coffee table in front of sofa f_L1_019 (between sofa and TV side), fixing the G2 group layout finding. |
| 30796 | 2 | move_piece | f_L0_019 | score: plausibility 80 -> 50 (F3 f_L0_019: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Shift bed 0.07 m right to raise left-side clearance from 0.53 m to 0.60 m (G5). |
| 30798 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has only 0.78 m clearance behind it, needing 0.81 m; moving it 0.1 m away from the piece behind provides the required clearance. |
| 30799 | 2 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 68 -> 58 (F4 f_L-1b_084: armchair faces a wall 0.02 m in front of it; F6 f_L-1b_084: armchair: the free zone in front of it is reaches out of the room) | Rotate reading corner armchair to face 180° toward the left wall, away from the sofa back, fixing F4 finding |
| 30801 | 2 | move_piece | f_L1_064 | snap: f_L1_064: no free place on wall w_L1_001 (doors, windows) | Snap the sideboard (TV unit) back onto wall w_L1_001 so its back is on a wall, fixing the F3 clearance finding. |
| 30805 | 2 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a sideboard to resolve the NR untyped finding. |
| 30806 | 2 | swap_model | f_L0_033 | off_style: f_L0_033: abo_B07DBB7831 is of the styles ['classic', 'modern', 'scandinavian'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric nightstand mesh with a library model (0.505x0.459 m, modern) to clear the below-library P7 finding. |
| 30807 | 2 | swap_model | f_L0_034 | off_style: f_L0_034: abo_B07DBB7831 is of the styles ['classic', 'modern', 'scandinavian'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric nightstand mesh with a library model (0.505x0.459 m, modern) to clear the below-library P7 finding. |
| 30808 | 2 | move_piece | f_L-1b_045 | f_L-1b_045: no_overlap, f_L-1b_085: no_overlap | Move sofa 0.41m up to snap its back against the top wall, fixing F3 off-wall finding |
| 30809 | 2 | mark_not_furniture | f_L-1b_002 | no_crop: f_L-1b_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The untyped drawn piece is 5.14 m x 2.37 m, far too large for a single furniture item; it is a misread cluster outline around the dining group, not furniture. |
| 30811 | 2 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a minimal-style library model (0.49x0.41 m) to clear the below-library P7 finding. |
| 30813 | 2 | move_piece | f_L1_038 | acceptance: finding G2:f_L1_038 is still there after the edit (coffee table f_L1_038 is not in front of the sofa and is 0.08 m from the sofa front, needs ≥ 0.30 m) | Shift the coffee table 0.3 m towards the front of sofa f_L1_019 so it sits in front of the sofa, fixing the G2 group layout finding. |
| 30814 | 2 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Snap sofa back to left wall w_L-1b_010 to fix F3 off-wall finding |
| 30817 | 2 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: hssd_xxxx562932e4x443cx47f7xaf2dxe60cabe20c9e: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a minimal/modern library model (0.51x0.43 m, 0.59 m high) to clear the below-library P7 finding. |
| 30824 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Round-1 individual moves failed (wardrobe clearance, bed headboard F3); let the solver re-place the AI pieces to clear G13/G5/G4. |
| 30825 | 2 | move_piece | f_L-1b_045 | f_L-1b_045: doors_free, f_L-1b_045: no_overlap, f_L-1b_085: no_overlap, score: plausibility 68 -> 48 (F7 f_L-1b_045: sofa blocks door o_L-1b_002) | Move sofa 0.38m right and 0.41m up to snap back against top wall, avoiding overlap with side table, fixing F3 |
| 30826 | 2 | swap_model | f_L0_033 | max_tries: f_L0_033 was edited 3 times in this round | Replace the parametric nightstand mesh with a minimal/modern library model (0.49x0.43 m, 0.49 m high) to clear the below-library P7 finding. |
| 30827 | 2 | swap_model | f_L0_007 | acceptance: pin_refused: f_L0_007: 3dwh_6b69a6b7be7b83959f327b3e: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:D3:f_L0_007, c:M30:f_L0_007, c:M30:f_L0_007#2, c:M30:f_L0_007#3: swap the bed to a modern model with a designed headboard backdrop and correct modern bedding (duvet overhang, smooth duvet, throw across the foot). |
| 30829 | 2 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: abo_B07GFDZWMS: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the bare open-cubby placeholder with a styled 3-door shoe cabinet (dark grey, 75x25x128) that fits the 0.6 m wall span and reads as real furniture. |
| 30830 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Candidate 1 left G13/G5/G4 unchanged; try the solver's second layout for better clearances. |
| 30831 | 2 | move_piece | f_L-1b_085 | f_L-1b_084: no_overlap, f_L-1b_085: no_overlap, score: plausibility 68 -> 58 (F9 f_L-1b_085: side_table f_L-1b_085 overlaps armchair f_L-1b_084 by 0.15 m²) | Move side table to clear space for sofa f_L-1b_045 to reach the wall |
| 30832 | 2 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B07L1DX1LH: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a minimal/modern library model (0.49x0.43 m, 0.49 m high) to clear the below-library P7 finding. |
| 30833 | 2 | swap_model | f_L0_032 | off_style: f_L0_032: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | a:F555: swap the nightstand to a library-level model (Classic Nightstand 01, 0.57x0.42x0.70 m) instead of the parametric mesh. |
| 30836 | 2 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_015, d_L1_004 | Reposition the L1 bathroom camera to a free point showing the washbasin, toilet and tub so the room reads as designed instead of a cramped corner. |
| 30839 | 2 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show f_L-1_094, d_L-1_001 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Reframe the hall view to show the entrance group (shoe cabinet) and the door so the room reads as a 12 m2 hall, not a corner crop. |
| 30841 | 2 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a minimal library model (0.49x0.41 m) to clear the below-library P7 finding. |
| 30847 | 2 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | c:R3:d_L-1_001: door swings into the washbasin on one hinge side; shift it up to 0.5 m to clear the swing |
| 30849 | 2 | swap_model | f_L0_007 | acceptance: pin_refused: f_L0_007: 3dwh_ff9b2965ef382aba8d577399: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:D3:f_L0_007, c:M30:f_L0_007, c:M30:f_L0_007#2, c:M30:f_L0_007#3: swap the bed to a modern model (Rivington King Bed, 2.30x2.18x1.02 m) with a designed headboard backdrop and correct modern bedding (duvet overhang, smooth duvet, throw across the foot). |
| 30850 | 2 | set_camera | r_L1_teras | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Reposition the terrace camera to frame the complete seating group (armchairs, side table) and the potted plants without cutting the foreground chair. |
| 30851 | 2 | set_camera | r_L-1_koridor_2 | show: none of the 8 best poses of r_L-1_koridor_2 that show f_L-1_094, d_L-1_003 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: furniture and fixtures fill 1% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Reframe the hall view to show the shoe cabinet and the second door so the room reads as a 12 m2 hall, not a corner crop. |
| 30852 | 2 | swap_model | f_L0_034 | max_tries: f_L0_034 was edited 3 times in this round | Replace the parametric nightstand mesh with a minimal/modern library model (0.51x0.43 m, 0.59 m high) to clear the below-library P7 finding. |
| 30853 | 2 | swap_model | f_L0_003 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | The current washbasin model floats 0.384 m above the floor (S1); swapping to a grounded sink model fixes the clearance error. |
| 30859 | 2 | swap_model | f_L0_032 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L0_032: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:F555: swap the nightstand to a library-level model (Side Table 01, 0.55x0.45x0.55 m, modern minimal) instead of the parametric mesh. |
| 30864 | 2 | swap_model | f_L0_003 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | The current washbasin model floats 0.384 m above the floor (S1); swapping to a grounded vanity model fixes the clearance error. |
| 30865 | 2 | swap_model | f_L0_007 | acceptance: pin_refused: f_L0_007: 3dwh_d659728f8e656e02d1516f4b: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:D3:f_L0_007, c:M30:f_L0_007, c:M30:f_L0_007#2, c:M30:f_L0_007#3: swap the bed to a modern model (Ikea MANDAL, 2.40x2.11x0.94 m) with a designed headboard backdrop and correct modern bedding (duvet overhang, smooth duvet, throw across the foot). |
| 30871 | 2 | set_camera | r_L1_teras | max_tries: r_L1_teras was edited 3 times in this round | Fix a:F13 (Q4, cam_r_L1_teras_1): reposition the terrace camera to frame the complete seating group (armchairs, side table) and the potted plants without cutting the foreground chair. |
| 30872 | 2 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_015 | Fix a:F21 (V1, cam_r_L1_banyo_1): reposition the L1 bathroom camera to a free point showing the washbasin and tub so the room reads as designed. |
| 30876 | 2 | swap_model | f_L0_003 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | The current washbasin model floats 0.384 m above the floor (S1); swapping to a grounded sink model fixes the clearance error. |
| 30889 | 2 | swap_model | f_L0_003 | max_tries: f_L0_003 was edited 3 times in this round | The current washbasin model floats 0.384 m above the floor (S1); swapping to a grounded vanity model fixes the clearance error. |
| 30893 | 2 | swap_model | f_L0_018 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | The current toilet model floats 0.200 m above the floor (S1); swapping to a grounded toilet model fixes the clearance error. |
| 30897 | 2 | swap_model | f_L0_018 | pin_refused: f_L0_018: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | The current toilet model floats 0.200 m above the floor (S1); swapping to a grounded toilet model fixes the clearance error. |
| 31460 | 3 | swap_model | f_L-1_102 | acceptance: pin_refused: f_L-1_102: abo_B07QB8DQ45: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tv_unit was built with a parametric mesh below the library level. swap_model to abo_B072ZNBRR6 was refused (fails fit rules). abo_B07QB8DQ45 (1.80 x 0.41 x 0.79 m) is a candidate that may fit. rotate_piece was refused (back not on wall) (fixes a:F271) |
| 31461 | 3 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: hssd_97162e912362bae3a0ca0d385f9dab8e43360108: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall_cabinet was built with a parametric mesh below the library level. swap_model to abo_B07LC9HXSF was refused (asset_unusable), and abo_B07GFFY4WT was refused (fails fit rules). hssd_97162e912362bae3a0ca0d385f9dab8e43360108 (0.55 x 0. (fixes a:F272) |
| 31462 | 3 | swap_model | f_L1_022 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The parametric toilet mesh was chosen but fails the fit rules under the sloped ceiling; the refused swap was a different gen model that also failed, so a real library model that fits is the correct fix. (fixes a:F289) |
| 31463 | 3 | swap_model | f_L0_015 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The parametric toilet floats 0.200 m above the floor; the refused swaps were gen models that failed fit rules or were audit-removed. A real library model that sits on the floor is the correct fix. (fixes a:F302) |
| 31464 | 3 | swap_model | f_L0_016 | asset_unusable: objaverse_3446229dce1f47528fa871cc7669136c is not used: audit removed | Argus: The parametric toilet sits 0.200 m above the floor; the gen_toilet_japandi models were refused (audit removed or fit rules), so a real library model with a proper base is needed. (fixes a:F323) |
| 31465 | 3 | swap_model | f_L0_017 | asset_unusable: objaverse_3446229dce1f47528fa871cc7669136c is not used: audit removed | Argus: The parametric toilet sits 0.200 m above the floor; the gen_toilet_japandi models were refused (fit rules or audit removed), so a real library model with a proper base is needed. (fixes a:F324) |
| 31466 | 3 | swap_model | f_L0_044 | acceptance: pin_refused: f_L0_044: abo_B07QS8TBXT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric nightstand was built below the library level; abo_B0861YKM8S and side_table_01 were refused by fit rules, and ClassicNightstand_01 is off-style. abo_B07QS8TBXT (0.40 x 0.40 x 0.45 m, modern minimal/minimal) matches the projec (fixes a:F325) |
| 31468 | 3 | swap_model | f_L-1_051 | asset_unusable: objaverse_3446229dce1f47528fa871cc7669136c is not used: audit removed | Argus: The parametric toilet sits 0.200 m above the floor; the gen_toilet_japandi models were refused (fit rules or audit removed), so a real library model with a proper base is needed. (fixes a:F335) |
| 31469 | 3 | swap_model | f_L-1_052 | asset_unusable: objaverse_3446229dce1f47528fa871cc7669136c is not used: audit removed | Argus: The parametric toilet sits 0.200 m above the floor; a real library model with a proper base is needed. (fixes a:F336) |
| 31470 | 3 | swap_model | f_L0_047 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L0_047: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current tall_cabinet is a heavy, dark, open shelving unit that clashes with the light, clean, minimalist bathroom style. The tried_and_refused list shows abo_B07RMJPJMX was refused (fails fit rules: caps, height). abo_B07GFFY4WT (0.52 x (fixes a:F343) |
| 31472 | 3 | place_group | r_L1_banyo | no_change: r_L1_banyo already has its bathroom_set r_L1_banyo.bathroom_set (anchor f_L1_021, members f_L1_015, f_L1_025): nothing missing, never a second set | Argus: The reference image clearly establishes a bathtub as a key element of the bathroom design, which is completely absent. The room r_L1_banyo currently has shower, tall_cabinet, toilet, washbasin but no bathtub. The set_camera attempt was refu (fixes a:F352) |
| 31473 | 3 | swap_model | f_L1_062 | exists: no piece 'f_L1_062' in a room of the building | Argus: The current TV unit model has a dated chevron pattern that clashes with the room's clean lines; a japandi/modern model fits. (fixes a:F356) |
| 31474 | 3 | swap_model | f_L-1_054 | asset_unusable: 3dwh_def9a8f7409863460c32b9d9 is not used: audit removed | Argus: The current model's parts stand 2.7 cm apart; the first candidate was audit-removed, so the next closed-join model is used. (fixes a:F357) |
| 31475 | 3 | swap_model | f_L-1_090 | built_in: f_L-1_090: the fridge stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: The refrigerator f_L-1_090 is a crude, featureless white box that looks like a placeholder. Swapping to hssd_821a2d741626ea190a2ed790a2ed794c681a51dbcda48fa (0.61 x 0.61 x 1.90 m, minimal/modern) gives a realistic fridge that fits the 0.60  (fixes a:F378) |
| 31476 | 3 | swap_model | f_L-1_028 | no_change: f_L-1_028 already uses the model hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 | Argus: The dining set is a dozen identical white molded chairs around a slab table; the reference style calls for a mix of a bench and upholstered or wood chairs. Swapping the chair f_L-1_028 to hssd_3e6ccc40ee0f11bc3dadecfc6a0b9ae516f872c3 (0.48  (fixes a:F382) |
| 31477 | 3 | swap_model | f_L-1_049 | no_change: f_L-1_049 already uses the model 3dwh_324a4061c7079774c20c56e9 | Argus: The grey armchair f_L-1_049 is a different style and material from the white sofa, creating a disjointed look. Swapping to 3dwh_324a4061c7079774c20c56e9 (0.97 x 0.84 x 0.93 m, minimal/modern/scandinavian) gives an armchair that matches the  (fixes a:F384) |
| 31481 | 3 | set_camera | ext_3 | eye height 2.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The previous attempt was refused because the eye was 2.16 m above ground at (0,-30) where the ground is at z -0.5; placing the eye at 1.6 m (about 2.1 m above the local ground) with a wider lens and a target on the facade keeps the view at  (fixes a:F404) |
| 31483 | 3 | set_material | walls | walls: wood_slat (wood) would clad every wall of every room; the walls keep a plain finish (paint), a feature finish goes on one accent wall of a room (its scheme's feature wall: slats, a fluted panel or a headboard panel behind the bed or the sofa) | Argus: The wall behind the dining area and the main living wall are flat and raw; setting the walls slot to a slatted wood look gives the feature wall the reference style calls for. (fixes a:F410) |
| 31484 | 3 | swap_model | f_L-1_027 | asset_unusable: 3dwh_b27bb152311c2c1b3f509195 is not used: audit removed | Argus: The current dining table (module:table_dining:table_long) clashes with the light oak and mid-tone pieces; the previously refused model (3dwh_371b2b828aef220519cc3b6a) failed the fit rules, so the neutral 3.35 x 1.26 m model is the next cand (fixes a:F411) |
| 31486 | 3 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show d_L0_001, d_L0_002 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 9% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The camera is directly in front of the door leaf, which blocks the view; removing it was refused (it is the only view of the room), so re-aiming it to show the shoe cabinet and doors from an offset pose fixes the framing. (fixes a:F414) |
| 31489 | 3 | swap_model | f_L-1_070 | acceptance: pin_refused: f_L-1_070: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The brown leather model clashes with the group; a minimal/modern model in the allowed list matches the set. Rotation was already refused, so the model is the fix. (fixes a:F418) |
| 31498 | 3 | rotate_piece | f_L-1_072 | memory: the same edit was rejected in round 2: f_L-1_072: clearance_ok; score: plausibility 30 -> 10 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F4 f_L-1_102: tv_unit stands behind the back of f_L-1_069, f_L-1_072, looking at it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armcha | Face the armchair away from the sofa back (toward the room) to resolve the F4 orientation conflict. |
| 31499 | 3 | rotate_piece | f_L-1_102 | memory: the same edit was rejected in round 2: score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of | Face the TV unit toward the seating area to resolve the F4 conflict of standing behind the back of f_L-1_069. |
| 31501 | 3 | rotate_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: f_L-1b_041: no_overlap; f_L-1b_081: no_overlap; score: plausibility 18 -> -32 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_041: sofa does not face its group (f_L-1b_081); F4 f_L-1b_054: armchair does not face its group (f_L-1b_081, f_L-1b_041, f_L-1b_045); F4 f_L-1b_084: a | Sofa turned 90° against product size and had no front; 270° sets its front into the open floor towards its partner. |
| 31502 | 3 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041, f_L-1b_081, f_L-1b_045)); 1 more kept | Armchair 90° off the coffee table and not facing its group; 180° orients it towards the seating group and table. |
| 31508 | 3 | move_piece | f_L0_012 | f_L0_012: clearance_ok, score: plausibility 70 -> 60 (F3 f_L0_012: wardrobe: its back is not on a wall (0.07 m off); G13 f_L0_012: wardrobe f_L0_012: 0.51 m free in front, needs ≥ 0.80 m) | Move wardrobe 0.14m away from the desk to increase front clearance from 0.66m to the required 0.80m. |
| 31509 | 3 | retype_piece | f_L1_011 | no_change: f_L1_011 is already a chair | Confirm the drawn dining chair's type (chair fits its 0.43x0.45 m footprint and the living room's dining group), addressing the wrong_type finding for the twin chair. |
| 31512 | 3 | move_piece | f_L0_012 | memory: the same edit was rejected in round 1: f_L0_012: inside_room (outline: wardrobe reaches 0.20 m² through the room outline, up to 0.136 m deep; 0.00 m² up to 0.000 m deep before); score: plausibility 70 -> 50 (F3 f_L0_012: wardrobe: its back is not on a wall (0.14 m off); F9 f_L0_012: wardrobe reaches 0.20 m² through the room outline, up t | Move wardrobe 0.14m away from the desk to increase front clearance from 0.66m to the required 0.80m. |
| 31513 | 3 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Re-solve the drawn kitchen run so the stove f_L-1_008 and sink f_L-1_067 are actually built in the scene (a:F91, a:F93). |
| 31514 | 3 | move_piece | f_L0_020 | memory: the same edit was rejected in round 1: f_L0_020: no_overlap; f_L0_045: no_overlap; score: plausibility 70 -> 67 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.47 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.05 m from the bed side (needs ≤ 0.30 m); G5 f_L0_020: bed_double f_L | Move bed 0.07m towards the window wall to increase side clearances from 0.53m/0.56m to the required 0.60m. |
| 31517 | 3 | complete_group | r_L-1_mutfak.kitchen_run | no_change: r_L-1_mutfak.kitchen_run: nothing missing (members: f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090) | Rebuild the missing members of the kitchen run (stove f_L-1_008, sink f_L-1_067) so they appear in the scene (a:F91, a:F93). |
| 31518 | 3 | swap_model | f_L0_021 | lower_quality: f_L0_021: abo_B07K7NXVXR is rated 3.0 against 4.0 of the current model abo_B0154VUESC: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Swap the bed to a warm scandinavian solid-wood double (Alkove Hayes, 140x190) so the bedroom reads residential instead of the flagged model, addressing F326/F141/F151. |
| 31521 | 3 | mark_not_furniture | f_L-1_021 | no_crop: f_L-1_021 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/cam_r_L-1_salon_1_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The untyped 5.54 m long, 0.60 m thin band is a dimension outline, not furniture. |
| 31522 | 3 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071, f_L-1b_046)) | Rotate armchair to face the sofa and coffee table (270°) instead of facing the other armchair |
| 31526 | 3 | swap_model | f_L-1_073 | room_rule: f_L-1_073: 3dwh_5d52596ee79cd202260f50b9 the drawn table_coffee is round and the model is not (its title names no round shape): a square table's corners and legs would stand in the chairs drawn round it (rule round_table) | Replace the parametric mesh with a real 0.55 m square coffee table model to clear the below-library findings. |
| 31527 | 3 | swap_model | f_L0_037 | asset_type: abo_B07K7K7GKC is a chair model, not a office_chair | Replace the corporate black mesh office chair with a warm scandinavian solid-wood chair (Alkove Hayes) to resolve the D3 style clash in the residential bedroom. |
| 31533 | 3 | swap_model | f_L-1_101 | acceptance: pin_refused: f_L-1_101: abo_B07VHNMRY8: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric tv_unit mesh with a real 1.76 x 0.40 m white/oak TV stand model. |
| 31535 | 3 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Vector geometry reads the drawn 1.52x0.60 m piece as a coat closet (hanging rail); confirming it as a wardrobe fits its footprint and the corridor storage group (c:RC:f_L1_027). |
| 31538 | 3 | retype_piece | f_L1_027 | acceptance: finding RC:f_L1_027 is still there after the edit (f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | Vector geometry reads the drawn 1.52x0.60 m piece as a coat closet (hanging rail); dresser is the storage-type candidate the size table allows for this footprint in a corridor (c:RC:f_L1_027). |
| 31539 | 3 | swap_model | f_L0_038 | asset_type: abo_B07K7K7GKC is a chair model, not a office_chair | Replace the black leather corporate office chair with a warm wild-oak wood chair that fits the calm bedroom palette and light wood desk (a:F415). |
| 31540 | 3 | swap_model | f_L0_037 | memory: the same edit was rejected in round 1: asset_unusable: chinese_armchair is not used: audit pending | Replace the corporate black mesh office chair with the warm residential Chinese armchair to resolve the D3 style clash in the bedroom. |
| 31544 | 3 | swap_model | f_L0_021 | off_style: f_L0_021: abo_B07BBWMPJM is of the styles ['scandinavian', 'rustic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Swap the bed to a warm scandinavian solid-pine double (Movian Corona, 140x200) so the bedroom reads residential, addressing F326/F141/F151. |
| 31545 | 3 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining | memory: the same edit was rejected in round 1: no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi_2.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | Add the missing chairs to the dining group to create a proper dining zone, fixing the missing_member and G6 findings. |
| 31546 | 3 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B07K7K7GTZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a real library model (Alkove Hayes solid wood nightstand, modern minimal) to resolve the below-library finding (a:F558). |
| 31549 | 3 | rotate_piece | f_L-1b_051 | f_L-1b_051: no_overlap, f_L-1b_052: no_overlap, score: plausibility 58 -> 48 (G11 f_L-1b_051: armchair f_L-1b_051: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Rotate armchair to face the sofa (135°) to fix G3 33° off and F6 clearance |
| 31550 | 3 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Toilet f_L1_022 was built below library level (parametric mesh) and floats 0.20 m above its floor; this generated toilet's 0.568 m height fits the 0.69 m drawn depth and should seat on the floor. |
| 31555 | 3 | move_piece | f_L-1b_051 | acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052) | Move armchair to clear the other armchair and create space for proper orientation |
| 31557 | 3 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_mediterranean_4_c5dc64de: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Washbasin f_L1_016 floats 0.384 m above its floor; this generated washbasin (0.556 m wide, 0.335 m deep) fits the 1.0 x 0.55 m drawn footprint and should seat on the floor. |
| 31558 | 3 | swap_model | f_L0_038 | acceptance: pin_refused: f_L0_038: abo_B07GPSQKV9: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the black leather corporate office chair with a white leather swivel chair that fits the calm, warm bedroom palette (a:F415). |
| 31559 | 3 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a real library model (modern minimal style) to clear the below-library P7 finding. |
| 31563 | 3 | move_piece | f_L-1b_051 | drawn_lock: f_L-1b_051: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.84 m) | Move armchair further to clear the front zone blocked by f_L-1b_052 |
| 31564 | 3 | swap_model | f_L0_007 | asset_unusable: 3dwh_8270603b7ecbfea2e8080be5 is not used: audit removed | a:D3:f_L0_007: swap the flat headboard for the Furniture Queen Platform Bed w Headboard Built-in Night Stands (japandi/modern) to give the bed a designed headboard backdrop and modern bedding. |
| 31565 | 3 | fix_fixture | f_L1_015 | fixture_place: f_L1_015: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_004) | Door d_L1_004 swings into the washbasin on one hinge side; nudge it off the swing arc (at most 0.5 m). |
| 31566 | 3 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B079VKDKC1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a real library model (Movian white/walnut bedside cabinet, modern minimal) to resolve the below-library finding (a:F558). |
| 31569 | 3 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric nightstand for a real library model (Movian 2-drawer bedside, modern minimal) to clear the below-library P7 finding. |
| 31570 | 3 | move_piece | f_L0_011 | f_L0_011: no_overlap, f_L0_028: clearance_ok, score: plausibility 67 -> 47 (F3 f_L0_011: wardrobe: its back is not on a wall (0.27 m off); F9 f_L0_028: desk f_L0_028 overlaps wardrobe f_L0_011 by 0.05 m²; G13 f_L0_011: wardrobe f_L0_011: 0.35 m free in front, needs ≥ 0.80 m) | Shift wardrobe 0.3 m away from the south wall to open the 0.8 m front clearance (G13). |
| 31571 | 3 | swap_model | f_L0_007 | asset_unusable: 3dwh_60e3a1e484f76ca874adba67 is not used: audit removed | a:D3:f_L0_007: swap the flat headboard for the Ludlow King Bed in White Eco Leather and Walnut (minimal/modern) to give the bed a designed headboard backdrop and modern bedding. |
| 31574 | 3 | move_piece | f_L-1b_051 | memory: the same edit was rejected in round 2: acceptance: finding F6:f_L-1b_051 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_052) | Move armchair 0.3m right to clear the front zone blocked by f_L-1b_052 |
| 31575 | 3 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the bare parametric grid for a styled walnut stacking shoe rack (0.70x0.27x0.40, japandi/minimal) that fits the 0.6x0.3 footprint and reads as designed furniture in the hall. |
| 31576 | 3 | swap_model | f_L0_038 | max_tries: f_L0_038 was edited 3 times in this round | Replace the black leather corporate office chair with a grey upholstered swivel chair that fits the calm, warm bedroom palette (a:F415). |
| 31577 | 3 | swap_model | f_L0_042 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L0_042: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand mesh with a real library model (Side Table 01, modern minimal) to resolve the below-library finding (a:F558). |
| 31579 | 3 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B07K7K7GTZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric nightstand for a real library model (Alkove Hayes 1-drawer nightstand, modern minimal) to clear the below-library P7 finding. |
| 31580 | 3 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift bed 0.3 m left to open the left-side clearance to 0.82 m (G5#2) while keeping the headboard on the north wall. |
| 31581 | 3 | move_piece | f_L-1b_051 | max_tries: f_L-1b_051 was edited 3 times in this round | Move armchair 0.3m forward to clear the front zone blocked by f_L-1b_052 |
| 31582 | 3 | swap_model | f_L0_007 | asset_unusable: 3dwh_ec2a72b55f612b7d14a9f2f0 is not used: audit removed | a:D3:f_L0_007: swap the flat headboard for the Ludlow King Bed in Pearl Gray Eco Leather and Gray Oak (minimal/modern) to give the bed a designed headboard backdrop and modern bedding. |
| 31589 | 3 | swap_model | f_L0_007 | max_tries: f_L0_007 was edited 3 times in this round | a:D3:f_L0_007: swap the flat headboard for the Professional bed (minimal/modern) to give the bed a designed headboard backdrop and modern bedding. |
| 31590 | 3 | fix_fixture | f_L-1_025 | fixture_place: f_L-1_025: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_002) | Door d_L-1_002 swings into the washbasin on one hinge side; shift it to the nearest valid spot to clear the swing. |
| 31591 | 3 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: 3dwh_4ffcbf16a46f1e8fe0ad06b9: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the bare parametric grid for a styled modern shoe cabinet (0.56x0.33x0.38) that fits the 0.6x0.3 footprint and reads as designed furniture in the hall. |
| 31595 | 3 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B079VNKB6Z: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric nightstand for a real library model (Movian 3-drawer bedside, modern minimal) to clear the below-library P7 finding. |
| 31596 | 3 | move_piece | f_L0_022 | memory: the same edit was rejected in round 1: score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.20 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift bed 0.2 m left to open the left-side clearance to 0.72 m (G5#2) while keeping the headboard on the north wall. |
| 31597 | 3 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swapping to a grounded modern washbasin model fixes the clearance error. |
| 31600 | 3 | swap_model | f_L0_018 | pin_refused: f_L0_018: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swapping to a grounded japandi toilet model fixes the clearance error. |
| 31601 | 3 | fix_fixture | f_L0_005 | fixture_place: f_L0_005: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_008) | Door d_L0_008 swings into the washbasin on one hinge side; nudge it out of the swing. |
| 31602 | 3 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.15 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift bed 0.15 m left to open the left-side clearance to 0.67 m (G5#2) while keeping the headboard on the north wall. |
| 31603 | 3 | swap_model | f_L-1_094 | asset_unusable: hssd_482351496548bc89258838f6630d0c73afe3a158 is not used: audit removed | Swap the bare parametric grid for a low cedar shoe rack (0.74x0.31x0.14, minimal/rustic) that fits the 0.6x0.3 footprint and reads as designed furniture in the hall. |
| 31608 | 3 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B07QD6TXWS: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric nightstand for a real library model (Rivet Claremont nightstand, modern minimal) to clear the below-library P7 finding. |
| 31610 | 3 | swap_model | f_L-1_094 | max_tries: f_L-1_094 was edited 3 times in this round | Swap the bare parametric grid for a styled extending shoe rack (0.62x0.30x0.45, minimal/modern) that fits the 0.6x0.3 footprint and reads as designed furniture in the hall. |
| 31611 | 3 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); trying a grounded minimal washbasin model. |
| 31612 | 3 | move_piece | f_L0_022 | max_tries: f_L0_022 was edited 3 times in this round | Shift bed 0.1 m left to open the left-side clearance to 0.62 m (G5#2) while keeping the headboard on the north wall. |
| 31613 | 3 | swap_model | f_L0_018 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); trying a grounded minimal toilet model. |
| 31620 | 3 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_japandi_3_fc4e0710: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); trying a grounded japandi washbasin model. |
| 31621 | 3 | swap_model | f_L0_018 | pin_refused: f_L0_018: gen_toilet_classic_3_293965c2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); trying a grounded classic toilet model. |
| 31626 | 3 | set_camera | r_L-1_koridor_2 | refused pose: cam_r_L-1_koridor_2_1 stands 4.50 m over its floor, over (or within 0.05 m of) its room's ceiling at 2.85 m there: it sees the back of the ceiling; cam_r_L-1_koridor_2_1: eye height 4.50 m (wanted 1.2-1.6 m); the nearest searched pose is the one the view has, no_change: cam_r_L-1_koridor_2_1 has this pose already (the accepted override (overrides.json seq 986)): position [4.341141, 8.664207, -1.75], target [4.841141, 9.530233, -1.75], lens 16.0 mm; nothing to change | Reposition the interior camera to a free point with headroom that frames the hall's main group (shoe cabinet, doors, opening) so the 12 m2 space reads as a whole rather than a tight corner crop. |
| 31627 | 3 | swap_model | f_L0_003 | max_tries: f_L0_003 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor (S1); trying a grounded mediterranean washbasin model. |
| 31628 | 3 | swap_model | f_L0_018 | max_tries: f_L0_018 was edited 3 times in this round | Current toilet model floats 0.200 m above the floor (S1); trying a grounded mediterranean toilet model. |
| 31630 | 3 | set_camera | r_L-1_koridor_2 | refused pose: cam_r_L-1_koridor_2_1 stands outside its room r_L-1_koridor_2; cam_r_L-1_koridor_2_1 stands 4.50 m over its floor, over (or within 0.05 m of) its room's ceiling at 2.85 m there: it sees the back of the ceiling; the nearest searched pose is the one the view has, no_change: cam_r_L-1_koridor_2_1 has this pose already (the accepted override (overrides.json seq 986)): position [4.341141, 8.664207, -1.75], target [4.841141, 9.530233, -1.75], lens 16.0 mm; nothing to change | Reposition the interior camera to a free point with headroom in the open area near the opening, framing the shoe cabinet and doors so the 12 m2 hall reads as a whole rather than a tight corner crop. |
| 31631 | 3 | set_camera | r_L-1_koridor_2 | refused pose: cam_r_L-1_koridor_2_1 stands 4.50 m over its floor, over (or within 0.05 m of) its room's ceiling at 2.85 m there: it sees the back of the ceiling; cam_r_L-1_koridor_2_1: eye height 4.50 m (wanted 1.2-1.6 m); the nearest searched pose is the one the view has, no_change: cam_r_L-1_koridor_2_1 has this pose already (the accepted override (overrides.json seq 986)): position [4.341141, 8.664207, -1.75], target [4.841141, 9.530233, -1.75], lens 16.0 mm; nothing to change | Reposition the interior camera to the room's only free point with headroom, looking toward the shoe cabinet and doors so the 12 m2 hall reads as a whole rather than a tight corner crop. |
| 31632 | 3 | set_camera | r_L-1_koridor_2 | memory: the same edit was rejected in round 3: refused pose: cam_r_L-1_koridor_2_1 stands 4.50 m over its floor, over (or within 0.05 m of) its room's ceiling at 2.85 m there: it sees the back of the ceiling; cam_r_L-1_koridor_2_1: eye height 4.50 m (wanted 1.2-1.6 m); the nearest searched pose is the one the view has; no_change: cam_r_L-1_korid | Reposition the interior camera to the room's only free point with headroom, looking toward the shoe cabinet and doors so the 12 m2 hall reads as a whole rather than a tight corner crop. |
| 31633 | 3 | set_camera | r_L-1_koridor_2 | refused pose: cam_r_L-1_koridor_2_1 stands outside its room r_L-1_koridor_2; cam_r_L-1_koridor_2_1 stands 4.50 m over its floor, over (or within 0.05 m of) its room's ceiling at 2.85 m there: it sees the back of the ceiling; the nearest searched pose is the one the view has, no_change: cam_r_L-1_koridor_2_1 has this pose already (the accepted override (overrides.json seq 986)): position [4.341141, 8.664207, -1.75], target [4.841141, 9.530233, -1.75], lens 16.0 mm; nothing to change | Reposition the interior camera to a free point with headroom in the open area near the opening, framing the shoe cabinet and doors so the 12 m2 hall reads as a whole rather than a tight corner crop. |
| 32505 | 4 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_025 | Argus: The camera frame is entirely black; re-aiming it to show the bathroom's fixtures at eye height fixes the failed render. (fixes a:F24) |
| 32506 | 4 | fix_fixture | f_L-1_008 | memory: the same edit was rejected in round 1: no_change: f_L-1_008: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The stove is 0.06 m off the wall it is drawn against; fix_fixture with no center snaps it to the nearest valid spot on that wall. (fixes a:F49) |
| 32507 | 4 | relayout_room | r_L-1_mutfak | no_place: r_L-1_mutfak relayout: no place passes the checks (dining: no place passes the checks) | Argus: The 0.55 m aisle in front of the 2.32 m counter is a layout problem of the whole kitchen run; re-solving the room re-places the run to meet the 0.90 m aisle. (fixes a:F50) |
| 32508 | 4 | fix_fixture | f_L-1_017 | memory: the same edit was rejected in round 1: no_change: f_L-1_017: nothing to fix (size within the real range, inside the room and off the doors) | Argus: Same off-wall stove as F49, in the duplicate kitchen room; fix_fixture snaps it to the wall. (fixes a:F51) |
| 32509 | 4 | relayout_room | r_L-1_mutfak_2 | no_place: r_L-1_mutfak_2 relayout: no place passes the checks (dining: no place passes the checks) | Argus: Same narrow-aisle kitchen run as F50, in the duplicate room; re-solving the room fixes the run. (fixes a:F52) |
| 32510 | 4 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: no place passes the checks (no candidate position fits the room) | Argus: The bed is 0.53 m from the left wall (needs 0.60 m) and every move was refused (it would push the headboard off the wall or overlap the nightstand); the sleeping group must be re-solved. (fixes a:F60) |
| 32511 | 4 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Argus: Same bed-side clearance shortfall as F60, in the duplicate bedroom; the sleeping group re-solve fixes it. (fixes a:F62) |
| 32512 | 4 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The 1.40 x 0.60 m shower is outside the product range (real showers are at least 0.80 m deep); fix_fixture resizes it to a real 1.20 x 0.80 m shower. (fixes a:F64) |
| 32513 | 4 | swap_model | f_L0_021 | no_change: f_L0_021 already uses the model abo_B01M0ZVGCQ | Argus: The bed is 1.55 m wide in a room where only 0.37 m is free on the left. The current model abo_B0154VUESC is 1.55 x 1.90 m. The model abo_B01M0ZVGCQ (1.45 x 1.95 m) is 0.10 m narrower, which would bring the left clearance to about 0.47 m. Th (fixes a:F66) |
| 32514 | 4 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | Argus: The bed is 1.55 m wide in a room where only 0.37 m is free on the right. The current model abo_B0154VUESC is 1.55 x 1.90 m. The model abo_B01M0ZVGCQ (1.45 x 1.95 m) is 0.10 m narrower, which would bring the right clearance to about 0.47 m.  (fixes a:F68) |
| 32515 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | group checks: F4 f_L1_113: armchair stands behind the back of f_L1_017, looking at it | Argus: The armchair f_L1_052 is behind the back of f_L1_017 (a sofa or tv_unit). This is a group orientation error. Relayouting the room will re-solve the seating group's positions and orientations. (fixes a:F70) |
| 32516 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: group checks: F4 f_L1_071: armchair stands behind the back of f_L1_018, looking at it | Argus: The armchair f_L1_029 is behind the back of f_L1_063 (a tv_unit). This is a group orientation error. Relayouting the room will re-solve the seating group's positions and orientations. (fixes a:F76) |
| 32517 | 4 | relayout_room | r_L-1_salon | memory: the same edit was rejected in round 1: group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Argus: The armchair is behind the back of f_L-1_053 (a sofa_corner). This is a group orientation error. The previous relayout attempt was refused because it would have caused a new F4 finding on the tv_unit. However, the root cause is the same: th (fixes a:F80) |
| 32519 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: F4 f_L1_117: armchair stands behind the back of f_L1_018, looking at it | Argus: f_L1_018 blocks the sofa's front zone; re-solving the room's AI layout is the cause-level fix. (fixes a:F85) |
| 32520 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | group checks: F4 f_L1_113: armchair stands behind the back of f_L1_017, looking at it | Argus: The armchair faces the back of f_L1_017; re-solving the room's AI layout fixes the orientation. (fixes a:F91) |
| 32521 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: F4 f_L1_117: armchair stands behind the back of f_L1_018, looking at it | Argus: The tv_unit is 1.01 m off a wall; re-solving the room's AI layout (a different candidate than F85) fixes it. (fixes a:F92) |
| 32522 | 4 | swap_model | f_L-1_008 | built_in: f_L-1_008: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: f_L-1_008 (stove) is planned but the scene has no object for it; fix_fixture was refused (nothing to fix), so the stove needs a standalone model of its 0.75 x 0.55 m size. (fixes a:F108) |
| 32523 | 4 | swap_model | f_L-1_017 | built_in: f_L-1_017: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: f_L-1_017 (stove) is planned but the scene has no object for it; fix_fixture was refused (nothing to fix), so the stove needs a standalone model of its 0.75 x 0.55 m size. (fixes a:F109) |
| 32524 | 4 | swap_model | f_L-1_067 | acceptance: pin_refused: f_L-1_067: 3dwh_f7b6a98720563577a93662a2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: f_L-1_067 (sink_kitchen) is planned but the scene has no object for it; the sink needs a standalone model of its 0.79 x 0.50 m size. (fixes a:F110) |
| 32525 | 4 | swap_model | f_L-1_068 | acceptance: pin_refused: f_L-1_068: 3dwh_f7b6a98720563577a93662a2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: f_L-1_068 (sink_kitchen) is planned but the scene has no object for it; the sink needs a standalone model of its 0.79 x 0.50 m size. (fixes a:F111) |
| 32530 | 4 | relayout_room | r_L0_yatak_odasi_3 | memory: the same edit was rejected in round 1: acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Argus: The room is typed bedroom but has no bed; it has desk, office_chair, wardrobe. The relayout was refused because candidate 1 still had wardrobe clearance issues. Trying candidate 2 may place the bed and resolve the wardrobe clearance. (fixes a:F168) |
| 32531 | 4 | set_camera | r_L0_koridor | memory: the same edit was rejected in round 1: show: none of the 8 best poses of r_L0_koridor that show f_L0_039 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 9% of its frame (at least 12%; the | Argus: The shoe_cabinet f_L0_039 is built in r_L0_koridor; the camera does not show it. Re-aiming the camera to show the shoe cabinet fixes the render. (fixes a:F171) |
| 32532 | 4 | correct_geometry | o_L1_001 | memory: the same edit was rejected in round 1: the opening already lies on the wall (0.000 m) | Argus: The opening o_L1_001 is on wall w_L1_003 but not cut through it. correct_geometry with fix_opening_on_wall should cut the opening through the wall. (fixes a:F172) |
| 32533 | 4 | swap_model | f_L-1_056 | acceptance: pin_refused: f_L-1_056: hssd_c878d6d2cca3590cb1e1b7e33642a8f505a7feef: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current shower model (module:shower:bath_set) renders as a bare bathtub with no taps or towel rail. Swapping to a library model that includes these elements will fix the render. (fixes a:F202) |
| 32534 | 4 | set_camera | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 2: show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_ | Argus: The camera does not show door d_L0_002. Setting the camera to show the door will fix this. (fixes a:F205) |

Rolled back (the refit refused them): #935 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #937 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0), #970 move_piece (locked check: f_L-1b_046: moved 0.300 m by the agent (> 0.3 m)), #971 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #978 rotate_piece (locked check: f_L-1b_054: drawn_front_deg None != the drawn front 0.0), #1002 move_piece (locked check: f_L-1b_046: moved 0.300 m by the agent (> 0.3 m)), #1004 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #1006 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0).

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F9 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| F9 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4, 6 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| G8 | minor | f_L-1b_055 | r_L-1b_salon_2 | - | soft_minimum | 1, 2, 3, 4, 6 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1b_056 | r_L-1b_salon | - | soft_minimum | 1, 2, 3, 4, 6 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| M13 | minor | f_L-1_099 | r_L-1_mutfak_2 | fit | kitchen_design | 1, 2, 3, 4, 6 | the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit composes them of real units on the base joints (modules.plan_wall_run); the build cuts them at the windows of the building as built. No agent tool builds a hood or splits a wall cabinet, so the finding is reported to the fit |
| M15 | minor | spk_001 | - | site | site_grading | 1, 2, 3, 4, 6 | the garden on the slope is graded by code (wenart/blender/grading.py: terraces at one level per side and planted, banks of at most 1:3 / 1:2, flights of solid treads with cheek walls and a landing, paths level across and stepped, walls in the house's base stone with a coping, the floors by use); no agent tool changes the terrain, so the finding is reported to the site stage |
| M17 | major | dec_L0_041 | - | decor | ceiling_light | 1, 2, 3, 4, 6 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | major | dec_L0_078 | - | decor | ceiling_light | 1, 2, 3, 4, 6 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon | r_L-1_salon | decor | ceiling_light | 1, 2, 3, 4, 6 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon_2 | r_L-1_salon_2 | decor | ceiling_light | 1, 2, 3, 4, 6 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M21 | minor | f_L1_019 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | f_L1_020 | r_L1_oyun_aktivite_ve_dinlenme_odasi | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | f_L1_069 | r_L1_oyun_aktivite_ve_dinlenme_odasi | layout | room_use | 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_banyo_2 | r_L0_e_banyo_2 | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi_2 | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo | r_L1_banyo | layout | room_use | 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_oyun_aktivite_ve_dinlenme_odasi | r_L1_oyun_aktivite_ve_dinlenme_odasi | layout | room_use | 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| Q3 | minor | win_L1_001 | r_L1_teras | architect | guard | 4, 6 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q7 | major | d_L0_001 | - | openings | opening_style | 1, 2, 3, 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q9 | major | d_L0_005 | - | site | entrance_layout | 4, 6 | the landings, steps, ramps and handrails in front of the doors are laid out by code for all the entrances together (site.entrance_layout: doors whose steps would meet share one platform with one flight, a ramp and the handrails keep clear of the other doors); no agent tool moves them, so the finding is reported to the site stage |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4, 6 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4, 6 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4, 6 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L-1_089 | r_L-1_salon | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_007 | r_L0_e_yatak_odasi | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_022 | r_L0_yatak_odasi_4 | decor | decor_rest | 1, 2, 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_020 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_061 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_067 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | facade | 2, 3, 4, 6 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | facade | 2, 3, 4, 6 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L-1_003 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | d_L-1_004 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_001 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_002 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_006 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_001 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_002 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_001 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_002 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_003 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_004 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L1_001 | - | - | scale | 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L1_002 | - | - | scale | 2, 3, 4, 6 | storey and door sizes come from the drawings |
| lighting_dark | major | cam_r_L0_e_banyo_2 | r_L0_e_banyo | - | lighting_beyond_cap | 1, 2, 3 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1_salon_2 | cut | 1 | 9643 | 32768 |
| 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 6 | 42976 | 32768 |
| 1 | r_L-1_salon | cut | 1 | 8111 | 32768 |
| 1 | r_L-1b_salon_2 | cut | 1 | 7586 | 32768 |
| 1 | r_L-1b_salon | cut | 1 | 7423 | 32768 |
| 1 | building | cut | 1 | 17184 | 32768 |
| 2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 3 | 22107 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 6770 | 32768 |
| 2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cut | 1 | 4991 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 1 | 6749 | 32768 |
| 2 | building | cut | 1 | 12000 | 32768 |
| 3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 1 | 11468 | 32768 |
| 3 | r_L-1_salon | cut | 4 | 14120 | 32768 |
| 3 | building | cut | 3 | 6826 | 32768 |
| 3 | r_L-1b_salon | cut | 1 | 6909 | 32768 |

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
| f_L-1_023 | piece | wardrobe | r_L-1_salon_2 | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | Qwen/Qwen3.8-27B-FP8 | Argus: The wardrobe pokes 0.020 m through the outline; a slightly shorter model (2.53 m) keeps it inside. (fixes a:F81) |
| f_L-1_024 | piece | wardrobe | r_L-1_salon | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | code (size_snap) | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_031 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge chair f_L-1_031 to resolve the 0.040 m cut with the dining table |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred | - | - | front: faces the coffee table f_L-1_087 |
| f_L-1_050 | piece | armchair | r_L-1_salon_2 | inferred | - | - | front: faces the coffee table f_L-1_088 |
| f_L-1_053 | piece | sofa_corner | r_L-1_salon | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_054 | piece | sofa_corner | r_L-1_salon_2 | inferred | - | - | an L outline with 0.5-1.3 m deep arms in a living room (a corner sofa; the open inner corner is its front) |
| f_L-1_055 | piece | shower | r_L-1_banyo_2 | inferred, adjusted_by_ai | type bathtub -> shower | code (infer.bath_or_shower) | f_L-1_055: a bath-sized footprint (1.83 x 0.80 m) the drawing does not name a bath, in a bathroom off the bedrooms' level (L-1; the main bathroom keeps its bath on L0): a walk-in shower (UL200) |
| f_L-1_056 | piece | shower | r_L-1_banyo | inferred, adjusted_by_ai | type bathtub -> shower | code (infer.bath_or_shower) | f_L-1_056: a bath-sized footprint (1.83 x 0.80 m) the drawing does not name a bath, in a bathroom off the bedrooms' level (L-1; the main bathroom keeps its bath on L0): a walk-in shower (UL200) |
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
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 (size_snap) | Resize armchair to match the drawn dimensions [0.642, 0.569]; size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_071 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 (size_snap) | Resize armchair to drawn dimensions to resolve K3 size mismatch a:F531; size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_072 | piece | armchair | r_L-1_salon_2 | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 (size_snap) | Resize armchair to match the drawn dimensions [0.642, 0.569] to resolve the K3 size mismatch finding.; size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_073 | piece | table_coffee | r_L-1_salon | inferred, adjusted_by_ai | - | code (architect F5) | architect F5: f_L-1_073 (table_coffee) cut f_L-1_071 (armchair) by 0.18 m; f_L-1_073 (table_coffee) moved 0.59 m clear of it (inside its room, clear of the other pieces and the doorways) |
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
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Center the wardrobe on the free wall span to open the 0.80 m front clearance. |
| f_L0_011 | piece | wardrobe | r_L0_yatak_odasi_4 | adjusted_by_ai | - | architect | wardrobe f_L0_011: 0.17 m free in front of its doors or drawers (f_L0_028 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred, adjusted_by_ai | - | code (back_gap) | shower f_L0_013: its back stood 0.10 m off its wall, parallel to it (a drawing gap): moved 0.08 m back onto the wall (plan crop recognition/reading/f_L0_013_ctx.png) |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred, adjusted_by_ai | - | code (bath_details.shower_entry) | f_L0_014: its front stood on a wall, its left side open: the way in turned to that side (0 deg; UL201) |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_001 (the answer to AI.move_piece:f_L0_019) |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_004 (the answer to AI.move_piece:f_L0_020) |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The 1.55 m bed leaves only 0.37 m on the left side (needs 0.60 m); moving it worsens the headboard clearance. A narrower bed (1.45 m) frees the side aisle without moving the headboard off the wall. (fixes a:F326) |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_021 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m); front: its back stands on the only side on a wall |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Fix c:S4:f_L0_023: bring the wardrobe height into the 1.50-2.45 m range (it was built at 2.99 m). |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shrink the wardrobe height from 2.99 m into the 1.50-2.45 m (+-15%) range to clear the S4 size finding. |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L0_025 in the twin room r_L0_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_035 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_036 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_037 stands in front; plan crop recognition/crops/sym_L0_011_ctx.png |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_038 stands in front; plan crop recognition/crops/sym_L0_012_ctx.png |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png) |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: Shift the right nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the required ≤0.30 m. |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_005 | piece | table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (anchor); moved 0.28 m |
| f_L1_006 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dining chairs are a mix of different models and styles that clash with the modern aesthetic; hssd_4652661588c3e25396b891901da281f41f7a140c (0.44 x 0.42 x 0.81 m, minimal/modern/scandinavian) is a style-matching candidate in the same siz (fixes a:F400) |
| f_L1_007 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.28 m |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_010 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | type chair -> ottoman | code (architect F5) | architect F5: f_L1_010 (ottoman) cut f_L1_009 (table_dining) by 0.26 m; f_L1_010 (ottoman) moved 0.28 m clear of it (inside its room, clear of the other pieces and the doorways) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift the sofa 0.3 m away from f_L1_018 to clear the blocked free zone in front of it, fixing the F6 clearance finding. |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred, adjusted_by_ai | - | code (build.shower_headroom) | f_L1_025: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200) |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred, adjusted_by_ai | - | code (build.shower_headroom) | f_L1_026: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200) |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: An upholstered indoor armchair (3dwh_826f2d90cfd567a923e3dc8c) is on the outdoor terrace. Swap to a minimal/modern outdoor-appropriate model. (fixes a:F172) (plan crop recognition/crops/sym_L1_008_ctx.png) |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The orange armchair is a second loud accent that does not belong with the rest of the neutral palette; abo_B07J2YB486 (0.68 x 0.77 x 0.86 m, minimal/modern) is a style-matching candidate in the same size class. (fixes a:F398) (plan crop recognition/crops/sym_L1_009_ctx.png) |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move the armchair 0.3 m closer to the coffee table f_L1_024 to satisfy the G3 distance requirement (≤ 2.50 m). (plan crop recognition/crops/sym_L1_010_ctx.png) |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Argus: An indoor console table/bench (abo_B075QDV39B) is on the outdoor terrace. retype_piece was refused (bench not a candidate). Swap to a japandi/modern outdoor-appropriate model. (fixes a:F174) (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: An indoor coffee table (3dwh_75ac3c7d6dc1da28c99a0ad6) is on the outdoor terrace. move_piece was refused multiple times (drawn_lock, score, acceptance). Swap to an industrial/modern outdoor-appropriate model. (fixes a:F175) |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current model (hssd_69803a92f62572f4bc4de8fc64fd84c6a6e63229) is a black mesh corporate chair that clashes with the warm bedroom; swapping to a minimal/modern 0.50 x 0.49 m chair fixes the palette. (fixes a:F416) (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current model (hssd_69803a92f62572f4bc4de8fc64fd84c6a6e63229) is a black leather corporate chair that clashes with the warm bedroom; the previously refused swap (chinese_armchair) was pending audit, so the minimal/modern 0.50 x 0.49 m c (fixes a:F415) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_039 | piece | shoe_cabinet | r_L0_koridor | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_039: the piece is not built |
| f_L0_040 | piece | shoe_cabinet | r_L0_koridor_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_040: the piece is not built |
| f_L-1_094 | piece | shoe_cabinet | r_L-1_koridor_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Try the 4-door Movian Idro (52x25x163, dark grey) as a styled, door-fronted shoe cabinet for the 0.6 m span. |
| f_L1_059 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current model (abo_B072JG3WK1) has a 2.4 cm gap between the back/arm and the seat; swapping to a modern/scandinavian armchair with integrated rests fixes it. Rotation was already refused, so the model itself is the cause. (fixes a:F406) |
| f_L1_064 | piece | sideboard | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | snap the sideboard back onto the wall to clear the clearance finding (F81) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
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
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_e_banyo_1 | ![](agent/r4_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_1 | ![](agent/r4_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_1_after.jpg) |
| 4 | cam_r_L1_teras_2 | ![](agent/r4_cam_r_L1_teras_2_before.jpg) | ![](agent/r4_cam_r_L1_teras_2_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- cam_r_L-1_banyo_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L-1_koridor_2_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L1_koridor_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- final/top_L-1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L-1_plan_6.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_6.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_6.jpg
