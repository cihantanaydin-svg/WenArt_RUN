# Final report: synthetic-04

14 views: 6 polished, 8 Cycles (gate 2, room 5, vision_check 1). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 14 |
| polished | 6 |
| Cycles | 8 (gate 2, room 5, vision_check 1) |
| confirmed mismatches on the final image | 1 in 1 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 1 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 5 |
| exposure | -0.83 .. +5.67 EV (0 at a limit), modes auto |
| window pull | 10 view(s), -2 .. -1 EV |
| camera policy | search 14 |
| camera score (min / mean / max) | 2.31 / 3.48 / 4.38 |
| rooms by number of views | 1 with 2, 4 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 71.7 s / 40.2 s / 8.3 s |
| seconds: polish / gate / check | 99.4 s / 17.6 s / 9.3 min |
| brief polish | yes (default, not in brief.yaml) |
| unit system | metric |
| side-by-side sheets | 5 |

## Advisory flags and open items

- vision check advisory: removal_flagged 0.7143 misses >= 0.8; removal_confirmed 0.5714 misses >= 0.6; insertion 0.0 misses >= 0.6
- check target missed: removal_flagged 0.714 (needs >= 0.8)
- check target missed: removal_confirmed 0.571 (needs >= 0.6)
- check target missed: insertion 0.000 (needs >= 0.6)
- the polish added an object in cam_r_L3_salon_mutfak_3: the Cycles render is final

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 100.0 % (limit 95 %), 40 comparisons |
| negative controls rejected | 98.0 % (limit 90 %), 98 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L3: [contact_L3.jpg](contact_L3.jpg)

## Side-by-side sheets (Cycles | polished)

Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the last attempt the gate saw) with the gate decision, both check verdicts and the final decision.

- r_L3_banyo: [contact_sbs_r_L3_banyo.jpg](contact_sbs_r_L3_banyo.jpg)

- r_L3_cocuk_odasi: [contact_sbs_r_L3_cocuk_odasi.jpg](contact_sbs_r_L3_cocuk_odasi.jpg)

- r_L3_hol: [contact_sbs_r_L3_hol.jpg](contact_sbs_r_L3_hol.jpg)

- r_L3_salon_mutfak: [contact_sbs_r_L3_salon_mutfak.jpg](contact_sbs_r_L3_salon_mutfak.jpg)

- r_L3_yatak_odasi: [contact_sbs_r_L3_yatak_odasi.jpg](contact_sbs_r_L3_yatak_odasi.jpg)

