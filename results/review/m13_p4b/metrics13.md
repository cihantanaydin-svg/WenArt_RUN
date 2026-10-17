# Milestone 13 metrics: real03

After: `/home/user/WenArt_RUN/runs/20261017-091212-full/results/final/real03` (results layout). Before (baseline): `/home/user/WenArt_RUN/results/final/real03` (results layout, project real03). Definitions: docs/milestone13.md §7 and the docstring of wenart/report/metrics13.py; a metric says "no data" when the file it needs is missing.

## Inputs

| input | after | before |
|---|---|---|
| building | /home/user/WenArt_RUN/runs/20261017-091212-full/results/furniture/real03/building_final.json | /home/user/WenArt_RUN/results/furniture/real03/building_final.json |
| scene | /home/user/WenArt_RUN/runs/20261017-091212-full/results/renders/real03/scene_manifest.json | /home/user/WenArt_RUN/results/renders/real03/scene_manifest.json |
| render | /home/user/WenArt_RUN/runs/20261017-091212-full/results/renders/real03/render_manifest.json | /home/user/WenArt_RUN/results/renders/real03/render_manifest.json |
| final | /home/user/WenArt_RUN/runs/20261017-091212-full/results/final/real03/final_manifest.json | /home/user/WenArt_RUN/results/final/real03/final_manifest.json |
| report | /home/user/WenArt_RUN/runs/20261017-091212-full/results/final/real03/final_report.md | /home/user/WenArt_RUN/results/final/real03/final_report.md |
| attribution | /home/user/WenArt_RUN/runs/20261017-091212-full/results/final/real03/ATTRIBUTION.md | /home/user/WenArt_RUN/results/final/real03/ATTRIBUTION.md |
| log | /home/user/WenArt_RUN/runs/20261017-091212-full/results/agent/real03/log.json | /home/user/WenArt_RUN/results/agent/real03/log.json |
| rubric | missing | /home/user/WenArt_RUN/results/review/m13_step0/real03_per_view.json |

## The 17 metrics

