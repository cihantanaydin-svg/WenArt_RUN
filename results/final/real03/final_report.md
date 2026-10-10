# Final report: real03

14 views: 0 polished, 14 Cycles (not_run 14). Stages: render run, gate validation not_run, polish not_run, vision check single_pass (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 14 |
| interior / exterior views | 14 / 0 |
| variant | base |
| polished | 0 |
| Cycles | 14 (not_run 14) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 6 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 9 |
| exposure | -1.00 .. +0.50 EV (0 at a limit), modes auto |
| window pull | - |
| camera policy | search 14 |
| camera score (min / mean / max) | 0.35 / 3.26 / 4.74 |
| rooms by number of views | 1 with 2, 4 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 53.8 s / 39.1 s / 5.2 s |
| seconds: polish / gate / check | - / - / 3.1 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 0 |

## 3D files

Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.

| file | size |
|---|---|
| [real03.blend](3d/real03.blend) | 100.8 MB |
| [real03.glb](3d/real03.glb) | 225.9 MB |

14 cameras; textures scaled to at most 1024 px (50 scaled) for the download.

## AI decor

14 decor items chosen by the AI (Qwen/Qwen3-VL-8B-Instruct; both passes agreeing) in 5 rooms; 0 items by the rules. The decor stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished rooms has its own section, `AI completion of furnished rooms`; `furniture/<project>/decor_report.md` has every room).

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check single pass: every result unverified (advisory)
- vision check advisory: single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)
- check target missed: fa_missing - (needs <= 0.05), single pass
- check target missed: fa_extra - (needs <= 0.1), single pass
- check target missed: removal_flagged - (needs >= 0.8), single pass
- check target missed: removal_confirmed - (needs >= 0.6), single pass
- check target missed: insertion - (needs >= 0.6), single pass
- 2 drawn piece(s) not typed: the two AI passes disagree or did not answer (unknown, unverified; footprint kept): f_L0_001, f_L0_002

## Gate validation

Not recorded: the gate calibration and validation did not run.

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Side-by-side sheets (Cycles | polished)

