# Vision check report: synthetic-07

30 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.625 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 16 info, 3 mismatch, 11 ok |
| polished images checked | 17 |
| polished rejected | vision_check 1 |
| views needing review | 3 |
| polished preferred (>= 3 of 4 votes) | 0 of 17 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L-1_hol_1 | r_L-1_hol | info | - | - | - | no | - |
| cam_r_L-1_hol_2 | r_L-1_hol | ok | - | - | - | no | - |
| cam_r_L-1_hol_3 | r_L-1_hol | info | - | - | - | no | - |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | info | info | kept | no (0/4) | no | - |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | info | ok | kept | no (0/4) | no | - |
| cam_r_L-1_salon_1 | r_L-1_salon | ok | - | - | - | no | - |
| cam_r_L-1_salon_2 | r_L-1_salon | info | - | - | - | no | - |
| cam_r_L-1_salon_3 | r_L-1_salon | info | ok | kept | no (0/4) | no | - |
| cam_r_L0_banyo_1 | r_L0_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L0_banyo_2 | r_L0_banyo | mismatch | mismatch | vision_check | no (0/4) | yes | - |
| cam_r_L0_banyo_3 | r_L0_banyo | mismatch | mismatch | kept | no (0/4) | yes | - |
| cam_r_L0_hol_1 | r_L0_hol | ok | - | - | - | no | - |
| cam_r_L0_hol_2 | r_L0_hol | ok | - | - | - | no | - |
| cam_r_L0_hol_3 | r_L0_hol | info | - | - | - | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | ok | ok | kept | no (0/4) | no | - |
| cam_r_L1_hol_1 | r_L1_hol | ok | info | kept | no (0/4) | no | - |
| cam_r_L1_hol_2 | r_L1_hol | info | info | kept | no (0/4) | no | - |
| cam_r_L1_hol_3 | r_L1_hol | ok | info | kept | no (0/4) | no | - |
| cam_r_L1_oyun_odasi_1 | r_L1_oyun_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_oyun_odasi_2 | r_L1_oyun_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_oyun_odasi_3 | r_L1_oyun_odasi | info | info | kept | no (0/4) | no | - |
| cam_r_L1_teras_1 | r_L1_teras | mismatch | mismatch | kept | no (0/4) | yes | - |
| ext_2 | - | info | - | - | - | no | - |
| ext_3 | - | info | - | - | - | no | - |
| ext_5 | - | ok | - | - | - | no | - |
| ext_6 | - | info | - | - | - | no | - |
| ext_7 | - | ok | - | - | - | no | - |

## Mismatches on the Cycles renders

