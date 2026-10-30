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
| JSON cross-check findings (Cycles render) | 24 |
| needs_review views | 13 |
| unverified pieces in view (sum over views) | 48 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.67 .. +2.50 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 23 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 8, m5 5, search 23 |
| camera score (min / mean / max) | 0.09 / 3.56 / 4.91 |
| rooms by number of views | 1 with 0, 4 with 1, 3 with 2, 7 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 6.5 min / 6.6 min / 90.4 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 35.7 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 15 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 853.4 MB |
| [real04.glb](3d/real04.glb) | 1701.1 MB |

36 cameras; textures scaled to at most 1024 px (362 scaled) for the download.

## AI decor

138 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 35 rooms; 341 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- camera cam_r_L-1_koridor_2_1: no free camera point in the room; no point clear of the walls and the tall proxies, camera at the room's inner point INSIDE a proxy
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 16 piece(s) moved beyond the tolerance, 69 locked-rule violation(s)
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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | agent | D3 A5 | 0 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_banyo_2 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | agent | D1 A2 | 1 | no | [preview](cam_r_L-1_banyo_2_final_preview.jpg) [plan](cam_r_L-1_banyo_2_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.50 | - | search 0.73 | D1 A3 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.67 | -3 | search 4.60 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.83 | -3 | search 3.78 | D5 A1 | 0 | yes | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.17 | -1 | search 4.23 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 3.66 | D8 A4 | 4 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 3.48 | D12 A5 | 3 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.00 | -3 | search 3.64 | D10 A5 | 4 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.33 | - | search 1.93 | D1 A1 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.33 | - | agent | D2 A1 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.17 | - | agent | D2 A4 | 0 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +2.50 | - | search 0.09 | D2 A2 | 1 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -1.33 | - | search 4.61 | D6 A10 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -1.00 | -1 | search 4.43 | D3 A8 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.83 | - | search 3.90 | D4 A2 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.17 | - | agent | D5 A4 | 1 | yes | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.67 | -1 | agent | D4 A7 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.83 | - | search 3.91 | D5 A7 | 3 | yes | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.67 | - | search 3.89 | D5 A5 | 3 | yes | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.67 | -3 | search 4.90 | D3 A6 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 4.71 | D6 A1 | 4 | yes | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +2.17 | -4 | search 4.81 | D4 A5 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | -0.17 | - | agent | D2 | 1 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.33 | -3 | agent | D4 A1 | 0 | yes | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 4.15 | D8 A5 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | -0.17 | -2 | search 3.69 | D9 A2 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | search 3.64 | D5 A4 | 2 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.50 | 0 | search 3.41 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.33 | 0 | search 3.10 | D1 A4 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.67 | 0 | search 2.65 | D2 A4 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.00 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 blocked | D4 | 1 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -5.17 | 0 | m5 | D10 | 1 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_7 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 | D6 | 1 | yes | [preview](ext_7_final_preview.jpg) [plan](ext_7_plan.jpg) |

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
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 71 % of its pixels > 0.10 m outside the drawing, 345190 px |
| cam_r_L0_koridor_1 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 10 % of its pixels > 0.10 m outside the drawing, 15715 px |
| cam_r_L0_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 62 % of its pixels > 0.10 m outside the drawing, 65278 px |
| cam_r_L0_yatak_odasi_3 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 64 % of its pixels > 0.10 m outside the drawing, 95141 px |
| cam_r_L0_yatak_odasi_3_2 | cycles | cross-check misplaced | d_L0_006 | door | - | from_documents | deneme1.dwg INSERT:2DDE5/1,INSERT:2DDE5/0,LWPOLYLINE:2DE07 vector 0.95 | yes | 67 % of its pixels > 0.10 m outside the drawing, 175544 px |
| cam_r_L1_koridor_1 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 44 % of its pixels > 0.10 m outside the drawing, 112396 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 60 % of its pixels > 0.10 m outside the drawing, 13825 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 57 % of its pixels > 0.10 m outside the drawing, 21221 px |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 24 % of its pixels > 0.10 m outside the drawing, 43606 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 16 % of its pixels > 0.10 m outside the drawing, 5636 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 23 % of its pixels > 0.10 m outside the drawing, 46285 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 15 % of its pixels > 0.10 m outside the drawing, 5723 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 33 % of its pixels > 0.10 m outside the drawing, 42275 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 27 % of its pixels > 0.10 m outside the drawing, 10292 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 72 % of its pixels > 0.10 m outside the drawing, 12346 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 65 % of its pixels > 0.10 m outside the drawing, 10069 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3079 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 2654 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 7116 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1556 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3294 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 48 % of its pixels > 0.10 m outside the drawing, 14379 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12221 px |

## Needs review

- cam_r_L-1_mutfak_2: json cross-check misplaced: d_L-1_003
- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: d_L0_001
- cam_r_L0_koridor_1: json cross-check misplaced: d_L0_001
- cam_r_L0_yatak_odasi_2: json cross-check misplaced: d_L0_005
- cam_r_L0_yatak_odasi_3: json cross-check misplaced: d_L0_005
- cam_r_L0_yatak_odasi_3_2: json cross-check misplaced: d_L0_006
- cam_r_L1_koridor_1: json cross-check misplaced: d_L1_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: json cross-check misplaced: d_L1_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: json cross-check misplaced: d_L1_001
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
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_071, f_L-1_087
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_071, f_L-1_073
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061, f_L-1_070, f_L-1_087
- cam_r_L0_banyo_1: f_L0_025
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_banyo_2: f_L0_013
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_e_yatak_odasi_3: f_L0_023
- cam_r_L0_koridor_1: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3_1: f_L0_021, f_L0_029, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L1_banyo_1: f_L1_025
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_023
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_023
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_023, f_L1_030
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

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 148 ok, 16 failed; 51 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_063 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_065 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L0_007 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_009 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_010 | wardrobe (wardrobe) | 0.70 | 0.00 | yes | - |
| f_L0_011 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_034 | nightstand (floor_lamp) | 0.12 | 0.00 | yes | - |
| f_L1_005 | table_dining (table_dining) | 0.32 | - | - | - |
| f_L1_006 | chair (chair) | 0.13 | 90.00 | - | - |
| f_L1_007 | chair (chair) | 0.23 | 0.00 | - | - |

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
| facade | stone_cladding | - | agent | no | agent override (docs/milestone11.md §17.3) |
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
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L1_banyo_1, cam_r_L1_koridor_1 | 0 / 19 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

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
| area_light | 1 | r_L0_e_yatak_odasi: agent: View cam_r_L0_e_yatak_odasi_3 is 1.35 stops over the EV cap; the finding names factor x3 for the room.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_e_yatak_odasi |
| area_light | 1 | r_L0_koridor: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_koridor_2 |
| area_light | 1 | r_L0_merdiven: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven |
| area_light | 1 | r_L0_merdiven_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_merdiven_2 |
| area_light | 1 | r_L0_yatak_odasi: agent: Raise room light power to meet the +3.0 EV cap for cam_r_L0_yatak_odasi_1 (finding names x1.71).; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi |
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
| bay_lights | 1 | an LED strip at the top of every bay lights the contents so they read through the see-through front (UL135; a wardrobe LED profile, 1000 lm per metre (UL135)) | furn_f_L0_023 |
| bedding | 1 | its cover is flat (relief 0 mm, 135 vertices/m2 on top: under 6 mm or 50; 80% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_020 |
| bedding | 1 | its cover is flat (relief 224 mm, 226 vertices/m2 on top: under 6 mm or 50; 9% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_007 |
| bedding | 1 | its cover is flat (relief 88 mm, 37 vertices/m2 on top: under 6 mm or 50; 100% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_022 |
| bedding | 1 | its pillows lie flat (bump 0.08 m < 0.22 m: no euro shams, no standing pillows; UL137): our shams and pillows stand against its headboard, its duvet kept; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_021 |
| bedding | 1 | its pillows lie flat (bump 0.19 m < 0.22 m: no euro shams, no standing pillows; UL137): our shams and pillows stand against its headboard, its duvet kept; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_019 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_008 |
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
| height | 2 | no height in the JSON; type height for sideboard | furn_f_L1_064, furn_f_L1_065 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 4 | no height in the JSON; type height for tv_unit | furn_f_L-1_101, furn_f_L-1_102, furn_f_L1_062 |
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
| level | 1 | parking spk_001: one level at +0.75 m (level marks lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred); no kerb along 32.1 m of its edges where another surface abuts it (its wall, coping or paving is the edge there; inferred) | platform_spk_001 |
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
| level | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 5 steps up out of it on edge 0 (0.70 m, onto spk_001, cut into spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0); its retaining wall stops at the building on edge 5 (1.73-1.99 m) (never through the house's wall, UL148) | platform_sp_002 |
| level | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | platform_sp_002_s1e4 |
| level | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 1 (0.84-1.20 m) (never through the house's wall, UL148) | platform_sp_002_s1e5 |
| level | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | platform_sp_002_s2e4 |
| level | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | platform_sp_002_s2e5 |
| level | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 5 steps up out of it on edge 0 (0.79 m, onto spk_001, cut into spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | platform_sp_003 |
| level | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); sp_004 edge 3: a planted bank of 1:2 up to the ground 2.5 m out (the ground 0.78 m over the level; a landscape architect grades the ground to the terrace where it can, no retaining wall; inferred); its retaining wall stops at the building on edge 2 (0.00-0.17 m) (never through the house's wall, UL148) | platform_sp_004 |
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
| light_well:win_L-1_002 | 1 | brief site_options.front_court: yes: an inferred sunken front court 3 m deep, 8.39 m wide, its floor at the basement floor, a 0.9 m parapet (decision D6; no court drawn) | site |
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
| path_grading | 1 | a stepped path: 18 % along is steeper than 1:12, so 7 risers of 0.137 m in 3 flight(s) (3/2/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_sp_004_0 |
| path_grading | 1 | a stepped path: 19 % along is steeper than 1:12, so 4 risers of 0.127 m in 1 flight(s) (4) with level landings, treads 0.35 m, level across, stone step edges; a handrail on the flights over 0.45 m (inferred) | path_access_sp_001_0 |
| path_grading | 1 | a stepped path: 25 % along is steeper than 1:12, so 7 risers of 0.139 m in 1 flight(s) (7) with level landings, treads 0.35 m, level across, stone step edges; a handrail on the flights over 0.45 m (inferred) | path_access_sp_004_1 |
| path_grading | 1 | a stepped path: 31 % along is steeper than 1:12, so 5 risers of 0.135 m in 2 flight(s) (3/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_011 |
| path_grading | 1 | a stepped path: 31 % along is steeper than 1:12, so 5 risers of 0.145 m in 2 flight(s) (3/2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_012 |
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
| platform:sp_002 | 1 | terrace sp_002: one level at -3.00 m (the floor of L-1 of b1 (-3.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -1.42 m)); ground -2.61..-0.50 m under it; edge: steps; pools pool_002 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.49 m (next to spk_001), edge 2 1.99 m (next to spk_001), edge 3 2.49 m (next to spk_001); stepped terraces on edges 4 (2 x 0.90 m up), 5 (2 x 0.90 m up) (retaining cap 1.2 m); a flight of 5 steps up out of it on edge 0 (0.70 m, onto spk_001, cut into spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0); its retaining wall stops at the building on edge 5 (1.73-1.99 m) (never through the house's wall, UL148) | site |
| platform:sp_002_s1e4 | 1 | terrace sp_002_s1e4: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.51..-0.30 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s1e5 | 1 | terrace sp_002_s1e5: step 1 of sp_002 at -2.10 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.51..-0.29 m under it; edge: retaining (inferred); its retaining wall stops at the building on edge 1 (0.84-1.20 m) (never through the house's wall, UL148) | site |
| platform:sp_002_s2e4 | 1 | terrace sp_002_s2e4: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.70 m over the level along its edge 4, more than the 1.2 m retaining cap); ground -0.31..-0.10 m under it; edge: retaining (inferred) | site |
| platform:sp_002_s2e5 | 1 | terrace sp_002_s2e5: step 2 of sp_002 at -1.20 m (stepped terrace: the ground lies 2.71 m over the level along its edge 5, more than the 1.2 m retaining cap); ground -0.30..-0.09 m under it; edge: retaining (inferred) | site |
| platform:sp_003 | 1 | terrace sp_003: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_004, win_arch_r_L0_yatak_odasi_4_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it +1.57 m)); ground +0.57..+2.36 m under it; edge: steps; pools pool_004 in the deck (inferred); retaining wall over the cap where no band fits: edge 1 1.46 m (next to spk_001), edge 2 1.85 m (next to spk_001), edge 3 2.25 m (next to spk_001), edge 4 2.30 m (next to spk_001), edge 5 2.36 m (next to spk_001); a flight of 5 steps up out of it on edge 0 (0.79 m, onto spk_001, cut into spk_001); edges 6, 7, 8, 9, 10, 11, 12 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 1 after 0, 2 after 0, 3 after 0, 4 after 0, 5 after 0) | site |
| platform:sp_004 | 1 | terrace sp_004: one level at +0.00 m (the floor of L-1 of b2 (+0.00 m): the windows win_L-1_003, win_arch_r_L0_yatak_odasi_3_1 open over it (a terrace takes the floor its doors and windows serve; the mean ground under it -0.20 m)); ground -1.94..+1.38 m under it; edge: steps; pools pool_003 in the deck (inferred); retaining wall over the cap where no band fits: edge 2 1.38 m (next to spk_001); stepped terraces on edges 6 (1 x 1.13 m down), 7 (2 x 1.13 m down), 8 (1 x 1.13 m down), 11 (1 x 1.13 m down) (retaining cap 1.2 m); edges 0, 1, 12, 13, 14, 15, 16 face the building (its walls retain there: no wall, band or steps); no further stepped band where it would enter the building or another platform (edge 2 after 0); sp_004 edge 3: a planted bank of 1:2 up to the ground 2.5 m out (the ground 0.78 m over the level; a landscape architect grades the ground to the terrace where it can, no retaining wall; inferred); its retaining wall stops at the building on edge 2 (0.00-0.17 m) (never through the house's wall, UL148) | site |
| platform:sp_004_s1e11 | 1 | terrace sp_004_s1e11: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.26 m under the level along its edge 11, more than the 1.2 m retaining cap); ground -1.26..-0.55 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e6 | 1 | terrace sp_004_s1e6: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 1.73 m under the level along its edge 6, more than the 1.2 m retaining cap); ground -1.73..-0.89 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e7 | 1 | terrace sp_004_s1e7: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.46..-1.43 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s1e8 | 1 | terrace sp_004_s1e8: step 1 of sp_004 at -1.13 m (stepped terrace: the ground lies 2.14 m under the level along its edge 8, more than the 1.2 m retaining cap); ground -2.14..-1.63 m under it; edge: retaining (inferred) | site |
| platform:sp_004_s2e7 | 1 | terrace sp_004_s2e7: step 2 of sp_004 at -2.26 m (stepped terrace: the ground lies 2.26 m under the level along its edge 7, more than the 1.2 m retaining cap); ground -2.97..-1.73 m under it; edge: retaining (inferred) | site |
| platform:spk_001 | 1 | parking spk_001: one level at +0.75 m (level marks lm_003, lm_006, lm_012, lm_016); ground -3.52..+2.84 m under it; edge: kerb (the marks spread over 1 m: the area is drawn sloped and stays draped) (inferred); no kerb along 32.1 m of its edges where another surface abuts it (its wall, coping or paving is the edge there; inferred) | site |
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
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_021 (no nightstand, no lamp): the wall sconce would cover the window win_arch_r_L0_yatak_odasi_3_1 | rig_r_L0_yatak_odasi_3 |
| rig_bedside | 1 | bedside lamp beside the head of the bed f_L0_022 (no nightstand, no lamp): the wall sconce would cover the window win_arch_r_L0_yatak_odasi_4_1 | rig_r_L0_yatak_odasi_4 |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_019 (the top of the nightstand f_L0_042 is taken by the books dec_L0_009): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi |
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the books dec_L0_059): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi_2 |
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
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/3 of its light under each decor ceiling light of the room (dec_L-1_040); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/3 of its light under each decor ceiling light of the room (dec_L-1_065); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak; 1/3 of its light under each decor ceiling light of the room (dec_L-1_066); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_6_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_097 over the counter f_L-1_010; 1627.9 lm -> 4.064 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_098 over the counter f_L-1_011; 355.4 lm -> 0.9331 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_2_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_099 over the counter f_L-1_011; 298.6 lm -> 0.7837 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_3_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/3 of its light under each decor ceiling light of the room (dec_L-1_074); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/3 of its light under each decor ceiling light of the room (dec_L-1_088); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_5_light |
| rig_light | 1 | r_L-1_mutfak_2: ceiling fixture at the pole of inaccessibility of r_L-1_mutfak_2; 1/3 of its light under each decor ceiling light of the room (dec_L-1_089); 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_6_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027 under the decor pendant dec_L-1_139; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038 under the decor pendant dec_L-1_156; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_034; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003, above the mirror dec_L0_033 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_038; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_037 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_023; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_022 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_025; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_024 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_031 is taken by the vase dec_L0_099); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_017); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_033 is taken by the vase dec_L0_106); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_046); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 2 | r_L0_koridor: ceiling fixture at the pole of inaccessibility of r_L0_koridor, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light, rig_r_L0_koridor_ceiling_2_light |
| rig_light | 2 | r_L0_koridor_2: ceiling fixture at the pole of inaccessibility of r_L0_koridor_2, 2 x 1100 lm bulbs for 450 lm/m2 over 7.6 m2 and 2 fixture(s); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light, rig_r_L0_koridor_2_ceiling_2_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_056 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_029 on f_L0_043 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_064 on f_L0_046 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_031); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_035); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_015; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_046; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
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
| suspension | 1 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L0_019_cord |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| terrace_railing | 1 | roof terrace ro_001: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_001 |
| terrace_railing | 1 | roof terrace ro_002: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_002 |
| tree | 28 | bush of the drawn size, 0.8 m tall (height assumed) | tree_sp_004_bank0_plant1, tree_sp_001_s1e2_plant1, tree_sp_001_s1e3_plant1 |
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
| wall_clear | 1 | covered by the wardrobe f_L0_009 in front of its wall, its top 1.96 m (build): a wall item stays clear of what stands in front of it (UL139); moved to another free wall of the room | dec_L0_032 |
| wall_clear | 1 | covered by the wardrobe f_L0_010 in front of its wall, its top 2.15 m (build): a wall item stays clear of what stands in front of it (UL139) | dec_L0_082 |
| wall_clear | 1 | covered by the wardrobe f_L0_011 in front of its wall, its top 1.81 m (build): a wall item stays clear of what stands in front of it (UL139); moved to another free wall of the room | dec_L0_067 |
| wall_clear | 1 | over the door d_L0_011 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_092 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_3_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_027 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_062 |
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
| wall_plate | 1 | inferred: a light switch on the wall next to the outside door d_L0_011 (entrance), as beside it the intercom dec_L0_092, 0.08 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_01 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_027 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_028 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_029 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_030 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_04 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_057, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_068, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_033, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_037, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_2_02 |
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
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 1.28 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_05, plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.51 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_06 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.72 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.25 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_04 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.30 m, 0.30 m over the floor | plate_r_L-1_salon_2_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.42 m, 0.30 m over the floor | plate_r_L-1_salon_05 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.57 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.87 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_02 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 2.98 m, 0.30 m over the floor | plate_r_L-1_salon_04, plate_r_L-1_salon_2_04 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 3.63 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_05, plate_r_L0_yatak_odasi_4_05 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.33 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_05, plate_r_L0_yatak_odasi_2_05 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 4.87 m, 0.30 m over the floor | plate_r_L-1_salon_03, plate_r_L-1_salon_2_03 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_022, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_02 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_024, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_101 beside it, 0.30 m over the floor | plate_r_L-1_salon_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_102 beside it, 0.30 m over the floor | plate_r_L-1_salon_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L1_062 beside it, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_02 |
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

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial], 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_4df9d791c4300f977420e8fd [non_commercial], 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_52f33bb92da2aee9f4cc12bb [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_73a3f2fd339beec5aabd5ed6 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8e456b89888577abcc0a5025 [non_commercial], 3dwh_9c3a1772a72c4b00c78bd2ea [non_commercial], 3dwh_a4e1395f626c963c2082d2a3 [non_commercial], 3dwh_a7197a08cbaa61fbfd714f4b [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], 3dwh_f5c7f12837d5da10f176ece9 [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_minimal_4_71886746 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], gen_potted_plant_modern_1_8fbfec3c [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_13dbb657414706f4c3ba192d2875ea2c7478b710 [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_3cc6a9d98da2e8813a1d4cf18a10c0dca380bb72 [non_commercial], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_652536faa9c5028ed8be69780c120af78c141968 [non_commercial], hssd_7731b27a33dba3816bd7bc321cf47bc12facc109 [non_commercial], hssd_b48e86b9315f28d3f5ad9d0d5e16e87b9075b4f6 [non_commercial], hssd_c32f5f957504b74bdc7aea67da189e7878d6ff32 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial], hssd_d7c839146e84643d034b5eff9b1142e5445af7af [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial], hssd_xxxxcf52c887xd6ccx47d0xbf5fx448bc77e113d [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial])
- cam_r_L-1_banyo_2: commercial-safe: no (flagged assets: hssd_652536faa9c5028ed8be69780c120af78c141968 [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: yes
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: gen_potted_plant_modern_1_8fbfec3c [tool_nc])
- cam_r_L-1_mutfak_3: commercial-safe: yes
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_9c3a1772a72c4b00c78bd2ea [non_commercial], 3dwh_a4e1395f626c963c2082d2a3 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_169eb04a11ba682bae4b1a3a [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_9c3a1772a72c4b00c78bd2ea [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_d46d68c38dd2d64388be98b66b665b7db512f1ab [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: yes
- cam_r_L0_e_banyo_2: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_4df9d791c4300f977420e8fd [non_commercial], 3dwh_f5c7f12837d5da10f176ece9 [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial], gen_plant_large_japandi_5_92708e0b [tool_nc])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_4df9d791c4300f977420e8fd [non_commercial], 3dwh_f5c7f12837d5da10f176ece9 [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_japandi_5_92708e0b [tool_nc])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_f5c7f12837d5da10f176ece9 [non_commercial])
- cam_r_L0_koridor_1: commercial-safe: no (flagged assets: 3dwh_f858f555e33dd365be821c2b [non_commercial])
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], 3dwh_d066a3e014bfc9238d3e4c4c [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_ce9604f33d3a30bc31bea94d [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: hssd_d7c839146e84643d034b5eff9b1142e5445af7af [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: 3dwh_21229a4e1db90fefa6b3188a [non_commercial], gen_plant_large_minimal_4_71886746 [tool_nc], hssd_b48e86b9315f28d3f5ad9d0d5e16e87b9075b4f6 [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_73a3f2fd339beec5aabd5ed6 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_8e456b89888577abcc0a5025 [non_commercial], 3dwh_a7197a08cbaa61fbfd714f4b [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_large_minimal_4_71886746 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_13dbb657414706f4c3ba192d2875ea2c7478b710 [non_commercial], hssd_c32f5f957504b74bdc7aea67da189e7878d6ff32 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_73a3f2fd339beec5aabd5ed6 [non_commercial], 3dwh_a7197a08cbaa61fbfd714f4b [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_large_minimal_4_71886746 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_13dbb657414706f4c3ba192d2875ea2c7478b710 [non_commercial], hssd_c32f5f957504b74bdc7aea67da189e7878d6ff32 [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_523bf9cafe725ff93a853009 [non_commercial], 3dwh_52f33bb92da2aee9f4cc12bb [non_commercial], 3dwh_73a3f2fd339beec5aabd5ed6 [non_commercial], 3dwh_b3a89eb091ee4ba0a1332150 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_large_minimal_4_71886746 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_3cc6a9d98da2e8813a1d4cf18a10c0dca380bb72 [non_commercial], hssd_7731b27a33dba3816bd7bc321cf47bc12facc109 [non_commercial], hssd_c32f5f957504b74bdc7aea67da189e7878d6ff32 [non_commercial], hssd_e9393fb84e42e59d93ba261275daf119df0cde2e [non_commercial], hssd_xxxxcf52c887xd6ccx47d0xbf5fx448bc77e113d [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: yes
- ext_5: commercial-safe: no (flagged assets: 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_b48e86b9315f28d3f5ad9d0d5e16e87b9075b4f6 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_3ec57e99c219f8ba9905119f [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])

## Built below library level (Milestone 13)

65 furniture piece(s) built from a module builder or a parametric family instead of a library model: 4 library gap(s) to close with a real model, 61 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L-1_102 | tv_unit | parametric | parametric:tv_unit | r_L-1_salon_2 | living | added_by_ai | no (by design) | - |
| f_L-1_103 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L-1_104 | tall_cabinet | parametric | parametric:tall_cabinet | r_L-1_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_047 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_e_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_048 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_049 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo_2 | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 3), cam_r_L1_teras_3 (15.0 degrees off the sun, sky pull k 3), ext_1 (6.0 degrees off the sun, sky pull k 3), ext_5 (5.6 degrees off the sun, sky pull k 0).

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

Assets: textures CC0 x 36; furniture/decor models 3DWH-UNREVIEWED x 48, CC-BY-4.0 x 122, CC-BY-NC-4.0 x 56, generated (Infinigen v1.19.0, BSD-3-Clause) x 3, generated (TRELLIS.2-4B, MIT) x 23 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 36 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_119)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_048)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_005)
- "Candle" by deniska40k (https://sketchfab.com/3d-models/c408586d8c1547448c4ff47abb4fb981), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_035)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261030-043021-full-20261030T043444Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 49.9 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 112.3 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.5 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.7 min | answers applied |
| fit | ok | 13.8 s | - |
| layout | ok | 57.4 s | - |
| decor_ask | ok | 2.4 min | - |
| photos | reused | 0.2 s | - |
| assets | ok | 49.4 s | - |
| decor | ok | 11.6 s | - |
| agent_apply | ok | 76.9 s | - |
| refit | ok | 114.0 s | - |
| build | ok | 51.8 min | - |
| agent_previews | ok | 8.4 min | 15 view(s) |
| agent | ok | 69.3 min | 4 round(s), 18 finding(s) removed by 85 accepted edit(s) (measured; 179 predicted by the dry re-checks), 15 new, net 3, 260 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 14.8 min | - |
| export | ok | 7.0 min | - |
| controls | ok | 2.1 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.3 min | - |
| check | ok | 3.6 min | - |
| combine | ok | 26.1 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 85 edit(s) accepted, 260 rejected, 699 model calls (8972410 tokens), 79.0 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 20300): earlier runs of the appended log are left out (20299 events, 6998 model calls, 632 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 85 / 260 (25 % accepted) |
| rejected by reason | acceptance 51, memory 27, no_change 23, pin_refused 20, score 20 |
| rooms checked by code / vision / planner | 38 / 14 / 29 |
| rooms with fixable critical or major findings visited | 29 of 29 |
| critical before -> after (after: round 4's critics, before its 12 accepted edit(s)) | 10 -> 21 |
| major before -> after (after: round 4's critics, before its 12 accepted edit(s)) | 296 -> 513 |
| agent minutes; first accepted edit after | 66.86; 5.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 27; 105; 97 (55) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 18 measured; 179 predicted (the last round's dry re-checks predicted 56 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 85 new; net -67 |
| edits removing their finding | 9 of 57 |
| plans ok / empty / refused / default | 55 / 38 / 4 / 0 |

### What the AI inspector saw on the final renders

500 vision finding(s) (51 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 64 fixed in the final round, 26 handed to the stage that owns them, 498 open; the architect leaves 0 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`.

Still open or handed on (critical and major):

- major Q3 building: The roof terrace on the upper level has a glass balustrade that is too low to provide a safe guard against falling. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- major X9 building: The retaining wall supporting the raised garden bed is a bare, untextured concrete slab, which looks unfinished and out of place with the st (open: a tool exists (set_terrain, set_ground_point, set_room_floor) but no edit was accept)
- critical Q3 r_L-1_salon: The large opening in the floor of the salon (living room) has no guard, railing, or glass pane, creating a direct fall hazard to the level b (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical Q3 r_L-1_salon_2: The large opening in the floor of the salon 2 (living room) has no guard, railing, or glass pane, creating a direct fall hazard to the level (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical Q3 r_L0_merdiven: The stairwell opening (merdiven) has no guardrail or safety barrier, creating a significant fall risk from the upper level. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical Q3 r_L0_merdiven_2: The second stairwell opening (merdiven 2) is completely open with no railing or glass pane, posing a fall hazard. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical Q3 r_L1_koridor_2: The stair opening in the second hall (koridor 2) has no guard or railing, creating a fall risk. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- major Q12 r_L1_banyo_2: The second bathroom is not fully designed: the washbasin has no mirror above it, and there is no towel rail visible. (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major Q12 f_L-1_026: a bathroom that is not designed: the washbasin is not in frame and there is no mirror over it; the only visible fixture is a tub rim, so the (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major D3 f_L-1_056: missing layer: warm light and styled surfaces; the reference sets a warm, layered light with a dark accent wall, but the render is flat beig (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major Q12 f_L-1_056: a bathroom that is not designed: The bathtub is shown in isolation with no visible taps, mixer, or surrounding design elements. It looks lik (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major V1 r_L-1_koridor_2: bad_camera: the view is a corner shot with a large blank wall filling the right half of the frame; the corridor's main group (the shoe cabin (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: seating. The reference hall anchors the space with a bench; this corridor has no place to sit or put on shoes, so the room ha (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: mirror. The reference uses a large backlit mirror to double the space and add light; the render has none, leaving the right w (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: warm light. The reference is lit by a statement chandelier and a mirror light; the render is flat and dim with no visible fix (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: styled surfaces / wall art. The reference has a feature wall, a clock and a console; here the only art is a painting cropped  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the reference shows a styled kitchen with a bowl of fruit, a cutting board, and small appliances; this rende (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the reference has a warm, inviting atmosphere with a pendant light; this render is lit with flat, cool daylight t (open: a tool exists (swap_model) but no edit was accepted)
- major Q13 f_L-1_091: The main counter run under the window has no wall cabinets or tall units above it, leaving a large, empty wall that makes the kitchen feel u (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major Q13 f_L-1_002: The worktop is completely bare. A well-designed kitchen needs styling (a kettle, a bowl of fruit, a cutting board) to feel lived-in and comp (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the reference shows a styled kitchen with a table setting, plants, and accessories; this render has a bare c (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the reference has a warm, inviting lighting scheme with a distinct pendant light; this render is lit with flat, c (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_salon: missing layer: feature wall — the wall behind the sofa and the TV wall are flat, untextured concrete with no panelling, wainscot or accent,  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_salon: missing layer: wall art — every wall is bare; the reference carries framed prints that this render lacks entirely. (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_salon: missing layer: layered curtains — the full-height glazing has no sheer or drape on a track, leaving the windows stark. (open: a tool exists (swap_model) but no edit was accepted)

### Argus, the auditor

Score 3.3 / 100 (100 = nothing open): 28 critical, 371 major, 139 minor open. By kind (critical + major): lost 50, detached 10, no_sense 53, misread 33, taste 102, geometry 58, process 34, other 26, silent 19, reference_missed 6, stale 6, untyped 2. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- detached dec_L1_029: ceiling_light dec_L1_029: its top 0.039 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- detached dec_L1_030: ceiling_light dec_L1_030: its top 0.039 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- detached dec_L1_031: ceiling_light dec_L1_031: its top 0.037 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- detached dec_L1_035: ceiling_light dec_L1_035: its top 0.037 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- detached dec_L1_050: ceiling_light dec_L1_050: its top 0.037 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- detached dec_L1_051: ceiling_light dec_L1_051: its top 0.037 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- no_sense r_L-1_salon: The large opening in the floor of the salon (living room) has no guard, railing, or glass pane, creating a direct fall hazard to the level below.
- no_sense r_L-1_salon_2: The large opening in the floor of the salon 2 (living room) has no guard, railing, or glass pane, creating a direct fall hazard to the level below.
- no_sense r_L0_merdiven: The stairwell opening (merdiven) has no guardrail or safety barrier, creating a significant fall risk from the upper level.
- no_sense r_L0_merdiven_2: The second stairwell opening (merdiven 2) is completely open with no railing or glass pane, posing a fall hazard.
- no_sense r_L1_koridor: The stair opening in the hall (koridor) has no guard or railing, creating a fall risk.
- no_sense r_L1_koridor_2: The stair opening in the second hall (koridor 2) has no guard or railing, creating a fall risk.
- misread f_L1_100: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- detached dec_L0_011: Argus: cushion dec_L0_011 on bed_double f_L0_007: penetration 0.049 m > 0.03 m
- detached dec_L0_012: Argus: cushion dec_L0_012 on bed_double f_L0_007: penetration 0.049 m > 0.03 m
- no_sense dec_L1_013: Argus: decor_dec_L1_013 pokes through the roof (top 5.32 m)
- taste cam_r_L1_banyo_1: Argus: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. This is a failed render, not 
- misread r_L1_teras: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- lost MTEXT:2C809:0: the documents name a room 'SALON' (46 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80A:0: the documents name a room 'AÇIK MUTFAK' (8.5 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80B:0: the documents name a room 'BANYO' (4.9 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80C:0: the documents name a room 'KORİDOR' (7 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C813:0: the documents name a room 'ODA' (13 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F038:0: the documents name a room 'SALON' (46 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F039:0: the documents name a room 'AÇIK MUTFAK' (8.5 m²) on L-1b; no room of the model uses it

Library gaps reported by the agent: desk modern (No audited desk model carries styled surfaces (laptop, books, decor) to clear the D3 bare-surface finding; the 180 library desks are all bare worktops.), wall_cabinet (No audited library model of wall_cabinet exists (catalog count 0), so the crude low-poly block of f_L-1_093 cannot be swapped for a realistic model.), kitchen_counter (No audited library model of kitchen_counter exists (catalog count 0), so the over-height worktop of f_L-1_003 (1.18 m) cannot be swapped for a model at working height.), fridge (f_L-1_090 is built into the counter run (integrated fridge in the run's fronts), so no library fridge model may replace it; the missing oven/hood are built by the kitchen fit, not by any agent tool.), wardrobe (Record the wardrobe library gap (no candidate within scale caps); the module build is kept.), washbasin modern minimal (All washbasin catalog models are generated (not real products); the code refuses a generated pin while a real product fits, so the dated fluted vanity model and its S1 height offset cannot be swapped to a real library model.), toilet modern minimal (All toilet catalog models are generated (not real products); the code refuses a generated pin while a real product fits, so the parametric-mesh toilet and its S1 height offset cannot be swapped to a real library model.), kitchen_counter (No audited kitchen_counter library model exists to swap f_L-1_012 to a 0.97 m working height; the piece is a module build of the drawn kitchen run.), washbasin (No audited library washbasin model fits the sloped ceiling constraint (max 1.60 m) at this location; all generated models fail the height cap, leaving the S1 floating finding unresolvable by swap.), toilet (No audited library toilet model fits the sloped ceiling constraint (max 1.52 m) at this location; all generated models fail the height cap, leaving the S1 floating finding unresolvable by swap.), tall_cabinet (The tall_cabinet was built below library level with a parametric mesh (P7); the piece has been removed but the gap is recorded for the library.), lighting warm (Finding a:D3 (missing warm light layer, cause wrong_model) has no lighting model to swap to; the warm-light layer is absent from the library, so the gap is recorded for review.), toilet (Toilet f_L-1_052 built below library level (parametric mesh, a:F412) and its lowest point is +0.200 m off the floor (c:S1:f_L-1_052); the prior swap_model was rejected because the refit kept the same model, so no audited library model of a fitting toilet exists.), washbasin (Washbasin f_L-1_025's lowest point is +0.384 m above its floor (c:S1:f_L-1_025, allowed -0.005..+0.01 m); the parametric mesh sits too high and no audited library model of a fitting washbasin exists.), washbasin (No audited real washbasin model fits: every generated candidate fails the fit rules (height cap 1.60 m under the sloped ceiling), so the floating S1 model cannot be swapped.), toilet (No audited real toilet model fits: every generated candidate fails the fit rules (height cap 1.52 m under the sloped ceiling) or was audit-removed, so the floating S1 model cannot be swapped.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 296 | 114 | 17 | 40 | 90 | layout | 36 |
| 2 | 11 | 286 | 106 | 17 | 22 | 90 | layout | 36 |
| 3 | 10 | 281 | 113 | 17 | 11 | 59 | layout | 15 |
| 4 | 21 | 513 | 157 | 37 | 12 | 21 | layout | 16 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A6 | 0 | 20 | 0 | 0 |
| AI1 | 0 | 80 | 0 | 8 |
| AI2 | 0 | 0 | 0 | 10 |
| AI3 | 0 | 5 | 0 | 0 |
| AI5 | 0 | 58 | 0 | 5 |
| B8 | 0 | 10 | 0 | 0 |
| C1 | 0 | 0 | 0 | 7 |
| C4 | 0 | 4 | 0 | 0 |
| C7 | 0 | 40 | 0 | 0 |
| D2 | 0 | 10 | 1 | 0 |
| D3 | 0 | 218 | 52 | 0 |
| F1 | 0 | 0 | 3 | 0 |
| F2 | 0 | 18 | 0 | 0 |
| F3 | 0 | 38 | 0 | 0 |
| F4 | 0 | 63 | 0 | 0 |
| F6 | 0 | 42 | 0 | 0 |
| F9 | 0 | 24 | 0 | 0 |
| G1 | 0 | 0 | 24 | 0 |
| G10 | 0 | 72 | 0 | 0 |
| G11 | 0 | 28 | 0 | 0 |
| G12 | 0 | 25 | 0 | 0 |
| G13 | 0 | 34 | 0 | 0 |
| G14 | 0 | 0 | 3 | 0 |
| G2 | 0 | 18 | 16 | 0 |
| G3 | 0 | 34 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 52 | 0 | 0 |
| G6 | 0 | 26 | 8 | 0 |
| G8 | 0 | 8 | 8 | 0 |
| G9 | 0 | 2 | 0 | 0 |
| J1 | 0 | 69 | 0 | 56 |
| K1 | 0 | 13 | 0 | 0 |
| K3 | 0 | 1 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 24 | 0 |
| M13 | 0 | 0 | 12 | 0 |
| M14 | 0 | 24 | 0 | 0 |
| M17 | 0 | 0 | 8 | 0 |
| M18 | 0 | 8 | 0 | 0 |
| M2 | 0 | 8 | 0 | 0 |
| M21 | 0 | 4 | 18 | 0 |
| M22 | 0 | 8 | 0 | 0 |
| M23 | 0 | 8 | 8 | 0 |
| M26 | 0 | 0 | 20 | 0 |
| M28 | 0 | 5 | 16 | 0 |
| M30 | 0 | 0 | 19 | 0 |
| M31 | 0 | 8 | 0 | 0 |
| M33 | 0 | 9 | 4 | 0 |
| M34 | 0 | 0 | 16 | 0 |
| NR | 0 | 18 | 0 | 0 |
| P0 | 0 | 32 | 0 | 0 |
| P2 | 0 | 4 | 0 | 0 |
| P6 | 0 | 4 | 0 | 0 |
| P7 | 0 | 41 | 0 | 0 |
| P9 | 0 | 0 | 0 | 1 |
| Q10 | 0 | 5 | 3 | 0 |
| Q12 | 0 | 21 | 1 | 0 |
| Q13 | 0 | 6 | 0 | 0 |
| Q14 | 0 | 12 | 8 | 0 |
| Q15 | 0 | 1 | 0 | 0 |
| Q3 | 7 | 1 | 0 | 0 |
| Q4 | 2 | 3 | 0 | 0 |
| Q5 | 0 | 2 | 1 | 0 |
| R3 | 0 | 0 | 32 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S1 | 0 | 64 | 0 | 0 |
| S2 | 0 | 11 | 35 | 0 |
| S4 | 0 | 0 | 2 | 0 |
| S5 | 34 | 0 | 41 | 0 |
| V1 | 4 | 28 | 3 | 0 |
| V2 | 0 | 0 | 0 | 1 |
| X2 | 5 | 2 | 8 | 0 |
| X3 | 0 | 3 | 0 | 0 |
| X5 | 0 | 0 | 55 | 0 |
| X6 | 0 | 9 | 0 | 0 |
| X9 | 0 | 1 | 0 | 0 |
| lighting_dark | 0 | 8 | 3 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 20768 | 1 | set_camera | r_L1_banyo | agent_override | - | Argus: The frame is black and empty, so the camera is not inside the room or is aimed at nothing; re-aiming it at the bathroom's main group from a free interior point restores a valid view. (fixes a:F17) | - | - |
| 20775 | 1 | swap_model | f_L1_017 | adjusted_by_ai | 41.0 -> 41.0 | Argus: The sofa is a blocky low-poly placeholder; the current model abo_B075X4F5CS is a real product but the judge says it looks crude. The swap to 3dwh_73a3f2fd339beec5aabd5ed6 (2.11 x 0.91 x 0.86 m, minimal/scandinavian) is a real library model  (fixes a:F248) | ![](agent/r1_003_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_004_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 20779 | 1 | set_camera | r_L-1_banyo | agent_override | - | Argus: The camera is pressed against the wall, cutting off the washbasin and cabinet. The set_camera tool with show will move the camera to a free pose that shows the named pieces. The previous set_camera was refused (duplicate), but that was for  (fixes a:F253) | - | - |
| 20780 | 1 | set_exterior | exterior:ground,site | agent_override | - | Argus: The outdoor view is a flat low-poly field; adding site items and ground cover gives the window a believable exterior. (fixes a:F257) | - | - |
| 20782 | 1 | swap_model | f_L-1_070 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The brown leather armchair clashes with the white sofa and black lounge chair; swapping to a minimal/modern/scandinavian model aligns it with the group. (fixes a:F261) | ![](agent/r1_009_swap_model_before_r_L-1_salon.png) | ![](agent/r1_010_swap_model_after_r_L-1_salon.png) |
| 20783 | 1 | swap_model | f_L-1_049 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The grey armchair clashes with the white sectional and blue dining chairs; swapping to a minimal/modern/scandinavian model aligns it with the group. (fixes a:F266) | ![](agent/r1_011_swap_model_before_r_L-1_salon.png) | ![](agent/r1_012_swap_model_after_r_L-1_salon.png) |
| 20784 | 1 | swap_model | f_L-1_028 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The single wood chair at the head of the table clashes with the other white chairs; swapping to a minimal/modern model aligns it with the set. (fixes a:F268) | ![](agent/r1_013_swap_model_before_r_L-1_salon.png) | ![](agent/r1_014_swap_model_after_r_L-1_salon.png) |
| 20785 | 1 | set_camera | r_L0_banyo | agent_override | - | Argus: The camera is pressed against a corner framing a blank wall and toilet roll; moving it to show the key fixtures frames the room properly. (fixes a:F272) | - | - |
| 20786 | 1 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The judge and the V1 check both say the camera is too close and hides the shower and toilet; the room's pieces are there, the pose is wrong. (fixes a:F273) | - | - |
| 20788 | 1 | set_camera | r_L0_koridor | agent_override | - | Argus: The judge and V1 both say the frame is a corner and a door leaf; the hall's only piece is the shoe_cabinet, so showing it from a free point frames the hall. (fixes a:F280) | - | - |
| 20789 | 1 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The judge names the black leather office chair as a corporate clash; the allowed list includes abo_B06W5XBL3D (0.55 x 0.53 x 0.91 m, modern), which fits the 0.50 x 0.50 m footprint and the room's style. The refused swap was abo_B081HMS8YK,  (fixes a:F282) | ![](agent/r1_015_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r1_016_swap_model_after_r_L0_yatak_odasi.png) |
| 20792 | 1 | set_camera | r_L1_koridor | agent_override | - | Argus: The judge says the corridor reads as bare and unfinished; the room does hold a shoe_cabinet, wardrobe and stair, so the camera is not showing them. Re-posing the camera to show the pieces and a door answers the cause. (fixes a:F289) | - | - |
| 20794 | 1 | swap_model | f_L1_020 | adjusted_by_ai | 41.0 -> 41.0 | Argus: The sofa is a bare boxy model. The generated model was refused (guessed units) while a real product fits; 3dwh_73a3f2fd339beec5aabd5ed6 is a real minimal/scandinavian sofa matching the 2.10 m footprint. (fixes a:F293) | ![](agent/r1_020_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_021_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 20796 | 1 | set_material | floor | agent_override | - | Argus: The terrace floor reads as a bare grey slab. A swap_model was refused (fit caps), so the floor material slot is the right lever: decking gives a designed outdoor finish. (fixes a:F299) | - | - |
| 20817 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 41.0 -> 41.0 | The 40.5 m2 room is furnished as a living room (sofa, tv_unit, table_dining, bookshelf) and the label 'Oyun Aktivite Ve Dinlenme Odası' means play/activity/relaxation room; it should be typed living so program, furniture and camera rules apply (a:N89). | ![](agent/r1_094_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_102_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 20836 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Top-scoring solver candidate places the required balcony planters and terrace_pair lounge set, resolving the missing-lounge findings and the window blockage. | ![](agent/r1_121_relayout_room_before_r_L1_teras.png) | ![](agent/r1_124_relayout_room_after_r_L1_teras.png) |
| 20839 | 1 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 0.0 -> 15.0 | The armchair is 114° off the sofa and its front is blocked by the other armchair; rotating it to face the sofa (90°) aligns it with the group and clears the front zone. | ![](agent/r1_126_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_129_rotate_piece_after_r_L-1b_salon_2.png) |
| 20844 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the terrace with the top-scored candidate to fix the twin single-chair misfit (N96) and move the two potted plants away from window win_L1_002 (G12). | ![](agent/r1_131_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_133_relayout_room_after_r_L1_teras_2.png) |
| 20850 | 1 | retype_piece | f_L1_037 | adjusted_by_ai | 21.0 -> 24.0 | Drawn 1.4x0.45 m wall piece; bench is not a living-room piece, console_table fits its size and the room, clearing F1/G14. | ![](agent/r1_135_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_137_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 20853 | 1 | report_library_gap | f_L0_029 | library_gap | - | No audited desk model carries styled surfaces (laptop, books, decor) to clear the D3 bare-surface finding; the 180 library desks are all bare worktops. | - | - |
| 20871 | 1 | move_piece | f_L0_032 | adjusted_by_ai | 77.0 -> 100.0 | Shift nightstand f_L0_032 away from the bed to resolve the 0.06 m² overlap (F9) and correct the -0.12 m gap to a valid distance (G4). | ![](agent/r1_151_move_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_153_move_piece_after_r_L0_e_yatak_odasi.png) |
| 20876 | 1 | report_library_gap | f_L-1_093 | library_gap | - | No audited library model of wall_cabinet exists (catalog count 0), so the crude low-poly block of f_L-1_093 cannot be swapped for a realistic model. | - | - |
| 20877 | 1 | move_piece | f_L0_034 | adjusted_by_ai | 77.0 -> 100.0 | Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. | ![](agent/r1_154_move_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_157_move_piece_after_r_L0_e_yatak_odasi_2.png) |
| 20878 | 1 | report_library_gap | f_L-1_003 | library_gap | - | No audited library model of kitchen_counter exists (catalog count 0), so the over-height worktop of f_L-1_003 (1.18 m) cannot be swapped for a model at working height. | - | - |
| 20881 | 1 | place_group | r_L0_e_yatak_odasi | added_by_ai | 100.0 -> 100.0 | Re-solve the sleeping_double group to ensure the nightstand on the free left side of the bed head is correctly positioned or added, addressing the missing member finding. | ![](agent/r1_155_place_group_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_161_place_group_after_r_L0_e_yatak_odasi.png) |
| 20883 | 1 | report_library_gap | f_L-1_090 | library_gap | - | f_L-1_090 is built into the counter run (integrated fridge in the run's fronts), so no library fridge model may replace it; the missing oven/hood are built by the kitchen fit, not by any agent tool. | - | - |
| 20895 | 1 | set_camera | r_L1_banyo | agent_override | - | The frame is entirely black (failed render); reposition to a free point with headroom showing the bathroom fixtures. | - | - |
| 20897 | 1 | set_lighting | r_L0_banyo | agent_override | - | Both interior views are under the EV cap; the finding names factor x1.81 on the room to cover headroom for light that does not scale with the room's lights. | - | - |
| 20900 | 1 | report_library_gap | f_L0_024 | library_gap | - | Record the wardrobe library gap (no candidate within scale caps); the module build is kept. | - | - |
| 20905 | 1 | remove_piece | f_L1_067 | added_by_ai | 77.0 -> 77.0 | AI-added parametric tall_cabinet pokes through the sloped ceiling (X2) and is mis-sized (S4); not required by the drawn bathroom_set. | ![](agent/r1_167_remove_piece_before_r_L1_banyo_2.png) | ![](agent/r1_169_remove_piece_after_r_L1_banyo_2.png) |
| 20913 | 1 | report_library_gap | f_L-1_026 | library_gap | - | All washbasin catalog models are generated (not real products); the code refuses a generated pin while a real product fits, so the dated fluted vanity model and its S1 height offset cannot be swapped to a real library model. | - | - |
| 20915 | 1 | relayout_room | r_L1_koridor | adjusted_by_ai | 100.0 -> 100.0 | Relayout with the highest-scoring candidate to resolve the missing console/wall niche (M28) for the hall. | ![](agent/r1_176_relayout_room_before_r_L1_koridor.png) | ![](agent/r1_179_relayout_room_after_r_L1_koridor.png) |
| 20916 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | Room too dark for cam_r_L0_e_banyo_1 (needs +3.68 EV vs +3.00 cap); finding names factor x2.28. | - | - |
| 20917 | 1 | report_library_gap | f_L-1_051 | library_gap | - | All toilet catalog models are generated (not real products); the code refuses a generated pin while a real product fits, so the parametric-mesh toilet and its S1 height offset cannot be swapped to a real library model. | - | - |
| 20930 | 1 | remove_piece | f_L1_066 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet stands where the sloped ceiling is only 0.82 m high (X2/F528) and no library tall_cabinet is under 1.6 m, so it cannot fit; the missing tall_cabinet is already recorded (a:F323). | ![](agent/r1_185_remove_piece_before_r_L1_banyo.png) | ![](agent/r1_187_remove_piece_after_r_L1_banyo.png) |
| 20931 | 1 | report_library_gap | f_L-1_012 | library_gap | - | No audited kitchen_counter library model exists to swap f_L-1_012 to a 0.97 m working height; the piece is a module build of the drawn kitchen run. | - | - |
| 20945 | 1 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Hall has only a shoe cabinet; solver's top candidate (9.2) re-solves the entrance group to add the missing console/coat storage for a 7.6 m² hall with 12 doors. | ![](agent/r1_191_relayout_room_before_r_L0_koridor.png) | ![](agent/r1_194_relayout_room_after_r_L0_koridor.png) |
| 20950 | 1 | report_library_gap | f_L1_016 | library_gap | - | No audited library washbasin model fits the sloped ceiling constraint (max 1.60 m) at this location; all generated models fail the height cap, leaving the S1 floating finding unresolvable by swap. | - | - |
| 20956 | 1 | report_library_gap | f_L1_022 | library_gap | - | No audited library toilet model fits the sloped ceiling constraint (max 1.52 m) at this location; all generated models fail the height cap, leaving the S1 floating finding unresolvable by swap. | - | - |
| 20959 | 1 | report_library_gap | f_L1_067 | library_gap | - | The tall_cabinet was built below library level with a parametric mesh (P7); the piece has been removed but the gap is recorded for the library. | - | - |
| 21467 | 2 | set_material | facade | agent_override | - | Argus: The exterior looks like a sterile massing study because the facade material is flat. Setting a wood cladding look will add the material richness seen in the reference. (fixes a:F306) | - | - |
| 21468 | 2 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The upper level balcony is empty. Placing a terrace_lounge group will add the necessary furniture for an outdoor living space. (fixes a:F307) | ![](agent/r2_001_place_group_before_r_L1_teras.png) | ![](agent/r2_002_place_group_after_r_L1_teras.png) |
| 21476 | 2 | set_camera | r_L-1_banyo | agent_override | - | Argus: The bathtub is built and furnished; the camera crops it so the frame reads as unfinished. Reframing the existing camera to show the full piece is the fix. (fixes a:F401) | - | - |
| 21478 | 2 | set_camera | r_L0_banyo | agent_override | - | Argus: The bathtub is built; the camera crops it into a corner against a bare tile wall. Reframing the existing camera to show the full piece is the fix. (fixes a:F403) | - | - |
| 21487 | 2 | set_material | floor | agent_override | - | Argus: The bedroom's wood floor is not laid in herringbone; setting the floor look to a herringbone parquet fixes the UL106 shortfall. (fixes a:F441) | - | - |
| 21489 | 2 | set_material | facade | agent_override | - | Argus: The stone cladding on the lower wall is a flat, repetitive texture that looks like a placeholder rather than a finished surface. (fixes a:F453) | - | - |
| 21499 | 2 | set_lighting | r_L0_yatak_odasi | agent_override | - | Raise room light power to meet the +3.0 EV cap for cam_r_L0_yatak_odasi_1 (finding names x1.71). | - | - |
| 21502 | 2 | move_piece | f_L0_010 | adjusted_by_ai | 70.0 -> 80.0 | Shift the wardrobe along the top wall toward the door corner to open the front clearance from 0.66 m to at least 0.80 m (G13). | ![](agent/r2_064_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r2_066_move_piece_after_r_L0_yatak_odasi.png) |
| 21531 | 2 | retype_piece | f_L1_035 | adjusted_by_ai | 41.0 -> 44.0 | A bench is not a living-room piece; the 1.4 x 0.45 m low table against the wall reads as a console table (c:F1:f_L1_035, c:G14:f_L1_035). | ![](agent/r2_091_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_099_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 21535 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 adds a second planter and keeps the full terrace_pair, giving the 19.7 m² terrace a proper outdoor lounge set with more greenery per the P15 lesson. | ![](agent/r2_096_relayout_room_before_r_L1_teras.png) | ![](agent/r2_102_relayout_room_after_r_L1_teras.png) |
| 21559 | 2 | set_lighting | r_L0_e_yatak_odasi | agent_override | - | View cam_r_L0_e_yatak_odasi_3 is 1.35 stops over the EV cap; the finding names factor x3 for the room. | - | - |
| 21566 | 2 | set_camera | r_L1_banyo | agent_override | - | The frame is entirely black; re-pose the camera to a free point showing the bathroom fixtures (basin, toilet, bath) at eye height. | - | - |
| 21571 | 2 | swap_model | f_L0_007 | adjusted_by_ai | 100.0 -> 100.0 | Swap to the Full Saddle Back Upholstered Bed (Grey), a modern/minimal 1.61x2.05 m model with layered bedding (throw, cushions) to fix the D3 missing-layer and M30 missing-throw findings. | ![](agent/r2_137_swap_model_before_r_L0_e_yatak_odasi.png) | ![](agent/r2_140_swap_model_after_r_L0_e_yatak_odasi.png) |
| 21573 | 2 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 gives the terrace_pair its full twin (2 members) and a complete balcony group, resolving the single-chair misfit finding a:N96. | ![](agent/r2_138_relayout_room_before_r_L1_teras_2.png) | ![](agent/r2_141_relayout_room_after_r_L1_teras_2.png) |
| 21577 | 2 | set_lighting | r_L-1_banyo | agent_override | - | View cam_r_L-1_banyo_1 is 0.19 stops over the EV cap; the finding prescribes x1.61 room lighting to bring incident light to target. | - | - |
| 21578 | 2 | relayout_room | r_L1_koridor | adjusted_by_ai | 100.0 -> 100.0 | Add the missing console/wall niche required by the hall program (H1, H4) via the solver's candidate 2 layout. | ![](agent/r2_142_relayout_room_before_r_L1_koridor.png) | ![](agent/r2_143_relayout_room_after_r_L1_koridor.png) |
| 21580 | 2 | report_library_gap | report_library_gap | library_gap | - | Finding a:D3 (missing warm light layer, cause wrong_model) has no lighting model to swap to; the warm-light layer is absent from the library, so the gap is recorded for review. | - | - |
| 21588 | 2 | report_library_gap | f_L-1_052 | library_gap | - | Toilet f_L-1_052 built below library level (parametric mesh, a:F412) and its lowest point is +0.200 m off the floor (c:S1:f_L-1_052); the prior swap_model was rejected because the refit kept the same model, so no audited library model of a fitting toilet exists. | - | - |
| 21589 | 2 | report_library_gap | f_L-1_025 | library_gap | - | Washbasin f_L-1_025's lowest point is +0.384 m above its floor (c:S1:f_L-1_025, allowed -0.005..+0.01 m); the parametric mesh sits too high and no audited library model of a fitting washbasin exists. | - | - |
| 21621 | 2 | report_library_gap | f_L1_015 | library_gap | - | No audited real washbasin model fits: every generated candidate fails the fit rules (height cap 1.60 m under the sloped ceiling), so the floating S1 model cannot be swapped. | - | - |
| 21622 | 2 | report_library_gap | f_L1_021 | library_gap | - | No audited real toilet model fits: every generated candidate fails the fit rules (height cap 1.52 m under the sloped ceiling) or was audit-removed, so the floating S1 model cannot be swapped. | - | - |
| 21633 | 2 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Candidate 1 was tried in round 1 and a:N88 (hall needs console/coat storage) persists; trying candidate 2 to add the missing entrance storage. | ![](agent/r2_160_relayout_room_before_r_L0_koridor.png) | ![](agent/r2_161_relayout_room_after_r_L0_koridor.png) |
| 22132 | 3 | place_group | r_L1_teras_2 | added_by_ai | 100.0 -> 100.0 | Argus: Twin terrace with the same single-chair misfit. (fixes a:N96) | ![](agent/r3_004_place_group_before_r_L1_teras_2.png) | ![](agent/r3_005_place_group_after_r_L1_teras_2.png) |
| 22135 | 3 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi | added_by_ai | 44.0 -> 54.0 | Argus: The L1 living room (40.5 m2) has a table_dining but no dining group (chairs around it). A dining table without chairs is a misfit; the room needs a dining group. (fixes a:N99) | ![](agent/r3_008_place_group_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_009_place_group_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 22185 | 3 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 3 re-solves the terrace with the balcony planters and a full terrace_pair lounge set, giving the 19.7 m² terrace a usable lounging arrangement (fixes a:N95, a:N115, a:F307). | ![](agent/r3_090_relayout_room_before_r_L1_teras.png) | ![](agent/r3_092_relayout_room_after_r_L1_teras.png) |
| 22188 | 3 | swap_model | f_L0_010 | adjusted_by_ai | 80.0 -> 80.0 | Swap the light pine wardrobe for a dark grey modern-minimal wardrobe to match the darker headboard wood and grey walls (F285). | ![](agent/r3_093_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r3_096_swap_model_after_r_L0_yatak_odasi.png) |
| 22193 | 3 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidates 1 and 2 were already tried and accepted but the twin-terrace single-chair misfit (a:N96) persists; candidate 3 is the only remaining untried solver layout, with better wall_use (0.59) and no hard failures. | ![](agent/r3_100_relayout_room_before_r_L1_teras_2.png) | ![](agent/r3_105_relayout_room_after_r_L1_teras_2.png) |
| 22205 | 3 | swap_model | f_L0_007 | adjusted_by_ai | 100.0 -> 100.0 | Swap to a modern bed model with layered bedding (throw, cushions) to fix the D3 missing-layer and M30 missing-throw findings. | ![](agent/r3_112_swap_model_before_r_L0_e_yatak_odasi.png) | ![](agent/r3_114_swap_model_after_r_L0_e_yatak_odasi.png) |
| 22210 | 3 | relayout_room | r_L1_koridor | adjusted_by_ai | 100.0 -> 100.0 | Candidates 1 and 2 already tried; candidate 3 is the remaining solver layout to satisfy the hall's console/wall-niche requirement (H1, H4). | ![](agent/r3_118_relayout_room_before_r_L1_koridor.png) | ![](agent/r3_123_relayout_room_after_r_L1_koridor.png) |
| 22218 | 3 | move_piece | f_L1_031 | adjusted_by_ai | 54.0 -> 64.0 | Move armchair 0.3m toward coffee table f_L1_023 to reduce distance below 2.50m | ![](agent/r3_127_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_128_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 22228 | 3 | move_piece | f_L1_007 | adjusted_by_ai | 64.0 -> 64.0 | Move dining chair north 0.31m to increase clearance behind it from wall | ![](agent/r3_130_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_132_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 22243 | 3 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Candidates 1 and 2 were already tried; candidate 3 is the remaining solver layout to address the missing console/coat storage in the hall. | ![](agent/r3_136_relayout_room_before_r_L0_koridor.png) | ![](agent/r3_138_relayout_room_after_r_L0_koridor.png) |
| 22262 | 3 | set_camera | r_L1_banyo | agent_override | - | The view is a failed black render (V1/J1) and misses the bathtub context (Q12); repositioning to a valid interior point with headroom will show the room and fixtures. | - | - |
| 23054 | 4 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace is missing its main furniture group (armchairs and side table). The place_group tool will add the missing terrace_lounge set. (fixes a:F13) | ![](agent/r4_001_place_group_before_r_L1_teras.png) | ![](agent/r4_002_place_group_after_r_L1_teras.png) |
| 23058 | 4 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The bed f_L0_019 is cut out of the render frame, so the bedroom has no visible anchor. Move the camera to show the bed and the door. (fixes a:F154) | - | - |
| 23061 | 4 | correct_geometry | o_L1_001 | corrected_by_ai | - | Argus: The opening o_L1_001 is not cut through wall w_L1_003, so the wall is solid where the documents show an opening. (fixes a:F161) | - | - |
| 23063 | 4 | set_camera | r_L-1_banyo | agent_override | - | Argus: The bathroom view shows only a tub rim; the washbasin is not in frame and there is no mirror over it, so the room reads as unfinished. (fixes a:F175) | - | - |
| 23064 | 4 | set_camera | r_L-1_banyo | agent_override | - | Argus: The bathtub is shown in isolation with no visible taps, mixer, or surrounding design elements; it looks like a bare object in a corner. (fixes a:F176) | - | - |
| 23073 | 4 | set_camera | r_L1_banyo | agent_override | - | Argus: The camera is a tight crop of a corner showing only a blank wall and a small fixture; the main pieces are not in view. (fixes a:F245) | - | - |
| 23077 | 4 | swap_model | f_L-1_049 | adjusted_by_ai | 30.0 -> 30.0 | Argus: models_it_may_take lists 3dwh_9c3a1772a72c4b00c78bd2ea as minimal/modern/scandinavian, matching the white modern sectional. (fixes a:F261) | ![](agent/r4_015_swap_model_before_r_L-1_salon.png) | ![](agent/r4_016_swap_model_after_r_L-1_salon.png) |
| 23078 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The finding says the main group (basin, toilet, cabinet) is not in view; showing the bathtub (f_L0_025) is the anchor of the bathroom set, and the code will pick a free pose that shows it plus the room. (fixes a:F265) | - | - |
| 23080 | 4 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The finding names the shower and toilet as out of view; f_L0_015 and f_L0_006 are the main fixtures to show. (fixes a:F269) | - | - |
| 23082 | 4 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The black mesh office chair reads as a home-office and clashes with the bed and the calm styled style. Swapping to a minimal/modern chair (3dwh_54a792101c925f12bff90916, 0.50 x 0.49 x 0.76 m) from the allowed list reconciles the set. (fixes a:F280) | ![](agent/r4_017_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r4_018_swap_model_after_r_L0_yatak_odasi_3.png) |
| 23083 | 4 | set_camera | r_L1_koridor | agent_override | - | Argus: The judge scores the view 2/5: the camera is positioned extremely close to a low-poly plant that blocks the view of the hallway. The camera must be moved to a free point that shows the hallway layout and the wardrobe. (fixes a:F283) | - | - |
| 23090 | 4 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Re-place the terrace furniture so the main seating group (armchairs + side table) is present and defined, fixing the missing-group findings. | ![](agent/r4_051_relayout_room_before_r_L1_teras.png) | ![](agent/r4_052_relayout_room_after_r_L1_teras.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 20769 | 1 | add_camera | r_L0_merdiven | show: none of the 6 best poses of r_L0_merdiven that show f_L0_001 passes the camera checks: cam_r_L0_merdiven_1 stands inside f_L0_001 (stair) | Argus: Room r_L0_merdiven (Merdiven, 5.7 m2) has no view: the stair fills the room and its only camera point is inside the stair. The hall shows it per docs/milestone11.md §1.3 M5. Adding an interior camera for this room with the stair in show wil (fixes a:F94) |
| 20770 | 1 | set_camera | r_L0_e_yatak_odasi | show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views | Argus: Door d_L0_002 is built (from_documents) but the one view that must show it, cam_r_L0_e_yatak_odasi_1, does not; the camera is the stage that failed to frame it. (fixes a:F104) |
| 20771 | 1 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 0.29 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No frontal view of the entrance facade exists; the exterior set lacks the required frontal shot. (fixes a:F165) |
| 20772 | 1 | retype_piece | f_L-1_056 | drawn_lock: f_L-1_056: drawn fixed equipment keeps its type (bathtub) | Argus: The L-1 bathrooms are built with a bathtub instead of the walk-in shower the lesson requires. (fixes a:F174) |
| 20773 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show d_L-1_003 passes the camera checks: cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Argus: The only interior view that sees a door on L-1 shows a closed door and a bare wall. (fixes a:F175) |
| 20774 | 1 | place_group | r_L1_koridor | no_change: r_L1_koridor already has its entrance r_L1_koridor.entrance (anchor None, members f_L1_054): nothing missing, never a second set | Argus: The hall has no console or wall niche; the entrance group adds the console and lit niche the hall scheme requires. set_room_type was refused (already a hall), so the missing piece is the group, not the type. (fixes a:F245) |
| 20776 | 1 | swap_model | f_L-1_038 | acceptance: pin_refused: f_L-1_038: 3dwh_371b2b828aef220519cc3b6a: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The table_dining and chair cut each other by 0.034 m (allowed 0.010 m). The current model module:table_dining:table_long is 3.35 x 1.00 m; swapping to 3dwh_371b2b828aef220519cc3b6a (3.20 x 1.20 x 0.74 m) changes the footprint so the collisi (fixes a:F249) |
| 20777 | 1 | swap_model | f_L0_006 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The washbasin is a crude low-poly model. The current model module:washbasin:bath_set is a parametric family that renders poorly. Swapping to 3dwh_6597c60d5f0b3aa5ee0c0169 (0.96 x 0.50 x 0.18 m, modern/scandinavian) is a real library model w (fixes a:F250) |
| 20778 | 1 | swap_model | f_L-1_026 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The washbasin and vanity cabinet are a dated catalog style. The current model module:washbasin:bath_set is a parametric family that renders as a disjointed dark bowl and fluted wood. Swapping to 3dwh_6597c60d5f0b3aa5ee0c0169 (0.96 x 0.50 x  (fixes a:F252) |
| 20781 | 1 | swap_model | f_L-1_090 | built_in: f_L-1_090: the fridge stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: The fridge is missing from the scene; swapping to a proper fridge model restores the essential kitchen appliance. (fixes a:F259) |
| 20787 | 1 | set_camera | r_L0_e_banyo | show: none of the 5 best poses of r_L0_e_banyo that show f_L0_015, f_L0_006 passes the camera checks: duplicate: cam_r_L0_e_banyo_2 would show the view cam_r_L0_e_banyo_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_banyo, or remove one of the two views; cam_r_L0_e_banyo_2: none of the room's main pieces (shower, toilet, washbasin) is in its frame, while the room's camera search frames one | Argus: The judge says the close-up hides the bathtub and toilet; the pieces exist in r_L0_e_banyo, the pose is wrong. (fixes a:F275) |
| 20790 | 1 | swap_model | f_L0_030 | acceptance: pin_refused: f_L0_030: abo_B075Z96KQL: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The judge names the white Shaker desk as a dated clash; the allowed list includes abo_B075Z96KQL (1.38 x 0.61 x 0.79 m, industrial/modern/scandinavian), which fits the 1.45 x 0.60 m footprint and the room's style. The refused swaps were abo (fixes a:F283) |
| 20791 | 1 | swap_model | f_L0_010 | lower_quality: f_L0_010: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The judge names the raw light wood as a clash; the allowed list includes hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 (1.48 x 0.61 x 1.99 m, modern/scandinavian), which fits the 1.45 x 0.60 m footprint and the room's style. The refused swa (fixes a:F285) |
| 20793 | 1 | swap_model | f_L1_005 | asset_unusable: abo_B07B82PXCW is not used: audit pending | Argus: The dark traditional table clashes with the modern room. The current model (hssd_...) is not in the allowed list and swap to the current model was refused as no-change; abo_B07B82PXCW is a minimal/modern table that fits the 0.78 m footprint (fixes a:F292) |
| 20795 | 1 | set_exterior | exterior:ground,site | no_change: the exterior already has these values ({"ground": "grass", "site": {"fence": "hedge", "path": true, "trees": 8}}): nothing to change | Argus: The judge says the lawn is a flat untextured green plane. Setting the ground to grass and adding trees/path answers the environment cause. (fixes a:F298) |
| 20797 | 1 | set_exterior | exterior:ground,site,sun | sun: azimuth 240 degrees (compass; 240 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Argus: The judge says the lighting is flat and grey and the landscaping generic. Setting a warm sun (azimuth 240, elevation 35) plus real ground/site detail answers both the lighting and the landscape cause. (fixes a:F304) |
| 20799 | 1 | move_piece | f_L0_045 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.16 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.07 m from the bed side (needs ≤ 0.30 m)) | Moving nightstand away from window win_L0_004 (sill 0.20m) to clear the blocked opening |
| 20802 | 1 | move_piece | f_L0_045 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.16 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.08 m from the bed side (needs ≤ 0.30 m)) | Moving nightstand further up along right wall to clear window and avoid bed overlap |
| 20803 | 1 | move_piece | f_L0_045 | score: plausibility 70 -> 34 (F3 f_L0_045: nightstand: its back is not on a wall (0.13 m off); F6 f_L0_045: nightstand f_L0_045: 0.34 m free in front of it (the wall in the way); it cannot be used (needs 0.30 m to open, 0.40 m to use); G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: its back 2.27 m from the headboard line (needs ≤ 0.30 m)) | Moving nightstand to left side of bed to clear window win_L0_004 |
| 20806 | 1 | move_piece | f_L0_045 | max_tries: f_L0_045 was edited 3 times in this round | Moving nightstand up 0.29m along right wall to clear window sill (0.20m + 0.05m buffer) |
| 20809 | 1 | move_piece | f_L0_012 | f_L0_012: inside_room (outline: wardrobe reaches 0.23 m² through the room outline, up to 0.156 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 70 -> 60 (F3 f_L0_012: wardrobe: its back is not on a wall (0.16 m off); F9 f_L0_012: wardrobe reaches 0.23 m² through the room outline, up to 0.156 m deep) | Moving wardrobe 0.16m towards wall to increase front clearance from 0.66m to 0.80m |
| 20810 | 1 | resize_piece | f_L-1b_042 | score: plausibility -15 -> -25 (F3 f_L-1b_042: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_051: armchair does not face its group (f_L-1b_042, f_L-1b_046); F4 f_L-1b_075: armchair does not face its group (f_L-1b_046, f_L-1b_042); G3 f_L-1b_051: armchair f_L-1b_051 is 65° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.57 m (needs ≤ 2.50 m)) | Sofa is turned 90° against product sizes; swap to 2.13m wide x 0.90m deep to match a real sofa. |
| 20811 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.65 m free in front, needs ≥ 0.80 m) | Moving wardrobe left along top wall to find a position with 0.80m front clearance |
| 20813 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn armchair f_L-1_072 to face +Y (into the room) so it no longer stands behind the back of sofa f_L-1_054 looking at it (c:F4:f_L-1_072). |
| 20814 | 1 | rotate_piece | f_L-1_102 | score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of it) | Turn tv_unit f_L-1_102 to face +X (toward the seating) so it no longer stands behind the back of armchair f_L-1_069 looking at it (c:F4:f_L-1_102). |
| 20815 | 1 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Shift table_coffee f_L-1_074 away from armchair f_L-1_069 to clear the 0.12 m² overlap (c:F9:f_L-1_074). |
| 20816 | 1 | mark_not_furniture | f_L-1b_001 | no_crop: f_L-1b_001 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The large untyped outline is a misread boundary around the already-built dining group, not a single piece of furniture. |
| 20818 | 1 | relayout_room | r_L-1_salon_2 | acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 2 more kept | Apply solver candidate 1 (score 9.24, recommended) to re-place the AI pieces and fix the G11 walkway clearance issues for the seating group. |
| 20819 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 50 (F3 f_L0_020: bed_double: the headboard stands in the room (0.22 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Moving bed 0.22m left to increase right-side clearance from 0.53m to 0.60m+ |
| 20820 | 1 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 0.59m off the wall; snap it to the right wall to clear F3 and the blocked front zone. |
| 20821 | 1 | resize_piece | f_L-1b_041 | score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.43 m (needs ≤ 2.50 m)) | The sofa is drawn 0.90 m wide x 2.13 m deep, 90° against the type's product sizes; swapping to 2.13 m wide x 0.90 m deep aligns it with real sofa dimensions. |
| 20822 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | acceptance: finding F1:f_L1_037 is still there after the edit (bench is not a piece of a living room); 1 more kept | Room is furnished as a living room (sofas, coffee tables, TV unit) but typed 'other'; setting to living resolves a:N90 and makes bench f_L1_037 valid (F1, G14). |
| 20824 | 1 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi.dining | no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | Dining table f_L1_005 has only 2 of 4 chairs; completing the group adds the missing chairs (a:N99, c:G6:f_L1_005). |
| 20825 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Moving bed 0.07m left to slightly increase right-side clearance while keeping headboard near wall |
| 20826 | 1 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Re-solve the overcrowded 14.1 m² bedroom so the bed, wardrobe and desk clearances (G5, G13) and the missing nightstand (G4) are fixed together. |
| 20827 | 1 | retype_piece | f_L1_019 | no_change: f_L1_019 is already a sofa | Confirm drawn sofa type to clear Argus wrong_type misfit a:N92. |
| 20828 | 1 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.f_L1_020 | no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.f_L1_020 (missing tv_unit): no place passes the checks (seating: no place passes the checks) | Sofa f_L1_020 has no TV unit opposite and the coffee table is not in front; completing the group adds the missing tv_unit and repositions the coffee table (a:N101, c:G1:f_L1_020, c:G2:f_L1_036). |
| 20829 | 1 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.35 m) | Move sofa back onto the right wall to clear F3 (back off wall) and the blocked front zone. |
| 20830 | 1 | move_piece | f_L0_020 | f_L0_020: no_overlap, f_L0_044: no_overlap, score: plausibility 70 -> 57 (F9 f_L0_044: nightstand f_L0_044 overlaps bed_double f_L0_020 by 0.07 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free left side of the head (0.36 m free); G4 f_L0_044: nightstand f_L0_044 of bed_double f_L0_020: -0.17 m from the bed side (needs ≤ 0.30 m); G5 f_L0_020: bed_double f_L0_020: 0.36 m free along the left side, needs ≥ 0.60 m) | Moving bed 0.19m up along right wall to check if clearance improves |
| 20831 | 1 | move_piece | f_L-1b_045 | acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.29 m off)) | The sofa is 0.59 m off the north wall; moving it 0.39 m north puts its back on the wall and clears the front zone blocked by the plant. |
| 20832 | 1 | relayout_room | r_L-1_salon_2 | candidate: candidate 2 does not exist: 1 usable candidate(s) | Try solver candidate 2 to see if it resolves the G11 walkway clearance issues for the seating group. |
| 20833 | 1 | retype_piece | f_L1_024 | acceptance: finding AI1:f_L1_024 is still there after the edit (Argus: Twin hall with the same wardrobe misfit.); a retype to the piece's own type only confirms it (status unverified -> verified, the same fitted model): nothing changes in the render, so its vision findings stay | Confirm drawn coffee table type to clear Argus wrong_type misfit a:N98. |
| 20835 | 1 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Using solver to find a layout that satisfies all clearance requirements for bed, wardrobe, and nightstand |
| 20837 | 1 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | Move table_coffee f_L-1_074 left to clear the 0.12 m² overlap with armchair f_L-1_069 (c:F9:f_L-1_074). |
| 20838 | 1 | move_piece | f_L1_020 | score: plausibility 41 -> -9 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_050: bookshelf f_L1_050: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Moving sofa f_L1_020 further from f_L1_017 to clear the blocked front zone (c:F6:f_L1_020, a:F6:f_L1_020). |
| 20840 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair f_L-1b_033 has only 0.78m behind it, needs 0.81m; nudge it away from the wall to gain clearance. |
| 20841 | 1 | move_piece | f_L1_036 | drawn_lock: f_L1_036: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.50 m) | Moving coffee table f_L1_036 to be in front of sofa f_L1_020 (c:G2:f_L1_036, a:G2:f_L1_036). |
| 20843 | 1 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.05 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move table_coffee f_L-1_074 further from armchair f_L-1_069 to clear the 0.12 m² overlap (c:F9:f_L-1_074). |
| 20847 | 1 | move_piece | f_L1_007 | acceptance: finding G6:f_L1_007 is still there after the edit (chair f_L1_007: 0.73 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Moving chair f_L1_007 slightly to increase clearance from the table edge to the wall behind (c:G6:f_L1_007, a:G6:f_L1_007). |
| 20849 | 1 | rotate_piece | f_L-1b_054 | acceptance: finding G3:f_L-1b_054 is still there after the edit (armchair f_L-1b_054 is 57° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m)) | The armchair is 33° off the sofa and its front is blocked by the other armchair; rotating it to face the sofa (90°) aligns it with the group and clears the front zone. |
| 20851 | 1 | mark_not_furniture | f_L-1b_002 | no_crop: f_L-1b_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The 5.14m x 2.37m untyped outline is a cluster of drawn pieces, not a single furniture item; mark it as not furniture. |
| 20854 | 1 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move table_coffee f_L-1_074 to the right to clear the 0.12 m² overlap with armchair f_L-1_069 (c:F9:f_L-1_074). |
| 20855 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_037 is still there after the edit (bench is not a piece of a living room); 1 more kept | Room is furnished as a living room (sofas, coffee tables, TV unit) but typed 'other'; setting to living resolves a:N90. |
| 20856 | 1 | rotate_piece | f_L-1b_051 | acceptance: finding F4:f_L-1b_051 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)) | Armchair f_L-1b_051 faces 180° but should face the sofa group (270°) to clear F4/G3. |
| 20857 | 1 | rotate_piece | f_L-1b_054 | f_L-1b_053: no_overlap, f_L-1b_054: no_overlap, score: plausibility 15 -> -5 (G3 f_L-1b_054: armchair f_L-1b_054 is 84° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m); G11 f_L-1b_054: armchair f_L-1b_054: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_085: bookshelf f_L-1b_085: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_087: armchair f_L-1b_087: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Facing the armchair directly at the sofa f_L-1b_041 (117°) brings it within 30° of the group axis and clears the front zone blocked by the other armchair. |
| 20858 | 1 | move_piece | f_L1_020 | score: plausibility 41 -> -9 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_050: bookshelf f_L1_050: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Moving sofa f_L1_020 slightly (0.29m) to clear the blocked front zone from f_L1_017 (c:F6:f_L1_020, a:F6:f_L1_020). |
| 20860 | 1 | move_piece | f_L1_036 | drawn_lock: f_L1_036: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.60 m) | Moving coffee table f_L1_036 0.24m towards the sofa f_L1_020 to be in front of it (c:G2:f_L1_036, a:G2:f_L1_036). |
| 20861 | 1 | move_piece | f_L1_007 | score: plausibility 41 -> 31 (F4 f_L1_007: chair does not face its group (f_L1_005); G6 f_L1_007: chair f_L1_007 is 73° off the table f_L1_005 (needs ≤ 45°)) | Moving chair f_L1_007 0.32m to increase clearance from the table edge to the wall behind to at least 0.81m (c:G6:f_L1_007, a:G6:f_L1_007). |
| 20863 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | The chair has only 0.78 m clearance behind it, needing 0.81 m; moving it 0.03 m south provides the required clearance. |
| 20865 | 1 | move_piece | f_L1_063 | snap: f_L1_063: no free place on wall w_L1_001 (doors, windows) | TV unit f_L1_063 is 1.01 m off the wall; snap its back to the north wall span s0 to clear F3. |
| 20866 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)) | Armchair f_L-1b_052 faces 0° but should face the sofa group (270°) to clear F4/G3. |
| 20867 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017); 3 more kept | Using solver candidate 1 to fix the seating group layout issues: f_L1_020 front zone blocked by f_L1_017, f_L1_036 not in front of f_L1_020, f_L1_031 too far from f_L1_023, and f_L1_007 clearance (c:F6:f_L1_020, c:G2:f_L1_036, c:G3:f_L1_031, c:G6:f_L1_007). |
| 20872 | 1 | move_piece | f_L-1b_045 | acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.29 m off)) | The sofa is 0.59 m off the north wall; moving it 0.46 m north puts its back on the wall and clears the front zone blocked by the plant. |
| 20882 | 1 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Vector geometry (hanging rail with hangers) outranks the AI passes; confirming the drawn wardrobe type resolves the RC wrong_type finding. |
| 20885 | 1 | move_piece | f_L-1b_041 | snap: f_L-1b_041: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | The sofa is 2.00 m off the west wall; snapping its back to the wall resolves the F3 finding and orients it correctly in the living room. |
| 20887 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free right side of the head. |
| 20888 | 1 | retype_piece | f_L1_027 | acceptance: finding RC:f_L1_027 is still there after the edit (f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | Vector geometry shows a hanging rail with hangers (coat closet); dresser is the candidate type that fits the 1.52 x 0.60 m footprint and the hall zone. |
| 20889 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | The chair has only 0.78 m clearance behind it, needing 0.81 m; moving it 0.06 m south provides the required clearance. |
| 20894 | 1 | place_group | r_L0_e_yatak_odasi_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-solve the drawn sleeping_double group around the bed anchor so a nightstand is placed on the free right side of the head (fixes G4:f_L0_008). |
| 20906 | 1 | retype_piece | f_L1_027 | acceptance: finding RC:f_L1_027 is still there after the edit (f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | The recognition crop shows a low hanging rail with hangers (coat closet); bench is the other candidate type that fits the 1.52 x 0.60 m footprint and hall zone, resolving the RC wrong_type finding. |
| 20907 | 1 | set_camera | r_L-1_banyo_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Camera pressed against a wall cutting off the washbasin; move to a free point framing the whole bathroom. |
| 20908 | 1 | set_camera | r_L-1_koridor_2 | show: no free camera point of r_L-1_koridor_2 shows door, corridor (door, corridor not in r_L-1_koridor_2: name its pieces, doors or windows) | Camera inside a proxy showing only a closed door and bare wall; move to a free point in the corridor showing the space and open door. |
| 20911 | 1 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | The drawn washbasin floats 0.384 m above the floor and reads as a bare bowl; a floor-standing modern vanity model removes the S1 gap and gives the integrated look the reference wants. |
| 20912 | 1 | swap_model | f_L0_018 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | The toilet's lowest point is 0.200 m above the floor; a floor-standing model of the same 0.41x0.69 footprint removes the S1 gap. |
| 20919 | 1 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Floor-standing japandi vanity model to remove the 0.384 m S1 gap and give the integrated look the reference wants. |
| 20920 | 1 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above floor; swapping to a floor-anchored modern washbasin model to clear S1. |
| 20921 | 1 | set_camera | r_L-1_banyo_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Camera pressed against a wall cutting off the washbasin; move to a free point framing the whole bathroom. |
| 20924 | 1 | swap_model | f_L1_022 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Current toilet model floats 0.200 m above floor; swapping to a floor-anchored japandi toilet model to clear S1. |
| 20925 | 1 | swap_model | f_L0_018 | pin_refused: f_L0_018: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Floor-standing toilet model of the same 0.40x0.71 footprint to remove the 0.200 m S1 gap. |
| 20926 | 1 | set_camera | r_L-1_koridor_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Camera inside a proxy showing only a closed door and bare wall; move to a free point in the corridor showing the space and the door. |
| 20932 | 1 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Floor-standing minimal vanity model to remove the 0.384 m S1 gap and give the integrated look the reference wants. |
| 20937 | 1 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Trying a lower-profile minimal washbasin model (0.32 m depth) that should fit under the sloped ceiling and anchor to the floor. |
| 20939 | 1 | swap_model | f_L0_018 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Floor-standing minimal toilet model of the same 0.39x0.73 footprint to remove the 0.200 m S1 gap. |
| 20940 | 1 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Trying a different japandi toilet model (0.415 x 0.691 x 0.568 m) that should anchor to the floor properly. |
| 20946 | 1 | rotate_piece | f_L0_014 | drawn_lock: f_L0_014: the new front does not fix the error (its front faces a wall); with the front at 270 deg its back is not on a wall | Shower front faced 90° into a wall 0.10 m away; turning it to face 270° (toward the room interior) clears the F4 orientation error. |
| 20947 | 1 | swap_model | f_L0_003 | max_tries: f_L0_003 was edited 3 times in this round | Floor-standing mediterranean vanity model to remove the 0.384 m S1 gap and give the integrated look the reference wants. |
| 20948 | 1 | swap_model | f_L0_018 | max_tries: f_L0_018 was edited 3 times in this round | Floor-standing japandi toilet model of the same 0.42x0.69 footprint to remove the 0.200 m S1 gap. |
| 20953 | 1 | add_camera | r_L0_merdiven | cam_r_L0_merdiven_2 stands inside f_L0_001 (stair), the camera stands 0.00 m from f_L0_001 (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [6.05, 8.66] | Stair core view (M5): pose in the open NE corner of the hall, lens kept out of the stair volume, looking across the room at the stair. |
| 20961 | 1 | add_camera | r_L0_merdiven | cam_r_L0_merdiven_3 stands inside f_L0_001 (stair), the camera stands 0.00 m from f_L0_001 (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [6.05, 8.66] | Stair core view (M5): the code's nearest free point in the hall, lens out of the stair volume, looking across at the stair. |
| 20965 | 1 | fix_fixture | f_L0_001 | fixture_place: f_L0_001: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door o_L0_001) | The stair's drawn footprint (2.64 x 2.1 m) fills the 5.7 m² hall so no camera point in the room is free of the stair volume; shrink it to the nearest real product size that fits the bay so the hall can be viewed (M5). |
| 21466 | 2 | set_exterior | exterior:sun | sun: azimuth 135 degrees (compass; 135 in the building frame, north 0, assumed (+Y is north: no north arrow)) lights the back: the X7 rule wants the sun on the side of the main (+y) facade | Argus: The render is flat and grey because the sun is not set to a warm, directional position. Setting the sun azimuth and elevation will add warm light and shadows. (fixes a:F305) |
| 21469 | 2 | set_camera | ext_3 | eye height 2.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The previous attempt was refused because the eye height was 2.16 m. Setting the position to 1.6 m (eye level) and adjusting the target and lens to frame the whole building will fix the awkward close-up framing. (fixes a:F309) |
| 21470 | 2 | retype_piece | f_L-1_085 | retype: side_table is no candidate for f_L-1_085 (0.30 x 0.20 m at [2.97, 11.70]): the size table and the room / zone give floor_lamp, potted_plant | Argus: The piece f_L-1_085 is untyped. Retyping it as a side_table (a common small furniture item in a living room) will allow it to be built. (fixes a:F312) |
| 21471 | 2 | place_group | r_L0_e_banyo_2 | no_change: r_L0_e_banyo_2 already has its bathroom_set r_L0_e_banyo_2.bathroom_set (anchor f_L0_014, members f_L0_004, f_L0_016): nothing missing, never a second set | Argus: The twin r_L0_e_banyo has the tall_cabinet; r_L0_e_banyo_2 is the same 4.0 m2 bathroom and is missing it. complete_group was refused because the group id is the room's set, so place_group on the room completes the set with what it misses. (fixes a:F322) |
| 21472 | 2 | place_group | r_L1_banyo | no_change: r_L1_banyo already has its bathroom_set r_L1_banyo.bathroom_set (anchor f_L1_021, members f_L1_015, f_L1_025): nothing missing, never a second set | Argus: Both r_L1_banyo and r_L1_banyo_2 have bathtub, toilet, washbasin but no tall_cabinet, while every other bathroom in the project has one. Completing the set adds the missing cabinet. (fixes a:F323) |
| 21473 | 2 | set_camera | ext_7 | role: ext_7 is the site view the camera policy allows and keeps its role (docs/milestone13.md D8 and the site view rule): an aerial view stands at least 1 m above the ridge (z 7.01 m or more; the ridge is at 6.01 m) and looks down at least 5 degrees; this pose stands at z 0.00 m, below that line (the camera validator and code X6 judge it as an eye-level view) and looks 0.0 degrees down, less than the 5 degrees (the next build would make it an eye-level view); its height above eye level and its downward pitch are by design, not a finding; add_camera with a new view id for an eye-level view | Argus: win_L-1_002 is a from_documents window that ext_7 must show but does not. Re-aiming ext_7 at the window (the code picks the valid exterior pose) restores the required view. (fixes a:F328) |
| 21474 | 2 | retype_piece | f_L-1_079 | no_change: f_L-1_079 is already a ottoman | Argus: The plan shows a 0.40 x 0.40 m ottoman in r_L-1_salon_2 that the model does not build; retype_piece fits and builds it. (fixes a:F378) |
| 21475 | 2 | retype_piece | f_L-1_080 | no_change: f_L-1_080 is already a ottoman | Argus: The plan shows a 0.40 x 0.40 m ottoman in r_L-1_salon that the model does not build; retype_piece fits and builds it. (fixes a:F379) |
| 21477 | 2 | swap_model | f_L0_003 | no_change: f_L0_003 already uses the model 3dwh_4736e8ccac82f4d690680828 | Argus: The two bowl-only models were refused (audit removed) and the third try hit max_tries; the remaining candidate 3dwh_4736e8ccac82f4d690680828 is a full-height (1.07 m) integrated unit that gives the designed look the finding asks for. (fixes a:F402) |
| 21479 | 2 | swap_model | f_L-1_051 | acceptance: pin_refused: f_L-1_051: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric mesh is below library level; the gen_toilet and objaverse candidates were refused (fit rules / audit removed), but 3dwh_36adbef7518af3145f49b210 (0.46 x 0.72 x 0.80 m) is a real model that fits the 0.50 x 0.69 m piece and was (fixes a:F411) |
| 21480 | 2 | swap_model | f_L-1_052 | acceptance: pin_refused: f_L-1_052: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric mesh is below library level; the gen_toilet and objaverse candidates were refused (fit rules / audit removed), but 3dwh_36adbef7518af3145f49b210 (0.46 x 0.72 x 0.80 m) is a real model that fits the 0.50 x 0.69 m piece and was (fixes a:F412) |
| 21481 | 2 | swap_model | f_L-1_073 | acceptance: pin_refused: f_L-1_073: abo_B07GDSF3MR: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric mesh is below library level; the move attempts were refused (overlap / no_overlap), but swapping to a real model (abo_B07GDSF3MR, 0.80 x 0.80 x 0.36 m, japandi) is a different action that was not tried and answers the 'below  (fixes a:F413) |
| 21482 | 2 | swap_model | f_L-1_074 | acceptance: pin_refused: f_L-1_074: abo_B07GDSF3MR: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric mesh is below library level; the move attempts were refused (overlap / drawn_lock / max_tries), but swapping to a real model (abo_B07GDSF3MR, 0.80 x 0.80 x 0.36 m, japandi) is a different action that was not tried and answers (fixes a:F414) |
| 21483 | 2 | swap_model | f_L-1_101 | acceptance: pin_refused: f_L-1_101: abo_B07QB8DQ45: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric mesh is below library level; the rotate attempt was refused (back not on a wall), but swapping to a real model (abo_B07QB8DQ45, 1.80 x 0.41 x 0.79 m, japandi) is a different action that was not tried and answers the 'below li (fixes a:F415) |
| 21484 | 2 | swap_model | f_L-1_102 | acceptance: pin_refused: f_L-1_102: abo_B07QB8DQ45: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The parametric mesh is below library level; no swap was tried, so swapping to a real model (abo_B07QB8DQ45, 1.80 x 0.41 x 0.79 m, japandi) answers the 'below library level' cause. (fixes a:F416) |
| 21485 | 2 | swap_model | f_L1_066 | exists: no piece 'f_L1_066' in a room of the building | Argus: The fitting chose the parametric mesh for a bathroom tall_cabinet; a library model of the same footprint (0.55 x 0.37 m) is available and lifts it to the library level. (fixes a:F433) |
| 21486 | 2 | swap_model | f_L1_067 | exists: no piece 'f_L1_067' in a room of the building | Argus: Same cause as F433: the parametric mesh was chosen for the twin bathroom tall_cabinet; the same library model fits its 0.40 x 0.35 m footprint. (fixes a:F434) |
| 21488 | 2 | swap_model | f_L-1_054 | asset_unusable: 3dwh_e5f77d70d0615bd56772bf1f is not used: audit removed | Argus: The current model is a 256 px blurred-fabric texture; a higher-grade model of the same type and close size is available. (fixes a:F449) |
| 21490 | 2 | set_entrance | d_L0_005 | exists: 'd_L0_005' is no outside door of site.entrances | Argus: The visible door is a simple, unadorned panel lacking architectural interest, lighting, or surrounding landscaping. (fixes a:F454) |
| 21491 | 2 | swap_model | f_L1_066 | exists: no piece 'f_L1_066' in a room of the building | Argus: The tall_cabinet is 1.60 m high but the ceiling is only 0.82 m at that spot. The model abo_B07RMJPJMX is 1.40 m high, which is still too tall. However, among the available models, this is the shortest. The real fix is to move the cabinet to (fixes a:F528) |
| 21492 | 2 | place_group | r_L0_koridor | no_change: r_L0_koridor already has its entrance r_L0_koridor.entrance (anchor None, members f_L0_051): nothing missing, never a second set | Argus: The L0 hall (r_L0_koridor) is furnished only with a shoe_cabinet. A 7.6 m2 hall with 12 doors on the floor needs a console or coat storage to be usable. (fixes a:N88) |
| 21493 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi is already a living | Argus: The 40.5 m2 room is typed 'other' (label 'Oyun Aktivite Ve Dinlenme Odası' = play/activity/relaxation room) and is furnished as a living room (sofa, tv_unit, table_dining, bookshelf). A 40 m2 room typed 'other' is a misread: the type should (fixes a:N89) |
| 21494 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_037 is still there after the edit (bench is not a piece of a living room); 1 more kept | Argus: Twin of the above: 40.5 m2 room typed 'other' and furnished as a living room. (fixes a:N90) |
| 21495 | 2 | retype_piece | f_L1_020 | retype: console_table is no candidate for f_L1_020 (2.10 x 0.90 m at [5.65, 5.91]): the size table and the room / zone give chaise, sofa, table_dining | Argus: The L1 hall (15.3 m2) is furnished with a shoe_cabinet and a wardrobe. A shoe cabinet belongs at an entrance, not in a mid-house hall; the wardrobe is oversized for a hall. The hall's program is circulation, not storage. (fixes a:N91) |
| 21504 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Face the armchair into the seating group instead of the back of the sofa (c:F4:f_L-1_070). |
| 21505 | 2 | rotate_piece | f_L-1_072 | memory: the same edit was rejected in round 1: f_L-1_072: clearance_ok; score: plausibility 30 -> 20 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m ( | Turn armchair f_L-1_072 to face into the room (away from the back of sofa f_L-1_054), fixing F4 orientation. |
| 21506 | 2 | rotate_piece | f_L-1_102 | memory: the same edit was rejected in round 1: score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of | Turn tv_unit f_L-1_102 to face into the room (away from the back of armchair f_L-1_069), fixing F4 orientation. |
| 21508 | 2 | rotate_piece | f_L-1_101 | score: plausibility 30 -> -10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_049: armchair stands behind the back of f_L-1_101, looking at it; F4 f_L-1_053: sofa_corner stands behind the back of f_L-1_101, looking at it; F4 f_L-1_101: tv_unit faces a wall 0.02 m in front of it) | Face the TV unit into the seating area instead of the back of armchair f_L-1_071 (c:F4:f_L-1_101). |
| 21510 | 2 | move_piece | f_L1_063 | memory: the same edit was rejected in round 1: snap: f_L1_063: no free place on wall w_L1_001 (doors, windows) | TV unit back is 1.01 m off a wall; snap it to the north wall span s0 so its back rests on the wall. |
| 21512 | 2 | move_piece | f_L0_019 | score: plausibility 80 -> 60 (F3 f_L0_019: bed_double: the headboard stands in the room (0.30 m off); G5 f_L0_019: bed_double f_L0_019: 0.54 m free along the left side, needs ≥ 0.60 m) | Center the bed in the room so both the left and right sides have at least 0.60 m clearance (G5). |
| 21513 | 2 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.06 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Nudge the coffee table away from armchair f_L-1_071 to clear the 0.12 m² overlap (c:F9:f_L-1_073). |
| 21514 | 2 | move_piece | f_L1_063 | f_L1_029: no_overlap, f_L1_032: no_overlap, f_L1_063: inside_room, f_L1_063: no_overlap | TV unit back is 1.01 m off a wall; move it to the free span s0 on the north wall so its back rests on the wall. |
| 21515 | 2 | move_piece | f_L-1_073 | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | Move the coffee table further from armchair f_L-1_071 to fully clear the overlap (c:F9:f_L-1_073). |
| 21517 | 2 | move_piece | f_L0_019 | f_L0_019: no_overlap, f_L0_041: no_overlap, score: plausibility 80 -> 77 (G4 f_L0_019: bed_double f_L0_019: no nightstand on the free right side of the head (0.41 m free); G4 f_L0_041: nightstand f_L0_041 of bed_double f_L0_019: -0.12 m from the bed side (needs ≤ 0.30 m); G5 f_L0_019: bed_double f_L0_019: 0.41 m free along the right side, needs ≥ 0.60 m) | Shift the bed along the left wall to center it between the two nightstands so both sides have at least 0.60 m clearance (G5). |
| 21518 | 2 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Nudge the coffee table 0.18 m away from armchair f_L-1_071 to clear the overlap (c:F9:f_L-1_073). |
| 21519 | 2 | move_piece | f_L1_063 | snap: f_L1_063: no free place on wall w_L1_012 (doors, windows) | TV unit back is 1.01 m off a wall; snap it to the free west wall span s7 so its back rests on the wall. |
| 21520 | 2 | swap_model | f_L1_005 | acceptance: pin_refused: f_L1_005: abo_B075YMXWZC: fails the fit rules (caps, height, at most 1.79 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the dark traditional turned-leg dining table with a modern minimal oak table to match the room's minimalist aesthetic (a:F292). |
| 21522 | 2 | move_piece | f_L0_019 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 80 -> 67 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.06 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.38 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.14 m from the bed side (needs ≤ 0.30 m); G5 f_L0_019: bed_double f_L0_019: 0.38 m free along the left side, needs ≥ 0.60 m) | Shift the bed along the left wall to center it between the two nightstands so both sides have at least 0.60 m clearance (G5). |
| 21523 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 2 more kept | Re-layout the room using candidate 1 to establish a 0.60 m walkway from the door to the seating group's front use zones (c:G11:f_L-1_049, c:G11:f_L-1_053, c:G11:f_L-1_070). |
| 21524 | 2 | move_piece | f_L1_063 | max_tries: f_L1_063 was edited 3 times in this round | TV unit back is 1.01 m off a wall; snap it to the free south wall span s4 so its back rests on the wall. |
| 21525 | 2 | resize_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L- | Sofa drawn 0.90 wide x 2.13 deep is 90° against product sizes; resize to 2.13 wide x 0.90 deep to match type proportions. |
| 21526 | 2 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.29 m off)) | Sofa is 0.59 m off the wall and its front zone is blocked by a plant; move 0.59 m north to put its back on the wall and clear the front. |
| 21528 | 2 | rotate_piece | f_L1_052 | f_L1_052: clearance_ok, score: plausibility 41 -> 21 (F4 f_L1_052: armchair faces a wall 0.02 m in front of it; F4 f_L1_062: tv_unit stands behind the back of f_L1_052, looking at it; F6 f_L1_052: armchair: the free zone in front of it is reaches out of the room) | Turn the reading-corner armchair away from the back of sofa f_L1_017 so it no longer stands behind it looking at it (c:F4:f_L1_052). |
| 21530 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Individual move_piece attempts for the wardrobe and bed were rejected; a global relayout with the solver's best candidate re-places the AI pieces to clear the G13 wardrobe front and G5 bed-side clearances and add the missing right nightstand. |
| 21533 | 2 | move_piece | f_L0_019 | max_tries: f_L0_019 was edited 3 times in this round | Restore the bed to its drawn position; the G5 side clearances are geometrically impossible in this 3.02 m-wide room (both sides need 0.60 m but only 1.47 m is available between the walls), so this finding stays for review. |
| 21534 | 2 | swap_model | f_L0_029 | no_change: f_L0_029 already uses the model abo_B07JXXR83F | Styled modern writing desk (1.40 x 0.55 m, close to the drawn 1.45 x 0.60) to replace the bare desk surface flagged by D3. |
| 21536 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 2 more kept | Re-layout the room using candidate 2 to establish a 0.60 m walkway from the door to the seating group's front use zones (c:G11:f_L-1_049, c:G11:f_L-1_053, c:G11:f_L-1_070). |
| 21537 | 2 | rotate_piece | f_L1_029 | f_L1_029: clearance_ok, score: plausibility 24 -> -6 (F4 f_L1_029: armchair faces a wall 0.23 m in front of it; F6 f_L1_029: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_029: armchair f_L1_029 is 160° off the sofa f_L1_018 (needs ≤ 30°) at 2.29 m (needs ≤ 2.50 m); G11 f_L1_029: armchair f_L1_029: its front use zone is not reached by a 0.60 m walkway from door d_L1_002) | Armchair f_L1_029 stands behind the back of the TV unit looking at it; rotate it to face the TV unit (front 270°). |
| 21539 | 2 | move_piece | f_L0_042 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 80 -> 57 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.13 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.08 m from the bed side (needs ≤ 0.30 m)) | Move the nightstand up off the window sill line to unblock the window opening (G12). |
| 21540 | 2 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall to the free span s0 so its front opens into the room instead of the door swing, clearing G13. |
| 21541 | 2 | rotate_piece | f_L1_032 | f_L1_032: clearance_ok, score: plausibility 24 -> 14 (F4 f_L1_032: armchair faces a wall 0.23 m in front of it; F6 f_L1_032: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_032: armchair f_L1_032 is 142° off the sofa f_L1_018 (needs ≤ 30°) at 2.75 m (needs ≤ 2.50 m)) | Armchair f_L1_032 stands behind the back of the TV unit looking at it; rotate it to face the TV unit (front 270°). |
| 21542 | 2 | swap_model | f_L1_005 | off_style: f_L1_005: abo_B075Z9QB7N is of the styles ['industrial'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the dark traditional turned-leg dining table with a small modern industrial round table that fits the 0.78 m footprint (a:F292). |
| 21543 | 2 | move_piece | f_L0_042 | f_L0_042: inside_room | Move the nightstand down toward the window wall, away from the bed, to unblock the window opening (G12). |
| 21544 | 2 | relayout_room | r_L-1_salon | acceptance: finding G11:f_L-1_049 is still there after the edit (armchair f_L-1_049: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001); 2 more kept | Re-layout the room using candidate 3 to establish a 0.60 m walkway from the door to the seating group's front use zones (c:G11:f_L-1_049, c:G11:f_L-1_053, c:G11:f_L-1_070). |
| 21545 | 2 | rotate_piece | f_L1_052 | acceptance: finding F4:f_L1_052 is still there after the edit (armchair does not face its group (f_L1_017, f_L1_023)) | Turn the reading-corner armchair to face the room interior (away from the wall and the back of sofa f_L1_017) (c:F4:f_L1_052). |
| 21547 | 2 | rotate_piece | f_L1_029 | acceptance: finding F4:f_L1_029 is still there after the edit (armchair stands behind the back of f_L1_063, looking at it); 1 more kept | Armchair f_L1_029 is against the north wall; rotate it to face into the room (front 90°) toward the seating area instead of the TV unit's back. |
| 21548 | 2 | move_piece | f_L0_042 | score: plausibility 80 -> 64 (F3 f_L0_042: nightstand: its back is not on a wall (0.13 m off); G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: its back 0.35 m from the headboard line (needs ≤ 0.30 m)) | Move the nightstand right, away from the window, to unblock the window opening (G12) while staying beside the bed. |
| 21549 | 2 | swap_model | f_L0_029 | acceptance: pin_refused: f_L0_029: abo_B01FK3FWNG: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Styled modern desk with a built-in riser (1.14 x 0.60 m) to give the desk surface believable styling for D3. |
| 21551 | 2 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Slide the wardrobe to the far end of the south wall (offset 1.36 m) so its front opens into the room past the door swing, clearing G13. |
| 21552 | 2 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Face the armchair toward the coffee table f_L-1_087 and the seating group instead of the back of the sofa (c:F4:f_L-1_070). |
| 21553 | 2 | move_piece | f_L0_042 | max_tries: f_L0_042 was edited 3 times in this round | Restore the nightstand to its position; it is wedged against the bed's foot so it cannot be moved off the window without overlapping the bed or leaving the room, so the G12 finding stays for review. |
| 21554 | 2 | rotate_piece | f_L1_059 | acceptance: finding F4:f_L1_059 is still there after the edit (armchair stands behind the back of f_L1_063, looking at it) | Armchair f_L1_059 stands behind the back of sofa f_L1_018 looking at it; rotate it to face the seating area (front 90°). |
| 21555 | 2 | swap_model | f_L1_005 | memory: the same edit was rejected in round 2: acceptance: pin_refused: f_L1_005: abo_B075YMXWZC: fails the fit rules (caps, height, at most 1.79 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the dark traditional turned-leg dining table with a modern minimal oak table to match the room's minimalist aesthetic (a:F292). |
| 21557 | 2 | move_piece | f_L0_009 | snap: f_L0_009: no free place on wall w_L0_010 (doors, windows, at most 1.2 m from the drawn place) | Move the wardrobe to the east wall (span s1) where its front opens into the room with full clearance, clearing G13. |
| 21558 | 2 | swap_model | f_L0_029 | lower_quality: f_L0_029: abo_B07GF5DCK2 is rated 4.0 against 4.5 of the current model abo_B07JXXR83F: a swap never takes a lower-rated model; choose one rated at least 4.2, or fix the view (camera, light) instead | Styled modern desk with drawer and curved corners (1.21 x 0.53 m) to give the desk surface believable styling for D3. |
| 21560 | 2 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi.dining | memory: the same edit was rejected in round 1: no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | The dining table f_L1_005 has only 2 of 4 chairs; add the missing chairs to complete the dining group (a:N99, c:G6:f_L1_005). |
| 21561 | 2 | rotate_piece | f_L-1_101 | f_L-1_101: inside_room, f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 30 -> 10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F9 f_L-1_101: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; G1 f_L-1_101: TV unit f_L-1_101 90° off the line to the sofa, needs ≤ 10°) | Face the TV unit toward the sofa and seating area instead of the back of armchair f_L-1_071 (c:F4:f_L-1_101). |
| 21562 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Use solver candidate 1 to resolve the group layout issues: sofa f_L1_019 clearance blocked by f_L1_018, coffee table f_L1_038 not between sofa and TV, armchair f_L1_032 alignment, and dining chair count. |
| 21563 | 2 | complete_group | r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.f_L1_020 | memory: the same edit was rejected in round 1: no_place: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.f_L1_020 (missing tv_unit): no place passes the checks (seating: no place passes the checks) | The seating group around sofa f_L1_020 is missing its TV unit; add it so the sofa has a TV opposite (c:G1:f_L1_020, a:N101). |
| 21568 | 2 | move_piece | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | Slide the wardrobe to the start of the south wall (offset 0) so its front opens into the room past the door swing, clearing G13. |
| 21569 | 2 | swap_model | f_L0_029 | max_tries: f_L0_029 was edited 3 times in this round | Styled modern 4-drawer desk (1.60 x 0.73 m) to give the desk surface believable styling for D3. |
| 21574 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: G2 f_L1_038: coffee table f_L1_038 is not in front of the sofa | Use solver candidate 2 to resolve the group layout issues: sofa f_L1_019 clearance, coffee table f_L1_038 placement, armchair f_L1_032 alignment, and dining chair count. |
| 21579 | 2 | set_camera | r_L-1_koridor_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The camera is inside a proxy showing only a closed door and bare wall; re-pose to a free point showing the hall, the open door and the room beyond. |
| 21583 | 2 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | max_tries: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 was edited 3 times in this round | Use solver candidate 3 to resolve the group layout issues: sofa f_L1_019 clearance, coffee table f_L1_038 placement, armchair f_L1_032 alignment, and dining chair count. |
| 21594 | 2 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Floor-anchored compact washbasin (0.61x0.51x0.37) to clear the S1 float of +0.384 m; previous candidates failed the sloped-ceiling height cap. |
| 21595 | 2 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Floor-anchored toilet (0.40x0.71x0.72) to clear the S1 float of +0.200 m; japandi_1 was audit-removed and japandi_6 failed the height cap. |
| 21596 | 2 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating washbasin model (lowest point +0.384 m) for a floor-anchored model to clear the S1 clearance error. |
| 21597 | 2 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating toilet model (lowest point +0.200 m) for a model with a proper base to clear the S1 clearance error. |
| 21599 | 2 | swap_model | f_L0_004 | pin_refused: f_L0_004: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swapping to a model with a correct base height fixes the clearance error. |
| 21600 | 2 | swap_model | f_L0_016 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swapping to a model with a correct base height fixes the clearance error. |
| 21603 | 2 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_mediterranean_4_c5dc64de: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating washbasin model (lowest point +0.384 m) for a lower, floor-anchored model to clear the S1 clearance error. |
| 21604 | 2 | swap_model | f_L1_021 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Swap the floating toilet model (lowest point +0.200 m) for a lower model with a proper base to clear the S1 clearance error. |
| 21608 | 2 | swap_model | f_L0_004 | pin_refused: f_L0_004: gen_washbasin_japandi_1_299a0eb2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); trying another model with a correct base height. |
| 21611 | 2 | swap_model | f_L0_016 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); trying another model with a correct base height. |
| 21613 | 2 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating washbasin model (lowest point +0.384 m) for a low, floor-anchored model to clear the S1 clearance error. |
| 21614 | 2 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap the floating toilet model (lowest point +0.200 m) for a low model with a proper base to clear the S1 clearance error. |
| 21615 | 2 | swap_model | f_L0_004 | asset_unusable: gen_washbasin_mediterranean_1_93c90025 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); trying another model with a correct base height. |
| 21616 | 2 | swap_model | f_L0_016 | pin_refused: f_L0_016: gen_toilet_classic_3_293965c2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); trying another model with a correct base height. |
| 21623 | 2 | swap_model | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor (S1); trying another model with a correct base height. |
| 21624 | 2 | swap_model | f_L0_016 | max_tries: f_L0_016 was edited 3 times in this round | Current toilet model floats 0.200 m above the floor (S1); trying another model with a correct base height. |
| 22129 | 3 | retype_piece | f_L1_019 | retype: console_table is no candidate for f_L1_019 (2.10 x 0.90 m at [9.52, 5.91]): the size table and the room / zone give chaise, desk, sofa, table_dining | Argus: Twin hall with the same shoe_cabinet + wardrobe misfit. (fixes a:N92) |
| 22130 | 3 | retype_piece | f_L1_021 | retype: shower is no candidate for f_L1_021 (0.50 x 0.69 m at [6.05, 10.27]): the size table and the room / zone give floor_lamp, potted_plant, side_table, tall_cabinet, toilet, washing_machine | Argus: The L1 bathroom (5.0 m2) is furnished with a bathtub, but the documents draw a shower for this bathroom (the L0 bathrooms use shower; the L1 bathroom is the same 5.0 m2 module). A 5 m2 bathroom with a bathtub is a misread of the wet fixture (fixes a:N93) |
| 22131 | 3 | retype_piece | f_L1_022 | retype: shower is no candidate for f_L1_022 (0.50 x 0.69 m at [9.12, 10.27]): the size table and the room / zone give floor_lamp, potted_plant, side_table, tall_cabinet, toilet, washing_machine | Argus: Twin bathroom with the same bathtub-for-shower misread. (fixes a:N94) |
| 22133 | 3 | retype_piece | f_L1_023 | retype: console_table is no candidate for f_L1_023 (1.03 x 0.69 m at [5.56, 4.06]): the size table and the room / zone give armchair, ottoman, potted_plant, table_coffee, table_dining | Argus: The L1 hall has a wardrobe (15.3 m2 hall). A wardrobe does not belong in a hall; it is a bedroom/storage piece. The hall's program is circulation. (fixes a:N97) |
| 22134 | 3 | retype_piece | f_L1_024 | retype: console_table is no candidate for f_L1_024 (1.03 x 0.69 m at [9.61, 4.06]): the size table and the room / zone give armchair, desk, ottoman, potted_plant, table_coffee, table_dining | Argus: Twin hall with the same wardrobe misfit. (fixes a:N98) |
| 22136 | 3 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | no_place: dining group re-solved around the drawn table_dining f_L1_009: the solver places nothing and leaves the drawn pieces as drawn (dining: no place passes the checks) | Argus: Twin living room with the same dining-table-without-chairs misfit. (fixes a:N100) |
| 22137 | 3 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi | no_place: seating group re-solved around the drawn sofa f_L1_017: the solver places nothing and leaves the drawn pieces as drawn (seating: no candidate position fits the room) | Argus: The L1 living room (40.5 m2) has a tv_unit but no seating group (sofa + armchair + coffee table) arranged around it. The current pieces are scattered; the room needs a seating group. (fixes a:N101) |
| 22138 | 3 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | no_place: seating group re-solved around the drawn sofa f_L1_018: the solver places nothing and leaves the drawn pieces as drawn (seating: no candidate position fits the room) | Argus: Twin living room with the same seating misfit. (fixes a:N102) |
| 22139 | 3 | place_group | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding X3:r_L1_oyun_aktivite_ve_dinlenme_odasi is still there after the edit (r_L1_oyun_aktivite_ve_dinlenme_odasi (living): 5.6 m of outer wall with no window or door: a blank facade) | Argus: The L1 living room (40.5 m2) has a bookshelf and sideboard but no storage group. The room needs a storage group (wardrobe or sideboard) to be complete. (fixes a:N103) |
| 22140 | 3 | place_group | r_L-1_banyo | no_change: r_L-1_banyo already has its bathroom_set r_L-1_banyo.bathroom_set (anchor f_L-1_051, members f_L-1_026, f_L-1_056): nothing missing, never a second set | Argus: lesson (lesson:UL123:L-1): The L-1 bathrooms (banyo, banyo_2) show a floating vanity with a vessel basin and a small mirror, but no walk-in shower with glass, no rain head, no linear drain, no lit open cubbies or floor glow, and the counter (fixes a:N104) |
| 22141 | 3 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017); 3 more kept | Argus: lesson (lesson:UL153:L1): The living-dining room (r_L1_oyun_aktivite_ve_dinlenme_odasi) does not reach the P16 reference: no handle-less full-height wall panels with lit niche, no very large framed print, no plank table with fringed rug, no (fixes a:N114) |
| 22142 | 3 | retype_piece | f_L-1_057 | no_change: f_L-1_057 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_057 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_057 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_058 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_058 stays (fixes a:c7) |
| 22143 | 3 | retype_piece | f_L-1_059 | no_change: f_L-1_059 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_059 (0.59 x 0.59 m) left out as a detail (floor_lamp f_L-1_059 (0.59 x 0.59 m) is drawn 33% inside the larger floor_lamp f_L-1_060 (0.79 x 0.79 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_060 stays (fixes a:c8) |
| 22144 | 3 | retype_piece | f_L-1_064 | no_change: f_L-1_064 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_064 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_064 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_063 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_063 stays (fixes a:c9) |
| 22145 | 3 | retype_piece | f_L-1_066 | no_change: f_L-1_066 is already a floor_lamp | the plan names it: Argus: drawn piece f_L-1_066 (0.44 x 0.44 m) left out as a detail (floor_lamp f_L-1_066 (0.44 x 0.44 m) is drawn 17% inside the larger floor_lamp f_L-1_065 (0.59 x 0.59 m) of its room: one floor lamp drawn twice, not two (two floor lamps never stand in each other); f_L-1_065 stays (fixes a:c10) |
| 22146 | 3 | retype_piece | f_L-1_075 | no_change: f_L-1_075 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_075 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_070: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_023_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c11) |
| 22147 | 3 | retype_piece | f_L-1_076 | no_change: f_L-1_076 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_076 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_069: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_024_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c12) |
| 22148 | 3 | retype_piece | f_L-1_077 | no_change: f_L-1_077 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_077 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_071: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_025_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c13) |
| 22149 | 3 | retype_piece | f_L-1_078 | no_change: f_L-1_078 is already a ottoman | the plan names it: Argus: drawn piece f_L-1_078 (0.47 x 0.48 m) left out as a detail (a 0.47 x 0.48 m ottoman drawn 85% inside the armchair f_L-1_072: its seat cushion, not a piece of its own (not built); plan crop recognition/crops/sym_L-1_026_ctx.png) although an AI pass named it ottoman, which fi (fixes a:c14) |
| 22157 | 3 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.09 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Shift the coffee table 0.18 m away from armchair f_L-1_071 to clear the 0.12 m² overlap (c:F9:f_L-1_073). |
| 22160 | 3 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F4 f_L-1_102: tv_unit stands behind the back of f_L-1_069, f_L-1_072, looking at it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn armchair f_L-1_072 to face away from the back of sofa f_L-1_054, fixing the F4 orientation finding. |
| 22161 | 3 | rotate_piece | f_L-1_102 | memory: the same edit was rejected in round 1: score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of | Turn tv_unit f_L-1_102 to face away from the back of armchair f_L-1_069, fixing the F4 orientation finding. |
| 22163 | 3 | retype_piece | f_L-1b_042 | retype: sofa is no candidate for f_L-1b_042 (0.90 x 2.13 m at [4.19, 4.48]): the size table and the room / zone give chaise, stair | Confirm the drawn sofa's type so the 0.90x2.13 footprint is accepted as a rotated standard sofa, resolving the F2 size-rotation finding. |
| 22166 | 3 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.30 m) | Snap the sofa's back to the right wall (within 0.3 m) to clear F3 off-wall and open its front zone blocked by the side table. |
| 22167 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_037 is still there after the edit (bench is not a piece of a living room); 1 more kept | 40.5 m2 room is furnished as a living room (sofas, coffee tables, dining); 'other' does not fit its area and furniture. |
| 22168 | 3 | retype_piece | f_L1_019 | memory: the same edit was rejected in round 1: no_change: f_L1_019 is already a sofa | Confirm the drawn 2.10 x 0.90 m sofa type that fits its size and the living room, resolving the twin-hall misfit reading. |
| 22169 | 3 | retype_piece | f_L1_024 | memory: the same edit was rejected in round 1: acceptance: finding AI1:f_L1_024 is still there after the edit (Argus: Twin hall with the same wardrobe misfit.); a retype to the piece's own type only confirms it (status unverified -> verified, the same fitted model): nothing changes in the render, so its vision findings stay | Confirm the drawn 1.03 x 0.69 m coffee table type that fits its size and the living room, resolving the twin-hall misfit reading. |
| 22171 | 3 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Candidate 2 re-solves the sleeping group with a different partner arrangement; candidate 1 already failed on wardrobe G13 clearance. |
| 22172 | 3 | relayout_room | r_L-1_salon_2 | memory: the same edit was rejected in round 1: acceptance: finding G11:f_L-1_050 is still there after the edit (armchair f_L-1_050: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002); 2 more kept | Relayout the room using candidate 1 to improve circulation and fix the G11 walkway clearance issues for the seating group. |
| 22173 | 3 | resize_piece | f_L-1b_041 | memory: the same edit was rejected in round 1: score: plausibility -15 -> -25 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_054: armchair does not face its group (f_L-1b_041, f_L-1b_045); F4 f_L-1b_087: armchair does not face its group (f_L-1b_045, f_L-1b_041); G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the sofa f_L- | Sofa drawn 0.90 wide x 2.13 deep is 90° against product sizes; resize to 2.13 x 0.9 to align with the type's real sizes (F2). |
| 22174 | 3 | rotate_piece | f_L-1b_052 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_046)) | Turn the armchair to face the sofa and its group, resolving the F4/G3 orientation findings. |
| 22176 | 3 | move_piece | f_L-1b_045 | memory: the same edit was rejected in round 1: acceptance: finding F3:f_L-1b_045 is still there after the edit (sofa: its back is not on a wall (0.29 m off)) | Sofa back is 0.59 m off the wall; move it north so its back sits on the wall (F3). |
| 22182 | 3 | move_piece | f_L-1b_051 | score: plausibility -15 -> -45 (G3 f_L-1b_051: armchair f_L-1b_051 is 41° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.69 m (needs ≤ 2.50 m); G11 f_L-1b_052: armchair f_L-1b_052: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_073: bookshelf f_L-1b_073: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_075: armchair f_L-1b_075: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Shift the armchair 0.3 m away from f_L-1b_052 to clear the blocked front zone of both armchairs. |
| 22183 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the end chair 0.14 m away from the table so the clearance behind it reaches the required 0.81 m. |
| 22186 | 3 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.17 m free in front, needs ≥ 0.80 m); 2 more kept | Candidate 2 re-solves the sleeping group with a different arrangement than the rejected candidate 1, aiming to clear the bed side clearances (G5) and the wardrobe front clearance (G13). |
| 22189 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the end chair 0.16 m towards the table so the pull-out clearance behind it reaches the required 0.81 m. |
| 22192 | 3 | swap_model | f_L0_030 | acceptance: pin_refused: f_L0_030: abo_B07GF5DCK2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the white Shaker desk for a modern minimal white/walnut desk to match the modern minimalist bedroom (F283). |
| 22194 | 3 | rotate_piece | f_L1_052 | memory: the same edit was rejected in round 2: acceptance: finding F4:f_L1_052 is still there after the edit (armchair does not face its group (f_L1_017, f_L1_023)) | Rotate armchair to face north toward the seating group instead of standing behind the back of sofa f_L1_017 |
| 22195 | 3 | move_piece | f_L-1b_026 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift the dining table 0.15 m towards the window so the pull-out clearance behind the end chair f_L-1b_033 reaches the required 0.81 m. |
| 22196 | 3 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_modern_minimal_1_d5536003: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Modern minimal washbasin to replace the dated catalog fluted vanity (a:F252) and ground the model to the floor (c:S1:f_L-1_026). |
| 22197 | 3 | move_piece | f_L1_020 | score: plausibility 54 -> 4 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_050: bookshelf f_L1_050: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Move second sofa east to clear the free zone in front, unblocking circulation from f_L1_017 |
| 22200 | 3 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Modern minimal toilet model close to the drawn 0.5x0.69 footprint to lift the parametric build to library level (a:F411) and ground it (c:S1:f_L-1_051). |
| 22201 | 3 | move_piece | f_L1_036 | drawn_lock: f_L1_036: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 2.74 m) | Move coffee table to be centered in front of sofa f_L1_020 which faces south (270°) |
| 22203 | 3 | move_piece | f_L1_031 | drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.73 m) | Move armchair closer to coffee table f_L1_023 to reduce distance from 2.73m to under 2.50m |
| 22204 | 3 | move_piece | f_L1_007 | f_L1_005: no_overlap, f_L1_007: no_overlap | Move dining chair east to ensure 0.81m clearance from the wall behind it |
| 22206 | 3 | move_piece | f_L-1b_026 | memory: the same edit was rejected in round 3: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift the dining table 0.15 m towards the window to fix G6:f_L-1b_033: the pull-out clearance behind the end chair reaches the required 0.81 m. |
| 22208 | 3 | move_piece | f_L-1b_026 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift the dining table 0.2 m towards the window to fix G6:f_L-1b_033: the pull-out clearance behind the end chair reaches the required 0.81 m. |
| 22213 | 3 | swap_model | f_L-1_026 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Real modern minimal sink (0.965x0.5) to replace the dated catalog fluted vanity (a:F252) and ground the model to the floor (c:S1:f_L-1_026). |
| 22214 | 3 | rotate_piece | f_L1_052 | f_L1_052: inside_room | Rotate armchair to face northeast toward the seating group center, avoiding the rejected 90° and 180° angles |
| 22215 | 3 | swap_model | f_L-1_051 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Real modern minimal toilet (0.48x0.68) matching the drawn footprint to lift the parametric build to library level (a:F411) and ground it (c:S1:f_L-1_051). |
| 22216 | 3 | move_piece | f_L1_020 | score: plausibility 54 -> 4 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_050: bookshelf f_L1_050: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Move second sofa slightly east (0.3m) to clear the free zone in front blocked by f_L1_017 |
| 22217 | 3 | move_piece | f_L1_036 | score: plausibility 54 -> -26 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_020: sofa f_L1_020: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Move coffee table 0.3m toward sofa f_L1_020 to be more in front of it |
| 22219 | 3 | move_piece | f_L-1b_033 | memory: the same edit was rejected in round 3: acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the end chair 0.14 m away from the table to fix G6:f_L-1b_033: the clearance behind it reaches the required 0.81 m. |
| 22223 | 3 | move_piece | f_L-1b_033 | max_tries: f_L-1b_033 was edited 3 times in this round | Move the end chair 0.19 m away from the table to fix G6:f_L-1b_033: the clearance behind it reaches the required 0.81 m. |
| 22224 | 3 | swap_model | f_L-1_026 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Real modern minimal vanity unit & basin (0.91x0.60) to replace the dated catalog fluted vanity (a:F252) and ground the model to the floor (c:S1:f_L-1_026). |
| 22229 | 3 | swap_model | f_L-1_051 | asset_unusable: objaverse_3446229dce1f47528fa871cc7669136c is not used: audit removed | Real modern minimal toilet (0.45x0.63) matching the drawn footprint to lift the parametric build to library level (a:F411) and ground it (c:S1:f_L-1_051). |
| 22231 | 3 | set_room_type | r_L1_banyo | no_change: r_L1_banyo is already a bathroom | Confirming the room type as bathroom per the AI1 finding a:N93 which flags the wet fixture misread; the room is already a bathroom, so this confirms the context for the fixture configuration. |
| 22237 | 3 | fix_fixture | f_L1_016 | fixture_place: f_L1_016: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_005) | Door d_L1_005 swings into the washbasin on one hinge side; nudge it to the nearest valid spot to clear the swing. |
| 22255 | 3 | add_camera | cam_r_L0_merdiven_ext | building_wide: add_camera changes the whole building (roof, site, sun, materials, geometry, levels or an exterior camera); only the building session may call it, not the session of r_L0_merdiven | Exterior view from the south side of the hall (outside the room, in front of the door o_L0_001) looking north into the stair core, since every interior pose stands inside the stair volume. |
| 23055 | 4 | swap_model | f_L0_023 | asset_unusable: 3dwh_e41345920f4dce2514160e34 is not used: audit pending | Argus: The current model module:wardrobe:wardrobe_run renders as a dark flat wall panel with a window frame, not a functional wardrobe. Swapping to a proper 3.15 m wardrobe model fixes the taste failure. (fixes a:F17) |
| 23056 | 4 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: kitchen r_L-1_mutfak has no fridge; the kitchen run is incomplete. (fixes a:F134) |
| 23057 | 4 | place_group | r_L-1_mutfak_2 | no_change: r_L-1_mutfak_2 already has its kitchen_run r_L-1_mutfak_2.kitchen_run (anchor f_L-1_010, members f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068, f_L-1_096): nothing missing, never a second set | Argus: kitchen r_L-1_mutfak_2 has no fridge; the kitchen run is incomplete. (fixes a:F135) |
| 23059 | 4 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 2: no_change: r_L1_oyun_aktivite_ve_dinlenme_odasi is already a living | Argus: The room is typed 'other' while its twin is 'living' and the documents label it a living/activity room. The wrong type starves it of its program. set_room_type was tried and refused as no_change (already living) in a previous round, but the (fixes a:F155) |
| 23060 | 4 | place_group | r_L1_banyo | memory: the same edit was rejected in round 2: no_change: r_L1_banyo already has its bathroom_set r_L1_banyo.bathroom_set (anchor f_L1_021, members f_L1_015, f_L1_025): nothing missing, never a second set | Argus: The L1 bathroom lacks a tall_cabinet that its twin and every other bathroom have, and the documents draw one. place_group was tried and refused as no_change (set already present), but the set is incomplete; the fit stage must add the missin (fixes a:F156) |
| 23062 | 4 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 0.29 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No frontal view of the entrance (+y) facade exists in the camera set. (fixes a:F171) |
| 23065 | 4 | set_camera | r_L-1_koridor_2 | memory: the same edit was rejected in round 1: show: none of the 4 best poses of r_L-1_koridor_2 that show d_L-1_003 passes the camera checks: cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Argus: The camera shows a closed door and a bare wall; re-aiming it to show the door open and the furnished salon beyond will make the view meaningful. (fixes a:F183) |
| 23066 | 4 | retype_piece | f_L-1_021 | retype: tv_unit is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Argus: A 5.54 x 0.60 m drawn piece in a living room is a TV unit (low, long, against a wall); retyping it will build it and remove it from the review list. (fixes a:F191) |
| 23067 | 4 | retype_piece | f_L-1_022 | retype: tv_unit is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Argus: A 5.54 x 0.60 m drawn piece in a living room is a TV unit (low, long, against a wall); retyping it will build it and remove it from the review list. (fixes a:F192) |
| 23068 | 4 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_037 is still there after the edit (bench is not a piece of a living room); 1 more kept | Argus: This twin is typed 'other' but holds a full living program (sofa, armchairs, coffee and dining tables). The earlier set_room_type was refused only because the bench (f_L1_037) is not allowed in a living room; the bench is a misread console_ (fixes a:F196) |
| 23069 | 4 | set_front | f_L1_035 | has_front: f_L1_035 faces 270° already: rotate_piece turns it | Argus: The bench's AI front (180 deg on its short side) is a reading error; the correct front is 270 deg (its back stands on the only side on a wall). Setting the front to 270 deg fixes the reading error. (fixes a:F205) |
| 23070 | 4 | set_front | f_L1_037 | has_front: f_L1_037 faces 270° already: rotate_piece turns it | Argus: The bench's AI front (0 deg on its short side) is a reading error; the correct front is 270 deg (its back stands on the only side on a wall). Setting the front to 270 deg fixes the reading error. Note: this piece is typed console_table in t (fixes a:F206) |
| 23071 | 4 | swap_model | f_L0_015 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Argus: The toilet is built from a parametric family that looks like a crude box; a realistic library model of the same size is available. (fixes a:F241) |
| 23072 | 4 | swap_model | f_L0_047 | acceptance: pin_refused: f_L0_047: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall cabinet renders as a crude placeholder; a library model of the same footprint is available. (fixes a:F242) |
| 23074 | 4 | swap_model | f_L1_017 | pin_refused: f_L1_017: gen_sofa_japandi_2_98a7a89b: a generated model (units guessed) while a real product of the type fits within the caps (abo_B075X4F5CS): the real model stays; swap to a real model of the type or use another tool | Argus: The sofa is a crude blocky white storage-bench model out of style; a japandi library model of the same footprint is available. (fixes a:F250) |
| 23075 | 4 | swap_model | f_L-1_038 | asset_unusable: 3dwh_b27bb152311c2c1b3f509195 is not used: audit removed | Argus: The table and chair cut each other by 0.034 m (allowed 0.010 m); the previous swap was refused for fit rules, but a different model with the same length and a different width may clear the chair. (fixes a:F251) |
| 23076 | 4 | swap_model | f_L0_006 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The washbasin is a crude low-poly model; the previous swap was refused because the asset was removed, but another library model of the same footprint is available. (fixes a:F252) |
| 23079 | 4 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_025 passes the camera checks: cam_r_L0_banyo_2: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_banyo_2 would show the view cam_r_L0_banyo_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views | Argus: Same cause as F265/F266; the second camera needs the same re-aim. (fixes a:F267) |
| 23081 | 4 | set_camera | r_L0_e_banyo | memory: the same edit was rejected in round 1: show: none of the 5 best poses of r_L0_e_banyo that show f_L0_015, f_L0_006 passes the camera checks: duplicate: cam_r_L0_e_banyo_2 would show the view cam_r_L0_e_banyo_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_banyo, or remove one of the two vi | Argus: Same cause as F269; the second camera needs the same re-aim. (fixes a:F271) |
| 23100 | 4 | set_camera | r_L1_banyo | set: position is required, set: target is required | The frame is entirely black (failed render); reposition the interior camera to a free point in the bathroom at eye height so the room and its main group are visible. |
| 23101 | 4 | set_camera | r_L1_banyo | max_tries: r_L1_banyo was edited 3 times in this round | The frame is entirely black (failed render); reposition the interior camera to a free point in the bathroom at eye height so the room and its main group are visible. |

Rolled back (the refit refused them): #649 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #702 move_piece (locked check: f_L1_031: moved 0.300 m by the agent (> 0.3 m)).

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
| M14 | major | dec_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_031 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_035 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M14 | major | dec_L1_051 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M17 | minor | r_L-1_salon | r_L-1_salon | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon_2 | r_L-1_salon_2 | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M18 | major | f_L-1_020 | r_L-1_koridor | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M18 | major | f_L0_002 | r_L0_merdiven_2 | build | stair_rails | 1, 2, 3, 4 | a stair's handrails, newels, infill and strings are planned by code for the whole stair at build time (stair_rails.plan_guards: one continuous balustrade per open side with newels at its turns, stopped under the slab and beside the floor guard above, a wall handrail where a flight has none); no agent tool edits a stair, so the finding is reported to the build |
| M21 | minor | r_L0_e_banyo_2 | r_L0_e_banyo_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo | r_L1_banyo | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo_2 | r_L1_banyo_2 | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M31 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| M31 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| Q3 | major | building | - | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_salon | r_L-1_salon | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_salon_2 | r_L-1_salon_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L0_koridor | r_L0_koridor | architect | guard | 2 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L0_merdiven | r_L0_merdiven | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L0_merdiven_2 | r_L0_merdiven_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L1_koridor | r_L1_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L1_koridor_2 | r_L1_koridor_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | critical | dec_L0_011 | - | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L0_012 | - | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_029 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_030 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_031 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_035 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_051 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_049 | r_L-1_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_050 | r_L-1_salon_2 | decor | decor_rest | 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_007 | r_L0_e_yatak_odasi | decor | decor_rest | 2, 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_019 | r_L0_yatak_odasi | decor | decor_rest | 1, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_020 | r_L0_yatak_odasi_2 | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_021 | r_L0_yatak_odasi_3 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_022 | r_L0_yatak_odasi_4 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_052 | r_L0_koridor | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_053 | r_L0_koridor | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_078 | r_L1_koridor | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_093 | r_L1_koridor | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X2 | critical | dec_L1_013 | - | decor | decor_under_roof | 1, 2, 3, 4 | a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor (the edit tools act on furniture), so it is reported to the decor stage |
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
| lighting_dark | major | cam_r_L0_e_banyo_2 | r_L0_e_banyo | - | lighting_beyond_cap | 1, 2 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |
| lighting_dark | minor | cam_r_L0_koridor_1 | r_L0_koridor | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 1 | 10180 | 32768 |
| 1 | r_L-1b_salon | cut | 1 | 7221 | 32768 |
| 1 | r_L-1b_salon_2 | cut | 2 | 12572 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 5734 | 32768 |
| 2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 2 | 11135 | 32768 |
| 2 | r_L-1_salon | cut | 1 | 9615 | 32768 |
| 2 | building | cut | 2 | 17872 | 32768 |
| 3 | r_L-1b_salon | cut | 1 | 6400 | 32768 |

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
| f_L-1_028 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The single wood chair at the head of the table clashes with the other white chairs; swapping to a minimal/modern model aligns it with the set. (fixes a:F268) |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: models_it_may_take lists 3dwh_9c3a1772a72c4b00c78bd2ea as minimal/modern/scandinavian, matching the white modern sectional. (fixes a:F261) |
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
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Argus: The brown leather armchair clashes with the white sofa and black lounge chair; swapping to a minimal/modern/scandinavian model aligns it with the group. (fixes a:F261) |
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
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size 2.55 x 2.00 m -> 1.60 x 2.00 m | Qwen/Qwen3.8-27B-FP8 | Swap to a modern bed model with layered bedding (throw, cushions) to fix the D3 missing-layer and M30 missing-throw findings. |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.80 x 2.00 m | code (size_snap) | size snap: the drawn bed_double 2.55 x 2.00 m is outside its product range (width 2.55 m is 27 % outside 1.35-2 m; nearest real product 1.80 x 2.00 m); nearest real product 1.80 x 2.00 x 1.00 m (king 180 x 200) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L0_009 | piece | wardrobe | r_L0_yatak_odasi_3 | adjusted_by_ai | - | architect | wardrobe f_L0_009: 0.17 m free in front of its doors or drawers (f_L0_029 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Swap the light pine wardrobe for a dark grey modern-minimal wardrobe to match the darker headboard wood and grey walls (F285). |
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
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_038 stands in front; plan crop recognition/crops/sym_L0_012_ctx.png |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png); then: the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.01 m |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.05 m |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png) |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then Qwen/Qwen3.8-27B-FP8 (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: Shift the lower nightstand away from the bed side to clear the 0.06 m² overlap and bring its gap to the bed within the 0.30 m tolerance. |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_005 | piece | table_dining | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (anchor); moved 0.32 m |
| f_L1_006 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | solver | the drawn table_dining f_L1_005 group is re-solved on request (drawn_group): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.13 m |
| f_L1_007 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move dining chair north 0.31m to increase clearance behind it from wall |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_017 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The sofa is a blocky low-poly placeholder; the current model abo_B075X4F5CS is a real product but the judge says it looks crude. The swap to 3dwh_73a3f2fd339beec5aabd5ed6 (2.11 x 0.91 x 0.86 m, minimal/scandinavian) is a real library model  (fixes a:F248) |
| f_L1_020 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The sofa is a bare boxy model. The generated model was refused (guessed units) while a real product fits; 3dwh_73a3f2fd339beec5aabd5ed6 is a real minimal/scandinavian sofa matching the 2.10 m footprint. (fixes a:F293) |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L1_025 in the twin room r_L1_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_029 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 named it too: the twins get one type; plan crop recognition/crops/sym_L1_008_ctx.png |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_010_ctx.png |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | A bench is not a living-room piece; the 1.4 x 0.45 m low table against the wall reads as a console table (c:F1:f_L1_035, c:G14:f_L1_035). (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: the same footprint (1.09 x 0.40 m) as f_L1_038 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (mirrored centre within 0.02 m) |
| f_L1_037 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | Drawn 1.4x0.45 m wall piece; bench is not a living-room piece, console_table fits its size and the room, clearing F1/G14. (plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black mesh office chair reads as a home-office and clashes with the bed and the calm styled style. Swapping to a minimal/modern chair (3dwh_54a792101c925f12bff90916, 0.50 x 0.49 x 0.76 m) from the allowed list reconciles the set. (fixes a:F280) (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The judge names the black leather office chair as a corporate clash; the allowed list includes abo_B06W5XBL3D (0.55 x 0.53 x 0.91 m, modern), which fits the 0.50 x 0.50 m footprint and the room's style. The refused swap was abo_B081HMS8YK,  (fixes a:F282) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_040 | piece | shoe_cabinet | r_L0_koridor_2 | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_040: the piece is not built |
| f_L1_049 | piece | floor_lamp | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_049: the piece is not built |
| o_L1_001 | geometry | fix_opening_on_wall | - | corrected_by_ai, record_only | - | - | Argus: The opening o_L1_001 is not cut through wall w_L1_003, so the wall is solid where the documents show an opening. (fixes a:F161) |

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
| 3 | cam_r_L0_e_yatak_odasi_1 | ![](agent/r3_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_e_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_e_yatak_odasi_2 | ![](agent/r3_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_e_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_e_yatak_odasi_3 | ![](agent/r3_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_e_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L0_koridor_1 | ![](agent/r3_cam_r_L0_koridor_1_before.jpg) | ![](agent/r3_cam_r_L0_koridor_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_1 | ![](agent/r3_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_2 | ![](agent/r3_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L1_banyo_1 | ![](agent/r3_cam_r_L1_banyo_1_before.jpg) | ![](agent/r3_cam_r_L1_banyo_1_after.jpg) |
| 3 | cam_r_L1_koridor_1 | ![](agent/r3_cam_r_L1_koridor_1_before.jpg) | ![](agent/r3_cam_r_L1_koridor_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 3 | cam_r_L1_teras_1 | ![](agent/r3_cam_r_L1_teras_1_before.jpg) | ![](agent/r3_cam_r_L1_teras_1_after.jpg) |
| 3 | cam_r_L1_teras_2 | ![](agent/r3_cam_r_L1_teras_2_before.jpg) | ![](agent/r3_cam_r_L1_teras_2_after.jpg) |
| 3 | cam_r_L1_teras_3 | ![](agent/r3_cam_r_L1_teras_3_before.jpg) | ![](agent/r3_cam_r_L1_teras_3_after.jpg) |
| 4 | cam_r_L-1_banyo_1 | ![](agent/r4_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L-1_banyo_1_after.jpg) |
| 4 | cam_r_L-1_banyo_2 | ![](agent/r4_cam_r_L-1_banyo_2_before.jpg) | ![](agent/r4_cam_r_L-1_banyo_2_after.jpg) |
| 4 | cam_r_L-1_salon_1 | ![](agent/r4_cam_r_L-1_salon_1_before.jpg) | ![](agent/r4_cam_r_L-1_salon_1_after.jpg) |
| 4 | cam_r_L-1_salon_2 | ![](agent/r4_cam_r_L-1_salon_2_before.jpg) | ![](agent/r4_cam_r_L-1_salon_2_after.jpg) |
| 4 | cam_r_L-1_salon_3 | ![](agent/r4_cam_r_L-1_salon_3_before.jpg) | ![](agent/r4_cam_r_L-1_salon_3_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_e_banyo_1 | ![](agent/r4_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_1 | ![](agent/r4_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_1 | ![](agent/r4_cam_r_L0_yatak_odasi_3_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_2 | ![](agent/r4_cam_r_L0_yatak_odasi_3_2_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_2_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_3_3 | ![](agent/r4_cam_r_L0_yatak_odasi_3_3_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_3_3_after.jpg) |
| 4 | cam_r_L1_banyo_1 | ![](agent/r4_cam_r_L1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L1_banyo_1_after.jpg) |
| 4 | cam_r_L1_koridor_1 | ![](agent/r4_cam_r_L1_koridor_1_before.jpg) | ![](agent/r4_cam_r_L1_koridor_1_after.jpg) |
| 4 | cam_r_L1_teras_1 | ![](agent/r4_cam_r_L1_teras_1_before.jpg) | ![](agent/r4_cam_r_L1_teras_1_after.jpg) |
| 4 | cam_r_L1_teras_2 | ![](agent/r4_cam_r_L1_teras_2_before.jpg) | ![](agent/r4_cam_r_L1_teras_2_after.jpg) |
| 4 | cam_r_L1_teras_3 | ![](agent/r4_cam_r_L1_teras_3_before.jpg) | ![](agent/r4_cam_r_L1_teras_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- cam_r_L-1_koridor_2_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L1_koridor_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- final/top_L-1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L-1_plan_3.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_3.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_3.jpg
