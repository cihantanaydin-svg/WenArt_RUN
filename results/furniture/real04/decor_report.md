# Decor: real04

AI decor (docs/milestone9.md §4): 88 items chosen by the AI (model Qwen/Qwen3.8-27B-FP8, both passes agreeing, confidence 0.9) in 25 rooms; 0 items by the rules (M4/M8) in 1 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | 7 | 5 / 7 | 5 | blind, book_set, cushion, pendant_light, throw | - | - |
| Mutfak (r_L-1_mutfak) | kitchen | 2 | 2 / 2 | 2 | blind, pendant_light | - | - |
| Banyo (r_L-1_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Oda (r_L-1b_oda) | bedroom | 9 | 8 / 8 | 7 | ceiling_light, cushion, cushion, plant_large, rug, table_lamp, throw, wall_art | - | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | 13 | 8 / 8 | 8 | ceiling_light, curtain, cushion, cushion, plant_small, rug, table_lamp, throw, wall_art | - | - |
| E.yatak Odası (r_L0_e_yatak_odasi) | bedroom | 2 | 2 / 2 | 1 | curtain | - | - |
| E.banyo (r_L0_e_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Yatak Odası (r_L0_yatak_odasi_4) | bedroom | 3 | 3 / 3 | 3 | ceiling_light, curtain, plant_large | - | - |
| Banyo (r_L0_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi) | other | 10 | 4 / 4 | 4 | curtain, cushion, cushion, cushion, cushion | plant_small (the slot leaves 0.37 x 0.27 x 0.15 m, below the smallest plant_small box) | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | other | 10 | 4 / 4 | 4 | curtain, cushion, cushion, cushion, cushion | plant_small (the slot leaves 0.37 x 0.27 x 0.15 m, below the smallest plant_small box) | - |
| Koridor (r_L1_koridor) | hall | 2 | 2 / 2 | 2 | mirror, pendant_light | - | - |
| Koridor (r_L1_koridor_2) | hall | 1 | 1 / 1 | 0 | - | - | the two passes agreed on no item |
| Banyo (r_L1_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Banyo (r_L-1_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| Koridor (r_L-1_koridor) | hall | 0 | - / - | 0 | - | - | - |
| Mutfak (r_L-1_mutfak_2) | kitchen | 0 | - / - | 0 | blind, pendant_light | - | - |
| Salon (r_L-1_salon_2) | living | 0 | - / - | 0 | blind, book_set, cushion, pendant_light, throw | - | - |
| Banyo (r_L-1b_banyo) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| Banyo (r_L-1b_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| Koridor (r_L-1b_koridor_2) | hall | 0 | - / - | 0 | - | - | - |
| Oda (r_L-1b_oda_2) | bedroom | 0 | - / - | 0 | ceiling_light, cushion, cushion, plant_large, rug, table_lamp, throw, wall_art | - | - |
| Banyo (r_L0_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| E.banyo (r_L0_e_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |
| E.yatak Odası (r_L0_e_yatak_odasi_2) | bedroom | 0 | - / - | 0 | curtain | - | - |
| Koridor (r_L0_koridor_2) | hall | 0 | - / - | 0 | - | - | - |
| Merdiven (r_L0_merdiven_2) | hall | 0 | - / - | 0 | - | - | - |
| Yatak Odası (r_L0_yatak_odasi_2) | bedroom | 0 | - / - | 0 | ceiling_light, curtain, cushion, cushion, plant_small, rug, table_lamp, throw, wall_art | - | - |
| Yatak Odası (r_L0_yatak_odasi_3) | bedroom | 0 | - / - | 0 | ceiling_light, curtain, plant_large | - | - |
| Banyo (r_L1_banyo_2) | bathroom | 0 | - / - | 0 | ceiling_light, mirror | - | - |

Items only one pass chose (not built):

- r_L-1_salon: cushion in f_L-1_075.cushions (pass 2)
- r_L-1_salon: cushion in f_L-1_077.cushions (pass 2)
- r_L-1b_oda: plant_small in f_L-1b_073.centre (pass 1)
- r_L-1b_oda: books in f_L-1b_073.centre (pass 2)
- r_L0_e_yatak_odasi: pendant_light in ceiling:centre_r_L0_e_yatak_odasi (pass 1)
- r_L0_e_yatak_odasi: ceiling_light in ceiling:centre_r_L0_e_yatak_odasi (pass 2)
- r_L1_koridor_2: pendant_light in ceiling:centre_r_L1_koridor_2 (pass 1)
- r_L1_koridor_2: ceiling_light in ceiling:centre_r_L1_koridor_2 (pass 2)

Places left out:

- r_L-1_salon: no free corner for a floor plant
- r_L-1_salon: window win_L-1_001: no room for a curtain rod (doors, windows or wall ends)
- r_L0_yatak_odasi: no free corner for a floor plant
- r_L0_e_yatak_odasi: no free corner for a floor plant
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_009 wall: wall_art: f_L1_009 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_012 wall: wall_art: f_L1_012 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_043 wall: wall_art: above f_L1_043: window win_L1_001 on the wall behind it leave 0.00 m for the picture (min 0.4 m); clock: above f_L1_043: window win_L1_001 on the wall behind it leave 0.00 m for the clock (min 0.25 m)
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_010 wall: wall_art: f_L1_010 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_011 wall: wall_art: f_L1_011 has no wall behind it
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_047 wall: wall_art: above f_L1_047: window win_L1_002 on the wall behind it leave 0.00 m for the picture (min 0.4 m); clock: above f_L1_047: window win_L1_002 on the wall behind it leave 0.00 m for the clock (min 0.25 m)
- r_L1_koridor: f_L1_045 left: no decor fits (0.39 x 0.24 m, 0.00 m high)
- r_L1_koridor: f_L1_045 right: no decor fits (0.39 x 0.24 m, 0.00 m high)
- r_L1_koridor: no free corner for a floor plant
- r_L1_koridor_2: f_L1_046 centre: no decor fits (0.54 x 0.24 m, 0.00 m high)
- r_L1_koridor_2: no free corner for a floor plant
- r_L-1_banyo_2: decor copied from r_L-1_banyo (twin, not asked)
- r_L-1_koridor: decor copied from r_L-1_koridor_2 (twin, not asked)
- r_L-1_mutfak_2: decor copied from r_L-1_mutfak (twin, not asked)
- r_L-1_salon_2: decor copied from r_L-1_salon (twin, not asked)
- r_L-1b_banyo: decor copied from r_L-1_banyo (same_as, not asked)
- r_L-1b_banyo_2: decor copied from r_L-1_banyo_2 (same_as, not asked)
- r_L-1b_koridor_2: decor copied from r_L-1b_koridor (twin, not asked)
- r_L-1b_oda_2: decor copied from r_L-1b_oda (twin, not asked)
- r_L0_banyo_2: decor copied from r_L0_banyo (twin, not asked)
- r_L0_e_banyo_2: decor copied from r_L0_e_banyo (twin, not asked)
- r_L0_e_yatak_odasi_2: decor copied from r_L0_e_yatak_odasi (twin, not asked)
- r_L0_koridor_2: decor copied from r_L0_koridor (twin, not asked)
- r_L0_merdiven_2: decor copied from r_L0_merdiven (twin, not asked)
- r_L0_yatak_odasi_2: decor copied from r_L0_yatak_odasi (twin, not asked)
- r_L0_yatak_odasi_3: decor copied from r_L0_yatak_odasi_4 (twin, not asked)
- r_L1_banyo_2: decor copied from r_L1_banyo (twin, not asked)
- r_L1_banyo_2: r_L-1b_salon_2: its twin partner r_L-1b_salon cannot be mapped (the twin's drawn furniture does not map onto this room: drawn unknown f_L-1b_046 has no counterpart here); decorated itself
- r_L1_banyo_2: r_L1_oyun_aktivite_ve_dinlenme_odasi_2: its twin partner r_L1_oyun_aktivite_ve_dinlenme_odasi cannot be mapped (the twin's drawn furniture does not map onto this room: drawn unknown f_L1_033 has no counterpart here); decorated itself
