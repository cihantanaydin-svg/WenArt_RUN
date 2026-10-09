# Vision check report: real02

17 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.5 misses >= 0.8; removal_confirmed 0.0 misses >= 0.6; insertion 0.5 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 11 info, 2 mismatch, 4 ok |
| polished images checked | 9 |
| polished rejected | vision_check 1 |
| views needing review | 2 |
| polished preferred (>= 3 of 4 votes) | 0 of 9 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | r_L-1b_acik_mutfak | info | info | kept | no (0/4) | no | - |
| cam_r_L-1b_acik_mutfak_2 | r_L-1b_acik_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1b_acik_mutfak_2_1 | r_L-1b_acik_mutfak_2 | info | - | - | - | no | - |
| cam_r_L-1b_acik_mutfak_2_2 | r_L-1b_acik_mutfak_2 | info | - | - | - | no | - |
| cam_r_L-1b_acik_mutfak_2_3 | r_L-1b_acik_mutfak_2 | info | - | - | - | no | - |
| cam_r_L-1b_acik_mutfak_3 | r_L-1b_acik_mutfak | info | info | kept | no (1/4) | no | - |
| cam_r_L-1b_koridor_1 | r_L-1b_koridor | info | mismatch | vision_check | no (0/4) | no | - |
| cam_r_L-1b_koridor_2 | r_L-1b_koridor | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1b_koridor_3 | r_L-1b_koridor | ok | ok | kept | no (1/4) | no | - |
| cam_r_L-1b_oda_1 | r_L-1b_oda | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1b_oda_2 | r_L-1b_oda | info | info | kept | no (0/4) | no | - |
| cam_r_L-1b_oda_3 | r_L-1b_oda | info | info | kept | no (0/4) | no | - |
| ext_1 | - | info | - | - | - | no | - |
| ext_2 | - | info | - | - | - | no | - |
| ext_3 | - | mismatch | - | - | - | yes | - |
| ext_4 | - | info | - | - | - | no | - |
| ext_5 | - | mismatch | - | - | - | yes | - |

## Mismatches on the Cycles renders