None: the polish did not run in this run.

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_guvenlik_holu_1 | r_L0_guvenlik_holu | L0 | cycles | not_run | - | - | info | - | - | +0.50 | - | search 0.39 | A3 | 0 | no | [preview](cam_r_L0_guvenlik_holu_1_final_preview.jpg) [plan](cam_r_L0_guvenlik_holu_1_plan.jpg) |
| cam_r_L0_guvenlik_holu_2 | r_L0_guvenlik_holu | L0 | cycles | not_run | - | - | info | - | - | +0.33 | - | search 0.35 | A3 | 0 | no | [preview](cam_r_L0_guvenlik_holu_2_final_preview.jpg) [plan](cam_r_L0_guvenlik_holu_2_plan.jpg) |
| cam_r_L0_kat_holu_1 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 3.82 | D2 A1 | 0 | no | [preview](cam_r_L0_kat_holu_1_final_preview.jpg) [plan](cam_r_L0_kat_holu_1_plan.jpg) |
| cam_r_L0_kat_holu_2 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 3.73 | D1 A1 | 0 | no | [preview](cam_r_L0_kat_holu_2_final_preview.jpg) [plan](cam_r_L0_kat_holu_2_plan.jpg) |
| cam_r_L0_kat_holu_3 | r_L0_kat_holu | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 3.30 | D2 A1 | 0 | no | [preview](cam_r_L0_kat_holu_3_final_preview.jpg) [plan](cam_r_L0_kat_holu_3_plan.jpg) |
| cam_r_L0_kat_merdiveni_1 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 4.74 | D1 A2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_1_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_1_plan.jpg) |
| cam_r_L0_kat_merdiveni_2 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 4.73 | D1 A2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_2_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_2_plan.jpg) |
| cam_r_L0_kat_merdiveni_3 | r_L0_kat_merdiveni | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 3.98 | D1 A2 | 1 | no | [preview](cam_r_L0_kat_merdiveni_3_final_preview.jpg) [plan](cam_r_L0_kat_merdiveni_3_plan.jpg) |
| cam_r_L0_ruzgarlik_1 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 4.20 | D2 A2 | 0 | no | [preview](cam_r_L0_ruzgarlik_1_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_1_plan.jpg) |
| cam_r_L0_ruzgarlik_2 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 4.02 | D3 A2 | 0 | no | [preview](cam_r_L0_ruzgarlik_2_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_2_plan.jpg) |
| cam_r_L0_ruzgarlik_3 | r_L0_ruzgarlik | L0 | cycles | not_run | - | - | info | - | - | -0.50 | - | search 3.99 | D1 A2 | 0 | no | [preview](cam_r_L0_ruzgarlik_3_final_preview.jpg) [plan](cam_r_L0_ruzgarlik_3_plan.jpg) |
| cam_r_L0_yangin_merdiveni_1 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | -0.83 | - | search 3.30 | D1 A5 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_1_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_1_plan.jpg) |
| cam_r_L0_yangin_merdiveni_2 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | -0.67 | - | search 2.55 | D1 A5 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_2_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_2_plan.jpg) |
| cam_r_L0_yangin_merdiveni_3 | r_L0_yangin_merdiveni | L0 | cycles | not_run | - | - | info | - | - | -1.00 | - | search 2.53 | D1 A5 | 1 | no | [preview](cam_r_L0_yangin_merdiveni_3_final_preview.jpg) [plan](cam_r_L0_yangin_merdiveni_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_guvenlik_holu | hall | L0 | 2 | 0 | 2 | cam_r_L0_guvenlik_holu_1, cam_r_L0_guvenlik_holu_2 |
| r_L0_kat_holu | hall | L0 | 3 | 0 | 3 | cam_r_L0_kat_holu_1, cam_r_L0_kat_holu_2, cam_r_L0_kat_holu_3 |
| r_L0_kat_merdiveni | other | L0 | 3 | 0 | 3 | cam_r_L0_kat_merdiveni_1, cam_r_L0_kat_merdiveni_2, cam_r_L0_kat_merdiveni_3 |
| r_L0_ruzgarlik | other | L0 | 3 | 0 | 3 | cam_r_L0_ruzgarlik_1, cam_r_L0_ruzgarlik_2, cam_r_L0_ruzgarlik_3 |
| r_L0_yangin_merdiveni | other | L0 | 3 | 0 | 3 | cam_r_L0_yangin_merdiveni_1, cam_r_L0_yangin_merdiveni_2, cam_r_L0_yangin_merdiveni_3 |

### Why Cycles

- cam_r_L0_guvenlik_holu_1: not_run: polish not run
- cam_r_L0_guvenlik_holu_2: not_run: polish not run
- cam_r_L0_kat_holu_1: not_run: polish not run
- cam_r_L0_kat_holu_2: not_run: polish not run
- cam_r_L0_kat_holu_3: not_run: polish not run
- cam_r_L0_kat_merdiveni_1: not_run: polish not run
- cam_r_L0_kat_merdiveni_2: not_run: polish not run
- cam_r_L0_kat_merdiveni_3: not_run: polish not run
- cam_r_L0_ruzgarlik_1: not_run: polish not run
- cam_r_L0_ruzgarlik_2: not_run: polish not run
- cam_r_L0_ruzgarlik_3: not_run: polish not run
- cam_r_L0_yangin_merdiveni_1: not_run: polish not run
- cam_r_L0_yangin_merdiveni_2: not_run: polish not run
- cam_r_L0_yangin_merdiveni_3: not_run: polish not run

## Mismatches (never auto-fixed)

None.

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

- w_L0_001
- w_L0_002
- w_L0_003
- w_L0_004
- w_L0_005
- w_L0_006
- w_L0_007
- w_L0_008
- w_L0_009
- w_L0_010
- w_L0_011
- w_L0_012
- w_L0_013
- w_L0_014
- w_L0_015
- w_L0_016
- w_L0_017
- w_L0_018
- w_L0_019
- w_L0_020
- w_L0_021
- w_L0_022
- w_L0_023
- w_L0_024
- w_L0_025
- w_L0_026
- w_L0_027
- w_L0_028
- w_L0_029
- w_L0_030
- f_L0_001
- f_L0_002
- f_L0_003

Unverified pieces in view:

- cam_r_L0_kat_merdiveni_1: f_L0_002
- cam_r_L0_kat_merdiveni_2: f_L0_002
- cam_r_L0_kat_merdiveni_3: f_L0_002
- cam_r_L0_yangin_merdiveni_1: f_L0_001
- cam_r_L0_yangin_merdiveni_2: f_L0_001
- cam_r_L0_yangin_merdiveni_3: f_L0_001

Conflicts:

| id | kind | elements | description | resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_001 | f_L0_001: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) kitchen_counter | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_type_disagreement | f_L0_002 | f_L0_002: sym_L0_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) kitchen_island | unresolved: the drawn footprint is kept as unknown, unverified |
| c_003 | symbol_type_disagreement | f_L0_003 | f_L0_003: sym_L0_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) console_table | unresolved: the drawn footprint is kept as unknown, unverified |

## Sheets

The sheets stage split every sheet into drawing regions and classified them before any wall was read. 1 regions (use: read 1). A region is read only when its class says it is a plan; everything else is ignored with its reason, never guessed.

Full analysis: [sheets_report.md](sheets_report.md).

Regions:

| region | file | class | decided by | status | level | variant | use |
|---|---|---|---|---|---|---|---|
| r1 | tekkat.dwg | floor_plan | title (0.99) | verified | L0 | base | read |

Levels and their alternative plans (a variant group):

| level | label | kind | base region | alternatives |
|---|---|---|---|---|
| L0 | Zemin Kat | floor | r1 | - |

Variants (the base building and one per alternative plan):

| variant | label | levels | regions |
|---|---|---|---|
| base | Base | L0 | r1 |

Strays (entities far from every drawing, ignored): 0.

Unit check (the drawing unit against the room-area labels, the level marks and the door widths):

| file | format | metres per unit | method | checks | conflict |
|---|---|---|---|---|---|
| tekkat.dwg | dwg | 0.01 | dxf_insunits | area_labels cm 0.83 (6); level_marks None - (0); door_widths cm 1.00 (4); wall_thickness None 0.46 (78); text_height None - (46); dimensions None - (0) | - |

Debug images (every region boxed and labelled with class, level and variant):

