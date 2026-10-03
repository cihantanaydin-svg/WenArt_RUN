# Ingest report: real01-scan

Status: **ok**
Source: `tests/fixtures/real01_raster/real01-scan`, pipeline commit `d69054ba`, created 2026-10-03T20:45:32Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| real01_scan.png | 1 | floor_plan | scan | L0 | 0.0117539 m/unit (dimension_text) | 0.50 | - | debug/real01_scan_png_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Ground floor (assumed) | 0 | 0.00 | 2.70 (assumed_default) | 18 | 22 | 9 | 17 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_bed_room | L0 | Bed Room | Bed Room | bedroom | 9,94 | - | yes | verified |
| r_L0_bath_toilet | L0 | Bath+ Toilet | Bath+ Toilet | bathroom | 3,12 | - | no | verified |
| r_L0_drawing_room | L0 | Drawing Room | Drawing Room | living | 18,05 | - | yes | verified |
| r_L0_room | L0 | Room | — | hall | 6,78 | - | yes | unverified |
| r_L0_pooja | L0 | Pooja | Pooja | prayer | 1,69 | - | yes | verified |
| r_L0_store | L0 | Store | Store | storage | 1,79 | - | yes | verified |
| r_L0_bed_room_2 | L0 | Bed Room | Bed Room | bedroom | 10,01 | - | yes | verified |
| r_L0_kitchen | L0 | Kitchen | Kitchen | kitchen | 8,61 | - | yes | verified |
| r_L0_dining | L0 | Dining | Dining | dining | 10,33 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_bed_room_2 | unknown | - | from_documents | 2.79 x 2.02 | 0 | unverified | real01_scan.png |
| f_L0_002 | L0 | r_L0_pooja | unknown | - | from_documents | 0.21 x 0.14 | 55 | unverified | real01_scan.png |
| f_L0_003 | L0 | r_L0_kitchen | unknown | - | from_documents | 0.21 x 0.17 | 78 | unverified | real01_scan.png |
| f_L0_004 | L0 | r_L0_store | unknown | - | from_documents | 0.21 x 0.14 | 90 | unverified | real01_scan.png |
| f_L0_005 | L0 | r_L0_kitchen | unknown | - | from_documents | 0.21 x 0.13 | 90 | unverified | real01_scan.png |
| f_L0_006 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.23 x 0.07 | 90 | unverified | real01_scan.png |
| f_L0_007 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.23 x 0.07 | 90 | unverified | real01_scan.png |
| f_L0_008 | L0 | r_L0_kitchen | unknown | - | from_documents | 2.98 x 0.91 | 153 | unverified | real01_scan.png |
| f_L0_009 | L0 | r_L0_bed_room | unknown | - | from_documents | 2.04 x 1.85 | 90 | unverified | real01_scan.png |
| f_L0_010 | L0 | r_L0_room | stair | - | from_documents | 1.49 x 2.39 | 0 | unverified | real01_scan.png |
| f_L0_011 | L0 | r_L0_dining | table_dining | - | from_documents | 1.51 x 1.32 | 39 | verified | real01_scan.png |
| f_L0_012 | L0 | r_L0_drawing_room | sofa | - | from_documents | 1.89 x 0.72 | 0 | verified | real01_scan.png |
| f_L0_013 | L0 | r_L0_drawing_room | unknown | - | from_documents | 1.87 x 0.71 | 90 | unverified | real01_scan.png |
| f_L0_014 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.95 x 0.94 | 0 | unverified | real01_scan.png |
| f_L0_015 | L0 | r_L0_dining | chair | - | from_documents | 0.46 x 0.38 | 90 | verified | real01_scan.png |
| f_L0_016 | L0 | r_L0_drawing_room | floor_lamp | - | from_documents | 0.34 x 0.33 | 0 | verified | real01_scan.png |
| f_L0_017 | L0 | r_L0_pooja | unknown | - | from_documents | 0.25 x 0.20 | 0 | unverified | real01_scan.png |

## Units

Project unit system: **imperial** (lengths in feet and inches, metres in brackets)

| Document | Unit system | Source kind |
|---|---|---|
| real01_scan.png | imperial | raster_scan |

## Scale

**real01_scan.png**: 0.0117539 m/unit, method `dimension_text`, confidence 0.70

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 30 | 30' 0" (9.14 m) | 777.95 | 30' 0" (9.14 m) | 0.0117539 | +0.00% | extension / extension (gap) |

