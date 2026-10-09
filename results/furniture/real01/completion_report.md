# AI completion of furnished rooms: real01

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Bed Room (r_L0_bed_room) | bedroom | completed | 3/2 (4.4 s) | 0/2 (1.9 s) | 0 | nightstand (0.6) | - |
| Drawing Room (r_L0_drawing_room) | living | completed | 3/3 (5.2 s) | 0/4 (3.5 s) | 0 | tv_unit (0.6) | - |
| Room (r_L0_room) | hall | completed | 0/1 (1.0 s) | 0/1 (1.0 s) | 0 | - | - |
| Bed Room (r_L0_bed_room_2) | bedroom | completed | 0/2 (1.9 s) | 0/2 (1.9 s) | 0 | nightstand (0.9) | - |
| Kitchen (r_L0_kitchen) | kitchen | completed | 0/4 (3.4 s) | 0/6 (5.1 s) | 0 | tall_cabinet (0.6), wall_cabinet (1.0) | - |
| Dining (r_L0_dining) | dining | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | sideboard (0.6) | - |

## Changes of drawn pieces (6)

| Room | Piece | Drawn type / size | New type / size | Status | Reason |
|---|---|---|---|---|---|
| r_L0_bed_room | f_L0_007 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_bed_room | f_L0_008 | - | nightstand | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_bed_room | f_L0_009 | - | nightstand | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_drawing_room | f_L0_017 | - | sofa | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_drawing_room | f_L0_018 | - | armchair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_drawing_room | f_L0_019 | - | table_coffee | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |

## Added pieces (6)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L0_bed_room | f_L0_023 | nightstand | [0.61, 1.12] | 0.60 x 0.45 | ai | 0.6 | - |
| r_L0_drawing_room | f_L0_024 | tv_unit | [5.35, 1.78] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L0_bed_room_2 | f_L0_025 | nightstand | [0.56, 6.36] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_kitchen | f_L0_026 | tall_cabinet | [10.91, 4.59] | 0.60 x 0.60 | ai | 0.6 | - |
| r_L0_kitchen | f_L0_027 | wall_cabinet | [12.35, 6.92] | 0.76 x 0.35 | rule | 1.0 | - |
| r_L0_dining | f_L0_028 | sideboard | [5.35, 6.00] | 1.60 x 0.45 | ai | 0.6 | - |

## Refused and dropped proposals (19)

- r_L0_bed_room: pass 1 bench at [1.75, 0.5]: no repair left
- r_L0_bed_room: pass 1 wardrobe at [2.89, 2.89]: no repair left
- r_L0_bed_room: pass 2 wardrobe at [2.89, 0.5]: no repair left
- r_L0_drawing_room: pass 1 sideboard at [8.73, 3.58]: no repair left
- r_L0_drawing_room: pass 1 armchair at [7.98, 3.58]: no repair left
- r_L0_drawing_room: pass 2 armchair at [7.0, 2.0]: no repair left
- r_L0_drawing_room: pass 2 tv_unit at [8.09, 1.5]: no repair left
- r_L0_room: pass 1 console_table at [3.43, 2.52]: no repair left
- r_L0_room: pass 2 console_table at [4.96, 6.5]: no repair left
- r_L0_bed_room_2: pass 1 wardrobe at [2.8, 3.5]: no repair left
- r_L0_bed_room_2: pass 2 wardrobe at [0.85, 3.95]: no repair left
- r_L0_kitchen: pass 1 chair at [11.44, 5.86]: no repair left
- r_L0_kitchen: pass 1 chair at [11.44, 5.26]: no repair left
- r_L0_kitchen: pass 1 table_dining at [11.44, 5.56]: no repair left
- r_L0_kitchen: pass 2 chair at [12.05, 6.55]: no repair left
- r_L0_kitchen: pass 2 table_dining at [11.44, 6.15]: no repair left
- r_L0_kitchen: pass 2 chair at [11.85, 6.35]: no table_dining in the room
- r_L0_kitchen: pass 2 chair at [11.65, 6.15]: no table_dining in the room
- r_L0_kitchen: pass 2 chair at [11.44, 5.95]: no table_dining in the room

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L0_bed_room: f_L0_007 fails no_overlap as drawn
- r_L0_bed_room: f_L0_008 fails no_overlap as drawn
- r_L0_room: f_L0_003 fails doors_free, inside_room as drawn
- r_L0_bed_room_2: f_L0_004 fails inside_room, no_overlap as drawn
- r_L0_bed_room_2: f_L0_005 fails inside_room as drawn
- r_L0_bed_room_2: f_L0_006 fails inside_room, no_overlap as drawn
- r_L0_kitchen: f_L0_001 fails inside_room as drawn
- r_L0_kitchen: f_L0_002 fails inside_room as drawn
- r_L0_dining: f_L0_010 fails no_overlap as drawn
- r_L0_dining: f_L0_011 fails no_overlap as drawn
- r_L0_dining: f_L0_013 fails no_overlap as drawn
- r_L0_dining: f_L0_014 fails no_overlap as drawn

## Locked check: pass

