# Ingest report: real02

Status: **ok**
Source: `projects/real02`, pipeline commit `cddf61aa`, created 2026-10-10T01:09:34Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| one_building.dwg | 1 r2 | floor_plan | vector | L-1 | 0.01 m/unit (unit_check) | 0.99 | - | debug/one_building_dwg_p1_r2.png |
| one_building.dwg | 1 r3 | floor_plan | vector | L-1b | 0.01 m/unit (unit_check) | 0.99 | - | debug/one_building_dwg_p1_r3.png |
| one_building.dwg | 1 r4 | floor_plan | vector | L0 | 0.01 m/unit (unit_check) | 0.99 | - | debug/one_building_dwg_p1_r4.png |
| one_building.dwg | 1 r5 | floor_plan | vector | L1 | 0.01 m/unit (unit_check) | 0.99 | - | debug/one_building_dwg_p1_r5.png |
| one_building.dwg | 1 r6 | section | vector | - | 0.01 m/unit (unit_check) | 0.85 | section: read for the heights by the sheets stage (sheets.json r6) | debug/one_building_dwg_p1_r6.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | -1 | -3.00 | 2.85 (section) | 15 | 10 | 8 | 88 |
| L-1b | Bodrum Kat | -1 | -3.00 | 2.85 (section) | 13 | 8 | 8 | 60 |
| L0 | Zemin Kat | 0 | 0.00 | 3.00 (section) | 17 | 18 | 14 | 34 |
| L1 | Çatı Katı | 1 | 3.15 | 3.43 (section) | 16 | 9 | 8 | 28 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L-1_salon | L-1 | Salon | SALON | living | 50,86 | 49,00 | yes | verified |
| r_L-1_salon_2 | L-1 | Salon | SALON | living | 50,86 | 49,00 | yes | verified |
| r_L-1_mutfak | L-1 | Mutfak | MUTFAK | kitchen | 13,63 | 14,50 | yes | verified |
| r_L-1_mutfak_2 | L-1 | Mutfak | MUTFAK | kitchen | 13,62 | 14,50 | yes | verified |
| r_L-1_koridor | L-1 | Koridor | KORİDOR | hall | 11,92 | 7,00 | yes | unverified |
| r_L-1_koridor_2 | L-1 | Koridor | KORİDOR | hall | 11,93 | 7,00 | yes | unverified |
| r_L-1_banyo | L-1 | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L-1_banyo_2 | L-1 | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L-1b_acik_mutfak | L-1b | Açık Mutfak | AÇIK MUTFAK | kitchen | 51,83 | 8,50 | yes | unverified |
| r_L-1b_acik_mutfak_2 | L-1b | Açık Mutfak | AÇIK MUTFAK | kitchen | 51,83 | 8,50 | yes | unverified |
| r_L-1b_oda | L-1b | Oda | ODA | other | 13,14 | 13,00 | no | verified |
| r_L-1b_oda_2 | L-1b | Oda | ODA | other | 13,15 | 13,00 | no | verified |
| r_L-1b_koridor | L-1b | Koridor | KORİDOR | hall | 11,50 | 7,00 | yes | unverified |
| r_L-1b_koridor_2 | L-1b | Koridor | KORİDOR | hall | 11,50 | 7,00 | yes | unverified |
| r_L-1b_banyo | L-1b | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L-1b_banyo_2 | L-1b | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | YATAK ODASI | bedroom | 16,13 | 16,00 | yes | verified |
| r_L0_e_yatak_odasi | L0 | E.yatak Odası | E.YATAK ODASI | bedroom | 16,86 | 17,00 | yes | verified |
| r_L0_e_yatak_odasi_2 | L0 | E.yatak Odası | E.YATAK ODASI | bedroom | 16,87 | 17,00 | yes | verified |
| r_L0_yatak_odasi_2 | L0 | Yatak Odası | YATAK ODASI | bedroom | 16,12 | 16,00 | yes | verified |
| r_L0_koridor | L0 | Koridor | KORİDOR | hall | 7,61 | 7,00 | no | unverified |
| r_L0_e_banyo | L0 | E.banyo | E.BANYO | bathroom | 4,00 | 4,00 | yes | verified |
| r_L0_e_banyo_2 | L0 | E.banyo | E.BANYO | bathroom | 4,00 | 4,00 | yes | verified |
| r_L0_koridor_2 | L0 | Koridor | KORİDOR | hall | 7,61 | 7,00 | no | unverified |
| r_L0_yatak_odasi_3 | L0 | Yatak Odası | YATAK ODASI | bedroom | 14,05 | 17,00 | yes | unverified |
| r_L0_yatak_odasi_4 | L0 | Yatak Odası | YATAK ODASI | bedroom | 14,04 | 17,00 | yes | unverified |
| r_L0_merdiven | L0 | Merdiven | — | hall | 5,71 | - | yes | unverified |
| r_L0_merdiven_2 | L0 | Merdiven | — | hall | 5,72 | - | yes | unverified |
| r_L0_banyo | L0 | Banyo | BANYO | bathroom | 4,97 | 4,90 | yes | verified |
| r_L0_banyo_2 | L0 | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L1_teras | L1 | Teras | TERAS | balcony | 19,68 | 22,00 | no | unverified |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | L1 | Oyun Aktivite Ve Dinlenme Odası | OYUN AKTİVİTE VE DİNLENME ODASI | other | 40,45 | 40,00 | yes | verified |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | L1 | Oyun Aktivite Ve Dinlenme Odası | OYUN AKTİVİTE VE DİNLENME ODASI | other | 40,45 | 40,00 | yes | verified |
| r_L1_koridor | L1 | Koridor | KORİDOR | hall | 15,34 | 10,00 | yes | verified |
| r_L1_koridor_2 | L1 | Koridor | KORİDOR | hall | 15,34 | 10,00 | yes | verified |
| r_L1_banyo | L1 | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L1_banyo_2 | L1 | Banyo | BANYO | bathroom | 4,98 | 4,90 | yes | verified |
| r_L1_teras_2 | L1 | Teras | TERAS | balcony | 19,68 | 22,00 | no | unverified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L-1_001 | L-1 | r_L-1_mutfak | kitchen_counter | - | from_documents | 3.66 x 0.60 | 270 | verified | one_building.dwg |
| f_L-1_002 | L-1 | r_L-1_mutfak | kitchen_counter | - | from_documents | 2.32 x 0.60 | 0 | verified | one_building.dwg |
| f_L-1_003 | L-1 | r_L-1_mutfak | kitchen_counter | - | from_documents | 1.88 x 0.60 | 90 | verified | one_building.dwg |
| f_L-1_004 | L-1 | r_L-1_mutfak | kitchen_counter | - | from_documents | 2.18 x 0.60 | 90 | verified | one_building.dwg |
| f_L-1_005 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.62 x 0.60 | 0 | unverified | one_building.dwg |
| f_L-1_006 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.45 x 0.23 | 90 | unverified | one_building.dwg |
| f_L-1_007 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.45 x 0.23 | 90 | unverified | one_building.dwg |
| f_L-1_008 | L-1 | r_L-1_mutfak | stove | ocak_ | from_documents | 0.75 x 0.55 | 0 | verified | one_building.dwg |
| f_L-1_009 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.51 x 0.11 | 90 | unverified | one_building.dwg |
| f_L-1_010 | L-1 | r_L-1_mutfak_2 | kitchen_counter | - | from_documents | 3.66 x 0.60 | 90 | verified | one_building.dwg |
| f_L-1_011 | L-1 | r_L-1_mutfak_2 | kitchen_counter | - | from_documents | 2.32 x 0.60 | 0 | verified | one_building.dwg |
| f_L-1_012 | L-1 | r_L-1_mutfak_2 | kitchen_counter | - | from_documents | 1.88 x 0.60 | 270 | verified | one_building.dwg |
| f_L-1_013 | L-1 | r_L-1_mutfak_2 | kitchen_counter | - | from_documents | 2.18 x 0.60 | 270 | verified | one_building.dwg |
| f_L-1_014 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.62 x 0.60 | 0 | unverified | one_building.dwg |
| f_L-1_015 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.45 x 0.23 | 90 | unverified | one_building.dwg |
| f_L-1_016 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.45 x 0.23 | 90 | unverified | one_building.dwg |
| f_L-1_017 | L-1 | r_L-1_mutfak_2 | stove | ocak_ | from_documents | 0.75 x 0.55 | 0 | verified | one_building.dwg |
| f_L-1_018 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.51 x 0.11 | 90 | unverified | one_building.dwg |
| f_L-1_019 | L-1 | r_L-1_koridor_2 | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L-1_020 | L-1 | r_L-1_koridor | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L-1_021 | L-1 | r_L-1_salon | unknown | - | from_documents | 5.54 x 0.60 | 90 | unverified | one_building.dwg |
| f_L-1_022 | L-1 | r_L-1_salon_2 | unknown | - | from_documents | 5.54 x 0.60 | 90 | unverified | one_building.dwg |
| f_L-1_023 | L-1 | r_L-1_salon_2 | wardrobe | dolap01 | from_documents | 2.57 x 0.74 | 0 | verified | one_building.dwg |
| f_L-1_024 | L-1 | r_L-1_salon | wardrobe | dolap01 | from_documents | 2.57 x 0.74 | 0 | verified | one_building.dwg |
| f_L-1_025 | L-1 | r_L-1_banyo_2 | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L-1_026 | L-1 | r_L-1_banyo | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L-1_027 | L-1 | r_L-1_salon | table_dining | masa | from_documents | 3.35 x 1.00 | 90 | verified | one_building.dwg |
| f_L-1_028 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_029 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_030 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_031 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_032 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_033 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_034 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_035 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_036 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_037 | L-1 | r_L-1_salon | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_038 | L-1 | r_L-1_salon_2 | table_dining | masa | from_documents | 3.35 x 1.00 | 90 | verified | one_building.dwg |
| f_L-1_039 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_040 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_041 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_042 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_043 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_044 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_045 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_046 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_047 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1_048 | L-1 | r_L-1_salon_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1_049 | L-1 | r_L-1_salon | armchair | koltuk | from_documents | 0.99 x 0.84 | 180 | verified | one_building.dwg |
| f_L-1_050 | L-1 | r_L-1_salon_2 | armchair | koltuk | from_documents | 0.99 x 0.84 | 180 | verified | one_building.dwg |
| f_L-1_051 | L-1 | r_L-1_banyo | toilet | klozet | from_documents | 0.50 x 0.69 | 180 | verified | one_building.dwg |
| f_L-1_052 | L-1 | r_L-1_banyo_2 | toilet | klozet | from_documents | 0.50 x 0.69 | 180 | verified | one_building.dwg |
| f_L-1_053 | L-1 | r_L-1_salon | sofa_corner | - | from_documents | 4.38 x 1.97 | 270 | verified | one_building.dwg |
| f_L-1_054 | L-1 | r_L-1_salon_2 | sofa_corner | - | from_documents | 4.38 x 1.97 | 90 | verified | one_building.dwg |
| f_L-1_055 | L-1 | r_L-1_banyo_2 | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L-1_056 | L-1 | r_L-1_banyo | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L-1_057 | L-1 | r_L-1_salon_2 | floor_lamp | - | from_documents | 0.59 x 0.59 | 180 | verified | one_building.dwg |
| f_L-1_058 | L-1 | r_L-1_salon_2 | unknown | - | from_documents | 0.79 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1_059 | L-1 | r_L-1_salon | floor_lamp | - | from_documents | 0.59 x 0.59 | 180 | verified | one_building.dwg |
| f_L-1_060 | L-1 | r_L-1_salon | unknown | - | from_documents | 0.79 x 0.79 | 90 | unverified | one_building.dwg |
| f_L-1_061 | L-1 | r_L-1_salon | sofa | - | from_documents | 1.30 x 0.63 | 90 | verified | one_building.dwg |
| f_L-1_062 | L-1 | r_L-1_salon_2 | sofa | - | from_documents | 1.30 x 0.63 | 90 | verified | one_building.dwg |
| f_L-1_063 | L-1 | r_L-1_salon | floor_lamp | - | from_documents | 0.59 x 0.59 | 0 | verified | one_building.dwg |
| f_L-1_064 | L-1 | r_L-1_salon | floor_lamp | - | from_documents | 0.44 x 0.44 | 270 | verified | one_building.dwg |
| f_L-1_065 | L-1 | r_L-1_salon_2 | floor_lamp | - | from_documents | 0.59 x 0.59 | 90 | verified | one_building.dwg |
| f_L-1_066 | L-1 | r_L-1_salon_2 | floor_lamp | - | from_documents | 0.44 x 0.44 | 90 | verified | one_building.dwg |
| f_L-1_067 | L-1 | r_L-1_mutfak | fridge | - | from_documents | 0.79 x 0.50 | 90 | verified | one_building.dwg |
| f_L-1_068 | L-1 | r_L-1_mutfak_2 | fridge | - | from_documents | 0.79 x 0.50 | 270 | verified | one_building.dwg |
| f_L-1_069 | L-1 | r_L-1_salon_2 | unknown | - | from_documents | 0.64 x 0.57 | 270 | unverified | one_building.dwg |
| f_L-1_070 | L-1 | r_L-1_salon | unknown | - | from_documents | 0.64 x 0.57 | 270 | unverified | one_building.dwg |
| f_L-1_071 | L-1 | r_L-1_salon | unknown | - | from_documents | 0.64 x 0.57 | 90 | unverified | one_building.dwg |
| f_L-1_072 | L-1 | r_L-1_salon_2 | unknown | - | from_documents | 0.64 x 0.57 | 90 | unverified | one_building.dwg |
| f_L-1_073 | L-1 | r_L-1_salon | table_coffee | - | from_documents | 0.56 x 0.56 | 270 | verified | one_building.dwg |
| f_L-1_074 | L-1 | r_L-1_salon_2 | table_coffee | - | from_documents | 0.56 x 0.56 | 90 | verified | one_building.dwg |
| f_L-1_075 | L-1 | r_L-1_salon | ottoman | - | from_documents | 0.47 x 0.48 | 90 | verified | one_building.dwg |
| f_L-1_076 | L-1 | r_L-1_salon_2 | ottoman | - | from_documents | 0.47 x 0.48 | 90 | verified | one_building.dwg |
| f_L-1_077 | L-1 | r_L-1_salon | ottoman | - | from_documents | 0.47 x 0.48 | 270 | verified | one_building.dwg |
| f_L-1_078 | L-1 | r_L-1_salon_2 | ottoman | - | from_documents | 0.47 x 0.48 | 270 | verified | one_building.dwg |
| f_L-1_079 | L-1 | r_L-1_salon_2 | ottoman | - | from_documents | 0.40 x 0.40 | 0 | verified | one_building.dwg |
| f_L-1_080 | L-1 | r_L-1_salon | ottoman | - | from_documents | 0.40 x 0.40 | 0 | verified | one_building.dwg |
| f_L-1_081 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.44 x 0.35 | 0 | unverified | one_building.dwg |
| f_L-1_082 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.44 x 0.35 | 0 | unverified | one_building.dwg |
| f_L-1_083 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.44 x 0.35 | 0 | unverified | one_building.dwg |
| f_L-1_084 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.44 x 0.35 | 0 | unverified | one_building.dwg |
| f_L-1_085 | L-1 | r_L-1_mutfak | unknown | - | from_documents | 0.30 x 0.20 | 0 | unverified | one_building.dwg |
| f_L-1_086 | L-1 | r_L-1_mutfak_2 | unknown | - | from_documents | 0.30 x 0.20 | 0 | unverified | one_building.dwg |
| f_L-1_087 | L-1 | r_L-1_salon | unknown | - | from_documents | 0.71 x 0.41 | 144 | unverified | one_building.dwg |
| f_L-1_088 | L-1 | r_L-1_salon_2 | unknown | - | from_documents | 0.71 x 0.41 | 36 | unverified | one_building.dwg |
| f_L-1b_001 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 5.54 x 2.77 | 90 | unverified | one_building.dwg |
| f_L-1b_002 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 5.54 x 2.77 | 90 | unverified | one_building.dwg |
| f_L-1b_003 | L-1b | r_L-1b_acik_mutfak_2 | kitchen_counter | - | from_documents | 3.12 x 0.60 | 0 | verified | one_building.dwg |
| f_L-1b_004 | L-1b | r_L-1b_acik_mutfak_2 | kitchen_counter | - | from_documents | 2.42 x 0.60 | 270 | verified | one_building.dwg |
| f_L-1b_005 | L-1b | r_L-1b_acik_mutfak_2 | kitchen_island | - | from_documents | 1.59 x 0.60 | 0 | verified | one_building.dwg |
| f_L-1b_006 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.62 x 0.60 | 90 | unverified | one_building.dwg |
| f_L-1b_007 | L-1b | r_L-1b_acik_mutfak_2 | stove | ocak_ | from_documents | 0.75 x 0.55 | 0 | verified | one_building.dwg |
| f_L-1b_008 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.51 x 0.11 | 90 | unverified | one_building.dwg |
| f_L-1b_009 | L-1b | r_L-1b_acik_mutfak | kitchen_counter | - | from_documents | 3.12 x 0.60 | 0 | verified | one_building.dwg |
| f_L-1b_010 | L-1b | r_L-1b_acik_mutfak | kitchen_counter | - | from_documents | 2.42 x 0.60 | 90 | verified | one_building.dwg |
| f_L-1b_011 | L-1b | r_L-1b_acik_mutfak | kitchen_island | - | from_documents | 1.59 x 0.60 | 0 | verified | one_building.dwg |
| f_L-1b_012 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.62 x 0.60 | 90 | unverified | one_building.dwg |
| f_L-1b_013 | L-1b | r_L-1b_acik_mutfak | stove | ocak_ | from_documents | 0.75 x 0.55 | 0 | verified | one_building.dwg |
| f_L-1b_014 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.51 x 0.11 | 90 | unverified | one_building.dwg |
| f_L-1b_015 | L-1b | r_L-1b_koridor_2 | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L-1b_016 | L-1b | r_L-1b_koridor | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L-1b_017 | L-1b | r_L-1b_acik_mutfak_2 | table_dining | - | from_documents | 2.30 x 1.00 | 90 | verified | one_building.dwg |
| f_L-1b_018 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1b_019 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1b_020 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1b_021 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1b_022 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1b_023 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1b_024 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 0 | verified | one_building.dwg |
| f_L-1b_025 | L-1b | r_L-1b_acik_mutfak_2 | chair | - | from_documents | 0.50 x 0.45 | 180 | verified | one_building.dwg |
| f_L-1b_026 | L-1b | r_L-1b_acik_mutfak | table_dining | - | from_documents | 2.30 x 1.00 | 90 | verified | one_building.dwg |
| f_L-1b_027 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1b_028 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1b_029 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1b_030 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1b_031 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L-1b_032 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L-1b_033 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 0 | verified | one_building.dwg |
| f_L-1b_034 | L-1b | r_L-1b_acik_mutfak | chair | - | from_documents | 0.50 x 0.45 | 180 | verified | one_building.dwg |
| f_L-1b_035 | L-1b | r_L-1b_banyo_2 | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L-1b_036 | L-1b | r_L-1b_banyo | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L-1b_037 | L-1b | r_L-1b_banyo_2 | toilet | klozet | from_documents | 0.69 x 0.50 | 90 | verified | one_building.dwg |
| f_L-1b_038 | L-1b | r_L-1b_banyo | toilet | klozet | from_documents | 0.69 x 0.50 | 90 | verified | one_building.dwg |
| f_L-1b_039 | L-1b | r_L-1b_acik_mutfak_2 | kitchen_island | - | from_documents | 0.90 x 2.13 | 0 | verified | one_building.dwg |
| f_L-1b_040 | L-1b | r_L-1b_acik_mutfak | kitchen_island | - | from_documents | 0.90 x 2.13 | 0 | unverified | one_building.dwg |
| f_L-1b_041 | L-1b | r_L-1b_banyo_2 | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L-1b_042 | L-1b | r_L-1b_banyo | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L-1b_043 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.82 x 1.64 | 270 | unverified | one_building.dwg |
| f_L-1b_044 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.82 x 1.64 | 270 | unverified | one_building.dwg |
| f_L-1b_045 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.59 x 0.59 | 90 | unverified | one_building.dwg |
| f_L-1b_046 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.79 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1b_047 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.59 x 0.59 | 90 | unverified | one_building.dwg |
| f_L-1b_048 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.79 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1b_049 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.82 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1b_050 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.82 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1b_051 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.82 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1b_052 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.82 x 0.79 | 0 | unverified | one_building.dwg |
| f_L-1b_053 | L-1b | r_L-1b_acik_mutfak_2 | fridge | - | from_documents | 0.79 x 0.50 | 270 | verified | one_building.dwg |
| f_L-1b_054 | L-1b | r_L-1b_acik_mutfak | fridge | - | from_documents | 0.79 x 0.50 | 90 | verified | one_building.dwg |
| f_L-1b_055 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.40 x 0.40 | 90 | unverified | one_building.dwg |
| f_L-1b_056 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.40 x 0.40 | 90 | unverified | one_building.dwg |
| f_L-1b_057 | L-1b | r_L-1b_acik_mutfak_2 | unknown | - | from_documents | 0.44 x 0.35 | 0 | unverified | one_building.dwg |
| f_L-1b_058 | L-1b | r_L-1b_acik_mutfak | unknown | - | from_documents | 0.44 x 0.35 | 0 | unverified | one_building.dwg |
| f_L-1b_059 | L-1b | r_L-1b_acik_mutfak_2 | wall_cabinet | - | from_documents | 0.44 x 0.35 | 0 | verified | one_building.dwg |
| f_L-1b_060 | L-1b | r_L-1b_acik_mutfak | wall_cabinet | - | from_documents | 0.44 x 0.35 | 0 | verified | one_building.dwg |
| f_L0_001 | L0 | r_L0_merdiven | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L0_002 | L0 | r_L0_merdiven_2 | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L0_003 | L0 | r_L0_banyo | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L0_004 | L0 | r_L0_e_banyo_2 | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 0 | verified | one_building.dwg |
| f_L0_005 | L0 | r_L0_banyo_2 | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L0_006 | L0 | r_L0_e_banyo | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 0 | verified | one_building.dwg |
| f_L0_007 | L0 | r_L0_e_yatak_odasi | bed_double | YATAK | from_documents | 2.55 x 2.00 | 270 | verified | one_building.dwg |
| f_L0_008 | L0 | r_L0_e_yatak_odasi_2 | bed_double | YATAK | from_documents | 2.55 x 2.00 | 90 | verified | one_building.dwg |
| f_L0_009 | L0 | r_L0_yatak_odasi_3 | wardrobe | dolappp/fwetwet | from_documents | 1.45 x 0.60 | 180 | verified | one_building.dwg |
| f_L0_010 | L0 | r_L0_yatak_odasi | wardrobe | dolappp/fwetwet | from_documents | 1.45 x 0.60 | 0 | verified | one_building.dwg |
| f_L0_011 | L0 | r_L0_yatak_odasi_4 | wardrobe | dolappp/fwetwet | from_documents | 1.45 x 0.60 | 180 | verified | one_building.dwg |
| f_L0_012 | L0 | r_L0_yatak_odasi_2 | wardrobe | dolappp/fwetwet | from_documents | 1.45 x 0.60 | 0 | verified | one_building.dwg |
| f_L0_013 | L0 | r_L0_e_banyo | shower | duşş | from_documents | 1.40 x 0.60 | 90 | unverified | one_building.dwg |
| f_L0_014 | L0 | r_L0_e_banyo_2 | shower | duşş | from_documents | 1.40 x 0.60 | 90 | unverified | one_building.dwg |
| f_L0_015 | L0 | r_L0_e_banyo | toilet | klozet | from_documents | 0.50 x 0.68 | 0 | verified | one_building.dwg |
| f_L0_016 | L0 | r_L0_e_banyo_2 | toilet | klozet | from_documents | 0.50 x 0.68 | 0 | verified | one_building.dwg |
| f_L0_017 | L0 | r_L0_banyo_2 | toilet | klozet | from_documents | 0.50 x 0.69 | 180 | verified | one_building.dwg |
| f_L0_018 | L0 | r_L0_banyo | toilet | klozet | from_documents | 0.50 x 0.69 | 180 | verified | one_building.dwg |
| f_L0_019 | L0 | r_L0_yatak_odasi | bed_double | - | from_documents | 1.55 x 1.90 | 90 | verified | one_building.dwg |
| f_L0_020 | L0 | r_L0_yatak_odasi_2 | bed_double | - | from_documents | 1.55 x 1.90 | 270 | verified | one_building.dwg |
| f_L0_021 | L0 | r_L0_yatak_odasi_3 | bed_double | - | from_documents | 1.55 x 1.90 | 90 | verified | one_building.dwg |
| f_L0_022 | L0 | r_L0_yatak_odasi_4 | bed_double | - | from_documents | 1.55 x 1.90 | 270 | verified | one_building.dwg |
| f_L0_023 | L0 | r_L0_e_yatak_odasi | wardrobe | - | from_documents | 3.11 x 0.60 | 90 | verified | one_building.dwg |
| f_L0_024 | L0 | r_L0_e_yatak_odasi_2 | wardrobe | - | from_documents | 3.11 x 0.60 | 270 | verified | one_building.dwg |
| f_L0_025 | L0 | r_L0_banyo | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L0_026 | L0 | r_L0_banyo_2 | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L0_027 | L0 | r_L0_yatak_odasi_2 | desk | - | from_documents | 1.45 x 0.91 | 270 | unverified | one_building.dwg |
| f_L0_028 | L0 | r_L0_yatak_odasi_4 | desk | - | from_documents | 1.45 x 0.91 | 270 | unverified | one_building.dwg |
| f_L0_029 | L0 | r_L0_yatak_odasi_3 | desk | - | from_documents | 1.45 x 0.91 | 90 | unverified | one_building.dwg |
| f_L0_030 | L0 | r_L0_yatak_odasi | desk | - | from_documents | 1.45 x 0.91 | 90 | unverified | one_building.dwg |
| f_L0_031 | L0 | r_L0_e_yatak_odasi | floor_lamp | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L0_032 | L0 | r_L0_e_yatak_odasi | floor_lamp | - | from_documents | 0.50 x 0.45 | 270 | verified | one_building.dwg |
| f_L0_033 | L0 | r_L0_e_yatak_odasi_2 | floor_lamp | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L0_034 | L0 | r_L0_e_yatak_odasi_2 | floor_lamp | - | from_documents | 0.50 x 0.45 | 90 | verified | one_building.dwg |
| f_L1_001 | L1 | r_L1_koridor_2 | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L1_002 | L1 | r_L1_koridor | stair | - | from_documents | 2.71 x 2.10 | 0 | verified | one_building.dwg |
| f_L1_003 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | from_documents | 4.49 x 3.02 | 90 | unverified | one_building.dwg |
| f_L1_004 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | from_documents | 4.49 x 3.02 | 90 | unverified | one_building.dwg |
| f_L1_005 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | from_documents | 3.66 x 0.40 | 0 | unverified | one_building.dwg |
| f_L1_006 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | from_documents | 3.66 x 0.40 | 0 | unverified | one_building.dwg |
| f_L1_007 | L1 | r_L1_banyo | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L1_008 | L1 | r_L1_banyo_2 | washbasin | ebeveynlavabo | from_documents | 1.00 x 0.55 | 180 | verified | one_building.dwg |
| f_L1_009 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | sofa | koltuk022/4.5+1-E$0$A$C00F12981 | from_documents | 2.10 x 0.90 | 270 | verified | one_building.dwg |
| f_L1_010 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | sofa | koltuk022/4.5+1-E$0$A$C00F12981 | from_documents | 2.10 x 0.90 | 90 | verified | one_building.dwg |
| f_L1_011 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | sofa | koltuk011/4.5+1-E$0$A$C00F12981 | from_documents | 2.10 x 0.90 | 180 | verified | one_building.dwg |
| f_L1_012 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | sofa | koltuk011/4.5+1-E$0$A$C00F12981 | from_documents | 2.10 x 0.90 | 180 | verified | one_building.dwg |
| f_L1_013 | L1 | r_L1_banyo | toilet | klozet | from_documents | 0.69 x 0.50 | 90 | verified | one_building.dwg |
| f_L1_014 | L1 | r_L1_banyo_2 | toilet | klozet | from_documents | 0.69 x 0.50 | 90 | verified | one_building.dwg |
| f_L1_015 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | from_documents | 1.03 x 0.69 | 79 | unverified | one_building.dwg |
| f_L1_016 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | from_documents | 1.03 x 0.69 | 101 | unverified | one_building.dwg |
| f_L1_017 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | from_documents | 1.63 x 1.52 | 90 | unverified | one_building.dwg |
| f_L1_018 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | from_documents | 1.63 x 1.52 | 90 | unverified | one_building.dwg |
| f_L1_019 | L1 | r_L1_banyo | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L1_020 | L1 | r_L1_banyo_2 | bathtub | - | from_documents | 1.83 x 0.80 | 90 | verified | one_building.dwg |
| f_L1_021 | L1 | r_L1_koridor | bench | - | from_documents | 0.60 x 1.52 | 90 | unverified | one_building.dwg |
| f_L1_022 | L1 | r_L1_koridor_2 | bench | - | from_documents | 0.60 x 1.52 | 270 | verified | one_building.dwg |
| f_L1_023 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | from_documents | 0.68 x 0.78 | 180 | unverified | one_building.dwg |
| f_L1_024 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | from_documents | 0.68 x 0.78 | 180 | unverified | one_building.dwg |
| f_L1_025 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | from_documents | 0.68 x 0.78 | 180 | unverified | one_building.dwg |
| f_L1_026 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | from_documents | 0.68 x 0.78 | 180 | unverified | one_building.dwg |
| f_L1_027 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi | ottoman | - | from_documents | 0.40 x 0.40 | 90 | unverified | one_building.dwg |
| f_L1_028 | L1 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ottoman | - | from_documents | 0.40 x 0.40 | 90 | unverified | one_building.dwg |

