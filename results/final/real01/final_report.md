# Final report: real01

20 views: 0 polished, 20 Cycles (gate_validation 20). Stages: render run, gate validation polish_disabled, polish not_run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 20 |
| polished | 0 |
| Cycles | 20 (gate_validation 20) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 3 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 7 |
| exposure | -0.67 .. +4.50 EV (0 at a limit), modes auto |
| window pull | 15 view(s), -2 .. -1 EV |
| camera policy | search 20 |
| camera score (min / mean / max) | 1.90 / 3.52 / 4.67 |
| rooms by number of views | 2 with 0, 1 with 2, 6 with 3 |
| gate validation | polish_disabled |
| seconds: build / render / metering | 52.2 s / 60.3 s / 7.1 s |
| seconds: polish / gate / check | - / - / 9.9 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | imperial |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real01.blend](3d/real01.blend) | 75.8 MB |
| [real01.glb](3d/real01.glb) | 152.6 MB |

20 cameras; textures scaled to at most 1024 px (72 scaled) for the download.

## AI decor

19 decor items chosen by the AI (Qwen/Qwen3-VL-8B-Instruct; both passes agreeing) in 5 rooms; 0 items by the rules. No furniture was moved, added or removed (`furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check advisory: removal_flagged 0.5714 misses >= 0.8; removal_confirmed 0.5714 misses >= 0.6; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.571 (needs >= 0.8)
- check target missed: removal_confirmed 0.571 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- gate validation polish_disabled: no polish for this project: every final image is the Cycles render (negative controls rejected 0.877 < 0.90 (106 comparisons): the gate lets geometry changes through)
- 1 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L0_018

## Gate validation

| item | value |
|---|---|
| decision | polish_disabled |
| benign controls accepted | 98.2 % (limit 95 %), 56 comparisons |
| negative controls rejected | 87.7 % (limit 90 %), 106 comparisons |
| effect | no polish for this project: every final image is the Cycles render |

Reasons:

- negative controls rejected 0.877 < 0.90 (106 comparisons): the gate lets geometry changes through

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Side-by-side sheets (Cycles | polished)

None: gate validation polish_disabled: no polish for this project.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | L0 | cycles | gate_validation | - | - | info | - | - | -0.67 | - | search 2.81 | D1 A3 | 0 | no | [preview](cam_r_L0_bath_toilet_1_final_preview.jpg) [plan](cam_r_L0_bath_toilet_1_plan.jpg) |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | L0 | cycles | gate_validation | - | - | info | - | - | -0.50 | - | search 1.90 | D1 A3 | 0 | no | [preview](cam_r_L0_bath_toilet_2_final_preview.jpg) [plan](cam_r_L0_bath_toilet_2_plan.jpg) |
| cam_r_L0_bed_room_1 | r_L0_bed_room | L0 | cycles | gate_validation | - | - | info | - | - | +3.33 | -1 | search 3.76 | D3 A1 | 0 | no | [preview](cam_r_L0_bed_room_1_final_preview.jpg) [plan](cam_r_L0_bed_room_1_plan.jpg) |
| cam_r_L0_bed_room_2 | r_L0_bed_room | L0 | cycles | gate_validation | - | - | ok | - | - | +3.67 | -2 | search 3.65 | D5 A1 | 0 | no | [preview](cam_r_L0_bed_room_2_final_preview.jpg) [plan](cam_r_L0_bed_room_2_plan.jpg) |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | L0 | cycles | gate_validation | - | - | info | - | - | +3.67 | -1 | search 3.79 | D4 A1 | 0 | no | [preview](cam_r_L0_bed_room_2_1_final_preview.jpg) [plan](cam_r_L0_bed_room_2_1_plan.jpg) |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | L0 | cycles | gate_validation | - | - | ok | - | - | +4.00 | -1 | search 3.69 | D4 A1 | 0 | no | [preview](cam_r_L0_bed_room_2_2_final_preview.jpg) [plan](cam_r_L0_bed_room_2_2_plan.jpg) |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | L0 | cycles | gate_validation | - | - | ok | - | - | +3.83 | -1 | search 3.45 | D5 A1 | 0 | no | [preview](cam_r_L0_bed_room_2_3_final_preview.jpg) [plan](cam_r_L0_bed_room_2_3_plan.jpg) |
| cam_r_L0_bed_room_3 | r_L0_bed_room | L0 | cycles | gate_validation | - | - | info | - | - | +3.50 | -1 | search 3.44 | D5 | 0 | no | [preview](cam_r_L0_bed_room_3_final_preview.jpg) [plan](cam_r_L0_bed_room_3_plan.jpg) |
| cam_r_L0_dining_1 | r_L0_dining | L0 | cycles | gate_validation | - | - | ok | - | - | +4.33 | -1 | search 3.00 | D9 A1 | 0 | no | [preview](cam_r_L0_dining_1_final_preview.jpg) [plan](cam_r_L0_dining_1_plan.jpg) |
| cam_r_L0_dining_2 | r_L0_dining | L0 | cycles | gate_validation | - | - | ok | - | - | +4.50 | -1 | search 2.51 | D7 A2 | 0 | no | [preview](cam_r_L0_dining_2_final_preview.jpg) [plan](cam_r_L0_dining_2_plan.jpg) |
| cam_r_L0_dining_3 | r_L0_dining | L0 | cycles | gate_validation | - | - | ok | - | - | +4.50 | -2 | search 2.48 | D8 A2 | 0 | no | [preview](cam_r_L0_dining_3_final_preview.jpg) [plan](cam_r_L0_dining_3_plan.jpg) |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | L0 | cycles | gate_validation | - | - | ok | - | - | +2.83 | -1 | search 3.83 | D6 A2 | 1 | no | [preview](cam_r_L0_drawing_room_1_final_preview.jpg) [plan](cam_r_L0_drawing_room_1_plan.jpg) |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | L0 | cycles | gate_validation | - | - | ok | - | - | +2.67 | -1 | search 3.60 | D6 A2 | 1 | no | [preview](cam_r_L0_drawing_room_2_final_preview.jpg) [plan](cam_r_L0_drawing_room_2_plan.jpg) |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | L0 | cycles | gate_validation | - | - | ok | - | - | +2.50 | -1 | search 3.48 | D8 A1 | 1 | no | [preview](cam_r_L0_drawing_room_3_final_preview.jpg) [plan](cam_r_L0_drawing_room_3_plan.jpg) |
| cam_r_L0_kitchen_1 | r_L0_kitchen | L0 | cycles | gate_validation | - | - | ok | - | - | +4.33 | -1 | search 4.67 | D4 | 0 | no | [preview](cam_r_L0_kitchen_1_final_preview.jpg) [plan](cam_r_L0_kitchen_1_plan.jpg) |
| cam_r_L0_kitchen_2 | r_L0_kitchen | L0 | cycles | gate_validation | - | - | ok | - | - | +4.50 | -1 | search 4.54 | D4 | 0 | no | [preview](cam_r_L0_kitchen_2_final_preview.jpg) [plan](cam_r_L0_kitchen_2_plan.jpg) |
| cam_r_L0_kitchen_3 | r_L0_kitchen | L0 | cycles | gate_validation | - | - | ok | - | - | +4.17 | -1 | search 3.98 | D5 | 0 | no | [preview](cam_r_L0_kitchen_3_final_preview.jpg) [plan](cam_r_L0_kitchen_3_plan.jpg) |
| cam_r_L0_room_1 | r_L0_room | L0 | cycles | gate_validation | - | - | info | - | - | +0.00 | - | search 4.19 | D2 | 0 | no | [preview](cam_r_L0_room_1_final_preview.jpg) [plan](cam_r_L0_room_1_plan.jpg) |
| cam_r_L0_room_2 | r_L0_room | L0 | cycles | gate_validation | - | - | ok | - | - | -0.17 | - | search 3.92 | D2 | 0 | no | [preview](cam_r_L0_room_2_final_preview.jpg) [plan](cam_r_L0_room_2_plan.jpg) |
| cam_r_L0_room_3 | r_L0_room | L0 | cycles | gate_validation | - | - | info | - | - | -0.50 | - | search 3.61 | D3 | 0 | no | [preview](cam_r_L0_room_3_final_preview.jpg) [plan](cam_r_L0_room_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_bath_toilet | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_bath_toilet_1, cam_r_L0_bath_toilet_2 |
| r_L0_bed_room | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_bed_room_1, cam_r_L0_bed_room_2, cam_r_L0_bed_room_3 |
| r_L0_bed_room_2 | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_bed_room_2_1, cam_r_L0_bed_room_2_2, cam_r_L0_bed_room_2_3 |
| r_L0_dining | dining | L0 | 3 | 0 | 3 | cam_r_L0_dining_1, cam_r_L0_dining_2, cam_r_L0_dining_3 |
| r_L0_drawing_room | living | L0 | 3 | 0 | 3 | cam_r_L0_drawing_room_1, cam_r_L0_drawing_room_2, cam_r_L0_drawing_room_3 |
| r_L0_kitchen | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_kitchen_1, cam_r_L0_kitchen_2, cam_r_L0_kitchen_3 |
| r_L0_pooja | prayer | L0 | 0 | 0 | 0 | - |
| r_L0_room | hall | L0 | 3 | 0 | 3 | cam_r_L0_room_1, cam_r_L0_room_2, cam_r_L0_room_3 |
| r_L0_store | storage | L0 | 0 | 0 | 0 | - |

Rooms without a rendered view: r_L0_pooja, r_L0_store.

### Why Cycles

- cam_r_L0_bath_toilet_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bath_toilet_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bed_room_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bed_room_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bed_room_2_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bed_room_2_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bed_room_2_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_bed_room_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_dining_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_dining_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_dining_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_drawing_room_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_drawing_room_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_drawing_room_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_kitchen_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_kitchen_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_kitchen_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_room_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_room_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_room_3: gate_validation: gate validation polish_disabled: no polish for this project

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_2 | cycles | disputed | f_L0_022 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_bed_room_2_1 | cycles | disputed | dec_L0_015 | rug | optional | added_by_ai | building.json ai 0.90; building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- r_L0_room
- f_L0_018

Unverified pieces in view:

- cam_r_L0_drawing_room_1: f_L0_018
- cam_r_L0_drawing_room_2: f_L0_018
- cam_r_L0_drawing_room_3: f_L0_018

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_018 | f_L0_018: sym_L0_015: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) wardrobe, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_front_disagreement | f_L0_004 | f_L0_004: sym_L0_001: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_003 | symbol_front_disagreement | f_L0_007 | f_L0_007: sym_L0_004: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_004 | symbol_front_disagreement | f_L0_011 | f_L0_011: sym_L0_008: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_005 | symbol_front_disagreement | f_L0_012 | f_L0_012: sym_L0_009: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_006 | symbol_front_disagreement | f_L0_013 | f_L0_013: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_007 | symbol_front_disagreement | f_L0_014 | f_L0_014: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_008 | symbol_front_disagreement | f_L0_015 | f_L0_015: sym_L0_012: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_009 | symbol_front_disagreement | f_L0_016 | f_L0_016: sym_L0_013: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_010 | symbol_front_disagreement | f_L0_017 | f_L0_017: sym_L0_014: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |

## Units

Project unit system: **imperial** (lengths in feet and inches, metres in brackets).

| document | unit system | source kind |
|---|---|---|
| real01.pdf | imperial | cad_pdf |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 16, none 1, rule 3. Recognition questions: 17; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_004 | r_L0_bed_room_2 | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front top 1.00 |
| f_L0_005 | r_L0_bed_room_2 | nightstand | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: nightstand, front right 0.90 |
| f_L0_006 | r_L0_bed_room_2 | nightstand | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: nightstand, front left 0.90 |
| f_L0_007 | r_L0_bed_room | bed_double | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: bed_double, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front top 0.90 |
| f_L0_008 | r_L0_bed_room | nightstand | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: nightstand, front left 0.90 |
| f_L0_009 | r_L0_bed_room | nightstand | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: nightstand, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: nightstand, front right 0.90 |
| f_L0_010 | r_L0_dining | table_dining | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_dining, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_dining 0.90 |
| f_L0_011 | r_L0_dining | chair | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: chair, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front top 0.90 |
| f_L0_012 | r_L0_dining | chair | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: chair, front top 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front top 0.90 |
| f_L0_013 | r_L0_dining | chair | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: chair, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front left 0.90 |
| f_L0_014 | r_L0_dining | chair | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: chair, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front left 1.00 |
| f_L0_015 | r_L0_dining | chair | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: chair, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L0_016 | r_L0_dining | chair | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: chair, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: chair, front right 0.90 |
| f_L0_017 | r_L0_drawing_room | sofa | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 1.00 |
| f_L0_018 | r_L0_drawing_room | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wardrobe, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: sofa, front left 1.00 |
| f_L0_019 | r_L0_drawing_room | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee 0.80 |
| f_L0_020 | r_L0_drawing_room | floor_lamp | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: floor_lamp 0.95; pass 2 zai-org/GLM-4.6V-Flash: floor_lamp 0.90 |

## Site

Recorded, not built.

| id | what | detail |
|---|---|---|
| sw_L0_001 | boundary wall (plot) | 50' 0" (15.24 m) long, 0' 6" (0.15 m) thick |
| sw_L0_002 | boundary wall (plot) | 50' 0" (15.24 m) long, 0' 6" (0.15 m) thick |
| sw_L0_003 | boundary wall (plot) | 29' 0" (8.85 m) long, 0' 6" (0.15 m) thick |
| sw_L0_004 | boundary wall (plot) | 17' 9" (5.41 m) long, 0' 6" (0.15 m) thick |
| sa_L0_parking | area 'Parking' | label size 11' 3" x 15' 3", measured 15' 6" (4.72 m) x 11' 3" (3.43 m) (unchecked), no closed outline |
| - | decor | other x 1, plant x 9 |

## Separators

Virtual lines that split an open-plan face where two room names share it (no geometry is built; the pipeline's report.md lists the candidates it dropped):

| id | level | length | status | reason |
|---|---|---|---|---|
| o_L0_004 | L0 | 4' 3" (1.29 m) | verified | virtual separator (end-to-wall, 1.29 m): two room names shared one face |

## Assumed values

- style: default text "Scandinavian, light oak floor, white walls, linen textiles, warm daylight" (no style in brief.yaml; wenart/defaults.yaml)
- brief empty_rooms: ai (default, not in brief.yaml)
- brief decor: True (default, not in brief.yaml)
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- brief render.lens_mm: auto (default, not in brief.yaml)
- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 8' 10" (2.70 m) (assumed_default)
- door height 6' 11" (2.10 m): 5 opening(s) (d_L0_001, d_L0_002, d_L0_003, d_L0_004, d_L0_005)
- opening height 6' 11" (2.10 m): 3 opening(s) (o_L0_001, o_L0_002, o_L0_003)
- window height 3' 11" (1.20 m): 9 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- window sill height 2' 11" (0.90 m): 9 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- f_L0_003 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_bath_toilet: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_bath_toilet |
| area_light | 1 | r_L0_room: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_room |
| area_light | 1 | r_L0_store: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_store |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
| counter_fronts | 2 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_001, furn_f_L0_002 |
| direction | 1 | no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair | furn_f_L0_003 |
| door_handles | 5 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| handrail | 1 | design detail on every flight side not against a wall; not in the documents | furn_f_L0_003 |
| height | 5 | door height listed as assumed in the building JSON | d_L0_001, d_L0_002, d_L0_003 |
| height | 1 | no height in the JSON; proxy table value for unknown | proxy_f_L0_018 |
| height | 2 | no height in the JSON; type height for bed_double | furn_f_L0_004, furn_f_L0_007 |
| height | 6 | no height in the JSON; type height for chair | furn_f_L0_011, furn_f_L0_012, furn_f_L0_013 |
| height | 1 | no height in the JSON; type height for floor_lamp | furn_f_L0_020 |
| height | 2 | no height in the JSON; type height for kitchen_counter | furn_f_L0_001, furn_f_L0_002 |
| height | 4 | no height in the JSON; type height for nightstand | furn_f_L0_005, furn_f_L0_006, furn_f_L0_008 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L0_017 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L0_019 |
| height | 1 | no height in the JSON; type height for table_dining | furn_f_L0_010 |
| height | 3 | opening height listed as assumed in the building JSON | o_L0_001, o_L0_002, o_L0_003 |
| height | 9 | window height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| riser_m | 1 | derived from assumed ceiling and slab: 2.850 m / 16 drawn risers | furn_f_L0_003 |
| sill_height | 9 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| skirting | 7 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_bed_room, skirting_r_L0_drawing_room, skirting_r_L0_room |
| turn | 1 | flights side by side read as a turning stair, climbed in turn; nothing drawn says which flight starts at the floor | furn_f_L0_003 |
| void | 1 | nothing drawn above the stair; the opening is assumed; the floor above is not modelled, so the cap hides the shaft | f_L0_003_void |
| waist | 1 | the documents show the stair in plan only | furn_f_L0_003 |

## Rooms mixing polished and Cycles views

None.

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check qwen | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | check_manifest.json |
| check glm | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | check_manifest.json |
| detector | google/owlv2-base-patch16-ensemble | cfd3195ba4ea9592eec887ded089f4c08eff231d | Apache-2.0 | check_manifest.json |

Assets: textures CC0 x 5; furniture/decor models CC-BY-4.0 x 30, CC0 x 1, generated (TRELLIS.2-4B, MIT) x 5 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "low poly Lamp 3d model" by mohamedvfx (https://sketchfab.com/3d-models/53409613b45b42b98b979f12ab8faa12), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_020)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Stages

This run (`20261006-065742-full-20261006T070339Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | pending | 0.0 s | reused: 17 recognition question(s) written (recognition/requests.json) |
| recognize | reused | 1.9 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.2 s | - |
| pipeline_final | reused | 0.0 s | - |
| fit | ok | 1.9 s | - |
| decor_ask | reused | 0.0 s | - |
| layout | reused | 0.0 s | - |
| assets | ok | 0.9 s | - |
| decor | reused | 0.0 s | - |
| refit | ok | 2.3 s | - |
| build | ok | 62.2 s | - |
| render | ok | 112.8 s | - |
| export | ok | 33.9 s | - |
| controls | ok | 44.9 s | - |
| detect | skipped | 0.0 s | gate not validated |
| gate | ok | 61.3 s | gate decision polish_disabled |
| polish | skipped | 0.0 s | gate not validated |
| expected | ok | 12.6 s | - |
| check | ok | 76.4 s | - |
| combine | ok | 15.4 s | - |

The report stage itself is recorded after this report.

## Warnings

- no brief.yaml in /workspace/repo/projects/real01: every brief value is a default
- polish/polish_manifest.json not used: the gate validation says polish_disabled (no polish for this project; the manifest is from an earlier polish run)
- final/contact_sbs_r_L0_bath_toilet.jpg is from an earlier run (not part of this report)
- final/contact_sbs_r_L0_bed_room.jpg is from an earlier run (not part of this report)
- final/contact_sbs_r_L0_bed_room_2.jpg is from an earlier run (not part of this report)
- final/contact_sbs_r_L0_dining.jpg is from an earlier run (not part of this report)
- final/contact_sbs_r_L0_drawing_room.jpg is from an earlier run (not part of this report)
- final/contact_sbs_r_L0_kitchen.jpg is from an earlier run (not part of this report)
- final/contact_sbs_r_L0_room.jpg is from an earlier run (not part of this report)
