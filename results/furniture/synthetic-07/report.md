# Ingest report: synthetic-07

Status: **ok**
Source: `projects/synthetic-07`, pipeline commit `7e95d4e1`, created 2026-10-09T13:51:59Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| sheet.dxf | 1 r1 | floor_plan | vector | L-1 | 0.01 m/unit (dxf_insunits) | 0.99 | - | debug/sheet_dxf_p1_r1.png |
| sheet.dxf | 1 r2 | floor_plan | vector | L-1b | 0.01 m/unit (dxf_insunits) | 0.99 | - | debug/sheet_dxf_p1_r2.png |
| sheet.dxf | 1 r3 | floor_plan | vector | L0 | 0.01 m/unit (dxf_insunits) | 0.99 | - | debug/sheet_dxf_p1_r3.png |
| sheet.dxf | 1 r4 | floor_plan | vector | L1 | 0.01 m/unit (dxf_insunits) | 0.99 | - | debug/sheet_dxf_p1_r4.png |
| sheet.dxf | 1 r5 | site_plan | vector | - | 0.01 m/unit (dxf_insunits) | 0.99 | site_plan: read for the exterior by the sheets stage (sheets.json r5) | debug/sheet_dxf_p1_r5.png |
| sheet.dxf | 1 r6 | section | vector | - | 0.01 m/unit (dxf_insunits) | 0.99 | section: read for the heights by the sheets stage (sheets.json r6) | debug/sheet_dxf_p1_r6.png |
| sheet.dxf | 1 r7 | elevation | vector | - | 0.01 m/unit (dxf_insunits) | 0.99 | elevation: read for the exterior by the sheets stage (sheets.json r7) | debug/sheet_dxf_p1_r7.png |
| sheet.dxf | 1 r8 | elevation | vector | - | 0.01 m/unit (dxf_insunits) | 0.99 | elevation: read for the exterior by the sheets stage (sheets.json r8) | debug/sheet_dxf_p1_r8.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L-1 | Bodrum Kat | -1 | -3.00 | 2.80 (section) | 6 | 10 | 3 | 6 |
| L-1b | Bodrum Kat | -1 | -3.00 | 2.80 (section) | 6 | 10 | 2 | 6 |
| L0 | Zemin Kat | 0 | 0.00 | 2.80 (section) | 6 | 10 | 3 | 5 |
| L1 | Çatı Katı | 1 | 3.00 | 3.80 (section) | 6 | 4 | 3 | 1 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L-1_salon | L-1 | Salon | SALON | living | 43,50 | 43,50 | yes | verified |
| r_L-1_mutfak | L-1 | Mutfak | MUTFAK | kitchen | 13,32 | 13,30 | yes | verified |
| r_L-1_hol | L-1 | Hol | HOL | hall | 13,32 | 13,30 | yes | verified |
| r_L-1b_salon_acik_mutfak | L-1b | Salon + Açık Mutfak | SALON + AÇIK MUTFAK | living | 57,19 | 57,20 | yes | verified |
| r_L-1b_hol | L-1b | Hol | HOL | hall | 13,32 | 13,30 | yes | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | YATAK ODASI | bedroom | 43,50 | 43,50 | yes | verified |
| r_L0_banyo | L0 | Banyo | BANYO | bathroom | 13,32 | 13,30 | yes | verified |
| r_L0_hol | L0 | Hol | HOL | hall | 13,32 | 13,30 | yes | verified |
| r_L1_oyun_odasi | L1 | Oyun Odası | OYUN ODASI | other | 43,50 | 43,50 | no | verified |
| r_L1_teras | L1 | Teras | TERAS | balcony | 13,32 | 13,30 | no | verified |
| r_L1_hol | L1 | Hol | HOL | hall | 13,32 | 13,30 | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L-1_001 | L-1 | r_L-1_hol | stair | - | from_documents | 3.00 x 1.00 | 90 | verified | sheet.dxf |
| f_L-1_002 | L-1 | r_L-1_mutfak | fridge | BUZDOLABI | from_documents | 0.70 x 0.70 | 0 | verified | sheet.dxf |
| f_L-1_003 | L-1 | r_L-1_mutfak | stove | OCAK | from_documents | 0.60 x 0.60 | 0 | verified | sheet.dxf |
| f_L-1_004 | L-1 | r_L-1_mutfak | kitchen_counter | TEZGAH | from_documents | 2.40 x 0.60 | 90 | verified | sheet.dxf |
| f_L-1_005 | L-1 | r_L-1_salon | sofa | KANEPE_3LU | from_documents | 2.20 x 0.90 | 0 | verified | sheet.dxf |
| f_L-1_006 | L-1 | r_L-1_mutfak | sink_kitchen | EVIYE | from_documents | 0.80 x 0.50 | 90 | verified | sheet.dxf |
| f_L-1b_001 | L-1b | r_L-1b_hol | stair | - | from_documents | 3.00 x 1.00 | 90 | verified | sheet.dxf |
| f_L-1b_002 | L-1b | r_L-1b_salon_acik_mutfak | fridge | BUZDOLABI | from_documents | 0.70 x 0.70 | 0 | verified | sheet.dxf |
| f_L-1b_003 | L-1b | r_L-1b_salon_acik_mutfak | stove | OCAK | from_documents | 0.60 x 0.60 | 0 | verified | sheet.dxf |
| f_L-1b_004 | L-1b | r_L-1b_salon_acik_mutfak | kitchen_counter | TEZGAH | from_documents | 2.40 x 0.60 | 90 | verified | sheet.dxf |
| f_L-1b_005 | L-1b | r_L-1b_salon_acik_mutfak | sofa | KANEPE_3LU | from_documents | 2.20 x 0.90 | 0 | verified | sheet.dxf |
| f_L-1b_006 | L-1b | r_L-1b_salon_acik_mutfak | sink_kitchen | EVIYE | from_documents | 0.80 x 0.50 | 90 | verified | sheet.dxf |
| f_L0_001 | L0 | r_L0_hol | stair | - | from_documents | 3.00 x 1.00 | 90 | verified | sheet.dxf |
| f_L0_002 | L0 | r_L0_yatak_odasi | bed_double | YATAK_CIFT | from_documents | 2.00 x 1.60 | 90 | verified | sheet.dxf |
| f_L0_003 | L0 | r_L0_banyo | shower | DUS | from_documents | 0.90 x 0.90 | 0 | verified | sheet.dxf |
| f_L0_004 | L0 | r_L0_banyo | toilet | KLOZET | from_documents | 0.70 x 0.40 | 0 | verified | sheet.dxf |
| f_L0_005 | L0 | r_L0_banyo | washbasin | LAVABO | from_documents | 0.60 x 0.45 | 90 | verified | sheet.dxf |
| f_L1_001 | L1 | r_L1_hol | stair | - | from_documents | 3.00 x 1.00 | 90 | verified | sheet.dxf |

