# Milestone 13 metrics: real04

After: `/home/user/WenArt_RUN/runs/20261023-135954-full/results/final/real04` (results layout). Before (baseline): `/home/user/WenArt_RUN/results/final/real04` (results layout, project real04). Definitions: docs/milestone13.md §7 and the docstring of wenart/report/metrics13.py; a metric says "no data" when the file it needs is missing.

## Inputs

| input | after | before |
|---|---|---|
| building | /home/user/WenArt_RUN/runs/20261023-135954-full/results/furniture/real04/building_final.json | /home/user/WenArt_RUN/results/furniture/real04/building_final.json |
| scene | /home/user/WenArt_RUN/runs/20261023-135954-full/results/renders/real04/scene_manifest.json | missing |
| render | /home/user/WenArt_RUN/runs/20261023-135954-full/results/renders/real04/render_manifest.json | missing |
| final | /home/user/WenArt_RUN/runs/20261023-135954-full/results/final/real04/final_manifest.json | /home/user/WenArt_RUN/results/final/real04/final_manifest.json |
| report | /home/user/WenArt_RUN/runs/20261023-135954-full/results/final/real04/final_report.md | /home/user/WenArt_RUN/results/final/real04/final_report.md |
| attribution | /home/user/WenArt_RUN/runs/20261023-135954-full/results/final/real04/ATTRIBUTION.md | /home/user/WenArt_RUN/results/final/real04/ATTRIBUTION.md |
| log | /home/user/WenArt_RUN/runs/20261023-135954-full/results/agent/real04/log.json | /home/user/WenArt_RUN/results/agent/real04/log.json |
| rubric | missing | /home/user/WenArt_RUN/results/review/m13_step0/real04_per_view.json |

## The 17 metrics

