# Final report: synthetic-01

30 views: 24 polished, 6 Cycles (room 6). Stages: render run, polish run, vision check run (calibration run). A polished image is final only when the gate accepted it and the vision check checked it without finding a lost or added element (§5.5). Mismatches are listed with their evidence and never auto-fixed.

## Summary

| item | value |
|---|---|
| views | 30 |
| polished | 24 |
| Cycles | 6 (room 6) |
| confirmed mismatches on the final image | 2 in 2 view(s) |
| JSON cross-check findings (Cycles render) | 0 |
| needs_review views | 2 |
| unverified pieces in view (sum over views) | 0 |
| rooms mixing polished and Cycles | 0 |
| advisory | yes |
| advisory flags | 2 |
| exposure | -1.00 .. +7.00 EV (0 at a limit), modes auto |
| seconds: build / render / metering | 19.5 s / 2.1 min / 7.8 s |
| seconds: polish / gate / check | 6.2 min / 26.7 s / 11.6 min |
| brief polish | yes (default, not in brief.yaml) |

## Advisory flags and open items

- vision check advisory: insertion 0.0 misses >= 0.6
- check target missed: insertion 0.000 (needs >= 0.6)

## Contact sheets

Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.

Level L0: [contact_L0.jpg](contact_L0.jpg)

Level L1: [contact_L1.jpg](contact_L1.jpg)

## Views

| view | room | level | final | reason | polish attempt | gate | check Cycles | check polished | preference | EV | ids D/A/R | U | review | files |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | ok | not preferred 1/4 | +6.17 | D3 | 0 | no | [preview](cam_r_L0_banyo_1_final_preview.jpg) [plan](cam_r_L0_banyo_1_plan.jpg) |
| cam_r_L0_banyo_2 | r_L0_banyo | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 2/4 | +5.83 | D3 | 0 | no | [preview](cam_r_L0_banyo_2_final_preview.jpg) [plan](cam_r_L0_banyo_2_plan.jpg) |
| cam_r_L0_banyo_3 | r_L0_banyo | L0 | polished | - | a3 s 0.125 depth x0.8 | accept | info | info | not preferred 0/4 | +6.17 | D3 | 0 | no | [preview](cam_r_L0_banyo_3_final_preview.jpg) [plan](cam_r_L0_banyo_3_plan.jpg) |
| cam_r_L0_hol_1 | r_L0_hol | L0 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | -0.83 | D2 A1 | 0 | no | [preview](cam_r_L0_hol_1_final_preview.jpg) [plan](cam_r_L0_hol_1_plan.jpg) |
| cam_r_L0_hol_2 | r_L0_hol | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | -0.83 | D3 A1 | 0 | no | [preview](cam_r_L0_hol_2_final_preview.jpg) [plan](cam_r_L0_hol_2_plan.jpg) |
| cam_r_L0_hol_3 | r_L0_hol | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | -1.00 | D1 A1 | 0 | no | [preview](cam_r_L0_hol_3_final_preview.jpg) [plan](cam_r_L0_hol_3_plan.jpg) |
| cam_r_L0_mutfak_1 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 1/4 | +4.67 | A5 | 0 | no | [preview](cam_r_L0_mutfak_1_final_preview.jpg) [plan](cam_r_L0_mutfak_1_plan.jpg) |
| cam_r_L0_mutfak_2 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.00 | D1 A5 | 0 | no | [preview](cam_r_L0_mutfak_2_final_preview.jpg) [plan](cam_r_L0_mutfak_2_plan.jpg) |
| cam_r_L0_mutfak_3 | r_L0_mutfak | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 1/4 | +5.33 | D1 A5 | 0 | no | [preview](cam_r_L0_mutfak_3_final_preview.jpg) [plan](cam_r_L0_mutfak_3_plan.jpg) |
| cam_r_L0_salon_1 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +3.33 | D6 | 0 | no | [preview](cam_r_L0_salon_1_final_preview.jpg) [plan](cam_r_L0_salon_1_plan.jpg) |
| cam_r_L0_salon_2 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | ok | not preferred 0/4 | +3.33 | D7 | 0 | no | [preview](cam_r_L0_salon_2_final_preview.jpg) [plan](cam_r_L0_salon_2_plan.jpg) |
| cam_r_L0_salon_3 | r_L0_salon | L0 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 1/4 | +3.50 | D4 | 0 | no | [preview](cam_r_L0_salon_3_final_preview.jpg) [plan](cam_r_L0_salon_3_plan.jpg) |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +4.33 | D3 A1 | 0 | no | [preview](cam_r_L0_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_1_plan.jpg) |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +4.33 | D3 | 0 | no | [preview](cam_r_L0_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_2_plan.jpg) |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | L0 | cycles | room | - | - | ok | - | - | +4.33 | D3 | 0 | no | [preview](cam_r_L0_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L0_yatak_odasi_3_plan.jpg) |
| cam_r_L1_banyo_1 | r_L1_banyo | L1 | polished | - | a3 s 0.125 depth x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +6.17 | A2 | 0 | yes | [preview](cam_r_L1_banyo_1_final_preview.jpg) [plan](cam_r_L1_banyo_1_plan.jpg) |
| cam_r_L1_banyo_2 | r_L1_banyo | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 2/4 | +6.50 | A1 | 0 | no | [preview](cam_r_L1_banyo_2_final_preview.jpg) [plan](cam_r_L1_banyo_2_plan.jpg) |
| cam_r_L1_banyo_3 | r_L1_banyo | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | mismatch (1) | mismatch (1) | not preferred 0/4 | +6.00 | A1 | 0 | yes | [preview](cam_r_L1_banyo_3_final_preview.jpg) [plan](cam_r_L1_banyo_3_plan.jpg) |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.50 | A2 | 0 | no | [preview](cam_r_L1_cocuk_odasi_1_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_1_plan.jpg) |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | info | info | not preferred 0/4 | +5.33 | D1 A3 | 0 | no | [preview](cam_r_L1_cocuk_odasi_2_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_2_plan.jpg) |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | +5.17 | A1 | 0 | no | [preview](cam_r_L1_cocuk_odasi_3_final_preview.jpg) [plan](cam_r_L1_cocuk_odasi_3_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 0/4 | +3.33 | D1 A3 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_1_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +3.50 | D1 A6 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_2_plan.jpg) |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | info | info | not preferred 0/4 | +3.17 | D1 A5 | 0 | no | [preview](cam_r_L1_ebeveyn_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_ebeveyn_yatak_odasi_3_plan.jpg) |
| cam_r_L1_hol_1 | r_L1_hol | L1 | cycles | room | - | - | info | - | - | +6.83 | D3 A2 | 0 | no | [preview](cam_r_L1_hol_1_final_preview.jpg) [plan](cam_r_L1_hol_1_plan.jpg) |
| cam_r_L1_hol_2 | r_L1_hol | L1 | cycles | room | - | - | ok | - | - | +7.00 | D3 | 0 | no | [preview](cam_r_L1_hol_2_final_preview.jpg) [plan](cam_r_L1_hol_2_plan.jpg) |
| cam_r_L1_hol_3 | r_L1_hol | L1 | cycles | room | - | - | info | - | - | +6.67 | D4 A2 | 0 | no | [preview](cam_r_L1_hol_3_final_preview.jpg) [plan](cam_r_L1_hol_3_plan.jpg) |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | L1 | polished | - | a2 s 0.25 canny x0.8 | accept | ok | ok | not preferred 0/4 | +3.67 | A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_1_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_1_plan.jpg) |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | ok | not preferred 0/4 | +3.67 | A3 | 0 | no | [preview](cam_r_L1_yatak_odasi_2_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_2_plan.jpg) |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | L1 | polished | - | a1 s 0.375 geometry x0.8 | accept | ok | info | not preferred 0/4 | +4.00 | D1 A2 | 0 | no | [preview](cam_r_L1_yatak_odasi_3_final_preview.jpg) [plan](cam_r_L1_yatak_odasi_3_plan.jpg) |

