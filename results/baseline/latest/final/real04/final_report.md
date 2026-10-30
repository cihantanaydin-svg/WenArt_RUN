# Final report: real04

34 views: 0 polished, 34 Cycles (error 10, gate_validation 5, not_run 2, room 17). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 34 |
| interior / exterior views | 29 / 5 |
| variant | base |
| polished | 0 |
| Cycles | 34 (error 10, gate_validation 5, not_run 2, room 17) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 37 |
| needs_review views | 19 |
| unverified pieces in view (sum over views) | 44 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 14 |
| exposure | -7.67 .. +2.50 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 24 view(s), -4 .. 0 EV |
| interior glazing pull | - |
| camera policy | agent 7, m5 5, search 22 |
| camera score (min / mean / max) | 0.07 / 3.57 / 4.73 |
| rooms by number of views | 1 with 0, 6 with 1, 1 with 2, 7 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 7.7 min / 6.8 min / 115.9 s |
| seconds: polish / gate / check | 3.5 min / 23.1 s / 40.5 min |
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

160 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 35 rooms; 367 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- camera cam_r_L-1_koridor_2_1: no free camera point in the room; no point clear of the walls and the tall proxies, camera at the room's inner point INSIDE a proxy
- camera cam_r_L1_banyo_1: no free camera point in the room; camera at the room's inner point; moved to the nearest point with 0.3 m of headroom under the sloped ceiling (1.55 m high there); blocked unavoidable
- 2 exterior view(s) dropped, no camera place worked: ext_4, ext_6
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.883 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 19 piece(s) moved beyond the tolerance, 70 locked-rule violation(s)
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
| cam_r_L-1_banyo_1 | r_L-1_banyo | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.33 | - | agent | D4 A5 | 1 | no | [preview](cam_r_L-1_banyo_1_final_preview.jpg) [plan](cam_r_L-1_banyo_1_plan.jpg) |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | L-1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.00 | - | search 0.07 | D1 A4 | 0 | no | [preview](cam_r_L-1_koridor_2_1_final_preview.jpg) [plan](cam_r_L-1_koridor_2_1_plan.jpg) |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.00 | -3 | search 4.54 | D5 A3 | 0 | no | [preview](cam_r_L-1_mutfak_1_final_preview.jpg) [plan](cam_r_L-1_mutfak_1_plan.jpg) |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.33 | -3 | search 3.83 | D5 A2 | 0 | yes | [preview](cam_r_L-1_mutfak_2_final_preview.jpg) [plan](cam_r_L-1_mutfak_2_plan.jpg) |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | L-1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.83 | -3 | search 4.13 | D5 A4 | 0 | no | [preview](cam_r_L-1_mutfak_3_final_preview.jpg) [plan](cam_r_L-1_mutfak_3_plan.jpg) |
| cam_r_L-1_salon_1 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.17 | -4 | search 3.66 | D8 A6 | 4 | no | [preview](cam_r_L-1_salon_1_final_preview.jpg) [plan](cam_r_L-1_salon_1_plan.jpg) |
| cam_r_L-1_salon_2 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.48 | D12 A7 | 3 | no | [preview](cam_r_L-1_salon_2_final_preview.jpg) [plan](cam_r_L-1_salon_2_plan.jpg) |
| cam_r_L-1_salon_3 | r_L-1_salon | L-1 | cycles | room | - | - | info | - | - | +1.83 | -4 | search 3.64 | D10 A7 | 4 | no | [preview](cam_r_L-1_salon_3_final_preview.jpg) [plan](cam_r_L-1_salon_3_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.50 | - | agent | D3 A4 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +2.50 | - | agent | D2 A2 | 1 | no | [preview](cam_r_L0_e_banyo_1_final_preview.jpg) [plan](cam_r_L0_e_banyo_1_plan.jpg) |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | L0 | cycles | not_run | - | - | info | - | - | +0.33 | - | agent | D4 A2 | 1 | yes | [preview](cam_r_L0_e_banyo_2_final_preview.jpg) [plan](cam_r_L0_e_banyo_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.83 | 0 | search 4.66 | D5 A10 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_1_plan.jpg) |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.33 | - | search 4.20 | D4 A2 | 1 | yes | [preview](cam_r_L0_e_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_2_plan.jpg) |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | L0 | cycles | room | - | - | info | - | - | -0.83 | -1 | search 4.59 | D3 A8 | 0 | no | [preview](cam_r_L0_e_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_e_yatak_odasi_3_plan.jpg) |
| cam_r_L0_koridor_1 | r_L0_koridor | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +2.33 | - | search 3.06 | D3 A3 | 0 | yes | [preview](cam_r_L0_koridor_1_final_preview.jpg) [plan](cam_r_L0_koridor_1_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.00 | -4 | agent | D4 A7 | 3 | yes | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +2.00 | -4 | search 3.98 | D3 A6 | 2 | yes | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | info | - | - | +1.83 | -4 | search 4.56 | D4 A7 | 3 | yes | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +2.17 | -4 | agent | D6 A2 | 4 | yes | [preview](cam_r_L0_yatak_odasi_3_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_1_plan.jpg) |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.33 | -3 | search 4.61 | D6 A4 | 4 | yes | [preview](cam_r_L0_yatak_odasi_3_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | L0 | cycles | room | - | - | info | - | - | +1.50 | -4 | search 4.73 | D4 A3 | 4 | no | [preview](cam_r_L0_yatak_odasi_3_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.17 | - | search 1.60 blocked | D2 A2 | 0 | yes | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_koridor_1 | r_L1_koridor | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.33 | - | agent | D3 A3 | 0 | yes | [preview](cam_r_L1_koridor_1_final_preview.jpg) [plan](cam_r_L1_koridor_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.17 | - | search 3.33 | D7 A5 | 2 | no | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.17 | -1 | search 4.05 | D7 A4 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_plan.jpg) |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | cycles | room | - | - | info | - | - | +0.33 | -2 | search 3.94 | D9 A2 | 1 | yes | [preview](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_final_preview.jpg) [plan](cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_plan.jpg) |
| cam_r_L1_teras_1 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.33 | 0 | search 2.35 | D1 A5 | 0 | no | [preview](cam_r_L1_teras_1_final_preview.jpg) [plan](cam_r_L1_teras_1_plan.jpg) |
| cam_r_L1_teras_2 | r_L1_teras | L1 | cycles | room | - | - | info | - | - | -4.17 | 0 | search 2.83 | D2 A4 | 0 | yes | [preview](cam_r_L1_teras_2_final_preview.jpg) [plan](cam_r_L1_teras_2_plan.jpg) |
| cam_r_L1_teras_3 | r_L1_teras | L1 | cycles | not_run | - | - | info | - | - | -4.17 | 0 | search 2.75 | D1 A3 | 0 | yes | [preview](cam_r_L1_teras_3_final_preview.jpg) [plan](cam_r_L1_teras_3_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.00 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 blocked | D8 | 1 | yes | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
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
| r_L0_banyo | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_1 |
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
| cam_r_L-1_mutfak_2 | cycles | cross-check misplaced | d_L-1_003 | door | - | from_documents | deneme1.dwg INSERT:365E2/1,INSERT:365E2/0 vector 0.95 | yes | 100 % of its pixels > 0.10 m outside the drawing, 75024 px |
| cam_r_L0_e_banyo_2 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 100 % of its pixels > 0.10 m outside the drawing, 4564 px |
| cam_r_L0_e_banyo_2 | cycles | cross-check misplaced | d_L0_002 | door | - | from_documents | deneme1.dwg INSERT:2DDF1/1,INSERT:2DDF1/0,LWPOLYLINE:2DDF5 vector 0.95 | yes | 61 % of its pixels > 0.10 m outside the drawing, 606585 px |
| cam_r_L0_e_yatak_odasi_2 | cycles | cross-check misplaced | d_L0_001 | door | - | from_documents | deneme1.dwg INSERT:2DDF6/1,INSERT:2DDF6/0 vector 0.95 | yes | 71 % of its pixels > 0.10 m outside the drawing, 345190 px |
| cam_r_L0_koridor_1 | cycles | cross-check misplaced | d_L0_007 | door | - | from_documents | deneme1.dwg INSERT:2DDDE/1,INSERT:2DDDE/0 vector 0.95 | yes | 23 % of its pixels > 0.10 m outside the drawing, 88659 px |
| cam_r_L0_yatak_odasi_1 | cycles | cross-check misplaced | f_L0_019 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDF7/0,INSERT:2DDF7/1,INSERT:2DDF7/10,INSERT:2DDF7/11,INSERT:2DDF7/12,INSERT:2DDF7/13,INSERT:2DDF7/14,INSERT:2DDF7/15,INSERT:2DDF7/16,INSERT:2DDF7/17,INSERT:2DDF7/18,INSERT:2DDF7/19,INSERT:2DDF7/2,INSERT:2DDF7/20,INSERT:2DDF7/21,INSERT:2DDF7/3,INSERT:2DDF7/4,INSERT:2DDF7/5,INSERT:2DDF7/6,INSERT:2DDF7/7,INSERT:2DDF7/8,INSERT:2DDF7/9 vector 0.90; deneme1.dwg INSERT:2DDF7/0,INSERT:2DDF7/1,INSERT:2DDF7/10,INSERT:2DDF7/11,INSERT:2DDF7/12,INSERT:2DDF7/13,INSERT:2DDF7/14,INSERT:2DDF7/15,INSERT:2DDF7/16,INSERT:2DDF7/17,INSERT:2DDF7/18,INSERT:2DDF7/19,INSERT:2DDF7/2,INSERT:2DDF7/20,INSERT:2DDF7/21,INSERT:2DDF7/3,INSERT:2DDF7/4,INSERT:2DDF7/5,INSERT:2DDF7/6,INSERT:2DDF7/7,INSERT:2DDF7/8,INSERT:2DDF7/9 inferred 0.60; +1 more | yes | 15 % of its pixels > 0.10 m outside the drawing, 216336 px |
| cam_r_L0_yatak_odasi_2 | cycles | cross-check misplaced | f_L0_019 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDF7/0,INSERT:2DDF7/1,INSERT:2DDF7/10,INSERT:2DDF7/11,INSERT:2DDF7/12,INSERT:2DDF7/13,INSERT:2DDF7/14,INSERT:2DDF7/15,INSERT:2DDF7/16,INSERT:2DDF7/17,INSERT:2DDF7/18,INSERT:2DDF7/19,INSERT:2DDF7/2,INSERT:2DDF7/20,INSERT:2DDF7/21,INSERT:2DDF7/3,INSERT:2DDF7/4,INSERT:2DDF7/5,INSERT:2DDF7/6,INSERT:2DDF7/7,INSERT:2DDF7/8,INSERT:2DDF7/9 vector 0.90; deneme1.dwg INSERT:2DDF7/0,INSERT:2DDF7/1,INSERT:2DDF7/10,INSERT:2DDF7/11,INSERT:2DDF7/12,INSERT:2DDF7/13,INSERT:2DDF7/14,INSERT:2DDF7/15,INSERT:2DDF7/16,INSERT:2DDF7/17,INSERT:2DDF7/18,INSERT:2DDF7/19,INSERT:2DDF7/2,INSERT:2DDF7/20,INSERT:2DDF7/21,INSERT:2DDF7/3,INSERT:2DDF7/4,INSERT:2DDF7/5,INSERT:2DDF7/6,INSERT:2DDF7/7,INSERT:2DDF7/8,INSERT:2DDF7/9 inferred 0.60; +1 more | yes | 14 % of its pixels > 0.10 m outside the drawing, 440250 px |
| cam_r_L0_yatak_odasi_3 | cycles | cross-check misplaced | f_L0_019 | bed_double | - | from_documents | deneme1.dwg INSERT:2DDF7/0,INSERT:2DDF7/1,INSERT:2DDF7/10,INSERT:2DDF7/11,INSERT:2DDF7/12,INSERT:2DDF7/13,INSERT:2DDF7/14,INSERT:2DDF7/15,INSERT:2DDF7/16,INSERT:2DDF7/17,INSERT:2DDF7/18,INSERT:2DDF7/19,INSERT:2DDF7/2,INSERT:2DDF7/20,INSERT:2DDF7/21,INSERT:2DDF7/3,INSERT:2DDF7/4,INSERT:2DDF7/5,INSERT:2DDF7/6,INSERT:2DDF7/7,INSERT:2DDF7/8,INSERT:2DDF7/9 vector 0.90; deneme1.dwg INSERT:2DDF7/0,INSERT:2DDF7/1,INSERT:2DDF7/10,INSERT:2DDF7/11,INSERT:2DDF7/12,INSERT:2DDF7/13,INSERT:2DDF7/14,INSERT:2DDF7/15,INSERT:2DDF7/16,INSERT:2DDF7/17,INSERT:2DDF7/18,INSERT:2DDF7/19,INSERT:2DDF7/2,INSERT:2DDF7/20,INSERT:2DDF7/21,INSERT:2DDF7/3,INSERT:2DDF7/4,INSERT:2DDF7/5,INSERT:2DDF7/6,INSERT:2DDF7/7,INSERT:2DDF7/8,INSERT:2DDF7/9 inferred 0.60; +1 more | yes | 16 % of its pixels > 0.10 m outside the drawing, 335592 px |
| cam_r_L0_yatak_odasi_3_1 | cycles | cross-check misplaced | d_L0_006 | door | - | from_documents | deneme1.dwg INSERT:2DDE5/1,INSERT:2DDE5/0,LWPOLYLINE:2DE07 vector 0.95 | yes | 65 % of its pixels > 0.10 m outside the drawing, 345586 px |
| cam_r_L0_yatak_odasi_3_2 | cycles | cross-check misplaced | d_L0_006 | door | - | from_documents | deneme1.dwg INSERT:2DDE5/1,INSERT:2DDE5/0,LWPOLYLINE:2DE07 vector 0.95 | yes | 70 % of its pixels > 0.10 m outside the drawing, 169049 px |
| cam_r_L1_banyo_1 | cycles | cross-check misplaced | d_L1_004 | door | - | from_documents | deneme1.dwg INSERT:2F799/1,INSERT:2F799/0 vector 0.95; door_states inferred 0.80 | yes | 70 % of its pixels > 0.10 m outside the drawing, 281109 px |
| cam_r_L1_koridor_1 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 44 % of its pixels > 0.10 m outside the drawing, 110490 px |
| cam_r_L1_koridor_1 | cycles | cross-check misplaced | f_L1_098 | armchair | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 8592 px; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 64 % of its pixels > 0.10 m outside the drawing, 22378 px |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | cycles | cross-check misplaced | d_L1_001 | door | - | from_documents | deneme1.dwg INSERT:36D77/1,INSERT:36D77/0 vector 0.95 | yes | 59 % of its pixels > 0.10 m outside the drawing, 21976 px |
| cam_r_L1_teras_2 | cycles | cross-check misplaced | f_L1_094 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 29 px; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_teras_3 | cycles | cross-check in_json_not_rendered | f_L1_093 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | visible 0.92, area 0.158; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_teras_3 | cycles | cross-check in_json_not_rendered | f_L1_094 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | visible 0.68, area 0.043; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_teras_3 | cycles | cross-check in_json_not_rendered | f_L1_095 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | visible 0.69, area 0.145; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_teras_3 | cycles | cross-check misplaced | f_L1_099 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 77537 px; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_teras_3 | cycles | cross-check misplaced | f_L1_100 | potted_plant | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 16988 px; added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_teras_3 | cycles | cross-check misplaced | f_L1_101 | armchair | - | added_by_ai | building.json derived 0.90; building.json derived 0.90; +1 more | yes | 100 % of its pixels > 0.10 m outside the drawing, 113703 px; added_by_ai: render/polish issue, not a document conflict |
| ext_1 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 24 % of its pixels > 0.10 m outside the drawing, 43609 px |
| ext_1 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 16 % of its pixels > 0.10 m outside the drawing, 5636 px |
| ext_2 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 23 % of its pixels > 0.10 m outside the drawing, 46282 px |
| ext_2 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 15 % of its pixels > 0.10 m outside the drawing, 5723 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 33 % of its pixels > 0.10 m outside the drawing, 42677 px |
| ext_5 | cycles | cross-check misplaced | win_L-1_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36603,LWPOLYLINE:36604 vector 0.90 | yes | 27 % of its pixels > 0.10 m outside the drawing, 10292 px |
| ext_5 | cycles | cross-check misplaced | win_L0_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE1C,LWPOLYLINE:2DE1D vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 72 % of its pixels > 0.10 m outside the drawing, 12346 px |
| ext_5 | cycles | cross-check misplaced | win_L0_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2DE19,LWPOLYLINE:2DE1A vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 65 % of its pixels > 0.10 m outside the drawing, 10069 px |
| ext_5 | cycles | cross-check misplaced | win_L0_003 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C1,LWPOLYLINE:2E1C2 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3079 px |
| ext_5 | cycles | cross-check misplaced | win_L0_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:2E1C4,LWPOLYLINE:2E1C5 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 2640 px |
| ext_5 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_3_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 26 % of its pixels > 0.10 m outside the drawing, 7116 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_001 | window | - | from_documents | deneme1.dwg LWPOLYLINE:365F5,LWPOLYLINE:365F6 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 1556 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_002 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A5F,LWPOLYLINE:36A60 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 100 % of its pixels > 0.10 m outside the drawing, 3294 px |
| ext_7 | cycles | cross-check misplaced | win_L-1_004 | window | - | from_documents | deneme1.dwg LWPOLYLINE:36A6D,LWPOLYLINE:36A6E vector 0.90 | yes | 48 % of its pixels > 0.10 m outside the drawing, 14375 px |
| ext_7 | cycles | cross-check misplaced | win_arch_r_L0_yatak_odasi_4_1 | window | - | from_documents | orchestrator/architect_answers.json inferred 0.60 | yes | 51 % of its pixels > 0.10 m outside the drawing, 12220 px |

## Needs review

- cam_r_L-1_mutfak_2: json cross-check misplaced: d_L-1_003
- cam_r_L0_e_banyo_2: json cross-check misplaced: d_L0_001; json cross-check misplaced: d_L0_002
- cam_r_L0_e_yatak_odasi_2: json cross-check misplaced: d_L0_001
- cam_r_L0_koridor_1: json cross-check misplaced: d_L0_007
- cam_r_L0_yatak_odasi_1: json cross-check misplaced: f_L0_019
- cam_r_L0_yatak_odasi_2: json cross-check misplaced: f_L0_019
- cam_r_L0_yatak_odasi_3: json cross-check misplaced: f_L0_019
- cam_r_L0_yatak_odasi_3_1: json cross-check misplaced: d_L0_006
- cam_r_L0_yatak_odasi_3_2: json cross-check misplaced: d_L0_006
- cam_r_L1_banyo_1: json cross-check misplaced: d_L1_004
- cam_r_L1_koridor_1: json cross-check misplaced: d_L1_001; json cross-check misplaced: f_L1_098
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: json cross-check misplaced: d_L1_001
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: json cross-check misplaced: d_L1_001
- cam_r_L1_teras_2: json cross-check misplaced: f_L1_094
- cam_r_L1_teras_3: json cross-check in_json_not_rendered: f_L1_093; json cross-check in_json_not_rendered: f_L1_094; json cross-check in_json_not_rendered: f_L1_095; json cross-check misplaced: f_L1_099; json cross-check misplaced: f_L1_100; json cross-check misplaced: f_L1_101
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
- cam_r_L-1_salon_3: f_L-1_053, f_L-1_061, f_L-1_070, f_L-1_087
- cam_r_L0_e_banyo_1: f_L0_013
- cam_r_L0_e_banyo_2: f_L0_023
- cam_r_L0_e_yatak_odasi_2: f_L0_023
- cam_r_L0_yatak_odasi_1: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_2: f_L0_019, f_L0_030
- cam_r_L0_yatak_odasi_3: f_L0_019, f_L0_030, f_L0_038
- cam_r_L0_yatak_odasi_3_1: f_L0_023, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_2: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L0_yatak_odasi_3_3: f_L0_021, f_L0_029, f_L0_037, win_arch_r_L0_yatak_odasi_3_1
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: f_L1_023, f_L1_031
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
- added f_L-1b_085: floor_lamp 0.40 x 0.40 (confidence -, rule)
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

Reference: source building.json; mode `complete`. 164 of 164 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 145 ok, 19 failed; 59 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

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
| f_L0_007 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_008 | bed_double (bed_double) | 0.10 | 0.00 | yes | - |
| f_L0_009 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_011 | wardrobe (wardrobe) | 0.40 | 0.00 | yes | - |
| f_L0_014 | shower (shower) | 0.76 | 90.00 | no | no longer against wall w_L0_002 (now centre None) |
| f_L1_006 | chair (chair) | 0.30 | 0.00 | - | - |
| f_L1_010 | chair (chair) | 0.27 | 0.00 | - | - |
| f_L1_019 | sofa (sofa) | 0.19 | 0.00 | - | - |

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
- f_L1_006: moved 0.304 m by the agent (> 0.3 m)

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
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: ok; left: unverified | yes |
| ext_7 | aerial | - | - | cycles (gate_validation) | ok | right: unverified | yes |

Dropped views:

| view | kind | sides | reason |
|---|---|---|---|
| ext_4 | corner | left, back | 12.5 m from the building corner, 30 degrees off the back facade: 81% of the view of the building is blocked by trees, the plot wall or another building; 14.5 m from the building corner, 30 degrees off the back facade: 75% of the view of the building is blocked by trees, the plot wall or another building; 16.5 m from the building corner, 30 degrees off the back facade: 57% of the view of the building is blocked by trees, the plot wall or another building; 11.0 m from the building corner, 30 degrees off the back facade: 87% of the view of the building is blocked by trees, the plot wall or another building; 18.5 m from the building corner, 30 degrees off the back facade: 48% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m from the building corner, 30 degrees off the back facade: the building fills 6% of the frame (< 8%); 24.5 m from the building corner, 30 degrees off the back facade: 36% of the view of the building is blocked by trees, the plot wall or another building |
| ext_6 | frontal | back | 17.5 m in front of the back (entrance) facade: inside the copy; 19.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 21.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 16.0 m in front of the back (entrance) facade: inside the copy; 23.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 26.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building; 29.5 m in front of the back (entrance) facade: 100% of the view of the building is blocked by trees, the plot wall or another building |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | plaster_exterior | - | agent | no | agent override (docs/milestone11.md §17.3) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | dark_bronze | - | style | no | style profile exterior.window_frame |
| door | wood_walnut | - | agent | no | agent override (docs/milestone11.md §17.3) |
| paving | paving_stone | - | agent | no | agent override (docs/milestone11.md §17.3) |
| garden | grass | - | agent | no | agent override (docs/milestone11.md §17.3) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | off white | build | yes | plot wall finish not drawn: the facade's look |
| surround | stone_cladding | - | agent | no | agent override (docs/milestone11.md §17.3) |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof mismatch.

Roof heights: built eaves 3,75 m, ridge 6,01 m; drawn eaves 3,75 m (vector), ridge 5,80 m (vector); result mismatch.

## Variants

One building per drawn alternative plan: the base and, for each alternative, the same building with that level replaced. An alternative renders only the rooms it changes, and its exterior views only when its outside differs (otherwise the base views stand for it). Each alternative has its own report in its sub-output (paths below, relative to the project output).

| variant | label | rooms changed | outside | interior views | polished / Cycles | mismatches | report |
|---|---|---|---|---|---|---|---|
| base | Base | - | its own views (this report) | cam_r_L-1_banyo_1, cam_r_L-1_koridor_2_1, cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_banyo_1, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3, cam_r_L0_koridor_1, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3, cam_r_L0_yatak_odasi_3_1, cam_r_L0_yatak_odasi_3_2, cam_r_L0_yatak_odasi_3_3, cam_r_L1_banyo_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3, cam_r_L1_teras_1, cam_r_L1_teras_2, cam_r_L1_teras_3 | 0 / 34 | 0 | - |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | r_L-1b_salon, r_L-1b_salon_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | its own 5 view(s) | cam_r_L-1b_koridor_1, cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3, cam_r_L-1b_salon_1, cam_r_L-1b_salon_2, cam_r_L-1b_salon_3, cam_r_L0_banyo_1, cam_r_L0_e_banyo_1, cam_r_L0_e_banyo_2, cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3_1, cam_r_L1_koridor_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_teras_1, cam_r_L1_teras_2 | 0 / 22 | 0 | variants/l-1b-acik-mutfak/final/final_report.md |

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
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
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
| apron:apron_L-1_1 | 1 | the paved strip at the foot of the glazed facade runs its whole glazing run (win_L-1_001, win_L-1_002): 6.94 m on from the light well of win_L-1_002, 0.8 m deep, on the ground (lesson UL142; inferred) | site |
| area_light | 1 | r_L-1_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo |
| area_light | 1 | r_L-1_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_banyo_2 |
| area_light | 1 | r_L-1_koridor: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor |
| area_light | 1 | r_L-1_koridor_2: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L-1_koridor_2 |
| area_light | 1 | r_L0_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; the room's light rig (2 fixtures) carries the light instead of the invisible ceiling light | rig_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_e_yatak_odasi: agent: Raise room light power x2.22 so cam_r_L0_e_yatak_odasi_2 exposure fits the +3.00 EV cap (finding names x2.22).; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_e_yatak_odasi |
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
| bath_details | 13 | the bathroom details of the piece (UL114, UL123, UL124: LED strips, a flush plate, towels and toiletries, shower fittings) inside its own box, one mesh | furn_f_L-1_051, furn_f_L-1_052, furn_f_L-1_103 |
| bath_items | 8 | the floating vanity's styling (UL114 B3, UL123 B19): part of its one mesh | furn_f_L-1_025, furn_f_L-1_026, furn_f_L0_003 |
| bay_lights | 6 | an LED strip at the top of every bay lights the contents so they read through the see-through front (UL135; a wardrobe LED profile, 1000 lm per metre (UL135)) | furn_f_L0_009, furn_f_L0_010, furn_f_L0_011 |
| bedding | 2 | its cover is flat (relief 0 mm, 135 vertices/m2 on top: under 6 mm or 50; 80% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_019, dress_f_L0_021 |
| bedding | 1 | its cover is flat (relief 5 mm, 249 vertices/m2 on top: under 6 mm or 50; 100% of the middle on the top: under 50%): poorer than our duvet; crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_008 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); crisp cotton, a velvet sham pair, a boucle and a knit cushion, a velvet lumbar, a houndstooth blanket under a fringed knit throw (the reference photo's set) | dress_f_L0_022 |
| car | 1 | library car 3dwh_53630bfe2d05103a88e1a270 ('Car') on the drawn parking spk_001 (parallel bay, 4.65 x 2.10 x 1.40 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_0 |
| car | 1 | library car 3dwh_867427c8bc03ecda3fbb809a ('CAR') on the drawn parking spk_001 (perpendicular bay, 4.75 x 2.10 x 1.45 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_1 |
| car | 1 | library car 3dwh_a21d4bbd6e7b27b084152ccd ('Sports Car - Porsche') on the drawn parking spk_001 (parallel bay, 4.90 x 2.02 x 1.42 m, scaled uniformly; the documents draw the parking, not a car); front +X lay across the car's long side: turned back to -Y (a car's front is an end of its length) | car_spk_001_2 |
| center | 1 | slid 0.24 m off the full-height wardrobe run f_L0_009 (from [1.825, 8.019]; UL182) | dec_L0_041 |
| center | 1 | slid 0.24 m off the full-height wardrobe run f_L0_011 (from [13.348, 8.019]; UL182) | dec_L0_078 |
| chimney | 1 | inferred chimney (modern family): the mirrored dwelling's own, over the twin room r_L-1_salon_2 of r_L-1_salon; top 6.70 m: 0.6 m over the roof within 3 m (its highest point there 6.01 m) and 0.9 m over where it leaves the roof (5.77 m), the 3-2-10 rule of thumb | chimney_2 |
| chimney | 1 | inferred chimney (modern family: a modern pitched-roof house keeps a fireplace or a stove in its living room); no fireplace or flue drawn; over the fireplace wall w_L-1_004 of the living room r_L-1_salon (a solid inner wall stretch of 2.8 m with no door or window); top 6.70 m: 0.6 m over the roof within 3 m (its highest point there 6.01 m) and 0.9 m over where it leaves the roof (5.77 m), the 3-2-10 rule of thumb | chimney_1 |
| climate | 1 | the drawing's language (tr): the climate most of its houses stand in (a guess) (inferred; the species of trees and hedges follow it): banyo, merdiven, mutfak, otopark, yatak | site |
| context | 1 | no context drawn: 159 trees of the mediterranean climate (stone_pine 57, olive 43, cypress 35, plane 24; species inferred) in groups around the site, 89-350 m from the building's centre (the exterior cameras stand within 89 m), with open fields between them so the horizon stays in view (inferred context) | site |
| direction | 1 | the plan of L0 draws the same stair (f_L0_001) with its landing at the east end: the half landing is there, 1.24 m deep | furn_f_L-1_019 |
| direction | 1 | the plan of L0 draws the same stair (f_L0_002) with its landing at the west end: the half landing is there, 1.19 m deep | furn_f_L-1_020 |
| direction | 1 | the plan of L1 draws the same stair (f_L1_001) with its landing at the west end: the half landing is there, 1.19 m deep | furn_f_L0_002 |
| direction | 1 | the plan of L1 draws the same stair (f_L1_002) with its landing at the east end: the half landing is there, 1.24 m deep | furn_f_L0_001 |
| door_frame | 1 | every door is framed (UL122): ours (the parametric door's frame round a bare leaf); architrave on the indoor face(s) [-1] | d_L0_012 |
| door_frame | 16 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1, 1] | d_L-1_001, d_L-1_002, d_L-1_003 |
| door_frame | 1 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1] | d_L0_011 |
| door_handles | 2 | design detail of the documented flush door (black handles on both faces and 3 hinges); not in the documents | d_L1_004_handle, d_L1_005_handle |
| door_handles | 2 | design detail of the documented glazed door (black handles on both faces and 3 hinges); not in the documents | d_L1_003_handle, d_L1_006_handle |
| door_product | 2 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_walnut); not in the documents | d_L1_004, d_L1_005 |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_walnut; glazed: door d_L1_003 opens from r_L1_koridor to the open-air r_L1_teras: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_003 |
| door_product | 1 | design detail of the documented door (the style family's door: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_walnut; glazed: door d_L1_006 opens from r_L1_koridor_2 to the open-air r_L1_teras_2: an outside door (glazed, weather-tight; adjusted_by_ai by code); frame in the windows' finish); not in the documents | d_L1_006 |
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
| height | 4 | no height in the JSON; type height for tv_unit | furn_f_L-1_101, furn_f_L-1_102, furn_f_L1_063 |
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
| library_model | 12 | library inside door hssd_200-5 ('HSSD door 200-5 (0.81 x 2.20 m)') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a horizontal leaf, an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_walnut; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_001, d_L-1_002, d_L0_001 |
| library_model | 2 | library inside door hssd_204-6 ('HSSD door 204-6 (0.93 x 2.20 m)') in 1 panel(s) of 0.80 x 1.80 m (proportions off by 6 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_walnut; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L1_001, d_L1_002 |
| library_model | 2 | library inside door hssd_204-7 ('HSSD door 204-7 (0.86 x 2.40 m)') in 1 panel(s) of 0.81 x 2.85 m (proportions off by 26 %; the documents draw the opening, not its product); the house's glazed inside door family; not a facade family; door style glazed: door glazed (drawn operation swing; a door into the living rooms: a glazed leaf brings daylight into the hall; an architrave and hinges where it is framed (the modern family's door, assumed)), style door wood_walnut; modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | d_L-1_003, d_L-1_004 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 3 panel(s) of 0.72 x 2.55 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_002, win_L0_003 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 4 panel(s) of 0.67 x 2.55 m (proportions off by 7 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L0_001, win_L0_004 |
| library_model | 2 | library window hssd_3753-20 ('HSSD window 3753-20 (0.48 x 1.70 m)') in 8 panel(s) of 0.34 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_arch_r_L0_yatak_odasi_3_1, win_arch_r_L0_yatak_odasi_4_1 |
| library_model | 2 | library window hssd_3753-30 ('HSSD window 3753-30 (1.18 x 1.70 m)') in 5 panel(s) of 0.83 x 1.20 m (proportions off by 0 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L-1_003, win_L-1_004 |
| library_model | 2 | library window hssd_3753-7 ('HSSD window 3753-7 (1.00 x 2.60 m)') in 8 panel(s) of 0.90 x 2.40 m (proportions off by 3 %; the documents draw the opening, not its product); the building's one window family (one of 6 equal families, picked by the house's seed); modern look: audited styles ['minimal', 'modern'] name modern; frames in the style's finish | win_L-1_001, win_L-1_002 |
| light_well:win_L-1_002 | 1 | window sill -2.80 m, ground outside -2.83 m: an open concrete light well 0.8 m deep, 7.59 m wide (no light well drawn) | site |
| light_well:win_L-1_003 | 1 | the terrace sp_001 at -3.00 m lies under the sill -2.10 m: no light well | site |
| light_well:win_L-1_004 | 1 | the terrace sp_002 at -3.00 m lies under the sill -2.10 m: no light well | site |
| modules | 36 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L-1_001, furn_f_L-1_002, furn_f_L-1_003 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| opening_model | 2 | no model of the house's solid inside door family 'HSSD door 200-5 (0.81 x 2.20 m)' fits 0.80 x 1.00 m: the parametric door keeps the house's door language | d_L1_004, d_L1_005 |
| parapet | 1 | roof terrace ro_001: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 0.6 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| parapet_height:ro_002 | 1 | not drawn; the wall stops at the eaves line (0.60 m over the terrace floor) and a railing reaches the 1.00 m guard height | roof |
| passage_lining | 3 | design detail of the documented passage: a lined reveal (jambs and head lining in the trim), no architrave (UL122); not in the documents | o_L0_001_lining, o_L0_002_lining, o_L1_001_lining |
| path:d_L0_011 | 1 | a paved path from the entrance to the front of building copy 1 (it never runs into a building) (inferred) | site |
| path:d_L0_012 | 1 | a paved path from the entrance to the front of building copy 1 (it never runs into a building) (inferred) | site |
| path_grading | 1 | a sloped walk: 0.0 % along (at most 1:12), laid level across (0.3 % of cross fall taken by its edges; inferred) | path_access_spk_001_c0 |
| path_grading | 1 | a sloped walk: 0.0 % along (at most 1:12), laid level across (37.4 % of cross fall taken by its edges; inferred) | path_access_sp_001_c0 |
| path_grading | 1 | a sloped walk: 0.0 % along (at most 1:12), laid level across (9.3 % of cross fall taken by its edges; inferred) | path_access_sp_002_c0 |
| path_grading | 1 | a sloped walk: 3.3 % along (at most 1:12), laid level across (34.4 % of cross fall taken by its edges; inferred) | path_access_sp_002_1 |
| path_grading | 1 | a stepped path: 12 % along is steeper than 1:12, so 2 risers of 0.078 m in 1 flight(s) (2) with level landings, treads 0.42 m, level across, stone step edges (inferred) | path_d_L0_011 |
| path_grading | 1 | a stepped path: 13 % along is steeper than 1:12, so 2 risers of 0.087 m in 1 flight(s) (2) with level landings, treads 0.41 m, level across, stone step edges (inferred) | path_access_spk_001_1 |
| path_grading | 1 | a stepped path: 17 % along is steeper than 1:12, so 2 risers of 0.135 m in 1 flight(s) (2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_d_L0_012 |
| path_grading | 1 | a stepped path: 18 % along is steeper than 1:12, so 3 risers of 0.106 m in 1 flight(s) (3) with level landings, treads 0.37 m, level across, stone step edges (inferred) | path_access_sp_004_0 |
| path_grading | 1 | a stepped path: 32 % along is steeper than 1:12, so 2 risers of 0.145 m in 1 flight(s) (2) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_sp_003_0 |
| path_grading | 1 | a stepped path: 36 % along is steeper than 1:12, so 4 risers of 0.120 m in 1 flight(s) (4) with level landings, treads 0.35 m, level across, stone step edges (inferred) | path_access_sp_001_0 |
| path_grading | 1 | a stepped path: 86 % along is steeper than 1:12, so 18 risers of 0.144 m in 2 flight(s) (9/9) with level landings, treads 0.30 m, level across, stone step edges; a handrail on the flights over 1 m (inferred) | path_access_sp_001_1 |
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
| rig_bedside | 1 | bedside wall sconce on the head wall beside the bed f_L0_020 (the top of the nightstand f_L0_045 is taken by the candle dec_L0_062): sconce back 0.071 m off every wall | rig_r_L0_yatak_odasi_2 |
| rig_ceiling | 1 | ceiling fixture at (1.66, 8.60) of r_L-1_mutfak not hung: the decor pendant dec_L-1_050 hangs 0.73 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L-1_mutfak |
| rig_ceiling | 1 | ceiling fixture at (11.21, 10.34) of r_L0_koridor_2 not hung: the decor pendant dec_L0_053 hangs 1.30 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor_2 |
| rig_ceiling | 1 | ceiling fixture at (11.21, 7.41) of r_L0_koridor_2 not hung: the decor pendant dec_L0_053 hangs 1.30 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor_2 |
| rig_ceiling | 1 | ceiling fixture at (13.51, 8.63) of r_L-1_mutfak_2 not hung: the decor pendant dec_L-1_084 hangs 0.64 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L-1_mutfak_2 |
| rig_ceiling | 1 | ceiling fixture at (3.97, 10.34) of r_L0_koridor not hung: the decor pendant dec_L0_022 hangs 1.29 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor |
| rig_ceiling | 1 | ceiling fixture at (3.97, 7.41) of r_L0_koridor not hung: the decor pendant dec_L0_022 hangs 1.29 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 2200 lm go into the pendant | rig_r_L0_koridor |
| rig_ceiling | 1 | ceiling fixture at (6.05, 10.87) of r_L1_banyo: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo |
| rig_ceiling | 1 | ceiling fixture at (9.12, 10.87) of r_L1_banyo_2: the ceiling over it is 1.32 m high, its bottom would be 1.21 m above the floor (< 1.55 m, camera height + headroom): no ceiling fixture, the fill light stays | rig_r_L1_banyo_2 |
| rig_light | 1 | r_L-1_banyo: ceiling fixture at the pole of inaccessibility of r_L-1_banyo; its light under the decor ceiling light dec_L-1_068; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo: mirror light over the washbasin f_L-1_026, above the mirror dec_L-1_067 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_mirror_1_light |
| rig_light | 1 | r_L-1_banyo_2: ceiling fixture at the pole of inaccessibility of r_L-1_banyo_2; its light under the decor ceiling light dec_L-1_079; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L-1_banyo_2: mirror light over the washbasin f_L-1_025, above the mirror dec_L-1_078 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L-1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L-1_koridor: ceiling fixture at the pole of inaccessibility of r_L-1_koridor, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_083); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_ceiling_1_light |
| rig_light | 1 | r_L-1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L-1_koridor_2, 5 x 1100 lm bulbs for 450 lm/m2 over 11.9 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L-1_077); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L-1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_091 over the counter f_L-1_001; 852.8 lm -> 2.3112 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_1_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_092 over the counter f_L-1_002; 299.1 lm -> 0.785 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_2_light |
| rig_light | 1 | r_L-1_mutfak: LED strip under the wall cabinet f_L-1_093 over the counter f_L-1_002; 357.2 lm -> 0.9377 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_strip_3_light |
| rig_light | 1 | r_L-1_mutfak: the ceiling light of the zone (spot(s) (1.66, 8.60)) in the decor pendant dec_L-1_050 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_ceiling_4_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_097 over the counter f_L-1_010; 852.8 lm -> 2.3112 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_1_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_098 over the counter f_L-1_011; 355.4 lm -> 0.9331 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_2_light |
| rig_light | 1 | r_L-1_mutfak_2: LED strip under the wall cabinet f_L-1_099 over the counter f_L-1_011; 298.6 lm -> 0.7837 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_strip_3_light |
| rig_light | 1 | r_L-1_mutfak_2: the ceiling light of the zone (spot(s) (13.51, 8.63)) in the decor pendant dec_L-1_084 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L-1_mutfak_2_ceiling_4_light |
| rig_light | 1 | r_L-1_salon: pendant light over the dining table f_L-1_027 under the decor pendant dec_L-1_158; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_1_light |
| rig_light | 1 | r_L-1_salon: the decor pendant dec_L-1_003 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L-1_salon_pendant_2_light |
| rig_light | 1 | r_L-1_salon_2: pendant light over the dining table f_L-1_038 under the decor pendant dec_L-1_177; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_1_light |
| rig_light | 1 | r_L-1_salon_2: the decor pendant dec_L-1_102 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L-1_salon_2_pendant_2_light |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_040; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_003, above the mirror dec_L0_039 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_banyo_2; its light under the decor ceiling light dec_L0_043; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_banyo_2: mirror light over the washbasin f_L0_005, above the mirror dec_L0_042 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo; its light under the decor ceiling light dec_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo: mirror light over the washbasin f_L0_006, above the mirror dec_L0_025 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_mirror_1_light |
| rig_light | 1 | r_L0_e_banyo_2: ceiling fixture at the pole of inaccessibility of r_L0_e_banyo_2; its light under the decor ceiling light dec_L0_028; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_e_banyo_2_ceiling_2_light |
| rig_light | 1 | r_L0_e_banyo_2: mirror light over the washbasin f_L0_004, above the mirror dec_L0_027 (top 2.15 m); 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_e_banyo_2_mirror_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_031 is taken by the vase dec_L0_115); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi: bedside wall sconce on the head wall beside the bed f_L0_007 (the top of the nightstand f_L0_032 is taken by the books dec_L0_020); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi: the decor pendant dec_L0_016 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_pendant_3_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_033 is taken by the vase dec_L0_122); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: bedside wall sconce on the head wall beside the bed f_L0_008 (the top of the nightstand f_L0_034 is taken by the books dec_L0_051); 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_bedside_2_light |
| rig_light | 1 | r_L0_e_yatak_odasi_2: the decor pendant dec_L0_047 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_e_yatak_odasi_2_pendant_3_light |
| rig_light | 1 | r_L0_koridor: the ceiling light of the zone (spot(s) (3.97, 7.41); (3.97, 10.34)) in the decor pendant dec_L0_022 (UL170: the pendant is the zone's light), 4400 lm over its 1 bulb(s); bulb 1/1; 4400.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_ceiling_1_light |
| rig_light | 1 | r_L0_koridor_2: the ceiling light of the zone (spot(s) (11.21, 7.41); (11.21, 10.34)) in the decor pendant dec_L0_053 (UL170: the pendant is the zone's light), 4400 lm over its 1 bulb(s); bulb 1/1; 4400.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven: ceiling fixture at the pole of inaccessibility of r_L0_merdiven, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_ceiling_1_light |
| rig_light | 1 | r_L0_merdiven_2: ceiling fixture at the pole of inaccessibility of r_L0_merdiven_2, 3 x 1100 lm bulbs for 450 lm/m2 over 5.7 m2 and 1 fixture(s); 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L0_merdiven_2_ceiling_1_light |
| rig_light | 1 | r_L0_yatak_odasi: bedside light in the shade of the table lamp dec_L0_006 on f_L0_041 beside the bed f_L0_019; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi: the decor pendant dec_L0_003 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_2: bedside light in the shade of the table lamp dec_L0_061 on f_L0_044 beside the bed f_L0_020; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_2: the decor pendant dec_L0_058 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_2_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_033 on f_L0_043 beside the bed f_L0_021; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_3: bedside light in the shade of the table lamp dec_L0_038 on f_L0_029 beside the bed f_L0_021; moved 0.13 m down by the ray check (z 1.06 -> 0.93 m): no ray left the model decor_f_L0_029_34 at the in-shade spot, so the light sits under its closed shade or bulb; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_3: the decor pendant dec_L0_030 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_3_pendant_3_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_072 on f_L0_046 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_1_light |
| rig_light | 1 | r_L0_yatak_odasi_4: bedside light in the shade of the table lamp dec_L0_077 on f_L0_028 beside the bed f_L0_022; 470.0 lm -> 1.2337 W radiant x gain 2.0 (two bedside lamps with a 470 lm (40 W-equivalent) LED bulb each; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_bedside_2_light |
| rig_light | 1 | r_L0_yatak_odasi_4: the decor pendant dec_L0_069 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_yatak_odasi_4_pendant_3_light |
| rig_light | 1 | r_L1_banyo: mirror light over the washbasin f_L1_015; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_mirror_1_light |
| rig_light | 1 | r_L1_banyo_2: mirror light over the washbasin f_L1_016; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L1_banyo_2_mirror_1_light |
| rig_light | 1 | r_L1_koridor: ceiling fixture at the pole of inaccessibility of r_L1_koridor, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_033); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_ceiling_1_light |
| rig_light | 1 | r_L1_koridor_2: ceiling fixture at the pole of inaccessibility of r_L1_koridor_2, 7 x 1100 lm bulbs for 450 lm/m2 over 15.3 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_037); 7700.0 lm -> 21.84 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, one per 3 m of a long hall, bulbs for 450 lm per m2 of floor; the documents say nothing about lamps) | rig_r_L1_koridor_2_ceiling_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant light over the dining table f_L1_005 under the decor pendant dec_L1_015; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_pendant_1_light |
| rig_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pendant light over the dining table f_L1_009 under the decor pendant dec_L1_049; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_pendant_1_light |
| rig_light_escape | 1 | r_L0_yatak_odasi_3: the rig light of rig_r_L0_yatak_odasi_3_bedside_1 was enclosed by its host dec_L0_038 (decor_f_L0_029_34) at the in-shade spot, z 1.06 m; moved 0.13 m down to z 0.93 m, where it gets out | rig_r_L0_yatak_odasi_3_bedside_1_light |
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
| see_through | 1 | the bedroom's wardrobe run (modern style): black-framed sliding doors, slatted ones and glass ones in turn with its garments and an LED strip showing through, a front no other bedroom of the house has (UL120, UL182); a top box to the ceiling (0.56 m of lidded boxes and baskets over the hanging bays); light dec_L0_041 slid 0.24 m off the run; replaces the library model hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 | furn_f_L0_009 |
| see_through | 1 | the bedroom's wardrobe run (modern style): black-framed sliding doors, slatted ones and glass ones in turn with its garments and an LED strip showing through, as its twin room r_L0_yatak_odasi_3 (UL120, UL182); a top box to the ceiling (0.56 m of lidded boxes and baskets over the hanging bays); light dec_L0_078 slid 0.24 m off the run; replaces the library model abo_B07B3XXD3P | furn_f_L0_011 |
| see_through | 1 | the bedroom's wardrobe run (modern style): horizontal black slat sliding doors with its garments and an LED strip showing through, as its twin room r_L0_e_yatak_odasi (UL120, UL182); a top box to the ceiling (0.90 m of lidded boxes and baskets over the hanging bays); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_024 |
| see_through | 1 | the bedroom's wardrobe run (modern style): reeded glass sliding doors in black frames with its garments and an LED strip showing through, as its twin room r_L0_yatak_odasi (UL120, UL182); a top box to the ceiling (0.56 m of lidded boxes and baskets over the hanging bays); replaces the library model hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 | furn_f_L0_012 |
| see_through | 1 | the bedroom's wardrobe run (modern style): reeded glass sliding doors in black frames with its garments and an LED strip showing through, the room scheme's front (limewash) (UL120, UL182); a top box to the ceiling (0.56 m of lidded boxes and baskets over the hanging bays); replaces the library model objaverse_08a3baeb2e0847939d53027824de5a49 | furn_f_L0_010 |
| see_through | 1 | the master bedroom's wardrobe run (modern style): horizontal black slat sliding doors with its garments and an LED strip showing through, the modern family's own front (UL120, UL182); a top box to the ceiling (0.90 m of lidded boxes and baskets over the hanging bays); replaces the library model module:wardrobe:wardrobe_run | furn_f_L0_023 |
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
| suspension | 3 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L-1_050_cord, decor_dec_L0_003_cord, decor_dec_L0_058_cord |
| terrace:ro_001 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003) | roof |
| terrace:ro_002 | 1 | brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006) | roof |
| terrace_railing | 1 | roof terrace ro_001: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_001 |
| terrace_railing | 1 | roof terrace ro_002: the parapet stops at the eaves line; a 0.05 m coping on it and a glass channel balustrade reach the guard height (not drawn; the kind follows the style) | roof_terrace_railing_ro_002 |
| threshold:d_L0_011 | 1 | d_L0_011 is flush with the ground outside and the documents give no level at its landing: one step of 0.15 m up into the house (the levels' riser), its landing 0.15 m under the floor with a stone threshold at the door, the ground graded down to the landing and falling away from it 6 % (lesson UL203; inferred) | site |
| threshold:d_L0_012 | 1 | d_L0_012 is flush with the ground outside and the documents give no level at its landing: one step of 0.15 m up into the house (the levels' riser), its landing 0.15 m under the floor with a stone threshold at the door, the ground graded down to the landing and falling away from it 6 % (lesson UL203; inferred) | site |
| tree | 27 | bush of the drawn size, 0.8 m tall (height assumed) | tree_sp_001_s1e2_plant1, tree_sp_001_s1e3_plant1, tree_sp_001_s1e5_plant1 |
| tree | 21 | shrub: crown 0.72 m as drawn (under a 1.5 m crown radius), 0.86 m tall (height by the crown class, assumed); species oleander (inferred) | tree_sd_L0_007, tree_sd_L0_008, tree_sd_L0_009 |
| turn | 4 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 1 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001, furn_f_L0_002 |
| under | 2 | the space under the stair lower than 2.00 m is closed by 5 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L-1_019, furn_f_L-1_020 |
| under_roof | 2 | its head room under the sloped ceiling is only 1.00 m (under 1.60 m) and no spot within 0.5 m along its wall leaves more: lowered to 1.00 m so nothing crosses the roof; it needs a dormer or a raised roof (review) | d_L1_004, d_L1_005 |
| under_roof | 2 | wardrobe 2.10 m high where the sloped ceiling over its footprint leaves 1.80 m: built 1.80 m high (UL128) | furn_f_L1_027, furn_f_L1_028 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.37 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| void_guard | 1 | floor opening 1 of L1 (f_L0_002 comes up through it): a 1.00 m glass channel balustrade on its 2 free edge(s), 1.52 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_1 |
| waist | 4 | the house's style (modern: plate structure, glass panels under a steel handrail, steel strings (glass channel language of the house)); the documents show the stair in plan only | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| wall_clear | 1 | over the door d_L0_011 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_108 |
| wall_clear | 2 | over the window win_arch_r_L0_yatak_odasi_3_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_099, dec_L0_100 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L0_131 |
| wall_clear | 1 | over the window win_arch_r_L0_yatak_odasi_4_1 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_132 |
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
| wall_plate | 1 | inferred: a light switch beside the door d_L1_004 into r_L1_banyo, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_004 into r_L1_koridor, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_005 into r_L1_banyo_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_005 into r_L1_koridor_2, on the latch side, assumed on the side with more free wall (0.56 m against 0.32 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_2_02 |
| wall_plate | 1 | inferred: a light switch beside the outside door d_L0_012 (solid), on the latch side, assumed on the side with more free wall (0.11 m against 0.00 m; the documents give no hinge side), its centre 0.10 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch beside the outside door d_L1_003 (solid), on the latch side, assumed on the side with more free wall (0.67 m against 0.34 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_01 |
| wall_plate | 1 | inferred: a light switch beside the outside door d_L1_006 (solid), on the latch side, assumed on the side with more free wall (0.67 m against 0.34 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_koridor_2_01 |
| wall_plate | 1 | inferred: a light switch on the wall next to the open side o_L-1_001 (a separator line, no wall), the room's only way in, 0.47 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L-1_salon_01 |
| wall_plate | 1 | inferred: a light switch on the wall next to the open side o_L-1_002 (a separator line, no wall), the room's only way in, 0.27 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L-1_salon_2_01 |
| wall_plate | 1 | inferred: a light switch on the wall next to the outside door d_L0_011 (entrance), as beside it the intercom dec_L0_108, 0.08 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L0_koridor_01 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_027 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_028 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_029 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_04 |
| wall_plate | 1 | inferred: a power socket at the desk f_L0_030 under its top, beside its legs, 0.30 m over the floor | plate_r_L0_yatak_odasi_04 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_067, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L-1_078, 1.20 m over the floor, outside the bath and shower zone | plate_r_L-1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_027, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_e_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_039, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L0_042, 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_030, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_02 |
| wall_plate | 1 | inferred: a power socket beside the mirror dec_L1_034, 1.20 m over the floor, outside the bath and shower zone | plate_r_L1_banyo_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (left side) beside its nightstand f_L0_031, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_007 (right side) beside its nightstand f_L0_032, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (left side) beside its nightstand f_L0_034, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_008 (right side) beside its nightstand f_L0_033, 0.30 m over the floor | plate_r_L0_e_yatak_odasi_2_04 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (left side) over its nightstand f_L0_041 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_019 (right side) over its nightstand f_L0_042 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (left side) over its nightstand f_L0_045 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_020 (right side) over its nightstand f_L0_044 at the bed's side, 0.42 m over the floor | plate_r_L0_yatak_odasi_2_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (left side) over its nightstand f_L0_043 at the bed's side, 0.67 m over the floor | plate_r_L0_yatak_odasi_3_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_021 (right side) beside its desk f_L0_029, 0.30 m over the floor | plate_r_L0_yatak_odasi_3_03 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (left side) beside its desk f_L0_028, 0.30 m over the floor | plate_r_L0_yatak_odasi_4_02 |
| wall_plate | 1 | inferred: a power socket for the bed_double f_L0_022 (right side) over its nightstand f_L0_046 at the bed's side, 0.81 m over the floor | plate_r_L0_yatak_odasi_4_03 |
| wall_plate | 2 | inferred: a power socket in the hall on its longest free wall (1.55 m), 0.30 m over the floor | plate_r_L1_koridor_03, plate_r_L1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (2.38 m), 0.30 m over the floor | plate_r_L0_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (2.96 m), 0.30 m over the floor | plate_r_L-1_koridor_2_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (3.26 m), 0.30 m over the floor | plate_r_L-1_koridor_03 |
| wall_plate | 1 | inferred: a power socket in the hall on its longest free wall (3.63 m), 0.30 m over the floor | plate_r_L0_koridor_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.10 m, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_04 |
| wall_plate | 2 | inferred: a power socket on a free wall stretch of 1.51 m, 0.30 m over the floor | plate_r_L0_yatak_odasi_06, plate_r_L0_yatak_odasi_2_06 |
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
| wall_plate | 1 | inferred: a socket over the worktop f_L-1_010 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_03 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_101 beside it, 0.30 m over the floor | plate_r_L-1_salon_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L-1_102 beside it, 0.30 m over the floor | plate_r_L-1_salon_2_02 |
| wall_plate | 1 | inferred: a socket pair (a double frame) for the TV unit f_L1_106 beside it, 0.30 m over the floor | plate_r_L1_oyun_aktivite_ve_dinlenme_odasi_02 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_002 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_03 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_003 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_02 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_011 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_04 |
| wall_plate | 1 | inferred: a socket pair over the worktop f_L-1_012 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L-1_mutfak_2_02 |
| wet_walls | 1 | the modern family's bathroom (FAMILY_BATH): large-format stone-look porcelain 60 x 120 cm in greige on the walls, floor to ceiling (UL114 B8; the brief names no wet-room tiles) | style |
| winders | 4 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L-1_019, furn_f_L-1_020, furn_f_L0_001 |
| window_fit | 1 | fitted again to its window win_L1_001 as built: 4.00 m wide, sill 0.20 m, head 1.71 m: a 4.40 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L1_005 |
| window_fit | 1 | fitted again to its window win_L1_002 as built: 4.00 m wide, sill 0.20 m, head 1.71 m: a 4.40 m rod past both sides of the whole glazing, its panels at the glazing's ends (UL181) | dec_L1_039 |
| window_handles | 2 | design detail of the documented window: a slider window of 2 pane(s), handles on the opening one(s) [1] (a 4.00 m glazing over 2.4 m with no drawn bars: 2 lift-and-slide panes on its low sill of at most 2 m (real products, UL181)); not in the documents | win_L1_001_handle, win_L1_002_handle |

## Rooms mixing polished and Cycles views

None.

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1_salon (rung None), r_L0_e_yatak_odasi (rung None), r_L0_yatak_odasi (rung None), r_L0_yatak_odasi_3 (rung None), r_L1_oyun_aktivite_ve_dinlenme_odasi (rung None), r_L1_teras (rung None).

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_1097864c4508a042341822ac [non_commercial], 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_2391c2116650ba6784258f6b [non_commercial], 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_324a4061c7079774c20c56e9 [non_commercial], 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_3ca51944db9df428d5f09afc [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_730bffda88163748fe87804f [non_commercial], 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], 3dwh_878ba8fda4c76a59ebca493e [non_commercial], 3dwh_89078d34005bcf2aa741eb7f [non_commercial], 3dwh_a31b877d1e39464af0091912 [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], 3dwh_c41eadfdc01e4ec60d4e0bea [non_commercial], 3dwh_cc9a735781c180a72cf558ce [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_books_scandinavian_2_a69db21c [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_large_scandinavian_5_c7cc94ed [tool_nc], gen_plant_small_industrial_5_effc724b [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], gen_potted_plant_scandinavian_1_04f97c4b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_03a8b87b73fec83efafca897e7084a395f746115 [non_commercial], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_3130bb35e30c725682e281d42085aaa0a09fcce5 [non_commercial], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial], hssd_9337b4a78dbaaecc4fb24c020d43749bbf1a710b [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L-1_banyo_1: commercial-safe: no (flagged assets: 3dwh_878ba8fda4c76a59ebca493e [non_commercial])
- cam_r_L-1_koridor_2_1: commercial-safe: no (flagged assets: 3dwh_1097864c4508a042341822ac [non_commercial], 3dwh_878ba8fda4c76a59ebca493e [non_commercial], hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial])
- cam_r_L-1_mutfak_1: commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L-1_mutfak_2: commercial-safe: no (flagged assets: 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L-1_mutfak_3: commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial])
- cam_r_L-1_salon_1: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_324a4061c7079774c20c56e9 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_9337b4a78dbaaecc4fb24c020d43749bbf1a710b [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial])
- cam_r_L-1_salon_2: commercial-safe: no (flagged assets: 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial], gen_bowl_japandi_5_f9ac0f6a [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial])
- cam_r_L-1_salon_3: commercial-safe: no (flagged assets: 3dwh_30a9b6efc5109d45e2cbb497 [non_commercial], 3dwh_324a4061c7079774c20c56e9 [non_commercial], 3dwh_b261da0cc9d99d0cd8297091 [non_commercial], 3dwh_bc790e2f62189290d277caa7 [non_commercial], 3dwh_cdae4af7cd93384e5e32c598 [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial], gen_books_industrial_1_e00c8743 [tool_nc], gen_bowl_japandi_5_f9ac0f6a [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_9337b4a78dbaaecc4fb24c020d43749bbf1a710b [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial], hssd_xxxx3a4d8840x65eax4986x98f8xb64e2fba5da6 [non_commercial])
- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L0_e_banyo_1: commercial-safe: yes
- cam_r_L0_e_banyo_2: commercial-safe: yes
- cam_r_L0_e_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_2391c2116650ba6784258f6b [non_commercial], gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_e_yatak_odasi_2: commercial-safe: no (flagged assets: hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_e_yatak_odasi_3: commercial-safe: no (flagged assets: gen_books_scandinavian_2_a69db21c [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc], hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial])
- cam_r_L0_koridor_1: commercial-safe: no (flagged assets: hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial])
- cam_r_L0_yatak_odasi_1: commercial-safe: no (flagged assets: 3dwh_730bffda88163748fe87804f [non_commercial], gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], gen_plant_small_industrial_5_effc724b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_3130bb35e30c725682e281d42085aaa0a09fcce5 [non_commercial])
- cam_r_L0_yatak_odasi_2: commercial-safe: no (flagged assets: gen_plant_small_industrial_5_effc724b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_3130bb35e30c725682e281d42085aaa0a09fcce5 [non_commercial])
- cam_r_L0_yatak_odasi_3: commercial-safe: no (flagged assets: gen_plant_small_industrial_5_effc724b [tool_nc], hssd_037c2aea5184e56ef6d240fabe3aee458ead4e52 [non_commercial], hssd_3130bb35e30c725682e281d42085aaa0a09fcce5 [non_commercial])
- cam_r_L0_yatak_odasi_3_1: commercial-safe: no (flagged assets: 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_f858f555e33dd365be821c2b [non_commercial])
- cam_r_L0_yatak_odasi_3_2: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial])
- cam_r_L0_yatak_odasi_3_3: commercial-safe: no (flagged assets: 3dwh_177294d47e9e845c6a47a25c [non_commercial], 3dwh_21229a4e1db90fefa6b3188a [non_commercial], 3dwh_2275084b071e23b25eda1ed0 [non_commercial], 3dwh_54a792101c925f12bff90916 [non_commercial], 3dwh_a31b877d1e39464af0091912 [non_commercial], gen_potted_plant_scandinavian_1_04f97c4b [tool_nc])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: 3dwh_89078d34005bcf2aa741eb7f [non_commercial])
- cam_r_L1_koridor_1: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_large_scandinavian_5_c7cc94ed [tool_nc])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1: commercial-safe: no (flagged assets: 3dwh_3ca51944db9df428d5f09afc [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], 3dwh_c41eadfdc01e4ec60d4e0bea [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2: commercial-safe: no (flagged assets: 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_cc9a735781c180a72cf558ce [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial])
- cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3: commercial-safe: no (flagged assets: 3dwh_75ac3c7d6dc1da28c99a0ad6 [non_commercial], 3dwh_be06a7c0ae9c48cd7f9164ce [non_commercial], 3dwh_e57ba8f838ebb1ee1874f71d [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_small_minimal_4_e8c7266b [tool_nc], hssd_0806e947f46c794f33aa87bc34a294008e79dede [non_commercial])
- cam_r_L1_teras_1: commercial-safe: no (flagged assets: 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_2: commercial-safe: no (flagged assets: 3dwh_1d13c0a8510409d30c46e992 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_8512ac158d0f8579041a1fc2 [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- cam_r_L1_teras_3: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial])
- ext_1: commercial-safe: yes
- ext_2: commercial-safe: no (flagged assets: hssd_03a8b87b73fec83efafca897e7084a395f746115 [non_commercial])
- ext_3: commercial-safe: no (flagged assets: hssd_03a8b87b73fec83efafca897e7084a395f746115 [non_commercial])
- ext_5: commercial-safe: no (flagged assets: 3dwh_37938c0ddf4de7b490c20f50 [non_commercial], 3dwh_4d0d32e27d3dd4435de64eb8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], gen_plant_large_scandinavian_5_c7cc94ed [tool_nc], hssd_2c681d7e64e0410d76156f500cd2df798975a25d [non_commercial], hssd_d886d10e71a0365a725abcf139142223409f7b4f [non_commercial])
- ext_7: commercial-safe: no (flagged assets: 3dwh_3ca51944db9df428d5f09afc [non_commercial], 3dwh_cc9a735781c180a72cf558ce [non_commercial])

## Built below library level (Milestone 13)

73 furniture piece(s) built from a module builder or a parametric family instead of a library model: 10 library gap(s) to close with a real model, 63 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

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
| f_L0_009 | wardrobe | module | module:wardrobe:wardrobe_run | r_L0_yatak_odasi_3 | bedroom | from_documents | yes | - |
| f_L0_010 | wardrobe | module | module:wardrobe:wardrobe_run | r_L0_yatak_odasi | bedroom | from_documents | yes | - |
| f_L0_011 | wardrobe | module | module:wardrobe:wardrobe_run | r_L0_yatak_odasi_4 | bedroom | from_documents | yes | - |
| f_L0_012 | wardrobe | module | module:wardrobe:wardrobe_run | r_L0_yatak_odasi_2 | bedroom | from_documents | yes | - |
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
| f_L1_025 | shower | module | bath_set | r_L1_banyo | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L1_026 | shower | module | bath_set | r_L1_banyo_2 | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L-1_091 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_092 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L-1_093 | wall_cabinet | module | wall_run | r_L-1_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_041 | nightstand | parametric | parametric:nightstand | r_L0_yatak_odasi | bedroom | added_by_ai | no (by design) | - |
| f_L0_042 | nightstand | parametric | parametric:nightstand | r_L0_yatak_odasi | bedroom | added_by_ai | no (by design) | - |
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

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): cam_r_L1_teras_2 (15.0 degrees off the sun, sky pull k 4), ext_1 (6.0 degrees off the sun, sky pull k 4), ext_5 (5.6 degrees off the sun, sky pull k 0).

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

Assets: textures CC0 x 50; furniture/decor models 3DWH-UNREVIEWED x 61, CC-BY-4.0 x 123, CC-BY-NC-4.0 x 50, generated (Infinigen v1.19.0, BSD-3-Clause) x 2, generated (TRELLIS.2-4B, MIT) x 29 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 34 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "Candles" by rhcreations (https://sketchfab.com/3d-models/4058a3ed739e4f9f89f49323c7db4b4c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_001)
- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_136)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_051)
- "Platform" by AlexBedrossian (https://sketchfab.com/3d-models/c274989766c344ac97817f77a046c0e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_011)
- "Candle" by deniska40k (https://sketchfab.com/3d-models/c408586d8c1547448c4ff47abb4fb981), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L-1_045, dec_L0_007)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261030-181158-full-20261030T181642Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | pending | 48.7 s | 8 sheet question(s) written (sheets/requests.json) |
| pipeline | pending | 109.3 s | 70 recognition question(s) written (recognition/requests.json); 8 sheet question(s) (sheets/requests.json) |
| recognize | reused | 3.4 s | - |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 2.6 min | answers applied |
| fit | ok | 11.7 s | - |
| layout | ok | 54.2 s | - |
| decor_ask | ok | 3.4 min | - |
| photos | reused | 0.2 s | - |
| assets | ok | 5.8 s | - |
| decor | ok | 11.8 s | - |
| agent_apply | ok | 107.9 s | - |
| refit | ok | 112.2 s | - |
| build | ok | 54.8 min | - |
| agent_previews | ok | 11.5 min | 34 view(s) |
| agent | ok | 88.8 min | 4 round(s), 30 finding(s) removed by 117 accepted edit(s) (measured; 280 predicted by the dry re-checks), 27 new, net 3, 368 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 15.0 min | - |
| controls | ok | 2.4 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 3.3 min | - |
| check | ok | 3.7 min | - |
| export | incomplete | 0.0 s | deadline: export not started |
| combine | ok | 29.9 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 4 round(s), 117 edit(s) accepted, 368 rejected, 771 model calls (10867797 tokens), 102.1 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 26174): earlier runs of the appended log are left out (26173 events, 8463 model calls, 807 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 117 / 368 (24 % accepted) |
| rejected by reason | acceptance 90, max_tries 34, memory 33, asset_unusable 31, pin_refused 22 |
| rooms checked by code / vision / planner | 38 / 14 / 31 |
| rooms with fixable critical or major findings visited | 31 of 31 |
| critical before -> after (after: round 4's critics, before its 6 accepted edit(s)) | 6 -> 9 |
| major before -> after (after: round 4's critics, before its 6 accepted edit(s)) | 371 -> 616 |
| agent minutes; first accepted edit after | 85.8; 10.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 33; 81; 94 (69) |
| critical/major findings removed in rounds 1-3 (measured by the next round; predicted by the dry re-checks of the same rounds) | 30 measured; 280 predicted (the last round's dry re-checks predicted 49 more, not measured) |
| new critical/major findings in rounds 1-3; net removed (gone - new) | 89 new; net -59 |
| edits removing their finding | 8 of 89 |
| plans ok / empty / refused / default | 69 / 21 / 2 / 2 |

### What the AI inspector saw on the final renders

592 vision finding(s) (86 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 32 fixed in the final round, 10 handed to the stage that owns them, 637 open; the architect leaves 0 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`.

Still open or handed on (critical and major):

- critical Q3 r_L-1_koridor: The stair opening in the hall (koridor) has no guardrail or barrier, creating a significant fall risk to the level below. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- critical Q3 r_L-1_koridor_2: The stair opening in the second hall (koridor 2) has no guardrail or barrier, creating a significant fall risk to the level below. (handed to the architect stage: a guard in front of an opening or a void is built by code ()
- major Q10 f_L1_017: An upholstered indoor sofa is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_020: An upholstered indoor sofa is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_023: An indoor coffee table is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_030: An upholstered indoor armchair is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_031: An upholstered indoor armchair is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_035: An indoor console table is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_036: An indoor coffee table is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_049: An indoor floor lamp is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_050: An indoor bookshelf is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_052: An upholstered indoor armchair is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_005: An indoor dining table is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major Q10 f_L1_006: An indoor dining chair is placed on the outdoor terrace. (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major V1 r_L-1_koridor_2: bad_camera: the frame is a low, tight crop of one corner; the hall's main group (the shoe cabinet, the doors, the opening) is not in view, s (open: a tool exists (set_camera, remove_camera) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: a place to sit. The reference hall anchors the space with a styled bench; this corridor has no seating or anchor piece at all (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: a warm light. The reference has a chandelier and warm wall sconces; the render is flat and dim with no visible ceiling or acc (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_koridor_2: missing layer: styled surfaces. The reference wall is a textured feature panel; here the walls are a flat, untextured beige with no accent,  (open: a tool exists (swap_model) but no edit was accepted)
- major D2 f_L-1_090: The refrigerator is a crude, featureless white box. It lacks any handles, panels, or realistic details, making it look like a placeholder mo (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces. The entire kitchen is completely bare. There are no plants, no small appliances (kettle, coffee machine), an (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: a warm light. The lighting is flat and cold. The reference shows a warm, inviting atmosphere with recessed lighting and a sty (open: a tool exists (swap_model) but no edit was accepted)
- major D2 f_L-1_090: The fridge is rendered as a giant, blocky white box sitting on top of the counter. It is the wrong scale, the wrong shape, and it is floatin (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major Q13 f_L-1_001: The kitchen is not designed. The worktop is completely bare (no kettle, coffee machine, or decor), and there are no wall cabinets or a hood  (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: styled surfaces. The reference shows a lived-in kitchen with books, a pitcher, and a bowl of fruit. This render has a complet (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L-1_mutfak: missing layer: warm light. The lighting is flat and clinical, lacking the warm, inviting glow and recessed lighting seen in the reference. (open: a tool exists (swap_model) but no edit was accepted)

### Argus, the auditor

Score 3.1 / 100 (100 = nothing open): 21 critical, 437 major, 133 minor open. By kind (critical + major): lost 52, no_sense 58, geometry 66, other 50, misread 35, taste 115, process 36, silent 27, reference_missed 7, stale 6, detached 5, untyped 1. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- geometry f_L1_025: shower f_L1_025 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: nothi
- geometry f_L1_026: shower f_L1_026 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: nothi
- no_sense f_L1_025: furn_f_L1_025 pokes through the roof (top 5.23 m)
- no_sense f_L1_026: furn_f_L1_026 pokes through the roof (top 5.23 m)
- other f_L1_025: shower f_L1_025 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: nothi
- other f_L1_026: shower f_L1_026 reaches 2.08 m over its floor where the sloped ceiling over it is 0.81 m high and the roof's top 1.05 m: it pokes through the roof (UL128: nothi
- no_sense r_L-1_koridor: The stair opening in the hall (koridor) has no guardrail or barrier, creating a significant fall risk to the level below.
- no_sense r_L-1_koridor_2: The stair opening in the second hall (koridor 2) has no guardrail or barrier, creating a significant fall risk to the level below.
- misread cam_r_L1_teras_1: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
- taste cam_r_L1_banyo_1: Argus: Argus: Argus: The camera frame is entirely black and empty; it does not show the room, its main group, or any architecture at eye height. This is a faile
- misread r_L1_teras: Argus: Argus: The main furniture group (armchairs and side table) is missing from the terrace, leaving the space empty and undefined.
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

Library gaps reported by the agent: wardrobe scandinavian (No audited wardrobe model rated at least 3.8 (the current abo_B07B3XXD3P is rated 4.0) fits the drawn 1.45 x 0.60 m footprint, so the S6 parametric finding on f_L0_011 stays for review.), nightstand modern minimal (No audited modern-minimal nightstand model fits the 0.50 x 0.45 m footprint within the height caps (side_table_01, abo_B079VK52WZ, abo_B01D3C7Z4A, abo_B079VKDKC1 all fail the fit rules), so the parametric build stays.), kitchen_counter (M2: f_L-1_003 counter top at 1.18 m over working height 0.97 m; no audited library model of kitchen_counter exists to swap to a standard-height module.), tall_cabinet (tall_cabinet f_L-1_104 is an added_by_ai parametric build below the library level; no audited library model of this type/style exists, so the gap is recorded rather than swapped.), tall_cabinet (tall_cabinet f_L1_066 was built below library level with a parametric mesh; no audited library model of a tall_cabinet exists for this bathroom's low-ceiling context), washbasin (washbasin f_L1_015 floats 0.384 m above floor (S1); no real product model in the library seats correctly under the sloped ceiling — all generated models fail the fit rules), toilet (toilet f_L1_021 floats 0.200 m above floor (S1); no real product model in the library seats correctly under the sloped ceiling — all generated models fail the fit rules), kitchen_counter (a:F175 (M2): the built kitchen_counter module has its top at 1.18 m, over the 0.97 m working height, and the audited library holds no kitchen_counter model to swap to (catalog returned 0 models).), nightstand modern minimal (No audited library nightstand model fits f_L0_033 (all swap attempts rejected by fit rules or style); the parametric build stands (a:F516).), nightstand modern minimal (No audited library nightstand model fits f_L0_034 (all swap attempts rejected by fit rules or style); the parametric build stands (a:F517).), kitchen_counter (Counter top at 1.18 m exceeds working height 0.97 m; no catalogue model at standard height exists to swap to.), tall_cabinet (Fixes a:F521: the 0.3x0.3 m tall_cabinet f_L0_047 was built parametrically below the library level because no audited library model fits its small footprint; the gap is recorded rather than forcing an invalid swap.), washbasin (c:S1:f_L0_003 / a:F312 / a:F162: no audited real-product washbasin model exists (only generated, units-guessed models, all refused by the fit rules), so the floating vessel basin and missing mirror cannot be fixed by swap), kitchen_counter (No audited library model of kitchen_counter exists (catalogue count 0), so the 1.18 m top of f_L-1_003 cannot be fixed by swap_model; the gap is recorded for review.), nightstand modern minimal (No audited modern-minimal nightstand model fits f_L0_033 (all swap attempts failed fit rules); parametric build kept (a:F516).), nightstand modern minimal (No audited modern-minimal nightstand model fits f_L0_034 (all swap attempts failed fit rules); parametric build kept (a:F517).), tall_cabinet (a:F522: tall cabinet built below library level (parametric mesh); prior swap candidate was audit-removed, no usable library model remains), washbasin (a:F162/c:S1:f_L0_003/a:F312: washbasin floats +0.384 m and lacks mirror/styling; prior swaps were audit-removed or failed fit rules, no usable library model remains), toilet (c:S1:f_L0_018: toilet floats +0.200 m; prior swap failed fit rules, no usable library model remains), tall_cabinet (The tall_cabinet f_L0_047 is built as a parametric mesh because no suitable library model fits its 0.3x0.3m footprint and 1.6m height; swap_model attempts have already failed due to fit rules, so the library gap is formally acknowledged.), washbasin (No audited library model of a washbasin fits under the sloped ceiling (0.81 m high) at this location; all generated models fail the fit rules (caps, height, at most 1.60 m high under the sloped ceiling).), toilet (No audited library model of a toilet fits under the sloped ceiling (0.81 m high) at this location; all generated models fail the fit rules (caps, height, at most 1.52 m high under the sloped ceiling).).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 371 | 107 | 13 | 46 | 126 | layout | 35 |
| 2 | 6 | 359 | 109 | 14 | 31 | 100 | layout | 35 |
| 3 | 6 | 357 | 107 | 13 | 34 | 118 | layout | 35 |
| 4 | 9 | 616 | 162 | 32 | 6 | 24 | layout | 8 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| AI1 | 0 | 157 | 0 | 12 |
| AI2 | 0 | 8 | 0 | 0 |
| AI3 | 0 | 12 | 0 | 0 |
| AI5 | 0 | 63 | 0 | 6 |
| C1 | 0 | 0 | 0 | 8 |
| C3 | 0 | 0 | 0 | 16 |
| C7 | 0 | 40 | 0 | 0 |
| D2 | 0 | 19 | 1 | 0 |
| D3 | 0 | 181 | 38 | 0 |
| F1 | 0 | 0 | 6 | 0 |
| F2 | 0 | 16 | 0 | 0 |
| F3 | 0 | 42 | 4 | 0 |
| F4 | 0 | 91 | 0 | 0 |
| F6 | 0 | 33 | 0 | 0 |
| F9 | 0 | 30 | 0 | 0 |
| G1 | 0 | 0 | 24 | 0 |
| G10 | 0 | 79 | 0 | 0 |
| G11 | 0 | 44 | 0 | 0 |
| G12 | 0 | 25 | 0 | 0 |
| G13 | 0 | 24 | 0 | 0 |
| G14 | 0 | 0 | 6 | 0 |
| G2 | 0 | 14 | 8 | 0 |
| G3 | 0 | 29 | 0 | 0 |
| G4 | 0 | 2 | 10 | 0 |
| G5 | 0 | 36 | 0 | 0 |
| G6 | 0 | 23 | 8 | 0 |
| G8 | 0 | 18 | 8 | 0 |
| G9 | 0 | 2 | 0 | 0 |
| J1 | 0 | 64 | 0 | 26 |
| K1 | 0 | 8 | 0 | 0 |
| K3 | 0 | 1 | 0 | 0 |
| L6 | 0 | 4 | 0 | 0 |
| LG | 0 | 0 | 24 | 0 |
| M13 | 0 | 0 | 4 | 0 |
| M15 | 0 | 0 | 4 | 0 |
| M17 | 0 | 17 | 8 | 0 |
| M2 | 0 | 8 | 0 | 0 |
| M21 | 0 | 0 | 24 | 0 |
| M22 | 0 | 15 | 0 | 0 |
| M23 | 0 | 0 | 8 | 0 |
| M26 | 0 | 0 | 20 | 0 |
| M28 | 0 | 2 | 8 | 0 |
| M30 | 0 | 0 | 3 | 0 |
| M31 | 8 | 8 | 0 | 0 |
| M33 | 0 | 37 | 4 | 0 |
| M34 | 0 | 4 | 16 | 0 |
| NR | 0 | 16 | 0 | 0 |
| P0 | 0 | 63 | 0 | 0 |
| P2 | 0 | 18 | 0 | 0 |
| P6 | 0 | 1 | 0 | 0 |
| P7 | 0 | 68 | 0 | 0 |
| P9 | 0 | 0 | 0 | 1 |
| Q1 | 0 | 3 | 0 | 0 |
| Q10 | 0 | 34 | 2 | 0 |
| Q12 | 0 | 51 | 2 | 0 |
| Q13 | 0 | 9 | 1 | 0 |
| Q14 | 0 | 16 | 4 | 0 |
| Q15 | 0 | 0 | 1 | 0 |
| Q3 | 2 | 0 | 0 | 0 |
| Q4 | 5 | 40 | 1 | 0 |
| Q5 | 0 | 7 | 0 | 0 |
| Q7 | 0 | 9 | 0 | 0 |
| R3 | 0 | 0 | 32 | 0 |
| RC | 0 | 0 | 28 | 0 |
| S1 | 0 | 96 | 0 | 0 |
| S2 | 0 | 12 | 32 | 0 |
| S4 | 0 | 0 | 28 | 0 |
| S5 | 0 | 0 | 48 | 0 |
| S6 | 0 | 16 | 0 | 0 |
| V1 | 4 | 50 | 4 | 0 |
| V2 | 0 | 0 | 0 | 2 |
| X2 | 8 | 12 | 8 | 0 |
| X3 | 0 | 3 | 0 | 1 |
| X5 | 0 | 0 | 55 | 0 |
| X6 | 0 | 9 | 0 | 0 |
| X9 | 0 | 8 | 0 | 0 |
| lighting_dark | 0 | 6 | 3 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 26704 | 1 | swap_model | f_L1_059 | added_by_ai | 21.0 -> 21.0 | Argus: The armchair's back/arm stands 2.4 cm from its seat; rotate_piece was already tried and refused (it only re-angled the piece, leaving the F4 behind-the-back finding), so the gap is a model defect that a swap to an integral-rest model fixes. (fixes a:F20) | ![](agent/r1_001_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_002_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 26708 | 1 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The bed f_L0_019 is built in r_L0_yatak_odasi but the camera cuts it out of the frame. The fix is to point the camera at the bed so the render shows the anchor piece. (fixes a:F139) | - | - |
| 26709 | 1 | set_camera | r_L0_banyo | agent_override | - | Argus: The bathroom r_L0_banyo has a bathtub, tall_cabinet, toilet, and washbasin, but the camera does not show the washbasin, toilet, or tall cabinet. The fix is to point the camera at the primary fixtures so the render shows the complete set. (fixes a:F140) | - | - |
| 26716 | 1 | set_camera | r_L-1_banyo | agent_override | - | Argus: The camera cam_r_L-1_banyo_1 does not show the washbasin, mirror, or tub; setting show to the fixture ids makes the code pick a free pose that shows them. (fixes a:F169) | - | - |
| 26717 | 1 | set_material | ground | agent_override | - | Argus: The outdoor setting is a flat, untextured green plane; setting the ground slot to a grass look adds texture and depth. (fixes a:F171) | - | - |
| 26718 | 1 | place_group | r_L1_teras | added_by_ai | 100.0 -> 100.0 | Argus: The terrace is sparsely furnished with only two plants; placing the terrace_lounge group adds the missing plants and furniture. (fixes a:F173) | ![](agent/r1_007_place_group_before_r_L1_teras.png) | ![](agent/r1_008_place_group_after_r_L1_teras.png) |
| 26719 | 1 | set_camera | r_L1_oyun_aktivite_ve_dinlenme_odasi | agent_override | - | Argus: The armchair is cut off by the frame; re-aiming to show the whole chair fixes it. (fixes a:F182) | - | - |
| 26720 | 1 | set_material | surround | agent_override | - | Argus: The bare concrete slab clashes with the stone facade; giving the surround slot a stone look matches it. (fixes a:F183) | - | - |
| 26722 | 1 | set_camera | r_L1_koridor | agent_override | - | Argus: The finding is that the hall view is dominated by closed doors; re-aiming the existing camera to show the entrance group and the open doors (not the closed slab) is the camera fix the code_fix names. place_group and relayout_room were alrea (fixes a:F194) | - | - |
| 26723 | 1 | set_material | facade | agent_override | - | Argus: The facade slot is the main outer wall and takes a plaster look; setting it to plaster_exterior restores the white render over the stone base the brief requires. (fixes a:F197) | - | - |
| 26724 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | 21.0 -> 21.0 | Argus: The twin room is correctly typed 'living'; this one is misread as 'other'. set_room_type is the direct fix; the earlier refusal was an acceptance conflict with a swap, not a type error, so setting the type directly is the right move. (fixes a:F208) | ![](agent/r1_009_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_010_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 26743 | 1 | resize_piece | f_L-1b_042 | adjusted_by_ai | 28.0 -> 28.0 | Sofa footprint was read rotated (0.90 wide x 2.13 deep); correct to real product size 2.13 x 0.90. | ![](agent/r1_075_resize_piece_before_r_L-1b_salon.png) | ![](agent/r1_080_resize_piece_after_r_L-1b_salon.png) |
| 26748 | 1 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Replace the black leather corporate office chair with the AmazonBasics Low-Back Upholstered Mesh Swivel Chair, a smaller (0.45x0.48 m) modern-minimal seat that fits the 0.5x0.5 footprint and reads softer than a corporate leather chair. | ![](agent/r1_088_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r1_095_swap_model_after_r_L0_yatak_odasi.png) |
| 26757 | 1 | move_piece | f_L-1b_046 | adjusted_by_ai | 28.0 -> 28.0 | Sofa back is 0.59 m off the wall; snap its back onto the top wall span s4 (closer than the right wall). | ![](agent/r1_103_move_piece_before_r_L-1b_salon.png) | ![](agent/r1_107_move_piece_after_r_L-1b_salon.png) |
| 26761 | 1 | rotate_piece | f_L-1b_045 | adjusted_by_ai | 18.0 -> 18.0 | Sofa front 180° on its short side is a reading error; the long side faces the most room at 270° (a:F229, a:F240). | ![](agent/r1_109_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_116_rotate_piece_after_r_L-1b_salon_2.png) |
| 26763 | 1 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 gives a fuller 6-piece layout (balcony + terrace_pair) with no hard failures, addressing the sparse-furnishing findings and the window blocked by f_L1_043. | ![](agent/r1_113_relayout_room_before_r_L1_teras.png) | ![](agent/r1_118_relayout_room_after_r_L1_teras.png) |
| 26768 | 1 | move_piece | f_L-1_023 | adjusted_by_ai | 30.0 -> 40.0 | Move wardrobe f_L-1_023 slightly inward (0.02m in -y) to clear the room outline collision. | ![](agent/r1_120_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_128_move_piece_after_r_L-1_salon_2.png) |
| 26769 | 1 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Armchair faces 180° but must face its group (sofa/coffee table) to the north; 90° also clears the 90° G3 offset to the coffee table (c:F4, c:G3, a:F237, a:F607). | ![](agent/r1_121_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r1_129_rotate_piece_after_r_L-1b_salon_2.png) |
| 26773 | 1 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 28.0 -> 58.0 | Armchair must face the coffee table/sofa to its north; rotate front to 90° to align with the seating group. | ![](agent/r1_130_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r1_135_rotate_piece_after_r_L-1b_salon.png) |
| 26774 | 1 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Re-solve with candidate 1 to add the missing second chair of the terrace pair and move the balcony planters away from window win_L1_002. | ![](agent/r1_131_relayout_room_before_r_L1_teras_2.png) | ![](agent/r1_134_relayout_room_after_r_L1_teras_2.png) |
| 26778 | 1 | move_piece | f_L1_031 | adjusted_by_ai | 41.0 -> 51.0 | Shift the armchair 0.33 m toward the coffee table f_L1_023 to get within the 2.5 m group radius, keeping its front aligned with the table. | ![](agent/r1_136_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_143_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 26784 | 1 | move_piece | f_L1_006 | adjusted_by_ai | 51.0 -> 51.0 | Move the chair to the right side of the dining table so it no longer cuts the table footprint. | ![](agent/r1_147_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_152_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 26786 | 1 | move_piece | f_L-1_039 | adjusted_by_ai | 40.0 -> 40.0 | Move chair f_L-1_039 slightly to resolve the 0.034 m cut with table_dining f_L-1_038. | ![](agent/r1_149_move_piece_before_r_L-1_salon_2.png) | ![](agent/r1_159_move_piece_after_r_L-1_salon_2.png) |
| 26790 | 1 | place_group | r_L0_e_yatak_odasi_2 | added_by_ai | 77.0 -> 100.0 | Re-solve the drawn sleeping_double group around the bed anchor to fix the missing second nightstand, the f_L0_034/bed collision and its negative gap. | ![](agent/r1_155_place_group_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_160_place_group_after_r_L0_e_yatak_odasi_2.png) |
| 26800 | 1 | move_piece | f_L1_019 | adjusted_by_ai | 21.0 -> 31.0 | Move sofa f_L1_019 slightly north to clear the front zone blocked by sofa f_L1_018 (F6). | ![](agent/r1_165_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_171_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 26803 | 1 | rotate_piece | f_L1_035 | adjusted_by_ai | 51.0 -> 51.0 | Turn the bench so its front faces 270° (into the room) with its back on the wall, correcting the AI front reading error. | ![](agent/r1_170_rotate_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r1_172_rotate_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 26808 | 1 | move_piece | f_L1_010 | adjusted_by_ai | 31.0 -> 31.0 | Move chair f_L1_010 away from table_dining f_L1_009 to resolve the 0.326 m collision (S2). | ![](agent/r1_176_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) | ![](agent/r1_183_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |
| 26814 | 1 | resize_piece | f_L0_024 | adjusted_by_ai | 100.0 -> 100.0 | Bring the wardrobe height back into the real 1.50-2.45 m range to fix the S4 size finding. | ![](agent/r1_182_resize_piece_before_r_L0_e_yatak_odasi_2.png) | ![](agent/r1_184_resize_piece_after_r_L0_e_yatak_odasi_2.png) |
| 26834 | 1 | report_library_gap | f_L0_011 | library_gap | - | No audited wardrobe model rated at least 3.8 (the current abo_B07B3XXD3P is rated 4.0) fits the drawn 1.45 x 0.60 m footprint, so the S6 parametric finding on f_L0_011 stays for review. | - | - |
| 26837 | 1 | place_group | r_L0_e_yatak_odasi | added_by_ai | 77.0 -> 100.0 | Re-solve the drawn sleeping_double group around the bed anchor to complete the set with a nightstand on the free left side of the head. | ![](agent/r1_196_place_group_before_r_L0_e_yatak_odasi.png) | ![](agent/r1_198_place_group_after_r_L0_e_yatak_odasi.png) |
| 26840 | 1 | retype_piece | f_L1_054 | added_by_ai | 100.0 -> 100.0 | Shoe cabinet is inappropriate for an upper-floor hall; bookshelf is a candidate that fits the 0.60x0.25m footprint and hall context. | ![](agent/r1_199_retype_piece_before_r_L1_koridor.png) | ![](agent/r1_202_retype_piece_after_r_L1_koridor.png) |
| 26846 | 1 | set_lighting | r_L-1_banyo | agent_override | - | View cam_r_L-1_banyo_1 is 0.33 stops over the EV cap; the finding names x1.77 for the room to bring incident light to target. | - | - |
| 26851 | 1 | set_lighting | r_L0_banyo | agent_override | - | cam_r_L0_banyo_1 is 0.53 stops over the EV cap; the finding names x2.05 for the room to reach target incident light. | - | - |
| 26855 | 1 | set_camera | r_L1_koridor | agent_override | - | Reframe the corridor view to show the wardrobe and the re-typed piece, giving the render content to address the bare/unfinished critique. | - | - |
| 26858 | 1 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the entrance group with the top-scoring candidate (9.2) to enrich the 7.6 m² hall beyond a lone shoe cabinet. | ![](agent/r1_219_relayout_room_before_r_L0_koridor.png) | ![](agent/r1_223_relayout_room_after_r_L0_koridor.png) |
| 26861 | 1 | set_lighting | r_L0_e_banyo | agent_override | - | View cam_r_L0_e_banyo_1 is 0.80 stops over the EV cap; the finding names factor x2.46 on the room. | - | - |
| 26873 | 1 | report_library_gap | f_L0_033 | library_gap | - | No audited modern-minimal nightstand model fits the 0.50 x 0.45 m footprint within the height caps (side_table_01, abo_B079VK52WZ, abo_B01D3C7Z4A, abo_B079VKDKC1 all fail the fit rules), so the parametric build stays. | - | - |
| 26882 | 1 | report_library_gap | f_L-1_003 | library_gap | - | M2: f_L-1_003 counter top at 1.18 m over working height 0.97 m; no audited library model of kitchen_counter exists to swap to a standard-height module. | - | - |
| 26883 | 1 | report_library_gap | f_L-1_104 | library_gap | - | tall_cabinet f_L-1_104 is an added_by_ai parametric build below the library level; no audited library model of this type/style exists, so the gap is recorded rather than swapped. | - | - |
| 26887 | 1 | remove_piece | f_L1_066 | added_by_ai | 77.0 -> 77.0 | tall_cabinet pokes through the sloped ceiling (0.82 m high) and its height is outside the valid range; it is an added_by_ai piece that does not fit the low-ceiling bathroom | ![](agent/r1_230_remove_piece_before_r_L1_banyo.png) | ![](agent/r1_233_remove_piece_after_r_L1_banyo.png) |
| 26896 | 1 | report_library_gap | f_L1_066 | library_gap | - | tall_cabinet f_L1_066 was built below library level with a parametric mesh; no audited library model of a tall_cabinet exists for this bathroom's low-ceiling context | - | - |
| 26898 | 1 | resize_piece | f_L-1_094 | added_by_ai | 100.0 -> 100.0 | Resizing to match the Movian Indre 1-door shoe cabinet (0.5m x 0.23m) so the swap_model can fit a real styled model within the room boundaries. | ![](agent/r1_236_resize_piece_before_r_L-1_koridor_2.png) | ![](agent/r1_240_resize_piece_after_r_L-1_koridor_2.png) |
| 26902 | 1 | report_library_gap | f_L1_015 | library_gap | - | washbasin f_L1_015 floats 0.384 m above floor (S1); no real product model in the library seats correctly under the sloped ceiling — all generated models fail the fit rules | - | - |
| 26907 | 1 | report_library_gap | f_L1_021 | library_gap | - | toilet f_L1_021 floats 0.200 m above floor (S1); no real product model in the library seats correctly under the sloped ceiling — all generated models fail the fit rules | - | - |
| 26908 | 1 | report_library_gap | f_L-1_012 | library_gap | - | a:F175 (M2): the built kitchen_counter module has its top at 1.18 m, over the 0.97 m working height, and the audited library holds no kitchen_counter model to swap to (catalog returned 0 models). | - | - |
| 26921 | 1 | relayout_room | r_L0_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | AI1: 7.6 m² hall under-furnished (only a shoe cabinet); solver candidate 1 (score 9.2, best balance and circulation, no hard failures) re-solves the entrance group to furnish the hall appropriately. | ![](agent/r1_244_relayout_room_before_r_L0_koridor_2.png) | ![](agent/r1_246_relayout_room_after_r_L0_koridor_2.png) |
| 27502 | 2 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Argus: cam_r_L-1_koridor_2_1 has no free camera point in r_L-1_koridor_2; the camera is inside a proxy. The room is a 11.9 m2 hall with a shoe_cabinet and a stair, which is crowded; relayout_room with the best candidate re-places the AI pieces to  (fixes a:F239) | ![](agent/r2_003_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r2_004_relayout_room_after_r_L-1_koridor_2.png) |
| 27503 | 2 | set_material | floor | agent_override | - | Argus: The render shows a flat plain plank floor where the style lays herringbone/chevron parquet; the floor material slot was never set to a patterned look. (fixes a:F305) | - | - |
| 27517 | 2 | set_camera | r_L0_banyo | agent_override | - | Argus: The camera is pressed against a corner showing only a wall and the edge of the bathtub; re-aiming it to show the bathroom set frames the room. (fixes a:F336) | - | - |
| 27519 | 2 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The black leather office chair is a corporate piece that clashes with the calm, warm bedroom palette. Swapping to a minimal/modern chair (3dwh_54a792101c925f12bff90916) that fits the residential style will resolve the mismatch. (fixes a:F344) | ![](agent/r2_017_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r2_018_swap_model_after_r_L0_yatak_odasi.png) |
| 27521 | 2 | swap_model | f_L0_037 | adjusted_by_ai | 67.0 -> 67.0 | Argus: The black mesh office chair is a corporate piece that clashes with the warm, residential bedroom style. Swapping to a minimal/modern chair (3dwh_54a792101c925f12bff90916) that fits the residential style will resolve the mismatch. (fixes a:F346) | ![](agent/r2_019_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_020_swap_model_after_r_L0_yatak_odasi_3.png) |
| 27522 | 2 | swap_model | f_L1_030 | adjusted_by_ai | 41.0 -> 41.0 | Argus: The woven armchair f_L1_030 and its pair f_L1_031 clash with the modern white sofa f_L1_017 and brown leather chair f_L1_052; swapping to a minimal/modern/scandinavian model of the same footprint (0.69 x 0.78 m) restores a coherent set. (fixes a:F353) | ![](agent/r2_021_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_022_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 27525 | 2 | swap_model | f_L-1_070 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The brown leather armchair f_L-1_070 clashes with the white boxy sofa and the black lounge chair; the three seating pieces are of different styles and colors. Swapping to a modern model of the same footprint (0.65 x 0.78 m) restores a coher (fixes a:F364) | ![](agent/r2_023_swap_model_before_r_L-1_salon.png) | ![](agent/r2_024_swap_model_after_r_L-1_salon.png) |
| 27526 | 2 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The render is a close-up that fails to show the room's layout or main fixtures (bathtub, toilet). Setting the camera to show the shower, toilet and washbasin lets the code pick a free pose that frames the whole room. (fixes a:F366) | - | - |
| 27528 | 2 | set_material | paving | agent_override | - | Argus: The terrace floor reads as a grey-box test surface; the material stage left the outdoor floor slot untextured. (fixes a:F370) | - | - |
| 27534 | 2 | move_piece | f_L-1b_046 | adjusted_by_ai | 28.0 -> 28.0 | Snap the sofa's back onto the free span of wall w_L-1b_004 to clear the off-wall F3 finding. | ![](agent/r2_072_move_piece_before_r_L-1b_salon.png) | ![](agent/r2_075_move_piece_after_r_L-1b_salon.png) |
| 27550 | 2 | move_piece | f_L-1_031 | adjusted_by_ai | 30.0 -> 30.0 | Nudge chair f_L-1_031 slightly to resolve the 0.040 m cut with the dining table. | ![](agent/r2_090_move_piece_before_r_L-1_salon.png) | ![](agent/r2_097_move_piece_after_r_L-1_salon.png) |
| 27555 | 2 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Face the armchair toward the seating group centroid (sofa f_L-1b_041 and coffee table f_L-1b_081 to its north), fixing the F4/G3 orientation errors. | ![](agent/r2_096_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r2_107_rotate_piece_after_r_L-1b_salon_2.png) |
| 27561 | 2 | swap_model | f_L0_043 | added_by_ai | 67.0 -> 67.0 | Replace the empty dark block nightstand with a modern-minimal 2-drawer bedside cabinet (0.40 x 0.36 x 0.47 m) matching the project's modern-minimal chain and the kept 0.40 x 0.40 footprint (a:D3:f_L0_043). | ![](agent/r2_105_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r2_109_swap_model_after_r_L0_yatak_odasi_3.png) |
| 27578 | 2 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Highest-scoring untried layout (16.88) places a proper balcony group and terrace pair, resolving the sparse-furnishing and missing-seating findings. | ![](agent/r2_121_relayout_room_before_r_L1_teras.png) | ![](agent/r2_126_relayout_room_after_r_L1_teras.png) |
| 27591 | 2 | resize_piece | f_L0_011 | adjusted_by_ai | 67.0 -> 67.0 | Shrink wardrobe height from 2.99 m to 2.40 m to fit the 1.50-2.45 m range (S4). | ![](agent/r2_137_resize_piece_before_r_L0_yatak_odasi_4.png) | ![](agent/r2_143_resize_piece_after_r_L0_yatak_odasi_4.png) |
| 27594 | 2 | move_piece | f_L1_031 | adjusted_by_ai | 41.0 -> 51.0 | Nudge armchair f_L1_031 toward the coffee table f_L1_023 to close the G3 distance (2.73 m -> ~2.5 m, needs ≤ 2.5 m). | ![](agent/r2_140_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_152_move_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 27595 | 2 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 adds the second armchair to the terrace_pair (fixing the single-chair finding) and re-solves the group, replacing the flawed armchair models that caused the M33 geometry errors. | ![](agent/r2_141_relayout_room_before_r_L1_teras_2.png) | ![](agent/r2_147_relayout_room_after_r_L1_teras_2.png) |
| 27599 | 2 | remove_piece | f_L1_054 | added_by_ai | 100.0 -> 100.0 | The slim 0.60x0.25 m unit is a misread symbol: it is too small to be a real bookshelf, and the finding says the hall needs a console instead; removing it lets the entrance group be re-solved with a proper console. | ![](agent/r2_151_remove_piece_before_r_L1_koridor.png) | ![](agent/r2_154_remove_piece_after_r_L1_koridor.png) |
| 27604 | 2 | set_lighting | r_L0_e_yatak_odasi | agent_override | - | Raise room light power x2.22 so cam_r_L0_e_yatak_odasi_2 exposure fits the +3.00 EV cap (finding names x2.22). | - | - |
| 27608 | 2 | report_library_gap | f_L0_033 | library_gap | - | No audited library nightstand model fits f_L0_033 (all swap attempts rejected by fit rules or style); the parametric build stands (a:F516). | - | - |
| 27609 | 2 | report_library_gap | f_L0_034 | library_gap | - | No audited library nightstand model fits f_L0_034 (all swap attempts rejected by fit rules or style); the parametric build stands (a:F517). | - | - |
| 27610 | 2 | report_library_gap | f_L-1_003 | library_gap | - | Counter top at 1.18 m exceeds working height 0.97 m; no catalogue model at standard height exists to swap to. | - | - |
| 27611 | 2 | place_group | r_L1_koridor | added_by_ai | 100.0 -> 100.0 | Replace the removed misread unit with a proper console for the upper-floor hall, matching the L-1b hall and clearing the missing-console finding. | ![](agent/r2_156_place_group_before_r_L1_koridor.png) | ![](agent/r2_161_place_group_after_r_L1_koridor.png) |
| 27619 | 2 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Candidate 2 re-solves the entrance group to add console/coat storage so the 7.6 m² hall is not furnished only with a shoe cabinet (a:F224, a:F494, a:N169). | ![](agent/r2_168_relayout_room_before_r_L0_koridor.png) | ![](agent/r2_171_relayout_room_after_r_L0_koridor.png) |
| 27623 | 2 | retype_piece | f_L1_035 | adjusted_by_ai | 51.0 -> 54.0 | The 1.40 x 0.45 m wall piece f_L1_035 is read as a bench but a bench is not a piece of this room; retype it to a console_table that fits its size and the room, clearing F1/G14. | ![](agent/r2_176_retype_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r2_187_retype_piece_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 27629 | 2 | set_camera | r_L0_banyo | agent_override | - | a:F359: move off the tight tub-corner crop to a distinct free pose framing the bathtub with the tall cabinet, a different part of the room than cam_r_L0_banyo_1 | - | - |
| 27641 | 2 | relayout_room | r_L-1_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Reposition the entrance group to clear the camera's blocked path (P0: no free camera point, camera inside a proxy). | ![](agent/r2_194_relayout_room_before_r_L-1_koridor_2.png) | ![](agent/r2_196_relayout_room_after_r_L-1_koridor_2.png) |
| 27648 | 2 | report_library_gap | f_L0_047 | library_gap | - | Fixes a:F521: the 0.3x0.3 m tall_cabinet f_L0_047 was built parametrically below the library level because no audited library model fits its small footprint; the gap is recorded rather than forcing an invalid swap. | - | - |
| 27649 | 2 | report_library_gap | f_L0_003 | library_gap | - | c:S1:f_L0_003 / a:F312 / a:F162: no audited real-product washbasin model exists (only generated, units-guessed models, all refused by the fit rules), so the floating vessel basin and missing mirror cannot be fixed by swap | - | - |
| 27661 | 2 | resize_piece | f_L0_023 | adjusted_by_ai | 100.0 -> 100.0 | Resize wardrobe f_L0_023 to bring its height from 2.99 m down into the valid 1.50-2.45 m range. | ![](agent/r2_206_resize_piece_before_r_L0_e_yatak_odasi.png) | ![](agent/r2_208_resize_piece_after_r_L0_e_yatak_odasi.png) |
| 27674 | 2 | relayout_room | r_L0_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the hall with the top-scoring candidate (9.2, recommended, no hard failures) to add the missing entrance-group members and balance the 7.6 m² hall (a:F495). | ![](agent/r2_211_relayout_room_before_r_L0_koridor_2.png) | ![](agent/r2_214_relayout_room_after_r_L0_koridor_2.png) |
| 28253 | 3 | set_camera | r_L0_yatak_odasi_3 | agent_override | - | Argus: The bedroom render is a flat grey-box corner with the bed cut out of frame and bare walls; the camera stage framed a partial view that omits the room's key furniture. (fixes a:F382) | - | - |
| 28255 | 3 | swap_model | f_L-1_049 | adjusted_by_ai | 30.0 -> 30.0 | Argus: The armchair's brown mid-century model clashes with the white modern sectional and the room's scandinavian set; swapping to a minimal/modern/scandinavian armchair of the same footprint unifies the set. (fixes a:F385) | ![](agent/r3_001_swap_model_before_r_L-1_salon.png) | ![](agent/r3_002_swap_model_after_r_L-1_salon.png) |
| 28256 | 3 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The current view shows a bare corner (desk + wardrobe) with the bed and nightstands absent; re-aiming it to show the bed and both nightstands makes the render read as a bedroom. (fixes a:F386) | - | - |
| 28275 | 3 | swap_model | f_L1_062 | added_by_ai | 44.0 -> 44.0 | Argus: The TV unit f_L1_062 stands on the floor; the reference style (P16/R45) calls for a floating low console. The model abo_B07QB8DQ45 (1.80 x 0.41 x 0.79 m, japandi/modern) is a floating console that matches the piece's footprint and the room' (fixes a:F533) | ![](agent/r3_020_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_021_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 28279 | 3 | set_material | door | agent_override | - | Argus: The dark, heavy door frames and leaf of d_L0_001 clash with the light wood slat aesthetic. Setting the door slot to wood_oak_light will lighten the door and frames to match the corridor's warm wood style. (fixes a:F539) | - | - |
| 28280 | 3 | swap_model | f_L1_049 | added_by_ai | 44.0 -> 44.0 | Argus: The floor lamp f_L1_049 is not built and the room lacks warm layered lighting. Swapping to hssd_7ecec7264a07a6c8759f7f23f1b875079b473b89 (0.40 x 0.40 x 1.62 m, minimal/modern) provides a buildable, taller lamp that can be lit to add warm am (fixes a:F540) | ![](agent/r3_023_swap_model_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r3_024_swap_model_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 28281 | 3 | set_material | door | agent_override | - | Argus: The entrance door d_L0_005 is a plain flat wooden slab that looks like a placeholder. Setting the door slot to wood_walnut will give it a richer, more detailed wood finish with better hardware visibility, matching the modern home's style. (fixes a:F542) | - | - |
| 28286 | 3 | swap_model | f_L0_009 | adjusted_by_ai | 67.0 -> 67.0 | Replace the parametric wardrobe with a glass pane and 2.99 m height by the Newport 3-door library wardrobe (1.50 x 0.61 x 2.00 m, modern) to fix the wrong model, parametric build and height. | ![](agent/r3_073_swap_model_before_r_L0_yatak_odasi_3.png) | ![](agent/r3_077_swap_model_after_r_L0_yatak_odasi_3.png) |
| 28294 | 3 | resize_piece | f_L-1b_042 | adjusted_by_ai | 28.0 -> 28.0 | Correct swapped sofa dimensions to real product proportions (2.13 wide x 0.9 deep) | ![](agent/r3_086_resize_piece_before_r_L-1b_salon.png) | ![](agent/r3_094_resize_piece_after_r_L-1b_salon.png) |
| 28295 | 3 | rotate_piece | f_L-1b_045 | adjusted_by_ai | 18.0 -> 18.0 | Sofa front 180° on its short side is a reading error; 270° puts the long side facing the most open floor (5.83 m free). | ![](agent/r3_087_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_100_rotate_piece_after_r_L-1b_salon_2.png) |
| 28306 | 3 | move_piece | f_L-1b_046 | adjusted_by_ai | 28.0 -> 28.0 | Snap sofa back onto wall w_L-1b_004 to fix off-wall finding | ![](agent/r3_101_move_piece_before_r_L-1b_salon.png) | ![](agent/r3_115_move_piece_after_r_L-1b_salon.png) |
| 28308 | 3 | move_piece | f_L-1_042 | adjusted_by_ai | 40.0 -> 40.0 | Move chair f_L-1_042 slightly along the table row to resolve the 0.034 m cut with table_dining f_L-1_038. | ![](agent/r3_112_move_piece_before_r_L-1_salon_2.png) | ![](agent/r3_119_move_piece_after_r_L-1_salon_2.png) |
| 28310 | 3 | rotate_piece | f_L-1b_053 | adjusted_by_ai | 18.0 -> 48.0 | Armchair is 90° off the coffee table and not facing its group; 90° faces it towards the seating group. | ![](agent/r3_113_rotate_piece_before_r_L-1b_salon_2.png) | ![](agent/r3_123_rotate_piece_after_r_L-1b_salon_2.png) |
| 28315 | 3 | swap_model | f_L0_010 | adjusted_by_ai | 70.0 -> 70.0 | Replace the parametric wardrobe (S6) with a real library wardrobe (no mirrored door, F345) at a standard 2.11 m height (S4) that fits the 1.45 x 0.60 m footprint. | ![](agent/r3_121_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r3_126_swap_model_after_r_L0_yatak_odasi.png) |
| 28316 | 3 | relayout_room | r_L1_teras | adjusted_by_ai | 100.0 -> 100.0 | Candidate 3 gives a 6-piece layout (2 planters + 2-piece terrace pair) to fix the sparse-furnishing findings a:N185, a:F377, a:F173. | ![](agent/r3_122_relayout_room_before_r_L1_teras.png) | ![](agent/r3_125_relayout_room_after_r_L1_teras.png) |
| 28324 | 3 | swap_model | f_L0_038 | adjusted_by_ai | 70.0 -> 70.0 | Replace the black leather corporate office chair (F344) with a fabric ergonomic chair that fits the calm, minimal bedroom palette. | ![](agent/r3_134_swap_model_before_r_L0_yatak_odasi.png) | ![](agent/r3_136_swap_model_after_r_L0_yatak_odasi.png) |
| 28328 | 3 | rotate_piece | f_L-1b_052 | adjusted_by_ai | 28.0 -> 58.0 | Turn armchair to face the sofa and coffee table (group direction ~90°), resolving F4 and G3 | ![](agent/r3_138_rotate_piece_before_r_L-1b_salon.png) | ![](agent/r3_143_rotate_piece_after_r_L-1b_salon.png) |
| 28342 | 3 | relayout_room | r_L1_teras_2 | adjusted_by_ai | 100.0 -> 100.0 | Candidate 3 re-solves the room to build the full terrace_pair (fixing the single chair finding) and re-places the balcony planters away from the window (fixing the window collision), with a different armchair model resolving the M33 geometry gap. | ![](agent/r3_145_relayout_room_before_r_L1_teras_2.png) | ![](agent/r3_147_relayout_room_after_r_L1_teras_2.png) |
| 28356 | 3 | report_library_gap | f_L-1_003 | library_gap | - | No audited library model of kitchen_counter exists (catalogue count 0), so the 1.18 m top of f_L-1_003 cannot be fixed by swap_model; the gap is recorded for review. | - | - |
| 28361 | 3 | report_library_gap | f_L0_033 | library_gap | - | No audited modern-minimal nightstand model fits f_L0_033 (all swap attempts failed fit rules); parametric build kept (a:F516). | - | - |
| 28363 | 3 | report_library_gap | f_L0_034 | library_gap | - | No audited modern-minimal nightstand model fits f_L0_034 (all swap attempts failed fit rules); parametric build kept (a:F517). | - | - |
| 28369 | 3 | remove_camera | cam_r_L0_banyo_2 | agent_override | - | a:F365/a:F359: view pressed against a corner framing a blank wall, duplicate of cam_r_L0_banyo_1; repositioning attempts all failed camera checks in this small room | - | - |
| 28375 | 3 | report_library_gap | f_L0_048 | library_gap | - | a:F522: tall cabinet built below library level (parametric mesh); prior swap candidate was audit-removed, no usable library model remains | - | - |
| 28376 | 3 | report_library_gap | f_L0_003 | library_gap | - | a:F162/c:S1:f_L0_003/a:F312: washbasin floats +0.384 m and lacks mirror/styling; prior swaps were audit-removed or failed fit rules, no usable library model remains | - | - |
| 28377 | 3 | report_library_gap | f_L0_018 | library_gap | - | c:S1:f_L0_018: toilet floats +0.200 m; prior swap failed fit rules, no usable library model remains | - | - |
| 28395 | 3 | relayout_room | r_L0_koridor | adjusted_by_ai | 100.0 -> 100.0 | Fixes a:F224, a:F494, a:N169: re-solve the entrance group with untried candidate 3 to add the missing console/storage member for the 7.6 m² hall. | ![](agent/r3_184_relayout_room_before_r_L0_koridor.png) | ![](agent/r3_189_relayout_room_after_r_L0_koridor.png) |
| 28398 | 3 | set_camera | r_L1_koridor | agent_override | - | Reframe the corridor view to show the wardrobe, the entrance console and the door so the render is not a bare wall. | - | - |
| 28402 | 3 | remove_piece | f_L1_067 | added_by_ai | 77.0 -> 77.0 | AI-added tall_cabinet pokes through the 0.82 m sloped ceiling (X2) and has invalid height (S4); no valid spot or model fits, so it is removed. | ![](agent/r3_196_remove_piece_before_r_L1_banyo_2.png) | ![](agent/r3_203_remove_piece_after_r_L1_banyo_2.png) |
| 28403 | 3 | set_camera | r_L0_e_banyo | agent_override | - | Re-pose the first interior camera to a wider, central vantage near the door corner looking diagonally across to capture the full room layout and all main fixtures (shower, toilet, washbasin), fixing the bad_camera and close-up findings. | - | - |
| 28404 | 3 | set_camera | r_L-1_banyo | agent_override | - | Fixes a:F381: view shows a partial bathroom missing the main anchor; reposition to show the full room context with all fixtures. | - | - |
| 28412 | 3 | report_library_gap | f_L0_047 | library_gap | - | The tall_cabinet f_L0_047 is built as a parametric mesh because no suitable library model fits its 0.3x0.3m footprint and 1.6m height; swap_model attempts have already failed due to fit rules, so the library gap is formally acknowledged. | - | - |
| 28435 | 3 | relayout_room | r_L0_koridor_2 | adjusted_by_ai | 100.0 -> 100.0 | Re-solve the hall layout to address the under-furnished finding (a:F495). | ![](agent/r3_211_relayout_room_before_r_L0_koridor_2.png) | ![](agent/r3_213_relayout_room_after_r_L0_koridor_2.png) |
| 28467 | 3 | report_library_gap | f_L1_015 | library_gap | - | No audited library model of a washbasin fits under the sloped ceiling (0.81 m high) at this location; all generated models fail the fit rules (caps, height, at most 1.60 m high under the sloped ceiling). | - | - |
| 28468 | 3 | report_library_gap | f_L1_021 | library_gap | - | No audited library model of a toilet fits under the sloped ceiling (0.81 m high) at this location; all generated models fail the fit rules (caps, height, at most 1.52 m high under the sloped ceiling). | - | - |
| 29374 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | 44.0 -> 54.0 | Argus: The armchair faces the back of the sofa; every rotation either faces a wall or leaves it off-group, so the L1 living set needs a fresh solve. (fixes a:F60) | ![](agent/r4_009_relayout_room_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](agent/r4_010_relayout_room_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 29388 | 4 | set_camera | r_L0_e_banyo | agent_override | - | Argus: The render of r_L0_e_banyo hides the toilet; pointing the camera at the full set makes the room read as a bathroom. (fixes a:F139) | - | - |
| 29389 | 4 | set_camera | r_L0_yatak_odasi | agent_override | - | Argus: The render of r_L0_yatak_odasi hides the bed and nightstands, so the room reads as an office; showing the sleeping set restores the bedroom reading. (fixes a:F140) | - | - |
| 29390 | 4 | set_camera | r_L1_teras | agent_override | - | Argus: The render of r_L1_teras hides the potted plants; showing them styles the terrace. (fixes a:F141) | - | - |
| 29391 | 4 | set_camera | r_L1_teras | agent_override | - | Argus: The render of r_L1_teras hides the armchair and side table; showing the seating set makes the 19.7 m2 balcony read as a terrace. (fixes a:F142) | - | - |
| 29394 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The render omits the washbasin, toilet and tall cabinet; re-aiming the camera at the fixtures makes the room read as a bathroom. (fixes a:F146) | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 26702 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_043, f_L1_042, f_L1_039, f_L1_040 passes the camera checks: duplicate: cam_r_L1_teras_1 would show the view cam_r_L1_teras_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; duplicate: cam_r_L1_teras_1 would show the view cam_r_L1_teras_3 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_teras, or remove one of the two views; cam_r_L1_teras_1: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The terrace camera does not show the armchairs and side table. The tried_and_refused set_camera was refused because no free point shows all five pieces; however, the camera still needs to be repositioned to show as many as possible. The cod (fixes a:F13) |
| 26703 | 1 | set_camera | r_L1_banyo | show: no free camera point of r_L1_banyo shows f_L1_025, win_L1_001 (win_L1_001 not in r_L1_banyo: name its pieces, doors or windows) | Argus: The bathroom camera renders black, meaning it is inside a wall or under the floor. Moving it to a free point with headroom that shows the shower and window will fix the render. (fixes a:F14) |
| 26705 | 1 | relayout_room | r_L-1_salon | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_071, looking at it | Argus: The armchair stands behind the back of the sofa_corner f_L-1_053; four rotate_piece attempts were refused (still behind the back, or facing a wall 0.11 m ahead), so the defect is the group layout, not a single rotation. (fixes a:F29) |
| 26706 | 1 | set_camera | r_L0_e_banyo | show: none of the 3 best poses of r_L0_e_banyo that show f_L0_015 passes the camera checks: duplicate: cam_r_L0_e_banyo_1 would show the view cam_r_L0_e_banyo_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_banyo, or remove one of the two views | Argus: The toilet f_L0_015 is built in r_L0_e_banyo but the camera does not show it. The fix is to point the camera at the toilet so the render shows the primary fixture. (fixes a:F133) |
| 26707 | 1 | set_camera | r_L1_teras | show: none of the 8 best poses of r_L1_teras that show f_L1_041, f_L1_043 passes the camera checks: cam_r_L1_teras_2: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L1_teras_2: furniture and fixtures fill 5% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L1_teras_2: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The terrace r_L1_teras has furniture (armchair, potted_plant, side_table) but the camera angle hides it, making the room look empty. The fix is to point the camera at the furniture so the render shows the seating area. (fixes a:F136) |
| 26710 | 1 | swap_model | f_L-1_056 | acceptance: pin_refused: f_L-1_056: hssd_c878d6d2cca3590cb1e1b7e33642a8f505a7feef: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The drawn 1.83 x 0.80 m shower is within 30% of the real bathtub range, so fix_fixture (size) is refused and the bare tub rim stays; swapping to a real shower model of the same type that fits the bay restores the missing taps and rail. (fixes a:F161) |
| 26711 | 1 | swap_model | f_L0_003 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The washbasin stands 0.00 m2 outside the room in door d_L0_007, so fix_fixture (place) is refused and the bare wall stays; swapping to a real washbasin model of the same type that fits the room restores the missing mirror. (fixes a:F162) |
| 26712 | 1 | swap_model | f_L0_006 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Argus: The washbasin's model fails the fit rules, so swap_model is refused and the bare wall stays; swapping to a real washbasin model of the same type that fits the room restores the missing mirror. (fixes a:F163) |
| 26713 | 1 | set_camera | r_L0_e_yatak_odasi | show: none of the 8 best poses of r_L0_e_yatak_odasi that show d_L0_002 passes the camera checks: duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_2 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views; duplicate: cam_r_L0_e_yatak_odasi_1 would show the view cam_r_L0_e_yatak_odasi_3 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_e_yatak_odasi, or remove one of the two views; cam_r_L0_e_yatak_odasi_1: none of the room's main pieces (bed_double, wardrobe) is in its frame, while the room's camera search frames one | Argus: The camera cam_r_L0_e_yatak_odasi_1 does not show door d_L0_002; setting show to [d_L0_002] makes the code pick a free pose that shows the door. (fixes a:F164) |
| 26714 | 1 | add_camera | ext_8 | the target is the position, the camera stands inside the building (level L-1), the camera stands under the roof, eye height 4.94 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, 0) is at z -3.34 m: use z -1.84 to -1.64 for an eye-level view | Argus: The frontal view of the entrance (+y) facade is missing; adding an exterior camera at eye height outside the building restores the view. (fixes a:F165) |
| 26715 | 1 | set_material | plot_wall | plot_wall: stone_wall_ashlar is another stone than the house's base stone_wall_ledgestone: one stone per house (the plinth, the plot walls and the facade's base match; UL204) | Argus: The retaining wall is a bare concrete slab; setting the plot_wall slot to a stone look matches the facade and removes the unfinished look. (fixes a:F166) |
| 26721 | 1 | set_camera | r_L-1_koridor_2 | show: none of the 4 best poses of r_L-1_koridor_2 that show d_L-1_003 passes the camera checks: cam_r_L-1_koridor_2_1: furniture and fixtures fill 1% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L-1_koridor_2_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L-1_koridor_2_1: furniture and fixtures fill 0% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The view shows only closed doors and a bare wall; re-aiming it to show the open door into the room fixes it. (fixes a:F191) |
| 26725 | 1 | place_group | r_L1_banyo_2 | no_change: r_L1_banyo_2 already has its bathroom_set r_L1_banyo_2.bathroom_set (anchor f_L1_022, members f_L1_016, f_L1_026): nothing missing, never a second set | Argus: The room's bathroom set is missing the tall_cabinet that every other bathroom in the project has; completing the set adds it. (fixes a:F209) |
| 26726 | 1 | retype_piece | f_L1_054 | retype: console_table is no candidate for f_L1_054 (0.60 x 0.25 m at [4.07, 7.74]): the size table and the room / zone give bookshelf, floor_lamp, potted_plant, shoe_cabinet | Argus: The L1 hall has a shoe_cabinet which is inappropriate for an upper floor; the L-1b hall has a console_table as the correct type. (fixes a:F216) |
| 26727 | 1 | place_group | r_L0_e_banyo_2 | no_change: r_L0_e_banyo_2 already has its bathroom_set r_L0_e_banyo_2.bathroom_set (anchor f_L0_014, members f_L0_004, f_L0_016): nothing missing, never a second set | Argus: The en-suite bathroom is missing the tall_cabinet that its twin has; completing the set adds it. (fixes a:F218) |
| 26728 | 1 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | Argus: The room is typed 'other' but is furnished and used as a living room; the documents name it a game/activity/relaxation room which is functionally a living space. (fixes a:F219) |
| 26729 | 1 | retype_piece | f_L1_018 | retype: console_table is no candidate for f_L1_018 (2.10 x 0.90 m at [10.96, 4.02]): the size table and the room / zone give chaise, sofa, table_dining | Argus: The L1 hall has a shoe_cabinet which is inappropriate for an upper floor; the L-1b hall has a console_table as the correct type. (fixes a:F222) |
| 26730 | 1 | retype_piece | f_L1_018 | no_change: f_L1_018 is already a sofa | Argus: The L1 living/play-and-rest room is furnished with two white bed-like daybeds with drawer fronts, not upholstered sofas; a daybed is not appropriate in a living room. (fixes a:F223) |
| 26731 | 1 | place_group | r_L0_koridor | no_change: r_L0_koridor already has its entrance r_L0_koridor.entrance (anchor None, members f_L0_039): nothing missing, never a second set | Argus: The L0 hall is furnished only with a shoe_cabinet; a 7.6 m2 hall with 12 doors needs a console or coat storage to be usable. (fixes a:F224) |
| 26734 | 1 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G4:f_L0_021 is still there after the edit (bed_double f_L0_021: no nightstand on the free left side of the head (0.37 m free)); 1 more kept | Re-solve layout to fix bed side clearances (G5) and add the missing second nightstand (F500/G4). |
| 26738 | 1 | swap_model | f_L0_010 | lower_quality: f_L0_010: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Replace the mirrored-door wardrobe (reflecting a non-existent furnished room) and the parametric mesh with the Leon Wardrobe, a real library model at 1.478x0.61x1.993 m that fits the 1.45x0.60 footprint, has a normal height and a calm scandinavian palette. |
| 26739 | 1 | swap_model | f_L0_038 | asset_unusable: chinese_armchair is not used: audit pending | Replace the black leather corporate office chair with the Chinese Armchair, a soft japandi/minimal seat that matches the warm bedroom palette and light wood desk instead of reading as an office. |
| 26740 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the below-library parametric nightstand mesh with the Side Table 01, a real library nightstand model (0.55x0.45x0.55 m) in a scandinavian/minimal style that matches the room. |
| 26741 | 1 | rotate_piece | f_L-1_070 | f_L-1_070: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Face the armchair into the seating group instead of the back of the sofa, resolving F4 orientation and G11 walkway findings. |
| 26742 | 1 | rotate_piece | f_L-1_101 | f_L-1_101: inside_room, f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility 30 -> 10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F9 f_L-1_101: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; G1 f_L-1_101: TV unit f_L-1_101 90° off the line to the sofa, needs ≤ 10°) | Face the TV unit into the seating area instead of the back of armchair f_L-1_071, resolving the F4 orientation finding. |
| 26745 | 1 | move_piece | f_L-1b_046 | snap: f_L-1b_046: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 0.59 m off the wall; snap its back onto the right wall span s3. |
| 26747 | 1 | swap_model | f_L0_010 | lower_quality: f_L0_010: hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Replace the mirrored-door wardrobe (reflecting a non-existent furnished room) and the parametric mesh with the Newport Three-plus Door Wardrobe, a real library model at 1.50x0.61x2.00 m that fits the 1.45x0.60 footprint with a normal height and a calm minimal/scandinavian palette. |
| 26750 | 1 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 30 -> 20 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Rotate armchair f_L-1_072 to face away from the back of sofa f_L-1_054, fixing the orientation finding. |
| 26751 | 1 | rotate_piece | f_L1_052 | f_L1_052: clearance_ok, score: plausibility 41 -> 21 (F4 f_L1_052: armchair faces a wall 0.02 m in front of it; F4 f_L1_062: tv_unit stands behind the back of f_L1_052, looking at it; F6 f_L1_052: armchair: the free zone in front of it is reaches out of the room) | Turn the reading-corner armchair away from the back of sofa f_L1_017 so it no longer stands behind the sofa looking at it. |
| 26752 | 1 | move_piece | f_L-1b_046 | drawn_lock: f_L-1b_046: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.35 m) | Sofa back is 0.59 m off the wall; shift it right so its back meets the right wall (span s3). |
| 26753 | 1 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B079VKDKC1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the below-library parametric nightstand mesh with the Movian High Gloss 2 Drawer Bedside Cabinet (White and Walnut, 0.40x0.36x0.47 m), a real library nightstand that fits the 0.4x0.4 footprint and the room's height rules. |
| 26754 | 1 | move_piece | f_L1_036 | score: plausibility 41 -> -29 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_020: sofa f_L1_020: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Pull the coffee table off the wall and into the free zone in front of sofa f_L1_020 (front faces 270°). |
| 26755 | 1 | rotate_piece | f_L-1_102 | score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of it) | Rotate tv_unit f_L-1_102 to face away from the back of armchair f_L-1_069, fixing the orientation finding. |
| 26756 | 1 | move_piece | f_L1_063 | snap: f_L1_063: no free place on wall w_L1_001 (doors, windows) | Snap tv_unit back onto the north wall span s0 so its back is on a wall (F3 off-wall 1.01 m). |
| 26758 | 1 | rotate_piece | f_L1_029 | f_L1_029: clearance_ok, score: plausibility 21 -> -9 (F4 f_L1_029: armchair faces a wall 0.23 m in front of it; F6 f_L1_029: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_029: armchair f_L1_029 is 160° off the sofa f_L1_018 (needs ≤ 30°) at 2.29 m (needs ≤ 2.50 m); G11 f_L1_029: armchair f_L1_029: its front use zone is not reached by a 0.60 m walkway from door d_L1_002) | Turn armchair f_L1_029 to face the TV unit on the north wall instead of standing behind its back (F4). |
| 26760 | 1 | rotate_piece | f_L-1b_041 | f_L-1b_041: no_overlap, f_L-1b_081: no_overlap, score: plausibility 18 -> -32 (F3 f_L-1b_041: sofa: its back is not on a wall (2.24 m off); F4 f_L-1b_041: sofa does not face its group (f_L-1b_081); F4 f_L-1b_054: armchair does not face its group (f_L-1b_081, f_L-1b_041, f_L-1b_045); F4 f_L-1b_084: armchair stands behind the back of f_L-1b_045, f_L-1b_041, looking at it) | Sofa had no front; code suggests 270° towards its partner across the open floor (a:F213, a:F502, a:F233). |
| 26762 | 1 | swap_model | f_L0_042 | off_style: f_L0_042: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the below-library parametric nightstand mesh with the Classic Nightstand 01, a real library nightstand model (0.57x0.42x0.70 m) that fits the 0.4x0.4 footprint and the room's height rules. |
| 26764 | 1 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071)); 1 more kept | Armchair is 89° off its group; rotate it to face the sofa/coffee table (front 180°). |
| 26765 | 1 | move_piece | f_L1_036 | acceptance: finding F6:f_L1_020 is still there after the edit (sofa: the free zone in front of it is blocked by f_L1_017); 1 more kept | Nudge the coffee table 0.14 m off the wall into the free zone in front of sofa f_L1_020 (front faces 270°) without blocking the walkway. |
| 26767 | 1 | move_piece | f_L1_063 | f_L1_029: no_overlap, f_L1_032: no_overlap, f_L1_063: inside_room, f_L1_063: no_overlap | Move tv_unit to the free north wall span s0 so its back is on the wall (F3 off-wall 1.01 m). |
| 26770 | 1 | move_piece | f_L1_031 | f_L1_030: clearance_ok, f_L1_030: no_overlap, f_L1_031: no_overlap | Bring the armchair closer to the coffee table f_L1_023 (within 2.5 m) while keeping its front aligned with the table. |
| 26771 | 1 | rotate_piece | f_L1_029 | f_L1_029: clearance_ok, score: plausibility 21 -> 1 (F4 f_L1_029: armchair does not face its group (f_L1_063, f_L1_018, f_L1_024); F6 f_L1_029: armchair: the free zone in front of it is blocked by f_L1_032; G3 f_L1_029: armchair f_L1_029 is 83° off the table_coffee f_L1_024 (needs ≤ 30°) at 2.69 m (needs ≤ 2.50 m)) | Turn armchair f_L1_029 to face the seating group (south) so it no longer stands behind the back of the tv_unit (F4). |
| 26775 | 1 | move_piece | f_L0_045 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.13 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.08 m from the bed side (needs ≤ 0.30 m)) | Shift the nightstand 0.35 m away from the window band so it no longer stands in front of win_L0_004 (G12). |
| 26776 | 1 | move_piece | f_L-1_074 | score: plausibility 40 -> 30 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move table_coffee f_L-1_074 away from armchair f_L-1_069 to resolve the 0.12 m² overlap. |
| 26777 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: F3 f_L1_084: tv_unit: its back is not on a wall (1.01 m off); F4 f_L1_029: armchair stands behind the back of f_L1_084, looking at it; F4 f_L1_032: armchair stands behind the back of f_L1_084, looking at it | Re-place the AI pieces (tv_unit, armchairs, lamps, storage) with the solver's best candidate to fix the off-wall tv_unit, the armchairs behind backs, and the seating group layout. |
| 26779 | 1 | rotate_piece | f_L-1b_054 | acceptance: finding G3:f_L-1b_054 is still there after the edit (armchair f_L-1b_054 is 99° off the table_coffee f_L-1b_081 (needs ≤ 30°) at 1.29 m (needs ≤ 2.50 m)) | Armchair faces 0° but must face its group (sofa f_L-1b_041) to the south; 180° clears the 33° G3 offset (c:F4, c:G3, a:F238, a:F608). |
| 26780 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Slide the wardrobe along the north wall to open ≥0.80 m of clearance in front of its doors (G13). |
| 26781 | 1 | move_piece | f_L-1_074 | score: plausibility 40 -> 30 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.05 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move table_coffee f_L-1_074 further from armchair f_L-1_069 to fully resolve the overlap. |
| 26782 | 1 | move_piece | f_L-1b_051 | drawn_lock: f_L-1b_051: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.70 m) | Armchair's front zone is blocked by f_L-1b_052 and it is 33° off the sofa; move it to a clearer spot facing the sofa. |
| 26783 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 50 (F3 f_L0_020: bed_double: the headboard stands in the room (0.17 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.17 m toward the left wall to open ≥0.60 m along its right side (G5). |
| 26785 | 1 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 48 -> 28 (F4 f_L-1b_084: armchair faces a wall 0.02 m in front of it; F6 f_L-1b_084: armchair: the free zone in front of it is reaches out of the room; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Reading-corner armchair stands behind the back of sofa f_L-1b_045 looking at it; turn it to face the open floor (c:F4). |
| 26789 | 1 | rotate_piece | f_L-1b_051 | f_L-1b_051: no_overlap, f_L-1b_052: no_overlap, score: plausibility 58 -> 38 (F4 f_L-1b_051: armchair does not face its group (f_L-1b_071, f_L-1b_042, f_L-1b_046); G3 f_L-1b_051: armchair f_L-1b_051 is 53° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m); G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Armchair is 33° off the sofa; rotate its front toward the sofa to align within 30°. |
| 26791 | 1 | move_piece | f_L0_045 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 60 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.16 m²) | Shift the nightstand 0.44 m away from the window band so it no longer stands in front of win_L0_004 (G12). |
| 26792 | 1 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | group checks: F3 f_L1_085: tv_unit: its back is not on a wall (1.01 m off); F4 f_L1_029: armchair stands behind the back of f_L1_085, looking at it; F4 f_L1_032: armchair stands behind the back of f_L1_085, looking at it | Try the solver's second candidate, which re-places the seating group (2 members) and living storage, to fix the off-wall tv_unit and the armchairs behind backs. |
| 26793 | 1 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has only 0.78 m behind it, needs 0.81 m; shift 0.16 m away from the wall (c:G6). |
| 26794 | 1 | move_piece | f_L1_007 | acceptance: finding G6:f_L1_007 is still there after the edit (chair f_L1_007: 0.65 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair to the left side of the dining table so it no longer cuts the table and gains the 0.81 m clearance behind it. |
| 26795 | 1 | move_piece | f_L-1_074 | f_L-1_072: no_overlap | Move table_coffee f_L-1_074 to the left, away from armchair f_L-1_069 at [9.79, 0.97], to resolve the overlap. |
| 26796 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Slide the wardrobe to the far end of the north wall so the desk no longer blocks its door swing and ≥0.80 m is free in front (G13). |
| 26797 | 1 | mark_not_furniture | f_L-1b_001 | no_crop: f_L-1b_001 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/r_L-1b_salon_2_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | 5.14 x 2.37 m untyped cluster larger than 4.5 m on a side: a group of drawn pieces, not a single piece of furniture (c:NR). |
| 26799 | 1 | rotate_piece | f_L-1b_051 | acceptance: finding G3:f_L-1b_051 is still there after the edit (armchair f_L-1b_051 is 123° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m)) | Armchair is 33° off the sofa which is to its west; rotate its front to 270° to face the sofa. |
| 26801 | 1 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a real library nightstand model to fix the below_library P7 finding. |
| 26802 | 1 | move_piece | f_L0_020 | snap: f_L0_020: no free place on wall w_L0_015 (doors, windows, at most 1.2 m from the drawn place) | Snap the bed's headboard back onto the left wall and centre it so ≥0.60 m is free along both sides (G5). |
| 26804 | 1 | move_piece | f_L-1b_045 | snap: f_L-1b_045: no free place on wall w_L-1b_010 (doors, windows, at most 1.2 m from the drawn place) | Sofa back is 0.59 m off the wall; snap its back onto the west wall (a:F3). |
| 26805 | 1 | move_piece | f_L-1_074 | max_tries: f_L-1_074 was edited 3 times in this round | Move table_coffee f_L-1_074 up and slightly left to clear both armchair f_L-1_069 and armchair f_L-1_072. |
| 26806 | 1 | swap_model | f_L0_011 | lower_quality: f_L0_011: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Replace the parametric wardrobe with the audited Leon Wardrobe library model (1.478 x 0.61 x 1.993 m, close to the drawn 1.45 x 0.60) to clear the S6 wrong_model finding. |
| 26807 | 1 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a real library nightstand model to fix the below_library P7 finding. |
| 26809 | 1 | move_piece | f_L1_007 | drawn_lock: f_L1_007: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.64 m) | Move the chair to the near (south) side of the dining table where the open floor gives the 0.81 m pull-out clearance behind it. |
| 26810 | 1 | relayout_room | r_L-1_salon_2 | group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_069, looking at it | Use solver candidate 1 to re-layout the room, aiming to fix the G11 walkway clearance issues for the seating group and the F4 orientation issues. |
| 26811 | 1 | relayout_room | r_L-1b_salon | group checks: F4 f_L-1b_096: tv_unit stands behind the back of f_L-1b_051, looking at it; G9 r_L-1b_salon_kitchen: kitchen r_L-1b_salon_kitchen has no fridge (fridge) | Let the solver re-place the seating group to resolve the armchair orientation (G3) and clearance findings holistically. |
| 26812 | 1 | swap_model | f_L0_011 | lower_quality: f_L0_011: hssd_d47861b542c4f2e8fe9adcf86d55e26e12d1a213 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Replace the parametric wardrobe with the audited Newport Three-plus Door Wardrobe (1.4994 x 0.6134 x 1.9995 m, close to the drawn 1.45 x 0.60) to clear the S6 wrong_model finding. |
| 26813 | 1 | move_piece | f_L0_045 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.16 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.12 m from the bed side (needs ≤ 0.30 m)) | Shift the nightstand 0.54 m away from the window band so it no longer stands in front of win_L0_004 (G12). |
| 26815 | 1 | move_piece | f_L-1b_045 | drawn_lock: f_L-1b_045: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 1.43 m) | Sofa back is 0.59 m off the west wall; shift 0.43 m west so its back sits on the wall (a:F3). |
| 26816 | 1 | move_piece | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.64 m free in front, needs ≥ 0.80 m) | Slide the wardrobe to the far end of the north wall so the desk no longer blocks its door swing and ≥0.80 m is free in front (G13). |
| 26817 | 1 | swap_model | f_L0_033 | off_style: f_L0_033: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric mesh with a real library nightstand model to fix the below_library P7 finding. |
| 26818 | 1 | relayout_room | r_L-1_salon_2 | candidate: candidate 2 does not exist: 1 usable candidate(s) | Use solver candidate 2 to re-layout the room, aiming to fix the G11 walkway clearance issues for the seating group. |
| 26819 | 1 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Chair has only 0.78 m clearance behind it (needs 0.81 m); shift it slightly to gain the required clearance. |
| 26820 | 1 | swap_model | f_L0_011 | asset_unusable: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e is not used: audit removed | Replace the parametric wardrobe with the audited Cream Triple Wardrobe (1.47 x 0.5488 x 1.7522 m, close to the drawn 1.45 x 0.60) to clear the S6 wrong_model finding. |
| 26821 | 1 | move_piece | f_L1_038 | drawn_lock: f_L1_038: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 3.17 m) | Move coffee table f_L1_038 to be between sofa f_L1_019 and the tv_unit f_L1_063 (G2). |
| 26822 | 1 | move_piece | f_L1_007 | memory: the same edit was rejected in round 1: acceptance: finding G6:f_L1_007 is still there after the edit (chair f_L1_007: 0.65 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair to the left side of the dining table so it no longer cuts the table footprint. |
| 26823 | 1 | move_piece | f_L-1b_045 | max_tries: f_L-1b_045 was edited 3 times in this round | Sofa back is 0.59 m off the west wall; shift 0.3 m west, the maximum allowed for a drawn piece, to bring its back onto the wall (a:F3). |
| 26825 | 1 | move_piece | f_L0_020 | score: plausibility 70 -> 50 (F3 f_L0_020: bed_double: the headboard stands in the room (0.27 m off); G5 f_L0_020: bed_double f_L0_020: 0.54 m free along the right side, needs ≥ 0.60 m) | Shift the bed 0.27 m toward the left wall to open ≥0.60 m along its right side (G5). |
| 26826 | 1 | move_piece | f_L1_007 | max_tries: f_L1_007 was edited 3 times in this round | Move the chair to the left side of the dining table (0.3 m) so it no longer cuts the table footprint. |
| 26827 | 1 | swap_model | f_L0_011 | max_tries: f_L0_011 was edited 3 times in this round | Replace the parametric wardrobe with the audited Oscar 3-door Wardrobe (1.52 x 0.6232 x 2.08 m, close to the drawn 1.45 x 0.60) to clear the S6 wrong_model finding. |
| 26828 | 1 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a real modern-minimal library nightstand model to fix the below_library P7 finding. |
| 26830 | 1 | rotate_piece | f_L1_059 | acceptance: finding F4:f_L1_059 is still there after the edit (armchair stands behind the back of f_L1_063, looking at it) | Turn armchair f_L1_059 to face the sofa f_L1_018 (west) so it no longer stands behind the back of the sofa (F4). |
| 26836 | 1 | retype_piece | f_L-1_022 | retype: sideboard is no candidate for f_L-1_022 (5.54 x 0.60 m at [14.67, 4.27]): the size table and the room / zone give none | Retype the untyped drawn piece f_L-1_022 (5.54 x 0.60 m) as a sideboard to resolve the untyped finding. |
| 26838 | 1 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m); 1 more kept | Re-solve the room layout to center the bed, creating 0.60 m clearance on both sides and space for a second nightstand, fixing the G5 clearance and G4/AI1 missing member findings. |
| 26841 | 1 | swap_model | f_L-1_003 | asset_exists: no catalogue model 'kitchen_counter_standard' | M2: counter top at 1.18 m over working height 0.97 m; swap to a standard-height kitchen counter module. |
| 26842 | 1 | swap_model | f_L0_033 | max_tries: f_L0_033 was edited 3 times in this round | Replace the parametric mesh with a real scandinavian/modern library nightstand model to fix the below_library P7 finding. |
| 26844 | 1 | relayout_room | r_L0_yatak_odasi_4 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m); 1 more kept | Re-solve the room layout with the second solver candidate to center the bed, creating 0.60 m clearance on both sides and space for a second nightstand, fixing the G5 clearance and G4/AI1 missing member findings. |
| 26845 | 1 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B01D3C7Z4A: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a real scandinavian/modern library nightstand model to fix the below_library P7 finding. |
| 26848 | 1 | set_camera | r_L1_koridor | show: none of the 8 best poses of r_L1_koridor that show f_L1_027, f_L1_054, d_L1_001, d_L1_003 passes the camera checks: cam_r_L1_koridor_1: none of the room's main pieces (wardrobe) is in its frame, while the room's camera search frames one; cam_r_L1_koridor_1: furniture and fixtures fill 6% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Reframe the corridor view to show the storage and entrance pieces plus doors, giving the render depth and content to address the bare/unfinished critique. |
| 26849 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Q13: worktop empty and no upper cabinets/hood; re-solve the kitchen_run group to add small worktop items and upper cabinets/hood over the stove. |
| 26850 | 1 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: abo_B07K7YMBNY: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replacing the bare parametric grid with a styled solid-wood shoe cabinet (Hayes Riva, Wild Oak) that fits the 0.6m width and reads as designed furniture in the hall. |
| 26853 | 1 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: abo_B079VKDKC1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric mesh with a real modern-minimal library nightstand model to fix the below_library P7 finding. |
| 26854 | 1 | set_camera | r_L-1_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The current close-up corner view cuts off the shower and cabinet; reposition to a wider interior view showing the main fixtures so the room can be judged as a whole. |
| 26859 | 1 | swap_model | f_L-1_094 | acceptance: pin_refused: f_L-1_094: abo_B07GFDZVYY: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swapping to a styled 1-door shoe cabinet with mirror (Movian Indre, Light Brown Oak-Effect, 0.5m wide) that fits the 0.6m footprint and provides doors and finish instead of a bare parametric grid. |
| 26860 | 1 | set_camera | r_L-1_banyo | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes J1 a:F381 (room r_L-1_banyo): the close-up corner view cuts off the shower and cabinet; reposition to a wider interior view showing the main fixtures so the room can be judged as a whole. |
| 26862 | 1 | set_camera | r_L0_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | a:F359: the frame is a low tight crop of the tub corner; reframe to show the main group (washbasin, toilet, tall cabinet) as a designed space. |
| 26864 | 1 | set_camera | r_L-1_banyo | max_tries: r_L-1_banyo was edited 3 times in this round | Fixes J1 a:F381 (room r_L-1_banyo): the close-up corner view cuts off the shower and cabinet; reposition to a wider interior view showing the main fixtures so the room can be judged as a whole. |
| 26865 | 1 | swap_model | f_L0_034 | max_tries: f_L0_034 was edited 3 times in this round | Replace the parametric mesh with a real modern-minimal library nightstand model to fix the below_library P7 finding. |
| 26866 | 1 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | washbasin model floats 0.384 m above the floor; swap to a floor-standing model that seats on the floor |
| 26872 | 1 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | washbasin floats 0.384 m above floor; try a model that seats on the floor |
| 26875 | 1 | set_camera | r_L0_koridor | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Wider, higher vantage to capture the full hall circulation, the new console/storage and the stair, instead of a tight low corner shot. |
| 26878 | 1 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | toilet floats 0.200 m above floor; swap to a model that sits on the floor |
| 26879 | 1 | retype_piece | f_L1_028 | retype: wardrobe is no candidate for f_L1_028 (1.52 x 0.60 m at [12.61, 9.90]): the size table and the room / zone give bench, dresser | RC finding: vector geometry (hanging rail with hangers) outranks the AI-passed 'bench' type; the piece is a coat closet, so retype it to the correct type that fits its 1.52x0.60 footprint and the hall room. |
| 26880 | 1 | set_camera | r_L0_e_banyo | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Re-pose from the SE corner to a wider 20mm view of the vanity wall showing washbasin and toilet, distinct from cam_r_L0_e_banyo_2's shower/cabinet framing. |
| 26885 | 1 | set_camera | r_L0_koridor | memory: the same edit was rejected in round 1: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fix a:F367 (J1): wider, higher vantage to capture the full hall circulation, the new console/storage and the stair, instead of a tight low corner shot. |
| 26886 | 1 | place_group | r_L-1_mutfak | no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Q13: worktop empty and no upper cabinets/hood; re-solve the kitchen_run with option I to add small worktop items and upper cabinets/hood over the stove. |
| 26889 | 1 | retype_piece | f_L1_028 | acceptance: finding RC:f_L1_028 is still there after the edit (f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | RC finding: vector geometry (hanging rail with hangers) outranks the AI-passed 'bench' type; the piece is a coat closet, so retype it to the correct type that fits its 1.52x0.60 footprint and the hall room. |
| 26890 | 1 | set_camera | r_L0_e_banyo | set: position is required | Reframe the fixed pose to look across the vanity wall (washbasin and toilet) instead of the shower, fixing the close-up corner framing of a:F360. |
| 26891 | 1 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_052, d_L0_001, d_L0_005 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 9% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Fix a:F367 (J1): show the full hall circulation with the new console/storage and the stair, instead of a tight low corner shot. |
| 26893 | 1 | swap_model | f_L1_067 | acceptance: pin_refused: f_L1_067: abo_B07H8PQFR2: fails the fit rules (caps, height, at most 0.77 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | tall_cabinet f_L1_067 was built as a parametric mesh below library level; the 0.40x0.57x1.85 m Movian Moselle vitrina matches its 0.40 m front width and gives a real library model. |
| 26894 | 1 | set_camera | r_L0_e_banyo | max_tries: r_L0_e_banyo was edited 3 times in this round | Reframe the fixed pose to look across the vanity wall (washbasin and toilet) instead of the shower, fixing the close-up corner framing of a:F360. |
| 26895 | 1 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_052, o_L0_001 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 9% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Fix a:F367 (J1): frame the hall's main pieces (shoe cabinet, new console/storage) and the stair opening so the view shows the circulation space, not a bare corner. |
| 26900 | 1 | set_camera | r_L0_koridor | max_tries: r_L0_koridor was edited 3 times in this round | Fix a:F367 (J1): from the free point near the hall's far end, a wider 18mm lens at eye height frames the full circulation, the shoe cabinet, the new console/storage and the stair opening. |
| 26904 | 1 | swap_model | f_L1_016 | pin_refused: f_L1_016: gen_washbasin_modern_minimal_1_d5536003: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | washbasin f_L1_016's current model floats 0.384 m above its floor; the 0.64x0.48x0.64 m modern minimal washbasin sits on the floor and fits the 1.0x0.55 m drawn footprint. |
| 26909 | 1 | swap_model | f_L1_022 | pin_refused: f_L1_022: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | toilet f_L1_022's current model floats 0.200 m above its floor; the 0.42x0.69x0.57 m japandi toilet matches the 0.5x0.69 m drawn footprint and sits on the floor. |
| 26910 | 1 | fix_fixture | f_L-1_010 | fixture_place: f_L-1_010: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_004) | c:R3:d_L-1_004: door d_L-1_004 swings into the drawn kitchen_counter f_L-1_010 on one hinge side; nudge the counter (up to 0.5 m) to clear the swing. |
| 26913 | 1 | move_piece | f_L1_067 | acceptance: finding X2:f_L1_067 is still there after the edit (f_L1_067: tall_cabinet with its top 1.60 m above the floor stands where the sloped ceiling is 0.82 m high; it shows through the ceiling) | tall_cabinet f_L1_067 stands where the sloped ceiling is only 0.82 m high and shows through it; moving it to the free span s3 on the south wall (into the room, away from the slope) clears the ceiling. |
| 26916 | 1 | swap_model | f_L-1_094 | memory: the same edit was rejected in round 1: acceptance: pin_refused: f_L-1_094: abo_B07GFDZVYY: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swapping to the Movian Indre 1-door shoe cabinet with mirror (Light Brown Oak-Effect, 0.5m x 0.23m x 1.79m) that matches the resized footprint and provides doors and styling instead of a bare parametric grid. |
| 26924 | 1 | move_piece | f_L1_067 | snap: f_L1_067: no free place on wall w_L1_007 (doors, windows) | tall_cabinet f_L1_067 shows through the sloped ceiling at its current spot; moving it to the far end of the free span s3 on the south wall (into the room, away from the slope) clears the ceiling. |
| 26925 | 1 | swap_model | f_L-1_094 | max_tries: f_L-1_094 was edited 3 times in this round | Swapping to the Movian Indre 1-door shoe cabinet with mirror (Dark Grey, 0.5m x 0.23m x 1.79m) that matches the resized footprint and provides doors and styling instead of a bare parametric grid. |
| 26926 | 1 | set_room_type | r_L0_banyo | max_tries: r_L0_banyo was edited 3 times in this round | Re-furnish the L0 wet room per the plan, which shows a shower, not the placed bathtub (finding a:N167). |
| 26933 | 1 | retype_piece | f_L1_028 | acceptance: finding RC:f_L1_028 is still there after the edit (f_L1_028: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | RC finding: the AI passes typed it bench; vector geometry says coat closet. Retype to bench (the size-table candidate) to see if it resolves the wrong_type finding. |
| 26934 | 1 | move_piece | f_L1_067 | max_tries: f_L1_067 was edited 3 times in this round | tall_cabinet f_L1_067 shows through the sloped ceiling at its current spot; moving it to the open middle of the room (south of the slope, clear of the door swing and the fixtures) clears the ceiling. |
| 27500 | 2 | set_front | f_L1_035 | has_front: f_L1_035 faces 270° already: rotate_piece turns it | Argus: f_L1_035 is a bench whose AI front (180 deg, on its short side) is a reading error; the correct front is 270 deg, the long side, with its back on the only wall side. The retype was refused (bench is no candidate for its size/room), so the f (fixes a:F230) |
| 27501 | 2 | set_front | f_L1_037 | has_front: f_L1_037 faces 270° already: rotate_piece turns it | Argus: f_L1_037 is a bench whose AI front (0 deg, on its short side) is a reading error; the correct front is 270 deg, the long side, with its back on the only wall side. The fix is to set the correct front. (fixes a:F231) |
| 27504 | 2 | swap_model | f_L-1_054 | asset_unusable: 3dwh_e5f77d70d0615bd56772bf1f is not used: audit removed | Argus: The current model's parts stand 2.7 cm apart; the only other candidate (3dwh_c7ebbb3791debf3dc433074c) was audit-removed, so swap to the next available corner sofa model. (fixes a:F309) |
| 27505 | 2 | swap_model | f_L-1_025 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; the two other candidates were audit-removed, so swap to the remaining available model. (fixes a:F310) |
| 27506 | 2 | swap_model | f_L-1_026 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; the two other candidates were audit-removed and max_tries was hit, so swap to the remaining available model. (fixes a:F311) |
| 27507 | 2 | swap_model | f_L0_003 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; the generated models were pin-refused and fix_fixture found no valid spot, so swap to the remaining available model. (fixes a:F312) |
| 27508 | 2 | swap_model | f_L0_004 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; the generated model was pin-refused, so swap to the remaining available model. (fixes a:F313) |
| 27509 | 2 | swap_model | f_L0_005 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; the generated models were pin-refused, so swap to the remaining available model. (fixes a:F314) |
| 27510 | 2 | swap_model | f_L0_006 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; no swap was attempted yet, so swap to the remaining available model. (fixes a:F315) |
| 27511 | 2 | swap_model | f_L1_015 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; no swap was attempted yet, so swap to the remaining available model. (fixes a:F316) |
| 27512 | 2 | swap_model | f_L1_016 | asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Argus: The module washbasin sits 0.384 m above the floor; the generated models were pin-refused under the sloped ceiling, so swap to the remaining available model. (fixes a:F317) |
| 27513 | 2 | swap_model | f_L0_009 | no_change: f_L0_009 already uses the model hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 | Argus: The current wardrobe model has a glass central door that reads as a window; a solid modern/scandinavian model of the same footprint (1.48 x 0.61 m) fits the room and the 0.80 m front clearance. (fixes a:F323) |
| 27514 | 2 | swap_model | f_L-1_053 | asset_unusable: 3dwh_e5f77d70d0615bd56772bf1f is not used: audit removed | Argus: The white corner sofa, dark blue sofa and white armchair are three different styles; swapping the corner sofa for a modern/scandinavian model of the same footprint (4.34 x 1.81 m) starts to coordinate the set. (fixes a:F329) |
| 27515 | 2 | set_material | walls | walls: wood_slat (wood) would clad every wall of every room; the walls keep a plain finish (paint), a feature finish goes on one accent wall of a room (its scheme's feature wall: slats, a fluted panel or a headboard panel behind the bed or the sofa) | Argus: The wall behind the dining area and the main living wall are flat untextured concrete/paint; setting the walls slot to wood_slat adds the feature wall the reference calls for. (fixes a:F333) |
| 27516 | 2 | swap_model | f_L-1_027 | acceptance: pin_refused: f_L-1_027: 3dwh_371b2b828aef220519cc3b6a: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The light oak dining table clashes with the dark walnut side table and mid-tone coffee table; swapping for a minimal/modern model of the same footprint (3.20 x 1.20 m) starts to coordinate the palette. (fixes a:F334) |
| 27518 | 2 | set_camera | r_L0_koridor | show: no free camera point of r_L0_koridor shows d_L0_002 (d_L0_002 not in r_L0_koridor: name its pieces, doors or windows) | Argus: The camera is positioned directly in front of the door leaf, which fills the center of the frame and obscures the room's layout. Moving the camera to show the door and the shoe cabinet from a side angle will reveal the hall's layout instead (fixes a:F338) |
| 27520 | 2 | swap_model | f_L0_010 | memory: the same edit was rejected in round 1: lower_quality: f_L0_010: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 is rated 3.0 against 4.0 of the current model abo_B07B3XXD3P: a swap never takes a lower-rated model; choose one rated at least 3.8, or fix the view (camera, light) instead | Argus: The wardrobe's mirrored door reflects a completely different, furnished bedroom that does not exist in this room, making the render unbelievable. Swapping to a non-mirrored wardrobe model (hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7, mode (fixes a:F345) |
| 27523 | 2 | set_material | facade | facade: wood_cladding (wood) would clad every wall of the house; the modern facade scheme keeps the main walls rendered (render off white) over a stone_wall_ledgestone base with wood_cladding at the entrance (the base and the accent are no set_material slot: a texture problem of the base is the build's) | Argus: The facade is a flat, untextured white and grey, lacking the rich timber cladding and material contrast seen in the reference; setting the facade slot to wood_cladding adds the warm wood layer. (fixes a:F355) |
| 27524 | 2 | set_camera | ext_3 | eye height 2.16 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 6.01 m), the ground at (0, -30) is at z -0.56 m: use z 0.94 to 1.14 for an eye-level view | Argus: The view is obstructed by a car in the foreground; the previous attempt was refused because the eye height was 2.16 m (above the 1.5-1.7 m exterior band) and the ground at (0,-30) is at z -0.5, so the camera was effectively at 2.66 m. Setti (fixes a:F356) |
| 27527 | 2 | set_exterior | exterior:ground,site | site front_court yes: a sunken front court with parapet walls is the documents' or the brief's decision, never an edit's (the paved light well and its strip along the glazing stay); leave front_court out or use auto | Argus: The judge scores the terrace view 2/5 because the environment is a flat, untextured lawn; the site stage left the ground and planting as placeholders. (fixes a:F369) |
| 27529 | 2 | set_material | plinth | plinth: stone_wall_ashlar is another stone than the house's base stone_wall_ledgestone: one stone per house (the plinth, the plot walls and the facade's base match; UL204) | Argus: The stone cladding on the lower wall is a flat, repetitive texture that looks like a placeholder; the material stage used a low-quality stone look. (fixes a:F380) |
| 27531 | 2 | retype_piece | f_L-1b_042 | acceptance: finding F2:f_L-1b_042 is still there after the edit (Argus: sofa 0.90 m wide x 2.13 m deep (seen from its front) is turned 90° against the type's product sizes); a retype to the piece's own type only confirms it (status unverified -> verified, the same fitted model): nothing changes in the render, so its vision findings stay | Confirm the drawn sofa's type so the swapped-dimension F2 finding is re-checked against a valid product size for this footprint. |
| 27535 | 2 | swap_model | f_L0_009 | acceptance: pin_refused: f_L0_009: abo_B07GFS1VB6: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric wardrobe (glass pane, 2.99 m height) with a solid-door library wardrobe at a real size (1.78 x 0.63 x 1.96 m), fixing a:F323, c:S6 and c:S4. |
| 27537 | 2 | swap_model | f_L0_043 | off_style: f_L0_043: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the empty dark block nightstand with a styled classic nightstand model to match the reference's styled surfaces (a:D3:f_L0_043). |
| 27541 | 2 | rotate_piece | f_L-1b_053 | acceptance: finding F4:f_L-1b_053 is still there after the edit (armchair does not face its group (f_L-1b_041, f_L-1b_081, f_L-1b_045)); 1 more kept | Face the armchair toward the coffee table and sofa group, fixing the 90° orientation error and the missing-front warning. |
| 27543 | 2 | swap_model | f_L0_009 | acceptance: pin_refused: f_L0_009: abo_B07GFRKNR1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric wardrobe (glass pane, 2.99 m) with a modern-minimal 2-door solid wardrobe at a real size (0.99 x 0.58 x 1.81 m), fixing a:F323, c:S6 and c:S4. |
| 27544 | 2 | move_piece | f_L1_063 | snap: f_L1_063: no free place on wall w_L1_001 (doors, windows) | Snap the tv_unit's back onto the free wall span s0 so it is no longer 1.01 m off a wall (F3). |
| 27545 | 2 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.10 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table 0.15 m away from armchair f_L-1_071 to clear the 0.12 m² overlap. |
| 27548 | 2 | remove_piece | f_L0_045 | score: plausibility 70 -> 67 (G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free)) | AI-added nightstand stands in front of window win_L0_004 (G12); moving it was rejected in round 1 due to bed overlap, so removing it clears the window obstruction. |
| 27549 | 2 | swap_model | f_L0_043 | acceptance: pin_refused: f_L0_043: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the empty dark block nightstand with a styled scandinavian/japandi side-table nightstand matching the project's modern-minimal chain (a:D3:f_L0_043). |
| 27552 | 2 | move_piece | f_L0_010 | f_L0_010: clearance_ok, score: plausibility 70 -> 60 (F3 f_L0_010: wardrobe: its back is not on a wall (0.08 m off); G13 f_L0_010: wardrobe f_L0_010: 0.51 m free in front, needs ≥ 0.80 m) | Move wardrobe 0.14 m off the top wall toward the room center to raise the front clearance from 0.66 m to >=0.80 m (G13) |
| 27553 | 2 | move_piece | f_L1_063 | memory: the same edit was rejected in round 1: f_L1_029: no_overlap; f_L1_032: no_overlap; f_L1_063: inside_room; f_L1_063: no_overlap | Move the tv_unit to the free wall span s0 so its back is on the wall, resolving the off-wall finding. |
| 27554 | 2 | rotate_piece | f_L1_052 | acceptance: finding F4:f_L1_052 is still there after the edit (armchair does not face its group (f_L1_017, f_L1_023)) | Face the reading-corner armchair into the room (90°) so it no longer stands behind the back of sofa f_L1_017 looking at it (F4). |
| 27556 | 2 | move_piece | f_L0_042 | f_L0_019: no_overlap, f_L0_042: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_042: nightstand f_L0_042 overlaps bed_double f_L0_019 by 0.13 m²; G4 f_L0_019: bed_double f_L0_019: no nightstand on the free left side of the head (0.53 m free); G4 f_L0_042: nightstand f_L0_042 of bed_double f_L0_019: -0.08 m from the bed side (needs ≤ 0.30 m)) | Move nightstand up along the bed side to clear the window win_L0_001 band (G12 blocked opening) |
| 27557 | 2 | place_group | r_L0_yatak_odasi_2 | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_020: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping group around the bed so the nightstand blocking window win_L0_004 (G12) is repositioned off the window while keeping a nightstand on the bed's free right side. |
| 27558 | 2 | retype_piece | f_L-1_021 | retype: sideboard is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a sideboard to resolve the untyped finding. |
| 27559 | 2 | swap_model | f_L0_009 | max_tries: f_L0_009 was edited 3 times in this round | Replace the parametric wardrobe (glass pane, 2.99 m) with a modern-minimal 3-door solid wardrobe at a real size (1.29 x 0.51 x 1.91 m) that fits the kept 1.45 x 0.60 footprint, fixing a:F323, c:S6 and c:S4. |
| 27560 | 2 | move_piece | f_L1_063 | f_L1_037: no_overlap, f_L1_038: no_overlap, f_L1_063: inside_room, f_L1_063: no_overlap, score: plausibility 31 -> -6 (F3 f_L1_063: tv_unit: its back is not on a wall (0.45 m off); F4 f_L1_063: tv_unit faces a wall 0.00 m in front of it; F9 f_L1_063: tv_unit f_L1_063 overlaps bench f_L1_037 by 0.18 m²; F9 f_L1_063: tv_unit f_L1_063 overlaps table_coffee f_L1_038 by 0.16 m²) | Move the tv_unit to the free south wall span s4 so its back is on the wall, resolving the off-wall finding. |
| 27562 | 2 | move_piece | f_L1_036 | drawn_lock: f_L1_036: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.74 m) | Move the coffee table into the free zone in front of sofa f_L1_020 (facing 270°) to fix G2 (not in front of sofa) and F6 (blocked front zone). |
| 27563 | 2 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Re-place the AI nightstands so the one blocking window win_L0_004 (G12) moves off the window while the bed keeps a nightstand on its free right side. |
| 27565 | 2 | move_piece | f_L1_063 | max_tries: f_L1_063 was edited 3 times in this round | Move the tv_unit to the free west wall span s6 so its back is on the wall, resolving the off-wall finding. |
| 27566 | 2 | relayout_room | r_L0_yatak_odasi_3 | memory: the same edit was rejected in round 1: acceptance: finding G4:f_L0_021 is still there after the edit (bed_double f_L0_021: no nightstand on the free left side of the head (0.37 m free)); 1 more kept | Re-solve the room layout to fix bed side clearance (G5) and add the missing second nightstand (F500/G4) by repositioning the sleeping group. |
| 27567 | 2 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 48 -> 38 (F6 f_L-1b_084: armchair: the free zone in front of it is blocked by f_L-1b_045, f_L-1b_085; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Turn the reading-corner armchair to face the open floor (away from the back of sofa f_L-1b_045), fixing the 'standing behind the back' orientation error. |
| 27568 | 2 | move_piece | f_L-1_073 | score: plausibility 30 -> 20 (F9 f_L-1_073: table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.06 m²; G11 f_L-1_071: armchair f_L-1_071: its front use zone is not reached by a 0.60 m walkway from door o_L-1_001) | Move coffee table 0.35 m away from armchair f_L-1_071 to fully clear the overlap. |
| 27569 | 2 | retype_piece | f_L-1_021 | retype: kitchen_counter is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a kitchen counter to resolve the untyped finding. |
| 27570 | 2 | relayout_room | r_L0_yatak_odasi_3 | acceptance: finding G4:f_L0_021 is still there after the edit (bed_double f_L0_021: no nightstand on the free left side of the head (0.37 m free)); 1 more kept | Re-solve the room layout with the solver's second candidate to fix bed side clearance (G5) and add the missing second nightstand (F500/G4). |
| 27572 | 2 | move_piece | f_L0_045 | memory: the same edit was rejected in round 1: f_L0_020: no_overlap; f_L0_045: no_overlap; score: plausibility 70 -> 47 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.13 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_02 | Move the AI nightstand up off the window win_L0_004 band (G12) while keeping it beside the bed's free right side. |
| 27573 | 2 | move_piece | f_L1_031 | drawn_lock: f_L1_031: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.89 m) | Bring armchair f_L1_031 closer to coffee table f_L1_023 (2.73 m -> ~2.2 m, needs ≤ 2.5 m) to fix G3. |
| 27574 | 2 | move_piece | f_L-1_073 | acceptance: finding F9:f_L-1_073 is still there after the edit (table_coffee f_L-1_073 overlaps armchair f_L-1_071 by 0.11 m²) | Move coffee table 0.15 m toward the window wall to clear the overlap with armchair f_L-1_071. |
| 27575 | 2 | rotate_piece | f_L1_029 | memory: the same edit was rejected in round 1: f_L1_029: clearance_ok; score: plausibility 21 -> -9 (F4 f_L1_029: armchair faces a wall 0.23 m in front of it; F6 f_L1_029: armchair: the free zone in front of it is reaches out of the room; G3 f_L1_029: armchair f_L1_029 is 160° off the sofa f_L1_018 (needs ≤ 30°) at 2.29 m (needs ≤ 2.50 m); G11 f | Rotate armchair f_L1_029 to face 270 degrees (towards the TV unit on the north wall) so it is no longer behind the back of the TV unit. |
| 27576 | 2 | rotate_piece | f_L-1b_084 | acceptance: finding F4:f_L-1b_084 is still there after the edit (armchair stands behind the back of f_L-1b_045, looking at it) | Turn the reading-corner armchair to face the open floor toward the west wall, away from the back of sofa f_L-1b_045, fixing the 'standing behind the back' orientation error. |
| 27579 | 2 | complete_group | r_L0_yatak_odasi_3.sleeping_double | no_place: r_L0_yatak_odasi_3.sleeping_double (missing nightstand): no place passes the checks (sleeping_double: no place passes the checks) | Add the missing second nightstand on the free left side of the bed head to complete the sleeping set (F500/G4). |
| 27580 | 2 | relayout_room | r_L0_yatak_odasi_2 | no_place: r_L0_yatak_odasi_2 relayout: no place passes the checks (no candidate position fits the room) | Use the solver's best candidate to re-place the AI nightstands so the one blocking window win_L0_004 (G12) moves off the window while the bed keeps a nightstand on its free right side. |
| 27581 | 2 | move_piece | f_L1_007 | acceptance: finding G6:f_L1_007 is still there after the edit (chair f_L1_007: 0.69 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L1_007 away from the table to clear the 0.378 m collision (S2) and gain ≥ 0.81 m clearance behind it (G6). |
| 27582 | 2 | retype_piece | f_L-1_021 | retype: display_cabinet is no candidate for f_L-1_021 (5.54 x 0.60 m at [0.50, 4.27]): the size table and the room / zone give none | Type the untyped 5.54 x 0.60 m drawn piece as a display cabinet to resolve the untyped finding. |
| 27583 | 2 | rotate_piece | f_L-1b_084 | f_L-1b_084: clearance_ok, score: plausibility 48 -> 38 (F4 f_L-1b_084: armchair faces a wall 0.02 m in front of it; F6 f_L-1b_084: armchair: the free zone in front of it is reaches out of the room) | Turn the reading-corner armchair to face south, away from the back of sofa f_L-1b_045, fixing the 'standing behind the back' orientation error. |
| 27584 | 2 | rotate_piece | f_L-1b_084 | max_tries: f_L-1b_084 was edited 3 times in this round | Turn the reading-corner armchair to face northeast, away from the back of sofa f_L-1b_045, fixing the 'standing behind the back' orientation error. |
| 27585 | 2 | move_piece | f_L1_007 | acceptance: finding G6:f_L1_007 is still there after the edit (chair f_L1_007: 0.69 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair f_L1_007 a bit further from the table so the pullout behind it reaches ≥ 0.81 m (G6) while keeping the S2 collision clear. |
| 27587 | 2 | relayout_room | r_L0_yatak_odasi_2 | max_tries: r_L0_yatak_odasi_2 was edited 3 times in this round | Try the solver's second candidate to re-place the AI nightstands so the one blocking window win_L0_004 (G12) moves off the window while the bed keeps a nightstand on its free right side. |
| 27588 | 2 | move_piece | f_L-1_073 | max_tries: f_L-1_073 was edited 3 times in this round | Move coffee table 0.15 m in +X to clear the overlap with armchair f_L-1_071. |
| 27589 | 2 | retype_piece | f_L-1_021 | max_tries: f_L-1_021 was edited 3 times in this round | Type the untyped 5.54 x 0.60 m drawn piece as a tall cabinet to resolve the untyped finding. |
| 27596 | 2 | retype_piece | f_L1_054 | no_change: f_L1_054 is already a bookshelf | Confirm the code-assigned bookshelf type for the slim 0.60x0.25 m unit; console_table was rejected by the size table, so the AI's bookshelf stands. |
| 27600 | 2 | place_group | r_L0_e_yatak_odasi_2 | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group as a unit around the bed anchor to ensure both nightstands are present and the set is complete (a:F499). |
| 27601 | 2 | relayout_room | r_L0_yatak_odasi_4 | memory: the same edit was rejected in round 1: acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m); 1 more kept | Re-solve the room layout to fix the bed side clearances (G5), wardrobe front clearance (G13) and add the missing second nightstand (G4, F501). |
| 27603 | 2 | relayout_room | r_L0_yatak_odasi_4 | memory: the same edit was rejected in round 1: acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m); 1 more kept | Re-solve the room layout with the second solver candidate to fix the bed side clearances (G5), wardrobe front clearance (G13) and add the missing second nightstand (G4, F501). |
| 27607 | 2 | move_piece | f_L1_036 | score: plausibility 51 -> -19 (G11 f_L1_017: sofa f_L1_017: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_020: sofa f_L1_020: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_030: armchair f_L1_030: its front use zone is not reached by a 0.60 m walkway from door d_L1_001; G11 f_L1_031: armchair f_L1_031: its front use zone is not reached by a 0.60 m walkway from door d_L1_001) | Move coffee table f_L1_036 into the free zone in front of sofa f_L1_020 (facing 270°) to fix G2 (not in front of sofa) and F6 (blocked front zone). |
| 27614 | 2 | place_group | r_L0_e_yatak_odasi | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_007: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group around the bed anchor so the set is complete (second nightstand) and correctly positioned. |
| 27615 | 2 | retype_piece | f_L1_035 | retype: bench is no candidate for f_L1_035 (1.40 x 0.45 m at [6.10, 7.22]): the size table and the room / zone give bookshelf, console_table, desk, display_cabinet, sideboard, table_coffee, tv_unit | Confirm the drawn bench f_L1_035 keeps its bench type (it is a real bench along the wall); retype with its own type verifies it so the room-type change is not blocked by F1/G14. |
| 27616 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | The 40.5 m2 room is furnished as a living room (sofa, tv_unit, coffee tables, armchairs, bookshelf, sideboard); typing it 'living' matches its actual program and clears the AI1 room_type findings. |
| 27618 | 2 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric mesh of nightstand f_L0_032 for a real library model to fix the 'built below the library level' finding. |
| 27620 | 2 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_018, f_L0_003, f_L0_025 passes the camera checks: cam_r_L0_banyo_2: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_banyo_2 would show the view cam_r_L0_banyo_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views; cam_r_L0_banyo_2: furniture and fixtures fill 12% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | a:F365: reposition from the corner blank-wall framing to a free pose with headroom showing the main bathroom group (toilet, washbasin, bathtub) |
| 27624 | 2 | set_camera | r_L0_banyo | show: none of the 8 best poses of r_L0_banyo that show f_L0_025, f_L0_018, f_L0_003 passes the camera checks: cam_r_L0_banyo_2: none of the room's main pieces (bathtub, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L0_banyo_2 would show the view cam_r_L0_banyo_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L0_banyo, or remove one of the two views; cam_r_L0_banyo_2: furniture and fixtures fill 12% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | a:F359: move off the tight tub-corner crop to a distinct free pose that frames the bathtub together with the main group (toilet, washbasin) as a designed space |
| 27627 | 2 | swap_model | f_L0_006 | pin_refused: f_L0_006: gen_washbasin_modern_1_833baa60: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes c:S1:f_L0_006 and a:F315 (washbasin floats +0.384 m above floor) and a:F163 (missing mirror/vanity): a proper modern vanity unit model with floor contact and mirror instead of the floating placeholder. |
| 27632 | 2 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric mesh of nightstand f_L0_032 for a real library model (0.40x0.36) that fits the 0.50x0.45 footprint to fix the 'built below the library level' finding. |
| 27637 | 2 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | The 40.5 m2 room is furnished as a living room (sofa, tv_unit, coffee tables, armchairs, bookshelf, sideboard); typing it 'living' matches its actual program and clears the AI1 room_type findings. |
| 27640 | 2 | swap_model | f_L0_003 | pin_refused: f_L0_003: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L0_003 / a:F312 / a:F162: swap the floating vessel basin to a model with correct base geometry so it sits on the counter and reads as a designed basin |
| 27642 | 2 | swap_model | f_L0_015 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Fixes c:S1:f_L0_015 (toilet floats +0.200 m above floor) and c:M26:f_L0_015 (no paper holder): a full WC model with correct floor contact and paper holder. |
| 27646 | 2 | swap_model | f_L0_032 | off_style: f_L0_032: painted_wooden_nightstand is of the styles ['rustic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Swap the parametric mesh of nightstand f_L0_032 for a real library model (0.50x0.51) matching the 0.50x0.45 footprint to fix the 'built below the library level' finding. |
| 27647 | 2 | set_camera | r_L0_koridor | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | a:F367: reframe the hall view to show the shoe cabinet and the main opening instead of a tight low corner shot. |
| 27652 | 2 | swap_model | f_L0_018 | pin_refused: f_L0_018: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | c:S1:f_L0_018: swap the floating toilet to a model with correct base geometry so it sits on the floor |
| 27653 | 2 | swap_model | f_L0_032 | max_tries: f_L0_032 was edited 3 times in this round | Swap the parametric mesh of nightstand f_L0_032 for a modern library model (0.40x0.36) to fix the 'built below the library level' finding. |
| 27658 | 2 | swap_model | f_L0_006 | pin_refused: f_L0_006: gen_washbasin_japandi_3_fc4e0710: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes c:S1:f_L0_006 and a:F315 (washbasin floats +0.384 m above floor) and a:F163 (missing mirror): a vanity unit model with floor contact and mirror; the previous generated model failed the fit caps. |
| 27660 | 2 | swap_model | f_L0_015 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Fixes c:S1:f_L0_015 (toilet floats +0.200 m above floor) and c:M26:f_L0_015 (no paper holder): a full WC model with floor contact and paper holder; the previous asset was audit-removed. |
| 27665 | 2 | swap_model | f_L0_006 | max_tries: f_L0_006 was edited 3 times in this round | Fixes c:S1:f_L0_006 and a:F315 (washbasin floats +0.384 m above floor) and a:F163 (missing mirror): a vanity unit model with floor contact and mirror; previous generated models failed the fit caps. |
| 27666 | 2 | swap_model | f_L0_015 | pin_refused: f_L0_015: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes c:S1:f_L0_015 (toilet floats +0.200 m above floor) and c:M26:f_L0_015 (no paper holder): a full WC model with floor contact and paper holder; previous assets were audit-removed. |
| 27667 | 2 | swap_model | f_L0_004 | pin_refused: f_L0_004: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor; swap to a model whose base sits on the floor. |
| 27670 | 2 | swap_model | f_L0_015 | max_tries: f_L0_015 was edited 3 times in this round | Fixes c:S1:f_L0_015 (toilet floats +0.200 m above floor) and c:M26:f_L0_015 (no paper holder): a full WC model with floor contact and paper holder; previous assets were audit-removed or failed the fit caps. |
| 27672 | 2 | swap_model | f_L0_004 | memory: the same edit was rejected in round 2: asset_unusable: 3dwh_6597c60d5f0b3aa5ee0c0169 is not used: audit removed | Real washbasin product model whose base sits on the floor, replacing the floating model. |
| 27675 | 2 | swap_model | f_L0_016 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Current toilet model floats 0.200 m above the floor; swap to a model whose base sits on the floor. |
| 27676 | 2 | swap_model | f_L0_005 | pin_refused: f_L0_005: gen_washbasin_modern_minimal_1_d5536003: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current washbasin model floats 0.384 m above the floor (S1); swapping to a grounded modern minimal model resolves the clearance error. |
| 27679 | 2 | swap_model | f_L0_017 | pin_refused: f_L0_017: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swapping to a grounded japandi toilet resolves the clearance error. |
| 27682 | 2 | swap_model | f_L0_016 | pin_refused: f_L0_016: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor; swap to a model whose base sits on the floor. |
| 27683 | 2 | swap_model | f_L0_016 | pin_refused: f_L0_016: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor; swap to a model whose base sits on the floor. |
| 27686 | 2 | swap_model | f_L0_005 | asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Current washbasin model floats 0.384 m above the floor (S1); swapping to the grounded real 'Sink' model (0.965x0.5) resolves the clearance error. |
| 27687 | 2 | swap_model | f_L0_016 | max_tries: f_L0_016 was edited 3 times in this round | Current toilet model floats 0.200 m above the floor; swap to a model whose base sits on the floor. |
| 27690 | 2 | swap_model | f_L0_017 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Current toilet model floats 0.200 m above the floor (S1); swapping to the grounded real 'Qualitas toilet' model (0.48x0.68) resolves the clearance error. |
| 27691 | 2 | swap_model | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor; swap to a model whose base sits on the floor. |
| 27695 | 2 | swap_model | f_L0_005 | max_tries: f_L0_005 was edited 3 times in this round | Current washbasin model floats 0.384 m above the floor (S1); swapping to the grounded real 'Hudson Reed Sublime Vanity Unit & Basin' (0.91x0.60) resolves the clearance error. |
| 27696 | 2 | swap_model | f_L0_017 | acceptance: pin_refused: f_L0_017: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Current toilet model floats 0.200 m above the floor (S1); swapping to the grounded real 'Caesar Toilet C1348' (0.46x0.72) resolves the clearance error. |
| 27699 | 2 | swap_model | f_L0_017 | max_tries: f_L0_017 was edited 3 times in this round | Current toilet model floats 0.200 m above the floor (S1); swapping to the grounded real 'toilet' model (0.43x0.72) resolves the clearance error. |
| 28254 | 3 | swap_model | f_L-1_094 | exists: no piece 'f_L-1_094' in a room of the building | Argus: The shoe cabinet is a bare, boxy grid of open cubbies with no doors or styling; the fit stage assigned a placeholder model. (fixes a:F384) |
| 28257 | 3 | place_group | r_L0_koridor_2 | no_change: r_L0_koridor_2 already has its entrance r_L0_koridor_2.entrance (anchor None, members f_L0_055): nothing missing, never a second set | Argus: The twin hall r_L0_koridor_2 has the same under-furnishing as r_L0_koridor; the entrance group is missing. (fixes a:F495) |
| 28258 | 3 | complete_group | r_L0_yatak_odasi.sleeping_double | no_change: r_L0_yatak_odasi.sleeping_double: nothing missing (members: f_L0_041, f_L0_042) | Argus: The bedroom has one nightstand but the sleeping set needs two; complete_group adds the missing partner. (fixes a:F496) |
| 28259 | 3 | swap_model | f_L-1_073 | no_change: f_L-1_073 already uses the model abo_B07GDSF3MR | Argus: The table_coffee was built with a parametric mesh below the library level; swapping to a library model of the same size (0.80 x 0.80 m) resolves it. (fixes a:F510) |
| 28260 | 3 | swap_model | f_L-1_074 | acceptance: pin_refused: f_L-1_074: abo_B07GDSF3MR: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The table_coffee was built with a parametric mesh below the library level; swapping to a library model of the same size (0.80 x 0.80 m) resolves it. (fixes a:F511) |
| 28261 | 3 | swap_model | f_L-1_102 | acceptance: pin_refused: f_L-1_102: abo_B072ZNBRR6: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The tv_unit was built with a parametric mesh below the library level; swapping to a library model of the same size (1.80 x 0.47 m) resolves it. (fixes a:F512) |
| 28262 | 3 | swap_model | f_L-1_103 | asset_unusable: abo_B07LC9HXSF is not used: audit removed | Argus: The finding is a taste flag: the tall_cabinet was built from the parametric mesh although library models of the right size exist; swapping to a real model is the fix of the cause. (fixes a:F513) |
| 28263 | 3 | swap_model | f_L-1_104 | asset_unusable: abo_B07LC9HXSF is not used: audit removed | Argus: Same cause as F513: parametric mesh chosen over an available library model of the right size. (fixes a:F514) |
| 28264 | 3 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: hssd_xxxx562932e4x443cx47f7xaf2dxe60cabe20c9e: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Nightstand built from the parametric mesh although a library model of the same footprint exists. (fixes a:F515) |
| 28265 | 3 | swap_model | f_L0_033 | acceptance: pin_refused: f_L0_033: hssd_xxxx562932e4x443cx47f7xaf2dxe60cabe20c9e: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Same cause: parametric mesh over an available library model. (fixes a:F516) |
| 28266 | 3 | swap_model | f_L0_034 | acceptance: pin_refused: f_L0_034: hssd_xxxx562932e4x443cx47f7xaf2dxe60cabe20c9e: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Same cause: parametric mesh over an available library model. (fixes a:F517) |
| 28267 | 3 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The move attempts were refused (overlap / inside_room), so the only remaining fix is the model itself: a library model of the same 0.40x0.40 footprint replaces the parametric mesh. (fixes a:F518) |
| 28268 | 3 | swap_model | f_L0_044 | acceptance: pin_refused: f_L0_044: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Same cause: parametric mesh over an available library model of the same footprint. (fixes a:F519) |
| 28269 | 3 | swap_model | f_L0_045 | acceptance: pin_refused: f_L0_045: abo_B0861YKM8S: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Removal was refused (the bed needs a nightstand on that side), so the fix is the model, not the piece: a library model of the same footprint replaces the parametric mesh. (fixes a:F520) |
| 28270 | 3 | swap_model | f_L0_047 | acceptance: pin_refused: f_L0_047: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The 0.30x0.30 tall_cabinet matches abo_B07RMJPJMX (0.30x0.27) better than the parametric mesh; swapping fixes the taste flag. (fixes a:F521) |
| 28271 | 3 | swap_model | f_L0_048 | asset_unusable: abo_B07LC9HXSF is not used: audit removed | Argus: Same cause: parametric mesh over an available library model. (fixes a:F522) |
| 28272 | 3 | swap_model | f_L1_009 | room_rule: f_L1_009: hssd_e9393fb84e42e59d93ba261275daf119df0cde2e the drawn table_dining is round and the model is not (its title names no round shape): a square table's corners and legs would stand in the chairs drawn round it (rule round_table) | Argus: The 0.78x0.78 dining table matches hssd_e9393fb84e42e59d93ba261275daf119df0cde2e (0.80x0.80) closely; swapping fixes the taste flag. (fixes a:F524) |
| 28273 | 3 | swap_model | f_L1_066 | exists: no piece 'f_L1_066' in a room of the building | Argus: Same cause: parametric mesh over an available library model. (fixes a:F525) |
| 28274 | 3 | swap_model | f_L1_067 | asset_unusable: abo_B07LC9HXSF is not used: audit removed | Argus: Same cause: parametric mesh over an available library model. (fixes a:F526) |
| 28276 | 3 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: The kitchen run f_L-1_004 is functional but lacks upper cabinets and a hood. The room already has a kitchen_run group; place_group will re-solve the drawn group around its anchor and add the missing members (wall_cabinet, hood) to complete  (fixes a:F536) |
| 28277 | 3 | set_material | kitchen_walls | kitchen_walls: wood_oak_light is a floor finish (its texture set WoodFloor051): a wall or ceiling takes a cladding, panelling or veneer look of that kind | Argus: The concrete-look backsplash on the kitchen counter f_L-1_001 is too harsh for the warm wood aesthetic. Setting the kitchen_walls slot to wood_oak_light will replace the concrete backsplash with a warm wood finish that matches the reference (fixes a:F537) |
| 28278 | 3 | swap_model | f_L-1_060 | acceptance: pin_refused: f_L-1_060: hssd_7ecec7264a07a6c8759f7f23f1b875079b473b89: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The floor lamp f_L-1_060 appears off or not contributing warmth. Swapping to hssd_7ecec7264a07a6c8759f7f23f1b875079b473b89 (0.40 x 0.40 x 1.62 m, minimal/modern) provides a taller, more visible lamp that can be lit to add warm ambient light (fixes a:F538) |
| 28282 | 3 | retype_piece | f_L0_001 | retype: shower is no candidate for f_L0_001 (2.64 x 2.10 m at [6.07, 8.64]): the size table and the room / zone give stair | Argus: The L0 bathroom (r_L0_banyo, 5.0 m2) is furnished with a bathtub, but the L0 plan shows a shower in that wet room, not a tub. The wrong wet fixture was placed. (fixes a:N167) |
| 28291 | 3 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Move the wardrobe along the south wall away from the door swing to open the 0.80 m clearance in front (G13). |
| 28293 | 3 | rotate_piece | f_L-1_072 | f_L-1_072: clearance_ok, score: plausibility 40 -> 20 (F4 f_L-1_072: armchair faces a wall 0.12 m in front of it; F4 f_L-1_102: tv_unit stands behind the back of f_L-1_069, f_L-1_072, looking at it; F6 f_L-1_072: armchair: the free zone in front of it is reaches out of the room; G3 f_L-1_072: armchair f_L-1_072 is 136° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m (needs ≤ 2.50 m)) | Turn armchair f_L-1_072 to face away from the back of sofa f_L-1_054, fixing the F4 orientation finding. |
| 28296 | 3 | swap_model | f_L0_010 | acceptance: pin_refused: f_L0_010: abo_B07GFS1VB6: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric wardrobe (S6) with a real library sliding-door wardrobe (no mirrored door, F345) at a standard 1.96 m height (S4), rated above the current model. |
| 28297 | 3 | rotate_piece | f_L-1_070 | memory: the same edit was rejected in round 1: f_L-1_070: clearance_ok; score: plausibility 30 -> 20 (F4 f_L-1_070: armchair does not face its group (f_L-1_073, f_L-1_053); F6 f_L-1_070: armchair: the free zone in front of it is blocked by f_L-1_089; G3 f_L-1_070: armchair f_L-1_070 is 46° off the table_coffee f_L-1_087 (needs ≤ 30°) at 6.20 m ( | Face the armchair into the room instead of the back of the sofa, resolving F4 and opening its front use zone for the walkway. |
| 28298 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | memory: the same edit was rejected in round 1: acceptance: finding F1:f_L1_035 is still there after the edit (bench is not a piece of a living room) | Documents name it 'Oyun Aktivite Ve Dinlenme Odası' (game/activity/relaxation room) and it is furnished as a living room (sofa, tv_unit, dining, armchairs); 'other' is a program misread. |
| 28299 | 3 | rotate_piece | f_L-1_101 | memory: the same edit was rejected in round 1: f_L-1_101: inside_room; f_L-1_101: inside_room (outline: tv_unit reaches 0.29 m² through the room outline, up to 0.655 m deep; 0.00 m² up to 0.000 m deep before); score: plausibility 30 -> 10 (F3 f_L-1_101: tv_unit: its back is not on a wall (0.20 m off); F9 f_L-1_101: tv_unit reaches 0.29 m² throug | Face the TV unit into the seating area instead of the back of armchair f_L-1_071, resolving the F4 orientation finding. |
| 28302 | 3 | move_piece | f_L0_009 | acceptance: finding G13:f_L0_009 is still there after the edit (wardrobe f_L0_009: 0.62 m free in front, needs ≥ 0.80 m) | Shift the wardrobe further along the south wall (towards the door) so the front clearance reaches 0.80 m (G13). |
| 28303 | 3 | set_room_type | r_L1_oyun_aktivite_ve_dinlenme_odasi | score: plausibility 44 -> -4 (F1 f_L1_017: sofa is not a piece of a dining room; F1 f_L1_020: sofa is not a piece of a dining room; F1 f_L1_023: table_coffee is not a piece of a dining room; F1 f_L1_030: armchair is not a piece of a dining room) | The 40.5 m2 room is furnished with a drawn dining group (table + chairs) plus a relaxation seating area; 'other' is a program misread and dining fits its drawn furniture. |
| 28304 | 3 | rotate_piece | f_L-1_102 | memory: the same edit was rejected in round 1: score: plausibility 30 -> -10 (F3 f_L-1_102: tv_unit: its back is not on a wall (0.47 m off); F4 f_L-1_050: armchair stands behind the back of f_L-1_102, looking at it; F4 f_L-1_054: sofa_corner stands behind the back of f_L-1_102, looking at it; F4 f_L-1_102: tv_unit faces a wall 0.02 m in front of | Turn tv_unit f_L-1_102 to face away from the back of armchair f_L-1_069, fixing the F4 orientation finding. |
| 28305 | 3 | swap_model | f_L0_038 | memory: the same edit was rejected in round 1: asset_unusable: chinese_armchair is not used: audit pending | Replace the black leather corporate office chair (F344) with a warm wood armchair that fits the calm, minimal bedroom palette. |
| 28307 | 3 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B07K7K7GTZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand (F518) with a real library solid-wood nightstand in the modern minimal style chain that passes the fit rules. |
| 28309 | 3 | move_piece | f_L0_045 | memory: the same edit was rejected in round 1: f_L0_020: no_overlap; f_L0_045: no_overlap; score: plausibility 70 -> 60 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.16 m²) | Shift the added nightstand 0.44 m up off the window band (G12) while keeping it beside the bed's right side. |
| 28311 | 3 | swap_model | f_L0_012 | acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.66 m free in front, needs ≥ 0.80 m) | Replace the parametric 2.99 m wardrobe with a real 1.91 m library model to fix S6 (parametric) and S4 (height). |
| 28314 | 3 | move_piece | f_L0_021 | score: plausibility 67 -> 47 (F3 f_L0_021: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_021: bed_double f_L0_021: no nightstand on the free left side of the head (0.38 m free)) | Shift the bed 0.30 m right so the left side gains 0.67 m of clearance (G5 left) while the right side keeps 0.52 m. |
| 28317 | 3 | swap_model | f_L0_044 | acceptance: pin_refused: f_L0_044: side_table_01: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand with a real 0.55 m library model to fix F519 (below library level). |
| 28319 | 3 | rotate_piece | f_L-1b_052 | acceptance: finding F4:f_L-1b_052 is still there after the edit (armchair does not face its group (f_L-1b_042, f_L-1b_071)); 1 more kept | Turn armchair to face the sofa/coffee table cluster, resolving F4 and G3 orientation findings |
| 28320 | 3 | move_piece | f_L-1_023 | score: plausibility 40 -> 30 (F3 f_L-1_023: wardrobe: its back is not on a wall (0.07 m off)) | Move wardrobe f_L-1_023 slightly into the room to clear the 0.020 m room outline collision. |
| 28322 | 3 | rotate_piece | f_L-1b_054 | acceptance: finding G3:f_L-1b_054 is still there after the edit (armchair f_L-1b_054 is 33° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m)) | Armchair is 33° off the sofa (needs ≤ 30°); facing 0° points it directly at the sofa. |
| 28323 | 3 | move_piece | f_L0_021 | acceptance: finding G5:f_L0_021 is still there after the edit (bed_double f_L0_021: 0.08 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.30 m down (foot away from the north wall) so the right side gains 0.82 m of clearance (G5 right) while the left keeps 0.37 m. |
| 28325 | 3 | move_piece | f_L0_045 | f_L0_020: no_overlap, f_L0_045: no_overlap, score: plausibility 70 -> 47 (F9 f_L0_045: nightstand f_L0_045 overlaps bed_double f_L0_020 by 0.11 m²; G4 f_L0_020: bed_double f_L0_020: no nightstand on the free right side of the head (0.53 m free); G4 f_L0_045: nightstand f_L0_045 of bed_double f_L0_020: -0.13 m from the bed side (needs ≤ 0.30 m)) | Shift the added nightstand 0.29 m up off the window band (G12) while keeping it beside the bed's right side. |
| 28327 | 3 | move_piece | f_L-1_074 | score: plausibility 40 -> 30 (F9 f_L-1_074: table_coffee f_L-1_074 overlaps armchair f_L-1_069 by 0.07 m²; G11 f_L-1_069: armchair f_L-1_069: its front use zone is not reached by a 0.60 m walkway from door o_L-1_002) | Move table_coffee f_L-1_074 slightly to resolve the 0.12 m² overlap with armchair f_L-1_069. |
| 28330 | 3 | swap_model | f_L0_012 | memory: the same edit was rejected in round 3: acceptance: finding G13:f_L0_012 is still there after the edit (wardrobe f_L0_012: 0.66 m free in front, needs ≥ 0.80 m) | Replace the parametric 2.99 m wardrobe with a real 1.91 m library model to fix S6 (parametric) and S4 (height). |
| 28331 | 3 | swap_model | f_L0_042 | acceptance: pin_refused: f_L0_042: abo_B079VK52WZ: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the parametric nightstand (F518) with a real library 2-drawer bedside cabinet in the modern minimal style chain that passes the fit rules. |
| 28332 | 3 | swap_model | f_L0_044 | off_style: f_L0_044: ClassicNightstand_01 is of the styles ['classic'], none of the project's chain modern -> modern minimal -> minimal: choose a model of the style | Replace the parametric nightstand with a real 0.70 m library model to fix F519 (below library level). |
| 28333 | 3 | move_piece | f_L0_021 | score: plausibility 67 -> 50 (F3 f_L0_021: bed_double: the headboard stands in the room (0.15 m off); G5 f_L0_021: bed_double f_L0_021: 0.23 m free along the left side, needs ≥ 0.60 m) | Shift the bed 0.15 m right and 0.15 m down so both sides gain clearance (left 0.52 m, right 0.67 m) while the headboard stays on the west wall. |
| 28334 | 3 | rotate_piece | f_L-1b_054 | acceptance: finding G3:f_L-1b_054 is still there after the edit (armchair f_L-1b_054 is 43° off the sofa f_L-1b_041 (needs ≤ 30°) at 1.51 m (needs ≤ 2.50 m)) | Armchair is 33° off the sofa (needs ≤ 30°); 350° points it within tolerance of the sofa. |
| 28337 | 3 | swap_model | f_L0_044 | max_tries: f_L0_044 was edited 3 times in this round | Replace the parametric nightstand with a real 0.47 m modern-minimal library model to fix F519 (below library level). |
| 28338 | 3 | move_piece | f_L-1_074 | drawn_lock: f_L-1_074: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.61 m) | Move table_coffee f_L-1_074 further into the room to clear the overlap with armchair f_L-1_069. |
| 28339 | 3 | swap_model | f_L0_042 | max_tries: f_L0_042 was edited 3 times in this round | Replace the parametric nightstand (F518) with a real library 2-drawer bedside table in the modern minimal style chain that passes the fit rules. |
| 28341 | 3 | swap_model | f_L0_045 | max_tries: f_L0_045 was edited 3 times in this round | Replace the parametric nightstand with a real 0.47 m modern-minimal library model to fix F520 (below library level). |
| 28343 | 3 | move_piece | f_L-1b_051 | score: plausibility 58 -> 48 (G3 f_L-1b_051: armchair f_L-1b_051 is 41° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.69 m (needs ≤ 2.50 m); G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Shift armchair 0.3m to clear the other armchair's front zone and improve alignment with the sofa |
| 28345 | 3 | rotate_piece | f_L-1b_054 | score: plausibility 48 -> 18 (G11 f_L-1b_041: sofa f_L-1b_041: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_054: armchair f_L-1b_054: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_082: bookshelf f_L-1b_082: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002; G11 f_L-1b_084: armchair f_L-1b_084: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_002) | Armchair is 33° off the sofa (needs ≤ 30°); 10° points it within tolerance of the sofa's front. |
| 28346 | 3 | relayout_room | r_L-1_salon_2 | memory: the same edit was rejected in round 1: group checks: F4 f_L-1_106: tv_unit stands behind the back of f_L-1_069, looking at it | Use solver candidate 1 to re-layout the room, aiming to fix the G11 walkway clearance issues for the seating group. |
| 28349 | 3 | complete_group | r_L0_yatak_odasi_4.sleeping_double | no_place: r_L0_yatak_odasi_4.sleeping_double (missing nightstand): no place passes the checks (sleeping_double: no place passes the checks) | Add the missing second nightstand to complete the sleeping set (F501/G4). |
| 28350 | 3 | rotate_piece | f_L-1b_054 | max_tries: f_L-1b_054 was edited 3 times in this round | Armchair is 33° off the sofa (needs ≤ 30°); 30° points it within tolerance of the sofa's front. |
| 28351 | 3 | move_piece | f_L-1b_051 | f_L-1b_051: no_overlap, f_L-1b_052: no_overlap, score: plausibility 58 -> 48 (F9 f_L-1b_052: armchair f_L-1b_052 overlaps armchair f_L-1b_051 by 0.16 m²; G3 f_L-1b_051: armchair f_L-1b_051 is 40° off the sofa f_L-1b_042 (needs ≤ 30°) at 1.27 m (needs ≤ 2.50 m)) | Shift armchair 0.3m toward the sofa to reduce the 33° angle to within 30° and clear the other armchair's front zone |
| 28352 | 3 | rotate_piece | f_L-1_072 | memory: the same edit was rejected in round 1: f_L-1_072: clearance_ok; score: plausibility 30 -> 20 (F4 f_L-1_072: armchair does not face its group (f_L-1_074, f_L-1_054); F6 f_L-1_072: armchair: the free zone in front of it is blocked by f_L-1_095; G3 f_L-1_072: armchair f_L-1_072 is 46° off the table_coffee f_L-1_088 (needs ≤ 30°) at 6.20 m ( | Turn armchair f_L-1_072 to face the coffee table (90°), away from the back of sofa f_L-1_054, fixing the F4 orientation finding. |
| 28355 | 3 | move_piece | f_L0_011 | acceptance: finding G13:f_L0_011 is still there after the edit (wardrobe f_L0_011: 0.15 m free in front, needs ≥ 0.80 m) | Move wardrobe to the free span on wall w_L0_004 to open ≥0.8 m clearance in front (G13). |
| 28357 | 3 | move_piece | f_L-1b_053 | acceptance: finding F6:f_L-1b_054 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_053) | Nudge the armchair to open the blocked free zone in front of it, resolving the mutual clearance conflict with f_L-1b_054. |
| 28358 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair 0.14m away from the table to increase clearance from 0.78m to ≥0.81m |
| 28359 | 3 | place_group | r_L-1_mutfak | no_place: dining group: no place passes the checks (dining: no place passes the checks) | A small bistro set gives the kitchen a lived-in spot and worktop presence, addressing the empty-worktop Q13 finding. |
| 28360 | 3 | place_group | r_L0_e_yatak_odasi_2 | memory: the same edit was rejected in round 2: no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the sleeping_double group around the drawn bed anchor so the second nightstand is placed and the set is complete (a:F499). |
| 28365 | 3 | place_group | r_L-1_mutfak | no_place: dining group: no place passes the checks (dining: no place passes the checks) | A compact square bistro table for two fits the free floor area and gives the kitchen a lived-in spot, addressing the empty-worktop Q13 finding. |
| 28366 | 3 | move_piece | f_L0_022 | score: plausibility 67 -> 47 (F3 f_L0_022: bed_double: the headboard stands in the room (0.30 m off); G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.38 m free)) | Shift bed 0.3 m left to open ≥0.6 m clearance along its left side (G5). |
| 28367 | 3 | move_piece | f_L0_022 | f_L0_022: no_overlap, f_L0_046: no_overlap, score: plausibility 67 -> 57 (F9 f_L0_046: nightstand f_L0_046 overlaps bed_double f_L0_022 by 0.11 m²; G4 f_L0_022: bed_double f_L0_022: no nightstand on the free right side of the head (0.67 m free); G4 f_L0_046: nightstand f_L0_046 of bed_double f_L0_022: -0.12 m from the bed side (needs ≤ 0.30 m); G5 f_L0_022: bed_double f_L0_022: 0.22 m free along the left side, needs ≥ 0.60 m) | Shift bed 0.3 m up to open ≥0.6 m clearance along its right side (G5). |
| 28368 | 3 | place_group | r_L-1_mutfak | max_tries: r_L-1_mutfak was edited 3 times in this round | A slim long bistro table for two along the free wall span s0 gives the kitchen a lived-in spot, addressing the empty-worktop Q13 finding. |
| 28370 | 3 | place_group | r_L0_e_yatak_odasi_2 | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the sleeping_double group around the drawn bed anchor with a different option so the second nightstand is placed and the set is complete (a:F499). |
| 28371 | 3 | move_piece | f_L-1b_053 | acceptance: finding F6:f_L-1b_054 is still there after the edit (armchair: the free zone in front of it is blocked by f_L-1b_053) | Move the armchair further to fully open the free zone in front of f_L-1b_054, resolving the mutual clearance conflict. |
| 28372 | 3 | move_piece | f_L-1b_033 | acceptance: finding G6:f_L-1b_033 is still there after the edit (chair f_L-1b_033: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move chair 0.29m further from table to increase pullout clearance to ≥0.81m |
| 28373 | 3 | move_piece | f_L0_028 | snap: f_L0_028: no free place on wall w_L0_016 (doors, windows, at most 1.2 m from the drawn place) | Snap desk to the right wall to free the bed's right side for ≥0.6 m clearance (G5). |
| 28374 | 3 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_japandi_2_6d594c3b: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes c:S1:f_L-1_026 and a:F311: current washbasin model floats 0.384 m above the floor; this floor-standing japandi basin (0.61x0.51x0.37) sits on the floor and fits the 1.0x0.55 drawn footprint. |
| 28378 | 3 | swap_model | f_L-1_051 | pin_refused: f_L-1_051: gen_toilet_japandi_6_1b5173e9: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes c:S1:f_L-1_051 and a:N188: current toilet floats 0.200 m and its flush plate is the forbidden black frame with two flat white panes; this japandi toilet (0.42x0.69x0.57) has correct base geometry and a slim rounded dual-flush plate. |
| 28381 | 3 | move_piece | f_L0_028 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift desk 0.3 m up to free the bed's right side for ≥0.6 m clearance (G5). |
| 28382 | 3 | place_group | r_L0_e_yatak_odasi_2 | no_place: sleeping_double group re-solved around the drawn bed_double f_L0_008: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the sleeping_double group around the drawn bed anchor with the dresser option so the second nightstand is placed and the set is complete (a:F499). |
| 28383 | 3 | swap_model | f_L-1_103 | acceptance: pin_refused: f_L-1_103: abo_B07GFFY4WT: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Fixes a:F513: tall cabinet was built as a parametric mesh below library level; this library model (0.52x0.25x1.63, Movian Idro Skoskåp) is a real product that fits the 0.4x0.35 footprint. |
| 28385 | 3 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair slightly away from the wall/piece behind to increase clearance from 0.78 m to ≥ 0.81 m. |
| 28386 | 3 | place_group | r_L0_e_yatak_odasi | memory: the same edit was rejected in round 2: no_place: sleeping_double group re-solved around the drawn bed_double f_L0_007: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Re-solve the drawn sleeping_double group around the bed anchor to complete the set with a second nightstand (a:F498). |
| 28387 | 3 | retype_piece | f_L1_027 | retype: wardrobe is no candidate for f_L1_027 (1.52 x 0.60 m at [2.56, 9.90]): the size table and the room / zone give bench, dresser | Confirm the drawn piece as a wardrobe (coat closet) per the vector-geometry reading; keeps its type and verifies it. |
| 28388 | 3 | mark_not_furniture | f_L-1b_002 | no_crop: f_L-1b_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The untyped drawn piece is 5.14 x 2.37 m, far too large for a single furniture item; it is a cluster or architectural element |
| 28389 | 3 | move_piece | f_L0_028 | memory: the same edit was rejected in round 3: acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Shift desk 0.3 m up to free the bed's right side for ≥0.6 m clearance (G5 f_L0_022). |
| 28390 | 3 | swap_model | f_L0_032 | acceptance: pin_refused: f_L0_032: abo_B079VKDKC1: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Swap the parametric mesh of nightstand f_L0_032 for a real modern-minimal library model (47x40x36 cm) to fix a:F515. |
| 28391 | 3 | set_camera | r_L-1_banyo | no view cam_r_L-1_banyo_2 | Fixes a:F362: view is a close-up corner shot pressed against the wall cutting off the washbasin and cabinet; reposition to a free point with headroom showing the whole bathroom. |
| 28393 | 3 | move_piece | f_L0_028 | max_tries: f_L0_028 was edited 3 times in this round | Shift desk 0.26 m up to free the bed's right side for ≥0.6 m clearance (G5 f_L0_022). |
| 28394 | 3 | move_piece | f_L-1b_024 | acceptance: finding G6:f_L-1b_024 is still there after the edit (chair f_L-1b_024: 0.78 m from the table edge to the wall or piece behind, needs ≥ 0.81 m) | Move the chair further from the table edge to increase the pullout clearance from 0.78 m to ≥ 0.81 m. |
| 28397 | 3 | rotate_piece | f_L-1b_051 | f_L-1b_051: no_overlap, f_L-1b_052: no_overlap, score: plausibility 58 -> 48 (G11 f_L-1b_051: armchair f_L-1b_051: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001; G11 f_L-1b_072: bookshelf f_L-1b_072: its front use zone is not reached by a 0.60 m walkway from door o_L-1b_001) | Turn armchair 20° toward the sofa to reduce the 33° angle to within 30° and clear the other armchair's front zone |
| 28406 | 3 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_056, o_L0_001 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Fixes a:F367: re-frame the tight low-angle corner shot to a wider vantage showing the hall's main piece (shoe cabinet) and the main opening for circulation. |
| 28407 | 3 | relayout_room | r_L-1b_salon_2 | group checks: G9 r_L-1b_salon_2_kitchen: kitchen r_L-1b_salon_2_kitchen has no fridge (fridge) | Re-layout the AI pieces to resolve the remaining orientation and clearance findings (G3, G6, F6, F4). |
| 28408 | 3 | retype_piece | f_L1_027 | acceptance: finding RC:f_L1_027 is still there after the edit (f_L1_027: the AI passes typed it bench; a coat closet: hanging rail with hangers (vector geometry outranks the AI passes)) | The vector geometry reads a coat closet (hanging rail); dresser is the valid candidate type that fits a 1.52 x 0.60 m storage piece in a hall, resolving the wrong_type finding. |
| 28409 | 3 | move_piece | f_L-1b_051 | max_tries: f_L-1b_051 was edited 3 times in this round | Shift armchair 0.3m toward the sofa to clear the other armchair's front zone (F6) while keeping the 33° angle |
| 28410 | 3 | set_camera | r_L-1_koridor_2 | the camera stands 0.00 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [4.34, 8.66] | Reframe the hall view from the entrance end down the corridor so the shoe cabinet and the stair opening are both in frame instead of a close-up of a corner and door frame. |
| 28413 | 3 | swap_model | f_L-1_026 | pin_refused: f_L-1_026: gen_washbasin_minimal_1_9dc765fb: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Fixes c:S1:f_L-1_026 and a:F311: current washbasin floats 0.384 m above the floor; this minimal floor-standing basin (0.59x0.52x0.32) sits on the floor. |
| 28414 | 3 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show f_L0_056 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one | Fixes a:F367: re-frame the tight low-angle corner shot to a wider vantage showing the hall's main piece (shoe cabinet) for proper furniture fill. |
| 28415 | 3 | set_camera | r_L-1_koridor_2 | the camera stands 0.00 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [4.34, 8.66] | Keep the only free camera point but aim it down the corridor toward the shoe cabinet so the view shows the hall and its furniture instead of a corner close-up. |
| 28417 | 3 | swap_model | f_L0_006 | memory: the same edit was rejected in round 1: asset_unusable: 3dwh_9314d5619fde2de825a4a2a1 is not used: audit removed | Replace the floating washbasin with a real product model (0.965x0.5m) that has correct floor contact, fixing S1 and providing a proper vanity appearance for Q12. |
| 28418 | 3 | swap_model | f_L0_015 | asset_unusable: objaverse_5b18711616054a44b025d9272b745a6a is not used: audit removed | Replace the floating toilet with a real product model (0.48x0.68m) that has correct floor contact, fixing S1 and providing a proper toilet appearance for M26. |
| 28419 | 3 | set_camera | r_L0_koridor | show: none of the 8 best poses of r_L0_koridor that show d_L0_001, d_L0_005 passes the camera checks: cam_r_L0_koridor_1: none of the room's main pieces (shoe_cabinet) is in its frame, while the room's camera search frames one; cam_r_L0_koridor_1: furniture and fixtures fill 0% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L0_koridor_1: furniture and fixtures fill 1% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Fixes a:F367: re-frame the tight low-angle corner shot to a wider vantage showing the hall's main doors for circulation context. |
| 28420 | 3 | swap_model | f_L-1_051 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Fixes c:S1:f_L-1_051 and a:N188: current toilet floats 0.200 m and has the forbidden flush plate; this japandi toilet (0.41x0.69x0.72) has correct base geometry and a slim rounded dual-flush plate. |
| 28421 | 3 | set_camera | r_L-1_koridor_2 | memory: the same edit was rejected in round 3: the camera stands 0.00 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [4.34, 8.66] | Keep the only free camera point but aim it down the corridor toward the shoe cabinet so the view shows the hall and its furniture instead of a corner close-up. |
| 28422 | 3 | fix_fixture | f_L-1_025 | fixture_place: f_L-1_025: no valid spot within 0.50 m (it stands 0.00 m² outside the room, in door d_L-1_002) | Door d_L-1_002 swings into the washbasin; move it up to 0.5 m to clear the swing. |
| 28424 | 3 | set_camera | r_L-1_koridor_2 | memory: the same edit was rejected in round 3: the camera stands 0.00 m from floor decor (free floor: 0.2 m from pieces, 0.15 m from walls); the nearest free point is [4.34, 8.66] | Keep the only free camera point but aim it down the corridor toward the shoe cabinet so the view shows the hall and its furniture instead of a corner close-up. |
| 28426 | 3 | set_camera | r_L0_koridor | show: no free camera point of r_L0_koridor shows o_L0_001 (o_L0_001 not in r_L0_koridor: name its pieces, doors or windows) | Fixes a:F367: re-frame to show the large opening (o_L0_001) which provides visual depth and circulation context for the hall. |
| 28428 | 3 | swap_model | f_L0_006 | asset_unusable: hssd_6219ef05f4a7b56419749e45a45143df8af44495 is not used: audit removed | Replace the floating washbasin with the Hudson Reed Sublime Vanity Unit & Basin (0.91x0.60m) which includes a vanity unit with mirror, fixing S1 floor contact and Q12 missing mirror. |
| 28429 | 3 | swap_model | f_L0_015 | acceptance: pin_refused: f_L0_015: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the floating toilet with the Caesar Toilet C1348 (0.46x0.72m) which has correct floor contact, fixing S1 and providing a proper toilet with paper holder for M26. |
| 28434 | 3 | remove_camera | cam_r_L0_koridor_1 | role: cam_r_L0_koridor_1 is the only view of r_L0_koridor (every room with something to show keeps a view: the camera policy and the render test): it is not removed; set_camera moves it to a free point of the room | Fixes a:F367: the camera cannot be re-framed to show the hall's main piece with adequate furniture fill (12%) from any free point in this narrow corridor; removing the low-value tight corner shot. |
| 28440 | 3 | set_camera | r_L0_koridor | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Fixes a:F367: move to a higher, wider vantage looking down the corridor to capture the hall's circulation and the shoe cabinet area. |
| 28441 | 3 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_japandi_3_fc4e0710: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap to a floor-standing japandi washbasin to fix the S1 floating finding (lowest point +0.384 m above floor). |
| 28442 | 3 | swap_model | f_L0_006 | asset_unusable: 3dwh_2a2928a83cea9dbe8fbc006f is not used: audit removed | Replace the floating washbasin with the Modern Single Lav Vanity (0.96x0.43m) which has correct floor contact, fixing S1 and providing a proper vanity appearance for Q12. |
| 28445 | 3 | swap_model | f_L0_015 | acceptance: pin_refused: f_L0_015: hssd_f983ff568379c97ee9dfa7095b02a7688fbf60a4: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Replace the floating toilet with the Close Coupled Toilet (0.41x0.68m) which has correct floor contact, fixing S1 and providing a proper toilet with paper holder for M26. |
| 28446 | 3 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_mediterranean_4_c5dc64de: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap to a low, compact mediterranean washbasin (0.56 m high) that should seat on the floor and fit under the sloped ceiling. |
| 28453 | 3 | swap_model | f_L0_006 | max_tries: f_L0_006 was edited 3 times in this round | Replace the floating washbasin with the Vanity Vessel (0.88x0.575m) which has correct floor contact, fixing S1 and providing a proper vanity appearance for Q12. |
| 28454 | 3 | swap_model | f_L0_015 | max_tries: f_L0_015 was edited 3 times in this round | Replace the floating toilet with the Toilet model (0.45x0.63m) which has correct floor contact, fixing S1 and providing a proper toilet with paper holder for M26. |
| 28456 | 3 | swap_model | f_L1_021 | asset_unusable: gen_toilet_japandi_1_42fdb46f is not used: audit removed | Swap to a floor-standing japandi toilet to fix the S1 floating finding (lowest point +0.200 m above floor). |
| 28459 | 3 | swap_model | f_L1_021 | pin_refused: f_L1_021: gen_toilet_japandi_3_4e49add0: fails the fit rules (caps, height, at most 1.52 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap to a floor-standing japandi toilet (0.72 m high) to fix the S1 floating finding. |
| 28463 | 3 | swap_model | f_L1_021 | asset_unusable: gen_toilet_minimal_1_3799392b is not used: audit removed | Swap to a minimal toilet model to fix the S1 floating finding (lowest point +0.200 m above floor). |
| 28466 | 3 | swap_model | f_L1_015 | pin_refused: f_L1_015: gen_washbasin_modern_minimal_1_d5536003: fails the fit rules (caps, height, at most 1.60 m high under the sloped ceiling): the real model stays; swap to a real model of the type or use another tool | Swap to a modern minimal washbasin (0.64 m high) to fix the S1 floating finding. |
| 29365 | 4 | swap_model | f_L0_019 | acceptance: finding G5:f_L0_019 is still there after the edit (bed_double f_L0_019: 0.56 m free along the right side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves 0.53 m on the left; a 1.63 m model is wider, so the room's geometry is the constraint and the bed must be re-fitted to a model that fits the side clearance. (fixes a:F51) |
| 29366 | 4 | swap_model | f_L0_020 | acceptance: finding G5:f_L0_020 is still there after the edit (bed_double f_L0_020: 0.56 m free along the left side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves 0.53 m on the right; a 1.45 m model restores the 0.60 m side walkway. (fixes a:F52) |
| 29367 | 4 | swap_model | f_L0_012 | asset_unusable: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e is not used: audit removed | Argus: The 0.60 m-deep wardrobe leaves 0.66 m in front; a 0.55 m-deep model restores the 0.80 m door swing. (fixes a:F53) |
| 29368 | 4 | swap_model | f_L0_013 | acceptance: pin_refused: f_L0_013: hssd_72807de315ae7f20a846e137cf5e755f909a398f: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The 1.40 x 0.60 m shower is not a real product; a 1.20 x 0.80 m model is a valid shower that fits the 4.0 m2 bathroom. (fixes a:F54) |
| 29369 | 4 | swap_model | f_L0_014 | acceptance: pin_refused: f_L0_014: hssd_72807de315ae7f20a846e137cf5e755f909a398f: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Same misread shower in the twin bathroom; a 1.20 x 0.80 m model is a valid product. (fixes a:F55) |
| 29370 | 4 | swap_model | f_L0_021 | acceptance: finding G5:f_L0_021 is still there after the edit (bed_double f_L0_021: 0.52 m free along the right side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves 0.37 m on the left; the room is 14.1 m2 and cannot give 0.60 m, so the bed must be re-fitted. (fixes a:F56) |
| 29371 | 4 | swap_model | f_L0_009 | asset_unusable: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e is not used: audit removed | Argus: The 0.60 m-deep wardrobe leaves 0.17 m in front; a 0.55 m-deep model restores the door swing. (fixes a:F57) |
| 29372 | 4 | swap_model | f_L0_022 | acceptance: finding G5:f_L0_022 is still there after the edit (bed_double f_L0_022: 0.52 m free along the left side, needs ≥ 0.60 m) | Argus: The 1.55 m bed leaves 0.37 m on the right; a 1.45 m model restores the 0.60 m side walkway. (fixes a:F58) |
| 29373 | 4 | swap_model | f_L0_011 | memory: the same edit was rejected in round 1: asset_unusable: hssd_b15e1d3e55fa2b36c327471ac84c3b42b562aa1e is not used: audit removed | Argus: The 0.60 m-deep wardrobe leaves 0.17 m in front; a 0.55 m-deep model restores the door swing. (fixes a:F59) |
| 29375 | 4 | relayout_room | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | memory: the same edit was rejected in round 1: group checks: F3 f_L1_084: tv_unit: its back is not on a wall (1.01 m off); F4 f_L1_029: armchair stands behind the back of f_L1_084, looking at it; F4 f_L1_032: armchair stands behind the back of f_L1_084, looking at it | Argus: The tv_unit is 1.01 m off the wall and no free span on w_L1_001 exists; the L1 media group needs a fresh solve. (fixes a:F64) |
| 29376 | 4 | fix_fixture | f_L-1_008 | no_change: f_L-1_008: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The stove stands 0.06 m off its wall with its back parallel to it; the code fix is to snap its back onto the wall. fix_fixture without a centre moves it to the nearest valid spot. (fixes a:F119) |
| 29377 | 4 | fix_fixture | f_L-1_017 | no_change: f_L-1_017: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The stove stands 0.06 m off its wall with its back parallel to it; the code fix is to snap its back onto the wall. fix_fixture without a centre moves it to the nearest valid spot. (fixes a:F120) |
| 29378 | 4 | fix_fixture | f_L0_014 | no_change: f_L0_014: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The shower stands 0.10 m off its wall with its back parallel to it; the code fix is to snap its back onto the wall. fix_fixture without a centre moves it to the nearest valid spot. (fixes a:F121) |
| 29379 | 4 | fix_fixture | f_L0_013 | fixture_size: f_L0_013: the drawn 1.40 x 0.60 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The 1.40 m shower in a 4.0 m2 bathroom leaves 0.05 m in front; a 1.20 x 0.80 m shower fits and restores the 0.53 m clearance. (fixes a:F130) |
| 29380 | 4 | fix_fixture | f_L0_018 | fixture_size: f_L0_018: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m wide toilet sits 0.33 m from the side wall; a 0.44 m wide model restores the 0.38 m clearance. (fixes a:F131) |
| 29381 | 4 | fix_fixture | f_L0_025 | fixture_size: f_L0_025: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The 1.83 m tub leaves 0.28 m in front; a 1.50 x 0.70 m tub fits the bay and restores the 0.53 m clearance. (fixes a:F132) |
| 29382 | 4 | fix_fixture | f_L0_017 | fixture_size: f_L0_017: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m wide toilet sits 0.33 m from the side wall; a 0.44 m wide model restores the 0.38 m clearance. (fixes a:F133) |
| 29383 | 4 | fix_fixture | f_L0_026 | fixture_size: f_L0_026: the drawn 1.83 x 0.80 m is within 30 % of the real bathtub range (width 1.40-1.90 m, depth 0.65-0.90 m): its size stays as drawn | Argus: The 1.83 m tub leaves 0.28 m in front; a 1.50 x 0.70 m tub fits the bay and restores the 0.53 m clearance. (fixes a:F134) |
| 29384 | 4 | fix_fixture | f_L1_021 | fixture_size: f_L1_021: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m wide toilet sits 0.33 m from the side wall; a 0.44 m wide model restores the 0.38 m clearance. (fixes a:F135) |
| 29385 | 4 | fix_fixture | f_L1_025 | fixture_size: f_L1_025: the drawn 1.83 x 0.80 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The 1.83 m shower leaves 0.28 m in front; a 1.20 x 0.80 m shower fits the bay and restores the 0.53 m clearance. (fixes a:F136) |
| 29386 | 4 | fix_fixture | f_L1_022 | fixture_size: f_L1_022: the drawn 0.50 x 0.69 m is within 30 % of the real toilet range (width 0.35-0.50 m, depth 0.55-0.80 m): its size stays as drawn | Argus: The 0.50 m wide toilet sits 0.33 m from the side wall; a 0.44 m wide model restores the 0.38 m clearance. (fixes a:F137) |
| 29387 | 4 | fix_fixture | f_L1_026 | fixture_size: f_L1_026: the drawn 1.83 x 0.80 m is within 30 % of the real shower range (width 0.70-1.60 m, depth 0.70-1.20 m): its size stays as drawn | Argus: The 1.83 m shower leaves 0.28 m in front; a 1.20 x 0.80 m shower fits the bay and restores the 0.53 m clearance. (fixes a:F138) |
| 29392 | 4 | place_group | r_L-1_mutfak | memory: the same edit was rejected in round 1: no_change: r_L-1_mutfak already has its kitchen_run r_L-1_mutfak.kitchen_run (anchor f_L-1_001, members f_L-1_002, f_L-1_003, f_L-1_004, f_L-1_008, f_L-1_067, f_L-1_090): nothing missing, never a second set | Argus: r_L-1_mutfak has a kitchen run without a fridge; re-solving the run around its drawn anchor adds the missing fridge. (fixes a:F143) |
| 29393 | 4 | place_group | r_L-1_mutfak_2 | no_change: r_L-1_mutfak_2 already has its kitchen_run r_L-1_mutfak_2.kitchen_run (anchor f_L-1_010, members f_L-1_011, f_L-1_012, f_L-1_013, f_L-1_017, f_L-1_068, f_L-1_096): nothing missing, never a second set | Argus: r_L-1_mutfak_2 has a kitchen run without a fridge; re-solving the run around its drawn anchor adds the missing fridge. (fixes a:F144) |

Rolled back (the refit refused them): #825 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #827 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0), #828 move_piece (locked check: f_L1_031: moved 0.300 m by the agent (> 0.3 m)), #865 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #870 move_piece (locked check: f_L1_031: moved 0.300 m by the agent (> 0.3 m)), #897 rotate_piece (locked check: f_L-1b_053: drawn_front_deg None != the drawn front 180.0), #901 rotate_piece (locked check: f_L-1b_052: drawn_front_deg None != the drawn front 0.0).

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F9 | major | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| F9 | major | f_L-1_024 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| G8 | minor | f_L-1b_055 | r_L-1b_salon_2 | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| G8 | minor | f_L-1b_056 | r_L-1b_salon | - | soft_minimum | 1, 2, 3, 4 | a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work triangle) is a scored term of the solver, reported only; no tool is offered |
| M13 | minor | f_L-1_099 | r_L-1_mutfak_2 | fit | kitchen_design | 1, 2, 3, 4 | the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit composes them of real units on the base joints (modules.plan_wall_run); the build cuts them at the windows of the building as built. No agent tool builds a hood or splits a wall cabinet, so the finding is reported to the fit |
| M15 | minor | spk_001 | - | site | site_grading | 1, 2, 3, 4 | the garden on the slope is graded by code (wenart/blender/grading.py: terraces at one level per side and planted, banks of at most 1:3 / 1:2, flights of solid treads with cheek walls and a landing, paths level across and stepped, walls in the house's base stone with a coping, the floors by use); no agent tool changes the terrain, so the finding is reported to the site stage |
| M17 | major | dec_L0_041 | r_L0_yatak_odasi_3 | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | major | dec_L0_078 | r_L0_yatak_odasi_4 | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon | r_L-1_salon | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M17 | minor | r_L-1_salon_2 | r_L-1_salon_2 | decor | ceiling_light | 1, 2, 3, 4 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M21 | minor | f_L1_019 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | f_L1_020 | r_L1_oyun_aktivite_ve_dinlenme_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_banyo_2 | r_L0_e_banyo_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi | r_L0_e_yatak_odasi | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi_2 | layout | room_use | 1, 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo | r_L1_banyo | layout | room_use | 2, 3, 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_banyo_2 | r_L1_banyo_2 | layout | room_use | 4 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M31 | major | d_L1_004 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| M31 | major | d_L1_005 | - | - | opening_under_roof | 1, 2, 3, 4 | a door or window under the sloped roof is clipped below a usable height: it needs a dormer (a design change, review); the roof comes from the drawings and set_exterior cannot fix it, so it is reported only |
| Q1 | major | d_L1_003 | r_L1_teras | architect | opening_sense | 4 | a door off its floor or into the air is the architect's (E1, O2, D4: its defaults turn such a door into a window or set its threshold); reported to the architect for the next build |
| Q1 | major | d_L1_004 | r_L1_banyo | architect | opening_sense | 4 | a door off its floor or into the air is the architect's (E1, O2, D4: its defaults turn such a door into a window or set its threshold); reported to the architect for the next build |
| Q3 | critical | r_L-1_koridor | r_L-1_koridor | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q3 | critical | r_L-1_koridor_2 | r_L-1_koridor_2 | architect | guard | 4 | a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's guard); reported to the architect |
| Q7 | major | d_L0_005 | - | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| S2 | minor | f_L-1_023 | r_L-1_salon_2 | - | within_tolerance | 1 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_027 | r_L-1_salon | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L-1_038 | r_L-1_salon_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_037 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S2 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | within_tolerance | 1, 2, 3, 4 | within tolerance: a cut below 0.03 m is not visible (S2 class tolerance); no tool is offered |
| S5 | minor | f_L-1_089 | r_L-1_salon | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_094 | r_L-1_koridor_2 | decor | decor_rest | 1 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_100 | r_L-1_koridor | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L-1_106 | r_L-1_koridor_2 | decor | decor_rest | 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_008 | r_L0_e_yatak_odasi_2 | decor | decor_rest | 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_052 | r_L0_koridor | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_053 | r_L0_koridor_2 | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_054 | r_L0_koridor | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_055 | r_L0_koridor_2 | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_056 | r_L0_koridor | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_057 | r_L0_koridor_2 | decor | decor_rest | 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_036 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_038 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_050 | r_L1_oyun_aktivite_ve_dinlenme_odasi | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_061 | r_L1_koridor_2 | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | major | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | - | facade | 2, 3, 4 | the facade openings come from the drawings; no agent tool |
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
| X5 | minor | win_L1_002 | - | - | scale | 2, 3, 4 | storey and door sizes come from the drawings |
| lighting_dark | minor | cam_r_L0_banyo_1 | r_L0_banyo | - | lighting_within_step | 2, 3 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | minor | cam_r_L0_banyo_2 | r_L0_banyo | - | lighting_within_step | 1 | the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds the exposure to that step, so a set_lighting re-render changes nothing visible; reported only |
| lighting_dark | major | cam_r_L0_e_banyo_2 | r_L0_e_banyo | - | lighting_beyond_cap | 1, 2 | the view needs more light than set_lighting's maximum (the room's lights x3): no factor clears it and there is no add-lamp tool, so it is reported only |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L-1b_salon_2 | cut | 2 | 12984 | 32768 |
| 1 | r_L-1b_salon | cut | 2 | 15024 | 32768 |
| 1 | r_L0_e_yatak_odasi | cut | 1 | 29392 | 32768 |
| 1 | r_L0_banyo | cut | 1 | 24277 | 32768 |
| 2 | r_L-1b_salon_2 | cut | 3 | 16931 | 32768 |
| 2 | building | cut | 13 | 50011 | 32768 |
| 2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | cut | 1 | 14219 | 32768 |
| 3 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | cut | 2 | 28670 | 32768 |
| 3 | building | cut | 5 | 56120 | 32768 |
| 3 | r_L-1b_salon | cut | 2 | 13839 | 32768 |
| 3 | r_L-1b_salon_2 | cut | 2 | 15977 | 32768 |

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
| f_L-1_023 | piece | wardrobe | r_L-1_salon_2 | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | Qwen/Qwen3.8-27B-FP8 | Move wardrobe f_L-1_023 slightly inward (0.02m in -y) to clear the room outline collision. |
| f_L-1_024 | piece | wardrobe | r_L-1_salon | adjusted_by_ai | size 2.57 x 0.74 m -> 2.57 x 0.60 m | code (size_snap) | size snap: the drawn wardrobe 2.57 x 0.74 m is outside its product range (depth 0.74 m is 6 % outside 0.5-0.7 m; a run keeps its length and takes the product depth); nearest real product 2.57 m long x 0.60 m deep (2-door 120 x 60) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L-1_031 | piece | chair | r_L-1_salon | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Nudge chair f_L-1_031 slightly to resolve the 0.040 m cut with the dining table. |
| f_L-1_039 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1_039 slightly to resolve the 0.034 m cut with table_dining f_L-1_038. |
| f_L-1_042 | piece | chair | r_L-1_salon_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move chair f_L-1_042 slightly along the table row to resolve the 0.034 m cut with table_dining f_L-1_038. |
| f_L-1_049 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The armchair's brown mid-century model clashes with the white modern sectional and the room's scandinavian set; swapping to a minimal/modern/scandinavian armchair of the same footprint unifies the set. (fixes a:F385) |
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
| f_L-1_070 | piece | armchair | r_L-1_salon | inferred, adjusted_by_ai | size 0.64 x 0.57 m -> 0.65 x 0.80 m | Qwen/Qwen3.8-27B-FP8 | Argus: The brown leather armchair f_L-1_070 clashes with the white boxy sofa and the black lounge chair; the three seating pieces are of different styles and colors. Swapping to a modern model of the same footprint (0.65 x 0.78 m) restores a coher (fixes a:F364) |
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
| f_L0_010 | piece | wardrobe | r_L0_yatak_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the parametric wardrobe (S6) with a real library wardrobe (no mirrored door, F345) at a standard 2.11 m height (S4) that fits the 1.45 x 0.60 m footprint. |
| f_L0_011 | piece | wardrobe | r_L0_yatak_odasi_4 | adjusted_by_ai | - | architect | wardrobe f_L0_011: 0.17 m free in front of its doors or drawers (f_L0_028 in the way; they need 0.50 m to open): it slid 0.40 m along its wall, so they open (1.99 m free; the safest move that passes the code checks: inside the room, no collision, the door swings free, no more of a window covered, every other front still opens) |
| f_L0_013 | piece | shower | r_L0_e_banyo | inferred, adjusted_by_ai | - | code (back_gap) | shower f_L0_013: its back stood 0.10 m off its wall, parallel to it (a drawing gap): moved 0.08 m back onto the wall (plan crop recognition/reading/f_L0_013_ctx.png) |
| f_L0_014 | piece | shower | r_L0_e_banyo_2 | inferred, adjusted_by_ai | - | code (bath_details.shower_entry) | f_L0_014: its front stood on a wall, its left side open: the way in turned to that side (0 deg; UL201) |
| f_L0_019 | piece | bed_double | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_001 (the answer to AI.move_piece:f_L0_019) |
| f_L0_020 | piece | bed_double | r_L0_yatak_odasi_2 | inferred, adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of win_L0_004 (the answer to AI.move_piece:f_L0_020) |
| f_L0_021 | piece | bed_double | r_L0_yatak_odasi_3 | inferred | - | - | bed_double: the same drawn block (the same strokes (22 INSERT here, within 2%)) and footprint (1.90 x 1.55 m, within 0.01 m) as f_L0_019, f_L0_020 (typed bed_double): one block, one type; front: its back stands on the only side on a wall |
| f_L0_022 | piece | bed_double | r_L0_yatak_odasi_4 | inferred | - | - | bed_double: the same footprint (1.90 x 1.55 m) as f_L0_021 in the twin room r_L0_yatak_odasi_3 (mirrored centre within 0.02 m); front: its back stands on the only side on a wall |
| f_L0_023 | piece | wardrobe | r_L0_e_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Resize wardrobe f_L0_023 to bring its height from 2.99 m down into the valid 1.50-2.45 m range. |
| f_L0_024 | piece | wardrobe | r_L0_e_yatak_odasi_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Bring the wardrobe height back into the real 1.50-2.45 m range to fix the S4 size finding. |
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
| f_L1_006 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi | adjusted_by_ai | - | code (architect F5) | architect F5: f_L1_006 (chair) cut f_L1_005 (table_dining) by 0.32 m; f_L1_006 (chair) moved 0.05 m clear of it (inside its room, clear of the other pieces and the doorways) |
| f_L1_008 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_010 | piece | chair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move chair f_L1_010 away from table_dining f_L1_009 to resolve the 0.326 m collision (S2). |
| f_L1_012 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | rug outline drawn around a table and its chairs: a rug mark, not a piece: 1.52 x 1.63 m, 78% of its box, the table and chairs inside it (fix round after P6a) (the decor stage places decor) |
| f_L1_013 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_014 | piece | unknown | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_019 | piece | sofa | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Move sofa f_L1_019 slightly north to clear the front zone blocked by sofa f_L1_018 (F6). |
| f_L1_023 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi.seating (anchor f_L1_017) misses table_coffee; r_L1_oyun_aktivite_ve_dinlenme_odasi.seating.2 (anchor f_L1_020) misses table_coffee, and the type's product range fits 1.03 x 0.69 m (the only missing member of that size) |
| f_L1_024 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: the same footprint (1.03 x 0.69 m) as f_L1_023 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi (mirrored centre within 0.02 m) |
| f_L1_025 | piece | shower | r_L1_banyo | inferred, adjusted_by_ai | type bathtub -> shower | code (infer.bath_or_shower) | f_L1_025: a bath-sized footprint (1.83 x 0.80 m) the drawing does not name a bath, in a bathroom off the bedrooms' level (L1; the main bathroom keeps its bath on L0): a walk-in shower (UL200) |
| f_L1_026 | piece | shower | r_L1_banyo_2 | inferred, adjusted_by_ai | type bathtub -> shower | code (infer.bath_or_shower) | f_L1_026: a bath-sized footprint (1.83 x 0.80 m) the drawing does not name a bath, in a bathroom off the bedrooms' level (L1; the main bathroom keeps its bath on L0): a walk-in shower (UL200) |
| f_L1_027 | piece | wardrobe | r_L1_koridor | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_028 | piece | wardrobe | r_L1_koridor_2 | inferred | - | - | front: standing in a corner: its long side on the wall is the back |
| f_L1_029 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the room misses it (the living room's reading_corner group has no armchair); plan crop recognition/crops/sym_L1_007_ctx.png |
| f_L1_030 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The woven armchair f_L1_030 and its pair f_L1_031 clash with the modern white sofa f_L1_017 and brown leather chair f_L1_052; swapping to a minimal/modern/scandinavian model of the same footprint (0.69 x 0.78 m) restores a coherent set. (fixes a:F353) (plan crop recognition/crops/sym_L1_008_ctx.png) |
| f_L1_031 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because its real product size is the nearer one to the drawn size; plan crop recognition/crops/sym_L1_009_ctx.png |
| f_L1_032 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | the two AI passes disagree (floor_lamp / armchair); both fit the drawn 0.68 x 0.78 m and the room: armchair, because the AI passes of its twin f_L1_031 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi named it too: the twins get one type; plan crop recognition/crops/sym_L1_010_ctx.png |
| f_L1_033 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_034 | piece | ottoman | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | drawn on the 'A-BA' layer(s): structure, not furniture (kept as an obstacle, not built) |
| f_L1_035 | piece | console_table | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred, adjusted_by_ai | type bench -> console_table; size 0.40 x 2.17 m -> 1.40 x 0.45 m | Qwen/Qwen3.8-27B-FP8 | The 1.40 x 0.45 m wall piece f_L1_035 is read as a bench but a bench is not a piece of this room; retype it to a console_table that fits its size and the room, clearing F1/G14. (plan crop recognition/crops/sym_L1_x975ffc83_ctx.png) |
| f_L1_036 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi | inferred | - | - | table_coffee: the same footprint (1.09 x 0.40 m) as f_L1_038 in the twin room r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (mirrored centre within 0.02 m) |
| f_L1_037 | piece | bench | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred, adjusted_by_ai | size 0.40 x 2.17 m -> 1.40 x 0.45 m | code (size_snap) | a bench faces along a long side: the front 0 deg on its short side (an AI front) is a reading error; front 270 deg: its back stands on the only side on a wall; plan crop recognition/crops/sym_L1_x59e6f5f5_ctx.png; size snap: the drawn bench 2.17 x 0.40 m is outside its product range (width 2.17 m is 8 % outside 0.8-2 m; nearest real product 1.40 x 0.45 m); nearest real product 1.40 x 0.45 x 0.46 m (product) (CLAUDE.md: a drawn size outside its type's product range is snapped to the nearest real product before the fit; user OK D5 of 12 Oct 2026) |
| f_L1_038 | piece | table_coffee | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | inferred | - | - | table_coffee: r_L1_oyun_aktivite_ve_dinlenme_odasi_2 misses it (r_L1_oyun_aktivite_ve_dinlenme_odasi_2.seating.2 (anchor f_L1_019) misses table_coffee) and the AI passes named it (pass 2 (glm)'s reason names table_coffee); plan crop recognition/crops/sym_L1_xf35ed8f5_ctx.png |
| f_L0_035 | piece | office_chair | r_L0_yatak_odasi_2 | inferred | - | - | the chair of the desk f_L0_027, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_009_ctx.png) |
| f_L0_036 | piece | office_chair | r_L0_yatak_odasi_4 | inferred | - | - | the chair of the desk f_L0_028, drawn in front of it in the desk symbol (plan crop recognition/crops/sym_L0_010_ctx.png) |
| f_L0_037 | piece | office_chair | r_L0_yatak_odasi_3 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black mesh office chair is a corporate piece that clashes with the warm, residential bedroom style. Swapping to a minimal/modern chair (3dwh_54a792101c925f12bff90916) that fits the residential style will resolve the mismatch. (fixes a:F346) (plan crop recognition/crops/sym_L0_011_ctx.png) |
| f_L0_038 | piece | office_chair | r_L0_yatak_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the black leather corporate office chair (F344) with a fabric ergonomic chair that fits the calm, minimal bedroom palette. (plan crop recognition/crops/sym_L0_012_ctx.png) |
| f_L0_043 | piece | nightstand | r_L0_yatak_odasi_3 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Replace the empty dark block nightstand with a modern-minimal 2-drawer bedside cabinet (0.40 x 0.36 x 0.47 m) matching the project's modern-minimal chain and the kept 0.40 x 0.40 footprint (a:D3:f_L0_043). |
| f_L1_059 | piece | armchair | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The armchair's back/arm stands 2.4 cm from its seat; rotate_piece was already tried and refused (it only re-angled the piece, leaving the F4 behind-the-back finding), so the gap is a model defect that a swap to an integral-rest model fixes. (fixes a:F20) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L-1_banyo_1 | ![](agent/r1_cam_r_L-1_banyo_1_before.jpg) | ![](agent/r1_cam_r_L-1_banyo_1_after.jpg) |
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
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |
| 4 | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |
| 4 | cam_r_L1_teras_1 | ![](agent/r4_cam_r_L1_teras_1_before.jpg) | ![](agent/r4_cam_r_L1_teras_1_after.jpg) |
| 4 | cam_r_L1_teras_2 | ![](agent/r4_cam_r_L1_teras_2_before.jpg) | ![](agent/r4_cam_r_L1_teras_2_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- cam_r_L-1_banyo_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L-1_koridor_2_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L0_banyo_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L1_koridor_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- final/cam_r_L-1_banyo_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L-1_banyo_2_final_preview_2.jpg
- final/cam_r_L0_banyo_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_banyo_2_final_preview.jpg
- final/cam_r_L-1_banyo_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L-1_banyo_2_plan_2.jpg
- final/cam_r_L0_banyo_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_banyo_2_plan.jpg
- final/top_L-1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L-1_plan_5.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_5.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_5.jpg
