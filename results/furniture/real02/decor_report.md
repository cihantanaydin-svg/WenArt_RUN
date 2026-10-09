# Decor: real02

AI decor (docs/milestone9.md §4): 53 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 18 rooms; 22 items by the rules (M4/M8) in 3 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | 0 | - / - | 0 | cushion, cushion, cushion, cushion, cushion, cushion, cushion, cushion, cushion | - | no slot for AI decor |
| Banyo (r_L-1_banyo) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Oda (r_L-1b_oda) | other | 11 | 5 / 5 | 2 | cushion, plant_large | - | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | 10 | 9 / 8 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| E.yatak Odası (r_L0_e_yatak_odasi) | bedroom | 9 | 8 / 7 | 5 | curtain, cushion, cushion, pendant_light, rug, throw | - | - |
| E.yatak Odası (r_L0_e_yatak_odasi_2) | bedroom | 10 | 8 / 8 | 6 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| E.banyo (r_L0_e_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Yatak Odası (r_L0_yatak_odasi_3) | bedroom | 0 | - / - | 0 | cushion, cushion | - | no slot for AI decor |
| Yatak Odası (r_L0_yatak_odasi_4) | bedroom | 0 | - / - | 0 | cushion, cushion | - | no slot for AI decor |
| Banyo (r_L0_banyo) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi) | other | 11 | 5 / 5 | 4 | cushion, cushion, pendant_light, plant_large, plant_large | - | - |
| Banyo (r_L1_banyo) | bathroom | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Banyo (r_L-1_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light | - | - |
| Koridor (r_L-1_koridor) | hall | 0 | - / - | 0 | - | - | - |
| Salon (r_L-1_salon_2) | living | 0 | - / - | 0 | cushion, cushion, cushion, cushion, cushion, cushion, cushion, cushion, cushion | - | - |
| Banyo (r_L-1b_banyo) | bathroom | 0 | - / - | 0 | ceiling_light | - | - |
| Banyo (r_L-1b_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light | - | - |
| Koridor (r_L-1b_koridor_2) | hall | 0 | - / - | 0 | - | - | - |
| Oda (r_L-1b_oda_2) | other | 0 | - / - | 0 | cushion, plant_large | - | - |
| Banyo (r_L0_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light | - | - |
| E.banyo (r_L0_e_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| Koridor (r_L0_koridor_2) | hall | 0 | - / - | 0 | - | - | - |
| Yatak Odası (r_L0_yatak_odasi_2) | bedroom | 0 | - / - | 0 | curtain, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Banyo (r_L1_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light | - | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | other | 0 | - / - | 0 | cushion, cushion, pendant_light, plant_large, plant_large | - | - |
| Teras (r_L1_teras_2) | balcony | 0 | - / - | 0 | - | - | - |

Items only one pass chose (not built):

- r_L-1b_oda: table_lamp in f_L-1b_039.back_left (pass 1)
- r_L-1b_oda: pendant_light in ceiling:over_f_L-1b_043 (pass 1)
- r_L-1b_oda: vase in f_L-1b_043.centre (pass 1)
- r_L-1b_oda: plant_small in f_L-1b_039.back_left (pass 2)
- r_L-1b_oda: pendant_light in ceiling:centre_r_L-1b_oda (pass 2)
- r_L-1b_oda: wall_art in f_L-1b_039.wall (pass 2)
- r_L0_yatak_odasi: table_lamp in f_L0_041.centre (pass 1)
- r_L0_yatak_odasi: plant_small in f_L0_042.centre (pass 1)
- r_L0_yatak_odasi: ceiling_light in ceiling:centre_r_L0_yatak_odasi (pass 1)
- r_L0_yatak_odasi: plant_small in f_L0_041.centre (pass 2)
- r_L0_yatak_odasi: book_set in f_L0_042.centre (pass 2)
- r_L0_e_yatak_odasi: table_lamp in f_L0_044.centre (pass 1)
- r_L0_e_yatak_odasi: plant_small in f_L0_045.centre (pass 1)
- r_L0_e_yatak_odasi: ceiling_light in ceiling:centre_r_L0_e_yatak_odasi (pass 1)
- r_L0_e_yatak_odasi: plant_small in f_L0_044.centre (pass 2)
- r_L0_e_yatak_odasi: book_set in f_L0_045.centre (pass 2)
- r_L0_e_yatak_odasi_2: table_lamp in f_L0_050.centre (pass 1)
- r_L0_e_yatak_odasi_2: plant_small in f_L0_051.centre (pass 1)
- r_L0_e_yatak_odasi_2: plant_small in f_L0_050.centre (pass 2)
- r_L0_e_yatak_odasi_2: book_set in f_L0_051.centre (pass 2)
- r_L1_oyun_aktivite_ve_dinlenme_odasi: cushion in f_L1_012.cushions (pass 1)
- r_L1_oyun_aktivite_ve_dinlenme_odasi: cushion in f_L1_029.cushions (pass 2)

Places left out:

- r_L-1_banyo: f_L-1_010 wall: mirror: f_L-1_010 has no wall behind it
- r_L0_yatak_odasi: no free corner for a floor plant
- r_L0_e_yatak_odasi: f_L0_009 wall: wall_art: f_L0_009 has no wall behind it
- r_L0_e_yatak_odasi: no free corner for a floor plant
- r_L0_e_yatak_odasi_2: no free corner for a floor plant
- r_L0_banyo: f_L0_005 wall: mirror: f_L0_005 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_009 wall: wall_art: f_L1_009 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_012 wall: wall_art: f_L1_012 has no wall behind it
- r_L1_banyo: f_L1_007 wall: mirror: f_L1_007 has no wall behind it
- r_L-1_banyo_2: decor copied from r_L-1_banyo (twin, not asked)
- r_L-1_koridor: decor copied from r_L-1_koridor_2 (twin, not asked)
- r_L-1_salon_2: decor copied from r_L-1_salon (twin, not asked)
- r_L-1b_banyo: decor copied from r_L-1_banyo (same_as, not asked)
- r_L-1b_banyo_2: decor copied from r_L-1_banyo_2 (same_as, not asked)
- r_L-1b_koridor_2: decor copied from r_L-1b_koridor (twin, not asked)
- r_L-1b_oda_2: decor copied from r_L-1b_oda (twin, not asked)
- r_L0_banyo_2: decor copied from r_L0_banyo (twin, not asked)
- r_L0_e_banyo_2: decor copied from r_L0_e_banyo (twin, not asked)
- r_L0_koridor_2: decor copied from r_L0_koridor (twin, not asked)
- r_L0_yatak_odasi_2: decor copied from r_L0_yatak_odasi (twin, not asked)
- r_L1_banyo_2: decor copied from r_L1_banyo (twin, not asked)
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: decor copied from r_L1_oyun_aktivite_ve_dinlenme_odasi (twin, not asked)
- r_L1_teras_2: decor copied from r_L1_teras (twin, not asked)
- r_L1_teras_2: r_L-1_mutfak_2: its twin partner r_L-1_mutfak cannot be mapped (the twin's drawn furniture does not map onto this room: drawn fridge f_L-1_031 has no counterpart here); decorated itself
- r_L1_teras_2: r_L0_e_yatak_odasi_2: its twin partner r_L0_e_yatak_odasi cannot be mapped (the twin's drawn furniture does not map onto this room: drawn wardrobe f_L0_025 has no counterpart here); decorated itself
- r_L1_teras_2: r_L0_yatak_odasi_4: its twin partner r_L0_yatak_odasi_3 cannot be mapped (the twin's drawn furniture does not map onto this room: drawn bed_double f_L0_023 has no counterpart here); decorated itself
