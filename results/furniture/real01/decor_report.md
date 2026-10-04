# Decor: real01

12 decor pieces (rule-based, `added_by_ai`, max 0.6 m except rugs and wall art). Cushions on sofas and beds, books on shelves and desks, one plant per living room or bedroom in a free corner (never on a door approach, a swing or a 0.9 m walkway). Rugs under the sofa + coffee table group, the lower two thirds of a double bed and dining tables (+ 0.6 m for the chairs), group + 0.3 m, inside the room shrunk by 0.3 m, never under a door swing; one wall art piece per living room, bedroom or dining room above a sofa, bed or dresser (0.25 m above its top, at most 0.6 x its width, never over a door or window; built only from a library model).

| Room | Cushions | Books | Plant | Rugs | Wall art | Note |
|---|---|---|---|---|---|---|
| Bed Room (r_L0_bed_room) | 2 | 0 | none | 1 | none | no free corner ((0.48, 0.48): no_overlap; (3.03, 0.48): no_overlap; (3.03, 3.335): doors_free; (0.48, 3.335): walkway); no wall art: above f_L0_007: window win_L0_001 on the wall behind it leave 0.00 m for the picture (min 0.4 m) |
| Bath+ Toilet (r_L0_bath_toilet) | 0 | 0 | - | 0 | - |  |
| Drawing Room (r_L0_drawing_room) | 2 | 0 | 5.356, 0.48 | 1 | none | no wall art: above f_L0_017: window win_L0_002 on the wall behind it leave 0.00 m for the picture (min 0.4 m) |
| Room (r_L0_room) | 0 | 0 | - | 0 | - |  |
| Pooja (r_L0_pooja) | 0 | 0 | - | 0 | - | prayer room: no decor (docs/milestone7.md §0) |
| Store (r_L0_store) | 0 | 0 | - | 0 | - |  |
| Bed Room (r_L0_bed_room_2) | 2 | 0 | 0.48, 3.985 | 1 | none | no wall art: above f_L0_004: window win_L0_004 on the wall behind it leave 0.00 m for the picture (min 0.4 m) |
| Kitchen (r_L0_kitchen) | 0 | 0 | - | 0 | - |  |
| Dining (r_L0_dining) | 0 | 0 | - | 1 | none | no wall art: no sofa, bed or dresser |
