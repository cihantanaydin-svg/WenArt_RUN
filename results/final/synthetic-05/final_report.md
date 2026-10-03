# Final report: synthetic-05

25 views: 0 polished, 25 Cycles (brief 25). Stages: render run, gate validation not_run, polish not_run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 25 |
| polished | 0 |
| Cycles | 25 (brief 25) |
| confirmed mismatches on the final image | 3 in 3 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 3 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 6 |
| exposure | -1.33 .. +6.00 EV (0 at a limit), modes auto |
| window pull | 16 view(s), -3 .. -1 EV |
| camera policy | search 25 |
| camera score (min / mean / max) | 1.77 / 3.17 / 4.14 |
| rooms by number of views | 2 with 2, 7 with 3 |
| gate validation | not recorded |
| seconds: build / render / metering | 23.8 s / 2.1 min / 10.5 s |
| seconds: polish / gate / check | - / - / 2.8 min |
| brief polish | no |

## Advisory flags and open items

- polish not run (every view is the Cycles render)
- vision check advisory: removal_flagged None misses >= 0.8 (no data); removal_confirmed None misses >= 0.6 (no data); insertion None misses >= 0.6 (no data)
- check target missed: removal_flagged - (needs >= 0.8), no data
- check target missed: removal_confirmed - (needs >= 0.6), no data
- check target missed: insertion - (needs >= 0.6), no data
- brief polish: false (no AI polish by request)

## Gate validation

