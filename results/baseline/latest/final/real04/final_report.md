# Final report: real04

36 views: 0 polished, 36 Cycles (error 11, gate_validation 5, not_run 3, room 17). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 36 |
| interior / exterior views | 31 / 5 |
| variant | base |
| polished | 0 |
| Cycles | 36 (error 11, gate_validation 5, not_run 3, room 17) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 24 |
| needs_review views | 13 |
| unverified pieces in view (sum over views) | 52 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 13 |
| exposure | -7.67 .. +2.33 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 23 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 9, m5 5, search 22 |
| camera score (min / mean / max) | 1.85 / 3.72 / 4.81 |
| rooms by number of views | 1 with 0, 6 with 1, 2 with 2, 7 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 9.7 min / 7.6 min / 111.7 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 43.5 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 16 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real04.blend](3d/real04.blend) | 900.6 MB |
| [real04.glb](3d/real04.glb) | 1970.0 MB |

35 cameras; textures scaled to at most 1024 px (417 scaled) for the download.

## AI decor

156 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 35 rooms; 385 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

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
- drawn-piece check: 17 piece(s) moved beyond the tolerance, 71 locked-rule violation(s)
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

- r_L0_e_banyo_2: [contact_sbs_r_L0_e_banyo_2.jpg](contact_sbs_r_L0_e_banyo_2.jpg)

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
| r_L0_e_banyo_2 | cam_r_L0_e_banyo_2 | - | - | info | - | - | cycles (not_run) |
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
| r_L1_banyo | cam_r_L1_banyo_2 | - | - | info | - | - | cycles (not_run) |
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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.00 | - | agent | D3 A3 | 1 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.83 | - | search 1.85 | D1 A3 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.00 | -3 | agent | D5 A2 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.33 | -1 | search 4.50 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.17 | -3 | search 3.75 | D5 A1 | 0 | yes | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.65 | D10 A7 | 4 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.48 | D12 A7 | 3 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.64 | D8 A6 | 4 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.00 | - | agent | D2 A5 | 0 | yes | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.67 | - | search 2.15 | D1 A2 | 1 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.17 | - | agent | D2 A2 | 1 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo_2 | L0 | cycles | not_run | - | - | info | - | - | +1.67 | - | agent | D2 A4 | 1 | no | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.50 | - | search 4.51 | D7 A11 | 1 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.50 | -3 | search 4.39 | D4 A10 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.33 | - | search 3.89 | D4 A3 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.17 | - | agent | D6 A5 | 1 | yes | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.83 | -4 | agent | D4 A7 | 3 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.00 | - | search 4.02 | D4 A3 | 2 | yes | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.67 | -3 | search 4.53 | D3 A7 | 2 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +0.83 | -3 | search 4.81 | D3 A5 | 3 | no | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 4.60 | D7 A3 | 4 | yes | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.17 | -3 | search 4.67 | D4 A5 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.67 | - | search 3.59 | D3 A2 | 1 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | +1.67 | - | search 3.48 | D5 A3 | 1 | yes | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.67 | - | agent | D3 A1 | 0 | no | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -2 | agent | D10 A2 | 3 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | -0.17 | -2 | search 3.82 | D11 A1 | 3 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | -0.17 | -2 | search 3.73 | D8 A7 | 3 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.33 | 0 | search 3.20 | D3 A3 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.33 | 0 | search 2.93 | D1 A4 | 0 | no | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.17 | 0 | search 2.68 | D1 A3 | 0 | no | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.00 | 0 | m5 blocked | D7 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D7 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.67 | 0 | m5 blocked | D4 | 1 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.00 | 0 | m5 | D10 | 1 | yes | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
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
| r_L0_e_banyo | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_e_banyo_1 |
| r_L0_e_banyo_2 | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_e_banyo_2 |
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
| r_L1_banyo | bathroom | L1 | 2 | 0 | 2 | cam_r_L1_banyo_1, cam_r_L1_banyo_2 |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 1 | 0 | 1 | cam_r_L1_koridor_1 |
| r_L1_koridor_2 | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | living | L1 | 3 | 0 | 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | living | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 3 | 0 | 3 | cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 |
| r_L1_teras_2 | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1_banyo_2 (twin of r_L-1_banyo), r_L-1_koridor (twin of r_L-1_koridor_2), r_L-1_mutfak_2 (twin of r_L-1_mutfak), r_L-1_salon_2 (twin of r_L-1_salon), r_L0_banyo_2 (twin of r_L0_banyo), r_L0_e_yatak_odasi_2 (twin of r_L0_e_yatak_odasi), r_L0_koridor_2 (twin of r_L0_koridor), r_L0_merdiven_2 (twin of r_L0_merdiven), r_L0_yatak_odasi_2 (twin of r_L0_yatak_odasi), r_L0_yatak_odasi_4 (twin of r_L0_yatak_odasi_3), r_L1_banyo_2 (twin of r_L1_banyo), r_L1_koridor_2 (twin of r_L1_koridor), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (twin of r_L1_oyun_aktivite_ve_dinlenme_odasi), r_L1_teras_2 (twin of r_L1_teras).

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
- cam_r_L1_banyo_2: not_run: view not in the polish manifest
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
| cam_r_L0_e_yatak_odasi_3 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 71 % of its pixels > 0.10 m outside the drawing, 345167 px |
| cam_r_L0_koridor_1 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 10 % of its pixels > 0.10 m outside the drawing, 15458 px |
| cam_r_L0_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_005 | door | - | from_documents | deneme1.dwg INSERT:2DDF8/1,INSERT:2DDF8/0,LWPOLYLINE:2DE08 vector 0.95 | yes | 70 % of its pixels > 0.10 m outside the drawing, 113659 px |
| cam_r_L0_yatak_odasi_3_2 | cycles | cross-check misplaced | d_L0_006 | door | - | from_documents | deneme1.dwg INSERT:2DDE5/1,INSERT:2DDE5/0,LWPOLYLINE:2DE07 vector 0.95 | yes | 67 % of its pixels > 0.10 m outside the drawing, 175161 px |
| cam_r_L1_banyo_2 | cycles | cross-check misplaced | d_L1_004 | door | - | from_documents | deneme1.dwg INSERT:2F799/1,INSERT:2F799/0 vector 0.95 | yes | 47 % of its pixels > 0.10 m outside the drawing, 342441 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 63 % of its pixels > 0.10 m outside the drawing, 20303 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 62 % of its pixels > 0.10 m outside the drawing, 27900 px |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 22 % of its pixels > 0.10 m outside the drawing, 44193 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 16 % of its pixels > 0.10 m outside the drawing, 5636 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 21 % of its pixels > 0.10 m outside the drawing, 46967 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 15 % of its pixels > 0.10 m outside the drawing, 5723 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 32 % of its pixels > 0.10 m outside the drawing, 40600 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90; building.json inferred 0.70 | yes | 27 % of its pixels > 0.10 m outside the drawing, 10248 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 71 % of its pixels > 0.10 m outside the drawing, 12858 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 65 % of its pixels > 0.10 m outside the drawing, 9949 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3184 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 1857 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 7060 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 1896 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 3093 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90; building.json inferred 0.70 | yes | 48 % of its pixels > 0.10 m outside the drawing, 14600 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12212 px |

## Needs review

- cam_r_L-1_mutfak_3: json cross-check misplaced: d_L-1_003
- cam_r_L0_banyo_1: json cross-check misplaced: d_L0_007
- cam_r_L0_e_yatak_odasi_3: json cross-check misplaced: d_L0_001
- cam_r_L0_koridor_1: json cross-check misplaced: d_L0_001
- cam_r_L0_yatak_odasi_2: json cross-check misplaced: d_L0_005
- cam_r_L0_yatak_odasi_3_2: json cross-check misplaced: d_L0_006
- cam_r_L1_banyo_2: json cross-check misplaced: d_L1_004
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

- cam_r_L-1_banyo_1: f_L-1_056
- cam_r_L-1_salon_1: f_L-1_053, f_L-1_061, f_L-1_071, f_L-1_087
- cam_r_L-1_salon_2: f_L-1_053, f_L-1_071, f_L-1_073
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061, f_L-1_071, f_L-1_087
- cam_r_L0_banyo_2: f_L0_025
- cam_r_L0_e_banyo_1: f_L0_013
- cam_r_L0_e_banyo_2: f_L0_014
- cam_r_L0_e_yatak_odasi_1: f_L0_023
- cam_r_L0_e_yatak_odasi_3: f_L0_023
- cam_r_L0_koridor_1: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030
- cam_r_L0_yatak_odasi_3_1: f_L0_021, f_L0_029, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L1_banyo_1: f_L1_025
- cam_r_L1_banyo_2: f_L1_025
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_023, f_L1_035, f_L1_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_023, f_L1_035, f_L1_036
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: f_L1_023, f_L1_030, f_L1_031
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

- added f_L-1b_080: shoe_cabinet 0.60 x 0.30 (confidence -, rule)
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

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 147 ok, 17 failed; 57 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L-1_031 | chair (chair) | 0.14 | 0.00 | - | - |
| f_L-1_039 | chair (chair) | 0.13 | 0.00 | - | - |
| f_L-1_063 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_065 | floor_lamp (floor_lamp) | 0.18 | - | - | - |
| f_L-1_069 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_070 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_071 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_072 | armchair (armchair) | 0.12 | 0.00 | - | - |
| f_L-1_073 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L-1_074 | table_coffee (table_coffee) | 0.72 | 0.00 | - | - |
| f_L0_007 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_008 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_009 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_010 | wardrobe (wardrobe) | 0.72 | 0.00 | yes | - |
| f_L0_011 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_014 | shower (shower) | 0.76 | 90.00 | no | no longer against wall w_L0_002 (now centre None) |
| f_L1_032 | armchair (armchair) | 0.30 | 0.00 | - | - |

Locked-rule violations:

