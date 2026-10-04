# Vision check report: synthetic-02

11 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.6667 misses >= 0.8; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 2 info, 1 mismatch, 8 ok |
| polished images checked | 0 |
| polished rejected | none |
| views needing review | 1 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_antre_1 | r_L0_antre | ok | - | - | - | no | - |
| cam_r_L0_banyo_1 | r_L0_banyo | info | - | - | - | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | ok | - | - | - | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | ok | - | - | - | no | - |
| cam_r_L0_salon_1 | r_L0_salon | ok | - | - | - | no | - |
| cam_r_L0_salon_2 | r_L0_salon | ok | - | - | - | no | - |
| cam_r_L0_salon_3 | r_L0_salon | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | mismatch | - | - | - | yes | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | ok | - | - | - | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_banyo_1: f_L0_008 (shower, from_documents, optional; evidence plan_scan.png p1 seg:50,seg:59,seg:70,seg:94 raster): missing (confirmed)
- cam_r_L0_yatak_odasi_1: f_L0_007 (unknown, from_documents, optional; evidence plan_scan.png p1 seg:182-184,seg:205,seg:207 raster): disputed (not confirmed)
- cam_r_L0_yatak_odasi_1: door count more than [0, 0] ({'qwen': 1, 'glm': 1})

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

None.

## Added-object detector

Not run for this project (no `detect/` folder).

## Realism preference (info only)

None.

## Unreliable or incomplete checks

- cam_r_L0_mutfak_2 cycles: decoy seen by qwen (unreliable)

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_salon_3 | insertion:win_L0_003 | yes | no |
| cam_r_L0_salon_3 | removal:win_L0_003 | yes | yes |
| cam_r_L0_yatak_odasi_1 | insertion:win_L0_002 | no | no |
| cam_r_L0_yatak_odasi_1 | removal:win_L0_002 | yes | yes |
| cam_r_L0_yatak_odasi_2 | insertion:d_L0_004 | no | no |
| cam_r_L0_yatak_odasi_2 | removal:d_L0_004 | no | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.091 | - |
| removal flagged | 0.667 | >= 0.8 |
| removal confirmed | 0.667 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| type swap confirmed | - | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.091 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.6667 misses >= 0.8
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
