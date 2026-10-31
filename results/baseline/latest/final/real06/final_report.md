# Final report: real06

29 views: 0 polished, 29 Cycles (error 10, gate 2, gate_validation 6, not_run 1, room 10). Stages: render run, gate validation ok, polish run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 29 |
| interior / exterior views | 23 / 6 |
| variant | base |
| polished | 0 |
| Cycles | 29 (error 10, gate 2, gate_validation 6, not_run 1, room 10) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 12 |
| needs_review views | 9 |
| unverified pieces in view (sum over views) | 82 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 11 |
| exposure | -7.17 .. +1.50 EV (0 at a limit), modes auto |
| views too dark for the EV cap (lighting_dark) | 0 (0 critical, 0 major) |
| blocked views | 0 |
| window pull | 24 view(s), -3 .. 0 EV |
| interior glazing pull | 1 view(s) with interior glazing, 0 pulled, 0 still clipped over 1.0 % |
| camera policy | agent 6, m5 6, search 17 |
| camera score (min / mean / max) | 0.79 / 3.90 / 5.95 |
| rooms by number of views | 1 with 0, 3 with 1, 4 with 2, 4 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 3.2 min / 6.1 min / 93.5 s |
| seconds: polish / gate / check | 2.9 min / 18.4 s / 44.9 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 12 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real06.blend](3d/real06.blend) | 516.8 MB |
| [real06.glb](3d/real06.glb) | 968.0 MB |

29 cameras; textures scaled to at most 1024 px (191 scaled) for the download.

## AI decor

46 decor items chosen by the AI (Qwen/Qwen3.8-27B-FP8; both passes agreeing) in 11 rooms; 100 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- elevation check: 0 facade(s) differ from the drawn elevation; roof heights mismatch
- drawn-piece check: 6 piece(s) moved beyond the tolerance, 9 locked-rule violation(s)
- AI completion: 7 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 98.4 % (limit 95 %), 64 comparisons |
| negative controls rejected | 90.9 % (limit 90 %), 176 comparisons |
| effect | polish allowed |

### Exterior views

Exterior decision: **polish_disabled**. The exterior views are the Cycles render; the rooms are not affected.

| item | value |
|---|---|
| benign exterior comparisons accepted | 95.8 % (limit 95 %), 24 comparisons |
| negative exterior comparisons rejected | 68.3 % (limit 90 %), 60 comparisons |

Reasons:

- negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- exterior_base: [contact_sbs_exterior_base.jpg](contact_sbs_exterior_base.jpg)

- r_L0_banyo: [contact_sbs_r_L0_banyo.jpg](contact_sbs_r_L0_banyo.jpg)

- r_L0_mutfak: [contact_sbs_r_L0_mutfak.jpg](contact_sbs_r_L0_mutfak.jpg)

- r_L0_salon: [contact_sbs_r_L0_salon.jpg](contact_sbs_r_L0_salon.jpg)

- r_L1_banyo: [contact_sbs_r_L1_banyo.jpg](contact_sbs_r_L1_banyo.jpg)

- r_L1_cocuk_odasi: [contact_sbs_r_L1_cocuk_odasi.jpg](contact_sbs_r_L1_cocuk_odasi.jpg)

- r_L1_dus: [contact_sbs_r_L1_dus.jpg](contact_sbs_r_L1_dus.jpg)

- r_L1_ebeveyn_y_odasi: [contact_sbs_r_L1_ebeveyn_y_odasi.jpg](contact_sbs_r_L1_ebeveyn_y_odasi.jpg)

- r_L1_hol: [contact_sbs_r_L1_hol.jpg](contact_sbs_r_L1_hol.jpg)

- r_L1_oda: [contact_sbs_r_L1_oda.jpg](contact_sbs_r_L1_oda.jpg)

- r_L1_oda_2: [contact_sbs_r_L1_oda_2.jpg](contact_sbs_r_L1_oda_2.jpg)

- r_L1_soyunma_odasi: [contact_sbs_r_L1_soyunma_odasi.jpg](contact_sbs_r_L1_soyunma_odasi.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| exterior_base | ext_1 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_2 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_3 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_4 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_5 | - | - | info | - | - | cycles (gate_validation) |
| exterior_base | ext_6 | - | - | info | - | - | cycles (gate_validation) |
| r_L0_banyo | cam_r_L0_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L0_mutfak | cam_r_L0_mutfak_1 | a3 s 0.125 depth x0.8 | accept | info | - | - | cycles (error) |
| r_L0_mutfak | cam_r_L0_mutfak_2 | a2 s 0.25 canny x0.8 | accept | info | - | - | cycles (error) |
| r_L0_mutfak | cam_r_L0_mutfak_3 | a2 s 0.25 canny x0.8 | accept | info | - | - | cycles (error) |
| r_L0_salon | cam_r_L0_salon_1 | - | - | info | - | - | cycles (room) |
| r_L0_salon | cam_r_L0_salon_2 | - | - | info | - | - | cycles (room) |
| r_L0_salon | cam_r_L0_salon_3 | - | - | info | - | - | cycles (room) |
| r_L1_banyo | cam_r_L1_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L1_banyo | cam_r_L1_banyo_2 | - | - | info | - | - | cycles (not_run) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_1 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_cocuk_odasi | cam_r_L1_cocuk_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L1_dus | cam_r_L1_dus_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L1_dus | cam_r_L1_dus_2 | a3 s 0.125 depth x0.8 | accept | info | - | - | cycles (error) |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_1 | - | - | info | - | - | cycles (gate) |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_2 | - | - | info | - | - | cycles (room) |
| r_L1_ebeveyn_y_odasi | cam_r_L1_ebeveyn_y_odasi_3 | - | - | info | - | - | cycles (room) |
| r_L1_hol | cam_r_L1_hol_1 | - | - | info | - | - | cycles (gate) |
| r_L1_oda | cam_r_L1_oda_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L1_oda_2 | cam_r_L1_oda_2_1 | - | - | info | - | - | cycles (room) |
| r_L1_oda_2 | cam_r_L1_oda_2_2 | - | - | info | - | - | cycles (room) |
| r_L1_soyunma_odasi | cam_r_L1_soyunma_odasi_1 | a1 s 0.375 geometry x0.8 | accept | info | - | - | cycles (error) |
| r_L1_soyunma_odasi | cam_r_L1_soyunma_odasi_2 | a2 s 0.25 canny x0.8 | accept | info | - | - | cycles (error) |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | -0.67 | - | agent | D3 A5 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | error | a3 s 0.125 depth x0.8 | accept | info | - | - | -0.17 | -2 | search 3.42 | D4 A5 | 3 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.00 | -3 | search 3.33 | D4 A9 | 3 | yes | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | -0.33 | -2 | search 3.19 | D5 A3 | 3 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | room | - | - | info | - | - | -0.33 | -2 | search 4.00 | D7 A5 | 2 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | cycles | room | - | - | info | - | - | -0.17 | -2 | search 4.00 | D8 A4 | 3 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | cycles | room | - | - | info | - | - | -0.33 | -2 | search 3.77 | D13 A6 | 9 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.00 | -3 | search 4.06 | D4 A6 | 2 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | cycles | not_run | - | - | info | - | - | +1.17 | -3 | search 2.52 | D6 A2 | 3 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | -0.67 | -1 | search 4.60 | D5 A8 | 1 | yes | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | -1.00 | -1 | agent | D5 A7 | 1 | yes | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | -0.83 | -1 | search 4.43 | D4 A5 | 1 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_dus_1 | r_L1_dus | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.67 | -3 | agent | D3 A3 | 0 | no | [preview](cam_r_L1_dus_1_final_preview.jpg) [plan](cam_r_L1_dus_1_plan.jpg) |
| cam_r_L1_dus_2 | r_L1_dus | L1 | cycles | error | a3 s 0.125 depth x0.8 | accept | info | - | - | +0.83 | -3 | search 0.79 | D3 A4 | 0 | no | [preview](cam_r_L1_dus_2_final_preview.jpg) [plan](cam_r_L1_dus_2_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_1 | r_L1_ebeveyn_y_odasi | L1 | cycles | gate | - | - | info | - | - | +0.00 | -2 | search 5.95 | D8 A4 | 3 | yes | [preview](cam_r_L1_ebeveyn_y_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_2 | r_L1_ebeveyn_y_odasi | L1 | cycles | room | - | - | info | - | - | +0.00 | -1 | search 5.66 | D8 A2 | 4 | yes | [preview](cam_r_L1_ebeveyn_y_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_y_odasi_3 | r_L1_ebeveyn_y_odasi | L1 | cycles | room | - | - | info | - | - | -0.17 | -2 | search 5.30 | D7 A3 | 3 | yes | [preview](cam_r_L1_ebeveyn_y_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_y_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | gate | - | - | info | - | - | +0.67 | - | agent | D2 A5 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_oda_1 | r_L1_oda | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +0.83 | - | agent | D3 A4 | 2 | yes | [preview](cam_r_L1_oda_1_final_preview.jpg) [plan](cam_r_L1_oda_1_plan.jpg) |
| cam_r_L1_oda_2_1 | r_L1_oda_2 | L1 | cycles | room | - | - | info | - | - | -1.00 | -1 | search 4.50 | D4 A2 | 4 | no | [preview](cam_r_L1_oda_2_1_final_preview.jpg) [plan](cam_r_L1_oda_2_1_plan.jpg) |
| cam_r_L1_oda_2_2 | r_L1_oda_2 | L1 | cycles | room | - | - | info | - | - | -1.00 | -1 | search 4.49 | D5 A3 | 5 | yes | [preview](cam_r_L1_oda_2_2_final_preview.jpg) [plan](cam_r_L1_oda_2_2_plan.jpg) |
| cam_r_L1_soyunma_odasi_1 | r_L1_soyunma_odasi | L1 | cycles | error | a1 s 0.375 geometry x0.8 | accept | info | - | - | +1.50 | - | search 2.29 | D4 A3 | 1 | yes | [preview](cam_r_L1_soyunma_odasi_1_final_preview.jpg) [plan](cam_r_L1_soyunma_odasi_1_plan.jpg) |
| cam_r_L1_soyunma_odasi_2 | r_L1_soyunma_odasi | L1 | cycles | error | a2 s 0.25 canny x0.8 | accept | info | - | - | +1.33 | - | agent | D4 | 3 | no | [preview](cam_r_L1_soyunma_odasi_2_final_preview.jpg) [plan](cam_r_L1_soyunma_odasi_2_plan.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D10 | 5 | no | [preview](ext_1_final_preview.jpg) [plan](ext_1_plan.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.83 | 0 | m5 | D15 | 7 | no | [preview](ext_2_final_preview.jpg) [plan](ext_2_plan.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | info | - | - | -4.17 | 0 | m5 | D14 | 6 | no | [preview](ext_3_final_preview.jpg) [plan](ext_3_plan.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -7.17 | 0 | m5 | D12 | 1 | no | [preview](ext_4_final_preview.jpg) [plan](ext_4_plan.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.17 | 0 | m5 | D14 | 6 | no | [preview](ext_5_final_preview.jpg) [plan](ext_5_plan.jpg) |
| ext_6 | - | unknown | cycles | gate_validation | - | - | info | - | - | -6.67 | 0 | m5 | D5 | 0 | no | [preview](ext_6_final_preview.jpg) [plan](ext_6_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5); interior: the panes of a window between two rooms, pulled k EV steps only where they clip (clip before -> as written). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_banyo | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_oda | storage | L0 | 0 | 0 | 0 | - |
| r_L0_salon | living | L0 | 3 | 0 | 3 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L1_banyo | storage | L1 | 2 | 0 | 2 | cam_r_L1_banyo_1, cam_r_L1_banyo_2 |
| r_L1_cocuk_odasi | storage | L1 | 3 | 0 | 3 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_dus | storage | L1 | 2 | 0 | 2 | cam_r_L1_dus_1, cam_r_L1_dus_2 |
| r_L1_ebeveyn_y_odasi | storage | L1 | 3 | 0 | 3 | cam_r_L1_ebeveyn_y_odasi_1, cam_r_L1_ebeveyn_y_odasi_2, cam_r_L1_ebeveyn_y_odasi_3 |
| r_L1_hol | storage | L1 | 1 | 0 | 1 | cam_r_L1_hol_1 |
| r_L1_oda | storage | L1 | 1 | 0 | 1 | cam_r_L1_oda_1 |
| r_L1_oda_2 | storage | L1 | 2 | 0 | 2 | cam_r_L1_oda_2_1, cam_r_L1_oda_2_2 |
| r_L1_soyunma_odasi | storage | L1 | 2 | 0 | 2 | cam_r_L1_soyunma_odasi_1, cam_r_L1_soyunma_odasi_2 |

Rooms without a rendered view: r_L0_oda (no furniture after layout and decor and 2.13 m2 < 2.5 m2: no view (docs/milestone7.md §6.2)).

### Why Cycles

- cam_r_L0_banyo_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_mutfak_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_mutfak_2: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_mutfak_3: error: polished from another render (source sha256 differs from the current render)
- cam_r_L0_salon_1: room: polish: room
- cam_r_L0_salon_2: room: polish: room
- cam_r_L0_salon_3: room: polish: room
- cam_r_L1_banyo_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_banyo_2: not_run: view not in the polish manifest
- cam_r_L1_cocuk_odasi_1: room: polish: room
- cam_r_L1_cocuk_odasi_2: room: polish: room
- cam_r_L1_cocuk_odasi_3: room: polish: room
- cam_r_L1_dus_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_dus_2: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_ebeveyn_y_odasi_1: gate: no ladder attempt passed the gate: a1 reject (masks, neutral); a2 reject (masks); a3 reject (masks)
- cam_r_L1_ebeveyn_y_odasi_2: room: polish: room
- cam_r_L1_ebeveyn_y_odasi_3: room: polish: room
- cam_r_L1_hol_1: gate: no ladder attempt passed the gate: a1 reject (depth, edges); a2 reject (depth); a3 reject (depth)
- cam_r_L1_oda_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_oda_2_1: room: polish: room
- cam_r_L1_oda_2_2: room: polish: room
- cam_r_L1_soyunma_odasi_1: error: polished from another render (source sha256 differs from the current render)
- cam_r_L1_soyunma_odasi_2: error: polished from another render (source sha256 differs from the current render)
- ext_1: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_2: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_3: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_4: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_5: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)
- ext_6: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_mutfak_2 | cycles | cross-check in_json_not_rendered | o_L0_001 | window | - | from_documents | real06.dwg gap:LINE:294815,LINE:294819,LINE:2947C5,LINE:2947C9 derived 0.50; orchestrator/architect_answers.json inferred 0.60 | yes | visible 0.86, area 0.034 |
| cam_r_L1_cocuk_odasi_1 | cycles | cross-check misplaced | d_L1_008 | door | - | from_documents | real06.dwg ARC:298361,LINE:298367,LINE:298363,LINE:29835D,LINE:298387,LINE:29835E,LINE:298388,LINE:29835F,CIRCLE:29835A,LINE:29835B,LINE:298358,CIRCLE:298359,LINE:298389,LINE:29AB59,ARC:29AB5A,LINE:29AB58,LINE:29AB5B vector 0.95 | yes | 73 % of its pixels > 0.10 m outside the drawing, 153019 px |
| cam_r_L1_cocuk_odasi_2 | cycles | cross-check misplaced | f_L1_007 | bed_double | - | from_documents | real06.dwg ARC:297260-297261,ARC:297270,ARC:297306,LINE:297267-297269,LINE:297271-297305,LINE:297307-297761,ARC:29725B,ARC:29725E,ARC:29725F,ARC:29726F,ARC:29735D,LINE:293E9B,LINE:29726A,LINE:29726B,LINE:29726C,LINE:29726D,LINE:29726E,LINE:29727A,LINE:29727B,LINE:29727C,LINE:29727D,LINE:29727E,LINE:29727F,LINE:29728A,LINE:29728B,LINE:29728C,LINE:29728D,LINE:29728E,LINE:29728F,LINE:29729A,LINE:29729B,LINE:29729C,LINE:29729D,LINE:29729E,LINE:29729F,LINE:2972A0,LINE:2972A1,LINE:2972A2,LINE:2972A3,LINE:2972A4,LINE:2972A5,LINE:2972A6,LINE:2972A7,LINE:2972A8,LINE:2972A9,LINE:2972AA,LINE:2972AB,LINE:2972AC,LINE:2972AD,LINE:2972AE,LINE:2972AF,LINE:2972B0,LINE:2972B1,LINE:2972B2,LINE:2972B3,LINE:2972B4,LINE:2972B5,LINE:2972B6,LINE:2972B7,LINE:2972B8,LINE:2972B9,LINE:2972BA,LINE:2972BB,LINE:2972BC,LINE:2972BD,LINE:2972BE,LINE:2972BF,LINE:2972C0,LINE:2972C1,LINE:2972C2,LINE:2972C3,LINE:2972C4,LINE:2972C5,LINE:2972C6,LINE:2972C7,LINE:2972C8,LINE:2972C9,LINE:2972CA,LINE:2972CB,LINE:2972CC,LINE:2972CD,LINE:2972CE,LINE:2972CF,LINE:2972D0,LINE:2972D1,LINE:2972D2,LINE:2972D3,LINE:2972D4,LINE:2972D5,LINE:2972D6,LINE:2972D7,LINE:2972D8,LINE:2972D9,LINE:2972DA,LINE:2972DB,LINE:2972DC,LINE:2972DD,LINE:2972DE,LINE:2972DF,LINE:2972E0,LINE:2972E1,LINE:2972E2,LINE:2972E3,LINE:2972E4,LINE:2972E5,LINE:2972E6,LINE:2972E7,LINE:2972E8,LINE:2972E9,LINE:2972EA,LINE:2972EB,LINE:2972EC,LINE:2972ED,LINE:2972EE,LINE:2972EF,LINE:2972F0,LINE:2972F1,LINE:2972F2,LINE:2972F3,LINE:2972F4,LINE:2972F5,LINE:2972F6,LINE:2972F7,LINE:2972F8,LINE:2972F9,LINE:2972FA,LINE:2972FB,LINE:2972FC,LINE:2972FD,LINE:2972FE,LINE:2972FF,LINE:29730A,LINE:29730B,LINE:29730C,LINE:29730D,LINE:29730E,LINE:29730F,LINE:29731A,LINE:29731B,LINE:29731C,LINE:29731D,LINE:29731E,LINE:29731F,LINE:29732A,LINE:29732B,LINE:29732C,LINE:29732D,LINE:29732E,LINE:29732F,LINE:29733A,LINE:29733B,LINE:29733C,LINE:29733D,LINE:29733E,LINE:29733F,LINE:29734A,LINE:29734B,LINE:29734C,LINE:29734D,LINE:29734E,LINE:29734F,LINE:29735A,LINE:29735B,LINE:29735C,LINE:29735E,LINE:29736A,LINE:29736B,LINE:29736C,LINE:29736D,LINE:29736E,LINE:29736F,LINE:29737A,LINE:29737B,LINE:29737C,LINE:29737D,LINE:29737E,LINE:29737F,LINE:29738A,LINE:29738B,LINE:29738C,LINE:29738D,LINE:29738E,LINE:29738F,LINE:29739A,LINE:29739B,LINE:29739C,LINE:29739D,LINE:29739E,LINE:29739F,LINE:2973A0,LINE:2973A1,LINE:2973A2,LINE:2973A3,LINE:2973A4,LINE:2973A5,LINE:2973A6,LINE:2973A7,LINE:2973A8,LINE:2973A9,LINE:2973AA,LINE:2973AB,LINE:2973AC,LINE:2973AD,LINE:2973AE,LINE:2973AF,LINE:2973B0,LINE:2973B1,LINE:2973B2,LINE:2973B3,LINE:2973B4,LINE:2973B5,LINE:2973B6,LINE:2973B7,LINE:2973B8,LINE:2973B9,LINE:2973BA,LINE:2973BB,LINE:2973BC,LINE:2973BD,LINE:2973BE,LINE:2973BF,LINE:2973C0,LINE:2973C1,LINE:2973C2,LINE:2973C3,LINE:2973C4,LINE:2973C5,LINE:2973C6,LINE:2973C7,LINE:2973C8,LINE:2973C9,LINE:2973CA,LINE:2973CB,LINE:2973CC,LINE:2973CD,LINE:2973CE,LINE:2973CF,LINE:2973D0,LINE:2973D1,LINE:2973D2,LINE:2973D3,LINE:2973D4,LINE:2973D5,LINE:2973D6,LINE:2973D7,LINE:2973D8,LINE:2973D9,LINE:2973DA,LINE:2973DB,LINE:2973DC,LINE:2973DD,LINE:2973DE,LINE:2973DF,LINE:2973E0,LINE:2973E1,LINE:2973E2,LINE:2973E3,LINE:2973E4,LINE:2973E5,LINE:2973E6,LINE:2973E7,LINE:2973E8,LINE:2973E9,LINE:2973EA,LINE:2973EB,LINE:2973EC,LINE:2973ED,LINE:2973EE,LINE:2973EF,LINE:2973F0,LINE:2973F1,LINE:2973F2,LINE:2973F3,LINE:2973F4,LINE:2973F5,LINE:2973F6,LINE:2973F7,LINE:2973F8,LINE:2973F9,LINE:2973FA,LINE:2973FB,LINE:2973FC,LINE:2973FD,LINE:2973FE,LINE:2973FF,LINE:29740A,LINE:29740B,LINE:29740C,LINE:29740D,LINE:29740E,LINE:29740F,LINE:29741A,LINE:29741B,LINE:29741C,LINE:29741D,LINE:29741E,LINE:29741F,LINE:29742A,LINE:29742B,LINE:29742C,LINE:29742D,LINE:29742E,LINE:29742F,LINE:29743A,LINE:29743B,LINE:29743C,LINE:29743D,LINE:29743E,LINE:29743F,LINE:29744A,LINE:29744B,LINE:29744C,LINE:29744D,LINE:29744E,LINE:29744F,LINE:29745A,LINE:29745B,LINE:29745C,LINE:29745D,LINE:29745E,LINE:29745F,LINE:29746A,LINE:29746B,LINE:29746C,LINE:29746D,LINE:29746E,LINE:29746F,LINE:29747A,LINE:29747B,LINE:29747C,LINE:29747D,LINE:29747E,LINE:29747F,LINE:29748A,LINE:29748B,LINE:29748C,LINE:29748D,LINE:29748E,LINE:29748F,LINE:29749A,LINE:29749B,LINE:29749C,LINE:29749D,LINE:29749E,LINE:29749F,LINE:2974A0,LINE:2974A1,LINE:2974A2,LINE:2974A3,LINE:2974A4,LINE:2974A5,LINE:2974A6,LINE:2974A7,LINE:2974A8,LINE:2974A9,LINE:2974AA,LINE:2974AB,LINE:2974AC,LINE:2974AD,LINE:2974AE,LINE:2974AF,LINE:2974B0,LINE:2974B1,LINE:2974B2,LINE:2974B3,LINE:2974B4,LINE:2974B5,LINE:2974B6,LINE:2974B7,LINE:2974B8,LINE:2974B9,LINE:2974BA,LINE:2974BB,LINE:2974BC,LINE:2974BD,LINE:2974BE,LINE:2974BF,LINE:2974C0,LINE:2974C1,LINE:2974C2,LINE:2974C3,LINE:2974C4,LINE:2974C5,LINE:2974C6,LINE:2974C7,LINE:2974C8,LINE:2974C9,LINE:2974CA,LINE:2974CB,LINE:2974CC,LINE:2974CD,LINE:2974CE,LINE:2974CF,LINE:2974D0,LINE:2974D1,LINE:2974D2,LINE:2974D3,LINE:2974D4,LINE:2974D5,LINE:2974D6,LINE:2974D7,LINE:2974D8,LINE:2974D9,LINE:2974DA,LINE:2974DB,LINE:2974DC,LINE:2974DD,LINE:2974DE,LINE:2974DF,LINE:2974E0,LINE:2974E1,LINE:2974E2,LINE:2974E3,LINE:2974E4,LINE:2974E5,LINE:2974E6,LINE:2974E7,LINE:2974E8,LINE:2974E9,LINE:2974EA,LINE:2974EB,LINE:2974EC,LINE:2974ED,LINE:2974EE,LINE:2974EF,LINE:2974F0,LINE:2974F1,LINE:2974F2,LINE:2974F3,LINE:2974F4,LINE:2974F5,LINE:2974F6,LINE:2974F7,LINE:2974F8,LINE:2974F9,LINE:2974FA,LINE:2974FB,LINE:2974FC,LINE:2974FD,LINE:2974FE,LINE:2974FF,LINE:29750A,LINE:29750B,LINE:29750C,LINE:29750D,LINE:29750E,LINE:29750F,LINE:29751A,LINE:29751B,LINE:29751C,LINE:29751D,LINE:29751E,LINE:29751F,LINE:29752A,LINE:29752B,LINE:29752C,LINE:29752D,LINE:29752E,LINE:29752F,LINE:29753A,LINE:29753B,LINE:29753C,LINE:29753D,LINE:29753E,LINE:29753F,LINE:29754A,LINE:29754B,LINE:29754C,LINE:29754D,LINE:29754E,LINE:29754F,LINE:29755A,LINE:29755B,LINE:29755C,LINE:29755D,LINE:29755E,LINE:29755F,LINE:29756A,LINE:29756B,LINE:29756C,LINE:29756D,LINE:29756E,LINE:29756F,LINE:29757A,LINE:29757B,LINE:29757C,LINE:29757D,LINE:29757E,LINE:29757F,LINE:29758A,LINE:29758B,LINE:29758C,LINE:29758D,LINE:29758E,LINE:29758F,LINE:29759A,LINE:29759B,LINE:29759C,LINE:29759D,LINE:29759E,LINE:29759F,LINE:2975A0,LINE:2975A1,LINE:2975A2,LINE:2975A3,LINE:2975A4,LINE:2975A5,LINE:2975A6,LINE:2975A7,LINE:2975A8,LINE:2975A9,LINE:2975AA,LINE:2975AB,LINE:2975AC,LINE:2975AD,LINE:2975AE,LINE:2975AF,LINE:2975B0,LINE:2975B1,LINE:2975B2,LINE:2975B3,LINE:2975B4,LINE:2975B5,LINE:2975B6,LINE:2975B7,LINE:2975B8,LINE:2975B9,LINE:2975BA,LINE:2975BB,LINE:2975BC,LINE:2975BD,LINE:2975BE,LINE:2975BF,LINE:2975C0,LINE:2975C1,LINE:2975C2,LINE:2975C3,LINE:2975C4,LINE:2975C5,LINE:2975C6,LINE:2975C7,LINE:2975C8,LINE:2975C9,LINE:2975CA,LINE:2975CB,LINE:2975CC,LINE:2975CD,LINE:2975CE,LINE:2975CF,LINE:2975D0,LINE:2975D1,LINE:2975D2,LINE:2975D3,LINE:2975D4,LINE:2975D5,LINE:2975D6,LINE:2975D7,LINE:2975D8,LINE:2975D9,LINE:2975DA,LINE:2975DB,LINE:2975DC,LINE:2975DD,LINE:2975DE,LINE:2975DF,LINE:2975E0,LINE:2975E1,LINE:2975E2,LINE:2975E3,LINE:2975E4,LINE:2975E5,LINE:2975E6,LINE:2975E7,LINE:2975E8,LINE:2975E9,LINE:2975EA,LINE:2975EB,LINE:2975EC,LINE:2975ED,LINE:2975EE,LINE:2975EF,LINE:2975F0,LINE:2975F1,LINE:2975F2,LINE:2975F3,LINE:2975F4,LINE:2975F5,LINE:2975F6,LINE:2975F7,LINE:2975F8,LINE:2975F9,LINE:2975FA,LINE:2975FB,LINE:2975FC,LINE:2975FD,LINE:2975FE,LINE:2975FF,LINE:29760A,LINE:29760B,LINE:29760C,LINE:29760D,LINE:29760E,LINE:29760F,LINE:29761A,LINE:29761B,LINE:29761C,LINE:29761D,LINE:29761E,LINE:29761F,LINE:29762A,LINE:29762B,LINE:29762C,LINE:29762D,LINE:29762E,LINE:29762F,LINE:29763A,LINE:29763B,LINE:29763C,LINE:29763D,LINE:29763E,LINE:29763F,LINE:29764A,LINE:29764B,LINE:29764C,LINE:29764D,LINE:29764E,LINE:29764F,LINE:29765A,LINE:29765B,LINE:29765C,LINE:29765D,LINE:29765E,LINE:29765F,LINE:29766A,LINE:29766B,LINE:29766C,LINE:29766D,LINE:29766E,LINE:29766F,LINE:29767A,LINE:29767B,LINE:29767C,LINE:29767D,LINE:29767E,LINE:29767F,LINE:29768A,LINE:29768B,LINE:29768C,LINE:29768D,LINE:29768E,LINE:29768F,LINE:29769A,LINE:29769B,LINE:29769C,LINE:29769D,LINE:29769E,LINE:29769F,LINE:2976A0,LINE:2976A1,LINE:2976A2,LINE:2976A3,LINE:2976A4,LINE:2976A5,LINE:2976A6,LINE:2976A7,LINE:2976A8,LINE:2976A9,LINE:2976AA,LINE:2976AB,LINE:2976AC,LINE:2976AD,LINE:2976AE,LINE:2976AF,LINE:2976B0,LINE:2976B1,LINE:2976B2,LINE:2976B3,LINE:2976B4,LINE:2976B5,LINE:2976B6,LINE:2976B7,LINE:2976B8,LINE:2976B9,LINE:2976BA,LINE:2976BB,LINE:2976BC,LINE:2976BD,LINE:2976BE,LINE:2976BF,LINE:2976C0,LINE:2976C1,LINE:2976C2,LINE:2976C3,LINE:2976C4,LINE:2976C5,LINE:2976C6,LINE:2976C7,LINE:2976C8,LINE:2976C9,LINE:2976CA,LINE:2976CB,LINE:2976CC,LINE:2976CD,LINE:2976CE,LINE:2976CF,LINE:2976D0,LINE:2976D1,LINE:2976D2,LINE:2976D3,LINE:2976D4,LINE:2976D5,LINE:2976D6,LINE:2976D7,LINE:2976D8,LINE:2976D9,LINE:2976DA,LINE:2976DB,LINE:2976DC,LINE:2976DD,LINE:2976DE,LINE:2976DF,LINE:2976E0,LINE:2976E1,LINE:2976E2,LINE:2976E3,LINE:2976E4,LINE:2976E5,LINE:2976E6,LINE:2976E7,LINE:2976E8,LINE:2976E9,LINE:2976EA,LINE:2976EB,LINE:2976EC,LINE:2976F2,LINE:2976F3,LINE:2976F4,LINE:2976F5,LINE:2976F6,LINE:2976F7,LINE:2976F8,LINE:2976F9,LINE:2976FA,LINE:2976FB,LINE:2976FC,LINE:2976FD,LINE:2976FE,LINE:2976FF,LINE:29770A,LINE:29770B,LINE:29770C,LINE:29770D,LINE:29770E,LINE:29770F,LINE:29771A,LINE:29771B,LINE:29771C,LINE:29771D,LINE:29771E,LINE:29771F,LINE:29772A,LINE:29772B,LINE:29772C,LINE:29772D,LINE:29772E,LINE:29772F,LINE:29773A,LINE:29773B,LINE:29773C,LINE:29773D,LINE:29773E,LINE:29773F,LINE:29774A,LINE:29774B,LINE:29774C,LINE:29774D,LINE:29774E,LINE:29774F,LINE:29775A,LINE:29775B,LINE:29775C,LINE:29775D,LINE:29775E,LINE:29775F vector 0.90; real06.dwg recognition:sym_L1_004 ai 0.95; +2 more | yes | 40 % of its pixels > 0.10 m outside the drawing, 181103 px |
| cam_r_L1_ebeveyn_y_odasi_1 | cycles | cross-check misplaced | d_L1_002 | door | - | from_documents | real06.dwg ARC:2982E5,LINE:2982EB,LINE:2982E7,LINE:2982E1,LINE:2982E2,LINE:2982E3,LINE:29AB8B,ARC:29AB8A,LINE:2982DC,LINE:2982DF,CIRCLE:2982DD,CIRCLE:2982DE,LINE:29AB89,LINE:29830D,LINE:29AB88,LINE:29830C,LINE:29830B vector 0.95 | yes | 100 % of its pixels > 0.10 m outside the drawing, 163009 px |
| cam_r_L1_ebeveyn_y_odasi_1 | cycles | cross-check misplaced | f_L1_010 | bed_double | - | from_documents | real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF vector 0.90; real06.dwg LINE:296900-296975,LINE:296980-297199,ARC:2968E4,ARC:2968E5,ARC:2968E6,ARC:2968F3,ARC:2968F8,ARC:29694C,ARC:296D54,ARC:296D5B,ARC:296D5F,ARC:296D60,ARC:296D61,ARC:296D67,ARC:296D68,ARC:296DCB,ARC:296DFB,LINE:2968E7,LINE:2968E8,LINE:2968E9,LINE:2968EA,LINE:2968EB,LINE:2968F4,LINE:2968F5,LINE:2968F6,LINE:2968F7,LINE:2968F9,LINE:2968FA,LINE:2968FB,LINE:2968FC,LINE:2968FD,LINE:2968FE,LINE:2968FF,LINE:29690A,LINE:29690B,LINE:29690C,LINE:29690D,LINE:29690E,LINE:29690F,LINE:29691A,LINE:29691B,LINE:29691C,LINE:29691D,LINE:29691E,LINE:29691F,LINE:29692A,LINE:29692B,LINE:29692C,LINE:29692D,LINE:29692E,LINE:29692F,LINE:29693A,LINE:29693B,LINE:29693C,LINE:29693D,LINE:29693E,LINE:29693F,LINE:29694A,LINE:29694B,LINE:29694D,LINE:29694E,LINE:29694F,LINE:29695A,LINE:29695B,LINE:29695C,LINE:29695D,LINE:29695E,LINE:29695F,LINE:29696A,LINE:29696B,LINE:29696C,LINE:29696D,LINE:29696E,LINE:29696F,LINE:29697B,LINE:29697C,LINE:29697D,LINE:29697E,LINE:29697F,LINE:29698A,LINE:29698B,LINE:29698C,LINE:29698D,LINE:29698E,LINE:29698F,LINE:29699A,LINE:29699B,LINE:29699C,LINE:29699D,LINE:29699E,LINE:29699F,LINE:2969A0,LINE:2969A1,LINE:2969A2,LINE:2969A3,LINE:2969A4,LINE:2969A5,LINE:2969A6,LINE:2969A7,LINE:2969A8,LINE:2969A9,LINE:2969AA,LINE:2969AB,LINE:2969AC,LINE:2969AD,LINE:2969AE,LINE:2969AF,LINE:2969B0,LINE:2969B1,LINE:2969B2,LINE:2969B3,LINE:2969B4,LINE:2969B5,LINE:2969B6,LINE:2969B7,LINE:2969B8,LINE:2969B9,LINE:2969BA,LINE:2969BB,LINE:2969BC,LINE:2969BD,LINE:2969BE,LINE:2969BF,LINE:2969C0,LINE:2969C1,LINE:2969C2,LINE:2969C3,LINE:2969C4,LINE:2969C5,LINE:2969C6,LINE:2969C7,LINE:2969C8,LINE:2969C9,LINE:2969CA,LINE:2969CB,LINE:2969CC,LINE:2969CD,LINE:2969CE,LINE:2969CF,LINE:2969D0,LINE:2969D1,LINE:2969D2,LINE:2969D3,LINE:2969D4,LINE:2969D5,LINE:2969D6,LINE:2969D7,LINE:2969D8,LINE:2969D9,LINE:2969DA,LINE:2969DB,LINE:2969DC,LINE:2969DD,LINE:2969DE,LINE:2969DF,LINE:2969E0,LINE:2969E1,LINE:2969E2,LINE:2969E3,LINE:2969E4,LINE:2969E5,LINE:2969E6,LINE:2969E7,LINE:2969E8,LINE:2969E9,LINE:2969EA,LINE:2969EB,LINE:2969EC,LINE:2969ED,LINE:2969EE,LINE:2969EF,LINE:2969F0,LINE:2969F1,LINE:2969F2,LINE:2969F3,LINE:2969F4,LINE:2969F5,LINE:2969F6,LINE:2969F7,LINE:2969F8,LINE:2969F9,LINE:2969FA,LINE:2969FB,LINE:2969FC,LINE:2969FD,LINE:2969FE,LINE:2969FF,LINE:296A00,LINE:296A01,LINE:296A02,LINE:296A03,LINE:296A04,LINE:296A05,LINE:296A06,LINE:296A07,LINE:296A08,LINE:296A09,LINE:296A0A,LINE:296A0B,LINE:296A0C,LINE:296A0D,LINE:296A0E,LINE:296A0F,LINE:296A10,LINE:296A11,LINE:296A12,LINE:296A13,LINE:296A14,LINE:296A15,LINE:296A16,LINE:296A17,LINE:296A18,LINE:296A19,LINE:296A1A,LINE:296A1B,LINE:296A1C,LINE:296A1D,LINE:296A1E,LINE:296A1F,LINE:296A20,LINE:296A21,LINE:296A22,LINE:296A23,LINE:296A24,LINE:296A25,LINE:296A26,LINE:296A27,LINE:296A28,LINE:296A29,LINE:296A2A,LINE:296A2B,LINE:296A2C,LINE:296A2D,LINE:296A2E,LINE:296A2F,LINE:296A30,LINE:296A31,LINE:296A32,LINE:296A33,LINE:296A34,LINE:296A35,LINE:296A36,LINE:296A37,LINE:296A38,LINE:296A39,LINE:296A3A,LINE:296A3B,LINE:296A3C,LINE:296A3D,LINE:296A3E,LINE:296A3F,LINE:296A40,LINE:296A41,LINE:296A42,LINE:296A43,LINE:296A44,LINE:296A45,LINE:296A46,LINE:296A47,LINE:296A48,LINE:296A49,LINE:296A4A,LINE:296A4B,LINE:296A4C,LINE:296A4D,LINE:296A4E,LINE:296A4F,LINE:296A50,LINE:296A51,LINE:296A52,LINE:296A53,LINE:296A54,LINE:296A55,LINE:296A56,LINE:296A57,LINE:296A58,LINE:296A59,LINE:296A5A,LINE:296A5B,LINE:296A5C,LINE:296A5D,LINE:296A5E,LINE:296A5F,LINE:296A60,LINE:296A61,LINE:296A62,LINE:296A63,LINE:296A64,LINE:296A65,LINE:296A66,LINE:296A67,LINE:296A68,LINE:296A69,LINE:296A6A,LINE:296A6B,LINE:296A6C,LINE:296A6D,LINE:296A6E,LINE:296A6F,LINE:296A70,LINE:296A71,LINE:296A72,LINE:296A73,LINE:296A74,LINE:296A75,LINE:296A76,LINE:296A77,LINE:296A78,LINE:296A79,LINE:296A7A,LINE:296A7B,LINE:296A7C,LINE:296A7D,LINE:296A7E,LINE:296A7F,LINE:296A80,LINE:296A81,LINE:296A82,LINE:296A83,LINE:296A84,LINE:296A85,LINE:296A86,LINE:296A87,LINE:296A88,LINE:296A89,LINE:296A8A,LINE:296A8B,LINE:296A8C,LINE:296A8D,LINE:296A8E,LINE:296A8F,LINE:296A90,LINE:296A91,LINE:296A92,LINE:296A93,LINE:296A94,LINE:296A95,LINE:296A96,LINE:296A97,LINE:296A98,LINE:296A99,LINE:296A9A,LINE:296A9B,LINE:296A9C,LINE:296A9D,LINE:296A9E,LINE:296A9F,LINE:296AA0,LINE:296AA1,LINE:296AA2,LINE:296AA3,LINE:296AA4,LINE:296AA5,LINE:296AA6,LINE:296AA7,LINE:296AA8,LINE:296AA9,LINE:296AAA,LINE:296AAB,LINE:296AAC,LINE:296AAD,LINE:296AAE,LINE:296AAF,LINE:296AB0,LINE:296AB1,LINE:296AB2,LINE:296AB3,LINE:296AB4,LINE:296AB5,LINE:296AB6,LINE:296AB7,LINE:296AB8,LINE:296AB9,LINE:296ABA,LINE:296ABB,LINE:296ABC,LINE:296ABD,LINE:296ABE,LINE:296ABF,LINE:296AC0,LINE:296AC1,LINE:296AC2,LINE:296AC3,LINE:296AC4,LINE:296AC5,LINE:296AC6,LINE:296AC7,LINE:296AC8,LINE:296AC9,LINE:296ACA,LINE:296ACB,LINE:296ACC,LINE:296ACD,LINE:296ACE,LINE:296ACF,LINE:296AD0,LINE:296AD1,LINE:296AD2,LINE:296AD3,LINE:296AD4,LINE:296AD5,LINE:296AD6,LINE:296AD7,LINE:296AD8,LINE:296AD9,LINE:296ADA,LINE:296ADB,LINE:296ADC,LINE:296ADD,LINE:296ADE,LINE:296ADF,LINE:296AE0,LINE:296AE1,LINE:296AE2,LINE:296AE3,LINE:296AE4,LINE:296AE5,LINE:296AE6,LINE:296AE7,LINE:296AE8,LINE:296AE9,LINE:296AEA,LINE:296AEB,LINE:296AEC,LINE:296AED,LINE:296AEE,LINE:296AEF,LINE:296AF0,LINE:296AF1,LINE:296AF2,LINE:296AF3,LINE:296AF4,LINE:296AF5,LINE:296AF6,LINE:296AF7,LINE:296AF8,LINE:296AF9,LINE:296AFA,LINE:296AFB,LINE:296AFC,LINE:296AFD,LINE:296AFE,LINE:296AFF,LINE:296B00,LINE:296B01,LINE:296B02,LINE:296B03,LINE:296B04,LINE:296B05,LINE:296B06,LINE:296B07,LINE:296B08,LINE:296B09,LINE:296B0A,LINE:296B0B,LINE:296B0C,LINE:296B0D,LINE:296B0E,LINE:296B0F,LINE:296B10,LINE:296B11,LINE:296B12,LINE:296B13,LINE:296B14,LINE:296B15,LINE:296B16,LINE:296B17,LINE:296B18,LINE:296B19,LINE:296B1A,LINE:296B1B,LINE:296B1C,LINE:296B1D,LINE:296B1E,LINE:296B1F,LINE:296B20,LINE:296B21,LINE:296B22,LINE:296B23,LINE:296B24,LINE:296B25,LINE:296B26,LINE:296B27,LINE:296B28,LINE:296B29,LINE:296B2A,LINE:296B2B,LINE:296B2C,LINE:296B2D,LINE:296B2E,LINE:296B2F,LINE:296B30,LINE:296B31,LINE:296B32,LINE:296B33,LINE:296B34,LINE:296B35,LINE:296B36,LINE:296B37,LINE:296B38,LINE:296B39,LINE:296B3A,LINE:296B3B,LINE:296B3C,LINE:296B3D,LINE:296B3E,LINE:296B3F,LINE:296B40,LINE:296B41,LINE:296B42,LINE:296B43,LINE:296B44,LINE:296B45,LINE:296B46,LINE:296B47,LINE:296B48,LINE:296B49,LINE:296B4A,LINE:296B4B,LINE:296B4C,LINE:296B4D,LINE:296B4E,LINE:296B4F,LINE:296B50,LINE:296B51,LINE:296B52,LINE:296B53,LINE:296B54,LINE:296B55,LINE:296B56,LINE:296B57,LINE:296B58,LINE:296B59,LINE:296B5A,LINE:296B5B,LINE:296B5C,LINE:296B5D,LINE:296B5E,LINE:296B5F,LINE:296B60,LINE:296B61,LINE:296B62,LINE:296B63,LINE:296B64,LINE:296B65,LINE:296B66,LINE:296B67,LINE:296B68,LINE:296B69,LINE:296B6A,LINE:296B6B,LINE:296B6C,LINE:296B6D,LINE:296B6E,LINE:296B6F,LINE:296B70,LINE:296B71,LINE:296B72,LINE:296B73,LINE:296B74,LINE:296B75,LINE:296B76,LINE:296B77,LINE:296B78,LINE:296B79,LINE:296B7A,LINE:296B7B,LINE:296B7C,LINE:296B7D,LINE:296B7E,LINE:296B7F,LINE:296B80,LINE:296B81,LINE:296B82,LINE:296B83,LINE:296B84,LINE:296B85,LINE:296B86,LINE:296B87,LINE:296B88,LINE:296B89,LINE:296B8A,LINE:296B8B,LINE:296B8C,LINE:296B8D,LINE:296B8E,LINE:296B8F,LINE:296B90,LINE:296B91,LINE:296B92,LINE:296B93,LINE:296B94,LINE:296B95,LINE:296B96,LINE:296B97,LINE:296B98,LINE:296B99,LINE:296B9A,LINE:296B9B,LINE:296B9C,LINE:296B9D,LINE:296B9E,LINE:296B9F,LINE:296BA0,LINE:296BA1,LINE:296BA2,LINE:296BA3,LINE:296BA4,LINE:296BA5,LINE:296BA6,LINE:296BA7,LINE:296BA8,LINE:296BA9,LINE:296BAA,LINE:296BAB,LINE:296BAC,LINE:296BAD,LINE:296BAE,LINE:296BAF,LINE:296BB0,LINE:296BB1,LINE:296BB2,LINE:296BB3,LINE:296BB4,LINE:296BB5,LINE:296BB6,LINE:296BB7,LINE:296BB8,LINE:296BB9,LINE:296BBA,LINE:296BBB,LINE:296BBC,LINE:296BBD,LINE:296BBE,LINE:296BBF,LINE:296BC0,LINE:296BC1,LINE:296BC2,LINE:296BC3,LINE:296BC4,LINE:296BC5,LINE:296BC6,LINE:296BC7,LINE:296BC8,LINE:296BC9,LINE:296BCA,LINE:296BCB,LINE:296BCC,LINE:296BCD,LINE:296BCE,LINE:296BCF,LINE:296BD0,LINE:296BD1,LINE:296BD2,LINE:296BD3,LINE:296BD4,LINE:296BD5,LINE:296BD6,LINE:296BD7,LINE:296BD8,LINE:296BD9,LINE:296BDA,LINE:296BDB,LINE:296BDC,LINE:296BDD,LINE:296BDE,LINE:296BDF,LINE:296BE0,LINE:296BE1,LINE:296BE2,LINE:296BE3,LINE:296BE4,LINE:296BE5,LINE:296BE6,LINE:296BE7,LINE:296BE8,LINE:296BE9,LINE:296BEA,LINE:296BEB,LINE:296BEC,LINE:296BED,LINE:296BEE,LINE:296BEF,LINE:296BF0,LINE:296BF1,LINE:296BF2,LINE:296BF3,LINE:296BF4,LINE:296BF5,LINE:296BF6,LINE:296BF7,LINE:296BF8,LINE:296BF9,LINE:296BFA,LINE:296BFB,LINE:296BFC,LINE:296BFD,LINE:296BFE,LINE:296BFF,LINE:296C00,LINE:296C01,LINE:296C02,LINE:296C03,LINE:296C04,LINE:296C05,LINE:296C06,LINE:296C07,LINE:296C08,LINE:296C09,LINE:296C0A,LINE:296C0B,LINE:296C0C,LINE:296C0D,LINE:296C0E,LINE:296C0F,LINE:296C10,LINE:296C11,LINE:296C12,LINE:296C13,LINE:296C14,LINE:296C15,LINE:296C16,LINE:296C17,LINE:296C18,LINE:296C19,LINE:296C1A,LINE:296C1B,LINE:296C1C,LINE:296C1D,LINE:296C1E,LINE:296C1F,LINE:296C20,LINE:296C21,LINE:296C22,LINE:296C23,LINE:296C24,LINE:296C25,LINE:296C26,LINE:296C27,LINE:296C28,LINE:296C29,LINE:296C2A,LINE:296C2B,LINE:296C2C,LINE:296C2D,LINE:296C2E,LINE:296C2F,LINE:296C30,LINE:296C31,LINE:296C32,LINE:296C33,LINE:296C34,LINE:296C35,LINE:296C36,LINE:296C37,LINE:296C38,LINE:296C39,LINE:296C3A,LINE:296C3B,LINE:296C3C,LINE:296C3D,LINE:296C3E,LINE:296C3F,LINE:296C40,LINE:296C41,LINE:296C42,LINE:296C43,LINE:296C44,LINE:296C45,LINE:296C46,LINE:296C47,LINE:296C48,LINE:296C49,LINE:296C4A,LINE:296C4B,LINE:296C4C,LINE:296C4D,LINE:296C4E,LINE:296C4F,LINE:296C50,LINE:296C51,LINE:296C52,LINE:296C53,LINE:296C54,LINE:296C55,LINE:296C56,LINE:296C57,LINE:296C58,LINE:296C59,LINE:296C5A,LINE:296C5B,LINE:296C5C,LINE:296C5D,LINE:296C5E,LINE:296C5F,LINE:296C60,LINE:296C61,LINE:296C62,LINE:296C63,LINE:296C64,LINE:296C65,LINE:296C66,LINE:296C67,LINE:296C68,LINE:296C69,LINE:296C6A,LINE:296C6B,LINE:296C6C,LINE:296C6D,LINE:296C6E,LINE:296C6F,LINE:296C70,LINE:296C71,LINE:296C72,LINE:296C73,LINE:296C74,LINE:296C75,LINE:296C76,LINE:296C77,LINE:296C78,LINE:296C79,LINE:296C7A,LINE:296C7B,LINE:296C7C,LINE:296C7D,LINE:296C7E,LINE:296C7F,LINE:296C80,LINE:296C81,LINE:296C82,LINE:296C83,LINE:296C84,LINE:296C85,LINE:296C86,LINE:296C87,LINE:296C88,LINE:296C89,LINE:296C8A,LINE:296C8B,LINE:296C8C,LINE:296C8D,LINE:296C8E,LINE:296C8F,LINE:296C90,LINE:296C91,LINE:296C92,LINE:296C93,LINE:296C94,LINE:296C95,LINE:296C96,LINE:296C97,LINE:296C98,LINE:296C99,LINE:296C9A,LINE:296C9B,LINE:296C9C,LINE:296C9D,LINE:296C9E,LINE:296C9F,LINE:296CA0,LINE:296CA1,LINE:296CA2,LINE:296CA3,LINE:296CA4,LINE:296CA5,LINE:296CA6,LINE:296CA7,LINE:296CA8,LINE:296CA9,LINE:296CAA,LINE:296CAB,LINE:296CAC,LINE:296CAD,LINE:296CAE,LINE:296CAF,LINE:296CB0,LINE:296CB1,LINE:296CB2,LINE:296CB3,LINE:296CB4,LINE:296CB5,LINE:296CB6,LINE:296CB7,LINE:296CB8,LINE:296CB9,LINE:296CBA,LINE:296CBB,LINE:296CBC,LINE:296CBD,LINE:296CBE,LINE:296CBF,LINE:296CC0,LINE:296CC1,LINE:296CC2,LINE:296CC3,LINE:296CC4,LINE:296CC5,LINE:296CC6,LINE:296CC7,LINE:296CC8,LINE:296CC9,LINE:296CCA,LINE:296CCB,LINE:296CCC,LINE:296CCD,LINE:296CCE,LINE:296CCF,LINE:296CD0,LINE:296CD1,LINE:296CD2,LINE:296CD3,LINE:296CD4,LINE:296CD5,LINE:296CD6,LINE:296CD7,LINE:296CD8,LINE:296CD9,LINE:296CDA,LINE:296CDB,LINE:296CDC,LINE:296CDD,LINE:296CDE,LINE:296CDF,LINE:296CE0,LINE:296CE1,LINE:296CE2,LINE:296CE3,LINE:296CE4,LINE:296CE5,LINE:296CE6,LINE:296CE7,LINE:296CE8,LINE:296CE9,LINE:296CEA,LINE:296CEB,LINE:296CEC,LINE:296CED,LINE:296CEE,LINE:296CEF,LINE:296CF0,LINE:296CF1,LINE:296CF2,LINE:296CF3,LINE:296CF4,LINE:296CF5,LINE:296CF6,LINE:296CF7,LINE:296CF8,LINE:296CF9,LINE:296CFA,LINE:296CFB,LINE:296CFC,LINE:296CFD,LINE:296CFE,LINE:296CFF,LINE:296D00,LINE:296D01,LINE:296D02,LINE:296D03,LINE:296D04,LINE:296D05,LINE:296D06,LINE:296D07,LINE:296D08,LINE:296D09,LINE:296D0A,LINE:296D0B,LINE:296D0C,LINE:296D0D,LINE:296D0E,LINE:296D0F,LINE:296D10,LINE:296D11,LINE:296D12,LINE:296D13,LINE:296D14,LINE:296D15,LINE:296D16,LINE:296D17,LINE:296D18,LINE:296D19,LINE:296D1A,LINE:296D1B,LINE:296D1C,LINE:296D1D,LINE:296D1E,LINE:296D1F,LINE:296D20,LINE:296D21,LINE:296D22,LINE:296D23,LINE:296D24,LINE:296D25,LINE:296D26,LINE:296D27,LINE:296D28,LINE:296D29,LINE:296D2A,LINE:296D2B,LINE:296D2C,LINE:296D2D,LINE:296D2E,LINE:296D2F,LINE:296D30,LINE:296D31,LINE:296D32,LINE:296D33,LINE:296D34,LINE:296D35,LINE:296D36,LINE:296D37,LINE:296D38,LINE:296D39,LINE:296D3A,LINE:296D3B,LINE:296D3C,LINE:296D3D,LINE:296D3E,LINE:296D3F,LINE:296D40,LINE:296D41,LINE:296D42,LINE:296D43,LINE:296D44,LINE:296D45,LINE:296D46,LINE:296D47,LINE:296D48,LINE:296D49,LINE:296D4A,LINE:296D4B,LINE:296D4C,LINE:296D4D,LINE:296D4E,LINE:296D4F,LINE:296D50,LINE:296D51,LINE:296D52,LINE:296D62,LINE:296D63,LINE:296D64,LINE:296D65,LINE:296D66,LINE:296D69,LINE:296D6A,LINE:296D6B,LINE:296D6C,LINE:296D6D,LINE:296D6E,LINE:296D6F,LINE:296D70,LINE:296D71,LINE:296D72,LINE:296D73,LINE:296D74,LINE:296D75,LINE:296D76,LINE:296D77,LINE:296D78,LINE:296D79,LINE:296D7A,LINE:296D7B,LINE:296D7C,LINE:296D7D,LINE:296D7E,LINE:296D7F,LINE:296D80,LINE:296D81,LINE:296D82,LINE:296D83,LINE:296D84,LINE:296D85,LINE:296D86,LINE:296D87,LINE:296D88,LINE:296D89,LINE:296D8A,LINE:296D8B,LINE:296D90,LINE:296D91,LINE:296D92,LINE:296D93,LINE:296D94,LINE:296D95,LINE:296D96,LINE:296D97,LINE:296D98,LINE:296D99,LINE:296D9A,LINE:296D9B,LINE:296D9C,LINE:296D9D,LINE:296D9E,LINE:296D9F,LINE:296DA0,LINE:296DA1,LINE:296DA2,LINE:296DA3,LINE:296DA4,LINE:296DA5,LINE:296DA6,LINE:296DA7,LINE:296DA8,LINE:296DA9,LINE:296DAA,LINE:296DAB,LINE:296DAC,LINE:296DAD,LINE:296DAE,LINE:296DAF,LINE:296DB0,LINE:296DB1,LINE:296DB2,LINE:296DB3,LINE:296DB4,LINE:296DB5,LINE:296DB6,LINE:296DB7,LINE:296DB8,LINE:296DB9,LINE:296DBA,LINE:296DBB,LINE:296DBC,LINE:296DBD,LINE:296DBE,LINE:296DBF,LINE:296DC0,LINE:296DC1,LINE:296DC2,LINE:296DC3,LINE:296DC4,LINE:296DC5,LINE:296DC6,LINE:296DC7,LINE:296DC8,LINE:296DC9,LINE:296DCA,LINE:296DCC,LINE:296DCD,LINE:296DCE,LINE:296DCF,LINE:296DD0,LINE:296DD1,LINE:296DD2,LINE:296DD3,LINE:296DD4,LINE:296DD5,LINE:296DD6,LINE:296DD7,LINE:296DD8,LINE:296DD9,LINE:296DDA,LINE:296DDB,LINE:296DDC,LINE:296DDD,LINE:296DDE,LINE:296DDF,LINE:296DE0,LINE:296DE1,LINE:296DE2,LINE:296DE3,LINE:296DE4,LINE:296DE5,LINE:296DE6,LINE:296DE7,LINE:296DE8,LINE:296DE9,LINE:296DEA,LINE:296DEB,LINE:296DEC,LINE:296DED,LINE:296DEE,LINE:296DEF,LINE:296DF0,LINE:296DF1,LINE:296DF2,LINE:296DF3,LINE:296DF4,LINE:296DF5,LINE:296DF6,LINE:296DF7,LINE:296DF8,LINE:296DF9,LINE:296DFA,LINE:296DFC,LINE:296DFD,LINE:296DFE,LINE:296DFF,LINE:296E00,LINE:296E01,LINE:296E02,LINE:296E03,LINE:296E04,LINE:296E05,LINE:296E06,LINE:296E07,LINE:296E08,LINE:296E09,LINE:296E0A,LINE:296E0B,LINE:296E0C,LINE:296E0D,LINE:296E0E,LINE:296E0F,LINE:296E10,LINE:296E11,LINE:296E12,LINE:296E13,LINE:296E14,LINE:296E15,LINE:296E16,LINE:296E17,LINE:296E18,LINE:296E19,LINE:296E1A,LINE:296E1B,LINE:296E1C,LINE:296E1D,LINE:296E1E,LINE:296E1F,LINE:296E20,LINE:296E21,LINE:296E22,LINE:296E23,LINE:296E24,LINE:296E25,LINE:296E26,LINE:296E27,LINE:296E28,LINE:296E29,LINE:296E2A,LINE:296E2B,LINE:296E2C,LINE:296E2D,LINE:296E2E,LINE:296E2F,LINE:296E30,LINE:296E31,LINE:296E32,LINE:296E33,LINE:296E34,LINE:296E35,LINE:296E36,LINE:296E37,LINE:296E38,LINE:296E39,LINE:296E3A,LINE:296E3B,LINE:296E3C,LINE:296E3D,LINE:296E3E,LINE:296E3F,LINE:296E40,LINE:296E41,LINE:296E42,LINE:296E43,LINE:296E44,LINE:296E45,LINE:296E46,LINE:296E47,LINE:296E48,LINE:296E49,LINE:296E4A,LINE:296E4B,LINE:296E4C,LINE:296E4D,LINE:296E4E,LINE:296E4F,LINE:296E50,LINE:296E51,LINE:296E52,LINE:296E53,LINE:296E54,LINE:296E55,LINE:296E56,LINE:296E57,LINE:296E58,LINE:296E59,LINE:296E5A,LINE:296E5B,LINE:296E5C,LINE:296E5D,LINE:296E5E,LINE:296E5F,LINE:296E60,LINE:296E63,LINE:296E64,LINE:296E65,LINE:296E66,LINE:296E67,LINE:296E68,LINE:296E69,LINE:296E6A,LINE:296E6B,LINE:296E6C,LINE:296E6D,LINE:296E6E,LINE:296E6F,LINE:296E70,LINE:296E71,LINE:296E72,LINE:296E73,LINE:296E74,LINE:296E75,LINE:296E76,LINE:296E77,LINE:296E78,LINE:296E79,LINE:296E7A,LINE:296E7B,LINE:296E7C,LINE:296E7D,LINE:296E7E,LINE:296E7F,LINE:296E80,LINE:296E81,LINE:296E82,LINE:296E83,LINE:296E84,LINE:296E85,LINE:296E86,LINE:296E87,LINE:296E88,LINE:296E89,LINE:296E8A,LINE:296E8B,LINE:296E8C,LINE:296E8D,LINE:296E8E,LINE:296E8F,LINE:296E90,LINE:296E91,LINE:296E92,LINE:296E93,LINE:296E94,LINE:296E95,LINE:296E96,LINE:296E97,LINE:296E98,LINE:296E99,LINE:296E9A,LINE:296E9B,LINE:296E9C,LINE:296E9D,LINE:296E9E,LINE:296E9F,LINE:296EA0,LINE:296EA1,LINE:296EA2,LINE:296EA3,LINE:296EA4,LINE:296EA5,LINE:296EA6,LINE:296EA7,LINE:296EA8,LINE:296EA9,LINE:296EAA,LINE:296EAB,LINE:296EAC,LINE:296EAD,LINE:296EAE,LINE:296EAF,LINE:296EB0,LINE:296EB1,LINE:296EB2,LINE:296EB3,LINE:296EB4,LINE:296EB5,LINE:296EB6,LINE:296EB7,LINE:296EB8,LINE:296EB9,LINE:296EBA,LINE:296EBB,LINE:296EBC,LINE:296EBD,LINE:296EBE,LINE:296EBF,LINE:296EC0,LINE:296EC1,LINE:296EC2,LINE:296EC3,LINE:296EC4,LINE:296EC5,LINE:296EC6,LINE:296EC7,LINE:296EC8,LINE:296EC9,LINE:296ECA,LINE:296ECB,LINE:296ECC,LINE:296ECD,LINE:296ECE,LINE:296ECF,LINE:296ED0,LINE:296ED1,LINE:296ED2,LINE:296ED3,LINE:296ED4,LINE:296ED5,LINE:296ED6,LINE:296ED7,LINE:296ED8,LINE:296ED9,LINE:296EDA,LINE:296EDB,LINE:296EDC,LINE:296EDD,LINE:296EDE,LINE:296EDF,LINE:296EE0,LINE:296EE1,LINE:296EE2,LINE:296EE3,LINE:296EE4,LINE:296EE5,LINE:296EE6,LINE:296EE7,LINE:296EE8,LINE:296EE9,LINE:296EEA,LINE:296EEB,LINE:296EEC,LINE:296EED,LINE:296EEE,LINE:296EEF,LINE:296EF0,LINE:296EF1,LINE:296EF2,LINE:296EF3,LINE:296EF4,LINE:296EF5,LINE:296EF6,LINE:296EF7,LINE:296EF8,LINE:296EF9,LINE:296EFA,LINE:296EFB,LINE:296EFC,LINE:296EFD,LINE:296EFE,LINE:296EFF,LINE:296F00,LINE:296F01,LINE:296F02,LINE:296F03,LINE:296F04,LINE:296F05,LINE:296F06,LINE:296F07,LINE:296F08,LINE:296F09,LINE:296F0A,LINE:296F0B,LINE:296F0C,LINE:296F0D,LINE:296F0E,LINE:296F0F,LINE:296F10,LINE:296F11,LINE:296F12,LINE:296F13,LINE:296F14,LINE:296F15,LINE:296F16,LINE:296F17,LINE:296F18,LINE:296F19,LINE:296F1A,LINE:296F1B,LINE:296F1C,LINE:296F1D,LINE:296F1E,LINE:296F1F,LINE:296F20,LINE:296F21,LINE:296F22,LINE:296F23,LINE:296F24,LINE:296F25,LINE:296F26,LINE:296F27,LINE:296F28,LINE:296F29,LINE:296F2A,LINE:296F2B,LINE:296F2C,LINE:296F2D,LINE:296F2E,LINE:296F2F,LINE:296F30,LINE:296F31,LINE:296F32,LINE:296F33,LINE:296F34,LINE:296F35,LINE:296F36,LINE:296F37,LINE:296F38,LINE:296F39,LINE:296F3A,LINE:296F3B,LINE:296F3C,LINE:296F3D,LINE:296F3E,LINE:296F3F,LINE:296F40,LINE:296F41,LINE:296F42,LINE:296F43,LINE:296F44,LINE:296F45,LINE:296F46,LINE:296F47,LINE:296F48,LINE:296F49,LINE:296F4A,LINE:296F4B,LINE:296F4C,LINE:296F4D,LINE:296F4E,LINE:296F4F,LINE:296F50,LINE:296F51,LINE:296F52,LINE:296F53,LINE:296F54,LINE:296F55,LINE:296F56,LINE:296F57,LINE:296F58,LINE:296F59,LINE:296F5A,LINE:296F5B,LINE:296F5C,LINE:296F5D,LINE:296F5E,LINE:296F5F,LINE:296F60,LINE:296F61,LINE:296F62,LINE:296F63,LINE:296F64,LINE:296F65,LINE:296F66,LINE:296F67,LINE:296F68,LINE:296F69,LINE:296F6A,LINE:296F6B,LINE:296F6C,LINE:296F6D,LINE:296F6E,LINE:296F6F,LINE:296F70,LINE:296F71,LINE:296F72,LINE:296F73,LINE:296F74,LINE:296F75,LINE:296F76,LINE:296F77,LINE:296F78,LINE:296F79,LINE:296F7A,LINE:296F7B,LINE:296F7C,LINE:296F7D,LINE:296F7E,LINE:296F7F,LINE:296F80,LINE:296F81,LINE:296F82,LINE:296F83,LINE:296F84,LINE:296F85,LINE:296F86,LINE:296F87,LINE:296F88,LINE:296F89,LINE:296F8A,LINE:296F8B,LINE:296F8C,LINE:296F8D,LINE:296F8E,LINE:296F8F,LINE:296F90,LINE:296F91,LINE:296F92,LINE:296F93,LINE:296F94,LINE:296F95,LINE:296F96,LINE:296F97,LINE:296F98,LINE:296F99,LINE:296F9A,LINE:296F9B,LINE:296F9C,LINE:296F9D,LINE:296F9E,LINE:296F9F,LINE:296FA0,LINE:296FA1,LINE:296FA2,LINE:296FA3,LINE:296FA4,LINE:296FA5,LINE:296FA6,LINE:296FA7,LINE:296FA8,LINE:296FA9,LINE:296FAA,LINE:296FAB,LINE:296FAC,LINE:296FAD,LINE:296FAE,LINE:296FAF,LINE:296FB0,LINE:296FB1,LINE:296FB2,LINE:296FB3,LINE:296FB4,LINE:296FB5,LINE:296FB6,LINE:296FB7,LINE:296FB8,LINE:296FB9,LINE:296FBA,LINE:296FBB,LINE:296FBC,LINE:296FBD,LINE:296FBE,LINE:296FBF,LINE:296FC0,LINE:296FC1,LINE:296FC2,LINE:296FC3,LINE:296FC4,LINE:296FC5,LINE:296FC6,LINE:296FC7,LINE:296FC8,LINE:296FC9,LINE:296FCA,LINE:296FCB,LINE:296FCC,LINE:296FCD,LINE:296FCE,LINE:296FCF,LINE:296FD0,LINE:296FD1,LINE:296FD2,LINE:296FD3,LINE:296FD4,LINE:296FD5,LINE:296FD6,LINE:296FD7,LINE:296FD8,LINE:296FD9,LINE:296FDA,LINE:296FDB,LINE:296FDC,LINE:296FDD,LINE:296FDE,LINE:296FDF,LINE:296FE0,LINE:296FE1,LINE:296FE2,LINE:296FE3,LINE:296FE4,LINE:296FE5,LINE:296FE6,LINE:296FE7,LINE:296FE8,LINE:296FE9,LINE:296FEA,LINE:296FEB,LINE:296FEC,LINE:296FED,LINE:296FEE,LINE:296FEF,LINE:296FF0,LINE:296FF1,LINE:296FF2,LINE:296FF3,LINE:296FF4,LINE:296FF5,LINE:296FF6,LINE:296FF7,LINE:296FF8,LINE:296FF9,LINE:296FFA,LINE:296FFB,LINE:296FFC,LINE:296FFD,LINE:296FFE,LINE:296FFF,LINE:29700A,LINE:29700B,LINE:29700C,LINE:29700D,LINE:29700E,LINE:29700F,LINE:29701A,LINE:29701B,LINE:29701C,LINE:29701D,LINE:29701E,LINE:29701F,LINE:29702A,LINE:29702B,LINE:29702C,LINE:29702D,LINE:29702E,LINE:29702F,LINE:29703A,LINE:29703B,LINE:29703C,LINE:29703D,LINE:29703E,LINE:29703F,LINE:29704A,LINE:29704B,LINE:29704C,LINE:29704D,LINE:29704E,LINE:29704F,LINE:29705A,LINE:29705B,LINE:29705C,LINE:29705D,LINE:29705E,LINE:29705F,LINE:29706A,LINE:29706B,LINE:29706C,LINE:29706D,LINE:29706E,LINE:29706F,LINE:29707A,LINE:29707B,LINE:29707C,LINE:29707D,LINE:29707E,LINE:29707F,LINE:29708A,LINE:29708B,LINE:29708C,LINE:29708D,LINE:29708E,LINE:29708F,LINE:29709A,LINE:29709B,LINE:29709C,LINE:29709D,LINE:29709E,LINE:29709F,LINE:2970A0,LINE:2970A1,LINE:2970A2,LINE:2970A3,LINE:2970A4,LINE:2970A5,LINE:2970A6,LINE:2970A7,LINE:2970A8,LINE:2970A9,LINE:2970AA,LINE:2970AB,LINE:2970AC,LINE:2970AD,LINE:2970AE,LINE:2970AF,LINE:2970B0,LINE:2970B1,LINE:2970B2,LINE:2970B3,LINE:2970B4,LINE:2970B5,LINE:2970B6,LINE:2970B7,LINE:2970B8,LINE:2970B9,LINE:2970BA,LINE:2970BB,LINE:2970BC,LINE:2970BD,LINE:2970BE,LINE:2970BF,LINE:2970C0,LINE:2970C1,LINE:2970C2,LINE:2970C3,LINE:2970C4,LINE:2970C5,LINE:2970C6,LINE:2970C7,LINE:2970C8,LINE:2970C9,LINE:2970CA,LINE:2970CB,LINE:2970CC,LINE:2970CD,LINE:2970CE,LINE:2970CF,LINE:2970D0,LINE:2970D1,LINE:2970D2,LINE:2970D3,LINE:2970D4,LINE:2970D5,LINE:2970D6,LINE:2970D7,LINE:2970D8,LINE:2970D9,LINE:2970DA,LINE:2970DB,LINE:2970DC,LINE:2970DD,LINE:2970DE,LINE:2970DF,LINE:2970E0,LINE:2970E1,LINE:2970E2,LINE:2970E3,LINE:2970E4,LINE:2970E5,LINE:2970E6,LINE:2970E7,LINE:2970E8,LINE:2970E9,LINE:2970EA,LINE:2970EB,LINE:2970EC,LINE:2970ED,LINE:2970EE,LINE:2970EF,LINE:2970F0,LINE:2970F1,LINE:2970F2,LINE:2970F3,LINE:2970F4,LINE:2970F5,LINE:2970F6,LINE:2970F7,LINE:2970F8,LINE:2970F9,LINE:2970FA,LINE:2970FB,LINE:2970FC,LINE:2970FD,LINE:2970FE,LINE:2970FF,LINE:29710A,LINE:29710B,LINE:29710C,LINE:29710D,LINE:29710E,LINE:29710F,LINE:29711A,LINE:29711B,LINE:29711C,LINE:29711D,LINE:29711E,LINE:29711F,LINE:29712A,LINE:29712B,LINE:29712C,LINE:29712D,LINE:29712E,LINE:29712F,LINE:29713A,LINE:29713B,LINE:29713C,LINE:29713D,LINE:29713E,LINE:29713F,LINE:29714A,LINE:29714B,LINE:29714C,LINE:29714D,LINE:29714E,LINE:29714F,LINE:29715A,LINE:29715B,LINE:29715C,LINE:29715D,LINE:29715E,LINE:29715F,LINE:29716A,LINE:29716B,LINE:29716C,LINE:29716D,LINE:29716E,LINE:29716F,LINE:29717A,LINE:29717B,LINE:29717C,LINE:29717D,LINE:29717E,LINE:29717F,LINE:29718A,LINE:29718B,LINE:29718C,LINE:29718D,LINE:29718E,LINE:29718F,LINE:29719A,LINE:29719B,LINE:29719C,LINE:29719D,LINE:29719E,LINE:29719F,LINE:2971A0,LINE:2971A1,LINE:2971A2,LINE:2971A3,LINE:2971A4,LINE:2971A5,LINE:2971A6,LINE:2971A7,LINE:2971A8,LINE:2971A9,LINE:2971AA,LINE:2971AB,LINE:2971AC,LINE:2971AD,LINE:2971AE,LINE:2971AF,LINE:2971B0,LINE:2971B1,LINE:2971B2,LINE:2971B3,LINE:2971B4,LINE:2971B5,LINE:2971B6,LINE:2971B7,LINE:2971B8,LINE:2971B9,LINE:2971BA,LINE:2971BB,LINE:2971BC,LINE:2971BD,LINE:2971BE,LINE:2971BF,LINE:2971C0,LINE:2971C1,LINE:2971C2,LINE:2971C3,LINE:2971C4,LINE:2971C5,LINE:2971C6,LINE:2971C7,LINE:2971C8,LINE:2971C9,LINE:2971CA,LINE:2971CB,LINE:2971CC,LINE:2971CD,LINE:2971CE,LINE:2971CF inferred 0.60; +1 more | yes | 12 % of its pixels > 0.10 m outside the drawing, 304068 px |
| cam_r_L1_ebeveyn_y_odasi_2 | cycles | cross-check misplaced | d_L1_002 | door | - | from_documents | real06.dwg ARC:2982E5,LINE:2982EB,LINE:2982E7,LINE:2982E1,LINE:2982E2,LINE:2982E3,LINE:29AB8B,ARC:29AB8A,LINE:2982DC,LINE:2982DF,CIRCLE:2982DD,CIRCLE:2982DE,LINE:29AB89,LINE:29830D,LINE:29AB88,LINE:29830C,LINE:29830B vector 0.95 | yes | 66 % of its pixels > 0.10 m outside the drawing, 37924 px |
| cam_r_L1_ebeveyn_y_odasi_2 | cycles | cross-check misplaced | d_L1_008 | door | - | from_documents | real06.dwg ARC:298361,LINE:298367,LINE:298363,LINE:29835D,LINE:298387,LINE:29835E,LINE:298388,LINE:29835F,CIRCLE:29835A,LINE:29835B,LINE:298358,CIRCLE:298359,LINE:298389,LINE:29AB59,ARC:29AB5A,LINE:29AB58,LINE:29AB5B vector 0.95 | yes | 31 % of its pixels > 0.10 m outside the drawing, 7438 px |
| cam_r_L1_ebeveyn_y_odasi_2 | cycles | cross-check misplaced | win_L1_003 | door | - | from_documents | real06.dwg LINE:2576F9,LINE:2576FA,LINE:27198A,LINE:293D27,LINE:293D2D,LINE:293D2E,LINE:293D36,LINE:294906 vector 0.90; orchestrator/architect_answers.json inferred 0.60 | yes | 28 % of its pixels > 0.10 m outside the drawing, 31030 px |
| cam_r_L1_ebeveyn_y_odasi_3 | cycles | cross-check misplaced | d_L1_002 | door | - | from_documents | real06.dwg ARC:2982E5,LINE:2982EB,LINE:2982E7,LINE:2982E1,LINE:2982E2,LINE:2982E3,LINE:29AB8B,ARC:29AB8A,LINE:2982DC,LINE:2982DF,CIRCLE:2982DD,CIRCLE:2982DE,LINE:29AB89,LINE:29830D,LINE:29AB88,LINE:29830C,LINE:29830B vector 0.95 | yes | 72 % of its pixels > 0.10 m outside the drawing, 143365 px |
| cam_r_L1_oda_1 | cycles | cross-check misplaced | d_L1_002 | door | - | from_documents | real06.dwg ARC:2982E5,LINE:2982EB,LINE:2982E7,LINE:2982E1,LINE:2982E2,LINE:2982E3,LINE:29AB8B,ARC:29AB8A,LINE:2982DC,LINE:2982DF,CIRCLE:2982DD,CIRCLE:2982DE,LINE:29AB89,LINE:29830D,LINE:29AB88,LINE:29830C,LINE:29830B vector 0.95 | yes | 24 % of its pixels > 0.10 m outside the drawing, 147825 px |
| cam_r_L1_oda_2_2 | cycles | cross-check misplaced | f_L1_013 | bed_single | - | from_documents | real06.dwg LINE:298000-298126,LINE:298130-298199,ARC:297C95,ARC:297C98,ARC:297C99,ARC:297C9A,ARC:297C9B,ARC:297CA9,ARC:297CAA,ARC:297D40,ARC:297D97,LINE:297CA1,LINE:297CA2,LINE:297CA3,LINE:297CA4,LINE:297CA5,LINE:297CA6,LINE:297CA7,LINE:297CA8,LINE:297CAB,LINE:297CAC,LINE:297CAD,LINE:297CAE,LINE:297CAF,LINE:297CB0,LINE:297CB1,LINE:297CB2,LINE:297CB3,LINE:297CB4,LINE:297CB5,LINE:297CB6,LINE:297CB7,LINE:297CB8,LINE:297CB9,LINE:297CBA,LINE:297CBB,LINE:297CBC,LINE:297CBD,LINE:297CBE,LINE:297CBF,LINE:297CC0,LINE:297CC1,LINE:297CC2,LINE:297CC3,LINE:297CC4,LINE:297CC5,LINE:297CC6,LINE:297CC7,LINE:297CC8,LINE:297CC9,LINE:297CCA,LINE:297CCB,LINE:297CCC,LINE:297CCD,LINE:297CCE,LINE:297CCF,LINE:297CD0,LINE:297CD1,LINE:297CD2,LINE:297CD3,LINE:297CD4,LINE:297CD5,LINE:297CD6,LINE:297CD7,LINE:297CD8,LINE:297CD9,LINE:297CDA,LINE:297CDB,LINE:297CDD,LINE:297CDF,LINE:297CE2,LINE:297CE3,LINE:297CE4,LINE:297CE5,LINE:297CE6,LINE:297CE7,LINE:297CE8,LINE:297CE9,LINE:297CEA,LINE:297CEB,LINE:297CEC,LINE:297CED,LINE:297CEE,LINE:297CEF,LINE:297CF0,LINE:297CF1,LINE:297CF2,LINE:297CF3,LINE:297CF4,LINE:297CF5,LINE:297CF6,LINE:297CF7,LINE:297CF8,LINE:297CF9,LINE:297CFA,LINE:297CFB,LINE:297CFC,LINE:297CFD,LINE:297CFE,LINE:297CFF,LINE:297D00,LINE:297D01,LINE:297D02,LINE:297D03,LINE:297D04,LINE:297D05,LINE:297D06,LINE:297D07,LINE:297D08,LINE:297D09,LINE:297D0A,LINE:297D0B,LINE:297D0C,LINE:297D0D,LINE:297D0E,LINE:297D0F,LINE:297D10,LINE:297D11,LINE:297D12,LINE:297D13,LINE:297D14,LINE:297D15,LINE:297D16,LINE:297D17,LINE:297D18,LINE:297D19,LINE:297D1A,LINE:297D1B,LINE:297D1C,LINE:297D1D,LINE:297D1E,LINE:297D1F,LINE:297D20,LINE:297D21,LINE:297D22,LINE:297D23,LINE:297D24,LINE:297D25,LINE:297D26,LINE:297D27,LINE:297D28,LINE:297D29,LINE:297D2A,LINE:297D2B,LINE:297D2C,LINE:297D2D,LINE:297D2E,LINE:297D2F,LINE:297D30,LINE:297D31,LINE:297D32,LINE:297D33,LINE:297D34,LINE:297D35,LINE:297D36,LINE:297D37,LINE:297D38,LINE:297D39,LINE:297D3A,LINE:297D3B,LINE:297D3C,LINE:297D3D,LINE:297D3E,LINE:297D3F,LINE:297D41,LINE:297D42,LINE:297D43,LINE:297D44,LINE:297D45,LINE:297D46,LINE:297D47,LINE:297D48,LINE:297D49,LINE:297D4A,LINE:297D4B,LINE:297D4C,LINE:297D4D,LINE:297D4E,LINE:297D4F,LINE:297D50,LINE:297D51,LINE:297D52,LINE:297D53,LINE:297D54,LINE:297D55,LINE:297D56,LINE:297D57,LINE:297D58,LINE:297D59,LINE:297D5A,LINE:297D5B,LINE:297D5C,LINE:297D5D,LINE:297D5E,LINE:297D5F,LINE:297D60,LINE:297D61,LINE:297D62,LINE:297D63,LINE:297D64,LINE:297D65,LINE:297D66,LINE:297D67,LINE:297D68,LINE:297D69,LINE:297D6A,LINE:297D6B,LINE:297D6C,LINE:297D6D,LINE:297D6E,LINE:297D6F,LINE:297D70,LINE:297D71,LINE:297D72,LINE:297D73,LINE:297D74,LINE:297D75,LINE:297D76,LINE:297D77,LINE:297D78,LINE:297D79,LINE:297D7A,LINE:297D7B,LINE:297D7C,LINE:297D7D,LINE:297D7E,LINE:297D7F,LINE:297D80,LINE:297D81,LINE:297D82,LINE:297D83,LINE:297D84,LINE:297D85,LINE:297D86,LINE:297D87,LINE:297D88,LINE:297D89,LINE:297D8A,LINE:297D8B,LINE:297D8C,LINE:297D8D,LINE:297D8E,LINE:297D8F,LINE:297D90,LINE:297D91,LINE:297D92,LINE:297D93,LINE:297D94,LINE:297D95,LINE:297D96,LINE:297D98,LINE:297D9A,LINE:297D9B,LINE:297D9C,LINE:297D9D,LINE:297D9E,LINE:297D9F,LINE:297DA0,LINE:297DA1,LINE:297DA2,LINE:297DA3,LINE:297DA4,LINE:297DA5,LINE:297DA6,LINE:297DA7,LINE:297DA8,LINE:297DA9,LINE:297DAA,LINE:297DAB,LINE:297DAC,LINE:297DAD,LINE:297DAE,LINE:297DAF,LINE:297DB0,LINE:297DB1,LINE:297DB2,LINE:297DB3,LINE:297DB4,LINE:297DB5,LINE:297DB6,LINE:297DB7,LINE:297DB8,LINE:297DB9,LINE:297DBA,LINE:297DBB,LINE:297DBC,LINE:297DBD,LINE:297DBE,LINE:297DBF,LINE:297DC0,LINE:297DC1,LINE:297DC2,LINE:297DC3,LINE:297DC4,LINE:297DC5,LINE:297DC6,LINE:297DC7,LINE:297DC8,LINE:297DC9,LINE:297DCA,LINE:297DCB,LINE:297DCC,LINE:297DCD,LINE:297DCE,LINE:297DCF,LINE:297DD0,LINE:297DD1,LINE:297DD2,LINE:297DD3,LINE:297DD4,LINE:297DD5,LINE:297DD6,LINE:297DD7,LINE:297DD8,LINE:297DD9,LINE:297DDA,LINE:297DDB,LINE:297DDC,LINE:297DDD,LINE:297DDE,LINE:297DDF,LINE:297DE0,LINE:297DE1,LINE:297DE2,LINE:297DE3,LINE:297DE4,LINE:297DE5,LINE:297DE6,LINE:297DE7,LINE:297DE8,LINE:297DE9,LINE:297DEA,LINE:297DEB,LINE:297DEC,LINE:297DED,LINE:297DEE,LINE:297DEF,LINE:297DF0,LINE:297DF1,LINE:297DF2,LINE:297DF3,LINE:297DF4,LINE:297DF5,LINE:297DF6,LINE:297DF7,LINE:297DF8,LINE:297DF9,LINE:297DFA,LINE:297DFB,LINE:297DFC,LINE:297DFD,LINE:297DFE,LINE:297DFF,LINE:297E00,LINE:297E01,LINE:297E02,LINE:297E03,LINE:297E04,LINE:297E05,LINE:297E06,LINE:297E07,LINE:297E08,LINE:297E09,LINE:297E0A,LINE:297E0B,LINE:297E0C,LINE:297E0D,LINE:297E0E,LINE:297E0F,LINE:297E10,LINE:297E11,LINE:297E12,LINE:297E13,LINE:297E14,LINE:297E15,LINE:297E16,LINE:297E17,LINE:297E18,LINE:297E19,LINE:297E1A,LINE:297E1B,LINE:297E1C,LINE:297E1D,LINE:297E1E,LINE:297E1F,LINE:297E20,LINE:297E21,LINE:297E22,LINE:297E23,LINE:297E24,LINE:297E25,LINE:297E26,LINE:297E27,LINE:297E28,LINE:297E29,LINE:297E2A,LINE:297E2B,LINE:297E2C,LINE:297E2D,LINE:297E2E,LINE:297E2F,LINE:297E30,LINE:297E31,LINE:297E32,LINE:297E33,LINE:297E34,LINE:297E35,LINE:297E36,LINE:297E37,LINE:297E38,LINE:297E39,LINE:297E3A,LINE:297E3B,LINE:297E3C,LINE:297E3D,LINE:297E3E,LINE:297E3F,LINE:297E40,LINE:297E41,LINE:297E42,LINE:297E43,LINE:297E44,LINE:297E45,LINE:297E46,LINE:297E47,LINE:297E48,LINE:297E49,LINE:297E4A,LINE:297E4B,LINE:297E4C,LINE:297E4D,LINE:297E4E,LINE:297E4F,LINE:297E50,LINE:297E51,LINE:297E52,LINE:297E53,LINE:297E54,LINE:297E55,LINE:297E56,LINE:297E57,LINE:297E58,LINE:297E59,LINE:297E5A,LINE:297E5B,LINE:297E5C,LINE:297E5D,LINE:297E5E,LINE:297E5F,LINE:297E60,LINE:297E61,LINE:297E62,LINE:297E63,LINE:297E64,LINE:297E65,LINE:297E66,LINE:297E67,LINE:297E68,LINE:297E69,LINE:297E6A,LINE:297E6B,LINE:297E6C,LINE:297E6D,LINE:297E6E,LINE:297E6F,LINE:297E70,LINE:297E71,LINE:297E72,LINE:297E73,LINE:297E74,LINE:297E75,LINE:297E76,LINE:297E77,LINE:297E78,LINE:297E79,LINE:297E7A,LINE:297E7B,LINE:297E7C,LINE:297E7D,LINE:297E7E,LINE:297E7F,LINE:297E80,LINE:297E81,LINE:297E82,LINE:297E83,LINE:297E84,LINE:297E85,LINE:297E86,LINE:297E87,LINE:297E88,LINE:297E89,LINE:297E8A,LINE:297E8B,LINE:297E8C,LINE:297E8D,LINE:297E8E,LINE:297E8F,LINE:297E90,LINE:297E91,LINE:297E92,LINE:297E93,LINE:297E94,LINE:297E95,LINE:297E96,LINE:297E97,LINE:297E98,LINE:297E99,LINE:297E9A,LINE:297E9B,LINE:297E9C,LINE:297E9D,LINE:297E9E,LINE:297E9F,LINE:297EA0,LINE:297EA1,LINE:297EA2,LINE:297EA3,LINE:297EA4,LINE:297EA5,LINE:297EA6,LINE:297EA7,LINE:297EA8,LINE:297EA9,LINE:297EAA,LINE:297EAB,LINE:297EAC,LINE:297EAD,LINE:297EAE,LINE:297EAF,LINE:297EB0,LINE:297EB1,LINE:297EB2,LINE:297EB3,LINE:297EB4,LINE:297EB5,LINE:297EB6,LINE:297EB7,LINE:297EB8,LINE:297EB9,LINE:297EBA,LINE:297EBB,LINE:297EBC,LINE:297EBD,LINE:297EBE,LINE:297EBF,LINE:297EC0,LINE:297EC1,LINE:297EC2,LINE:297EC3,LINE:297EC4,LINE:297EC5,LINE:297EC6,LINE:297EC7,LINE:297EC8,LINE:297EC9,LINE:297ECA,LINE:297ECB,LINE:297ECC,LINE:297ECD,LINE:297ECE,LINE:297ECF,LINE:297ED0,LINE:297ED1,LINE:297ED2,LINE:297ED3,LINE:297ED4,LINE:297ED5,LINE:297ED6,LINE:297ED7,LINE:297ED8,LINE:297ED9,LINE:297EDA,LINE:297EDB,LINE:297EDC,LINE:297EDD,LINE:297EDE,LINE:297EDF,LINE:297EE0,LINE:297EE1,LINE:297EE2,LINE:297EE3,LINE:297EE4,LINE:297EE5,LINE:297EE6,LINE:297EE7,LINE:297EE8,LINE:297EE9,LINE:297EEA,LINE:297EEB,LINE:297EEC,LINE:297EED,LINE:297EEE,LINE:297EEF,LINE:297EF0,LINE:297EF1,LINE:297EF2,LINE:297EF3,LINE:297EF4,LINE:297EF5,LINE:297EF6,LINE:297EF7,LINE:297EF8,LINE:297EF9,LINE:297EFA,LINE:297EFB,LINE:297EFC,LINE:297EFD,LINE:297EFE,LINE:297EFF,LINE:297F00,LINE:297F01,LINE:297F02,LINE:297F03,LINE:297F04,LINE:297F05,LINE:297F06,LINE:297F07,LINE:297F08,LINE:297F09,LINE:297F0A,LINE:297F0B,LINE:297F0C,LINE:297F0D,LINE:297F0E,LINE:297F0F,LINE:297F10,LINE:297F11,LINE:297F12,LINE:297F13,LINE:297F14,LINE:297F15,LINE:297F16,LINE:297F17,LINE:297F18,LINE:297F19,LINE:297F1A,LINE:297F1B,LINE:297F1C,LINE:297F1D,LINE:297F1E,LINE:297F1F,LINE:297F20,LINE:297F21,LINE:297F22,LINE:297F23,LINE:297F24,LINE:297F25,LINE:297F26,LINE:297F27,LINE:297F28,LINE:297F29,LINE:297F2A,LINE:297F2B,LINE:297F2C,LINE:297F2D,LINE:297F2E,LINE:297F2F,LINE:297F30,LINE:297F31,LINE:297F32,LINE:297F33,LINE:297F34,LINE:297F35,LINE:297F36,LINE:297F37,LINE:297F38,LINE:297F39,LINE:297F3A,LINE:297F3B,LINE:297F3C,LINE:297F3D,LINE:297F3E,LINE:297F3F,LINE:297F40,LINE:297F41,LINE:297F42,LINE:297F43,LINE:297F44,LINE:297F45,LINE:297F46,LINE:297F47,LINE:297F48,LINE:297F49,LINE:297F4A,LINE:297F4B,LINE:297F4C,LINE:297F4D,LINE:297F4E,LINE:297F4F,LINE:297F50,LINE:297F51,LINE:297F52,LINE:297F53,LINE:297F54,LINE:297F55,LINE:297F56,LINE:297F57,LINE:297F58,LINE:297F59,LINE:297F5A,LINE:297F5B,LINE:297F5C,LINE:297F5D,LINE:297F5E,LINE:297F5F,LINE:297F60,LINE:297F61,LINE:297F62,LINE:297F63,LINE:297F64,LINE:297F65,LINE:297F66,LINE:297F67,LINE:297F68,LINE:297F69,LINE:297F6A,LINE:297F6B,LINE:297F6C,LINE:297F6D,LINE:297F6E,LINE:297F6F,LINE:297F70,LINE:297F71,LINE:297F72,LINE:297F73,LINE:297F74,LINE:297F75,LINE:297F76,LINE:297F77,LINE:297F78,LINE:297F79,LINE:297F7A,LINE:297F7B,LINE:297F7C,LINE:297F7D,LINE:297F7E,LINE:297F7F,LINE:297F80,LINE:297F81,LINE:297F82,LINE:297F83,LINE:297F84,LINE:297F85,LINE:297F86,LINE:297F87,LINE:297F88,LINE:297F89,LINE:297F8A,LINE:297F8B,LINE:297F8C,LINE:297F8D,LINE:297F8E,LINE:297F8F,LINE:297F90,LINE:297F91,LINE:297F92,LINE:297F93,LINE:297F94,LINE:297F95,LINE:297F96,LINE:297F97,LINE:297F98,LINE:297F99,LINE:297F9A,LINE:297F9B,LINE:297F9C,LINE:297F9D,LINE:297F9E,LINE:297F9F,LINE:297FA0,LINE:297FA1,LINE:297FA2,LINE:297FA3,LINE:297FA4,LINE:297FA5,LINE:297FA6,LINE:297FA7,LINE:297FA8,LINE:297FA9,LINE:297FAA,LINE:297FAB,LINE:297FAC,LINE:297FAD,LINE:297FAE,LINE:297FAF,LINE:297FB0,LINE:297FB1,LINE:297FB2,LINE:297FB3,LINE:297FB4,LINE:297FB5,LINE:297FB6,LINE:297FB7,LINE:297FB8,LINE:297FB9,LINE:297FBA,LINE:297FBB,LINE:297FBC,LINE:297FBD,LINE:297FBE,LINE:297FBF,LINE:297FC0,LINE:297FC1,LINE:297FC2,LINE:297FC3,LINE:297FC4,LINE:297FC5,LINE:297FC6,LINE:297FC7,LINE:297FC8,LINE:297FC9,LINE:297FCA,LINE:297FCB,LINE:297FCC,LINE:297FCD,LINE:297FCE,LINE:297FCF,LINE:297FD0,LINE:297FD1,LINE:297FD2,LINE:297FD3,LINE:297FD4,LINE:297FD5,LINE:297FD6,LINE:297FD7,LINE:297FD8,LINE:297FD9,LINE:297FDA,LINE:297FDB,LINE:297FDC,LINE:297FDD,LINE:297FDE,LINE:297FDF,LINE:297FE0,LINE:297FE1,LINE:297FE2,LINE:297FE3,LINE:297FE4,LINE:297FE5,LINE:297FE6,LINE:297FE7,LINE:297FE8,LINE:297FE9,LINE:297FEA,LINE:297FEB,LINE:297FEC,LINE:297FED,LINE:297FEE,LINE:297FEF,LINE:297FF0,LINE:297FF1,LINE:297FF2,LINE:297FF3,LINE:297FF4,LINE:297FF5,LINE:297FF6,LINE:297FF7,LINE:297FF8,LINE:297FF9,LINE:297FFA,LINE:297FFB,LINE:297FFC,LINE:297FFD,LINE:297FFE,LINE:297FFF,LINE:29800A,LINE:29800B,LINE:29800C,LINE:29800D,LINE:29800E,LINE:29800F,LINE:29801A,LINE:29801B,LINE:29801C,LINE:29801D,LINE:29801E,LINE:29801F,LINE:29802A,LINE:29802B,LINE:29802C,LINE:29802D,LINE:29802E,LINE:29802F,LINE:29803A,LINE:29803B,LINE:29803C,LINE:29803D,LINE:29803E,LINE:29803F,LINE:29804A,LINE:29804B,LINE:29804C,LINE:29804D,LINE:29804E,LINE:29804F,LINE:29805A,LINE:29805B,LINE:29805C,LINE:29805D,LINE:29805E,LINE:29805F,LINE:29806A,LINE:29806B,LINE:29806C,LINE:29806D,LINE:29806E,LINE:29806F,LINE:29807A,LINE:29807B,LINE:29807C,LINE:29807D,LINE:29807E,LINE:29807F,LINE:29808A,LINE:29808B,LINE:29808C,LINE:29808D,LINE:29808E,LINE:29808F,LINE:29809A,LINE:29809B,LINE:29809C,LINE:29809D,LINE:29809E,LINE:29809F,LINE:2980A0,LINE:2980A1,LINE:2980A2,LINE:2980A3,LINE:2980A4,LINE:2980A5,LINE:2980A6,LINE:2980A7,LINE:2980A8,LINE:2980A9,LINE:2980AA,LINE:2980AB,LINE:2980AC,LINE:2980AD,LINE:2980AE,LINE:2980AF,LINE:2980B0,LINE:2980B1,LINE:2980B2,LINE:2980B3,LINE:2980B4,LINE:2980B5,LINE:2980B6,LINE:2980B7,LINE:2980B8,LINE:2980B9,LINE:2980BA,LINE:2980BB,LINE:2980BC,LINE:2980BD,LINE:2980BE,LINE:2980BF,LINE:2980C0,LINE:2980C1,LINE:2980C2,LINE:2980C3,LINE:2980C4,LINE:2980C5,LINE:2980C6,LINE:2980C7,LINE:2980C8,LINE:2980C9,LINE:2980CA,LINE:2980CB,LINE:2980CC,LINE:2980CD,LINE:2980CE,LINE:2980CF,LINE:2980D0,LINE:2980D1,LINE:2980D2,LINE:2980D3,LINE:2980D4,LINE:2980D5,LINE:2980D6,LINE:2980D7,LINE:2980D8,LINE:2980D9,LINE:2980DA,LINE:2980DB,LINE:2980DC,LINE:2980DD,LINE:2980DE,LINE:2980DF,LINE:2980E0,LINE:2980E1,LINE:2980E2,LINE:2980E3,LINE:2980E4,LINE:2980E5,LINE:2980E6,LINE:2980E7,LINE:2980E8,LINE:2980E9,LINE:2980EA,LINE:2980EB,LINE:2980EC,LINE:2980ED,LINE:2980EE,LINE:2980EF,LINE:2980F0,LINE:2980F1,LINE:2980F2,LINE:2980F3,LINE:2980F4,LINE:2980F5,LINE:2980F6,LINE:2980F7,LINE:2980F8,LINE:2980F9,LINE:2980FA,LINE:2980FB,LINE:2980FC,LINE:2980FD,LINE:2980FE,LINE:2980FF,LINE:29810A,LINE:29810B,LINE:29810C,LINE:29810D,LINE:29810E,LINE:29810F,LINE:29811A,LINE:29811B,LINE:29811C,LINE:29811D,LINE:29811E,LINE:29811F,LINE:29812C,LINE:29812D,LINE:29812E,LINE:29812F,LINE:29813A,LINE:29813B,LINE:29813C,LINE:29813D,LINE:29813E,LINE:29813F,LINE:29814A,LINE:29814B,LINE:29814C,LINE:29814D,LINE:29814E,LINE:29814F,LINE:29815A,LINE:29815B,LINE:29815C,LINE:29815D,LINE:29815E,LINE:29815F,LINE:29816A,LINE:29816B,LINE:29816C,LINE:29816D,LINE:29816E,LINE:29816F,LINE:29817A,LINE:29817B,LINE:29817C,LINE:29817D,LINE:29817E,LINE:29817F,LINE:29818A,LINE:29818B,LINE:29818C,LINE:29818D,LINE:29818E,LINE:29818F,LINE:29819A,LINE:29819B vector 0.90; real06.dwg LINE:298000-298126,LINE:298130-298199,ARC:297C95,ARC:297C98,ARC:297C99,ARC:297C9A,ARC:297C9B,ARC:297CA9,ARC:297CAA,ARC:297D40,ARC:297D97,LINE:297CA1,LINE:297CA2,LINE:297CA3,LINE:297CA4,LINE:297CA5,LINE:297CA6,LINE:297CA7,LINE:297CA8,LINE:297CAB,LINE:297CAC,LINE:297CAD,LINE:297CAE,LINE:297CAF,LINE:297CB0,LINE:297CB1,LINE:297CB2,LINE:297CB3,LINE:297CB4,LINE:297CB5,LINE:297CB6,LINE:297CB7,LINE:297CB8,LINE:297CB9,LINE:297CBA,LINE:297CBB,LINE:297CBC,LINE:297CBD,LINE:297CBE,LINE:297CBF,LINE:297CC0,LINE:297CC1,LINE:297CC2,LINE:297CC3,LINE:297CC4,LINE:297CC5,LINE:297CC6,LINE:297CC7,LINE:297CC8,LINE:297CC9,LINE:297CCA,LINE:297CCB,LINE:297CCC,LINE:297CCD,LINE:297CCE,LINE:297CCF,LINE:297CD0,LINE:297CD1,LINE:297CD2,LINE:297CD3,LINE:297CD4,LINE:297CD5,LINE:297CD6,LINE:297CD7,LINE:297CD8,LINE:297CD9,LINE:297CDA,LINE:297CDB,LINE:297CDD,LINE:297CDF,LINE:297CE2,LINE:297CE3,LINE:297CE4,LINE:297CE5,LINE:297CE6,LINE:297CE7,LINE:297CE8,LINE:297CE9,LINE:297CEA,LINE:297CEB,LINE:297CEC,LINE:297CED,LINE:297CEE,LINE:297CEF,LINE:297CF0,LINE:297CF1,LINE:297CF2,LINE:297CF3,LINE:297CF4,LINE:297CF5,LINE:297CF6,LINE:297CF7,LINE:297CF8,LINE:297CF9,LINE:297CFA,LINE:297CFB,LINE:297CFC,LINE:297CFD,LINE:297CFE,LINE:297CFF,LINE:297D00,LINE:297D01,LINE:297D02,LINE:297D03,LINE:297D04,LINE:297D05,LINE:297D06,LINE:297D07,LINE:297D08,LINE:297D09,LINE:297D0A,LINE:297D0B,LINE:297D0C,LINE:297D0D,LINE:297D0E,LINE:297D0F,LINE:297D10,LINE:297D11,LINE:297D12,LINE:297D13,LINE:297D14,LINE:297D15,LINE:297D16,LINE:297D17,LINE:297D18,LINE:297D19,LINE:297D1A,LINE:297D1B,LINE:297D1C,LINE:297D1D,LINE:297D1E,LINE:297D1F,LINE:297D20,LINE:297D21,LINE:297D22,LINE:297D23,LINE:297D24,LINE:297D25,LINE:297D26,LINE:297D27,LINE:297D28,LINE:297D29,LINE:297D2A,LINE:297D2B,LINE:297D2C,LINE:297D2D,LINE:297D2E,LINE:297D2F,LINE:297D30,LINE:297D31,LINE:297D32,LINE:297D33,LINE:297D34,LINE:297D35,LINE:297D36,LINE:297D37,LINE:297D38,LINE:297D39,LINE:297D3A,LINE:297D3B,LINE:297D3C,LINE:297D3D,LINE:297D3E,LINE:297D3F,LINE:297D41,LINE:297D42,LINE:297D43,LINE:297D44,LINE:297D45,LINE:297D46,LINE:297D47,LINE:297D48,LINE:297D49,LINE:297D4A,LINE:297D4B,LINE:297D4C,LINE:297D4D,LINE:297D4E,LINE:297D4F,LINE:297D50,LINE:297D51,LINE:297D52,LINE:297D53,LINE:297D54,LINE:297D55,LINE:297D56,LINE:297D57,LINE:297D58,LINE:297D59,LINE:297D5A,LINE:297D5B,LINE:297D5C,LINE:297D5D,LINE:297D5E,LINE:297D5F,LINE:297D60,LINE:297D61,LINE:297D62,LINE:297D63,LINE:297D64,LINE:297D65,LINE:297D66,LINE:297D67,LINE:297D68,LINE:297D69,LINE:297D6A,LINE:297D6B,LINE:297D6C,LINE:297D6D,LINE:297D6E,LINE:297D6F,LINE:297D70,LINE:297D71,LINE:297D72,LINE:297D73,LINE:297D74,LINE:297D75,LINE:297D76,LINE:297D77,LINE:297D78,LINE:297D79,LINE:297D7A,LINE:297D7B,LINE:297D7C,LINE:297D7D,LINE:297D7E,LINE:297D7F,LINE:297D80,LINE:297D81,LINE:297D82,LINE:297D83,LINE:297D84,LINE:297D85,LINE:297D86,LINE:297D87,LINE:297D88,LINE:297D89,LINE:297D8A,LINE:297D8B,LINE:297D8C,LINE:297D8D,LINE:297D8E,LINE:297D8F,LINE:297D90,LINE:297D91,LINE:297D92,LINE:297D93,LINE:297D94,LINE:297D95,LINE:297D96,LINE:297D98,LINE:297D9A,LINE:297D9B,LINE:297D9C,LINE:297D9D,LINE:297D9E,LINE:297D9F,LINE:297DA0,LINE:297DA1,LINE:297DA2,LINE:297DA3,LINE:297DA4,LINE:297DA5,LINE:297DA6,LINE:297DA7,LINE:297DA8,LINE:297DA9,LINE:297DAA,LINE:297DAB,LINE:297DAC,LINE:297DAD,LINE:297DAE,LINE:297DAF,LINE:297DB0,LINE:297DB1,LINE:297DB2,LINE:297DB3,LINE:297DB4,LINE:297DB5,LINE:297DB6,LINE:297DB7,LINE:297DB8,LINE:297DB9,LINE:297DBA,LINE:297DBB,LINE:297DBC,LINE:297DBD,LINE:297DBE,LINE:297DBF,LINE:297DC0,LINE:297DC1,LINE:297DC2,LINE:297DC3,LINE:297DC4,LINE:297DC5,LINE:297DC6,LINE:297DC7,LINE:297DC8,LINE:297DC9,LINE:297DCA,LINE:297DCB,LINE:297DCC,LINE:297DCD,LINE:297DCE,LINE:297DCF,LINE:297DD0,LINE:297DD1,LINE:297DD2,LINE:297DD3,LINE:297DD4,LINE:297DD5,LINE:297DD6,LINE:297DD7,LINE:297DD8,LINE:297DD9,LINE:297DDA,LINE:297DDB,LINE:297DDC,LINE:297DDD,LINE:297DDE,LINE:297DDF,LINE:297DE0,LINE:297DE1,LINE:297DE2,LINE:297DE3,LINE:297DE4,LINE:297DE5,LINE:297DE6,LINE:297DE7,LINE:297DE8,LINE:297DE9,LINE:297DEA,LINE:297DEB,LINE:297DEC,LINE:297DED,LINE:297DEE,LINE:297DEF,LINE:297DF0,LINE:297DF1,LINE:297DF2,LINE:297DF3,LINE:297DF4,LINE:297DF5,LINE:297DF6,LINE:297DF7,LINE:297DF8,LINE:297DF9,LINE:297DFA,LINE:297DFB,LINE:297DFC,LINE:297DFD,LINE:297DFE,LINE:297DFF,LINE:297E00,LINE:297E01,LINE:297E02,LINE:297E03,LINE:297E04,LINE:297E05,LINE:297E06,LINE:297E07,LINE:297E08,LINE:297E09,LINE:297E0A,LINE:297E0B,LINE:297E0C,LINE:297E0D,LINE:297E0E,LINE:297E0F,LINE:297E10,LINE:297E11,LINE:297E12,LINE:297E13,LINE:297E14,LINE:297E15,LINE:297E16,LINE:297E17,LINE:297E18,LINE:297E19,LINE:297E1A,LINE:297E1B,LINE:297E1C,LINE:297E1D,LINE:297E1E,LINE:297E1F,LINE:297E20,LINE:297E21,LINE:297E22,LINE:297E23,LINE:297E24,LINE:297E25,LINE:297E26,LINE:297E27,LINE:297E28,LINE:297E29,LINE:297E2A,LINE:297E2B,LINE:297E2C,LINE:297E2D,LINE:297E2E,LINE:297E2F,LINE:297E30,LINE:297E31,LINE:297E32,LINE:297E33,LINE:297E34,LINE:297E35,LINE:297E36,LINE:297E37,LINE:297E38,LINE:297E39,LINE:297E3A,LINE:297E3B,LINE:297E3C,LINE:297E3D,LINE:297E3E,LINE:297E3F,LINE:297E40,LINE:297E41,LINE:297E42,LINE:297E43,LINE:297E44,LINE:297E45,LINE:297E46,LINE:297E47,LINE:297E48,LINE:297E49,LINE:297E4A,LINE:297E4B,LINE:297E4C,LINE:297E4D,LINE:297E4E,LINE:297E4F,LINE:297E50,LINE:297E51,LINE:297E52,LINE:297E53,LINE:297E54,LINE:297E55,LINE:297E56,LINE:297E57,LINE:297E58,LINE:297E59,LINE:297E5A,LINE:297E5B,LINE:297E5C,LINE:297E5D,LINE:297E5E,LINE:297E5F,LINE:297E60,LINE:297E61,LINE:297E62,LINE:297E63,LINE:297E64,LINE:297E65,LINE:297E66,LINE:297E67,LINE:297E68,LINE:297E69,LINE:297E6A,LINE:297E6B,LINE:297E6C,LINE:297E6D,LINE:297E6E,LINE:297E6F,LINE:297E70,LINE:297E71,LINE:297E72,LINE:297E73,LINE:297E74,LINE:297E75,LINE:297E76,LINE:297E77,LINE:297E78,LINE:297E79,LINE:297E7A,LINE:297E7B,LINE:297E7C,LINE:297E7D,LINE:297E7E,LINE:297E7F,LINE:297E80,LINE:297E81,LINE:297E82,LINE:297E83,LINE:297E84,LINE:297E85,LINE:297E86,LINE:297E87,LINE:297E88,LINE:297E89,LINE:297E8A,LINE:297E8B,LINE:297E8C,LINE:297E8D,LINE:297E8E,LINE:297E8F,LINE:297E90,LINE:297E91,LINE:297E92,LINE:297E93,LINE:297E94,LINE:297E95,LINE:297E96,LINE:297E97,LINE:297E98,LINE:297E99,LINE:297E9A,LINE:297E9B,LINE:297E9C,LINE:297E9D,LINE:297E9E,LINE:297E9F,LINE:297EA0,LINE:297EA1,LINE:297EA2,LINE:297EA3,LINE:297EA4,LINE:297EA5,LINE:297EA6,LINE:297EA7,LINE:297EA8,LINE:297EA9,LINE:297EAA,LINE:297EAB,LINE:297EAC,LINE:297EAD,LINE:297EAE,LINE:297EAF,LINE:297EB0,LINE:297EB1,LINE:297EB2,LINE:297EB3,LINE:297EB4,LINE:297EB5,LINE:297EB6,LINE:297EB7,LINE:297EB8,LINE:297EB9,LINE:297EBA,LINE:297EBB,LINE:297EBC,LINE:297EBD,LINE:297EBE,LINE:297EBF,LINE:297EC0,LINE:297EC1,LINE:297EC2,LINE:297EC3,LINE:297EC4,LINE:297EC5,LINE:297EC6,LINE:297EC7,LINE:297EC8,LINE:297EC9,LINE:297ECA,LINE:297ECB,LINE:297ECC,LINE:297ECD,LINE:297ECE,LINE:297ECF,LINE:297ED0,LINE:297ED1,LINE:297ED2,LINE:297ED3,LINE:297ED4,LINE:297ED5,LINE:297ED6,LINE:297ED7,LINE:297ED8,LINE:297ED9,LINE:297EDA,LINE:297EDB,LINE:297EDC,LINE:297EDD,LINE:297EDE,LINE:297EDF,LINE:297EE0,LINE:297EE1,LINE:297EE2,LINE:297EE3,LINE:297EE4,LINE:297EE5,LINE:297EE6,LINE:297EE7,LINE:297EE8,LINE:297EE9,LINE:297EEA,LINE:297EEB,LINE:297EEC,LINE:297EED,LINE:297EEE,LINE:297EEF,LINE:297EF0,LINE:297EF1,LINE:297EF2,LINE:297EF3,LINE:297EF4,LINE:297EF5,LINE:297EF6,LINE:297EF7,LINE:297EF8,LINE:297EF9,LINE:297EFA,LINE:297EFB,LINE:297EFC,LINE:297EFD,LINE:297EFE,LINE:297EFF,LINE:297F00,LINE:297F01,LINE:297F02,LINE:297F03,LINE:297F04,LINE:297F05,LINE:297F06,LINE:297F07,LINE:297F08,LINE:297F09,LINE:297F0A,LINE:297F0B,LINE:297F0C,LINE:297F0D,LINE:297F0E,LINE:297F0F,LINE:297F10,LINE:297F11,LINE:297F12,LINE:297F13,LINE:297F14,LINE:297F15,LINE:297F16,LINE:297F17,LINE:297F18,LINE:297F19,LINE:297F1A,LINE:297F1B,LINE:297F1C,LINE:297F1D,LINE:297F1E,LINE:297F1F,LINE:297F20,LINE:297F21,LINE:297F22,LINE:297F23,LINE:297F24,LINE:297F25,LINE:297F26,LINE:297F27,LINE:297F28,LINE:297F29,LINE:297F2A,LINE:297F2B,LINE:297F2C,LINE:297F2D,LINE:297F2E,LINE:297F2F,LINE:297F30,LINE:297F31,LINE:297F32,LINE:297F33,LINE:297F34,LINE:297F35,LINE:297F36,LINE:297F37,LINE:297F38,LINE:297F39,LINE:297F3A,LINE:297F3B,LINE:297F3C,LINE:297F3D,LINE:297F3E,LINE:297F3F,LINE:297F40,LINE:297F41,LINE:297F42,LINE:297F43,LINE:297F44,LINE:297F45,LINE:297F46,LINE:297F47,LINE:297F48,LINE:297F49,LINE:297F4A,LINE:297F4B,LINE:297F4C,LINE:297F4D,LINE:297F4E,LINE:297F4F,LINE:297F50,LINE:297F51,LINE:297F52,LINE:297F53,LINE:297F54,LINE:297F55,LINE:297F56,LINE:297F57,LINE:297F58,LINE:297F59,LINE:297F5A,LINE:297F5B,LINE:297F5C,LINE:297F5D,LINE:297F5E,LINE:297F5F,LINE:297F60,LINE:297F61,LINE:297F62,LINE:297F63,LINE:297F64,LINE:297F65,LINE:297F66,LINE:297F67,LINE:297F68,LINE:297F69,LINE:297F6A,LINE:297F6B,LINE:297F6C,LINE:297F6D,LINE:297F6E,LINE:297F6F,LINE:297F70,LINE:297F71,LINE:297F72,LINE:297F73,LINE:297F74,LINE:297F75,LINE:297F76,LINE:297F77,LINE:297F78,LINE:297F79,LINE:297F7A,LINE:297F7B,LINE:297F7C,LINE:297F7D,LINE:297F7E,LINE:297F7F,LINE:297F80,LINE:297F81,LINE:297F82,LINE:297F83,LINE:297F84,LINE:297F85,LINE:297F86,LINE:297F87,LINE:297F88,LINE:297F89,LINE:297F8A,LINE:297F8B,LINE:297F8C,LINE:297F8D,LINE:297F8E,LINE:297F8F,LINE:297F90,LINE:297F91,LINE:297F92,LINE:297F93,LINE:297F94,LINE:297F95,LINE:297F96,LINE:297F97,LINE:297F98,LINE:297F99,LINE:297F9A,LINE:297F9B,LINE:297F9C,LINE:297F9D,LINE:297F9E,LINE:297F9F,LINE:297FA0,LINE:297FA1,LINE:297FA2,LINE:297FA3,LINE:297FA4,LINE:297FA5,LINE:297FA6,LINE:297FA7,LINE:297FA8,LINE:297FA9,LINE:297FAA,LINE:297FAB,LINE:297FAC,LINE:297FAD,LINE:297FAE,LINE:297FAF,LINE:297FB0,LINE:297FB1,LINE:297FB2,LINE:297FB3,LINE:297FB4,LINE:297FB5,LINE:297FB6,LINE:297FB7,LINE:297FB8,LINE:297FB9,LINE:297FBA,LINE:297FBB,LINE:297FBC,LINE:297FBD,LINE:297FBE,LINE:297FBF,LINE:297FC0,LINE:297FC1,LINE:297FC2,LINE:297FC3,LINE:297FC4,LINE:297FC5,LINE:297FC6,LINE:297FC7,LINE:297FC8,LINE:297FC9,LINE:297FCA,LINE:297FCB,LINE:297FCC,LINE:297FCD,LINE:297FCE,LINE:297FCF,LINE:297FD0,LINE:297FD1,LINE:297FD2,LINE:297FD3,LINE:297FD4,LINE:297FD5,LINE:297FD6,LINE:297FD7,LINE:297FD8,LINE:297FD9,LINE:297FDA,LINE:297FDB,LINE:297FDC,LINE:297FDD,LINE:297FDE,LINE:297FDF,LINE:297FE0,LINE:297FE1,LINE:297FE2,LINE:297FE3,LINE:297FE4,LINE:297FE5,LINE:297FE6,LINE:297FE7,LINE:297FE8,LINE:297FE9,LINE:297FEA,LINE:297FEB,LINE:297FEC,LINE:297FED,LINE:297FEE,LINE:297FEF,LINE:297FF0,LINE:297FF1,LINE:297FF2,LINE:297FF3,LINE:297FF4,LINE:297FF5,LINE:297FF6,LINE:297FF7,LINE:297FF8,LINE:297FF9,LINE:297FFA,LINE:297FFB,LINE:297FFC,LINE:297FFD,LINE:297FFE,LINE:297FFF,LINE:29800A,LINE:29800B,LINE:29800C,LINE:29800D,LINE:29800E,LINE:29800F,LINE:29801A,LINE:29801B,LINE:29801C,LINE:29801D,LINE:29801E,LINE:29801F,LINE:29802A,LINE:29802B,LINE:29802C,LINE:29802D,LINE:29802E,LINE:29802F,LINE:29803A,LINE:29803B,LINE:29803C,LINE:29803D,LINE:29803E,LINE:29803F,LINE:29804A,LINE:29804B,LINE:29804C,LINE:29804D,LINE:29804E,LINE:29804F,LINE:29805A,LINE:29805B,LINE:29805C,LINE:29805D,LINE:29805E,LINE:29805F,LINE:29806A,LINE:29806B,LINE:29806C,LINE:29806D,LINE:29806E,LINE:29806F,LINE:29807A,LINE:29807B,LINE:29807C,LINE:29807D,LINE:29807E,LINE:29807F,LINE:29808A,LINE:29808B,LINE:29808C,LINE:29808D,LINE:29808E,LINE:29808F,LINE:29809A,LINE:29809B,LINE:29809C,LINE:29809D,LINE:29809E,LINE:29809F,LINE:2980A0,LINE:2980A1,LINE:2980A2,LINE:2980A3,LINE:2980A4,LINE:2980A5,LINE:2980A6,LINE:2980A7,LINE:2980A8,LINE:2980A9,LINE:2980AA,LINE:2980AB,LINE:2980AC,LINE:2980AD,LINE:2980AE,LINE:2980AF,LINE:2980B0,LINE:2980B1,LINE:2980B2,LINE:2980B3,LINE:2980B4,LINE:2980B5,LINE:2980B6,LINE:2980B7,LINE:2980B8,LINE:2980B9,LINE:2980BA,LINE:2980BB,LINE:2980BC,LINE:2980BD,LINE:2980BE,LINE:2980BF,LINE:2980C0,LINE:2980C1,LINE:2980C2,LINE:2980C3,LINE:2980C4,LINE:2980C5,LINE:2980C6,LINE:2980C7,LINE:2980C8,LINE:2980C9,LINE:2980CA,LINE:2980CB,LINE:2980CC,LINE:2980CD,LINE:2980CE,LINE:2980CF,LINE:2980D0,LINE:2980D1,LINE:2980D2,LINE:2980D3,LINE:2980D4,LINE:2980D5,LINE:2980D6,LINE:2980D7,LINE:2980D8,LINE:2980D9,LINE:2980DA,LINE:2980DB,LINE:2980DC,LINE:2980DD,LINE:2980DE,LINE:2980DF,LINE:2980E0,LINE:2980E1,LINE:2980E2,LINE:2980E3,LINE:2980E4,LINE:2980E5,LINE:2980E6,LINE:2980E7,LINE:2980E8,LINE:2980E9,LINE:2980EA,LINE:2980EB,LINE:2980EC,LINE:2980ED,LINE:2980EE,LINE:2980EF,LINE:2980F0,LINE:2980F1,LINE:2980F2,LINE:2980F3,LINE:2980F4,LINE:2980F5,LINE:2980F6,LINE:2980F7,LINE:2980F8,LINE:2980F9,LINE:2980FA,LINE:2980FB,LINE:2980FC,LINE:2980FD,LINE:2980FE,LINE:2980FF,LINE:29810A,LINE:29810B,LINE:29810C,LINE:29810D,LINE:29810E,LINE:29810F,LINE:29811A,LINE:29811B,LINE:29811C,LINE:29811D,LINE:29811E,LINE:29811F,LINE:29812C,LINE:29812D,LINE:29812E,LINE:29812F,LINE:29813A,LINE:29813B,LINE:29813C,LINE:29813D,LINE:29813E,LINE:29813F,LINE:29814A,LINE:29814B,LINE:29814C,LINE:29814D,LINE:29814E,LINE:29814F,LINE:29815A,LINE:29815B,LINE:29815C,LINE:29815D,LINE:29815E,LINE:29815F,LINE:29816A,LINE:29816B,LINE:29816C,LINE:29816D,LINE:29816E,LINE:29816F,LINE:29817A,LINE:29817B,LINE:29817C,LINE:29817D,LINE:29817E,LINE:29817F,LINE:29818A,LINE:29818B,LINE:29818C,LINE:29818D,LINE:29818E,LINE:29818F,LINE:29819A,LINE:29819B inferred 0.60; +1 more | yes | 25 % of its pixels > 0.10 m outside the drawing, 316532 px |
| cam_r_L1_soyunma_odasi_1 | cycles | cross-check misplaced | d_L1_003 | door | - | from_documents | real06.dwg ARC:2982A7,LINE:2982A9,LINE:2982AD,LINE:2982CD,LINE:2982CE,LINE:29ABA0,LINE:2982CF,LINE:29ABA1,CIRCLE:29829F,CIRCLE:2982A0,LINE:2982A1,LINE:29829E,ARC:29ABA2,LINE:29ABA3,LINE:2982A5,LINE:2982A4,LINE:2982A3 vector 0.95 | yes | 12 % of its pixels > 0.10 m outside the drawing, 409950 px |

## Needs review

- cam_r_L0_mutfak_2: json cross-check in_json_not_rendered: o_L0_001
- cam_r_L1_cocuk_odasi_1: json cross-check misplaced: d_L1_008
- cam_r_L1_cocuk_odasi_2: json cross-check misplaced: f_L1_007
- cam_r_L1_ebeveyn_y_odasi_1: json cross-check misplaced: d_L1_002; json cross-check misplaced: f_L1_010
- cam_r_L1_ebeveyn_y_odasi_2: json cross-check misplaced: d_L1_002; json cross-check misplaced: d_L1_008; json cross-check misplaced: win_L1_003
- cam_r_L1_ebeveyn_y_odasi_3: json cross-check misplaced: d_L1_002
- cam_r_L1_oda_1: json cross-check misplaced: d_L1_002
- cam_r_L1_oda_2_2: json cross-check misplaced: f_L1_013
- cam_r_L1_soyunma_odasi_1: json cross-check misplaced: d_L1_003

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- o_L0_001
- o_L0_002
- o_L0_003
- o_L0_004
- o_L0_005
- o_L0_006
- o_L0_007
- o_L1_001
- o_L1_002
- o_L1_003
- o_L1_004
- o_L1_005
- o_L1_006
- o_L1_007
- r_L0_salon
- r_L0_mutfak
- r_L0_oda
- r_L1_oda
- r_L1_dus
- f_L0_001
- f_L0_004
- f_L0_005
- f_L0_006
- f_L0_009
- f_L0_010
- f_L0_011
- f_L0_012
- f_L0_013
- f_L0_014
- f_L0_015
- f_L0_020
- f_L0_027
- f_L0_028
- f_L0_029
- f_L0_030
- f_L1_002
- f_L1_003
- f_L1_005
- f_L1_006
- f_L1_009
- f_L1_010
- f_L1_011
- f_L1_012
- f_L1_013
- f_L1_014
- f_L1_017
- f_L1_020
- f_L1_024
- f_L1_025
- f_L1_026
- f_L1_027
- f_L0_031
- f_L0_032

Unverified pieces in view:

- cam_r_L0_banyo_1: f_L0_010
- cam_r_L0_mutfak_1: f_L0_031, f_L0_032, o_L0_004
- cam_r_L0_mutfak_2: f_L0_001, f_L0_031, o_L0_004
- cam_r_L0_mutfak_3: f_L0_031, f_L0_032, o_L0_004
- cam_r_L0_salon_1: f_L0_006, f_L0_014
- cam_r_L0_salon_2: f_L0_006, f_L0_014, o_L0_005
- cam_r_L0_salon_3: f_L0_006, f_L0_011, f_L0_014, f_L0_027, f_L0_028, f_L0_029, f_L0_030, o_L0_003, o_L0_005
- cam_r_L1_banyo_1: f_L1_009, o_L1_004
- cam_r_L1_banyo_2: f_L0_001, f_L1_009, o_L1_004
- cam_r_L1_cocuk_odasi_1: f_L1_005
- cam_r_L1_cocuk_odasi_2: f_L1_005
- cam_r_L1_cocuk_odasi_3: f_L1_005
- cam_r_L1_ebeveyn_y_odasi_1: f_L1_010, f_L1_020, f_L1_024
- cam_r_L1_ebeveyn_y_odasi_2: f_L1_010, f_L1_011, f_L1_024, f_L1_026
- cam_r_L1_ebeveyn_y_odasi_3: f_L1_010, f_L1_024, f_L1_026
- cam_r_L1_oda_1: f_L1_010, f_L1_024
- cam_r_L1_oda_2_1: f_L1_013, f_L1_014, f_L1_025, o_L1_003
- cam_r_L1_oda_2_2: f_L1_013, f_L1_014, f_L1_025, o_L1_003, o_L1_005
- cam_r_L1_soyunma_odasi_1: f_L1_011
- cam_r_L1_soyunma_odasi_2: f_L1_011, f_L1_012, o_L1_006
- ext_1: o_L0_005, o_L0_006, o_L0_007, o_L1_006, o_L1_007
- ext_2: o_L0_002, o_L0_005, o_L0_006, o_L0_007, o_L1_003, o_L1_004, o_L1_007
- ext_3: o_L0_002, o_L0_003, o_L0_004, o_L1_003, o_L1_004, o_L1_005
- ext_4: o_L0_003
- ext_5: o_L0_002, o_L0_003, o_L0_004, o_L1_003, o_L1_004, o_L1_005

Drawn pieces left for review (untyped, not built; docs/milestone12.md §4.1):

| id | kind | room | reason | crop |
|---|---|---|---|---|
| f_L1_002 | untyped_piece | r_L1_cocuk_odasi | drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi has no type; cluster larger than 4.5 m on a side: a group of drawn pieces, not built: not built | - |
| TEXT:29AC25 | named_piece | r_L1_ebeveyn_y_odasi | the documents name a dresser ('*SIFONIYER' (TEXT:29AC25)) at (8.11, 4.91) m on L1 and no drawn dresser stands there: not added: the nearest place that passes every check in r_L1_ebeveyn_y_odasi is 1.47 m from the text (more than 1 m) | - |

Drawn symbols read as not furniture (never built): door_arc 1, level_mark 2.

Library models kept with a vision doubt (user decision 1a; the room critic and the final check look at them):

| piece | kind | type | model | doubt |
|---|---|---|---|---|
| f_L0_016 | furniture | armchair | 3dwh_d1ed36390489612fbb2a5baa | the vision check sees more than one object |
| f_L1_007 | furniture | bed_double | hssd_02e22ed56270338bef5f8436e82023c36cd29104 | the vision check sees more than one object |

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L0_salon | Label says 39,15 m², polygon gives 55,58 m² (42.0%) | over 8%: room marked unverified, polygon from real06.dwg kept |
| c_002 | area_label_vs_computed | r_L0_mutfak | Label says 12,00 m², polygon gives 24,81 m² minus the stair 4,62 m² = 20,19 m² (68.3%) | over 8%: room marked unverified, polygon from real06.dwg kept |
| c_003 | area_label_vs_computed | r_L0_banyo | Label says 7,25 m², polygon gives 6,67 m² (8.0%) | within tolerance (8%), kept polygon from real06.dwg |
| c_004 | area_label_vs_computed | r_L1_ebeveyn_y_odasi | Label says 23,90 m², polygon gives 23,32 m² (2.4%) | within tolerance (8%), kept polygon from real06.dwg |
| c_005 | area_label_vs_computed | r_L1_cocuk_odasi | Label says 23,10 m², polygon gives 22,39 m² (3.1%) | within tolerance (8%), kept polygon from real06.dwg |
| c_006 | area_label_vs_computed | r_L1_soyunma_odasi | Label says 6,25 m², polygon gives 5,88 m² (5.9%) | within tolerance (8%), kept polygon from real06.dwg |
| c_007 | area_label_vs_computed | r_L1_dus | Label says 5,00 m², polygon gives 4,53 m² (9.4%) | over 8%: room marked unverified, polygon from real06.dwg kept |
| c_008 | area_label_vs_computed | r_L1_oda_2 | Label says 12,00 m², polygon gives 11,34 m² (5.5%) | within tolerance (8%), kept polygon from real06.dwg |
| c_009 | area_label_vs_computed | r_L1_banyo | Label says 7,25 m², polygon gives 6,67 m² (8.0%) | within tolerance (8%), kept polygon from real06.dwg |
| c_010 | dimension_vs_measured | L0 | real06.dwg: dimension text 1 vs measured 0.70 m (42.9%) | kept measured geometry (DWG) |
| c_011 | dimension_vs_measured | L0 | real06.dwg: dimension text 1 vs measured 0.50 m (100.0%) | kept measured geometry (DWG) |
| c_012 | dimension_vs_measured | L0 | real06.dwg: dimension text 3 vs measured 1.40 m (114.3%) | kept measured geometry (DWG) |
| c_013 | dimension_vs_measured | w_L0_012 | real06.dwg: dimension text 2 vs measured 1.00 m (100.0%) | kept measured geometry (DWG) |
| c_014 | dimension_vs_measured | w_L0_021, w_L0_012 | real06.dwg: dimension text 3 vs measured 1.00 m (200.0%) | kept measured geometry (DWG) |
| c_015 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 4 vs measured 1.00 m (300.0%) | kept measured geometry (DWG) |
| c_016 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 5 vs measured 1.00 m (400.0%) | kept measured geometry (DWG) |
| c_017 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 6 vs measured 1.00 m (500.0%) | kept measured geometry (DWG) |
| c_018 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 7 vs measured 1.00 m (600.0%) | kept measured geometry (DWG) |
| c_019 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 8 vs measured 1.00 m (700.0%) | kept measured geometry (DWG) |
| c_020 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 9 vs measured 1.00 m (800.0%) | kept measured geometry (DWG) |
| c_021 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 10 vs measured 1.00 m (900.0%) | kept measured geometry (DWG) |
| c_022 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 11 vs measured 1.00 m (1000.0%) | kept measured geometry (DWG) |
| c_023 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 12 vs measured 0.48 m (2390.1%) | kept measured geometry (DWG) |
| c_024 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 13 vs measured 1.00 m (1200.0%) | kept measured geometry (DWG) |
| c_025 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 14 vs measured 1.00 m (1300.0%) | kept measured geometry (DWG) |
| c_026 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 15 vs measured 1.00 m (1400.0%) | kept measured geometry (DWG) |
| c_027 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 16 vs measured 1.00 m (1500.0%) | kept measured geometry (DWG) |
| c_028 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 17 vs measured 1.00 m (1600.0%) | kept measured geometry (DWG) |
| c_029 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 18 vs measured 0.58 m (3012.0%) | kept measured geometry (DWG) |
| c_030 | dimension_vs_measured | L0 | real06.dwg: dimension text 7,20 vs measured 6.60 m (9.1%) | kept measured geometry (DWG) |
| c_031 | dimension_vs_measured | w_L0_019 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_032 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 70 vs measured 0.70 m (9900.0%) | kept measured geometry (DWG) |
| c_033 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 70 vs measured 1.15 m (5987.0%) | kept measured geometry (DWG) |
| c_034 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 70 vs measured 0.70 m (9900.0%) | kept measured geometry (DWG) |
| c_035 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_036 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 35 vs measured 0.19 m (18321.1%) | kept measured geometry (DWG) |
| c_037 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 50 vs measured 0.50 m (9916.0%) | kept measured geometry (DWG) |
| c_038 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 155 vs measured 1.55 m (9894.8%) | kept measured geometry (DWG) |
| c_039 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.24 m (10104.1%) | kept measured geometry (DWG) |
| c_040 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_041 | dimension_vs_measured | L0 | real06.dwg: dimension text 295 vs measured 2.95 m (9900.0%) | kept measured geometry (DWG) |
| c_042 | dimension_vs_measured | w_L0_019 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_043 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_044 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_045 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_046 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_047 | dimension_vs_measured | L0 | real06.dwg: dimension text 245 vs measured 2.45 m (9900.0%) | kept measured geometry (DWG) |
| c_048 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_049 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_050 | dimension_vs_measured | L0 | real06.dwg: dimension text 155 vs measured 1.55 m (9900.0%) | kept measured geometry (DWG) |
| c_051 | dimension_vs_measured | w_L0_015 | real06.dwg: dimension text 80 vs measured 0.80 m (9903.8%) | kept measured geometry (DWG) |
| c_052 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 10 vs measured 0.10 m (9870.1%) | kept measured geometry (DWG) |
| c_053 | dimension_vs_measured | w_L0_020 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_054 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.03 m (70322.5%) | kept measured geometry (DWG) |
| c_055 | dimension_vs_measured | w_L0_014 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_056 | dimension_vs_measured | L0 | real06.dwg: dimension text 140 vs measured 1.40 m (9900.0%) | kept measured geometry (DWG) |
| c_057 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_058 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_059 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_060 | dimension_vs_measured | L0 | real06.dwg: dimension text 85 vs measured 0.85 m (9909.4%) | kept measured geometry (DWG) |
| c_061 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 200 vs measured 2.00 m (9896.0%) | kept measured geometry (DWG) |
| c_062 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_063 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_064 | dimension_vs_measured | L0 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_065 | dimension_vs_measured | w_L0_012 | real06.dwg: dimension text 200 vs measured 1.84 m (10764.3%) | kept measured geometry (DWG) |
| c_066 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 180 vs measured 1.07 m (16666.0%) | kept measured geometry (DWG) |
| c_067 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_068 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_069 | dimension_vs_measured | L0 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_070 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_071 | dimension_vs_measured | L0 | real06.dwg: dimension text 480 vs measured 2.46 m (19441.6%) | kept measured geometry (DWG) |
| c_072 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_073 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 25 vs measured 0.24 m (10209.3%) | kept measured geometry (DWG) |
| c_074 | dimension_vs_measured | w_L0_004 | real06.dwg: dimension text 5 vs measured 0.05 m (9900.0%) | kept measured geometry (DWG) |
| c_075 | dimension_vs_measured | w_L0_004 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_076 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 95 vs measured 0.95 m (9900.0%) | kept measured geometry (DWG) |
| c_077 | dimension_vs_measured | L0 | real06.dwg: dimension text 385 vs measured 3.85 m (9900.0%) | kept measured geometry (DWG) |
| c_078 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.03 m (58551.0%) | kept measured geometry (DWG) |
| c_079 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_080 | dimension_vs_measured | L0 | real06.dwg: dimension text 465 vs measured 4.65 m (9900.0%) | kept measured geometry (DWG) |
| c_081 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_082 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 385 vs measured 0.46 m (83723.2%) | kept measured geometry (DWG) |
| c_083 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.94 m (2025.6%) | kept measured geometry (DWG) |
| c_084 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_085 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 65 vs measured 0.65 m (9901.5%) | kept measured geometry (DWG) |
| c_086 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 220 vs measured 0.82 m (26696.6%) | kept measured geometry (DWG) |
| c_087 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 95 vs measured 0.95 m (9900.0%) | kept measured geometry (DWG) |
| c_088 | dimension_vs_measured | L0 | real06.dwg: dimension text 25 vs measured 0.24 m (10116.6%) | kept measured geometry (DWG) |
| c_089 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_090 | dimension_vs_measured | L0 | real06.dwg: dimension text 465 vs measured 4.65 m (9900.0%) | kept measured geometry (DWG) |
| c_091 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_092 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 25 vs measured 0.28 m (8990.9%) | kept measured geometry (DWG) |
| c_093 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 150 vs measured 0.83 m (17985.4%) | kept measured geometry (DWG) |
| c_094 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 125 vs measured 1.25 m (9900.0%) | kept measured geometry (DWG) |
| c_095 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_096 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 125 vs measured 1.25 m (9898.4%) | kept measured geometry (DWG) |
| c_097 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 220 vs measured 2.20 m (9900.9%) | kept measured geometry (DWG) |
| c_098 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_099 | dimension_vs_measured | w_L0_023 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_100 | dimension_vs_measured | L0 | real06.dwg: dimension text 490 vs measured 4.90 m (9900.0%) | kept measured geometry (DWG) |
| c_101 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_102 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_103 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 400 vs measured 4.00 m (9900.0%) | kept measured geometry (DWG) |
| c_104 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_105 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 560 vs measured 5.60 m (9900.0%) | kept measured geometry (DWG) |
| c_106 | dimension_vs_measured | w_L0_023 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_107 | dimension_vs_measured | w_L0_025 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_108 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 100 vs measured 2.50 m (3900.0%) | kept measured geometry (DWG) |
| c_109 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_110 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_111 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_112 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 80 vs measured 0.80 m (9900.0%) | kept measured geometry (DWG) |
| c_113 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 370 vs measured 3.70 m (9899.2%) | kept measured geometry (DWG) |
| c_114 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 110 vs measured 1.10 m (9902.7%) | kept measured geometry (DWG) |
| c_115 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_116 | dimension_vs_measured | L0 | real06.dwg: dimension text 490 vs measured 4.90 m (9900.0%) | kept measured geometry (DWG) |
| c_117 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_118 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 20 vs measured 0.05 m (37707.2%) | kept measured geometry (DWG) |
| c_119 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 300 vs measured 3.00 m (9900.0%) | kept measured geometry (DWG) |
| c_120 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_121 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_122 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 570 vs measured 5.70 m (9900.0%) | kept measured geometry (DWG) |
| c_123 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 215 vs measured 2.15 m (9900.9%) | kept measured geometry (DWG) |
| c_124 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 80 vs measured 0.80 m (9897.5%) | kept measured geometry (DWG) |
| c_125 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 15 vs measured 0.15 m (9900.0%) | kept measured geometry (DWG) |
| c_126 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_127 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 20 vs measured 0.41 m (4755.5%) | kept measured geometry (DWG) |
| c_128 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 290 vs measured 2.90 m (9900.0%) | kept measured geometry (DWG) |
| c_129 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_130 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_131 | dimension_vs_measured | w_L0_033 | real06.dwg: dimension text 100 vs measured 1.00 m (9857.2%) | kept measured geometry (DWG) |
| c_132 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (10349.3%) | kept measured geometry (DWG) |
| c_133 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_134 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 880 vs measured 5.83 m (14987.1%) | kept measured geometry (DWG) |
| c_135 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9915.0%) | kept measured geometry (DWG) |
| c_136 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_137 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_138 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_139 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 360 vs measured 1.07 m (33633.1%) | kept measured geometry (DWG) |
| c_140 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.60 m (9896.3%) | kept measured geometry (DWG) |
| c_141 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 80 vs measured 0.47 m (17008.6%) | kept measured geometry (DWG) |
| c_142 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.47 m (10754.8%) | kept measured geometry (DWG) |
| c_143 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 110 vs measured 1.10 m (9876.4%) | kept measured geometry (DWG) |
| c_144 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_145 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 330 vs measured 3.30 m (9900.0%) | kept measured geometry (DWG) |
| c_146 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 80 vs measured 0.80 m (9900.0%) | kept measured geometry (DWG) |
| c_147 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_148 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_149 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 360 vs measured 3.60 m (9900.0%) | kept measured geometry (DWG) |
| c_150 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_151 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.60 m (9900.0%) | kept measured geometry (DWG) |
| c_152 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_153 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 40 vs measured 0.40 m (9900.0%) | kept measured geometry (DWG) |
| c_154 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_155 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 160 vs measured 1.60 m (9900.0%) | kept measured geometry (DWG) |
| c_156 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_157 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 110 vs measured 1.10 m (9900.0%) | kept measured geometry (DWG) |
| c_158 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_159 | dimension_vs_measured | L0 | real06.dwg: dimension text 180 vs measured 1.80 m (9900.0%) | kept measured geometry (DWG) |
| c_160 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_161 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 910 vs measured 9.10 m (9900.0%) | kept measured geometry (DWG) |
| c_162 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_163 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 330 vs measured 3.30 m (9900.0%) | kept measured geometry (DWG) |
| c_164 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_165 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 125 vs measured 1.25 m (9900.0%) | kept measured geometry (DWG) |
| c_166 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_167 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 150 vs measured 1.50 m (9900.0%) | kept measured geometry (DWG) |
| c_168 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_169 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 235 vs measured 2.35 m (9900.0%) | kept measured geometry (DWG) |
| c_170 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_171 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 220 vs measured 2.20 m (9900.0%) | kept measured geometry (DWG) |
| c_172 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_173 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_174 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 195 vs measured 1.95 m (9900.0%) | kept measured geometry (DWG) |
| c_175 | dimension_vs_measured | w_L0_029 | real06.dwg: dimension text 80 vs measured 0.80 m (9900.0%) | kept measured geometry (DWG) |
| c_176 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 35 vs measured 0.35 m (9900.0%) | kept measured geometry (DWG) |
| c_177 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_178 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_179 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 1020 vs measured 10.20 m (9900.0%) | kept measured geometry (DWG) |
| c_180 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_181 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_182 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_183 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_184 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_185 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 260 vs measured 2.60 m (9900.0%) | kept measured geometry (DWG) |
| c_186 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 320 vs measured 3.20 m (9900.0%) | kept measured geometry (DWG) |
| c_187 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_188 | dimension_vs_measured | L0 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_189 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_190 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_191 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 1430 vs measured 14.30 m (9900.0%) | kept measured geometry (DWG) |
| c_192 | dimension_vs_measured | w_L0_025 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_193 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_194 | dimension_vs_measured | w_L0_032 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_195 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 210 vs measured 2.10 m (9900.0%) | kept measured geometry (DWG) |
| c_196 | dimension_vs_measured | w_L0_022 | real06.dwg: dimension text 260 vs measured 2.60 m (9900.0%) | kept measured geometry (DWG) |
| c_197 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 320 vs measured 3.20 m (9900.0%) | kept measured geometry (DWG) |
| c_198 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 310 vs measured 3.10 m (9900.0%) | kept measured geometry (DWG) |
| c_199 | dimension_vs_measured | w_L0_038 | real06.dwg: dimension text 1430 vs measured 14.30 m (9900.0%) | kept measured geometry (DWG) |
| c_200 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_201 | dimension_vs_measured | L0 | real06.dwg: dimension text 315 vs measured 3.15 m (9900.0%) | kept measured geometry (DWG) |
| c_202 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 95 vs measured 0.95 m (9900.0%) | kept measured geometry (DWG) |
| c_203 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 70 vs measured 0.70 m (9900.0%) | kept measured geometry (DWG) |
| c_204 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 130 vs measured 1.30 m (9900.0%) | kept measured geometry (DWG) |
| c_205 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 50 vs measured 0.50 m (9900.0%) | kept measured geometry (DWG) |
| c_206 | dimension_vs_measured | L0 | real06.dwg: dimension text 180 vs measured 1.80 m (9900.0%) | kept measured geometry (DWG) |
| c_207 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_208 | dimension_vs_measured | L0 | real06.dwg: dimension text 315 vs measured 3.15 m (9900.0%) | kept measured geometry (DWG) |
| c_209 | dimension_vs_measured | L0 | real06.dwg: dimension text 525 vs measured 5.25 m (9900.0%) | kept measured geometry (DWG) |
| c_210 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.30 m (3233.3%) | kept measured geometry (DWG) |
| c_211 | dimension_vs_measured | L0 | real06.dwg: dimension text 165 vs measured 1.65 m (9900.0%) | kept measured geometry (DWG) |
| c_212 | dimension_vs_measured | w_L0_019 | real06.dwg: dimension text 150 vs measured 1.50 m (9900.0%) | kept measured geometry (DWG) |
| c_213 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_214 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_215 | dimension_vs_measured | w_L0_021 | real06.dwg: dimension text 140 vs measured 1.40 m (9900.0%) | kept measured geometry (DWG) |
| c_216 | dimension_vs_measured | L0 | real06.dwg: dimension text 265 vs measured 2.65 m (9900.0%) | kept measured geometry (DWG) |
| c_217 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_218 | dimension_vs_measured | L0 | real06.dwg: dimension text 840 vs measured 8.40 m (9900.0%) | kept measured geometry (DWG) |
| c_219 | dimension_vs_measured | L0 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_220 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_221 | dimension_vs_measured | w_L0_018 | real06.dwg: dimension text 25 vs measured 0.25 m (9900.0%) | kept measured geometry (DWG) |
| c_222 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 300 vs measured 3.00 m (9900.0%) | kept measured geometry (DWG) |
| c_223 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_224 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 65 vs measured 0.65 m (9900.0%) | kept measured geometry (DWG) |
| c_225 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_226 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 220 vs measured 2.20 m (9900.0%) | kept measured geometry (DWG) |
| c_227 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_228 | dimension_vs_measured | L0 | real06.dwg: dimension text 100 vs measured 1.00 m (9900.0%) | kept measured geometry (DWG) |
| c_229 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_230 | dimension_vs_measured | L0 | real06.dwg: dimension text 120 vs measured 1.20 m (9900.0%) | kept measured geometry (DWG) |
| c_231 | dimension_vs_measured | L0 | real06.dwg: dimension text 415 vs measured 4.15 m (9900.0%) | kept measured geometry (DWG) |
| c_232 | dimension_vs_measured | L0 | real06.dwg: dimension text 425 vs measured 4.25 m (9900.0%) | kept measured geometry (DWG) |
| c_233 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.30 m (3233.3%) | kept measured geometry (DWG) |
| c_234 | dimension_vs_measured | L0 | real06.dwg: dimension text 165 vs measured 1.65 m (9900.0%) | kept measured geometry (DWG) |
| c_235 | dimension_vs_measured | w_L0_004 | real06.dwg: dimension text 150 vs measured 1.50 m (9900.0%) | kept measured geometry (DWG) |
| c_236 | dimension_vs_measured | w_L0_009 | real06.dwg: dimension text 90 vs measured 0.90 m (9900.0%) | kept measured geometry (DWG) |
| c_237 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_238 | dimension_vs_measured | w_L0_001 | real06.dwg: dimension text 140 vs measured 1.40 m (9900.0%) | kept measured geometry (DWG) |
| c_239 | dimension_vs_measured | L0 | real06.dwg: dimension text 265 vs measured 2.65 m (9900.0%) | kept measured geometry (DWG) |
| c_240 | dimension_vs_measured | L0 | real06.dwg: dimension text 10 vs measured 0.10 m (9900.0%) | kept measured geometry (DWG) |
| c_241 | dimension_vs_measured | L0 | real06.dwg: dimension text 840 vs measured 8.40 m (9900.0%) | kept measured geometry (DWG) |
| c_242 | dimension_vs_measured | L0 | real06.dwg: dimension text 180 vs measured 1.80 m (9900.0%) | kept measured geometry (DWG) |
| c_243 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_244 | dimension_vs_measured | L0 | real06.dwg: dimension text 190 vs measured 1.90 m (9900.0%) | kept measured geometry (DWG) |
| c_245 | dimension_vs_measured | L0 | real06.dwg: dimension text 20 vs measured 0.20 m (9900.0%) | kept measured geometry (DWG) |
| c_246 | dimension_vs_measured | L0 | real06.dwg: dimension text 200 vs measured 2.00 m (9900.0%) | kept measured geometry (DWG) |
| c_247 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 6 vs measured 1.00 m (94.0%) | kept measured geometry (DWG) |
| c_248 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 7 vs measured 1.00 m (93.0%) | kept measured geometry (DWG) |
| c_249 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 8 vs measured 1.00 m (92.0%) | kept measured geometry (DWG) |
| c_250 | dimension_vs_measured | w_L1_021 | real06.dwg: dimension text 9 vs measured 1.00 m (91.0%) | kept measured geometry (DWG) |
| c_251 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 10 vs measured 1.00 m (90.0%) | kept measured geometry (DWG) |
| c_252 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 11 vs measured 1.00 m (89.0%) | kept measured geometry (DWG) |
| c_253 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 12 vs measured 0.48 m (75.1%) | kept measured geometry (DWG) |
| c_254 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 13 vs measured 1.00 m (87.0%) | kept measured geometry (DWG) |
| c_255 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 14 vs measured 1.00 m (86.0%) | kept measured geometry (DWG) |
| c_256 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 15 vs measured 1.00 m (85.0%) | kept measured geometry (DWG) |
| c_257 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 16 vs measured 1.00 m (84.0%) | kept measured geometry (DWG) |
| c_258 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 17 vs measured 1.00 m (83.0%) | kept measured geometry (DWG) |
| c_259 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 18 vs measured 0.85 m (78.8%) | kept measured geometry (DWG) |
| c_260 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 25 vs measured 0.20 m (24.3%) | kept measured geometry (DWG) |
| c_261 | dimension_vs_measured | w_L1_020 | real06.dwg: dimension text 30 vs measured 0.33 m (7.7%) | kept measured geometry (DWG) |
| c_262 | dimension_vs_measured | w_L1_020 | real06.dwg: dimension text 35 vs measured 0.15 m (133.3%) | kept measured geometry (DWG) |
| c_263 | dimension_vs_measured | w_L1_012 | real06.dwg: dimension text 20 vs measured 0.09 m (130.9%) | kept measured geometry (DWG) |
| c_264 | dimension_vs_measured | w_L1_038 | real06.dwg: dimension text 20 vs measured 0.41 m (51.5%) | kept measured geometry (DWG) |
| c_265 | dimension_vs_measured | L1 | real06.dwg: dimension text 25 vs measured 0.17 m (44.5%) | kept measured geometry (DWG) |
| c_266 | dimension_vs_measured | L1 | real06.dwg: dimension text 20 vs measured 0.05 m (300.0%) | kept measured geometry (DWG) |
| c_267 | dimension_vs_measured | w_L1_028 | real06.dwg: dimension text 275 vs measured 0.82 m (235.4%) | kept measured geometry (DWG) |
| c_268 | dimension_vs_measured | L1 | real06.dwg: dimension text 25 vs measured 0.23 m (11.1%) | kept measured geometry (DWG) |
| c_269 | dimension_vs_measured | w_L1_001 | real06.dwg: dimension text 95 vs measured 0.74 m (28.3%) | kept measured geometry (DWG) |
| c_270 | dimension_vs_measured | w_L1_001 | real06.dwg: dimension text 220 vs measured 1.27 m (72.8%) | kept measured geometry (DWG) |
| c_271 | dimension_vs_measured | w_L1_022 | real06.dwg: dimension text 190 vs measured 0.36 m (427.8%) | kept measured geometry (DWG) |
| c_272 | dimension_vs_measured | w_L1_022 | real06.dwg: dimension text 205 vs measured 0.36 m (469.4%) | kept measured geometry (DWG) |
| c_273 | dimension_vs_measured | w_L1_019 | real06.dwg: dimension text 20 vs measured 0.64 m (68.9%) | kept measured geometry (DWG) |
| c_274 | dimension_vs_measured | w_L1_004 | real06.dwg: dimension text 20 vs measured 0.03 m (604.2%) | kept measured geometry (DWG) |
| c_275 | dimension_vs_measured | w_L1_033 | real06.dwg: dimension text 25 vs measured 0.20 m (22.8%) | kept measured geometry (DWG) |
| c_276 | dimension_vs_measured | w_L1_033 | real06.dwg: dimension text 5 vs measured 0.29 m (82.8%) | kept measured geometry (DWG) |
| c_277 | dimension_vs_measured | w_L1_029 | real06.dwg: dimension text 460 vs measured 1.79 m (156.8%) | kept measured geometry (DWG) |
| c_278 | dimension_vs_measured | w_L1_032 | real06.dwg: dimension text 190 vs measured 1.40 m (35.7%) | kept measured geometry (DWG) |
| c_279 | dimension_vs_measured | L1 | real06.dwg: dimension text 15 vs measured 0.82 m (81.8%) | kept measured geometry (DWG) |
| c_280 | dimension_vs_measured | L1 | real06.dwg: dimension text 20 vs measured 0.33 m (38.5%) | kept measured geometry (DWG) |
| c_281 | dimension_vs_measured | L1 | real06.dwg: dimension text 20 vs measured 0.15 m (33.4%) | kept measured geometry (DWG) |
| c_282 | dimension_vs_measured | w_L1_038 | real06.dwg: dimension text 250 vs measured 2.22 m (12.7%) | kept measured geometry (DWG) |
| c_283 | dimension_vs_measured | w_L1_038 | real06.dwg: dimension text 110 vs measured 1.20 m (8.3%) | kept measured geometry (DWG) |
| c_284 | dimension_vs_measured | L1 | real06.dwg: dimension text 10 vs measured 0.30 m (66.7%) | kept measured geometry (DWG) |
| c_285 | dimension_vs_measured | L1 | real06.dwg: dimension text 10 vs measured 0.30 m (66.7%) | kept measured geometry (DWG) |
| c_286 | outline_mismatch | L0, L1 | Outer wall outline of Level 1 differs from Ground floor by up to 0.201 m (areas 105.78 / 105.77 m²) | unresolved: each level kept as drawn |
| c_287 | type_disagreement | sy_L0_002 | f_L0_023: the AI passes typed it wall_cabinet, the drawing shows a level_mark (drawn on the 'kot' layer(s): level_mark, not furniture) | moved to building.symbols (trust order: vector geometry > AI) |
| c_288 | symbol_type_disagreement | f_L0_006 | f_L0_006: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_289 | symbol_type_disagreement | f_L0_009 | f_L0_009: sym_L0_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_290 | symbol_type_disagreement | f_L0_010 | f_L0_010: sym_L0_005: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | typed bathtub by code (ai_member): bathtub: r_L0_banyo misses it (r_L0_banyo.bathroom_set (anchor f_L0_024) misses shower\|bathtub) and the AI passes named it (pass 1 (qwen)'s reason names bathtub; pass 2 (glm)'s reason names bathtub); the drawn 2.54 x 1.01 m is outside the b; inferred, listed in the report |
| c_291 | symbol_type_disagreement | f_L0_012 | f_L0_012: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_292 | symbol_type_disagreement | f_L0_013 | f_L0_013: sym_L0_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_293 | symbol_type_disagreement | f_L0_014 | f_L0_014: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_dining, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_294 | symbol_type_disagreement | f_L0_015 | f_L0_015: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) bookshelf | typed table_coffee by code (ai_member): table_coffee: r_L0_salon misses it (r_L0_salon.seating (anchor f_L0_006) misses table_coffee) and the AI passes named it (pass 1 (qwen) answered table_coffee; pass 1 (qwen)'s reason names table_coffee); plan crop recognition/crops/sym_L0_01; inferred, listed in the report |
| c_295 | symbol_type_disagreement | f_L0_019 | f_L0_019: sym_L0_014: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_296 | symbol_type_disagreement | f_L0_022 | f_L0_022: sym_L0_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) washbasin | unresolved: the drawn footprint is kept as unknown, unverified |
| c_297 | symbol_type_disagreement | f_L0_024 | f_L0_024: sym_L0_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) washbasin, pass 2 (zai-org/GLM-4.6V-Flash) toilet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_298 | symbol_type_disagreement | f_L0_025 | f_L0_025: sym_L0_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sink_kitchen, pass 2 (zai-org/GLM-4.6V-Flash) wall_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_299 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_022: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_300 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_023: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_301 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_024: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_302 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_025: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_303 | symbol_type_disagreement | f_L1_005 | f_L1_005: sym_L1_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) dresser, pass 2 (zai-org/GLM-4.6V-Flash) desk | typed dresser by code (name_text): dresser: the documents name it: the text '*SIFONIYER' (TEXT:29AC0C) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.56 m within 40%; inferred, listed in the report |
| c_304 | symbol_type_disagreement | f_L1_006 | f_L1_006: sym_L1_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) nightstand, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_305 | symbol_type_disagreement | f_L1_009 | f_L1_009: sym_L1_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | typed bathtub by code (ai_member): bathtub: r_L1_banyo misses it (r_L1_banyo.bathroom_set (anchor f_L1_022) misses shower\|bathtub) and the AI passes named it (pass 1 (qwen)'s reason names bathtub); the drawn 2.42 x 0.98 m is outside the bathtub's range: the drawn outline 2.4; inferred, listed in the report |
| c_306 | symbol_type_disagreement | f_L1_011 | f_L1_011: sym_L1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) stair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_307 | symbol_type_disagreement | f_L1_012 | f_L1_012: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) stair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_308 | symbol_type_disagreement | f_L1_017 | f_L1_017: sym_L1_014: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) dresser, pass 2 (zai-org/GLM-4.6V-Flash) desk | typed dresser by code (name_text): dresser: the documents name it: the text '*SIFONIYER' (TEXT:29ABD3) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.55 m within 40%; inferred, listed in the report |
| c_309 | symbol_type_disagreement | f_L1_020 | f_L1_020: sym_L1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_310 | symbol_type_disagreement | f_L1_027 | f_L1_027: sym_L1_024: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) washbasin | typed washbasin by code (ai_member): washbasin: r_L1_dus misses it (r_L1_dus.bathroom_set (anchor f_L1_018) misses washbasin) and the AI passes named it (pass 2 (glm) answered washbasin; pass 2 (glm)'s reason names washbasin); plan crop recognition/crops/sym_L1_024_ctx.png; inferred, listed in the report |
| c_311 | other | r_L0_salon | r_L0_salon: one face holds the room names 'Salon' and 'YEMEK BÖLÜMÜ' | unresolved: first label kept, room unverified |
| c_312 | other | r_L0_mutfak | r_L0_mutfak: one face holds the room names 'Mutfak' and 'ANTRE m²' | unresolved: first label kept, room unverified |
| c_313 | symbol_front_disagreement | f_L0_006 | f_L0_006: sym_L0_001: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_314 | symbol_front_disagreement | f_L0_014 | f_L0_014: sym_L0_009: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_315 | symbol_front_disagreement | f_L0_024 | f_L0_024: sym_L0_019: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_316 | symbol_front_disagreement | f_L0_025 | f_L0_025: sym_L0_020: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_317 | symbol_front_disagreement | f_L1_005 | f_L1_005: sym_L1_002: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_318 | symbol_front_disagreement | f_L1_008 | f_L1_008: sym_L1_005: AI front [0.0, 90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_319 | symbol_front_disagreement | f_L1_017 | f_L1_017: sym_L1_014: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_320 | symbol_front_disagreement | f_L1_021 | f_L1_021: sym_L1_018: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_321 | symbol_front_disagreement | f_L1_022 | f_L1_022: sym_L1_019: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_322 | registration_residual | r4, r3 | sheets.json sc_001: real06.dwg r4 (L1) registered onto r3 (L0) with an RMS outline distance of 0.130 m (826 of 1016 outline points within 5 cm; outlines 14.17 x 20.70 m vs 14.47 x 20.70 m) | unresolved: each level is built as drawn |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 9 regions (use: exterior 5, heights 2, read 2). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r2 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r3 | real06.dwg | floor_plan | geometry (0.70) | verified | L0 (assumed) | base | read |
| r4 | real06.dwg | floor_plan | geometry (0.70) | verified | L1 (assumed) | base | read |
| r5 | real06.dwg | section | geometry (0.85) | verified | - | - | heights |
| r6 | real06.dwg | roof_plan | geometry (0.60) | verified | - | - | exterior |
| r7 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r8 | real06.dwg | elevation | geometry (0.70) | verified | - | - | exterior |
| r9 | real06.dwg | section | geometry (0.85) | verified | - | - | heights |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L0 | Ground floor | floor | r3 | - |
| L1 | Level 1 | floor | r4 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L0, L1 | r3, r4 |

Section regions (heights): r5.

Strays (entities far from every drawing, ignored): 0.

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| real06.dwg | dwg | 50.00 | unit_check | area_labels None 0.00 (3); level_marks m 1:50 0.98 (164); door_widths m 1:50 1.00 (10); wall_thickness None 0.00 (2468); text_height m 1:50 1.00 (803); dimensions None - (0); dimension_texts None - (565) | - |

Conflicts:

| id | kind | description | resolution |
|---|---|---|---|
| sc_001 | registration_residual | real06.dwg r4 (L1) registered onto r3 (L0) with an RMS outline distance of 0.130 m (826 of 1016 outline points within 5 cm; outlines 14.17 x 20.70 m vs 14.47 x 20.70 m) | unresolved: each level is built as drawn |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/real06_dwg_s1.jpg](debug/real06_dwg_s1.jpg)

Sheet warnings:

- real06.dwg: $INSUNITS 0 names no unit; the drawing is scaled: drawn in m at 1:50 (50 m per unit), inferred from 3 agreeing checks (level_marks 98%, door_widths 100%, text_height 100%); no plain unit fits
- real06.dwg r1: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r2: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r7: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r8: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r3: plan without a level title: level L0 'Ground floor' inferred from its floor mark +0.50 m (2 untitled plans ordered by their floor marks)
- real06.dwg r4: plan without a level title: level L1 'Level 1' inferred from its floor mark +3.50 m (2 untitled plans ordered by their floor marks)
- registration: r3 (L0): stairs drawn on this level only
- registration: r4 (L1): stairs drawn on the level next to it only
- 2 sections: heights from r5; r9 not read for heights
- section r5: 16.32 m wide, no outline extent fits; the cut line on r3 gives the axis y
- roof: the roof plan r6 gives a hip roof at 33 %; the section's profile reads as gambrel (its outline also draws trusses and trims): the roof plan wins
- elevation r1: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r2: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r7: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r8: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L0 | Ground floor | floor | 0,00 m (section) | 2,85 m (section) | base | r3 |
| L1 | Level 1 | floor | 3,00 m (section) | 2,85 m (section) | base | r4 |

Variants:

| variant | label | levels | rooms changed | outside changed |
|---|---|---|---|---|
| base | Base | L0, L1 | 0 | no |

Heights (drawn = read from a document; assumed = a default, listed again under Assumed values):

| item | value | state | from | note |
|---|---|---|---|---|
| L0 ceiling height | 2,85 m | drawn | section | - |
| L0 floor level | 0,00 m | drawn | section | - |
| L0 floor to floor | 3,00 m | drawn | vector | - |
| L1 ceiling height | 2,85 m | drawn | section | - |
| L1 floor level | 3,00 m | drawn | section | - |
| L1 floor to floor | 3,00 m | drawn | vector | - |
| sl_L0 thickness | 0,15 m | drawn | section | - |
| sl_L1 thickness | 0,15 m | drawn | section | - |
| roof eaves height | 6,00 m | drawn | vector | 3.00 m above the top floor |
| roof ridge height | 7,77 m | drawn | vector | 4.77 m above the top floor |
| roof overhang | 0,47 m | drawn | vector | left 0.50 m, right 0.48 m |
| roof knee wall | 3,00 m | drawn | vector | the roof's top surface at the outer face of the outer wall above the top floor (a cross-check) |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L0 | L0 | 0,00 m | 0,15 m | section | 0 | all | verified |
| sl_L1 | L1 | 3,00 m | 0,15 m | section | 1 | all | verified |

Roof:

- type hip (roof_plan)
- over level L1
- eaves 6,00 m (drawn)
- ridge 7,77 m (drawn)
- overhang 0,47 m (drawn)
- knee wall 3,00 m (drawn)
- pitch 18.3 deg (drawn)
- 0 planes, 0 opening(s)
- covering not drawn (outside look: see Exterior views)

Facade:

| elevation | title | side | windows | doors | plan check |
|---|---|---|---|---|---|
| r1 | - | all | 0 | 0 | - |
| r2 | - | all | 0 | 0 | - |
| r7 | - | all | 0 | 0 | - |
| r8 | - | all | 0 | 0 | - |

Site:

- plot not drawn
- 0 paving area(s), 0 grass, 0 parking built
- 0 boundary wall(s), 35 decor item(s) built
- 2 labelled area(s), 2 recorded only (label, not built)
- ground levels: right -0,50 m (drawn)
- terrain flat, 0 light well(s)

Levels and ground (Milestone 12):

- 7 level mark(s) read (floor 2, ground_finished 1, slab_top 2, threshold 2); 2 mark symbol(s) taken out of the furniture
- datum ±0.00 = 0.50 m (drawn)
- ground from: marks; terrain flat
- plinth top 0,00 m (inferred)

| Door | Threshold | Ground | Rise | Solution | Main |
|---|---|---|---|---|---|
| d_L0_004 | 0,00 m | -0,50 m | 0,50 m | none | yes |
| d_L0_006 | 0,00 m | -0,50 m | 0,50 m | none |  |
| d_L1_007 | 3,00 m | -0,50 m | 3,50 m | none |  |
| d_L1_011 | 3,00 m | -0,50 m | 3,50 m | none |  |

Inferred (listed, CLAUDE.md evidence rules):

- outdoor space column: sd_L0_010 at (1.95, -1.55): one column from os_L0_veranda's floor (+0.00 m) through the slab of os_L1_balkon to +6.00 m (it stopped at +2.80 m and a second post stood on it: the slab cut it in the middle; lesson UL209)
- outdoor space column: sd_L0_009 at (4.36, -1.57): one column from os_L0_veranda's floor (+0.00 m) through the slab of os_L1_balkon to +6.00 m (it stopped at +2.80 m and a second post stood on it: the slab cut it in the middle; lesson UL209)
- outdoor space os_L0_veranda: veranda 'VERANDA' on L0: 22.84 m² (stated 22.80 m²), strokes; floor +0.00 m (the level mark(s) +0,50 inside it); doors d_L0_004, d_L0_006 open onto it (it is their landing); its edge and steps down to the ground -0.50 m (the drawn steps); pitched over 15.22 m², top +3.00 m; 3 post(s) (2 drawn column(s)) (inferred)
- outdoor space os_L1_balkon: balcony 'BALKON' on L1: 11.60 m² (stated 11.80 m²), strokes; floor +3.00 m (the level mark(s) +3,50 inside it); doors d_L1_007, d_L1_011 open onto it (it is their landing); a slab with a guard on its open edges (inferred)
- site symbols: axis_bubble: 28 drawn site symbol(s) typed axis_bubble (a structural grid bubble (the axis label), drawing annotation; not built): sd_L0_001, sd_L0_002, sd_L0_003, sd_L0_004, sd_L0_005, sd_L0_006, sd_L0_007, sd_L0_008 ...
- site symbols: column: 2 drawn site symbol(s) typed column (a column; built with os_L0_veranda): sd_L0_009, sd_L0_010
- site symbols: door_symbol: 1 drawn site symbol(s) typed door_symbol (a door symbol; not built): sd_L0_013
- site symbols: hatch: 1 drawn site symbol(s) typed hatch (a hatch; not built): sd_L0_015
- site symbols: level_mark: 2 drawn site symbol(s) typed level_mark (a level mark symbol; not built): sd_L0_014, sd_L0_021
- site symbols: outdoor_space_detail: 1 drawn site symbol(s) typed outdoor_space_detail (a detail of an outdoor space (its edge or steps); built with os_L0_veranda): sd_L0_016
- entrance d_L0_001: 0.50 m above the ground (terrain (flat)): a landing and 4 riser(s) of 0.125 m, tread 0.33 m (inferred)
- entrance d_L0_003: 0.50 m above the ground (terrain (flat)): a landing and 4 riser(s) of 0.125 m, tread 0.33 m (inferred)
- site.plinth: no SB. mark: the plinth up to the ground floor

Flagged: step and ramp numbers: secondary sources on TS 9111 (docs/milestone12.md §3.7).

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 19 piece(s) added, 2 wall cabinet run(s).

### Salon (r_L0_salon, living): completed

- added f_L0_033: floor_lamp 0.40 x 0.40 (confidence -, rule)
- added f_L0_034: bookshelf 1.00 x 0.35 (confidence -, rule)
- added f_L0_035: potted_plant 0.35 x 0.35 (confidence -, rule)
- added f_L0_036: armchair 0.80 x 0.80 (confidence -, rule)
- added f_L0_037: ottoman 0.50 x 0.50 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_009, f_L0_011, f_L0_012, f_L0_013, f_L0_014, f_L0_016, f_L0_027, f_L0_028, f_L0_029, f_L0_030

### Mutfak (r_L0_mutfak, kitchen): completed

- added f_L0_038: stove 0.45 x 0.60 (confidence -, rule)
- added f_L0_039: table_dining 0.80 x 0.70 (confidence -, rule)
- added f_L0_040: chair 0.45 x 0.45 (confidence -, rule)
- added f_L0_041: chair 0.45 x 0.45 (confidence -, rule)
- added f_L0_042: kitchen_island 1.20 x 0.80 (confidence -, rule)
- added f_L0_043: bar_stool 0.42 x 0.42 (confidence -, rule)
- added f_L0_044: bar_stool 0.42 x 0.42 (confidence -, rule)
- 2 wall cabinet run(s) over the drawn counter
- not placed kitchen_run: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001, f_L0_002, f_L0_003, f_L0_004, f_L0_020, f_L0_031, f_L0_032

### Banyo (r_L0_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_010, f_L0_024

### Ebeveyn Y.odası (r_L1_ebeveyn_y_odasi, bedroom): completed

- added f_L1_029: desk 1.00 x 0.50 (confidence -, rule)
- added f_L1_030: office_chair 0.60 x 0.60 (confidence -, rule)
- added f_L1_031: floor_lamp 0.40 x 0.40 (confidence -, rule)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_015, f_L1_016

### Çocuk Odası (r_L1_cocuk_odasi, bedroom): completed

- added f_L1_032: wardrobe 1.20 x 0.50 (confidence -, rule)
- added f_L1_033: desk 1.00 x 0.50 (confidence -, rule)
- added f_L1_034: office_chair 0.60 x 0.60 (confidence -, rule)
- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- not placed sleeping_double: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_004, f_L1_005, f_L1_006, f_L1_007, f_L1_008

### Soyunma Odası (r_L1_soyunma_odasi, other): completed (nothing fits: dressing: no place passes the checks)

- not placed dressing: no free place passed the placer checks (no place passes the checks)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_011, f_L1_012

### Hol (r_L1_hol, hall): completed

- added f_L1_035: shoe_cabinet 1.00 x 0.35 (confidence -, rule)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_003

### Duş (r_L1_dus, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_018, f_L1_021, f_L1_027

### Oda (r_L1_oda_2, bedroom): completed (nothing to add)

- not placed sleeping_single: no free place passed the placer checks (no candidate position fits the room)
- not placed storage: no free place passed the placer checks (no candidate position fits the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_013, f_L1_014, f_L1_017, f_L1_025

### Banyo (r_L1_banyo, bathroom): completed (nothing missing: the drawn groups are complete)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_009, f_L1_019, f_L1_022

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 56 of 56 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 50 ok, 6 failed; 33 changed by the AI or by code (an adjusted_by_ai, modified_by_ai or corrected_by_ai label in the final building; listed with their reasons under Inferred and AI-changed items).

| piece | type (drawn) | anchor moved (m) | front turned (deg) | same wall | notes |
|---|---|---|---|---|---|
| f_L0_014 | sofa (sofa) | 0.41 | 0.00 | - | - |
| f_L0_020 | sink_kitchen (sink_kitchen) | 0.44 | 0.00 | - | - |
| f_L0_029 | chair (chair) | 0.08 | 0.00 | - | - |
| f_L0_030 | chair (chair) | 0.09 | 0.00 | - | - |
| f_L1_005 | dresser (dresser) | 0.27 | 0.00 | yes | - |
| f_L1_014 | wardrobe (wardrobe) | 0.05 | 0.00 | yes | - |

Locked-rule violations:

- openings: must stay as drawn (byte-equal): changed d_L0_001, d_L0_004, d_L0_005, d_L0_006, d_L0_007, d_L1_002, d_L1_003, d_L1_004, d_L1_006, d_L1_007, d_L1_008, d_L1_009, d_L1_010, d_L1_011, o_L0_001, o_L0_002, o_L0_003, o_L0_005, o_L0_006, o_L0_007, o_L1_003, o_L1_004, o_L1_005, o_L1_006, o_L1_007, win_L0_001, win_L0_002, win_L0_004, win_L0_005, win_L0_006, win_L0_007, win_L1_001, win_L1_002, win_L1_003, win_L1_006, win_L1_007, win_L1_009; removed d_L0_003, o_L1_001, win_L0_003, win_L1_004, win_L1_005, win_L1_008
- rooms: must stay as drawn (byte-equal): changed r_L0_salon, r_L1_banyo, r_L1_cocuk_odasi, r_L1_dus, r_L1_ebeveyn_y_odasi, r_L1_hol, r_L1_oda, r_L1_oda_2, r_L1_soyunma_odasi
- f_L0_002: fixed equipment removed
- f_L0_010: fixed equipment changed its type
- f_L0_014: moved 0.413 m by the agent (> 0.3 m)
- f_L0_020: fixed equipment moved or resized (only the orientation may change)
- f_L0_026: fixed equipment moved or resized (only the orientation may change)
- f_L1_009: fixed equipment moved or resized (only the orientation may change)
- f_L1_023: fixed equipment moved or resized (only the orientation may change)

## Exterior views

6 of 6 exterior view(s) of variant `base` rendered.

- contact sheet of `base`: [contact_exterior_base.jpg](contact_exterior_base.jpg)

Gate for the exterior polish: **polish_disabled** (exterior views stay the Cycles render): negative controls rejected 0.683 < 0.90 (60 comparisons): the gate lets geometry changes through.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | front, right | - | cycles (gate_validation) | not_in_view | front: unverified; right: unverified | no |
| ext_2 | corner | back, right | - | cycles (gate_validation) | not_in_view | back: unverified; right: unverified | no |
| ext_3 | corner | back, left | - | cycles (gate_validation) | not_in_view | back: unverified; left: unverified | no |
| ext_4 | corner | front, left | - | cycles (gate_validation) | ok | front: unverified; left: unverified | no |
| ext_5 | aerial | back, left | - | cycles (gate_validation) | ok | back: unverified; left: unverified | no |
| ext_6 | frontal | front | - | cycles (gate_validation) | ok | front: unverified | no |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | - | agent | no | agent override (docs/milestone11.md §17.3) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | painted_metal_white | - | fallback | yes | style profile exterior.window_frame (assumed) |
| door | painted_wood_white | - | agent | no | agent override (docs/milestone11.md §17.3) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | fallback | yes | style profile exterior.garden (assumed) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | white | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: building.json facade.elevations. 4 facade(s): 0 ok, 0 mismatch, 4 not checked; roof mismatch.

| elevation | side | drawn win/door | built win/door | result | notes |
|---|---|---|---|---|---|
| r1 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r2 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r7 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |
| r8 | all | 0/0 | - | not_checked | the elevation has neither a view bearing nor a side: nothing to compare |

Roof heights: built eaves 6,00 m, ridge 7,55 m; drawn eaves 6,00 m (vector), ridge 7,77 m (vector); result mismatch.

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| real06.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 8, group_member 8, inferred 9, level 1, name_text 3, none 8, rule 15, same_block 3, zone_label 1. Recognition questions: 41; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers, unless code types it afterwards (a twin, a group member, the size inference: the `agreed` column names the method).

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_006 | r_L0_salon | sofa | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.85; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 1.00 |
| f_L0_009 | r_L0_salon | unknown | no | unverified | no (drawn inside sofa f_L0_006 (2.12 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.80 |
| f_L0_010 | r_L0_banyo | shower | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L0_012 | r_L0_salon | unknown | no | unverified | no (drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.80 |
| f_L0_013 | r_L0_salon | unknown | no | unverified | no (drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.80 |
| f_L0_014 | r_L0_salon | sofa | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_dining 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_015 | r_L0_salon | table_coffee | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: bookshelf, front right 0.90 |
| f_L0_019 | r_L0_salon | armchair | no (typed by same_block) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.85; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L0_021 | r_L0_salon | table_coffee | no (typed by inferred) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_024 | r_L0_banyo | toilet | no (typed by level) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: toilet, front right 1.00 |
| f_L0_026 | r_L0_banyo | washbasin | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front bottom 0.90 |
| f_L0_027 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L0_028 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front bottom 0.90 |
| f_L0_029 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L0_030 | r_L0_salon | chair | no (typed by rule) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L1_004 | r_L1_cocuk_odasi | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front top 0.90 |
| f_L1_005 | r_L1_cocuk_odasi | dresser | no (typed by name_text) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: dresser, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: desk, front left 0.90 |
| f_L1_006 | r_L1_cocuk_odasi | unknown | no | unverified | no (drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)) | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_007 | r_L1_cocuk_odasi | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 0.90 |
| f_L1_008 | r_L1_cocuk_odasi | nightstand | yes | verified | no (architect F5: it cut f_L1_007 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: nightstand, front right 0.90 |
| f_L1_009 | r_L1_banyo | bathtub | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_011 | r_L1_soyunma_odasi | wardrobe | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front left 0.85; pass 2 zai-org/GLM-4.6V-Flash: stair, front right 0.90 |
| f_L1_012 | r_L1_soyunma_odasi | wardrobe | no (typed by group_member) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.85; pass 2 zai-org/GLM-4.6V-Flash: stair, front left 0.90 |
| f_L1_017 | r_L1_oda_2 | dresser | no (typed by name_text) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: dresser, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: desk, front left 0.80 |
| f_L1_018 | r_L1_dus | shower | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: shower, front right 1.00 |
| f_L1_019 | r_L1_banyo | washing_machine | no (typed by name_text) | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin 0.90 |
| f_L1_020 | r_L1_ebeveyn_y_odasi | floor_lamp | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.90 |
| f_L1_021 | r_L1_dus | toilet | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: toilet, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: toilet, front top 1.00 |
| f_L1_022 | r_L1_banyo | toilet | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: toilet, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: toilet, front right 1.00 |
| f_L1_023 | r_L1_banyo | washbasin | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front bottom 0.90 |
| f_L1_027 | r_L1_dus | washbasin | no (typed by inferred) | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front right 0.90 |

## Site

The plot, paving, grass, parking and boundary walls marked built are built in the 3D scene and show in the exterior views; an area that is only a label (not built) is recorded, not built.

| id | what | detail |
|---|---|---|
| sa_L0_veranda | area 'VERANDA' (other) | label size -, measured - (-), built as the outdoor space os_L0_veranda (inferred) |
| sa_L1_balkon | area 'BALKON' (other) | label size -, measured - (-), built as the outdoor space os_L1_balkon (inferred) |
| - | decor | other x 35 |

## Separators

None.

## Assumed values

- style: default text "Scandinavian, light oak floor, white walls, linen textiles, warm daylight" (no style in brief.yaml; wenart/defaults.yaml)
- style exterior facade render in white, roof concrete_tiles in anthracite, window_frame as inside (painted_metal_white), door as inside (wood_oak_light), paving paving in grey, garden grass from style.exterior_fallback of wenart/defaults.yaml (no word for them in the brief)
- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
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
- brief library.licence_mode: relaxed (default, not in brief.yaml)
- L0: level 'Ground floor' assumed (no level title on the page)
- L1: level 'Level 1' assumed (no level title on the page)
- front kept from the drawing although both AI passes answered 'none': 2 piece(s) (f_L0_026, f_L1_023)
- door height 2,10 m: 11 opening(s) (d_L0_005, d_L0_006, d_L0_007, d_L1_002, d_L1_003, d_L1_006 ...)
- door height 2,30 m: 1 opening(s) (d_L0_004)
- door sill height -: 1 opening(s) (win_L1_003)
- opening height 2,10 m: 1 opening(s) (o_L1_002)
- window height 1,15 m: 1 opening(s) (o_L0_001)
- window height 1,20 m: 20 opening(s) (win_L0_001, o_L0_002, o_L0_004, o_L0_007, win_L0_002, win_L0_004 ...)
- window height 1,80 m: 3 opening(s) (d_L1_004, win_L1_006, win_L1_009)
- window height 2,40 m: 6 opening(s) (d_L0_001, o_L0_003, o_L0_005, o_L0_006, win_L0_005, win_L0_006)
- window sill height 0,20 m: 2 opening(s) (win_L0_005, win_L0_006)
- window sill height 0,30 m: 2 opening(s) (win_L1_006, win_L1_009)
- window sill height 0,90 m: 9 opening(s) (win_L0_001, win_L0_002, win_L0_004, win_L0_007, win_L1_001, win_L1_002 ...)
- f_L0_001 (stair): void assumed (the plan of L1 draws the same stair (f_L1_001) with its landing at the north end: the half landing is there, 1.22 m deep; it draws only the flight at (4.08, 12.33): that flight arrives on L1)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- roof covering: not drawn (the outside look decides, see below)
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
- outside look window_frame: painted_metal_white (fallback: style profile exterior.window_frame (assumed))
- outside look paving: paving in grey (fallback: style profile exterior.paving (assumed))
- outside look garden: grass (fallback: style profile exterior.garden (assumed))
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))
- outside look plot_wall: render in white (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_banyo: agent: View cam_r_L0_banyo_1 is 0.19 stops over the EV cap; the finding names x1.61 to bring incident light to target.; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_banyo |
| area_light | 1 | r_L1_oda: room has no window; the room's light rig (1 fixtures) carries the light instead of the invisible ceiling light | rig_r_L1_oda |
| azimuth_deg | 1 | no north arrow: the sun 45 degrees off the main (-y) facade, so the views of it show light and shadows (docs/milestone11.md §4.1 X7; was 210) | sun |
| balustrade | 1 | one continuous balustrade per open side with newels at its turns (not drawn: assumed; scandinavian: stringer structure, glass panels under a timber handrail, structure strings (glass posts language of the house)) | furn_f_L0_001 |
| bath_details | 6 | the bathroom details of the piece (UL114, UL123, UL124: LED strips, a flush plate, towels and toiletries, shower fittings) inside its own box, one mesh | furn_f_L0_024, furn_f_L0_047, furn_f_L1_021 |
| bath_items | 3 | the floating vanity's styling (UL114 B3, UL123 B19): part of its one mesh | furn_f_L0_026, furn_f_L1_023, furn_f_L1_027 |
| bay_lights | 2 | an LED strip at the top of every bay lights the contents so they read through the see-through front (UL135; a wardrobe LED profile, 1000 lm per metre (UL135)) | furn_f_L1_011, furn_f_L1_012 |
| bedding | 1 | its cover is flat (relief 0 mm, 211 vertices/m2 on top: under 6 mm or 50; 97% of the middle on the top: under 50%): poorer than our duvet; light linen layers in soft neutrals, a boucle and a knit cushion, a striped wool blanket under a fringed knit throw (Scandinavian: natural textures, little pattern) | dress_f_L1_010 |
| bedding | 1 | its cover is flat (relief 86 mm, 91 vertices/m2 on top: under 6 mm or 50; 10% of the middle on the top: under 50%): poorer than our duvet; light linen layers in soft neutrals, a boucle and a knit cushion, a striped wool blanket under a fringed knit throw (Scandinavian: natural textures, little pattern) | dress_f_L1_007 |
| bedding | 1 | the bed model has no bedding (docs/milestone12.md §4.7); light linen layers in soft neutrals, a boucle and a knit cushion, a striped wool blanket under a fringed knit throw (Scandinavian: natural textures, little pattern) | dress_f_L1_013 |
| boundary | 1 | no site plan: a low hedge on the inferred plot boundary (inferred) | site |
| chimney | 1 | inferred chimney (scandinavian family: a Scandinavian house warms its living room with a wood-burning stove); no fireplace or flue drawn; over the fireplace wall w_L0_011 of the living room r_L0_salon (a solid inner wall stretch of 1.4 m with no door or window); top 8.20 m: 0.6 m over the roof within 3 m (its highest point there 7.55 m) and 0.9 m over where it leaves the roof (6.62 m), the 3-2-10 rule of thumb | chimney_1 |
| climate | 1 | the drawing's language (tr): the climate most of its houses stand in (a guess) (inferred; the species of trees and hedges follow it): banyo, cocuk, ebeveyn, mutfak | site |
| column_design | 1 | sd_L0_009: a slender 219.1 mm round steel post on a base plate, 6.00 m tall (about 1:27); drawn a 0.40 m round column (kept as drawn_look); the user chose slender steel posts for the house's columns (lesson UL214) | site_columns |
| column_design | 1 | sd_L0_010: a slender 219.1 mm round steel post on a base plate, 6.00 m tall (about 1:27); drawn a 0.40 m round column (kept as drawn_look); the user chose slender steel posts for the house's columns (lesson UL214) | site_columns |
| context | 1 | no context drawn: 137 trees of the mediterranean climate (stone_pine 52, olive 37, plane 25, cypress 23; species inferred) in groups around the site, 54-350 m from the building's centre (the exterior cameras stand within 54 m), with open fields between them so the horizon stays in view (inferred context) | site |
| cut_through | 1 | the wall overlaps w_L0_018 at its opening win_L0_002: cut through both (a facade line drawn over a thicker wall) | w_L0_019 |
| cut_through | 1 | the wall overlaps w_L0_019 at its opening win_L0_007: cut through both (a facade line drawn over a thicker wall) | w_L0_017 |
| cut_through | 1 | the wall overlaps w_L0_023 at its opening win_L0_005: cut through both (a facade line drawn over a thicker wall) | w_L0_022 |
| cut_through | 1 | the wall overlaps w_L0_029 at its opening win_L0_006: cut through both (a facade line drawn over a thicker wall) | w_L0_028 |
| cut_through | 1 | the wall overlaps w_L1_026 at its opening win_L1_009: cut through both (a facade line drawn over a thicker wall) | w_L1_025 |
| door_frame | 1 | every door is framed (UL122): ours (the parametric door's frame round a bare leaf); architrave on the indoor face(s) [-1] | d_L1_007 |
| door_frame | 8 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1, 1] | d_L0_005, d_L0_007, d_L1_002 |
| door_frame | 1 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [-1] | d_L0_004 |
| door_frame | 2 | every door is framed (UL122): the model's own frame; architrave on the indoor face(s) [1] | d_L0_006, d_L1_011 |
| door_size | 1 | D5 door sizes by role and family (dressing door, scandinavian style): the nearest door set width 0.75 m (drawn 0.77 m: no product size) | win_L1_003 |
| door_size | 1 | D5 door sizes by role and family (entrance door, scandinavian style): an entrance at least an entrance door set wide (0.90 m; drawn 0.80 m); its wall leaves 0.02 m on its tighter side: 0.80 m; a taller entrance door: 2.30 m high | d_L0_004 |
| door_size | 1 | D5 door sizes by role and family (storage door, scandinavian style): the nearest door set width 0.90 m (drawn 0.95 m: no product size) | d_L0_005 |
| fabric | 2 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture |
| fascia_material | 1 | pitched roof: the eaves and verge edges are a fascia board in the gutter's aluminium_anthracite (not drawn; the roof covering stretched over a 0.2 m edge read as a paper-thin sheet) | roof |
| floor_pattern | 1 | assumed: the scandinavian style lays its wood_oak_light floor in herringbone (designer value, UL106) | r_L0_salon_floor |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| ground:+y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-x | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| handrail | 1 | design detail on every stair side not against a wall; not in the documents | furn_f_L0_001 |
| hedge | 5 | no site plan: a low hedge on the inferred plot boundary (inferred) | boundary_hedge_01, boundary_hedge_02, boundary_hedge_03 |
| height | 12 | door height listed as assumed in the building JSON | d_L0_004, d_L0_005, d_L0_006 |
| height | 9 | no height in the JSON; type height for armchair | furn_f_L0_007, furn_f_L0_008, furn_f_L0_016 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L1_004, furn_f_L1_007 |
| height | 4 | no height in the JSON; type height for chair | furn_f_L0_027, furn_f_L0_028, furn_f_L0_029 |
| height | 1 | no height in the JSON; type height for floor_lamp | furn_f_L1_020 |
| height | 2 | no height in the JSON; type height for kitchen_counter | furn_f_L0_031, furn_f_L0_032 |
| height | 1 | no height in the JSON; type height for shower | furn_f_L1_018 |
| height | 2 | no height in the JSON; type height for sofa | furn_f_L0_014, furn_f_L0_048 |
| height | 2 | no height in the JSON; type height for table_coffee | furn_f_L0_021, furn_f_L0_049 |
| height | 2 | no height in the JSON; type height for toilet | furn_f_L1_021, furn_f_L1_022 |
| height | 2 | no height in the JSON; type height for washbasin | furn_f_L0_026, furn_f_L1_023 |
| height | 1 | no height in the JSON; type height for washing_machine | furn_f_L1_019 |
| height | 1 | opening height listed as assumed in the building JSON | o_L1_002 |
| height | 30 | window height listed as assumed in the building JSON | d_L0_001, o_L0_001, win_L0_001 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.125 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | o_L0_002_inside_sill, o_L1_004_inside_sill |
| kit:canopy | 1 | entrance canopy over the entrance door: a slim anthracite metal canopy with a deeper front fascia as its drip edge (the door is drawn; the canopy is not) (inferred) | facade |
| kit:canopy_rod | 1 | the entrance canopy's two tie rods to wall plates above it (not drawn) (inferred) | facade |
| kit:canopy_soffit | 1 | the entrance canopy's wood soffit (not drawn) (inferred) | facade |
| kit:downpipe | 1 | downpipe at the eaves corners (not drawn) (inferred) | facade |
| kit:guard_glass | 1 | glass guard in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:gutter | 1 | gutter along the eaves (a pitched roof is drawn; the gutter is not) (inferred) | facade |
| kit:railing | 1 | guard's metal (rails, posts, bars or a glass channel) in front of an opening over a drop with no balcony (not drawn) (inferred) | facade |
| kit:reveal | 1 | window reveal frame at the outer face (modern family; not drawn) (inferred) | facade |
| kit:wall_light | 1 | wall light beside the entrance door (not drawn) (inferred) | facade |
| leaf_state | 3 | an outside or terrace door stays closed (an open one reads as a mistake) | d_L0_006, d_L1_007, d_L1_011 |
| leaf_state | 1 | every interior door stands open by default (UL127; a bathroom or WC door); hinged at the jamb by the wall beside it (right seen from r_L0_banyo) | d_L0_007 |
| leaf_state | 1 | every interior door stands open by default (UL127; a storage room's door); hinged at the jamb by the wall beside it (left seen from r_L1_banyo) | d_L1_009 |
| leaf_state | 1 | every interior door stands open by default (UL127; a storage room's door); hinged at the jamb by the wall beside it (left seen from r_L1_cocuk_odasi) | d_L1_008 |
| leaf_state | 1 | every interior door stands open by default (UL127; a storage room's door); hinged at the jamb by the wall beside it (left seen from r_L1_ebeveyn_y_odasi) | d_L1_002 |
| leaf_state | 1 | every interior door stands open by default (UL127; a storage room's door); hinged at the jamb by the wall beside it (right seen from r_L0_mutfak) | d_L0_005 |
| leaf_state | 1 | every interior door stands open by default (UL127; a storage room's door); hinged at the jamb by the wall beside it (right seen from r_L1_oda_2) | d_L1_006 |
| leaf_state | 1 | every interior door stands open by default (UL127; into the dressing room); hinged at the jamb by the wall beside it (left seen from r_L1_ebeveyn_y_odasi); the side it opens to is assumed (no swing side drawn) | win_L1_003 |
| leaf_state | 1 | every interior door stands open by default (UL127; into the dressing room); hinged at the jamb by the wall beside it (right seen from r_L1_dus) | d_L1_003 |
| leaf_state | 1 | the entrance door stays closed (an open front door reads as a mistake) | d_L0_004 |
| left_out:door | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the scandinavian look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the scandinavian look; hssd_3764-1: glazing bars (the audit): the scandinavian look wants no or few bars; hssd_4076-9: glazing bars (the audit): the scandinavian look wants no or few bars | openings |
| left_out:entrance | 1 | models out of the style's look: 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_3a160c3c14f4cc8f244f2fcf: a panelled leaf: not the scandinavian look; 3dwh_75e4b7c9cda6ad482e21c230: a panelled leaf: not the scandinavian look; hssd_3764-0: glazing bars (the audit): the scandinavian look wants no or few bars; hssd_3764-1: glazing bars (the audit): the scandinavian look wants no or few bars; hssd_4076-9: glazing bars (the audit): the scandinavian look wants no or few bars | openings |
| left_out:glazed_door | 1 | models out of the style's look: 3dwh_5b8d6e9c0eff7893f9fe2795: patterned glass (an image on its glass): the scandinavian look wants clear glass; 3dwh_5e2175bedf4e725cd2760f52: glazing bars (16 lites, 4.1 per m2): the scandinavian look wants no or few bars; 3dwh_73ccc78df8b9b5ec4219d9b8: no see-through glass; 3dwh_a5392fea8c223c7b149f9f68: audited styles ['classic', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_c5c7d6e0742ba53b5c347d2d: no see-through glass; 3dwh_f2728c908c75fedd317b9d83: glass 20% of its face (< 45%); hssd_0d1021de4ced65417a568c62e6ecf169d47b1f85: glass 23% of its face (< 45%); hssd_209-10: glazing bars (the audit): the scandinavian look wants no or few bars | openings |
| left_out:inside_door:solid | 1 | models out of the style's look: 3dwh_07b2214948fc287e2651d776: glass 100% of its face (> 8%): not a solid leaf; 3dwh_171ad2acc3490673ce6fcb44: audited styles ['classic', 'modern', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_31a4f763e80370fb618fd10d: made for a bathroom / wc (its title): 7 solid door(s) open into none (d_L0_005, d_L1_002, d_L1_003, d_L1_006); 3dwh_3befa867f6b07c735086bba4: a sliding door for a swing door; 3dwh_4555ada4db4043a2400c0747: made for a bathroom / bedroom / wc (its title): 7 solid door(s) open into none (d_L0_005, d_L1_002, d_L1_003, d_L1_006); 3dwh_779ae72d1a217f8a883b35b7: glass 15% of its face (> 8%): not a solid leaf; 3dwh_80ecf1763916b0e5e2bd9147: a panelled leaf: not the scandinavian look; 3dwh_8af4cac2bbaed9252628dfb7: made for a bathroom / wc (its title): 7 solid door(s) open into none (d_L0_005, d_L1_002, d_L1_003, d_L1_006) | openings |
| left_out:window | 1 | models out of the style's look: 3dwh_008fc2b4ab59c1a67589cb97: no see-through glass; 3dwh_16c5fdb11c4ec7d95492a04b: glazing bars (12 lites, 3.0 per m2): the scandinavian look wants no or few bars; 3dwh_2a2ec61614b5278cf6fe1011: no see-through glass; 3dwh_48bec799740fad36241c99d9: no see-through glass; 3dwh_4a7dc5974d3b797601e64e12: audited styles ['classic', 'rustic']: mostly classic, rustic, not the scandinavian look; 3dwh_56f518dddfda5b3c284ddf47: no see-through glass; 3dwh_5c21a04d22581a3786ae9bef: no see-through glass; 3dwh_5faa67969eb7104b4adee381: its title says 'traditional': not the scandinavian look | openings |
| level | 1 | terrace os_L0_veranda: one level at +0.00 m (the level mark(s) +0,50 inside it); ground -0.50..-0.50 m under it; edge: steps (inferred); the labelled veranda 'VERANDA' of L0, the landing of d_L0_004, d_L0_006; the drawn steps on edge 7; edges 0, 1, 2, 3, 4, 5, 14 face the building (its walls retain there: no wall, band or steps); a flight of 3 risers of 0.167 m, tread 0.25 m down 0.50 m from edge 7 to the ground at its foot (the count settled on the ground the last riser lands on); each tread a solid block on the one below, cheek walls holding the ground beside it, a landing at its foot, a hole in the lawn (inferred); its retaining wall stops at the building on edges 6 (0.00-0.17 m), 13 (1.60-1.77 m) (never through the house's wall, UL148) | platform_os_L0_veranda |
| level | 1 | terrace os_L1_balkon: one level at +3.00 m (the level mark(s) +3,50 inside it); ground -0.50..-0.50 m under it; edge: none (inferred); the labelled balcony 'BALKON' of L1, the landing of d_L1_007, d_L1_011; elevated: a slab with a guard on its open edges; a crisp 0.42 m edge band on its exposed edges 6, 7 (UL214) | platform_os_L1_balkon |
| library_model | 1 | library door 3dwh_54d07ce98f9345c95081fc1e ('Modern Single Door') in 1 panel(s) of 0.80 x 2.10 m (proportions off by 15 %; the documents draw the opening, not its product); the building's one door family; another family than the entrance's; scandinavian look: audited styles ['modern'] suit the scandinavian look; its leaf not seen by the audit's opening question: after the doors it saw; frames in the style's finish | d_L1_007 |
| library_model | 1 | library entrance hssd_4141-3 ('HSSD door 4141-3 (0.91 x 2.13 m)') in 1 panel(s) of 0.80 x 2.30 m (proportions off by 23 %; the documents draw the opening, not its product); the building's one entrance family; scandinavian look: audited styles ['industrial', 'modern'] suit the scandinavian look; frames in the style's finish | d_L0_004 |
| library_model | 1 | library glazed door hssd_208-5 ('HSSD double door 208-5 (2.00 x 2.00 m)') in 1 panel(s) of 1.98 x 2.10 m (proportions off by 6 %; the documents draw the opening, not its product); the building's glazed door family for the doors that open hinged (the first, door:series:hssd:6161, opens another way); scandinavian look: audited styles ['industrial', 'modern'] suit the scandinavian look; frames in the style's finish | d_L1_011 |
| library_model | 1 | library glazed door hssd_6161-2 ('HSSD sliding door 6161-2 (1.69 x 2.20 m)') in 2 panel(s) of 1.48 x 2.10 m (proportions off by 10 %; the documents draw the opening, not its product); the building's one glazed door family (one of 3 equal families, picked by the house's seed); another family than the entrance's; scandinavian look: audited styles ['minimal', 'modern'] suit the scandinavian look; frames in the style's finish | d_L0_006 |
| library_model | 3 | library inside door hssd_200-32 ('HSSD door 200-32 (0.91 x 2.20 m)') in 1 panel(s) of 0.85 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a lined leaf, an architrave and hinges where it is framed (the scandinavian family's door, assumed)), style door painted_wood_white; scandinavian look: audited styles ['minimal', 'modern'] suit the scandinavian look; frames in the style's finish | d_L1_002, d_L1_006, d_L1_008 |
| library_model | 2 | library inside door hssd_200-32 ('HSSD door 200-32 (0.91 x 2.20 m)') in 1 panel(s) of 0.90 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a lined leaf, an architrave and hinges where it is framed (the scandinavian family's door, assumed)), style door painted_wood_white; scandinavian look: audited styles ['minimal', 'modern'] suit the scandinavian look; frames in the style's finish | d_L0_005, d_L0_007 |
| library_model | 3 | library inside door hssd_200-5 ('HSSD door 200-5 (0.81 x 2.20 m)') in 1 panel(s) of 0.75 x 2.10 m (proportions off by 3 %; the documents draw the opening, not its product); the house's solid inside door family; not a facade family; door style flush: door flush (drawn operation swing; a lined leaf, an architrave and hinges where it is framed (the scandinavian family's door, assumed)), style door painted_wood_white; scandinavian look: audited styles ['minimal', 'modern'] suit the scandinavian look; frames in the style's finish | d_L1_003, d_L1_009, win_L1_003 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 0.75 x 1.20 m (proportions off by 28 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_010 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 0.77 x 1.20 m (proportions off by 24 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_007 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 0.95 x 1.20 m (proportions off by 1 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_001 |
| library_model | 2 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 1.12 x 1.20 m (proportions off by 16 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L0_004, win_L1_007 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 1.16 x 1.80 m (proportions off by 24 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | win_L1_009 |
| library_model | 2 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 1.55 x 2.40 m (proportions off by 24 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_005, o_L0_006 |
| library_model | 2 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 1 panel(s) of 2.15 x 2.40 m (proportions off by 12 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L0_001, o_L0_003 |
| library_model | 3 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 2 panel(s) of 0.78 x 1.20 m (proportions off by 24 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L1_005, o_L1_006, o_L1_007 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 2 panel(s) of 0.93 x 1.20 m (proportions off by 4 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L0_007 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 2 panel(s) of 0.97 x 1.20 m (proportions off by 2 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | o_L1_003 |
| library_model | 1 | library window 3dwh_f3ac62c6f63d05d554d7c9a7 ('Double Casement Window') in 2 panel(s) of 1.07 x 1.20 m (proportions off by 12 %; the documents draw the opening, not its product); the building's one window family; scandinavian look: audited styles ['minimal', 'modern', 'scandinavian'] name scandinavian; frames in the style's finish | d_L1_001 |
| modules | 11 | built from real product modules (docs/milestone13.md §12 D4): no audited library model fits the drawn size; the drawn footprint is kept (fit {'dw_m': 0.0, 'dd_m': 0.0, 'rel': 0.0, 'tol': 0.1, 'within_cap': True}) | furn_f_L0_010, furn_f_L0_026, furn_f_L0_031 |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 0.45 x 1.20 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | d_L1_010 |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 0.64 x 1.20 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | win_L0_002 |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 0.65 x 1.80 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | d_L1_004 |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 0.68 x 1.80 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | win_L1_006 |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 0.70 x 2.40 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | win_L0_005 |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 1.10 x 2.40 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | win_L0_006 |
| opening_model | 1 | no model of the building's window family 'Double Casement Window' fits 1.27 x 1.20 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | win_L1_002 |
| opening_model | 3 | no model of the building's window family 'Double Casement Window' fits 1.45 x 1.20 m (or opens its way): the parametric opening in the style's finish keeps one door and window language | o_L0_004, o_L1_005, win_L1_011 |
| passage_lining | 1 | design detail of the documented passage: a lined reveal (jambs and head lining in the trim), no architrave (UL122); not in the documents | o_L1_002_lining |
| path:d_L0_004,d_L0_006 | 1 | a paved path from the entrance to the plot edge (inferred) | site |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| platform:os_L0_veranda | 1 | terrace os_L0_veranda: one level at +0.00 m (the level mark(s) +0,50 inside it); ground -0.50..-0.50 m under it; edge: steps (inferred); the labelled veranda 'VERANDA' of L0, the landing of d_L0_004, d_L0_006; the drawn steps on edge 7; edges 0, 1, 2, 3, 4, 5, 14 face the building (its walls retain there: no wall, band or steps); a flight of 3 risers of 0.167 m, tread 0.25 m down 0.50 m from edge 7 to the ground at its foot (the count settled on the ground the last riser lands on); each tread a solid block on the one below, cheek walls holding the ground beside it, a landing at its foot, a hole in the lawn (inferred); its retaining wall stops at the building on edges 6 (0.00-0.17 m), 13 (1.60-1.77 m) (never through the house's wall, UL148) | site |
| platform:os_L1_balkon | 1 | terrace os_L1_balkon: one level at +3.00 m (the level mark(s) +3,50 inside it); ground -0.50..-0.50 m under it; edge: none (inferred); the labelled balcony 'BALKON' of L1, the landing of d_L1_007, d_L1_011; elevated: a slab with a guard on its open edges; a crisp 0.42 m edge band on its exposed edges 6, 7 (UL214) | site |
| plinth | 1 | plinth: a raised base from the ground up to +0.00 m (the ground floor), at least 0.15 m high; plinth band: stone_wall_ledgestone (style family scandinavian; not drawn) | facade |
| plot | 1 | no site plan: the plot is the outline's rectangle + 6 m (inferred) | site |
| ridge_caps | 1 | ridge and hip caps along the roof's ridges and hips (not drawn; a tiled roof has them) | roof_ridges |
| rig_ceiling | 1 | ceiling fixture at (1.90, 11.32) of r_L1_oda_2 not hung: the decor pendant dec_L1_034 hangs 1.06 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 5500 lm go into the pendant | rig_r_L1_oda_2 |
| rig_ceiling | 1 | ceiling fixture at (1.94, 10.84) of r_L0_mutfak not hung: the decor pendant dec_L0_059 hangs 0.68 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 1600 lm go into the pendant | rig_r_L0_mutfak |
| rig_ceiling | 1 | ceiling fixture at (6.50, 3.52) of r_L1_ebeveyn_y_odasi not hung: the decor pendant dec_L1_008 hangs 0.82 m from it (within 1.5 m: the pendant is the zone's light, a flush light beside it reads as two lights together, UL170); its 11000 lm go into the pendant | rig_r_L1_ebeveyn_y_odasi |
| rig_light | 1 | r_L0_banyo: ceiling fixture at the pole of inaccessibility of r_L0_banyo; its light under the decor ceiling light dec_L0_052; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with a 1100 lm (75 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_banyo_ceiling_2_light |
| rig_light | 1 | r_L0_banyo: mirror light over the washbasin f_L0_026; 1100.0 lm -> 3.12 W radiant x gain 2.0 (mirror light bar, 1100 lm (75 W-equivalent); the documents say nothing about lamps) | rig_r_L0_banyo_mirror_1_light |
| rig_light | 1 | r_L0_mutfak: LED strip under the wall cabinet f_L0_045 over the counter f_L0_031; 247.2 lm -> 0.6488 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L0_mutfak_strip_1_light |
| rig_light | 1 | r_L0_mutfak: LED strip under the wall cabinet f_L0_046 over the counter f_L0_032; 375.6 lm -> 0.9858 W radiant x gain 2.0 (LED strip under the wall cabinets, 400-600 lm per metre; the documents say nothing about lamps) | rig_r_L0_mutfak_strip_2_light |
| rig_light | 1 | r_L0_mutfak: the ceiling light of the zone (spot(s) (1.94, 10.84)) in the decor pendant dec_L0_059 (UL170: the pendant is the zone's light), 1600 lm over its 1 bulb(s); bulb 1/1; 1600.0 lm -> 4.05 W radiant x gain 2.0 (ceiling fixture with a 1600 lm (100 W-equivalent) LED bulb; the documents say nothing about lamps) | rig_r_L0_mutfak_ceiling_4_light |
| rig_light | 1 | r_L0_mutfak: the decor pendant dec_L0_034 gives light (UL170: every pendant is a light), 1100 lm over its 1 bulb(s); bulb 1/1; 1100.0 lm -> 3.12 W radiant x gain 2.0 (the decor pendant's own light: 1100 lm (one 75 W-equivalent ceiling light) over its bulbs; the documents say nothing about lamps) | rig_r_L0_mutfak_pendant_3_light |
| rig_light | 1 | r_L0_oda: ceiling fixture at the pole of inaccessibility of r_L0_oda, 1 x 1100 lm bulbs for 450 lm/m2 over 2.1 m2 and 1 fixture(s); its light under the decor ceiling light dec_L0_062; 1100.0 lm -> 3.12 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L0_oda_ceiling_1_light |
| rig_light | 1 | r_L0_salon: pendant light over the dining table f_L0_011 under the decor pendant dec_L0_053; 2400.0 lm -> 4.45 W radiant x gain 2.0 (pendant with 3 x 800 lm LED bulbs over the dining table of an open living room; the documents say nothing about lamps) | rig_r_L0_salon_pendant_1_light |
| rig_light | 1 | r_L1_banyo: ceiling fixture at the pole of inaccessibility of r_L1_banyo, 3 x 1100 lm bulbs for 450 lm/m2 over 6.7 m2 and 1 fixture(s); its light under the decor ceiling light dec_L1_041; 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_banyo_ceiling_1_light |
| rig_light | 1 | r_L1_cocuk_odasi: ceiling fixture at the pole of inaccessibility of r_L1_cocuk_odasi, 10 x 1100 lm bulbs for 450 lm/m2 over 22.4 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_014; 11000.0 lm -> 31.2 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_cocuk_odasi_ceiling_1_light |
| rig_light | 1 | r_L1_dus: ceiling fixture at the pole of inaccessibility of r_L1_dus, 2 x 1100 lm bulbs for 450 lm/m2 over 4.5 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_046); 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_dus_ceiling_1_light |
| rig_light | 1 | r_L1_ebeveyn_y_odasi: the ceiling light of the zone (spot(s) (6.50, 3.52)) in the decor pendant dec_L1_008 (UL170: the pendant is the zone's light), 11000 lm over its 1 bulb(s); bulb 1/1; 11000.0 lm -> 31.2 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_ebeveyn_y_odasi_ceiling_1_light |
| rig_light | 1 | r_L1_hol: ceiling fixture at the pole of inaccessibility of r_L1_hol, 5 x 1100 lm bulbs for 450 lm/m2 over 11.0 m2 and 1 fixture(s); 1/1 of its light under each decor ceiling light of the room (dec_L1_045); 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_hol_ceiling_1_light |
| rig_light | 1 | r_L1_oda: ceiling fixture at the pole of inaccessibility of r_L1_oda, 2 x 1100 lm bulbs for 450 lm/m2 over 3.1 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_025; 2200.0 lm -> 6.24 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_oda_ceiling_1_light |
| rig_light | 1 | r_L1_oda_2: the ceiling light of the zone (spot(s) (1.90, 11.32)) in the decor pendant dec_L1_034 (UL170: the pendant is the zone's light), 5500 lm over its 1 bulb(s); bulb 1/1; 5500.0 lm -> 15.6 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_oda_2_ceiling_1_light |
| rig_light | 1 | r_L1_soyunma_odasi: ceiling fixture at the pole of inaccessibility of r_L1_soyunma_odasi, 3 x 1100 lm bulbs for 450 lm/m2 over 5.9 m2 and 1 fixture(s); its light under the decor pendant light dec_L1_028; 3300.0 lm -> 9.36 W radiant x gain 2.0 (ceiling fixture with 1100 lm (75 W-equivalent) LED bulbs, bulbs for 450 lm per m2 of floor (every room people walk into has a ceiling light point); the documents say nothing about lamps) | rig_r_L1_soyunma_odasi_ceiling_1_light |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.000 m / 17 drawn risers | furn_f_L0_001 |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| see_through | 1 | a walk-in (a dressing room), see-through on every side: horizontal black slat sliding doors with real contents and a light inside (the architect's answer (architect: r_L1_soyunma_odasi: horizontal black slat sliding doors); UL120, UL125); a top box to the ceiling (0.75 m of lidded boxes and baskets over the hanging bays); replaces the library model 3dwh_cd977a9c92ad97fb4850257f | furn_f_L1_012 |
| see_through | 1 | a walk-in (a dressing room), see-through on every side: horizontal black slat sliding doors with real contents and a light inside (the architect's answer (architect: r_L1_soyunma_odasi: horizontal black slat sliding doors); UL120, UL125); replaces the library model 3dwh_cd977a9c92ad97fb4850257f | furn_f_L1_011 |
| sill | 1 | outside sill 0.51 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | d_L1_010_sill |
| sill | 1 | outside sill 0.7001 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill |
| sill | 1 | outside sill 0.71 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | d_L1_004_sill |
| sill | 1 | outside sill 0.7357 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_006_sill |
| sill | 1 | outside sill 0.76 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_005_sill |
| sill | 1 | outside sill 0.81 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_010_sill |
| sill | 1 | outside sill 0.8348 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_007_sill |
| sill | 1 | outside sill 1.01 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_001_sill |
| sill | 1 | outside sill 1.16 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_006_sill |
| sill | 1 | outside sill 1.16 x 0.134 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_002_sill |
| sill | 2 | outside sill 1.1751 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_004_sill, win_L1_007_sill |
| sill | 1 | outside sill 1.21 x 0.134 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L1_004_sill |
| sill | 1 | outside sill 1.2248 x 0.149 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_009_sill |
| sill | 1 | outside sill 1.3252 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L1_002_sill |
| sill | 3 | outside sill 1.51 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_004_sill, o_L1_005_sill, win_L1_011_sill |
| sill | 5 | outside sill 1.61 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_005_sill, o_L0_006_sill, d_L1_005_sill |
| sill | 1 | outside sill 1.91 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L0_007_sill |
| sill | 1 | outside sill 2.01 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | o_L1_003_sill |
| sill | 3 | outside sill 2.21 x 0.124 m, 0.04 m proud of the facade (not drawn; size assumed) | d_L0_001_sill, o_L0_003_sill, d_L1_001_sill |
| sill_height | 13 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_004 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 11 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_salon, skirting_r_L0_mutfak, skirting_r_L0_oda |
| slab_band | 1 | slab band / coping: the facade material, set off in colour (not drawn) | facade |
| splashback | 1 | kitchen splashback: tiles 0.6 m high from the counter top behind f_L0_031, f_L0_032, f_L0_038 (docs/milestone11.md §1.3 M2; not drawn); cut at the opening(s) o_L0_004, win_L0_002, win_L0_007 | splashback_r_L0_mutfak |
| splashback_cut | 1 | the splashback behind f_L0_031 is cut at the opening(s) o_L0_004 of its wall (a wall finish never covers an opening): 2 piece(s) left | splashback_r_L0_mutfak |
| splashback_cut | 1 | the splashback behind f_L0_032 is cut at the opening(s) win_L0_002, win_L0_007 of its wall (a wall finish never covers an opening): 1 piece(s) left | splashback_r_L0_mutfak |
| stair | 1 | no level above L1: the drawn stair lies over f_L0_001 (100% of the smaller footprint; slab opening sv_L1_001); read as its upper end, not built as a second flight | f_L1_001 |
| stair_finishes | 1 | the house's style family (H8); the documents show the stair in plan only | furn_f_L0_001 |
| suspension | 7 | a hung light is connected to the ceiling over it (28 Oct 2026) | decor_dec_L0_034_cord, decor_dec_L0_053_cord, decor_dec_L0_059_cord |
| thickness | 1 | roof thickness not drawn | roof |
| tree | 6 | medium tree: crown 5.0 m as drawn, 8.0 m tall (height by the crown class, assumed); species stone_pine (inferred) | tree_tree_inferred_3, tree_tree_inferred_4, tree_tree_inferred_5 |
| tree | 2 | small tree: crown 3.5 m as drawn, 5.6 m tall (height by the crown class, assumed); species olive (inferred) | tree_tree_inferred_1, tree_tree_inferred_2 |
| tree:tree_inferred_1 | 1 | no site plan: a tree that frames the windows' view (seen from 5 window(s) (d_L1_005, o_L0_003, o_L0_004, o_L1_005, ...), 5.9 m from the nearest); its crown keeps 2.5 m clear of every window and off their straight view within 6 m; the strict pass placed 0 of 8 (inferred, docs/milestone11.md §1.1 E11; 26 Oct 2026) | site |
| tree:tree_inferred_2 | 1 | no site plan: a tree that frames the windows' view (seen from 4 window(s) (d_L1_010, o_L0_007, win_L1_001, win_L1_011), 6.0 m from the nearest); its crown keeps 2.5 m clear of every window and off their straight view within 6 m; the strict pass placed 0 of 8 (inferred, docs/milestone11.md §1.1 E11; 26 Oct 2026) | site |
| tree:tree_inferred_3 | 1 | the plot leaves no room for 8 trees: a neighbour's tree just beyond the plot edge (seen from 9 window(s) (d_L1_004, o_L0_002, o_L1_003, o_L1_004, ...), 9.1 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_4 | 1 | the plot leaves no room for 8 trees: a neighbour's tree just beyond the plot edge (seen from 8 window(s) (d_L1_010, o_L0_005, o_L0_006, o_L0_007, ...), 9.3 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_5 | 1 | the plot leaves no room for 8 trees: a neighbour's tree just beyond the plot edge (seen from 6 window(s) (d_L1_005, o_L0_003, o_L0_004, o_L1_005, ...), 11.5 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_6 | 1 | the plot leaves no room for 8 trees: a neighbour's tree just beyond the plot edge (seen from 9 window(s) (d_L1_004, o_L0_002, o_L1_003, o_L1_004, ...), 11.4 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_7 | 1 | the plot leaves no room for 8 trees: a neighbour's tree just beyond the plot edge (seen from 9 window(s) (d_L1_004, o_L0_002, o_L1_003, o_L1_004, ...), 12.4 m from the nearest; inferred context, 26 Oct 2026) | site |
| tree:tree_inferred_8 | 1 | the plot leaves no room for 8 trees: a neighbour's tree just beyond the plot edge (seen from 8 window(s) (d_L1_010, o_L0_005, o_L0_006, o_L0_007, ...), 9.3 m from the nearest; inferred context, 26 Oct 2026) | site |
| trees | 1 | inferred trees: placed 8 of 8 (74 candidates; removed by building 1, path 5, sightline 36, window 65, front 27; most by window; the framing pass (the window rule near the facade only) placed 2 of 500 candidates (removed by building 314, path 30, sightline 200, window 337, front 140); the beyond-plot pass (a neighbour's garden) placed 6 of 252 candidates (removed by path 12, sightline 124, front 104); seen from 23 of 28 windows) | site |
| under | 1 | the space under the stair lower than 2.00 m is closed by 4 spandrel panel(s) in its structure finish where no wall closes it (not drawn: assumed, so the stair reads as built from below and the side) | furn_f_L0_001 |
| void_guard | 1 | floor opening 0 of L1 (f_L0_001 comes up through it): a 1.00 m glass posts balustrade on its 2 free edge(s), 1.49 m (not drawn: assumed; the kind follows the style, as the stair's) | void_guard_L1_0 |
| waist | 1 | the house's style (scandinavian: stringer structure, glass panels under a timber handrail, structure strings (glass posts language of the house)); the documents show the stair in plan only | furn_f_L0_001 |
| wall_cabinet_cut | 1 | it would cover win_L0_007 of the building as built (a window or glazed door of its wall) and no wall unit fits beside it: not built | furn_f_L0_046 |
| wall_clear | 1 | over the window o_L1_005 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134) | dec_L1_039 |
| wall_clear | 1 | over the window win_L0_006 of its wall (build): a wall item keeps its width + 0.1 m each side and its height clear of every door, window and frame (UL134); moved to another free wall of the room | dec_L0_005 |
| wall_gap_m | 1 | the drawn shower stands 0.3 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L1_018 |
| wall_gap_m | 3 | the drawn tall_cabinet stands 2.0 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_047, furn_f_L1_037, furn_f_L1_038 |
| wall_gap_m | 3 | the drawn toilet reaches 2.0 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_024, furn_f_L1_021, furn_f_L1_022 |
| wall_gap_m | 1 | the drawn washbasin reaches 2.4 cm into the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L1_027 |
| wall_gap_m | 2 | the drawn washbasin stands 2.1 cm off the wall: its made-to-measure parts (the WC's pan and flush plate, a vanity's back, the shower's fittings) are built on the wall's face; the drawn footprint stays | furn_f_L0_026, furn_f_L1_023 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_005 into r_L0_mutfak, on the latch side, assumed on the side with more free wall (0.73 m against 0.03 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_mutfak_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_005 into r_L0_oda, on the latch side, assumed on the side with more free wall (0.73 m against 0.03 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_oda_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L0_007 into r_L0_banyo, on the latch side, assumed on the side with more free wall (1.31 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L0_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_002 into r_L1_ebeveyn_y_odasi, on the latch side, assumed on the side with more free wall (1.97 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_ebeveyn_y_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_002 into r_L1_oda, on the latch side, assumed on the side with more free wall (0.21 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_oda_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_003 into r_L1_dus, on the latch side, assumed on the side with more free wall (0.76 m against 0.71 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_dus_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_003 into r_L1_soyunma_odasi, on the latch side, assumed on the side with more free wall (0.17 m against 0.10 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_soyunma_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_006 into r_L1_hol, on the latch side, assumed on the side with more free wall (0.84 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_hol_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_006 into r_L1_oda_2, on the latch side, assumed on the side with more free wall (0.54 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_oda_2_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_008 into r_L1_cocuk_odasi, on the latch side, assumed on the side with more free wall (0.59 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_cocuk_odasi_01 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_008 into r_L1_oda, on the latch side, assumed on the side with more free wall (1.31 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_oda_02 |
| wall_plate | 1 | inferred: a light switch beside the door d_L1_009 into r_L1_banyo, on the latch side, assumed on the side with more free wall (0.65 m against 0.01 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_banyo_01 |
| wall_plate | 1 | inferred: a light switch beside the door win_L1_003 into r_L1_ebeveyn_y_odasi, on the latch side, assumed on the side with more free wall (1.81 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_ebeveyn_y_odasi_02 |
| wall_plate | 1 | inferred: a light switch beside the door win_L1_003 into r_L1_soyunma_odasi, on the latch side, assumed on the side with more free wall (0.94 m against 0.00 m; the documents give no hinge side), its centre 0.12 m from the frame, 1.05 m over the floor (a common European height) | plate_r_L1_soyunma_odasi_02 |
| wall_plate | 1 | inferred: a light switch on the wall next to the door d_L1_009 into r_L1_hol, as beside it the wall ends there (a corner or an open side), 0.36 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L1_hol_02 |
| wall_plate | 1 | inferred: a light switch on the wall next to the outside door d_L0_004 (entrance), as beside it the intercom dec_L0_069, 0.07 m from its edge, 1.05 m over the floor (a common European height) | plate_r_L0_salon_01 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 1.24 m, 0.30 m over the floor | plate_r_L0_salon_04 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.34 m, 0.30 m over the floor | plate_r_L0_salon_03 |
| wall_plate | 1 | inferred: a power socket on a free wall stretch of 2.63 m, 0.30 m over the floor | plate_r_L0_salon_02 |
| wall_plate | 1 | inferred: a power socket on the wall nearest the basin f_L0_026 (no mirror hangs over it), as beside it the wall ends there (a corner or an open side), 1.20 m over the floor, outside the bath and shower zone | plate_r_L0_banyo_02 |
| wall_plate | 3 | inferred: a socket pair over the worktop f_L0_031 on the splashback, 0.18 m over its top (1.08 m over the floor), clear of the hob and the sink | plate_r_L0_mutfak_02, plate_r_L0_mutfak_03, plate_r_L0_mutfak_04 |
| wet_walls | 1 | the scandinavian family's bathroom (FAMILY_BATH): large-format stone-look porcelain 60 x 120 cm in light grey on the walls, floor to ceiling (UL114 B8; the brief names no wet-room tiles) | style |
| winders | 1 | the architect's answer (K1): the half landing turned into winders, so the drawn footprint holds comfortable risers | furn_f_L0_001 |
| window_frame | 1 | style profile exterior.window_frame (assumed) | exterior |
| window_group | 1 | o_L0_002 on the facade line of win_L0_004: one composition, sill 0.90 m and head 2.10 m (was 1.25-2.10 m); a fixed lower light to 1.25 m under a transom (its own sill 1.25 m (a bathroom window over the basin: sill 0.90 -> 1.25 m (head kept), clear of the tap; the mirror hangs beside the basin); in front of f_L0_026 (1.08 m)); satin glass in a wet room (privacy from the glass, not a higher sill) (UL210, user: "Big windows next to small windows not making any sense") | o_L0_002 |
| window_group | 1 | o_L1_004 on the facade line of win_L1_007: one composition, sill 0.90 m and head 2.10 m (was 1.25-2.10 m); a fixed lower light to 1.25 m under a transom (its own sill 1.25 m (a bathroom window over the basin: sill 0.90 -> 1.25 m (head kept), clear of the tap; the mirror hangs beside the basin); in front of f_L1_023 (1.08 m)) (UL210, user: "Big windows next to small windows not making any sense") | o_L1_004 |
| window_group | 1 | win_L0_004 on the facade line of o_L0_002: one composition, sill 0.90 m and head 2.10 m (was 0.90-2.10 m); satin glass in a wet room (privacy from the glass, not a higher sill) (UL210, user: "Big windows next to small windows not making any sense") | win_L0_004 |
| window_handles | 2 | design detail of the documented window: a casement window of 1 pane(s), handles on the opening one(s) [0] (1 casement(s) of at most 1.2 m); not in the documents | o_L0_002_handle, o_L1_004_handle |
| window_pier | 1 | win_L0_002: its frame stood 0.12 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.20 m away from the corner and narrowed from its side to 0.64 m (a longer move: it would stand behind f_L0_032 (2.85 m)) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L0_002 |
| window_pier | 1 | win_L0_004: its frame stood 0.00 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): narrowed from the corner side to 1.12 m (the far jamb kept: another opening within 0.10 m; it would stand behind f_L0_026 (1.08 m)) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L0_004 |
| window_pier | 1 | win_L0_005: its frame stood 0.12 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.28 m along its wall away from the corner (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L0_005 |
| window_pier | 1 | win_L1_002: its frame stood 0.00 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): narrowed from the corner side to 1.27 m (the far jamb kept: another opening within 0.10 m) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L1_002 |
| window_pier | 1 | win_L1_007: its frame stood 0.00 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): narrowed from the corner side to 1.12 m (the far jamb kept: another opening within 0.10 m; it would stand behind f_L1_023 (1.08 m)) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L1_007 |
| window_pier | 1 | win_L1_009: its frame stood 0.11 m from its facade's corner (under the 0.40 m of solid wall a corner keeps): moved 0.25 m away from the corner and narrowed from its side to 1.16 m (a longer move: another room or no outside along the new place) (UL211, user: "This window all the way to the edge of a wall not making any sense") | win_L1_009 |
| worktop_slide | 1 | slid along f_L0_032: in front of win_L0_007 of the building as built | dec_L0_041 |

## Rooms mixing polished and Cycles views

None.

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L0_salon (rung None), r_L1_cocuk_odasi (rung None), r_L1_ebeveyn_y_odasi (rung None), r_L1_oda_2 (rung None).

## Commercial-safe per view (Milestone 13)

Licence mode: relaxed (building project.licence_mode). Project: commercial-safe: no (flagged assets: 3dwh_15f0f92bbca84575db8985c5 [non_commercial], 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_7c41f538b2d0873e672fe42f [non_commercial], 3dwh_7df9604e434dddb8c98458ee [non_commercial], 3dwh_905c6949b87e785ec3623cfa [non_commercial], 3dwh_a4a23730e4f99f069784415b [non_commercial], 3dwh_a65d8ba435dfdd6d34187ae9 [non_commercial], 3dwh_add6a04534b77f29e95451d8 [non_commercial], 3dwh_d049478457e41fbd2c0e79eb [non_commercial], 3dwh_f285a27eafb79659b4d63006 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], gen_plant_small_classic_1_08e9f778 [tool_nc], gen_plant_small_mediterranean_1_3691e399 [tool_nc], gen_potted_plant_japandi_3_36d34f2a [tool_nc], gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], gen_potted_plant_modern_1_8fbfec3c [tool_nc], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_0e8dfdbc4db21b620cbc40daebda5f225f48fa1f [non_commercial], hssd_4364e0d4faa0006a6e447b9293fdfbe3c415cfa7 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_68333b64226ceb3585f2355a154a77cfa3276c21 [non_commercial], hssd_7ecec7264a07a6c8759f7f23f1b875079b473b89 [non_commercial], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_b48e86b9315f28d3f5ad9d0d5e16e87b9075b4f6 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial], hssd_d6f9b4561838f68f34d3fc36a7b700bc2c180253 [non_commercial], hssd_dbce8b7313cd8c2c3689cf4083956ba734228e01 [non_commercial], hssd_e4258a74474114a9e2677548124b209cf0f6ae43 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial], hssd_xxxxefdf1c75x32c0x4bfaxada2x48abb454466a [non_commercial]). A view is commercial-safe when no library asset in its object-index pass carries a licence flag (docs/milestone13.md §6).

- cam_r_L0_banyo_1: commercial-safe: no (flagged assets: gen_potted_plant_modern_1_8fbfec3c [tool_nc])
- cam_r_L0_mutfak_1: commercial-safe: no (flagged assets: gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], hssd_68333b64226ceb3585f2355a154a77cfa3276c21 [non_commercial])
- cam_r_L0_mutfak_2: commercial-safe: no (flagged assets: 3dwh_61d3ec6b31b39c2256ef4df4 [non_commercial], 3dwh_a65d8ba435dfdd6d34187ae9 [non_commercial], gen_ceiling_light_japandi_1_200ebd4d [tool_nc], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc], gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], hssd_68333b64226ceb3585f2355a154a77cfa3276c21 [non_commercial])
- cam_r_L0_mutfak_3: commercial-safe: no (flagged assets: hssd_dbce8b7313cd8c2c3689cf4083956ba734228e01 [non_commercial])
- cam_r_L0_salon_1: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a4a23730e4f99f069784415b [non_commercial], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_0e8dfdbc4db21b620cbc40daebda5f225f48fa1f [non_commercial], hssd_4364e0d4faa0006a6e447b9293fdfbe3c415cfa7 [non_commercial], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial], hssd_xxxxefdf1c75x32c0x4bfaxada2x48abb454466a [non_commercial])
- cam_r_L0_salon_2: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a4a23730e4f99f069784415b [non_commercial], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_4364e0d4faa0006a6e447b9293fdfbe3c415cfa7 [non_commercial], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial], hssd_xxxxefdf1c75x32c0x4bfaxada2x48abb454466a [non_commercial])
- cam_r_L0_salon_3: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a4a23730e4f99f069784415b [non_commercial], 3dwh_f285a27eafb79659b4d63006 [non_commercial], gen_potted_plant_scandinavian_2_98f7bbd2 [tool_nc], hssd_0e8dfdbc4db21b620cbc40daebda5f225f48fa1f [non_commercial], hssd_4364e0d4faa0006a6e447b9293fdfbe3c415cfa7 [non_commercial], hssd_5274751529e50c02430fb9b3ee3019ea9c091520 [non_commercial], hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_d5283d7fe8cf91f273d341bf259e1f3df3b349be [non_commercial], hssd_e4258a74474114a9e2677548124b209cf0f6ae43 [non_commercial], hssd_e844128a8ac14233b368655be2b4f14bd4e4098d [non_commercial], hssd_xxxxefdf1c75x32c0x4bfaxada2x48abb454466a [non_commercial])
- cam_r_L1_banyo_1: commercial-safe: no (flagged assets: gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial])
- cam_r_L1_banyo_2: commercial-safe: no (flagged assets: gen_potted_plant_minimal_1_5cf2e7a2 [tool_nc], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial])
- cam_r_L1_cocuk_odasi_1: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_905c6949b87e785ec3623cfa [non_commercial], 3dwh_add6a04534b77f29e95451d8 [non_commercial], 3dwh_d049478457e41fbd2c0e79eb [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_small_mediterranean_1_3691e399 [tool_nc], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial], hssd_d6f9b4561838f68f34d3fc36a7b700bc2c180253 [non_commercial])
- cam_r_L1_cocuk_odasi_2: commercial-safe: no (flagged assets: 3dwh_905c6949b87e785ec3623cfa [non_commercial], 3dwh_add6a04534b77f29e95451d8 [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], gen_plant_small_mediterranean_1_3691e399 [tool_nc], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial], hssd_d6f9b4561838f68f34d3fc36a7b700bc2c180253 [non_commercial])
- cam_r_L1_cocuk_odasi_3: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_905c6949b87e785ec3623cfa [non_commercial], 3dwh_d049478457e41fbd2c0e79eb [non_commercial], gen_books_mediterranean_1_a40f12bd [tool_nc], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d [non_commercial])
- cam_r_L1_dus_1: commercial-safe: yes
- cam_r_L1_dus_2: commercial-safe: no (flagged assets: gen_potted_plant_japandi_3_36d34f2a [tool_nc])
- cam_r_L1_ebeveyn_y_odasi_1: commercial-safe: no (flagged assets: 3dwh_15f0f92bbca84575db8985c5 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a65d8ba435dfdd6d34187ae9 [non_commercial], hssd_7ecec7264a07a6c8759f7f23f1b875079b473b89 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_2: commercial-safe: no (flagged assets: 3dwh_15f0f92bbca84575db8985c5 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a65d8ba435dfdd6d34187ae9 [non_commercial], hssd_02e22ed56270338bef5f8436e82023c36cd29104 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_ebeveyn_y_odasi_3: commercial-safe: no (flagged assets: 3dwh_15f0f92bbca84575db8985c5 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a65d8ba435dfdd6d34187ae9 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_hol_1: commercial-safe: no (flagged assets: gen_plant_small_classic_1_08e9f778 [tool_nc], hssd_b48e86b9315f28d3f5ad9d0d5e16e87b9075b4f6 [non_commercial])
- cam_r_L1_oda_1: commercial-safe: no (flagged assets: 3dwh_15f0f92bbca84575db8985c5 [non_commercial], 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_a65d8ba435dfdd6d34187ae9 [non_commercial], hssd_cb73b8d7a7eba06c5070a71263b39705724e9f7b [non_commercial])
- cam_r_L1_oda_2_1: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial])
- cam_r_L1_oda_2_2: commercial-safe: no (flagged assets: 3dwh_61fbd23bb5e06a5e5f81ebc8 [non_commercial], 3dwh_7df9604e434dddb8c98458ee [non_commercial])
- cam_r_L1_soyunma_odasi_1: commercial-safe: yes
- cam_r_L1_soyunma_odasi_2: commercial-safe: yes
- ext_1: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc])
- ext_2: commercial-safe: yes
- ext_3: commercial-safe: no (flagged assets: gen_plant_large_mediterranean_4_b7e80c9d [tool_nc])
- ext_4: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc])
- ext_5: commercial-safe: no (flagged assets: gen_plant_large_mediterranean_4_b7e80c9d [tool_nc])
- ext_6: commercial-safe: no (flagged assets: 3dwh_7c41f538b2d0873e672fe42f [non_commercial], gen_plant_large_mediterranean_4_b7e80c9d [tool_nc])

## Built below library level (Milestone 13)

27 furniture piece(s) built from a module builder or a parametric family instead of a library model: 5 library gap(s) to close with a real model, 22 made to the drawing by design (kitchen runs, stairs, fixtures; no gap).

| id | type | method | builder | room | room type | source | gap | used |
|---|---|---|---|---|---|---|---|---|
| f_L0_001 | stair | parametric | parametric:stair | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_008 | armchair | parametric | parametric:armchair | r_L0_salon | living | from_documents | yes | parametric family (built below the library level) |
| f_L0_010 | shower | module | bath_set | r_L0_banyo | bathroom | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L0_020 | sink_kitchen | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_021 | table_coffee | parametric | parametric:table_coffee | r_L0_salon | living | from_documents | no (by design) | - |
| f_L0_024 | toilet | parametric | parametric:toilet | r_L0_banyo | bathroom | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L0_026 | washbasin | module | bath_set | r_L0_banyo | bathroom | from_documents | no (by design) | module builder bath_set (stone_slab floating vanity, by design) |
| f_L1_001 | stair | parametric | parametric:stair | r_L1_hol | storage | from_documents | no (by design) | - |
| f_L1_011 | wardrobe | module | module:wardrobe:wardrobe_run | r_L1_soyunma_odasi | storage | from_documents | yes | - |
| f_L1_012 | wardrobe | module | module:wardrobe:wardrobe_run | r_L1_soyunma_odasi | storage | from_documents | yes | - |
| f_L1_018 | shower | module | bath_set | r_L1_dus | storage | from_documents | no (by design) | module builder bath_set (walk-in shower, by design) |
| f_L1_021 | toilet | parametric | parametric:toilet | r_L1_dus | storage | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L1_022 | toilet | parametric | parametric:toilet | r_L1_banyo | storage | from_documents | no (by design) | our parametric wall-hung WC with its flush plate (by design) |
| f_L1_023 | washbasin | module | bath_set | r_L1_banyo | storage | from_documents | no (by design) | module builder bath_set (stone_slab floating vanity, by design) |
| f_L1_025 | nightstand | parametric | parametric:nightstand | r_L1_oda_2 | storage | from_documents | no (by design) | - |
| f_L1_027 | washbasin | module | bath_set | r_L1_dus | storage | from_documents | no (by design) | module builder bath_set (stone_slab floating vanity, by design) |
| f_L0_031 | kitchen_counter | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_032 | kitchen_counter | module | kitchen_run | r_L0_mutfak | kitchen | from_documents | no (by design) | - |
| f_L0_038 | stove | module | kitchen_run | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_042 | kitchen_island | module | kitchen_run | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_045 | wall_cabinet | module | wall_run | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_046 | wall_cabinet | module | wall_run | r_L0_mutfak | kitchen | added_by_ai | no (by design) | - |
| f_L0_047 | tall_cabinet | parametric | parametric:tall_cabinet | r_L0_banyo | bathroom | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L1_037 | tall_cabinet | parametric | parametric:tall_cabinet | r_L1_dus | storage | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L1_038 | tall_cabinet | parametric | parametric:tall_cabinet | r_L1_banyo | storage | added_by_ai | no (by design) | our parametric open lit niche column (by design) |
| f_L0_048 | sofa | parametric | parametric:sofa | - | - | added_by_ai | yes | parametric family in weather-proof materials (a teak frame with outdoor cushions) |
| f_L0_049 | table_coffee | parametric | parametric:table_coffee | - | - | added_by_ai | yes | parametric family in weather-proof materials (a teak top on brushed steel legs) |

## Views too dark for the EV cap (Milestone 13)

0 view(s) whose metered exposure passed the cap +3.00 EV (0 critical, 0 major: critical from 2 stops over). The render keeps the cap, so the room shows darker than metered; the agent's set_lighting raises the room's lights (docs/milestone13.md §14.3).

Views that look into the sun (their sky may stay white whatever the sky pull; a project decision on the sun azimuth or the camera, docs/milestone13.md §14.10): ext_2 (10.4 degrees off the sun, sky pull k 3).

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
| recognition pass 1 | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | recognition/requests.json (41 of 41 answered) |
| recognition pass 2 | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | recognition/requests.json (41 of 41 answered) |

Assets: textures CC0 x 46; furniture/decor models 3DWH-UNREVIEWED x 31, CC-BY-4.0 x 34, CC-BY-NC-4.0 x 32, CC0 x 1, generated (TRELLIS.2-4B, MIT) x 14 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

No view of this run was AI-retouched (0 of 29 views polished), so the change "AI-retouched" of the catalogue's credit texts is left out.

- "book pile ( no memes)" by Renee Beenen (https://sketchfab.com/3d-models/4655f87dfe2e47aa8ecd3ddc2443c240), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_011)
- "Candles" by thegraphicsgeek (https://sketchfab.com/3d-models/92bb9f59fd9046b1beb9dca6b21489e2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L0_064)
- "Childhood books" by riemaeker (https://sketchfab.com/3d-models/99d6bc041c9d4f56ab414b771e14474c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered (used for dec_L1_040)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261030-224530-full-20261030T225014Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 25.6 s | - |
| pipeline | pending | 36.0 s | 31 recognition question(s) written (recognition/requests.json) |
| recognize | reused | 1.8 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.3 s | - |
| pipeline_final | ok | 36.9 s | answers applied |
| fit | ok | 7.8 s | - |
| layout | ok | 22.4 s | - |
| decor_ask | ok | 2.5 min | - |
| assets | ok | 6.2 s | - |
| decor | ok | 27.6 s | - |
| agent_apply | ok | 38.1 s | - |
| refit | ok | 73.3 s | - |
| build | ok | 27.2 min | - |
| agent_previews | ok | 6.4 min | 3 view(s) |
| agent | ok | 39.8 min | 5 round(s), 32 finding(s) removed by 59 accepted edit(s) (measured; 131 predicted by the dry re-checks), 0 new, net 32, 180 rejected; stop: max rounds reached; final round for critical findings done |
| render | ok | 19.6 min | - |
| controls | ok | 2.6 min | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 2.4 min | - |
| check | ok | 5.3 min | - |
| export | ok | 2.2 min | - |
| combine | ok | 24.5 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 5 round(s), 59 edit(s) accepted, 180 rejected, 539 model calls (6433661 tokens), 46.8 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

This run only (log events from seq 12448): earlier runs of the appended log are left out (12447 events, 3630 model calls, 349 stored edits); `orchestrator/log.md` has them.

### Agent metrics

| metric | value |
|---|---|
| edits accepted / rejected | 59 / 180 (25 % accepted) |
| rejected by reason | memory 32, acceptance 30, no_change 15, no_place 14, max_tries 13 |
| rooms checked by code / vision / planner | 12 / 11 / 13 |
| rooms with fixable critical or major findings visited | 13 of 13 |
| critical before -> after (after: round 6's critics, before its 5 accepted edit(s)) | 9 -> 16 |
| major before -> after (after: round 6's critics, before its 5 accepted edit(s)) | 159 -> 366 |
| agent minutes; first accepted edit after | 50.46; 4.0 s |
| repeats refused by the memory; dry runs; plans (valid) | 32; 57; 63 (27) |
| critical/major findings removed in rounds 1-4 (measured by the next round; predicted by the dry re-checks of the same rounds) | 32 measured; 131 predicted (the last round's dry re-checks predicted 21 more, not measured) |
| new critical/major findings in rounds 1-4; net removed (gone - new) | 68 new; net -36 |
| edits removing their finding | 3 of 46 |
| plans ok / empty / refused / default | 27 / 31 / 5 / 0 |

### What the AI inspector saw on the final renders

393 vision finding(s) (35 of the visitor checks Q1-Q9: doors, working heights, falls, rooms that make no sense, pieces that clash, doors and windows, rain water): 31 fixed in the final round, 14 handed to the stage that owns them, 381 open; the architect leaves 7 major open point(s). Every finding with its outcome: `orchestrator/inspector.md`.

Still open or handed on (critical and major):

- major Q12 f_L0_026: The washbasin is placed directly under a window, which is a poor design choice as it prevents the installation of a mirror and creates a ris (open: a tool exists (complete_group, place_group, relayout_room) but no edit was accepted)
- major Q4 f_L0_024: missing anchor: the room is missing the toilet (f_L0_024), which is a primary fixture for a bathroom. Its absence makes the space feel incom (open: a tool exists (retype_piece, mark_not_furniture, remove_piece) but no edit was accep)
- major D3 r_L0_mutfak: missing layer: styled surfaces (the dining table is completely bare, lacking the plates, glasses, or centerpiece that would make it feel liv (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: wall art (the large blank wall to the left is stark and needs a frame or mirror to balance the space) (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: rug. The reference shows a patterned rug anchoring the seating area; the render has bare, reflective tile throughout, which m (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: wall art. The reference uses framed art to add personality to the white walls. The render's walls are completely empty, contr (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: styled surfaces. The reference kitchen has a kettle, utensils, and other small items on the counter. The render's island (f_L (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: wall art. The large blank wall above the counter is completely empty, whereas the reference style uses framed art to define t (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: plants. There is no greenery anywhere in the room, making it feel sterile compared to the reference. (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: styled surfaces. The worktops are almost entirely bare. A kitchen needs a kettle, a bowl of fruit, or a cutting board to look (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: rug. The floor is a single expanse of tile with no softening element, which is a step down from the reference's layered floor (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_mutfak: missing layer: warm light. The scene is lit by harsh, direct sunlight with no visible warm artificial lighting (like a pendant over the isla (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L0_016: mismatched_set: the dark navy wingback armchair is a completely different style and colour family from the beige sofa and the patterned armc (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 r_L0_salon: missing layer: feature wall: the wall behind the main sofa is a flat, untextured paint colour, lacking the vertical wood panelling or wainsc (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_salon: missing layer: styled surfaces: there is no console, coffee table, or shelf with any styling (books, vases, art prints), leaving the room fe (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_salon: missing layer: light layers: the room is lit only by flat daylight; it lacks the warm, layered lighting (statement fixture, table lamps, dow (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_salon: missing layer: wall art: the large expanse of wall is completely bare, missing the frames and prints that would add personality and scale. (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L0_016: mismatched_set: the dark, angular armchair with the loud red-striped cushion clashes with the light, neutral palette and the other furniture (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L0_006: mismatched_set: the curved beige sofa is a different design language from the boxy cream armchair and the mid-century daybed, making the sea (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 r_L0_salon: missing layer: feature wall; the walls are a flat, untextured paint color, lacking the slatted wood or paneling that defines the project's s (open: a tool exists (swap_model) but no edit was accepted)
- major D3 r_L0_salon: missing layer: wall art; the large wall space above the seating is completely empty, unlike the styled shelves and frames in the reference. (open: a tool exists (swap_model) but no edit was accepted)
- major D3 f_L0_021: missing layer: styled surfaces; the coffee table is completely bare, lacking the books, vases, and decor that would make the room feel lived (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L0_011: mismatched_set: The dining table and chairs (f_L0_011, f_L0_027-030) are a stark, modern set that clashes completely with the soft, neutral, (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 f_L0_006: not_stylish: The sofa (f_L0_006) and the surrounding armchairs are generic and lack the tailored, high-end look of the reference. The combin (open: a tool exists (swap_model, report_library_gap) but no edit was accepted)
- major D3 r_L0_salon: missing layer: wall art. The large, blank walls are a major flaw. The reference shows a styled wall with a shelf, art, and greenery. This re (open: a tool exists (swap_model) but no edit was accepted)

### Argus, the auditor

Score 5.4 / 100 (100 = nothing open): 12 critical, 243 major, 65 minor open. By kind (critical + major): geometry 30, stale 8, taste 79, no_sense 33, detached 4, misread 35, other 23, process 16, lost 14, silent 9, reference_missed 4. Every finding with its kind, owner and fix: `orchestrator/argus.md`.

Critical:

- geometry d_L0_004: no 0.60 m walkway from door d_L0_004 to door d_L0_006
- geometry f_L1_007: bed_double blocks door d_L1_011
- geometry f_L1_011: wardrobe blocks door win_L1_003
- geometry d_L1_003: no 0.60 m walkway from door d_L1_003 to door win_L1_003
- geometry d_L1_006: no 0.60 m walkway from door d_L1_006 to door d_L1_009
- geometry o_L1_002: no 0.60 m walkway from door o_L1_002 to door d_L1_009
- no_sense d_L1_010: door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air)
- detached dec_L0_041: utensil_pot dec_L0_041 on kitchen_counter f_L0_032: 0% of the footprint over the support < 80%
- taste cam_r_L1_soyunma_odasi_1: Argus: Argus: bad_camera: The camera is pressed against a wall/corner, showing only a flat brown surface and the edge of a wardrobe. The room's main group (the 
- stale G11: 10 elements: the critic finds G11 on 10 element(s) (d_L0_004, f_L0_016, f_L0_019, d_L1_002, d_L1_007, f_L1_004 ...; e.g. no 0.60 m walkway from door d_L0_004 to door d_L0_00
- stale F7: 2 elements: the critic finds F7 on 2 element(s) (d_L1_011, win_L1_003; e.g. bed_double blocks door d_L1_011) and the architect's rule F2 / F3 says they are fine: the rule n
- stale d_L1_010: the critic finds X3 on 1 element(s) (d_L1_010; e.g. door d_L1_010 is 3.50 m above the ground with nothing to reach it (a door into the air)) and the architect's

Library gaps reported by the agent: tall_cabinet (tall_cabinet f_L1_037 (added_by_ai) was built below the library level with a parametric mesh; no audited library model fits, so the gap is recorded for review.), toilet (toilet f_L1_021 floats +0.200 m above its floor (wrong model base); as drawn fixed equipment it cannot be swapped, so the gap is recorded for review.), washbasin (washbasin f_L1_027 floats +0.314 m above its floor (wrong model base); as drawn fixed equipment it cannot be swapped, so the gap is recorded for review.), washbasin (No audited library washbasin model with an integrated mirror fits the drawn 0.53x0.34 hung basin over window o_L0_002; the missing mirror (D3, M26) cannot be added by any allowed tool.), tall_cabinet (tall_cabinet f_L1_038 (added_by_ai) was built as a parametric mesh below library level; the only real-model swap (abo_B07RMJPJMX) was rejected as a no-op pin, so no audited library model of this type/size exists.), toilet (toilet f_L1_022 (drawn fixed equipment) has a model whose lowest point floats +0.200 m off its floor (allowed -0.005..+0.01 m); no audited library model of this type fits, so the gap is recorded for review.), washbasin (washbasin f_L1_023 (drawn fixed equipment) has a model whose lowest point floats +0.314 m off its floor (allowed -0.005..+0.01 m); no audited library model of this type fits, so the gap is recorded for review.), kitchen_island (No audited library model of a kitchen_island exists, so the bare worktop/island styling (a:D3) cannot be fixed by a model swap.).

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 9 | 159 | 34 | 20 | 21 | 68 | layout | 17 |
| 2 | 9 | 151 | 38 | 22 | 17 | 36 | layout | 29 |
| 3 | 9 | 151 | 41 | 21 | 2 | 20 | layout | 3 |
| 4 | 9 | 320 | 82 | 33 | 14 | 24 | refit | 29 |
| 6 | 16 | 366 | 76 | 32 | 5 | 32 | refit | 5 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| A10 | 0 | 0 | 0 | 1 |
| A6 | 0 | 1 | 0 | 0 |
| AI1 | 0 | 61 | 0 | 40 |
| AI2 | 0 | 23 | 0 | 7 |
| AI3 | 0 | 4 | 0 | 0 |
| AI5 | 0 | 48 | 0 | 0 |
| C1 | 0 | 0 | 0 | 1 |
| C3 | 0 | 0 | 0 | 1 |
| C6 | 0 | 46 | 0 | 5 |
| C7 | 0 | 7 | 0 | 0 |
| D2 | 0 | 5 | 0 | 2 |
| D3 | 0 | 344 | 88 | 0 |
| F1 | 0 | 0 | 10 | 0 |
| F3 | 0 | 11 | 0 | 0 |
| F4 | 0 | 5 | 0 | 0 |
| F6 | 0 | 12 | 0 | 0 |
| F7 | 12 | 0 | 0 | 0 |
| F9 | 0 | 18 | 0 | 1 |
| G1 | 0 | 0 | 10 | 0 |
| G10 | 0 | 18 | 0 | 0 |
| G11 | 24 | 33 | 0 | 0 |
| G12 | 0 | 11 | 0 | 0 |
| G14 | 0 | 0 | 10 | 0 |
| G2 | 0 | 6 | 5 | 0 |
| G3 | 0 | 24 | 0 | 0 |
| G4 | 0 | 5 | 11 | 0 |
| G5 | 0 | 20 | 0 | 0 |
| G6 | 0 | 0 | 5 | 0 |
| G8 | 0 | 5 | 0 | 0 |
| G9 | 0 | 5 | 0 | 0 |
| J1 | 0 | 75 | 0 | 56 |
| K1 | 0 | 23 | 0 | 0 |
| K3 | 0 | 15 | 0 | 0 |
| K4 | 0 | 0 | 0 | 2 |
| L2 | 0 | 5 | 0 | 0 |
| LG | 0 | 0 | 15 | 0 |
| M10 | 0 | 0 | 10 | 0 |
| M17 | 0 | 0 | 2 | 0 |
| M19 | 0 | 10 | 0 | 0 |
| M21 | 0 | 0 | 23 | 0 |
| M26 | 0 | 0 | 5 | 0 |
| M28 | 0 | 0 | 1 | 0 |
| M32 | 0 | 48 | 0 | 0 |
| M33 | 0 | 14 | 0 | 0 |
| N5 | 0 | 7 | 0 | 0 |
| NR | 0 | 11 | 0 | 0 |
| P0 | 0 | 12 | 0 | 0 |
| P5 | 0 | 0 | 0 | 6 |
| P7 | 0 | 38 | 0 | 0 |
| P9 | 0 | 0 | 0 | 6 |
| Q12 | 0 | 10 | 2 | 0 |
| Q13 | 0 | 0 | 4 | 0 |
| Q14 | 0 | 2 | 3 | 0 |
| Q15 | 0 | 0 | 1 | 0 |
| Q4 | 0 | 47 | 1 | 0 |
| Q5 | 0 | 4 | 2 | 0 |
| Q7 | 0 | 5 | 3 | 0 |
| RC | 0 | 0 | 5 | 0 |
| S1 | 0 | 33 | 0 | 0 |
| S2 | 0 | 16 | 0 | 0 |
| S4 | 0 | 0 | 5 | 0 |
| S5 | 6 | 0 | 14 | 0 |
| S6 | 0 | 11 | 0 | 0 |
| U10 | 0 | 14 | 0 | 0 |
| V1 | 5 | 34 | 6 | 0 |
| X3 | 5 | 0 | 0 | 0 |
| X5 | 0 | 0 | 30 | 0 |
| lighting_dark | 0 | 1 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 12699 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The room's only furniture is the wardrobe; the camera is pressed against a wall showing a flat surface. The place_group refusal (no place for a dressing group) is a separate layout issue, but the camera can be fixed now to show the room's a (fixes a:F1) | - | - |
| 12701 | 1 | swap_model | f_L0_034 | added_by_ai | 0.0 -> 0.0 | Argus: The bookshelf was removed by the AI, but the documents show it in the salon. The current model is not built. Swapping to a valid library model (hssd_897e7615d4488fca5aeb35c34e037b6615388b44, 1.00 x 0.34 x 1.80 m) will rebuild the piece. (fixes a:F22) | ![](agent/r1_001_swap_model_before_r_L0_salon.png) | ![](agent/r1_002_swap_model_after_r_L0_salon.png) |
| 12702 | 1 | swap_model | f_L0_037 | added_by_ai | 0.0 -> 0.0 | Argus: The dining table was removed by the AI, but the documents show it in the kitchen. The current model is not built. Swapping to a valid library model (hssd_5b8a27a3c3098b93e3b9c16c7f58c9aace0a073c, 0.50 x 0.50 x 0.50 m) will rebuild the piece (fixes a:F23) | ![](agent/r1_003_swap_model_before_r_L0_salon.png) | ![](agent/r1_004_swap_model_after_r_L0_salon.png) |
| 12703 | 1 | set_camera | r_L0_banyo | agent_override | - | Argus: The toilet is present in the model but not visible in the render. Moving the camera to show the toilet fixes the render without touching the geometry. (fixes a:F29) | - | - |
| 12704 | 1 | set_camera | r_L1_dus | agent_override | - | Argus: The shower is present in the model but not visible in the render. Moving the camera to show the shower fixes the render without touching the geometry. (fixes a:F31) | - | - |
| 12710 | 1 | set_camera | r_L1_oda | agent_override | - | Argus: The camera is positioned too low and too close to the corner, resulting in a cramped view that cuts off the ceiling and fails to show the room's layout or scale. Moving the camera to show the shoe_cabinet (f_L1_014) and the door (d_L1_002)  (fixes a:F92) | - | - |
| 12714 | 1 | set_camera | r_L1_hol | agent_override | - | Argus: The judge sees a failed close-up of a corner; the stair and shoe cabinet are not visible. Repointing the camera at them fixes it. (fixes a:F117) | - | - |
| 12716 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The judge sees a close-up of a corner, a flat untextured brown wall and the edge of a wardrobe; the room is not visible. Repointing the camera at the wardrobe fixes it. (fixes a:F126) | - | - |
| 12719 | 1 | set_room_type | r_L0_oda | adjusted_by_ai | 100.0 -> 100.0 | Argus: The room 'r_L0_oda' is typed as 'hall' but has an area of only 2.1 m² and no pieces. A 2.1 m² hall is functionally non-existent. Retyping it as 'storage' is more appropriate for such a small space. (fixes a:F135) | ![](agent/r1_011_set_room_type_before_r_L0_oda.png) | ![](agent/r1_012_set_room_type_after_r_L0_oda.png) |
| 12723 | 1 | swap_model | f_L1_029 | added_by_ai | 70.0 -> 70.0 | Argus: The desk f_L1_029 is not present, so the room lacks the work/styled-surface layer the reference sets. Swapping to a real library model abo_B0876NZQ9C (1.02 x 0.51 x 0.76 m, scandinavian/modern minimal) should work as it fits the size and st (fixes a:F156) | ![](agent/r1_016_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r1_017_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 12728 | 1 | swap_model | f_L1_015 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The two armchairs are different models/colours; swapping f_L1_015 to the modern abo_B075X2WN36 (0.85 x 0.78 x 0.89 m) aligns the pair. (fixes a:F201) | ![](agent/r1_022_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r1_023_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 12740 | 1 | move_piece | f_L1_014 | adjusted_by_ai | 0.0 -> 0.0 | Shift wardrobe 0.05 m in -x so its back edge clears wall w_L1_024 and the room outline (F9/S2). | ![](agent/r1_061_move_piece_before_r_L1_oda_2.png) | ![](agent/r1_063_move_piece_after_r_L1_oda_2.png) |
| 12758 | 1 | set_lighting | r_L0_banyo | agent_override | - | View cam_r_L0_banyo_1 is 0.19 stops over the EV cap; the finding names x1.61 to bring incident light to target. | - | - |
| 12763 | 1 | report_library_gap | f_L1_037 | library_gap | - | tall_cabinet f_L1_037 (added_by_ai) was built below the library level with a parametric mesh; no audited library model fits, so the gap is recorded for review. | - | - |
| 12766 | 1 | report_library_gap | f_L1_021 | library_gap | - | toilet f_L1_021 floats +0.200 m above its floor (wrong model base); as drawn fixed equipment it cannot be swapped, so the gap is recorded for review. | - | - |
| 12768 | 1 | report_library_gap | f_L1_027 | library_gap | - | washbasin f_L1_027 floats +0.314 m above its floor (wrong model base); as drawn fixed equipment it cannot be swapped, so the gap is recorded for review. | - | - |
| 12773 | 1 | swap_model | f_L1_016 | adjusted_by_ai | 70.0 -> 70.0 | Match the second armchair to the first (same model) so the seating pair reads as a cohesive set (D3). | ![](agent/r1_083_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r1_087_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 12775 | 1 | relayout_room | r_L1_oda | adjusted_by_ai | 100.0 -> 100.0 | Argus says the storage room is missing its main storage furniture; relayout with the best solver candidate to add it. | ![](agent/r1_085_relayout_room_before_r_L1_oda.png) | ![](agent/r1_086_relayout_room_after_r_L1_oda.png) |
| 12776 | 1 | set_camera | r_L1_soyunma_odasi | agent_override | - | Camera is pressed against a wall showing only a wardrobe edge; reposition to a free point with headroom so the dressing group is in frame. | - | - |
| 12786 | 1 | set_camera | r_L1_dus | agent_override | - | Camera shows a blank wall and floating slab; reposition to a free point with headroom so shower, toilet and washbasin are visible. | - | - |
| 12797 | 1 | move_piece | f_L1_005 | adjusted_by_ai | 0.0 -> 0.0 | Shift dresser 0.26 m down to clear the overlap with bed f_L1_004. | ![](agent/r1_105_move_piece_before_r_L1_cocuk_odasi.png) | ![](agent/r1_107_move_piece_after_r_L1_cocuk_odasi.png) |
| 13075 | 2 | swap_model | f_L1_020 | adjusted_by_ai | 70.0 -> 70.0 | Argus: The current lamp is a dated style; the 0.40 x 0.40 x 1.62 m minimal/modern lamp fits the footprint and the room's look. (fixes a:F202) | ![](agent/r2_001_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r2_002_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 13076 | 2 | swap_model | f_L1_034 | added_by_ai | 0.0 -> 0.0 | Argus: The current model is a bright orange wood that clashes; the 0.60 x 0.61 x 0.91 m minimal/modern model fits the 0.60 x 0.60 m footprint and the palette. (fixes a:F203) | ![](agent/r2_003_swap_model_before_r_L1_cocuk_odasi.png) | ![](agent/r2_004_swap_model_after_r_L1_cocuk_odasi.png) |
| 13078 | 2 | swap_model | f_L0_037 | added_by_ai | 0.0 -> 0.0 | Argus: The ottoman was removed by AI but is still drawn. The previous move was refused due to overlap. Swapping to a different model (abo_B082QDJLSP, 0.50 x 0.50 x 0.41 m) may allow the builder to find a valid placement or at least re-engage the b (fixes a:F229) | ![](agent/r2_006_swap_model_before_r_L0_salon.png) | ![](agent/r2_007_swap_model_after_r_L0_salon.png) |
| 13082 | 2 | swap_model | f_L1_031 | added_by_ai | 70.0 -> 70.0 | Argus: The floor lamp was removed by AI but is still drawn. The previous swap was refused because the model failed fit rules. The new model hssd_7ecec7264a07a6c8759f7f23f1b875079b473b89 (0.40 x 0.40 x 1.62 m) is a standard floor lamp size and shou (fixes a:F238) | ![](agent/r2_010_swap_model_before_r_L1_ebeveyn_y_odasi.png) | ![](agent/r2_011_swap_model_after_r_L1_ebeveyn_y_odasi.png) |
| 13094 | 2 | place_group | r_L0_salon | added_by_ai | 0.0 -> 0.0 | Argus: lesson (lesson:UL99:L0): No television is listed in any room (salon, bedrooms) and none is visible in the renders; the house has no TV. (fixes a:N69) | ![](agent/r2_021_place_group_before_r_L0_salon.png) | ![](agent/r2_022_place_group_after_r_L0_salon.png) |
| 13096 | 2 | set_exterior | exterior:site | agent_override | - | Argus: lesson (lesson:UL04): The garden is only a flat green lawn with a few scattered trees and a low hedge; there is no planting, no hedge line, no path and no car where one belongs. (fixes a:N74) | - | - |
| 13097 | 2 | set_exterior | exterior:site | agent_override | - | Argus: lesson (lesson:UL172): The house stands alone on an empty lawn with no fenced neighbouring plots and no roads coming to it from outside (ext_1..ext_4); the site is bare grass to the horizon. (fixes a:N76) | - | - |
| 13101 | 2 | set_material | wet_walls | agent_override | - | Argus: The walls are flat beige panels instead of the reference's wood cladding. Setting the wet_walls slot to a wood cladding look adds the missing warm wood layer. (fixes a:F106) | - | - |
| 13121 | 2 | report_library_gap | f_L0_026 | library_gap | - | No audited library washbasin model with an integrated mirror fits the drawn 0.53x0.34 hung basin over window o_L0_002; the missing mirror (D3, M26) cannot be added by any allowed tool. | - | - |
| 13134 | 2 | report_library_gap | f_L1_038 | library_gap | - | tall_cabinet f_L1_038 (added_by_ai) was built as a parametric mesh below library level; the only real-model swap (abo_B07RMJPJMX) was rejected as a no-op pin, so no audited library model of this type/size exists. | - | - |
| 13136 | 2 | report_library_gap | f_L1_022 | library_gap | - | toilet f_L1_022 (drawn fixed equipment) has a model whose lowest point floats +0.200 m off its floor (allowed -0.005..+0.01 m); no audited library model of this type fits, so the gap is recorded for review. | - | - |
| 13137 | 2 | report_library_gap | f_L1_023 | library_gap | - | washbasin f_L1_023 (drawn fixed equipment) has a model whose lowest point floats +0.314 m off its floor (allowed -0.005..+0.01 m); no audited library model of this type fits, so the gap is recorded for review. | - | - |
| 13141 | 2 | relayout_room | r_L1_cocuk_odasi | adjusted_by_ai | 0.0 -> 0.0 | Re-solve the room to fix bed f_L1_007 blocking door d_L1_011, cutting wall w_L1_004, and clearance issues | ![](agent/r2_091_relayout_room_before_r_L1_cocuk_odasi.png) | ![](agent/r2_093_relayout_room_after_r_L1_cocuk_odasi.png) |
| 13142 | 2 | report_library_gap | f_L0_042 | library_gap | - | No audited library model of a kitchen_island exists, so the bare worktop/island styling (a:D3) cannot be fixed by a model swap. | - | - |
| 13143 | 2 | relayout_room | r_L1_oda | adjusted_by_ai | 100.0 -> 100.0 | Candidate 1 was already tried and the missing-storage finding persists; trying candidate 2 to see if a different layout resolves it. | ![](agent/r2_092_relayout_room_before_r_L1_oda.png) | ![](agent/r2_094_relayout_room_after_r_L1_oda.png) |
| 13157 | 2 | swap_model | f_L1_011 | adjusted_by_ai | 70.0 -> 70.0 | Replace the parametric wardrobe with a real library model (WARDROBE 2.34x0.62) to fix S6 and add styled surfaces for the dressing room. | ![](agent/r2_104_swap_model_before_r_L1_soyunma_odasi.png) | ![](agent/r2_105_swap_model_after_r_L1_soyunma_odasi.png) |
| 13158 | 2 | swap_model | f_L1_012 | adjusted_by_ai | 70.0 -> 70.0 | Replace the parametric wardrobe with a real library model (WARDROBE 2.34x0.62) to fix S6. | ![](agent/r2_106_swap_model_before_r_L1_soyunma_odasi.png) | ![](agent/r2_107_swap_model_after_r_L1_soyunma_odasi.png) |
| 13472 | 3 | resize_piece | f_L1_012 | adjusted_by_ai | 70.0 -> 70.0 | Bring wardrobe f_L1_012 height back into the 1.50-2.45 m range (S4) by resizing to a real wardrobe size. | ![](agent/r3_039_resize_piece_before_r_L1_soyunma_odasi.png) | ![](agent/r3_041_resize_piece_after_r_L1_soyunma_odasi.png) |
| 13488 | 3 | relayout_room | r_L1_oda | adjusted_by_ai | 100.0 -> 100.0 | Try the untried solver candidate 3 to address the missing main storage furniture (a:F150). | ![](agent/r3_048_relayout_room_before_r_L1_oda.png) | ![](agent/r3_051_relayout_room_after_r_L1_oda.png) |
| 13995 | 4 | set_camera | r_L1_banyo | agent_override | - | Argus: The toilet and washing machine are in the model but not visible in the render; re-aiming the camera to show them is the direct fix. (fixes a:F29) | - | - |
| 13997 | 4 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: The wardrobes are in the model but not visible in the render (blocked by a louvered screen); re-aiming the camera to a free pose that shows them is the direct fix. (fixes a:F32) | - | - |
| 13998 | 4 | set_exterior | exterior:site | agent_override | - | Argus: The garden is bare flat grass with a few generic trees and a hedge line; no planted beds, shrubs or ground cover. (fixes a:F62) | - | - |
| 14000 | 4 | set_camera | r_L0_banyo | agent_override | - | Argus: The camera currently shows the toilet and shower but excludes the vanity. A client needs to see the sink and mirror to judge the bathroom design. Re-aiming the camera to show the washbasin fixes the framing. (fixes a:F84) | - | - |
| 14001 | 4 | swap_model | f_L0_040 | added_by_ai | 57.0 -> 57.0 | Argus: The dark heavy wood chair clashes with the light oak table and pale modern kitchen. Swapping to a minimal/modern/scandinavian chair (0.44 x 0.42 m) matches the room's style. (fixes a:F86) | ![](agent/r4_001_swap_model_before_r_L0_mutfak.png) | ![](agent/r4_002_swap_model_after_r_L0_mutfak.png) |
| 14002 | 4 | swap_model | f_L0_016 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The dark angular armchair clashes with the warm neutral palette. Swapping to a minimal/modern/scandinavian armchair (0.91 x 0.76 m) matches the room's style. (fixes a:F88) | ![](agent/r4_003_swap_model_before_r_L0_salon.png) | ![](agent/r4_004_swap_model_after_r_L0_salon.png) |
| 14003 | 4 | swap_model | f_L0_006 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The cognac leather sofa is 70s style and does not match the modern Scandinavian feel. Swapping to a modern/scandinavian sofa (2.13 x 0.86 m) matches the project's reference style. (fixes a:F89) | ![](agent/r4_005_swap_model_before_r_L0_salon.png) | ![](agent/r4_006_swap_model_after_r_L0_salon.png) |
| 14004 | 4 | swap_model | f_L0_014 | adjusted_by_ai | 0.0 -> 0.0 | Argus: The terracotta leather sofa clashes with the other seating. Swapping to a modern/scandinavian sofa (1.52 x 0.87 m) creates a cohesive set. (fixes a:F90) | ![](agent/r4_007_swap_model_before_r_L0_salon.png) | ![](agent/r4_008_swap_model_after_r_L0_salon.png) |
| 14006 | 4 | swap_model | f_L1_042 | added_by_ai | 0.0 -> 0.0 | Argus: The black leather office chair (model 3dwh_2be96519caebb57579ea6e05) clashes with the child's bedroom. Swapping to the scandinavian/minimal model hssd_d6f9b4561838f68f34d3fc36a7b700bc2c180253 (0.60 x 0.61 x 0.75 m) keeps the office_chair ty (fixes a:F99) | ![](agent/r4_010_swap_model_before_r_L1_cocuk_odasi.png) | ![](agent/r4_011_swap_model_after_r_L1_cocuk_odasi.png) |
| 14008 | 4 | set_camera | r_L1_cocuk_odasi | agent_override | - | Argus: The judge says the render shows only a desk, wardrobe and a bare wall; the two beds (f_L1_004, f_L1_007) are missing from the frame. Re-aiming the camera to show the beds and main furniture fixes the framing. (fixes a:F104) | - | - |
| 14010 | 4 | set_material | door | agent_override | - | Argus: The dark door leaf is a material mismatch, not a geometry or layout error; a painted light finish restores the cohesive palette. (fixes a:F113) | - | - |
| 14011 | 4 | set_camera | r_L1_hol | agent_override | - | Argus: The current view is a flat wall shot; re-aiming it at the hall's furniture shows the space. (fixes a:F114) | - | - |
| 14012 | 4 | set_camera | r_L1_oda | agent_override | - | Argus: The camera is too close to the console table, blocking the hall view; re-aiming it to show the console and the door from a free point fixes the framing. (fixes a:F116) | - | - |
| 14018 | 4 | set_material | facade | agent_override | - | Argus: The facade is a flat grey-box; setting the facade slot to the style's render finish adds material richness. (fixes a:F127) | - | - |
| 14606 | 6 | set_camera | r_L1_soyunma_odasi | agent_override | - | Argus: the camera is pressed against a wall; it must be moved to show the wardrobe (fixes a:F12) | - | - |
| 14610 | 6 | swap_model | f_L0_034 | added_by_ai | 0.0 -> 0.0 | Argus: Bookshelf f_L0_034 is not built; swapping to a valid model should resolve the build issue. (fixes a:F45) | ![](agent/r6_001_swap_model_before_r_L0_salon.png) | ![](agent/r6_002_swap_model_after_r_L0_salon.png) |
| 14611 | 6 | swap_model | f_L0_035 | added_by_ai | 0.0 -> 0.0 | Argus: Potted plant f_L0_035 is not built; previous swaps were refused for fit rules, so a different model with compatible dimensions is needed. (fixes a:F46) | ![](agent/r6_003_swap_model_before_r_L0_salon.png) | ![](agent/r6_004_swap_model_after_r_L0_salon.png) |
| 14612 | 6 | swap_model | f_L0_037 | added_by_ai | 0.0 -> 0.0 | Argus: Ottoman f_L0_037 is not built; swapping to a valid model should resolve the build issue. (fixes a:F47) | ![](agent/r6_005_swap_model_before_r_L0_salon.png) | ![](agent/r6_006_swap_model_after_r_L0_salon.png) |
| 14621 | 6 | set_camera | r_L0_banyo | agent_override | - | Argus: The toilet is absent from the bathroom render; the camera is moved to a free pose that shows the primary fixture. (fixes a:F72) | - | - |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 12700 | 1 | set_camera | r_L0_mutfak | show: none of the 8 best poses of r_L0_mutfak that show f_L0_040, f_L0_041 passes the camera checks: cam_r_L0_mutfak_1: furniture and fixtures fill 2% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L0_mutfak_1: none of the room's main pieces (kitchen_counter, kitchen_island, sink_kitchen, stove, table_dining) is in its frame, while the room's camera search frames one; cam_r_L0_mutfak_1: furniture and fixtures fill 8% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: Chair f_L0_040 is not seen in cam_r_L0_mutfak_1. The camera must be re-posed to show the chair. F16 (f_L0_041) has the same cause and is fixed by the same camera edit. (fixes a:F15) |
| 12705 | 1 | move_group | r_L0_mutfak.kitchen_run | drawn_lock: r_L0_mutfak.kitchen_run: drawn pieces (f_L0_002, f_L0_020, f_L0_031, f_L0_032) stay where they are drawn; complete_group adds partners, relayout_room re-solves the room | Argus: The wall cabinet f_L0_041 is cut at win_L0_007. The tried_and_refused shows move_piece was refused for no free place on w_L0_024 and w_L0_032. The code_fix is move_group, which moves the whole kitchen run to a free wall span. However, the t (fixes a:F43) |
| 12706 | 1 | complete_group | r_L0_banyo.bathroom_set | unverified: r_L0_banyo.bathroom_set: the anchor f_L0_010 is unverified and not typed by code from the drawing (retype_piece first) | Argus: The bathroom set is missing its mirror over the basin; the earlier place_group was refused as a no-change because the set already exists, so the correct tool is complete_group on the existing set to add the missing mirror. (fixes a:F66) |
| 12707 | 1 | complete_group | r_L1_dus.bathroom_set | no_change: r_L1_dus.bathroom_set: nothing missing (members: f_L1_021, f_L1_027) | Argus: The bathroom set is missing its mirror over the basin; complete_group adds the missing partner to the existing set. (fixes a:F67) |
| 12708 | 1 | complete_group | r_L1_banyo.bathroom_set | unverified: r_L1_banyo.bathroom_set: the anchor f_L1_009 is unverified and not typed by code from the drawing (retype_piece first) | Argus: The bathroom set is missing its mirror over the basin; complete_group adds the missing partner to the existing set. (fixes a:F68) |
| 12709 | 1 | set_exterior | exterior:ground,site | site front_court yes: a sunken front court with parapet walls is the documents' or the brief's decision, never an edit's (the paved light well and its strip along the glazing stay); leave front_court out or use auto | Argus: The garden is bare flat grass with no planted beds, shrubs, ground cover or parking; set_exterior can add more trees, a path and a front court to make the garden read as a designed landscape. (fixes a:F72) |
| 12711 | 1 | set_material | walls | walls: wood_panel (wood) would clad every wall of every room; the walls keep a plain finish (plaster_white), a feature finish goes on one accent wall of a room (its scheme's feature wall: slats, a fluted panel or a headboard panel behind the bed or the sofa) | Argus: The wall behind the bed is flat, untextured paint, lacking the vertical wood panelling seen in the reference. Setting the walls slot to a wood panel look adds the feature-wall layer. (fixes a:F108) |
| 12712 | 1 | swap_model | f_L1_036 | asset_unusable: abo_B07HSCNKCT is not used: audit removed | Argus: The tall cabinet is a featureless white slab; the scandinavian/japandi model abo_B07HSCNKCT (0.75 x 0.31 x 1.47 m) fits the 0.60 x 0.30 m footprint and adds the missing definition. (fixes a:F114) |
| 12713 | 1 | set_camera | r_L1_dus | show: none of the 8 best poses of r_L1_dus that show f_L1_018, f_L1_021, f_L1_027 passes the camera checks: duplicate: cam_r_L1_dus_2 would show the view cam_r_L1_dus_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_dus, or remove one of the two views; cam_r_L1_dus_2: none of the room's main pieces (shower, toilet, washbasin) is in its frame, while the room's camera search frames one; cam_r_L1_dus_2: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The judge sees a close-up of a blank wall and a cabinet handle; the room's layout is not visible. Repointing the camera at the fixtures fixes it. (fixes a:F116) |
| 12715 | 1 | swap_model | f_L1_011 | no_change: f_L1_011 already uses the model 3dwh_11916ad11dca0c0b94c659f6 | Argus: The wardrobe is a crude, blocky model; the minimal/modern model 3dwh_11916ad11dca0c0b94c659f6 (2.24 x 0.60 x 2.50 m) fits the 2.27 x 0.60 m footprint and adds the missing styling. (fixes a:F125) |
| 12717 | 1 | set_material | facade | facade: wood_cladding (wood) would clad every wall of the house; the scandinavian facade scheme keeps the main walls rendered (render white) over a stone_wall_ledgestone base with wood_cladding at the entrance (the base and the accent are no set_material slot: a texture problem of the base is the build's) | Argus: The exterior is a grey-box placeholder; setting the facade to wood_cladding adds the timber contrast the reference demands. (fixes a:F127) |
| 12718 | 1 | set_material | facade | facade: stone_cladding (stone) would clad every wall of the house; the scandinavian facade scheme keeps the main walls rendered (render white) over a stone_wall_ledgestone base with wood_cladding at the entrance (the base and the accent are no set_material slot: a texture problem of the base is the build's) | Argus: The judge scores the exterior view 2/5 because the facade is a flat white box and the site is a void. Setting the facade material to a textured stone cladding addresses the core complaint of missing material richness. (fixes a:F129) |
| 12720 | 1 | swap_model | f_L0_035 | asset_unusable: 3dwh_6a79c95467305e1645426b11 is not used: audit removed | Argus: The potted_plant f_L0_035 was removed by the AI but the documents show a plant in the salon. The previous swap attempts were refused (asset_unusable, pin_refused for a generated model). Swapping to a real library model 3dwh_6a79c95467305e16 (fixes a:F148) |
| 12721 | 1 | swap_model | f_L0_038 | built_in: f_L0_038: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: The chair f_L0_038 was removed by the AI but the documents show a chair in the kitchen (dining set). The previous swap attempts were refused (retype_piece, swap_model built_in, swap_model asset_type). Swapping to a real library model hssd_a (fixes a:F149) |
| 12722 | 1 | place_group | r_L1_oda | room_type: a storage group does not belong in a hall room (groups.yaml room types: bedroom) | Argus: The storage room (Oda) on L1 is missing its main storage furniture (wardrobe or tall cabinet). The previous place_group attempt was refused because a storage group does not belong in a hall room. However, the room is typed as 'hall' but is  (fixes a:F150) |
| 12724 | 1 | rotate_piece | f_L0_017 | f_L0_017: clearance_ok, score: plausibility -119 -> -149 (F4 f_L0_017: armchair does not face its group (f_L0_021, f_L0_015); F6 f_L0_017: armchair: the free zone in front of it is blocked by f_L0_019; G11 f_L0_017: armchair f_L0_017: its front use zone is not reached by a 0.60 m walkway from door d_L0_006) | Argus: The armchair f_L0_017 differs from the drawing (tolerance 0.05 m): turned 29 deg. The layout stage should rotate the armchair to its drawn orientation. (fixes a:F158) |
| 12725 | 1 | rotate_piece | f_L0_019 | f_L0_019: clearance_ok, score: plausibility -119 -> -139 (F4 f_L0_019: armchair faces a wall 0.26 m in front of it; F6 f_L0_019: armchair: the free zone in front of it is reaches out of the room) | Argus: The armchair f_L0_019 differs from the drawing (tolerance 0.05 m): turned 29 deg. The layout stage should rotate the armchair to its drawn orientation. (fixes a:F159) |
| 12726 | 1 | swap_model | f_L1_037 | acceptance: pin_refused: f_L1_037: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The fitting fell back to the parametric mesh; the 0.30 x 0.27 x 1.40 m scandinavian model matches the piece's footprint and lifts it to library quality. (fixes a:F193) |
| 12727 | 1 | swap_model | f_L1_038 | acceptance: pin_refused: f_L1_038: abo_B07RMJPJMX: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: Same cause as F193: the 0.30 x 0.27 x 1.40 m model fits the 0.30 x 0.30 m footprint and replaces the parametric mesh. (fixes a:F194) |
| 12730 | 1 | relayout_room | r_L1_hol | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 1 more kept | Reposition the entrance group per the top-scored solver candidate to clear the 0.60 m walkways between doors d_L1_006, o_L1_002 and d_L1_009 (G11 critical). |
| 12735 | 1 | move_piece | f_L1_014 | acceptance: finding F9:f_L1_014 is still there after the edit (wardrobe reaches 0.09 m² through the room outline, up to 0.049 m deep); 1 more kept | Shift wardrobe 0.05 m in -y to clear wall w_L1_024 and the room outline collision (F9/S2). |
| 12736 | 1 | complete_group | r_L0_mutfak.kitchen_run | no_place: r_L0_mutfak.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Kitchen run is missing its fridge (G9, N59, c187, N70) and the sink f_L0_020 is planned but not built (N65); complete_group adds the missing partners to the drawn run. |
| 12737 | 1 | move_piece | f_L1_020 | drawn_lock: f_L1_020: a drawn piece moves at most 0.3 m, or 1.2 m when its back snaps onto a wall (this move: 0.69 m) | Move the floor lamp out of the free zone in front of both armchairs to clear the seating corner (F6). |
| 12738 | 1 | move_piece | f_L0_041 | snap: f_L0_041: no free place on wall w_L0_032 (doors, windows) | Wall cabinet f_L0_041 is cut at window win_L0_007; move it to free span s3 (wall w_L0_032) clear of the window. |
| 12739 | 1 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_008 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe f_L1_011 to the south wall to clear the door d_L1_003 walkway and unblock windows win_L1_003/win_L1_005. |
| 12741 | 1 | move_piece | f_L1_020 | snap: f_L1_020: no free place on wall w_L1_001 (doors, windows, at most 1.2 m from the drawn place) | Snap the floor lamp's back to the south wall between the two armchairs, clearing the free zone in front of both (F6). |
| 12742 | 1 | relayout_room | r_L1_hol | candidate: candidate 3 does not exist: 2 usable candidate(s) | Candidate 3 drops the entrance piece that sits in the d_L1_006→d_L1_009 corridor, restoring the 0.60 m walkways (G11 critical); the entrance group is optional. |
| 12743 | 1 | move_piece | f_L0_041 | f_L0_001: no_overlap, f_L0_041: inside_room, f_L0_041: no_overlap, score: plausibility 57 -> 27 (F4 f_L0_041: chair faces a wall 0.00 m in front of it; F9 f_L0_041: chair f_L0_041 overlaps stair f_L0_001 by 0.20 m²; G6 f_L0_041: chair f_L0_041 is 91° off the table f_L0_039 (needs ≤ 45°)) | Wall cabinet f_L0_041 is cut at window win_L0_007; move it to the free span s3 (wall w_L0_032) clear of the window. |
| 12744 | 1 | move_piece | f_L1_011 | f_L1_011: clearance_ok | Nudge wardrobe f_L1_011 0.17 m into the room to clear the door d_L1_003 walkway (G11) and unblock window win_L1_003 (F7). |
| 12745 | 1 | move_piece | f_L1_020 | acceptance: finding F6:f_L1_015 is still there after the edit (armchair: the free zone in front of it is blocked by f_L1_020); 1 more kept | Shift the floor lamp 0.3 m north, out of the free zone in front of both armchairs (F6). |
| 12746 | 1 | relayout_room | r_L1_hol | max_tries: r_L1_hol was edited 3 times in this round | Candidate 2 repositions the entrance piece to clear the 0.60 m walkways between the doors (G11 critical). |
| 12747 | 1 | move_piece | f_L1_011 | memory: the same edit was rejected in round 1: f_L1_011: clearance_ok | Nudge wardrobe f_L1_011 0.17 m into the room to clear the door d_L1_003 walkway (G11) and unblock window win_L1_003 (F7). |
| 12748 | 1 | relayout_room | r_L0_mutfak | f_L0_058: inside_room, f_L0_058: no_overlap, group checks: G8 f_L0_031: kitchen aisle 0.05 m in front of kitchen_counter f_L0_031, needs ≥ 0.90 m; G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove), set: the edit takes the room's hob away (the kitchen set needs it; pick another candidate or option) | Re-solve the room so the kitchen run gets its missing fridge (G9/N59/c187/N70) and the sink f_L0_020 is built (N65). |
| 12749 | 1 | move_piece | f_L1_020 | max_tries: f_L1_020 was edited 3 times in this round | Shift the floor lamp 0.3 m south, out of the free zone in front of both armchairs (F6). |
| 12750 | 1 | move_piece | f_L1_011 | max_tries: f_L1_011 was edited 3 times in this round | Nudge wardrobe f_L1_011 0.14 m into the room to clear the door d_L1_003 walkway (G11) and unblock window win_L1_003 (F7). |
| 12752 | 1 | move_piece | f_L0_041 | f_L0_001: no_overlap, f_L0_041: inside_room, f_L0_041: no_overlap, score: plausibility 57 -> 27 (F4 f_L0_041: chair faces a wall 0.00 m in front of it; F9 f_L0_041: chair f_L0_041 overlaps stair f_L0_001 by 0.20 m²; G6 f_L0_041: chair f_L0_041 is 91° off the table f_L0_039 (needs ≤ 45°)) | Wall cabinet f_L0_041 is cut at window win_L0_007; move it to the free span s3 (wall w_L0_032) clear of the window and the stair. |
| 12755 | 1 | relayout_room | r_L1_ebeveyn_y_odasi | acceptance: finding G11:d_L1_002 is still there after the edit (the main walkway from the entrance door is below 0.80 m between doors d_L1_002 and d_L1_007); 1 more kept | Re-solve the work group to candidate 3 (best circulation 0.93) to open the main walkway between the doors to at least 0.80 m (G11). |
| 12757 | 1 | relayout_room | r_L0_mutfak | f_L0_058: inside_room, f_L0_058: no_overlap, group checks: G8 f_L0_031: kitchen aisle 0.05 m in front of kitchen_counter f_L0_031, needs ≥ 0.90 m; G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove), set: the edit takes the room's hob away (the kitchen set needs it; pick another candidate or option) | Re-solve the room (candidate 2) so the kitchen run gets its missing fridge (G9/N59/c187/N70) and the sink f_L0_020 is built (N65). |
| 12761 | 1 | relayout_room | r_L1_ebeveyn_y_odasi | acceptance: finding G11:d_L1_002 is still there after the edit (the main walkway from the entrance door is below 0.80 m between doors d_L1_002 and d_L1_007); 1 more kept | Re-solve the work group to candidate 1 (best score, circulation 0.86) to open the main walkway between the doors to at least 0.80 m (G11). |
| 12762 | 1 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 resolves the critical walkway blockage from door d_L0_004 to d_L0_006 and fixes the major G2/G3 group layout issues for the seating groups. |
| 12764 | 1 | relayout_room | r_L0_mutfak | f_L0_058: inside_room, f_L0_058: no_overlap, group checks: G8 f_L0_031: kitchen aisle 0.05 m in front of kitchen_counter f_L0_031, needs ≥ 0.90 m; G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove), set: the edit takes the room's hob away (the kitchen set needs it; pick another candidate or option) | Re-solve the room (candidate 3) so the kitchen run gets its missing fridge (G9/N59/c187/N70) and the sink f_L0_020 is built (N65). |
| 12765 | 1 | relayout_room | r_L1_ebeveyn_y_odasi | acceptance: finding G11:d_L1_002 is still there after the edit (the main walkway from the entrance door is below 0.80 m between doors d_L1_002 and d_L1_007); 1 more kept | Re-solve the work group to candidate 2 (circulation 0.84) to open the main walkway between the doors to at least 0.80 m (G11). |
| 12767 | 1 | swap_model | f_L0_024 | pin_refused: f_L0_024: gen_toilet_classic_3_293965c2: fails the fit rules (caps, height): the real model stays; swap to a real model of the type or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to a floor-standing classic toilet that sits on the floor. |
| 12770 | 1 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 2 re-solves the seating groups around the drawn anchors with 2 members, attempting to clear the critical d_L0_004-d_L0_006 walkway and the G2/G3 group layout findings. |
| 12774 | 1 | swap_model | f_L0_024 | acceptance: pin_refused: f_L0_024: 3dwh_36adbef7518af3145f49b210: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to the real floor-standing Caesar Toilet C1348 that sits on the floor. |
| 12778 | 1 | move_piece | f_L0_041 | max_tries: f_L0_041 was edited 3 times in this round | Wall cabinet f_L0_041 is cut at window win_L0_007; move it to the free span s4 (wall w_L0_020) clear of the window. |
| 12781 | 1 | move_piece | f_L1_007 | score: plausibility -35 -> -52 (F3 f_L1_007: bed_double: the headboard stands in the room (0.07 m off); G4 f_L1_007: bed_double f_L1_007: no nightstand on the free left side of the head (1.54 m free); G4 f_L1_008: nightstand f_L1_008 of bed_double f_L1_007: its back 0.69 m from the headboard line (needs ≤ 0.30 m); its front 90° off the bed's front; G5 f_L1_007: bed_double f_L1_007: 0.19 m free at the foot, needs ≥ 0.60 m) | Shift bed 0.3 m up to clear door d_L1_011, stop cutting wall w_L1_004 and gain foot clearance. |
| 12782 | 1 | relayout_room | r_L0_salon | acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 3 re-solves the seating groups around the drawn anchors, attempting to clear the critical d_L0_004-d_L0_006 walkway and the G2/G3 group layout findings. |
| 12783 | 1 | swap_model | f_L0_024 | acceptance: pin_refused: f_L0_024: 3dwh_670407ad54a23fbdf5bbd2fe: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Current toilet model floats 0.200 m above the floor (S1); swap to the real floor-standing toilet (0.43x0.72x0.65) that sits on the floor. |
| 12784 | 1 | set_room_type | r_L0_oda | no_change: r_L0_oda is already a storage | Re-assert storage type for the 2.1 m2 empty utility space to clear the stale AI1 finding that still references the old hall type. |
| 12785 | 1 | retype_piece | f_L1_028 | exists: no piece 'f_L1_028' in a room of the building | Confirm the unverified shoe cabinet so it is built (it fits the hall entrance group). |
| 12787 | 1 | swap_model | f_L1_020 | max_tries: f_L1_020 was edited 3 times in this round | Replace the dated mid-century floor lamp with a modern model that fits the room's warm aesthetic (D3). |
| 12788 | 1 | retype_piece | f_L1_029 | score: plausibility 70 -> 50 (F8 f_L1_030: office_chair stands alone in the room (no wall, no desk within 1.0 m); G13 f_L1_029: dresser f_L1_029: 0.05 m free in front, needs ≥ 0.80 m) | The documents name a dresser ('SIFONIYER') at (8.11, 4.91); retype the nearby desk to a dresser to satisfy the named piece (NR). |
| 12790 | 1 | set_camera | r_L1_hol | max_tries: r_L1_hol was edited 3 times in this round | Camera is a failed close-up of a corner; reposition to a free point with headroom so the stair and shoe cabinet are visible. |
| 12791 | 1 | move_piece | f_L1_008 | acceptance: finding F9:f_L1_008 is still there after the edit (nightstand f_L1_008 overlaps bed_double f_L1_007 by 0.17 m²) | Move nightstand up to the headboard line of bed f_L1_007 (back within 0.30 m) and off the bed footprint. |
| 12792 | 1 | swap_model | f_L0_026 | acceptance: pin_refused: f_L0_026: hssd_7b5d656c72b56ae0e8200132ec92a1ae03869b93: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Current washbasin floats 0.314 m above the floor (S1) and has no mirror (M26/D3); swap to the real Sink model (0.57x0.48x0.33) that sits correctly on the wall. |
| 12793 | 1 | set_camera | r_L1_oda | show: no free camera point of r_L1_oda shows bed, wardrobe, nightstand (bed, wardrobe, nightstand not in r_L1_oda: name its pieces, doors or windows) | Camera is too low and close to a corner, cutting off ceiling and floor; raise and pull back to a free point with headroom to present the room as a coherent space. |
| 12795 | 1 | set_camera | r_L1_oda | max_tries: r_L1_oda was edited 3 times in this round | Camera is too low and close to a corner, cutting off ceiling and floor; reposition to a free point with headroom to present the hall as a coherent space. |
| 12798 | 1 | set_camera | r_L1_dus | show: none of the 8 best poses of r_L1_dus that show f_L1_018, f_L1_021, f_L1_027 passes the camera checks: duplicate: cam_r_L1_dus_2 would show the view cam_r_L1_dus_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_dus, or remove one of the two views; cam_r_L1_dus_2: none of the room's main pieces (shower, toilet, washbasin) is in its frame, while the room's camera search frames one; cam_r_L1_dus_2: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Camera is a close-up of a cabinet handle; move to a free point with headroom to show the room layout and styling. |
| 12799 | 1 | swap_model | f_L0_024 | max_tries: f_L0_024 was edited 3 times in this round | Current toilet model floats 0.200 m above the floor (S1); swap to the real floor-standing ConDoc 5 Toilet (0.44x0.72x0.76) that sits on the floor. |
| 12800 | 1 | move_piece | f_L1_004 | f_L1_004: inside_room (outline: bed_double reaches 0.56 m² through the room outline, up to 0.277 m deep; 0.00 m² up to 0.000 m deep before), score: plausibility -32 -> -75 (F3 f_L1_004: bed_double: the headboard stands in the room (0.27 m off); F9 f_L1_004: bed_double reaches 0.56 m² through the room outline, up to 0.277 m deep; G4 f_L1_004: bed_double f_L1_004: no nightstand on the free right side of the head (6.00 m free); G5 f_L1_004: bed_double f_L1_004: 0.11 m free along the right side, needs ≥ 0.60 m) | Shift bed 0.3 m left to open a 0.60 m walkway to its right use zone from door d_L1_011. |
| 12801 | 1 | move_piece | f_L1_007 | f_L1_007: inside_room (outline: bed_double reaches 0.67 m² through the room outline, up to 0.345 m deep; 0.10 m² up to 0.049 m deep before), score: plausibility -32 -> -62 (F3 f_L1_007: bed_double: the headboard stands in the room (0.34 m off); F9 f_L1_007: bed_double reaches 0.67 m² through the room outline, up to 0.345 m deep; G4 f_L1_008: nightstand f_L1_008 of bed_double f_L1_007: its back 1.29 m from the headboard line (needs ≤ 0.30 m); its front 90° off the bed's front; G5 f_L1_007: bed_double f_L1_007: 0.53 m free at the foot, needs ≥ 0.60 m) | Shift bed 0.3 m down to clear door d_L1_011, stop cutting wall w_L1_004 and gain foot clearance. |
| 12802 | 1 | set_camera | r_L1_dus | show: none of the 7 best poses of r_L1_dus that show f_L1_037, win_L1_011 passes the camera checks: cam_r_L1_dus_2: none of the room's main pieces (shower, toilet, washbasin) is in its frame, while the room's camera search frames one; duplicate: cam_r_L1_dus_2 would show the view cam_r_L1_dus_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_dus, or remove one of the two views; cam_r_L1_dus_2: furniture and fixtures fill 4% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Camera is a close-up of a cabinet handle; move to a free point with headroom to show the tall cabinet and window, a different part of the bathroom than cam_r_L1_dus_1. |
| 12803 | 1 | move_piece | f_L1_008 | acceptance: finding F9:f_L1_008 is still there after the edit (nightstand f_L1_008 overlaps bed_double f_L1_007 by 0.17 m²) | Move nightstand down to the headboard line of bed f_L1_007 (back within 0.30 m) and off the bed footprint. |
| 12804 | 1 | remove_camera | cam_r_L1_dus_2 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | The second bathroom view is a close-up of a cabinet handle and duplicates the repositioned cam_r_L1_dus_1; no free pose of the 4.5 m2 bathroom shows a different part of the room, so the redundant view is removed. |
| 12805 | 1 | move_piece | f_L1_004 | f_L1_004: no_overlap, f_L1_005: no_overlap | Shift bed 0.3 m down to open a 0.60 m walkway to its right use zone from door d_L1_011. |
| 12806 | 1 | set_camera | r_L0_mutfak | memory: the same edit was rejected in round 1: show: none of the 8 best poses of r_L0_mutfak that show f_L0_040, f_L0_041 passes the camera checks: cam_r_L0_mutfak_1: furniture and fixtures fill 2% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L0_mutfak_1: none of the ro | Chairs f_L0_040 and f_L0_041 are not seen; reposition the kitchen camera to a free point with headroom so the dining chairs are in frame. |
| 12807 | 1 | move_piece | f_L1_007 | acceptance: finding F7:f_L1_007 is still there after the edit (bed_double blocks door d_L1_011) | Shift bed 0.3 m right to clear door d_L1_011, stop cutting wall w_L1_004 and open the right use zone walkway. |
| 13077 | 2 | retype_piece | f_L0_034 | no_change: f_L0_034 is already a bookshelf | Argus: The bookshelf was removed by an AI decision but is still drawn in the salon. The retype was refused as 'no_change' because the type is already correct, but the piece is not built. Retyping forces a rebuild. Since the type is already bookshe (fixes a:F227) |
| 13079 | 2 | retype_piece | f_L1_028 | memory: the same edit was rejected in round 1: exists: no piece 'f_L1_028' in a room of the building | Argus: The shoe cabinet was removed by an AI decision but is still drawn in the hall. The previous swap was refused because the piece was not in the building. Retyping forces a rebuild. The type is already shoe_cabinet, so the issue is the removal (fixes a:F235) |
| 13080 | 2 | retype_piece | f_L1_029 | no_change: f_L1_029 is already a desk | Argus: The desk was removed by an AI decision but is still drawn in the master bedroom. Retyping forces a rebuild. The type is already desk, so the issue is the removal flag. (fixes a:F236) |
| 13081 | 2 | retype_piece | f_L1_030 | no_change: f_L1_030 is already a office_chair | Argus: The office chair was removed by an AI decision but is still drawn in the master bedroom. Retyping forces a rebuild. The type is already office_chair, so the issue is the removal flag. (fixes a:F237) |
| 13083 | 2 | retype_piece | f_L1_032 | no_change: f_L1_032 is already a wardrobe | Argus: The wardrobe was removed by an AI decision but is still drawn in the child's bedroom. Retyping forces a rebuild. The type is already wardrobe, so the issue is the removal flag. (fixes a:F239) |
| 13084 | 2 | retype_piece | f_L1_033 | no_change: f_L1_033 is already a desk | Argus: The desk was removed by an AI decision but is still drawn in the child's bedroom. Retyping forces a rebuild. The type is already desk, so the issue is the removal flag. (fixes a:F240) |
| 13085 | 2 | retype_piece | f_L0_001 | retype: fridge is no candidate for f_L0_001 (2.20 x 2.72 m at [4.68, 12.94]): the size table and the room / zone give stair | Argus: The kitchen has no fridge. The documents show a tall unit on the kitchen run (the black tall cabinet at the right of the kitchen in the plan), but the model built it as a wall_cabinet and the kitchen is missing its fridge entirely (f_L0_001 (fixes a:N59) |
| 13086 | 2 | place_group | r_L0_banyo | no_change: r_L0_banyo already has its bathroom_set r_L0_banyo.bathroom_set (anchor f_L0_010, members f_L0_024, f_L0_026): nothing missing, never a second set | Argus: The washbasin f_L0_026 hangs over the window o_L0_002 of its wall in r_L0_banyo, and the toilet f_L0_024 is absent from the render. The bathroom fixtures are placed on the wrong wall / not built, so the room reads as a bare box. (fixes a:N60) |
| 13087 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Argus: The living room is a mishmash of clashing styles: a mid-century egg chair (f_L0_007), a mid-century bench sofa (f_L0_014), a red mid-century armchair (f_L0_016) and a patterned armchair (f_L0_016) all sit next to a tufted leather sofa and a (fixes a:N61) |
| 13088 | 2 | relayout_room | r_L1_oda_2 | no_place: r_L1_oda_2 relayout: the solver places nothing and leaves the drawn pieces as drawn (sleeping_single: no candidate position fits the room; storage: no candidate position fits the room) | Argus: The wall_art dec_L1_039 hangs over the window o_L1_005 of its wall in r_L1_oda_2. Same art-over-window error as the salon. (fixes a:N63) |
| 13089 | 2 | place_group | r_L1_cocuk_odasi | no_place: bedroom_chest group: no place passes the checks (bedroom_chest: no place passes the checks) | Argus: The documents name a dresser ('*SIFONIYER') on L1 but the model has no piece within 1.2 m of it. The dresser is missing from the built house. (fixes a:N64) |
| 13090 | 2 | place_group | r_L0_mutfak | no_place: r_L0_mutfak.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Argus: The sink_kitchen f_L0_020 is planned to be built but the scene has no object for it. The kitchen has a counter and an island but no visible sink. (fixes a:N65) |
| 13091 | 2 | place_group | r_L1_dus | no_change: r_L1_dus already has its bathroom_set r_L1_dus.bathroom_set (anchor f_L1_018, members f_L1_021, f_L1_027): nothing missing, never a second set | Argus: The bathroom r_L1_dus (4.5 m2) has a shower, tall_cabinet, toilet and washbasin, but the renders score 1/5: the camera shows a cramped, cluttered box. The room is too small for four fixtures and the layout is not working. (fixes a:N66) |
| 13092 | 2 | place_group | r_L1_soyunma_odasi | no_place: dressing group: no place passes the checks (dressing: no place passes the checks) | Argus: The dressing room r_L1_soyunma_odasi (5.9 m2) has only a wardrobe, and the renders score 1/5: the camera shows a flat, empty box. A dressing room with only a wardrobe and no mirror, bench or lighting is not a dressing room. (fixes a:N67) |
| 13093 | 2 | set_entrance | d_L0_001 | exists: 'd_L0_001' is no outside door of site.entrances | Argus: The entrance is met by a short flight of bare concrete steps with a lesson (UL82) noting the steps are bare. The entrance is not finished. (fixes a:N68) |
| 13095 | 2 | place_group | r_L0_banyo | room_type: a wc_set group does not belong in a bathroom room (groups.yaml room types: wc) | Argus: lesson (lesson:UL205:L0): The L0 bathroom WC is a floor-standing toilet against a plain tiled wall with no half-height installation wall, recessed niches, backlit mirror, wall-hung WC with flush plate, bench/console basin, brush or roll hol (fixes a:N71) |
| 13098 | 2 | retype_piece | f_L1_006 | f_L1_004: no_overlap, f_L1_006: no_overlap, score: plausibility -32 -> -42 (F9 f_L1_006: floor_lamp f_L1_006 overlaps bed_double f_L1_004 by 0.16 m²) | the plan names it: drawn piece f_L1_006 (0.40 x 0.40 m) left out as a detail (drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)) although an AI pass named it floor_lamp / nightstand, which fits its size: (fixes a:c8) |
| 13099 | 2 | retype_piece | f_L0_001 | memory: the same edit was rejected in round 2: retype: fridge is no candidate for f_L0_001 (2.20 x 2.72 m at [4.68, 12.94]): the size table and the room / zone give stair | the room misses its fridge: r_L0_mutfak: kitchen r_L0_mutfak has no fridge (fridge), while f_L0_001 (stair, 2.20 x 2.72 m) stands in it: most likely the missing fridge (fixes a:c187) |
| 13100 | 2 | set_camera | ext_4 | eye height 8.50 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 7.55 m), the ground at (12, 1.6) is at z -0.50 m: use z 1.00 to 1.20 for an eye-level view | Argus: The window exists in the model (from_documents) but the exterior view ext_4 does not frame it. Moving the camera to show the window fixes the render without touching the geometry. (fixes a:F17) |
| 13102 | 2 | place_group | r_L0_salon | room_type: a terrace_lounge group does not belong in a living room (groups.yaml room types: balcony) | Argus: lesson (lesson:UL152): The veranda (os_L0_veranda, ext_1, ext_4) is furnished with dining-style chairs and a table rather than the P15 outdoor lounge set (slatted armchairs or a cushioned sofa, a woven pouf, a small round side table with a  (fixes a:N75) |
| 13111 | 2 | complete_group | r_L0_mutfak.kitchen_run | memory: the same edit was rejected in round 1: no_place: r_L0_mutfak.kitchen_run (missing fridge): no place passes the checks (kitchen_run: no candidate position fits the room) | Add the missing fridge partner to the drawn kitchen run (G9, N59, c187, N70) and rebuild the run members including the sink f_L0_020 (N65). |
| 13112 | 2 | complete_group | r_L0_mutfak.dining | no_place: r_L0_mutfak.dining (missing chair, chair): no place passes the checks (dining: no candidate position fits the room) | Add the missing third chair to the dining set (G6 minor: 2 of 3 chairs). |
| 13113 | 2 | move_piece | f_L0_041 | snap: f_L0_041: no free place on wall w_L0_032 (doors, windows) | Move the wall cabinet off window win_L007 to the free span s3 (a:F43). |
| 13117 | 2 | move_piece | f_L0_041 | wall_in_room: wall w_L0_020 does not bound the piece's room | Move the wall cabinet off window win_L007 to the free span s4 on wall w_L0_020 (a:F43). |
| 13118 | 2 | swap_model | f_L0_038 | asset_type: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 is a chair model, not a stove | Restore the dining chair the documents show, using the library chair model named in the finding (a:F149). |
| 13124 | 2 | move_piece | f_L0_041 | snap: f_L0_041: no free place on wall w_L0_025 (doors, windows) | Move the wall cabinet off window win_L007 to the free span s5 on wall w_L0_025 (a:F43). |
| 13125 | 2 | swap_model | f_L0_042 | asset_type: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 is a chair model, not a kitchen_island | Give the island a styled-surface model to match the reference (a:D3). |
| 13127 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 resolves the critical walkway blockage from door d_L0_004 to d_L0_006 and fixes the major group layout issues (G2/G3) for the seating group. |
| 13128 | 2 | move_piece | f_L0_041 | max_tries: f_L0_041 was edited 3 times in this round | Move the wall cabinet off window win_L007 to the free span s8 on wall w_L0_017 (a:F43). |
| 13131 | 2 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 2 has 2 seating members and may resolve the critical walkway blockage from door d_L0_004 to d_L0_006 differently than candidate 1. |
| 13150 | 2 | swap_model | f_L1_011 | asset_unusable: hssd_3bc24e0ea79ade13d4703ca23ece1e4019f9b70b is not used: audit removed | Replace the parametric wardrobe with a real library model (Aspen 5-door with centre mirror) to fix S6 and add styled surfaces for the dressing room. |
| 13151 | 2 | swap_model | f_L1_012 | asset_unusable: hssd_3bc24e0ea79ade13d4703ca23ece1e4019f9b70b is not used: audit removed | Replace the parametric wardrobe with a real library model (Aspen 5-door with centre mirror) to fix S6. |
| 13152 | 2 | swap_model | f_L1_011 | asset_unusable: 3dwh_bf4c5e1d2800e2b7de51a210 is not used: audit pending | Replace the parametric wardrobe with a real library model (IKEA PAX elements) to fix S6 and add styled surfaces for the dressing room. |
| 13153 | 2 | swap_model | f_L1_012 | asset_unusable: 3dwh_bf4c5e1d2800e2b7de51a210 is not used: audit pending | Replace the parametric wardrobe with a real library model (IKEA PAX elements) to fix S6. |
| 13159 | 2 | move_piece | f_L1_011 | max_tries: f_L1_011 was edited 3 times in this round | Move wardrobe f_L1_011 to the free wall span s1 (wall w_L1_012) to clear the door walkway and unblock window win_L1_003. |
| 13160 | 2 | place_group | r_L1_soyunma_odasi | no_place: dressing group: no place passes the checks (dressing: no place passes the checks) | Place the dressing group (bench, mirror, etc.) to complete the dressing room program and address the missing member finding. |
| 13448 | 3 | move_piece | f_L1_011 | snap: f_L1_011: no free place on wall w_L1_012 (doors, windows, at most 1.2 m from the drawn place) | Move wardrobe f_L1_011 to free span s1 (wall w_L1_012) to clear the door walkway (G11), unblock the door opening (F7) and leave windows win_L1_001/003/005 (G12). |
| 13452 | 3 | retype_piece | f_L1_029 | memory: the same edit was rejected in round 2: no_change: f_L1_029 is already a desk | Rebuild the not-built desk (a:F236) so the work group renders |
| 13455 | 3 | retype_piece | f_L1_030 | memory: the same edit was rejected in round 2: no_change: f_L1_030 is already a office_chair | Rebuild the not-built office chair (a:F237) so the work group renders |
| 13462 | 3 | relayout_room | r_L1_cocuk_odasi | acceptance: finding F7:f_L1_007 is still there after the edit (bed_double blocks door d_L1_011); 5 more kept | Re-solve sleeping_double groups around drawn anchors to clear f_L1_007 door block, wall cut, outline breach and nightstand overlap/placement. |
| 13464 | 3 | relayout_room | r_L0_mutfak | memory: the same edit was rejected in round 1: f_L0_058: inside_room; f_L0_058: no_overlap; group checks: G8 f_L0_031: kitchen aisle 0.05 m in front of kitchen_counter f_L0_031, needs ≥ 0.90 m; G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove); set: the edit takes the room's hob away (the kitchen set needs it; pick another candidate or opti | Solver candidate 1 re-solves the dining group (3 chairs around the table, fixing G6) and the island, and places the missing fridge in the kitchen run (fixing G9) while keeping the drawn run anchored. |
| 13467 | 3 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 resolves the critical walkway blockage between doors d_L0_004 and d_L0_006 and re-solves the seating groups to fix the major G2/G3 orientation and placement findings. |
| 13468 | 3 | relayout_room | r_L0_mutfak | memory: the same edit was rejected in round 1: f_L0_058: inside_room; f_L0_058: no_overlap; group checks: G8 f_L0_031: kitchen aisle 0.05 m in front of kitchen_counter f_L0_031, needs ≥ 0.90 m; G9 r_L0_mutfak: kitchen r_L0_mutfak has no hob (stove); set: the edit takes the room's hob away (the kitchen set needs it; pick another candidate or opti | Solver candidate 2 re-solves the dining group (3 chairs around the table, fixing G6) and the island, and places the missing fridge in the kitchen run (fixing G9) while keeping the drawn run anchored. |
| 13471 | 3 | move_piece | f_L1_007 | memory: the same edit was rejected in round 1: score: plausibility -35 -> -52 (F3 f_L1_007: bed_double: the headboard stands in the room (0.07 m off); G4 f_L1_007: bed_double f_L1_007: no nightstand on the free left side of the head (1.54 m free); G4 f_L1_008: nightstand f_L1_008 of bed_double f_L1_007: its back 0.69 m from the headboard line (n | Shift the bed 0.3 m away from the bottom wall to clear the wall cut, outline breach and door d_L1_011 swing. |
| 13473 | 3 | move_piece | f_L0_006 | acceptance: finding F4:f_L0_006 is still there after the edit (sofa does not face its group (f_L0_015, f_L0_021)) | Snap the sofa back onto the right wall (0.16 m off) to fix F3 off-wall. |
| 13476 | 3 | move_piece | f_L1_007 | score: plausibility -32 -> -49 (F3 f_L1_007: bed_double: the headboard stands in the room (0.07 m off); G4 f_L1_008: nightstand f_L1_008 of bed_double f_L1_007: its back 0.79 m from the headboard line (needs ≤ 0.30 m); its front 90° off the bed's front; G5 f_L1_007: bed_double f_L1_007: 0.03 m free at the foot, needs ≥ 0.60 m) | Shift the bed 0.2 m away from the bottom wall to clear the wall cut, outline breach and door d_L1_011 swing. |
| 13481 | 3 | rotate_piece | f_L0_006 | f_L0_006: clearance_ok, f_L0_006: inside_room, f_L0_006: inside_room (outline: sofa reaches 0.39 m² through the room outline, up to 0.502 m deep; 0.00 m² up to 0.000 m deep before) | Turn the sofa's front to face the coffee table group (f_L0_015, f_L0_021) to fix F4 orientation. |
| 13482 | 3 | move_piece | f_L1_007 | score: plausibility -32 -> -49 (F3 f_L1_007: bed_double: the headboard stands in the room (0.06 m off); G4 f_L1_008: nightstand f_L1_008 of bed_double f_L1_007: its back 0.89 m from the headboard line (needs ≤ 0.30 m); its front 90° off the bed's front; G5 f_L1_007: bed_double f_L1_007: 0.12 m free at the foot, needs ≥ 0.60 m) | Shift the bed 0.1 m away from the bottom wall to clear the wall cut, outline breach and door d_L1_011 swing. |
| 13485 | 3 | move_piece | f_L0_006 | acceptance: finding F3:f_L0_006 is still there after the edit (sofa: its back is not on a wall (0.16 m off)); 1 more kept | Restore the sofa to its drawn position after the rejected snap and rotation. |
| 13486 | 3 | move_piece | f_L1_007 | max_tries: f_L1_007 was edited 3 times in this round | Restore the bed to its drawn centre after the rejected shifts. |
| 13493 | 3 | complete_group | r_L1_cocuk_odasi.sleeping_double | no_place: r_L1_cocuk_odasi.sleeping_double (missing nightstand, nightstand), re-solved as one unit around the drawn bed_double f_L1_004: the solver places nothing and leaves the drawn pieces as drawn (sleeping_double: no candidate position fits the room) | Add the missing nightstands of the drawn bed f_L1_004 group. |
| 13496 | 3 | move_piece | f_L0_006 | memory: the same edit was rejected in round 3: acceptance: finding F3:f_L0_006 is still there after the edit (sofa: its back is not on a wall (0.16 m off)); 1 more kept | Restore the sofa to its drawn position after the rejected snap and rotation. |
| 13499 | 3 | move_piece | f_L0_006 | max_tries: f_L0_006 was edited 3 times in this round | Restore the sofa to its drawn position after the rejected snap and rotation. |
| 13502 | 3 | swap_model | f_L1_005 | asset_type: hssd_929b01c5bca6f8ca73e30da0c30b2930d095dcf6 is a office_chair model, not a dresser | Give the dresser a styled model with surfaces instead of a featureless slab. |
| 13510 | 3 | swap_model | f_L1_005 | off_style: f_L1_005: hssd_0a9e33bd8772e0b3030d0a443b990328141c7028 is of the styles ['classic'], none of the project's chain scandinavian -> minimal -> modern: choose a model of the style | Give the dresser a styled model (Sweet Dreams) with real surfaces instead of a featureless slab. |
| 13513 | 3 | mark_not_furniture | f_L1_002 | no_crop: f_L1_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/cam_r_L1_cocuk_odasi_1_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | The 4.64 m drawn cluster is a wall run of drawn pieces (a group), not a single furniture piece; it is not built. |
| 13996 | 4 | set_camera | r_L1_dus | show: none of the 4 best poses of r_L1_dus that show f_L1_027 passes the camera checks: cam_r_L1_dus_1: none of the room's main pieces (shower, toilet, washbasin) is in its frame, while the room's camera search frames one; cam_r_L1_dus_1: furniture and fixtures fill 7% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value | Argus: The washbasin is in the model but not visible in the render; re-aiming the camera to show it is the direct fix. (fixes a:F31) |
| 13999 | 4 | set_material | walls | walls: wood_slat (wood) would clad every wall of every room; the walls keep a plain finish (plaster_white), a feature finish goes on one accent wall of a room (its scheme's feature wall: slats, a fluted panel or a headboard panel behind the bed or the sofa) | Argus: The reference style calls for vertical slatted wood panelling on the accent wall behind the seating. Setting the walls slot to wood_slat provides the feature wall layer that is currently missing. (fixes a:F82) |
| 14005 | 4 | swap_model | f_L1_009 | asset_unusable: 3dwh_d989454d1f62854400613026 is not used: audit removed | Argus: The dark blocky bathtub surround clashes with the light wood vanity and warm wood floor. Swapping to a minimal/modern bathtub (1.52 x 0.74 m) matches the unified wood-and-stone palette. (fixes a:F96) |
| 14007 | 4 | swap_model | f_L1_005 | acceptance: pin_refused: f_L1_005: hssd_68b22165ccec115439ff5bca2a28bd2ebf1fdb9d: fails the fit rules (caps, height, at most 0.88 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The current dresser model hssd_44c41c97eee1e7c7e05b91d58da8d1737586d55d is classic style, which was refused in a prior swap (off_style). The scandinavian/minimal model hssd_68b22165ccec115439ff5bca2a28bd2ebf1fdb9d (1.18 x 0.48 x 0.97 m) mat (fixes a:F103) |
| 14009 | 4 | set_camera | r_L1_dus | memory: the same edit was rejected in round 1: show: none of the 8 best poses of r_L1_dus that show f_L1_018, f_L1_021, f_L1_027 passes the camera checks: duplicate: cam_r_L1_dus_2 would show the view cam_r_L1_dus_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_dus, or remove one of the two views; c | Argus: The camera is pressed against a glass partition, half the frame is a wall, and the main group (basin, mirror, cabinet) is not in view. A prior remove_camera was refused (no target finding named). Re-aiming the camera to show the main fixtur (fixes a:F110) |
| 14013 | 4 | swap_model | f_L1_013 | asset_unusable: gen_bed_single_scandinavian_1_8060783a is not used: audit removed | Argus: The current bed model is a flat sheet; swapping to a styled single bed adds the missing bedding layers. (fixes a:F121) |
| 14014 | 4 | swap_model | f_L1_014 | pin_refused: f_L1_014: gen_wardrobe_rustic_1_97c119f6: a generated model (units guessed) while a real product of the type fits within the caps (hssd_602e95402b712af5ac6273ce4d2d2e6f57229516): the real model stays; swap to a real model of the type or use another tool | Argus: The current wardrobe is a placeholder slab; the rustic model adds the missing detail and a more human scale. (fixes a:F122) |
| 14015 | 4 | set_camera | r_L1_soyunma_odasi | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: The camera is flat against a wall and screen; re-aiming it to show the wardrobe from a free point frames the 5.9 m2 room. (fixes a:F124) |
| 14016 | 4 | set_exterior | exterior:site | site front_court yes: a sunken front court with parapet walls is the documents' or the brief's decision, never an edit's (the paved light well and its strip along the glazing stay); leave front_court out or use auto | Argus: The render is a grey-box placeholder; adding site elements (path, trees, front court) brings it to the reference standard. (fixes a:F125) |
| 14017 | 4 | set_exterior | exterior:site | no_change: the exterior already has these values ({"site": {"path": true}}): nothing to change | Argus: The front is a flat green plane with no path; enabling the site path adds the missing walkway. (fixes a:F126) |
| 14019 | 4 | set_camera | ext_4 | eye height 2.10 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 7.55 m), the ground at (12, 1.6) is at z -0.50 m: use z 1.00 to 1.20 for an eye-level view | Argus: The previous set_camera was refused because the eye height 8.50 m is neither eye level nor above the ridge (7.55 m). The judge's complaint is the grey-box, unlandscaped look; a proper eye-level entrance view is the standard fix for an exter (fixes a:F129) |
| 14020 | 4 | set_camera | ext_5 | role: ext_5 is the aerial view the camera policy allows and keeps its role (docs/milestone13.md D8 and the site view rule): an aerial view stands at least 1 m above the ridge (z 8.55 m or more; the ridge is at 7.55 m) and looks down at least 5 degrees; this pose stands at z 1.60 m, below that line (the camera validator and code X6 judge it as an eye-level view) and looks -8.0 degrees down, less than the 5 degrees (the next build would make it an eye-level view); its height above eye level and its downward pitch are by design, not a finding; add_camera with a new view id for an eye-level view | Argus: Same cause as F129: the camera is a high massing shot. Re-aiming to eye level at the entrance is the standard fix; the landscape/ground complaints are a separate site issue (F137/F142) that no camera can fix. (fixes a:F130) |
| 14021 | 4 | swap_model | f_L0_035 | acceptance: pin_refused: f_L0_035: 3dwh_5407530ab15149cd71f3b895: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The potted_plant f_L0_035 was removed by the AI but the documents show a plant in the salon. The previous swap attempt was refused (asset_unusable). Swapping to a real library model 3dwh_5407530ab15149cd71f3b895 (0.47 x 0.35 x 0.45 m, minim (fixes a:F147) |
| 14022 | 4 | swap_model | f_L0_038 | memory: the same edit was rejected in round 1: built_in: f_L0_038: the stove stands in a counter run and is built into it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen design rule of 28 Oct 2026); no library model replaces it | Argus: The stove f_L0_038 was removed by the AI but the documents show a stove in the kitchen. The previous swap attempts were refused (built_in, asset_type). Swapping to hssd_a34eb58d8e8c6c14548c4d3b915eed8b124dbd63 (0.50 x 0.60 x 0.90 m, minimal (fixes a:F148) |
| 14023 | 4 | set_room_type | r_L1_oda | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: The room r_L1_oda is typed as 'hall' but the finding says it is a storage room missing its main storage furniture. The place_group was refused because a storage group does not belong in a hall room. Retyping the room to 'storage' will allow (fixes a:F149) |
| 14024 | 4 | swap_model | f_L0_008 | acceptance: pin_refused: f_L0_008: 3dwh_61738b81cf37f0fe78386bc5: fails the fit rules (caps, height): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The armchair is built with a parametric mesh. A real library model (0.83 x 0.63 x 1.34 m, minimal/modern/scandinavian) fits the 0.92 x 0.62 m footprint and upgrades the render quality. (fixes a:F178) |
| 14028 | 4 | relayout_room | r_L1_hol | acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 1 more kept | Candidate 2 has the best circulation score (0.85) with no hard failures; candidate 1 was already rejected for failing the G11 walkway checks and candidate 3 is empty. |
| 14034 | 4 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 is the only solver layout that resolves the critical walkway blockage between doors d_L0_004 and d_L0_006 and re-solves the seating groups. |
| 14038 | 4 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s3: no place passes the checks (entrance: no candidate position fits the room) | Moving the entrance group from the right wall (near d_L1_009) to the right wall span s3 (y=12.4-13.8) to clear the 0.60m walkway between doors d_L1_006, o_L1_002 and d_L1_009. |
| 14040 | 4 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s7: the places that pass the checks are elsewhere (candidate 1: shoe_cabinet at [5.6692, 10.6707]) | Moving the entrance group to the left wall span s7 (below window win_L1_008) to clear the walkway between doors d_L1_006, o_L1_002 and d_L1_009 on the right side. |
| 14042 | 4 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 2 has no hard failures and circulation 0.92; trying it to clear the critical walkway blockage between doors d_L0_004 and d_L0_006. |
| 14044 | 4 | move_piece | f_L1_035 | snap: f_L1_035: no free place on wall w_L1_024 (doors, windows) | Moving the shoe cabinet to the left wall (w_L1_024) to clear the 0.60m walkway between doors d_L1_006, o_L1_002 and d_L1_009 on the right side of the hall. |
| 14045 | 4 | remove_piece | f_L1_035 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Removing the shoe cabinet to clear the 0.60m walkway between doors d_L1_006, o_L1_002 and d_L1_009; the entrance group is optional and no free wall span can accommodate it without blocking circulation. |
| 14046 | 4 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s1: no place passes the checks (entrance: no candidate position fits the room) | Moving the entrance group to the bottom wall span s1 (0.75m) to clear the walkway between doors d_L1_006, o_L1_002 and d_L1_009. |
| 14607 | 6 | swap_model | f_L0_050 | exists: no piece 'f_L0_050' in a room of the building | Argus: the model's rests are 5.2 cm apart from the seat; a different model with proper rests is needed (fixes a:F14) |
| 14608 | 6 | swap_model | f_L0_051 | exists: no piece 'f_L0_051' in a room of the building | Argus: the model's rests are 5.2 cm apart from the seat; a different model with proper rests is needed (fixes a:F15) |
| 14609 | 6 | retype_piece | f_L1_006 | memory: the same edit was rejected in round 2: f_L1_004: no_overlap; f_L1_006: no_overlap; score: plausibility -32 -> -42 (F9 f_L1_006: floor_lamp f_L1_006 overlaps bed_double f_L1_004 by 0.16 m²) | Argus: f_L1_006 is drawn inside bed f_L1_004 and was named floor_lamp/nightstand by an AI pass; it should be typed as a floor_lamp to be built. (fixes a:F44) |
| 14613 | 6 | set_camera | r_L0_mutfak | memory: the same edit was rejected in round 1: show: none of the 8 best poses of r_L0_mutfak that show f_L0_040, f_L0_041 passes the camera checks: cam_r_L0_mutfak_1: furniture and fixtures fill 2% of its frame (at least 12%; the room's camera search frames more): a view of bare walls and ceiling gives no value; cam_r_L0_mutfak_1: none of the ro | Argus: The chair f_L0_040 is built in the kitchen but not seen in the one view that must show it. The camera is moved to show it (and f_L0_041, F54, in the same view). (fixes a:F53) |
| 14614 | 6 | set_camera | ext_4 | eye height 2.10 m above the ground (an exterior view: 1.5-1.7 m, or a high view above the ridge 7.55 m), the ground at (18, 0) is at z -0.50 m: use z 1.00 to 1.20 for an eye-level view | Argus: The window win_L0_006 is built on the facade but not seen in the exterior view ext_4. The camera is moved to show it (and win_L0_005, F56, in the same view). (fixes a:F55) |
| 14615 | 6 | add_camera | r_L1_ebeveyn_y_odasi | show: none of the 8 best poses of r_L1_ebeveyn_y_odasi that show f_L1_010, f_L1_015 passes the camera checks: duplicate: cam_r_L1_ebeveyn_y_odasi_4 would show the view cam_r_L1_ebeveyn_y_odasi_1 shows (within 1 m and 50 degrees of its pose): choose a pose that shows another part of r_L1_ebeveyn_y_odasi, or remove one of the two views; cam_r_L1_ebeveyn_y_odasi_4: none of the room's main pieces (bed_double, desk) is in its frame, while the room's camera search frames one | Argus: The documents name a dresser on L1; the model has no piece within 1.2 m. The build must add it (the code_fix is add_piece, but the tool is not available; the camera is added to show the desk f_L1_033 which is the nearest piece, and the furn (fixes a:F59) |
| 14616 | 6 | fix_fixture | f_L0_026 | no_change: f_L0_026: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The washbasin centre is 0.31 m from the left wall, under the 0.38 m clearance; swap_model was refused (fit rules). The code moves it to the nearest valid spot to restore clearance. (fixes a:F66) |
| 14617 | 6 | fix_fixture | f_L1_022 | no_change: f_L1_022: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet centre is 0.33 m from the right wall/fixture, under the 0.38 m clearance; the code moves it to the nearest valid spot. (fixes a:F67) |
| 14618 | 6 | fix_fixture | f_L1_023 | no_change: f_L1_023: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The washbasin centre is 0.31 m from the left wall, under the 0.38 m clearance; the code moves it to the nearest valid spot. (fixes a:F68) |
| 14619 | 6 | relayout_room | r_L1_cocuk_odasi | memory: the same edit was rejected in round 3: acceptance: finding F7:f_L1_007 is still there after the edit (bed_double blocks door d_L1_011); 5 more kept | Argus: The bedroom's bed (f_L1_004) is not placed (move_piece refused: it reaches through the room outline and overlaps f_L1_005). Re-solving the room's AI pieces with the best candidate re-places the bed so the room has its anchor. (fixes a:F69) |
| 14620 | 6 | set_camera | r_L1_dus | memory: the same edit was rejected in round 4: show: none of the 4 best poses of r_L1_dus that show f_L1_027 passes the camera checks: cam_r_L1_dus_1: none of the room's main pieces (shower, toilet, washbasin) is in its frame, while the room's camera search frames one; cam_r_L1_dus_1: furniture and fixtures fill 7% of its frame (at least 12%; th | Argus: The bathroom render does not show the primary fixture (washbasin); the camera is moved to a free pose that shows it. (fixes a:F70) |
| 14622 | 6 | swap_model | f_L1_029 | acceptance: pin_refused: f_L1_029: abo_B07GFT639N: fails the fit rules (caps, height, at most 0.88 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The desk (f_L1_029) is not built and the office chair stands alone; retype was refused (already a desk, and the score would drop). Swapping to a real desk model that fits the room restores the work/styled-surface layer. (fixes a:F75) |
| 14623 | 6 | fix_fixture | f_L0_024 | no_change: f_L0_024: nothing to fix (size within the real range, inside the room and off the doors) | Argus: The toilet is the bathroom's primary fixture and is not properly placed; swap_model was refused (fit rules). The code moves it to the nearest valid spot so it is present and clear. (fixes a:F76) |
| 14624 | 6 | swap_model | f_L1_009 | asset_unusable: gen_bathtub_modern_5_e14ba0b4 is not used: audit removed | Argus: The bathtub is the bathroom's main anchor and is not built (the previous swap asset was removed by audit). Swapping to a usable bathtub model restores the anchor. (fixes a:F77) |
| 14625 | 6 | place_group | r_L1_dus | memory: the same edit was rejected in round 2: no_change: r_L1_dus already has its bathroom_set r_L1_dus.bathroom_set (anchor f_L1_018, members f_L1_021, f_L1_027): nothing missing, never a second set | Argus: The bathroom r_L1_dus lacks a mirror and styling around the washbasin f_L1_027. (fixes a:F104) |
| 14626 | 6 | complete_group | r_L0_banyo.bathroom_set | memory: the same edit was rejected in round 1: unverified: r_L0_banyo.bathroom_set: the anchor f_L0_010 is unverified and not typed by code from the drawing (retype_piece first) | Argus: The bathroom r_L0_banyo has a washbasin but no mirror over it. (fixes a:F105) |
| 14627 | 6 | complete_group | r_L1_dus.bathroom_set | memory: the same edit was rejected in round 1: no_change: r_L1_dus.bathroom_set: nothing missing (members: f_L1_021, f_L1_027) | Argus: The bathroom r_L1_dus has a washbasin but no mirror over it. (fixes a:F106) |
| 14628 | 6 | rotate_piece | f_L0_017 | f_L0_017: clearance_ok, score: plausibility -119 -> -149 (F4 f_L0_017: armchair does not face its group (f_L0_021, f_L0_015); F6 f_L0_017: armchair: the free zone in front of it is blocked by f_L0_019; G11 f_L0_017: armchair f_L0_017: its front use zone is not reached by a 0.60 m walkway from door d_L0_006) | Argus: The armchair f_L0_017 is turned 29 degrees from its drawn position. (fixes a:F108) |
| 14629 | 6 | rotate_piece | f_L0_019 | f_L0_019: clearance_ok, score: plausibility -119 -> -139 (F4 f_L0_019: armchair does not face its group (f_L0_021, f_L0_015); F6 f_L0_019: armchair: the free zone in front of it is reaches out of the room) | Argus: The armchair f_L0_019 is turned 29 degrees from its drawn position. (fixes a:F109) |
| 14630 | 6 | swap_model | f_L1_005 | memory: the same edit was rejected in round 4: acceptance: pin_refused: f_L1_005: hssd_68b22165ccec115439ff5bca2a28bd2ebf1fdb9d: fails the fit rules (caps, height, at most 0.88 m high under the sloped ceiling): the refit keeps the model it had, so the swap changes nothing in the scene; swap to a real model of the type, or use another tool | Argus: The dresser f_L1_005 is 0.15 m from its drawn position. Swapping to a model that fits better may resolve the issue. (fixes a:F110) |
| 14631 | 6 | swap_model | f_L1_014 | memory: the same edit was rejected in round 4: pin_refused: f_L1_014: gen_wardrobe_rustic_1_97c119f6: a generated model (units guessed) while a real product of the type fits within the caps (hssd_602e95402b712af5ac6273ce4d2d2e6f57229516): the real model stays; swap to a real model of the type or use another tool | Argus: The wardrobe f_L1_014 is 0.05 m from its drawn position. Swapping to a model that fits better may resolve the issue. (fixes a:F111) |
| 14632 | 6 | set_exterior | exterior:site | site front_court yes: a sunken front court with parapet walls is the documents' or the brief's decision, never an edit's (the paved light well and its strip along the glazing stay); leave front_court out or use auto | Argus: The garden is bare flat grass with no planted beds, shrubs, or parking. Setting the site with a path, hedge, more trees, and a front court will add the missing landscape elements. (fixes a:F115) |
| 14633 | 6 | set_entrance | d_L0_001 | memory: the same edit was rejected in round 2: exists: 'd_L0_001' is no outside door of site.entrances | Argus: The entrance has bare concrete steps with no cheek walls, landing, or stone coping. Setting the entrance solution to 'steps' will build a proper entrance with steps, landing, and coping. (fixes a:F117) |
| 14634 | 6 | mark_not_furniture | f_L1_002 | no_crop: f_L1_002 is an untyped drawn piece: it is marked as not furniture only with its own recognition crop (the crop of its own question, or the one its review entry records); check/r_L1_cocuk_odasi_plan.jpg is not its crop (a whole sheet, a room's or camera's plan crop or another symbol's crop shows no reading of this piece); it has none, so it stays listed for review; CLAUDE.md removes a drawn piece only with its plan crop | Argus: The drawn piece 4.64 x 0.68 m in r_L1_cocuk_odasi is a cluster larger than 4.5 m on a side, not a single piece of furniture. It is likely a dimension line, axis bubble, or text frame. Marking it as not furniture with kind 'other' will remov (fixes a:F118) |
| 14635 | 6 | swap_model | f_L0_034 | acceptance: no target finding: an edit must name the finding it fixes (check id and target id) | Argus: The bookshelf f_L0_034 was removed by the AI but the documents show a bookshelf in the salon. The current model is not built. Swapping to hssd_8b3ad7f96cefa754be3171921c4c970be2d20b02 (0.98 x 0.36 x 2.16 m, minimal/modern) will build the bo (fixes a:F120) |
| 14638 | 6 | relayout_room | r_L1_hol | memory: the same edit was rejected in round 4: acceptance: finding G11:d_L1_006 is still there after the edit (no 0.60 m walkway from door d_L1_006 to door d_L1_009); 1 more kept | Candidate 2 has the best circulation score (0.85) and no hard failures; repositioning the entrance group to clear the G11 walkways between doors. |
| 14642 | 6 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s2: no place passes the checks (entrance: no candidate position fits the room) | Move the shoe cabinet to the short right wall span to free the walkway between doors d_L1_006 and d_L1_009. |
| 14645 | 6 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 1 is the only solver layout that resolves the critical walkway blockage between doors d_L0_004 and d_L0_006 and re-solves the seating groups. |
| 14646 | 6 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s4: no place passes the checks (entrance: no candidate position fits the room) | Move the shoe cabinet to the short right wall span near the top to free the walkway between doors d_L1_006 and d_L1_009. |
| 14648 | 6 | move_group | r_L1_hol.entrance | no_place: r_L1_hol.entrance on span r_L1_hol.s0: no place passes the checks (entrance: no candidate position fits the room) | Move the shoe cabinet to the short left wall span to free the walkway between doors d_L1_006 and d_L1_009. |
| 14649 | 6 | relayout_room | r_L0_salon | memory: the same edit was rejected in round 1: acceptance: finding G11:d_L0_004 is still there after the edit (no 0.60 m walkway from door d_L0_004 to door d_L0_006); 7 more kept | Candidate 2 has the same circulation score (0.92) as candidate 1 and may resolve the critical walkway blockage between doors d_L0_004 and d_L0_006. |
| 14653 | 6 | move_group | r_L1_hol.entrance | max_tries: r_L1_hol.entrance was edited 3 times in this round | Move the shoe cabinet to the left wall span s1 to free the walkway between doors d_L1_006 and d_L1_009. |

### Reported to other stages

| check | severity | target | room | stage | cause | rounds | why |
|---|---|---|---|---|---|---|---|
| F9 | major | f_L0_032 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4, 6 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| G8 | major | f_L0_031 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4, 6 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| M10 | minor | os_L0_veranda | - | site | outdoor_space | 1, 2, 3, 4, 6 | the verandas, balconies and terraces are planned by code from the documents (their floors, guards, covers and posts: wenart.levels.outdoor, site.space_platform); no agent tool changes them, so the finding is reported to the site stage |
| M17 | minor | r_L1_cocuk_odasi | r_L1_cocuk_odasi | decor | ceiling_light | 1, 2 | the ceiling lights of a room are hung by the decor stage's lighting rule (a row of pendants along each dining table, a light over each seating group, bed, desk and counter run, the lumen method's count for the floor: wenart.furniture.ceiling_lights); no agent tool adds a decor light, so the finding is reported to the decor stage |
| M19 | major | f_L0_026 | r_L0_banyo | architect | opening_sense | 1, 2, 3, 4, 6 | a door off its floor or into the air is the architect's (E1, O2, D4: its defaults turn such a door into a window or set its threshold); reported to the architect for the next build |
| M19 | major | f_L1_023 | r_L1_banyo | architect | opening_sense | 1, 2, 3, 4, 6 | a door off its floor or into the air is the architect's (E1, O2, D4: its defaults turn such a door into a window or set its threshold); reported to the architect for the next build |
| M21 | minor | f_L0_052 | r_L0_salon | layout | room_use | 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | f_L1_043 | r_L1_cocuk_odasi | layout | room_use | 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L0_salon | r_L0_salon | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M21 | minor | r_L1_ebeveyn_y_odasi | r_L1_ebeveyn_y_odasi | layout | room_use | 1, 2, 3, 4, 6 | the TV unit and TV of a living room, the sideboard, the bookshelves and their books, a bathroom's storage are added by code (wenart.furniture.media_wall, room_fill, tabletop.shelf_books) and the fit never takes a model the user rejected (catalog.user_rejection); the finding is reported to the layout stage |
| M32 | major | dec_L0_005 | - | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M32 | major | dec_L1_039 | - | decor | decor_rest | 1, 2, 3, 4 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M32 | major | f_L0_026 | r_L0_banyo | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| M32 | major | f_L1_023 | r_L1_banyo | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| Q7 | minor | d_L1_008 | r_L1_oda | openings | opening_style | 4 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | major | f_L1_034 | - | openings | opening_style | 6 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| Q7 | minor | o_L1_002 | r_L1_hol | openings | opening_style | 4, 6 | the door and window models are chosen by code for the whole building (one language); reported to the openings stage |
| RC | minor | sy_L0_002 | - | - | resolved_by_code | 1, 2, 3, 4, 6 | a reading conflict the code already resolved (the drawing won, the item was moved to the symbols): it names no furniture piece or room, so there is nothing to edit; reported |
| S2 | major | f_L0_031 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4, 6 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| S2 | major | f_L0_032 | r_L0_mutfak | - | drawn_layout | 1, 2, 3, 4, 6 | the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at most 0.5 m, and the code's search found no valid spot within that reach (inside the room, off the doors and the other pieces), so no edit clears the finding; it is reported for review |
| S5 | critical | dec_L0_041 | r_L0_mutfak | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L0_006 | r_L0_salon | decor | decor_rest | 1, 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_015 | r_L1_ebeveyn_y_odasi | decor | decor_rest | 2, 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_039 | r_L1_oda | decor | decor_rest | 2 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_041 | r_L1_cocuk_odasi | decor | decor_rest | 3, 4, 6 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| S5 | minor | f_L1_044 | r_L1_oda | decor | decor_rest | 3 | decor rest is placed by the decor stage on the built mesh (S5): no agent tool |
| X3 | critical | d_L1_010 | - | - | facade | 1, 2, 3, 4, 6 | the facade openings come from the drawings; no agent tool |
| X5 | minor | d_L0_001 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | o_L0_003 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | o_L0_005 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | o_L0_006 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_005 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |
| X5 | minor | win_L0_006 | - | - | scale | 1, 2, 3, 4, 6 | storey and door sizes come from the drawings |

### Context budget of the planner sessions

| round | session | status | cuts | characters removed | context (tokens) |
|---|---|---|---|---|---|
| 1 | r_L0_salon | cut | 6 | 34187 | 32768 |
| 2 | r_L1_ebeveyn_y_odasi | cut | 1 | 21625 | 32768 |
| 2 | r_L1_cocuk_odasi | cut | 1 | 11615 | 32768 |
| 3 | building | cut | 3 | 43866 | 32768 |
| 6 | building | cut | 1 | 21783 | 32768 |

### Inferred and AI-changed items

| id | kind | type | room | labels | change | by (rule) | reason |
|---|---|---|---|---|---|---|---|
| f_L0_001 | piece | stair | r_L0_mutfak | adjusted_by_ai | size 2.20 x 2.15 m -> 2.20 x 2.73 m | architect (architect K1) | a riser of 0.214 m is a drawing error (the stair is drawn with too few treads for its storey): the half landing becomes winders, the footprint stays as drawn |
| f_L0_002 | piece | kitchen_counter | r_L0_mutfak | adjusted_by_ai | - | code (architect F5) | architect F5: f_L0_002 (kitchen_counter) lies inside f_L0_032 (kitchen_counter): one object read twice; built once |
| f_L0_003 | piece | kitchen_counter | r_L0_mutfak | inferred | - | - | drawn inside the kitchen_counter f_L0_002 (60% or more of it): the same piece drawn twice, or a part of it (not built) |
| f_L0_004 | piece | unknown | r_L0_mutfak | inferred, adjusted_by_ai | - | code (reading.kitchen_outline) | the kitchen run drawn as one outline with its fixtures (sink: 8 circles): replaced by its counter legs f_L0_031, f_L0_032 along the walls (not built); plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_005 | piece | unknown | r_L0_salon | inferred | - | - | outline 3.89 x 1.42 m around 3 other piece(s) (f_L0_006, f_L0_007, f_L0_008): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L0_006 | piece | sofa | r_L0_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The cognac leather sofa is 70s style and does not match the modern Scandinavian feel. Swapping to a modern/scandinavian sofa (2.13 x 0.86 m) matches the project's reference style. (fixes a:F89) |
| f_L0_007 | piece | armchair | r_L0_salon | inferred | - | - | front: its back stands on the only side on a wall |
| f_L0_008 | piece | armchair | r_L0_salon | adjusted_by_ai | - | code (missing_front) | f_L0_008 (armchair) had no front: the side that looks into the most open floor, towards its partner (0 deg) |
| f_L0_009 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside sofa f_L0_006 (2.12 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_010 | piece | shower | r_L0_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | type unknown -> shower; size 2.54 x 1.01 m -> 1.55 x 0.75 m | architect | the drawn outline 2.54 x 1.01 m at 161.5 deg is no shower where it stands (a misread or merged outline): the real product 1.55 x 0.75 m seated in it, its back on a wall of the room and along it, in a corner, 94% of it on the drawn outline, clear of the other drawn fixtures and the door swings, clear of f_L0_026 (the answer to AI.move_piece:f_L0_010) (plan crop recognition/crops/sym_L0_005_ctx.png) |
| f_L0_011 | piece | table_dining | r_L0_salon | inferred, adjusted_by_ai | size 1.69 x 1.69 m -> 1.00 x 1.00 m | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (anchor); moved 0.04 m, sized 1.69 x 1.69 m -> 1.00 x 1.00 m (a real product size) |
| f_L0_012 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_013 | piece | unknown | r_L0_salon | inferred | - | - | drawn inside unknown f_L0_014 (1.52 x 0.78 m): a cushion, pillow or detail drawn on that piece, not a piece of its own (not built) |
| f_L0_014 | piece | sofa | r_L0_salon | inferred, adjusted_by_ai | - | architect | moved 0.41 m clear of d_L0_001 (the answer to AI.move_piece:f_L0_014) |
| f_L0_015 | piece | table_coffee | r_L0_salon | inferred | - | - | table_coffee: r_L0_salon misses it (r_L0_salon.seating (anchor f_L0_006) misses table_coffee) and the AI passes named it (pass 1 (qwen) answered table_coffee; pass 1 (qwen)'s reason names table_coffee); plan crop recognition/crops/sym_L0_010_ctx.png |
| f_L0_016 | piece | armchair | r_L0_salon | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dark angular armchair clashes with the warm neutral palette. Swapping to a minimal/modern/scandinavian armchair (0.91 x 0.76 m) matches the room's style. (fixes a:F88) |
| f_L0_017 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_018 | piece | armchair | r_L0_salon | inferred | - | - | front: faces the coffee table f_L0_021 |
| f_L0_019 | piece | armchair | r_L0_salon | inferred | - | - | armchair: the same drawn block (the same strokes (301 LINE here, within 2%)) and footprint (0.92 x 0.77 m, within 0.01 m) as f_L0_007, f_L0_016, f_L0_017, f_L0_018 (typed armchair): one block, one type; front: faces the coffee table f_L0_021 |
| f_L0_020 | piece | sink_kitchen | r_L0_mutfak | inferred, adjusted_by_ai | - | architect | moved 0.44 m clear of o_L0_004 (the answer to AI.move_piece:f_L0_020) |
| f_L0_021 | piece | table_coffee | r_L0_salon | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type floor_lamp -> table_coffee | code (ringed_table) | table_coffee: a drawn round floor_lamp (ai_two_pass) 0.66 m across with 4 seats around it (f_L0_016, f_L0_017, f_L0_018, f_L0_019) facing it: the table of the seating group, not a floor lamp (plan crop recognition/crops/sym_L0_016_ctx.png) |
| f_L0_024 | piece | toilet | r_L0_banyo | inferred | - | - | toilet: the same footprint (0.70 x 0.45 m) at the same plan position as f_L1_022 on level L1 (within 0.01 m) |
| f_L0_026 | piece | washbasin | r_L0_banyo | adjusted_by_ai | - | architect | moved 0.02 m along its wall to the nearest free place, clear of f_L0_010 (the answer to AI.move_piece:f_L0_026) (plan crop recognition/crops/sym_L0_021_ctx.png) |
| f_L0_027 | piece | chair | r_L0_salon | inferred | - | - | a 0.45 x 0.32 m seat 0.00 m from the table f_L0_011, facing it |
| f_L0_028 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.04 m |
| f_L0_029 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.08 m |
| f_L0_030 | piece | chair | r_L0_salon | inferred, adjusted_by_ai | - | solver | the drawn table_dining f_L0_011 is misread: 1.69 x 1.69 m is outside the product grid (depth 1.69 m is 41 % outside 0.7-1.2 m (square symbol: square products only); nearest real product 1.00 x 1.00 m): re-solved with its dining group as one unit around the drawn anchor (partner); moved 0.09 m |
| f_L1_003 | piece | unknown | r_L1_hol | inferred | - | - | 0.50 x 0.12 m fits no type and is thinner than 0.2 m: a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built) |
| f_L1_004 | piece | bed_double | r_L1_cocuk_odasi | inferred | - | - | front: its back stands on the only side on a wall |
| f_L1_005 | piece | dresser | r_L1_cocuk_odasi | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 (back_gap) | Shift dresser 0.26 m down to clear the overlap with bed f_L1_004. (plan crop recognition/crops/sym_L1_002_ctx.png) |
| f_L1_006 | piece | unknown | r_L1_cocuk_odasi | inferred | - | - | drawn inside bed_double f_L1_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L1_007 | piece | bed_double | r_L1_cocuk_odasi | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_008 | piece | nightstand | r_L1_cocuk_odasi | adjusted_by_ai | - | code (architect F5) | architect F5: it cut f_L1_007 (bed_double) by 0.40 m and no free place lies within 1.0 m; not built |
| f_L1_009 | piece | bathtub | r_L1_banyo | inferred, adjusted_by_ai (bath/shower longer than its bay shrunk, decision of 22 Oct 2026) | type unknown -> bathtub; size 2.42 x 0.98 m -> 1.55 x 0.75 m | architect | moved 0.01 m along its wall to the nearest free place, clear of f_L1_023 (the answer to AI.move_piece:f_L1_009) (plan crop recognition/crops/sym_L1_006_ctx.png) |
| f_L1_010 | piece | bed_double | r_L1_ebeveyn_y_odasi | inferred, adjusted_by_ai | - | code (back_gap) | bed_double f_L1_010: its back stood 0.06 m off its wall, parallel to it (a drawing gap): moved 0.04 m back onto the wall (plan crop recognition/crops/sym_L1_007_ctx.png) |
| f_L1_011 | piece | wardrobe | r_L1_soyunma_odasi | inferred, adjusted_by_ai | type unknown -> wardrobe; size 2.27 x 0.85 m -> 2.27 x 0.60 m | architect | moved 0.05 m along its wall to the nearest free place, clear of win_L1_001 (the answer to AI.move_piece:f_L1_011) |
| f_L1_012 | piece | wardrobe | r_L1_soyunma_odasi | inferred, adjusted_by_ai | type unknown -> wardrobe; size 2.27 x 0.85 m -> 2.27 x 0.60 m | Qwen/Qwen3.8-27B-FP8 (wardrobe_run) | Bring wardrobe f_L1_012 height back into the 1.50-2.45 m range (S4) by resizing to a real wardrobe size. |
| f_L1_013 | piece | bed_single | r_L1_oda_2 | inferred | - | - | bed_single: the bedroom room misses its anchor (bed_double \| bed_single), and the type's product range fits 1.90 x 0.90 m (the only missing member of that size); front: standing in a corner: its short side on the wall is the back |
| f_L1_014 | piece | wardrobe | r_L1_oda_2 | inferred, adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Shift wardrobe 0.05 m in -x so its back edge clears wall w_L1_024 and the room outline (F9/S2). |
| f_L1_015 | piece | armchair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 (missing_front) | Argus: The two armchairs are different models/colours; swapping f_L1_015 to the modern abo_B075X2WN36 (0.85 x 0.78 x 0.89 m) aligns the pair. (fixes a:F201) |
| f_L1_016 | piece | armchair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 (missing_front) | Match the second armchair to the first (same model) so the seating pair reads as a cohesive set (D3). |
| f_L1_017 | piece | dresser | r_L1_oda_2 | inferred | - | - | dresser: the documents name it: the text '*SIFONIYER' (TEXT:29ABD3) stands on the footprint (within 1.2 m, the nearest drawn piece of that size), and the type's product range fits 1.20 x 0.55 m within 40% |
| f_L1_018 | piece | shower | r_L1_dus | inferred | - | - | front: the free side facing the most room is the front |
| f_L1_019 | piece | washing_machine | r_L1_banyo | inferred, adjusted_by_ai (code retype of a vision-typed piece, decision of 22 Oct 2026) | type washbasin -> washing_machine | code (free_front) | washing_machine: the documents name it: the text 'çamaşır mak.' (TEXT:2772EB) is written 0.01 m from it; the ai_two_pass reading said washbasin; the named type's product range fits 0.60 x 0.60 m and the room holds it (trust order: the documents' text before AI vision); plan crop recognition/crops/sym_L1_016_ctx.png; washing_machine f_L1_019: its front (270 deg) had 0.00 m free (the wall in the way; its door or drawers need 0.45 m to open, 0.60 m to use): a front read the wrong way round (a reading error): turned 90 deg in place to its free side (180 deg), its back on a wall |
| f_L1_020 | piece | floor_lamp | r_L1_ebeveyn_y_odasi | inferred, adjusted_by_ai | size 0.58 x 0.58 m -> 0.40 x 0.40 m | Qwen/Qwen3.8-27B-FP8 | Argus: The current lamp is a dated style; the 0.40 x 0.40 x 1.62 m minimal/modern lamp fits the footprint and the room's look. (fixes a:F202) |
| f_L1_023 | piece | washbasin | r_L1_banyo | adjusted_by_ai | - | architect | moved 0.01 m along its wall to the nearest free place, clear of f_L1_009 (the answer to AI.move_piece:f_L1_023) (plan crop recognition/crops/sym_L1_020_ctx.png) |
| f_L1_024 | piece | nightstand | r_L1_ebeveyn_y_odasi | inferred, adjusted_by_ai | - | code (back_gap) | nightstand f_L1_024: its back stood 0.06 m off its wall, parallel to it (a drawing gap): moved 0.04 m back onto the wall (plan crop recognition/crops/sym_L1_021_ctx.png) |
| f_L1_025 | piece | nightstand | r_L1_oda_2 | inferred, adjusted_by_ai | - | code (back_gap) | nightstand f_L1_025: its back stood 0.07 m off its wall, parallel to it (a drawing gap): moved 0.05 m back onto the wall (plan crop recognition/crops/sym_L1_022_ctx.png) |
| f_L1_026 | piece | nightstand | r_L1_ebeveyn_y_odasi | inferred, adjusted_by_ai | - | code (back_gap) | nightstand f_L1_026: its back stood 0.06 m off its wall, parallel to it (a drawing gap): moved 0.04 m back onto the wall (plan crop recognition/crops/sym_L1_023_ctx.png) |
| f_L1_027 | piece | washbasin | r_L1_dus | inferred, adjusted_by_ai | - | code (reading.fixed_equipment) | misread fixed equipment (CLAUDE.md, user OK of 10 Oct 2026): through a wall: moved 0.05 m to the nearest free spot (plan crop recognition/crops/sym_L1_024_ctx.png) |
| f_L0_031 | piece | kitchen_counter | r_L0_mutfak | inferred, adjusted_by_ai | type unknown -> kitchen_counter; size 3.99 x 2.40 m -> 3.19 x 0.60 m | code (reading.kitchen_outline) | the kitchen run drawn as one 3.99 x 2.40 m outline f_L0_004 with its fixtures (sink: 8 circles) in the kitchen: a counter leg 3.19 x 0.60 m along its wall side, facing the room (inferred); the outline stopped 0.58 m short of the wall behind f_L0_020: the run reaches that wall; plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_032 | piece | kitchen_counter | r_L0_mutfak | inferred, adjusted_by_ai | type unknown -> kitchen_counter; size 3.99 x 2.40 m -> 2.38 x 0.60 m | code (reading.kitchen_outline) | the kitchen run drawn as one 3.99 x 2.40 m outline f_L0_004 with its fixtures (sink: 8 circles) in the kitchen: a counter leg 2.38 x 0.60 m along its wall side, facing the room (inferred); the outline stopped 0.58 m short of the wall behind f_L0_020: the run reaches that wall; plan crop recognition/reading/f_L0_004_ctx.png |
| f_L0_034 | piece | bookshelf | r_L0_salon | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_034: the piece is not built |
| f_L0_035 | piece | potted_plant | r_L0_salon | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_035: the piece is not built |
| f_L0_037 | piece | ottoman | r_L0_salon | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L0_037: the piece is not built |
| f_L0_040 | piece | chair | r_L0_mutfak | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The dark heavy wood chair clashes with the light oak table and pale modern kitchen. Swapping to a minimal/modern/scandinavian chair (0.44 x 0.42 m) matches the room's style. (fixes a:F86) |
| f_L1_029 | piece | desk | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_029: the piece is not built |
| f_L1_030 | piece | office_chair | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_030: the piece is not built |
| f_L1_031 | piece | floor_lamp | r_L1_ebeveyn_y_odasi | adjusted_by_ai | - | architect | the answer to AI.remove_piece:f_L1_031: the piece is not built |
| f_L0_048 | piece | sofa | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots and a lantern (2 reference photos)) |
| f_L0_049 | piece | table_coffee | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots and a lantern (2 reference photos)) |
| f_L0_050 | piece | armchair | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots and a lantern (2 reference photos)) |
| f_L0_051 | piece | armchair | - | inferred | - | - | lounge set of the veranda os_L0_veranda (recipe: good veranda photos show a place to sit, plants in big pots and a lantern (2 reference photos)) |
| f_L1_042 | piece | office_chair | r_L1_cocuk_odasi | adjusted_by_ai | - | Qwen/Qwen3.8-27B-FP8 | Argus: The black leather office chair (model 3dwh_2be96519caebb57579ea6e05) clashes with the child's bedroom. Swapping to the scandinavian/minimal model hssd_d6f9b4561838f68f34d3fc36a7b700bc2c180253 (0.60 x 0.61 x 0.75 m) keeps the office_chair ty (fixes a:F99) |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_banyo_1 | ![](agent/r1_cam_r_L0_banyo_1_before.jpg) | ![](agent/r1_cam_r_L0_banyo_1_after.jpg) |
| 1 | cam_r_L0_salon_1 | ![](agent/r1_cam_r_L0_salon_1_before.jpg) | ![](agent/r1_cam_r_L0_salon_1_after.jpg) |
| 1 | cam_r_L0_salon_2 | ![](agent/r1_cam_r_L0_salon_2_before.jpg) | ![](agent/r1_cam_r_L0_salon_2_after.jpg) |
| 1 | cam_r_L0_salon_3 | ![](agent/r1_cam_r_L0_salon_3_before.jpg) | ![](agent/r1_cam_r_L0_salon_3_after.jpg) |
| 1 | cam_r_L1_cocuk_odasi_1 | ![](agent/r1_cam_r_L1_cocuk_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_cocuk_odasi_1_after.jpg) |
| 1 | cam_r_L1_cocuk_odasi_2 | ![](agent/r1_cam_r_L1_cocuk_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_cocuk_odasi_2_after.jpg) |
| 1 | cam_r_L1_cocuk_odasi_3 | ![](agent/r1_cam_r_L1_cocuk_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_cocuk_odasi_3_after.jpg) |
| 1 | cam_r_L1_dus_1 | ![](agent/r1_cam_r_L1_dus_1_before.jpg) | ![](agent/r1_cam_r_L1_dus_1_after.jpg) |
| 1 | cam_r_L1_ebeveyn_y_odasi_1 | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_1_after.jpg) |
| 1 | cam_r_L1_ebeveyn_y_odasi_2 | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_2_after.jpg) |
| 1 | cam_r_L1_ebeveyn_y_odasi_3 | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_3_before.jpg) | ![](agent/r1_cam_r_L1_ebeveyn_y_odasi_3_after.jpg) |
| 1 | cam_r_L1_hol_1 | ![](agent/r1_cam_r_L1_hol_1_before.jpg) | ![](agent/r1_cam_r_L1_hol_1_after.jpg) |
| 1 | cam_r_L1_oda_1 | ![](agent/r1_cam_r_L1_oda_1_before.jpg) | ![](agent/r1_cam_r_L1_oda_1_after.jpg) |
| 1 | cam_r_L1_oda_2_1 | ![](agent/r1_cam_r_L1_oda_2_1_before.jpg) | ![](agent/r1_cam_r_L1_oda_2_1_after.jpg) |
| 1 | cam_r_L1_oda_2_2 | ![](agent/r1_cam_r_L1_oda_2_2_before.jpg) | ![](agent/r1_cam_r_L1_oda_2_2_after.jpg) |
| 1 | cam_r_L1_soyunma_odasi_1 | ![](agent/r1_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r1_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 1 | cam_r_L1_soyunma_odasi_2 | ![](agent/r1_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r1_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 2 | cam_r_L0_banyo_1 | ![](agent/r2_cam_r_L0_banyo_1_before.jpg) | ![](agent/r2_cam_r_L0_banyo_1_after.jpg) |
| 2 | cam_r_L0_mutfak_1 | ![](agent/r2_cam_r_L0_mutfak_1_before.jpg) | ![](agent/r2_cam_r_L0_mutfak_1_after.jpg) |
| 2 | cam_r_L0_mutfak_2 | ![](agent/r2_cam_r_L0_mutfak_2_before.jpg) | ![](agent/r2_cam_r_L0_mutfak_2_after.jpg) |
| 2 | cam_r_L0_mutfak_3 | ![](agent/r2_cam_r_L0_mutfak_3_before.jpg) | ![](agent/r2_cam_r_L0_mutfak_3_after.jpg) |
| 2 | cam_r_L0_salon_1 | ![](agent/r2_cam_r_L0_salon_1_before.jpg) | ![](agent/r2_cam_r_L0_salon_1_after.jpg) |
| 2 | cam_r_L0_salon_2 | ![](agent/r2_cam_r_L0_salon_2_before.jpg) | ![](agent/r2_cam_r_L0_salon_2_after.jpg) |
| 2 | cam_r_L0_salon_3 | ![](agent/r2_cam_r_L0_salon_3_before.jpg) | ![](agent/r2_cam_r_L0_salon_3_after.jpg) |
| 2 | cam_r_L1_banyo_1 | ![](agent/r2_cam_r_L1_banyo_1_before.jpg) | ![](agent/r2_cam_r_L1_banyo_1_after.jpg) |
| 2 | cam_r_L1_banyo_2 | ![](agent/r2_cam_r_L1_banyo_2_before.jpg) | ![](agent/r2_cam_r_L1_banyo_2_after.jpg) |
| 2 | cam_r_L1_cocuk_odasi_1 | ![](agent/r2_cam_r_L1_cocuk_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_cocuk_odasi_1_after.jpg) |
| 2 | cam_r_L1_cocuk_odasi_2 | ![](agent/r2_cam_r_L1_cocuk_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_cocuk_odasi_2_after.jpg) |
| 2 | cam_r_L1_cocuk_odasi_3 | ![](agent/r2_cam_r_L1_cocuk_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_cocuk_odasi_3_after.jpg) |
| 2 | cam_r_L1_dus_1 | ![](agent/r2_cam_r_L1_dus_1_before.jpg) | ![](agent/r2_cam_r_L1_dus_1_after.jpg) |
| 2 | cam_r_L1_dus_2 | ![](agent/r2_cam_r_L1_dus_2_before.jpg) | ![](agent/r2_cam_r_L1_dus_2_after.jpg) |
| 2 | cam_r_L1_ebeveyn_y_odasi_1 | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_1_after.jpg) |
| 2 | cam_r_L1_ebeveyn_y_odasi_2 | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_2_after.jpg) |
| 2 | cam_r_L1_ebeveyn_y_odasi_3 | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_3_before.jpg) | ![](agent/r2_cam_r_L1_ebeveyn_y_odasi_3_after.jpg) |
| 2 | cam_r_L1_hol_1 | ![](agent/r2_cam_r_L1_hol_1_before.jpg) | ![](agent/r2_cam_r_L1_hol_1_after.jpg) |
| 2 | cam_r_L1_oda_1 | ![](agent/r2_cam_r_L1_oda_1_before.jpg) | ![](agent/r2_cam_r_L1_oda_1_after.jpg) |
| 2 | cam_r_L1_oda_2_1 | ![](agent/r2_cam_r_L1_oda_2_1_before.jpg) | ![](agent/r2_cam_r_L1_oda_2_1_after.jpg) |
| 2 | cam_r_L1_oda_2_2 | ![](agent/r2_cam_r_L1_oda_2_2_before.jpg) | ![](agent/r2_cam_r_L1_oda_2_2_after.jpg) |
| 2 | cam_r_L1_soyunma_odasi_1 | ![](agent/r2_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r2_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 2 | cam_r_L1_soyunma_odasi_2 | ![](agent/r2_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r2_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 2 | ext_1 | ![](agent/r2_ext_1_before.jpg) | ![](agent/r2_ext_1_after.jpg) |
| 2 | ext_2 | ![](agent/r2_ext_2_before.jpg) | ![](agent/r2_ext_2_after.jpg) |
| 2 | ext_3 | ![](agent/r2_ext_3_before.jpg) | ![](agent/r2_ext_3_after.jpg) |
| 2 | ext_4 | ![](agent/r2_ext_4_before.jpg) | ![](agent/r2_ext_4_after.jpg) |
| 2 | ext_5 | ![](agent/r2_ext_5_before.jpg) | ![](agent/r2_ext_5_after.jpg) |
| 2 | ext_6 | ![](agent/r2_ext_6_before.jpg) | ![](agent/r2_ext_6_after.jpg) |
| 3 | cam_r_L1_oda_1 | ![](agent/r3_cam_r_L1_oda_1_before.jpg) | ![](agent/r3_cam_r_L1_oda_1_after.jpg) |
| 3 | cam_r_L1_soyunma_odasi_1 | ![](agent/r3_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r3_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 3 | cam_r_L1_soyunma_odasi_2 | ![](agent/r3_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r3_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 4 | cam_r_L0_banyo_1 | ![](agent/r4_cam_r_L0_banyo_1_before.jpg) | ![](agent/r4_cam_r_L0_banyo_1_after.jpg) |
| 4 | cam_r_L0_mutfak_1 | ![](agent/r4_cam_r_L0_mutfak_1_before.jpg) | ![](agent/r4_cam_r_L0_mutfak_1_after.jpg) |
| 4 | cam_r_L0_mutfak_2 | ![](agent/r4_cam_r_L0_mutfak_2_before.jpg) | ![](agent/r4_cam_r_L0_mutfak_2_after.jpg) |
| 4 | cam_r_L0_mutfak_3 | ![](agent/r4_cam_r_L0_mutfak_3_before.jpg) | ![](agent/r4_cam_r_L0_mutfak_3_after.jpg) |
| 4 | cam_r_L0_salon_1 | ![](agent/r4_cam_r_L0_salon_1_before.jpg) | ![](agent/r4_cam_r_L0_salon_1_after.jpg) |
| 4 | cam_r_L0_salon_2 | ![](agent/r4_cam_r_L0_salon_2_before.jpg) | ![](agent/r4_cam_r_L0_salon_2_after.jpg) |
| 4 | cam_r_L0_salon_3 | ![](agent/r4_cam_r_L0_salon_3_before.jpg) | ![](agent/r4_cam_r_L0_salon_3_after.jpg) |
| 4 | cam_r_L1_banyo_1 | ![](agent/r4_cam_r_L1_banyo_1_before.jpg) | ![](agent/r4_cam_r_L1_banyo_1_after.jpg) |
| 4 | cam_r_L1_banyo_2 | ![](agent/r4_cam_r_L1_banyo_2_before.jpg) | ![](agent/r4_cam_r_L1_banyo_2_after.jpg) |
| 4 | cam_r_L1_cocuk_odasi_1 | ![](agent/r4_cam_r_L1_cocuk_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_cocuk_odasi_1_after.jpg) |
| 4 | cam_r_L1_cocuk_odasi_2 | ![](agent/r4_cam_r_L1_cocuk_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_cocuk_odasi_2_after.jpg) |
| 4 | cam_r_L1_cocuk_odasi_3 | ![](agent/r4_cam_r_L1_cocuk_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_cocuk_odasi_3_after.jpg) |
| 4 | cam_r_L1_dus_1 | ![](agent/r4_cam_r_L1_dus_1_before.jpg) | ![](agent/r4_cam_r_L1_dus_1_after.jpg) |
| 4 | cam_r_L1_dus_2 | ![](agent/r4_cam_r_L1_dus_2_before.jpg) | ![](agent/r4_cam_r_L1_dus_2_after.jpg) |
| 4 | cam_r_L1_ebeveyn_y_odasi_1 | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_1_after.jpg) |
| 4 | cam_r_L1_ebeveyn_y_odasi_2 | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_2_after.jpg) |
| 4 | cam_r_L1_ebeveyn_y_odasi_3 | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_3_before.jpg) | ![](agent/r4_cam_r_L1_ebeveyn_y_odasi_3_after.jpg) |
| 4 | cam_r_L1_hol_1 | ![](agent/r4_cam_r_L1_hol_1_before.jpg) | ![](agent/r4_cam_r_L1_hol_1_after.jpg) |
| 4 | cam_r_L1_oda_1 | ![](agent/r4_cam_r_L1_oda_1_before.jpg) | ![](agent/r4_cam_r_L1_oda_1_after.jpg) |
| 4 | cam_r_L1_oda_2_1 | ![](agent/r4_cam_r_L1_oda_2_1_before.jpg) | ![](agent/r4_cam_r_L1_oda_2_1_after.jpg) |
| 4 | cam_r_L1_oda_2_2 | ![](agent/r4_cam_r_L1_oda_2_2_before.jpg) | ![](agent/r4_cam_r_L1_oda_2_2_after.jpg) |
| 4 | cam_r_L1_soyunma_odasi_1 | ![](agent/r4_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r4_cam_r_L1_soyunma_odasi_1_after.jpg) |
| 4 | cam_r_L1_soyunma_odasi_2 | ![](agent/r4_cam_r_L1_soyunma_odasi_2_before.jpg) | ![](agent/r4_cam_r_L1_soyunma_odasi_2_after.jpg) |
| 4 | ext_1 | ![](agent/r4_ext_1_before.jpg) | ![](agent/r4_ext_1_after.jpg) |
| 4 | ext_2 | ![](agent/r4_ext_2_before.jpg) | ![](agent/r4_ext_2_after.jpg) |
| 4 | ext_3 | ![](agent/r4_ext_3_before.jpg) | ![](agent/r4_ext_3_after.jpg) |
| 4 | ext_4 | ![](agent/r4_ext_4_before.jpg) | ![](agent/r4_ext_4_after.jpg) |
| 4 | ext_5 | ![](agent/r4_ext_5_before.jpg) | ![](agent/r4_ext_5_after.jpg) |
| 4 | ext_6 | ![](agent/r4_ext_6_before.jpg) | ![](agent/r4_ext_6_after.jpg) |
| 6 | cam_r_L0_banyo_1 | ![](agent/r6_cam_r_L0_banyo_1_before.jpg) | ![](agent/r6_cam_r_L0_banyo_1_after.jpg) |
| 6 | cam_r_L0_salon_1 | ![](agent/r6_cam_r_L0_salon_1_before.jpg) | ![](agent/r6_cam_r_L0_salon_1_after.jpg) |
| 6 | cam_r_L0_salon_2 | ![](agent/r6_cam_r_L0_salon_2_before.jpg) | ![](agent/r6_cam_r_L0_salon_2_after.jpg) |
| 6 | cam_r_L0_salon_3 | ![](agent/r6_cam_r_L0_salon_3_before.jpg) | ![](agent/r6_cam_r_L0_salon_3_after.jpg) |
| 6 | cam_r_L1_soyunma_odasi_1 | ![](agent/r6_cam_r_L1_soyunma_odasi_1_before.jpg) | ![](agent/r6_cam_r_L1_soyunma_odasi_1_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

- no brief.yaml in /workspace/repo/projects/real06: every brief value is a default
- cam_r_L0_banyo_2: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- cam_r_L1_oda_2_3: in the polish manifest but not in the render manifest (an earlier run's camera; not a view of this report)
- final/cam_r_L0_banyo_2_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_banyo_2_final_preview_2.jpg
- final/cam_r_L1_oda_2_3_final_preview.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_oda_2_3_final_preview_2.jpg
- final/cam_r_L0_banyo_2_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L0_banyo_2_plan_2.jpg
- final/cam_r_L1_oda_2_3_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/cam_r_L1_oda_2_3_plan_2.jpg
- final/top_L0_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L0_plan_2.jpg
- final/top_L1_plan.jpg is from an earlier run (not part of this report): moved to final/earlier_run/top_L1_plan_2.jpg
