# AI completion of furnished rooms: real02

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | completed | 0/12 (9.9 s) | 0/12 (9.7 s) | 0 | tv_unit (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), armchair (0.9), chaise (0.6), console_table (0.6), sideboard (0.6) | - |
| Salon (r_L-1_salon_2) | living | mirrored | - | - | 0 | tv_unit (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), chair (0.6), armchair (0.9), chaise (0.6), console_table (0.6), sideboard (0.6) | decisions of r_L-1_salon (twin), not asked again |
| Mutfak (r_L-1_mutfak) | kitchen | completed | 0/6 (5.4 s) | 0/6 (5.0 s) | 0 | - | - |
| Mutfak (r_L-1_mutfak_2) | kitchen | completed | 0/6 (5.3 s) | 0/6 (5.1 s) | 0 | - | partner r_L-1_mutfak (twin) not used: the twin's drawn furniture does not map onto this room: drawn fridge f_L-1_031 has no counterpart here; asked itself |
| Koridor (r_L-1_koridor) | hall | mirrored | - | - | 0 | console_table (0.9) | decisions of r_L-1_koridor_2 (twin), not asked again |
| Koridor (r_L-1_koridor_2) | hall | completed | 0/1 (1.0 s) | 0/1 (1.0 s) | 0 | console_table (0.9) | - |
| Banyo (r_L-1_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L-1_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L-1_banyo (twin), not asked again |
| Açık Mutfak (r_L-1b_acik_mutfak) | kitchen | completed | 0/6 (5.5 s) | 0/6 (5.4 s) | 0 | tall_cabinet (0.9) | - |
| Açık Mutfak (r_L-1b_acik_mutfak_2) | kitchen | completed | 0/10 (8.4 s) | 0/7 (6.0 s) | 0 | bar_stool (0.6), bar_stool (0.6), bar_stool (0.6), bar_stool (0.6) | - |
| Koridor (r_L-1b_koridor) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | console_table (0.9) | - |
| Koridor (r_L-1b_koridor_2) | hall | mirrored | - | - | 0 | console_table (0.9) | decisions of r_L-1b_koridor (twin), not asked again |
| Banyo (r_L-1b_banyo) | bathroom | copied | - | - | 0 | - | decisions of r_L-1_banyo (same_as), not asked again |
| Banyo (r_L-1b_banyo_2) | bathroom | copied | - | - | 0 | - | decisions of r_L-1_banyo_2 (same_as), not asked again |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | completed | 2/6 (6.6 s) | 0/3 (2.7 s) | 0 | nightstand (0.9), nightstand (0.9), bench (0.6) | - |
| E.yatak Odası (r_L0_e_yatak_odasi) | bedroom | completed | 1/3 (3.6 s) | 0/3 (2.8 s) | 0 | nightstand (0.9), nightstand (0.9), bench (0.6) | - |
| E.yatak Odası (r_L0_e_yatak_odasi_2) | bedroom | completed | 0/3 (2.9 s) | 0/3 (2.7 s) | 0 | nightstand (0.9), nightstand (0.9), bench (0.6) | partner r_L0_e_yatak_odasi (twin) not used: the twin's drawn furniture does not map onto this room: drawn wardrobe f_L0_025 has no counterpart here; asked itself |
| Yatak Odası (r_L0_yatak_odasi_2) | bedroom | mirrored | - | - | 0 | nightstand (0.9), nightstand (0.9), bench (0.6) | decisions of r_L0_yatak_odasi (twin), not asked again |
| E.banyo (r_L0_e_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| E.banyo (r_L0_e_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L0_e_banyo (twin), not asked again |
| Yatak Odası (r_L0_yatak_odasi_3) | bedroom | completed | 1/3 (3.5 s) | 0/3 (2.6 s) | 0 | nightstand (0.9), nightstand (0.9), bench (0.9) | - |
| Yatak Odası (r_L0_yatak_odasi_4) | bedroom | completed | 2/3 (4.3 s) | 0/2 (1.9 s) | 0 | nightstand (0.6), nightstand (0.6), bench (0.6) | partner r_L0_yatak_odasi_3 (twin) not used: the twin's drawn furniture does not map onto this room: drawn bed_double f_L0_023 has no counterpart here; asked itself |
| Oda (r_L0_oda) | hall | completed | 0/1 (1.0 s) | 0/1 (1.0 s) | 0 | - | - |
| Oda (r_L0_oda_2) | hall | completed | 0/1 (1.0 s) | 0/1 (1.0 s) | 0 | - | - |
| Banyo (r_L0_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L0_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L0_banyo (twin), not asked again |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi) | other | completed | 0/3 (2.9 s) | 0/3 (2.8 s) | 0 | armchair (0.9), chair (0.6), bookshelf (0.9) | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | other | mirrored | - | - | 0 | chair (0.6), bookshelf (0.9) | decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again |
| Koridor (r_L1_koridor) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | console_table (0.9) | - |
| Koridor (r_L1_koridor_2) | hall | completed | 0/1 (1.2 s) | 0/1 (1.2 s) | 0 | console_table (0.6) | - |
| Banyo (r_L1_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L1_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L1_banyo (twin), not asked again |

## Changes of drawn pieces (6)

| Room | Piece | Drawn type / size | New type / size | Status | Reason |
|---|---|---|---|---|---|
| r_L0_yatak_odasi | f_L0_021 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yatak_odasi | f_L0_032 | - | dresser | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_e_yatak_odasi | f_L0_009 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yatak_odasi_3 | f_L0_011 | - | wardrobe | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yatak_odasi_4 | f_L0_013 | - | wardrobe | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yatak_odasi_4 | f_L0_024 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |

## Added pieces (58)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L-1_salon | f_L-1_053 | tv_unit | [5.57, 0.42] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_054 | chair | [5.00, 2.50] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_055 | chair | [5.00, 3.00] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_056 | chair | [5.30, 2.00] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_057 | chair | [5.80, 2.00] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_058 | chair | [7.10, 2.60] | 0.45 x 0.45 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_059 | chair | [6.27, 2.04] | 0.40 x 0.40 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_060 | chair | [6.69, 1.97] | 0.40 x 0.40 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_061 | armchair | [1.50, 4.50] | 0.90 x 0.90 | ai | 0.9 | - |
| r_L-1_salon | f_L-1_062 | chaise | [1.19, 5.85] | 0.75 x 1.70 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_063 | console_table | [6.76, 0.40] | 1.20 x 0.35 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_064 | sideboard | [7.16, 3.80] | 1.40 x 0.42 | ai | 0.6 | - |
| r_L-1_salon_2 | f_L-1_066 | tv_unit | [9.61, 0.42] | 1.20 x 0.40 | ai | 0.6 | f_L-1_053 |
| r_L-1_salon_2 | f_L-1_067 | chair | [10.17, 2.50] | 0.50 x 0.50 | ai | 0.6 | f_L-1_054 |
| r_L-1_salon_2 | f_L-1_068 | chair | [10.17, 3.00] | 0.50 x 0.50 | ai | 0.6 | f_L-1_055 |
| r_L-1_salon_2 | f_L-1_069 | chair | [9.87, 2.00] | 0.50 x 0.50 | ai | 0.6 | f_L-1_056 |
| r_L-1_salon_2 | f_L-1_070 | chair | [9.37, 2.00] | 0.50 x 0.50 | ai | 0.6 | f_L-1_057 |
| r_L-1_salon_2 | f_L-1_071 | chair | [8.07, 2.60] | 0.45 x 0.45 | ai | 0.6 | f_L-1_058 |
| r_L-1_salon_2 | f_L-1_072 | chair | [8.90, 2.04] | 0.40 x 0.40 | ai | 0.6 | f_L-1_059 |
| r_L-1_salon_2 | f_L-1_073 | chair | [8.48, 1.97] | 0.40 x 0.40 | ai | 0.6 | f_L-1_060 |
| r_L-1_salon_2 | f_L-1_074 | armchair | [13.67, 4.50] | 0.90 x 0.90 | ai | 0.9 | f_L-1_061 |
| r_L-1_salon_2 | f_L-1_075 | chaise | [13.99, 5.85] | 0.75 x 1.70 | ai | 0.6 | f_L-1_062 |
| r_L-1_salon_2 | f_L-1_076 | console_table | [8.41, 0.40] | 1.20 x 0.35 | ai | 0.6 | f_L-1_063 |
| r_L-1_salon_2 | f_L-1_077 | sideboard | [8.02, 3.80] | 1.40 x 0.42 | ai | 0.6 | f_L-1_064 |
| r_L-1_koridor | f_L-1_078 | console_table | [11.76, 9.03] | 1.20 x 0.35 | ai | 0.9 | f_L-1_065 |
| r_L-1_koridor_2 | f_L-1_065 | console_table | [3.41, 9.03] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L-1b_acik_mutfak | f_L-1b_049 | tall_cabinet | [0.51, 0.71] | 0.40 x 0.58 | ai | 0.9 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_050 | bar_stool | [11.68, 4.20] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_051 | bar_stool | [11.68, 3.70] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_052 | bar_stool | [11.48, 3.20] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_053 | bar_stool | [10.98, 2.90] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_koridor | f_L-1b_054 | console_table | [3.51, 9.29] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L-1b_koridor_2 | f_L-1b_055 | console_table | [11.66, 9.29] | 1.20 x 0.35 | ai | 0.9 | f_L-1b_054 |
| r_L0_yatak_odasi | f_L0_041 | nightstand | [0.42, 4.08] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi | f_L0_042 | nightstand | [0.42, 1.98] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi | f_L0_043 | bench | [2.35, 2.33] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_e_yatak_odasi | f_L0_044 | nightstand | [7.14, 2.02] | 0.60 x 0.45 | ai | 0.9 | - |
| r_L0_e_yatak_odasi | f_L0_045 | nightstand | [7.14, 5.42] | 0.60 x 0.45 | ai | 0.9 | - |
| r_L0_e_yatak_odasi | f_L0_046 | bench | [6.28, 5.62] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_e_yatak_odasi_2 | f_L0_050 | nightstand | [8.01, 2.12] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_e_yatak_odasi_2 | f_L0_051 | nightstand | [8.01, 5.42] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_e_yatak_odasi_2 | f_L0_052 | bench | [8.90, 5.29] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_yatak_odasi_2 | f_L0_053 | nightstand | [14.75, 4.08] | 0.50 x 0.40 | ai | 0.9 | f_L0_041 |
| r_L0_yatak_odasi_2 | f_L0_054 | nightstand | [14.75, 1.98] | 0.50 x 0.40 | ai | 0.9 | f_L0_042 |
| r_L0_yatak_odasi_2 | f_L0_055 | bench | [12.82, 2.33] | 1.20 x 0.40 | ai | 0.6 | f_L0_043 |
| r_L0_yatak_odasi_3 | f_L0_047 | nightstand | [2.32, 11.58] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi_3 | f_L0_048 | nightstand | [1.75, 11.58] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi_3 | f_L0_049 | bench | [0.91, 11.52] | 1.00 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi_4 | f_L0_056 | nightstand | [12.18, 10.51] | 0.50 x 0.40 | ai | 0.6 | - |
| r_L0_yatak_odasi_4 | f_L0_057 | nightstand | [14.75, 11.51] | 0.40 x 0.40 | ai | 0.6 | - |
| r_L0_yatak_odasi_4 | f_L0_058 | bench | [13.42, 9.50] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_029 | armchair | [3.30, 3.60] | 0.90 x 0.90 | ai | 0.9 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_030 | chair | [2.50, 3.40] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_031 | bookshelf | [1.97, 6.00] | 0.80 x 0.30 | ai | 0.9 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_034 | chair | [12.67, 3.40] | 0.50 x 0.50 | ai | 0.6 | f_L1_030 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_035 | bookshelf | [13.20, 6.00] | 0.80 x 0.30 | ai | 0.9 | f_L1_031 |
| r_L1_koridor | f_L1_032 | console_table | [3.51, 10.81] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L1_koridor_2 | f_L1_033 | console_table | [11.66, 10.81] | 1.20 x 0.35 | ai | 0.6 | - |

## Refused and dropped proposals (62)

- r_L-1_salon: pass 1 chair at [7.4, 6.0]: covered: at most 8 chair
- r_L-1_salon: pass 1 chair at [6.7, 6.0]: no repair left
- r_L-1_salon: pass 1 chair at [6.0, 6.0]: no repair left
- r_L-1_salon: pass 1 chair at [3.9, 6.0]: 1.02 m from the nearest table_dining (> 0.6 m)
- r_L-1_salon: pass 1 chair at [3.2, 6.0]: 1.55 m from the nearest table_dining (> 0.6 m)
- r_L-1_salon: pass 1 chair at [2.5, 6.0]: 3.00 m from the nearest table_dining (> 0.6 m)
- r_L-1_salon: pass 1 chair at [1.8, 6.0]: 3.21 m from the nearest table_dining (> 0.6 m)
- r_L-1_mutfak: pass 1 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 1 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 1 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 1 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 1 table_dining at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 1 tall_cabinet at [0.45, 10.26]: no repair left
- r_L-1_mutfak: pass 2 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 2 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 2 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 2 chair at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 2 table_dining at [1.66, 9.44]: no repair left
- r_L-1_mutfak: pass 2 tall_cabinet at [3.12, 11.8]: no repair left
- r_L-1_mutfak_2: pass 1 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 1 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 1 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 1 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 1 table_dining at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 1 tall_cabinet at [12.03, 11.8]: no repair left
- r_L-1_mutfak_2: pass 2 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 2 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 2 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 2 chair at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 2 table_dining at [13.51, 9.44]: no repair left
- r_L-1_mutfak_2: pass 2 tall_cabinet at [14.97, 11.8]: no repair left
- r_L-1b_acik_mutfak: pass 1 chair at [1.82, 6.04]: no repair left
- r_L-1b_acik_mutfak: pass 1 chair at [1.82, 5.6]: no repair left
- r_L-1b_acik_mutfak: pass 1 chair at [2.0, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 1 chair at [1.6, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 1 table_dining at [1.82, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 2 chair at [1.82, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 2 chair at [1.82, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 2 chair at [1.82, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 2 chair at [1.82, 5.82]: no repair left
- r_L-1b_acik_mutfak: pass 2 table_dining at [1.82, 5.82]: no repair left
- r_L-1b_acik_mutfak_2: pass 1 chair at [13.36, 5.82]: no repair left
- r_L-1b_acik_mutfak_2: pass 1 chair at [13.36, 5.82]: no repair left
- r_L-1b_acik_mutfak_2: pass 1 chair at [13.36, 5.82]: no repair left
- r_L-1b_acik_mutfak_2: pass 1 chair at [13.36, 5.82]: no repair left
- r_L-1b_acik_mutfak_2: pass 1 table_dining at [13.36, 5.82]: no repair left
- r_L-1b_acik_mutfak_2: pass 1 tall_cabinet at [14.67, 6.07]: no repair left
- r_L-1b_acik_mutfak_2: pass 2 chair at [12.1, 5.8]: no repair left
- r_L-1b_acik_mutfak_2: pass 2 table_dining at [11.86, 5.8]: no repair left
- r_L-1b_acik_mutfak_2: pass 2 tall_cabinet at [13.43, 2.4]: no repair left
- r_L-1b_acik_mutfak_2: pass 2 chair at [11.95, 5.8]: no table_dining in the room
- r_L-1b_acik_mutfak_2: pass 2 chair at [11.6, 5.8]: no table_dining in the room
- r_L-1b_acik_mutfak_2: pass 2 chair at [11.86, 5.8]: no table_dining in the room
- r_L0_yatak_odasi: pass 1 armchair at [2.8, 3.5]: no repair left
- r_L0_yatak_odasi: pass 1 ottoman at [2.8, 3.0]: no repair left
- r_L0_yatak_odasi: pass 1 bench at [1.15, 6.74]: no repair left
- r_L0_oda: pass 1 console_table at [4.72, 9.74]: no repair left
- r_L0_oda: pass 2 console_table at [7.39, 9.0]: no repair left
- r_L0_oda_2: pass 1 console_table at [7.79, 9.0]: no repair left
- r_L0_oda_2: pass 2 console_table at [7.79, 9.27]: no repair left
- r_L1_oyun_aktivite_ve_dinlenme_odasi: pass 2 table_dining at [3.5, 2.5]: no repair left
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: pass - armchair at [3.3, 3.6]: the copy fails clearance_ok here

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L-1_salon: f_L-1_005 fails inside_room as drawn
- r_L-1_salon: f_L-1_008 fails inside_room as drawn
- r_L-1_salon: f_L-1_017 fails doors_free as drawn
- r_L-1_salon: f_L-1_023 fails no_overlap, windows_free as drawn
- r_L-1_salon: f_L-1_024 fails no_overlap as drawn
- r_L-1_salon: f_L-1_027 fails no_overlap, windows_free as drawn
- r_L-1_salon: f_L-1_028 fails no_overlap as drawn
- r_L-1_salon: f_L-1_034 fails no_overlap as drawn
- r_L-1_salon: f_L-1_035 fails no_overlap as drawn
- r_L-1_salon: f_L-1_039 fails no_overlap as drawn
- r_L-1_salon: f_L-1_041 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_006 fails inside_room as drawn
- r_L-1_salon_2: f_L-1_007 fails doors_free, inside_room as drawn
- r_L-1_salon_2: f_L-1_018 fails doors_free as drawn
- r_L-1_salon_2: f_L-1_021 fails no_overlap, windows_free as drawn
- r_L-1_salon_2: f_L-1_022 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_029 fails no_overlap, windows_free as drawn
- r_L-1_salon_2: f_L-1_030 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_033 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_036 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_040 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_042 fails no_overlap as drawn
- r_L-1_mutfak: f_L-1_001 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_031 fails inside_room, no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_045 fails no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_047 fails no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_049 fails inside_room, no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_002 fails doors_free, inside_room, no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_032 fails inside_room, no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_046 fails no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_048 fails no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_050 fails inside_room, no_overlap as drawn
- r_L-1_koridor: f_L-1_004 fails inside_room as drawn
- r_L-1_koridor_2: f_L-1_003 fails inside_room as drawn
- r_L-1_banyo: f_L-1_010 fails doors_free, inside_room as drawn
- r_L-1_banyo: f_L-1_015 fails inside_room as drawn
- r_L-1_banyo: f_L-1_020 fails inside_room as drawn
- r_L-1_banyo_2: f_L-1_009 fails doors_free, inside_room as drawn
- r_L-1_banyo_2: f_L-1_016 fails inside_room as drawn
- r_L-1_banyo_2: f_L-1_019 fails inside_room as drawn
- r_L-1b_acik_mutfak: f_L-1b_002 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_006 fails doors_free, inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_015 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_016 fails inside_room as drawn
- r_L-1b_acik_mutfak: f_L-1b_018 fails doors_free, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_022 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_025 fails no_overlap, windows_free as drawn
- r_L-1b_acik_mutfak: f_L-1b_026 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_027 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_028 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_032 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_036 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_001 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_005 fails doors_free, inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_013 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_014 fails inside_room as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_017 fails doors_free, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_021 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_023 fails no_overlap, windows_free as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_024 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_029 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_030 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_031 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_035 fails no_overlap as drawn
- r_L-1b_koridor: f_L-1b_004 fails inside_room as drawn
- r_L-1b_koridor_2: f_L-1b_003 fails inside_room as drawn
- r_L-1b_banyo: f_L-1b_010 fails doors_free, inside_room as drawn
- r_L-1b_banyo: f_L-1b_012 fails inside_room as drawn
- r_L-1b_banyo: f_L-1b_020 fails inside_room as drawn
- r_L-1b_banyo_2: f_L-1b_009 fails doors_free, inside_room as drawn
- r_L-1b_banyo_2: f_L-1b_011 fails inside_room as drawn
- r_L-1b_banyo_2: f_L-1b_019 fails inside_room as drawn
- r_L0_yatak_odasi: f_L0_012 fails inside_room as drawn
- r_L0_yatak_odasi: f_L0_021 fails inside_room as drawn
- r_L0_yatak_odasi: f_L0_032 fails inside_room as drawn
- r_L0_e_yatak_odasi: f_L0_003 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi: f_L0_009 fails clearance_ok, doors_free, inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi: f_L0_025 fails clearance_ok, inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi: f_L0_033 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi: f_L0_034 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_004 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_010 fails doors_free, inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_026 fails clearance_ok, inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_035 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_036 fails inside_room, no_overlap as drawn
- r_L0_yatak_odasi_2: f_L0_014 fails inside_room as drawn
- r_L0_yatak_odasi_2: f_L0_022 fails clearance_ok, inside_room as drawn
- r_L0_yatak_odasi_2: f_L0_029 fails inside_room as drawn
- r_L0_e_banyo: f_L0_008 fails inside_room as drawn
- r_L0_e_banyo: f_L0_015 fails inside_room as drawn
- r_L0_e_banyo: f_L0_017 fails inside_room as drawn
- r_L0_e_banyo_2: f_L0_006 fails inside_room as drawn
- r_L0_e_banyo_2: f_L0_016 fails inside_room as drawn
- r_L0_e_banyo_2: f_L0_018 fails inside_room as drawn
- r_L0_yatak_odasi_3: f_L0_011 fails clearance_ok, inside_room as drawn
- r_L0_yatak_odasi_3: f_L0_023 fails inside_room as drawn
- r_L0_yatak_odasi_3: f_L0_031 fails inside_room as drawn
- r_L0_yatak_odasi_4: f_L0_013 fails clearance_ok, inside_room as drawn
- r_L0_yatak_odasi_4: f_L0_024 fails inside_room as drawn
- r_L0_yatak_odasi_4: f_L0_030 fails inside_room as drawn
- r_L0_oda: f_L0_001 fails doors_free, inside_room as drawn
- r_L0_oda_2: f_L0_002 fails doors_free, inside_room as drawn
- r_L0_banyo: f_L0_005 fails doors_free, inside_room as drawn
- r_L0_banyo: f_L0_020 fails inside_room as drawn
- r_L0_banyo: f_L0_027 fails inside_room as drawn
- r_L0_banyo_2: f_L0_007 fails doors_free, inside_room as drawn
- r_L0_banyo_2: f_L0_019 fails inside_room as drawn
- r_L0_banyo_2: f_L0_028 fails inside_room as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_003 fails inside_room, no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_005 fails inside_room as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_009 fails clearance_ok, no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_012 fails clearance_ok, no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_015 fails no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_004 fails inside_room, no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_006 fails inside_room as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_010 fails clearance_ok, no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_011 fails clearance_ok, no_overlap as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_016 fails no_overlap as drawn
- r_L1_koridor: f_L1_002 fails inside_room as drawn
- r_L1_koridor: f_L1_021 fails inside_room as drawn
- r_L1_koridor_2: f_L1_001 fails inside_room as drawn
- r_L1_koridor_2: f_L1_022 fails inside_room as drawn
- r_L1_banyo: f_L1_007 fails doors_free, inside_room as drawn
- r_L1_banyo: f_L1_013 fails inside_room as drawn
- r_L1_banyo: f_L1_019 fails inside_room as drawn
- r_L1_banyo_2: f_L1_008 fails doors_free, inside_room as drawn
- r_L1_banyo_2: f_L1_014 fails inside_room as drawn
- r_L1_banyo_2: f_L1_020 fails inside_room as drawn
- r_L-1_salon: walkway o_L-1_001 - win_L-1_001 broken as drawn
- r_L-1_salon_2: walkway o_L-1_002 - win_L-1_002 broken as drawn
- r_L-1_mutfak: walkway d_L-1_003 - win_L-1_003 broken as drawn
- r_L-1_mutfak_2: walkway d_L-1_004 - win_L-1_004 broken as drawn
- r_L-1b_acik_mutfak: walkway o_L-1b_001 - win_L-1b_001 broken as drawn
- r_L-1b_acik_mutfak_2: walkway o_L-1b_002 - win_L-1b_002 broken as drawn
- r_L0_e_yatak_odasi: walkway d_L0_001 - d_L0_002 broken as drawn
- r_L0_e_yatak_odasi: walkway d_L0_001 - win_L0_002 broken as drawn
- r_L0_e_yatak_odasi: walkway d_L0_002 - win_L0_002 broken as drawn
- r_L0_e_yatak_odasi_2: walkway d_L0_003 - d_L0_004 broken as drawn
- r_L0_e_yatak_odasi_2: walkway d_L0_003 - win_L0_003 broken as drawn
- r_L0_e_yatak_odasi_2: walkway d_L0_004 - win_L0_003 broken as drawn

## Locked check: pass

