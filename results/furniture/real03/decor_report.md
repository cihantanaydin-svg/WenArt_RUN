# Decor: real03

AI decor (docs/milestone9.md §4): 102 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 22 rooms; 6 items by the rules (M4/M8) in 2 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Ebeveyn Odası (r_L0_ebeveyn_odasi) | bedroom | 10 | 8 / 8 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_2) | bedroom | 7 | 6 / 6 | 4 | curtain, cushion, cushion, pendant_light, throw | - | - |
| Yaşama (r_L0_yasama) | living | 0 | - / - | 0 | cushion, cushion | - | no slot for AI decor |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_3) | bedroom | 9 | 8 / 7 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_4) | bedroom | 0 | - / - | 0 | cushion, cushion, cushion, cushion | - | no slot for AI decor |
| Yaşama (r_L0_yasama_2) | living | 8 | 7 / 7 | 6 | curtain, curtain, cushion, cushion, pendant_light, plant_small, throw | - | - |
| Oda-01 (r_L0_oda_01) | bedroom | 8 | 7 / 6 | 6 | curtain, cushion, pendant_light, plant_small, throw, wall_art | - | - |
| Yaşama (r_L0_yasama_3) | living | 9 | 9 / 7 | 6 | curtain, curtain, cushion, cushion, pendant_light, plant_small, throw | - | - |
| Banyo (r_L0_banyo) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L0_banyo_2) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L0_banyo_3) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L0_banyo_4) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Yaşama (r_L0_yasama_5) | living | 7 | 7 / 5 | 4 | curtain, curtain, pendant_light, plant_small | - | - |
| Yaşama (r_L0_yasama_6) | living | 8 | 8 / 6 | 4 | curtain, curtain, pendant_light, plant_small | - | - |
| Banyo (r_L0_banyo_5) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L0_banyo_6) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L0_banyo_7) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L0_banyo_8) | bathroom | 2 | 2 / 2 | 2 | blind, ceiling_light | - | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_5) | bedroom | 10 | 8 / 8 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_6) | bedroom | 11 | 9 / 8 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Yaşama (r_L0_yasama_7) | living | 11 | 11 / 9 | 8 | blind, curtain, cushion, cushion, cushion, cushion, pendant_light, plant_small, throw, wall_art | - | - |
| Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a) | bedroom | 12 | 9 / 7 | 6 | curtain, cushion, cushion, rug, table_lamp, throw, wall_art | - | - |
| Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a_2) | bedroom | 11 | 8 / 7 | 5 | curtain, cushion, cushion, plant, table_lamp, throw | - | - |
| Yaşama (r_L0_yasama_8) | living | 9 | 9 / 8 | 7 | blind, curtain, cushion, cushion, cushion, pendant_light, plant_small, throw, wall_art | - | - |

Items only one pass chose (not built):

