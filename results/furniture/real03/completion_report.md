# AI completion of furnished rooms: real03

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Ebeveyn Odası (r_L0_ebeveyn_odasi) | bedroom | completed | 1/3 (4.2 s) | 0/3 (2.9 s) | 0 | nightstand (0.9), nightstand (0.9) | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_2) | bedroom | completed | 0/2 (2.2 s) | 0/2 (2.1 s) | 0 | - | - |
| Yaşama (r_L0_yasama) | living | completed | 0/5 (4.7 s) | 0/5 (4.4 s) | 0 | sofa (0.6), table_coffee (0.6), tv_unit (0.6), armchair (0.6), sideboard (0.6) | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_3) | bedroom | completed | 1/2 (3.1 s) | 0/3 (2.9 s) | 0 | nightstand (0.6) | - |
| Rüzgarlık (r_L0_ruzgarlik) | hall | completed | 0/1 (1.2 s) | 0/1 (1.2 s) | 0 | console_table (0.6) | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_4) | bedroom | completed | 1/3 (3.7 s) | 0/2 (2.1 s) | 0 | nightstand (0.9) | - |
| Yaşama (r_L0_yasama_2) | living | completed | 3/3 (5.6 s) | 0/2 (2.2 s) | 0 | tv_unit (0.6) | - |
| Oda-01 (r_L0_oda_01) | bedroom | completed | 0/2 (2.0 s) | 0/2 (2.1 s) | 0 | nightstand (0.9) | - |
| Yaşama (r_L0_yasama_3) | living | completed | 3/2 (4.8 s) | 0/2 (2.1 s) | 0 | tv_unit (0.6) | - |
| Yaşama (r_L0_yasama_4) | living | completed | 0/4 (3.8 s) | 0/5 (4.9 s) | 0 | - | - |
| Giriş Holü (r_L0_giris_holu) | hall | completed | 0/1 (1.3 s) | 1/1 (2.1 s) | 0 | - | - |
| Banyo (r_L0_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L0_banyo_2) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L0_banyo_3) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Giriş Holü (r_L0_giris_holu_2) | hall | completed | 0/1 (1.2 s) | 1/1 (2.1 s) | 0 | - | - |
| Banyo (r_L0_banyo_4) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Oda (r_L0_oda_7) | hall | completed | 0/1 (1.2 s) | 0/1 (1.2 s) | 0 | - | - |
| Kat Holü (r_L0_kat_holu) | hall | completed | 0/1 (1.3 s) | 0/1 (1.4 s) | 0 | shoe_cabinet (0.6) | - |
| Oda (r_L0_oda_10) | hall | completed | 0/1 (1.3 s) | 0/1 (1.2 s) | 0 | - | - |
| Yaşama (r_L0_yasama_5) | living | completed | 0/5 (5.0 s) | 0/3 (3.2 s) | 0 | tv_unit (0.9) | - |
| Yaşama (r_L0_yasama_6) | living | completed | 0/5 (4.9 s) | 0/5 (5.1 s) | 0 | tv_unit (0.6), sideboard (0.6) | - |
| Banyo (r_L0_banyo_5) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Yangın Merdiveni (r_L0_yangin_merdiveni) | stair | skipped | - | - | 0 | - | stair room: never furnished by AI |
| Banyo (r_L0_banyo_6) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Kat Merdiveni (r_L0_kat_merdiveni) | stair | skipped | - | - | 0 | - | stair room: never furnished by AI |
| Giriş Holü (r_L0_giris_holu_3) | hall | completed | 0/1 (1.2 s) | 0/1 (1.3 s) | 0 | console_table (0.9) | - |
| Oda (r_L0_oda_19) | unknown | skipped | - | - | 0 | - | room type unknown: no furniture types to complete |
| Banyo (r_L0_banyo_7) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Giriş Holü (r_L0_giris_holu_4) | hall | completed | 0/1 (1.3 s) | 0/1 (1.2 s) | 0 | console_table (0.6) | - |
| Banyo (r_L0_banyo_8) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_5) | bedroom | completed | 1/1 (2.2 s) | 0/2 (2.0 s) | 0 | - | - |
| Ebeveyn Odası (r_L0_ebeveyn_odasi_6) | bedroom | completed | 0/2 (2.1 s) | 0/2 (2.0 s) | 0 | bench (0.6) | - |
| Yaşama (r_L0_yasama_7) | living | completed | 3/3 (5.8 s) | 0/4 (4.0 s) | 0 | tv_unit (0.6), armchair (0.9), ottoman (0.6) | - |
| Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a) | bedroom | completed | 0/4 (4.0 s) | 0/2 (2.2 s) | 0 | bench (0.9), dresser (0.9) | - |
| Ebeveyn Odası (m.k.a.) (r_L0_ebeveyn_odasi_m_k_a_2) | bedroom | completed | 4/3 (6.2 s) | 0/2 (2.1 s) | 0 | dresser (0.6) | - |
| Yaşama (r_L0_yasama_8) | living | completed | 2/3 (5.0 s) | 0/4 (3.9 s) | 0 | tv_unit (0.6), ottoman (0.6) | - |

