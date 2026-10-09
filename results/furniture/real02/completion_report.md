# AI completion of furnished rooms: real02

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces keep their anchor (± 5 cm) and front (± 1°); fixed equipment never changes. A change needs both passes; added pieces pass the six placer checks (confidence 0.9 when both passes proposed them, else 0.6). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Pass 1 (changes/added, s) | Pass 2 | Changed | Added | Note |
|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | completed | 0/5 (5.1 s) | 0/4 (3.9 s) | 0 | tv_unit (0.6), armchair (0.9), console_table (0.9), chaise (0.6), bookshelf (0.6) | - |
| Salon (r_L-1_salon_2) | living | mirrored | - | - | 0 | tv_unit (0.6), armchair (0.9), console_table (0.9), bookshelf (0.6) | decisions of r_L-1_salon (twin), not asked again |
| Mutfak (r_L-1_mutfak) | kitchen | completed | 0/6 (5.7 s) | 0/6 (5.8 s) | 0 | tall_cabinet (0.6), table_dining (0.6), chair (0.6), chair (0.6), wall_cabinet (1.0), wall_cabinet (1.0), wall_cabinet (1.0) | - |
| Mutfak (r_L-1_mutfak_2) | kitchen | mirrored | - | - | 0 | tall_cabinet (0.6), table_dining (0.6), chair (0.6), chair (0.6), wall_cabinet (1.0), wall_cabinet (1.0), wall_cabinet (1.0) | decisions of r_L-1_mutfak (twin), not asked again |
| Koridor (r_L-1_koridor) | hall | mirrored | - | - | 0 | console_table (0.9) | decisions of r_L-1_koridor_2 (twin), not asked again |
| Koridor (r_L-1_koridor_2) | hall | completed | 0/1 (1.2 s) | 0/1 (1.1 s) | 0 | console_table (0.9) | - |
| Banyo (r_L-1_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L-1_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L-1_banyo (twin), not asked again |
| Açık Mutfak (r_L-1b_acik_mutfak) | kitchen | completed | 0/4 (4.1 s) | 0/4 (4.1 s) | 0 | bar_stool (0.9), bar_stool (0.9), bar_stool (0.9), tall_cabinet (0.6) | - |
| Açık Mutfak (r_L-1b_acik_mutfak_2) | kitchen | completed | 0/5 (5.2 s) | 0/5 (4.9 s) | 0 | tall_cabinet (0.6), bar_stool (0.6), bar_stool (0.6), bar_stool (0.6), bar_stool (0.6) | partner r_L-1b_acik_mutfak (twin) not used: the twin's drawn furniture does not map onto this room: drawn unknown f_L-1b_040 has no counterpart here; asked itself |
| Koridor (r_L-1b_koridor) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | console_table (0.9) | - |
| Koridor (r_L-1b_koridor_2) | hall | mirrored | - | - | 0 | console_table (0.9) | decisions of r_L-1b_koridor (twin), not asked again |
| Banyo (r_L-1b_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get; partner r_L-1_banyo (same_as) not used: the same_as's drawn furniture does not map onto this room: drawn toilet f_L-1_051 has no counterpart here; asked itself |
| Banyo (r_L-1b_banyo_2) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get; partner r_L-1_banyo_2 (same_as) not used: the same_as's drawn furniture does not map onto this room: drawn toilet f_L-1_052 has no counterpart here; asked itself |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | completed | 1/4 (4.7 s) | 0/3 (3.1 s) | 0 | nightstand (0.6), nightstand (0.9), bench (0.6) | - |
| E.yatak Odası (r_L0_e_yatak_odasi) | bedroom | completed | 1/3 (3.9 s) | 0/2 (2.1 s) | 0 | nightstand (0.6), nightstand (0.6), bench (0.6) | - |
| E.yatak Odası (r_L0_e_yatak_odasi_2) | bedroom | mirrored | - | - | 0 | nightstand (0.6), nightstand (0.6), bench (0.6) | decisions of r_L0_e_yatak_odasi (twin), not asked again |
| Yatak Odası (r_L0_yatak_odasi_2) | bedroom | mirrored | - | - | 0 | nightstand (0.6), nightstand (0.9), bench (0.6) | decisions of r_L0_yatak_odasi (twin), not asked again |
| E.banyo (r_L0_e_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| E.banyo (r_L0_e_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L0_e_banyo (twin), not asked again |
| Yatak Odası (r_L0_yatak_odasi_3) | bedroom | completed | 1/3 (3.7 s) | 0/3 (2.8 s) | 0 | nightstand (0.9), nightstand (0.9), bench (0.9) | - |
| Yatak Odası (r_L0_yatak_odasi_4) | bedroom | mirrored | - | - | 0 | nightstand (0.9), nightstand (0.9), bench (0.9) | decisions of r_L0_yatak_odasi_3 (twin), not asked again |
| Merdiven (r_L0_merdiven) | hall | completed | 0/1 (1.1 s) | 0/1 (1.1 s) | 0 | - | - |
| Merdiven (r_L0_merdiven_2) | hall | mirrored | - | - | 0 | - | decisions of r_L0_merdiven (twin), not asked again |
| Banyo (r_L0_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L0_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L0_banyo (twin), not asked again |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi) | other | completed | 0/3 (3.0 s) | 0/3 (3.0 s) | 0 | armchair (0.9), chair (0.6), bookshelf (0.9) | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | other | mirrored | - | - | 0 | armchair (0.9), chair (0.6), bookshelf (0.9) | decisions of r_L1_oyun_aktivite_ve_dinlenme_odasi (twin), not asked again |
| Koridor (r_L1_koridor) | hall | completed | 0/1 (1.2 s) | 0/1 (1.3 s) | 0 | console_table (0.6) | - |
| Koridor (r_L1_koridor_2) | hall | mirrored | - | - | 0 | console_table (0.6) | decisions of r_L1_koridor (twin), not asked again |
| Banyo (r_L1_banyo) | bathroom | completed | - | - | 0 | - | nothing to ask: no changeable drawn piece and nothing the room may get |
| Banyo (r_L1_banyo_2) | bathroom | mirrored | - | - | 0 | - | decisions of r_L1_banyo (twin), not asked again |

## Changes of drawn pieces (3)

| Room | Piece | Drawn type / size | New type / size | Status | Reason |
|---|---|---|---|---|---|
| r_L0_yatak_odasi | f_L0_019 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_e_yatak_odasi | f_L0_007 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |
| r_L0_yatak_odasi_3 | f_L0_021 | - | bed_double | not_agreed | only pass 1 changes it (a drawn piece needs both passes) |

## Added pieces (62)

| Room | Piece | Type | Centre | Size | Method | Confidence | From |
|---|---|---|---|---|---|---|---|
| r_L-1_salon | f_L-1_089 | tv_unit | [3.08, 0.45] | 1.60 x 0.45 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_090 | armchair | [1.30, 5.00] | 0.90 x 0.90 | ai | 0.9 | - |
| r_L-1_salon | f_L-1_091 | console_table | [1.50, 4.30] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L-1_salon | f_L-1_092 | chaise | [1.50, 3.00] | 0.75 x 1.70 | ai | 0.6 | - |
| r_L-1_salon | f_L-1_093 | bookshelf | [7.19, 1.87] | 1.00 x 0.35 | ai | 0.6 | - |
| r_L-1_salon_2 | f_L-1_102 | tv_unit | [12.09, 0.45] | 1.60 x 0.45 | ai | 0.6 | f_L-1_089 |
| r_L-1_salon_2 | f_L-1_103 | armchair | [13.87, 5.00] | 0.90 x 0.90 | ai | 0.9 | f_L-1_090 |
| r_L-1_salon_2 | f_L-1_104 | console_table | [13.67, 4.30] | 1.20 x 0.35 | ai | 0.9 | f_L-1_091 |
| r_L-1_salon_2 | f_L-1_105 | bookshelf | [7.98, 1.87] | 1.00 x 0.35 | ai | 0.6 | f_L-1_093 |
| r_L-1_mutfak | f_L-1_094 | tall_cabinet | [1.41, 7.45] | 0.40 x 0.58 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_095 | table_dining | [1.66, 10.26] | 1.60 x 0.90 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_096 | chair | [1.86, 10.96] | 0.45 x 0.45 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_097 | chair | [1.36, 10.96] | 0.45 x 0.45 | ai | 0.6 | - |
| r_L-1_mutfak | f_L-1_098 | wall_cabinet | [2.95, 10.13] | 3.35 x 0.35 | rule | 1.0 | - |
| r_L-1_mutfak | f_L-1_099 | wall_cabinet | [0.86, 11.63] | 0.69 x 0.35 | rule | 1.0 | - |
| r_L-1_mutfak | f_L-1_100 | wall_cabinet | [2.24, 11.63] | 0.56 x 0.35 | rule | 1.0 | - |
| r_L-1_mutfak_2 | f_L-1_106 | tall_cabinet | [13.76, 7.45] | 0.40 x 0.58 | ai | 0.6 | f_L-1_094 |
| r_L-1_mutfak_2 | f_L-1_107 | table_dining | [13.51, 10.26] | 1.60 x 0.90 | ai | 0.6 | f_L-1_095 |
| r_L-1_mutfak_2 | f_L-1_108 | chair | [13.31, 10.96] | 0.45 x 0.45 | ai | 0.6 | f_L-1_096 |
| r_L-1_mutfak_2 | f_L-1_109 | chair | [13.81, 10.96] | 0.45 x 0.45 | ai | 0.6 | f_L-1_097 |
| r_L-1_mutfak_2 | f_L-1_110 | wall_cabinet | [12.23, 10.12] | 3.36 x 0.35 | rule | 1.0 | - |
| r_L-1_mutfak_2 | f_L-1_111 | wall_cabinet | [12.93, 11.63] | 0.56 x 0.35 | rule | 1.0 | - |
| r_L-1_mutfak_2 | f_L-1_112 | wall_cabinet | [14.32, 11.63] | 0.69 x 0.35 | rule | 1.0 | - |
| r_L-1_koridor | f_L-1_113 | console_table | [11.76, 9.03] | 1.20 x 0.35 | ai | 0.9 | f_L-1_101 |
| r_L-1_koridor_2 | f_L-1_101 | console_table | [3.41, 9.03] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L-1b_acik_mutfak | f_L-1b_071 | bar_stool | [1.59, 4.10] | 0.42 x 0.42 | ai | 0.9 | - |
| r_L-1b_acik_mutfak | f_L-1b_072 | bar_stool | [2.09, 4.10] | 0.42 x 0.42 | ai | 0.9 | - |
| r_L-1b_acik_mutfak | f_L-1b_073 | bar_stool | [1.09, 3.80] | 0.42 x 0.42 | ai | 0.9 | - |
| r_L-1b_acik_mutfak | f_L-1b_074 | tall_cabinet | [7.07, 4.48] | 0.60 x 0.60 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_076 | tall_cabinet | [8.11, 5.73] | 0.60 x 0.60 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_077 | bar_stool | [10.28, 4.98] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_078 | bar_stool | [10.28, 3.98] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_079 | bar_stool | [11.68, 4.48] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_acik_mutfak_2 | f_L-1b_080 | bar_stool | [10.28, 4.48] | 0.42 x 0.42 | ai | 0.6 | - |
| r_L-1b_koridor | f_L-1b_075 | console_table | [3.51, 9.29] | 1.20 x 0.35 | ai | 0.9 | - |
| r_L-1b_koridor_2 | f_L-1b_081 | console_table | [11.66, 9.29] | 1.20 x 0.35 | ai | 0.9 | f_L-1b_075 |
| r_L0_yatak_odasi | f_L0_039 | nightstand | [0.42, 4.01] | 0.40 x 0.40 | ai | 0.6 | - |
| r_L0_yatak_odasi | f_L0_040 | nightstand | [1.75, 1.92] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi | f_L0_041 | bench | [0.90, 1.95] | 1.00 x 0.40 | ai | 0.6 | - |
| r_L0_e_yatak_odasi | f_L0_042 | nightstand | [6.67, 1.92] | 0.50 x 0.40 | ai | 0.6 | - |
| r_L0_e_yatak_odasi | f_L0_043 | nightstand | [7.17, 2.12] | 0.50 x 0.40 | ai | 0.6 | - |
| r_L0_e_yatak_odasi | f_L0_044 | bench | [6.39, 5.32] | 1.20 x 0.40 | ai | 0.6 | - |
| r_L0_e_yatak_odasi_2 | f_L0_048 | nightstand | [8.51, 1.92] | 0.50 x 0.40 | ai | 0.6 | f_L0_042 |
| r_L0_e_yatak_odasi_2 | f_L0_049 | nightstand | [8.01, 2.12] | 0.50 x 0.40 | ai | 0.6 | f_L0_043 |
| r_L0_e_yatak_odasi_2 | f_L0_050 | bench | [8.78, 5.32] | 1.20 x 0.40 | ai | 0.6 | f_L0_044 |
| r_L0_yatak_odasi_2 | f_L0_051 | nightstand | [14.75, 4.01] | 0.40 x 0.40 | ai | 0.6 | f_L0_039 |
| r_L0_yatak_odasi_2 | f_L0_052 | nightstand | [13.42, 1.92] | 0.50 x 0.40 | ai | 0.9 | f_L0_040 |
| r_L0_yatak_odasi_2 | f_L0_053 | bench | [14.27, 1.95] | 1.00 x 0.40 | ai | 0.6 | f_L0_041 |
| r_L0_yatak_odasi_3 | f_L0_045 | nightstand | [2.32, 11.58] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi_3 | f_L0_046 | nightstand | [1.80, 11.58] | 0.50 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi_3 | f_L0_047 | bench | [0.90, 11.56] | 1.20 x 0.40 | ai | 0.9 | - |
| r_L0_yatak_odasi_4 | f_L0_054 | nightstand | [12.85, 11.58] | 0.50 x 0.40 | ai | 0.9 | f_L0_045 |
| r_L0_yatak_odasi_4 | f_L0_055 | nightstand | [13.37, 11.58] | 0.50 x 0.40 | ai | 0.9 | f_L0_046 |
| r_L0_yatak_odasi_4 | f_L0_056 | bench | [14.28, 11.56] | 1.20 x 0.40 | ai | 0.9 | f_L0_047 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_029 | armchair | [2.70, 4.10] | 0.90 x 0.90 | ai | 0.9 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_030 | chair | [2.30, 3.40] | 0.50 x 0.50 | ai | 0.6 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_031 | bookshelf | [1.97, 6.00] | 0.80 x 0.30 | ai | 0.9 | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_033 | armchair | [12.47, 4.10] | 0.90 x 0.90 | ai | 0.9 | f_L1_029 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_034 | chair | [12.87, 3.40] | 0.50 x 0.50 | ai | 0.6 | f_L1_030 |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_035 | bookshelf | [13.20, 6.00] | 0.80 x 0.30 | ai | 0.9 | f_L1_031 |
| r_L1_koridor | f_L1_032 | console_table | [3.49, 10.66] | 0.90 x 0.30 | ai | 0.6 | - |
| r_L1_koridor_2 | f_L1_036 | console_table | [11.68, 10.66] | 0.90 x 0.30 | ai | 0.6 | f_L1_032 |

## Refused and dropped proposals (14)

- r_L-1_salon_2: pass - chaise at [1.5, 3.0]: the copy fails clearance_ok here
- r_L-1_mutfak: pass 1 chair at [1.5, 8.7]: no repair left
- r_L-1_mutfak: pass 1 chair at [1.2, 8.7]: no repair left
- r_L-1_mutfak: pass 1 chair at [1.5, 8.3]: no repair left
- r_L-1_mutfak: pass 1 table_dining at [1.36, 8.5]: no repair left
- r_L-1_mutfak: pass 1 tall_cabinet at [3.12, 8.15]: no repair left
- r_L-1_mutfak: pass 1 chair at [1.2, 8.3]: no table_dining in the room
- r_L-1_mutfak: pass 2 chair at [1.36, 10.26]: no repair left
- r_L-1_mutfak: pass 2 chair at [1.36, 10.26]: no repair left
- r_L-1b_acik_mutfak: pass 1 bar_stool at [1.59, 2.4]: 1.71 m from the nearest kitchen_island (> 0.6 m)
- r_L-1b_acik_mutfak_2: pass 2 bar_stool at [13.58, 3.2]: 0.61 m from the nearest kitchen_island (> 0.6 m)
- r_L0_yatak_odasi: pass 1 dresser at [2.5, 5.06]: no repair left
- r_L0_merdiven: pass 1 console_table at [4.72, 9.74]: no repair left
- r_L0_merdiven: pass 2 console_table at [7.39, 8.97]: no repair left

## drawn_layout (checks the drawn layout already fails; not counted against the AI)

- r_L-1_salon: f_L-1_021 fails inside_room as drawn
- r_L-1_salon: f_L-1_024 fails inside_room as drawn
- r_L-1_salon: f_L-1_027 fails no_overlap as drawn
- r_L-1_salon: f_L-1_028 fails no_overlap as drawn
- r_L-1_salon: f_L-1_029 fails no_overlap as drawn
- r_L-1_salon: f_L-1_030 fails no_overlap as drawn
- r_L-1_salon: f_L-1_031 fails no_overlap as drawn
- r_L-1_salon: f_L-1_032 fails no_overlap as drawn
- r_L-1_salon: f_L-1_033 fails no_overlap as drawn
- r_L-1_salon: f_L-1_034 fails no_overlap as drawn
- r_L-1_salon: f_L-1_035 fails no_overlap as drawn
- r_L-1_salon: f_L-1_036 fails no_overlap as drawn
- r_L-1_salon: f_L-1_037 fails no_overlap as drawn
- r_L-1_salon: f_L-1_049 fails clearance_ok, no_overlap as drawn
- r_L-1_salon: f_L-1_053 fails doors_free as drawn
- r_L-1_salon: f_L-1_059 fails no_overlap, windows_free as drawn
- r_L-1_salon: f_L-1_060 fails no_overlap as drawn
- r_L-1_salon: f_L-1_063 fails no_overlap, windows_free as drawn
- r_L-1_salon: f_L-1_064 fails no_overlap as drawn
- r_L-1_salon: f_L-1_070 fails no_overlap as drawn
- r_L-1_salon: f_L-1_071 fails no_overlap as drawn
- r_L-1_salon: f_L-1_075 fails no_overlap as drawn
- r_L-1_salon: f_L-1_077 fails no_overlap as drawn
- r_L-1_salon: f_L-1_087 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_022 fails inside_room as drawn
- r_L-1_salon_2: f_L-1_023 fails doors_free, inside_room as drawn
- r_L-1_salon_2: f_L-1_038 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_039 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_040 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_041 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_042 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_043 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_044 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_045 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_046 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_047 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_048 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_050 fails clearance_ok, no_overlap as drawn
- r_L-1_salon_2: f_L-1_054 fails doors_free as drawn
- r_L-1_salon_2: f_L-1_057 fails no_overlap, windows_free as drawn
- r_L-1_salon_2: f_L-1_058 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_065 fails no_overlap, windows_free as drawn
- r_L-1_salon_2: f_L-1_066 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_069 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_072 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_076 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_078 fails no_overlap as drawn
- r_L-1_salon_2: f_L-1_088 fails no_overlap as drawn
- r_L-1_mutfak: f_L-1_001 fails doors_free, inside_room, no_overlap as drawn
- r_L-1_mutfak: f_L-1_002 fails inside_room, no_overlap as drawn
- r_L-1_mutfak: f_L-1_003 fails inside_room, no_overlap as drawn
- r_L-1_mutfak: f_L-1_004 fails inside_room as drawn
- r_L-1_mutfak: f_L-1_005 fails doors_free, inside_room, no_overlap as drawn
- r_L-1_mutfak: f_L-1_008 fails no_overlap as drawn
- r_L-1_mutfak: f_L-1_009 fails no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_067 fails inside_room, no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_081 fails no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_083 fails no_overlap, windows_free as drawn
- r_L-1_mutfak: f_L-1_085 fails inside_room, no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_010 fails doors_free, inside_room, no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_011 fails inside_room, no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_012 fails inside_room, no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_013 fails inside_room as drawn
- r_L-1_mutfak_2: f_L-1_014 fails doors_free, inside_room, no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_017 fails no_overlap as drawn
- r_L-1_mutfak_2: f_L-1_018 fails no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_068 fails inside_room, no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_082 fails no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_084 fails no_overlap, windows_free as drawn
- r_L-1_mutfak_2: f_L-1_086 fails inside_room, no_overlap as drawn
- r_L-1_koridor: f_L-1_020 fails inside_room as drawn
- r_L-1_koridor_2: f_L-1_019 fails inside_room as drawn
- r_L-1_banyo: f_L-1_026 fails doors_free, inside_room as drawn
- r_L-1_banyo: f_L-1_051 fails inside_room as drawn
- r_L-1_banyo: f_L-1_056 fails inside_room as drawn
- r_L-1_banyo_2: f_L-1_025 fails doors_free, inside_room as drawn
- r_L-1_banyo_2: f_L-1_052 fails inside_room as drawn
- r_L-1_banyo_2: f_L-1_055 fails inside_room as drawn
- r_L-1b_acik_mutfak: f_L-1b_009 fails doors_free, inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_010 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_012 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_013 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_014 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_026 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_027 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_028 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_029 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_030 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_031 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_032 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_033 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_034 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_047 fails no_overlap, windows_free as drawn
- r_L-1b_acik_mutfak: f_L-1b_048 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_054 fails no_overlap as drawn
- r_L-1b_acik_mutfak: f_L-1b_058 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_003 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_004 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_006 fails inside_room, no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_007 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_008 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_017 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_018 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_019 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_020 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_021 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_022 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_023 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_024 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_025 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_045 fails no_overlap, windows_free as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_046 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_053 fails no_overlap as drawn
- r_L-1b_acik_mutfak_2: f_L-1b_057 fails no_overlap as drawn
- r_L-1b_koridor: f_L-1b_016 fails inside_room as drawn
- r_L-1b_koridor_2: f_L-1b_015 fails inside_room as drawn
- r_L-1b_banyo: f_L-1b_036 fails doors_free, inside_room as drawn
- r_L-1b_banyo: f_L-1b_038 fails inside_room as drawn
- r_L-1b_banyo: f_L-1b_042 fails inside_room as drawn
- r_L-1b_banyo_2: f_L-1b_035 fails doors_free, inside_room as drawn
- r_L-1b_banyo_2: f_L-1b_037 fails inside_room as drawn
- r_L-1b_banyo_2: f_L-1b_041 fails inside_room as drawn
- r_L0_yatak_odasi: f_L0_010 fails inside_room as drawn
- r_L0_yatak_odasi: f_L0_019 fails inside_room as drawn
- r_L0_yatak_odasi: f_L0_030 fails inside_room as drawn
- r_L0_e_yatak_odasi: f_L0_007 fails doors_free, inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi: f_L0_023 fails inside_room as drawn
- r_L0_e_yatak_odasi: f_L0_031 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi: f_L0_032 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_008 fails doors_free, inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_024 fails inside_room as drawn
- r_L0_e_yatak_odasi_2: f_L0_033 fails inside_room, no_overlap as drawn
- r_L0_e_yatak_odasi_2: f_L0_034 fails inside_room, no_overlap as drawn
- r_L0_yatak_odasi_2: f_L0_012 fails inside_room as drawn
- r_L0_yatak_odasi_2: f_L0_020 fails inside_room as drawn
- r_L0_yatak_odasi_2: f_L0_027 fails inside_room as drawn
- r_L0_e_banyo: f_L0_006 fails inside_room as drawn
- r_L0_e_banyo: f_L0_013 fails inside_room as drawn
- r_L0_e_banyo: f_L0_015 fails inside_room as drawn
- r_L0_e_banyo_2: f_L0_004 fails inside_room as drawn
- r_L0_e_banyo_2: f_L0_014 fails inside_room as drawn
- r_L0_e_banyo_2: f_L0_016 fails inside_room as drawn
- r_L0_yatak_odasi_3: f_L0_009 fails clearance_ok, inside_room as drawn
- r_L0_yatak_odasi_3: f_L0_021 fails inside_room as drawn
- r_L0_yatak_odasi_3: f_L0_029 fails inside_room as drawn
- r_L0_yatak_odasi_4: f_L0_011 fails clearance_ok, inside_room as drawn
- r_L0_yatak_odasi_4: f_L0_022 fails inside_room as drawn
- r_L0_yatak_odasi_4: f_L0_028 fails inside_room as drawn
- r_L0_merdiven: f_L0_001 fails doors_free, inside_room as drawn
- r_L0_merdiven_2: f_L0_002 fails doors_free, inside_room as drawn
- r_L0_banyo: f_L0_003 fails doors_free, inside_room as drawn
- r_L0_banyo: f_L0_018 fails inside_room as drawn
- r_L0_banyo: f_L0_025 fails inside_room as drawn
- r_L0_banyo_2: f_L0_005 fails doors_free, inside_room as drawn
- r_L0_banyo_2: f_L0_017 fails inside_room as drawn
- r_L0_banyo_2: f_L0_026 fails inside_room as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_005 fails inside_room as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi: f_L1_009 fails clearance_ok as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_006 fails inside_room as drawn
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: f_L1_010 fails clearance_ok as drawn
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
- r_L0_e_yatak_odasi: walkway d_L0_001 - d_L0_002 broken as drawn
- r_L0_e_yatak_odasi: walkway d_L0_001 - win_L0_002 broken as drawn
- r_L0_e_yatak_odasi: walkway d_L0_002 - win_L0_002 broken as drawn
- r_L0_e_yatak_odasi_2: walkway d_L0_003 - d_L0_004 broken as drawn
- r_L0_e_yatak_odasi_2: walkway d_L0_003 - win_L0_003 broken as drawn
- r_L0_e_yatak_odasi_2: walkway d_L0_004 - win_L0_003 broken as drawn

## Locked check: pass