- [debug/tekkat_dwg_s1.jpg](debug/tekkat_dwg_s1.jpg)

## AI completion of furnished rooms (Feature 1)

Mode `furnished_rooms: complete` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (+-5 cm) and front (+-1 deg); the AI may change a piece's type (within the room type's types), size, height and look (it stays `from_documents`, `modified_by_ai`, with the drawn type and size recorded) and add the pieces the room type misses (`added_by_ai`, never a second main piece). Fixed equipment never changes. A change needs both AI passes.

0 change(s) applied, 8 piece(s) added, 0 wall cabinet run(s).

### Kat Holü (r_L0_kat_holu, hall): completed

- added f_L0_010: console_table 1.20 x 0.35 (confidence 0.90, ai)

### Yangın Merdiveni (r_L0_yangin_merdiveni, other): completed

- added f_L0_011: armchair 0.90 x 0.90 (confidence 0.60, ai)
- added f_L0_012: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L0_013: table_dining 1.20 x 0.80 (confidence 0.60, ai)
- added f_L0_014: bookshelf 1.00 x 0.35 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_001

### Kat Merdiveni (r_L0_kat_merdiveni, other): completed

- added f_L0_015: armchair 0.90 x 0.90 (confidence 0.60, ai)
- added f_L0_016: chair 0.50 x 0.50 (confidence 0.60, ai)
- added f_L0_017: table_dining 1.60 x 0.90 (confidence 0.60, ai)
- drawn pieces that already fail a placer check as drawn (kept, never moved): f_L0_002

### Drawn pieces against the source plan

Reference: source building.json; mode `complete`. 3 of 3 drawn piece(s) checked: anchor within 0.05 m, front within 1.0 deg, the same wall; 3 ok, 0 failed; 0 changed by the AI.

## Units

Project unit system: **metric**.

| document | unit system | source kind |
|---|---|---|
| tekkat.dwg | metric | dxf |

## Recognition (AI typing and raster labels)

Furniture type methods: none 3. Recognition questions: 3; answer files: answers_glm-4.6v-flash.json, answers_qwen3-vl-8b.json. A type counts only when both passes agree and the drawn footprint fits the type's size range; otherwise the piece stays `unknown` and `unverified` with both answers.

AI-typed pieces:

| piece | room | type | agreed | status | built | answers |
|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_yangin_merdiveni | kitchen_counter | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: kitchen_counter, front left 0.90 |
| f_L0_002 | r_L0_kat_merdiveni | kitchen_island | no | unverified | yes | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.80; pass 2 zai-org/GLM-4.6V-Flash: kitchen_island 0.80 |
| f_L0_003 | r_L0_kat_holu | unknown | no | unverified | no (drawn symbol, not built) | pass 1 Qwen/Qwen3-VL-8B-Instruct: unknown 0.85; pass 2 zai-org/GLM-4.6V-Flash: console_table, front right 0.90 |

## Site

Recorded, not built.

| id | what | detail |
|---|---|---|
| - | decor | other x 16 |

## Separators

None.

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
- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2,70 m (assumed_default)
- door height 2,10 m: 4 opening(s) (d_L0_001, d_L0_002, d_L0_003, d_L0_004)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L0_guvenlik_holu: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_guvenlik_holu |
| area_light | 1 | r_L0_kat_holu: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_kat_holu |
| area_light | 1 | r_L0_kat_merdiveni: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_kat_merdiveni |
| area_light | 1 | r_L0_ruzgarlik: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_ruzgarlik |
| area_light | 1 | r_L0_yangin_merdiveni: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L0_yangin_merdiveni |
| ceiling_height | 1 | building JSON: assumed_default | level_L0 |
| counter_fronts | 2 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L0_001, furn_f_L0_002 |
| door_handles | 4 | design detail of the documented door (lever handles on both faces); not in the documents | d_L0_001_handle, d_L0_002_handle, d_L0_003_handle |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| height | 4 | door height listed as assumed in the building JSON | d_L0_001, d_L0_002, d_L0_003 |
| height | 1 | no height in the JSON; type height for kitchen_counter | furn_f_L0_001 |
| height | 1 | no height in the JSON; type height for kitchen_island | furn_f_L0_002 |
| skirting | 5 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L0_ruzgarlik, skirting_r_L0_kat_holu, skirting_r_L0_guvenlik_holu |

## Rooms mixing polished and Cycles views

None.

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check agent | Qwen/Qwen3.8-27B-FP8 | 017b9c7af6b5689d5dd426a76e0bc077eb5ca20a | Apache-2.0 | check_manifest.json |