- walls: must stay as drawn (byte-equal): removed w_L-1b_001, w_L-1b_002, w_L-1b_003, w_L-1b_004, w_L-1b_005, w_L-1b_006, w_L-1b_007, w_L-1b_008, w_L-1b_009, w_L-1b_010, w_L-1b_011, w_L-1b_012, w_L-1b_013
- openings: must stay as drawn (byte-equal): changed d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_005, d_L0_006, d_L0_007, d_L0_008, d_L0_009, d_L0_010, d_L0_011, d_L0_012, d_L1_001, d_L1_002, d_L1_003, d_L1_004, d_L1_005, d_L1_006, win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L1_001, win_L1_002; removed d_L-1b_001, d_L-1b_002, d_L-1b_003, d_L-1b_004, o_L-1b_001, o_L-1b_002, win_L-1b_001, win_L-1b_002; added win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1
- rooms: must stay as drawn (byte-equal): changed r_L-1_koridor, r_L-1_koridor_2, r_L-1_salon, r_L-1_salon_2, r_L0_e_yatak_odasi, r_L0_e_yatak_odasi_2, r_L0_yatak_odasi, r_L0_yatak_odasi_2, r_L0_yatak_odasi_3, r_L0_yatak_odasi_4, r_L1_oyun_aktivite_ve_dinlenme_odasi, r_L1_oyun_aktivite_ve_dinlenme_odasi_2; removed r_L-1b_banyo, r_L-1b_banyo_2, r_L-1b_koridor, r_L-1b_koridor_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_salon, r_L-1b_salon_2
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
- f_L1_015: fixed equipment moved or resized (only the orientation may change)
- f_L1_016: fixed equipment moved or resized (only the orientation may change)

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
| ext_3 | corner | right, back | - | cycles (gate_validation) | partial | back: unverified | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: unverified; left: unverified | yes |
| ext_7 | aerial | - | - | cycles (gate_validation) | ok | right: unverified | yes |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_4 | corner | left, back | 12.5 m from the building corner, 30 degrees off the back facade: 82% of the view of the building is blocked by trees, the plot wall or another building; 14.5 m from the building corner, 30 degrees off the back facade: 74% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m from the building corner, 30 degrees off the back facade: 57% of the view of the building is blocked by trees, the plot wall or another building; 11.0 m from the building corner, 30 degrees off the back facade: 88% of the view of the building is blocked by trees, the plot wall or another building; 18.5 m from the building corner, 30 degrees off the back facade: 48% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m from the building corner, 30 degrees off the back facade: the building fills 7% of the frame (< 8%); 24.5 m from the building corner, 30 degrees off the back facade: 36% of the view of the building is blocked by trees, the plot wall or another building |
| ext_6 | frontal | back | 17.5 m in front of the back (entrance) facade: inside the copy; 19.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 16.0 m in front of the back (entrance) facade: inside the copy; 23.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 26.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 29.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | plaster_exterior | - | agent | no | agent override (docs/milestone11.md §17.3) |
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
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_koridor_2_1, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 36 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | 0 / 18 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

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
- door height 2,02 m: 2 opening(s) (d_L1_004, d_L1_005)
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
| area_light | 1 | r_L1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_banyo |
| area_light | 1 | r_L1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_banyo_2 |
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
| bay_lights | 2 | an LED strip at the top of every bay lights the contents so they read through the see-through front (UL135; a wardrobe LED profile with an opal diffuser, 800 lm per metre, a 120 degree beam tilted 15 degrees to the contents (UL135, UL246)) | furn_f_L0_023, furn_f_L0_024 |
| bed_front | 4 | a planting bed along the house's facade, 0.8 m deep, clear of its doors, light wells and paved strips (UL248, UL249; inferred) | landscape_bed_facade_6_1, landscape_bed_facade_6_2, landscape_bed_b2_5_1 |
| bed_path | 2 | a planting bed beside the path, 0.6 m deep, clear of its joints and the walkways (UL248, UL249; inferred) | landscape_bed_path_access_spk_001_1_l_1, landscape_bed_path_access_sp_001_1_r_1 |
| bed_planted | 1 | a bank of the terrain 2.0 m² rising 0.54 m at up to 1:2.9 (steeper than 1:4): a slope between levels, not a walking surface, never paved: a planted bank: ground cover, ornamental grasses and accent shrubs in a gravel bed (UL248, UL249; inferred) | landscape_bank_6 |
| bed_planted | 1 | a bank of the terrain 2.5 m² rising 1.37 m at up to 1:2.9 (steeper than 1:4): a slope between levels, not a walking surface, never paved: a planted bank: ground cover, ornamental grasses and accent shrubs in a gravel bed (UL248, UL249; inferred) | landscape_bank_2 |
| bed_planted | 1 | a bank of the terrain 3.5 m² rising 0.88 m at up to 1:3.2 (steeper than 1:4): a slope between levels, not a walking surface, never paved: a planted bank: ground cover, ornamental grasses and accent shrubs in a gravel bed (UL248, UL249; inferred) | landscape_bank_3 |
| bed_planted | 1 | a bank of the terrain 7.5 m² rising 2.83 m at up to 1:2.4 (steeper than 1:4): a slope between levels, not a walking surface, never paved: a planted bank: ground cover, ornamental grasses and accent shrubs in a gravel bed (UL248, UL249; inferred) | landscape_bank_1 |
| bedding | 1 | its cover is flat (relief 190 mm, 3567 vertices/m2 on top: under 6 mm or 50; 18% of the middle on the top: under 50%): poorer than our duvet; its own pillows stand at the head (bump 0.12 m, 30862 vertices): our duvet under them, no pillows of ours (never two sets, UL236); four sleeping pillows stacked in two rows (a hotel bed); a linen duvet in greige, sateen pillows in off white, sateen pillows, the throw runner in wool (1 Nov 2026, user: "bedding seem to be using the same set of pillows sheets etc, use better models better textures, more details and more variants, consider the size of the bedding") | dress_f_L0_022 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); four sleeping pillows stacked in two rows (a hotel bed); a quilted channel coverlet in light grey, linen pillows in ivory, linen pillows, the throw corner drape in chunky_knit (1 Nov 2026, user: "bedding seem to be using the same set of pillows sheets etc, use better models better textures, more details and more variants, consider the size of the bedding") | dress_f_L0_020 |
| border_band | 1 | apron_L-1_1: a 12 cm border band of slate_floor (a soldier course contrasting with its concrete) where it meets the lawn or a bed (UL248, UL249; inferred) | landscape_border_apron_L-1_1 |
| boulder | 1 | an accent boulder half buried in the planted bank bank_1 (UL248, UL249; inferred) | landscape_boulder_bank_1_1 |
| built_in | 1 | no built-in run here: neither end stands against a wall (gaps 0.73 m, 0.84 m): a built-in goes from wall to wall or from a wall, never floats mid-wall; the fit's free-standing wardrobe stays | furn_f_L0_010 |
| built_in | 1 | the house has 2 of its 2 rooms of built-in runs (r_L0_e_yatak_odasi, r_L0_e_yatak_odasi_2) and this room's unit needs 1: a free-standing wardrobe (a built-in is an option for some rooms, not every bedroom's) | furn_f_L0_012 |
| car | 1 | library car 3dwh_53630bfe2d05103a88e1a270 ('Car') on the drawn parking spk_001 (parallel bay, 4.65 x 2.10 x 1.40 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_0 |
| car | 1 | library car 3dwh_867427c8bc03ecda3fbb809a ('CAR') on the drawn parking spk_001 (perpendicular bay, 4.75 x 2.10 x 1.45 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_1 |
| car | 1 | library car 3dwh_a21d4bbd6e7b27b084152ccd ('Sports Car - Porsche') on the drawn parking spk_001 (parallel bay, 4.90 x 2.02 x 1.42 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_2 |
| center | 1 | door d_L1_005 slid -0.50 m along its wall to where the raised slope gives it 2.02 m (it had 1.00 m; UL234) | d_L1_005 |
| chimney | 1 | inferred chimney (modern family): the mirrored dwelling's own, over the twin room r_L-1_salon_2 of r_L-1_salon; top 7.00 m: 0.6 m over the roof within 3 m (its highest point there 6.21 m) and 0.9 m over where it leaves the roof (6.09 m), the 3-2-10 rule of thumb | chimney_2 |
| chimney | 1 | inferred chimney (modern family: a modern pitched-roof house keeps a fireplace or a stove in its living room); no fireplace or flue drawn; over the fireplace wall w_L-1_004 of the living room r_L-1_salon (a solid inner wall stretch of 2.8 m with no door or window); top 7.00 m: 0.6 m over the roof within 3 m (its highest point there 6.21 m) and 0.9 m over where it leaves the roof (6.09 m), the 3-2-10 rule of thumb | chimney_1 |
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
| door_size | 6 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size) | d_L-1_001, d_L-1_002, d_L0_002 |
| door_size | 2 | D5 door sizes by role and family (wet door, modern style): the nearest door set width 0.80 m (drawn 0.82 m: no product size); a standard door: 2.02 m, its head room under the sloped ceiling at its wall | d_L1_004, d_L1_005 |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade_scheme | 1 | facade scheme (modern): stone_wall_ledgestone on the basement level L-1 (not drawn) | L-1 |
| facade_scheme | 1 | facade scheme (modern): wood_cladding framing the main entrance d_L0_011 (3.0 m wide; not drawn) | w_L0_007 |
| facade_scheme | 1 | facade scheme (modern): wood_cladding on the top storey L1 over the rendered floors below (not drawn) | L1 |
| fascia_material | 1 | pitched roof: the eaves and verge edges are a fascia board in the gutter's aluminium_anthracite (not drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet) | roof |
| feature_wall | 1 | headboard panel 2.62 m wide on accent wall of r_L0_yatak_odasi: the wall behind the bed double f_L0_019 (the room's scheme limewash:warm greige: a limewash texture all round (R34)): the room's scheme limewash:warm greige: a timber headboard panel wider than the bed, a ledge on top (R32); wall panelling in 50% of 8 reference photos of the space and style | feature_wall_r_L0_yatak_odasi |
| feature_wall | 1 | headboard panel 2.62 m wide on accent wall of r_L0_yatak_odasi_2: the wall behind the bed double f_L0_020 (the room's scheme limewash:warm greige: a limewash texture all round (R34)): the room's scheme limewash:warm greige: a timber headboard panel wider than the bed, a ledge on top (R32); wall panelling in 50% of 8 reference photos of the space and style | feature_wall_r_L0_yatak_odasi_2 |
| floor | 2 | large glossy porcelain tiles: the modern family's kitchen floor (K11) | r_L-1_mutfak_floor, r_L-1_mutfak_2_floor |
| floor_pattern | 10 | assumed: the modern style lays its wood_oak_light floor in herringbone (designer value, UL106) | r_L-1_salon_floor, r_L-1_salon_2_floor, r_L0_yatak_odasi_floor |
| floor_pattern | 1 | one floor with r_L-1_salon (a doorless opening joins them): assumed: the modern style lays its wood_oak_light floor in herringbone (designer value, UL106) | r_L-1_koridor_2_floor |
| floor_pattern | 1 | one floor with r_L-1_salon_2 (a doorless opening joins them): assumed: the modern style lays its wood_oak_light floor in herringbone (designer value, UL106) | r_L-1_koridor_floor |
| garden_light | 1 | a low garden light (bollard) along path path_access_sp_001_1, every 3.5 m beside its edge (UL248, UL249; added_by_ai; inferred); library gap: a parametric bollard | landscape_light_path_access_sp_001_1_1 |
| garden_light | 1 | a low garden light (bollard) along path path_access_spk_001_1, every 3.5 m beside its edge (UL248, UL249; added_by_ai; inferred); library gap: a parametric bollard | landscape_light_path_access_spk_001_1_1 |
| garden_light | 2 | a low garden light (bollard) along path path_d_L0_011, every 3.5 m beside its edge (UL248, UL249; added_by_ai; inferred); library gap: a parametric bollard | landscape_light_path_d_L0_011_1, landscape_light_path_d_L0_011_2 |
| garden_light | 2 | a low garden light (bollard) along path path_d_L0_012, every 3.5 m beside its edge (UL248, UL249; added_by_ai; inferred); library gap: a parametric bollard | landscape_light_path_d_L0_012_1, landscape_light_path_d_L0_012_2 |
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
| height | 2 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (2.08 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8) | d_L1_004, d_L1_005 |
| height | 6 | no height in the JSON; type height for armchair | furn_f_L-1_049, furn_f_L-1_050, furn_f_L-1_069 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L0_007, furn_f_L0_008 |
| height | 2 | no height in the JSON; type height for bench | furn_f_L1_035, furn_f_L1_037 |
| height | 24 | no height in the JSON; type height for chair | furn_f_L-1_028, furn_f_L-1_029, furn_f_L-1_030 |
| height | 4 | no height in the JSON; type height for desk | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L-1_058, furn_f_L-1_060, furn_f_L-1_063 |
| height | 8 | no height in the JSON; type height for kitchen_counter | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| height | 4 | no height in the JSON; type height for nightstand | furn_f_L0_031, furn_f_L0_032, furn_f_L0_033 |
| height | 4 | no height in the JSON; type height for office_chair | furn_f_L0_035, furn_f_L0_036, furn_f_L0_037 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_013, furn_f_L0_014 |
| height | 2 | no height in the JSON; type height for sideboard | furn_f_L1_063, furn_f_L1_064 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_017, furn_f_L1_018, furn_f_L1_019 |
| height | 2 | no height in the JSON; type height for sofa_corner | furn_f_L-1_053, furn_f_L-1_054 |
| height | 4 | no height in the JSON; type height for table_coffee | furn_f_L-1_073, furn_f_L-1_074, furn_f_L-1_087 |
| height | 4 | no height in the JSON; type height for table_dining | furn_f_L-1_027, furn_f_L-1_038, furn_f_L1_005 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1_051, furn_f_L-1_052, furn_f_L0_015 |
| height | 3 | no height in the JSON; type height for tv_unit | furn_f_L-1_101, furn_f_L-1_102, furn_f_L1_062 |
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
| lawn_edge | 1 | a clean steel edge where a bed meets the lawn (175 pieces; UL248, UL249; inferred) | landscape_lawn_edges |
| leaf_state | 3 | an outside or terrace door stays closed (an open one reads as a mistake) | d_L0_012, d_L1_003, d_L1_006 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L-1_banyo_2) | d_L-1_002 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L0_banyo_2) | d_L0_008 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L0_e_banyo_2) | d_L0_003 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (left seen from r_L1_banyo); ajar at 20 deg, the widest its leaf and swing are free (its open leaf would hit f_L1_015) | d_L1_004 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L-1_banyo) | d_L-1_001 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L0_banyo) | d_L0_007 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L0_e_banyo) | d_L0_002 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L1_banyo_2); ajar at 20 deg, the widest its leaf and swing are free (its open leaf would hit f_L1_016) | d_L1_005 |
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
| library_model | 2 | library inside door hssd_200-32 ('HSSD door 200-32 (0.91 x 2.20 m)') in 1 panel(s) of 0.80 x 2.02 m (proportions off by 5 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L1_004, d_L1_005 |
| library_model | 12 | library inside door hssd_200-5 ('HSSD door 200-5 (0.81 x 2.20 m)') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_oak_light; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_001, d_L-1_002, d_L0_001 |
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
| modules | 30 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
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
| planter | 1 | a large planter at the outer corner 4 of sp_003, 0.45 m in from its edges, clear of the pool's coping and walkway, its flights and seating (UL248, UL249; added_by_ai; inferred); library gap: a parametric planter (no audited planter model made for outside) | landscape_planter_sp_003_4 |
| planter | 2 | a large planter beside the landing of entrance d_L0_011, against the facade, clear of its approach (UL248, UL249; added_by_ai; inferred); library gap: a parametric planter (no audited planter model made for outside) | landscape_planter_d_L0_011_a, landscape_planter_d_L0_011_b |
| planter | 2 | a large planter beside the landing of entrance d_L0_012, against the facade, clear of its approach (UL248, UL249; added_by_ai; inferred); library gap: a parametric planter (no audited planter model made for outside) | landscape_planter_d_L0_012_a, landscape_planter_d_L0_012_b |
| planting_coping | 1 | a bank of the terrain 13.5 m² rising 1.76 m at up to 1:0.5 (steeper than 1:4): a slope between levels, not a walking surface, never paved: terraced planting steps with low stone edging walls (steeper than the planted slope 1:2) (UL248, UL249; inferred): low edging walls in the house's base stone, a coping on each | landscape_bank_5_coping |
| planting_coping | 1 | a bank of the terrain 2.0 m² rising 1.13 m at up to 1:0.7 (steeper than 1:4): a slope between levels, not a walking surface, never paved: terraced planting steps with low stone edging walls (steeper than the planted slope 1:2) (UL248, UL249; inferred): low edging walls in the house's base stone, a coping on each | landscape_bank_4_coping |
| planting_steps | 1 | a bank of the terrain 13.5 m² rising 1.76 m at up to 1:0.5 (steeper than 1:4): a slope between levels, not a walking surface, never paved: terraced planting steps with low stone edging walls (steeper than the planted slope 1:2) (UL248, UL249; inferred) | landscape_bank_5_steps |
| planting_steps | 1 | a bank of the terrain 2.0 m² rising 1.13 m at up to 1:0.7 (steeper than 1:4): a slope between levels, not a walking surface, never paved: terraced planting steps with low stone edging walls (steeper than the planted slope 1:2) (UL248, UL249; inferred) | landscape_bank_4_steps |
| planting_walls | 1 | a bank of the terrain 13.5 m² rising 1.76 m at up to 1:0.5 (steeper than 1:4): a slope between levels, not a walking surface, never paved: terraced planting steps with low stone edging walls (steeper than the planted slope 1:2) (UL248, UL249; inferred): low edging walls in the house's base stone, a coping on each | landscape_bank_5_walls |
| planting_walls | 1 | a bank of the terrain 2.0 m² rising 1.13 m at up to 1:0.7 (steeper than 1:4): a slope between levels, not a walking surface, never paved: terraced planting steps with low stone edging walls (steeper than the planted slope 1:2) (UL248, UL249; inferred): low edging walls in the house's base stone, a coping on each | landscape_bank_4_walls |
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
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_034 on f_L0_053 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_040 on f_L0_029 beside the bed f_L0_021; moved 0.13 m down by the ray check (z 1.06 -> 0.93 m): no ray left the model decor_f_L0_029_36 at the in-shade spot, so the light sits under its closed shade or bulb; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: the decor pendant dec_L0_037 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_075 on f_L0_046 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_081 on f_L0_028 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: the decor pendant dec_L0_078 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_pendant_3_light |
| rig_light | 1 | r_L1_banyo: ceiling fixture at the pole of inaccessibility of r_L1_banyo; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_banyo_ceiling_2_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L1_banyo_2; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_036); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_040); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_015; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_050; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
| rig_light_escape | 1 | r_L0_yatak_odasi_3: the rig light of rig_r_L0_yatak_odasi_3_bedside_1 was enclosed by its host dec_L0_040 (decor_f_L0_029_36) at the in-shade spot, z 1.06 m; moved 0.13 m down to z 0.93 m, where it gets out | rig_r_L0_yatak_odasi_3_bedside_1_light |
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
| see_through | 1 | the bedroom's wardrobe run (modern style): sliding doors of wood slats in slim metal frames with its garments and an LED strip showing through, as its twin room r_L0_e_yatak_odasi (UL120, UL182; a built-in in 2 of at most 2 rooms, from the wall at one end to the middle of the wall); a top box to the ceiling (0.90 m of lidded boxes and baskets over the hanging bays); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_024 |
| see_through | 1 | the master bedroom's wardrobe run (modern style): sliding doors of wood slats in slim metal frames with its garments and an LED strip showing through, the modern family's own front (UL120, UL182; a built-in in 1 of at most 2 rooms, from the wall at one end to the middle of the wall); a top box to the ceiling (0.90 m of lidded boxes and baskets over the hanging bays); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_023 |
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
| slope:2 | 1 | the roof slope over door d_L1_004 rises 0.68 m, parallel to itself (its pitch stays; the knee wall on that side rises with it), so the drawn door gets 2.00 m of head room (it had 1.00 m); the other side of the roof stays (UL234, the user's choice: the slopes on that side rise, 2.0 m doors); the door slid -0.50 m along its wall first (the most head room within 0.5 m) | roof |
| slope:4 | 1 | the roof slope over door d_L1_004 rises 0.38 m, parallel to itself (its pitch stays; the knee wall on that side rises with it), so the drawn door gets 2.00 m of head room (it had 1.00 m); the other side of the roof stays (UL234, the user's choice: the slopes on that side rise, 2.0 m doors); the door slid -0.50 m along its wall first (the most head room within 0.5 m) | roof |
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
| suspension | 3 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L-1_049_cord, decor_dec_L0_003_cord, decor_dec_L0_060_cord |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| terrace_railing | 1 | roof terrace ro_001: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_001 |
| terrace_railing | 1 | roof terrace ro_002: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_002 |
| threshold:d_L0_011 | 1 | d_L0_011 is flush with the ground outside and the documents give no level at its landing: one step of 0.15 m up into the house (the levels' riser), its landing 0.15 m under the floor with a stone threshold at the door, the ground graded down to the landing and falling away from it 6 % (lesson UL203; inferred) | site |
| threshold:d_L0_012 | 1 | d_L0_012 is flush with the ground outside and the documents give no level at its landing: one step of 0.15 m up into the house (the levels' riser), its landing 0.15 m under the floor with a stone threshold at the door, the ground graded down to the landing and falling away from it 6 % (lesson UL203; inferred) | site |
| tree | 1 | accent of the planting, 1.0 m tall: a planting bed along the house: accent oleander (inferred; UL248, UL249) | tree_ls_bed_facade_6_2_p2 |
| tree | 1 | accent of the planting, 1.0 m tall: planted bank bank_1: accent oleander (inferred; UL248, UL249) | tree_ls_bank_1_p1 |
| tree | 1 | accent of the planting, 1.0 m tall: planted bank bank_1: accent privet_shrub (inferred; UL248, UL249) | tree_ls_bank_1_p7 |
| tree | 1 | accent of the planting, 1.0 m tall: planted bank bank_3: accent oleander (inferred; UL248, UL249) | tree_ls_bank_3_p1 |
| tree | 1 | accent of the planting, 1.0 m tall: planted bank bank_6: accent privet_shrub (inferred; UL248, UL249) | tree_ls_bank_6_p1 |
| tree | 1 | accent of the planting, 1.0 m tall: terraced planting step 2 of bank_5: accent oleander (inferred; UL248, UL249) | tree_ls_bank_5_t2_p12 |
| tree | 1 | accent of the planting, 1.0 m tall: terraced planting step 2 of bank_5: accent privet_shrub (inferred; UL248, UL249) | tree_ls_bank_5_t2_p8 |
| tree | 27 | bush of the drawn size, 0.8 m tall (height assumed) | tree_sp_001_s1e2_plant1, tree_sp_001_s1e3_plant1, tree_sp_001_s1e5_plant1 |
| tree | 2 | grass of the planting, 0.6 m tall: a planting bed along the house: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bed_facade_6_2_p3, tree_ls_bed_b2_6_1_p3 |
| tree | 2 | grass of the planting, 0.6 m tall: a planting bed beside the path: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bed_path_access_spk_001_1_l_1_p3, tree_ls_bed_path_access_sp_001_1_r_1_p1 |
| tree | 1 | grass of the planting, 0.6 m tall: planted bank bank_1: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_1_p4 |
| tree | 3 | grass of the planting, 0.6 m tall: planted bank bank_2: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_2_p3, tree_ls_bank_2_p4, tree_ls_bank_2_p5 |
| tree | 4 | grass of the planting, 0.6 m tall: planted bank bank_6: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_6_p2, tree_ls_bank_6_p3, tree_ls_bank_6_p4 |
| tree | 1 | grass of the planting, 0.6 m tall: terraced planting step 1 of bank_5: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_5_t1_p3 |
| tree | 1 | grass of the planting, 0.6 m tall: terraced planting step 2 of bank_4: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_4_t2_p1 |
| tree | 2 | grass of the planting, 0.6 m tall: terraced planting step 2 of bank_5: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_5_t2_p3, tree_ls_bank_5_t2_p4 |
| tree | 6 | grass of the planting, 0.6 m tall: terraced planting step 3 of bank_5: grass ornamental_grass (inferred; UL248, UL249) | tree_ls_bank_5_t3_p1, tree_ls_bank_5_t3_p2, tree_ls_bank_5_t3_p3 |
| tree | 6 | groundcover of the planting, 0.4 m tall: a planting bed along the house: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bed_facade_6_1_p1, tree_ls_bed_facade_6_1_p2, tree_ls_bed_facade_6_2_p1 |
| tree | 2 | groundcover of the planting, 0.4 m tall: a planting bed beside the path: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bed_path_access_spk_001_1_l_1_p1, tree_ls_bed_path_access_spk_001_1_l_1_p2 |
| tree | 5 | groundcover of the planting, 0.4 m tall: planted bank bank_1: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bank_1_p2, tree_ls_bank_1_p3, tree_ls_bank_1_p5 |
| tree | 2 | groundcover of the planting, 0.4 m tall: planted bank bank_2: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bank_2_p1, tree_ls_bank_2_p2 |
| tree | 1 | groundcover of the planting, 0.4 m tall: terraced planting step 1 of bank_4: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bank_4_t1_p1 |
| tree | 2 | groundcover of the planting, 0.4 m tall: terraced planting step 1 of bank_5: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bank_5_t1_p1, tree_ls_bank_5_t1_p2 |
| tree | 9 | groundcover of the planting, 0.4 m tall: terraced planting step 2 of bank_5: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bank_5_t2_p1, tree_ls_bank_5_t2_p2, tree_ls_bank_5_t2_p5 |
| tree | 5 | groundcover of the planting, 0.4 m tall: terraced planting step 3 of bank_5: ground cover succulent_shrub (inferred; UL248, UL249) | tree_ls_bank_5_t3_p4, tree_ls_bank_5_t3_p8, tree_ls_bank_5_t3_p9 |
| tree | 1 | potted of the planting, 0.8 m tall: the shrub in planter_d_L0_011_a: oleander (UL248, UL249; inferred) | tree_ls_planter_d_L0_011_a_plant |
| tree | 1 | potted of the planting, 0.8 m tall: the shrub in planter_d_L0_011_b: oleander (UL248, UL249; inferred) | tree_ls_planter_d_L0_011_b_plant |
| tree | 1 | potted of the planting, 0.8 m tall: the shrub in planter_d_L0_012_a: oleander (UL248, UL249; inferred) | tree_ls_planter_d_L0_012_a_plant |
| tree | 1 | potted of the planting, 0.8 m tall: the shrub in planter_d_L0_012_b: oleander (UL248, UL249; inferred) | tree_ls_planter_d_L0_012_b_plant |
| tree | 1 | potted of the planting, 0.8 m tall: the shrub in planter_sp_003_4: oleander (UL248, UL249; inferred) | tree_ls_planter_sp_003_4_plant |
| tree | 21 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| type | 1 | f_L1_025: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200); its shower model module:shower:bath_set left out (the bathtub is built as a bathtub) | furn_f_L1_025 |
| type | 1 | f_L1_026: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200); its shower model module:shower:bath_set left out (the bathtub is built as a bathtub) | furn_f_L1_026 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 1 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001, furn_f_L0_002 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 5 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L-1_019, furn_f_L-1_020 |
| under_roof | 2 | wardrobe 2.10 m high where the sloped ceiling over its footprint leaves 1.80 m: built 1.80 m high (UL128) | furn_f_L1_027, furn_f_L1_028 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.37 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| void_guard | 1 | floor opening 1 of L1 (f_L0_002 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_1 |
| waist | 4 | the house's style (modern: plate structure, glass panels under a steel handrail, steel strings (glass channel language of the house)); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_clear | 1 | over the door d_L0_011 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_112 |
| wall_clear | 2 | over the window win_arch_r_L0_yatak_odasi_3_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_103, dec_L0_104 |
| wall_clear | 2 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_133, dec_L0_134 |
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
| wall_plate | 1 | inferred: a light switch beside the door d_L1_004 into r_L1_banyo, on the latch side, assumed on the side with more free wall (0.82 m against 0.06 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_004 into r_L1_koridor, on the latch side, assumed on the side with more free wall (0.82 m against 0.06 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_005 into r_L1_banyo_2, on the latch side, assumed on the side with more free wall (0.82 m against 0.06 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_005 into r_L1_koridor_2, on the latch side, assumed on the side with more free wall (0.82 m against 0.06 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_2_02 |
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
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_033, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_037, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (left side) beside its nightstand f_L0_031, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (right side) beside its nightstand f_L0_032, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (left side) beside its nightstand f_L0_034, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (right side) beside its nightstand f_L0_033, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (left side) over its nightstand f_L0_041 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (right side) over its nightstand f_L0_042 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (left side) over its nightstand f_L0_045 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (right side) over its nightstand f_L0_044 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (left side) over its nightstand f_L0_053 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_3_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (right side) beside its desk f_L0_029, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (left side) beside its desk f_L0_028, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (right side) over its nightstand f_L0_046 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_4_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (1.55 m), 0.30 m over the floor | plate_r_L1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (1.85 m), 0.30 m over the floor | plate_r_L1_koridor_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (1.96 m), 0.30 m over the floor | plate_r_L-1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (3.26 m), 0.30 m over the floor | plate_r_L-1_koridor_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (3.63 m), 0.30 m over the floor | plate_r_L0_koridor_03, plate_r_L0_koridor_2_03 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 1.10 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_05, plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_04 |
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
| wall_plate | 1 | inferred: a power socket on the wall nearest the mirror dec_L0_025, as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_02 |
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_003 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_02 |
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_010 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_03 |
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_012 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_101 beside it, 0.30 m over the floor | plate_r_L-1_salon_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_102 beside it, 0.30 m over the floor | plate_r_L-1_salon_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L1_062 beside it, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_02 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_002 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_03 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_011 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_04 |
| wet_walls | 1 | the modern family's bathroom (FAMILY_BATH): large-format stone-look porcelain 60 x 120 cm in greige on the walls, floor to ceiling (UL114 B8; the brief names no wet-room tiles) | style |
| winders | 4 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| window_fit | 1 | fitted again to its window win_L0_001 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 2.72 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_098 |
| window_fit | 1 | fitted again to its window win_L0_001 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 3.02 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_002 |
| window_fit | 1 | fitted again to its window win_L0_004 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 2.72 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_130 |
| window_fit | 1 | fitted again to its window win_L0_004 as built: 2.62 m wide, sill 0.20 m, head 2.75 m: a 3.02 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L0_059 |
| window_fit | 1 | fitted again to its window win_L1_001 as built: 4.00 m wide, sill 0.20 m, head 1.71 m: a 4.40 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L1_004 |
| window_fit | 1 | fitted again to its window win_L1_002 as built: 4.00 m wide, sill 0.20 m, head 1.71 m: a 4.40 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L1_041 |
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

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_1640cba5fd553782ad05455c [non_commercial], 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_28b05461a14cd78d34d08afc [non_commercial], 3dwh_2b07d278d3a113582913c9a5 [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_31573d0913b5f49f79b8a0e8 [non_commercial], 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_4d053f976db6e628c7ca5635 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_52f33bb92da2aee9f4cc12bb [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_730bffda88163748fe87804f [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_826f2d90cfd567a923e3dc8c [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_93911ea73e9c2492f926d10c [non_commercial], 3dwh_a3d4e935c4ce449bf9a75f73 [non_commercial], 3dwh_b17f872496115c534b21fd29 [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_c41eadfdc01e4ec60d4e0bea [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_large_scandinavian_5_c7cc94ed [tool_nc], gen_plant_small_industrial_1_94d74431 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_industrial_3_23920a8f [tool_nc], gen_potted_plant_modern_1_8fbfec3c [tool_nc], gen_potted_plant_scandinavian_1_04f97c4b [tool_nc], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_9337b4a78dbaaecc4fb24c020d43749bbf1a710b [non_commercial], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_e91f9db75c0e3679b4bdd1d012ceb0819bb287f5 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: yes
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_1640cba5fd553782ad05455c [non_commercial], gen_potted_plant_modern_1_8fbfec3c [tool_nc], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: 3dwh_730bffda88163748fe87804f [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: yes
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: gen_potted_plant_scandinavian_1_04f97c4b [tool_nc])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_31573d0913b5f49f79b8a0e8 [non_commercial], 3dwh_4d053f976db6e628c7ca5635 [non_commercial], 3dwh_a3d4e935c4ce449bf9a75f73 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_31573d0913b5f49f79b8a0e8 [non_commercial], 3dwh_a3d4e935c4ce449bf9a75f73 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_31573d0913b5f49f79b8a0e8 [non_commercial], 3dwh_4d053f976db6e628c7ca5635 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_fd15bf26e16ebca830a04410 [non_commercial], gen_books_industrial_3_fef33ab7 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_b314e028c0b084d9d3982a8b6ea4027b6d623be8 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L0_banyo_2: commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: yes
- cam_r_L0_e_banyo_2: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_28b05461a14cd78d34d08afc [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], hssd_9337b4a78dbaaecc4fb24c020d43749bbf1a710b [non_commercial], hssd_e91f9db75c0e3679b4bdd1d012ceb0819bb287f5 [non_commercial])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_28b05461a14cd78d34d08afc [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], hssd_e91f9db75c0e3679b4bdd1d012ceb0819bb287f5 [non_commercial])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: hssd_e91f9db75c0e3679b4bdd1d012ceb0819bb287f5 [non_commercial])
- cam_r_L0_koridor_1: commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_9337b4a78dbaaecc4fb24c020d43749bbf1a710b [non_commercial])
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_730bffda88163748fe87804f [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: 3dwh_3967e9b638968e36185f0841 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_small_industrial_1_94d74431 [tool_nc], gen_potted_plant_industrial_3_23920a8f [tool_nc])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_small_industrial_1_94d74431 [tool_nc], hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_5d4653c83c5bfef7ff85d960 [non_commercial], 3dwh_f8cd3c17fe4b3f54f3c953bc [non_commercial], gen_plant_small_industrial_1_94d74431 [tool_nc], gen_potted_plant_industrial_3_23920a8f [tool_nc])
- cam_r_L1_banyo_1: commercial-safe: yes
- cam_r_L1_banyo_2: commercial-safe: yes
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: gen_plant_large_scandinavian_5_c7cc94ed [tool_nc])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_2b07d278d3a113582913c9a5 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_2b07d278d3a113582913c9a5 [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_b17f872496115c534b21fd29 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_040dd50cd138cbc316c9caec [non_commercial], 3dwh_1172843db1fb2000f7b5a16e [non_commercial], 3dwh_2b07d278d3a113582913c9a5 [non_commercial], 3dwh_52f33bb92da2aee9f4cc12bb [non_commercial], 3dwh_826f2d90cfd567a923e3dc8c [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_b17f872496115c534b21fd29 [non_commercial], 3dwh_c41eadfdc01e4ec60d4e0bea [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_a3d4e935c4ce449bf9a75f73 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_a3d4e935c4ce449bf9a75f73 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: no (flagged assets: 3dwh_8512ac158d0f8579041a1fc2 [non_commercial])
- ext_5: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_a3d4e935c4ce449bf9a75f73 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_93911ea73e9c2492f926d10c [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])

## Built below library level (Milestone 13)

69 furniture piece(s) built from a module builder or a parametric family instead of a library model: 6 library gap(s) to close with a real model, 63 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_1 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.0 degrees off the sun, sky pull k 4), ext_5 (5.6 degrees off the sun, sky pull k 0).

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

Assets: textures CC0 x 96; furniture/decor models 3DWH-UNREVIEWED x 81, CC-BY-4.0 x 131, CC-BY-NC-4.0 x 39, CC0 x 1, generated (Infinigen v1.19.0, BSD-3-Clause) x 1, generated (TRELLIS.2-4B, MIT) x 27 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 36 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Candles" by rhcreations (https://sketchfab.com/3d-models/4058a3ed739e4f9f89f49323c7db4b4c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_009, dec_L0_007)
- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_136)
- "Candles" by thegraphicsgeek (https://sketchfab.com/3d-models/92bb9f59fd9046b1beb9dca6b21489e2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_144)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_057)
- "Three candles and a golden candlestick" by Leon_dp (https://sketchfab.com/3d-models/9d46daabbefe4b4eab74d9da349dd015), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_110)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_037)
- "Доработка дно пирожницы h=23 l=75 без рёбер" by Александр (https://sketchfab.com/3d-models/e736a1e7cdcb48a5a4f2ca4100d52d28), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_022, dec_L1_056)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261101-093151-full-20261101T093628Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 50.6 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 112.7 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.5 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.7 min | answers applied |
| fit | ok | 10.4 s | - |
| layout | ok | 55.0 s | - |
| decor_ask | ok | 49.7 s | - |
| photos | reused | 0.2 s | - |
| assets | ok | 6.3 s | - |
| decor | ok | 14.2 s | - |
| agent_apply | ok | 77.8 s | - |
| refit | ok | 117.4 s | - |
| build | ok | 62.2 min | - |
| agent_previews | ok | 8.0 min | 12 view(s) |
| agent | ok | 101.2 min | 4 round(s), 28 finding(s) removed by 76 accepted edit(s) (measured; 194 predicted by the dry re-checks), 19 new, net 9, 285 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 13.6 min | - |
| controls | ok | 2.1 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.4 min | - |
| check | ok | 3.4 min | - |
| export | incomplete | 91.5 s | timeout |
| combine | ok | 29.1 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 76 edit(s) accepted, 285 rejected, 651 model calls (9109210 tokens), 110.5 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 33278): earlier runs of the appended log are left out (33277 events, 10057 model calls, 1018 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 76 / 285 (21 % accepted) |
| rejected by reason | acceptance 84, no_change 28, memory 21, max_tries 20, asset_unusable 19 |
| rooms checked by code / vision / planner | 38 / 15 / 28 |
| rooms with fixable critical or major findings visited | 28 of 28 |
| critical before -> after (after: round 4's critics, before its 5 accepted edit(s)) | 13 -> 24 |
| major before -> after (after: round 4's critics, before its 5 accepted edit(s)) | 314 -> 550 |
| agent minutes; first accepted edit after | 101.81; 32.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 21; 87; 82 (65) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 28 measured; 194 predicted (the last round's dry re-checks predicted 31 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 104 new; net -76 |
| edits removing their finding | 8 of 60 |
| plans ok / empty / refused / default | 65 / 15 / 1 / 1 |

### What the AI inspector saw on the final renders

555 vision finding(s) (86 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 18 fixed in the final round, 8 handed to the stage that owns them, 604 open; the architect leaves 0 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`.

Still open or handed on (critical and major):

- major Q12 f_L0_006: The washbasin is a bare bowl sitting on the counter with no mirror above it, which is a standard requirement for a designed bathroom vanity. (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major Q12 f_L1_025: The bathtub is missing its taps and controls, appearing as a bare white box without any way to fill it. (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- critical Q3 r_L1_koridor: The stairwell opening in the hall (koridor) has no guard rail or barrier, creating a direct fall risk to the floor below. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical Q3 r_L1_koridor_2: The second stairwell opening in the hall (koridor 2) is completely open with no railing or safety barrier. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- major D3 r_L-1_banyo: missing layer: warm light. The lighting is flat and clinical, lacking the warm, layered lighting (recessed spots, under-cabinet glow) seen i (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_banyo: missing layer: styled surfaces. The vanity counter is almost bare. While there is a bottle and a vase, the reference shows a more curated lo (open: a tool exists (swap_model) but no edit was accepted)
- major V1 r_L-1_koridor_2: bad_camera: The camera is positioned too low and too close to the corner, framing only a wall, a piece of furniture, and a sliver of the flo (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major D3 f_L-1_108: mismatched_set: The grey, open-frame shoe cabinet is a modern, almost industrial piece that clashes with the warm, classic style suggested b (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: a rug. The reference shows a large, textured rug that anchors the space. The render has two small, generic mats that look lik (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: a warm light. The reference has a prominent, stylish chandelier. The render is lit by a flat, anonymous light source, creatin (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the reference shows a styled kitchen with a kettle and accessories, while this render has completely bare co (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: a warm light (the reference has a warm, inviting glow, whereas this render is lit by flat, cold, generic light) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces (the worktops are bare except for a fruit bowl; the reference shows kettles, jars, and small appliances that  (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light (the scene is lit by flat, cool daylight; the reference has a warm, layered lighting scheme with a statement penda (open: a tool exists (swap_model) but no edit was accepted)
- major Q13 f_L-1_091: The kitchen is not designed: the long worktop run is completely bare with no wall units (upper cabinets) or tall units, making it look like  (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: wall art. The large blank wall is completely devoid of any decoration, which is a major step down from the styled reference. (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces. The worktop is empty except for a bowl of fruit; it lacks the 'lived-in' feel of small appliances, a kettle, (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light. The lighting is flat and cold, lacking the warm, inviting glow and specific fixtures (like the ring light in the  (open: a tool exists (swap_model) but no edit was accepted)
- major Q5 f_L-1_028: mismatched_set: the dining table is surrounded by at least three different chair models (a black shell chair, a black side chair, and a ligh (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_049: mismatched_set: the mid-century lounge chair with its dark leather and light wood frame clashes with the modern, low-profile white sectional (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major Q5 f_L-1_061: mismatched_set: there are three different coffee tables in the lounge area (a low rectangular one, a round one, and a small square one), whi (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_027: mismatched_set: the dining table is a pale slab on a dark monolithic base that clashes with the ten black chairs and the warm wood floor; th (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L-1_053: missing layer: feature wall: the wall behind the sofa is a flat, untextured surface; the style calls for a fluted or slatted wood panel or a (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 win_L-1_001: missing layer: layered curtains: the full-height glazing is bare; it needs a white sheer behind a heavier drape on a ceiling track to soften (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L-1_101: missing layer: styled surfaces: the TV unit and coffee tables are empty; they need a round mirror, a vase with dried grass, books, and a lea (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)

### Argus, the auditor

Score 3.2 / 100 (100 = nothing open): 29 critical, 390 major, 138 minor open. By kind (critical + major): lost 47, misread 35, taste 113, geometry 63, no_sense 48, detached 8, stale 7, other 39, process 37, silent 14, reference_missed 7, untyped 1. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- taste r_L1_banyo: Argus: Argus: Argus: Argus: Argus: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. T
- geometry f_L1_015: washbasin blocks door d_L1_004
- misread d_L1_004: door d_L1_004 swings into f_L1_015
- geometry f_L1_016: washbasin blocks door d_L1_005
- misread d_L1_005: door d_L1_005 swings into f_L1_016
- detached dec_L1_036: ceiling_light dec_L1_036: its top 0.186 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- detached dec_L1_040: ceiling_light dec_L1_040: its top 0.196 m under the ceiling over it with nothing up to it > 0.02 m (it hangs in the air: a cord or rod and a canopy must reach t
- no_sense r_L1_koridor: The stairwell opening in the hall (koridor) has no guard rail or barrier, creating a direct fall risk to the floor below.
- no_sense r_L1_koridor_2: The second stairwell opening in the hall (koridor 2) is completely open with no railing or safety barrier.
- misread f_L0_019: missing anchor: the bedroom has no bed (f_L0_019, f_L0_041, f_L0_042 and win_L0_001 are not in the render), so the room reads as a corner office, not a bedroom.
- taste w_L0_001: bad_camera: The view is severely obstructed by a car in the foreground and a large wall on the right, making it impossible to see the house's design or entrance
- misread f_L0_041: Argus: missing anchor: the nightstands (f_L0_041, f_L0_042) and the window win_L0_001 are absent, leaving a bare corner with only a desk and a wardrobe.
- misread cam_r_L1_teras_1: Argus: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- misread cam_r_L1_teras_2: Argus: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- misread cam_r_L1_teras_3: Argus: Argus: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- misread f_L1_108: Argus: Argus: The main furniture group (armchairs and side table) is missing from the balcony, leaving the room empty and without its primary function.
- taste cam_r_L1_banyo_1: Argus: Argus: Argus: Argus: Argus: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. T
- misread r_L1_teras: Argus: Argus: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- stale F7: 2 elements: the critic finds F7 on 2 element(s) (d_L1_004, d_L1_005; e.g. washbasin blocks door d_L1_004) and the architect's rule F2 / F3 says they are fine: the rule need
- lost MTEXT:2C809:0: the documents name a room 'SALON' (46 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80A:0: the documents name a room 'AÇIK MUTFAK' (8.5 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80B:0: the documents name a room 'BANYO' (4.9 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C80C:0: the documents name a room 'KORİDOR' (7 m²) on L-1b; no room of the model uses it
- lost MTEXT:2C813:0: the documents name a room 'ODA' (13 m²) on L-1b; no room of the model uses it
- lost MTEXT:2F038:0: the documents name a room 'SALON' (46 m²) on L-1b; no room of the model uses it

Library gaps reported by the agent: washbasin (Washbasin model floats 0.384 m above the floor (S1); prior swap_model attempts were rejected by fit rules or audit removal, so no audited library model fits this drawn fixture.), toilet (Toilet model floats 0.200 m above the floor (S1); prior swap_model attempts were rejected, and the fixture is locked in place and size, so no valid library model exists for it.), tall_cabinet (Tall cabinet was built with a parametric mesh below the library level (P7); prior swap_model attempts were rejected, so no suitable audited library model is available.), nightstand scandinavian (Nightstand f_L0_042 was built below the library level (parametric mesh) because every library nightstand tried (abo_B01D3C7Z4A, side_table_01, abo_B07QS8TBXT) failed the fit rules (caps, height); no audited model fits this 0.4x0.4x0.5 m slot (a:F237).), nightstand modern minimal (Multiple swap_model attempts (side_table_01, abo_B079VK52WZ, ClassicNightstand_01, abo_B0861YKM8S) all failed fit rules or style; no audited modern/minimal nightstand model fits, so the parametric mesh stays.), office_chair warm residential (No audited office_chair model in a warm residential style exists: the only non-corporate candidate (chinese_armchair, classic/japandi) is audit-pending and unusable, and every other model is a black mesh/leather corporate swivel chair that clashes with the bedroom style (a:F353).), tall_cabinet (tall_cabinet f_L0_049 built below the library level (parametric mesh); all swap_model attempts failed the fit rules (caps/height), so the library gap is recorded instead of forcing a bad swap.), washbasin (washbasin f_L0_005 model has a height offset error (+0.384 m lowest point); previous swap_model attempts failed the fit rules, so the library gap is recorded.), toilet (toilet f_L0_017 model has a height offset error (+0.200 m lowest point); previous swap_model attempts failed the fit rules or were unusable, so the library gap is recorded.), washbasin (No audited real washbasin model sits on the floor for f_L0_004 (drawn 1.0 x 0.55 m); the catalog only lists generated models, which fail the fit rules (a real product fits) or were audit-removed, so the S1 floating (+0.384 m) cannot be cleared by swap_model.), toilet (No audited real toilet model sits on the floor for f_L0_016 (drawn 0.5 x 0.68 m); the catalog only lists generated models, which fail the fit rules (a real product fits) or were audit-removed, so the S1 floating (+0.200 m) cannot be cleared by swap_model.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 13 | 314 | 106 | 18 | 26 | 109 | layout | 30 |
| 2 | 13 | 303 | 113 | 18 | 22 | 81 | layout | 35 |
| 3 | 13 | 301 | 116 | 21 | 23 | 70 | layout | 12 |
| 4 | 24 | 550 | 165 | 40 | 5 | 25 | refit | 8 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A6 | 0 | 0 | 0 | 45 |
| AI1 | 0 | 141 | 0 | 27 |
| AI2 | 0 | 8 | 0 | 0 |
| AI3 | 0 | 14 | 0 | 0 |
| AI5 | 0 | 29 | 0 | 0 |
| C7 | 0 | 72 | 0 | 0 |
| D1 | 0 | 0 | 0 | 3 |
| D2 | 0 | 7 | 0 | 0 |
| D3 | 0 | 171 | 55 | 0 |
| F1 | 0 | 0 | 8 | 0 |
| F2 | 0 | 16 | 0 | 0 |
| F3 | 0 | 10 | 4 | 0 |
| F4 | 0 | 87 | 0 | 0 |
| F6 | 0 | 39 | 0 | 0 |
| F7 | 8 | 0 | 0 | 0 |
| F9 | 0 | 37 | 0 | 0 |
| G1 | 0 | 0 | 28 | 0 |
| G10 | 0 | 76 | 0 | 0 |
| G11 | 0 | 49 | 0 | 0 |
| G13 | 0 | 20 | 0 | 0 |
| G14 | 0 | 0 | 8 | 0 |
| G2 | 0 | 18 | 8 | 0 |
| G3 | 0 | 26 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 50 | 0 | 0 |
| G6 | 0 | 22 | 8 | 0 |
| G8 | 0 | 12 | 8 | 0 |
| J1 | 0 | 49 | 0 | 20 |
| K1 | 0 | 8 | 0 | 0 |
| K3 | 0 | 4 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 24 | 0 |
| M13 | 0 | 0 | 4 | 0 |
| M15 | 0 | 0 | 4 | 0 |
| M17 | 0 | 0 | 8 | 0 |
| M21 | 0 | 0 | 33 | 0 |
| M22 | 0 | 19 | 0 | 0 |
| M23 | 0 | 0 | 8 | 0 |
| M26 | 0 | 0 | 20 | 0 |
| M28 | 0 | 4 | 8 | 0 |
| M29 | 0 | 2 | 0 | 0 |
| M30 | 0 | 0 | 3 | 0 |
| M31 | 0 | 8 | 0 | 0 |
| M33 | 0 | 29 | 8 | 0 |
| M34 | 0 | 0 | 24 | 0 |
| NR | 0 | 16 | 0 | 0 |
| P0 | 0 | 21 | 0 | 0 |
| P2 | 0 | 9 | 0 | 0 |
| P7 | 0 | 82 | 0 | 0 |
| P9 | 0 | 0 | 0 | 1 |
| Q10 | 0 | 32 | 1 | 0 |
| Q12 | 0 | 31 | 5 | 0 |
| Q13 | 0 | 3 | 0 | 0 |
| Q14 | 0 | 13 | 9 | 0 |
| Q15 | 0 | 7 | 0 | 0 |
| Q3 | 2 | 0 | 0 | 0 |
| Q4 | 31 | 7 | 1 | 0 |
| Q5 | 0 | 7 | 0 | 0 |
| Q6 | 0 | 1 | 1 | 0 |
| Q7 | 0 | 7 | 1 | 0 |
| Q9 | 0 | 4 | 0 | 0 |
| R3 | 8 | 0 | 24 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S1 | 0 | 64 | 0 | 0 |
| S2 | 0 | 20 | 33 | 0 |
| S4 | 0 | 0 | 8 | 0 |
| S5 | 8 | 0 | 50 | 0 |
| V1 | 6 | 67 | 0 | 0 |
| V2 | 0 | 0 | 0 | 1 |
| X2 | 0 | 7 | 8 | 0 |
| X3 | 0 | 6 | 0 | 0 |
| X5 | 0 | 0 | 50 | 0 |
| X6 | 0 | 16 | 0 | 0 |
| X9 | 0 | 9 | 0 | 0 |
| lighting_dark | 0 | 6 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 33778 | 1 | relayout_room | r_L0_yatak_odasi_3 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The bed is 0.37 m from the left wall, 0.23 m short; swap_model was refused (lower quality, off style, no change), so the sleeping group must be re-solved to give the bed its side clearance. (fixes a:F64) | ![](agent/r1_011_relayout_room_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_012_relayout_room_after_r_L0_yatak_odasi_3.png) |
| 33796 | 1 | move_piece | f_L0_010 | adjusted_by_ai | 70.0 -> 80.0 | Center the wardrobe on the free span s2 to open the 0.80 m front clearance (G13). | ![](agent/r1_076_move_piece_before_r_L0_yatak_odasi.png) | ![](agent/r1_081_move_piece_after_r_L0_yatak_odasi.png) |
| 33804 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 41.0 -> 41.0 | Label 'Oyun Aktivite Ve Dinlenme Odası' and drawn sofas/dining indicate a living/relaxation room, not 'other'; fixes the X3 type misread. | ![](agent/r1_087_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_101_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 33806 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | 48.0 -> 48.0 | Room has a living program (sofas, dining, reading corner) but is typed 'other'; setting to living resolves a:N174. | ![](agent/r1_089_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_097_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 33808 | 1 | rotate_piece | f_L-1b_045 | adjusted_by_ai | 18.0 -> 18.0 | The AI front 180° sits on the short side (reading error); rotate so the long side faces the open floor at 270° per the plan crop. | ![](agent/r1_091_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_105_rotate_piece_after_r_L-1b_salon_2.png) |
| 33811 | 1 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 28.0 -> 58.0 | Armchair f_L-1b_052 faces the window wall (0°) but its group (sofa f_L-1b_042, coffee table f_L-1b_071, sofa f_L-1b_046) is to its east; facing 90° aligns it with the group and clears the F4/G3 orientation findings. | ![](agent/r1_110_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r1_116_rotate_piece_after_r_L-1b_salon.png) |
| 33822 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Top solver candidate (score 16.87, 5 pieces, no hard failures) builds out the balcony planters and terrace_pair seating set, fixing the sparse/bare terrace findings. | ![](agent/r1_125_relayout_room_before_r_L1_teras.png) | ![](agent/r1_133_relayout_room_after_r_L1_teras.png) |
| 33829 | 1 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Face the armchair toward the seating group centroid (sofa f_L-1b_041 at 114°, coffee table and sofa f_L-1b_045 at 90°) to fix F4 and G3, and clear the mutual front-zone block with f_L-1b_054. | ![](agent/r1_147_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_158_rotate_piece_after_r_L-1b_salon_2.png) |
| 33846 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 provides a complete terrace_pair (2 chairs) fixing the missing member, and re-solves the group with new library models to resolve the M33 geometry defects on the current armchairs. | ![](agent/r1_160_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_167_relayout_room_after_r_L1_teras_2.png) |
| 33847 | 1 | place_group | r_L0_e_yatak_odasi_2 | added_by_ai | 77.0 -> 100.0 | Re-solve the drawn sleeping_double group around the bed anchor to complete the set and place the missing nightstand on the free right side of the head. | ![](agent/r1_163_place_group_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_169_place_group_after_r_L0_e_yatak_odasi_2.png) |
| 33848 | 1 | place_group | r_L0_e_yatak_odasi | added_by_ai | 77.0 -> 100.0 | Re-solve the drawn sleeping_double group around the bed anchor to fix the nightstand collision, negative gap and missing left nightstand. | ![](agent/r1_164_place_group_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_168_place_group_after_r_L0_e_yatak_odasi.png) |
| 33849 | 1 | move_piece | f_L1_010 | adjusted_by_ai | 48.0 -> 48.0 | Chair f_L1_010 cuts table f_L1_009 by 0.326 m; moving it 0.3 m west (away from the table, keeping its 0° facing toward the table) resolves the S2 collision. | ![](agent/r1_161_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_170_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 33852 | 1 | move_piece | f_L-1_031 | adjusted_by_ai | 30.0 -> 30.0 | Move chair f_L-1_031 slightly to reduce the cut with the dining table to within tolerance. | ![](agent/r1_165_move_piece_before_r_L-1_salon.png) | ![](agent/r1_171_move_piece_after_r_L-1_salon.png) |
| 33857 | 1 | relayout_room | r_L0_yatak_odasi_3 | adjusted_by_ai | 67.0 -> 67.0 | Try solver candidate 2 to place the missing second nightstand and improve bed side clearances. | ![](agent/r1_176_relayout_room_before_r_L0_yatak_odasi_3.png) | ![](agent/r1_184_relayout_room_after_r_L0_yatak_odasi_3.png) |
| 33861 | 1 | resize_piece | f_L0_023 | adjusted_by_ai | 100.0 -> 100.0 | Resize wardrobe height from 2.99m to standard 2.1m to fix S4 size finding (height outside 1.50-2.45m range). | ![](agent/r1_180_resize_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_186_resize_piece_after_r_L0_e_yatak_odasi.png) |
| 33869 | 1 | set_camera | r_L0_e_banyo | agent_override | - | Move the L0 en-suite bathroom camera to show the open door, shower, toilet, washbasin and tall cabinet. | - | - |
| 33870 | 1 | move_piece | f_L1_032 | adjusted_by_ai | 48.0 -> 58.0 | Armchair f_L1_032 is 2.73 m from coffee table f_L1_024 (needs ≤ 2.50 m); moving it 0.3 m NE toward the table closes the gap to fix G3. | ![](agent/r1_189_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_198_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 33872 | 1 | move_piece | f_L-1b_084 | added_by_ai | 48.0 -> 58.0 | Shift the reading-corner armchair 0.3 m away from the back of sofa f_L-1b_045 so it no longer stands behind the sofa's back (F4). | ![](agent/r1_196_move_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_202_move_piece_after_r_L-1b_salon_2.png) |
| 33874 | 1 | remove_piece | f_L1_066 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet (1.60 m) penetrates the sloped ceiling (0.82-1.52 m); removing it clears the under_roof and wrong_model findings. | ![](agent/r1_199_remove_piece_before_r_L1_banyo_2.png) | ![](agent/r1_201_remove_piece_after_r_L1_banyo_2.png) |
| 33875 | 1 | set_camera | r_L0_e_banyo_2 | agent_override | - | Move the L0 en-suite bathroom 2 camera away from the door leaf to show the vanity and room. | - | - |
| 33887 | 1 | set_lighting | r_L0_banyo | agent_override | - | Both cameras report the room too dark (exposure over the +3.00 EV cap); raising room light x1.97 covers the worst case for both views. | - | - |
| 33892 | 1 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Relayout with top-scoring candidate (9.02, circulation 0.94) to reposition the entrance group and clear a free camera point (fixes a:F251, a:F245). | ![](agent/r1_212_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r1_214_relayout_room_after_r_L-1_koridor_2.png) |
| 33897 | 1 | set_lighting | r_L-1_banyo | agent_override | - | View cam_r_L-1_banyo_1 is 0.49 stops over the EV cap; the finding names factor x1.98 on the room. | - | - |
| 33898 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | View cam_r_L0_e_banyo_1 is 0.81 stops over the EV cap; the finding names factor x2.49 on the room. | - | - |
| 33928 | 1 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | AI1: hall furnished only with a shoe_cabinet; candidate 1 (score 9.2, best balance and circulation, no hard failures) re-solves the entrance group to add the missing console/coat storage. | ![](agent/r1_237_relayout_room_before_r_L0_koridor.png) | ![](agent/r1_238_relayout_room_after_r_L0_koridor.png) |
| 33932 | 1 | relayout_room | r_L0_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Hall is under-furnished (only a shoe cabinet); solver candidate 1 (score 9.2, best balance 0.82, circulation 0.94, no hard failures) furnishes the 7.6 m² hall appropriately. | ![](agent/r1_239_relayout_room_before_r_L0_koridor_2.png) | ![](agent/r1_242_relayout_room_after_r_L0_koridor_2.png) |
| 34467 | 2 | set_camera | r_L-1_banyo | agent_override | - | Argus: The view shows only a tub rim; re-aiming to show the washbasin fixes the composition. (fixes a:F168) | - | - |
| 34468 | 2 | set_material | wet_walls | agent_override | - | Argus: The bathroom walls are bare flat tile with no accent; a styled wet-wall look fixes it. (Camera poses were already refused, so the material is the actionable cause.) (fixes a:F169) | - | - |
| 34469 | 2 | set_material | ground | agent_override | - | Argus: The outdoor setting is a flat untextured plane; setting the ground slot to a textured grass look fixes it. (fixes a:F170) | - | - |
| 34470 | 2 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace is sparsely furnished (only two plants); adding the terrace_lounge group completes it. (Camera poses were already refused, so the missing furniture is the cause.) (fixes a:F171) | ![](agent/r2_001_place_group_before_r_L1_teras.png) | ![](agent/r2_002_place_group_after_r_L1_teras.png) |
| 34472 | 2 | set_camera | r_L1_oyun_aktivite_ve_dinlenme_odasi | agent_override | - | Argus: The render crops the foreground armchair; re-aiming the camera to show the complete piece fixes the unfinished look. (fixes a:F177) | - | - |
| 34479 | 2 | set_camera | r_L1_koridor | agent_override | - | Argus: The current view is dominated by a closed door; re-aiming to show the open door into the living space fixes it. (fixes a:F190) | - | - |
| 34480 | 2 | set_material | facade | agent_override | - | Argus: The whole facade is clad in stone; the scheme requires white render over the stone base, so the facade slot is set to an exterior render look. (fixes a:F191) | - | - |
| 34481 | 2 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The render shows a closed wood door filling the frame instead of the furnished room; re-posing the camera to show the bathroom's main pieces fixes the view. (fixes a:F193) | - | - |
| 34492 | 2 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The render cuts the bed out of frame, leaving the room without an anchor; pointing the camera at the bed fixes it. (fixes a:F209) | - | - |
| 34495 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 adds a second planter to the balcony group and keeps the full terrace_pair (2 chairs + table), addressing the sparse/bare terrace findings (a:F213, a:F171, a:F342); candidate 1 was already tried. | ![](agent/r2_061_relayout_room_before_r_L1_teras.png) | ![](agent/r2_063_relayout_room_after_r_L1_teras.png) |
| 34511 | 2 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 28.0 -> 58.0 | Face armchair f_L-1b_052 towards the sofa f_L-1b_042 (90°) to fix F4/G3 orientation findings. | ![](agent/r2_086_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r2_095_rotate_piece_after_r_L-1b_salon.png) |
| 34522 | 2 | swap_model | f_L0_038 | adjusted_by_ai | 80.0 -> 80.0 | Replace the corporate black leather office chair with a modern-minimal leather-padded swivel chair that fits the calm bedroom palette (F334). | ![](agent/r2_124_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_126_swap_model_after_r_L0_yatak_odasi.png) |
| 34531 | 2 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 provides a complete terrace_pair (2 members) and complete balcony group, resolving the missing-member finding a:F214. | ![](agent/r2_141_relayout_room_before_r_L1_teras_2.png) | ![](agent/r2_146_relayout_room_after_r_L1_teras_2.png) |
| 34540 | 2 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Replace the black mesh corporate office chair with a mid-century open-back swivel chair (marble, scandinavian/minimal) that fits the warm residential bedroom style (D3). | ![](agent/r2_151_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_157_swap_model_after_r_L0_yatak_odasi_3.png) |
| 34547 | 2 | remove_piece | f_L1_065 | added_by_ai | 77.0 -> 77.0 | tall_cabinet 1.60 m high pokes through the sloped ceiling (1.47-1.52 m) at its spot; removing it clears X2 and F596 | ![](agent/r2_160_remove_piece_before_r_L1_banyo.png) | ![](agent/r2_162_remove_piece_after_r_L1_banyo.png) |
| 34560 | 2 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Relayout with candidate 2 (best circulation 0.95) to reposition the entrance group and free a clear camera point, fixing the camera-inside-proxy findings a:F251 and a:F245. | ![](agent/r2_175_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r2_178_relayout_room_after_r_L-1_koridor_2.png) |
| 34580 | 2 | report_library_gap | f_L0_003 | library_gap | - | Washbasin model floats 0.384 m above the floor (S1); prior swap_model attempts were rejected by fit rules or audit removal, so no audited library model fits this drawn fixture. | - | - |
| 34581 | 2 | report_library_gap | f_L0_018 | library_gap | - | Toilet model floats 0.200 m above the floor (S1); prior swap_model attempts were rejected, and the fixture is locked in place and size, so no valid library model exists for it. | - | - |
| 34588 | 2 | set_lighting | r_L0_e_banyo_2 | agent_override | - | Room is too dark for the camera (0.85 stops over the EV cap); the finding names a lighting factor of x2.55 on r_L0_e_banyo_2. | - | - |
| 34589 | 2 | report_library_gap | f_L0_048 | library_gap | - | Tall cabinet was built with a parametric mesh below the library level (P7); prior swap_model attempts were rejected, so no suitable audited library model is available. | - | - |
| 34593 | 2 | relayout_room | r_L0_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 1 (round 1) did not clear the under-furnished hall finding; trying the next best solver candidate to re-solve the layout. | ![](agent/r2_192_relayout_room_before_r_L0_koridor_2.png) | ![](agent/r2_194_relayout_room_after_r_L0_koridor_2.png) |
| 34594 | 2 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | AI1: hall has only a shoe_cabinet; candidate 2 re-solves the entrance group to add the missing console/coat storage. | ![](agent/r2_193_relayout_room_before_r_L0_koridor.png) | ![](agent/r2_196_relayout_room_after_r_L0_koridor.png) |
| 35142 | 3 | place_group | r_L1_teras_2 | added_by_ai | 100.0 -> 100.0 | Argus: Twin of F213 on the second unit; placing a terrace_lounge group adds the missing seating set. (fixes a:F214) | ![](agent/r3_001_place_group_before_r_L1_teras_2.png) | ![](agent/r3_002_place_group_after_r_L1_teras_2.png) |
| 35158 | 3 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Argus: Every set_camera attempt was refused because the room's furniture leaves no free point; relayouting the room frees a camera position. (fixes a:F245) | ![](agent/r3_015_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r3_016_relayout_room_after_r_L-1_koridor_2.png) |
| 35162 | 3 | set_camera | r_L-1_mutfak | agent_override | - | Argus: The camera is too close to the left wall, cutting off the fridge and stove; re-aiming it to show the fridge, counter and stove will frame the whole kitchen run. (fixes a:F322) | - | - |
| 35165 | 3 | set_camera | r_L0_koridor | agent_override | - | Argus: The camera is pressed against a wall showing only a picture frame; re-aiming it to show the shoe cabinet and main doors will present the hall properly. (fixes a:F333) | - | - |
| 35166 | 3 | swap_model | f_L0_038 | adjusted_by_ai | 80.0 -> 80.0 | Argus: The black leather office chair clashes with the warm bedroom palette; 3dwh_54a792101c925f12bff90916 is a minimal/modern chair that matches the room's style. (fixes a:F334) | ![](agent/r3_021_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r3_022_swap_model_after_r_L0_yatak_odasi.png) |
| 35167 | 3 | swap_model | f_L1_030 | adjusted_by_ai | 41.0 -> 41.0 | Argus: The armchair's model (teal, different era) clashes with the room's brown sofa set. A same-size minimal/modern/scandinavian armchair is offered; swapping the model fixes the set mismatch without moving the piece. (fixes a:F339) | ![](agent/r3_023_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_024_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 35168 | 3 | swap_model | f_L1_006 | adjusted_by_ai | 41.0 -> 41.0 | Argus: The chair's model (white spindle, cheaper style) does not go with the round pedestal table or the rest of the room. A same-size modern/scandinavian chair is offered; swapping the model fixes the set mismatch. (fixes a:F341) | ![](agent/r3_025_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_026_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 35171 | 3 | swap_model | f_L1_059 | added_by_ai | 58.0 -> 58.0 | Argus: The current model has a back/arm standing 2.4 cm from the seat (over the 5 mm tolerance), so the rests look apart from the sitting. A same-size modern/scandinavian armchair is offered; swapping the model fixes the proportion defect. The rot (fixes a:F347) | ![](agent/r3_027_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r3_028_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 35175 | 3 | report_library_gap | f_L0_042 | library_gap | - | Nightstand f_L0_042 was built below the library level (parametric mesh) because every library nightstand tried (abo_B01D3C7Z4A, side_table_01, abo_B07QS8TBXT) failed the fit rules (caps, height); no audited model fits this 0.4x0.4x0.5 m slot (a:F237). | - | - |
| 35178 | 3 | rotate_piece | f_L-1b_045 | adjusted_by_ai | 28.0 -> 28.0 | Sofa f_L-1b_045 faces along its long side into the open floor (270°), fixing the P2 reading error where the AI front 180° was on its short side. | ![](agent/r3_077_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_081_rotate_piece_after_r_L-1b_salon_2.png) |
| 35186 | 3 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 gives a 6-piece layout with a full terrace_pair and a 2-member balcony group, addressing the sparse-furnishing findings (single chair, bare terrace, no decor). | ![](agent/r3_082_relayout_room_before_r_L1_teras.png) | ![](agent/r3_089_relayout_room_after_r_L1_teras.png) |
| 35197 | 3 | report_library_gap | f_L0_044 | library_gap | - | Multiple swap_model attempts (side_table_01, abo_B079VK52WZ, ClassicNightstand_01, abo_B0861YKM8S) all failed fit rules or style; no audited modern/minimal nightstand model fits, so the parametric mesh stays. | - | - |
| 35206 | 3 | move_piece | f_L-1_039 | adjusted_by_ai | 30.0 -> 30.0 | Nudge chair f_L-1_039 away from table_dining f_L-1_038 to clear the 0.034 m cut (S2). | ![](agent/r3_101_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_104_move_piece_after_r_L-1_salon_2.png) |
| 35207 | 3 | report_library_gap | f_L0_037 | library_gap | - | No audited office_chair model in a warm residential style exists: the only non-corporate candidate (chinese_armchair, classic/japandi) is audit-pending and unusable, and every other model is a black mesh/leather corporate swivel chair that clashes with the bedroom style (a:F353). | - | - |
| 35210 | 3 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 re-solves the balcony group (2 planters) and the terrace pair (2 armchairs + 2 side tables), addressing the single-chair complaint (F214) and the missing balcony planters (F197). | ![](agent/r3_103_relayout_room_before_r_L1_teras_2.png) | ![](agent/r3_107_relayout_room_after_r_L1_teras_2.png) |
| 35250 | 3 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Relayout with untried candidate 3 to open a free camera point (fixes a:F251/a:F245 camera-inside-proxy clearance). | ![](agent/r3_129_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r3_130_relayout_room_after_r_L-1_koridor_2.png) |
| 35279 | 3 | report_library_gap | f_L0_049 | library_gap | - | tall_cabinet f_L0_049 built below the library level (parametric mesh); all swap_model attempts failed the fit rules (caps/height), so the library gap is recorded instead of forcing a bad swap. | - | - |
| 35285 | 3 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Candidates 1 and 2 were already tried; candidate 3 is the remaining solver layout to address the missing console/coat storage in the hall. | ![](agent/r3_143_relayout_room_before_r_L0_koridor.png) | ![](agent/r3_147_relayout_room_after_r_L0_koridor.png) |
| 35286 | 3 | relayout_room | r_L0_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidates 1 and 2 were already tried and the under-furnished finding persists; trying the remaining solver candidate 3 to resolve the missing member for the 7.6 m2 hall. | ![](agent/r3_144_relayout_room_before_r_L0_koridor_2.png) | ![](agent/r3_146_relayout_room_after_r_L0_koridor_2.png) |
| 35287 | 3 | report_library_gap | f_L0_005 | library_gap | - | washbasin f_L0_005 model has a height offset error (+0.384 m lowest point); previous swap_model attempts failed the fit rules, so the library gap is recorded. | - | - |
| 35288 | 3 | report_library_gap | f_L0_017 | library_gap | - | toilet f_L0_017 model has a height offset error (+0.200 m lowest point); previous swap_model attempts failed the fit rules or were unusable, so the library gap is recorded. | - | - |
| 35298 | 3 | report_library_gap | f_L0_004 | library_gap | - | No audited real washbasin model sits on the floor for f_L0_004 (drawn 1.0 x 0.55 m); the catalog only lists generated models, which fail the fit rules (a real product fits) or were audit-removed, so the S1 floating (+0.384 m) cannot be cleared by swap_model. | - | - |
| 35300 | 3 | report_library_gap | f_L0_016 | library_gap | - | No audited real toilet model sits on the floor for f_L0_016 (drawn 0.5 x 0.68 m); the catalog only lists generated models, which fail the fit rules (a real product fits) or were audit-removed, so the S1 floating (+0.200 m) cannot be cleared by swap_model. | - | - |
| 36155 | 4 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The render of the en-suite bathroom does not show the toilet, so the room reads as incomplete; re-posing the camera to include the toilet fixes the view. (fixes a:F145) | - | - |
| 36156 | 4 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The bed is cut out of the frame, leaving the bedroom without its main piece; re-posing the camera to include the bed restores the anchor. (fixes a:F146) | - | - |
| 36157 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The bathroom render omits its primary fixtures (washbasin, toilet, tall cabinet), so the room looks unfinished; re-posing the camera to include them fixes the view. (fixes a:F147) | - | - |
| 36159 | 4 | set_exterior | exterior:ground,site | agent_override | - | Argus: The flat grey outdoor environment makes the scene look like a placeholder; adding trees, a hedge and a grass ground gives the exterior depth and a finished look. (fixes a:F151) | - | - |
| 36161 | 4 | swap_model | f_L1_105 | added_by_ai | 100.0 -> 100.0 | Argus: The potted-plant/terrace pieces read as generic placeholders; swapping to a higher-detail minimal/modern model from the allowed list improves the terrace styling. (fixes a:F170) | ![](agent/r4_016_swap_model_before_r_L1_teras_2.png) | ![](agent/r4_017_swap_model_after_r_L1_teras_2.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 33760 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_042, f_L1_043 passes the camera checks: cam_r_L1_teras_1: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; duplicate: cam_r_L1_teras_1 would show the view cam_r_L1_teras_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; cam_r_L1_teras_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The terrace r_L1_teras has armchairs and a side table (f_L1_041, f_L1_042, f_L1_043) but the camera does not show them, so the render reads as an empty space. The previous set_camera attempts were refused because the poses did not pass the  (fixes a:F13) |
| 33761 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_042, f_L1_043 passes the camera checks: duplicate: cam_r_L1_teras_2 would show the view cam_r_L1_teras_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; cam_r_L1_teras_2: furniture and fixtures fill 9% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L1_teras_2: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: Same as F13: the second terrace camera also fails to show the furniture group. The previous attempts were refused for the same reason; this attempt names the pieces to show. (fixes a:F14) |
| 33762 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_042, f_L1_043 passes the camera checks: duplicate: cam_r_L1_teras_3 would show the view cam_r_L1_teras_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; duplicate: cam_r_L1_teras_3 would show the view cam_r_L1_teras_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; cam_r_L1_teras_3: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: Same as F13/F14: the third terrace camera also fails to show the furniture group. (fixes a:F15) |
| 33763 | 1 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_025 | Argus: The camera frame is entirely black and empty, so it does not show the room, its main group, or any architecture at eye height. This is a failed render, not a view of the bathroom. The fix is to re-pose the camera to a free point with headro (fixes a:F21) |
| 33764 | 1 | relayout_room | r_L-1_salon | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Argus: f_L-1_070 sits behind the back of sofa_corner f_L-1_053. All four rotate_piece attempts were refused because each new orientation broke F4 (facing a wall or the wrong group) or G3 (off-axis). The armchair and the sofa are placed as a group; (fixes a:F36) |
| 33765 | 1 | relayout_room | r_L-1_salon | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Argus: f_L-1_101 (tv_unit) is 0.47 m off the wall and behind the back of armchair f_L-1_071. rotate_piece was refused (would break F3 further), swap_model was refused (fit rules). The tv_unit and the seating it faces must be re-placed together by  (fixes a:F37) |
| 33766 | 1 | relayout_room | r_L-1_salon | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Argus: f_L-1_073 (table_coffee) overlaps f_L-1_071 (armchair) by 0.10 m². Three move_piece attempts were refused (still overlapping, or max_tries). The table and the armchair are part of the same seating group; the group's layout must be re-solved (fixes a:F39) |
| 33767 | 1 | relayout_room | r_L-1_salon | max_tries: r_L-1_salon was edited 3 times in this round | Argus: f_L-1_049 (armchair) blocks the walkway from o_L-1_001. swap_model was a no-op. The armchair is part of the seating group whose overall placement blocks the door approach; the room must be re-solved. (fixes a:F40) |
| 33768 | 1 | relayout_room | r_L-1_salon | max_tries: r_L-1_salon was edited 3 times in this round | Argus: f_L-1_053 (sofa_corner, 4.38 x 1.97 m) blocks the walkway from o_L-1_001. No single edit can fix this without moving the whole seating arrangement; the room solver must re-place the AI pieces. (fixes a:F41) |
| 33769 | 1 | relayout_room | r_L-1_salon_2 | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_069, looking at it | Argus: f_L-1_072 sits behind the back of sofa_corner f_L-1_054. rotate_piece was refused (would face a wall 0.12 m away). The twin salon's seating group must be re-solved. (fixes a:F43) |
| 33770 | 1 | relayout_room | r_L-1_salon_2 | candidate: candidate 2 does not exist: 1 usable candidate(s) | Argus: f_L-1_102 (tv_unit) is 0.47 m off the wall and behind the back of armchair f_L-1_069. rotate_piece, move_piece, and swap_model were all refused. The media axis and seating must be re-placed together. (fixes a:F44) |
| 33771 | 1 | relayout_room | r_L-1_salon_2 | candidate: candidate 3 does not exist: 1 usable candidate(s) | Argus: f_L-1_074 (table_coffee) overlaps f_L-1_069 (armchair) by 0.12 m². Three move_piece attempts and one swap_model were refused. The seating group's layout must be re-solved. (fixes a:F45) |
| 33772 | 1 | relayout_room | r_L-1_salon_2 | max_tries: r_L-1_salon_2 was edited 3 times in this round | Argus: f_L-1_050 (armchair) blocks the walkway from o_L-1_002. Part of the same seating group as F43, F44, F45; the room re-solve addresses all of them. (fixes a:F46) |
| 33773 | 1 | relayout_room | r_L-1_salon_2 | max_tries: r_L-1_salon_2 was edited 3 times in this round | Argus: f_L-1_054 (sofa_corner, 4.38 x 1.97 m) blocks the walkway from o_L-1_002. swap_model was refused (asset removed by audit). The room solver must re-place the AI pieces. (fixes a:F47) |
| 33774 | 1 | relayout_room | r_L0_yatak_odasi | no_place: r_L0_yatak_odasi relayout: no place passes the checks (no candidate position fits the room) | Argus: The bed is 0.53 m from the left wall, 0.07 m short; every move either pushes the headboard off the wall (F3) or overlaps the nightstand (F9), so the sleeping group must be re-solved. (fixes a:F59) |
| 33775 | 1 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Argus: The bed is 0.53 m from the right wall, 0.07 m short; moves were refused (headboard off wall, max_tries), so the sleeping group must be re-solved. (fixes a:F60) |
| 33776 | 1 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The drawn 1.40 x 0.60 m shower is outside the real depth range (0.70-1.20 m); fix_fixture was refused because the code saw the size as within 30% of the range, but the depth 0.60 m is below the 0.70 m minimum, so the depth is corrected to 0 (fixes a:F62) |
| 33777 | 1 | fix_fixture | f_L0_014 | fixture_size: f_L0_014: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: Same cause as F62: the drawn 1.40 x 0.60 m shower in r_L0_e_banyo_2 is outside the real depth range; the depth is corrected to 0.80 m. (fixes a:F63) |
| 33779 | 1 | swap_model | f_L-1_023 | acceptance: finding F9:f_L-1_023 is still there after the edit (wardrobe reaches 0.05 m² through the room outline, up to 0.020 m deep) | Argus: The current wardrobe model protrudes 0.020 m through the room outline. Swapping to a model with the same 2.58 x 0.60 m footprint but a different internal geometry (hssd_2e32ff526dbeb03092164450a309d084a99879cd) should resolve the minor over (fixes a:F82) |
| 33780 | 1 | retype_piece | f_L-1_057 | no_change: f_L-1_057 is already a floor_lamp | Argus: The drawn piece f_L-1_057 (0.59 x 0.59 m) is a floor lamp that was left out as a detail because it overlaps 33% with a larger floor lamp f_L-1_058. The code_fix already identifies it as a floor_lamp. Retyping it will cause it to be fitted a (fixes a:F88) |
| 33781 | 1 | retype_piece | f_L-1_059 | no_change: f_L-1_059 is already a floor_lamp | Argus: Same as F88: f_L-1_059 is a floor lamp drawn 33% inside f_L-1_060, left out as a detail. Retyping it as floor_lamp will build it. Persistent across 7 runs. (fixes a:F89) |
| 33782 | 1 | retype_piece | f_L-1_064 | no_change: f_L-1_064 is already a floor_lamp | Argus: f_L-1_064 (0.44 x 0.44 m) is a floor lamp drawn 17% inside f_L-1_063, left out as a detail. Retyping as floor_lamp will build it. Persistent across 7 runs. (fixes a:F90) |
| 33783 | 1 | retype_piece | f_L-1_066 | no_change: f_L-1_066 is already a floor_lamp | Argus: Same as F90: f_L-1_066 is a floor lamp drawn 17% inside f_L-1_065, left out as a detail. Retyping as floor_lamp will build it. Persistent across 7 runs. (fixes a:F91) |
| 33784 | 1 | retype_piece | f_L-1_075 | no_change: f_L-1_075 is already a ottoman | Argus: f_L-1_075 (0.47 x 0.48 m) is an ottoman drawn 85% inside armchair f_L-1_070, left out as a detail (seat cushion). The AI pass named it ottoman. Retyping as ottoman will build it. Persistent across 7 runs. (fixes a:F92) |
| 33785 | 1 | retype_piece | f_L-1_076 | no_change: f_L-1_076 is already a ottoman | Argus: Same as F92: f_L-1_076 is an ottoman drawn 85% inside armchair f_L-1_069, left out as a detail. Retyping as ottoman will build it. Persistent across 7 runs. (fixes a:F93) |
| 33786 | 1 | retype_piece | f_L-1_077 | no_change: f_L-1_077 is already a ottoman | Argus: Same as F92: f_L-1_077 is an ottoman drawn 85% inside armchair f_L-1_071, left out as a detail. Retyping as ottoman will build it. Persistent across 7 runs. (fixes a:F94) |
| 33787 | 1 | retype_piece | f_L-1_078 | no_change: f_L-1_078 is already a ottoman | Argus: Same as F92: f_L-1_078 is an ottoman drawn 85% inside armchair f_L-1_072, left out as a detail. Retyping as ottoman will build it. Persistent across 7 runs. (fixes a:F95) |
| 33788 | 1 | fix_fixture | f_L0_014 | no_change: f_L0_014: nothing to fix (size within the real range, inside the room and off the doors) | Argus: fix_fixture was refused only as 'no_change' (size/position within range), but the 0.10 m wall gap is a real placement error the code did not correct; snapping the back to the wall is the cause fix. (fixes a:F115) |
| 33789 | 1 | swap_model | f_L1_066 | acceptance: pin_refused: f_L1_066: abo_B07RMJPJMX: fails the fit rules (caps, height, at most 0.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall_cabinet f_L1_066 (1.60 m) stands where the sloped ceiling is only 0.82 m high; it shows through the ceiling. The model abo_B07RMJPJMX (1.40 m) is the shortest available and is the best fit, though still tall for 0.82 m clearance; t (fixes a:F156) |
| 33793 | 1 | move_piece | f_L0_012 | f_L0_012: clearance_ok, score: plausibility 70 -> 60 (F3 f_L0_012: wardrobe: its back is not on a wall (0.07 m off); G13 f_L0_012: wardrobe f_L0_012: 0.51 m free in front, needs ≥ 0.80 m) | Move wardrobe 0.14m away from the desk to increase front clearance from 0.66m to the required 0.80m. |
| 33795 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Snap wardrobe back to the north wall and shift it 0.28m along the wall away from the desk to open the 0.80m front clearance. |
| 33797 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071, f_L-1b_046)); 1 more kept | Armchair f_L-1b_052 faces the window wall (0°) but must face the seating group (sofa f_L-1b_042 / coffee table f_L-1b_071) to its west; 270° aligns it with the group and clears the G3 orientation finding. |
| 33798 | 1 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041, f_L-1b_081, f_L-1b_045)); 1 more kept | Face the armchair into the seating group (toward sofa f_L-1b_041 / coffee table f_L-1b_081) to fix F4, G3 and clear the mutual front-zone block with f_L-1b_054. |
| 33803 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Move bed 0.07m towards the left wall to increase right-side clearance to 0.60m and left-side clearance to 0.63m. |
| 33805 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 10 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_070: armchair f_L-1_070 is 90° off the table_coffee f_L-1_073 (needs ≤ 30°) at 0.48 m (needs ≤ 2.50 m)) | Turn the armchair so its front faces the room center instead of the back of the sofa, resolving the F4 orientation conflict. |
| 33807 | 1 | swap_model | f_L0_038 | off_style: f_L0_038: abo_B07M66SYGT is of the styles ['minimal', 'modern', 'scandinavian'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the black leather corporate chair with a beige twill scandinavian swivel chair that fits the calm warm bedroom palette (F334). |
| 33809 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B01D3C7Z4A: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric nightstand for a light-oak scandinavian library model to fix the below-library-level finding (F237). |
| 33810 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 54 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free left side of the head (0.97 m free); G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (2.83 m free); G4 f_L0_044: nightstand f_L0_044 of bed_double f_L0_020: its back 2.57 m from the headboard line (needs ≤ 0.30 m); its front 180° off the bed's front; G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: 0.46 m from the bed side (needs ≤ 0.30 m); its back 2.57 m from the headboard line (needs ≤ 0.30 m); its front 180° off the bed's front) | Snap the bed's headboard back onto the left wall and shift it 0.07m along the wall to open 0.60m clearance on the right side. |
| 33812 | 1 | rotate_piece | f_L-1_101 | f_L-1_101: inside_room, f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 30 -> 10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F9 f_L-1_101: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; G1 f_L-1_101: TV unit f_L-1_101 90° off the line to the sofa, needs ≤ 10°) | Turn the TV unit so its front faces the seating area instead of the back of armchair f_L-1_071, resolving the F4 orientation conflict. |
| 33813 | 1 | rotate_piece | f_L1_059 | f_L1_059: clearance_ok, score: plausibility 48 -> 28 (F4 f_L1_059: armchair faces a wall 0.02 m in front of it; F6 f_L1_059: armchair: the free zone in front of it is reaches out of the room; G11 f_L1_059: armchair f_L1_059: its front use zone is not reached by a 0.60 m walkway from door d_L1_002) | Armchair f_L1_059 faces 180° into the back of sofa f_L1_018; turning it to face 0° (toward the room) fixes the F4 orientation finding. |
| 33814 | 1 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 18 -> -2 (F4 f_L-1b_084: armchair faces a wall 0.02 m in front of it; F6 f_L-1b_084: armchair: the free zone in front of it is reaches out of the room; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | The armchair stands behind the back of sofa f_L-1b_045 looking at it; turn it to face into the room (90°) toward its reading-corner group. |
| 33817 | 1 | swap_model | f_L0_044 | acceptance: pin_refused: f_L0_044: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap parametric nightstand for a library model to resolve the below_library finding. |
| 33818 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 12° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)); 3 more kept | Fixes the seating group issues: armchair f_L1_052 behind sofa, f_L1_031 misaligned with coffee table, f_L1_036 not in front of sofa f_L1_020, and f_L1_020's blocked front zone. |
| 33819 | 1 | swap_model | f_L0_038 | acceptance: pin_refused: f_L0_038: hssd_d6f9b4561838f68f34d3fc36a7b700bc2c180253: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the black leather corporate chair with a minimal aluminium-frame task chair that fits the project's modern/minimal chain and the calm bedroom palette (F334). |
| 33823 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge the head chair 3 cm away from the table to open the 0.78 m clearance behind it to the required 0.81 m (G6). |
| 33825 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric nightstand for the scandinavian Side Table 01 library model (0.55 x 0.45 x 0.55 m) that fits the 0.40 m footprint and height cap (F237). |
| 33826 | 1 | swap_model | f_L0_044 | acceptance: pin_refused: f_L0_044: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap parametric nightstand for a real library model (40x36cm, height 47cm) to resolve the below_library finding. |
| 33828 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 12° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)); 3 more kept | Second solver candidate to clear the seating group findings (G3 f_L1_031, G2 f_L1_036, F6 f_L1_020, F4 f_L1_052) that candidate 1 left. |
| 33833 | 1 | swap_model | f_L0_044 | off_style: f_L0_044: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Swap parametric nightstand for a real library model (57x42cm, height 70cm) to resolve the below_library finding. |
| 33834 | 1 | swap_model | f_L0_038 | asset_unusable: chinese_armchair is not used: audit pending | Replace the black leather corporate chair with the japandi/minimal Chinese Armchair, which fits the project's modern/minimal chain and the calm warm bedroom palette (F334). |
| 33839 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | max_tries: r_L1_oyun_aktivite_ve_dinlenme_odasi was edited 3 times in this round | Third solver candidate to clear the seating group findings (G3 f_L1_031, G2 f_L1_036, F6 f_L1_020, F4 f_L1_052) that candidates 1-2 left. |
| 33840 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge the head chair 9 cm away from the table to open the 0.78 m clearance behind it to the required 0.81 m (G6). |
| 33850 | 1 | complete_group | r_L0_yatak_odasi_3.sleeping_double | no_place: r_L0_yatak_odasi_3.sleeping_double (missing nightstand): no place passes the checks (sleeping_double: no place passes the checks) | Add the missing second nightstand to complete the sleeping set (AI1/G4). |
| 33853 | 1 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 48 -> 38 (F4 f_L-1b_084: armchair faces a wall 0.02 m in front of it; F6 f_L-1b_084: armchair: the free zone in front of it is reaches out of the room) | Turn the reading-corner armchair away from the back of sofa f_L-1b_045 to face the open floor (180°) so it no longer looks at the sofa's back. |
| 33854 | 1 | set_camera | r_L1_teras | show: no free camera point of r_L1_teras shows f_L1_108, f_L1_109, f_L1_110 (f_L1_108, f_L1_109, f_L1_110 not in r_L1_teras: name its pieces, doors or windows) | Reposition the L1 terrace camera to a free point that frames the armchair/side-table group and the outdoor setting without cutting the foreground chair. |
| 33855 | 1 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_015, f_L1_021 | The L1 bathroom render is entirely black; move the camera to a valid interior point with headroom that shows the tub, washbasin and room. |
| 33856 | 1 | set_camera | r_L-1_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Move the L-1 bathroom camera away from the corner so the washbasin, tub and room layout are all in frame. |
| 33858 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show f_L-1_094 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Move the L-1 hall camera to a free point showing the hall, its doors and the cabinet, not a closed door and bare wall. |
| 33860 | 1 | set_camera | r_L-1_mutfak | show: none of the 8 best poses of r_L-1_mutfak that show f_L-1_008 passes the camera checks: duplicate: cam_r_L-1_mutfak_3 would show the view cam_r_L-1_mutfak_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_mutfak, or remove one of the two views; duplicate: cam_r_L-1_mutfak_3 would show the view cam_r_L-1_mutfak_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L-1_mutfak, or remove one of the two views | Reposition the L-1 kitchen camera to show the full kitchen run, upper storage and worktop. |
| 33863 | 1 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_025, f_L0_018, f_L0_003, f_L0_048 passes the camera checks: cam_r_L0_banyo_1: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_banyo_1 would show the view cam_r_L0_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views | Move the L0 bathroom camera away from the door frame/vanity to show the tub, toilet, washbasin and cabinet. |
| 33864 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Nudge the head chair 4 cm away from the table (within its 0.3 m allowance) to open the 0.78 m clearance behind it to the required 0.81 m (G6). |
| 33865 | 1 | complete_group | r_L0_yatak_odasi_4.sleeping_double | no_place: r_L0_yatak_odasi_4.sleeping_double (missing nightstand): no place passes the checks (sleeping_double: no place passes the checks) | Add the missing second nightstand to complete the sleeping set (a:F205). |
| 33866 | 1 | move_piece | f_L0_034 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Move the nightstand away from the bed to resolve the 0.06 m² collision and correct the -0.12 m offset to a valid gap (≤ 0.30 m). |
| 33868 | 1 | fix_fixture | f_L1_016 | fixture_place: f_L1_016: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_005) | Washbasin blocks door d_L1_005 swing; move it up to 0.5 m to clear the door path. |
| 33871 | 1 | swap_model | f_L0_037 | asset_type: dining_chair_02 is a chair model, not a office_chair | Replace the corporate black mesh office chair with a residential modern dining chair to match the warm bedroom style (D3). |
| 33873 | 1 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the south wall to the left so the door swing and the desk zone free up ≥0.8 m in front (G13). |
| 33877 | 1 | move_piece | f_L0_034 | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:F9:f_L0_034 and c:G4:f_L0_034: move the nightstand away from the bed to resolve the 0.06 m² collision and correct the -0.12 m offset to a valid gap (≤ 0.30 m). |
| 33878 | 1 | move_piece | f_L0_009 | f_L0_009: no_overlap, f_L0_029: clearance_ok, score: plausibility 67 -> 47 (F3 f_L0_009: wardrobe: its back is not on a wall (0.28 m off); F9 f_L0_029: desk f_L0_029 overlaps wardrobe f_L0_009 by 0.05 m²; G13 f_L0_009: wardrobe f_L0_009: 0.35 m free in front, needs ≥ 0.80 m) | Move wardrobe 0.3 m away from the south wall to increase front clearance from 0.17 m toward the 0.80 m needed (G13). |
| 33879 | 1 | fix_fixture | f_L1_015 | fixture_place: f_L1_015: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L1_004) | Door d_L1_004 swings into the washbasin; move it to the nearest valid spot off the door swing. |
| 33880 | 1 | move_piece | f_L0_034 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix c:F9:f_L0_034 and c:G4:f_L0_034: move the nightstand away from the bed to resolve the 0.06 m² collision and correct the -0.12 m offset to a valid gap (≤ 0.30 m). |
| 33881 | 1 | move_piece | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.08 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.3 m south so the left side gains ≥0.6 m of clearance (G5 left) and the right side opens for the second nightstand (G4/G5 right). |
| 33883 | 1 | set_camera | r_L0_e_yatak_odasi | show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002, f_L0_007 passes the camera checks: cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_3 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views | Reposition the L0 en-suite bedroom camera to include door d_L0_002 and the bed. |
| 33884 | 1 | move_piece | f_L0_021 | score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Move bed 0.3 m toward room centre to balance side clearances toward the 0.60 m needed (G5). |
| 33885 | 1 | move_piece | f_L-1b_024 | max_tries: f_L-1b_024 was edited 3 times in this round | Nudge the head chair 9 cm away from the table (within its 0.3 m allowance) to open the 0.78 m clearance behind it to the required 0.81 m (G6). |
| 33886 | 1 | swap_model | f_L1_021 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Toilet floats 0.20 m above floor and was built below library level; swap to a real library toilet model that sits on the floor. |
| 33891 | 1 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift the bed 0.3 m west so the right side gains ≥0.6 m of clearance (G5 right) and the left side keeps its 0.82 m. |
| 33895 | 1 | swap_model | f_L1_021 | acceptance: pin_refused: f_L1_021: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Toilet floats 0.20 m above floor and was built below library level; swap to the real Caesar C1348 toilet model that sits on the floor. |
| 33896 | 1 | swap_model | f_L0_037 | asset_unusable: chinese_armchair is not used: audit pending | Replace the corporate black mesh office chair with a residential japandi armchair to match the warm bedroom style (D3). |
| 33900 | 1 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_industrial_1_6794b9a5: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swapping to a model with a proper floor contact and a footprint close to the drawn 1.0x0.55. |
| 33901 | 1 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.20 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift the bed 0.2 m west, keeping the headboard on the north wall, so the right side gains ≥0.6 m of clearance (G5 right). |
| 33903 | 1 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Slide wardrobe along the south wall into the free span to open front clearance (G13). |
| 33904 | 1 | swap_model | f_L0_018 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swapping to a model with proper floor contact and a footprint close to the drawn 0.5x0.69. |
| 33905 | 1 | move_piece | f_L0_022 | max_tries: f_L0_022 was edited 3 times in this round | Shift the bed 0.3 m north, keeping the headboard on the north wall, so the left side gains ≥0.6 m of clearance (G5 left) and the right side opens for the second nightstand. |
| 33906 | 1 | swap_model | f_L1_015 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Washbasin floats 0.384 m above its floor; swap to a real sink model that sits on the floor. |
| 33909 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet f_L-1_104 was built below the library level (parametric mesh); swap to the real library model Movian Argenton Colonna da bagno (0.30x0.27x1.40) at the same footprint. |
| 33912 | 1 | swap_model | f_L0_048 | acceptance: pin_refused: f_L0_048: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet was built below library level with a parametric mesh (F241); swapping to a real library model (narrow 0.4 m wide, close to the drawn 0.4x0.35). |
| 33913 | 1 | swap_model | f_L1_015 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Washbasin floats 0.384 m above its floor; swap to the Hudson Reed vanity unit & basin that sits on the floor. |
| 33915 | 1 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet f_L0_049 was built below the library level with a parametric mesh; swap to the 0.40x0.57x1.85 m library model to clear the wrong_model finding. |
| 33916 | 1 | swap_model | f_L0_004 | pin_refused: f_L0_004: gen_washbasin_modern_minimal_1_d5536003: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swap to a floor-sitting modern minimal model of similar footprint (0.64 x 0.64 m). |
| 33918 | 1 | swap_model | f_L-1_025 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | washbasin f_L-1_025 sits +0.384 m above its floor; swap to the library Sink (0.965x0.5) whose base sits on the floor. |
| 33921 | 1 | swap_model | f_L0_016 | pin_refused: f_L0_016: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to a floor-sitting japandi toilet of similar footprint (0.42 x 0.69 m). |
| 33925 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | washbasin f_L0_005 sits +0.384 m above its floor; swap to a library model whose base sits on the floor to clear the S1 wrong_model finding. |
| 33926 | 1 | swap_model | f_L-1_052 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | toilet f_L-1_052 sits +0.200 m above its floor; swap to the library Qualitas toilet (0.48x0.68) whose base sits on the floor. |
| 33927 | 1 | swap_model | f_L0_003 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); swapping to a real product (0.965x0.5, close to the drawn 1.0x0.55) with proper floor contact. |
| 33933 | 1 | swap_model | f_L0_004 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); swap to a real floor-sitting sink model (0.97 x 0.50 m) close to the drawn 1.0 x 0.55 m footprint. |
| 33934 | 1 | swap_model | f_L0_017 | pin_refused: f_L0_017: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | toilet f_L0_017 sits +0.200 m above its floor; swap to a library model whose base sits on the floor to clear the S1 wrong_model finding. |
| 33939 | 1 | swap_model | f_L0_016 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swap to a real floor-sitting toilet model (0.48 x 0.68 m) matching the drawn 0.5 x 0.68 m footprint. |
| 33941 | 1 | swap_model | f_L0_004 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); swap to a real floor-sitting vanity unit & basin (0.91 x 0.60 m) close to the drawn 1.0 x 0.55 m footprint. |
| 33942 | 1 | swap_model | f_L0_016 | acceptance: pin_refused: f_L0_016: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to a real floor-sitting toilet (0.46 x 0.72 m) close to the drawn 0.5 x 0.68 m footprint. |
| 33943 | 1 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet f_L0_049 was built below the library level with a parametric mesh; swap to the 0.52x0.25x1.63 m library model to clear the wrong_model finding. |
| 33944 | 1 | swap_model | f_L-1_104 | acceptance: pin_refused: f_L-1_104: hssd_97162e912362bae3a0ca0d385f9dab8e43360108: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet f_L-1_104 was built below the library level (parametric mesh); swap to the real library model Prada Laundry Cabinet (0.55x0.37x1.80) at the same footprint. |
| 33945 | 1 | swap_model | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor (S1); swap to a real floor-sitting sink (0.96 x 0.50 m) close to the drawn 1.0 x 0.55 m footprint. |
| 33946 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_mediterranean_4_c5dc64de: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | washbasin f_L0_005 sits +0.384 m above its floor; swap to a library model whose base sits on the floor to clear the S1 wrong_model finding. |
| 33947 | 1 | swap_model | f_L-1_025 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | washbasin f_L-1_025 sits +0.384 m above its floor; swap to the library Hudson Reed Sublime Vanity Unit & Basin (0.91x0.60) whose base sits on the floor. |
| 33948 | 1 | swap_model | f_L0_017 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | toilet f_L0_017 sits +0.200 m above its floor; swap to a library model whose base sits on the floor to clear the S1 wrong_model finding. |
| 33949 | 1 | swap_model | f_L-1_052 | acceptance: pin_refused: f_L-1_052: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | toilet f_L-1_052 sits +0.200 m above its floor; swap to the library Caesar Toilet C1348 (0.46x0.72) whose base sits on the floor. |
| 33950 | 1 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: drawer_cabinet: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet f_L0_049 was built below the library level with a parametric mesh; swap to the 1.14x0.49x1.88 m library model to clear the wrong_model finding. |
| 33951 | 1 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | washbasin f_L0_005 sits +0.384 m above its floor; swap to a library model whose base sits on the floor to clear the S1 wrong_model finding. |
| 33952 | 1 | swap_model | f_L0_017 | pin_refused: f_L0_017: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | toilet f_L0_017 sits +0.200 m above its floor; swap to a library model whose base sits on the floor to clear the S1 wrong_model finding. |
| 34463 | 2 | add_camera | ext_8 | the camera stands inside the building b2 (another building on the plot), eye height 1.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.21 m), the ground at (0, 25) is at z 0.44 m: use z 1.94 to 2.14 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No frontal view of the entrance (+y) facade exists in the exterior camera set. (fixes a:F159) |
| 34464 | 2 | set_entrance | d_L0_005 | exists: 'd_L0_005' is no outside door of site.entrances | Argus: The entrance leads to a dead-end wall / undefined door; setting the entrance solution defines the approach and door. (fixes a:F163) |
| 34465 | 2 | set_camera | r_L0_e_yatak_odasi | show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views | Argus: The view must show door d_L0_002 but does not; re-aiming the camera to show it fixes it. (fixes a:F165) |
| 34466 | 2 | set_material | plot_wall | plot_wall: stone_wall_ashlar is another stone than the house's base stone_wall_ledgestone: one stone per house (the plinth, the plot walls and the facade's base match; UL204) | Argus: The retaining wall is a bare concrete slab out of place with the stone facade; setting the plot_wall slot to a stone look fixes it. (fixes a:F167) |
| 34471 | 2 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_025, f_L0_003 passes the camera checks: cam_r_L0_banyo_1: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_banyo_1 would show the view cam_r_L0_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views | Argus: The bathtub is barely visible and the wall is unbroken; re-aiming to show the tub and basin fixes the composition. (fixes a:F174) |
| 34473 | 2 | add_camera | ext_9 | eye height 0.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.21 m), the ground at (0, 40) is at z 1.44 m: use z 2.94 to 3.14 for an eye-level view | Argus: The previous attempt was refused because the camera stood inside the building; a new exterior camera placed in the open ground in front of the +y facade gives the missing frontal view. (fixes a:F180) |
| 34474 | 2 | swap_model | f_L1_017 | room_rule: f_L1_017: 3dwh_73a3f2fd339beec5aabd5ed6 names daybed: a bed-like daybed, not the sofa of a living room (the piece does not ask for one; a guest, child's or study room keeps it: UL161) | Argus: The indoor upholstered sofa is wrong for the terrace; the generated model was refused, so a real product of the type that fits the caps is swapped in. (fixes a:F181) |
| 34475 | 2 | swap_model | f_L1_020 | asset_unusable: hssd_6502402525039b58cbeccba1add4fc43d9102010 is not used: audit removed | Argus: Same cause as F181: an indoor sofa on the terrace; a real product of the type that fits the caps is swapped in. (fixes a:F182) |
| 34476 | 2 | swap_model | f_L1_023 | acceptance: pin_refused: f_L1_023: hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82: the user rejected this model on 2026-11-01 (UL239: "Don't use this table", real04 run 20261031-194116-full, r_L1_oyun_aktivite_ve_dinlenme_odasi (f_L1_023)): never used again on any project (results/library/user_rejected.json): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The indoor coffee table is wrong for the terrace and the previously tried asset was removed by audit; a usable real product of the type is swapped in. (fixes a:F183) |
| 34477 | 2 | swap_model | f_L-1_071 | asset_unusable: 3dwh_49c89838e523cdc64ffa7de1 is not used: audit removed | Argus: The current armchair is 0.12 m off its drawn place and its depth (0.80 m) exceeds the drawn 0.569 m; a model closer to the drawn size is swapped in. (fixes a:F184) |
| 34478 | 2 | set_camera | r_L-1_koridor_2 | show: none of the 3 best poses of r_L-1_koridor_2 that show d_L-1_001, d_L-1_002 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Argus: The current view shows only closed doors and a bare wall; re-aiming to show the open doors into the rooms makes the hall read as a space. (fixes a:F189) |
| 34482 | 2 | place_group | r_L0_e_banyo_2 | no_change: r_L0_e_banyo_2 already has its bathroom_set r_L0_e_banyo_2.bathroom_set (anchor f_L0_014, members f_L0_004, f_L0_016): nothing missing, never a second set | Argus: The twin r_L0_e_banyo has a tall_cabinet that r_L0_e_banyo_2 lacks; completing the bathroom set adds the missing storage member. (fixes a:F194) |
| 34483 | 2 | place_group | r_L0_koridor | no_change: r_L0_koridor already has its entrance r_L0_koridor.entrance (anchor None, members f_L0_054): nothing missing, never a second set | Argus: The 7.6 m2 hall with 12 doors holds only a shoe_cabinet; adding the entrance group supplies the missing console/coat storage. (fixes a:F196) |
| 34484 | 2 | place_group | r_L0_koridor_2 | no_change: r_L0_koridor_2 already has its entrance r_L0_koridor_2.entrance (anchor None, members f_L0_055): nothing missing, never a second set | Argus: r_L0_koridor_2 holds only a shoe_cabinet and no stair; adding the entrance group supplies the missing console/coat storage for the 7.6 m2 hall. (fixes a:F199) |
| 34485 | 2 | complete_group | r_L0_yatak_odasi.sleeping_double | no_change: r_L0_yatak_odasi.sleeping_double: nothing missing (members: f_L0_041, f_L0_042) | Argus: The bedroom has one nightstand; completing the sleeping_double group adds the missing second nightstand. (fixes a:F200) |
| 34486 | 2 | complete_group | r_L0_yatak_odasi_2.sleeping_double | no_change: r_L0_yatak_odasi_2.sleeping_double: nothing missing (members: f_L0_044, f_L0_045) | Argus: The bedroom has one nightstand; completing the sleeping_double group adds the missing second nightstand. (fixes a:F201) |
| 34487 | 2 | complete_group | r_L0_e_yatak_odasi.sleeping_double | no_change: r_L0_e_yatak_odasi.sleeping_double: nothing missing (members: f_L0_031, f_L0_032, f_L0_051) | Argus: The bedroom has one nightstand; completing the sleeping_double group adds the missing second nightstand. (fixes a:F202) |
| 34488 | 2 | complete_group | r_L0_e_yatak_odasi_2.sleeping_double | no_change: r_L0_e_yatak_odasi_2.sleeping_double: nothing missing (members: f_L0_033, f_L0_034, f_L0_052) | Argus: The bedroom has one nightstand; completing the sleeping_double group adds the missing second nightstand. (fixes a:F203) |
| 34489 | 2 | complete_group | r_L0_yatak_odasi_3.sleeping_double | memory: the same edit was rejected in round 1: no_place: r_L0_yatak_odasi_3.sleeping_double (missing nightstand): no place passes the checks (sleeping_double: no place passes the checks) | Argus: The bedroom has one nightstand; completing the sleeping_double group adds the missing second nightstand. (fixes a:F204) |
| 34490 | 2 | complete_group | r_L0_yatak_odasi_4.sleeping_double | memory: the same edit was rejected in round 1: no_place: r_L0_yatak_odasi_4.sleeping_double (missing nightstand): no place passes the checks (sleeping_double: no place passes the checks) | Argus: The bedroom has one nightstand; completing the sleeping_double group adds the missing second nightstand. (fixes a:F205) |
| 34491 | 2 | place_group | r_L0_e_banyo | no_change: r_L0_e_banyo already has its bathroom_set r_L0_e_banyo.bathroom_set (anchor f_L0_013, members f_L0_006, f_L0_015): nothing missing, never a second set | Argus: The twin r_L0_e_banyo_2 has a tall_cabinet that r_L0_e_banyo lacks; completing the bathroom set adds the missing storage member. (fixes a:F207) |
| 34496 | 2 | retype_piece | f_L0_019 | acceptance: finding Q4:f_L0_019 is still there after the edit (Argus: missing anchor: the double bed is not in the room, so the bedroom has no bed; the wardrobe mirror even reflects a bed that is not present, which makes th); a retype to the piece's own type only confirms it (status unverified -> verified, the same fitted model): nothing changes in the render, so its vision findings stay | Confirm the drawn double bed's type so the bedroom's anchor bed is verified and present (Q4 missing anchor). |
| 34499 | 2 | retype_piece | f_L0_041 | no_change: f_L0_041 is already a nightstand | Confirm the nightstand's type so the sleeping set's members are verified and present (Q4 missing anchor). |
| 34500 | 2 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071, f_L-1b_046)); 1 more kept | Face armchair f_L-1b_052 towards the sofa f_L-1b_042 and coffee table f_L-1b_071 to fix F4/G3 orientation findings. |
| 34504 | 2 | move_piece | f_L-1_073 | f_L-1_070: no_overlap | Shift coffee table 0.2 m right to clear the 0.12 m² overlap with armchair f_L-1_071. |
| 34506 | 2 | move_piece | f_L-1_070 | f_L-1_070: no_overlap, f_L-1_089: no_overlap | Pull armchair away from the back of sofa f_L-1_053 to fix the behind-the-back orientation and open a 0.6 m walkway to its front. |
| 34507 | 2 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Face the armchair into the room (away from the back of sofa f_L-1_054) to fix F4 orientation and improve G11 walkway access. |
| 34508 | 2 | rotate_piece | f_L-1_102 | score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of it) | Face the tv_unit into the seating area (away from the back of armchair f_L-1_069) to fix F4 orientation. |
| 34510 | 2 | move_piece | f_L-1_073 | memory: the same edit was rejected in round 2: f_L-1_070: no_overlap | Shift coffee table 0.2 m right to clear the 0.12 m² overlap with armchair f_L-1_071. |
| 34513 | 2 | rotate_piece | f_L1_052 | acceptance: finding F4:f_L1_052 is still there after the edit (armchair does not face its group (f_L1_017, f_L1_023)) | Turn the reading-corner armchair away from the back of sofa f_L1_017 so it faces into the room (c:F4). |
| 34514 | 2 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Slide wardrobe along the top wall toward the corner to open ≥0.80 m in front (0.66 m now) while keeping its back on the wall. |
| 34516 | 2 | move_piece | f_L-1b_051 | score: plausibility 58 -> 28 (G3 f_L-1b_051: armchair f_L-1b_051 is 40° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.66 m (needs ≤ 2.50 m); G11 f_L-1b_042: sofa f_L-1b_042: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_074: armchair f_L-1b_074: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Move armchair f_L-1b_051 slightly south to clear the front zone of f_L-1b_052 and improve alignment with sofa f_L-1b_042. |
| 34518 | 2 | move_piece | f_L-1_070 | drawn_lock: f_L-1_070: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.84 m) | Pull armchair f_L-1_070 up to y=1.8 to clear the bookshelf f_L-1_089 and the back of sofa f_L-1_053, opening a walkway to its front. |
| 34519 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_033 slightly north to increase clearance from table edge to at least 0.81 m. |
| 34520 | 2 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Slide wardrobe along the top wall to the far end so the desk no longer blocks its front, opening ≥0.80 m clearance. |
| 34521 | 2 | move_piece | f_L-1_070 | f_L-1_070: no_overlap, f_L-1_089: no_overlap | Move armchair f_L-1_070 up 0.3 m to clear the back of sofa f_L-1_053 and open a walkway to its front. |
| 34523 | 2 | rotate_piece | f_L-1b_051 | acceptance: finding G3:f_L-1b_051 is still there after the edit (armchair f_L-1b_051 is 123° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m)) | Rotate armchair f_L-1b_051 to face 270° (towards the sofa f_L-1b_042) to fix the 33° G3 angle finding. |
| 34526 | 2 | move_piece | f_L-1_070 | max_tries: f_L-1_070 was edited 3 times in this round | Move armchair f_L-1_070 left 0.3 m to clear the bookshelf f_L-1_089 and the back of sofa f_L-1_053. |
| 34527 | 2 | move_piece | f_L0_020 | memory: the same edit was rejected in round 1: score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.07 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.07 m toward the left wall to open ≥0.60 m on the right side (0.53 m now) and 0.63 m on the left. |
| 34530 | 2 | move_piece | f_L0_020 | memory: the same edit was rejected in round 1: score: plausibility 70 -> 54 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free left side of the head (0.97 m free); G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (2.83 m free); G4 f_L0_044: nightstand f_L0_044 of bed_double f_L0_020: its back 2.57 m fr | Snap the bed's headboard flush to the left wall (it stands 0.07 m off) to open ≥0.60 m on both sides. |
| 34533 | 2 | move_piece | f_L-1_101 | score: plausibility 30 -> 20 (G1 f_L-1_101: TV unit f_L-1_101 1.15 m off the sofa axis, needs ≤ 0.30 m) | Move tv_unit f_L-1_101 up to y=2.5 to pull it away from the back of armchair f_L-1_071, resolving the behind-the-back orientation. |
| 34535 | 2 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_033 further north to increase clearance from table edge to at least 0.81 m. |
| 34539 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G4:f_L0_022 is still there after the edit (bed_double f_L0_022: no nightstand on the free right side of the head (0.37 m free)); 2 more kept | Individual moves and complete_group failed on tight clearances; solver candidate 1 repositions bed, wardrobe and work group as a system to satisfy bed side clearances, wardrobe front clearance and the missing second nightstand. |
| 34541 | 2 | place_group | r_L0_e_yatak_odasi_2 | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group around the bed anchor to fix a:F203 (incomplete sleeping set / missing second nightstand) and ensure valid nightstand placement. |
| 34542 | 2 | move_piece | f_L-1_049 | drawn_lock: f_L-1_049: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.73 m) | Move armchair f_L-1_049 down to y=5.5 to shift it away from the sofa corner and ensure its front use zone is reachable by a 0.6 m walkway from the door. |
| 34545 | 2 | relayout_room | r_L-1b_salon | group checks: F4 f_L-1b_096: tv_unit stands behind the back of f_L-1b_051, looking at it; G9 r_L-1b_salon_kitchen: kitchen r_L-1b_salon_kitchen has no fridge (fridge) | Use solver candidate 1 to re-layout the room, addressing remaining armchair orientation (G3 f_L-1b_051), clearance (G6 f_L-1b_033), and F6 findings. |
| 34546 | 2 | swap_model | f_L1_089 | off_style: f_L1_089: ArmChair_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the defective armchair model (back/arm 5.2 cm off the seat, M33) with a clean classic armchair. |
| 34548 | 2 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Test whether the wardrobe can be re-placed with ≥0.80 m front clearance (G13); the previous 0.3 m move was rejected for overlap with the desk, so I probe the validator for a valid spot. |
| 34549 | 2 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G4:f_L0_022 is still there after the edit (bed_double f_L0_022: no nightstand on the free right side of the head (0.37 m free)); 2 more kept | Candidate 1 kept G4/G5/G13; trying solver candidate 2, which places the sleeping group differently (partners 0.33) to free the bed's right side for the second nightstand. |
| 34550 | 2 | move_piece | f_L-1_101 | acceptance: finding F4:f_L-1_101 is still there after the edit (tv_unit stands behind the back of f_L-1_071, looking at it) | Move tv_unit f_L-1_101 up 0.3 m to pull it away from the back of armchair f_L-1_071 while staying on the sofa axis. |
| 34554 | 2 | place_group | r_L0_e_yatak_odasi_2 | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group around the bed anchor with the bench option to fix a:F203 (incomplete sleeping set) and place the nightstands validly. |
| 34555 | 2 | swap_model | f_L1_089 | acceptance: pin_refused: f_L1_089: modern_arm_chair_01: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the defective armchair model (back/arm 5.2 cm off the seat, M33) with a modern armchair matching the project style chain. |
| 34556 | 2 | move_piece | f_L-1b_051 | score: plausibility 58 -> 38 (G11 f_L-1b_042: sofa f_L-1b_042: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_074: armchair f_L-1b_074: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Move armchair f_L-1b_051 to clear the front zone of f_L-1b_052 and improve alignment with sofa f_L-1b_042. |
| 34557 | 2 | place_group | r_L0_e_yatak_odasi | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_007: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group around the bed anchor so the nightstands sit correctly and the set is complete (a:F202). |
| 34559 | 2 | move_piece | f_L0_021 | score: plausibility 67 -> 37 (F3 f_L0_021: bed_double: the headboard stands in the room (0.15 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free); G5 f_L0_021: bed_double f_L0_021: 0.38 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.15 m toward the room centre to gain side clearance on both flanks (G5 left 0.37 m, right 0.52 m, needs 0.60 m). |
| 34563 | 2 | swap_model | f_L1_089 | acceptance: pin_refused: f_L1_089: abo_B07124WN69: fails the fit rules (caps, height, at most 1.22 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the defective armchair model (back/arm 5.2 cm off the seat, M33) with a modern/scandinavian armchair of a real product size that fits the 0.75 m footprint. |
| 34564 | 2 | swap_model | f_L0_033 | off_style: f_L0_033: abo_B07DBB7831 is of the styles ['classic', 'modern', 'scandinavian'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric mesh with a library nightstand model to fix a:F235 (below-library-level finding) for nightstand f_L0_033. |
| 34565 | 2 | move_piece | f_L-1b_051 | max_tries: f_L-1b_051 was edited 3 times in this round | Move armchair f_L-1b_051 slightly east to clear the front zone of f_L-1b_052 (F6) while maintaining alignment with sofa f_L-1b_042. |
| 34566 | 2 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Vector geometry (hanging rail with hangers) outranks the AI's bench reading; it is a coat closet, and wardrobe is the storage group's option. |
| 34568 | 2 | move_piece | f_L0_021 | acceptance: finding G5:f_L0_021 is still there after the edit (bed_double f_L0_021: 0.23 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.15 m toward the foot (away from the nightstand side) to gain clearance along the left flank (G5 left 0.37 m, needs 0.60 m) while keeping the headboard on the wall. |
| 34569 | 2 | swap_model | f_L0_032 | off_style: f_L0_032: abo_B07DBB7831 is of the styles ['classic', 'modern', 'scandinavian'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric mesh of nightstand f_L0_032 with a library model (0.505x0.459, modern/scandinavian) to resolve the below_library finding a:F234. |
| 34570 | 2 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L-1_026: washbasin floats +0.384 m above floor; swap to a library model that sits on the floor |
| 34573 | 2 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L-1_051: toilet floats +0.200 m above floor; swap to a library model that sits on the floor |
| 34574 | 2 | swap_model | f_L1_089 | max_tries: f_L1_089 was edited 3 times in this round | Replace the defective armchair model (back/arm 5.2 cm off the seat, M33) with a modern minimal armchair of a real product size that fits the 0.75 m footprint. |
| 34575 | 2 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B07L1DX1LH: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a minimal/modern library nightstand model to fix a:F235 (below-library-level finding) for nightstand f_L0_033. |
| 34576 | 2 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: abo_B07L1DX1LH: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh of nightstand f_L0_032 with a minimal/modern library model (0.489x0.427) to resolve the below_library finding a:F234. |
| 34578 | 2 | fix_fixture | f_L0_005 | fixture_place: f_L0_005: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_008) | Door d_L0_008 swings into the washbasin on one hinge side; nudge it out of the swing. |
| 34585 | 2 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: abo_B07H8PQFR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:F232: tall_cabinet built below library level (parametric mesh); swap to a proper library model |
| 34586 | 2 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh of nightstand f_L0_032 with a minimal/modern library model (0.49x0.415) to resolve the below_library finding a:F234. |
| 34587 | 2 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: hssd_d06c4e7cdfc08578e0d7f16725f4453c93a401ce: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a minimal/modern library nightstand model (Helen Night Stand) to fix a:F235 (below-library-level finding) for nightstand f_L0_033. |
| 34597 | 2 | swap_model | f_L0_033 | max_tries: f_L0_033 was edited 3 times in this round | Replace the parametric mesh with a modern/minimal library nightstand model (Side Table 01, 0.55 m tall) to fix a:F235 (below-library-level finding) for nightstand f_L0_033. |
| 34598 | 2 | swap_model | f_L0_032 | max_tries: f_L0_032 was edited 3 times in this round | Replace the parametric mesh of nightstand f_L0_032 with a minimal/modern library model (0.509x0.434) to resolve the below_library finding a:F234. |
| 34600 | 2 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_mediterranean_4_c5dc64de: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L-1_026: washbasin floats +0.384 m above floor; try another library model that sits on the floor |
| 34603 | 2 | swap_model | f_L-1_051 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | c:S1:f_L-1_051: toilet floats +0.200 m above floor; try another library model that sits on the floor |
| 34604 | 2 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:F232: tall_cabinet built below library level; try a real product model (0.52x0.25x1.63) that fits the 0.4x0.35 footprint |
| 34605 | 2 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a modern/minimal library nightstand model (Side Table 01, 0.55 m tall) to fix a:F236 (below-library-level finding) for nightstand f_L0_034. |
| 34608 | 2 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L-1_026: washbasin floats +0.384 m above floor; try another library model that sits on the floor |
| 34612 | 2 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a modern library nightstand model (Recycled Retro Chest, 0.6 m tall) to fix a:F236 (below-library-level finding) for nightstand f_L0_034. |
| 34614 | 2 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L-1_051: toilet floats +0.200 m above floor; try another library model that sits on the floor |
| 34615 | 2 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: drawer_cabinet: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | a:F232: tall_cabinet built below library level; try the polyhaven drawer cabinet model |
| 34616 | 2 | swap_model | f_L0_034 | no_change: f_L0_034 already uses the model abo_B07HSH4ZR2 | Replace the parametric mesh with a modern/scandinavian library nightstand model (Rivet Kingston, 0.57 m tall) to fix a:F236 (below-library-level finding) for nightstand f_L0_034. |
| 35143 | 3 | swap_model | f_L-1_073 | asset_unusable: 3dwh_bb844ce3afc495e5987d7713 is not used: audit removed | Argus: The table_coffee f_L-1_073 was built with a parametric mesh that sits below the library level. The fit stage chose the parametric model instead of a library model. Swapping to a library model (3dwh_bb844ce3afc495e5987d7713, 0.80 x 0.80 x 0. (fixes a:F229) |
| 35144 | 3 | swap_model | f_L-1_074 | asset_unusable: 3dwh_bb844ce3afc495e5987d7713 is not used: audit removed | Argus: The table_coffee f_L-1_074 was built with a parametric mesh that sits below the library level. The previous swap_model attempt with abo_B07GDSF3MR was refused (pin_refused: fails fit rules). Trying 3dwh_bb844ce3afc495e5987d7713 (0.80 x 0.80 (fixes a:F230) |
| 35145 | 3 | swap_model | f_L-1_102 | acceptance: pin_refused: f_L-1_102: abo_B072ZNBRR6: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tv_unit f_L-1_102 was built with a parametric mesh that sits below the library level. The previous swap_model attempt with abo_B07QB8DQ45 was refused (pin_refused: fails fit rules). Trying abo_B072ZNBRR6 (1.80 x 0.47 x 0.42 m, industria (fixes a:F231) |
| 35146 | 3 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall_cabinet f_L-1_103 (0.40 x 0.35 m) in the bathroom was built with a parametric mesh below the library level. Previous swaps (abo_B07H8PQFR2, drawer_cabinet, hssd_97162e...) were all refused (pin_refused: fails fit rules). Trying abo (fixes a:F232) |
| 35147 | 3 | swap_model | f_L-1_104 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L-1_104: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall_cabinet f_L-1_104 (0.40 x 0.35 m) in the bathroom was built with a parametric mesh below the library level. Previous swaps (abo_B07GFFY4WT, abo_B07H8PQFR2, drawer_cabinet) were all refused (pin_refused: fails fit rules). Trying abo (fixes a:F233) |
| 35148 | 3 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: abo_B07HSH4ZR2: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The nightstand f_L0_032 (0.50 x 0.45 m) was built with a parametric mesh below the library level. Previous swaps (side_table_01, ClassicNightstand_01) were refused (pin_refused / off_style). Trying abo_B07HSH4ZR2 (0.50 x 0.41 x 0.57 m, mode (fixes a:F234) |
| 35149 | 3 | swap_model | f_L0_033 | no_change: f_L0_033 already uses the model abo_B07HSH4ZR2 | Argus: The nightstand f_L0_033 (0.50 x 0.45 m) was built with a parametric mesh below the library level. Previous swaps (abo_B07DBB7831 off_style, hssd_d06c4e... pin_refused, hssd_xxxx5629... pin_refused) were all refused, and max_tries was hit. T (fixes a:F235) |
| 35150 | 3 | swap_model | f_L0_034 | memory: the same edit was rejected in round 2: no_change: f_L0_034 already uses the model abo_B07HSH4ZR2 | Argus: The nightstand f_L0_034 (0.50 x 0.45 m) was built with a parametric mesh below the library level. Previous swaps (abo_B07DBB7831 off_style, abo_B07L1DX1LH pin_refused, hssd_d06c4e... pin_refused) were all refused, and max_tries was hit. Try (fixes a:F236) |
| 35151 | 3 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B07QS8TBXT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The nightstand f_L0_042 (0.40 x 0.40 m) was built with a parametric mesh below the library level. Previous swaps (abo_B01D3C7Z4A, side_table_01, ClassicNightstand_01, abo_B07K7K7GTZ) were all refused (pin_refused / off_style). Trying abo_B0 (fixes a:F237) |
| 35152 | 3 | swap_model | f_L0_044 | acceptance: pin_refused: f_L0_044: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The nightstand f_L0_044 (0.40 x 0.40 m) was built with a parametric mesh below the library level. The previous swap (abo_B07QS8TBXT) was refused (pin_refused: fails fit rules). Trying abo_B0861YKM8S (0.40 x 0.40 x 0.61 m, minimal/modern) wh (fixes a:F238) |
| 35153 | 3 | swap_model | f_L0_045 | acceptance: pin_refused: f_L0_045: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The nightstand f_L0_045 (0.40 x 0.40 m) was built with a parametric mesh below the library level. The only previous attempt was move_piece which was refused (inside_room). Trying abo_B0861YKM8S (0.40 x 0.40 x 0.61 m, minimal/modern) which e (fixes a:F239) |
| 35154 | 3 | swap_model | f_L0_047 | acceptance: pin_refused: f_L0_047: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tall_cabinet f_L0_047 (0.30 x 0.30 m) in the bathroom was built with a parametric mesh below the library level. The previous swap (abo_B07GFFY4WT) was refused (pin_refused: fails fit rules). Trying abo_B07RMJPJMX (0.30 x 0.27 x 1.40 m,  (fixes a:F240) |
| 35155 | 3 | swap_model | f_L0_048 | acceptance: pin_refused: f_L0_048: hssd_97162e912362bae3a0ca0d385f9dab8e43360108: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The fitting chose the parametric mesh; a library tall_cabinet of the same type and size fits the bathroom and leaves the review list. (fixes a:F241) |
| 35156 | 3 | swap_model | f_L1_009 | room_rule: f_L1_009: hssd_e9393fb84e42e59d93ba261275daf119df0cde2e the drawn table_dining is round and the model is not (its title names no round shape): a square table's corners and legs would stand in the chairs drawn round it (rule round_table) | Argus: The fitting chose the parametric mesh; a library table_dining of the same type and size fits the room and leaves the review list. (fixes a:F242) |
| 35157 | 3 | swap_model | f_L1_066 | exists: no piece 'f_L1_066' in a room of the building | Argus: The fitting chose the parametric mesh; a library tall_cabinet of the same type and size fits the bathroom and leaves the review list. (fixes a:F243) |
| 35159 | 3 | swap_model | f_L0_049 | acceptance: pin_refused: f_L0_049: hssd_97162e912362bae3a0ca0d385f9dab8e43360108: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The fitting chose the parametric mesh; a library tall_cabinet of the same type and size fits the bathroom and leaves the review list. (fixes a:F246) |
| 35160 | 3 | swap_model | f_L1_021 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L1_021: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The fitting chose the parametric mesh; the other library toilets were refused (audit removed or failing the sloped-ceiling height cap), but 3dwh_36adbef7518af3145f49b210 (0.46 x 0.72 x 0.80 m) is in the allowed list and was not refused, so  (fixes a:F247) |
| 35161 | 3 | swap_model | f_L1_022 | acceptance: pin_refused: f_L1_022: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The fitting chose the parametric mesh; the other library toilets were refused (audit removed or failing the sloped-ceiling height cap), but 3dwh_36adbef7518af3145f49b210 (0.46 x 0.72 x 0.80 m) is in the allowed list and was not refused, so  (fixes a:F248) |
| 35163 | 3 | swap_model | f_L-1_049 | no_change: f_L-1_049 already uses the model 3dwh_324a4061c7079774c20c56e9 | Argus: The dark sculptural lounge chair clashes with the light minimalist sofa and dining set; the minimal/modern/scandinavian model 3dwh_324a4061c7079774c20c56e9 matches the room's palette and was already attempted (no_change means it is the curr (fixes a:F323) |
| 35164 | 3 | swap_model | f_L-1_027 | acceptance: pin_refused: f_L-1_027: 3dwh_371b2b828aef220519cc3b6a: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The dark heavy mid-century dining table clashes with the light minimalist living group; 3dwh_371b2b828aef220519cc3b6a is a minimal/modern table that matches the room's palette. (fixes a:F324) |
| 35169 | 3 | set_material | walls | walls: wood_panel (wood) would clad every wall of every room; the walls keep a plain finish (paint), a feature finish goes on one accent wall of a room (its scheme's feature wall: slats, a fluted panel or a headboard panel behind the bed or the sofa) | Argus: The reference style mixes white and wood; the build is all grey. Setting the walls slot to a warm wood panel look adds the missing warm-wood layer. (fixes a:F343) |
| 35170 | 3 | set_camera | ext_3 | eye height 2.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.21 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The previous attempt was refused because the eye height (2.16 m) was outside the allowed exterior range (1.5-1.7 m) and the ground at (0,-30) is at z -0.5. Setting the eye to 1.6 m (within 1.5-1.7) at the same free point, aimed at the facad (fixes a:F345) |
| 35174 | 3 | swap_model | f_L0_038 | memory: the same edit was rejected in round 1: asset_unusable: chinese_armchair is not used: audit pending | Replaces the corporate black leather office chair with a warm classic armchair that fits the calm bedroom palette and light wood desk (a:F334). |
| 35176 | 3 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Center the wardrobe on the free span s2 of wall w_L0_004 to maximize front clearance (needs >= 0.80 m, currently 0.66 m). |
| 35184 | 3 | move_piece | f_L0_020 | snap: f_L0_020: no free place on wall w_L0_001 (doors, windows, at most 1.2 m from the drawn place) | Center the bed on the window wall span s0 to maximize side clearances (needs >= 0.60 m each side, currently 0.53/0.56 m). |
| 35185 | 3 | rotate_piece | f_L1_052 | f_L1_052: clearance_ok, score: plausibility 41 -> 21 (F4 f_L1_052: armchair faces a wall 0.02 m in front of it; F4 f_L1_062: tv_unit stands behind the back of f_L1_052, looking at it; F6 f_L1_052: armchair: the free zone in front of it is reaches out of the room) | Face the reading-corner armchair into the room (180°) so it no longer stands behind the back of sofa f_L1_017 looking at it. |
| 35188 | 3 | move_piece | f_L0_020 | score: plausibility 70 -> 40 (F3 f_L0_020: bed_double: the headboard stands in the room (0.12 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.12 m left to widen the right-side clearance to >= 0.60 m (currently 0.53 m). |
| 35189 | 3 | mark_not_furniture | f_L-1b_002 | no_crop: f_L-1b_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The untyped 5.14 x 2.37 m drawn outline is the cluster outline of the dining group (table plus chairs), not a single piece of furniture. |
| 35190 | 3 | rotate_piece | f_L1_052 | f_L1_052: clearance_ok, score: plausibility 41 -> 21 (F4 f_L1_052: armchair faces a wall 0.22 m in front of it; F6 f_L1_052: armchair: the free zone in front of it is reaches out of the room; G11 f_L1_052: armchair f_L1_052: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Face the reading-corner armchair into the room (270°) so it no longer stands behind the back of sofa f_L1_017 looking at it. |
| 35191 | 3 | move_piece | f_L0_020 | score: plausibility 70 -> 50 (F3 f_L0_020: bed_double: the headboard stands in the room (0.27 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.27 m left so the headboard stays on the left wall and the right-side clearance reaches >= 0.60 m (currently 0.53 m). |
| 35192 | 3 | rotate_piece | f_L-1b_053 | memory: the same edit was rejected in round 1: acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041, f_L-1b_081, f_L-1b_045)); 1 more kept | Rotate armchair f_L-1b_053 to face the seating group (sofa/coffee table) at 270°, resolving the F4 'does not face group' and G3 '90° off' findings. |
| 35193 | 3 | move_piece | f_L1_052 | acceptance: finding F4:f_L1_052 is still there after the edit (armchair stands behind the back of f_L1_017, looking at it) | Shift the reading-corner armchair 0.3 m into the room so its front use zone fits before re-facing it. |
| 35194 | 3 | move_piece | f_L-1_074 | score: plausibility 30 -> 20 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Shift table_coffee f_L-1_074 away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 35195 | 3 | move_piece | f_L0_020 | max_tries: f_L0_020 was edited 3 times in this round | Shift the bed 0.13 m right so the left-side clearance reaches >= 0.60 m (currently 0.56 m) while the headboard stays on the right wall. |
| 35199 | 3 | move_piece | f_L-1b_053 | acceptance: finding F6:f_L-1b_053 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_054) | Move armchair f_L-1b_053 away from f_L-1b_054 to clear the blocked front zone (F6) and give both chairs open space in front. |
| 35209 | 3 | move_piece | f_L1_052 | max_tries: f_L1_052 was edited 3 times in this round | Shift the reading-corner armchair 0.6 m into the room so its front use zone fits before re-facing it. |
| 35214 | 3 | move_piece | f_L-1b_053 | drawn_lock: f_L-1b_053: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.70 m) | Move armchair f_L-1b_053 further south to create clear separation from f_L-1b_054, clearing the F6 front-zone blockage for both chairs. |
| 35216 | 3 | move_piece | f_L0_009 | memory: the same edit was rejected in round 1: f_L0_009: no_overlap; f_L0_029: clearance_ok; score: plausibility 67 -> 47 (F3 f_L0_009: wardrobe: its back is not on a wall (0.28 m off); F9 f_L0_029: desk f_L0_029 overlaps wardrobe f_L0_009 by 0.05 m²; G13 f_L0_009: wardrobe f_L0_009: 0.35 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.30 m away from the south wall to open the 0.17 m front clearance toward the required 0.80 m (G13). |
| 35217 | 3 | swap_model | f_L0_022 | acceptance: pin_refused: f_L0_022: abo_B01M0ZVGCQ: the user rejected this model on 2026-11-01 (UL236: "This model is too plain", real04 run 20261031-194116-full, r_L0_yatak_odasi_3 (f_L0_021)): never used again on any project (results/library/user_rejected.json): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap to the Movian Belaya modern-minimal bed (1.45 x 1.95 m, close to the drawn 1.55 x 1.90 m) whose smooth modern bedding fixes the lumpy-duvet decor finding (UL136). |
| 35219 | 3 | move_piece | f_L-1_042 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Nudge chair f_L-1_042 away from table_dining f_L-1_038 to clear the 0.034 m cut (S2). |
| 35225 | 3 | move_piece | f_L0_009 | score: plausibility 67 -> 57 (F3 f_L0_009: wardrobe: its back is not on a wall (0.16 m off); G13 f_L0_009: wardrobe f_L0_009: 0.01 m free in front, needs ≥ 0.80 m) | Shift the wardrobe 0.16 m away from the south wall to open the 0.17 m front clearance toward the required 0.80 m (G13), staying clear of the desk. |
| 35226 | 3 | set_camera | r_L1_teras | memory: the same edit was rejected in round 1: show: no free camera point of r_L1_teras shows f_L1_108, f_L1_109, f_L1_110 (f_L1_108, f_L1_109, f_L1_110 not in r_L1_teras: name its pieces, doors or windows) | Reframe the terrace so the full armchair-and-side-table group is in frame instead of the foreground chair being cut off. |
| 35227 | 3 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 2: no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group around the bed anchor to complete the set with the missing second nightstand (a:F203). |
| 35229 | 3 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Give the untyped 5.54 x 0.60 m drawn piece a type that fits its size and the living room to clear the NR finding. |
| 35230 | 3 | move_piece | f_L0_021 | memory: the same edit was rejected in round 2: score: plausibility 67 -> 37 (F3 f_L0_021: bed_double: the headboard stands in the room (0.15 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free); G5 f_L0_021: bed_double f_L0_021: 0.38 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.15 m toward the room centre to open the left-side clearance from 0.37 m toward the required 0.60 m (G5). |
| 35231 | 3 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | Swap to the Movian Loue modern bed frame with headboard (1.72 x 2.06 m, fitted to the drawn 1.55 x 1.90 m footprint) whose smooth modern bedding fixes the lumpy-duvet decor finding (UL136). |
| 35232 | 3 | move_piece | f_L-1b_053 | max_tries: f_L-1b_053 was edited 3 times in this round | Move armchair f_L-1b_053 0.3 m east to separate it from f_L-1b_054, clearing the F6 front-zone blockage. |
| 35234 | 3 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh of nightstand f_L0_033 with a real library model (Movian 2-drawer bedside, modern minimal) to fix the below-library-level finding a:F235. |
| 35235 | 3 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | Move table_coffee f_L-1_074 further from armchair f_L-1_069 to fully clear the 0.12 m² overlap (F9). |
| 35236 | 3 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L-1b_024 0.09 m north to increase clearance behind it from 0.78 m to ≥ 0.81 m, fixing G6. |
| 35240 | 3 | move_group | r_L1_banyo_2.bathroom_set | drawn_lock: r_L1_banyo_2.bathroom_set: drawn pieces (f_L1_016, f_L1_022, f_L1_026) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Door d_L1_005 swings into the washbasin; re-solve the drawn bathroom set around its anchor on the long free south wall span to clear the door swing. |
| 35242 | 3 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B079VKDKC1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh of nightstand f_L0_034 with a real library model (Movian 2-drawer bedside, modern minimal) to fix the below-library-level finding a:F236. |
| 35244 | 3 | move_piece | f_L-1_042 | memory: the same edit was rejected in round 3: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Nudge chair f_L-1_042 away from table_dining f_L-1_038 to clear the 0.034 m cut (S2). |
| 35245 | 3 | retype_piece | f_L-1_022 | retype: display_cabinet is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Give the untyped 5.54 x 0.60 m drawn piece a type that fits its size and the living room to clear the NR finding. |
| 35246 | 3 | set_camera | r_L1_teras | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Reframe the terrace so the full armchair-and-side-table group is in frame instead of the foreground chair being cut off. |
| 35248 | 3 | relayout_room | r_L1_banyo_2 | no_place: r_L1_banyo_2 relayout: no place passes the checks (no candidate position fits the room) | Re-solve the bathroom so the door d_L1_005 swing no longer hits the washbasin. |
| 35249 | 3 | relayout_room | r_L-1b_salon_2 | group checks: G3 f_L-1b_053: armchair f_L-1b_053 is 90° off the table_coffee f_L-1b_093 (needs ≤ 30°) at 1.28 m (needs ≤ 2.50 m); G9 r_L-1b_salon_2_kitchen: kitchen r_L-1b_salon_2_kitchen has no fridge (fridge) | Use solver candidate 1 to reposition the seating and living_storage groups, potentially resolving G3 orientation issues and G6 clearance. |
| 35254 | 3 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B07K7K7GTZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh of nightstand f_L0_033 with a real library model (Alkove Hayes 1-drawer nightstand, modern minimal) to fix a:F235. |
| 35255 | 3 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move table_coffee f_L-1_074 away from armchair f_L-1_069 to clear the 0.12 m² overlap (F9). |
| 35256 | 3 | move_piece | f_L-1_042 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Nudge chair f_L-1_042 away from table_dining f_L-1_038 to clear the 0.034 m cut (S2). |
| 35260 | 3 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Washbasin f_L1_016 floats +0.384 m above its floor; swap to a real product model that sits on the floor. |
| 35262 | 3 | move_piece | f_L-1b_024 | score: plausibility 28 -> 18 (F9 f_L-1b_024: chair f_L-1b_024 stands in the corner legs of table_dining f_L-1b_017 (0.02 m into a leg): tucked only between the legs) | Move chair f_L-1b_024 slightly east to change the clearance geometry behind it, attempting to fix G6 (0.78 m → ≥ 0.81 m). |
| 35263 | 3 | fix_fixture | f_L-1_026 | fixture_place: f_L-1_026: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_001) | Door d_L-1_001 swings into the washbasin on one hinge side; move it up to 0.5 m out of the swing. |
| 35264 | 3 | set_camera | r_L1_teras | max_tries: r_L1_teras was edited 3 times in this round | Reframe the terrace so the full armchair-and-side-table group is in frame instead of the foreground chair being cut off (fixes a:F13). |
| 35265 | 3 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B07QD6TXWS: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh of nightstand f_L0_034 with a real library model (Rivet Claremont nightstand, modern minimal) to fix a:F236. |
| 35266 | 3 | retype_piece | f_L-1_022 | retype: tall_cabinet is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Give the untyped 5.54 x 0.60 m drawn piece a type that fits its size and the living room to clear the NR finding. |
| 35274 | 3 | swap_model | f_L0_033 | max_tries: f_L0_033 was edited 3 times in this round | Replace the parametric mesh of nightstand f_L0_033 with a real library model (AmazonBasics 2-drawer bedside, modern minimal) to fix a:F235. |
| 35275 | 3 | swap_model | f_L1_022 | memory: the same edit was rejected in round 3: acceptance: pin_refused: f_L1_022: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Toilet f_L1_022 floats +0.200 m above its floor and was built below library level; swap to a real product model that sits on the floor. |
| 35276 | 3 | swap_model | f_L0_034 | max_tries: f_L0_034 was edited 3 times in this round | Replace the parametric mesh of nightstand f_L0_034 with a real library model (AmazonBasics 1-drawer 1-shelf bedside, modern minimal) to fix a:F236. |
| 35284 | 3 | fix_fixture | f_L0_003 | fixture_place: f_L0_003: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L0_007) | Door d_L0_007 swings into the washbasin on one hinge side; move it up to 0.5 m out of the swing. |
| 36136 | 4 | set_camera | ext_1 | the camera stands inside the building (level L-1), the camera stands under the roof, eye height 4.94 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.21 m), the ground at (0, 0) is at z -3.34 m: use z -1.84 to -1.64 for an eye-level view | Argus: The exterior camera view is obstructed by a car and a wall, making the house invisible. The camera needs to be repositioned to a clear vantage point showing the facade or entrance. (fixes a:F21) |
| 36137 | 4 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_025, win_L1_001 (win_L1_001 not in r_L1_banyo: name its pieces, doors or windows) | Argus: The camera frame is entirely black and empty, indicating it is placed outside the room or aimed at a wall. It needs to be repositioned inside the bathroom to show the fixtures. (fixes a:F22) |
| 36138 | 4 | swap_model | f_L0_021 | lower_quality: f_L0_021: hssd_24260cc2eff93ee6c74f6db6beb1c5137b9d8bcd is rated 3.0 against 4.0 of the current model abo_B0154VUESC: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The room is 14.1 m2; the 1.55 m bed leaves only 0.37 m on the left. A 1.45 m bed frees 0.47 m more, and with the headboard against the wall the clearance can reach 0.60 m. Move attempts failed because the headboard kept standing in the room (fixes a:F65) |
| 36139 | 4 | swap_model | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.17 m free in front, needs ≥ 0.80 m) | Argus: The 0.60 m deep wardrobe leaves only 0.17 m in front. A 0.57 m deep model frees 0.03 m, and combined with a slight reposition along the wall the 0.80 m aisle can be met. Move attempts failed because the back kept leaving the wall. (fixes a:F66) |
| 36140 | 4 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | Argus: Same cause as F65: the 1.55 m bed in a 14.0 m2 room leaves 0.37 m on the right. A 1.45 m bed frees enough for the 0.60 m clearance. (fixes a:F67) |
| 36141 | 4 | swap_model | f_L0_011 | no_change: f_L0_011 already uses the model abo_B07B3XXD3P | Argus: Same cause as F66: the 0.60 m deep wardrobe leaves 0.17 m in front. A 0.57 m deep model helps meet the 0.80 m aisle. (fixes a:F68) |
| 36142 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding G3:f_L1_031 is still there after the edit (armchair f_L1_031 is 12° off the table_coffee f_L1_023 (needs ≤ 30°) at 2.73 m (needs ≤ 2.50 m)); 3 more kept | Argus: The sofa's front is blocked by f_L1_017. The swap_model attempt was refused because the asset was removed. A room relayout can move f_L1_017 out of the sofa's front zone. (fixes a:F69) |
| 36143 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: F4 f_L1_110: armchair stands behind the back of f_L1_018, looking at it | Argus: The armchair faces the back of f_L1_018. A relayout will reorient it to face the group. (fixes a:F72) |
| 36144 | 4 | relayout_room | r_L-1_mutfak | no_place: r_L-1_mutfak relayout: no place passes the checks (dining: no place passes the checks) | Argus: The aisle is 0.55 m, needs 0.90 m. The set_camera attempt was refused. A relayout of the kitchen pieces can free the aisle. (fixes a:F75) |
| 36145 | 4 | relayout_room | r_L-1_mutfak_2 | no_place: r_L-1_mutfak_2 relayout: no place passes the checks (dining: no place passes the checks) | Argus: Same cause as F75 in the duplicate room. A relayout can free the aisle. (fixes a:F76) |
| 36146 | 4 | swap_model | f_L0_019 | acceptance: finding G5:f_L0_019 is still there after the edit (bed_double f_L0_019: 0.56 m free along the right side, needs ≥ 0.60 m) | Argus: The bed leaves 0.53 m on the left, needs 0.60 m. The relayout was refused (no place fits). A 1.45 m bed frees 0.10 m more, which should meet the clearance. (fixes a:F79) |
| 36147 | 4 | swap_model | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Argus: Same cause as F79 in the duplicate room. A 1.45 m bed frees enough for the 0.60 m clearance. (fixes a:F80) |
| 36148 | 4 | fix_fixture | f_L-1_008 | no_change: f_L-1_008: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The stove is drawn 0.06 m off its wall with its back parallel to it; it belongs on the wall. fix_fixture without a centre moves it to the nearest valid spot, closing the gap. (fixes a:F122) |
| 36149 | 4 | fix_fixture | f_L-1_017 | no_change: f_L-1_017: nothing to fix (size within the real range, inside the room and off the doors) | Argus: Same drawing gap as F122 in the twin kitchen (r_L-1_mutfak_2); the stove belongs on its wall. fix_fixture without a centre moves it to the nearest valid spot. (fixes a:F123) |
| 36150 | 4 | fix_fixture | f_L0_014 | memory: the same edit was rejected in round 1: no_change: f_L0_014: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower stands 0.10 m off its wall with its back parallel to it; it belongs on the wall. The earlier refusals were about size (within range) and a no-op, not about the wall gap, so a plain fix_fixture (no centre) to the nearest valid spo (fixes a:F124) |
| 36151 | 4 | fix_fixture | f_L-1_051 | no_change: f_L-1_051: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet's centre is 0.33 m from the side wall/fixture, under the 0.38 m minimum. Model swaps were refused (fit rules), so the fix is to reposition the toilet to the nearest valid spot that restores the side clearance. (fixes a:F125) |
| 36152 | 4 | fix_fixture | f_L-1_056 | no_change: f_L-1_056: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower has only 0.28 m clear in front, under the 0.53 m minimum. fix_fixture without a centre moves it to the nearest valid spot that restores the front clearance. (fixes a:F126) |
| 36153 | 4 | fix_fixture | f_L-1_052 | no_change: f_L-1_052: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet's centre is 0.33 m from the side wall/fixture on its left, under the 0.38 m minimum. Model swaps were refused, so repositioning to the nearest valid spot restores the clearance. (fixes a:F127) |
| 36154 | 4 | fix_fixture | f_L-1_055 | no_change: f_L-1_055: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower has only 0.28 m clear in front, under the 0.53 m minimum. fix_fixture without a centre moves it to the nearest valid spot that restores the front clearance. (fixes a:F128) |
| 36158 | 4 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_059 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Argus: The hall's shoe cabinet is not visible in the render, so the room reads as an empty wall; re-posing the camera to include the cabinet restores the anchor. (fixes a:F150) |
| 36160 | 4 | add_camera | ext_9 | the camera stands inside the building b2 (another building on the plot), eye height 0.29 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.21 m), the ground at (0, 30) is at z 1.31 m: use z 2.81 to 3.01 for an eye-level view, no eye-level view fits the free stretch on the view line from the target: (0.00, 12.40) to (0.00, 18.20), 12.4-18.2 m from the target (a building stands beyond it): a level 26 mm camera at eye height at its far end (0.00, 18.20) frames no view: the building spans 1.20 of the frame width (it does not fit); a level eye-level view of the whole building stands about 26.0 m from the target; whether this facade gets a frontal view is a user decision (docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch | Argus: No camera currently shows the +y entrance facade frontally; adding an exterior camera in front of it (clear of the other building b2 that blocked the previous attempt) satisfies the requirement. (fixes a:F168) |
| 36162 | 4 | swap_model | f_L-1_056 | acceptance: pin_refused: f_L-1_056: hssd_c878d6d2cca3590cb1e1b7e33642a8f505a7feef: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current shower/bath module renders as a bare tub with no taps or fittings; swapping to a complete minimal/modern shower model from the allowed list makes the bathroom read as designed. (fixes a:F173) |
| 36163 | 4 | set_camera | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 2: show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_ | Argus: The camera does not show door d_L0_002, which it is required to; re-aiming it to show the door fixes the finding. (fixes a:F174) |
| 36164 | 4 | add_camera | ext_10 | eye height -0.07 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.21 m), the ground at (0, 32) is at z 1.67 m: use z 3.17 to 3.37 for an eye-level view | Argus: The previous add_camera was refused because the camera stood inside building b2; placing the new camera farther out (y=32) clears the other building and gives the required frontal entrance view. (fixes a:F175) |
| 36165 | 4 | set_material | plot_wall | memory: the same edit was rejected in round 2: plot_wall: stone_wall_ashlar is another stone than the house's base stone_wall_ledgestone: one stone per house (the plinth, the plot walls and the facade's base match; UL204) | Argus: The retaining wall is a bare concrete slab that clashes with the stone facade; setting the plot_wall slot to a stone look makes it read as finished and consistent. (fixes a:F176) |

Rolled back (the refit refused them): #1024 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0), #1026 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #1030 move_piece (locked check: f_L1_010: moved 0.300 m by the agent (> 0.3 m)), #1055 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0).

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F7 | critical | f_L1_015 | r_L1_banyo | - | drawn_layout | 1, 2, 3, 4 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| F7 | critical | f_L1_016 | r_L1_banyo_2 | - | drawn_layout | 1, 2, 3, 4 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| F9 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| F9 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| G8 | minor | f_L-1b_055 | r_L-1b_salon_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1b_056 | r_L-1b_salon | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| M13 | minor | f_L-1_099 | r_L-1_mutfak_2 | fit | kitchen_design | 1, 2, 3, 4 | the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit composes them of real units on the base joints (modules.plan_wall_run); the build cuts them at the windows of the building as built. No agent tool builds a hood or splits a wall cabinet, so the finding is reported to the fit |
| M15 | minor | spk_001 | - | site | site_grading | 1, 2, 3, 4 | the garden on the slope is graded by code (wenart/blender/grading.py: terraces at one level per side and planted, banks of at most 1:3 / 1:2, flights of solid treads with cheek walls and a landing, paths level across and stepped, walls in the house's base stone with a coping, the floors by use); no agent tool changes the terrain, so the finding is reported to the site stage |
| M17 | minor | r_L-1_salon | r_L-1_salon | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon_2 | r_L-1_salon_2 | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M21 | minor | f_L1_019 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | f_L1_020 | r_L1_oyun_aktivite_ve_dinlenme_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_banyo_2 | r_L0_e_banyo_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo | r_L1_banyo | layout | room_use | 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo_2 | r_L1_banyo_2 | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M29 | major | d_L1_004 | - | openings | opening_style | 3, 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q3 | critical | r_L1_koridor | r_L1_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L1_koridor_2 | r_L1_koridor_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q7 | minor | d_L0_005 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | major | w_L-1_001 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | critical | dec_L1_036 | r_L1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | critical | dec_L1_040 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_089 | r_L-1_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_105 | r_L-1_koridor_2 | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_106 | r_L-1_koridor_2 | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_108 | r_L-1_koridor_2 | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_054 | r_L0_koridor | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_055 | r_L0_koridor_2 | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_056 | r_L0_koridor_2 | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_057 | r_L0_koridor | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_058 | r_L0_koridor_2 | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_059 | r_L0_koridor | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_020 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_061 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | facade | 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | facade | 2, 3, 4 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L-1_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L-1_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | d_L1_006 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L-1_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_001 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_002 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_003 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_004 | - | - | scale | 1, 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L1_001 | - | - | scale | 2, 3, 4 | storey and door sizes come from the drawings |
| X5 | minor | win_L1_002 | - | - | scale | 2, 3, 4 | storey and door sizes come from the drawings |
| lighting_dark | major | cam_r_L0_e_banyo_2 | r_L0_e_banyo | - | lighting_beyond_cap | 1 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1_salon_2 | cut | 3 | 22936 | 32768 |
| 1 | r_L-1b_salon | cut | 5 | 28810 | 32768 |
| 1 | r_L-1b_salon_2 | cut | 1 | 9020 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 2 | 11468 | 32768 |
| 2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cut | 1 | 17202 | 32768 |
| 2 | building | cut | 5 | 6564 | 32768 |
| 2 | r_L-1b_salon | cut | 1 | 8016 | 32768 |
| 3 | building | cut | 9 | 13193 | 32768 |
| 3 | r_L-1b_salon_2 | cut | 1 | 9457 | 32768 |

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
| f_L-1_031 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1_031 slightly to reduce the cut with the dining table to within tolerance. |
| f_L-1_039 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge chair f_L-1_039 away from table_dining f_L-1_038 to clear the 0.034 m cut (S2). |
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
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | code (size_snap) | size snap: the drawn armchair 0.64 x 0.57 m is outside its product range (depth 0.57 m is 5 % outside 0.6-1.1 m; nearest real product 0.65 x 0.80 m); nearest real product 0.65 x 0.80 x 0.80 m (small accent chair 65 x 80) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
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
| f_L0_007 | piece | bed_double | r_L0_e_yatak_odasi | adjusted_by_ai | size 2.55 x 2.00 m -> 1.60 x 2.00 m | solver | the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (anchor); moved 0.10 m, sized 1.80 x 2.00 m -> 1.60 x 2.00 m (a real product size) |
| f_L0_008 | piece | bed_double | r_L0_e_yatak_odasi_2 | adjusted_by_ai | size 2.55 x 2.00 m -> 1.60 x 2.00 m | solver | the drawn bed_double f_L0_008 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (anchor); moved 0.10 m, sized 1.80 x 2.00 m -> 1.60 x 2.00 m (a real product size) |
| f_L0_009 | piece | wardrobe | r_L0_yatak_odasi_3 | adjusted_by_ai | - | architect | wardrobe f_L0_009: 0.17 m free in front of its doors or drawers (f_L0_029 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Center the wardrobe on the free span s2 to open the 0.80 m front clearance (G13). |
| f_L0_011 | piece | wardrobe | r_L0_yatak_odasi_4 | adjusted_by_ai | - | architect | wardrobe f_L0_011: 0.17 m free in front of its doors or drawers (f_L0_028 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred, adjusted_by_ai | - | code (back_gap) | shower f_L0_013: its back stood 0.10 m off its wall, parallel to it (a drawing gap): moved 0.08 m back onto the wall (plan crop recognition/reading/f_L0_013_ctx.png) |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred, adjusted_by_ai | - | code (bath_details.shower_entry) | f_L0_014: its front stood on a wall, its left side open: the way in turned to that side (0 deg; UL201) |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_001 (the answer to AI.move_piece:f_L0_019) |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_004 (the answer to AI.move_piece:f_L0_020) |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred | - | - | bed_double: the same drawn block (the same strokes (22 INSERT here, within 2%)) and footprint (1.90 x 1.55 m, within 0.01 m) as f_L0_019, f_L0_020 (typed bed_double): one block, one type; front: its back stands on the only side on a wall |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_021 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m); front: its back stands on the only side on a wall |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Resize wardrobe height from 2.99m to standard 2.1m to fix S4 size finding (height outside 1.50-2.45m range). |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred | - | - | wardrobe: the same footprint (3.11 x 0.60 m) as f_L0_023 in the twin room r_L0_e_yatak_odasi (mirrored centre within 0.02 m); front: standing in a corner: its long side on the wall is the back |
| f_L0_025 | piece | bathtub | r_L0_banyo | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) at the same plan position as f_L-1_056 on level L-1 (within 0.01 m); front: the free side facing the most room is the front |
| f_L0_026 | piece | bathtub | r_L0_banyo_2 | inferred | - | - | bathtub: the same footprint (1.83 x 0.80 m) as f_L0_025 in the twin room r_L0_banyo (mirrored centre within 0.02 m); front: the free side facing the most room is the front |
| f_L0_027 | piece | desk | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_035 stands in front; plan crop recognition/crops/sym_L0_009_ctx.png |
| f_L0_028 | piece | desk | r_L0_yatak_odasi_4 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_036 stands in front; plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_029 | piece | desk | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_037 stands in front; plan crop recognition/crops/sym_L0_011_ctx.png |
| f_L0_030 | piece | desk | r_L0_yatak_odasi | inferred, adjusted_by_ai | size 1.45 x 0.91 m -> 1.45 x 0.60 m | code (reading.desk_chair) | a 1.45 x 0.91 m desk symbol holds the chair drawn in front of it (CLAUDE.md: a table footprint that includes its chairs): the desk keeps 0.60 m at its wall, the chair f_L0_038 stands in front; plan crop recognition/crops/sym_L0_012_ctx.png |
| f_L0_031 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_013_ctx.png); then: the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.01 m |
| f_L0_032 | piece | nightstand | r_L0_e_yatak_odasi | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_007's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_014_ctx.png); then: the drawn bed_double f_L0_007 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.05 m |
| f_L0_033 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the left side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.13 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_015_ctx.png); then: the drawn bed_double f_L0_008 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.01 m |
| f_L0_034 | piece | nightstand | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> nightstand | code, then solver (nightstand_symbol) | nightstand: a drawn floor_lamp of a nightstand's size (0.50 x 0.45 m) at the right side of the drawn bed_double f_L0_008's head (back 0.00 m from the headboard line, -0.00 m from the bed side; nightstand_gap 0.30 m): the bed's nightstand drawn with its table lamp, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png); then: the drawn bed_double f_L0_008 group is re-solved on request (drawn_group): re-solved with its sleeping_double group as one unit around the drawn anchor (partner); moved 0.05 m |
| f_L1_003 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_020, f_L1_023): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_019, f_L1_024): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_006 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The chair's model (white spindle, cheaper style) does not go with the round pedestal table or the rest of the room. A same-size modern/scandinavian chair is offered; swapping the model fixes the set mismatch. (fixes a:F341) |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_015 | piece | washbasin | r_L1_banyo | adjusted_by_ai | - | architect | moved 0.05 m along its wall to the nearest free place, clear of d_L1_004 (the answer to F2:d_L1_004) |
| f_L1_016 | piece | washbasin | r_L1_banyo_2 | adjusted_by_ai | - | architect | moved 0.05 m along its wall to the nearest free place, clear of d_L1_005 (the answer to F2:d_L1_005) |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | bathtub | r_L1_banyo | inferred, adjusted_by_ai | - | code (build.shower_headroom) | f_L1_025: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200); its shower model module:shower:bath_set left out (the bathtub is built as a bathtub) |
| f_L1_026 | piece | bathtub | r_L1_banyo_2 | inferred, adjusted_by_ai | - | code (build.shower_headroom) | f_L1_026: the ceiling over it is 0.81 m high, under the 2.10 m a walk-in shower stands in: the bathtub of the drawing again (a bath fits under a slope; UL200); its shower model module:shower:bath_set left out (the bathtub is built as a bathtub) |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The armchair's model (teal, different era) clashes with the room's brown sofa set. A same-size minimal/modern/scandinavian armchair is offered; swapping the model fixes the set mismatch without moving the piece. (fixes a:F339) (plan crop recognition/crops/sym_L1_008_ctx.png) |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Armchair f_L1_032 is 2.73 m from coffee table f_L1_024 (needs ≤ 2.50 m); moving it 0.3 m NE toward the table closes the gap to fix G3. (plan crop recognition/crops/sym_L1_010_ctx.png) |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 180 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x975ffc83_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: the same footprint (1.09 x 0.40 m) as f_L1_038 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (mirrored centre within 0.02 m) |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the black mesh corporate office chair with a mid-century open-back swivel chair (marble, scandinavian/minimal) that fits the warm residential bedroom style (D3). (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black leather office chair clashes with the warm bedroom palette; 3dwh_54a792101c925f12bff90916 is a minimal/modern chair that matches the room's style. (fixes a:F334) (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L1_049 | piece | floor_lamp | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_049: the piece is not built |
| f_L1_054 | piece | shoe_cabinet | r_L1_koridor | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_054: the piece is not built |
| f_L1_059 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The current model has a back/arm standing 2.4 cm from the seat (over the 5 mm tolerance), so the rests look apart from the sitting. A same-size modern/scandinavian armchair is offered; swapping the model fixes the proportion defect. The rot (fixes a:F347) |
| f_L1_105 | piece | armchair | r_L1_teras_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The potted-plant/terrace pieces read as generic placeholders; swapping to a higher-detail minimal/modern model from the allowed list improves the terrace styling. (fixes a:F170) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
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
| 3 | cam_r_L-1_koridor_2_1 | ![](agent/r3_cam_r_L-1_koridor_2_1_before.jpg) | ![](agent/r3_cam_r_L-1_koridor_2_1_after.jpg) |
| 3 | cam_r_L-1_mutfak_1 | ![](agent/r3_cam_r_L-1_mutfak_1_before.jpg) | ![](agent/r3_cam_r_L-1_mutfak_1_after.jpg) |
| 3 | cam_r_L0_koridor_1 | ![](agent/r3_cam_r_L0_koridor_1_before.jpg) | ![](agent/r3_cam_r_L0_koridor_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_1 | ![](agent/r3_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_1_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_2 | ![](agent/r3_cam_r_L0_yatak_odasi_2_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_2_after.jpg) |
| 3 | cam_r_L0_yatak_odasi_3 | ![](agent/r3_cam_r_L0_yatak_odasi_3_before.jpg) | ![](agent/r3_cam_r_L0_yatak_odasi_3_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 3 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r3_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 3 | cam_r_L1_teras_1 | ![](agent/r3_cam_r_L1_teras_1_before.jpg) | ![](agent/r3_cam_r_L1_teras_1_after.jpg) |
| 3 | cam_r_L1_teras_2 | ![](agent/r3_cam_r_L1_teras_2_before.jpg) | ![](agent/r3_cam_r_L1_teras_2_after.jpg) |
| 3 | cam_r_L1_teras_3 | ![](agent/r3_cam_r_L1_teras_3_before.jpg) | ![](agent/r3_cam_r_L1_teras_3_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_e_banyo_1 | ![](agent/r4_cam_r_L0_e_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_e_banyo_1_after.jpg) |
| 4 | cam_r_L0_yatak_odasi_1 | ![](agent/r4_cam_r_L0_yatak_odasi_1_before.jpg) | ![](agent/r4_cam_r_L0_yatak_odasi_1_after.jpg) |
| 4 | ext_1 | ![](agent/r4_ext_1_before.jpg) | ![](agent/r4_ext_1_after.jpg) |
| 4 | ext_2 | ![](agent/r4_ext_2_before.jpg) | ![](agent/r4_ext_2_after.jpg) |
| 4 | ext_3 | ![](agent/r4_ext_3_before.jpg) | ![](agent/r4_ext_3_after.jpg) |
| 4 | ext_5 | ![](agent/r4_ext_5_before.jpg) | ![](agent/r4_ext_5_after.jpg) |
| 4 | ext_7 | ![](agent/r4_ext_7_before.jpg) | ![](agent/r4_ext_7_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- cam_r_L-1_banyo_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L-1_koridor_2_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L1_koridor_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- final/top_L-1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L-1_plan_7.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_7.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_7.jpg
