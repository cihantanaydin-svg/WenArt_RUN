# Final report: synthetic-02

11 views: 0 polished, 11 Cycles (gate_validation 11). Stages: render run, gate validation polish_disabled, polish not_run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 11 |
| polished | 0 |
| Cycles | 11 (gate_validation 11) |
| confirmed mismatches on the final image | 1 in 1 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 18 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 7 |
| exposure | -0.50 .. +4.50 EV (0 at a limit), modes auto |
| window pull | 9 view(s), -1 .. 0 EV |
| camera policy | search 11 |
| camera score (min / mean / max) | 1.13 / 3.19 / 3.96 |
| rooms by number of views | 2 with 1, 3 with 3 |
| gate validation | polish_disabled |
| seconds: build / render / metering | 8.1 s / 31.1 s / 2.8 s |
| seconds: polish / gate / check | - / - / 2.1 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check advisory: removal_flagged 0.6667 misses >= 0.8; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.667 (needs >= 0.8)
- check target missed: insertion 0.000 (needs >= 0.6)
- gate validation polish_disabled: no polish for this project: every final image is the Cycles render (negative controls rejected 0.828 < 0.90 (58 comparisons): the gate lets geometry changes through)
- camera cam_r_L0_banyo_1: no free camera point in the room; room's inner point inside a tall proxy, camera at the nearest point clear of tall proxies
- 8 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L0_001, f_L0_002, f_L0_004, f_L0_005, f_L0_007, f_L0_012, f_L0_013, f_L0_015

## Gate validation

| item | value |
|---|---|
| decision | polish_disabled |
| benign controls accepted | 100.0 % (limit 95 %), 40 comparisons |
| negative controls rejected | 82.8 % (limit 90 %), 58 comparisons |
| effect | no polish for this project: every final image is the Cycles render |

Reasons:

- negative controls rejected 0.828 < 0.90 (58 comparisons): the gate lets geometry changes through

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Side-by-side sheets (Cycles | polished)

None: gate validation polish_disabled: no polish for this project.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_antre_1 | r_L0_antre | L0 | cycles | gate_validation | - | - | ok | - | - | -0.50 | - | search 1.48 | D2 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | gate_validation | - | - | info | - | - | +4.00 | -1 | search 1.13 | D3 | 1 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | gate_validation | - | - | ok | - | - | +4.33 | -1 | search 3.69 | D4 | 2 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | gate_validation | - | - | info | - | - | +4.50 | -1 | search 3.62 | D5 | 2 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | gate_validation | - | - | ok | - | - | +4.17 | -1 | search 3.57 | D4 | 2 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | gate_validation | - | - | ok | - | - | +3.50 | -1 | search 3.61 | D5 | 3 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | cycles | gate_validation | - | - | ok | - | - | +3.17 | -1 | search 3.57 | D4 | 2 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | cycles | gate_validation | - | - | ok | - | - | +3.50 | -1 | search 3.29 | D5 | 2 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | gate_validation | - | - | mismatch (1) | - | - | +4.33 | -1 | search 3.96 | D4 | 2 | yes | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | gate_validation | - | - | ok | - | - | +4.50 | 0 | search 3.77 | D4 | 1 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | gate_validation | - | - | ok | - | - | +4.33 | - | search 3.35 | D3 | 1 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_antre | hall | L0 | 1 | 0 | 1 | cam_r_L0_antre_1 |
| r_L0_banyo | bathroom | L0 | 1 | 0 | 1 | cam_r_L0_banyo_1 |
| r_L0_mutfak | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 0 | 3 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |

### Why Cycles

- cam_r_L0_antre_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_banyo_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_mutfak_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_mutfak_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_mutfak_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_salon_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_salon_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_salon_3: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_yatak_odasi_1: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_yatak_odasi_2: gate_validation: gate validation polish_disabled: no polish for this project
- cam_r_L0_yatak_odasi_3: gate_validation: gate validation polish_disabled: no polish for this project

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | cycles | missing | f_L0_008 | shower | optional | from_documents | plan_scan.png p1 seg:50,seg:59,seg:70,seg:94 raster 0.70; plan_scan.png p1 recognition:sym_L0_008 ai 0.95; +1 more | info | - |
| cam_r_L0_yatak_odasi_1 | cycles | disputed | f_L0_007 | unknown | optional | from_documents | plan_scan.png p1 seg:182-184,seg:205,seg:207 raster 0.70; plan_scan.png p1 recognition:sym_L0_007 ai 0.95; +2 more | info | - |
| cam_r_L0_yatak_odasi_1 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |

## Needs review

