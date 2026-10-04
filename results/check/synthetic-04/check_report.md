# Vision check report: synthetic-04

14 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 5 info, 1 mismatch, 8 ok |
| polished images checked | 8 |
| polished rejected | vision_check 1 |
| views needing review | 1 |
| polished preferred (>= 3 of 4 votes) | 0 of 8 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | r_L3_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_banyo_2 | r_L3_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_cocuk_odasi_1 | r_L3_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L3_cocuk_odasi_2 | r_L3_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L3_cocuk_odasi_3 | r_L3_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L3_hol_1 | r_L3_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_hol_2 | r_L3_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_hol_3 | r_L3_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_salon_mutfak_1 | r_L3_salon_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_salon_mutfak_2 | r_L3_salon_mutfak | info | info | vision_check | no (0/4) | no | - |
| cam_r_L3_salon_mutfak_3 | r_L3_salon_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_yatak_odasi_1 | r_L3_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L3_yatak_odasi_2 | r_L3_yatak_odasi | info | - | - | - | no | - |
| cam_r_L3_yatak_odasi_3 | r_L3_yatak_odasi | mismatch | - | - | - | yes | - |

## Mismatches on the Cycles renders

- cam_r_L3_cocuk_odasi_2: f_L3_025 (wardrobe, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L3_cocuk_odasi_3: f_L3_024 (nightstand, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L3_cocuk_odasi_3: f_L3_025 (wardrobe, added_by_ai, optional; evidence building.json ai): missing_or_changed (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L3_yatak_odasi_3: door count more than [0, 0] ({'qwen': 1, 'glm': 1})

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

- cam_r_L3_salon_mutfak_2: vision_check: added_by_polish furniture (detector: sink_kitchen 0.20, confirmed by score) at [1399, 370, 1462, 405]; added_by_polish furniture (detector: fridge 0.15, confirmed by score) at [1352, 311, 1460, 400]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L3_banyo_1 | ok | none |
| cam_r_L3_banyo_2 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L3_hol_1 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L3_hol_2 | ok | none |
| cam_r_L3_hol_3 | ok | none |
| cam_r_L3_salon_mutfak_1 | ok | none |
| cam_r_L3_salon_mutfak_2 | added_by_polish | sink_kitchen 0.20 at [1399, 370, 1462, 405] (score); fridge 0.15 at [1352, 311, 1460, 400] (score) (+ 1 unconfirmed or decor) |
| cam_r_L3_salon_mutfak_3 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L3_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L3_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L3_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L3_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L3_hol_3 | polished | 0 / 4 of 4 | no |
| cam_r_L3_salon_mutfak_1 | polished | 0 / 4 of 4 | no |
| cam_r_L3_salon_mutfak_2 | polished | 0 / 4 of 4 | no |
| cam_r_L3_salon_mutfak_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L3_cocuk_odasi_1 | insertion:win_L3_008 | no | no |
| cam_r_L3_cocuk_odasi_1 | removal:win_L3_008 | yes | no |
| cam_r_L3_salon_mutfak_1 | insertion:win_L3_001 | no | no |
| cam_r_L3_salon_mutfak_1 | removal:win_L3_001 | yes | yes |
| cam_r_L3_salon_mutfak_2 | insertion:d_L3_002 | yes | no |
| cam_r_L3_salon_mutfak_2 | removal:d_L3_002 | no | no |
| cam_r_L3_salon_mutfak_3 | insertion:f_L3_010 | yes | no |
| cam_r_L3_salon_mutfak_3 | removal:f_L3_010 | yes | yes |
| cam_r_L3_salon_mutfak_3 | swap:f_L3_010 | yes | yes |
| cam_r_L3_yatak_odasi_2 | insertion:f_L3_018 | yes | no |
| cam_r_L3_yatak_odasi_2 | removal:f_L3_018 | yes | yes |
| cam_r_L3_yatak_odasi_3 | insertion:win_L3_009 | no | no |
| cam_r_L3_yatak_odasi_3 | removal:win_L3_009 | yes | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.071 | - |
| removal flagged | 0.833 | >= 0.8 |
| removal confirmed | 0.500 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (6 controls) | 1.000 / 1.000 / 1.000 | - |
| type swap confirmed | 1.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_confirmed 0.5 misses >= 0.6
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
