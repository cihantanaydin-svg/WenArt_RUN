# AI completion of furnished rooms: real01

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Bed Room (r_L0_bed_room) | bedroom | completed | 3/2 (4.7 s) | 0/2 (2.0 s) | 0 | nightstand (0.6) | - |
| Drawing Room (r_L0_drawing_room) | living | completed | 3/3 (5.6 s) | 0/4 (3.8 s) | 0 | tv_unit (0.6) | - |
| Room (r_L0_room) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | - | - |
| Bed Room (r_L0_bed_room_2) | bedroom | completed | 0/2 (2.0 s) | 0/2 (2.1 s) | 0 | - | - |
| Kitchen (r_L0_kitchen) | kitchen | completed | 0/4 (3.7 s) | 0/6 (5.4 s) | 0 | tall_cabinet (0.6), wall_cabinet (1.0) | - |
| Dining (r_L0_dining) | dining | completed | 7/1 (7.5 s) | 0/1 (1.1 s) | 0 | sideboard (0.6) | - |

## Changes of drawn pieces (13)

| Room | Piece | Drawn type / size | New type / size | Status | Reason |
|---|---|---|---|---|---|
| r_L0_bed_room | f_L0_007 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_bed_room | f_L0_008 | - | nightstand | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_bed_room | f_L0_009 | - | nightstand | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_drawing_room | f_L0_017 | - | sofa | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_drawing_room | f_L0_018 | - | armchair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_drawing_room | f_L0_019 | - | table_coffee | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_010 | - | table_dining | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_011 | - | chair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_012 | - | chair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_013 | - | chair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_014 | - | chair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_015 | - | chair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_dining | f_L0_016 | - | chair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |

## Added pieces (5)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L0_bed_room | f_L0_023 | nightstand | [0.61, 1.12] | 0.60 x 0.45 | ai | 0.6 | - |
| r_L0_drawing_room | f_L0_024 | tv_unit | [5.35, 1.78] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L0_kitchen | f_L0_025 | tall_cabinet | [10.91, 4.59] | 0.60 x 0.60 | ai | 0.6 | - |
| r_L0_kitchen | f_L0_026 | wall_cabinet | [12.35, 6.92] | 0.76 x 0.35 | rule | 1.0 | - |
| r_L0_dining | f_L0_027 | sideboard | [5.35, 6.27] | 1.60 x 0.45 | ai | 0.6 | - |

## Refused and dropped proposals (21)

- r_L0_bed_room: pass 1 bench at [1.75, 2.8]: no repair left
- r_L0_bed_room: pass 1 wardrobe at [2.8, 2.8]: no repair left
- r_L0_bed_room: pass 2 wardrobe at [2.89, 0.5]: no repair left
- r_L0_drawing_room: pass 1 sideboard at [8.73, 3.58]: no repair left
- r_L0_drawing_room: pass 1 armchair at [7.98, 3.58]: no repair left
- r_L0_drawing_room: pass 2 armchair at [7.0, 2.0]: no repair left
- r_L0_drawing_room: pass 2 tv_unit at [8.09, 1.5]: no repair left
- r_L0_room: pass 1 console_table at [3.43, 2.52]: no repair left
- r_L0_room: pass 2 console_table at [4.96, 6.5]: no repair left
- r_L0_bed_room_2: pass 1 bench at [1.8, 6.8]: no repair left
- r_L0_bed_room_2: pass 1 wardrobe at [2.85, 3.0]: no repair left
- r_L0_bed_room_2: pass 2 bench at [1.8, 5.5]: no repair left
- r_L0_bed_room_2: pass 2 wardrobe at [2.75, 3.73]: no repair left
- r_L0_kitchen: pass 1 chair at [11.44, 5.86]: no repair left
- r_L0_kitchen: pass 1 chair at [11.44, 5.26]: no repair left
- r_L0_kitchen: pass 1 table_dining at [11.44, 5.56]: no repair left
- r_L0_kitchen: pass 2 chair at [11.44, 7.15]: no repair left
- r_L0_kitchen: pass 2 chair at [11.44, 6.75]: no repair left
- r_L0_kitchen: pass 2 table_dining at [11.44, 6.15]: no repair left
- r_L0_kitchen: pass 2 chair at [11.44, 6.35]: no table_dining in the room
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