- cam_r_L0_yatak_odasi_1: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- f_L0_001
- f_L0_002
- f_L0_004
- f_L0_005
- f_L0_007
- f_L0_009
- f_L0_012
- f_L0_013
- f_L0_014
- f_L0_015

Unverified pieces in view:

- cam_r_L0_banyo_1: f_L0_013
- cam_r_L0_mutfak_1: f_L0_004, f_L0_012
- cam_r_L0_mutfak_2: f_L0_004, f_L0_012
- cam_r_L0_mutfak_3: f_L0_004, f_L0_012
- cam_r_L0_salon_1: f_L0_002, f_L0_005, f_L0_009
- cam_r_L0_salon_2: f_L0_002, f_L0_009
- cam_r_L0_salon_3: f_L0_005, f_L0_009
- cam_r_L0_yatak_odasi_1: f_L0_001, f_L0_007
- cam_r_L0_yatak_odasi_2: f_L0_001
- cam_r_L0_yatak_odasi_3: f_L0_001

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_001 | f_L0_001: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bed_double | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_type_disagreement | f_L0_002 | f_L0_002: sym_L0_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) kitchen_counter | unresolved: the drawn footprint is kept as unknown, unverified |
| c_003 | symbol_type_disagreement | f_L0_004 | f_L0_004: sym_L0_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sofa, pass 2 (zai-org/GLM-4.6V-Flash) table_dining | unresolved: the drawn footprint is kept as unknown, unverified |
| c_004 | symbol_type_disagreement | f_L0_005 | f_L0_005: sym_L0_005: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sofa, pass 2 (zai-org/GLM-4.6V-Flash) table_dining | unresolved: the drawn footprint is kept as unknown, unverified |
| c_005 | symbol_type_disagreement | f_L0_007 | f_L0_007: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) wardrobe | unresolved: the drawn footprint is kept as unknown, unverified |
| c_006 | symbol_type_disagreement | f_L0_012 | f_L0_012: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) fridge, pass 2 (zai-org/GLM-4.6V-Flash) unknown | unresolved: the drawn footprint is kept as unknown, unverified |
| c_007 | symbol_type_disagreement | f_L0_013 | f_L0_013: sym_L0_013: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) side_table, pass 2 (zai-org/GLM-4.6V-Flash) fridge | unresolved: the drawn footprint is kept as unknown, unverified |
| c_008 | symbol_type_disagreement | f_L0_015 | f_L0_015: sym_L0_015: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) stove | unresolved: the drawn footprint is kept as unknown, unverified |
| c_009 | raster_count_mismatch | win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006, win_L0_007 | Zemin Kat: plan_scan.png has 7 windows, the photo plan_photo.jpg shows 5 (more than 1 apart) | scan wins; the photo is evidence only |
| c_010 | symbol_front_disagreement | f_L0_004 | f_L0_004: sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_011 | symbol_front_disagreement | f_L0_012 | f_L0_012: sym_L0_012: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| plan_photo.jpg | metric | raster_photo |
| plan_scan.png | metric | raster_scan |

## Recognition (AI typing and raster labels)

Furniture type methods: ai_two_pass 7, none 9. Recognition questions: 21; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_yatak_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: bed_double, front bottom 0.90 |
| f_L0_002 | r_L0_salon | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown, front left 0.85; pass 2 zai-org/GLM-4.6V-Flash: kitchen_counter, front left 0.80 |
| f_L0_003 | r_L0_mutfak | kitchen_counter | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: kitchen_counter, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: kitchen_counter, front top 0.90 |
| f_L0_004 | r_L0_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_dining, front bottom 0.80 |
| f_L0_005 | r_L0_salon | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: sofa, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_dining, front bottom 0.80 |
| f_L0_006 | r_L0_yatak_odasi | wardrobe | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: wardrobe, front right 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front right 0.90 |
| f_L0_007 | r_L0_yatak_odasi | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: desk, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: wardrobe, front right 0.90 |
| f_L0_008 | r_L0_banyo | shower | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: shower, front bottom 0.90 |
| f_L0_009 | r_L0_salon | fridge | yes | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: fridge, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: fridge, front left 0.90 |
| f_L0_010 | r_L0_banyo | shower | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: shower, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: shower 0.90 |
| f_L0_011 | r_L0_salon | table_coffee | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: table_coffee, front bottom 0.95; pass 2 zai-org/GLM-4.6V-Flash: table_coffee, front bottom 0.80 |
| f_L0_012 | r_L0_mutfak | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: fridge, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: unknown 0.60 |
| f_L0_013 | r_L0_banyo | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: side_table 0.95; pass 2 zai-org/GLM-4.6V-Flash: fridge, front right 0.90 |
| f_L0_014 | r_L0_antre | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: not_furniture, front left 0.99; pass 2 zai-org/GLM-4.6V-Flash: not_furniture 0.90 |
| f_L0_015 | r_L0_banyo | unknown | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.95; pass 2 zai-org/GLM-4.6V-Flash: stove, front right 0.80 |
| f_L0_016 | r_L0_banyo | washbasin | yes | verified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: washbasin, front left 0.95; pass 2 zai-org/GLM-4.6V-Flash: washbasin, front left 0.80 |

