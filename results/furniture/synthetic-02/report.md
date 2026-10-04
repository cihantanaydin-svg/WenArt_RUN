# Ingest report: synthetic-02

Status: **ok**
Source: `projects/synthetic-02`, pipeline commit `2be169d6`, created 2026-10-04T00:08:18Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| plan_photo.jpg | 1 | floor_plan | photo | L0 | 0.0185148 m/unit (dimension_text) | 0.90 | - | debug/plan_photo_jpg_p1.png |
| plan_scan.png | 1 | floor_plan | scan | L0 | 0.0169518 m/unit (dimension_text) | 0.90 | - | debug/plan_scan_png_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Zemin Kat | 0 | 0.00 | 2.70 (assumed_default) | 7 | 11 | 5 | 16 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_salon | L0 | Salon | SALON | living | 16,14 | - | yes | verified |
| r_L0_yatak_odasi | L0 | Yatak Odası | YATAK ODASI | bedroom | 13,81 | - | yes | verified |
| r_L0_mutfak | L0 | Mutfak | MUTFAK | kitchen | 8,60 | - | yes | verified |
| r_L0_antre | L0 | Antre | ANTRE | hall | 3,21 | - | yes | verified |
| r_L0_banyo | L0 | Banyo | BANYO | bathroom | 3,86 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_yatak_odasi | unknown | - | from_documents | 2.09 x 2.05 | 0 | unverified | plan_scan.png |
| f_L0_002 | L0 | r_L0_salon | unknown | - | from_documents | 0.53 x 3.19 | 270 | unverified | plan_scan.png |
| f_L0_003 | L0 | r_L0_mutfak | kitchen_counter | - | from_documents | 2.46 x 0.66 | 0 | verified | plan_scan.png |
| f_L0_004 | L0 | r_L0_mutfak | unknown | - | from_documents | 1.64 x 0.95 | 180 | unverified | plan_scan.png |
| f_L0_005 | L0 | r_L0_salon | unknown | - | from_documents | 1.62 x 0.93 | 0 | unverified | plan_scan.png |
| f_L0_006 | L0 | r_L0_yatak_odasi | wardrobe | - | from_documents | 1.81 x 0.69 | 90 | verified | plan_scan.png |
| f_L0_007 | L0 | r_L0_yatak_odasi | unknown | - | from_documents | 1.42 x 0.76 | 90 | unverified | plan_scan.png |
| f_L0_008 | L0 | r_L0_banyo | shower | - | from_documents | 1.00 x 0.93 | 0 | verified | plan_scan.png |
| f_L0_009 | L0 | r_L0_salon | fridge | - | from_documents | 0.92 x 0.92 | 270 | unverified | plan_scan.png |
| f_L0_010 | L0 | r_L0_banyo | shower | - | from_documents | 0.79 x 0.83 | 90 | verified | plan_scan.png |
| f_L0_011 | L0 | r_L0_salon | table_coffee | - | from_documents | 1.03 x 0.63 | 0 | verified | plan_scan.png |
| f_L0_012 | L0 | r_L0_mutfak | unknown | - | from_documents | 0.70 x 0.73 | 0 | unverified | plan_scan.png |
| f_L0_013 | L0 | r_L0_banyo | unknown | - | from_documents | 0.72 x 0.68 | 90 | unverified | plan_scan.png |
| f_L0_014 | L0 | r_L0_antre | unknown | - | from_documents | 1.02 x 0.42 | 90 | unverified | plan_scan.png |
| f_L0_015 | L0 | r_L0_banyo | unknown | - | from_documents | 0.79 x 0.43 | 126 | unverified | plan_scan.png |
| f_L0_016 | L0 | r_L0_banyo | washbasin | - | from_documents | 0.39 x 0.76 | 270 | verified | plan_scan.png |

## Units

Project unit system: **metric**

| Document | Unit system | Source kind |
|---|---|---|
| plan_photo.jpg | metric | raster_photo |
| plan_scan.png | metric | raster_scan |

## Scale

