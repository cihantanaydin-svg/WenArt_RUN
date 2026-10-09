# Decor: synthetic-03

AI decor (docs/milestone9.md §4): 67 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 15 rooms; 0 items by the rules (M4/M8) in 0 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Hol (r_L-1_hol) | hall | 7 | 4 / 4 | 3 | mirror, plant, vase | - | - |
| Yatak Odası (r_L-1_yatak_odasi) | bedroom | 14 | 10 / 10 | 7 | blind, cushion, cushion, plant_small, rug, table_lamp, throw, wall_art | - | - |
| WC (r_L-1_wc) | wc | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Banyo (r_L-1_banyo) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Salon (r_L0_salon) | living | 19 | 14 / 10 | 6 | blind, cushion, cushion, pendant_light, rug, throw, wall_art | - | - |
| Hol (r_L0_hol) | hall | 7 | 4 / 3 | 2 | mirror, vase | - | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | 14 | 11 / 11 | 11 | book_set, curtain, cushion, cushion, mirror, pendant_light, plant_small, rug, table_lamp, throw, vase, wall_art | - | - |
| Mutfak (r_L0_mutfak) | kitchen | 3 | 3 / 3 | 2 | blind, pendant_light | - | - |
| Antre (r_L0_antre) | hall | 4 | 3 / 3 | 2 | mirror, vase | - | - |
| WC (r_L0_wc) | wc | 1 | 1 / 1 | 1 | ceiling_light | - | - |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 14 | 11 / 8 | 6 | curtain, cushion, cushion, rug, table_lamp, throw, wall_art | - | - |
| Hol (r_L1_hol) | hall | 7 | 4 / 3 | 2 | mirror, vase | - | - |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 10 | 9 / 8 | 7 | curtain, cushion, cushion, pendant_light, plant, rug, table_lamp, throw | - | - |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 11 | 8 / 7 | 6 | curtain, cushion, plant, table_lamp, throw, wall_art | - | - |
| Banyo (r_L1_banyo) | bathroom | 3 | 3 / 3 | 3 | blind, ceiling_light, mirror | - | - |

Items only one pass chose (not built):

- r_L-1_hol: pendant_light in ceiling:centre_r_L-1_hol (pass 1)
- r_L-1_hol: ceiling_light in ceiling:centre_r_L-1_hol (pass 2)
- r_L-1_yatak_odasi: book_set in f_L-1_006.back_left (pass 1)
- r_L-1_yatak_odasi: clock in f_L-1_006.wall (pass 1)
- r_L-1_yatak_odasi: pendant_light in ceiling:over_f_L-1_003 (pass 1)
- r_L-1_yatak_odasi: vase in f_L-1_006.back_left (pass 2)
- r_L-1_yatak_odasi: plant in r_L-1_yatak_odasi.corner1 (pass 2)
- r_L-1_yatak_odasi: ceiling_light in ceiling:over_f_L-1_003 (pass 2)
- r_L0_salon: tray in f_L0_004.centre (pass 1)
- r_L0_salon: vase in f_L0_005.left (pass 1)
- r_L0_salon: book_set in f_L0_005.right (pass 1)
- r_L0_salon: book_set in f_L0_006.shelf (pass 1)
- r_L0_salon: cushion in f_L0_025.cushions (pass 1)
- r_L0_salon: plant_large in r_L0_salon.corner1 (pass 1)
- r_L0_salon: curtain in window:win_L0_001 (pass 1)
- r_L0_salon: ceiling_light in ceiling:centre_r_L0_salon (pass 1)
- r_L0_salon: blind in window:win_L0_001 (pass 2)
- r_L0_salon: vase in f_L0_004.centre (pass 2)
- r_L0_salon: book_set in f_L0_005.left (pass 2)
- r_L0_salon: candle in f_L0_005.right (pass 2)
- r_L0_hol: plant in r_L0_hol.corner1 (pass 1)
- r_L0_hol: pendant_light in ceiling:centre_r_L0_hol (pass 1)
- r_L0_hol: ceiling_light in ceiling:centre_r_L0_hol (pass 2)
- r_L0_mutfak: bowl in f_L0_011.centre (pass 1)
- r_L0_mutfak: vase in f_L0_011.centre (pass 2)
- r_L0_antre: pendant_light in ceiling:centre_r_L0_antre (pass 1)
- r_L0_antre: ceiling_light in ceiling:centre_r_L0_antre (pass 2)
- r_L1_ebeveyn_yatak_odasi: plant_small in f_L1_003.centre (pass 1)
- r_L1_ebeveyn_yatak_odasi: book_set in f_L1_005.back_left (pass 1)
- r_L1_ebeveyn_yatak_odasi: clock in f_L1_005.wall (pass 1)
- r_L1_ebeveyn_yatak_odasi: plant_large in r_L1_ebeveyn_yatak_odasi.corner1 (pass 1)
- r_L1_ebeveyn_yatak_odasi: pendant_light in ceiling:over_f_L1_001 (pass 1)
- r_L1_ebeveyn_yatak_odasi: plant_small in f_L1_005.back_left (pass 2)
- r_L1_ebeveyn_yatak_odasi: ceiling_light in ceiling:over_f_L1_001 (pass 2)
- r_L1_hol: plant in r_L1_hol.corner1 (pass 1)
- r_L1_hol: pendant_light in ceiling:centre_r_L1_hol (pass 1)
- r_L1_hol: ceiling_light in ceiling:centre_r_L1_hol (pass 2)
- r_L1_yatak_odasi: plant_small in f_L1_011.centre (pass 1)
- r_L1_yatak_odasi: ceiling_light in ceiling:centre_r_L1_yatak_odasi (pass 1)
- r_L1_yatak_odasi: book_set in f_L1_011.centre (pass 2)
- r_L1_cocuk_odasi: plant_small in f_L1_016.back_left (pass 1)
- r_L1_cocuk_odasi: pendant_light in ceiling:over_f_L1_013 (pass 1)
- r_L1_cocuk_odasi: ceiling_light in ceiling:over_f_L1_013 (pass 2)

Places left out:

- r_L0_yatak_odasi: no free corner for a floor plant
- r_L0_yatak_odasi: window win_L0_002: no room for a curtain rod (doors, windows or wall ends)
- r_L0_antre: no free corner for a floor plant
- r_L0_wc: f_L0_020 wall: mirror: above f_L0_020: door d_L0_007 on the wall behind it leave 0.10 m for the mirror (min 0.35 m)
- r_L1_yatak_odasi: f_L1_009 wall: wall_art: above f_L1_009: window win_L1_002 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L1_cocuk_odasi: f_L1_016 wall: wall_art: above f_L1_016: window win_L1_005 on the wall behind it leave 0.00 m for the picture (min 0.4 m); clock: above f_L1_016: window win_L1_005 on the wall behind it leave 0.00 m for the clock (min 0.25 m)
