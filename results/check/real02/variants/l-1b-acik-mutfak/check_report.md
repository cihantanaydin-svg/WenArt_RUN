# Vision check report: real02

15 views checked by 1 model(s) (agent), single pass. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model agent | Qwen/Qwen3.8-27B-FP8 @ 017b9c7af6b5 (Apache-2.0) |
| Cycles verdicts | 15 info |
| polished images checked | 0 |
| polished rejected | none |
| views needing review | 0 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L-1b_acik_mutfak_1 | r_L-1b_acik_mutfak | info | - | - | - | no | - |
| cam_r_L-1b_acik_mutfak_2 | r_L-1b_acik_mutfak | info | - | - | - | no | - |
| cam_r_L-1b_acik_mutfak_3 | r_L-1b_acik_mutfak | info | - | - | - | no | - |
| cam_r_L-1b_koridor_1 | r_L-1b_koridor | info | - | - | - | no | - |
| cam_r_L-1b_koridor_2 | r_L-1b_koridor | info | - | - | - | no | - |
| cam_r_L-1b_koridor_3 | r_L-1b_koridor | info | - | - | - | no | - |
| cam_r_L-1b_oda_1 | r_L-1b_oda | info | - | - | - | no | - |
| cam_r_L-1b_oda_2 | r_L-1b_oda | info | - | - | - | no | - |
| cam_r_L-1b_oda_3 | r_L-1b_oda | info | - | - | - | no | - |
| ext_1 | - | info | - | - | - | no | - |
| ext_2 | - | info | - | - | - | no | - |
| ext_3 | - | info | - | - | - | no | - |
| ext_4 | - | info | - | - | - | no | - |
| ext_5 | - | info | - | - | - | no | - |
| ext_6 | - | info | - | - | - | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 200 of 210 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

- f_L-1_023 (wardrobe): anchor moved 0.1791 m, front turned 0.0 deg, no longer against wall w_L-1_004 (now centre None)
- f_L-1_024 (wardrobe): anchor moved 0.18 m, front turned 0.0 deg, no longer against wall w_L-1_004 (now centre None)
- f_L-1_050 (armchair): anchor moved 0.0 m, front turned 90.0 deg
- f_L-1_054 (sofa_corner): anchor moved 0.0 m, front turned 90.0 deg
- f_L-1_057 (floor_lamp): anchor moved 0.8175 m, front turned 90.0 deg
- f_L-1_059 (floor_lamp): anchor moved 0.2915 m, front turned 0.0 deg
- f_L-1_062 (sofa): anchor moved 0.3 m, front turned None deg
- f_L-1_065 (floor_lamp): anchor moved 0.3 m, front turned None deg
- f_L0_029 (desk): anchor moved 0.3 m, front turned 0.0 deg
- f_L0_033 (floor_lamp): anchor moved 0.0615 m, front turned 0.0 deg

## Exterior views

| camera | view | sides | Cycles | roof (present share) | planned, not seen | seen, not planned |
|---|---|---|---|---|---|---|
| ext_1 | corner | left, front | info | ok (0.967) | 0 | 2 |
| ext_2 | corner | right, front | info | ok (0.969) | 0 | 2 |
| ext_3 | corner | right, back | info | ok (0.971) | 0 | 0 |
| ext_4 | corner | left, back | info | ok (0.970) | 0 | 0 |
| ext_5 | aerial | left, front | info | ok (0.998) | 0 | 2 |
| ext_6 | frontal | back | info | ok (1.000) | 0 | 0 |

Advisory window and door count per visible facade (the crop of the render; the expected range is the openings seen in full to the openings seen in part; never a mismatch of the view and never a polish reason):

| camera | facade | expected windows / doors | counted | result |
|---|---|---|---|---|
| ext_1 | front | 2-4 / 0-0 | agent: 5 windows, 0 doors | unverified |
| ext_2 | front | 2-4 / 0-0 | agent: 5 windows, 0 doors | unverified |
| ext_3 | back | 0-0 / 2-2 | agent: 1 windows, 2 doors | unverified |
| ext_4 | back | 0-0 / 2-2 | agent: 1 windows, 2 doors | unverified |
| ext_5 | front | 2-2 / 0-0 | agent: 2 windows, 0 doors | ok |
| ext_6 | back | 0-0 / 2-2 | agent: 0 windows, 2 doors | ok |

## Elevation check (building JSON against the drawn elevations and the section)

Variant `l-1b-acik-mutfak`; elevations from sheets.json exterior.openings_seen; north 0 deg (assumed (+Y is north: no north arrow)).
No drawn elevation: nothing to compare the facades with.

Roof heights (building z, the top surface): built eaves 3.650, ridge 6.789; section eaves 3.650, ridge 6.789: **ok** (differences {'eaves': -0.0003, 'ridge': 0.0}).

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
| cam_r_L-1b_acik_mutfak_2 | insertion:win_L-1b_001 | yes | no |
| cam_r_L-1b_acik_mutfak_2 | removal:win_L-1b_001 | yes | no |
| cam_r_L-1b_oda_1 | insertion:f_L-1b_062 | yes | no |
| cam_r_L-1b_oda_1 | removal:f_L-1b_062 | yes | no |
| cam_r_L-1b_oda_3 | insertion:d_L-1b_001 | yes | no |
| cam_r_L-1b_oda_3 | removal:d_L-1b_001 | yes | no |

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

- cam_r_L-1b_acik_mutfak_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_acik_mutfak_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_acik_mutfak_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_koridor_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_koridor_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_koridor_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_oda_1: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_oda_2: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_oda_3: polish images were made from another Cycles render (source_sha256); not checked
- cam_r_L-1b_oda_1: detect/cam_r_L-1b_oda_1.json cycles was made from another image (sha256); not used
- cam_r_L-1b_acik_mutfak_2: detect/cam_r_L-1b_acik_mutfak_2.json cycles was made from another image (sha256); not used
- cam_r_L-1b_oda_3: detect/cam_r_L-1b_oda_3.json cycles was made from another image (sha256); not used
