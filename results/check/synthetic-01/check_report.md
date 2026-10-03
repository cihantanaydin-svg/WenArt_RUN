# Vision check report: synthetic-01

29 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged None misses >= 0.8 (no data); removal_confirmed None misses >= 0.6 (no data); insertion None misses >= 0.6 (no data)): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 8 info, 2 mismatch, 19 ok |
| polished images checked | 18 |
| polished rejected | none |
| views needing review | 2 |
| polished preferred (>= 3 of 4 votes) | 0 of 18 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_banyo_2 | r_L0_banyo | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L0_banyo_3 | r_L0_banyo | info | - | - | - | no | - |
| cam_r_L0_hol_1 | r_L0_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_hol_2 | r_L0_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | ok | - | - | - | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | ok | - | - | - | no | - |
| cam_r_L0_salon_1 | r_L0_salon | ok | info | kept | no (1/4) | no | - |
| cam_r_L0_salon_2 | r_L0_salon | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_salon_3 | r_L0_salon | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L1_banyo_1 | r_L1_banyo | info | - | - | - | no | - |
| cam_r_L1_banyo_2 | r_L1_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_banyo_3 | r_L1_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L1_hol_1 | r_L1_hol | ok | info | kept | no (0/4) | no | - |
| cam_r_L1_hol_2 | r_L1_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_3 | r_L1_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | info | info | kept | no (0/4) | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_banyo_2: f_L0_011 (washbasin, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector): disputed (not confirmed)
- cam_r_L0_banyo_2: f_L0_012 (shower, from_documents, required; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): missing (confirmed)
- cam_r_L0_banyo_3: f_L0_012 (shower, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): missing (confirmed)
- cam_r_L1_banyo_1: f_L1_012 (shower, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_banyo_3: f_L1_012 (shower, added_by_ai, required; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_cocuk_odasi_1: f_L1_017 (wardrobe, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_ebeveyn_yatak_odasi_3: door count more than [0, 0] ({'qwen': 1, 'glm': 1})
- cam_r_L1_yatak_odasi_3: f_L1_008 (bed_double, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_yatak_odasi_3: f_L1_011 (chair, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

None.

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L0_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_1 | polished | 1 / 4 of 4 | no |
| cam_r_L0_salon_2 | polished | 1 / 4 of 4 | no |
| cam_r_L0_salon_3 | polished | 1 / 4 of 4 | no |
| cam_r_L1_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_banyo_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_ebeveyn_yatak_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_yatak_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_yatak_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_yatak_odasi_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

None.

## Controls

None.

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.022 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.035 | - |
| removal flagged | - | >= 0.8 |
| removal confirmed | - | >= 0.6 |
| insertion detected | - | >= 0.6 |
| type swap confirmed | - | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.067 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.022 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged None misses >= 0.8 (no data)
- removal_confirmed None misses >= 0.6 (no data)
- insertion None misses >= 0.6 (no data)

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
