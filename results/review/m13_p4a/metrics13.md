# Milestone 13 metrics: real02

After: `/home/user/WenArt_RUN/runs/20261017-072801-full/results/final/real02` (results layout). Before (baseline): `/home/user/WenArt_RUN/results/final/real02` (results layout, project real02). Definitions: docs/milestone13.md §7 and the docstring of wenart/report/metrics13.py; a metric says "no data" when the file it needs is missing.

## Inputs

| input | after | before |
|---|---|---|
| building | /home/user/WenArt_RUN/runs/20261017-072801-full/results/furniture/real02/building_final.json | /home/user/WenArt_RUN/results/furniture/real02/building_final.json |
| scene | /home/user/WenArt_RUN/runs/20261017-072801-full/results/renders/real02/scene_manifest.json | /home/user/WenArt_RUN/results/renders/real02/scene_manifest.json |
| render | /home/user/WenArt_RUN/runs/20261017-072801-full/results/renders/real02/render_manifest.json | /home/user/WenArt_RUN/results/renders/real02/render_manifest.json |
| final | /home/user/WenArt_RUN/runs/20261017-072801-full/results/final/real02/final_manifest.json | /home/user/WenArt_RUN/results/final/real02/final_manifest.json |
| report | /home/user/WenArt_RUN/runs/20261017-072801-full/results/final/real02/final_report.md | /home/user/WenArt_RUN/results/final/real02/final_report.md |
| attribution | /home/user/WenArt_RUN/runs/20261017-072801-full/results/final/real02/ATTRIBUTION.md | /home/user/WenArt_RUN/results/final/real02/ATTRIBUTION.md |
| log | /home/user/WenArt_RUN/runs/20261017-072801-full/results/agent/real02/log.json | /home/user/WenArt_RUN/results/agent/real02/log.json |
| rubric | missing | /home/user/WenArt_RUN/results/review/m13_step0/real02_per_view.json |

## The 17 metrics

| # | metric | before | after | target | unit |
|---|---|---|---|---|---|
| 1 | drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk) | 29 of 30 (97 %) | 37 of 38 (97 %) | 100 % | % |
| 2 | drawn pieces in the scene (built, method not none) | 185 of 210 (88 %); without the 12 explained non-furniture pieces: 185 of 198 (93 %) | 183 of 230 (80 %); without the 36 explained non-furniture pieces: 183 of 194 (94 %) | >= 90 % | % |
| 3 | pieces with asset.method none | 0 | 21 | 0 | count |
| 4 | parametric share of the built pieces; grey boxes | 109 of 257 (42 %) parametric of the built pieces; 132 of 282 (47 %) of every fitted piece; module 0; grey boxes 21 | 30 of 233 (13 %) parametric of the built pieces; 56 of 259 (22 %) of every fitted piece; module 22; grey boxes 0 | <= 25 %; 0 | % |
| 5 | rooms with a complete group set | bathroom 10/10; bedroom 6/6; kitchen 0/4; living 2/3 | bathroom 10/10; bedroom 2/8; kitchen 2/2; living 0/4 | >= 90 % of the furnished main rooms | % |
| 6 | last-round findings F8 + S2 (> 3 cm) + G10 + LG | round 4: F8 5 / S2 > 3 cm 0 (S2 all 0) / G10 0 / LG 0 | round 4: F8 9 / S2 > 3 cm 7 (S2 all 13) / G10 18 / LG 14 | <= 5 / <= 3 / report-only / <= 5 | count |
| 7 | accepted agent edits whose finding is gone next round | 12 of 41 (29 %) (accepted edits 50, rounds 4) | 17 of 25 (68 %) (accepted edits 25, rounds 4) | >= 60 % (or the agent is off) | % |
| 8 | built library pieces: top model share; distinct; units unknown; stretch > 5 %; quality <= 3 | top objaverse_d2785b57e7da45858f2fe8bf4dedd68d 42 of 148 (28 %); distinct 30; units unknown 76 of 148 (51 %); stretch > 5 % 79 of 148 (53 %); quality <= 3 6 of 148 (4 %) | top objaverse_3446229dce1f47528fa871cc7669136c 10 of 181 (6 %); distinct 83; units unknown 11 of 181 (6 %); stretch > 5 % 0 of 181 (0 %); quality <= 3 37 of 56 (66 %) | <= 15 %; >= 60; <= 10 %; <= 10 %; <= 25 % | % |
| 9 | interior views at EV >= +5; EV median gap lit vs daylight rooms | 9 of 35 interior views at EV >= +5; gap 6.92 EV (median -0.67 over 19 views of rooms without a window vs +6.25 over 16 views of rooms with one) | 0 of 41 interior views at EV >= +5; gap 2.67 EV (median +2.00 over 22 views of rooms without a window vs -0.67 over 19 views of rooms with one); 2 view(s) held at the EV cap (lighting_dark: 0 critical, 2 major), counted at their metered EV | 0; <= 2 EV | count |
| 10 | shell slots on PBR sets with normal + roughness; fabric colour applied | shell slots with normal + roughness: no data (maps not recorded in the scene manifest); fabric colour applied: 0 of 23 (0 %) (23 upholstered pieces built) | shell slots with normal + roughness: 18 of 18 (100 %); fabric colour applied: 0 of 16 (0 %) (16 upholstered pieces built) | >= 90 %; 100 % | % |
| 11 | drawn trees built as real geometry; hedges from the drawn rows; black pixels in the site view | trees built 0 of 0 (0 drawn); hedges 1 built of 0 drawn rows; black pixels in the site view 0.0 % (ext_5) | trees built 2 of 0 (0 drawn); hedges 6 built of 0 drawn rows; black pixels in the site view 0.0 % (ext_5) | 100 %; 2; 0 % | % |
| 12 | exterior views rendered of planned | 6 of 6 (0 dropped) | 7 of 6 (0 dropped) | 7 of 7 | count |
| 13 | views in halls or with >= 50 % bare wall | 16 of 41 views: halls 9, bare wall >= 50 % 11 | 19 of 48 views: halls 12, bare wall >= 50 % 12 | <= 4 | count |
| 14 | in_json_not_rendered mismatches of the final check | 0 in 0 view(s) | 3 in 3 view(s) | 0 | count |
| 15 | rubric score (reviewer, same rubric) | mean 1.90 over 41 views; 8 at 1; 0 at 4-5 (0 %) | no data | mean >= 3.0; 0 at 1; >= 25 % at 4-5 | score |
| 16 | commercial-safe line present; ATTRIBUTION lists every flagged asset | line present for 0 of 41 (0 %); flagged assets 0, missing in ATTRIBUTION.md 0 | line present for 48 of 48 (100 %); flagged assets 20, missing in ATTRIBUTION.md 0 | 100 %; 0 missing | % |
| 17 | minutes and USD per full run | 29 min of stages, $1.22 at $2.49/h (24 stage records) | 80 min of stages, $3.34 at $2.49/h (27 stage records) | <= 150 min, <= $6.50 at $2.49/h | min |

