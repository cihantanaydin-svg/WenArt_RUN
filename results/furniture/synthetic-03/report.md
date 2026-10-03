# Ingest report: synthetic-03

Status: **ok**
Source: `projects/synthetic-03`, pipeline commit `76bd17dd`, created 2026-10-03T01:52:27Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| kat_planlari.pdf | 1 | floor_plan | vector | L-1 | 0.0352778 m/unit (pdf_scale_text) | 1.00 | - | debug/kat_planlari_pdf_p1.png |
| kat_planlari.pdf | 2 | floor_plan | vector | L0 | 0.0352778 m/unit (pdf_scale_text) | 1.00 | - | debug/kat_planlari_pdf_p2.png |
| kat_planlari.pdf | 3 | floor_plan | vector | L1 | 0.0352778 m/unit (pdf_scale_text) | 1.00 | - | debug/kat_planlari_pdf_p3.png |
| mobilya_plani.dxf | 1 | furniture_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/mobilya_plani_dxf_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | -1 | -3.00 | 2.70 (assumed_default) | 9 | 8 | 6 | 0 |
| L0 | Zemin Kat | 0 | 0.00 | 2.70 (assumed_default) | 10 | 13 | 7 | 21 |
| L1 | 1. Kat | 1 | 3.00 | 2.70 (assumed_default) | 9 | 12 | 6 | 0 |

## Rooms

| Room | Level | Label | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|
| r_L-1_kiler | L-1 | Kiler | storage | 14,00 | - | no | verified |
| r_L-1_hol | L-1 | Hol | hall | 11,68 | - | no | verified |
| r_L-1_yatak_odasi | L-1 | Yatak Odası | bedroom | 20,28 | - | no | verified |
| r_L-1_kiler_2 | L-1 | Kiler | storage | 14,80 | - | no | verified |
| r_L-1_wc | L-1 | WC | wc | 3,80 | - | no | verified |
| r_L-1_banyo | L-1 | Banyo | bathroom | 3,80 | - | no | verified |
| r_L0_salon | L0 | Salon | living | 23,50 | 24,00 | yes | verified |
| r_L0_hol | L0 | Hol | hall | 11,68 | - | no | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | bedroom | 15,08 | - | yes | verified |
| r_L0_mutfak | L0 | Mutfak | kitchen | 8,25 | - | yes | verified |
| r_L0_antre | L0 | Antre | hall | 4,00 | - | no | verified |
| r_L0_wc | L0 | WC | wc | 2,80 | - | yes | verified |
| r_L0_kiler | L0 | Kiler | storage | 2,80 | - | yes | verified |
| r_L1_ebeveyn_yatak_odasi | L1 | Ebeveyn Yatak Odası | bedroom | 15,60 | - | no | verified |
| r_L1_hol | L1 | Hol | hall | 11,68 | - | no | verified |
| r_L1_yatak_odasi | L1 | Yatak Odası | bedroom | 15,21 | - | no | verified |
| r_L1_cocuk_odasi | L1 | Çocuk Odası | bedroom | 13,20 | - | no | verified |
| r_L1_banyo | L1 | Banyo | bathroom | 6,27 | - | no | verified |
| r_L1_balkon | L1 | Balkon | balcony | 6,27 | - | no | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_salon | sofa | KANEPE_3LU | from_documents | 2.20 x 0.90 | 0 | verified | mobilya_plani.dxf |
| f_L0_002 | L0 | r_L0_salon | armchair | KOLTUK | from_documents | 0.90 x 0.90 | 270 | verified | mobilya_plani.dxf |
| f_L0_003 | L0 | r_L0_salon | armchair | KOLTUK | from_documents | 0.90 x 0.90 | 90 | verified | mobilya_plani.dxf |
| f_L0_004 | L0 | r_L0_salon | table_coffee | SEHPA | from_documents | 1.00 x 0.60 | 0 | verified | mobilya_plani.dxf |
| f_L0_005 | L0 | r_L0_salon | tv_unit | TV_UNITESI | from_documents | 1.60 x 0.45 | 180 | verified | mobilya_plani.dxf |
| f_L0_006 | L0 | r_L0_salon | bookshelf | KITAPLIK | from_documents | 1.00 x 0.35 | 270 | verified | mobilya_plani.dxf |
| f_L0_007 | L0 | r_L0_mutfak | kitchen_counter | TEZGAH | from_documents | 2.40 x 0.60 | 0 | verified | mobilya_plani.dxf |
| f_L0_008 | L0 | r_L0_mutfak | sink_kitchen | EVIYE | from_documents | 0.80 x 0.50 | 0 | verified | mobilya_plani.dxf |
| f_L0_009 | L0 | r_L0_mutfak | stove | OCAK | from_documents | 0.60 x 0.60 | 0 | verified | mobilya_plani.dxf |
| f_L0_010 | L0 | r_L0_mutfak | fridge | BUZDOLABI | from_documents | 0.70 x 0.70 | 0 | verified | mobilya_plani.dxf |
| f_L0_011 | L0 | r_L0_mutfak | table_dining | YEMEK_MASASI | from_documents | 1.60 x 0.90 | 0 | verified | mobilya_plani.dxf |
| f_L0_012 | L0 | r_L0_mutfak | chair | SANDALYE | from_documents | 0.45 x 0.45 | 180 | verified | mobilya_plani.dxf |
| f_L0_013 | L0 | r_L0_mutfak | chair | SANDALYE | from_documents | 0.45 x 0.45 | 180 | verified | mobilya_plani.dxf |
| f_L0_014 | L0 | r_L0_yatak_odasi | bed_double | YATAK_CIFT | from_documents | 1.60 x 2.00 | 0 | verified | mobilya_plani.dxf |
| f_L0_015 | L0 | r_L0_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | mobilya_plani.dxf |
| f_L0_016 | L0 | r_L0_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | mobilya_plani.dxf |
| f_L0_017 | L0 | r_L0_yatak_odasi | wardrobe | DOLAP | from_documents | 1.80 x 0.60 | 180 | verified | mobilya_plani.dxf |
| f_L0_018 | L0 | r_L0_yatak_odasi | dresser | SIFONYER | from_documents | 1.20 x 0.50 | 270 | verified | mobilya_plani.dxf |
| f_L0_019 | L0 | r_L0_wc | toilet | KLOZET | from_documents | 0.40 x 0.70 | 270 | verified | mobilya_plani.dxf |
| f_L0_020 | L0 | r_L0_wc | washbasin | LAVABO | from_documents | 0.60 x 0.45 | 270 | verified | mobilya_plani.dxf |
| f_L0_021 | L0 | r_L0_kiler | unknown | BLOK_A | from_documents | 1.20 x 0.50 | 90 | unverified | mobilya_plani.dxf |

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L0_salon | Label says 24,00 m², polygon gives 23,50 m² (2.1%) | within tolerance (3%), kept polygon from mobilya_plani.dxf |
| c_002 | dimension_vs_measured | w_L-1_004 | kat_planlari.pdf p1: dimension text 3,99 vs measured 3.80 m (5.0%) | kept measured geometry (vector PDF) |
| c_003 | count_mismatch | win_L0_004 | Zemin Kat: mobilya_plani.dxf has 6 windows, kat_planlari.pdf p2 has 5 | DXF wins over vector PDF, window kept |

## Unverified

- f_L0_021

## Warnings

- Level L-1: ceiling height assumed 2.70 m (no section drawing found)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- Level L1: ceiling height assumed 2.70 m (no section drawing found)
