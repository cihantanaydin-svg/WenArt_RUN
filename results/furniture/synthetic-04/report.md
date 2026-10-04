# Ingest report: synthetic-04

Status: **ok**
Source: `projects/synthetic-04`, pipeline commit `2be169d6`, created 2026-10-04T00:06:34Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| 3_kat_plani.dxf | 1 | floor_plan | vector | L3 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/3_kat_plani_dxf_p1.png |
| 3_kat_plani_pdf.pdf | 1 | floor_plan | vector | L3 | 0.0352778 m/unit (pdf_scale_text) | 1.00 | - | debug/3_kat_plani_pdf_pdf_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L3 | 3. Kat | 3 | 9.00 | 2.70 (assumed_default) | 10 | 15 | 5 | 21 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L3_salon_mutfak | L3 | Salon + Mutfak | SALON + MUTFAK 39,05 m² | living | 39,05 | 39,05 | yes | verified |
| r_L3_yatak_odasi | L3 | Yatak Odası | YATAK ODASI | bedroom | 20,21 | - | yes | verified |
| r_L3_hol | L3 | Hol | HOL | hall | 8,32 | - | no | verified |
| r_L3_cocuk_odasi | L3 | Çocuk Odası | ÇOCUK ODASI | bedroom | 11,47 | - | no | verified |
| r_L3_banyo | L3 | Banyo | BANYO | bathroom | 4,86 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L3_001 | L3 | r_L3_salon_mutfak | kitchen_counter | TEZGAH | from_documents | 2.40 x 0.60 | 0 | verified | 3_kat_plani.dxf |
| f_L3_002 | L3 | r_L3_salon_mutfak | sink_kitchen | EVIYE | from_documents | 0.80 x 0.50 | 0 | verified | 3_kat_plani.dxf |
| f_L3_003 | L3 | r_L3_salon_mutfak | stove | OCAK | from_documents | 0.60 x 0.60 | 0 | verified | 3_kat_plani.dxf |
| f_L3_004 | L3 | r_L3_salon_mutfak | fridge | BUZDOLABI | from_documents | 0.70 x 0.70 | 0 | verified | 3_kat_plani.dxf |
| f_L3_005 | L3 | r_L3_salon_mutfak | table_dining | YEMEK_MASASI | from_documents | 1.60 x 0.90 | 0 | verified | 3_kat_plani.dxf |
| f_L3_006 | L3 | r_L3_salon_mutfak | chair | SANDALYE | from_documents | 0.45 x 0.45 | 180 | verified | 3_kat_plani.dxf |
| f_L3_007 | L3 | r_L3_salon_mutfak | chair | SANDALYE | from_documents | 0.45 x 0.45 | 180 | verified | 3_kat_plani.dxf |
| f_L3_008 | L3 | r_L3_salon_mutfak | chair | SANDALYE | from_documents | 0.45 x 0.45 | 0 | verified | 3_kat_plani.dxf |
| f_L3_009 | L3 | r_L3_salon_mutfak | chair | SANDALYE | from_documents | 0.45 x 0.45 | 0 | verified | 3_kat_plani.dxf |
| f_L3_010 | L3 | r_L3_salon_mutfak | sofa | KANEPE_3LU | from_documents | 2.20 x 0.90 | 90 | verified | 3_kat_plani.dxf |
| f_L3_011 | L3 | r_L3_salon_mutfak | table_coffee | SEHPA | from_documents | 1.00 x 0.60 | 90 | verified | 3_kat_plani.dxf |
| f_L3_012 | L3 | r_L3_salon_mutfak | tv_unit | TV_UNITESI | from_documents | 1.60 x 0.45 | 270 | verified | 3_kat_plani.dxf |
| f_L3_013 | L3 | r_L3_salon_mutfak | armchair | KOLTUK | from_documents | 0.90 x 0.90 | 315 | verified | 3_kat_plani.dxf |
| f_L3_014 | L3 | r_L3_salon_mutfak | bookshelf | KITAPLIK | from_documents | 1.00 x 0.35 | 90 | verified | 3_kat_plani.dxf |
| f_L3_015 | L3 | r_L3_yatak_odasi | bed_double | YATAK_CIFT | from_documents | 1.60 x 2.00 | 0 | verified | 3_kat_plani.dxf |
| f_L3_016 | L3 | r_L3_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | 3_kat_plani.dxf |
| f_L3_017 | L3 | r_L3_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | 3_kat_plani.dxf |
| f_L3_018 | L3 | r_L3_yatak_odasi | wardrobe | DOLAP | from_documents | 1.80 x 0.60 | 90 | verified | 3_kat_plani.dxf |
| f_L3_019 | L3 | r_L3_banyo | bathtub | KUVET | from_documents | 1.70 x 0.75 | 0 | verified | 3_kat_plani.dxf |
| f_L3_020 | L3 | r_L3_banyo | toilet | KLOZET | from_documents | 0.40 x 0.70 | 270 | verified | 3_kat_plani.dxf |
| f_L3_021 | L3 | r_L3_banyo | washbasin | LAVABO | from_documents | 0.60 x 0.45 | 180 | verified | 3_kat_plani.dxf |

## Conflicts

None.

## Unverified

None.

## Warnings

- Level L3: ceiling height assumed 2.70 m (no section drawing found)