## Inferred (Milestone 11)

Pieces whose type, front or role the documents left unclear; inferred by code (the agent may change them on the plan crop).

| Piece | Room | Type | Front | Built | Reason |
|---|---|---|---|---|---|
| f_L-1_051 | r_L-1_banyo | toilet | 90 | yes | front of f_L-1_052, its mirror twin in r_L-1_banyo_2 (U16) |
| f_L-1_081 | r_L-1_mutfak | unknown | - | no | drawn inside kitchen_counter f_L-1_003 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L-1_082 | r_L-1_mutfak_2 | unknown | - | no | drawn inside kitchen_counter f_L-1_012 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L-1_083 | r_L-1_mutfak | unknown | - | no | drawn inside kitchen_counter f_L-1_003 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L-1_084 | r_L-1_mutfak_2 | unknown | - | no | drawn inside kitchen_counter f_L-1_012 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L-1_086 | r_L-1_mutfak_2 | unknown | - | no | drawn inside kitchen_counter f_L-1_010 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L-1b_001 | r_L-1b_acik_mutfak_2 | unknown | - | no | outline 5.54 x 2.77 m around 3 other piece(s) (f_L-1b_043, f_L-1b_051, f_L-1b_052): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L-1b_002 | r_L-1b_acik_mutfak | unknown | - | no | outline 5.54 x 2.77 m around 3 other piece(s) (f_L-1b_044, f_L-1b_049, f_L-1b_050): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L-1b_040 | r_L-1b_acik_mutfak | kitchen_island | 270 | yes | type and front of f_L-1b_039, its mirror twin in r_L-1b_acik_mutfak_2 (U16) |
| f_L-1b_057 | r_L-1b_acik_mutfak_2 | unknown | - | no | drawn inside kitchen_counter f_L-1b_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L-1b_058 | r_L-1b_acik_mutfak | unknown | - | no | drawn inside kitchen_counter f_L-1b_010 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built) |
| f_L0_016 | r_L0_e_banyo_2 | toilet | 270 | yes | front of f_L0_015, its mirror twin in r_L0_e_banyo (U16) |
| f_L0_017 | r_L0_banyo_2 | toilet | 90 | yes | front of f_L0_018, its mirror twin in r_L0_banyo (U16) |
| f_L0_027 | r_L0_yatak_odasi_2 | desk | 180 | yes | desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here |
| f_L0_028 | r_L0_yatak_odasi_4 | desk | 180 | yes | desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here |
| f_L0_029 | r_L0_yatak_odasi_3 | desk | 0 | yes | desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here |
| f_L0_030 | r_L0_yatak_odasi | desk | 0 | yes | desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here |
| f_L1_003 | r_L1_oyun_aktivite_ve_dinlenme_odasi | unknown | - | no | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_012, f_L1_015): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_004 | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | unknown | - | no | outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_011, f_L1_016): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups) |
| f_L1_021 | r_L1_koridor | bench | 0 | yes | type and front of f_L1_022, its mirror twin in r_L1_koridor_2 (U16) |