Raster pages (scans and photos):

| file | page | kind | class | level | rectified image | skip reason |
|---|---|---|---|---|---|---|
| plan_photo.jpg | 1 | photo | floor_plan | L0 | rectified/plan_photo_jpg_p1.png | - |
| plan_scan.png | 1 | scan | floor_plan | L0 | rectified/plan_scan_png_p1.png | - |

Room labels of the raster pages and how they were accepted (§3.4):

| room | label | as read | type | status | accepted by |
|---|---|---|---|---|---|
| r_L0_salon | Salon | SALON | living | verified | two passes agree |
| r_L0_yatak_odasi | Yatak Odası | YATAK ODASI | bedroom | verified | two passes agree |
| r_L0_mutfak | Mutfak | MUTFAK | kitchen | verified | two passes agree |
| r_L0_antre | Antre | ANTRE | hall | verified | two passes agree |
| r_L0_banyo | Banyo | BANYO | bathroom | verified | two passes agree |

## Site

Recorded, not built.

None.

## Separators

None.

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
- L0: ceiling height 2,70 m (assumed_default)
- plan_photo.jpg p1: photo aspect assumed: snapped to the ISO (sqrt 2) sheet ratio 1.41421 (measured 1.37642, 2.67 % off)
- door height 2,10 m: 4 opening(s) (d_L0_001, d_L0_002, d_L0_003, d_L0_004)
- window height 1,20 m: 7 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)
- window sill height 0,90 m: 7 opening(s) (win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006 ...)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_antre: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_antre |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
| counter_fronts | 1 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_003 |
| door_handles | 4 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| height | 4 | door height listed as assumed in the building JSON | d_L0_001, d_L0_002, d_L0_003 |
| height | 8 | no height in the JSON; proxy table value for unknown | proxy_f_L0_001, proxy_f_L0_002, proxy_f_L0_004 |
| height | 1 | no height in the JSON; type height for fridge | furn_f_L0_009 |
| height | 1 | no height in the JSON; type height for kitchen_counter | furn_f_L0_003 |
| height | 2 | no height in the JSON; type height for shower | furn_f_L0_008, furn_f_L0_010 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L0_011 |
| height | 1 | no height in the JSON; type height for wardrobe | furn_f_L0_006 |
| height | 1 | no height in the JSON; type height for washbasin | furn_f_L0_016 |
| height | 7 | window height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| height_lift | 1 | footprint overlaps another piece of the same height; lifted so the top faces do not coincide | proxy_f_L0_015 |
| sill_height | 7 | window sill_height listed as assumed in the building JSON | win_L0_001, win_L0_002, win_L0_003 |
| skirting | 3 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_salon, skirting_r_L0_yatak_odasi, skirting_r_L0_antre |

## Rooms mixing polished and Cycles views

None.

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check qwen | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | check_manifest.json |
| check glm | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | check_manifest.json |

Assets: textures CC0 x 4; furniture/decor models - (parametric meshes need no licence).

## Attribution

No CC BY or Objaverse model in this project (Poly Haven CC0 models and parametric meshes need no credit).

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261004-000052-full-20261004T000516Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | pending | 60.4 s | 21 recognition question(s) written (recognition/requests.json) |
| recognize | reused | 1.9 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.2 s | - |
| pipeline_final | ok | 51.9 s | answers applied |
| fit | ok | 1.2 s | - |
| layout | skipped | 0.0 s | no empty room |
| assets | ok | 0.5 s | - |
| decor | ok | 1.7 s | - |
| refit | ok | 1.0 s | - |
| build | ok | 13.2 s | - |
| render | ok | 80.3 s | - |
| controls | ok | 39.0 s | - |
| detect | skipped | 0.0 s | gate not validated |
| gate | ok | 41.2 s | gate decision polish_disabled |
| polish | skipped | 0.0 s | gate not validated |
| expected | ok | 12.0 s | - |
| check | ok | 50.1 s | - |
| combine | ok | 103.4 s | - |

The report stage itself is recorded after this report.

## Warnings

- no brief.yaml in /workspace/repo/projects/synthetic-02: every brief value is a default
