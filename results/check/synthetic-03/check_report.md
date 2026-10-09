# Vision check report: synthetic-03

44 views checked by 2 model(s) (qwen, glm), two independent passes. Verdicts come only from agreeing passes; nothing is auto-fixed. The check is ADVISORY (removal_flagged 0.75 misses >= 0.8; removal_confirmed 0.5 misses >= 0.6; insertion 0.0 misses >= 0.6): an advisory check is an open item that needs the user's OK; the differential decision on polished images stays active.

| item | value |
|---|---|
| model qwen | Qwen/Qwen3-VL-8B-Instruct @ 0c351dd01ed8 (Apache-2.0) |
| model glm | zai-org/GLM-4.6V-Flash @ 411bb4d77144 (MIT) |
| Cycles verdicts | 24 info, 1 mismatch, 19 ok |
| polished images checked | 16 |
| polished rejected | vision_check 5 |
| views needing review | 1 |
| polished preferred (>= 3 of 4 votes) | 0 of 16 |

## Per view

| camera | room | Cycles | polished | polished decision | preferred | needs review | cross-check |
|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | ok | info | kept | no (1/4) | no | - |
| cam_r_L-1_banyo_2 | r_L-1_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L-1_hol_1 | r_L-1_hol | ok | - | - | - | no | - |
| cam_r_L-1_hol_2 | r_L-1_hol | ok | - | - | - | no | - |
| cam_r_L-1_hol_3 | r_L-1_hol | info | - | - | - | no | - |
| cam_r_L-1_kiler_1 | r_L-1_kiler | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1_kiler_2_1 | r_L-1_kiler_2 | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1_wc_1 | r_L-1_wc | ok | ok | vision_check | no (0/4) | no | - |
| cam_r_L-1_wc_2 | r_L-1_wc | ok | ok | kept | no (0/4) | no | - |
| cam_r_L-1_yatak_odasi_1 | r_L-1_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L-1_yatak_odasi_2 | r_L-1_yatak_odasi | info | - | - | - | no | - |
| cam_r_L-1_yatak_odasi_3 | r_L-1_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L0_antre_1 | r_L0_antre | info | ok | kept | no (0/4) | no | - |
| cam_r_L0_antre_2 | r_L0_antre | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_hol_1 | r_L0_hol | info | - | - | - | no | - |
| cam_r_L0_hol_2 | r_L0_hol | ok | - | - | - | no | - |
| cam_r_L0_hol_3 | r_L0_hol | info | - | - | - | no | - |
| cam_r_L0_kiler_1 | r_L0_kiler | info | ok | kept | no (0/4) | no | - |
| cam_r_L0_mutfak_1 | r_L0_mutfak | info | info | vision_check | no (0/4) | no | - |
| cam_r_L0_mutfak_2 | r_L0_mutfak | ok | - | - | - | no | - |
| cam_r_L0_mutfak_3 | r_L0_mutfak | ok | ok | kept | no (0/4) | no | - |
| cam_r_L0_salon_1 | r_L0_salon | ok | - | - | - | no | - |
| cam_r_L0_salon_2 | r_L0_salon | info | - | - | - | no | - |
| cam_r_L0_salon_3 | r_L0_salon | info | - | - | - | no | - |
| cam_r_L0_wc_1 | r_L0_wc | ok | ok | kept | no (1/4) | no | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | info | - | - | - | no | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | info | - | - | - | no | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_balkon_1 | r_L1_balkon | ok | ok | vision_check | no (0/4) | no | - |
| cam_r_L1_banyo_1 | r_L1_banyo | mismatch | mismatch | vision_check | no (0/4) | yes | - |
| cam_r_L1_banyo_2 | r_L1_banyo | ok | ok | vision_check | no (1/4) | no | - |
| cam_r_L1_banyo_3 | r_L1_banyo | info | info | kept | no (0/4) | no | - |
| cam_r_L1_cocuk_odasi_1 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_2 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_cocuk_odasi_3 | r_L1_cocuk_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_1 | r_L1_ebeveyn_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_2 | r_L1_ebeveyn_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_ebeveyn_yatak_odasi_3 | r_L1_ebeveyn_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L1_hol_1 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_hol_2 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_hol_3 | r_L1_hol | info | - | - | - | no | - |
| cam_r_L1_yatak_odasi_1 | r_L1_yatak_odasi | info | - | - | - | no | - |
| cam_r_L1_yatak_odasi_2 | r_L1_yatak_odasi | ok | - | - | - | no | - |
| cam_r_L1_yatak_odasi_3 | r_L1_yatak_odasi | info | - | - | - | no | - |

## Mismatches on the Cycles renders

