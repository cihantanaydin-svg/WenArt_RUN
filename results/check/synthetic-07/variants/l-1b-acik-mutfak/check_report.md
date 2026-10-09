# Vision check report: synthetic-07

3 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.6667 misses >= 0.8; removal_confirmed 0.0 misses >= 0.6; insertion 0.0 misses >= 0.6; decoy_accept[qwen] 0.3333 misses <= 0.1): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 1 info, 2 ok |
| polished images checked | 3 |
| polished rejected | check_incomplete 1 |
| views needing review | 0 |
| polished preferred (>= 3 of 4 votes) | 0 of 3 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | r_L-1b_salon_acik_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1b_salon_acik_mutfak_2 | r_L-1b_salon_acik_mutfak | info | info | check_incomplete | no (0/4) | no | - |
| cam_r_L-1b_salon_acik_mutfak_3 | r_L-1b_salon_acik_mutfak | ok | ok | kept | no (0/4) | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 18 of 18 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

## Exterior views

No exterior view in this project.

## Elevation check (building JSON against the drawn elevations and the section)

Variant `l-1b-acik-mutfak`; elevations from building.json facade.elevations; north 0 deg (site.north_deg (vector)).

| elevation | side | drawn windows / doors | building windows / doors | positions | result |
|---|---|---|---|---|---|
| r7 | south | 2 / 1 | 5 / 1 | 0 matched, offset +0.00 m | mismatch |
| r8 | east | 2 / 0 | 3 / 0 | 0 matched, offset +0.00 m | mismatch |

- south: the drawn heights are +0.60 m from the building's (an elevation without a level mark takes its ground as z 0.00, assumed): a common offset, listed
- east: the drawn heights are +3.15 m from the building's: more than the 1.0 m a drawn ground at z 0.00 can explain; positions not trusted

Roof heights (building z, the top surface): built eaves 3.955, ridge 7.106; section eaves 3.955, ridge 7.106: **ok** (differences {'eaves': 0.0, 'ridge': -0.0001}).

## Polished images rejected

- cam_r_L-1b_salon_acik_mutfak_2: check_incomplete: polished: unreliable (decoy seen): qwen; cycles: unreliable (decoy seen): qwen

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | ok | none |
| cam_r_L-1b_salon_acik_mutfak_2 | ok | none |
| cam_r_L-1b_salon_acik_mutfak_3 | ok | none (+ 1 unconfirmed or decor) |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_salon_acik_mutfak_2 | polished | 0 / 4 of 4 | no |
| cam_r_L-1b_salon_acik_mutfak_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

- cam_r_L-1b_salon_acik_mutfak_2 cycles: decoy seen by qwen (unreliable)
- cam_r_L-1b_salon_acik_mutfak_2 polished: decoy seen by qwen (unreliable)

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L-1b_salon_acik_mutfak_1 | insertion:f_L-1b_005 | yes | no |
| cam_r_L-1b_salon_acik_mutfak_1 | insertion:win_L-1b_006 | no | no |
| cam_r_L-1b_salon_acik_mutfak_1 | removal:f_L-1b_005 | yes | no |
| cam_r_L-1b_salon_acik_mutfak_1 | removal:win_L-1b_006 | yes | no |
| cam_r_L-1b_salon_acik_mutfak_1 | swap:f_L-1b_005 | yes | no |
| cam_r_L-1b_salon_acik_mutfak_2 | insertion:d_L-1b_003 | no | no |
| cam_r_L-1b_salon_acik_mutfak_2 | removal:d_L-1b_003 | no | no |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.000 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.667 | >= 0.8 |
| removal confirmed | 0.000 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (3 controls) | 1.000 / 1.000 / 1.000 | - |
| type swap confirmed | 0.000 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.333 / 0.000 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.000 | decoy <= 0.1 |

Missed targets (the check is advisory):
- removal_flagged 0.6667 misses >= 0.8
- removal_confirmed 0.0 misses >= 0.6
- insertion 0.0 misses >= 0.6
- decoy_accept[qwen] 0.3333 misses <= 0.1

## Source plan

- source plan compared through the evidence chain, the projected cross-check and the side-by-side crop.
- plan A/B on 0 camera(s): FA missing - -> -, removal confirmed - -> -.
- every view's source-plan crop is `<camera>_plan.jpg` in this folder.

## Warnings

None.