- cam_r_L-1b_acik_mutfak_2_1: f_L-1b_005 (unknown, from_documents, optional; evidence one_building.dwg INSERT:2C4A2/1,INSERT:2C4A2/10,INSERT:2C4A2/11,INSERT:2C4A2/12,INSERT:2C4A2/13,INSERT:2C4A2/2,INSERT:2C4A2/3,INSERT:2C4A2/4,INSERT:2C4A2/5,INSERT:2C4A2/6,INSERT:2C4A2/7,INSERT:2C4A2/8,INSERT:2C4A2/9,INSERT:2C4A3/0,INSERT:2C4A3/1,INSERT:2C4A3/10,INSERT:2C4A3/11,INSERT:2C4A3/12,INSERT:2C4A3/13,INSERT:2C4A3/14,INSERT:2C4A3/15,INSERT:2C4A3/16,INSERT:2C4A3/17,INSERT:2C4A3/18,INSERT:2C4A3/19,INSERT:2C4A3/2,INSERT:2C4A3/20,INSERT:2C4A3/21,INSERT:2C4A3/22,INSERT:2C4A3/23,INSERT:2C4A3/24,INSERT:2C4A3/25,INSERT:2C4A3/26,INSERT:2C4A3/27,INSERT:2C4A3/28,INSERT:2C4A3/29,INSERT:2C4A3/3,INSERT:2C4A3/30,INSERT:2C4A3/31,INSERT:2C4A3/32,INSERT:2C4A3/33,INSERT:2C4A3/34,INSERT:2C4A3/35,INSERT:2C4A3/4,INSERT:2C4A3/5,INSERT:2C4A3/6,INSERT:2C4A3/7,INSERT:2C4A3/8,INSERT:2C4A3/9,LWPOLYLINE:2C814 vector): disputed (not confirmed)
- cam_r_L-1b_acik_mutfak_2_1: f_L-1b_031 (fridge, from_documents, optional; evidence one_building.dwg INSERT:2C84A/4,INSERT:2C84A/9 vector): disputed (not confirmed)
- cam_r_L-1b_acik_mutfak_2_1: f_L-1b_037 (wall_cabinet, from_documents, optional; evidence one_building.dwg INSERT:2C84A/11 vector): missing (confirmed)
- cam_r_L-1b_acik_mutfak_3: f_L-1b_006 (unknown, from_documents, optional; evidence one_building.dwg INSERT:2ECCF/1,INSERT:2ECCF/10,INSERT:2ECCF/11,INSERT:2ECCF/12,INSERT:2ECCF/13,INSERT:2ECCF/2,INSERT:2ECCF/3,INSERT:2ECCF/4,INSERT:2ECCF/5,INSERT:2ECCF/6,INSERT:2ECCF/7,INSERT:2ECCF/8,INSERT:2ECCF/9,INSERT:2ECD0/0,INSERT:2ECD0/1,INSERT:2ECD0/10,INSERT:2ECD0/11,INSERT:2ECD0/12,INSERT:2ECD0/13,INSERT:2ECD0/14,INSERT:2ECD0/15,INSERT:2ECD0/16,INSERT:2ECD0/17,INSERT:2ECD0/18,INSERT:2ECD0/19,INSERT:2ECD0/2,INSERT:2ECD0/20,INSERT:2ECD0/21,INSERT:2ECD0/22,INSERT:2ECD0/23,INSERT:2ECD0/24,INSERT:2ECD0/25,INSERT:2ECD0/26,INSERT:2ECD0/27,INSERT:2ECD0/28,INSERT:2ECD0/29,INSERT:2ECD0/3,INSERT:2ECD0/30,INSERT:2ECD0/31,INSERT:2ECD0/32,INSERT:2ECD0/33,INSERT:2ECD0/34,INSERT:2ECD0/35,INSERT:2ECD0/4,INSERT:2ECD0/5,INSERT:2ECD0/6,INSERT:2ECD0/7,INSERT:2ECD0/8,INSERT:2ECD0/9,LWPOLYLINE:2F042 vector): missing (confirmed)
- ext_3: window count more than [0, 1] ({'qwen': 2, 'glm': 4})
- ext_5: win_L-1b_001 (window, from_documents, required; evidence one_building.dwg LWPOLYLINE:2F03F,LWPOLYLINE:2F040 vector): missing (confirmed)
- ext_5: win_L-1b_002 (window, from_documents, optional; evidence one_building.dwg LWPOLYLINE:2C810,LWPOLYLINE:2C811 vector): missing (confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 154 of 154 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

## Exterior views

| camera | view | sides | Cycles | roof (present share) | planned, not seen | seen, not planned |
|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | info | ok (0.999) | 0 | 1 |
| ext_2 | corner | right, front | info | ok (0.998) | 0 | 1 |
| ext_3 | corner | right, back | mismatch | ok (0.999) | 1 | 0 |
| ext_4 | corner | left, back | info | ok (0.999) | 1 | 0 |
| ext_5 | aerial | left, front | mismatch | ok (1.000) | 0 | 2 |

Advisory window and door count per visible facade (the crop of the render; the expected range is the openings seen in full to the openings seen in part; never a mismatch of the view and never a polish reason):

| camera | facade | expected windows / doors | counted | result |
|---|---|---|---|---|
| ext_1 | front | 1-2 / 0-0 | qwen: 2 windows, 0 doors, glm: 2 windows, 0 doors | ok |
| ext_2 | front | 1-2 / 0-0 | qwen: 2 windows, 0 doors, glm: 2 windows, 0 doors | ok |
| ext_3 | back | 0-0 / 1-2 | qwen: 0 windows, 2 doors, glm: 0 windows, 2 doors | ok |
| ext_4 | back | 0-0 / 1-2 | qwen: 0 windows, 2 doors, glm: 0 windows, 2 doors | ok |
| ext_5 | front | 2-2 / 0-0 | qwen: 0 windows, 0 doors, glm: 0 windows, 0 doors | mismatch |

## Elevation check (building JSON against the drawn elevations and the section)

Variant `l-1b-acik-mutfak`; elevations from sheets.json exterior.openings_seen; north 0 deg (assumed (+Y is north: no north arrow)).
No drawn elevation: nothing to compare the facades with.

Roof heights (building z, the top surface): built eaves 3.650, ridge 6.789; section eaves 3.650, ridge 6.789: **ok** (differences {'eaves': -0.0003, 'ridge': 0.0}).

## Polished images rejected

- cam_r_L-1b_koridor_1: vision_check: added_by_polish furniture ['other_furniture'] (+ detector); added_by_polish furniture (detector: bench 0.12, confirmed by score) at [861, 389, 1281, 771]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L-1b_acik_mutfak_2 | ok | none |
| cam_r_L-1b_acik_mutfak_3 | ok | none |
| cam_r_L-1b_koridor_1 | added_by_polish | bench 0.12 at [861, 389, 1281, 771] (score); bench 0.11 at [861, 393, 1076, 735] (score, vlm:qwen); chaise 0.10 at [861, 393, 1076, 735] (vlm:qwen) (+ 4 unconfirmed or decor) |
| cam_r_L-1b_koridor_2 | ok | none |
| cam_r_L-1b_koridor_3 | ok | none |
| cam_r_L-1b_oda_1 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L-1b_oda_2 | ok | none |
| cam_r_L-1b_oda_3 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_acik_mutfak_2 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_acik_mutfak_3 | polished | 1 / 4 of 4 | no |
| cam_r_L-1b_koridor_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_koridor_2 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_koridor_3 | polished | 1 / 4 of 4 | no |
| cam_r_L-1b_oda_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_oda_2 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_oda_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L-1b_acik_mutfak_2_2 | insertion:f_L-1b_017 | no | no |
| cam_r_L-1b_acik_mutfak_2_2 | removal:f_L-1b_017 | no | no |
| cam_r_L-1b_oda_1 | insertion:f_L-1b_040 | yes | yes |
| cam_r_L-1b_oda_1 | removal:f_L-1b_040 | yes | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.500 | >= 0.8 |
| removal confirmed | 0.000 | >= 0.6 |
| insertion detected | 0.500 | >= 0.6 |
| detector insertion found / flagged / confirmed (2 controls) | 1.000 / 1.000 / 1.000 | - |
| type swap confirmed | - | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.5 misses >= 0.8
- removal_confirmed 0.0 misses >= 0.6
- insertion 0.5 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
