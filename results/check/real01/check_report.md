# Vision check report: real01

20 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.7143 misses >= 0.8; removal_confirmed 0.4286 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 9 info, 11 ok |
| polished images checked | 11 |
| polished rejected | vision_check 2 |
| views needing review | 0 |
| polished preferred (>= 3 of 4 votes) | 2 of 11 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | info | info | kept | yes (3/4) | no | - |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | info | info | vision_check | yes (3/4) | no | - |
| cam_r_L0_bed_room_1 | r_L0_bed_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_bed_room_2 | r_L0_bed_room | info | info | kept | no (0/4) | no | - |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | ok | - | - | - | no | - |
| cam_r_L0_bed_room_3 | r_L0_bed_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_dining_1 | r_L0_dining | info | info | vision_check | no (0/4) | no | - |
| cam_r_L0_dining_2 | r_L0_dining | info | info | kept | no (0/4) | no | - |
| cam_r_L0_dining_3 | r_L0_dining | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | ok | info | kept | no (0/4) | no | - |
| cam_r_L0_kitchen_1 | r_L0_kitchen | ok | - | - | - | no | - |
| cam_r_L0_kitchen_2 | r_L0_kitchen | info | - | - | - | no | - |
| cam_r_L0_kitchen_3 | r_L0_kitchen | info | - | - | - | no | - |
| cam_r_L0_room_1 | r_L0_room | info | - | - | - | no | - |
| cam_r_L0_room_2 | r_L0_room | ok | - | - | - | no | - |
| cam_r_L0_room_3 | r_L0_room | info | - | - | - | no | - |

## Mismatches on the Cycles renders

- cam_r_L0_bath_toilet_1: f_L0_022 (washbasin, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_bath_toilet_2: f_L0_022 (washbasin, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_dining_1: dec_L0_032 (curtain, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_dining_1: f_L0_026 (tall_cabinet, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L0_kitchen_2: dec_L0_028 (blind, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L0_kitchen_2: f_L0_026 (tall_cabinet, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L0_kitchen_3: f_L0_026 (tall_cabinet, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 20 of 20 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

## Exterior views

No exterior view in this project.

## Elevation check (building JSON against the drawn elevations and the section)

Variant `base`; elevations from sheets.json exterior.openings_seen; north 0 deg (assumed (+Y is north: no north arrow)).
No drawn elevation: nothing to compare the facades with.

Roof heights (building z, the top surface): built eaves -, ridge -; section eaves -, ridge -: **not_checked**.
- no roof object in the scene manifest (the build made a flat roof, or no scene)

## Polished images rejected

- cam_r_L0_bath_toilet_2: vision_check: added_by_polish furniture (detector: shower 0.17, confirmed by score) at [57, 0, 201, 84]
- cam_r_L0_dining_1: vision_check: added_by_polish furniture (detector: washbasin 0.12, confirmed by score) at [1191, 404, 1246, 419]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L0_bath_toilet_1 | ok | none (+ 4 unconfirmed or decor) |
| cam_r_L0_bath_toilet_2 | added_by_polish | shower 0.17 at [57, 0, 201, 84] (score) |
| cam_r_L0_bed_room_1 | ok | none |
| cam_r_L0_bed_room_2 | ok | none |
| cam_r_L0_bed_room_3 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_dining_1 | added_by_polish | washbasin 0.12 at [1191, 404, 1246, 419] (score) (+ 5 unconfirmed or decor) |
| cam_r_L0_dining_2 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_dining_3 | ok | none |
| cam_r_L0_drawing_room_1 | ok | none |
| cam_r_L0_drawing_room_2 | ok | none |
| cam_r_L0_drawing_room_3 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L0_bath_toilet_1 | polished | 3 / 4 of 4 | yes |
| cam_r_L0_bath_toilet_2 | polished | 3 / 4 of 4 | yes |
| cam_r_L0_bed_room_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_bed_room_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_bed_room_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_dining_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_dining_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_dining_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_drawing_room_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_drawing_room_2 | polished | 1 / 4 of 4 | no |
| cam_r_L0_drawing_room_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

- cam_r_L0_dining_2 insertion:f_L0_028: decoy seen by qwen, glm (unreliable)

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_bed_room_2_3 | insertion:win_L0_004 | no | no |
| cam_r_L0_bed_room_2_3 | removal:win_L0_004 | yes | no |
| cam_r_L0_dining_2 | insertion:f_L0_028 | no | no |
| cam_r_L0_dining_2 | removal:f_L0_028 | yes | no |
| cam_r_L0_drawing_room_1 | insertion:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_1 | insertion:win_L0_002 | no | no |
| cam_r_L0_drawing_room_1 | removal:f_L0_017 | yes | yes |
| cam_r_L0_drawing_room_1 | removal:win_L0_002 | yes | yes |
| cam_r_L0_drawing_room_1 | swap:f_L0_017 | yes | yes |
| cam_r_L0_drawing_room_3 | insertion:d_L0_003 | yes | no |
| cam_r_L0_drawing_room_3 | removal:d_L0_003 | no | no |
| cam_r_L0_kitchen_1 | insertion:f_L0_002 | no | no |
| cam_r_L0_kitchen_1 | removal:f_L0_002 | no | no |
| cam_r_L0_kitchen_2 | insertion:win_L0_009 | no | no |
| cam_r_L0_kitchen_2 | removal:win_L0_009 | yes | yes |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.714 | >= 0.8 |
| removal confirmed | 0.429 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (7 controls) | 0.857 / 0.857 / 0.857 | - |
| type swap confirmed | 1.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.7143 misses >= 0.8
- removal_confirmed 0.4286 misses >= 0.6
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
