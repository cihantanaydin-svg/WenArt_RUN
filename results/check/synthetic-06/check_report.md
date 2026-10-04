# Vision check report: synthetic-06

17 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.75 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 6 info, 11 ok |
| polished images checked | 17 |
| polished rejected | vision_check 1 |
| views needing review | 0 |
| polished preferred (>= 3 of 4 votes) | 0 of 17 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_1 | r_L0_bath | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_bath_2 | r_L0_bath | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_bed_room_1 | r_L0_bed_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_bed_room_2 | r_L0_bed_room | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_bed_room_3 | r_L0_bed_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_1 | r_L0_kitchen | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_2 | r_L0_kitchen | ok | info | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_3 | r_L0_kitchen | info | info | kept | no (0/4) | no | - |
| cam_r_L0_living_room_1 | r_L0_living_room | info | info | kept | no (0/4) | no | - |
| cam_r_L0_living_room_2 | r_L0_living_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_living_room_3 | r_L0_living_room | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_lobby_1 | r_L0_lobby | info | info | kept | no (0/4) | no | - |
| cam_r_L0_lobby_2 | r_L0_lobby | info | info | kept | no (0/4) | no | - |
| cam_r_L0_lobby_3 | r_L0_lobby | ok | info | kept | no (0/4) | no | - |
| cam_r_L0_master_bed_room_1 | r_L0_master_bed_room | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_master_bed_room_2 | r_L0_master_bed_room | info | info | kept | no (0/4) | no | - |
| cam_r_L0_master_bed_room_3 | r_L0_master_bed_room | info | info | vision_check | no (0/4) | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_kitchen_3: f_L0_007 (chair, from_documents, optional; evidence synthetic-06.dwg INSERT:FF/6/0,INSERT:FF/6/1 DINING-6/CHAIR vector): disputed (not confirmed)
- cam_r_L0_lobby_1: d_L0_003 (door, from_documents, optional; evidence synthetic-06.dwg ARC:CF,LINE:D0 vector): missing (confirmed)
- cam_r_L0_lobby_2: d_L0_003 (door, from_documents, optional; evidence synthetic-06.dwg ARC:CF,LINE:D0 vector): missing (confirmed)
- cam_r_L0_lobby_2: d_L0_004 (door, from_documents, optional; evidence synthetic-06.dwg ARC:D1,LINE:D2 vector): missing (confirmed)
- cam_r_L0_lobby_2: d_L0_005 (door, from_documents, optional; evidence synthetic-06.dwg ARC:D3,LINE:D4 vector): missing (confirmed)
- cam_r_L0_master_bed_room_2: d_L0_004 (door, from_documents, optional; evidence synthetic-06.dwg ARC:D1,LINE:D2 vector): missing (confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Polished images rejected

- cam_r_L0_master_bed_room_3: vision_check: added_by_polish furniture (detector: bathtub 0.10, confirmed by vlm:qwen) at [24, 845, 562, 1015]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L0_bath_1 | ok | none |
| cam_r_L0_bath_2 | ok | none |
| cam_r_L0_bed_room_1 | ok | none |
| cam_r_L0_bed_room_2 | ok | none |
| cam_r_L0_bed_room_3 | ok | none |
| cam_r_L0_kitchen_1 | ok | none |
| cam_r_L0_kitchen_2 | ok | none |
| cam_r_L0_kitchen_3 | ok | none (+ 2 unconfirmed or decor) |
| cam_r_L0_living_room_1 | ok | none |
| cam_r_L0_living_room_2 | ok | none |
| cam_r_L0_living_room_3 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_lobby_1 | ok | none |
| cam_r_L0_lobby_2 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_lobby_3 | ok | none |
| cam_r_L0_master_bed_room_1 | ok | none |
| cam_r_L0_master_bed_room_2 | ok | none |
| cam_r_L0_master_bed_room_3 | added_by_polish | bathtub 0.10 at [24, 845, 562, 1015] (vlm:qwen) |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L0_bath_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_bath_2 | polished | 1 / 4 of 4 | no |
| cam_r_L0_bed_room_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_bed_room_2 | polished | 1 / 4 of 4 | no |
| cam_r_L0_bed_room_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kitchen_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kitchen_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kitchen_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_living_room_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_living_room_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_living_room_3 | polished | 1 / 4 of 4 | no |
| cam_r_L0_lobby_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_lobby_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_lobby_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_master_bed_room_1 | polished | 1 / 4 of 4 | no |
| cam_r_L0_master_bed_room_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_master_bed_room_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_bed_room_1 | insertion:f_L0_014 | yes | no |
| cam_r_L0_bed_room_1 | removal:f_L0_014 | yes | no |
| cam_r_L0_living_room_2 | insertion:f_L0_002 | yes | no |
| cam_r_L0_living_room_2 | insertion:win_L0_002 | no | no |
| cam_r_L0_living_room_2 | removal:f_L0_002 | yes | yes |
| cam_r_L0_living_room_2 | removal:win_L0_002 | yes | yes |
| cam_r_L0_living_room_2 | swap:f_L0_002 | yes | no |
| cam_r_L0_lobby_1 | insertion:d_L0_001 | no | no |
| cam_r_L0_lobby_1 | removal:d_L0_001 | no | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.750 | >= 0.8 |
| removal confirmed | 0.500 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (4 controls) | 0.750 / 0.750 / 0.750 | - |
| type swap confirmed | 0.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.75 misses >= 0.8
- removal_confirmed 0.5 misses >= 0.6
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