Assets: textures CC0 x 4; furniture/decor models CC-BY-4.0 x 12, generated (TRELLIS.2-4B, MIT) x 9 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_012)
- "High Bookcase" by 8549 (https://sketchfab.com/3d-models/d48a42e91c5d4716a8c254addf8c9d99), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L0_005, f_L0_009)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Not run for this project (no `detect/` results in the check manifest).

## Stages

This run (`20261010-104048-full-20261010T104652Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| sheets | ok | 21.7 s | - |
| pipeline | pending | 44.1 s | 3 recognition question(s) written (recognition/requests.json) |
| style | ok | 0.3 s | - |
| recognize | ok | 7.5 s | - |
| pipeline_final | ok | 44.2 s | answers applied |
| fit | ok | 1.2 s | - |
| layout | ok | 28.0 s | - |
| decor_ask | ok | 29.4 s | - |
| photos | ok | 3.4 s | - |
| assets | ok | 1.4 s | - |
| decor | ok | 2.8 s | - |
| refit | ok | 10.3 s | - |
| build | ok | 4.5 min | - |
| agent_previews | ok | 72.6 s | 3 view(s) |
| agent_apply | ok | 6.5 s | - |
| agent | ok | 17.0 min | 4 round(s), 11 edit(s) accepted, 46 rejected; stop: no edit accepted in this round |
| render | ok | 72.5 s | - |
| export | ok | 19.6 s | - |
| controls | ok | 30.4 s | - |
| detect | skipped | 0.0 s | polish off |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 18.6 s | - |
| check | ok | 60.8 s | - |
| combine | ok | 10.5 s | - |

The report stage itself is recorded after this report.

## AI orchestrator

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`: 5 round(s), 11 edit(s) accepted, 46 rejected, 138 model calls (1138105 tokens), 18.3 min. Stop: final round for critical findings done. Every edit was checked by code before it was accepted; the full log is `orchestrator/log.md` on the volume.

### Rounds

| round | critical | major | minor | dropped (vision) | accepted | rejected | re-run from | views |
|---|---|---|---|---|---|---|---|---|
| 1 | 1 | 11 | 3 | 8 | 6 | 16 | refit | 9 |
| 2 | 2 | 9 | 2 | 3 | 4 | 11 | refit | 6 |
| 3 | 2 | 8 | 2 | 1 | 1 | 10 | refit | 3 |
| 4 | 2 | 6 | 2 | 2 | 0 | 9 | - | 0 |
| 5 | 2 | 6 | 2 | 0 | 0 | 0 | - | 0 |

### Findings by check

| check | critical | major | minor | dropped |
|---|---|---|---|---|
| F1 | 0 | 14 | 0 | 0 |
| F3 | 0 | 6 | 0 | 7 |
| F4 | 0 | 9 | 0 | 0 |
| F5 | 0 | 2 | 10 | 2 |
| F6 | 0 | 0 | 0 | 1 |
| F8 | 0 | 1 | 0 | 4 |
| F9 | 0 | 8 | 1 | 0 |
| R5 | 9 | 0 | 0 | 0 |

### Accepted edits

| # | round | tool | target | label | score | reason | before | after |
|---|---|---|---|---|---|---|---|---|
| 32 | 1 | move_piece | f_L0_010 | added_by_ai | 87.0 -> 97.0 | Snap the console table's back onto the south wall w_L0_005 to fix the 0.94 m off-wall violation. | ![](agent/r1_007_move_piece_before_r_L0_kat_holu.png) | ![](agent/r1_008_move_piece_after_r_L0_kat_holu.png) |
| 34 | 1 | remove_piece | f_L0_003 | adjusted_by_ai | 97.0 -> 100.0 | The 0.90×0.34 m box is a thin sliver inside the entry nook, not a plausible standalone furniture item; no plan crop exists to identify it, so it is removed as a drawing artifact. | ![](agent/r1_010_remove_piece_before_r_L0_kat_holu.png) | ![](agent/r1_011_remove_piece_after_r_L0_kat_holu.png) |
| 36 | 1 | remove_piece | f_L0_015 | added_by_ai | 70.0 -> 80.0 | AI-added armchair stands alone in a stair room with no sofa or wall seating context (F8); removing it leaves the dining set as the only furniture. | ![](agent/r1_014_remove_piece_before_r_L0_kat_merdiveni.png) | ![](agent/r1_015_remove_piece_after_r_L0_kat_merdiveni.png) |
| 38 | 1 | resize_piece | f_L0_017 | added_by_ai | 80.0 -> 80.0 | Vision found the dining table rendered ~1.2 m high like a bench; resizing to a standard 1.2×0.8 m dining table restores the correct proportions. | ![](agent/r1_017_resize_piece_before_r_L0_kat_merdiveni.png) | ![](agent/r1_018_resize_piece_after_r_L0_kat_merdiveni.png) |
| 48 | 1 | move_piece | f_L0_011 | added_by_ai | 77.0 -> 77.0 | Shift the armchair north to clear the counter, then it can face the table. | ![](agent/r1_029_move_piece_before_r_L0_yangin_merdiveni.png) | ![](agent/r1_030_move_piece_after_r_L0_yangin_merdiveni.png) |
| 49 | 1 | move_piece | f_L0_012 | added_by_ai | 77.0 -> 77.0 | Place the dining chair just south of the table's south edge so it can face the table. | ![](agent/r1_031_move_piece_before_r_L0_yangin_merdiveni.png) | ![](agent/r1_032_move_piece_after_r_L0_yangin_merdiveni.png) |
| 87 | 2 | remove_piece | f_L0_014 | added_by_ai | 77.0 -> 77.0 | Bookshelf is inappropriate in a fire escape/stairwell; it was AI-added to complete the room. | ![](agent/r2_008_remove_piece_before_r_L0_yangin_merdiveni.png) | ![](agent/r2_009_remove_piece_after_r_L0_yangin_merdiveni.png) |
| 88 | 2 | remove_piece | f_L0_011 | added_by_ai | 77.0 -> 77.0 | Armchair is inappropriate in a fire escape/stairwell; it was AI-added to complete the room. | ![](agent/r2_010_remove_piece_before_r_L0_yangin_merdiveni.png) | ![](agent/r2_011_remove_piece_after_r_L0_yangin_merdiveni.png) |
| 92 | 2 | move_piece | f_L0_012 | added_by_ai | 77.0 -> 77.0 | Keep chair adjacent to the dining table so the table is not left chairless while the stairwell furniture is being resolved. | ![](agent/r2_015_move_piece_before_r_L0_yangin_merdiveni.png) | ![](agent/r2_016_move_piece_after_r_L0_yangin_merdiveni.png) |
| 95 | 2 | remove_piece | f_L0_017 | added_by_ai | 80.0 -> 80.0 | The dining table was AI-added to a 14 m² stair room (Kat Merdiveni) where it does not belong; removing it also resolves the F5 'dining table without chairs' finding. | ![](agent/r2_020_remove_piece_before_r_L0_kat_merdiveni.png) | ![](agent/r2_021_remove_piece_after_r_L0_kat_merdiveni.png) |
| 130 | 3 | remove_piece | f_L0_016 | added_by_ai | 80.0 -> 90.0 | AI-added chair in a staircase/void room with no table or seating group; inappropriate fixture for this space. | ![](agent/r3_009_remove_piece_before_r_L0_kat_merdiveni.png) | ![](agent/r3_010_remove_piece_after_r_L0_kat_merdiveni.png) |

### Rejected edits

| # | round | tool | target | failed checks | reason |
|---|---|---|---|---|---|
| 33 | 1 | change_type | f_L0_003 | score: plausibility 97 -> 90 (F8 f_L0_003: bench stands alone in the room (no wall, no bed_double / bed_single / bunk_bed within 0.8 m)) | The 0.90×0.34 m drawn box in the entry nook matches a bench footprint, resolving the unexplained unknown box. |
| 35 | 1 | remove_piece | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment (kitchen_island) is never removed | Drawn box in a stair room (Kat Merdiveni) with no plan crop, no kitchen context and an unresolved symbol disagreement (unknown vs kitchen_island); a 2.6×0.55 m box is not a kitchen island here, so it is removed as a non-furniture drawing artifact. |
| 37 | 1 | change_type | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment keeps its type (kitchen_island) | The 2.6×0.55 m drawn box in the stair room is not a kitchen island (no kitchen context, unresolved symbol disagreement); a long low console table fits the footprint and the room type. |
| 39 | 1 | move_piece | f_L0_016 | f_L0_016: no_overlap, f_L0_017: no_overlap, score: plausibility 80 -> 77 (F4 f_L0_016: chair does not face its group (f_L0_017); F5 f_L0_017: dining table with 1 of 4 chairs) | Move the chair to the far side of the dining table so the table has chairs on both sides (F5). |
| 40 | 1 | rotate_piece | f_L0_016 | score: plausibility 80 -> 70 (F4 f_L0_016: chair faces a wall 0.05 m in front of it) | Face the chair towards the dining table after moving it to the far side. |
| 41 | 1 | move_piece | f_L0_016 | f_L0_016: no_overlap, f_L0_017: no_overlap, score: plausibility 80 -> 77 (F4 f_L0_016: chair does not face its group (f_L0_017); F5 f_L0_017: dining table with 1 of 4 chairs) | Place the chair on the far side of the dining table (table spans y 11.3–12.1) so the table has chairs on both sides (F5). |
| 42 | 1 | change_type | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment keeps its type (kitchen_counter) | The 2.6x0.55 m drawn box along the south wall of the fire-escape stair is a slim wall-hung console, not a kitchen counter (no kitchen fixtures, room is a stair enclosure). |
| 43 | 1 | rotate_piece | f_L0_011 | f_L0_011: clearance_ok, score: plausibility 77 -> 67 (F6 f_L0_011: armchair: the free zone in front of it is blocked by f_L0_013) | Turn the armchair away from the west wall so it faces the dining table and room center. |
| 44 | 1 | rotate_piece | f_L0_012 | score: plausibility 77 -> 67 (F4 f_L0_012: chair does not face its group (f_L0_013)) | Turn the dining chair to face the dining table instead of the east wall. |
| 45 | 1 | move_piece | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment (kitchen_counter) is never moved | Snap the drawn counter's back edge onto the south wall it is drawn against, closing the 0.13 m gap. |
| 46 | 1 | move_piece | f_L0_011 | f_L0_011: clearance_ok, score: plausibility 77 -> 67 (F6 f_L0_011: armchair: the free zone in front of it is blocked by f_L0_001) | Shift the armchair south to open a clear zone in front of it before turning it toward the table. |
| 47 | 1 | move_piece | f_L0_012 | f_L0_012: no_overlap, f_L0_013: no_overlap | Move the dining chair to the south side of the table so it can face the table. |
| 50 | 1 | rotate_piece | f_L0_004 | f_L0_004: clearance_ok, f_L0_004: inside_room, score: plausibility 97 -> 67 (F3 f_L0_004: desk: its back is not on a wall (0.02 m off); F6 f_L0_004: desk: the free zone in front of it is reaches out of the room; F9 f_L0_004: desk reaches 0.23 m² through the room outline) | Desk front currently faces the west wall; rotate so the front faces into the room (east) for a usable workspace. |
| 51 | 1 | move_piece | f_L0_004 | f_L0_004: doors_free, score: plausibility 97 -> 37 (F3 f_L0_004: desk: its back is not on a wall (0.22 m off); F6 f_L0_004: no 0.9 m walkway from d_L0_001 to d_L0_002 (blocked by f_L0_004); F6 f_L0_004: no 0.9 m walkway from d_L0_001 to d_L0_004 (blocked by f_L0_004); F6 f_L0_004: no 0.9 m walkway from d_L0_002 to d_L0_003 (blocked by f_L0_004)) | Shift desk east so its back edge sits on the west wall, keeping the front facing into the room. |
| 52 | 1 | move_piece | f_L0_004 | snap: f_L0_004: no free place on wall w_L0_003 (doors, windows) | Snap the desk back onto the north wall (d_L0_004 side) so its front faces into the room, away from the wall. |
| 53 | 1 | move_piece | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Snap the desk back onto the west wall so its front faces into the room (east), fixing the wall-facing orientation. |
| 86 | 2 | remove_piece | f_L0_013 | score: plausibility 77 -> 70 (F8 f_L0_012: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m)) | Dining table is inappropriate in a fire escape/stairwell; it was AI-added to complete the room. |
| 89 | 2 | remove_piece | f_L0_012 | score: plausibility 77 -> 60 (F5 f_L0_013: dining table without chairs; F8 f_L0_013: table_dining stands alone in the room (no wall, no chair / bench / bar_stool within 1.0 m)) | Chair is inappropriate in a fire escape/stairwell and faces away from the table; it was AI-added. |
| 90 | 2 | remove_piece | f_L0_013 | score: plausibility 77 -> 70 (F8 f_L0_012: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m)) | Dining table is inappropriate in a fire escape/stairwell; it was AI-added to complete the room. |
| 91 | 2 | remove_piece | f_L0_012 | score: plausibility 77 -> 60 (F5 f_L0_013: dining table without chairs; F8 f_L0_013: table_dining stands alone in the room (no wall, no chair / bench / bar_stool within 1.0 m)) | Chair is inappropriate in a fire escape/stairwell and faces away from the table; it was AI-added. |
| 93 | 2 | remove_piece | f_L0_013 | score: plausibility 77 -> 70 (F8 f_L0_012: chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m)) | Dining table is inappropriate in a fire escape/stairwell; it was AI-added to complete the room. |
| 94 | 2 | remove_piece | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment (kitchen_island) is never removed | The 2.6×0.55 m box spans the full width of the 2.6 m stair room at the bottom, matching the stair flight drawn in the plan (the room is Kat Merdiveni, a stair room); it is not a kitchen island and not furniture, so it is removed. |
| 96 | 2 | change_type | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment keeps its type (kitchen_island) | The 2.6×0.55 m box spans the full width of the 2.6 m stair room (Kat Merdiveni) at the bottom, matching the stair flight drawn in the plan; it is a stair, not a kitchen island, so the type is corrected. |
| 97 | 2 | rotate_piece | f_L0_004 | f_L0_004: clearance_ok, f_L0_004: inside_room, score: plausibility 97 -> 67 (F3 f_L0_004: desk: its back is not on a wall (0.02 m off); F6 f_L0_004: desk: the free zone in front of it is reaches out of the room; F9 f_L0_004: desk reaches 0.23 m² through the room outline) | Turn the desk so its front faces into the room (away from the west wall) instead of facing the wall. |
| 98 | 2 | move_piece | f_L0_004 | snap: f_L0_004: no free place on wall w_L0_022 (doors, windows) | Snap the desk's back edge onto the west wall so it sits flush against the wall. |
| 99 | 2 | move_piece | f_L0_004 | f_L0_004: doors_free, score: plausibility 97 -> 87 (F3 f_L0_004: desk: its back is not on a wall (0.17 m off)) | Shift the desk east so its back edge sits flush on the west wall (wall inner face at x=10.0) while keeping its front facing the room. |
| 100 | 2 | move_piece | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Shift the desk east so its back edge sits flush on the west wall (inner face at x=10.0) while keeping its front facing the room. |
| 126 | 3 | remove_piece | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment (kitchen_counter) is never removed | A kitchen counter is not a valid piece of a fire-escape stair room (type 'other'); it is an inferred box with no plan crop evidence, and it renders as a solid wall-like slab blocking the room. |
| 127 | 3 | move_piece | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment (kitchen_counter) is never moved | Snap the counter's back edge onto the south wall to resolve the 0.13 m off-wall violation. |
| 128 | 3 | change_type | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment keeps its type (kitchen_counter) | A kitchen counter is not a valid piece of a fire-escape stair room; the 2.6 m long low box along the wall reads as a bench, which is a plausible piece for this room type. |
| 129 | 3 | swap_model | f_L0_001 | max_tries: f_L0_001 was edited 3 times in this round | Replace the wall-like opaque counter model with a low base-cabinet counter model so the back of the room stays visible. |
| 131 | 3 | change_type | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment keeps its type (kitchen_island) | In a staircase/void room a 2.6x0.55 m low drawn box along the wall is a console table, not a kitchen island; the second vision pass suggested console_table. |
| 132 | 3 | remove_piece | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment (kitchen_island) is never removed | A kitchen island cannot exist in a staircase/void room; the drawn box is an inferred misread (vision passes disagreed, no plan crop on disk to confirm it is furniture), so it is not furniture in this space. |
| 133 | 3 | rotate_piece | f_L0_004 | f_L0_004: clearance_ok, f_L0_004: inside_room, score: plausibility 97 -> 67 (F3 f_L0_004: desk: its back is not on a wall (0.02 m off); F6 f_L0_004: desk: the free zone in front of it is reaches out of the room; F9 f_L0_004: desk reaches 0.23 m² through the room outline) | Desk front currently faces the left wall; rotate so the front faces into the room (east) for a usable workspace. |
| 134 | 3 | move_piece | f_L0_004 | f_L0_004: doors_free, score: plausibility 97 -> 37 (F3 f_L0_004: desk: its back is not on a wall (0.25 m off); F6 f_L0_004: no 0.9 m walkway from d_L0_001 to d_L0_002 (blocked by f_L0_004); F6 f_L0_004: no 0.9 m walkway from d_L0_001 to d_L0_004 (blocked by f_L0_004); F6 f_L0_004: no 0.9 m walkway from d_L0_002 to d_L0_003 (blocked by f_L0_004)) | Shift desk east so its front (facing +X into the room) has a free zone inside the room and it no longer crosses the outline. |
| 135 | 3 | move_piece | f_L0_004 | f_L0_004: doors_free, score: plausibility 97 -> 87 (F3 f_L0_004: desk: its back is not on a wall (0.20 m off)) | Shift desk east so its front (facing +X into the room) has a free zone inside the room and it no longer crosses the outline. |
| 136 | 3 | move_piece | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Snap desk back to the west wall so its front faces into the room (east) with a clear free zone, fixing the wall-facing orientation. |
| 157 | 4 | remove_piece | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment (kitchen_counter) is never removed | The room is a fire stair (Yangın Merdiveni) with no doors, windows or kitchen fixtures; the 2.6×0.55 m box is a misread drawing artifact (vision shows it as a solid wall-like slab, and the two vision passes disagreed on its type), not a kitchen counter. |
| 158 | 4 | change_type | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment keeps its type (kitchen_counter) | The room is a fire stair (Yangın Merdiveni) with no doors, windows or kitchen fixtures, so a kitchen counter cannot belong here; the 2.6×0.55 m low box along the wall matches a console table, which is allowed in an 'other' room. |
| 159 | 4 | move_piece | f_L0_001 | drawn_lock: f_L0_001: drawn fixed equipment (kitchen_counter) is never moved | Snap the counter's back edge onto the south wall (w_L0_016) to clear the F3 'back 0.13 m off a wall' finding. |
| 160 | 4 | remove_piece | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment (kitchen_island) is never removed | The 2.6×0.55 m box spans the full width of the stair room (Kat Merdiveni) at the landing level, matching the stair flight/landing drawn in the plan, not a kitchen island; the two vision passes disagreed (unknown vs kitchen_island) and no kitchen exists in this building, so it is not furniture. |
| 161 | 4 | change_type | f_L0_002 | drawn_lock: f_L0_002: drawn fixed equipment keeps its type (kitchen_island) | The 2.6×0.55 m box spans the full width of the stair room (Kat Merdiveni) at the landing level, matching the stair flight/landing drawn in the plan; the two vision passes disagreed (unknown vs kitchen_island) and no kitchen exists in this building, so it is the stair, not an island. |
| 162 | 4 | rotate_piece | f_L0_004 | f_L0_004: clearance_ok, f_L0_004: inside_room, score: plausibility 97 -> 67 (F3 f_L0_004: desk: its back is not on a wall (0.02 m off); F6 f_L0_004: desk: the free zone in front of it is reaches out of the room; F9 f_L0_004: desk reaches 0.23 m² through the room outline) | Turn the desk so its front faces the open room instead of the west wall. |
| 163 | 4 | move_piece | f_L0_004 | f_L0_004: doors_free, score: plausibility 97 -> 34 (F3 f_L0_004: desk: its back is not on a wall (0.30 m off); F6 f_L0_004: no 0.9 m walkway from d_L0_001 to d_L0_002 (blocked by f_L0_004); F6 f_L0_004: no 0.9 m walkway from d_L0_001 to d_L0_004 (blocked by f_L0_004); F6 f_L0_004: no 0.9 m walkway from d_L0_002 to d_L0_003 (blocked by f_L0_004)) | Shift the desk east so its front faces the open room with a clear working zone. |
| 164 | 4 | move_piece | f_L0_004 | snap: f_L0_004: no free place on wall w_L0_003 (doors, windows) | Snap the desk's back to the north wall so its front faces the open room. |
| 165 | 4 | move_piece | f_L0_004 | max_tries: f_L0_004 was edited 3 times in this round | Place the desk against the north wall between the two doors so its front faces the open room. |