## Building (sheets)

| Level | Kind | Variant | Region | Elevation | Source | Ceiling | Source |
|---|---|---|---|---|---|---|---|
| L-1 | basement | base | r1 | -3.00 | section | 2.80 | section |
| L-1b | basement | Açık mutfak | r2 | -3.00 | section | 2.80 | section |
| L0 | floor | base | r3 | 0.00 | section | 2.80 | section |
| L1 | attic | base | r4 | 3.00 | section | 3.80 | section |

Levels left out (failed_levels: leave_out):

- none

| Variant | Label | Levels | Rooms changed | Exterior changed |
|---|---|---|---|---|
| base | Base | L-1, L0, L1 | - | False |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r_L-1b_salon_acik_mutfak | False |

| Slab | Top z | Thickness | Source | Stair voids |
|---|---|---|---|---|
| sl_L-1 | -3.00 | 0.20 | section | 0 |
| sl_L0 | 0.00 | 0.20 | section | 1 |
| sl_L1 | 3.00 | 0.20 | section | 1 |

Roof: **gable** (section); eaves 3.96 m, ridge 7.11 m, pitches 35.00 deg, overhang 0.50 m, thickness 0.25 m; assumed: the ridge runs across the cut (a gable read from one section)

Facade (drawn faces only; every other look is resolved by the build):

- south: render (whole height)
- south: stone_cladding z 0.00 to 0.60 m
- east: render (whole height)
- elevation r7 (south): 2 windows, 1 doors; plan check: 3 matched, 0 on the plans only, 0 on the elevation only
- elevation r8 (east): 2 windows, 0 doors; plan check: 2 matched, 0 on the plans only, 0 on the elevation only

Site: plot drawn; 0 paving, 1 grass, 1 parking surfaces; 2 labels; north 0.0 deg

## Units

Project unit system: **metric**

| Document | Unit system | Source kind |
|---|---|---|
| sheet.dxf | metric | dxf |

## Scale

**sheet.dxf**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- sheet.dxf p1: drawing units known (0.01 m per unit)

