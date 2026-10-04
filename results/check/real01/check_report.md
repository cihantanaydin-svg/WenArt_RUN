# Vision check report: real01

20 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.5714 misses >= 0.8; removal_confirmed 0.5714 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 7 info, 13 ok |
| polished images checked | 0 |
| polished rejected | none |
| views needing review | 0 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | info | - | - | - | no | - |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | info | - | - | - | no | - |
| cam_r_L0_bed_room_1 | r_L0_bed_room | info | - | - | - | no | - |
| cam_r_L0_bed_room_2 | r_L0_bed_room | ok | - | - | - | no | - |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | info | - | - | - | no | - |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_3 | r_L0_bed_room | info | - | - | - | no | - |
| cam_r_L0_dining_1 | r_L0_dining | ok | - | - | - | no | - |
| cam_r_L0_dining_2 | r_L0_dining | ok | - | - | - | no | - |
| cam_r_L0_dining_3 | r_L0_dining | ok | - | - | - | no | - |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | ok | - | - | - | no | - |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | ok | - | - | - | no | - |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | ok | - | - | - | no | - |
| cam_r_L0_kitchen_1 | r_L0_kitchen | ok | - | - | - | no | - |
| cam_r_L0_kitchen_2 | r_L0_kitchen | ok | - | - | - | no | - |
| cam_r_L0_kitchen_3 | r_L0_kitchen | ok | - | - | - | no | - |
| cam_r_L0_room_1 | r_L0_room | info | - | - | - | no | - |
| cam_r_L0_room_2 | r_L0_room | ok | - | - | - | no | - |
| cam_r_L0_room_3 | r_L0_room | info | - | - | - | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_bath_toilet_2: f_L0_022 (washbasin, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_bed_room_2_1: dec_L0_015 (rug, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

None.

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

## Realism preference (info only)

None.

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_bed_room_2_2 | insertion:f_L0_005 | yes | no |
| cam_r_L0_bed_room_2_2 | removal:f_L0_005 | no | no |
| cam_r_L0_bed_room_2_3 | insertion:win_L0_004 | no | no |
| cam_r_L0_bed_room_2_3 | removal:win_L0_004 | yes | yes |
| cam_r_L0_drawing_room_1 | insertion:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_1 | insertion:win_L0_002 | no | no |
| cam_r_L0_drawing_room_1 | removal:f_L0_017 | yes | yes |
| cam_r_L0_drawing_room_1 | removal:win_L0_002 | yes | yes |
| cam_r_L0_drawing_room_1 | swap:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_3 | insertion:d_L0_003 | yes | no |
| cam_r_L0_drawing_room_3 | removal:d_L0_003 | no | no |
| cam_r_L0_kitchen_1 | insertion:f_L0_002 | no | no |
| cam_r_L0_kitchen_1 | insertion:win_L0_006 | no | no |
| cam_r_L0_kitchen_1 | removal:f_L0_002 | no | no |
| cam_r_L0_kitchen_1 | removal:win_L0_006 | yes | yes |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.571 | >= 0.8 |
| removal confirmed | 0.571 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| type swap confirmed | 0.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.5714 misses >= 0.8
- removal_confirmed 0.5714 misses >= 0.6
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

- cam_r_L0_bath_toilet_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_dining_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_dining_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_dining_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_drawing_room_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_drawing_room_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_drawing_room_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_kitchen_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_kitchen_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_kitchen_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_kitchen_1: detect/cam_r_L0_kitchen_1.json cycles was made from another image (sha256); not used
- cam_r_L0_drawing_room_1: detect/cam_r_L0_drawing_room_1.json cycles was made from another image (sha256); not used
- cam_r_L0_bed_room_2_2: detect/cam_r_L0_bed_room_2_2.json cycles was made from another image (sha256); not used
- cam_r_L0_drawing_room_3: detect/cam_r_L0_drawing_room_3.json cycles was made from another image (sha256); not used
- cam_r_L0_drawing_room_3: detect/cam_r_L0_drawing_room_3.json control:d_L0_003 was made from another image (sha256); not used
