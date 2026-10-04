# Vision check report: synthetic-01

29 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 10 info, 1 mismatch, 18 ok |
| polished images checked | 19 |
| polished rejected | none |
| views needing review | 1 |
| polished preferred (>= 3 of 4 votes) | 0 of 19 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L0_banyo_2 | r_L0_banyo | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L0_banyo_3 | r_L0_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L0_hol_1 | r_L0_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_hol_2 | r_L0_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | ok | - | - | - | no | - |
| cam_r_L0_salon_1 | r_L0_salon | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_salon_2 | r_L0_salon | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_salon_3 | r_L0_salon | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L1_banyo_1 | r_L1_banyo | info | - | - | - | no | - |
| cam_r_L1_banyo_2 | r_L1_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_banyo_3 | r_L1_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | ok | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | ok | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_1 | r_L1_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_2 | r_L1_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_3 | r_L1_hol | info | info | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_banyo_2: f_L0_011 (washbasin, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:11E LAVABO vector): disputed (not confirmed)
- cam_r_L0_banyo_2: f_L0_012 (shower, from_documents, required; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): missing (confirmed)
- cam_r_L0_banyo_2: f_L0_013 (washing_machine, from_documents, required; evidence zemin_kat.dxf MOBILYA INSERT:122 CAMASIR_MAK vector): disputed (not confirmed)
- cam_r_L0_banyo_3: f_L0_012 (shower, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): missing (confirmed)
- cam_r_L0_mutfak_1: f_L0_016 (sink_kitchen, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_cocuk_odasi_1: f_L1_016 (bed_single, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_cocuk_odasi_1: f_L1_020 (bookshelf, added_by_ai, required; evidence building.json ai): disputed (not confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

None.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L0_banyo_1 | ok | none |
| cam_r_L0_banyo_2 | ok | none |
| cam_r_L0_banyo_3 | ok | none |
| cam_r_L0_hol_1 | ok | none |
| cam_r_L0_hol_2 | ok | none |
| cam_r_L0_salon_1 | ok | none |
| cam_r_L0_salon_2 | ok | none |
| cam_r_L0_salon_3 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L1_banyo_2 | ok | none |
| cam_r_L1_banyo_3 | ok | none |
| cam_r_L1_ebeveyn_yatak_odasi_1 | ok | none |
| cam_r_L1_ebeveyn_yatak_odasi_2 | ok | none |
| cam_r_L1_ebeveyn_yatak_odasi_3 | ok | none |
| cam_r_L1_hol_1 | ok | none |
| cam_r_L1_hol_2 | ok | none (+ 2 unconfirmed or decor) |
| cam_r_L1_hol_3 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L1_yatak_odasi_1 | ok | none |
| cam_r_L1_yatak_odasi_2 | ok | none |
| cam_r_L1_yatak_odasi_3 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L0_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_banyo_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_3 | polished | 0 / 4 of 4 | no |
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

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_mutfak_1 | insertion:f_L0_018 | no | no |
| cam_r_L0_mutfak_1 | removal:f_L0_018 | yes | yes |
| cam_r_L0_salon_1 | insertion:f_L0_001 | yes | no |
| cam_r_L0_salon_1 | removal:f_L0_001 | yes | yes |
| cam_r_L0_salon_1 | swap:f_L0_001 | yes | no |
| cam_r_L0_salon_2 | insertion:win_L0_001 | yes | no |
| cam_r_L0_salon_2 | removal:win_L0_001 | yes | yes |
| cam_r_L1_cocuk_odasi_1 | insertion:d_L1_002 | no | no |
| cam_r_L1_cocuk_odasi_1 | removal:d_L1_002 | no | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | swap:f_L1_005 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | insertion:win_L1_003 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | removal:win_L1_003 | yes | yes |
| cam_r_L1_hol_2 | insertion:f_L1_006 | yes | no |
| cam_r_L1_hol_2 | removal:f_L1_006 | yes | yes |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.023 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.833 | >= 0.8 |
| removal confirmed | 0.833 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (6 controls) | 1.000 / 0.833 / 0.833 | - |
| type swap confirmed | 0.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.068 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.023 | decoy <= 0.1 |

Missed targets (the check is advisory):
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
