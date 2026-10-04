# Final report: synthetic-06

17 views: 16 polished, 1 Cycles (vision_check 1). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 17 |
| polished | 16 |
| Cycles | 1 (vision_check 1) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 5 |
| exposure | -0.67 .. +4.83 EV (0 at a limit), modes auto |
| window pull | 11 view(s), -2 .. -1 EV |
| camera policy | search 17 |
| camera score (min / mean / max) | 1.26 / 3.33 / 5.22 |
| rooms by number of views | 1 with 2, 5 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 28.2 s / 46.3 s / 5.2 s |
| seconds: polish / gate / check | 71.8 s / 6.5 s / 8.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | imperial |
| side-by-side sheets | 6 |

## Advisory flags and open items

- vision check advisory: removal_flagged 0.75 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.750 (needs >= 0.8)
- check target missed: removal_confirmed 0.500 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- the polish added an object in cam_r_L0_master_bed_room_3: the Cycles render is final

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 95.8 % (limit 95 %), 48 comparisons |
| negative controls rejected | 97.2 % (limit 90 %), 72 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- r_L0_bath: [contact_sbs_r_L0_bath.jpg](contact_sbs_r_L0_bath.jpg)

- r_L0_bed_room: [contact_sbs_r_L0_bed_room.jpg](contact_sbs_r_L0_bed_room.jpg)

- r_L0_kitchen: [contact_sbs_r_L0_kitchen.jpg](contact_sbs_r_L0_kitchen.jpg)

- r_L0_living_room: [contact_sbs_r_L0_living_room.jpg](contact_sbs_r_L0_living_room.jpg)

- r_L0_lobby: [contact_sbs_r_L0_lobby.jpg](contact_sbs_r_L0_lobby.jpg)