## Building (sheets)

| Level | Kind | Variant | Region | Elevation | Source | Ceiling | Source |
|---|---|---|---|---|---|---|---|
| L-1 | basement | base | r2 | -3.00 | section | 2.85 | section |
| L-1b | basement | Açık mutfak | r3 | -3.00 | section | 2.85 | section |
| L0 | floor | base | r4 | 0.00 | section | 3.00 | section |
| L1 | attic | base | r5 | 3.15 | section | 3.43 | section |

Levels left out (failed_levels: leave_out):

- none

| Variant | Label | Levels | Rooms changed | Exterior changed |
|---|---|---|---|---|
| base | Base | L-1, L0, L1 | - | False |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r_L-1b_acik_mutfak, r_L-1b_acik_mutfak_2, r_L-1b_oda, r_L-1b_oda_2, r_L-1b_koridor, r_L-1b_koridor_2 | True |

| Slab | Top z | Thickness | Source | Stair voids |
|---|---|---|---|---|
| sl_L-1 | -3.00 | 0.15 | section | 0 |
| sl_L0 | 0.00 | 0.15 | section | 2 |
| sl_L1 | 3.15 | 0.15 | section | 2 |

Roof: **mansard** (plan_roof_lines); eaves 3.65 m, ridge 6.79 m, pitches 40.40, 13.30 deg, overhang 0.50 m, thickness 0.20 m; assumed: none