| Room-size label | Printed | Measured (clear size) | Off | Status |
|---|---|---|---|---|
| Kitchen (9' 3" x 10' 3") | 9' 3" (2.82 m) x 10' 3" (3.12 m) | 9' 1" (2.78 m) x 10' 2" (3.10 m) | +1.5%, +0.8% | ok |
| Store (4' x 5') | 4' 0" (1.22 m) x 5' 0" (1.52 m) | 3' 11" (1.19 m) x 4' 11" (1.51 m) | +2.5%, +1.0% | ok |
| Pooja (4' x 4' 9") | 4' 0" (1.22 m) x 4' 9" (1.45 m) | 3' 11" (1.19 m) x 4' 8" (1.42 m) | +2.5%, +1.9% | ok |
| Drawing Room (14' x 14') | 14' 0" (4.27 m) x 14' 0" (4.27 m) | 13' 11" (4.24 m) x 14' 2" (4.32 m) | +0.7%, -1.3% | ok |
| Dining (14' x 8') | 14' 0" (4.27 m) x 8' 0" (2.44 m) | 13' 11" (4.24 m) x 8' 3" (2.50 m) | +0.7%, -2.5% | ok |
| Bath+ Toilet (7' x 5') | 7' 0" (2.13 m) x 5' 0" (1.52 m) | 6' 11" (2.11 m) x 4' 11" (1.50 m) | +1.1%, +2.0% | ok |
| Bed Room (11' x 10') | 11' 0" (3.35 m) x 10' 0" (3.05 m) | 10' 11" (3.33 m) x 9' 10" (3.01 m) | +0.7%, +1.3% | ok |
| Bed Room (11' x 10') | 11' 0" (3.35 m) x 10' 0" (3.05 m) | 10' 11" (3.32 m) x 9' 10" (3.01 m) | +1.0%, +1.3% | ok |

- real01_scan.png p1: provisional scale from 1 dimension text ('30'): 0.011754 m/unit; needs >= 3 room-size labels within 5%
- scale from one dimension, corroborated by 8 room sizes

## Room size labels

| Room | Label size | Measured | Status |
|---|---|---|---|
| r_L0_bed_room | 11' x 10' | 10' 11" (3.32 m) x 9' 10" (3.01 m) | ok |
| r_L0_bath_toilet | 7' x 5' | 6' 11" (2.11 m) x 4' 11" (1.50 m) | ok |
| r_L0_drawing_room | 14' x 14' | 14' 2" (4.33 m) x 13' 11" (4.24 m) | ok |
| r_L0_pooja | 4' x 4' 9" | 3' 11" (1.19 m) x 4' 8" (1.42 m) | ok |
| r_L0_store | 4' x 5' | 3' 11" (1.19 m) x 4' 11" (1.51 m) | ok |
| r_L0_bed_room_2 | 11' x 10' | 10' 11" (3.33 m) x 9' 10" (3.01 m) | ok |
| r_L0_kitchen | 9' 3" x 10' 3" | 9' 1" (2.78 m) x 10' 2" (3.10 m) | ok |
| r_L0_dining | 14' x 8' | 13' 11" (4.24 m) x 8' 3" (2.50 m) | ok |

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sw_L0_001 | boundary wall (plot) | 50' 1" (15.27 m) long, 0' 7" (0.18 m) thick |
| sw_L0_002 | boundary wall (plot) | 50' 1" (15.26 m) long, 0' 7" (0.17 m) thick |
| sw_L0_003 | boundary wall (plot) | 28' 11" (8.81 m) long, 0' 7" (0.18 m) thick |
| sw_L0_004 | boundary wall (plot) | 17' 9" (5.41 m) long, 0' 7" (0.19 m) thick |
| sa_L0_parking | area 'Parking' | label size -, measured - (-), no closed outline |
| sd_L0_001 | decor (other) | 1' 6" (0.47 m) x 4' 7" (1.40 m) |
| sd_L0_002 | decor (other) | 1' 3" (0.39 m) x 1' 1" (0.32 m) |
| sd_L0_003 | decor (other) | 0' 11" (0.27 m) x 0' 11" (0.29 m) |
| sd_L0_004 | decor (other) | 1' 3" (0.39 m) x 1' 2" (0.34 m) |
| sd_L0_005 | decor (other) | 1' 1" (0.33 m) x 0' 3" (0.07 m) |
| sd_L0_006 | decor (other) | 1' 0" (0.30 m) x 1' 0" (0.31 m) |
| sd_L0_007 | decor (other) | 0' 3" (0.06 m) x 1' 1" (0.34 m) |
| sd_L0_008 | decor (other) | 1' 0" (0.30 m) x 1' 1" (0.33 m) |
| sd_L0_009 | decor (other) | 0' 9" (0.22 m) x 1' 3" (0.38 m) |

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| real01_scan.png | end_to_wall | 4' 2" (1.27 m) | yes | two room names shared one face |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| real01_scan.png | run | window | 4' 10" (1.48 m) | seg:1206, seg:1208, seg:1210, seg:1214 |
| real01_scan.png | run | window | 4' 11" (1.50 m) | seg:1207, seg:1209, seg:1211, seg:1213 |
| real01_scan.png | run | window | 1' 11" (0.58 m) | seg:787, seg:797, seg:805, seg:811 |
| real01_scan.png | run | door | 2' 11" (0.88 m) | arc:22 |
| real01_scan.png | run | window | 4' 11" (1.49 m) | seg:35, seg:38, seg:41, seg:45, seg:46 |
| real01_scan.png | run | window | 4' 11" (1.50 m) | seg:36, seg:39, seg:42, seg:43 |
| real01_scan.png | run | window | 3' 11" (1.19 m) | seg:34, seg:37, seg:40, seg:44 |
| real01_scan.png | run | window | 3' 11" (1.19 m) | seg:818, seg:819, seg:820, seg:821 |
| real01_scan.png | run | window | 3' 11" (1.19 m) | seg:350, seg:351, seg:352, seg:353 |
| real01_scan.png | split | unclassified | 2' 7" (0.80 m) | - |
| real01_scan.png | split | door | 2' 10" (0.86 m) | arc:21, seg:630 |
| real01_scan.png | split | unclassified | 2' 9" (0.83 m) | - |
| real01_scan.png | split | unclassified | 2' 11" (0.89 m) | - |
| real01_scan.png | run | unclassified | 2' 8" (0.81 m) | - |
| real01_scan.png | run | empty | 5' 10" (1.78 m) | - |
| real01_scan.png | run | door | 3' 5" (1.03 m) | arc:42, seg:1174, seg:1177, seg:1178, seg:1182, seg:1184 (+6) |
| real01_scan.png | run | unclassified | 3' 2" (0.97 m) | - |
| real01_scan.png | run | empty | 5' 1" (1.56 m) | - |
| real01_scan.png | run | window | 3' 10" (1.18 m) | seg:318, seg:319, seg:326, seg:327 |
| real01_scan.png | end | door | 2' 2" (0.65 m) | arc:27, seg:815, seg:816 |
| real01_scan.png | end | door | 2' 9" (0.85 m) | arc:20, seg:635, seg:636, seg:637, seg:638, seg:640 (+1) |
| real01_scan.png | end | empty | 4' 2" (1.27 m) | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L0_001 | unknown | none (fits no size-table type) | - | yes | unverified |
| f_L0_002 | unknown | none (possible group of 4 pieces) | - | yes | unverified |
| f_L0_003 | unknown | none (possible group of 8 pieces) | - | yes | unverified |
| f_L0_004 | unknown | none (possible group of 6 pieces) | - | yes | unverified |
| f_L0_005 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_006 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_007 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_008 | unknown | none | pass 1: not_furniture; pass 2: not_furniture | no (drawn symbol, not built) | unverified |
| f_L0_009 | unknown | none | pass 1: unknown; pass 2: bed_double | yes | unverified |
| f_L0_010 | stair | ai_two_pass | pass 1: stair; pass 2: stair | yes | unverified |
| f_L0_011 | table_dining | ai_two_pass | pass 1: table_dining; pass 2: table_dining | yes | verified |
| f_L0_012 | sofa | ai_two_pass | pass 1: sofa; pass 2: sofa | yes | verified |
| f_L0_013 | unknown | none | pass 1: wardrobe; pass 2: sofa | yes | unverified |
| f_L0_014 | unknown | none | pass 1: unknown; pass 2: shower | yes | unverified |
| f_L0_015 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_016 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |
| f_L0_017 | unknown | none | pass 1: not_furniture; pass 2: not_furniture | no (drawn symbol, not built) | unverified |

Recognition questions: 19 (`recognition/requests.json`), 0 without a complete pair of answers.

## Assumed values

- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2.70 m (assumed_default)
- win_L0_001 (window): height 3' 11" (1.20 m)
- win_L0_001 (window): sill height 2' 11" (0.90 m)
- win_L0_002 (window): height 3' 11" (1.20 m)
- win_L0_002 (window): sill height 2' 11" (0.90 m)
- win_L0_003 (window): height 3' 11" (1.20 m)
- win_L0_003 (window): sill height 2' 11" (0.90 m)
- d_L0_001 (door): height 6' 11" (2.10 m)
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
- o_L0_001 (opening): height 6' 11" (2.10 m)
- d_L0_002 (door): height 6' 11" (2.10 m)
- o_L0_002 (opening): height 6' 11" (2.10 m)
- o_L0_003 (opening): height 6' 11" (2.10 m)
- o_L0_004 (opening): height 6' 11" (2.10 m)
- o_L0_005 (opening): height 6' 11" (2.10 m)
- d_L0_003 (door): height 6' 11" (2.10 m)
- o_L0_006 (opening): height 6' 11" (2.10 m)
- o_L0_007 (opening): height 6' 11" (2.10 m)
- win_L0_009 (window): height 3' 11" (1.20 m)
- win_L0_009 (window): sill height 2' 11" (0.90 m)
- d_L0_004 (door): height 6' 11" (2.10 m)
- d_L0_005 (door): height 6' 11" (2.10 m)

## Notes

### real01_scan.png p1

- image file
- deskew: rotated by -0.814 deg (dominant direction of 438 long strokes)
- length text '90"' read with confidence 0.00 < 0.85: not used
- length text '25' read with confidence 0.00 < 0.85: not used
- length text '0' read with confidence 0.00 < 0.85: not used
- 4 raster wall ends moved onto the wall face they stop short of by <= 1.5 px: wall 1 start +4 mm, wall 2 start +5 mm, wall 3 start +1 mm, wall 8 start +4 mm
- furniture size checks use the wenart/recognition/size_table.yaml
- 392 glyph strokes inside text boxes ignored
- 12 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- unknown piece 2.79 x 2.02 m at (5.95, 9.50): fits no size-table type
- unknown piece 0.21 x 0.14 m at (13.89, 6.76): possible group of 4 pieces
- unknown piece 0.21 x 0.17 m at (14.34, 8.76): possible group of 8 pieces
- unknown piece 0.14 x 0.21 m at (16.06, 6.66): possible group of 6 pieces
- unknown piece 0.13 x 0.21 m at (15.45, 8.76): possible group of 2 pieces
- unknown piece 0.07 x 0.23 m at (9.96, 6.88): possible group of 2 pieces
- unknown piece 0.07 x 0.23 m at (10.72, 6.88): possible group of 2 pieces
- 21 drawn details smaller than 0.2 m ignored
- 6 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: seg:642-643,seg:654,seg:658,seg:1175,seg:1189
- 8 site edge or boundary line groups outside the building (not decor)

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_009 | f_L0_009: sym_L0_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bed_double | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_type_disagreement | f_L0_013 | f_L0_013: sym_L0_006: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) wardrobe, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_003 | symbol_type_disagreement | f_L0_014 | f_L0_014: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) shower | unresolved: the drawn footprint is kept as unknown, unverified |