| room | view | polish attempt | gate | check Cycles | check polished | detector | final |
|---|---|---|---|---|---|---|---|
| r_L3_banyo | cam_r_L3_banyo_1 | a1 s 0.375 geometry x0.8 | accept | info | info | calibrated | polished |
| r_L3_banyo | cam_r_L3_banyo_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L3_cocuk_odasi | cam_r_L3_cocuk_odasi_1 | - | - | mismatch (1) | - | - | cycles (room) |
| r_L3_cocuk_odasi | cam_r_L3_cocuk_odasi_2 | - | - | ok | - | - | cycles (room) |
| r_L3_cocuk_odasi | cam_r_L3_cocuk_odasi_3 | - | - | info | - | - | cycles (gate) |
| r_L3_hol | cam_r_L3_hol_1 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L3_hol | cam_r_L3_hol_2 | a2 s 0.25 canny x0.8 | accept | ok | ok | calibrated | polished |
| r_L3_hol | cam_r_L3_hol_3 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L3_salon_mutfak | cam_r_L3_salon_mutfak_1 | - | - | info | - | - | cycles (gate) |
| r_L3_salon_mutfak | cam_r_L3_salon_mutfak_2 | a1 s 0.375 geometry x0.8 | accept | ok | ok | calibrated | polished |
| r_L3_salon_mutfak | cam_r_L3_salon_mutfak_3 | a2 s 0.25 canny x0.8 | accept | info | info | added_by_polish | cycles (vision_check) |
| r_L3_yatak_odasi | cam_r_L3_yatak_odasi_1 | - | - | ok | - | - | cycles (room) |
| r_L3_yatak_odasi | cam_r_L3_yatak_odasi_2 | - | - | ok | - | - | cycles (room) |
| r_L3_yatak_odasi | cam_r_L3_yatak_odasi_3 | - | - | ok | - | - | cycles (room) |

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | r_L3_banyo | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.50 | -2 | search 2.51 | D4 | 0 | no | [preview](cam_r_L3_banyo_1_final_preview.jpg) [plan](cam_r_L3_banyo_1_plan.jpg) |
| cam_r_L3_banyo_2 | r_L3_banyo | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.67 | -2 | search 2.32 | D2 | 0 | no | [preview](cam_r_L3_banyo_2_final_preview.jpg) [plan](cam_r_L3_banyo_2_plan.jpg) |
| cam_r_L3_cocuk_odasi_1 | r_L3_cocuk_odasi | L3 | cycles | room | - | - | mismatch (1) | - | - | +5.00 | -2 | search 3.70 | D2 A4 | 0 | yes | [preview](cam_r_L3_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L3_cocuk_odasi_1_plan.jpg) |
| cam_r_L3_cocuk_odasi_2 | r_L3_cocuk_odasi | L3 | cycles | room | - | - | ok | - | - | +4.33 | -1 | search 3.62 | D2 A4 | 0 | no | [preview](cam_r_L3_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L3_cocuk_odasi_2_plan.jpg) |
| cam_r_L3_cocuk_odasi_3 | r_L3_cocuk_odasi | L3 | cycles | gate | - | - | info | - | - | +4.50 | - | search 3.27 | D2 A4 | 0 | no | [preview](cam_r_L3_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L3_cocuk_odasi_3_plan.jpg) |
| cam_r_L3_hol_1 | r_L3_hol | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | - | search 4.16 | D1 A1 | 0 | no | [preview](cam_r_L3_hol_1_final_preview.jpg) [plan](cam_r_L3_hol_1_plan.jpg) |
| cam_r_L3_hol_2 | r_L3_hol | L3 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | - | search 3.23 | D1 A1 | 0 | no | [preview](cam_r_L3_hol_2_final_preview.jpg) [plan](cam_r_L3_hol_2_plan.jpg) |
| cam_r_L3_hol_3 | r_L3_hol | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.67 | - | search 3.20 | D1 A1 | 0 | no | [preview](cam_r_L3_hol_3_final_preview.jpg) [plan](cam_r_L3_hol_3_plan.jpg) |
| cam_r_L3_salon_mutfak_1 | r_L3_salon_mutfak | L3 | cycles | gate | - | - | info | - | - | +3.83 | -2 | search 3.32 | D9 A2 | 0 | no | [preview](cam_r_L3_salon_mutfak_1_final_preview.jpg) [plan](cam_r_L3_salon_mutfak_1_plan.jpg) |
| cam_r_L3_salon_mutfak_2 | r_L3_salon_mutfak | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.33 | -1 | search 3.26 | D6 A1 | 0 | no | [preview](cam_r_L3_salon_mutfak_2_final_preview.jpg) [plan](cam_r_L3_salon_mutfak_2_plan.jpg) |
| cam_r_L3_salon_mutfak_3 | r_L3_salon_mutfak | L3 | cycles | vision_check | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +3.50 | -1 | search 3.25 | D12 A2 | 0 | no | [preview](cam_r_L3_salon_mutfak_3_final_preview.jpg) [plan](cam_r_L3_salon_mutfak_3_plan.jpg) |
| cam_r_L3_yatak_odasi_1 | r_L3_yatak_odasi | L3 | cycles | room | - | - | ok | - | - | +4.33 | -1 | search 4.37 | D4 A2 | 0 | no | [preview](cam_r_L3_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L3_yatak_odasi_1_plan.jpg) |
| cam_r_L3_yatak_odasi_2 | r_L3_yatak_odasi | L3 | cycles | room | - | - | ok | - | - | +4.33 | -1 | search 4.37 | D5 A2 | 0 | no | [preview](cam_r_L3_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L3_yatak_odasi_2_plan.jpg) |
| cam_r_L3_yatak_odasi_3 | r_L3_yatak_odasi | L3 | cycles | room | - | - | ok | - | - | +4.33 | -2 | search 4.11 | D4 A2 | 0 | no | [preview](cam_r_L3_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L3_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L3_banyo | bathroom | L3 | 2 | 2 | 0 | cam_r_L3_banyo_1, cam_r_L3_banyo_2 |
| r_L3_cocuk_odasi | bedroom | L3 | 3 | 0 | 3 | cam_r_L3_cocuk_odasi_1, cam_r_L3_cocuk_odasi_2, cam_r_L3_cocuk_odasi_3 |
| r_L3_hol | hall | L3 | 3 | 3 | 0 | cam_r_L3_hol_1, cam_r_L3_hol_2, cam_r_L3_hol_3 |
| r_L3_salon_mutfak | living | L3 | 3 | 1 | 2 | cam_r_L3_salon_mutfak_1, cam_r_L3_salon_mutfak_2, cam_r_L3_salon_mutfak_3 |
| r_L3_yatak_odasi | bedroom | L3 | 3 | 0 | 3 | cam_r_L3_yatak_odasi_1, cam_r_L3_yatak_odasi_2, cam_r_L3_yatak_odasi_3 |

### Why Cycles

- cam_r_L3_cocuk_odasi_1: room: polish: room
- cam_r_L3_cocuk_odasi_2: room: polish: room
- cam_r_L3_cocuk_odasi_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L3_salon_mutfak_1: gate: no ladder attempt passed the gate: a1 reject (edges); a2 reject (edges); a3 reject (edges)
- cam_r_L3_salon_mutfak_3: vision_check: added_by_polish fixture at [825.6, 359.8, 839.5, 398.8]; added_by_polish furniture at [902.6, 436.2, 1041.7, 452.0]
- cam_r_L3_yatak_odasi_1: room: polish: room
- cam_r_L3_yatak_odasi_2: room: polish: room
- cam_r_L3_yatak_odasi_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | cycles | disputed | f_L3_021 | washbasin | optional | from_documents | 3_kat_plani.dxf MOBILYA INSERT:155 LAVABO vector 1.00; 3_kat_plani_pdf.pdf p1 path:101 vector 1.00 | info | - |
| cam_r_L3_banyo_1 | polished | disputed | f_L3_021 | washbasin | optional | from_documents | 3_kat_plani.dxf MOBILYA INSERT:155 LAVABO vector 1.00; 3_kat_plani_pdf.pdf p1 path:101 vector 1.00 | info | - |
| cam_r_L3_cocuk_odasi_1 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L3_salon_mutfak_1 | cycles | disputed | dec_L3_005 | rug | optional | added_by_ai | rule: rug under the dining table (+ 0.6 m each side for the chairs); cut from 3.40 x 2.70 m to stay off walls, door swings and fixed pieces | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L3_salon_mutfak_3 | cycles | missing | f_L3_010 | sofa | optional | from_documents | 3_kat_plani.dxf MOBILYA INSERT:13F KANEPE_3LU vector 1.00; 3_kat_plani_pdf.pdf p1 path:79 vector 1.00 | info | - |
| cam_r_L3_salon_mutfak_3 | cycles | missing | f_L3_003 | stove | optional | from_documents | 3_kat_plani.dxf MOBILYA INSERT:131 OCAK vector 1.00; 3_kat_plani_pdf.pdf p1 path:65 vector 1.00 | info | - |
| cam_r_L3_salon_mutfak_3 | polished | missing | f_L3_010 | sofa | optional | from_documents | 3_kat_plani.dxf MOBILYA INSERT:13F KANEPE_3LU vector 1.00; 3_kat_plani_pdf.pdf p1 path:79 vector 1.00 | info | - |
| cam_r_L3_salon_mutfak_3 | polished | missing | f_L3_003 | stove | optional | from_documents | 3_kat_plani.dxf MOBILYA INSERT:131 OCAK vector 1.00; 3_kat_plani_pdf.pdf p1 path:65 vector 1.00 | info | - |

## Needs review

- cam_r_L3_cocuk_odasi_1: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

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
| 3_kat_plani.dxf | metric | dxf |
| 3_kat_plani_pdf.pdf | metric | cad_pdf |

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
- brief polish: True (default, not in brief.yaml)
- brief style_photos: [] (default, not in brief.yaml)
- brief ceiling_height: 2.7 (default, not in brief.yaml)
- brief render.views_per_room: 3 (default, not in brief.yaml)
- brief render.resolution: [1920, 1080] (default, not in brief.yaml)
- brief render.samples: 256 (default, not in brief.yaml)
- brief render.lens_mm: auto (default, not in brief.yaml)
- L3: ceiling height 2,70 m (assumed_default)

Scene (build) assumptions:

| field | objects | reason | e.g. |
|---|---|---|---|
| area_light | 1 | r_L3_hol: room has no window; soft ceiling light added (lighting mood, invisible to the camera) | light_r_L3_hol |
| ceiling_height | 1 | building JSON: assumed_default | level_L3 |
| counter_fronts | 1 | design detail of the counter (fronts and handles inside its own box); the documents show only the footprint | furn_f_L3_001 |
| door_handles | 5 | design detail of the documented door (lever handles on both faces); not in the documents | d_L3_001_handle, d_L3_002_handle, d_L3_003_handle |
| fabric | 1 | style profile has no textiles slot; default fabric for sofas and chairs | furniture |
| height | 5 | door height not in the JSON; default | d_L3_001, d_L3_002, d_L3_003 |
| height | 1 | no height in the JSON; type height for armchair | furn_f_L3_013 |
| height | 1 | no height in the JSON; type height for bathtub | furn_f_L3_019 |
| height | 1 | no height in the JSON; type height for bed_double | furn_f_L3_015 |
| height | 1 | no height in the JSON; type height for bookshelf | furn_f_L3_014 |
| height | 4 | no height in the JSON; type height for chair | furn_f_L3_006, furn_f_L3_007, furn_f_L3_008 |
| height | 1 | no height in the JSON; type height for fridge | furn_f_L3_004 |
| height | 1 | no height in the JSON; type height for kitchen_counter | furn_f_L3_001 |
| height | 2 | no height in the JSON; type height for nightstand | furn_f_L3_016, furn_f_L3_017 |
| height | 1 | no height in the JSON; type height for sink_kitchen | furn_f_L3_002 |
| height | 1 | no height in the JSON; type height for sofa | furn_f_L3_010 |
| height | 1 | no height in the JSON; type height for stove | furn_f_L3_003 |
| height | 1 | no height in the JSON; type height for table_coffee | furn_f_L3_011 |
| height | 1 | no height in the JSON; type height for table_dining | furn_f_L3_005 |
| height | 1 | no height in the JSON; type height for toilet | furn_f_L3_020 |
| height | 1 | no height in the JSON; type height for tv_unit | furn_f_L3_012 |
| height | 1 | no height in the JSON; type height for wardrobe | furn_f_L3_018 |
| height | 1 | no height in the JSON; type height for washbasin | furn_f_L3_021 |
| height | 10 | window height not in the JSON; default | win_L3_001, win_L3_002, win_L3_003 |
| height_lift | 2 | footprint overlaps another piece of the same height; lifted so the top faces do not coincide | furn_f_L3_002, furn_f_L3_003 |
| sill_height | 10 | window sill_height not in the JSON; default | win_L3_001, win_L3_002, win_L3_003 |
| skirting | 4 | design detail of the room's documented walls (painted skirting board); not in the documents | skirting_r_L3_salon_mutfak, skirting_r_L3_yatak_odasi, skirting_r_L3_hol |

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L3_salon_mutfak | cam_r_L3_salon_mutfak_2 | cam_r_L3_salon_mutfak_1 (gate), cam_r_L3_salon_mutfak_3 (vision_check) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L3_cocuk_odasi (rung None), r_L3_yatak_odasi (rung None).

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

Assets: textures CC0 x 5; furniture/decor models CC-BY-4.0 x 26, CC0 x 3 (parametric meshes need no licence).

## Attribution

3D models from Objaverse 1.0 used in these images (§7.3):

- "Lowpoly Bed" by Mohamed199 (https://sketchfab.com/3d-models/6eb4212e70b941a3bd2db196a47828b9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (used for f_L3_023)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image (the Cycles render is final).
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| view | detector | computed | added_by_polish | confirmed boxes |
|---|---|---|---|---|
| cam_r_L3_banyo_1 | calibrated | yes | no | - |
| cam_r_L3_banyo_2 | calibrated | yes | no | - |
| cam_r_L3_hol_1 | calibrated | yes | no | - |
| cam_r_L3_hol_2 | calibrated | yes | no | - |
| cam_r_L3_hol_3 | calibrated | yes | no | - |
| cam_r_L3_salon_mutfak_2 | calibrated | yes | no | - |
| cam_r_L3_salon_mutfak_3 | calibrated | yes | yes | fixture [825.6, 359.8, 839.5, 398.8] (score); furniture [902.6, 436.2, 1041.7, 452.0] (score) |

## Stages

This run (`20261004-095244-full-20261004T095809Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 12.6 s | - |
| pipeline_final | skipped | 0.0 s | no questions |
| recognize | skipped | 0.0 s | no questions |
| fit | ok | 2.1 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.4 s | - |
| layout | ok | 17.6 s | - |
| assets | ok | 0.7 s | - |
| decor | ok | 1.8 s | - |
| refit | ok | 1.8 s | - |
| build | ok | 81.5 s | - |
| render | ok | 86.6 s | - |
| controls | ok | 57.5 s | - |
| gate | ok | 59.0 s | gate decision ok |
| polish | ok | 3.1 min | - |
| detect | ok | 8.1 s | - |
| expected | ok | 15.3 s | - |
| check | ok | 86.1 s | - |
| combine | ok | 13.6 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