## Changes of drawn pieces (21)

| Room | Piece | Drawn type / size | New type / size | Status | Reason |
|---|---|---|---|---|---|
| r_L0_ebeveyn_odasi | f_L0_024 | - | dresser | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_3 | f_L0_025 | - | wardrobe | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_4 | f_L0_058 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_2 | f_L0_102 | - | sofa | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_2 | f_L0_103 | - | console_table | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_2 | f_L0_130 | - | sideboard | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_3 | f_L0_095 | - | sofa | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_3 | f_L0_096 | - | console_table | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_3 | f_L0_097 | - | armchair | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_giris_holu | f_L0_135 | - | console_table | not_agreed | only pass 2 changes it (a drawn piece needs both passes) |
| r_L0_giris_holu_2 | f_L0_138 | - | console_table | not_agreed | only pass 2 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_5 | f_L0_023 | - | wardrobe | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_7 | f_L0_073 | - | table_coffee | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_7 | f_L0_117 | - | sofa | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_7 | f_L0_140 | - | bookshelf | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_m_k_a_2 | f_L0_057 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_m_k_a_2 | f_L0_081 | - | bench | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_m_k_a_2 | f_L0_112 | - | nightstand | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_ebeveyn_odasi_m_k_a_2 | f_L0_113 | - | nightstand | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_8 | f_L0_074 | - | table_coffee | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yasama_8 | f_L0_141 | - | bookshelf | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |

## Added pieces (28)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L0_ebeveyn_odasi | f_L0_166 | nightstand | [5.48, 3.00] | 0.60 x 0.45 | ai | 0.9 | - |
| r_L0_ebeveyn_odasi | f_L0_167 | nightstand | [6.08, 3.00] | 0.60 x 0.45 | ai | 0.9 | - |
| r_L0_yasama | f_L0_168 | sofa | [8.19, 3.54] | 1.60 x 0.90 | ai | 0.6 | - |
| r_L0_yasama | f_L0_169 | table_coffee | [8.20, 1.80] | 1.00 x 0.60 | ai | 0.6 | - |
| r_L0_yasama | f_L0_170 | tv_unit | [7.30, 1.60] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L0_yasama | f_L0_171 | armchair | [8.70, 4.90] | 0.90 x 0.90 | ai | 0.6 | - |
| r_L0_yasama | f_L0_172 | sideboard | [8.77, 0.40] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L0_ebeveyn_odasi_3 | f_L0_173 | nightstand | [27.10, 3.03] | 0.50 x 0.40 | ai | 0.6 | - |
| r_L0_ruzgarlik | f_L0_174 | console_table | [13.76, 4.53] | 1.20 x 0.35 | ai | 0.6 | - |
| r_L0_ebeveyn_odasi_4 | f_L0_175 | nightstand | [17.02, 3.06] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yasama_2 | f_L0_176 | tv_unit | [30.69, 1.37] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_oda_01 | f_L0_177 | nightstand | [20.64, 0.37] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yasama_3 | f_L0_178 | tv_unit | [1.65, 1.37] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_kat_holu | f_L0_179 | shoe_cabinet | [24.80, 6.18] | 0.80 x 0.32 | ai | 0.6 | - |
| r_L0_yasama_5 | f_L0_180 | tv_unit | [2.53, 12.03] | 1.20 x 0.40 | ai | 0.9 | - |
| r_L0_yasama_6 | f_L0_181 | tv_unit | [32.15, 12.03] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_yasama_6 | f_L0_182 | sideboard | [30.79, 12.02] | 1.40 x 0.42 | ai | 0.6 | - |
| r_L0_giris_holu_3 | f_L0_183 | console_table | [29.58, 8.84] | 0.90 x 0.30 | ai | 0.9 | - |
| r_L0_giris_holu_4 | f_L0_184 | console_table | [3.62, 8.84] | 0.90 x 0.30 | ai | 0.6 | - |
| r_L0_ebeveyn_odasi_6 | f_L0_185 | bench | [5.61, 10.41] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_yasama_7 | f_L0_186 | tv_unit | [20.62, 13.80] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L0_yasama_7 | f_L0_187 | armchair | [20.60, 11.50] | 0.90 x 0.90 | ai | 0.9 | - |
| r_L0_yasama_7 | f_L0_188 | ottoman | [21.50, 11.00] | 0.60 x 0.60 | ai | 0.6 | - |
| r_L0_ebeveyn_odasi_m_k_a | f_L0_189 | bench | [15.45, 13.83] | 1.20 x 0.40 | ai | 0.9 | - |
| r_L0_ebeveyn_odasi_m_k_a | f_L0_190 | dresser | [14.12, 13.78] | 1.20 x 0.50 | ai | 0.9 | - |
| r_L0_ebeveyn_odasi_m_k_a_2 | f_L0_191 | dresser | [17.89, 13.78] | 1.40 x 0.50 | ai | 0.6 | - |
| r_L0_yasama_8 | f_L0_192 | tv_unit | [12.58, 13.80] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L0_yasama_8 | f_L0_193 | ottoman | [11.41, 9.64] | 0.50 x 0.50 | ai | 0.6 | - |

