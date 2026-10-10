# Vision check report: synthetic-01

29 views checked by 1 model(s) (agent), single pass. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (single pass: no two-model agreement; fa_missing None misses <= 0.05 (single pass); fa_extra None misses <= 0.1 (single pass); removal_flagged None misses >= 0.8 (single pass); removal_confirmed None misses >= 0.6 (single pass); insertion None misses >= 0.6 (single pass)): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model agent | Qwen/Qwen3.8-27B-FP8 @ 017b9c7af6b5 (Apache-2.0) |
| Cycles verdicts | 29 info |
| polished images checked | 0 |
| polished rejected | none |
| views needing review | 0 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L0_banyo_1 | r_L0_banyo | info | - | - | - | no | - |
| cam_r_L0_banyo_2 | r_L0_banyo | info | - | - | - | no | - |
| cam_r_L0_banyo_3 | r_L0_banyo | info | - | - | - | no | - |
| cam_r_L0_hol_1 | r_L0_hol | info | - | - | - | no | - |
| cam_r_L0_hol_2 | r_L0_hol | info | - | - | - | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | info | - | - | - | no | - |
| cam_r_L0_salon_1 | r_L0_salon | info | - | - | - | no | - |
| cam_r_L0_salon_2 | r_L0_salon | info | - | - | - | no | - |
| cam_r_L0_salon_3 | r_L0_salon | info | - | - | - | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | info | - | - | - | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | info | - | - | - | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_banyo_1 | r_L1_banyo | info | - | - | - | no | - |
| cam_r_L1_banyo_2 | r_L1_banyo | info | - | - | - | no | - |
| cam_r_L1_banyo_3 | r_L1_banyo | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_hol_1 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_hol_2 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_hol_3 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | info | - | - | - | no | - |

## Mismatches on the Cycles renders

None.

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 13 of 13 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

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
| cam_r_L0_banyo_1 | insertion:win_L0_006 | yes | no |
| cam_r_L0_banyo_1 | removal:win_L0_006 | no | no |
| cam_r_L0_mutfak_2 | insertion:d_L0_003 | no | no |
| cam_r_L0_mutfak_2 | removal:d_L0_003 | yes | no |
| cam_r_L0_salon_1 | insertion:f_L0_001 | yes | no |
| cam_r_L0_salon_1 | removal:f_L0_001 | yes | no |
| cam_r_L0_salon_1 | swap:f_L0_001 | yes | no |
| cam_r_L0_salon_3 | insertion:win_L0_004 | yes | no |
| cam_r_L0_salon_3 | removal:win_L0_004 | yes | no |
| cam_r_L0_yatak_odasi_1 | insertion:f_L0_006 | no | no |
| cam_r_L0_yatak_odasi_1 | removal:f_L0_006 | yes | no |
| cam_r_L0_yatak_odasi_1 | swap:f_L0_006 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | insertion:f_L1_001 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | removal:f_L1_001 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | swap:f_L1_001 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | insertion:win_L1_003 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_2 | removal:win_L1_003 | yes | no |
| cam_r_L1_yatak_odasi_2 | insertion:d_L1_003 | no | no |
| cam_r_L1_yatak_odasi_2 | removal:d_L1_003 | no | no |

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
| agent: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.018 | decoy <= 0.1 |

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
