# Ingest report: synthetic-05

Status: **ok**
Source: `projects/synthetic-05`, pipeline commit `2be169d6`, created 2026-10-04T00:07:55Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| zemin_kat.dxf | 1 | floor_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/zemin_kat_dxf_p1.png |
| zemin_kat_mobilya.dxf | 1 | furniture_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/zemin_kat_mobilya_dxf_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Zemin Kat | 0 | 0.00 | 2.70 (assumed_default) | 14 | 19 | 9 | 26 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_salon | L0 | Salon | SALON 19,76 m² | living | 19,76 | 19,76 | yes | verified |
| r_L0_ebeveyn_yatak_odasi | L0 | Ebeveyn Yatak Odası | EBEVEYN YATAK ODASI | bedroom | 17,86 | - | yes | verified |
| r_L0_ebeveyn_banyo | L0 | Ebeveyn Banyo | EBEVEYN BANYO | bathroom | 5,95 | - | yes | verified |
| r_L0_mutfak | L0 | Mutfak | MUTFAK | kitchen | 14,72 | - | yes | verified |
| r_L0_hol | L0 | Hol | HOL | hall | 7,92 | - | no | verified |
| r_L0_calisma_odasi | L0 | Çalışma Odası | ÇALIŞMA ODASI | other | 13,80 | - | no | verified |
| r_L0_antre | L0 | Antre | ANTRE | hall | 4,95 | - | no | verified |
| r_L0_banyo | L0 | Banyo | BANYO | bathroom | 6,60 | - | yes | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | YATAK ODASI | bedroom | 9,57 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_salon | sofa | KANEPE_3LU | from_documents | 2.20 x 0.90 | 90 | verified | zemin_kat_mobilya.dxf |
| f_L0_002 | L0 | r_L0_salon | table_coffee | SEHPA | from_documents | 1.00 x 0.60 | 90 | verified | zemin_kat_mobilya.dxf |
| f_L0_003 | L0 | r_L0_salon | tv_unit | TV_UNITESI | from_documents | 1.60 x 0.45 | 270 | verified | zemin_kat_mobilya.dxf |
| f_L0_004 | L0 | r_L0_salon | table_dining | YEMEK_MASASI | from_documents | 1.60 x 0.90 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_005 | L0 | r_L0_salon | chair | SANDALYE | from_documents | 0.45 x 0.45 | 180 | verified | zemin_kat_mobilya.dxf |
| f_L0_006 | L0 | r_L0_salon | chair | SANDALYE | from_documents | 0.45 x 0.45 | 180 | verified | zemin_kat_mobilya.dxf |
| f_L0_007 | L0 | r_L0_ebeveyn_yatak_odasi | bed_double | YATAK_CIFT | from_documents | 1.60 x 2.00 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_008 | L0 | r_L0_ebeveyn_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_009 | L0 | r_L0_ebeveyn_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_010 | L0 | r_L0_ebeveyn_yatak_odasi | wardrobe | DOLAP | from_documents | 1.80 x 0.60 | 90 | verified | zemin_kat_mobilya.dxf |
| f_L0_011 | L0 | r_L0_ebeveyn_yatak_odasi | dresser | SIFONYER | from_documents | 1.20 x 0.50 | 180 | verified | zemin_kat_mobilya.dxf |
| f_L0_012 | L0 | r_L0_ebeveyn_banyo | shower | DUS | from_documents | 0.90 x 0.90 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_013 | L0 | r_L0_ebeveyn_banyo | toilet | KLOZET | from_documents | 0.40 x 0.70 | 180 | verified | zemin_kat_mobilya.dxf |
| f_L0_014 | L0 | r_L0_ebeveyn_banyo | washbasin | LAVABO | from_documents | 0.60 x 0.45 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_015 | L0 | r_L0_mutfak | kitchen_counter | TEZGAH | from_documents | 2.40 x 0.60 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_016 | L0 | r_L0_mutfak | kitchen_counter | TEZGAH | from_documents | 2.40 x 0.60 | 90 | verified | zemin_kat_mobilya.dxf |
| f_L0_017 | L0 | r_L0_mutfak | sink_kitchen | EVIYE | from_documents | 0.80 x 0.50 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_018 | L0 | r_L0_mutfak | stove | OCAK | from_documents | 0.60 x 0.60 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_019 | L0 | r_L0_mutfak | fridge | BUZDOLABI | from_documents | 0.70 x 0.70 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_020 | L0 | r_L0_mutfak | washing_machine | CAMASIR_MAK | from_documents | 0.60 x 0.60 | 90 | verified | zemin_kat_mobilya.dxf |
| f_L0_021 | L0 | r_L0_banyo | bathtub | KUVET | from_documents | 1.70 x 0.75 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_022 | L0 | r_L0_banyo | toilet | KLOZET | from_documents | 0.40 x 0.70 | 90 | verified | zemin_kat_mobilya.dxf |
| f_L0_023 | L0 | r_L0_banyo | washbasin | LAVABO | from_documents | 0.60 x 0.45 | 270 | verified | zemin_kat_mobilya.dxf |
| f_L0_024 | L0 | r_L0_yatak_odasi | bed_single | YATAK_TEK | from_documents | 0.90 x 2.00 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_025 | L0 | r_L0_yatak_odasi | bed_single | YATAK_TEK | from_documents | 0.90 x 2.00 | 0 | verified | zemin_kat_mobilya.dxf |
| f_L0_026 | L0 | r_L0_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | zemin_kat_mobilya.dxf |

## Conflicts

None.

## Unverified

None.

## Warnings

- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- Zemin Kat: furniture taken from zemin_kat_mobilya.dxf (26 pieces); zemin_kat.dxf draws none
