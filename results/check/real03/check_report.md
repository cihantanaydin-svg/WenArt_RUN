# Vision check report: real03

14 views checked by 1 model(s) (agent), single pass. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model agent | Qwen/Qwen3.8-27B-FP8 @ 017b9c7af6b5 (Apache-2.0) |
| Cycles verdicts | 14 info |
| polished images checked | 0 |
| polished rejected | none |
| views needing review | 0 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_guvenlik_holu_1 | r_L0_guvenlik_holu | info | - | - | - | no | - |
| cam_r_L0_guvenlik_holu_2 | r_L0_guvenlik_holu | info | - | - | - | no | - |
| cam_r_L0_kat_holu_1 | r_L0_kat_holu | info | - | - | - | no | - |
| cam_r_L0_kat_holu_2 | r_L0_kat_holu | info | - | - | - | no | - |
| cam_r_L0_kat_holu_3 | r_L0_kat_holu | info | - | - | - | no | - |
| cam_r_L0_kat_merdiveni_1 | r_L0_kat_merdiveni | info | - | - | - | no | - |
| cam_r_L0_kat_merdiveni_2 | r_L0_kat_merdiveni | info | - | - | - | no | - |
| cam_r_L0_kat_merdiveni_3 | r_L0_kat_merdiveni | info | - | - | - | no | - |
| cam_r_L0_ruzgarlik_1 | r_L0_ruzgarlik | info | - | - | - | no | - |
| cam_r_L0_ruzgarlik_2 | r_L0_ruzgarlik | info | - | - | - | no | - |
| cam_r_L0_ruzgarlik_3 | r_L0_ruzgarlik | info | - | - | - | no | - |
| cam_r_L0_yangin_merdiveni_1 | r_L0_yangin_merdiveni | info | - | - | - | no | - |
| cam_r_L0_yangin_merdiveni_2 | r_L0_yangin_merdiveni | info | - | - | - | no | - |
| cam_r_L0_yangin_merdiveni_3 | r_L0_yangin_merdiveni | info | - | - | - | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 3 of 3 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

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

Not run for this project (no `detect/` folder).

## Realism preference (info only)

None.

## Unreliable or incomplete checks

None.

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L0_kat_holu_1 | insertion:d_L0_004 | no | no |
| cam_r_L0_kat_holu_1 | removal:d_L0_004 | no | no |
| cam_r_L0_kat_holu_2 | insertion:f_L0_010 | yes | no |
| cam_r_L0_kat_holu_2 | removal:f_L0_010 | yes | no |
| cam_r_L0_ruzgarlik_1 | insertion:d_L0_002 | yes | no |
| cam_r_L0_ruzgarlik_1 | removal:d_L0_002 | yes | no |
| cam_r_L0_ruzgarlik_2 | insertion:f_L0_005 | yes | no |
| cam_r_L0_ruzgarlik_2 | removal:f_L0_005 | yes | no |
| cam_r_L0_ruzgarlik_3 | swap:f_L0_004 | yes | no |
| cam_r_L0_yangin_merdiveni_2 | insertion:f_L0_013 | no | no |
| cam_r_L0_yangin_merdiveni_2 | removal:f_L0_013 | yes | no |

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

None.