- r_L0_ebeveyn_odasi: table_lamp in f_L0_166.centre (pass 1)
- r_L0_ebeveyn_odasi: plant_small in f_L0_167.centre (pass 1)
- r_L0_ebeveyn_odasi: plant_small in f_L0_166.centre (pass 2)
- r_L0_ebeveyn_odasi: book_set in f_L0_167.centre (pass 2)
- r_L0_ebeveyn_odasi_2: table_lamp in f_L0_085.centre (pass 1)
- r_L0_ebeveyn_odasi_2: plant_small in f_L0_086.centre (pass 1)
- r_L0_ebeveyn_odasi_2: plant_small in f_L0_085.centre (pass 2)
- r_L0_ebeveyn_odasi_2: table_lamp in f_L0_086.centre (pass 2)
- r_L0_ebeveyn_odasi_3: table_lamp in f_L0_173.centre (pass 1)
- r_L0_ebeveyn_odasi_3: ceiling_light in ceiling:centre_r_L0_ebeveyn_odasi_3 (pass 1)
- r_L0_ebeveyn_odasi_3: plant_small in f_L0_173.centre (pass 2)
- r_L0_yasama_2: plant_small in f_L0_176.right (pass 1)
- r_L0_yasama_2: book_set in f_L0_176.right (pass 2)
- r_L0_oda_01: ceiling_light in ceiling:centre_r_L0_oda_01 (pass 1)
- r_L0_yasama_3: plant_small in f_L0_178.right (pass 1)
- r_L0_yasama_3: blind in window:win_L0_039 (pass 1)
- r_L0_yasama_3: blind in window:win_L0_052 (pass 1)
- r_L0_yasama_3: book_set in f_L0_178.right (pass 2)
- r_L0_yasama_5: plant_small in f_L0_180.right (pass 1)
- r_L0_yasama_5: blind in window:win_L0_039 (pass 1)
- r_L0_yasama_5: blind in window:win_L0_053 (pass 1)
- r_L0_yasama_5: book_set in f_L0_180.right (pass 2)
- r_L0_yasama_6: vase in f_L0_181.right (pass 1)
- r_L0_yasama_6: candle in f_L0_182.left (pass 1)
- r_L0_yasama_6: tray in f_L0_182.right (pass 1)
- r_L0_yasama_6: blind in window:win_L0_040 (pass 1)
- r_L0_yasama_6: tray in f_L0_182.left (pass 2)
- r_L0_yasama_6: book_set in f_L0_181.right (pass 2)
- r_L0_ebeveyn_odasi_5: table_lamp in f_L0_108.centre (pass 1)
- r_L0_ebeveyn_odasi_5: plant_small in f_L0_109.centre (pass 1)
- r_L0_ebeveyn_odasi_5: plant_small in f_L0_108.centre (pass 2)
- r_L0_ebeveyn_odasi_5: book_set in f_L0_109.centre (pass 2)
- r_L0_ebeveyn_odasi_6: table_lamp in f_L0_106.centre (pass 1)
- r_L0_ebeveyn_odasi_6: plant_small in f_L0_107.centre (pass 1)
- r_L0_ebeveyn_odasi_6: ceiling_light in ceiling:centre_r_L0_ebeveyn_odasi_6 (pass 1)
- r_L0_ebeveyn_odasi_6: plant_small in f_L0_106.centre (pass 2)
- r_L0_ebeveyn_odasi_6: book_set in f_L0_107.centre (pass 2)
- r_L0_yasama_7: vase in f_L0_186.right (pass 1)
- r_L0_yasama_7: throw in f_L0_187.throw (pass 1)
- r_L0_yasama_7: cushion in f_L0_188.cushions (pass 1)
- r_L0_yasama_7: book_set in f_L0_186.right (pass 2)
- r_L0_ebeveyn_odasi_m_k_a: plant_small in f_L0_111.centre (pass 1)
- r_L0_ebeveyn_odasi_m_k_a: cushion in f_L0_189.cushions (pass 1)
- r_L0_ebeveyn_odasi_m_k_a: pendant_light in ceiling:over_f_L0_056 (pass 1)
- r_L0_ebeveyn_odasi_m_k_a: ceiling_light in ceiling:over_f_L0_056 (pass 2)
- r_L0_ebeveyn_odasi_m_k_a_2: plant_small in f_L0_113.centre (pass 1)
- r_L0_ebeveyn_odasi_m_k_a_2: rug in r_L0_ebeveyn_odasi_m_k_a_2.rug1 (pass 1)
- r_L0_ebeveyn_odasi_m_k_a_2: pendant_light in ceiling:over_f_L0_057 (pass 1)
- r_L0_ebeveyn_odasi_m_k_a_2: book_set in f_L0_191.left (pass 2)
- r_L0_ebeveyn_odasi_m_k_a_2: ceiling_light in ceiling:over_f_L0_057 (pass 2)
- r_L0_yasama_8: plant_small in f_L0_192.right (pass 1)
- r_L0_yasama_8: cushion in f_L0_193.cushions (pass 1)
- r_L0_yasama_8: book_set in f_L0_192.right (pass 2)

