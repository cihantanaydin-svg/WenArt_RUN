# Final report: synthetic-01

29 views: 18 polished, 11 Cycles (gate 2, room 9). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 29 |
| polished | 18 |
| Cycles | 11 (gate 2, room 9) |
| confirmed mismatches on the final image | 2 in 2 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 2 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 2 |
| advisory | yes |
| advisory flags | 4 |
| exposure | -0.67 .. +6.50 EV (0 at a limit), modes auto |
| window pull | 18 view(s), -4 .. 0 EV |
| camera policy | search 29 |
| camera score (min / mean / max) | 1.69 / 3.21 / 3.82 |
| rooms by number of views | 1 with 2, 9 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 28.4 s / 2.7 min / 12.8 s |
| seconds: polish / gate / check | 6.3 min / 27.4 s / 6.5 min |
| brief polish | yes (default, not in brief.yaml) |

## Advisory flags and open items

- vision check advisory: removal_flagged None misses >= 0.8 (no data); removal_confirmed None misses >= 0.6 (no data); insertion None misses >= 0.6 (no data)
- check target missed: removal_flagged - (needs >= 0.8), no data
- check target missed: removal_confirmed - (needs >= 0.6), no data
- check target missed: insertion - (needs >= 0.6), no data

## Gate validation

| item | value |
|---|---|
| decision | ok |
| benign controls accepted | 96.9 % (limit 95 %), 64 comparisons |
| negative controls rejected | 96.4 % (limit 90 %), 166 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | +6.50 | -3 | search 2.81 | D5 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +6.33 | -4 | search 2.58 | D5 | 0 | yes | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_banyo_3 | r_L0_banyo | L0 | cycles | gate | - | - | info | - | - | +6.17 | - | search 2.06 | D2 | 0 | no | [preview](cam_r_L0_banyo_3_final_preview.jpg) [plan](cam_r_L0_banyo_3_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.67 | - | search 3.82 | D1 A1 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.67 | - | search 3.72 | D1 A1 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | room | - | - | info | - | - | +4.67 | -2 | search 2.86 | D1 A6 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | room | - | - | ok | - | - | +4.17 | -1 | search 2.47 | D2 A2 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | room | - | - | ok | - | - | +5.83 | -4 | search 1.69 | D1 A1 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 1/4 | +3.50 | -1 | search 3.53 | D5 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +3.50 | -1 | search 3.51 | D6 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +3.50 | -2 | search 3.44 | D6 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +3.83 | -1 | search 3.72 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +4.17 | -1 | search 3.58 | D3 A1 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +4.33 | - | search 3.33 | D5 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | cycles | gate | - | - | info | - | - | +0.00 | - | search 3.69 | D1 A3 | 0 | no | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | +0.00 | 0 | search 3.60 | D2 A3 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | -0.17 | - | search 3.37 | D1 A2 | 0 | no | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +5.67 | -3 | search 3.48 | D1 A5 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +5.67 | -3 | search 3.17 | D2 A5 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | cycles | room | - | - | info | - | - | +5.50 | -3 | search 2.98 | D1 A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.17 | -3 | search 3.62 | D2 A4 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.00 | - | search 3.33 | D1 A2 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +3.00 | -2 | search 3.31 | D1 A4 | 0 | yes | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | info | not preferred 0/4 | +0.17 | 0 | search 3.74 | D4 A2 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 3.05 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +0.17 | - | search 2.99 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.67 | - | search 3.57 | D1 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.00 | - | search 3.34 | D1 A2 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +3.33 | -1 | search 2.89 | D1 A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_banyo | bathroom | L0 | 3 | 2 | 1 | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_hol | hall | L0 | 2 | 2 | 0 | cam_r_L0_hol_1, cam_r_L0_hol_2 |
| r_L0_mutfak | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 3 | 0 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |
| r_L1_banyo | bathroom | L1 | 3 | 2 | 1 | cam_r_L1_banyo_1, cam_r_L1_banyo_2, cam_r_L1_banyo_3 |
| r_L1_cocuk_odasi | bedroom | L1 | 3 | 0 | 3 | cam_r_L1_cocuk_odasi_1, cam_r_L1_cocuk_odasi_2, cam_r_L1_cocuk_odasi_3 |
| r_L1_ebeveyn_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_ebeveyn_yatak_odasi_1, cam_r_L1_ebeveyn_yatak_odasi_2, cam_r_L1_ebeveyn_yatak_odasi_3 |
| r_L1_hol | hall | L1 | 3 | 3 | 0 | cam_r_L1_hol_1, cam_r_L1_hol_2, cam_r_L1_hol_3 |
| r_L1_yatak_odasi | bedroom | L1 | 3 | 3 | 0 | cam_r_L1_yatak_odasi_1, cam_r_L1_yatak_odasi_2, cam_r_L1_yatak_odasi_3 |

### Why Cycles

- cam_r_L0_banyo_3: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L0_mutfak_1: room: polish: room
- cam_r_L0_mutfak_2: room: polish: room
- cam_r_L0_mutfak_3: room: polish: room
- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: room: polish: room
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L1_banyo_1: gate: no ladder attempt passed the gate: a1 reject (depth); a2 reject (depth); a3 reject (depth)
- cam_r_L1_cocuk_odasi_1: room: polish: room
- cam_r_L1_cocuk_odasi_2: room: polish: room
- cam_r_L1_cocuk_odasi_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_2 | cycles | missing | f_L0_012 | shower | required | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | yes | - |
| cam_r_L0_banyo_2 | cycles | disputed | f_L0_011 | washbasin | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector 1.00 | info | - |
| cam_r_L0_banyo_2 | polished | missing | f_L0_012 | shower | required | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | yes | - |
| cam_r_L0_banyo_2 | polished | disputed | f_L0_013 | washing_machine | required | from_documents | zemin_kat.dxf MOBILYA INSERT:122 CAMASIR_MAK vector 1.00 | info | - |
| cam_r_L0_banyo_2 | polished | disputed | f_L0_011 | washbasin | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector 1.00 | info | - |
| cam_r_L0_banyo_3 | cycles | missing | f_L0_012 | shower | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | info | - |
| cam_r_L0_salon_1 | polished | disputed | f_L0_004 | armchair | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:110 KOLTUK vector 1.00 | info | - |
| cam_r_L1_banyo_1 | cycles | disputed | f_L1_012 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | disputed | f_L1_012 | shower | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_cocuk_odasi_1 | cycles | missing | f_L1_017 | wardrobe | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_3 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_ebeveyn_yatak_odasi_3 | polished | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_yatak_odasi_3 | cycles | missing | f_L1_008 | bed_double | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_3 | cycles | disputed | f_L1_011 | chair | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_3 | polished | missing | f_L1_008 | bed_double | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_yatak_odasi_3 | polished | missing | f_L1_011 | chair | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |

## Needs review

- cam_r_L0_banyo_2: f_L0_012 (shower, from_documents): missing
- cam_r_L1_ebeveyn_yatak_odasi_3: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L0_banyo | cam_r_L0_banyo_1, cam_r_L0_banyo_2 | cam_r_L0_banyo_3 (gate) | ok |
| r_L1_banyo | cam_r_L1_banyo_2, cam_r_L1_banyo_3 | cam_r_L1_banyo_1 (gate) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L0_mutfak (rung None), r_L0_yatak_odasi (rung None), r_L1_cocuk_odasi (rung None).

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

Assets: textures CC0 x 6; furniture/decor models CC0 x 23 (parametric meshes need no licence).

## Stages

This run (`20261003-014522-full-20261003T015157Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 19.4 s | earlier outputs without run records moved to /workspace/outputs-archive/synthetic-01-20261003T015157Z |
| fit | ok | 2.7 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.4 s | - |
| layout | ok | 67.8 s | - |
| assets | ok | 4.6 s | - |
| decor | ok | 2.3 s | - |
| refit | ok | 2.7 s | - |
| build | ok | 43.0 s | - |
| render | ok | 4.2 min | - |
| controls | ok | 86.2 s | - |
| gate | ok | 2.4 min | gate decision ok |
| polish | ok | 9.0 min | - |
| expected | ok | 26.9 s | - |
| check | ok | 5.3 min | - |
| combine | ok | 28.5 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