**plan_photo.jpg**: 0.0185148 m/unit, method `dimension_text`, confidence 0.70

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 4,50 | 4,50 m | 244.00 | 4,52 m | 0.0184426 | -0.39% | tick / tick (parallel) |
| 3.90 | 3,90 m | 268.00 | 4,96 m | 0.0145523 | -21.40% | tick / tick (parallel) |
| 2,40 | 2,40 m | 129.63 | 2,40 m | 0.0185148 | +0.00% | extension / tick (parallel) |
| 6,60 | 6,60 m | 355.94 | 6,59 m | 0.0185427 | +0.15% | extension / tick (parallel) |
| 4,20 | 4,20 m | 225.00 | 4,17 m | 0.0186667 | +0.82% | tick / tick (parallel) |

- plan_photo.jpg p1: scale note 'ÖLÇEK 1/100' ignored: raster page without a verified pixel size
- plan_photo.jpg p1: scale from 4 of 5 agreeing dimension texts; disagreeing: '3.90' (-21.4%)

**plan_scan.png**: 0.0169518 m/unit, method `dimension_text`, confidence 0.90

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 4,50 | 4,50 m | 266.00 | 4,51 m | 0.0169173 | -0.20% | tick / tick (parallel) |
| 3,90 | 3,90 m | 229.97 | 3,90 m | 0.0169588 | +0.04% | tick / extension (parallel) |
| 8,40 | 8,40 m | 495.74 | 8,40 m | 0.0169443 | -0.04% | extension / extension (parallel) |
| 2,40 | 2,40 m | 141.08 | 2,39 m | 0.0170112 | +0.35% | extension / extension (parallel) |
| 6,60 | 6,60 m | 388.94 | 6,59 m | 0.0169691 | +0.10% | extension / extension (parallel) |
| 4,20 | 4,20 m | 247.87 | 4,20 m | 0.0169447 | -0.04% | extension / tick (parallel) |

- plan_scan.png p1: scale note 'OLCEK 1/100' ignored: raster page without a verified pixel size
- plan_scan.png p1: scale from 6 of 6 agreeing dimension texts

## Room size labels

None.

## Site

Recorded, not built.

None.

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| plan_scan.png | end_to_end | 7,85 m | no | longer than 2.4 m |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| plan_photo.jpg | split | closed | 0,02 m | - |
| plan_photo.jpg | split | closed | 0,01 m | - |
| plan_photo.jpg | run | closed | 0,02 m | - |
| plan_photo.jpg | split | closed | 0,02 m | - |
| plan_photo.jpg | split | closed | 0,01 m | - |
| plan_photo.jpg | continuous | door | 0,75 m | - |
| plan_photo.jpg | continuous | door | 0,81 m | - |
| plan_photo.jpg | continuous | door | 0,92 m | - |
| plan_photo.jpg | continuous | door | 0,78 m | - |
| plan_photo.jpg | continuous | window | 1,52 m | - |
| plan_photo.jpg | continuous | window | 1,78 m | - |
| plan_photo.jpg | continuous | window | 1,18 m | - |
| plan_photo.jpg | continuous | window | 0,63 m | - |
| plan_photo.jpg | continuous | window | 1,18 m | - |
| plan_scan.png | run | closed | 0,01 m | - |
| plan_scan.png | run | closed | 0,01 m | - |
| plan_scan.png | continuous | door | 0,88 m | - |
| plan_scan.png | continuous | door | 0,79 m | - |
| plan_scan.png | continuous | door | 0,88 m | - |
| plan_scan.png | continuous | door | 0,77 m | - |
| plan_scan.png | continuous | window | 1,76 m | - |
| plan_scan.png | continuous | window | 1,71 m | - |
| plan_scan.png | continuous | window | 0,76 m | - |
| plan_scan.png | continuous | window | 0,42 m | - |
| plan_scan.png | continuous | window | 1,71 m | - |
| plan_scan.png | continuous | window | 0,58 m | - |
| plan_scan.png | continuous | window | 1,20 m | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L0_001 | unknown | none | pass 1: unknown; pass 2: bed_double | yes | unverified |
| f_L0_002 | unknown | none | pass 1: unknown; pass 2: kitchen_counter | yes | unverified |
| f_L0_003 | kitchen_counter | ai_two_pass | pass 1: kitchen_counter; pass 2: kitchen_counter | yes | verified |
| f_L0_004 | unknown | none | pass 1: sofa; pass 2: table_dining | yes | unverified |
| f_L0_005 | unknown | none | pass 1: sofa; pass 2: table_dining | yes | unverified |
| f_L0_006 | wardrobe | ai_two_pass | pass 1: wardrobe; pass 2: wardrobe | yes | verified |
| f_L0_007 | unknown | none | pass 1: desk; pass 2: wardrobe | yes | unverified |
| f_L0_008 | shower | ai_two_pass | pass 1: shower; pass 2: shower | yes | verified |
| f_L0_009 | fridge | ai_two_pass | pass 1: fridge; pass 2: fridge | yes | unverified |
| f_L0_010 | shower | ai_two_pass | pass 1: shower; pass 2: shower | yes | verified |
| f_L0_011 | table_coffee | ai_two_pass | pass 1: table_coffee; pass 2: table_coffee | yes | verified |
| f_L0_012 | unknown | none | pass 1: fridge; pass 2: unknown | yes | unverified |
| f_L0_013 | unknown | none | pass 1: side_table; pass 2: fridge | yes | unverified |
| f_L0_014 | unknown | none | pass 1: not_furniture; pass 2: not_furniture | no (drawn symbol, not built) | unverified |
| f_L0_015 | unknown | none | pass 1: unknown; pass 2: stove | yes | unverified |
| f_L0_016 | washbasin | ai_two_pass | pass 1: washbasin; pass 2: washbasin | yes | verified |

