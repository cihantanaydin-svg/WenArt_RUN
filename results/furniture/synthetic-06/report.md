# Ingest report: synthetic-06

Status: **ok**
Source: `projects/synthetic-06`, pipeline commit `2be169d6`, created 2026-10-04T00:07:46Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| synthetic-06.dwg | 1 | floor_plan | vector | L0 | 0.0254 m/unit (dxf_insunits) | 0.60 | - | debug/synthetic_06_dwg_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Ground floor (assumed) | 0 | 0.00 | 2.70 (assumed_default) | 9 | 14 | 6 | 11 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_kitchen | L0 | Kitchen | KITCHEN | kitchen | 9,06 | - | yes | verified |
| r_L0_living_room | L0 | Living Room | LIVING ROOM | living | 15,75 | - | yes | verified |
| r_L0_bath | L0 | Bath | BATH | bathroom | 3,25 | - | yes | verified |
| r_L0_lobby | L0 | Lobby | LOBBY | hall | 6,97 | - | no | verified |
| r_L0_bed_room | L0 | Bed Room | BED ROOM | bedroom | 10,72 | - | no | verified |
| r_L0_master_bed_room | L0 | Master Bed Room | MASTER BED ROOM | bedroom | 11,74 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_master_bed_room | bed_double | BED-DOUBLE | from_documents | 2.03 x 1.52 | 90 | verified | synthetic-06.dwg |
| f_L0_002 | L0 | r_L0_living_room | sofa | SOFA-3 | from_documents | 2.13 x 0.91 | 0 | verified | synthetic-06.dwg |
| f_L0_003 | L0 | r_L0_kitchen | table_dining | DINING-6 | from_documents | 1.83 x 0.91 | 90 | verified | synthetic-06.dwg |
| f_L0_004 | L0 | r_L0_bath | toilet | WC | from_documents | 0.71 x 0.51 | 0 | verified | synthetic-06.dwg |
| f_L0_005 | L0 | r_L0_kitchen | chair | DINING-6/CHAIR | from_documents | 0.46 x 0.46 | 0 | verified | synthetic-06.dwg |
| f_L0_006 | L0 | r_L0_kitchen | chair | DINING-6/CHAIR | from_documents | 0.46 x 0.46 | 0 | verified | synthetic-06.dwg |
| f_L0_007 | L0 | r_L0_kitchen | chair | DINING-6/CHAIR | from_documents | 0.46 x 0.46 | 0 | verified | synthetic-06.dwg |
| f_L0_008 | L0 | r_L0_kitchen | chair | DINING-6/CHAIR | from_documents | 0.46 x 0.46 | 0 | verified | synthetic-06.dwg |
| f_L0_009 | L0 | r_L0_kitchen | chair | DINING-6/CHAIR | from_documents | 0.46 x 0.46 | 90 | verified | synthetic-06.dwg |
| f_L0_010 | L0 | r_L0_kitchen | chair | DINING-6/CHAIR | from_documents | 0.46 x 0.46 | 90 | verified | synthetic-06.dwg |
| f_L0_011 | L0 | r_L0_bath | washbasin | BASIN | from_documents | 0.51 x 0.41 | 0 | verified | synthetic-06.dwg |

## Units

Project unit system: **imperial** (lengths in feet and inches, metres in brackets)

| Document | Unit system | Source kind |
|---|---|---|
| synthetic-06.dwg | imperial | dxf |

## Scale