- cam_r_L-1_hol_3: d_L-1_003 (door, from_documents, optional; evidence sheet.dxf INSERT:141/0,INSERT:141/1,INSERT:141/2,INSERT:141/3 vector): missing (confirmed)
- cam_r_L-1_mutfak_2: f_L-1_002 (fridge, from_documents, optional; evidence sheet.dxf INSERT:157/0,INSERT:157/1 BUZDOLABI vector): disputed (not confirmed)
- cam_r_L-1_mutfak_3: f_L-1_011 (tall_cabinet, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L-1_salon_2: f_L-1_007 (table_coffee, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L-1_salon_3: f_L-1_007 (table_coffee, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_banyo_1: f_L0_003 (shower, from_documents, required; evidence sheet.dxf INSERT:1F4/0,INSERT:1F4/1 DUS vector): disputed (not confirmed)
- cam_r_L0_banyo_2: f_L0_005 (washbasin, from_documents, optional; evidence sheet.dxf INSERT:1F2/0,INSERT:1F2/1 LAVABO vector): missing (confirmed)
- cam_r_L0_banyo_2: door count more than [0, 0] ({'qwen': 1, 'glm': 1})
- cam_r_L0_banyo_3: f_L0_003 (shower, from_documents, optional; evidence sheet.dxf INSERT:1F4/0,INSERT:1F4/1 DUS vector): missing (confirmed)
- cam_r_L0_banyo_3: door count more than [0, 0] ({'qwen': 1, 'glm': 1})
- cam_r_L0_yatak_odasi_2: f_L0_007 (nightstand, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_oyun_odasi_1: f_L1_005 (chair, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_teras_1: window count more than [0, 0] ({'qwen': 1, 'glm': 1})
- ext_6: d_L1_001 (door, from_documents, optional; evidence sheet.dxf INSERT:223/1 vector): disputed (not confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 18 of 18 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

## Exterior views

| camera | view | sides | Cycles | roof (present share) | planned, not seen | seen, not planned |
|---|---|---|---|---|---|---|
| ext_2 | corner | east, south | info | ok (1.000) | 0 | 0 |
| ext_3 | corner | east, north | info | ok (0.941) | 0 | 0 |
| ext_5 | aerial | west, south | ok | ok (1.000) | 1 | 0 |
| ext_6 | elevation | south | info | ok (1.000) | 0 | 0 |
| ext_7 | elevation | east | ok | ok (1.000) | 0 | 0 |

Advisory window and door count per visible facade (the crop of the render; the expected range is the openings seen in full to the openings seen in part; never a mismatch of the view and never a polish reason):

| camera | facade | expected windows / doors | counted | result |
|---|---|---|---|---|
| ext_2 | east | 2-2 / 0-0 | qwen: 2 windows, 0 doors, glm: 2 windows, 0 doors | ok |
| ext_2 | south | 2-2 / 0-0 | qwen: 2 windows, 0 doors, glm: 2 windows, 0 doors | ok |
| ext_3 | east | 2-2 / 0-0 | qwen: 2 windows, 0 doors, glm: 2 windows, 0 doors | ok |
| ext_3 | north | 2-2 / 1-1 | qwen: 2 windows, 1 doors, glm: 2 windows, 1 doors | ok |
| ext_5 | south | 2-4 / 0-1 | qwen: 2 windows, 1 doors, glm: 3 windows, 1 doors | ok |
| ext_5 | west | 2-3 / 0-0 | qwen: 2 windows, 0 doors, glm: 2 windows, 0 doors | ok |
| ext_6 | south | 2-2 / 1-1 | qwen: 2 windows, 1 doors, glm: 2 windows, 1 doors | ok |
| ext_7 | east | 2-2 / 0-0 | qwen: 2 windows, 0 doors, glm: 1 windows, 1 doors | unverified |

## Elevation check (building JSON against the drawn elevations and the section)

Variant `base`; elevations from building.json facade.elevations; north 0 deg (site.north_deg (vector)).

| elevation | side | drawn windows / doors | building windows / doors | positions | result |
|---|---|---|---|---|---|
| r7 | south | 2 / 1 | 5 / 1 | 0 matched, offset +0.00 m | mismatch |
| r8 | east | 2 / 0 | 3 / 0 | 0 matched, offset +0.00 m | mismatch |

- south: the drawn heights are +0.60 m from the building's (an elevation without a level mark takes its ground as z 0.00, assumed): a common offset, listed
- east: the drawn heights are +3.15 m from the building's: more than the 1.0 m a drawn ground at z 0.00 can explain; positions not trusted

Roof heights (building z, the top surface): built eaves 3.955, ridge 7.106; section eaves 3.955, ridge 7.106: **ok** (differences {'eaves': 0.0, 'ridge': -0.0001}).

## Polished images rejected

- cam_r_L0_banyo_2: vision_check: added_by_polish furniture (detector: shower 0.18, confirmed by score) at [1196, 338, 1235, 384]; added_by_polish furniture (detector: bathtub 0.13, confirmed by score) at [738, 389, 1040, 654]; added_by_polish furniture (detector: shower 0.12, confirmed by score) at [901, 399, 960, 487]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L-1_mutfak_1 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L-1_mutfak_2 | ok | none |
| cam_r_L-1_mutfak_3 | ok | none |
| cam_r_L-1_salon_3 | ok | none |
| cam_r_L0_banyo_1 | ok | none |
| cam_r_L0_banyo_2 | added_by_polish | shower 0.18 at [1196, 338, 1235, 384] (score); bathtub 0.13 at [738, 389, 1040, 654] (score); shower 0.12 at [901, 399, 960, 487] (score) (+ 6 unconfirmed or decor) |
| cam_r_L0_banyo_3 | ok | none |
| cam_r_L0_yatak_odasi_1 | ok | none |
| cam_r_L0_yatak_odasi_2 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_yatak_odasi_3 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L1_hol_1 | ok | none |
| cam_r_L1_hol_2 | ok | none |
| cam_r_L1_hol_3 | ok | none |
| cam_r_L1_oyun_odasi_1 | ok | none (+ 2 unconfirmed or decor) |
| cam_r_L1_oyun_odasi_2 | ok | none |
| cam_r_L1_oyun_odasi_3 | ok | none |
| cam_r_L1_teras_1 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L-1_mutfak_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_mutfak_2 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_mutfak_3 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_salon_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_banyo_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_yatak_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_yatak_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_yatak_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_hol_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_oyun_odasi_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_oyun_odasi_2 | polished | 0 / 4 of 4 | no |
| cam_r_L1_oyun_odasi_3 | polished | 0 / 4 of 4 | no |
| cam_r_L1_teras_1 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L-1_hol_2 | insertion:d_L-1_002 | yes | no |
| cam_r_L-1_hol_2 | removal:d_L-1_002 | no | no |
| cam_r_L-1_mutfak_2 | insertion:win_L-1_003 | yes | no |
| cam_r_L-1_mutfak_2 | removal:win_L-1_003 | yes | yes |
| cam_r_L-1_salon_2 | insertion:f_L-1_005 | yes | no |
| cam_r_L-1_salon_2 | insertion:win_L-1_005 | no | no |
| cam_r_L-1_salon_2 | removal:f_L-1_005 | no | no |
| cam_r_L-1_salon_2 | removal:win_L-1_005 | yes | no |
| cam_r_L-1_salon_2 | swap:f_L-1_005 | yes | no |
| cam_r_L0_banyo_2 | insertion:f_L0_003 | yes | no |
| cam_r_L0_banyo_2 | removal:f_L0_003 | yes | yes |
| cam_r_L0_hol_1 | insertion:d_L0_003 | no | no |
| cam_r_L0_hol_1 | removal:d_L0_003 | no | no |
| cam_r_L0_yatak_odasi_2 | insertion:f_L0_002 | no | no |
| cam_r_L0_yatak_odasi_2 | removal:f_L0_002 | yes | yes |
| cam_r_L0_yatak_odasi_2 | swap:f_L0_002 | yes | no |
| cam_r_L1_oyun_odasi_2 | swap:f_L1_004 | yes | yes |
| cam_r_L1_oyun_odasi_3 | insertion:win_L1_001 | no | no |
| cam_r_L1_oyun_odasi_3 | removal:win_L1_001 | yes | yes |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.120 | - |
| removal flagged | 0.625 | >= 0.8 |
| removal confirmed | 0.500 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (8 controls) | 1.000 / 0.875 / 0.750 | - |
| type swap confirmed | 0.333 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.016 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.625 misses >= 0.8
- removal_confirmed 0.5 misses >= 0.6
- insertion 0.0 misses >= 0.6

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