Sources:

- 1: building_final.json furniture[]: source from_documents, type or drawn_type in ANCHOR_TYPES; built = build not false and asset.method in library / module / parametric
- 2: building_final.json furniture[]: source from_documents; built = build not false and asset.method not none; parts furniture / built_of_furniture leave out the unbuilt pieces explained as no furniture (inferred_as rug / detail / column / decor, both AI passes not_furniture, a counter-leg detail)
- 3: building_final.json furniture[].asset.method == none
- 4: building_final.json: built pieces (build not false, method not none) by asset.method; fitted = pieces with an asset whose method is not none (the unbuilt ones count, §7); grey boxes = scene_manifest.json objects of kind furniture_proxy
- 5: building_final.json rooms[].room_type x ROOM_SETS over the built furniture and decor of each room (furnished main rooms: rooms of a set type with at least one built piece)
- 6: orchestrator log.json finding events of the last round of the latest run (run_first_seq; not dropped) by checklist; S2 counted when evidence.metrics.depth_m > 0.03 m
- 7: orchestrator log.json of the latest run (run_first_seq): accepted edit events of round r < last with checklist and target; gone = no finding with the same checklist and target in round r + 1
- 8: building_final.json built pieces with asset.method library: asset_id counts, units_known, fit_scale (max / min - 1 > 5 %), quality (lower M8 judge <= 3) or a catalogue audit vision_doubt
- 9: render_manifest.json (else final_manifest.json views) exposure.ev of the interior views, the metered EV (lighting_dark metrics.ev_wanted) for a view the +3 cap held; window rooms from the scene manifest's window objects (room_ids); gap = median EV (no window) - median EV (window)
- 10: scene_manifest.json materials[] (textured shell slots with a maps record naming normal and roughness); built upholstered pieces (sofa, sofa_corner, armchair, ottoman) whose scene object recolour has a fabric slot
- 11: building_final.json site.decor (kind tree) and site.hedges; scene_manifest.json site.vegetation / site.trees records (method not a primitive), site hedge objects; black pixels (every channel < 16) of the aerial / site camera's final preview
- 12: scene_manifest.json cameras (kind exterior) + cameras_dropped = planned; render_manifest.json / final_manifest.json exterior views = rendered
- 13: views whose room (building rooms[].room_type, else the final manifest's room_type) is a hall type (hall, corridor, vestibule, landing, stair) or whose scene camera score.shares.wall >= 0.5
- 14: final_manifest.json views[].json_crosscheck.in_json_not_rendered
- 15: the reviewer's per-view rubric file (client_ready_score 1-5), over the views of the final report
- 16: final_manifest.json views[].commercial_safe and the commercial-safe lines of final_report.md; the flagged asset ids against final/ATTRIBUTION.md
- 17: the stage seconds of the run (run/*.json records of the run id, else final_manifest.json run_stages) / 60; USD at 2.49 USD per GPU hour (WENART_GPU_USD_PER_H overrides); the pod's wall time is longer (setup, downloads: docs/gpu-log.md)

## Per view

| camera | room | type | kind | EV before | EV after | score before | score after | commercial-safe before | commercial-safe after | in_json_not_rendered | bare wall | rubric tags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cam_r_L-1_banyo_1 | r_L-1_banyo | bathroom | interior | -0.83 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.502 | - |
| cam_r_L-1_banyo_2 | r_L-1_banyo | bathroom | interior | -0.83 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_2991e695ef8215a75b43d63417caed6a7c5c0fed [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.576 | - |
| cam_r_L-1_koridor_2_1 | r_L-1_koridor_2 | hall | interior | -0.17 | 2.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial]) | 0 | 0.264 | - |
| cam_r_L-1_koridor_2_2 | r_L-1_koridor_2 | hall | interior | 0.17 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial]) | 0 | 0.569 | - |
| cam_r_L-1_koridor_2_3 | r_L-1_koridor_2 | hall | interior | 0.33 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial]) | 0 | 0.437 | - |
| cam_r_L-1_mutfak_1 | r_L-1_mutfak | kitchen | interior | 8 | 1.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_fridge_mediterranean_3_e70ec886 [tool_nc], hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 1 | 0.148 | - |
| cam_r_L-1_mutfak_2 | r_L-1_mutfak | kitchen | interior | 8 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 1 | 0.165 | - |
| cam_r_L-1_mutfak_3 | r_L-1_mutfak | kitchen | interior | 8 | 1.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_a354f2a1205878521964e4eb5fc968981549c6fe [non_commercial]) | 1 | 0.157 | - |
| cam_r_L-1_salon_1 | r_L-1_salon | living | interior | 4.17 | 3 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial]) | 0 | 0.221 | - |
| cam_r_L-1_salon_2 | r_L-1_salon | living | interior | 3.67 | 3 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial]) | 0 | 0.25 | - |
| cam_r_L-1_salon_3 | r_L-1_salon | living | interior | 3.83 | 2.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_0ef97f65cbf5ec5a97e982db08cfb42533d8dc12 [non_commercial], hssd_c70bd1ccbbc01c9e8354858deb36b5a61df1b0ae [non_commercial], hssd_cad4f138344f6fc378d72b05e0584155649f1ad6 [non_commercial]) | 0 | 0.25 | - |
| cam_r_L0_banyo_1 | r_L0_banyo | bathroom | interior | -0.67 | 1.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.502 | - |
| cam_r_L0_banyo_2 | r_L0_banyo | bathroom | interior | -0.67 | 2.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial], hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.576 | - |
| cam_r_L0_e_banyo_1 | r_L0_e_banyo | bathroom | interior | -0.5 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.635 | - |
| cam_r_L0_e_banyo_2 | r_L0_e_banyo | bathroom | interior | -0.5 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.56 | - |
| cam_r_L0_e_yatak_odasi_1 | r_L0_e_yatak_odasi | bedroom | interior | 6.17 | -1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_japandi_5_92708e0b [tool_nc]) | 0 | 0.303 | - |
| cam_r_L0_e_yatak_odasi_2 | r_L0_e_yatak_odasi | bedroom | interior | 6.33 | -1.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_japandi_5_92708e0b [tool_nc]) | 0 | 0.369 | - |
| cam_r_L0_e_yatak_odasi_3 | r_L0_e_yatak_odasi | bedroom | interior | 7.17 | -1 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.309 | - |
| cam_r_L0_koridor_1 | r_L0_koridor | hall | interior | 0.67 | 2.67 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.136 | - |
| cam_r_L0_koridor_2 | r_L0_koridor | hall | interior | 0.17 | 2.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.441 | - |
| cam_r_L0_koridor_3 | r_L0_koridor | hall | interior | 0 | 2.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.54 | - |
| cam_r_L0_yatak_odasi_1 | r_L0_yatak_odasi | bedroom | interior | 7.17 | -0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.442 | - |
| cam_r_L0_yatak_odasi_2 | r_L0_yatak_odasi | bedroom | interior | 6.67 | -0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_49c43df0f4010e965d68f8f748c9810b335ca4a7 [non_commercial]) | 0 | 0.434 | - |
| cam_r_L0_yatak_odasi_3 | r_L0_yatak_odasi | bedroom | interior | 6.83 | -0.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.448 | - |
| cam_r_L0_yatak_odasi_3_1 | r_L0_yatak_odasi_3 | bedroom | interior | -0.83 | -0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial]) | 0 | 0.375 | - |
| cam_r_L0_yatak_odasi_3_2 | r_L0_yatak_odasi_3 | bedroom | interior | -0.83 | -0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial]) | 0 | 0.445 | - |
| cam_r_L0_yatak_odasi_3_3 | r_L0_yatak_odasi_3 | bedroom | interior | -0.67 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial]) | 0 | 0.538 | - |
| cam_r_L1_banyo_1 | r_L1_banyo | bathroom | interior | -1 | 0.83 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_c6ffbbcdb60a0cf942ce85663aa54754cd760551 [non_commercial]) | 0 | 0.474 | - |
| cam_r_L1_koridor_1 | r_L1_koridor | hall | interior | -1 | 2.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_5ae72d0e8fdadc834a6de0b722be6f259c587c96 [non_commercial]) | 0 | 0.411 | - |
| cam_r_L1_koridor_2 | r_L1_koridor | hall | interior | -1.17 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.576 | - |
| cam_r_L1_koridor_2_1 | r_L1_koridor_2 | hall | interior | - | 1.83 | - | no data | - | commercial-safe: yes | 0 | 0.567 | - |
| cam_r_L1_koridor_2_2 | r_L1_koridor_2 | hall | interior | - | 2.17 | - | no data | - | commercial-safe: no (flagged assets: hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial], hssd_ac699faed7efa37f5b22c3dde720756e71dbf3b1 [non_commercial]) | 0 | 0.434 | - |
| cam_r_L1_koridor_2_3 | r_L1_koridor_2 | hall | interior | - | 2 | - | no data | - | commercial-safe: no (flagged assets: hssd_8d5bb48091eb674ed2e72177175d7a80e7196f31 [non_commercial]) | 0 | 0.47 | - |
| cam_r_L1_koridor_3 | r_L1_koridor | hall | interior | -1 | 2.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.65 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial]) | 0 | 0.314 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_cc238b28d54e7452ba790f3332d4ba0f6da18b82 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial]) | 0 | 0.356 | - |
| cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | r_L1_oyun_aktivite_ve_dinlenme_odasi | other | interior | 0.67 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b1d8f04a74bc6fe1a303593f1acf0c1c5efb19e7 [non_commercial], hssd_e2470c29a511a8c9f4937a689ee1b9127974a61b [non_commercial], hssd_xxxxedd99980xebeax4c23xabb2xdf610602fc13 [non_commercial]) | 0 | 0.323 | - |
| cam_r_L1_teras_1 | r_L1_teras | balcony | interior | 1.5 | -4.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.37 | - |
| cam_r_L1_teras_2_1 | r_L1_teras_2 | balcony | interior | - | -7.5 | - | no data | - | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | 0.336 | - |
| cam_r_L1_teras_2_2 | r_L1_teras_2 | balcony | interior | - | -5.17 | - | no data | - | commercial-safe: no (flagged assets: hssd_8ca311f2d9dfe726d268e0386285d1a6ac466848 [non_commercial]) | 0 | 0.273 | - |
| cam_r_L1_teras_2_3 | r_L1_teras_2 | balcony | interior | - | -7.67 | - | no data | - | commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial]) | 0 | 0.437 | - |
| ext_1 | - | - | exterior | -0.5 | -4 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial]) | 0 | no data | - |
| ext_2 | - | - | exterior | -0.67 | -4.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial]) | 0 | no data | - |
| ext_3 | - | - | exterior | -1.5 | -7.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial]) | 0 | no data | - |
| ext_4 | - | - | exterior | -1.33 | -6.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | no data | - |
| ext_5 | - | - | exterior | -0.33 | -4.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial]) | 0 | no data | - |
| ext_6 | - | - | exterior | -1.33 | -7.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | no data | - |
| ext_6.001 | - | - | exterior | - | -7.5 | - | no data | - | commercial-safe: no (flagged assets: hssd_4ff59e8070d5ea9934152438923cccb3c0a94c20 [non_commercial]) | 0 | no data | - |

## Warnings

- rubric: no file (results layout under /home/user/WenArt_RUN/runs/20261017-072801-full/results/final/real02)
