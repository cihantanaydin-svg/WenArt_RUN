# Final report: synthetic-04

14 views: 10 polished, 4 Cycles (check_incomplete 1, room 3). Stages: render run, gate validation ok, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 14 |
| polished | 10 |
| Cycles | 4 (check_incomplete 1, room 3) |
| confirmed mismatches on the final image | 0 in 0 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 0 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 1 |
| advisory | yes |
| advisory flags | 4 |
| exposure | -0.83 .. +5.83 EV (0 at a limit), modes auto |
| window pull | 12 view(s), -3 .. 0 EV |
| camera policy | search 14 |
| camera score (min / mean / max) | 1.85 / 3.38 / 4.14 |
| rooms by number of views | 1 with 2, 4 with 3 |
| gate validation | ok |
| seconds: build / render / metering | 21.8 s / 63.8 s / 6.2 s |
| seconds: polish / gate / check | 2.7 min / 11.9 s / 3.6 min |
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
| benign controls accepted | 97.5 % (limit 95 %), 40 comparisons |
| negative controls rejected | 97.8 % (limit 90 %), 90 comparisons |
| effect | polish allowed |

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L3: [contact_L3.jpg](contact_L3.jpg)

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | r_L3_banyo | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.50 | -2 | search 2.26 | D3 | 0 | no | [preview](cam_r_L3_banyo_1_final_preview.jpg) [plan](cam_r_L3_banyo_1_plan.jpg) |
| cam_r_L3_banyo_2 | r_L3_banyo | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +5.83 | -2 | search 1.85 | D2 | 0 | no | [preview](cam_r_L3_banyo_2_final_preview.jpg) [plan](cam_r_L3_banyo_2_plan.jpg) |
| cam_r_L3_cocuk_odasi_1 | r_L3_cocuk_odasi | L3 | cycles | check_incomplete | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.83 | -2 | search 3.52 | D2 A5 | 0 | no | [preview](cam_r_L3_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L3_cocuk_odasi_1_plan.jpg) |
| cam_r_L3_cocuk_odasi_2 | r_L3_cocuk_odasi | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +4.67 | -2 | search 3.26 | D2 A3 | 0 | no | [preview](cam_r_L3_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L3_cocuk_odasi_2_plan.jpg) |
| cam_r_L3_cocuk_odasi_3 | r_L3_cocuk_odasi | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +4.67 | -1 | search 3.00 | D1 A4 | 0 | no | [preview](cam_r_L3_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L3_cocuk_odasi_3_plan.jpg) |
| cam_r_L3_hol_1 | r_L3_hol | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | 0 | search 4.14 | D1 A1 | 0 | no | [preview](cam_r_L3_hol_1_final_preview.jpg) [plan](cam_r_L3_hol_1_plan.jpg) |
| cam_r_L3_hol_2 | r_L3_hol | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.50 | - | search 4.11 | D2 A1 | 0 | no | [preview](cam_r_L3_hol_2_final_preview.jpg) [plan](cam_r_L3_hol_2_plan.jpg) |
| cam_r_L3_hol_3 | r_L3_hol | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | -0.83 | - | search 3.30 | D1 A1 | 0 | no | [preview](cam_r_L3_hol_3_final_preview.jpg) [plan](cam_r_L3_hol_3_plan.jpg) |
| cam_r_L3_salon_mutfak_1 | r_L3_salon_mutfak | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 2/4 | +3.83 | -1 | search 3.32 | D7 | 0 | no | [preview](cam_r_L3_salon_mutfak_1_final_preview.jpg) [plan](cam_r_L3_salon_mutfak_1_plan.jpg) |
| cam_r_L3_salon_mutfak_2 | r_L3_salon_mutfak | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | preferred 3/4 | +4.00 | -3 | search 3.29 | D11 | 0 | no | [preview](cam_r_L3_salon_mutfak_2_final_preview.jpg) [plan](cam_r_L3_salon_mutfak_2_plan.jpg) |
| cam_r_L3_salon_mutfak_3 | r_L3_salon_mutfak | L3 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | preferred 3/4 | +4.00 | -1 | search 3.25 | D6 | 0 | no | [preview](cam_r_L3_salon_mutfak_3_final_preview.jpg) [plan](cam_r_L3_salon_mutfak_3_plan.jpg) |
| cam_r_L3_yatak_odasi_1 | r_L3_yatak_odasi | L3 | cycles | room | - | - | ok | - | - | +4.50 | -2 | search 4.13 | D4 | 0 | no | [preview](cam_r_L3_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L3_yatak_odasi_1_plan.jpg) |
| cam_r_L3_yatak_odasi_2 | r_L3_yatak_odasi | L3 | cycles | room | - | - | ok | - | - | +4.83 | -2 | search 4.03 | D4 A1 | 0 | no | [preview](cam_r_L3_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L3_yatak_odasi_2_plan.jpg) |
| cam_r_L3_yatak_odasi_3 | r_L3_yatak_odasi | L3 | cycles | room | - | - | ok | - | - | +4.33 | -2 | search 3.82 | D3 A1 | 0 | no | [preview](cam_r_L3_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L3_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L3_banyo | bathroom | L3 | 2 | 2 | 0 | cam_r_L3_banyo_1, cam_r_L3_banyo_2 |
| r_L3_cocuk_odasi | bedroom | L3 | 3 | 2 | 1 | cam_r_L3_cocuk_odasi_1, cam_r_L3_cocuk_odasi_2, cam_r_L3_cocuk_odasi_3 |
| r_L3_hol | hall | L3 | 3 | 3 | 0 | cam_r_L3_hol_1, cam_r_L3_hol_2, cam_r_L3_hol_3 |
| r_L3_salon_mutfak | living | L3 | 3 | 3 | 0 | cam_r_L3_salon_mutfak_1, cam_r_L3_salon_mutfak_2, cam_r_L3_salon_mutfak_3 |
| r_L3_yatak_odasi | bedroom | L3 | 3 | 0 | 3 | cam_r_L3_yatak_odasi_1, cam_r_L3_yatak_odasi_2, cam_r_L3_yatak_odasi_3 |

### Why Cycles

- cam_r_L3_cocuk_odasi_1: check_incomplete: polished image: unreliable pass (glm saw the decoy)
- cam_r_L3_yatak_odasi_1: room: polish: room
- cam_r_L3_yatak_odasi_2: room: polish: room
- cam_r_L3_yatak_odasi_3: room: polish: room

## Mismatches (never auto-fixed)

None.

## Needs review

None.

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Rooms mixing polished and Cycles views

| room | polished | Cycles (reason) | polish room rule |
|---|---|---|---|
| r_L3_cocuk_odasi | cam_r_L3_cocuk_odasi_2, cam_r_L3_cocuk_odasi_3 | cam_r_L3_cocuk_odasi_1 (check_incomplete) | ok |

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L3_yatak_odasi (rung None).

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

Assets: textures CC0 x 6; furniture/decor models CC0 x 15 (parametric meshes need no licence).

## Stages

This run (`20261003-030812-full-20261003T031435Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 14.4 s | - |
| fit | ok | 2.6 s | - |
| photos | skipped | 0.0 s | no style photos |
| style | ok | 0.4 s | - |
| layout | ok | 21.7 s | - |
| assets | ok | 4.1 s | - |
| decor | ok | 2.0 s | - |
| refit | ok | 2.5 s | - |
| build | ok | 33.7 s | - |
| render | ok | 115.4 s | - |
| controls | ok | 75.4 s | - |
| gate | ok | 94.4 s | gate decision ok |
| polish | ok | 4.2 min | - |
| expected | ok | 20.6 s | - |
| check | ok | 3.2 min | - |
| combine | ok | 18.3 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