## Refused and dropped proposals (62)

- r_L0_ebeveyn_odasi: pass 1 wardrobe at [6.43, 2.51]: no repair left
- r_L0_ebeveyn_odasi: pass 1 nightstand at [4.43, 0.91]: no repair left
- r_L0_ebeveyn_odasi: pass 2 wardrobe at [3.45, 2.51]: no repair left
- r_L0_ebeveyn_odasi_2: pass 1 bench at [12.22, 2.8]: no repair left
- r_L0_ebeveyn_odasi_2: pass 1 wardrobe at [10.17, 0.72]: no repair left
- r_L0_ebeveyn_odasi_2: pass 2 bench at [12.22, 2.75]: no repair left
- r_L0_ebeveyn_odasi_2: pass 2 wardrobe at [10.15, 1.75]: no repair left
- r_L0_yasama: pass 1 armchair at [6.5, 4.0]: no repair left
- r_L0_ebeveyn_odasi_3: pass 1 nightstand at [27.42, 1.7]: no repair left
- r_L0_ebeveyn_odasi_3: pass 2 wardrobe at [26.4, 2.92]: no repair left
- r_L0_ebeveyn_odasi_4: pass 1 bench at [17.88, 4.65]: no repair left
- r_L0_ebeveyn_odasi_4: pass 1 wardrobe at [16.8, 4.05]: no repair left
- r_L0_ebeveyn_odasi_4: pass 2 wardrobe at [16.8, 4.65]: no repair left
- r_L0_yasama_2: pass 1 armchair at [30.8, 4.8]: no repair left
- r_L0_yasama_2: pass 1 table_coffee at [32.1, 3.85]: no repair left
- r_L0_yasama_2: pass 2 table_coffee at [32.34, 3.5]: no repair left
- r_L0_oda_01: pass 1 wardrobe at [19.65, 1.42]: no repair left
- r_L0_oda_01: pass 2 wardrobe at [19.65, 1.89]: no repair left
- r_L0_yasama_3: pass 1 table_coffee at [0.87, 3.75]: no repair left
- r_L0_yasama_3: pass 2 table_coffee at [1.2, 3.85]: no repair left
- r_L0_yasama_4: pass 1 armchair at [21.5, 4.5]: no repair left
- r_L0_yasama_4: pass 1 tv_unit at [23.08, 4.28]: no repair left
- r_L0_yasama_4: pass 1 table_coffee at [23.08, 3.68]: no repair left
- r_L0_yasama_4: pass 1 sofa at [23.08, 3.08]: no repair left
- r_L0_yasama_4: pass 2 sideboard at [24.0, 4.5]: no repair left
- r_L0_yasama_4: pass 2 armchair at [21.0, 4.0]: no repair left
- r_L0_yasama_4: pass 2 tv_unit at [22.5, 2.0]: no repair left
- r_L0_yasama_4: pass 2 table_coffee at [22.5, 3.0]: no repair left
- r_L0_yasama_4: pass 2 sofa at [22.5, 3.5]: no repair left
- r_L0_giris_holu: pass 1 console_table at [3.58, 4.7]: no repair left
- r_L0_giris_holu: pass 2 bench at [3.69, 5.01]: no repair left
- r_L0_giris_holu_2: pass 1 console_table at [29.63, 4.0]: no repair left
- r_L0_giris_holu_2: pass 2 bench at [28.1, 4.7]: no repair left
- r_L0_oda_7: pass 1 console_table at [3.77, 6.7]: no repair left
- r_L0_oda_7: pass 2 console_table at [3.77, 6.7]: no repair left
- r_L0_oda_10: pass 1 console_table at [28.8, 6.7]: no repair left
- r_L0_oda_10: pass 2 console_table at [29.26, 6.7]: no repair left
- r_L0_yasama_5: pass 1 armchair at [0.87, 9.33]: no repair left
- r_L0_yasama_5: pass 1 table_coffee at [1.65, 8.85]: no repair left
- r_L0_yasama_5: pass 1 sofa at [1.65, 9.39]: no repair left
- r_L0_yasama_5: pass 2 table_coffee at [1.65, 9.0]: no repair left
- r_L0_yasama_5: pass 2 sofa at [1.65, 9.39]: no repair left
- r_L0_yasama_6: pass 1 armchair at [30.5, 9.5]: no repair left
- r_L0_yasama_6: pass 1 table_coffee at [31.55, 10.0]: no repair left
- r_L0_yasama_6: pass 1 sofa at [31.55, 9.39]: no repair left
- r_L0_yasama_6: pass 2 armchair at [30.07, 10.0]: no repair left
- r_L0_yasama_6: pass 2 table_coffee at [31.55, 8.95]: no repair left
- r_L0_yasama_6: pass 2 sofa at [31.55, 9.39]: no repair left
- r_L0_ebeveyn_odasi_5: pass 1 bench at [27.42, 12.73]: no repair left
- r_L0_ebeveyn_odasi_5: pass 2 bench at [27.4, 12.5]: no repair left
- r_L0_ebeveyn_odasi_5: pass 2 wardrobe at [24.5, 11.5]: no repair left
- r_L0_ebeveyn_odasi_6: pass 1 wardrobe at [2.8, 12.0]: no repair left
- r_L0_ebeveyn_odasi_6: pass 2 wardrobe at [3.45, 12.5]: no repair left
- r_L0_yasama_7: pass 2 tv_unit at [19.8, 12.66]: no repair left
- r_L0_ebeveyn_odasi_m_k_a: pass 1 armchair at [14.5, 12.0]: no repair left
- r_L0_ebeveyn_odasi_m_k_a: pass 1 dresser at [13.5, 11.5]: no repair left
- r_L0_ebeveyn_odasi_m_k_a_2: pass 1 office_chair at [18.5, 11.5]: no repair left
- r_L0_ebeveyn_odasi_m_k_a_2: pass 1 desk at [18.5, 11.5]: no repair left
- r_L0_ebeveyn_odasi_m_k_a_2: pass 2 bench at [17.76, 12.58]: no repair left
- r_L0_yasama_8: pass 1 armchair at [11.23, 8.33]: no repair left
- r_L0_yasama_8: pass 2 tv_unit at [13.2, 12.0]: no repair left
- r_L0_yasama_8: pass 2 table_coffee at [11.0, 12.0]: no repair left

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L0_ebeveyn_odasi: f_L0_024 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_ebeveyn_odasi: f_L0_059 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_2: f_L0_002 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_ebeveyn_odasi_2: f_L0_046 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_2: f_L0_084 fails inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_2: f_L0_085 fails doors_free, inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_2: f_L0_086 fails inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_2: f_L0_088 fails inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_3: f_L0_025 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_ebeveyn_odasi_3: f_L0_060 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_ruzgarlik: f_L0_118 fails doors_free, inside_room, windows_free as drawn
- r_L0_ebeveyn_odasi_4: f_L0_058 fails doors_free, inside_room as drawn
- r_L0_ebeveyn_odasi_4: f_L0_114 fails inside_room as drawn
- r_L0_ebeveyn_odasi_4: f_L0_119 fails clearance_ok, inside_room as drawn
- r_L0_yasama_2: f_L0_007 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_2: f_L0_053 fails no_overlap as drawn
- r_L0_yasama_2: f_L0_102 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_yasama_2: f_L0_103 fails doors_free, inside_room, no_overlap as drawn
- r_L0_yasama_2: f_L0_104 fails clearance_ok, doors_free, no_overlap as drawn
- r_L0_yasama_2: f_L0_105 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_2: f_L0_130 fails doors_free, no_overlap as drawn
- r_L0_oda_01: f_L0_061 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_oda_01: f_L0_089 fails doors_free, inside_room as drawn
- r_L0_oda_01: f_L0_090 fails inside_room, windows_free as drawn
- r_L0_oda_01: f_L0_161 fails no_overlap as drawn
- r_L0_yasama_3: f_L0_005 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_3: f_L0_051 fails no_overlap as drawn
- r_L0_yasama_3: f_L0_095 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_yasama_3: f_L0_096 fails doors_free, inside_room, no_overlap as drawn
- r_L0_yasama_3: f_L0_097 fails clearance_ok, doors_free, no_overlap as drawn
- r_L0_yasama_3: f_L0_098 fails doors_free, no_overlap as drawn
- r_L0_yasama_3: f_L0_134 fails doors_free, no_overlap as drawn
- r_L0_yasama_4: f_L0_003 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_4: f_L0_047 fails no_overlap as drawn
- r_L0_giris_holu: f_L0_062 fails inside_room as drawn
- r_L0_giris_holu: f_L0_135 fails inside_room, wall_contact, windows_free as drawn
- r_L0_banyo: f_L0_030 fails inside_room as drawn
- r_L0_banyo: f_L0_033 fails inside_room as drawn
- r_L0_banyo: f_L0_069 fails doors_free, inside_room as drawn
- r_L0_banyo: f_L0_128 fails inside_room as drawn
- r_L0_banyo: f_L0_164 fails doors_free, inside_room as drawn
- r_L0_banyo_2: f_L0_032 fails inside_room as drawn
- r_L0_banyo_2: f_L0_035 fails inside_room as drawn
- r_L0_banyo_2: f_L0_067 fails doors_free, inside_room as drawn
- r_L0_banyo_2: f_L0_126 fails inside_room as drawn
- r_L0_banyo_2: f_L0_165 fails doors_free, inside_room as drawn
- r_L0_banyo_3: f_L0_014 fails doors_free, inside_room as drawn
- r_L0_banyo_3: f_L0_015 fails doors_free, inside_room as drawn
- r_L0_banyo_3: f_L0_042 fails doors_free, inside_room as drawn
- r_L0_banyo_3: f_L0_044 fails doors_free, inside_room as drawn
- r_L0_giris_holu_2: f_L0_065 fails inside_room as drawn
- r_L0_giris_holu_2: f_L0_138 fails inside_room, wall_contact, windows_free as drawn
- r_L0_banyo_4: f_L0_016 fails inside_room as drawn
- r_L0_banyo_4: f_L0_017 fails inside_room as drawn
- r_L0_banyo_4: f_L0_048 fails doors_free, inside_room as drawn
- r_L0_banyo_4: f_L0_123 fails doors_free, inside_room as drawn
- r_L0_oda_7: f_L0_144 fails doors_free, inside_room, no_overlap as drawn
- r_L0_oda_7: f_L0_145 fails doors_free, inside_room, no_overlap as drawn
- r_L0_oda_7: f_L0_149 fails doors_free, no_overlap as drawn
- r_L0_oda_7: f_L0_152 fails doors_free, no_overlap as drawn
- r_L0_kat_holu: f_L0_028 fails doors_free, inside_room as drawn
- r_L0_kat_holu: f_L0_087 fails doors_free, inside_room as drawn
- r_L0_kat_holu: f_L0_146 fails doors_free, inside_room as drawn
- r_L0_kat_holu: f_L0_147 fails doors_free, inside_room as drawn
- r_L0_kat_holu: f_L0_148 fails doors_free, inside_room as drawn
- r_L0_kat_holu: f_L0_150 fails doors_free as drawn
- r_L0_kat_holu: f_L0_151 fails doors_free as drawn
- r_L0_kat_holu: f_L0_153 fails doors_free as drawn
- r_L0_kat_holu: f_L0_154 fails doors_free as drawn
- r_L0_oda_10: f_L0_139 fails doors_free, inside_room, no_overlap as drawn
- r_L0_oda_10: f_L0_155 fails doors_free, no_overlap as drawn
- r_L0_oda_10: f_L0_156 fails doors_free, no_overlap as drawn
- r_L0_yasama_5: f_L0_004 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_5: f_L0_050 fails no_overlap as drawn
- r_L0_yasama_5: f_L0_091 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_5: f_L0_092 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_5: f_L0_093 fails doors_free, no_overlap as drawn
- r_L0_yasama_5: f_L0_094 fails no_overlap as drawn
- r_L0_yasama_5: f_L0_131 fails doors_free, no_overlap as drawn
- r_L0_yasama_6: f_L0_006 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_6: f_L0_052 fails no_overlap as drawn
- r_L0_yasama_6: f_L0_099 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_6: f_L0_100 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_6: f_L0_101 fails doors_free, no_overlap as drawn
- r_L0_yasama_6: f_L0_129 fails doors_free, no_overlap as drawn
- r_L0_banyo_5: f_L0_029 fails inside_room as drawn
- r_L0_banyo_5: f_L0_034 fails inside_room as drawn
- r_L0_banyo_5: f_L0_068 fails doors_free, inside_room as drawn
- r_L0_banyo_5: f_L0_127 fails inside_room as drawn
- r_L0_banyo_5: f_L0_162 fails doors_free, inside_room as drawn
- r_L0_banyo_6: f_L0_010 fails inside_room as drawn
- r_L0_banyo_6: f_L0_013 fails inside_room as drawn
- r_L0_banyo_6: f_L0_039 fails doors_free, inside_room, wall_contact as drawn
- r_L0_banyo_6: f_L0_041 fails doors_free as drawn
- r_L0_banyo_6: f_L0_075 fails inside_room as drawn
- r_L0_banyo_6: f_L0_157 fails inside_room as drawn
- r_L0_giris_holu_3: f_L0_064 fails inside_room as drawn
- r_L0_giris_holu_3: f_L0_137 fails inside_room, no_overlap, windows_free as drawn
- r_L0_giris_holu_3: f_L0_143 fails doors_free, no_overlap as drawn
- r_L0_banyo_7: f_L0_031 fails inside_room as drawn
- r_L0_banyo_7: f_L0_036 fails inside_room as drawn
- r_L0_banyo_7: f_L0_066 fails doors_free, inside_room as drawn
- r_L0_banyo_7: f_L0_125 fails inside_room as drawn
- r_L0_banyo_7: f_L0_163 fails doors_free, inside_room as drawn
- r_L0_giris_holu_4: f_L0_063 fails inside_room as drawn
- r_L0_giris_holu_4: f_L0_136 fails inside_room, wall_contact, windows_free as drawn
- r_L0_banyo_8: f_L0_011 fails inside_room as drawn
- r_L0_banyo_8: f_L0_012 fails inside_room as drawn
- r_L0_banyo_8: f_L0_040 fails doors_free, inside_room, wall_contact as drawn
- r_L0_banyo_8: f_L0_070 fails doors_free as drawn
- r_L0_banyo_8: f_L0_076 fails inside_room as drawn
- r_L0_banyo_8: f_L0_158 fails inside_room, windows_free as drawn
- r_L0_ebeveyn_odasi_5: f_L0_023 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_ebeveyn_odasi_5: f_L0_055 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_5: f_L0_108 fails inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_5: f_L0_109 fails inside_room as drawn
- r_L0_ebeveyn_odasi_6: f_L0_022 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_ebeveyn_odasi_6: f_L0_054 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_6: f_L0_106 fails inside_room, no_overlap as drawn
- r_L0_ebeveyn_odasi_6: f_L0_107 fails inside_room as drawn
- r_L0_yasama_7: f_L0_038 fails no_overlap as drawn
- r_L0_yasama_7: f_L0_073 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_7: f_L0_117 fails clearance_ok as drawn
- r_L0_yasama_7: f_L0_140 fails inside_room as drawn
- r_L0_yasama_7: f_L0_160 fails no_overlap as drawn
- r_L0_ebeveyn_odasi_m_k_a: f_L0_056 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a: f_L0_080 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a: f_L0_110 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a: f_L0_111 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a: f_L0_121 fails clearance_ok, inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_057 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_081 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_112 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_113 fails inside_room as drawn
- r_L0_ebeveyn_odasi_m_k_a_2: f_L0_122 fails clearance_ok, inside_room as drawn
- r_L0_yasama_8: f_L0_037 fails no_overlap as drawn
- r_L0_yasama_8: f_L0_074 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L0_yasama_8: f_L0_077 fails doors_free, no_overlap as drawn
- r_L0_yasama_8: f_L0_079 fails doors_free, no_overlap as drawn
- r_L0_yasama_8: f_L0_116 fails clearance_ok, doors_free as drawn
- r_L0_yasama_8: f_L0_132 fails doors_free as drawn
- r_L0_yasama_8: f_L0_141 fails inside_room as drawn
- r_L0_yasama_8: f_L0_159 fails no_overlap as drawn
- r_L0_ebeveyn_odasi: walkway d_L0_006 - win_L0_007 broken as drawn
- r_L0_ebeveyn_odasi: walkway d_L0_006 - win_L0_031 broken as drawn
- r_L0_ebeveyn_odasi_2: walkway o_L0_003 - win_L0_033 broken as drawn
- r_L0_ebeveyn_odasi_2: walkway o_L0_003 - win_L0_056 broken as drawn
- r_L0_ebeveyn_odasi_3: walkway d_L0_012 - win_L0_024 broken as drawn
- r_L0_ebeveyn_odasi_3: walkway d_L0_012 - win_L0_036 broken as drawn
- r_L0_ruzgarlik: walkway d_L0_019 - win_L0_056 broken as drawn
- r_L0_ruzgarlik: walkway d_L0_020 - win_L0_056 broken as drawn
- r_L0_ebeveyn_odasi_4: walkway d_L0_023 - win_L0_058 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_022 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_024 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_025 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_026 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_038 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_040 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_061 broken as drawn
- r_L0_yasama_2: walkway o_L0_016 - win_L0_063 broken as drawn
- r_L0_oda_01: walkway d_L0_021 - win_L0_034 broken as drawn
- r_L0_oda_01: walkway d_L0_021 - win_L0_058 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_007 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_008 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_009 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_013 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_037 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_039 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_050 broken as drawn
- r_L0_yasama_3: walkway o_L0_007 - win_L0_052 broken as drawn
- r_L0_yasama_4: walkway d_L0_021 - d_L0_022 broken as drawn
- r_L0_yasama_4: walkway d_L0_021 - d_L0_023 broken as drawn
- r_L0_yasama_4: walkway d_L0_021 - d_L0_024 broken as drawn
- r_L0_yasama_4: walkway d_L0_021 - win_L0_035 broken as drawn
- r_L0_yasama_4: walkway d_L0_021 - win_L0_060 broken as drawn
- r_L0_yasama_4: walkway d_L0_022 - d_L0_023 broken as drawn
- r_L0_yasama_4: walkway d_L0_022 - d_L0_024 broken as drawn
- r_L0_yasama_4: walkway d_L0_022 - win_L0_035 broken as drawn
- r_L0_yasama_4: walkway d_L0_022 - win_L0_060 broken as drawn
- r_L0_yasama_4: walkway d_L0_023 - d_L0_024 broken as drawn
- r_L0_yasama_4: walkway d_L0_023 - win_L0_035 broken as drawn
- r_L0_yasama_4: walkway d_L0_023 - win_L0_060 broken as drawn
- r_L0_yasama_4: walkway d_L0_024 - win_L0_035 broken as drawn
- r_L0_yasama_4: walkway d_L0_024 - win_L0_060 broken as drawn
- r_L0_banyo_3: walkway o_L0_003 - d_L0_017 broken as drawn
- r_L0_oda_7: walkway o_L0_012 - d_L0_001 broken as drawn
- r_L0_oda_7: walkway o_L0_012 - d_L0_004 broken as drawn
- r_L0_oda_7: walkway d_L0_001 - d_L0_004 broken as drawn
- r_L0_kat_holu: walkway o_L0_004 - o_L0_013 broken as drawn
- r_L0_kat_holu: walkway o_L0_004 - d_L0_014 broken as drawn
- r_L0_kat_holu: walkway o_L0_004 - d_L0_016 broken as drawn
- r_L0_kat_holu: walkway o_L0_004 - win_L0_004 broken as drawn
- r_L0_kat_holu: walkway o_L0_004 - win_L0_005 broken as drawn
- r_L0_kat_holu: walkway o_L0_004 - win_L0_006 broken as drawn
- r_L0_kat_holu: walkway o_L0_013 - o_L0_014 broken as drawn
- r_L0_kat_holu: walkway o_L0_013 - d_L0_014 broken as drawn
- r_L0_kat_holu: walkway o_L0_013 - d_L0_016 broken as drawn
- r_L0_kat_holu: walkway o_L0_013 - win_L0_003 broken as drawn
- r_L0_kat_holu: walkway o_L0_013 - win_L0_005 broken as drawn
- r_L0_kat_holu: walkway o_L0_013 - win_L0_006 broken as drawn
- r_L0_kat_holu: walkway o_L0_014 - d_L0_014 broken as drawn
- r_L0_kat_holu: walkway o_L0_014 - d_L0_016 broken as drawn
- r_L0_kat_holu: walkway o_L0_014 - win_L0_004 broken as drawn
- r_L0_kat_holu: walkway o_L0_014 - win_L0_005 broken as drawn
- r_L0_kat_holu: walkway o_L0_014 - win_L0_006 broken as drawn
- r_L0_kat_holu: walkway d_L0_014 - d_L0_016 broken as drawn
- r_L0_kat_holu: walkway d_L0_014 - win_L0_003 broken as drawn
- r_L0_kat_holu: walkway d_L0_014 - win_L0_004 broken as drawn
- r_L0_kat_holu: walkway d_L0_014 - win_L0_005 broken as drawn
- r_L0_kat_holu: walkway d_L0_014 - win_L0_006 broken as drawn
- r_L0_kat_holu: walkway d_L0_016 - win_L0_003 broken as drawn
- r_L0_kat_holu: walkway d_L0_016 - win_L0_004 broken as drawn
- r_L0_kat_holu: walkway d_L0_016 - win_L0_005 broken as drawn
- r_L0_kat_holu: walkway d_L0_016 - win_L0_006 broken as drawn
- r_L0_oda_10: walkway o_L0_015 - d_L0_007 broken as drawn
- r_L0_oda_10: walkway o_L0_015 - d_L0_010 broken as drawn
- r_L0_oda_10: walkway d_L0_007 - d_L0_010 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_010 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_011 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_012 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_014 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_039 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_042 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_051 broken as drawn
- r_L0_yasama_5: walkway o_L0_010 - win_L0_053 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_023 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_027 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_028 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_029 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_040 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_043 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_062 broken as drawn
- r_L0_yasama_6: walkway o_L0_019 - win_L0_064 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_007 - d_L0_008 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_007 - d_L0_009 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_008 - d_L0_009 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_008 - win_L0_028 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_008 - win_L0_062 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_009 - win_L0_028 broken as drawn
- r_L0_giris_holu_3: walkway d_L0_009 - win_L0_062 broken as drawn
- r_L0_banyo_8: walkway d_L0_015 - win_L0_057 broken as drawn
- r_L0_ebeveyn_odasi_5: walkway d_L0_009 - win_L0_029 broken as drawn
- r_L0_ebeveyn_odasi_5: walkway d_L0_009 - win_L0_045 broken as drawn
- r_L0_ebeveyn_odasi_6: walkway d_L0_003 - win_L0_012 broken as drawn
- r_L0_ebeveyn_odasi_6: walkway d_L0_003 - win_L0_044 broken as drawn
- r_L0_yasama_7: walkway d_L0_015 - win_L0_059 broken as drawn
- r_L0_yasama_8: walkway d_L0_013 - d_L0_014 broken as drawn
- r_L0_yasama_8: walkway d_L0_013 - win_L0_055 broken as drawn
- r_L0_yasama_8: walkway d_L0_014 - win_L0_046 broken as drawn
- r_L0_yasama_8: walkway d_L0_014 - win_L0_055 broken as drawn

## Locked check: pass

