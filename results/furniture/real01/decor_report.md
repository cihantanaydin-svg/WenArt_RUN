# Decor: real01

AI decor (docs/milestone9.md §4): 19 items chosen by the AI (model Qwen/Qwen3-VL-8B-Instruct, both passes agreeing, confidence 0.9) in 5 rooms; 0 items by the rules (M4/M8) in 0 rooms where the AI decor did not apply (reason per room). Every item is `added_by_ai`, labelled decor (not furniture); no furniture was moved, added or removed.

| Room | Type | Slots | Pass 1 / pass 2 items | Agreed | Built | Refused | Fallback |
|---|---|---|---|---|---|---|---|
| Bed Room (r_L0_bed_room) | bedroom | 4 | 4 / 4 | 4 | cushion, cushion, plant_small, rug, table_lamp | - | - |
| Bath+ Toilet (r_L0_bath_toilet) | bathroom | 1 | 1 / 1 | 1 | mirror | - | - |
| Drawing Room (r_L0_drawing_room) | living | 4 | 4 / 4 | 4 | cushion, cushion, plant, rug, vase | - | - |
| Bed Room (r_L0_bed_room_2) | bedroom | 5 | 5 / 4 | 4 | cushion, cushion, plant, rug, table_lamp | - | - |
| Dining (r_L0_dining) | dining | 4 | 3 / 3 | 3 | plant, rug, vase | - | - |

Items only one pass chose (not built):

- r_L0_bed_room_2: plant_small in f_L0_006.centre (pass 1)

Places left out:

- r_L0_bed_room: f_L0_007 wall: wall_art: above f_L0_007: window win_L0_001 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_bed_room: no free corner for a floor plant
- r_L0_drawing_room: f_L0_017 wall: wall_art: above f_L0_017: window win_L0_002 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
- r_L0_bed_room_2: f_L0_004 wall: wall_art: above f_L0_004: window win_L0_004 on the wall behind it leave 0.00 m for the picture (min 0.4 m)
