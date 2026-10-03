# Ingest report: synthetic-01

Status: **ok**
Source: `projects/synthetic-01`, pipeline commit `76bd17dd`, created 2026-10-03T01:52:06Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| 1_kat.pdf | 1 | floor_plan | vector | L1 | 0.0352778 m/unit (pdf_scale_text) | 1.00 | - | debug/1_kat_pdf_p1.png |
| 1_kat_scan.png | 1 | other | scan | - | - | 0.00 | no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here | debug/1_kat_scan_png_p1.png |
| zemin_kat.dxf | 1 | floor_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/zemin_kat_dxf_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Zemin Kat | 0 | 0.00 | 2.70 (assumed_default) | 8 | 11 | 5 | 13 |
| L1 | 1. Kat | 1 | 3.00 | 2.70 (assumed_default) | 8 | 10 | 5 | 0 |

## Rooms

| Room | Level | Label | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|
| r_L0_salon | L0 | Salon | living | 24,50 | 24,50 | yes | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | bedroom | 14,00 | - | yes | verified |
| r_L0_hol | L0 | Hol | hall | 4,96 | - | no | verified |
| r_L0_banyo | L0 | Banyo | bathroom | 7,13 | - | yes | verified |
| r_L0_mutfak | L0 | Mutfak | kitchen | 8,50 | - | no | verified |
| r_L1_ebeveyn_yatak_odasi | L1 | Ebeveyn Yatak Odası | bedroom | 15,60 | - | no | verified |
| r_L1_hol | L1 | Hol | hall | 10,72 | - | no | verified |
| r_L1_yatak_odasi | L1 | Yatak Odası | bedroom | 12,21 | - | no | verified |
| r_L1_banyo | L1 | Banyo | bathroom | 9,57 | - | no | verified |
| r_L1_cocuk_odasi | L1 | Çocuk Odası | bedroom | 10,80 | - | no | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_salon | sofa | KANEPE_3LU | from_documents | 2.20 x 0.90 | 0 | verified | zemin_kat.dxf |
| f_L0_002 | L0 | r_L0_salon | table_coffee | SEHPA | from_documents | 1.00 x 0.60 | 0 | verified | zemin_kat.dxf |
| f_L0_003 | L0 | r_L0_salon | tv_unit | TV_UNITESI | from_documents | 1.60 x 0.45 | 180 | verified | zemin_kat.dxf |
| f_L0_004 | L0 | r_L0_salon | armchair | KOLTUK | from_documents | 0.90 x 0.90 | 270 | verified | zemin_kat.dxf |
| f_L0_005 | L0 | r_L0_salon | bookshelf | KITAPLIK | from_documents | 1.00 x 0.35 | 90 | verified | zemin_kat.dxf |
| f_L0_006 | L0 | r_L0_yatak_odasi | bed_double | YATAK_CIFT | from_documents | 1.60 x 2.00 | 0 | verified | zemin_kat.dxf |
| f_L0_007 | L0 | r_L0_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | zemin_kat.dxf |
| f_L0_008 | L0 | r_L0_yatak_odasi | nightstand | KOMIDIN | from_documents | 0.50 x 0.40 | 0 | verified | zemin_kat.dxf |
| f_L0_009 | L0 | r_L0_yatak_odasi | wardrobe | DOLAP | from_documents | 1.80 x 0.60 | 270 | verified | zemin_kat.dxf |
| f_L0_010 | L0 | r_L0_banyo | toilet | KLOZET | from_documents | 0.40 x 0.70 | 270 | verified | zemin_kat.dxf |
| f_L0_011 | L0 | r_L0_banyo | washbasin | LAVABO | from_documents | 0.60 x 0.45 | 270 | verified | zemin_kat.dxf |
| f_L0_012 | L0 | r_L0_banyo | shower | DUS | from_documents | 0.90 x 0.90 | 0 | verified | zemin_kat.dxf |
| f_L0_013 | L0 | r_L0_banyo | washing_machine | CAMASIR_MAK | from_documents | 0.60 x 0.60 | 0 | verified | zemin_kat.dxf |

## Conflicts

None.

## Unverified

None.

## Warnings

- 1_kat_scan.png p1: scan page skipped (no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- Level L1: ceiling height assumed 2.70 m (no section drawing found)