| # | metric | before | after | target | unit |
|---|---|---|---|---|---|
| 1 | drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk) | 12 of 34 (35 %) | 40 of 40 (100 %) | 100 % | % |
| 2 | drawn pieces in the scene (built, method not none) | 128 of 240 (53 %); without the 38 explained non-furniture pieces: 128 of 202 (63 %) | 190 of 238 (80 %); without the 44 explained non-furniture pieces: 190 of 194 (98 %) | >= 90 % | % |
| 3 | pieces with asset.method none | 43 | 26 | 0 | count |
| 4 | parametric share of the built pieces; grey boxes | 58 of 177 (33 %) parametric of the built pieces; 115 of 246 (47 %) of every fitted piece; module 0; grey boxes no data | 22 of 235 (9 %) parametric of the built pieces; 44 of 257 (17 %) of every fitted piece; module 22; grey boxes 0 | <= 25 %; 0 | % |
| 5 | rooms with a complete group set | bathroom 8/10; bedroom 4/8; kitchen 0/2; living 0/4 | bathroom 10/10; bedroom 8/8; kitchen 2/2; living 0/4 | >= 90 % of the furnished main rooms | % |
| 6 | last-round findings F8 + S2 (> 3 cm) + G10 + LG | round 7: F8 38 / S2 > 3 cm 1 (S2 all 17) / G10 18 / LG 66 | round 4: F8 4 / S2 > 3 cm 3 (S2 all 10) / G10 18 / LG 4 | <= 5 / <= 3 / report-only / <= 5 | count |
| 7 | accepted agent edits whose finding is gone next round | 19 of 147 (13 %) (accepted edits 183, rounds 7) | 10 of 11 (91 %) (accepted edits 18, rounds 4) | >= 60 % (or the agent is off) | % |
| 8 | built library pieces: top model share; distinct; units unknown; stretch > 5 %; quality <= 3 | top objaverse_d2785b57e7da45858f2fe8bf4dedd68d 40 of 119 (34 %); distinct 26; units unknown 59 of 119 (50 %); stretch > 5 % 58 of 119 (49 %); quality <= 3 13 of 111 (12 %) | top objaverse_3446229dce1f47528fa871cc7669136c 10 of 191 (5 %); distinct 98; units unknown 12 of 191 (6 %); stretch > 5 % 0 of 191 (0 %); quality <= 3 33 of 63 (52 %) | <= 15 %; >= 60; <= 10 %; <= 10 %; <= 25 % | % |
| 9 | interior views at EV >= +5; EV median gap lit vs daylight rooms | 9 of 44 interior views at EV >= +5; gap no data (window rooms unknown without the scene manifest) | 0 of 37 interior views at EV >= +5; gap 0.17 EV (median +1.67 over 19 views of rooms without a window vs +1.50 over 18 views of rooms with one) | 0; <= 2 EV | count |
| 10 | shell slots on PBR sets with normal + roughness; fabric colour applied | shell slots with normal + roughness: no data; fabric colour applied: no data (14 upholstered pieces built) | shell slots with normal + roughness: 18 of 18 (100 %); fabric colour applied: 3 of 20 (15 %) (recoloured 1, module / parametric fabric slot 2; colour asked but the model has no recolourable fabric slot: 7 piece(s), 5 model(s); no fabric colour asked: 10 piece(s); read from the alternatives' scenes: 4) (20 upholstered pieces built) | >= 90 %; 100 % | % |
| 11 | drawn trees built as real geometry; hedges from the drawn rows; black pixels in the site view | trees built no data (100 drawn); hedges no data built of 0 drawn rows; black pixels in the site view 29.8 % (ext_7, the darkest exterior: the run records no view kinds) | trees built 20 of 20 (100 %) (20 drawn); hedges 4 built of 4 drawn rows; black pixels in the site view 3.6 % (ext_7) | 100 %; 2; 0 % | % |
| 12 | exterior views rendered of planned | 4 rendered of no data planned (no scene manifest) | 5 of 7 (2 dropped: ext_4, ext_6) | 7 of 7 | count |
| 13 | views in halls or with >= 50 % bare wall | 12 of 48 views: halls 12, bare wall >= 50 % no data | 17 of 42 views: halls 9, bare wall >= 50 % 9 | <= 4 | count |
| 14 | in_json_not_rendered mismatches of the final check | 18 in 10 view(s) | 0 in 0 view(s) | 0 | count |
| 15 | rubric score (reviewer, same rubric) | mean 1.88 over 48 views; 20 at 1; 3 at 4-5 (6 %) | no reviewer rubric file | mean >= 3.0; 0 at 1; >= 25 % at 4-5 | score |
| 16 | commercial-safe line present; ATTRIBUTION lists every flagged asset | line present for 0 of 48 (0 %); flagged assets 0, missing in ATTRIBUTION.md 0 | line present for 42 of 42 (100 %); flagged assets 18, missing in ATTRIBUTION.md 0 | 100 %; 0 missing | % |
| 17 | minutes and USD per full run | 122 min of stages, $5.07 at $2.49/h (26 stage records) | 87 min of stages, $3.62 at $2.49/h (27 stage records) | <= 150 min, <= $6.50 at $2.49/h | min |

Sources:

- 1: building_final.json furniture[]: source from_documents, type or drawn_type in ANCHOR_TYPES; built = build not false and asset.method in library / module / parametric
- 2: building_final.json furniture[]: source from_documents; built = build not false and asset.method not none; parts furniture / built_of_furniture leave out the unbuilt pieces explained as no furniture (inferred_as rug / detail / column / decor, both AI passes not_furniture, a counter-leg detail)
- 3: building_final.json furniture[].asset.method == none
- 4: building_final.json: built pieces (build not false, method not none) by asset.method; fitted = pieces with an asset whose method is not none (the unbuilt ones count, §7); grey boxes = scene_manifest.json objects of kind furniture_proxy
- 5: building_final.json rooms[].room_type x ROOM_SETS over the built furniture and decor of each room (furnished main rooms: rooms of a set type with at least one built piece)
- 6: orchestrator log.json finding events of the last round of the latest run (run_first_seq; not dropped) by checklist; S2 counted when evidence.metrics.depth_m > 0.03 m
- 7: orchestrator log.json of the latest run (run_first_seq): accepted edits that target a finding and have a next round (agent.metrics edits_with_target); gone = every critical / major finding they targeted that their round has is gone in the next round (edits_removing_finding)
- 8: building_final.json built pieces with asset.method library: asset_id counts, units_known, fit_scale (max / min - 1 > 5 %), quality (lower M8 judge <= 3) or a catalogue audit vision_doubt
- 9: render_manifest.json (else final_manifest.json views) exposure.ev of the interior views, the metered EV (lighting_dark metrics.ev_wanted) for a view the +3 cap held; window rooms from the scene manifest's window objects (room_ids); gap = median EV (no window) - median EV (window)
- 10: scene_manifest.json materials[] (textured shell slots with a maps record naming normal and roughness); built upholstered pieces (sofa, sofa_corner, armchair, ottoman) of the scene that builds them (base, else an alternative's scene manifest): applied = a recolour with a fabric slot (library model) or a fabric material key (module / parametric); models without a recolourable fabric slot are listed apart
- 11: building_final.json site.decor (kind tree) and site.hedges; scene_manifest.json site.vegetation / site.trees records (method not a primitive), site hedge objects; black pixels (every channel < 16) of the aerial / site camera's final preview; with no drawn tree, the scene's trees (records and site_kind tree objects; an object without a record is a primitive) built as real geometry
- 12: scene_manifest.json cameras (kind exterior) | cameras_dropped, by name = planned; render_manifest.json / final_manifest.json exterior views of a planned camera = rendered
- 13: views whose room (building rooms[].room_type, else the final manifest's room_type) is a hall type (hall, corridor, vestibule, landing, stair) or whose scene camera score.shares.wall >= 0.5
- 14: final_manifest.json views[].json_crosscheck.in_json_not_rendered
- 15: the reviewer's per-view rubric file (client_ready_score 1-5), over the views of the final report
- 16: final_manifest.json views[].commercial_safe and the commercial-safe lines of final_report.md; the flagged asset ids against final/ATTRIBUTION.md
- 17: the stage seconds of the run (run/*.json records of the run id, else final_manifest.json run_stages) / 60; USD at 2.49 USD per GPU hour (WENART_GPU_USD_PER_H overrides); the pod's wall time is longer (setup, downloads: docs/gpu-log.md)

## Per view

| camera | room | type | kind | EV before | EV after | score before | score after | commercial-safe before | commercial-safe after | in_json_not_rendered | bare wall | rubric tags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | bathroom | interior | -0.67 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.55 | - |
| cam_r_L-1_banyo_2 | r_L-1_banyo | bathroom | interior | -0.67 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.638 | - |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | hall | interior | 0 | 2.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial]) | 0 | 0.269 | - |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | hall | interior | 0.17 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.536 | - |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | hall | interior | 0.17 | 2.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial], hssd_db19f85684c964132250926f988da86ac513baa6 [non_commercial]) | 0 | 0.368 | - |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | kitchen | interior | 6.5 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 0 | 0.154 | - |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | kitchen | interior | 6.5 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 0 | 0.165 | - |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | kitchen | interior | 7 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 [non_commercial]) | 0 | 0.238 | - |
| cam_r_L-1_salon_1 | r_L-1_salon | living | interior | 3.5 | 1.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.287 | - |
| cam_r_L-1_salon_2 | r_L-1_salon | living | interior | 3.17 | 1.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.297 | - |
| cam_r_L-1_salon_3 | r_L-1_salon | living | interior | 3.33 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.234 | - |
| cam_r_L0_banyo_1 | r_L0_banyo | bathroom | interior | -0.67 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.499 | - |
| cam_r_L0_banyo_2 | r_L0_banyo | bathroom | interior | -0.83 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.614 | - |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | bathroom | interior | -0.33 | 1.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.626 | - |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | bathroom | interior | -0.5 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.723 | - |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | bedroom | interior | 7.67 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.216 | - |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | bedroom | interior | 6.17 | 1.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc]) | 0 | 0.343 | - |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | bedroom | interior | 6.5 | 1.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_books_classic_3_3223f281 [tool_nc], gen_plant_large_modern_4_2b0c9146 [tool_nc]) | 0 | 0.398 | - |
| cam_r_L0_koridor_1 | r_L0_koridor | hall | interior | 0.5 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.367 | - |
| cam_r_L0_koridor_2 | r_L0_koridor | hall | interior | 0.5 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.496 | - |
| cam_r_L0_koridor_3 | r_L0_koridor | hall | interior | 0.67 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.141 | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | bedroom | interior | 6.33 | 2.5 | 4 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc]) | 0 | 0.441 | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | bedroom | interior | 7 | 2.17 | 4 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_modern_minimal_1_7ea34d3d [tool_nc]) | 0 | 0.463 | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | bedroom | interior | 6.5 | 2.17 | 4 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.451 | - |
| cam_r_L0_yatak_odasi_4_1 | r_L0_yatak_odasi_4 | bedroom | interior | -0.17 | -0.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial]) | 0 | 0.478 | - |
| cam_r_L0_yatak_odasi_4_2 | r_L0_yatak_odasi_4 | bedroom | interior | -0.17 | -0.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial]) | 0 | 0.503 | - |
| cam_r_L0_yatak_odasi_4_3 | r_L0_yatak_odasi_4 | bedroom | interior | -0.17 | -0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_033ec086c23a6d39fb37df87e6748c413bf80e29 [non_commercial], hssd_1fa3dec03ab0afb0749373b2c8da8bf77c92e271 [non_commercial]) | 0 | 0.412 | - |
| cam_r_L1_banyo_1 | r_L1_banyo | bathroom | interior | -1.33 | -1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.503 | - |
| cam_r_L1_koridor_1 | r_L1_koridor | hall | interior | -0.83 | 1.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.284 | - |
| cam_r_L1_koridor_2 | r_L1_koridor | hall | interior | -0.83 | 1.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial]) | 0 | 0.423 | - |
| cam_r_L1_koridor_3 | r_L1_koridor | hall | interior | -0.83 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.243 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.83 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial]) | 0 | 0.311 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.67 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial]) | 0 | 0.307 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b8e36ac6fc006b0b7aaa4dabcbce9fa3108abcc2 [non_commercial]) | 0 | 0.312 | - |
| cam_r_L1_teras_1 | r_L1_teras | balcony | interior | -1 | -4.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial]) | 0 | 0.484 | - |
| cam_r_L1_teras_2 | r_L1_teras | balcony | interior | -1 | -4.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial]) | 0 | 0.434 | - |
| cam_r_L1_teras_3 | r_L1_teras | balcony | interior | -0.67 | -4.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial]) | 0 | 0.543 | - |
| ext_1 | - | - | exterior | -0.17 | -5 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | no data | - |
| ext_2 | - | - | exterior | -0.33 | -6.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | no data | - |
| ext_3 | - | - | exterior | - | -7.67 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_5 | - | - | exterior | -1.33 | -6 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial]) | 0 | no data | - |
| ext_7 | - | - | exterior | -1.33 | -7.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_088c257155d527517719972d29f363a438cfb4cd [non_commercial]) | 0 | no data | - |

Views only in the baseline: cam_r_L1_banyo_2, cam_r_L1_koridor_2_1, cam_r_L1_koridor_2_2, cam_r_L1_koridor_2_3, cam_r_L1_teras_2_1, cam_r_L1_teras_2_2, cam_r_L1_teras_2_3.

## Warnings

- orchestrator log: the latest run from seq 6859 (1024 of 7882 events; earlier runs of the appended log left out)
- rubric: no file (results layout under /home/user/WenArt_RUN/runs/20261023-135954-full/results/final/real04)
- baseline: render: no file (results layout under /home/user/WenArt_RUN/results/final/real04)
- baseline: scene: no file (results layout under /home/user/WenArt_RUN/results/final/real04)