- r_L0_master_bed_room: [contact_sbs_r_L0_master_bed_room.jpg](contact_sbs_r_L0_master_bed_room.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| r_L0_bath | cam_r_L0_bath_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_bath | cam_r_L0_bath_2 | a3 s 0.125 depth x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_bed_room | cam_r_L0_bed_room_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_bed_room | cam_r_L0_bed_room_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_bed_room | cam_r_L0_bed_room_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_kitchen | cam_r_L0_kitchen_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_kitchen | cam_r_L0_kitchen_2 | a1 s 0.375 geometry x0.8 | accept | ok | info | calibrated | polished |
| r_L0_kitchen | cam_r_L0_kitchen_3 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_living_room | cam_r_L0_living_room_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_living_room | cam_r_L0_living_room_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_living_room | cam_r_L0_living_room_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_lobby | cam_r_L0_lobby_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_lobby | cam_r_L0_lobby_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_lobby | cam_r_L0_lobby_3 | a1 s 0.375 geometry x0.8 | accept | ok | info | calibrated | polished |
| r_L0_master_bed_room | cam_r_L0_master_bed_room_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L0_master_bed_room | cam_r_L0_master_bed_room_2 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L0_master_bed_room | cam_r_L0_master_bed_room_3 | a1 s 0.375 geometry x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_1 | r_L0_bath | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.83 | -2 | search 1.40 | D2 | 0 | no | [preview](cam_r_L0_bath_1_final_preview.jpg) [plan](cam_r_L0_bath_1_plan.jpg) |
| cam_r_L0_bath_2 | r_L0_bath | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | ok | ok | not preferred 1/4 | +3.67 | - | search 1.26 | D1 | 0 | no | [preview](cam_r_L0_bath_2_final_preview.jpg) [plan](cam_r_L0_bath_2_plan.jpg) |
| cam_r_L0_bed_room_1 | r_L0_bed_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.00 | -1 | search 3.65 | D2 A3 | 0 | no | [preview](cam_r_L0_bed_room_1_final_preview.jpg) [plan](cam_r_L0_bed_room_1_plan.jpg) |
| cam_r_L0_bed_room_2 | r_L0_bed_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +3.67 | -1 | search 3.44 | D2 A1 | 0 | no | [preview](cam_r_L0_bed_room_2_final_preview.jpg) [plan](cam_r_L0_bed_room_2_plan.jpg) |
| cam_r_L0_bed_room_3 | r_L0_bed_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.83 | -2 | search 3.24 | D2 A4 | 0 | no | [preview](cam_r_L0_bed_room_3_final_preview.jpg) [plan](cam_r_L0_bed_room_3_plan.jpg) |
| cam_r_L0_kitchen_1 | r_L0_kitchen | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.67 | -1 | search 2.63 | D7 | 0 | no | [preview](cam_r_L0_kitchen_1_final_preview.jpg) [plan](cam_r_L0_kitchen_1_plan.jpg) |
| cam_r_L0_kitchen_2 | r_L0_kitchen | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 0/4 | +4.50 | -1 | search 2.60 | D6 | 0 | no | [preview](cam_r_L0_kitchen_2_final_preview.jpg) [plan](cam_r_L0_kitchen_2_plan.jpg) |
| cam_r_L0_kitchen_3 | r_L0_kitchen | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.67 | - | search 1.84 | D7 | 0 | no | [preview](cam_r_L0_kitchen_3_final_preview.jpg) [plan](cam_r_L0_kitchen_3_plan.jpg) |
| cam_r_L0_living_room_1 | r_L0_living_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.50 | -1 | search 5.22 | D3 | 0 | no | [preview](cam_r_L0_living_room_1_final_preview.jpg) [plan](cam_r_L0_living_room_1_plan.jpg) |
| cam_r_L0_living_room_2 | r_L0_living_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.50 | -1 | search 5.19 | D6 A1 | 0 | no | [preview](cam_r_L0_living_room_2_final_preview.jpg) [plan](cam_r_L0_living_room_2_plan.jpg) |
| cam_r_L0_living_room_3 | r_L0_living_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +4.50 | -1 | search 4.62 | D2 A1 | 0 | no | [preview](cam_r_L0_living_room_3_final_preview.jpg) [plan](cam_r_L0_living_room_3_plan.jpg) |
| cam_r_L0_lobby_1 | r_L0_lobby | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | -0.50 | - | search 2.86 | D4 A1 | 0 | no | [preview](cam_r_L0_lobby_1_final_preview.jpg) [plan](cam_r_L0_lobby_1_plan.jpg) |
| cam_r_L0_lobby_2 | r_L0_lobby | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | -0.50 | - | search 2.64 | D4 A1 | 0 | no | [preview](cam_r_L0_lobby_2_final_preview.jpg) [plan](cam_r_L0_lobby_2_plan.jpg) |
| cam_r_L0_lobby_3 | r_L0_lobby | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 0/4 | -0.67 | - | search 2.36 | D3 A1 | 0 | no | [preview](cam_r_L0_lobby_3_final_preview.jpg) [plan](cam_r_L0_lobby_3_plan.jpg) |
| cam_r_L0_master_bed_room_1 | r_L0_master_bed_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +4.17 | - | search 4.62 | D2 | 0 | no | [preview](cam_r_L0_master_bed_room_1_final_preview.jpg) [plan](cam_r_L0_master_bed_room_1_plan.jpg) |
| cam_r_L0_master_bed_room_2 | r_L0_master_bed_room | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.17 | -1 | search 4.59 | D3 | 0 | no | [preview](cam_r_L0_master_bed_room_2_final_preview.jpg) [plan](cam_r_L0_master_bed_room_2_plan.jpg) |
| cam_r_L0_master_bed_room_3 | r_L0_master_bed_room | L0 | cycles | vision_check | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.83 | -1 | search 4.54 | D3 A1 | 0 | no | [preview](cam_r_L0_master_bed_room_3_final_preview.jpg) [plan](cam_r_L0_master_bed_room_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_bath | bathroom | L0 | 2 | 2 | 0 | cam_r_L0_bath_1, cam_r_L0_bath_2 |
| r_L0_bed_room | bedroom | L0 | 3 | 3 | 0 | cam_r_L0_bed_room_1, cam_r_L0_bed_room_2, cam_r_L0_bed_room_3 |
| r_L0_kitchen | kitchen | L0 | 3 | 3 | 0 | cam_r_L0_kitchen_1, cam_r_L0_kitchen_2, cam_r_L0_kitchen_3 |
| r_L0_living_room | living | L0 | 3 | 3 | 0 | cam_r_L0_living_room_1, cam_r_L0_living_room_2, cam_r_L0_living_room_3 |
| r_L0_lobby | hall | L0 | 3 | 3 | 0 | cam_r_L0_lobby_1, cam_r_L0_lobby_2, cam_r_L0_lobby_3 |
| r_L0_master_bed_room | bedroom | L0 | 3 | 2 | 1 | cam_r_L0_master_bed_room_1, cam_r_L0_master_bed_room_2, cam_r_L0_master_bed_room_3 |

### Why Cycles

- cam_r_L0_master_bed_room_3: vision_check: added_by_polish furniture at [23.8, 845.0, 562.0, 1014.9]

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_kitchen_3 | cycles | disputed | f_L0_007 | chair | optional | from_documents | synthetic-06.dwg INSERT:FF/6/0,INSERT:FF/6/1 DINING-6/CHAIR vector 0.90 | info | - |
| cam_r_L0_kitchen_3 | polished | disputed | f_L0_007 | chair | optional | from_documents | synthetic-06.dwg INSERT:FF/6/0,INSERT:FF/6/1 DINING-6/CHAIR vector 0.90 | info | - |
| cam_r_L0_lobby_1 | cycles | missing | d_L0_003 | door | optional | from_documents | synthetic-06.dwg ARC:CF,LINE:D0 vector 0.95 | info | - |
| cam_r_L0_lobby_1 | polished | missing | d_L0_003 | door | optional | from_documents | synthetic-06.dwg ARC:CF,LINE:D0 vector 0.95 | info | - |
| cam_r_L0_lobby_2 | cycles | missing | d_L0_005 | door | optional | from_documents | synthetic-06.dwg ARC:D3,LINE:D4 vector 0.95 | info | - |
| cam_r_L0_lobby_2 | cycles | missing | d_L0_004 | door | optional | from_documents | synthetic-06.dwg ARC:D1,LINE:D2 vector 0.95 | info | - |
| cam_r_L0_lobby_2 | cycles | missing | d_L0_003 | door | optional | from_documents | synthetic-06.dwg ARC:CF,LINE:D0 vector 0.95 | info | - |
| cam_r_L0_lobby_2 | polished | missing | d_L0_004 | door | optional | from_documents | synthetic-06.dwg ARC:D1,LINE:D2 vector 0.95 | info | - |
| cam_r_L0_lobby_2 | polished | missing | d_L0_003 | door | optional | from_documents | synthetic-06.dwg ARC:CF,LINE:D0 vector 0.95 | info | - |
| cam_r_L0_master_bed_room_2 | cycles | missing | d_L0_004 | door | optional | from_documents | synthetic-06.dwg ARC:D1,LINE:D2 vector 0.95 | info | - |
| cam_r_L0_master_bed_room_2 | polished | missing | d_L0_004 | door | optional | from_documents | synthetic-06.dwg ARC:D1,LINE:D2 vector 0.95 | info | - |

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Units

Project unit system: **imperial** (lengths in feet and inches, metres in brackets).

| document | unit system | source kind |
|---|---|---|
| synthetic-06.dwg | imperial | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: block_name 11. Recognition questions: -; answer files: none. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

## Site

Recorded, not built.

None.

## Separators

Virtual lines that split an open-plan face where two room names share it (no geometry is built; the pipeline's report.md lists the candidates it dropped):

| id | level | length | status | reason |
|---|---|---|---|---|
| o_L0_001 | L0 | 6' 0" (1.83 m) | verified | virtual separator (end-to-wall, 1.83 m): two room names shared one face |

## Assumed values

- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 8' 10" (2.70 m) (assumed_default)
- door height 6' 11" (2.10 m): 5 opening(s) (d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_005)
- window height 3' 11" (1.20 m): 8 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- window sill height 2' 11" (0.90 m): 8 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_lobby: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_lobby |
| bedding | 1 | design detail of the bed (soft bedding inside the bed's own box); the documents show only the footprint | furn_f_L0_001 |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
| door_handles | 5 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| height | 5 | door height listed as assumed in the building JSON | d_L0_001, d_L0_002, d_L0_003 |
| height | 1 | no height in the JSON; type height for bed_double | furn_f_L0_001 |
| height | 6 | no height in the JSON; type height for chair | furn_f_L0_005, furn_f_L0_006, furn_f_L0_007 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L0_002 |
| height | 1 | no height in the JSON; type height for table_dining | furn_f_L0_003 |
| height | 1 | no height in the JSON; type height for toilet | furn_f_L0_004 |
| height | 1 | no height in the JSON; type height for washbasin | furn_f_L0_011 |
| height | 8 | window height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| sill_height | 8 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| skirting | 4 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_living_room, skirting_r_L0_lobby, skirting_r_L0_bed_room |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L0_master_bed_room | cam_r_L0_master_bed_room_1, cam_r_L0_master_bed_room_2 | cam_r_L0_master_bed_room_3 (vision_check) | ok |

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

Assets: textures CC0 x 6; furniture/decor models CC-BY-4.0 x 10, CC0 x 5 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Bed For Vr" by olamii (https://sketchfab.com/3d-models/2bd3fcc82c9f43cfb0c8cf26c7d0107c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_013)
- "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_002)
- "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_011)
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_005, f_L0_006, f_L0_007, f_L0_008, f_L0_009, f_L0_010, f_L0_012)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence (here CC0 1.0 or CC BY 4.0), as declared by its uploader and not verified by WenArt_RUN: check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L0_bath_1 | calibrated | yes | no | - |
| cam_r_L0_bath_2 | calibrated | yes | no | - |
| cam_r_L0_bed_room_1 | calibrated | yes | no | - |
| cam_r_L0_bed_room_2 | calibrated | yes | no | - |
| cam_r_L0_bed_room_3 | calibrated | yes | no | - |
| cam_r_L0_kitchen_1 | calibrated | yes | no | - |
| cam_r_L0_kitchen_2 | calibrated | yes | no | - |
| cam_r_L0_kitchen_3 | calibrated | yes | no | - |
| cam_r_L0_living_room_1 | calibrated | yes | no | - |
| cam_r_L0_living_room_2 | calibrated | yes | no | - |
| cam_r_L0_living_room_3 | calibrated | yes | no | - |
| cam_r_L0_lobby_1 | calibrated | yes | no | - |
| cam_r_L0_lobby_2 | calibrated | yes | no | - |
| cam_r_L0_lobby_3 | calibrated | yes | no | - |
| cam_r_L0_master_bed_room_1 | calibrated | yes | no | - |
| cam_r_L0_master_bed_room_2 | calibrated | yes | no | - |
| cam_r_L0_master_bed_room_3 | calibrated | yes | yes | furniture [23.8, 845.0, 562.0, 1014.9] (vlm:qwen) |

## Stages

This run (`20261004-000052-full-20261004T000516Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 8.5 s | - |
| pipeline_final | skipped | 0.0 s | no questions |
| recognize | skipped | 0.0 s | no questions |
| fit | ok | 1.3 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.2 s | - |
| layout | ok | 17.1 s | - |
| assets | ok | 0.5 s | - |
| decor | ok | 1.6 s | - |
| refit | ok | 1.2 s | - |
| build | ok | 33.9 s | - |
| render | ok | 95.4 s | - |
| controls | ok | 49.0 s | - |
| gate | ok | 47.0 s | gate decision ok |
| polish | ok | 2.1 min | - |
| detect | ok | 10.2 s | - |
| expected | ok | 16.1 s | - |
| check | ok | 114.0 s | - |
| combine | ok | 114.1 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