**synthetic-06.dwg**: 0.0254 m/unit, method `dxf_insunits`, confidence 1.00

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 9'-0" | 9' 0" (2.74 m) | 108.00 | 9' 0" (2.74 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 15'-0" | 15' 0" (4.57 m) | 180.00 | 15' 0" (4.57 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 24'-0" | 24' 0" (7.32 m) | 288.00 | 24' 0" (7.32 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 13'-0" | 13' 0" (3.96 m) | 156.00 | 13' 0" (3.96 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 5'-6" | 5' 6" (1.68 m) | 66.00 | 5' 6" (1.68 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 12'-0" | 12' 0" (3.66 m) | 144.00 | 12' 0" (3.66 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 30'-6" | 30' 6" (9.30 m) | 366.00 | 30' 6" (9.30 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |
| 30'-6" | 30' 6" (9.30 m) | 366.00 | 30' 6" (9.30 m) | 0.0254 | +0.00% | dimension / dimension (dimension_entity) |

| Room-size label | Printed | Measured (clear size) | Off | Status |
|---|---|---|---|---|
| LIVING ROOM (14'-0" X 12'-0") | 14' 0" (4.27 m) x 12' 0" (3.66 m) | 14' 3" (4.34 m) x 12' 0" (3.66 m) | -1.7%, +0.0% | ok |

- synthetic-06.dwg p1: drawing units known (0.0254 m per unit)

## Room size labels

| Room | Label size | Measured | Status |
|---|---|---|---|
| r_L0_living_room | 14'-0" X 12'-0" | 14' 3" (4.34 m) x 12' 0" (3.66 m) | ok |

## Site

Recorded, not built.

None.

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| synthetic-06.dwg | end_to_wall | 6' 0" (1.83 m) | yes | two room names shared one face |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| synthetic-06.dwg | end | empty | 6' 0" (1.83 m) | - |
| synthetic-06.dwg | continuous | door | 3' 0" (0.91 m) | - |
| synthetic-06.dwg | continuous | door | 2' 6" (0.76 m) | - |
| synthetic-06.dwg | continuous | door | 2' 8" (0.81 m) | - |
| synthetic-06.dwg | continuous | door | 2' 8" (0.81 m) | - |
| synthetic-06.dwg | continuous | door | 2' 8" (0.81 m) | - |
| synthetic-06.dwg | continuous | window | 4' 0" (1.22 m) | - |
| synthetic-06.dwg | continuous | window | 6' 0" (1.83 m) | - |
| synthetic-06.dwg | continuous | window | 5' 0" (1.52 m) | - |
| synthetic-06.dwg | continuous | window | 5' 0" (1.52 m) | - |
| synthetic-06.dwg | continuous | window | 2' 0" (0.61 m) | - |
| synthetic-06.dwg | continuous | window | 4' 0" (1.22 m) | - |
| synthetic-06.dwg | continuous | window | 4' 0" (1.22 m) | - |
| synthetic-06.dwg | continuous | window | 4' 0" (1.22 m) | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L0_001 | bed_double | block_name | - | yes | verified |
| f_L0_002 | sofa | block_name | - | yes | verified |
| f_L0_003 | table_dining | block_name | - | yes | verified |
| f_L0_004 | toilet | block_name | - | yes | verified |
| f_L0_005 | chair | block_name | - | yes | verified |
| f_L0_006 | chair | block_name | - | yes | verified |
| f_L0_007 | chair | block_name | - | yes | verified |
| f_L0_008 | chair | block_name | - | yes | verified |
| f_L0_009 | chair | block_name | - | yes | verified |
| f_L0_010 | chair | block_name | - | yes | verified |
| f_L0_011 | washbasin | block_name | - | yes | verified |

## Assumed values

- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2.70 m (assumed_default)
- d_L0_001 (door): height 6' 11" (2.10 m)
- d_L0_002 (door): height 6' 11" (2.10 m)
- d_L0_003 (door): height 6' 11" (2.10 m)
- d_L0_004 (door): height 6' 11" (2.10 m)
- d_L0_005 (door): height 6' 11" (2.10 m)
- win_L0_001 (window): height 3' 11" (1.20 m)
- win_L0_001 (window): sill height 2' 11" (0.90 m)
- win_L0_002 (window): height 3' 11" (1.20 m)
- win_L0_002 (window): sill height 2' 11" (0.90 m)
- win_L0_003 (window): height 3' 11" (1.20 m)
- win_L0_003 (window): sill height 2' 11" (0.90 m)
- win_L0_004 (window): height 3' 11" (1.20 m)
- win_L0_004 (window): sill height 2' 11" (0.90 m)
- win_L0_005 (window): height 3' 11" (1.20 m)
- win_L0_005 (window): sill height 2' 11" (0.90 m)
- win_L0_006 (window): height 3' 11" (1.20 m)
- win_L0_006 (window): sill height 2' 11" (0.90 m)
- win_L0_007 (window): height 3' 11" (1.20 m)
- win_L0_007 (window): sill height 2' 11" (0.90 m)
- win_L0_008 (window): height 3' 11" (1.20 m)
- win_L0_008 (window): sill height 2' 11" (0.90 m)

## Notes

### synthetic-06.dwg

- furniture size checks use the wenart/recognition/size_table.yaml
- 60 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)

## Conflicts

None.

## Unverified

None.

## Warnings

- level title missing: assumed L0 Ground floor
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
