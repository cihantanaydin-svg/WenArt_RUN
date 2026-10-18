# Milestone 13 metrics: real04

After: `/home/user/WenArt_RUN/runs/20261016-172855-full/results/final/real04` (results layout). Before (baseline): `/home/user/WenArt_RUN/results/final/real04` (results layout, project real04). Definitions: docs/milestone13.md §7 and the docstring of wenart/report/metrics13.py; a metric says "no data" when the file it needs is missing.

## Inputs

| input | after | before |
|---|---|---|
| building | /home/user/WenArt_RUN/runs/20261016-172855-full/results/furniture/real04/building_final.json | /home/user/WenArt_RUN/results/furniture/real04/building_final.json |
| scene | /home/user/WenArt_RUN/runs/20261016-172855-full/results/renders/real04/scene_manifest.json | missing |
| render | /home/user/WenArt_RUN/runs/20261016-172855-full/results/renders/real04/render_manifest.json | missing |
| final | /home/user/WenArt_RUN/runs/20261016-172855-full/results/final/real04/final_manifest.json | /home/user/WenArt_RUN/results/final/real04/final_manifest.json |
| report | /home/user/WenArt_RUN/runs/20261016-172855-full/results/final/real04/final_report.md | /home/user/WenArt_RUN/results/final/real04/final_report.md |
| attribution | /home/user/WenArt_RUN/runs/20261016-172855-full/results/final/real04/ATTRIBUTION.md | /home/user/WenArt_RUN/results/final/real04/ATTRIBUTION.md |
| log | /home/user/WenArt_RUN/runs/20261016-172855-full/results/agent/real04/log.json | /home/user/WenArt_RUN/results/agent/real04/log.json |
| rubric | missing | /home/user/WenArt_RUN/results/review/m13_step0/real04_per_view.json |

## The 17 metrics

