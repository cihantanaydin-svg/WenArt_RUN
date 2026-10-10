# Decor: synthetic-01

AI decor (docs/milestone9.md §4): 59 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 10 rooms; 0 items by the rules (M4/M8) in 0 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Salon (r_L0_salon) | living | 20 | 16 / 16 | 13 | book_set, candle, curtain, cushion, cushion, cushion, cushion, mirror, plant_small, rug, throw, throw, throw, wall_art | - | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | 11 | 9 / 9 | 8 | curtain, cushion, cushion, pendant_light, plant, plant_small, rug, table_lamp, throw | - | - |
| Hol (r_L0_hol) | hall | 4 | 3 / 3 | 2 | mirror, vase | - | - |
| Banyo (r_L0_banyo) | bathroom | 3 | 3 / 3 | 3 | blind, ceiling_light, mirror | - | - |
| Mutfak (r_L0_mutfak) | kitchen | 2 | 2 / 2 | 2 | blind, pendant_light | - | - |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 13 | 9 / 9 | 8 | curtain, cushion, cushion, plant, plant_small, rug, table_lamp, throw, wall_art | - | - |
| Hol (r_L1_hol) | hall | 7 | 4 / 4 | 3 | mirror, plant, vase | - | - |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 11 | 10 / 8 | 7 | curtain, cushion, cushion, plant_small, rug, table_lamp, throw, wall_art | - | - |
| Banyo (r_L1_banyo) | bathroom | 3 | 3 / 3 | 3 | blind, ceiling_light, mirror | - | - |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 11 | 10 / 7 | 6 | curtain, cushion, plant_small, table_lamp, throw, wall_art | - | - |

Items only one pass chose (not built):

- r_L0_salon: candle in f_L0_020.left (pass 1)
- r_L0_salon: tray in f_L0_020.right (pass 1)
- r_L0_salon: blind in window:win_L0_002 (pass 1)
- r_L0_salon: book_set in f_L0_005.shelf (pass 2)
- r_L0_salon: tray in f_L0_020.left (pass 2)
- r_L0_salon: candle in f_L0_020.right (pass 2)
- r_L0_yatak_odasi: wall_art in f_L0_006.wall (pass 1)
- r_L0_yatak_odasi: cushion in f_L0_021.cushions (pass 2)
- r_L0_hol: pendant_light in ceiling:centre_r_L0_hol (pass 1)
- r_L0_hol: ceiling_light in ceiling:centre_r_L0_hol (pass 2)
- r_L1_ebeveyn_yatak_odasi: pendant_light in ceiling:over_f_L1_001 (pass 1)
- r_L1_ebeveyn_yatak_odasi: ceiling_light in ceiling:over_f_L1_001 (pass 2)
- r_L1_hol: pendant_light in ceiling:centre_r_L1_hol (pass 1)
- r_L1_hol: ceiling_light in ceiling:centre_r_L1_hol (pass 2)
- r_L1_yatak_odasi: plant in r_L1_yatak_odasi.corner1 (pass 1)
- r_L1_yatak_odasi: pendant_light in ceiling:over_f_L1_010 (pass 1)
- r_L1_yatak_odasi: ceiling_light in ceiling:centre_r_L1_yatak_odasi (pass 1)
- r_L1_yatak_odasi: ceiling_light in ceiling:over_f_L1_010 (pass 2)
- r_L1_cocuk_odasi: book_set in f_L1_020.back_right (pass 1)
- r_L1_cocuk_odasi: clock in f_L1_020.wall (pass 1)
- r_L1_cocuk_odasi: plant in r_L1_cocuk_odasi.corner1 (pass 1)
- r_L1_cocuk_odasi: pendant_light in ceiling:over_f_L1_017 (pass 1)
- r_L1_cocuk_odasi: ceiling_light in ceiling:over_f_L1_017 (pass 2)

Places left out:

- r_L0_salon: no free corner for a floor plant
- r_L0_hol: no free corner for a floor plant
- r_L1_ebeveyn_yatak_odasi: f_L1_005 wall: wall_art: above f_L1_005: window win_L1_001 on the wall behind it leave 0.00 m for the picture (min 0.4 m); clock: above f_L1_005: window win_L1_001 on the wall behind it leave 0.00 m for the clock (min 0.25 m)