## Unverified

- d_L0_001
- o_L0_001
- o_L0_002
- o_L0_003
- o_L0_004
- o_L0_006
- r_L0_room
- f_L0_001
- f_L0_002
- f_L0_003
- f_L0_004
- f_L0_005
- f_L0_006
- f_L0_007
- f_L0_008
- f_L0_009
- f_L0_010
- f_L0_013
- f_L0_014
- f_L0_017

## Warnings

- level title missing: assumed L0 Ground floor
- real01_scan.png p1: scale from one dimension, corroborated by 8 room sizes
- sym_L0_001: both passes say not_furniture: kept as an obstacle, not built
- sym_L0_002: AI front [90.0, 270.0] disagrees with the drawn front 90: front unknown
- sym_L0_003: stair named by both passes, but the stair rule found no treads there: flights unknown, unverified
- sym_L0_005: AI front [180.0] disagrees with the drawn front 90: front unknown
- sym_L0_005: sofa without an agreed front: front unknown: width and depth follow the sofa size convention; the side the builder faces is assumed
- sym_L0_008: AI front [90.0, 270.0] disagrees with the drawn front 90: front unknown
- sym_L0_008: chair without an agreed front: front unknown: width and depth follow the chair size convention; the side the builder faces is assumed
- sym_L0_010: both passes say not_furniture: kept as an obstacle, not built
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- L0: room at (3.4589, 2.55) (6.78 m²) has no label: unlabelled face holding the stair
- r_L0_drawing_room: room label 'Drawing Room' (two VLM passes) where Tesseract read 'Drawing Room MI' on real01_scan.png: no word disagrees, the passes' spelling kept
- r_L0_bath_toilet: room label 'Bath+ Toilet' (two VLM passes) where Tesseract read 'Bath* Toilet' on real01_scan.png: no word disagrees, the passes' spelling kept
- d_L0_001: swing side (2.96, 3.53) lies in no room of L0