Recognition questions: 21 (`recognition/requests.json`), 0 without a complete pair of answers.

## Assumed values

- plan_photo.jpg p1: photo aspect assumed: the page quad measures 1.3764 (width / height, side_ratio), snapped to the ISO (sqrt 2) sheet ratio 1.4142 (2.7 % off; no dimension groups to check it)
- L0: ceiling height 2.70 m (assumed_default)
- d_L0_001 (door): height 2,10 m
- d_L0_002 (door): height 2,10 m
- d_L0_003 (door): height 2,10 m
- d_L0_004 (door): height 2,10 m
- win_L0_001 (window): height 1,20 m
- win_L0_001 (window): sill height 0,90 m
- win_L0_002 (window): height 1,20 m
- win_L0_002 (window): sill height 0,90 m
- win_L0_003 (window): height 1,20 m
- win_L0_003 (window): sill height 0,90 m
- win_L0_004 (window): height 1,20 m
- win_L0_004 (window): sill height 0,90 m
- win_L0_005 (window): height 1,20 m
- win_L0_005 (window): sill height 0,90 m
- win_L0_006 (window): height 1,20 m
- win_L0_006 (window): sill height 0,90 m
- win_L0_007 (window): height 1,20 m
- win_L0_007 (window): sill height 0,90 m

## Notes

### plan_photo.jpg p1 (evidence-only page)

- image file
- page quad (33.5, 27.9), (2334.7, 104.1), (2332.3, 1693.1), (90.1, 1740.2)
- aspect measured 1.3764 (side_ratio; side ratio 1.3764)
- aspect snapped to ISO (sqrt 2) 1.4142 (2.7 % off): assumed
- deskew: rotated by -1.135 deg (dominant direction of 112 long strokes)
- length text '8' read with confidence 0.00 < 0.85: not used
- 2 raster wall ends moved onto the wall face they stop short of by <= 1.5 px: wall 4 start +0 mm, wall 5 start +1 mm
- furniture size checks use the wenart/recognition/size_table.yaml
- 19 glyph strokes inside text boxes ignored
- 92 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 2 drawn details smaller than 0.2 m ignored
- 3 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: seg:161,seg:202,seg:205
- 66 site edge or boundary line groups outside the building (not decor)
- 15 raster furniture candidates not asked (evidence-only raster page: no AI questions (§0)); they stay unknown, unverified

### plan_scan.png p1