**sheet.dxf**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- sheet.dxf p1: drawing units known (0.01 m per unit)

**sheet.dxf**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- sheet.dxf p1: drawing units known (0.01 m per unit)

**sheet.dxf**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- sheet.dxf p1: drawing units known (0.01 m per unit)

## Room size labels

None.

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sw_L0_001 | boundary wall (plot) | 19,70 m long, 0,20 m thick |
| sw_L0_002 | boundary wall (plot) | 23,70 m long, 0,20 m thick |
| sw_L0_003 | boundary wall (plot) | 19,70 m long, 0,20 m thick |
| sw_L0_004 | boundary wall (plot) | 23,70 m long, 0,20 m thick |
| sa_L0_otopark | area 'Otopark' | label size -, measured - (-), no closed outline |
| sa_L0_bahce | area 'Bahçe' | label size -, measured - (-), no closed outline |
| sd_L0_001 | decor (tree) | 2,40 m x 2,40 m |
| sd_L0_002 | decor (tree) | 2,40 m x 2,40 m |
| sd_L0_003 | decor (tree) | 2,40 m x 2,40 m |

## Separators

None considered.

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| sheet.dxf | run | window | 1,20 m | INSERT:1E2/0, INSERT:1E2/1, INSERT:1E2/2, INSERT:1E2/3, INSERT:1E2/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:1E0/1 |
| sheet.dxf | run | window | 0,60 m | INSERT:1E4/0, INSERT:1E4/1, INSERT:1E4/2, INSERT:1E4/3, INSERT:1E4/4 |
| sheet.dxf | run | door | 0,80 m | INSERT:1DE/1 |
| sheet.dxf | run | window | 1,20 m | INSERT:1E8/0, INSERT:1E8/1, INSERT:1E8/2, INSERT:1E8/3, INSERT:1E8/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:1EA/0, INSERT:1EA/1, INSERT:1EA/2, INSERT:1EA/3, INSERT:1EA/4 |
| sheet.dxf | run | door | 1,40 m | INSERT:1DA/1, INSERT:1DA/3 |
| sheet.dxf | run | window | 1,20 m | INSERT:1E6/0, INSERT:1E6/1, INSERT:1E6/2, INSERT:1E6/3, INSERT:1E6/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:1DC/1 |
| sheet.dxf | run | window | 0,60 m | INSERT:1EC/0, INSERT:1EC/1, INSERT:1EC/2, INSERT:1EC/3, INSERT:1EC/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:147/0, INSERT:147/1, INSERT:147/2, INSERT:147/3, INSERT:147/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:149/0, INSERT:149/1, INSERT:149/2, INSERT:149/3, INSERT:149/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:14B/0, INSERT:14B/1, INSERT:14B/2, INSERT:14B/3, INSERT:14B/4 |
| sheet.dxf | run | door | 0,80 m | INSERT:143/1 |
| sheet.dxf | run | window | 1,20 m | INSERT:14F/0, INSERT:14F/1, INSERT:14F/2, INSERT:14F/3, INSERT:14F/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:151/0, INSERT:151/1, INSERT:151/2, INSERT:151/3, INSERT:151/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:145/1 |
| sheet.dxf | run | window | 1,20 m | INSERT:14D/0, INSERT:14D/1, INSERT:14D/2, INSERT:14D/3, INSERT:14D/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:141/0, INSERT:141/1, INSERT:141/2, INSERT:141/3 |
| sheet.dxf | run | window | 0,60 m | INSERT:153/0, INSERT:153/1, INSERT:153/2, INSERT:153/3, INSERT:153/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:193/0, INSERT:193/1, INSERT:193/2, INSERT:193/3, INSERT:193/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:195/0, INSERT:195/1, INSERT:195/2, INSERT:195/3, INSERT:195/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:197/0, INSERT:197/1, INSERT:197/2, INSERT:197/3, INSERT:197/4 |
| sheet.dxf | run | door | 0,80 m | INSERT:18F/1 |
| sheet.dxf | run | window | 1,20 m | INSERT:19B/0, INSERT:19B/1, INSERT:19B/2, INSERT:19B/3, INSERT:19B/4 |
| sheet.dxf | run | window | 1,20 m | INSERT:19D/0, INSERT:19D/1, INSERT:19D/2, INSERT:19D/3, INSERT:19D/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:191/1 |
| sheet.dxf | run | window | 1,20 m | INSERT:199/0, INSERT:199/1, INSERT:199/2, INSERT:199/3, INSERT:199/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:18D/0, INSERT:18D/1, INSERT:18D/2, INSERT:18D/3 |
| sheet.dxf | run | window | 0,60 m | INSERT:19F/0, INSERT:19F/1, INSERT:19F/2, INSERT:19F/3, INSERT:19F/4 |
| sheet.dxf | run | door | 0,80 m | INSERT:223/1 |
| sheet.dxf | run | window | 1,20 m | INSERT:225/0, INSERT:225/1, INSERT:225/2, INSERT:225/3, INSERT:225/4 |
| sheet.dxf | run | door | 0,90 m | INSERT:221/1 |
| sheet.dxf | run | window | 0,60 m | INSERT:227/0, INSERT:227/1, INSERT:227/2, INSERT:227/3, INSERT:227/4 |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L-1_001 | stair | rule (stair rule: 1 flight(s), 13 tread lines) | - | yes | verified |
| f_L-1_002 | fridge | block_name | - | yes | verified |
| f_L-1_003 | stove | block_name | - | yes | verified |
| f_L-1_004 | kitchen_counter | block_name | - | yes | verified |
| f_L-1_005 | sofa | block_name | - | yes | verified |
| f_L-1_006 | sink_kitchen | block_name | - | yes | verified |
| f_L-1b_001 | stair | rule (stair rule: 1 flight(s), 13 tread lines) | - | yes | verified |
| f_L-1b_002 | fridge | block_name | - | yes | verified |
| f_L-1b_003 | stove | block_name | - | yes | verified |
| f_L-1b_004 | kitchen_counter | block_name | - | yes | verified |
| f_L-1b_005 | sofa | block_name | - | yes | verified |
| f_L-1b_006 | sink_kitchen | block_name | - | yes | verified |
| f_L0_001 | stair | rule (stair rule: 1 flight(s), 13 tread lines) | - | yes | verified |
| f_L0_002 | bed_double | block_name | - | yes | verified |
| f_L0_003 | shower | block_name | - | yes | verified |
| f_L0_004 | toilet | block_name | - | yes | verified |
| f_L0_005 | washbasin | block_name | - | yes | verified |
| f_L1_001 | stair | rule (stair rule: 1 flight(s), 13 tread lines) | - | yes | verified |

