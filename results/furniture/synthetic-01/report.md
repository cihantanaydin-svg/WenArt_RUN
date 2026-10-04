# Ingest report: synthetic-01

Status: **ok**
Source: `projects/synthetic-01`, pipeline commit `714dcc50e`, created 2026-10-04T09:58:36Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| 1_kat.pdf | 1 | floor_plan | vector | L1 | 0.0352778 m/unit (pdf_scale_text) | 1.00 | - | debug/1_kat_pdf_p1.png |
| 1_kat_scan.png | 1 | floor_plan | scan | L1 | 0.0169584 m/unit (dimension_text) | 0.90 | - | debug/1_kat_scan_png_p1.png |
| zemin_kat.dxf | 1 | floor_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/zemin_kat_dxf_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Zemin Kat | 0 | 0.00 | 2.70 (assumed_default) | 8 | 11 | 5 | 13 |
| L1 | 1. Kat | 1 | 3.00 | 2.70 (assumed_default) | 8 | 10 | 5 | 0 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_salon | L0 | Salon | SALON 24,50 m² | living | 24,50 | 24,50 | yes | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | YATAK ODASI | bedroom | 14,00 | - | yes | verified |
| r_L0_hol | L0 | Hol | HOL | hall | 4,96 | - | no | verified |
| r_L0_banyo | L0 | Banyo | BANYO | bathroom | 7,13 | - | yes | verified |
| r_L0_mutfak | L0 | Mutfak | MUTFAK | kitchen | 8,50 | - | no | verified |
| r_L1_ebeveyn_yatak_odasi | L1 | Ebeveyn Yatak Odası | EBEVEYN YATAK ODASI | bedroom | 15,60 | - | no | verified |
| r_L1_hol | L1 | Hol | HOL | hall | 10,72 | - | no | verified |
| r_L1_yatak_odasi | L1 | Yatak Odası | YATAK ODASI | bedroom | 12,21 | - | no | verified |
| r_L1_banyo | L1 | Banyo | BANYO | bathroom | 9,57 | - | no | verified |
| r_L1_cocuk_odasi | L1 | Çocuk Odası | ÇOCUK ODASI | bedroom | 10,80 | - | no | verified |

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

## Units

Project unit system: **metric**

| Document | Unit system | Source kind |
|---|---|---|
| 1_kat.pdf | metric | cad_pdf |
| 1_kat_scan.png | metric | raster_scan |
| zemin_kat.dxf | metric | dxf |

## Scale

**1_kat_scan.png**: 0.0169584 m/unit, method `dimension_text`, confidence 0.90

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 4,30 | 4,30 m | 253.85 | 4,30 m | 0.0169391 | -0.11% | extension / extension (parallel) |
| 3,60 | 3,60 m | 211.11 | 3,58 m | 0.017053 | +0.56% | extension / tick (parallel) |
| 1,70 | 1,70 m | 99.97 | 1,70 m | 0.0170056 | +0.28% | extension / extension (parallel) |
| 9,60 | 9,60 m | 566.09 | 9,60 m | 0.0169584 | +0.00% | extension / extension (parallel) |
| 3,00 | 3,00 m | 177.47 | 3,01 m | 0.0169046 | -0.32% | extension / extension (parallel) |
| 7,20 | 7,20 m | 424.83 | 7,20 m | 0.0169478 | -0.06% | extension / tick (parallel) |
| 4,20 | 4,20 m | 247.47 | 4,20 m | 0.0169715 | +0.08% | extension / tick (parallel) |

- 1_kat_scan.png p1: scale note 'ÖLÇEK 1/100' ignored: raster page without a verified pixel size
- 1_kat_scan.png p1: scale from 7 of 7 agreeing dimension texts

## Room size labels

None.

## Site

Recorded, not built.

None.

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| 1_kat_scan.png | end_to_end | 9,10 m | no | longer than 2.4 m |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| 1_kat_scan.png | run | closed | 0,01 m | - |
| 1_kat_scan.png | run | closed | 0,01 m | - |
| 1_kat_scan.png | continuous | door | 0,80 m | - |
| 1_kat_scan.png | continuous | door | 0,78 m | - |
| 1_kat_scan.png | continuous | door | 0,89 m | - |
| 1_kat_scan.png | continuous | window | 1,87 m | - |
| 1_kat_scan.png | continuous | window | 1,87 m | - |
| 1_kat_scan.png | continuous | window | 1,24 m | - |
| 1_kat_scan.png | continuous | window | 0,64 m | - |
| 1_kat_scan.png | continuous | window | 0,63 m | - |
| 1_kat_scan.png | continuous | window | 1,22 m | - |

## Furniture typing

None.

## Assumed values

- L0: ceiling height 2.70 m (assumed_default)
- L1: ceiling height 2.70 m (assumed_default)

## Notes

### 1_kat_scan.png p1 (evidence-only page)

- image file
- deskew: rotated by +0.027 deg (dominant direction of 139 long strokes)
- 5 raster wall ends moved onto the wall face they stop short of by <= 1.5 px: wall 1 start +1 mm, wall 2 end +0 mm, wall 4 end +5 mm, wall 5 end +14 mm, wall 6 start +16 mm
- furniture size checks use the wenart/recognition/size_table.yaml
- 14 glyph strokes inside text boxes ignored
- 69 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 1 drawn details smaller than 0.2 m ignored
- 1 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: seg:85
- 3 site edge or boundary line groups outside the building (not decor)

## Conflicts

None.

## Unverified

None.

## Warnings

- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- Level L1: ceiling height assumed 2.70 m (no section drawing found)
- 1. Kat: 1_kat_scan.png (scan) is evidence only for 1_kat.pdf p1: 8 walls, 9 openings, 0 furniture pieces and 4 room names confirmed
