# Vision check report: synthetic-04

14 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged None misses >= 0.8 (no data); removal_confirmed None misses >= 0.6 (no data); insertion None misses >= 0.6 (no data)): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 4 info, 10 ok |
| polished images checked | 11 |
| polished rejected | check_incomplete 1 |
| views needing review | 0 |
| polished preferred (>= 3 of 4 votes) | 2 of 11 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L3_banyo_1 | r_L3_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_banyo_2 | r_L3_banyo | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_cocuk_odasi_1 | r_L3_cocuk_odasi | info | info | check_incomplete | no (0/4) | no | - |
| cam_r_L3_cocuk_odasi_2 | r_L3_cocuk_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L3_cocuk_odasi_3 | r_L3_cocuk_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_hol_1 | r_L3_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_hol_2 | r_L3_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_hol_3 | r_L3_hol | ok | ok | kept | no (0/4) | no | - |
| cam_r_L3_salon_mutfak_1 | r_L3_salon_mutfak | info | info | kept | no (2/4) | no | - |
| cam_r_L3_salon_mutfak_2 | r_L3_salon_mutfak | info | info | kept | yes (3/4) | no | - |
| cam_r_L3_salon_mutfak_3 | r_L3_salon_mutfak | ok | ok | kept | yes (3/4) | no | - |
| cam_r_L3_yatak_odasi_1 | r_L3_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L3_yatak_odasi_2 | r_L3_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L3_yatak_odasi_3 | r_L3_yatak_odasi | ok | - | - | - | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

- cam_r_L3_cocuk_odasi_1: check_incomplete: polished: unreliable (decoy seen): glm; cycles: unreliable (decoy seen): glm

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L3_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L3_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L3_cocuk_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L3_cocuk_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L3_cocuk_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L3_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L3_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L3_hol_3 | polished | 0 / 4 of 4 | no |
| cam_r_L3_salon_mutfak_1 | polished | 2 / 4 of 4 | no |
| cam_r_L3_salon_mutfak_2 | polished | 3 / 4 of 4 | yes |
| cam_r_L3_salon_mutfak_3 | polished | 3 / 4 of 4 | yes |

## Unreliable or incomplete checks

- cam_r_L3_cocuk_odasi_1 cycles: decoy seen by glm (unreliable)
- cam_r_L3_cocuk_odasi_1 polished: decoy seen by glm (unreliable)

## Controls

None.

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | - | >= 0.8 |
| removal confirmed | - | >= 0.6 |
| insertion detected | - | >= 0.6 |
| type swap confirmed | - | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.071 / 0.000 | decoy <= 0.1 |

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