Not needed: brief polish: false (every view is the Cycles render).

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | pull EV | camera | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_antre_1 | r_L0_antre | L0 | cycles | brief | - | - | ok | - | - | -0.83 | - | search 4.04 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_1_final_preview.jpg) [plan](cam_r_L0_antre_1_plan.jpg) |
| cam_r_L0_antre_2 | r_L0_antre | L0 | cycles | brief | - | - | ok | - | - | -0.83 | - | search 3.61 | D1 A1 | 0 | no | [preview](cam_r_L0_antre_2_final_preview.jpg) [plan](cam_r_L0_antre_2_plan.jpg) |
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | cycles | brief | - | - | info | - | - | +5.83 | -2 | search 2.72 | D4 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | cycles | brief | - | - | ok | - | - | +6.00 | -3 | search 2.39 | D2 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_banyo_3 | r_L0_banyo | L0 | cycles | brief | - | - | ok | - | - | +5.83 | - | search 1.77 | D2 | 0 | no | [preview](cam_r_L0_banyo_3_final_preview.jpg) [plan](cam_r_L0_banyo_3_plan.jpg) |
| cam_r_L0_calisma_odasi_1 | r_L0_calisma_odasi | L0 | cycles | brief | - | - | info | - | - | +5.00 | -2 | search 3.30 | D2 A4 | 0 | no | [preview](cam_r_L0_calisma_odasi_1_final_preview.jpg) [plan](cam_r_L0_calisma_odasi_1_plan.jpg) |
| cam_r_L0_calisma_odasi_2 | r_L0_calisma_odasi | L0 | cycles | brief | - | - | info | - | - | +4.67 | -1 | search 3.13 | D2 A4 | 0 | no | [preview](cam_r_L0_calisma_odasi_2_final_preview.jpg) [plan](cam_r_L0_calisma_odasi_2_plan.jpg) |
| cam_r_L0_calisma_odasi_3 | r_L0_calisma_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.83 | -2 | search 3.09 | D1 A2 | 0 | no | [preview](cam_r_L0_calisma_odasi_3_final_preview.jpg) [plan](cam_r_L0_calisma_odasi_3_plan.jpg) |
| cam_r_L0_ebeveyn_banyo_1 | r_L0_ebeveyn_banyo | L0 | cycles | brief | - | - | mismatch (1) | - | - | +5.00 | -2 | search 3.52 | D4 | 0 | yes | [preview](cam_r_L0_ebeveyn_banyo_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_banyo_1_plan.jpg) |
| cam_r_L0_ebeveyn_banyo_2 | r_L0_ebeveyn_banyo | L0 | cycles | brief | - | - | mismatch (1) | - | - | +5.00 | - | search 2.95 | D4 | 0 | yes | [preview](cam_r_L0_ebeveyn_banyo_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_banyo_2_plan.jpg) |
| cam_r_L0_ebeveyn_yatak_odasi_1 | r_L0_ebeveyn_yatak_odasi | L0 | cycles | brief | - | - | info | - | - | +4.50 | -2 | search 4.14 | D4 | 0 | no | [preview](cam_r_L0_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L0_ebeveyn_yatak_odasi_2 | r_L0_ebeveyn_yatak_odasi | L0 | cycles | brief | - | - | mismatch (1) | - | - | +4.67 | -2 | search 3.91 | D4 | 0 | yes | [preview](cam_r_L0_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L0_ebeveyn_yatak_odasi_3 | r_L0_ebeveyn_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +4.33 | - | search 3.72 | D4 | 0 | no | [preview](cam_r_L0_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | cycles | brief | - | - | ok | - | - | -0.33 | - | search 2.11 | D5 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | cycles | brief | - | - | ok | - | - | -1.33 | - | search 2.01 | D4 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_hol_3 | r_L0_hol | L0 | cycles | brief | - | - | ok | - | - | -0.33 | - | search 1.98 | D5 | 0 | no | [preview](cam_r_L0_hol_3_final_preview.jpg) [plan](cam_r_L0_hol_3_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | cycles | brief | - | - | ok | - | - | +4.33 | -2 | search 3.82 | D6 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | cycles | brief | - | - | ok | - | - | +4.17 | -2 | search 3.67 | D6 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | cycles | brief | - | - | ok | - | - | +4.33 | -1 | search 3.66 | D6 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | cycles | brief | - | - | ok | - | - | +4.00 | -2 | search 3.18 | D4 A1 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | cycles | brief | - | - | ok | - | - | +3.83 | -1 | search 3.00 | D4 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | cycles | brief | - | - | info | - | - | +3.83 | - | search 2.98 | D7 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | brief | - | - | info | - | - | +5.50 | -3 | search 3.58 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | brief | - | - | info | - | - | +5.50 | -3 | search 3.51 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | brief | - | - | ok | - | - | +5.83 | -3 | search 3.48 | D4 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). pull EV: the window pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

## Views per room

| room | type | level | views | polished | Cycles | cameras |
|---|---|---|---|---|---|---|
| r_L0_antre | hall | L0 | 2 | 0 | 2 | cam_r_L0_antre_1, cam_r_L0_antre_2 |
| r_L0_banyo | bathroom | L0 | 3 | 0 | 3 | cam_r_L0_banyo_1, cam_r_L0_banyo_2, cam_r_L0_banyo_3 |
| r_L0_calisma_odasi | other | L0 | 3 | 0 | 3 | cam_r_L0_calisma_odasi_1, cam_r_L0_calisma_odasi_2, cam_r_L0_calisma_odasi_3 |
| r_L0_ebeveyn_banyo | bathroom | L0 | 2 | 0 | 2 | cam_r_L0_ebeveyn_banyo_1, cam_r_L0_ebeveyn_banyo_2 |
| r_L0_ebeveyn_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_ebeveyn_yatak_odasi_1, cam_r_L0_ebeveyn_yatak_odasi_2, cam_r_L0_ebeveyn_yatak_odasi_3 |
| r_L0_hol | hall | L0 | 3 | 0 | 3 | cam_r_L0_hol_1, cam_r_L0_hol_2, cam_r_L0_hol_3 |
| r_L0_mutfak | kitchen | L0 | 3 | 0 | 3 | cam_r_L0_mutfak_1, cam_r_L0_mutfak_2, cam_r_L0_mutfak_3 |
| r_L0_salon | living | L0 | 3 | 0 | 3 | cam_r_L0_salon_1, cam_r_L0_salon_2, cam_r_L0_salon_3 |
| r_L0_yatak_odasi | bedroom | L0 | 3 | 0 | 3 | cam_r_L0_yatak_odasi_1, cam_r_L0_yatak_odasi_2, cam_r_L0_yatak_odasi_3 |

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | cycles | disputed | f_L0_022 | toilet | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:16D KLOZET vector 1.00 | info | - |
| cam_r_L0_ebeveyn_banyo_1 | cycles | disputed | f_L0_014 | washbasin | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:15D LAVABO vector 1.00 | info | - |
| cam_r_L0_ebeveyn_banyo_1 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L0_ebeveyn_banyo_2 | cycles | missing | f_L0_012 | shower | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:159 DUS vector 1.00 | info | - |
| cam_r_L0_ebeveyn_banyo_2 | cycles | missing | f_L0_013 | toilet | optional | from_documents | zemin_kat_mobilya.dxf MOBILYA INSERT:15B KLOZET vector 1.00 | info | - |
| cam_r_L0_ebeveyn_banyo_2 | cycles | window count more | window | window | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L0_ebeveyn_yatak_odasi_2 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |

## Needs review

- cam_r_L0_ebeveyn_banyo_1: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}
- cam_r_L0_ebeveyn_banyo_2: window count more than expected [0, 0]: {'qwen': 1, 'glm': 1}
- cam_r_L0_ebeveyn_yatak_odasi_2: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Rooms mixing polished and Cycles views

None.

## Models and licences

| role | model | revision | licence | from |
|---|---|---|---|---|
| check qwen | Qwen/Qwen3-VL-8B-Instruct | 0c351dd01ed87e9c1b53cbc748cba10e6187ff3b | Apache-2.0 | check_manifest.json |
| check glm | zai-org/GLM-4.6V-Flash | 411bb4d77144a3f03accbf4b780f5acb8b7cde4e | MIT | check_manifest.json |

Assets: textures CC0 x 4; furniture/decor models CC0 x 15 (parametric meshes need no licence).

## Stages

This run (`20261003-030812-full-20261003T031435Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | ok | 9.9 s | - |
| fit | ok | 3.6 s | - |
| style | ok | 0.4 s | - |
| layout | ok | 18.0 s | - |
| photos | ok | 7.7 s | - |
| assets | ok | 1.1 s | - |
| decor | ok | 2.2 s | - |
| refit | ok | 2.4 s | - |
| build | ok | 36.5 s | - |
| render | ok | 3.5 min | - |
| controls | ok | 76.8 s | - |
| gate | skipped | 0.0 s | polish off |
| polish | skipped | 0.0 s | polish off |
| expected | ok | 24.1 s | - |
| check | ok | 2.3 min | - |
| combine | ok | 22.6 s | - |

The report stage itself is recorded after this report.

## Warnings

None.