| # | metric | before | after | target | unit |
|---|---|---|---|---|---|
| 1 | drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk) | 12 of 34 (35 %) | 34 of 34 (100 %) | 100 % | % |
| 2 | drawn pieces in the scene (built, method not none) | 128 of 240 (53 %); without the 38 explained non-furniture pieces: 128 of 202 (63 %) | 178 of 240 (74 %); without the 38 explained non-furniture pieces: 178 of 202 (88 %) | >= 90 % | % |
| 3 | pieces with asset.method none | 43 | 18 | 0 | count |
| 4 | parametric share of the built pieces; grey boxes | 58 of 177 (33 %) parametric of the built pieces; 115 of 246 (47 %) of every fitted piece; module 0; grey boxes no data | 24 of 236 (10 %) parametric of the built pieces; 68 of 280 (24 %) of every fitted piece; module 20; grey boxes 0 | <= 25 %; 0 | % |
| 5 | rooms with a complete group set | bathroom 8/10; bedroom 4/8; kitchen 0/2; living 0/4 | bathroom 10/10; bedroom 4/8; kitchen 2/2; living 0/4 | >= 90 % of the furnished main rooms | % |
| 6 | last-round findings F8 + S2 (> 3 cm) + G10 + LG | round 7: F8 38 / S2 > 3 cm 1 (S2 all 17) / G10 18 / LG 66 | round 4: F8 2 / S2 > 3 cm 10 (S2 all 25) / G10 18 / LG 8 | <= 5 / <= 3 / report-only / <= 5 | count |
| 7 | accepted agent edits whose finding is gone next round | 19 of 147 (13 %) (accepted edits 183, rounds 7) | 22 of 39 (56 %) (accepted edits 39, rounds 4) | >= 60 % (or the agent is off) | % |
| 8 | built library pieces: top model share; distinct; units unknown; stretch > 5 %; quality <= 3 | top objaverse_d2785b57e7da45858f2fe8bf4dedd68d 40 of 119 (34 %); distinct 26; units unknown 59 of 119 (50 %); stretch > 5 % 58 of 119 (49 %); quality <= 3 13 of 111 (12 %) | top objaverse_3446229dce1f47528fa871cc7669136c 10 of 192 (5 %); distinct 97; units unknown 14 of 192 (7 %); stretch > 5 % 0 of 192 (0 %); quality <= 3 37 of 66 (56 %) | <= 15 %; >= 60; <= 10 %; <= 10 %; <= 25 % | % |
| 9 | interior views at EV >= +5; EV median gap lit vs daylight rooms | 9 of 44 interior views at EV >= +5; gap no data (window rooms unknown without the scene manifest) | 3 of 42 interior views at EV >= +5; gap 1.49 EV (median +3.07 over 18 views of rooms without a window vs +1.58 over 24 views of rooms with one); 13 view(s) held at the EV cap (lighting_dark: 3 critical, 10 major), counted at their metered EV | 0; <= 2 EV | count |
| 10 | shell slots on PBR sets with normal + roughness; fabric colour applied | shell slots with normal + roughness: no data; fabric colour applied: no data (14 upholstered pieces built) | shell slots with normal + roughness: 19 of 19 (100 %); fabric colour applied: 2 of 20 (10 %) (20 upholstered pieces built) | >= 90 %; 100 % | % |
| 11 | drawn trees built as real geometry; hedges from the drawn rows; black pixels in the site view | trees built no data (100 drawn); hedges no data built of 0 drawn rows; black pixels in the site view 29.8 % (ext_7, the darkest exterior: the run records no view kinds) | trees built 20 of 20 (100 %) (20 drawn); hedges 4 built of 4 drawn rows; black pixels in the site view 4.1 % (ext_7) | 100 %; 2; 0 % | % |
| 12 | exterior views rendered of planned | 4 rendered of no data planned (no scene manifest) | 6 of 7 (1 dropped: ext_6) | 7 of 7 | count |
| 13 | views in halls or with >= 50 % bare wall | 12 of 48 views: halls 12, bare wall >= 50 % no data | 19 of 48 views: halls 10, bare wall >= 50 % 13 | <= 4 | count |
| 14 | in_json_not_rendered mismatches of the final check | 18 in 10 view(s) | 0 in 0 view(s) | 0 | count |
| 15 | rubric score (reviewer, same rubric) | mean 1.88 over 48 views; 20 at 1; 3 at 4-5 (6 %) | no reviewer rubric file | mean >= 3.0; 0 at 1; >= 25 % at 4-5 | score |
| 16 | commercial-safe line present; ATTRIBUTION lists every flagged asset | line present for 0 of 48 (0 %); flagged assets 0, missing in ATTRIBUTION.md 0 | line present for 48 of 48 (100 %); flagged assets 21, missing in ATTRIBUTION.md 0 | 100 %; 0 missing | % |
| 17 | minutes and USD per full run | 122 min of stages, $5.07 at $2.49/h (26 stage records) | 104 min of stages, $4.34 at $2.49/h (27 stage records) | <= 150 min, <= $6.50 at $2.49/h | min |

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
- 10: scene_manifest.json materials[] (textured shell slots with a maps record naming normal and roughness); built upholstered pieces (sofa, sofa_corner, armchair, ottoman) whose scene object recolour has a fabric slot
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
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | hall | interior | 0 | 3 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_50549dea6434f912fa0134d5ed43f35f164908a4 [non_commercial], hssd_a72d7403a0ea8133a89bff0bfc266d443613420a [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.269 | - |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | hall | interior | 0.17 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.536 | - |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | hall | interior | 0.17 | 3 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_a72d7403a0ea8133a89bff0bfc266d443613420a [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.368 | - |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | kitchen | interior | 6.5 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_sink_kitchen_scandinavian_2_470fa047 [tool_nc], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 0 | 0.157 | - |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | kitchen | interior | 6.5 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_sink_kitchen_scandinavian_2_470fa047 [tool_nc], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 0 | 0.171 | - |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | kitchen | interior | 7 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78a02cbe18b9bac0aedf264e100a73f34fd05023 [non_commercial]) | 0 | 0.238 | - |
| cam_r_L-1_salon_1 | r_L-1_salon | living | interior | 3.5 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_50549dea6434f912fa0134d5ed43f35f164908a4 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.283 | - |
| cam_r_L-1_salon_2 | r_L-1_salon | living | interior | 3.17 | 1.83 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_50549dea6434f912fa0134d5ed43f35f164908a4 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.296 | - |
| cam_r_L-1_salon_3 | r_L-1_salon | living | interior | 3.33 | 1.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_018f52ea0b259b9134aaa3685171d7ffe624c3dc [non_commercial], hssd_50549dea6434f912fa0134d5ed43f35f164908a4 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cb3ded4460b53bfe63437e8d950482cfc8f88610 [non_commercial]) | 0 | 0.223 | - |
| cam_r_L0_banyo_1 | r_L0_banyo | bathroom | interior | -0.67 | 1.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.499 | - |
| cam_r_L0_banyo_2 | r_L0_banyo | bathroom | interior | -0.83 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.614 | - |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | bathroom | interior | -0.33 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.626 | - |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | bathroom | interior | -0.5 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.723 | - |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | bedroom | interior | 7.67 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.18 | - |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | bedroom | interior | 6.17 | 1.83 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc]) | 0 | 0.361 | - |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | bedroom | interior | 6.5 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.259 | - |
| cam_r_L0_koridor_1 | r_L0_koridor | hall | interior | 0.5 | 3 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.159 | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | bedroom | interior | 6.33 | 2.5 | 4 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.483 | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | bedroom | interior | 7 | 2 | 4 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_scandinavian_2_20075b95 [tool_nc]) | 0 | 0.552 | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | bedroom | interior | 6.5 | 1.83 | 4 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_scandinavian_2_20075b95 [tool_nc]) | 0 | 0.533 | - |
| cam_r_L0_yatak_odasi_4_1 | r_L0_yatak_odasi_4 | bedroom | interior | -0.17 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.321 | - |
| cam_r_L0_yatak_odasi_4_2 | r_L0_yatak_odasi_4 | bedroom | interior | -0.17 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.486 | - |
| cam_r_L0_yatak_odasi_4_3 | r_L0_yatak_odasi_4 | bedroom | interior | -0.17 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.405 | - |
| cam_r_L1_banyo_1 | r_L1_banyo | bathroom | interior | -1.33 | 1.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.527 | - |
| cam_r_L1_banyo_2 | r_L1_banyo | bathroom | interior | -1.33 | 1.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_df8abd46ef3dd6017f6863558381655f1510d275 [non_commercial]) | 0 | 0.632 | - |
| cam_r_L1_koridor_1 | r_L1_koridor | hall | interior | -0.83 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.549 | - |
| cam_r_L1_koridor_2 | r_L1_koridor | hall | interior | -0.83 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial]) | 0 | 0.512 | - |
| cam_r_L1_koridor_2_1 | r_L1_koridor_2 | hall | interior | -1 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.577 | - |
| cam_r_L1_koridor_2_2 | r_L1_koridor_2 | hall | interior | -1 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial]) | 0 | 0.483 | - |
| cam_r_L1_koridor_2_3 | r_L1_koridor_2 | hall | interior | -1 | 3 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.496 | - |
| cam_r_L1_koridor_3 | r_L1_koridor | hall | interior | -0.83 | 3 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_japandi_1_32d3b9fb [tool_nc], hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial]) | 0 | 0.457 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial]) | 0 | 0.313 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial]) | 0 | 0.326 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial]) | 0 | 0.296 | - |
| cam_r_L1_teras_1 | r_L1_teras | balcony | interior | -1 | -3.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.339 | - |
| cam_r_L1_teras_2 | r_L1_teras | balcony | interior | -1 | -3.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.34 | - |
| cam_r_L1_teras_2_1 | r_L1_teras_2 | balcony | interior | -1.17 | -7.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | 0.385 | - |
| cam_r_L1_teras_2_2 | r_L1_teras_2 | balcony | interior | -1.17 | -7.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | 0.479 | - |
| cam_r_L1_teras_2_3 | r_L1_teras_2 | balcony | interior | -1 | -7.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | 0.482 | - |
| cam_r_L1_teras_3 | r_L1_teras | balcony | interior | -0.67 | -3.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.487 | - |
| ext_1 | - | - | exterior | -0.17 | -4 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | no data | - |
| ext_2 | - | - | exterior | -0.33 | -4.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | no data | - |
| ext_3 | - | - | exterior | - | -7.67 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_4 | - | - | exterior | - | -4.5 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_5 | - | - | exterior | -1.33 | -7.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | no data | - |
| ext_7 | - | - | exterior | -1.33 | -7.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | no data | - |

Views only in the baseline: cam_r_L0_koridor_2, cam_r_L0_koridor_3.

## Warnings

- orchestrator log: the latest run from seq 2925 (1439 of 4363 events; earlier runs of the appended log left out)
- rubric: no file (results layout under /home/user/WenArt_RUN/runs/20261016-172855-full/results/final/real04)
- baseline: render: no file (results layout under /home/user/WenArt_RUN/results/final/real04)
- baseline: scene: no file (results layout under /home/user/WenArt_RUN/results/final/real04)
