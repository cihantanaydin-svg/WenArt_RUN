# Decor: real01

AI decor (docs/milestone9.md §4): 33 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 6 rooms; 0 items by the rules (M4/M8) in 0 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Bed Room (r_L0_bed_room) | bedroom | 9 | 7 / 7 | 6 | curtain, cushion, cushion, plant_small, rug, table_lamp, throw | - | - |
| Bath+ Toilet (r_L0_bath_toilet) | bathroom | 2 | 2 / 2 | 2 | ceiling_light, mirror | - | - |
| Drawing Room (r_L0_drawing_room) | living | 10 | 9 / 9 | 9 | book_set, candle, curtain, cushion, cushion, pendant_light, plant, rug, throw, vase | - | - |
| Bed Room (r_L0_bed_room_2) | bedroom | 9 | 8 / 7 | 7 | curtain, cushion, cushion, pendant_light, plant, rug, table_lamp, throw | - | - |
| Kitchen (r_L0_kitchen) | kitchen | 3 | 3 / 2 | 2 | blind, pendant_light | - | - |
| Dining (r_L0_dining) | dining | 10 | 5 / 5 | 4 | curtain, pendant_light, rug, vase | - | - |

Items only one pass chose (not built):

- r_L0_bed_room: pendant_light in ceiling:over_f_L0_007 (pass 1)
- r_L0_bed_room: ceiling_light in ceiling:over_f_L0_007 (pass 2)
- r_L0_bed_room_2: curtain in window:win_L0_008 (pass 1)
- r_L0_kitchen: blind in window:win_L0_009 (pass 1)
- r_L0_dining: wall_art in f_L0_027.wall (pass 1)
- r_L0_dining: mirror in f_L0_027.wall (pass 2)

Places left out:

- r_L0_bed_room: f_L0_007 wall: wall_art: above f_L0_007: window win_L0_001 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_bed_room: no free corner for a floor plant
- r_L0_drawing_room: f_L0_017 wall: wall_art: above f_L0_017: window win_L0_002 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_bed_room_2: f_L0_004 wall: wall_art: above f_L0_004: window win_L0_004 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
