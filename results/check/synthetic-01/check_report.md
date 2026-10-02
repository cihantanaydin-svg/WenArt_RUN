# Vision check report: synthetic-01

30 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 17 info, 2 mismatch, 11 ok |
| polished images checked | 24 |
| polished rejected | none |
| views needing review | 2 |
| polished preferred (>= 3 of 4 votes) | 0 of 24 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | info | ok | kept | no (1/4) | no | - |
| cam_r_L0_banyo_2 | r_L0_banyo | info | info | kept | no (2/4) | no | - |
| cam_r_L0_banyo_3 | r_L0_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L0_hol_1 | r_L0_hol | info | info | kept | no (0/4) | no | - |
| cam_r_L0_hol_2 | r_L0_hol | info | info | kept | no (0/4) | no | - |
| cam_r_L0_hol_3 | r_L0_hol | info | info | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | info | info | kept | no (1/4) | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | info | info | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_salon_1 | r_L0_salon | info | info | kept | no (0/4) | no | - |
| cam_r_L0_salon_2 | r_L0_salon | info | ok | kept | no (0/4) | no | - |
| cam_r_L0_salon_3 | r_L0_salon | ok | info | kept | no (1/4) | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L1_banyo_1 | r_L1_banyo | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L1_banyo_2 | r_L1_banyo | info | info | kept | no (2/4) | no | - |
| cam_r_L1_banyo_3 | r_L1_banyo | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | ok | info | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_hol_1 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_hol_2 | r_L1_hol | ok | - | - | - | no | - |
| cam_r_L1_hol_3 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | ok | info | kept | no (0/4) | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_banyo_1: f_L0_010 (toilet, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector): disputed (not confirmed)
- cam_r_L0_banyo_2: f_L0_010 (toilet, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector): missing (confirmed)
- cam_r_L0_banyo_3: f_L0_010 (toilet, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:11C KLOZET vector): missing (confirmed)
- cam_r_L0_banyo_3: f_L0_011 (washbasin, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector): missing (confirmed)
- cam_r_L0_banyo_3: f_L0_012 (shower, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): missing (confirmed)
- cam_r_L0_hol_1: d_L0_005 (door, from_documents, optional; evidence zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector): missing (confirmed)
- cam_r_L0_hol_1: f_L0_014 (dresser, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_hol_2: d_L0_002 (door, from_documents, optional; evidence zemin_kat.dxf KAPI INSERT:F6 KAPI_90 vector): disputed (not confirmed)
- cam_r_L0_hol_2: d_L0_005 (door, from_documents, optional; evidence zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector): disputed (not confirmed)
- cam_r_L0_hol_3: d_L0_005 (door, from_documents, optional; evidence zemin_kat.dxf KAPI INSERT:FC KAPI_80 vector): disputed (not confirmed)
- cam_r_L0_hol_3: f_L0_014 (dresser, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L0_mutfak_1: f_L0_016 (sink_kitchen, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L0_mutfak_2: f_L0_016 (sink_kitchen, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L0_salon_1: f_L0_002 (table_coffee, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:10C SEHPA vector): missing (confirmed)
- cam_r_L0_salon_2: f_L0_001 (sofa, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:10A KANEPE_3LU vector): disputed (not confirmed)
- cam_r_L1_banyo_1: f_L1_013 (shower, added_by_ai, required; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_banyo_1: f_L1_015 (washbasin, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_banyo_1: door count more than [0, 0] ({'qwen': 1, 'glm': 1})
- cam_r_L1_banyo_2: f_L1_013 (shower, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_banyo_3: f_L1_013 (shower, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_banyo_3: window count more than [0, 0] ({'qwen': 1, 'glm': 1})
- cam_r_L1_cocuk_odasi_1: f_L1_016 (bed_single, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_cocuk_odasi_2: f_L1_019 (chair, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_ebeveyn_yatak_odasi_2: f_L1_002 (nightstand, added_by_ai, required; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_ebeveyn_yatak_odasi_2: f_L1_003 (nightstand, added_by_ai, required; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_ebeveyn_yatak_odasi_2: f_L1_004 (wardrobe, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_hol_1: d_L1_004 (door, from_documents, optional; evidence 1_kat.pdf p1 path:15 vector): missing (confirmed)
- cam_r_L1_hol_3: d_L1_002 (door, from_documents, optional; evidence 1_kat.pdf p1 path:11 vector): missing (confirmed)
- cam_r_L1_hol_3: d_L1_004 (door, from_documents, optional; evidence 1_kat.pdf p1 path:15 vector): missing (confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

None.

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L0_banyo_1 | polished | 1 / 4 of 4 | no |
| cam_r_L0_banyo_2 | polished | 2 / 4 of 4 | no |
| cam_r_L0_banyo_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_2 | sweep:a9 | 1 / 4 of 4 | no |
| cam_r_L0_hol_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_1 | polished | 1 / 4 of 4 | no |
| cam_r_L0_mutfak_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_2 | sweep:a8 | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_2 | sweep:a9 | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_3 | polished | 1 / 4 of 4 | no |
| cam_r_L0_salon_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_3 | polished | 1 / 4 of 4 | no |
| cam_r_L1_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_banyo_2 | polished | 2 / 4 of 4 | no |
| cam_r_L1_banyo_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_cocuk_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_cocuk_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_cocuk_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | sweep:a10 | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_1 | sweep:a10 | 0 / 4 of 4 | no |
| cam_r_L1_hol_1 | sweep:a8 | 0 / 4 of 4 | no |
| cam_r_L1_yatak_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_yatak_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_yatak_odasi_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

- cam_r_L0_hol_2 plan_ab:cam_r_L0_hol_2: not computed for qwen, glm
- cam_r_L0_hol_2 plan_ab:removal:d_L0_004: not computed for qwen, glm
- cam_r_L0_mutfak_2 plan_ab:cam_r_L0_mutfak_2: not computed for qwen, glm
- cam_r_L0_mutfak_2 plan_ab:removal:f_L0_018: not computed for qwen, glm
- cam_r_L0_salon_1 plan_ab:cam_r_L0_salon_1: not computed for qwen, glm
- cam_r_L0_salon_1 plan_ab:removal:win_L0_002: not computed for qwen, glm
- cam_r_L0_salon_2 plan_ab:cam_r_L0_salon_2: not computed for qwen, glm
- cam_r_L0_salon_2 plan_ab:removal:f_L0_003: not computed for qwen, glm
- cam_r_L0_yatak_odasi_1 plan_ab:cam_r_L0_yatak_odasi_1: not computed for qwen, glm
- cam_r_L0_yatak_odasi_1 plan_ab:removal:win_L0_003: not computed for qwen, glm
- cam_r_L0_yatak_odasi_2 plan_ab:cam_r_L0_yatak_odasi_2: not computed for qwen, glm
- cam_r_L0_yatak_odasi_2 plan_ab:removal:f_L0_009: not computed for qwen, glm
- cam_r_L1_ebeveyn_yatak_odasi_1 plan_ab:cam_r_L1_ebeveyn_yatak_odasi_1: not computed for qwen, glm
- cam_r_L1_ebeveyn_yatak_odasi_1 plan_ab:removal:win_L1_001: not computed for qwen, glm
- cam_r_L1_ebeveyn_yatak_odasi_2 plan_ab:cam_r_L1_ebeveyn_yatak_odasi_2: not computed for qwen, glm
- cam_r_L1_hol_1 plan_ab:cam_r_L1_hol_1: not computed for qwen, glm

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_hol_2 | insertion:d_L0_004 | no | no |
| cam_r_L0_hol_2 | plan_ab:removal:d_L0_004 | no | no |
| cam_r_L0_hol_2 | removal:d_L0_004 | yes | no |
| cam_r_L0_mutfak_2 | insertion:f_L0_018 | yes | no |
| cam_r_L0_mutfak_2 | plan_ab:removal:f_L0_018 | no | no |
| cam_r_L0_mutfak_2 | removal:f_L0_018 | yes | no |
| cam_r_L0_salon_1 | insertion:win_L0_002 | no | no |
| cam_r_L0_salon_1 | plan_ab:removal:win_L0_002 | no | no |
| cam_r_L0_salon_1 | removal:win_L0_002 | yes | yes |
| cam_r_L0_salon_2 | insertion:f_L0_003 | yes | no |
| cam_r_L0_salon_2 | plan_ab:removal:f_L0_003 | no | no |
| cam_r_L0_salon_2 | removal:f_L0_003 | yes | yes |
| cam_r_L0_salon_3 | swap:f_L0_004 | yes | yes |
| cam_r_L0_yatak_odasi_1 | insertion:win_L0_003 | yes | no |
| cam_r_L0_yatak_odasi_1 | plan_ab:removal:win_L0_003 | no | no |
| cam_r_L0_yatak_odasi_1 | removal:win_L0_003 | yes | yes |
| cam_r_L0_yatak_odasi_2 | insertion:f_L0_009 | yes | no |
| cam_r_L0_yatak_odasi_2 | plan_ab:removal:f_L0_009 | no | no |
| cam_r_L0_yatak_odasi_2 | removal:f_L0_009 | yes | yes |
| cam_r_L1_ebeveyn_yatak_odasi_1 | insertion:win_L1_001 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | plan_ab:removal:win_L1_001 | no | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | removal:win_L1_001 | yes | yes |
| cam_r_L1_hol_2 | insertion:d_L1_004 | no | no |
| cam_r_L1_hol_2 | plan_ab:removal:d_L1_004 | yes | no |
| cam_r_L1_hol_2 | removal:d_L1_004 | yes | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.067 | - |
| removal flagged | 1.000 | >= 0.8 |
| removal confirmed | 0.625 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| type swap confirmed | 1.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.068 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 10 camera(s): FA missing 0.000 -> 0.000, removal confirmed 0.000 -> 0.000.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

- qwen: stale answer for plan_ab|cam_r_L0_yatak_odasi_2|plan_ab:cam_r_L0_yatak_odasi_2 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_yatak_odasi_2|plan_ab:cam_r_L0_yatak_odasi_2 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_salon_2|plan_ab:cam_r_L0_salon_2 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_salon_2|plan_ab:cam_r_L0_salon_2 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_mutfak_2|plan_ab:cam_r_L0_mutfak_2 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_mutfak_2|plan_ab:cam_r_L0_mutfak_2 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L1_ebeveyn_yatak_odasi_1|plan_ab:cam_r_L1_ebeveyn_yatak_odasi_1 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L1_ebeveyn_yatak_odasi_1|plan_ab:cam_r_L1_ebeveyn_yatak_odasi_1 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_yatak_odasi_1|plan_ab:cam_r_L0_yatak_odasi_1 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_yatak_odasi_1|plan_ab:cam_r_L0_yatak_odasi_1 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_salon_1|plan_ab:cam_r_L0_salon_1 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_salon_1|plan_ab:cam_r_L0_salon_1 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_hol_2|plan_ab:cam_r_L0_hol_2 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_hol_2|plan_ab:cam_r_L0_hol_2 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L1_hol_1|plan_ab:cam_r_L1_hol_1 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L1_hol_1|plan_ab:cam_r_L1_hol_1 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L1_ebeveyn_yatak_odasi_2|plan_ab:cam_r_L1_ebeveyn_yatak_odasi_2 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L1_ebeveyn_yatak_odasi_2|plan_ab:cam_r_L1_ebeveyn_yatak_odasi_2 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_yatak_odasi_2|plan_ab:removal:f_L0_009 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_yatak_odasi_2|plan_ab:removal:f_L0_009 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_salon_2|plan_ab:removal:f_L0_003 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_salon_2|plan_ab:removal:f_L0_003 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_mutfak_2|plan_ab:removal:f_L0_018 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_mutfak_2|plan_ab:removal:f_L0_018 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L1_ebeveyn_yatak_odasi_1|plan_ab:removal:win_L1_001 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L1_ebeveyn_yatak_odasi_1|plan_ab:removal:win_L1_001 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_yatak_odasi_1|plan_ab:removal:win_L0_003 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_yatak_odasi_1|plan_ab:removal:win_L0_003 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_salon_1|plan_ab:removal:win_L0_002 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_salon_1|plan_ab:removal:win_L0_002 (inputs changed); not used
- qwen: stale answer for plan_ab|cam_r_L0_hol_2|plan_ab:removal:d_L0_004 (inputs changed); not used
- glm: stale answer for plan_ab|cam_r_L0_hol_2|plan_ab:removal:d_L0_004 (inputs changed); not used