| # | metric | before | after | target | unit |
|---|---|---|---|---|---|
| 1 | drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk) | 15 of 15 (100 %) | 26 of 26 (100 %) | 100 % | % |
| 2 | drawn pieces in the scene (built, method not none) | 130 of 165 (79 %); without the 26 explained non-furniture pieces: 130 of 139 (94 %) | 138 of 171 (81 %); without the 25 explained non-furniture pieces: 138 of 146 (95 %) | >= 90 % | % |
| 3 | pieces with asset.method none | 0 | 2 | 0 | count |
| 4 | parametric share of the built pieces; grey boxes | 70 of 158 (44 %) parametric of the built pieces; 104 of 193 (54 %) of every fitted piece; module 0; grey boxes 42 | 14 of 151 (9 %) parametric of the built pieces; 45 of 182 (25 %) of every fitted piece; module 22; grey boxes 0 | <= 25 %; 0 | % |
| 5 | rooms with a complete group set | bathroom 0/8; bedroom 2/9; living 0/8 | bathroom 2/8; bedroom 3/9; living 4/8 | >= 90 % of the furnished main rooms | % |
| 6 | last-round findings F8 + S2 (> 3 cm) + G10 + LG | round 5: F8 0 / S2 > 3 cm 0 (S2 all 0) / G10 0 / LG 0 | round 4: F8 0 / S2 > 3 cm 14 (S2 all 18) / G10 11 / LG 6 | <= 5 / <= 3 / report-only / <= 5 | count |
| 7 | accepted agent edits whose finding is gone next round | 12 of 16 (75 %) (accepted edits 16, rounds 5) | 38 of 47 (81 %) (accepted edits 48, rounds 4) | >= 60 % (or the agent is off) | % |
| 8 | built library pieces: top model share; distinct; units unknown; stretch > 5 %; quality <= 3 | top objaverse_68e164f1a9414c29820ac2eaf6d8ac04 10 of 88 (11 %); distinct 33; units unknown 35 of 88 (40 %); stretch > 5 % 33 of 88 (38 %); quality <= 3 28 of 88 (32 %) | top hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 8 of 115 (7 %); distinct 72; units unknown 5 of 115 (4 %); stretch > 5 % 0 of 115 (0 %); quality <= 3 8 of 49 (16 %) | <= 15 %; >= 60; <= 10 %; <= 10 %; <= 25 % | % |
| 9 | interior views at EV >= +5; EV median gap lit vs daylight rooms | 27 of 83 interior views at EV >= +5; gap 5.17 EV (median -0.50 over 12 views of rooms without a window vs +4.67 over 71 views of rooms with one) | 0 of 83 interior views at EV >= +5; gap 1.33 EV (median +2.50 over 12 views of rooms without a window vs +1.17 over 71 views of rooms with one) | 0; <= 2 EV | count |
| 10 | shell slots on PBR sets with normal + roughness; fabric colour applied | shell slots with normal + roughness: no data (maps not recorded in the scene manifest); fabric colour applied: 0 of 11 (0 %) (11 upholstered pieces built) | shell slots with normal + roughness: 18 of 18 (100 %); fabric colour applied: 3 of 8 (38 %) (8 upholstered pieces built) | >= 90 %; 100 % | % |
| 11 | drawn trees built as real geometry; hedges from the drawn rows; black pixels in the site view | trees built 0 of 0 (0 drawn); hedges 0 built of 0 drawn rows; black pixels in the site view no data | trees built 0 of 0 (0 drawn); hedges 0 built of 0 drawn rows; black pixels in the site view 1.9 % (ext_6) | 100 %; 2; 0 % | % |
| 12 | exterior views rendered of planned | 0 of 0 (0 dropped) | 6 of 8 (2 dropped) | 7 of 7 | count |
| 13 | views in halls or with >= 50 % bare wall | 29 of 83 views: halls 21, bare wall >= 50 % 14 | 29 of 89 views: halls 21, bare wall >= 50 % 14 | <= 4 | count |
| 14 | in_json_not_rendered mismatches of the final check | 2 in 2 view(s) | 10 in 10 view(s) | 0 | count |
| 15 | rubric score (reviewer, same rubric) | mean 1.83 over 83 views; 28 at 1; 1 at 4-5 (1 %) | no data | mean >= 3.0; 0 at 1; >= 25 % at 4-5 | score |
| 16 | commercial-safe line present; ATTRIBUTION lists every flagged asset | line present for 0 of 83 (0 %); flagged assets 0, missing in ATTRIBUTION.md 0 | line present for 89 of 89 (100 %); flagged assets 31, missing in ATTRIBUTION.md 0 | 100 %; 0 missing | % |
| 17 | minutes and USD per full run | 56 min of stages, $2.32 at $2.49/h (26 stage records) | 132 min of stages, $5.49 at $2.49/h (27 stage records) | <= 150 min, <= $6.50 at $2.49/h | min |

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
| cam_r_L0_banyo_1 | r_L0_banyo | bathroom | interior | -0.5 | 2.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_e00975f6de5015107944634171269d8700c136a7 [non_commercial]) | 0 | 0.698 | - |
| cam_r_L0_banyo_2_1 | r_L0_banyo_2 | bathroom | interior | -0.5 | 2.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.698 | - |
| cam_r_L0_banyo_3_1 | r_L0_banyo_3 | bathroom | interior | -0.17 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_7835135c9a3abefa43deca495710555800d8aeca [non_commercial], hssd_856317b238f6a70ae6f0afffed1f6d5e3ab7b80c [non_commercial]) | 0 | 0.289 | - |
| cam_r_L0_banyo_4_1 | r_L0_banyo_4 | bathroom | interior | -0.5 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_031024e00569909d466d87df9fead90355ba29e5 [non_commercial], hssd_81222d2540321a5f3bab53c38a4605b0990b5800 [non_commercial]) | 0 | 0.434 | - |
| cam_r_L0_banyo_4_2 | r_L0_banyo_4 | bathroom | interior | -0.5 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_031024e00569909d466d87df9fead90355ba29e5 [non_commercial], hssd_81222d2540321a5f3bab53c38a4605b0990b5800 [non_commercial]) | 0 | 0.512 | - |
| cam_r_L0_banyo_5_1 | r_L0_banyo_5 | bathroom | interior | -0.17 | 2.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial]) | 0 | 0.49 | - |
| cam_r_L0_banyo_5_2 | r_L0_banyo_5 | bathroom | interior | -0.33 | 2.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_c1965c146b48cddf434f6d5407dfc6ac43bde9b7 [non_commercial]) | 0 | 0.68 | - |
| cam_r_L0_banyo_6_1 | r_L0_banyo_6 | bathroom | interior | -0.67 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_01a976d8dd0f7a1f35b01709c20fca6683b94311 [non_commercial]) | 0 | 0.393 | - |
| cam_r_L0_banyo_6_2 | r_L0_banyo_6 | bathroom | interior | -0.83 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_washing_machine_modern_1_f4bdd46e [tool_nc]) | 0 | 0.383 | - |
| cam_r_L0_banyo_7_1 | r_L0_banyo_7 | bathroom | interior | -0.67 | 2.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_94f82d1154b9db0d56038b183832b0dfceff8819 [non_commercial]) | 0 | 0.651 | - |
| cam_r_L0_banyo_8_1 | r_L0_banyo_8 | bathroom | interior | -0.67 | 2.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_shower_scandinavian_1_0ae4a37a [tool_nc]) | 0 | 0.488 | - |
| cam_r_L0_ebeveyn_odasi_1 | r_L0_ebeveyn_odasi | bedroom | interior | 4.5 | 1 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.344 | - |
| cam_r_L0_ebeveyn_odasi_2 | r_L0_ebeveyn_odasi | bedroom | interior | 4.5 | 1.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.169 | - |
| cam_r_L0_ebeveyn_odasi_2_1 | r_L0_ebeveyn_odasi_2 | bedroom | interior | 4.5 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.27 | - |
| cam_r_L0_ebeveyn_odasi_2_2 | r_L0_ebeveyn_odasi_2 | bedroom | interior | 4.5 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.335 | - |
| cam_r_L0_ebeveyn_odasi_2_3 | r_L0_ebeveyn_odasi_2 | bedroom | interior | 4.5 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.336 | - |
| cam_r_L0_ebeveyn_odasi_3_1 | r_L0_ebeveyn_odasi_3 | bedroom | interior | 4.83 | 0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.343 | - |
| cam_r_L0_ebeveyn_odasi_3_2 | r_L0_ebeveyn_odasi_3 | bedroom | interior | 4.17 | 0.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.149 | - |
| cam_r_L0_ebeveyn_odasi_4_1 | r_L0_ebeveyn_odasi_4 | bedroom | interior | 8 | 0.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.411 | - |
| cam_r_L0_ebeveyn_odasi_4_2 | r_L0_ebeveyn_odasi_4 | bedroom | interior | 8 | 0.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_xxxxbeae246cx5cbcx482dx81faxd6e6f844d62d [non_commercial]) | 0 | 0.48 | - |
| cam_r_L0_ebeveyn_odasi_4_3 | r_L0_ebeveyn_odasi_4 | bedroom | interior | 8 | 0 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.47 | - |
| cam_r_L0_ebeveyn_odasi_5_1 | r_L0_ebeveyn_odasi_5 | bedroom | interior | 5.67 | 1.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.325 | - |
| cam_r_L0_ebeveyn_odasi_5_2 | r_L0_ebeveyn_odasi_5 | bedroom | interior | 5.5 | 1.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.264 | - |
| cam_r_L0_ebeveyn_odasi_5_3 | r_L0_ebeveyn_odasi_5 | bedroom | interior | 5.5 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.28 | - |
| cam_r_L0_ebeveyn_odasi_6_1 | r_L0_ebeveyn_odasi_6 | bedroom | interior | 5.83 | 1.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.305 | - |
| cam_r_L0_ebeveyn_odasi_6_2 | r_L0_ebeveyn_odasi_6 | bedroom | interior | 6 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.181 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_1 | r_L0_ebeveyn_odasi_m_k_a | bedroom | interior | 4.83 | 1 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial]) | 0 | 0.33 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2 | r_L0_ebeveyn_odasi_m_k_a | bedroom | interior | 5 | 1.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial]) | 0 | 0.312 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_1 | r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | interior | 5 | 1 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.281 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_2 | r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | interior | 5.33 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.309 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_3 | r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | interior | 5 | 1 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_minimal_4_71886746 [tool_nc]) | 0 | 0.348 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_3 | r_L0_ebeveyn_odasi_m_k_a | bedroom | interior | 5.17 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc], hssd_3fce46b44d59007f02e60c8adf5fc333b0c58528 [non_commercial]) | 0 | 0.334 | - |
| cam_r_L0_giris_holu_1 | r_L0_giris_holu | hall | interior | 7.83 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_2c2b2914fc526f6e8bbe65511ecf58bba0027ec0 [non_commercial]) | 0 | 0.392 | - |
| cam_r_L0_giris_holu_2 | r_L0_giris_holu | hall | interior | 8 | 2.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_2c2b2914fc526f6e8bbe65511ecf58bba0027ec0 [non_commercial]) | 0 | 0.517 | - |
| cam_r_L0_giris_holu_2_1 | r_L0_giris_holu_2 | hall | interior | 8 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_washing_machine_classic_1_dffff7e0 [tool_nc]) | 0 | 0.391 | - |
| cam_r_L0_giris_holu_2_2 | r_L0_giris_holu_2 | hall | interior | 8 | 0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.572 | - |
| cam_r_L0_giris_holu_3_1 | r_L0_giris_holu_3 | hall | interior | 8 | 2.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial]) | 0 | 0.255 | - |
| cam_r_L0_giris_holu_4_1 | r_L0_giris_holu_4 | hall | interior | 8 | 0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial]) | 0 | 0.324 | - |
| cam_r_L0_giris_holu_4_2 | r_L0_giris_holu_4 | hall | interior | 8 | 0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial]) | 0 | 0.43 | - |
| cam_r_L0_kat_holu_1 | r_L0_kat_holu | hall | interior | -0.33 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.537 | - |
| cam_r_L0_kat_holu_2 | r_L0_kat_holu | hall | interior | -0.33 | 2.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.501 | - |
| cam_r_L0_kat_holu_3 | r_L0_kat_holu | hall | interior | -0.17 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.457 | - |
| cam_r_L0_kat_merdiveni_1 | r_L0_kat_merdiveni | stair | interior | -0.67 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.341 | - |
| cam_r_L0_kat_merdiveni_2 | r_L0_kat_merdiveni | stair | interior | -0.17 | 2.33 | 4 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.333 | - |
| cam_r_L0_kat_merdiveni_3 | r_L0_kat_merdiveni | stair | interior | -0.5 | 2.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.41 | - |
| cam_r_L0_oda_01_1 | r_L0_oda_01 | bedroom | interior | 4.33 | 0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.486 | - |
| cam_r_L0_oda_01_2 | r_L0_oda_01 | bedroom | interior | 4.67 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.486 | - |
| cam_r_L0_oda_01_3 | r_L0_oda_01 | bedroom | interior | 5 | 0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.479 | - |
| cam_r_L0_oda_10_1 | r_L0_oda_10 | hall | interior | 0 | 2.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.094 | - |
| cam_r_L0_oda_19_1 | r_L0_oda_19 | unknown | interior | -0.67 | -0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.524 | - |
| cam_r_L0_oda_19_2 | r_L0_oda_19 | unknown | interior | -0.67 | -0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.524 | - |
| cam_r_L0_oda_19_3 | r_L0_oda_19 | unknown | interior | -0.67 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.484 | - |
| cam_r_L0_oda_7_1 | r_L0_oda_7 | hall | interior | 0.17 | 2.83 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.062 | - |
| cam_r_L0_ruzgarlik_1 | r_L0_ruzgarlik | hall | interior | 4.5 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial]) | 0 | 0.383 | - |
| cam_r_L0_ruzgarlik_2 | r_L0_ruzgarlik | hall | interior | 4.67 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial]) | 0 | 0.241 | - |
| cam_r_L0_ruzgarlik_3 | r_L0_ruzgarlik | hall | interior | 4.67 | 1.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial]) | 0 | 0.503 | - |
| cam_r_L0_yangin_merdiveni_1 | r_L0_yangin_merdiveni | stair | interior | -0.67 | 2.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.42 | - |
| cam_r_L0_yangin_merdiveni_2 | r_L0_yangin_merdiveni | stair | interior | -0.17 | 1.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.503 | - |
| cam_r_L0_yangin_merdiveni_3 | r_L0_yangin_merdiveni | stair | interior | 3.67 | 2.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.495 | - |
| cam_r_L0_yasama_1 | r_L0_yasama | living | interior | 4 | 1.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 1 | 0.332 | - |
| cam_r_L0_yasama_2 | r_L0_yasama | living | interior | 3.83 | 1.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 1 | 0.377 | - |
| cam_r_L0_yasama_2_1 | r_L0_yasama_2 | living | interior | 5.33 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial]) | 1 | 0.244 | - |
| cam_r_L0_yasama_2_2 | r_L0_yasama_2 | living | interior | 5.5 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial]) | 0 | 0.304 | - |
| cam_r_L0_yasama_2_3 | r_L0_yasama_2 | living | interior | 4.83 | 0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial]) | 0 | 0.232 | - |
| cam_r_L0_yasama_3 | r_L0_yasama | living | interior | 4 | 1.83 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 1 | 0.343 | - |
| cam_r_L0_yasama_3_1 | r_L0_yasama_3 | living | interior | 4.67 | 0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 1 | 0.286 | - |
| cam_r_L0_yasama_3_2 | r_L0_yasama_3 | living | interior | 4.17 | 0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.305 | - |
| cam_r_L0_yasama_3_3 | r_L0_yasama_3 | living | interior | 4.33 | 0.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.315 | - |
| cam_r_L0_yasama_4_1 | r_L0_yasama_4 | living | interior | 3.83 | 2 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_333fbf609c0f0877768188c43a0a812cc46e26ae [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 1 | 0.508 | - |
| cam_r_L0_yasama_4_2 | r_L0_yasama_4 | living | interior | 3.67 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.354 | - |
| cam_r_L0_yasama_4_3 | r_L0_yasama_4 | living | interior | 3.83 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.313 | - |
| cam_r_L0_yasama_5_1 | r_L0_yasama_5 | living | interior | 3.83 | 0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.154 | - |
| cam_r_L0_yasama_5_2 | r_L0_yasama_5 | living | interior | 4.83 | 0.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.261 | - |
| cam_r_L0_yasama_5_3 | r_L0_yasama_5 | living | interior | 4.67 | 0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.231 | - |
| cam_r_L0_yasama_6_1 | r_L0_yasama_6 | living | interior | 5.83 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 0 | 0.311 | - |
| cam_r_L0_yasama_6_2 | r_L0_yasama_6 | living | interior | 6 | 1.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 0 | 0.227 | - |
| cam_r_L0_yasama_6_3 | r_L0_yasama_6 | living | interior | 5.5 | 1.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 1 | 0.281 | - |
| cam_r_L0_yasama_7_1 | r_L0_yasama_7 | living | interior | 3.67 | -0.5 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc]) | 0 | 0.271 | - |
| cam_r_L0_yasama_7_2 | r_L0_yasama_7 | living | interior | 3.17 | 0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_potted_plant_industrial_2_eb3d21f5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 1 | 0.264 | - |
| cam_r_L0_yasama_7_3 | r_L0_yasama_7 | living | interior | 3.83 | -0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_potted_plant_industrial_2_eb3d21f5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 1 | 0.354 | - |
| cam_r_L0_yasama_8_1 | r_L0_yasama_8 | living | interior | 4.83 | 2.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 1 | 0.309 | - |
| cam_r_L0_yasama_8_2 | r_L0_yasama_8 | living | interior | 5 | 2.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.357 | - |
| cam_r_L0_yasama_8_3 | r_L0_yasama_8 | living | interior | 4.83 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.244 | - |
| ext_1 | - | - | exterior | - | -6.83 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_2 | - | - | exterior | - | -6.5 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_3 | - | - | exterior | - | -4.33 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_4 | - | - | exterior | - | -4.67 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_6 | - | - | exterior | - | -7 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_7 | - | - | exterior | - | -7.17 | - | no data | - | commercial-safe: yes | 0 | no data | - |

## Warnings

- rubric: no file (results layout under /home/user/WenArt_RUN/runs/20261017-091212-full/results/final/real03)