- cam_r_L-1_banyo_2: f_L-1_009 (shower, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_hol_3: d_L0_006 (door, from_documents, optional; evidence mobilya_plani.dxf KAPI INSERT:11E KAPI_80 vector): missing (confirmed)
- cam_r_L0_kiler_1: d_L0_007 (door, from_documents, optional; evidence mobilya_plani.dxf KAPI INSERT:120 KAPI_80 vector): disputed (not confirmed)
- cam_r_L0_mutfak_1: f_L0_010 (fridge, from_documents, optional; evidence mobilya_plani.dxf MOBILYA INSERT:140 BUZDOLABI vector): disputed (not confirmed)
- cam_r_L0_mutfak_1: f_L0_013 (chair, from_documents, optional; evidence mobilya_plani.dxf MOBILYA INSERT:146 SANDALYE vector): disputed (not confirmed)
- cam_r_L0_salon_3: dec_L0_006 (blind, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_yatak_odasi_1: dec_L0_020 (curtain, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L0_yatak_odasi_1: f_L0_014 (bed_double, from_documents, optional; evidence mobilya_plani.dxf MOBILYA INSERT:148 YATAK_CIFT vector): disputed (not confirmed)
- cam_r_L1_banyo_1: f_L1_018 (shower, added_by_ai, required; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_banyo_3: f_L1_018 (shower, added_by_ai, optional; evidence building.json ai): missing (confirmed) (added_by_ai: render/polish issue, not a document conflict)
- cam_r_L1_hol_1: dec_L1_008 (mirror, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)
- cam_r_L1_hol_3: d_L1_002 (door, from_documents, optional; evidence kat_planlari.pdf p3 path:12 vector): disputed (not confirmed)
- cam_r_L1_hol_3: d_L1_004 (door, from_documents, optional; evidence kat_planlari.pdf p3 path:16 vector): disputed (not confirmed)
- cam_r_L1_yatak_odasi_3: dec_L1_016 (curtain, added_by_ai, optional; evidence building.json ai): disputed (not confirmed)

## JSON cross-check (building JSON projected with a depth test)

None.

## Drawn pieces against the source plan

Reference: source building.json; mode `furnished_rooms: complete`. 21 of 21 checked drawn pieces keep their anchor (within 0.05 m), front (within 1.0 deg) and wall; 0 changed by the AI, 0 type proposal(s) for unverified pieces.

## Exterior views

No exterior view in this project.

## Elevation check (building JSON against the drawn elevations and the section)

Variant `base`; elevations from sheets.json exterior.openings_seen; north 0 deg (assumed (+Y is north: no north arrow)).
No drawn elevation: nothing to compare the facades with.

Roof heights (building z, the top surface): built eaves -, ridge -; section eaves -, ridge -: **not_checked**.
- no roof object in the scene manifest (the build made a flat roof, or no scene)

## Polished images rejected

- cam_r_L-1_wc_1: vision_check: added_by_polish furniture (detector: shower 0.12, confirmed by score) at [845, 359, 953, 456]
- cam_r_L0_mutfak_1: vision_check: added_by_polish furniture (detector: sink_kitchen 0.14, confirmed by score) at [1471, 524, 1603, 581]
- cam_r_L1_balkon_1: vision_check: added_by_polish furniture (detector: bed_single 0.27, confirmed by score) at [166, 682, 1484, 1076]; added_by_polish furniture (detector: bed_double 0.20, confirmed by score) at [166, 682, 1484, 1076]
- cam_r_L1_banyo_1: vision_check: added_by_polish furniture (detector: chaise 0.12, confirmed by score) at [1523, 813, 1920, 1075]
- cam_r_L1_banyo_2: vision_check: added_by_polish furniture (detector: dresser 0.23, confirmed by score) at [215, 0, 952, 1080]; added_by_polish furniture (detector: kitchen_island 0.14, confirmed by score) at [215, 0, 952, 1080]

## Added-object detector

Calibrated: t_det 0.08, t_strong 0.11; a confirmed added non-decor object rejects the polished image.
Model: google/owlv2-base-patch16-ensemble @ cfd3195ba4ea (Apache-2.0).

| camera | detector | boxes |
|---|---|---|
| cam_r_L-1_banyo_1 | ok | none |
| cam_r_L-1_banyo_2 | ok | none |
| cam_r_L-1_kiler_1 | ok | none |
| cam_r_L-1_kiler_2_1 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L-1_wc_1 | added_by_polish | shower 0.12 at [845, 359, 953, 456] (score) (+ 4 unconfirmed or decor) |
| cam_r_L-1_wc_2 | ok | none |
| cam_r_L0_antre_1 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_antre_2 | ok | none |
| cam_r_L0_kiler_1 | ok | none |
| cam_r_L0_mutfak_1 | added_by_polish | sink_kitchen 0.14 at [1471, 524, 1603, 581] (score) (+ 2 unconfirmed or decor) |
| cam_r_L0_mutfak_3 | ok | none (+ 1 unconfirmed or decor) |
| cam_r_L0_wc_1 | ok | none (+ 3 unconfirmed or decor) |
| cam_r_L1_balkon_1 | added_by_polish | bed_single 0.27 at [166, 682, 1484, 1076] (score); bed_double 0.20 at [166, 682, 1484, 1076] (score) (+ 2 unconfirmed or decor) |
| cam_r_L1_banyo_1 | added_by_polish | chaise 0.12 at [1523, 813, 1920, 1075] (score) (+ 1 unconfirmed or decor) |
| cam_r_L1_banyo_2 | added_by_polish | dresser 0.23 at [215, 0, 952, 1080] (score); kitchen_island 0.14 at [215, 0, 952, 1080] (score) (+ 2 unconfirmed or decor) |
| cam_r_L1_banyo_3 | ok | none |

## Realism preference (info only)

| camera | image | votes for the polished image | preferred |
|---|---|---|---|
| cam_r_L-1_banyo_1 | polished | 1 / 4 of 4 | no |
| cam_r_L-1_banyo_2 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_kiler_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_kiler_2_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_wc_1 | polished | 0 / 4 of 4 | no |
| cam_r_L-1_wc_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_antre_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_antre_2 | polished | 0 / 4 of 4 | no |
| cam_r_L0_kiler_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_1 | polished | 0 / 4 of 4 | no |
| cam_r_L0_mutfak_3 | polished | 0 / 4 of 4 | no |
| cam_r_L0_wc_1 | polished | 1 / 4 of 4 | no |
| cam_r_L1_balkon_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_banyo_1 | polished | 0 / 4 of 4 | no |
| cam_r_L1_banyo_2 | polished | 1 / 4 of 4 | no |
| cam_r_L1_banyo_3 | polished | 0 / 4 of 4 | no |

## Unreliable or incomplete checks

- cam_r_L-1_yatak_odasi_3 insertion:f_L-1_003: decoy seen by qwen, glm (unreliable)
- cam_r_L-1_yatak_odasi_3 swap:f_L-1_003: decoy seen by qwen, glm (unreliable)
- cam_r_L1_yatak_odasi_1 swap:f_L1_009: decoy seen by qwen (unreliable)

## Controls

| camera | control | flagged | confirmed |
|---|---|---|---|
| cam_r_L-1_kiler_1 | insertion:d_L-1_001 | no | no |
| cam_r_L-1_kiler_1 | removal:d_L-1_001 | no | no |
| cam_r_L-1_kiler_2_1 | insertion:d_L-1_002 | no | no |
| cam_r_L-1_kiler_2_1 | removal:d_L-1_002 | no | no |
| cam_r_L-1_yatak_odasi_3 | insertion:f_L-1_003 | no | no |
| cam_r_L-1_yatak_odasi_3 | removal:f_L-1_003 | yes | yes |
| cam_r_L-1_yatak_odasi_3 | swap:f_L-1_003 | yes | yes |
| cam_r_L0_mutfak_2 | insertion:win_L0_004 | yes | no |
| cam_r_L0_mutfak_2 | removal:win_L0_004 | yes | yes |
| cam_r_L0_yatak_odasi_2 | insertion:f_L0_014 | no | no |
| cam_r_L0_yatak_odasi_2 | removal:f_L0_014 | yes | yes |
| cam_r_L0_yatak_odasi_2 | swap:f_L0_014 | yes | no |
| cam_r_L1_cocuk_odasi_2 | insertion:win_L1_005 | no | no |
| cam_r_L1_cocuk_odasi_2 | removal:win_L1_005 | yes | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | insertion:win_L1_003 | no | no |
| cam_r_L1_ebeveyn_yatak_odasi_1 | removal:win_L1_003 | yes | no |
| cam_r_L1_yatak_odasi_1 | swap:f_L1_009 | yes | yes |
| cam_r_L1_yatak_odasi_2 | insertion:f_L1_012 | yes | no |
| cam_r_L1_yatak_odasi_2 | removal:f_L1_012 | yes | yes |

## Calibration

| metric | value | target |
|---|---|---|
| combined FA missing | 0.013 | <= 0.05 |
| views with a confirmed non-decor extra | 0.000 | <= 0.1 |
| count error rate | 0.000 | - |
| removal flagged | 0.750 | >= 0.8 |
| removal confirmed | 0.500 | >= 0.6 |
| insertion detected | 0.000 | >= 0.6 |
| detector insertion found / flagged / confirmed (8 controls) | 0.875 / 0.750 / 0.750 | - |
| type swap confirmed | 0.667 | - |
| qwen: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.013 | decoy <= 0.1 |
| glm: answered / decoy accepted / single-pass FA missing | 1.000 / 0.000 / 0.013 | decoy <= 0.1 |

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
