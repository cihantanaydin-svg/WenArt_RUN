# AI completion of furnished rooms: synthetic-01

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Salon (r_L0_salon) | living | completed | 0/2 (2.2 s) | 0/2 (2.2 s) | 0 | armchair (0.6), console_table (0.6) | - |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | completed | 0/1 (1.2 s) | 0/1 (1.2 s) | 0 | bench (0.9) | - |
| Banyo (r_L0_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |

## Changes of drawn pieces (0)


## Added pieces (3)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L0_salon | f_L0_019 | armchair | [1.20, 4.68] | 0.90 x 0.90 | ai | 0.6 | - |
| r_L0_salon | f_L0_020 | console_table | [0.45, 0.90] | 1.20 x 0.35 | ai | 0.6 | - |
| r_L0_yatak_odasi | f_L0_021 | bench | [7.40, 1.20] | 1.40 x 0.45 | ai | 0.9 | - |

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L0_salon: f_L0_001 fails clearance_ok, doors_free as drawn
- r_L0_salon: f_L0_003 fails wall_contact as drawn
- r_L0_salon: f_L0_004 fails doors_free as drawn
- r_L0_salon: f_L0_005 fails wall_contact as drawn
- r_L0_yatak_odasi: f_L0_007 fails doors_free as drawn
- r_L0_yatak_odasi: f_L0_009 fails clearance_ok as drawn
- r_L0_banyo: f_L0_010 fails wall_contact as drawn
- r_L0_banyo: f_L0_011 fails doors_free, wall_contact as drawn
- r_L0_banyo: f_L0_012 fails doors_free, windows_free as drawn
- r_L0_salon: walkway d_L0_002 - win_L0_001 broken as drawn
- r_L0_salon: walkway d_L0_002 - win_L0_002 broken as drawn
- r_L0_salon: walkway d_L0_002 - win_L0_004 broken as drawn
- r_L0_banyo: walkway d_L0_005 - win_L0_006 broken as drawn

## Locked check: pass