## Assumed values

- L-1: ceiling height 2.80 m (section)
- L-1b: ceiling height 2.80 m (section)
- L0: ceiling height 2.80 m (section)
- L1: ceiling height 3.80 m (section)
- win_L-1_001 (window): height 1,20 m
- win_L-1_001 (window): sill height 0,90 m
- win_L-1_002 (window): height 1,20 m
- win_L-1_002 (window): sill height 0,90 m
- win_L-1_003 (window): height 1,20 m
- win_L-1_003 (window): sill height 0,90 m
- d_L-1_001 (door): height 2,10 m
- win_L-1_004 (window): height 1,20 m
- win_L-1_004 (window): sill height 0,90 m
- win_L-1_005 (window): height 1,20 m
- win_L-1_005 (window): sill height 0,90 m
- d_L-1_002 (door): height 2,10 m
- win_L-1_006 (window): height 1,20 m
- win_L-1_006 (window): sill height 0,90 m
- d_L-1_003 (door): height 2,10 m
- win_L-1_007 (window): height 1,20 m
- win_L-1_007 (window): sill height 0,90 m
- win_L-1b_001 (window): height 1,20 m
- win_L-1b_001 (window): sill height 0,90 m
- win_L-1b_002 (window): height 1,20 m
- win_L-1b_002 (window): sill height 0,90 m
- win_L-1b_003 (window): height 1,20 m
- win_L-1b_003 (window): sill height 0,90 m
- d_L-1b_001 (door): height 2,10 m
- win_L-1b_004 (window): height 1,20 m
- win_L-1b_004 (window): sill height 0,90 m
- win_L-1b_005 (window): height 1,20 m
- win_L-1b_005 (window): sill height 0,90 m
- d_L-1b_002 (door): height 2,10 m
- win_L-1b_006 (window): height 1,20 m
- win_L-1b_006 (window): sill height 0,90 m
- d_L-1b_003 (door): height 2,10 m
- win_L-1b_007 (window): height 1,20 m
- win_L-1b_007 (window): sill height 0,90 m
- win_L0_001 (window): height 1,20 m
- win_L0_001 (window): sill height 0,90 m
- d_L0_001 (door): height 2,10 m
- win_L0_002 (window): height 1,20 m
- win_L0_002 (window): sill height 0,90 m
- d_L0_002 (door): height 2,10 m
- win_L0_003 (window): height 1,20 m
- win_L0_003 (window): sill height 0,90 m
- win_L0_004 (window): height 1,20 m
- win_L0_004 (window): sill height 0,90 m
- d_L0_003 (door): height 2,10 m
- win_L0_005 (window): height 1,20 m
- win_L0_005 (window): sill height 0,90 m
- d_L0_004 (door): height 2,10 m
- win_L0_006 (window): height 1,20 m
- win_L0_006 (window): sill height 0,90 m
- d_L1_001 (door): height 2,10 m
- win_L1_001 (window): height 1,20 m
- win_L1_001 (window): sill height 0,90 m
- d_L1_002 (door): height 2,10 m
- win_L1_002 (window): height 1,20 m
- win_L1_002 (window): sill height 0,90 m
- f_L-1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- f_L-1b_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- f_L0_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)
- f_L1_001 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed)

