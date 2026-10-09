# Decor: synthetic-07

AI decor (docs/milestone9.md §4): 40 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 10 rooms; 0 items by the rules (M4/M8) in 0 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | 21 | 12 / 12 | 7 | cushion, cushion, pendant_light, plant_large, rug, table_lamp, throw, tray | - | - |
| Mutfak (r_L-1_mutfak) | kitchen | 3 | 3 / 3 | 2 | blind, pendant_light | - | - |
| Hol (r_L-1_hol) | hall | 4 | 3 / 3 | 2 | mirror, vase | - | - |
| Salon + Açık Mutfak (r_L-1b_salon_acik_mutfak) | living | 22 | 16 / 10 | 7 | cushion, cushion, pendant_light, plant, rug, table_lamp, throw, wall_art | - | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | 13 | 9 / 8 | 6 | curtain, cushion, cushion, plant, rug, table_lamp, throw | - | - |
| Banyo (r_L0_banyo) | bathroom | 3 | 2 / 2 | 2 | blind, ceiling_light | - | - |
| Hol (r_L0_hol) | hall | 6 | 4 / 4 | 4 | ceiling_light, mirror, plant, vase | - | - |
| Oyun Odası (r_L1_oyun_odasi) | other | 10 | 5 / 5 | 3 | pendant_light, plant_large, table_lamp | - | - |
| Hol (r_L1_hol) | hall | 4 | 3 / 3 | 2 | mirror, vase | - | - |
| Hol (r_L-1b_hol) | hall | 0 | - / - | 0 | mirror, vase | - | - |

Items only one pass chose (not built):

- r_L-1_salon: wall_art in f_L-1_005.wall (pass 1)
- r_L-1_salon: vase in f_L-1_007.centre (pass 1)
- r_L-1_salon: mirror in f_L-1_010.wall (pass 1)
- r_L-1_salon: curtain in window:win_L-1_001 (pass 1)
- r_L-1_salon: ceiling_light in ceiling:centre_r_L-1_salon (pass 1)
- r_L-1_salon: plant_small in f_L-1_007.centre (pass 2)
- r_L-1_salon: vase in f_L-1_008.left (pass 2)
- r_L-1_salon: book_set in f_L-1_008.right (pass 2)
- r_L-1_salon: wall_art in f_L-1_010.wall (pass 2)
- r_L-1_salon: blind in window:win_L-1_001 (pass 2)
- r_L-1_mutfak: bowl in f_L-1_012.centre (pass 1)
- r_L-1_mutfak: vase in f_L-1_012.centre (pass 2)
- r_L-1_hol: pendant_light in ceiling:centre_r_L-1_hol (pass 1)
- r_L-1_hol: ceiling_light in ceiling:centre_r_L-1_hol (pass 2)
- r_L-1b_salon_acik_mutfak: vase in f_L-1b_007.centre (pass 1)
- r_L-1b_salon_acik_mutfak: candle in f_L-1b_008.left (pass 1)
- r_L-1b_salon_acik_mutfak: candle in f_L-1b_008.right (pass 1)
- r_L-1b_salon_acik_mutfak: cushion in f_L-1b_009.cushions (pass 1)
- r_L-1b_salon_acik_mutfak: throw in f_L-1b_009.throw (pass 1)
- r_L-1b_salon_acik_mutfak: table_lamp in f_L-1b_010.right (pass 1)
- r_L-1b_salon_acik_mutfak: mirror in f_L-1b_010.wall (pass 1)
- r_L-1b_salon_acik_mutfak: curtain in window:win_L-1b_001 (pass 1)
- r_L-1b_salon_acik_mutfak: curtain in window:win_L-1b_002 (pass 1)
- r_L-1b_salon_acik_mutfak: plant_small in f_L-1b_007.centre (pass 2)
- r_L-1b_salon_acik_mutfak: vase in f_L-1b_010.right (pass 2)
- r_L-1b_salon_acik_mutfak: blind in window:win_L-1b_001 (pass 2)
- r_L0_yatak_odasi: plant_small in f_L0_007.centre (pass 1)
- r_L0_yatak_odasi: pendant_light in ceiling:over_f_L0_002 (pass 1)
- r_L0_yatak_odasi: ceiling_light in ceiling:centre_r_L0_yatak_odasi (pass 1)
- r_L0_yatak_odasi: book_set in f_L0_007.centre (pass 2)
- r_L0_yatak_odasi: ceiling_light in ceiling:over_f_L0_002 (pass 2)
- r_L1_oyun_odasi: wall_art in f_L1_002.wall (pass 1)
- r_L1_oyun_odasi: curtain in window:win_L1_001 (pass 1)
- r_L1_oyun_odasi: plant_small in f_L1_002.back_right (pass 2)
- r_L1_oyun_odasi: cushion in f_L1_004.cushions (pass 2)
- r_L1_hol: pendant_light in ceiling:centre_r_L1_hol (pass 1)
- r_L1_hol: ceiling_light in ceiling:centre_r_L1_hol (pass 2)

Places left out:

- r_L-1_hol: no free corner for a floor plant
- r_L0_yatak_odasi: f_L0_002 wall: wall_art: f_L0_002 has no wall behind it
- r_L0_banyo: f_L0_005 wall: mirror: f_L0_005 has no wall behind it
- r_L1_hol: no free corner for a floor plant
- r_L-1b_hol: decor copied from r_L-1_hol (same_as, not asked)
