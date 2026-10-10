# Vision check report: real01

18 views checked by 1 model(s) (agent), single pass. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model agent | Qwen/Qwen3.8-27B-FP8 @ 017b9c7af6b5 (Apache-2.0) |
| Cycles verdicts | 18 info |
| polished images checked | 0 |
| polished rejected | none |
| views needing review | 0 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_bath_toilet_1 | r_L0_bath_toilet | info | - | - | - | no | - |
| cam_r_L0_bath_toilet_2 | r_L0_bath_toilet | info | - | - | - | no | - |
| cam_r_L0_bed_room_1 | r_L0_bed_room | info | - | - | - | no | - |
| cam_r_L0_bed_room_2 | r_L0_bed_room | info | - | - | - | no | - |
| cam_r_L0_bed_room_2_1 | r_L0_bed_room_2 | info | - | - | - | no | - |
| cam_r_L0_bed_room_2_2 | r_L0_bed_room_2 | info | - | - | - | no | - |
| cam_r_L0_bed_room_2_3 | r_L0_bed_room_2 | info | - | - | - | no | - |
| cam_r_L0_bed_room_3 | r_L0_bed_room | info | - | - | - | no | - |
| cam_r_L0_dining_1 | r_L0_dining | info | - | - | - | no | - |
| cam_r_L0_dining_2 | r_L0_dining | info | - | - | - | no | - |
| cam_r_L0_dining_3 | r_L0_dining | info | - | - | - | no | - |
| cam_r_L0_drawing_room_1 | r_L0_drawing_room | info | - | - | - | no | - |
| cam_r_L0_drawing_room_2 | r_L0_drawing_room | info | - | - | - | no | - |
| cam_r_L0_drawing_room_3 | r_L0_drawing_room | info | - | - | - | no | - |
| cam_r_L0_kitchen_1 | r_L0_kitchen | info | - | - | - | no | - |
| cam_r_L0_kitchen_2 | r_L0_kitchen | info | - | - | - | no | - |
| cam_r_L0_kitchen_3 | r_L0_kitchen | info | - | - | - | no | - |
| cam_r_L0_room_1 | r_L0_room | info | - | - | - | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 19 of 20 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

- f_L0_008 (nightstand): anchor moved 0.1207 m, front turned None deg, front missing on one side

## Exterior views

No exterior view in this project.

## Elevation check (building JSON against the drawn elevations and the section)

Variant `base`; elevations from sheets.json exterior.openings_seen; north 0 deg (assumed (+Y is north: no north arrow)).
No drawn elevation: nothing to compare the facades with.

Roof heights (building z, the top surface): built eaves -, ridge -; section eaves -, ridge -: **not_checked**.
- no roof object in the scene manifest (the build made a flat roof, or no scene)

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
| cam_r_L0_bed_room_2_2 | insertion:win_L0_008 | yes | no |
| cam_r_L0_bed_room_2_2 | removal:win_L0_008 | yes | no |
| cam_r_L0_bed_room_3 | insertion:win_L0_001 | yes | no |
| cam_r_L0_bed_room_3 | removal:win_L0_001 | yes | no |
| cam_r_L0_dining_3 | insertion:f_L0_027 | yes | no |
| cam_r_L0_dining_3 | removal:f_L0_027 | yes | no |
| cam_r_L0_drawing_room_1 | insertion:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_1 | removal:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_1 | swap:f_L0_017 | yes | no |
| cam_r_L0_drawing_room_2 | insertion:d_L0_003 | yes | no |
| cam_r_L0_drawing_room_2 | removal:d_L0_003 | yes | no |
| cam_r_L0_drawing_room_3 | insertion:win_L0_002 | yes | no |
| cam_r_L0_drawing_room_3 | removal:win_L0_002 | yes | no |
| cam_r_L0_kitchen_1 | insertion:f_L0_002 | no | no |
| cam_r_L0_kitchen_1 | removal:f_L0_002 | yes | no |
| cam_r_L0_kitchen_2 | insertion:d_L0_005 | yes | no |
| cam_r_L0_kitchen_2 | removal:d_L0_005 | yes | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | - | <= 0.05 |
| views with a confirmed non-decor extra | - | <= 0.1 |
| count error rate | - | - |
| removal flagged | - | >= 0.8 |
| removal confirmed | - | >= 0.6 |
| insertion detected | - | >= 0.6 |
| type swap confirmed | - | - |
| agent: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- single pass: no two-model agreement
- fa_missing None misses <= 0.05 (single pass)
- fa_extra None misses <= 0.1 (single pass)
- removal_flagged None misses >= 0.8 (single pass)
- removal_confirmed None misses >= 0.6 (single pass)
- insertion None misses >= 0.6 (single pass)

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

- cam_r_L0_bath_toilet_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_bath_toilet_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_bed_room_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_bed_room_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_bed_room_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_dining_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_dining_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_dining_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_drawing_room_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_drawing_room_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_drawing_room_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L0_kitchen_1: detect/cam_r_L0_kitchen_1.json cycles was made from another image (sha256); not used
- cam_r_L0_kitchen_1: detect/cam_r_L0_kitchen_1.json control:f_L0_002 was made from another image (sha256); not used
- cam_r_L0_drawing_room_1: detect/cam_r_L0_drawing_room_1.json cycles was made from another image (sha256); not used
- cam_r_L0_drawing_room_1: detect/cam_r_L0_drawing_room_1.json control:f_L0_017 was made from another image (sha256); not used
- cam_r_L0_dining_3: detect/cam_r_L0_dining_3.json cycles was made from another image (sha256); not used
- cam_r_L0_drawing_room_3: detect/cam_r_L0_drawing_room_3.json cycles was made from another image (sha256); not used
- cam_r_L0_bed_room_3: detect/cam_r_L0_bed_room_3.json cycles was made from another image (sha256); not used
- cam_r_L0_kitchen_2: detect/cam_r_L0_kitchen_2.json cycles was made from another image (sha256); not used
- cam_r_L0_drawing_room_2: detect/cam_r_L0_drawing_room_2.json cycles was made from another image (sha256); not used
