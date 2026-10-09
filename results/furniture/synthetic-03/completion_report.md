# AI completion of furnished rooms: synthetic-03

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Salon (r_L0_salon) | living | completed | 0/1 (1.1 s) | 0/2 (2.1 s) | 0 | ottoman (0.6) | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | bench (0.6) | - |
| Mutfak (r_L0_mutfak) | kitchen | completed | 0/5 (4.3 s) | 1/5 (5.1 s) | 0 | tall_cabinet (0.9), chair (0.9), chair (0.9), chair (0.9), chair (0.9), wall_cabinet (1.0) | - |
| WC (r_L0_wc) | wc | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Kiler (r_L0_kiler) | storage | skipped | - | - | 0 | - | room type storage: no furniture types to complete |

## Changes of drawn pieces (1)

| Room | Piece | Drawn type / size | New type / size | Status | Reason |
|---|---|---|---|---|---|
| r_L0_mutfak | f_L0_011 | - | table_dining | not_agreed | only pass 2 changes it (a drawn piece needs both passes) |

## Added pieces (8)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L0_salon | f_L0_025 | ottoman | [4.40, 3.60] | 0.60 x 0.60 | ai | 0.6 | - |
| r_L0_yatak_odasi | f_L0_026 | bench | [8.70, 3.10] | 1.40 x 0.45 | ai | 0.6 | - |
| r_L0_mutfak | f_L0_027 | tall_cabinet | [0.56, 6.70] | 0.40 x 0.58 | ai | 0.9 | - |
| r_L0_mutfak | f_L0_028 | chair | [0.50, 5.80] | 0.45 x 0.45 | ai | 0.9 | - |
| r_L0_mutfak | f_L0_029 | chair | [3.00, 5.30] | 0.45 x 0.45 | ai | 0.9 | - |
| r_L0_mutfak | f_L0_030 | chair | [2.50, 5.30] | 0.45 x 0.45 | ai | 0.9 | - |
| r_L0_mutfak | f_L0_031 | chair | [0.70, 5.30] | 0.45 x 0.45 | ai | 0.9 | - |
| r_L0_mutfak | f_L0_032 | wall_cabinet | [0.65, 7.38] | 0.70 x 0.35 | rule | 1.0 | - |

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L0_salon: f_L0_001 fails clearance_ok as drawn
- r_L0_salon: f_L0_003 fails wall_contact as drawn
- r_L0_salon: f_L0_005 fails wall_contact as drawn
- r_L0_yatak_odasi: f_L0_014 fails doors_free as drawn
- r_L0_yatak_odasi: f_L0_017 fails wall_contact, windows_free as drawn
- r_L0_mutfak: f_L0_007 fails no_overlap as drawn
- r_L0_mutfak: f_L0_008 fails no_overlap as drawn
- r_L0_mutfak: f_L0_009 fails no_overlap as drawn
- r_L0_mutfak: f_L0_010 fails doors_free as drawn
- r_L0_mutfak: f_L0_011 fails doors_free as drawn
- r_L0_wc: f_L0_019 fails doors_free as drawn
- r_L0_wc: f_L0_020 fails doors_free as drawn
- r_L0_mutfak: walkway d_L0_003 - win_L0_004 broken as drawn
- r_L0_wc: walkway d_L0_006 - d_L0_007 broken as drawn

## Locked check: pass

