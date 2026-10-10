# AI completion of furnished rooms: real03

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Kat Holü (r_L0_kat_holu) | hall | completed | 0/1 (1.3 s) | 0/1 (1.2 s) | 0 | console_table (0.9) | - |
| Yangın Merdiveni (r_L0_yangin_merdiveni) | other | completed | 0/4 (3.6 s) | 0/0 (0.2 s) | 0 | armchair (0.6), chair (0.6), table_dining (0.6), bookshelf (0.6) | - |
| Kat Merdiveni (r_L0_kat_merdiveni) | other | completed | 0/3 (2.8 s) | 0/3 (2.9 s) | 0 | armchair (0.6), chair (0.6), table_dining (0.6) | - |

## Changes of drawn pieces (0)


## Added pieces (8)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L0_kat_holu | f_L0_010 | console_table | [11.71, 5.34] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L0_yangin_merdiveni | f_L0_011 | armchair | [4.09, 11.73] | 0.90 x 0.90 | ai | 0.6 | - |
| r_L0_yangin_merdiveni | f_L0_012 | chair | [5.50, 11.50] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L0_yangin_merdiveni | f_L0_013 | table_dining | [5.30, 12.20] | 1.20 x 0.80 | ai | 0.6 | - |
| r_L0_yangin_merdiveni | f_L0_014 | bookshelf | [3.80, 13.00] | 1.00 x 0.35 | ai | 0.6 | - |
| r_L0_kat_merdiveni | f_L0_015 | armchair | [21.00, 11.80] | 0.90 x 0.90 | ai | 0.6 | - |
| r_L0_kat_merdiveni | f_L0_016 | chair | [20.30, 11.10] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L0_kat_merdiveni | f_L0_017 | table_dining | [21.90, 11.70] | 1.60 x 0.90 | ai | 0.6 | - |

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L0_yangin_merdiveni: f_L0_001 fails inside_room as drawn
- r_L0_kat_merdiveni: f_L0_002 fails inside_room as drawn

## Locked check: pass