polish attempt: the polish candidate (used only when final is polished). ids: D from_documents, A added_by_ai, R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.

### Why Cycles

- cam_r_L0_yatak_odasi_1: room: polish: room
- cam_r_L0_yatak_odasi_2: room: polish: room
- cam_r_L0_yatak_odasi_3: room: polish: room
- cam_r_L1_hol_1: room: polish: room
- cam_r_L1_hol_2: room: polish: room
- cam_r_L1_hol_3: room: polish: room

## Mismatches (never auto-fixed)

| view | image | result | id | type | role | source | evidence | counted | notes |
|---|---|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | cycles | disputed | f_L0_010 | toilet | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector 1.00 | info | - |
| cam_r_L0_banyo_2 | cycles | missing | f_L0_010 | toilet | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector 1.00 | info | - |
| cam_r_L0_banyo_2 | polished | missing | f_L0_010 | toilet | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector 1.00 | info | - |
| cam_r_L0_banyo_3 | cycles | missing | f_L0_012 | shower | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | info | - |
| cam_r_L0_banyo_3 | cycles | missing | f_L0_010 | toilet | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector 1.00 | info | - |
| cam_r_L0_banyo_3 | cycles | missing | f_L0_011 | washbasin | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector 1.00 | info | - |
| cam_r_L0_banyo_3 | polished | missing | f_L0_012 | shower | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:120 DUS vector 1.00 | info | - |
| cam_r_L0_banyo_3 | polished | missing | f_L0_010 | toilet | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector 1.00 | info | - |
| cam_r_L0_banyo_3 | polished | missing | f_L0_011 | washbasin | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector 1.00 | info | - |
| cam_r_L0_hol_1 | cycles | missing | d_L0_005 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector 1.00 | info | - |
| cam_r_L0_hol_1 | cycles | disputed | f_L0_014 | dresser | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_hol_1 | polished | missing | d_L0_005 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector 1.00 | info | - |
| cam_r_L0_hol_2 | cycles | disputed | d_L0_005 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector 1.00 | info | - |
| cam_r_L0_hol_2 | cycles | disputed | d_L0_002 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:F6 KAPI_90 vector 1.00 | info | - |
| cam_r_L0_hol_2 | polished | disputed | d_L0_005 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector 1.00 | info | - |
| cam_r_L0_hol_2 | polished | disputed | d_L0_002 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:F6 KAPI_90 vector 1.00 | info | - |
| cam_r_L0_hol_3 | cycles | disputed | d_L0_005 | door | optional | from_documents | zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector 1.00 | info | - |
| cam_r_L0_hol_3 | cycles | missing | f_L0_014 | dresser | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_hol_3 | polished | disputed | f_L0_014 | dresser | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_mutfak_1 | cycles | missing | f_L0_016 | sink_kitchen | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_mutfak_1 | polished | missing | f_L0_016 | sink_kitchen | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_mutfak_2 | cycles | missing | f_L0_016 | sink_kitchen | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L0_salon_1 | cycles | missing | f_L0_002 | table_coffee | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:10C SEHPA vector 1.00 | info | - |
| cam_r_L0_salon_1 | polished | missing | f_L0_002 | table_coffee | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:10C SEHPA vector 1.00 | info | - |
| cam_r_L0_salon_2 | cycles | disputed | f_L0_001 | sofa | optional | from_documents | zemin_kat.dxf MOBILYA INSERT:10A KANEPE_3LU vector 1.00 | info | - |
| cam_r_L1_banyo_1 | cycles | disputed | f_L1_013 | shower | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | cycles | missing | f_L1_015 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | cycles | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_banyo_1 | polished | disputed | f_L1_013 | shower | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | polished | missing | f_L1_015 | washbasin | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_1 | polished | door count more | door | door | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_banyo_2 | cycles | missing | f_L1_013 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_2 | polished | missing | f_L1_013 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | disputed | f_L1_013 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | cycles | window count more | window | window | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_banyo_3 | polished | missing | f_L1_013 | shower | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_banyo_3 | polished | window count more | window | window | - | - | - | yes | expected [0, 0], passes {'qwen': 1, 'glm': 1} |
| cam_r_L1_cocuk_odasi_1 | cycles | disputed | f_L1_016 | bed_single | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_cocuk_odasi_1 | polished | disputed | f_L1_016 | bed_single | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_cocuk_odasi_2 | cycles | missing | f_L1_019 | chair | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_cocuk_odasi_2 | polished | disputed | f_L1_019 | chair | optional | added_by_ai | building.json ai 0.90 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | cycles | missing | f_L1_004 | wardrobe | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | cycles | disputed | f_L1_003 | nightstand | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | cycles | disputed | f_L1_002 | nightstand | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | polished | missing | f_L1_004 | wardrobe | optional | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | polished | disputed | f_L1_003 | nightstand | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_ebeveyn_yatak_odasi_2 | polished | disputed | f_L1_002 | nightstand | required | added_by_ai | building.json ai 0.60 | info | added_by_ai: render/polish issue, not a document conflict |
| cam_r_L1_hol_1 | cycles | missing | d_L1_004 | door | optional | from_documents | 1_kat.pdf p1 path:15 vector 1.00 | info | - |
| cam_r_L1_hol_3 | cycles | missing | d_L1_002 | door | optional | from_documents | 1_kat.pdf p1 path:11 vector 1.00 | info | - |
| cam_r_L1_hol_3 | cycles | missing | d_L1_004 | door | optional | from_documents | 1_kat.pdf p1 path:15 vector 1.00 | info | - |

## Needs review

- cam_r_L1_banyo_1: door count more than expected [0, 0]: {'qwen': 1, 'glm': 1}
- cam_r_L1_banyo_3: window count more than expected [0, 0]: {'qwen': 1, 'glm': 1}

## Building JSON: unverified items and conflicts

Status: ok.

Unverified items:

None.

Conflicts:

None.

## Rooms mixing polished and Cycles views

None.

Polish room rule (wall colour within ΔE 5 per room) downgraded: r_L0_yatak_odasi (rung None), r_L1_hol (rung None).

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

Assets: textures CC0 x 3; furniture/decor models CC0 x 22 (parametric meshes need no licence).

## Warnings

None.
