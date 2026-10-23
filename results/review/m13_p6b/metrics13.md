# Milestone 13 metrics: real03

After: `/home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/final/real03` (results layout). Before (baseline): `/home/user/WenArt_RUN/results/final/real03` (results layout, project real03). Definitions: docs/milestone13.md §7 and the docstring of wenart/report/metrics13.py; a metric says "no data" when the file it needs is missing.

## Inputs

| input | after | before |
|---|---|---|
| building | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/furniture/real03/building_final.json | /home/user/WenArt_RUN/results/furniture/real03/building_final.json |
| scene | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/renders/real03/scene_manifest.json | /home/user/WenArt_RUN/results/renders/real03/scene_manifest.json |
| render | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/renders/real03/render_manifest.json | /home/user/WenArt_RUN/results/renders/real03/render_manifest.json |
| final | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/final/real03/final_manifest.json | /home/user/WenArt_RUN/results/final/real03/final_manifest.json |
| report | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/final/real03/final_report.md | /home/user/WenArt_RUN/results/final/real03/final_report.md |
| attribution | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/final/real03/ATTRIBUTION.md | /home/user/WenArt_RUN/results/final/real03/ATTRIBUTION.md |
| log | /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/agent/real03/log.json | /home/user/WenArt_RUN/results/agent/real03/log.json |
| rubric | missing | /home/user/WenArt_RUN/results/review/m13_step0/real03_per_view.json |

## The 17 metrics