## Notes

### sheet.dxf

- furniture size checks use the wenart/recognition/size_table.yaml
- 3 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- stair at (49.25, 46.40): 1 flight(s) of 1.000 m
- 5 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: INSERT:1DA/0,INSERT:1DA/2,INSERT:1DC/0,INSERT:1DE/0,INSERT:1E0/0

### sheet.dxf

- furniture size checks use the wenart/recognition/size_table.yaml
- 5 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- stair at (15.25, 48.00): 1 flight(s) of 1.000 m
- 3 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: INSERT:143/0,INSERT:145/0,INSERT:15B/1

### sheet.dxf

- furniture size checks use the wenart/recognition/size_table.yaml
- 5 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- stair at (32.25, 47.75): 1 flight(s) of 1.000 m
- 3 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: INSERT:18F/0,INSERT:191/0,INSERT:1A7/1

### sheet.dxf

- furniture size checks use the wenart/recognition/size_table.yaml
- 1 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 4 sides of outlines larger than 4.5 m both ways are no furniture: LWPOLYLINE:22E
- 1 straight strokes longer than 4.5 m that cross the building outline are no furniture: LINE:22F
- stair at (66.75, 46.75): 1 flight(s) of 1.000 m
- 2 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: INSERT:221/0,INSERT:223/0

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | area_label_vs_computed | r_L-1_mutfak | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_002 | area_label_vs_computed | r_L-1_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_003 | area_label_vs_computed | r_L-1b_salon_acik_mutfak | Label says 57,20 m², polygon gives 57,19 m² (0.0%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_004 | area_label_vs_computed | r_L-1b_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_005 | area_label_vs_computed | r_L0_banyo | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_006 | area_label_vs_computed | r_L0_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_007 | area_label_vs_computed | r_L1_teras | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |
| c_008 | area_label_vs_computed | r_L1_hol | Label says 13,30 m², polygon gives 13,32 m² (0.2%) | within tolerance (3%), kept polygon from sheet.dxf |

## Unverified

None.

## Warnings

- sheet.dxf: walls drawn as face lines: layer 'AR_w_sld' chosen by evidence (closes in 3 of 3 labelled rooms, 100% of its long strokes pair, widths 0.10, 0.25 m); runner-up 'A_Pencere' (0 of 3); 6 columns join the walls (0.00 m² of them standing out of the wall bands not modelled)
- sheet.dxf: walls drawn as face lines: layer 'AR_w_sld' chosen by evidence (closes in 2 of 2 labelled rooms, 100% of its long strokes pair, widths 0.10, 0.25 m); runner-up 'A_Pencere' (0 of 2); 6 columns join the walls (0.00 m² of them standing out of the wall bands not modelled)
- sheet.dxf: walls drawn as face lines: layer 'AR_w_sld' chosen by evidence (closes in 3 of 3 labelled rooms, 100% of its long strokes pair, widths 0.10, 0.25 m); runner-up 'A_Mobilya' (0 of 3); 6 columns join the walls (0.00 m² of them standing out of the wall bands not modelled)
- sheet.dxf r5: site_plan: read for the exterior by the sheets stage (sheets.json r5)
- sheet.dxf r6: section: read for the heights by the sheets stage (sheets.json r6)
- sheet.dxf r7: elevation: read for the exterior by the sheets stage (sheets.json r7)
- sheet.dxf r8: elevation: read for the exterior by the sheets stage (sheets.json r8)