- image file
- deskew: rotated by -1.140 deg (dominant direction of 113 long strokes)
- length text '8' read with confidence 0.52 < 0.85: not used
- 4 raster wall ends moved onto the wall face they stop short of by <= 1.5 px: wall 3 end +0 mm, wall 4 end +0 mm, wall 5 end +0 mm, wall 6 end +0 mm
- furniture size checks use the wenart/recognition/size_table.yaml
- 15 glyph strokes inside text boxes ignored
- 78 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 1 drawn details smaller than 0.2 m ignored
- 1 site edge or boundary line groups outside the building (not decor)

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_001 | f_L0_001: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) bed_double | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_type_disagreement | f_L0_002 | f_L0_002: sym_L0_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) kitchen_counter | unresolved: the drawn footprint is kept as unknown, unverified |
| c_003 | symbol_type_disagreement | f_L0_004 | f_L0_004: sym_L0_004: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sofa, pass 2 (zai-org/GLM-4.6V-Flash) table_dining | unresolved: the drawn footprint is kept as unknown, unverified |
| c_004 | symbol_type_disagreement | f_L0_005 | f_L0_005: sym_L0_005: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) sofa, pass 2 (zai-org/GLM-4.6V-Flash) table_dining | unresolved: the drawn footprint is kept as unknown, unverified |
| c_005 | symbol_type_disagreement | f_L0_007 | f_L0_007: sym_L0_007: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) desk, pass 2 (zai-org/GLM-4.6V-Flash) wardrobe | unresolved: the drawn footprint is kept as unknown, unverified |
| c_006 | symbol_type_disagreement | f_L0_012 | f_L0_012: sym_L0_012: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) fridge, pass 2 (zai-org/GLM-4.6V-Flash) unknown | unresolved: the drawn footprint is kept as unknown, unverified |
| c_007 | symbol_type_disagreement | f_L0_013 | f_L0_013: sym_L0_013: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) side_table, pass 2 (zai-org/GLM-4.6V-Flash) fridge | unresolved: the drawn footprint is kept as unknown, unverified |
| c_008 | symbol_type_disagreement | f_L0_015 | f_L0_015: sym_L0_015: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) stove | unresolved: the drawn footprint is kept as unknown, unverified |
| c_009 | raster_count_mismatch | win_L0_001, win_L0_002, win_L0_003, win_L0_004, win_L0_005, win_L0_006, win_L0_007 | Zemin Kat: plan_scan.png has 7 windows, the photo plan_photo.jpg shows 5 (more than 1 apart) | scan wins; the photo is evidence only |
| c_010 | symbol_front_disagreement | f_L0_004 | f_L0_004: sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_011 | symbol_front_disagreement | f_L0_012 | f_L0_012: sym_L0_012: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |

## Unverified

- f_L0_001
- f_L0_002
- f_L0_004
- f_L0_005
- f_L0_007
- f_L0_009
- f_L0_012
- f_L0_013
- f_L0_014
- f_L0_015

## Warnings

- plan_photo.jpg p1: photo aspect assumed: the page quad measures 1.3764 (width / height, side_ratio), snapped to the ISO (sqrt 2) sheet ratio 1.4142 (2.7 % off; no dimension groups to check it) (evidence-only page)
- sym_L0_003: kitchen_counter without an agreed front: front unknown: width and depth follow the kitchen_counter size convention; the side the builder faces is assumed
- sym_L0_004: AI front [180.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) bottom) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_009: fridge is not a type allowed in a living room: kept, unverified
- sym_L0_010: shower without an agreed front: front unknown: width and depth follow the shower size convention (footprint turned 90 deg); the side the builder faces is assumed
- sym_L0_012: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_014: both passes say not_furniture: kept as an obstacle, not built
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- r_L0_yatak_odasi: room label 'YATAK ODASI' (two VLM passes) where Tesseract read 'Li YATAK ODASI' on plan_scan.png: no word disagrees, the passes' spelling kept
- Zemin Kat: plan_photo.jpg (photo) is evidence only for plan_scan.png: 7 walls, 7 openings, 8 furniture pieces and 2 room names confirmed
- plan_photo.jpg (evidence only): dimension text 3.90 vs 4.96 m measured on the raster (21.4%)
