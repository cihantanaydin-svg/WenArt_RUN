# Vision check report: synthetic-01

29 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.75 misses >= 0.8; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 4 info, 2 mismatch, 23 ok |
| polished images checked | 25 |
| polished rejected | vision_check 2 |
| views needing review | 2 |
| polished preferred (>= 3 of 4 votes) | 0 of 25 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_banyo_2 | r_L0_banyo | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L0_banyo_3 | r_L0_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L0_hol_1 | r_L0_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_hol_2 | r_L0_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | ok | ok | vision_check | no (0/4) | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | ok | info | kept | no (0/4) | no | - |
| cam_r_L0_salon_1 | r_L0_salon | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_salon_2 | r_L0_salon | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_salon_3 | r_L0_salon | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_banyo_1 | r_L1_banyo | ok | info | kept | no (0/4) | no | - |
| cam_r_L1_banyo_2 | r_L1_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_banyo_3 | r_L1_banyo | ok | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | ok | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | mismatch | - | - | - | yes | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_1 | r_L1_hol | ok | ok | vision_check | no (0/4) | no | - |
| cam_r_L1_hol_2 | r_L1_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_3 | r_L1_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | ok | ok | kept | no (0/4) | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_banyo_2: f_L0_012 (shower, from_documents, required; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): disputed (not confirmed)
- cam_r_L0_banyo_2: door count more than [0, 1] ({'qwen': 2, 'glm': 2})
- cam_r_L0_banyo_3: f_L0_012 (shower, from_documents, optional; evidence zemin_kat.dxf MOBILYA INSERT:120 DUS vector): missing (confirmed)
- cam_r_L1_cocuk_odasi_2: f_L1_018 (wardrobe, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_cocuk_odasi_3: door count more than [0, 0] ({'qwen': 1, 'glm': 1})

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

- cam_r_L0_mutfak_1: vision_check: added_by_polish furniture (detector: bathtub 0.12, confirmed by score) at [2, 494, 205, 1011]
- cam_r_L1_hol_1: vision_check: added_by_polish window (detector: window 0.13, confirmed by score) at [2, 0, 619, 405]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L0_banyo_1 | ok | none |
| cam_r_L0_banyo_2 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_banyo_3 | ok | none |
| cam_r_L0_hol_1 | ok | none |
| cam_r_L0_hol_2 | ok | none |
| cam_r_L0_mutfak_1 | added_by_polish | bathtub 0.12 at [2, 494, 205, 1011] (score) (+ 2 unconfirmed or decor) |
| cam_r_L0_mutfak_2 | ok | none (+ 3 unconfirmed or decor) |
| cam_r_L0_mutfak_3 | ok | none |
| cam_r_L0_salon_1 | ok | none |
| cam_r_L0_salon_2 | ok | none |
| cam_r_L0_salon_3 | ok | none |
| cam_r_L0_yatak_odasi_1 | ok | none |
| cam_r_L0_yatak_odasi_2 | ok | none |
| cam_r_L0_yatak_odasi_3 | ok | none |
| cam_r_L1_banyo_1 | ok | none |
| cam_r_L1_banyo_2 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L1_ebeveyn_yatak_odasi_1 | ok | none |
| cam_r_L1_ebeveyn_yatak_odasi_2 | ok | none |
| cam_r_L1_ebeveyn_yatak_odasi_3 | ok | none |
| cam_r_L1_hol_1 | added_by_polish | window 0.13 at [2, 0, 619, 405] (score) (+ 1 unconfirmed or decor) |
| cam_r_L1_hol_2 | ok | none |
| cam_r_L1_hol_3 | ok | none |
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
| cam_r_L0_mutfak_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_salon_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_yatak_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_yatak_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_yatak_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_banyo_2 | polished | 0 / 4 of 4 | no |
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
| cam_r_L0_banyo_1 | insertion:win_L0_006 | yes | no |
| cam_r_L0_banyo_1 | removal:win_L0_006 | yes | yes |
| cam_r_L0_hol_1 | insertion:d_L0_001 | no | no |
| cam_r_L0_hol_1 | removal:d_L0_001 | no | no |
| cam_r_L0_salon_1 | swap:f_L0_001 | yes | yes |
| cam_r_L0_yatak_odasi_1 | insertion:f_L0_006 | no | no |
| cam_r_L0_yatak_odasi_1 | removal:f_L0_006 | yes | yes |
| cam_r_L0_yatak_odasi_1 | swap:f_L0_006 | yes | no |
| cam_r_L1_cocuk_odasi_1 | insertion:f_L1_018 | yes | no |
| cam_r_L1_cocuk_odasi_1 | insertion:win_L1_004 | yes | no |
| cam_r_L1_cocuk_odasi_1 | removal:f_L1_018 | yes | yes |
| cam_r_L1_cocuk_odasi_1 | removal:win_L1_004 | yes | yes |
| cam_r_L1_ebeveyn_yatak_odasi_1 | insertion:f_L1_001 | no | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | removal:f_L1_001 | yes | yes |
| cam_r_L1_ebeveyn_yatak_odasi_1 | swap:f_L1_001 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_3 | insertion:win_L1_001 | no | no |
| cam_r_L1_ebeveyn_yatak_odasi_3 | removal:win_L1_001 | yes | yes |
| cam_r_L1_yatak_odasi_3 | insertion:d_L1_003 | no | no |
| cam_r_L1_yatak_odasi_3 | removal:d_L1_003 | no | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.069 | - |
| removal flagged | 0.750 | >= 0.8 |
| removal confirmed | 0.750 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (8 controls) | 0.875 / 0.750 / 0.750 | - |
| type swap confirmed | 0.333 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.018 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.75 misses >= 0.8
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
