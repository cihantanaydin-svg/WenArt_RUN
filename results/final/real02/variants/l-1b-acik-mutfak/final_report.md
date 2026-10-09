# Final report: real02

17 views: 8 polished, 9 Cycles (gate_validation 5, room 3, vision_check 1). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 17 |
| interior / exterior views | 12 / 5 |
| variant | l-1b-acik-mutfak |
| polished | 8 |
| Cycles | 9 (gate_validation 5, room 3, vision_check 1) |
| confirmed mismatches on the final image | 2 in 2 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 2 |
| unverified pieces in view (sum over views) | 32 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 9 |
| exposure | -0.67 .. +5.50 EV (0 at a limit), modes auto |
| window pull | 12 view(s), -1 .. 0 EV |
| camera policy | m5 5, search 12 |
| camera score (min / mean / max) | 2.50 / 2.88 / 3.34 |
| rooms by number of views | 4 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 2.4 min / 39.8 s / 15.5 s |
| seconds: polish / gate / check | 69.1 s / 6.3 s / 6.2 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 5 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real02-l-1b-acik-mutfak.blend](3d/real02-l-1b-acik-mutfak.blend) | 204.5 MB |
| [real02-l-1b-acik-mutfak.glb](3d/real02-l-1b-acik-mutfak.glb) | 534.8 MB |

17 cameras; textures scaled to at most 1024 px (164 scaled) for the download.

## Advisory flags and open items

- vision check advisory: removal_flagged 0.5 misses >= 0.8; removal_confirmed 0.0 misses >= 0.6; insertion 0.5 misses >= 0.6
- check target missed: removal_flagged 0.500 (needs >= 0.8)
- check target missed: removal_confirmed 0.000 (needs >= 0.6)
- check target missed: insertion 0.500 (needs >= 0.6)
- 42 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L-1_022, f_L-1_024, f_L-1_033, f_L-1_034, f_L-1_035, f_L-1_036, f_L-1_045, f_L-1_046
- 14 drawn piece(s) without an AI answer (not asked, or the answers were not applied; unknown, unverified; footprint kept): f_L-1_001, f_L-1_002, f_L-1_005, f_L-1_006, f_L-1b_001, f_L-1b_002, f_L-1b_005, f_L-1b_006
- the polish added an object in cam_r_L-1b_koridor_1: the Cycles render is final
- exterior gate polish_disabled: the exterior views are the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- AI completion: 68 proposal(s) refused, reverted or not placed (listed per room)

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 100.0 % (limit 95 %), 64 comparisons |
| negative controls rejected | 97.7 % (limit 90 %), 176 comparisons |
| effect | polish allowed |

### Exterior views

Exterior decision: **polish_disabled**. The exterior views are the Cycles render; the rooms are not affected.

| item | value |
|---|---|
| benign exterior comparisons accepted | 100.0 % (limit 95 %), 24 comparisons |
| negative exterior comparisons rejected | 84.6 % (limit 90 %), 52 comparisons |

Reasons:

- negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L-1b: [contact_L-1b.jpg](contact_L-1b.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- exterior_l-1b-acik-mutfak: [contact_sbs_exterior_l-1b-acik-mutfak.jpg](contact_sbs_exterior_l-1b-acik-mutfak.jpg)

- r_L-1b_acik_mutfak: [contact_sbs_r_L-1b_acik_mutfak.jpg](contact_sbs_r_L-1b_acik_mutfak.jpg)

- r_L-1b_acik_mutfak_2: [contact_sbs_r_L-1b_acik_mutfak_2.jpg](contact_sbs_r_L-1b_acik_mutfak_2.jpg)

- r_L-1b_koridor: [contact_sbs_r_L-1b_koridor.jpg](contact_sbs_r_L-1b_koridor.jpg)

- r_L-1b_oda: [contact_sbs_r_L-1b_oda.jpg](contact_sbs_r_L-1b_oda.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| exterior_l-1b-acik-mutfak | ext_1 | - | - | info | - | - | cycles (gate_validation) |
| exterior_l-1b-acik-mutfak | ext_2 | - | - | info | - | - | cycles (gate_validation) |
| exterior_l-1b-acik-mutfak | ext_3 | - | - | mismatch (1) | - | - | cycles (gate_validation) |
| exterior_l-1b-acik-mutfak | ext_4 | - | - | info | - | - | cycles (gate_validation) |
| exterior_l-1b-acik-mutfak | ext_5 | - | - | mismatch (1) | - | - | cycles (gate_validation) |
| r_L-1b_acik_mutfak | cam_r_L-1b_acik_mutfak_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1b_acik_mutfak | cam_r_L-1b_acik_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1b_acik_mutfak | cam_r_L-1b_acik_mutfak_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L-1b_acik_mutfak_2 | cam_r_L-1b_acik_mutfak_2_1 | - | - | info | - | - | cycles (room) |
| r_L-1b_acik_mutfak_2 | cam_r_L-1b_acik_mutfak_2_2 | - | - | info | - | - | cycles (room) |
| r_L-1b_acik_mutfak_2 | cam_r_L-1b_acik_mutfak_2_3 | - | - | info | - | - | cycles (room) |
| r_L-1b_koridor | cam_r_L-1b_koridor_1 | a2 s 0.25 canny x0.8 | accept | info | mismatch (1) | added_by_polish | cycles (vision_check) |
| r_L-1b_koridor | cam_r_L-1b_koridor_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1b_koridor | cam_r_L-1b_koridor_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1b_oda | cam_r_L-1b_oda_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L-1b_oda | cam_r_L-1b_oda_2 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |
| r_L-1b_oda | cam_r_L-1b_oda_3 | a2 s 0.25 canny x0.8 | accept | info | info | calibrated | polished |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | r_L-1b_acik_mutfak | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.17 | -1 | search 3.02 | D5 A1 | 2 | no | [preview](cam_r_L-1b_acik_mutfak_1_final_preview.jpg) |
| cam_r_L-1b_acik_mutfak_2 | r_L-1b_acik_mutfak | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.83 | -1 | search 2.93 | D8 | 7 | no | [preview](cam_r_L-1b_acik_mutfak_2_final_preview.jpg) |
| cam_r_L-1b_acik_mutfak_2_1 | r_L-1b_acik_mutfak_2 | L-1b | cycles | room | - | - | info | - | - | +4.83 | -1 | search 2.84 | D6 | 3 | no | [preview](cam_r_L-1b_acik_mutfak_2_1_final_preview.jpg) |
| cam_r_L-1b_acik_mutfak_2_2 | r_L-1b_acik_mutfak_2 | L-1b | cycles | room | - | - | info | - | - | +5.33 | -1 | search 2.81 | D9 A4 | 6 | no | [preview](cam_r_L-1b_acik_mutfak_2_2_final_preview.jpg) |
| cam_r_L-1b_acik_mutfak_2_3 | r_L-1b_acik_mutfak_2 | L-1b | cycles | room | - | - | info | - | - | +5.50 | -1 | search 2.77 | D8 A1 | 6 | no | [preview](cam_r_L-1b_acik_mutfak_2_3_final_preview.jpg) |
| cam_r_L-1b_acik_mutfak_3 | r_L-1b_acik_mutfak | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | +3.83 | -1 | search 2.80 | D3 A1 | 2 | no | [preview](cam_r_L-1b_acik_mutfak_3_final_preview.jpg) |
| cam_r_L-1b_koridor_1 | r_L-1b_koridor | L-1b | cycles | vision_check | a2 s 0.25 canny x0.8 | accept | info | mismatch (1) | not preferred 0/4 | -0.67 | 0 | search 3.34 | D7 A1 | 4 | no | [preview](cam_r_L-1b_koridor_1_final_preview.jpg) |
| cam_r_L-1b_koridor_2 | r_L-1b_koridor | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.33 | - | search 3.11 | D2 A1 | 0 | no | [preview](cam_r_L-1b_koridor_2_final_preview.jpg) |
| cam_r_L-1b_koridor_3 | r_L-1b_koridor | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | -0.50 | - | search 2.50 | D2 A1 | 0 | no | [preview](cam_r_L-1b_koridor_3_final_preview.jpg) |
| cam_r_L-1b_oda_1 | r_L-1b_oda | L-1b | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.50 | - | search 2.90 | D2 A4 | 1 | no | [preview](cam_r_L-1b_oda_1_final_preview.jpg) |
| cam_r_L-1b_oda_2 | r_L-1b_oda | L-1b | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | -0.50 | - | search 2.88 | D2 A3 | 1 | no | [preview](cam_r_L-1b_oda_2_final_preview.jpg) |
| cam_r_L-1b_oda_3 | r_L-1b_oda | L-1b | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | -0.67 | - | search 2.70 | D1 A4 | 0 | no | [preview](cam_r_L-1b_oda_3_final_preview.jpg) |
| ext_1 | - | unknown | cycles | gate_validation | - | - | info | - | - | -0.50 | 0 | m5 | D4 | 0 | no | [preview](ext_1_final_preview.jpg) |
| ext_2 | - | unknown | cycles | gate_validation | - | - | info | - | - | +1.17 | 0 | m5 | D4 | 0 | no | [preview](ext_2_final_preview.jpg) |
| ext_3 | - | unknown | cycles | gate_validation | - | - | mismatch (1) | - | - | +1.17 | -1 | m5 | D6 | 0 | yes | [preview](ext_3_final_preview.jpg) |
| ext_4 | - | unknown | cycles | gate_validation | - | - | info | - | - | -0.33 | 0 | m5 | D6 | 0 | no | [preview](ext_4_final_preview.jpg) |
| ext_5 | - | unknown | cycles | gate_validation | - | - | mismatch (1) | - | - | -0.50 | 0 | m5 | D4 | 0 | yes | [preview](ext_5_final_preview.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L-1b_acik_mutfak | kitchen | L-1b | 3 | 3 | 0 | cam_r_L-1b_acik_mutfak_1, cam_r_L-1b_acik_mutfak_2, cam_r_L-1b_acik_mutfak_3 |
| r_L-1b_acik_mutfak_2 | kitchen | L-1b | 3 | 0 | 3 | cam_r_L-1b_acik_mutfak_2_1, cam_r_L-1b_acik_mutfak_2_2, cam_r_L-1b_acik_mutfak_2_3 |
| r_L-1b_banyo | bathroom | L-1b | 0 | 0 | 0 | - |
| r_L-1b_banyo_2 | bathroom | L-1b | 0 | 0 | 0 | - |
| r_L-1b_koridor | hall | L-1b | 3 | 2 | 1 | cam_r_L-1b_koridor_1, cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3 |
| r_L-1b_koridor_2 | hall | L-1b | 0 | 0 | 0 | - |
| r_L-1b_oda | other | L-1b | 3 | 3 | 0 | cam_r_L-1b_oda_1, cam_r_L-1b_oda_2, cam_r_L-1b_oda_3 |
| r_L-1b_oda_2 | other | L-1b | 0 | 0 | 0 | - |
| r_L0_banyo | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_banyo_2 | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_banyo | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_banyo_2 | bathroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_yatak_odasi | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_e_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_koridor | hall | L0 | 0 | 0 | 0 | - |
| r_L0_koridor_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_oda | hall | L0 | 0 | 0 | 0 | - |
| r_L0_oda_2 | hall | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_2 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_3 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L0_yatak_odasi_4 | bedroom | L0 | 0 | 0 | 0 | - |
| r_L1_banyo | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_banyo_2 | bathroom | L1 | 0 | 0 | 0 | - |
| r_L1_koridor | hall | L1 | 0 | 0 | 0 | - |
| r_L1_koridor_2 | hall | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | other | L1 | 0 | 0 | 0 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | other | L1 | 0 | 0 | 0 | - |
| r_L1_teras | balcony | L1 | 0 | 0 | 0 | - |
| r_L1_teras_2 | balcony | L1 | 0 | 0 | 0 | - |

Rooms not rendered on purpose: r_L-1b_banyo (same as r_L-1_banyo), r_L-1b_banyo_2 (same as r_L-1_banyo_2), r_L-1b_koridor_2 (twin of r_L-1b_koridor), r_L-1b_oda_2 (twin of r_L-1b_oda), r_L0_banyo (unchanged in variant), r_L0_banyo_2 (unchanged in variant), r_L0_e_banyo (unchanged in variant), r_L0_e_banyo_2 (unchanged in variant), r_L0_e_yatak_odasi (unchanged in variant), r_L0_e_yatak_odasi_2 (unchanged in variant), r_L0_koridor (unchanged in variant), r_L0_koridor_2 (unchanged in variant), r_L0_oda (unchanged in variant), r_L0_oda_2 (unchanged in variant), r_L0_yatak_odasi (unchanged in variant), r_L0_yatak_odasi_2 (unchanged in variant), r_L0_yatak_odasi_3 (unchanged in variant), r_L0_yatak_odasi_4 (unchanged in variant), r_L1_banyo (unchanged in variant), r_L1_banyo_2 (unchanged in variant), r_L1_koridor (unchanged in variant), r_L1_koridor_2 (unchanged in variant), r_L1_oyun_aktivite_ve_dinlenme_odasi (unchanged in variant), r_L1_oyun_aktivite_ve_dinlenme_odasi_2 (unchanged in variant), r_L1_teras (unchanged in variant), r_L1_teras_2 (unchanged in variant).

### Why Cycles

- cam_r_L-1b_acik_mutfak_2_1: room: polish: room
- cam_r_L-1b_acik_mutfak_2_2: room: polish: room
- cam_r_L-1b_acik_mutfak_2_3: room: polish: room
- cam_r_L-1b_koridor_1: vision_check: added_by_polish furniture at [860.2, 394.2, 929.3, 753.8]; added_by_polish furniture at [861.3, 388.6, 1281.1, 770.6]
- ext_1: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_2: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_3: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_4: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)
- ext_5: gate_validation: exterior gate validation polish_disabled: the exterior views stay the Cycles render (negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through)

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_2_1 | cycles | disputed | f_L-1b_005 | unknown | optional | from_documents | one_building.dwg INSERT:2C4A2/1,INSERT:2C4A2/10,INSERT:2C4A2/11,INSERT:2C4A2/12,INSERT:2C4A2/13,INSERT:2C4A2/2,INSERT:2C4A2/3,INSERT:2C4A2/4,INSERT:2C4A2/5,INSERT:2C4A2/6,INSERT:2C4A2/7,INSERT:2C4A2/8,INSERT:2C4A2/9,INSERT:2C4A3/0,INSERT:2C4A3/1,INSERT:2C4A3/10,INSERT:2C4A3/11,INSERT:2C4A3/12,INSERT:2C4A3/13,INSERT:2C4A3/14,INSERT:2C4A3/15,INSERT:2C4A3/16,INSERT:2C4A3/17,INSERT:2C4A3/18,INSERT:2C4A3/19,INSERT:2C4A3/2,INSERT:2C4A3/20,INSERT:2C4A3/21,INSERT:2C4A3/22,INSERT:2C4A3/23,INSERT:2C4A3/24,INSERT:2C4A3/25,INSERT:2C4A3/26,INSERT:2C4A3/27,INSERT:2C4A3/28,INSERT:2C4A3/29,INSERT:2C4A3/3,INSERT:2C4A3/30,INSERT:2C4A3/31,INSERT:2C4A3/32,INSERT:2C4A3/33,INSERT:2C4A3/34,INSERT:2C4A3/35,INSERT:2C4A3/4,INSERT:2C4A3/5,INSERT:2C4A3/6,INSERT:2C4A3/7,INSERT:2C4A3/8,INSERT:2C4A3/9,LWPOLYLINE:2C814 vector 0.90 | info | - |
| cam_r_L-1b_acik_mutfak_2_1 | cycles | disputed | f_L-1b_031 | fridge | optional | from_documents | one_building.dwg INSERT:2C84A/4,INSERT:2C84A/9 vector 0.90; one_building.dwg recognition:sym_L-1b_019 ai 0.95; +1 more | info | - |
| cam_r_L-1b_acik_mutfak_2_1 | cycles | missing | f_L-1b_037 | wall_cabinet | optional | from_documents | one_building.dwg INSERT:2C84A/11 vector 0.90; one_building.dwg recognition:sym_L-1b_025 ai 0.95; +2 more | info | - |
| cam_r_L-1b_acik_mutfak_3 | cycles | missing | f_L-1b_006 | unknown | optional | from_documents | one_building.dwg INSERT:2ECCF/1,INSERT:2ECCF/10,INSERT:2ECCF/11,INSERT:2ECCF/12,INSERT:2ECCF/13,INSERT:2ECCF/2,INSERT:2ECCF/3,INSERT:2ECCF/4,INSERT:2ECCF/5,INSERT:2ECCF/6,INSERT:2ECCF/7,INSERT:2ECCF/8,INSERT:2ECCF/9,INSERT:2ECD0/0,INSERT:2ECD0/1,INSERT:2ECD0/10,INSERT:2ECD0/11,INSERT:2ECD0/12,INSERT:2ECD0/13,INSERT:2ECD0/14,INSERT:2ECD0/15,INSERT:2ECD0/16,INSERT:2ECD0/17,INSERT:2ECD0/18,INSERT:2ECD0/19,INSERT:2ECD0/2,INSERT:2ECD0/20,INSERT:2ECD0/21,INSERT:2ECD0/22,INSERT:2ECD0/23,INSERT:2ECD0/24,INSERT:2ECD0/25,INSERT:2ECD0/26,INSERT:2ECD0/27,INSERT:2ECD0/28,INSERT:2ECD0/29,INSERT:2ECD0/3,INSERT:2ECD0/30,INSERT:2ECD0/31,INSERT:2ECD0/32,INSERT:2ECD0/33,INSERT:2ECD0/34,INSERT:2ECD0/35,INSERT:2ECD0/4,INSERT:2ECD0/5,INSERT:2ECD0/6,INSERT:2ECD0/7,INSERT:2ECD0/8,INSERT:2ECD0/9,LWPOLYLINE:2F042 vector 0.90 | info | - |
| cam_r_L-1b_acik_mutfak_3 | polished | missing | f_L-1b_006 | unknown | optional | from_documents | one_building.dwg INSERT:2ECCF/1,INSERT:2ECCF/10,INSERT:2ECCF/11,INSERT:2ECCF/12,INSERT:2ECCF/13,INSERT:2ECCF/2,INSERT:2ECCF/3,INSERT:2ECCF/4,INSERT:2ECCF/5,INSERT:2ECCF/6,INSERT:2ECCF/7,INSERT:2ECCF/8,INSERT:2ECCF/9,INSERT:2ECD0/0,INSERT:2ECD0/1,INSERT:2ECD0/10,INSERT:2ECD0/11,INSERT:2ECD0/12,INSERT:2ECD0/13,INSERT:2ECD0/14,INSERT:2ECD0/15,INSERT:2ECD0/16,INSERT:2ECD0/17,INSERT:2ECD0/18,INSERT:2ECD0/19,INSERT:2ECD0/2,INSERT:2ECD0/20,INSERT:2ECD0/21,INSERT:2ECD0/22,INSERT:2ECD0/23,INSERT:2ECD0/24,INSERT:2ECD0/25,INSERT:2ECD0/26,INSERT:2ECD0/27,INSERT:2ECD0/28,INSERT:2ECD0/29,INSERT:2ECD0/3,INSERT:2ECD0/30,INSERT:2ECD0/31,INSERT:2ECD0/32,INSERT:2ECD0/33,INSERT:2ECD0/34,INSERT:2ECD0/35,INSERT:2ECD0/4,INSERT:2ECD0/5,INSERT:2ECD0/6,INSERT:2ECD0/7,INSERT:2ECD0/8,INSERT:2ECD0/9,LWPOLYLINE:2F042 vector 0.90 | info | - |
| cam_r_L-1b_koridor_1 | polished | extra | furniture | other_furniture | - | - | - | yes | box [860, 394, 929, 754] |
| cam_r_L-1b_oda_2 | polished | disputed | f_L-1b_006 | unknown | optional | from_documents | one_building.dwg INSERT:2ECCF/1,INSERT:2ECCF/10,INSERT:2ECCF/11,INSERT:2ECCF/12,INSERT:2ECCF/13,INSERT:2ECCF/2,INSERT:2ECCF/3,INSERT:2ECCF/4,INSERT:2ECCF/5,INSERT:2ECCF/6,INSERT:2ECCF/7,INSERT:2ECCF/8,INSERT:2ECCF/9,INSERT:2ECD0/0,INSERT:2ECD0/1,INSERT:2ECD0/10,INSERT:2ECD0/11,INSERT:2ECD0/12,INSERT:2ECD0/13,INSERT:2ECD0/14,INSERT:2ECD0/15,INSERT:2ECD0/16,INSERT:2ECD0/17,INSERT:2ECD0/18,INSERT:2ECD0/19,INSERT:2ECD0/2,INSERT:2ECD0/20,INSERT:2ECD0/21,INSERT:2ECD0/22,INSERT:2ECD0/23,INSERT:2ECD0/24,INSERT:2ECD0/25,INSERT:2ECD0/26,INSERT:2ECD0/27,INSERT:2ECD0/28,INSERT:2ECD0/29,INSERT:2ECD0/3,INSERT:2ECD0/30,INSERT:2ECD0/31,INSERT:2ECD0/32,INSERT:2ECD0/33,INSERT:2ECD0/34,INSERT:2ECD0/35,INSERT:2ECD0/4,INSERT:2ECD0/5,INSERT:2ECD0/6,INSERT:2ECD0/7,INSERT:2ECD0/8,INSERT:2ECD0/9,LWPOLYLINE:2F042 vector 0.90 | info | - |
| ext_3 | cycles | window count more | window | window | - | - | - | yes | expected [0, 1], passes {'qwen': 2, 'glm': 4} |
| ext_5 | cycles | missing | win_L-1b_001 | window | required | from_documents | one_building.dwg LWPOLYLINE:2F03F,LWPOLYLINE:2F040 vector 0.90 | yes | - |
| ext_5 | cycles | missing | win_L-1b_002 | window | optional | from_documents | one_building.dwg LWPOLYLINE:2C810,LWPOLYLINE:2C811 vector 0.90 | info | - |

## Needs review

- ext_3: window count more than expected [0, 1]: {'qwen': 2, 'glm': 4}
- ext_5: win_L-1b_001 (window, from_documents): missing

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- o_L0_001
- o_L0_002
- r_L-1_salon
- r_L-1_salon_2
- r_L-1_mutfak
- r_L-1_mutfak_2
- r_L-1_koridor
- r_L-1_koridor_2
- r_L-1b_acik_mutfak
- r_L-1b_acik_mutfak_2
- r_L-1b_koridor
- r_L-1b_koridor_2
- r_L0_koridor
- r_L0_koridor_2
- r_L0_yatak_odasi_3
- r_L0_yatak_odasi_4
- r_L0_oda
- r_L0_oda_2
- r_L1_teras
- r_L1_koridor
- r_L1_koridor_2
- r_L1_teras_2
- f_L-1_001
- f_L-1_002
- f_L-1_005
- f_L-1_006
- f_L-1_011
- f_L-1_012
- f_L-1_022
- f_L-1_024
- f_L-1_033
- f_L-1_034
- f_L-1_035
- f_L-1_036
- f_L-1_045
- f_L-1_046
- f_L-1_047
- f_L-1_048
- f_L-1_049
- f_L-1_050
- f_L-1_051
- f_L-1_052
- f_L-1b_001
- f_L-1b_002
- f_L-1b_005
- f_L-1b_006
- f_L-1b_007
- f_L-1b_008
- f_L-1b_014
- f_L-1b_016
- f_L-1b_018
- f_L-1b_021
- f_L-1b_022
- f_L-1b_023
- f_L-1b_024
- f_L-1b_025
- f_L-1b_026
- f_L-1b_027
- f_L-1b_028
- f_L-1b_029
- f_L-1b_030
- f_L-1b_033
- f_L-1b_034
- f_L-1b_035
- f_L-1b_036
- f_L0_003
- f_L0_004
- f_L0_015
- f_L0_016
- f_L0_029
- f_L0_030
- f_L0_031
- f_L0_032
- f_L1_003
- f_L1_004
- f_L1_005
- f_L1_006
- f_L1_015
- f_L1_016
- f_L1_017
- f_L1_018
- f_L1_021
- f_L1_023
- f_L1_024
- f_L1_025
- f_L1_026
- f_L1_027
- f_L1_028

Unverified pieces in view:

- cam_r_L-1b_acik_mutfak_1: f_L-1b_006, f_L-1b_008
- cam_r_L-1b_acik_mutfak_2: f_L-1b_002, f_L-1b_008, f_L-1b_018, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_034
- cam_r_L-1b_acik_mutfak_2_1: f_L-1b_005, f_L-1b_007, f_L-1b_033
- cam_r_L-1b_acik_mutfak_2_2: f_L-1b_001, f_L-1b_023, f_L-1b_024, f_L-1b_029, f_L-1b_030, f_L-1b_033
- cam_r_L-1b_acik_mutfak_2_3: f_L-1b_001, f_L-1b_023, f_L-1b_024, f_L-1b_029, f_L-1b_030, f_L-1b_033
- cam_r_L-1b_acik_mutfak_3: f_L-1b_006, f_L-1b_008
- cam_r_L-1b_koridor_1: f_L-1b_002, f_L-1b_006, f_L-1b_008, f_L-1b_018
- cam_r_L-1b_oda_1: f_L-1b_006
- cam_r_L-1b_oda_2: f_L-1b_006

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L-1_salon | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_002 | area_label_vs_computed | r_L-1_salon_2 | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_003 | area_label_vs_computed | r_L-1_mutfak | Label says 14,50 m², polygon gives 13,63 m² (6.0%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_004 | area_label_vs_computed | r_L-1_mutfak_2 | Label says 14,50 m², polygon gives 13,62 m² (6.1%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_005 | area_label_vs_computed | r_L-1_koridor | Label says 7,00 m², polygon gives 11,92 m² (70.3%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_006 | area_label_vs_computed | r_L-1_koridor_2 | Label says 7,00 m², polygon gives 11,93 m² (70.4%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_007 | area_label_vs_computed | r_L-1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_008 | area_label_vs_computed | r_L-1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_009 | area_label_vs_computed | r_L-1b_acik_mutfak | Label says 8,50 m², polygon gives 51,83 m² (509.7%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_010 | area_label_vs_computed | r_L-1b_acik_mutfak_2 | Label says 8,50 m², polygon gives 51,83 m² (509.7%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_011 | area_label_vs_computed | r_L-1b_oda | Label says 13,00 m², polygon gives 13,14 m² (1.1%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_012 | area_label_vs_computed | r_L-1b_oda_2 | Label says 13,00 m², polygon gives 13,15 m² (1.2%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_013 | area_label_vs_computed | r_L-1b_koridor | Label says 7,00 m², polygon gives 11,50 m² (64.3%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_014 | area_label_vs_computed | r_L-1b_koridor_2 | Label says 7,00 m², polygon gives 11,50 m² (64.2%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_015 | area_label_vs_computed | r_L-1b_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.7%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_016 | area_label_vs_computed | r_L-1b_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_017 | area_label_vs_computed | r_L0_yatak_odasi | Label says 16,00 m², polygon gives 16,13 m² (0.8%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_018 | area_label_vs_computed | r_L0_e_yatak_odasi | Label says 17,00 m², polygon gives 16,86 m² (0.8%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_019 | area_label_vs_computed | r_L0_e_yatak_odasi_2 | Label says 17,00 m², polygon gives 16,87 m² (0.8%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_020 | area_label_vs_computed | r_L0_yatak_odasi_2 | Label says 16,00 m², polygon gives 16,12 m² (0.7%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_021 | area_label_vs_computed | r_L0_koridor | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_022 | area_label_vs_computed | r_L0_koridor_2 | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_023 | area_label_vs_computed | r_L0_yatak_odasi_3 | Label says 17,00 m², polygon gives 14,05 m² (17.3%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_024 | area_label_vs_computed | r_L0_yatak_odasi_4 | Label says 17,00 m², polygon gives 14,04 m² (17.4%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_025 | area_label_vs_computed | r_L0_banyo | Label says 4,90 m², polygon gives 4,97 m² (1.5%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_026 | area_label_vs_computed | r_L0_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_027 | area_label_vs_computed | r_L1_teras | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_028 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_029 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_030 | area_label_vs_computed | r_L1_koridor | Label says 10,00 m², polygon gives 15,34 m² (53.4%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_031 | area_label_vs_computed | r_L1_koridor_2 | Label says 10,00 m², polygon gives 15,34 m² (53.4%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_032 | area_label_vs_computed | r_L1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_033 | area_label_vs_computed | r_L1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (3%), kept polygon from one_building.dwg |
| c_034 | area_label_vs_computed | r_L1_teras_2 | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 3%: room marked unverified, polygon from one_building.dwg kept |
| c_035 | outline_mismatch | L0, L-1 | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_036 | outline_mismatch | L0, L-1b | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_037 | outline_mismatch | L0, L1 | Outer wall outline of Çatı Katı differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_038 | symbol_type_disagreement | f_L-1_022 | f_L-1_022: sym_L-1_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_039 | symbol_type_disagreement | f_L-1_024 | f_L-1_024: sym_L-1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_040 | symbol_type_disagreement | f_L-1_033 | f_L-1_033: sym_L-1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_041 | symbol_type_disagreement | f_L-1_034 | f_L-1_034: sym_L-1_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_042 | symbol_type_disagreement | f_L-1_035 | f_L-1_035: sym_L-1_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_043 | symbol_type_disagreement | f_L-1_036 | f_L-1_036: sym_L-1_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_044 | symbol_type_disagreement | f_L-1_045 | f_L-1_045: sym_L-1_029: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_045 | symbol_type_disagreement | f_L-1_046 | f_L-1_046: sym_L-1_030: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_046 | symbol_type_disagreement | f_L-1_047 | f_L-1_047: sym_L-1_031: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) wall_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_047 | symbol_type_disagreement | f_L-1_048 | f_L-1_048: sym_L-1_032: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_048 | symbol_type_disagreement | f_L-1_050 | f_L-1_050: sym_L-1_034: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) not_furniture, pass 2 (zai-org/GLM-4.6V-Flash) unknown | unresolved: the drawn footprint is kept as unknown, unverified |
| c_049 | symbol_type_disagreement | f_L-1_051 | f_L-1_051: sym_L-1_035: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L-1_052 | f_L-1_052: sym_L-1_036: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L-1b_016 | f_L-1b_016: sym_L-1b_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) not_furniture, pass 2 (zai-org/GLM-4.6V-Flash) unknown | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L-1b_018 | f_L-1b_018: sym_L-1b_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_053 | symbol_type_disagreement | f_L-1b_021 | f_L-1b_021: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_054 | symbol_type_disagreement | f_L-1b_022 | f_L-1b_022: sym_L-1b_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_055 | symbol_type_disagreement | f_L-1b_023 | f_L-1b_023: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_056 | symbol_type_disagreement | f_L-1b_024 | f_L-1b_024: sym_L-1b_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_057 | symbol_type_disagreement | f_L-1b_025 | f_L-1b_025: sym_L-1b_013: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_058 | symbol_type_disagreement | f_L-1b_026 | f_L-1b_026: sym_L-1b_014: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L-1b_027 | f_L-1b_027: sym_L-1b_015: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L-1b_028 | f_L-1b_028: sym_L-1b_016: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L-1b_029 | f_L-1b_029: sym_L-1b_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L-1b_030 | f_L-1b_030: sym_L-1b_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_063 | symbol_type_disagreement | f_L-1b_033 | f_L-1b_033: sym_L-1b_021: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_064 | symbol_type_disagreement | f_L-1b_034 | f_L-1b_034: sym_L-1b_022: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_065 | symbol_type_disagreement | f_L-1b_035 | f_L-1b_035: sym_L-1b_023: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_066 | symbol_type_disagreement | f_L-1b_036 | f_L-1b_036: sym_L-1b_024: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_067 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_069 | symbol_type_disagreement | f_L0_031 | f_L0_031: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_070 | symbol_type_disagreement | f_L0_032 | f_L0_032: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_071 | symbol_type_disagreement | f_L1_015 | f_L1_015: sym_L1_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_072 | symbol_type_disagreement | f_L1_016 | f_L1_016: sym_L1_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_073 | symbol_type_disagreement | f_L1_017 | f_L1_017: sym_L1_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_074 | symbol_type_disagreement | f_L1_018 | f_L1_018: sym_L1_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_075 | symbol_type_disagreement | f_L1_021 | f_L1_021: sym_L1_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bench | unresolved: the drawn footprint is kept as unknown, unverified |
| c_076 | symbol_type_disagreement | f_L1_023 | f_L1_023: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_077 | symbol_type_disagreement | f_L1_024 | f_L1_024: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_078 | symbol_type_disagreement | f_L1_025 | f_L1_025: sym_L1_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_079 | symbol_type_disagreement | f_L1_026 | f_L1_026: sym_L1_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_080 | other | r_L-1b_acik_mutfak | r_L-1b_acik_mutfak: one face holds the room names 'Açık Mutfak' and 'SALON' | unresolved: first label kept, room unverified |
| c_081 | other | r_L-1b_acik_mutfak_2 | r_L-1b_acik_mutfak_2: one face holds the room names 'Açık Mutfak' and 'SALON' | unresolved: first label kept, room unverified |
| c_082 | symbol_front_disagreement | f_L-1_017 | f_L-1_017: sym_L-1_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (L outline: the open inner corner is the front) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L-1_018 | f_L-1_018: sym_L-1_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (L outline: the open inner corner is the front) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L-1_033 | f_L-1_033: sym_L-1_017: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L-1_034 | f_L-1_034: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L-1_035 | f_L-1_035: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L-1_036 | f_L-1_036: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L-1_039 | f_L-1_039: sym_L-1_023: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L-1_040 | f_L-1_040: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L-1_041 | f_L-1_041: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | symbol_front_disagreement | f_L-1_042 | f_L-1_042: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_092 | symbol_front_disagreement | f_L-1b_031 | f_L-1b_031: sym_L-1b_019: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_093 | symbol_front_disagreement | f_L-1b_032 | f_L-1b_032: sym_L-1b_020: AI front [90.0] (pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_094 | symbol_front_disagreement | f_L0_024 | f_L0_024: sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_095 | symbol_front_disagreement | f_L0_029 | f_L0_029: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_096 | symbol_front_disagreement | f_L0_030 | f_L0_030: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_097 | symbol_front_disagreement | f_L0_031 | f_L0_031: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_098 | symbol_front_disagreement | f_L0_032 | f_L0_032: sym_L0_012: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_099 | symbol_front_disagreement | f_L1_023 | f_L1_023: sym_L1_009: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_100 | symbol_front_disagreement | f_L1_024 | f_L1_024: sym_L1_010: AI front [270.0] (pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_101 | symbol_front_disagreement | f_L1_025 | f_L1_025: sym_L1_011: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_102 | symbol_front_disagreement | f_L1_026 | f_L1_026: sym_L1_012: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_103 | unit_mismatch | r1, r2, r3, r4, r5, r6 | sheets.json sc_001: one_building.dwg: $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_104 | level_mark_mismatch | r6 | sheets.json sc_002: section r6: the level mark 40.00 (MTEXT:304DD) gives -3.00 m but points at -3.15 m (the bottom of a slab) (0.15 m apart) | geometry wins: slab tops from the slab lines |

## This report: variant `l-1b-acik-mutfak`

An alternative's sub-output: it renders the rooms its plan changes, and its exterior views only when its outside differs from the base. The sheets and the other variants are in the base project's report (`../../final/final_report.md`). The base exterior views of this run: ext_1, ext_2, ext_3, ext_4, ext_5.

## Building

The whole building as it was read and built: every level stacked on one frame with its slabs, the roof over the top level, the facade and the site. Each height says whether a document gave it or it was assumed (never silently).

Levels:

| level | label | kind | floor level | ceiling height | variant | region |
|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | basement | -3,00 m (section) | 2,85 m (section) | base | r2 |
| L-1b | Bodrum Kat | basement | -3,00 m (section) | 2,85 m (section) | Açık mutfak | r3 |
| L0 | Zemin Kat | floor | 0,00 m (section) | 3,00 m (section) | base | r4 |
| L1 | Çatı Katı | attic | 3,15 m (section) | 3,43 m (section) | base | r5 |

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
| L-1b ceiling height | 2,85 m | drawn | section | - |
| L-1b floor level | -3,00 m | drawn | section | - |
| L-1b floor to floor | 3,00 m | drawn | vector | - |
| L0 ceiling height | 3,00 m | drawn | section | - |
| L0 floor level | 0,00 m | drawn | section | - |
| L0 floor to floor | 3,15 m | drawn | vector | - |
| L1 ceiling height | 3,43 m | drawn | section | - |
| L1 floor level | 3,15 m | drawn | section | - |
| sl_L-1 thickness | 0,15 m | drawn | section | - |
| sl_L0 thickness | 0,15 m | drawn | section | - |
| sl_L1 thickness | 0,15 m | drawn | section | - |
| roof eaves height | 3,65 m | drawn | vector | 0.50 m above the top floor |
| roof ridge height | 6,79 m | drawn | vector | 3.64 m above the top floor |
| roof overhang | 0,50 m | drawn | vector | left 0.50 m, right 0.50 m |
| roof thickness | 0,20 m | drawn | vector | perpendicular to the first slope |
| roof knee wall | 0,93 m | drawn | vector | the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 0.66 m above the floor |

Slabs:

| slab | carries level | top | thickness | from | stair voids | variants | status |
|---|---|---|---|---|---|---|---|
| sl_L-1 | L-1 | -3,00 m | 0,15 m | section | 0 | all | verified |
| sl_L0 | L0 | 0,00 m | 0,15 m | section | 2 | all | verified |
| sl_L1 | L1 | 3,15 m | 0,15 m | section | 2 | all | verified |

Roof:

- type mansard (plan_roof_lines)
- over level L1
- eaves 3,65 m (drawn)
- ridge 6,79 m (drawn)
- overhang 0,50 m (drawn)
- thickness 0,20 m (drawn)
- knee wall 0,93 m (drawn)
- pitch 40.4 deg (drawn), 13.3 deg (drawn)
- 0 planes, 2 opening(s)
- covering not drawn (outside look: see Exterior views)

Facade:

No facade face or elevation drawn: the outside look is resolved from the brief, the style or the defaults (see Exterior views).

Site:

- plot not drawn
- 0 paving area(s), 0 grass, 0 parking built
- 0 boundary wall(s), 6 decor item(s) built
- 0 labelled area(s), 0 recorded only (label, not built)
- drawn ground levels: left -, right -
- terrain flat, 0 light well(s)

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 58 piece(s) added, 0 wall cabinet run(s).

### Salon (r_L-1_salon, living): completed

- added f_L-1_053: tv_unit 1.20 x 0.40 (confidence 0.60, ai)
- added f_L-1_054: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L-1_055: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L-1_056: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L-1_057: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L-1_058: chair 0.45 x 0.45 (confidence 0.60, ai)
- added f_L-1_059: chair 0.40 x 0.40 (confidence 0.60, ai)
- added f_L-1_060: chair 0.40 x 0.40 (confidence 0.60, ai)
- added f_L-1_061: armchair 0.90 x 0.90 (confidence 0.90, ai)
- added f_L-1_062: chaise 0.75 x 1.70 (confidence 0.60, ai)
- added f_L-1_063: console_table 1.20 x 0.35 (confidence 0.60, ai)
- added f_L-1_064: sideboard 1.40 x 0.42 (confidence 0.60, ai)
- refused to add chair: covered: at most 8 chair
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (1.02 m from the nearest table_dining (> 0.6 m))
- not placed chair: no free place passed the placer checks (1.55 m from the nearest table_dining (> 0.6 m))
- not placed chair: no free place passed the placer checks (3.00 m from the nearest table_dining (> 0.6 m))
- not placed chair: no free place passed the placer checks (3.21 m from the nearest table_dining (> 0.6 m))
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_005, f_L-1_008, f_L-1_017, f_L-1_023, f_L-1_024, f_L-1_027, f_L-1_028, f_L-1_034, f_L-1_035, f_L-1_039, f_L-1_041

### Salon (r_L-1_salon_2, living): mirrored (decisions of r_L-1_salon (twin), not asked again)

- added f_L-1_066: tv_unit 1.20 x 0.40 (confidence 0.60, ai, mirrored from f_L-1_053)
- added f_L-1_067: chair 0.50 x 0.50 (confidence 0.60, ai, mirrored from f_L-1_054)
- added f_L-1_068: chair 0.50 x 0.50 (confidence 0.60, ai, mirrored from f_L-1_055)
- added f_L-1_069: chair 0.50 x 0.50 (confidence 0.60, ai, mirrored from f_L-1_056)
- added f_L-1_070: chair 0.50 x 0.50 (confidence 0.60, ai, mirrored from f_L-1_057)
- added f_L-1_071: chair 0.45 x 0.45 (confidence 0.60, ai, mirrored from f_L-1_058)
- added f_L-1_072: chair 0.40 x 0.40 (confidence 0.60, ai, mirrored from f_L-1_059)
- added f_L-1_073: chair 0.40 x 0.40 (confidence 0.60, ai, mirrored from f_L-1_060)
- added f_L-1_074: armchair 0.90 x 0.90 (confidence 0.90, ai, mirrored from f_L-1_061)
- added f_L-1_075: chaise 0.75 x 1.70 (confidence 0.60, ai, mirrored from f_L-1_062)
- added f_L-1_076: console_table 1.20 x 0.35 (confidence 0.60, ai, mirrored from f_L-1_063)
- added f_L-1_077: sideboard 1.40 x 0.42 (confidence 0.60, ai, mirrored from f_L-1_064)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_006, f_L-1_007, f_L-1_018, f_L-1_021, f_L-1_022, f_L-1_029, f_L-1_030, f_L-1_033, f_L-1_036, f_L-1_040, f_L-1_042

### Mutfak (r_L-1_mutfak, kitchen): completed

- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed tall_cabinet: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed tall_cabinet: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_001, f_L-1_031, f_L-1_045, f_L-1_047, f_L-1_049

### Mutfak (r_L-1_mutfak_2, kitchen): completed (partner r_L-1_mutfak (twin) not used: the twin's drawn furniture does not map onto this room: drawn fridge f_L-1_031 has no counterpart here; asked itself)

- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed tall_cabinet: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed tall_cabinet: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_002, f_L-1_032, f_L-1_046, f_L-1_048, f_L-1_050

### Koridor (r_L-1_koridor, hall): mirrored (decisions of r_L-1_koridor_2 (twin), not asked again)

- added f_L-1_078: console_table 1.20 x 0.35 (confidence 0.90, ai, mirrored from f_L-1_065)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_004

### Koridor (r_L-1_koridor_2, hall): completed

- added f_L-1_065: console_table 1.20 x 0.35 (confidence 0.90, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_003

### Banyo (r_L-1_banyo, bathroom): completed (nothing to ask: no changeable drawn piece and nothing the room may get)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_010, f_L-1_015, f_L-1_020

### Banyo (r_L-1_banyo_2, bathroom): mirrored (decisions of r_L-1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1_009, f_L-1_016, f_L-1_019

### Açık Mutfak (r_L-1b_acik_mutfak, kitchen): completed

- added f_L-1b_049: tall_cabinet 0.40 x 0.58 (confidence 0.90, ai)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_002, f_L-1b_006, f_L-1b_015, f_L-1b_016, f_L-1b_018, f_L-1b_022, f_L-1b_025, f_L-1b_026, f_L-1b_027, f_L-1b_028, f_L-1b_032, f_L-1b_036

### Açık Mutfak (r_L-1b_acik_mutfak_2, kitchen): completed

- added f_L-1b_050: bar_stool 0.42 x 0.42 (confidence 0.60, ai)
- added f_L-1b_051: bar_stool 0.42 x 0.42 (confidence 0.60, ai)
- added f_L-1b_052: bar_stool 0.42 x 0.42 (confidence 0.60, ai)
- added f_L-1b_053: bar_stool 0.42 x 0.42 (confidence 0.60, ai)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed tall_cabinet: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no repair left)
- not placed table_dining: no free place passed the placer checks (no repair left)
- not placed tall_cabinet: no free place passed the placer checks (no repair left)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- not placed chair: no free place passed the placer checks (no table_dining in the room)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_001, f_L-1b_005, f_L-1b_013, f_L-1b_014, f_L-1b_017, f_L-1b_021, f_L-1b_023, f_L-1b_024, f_L-1b_029, f_L-1b_030, f_L-1b_031, f_L-1b_035

### Koridor (r_L-1b_koridor, hall): completed

- added f_L-1b_054: console_table 1.20 x 0.35 (confidence 0.90, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_004

### Koridor (r_L-1b_koridor_2, hall): mirrored (decisions of r_L-1b_koridor (twin), not asked again)

- added f_L-1b_055: console_table 1.20 x 0.35 (confidence 0.90, ai, mirrored from f_L-1b_054)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_003

### Banyo (r_L-1b_banyo, bathroom): copied (decisions of r_L-1_banyo (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_010, f_L-1b_012, f_L-1b_020

### Banyo (r_L-1b_banyo_2, bathroom): copied (decisions of r_L-1_banyo_2 (same_as), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L-1b_009, f_L-1b_011, f_L-1b_019

### Yatak Odası (r_L0_yatak_odasi, bedroom): completed

- added f_L0_041: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_042: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_043: bench 1.20 x 0.40 (confidence 0.60, ai)
- refused f_L0_021 -> bed_double: only pass 1 changes it (a drawn piece needs both passes)
- refused f_L0_032 -> dresser: only pass 1 changes it (a drawn piece needs both passes)
- not placed armchair: no free place passed the placer checks (no repair left)
- not placed ottoman: no free place passed the placer checks (no repair left)
- not placed bench: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_012, f_L0_021, f_L0_032

### E.yatak Odası (r_L0_e_yatak_odasi, bedroom): completed

- added f_L0_044: nightstand 0.60 x 0.45 (confidence 0.90, ai)
- added f_L0_045: nightstand 0.60 x 0.45 (confidence 0.90, ai)
- added f_L0_046: bench 1.20 x 0.40 (confidence 0.60, ai)
- refused f_L0_009 -> bed_double: only pass 1 changes it (a drawn piece needs both passes)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_003, f_L0_009, f_L0_025, f_L0_033, f_L0_034

### E.yatak Odası (r_L0_e_yatak_odasi_2, bedroom): completed (partner r_L0_e_yatak_odasi (twin) not used: the twin's drawn furniture does not map onto this room: drawn wardrobe f_L0_025 has no counterpart here; asked itself)

- added f_L0_050: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_051: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_052: bench 1.20 x 0.40 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_004, f_L0_010, f_L0_026, f_L0_035, f_L0_036

### Yatak Odası (r_L0_yatak_odasi_2, bedroom): mirrored (decisions of r_L0_yatak_odasi (twin), not asked again)

- added f_L0_053: nightstand 0.50 x 0.40 (confidence 0.90, ai, mirrored from f_L0_041)
- added f_L0_054: nightstand 0.50 x 0.40 (confidence 0.90, ai, mirrored from f_L0_042)
- added f_L0_055: bench 1.20 x 0.40 (confidence 0.60, ai, mirrored from f_L0_043)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_014, f_L0_022, f_L0_029

### E.banyo (r_L0_e_banyo, bathroom): completed (nothing to ask: no changeable drawn piece and nothing the room may get)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_008, f_L0_015, f_L0_017

### E.banyo (r_L0_e_banyo_2, bathroom): mirrored (decisions of r_L0_e_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_006, f_L0_016, f_L0_018

### Yatak Odası (r_L0_yatak_odasi_3, bedroom): completed

- added f_L0_047: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_048: nightstand 0.50 x 0.40 (confidence 0.90, ai)
- added f_L0_049: bench 1.00 x 0.40 (confidence 0.90, ai)
- refused f_L0_011 -> wardrobe: only pass 1 changes it (a drawn piece needs both passes)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_011, f_L0_023, f_L0_031

### Yatak Odası (r_L0_yatak_odasi_4, bedroom): completed (partner r_L0_yatak_odasi_3 (twin) not used: the twin's drawn furniture does not map onto this room: drawn bed_double f_L0_023 has no counterpart here; asked itself)

- added f_L0_056: nightstand 0.50 x 0.40 (confidence 0.60, ai)
- added f_L0_057: nightstand 0.40 x 0.40 (confidence 0.60, ai)
- added f_L0_058: bench 1.20 x 0.40 (confidence 0.60, ai)
- refused f_L0_013 -> wardrobe: only pass 1 changes it (a drawn piece needs both passes)
- refused f_L0_024 -> bed_double: only pass 1 changes it (a drawn piece needs both passes)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_013, f_L0_024, f_L0_030

### Oda (r_L0_oda, hall): completed

- not placed console_table: no free place passed the placer checks (no repair left)
- not placed console_table: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Oda (r_L0_oda_2, hall): completed

- not placed console_table: no free place passed the placer checks (no repair left)
- not placed console_table: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Banyo (r_L0_banyo, bathroom): completed (nothing to ask: no changeable drawn piece and nothing the room may get)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_005, f_L0_020, f_L0_027

### Banyo (r_L0_banyo_2, bathroom): mirrored (decisions of r_L0_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_007, f_L0_019, f_L0_028

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi, other): completed

- added f_L1_029: armchair 0.90 x 0.90 (confidence 0.90, ai)
- added f_L1_030: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L1_031: bookshelf 0.80 x 0.30 (confidence 0.90, ai)
- not placed table_dining: no free place passed the placer checks (no repair left)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_003, f_L1_005, f_L1_009, f_L1_012, f_L1_015

### Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2, other): mirrored (decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again)

- added f_L1_034: chair 0.50 x 0.50 (confidence 0.60, ai, mirrored from f_L1_030)
- added f_L1_035: bookshelf 0.80 x 0.30 (confidence 0.90, ai, mirrored from f_L1_031)
- not placed armchair: no free place passed the placer checks (the copy fails clearance_ok here)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_004, f_L1_006, f_L1_010, f_L1_011, f_L1_016

### Koridor (r_L1_koridor, hall): completed

- added f_L1_032: console_table 1.20 x 0.35 (confidence 0.90, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_002, f_L1_021

### Koridor (r_L1_koridor_2, hall): completed

- added f_L1_033: console_table 1.20 x 0.35 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_001, f_L1_022

### Banyo (r_L1_banyo, bathroom): completed (nothing to ask: no changeable drawn piece and nothing the room may get)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_007, f_L1_013, f_L1_019

### Banyo (r_L1_banyo_2, bathroom): mirrored (decisions of r_L1_banyo (twin), not asked again)

- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L1_008, f_L1_014, f_L1_020

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 154 of 154 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 154 ok, 0 failed; 0 changed by the AI.

## Exterior views

5 of 5 exterior view(s) of variant `l-1b-acik-mutfak` rendered.

- contact sheet of `l-1b-acik-mutfak`: [contact_exterior_l-1b-acik-mutfak.jpg](contact_exterior_l-1b-acik-mutfak.jpg)

Gate for the exterior polish: **polish_disabled** (exterior views stay the Cycles render): negative controls rejected 0.846 < 0.90 (52 comparisons): the gate lets geometry changes through.

Views:

| view | kind | sides | region | final | roof | facade counts (advisory) | review |
|---|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | - | cycles (gate_validation) | ok | front: ok | no |
| ext_2 | corner | right, front | - | cycles (gate_validation) | ok | front: ok | no |
| ext_3 | corner | right, back | - | cycles (gate_validation) | ok | back: ok | yes |
| ext_4 | corner | left, back | - | cycles (gate_validation) | ok | back: ok | no |
| ext_5 | aerial | left, front | - | cycles (gate_validation) | ok | front: mismatch | yes |

Outside looks (documents > brief > style > fallback; assumed ones are also listed under Assumed values):

| slot | material | colour | source | assumed | reason |
|---|---|---|---|---|---|
| facade | render | warm greige | fallback | yes | style profile exterior.facade (assumed) |
| roof | concrete_tiles | anthracite | fallback | yes | style profile exterior.roof (assumed) |
| window_frame | dark_bronze | - | style | no | style profile exterior.window_frame |
| door | wood_oak_light | - | fallback | yes | style profile exterior.door (assumed) |
| paving | paving | grey | fallback | yes | style profile exterior.paving (assumed) |
| garden | grass | - | fallback | yes | style profile exterior.garden (assumed) |
| sill | stone | - | build | yes | exterior sill not drawn |
| light_well | concrete | - | build | yes | light well: concrete (not drawn) |
| railing | steel_brushed | - | build | yes | railing not drawn: steel rail and glass panel |
| soffit | soffit | - | build | yes | roof soffit: painted (not drawn) |
| bark | bark | - | build | yes | parametric tree |
| foliage | foliage | - | build | yes | parametric tree |
| ground | soil | - | build | yes | neutral ground (brief site: ground) |
| plot_wall | render | warm greige | build | yes | plot wall finish not drawn: the facade's look |

Elevation check (window and door counts and positions per facade, building JSON against the drawn elevation; built eaves and ridge against the section; deterministic):

Source: sheets.json exterior.openings_seen. 0 facade(s): 0 ok, 0 mismatch, 0 not checked; roof ok.

Roof heights: built eaves 3,65 m, ridge 6,79 m; drawn eaves 3,65 m (vector), ridge 6,79 m (vector); result ok.

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| one_building.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 48, block_name 38, none 58, rule 10. Recognition questions: -; answer files: none. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L-1_017 | r_L-1_salon | sofa_corner | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa_corner, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa_corner, front left 1.00 |
| f_L-1_018 | r_L-1_salon_2 | sofa_corner | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa_corner, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa_corner, front left 1.00 |
| f_L-1_019 | r_L-1_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1_020 | r_L-1_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1_021 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_022 | r_L-1_salon_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1_023 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_024 | r_L-1_salon | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1_025 | r_L-1_salon | sofa | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1_026 | r_L-1_salon_2 | sofa | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1_027 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_028 | r_L-1_salon | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_029 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_030 | r_L-1_salon_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L-1_031 | r_L-1_mutfak | fridge | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: fridge 0.95; pass 2 zai-org/GLM-4.6V-Flash: fridge, front right 0.90 |
| f_L-1_032 | r_L-1_mutfak_2 | fridge | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: fridge 0.95; pass 2 zai-org/GLM-4.6V-Flash: fridge, front right 0.90 |
| f_L-1_033 | r_L-1_salon_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_034 | r_L-1_salon | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L-1_035 | r_L-1_salon | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_036 | r_L-1_salon_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L-1_037 | r_L-1_salon | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.90 |
| f_L-1_038 | r_L-1_salon_2 | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.80 |
| f_L-1_039 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_040 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front left 0.80 |
| f_L-1_041 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_042 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman, front right 0.80 |
| f_L-1_043 | r_L-1_salon_2 | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_044 | r_L-1_salon | ottoman | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L-1_045 | r_L-1_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: sink_kitchen 0.90 |
| f_L-1_046 | r_L-1_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: sink_kitchen 0.90 |
| f_L-1_047 | r_L-1_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: wall_cabinet, front right 0.90 |
| f_L-1_048 | r_L-1_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: sink_kitchen 0.90 |
| f_L-1_049 | r_L-1_mutfak | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1_050 | r_L-1_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: unknown 0.80 |
| f_L-1_051 | r_L-1_salon | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1_052 | r_L-1_salon_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front right 0.90 |
| f_L-1b_013 | r_L-1b_acik_mutfak_2 | stove | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: stove 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove 0.90 |
| f_L-1b_014 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L-1b_015 | r_L-1b_acik_mutfak | stove | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: stove 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove 0.90 |
| f_L-1b_016 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture 0.95; pass 2 zai-org/GLM-4.6V-Flash: unknown 0.80 |
| f_L-1b_017 | r_L-1b_acik_mutfak_2 | kitchen_island | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: kitchen_island, front bottom 0.90 |
| f_L-1b_018 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front top 0.90 |
| f_L-1b_019 | r_L-1b_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1b_020 | r_L-1b_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L-1b_021 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_022 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_island, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L-1b_023 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_024 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_025 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_026 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter 0.95; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L-1b_027 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front top 0.90 |
| f_L-1b_028 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front top 0.90 |
| f_L-1b_029 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front top 0.90 |
| f_L-1b_030 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front top 0.90 |
| f_L-1b_031 | r_L-1b_acik_mutfak_2 | fridge | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: fridge 0.95; pass 2 zai-org/GLM-4.6V-Flash: fridge, front right 0.90 |
| f_L-1b_032 | r_L-1b_acik_mutfak | fridge | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: fridge 0.95; pass 2 zai-org/GLM-4.6V-Flash: fridge, front top 0.90 |
| f_L-1b_033 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L-1b_034 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.80 |
| f_L-1b_035 | r_L-1b_acik_mutfak_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: sink_kitchen, front bottom 0.90 |
| f_L-1b_036 | r_L-1b_acik_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bar_stool 0.95; pass 2 zai-org/GLM-4.6V-Flash: sink_kitchen, front right 0.90 |
| f_L-1b_037 | r_L-1b_acik_mutfak_2 | wall_cabinet | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wall_cabinet 0.95; pass 2 zai-org/GLM-4.6V-Flash: wall_cabinet, front right 0.90 |
| f_L-1b_038 | r_L-1b_acik_mutfak | wall_cabinet | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wall_cabinet 0.95; pass 2 zai-org/GLM-4.6V-Flash: wall_cabinet, front top 0.90 |
| f_L0_021 | r_L0_yatak_odasi | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 1.00 |
| f_L0_022 | r_L0_yatak_odasi_2 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 0.90 |
| f_L0_023 | r_L0_yatak_odasi_3 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front right 0.90 |
| f_L0_024 | r_L0_yatak_odasi_4 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front left 0.90 |
| f_L0_025 | r_L0_e_yatak_odasi | wardrobe | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wardrobe, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front left 0.90 |
| f_L0_026 | r_L0_e_yatak_odasi_2 | wardrobe | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wardrobe, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front right 0.90 |
| f_L0_027 | r_L0_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L0_028 | r_L0_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L0_029 | r_L0_yatak_odasi_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_030 | r_L0_yatak_odasi_4 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front right 0.90 |
| f_L0_031 | r_L0_yatak_odasi_3 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_032 | r_L0_yatak_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front right 0.85; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 0.90 |
| f_L0_033 | r_L0_e_yatak_odasi | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_034 | r_L0_e_yatak_odasi | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_035 | r_L0_e_yatak_odasi_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L0_036 | r_L0_e_yatak_odasi_2 | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |
| f_L1_015 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L1_016 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.90; pass 2 zai-org/GLM-4.6V-Flash: potted_plant 0.90 |
| f_L1_017 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_018 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L1_019 | r_L1_banyo | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L1_020 | r_L1_banyo_2 | bathtub | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bathtub, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bathtub, front bottom 0.90 |
| f_L1_021 | r_L1_koridor | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.90 |
| f_L1_022 | r_L1_koridor_2 | bench | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bench, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: bench, front left 0.90 |
| f_L1_023 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_024 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front bottom 0.90 |
| f_L1_025 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front right 0.90 |
| f_L1_026 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: armchair, front left 0.90 |
| f_L1_027 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |
| f_L1_028 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: ottoman 0.95; pass 2 zai-org/GLM-4.6V-Flash: ottoman 0.90 |

## Site

Recorded, not built.

| id | what | detail |
|---|---|---|
| - | decor | other x 6 |

## Separators

Virtual lines that split an open-plan face where two room names share it (no geometry is built; the pipeline's report.md lists the candidates it dropped):

| id | level | length | status | reason |
|---|---|---|---|---|
| o_L-1_001 | L-1 | 1,38 m | verified | virtual separator (end-to-face, 1.38 m): two room names shared one face |
| o_L-1_002 | L-1 | 1,38 m | verified | virtual separator (end-to-face, 1.38 m): two room names shared one face |
| o_L-1b_001 | L-1b | 1,30 m | verified | virtual separator (end-to-wall, 1.30 m): two room names shared one face |
| o_L-1b_002 | L-1b | 1,30 m | verified | virtual separator (end-to-wall, 1.30 m): two room names shared one face |

## Assumed values

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
- front kept from the drawing although both AI passes answered 'none': 10 piece(s) (f_L-1_021, f_L-1_023, f_L-1_028, f_L-1_030, f_L-1_037, f_L-1_038 ...)
- door height 2,10 m: 26 opening(s) (d_L-1_001, d_L-1_002, d_L-1_003, d_L-1_004, d_L-1b_001, d_L-1b_002 ...)
- opening height 2,10 m: 3 opening(s) (o_L0_001, o_L0_002, o_L1_001)
- window height 1,20 m: 12 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1b_001, win_L-1b_002 ...)
- window sill height 0,90 m: 12 opening(s) (win_L-1_001, win_L-1_002, win_L-1_003, win_L-1_004, win_L-1b_001, win_L-1b_002 ...)
- f_L-1_003 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1_004 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1b_003 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1b_004 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- roof covering: not drawn (the outside look decides, see below)
- outside look facade: render in warm greige (fallback: style profile exterior.facade (assumed))
- outside look roof: concrete_tiles in anthracite (fallback: style profile exterior.roof (assumed))
- outside look door: wood_oak_light (fallback: style profile exterior.door (assumed))
- outside look paving: paving in grey (fallback: style profile exterior.paving (assumed))
- outside look garden: grass (fallback: style profile exterior.garden (assumed))
- outside look sill: stone (build: exterior sill not drawn)
- outside look light_well: concrete (build: light well: concrete (not drawn))
- outside look railing: steel_brushed (build: railing not drawn: steel rail and glass panel)
- outside look soffit: soffit (build: roof soffit: painted (not drawn))
- outside look bark: bark (build: parametric tree)
- outside look foliage: foliage (build: parametric tree)
- outside look ground: soil (build: neutral ground (brief site: ground))
- outside look plot_wall: render in warm greige (build: plot wall finish not drawn: the facade's look)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L-1b_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_banyo |
| area_light | 1 | r_L-1b_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_banyo_2 |
| area_light | 1 | r_L-1b_koridor: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_koridor |
| area_light | 1 | r_L-1b_koridor_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_koridor_2 |
| area_light | 1 | r_L-1b_oda: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_oda |
| area_light | 1 | r_L-1b_oda_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L-1b_oda_2 |
| area_light | 1 | r_L0_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_banyo |
| area_light | 1 | r_L0_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_banyo_2 |
| area_light | 1 | r_L0_e_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_e_banyo |
| area_light | 1 | r_L0_e_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_e_banyo_2 |
| area_light | 1 | r_L0_koridor: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_koridor |
| area_light | 1 | r_L0_koridor_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_koridor_2 |
| area_light | 1 | r_L0_oda: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda |
| area_light | 1 | r_L0_oda_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_oda_2 |
| area_light | 1 | r_L0_yatak_odasi_3: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_3 |
| area_light | 1 | r_L0_yatak_odasi_4: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yatak_odasi_4 |
| area_light | 1 | r_L1_banyo: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo |
| area_light | 1 | r_L1_banyo_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_banyo_2 |
| area_light | 1 | r_L1_koridor: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_koridor |
| area_light | 1 | r_L1_koridor_2: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_koridor_2 |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi: room has little daylight (window/floor 0.059 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi |
| area_light | 1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2: room has little daylight (window/floor 0.059 < 0.08); soft ceiling light added (lighting mood, invisible to the camera) | light_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |
| cabinet_fronts | 3 | design detail of the cabinet (fronts and handles inside its own box); the documents show only the footprint | furn_f_L-1b_037, furn_f_L-1b_038, furn_f_L-1b_049 |
| counter_fronts | 3 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L-1b_017, furn_f_L0_003, furn_f_L0_004 |
| direction | 6 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L-1b_003, furn_f_L-1b_004, furn_f_L0_001 |
| door | 1 | style profile exterior.door (assumed) | exterior |
| door_handles | 22 | design detail of the documented door (lever handles on both faces); not in the documents | d_L-1b_001_handle, d_L-1b_002_handle, d_L-1b_003_handle |
| fabric | 3 | style profile has no textiles slot; default fabric for sofas and chairs | furniture, furniture, furniture |
| facade | 1 | style profile exterior.facade (assumed) | exterior |
| garden | 1 | style profile exterior.garden (assumed) | exterior |
| ground:+y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| ground:-y | 1 | no ground level drawn on this side: the mean of the drawn sides | site |
| handrail | 6 | design detail on every flight side not against a wall; not in the documents | furn_f_L-1b_003, furn_f_L-1b_004, furn_f_L0_001 |
| height | 22 | door height listed as assumed in the building JSON | d_L-1b_001, d_L-1b_002, d_L-1b_003 |
| height | 39 | no height in the JSON; proxy table value for unknown | proxy_f_L-1b_001, proxy_f_L-1b_002, proxy_f_L-1b_005 |
| height | 6 | no height in the JSON; type height for bathtub | furn_f_L-1b_019, furn_f_L-1b_020, furn_f_L0_027 |
| height | 6 | no height in the JSON; type height for bed_double | furn_f_L0_009, furn_f_L0_010, furn_f_L0_021 |
| height | 1 | no height in the JSON; type height for bench | furn_f_L1_022 |
| height | 4 | no height in the JSON; type height for floor_lamp | furn_f_L0_033, furn_f_L0_034, furn_f_L0_035 |
| height | 2 | no height in the JSON; type height for fridge | furn_f_L-1b_031, furn_f_L-1b_032 |
| height | 2 | no height in the JSON; type height for kitchen_counter | furn_f_L0_003, furn_f_L0_004 |
| height | 1 | no height in the JSON; type height for kitchen_island | furn_f_L-1b_017 |
| height | 2 | no height in the JSON; type height for ottoman | furn_f_L1_027, furn_f_L1_028 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_015, furn_f_L0_016 |
| height | 4 | no height in the JSON; type height for sofa | furn_f_L1_009, furn_f_L1_010, furn_f_L1_011 |
| height | 2 | no height in the JSON; type height for stove | furn_f_L-1b_013, furn_f_L-1b_015 |
| height | 8 | no height in the JSON; type height for toilet | furn_f_L-1b_011, furn_f_L-1b_012, furn_f_L0_017 |
| height | 2 | no height in the JSON; type height for wall_cabinet | furn_f_L-1b_037, furn_f_L-1b_038 |
| height | 6 | no height in the JSON; type height for wardrobe | furn_f_L0_011, furn_f_L0_012, furn_f_L0_013 |
| height | 8 | no height in the JSON; type height for washbasin | furn_f_L-1b_009, furn_f_L-1b_010, furn_f_L0_005 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L1_001 |
| height | 8 | window height listed as assumed in the building JSON | win_L-1b_001, win_L-1b_002, win_L0_001 |
| height_lift | 15 | footprint overlaps another piece of the same height; lifted so the top faces do not coincide | proxy_f_L-1b_018, proxy_f_L-1b_021, proxy_f_L-1b_022 |
| inside_sill | 2 | design detail of the documented window: an inside sill 0.05 m deep, 0.03 m proud of the wall face, in the trim look; rooms on both sides or none: the sill on the wall's right face; not in the documents | win_L1_001_inside_sill, win_L1_002_inside_sill |
| inside_sill | 6 | design detail of the documented window: an inside sill 0.1 m deep, 0.03 m proud of the wall face, in the trim look; not in the documents | win_L-1b_001_inside_sill, win_L-1b_002_inside_sill, win_L0_001_inside_sill |
| light_well:win_L-1b_001 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 7.59 m wide (no light well drawn) | site |
| light_well:win_L-1b_002 | 1 | window sill -2.10 m, ground outside 0.00 m: an open concrete light well 0.8 m deep, 7.59 m wide (no light well drawn) | site |
| mansard_ends | 1 | the section does not cut the two other sides: their lower slopes take the section's lower pitch from the eaves height and, with no upper slope drawn there, run up to the ridge | roof |
| north_deg | 1 | assumed (+Y is north: no north arrow) | sun |
| parapet | 1 | roof terrace ro_001: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_008 |
| parapet | 1 | roof terrace ro_002: its walls end at a 1.0 m parapet (height assumed) | w_L1_001,w_L1_007,w_L1_016 |
| parapet_height:ro_001 | 1 | not drawn | roof |
| parapet_height:ro_002 | 1 | not drawn | roof |
| paving | 1 | style profile exterior.paving (assumed) | exterior |
| ridge_direction | 1 | read from one section profile (cut along x): the ridge runs across the cut through its highest point | roof |
| riser_m | 2 | derived from the documented ceiling and assumed slab: 3.583 m / 12 drawn risers | furn_f_L1_001, furn_f_L1_002 |
| riser_m | 2 | derived from the level elevations (floor to floor): 3.000 m / 12 drawn risers | furn_f_L-1b_003, furn_f_L-1b_004 |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.150 m / 11 drawn risers | furn_f_L0_001 |
| riser_m | 1 | derived from the level elevations (floor to floor): 3.150 m / 12 drawn risers | furn_f_L0_002 |
| roof | 1 | style profile exterior.roof (assumed) | exterior |
| sill | 2 | outside sill 2.2285 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_002_sill, win_L0_003_sill |
| sill | 2 | outside sill 2.7431 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L0_001_sill, win_L0_004_sill |
| sill | 2 | outside sill 7.2461 x 0.109 m, 0.04 m proud of the facade (not drawn; size assumed) | win_L-1b_001_sill, win_L-1b_002_sill |
| sill_height | 8 | window sill_height listed as assumed in the building JSON | win_L-1b_001, win_L-1b_002, win_L0_001 |
| site | 1 | not in the brief: the default of wenart/defaults.yaml | brief |
| skirting | 18 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L-1b_oda, skirting_r_L-1b_oda_2, skirting_r_L-1b_koridor |
| turn | 6 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L-1b_003, furn_f_L-1b_004, furn_f_L0_001 |
| void | 2 | nothing drawn above the stair; the opening is assumed; the floor above is not modelled, so the cap hides the shaft | f_L1_001_void, f_L1_002_void |
| waist | 6 | the documents show the stair in plan only | furn_f_L-1b_003, furn_f_L-1b_004, furn_f_L0_001 |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L-1b_koridor | cam_r_L-1b_koridor_2, cam_r_L-1b_koridor_3 | cam_r_L-1b_koridor_1 (vision_check) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L-1b_acik_mutfak_2 (rung None).

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

Assets: textures CC0 x 14; furniture/decor models CC-BY-4.0 x 163, generated (TRELLIS.2-4B, MIT) x 11 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Bed" by Ambriel (https://sketchfab.com/3d-models/08f7f65edfea417b8ed9ca748381e507), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_009, f_L0_010)
- "low poly Lamp 3d model" by mohamedvfx (https://sketchfab.com/3d-models/53409613b45b42b98b979f12ab8faa12), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1_021, f_L-1_023, f_L-1_027, f_L-1_028, f_L-1_029, f_L-1_030, f_L0_033, f_L0_034, f_L0_035, f_L0_036)
- "Fridge" by Yaseen Ali (https://sketchfab.com/3d-models/66878d980a364b2db1a5cc44c67bb45d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1_031, f_L-1_032, f_L-1b_031, f_L-1b_032)
- "JuiceMachine" by voxelpoint (https://sketchfab.com/3d-models/6b46b33bdff44269bf9391774bb8dd63), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for dec_L0_003, dec_L0_033)
- "R RETRO FIRIN" by Motto Teknoloji (https://sketchfab.com/3d-models/934716ccd00d4f6ba9555d1cea788488), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1b_013, f_L-1b_015)
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1b_042, f_L-1b_047, f_L-1_054, f_L-1_055, f_L-1_056, f_L-1_057, f_L-1_058, f_L-1_059, f_L-1_060, f_L1_030, f_L-1_067, f_L-1_068, f_L-1_069, f_L-1_070, f_L-1_071, f_L-1_072, f_L-1_073, f_L1_034)
- "High Bookcase" by 8549 (https://sketchfab.com/3d-models/d48a42e91c5d4716a8c254addf8c9d99), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L-1b_040, f_L-1b_045)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | calibrated | yes | no | - |
| cam_r_L-1b_acik_mutfak_2 | calibrated | yes | no | - |
| cam_r_L-1b_acik_mutfak_3 | calibrated | yes | no | - |
| cam_r_L-1b_koridor_1 | calibrated | yes | yes | furniture [861.3, 388.6, 1281.1, 770.6] (score); furniture [860.9, 392.8, 1076.5, 735.1] (score, vlm:qwen); furniture [860.9, 392.8, 1076.5, 735.1] (vlm:qwen) |
| cam_r_L-1b_koridor_2 | calibrated | yes | no | - |
| cam_r_L-1b_koridor_3 | calibrated | yes | no | - |
| cam_r_L-1b_oda_1 | calibrated | yes | no | - |
| cam_r_L-1b_oda_2 | calibrated | yes | no | - |
| cam_r_L-1b_oda_3 | calibrated | yes | no | - |

## Stages

This run (`20261009-082737-full-20261009T083331Z`):

| stage | status | seconds | note |
|---|---|---|---|
| build | ok | 2.5 min | - |
| render | ok | 110.3 s | - |
| export | ok | 49.5 s | - |
| controls | ok | 28.2 s | - |
| gate | ok | 1.4 s | gate decision ok (the base project's calibration) |
| polish | ok | 118.4 s | - |
| detect | ok | 7.2 s | - |
| expected | ok | 12.5 s | - |
| check | ok | 88.0 s | - |
| combine | ok | 20.1 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
