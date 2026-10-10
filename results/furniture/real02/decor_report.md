# Decor: real02

AI decor (docs/milestone9.md §4): 98 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 24 rooms; 4 items by the rules (M4/M8) in 1 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | 23 | 12 / 9 | 5 | blind, cushion, cushion, cushion, cushion, cushion, cushion, cushion, pendant_light, rug, wall_art | - | - |
| Mutfak (r_L-1_mutfak) | kitchen | 4 | 3 / 3 | 3 | blind, pendant_light, vase | - | - |
| Banyo (r_L-1_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Oda (r_L-1b_oda) | other | 11 | 5 / 5 | 3 | cushion, plant_large, table_lamp | - | - |
| Banyo (r_L-1b_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Banyo (r_L-1b_banyo_2) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | 10 | 9 / 8 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| E.yatak Odası (r_L0_e_yatak_odasi) | bedroom | 10 | 9 / 8 | 8 | book_set, curtain, cushion, cushion, pendant_light, plant_small, rug, throw, wall_art | - | - |
| E.banyo (r_L0_e_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Yatak Odası (r_L0_yatak_odasi_3) | bedroom | 0 | - / - | 0 | cushion, cushion | - | no slot for AI decor |
| Banyo (r_L0_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi) | other | 11 | 5 / 5 | 4 | basket, curtain, cushion, cushion, cushion | - | - |
| Koridor (r_L1_koridor) | hall | 4 | 3 / 3 | 1 | mirror | - | - |
| Banyo (r_L1_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Banyo (r_L-1_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| Koridor (r_L-1_koridor) | hall | 0 | - / - | 0 | - | - | - |
| Mutfak (r_L-1_mutfak_2) | kitchen | 0 | - / - | 0 | blind, pendant_light, vase | - | - |
| Salon (r_L-1_salon_2) | living | 0 | - / - | 0 | blind, cushion, cushion, cushion, cushion, cushion, cushion, cushion, pendant_light, rug, wall_art | - | - |
| Koridor (r_L-1b_koridor_2) | hall | 0 | - / - | 0 | - | - | - |
| Oda (r_L-1b_oda_2) | other | 0 | - / - | 0 | cushion, plant_large, table_lamp | - | - |
| Banyo (r_L0_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| E.banyo (r_L0_e_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| E.yatak Odası (r_L0_e_yatak_odasi_2) | bedroom | 0 | - / - | 0 | book_set, curtain, cushion, cushion, pendant_light, plant_small, rug, throw, wall_art | - | - |
| Koridor (r_L0_koridor_2) | hall | 0 | - / - | 0 | - | - | - |
| Merdiven (r_L0_merdiven_2) | hall | 0 | - / - | 0 | - | - | - |
| Yatak Odası (r_L0_yatak_odasi_2) | bedroom | 0 | - / - | 0 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Yatak Odası (r_L0_yatak_odasi_4) | bedroom | 0 | - / - | 0 | cushion, cushion | - | - |
| Banyo (r_L1_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| Koridor (r_L1_koridor_2) | hall | 0 | - / - | 0 | mirror | - | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | other | 0 | - / - | 0 | basket, curtain, cushion, cushion, cushion | - | - |
| Teras (r_L1_teras_2) | balcony | 0 | - / - | 0 | - | - | - |

Items only one pass chose (not built):

- r_L-1_salon: throw in f_L-1_053.throw (pass 1)
- r_L-1_salon: vase in f_L-1_073.centre (pass 1)
- r_L-1_salon: table_lamp in f_L-1_091.left (pass 1)
- r_L-1_salon: plant_small in f_L-1_089.left (pass 1)
- r_L-1_salon: book_set in f_L-1_089.right (pass 1)
- r_L-1_salon: cushion in f_L-1_049.cushions (pass 1)
- r_L-1_salon: cushion in f_L-1_090.cushions (pass 1)
- r_L-1_salon: cushion in f_L-1_061.cushions (pass 2)
- r_L-1_salon: plant_small in f_L-1_073.centre (pass 2)
- r_L-1_salon: plant_small in f_L-1_091.left (pass 2)
- r_L-1_salon: vase in f_L-1_091.right (pass 2)
- r_L-1b_oda: pendant_light in ceiling:over_f_L-1b_065 (pass 1)
- r_L-1b_oda: wall_art in f_L-1b_061.wall (pass 1)
- r_L-1b_oda: vase in f_L-1b_065.centre (pass 2)
- r_L-1b_oda: ceiling_light in ceiling:centre_r_L-1b_oda (pass 2)
- r_L0_yatak_odasi: table_lamp in f_L0_039.centre (pass 1)
- r_L0_yatak_odasi: plant_small in f_L0_040.centre (pass 1)
- r_L0_yatak_odasi: ceiling_light in ceiling:centre_r_L0_yatak_odasi (pass 1)
- r_L0_yatak_odasi: plant_small in f_L0_039.centre (pass 2)
- r_L0_yatak_odasi: book_set in f_L0_040.centre (pass 2)
- r_L0_e_yatak_odasi: cushion in f_L0_044.cushions (pass 1)
- r_L1_oyun_aktivite_ve_dinlenme_odasi: cushion in f_L1_012.cushions (pass 1)
- r_L1_oyun_aktivite_ve_dinlenme_odasi: pendant_light in ceiling:centre_r_L1_oyun_aktivite_ve_dinlenme_odasi (pass 2)
- r_L1_koridor: vase in f_L1_032.left (pass 1)
- r_L1_koridor: pendant_light in ceiling:centre_r_L1_koridor (pass 1)
- r_L1_koridor: plant_small in f_L1_032.left (pass 2)
- r_L1_koridor: ceiling_light in ceiling:centre_r_L1_koridor (pass 2)

Places left out:

- r_L-1_salon: f_L-1_053 wall: wall_art: f_L-1_053 has no wall behind it
- r_L-1_salon: f_L-1_061 wall: wall_art: f_L-1_061 has no wall behind it
- r_L-1_salon: no rug: no coffee table in front of a sofa
- r_L-1_salon: no free corner for a floor plant
- r_L-1_salon: window win_L-1_001: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yatak_odasi: no free corner for a floor plant
- r_L0_e_yatak_odasi: no free corner for a floor plant
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_009 wall: wall_art: f_L1_009 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_012 wall: wall_art: f_L1_012 has no wall behind it
- r_L1_koridor: no free corner for a floor plant
- r_L-1_banyo_2: decor copied from r_L-1_banyo (twin, not asked)
- r_L-1_koridor: decor copied from r_L-1_koridor_2 (twin, not asked)
- r_L-1_mutfak_2: decor copied from r_L-1_mutfak (twin, not asked)
- r_L-1_salon_2: decor copied from r_L-1_salon (twin, not asked)
- r_L-1b_koridor_2: decor copied from r_L-1b_koridor (twin, not asked)
- r_L-1b_oda_2: decor copied from r_L-1b_oda (twin, not asked)
- r_L0_banyo_2: decor copied from r_L0_banyo (twin, not asked)
- r_L0_e_banyo_2: decor copied from r_L0_e_banyo (twin, not asked)
- r_L0_e_yatak_odasi_2: decor copied from r_L0_e_yatak_odasi (twin, not asked)
- r_L0_koridor_2: decor copied from r_L0_koridor (twin, not asked)
- r_L0_merdiven_2: decor copied from r_L0_merdiven (twin, not asked)
- r_L0_yatak_odasi_2: decor copied from r_L0_yatak_odasi (twin, not asked)
- r_L0_yatak_odasi_4: decor copied from r_L0_yatak_odasi_3 (twin, not asked)
- r_L1_banyo_2: decor copied from r_L1_banyo (twin, not asked)
- r_L1_koridor_2: decor copied from r_L1_koridor (twin, not asked)
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: decor copied from r_L1_oyun_aktivite_ve_dinlenme_odasi (twin, not asked)
- r_L1_teras_2: decor copied from r_L1_teras (twin, not asked)
- r_L1_teras_2: r_L-1b_acik_mutfak_2: its twin partner r_L-1b_acik_mutfak cannot be mapped (the twin's drawn furniture does not map onto this room: drawn unknown f_L-1b_044 has no counterpart here); decorated itself
- r_L1_teras_2: r_L-1b_banyo: its same_as partner r_L-1_banyo cannot be mapped (the same_as's drawn furniture does not map onto this room: drawn toilet f_L-1_051 has no counterpart here); decorated itself
- r_L1_teras_2: r_L-1b_banyo_2: its same_as partner r_L-1_banyo_2 cannot be mapped (the same_as's drawn furniture does not map onto this room: drawn toilet f_L-1_052 has no counterpart here); decorated itself