| # | metric | before | after | target | unit |
|---|---|---|---|---|---|
| 1 | drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk) | 15 of 15 (100 %) | 27 of 27 (100 %) | 100 % | % |
| 2 | drawn pieces in the scene (built, method not none) | 130 of 165 (79 %); without the 26 explained non-furniture pieces: 130 of 139 (94 %) | 145 of 171 (85 %); without the 25 explained non-furniture pieces: 145 of 146 (99 %) | >= 90 % | % |
| 3 | pieces with asset.method none | 0 | 2 | 0 | count |
| 4 | parametric share of the built pieces; grey boxes | 70 of 158 (44 %) parametric of the built pieces; 104 of 193 (54 %) of every fitted piece; module 0; grey boxes 42 | 12 of 154 (8 %) parametric of the built pieces; 36 of 178 (20 %) of every fitted piece; module 24; grey boxes 0 | <= 25 %; 0 | % |
| 5 | rooms with a complete group set | bathroom 0/8; bedroom 2/9; living 0/8 | bathroom 8/8; bedroom 3/9; living 4/8 | >= 90 % of the furnished main rooms | % |
| 6 | last-round findings F8 + S2 (> 3 cm) + G10 + LG | round 5: F8 0 / S2 > 3 cm 0 (S2 all 0) / G10 0 / LG 0 | round 4: F8 0 / S2 > 3 cm 8 (S2 all 11) / G10 11 / LG 4 | <= 5 / <= 3 / report-only / <= 5 | count |
| 7 | accepted agent edits whose finding is gone next round | 11 of 16 (69 %) (accepted edits 16, rounds 5) | 21 of 24 (88 %) (accepted edits 24, rounds 4) | >= 60 % (or the agent is off) | % |
| 8 | built library pieces: top model share; distinct; units unknown; stretch > 5 %; quality <= 3 | top objaverse_68e164f1a9414c29820ac2eaf6d8ac04 10 of 88 (11 %); distinct 33; units unknown 35 of 88 (40 %); stretch > 5 % 33 of 88 (38 %); quality <= 3 28 of 88 (32 %) | top hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 8 of 118 (7 %); distinct 66; units unknown 2 of 118 (2 %); stretch > 5 % 0 of 118 (0 %); quality <= 3 8 of 43 (19 %) | <= 15 %; >= 60; <= 10 %; <= 10 %; <= 25 % | % |
| 9 | interior views at EV >= +5; EV median gap lit vs daylight rooms | 27 of 83 interior views at EV >= +5; gap 5.17 EV (median -0.50 over 12 views of rooms without a window vs +4.67 over 71 views of rooms with one) | 0 of 83 interior views at EV >= +5; gap 0.75 EV (median +1.75 over 12 views of rooms without a window vs +1.00 over 71 views of rooms with one) | 0; <= 2 EV | count |
| 10 | shell slots on PBR sets with normal + roughness; fabric colour applied | shell slots with normal + roughness: no data (maps not recorded in the scene manifest); fabric colour applied: 0 of 11 (0 %) (recoloured 0, module / parametric fabric slot 0; colour asked but the model has no recolourable fabric slot: 0 piece(s), 0 model(s); no fabric colour asked: 11 piece(s)) (11 upholstered pieces built) | shell slots with normal + roughness: 19 of 19 (100 %); fabric colour applied: 3 of 8 (38 %) (recoloured 3, module / parametric fabric slot 0; colour asked but the model has no recolourable fabric slot: 5 piece(s), 3 model(s); no fabric colour asked: 0 piece(s)) (8 upholstered pieces built) | >= 90 %; 100 % | % |
| 11 | drawn trees built as real geometry; hedges from the drawn rows; black pixels in the site view | no drawn tree; no tree in the scene; hedges 0 built of 0 drawn rows; black pixels in the site view no data | no drawn tree; trees in the scene (inferred) as real geometry 2 of 2 (100 %); hedges 5 built of 0 drawn rows; black pixels in the site view no data (no aerial or site view: ext_5 (aerial) dropped: flat_cut roof (upper floors not drawn): no aerial view) | 100 %; 2; 0 % | % |
| 12 | exterior views rendered of planned | 0 of 0 (0 dropped) | 6 of 7 (1 dropped: ext_5) | 7 of 7 | count |
| 13 | views in halls or with >= 50 % bare wall | 29 of 83 views: halls 21, bare wall >= 50 % 14 | 29 of 89 views: halls 21, bare wall >= 50 % 14 | <= 4 | count |
| 14 | in_json_not_rendered mismatches of the final check | 2 in 2 view(s) | 0 in 0 view(s) | 0 | count |
| 15 | rubric score (reviewer, same rubric) | mean 1.83 over 83 views; 28 at 1; 1 at 4-5 (1 %) | no reviewer rubric file | mean >= 3.0; 0 at 1; >= 25 % at 4-5 | score |
| 16 | commercial-safe line present; ATTRIBUTION lists every flagged asset | line present for 0 of 83 (0 %); flagged assets 0, missing in ATTRIBUTION.md 0 | line present for 89 of 89 (100 %); flagged assets 32, missing in ATTRIBUTION.md 0 | 100 %; 0 missing | % |
| 17 | minutes and USD per full run | 56 min of stages, $2.32 at $2.49/h (26 stage records) | 146 min of stages, $6.06 at $2.49/h (27 stage records) | <= 150 min, <= $6.50 at $2.49/h | min |

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
| cam_r_L0_banyo_1 | r_L0_banyo | bathroom | interior | -0.5 | 1.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.698 | - |
| cam_r_L0_banyo_2_1 | r_L0_banyo_2 | bathroom | interior | -0.5 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.698 | - |
| cam_r_L0_banyo_3_1 | r_L0_banyo_3 | bathroom | interior | -0.17 | 1.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_6cd2dc2611c27f758c972b4874efad8c8cbd5d29 [non_commercial], hssd_7835135c9a3abefa43deca495710555800d8aeca [non_commercial]) | 0 | 0.289 | - |
| cam_r_L0_banyo_4_1 | r_L0_banyo_4 | bathroom | interior | -0.5 | 1.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_762d42fce4ff28d319112e66bde33c3f4329c175 [non_commercial]) | 0 | 0.434 | - |
| cam_r_L0_banyo_4_2 | r_L0_banyo_4 | bathroom | interior | -0.5 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial], hssd_762d42fce4ff28d319112e66bde33c3f4329c175 [non_commercial]) | 0 | 0.512 | - |
| cam_r_L0_banyo_5_1 | r_L0_banyo_5 | bathroom | interior | -0.17 | 1.83 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_43fa24cb165eb3bfde976d070bfd615f41c78028 [non_commercial], hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial]) | 0 | 0.49 | - |
| cam_r_L0_banyo_5_2 | r_L0_banyo_5 | bathroom | interior | -0.33 | 1.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_573d7dcc478330c40f3b05b9473a2fda1236c3e4 [non_commercial], hssd_ae556cf9509ae72d95a6ffd0bdb3864bf5fcea6c [non_commercial]) | 0 | 0.68 | - |
| cam_r_L0_banyo_6_1 | r_L0_banyo_6 | bathroom | interior | -0.67 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_6b6d600719446182c0a798676eb807c0ea4ec772 [non_commercial]) | 0 | 0.393 | - |
| cam_r_L0_banyo_6_2 | r_L0_banyo_6 | bathroom | interior | -0.83 | 2 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_31609de54bc7b3cceb58cff41b88b69d7f7db9ec [non_commercial]) | 0 | 0.383 | - |
| cam_r_L0_banyo_7_1 | r_L0_banyo_7 | bathroom | interior | -0.67 | 1.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_ead365ee0f62fd7ab510ffb80417061b626087b7 [non_commercial]) | 0 | 0.651 | - |
| cam_r_L0_banyo_8_1 | r_L0_banyo_8 | bathroom | interior | -0.67 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_b74cfc2ae648ddcf1375088e23d9643b7c5ed736 [non_commercial]) | 0 | 0.488 | - |
| cam_r_L0_ebeveyn_odasi_1 | r_L0_ebeveyn_odasi | bedroom | interior | 4.5 | 0.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial]) | 0 | 0.344 | - |
| cam_r_L0_ebeveyn_odasi_2 | r_L0_ebeveyn_odasi | bedroom | interior | 4.5 | 0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_589bcc23d287e1669b4acaf573d0affdc4e058d5 [non_commercial]) | 0 | 0.169 | - |
| cam_r_L0_ebeveyn_odasi_2_1 | r_L0_ebeveyn_odasi_2 | bedroom | interior | 4.5 | 0 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.27 | - |
| cam_r_L0_ebeveyn_odasi_2_2 | r_L0_ebeveyn_odasi_2 | bedroom | interior | 4.5 | 0.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.335 | - |
| cam_r_L0_ebeveyn_odasi_2_3 | r_L0_ebeveyn_odasi_2 | bedroom | interior | 4.5 | 0 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_52e54d4aedff229ec50eefe25bd168c60141c37f [non_commercial]) | 0 | 0.336 | - |
| cam_r_L0_ebeveyn_odasi_3_1 | r_L0_ebeveyn_odasi_3 | bedroom | interior | 4.83 | 0 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial]) | 0 | 0.343 | - |
| cam_r_L0_ebeveyn_odasi_3_2 | r_L0_ebeveyn_odasi_3 | bedroom | interior | 4.17 | -0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_55178b6f7cfabac7480cc6e677b8223227604907 [non_commercial]) | 0 | 0.149 | - |
| cam_r_L0_ebeveyn_odasi_4_1 | r_L0_ebeveyn_odasi_4 | bedroom | interior | 8 | -0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.411 | - |
| cam_r_L0_ebeveyn_odasi_4_2 | r_L0_ebeveyn_odasi_4 | bedroom | interior | 8 | -0.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_xxxxbeae246cx5cbcx482dx81faxd6e6f844d62d [non_commercial]) | 0 | 0.48 | - |
| cam_r_L0_ebeveyn_odasi_4_3 | r_L0_ebeveyn_odasi_4 | bedroom | interior | 8 | -0.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.47 | - |
| cam_r_L0_ebeveyn_odasi_5_1 | r_L0_ebeveyn_odasi_5 | bedroom | interior | 5.67 | 1.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.325 | - |
| cam_r_L0_ebeveyn_odasi_5_2 | r_L0_ebeveyn_odasi_5 | bedroom | interior | 5.5 | 1.83 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.264 | - |
| cam_r_L0_ebeveyn_odasi_5_3 | r_L0_ebeveyn_odasi_5 | bedroom | interior | 5.5 | 2.17 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.28 | - |
| cam_r_L0_ebeveyn_odasi_6_1 | r_L0_ebeveyn_odasi_6 | bedroom | interior | 5.83 | 1.83 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.305 | - |
| cam_r_L0_ebeveyn_odasi_6_2 | r_L0_ebeveyn_odasi_6 | bedroom | interior | 6 | 2.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.181 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_1 | r_L0_ebeveyn_odasi_m_k_a | bedroom | interior | 4.83 | 1.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.33 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2 | r_L0_ebeveyn_odasi_m_k_a | bedroom | interior | 5 | 1.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.312 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_1 | r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | interior | 5 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_rustic_4_694dfd55 [tool_nc]) | 0 | 0.281 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_2 | r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | interior | 5.33 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_small_rustic_4_694dfd55 [tool_nc]) | 0 | 0.309 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_2_3 | r_L0_ebeveyn_odasi_m_k_a_2 | bedroom | interior | 5 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_modern_minimal_1_06ccb749 [tool_nc], gen_plant_small_rustic_4_694dfd55 [tool_nc]) | 0 | 0.348 | - |
| cam_r_L0_ebeveyn_odasi_m_k_a_3 | r_L0_ebeveyn_odasi_m_k_a | bedroom | interior | 5.17 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_modern_4_2b0c9146 [tool_nc]) | 0 | 0.334 | - |
| cam_r_L0_giris_holu_1 | r_L0_giris_holu | hall | interior | 7.83 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial]) | 0 | 0.392 | - |
| cam_r_L0_giris_holu_2 | r_L0_giris_holu | hall | interior | 8 | 2.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial]) | 0 | 0.517 | - |
| cam_r_L0_giris_holu_2_1 | r_L0_giris_holu_2 | hall | interior | 8 | 2.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial]) | 0 | 0.391 | - |
| cam_r_L0_giris_holu_2_2 | r_L0_giris_holu_2 | hall | interior | 8 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.572 | - |
| cam_r_L0_giris_holu_3_1 | r_L0_giris_holu_3 | hall | interior | 8 | 2.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_3c69f2f448fd917843cc2ef9082e80000907ee25 [non_commercial]) | 0 | 0.255 | - |
| cam_r_L0_giris_holu_4_1 | r_L0_giris_holu_4 | hall | interior | 8 | 2.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial]) | 0 | 0.324 | - |
| cam_r_L0_giris_holu_4_2 | r_L0_giris_holu_4 | hall | interior | 8 | 2.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_4bc6f883a374400355bcf95e611a4e8f8b950ed5 [non_commercial]) | 0 | 0.43 | - |
| cam_r_L0_kat_holu_1 | r_L0_kat_holu | hall | interior | -0.33 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.537 | - |
| cam_r_L0_kat_holu_2 | r_L0_kat_holu | hall | interior | -0.33 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.501 | - |
| cam_r_L0_kat_holu_3 | r_L0_kat_holu | hall | interior | -0.17 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.457 | - |
| cam_r_L0_kat_merdiveni_1 | r_L0_kat_merdiveni | stair | interior | -0.67 | 2.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.341 | - |
| cam_r_L0_kat_merdiveni_2 | r_L0_kat_merdiveni | stair | interior | -0.17 | 2.5 | 4 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.333 | - |
| cam_r_L0_kat_merdiveni_3 | r_L0_kat_merdiveni | stair | interior | -0.5 | 2.33 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.41 | - |
| cam_r_L0_oda_01_1 | r_L0_oda_01 | bedroom | interior | 4.33 | -0.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.486 | - |
| cam_r_L0_oda_01_2 | r_L0_oda_01 | bedroom | interior | 4.67 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.486 | - |
| cam_r_L0_oda_01_3 | r_L0_oda_01 | bedroom | interior | 5 | -0.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.479 | - |
| cam_r_L0_oda_10_1 | r_L0_oda_10 | hall | interior | 0 | 2.5 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.094 | - |
| cam_r_L0_oda_19_1 | r_L0_oda_19 | balcony | interior | -0.67 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.524 | - |
| cam_r_L0_oda_19_2 | r_L0_oda_19 | balcony | interior | -0.67 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.524 | - |
| cam_r_L0_oda_19_3 | r_L0_oda_19 | balcony | interior | -0.67 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.484 | - |
| cam_r_L0_oda_7_1 | r_L0_oda_7 | hall | interior | 0.17 | 2.67 | 1 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.062 | - |
| cam_r_L0_ruzgarlik_1 | r_L0_ruzgarlik | hall | interior | 4.5 | 1 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial]) | 0 | 0.383 | - |
| cam_r_L0_ruzgarlik_2 | r_L0_ruzgarlik | hall | interior | 4.67 | 1 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial]) | 0 | 0.241 | - |
| cam_r_L0_ruzgarlik_3 | r_L0_ruzgarlik | hall | interior | 4.67 | 0.83 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_85a85b8d95fa810baeaebaf0d04d6c931d23ed3b [non_commercial]) | 0 | 0.503 | - |
| cam_r_L0_yangin_merdiveni_1 | r_L0_yangin_merdiveni | stair | interior | -0.67 | 2.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.42 | - |
| cam_r_L0_yangin_merdiveni_2 | r_L0_yangin_merdiveni | stair | interior | -0.17 | 1 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.503 | - |
| cam_r_L0_yangin_merdiveni_3 | r_L0_yangin_merdiveni | stair | interior | 3.67 | 1.83 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.495 | - |
| cam_r_L0_yasama_1 | r_L0_yasama | living | interior | 4 | 0.67 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 0 | 0.332 | - |
| cam_r_L0_yasama_2 | r_L0_yasama | living | interior | 3.83 | 0.67 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.377 | - |
| cam_r_L0_yasama_2_1 | r_L0_yasama_2 | living | interior | 5.33 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.244 | - |
| cam_r_L0_yasama_2_2 | r_L0_yasama_2 | living | interior | 5.5 | 1.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.304 | - |
| cam_r_L0_yasama_2_3 | r_L0_yasama_2 | living | interior | 4.83 | 0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_79ad3c2f9e40b87e3a22d82bec28cbfb4f0ab627 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.232 | - |
| cam_r_L0_yasama_3 | r_L0_yasama | living | interior | 4 | 1.17 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial]) | 0 | 0.343 | - |
| cam_r_L0_yasama_3_1 | r_L0_yasama_3 | living | interior | 4.67 | -0.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.286 | - |
| cam_r_L0_yasama_3_2 | r_L0_yasama_3 | living | interior | 4.17 | 0 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.305 | - |
| cam_r_L0_yasama_3_3 | r_L0_yasama_3 | living | interior | 4.33 | -0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_240225989a0ed75d14f4663e867dbb065e2880b4 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_eccf8ba37c804b9067e675f09eec2c13e951f61c [non_commercial]) | 0 | 0.315 | - |
| cam_r_L0_yasama_4_1 | r_L0_yasama_4 | living | interior | 3.83 | 1.17 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.508 | - |
| cam_r_L0_yasama_4_2 | r_L0_yasama_4 | living | interior | 3.67 | 0.67 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.354 | - |
| cam_r_L0_yasama_4_3 | r_L0_yasama_4 | living | interior | 3.83 | 0.33 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_31b5ec475d6fdcbb9461561c0a3bbe22dee18e99 [non_commercial], hssd_50d2f90f2ef2466c22a1d1da45fc657763cbfb2a [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.313 | - |
| cam_r_L0_yasama_5_1 | r_L0_yasama_5 | living | interior | 3.83 | 0 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.154 | - |
| cam_r_L0_yasama_5_2 | r_L0_yasama_5 | living | interior | 4.83 | 0 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.261 | - |
| cam_r_L0_yasama_5_3 | r_L0_yasama_5 | living | interior | 4.67 | 0 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial]) | 0 | 0.231 | - |
| cam_r_L0_yasama_6_1 | r_L0_yasama_6 | living | interior | 5.83 | 0 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.311 | - |
| cam_r_L0_yasama_6_2 | r_L0_yasama_6 | living | interior | 6 | 1.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.227 | - |
| cam_r_L0_yasama_6_3 | r_L0_yasama_6 | living | interior | 5.5 | 1.33 | 1 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: hssd_40667dfcf9d1c152d8bf09f7b7e045b85dd67240 [non_commercial], hssd_78da408a3864493508ff2078d9ef2c0b1ff81b93 [non_commercial], hssd_a87ae8e3bd9b8c3c45d3330cbac583baa957c3bb [non_commercial], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.281 | - |
| cam_r_L0_yasama_7_1 | r_L0_yasama_7 | living | interior | 3.67 | -1.67 | 3 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc]) | 0 | 0.271 | - |
| cam_r_L0_yasama_7_2 | r_L0_yasama_7 | living | interior | 3.17 | -0.5 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_potted_plant_industrial_3_23920a8f [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.264 | - |
| cam_r_L0_yasama_7_3 | r_L0_yasama_7 | living | interior | 3.83 | -1.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_potted_plant_industrial_3_23920a8f [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.354 | - |
| cam_r_L0_yasama_8_1 | r_L0_yasama_8 | living | interior | 4.83 | -0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: no (flagged assets: gen_plant_large_scandinavian_1_2265e7c5 [tool_nc], hssd_d1bb1e76ecd549767fd650aa211e3ce29be75ad6 [non_commercial]) | 0 | 0.309 | - |
| cam_r_L0_yasama_8_2 | r_L0_yasama_8 | living | interior | 5 | -1 | 3 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.357 | - |
| cam_r_L0_yasama_8_3 | r_L0_yasama_8 | living | interior | 4.83 | -0.83 | 2 | no data | commercial-safe: not recorded | commercial-safe: yes | 0 | 0.244 | - |
| ext_1 | - | - | exterior | - | -7.5 | - | no data | - | commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial]) | 0 | no data | - |
| ext_2 | - | - | exterior | - | -6.5 | - | no data | - | commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial]) | 0 | no data | - |
| ext_3 | - | - | exterior | - | -5 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_4 | - | - | exterior | - | -6.33 | - | no data | - | commercial-safe: yes | 0 | no data | - |
| ext_6 | - | - | exterior | - | -7.67 | - | no data | - | commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial]) | 0 | no data | - |
| ext_7 | - | - | exterior | - | -7.83 | - | no data | - | commercial-safe: no (flagged assets: hssd_69340d8678701e72f39cc01890da1b8af3fd603d [non_commercial]) | 0 | no data | - |

## Warnings

- orchestrator log: the latest run from seq 1614 (1240 of 2853 events; earlier runs of the appended log left out)
- rubric: no file (results layout under /home/user/WenArt_RUN/runs/20261022-235127-fetch_results/results/final/real03)
