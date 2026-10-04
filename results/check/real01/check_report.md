# Vision check report: real01

20 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_confirmed 0.4 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 7 info, 13 ok |
| polished images checked | 10 |
| polished rejected | none |
| views needing review | 0 |
| polished preferred (>= 3 of 4 votes) | 0 of 10 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | ok | ok | kept | no (2/4) | no | - |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | ok | - | - | - | no | - |
| cam_r_L0_bed_room_1 | r_L0_bed_room | ok | - | - | - | no | - |
| cam_r_L0_bed_room_2 | r_L0_bed_room | info | - | - | - | no | - |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | info | - | - | - | no | - |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_3 | r_L0_bed_room | ok | - | - | - | no | - |
| cam_r_L0_dining_1 | r_L0_dining | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_dining_2 | r_L0_dining | info | info | kept | no (0/4) | no | - |
| cam_r_L0_dining_3 | r_L0_dining | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | info | info | kept | no (0/4) | no | - |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_1 | r_L0_kitchen | ok | info | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_2 | r_L0_kitchen | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_3 | r_L0_kitchen | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_room_1 | r_L0_room | info | - | - | - | no | - |
| cam_r_L0_room_2 | r_L0_room | info | - | - | - | no | - |
| cam_r_L0_room_3 | r_L0_room | info | - | - | - | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

None.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L0_bath_toilet_1 | ok | none |
| cam_r_L0_dining_1 | ok | none |
| cam_r_L0_dining_2 | ok | none |
| cam_r_L0_dining_3 | ok | none |
| cam_r_L0_drawing_room_1 | ok | none |
| cam_r_L0_drawing_room_2 | ok | none |
| cam_r_L0_drawing_room_3 | ok | none |
| cam_r_L0_kitchen_1 | ok | none |
| cam_r_L0_kitchen_2 | ok | none |
| cam_r_L0_kitchen_3 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L0_bath_toilet_1 | polished | 2 / 4 of 4 | no |
| cam_r_L0_dining_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_dining_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_dining_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_drawing_room_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_drawing_room_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_drawing_room_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kitchen_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kitchen_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kitchen_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_bed_room_2_2 | insertion:f_L0_006 | yes | no |
| cam_r_L0_bed_room_2_2 | removal:f_L0_006 | yes | no |
| cam_r_L0_drawing_room_2 | insertion:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_2 | insertion:win_L0_002 | no | no |
| cam_r_L0_drawing_room_2 | removal:f_L0_017 | yes | yes |
| cam_r_L0_drawing_room_2 | removal:win_L0_002 | yes | yes |
| cam_r_L0_drawing_room_2 | swap:f_L0_017 | yes | yes |
| cam_r_L0_drawing_room_3 | insertion:d_L0_003 | yes | no |
| cam_r_L0_drawing_room_3 | removal:d_L0_003 | no | no |
| cam_r_L0_kitchen_1 | insertion:f_L0_001 | no | no |
| cam_r_L0_kitchen_1 | removal:f_L0_001 | yes | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.800 | >= 0.8 |
| removal confirmed | 0.400 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (5 controls) | 0.800 / 0.800 / 0.800 | - |
| type swap confirmed | 1.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_confirmed 0.4 misses >= 0.6
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