Facade (drawn faces only; every other look is resolved by the build):

- none drawn

Site: plot not drawn; 0 paving, 0 grass, 0 parking surfaces; 0 labels; north unknown

## Units

Project unit system: **metric**

| Document | Unit system | Source kind |
|---|---|---|
| one_building.dwg | metric | dxf |

## Scale

**one_building.dwg**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- one_building.dwg p1: drawing units known (0.01 m per unit)

**one_building.dwg**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- one_building.dwg p1: drawing units known (0.01 m per unit)

**one_building.dwg**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- one_building.dwg p1: drawing units known (0.01 m per unit)

**one_building.dwg**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- one_building.dwg p1: drawing units known (0.01 m per unit)

## Room size labels

None.

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sd_L0_001 | decor (other) | 0,64 m x 0,64 m |
| sd_L0_002 | decor (other) | 0,64 m x 0,64 m |
| sd_L0_003 | decor (other) | 0,64 m x 0,64 m |
| sd_L0_004 | decor (other) | 0,64 m x 0,64 m |
| sd_L0_005 | decor (other) | 0,56 m x 0,56 m |
| sd_L0_006 | decor (other) | 0,56 m x 0,56 m |

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| one_building.dwg | end_to_end | 3,12 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 3,12 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 4,17 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 4,17 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 7,39 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 7,39 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 8,54 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 11,75 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 11,76 m | no | longer than 2.4 m |
| one_building.dwg | end_to_end | 14,97 m | no | longer than 2.4 m |
| one_building.dwg | end_to_face | 1,38 m | yes | two room names shared one face |
| one_building.dwg | end_to_face | 1,38 m | yes | two room names shared one face |
| one_building.dwg | end_to_wall | 1,30 m | yes | two room names shared one face |
| one_building.dwg | end_to_wall | 1,30 m | yes | two room names shared one face |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| one_building.dwg | run | door | 0,82 m | INSERT:2DDF6/0, INSERT:2DDF6/1, LWPOLYLINE:2DE0A, LWPOLYLINE:2DE0B |
| one_building.dwg | run | door | 0,82 m | INSERT:2DDF1/0, INSERT:2DDF1/1, LWPOLYLINE:2DDF4, LWPOLYLINE:2DDF5 |
| one_building.dwg | run | door | 0,82 m | INSERT:2E199/0, INSERT:2E199/1, LWPOLYLINE:2E19C, LWPOLYLINE:2E19D |
| one_building.dwg | run | door | 0,82 m | INSERT:2E19E/0, INSERT:2E19E/1, LWPOLYLINE:2E1B2, LWPOLYLINE:2E1B3 |
| one_building.dwg | split | open | 1,30 m | - |
| one_building.dwg | split | open | 2,67 m | - |
| one_building.dwg | split | open | 2,67 m | - |
| one_building.dwg | split | open | 1,30 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:2DDF8/0, INSERT:2DDF8/1, LWPOLYLINE:2DE08, LWPOLYLINE:2DE09 |
| one_building.dwg | run | door | 0,78 m | INSERT:2DDE5/0, INSERT:2DDE5/1, LWPOLYLINE:2DE06, LWPOLYLINE:2DE07 |
| one_building.dwg | run | unclassified | 2,14 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:2DDDE/0, INSERT:2DDDE/1 |
| one_building.dwg | run | unclassified | 2,14 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:2E186/0, INSERT:2E186/1 |
| one_building.dwg | run | door | 0,82 m | INSERT:2E1A0/0, INSERT:2E1A0/1, LWPOLYLINE:2E1B0, LWPOLYLINE:2E1B1 |
| one_building.dwg | run | door | 0,78 m | INSERT:2E18D/0, INSERT:2E18D/1, LWPOLYLINE:2E1AE, LWPOLYLINE:2E1AF |
| one_building.dwg | continuous | door | 0,82 m | - |
| one_building.dwg | continuous | door | 0,82 m | - |
| one_building.dwg | continuous | window | 2,68 m | - |
| one_building.dwg | continuous | window | 2,17 m | - |
| one_building.dwg | continuous | window | 2,17 m | - |
| one_building.dwg | continuous | window | 2,68 m | - |
| one_building.dwg | split | open | 4,14 m | - |
| one_building.dwg | split | open | 4,14 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:365DF/0, INSERT:365DF/1 |
| one_building.dwg | run | door | 0,82 m | INSERT:36A49/0, INSERT:36A49/1 |
| one_building.dwg | end | closed | 0,23 m | - |
| one_building.dwg | end | closed | 0,22 m | - |
| one_building.dwg | end | door | 0,82 m | INSERT:365E2/0, INSERT:365E2/1 |
| one_building.dwg | end | door | 0,82 m | INSERT:36A4C/0, INSERT:36A4C/1 |
| one_building.dwg | continuous | window | 7,19 m | - |
| one_building.dwg | continuous | window | 7,19 m | - |
| one_building.dwg | continuous | window | 4,16 m | - |
| one_building.dwg | continuous | window | 4,16 m | - |
| one_building.dwg | split | open | 4,07 m | - |
| one_building.dwg | split | open | 4,07 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:2F028/0, INSERT:2F028/1, LWPOLYLINE:2F033 |
| one_building.dwg | run | door | 0,82 m | INSERT:2F023/0, INSERT:2F023/1 |
| one_building.dwg | run | door | 0,82 m | INSERT:2C7F4/0, INSERT:2C7F4/1 |
| one_building.dwg | run | door | 0,82 m | INSERT:2C7F9/0, INSERT:2C7F9/1, LWPOLYLINE:2C804 |
| one_building.dwg | end | empty | 1,30 m | - |
| one_building.dwg | end | empty | 1,30 m | - |
| one_building.dwg | continuous | window | 7,19 m | - |
| one_building.dwg | continuous | window | 7,19 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:36D77/0, INSERT:36D77/1, LWPOLYLINE:36D78, LWPOLYLINE:36D7A |
| one_building.dwg | run | empty | 0,40 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:37B29/0, INSERT:37B29/1, LWPOLYLINE:37B2A, LWPOLYLINE:37B2B |
| one_building.dwg | split | open | 1,30 m | - |
| one_building.dwg | split | open | 2,67 m | - |
| one_building.dwg | split | open | 2,67 m | - |
| one_building.dwg | split | open | 1,30 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:3749F/0, INSERT:3749F/1 |
| one_building.dwg | run | door | 0,82 m | INSERT:2F799/0, INSERT:2F799/1 |
| one_building.dwg | run | closed | 0,10 m | - |
| one_building.dwg | run | door | 0,82 m | INSERT:37A7D/0, INSERT:37A7D/1 |
| one_building.dwg | run | door | 0,82 m | INSERT:37B34/0, INSERT:37B34/1 |
| one_building.dwg | continuous | window | 2,00 m | - |
| one_building.dwg | continuous | window | 2,00 m | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L-1_001 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_002 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_003 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_004 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_005 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1_006 | unknown | none (part of a kitchen counter cluster (M11 split): not asked, the agent types it) | - | yes | unverified |
| f_L-1_007 | unknown | none (part of a kitchen counter cluster (M11 split): not asked, the agent types it) | - | yes | unverified |
| f_L-1_008 | stove | block_name (stove block ocak_ on a counter leg: the leg's front (M11 split)) | - | yes | verified |
| f_L-1_009 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1_010 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_011 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_012 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_013 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1_014 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1_015 | unknown | none (part of a kitchen counter cluster (M11 split): not asked, the agent types it) | - | yes | unverified |
| f_L-1_016 | unknown | none (part of a kitchen counter cluster (M11 split): not asked, the agent types it) | - | yes | unverified |
| f_L-1_017 | stove | block_name (stove block ocak_ on a counter leg: the leg's front (M11 split)) | - | yes | verified |
| f_L-1_018 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1_019 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L-1_020 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L-1_021 | unknown | none (cluster larger than 4.5 m on a side) | - | yes | unverified |
| f_L-1_022 | unknown | none (cluster larger than 4.5 m on a side) | - | yes | unverified |
| f_L-1_023 | wardrobe | block_name (front 270 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L-1_024 | wardrobe | block_name (front 270 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L-1_025 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L-1_026 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L-1_027 | table_dining | block_name (block masa (1.57 x 3.35 m) holds a table and 10 chairs: split (M11)) | - | yes | verified |
| f_L-1_028 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_029 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_030 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_031 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_032 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_033 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_034 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_035 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_036 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_037 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_038 | table_dining | block_name (block masa (1.57 x 3.35 m) holds a table and 10 chairs: split (M11)) | - | yes | verified |
| f_L-1_039 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_040 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_041 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_042 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_043 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_044 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_045 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_046 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_047 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_048 | chair | rule (chair of block masa, facing the table (M11 split)) | - | yes | verified |
| f_L-1_049 | armchair | block_name (front 90 deg: head = side with >= 2 small closed shapes; block koltuk holds 2 drawn pieces: the 0.84 x 0.99 m piece takes the name, the others are asked) | - | yes | verified |
| f_L-1_050 | armchair | block_name (front 90 deg: head = side with >= 2 small closed shapes; block koltuk holds 2 drawn pieces: the 0.99 x 0.84 m piece takes the name, the others are asked) | - | yes | verified |
| f_L-1_051 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L-1_052 | toilet | block_name (front 90 deg: only side within 0.25 m of a wall is the back; 2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L-1_053 | sofa_corner | ai_two_pass (L outline 4.38 x 1.97 m: main seat 0.75 m deep, chaise 0.76 x 1.97 m on the right (seen from the front), open corner 1.22 x 3.62 m) | pass 1: sofa_corner; pass 2: sofa_corner | yes | verified |
| f_L-1_054 | sofa_corner | ai_two_pass (L outline 4.38 x 1.97 m: main seat 0.75 m deep, chaise 0.76 x 1.97 m on the left (seen from the front), open corner 1.22 x 3.62 m) | pass 1: sofa_corner; pass 2: sofa_corner | yes | verified |
| f_L-1_055 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L-1_056 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L-1_057 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L-1_058 | unknown | none | pass 1: table_coffee; pass 2: potted_plant | yes | unverified |
| f_L-1_059 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L-1_060 | unknown | none | pass 1: table_coffee; pass 2: potted_plant | yes | unverified |
| f_L-1_061 | sofa | ai_two_pass | pass 1: sofa; pass 2: sofa | yes | verified |
| f_L-1_062 | sofa | ai_two_pass | pass 1: sofa; pass 2: sofa | yes | verified |
| f_L-1_063 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L-1_064 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L-1_065 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L-1_066 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L-1_067 | fridge | ai_two_pass | pass 1: fridge; pass 2: fridge | yes | verified |
| f_L-1_068 | fridge | ai_two_pass | pass 1: fridge; pass 2: fridge | yes | verified |
| f_L-1_069 | unknown | none | pass 1: table_coffee; pass 2: armchair | yes | unverified |
| f_L-1_070 | unknown | none | pass 1: table_coffee; pass 2: armchair | yes | unverified |
| f_L-1_071 | unknown | none | pass 1: ottoman; pass 2: armchair | yes | unverified |
| f_L-1_072 | unknown | none | pass 1: table_coffee; pass 2: armchair | yes | unverified |
| f_L-1_073 | table_coffee | ai_two_pass | pass 1: table_coffee; pass 2: table_coffee | yes | verified |
| f_L-1_074 | table_coffee | ai_two_pass | pass 1: table_coffee; pass 2: table_coffee | yes | verified |
| f_L-1_075 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | verified |
| f_L-1_076 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | verified |
| f_L-1_077 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | verified |
| f_L-1_078 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | verified |
| f_L-1_079 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | verified |
| f_L-1_080 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | verified |
| f_L-1_081 | unknown | none | pass 1: bar_stool; pass 2: sink_kitchen | no (drawn symbol, not built) | unverified |
| f_L-1_082 | unknown | none | pass 1: bar_stool; pass 2: sink_kitchen | no (drawn symbol, not built) | unverified |
| f_L-1_083 | unknown | none | pass 1: bar_stool; pass 2: wall_cabinet | no (drawn symbol, not built) | unverified |
| f_L-1_084 | unknown | none | pass 1: bar_stool; pass 2: sink_kitchen | no (drawn symbol, not built) | unverified |
| f_L-1_085 | unknown | none | pass 1: not_furniture; pass 2: not_furniture | no (drawn symbol, not built) | unverified |
| f_L-1_086 | unknown | none | pass 1: not_furniture; pass 2: unknown | no (drawn symbol, not built) | unverified |
| f_L-1_087 | unknown | none (drawn inside block koltuk next to its named piece; type asked) | pass 1: ottoman; pass 2: table_coffee | yes | unverified |
| f_L-1_088 | unknown | none (drawn inside block koltuk next to its named piece; type asked) | pass 1: ottoman; pass 2: table_coffee | yes | unverified |
| f_L-1b_001 | unknown | none (cluster larger than 4.5 m on a side) | - | no (drawn symbol, not built) | unverified |
| f_L-1b_002 | unknown | none (cluster larger than 4.5 m on a side) | - | no (drawn symbol, not built) | unverified |
| f_L-1b_003 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1b_004 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1b_005 | kitchen_island | rule (free block of a kitchen counter outline (peninsula or island, M11 split)) | - | yes | verified |
| f_L-1b_006 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1b_007 | stove | block_name (stove block ocak_ on a counter leg: the leg's front (M11 split)) | - | yes | verified |
| f_L-1b_008 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1b_009 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1b_010 | kitchen_counter | rule (kitchen counter run drawn as a closed outline along the walls (M11 split)) | - | yes | verified |
| f_L-1b_011 | kitchen_island | rule (free block of a kitchen counter outline (peninsula or island, M11 split)) | - | yes | verified |
| f_L-1b_012 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1b_013 | stove | block_name (stove block ocak_ on a counter leg: the leg's front (M11 split)) | - | yes | verified |
| f_L-1b_014 | unknown | none (detail inside a kitchen counter leg (an appliance front or drawers, M11 split): not built) | - | no (drawn symbol, not built) | unverified |
| f_L-1b_015 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L-1b_016 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L-1b_017 | table_dining | rule (table + 8 chairs drawn as one group: split (M11)) | - | yes | verified |
| f_L-1b_018 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_019 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_020 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_021 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_022 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_023 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_024 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_025 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_026 | table_dining | rule (table + 8 chairs drawn as one group: split (M11)) | - | yes | verified |
| f_L-1b_027 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_028 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_029 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_030 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_031 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_032 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_033 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_034 | chair | rule (chair of the drawn table + chairs group, facing the table (M11 split)) | - | yes | verified |
| f_L-1b_035 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L-1b_036 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L-1b_037 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L-1b_038 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L-1b_039 | kitchen_island | ai_two_pass | pass 1: kitchen_island; pass 2: kitchen_island | yes | verified |
| f_L-1b_040 | kitchen_island | none | pass 1: kitchen_island; pass 2: sofa | yes | unverified |
| f_L-1b_041 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L-1b_042 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L-1b_043 | unknown | none | pass 1: kitchen_island; pass 2: sofa | yes | unverified |
| f_L-1b_044 | unknown | none | pass 1: kitchen_island; pass 2: sofa | yes | unverified |
| f_L-1b_045 | unknown | none | pass 1: floor_lamp; pass 2: potted_plant | yes | unverified |
| f_L-1b_046 | unknown | none | pass 1: kitchen_counter; pass 2: potted_plant | yes | unverified |
| f_L-1b_047 | unknown | none | pass 1: floor_lamp; pass 2: potted_plant | yes | unverified |
| f_L-1b_048 | unknown | none | pass 1: kitchen_counter; pass 2: potted_plant | yes | unverified |
| f_L-1b_049 | unknown | none | pass 1: kitchen_counter; pass 2: armchair | yes | unverified |
| f_L-1b_050 | unknown | none | pass 1: kitchen_counter; pass 2: armchair | yes | unverified |
| f_L-1b_051 | unknown | none | pass 1: kitchen_counter; pass 2: armchair | yes | unverified |
| f_L-1b_052 | unknown | none | pass 1: kitchen_counter; pass 2: armchair | yes | unverified |
| f_L-1b_053 | fridge | ai_two_pass | pass 1: fridge; pass 2: fridge | yes | verified |
| f_L-1b_054 | fridge | ai_two_pass | pass 1: fridge; pass 2: fridge | yes | verified |
| f_L-1b_055 | unknown | none | pass 1: bar_stool; pass 2: chair | yes | unverified |
| f_L-1b_056 | unknown | none | pass 1: bar_stool; pass 2: chair | yes | unverified |
| f_L-1b_057 | unknown | none | pass 1: bar_stool; pass 2: sink_kitchen | no (drawn symbol, not built) | unverified |
| f_L-1b_058 | unknown | none | pass 1: bar_stool; pass 2: sink_kitchen | no (drawn symbol, not built) | unverified |
| f_L-1b_059 | wall_cabinet | ai_two_pass | pass 1: wall_cabinet; pass 2: wall_cabinet | yes | verified |
| f_L-1b_060 | wall_cabinet | ai_two_pass | pass 1: wall_cabinet; pass 2: wall_cabinet | yes | verified |
| f_L0_001 | stair | rule (stair rule: 2 flight(s), 6, 5 tread lines) | - | yes | verified |
| f_L0_002 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L0_003 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_004 | washbasin | block_name (front 270 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_005 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_006 | washbasin | block_name (front 270 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_007 | bed_double | block_name (front 180 deg: only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes; block YATAK (2.00 x 2.68 m) holds 3 drawn pieces: the 2.00 x 2.55 m piece takes the name, the others are asked) | - | yes | verified |
| f_L0_008 | bed_double | block_name (front 0 deg: only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes; block YATAK (2.00 x 2.68 m) holds 3 drawn pieces: the 2.00 x 2.55 m piece takes the name, the others are asked) | - | yes | verified |
| f_L0_009 | wardrobe | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_010 | wardrobe | block_name (front 270 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_011 | wardrobe | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_012 | wardrobe | block_name (front 270 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L0_013 | shower | block_name (block name says shower but 0.60 x 1.40 m does not fit its size range) | - | yes | unverified |
| f_L0_014 | shower | block_name (block name says shower but 0.60 x 1.40 m does not fit its size range) | - | yes | unverified |
| f_L0_015 | toilet | block_name (front 270 deg: only side within 0.25 m of a wall is the back; 2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L0_016 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L0_017 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L0_018 | toilet | block_name (front 90 deg: only side within 0.25 m of a wall is the back; 2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L0_019 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_020 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_021 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_022 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_023 | wardrobe | ai_two_pass | pass 1: wardrobe; pass 2: wardrobe | yes | verified |
| f_L0_024 | wardrobe | ai_two_pass | pass 1: wardrobe; pass 2: wardrobe | yes | verified |
| f_L0_025 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L0_026 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L0_027 | desk | none | pass 1: desk; pass 2: sofa | yes | unverified |
| f_L0_028 | desk | none | pass 1: desk; pass 2: sofa | yes | unverified |
| f_L0_029 | desk | none | pass 1: desk; pass 2: sofa | yes | unverified |
| f_L0_030 | desk | none | pass 1: unknown; pass 2: sofa | yes | unverified |
| f_L0_031 | floor_lamp | ai_two_pass (drawn inside block YATAK next to its named piece; type asked) | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L0_032 | floor_lamp | ai_two_pass (drawn inside block YATAK next to its named piece; type asked) | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L0_033 | floor_lamp | ai_two_pass (drawn inside block YATAK next to its named piece; type asked) | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L0_034 | floor_lamp | ai_two_pass (drawn inside block YATAK next to its named piece; type asked) | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L1_001 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L1_002 | stair | rule (stair rule: 2 flight(s), 6, 6 tread lines) | - | yes | verified |
| f_L1_003 | unknown | none (fits no size-table type) | - | no (drawn symbol, not built) | unverified |
| f_L1_004 | unknown | none (fits no size-table type) | - | no (drawn symbol, not built) | unverified |
| f_L1_005 | unknown | none (fits no size-table type) | - | yes | unverified |
| f_L1_006 | unknown | none (fits no size-table type) | - | yes | unverified |
| f_L1_007 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L1_008 | washbasin | block_name (front 90 deg: corner: the long side against a wall is the back) | - | yes | verified |
| f_L1_009 | sofa | block_name (front 180 deg: head = side with >= 2 small closed shapes) | - | yes | verified |
| f_L1_010 | sofa | block_name (front 0 deg: head = side with >= 2 small closed shapes) | - | yes | verified |
| f_L1_011 | sofa | block_name (front 90 deg: head = side with >= 2 small closed shapes) | - | yes | verified |
| f_L1_012 | sofa | block_name (front 90 deg: head = side with >= 2 small closed shapes) | - | yes | verified |
| f_L1_013 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L1_014 | toilet | block_name (2 drawn parts of one block instance are one piece) | - | yes | verified |
| f_L1_015 | unknown | none | pass 1: unknown; pass 2: potted_plant | yes | unverified |
| f_L1_016 | unknown | none | pass 1: unknown; pass 2: potted_plant | yes | unverified |
| f_L1_017 | unknown | none | pass 1: unknown; pass 2: not_furniture | yes | unverified |
| f_L1_018 | unknown | none | pass 1: unknown; pass 2: not_furniture | yes | unverified |
| f_L1_019 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L1_020 | bathtub | ai_two_pass | pass 1: bathtub; pass 2: bathtub | yes | verified |
| f_L1_021 | bench | none | pass 1: unknown; pass 2: bench | yes | unverified |
| f_L1_022 | bench | ai_two_pass | pass 1: bench; pass 2: bench | yes | verified |
| f_L1_023 | unknown | none | pass 1: ottoman; pass 2: armchair | yes | unverified |
| f_L1_024 | unknown | none | pass 1: table_coffee; pass 2: armchair | yes | unverified |
| f_L1_025 | unknown | none | pass 1: table_coffee; pass 2: armchair | yes | unverified |
| f_L1_026 | unknown | none | pass 1: table_coffee; pass 2: armchair | yes | unverified |
| f_L1_027 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | unverified |
| f_L1_028 | ottoman | ai_two_pass | pass 1: ottoman; pass 2: ottoman | yes | unverified |

Recognition questions: 88 (`recognition/requests.json`), 0 without a complete pair of answers.

## Assumed values

- L-1: ceiling height 2.85 m (section)
- L-1b: ceiling height 2.85 m (section)
- L0: ceiling height 3.00 m (section)
- L1: ceiling height 3.43 m (section)
- d_L-1_001 (door): height 2,10 m
- d_L-1_002 (door): height 2,10 m
- d_L-1_003 (door): height 2,10 m
- d_L-1_004 (door): height 2,10 m
- win_L-1_001 (window): height 1,20 m
- win_L-1_001 (window): sill height 0,90 m
- win_L-1_002 (window): height 1,20 m
- win_L-1_002 (window): sill height 0,90 m
- win_L-1_003 (window): height 1,20 m
- win_L-1_003 (window): sill height 0,90 m
- win_L-1_004 (window): height 1,20 m
- win_L-1_004 (window): sill height 0,90 m
- d_L-1b_001 (door): height 2,10 m
- d_L-1b_002 (door): height 2,10 m
- d_L-1b_003 (door): height 2,10 m
- d_L-1b_004 (door): height 2,10 m
- win_L-1b_001 (window): height 1,20 m
- win_L-1b_001 (window): sill height 0,90 m
- win_L-1b_002 (window): height 1,20 m
- win_L-1b_002 (window): sill height 0,90 m
- d_L0_001 (door): height 2,10 m
- d_L0_002 (door): height 2,10 m
- d_L0_003 (door): height 2,10 m
- d_L0_004 (door): height 2,10 m
- d_L0_005 (door): height 2,10 m
- d_L0_006 (door): height 2,10 m
- o_L0_001 (opening): height 2,10 m
- d_L0_007 (door): height 2,10 m
- o_L0_002 (opening): height 2,10 m
- d_L0_008 (door): height 2,10 m
- d_L0_009 (door): height 2,10 m
- d_L0_010 (door): height 2,10 m
- d_L0_011 (door): height 2,10 m
- d_L0_012 (door): height 2,10 m
- win_L0_001 (window): height 1,20 m
- win_L0_001 (window): sill height 0,90 m
- win_L0_002 (window): height 1,20 m
- win_L0_002 (window): sill height 0,90 m
- win_L0_003 (window): height 1,20 m
- win_L0_003 (window): sill height 0,90 m
- win_L0_004 (window): height 1,20 m
- win_L0_004 (window): sill height 0,90 m
- d_L1_001 (door): height 2,10 m
- o_L1_001 (opening): height 2,10 m
- d_L1_002 (door): height 2,10 m
- d_L1_003 (door): height 2,10 m
- d_L1_004 (door): height 2,10 m
- d_L1_005 (door): height 2,10 m
- d_L1_006 (door): height 2,10 m
- win_L1_001 (window): height 1,20 m
- win_L1_001 (window): sill height 0,90 m
- win_L1_002 (window): height 1,20 m
- win_L1_002 (window): sill height 0,90 m
- f_L-1_019 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1_020 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1_057 (floor_lamp): front 90 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_059 (floor_lamp): front 90 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_064 (floor_lamp): front 180 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_066 (floor_lamp): front 0 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_073 (table_coffee): front 180 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_074 (table_coffee): front 0 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_079 (ottoman): front 270 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1_080 (ottoman): front 270 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L-1b_015 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L-1b_016 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L0_023 (wardrobe): front 0 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L0_024 (wardrobe): front 180 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L0_031 (floor_lamp): front 180 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L0_032 (floor_lamp): front 180 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L0_033 (floor_lamp): front 0 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L0_034 (floor_lamp): front 0 deg assumed (the drawn front kept; both AI passes answered 'none')
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)
- f_L1_002 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)

## Notes

### one_building.dwg

- furniture size checks use the wenart/recognition/size_table.yaml
- 351 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- stair at (7238.27, 44907.71): 2 flight(s) of 0.950, 0.950 m
- stair at (7241.33, 44907.71): 2 flight(s) of 0.950, 0.950 m
- block YATAK (2.00 x 2.68 m) holds 3 drawn pieces: the 2.00 x 2.55 m piece takes the name, the others are asked
- block YATAK (2.00 x 2.68 m) holds 3 drawn pieces: the 2.00 x 2.55 m piece takes the name, the others are asked
- klozet at (7238.38, 44906.18): 2 drawn parts of one block instance are one piece
- klozet at (7241.22, 44906.18): 2 drawn parts of one block instance are one piece
- klozet at (7241.33, 44909.34): 2 drawn parts of one block instance are one piece
- klozet at (7238.26, 44909.34): 2 drawn parts of one block instance are one piece
- 2 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: INSERT:2DDEC/1,INSERT:2E194/1
- 2 site edge or boundary line groups outside the building (not decor)

### one_building.dwg

- furniture size checks use the wenart/recognition/size_table.yaml
- 150 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- kitchen counter cluster split (M11): 4 counter legs, 0 free blocks, 5 other parts
- kitchen counter cluster split (M11): 4 counter legs, 0 free blocks, 5 other parts
- stair at (7259.69, 44923.45): 2 flight(s) of 0.950, 0.950 m
- stair at (7262.74, 44923.45): 2 flight(s) of 0.950, 0.950 m
- cluster 0.60 x 5.54 m at (7254.13, 44919.08) larger than 4.5 m: unknown, unverified, not asked
- cluster 0.60 x 5.54 m at (7268.30, 44919.08) larger than 4.5 m: unknown, unverified, not asked
- block masa (1.57 x 3.35 m) holds a table and 10 chairs: split (M11)
- block masa (1.57 x 3.35 m) holds a table and 10 chairs: split (M11)
- block koltuk holds 2 drawn pieces: the 0.84 x 0.99 m piece takes the name, the others are asked
- block koltuk holds 2 drawn pieces: the 0.99 x 0.84 m piece takes the name, the others are asked
- klozet at (7259.68, 44925.07): 2 drawn parts of one block instance are one piece
- klozet at (7262.75, 44925.07): 2 drawn parts of one block instance are one piece
- 2 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: LWPOLYLINE:3660A,LWPOLYLINE:36A74

### one_building.dwg

- furniture size checks use the wenart/recognition/size_table.yaml
- 130 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- cluster 2.77 x 5.54 m at (7262.80, 44903.93) larger than 4.5 m: unknown, unverified, not asked
- cluster 2.77 x 5.54 m at (7259.63, 44903.93) larger than 4.5 m: unknown, unverified, not asked
- kitchen counter cluster split (M11): 2 counter legs, 1 free blocks, 3 other parts
- kitchen counter cluster split (M11): 2 counter legs, 1 free blocks, 3 other parts
- stair at (7262.74, 44907.90): 2 flight(s) of 0.950, 0.950 m
- stair at (7259.69, 44907.90): 2 flight(s) of 0.950, 0.950 m
- klozet at (7262.75, 44909.53): 2 drawn parts of one block instance are one piece
- klozet at (7259.68, 44909.53): 2 drawn parts of one block instance are one piece
- table + 8 chairs at (7267.06, 44901.66) split (M11)
- table + 8 chairs at (7255.37, 44901.66) split (M11)

### one_building.dwg

- furniture size checks use the wenart/recognition/size_table.yaml
- 113 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 6 sides of outlines larger than 4.5 m both ways are no furniture: LWPOLYLINE:2F87A,LWPOLYLINE:304CA
- stair at (7250.69, 44887.30): 2 flight(s) of 0.950, 0.950 m
- stair at (7247.63, 44887.30): 2 flight(s) of 0.950, 0.950 m
- klozet at (7247.62, 44888.92): 2 drawn parts of one block instance are one piece
- klozet at (7250.69, 44888.92): 2 drawn parts of one block instance are one piece
- unknown piece 3.02 x 4.49 m at (7247.45, 44882.92): fits no size-table type
- unknown piece 3.02 x 4.49 m at (7250.87, 44882.92): fits no size-table type
- unknown piece 3.66 x 0.40 m at (7246.93, 44885.90): fits no size-table type
- unknown piece 3.66 x 0.40 m at (7251.39, 44885.90): fits no size-table type
- 4 drawn details smaller than 0.2 m ignored

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L-1_salon | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_002 | area_label_vs_computed | r_L-1_salon_2 | Label says 49,00 m², polygon gives 50,86 m² (3.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_003 | area_label_vs_computed | r_L-1_mutfak | Label says 14,50 m², polygon gives 13,63 m² (6.0%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_004 | area_label_vs_computed | r_L-1_mutfak_2 | Label says 14,50 m², polygon gives 13,62 m² (6.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_005 | area_label_vs_computed | r_L-1_koridor | Label says 7,00 m², polygon gives 11,92 m² minus the stair 5,64 m² = 6,28 m² (10.2%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_006 | area_label_vs_computed | r_L-1_koridor_2 | Label says 7,00 m², polygon gives 11,93 m² minus the stair 5,64 m² = 6,29 m² (10.2%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_007 | area_label_vs_computed | r_L-1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_008 | area_label_vs_computed | r_L-1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_009 | area_label_vs_computed | r_L-1b_acik_mutfak | Label says 8,50 m², polygon gives 51,83 m² (509.7%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_010 | area_label_vs_computed | r_L-1b_acik_mutfak_2 | Label says 8,50 m², polygon gives 51,83 m² (509.7%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_011 | area_label_vs_computed | r_L-1b_oda | Label says 13,00 m², polygon gives 13,14 m² (1.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_012 | area_label_vs_computed | r_L-1b_oda_2 | Label says 13,00 m², polygon gives 13,15 m² (1.2%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_013 | area_label_vs_computed | r_L-1b_koridor | Label says 7,00 m², polygon gives 11,50 m² minus the stair 5,64 m² = 5,86 m² (16.3%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_014 | area_label_vs_computed | r_L-1b_koridor_2 | Label says 7,00 m², polygon gives 11,50 m² minus the stair 5,64 m² = 5,86 m² (16.3%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_015 | area_label_vs_computed | r_L-1b_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.7%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_016 | area_label_vs_computed | r_L-1b_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_017 | area_label_vs_computed | r_L0_yatak_odasi | Label says 16,00 m², polygon gives 16,13 m² (0.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_018 | area_label_vs_computed | r_L0_e_yatak_odasi | Label says 17,00 m², polygon gives 16,86 m² (0.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_019 | area_label_vs_computed | r_L0_e_yatak_odasi_2 | Label says 17,00 m², polygon gives 16,87 m² (0.8%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_020 | area_label_vs_computed | r_L0_yatak_odasi_2 | Label says 16,00 m², polygon gives 16,12 m² (0.7%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_021 | area_label_vs_computed | r_L0_koridor | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_022 | area_label_vs_computed | r_L0_koridor_2 | Label says 7,00 m², polygon gives 7,61 m² (8.8%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_023 | area_label_vs_computed | r_L0_yatak_odasi_3 | Label says 17,00 m², polygon gives 14,05 m² (17.3%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_024 | area_label_vs_computed | r_L0_yatak_odasi_4 | Label says 17,00 m², polygon gives 14,04 m² (17.4%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_025 | area_label_vs_computed | r_L0_banyo | Label says 4,90 m², polygon gives 4,97 m² (1.5%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_026 | area_label_vs_computed | r_L0_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_027 | area_label_vs_computed | r_L1_teras | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_028 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_029 | area_label_vs_computed | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | Label says 40,00 m², polygon gives 40,45 m² (1.1%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_030 | area_label_vs_computed | r_L1_koridor | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_031 | area_label_vs_computed | r_L1_koridor_2 | Label says 10,00 m², polygon gives 15,34 m² minus the stair 5,64 m² = 9,71 m² (2.9%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_032 | area_label_vs_computed | r_L1_banyo | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_033 | area_label_vs_computed | r_L1_banyo_2 | Label says 4,90 m², polygon gives 4,98 m² (1.6%) | within tolerance (8%), kept polygon from one_building.dwg |
| c_034 | area_label_vs_computed | r_L1_teras_2 | Label says 22,00 m², polygon gives 19,68 m² (10.6%) | over 8%: room marked unverified, polygon from one_building.dwg kept |
| c_035 | outline_mismatch | L0, L-1 | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_036 | outline_mismatch | L0, L-1b | Outer wall outline of Bodrum Kat differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_037 | outline_mismatch | L0, L1 | Outer wall outline of Çatı Katı differs from Zemin Kat by up to 1.499 m (areas 160.21 / 182.06 m²) | unresolved: each level kept as drawn |
| c_038 | symbol_type_disagreement | f_L-1_058 | f_L-1_058: sym_L-1_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_039 | symbol_type_disagreement | f_L-1_060 | f_L-1_060: sym_L-1_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_040 | symbol_type_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_041 | symbol_type_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_042 | symbol_type_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_043 | symbol_type_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_044 | symbol_type_disagreement | f_L-1_081 | f_L-1_081: sym_L-1_029: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_045 | symbol_type_disagreement | f_L-1_082 | f_L-1_082: sym_L-1_030: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_046 | symbol_type_disagreement | f_L-1_083 | f_L-1_083: sym_L-1_031: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) wall_cabinet | unresolved: the drawn footprint is kept as unknown, unverified |
| c_047 | symbol_type_disagreement | f_L-1_084 | f_L-1_084: sym_L-1_032: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_048 | symbol_type_disagreement | f_L-1_086 | f_L-1_086: sym_L-1_034: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) not_furniture, pass 2 (zai-org/GLM-4.6V-Flash) unknown | unresolved: the drawn footprint is kept as unknown, unverified |
| c_049 | symbol_type_disagreement | f_L-1_087 | f_L-1_087: sym_L-1_035: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_050 | symbol_type_disagreement | f_L-1_088 | f_L-1_088: sym_L-1_036: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) table_coffee | unresolved: the drawn footprint is kept as unknown, unverified |
| c_051 | symbol_type_disagreement | f_L-1b_040 | f_L-1b_040: sym_L-1b_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_052 | symbol_type_disagreement | f_L-1b_043 | f_L-1b_043: sym_L-1b_005: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_053 | symbol_type_disagreement | f_L-1b_044 | f_L-1b_044: sym_L-1b_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_island, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_054 | symbol_type_disagreement | f_L-1b_045 | f_L-1b_045: sym_L-1b_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_055 | symbol_type_disagreement | f_L-1b_046 | f_L-1b_046: sym_L-1b_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_056 | symbol_type_disagreement | f_L-1b_047 | f_L-1b_047: sym_L-1b_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) floor_lamp, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_057 | symbol_type_disagreement | f_L-1b_048 | f_L-1b_048: sym_L-1b_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_058 | symbol_type_disagreement | f_L-1b_049 | f_L-1b_049: sym_L-1b_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_059 | symbol_type_disagreement | f_L-1b_050 | f_L-1b_050: sym_L-1b_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_060 | symbol_type_disagreement | f_L-1b_051 | f_L-1b_051: sym_L-1b_013: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_061 | symbol_type_disagreement | f_L-1b_052 | f_L-1b_052: sym_L-1b_014: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) kitchen_counter, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_062 | symbol_type_disagreement | f_L-1b_055 | f_L-1b_055: sym_L-1b_017: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_063 | symbol_type_disagreement | f_L-1b_056 | f_L-1b_056: sym_L-1b_018: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) chair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_064 | symbol_type_disagreement | f_L-1b_057 | f_L-1b_057: sym_L-1b_019: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_065 | symbol_type_disagreement | f_L-1b_058 | f_L-1b_058: sym_L-1b_020: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) bar_stool, pass 2 (zai-org/GLM-4.6V-Flash) sink_kitchen | unresolved: the drawn footprint is kept as unknown, unverified |
| c_066 | symbol_type_disagreement | f_L0_027 | f_L0_027: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_067 | symbol_type_disagreement | f_L0_028 | f_L0_028: sym_L0_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_068 | symbol_type_disagreement | f_L0_029 | f_L0_029: sym_L0_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_069 | symbol_type_disagreement | f_L0_030 | f_L0_030: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_070 | symbol_type_disagreement | f_L1_015 | f_L1_015: sym_L1_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_071 | symbol_type_disagreement | f_L1_016 | f_L1_016: sym_L1_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_072 | symbol_type_disagreement | f_L1_017 | f_L1_017: sym_L1_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_073 | symbol_type_disagreement | f_L1_018 | f_L1_018: sym_L1_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) not_furniture | unresolved: the drawn footprint is kept as unknown, unverified |
| c_074 | symbol_type_disagreement | f_L1_021 | f_L1_021: sym_L1_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bench | unresolved: the drawn footprint is kept as unknown, unverified |
| c_075 | symbol_type_disagreement | f_L1_023 | f_L1_023: sym_L1_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) ottoman, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_076 | symbol_type_disagreement | f_L1_024 | f_L1_024: sym_L1_010: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_077 | symbol_type_disagreement | f_L1_025 | f_L1_025: sym_L1_011: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_078 | symbol_type_disagreement | f_L1_026 | f_L1_026: sym_L1_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) table_coffee, pass 2 (zai-org/GLM-4.6V-Flash) armchair | unresolved: the drawn footprint is kept as unknown, unverified |
| c_079 | other | r_L-1b_acik_mutfak | r_L-1b_acik_mutfak: one face holds the room names 'Açık Mutfak' and 'SALON' | unresolved: first label kept, room unverified |
| c_080 | other | r_L-1b_acik_mutfak_2 | r_L-1b_acik_mutfak_2: one face holds the room names 'Açık Mutfak' and 'SALON' | unresolved: first label kept, room unverified |
| c_081 | symbol_front_disagreement | f_L-1_053 | f_L-1_053: sym_L-1_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (L outline: the open inner corner is the front) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_082 | symbol_front_disagreement | f_L-1_054 | f_L-1_054: sym_L-1_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (L outline: the open inner corner is the front) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_083 | symbol_front_disagreement | f_L-1_068 | f_L-1_068: sym_L-1_016: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_084 | symbol_front_disagreement | f_L-1_069 | f_L-1_069: sym_L-1_017: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_085 | symbol_front_disagreement | f_L-1_070 | f_L-1_070: sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_086 | symbol_front_disagreement | f_L-1_071 | f_L-1_071: sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_087 | symbol_front_disagreement | f_L-1_072 | f_L-1_072: sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_088 | symbol_front_disagreement | f_L-1_075 | f_L-1_075: sym_L-1_023: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_089 | symbol_front_disagreement | f_L-1_076 | f_L-1_076: sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_090 | symbol_front_disagreement | f_L-1_077 | f_L-1_077: sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_091 | symbol_front_disagreement | f_L-1_078 | f_L-1_078: sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_092 | symbol_front_disagreement | f_L-1b_053 | f_L-1b_053: sym_L-1b_015: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_093 | symbol_front_disagreement | f_L-1b_054 | f_L-1b_054: sym_L-1b_016: AI front [90.0] (pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_094 | symbol_front_disagreement | f_L0_019 | f_L0_019: sym_L0_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_095 | symbol_front_disagreement | f_L0_020 | f_L0_020: sym_L0_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_096 | symbol_front_disagreement | f_L0_021 | f_L0_021: sym_L0_003: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_097 | symbol_front_disagreement | f_L0_022 | f_L0_022: sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_098 | symbol_front_disagreement | f_L0_027 | f_L0_027: sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_099 | symbol_front_disagreement | f_L0_028 | f_L0_028: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_100 | symbol_front_disagreement | f_L0_029 | f_L0_029: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_101 | symbol_front_disagreement | f_L0_030 | f_L0_030: sym_L0_012: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_102 | symbol_front_disagreement | f_L1_023 | f_L1_023: sym_L1_009: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_103 | symbol_front_disagreement | f_L1_024 | f_L1_024: sym_L1_010: AI front [270.0] (pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_104 | symbol_front_disagreement | f_L1_025 | f_L1_025: sym_L1_011: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_105 | symbol_front_disagreement | f_L1_026 | f_L1_026: sym_L1_012: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_106 | unit_mismatch | r1, r2, r3, r4, r5, r6 | sheets.json sc_001: one_building.dwg: $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| c_107 | level_mark_mismatch | r6 | sheets.json sc_002: section r6: the level mark 40.00 (MTEXT:304DD) gives -3.00 m but points at -3.15 m (the bottom of a slab) (0.15 m apart) | geometry wins: slab tops from the slab lines |

## Unverified

- o_L0_001
- o_L0_002
- r_L-1_koridor
- r_L-1_koridor_2
- r_L-1b_acik_mutfak
- r_L-1b_acik_mutfak_2
- r_L-1b_koridor
- r_L-1b_koridor_2
- r_L0_koridor
- r_L0_koridor_2
- r_L0_yatak_odasi_3
- r_L0_yatak_odasi_4
- r_L0_merdiven
- r_L0_merdiven_2
- r_L1_teras
- r_L1_teras_2
- f_L-1_005
- f_L-1_006
- f_L-1_007
- f_L-1_009
- f_L-1_014
- f_L-1_015
- f_L-1_016
- f_L-1_018
- f_L-1_021
- f_L-1_022
- f_L-1_058
- f_L-1_060
- f_L-1_069
- f_L-1_070
- f_L-1_071
- f_L-1_072
- f_L-1_081
- f_L-1_082
- f_L-1_083
- f_L-1_084
- f_L-1_085
- f_L-1_086
- f_L-1_087
- f_L-1_088
- f_L-1b_001
- f_L-1b_002
- f_L-1b_006
- f_L-1b_008
- f_L-1b_012
- f_L-1b_014
- f_L-1b_040
- f_L-1b_043
- f_L-1b_044
- f_L-1b_045
- f_L-1b_046
- f_L-1b_047
- f_L-1b_048
- f_L-1b_049
- f_L-1b_050
- f_L-1b_051
- f_L-1b_052
- f_L-1b_055
- f_L-1b_056
- f_L-1b_057
- f_L-1b_058
- f_L0_013
- f_L0_014
- f_L0_027
- f_L0_028
- f_L0_029
- f_L0_030
- f_L1_003
- f_L1_004
- f_L1_005
- f_L1_006
- f_L1_015
- f_L1_016
- f_L1_017
- f_L1_018
- f_L1_021
- f_L1_023
- f_L1_024
- f_L1_025
- f_L1_026
- f_L1_027
- f_L1_028

## Warnings

- one_building.dwg: 2 entities on layers that are off or frozen (or invisible) were not read
- one_building.dwg: entity types not read: WIPEOUT x40
- one_building.dwg: walls drawn as face lines: layer 'DBM_w_sld' chosen by evidence (closes in 12 of 12 labelled rooms, 100% of its long strokes pair, widths 0.10, 0.15, 0.20 m); runner-up 'A-BA' (0 of 12); 18 columns join the walls (1.12 m² of them standing out of the wall bands not modelled); 26 other wall primitives off that layer left out
- sym_L0_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_003: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_005: both passes say front 180 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L0_005: wardrobe without an agreed front: front 0 deg assumed (corner: the long side against a wall is the back)
- sym_L0_006: wardrobe without an agreed front: front 180 deg assumed (corner: the long side against a wall is the back)
- sym_L0_007: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L0_007: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L0_008: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L0_008: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L0_009: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_012: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_013: front assumed: both passes answered none; the drawn front 180 deg (only side within 0.25 m of a wall is the back) is kept
- sym_L0_014: front assumed: both passes answered none; the drawn front 180 deg (only side within 0.25 m of a wall is the back) is kept
- sym_L0_015: front assumed: both passes answered none; the drawn front 0 deg (only side within 0.25 m of a wall is the back) is kept
- sym_L0_016: front assumed: both passes answered none; the drawn front 0 deg (only side within 0.25 m of a wall is the back) is kept
- one_building.dwg: walls drawn as face lines: layer 'DBM_w_sld' chosen by evidence (closes in 8 of 8 labelled rooms, 98% of its long strokes pair, widths 0.10, 0.15, 0.20 m); runner-up 'DEKOAKRILIK01' (2 of 8); 14 columns join the walls (0.92 m² of them standing out of the wall bands not modelled); 24 other wall primitives off that layer left out
- sym_L-1_001: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (L outline: the open inner corner is the front): the drawn front is kept (vector geometry > AI)
- sym_L-1_002: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (L outline: the open inner corner is the front): the drawn front is kept (vector geometry > AI)
- sym_L-1_003: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L-1_003: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L-1_004: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L-1_004: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L-1_005: front assumed: both passes answered none; the drawn front 90 deg (only side within 0.25 m of a wall is the back) is kept
- sym_L-1_007: front assumed: both passes answered none; the drawn front 90 deg (only side within 0.25 m of a wall is the back) is kept
- sym_L-1_009: sofa without an agreed front: front unknown: width and depth follow the sofa size convention; the side the builder faces is assumed
- sym_L-1_010: sofa without an agreed front: front unknown: width and depth follow the sofa size convention; the side the builder faces is assumed
- sym_L-1_012: front assumed: both passes answered none; the drawn front 180 deg (chair faces the nearest table) is kept
- sym_L-1_014: front assumed: both passes answered none; the drawn front 0 deg (chair faces the nearest table) is kept
- sym_L-1_016: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L-1_017: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_018: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_019: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_020: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_021: front assumed: both passes answered none; the drawn front 180 deg (chair faces the nearest table) is kept
- sym_L-1_022: front assumed: both passes answered none; the drawn front 0 deg (chair faces the nearest table) is kept
- sym_L-1_023: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_024: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_025: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_026: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L-1_027: front assumed: both passes answered none; the drawn front 270 deg (chair faces the nearest table) is kept
- sym_L-1_028: front assumed: both passes answered none; the drawn front 270 deg (chair faces the nearest table) is kept
- sym_L-1_033: both passes say not_furniture: kept as an obstacle, not built
- one_building.dwg: walls drawn as face lines: layer 'DBM_w_sld' chosen by evidence (closes in 10 of 10 labelled rooms, 93% of its long strokes pair, widths 0.10, 0.15, 0.20 m); runner-up 'A-TEFRIS' (2 of 10); 14 columns join the walls (0.88 m² of them standing out of the wall bands not modelled); 28 other wall primitives off that layer left out
- sym_L-1b_003: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L-1b_003: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L-1b_004: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L-1b_004: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L-1b_015: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L-1b_016: AI front [90.0] (pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 0 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L-1b_021: wall_cabinet without an agreed front: front unknown: width and depth follow the wall_cabinet size convention; the side the builder faces is assumed
- sym_L-1b_022: wall_cabinet without an agreed front: front unknown: width and depth follow the wall_cabinet size convention; the side the builder faces is assumed
- one_building.dwg: walls drawn as face lines: layer 'DBM_w_sld' chosen by evidence (closes in 8 of 8 labelled rooms, 98% of its long strokes pair, widths 0.10, 0.15, 0.20 m); runner-up 'A-BA' (0 of 8); 14 columns join the walls (0.93 m² of them standing out of the wall bands not modelled); 20 other wall primitives off that layer left out
- sym_L1_005: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L1_005: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L1_006: both passes say front 270 deg, but that side stands within 0.25 m of a wall: the AI front is not used
- sym_L1_006: bathtub without an agreed front: front unknown: width and depth follow the bathtub size convention; the side the builder faces is assumed
- sym_L1_009: AI front [0.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L1_010: AI front [270.0] (pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L1_011: AI front [0.0] (pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L1_012: AI front [180.0] (pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L1_013: ottoman is not a type allowed in a other room: kept, unverified
- sym_L1_013: ottoman without an agreed front: front unknown: width and depth follow the ottoman size convention; the side the builder faces is assumed
- sym_L1_014: ottoman is not a type allowed in a other room: kept, unverified
- sym_L1_014: ottoman without an agreed front: front unknown: width and depth follow the ottoman size convention; the side the builder faces is assumed
- one_building.dwg r6: section: read for the heights by the sheets stage (sheets.json r6)
- L-1b: room 'Açık Mutfak' has more labels: SALON; first label kept
- L0: room at (4.718, 7.594) (5.71 m²) has no label: unlabelled face holding the stair
- L0: room at (7.786, 7.594) (5.72 m²) has no label: unlabelled face holding the stair
- twin copy: f_L-1_051: toilet -> toilet, front 90 deg (front of f_L-1_052, its mirror twin in r_L-1_banyo_2 (U16); inferred)
- twin copy: f_L-1b_040: unknown -> kitchen_island, front 270 deg (type and front of f_L-1b_039, its mirror twin in r_L-1b_acik_mutfak_2 (U16); inferred)
- twin copy: f_L0_016: toilet -> toilet, front 270 deg (front of f_L0_015, its mirror twin in r_L0_e_banyo (U16); inferred)
- twin copy: f_L0_017: toilet -> toilet, front 90 deg (front of f_L0_018, its mirror twin in r_L0_banyo (U16); inferred)
- twin copy: f_L1_021: unknown -> bench, front 0 deg (type and front of f_L1_022, its mirror twin in r_L1_koridor_2 (U16); inferred)
- f_L-1_081: not built (rug or group outline): drawn inside kitchen_counter f_L-1_003 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L-1_082: not built (rug or group outline): drawn inside kitchen_counter f_L-1_012 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L-1_083: not built (rug or group outline): drawn inside kitchen_counter f_L-1_003 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L-1_084: not built (rug or group outline): drawn inside kitchen_counter f_L-1_012 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L-1_086: not built (rug or group outline): drawn inside kitchen_counter f_L-1_010 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L-1b_001: not built (rug or group outline): outline 5.54 x 2.77 m around 3 other piece(s) (f_L-1b_043, f_L-1b_051, f_L-1b_052): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups)
- f_L-1b_002: not built (rug or group outline): outline 5.54 x 2.77 m around 3 other piece(s) (f_L-1b_044, f_L-1b_049, f_L-1b_050): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups)
- f_L-1b_057: not built (rug or group outline): drawn inside kitchen_counter f_L-1b_004 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L-1b_058: not built (rug or group outline): drawn inside kitchen_counter f_L-1b_010 (60% or more of it): a detail of that piece (a sink bowl, an appliance front), not a piece of its own (not built)
- f_L0_027: inferred desk: desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here
- f_L0_028: inferred desk: desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here
- f_L0_029: inferred desk: desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here
- f_L0_030: inferred desk: desk: the only type whose size range fits 1.45 x 0.91 m, that a bedroom room holds and whose position rule holds here
- f_L1_003: not built (rug or group outline): outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_012, f_L1_015): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups)
- f_L1_004: not built (rug or group outline): outline 4.49 x 3.02 m around 2 other piece(s) (f_L1_011, f_L1_016): a rug or zone outline, not a piece (not built; the decor rules lay rugs under the groups)
- f_L-1b_059: wall cabinet hung at 1.45 m above the floor (assumed: the rule of docs/milestone10.md §4.4, the documents give no height)
- f_L-1b_060: wall cabinet hung at 1.45 m above the floor (assumed: the rule of docs/milestone10.md §4.4, the documents give no height)
