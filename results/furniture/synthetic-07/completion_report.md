# AI completion of furnished rooms: synthetic-07

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | completed | 0/4 (3.6 s) | 0/4 (3.8 s) | 0 | table_coffee (0.9), tv_unit (0.6), armchair (0.9), sideboard (0.6) | - |
| Mutfak (r_L-1_mutfak) | kitchen | completed | 0/6 (5.2 s) | 0/6 (5.3 s) | 0 | tall_cabinet (0.6), table_dining (0.6), chair (0.9), chair (0.6), chair (0.6), chair (0.6) | - |
| Hol (r_L-1_hol) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | console_table (0.6) | - |
| Salon + Açık Mutfak (r_L-1b_salon_acik_mutfak) | living | completed | 0/4 (3.7 s) | 0/4 (3.6 s) | 0 | table_coffee (0.9), tv_unit (0.6), armchair (0.6), sideboard (0.6) | - |
| Hol (r_L-1b_hol) | hall | copied | - | - | 0 | console_table (0.6) | decisions of r_L-1_hol (same_as), not asked again |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | completed | 0/3 (2.7 s) | 0/3 (2.7 s) | 0 | nightstand (0.9), nightstand (0.9), wardrobe (0.6) | - |
| Banyo (r_L0_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Hol (r_L0_hol) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | console_table (0.6) | - |
| Hol (r_L1_hol) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | console_table (0.6) | - |

## Changes of drawn pieces (0)


## Added pieces (21)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L-1_salon | f_L-1_007 | table_coffee | [3.20, 5.80] | 1.00 x 0.60 | ai | 0.9 | - |
| r_L-1_salon | f_L-1_008 | tv_unit | [3.20, 0.50] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_009 | armchair | [1.60, 6.50] | 0.90 x 0.90 | ai | 0.9 | - |
| r_L-1_salon | f_L-1_010 | sideboard | [5.80, 2.00] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_011 | tall_cabinet | [8.83, 0.56] | 0.40 x 0.58 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_012 | table_dining | [8.00, 2.50] | 1.20 x 0.80 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_013 | chair | [7.30, 1.85] | 0.45 x 0.45 | ai | 0.9 | - |
| r_L-1_mutfak | f_L-1_014 | chair | [8.90, 2.55] | 0.45 x 0.45 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_015 | chair | [7.80, 1.85] | 0.45 x 0.45 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_016 | chair | [8.40, 3.15] | 0.45 x 0.45 | ai | 0.6 | - |
| r_L-1_hol | f_L-1_017 | console_table | [6.35, 4.90] | 1.20 x 0.35 | ai | 0.6 | - |
| r_L-1b_salon_acik_mutfak | f_L-1b_007 | table_coffee | [3.20, 5.80] | 1.00 x 0.60 | ai | 0.9 | - |
| r_L-1b_salon_acik_mutfak | f_L-1b_008 | tv_unit | [5.83, 4.77] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L-1b_salon_acik_mutfak | f_L-1b_009 | armchair | [1.60, 6.80] | 0.90 x 0.90 | ai | 0.6 | - |
| r_L-1b_salon_acik_mutfak | f_L-1b_010 | sideboard | [0.50, 1.50] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L-1b_hol | f_L-1b_011 | console_table | [6.35, 4.90] | 1.20 x 0.35 | ai | 0.6 | f_L-1_017 |
| r_L0_yatak_odasi | f_L0_006 | nightstand | [1.90, 7.53] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi | f_L0_007 | nightstand | [4.70, 7.53] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi | f_L0_008 | wardrobe | [5.73, 2.50] | 1.80 x 0.60 | ai | 0.6 | - |
| r_L0_hol | f_L0_009 | console_table | [6.35, 4.90] | 1.20 x 0.35 | ai | 0.6 | - |
| r_L1_hol | f_L1_006 | console_table | [9.13, 4.25] | 1.20 x 0.35 | ai | 0.6 | - |

## Refused and dropped proposals (5)

- r_L-1_mutfak: pass 1 table_dining at [7.6, 2.0]: no repair left
- r_L-1_mutfak: pass 1 chair at [7.9, 2.1]: no table_dining in the room
- r_L-1_mutfak: pass 1 chair at [7.3, 2.1]: no table_dining in the room
- r_L-1_mutfak: pass 1 chair at [7.9, 1.9]: no table_dining in the room
- r_L-1_mutfak: pass 1 chair at [7.3, 1.9]: no table_dining in the room

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L-1_mutfak: f_L-1_002 fails inside_room as drawn
- r_L-1_mutfak: f_L-1_003 fails inside_room, no_overlap as drawn
- r_L-1_mutfak: f_L-1_004 fails inside_room, no_overlap as drawn
- r_L-1_mutfak: f_L-1_006 fails inside_room, no_overlap as drawn
- r_L-1_hol: f_L-1_001 fails doors_free, inside_room, windows_free as drawn
- r_L-1b_salon_acik_mutfak: f_L-1b_002 fails inside_room as drawn
- r_L-1b_salon_acik_mutfak: f_L-1b_003 fails inside_room, no_overlap as drawn
- r_L-1b_salon_acik_mutfak: f_L-1b_004 fails inside_room, no_overlap as drawn
- r_L-1b_salon_acik_mutfak: f_L-1b_006 fails inside_room, no_overlap as drawn
- r_L-1b_hol: f_L-1b_001 fails doors_free, inside_room, windows_free as drawn
- r_L0_banyo: f_L0_004 fails inside_room as drawn
- r_L0_banyo: f_L0_005 fails inside_room as drawn
- r_L0_hol: f_L0_001 fails doors_free, inside_room as drawn
- r_L1_hol: f_L1_001 fails doors_free, inside_room, windows_free as drawn
- r_L-1_hol: walkway d_L-1_001 - win_L-1_007 broken as drawn
- r_L-1_hol: walkway d_L-1_002 - win_L-1_007 broken as drawn
- r_L-1_hol: walkway d_L-1_003 - win_L-1_007 broken as drawn
- r_L-1b_hol: walkway d_L-1b_001 - win_L-1b_007 broken as drawn
- r_L-1b_hol: walkway d_L-1b_002 - win_L-1b_007 broken as drawn
- r_L-1b_hol: walkway d_L-1b_003 - win_L-1b_007 broken as drawn
- r_L1_hol: walkway d_L1_001 - win_L1_002 broken as drawn
- r_L1_hol: walkway d_L1_002 - win_L1_002 broken as drawn

## Locked check: pass