Places left out:

- r_L0_ebeveyn_odasi: no free corner for a floor plant
- r_L0_ebeveyn_odasi: window win_L0_007: no room for a curtain rod (doors, windows or wall ends)
- r_L0_ebeveyn_odasi_2: f_L0_046 wall: wall_art: above f_L0_046: window win_L0_056 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_ebeveyn_odasi_2: no rug under f_L0_046: no free floor around the group
- r_L0_ebeveyn_odasi_2: no free corner for a floor plant
- r_L0_ebeveyn_odasi_2: window win_L0_056: no room for a curtain rod (doors, windows or wall ends)
- r_L0_ebeveyn_odasi_3: no free corner for a floor plant
- r_L0_ebeveyn_odasi_3: window win_L0_024: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_2: f_L0_102 wall: wall_art: above f_L0_102: window win_L0_063 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_yasama_2: no rug: no coffee table in front of a sofa
- r_L0_yasama_2: no free corner for a floor plant
- r_L0_yasama_2: window win_L0_024: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_2: window win_L0_025: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_2: window win_L0_040: no room for a curtain rod (doors, windows or wall ends)
- r_L0_oda_01: no free corner for a floor plant
- r_L0_yasama_3: f_L0_095 wall: wall_art: above f_L0_095: window win_L0_050 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_yasama_3: no rug: no coffee table in front of a sofa
- r_L0_yasama_3: no free corner for a floor plant
- r_L0_yasama_3: window win_L0_007: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_3: window win_L0_008: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_3: window win_L0_039: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_5: no free corner for a floor plant
- r_L0_yasama_5: window win_L0_011: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_5: window win_L0_012: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_5: window win_L0_039: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_6: f_L0_182 wall: wall_art: above f_L0_182: window win_L0_043 on the wall behind it leave 0.00 m for the picture (min 0.4 m); mirror: above f_L0_182: window win_L0_043 on the wall behind it leave 0.00 m for the mirror (min 0.35 m); clock: above f_L0_182: window win_L0_043 on the wall behind it leave 0.00 m for the clock (min 0.25 m)
- r_L0_yasama_6: no free corner for a floor plant
- r_L0_yasama_6: window win_L0_028: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_6: window win_L0_029: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_6: window win_L0_040: no room for a curtain rod (doors, windows or wall ends)
- r_L0_ebeveyn_odasi_5: no free corner for a floor plant
- r_L0_ebeveyn_odasi_5: window win_L0_029: no room for a curtain rod (doors, windows or wall ends)
- r_L0_ebeveyn_odasi_6: no free corner for a floor plant
- r_L0_ebeveyn_odasi_6: window win_L0_012: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_7: no rug: no coffee table in front of a sofa
- r_L0_yasama_7: no free corner for a floor plant
- r_L0_yasama_7: window win_L0_059: no room for a curtain rod (doors, windows or wall ends)
- r_L0_ebeveyn_odasi_m_k_a: f_L0_056 wall: wall_art: above f_L0_056: window win_L0_041 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_ebeveyn_odasi_m_k_a: no free corner for a floor plant
- r_L0_ebeveyn_odasi_m_k_a: window win_L0_041: no room for a curtain rod (doors, windows or wall ends)
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_057 wall: wall_art: above f_L0_057: window win_L0_041 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_191 wall: wall_art: above f_L0_191: window win_L0_048 on the wall behind it leave 0.00 m for the picture (min 0.4 m); mirror: above f_L0_191: window win_L0_048 on the wall behind it leave 0.00 m for the mirror (min 0.35 m); clock: above f_L0_191: window win_L0_048 on the wall behind it leave 0.00 m for the clock (min 0.25 m)
- r_L0_ebeveyn_odasi_m_k_a_2: window win_L0_041: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yasama_8: no rug: no coffee table in front of a sofa
- r_L0_yasama_8: no free corner for a floor plant
- r_L0_yasama_8: window win_L0_055: no room for a curtain rod (doors, windows or wall ends)
