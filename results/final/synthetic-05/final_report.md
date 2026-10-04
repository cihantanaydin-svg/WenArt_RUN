# Final report: synthetic-05

23 views: 0 polished, 23 Cycles (brief 23). Stages: render run, gate validation not_run, polish not_run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 23 |
| polished | 0 |
| Cycles | 23 (brief 23) |
| confirmed mismatches on the final image | 1 in 1 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 6 |
| exposure | -1.00 .. +6.00 EV (0 at a limit), modes auto |
| window pull | 16 view(s), -3 .. -1 EV |
| camera policy | search 23 |
| camera score (min / mean / max) | 1.81 / 3.14 / 3.75 |
| rooms by number of views | 1 with 1, 2 with 2, 6 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 18.6 s / 71.7 s / 6.6 s |
| seconds: polish / gate / check | - / - / 5.6 min |
| brief polish | no |
| unit system | metric |
| side-by-side sheets | 0 |

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check advisory: removal_flagged 0.6667 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.667 (needs >= 0.8)
- check target missed: removal_confirmed 0.500 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- brief polish: false (no AI polish by request)

## Gate validation

Not needed: brief polish: false (every view is the Cycles render).

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Side-by-side sheets (Cycles | polished)

None: brief polish: false.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_antre_1 | r_L0_antre | L0 | cycles | brief | - | - | ok | - | - | -1.00 | - | search 3.13 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_antre_2 | r_L0_antre | L0 | cycles | brief | - | - | ok | - | - | -1.00 | - | search 3.11 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_2_final_preview.jpg) [plan](cam_r_L0_antre_2_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | brief | - | - | ok | - | - | +5.67 | -2 | search 2.49 | D3 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | brief | - | - | info | - | - | +5.83 | -3 | search 2.32 | D4 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_banyo_3 | r_L0_banyo | L0 | cycles | brief | - | - | info | - | - | +6.00 | -2 | search 1.81 | D2 | 0 | no | [preview](cam_r_L0_banyo_3_final_preview.jpg) [plan](cam_r_L0_banyo_3_plan.jpg) |
| cam_r_L0_calisma_odasi_1 | r_L0_calisma_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.67 | -1 | search 3.58 | D2 A3 | 0 | no | [preview](cam_r_L0_calisma_odasi_1_final_preview.jpg) [plan](cam_r_L0_calisma_odasi_1_plan.jpg) |
| cam_r_L0_calisma_odasi_2 | r_L0_calisma_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.50 | - | search 3.39 | D1 A3 | 0 | no | [preview](cam_r_L0_calisma_odasi_2_final_preview.jpg) [plan](cam_r_L0_calisma_odasi_2_plan.jpg) |
| cam_r_L0_calisma_odasi_3 | r_L0_calisma_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.67 | - | search 3.28 | D1 A3 | 0 | no | [preview](cam_r_L0_calisma_odasi_3_final_preview.jpg) [plan](cam_r_L0_calisma_odasi_3_plan.jpg) |
| cam_r_L0_ebeveyn_banyo_1 | r_L0_ebeveyn_banyo | L0 | cycles | brief | - | - | mismatch (1) | - | - | +5.00 | -1 | search 3.07 | D3 | 0 | yes | [preview](cam_r_L0_ebeveyn_banyo_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_banyo_1_plan.jpg) |
| cam_r_L0_ebeveyn_banyo_2 | r_L0_ebeveyn_banyo | L0 | cycles | brief | - | - | info | - | - | +4.50 | -1 | search 2.56 | D3 | 0 | no | [preview](cam_r_L0_ebeveyn_banyo_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_banyo_2_plan.jpg) |
| cam_r_L0_ebeveyn_yatak_odasi_1 | r_L0_ebeveyn_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.17 | -1 | search 3.73 | D5 | 0 | no | [preview](cam_r_L0_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L0_ebeveyn_yatak_odasi_2 | r_L0_ebeveyn_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.00 | - | search 3.72 | D4 | 0 | no | [preview](cam_r_L0_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L0_ebeveyn_yatak_odasi_3 | r_L0_ebeveyn_yatak_odasi | L0 | cycles | brief | - | - | info | - | - | +4.17 | -1 | search 3.68 | D3 | 0 | no | [preview](cam_r_L0_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | cycles | brief | - | - | ok | - | - | -0.33 | - | search 2.11 | D5 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | brief | - | - | info | - | - | +4.33 | -1 | search 3.75 | D6 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | brief | - | - | ok | - | - | +4.17 | -1 | search 3.61 | D6 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | brief | - | - | ok | - | - | +4.17 | -1 | search 3.59 | D6 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | brief | - | - | ok | - | - | +3.83 | -1 | search 3.11 | D4 A1 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | cycles | brief | - | - | info | - | - | +3.83 | -1 | search 3.08 | D6 A1 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | cycles | brief | - | - | info | - | - | +3.67 | - | search 2.95 | D7 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.83 | -1 | search 3.56 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.83 | -1 | search 3.52 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +5.33 | -1 | search 3.15 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_antre | hall | L0 | 2 | 0 | 2 | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_banyo | bathroom | L0 | 3 | 0 | 3 | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_calisma_odasi | other | L0 | 3 | 0 | 3 | cam_r_L0_calisma_odasi_1, cam_r_L0_calisma_odasi_2, cam_r_L0_calisma_odasi_3 |
| r_L0_ebeveyn_banyo | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_ebeveyn_banyo_1, cam_r_L0_ebeveyn_banyo_2 |
| r_L0_ebeveyn_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_yatak_odasi_1, cam_r_L0_ebeveyn_yatak_odasi_2, cam_r_L0_ebeveyn_yatak_odasi_3 |
| r_L0_hol | hall | L0 | 1 | 0 | 1 | cam_r_L0_hol_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 0 | 3 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_2 | cycles | disputed | f_L0_022 | toilet | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:16D KLOZET vector 1.00 | info | - |
| cam_r_L0_banyo_3 | cycles | disputed | f_L0_021 | bathtub | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:16B KUVET vector 1.00 | info | - |
| cam_r_L0_ebeveyn_banyo_1 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L0_ebeveyn_yatak_odasi_3 | cycles | disputed | f_L0_007 | bed_double | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:14F YATAK_CIFT vector 1.00 | info | - |
| cam_r_L0_salon_2 | cycles | disputed | f_L0_005 | chair | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:14B SANDALYE vector 1.00 | info | - |
| cam_r_L0_salon_2 | cycles | disputed | f_L0_004 | table_dining | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:149 YEMEK_MASASI vector 1.00 | info | - |

## Needs review

- cam_r_L0_ebeveyn_banyo_1: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Units

Project unit system: **metric** (not recorded in the building JSON: metric).

| document | unit system | source kind |
|---|---|---|
| zemin_kat.dxf | metric | dxf |
| zemin_kat_mobilya.dxf | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: -. Recognition questions: -; answer files: none. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

## Site

Recorded, not built.

None.

## Separators

None.

## Assumed values

- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- L0: ceiling height 2,70 m (assumed_default)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_antre: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_antre |
| area_light | 1 | r_L0_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_hol |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
| counter_fronts | 2 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_015, furn_f_L0_016 |
| door_handles | 9 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| height | 9 | door height not in the JSON; default | d_L0_001, d_L0_002, d_L0_003 |
| height | 1 | no height in the JSON; type height for bathtub | furn_f_L0_021 |
| height | 1 | no height in the JSON; type height for bed_double | furn_f_L0_007 |
| height | 2 | no height in the JSON; type height for bed_single | furn_f_L0_024, furn_f_L0_025 |
| height | 2 | no height in the JSON; type height for chair | furn_f_L0_005, furn_f_L0_006 |
| height | 1 | no height in the JSON; type height for dresser | furn_f_L0_011 |
| height | 1 | no height in the JSON; type height for fridge | furn_f_L0_019 |
| height | 2 | no height in the JSON; type height for kitchen_counter | furn_f_L0_015, furn_f_L0_016 |
| height | 3 | no height in the JSON; type height for nightstand | furn_f_L0_008, furn_f_L0_009, furn_f_L0_026 |
| height | 1 | no height in the JSON; type height for shower | furn_f_L0_012 |
| height | 1 | no height in the JSON; type height for sink_kitchen | furn_f_L0_017 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L0_001 |
| height | 1 | no height in the JSON; type height for stove | furn_f_L0_018 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L0_002 |
| height | 1 | no height in the JSON; type height for table_dining | furn_f_L0_004 |
| height | 2 | no height in the JSON; type height for toilet | furn_f_L0_013, furn_f_L0_022 |
| height | 1 | no height in the JSON; type height for tv_unit | furn_f_L0_003 |
| height | 1 | no height in the JSON; type height for wardrobe | furn_f_L0_010 |
| height | 2 | no height in the JSON; type height for washbasin | furn_f_L0_014, furn_f_L0_023 |
| height | 1 | no height in the JSON; type height for washing_machine | furn_f_L0_020 |
| height | 10 | window height not in the JSON; default | win_L0_001, win_L0_002, win_L0_003 |
| height_lift | 2 | footprint overlaps another piece of the same height; lifted so the top faces do not coincide | furn_f_L0_017, furn_f_L0_018 |
| sill_height | 10 | window sill_height not in the JSON; default | win_L0_001, win_L0_002, win_L0_003 |
| skirting | 6 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_salon, skirting_r_L0_ebeveyn_yatak_odasi, skirting_r_L0_hol |
| wood | 1 | style floor 'concrete_polished' is not wood; default veneer for furniture frames | furniture |

## Rooms mixing polished and Cycles views

None.

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check qwen | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | check_manifest.json |
| check glm | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | check_manifest.json |

Assets: textures CC0 x 4; furniture/decor models CC-BY-4.0 x 11, CC0 x 6 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Bed For Vr" by olamii (https://sketchfab.com/3d-models/2bd3fcc82c9f43cfb0c8cf26c7d0107c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_007)
- "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_001)
- "Low Poly - Chair and Table" by tadeus (https://sketchfab.com/3d-models/5f235f066a9a416fb7177496a9117ec7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_004)
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_019)
- "Bed - Sample" by Mifu Saja (https://sketchfab.com/3d-models/b547d81073b64d3e97200fd3ae9a74af), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_024, f_L0_025)
- "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_014, f_L0_023)
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_005, f_L0_006, f_L0_029)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence (here CC0 1.0 or CC BY 4.0), as declared by its uploader and not verified by WenArt_RUN: check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261004-000052-full-20261004T000516Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 6.2 s | - |
| pipeline_final | skipped | 0.0 s | no questions |
| recognize | skipped | 0.0 s | no questions |
| fit | ok | 1.2 s | - |
| style | ok | 0.2 s | - |
| layout | ok | 15.5 s | - |
| photos | reused | 0.2 s | - |
| assets | ok | 0.6 s | - |
| decor | ok | 1.6 s | - |
| refit | ok | 1.2 s | - |
| build | ok | 24.3 s | - |
| render | ok | 2.9 min | - |
| controls | ok | 63.6 s | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 19.8 s | - |
| check | ok | 84.2 s | - |
| combine | ok | 2.2 min | - |

The report stage itself is recorded after this report.

## Warnings

- final/cam_r_L0_hol_2_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L0_hol_3_final_preview.jpg is from an earlier run (not part of this report)
- final/cam_r_L0_hol_2_plan.jpg is from an earlier run (not part of this report)
- final/cam_r_L0_hol_3_plan.jpg is from an earlier run (not part of this report)