### Inferred and AI-changed items

| id | kind | type | room | labels | reason |
|---|---|---|---|---|---|
| f_L0_001 | piece | kitchen_counter | r_L0_yangin_merdiveni | inferred | - |
| f_L0_002 | piece | kitchen_island | r_L0_kat_merdiveni | inferred | - |
| f_L0_003 | piece | unknown | r_L0_kat_holu | adjusted_by_ai | The 0.90×0.34 m box is a thin sliver inside the entry nook, not a plausible standalone furniture item; no plan crop exists to identify it, so it is removed as a drawing artifact. |
| f_L0_010 | piece | console_table | r_L0_kat_holu | adjusted_by_ai | Snap the console table's back onto the south wall w_L0_005 to fix the 0.94 m off-wall violation. |
| f_L0_012 | piece | chair | r_L0_yangin_merdiveni | adjusted_by_ai | Keep chair adjacent to the dining table so the table is not left chairless while the stairwell furniture is being resolved. |

### Before and after (previews of the re-rendered views)

| round | view | before | after |
|---|---|---|---|
| 1 | cam_r_L0_kat_holu_1 | ![](agent/r1_cam_r_L0_kat_holu_1_before.jpg) | ![](agent/r1_cam_r_L0_kat_holu_1_after.jpg) |
| 1 | cam_r_L0_kat_holu_2 | ![](agent/r1_cam_r_L0_kat_holu_2_before.jpg) | ![](agent/r1_cam_r_L0_kat_holu_2_after.jpg) |
| 1 | cam_r_L0_kat_holu_3 | ![](agent/r1_cam_r_L0_kat_holu_3_before.jpg) | ![](agent/r1_cam_r_L0_kat_holu_3_after.jpg) |
| 1 | cam_r_L0_kat_merdiveni_1 | ![](agent/r1_cam_r_L0_kat_merdiveni_1_before.jpg) | ![](agent/r1_cam_r_L0_kat_merdiveni_1_after.jpg) |
| 1 | cam_r_L0_kat_merdiveni_2 | ![](agent/r1_cam_r_L0_kat_merdiveni_2_before.jpg) | ![](agent/r1_cam_r_L0_kat_merdiveni_2_after.jpg) |
| 1 | cam_r_L0_kat_merdiveni_3 | ![](agent/r1_cam_r_L0_kat_merdiveni_3_before.jpg) | ![](agent/r1_cam_r_L0_kat_merdiveni_3_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_1 | ![](agent/r1_cam_r_L0_yangin_merdiveni_1_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_1_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_2 | ![](agent/r1_cam_r_L0_yangin_merdiveni_2_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_2_after.jpg) |
| 1 | cam_r_L0_yangin_merdiveni_3 | ![](agent/r1_cam_r_L0_yangin_merdiveni_3_before.jpg) | ![](agent/r1_cam_r_L0_yangin_merdiveni_3_after.jpg) |
| 2 | cam_r_L0_kat_merdiveni_1 | ![](agent/r2_cam_r_L0_kat_merdiveni_1_before.jpg) | ![](agent/r2_cam_r_L0_kat_merdiveni_1_after.jpg) |
| 2 | cam_r_L0_kat_merdiveni_2 | ![](agent/r2_cam_r_L0_kat_merdiveni_2_before.jpg) | ![](agent/r2_cam_r_L0_kat_merdiveni_2_after.jpg) |
| 2 | cam_r_L0_kat_merdiveni_3 | ![](agent/r2_cam_r_L0_kat_merdiveni_3_before.jpg) | ![](agent/r2_cam_r_L0_kat_merdiveni_3_after.jpg) |
| 2 | cam_r_L0_yangin_merdiveni_1 | ![](agent/r2_cam_r_L0_yangin_merdiveni_1_before.jpg) | ![](agent/r2_cam_r_L0_yangin_merdiveni_1_after.jpg) |
| 2 | cam_r_L0_yangin_merdiveni_2 | ![](agent/r2_cam_r_L0_yangin_merdiveni_2_before.jpg) | ![](agent/r2_cam_r_L0_yangin_merdiveni_2_after.jpg) |
| 2 | cam_r_L0_yangin_merdiveni_3 | ![](agent/r2_cam_r_L0_yangin_merdiveni_3_before.jpg) | ![](agent/r2_cam_r_L0_yangin_merdiveni_3_after.jpg) |
| 3 | cam_r_L0_kat_merdiveni_1 | ![](agent/r3_cam_r_L0_kat_merdiveni_1_before.jpg) | ![](agent/r3_cam_r_L0_kat_merdiveni_1_after.jpg) |
| 3 | cam_r_L0_kat_merdiveni_2 | ![](agent/r3_cam_r_L0_kat_merdiveni_2_before.jpg) | ![](agent/r3_cam_r_L0_kat_merdiveni_2_after.jpg) |
| 3 | cam_r_L0_kat_merdiveni_3 | ![](agent/r3_cam_r_L0_kat_merdiveni_3_before.jpg) | ![](agent/r3_cam_r_L0_kat_merdiveni_3_after.jpg) |

### Old pipeline vs orchestrator

Not made yet: the images of both runs come from the pods (`orchestrator/compare.json`).

## Warnings

None.
