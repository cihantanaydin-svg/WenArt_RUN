# Ingest report: real01-photo

Status: **ok**
Source: `tests/fixtures/real01_raster/real01-photo`, pipeline commit `dd3449d4`, created 2026-10-04T02:50:00Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| real01_photo.jpg | 1 | floor_plan | photo | L0 | 0.012712 m/unit (dimension_text) | 0.50 | - | debug/real01_photo_jpg_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Ground floor (assumed) | 0 | 0.00 | 2.70 (assumed_default) | 20 | 19 | 9 | 21 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_bed_room | L0 | Bed Room | Bed Room | bedroom | 10,03 | - | yes | verified |
| r_L0_bath_toilet | L0 | Bath+ Toilet | Bath+ Toilet | bathroom | 3,15 | - | no | verified |
| r_L0_drawing_room | L0 | Drawing Room | Drawing Room | living | 18,11 | - | yes | verified |
| r_L0_room | L0 | Room | — | hall | 6,82 | - | yes | unverified |
| r_L0_pooja | L0 | Pooja | Pooja | prayer | 1,70 | - | no | verified |
| r_L0_store | L0 | Store | Store | storage | 1,80 | - | no | verified |
| r_L0_bed_room_2 | L0 | Bed Room | Bed Room | bedroom | 10,07 | - | yes | verified |
| r_L0_kitchen | L0 | Kitchen | Kitchen | kitchen | 8,65 | - | yes | verified |
| r_L0_dining | L0 | Dining | Dining | dining | 10,34 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_kitchen | unknown | - | from_documents | 0.23 x 0.17 | 57 | unverified | real01_photo.jpg |
| f_L0_002 | L0 | r_L0_bed_room_2 | unknown | - | from_documents | 0.34 x 0.11 | 90 | unverified | real01_photo.jpg |
| f_L0_003 | L0 | r_L0_dining | unknown | - | from_documents | 0.43 x 0.05 | 86 | unverified | real01_photo.jpg |
| f_L0_004 | L0 | r_L0_bed_room_2 | unknown | - | from_documents | 0.20 x 0.12 | 85 | unverified | real01_photo.jpg |
| f_L0_005 | L0 | r_L0_bed_room | unknown | - | from_documents | 0.23 x 0.09 | 90 | unverified | real01_photo.jpg |
| f_L0_006 | L0 | r_L0_bed_room_2 | unknown | - | from_documents | 0.23 x 0.07 | 90 | unverified | real01_photo.jpg |
| f_L0_007 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.23 x 0.07 | 90 | unverified | real01_photo.jpg |
| f_L0_008 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.21 x 0.07 | 90 | unverified | real01_photo.jpg |
| f_L0_009 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.22 x 0.06 | 87 | unverified | real01_photo.jpg |
| f_L0_010 | L0 | r_L0_bed_room | unknown | - | from_documents | 0.21 x 0.06 | 90 | unverified | real01_photo.jpg |
| f_L0_011 | L0 | r_L0_bed_room | unknown | - | from_documents | 0.21 x 0.06 | 90 | unverified | real01_photo.jpg |
| f_L0_012 | L0 | r_L0_bed_room | bed_double | - | from_documents | 2.34 x 2.06 | 0 | verified | real01_photo.jpg |
| f_L0_013 | L0 | r_L0_kitchen | unknown | - | from_documents | 2.96 x 0.91 | 152 | unverified | real01_photo.jpg |
| f_L0_014 | L0 | r_L0_room | stair | - | from_documents | 1.49 x 2.27 | 0 | unverified | real01_photo.jpg |
| f_L0_015 | L0 | r_L0_bed_room_2 | bed_double | - | from_documents | 1.65 x 1.82 | 90 | verified | real01_photo.jpg |
| f_L0_016 | L0 | r_L0_drawing_room | unknown | - | from_documents | 1.88 x 0.74 | 90 | unverified | real01_photo.jpg |
| f_L0_017 | L0 | r_L0_drawing_room | sofa | - | from_documents | 1.87 x 0.71 | 180 | verified | real01_photo.jpg |
| f_L0_018 | L0 | r_L0_drawing_room | unknown | - | from_documents | 0.85 x 0.85 | 90 | unverified | real01_photo.jpg |
| f_L0_019 | L0 | r_L0_dining | unknown | - | from_documents | 0.76 x 0.60 | 0 | unverified | real01_photo.jpg |
| f_L0_020 | L0 | r_L0_bed_room_2 | unknown | - | from_documents | 0.42 x 0.38 | 98 | unverified | real01_photo.jpg |
| f_L0_021 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.41 | 180 | verified | real01_photo.jpg |

## Units

Project unit system: **imperial** (lengths in feet and inches, metres in brackets)

| Document | Unit system | Source kind |
|---|---|---|
| real01_photo.jpg | imperial | raster_photo |

## Scale

**real01_photo.jpg**: 0.012712 m/unit, method `dimension_text`, confidence 0.70

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 50 | 50' 0" (15.24 m) | 1198.87 | 50' 0" (15.24 m) | 0.012712 | +0.00% | extension / extension (gap) |

| Room-size label | Printed | Measured (clear size) | Off | Status |
|---|---|---|---|---|
| Kitchen (9' 3" x 10' 3") | 9' 3" (2.82 m) x 10' 3" (3.12 m) | 9' 2" (2.79 m) x 10' 2" (3.10 m) | +1.0%, +0.8% | ok |
| Store (4' x 5') | 4' 0" (1.22 m) x 5' 0" (1.52 m) | 3' 11" (1.20 m) x 4' 11" (1.50 m) | +1.7%, +1.6% | ok |
| Pooja (4' x 4' 9") | 4' 0" (1.22 m) x 4' 9" (1.45 m) | 3' 11" (1.20 m) x 4' 8" (1.42 m) | +1.7%, +2.0% | ok |
| Drawing Room (14' x 14') | 14' 0" (4.27 m) x 14' 0" (4.27 m) | 14' 3" (4.33 m) x 13' 11" (4.24 m) | -1.6%, +0.6% | ok |
| Dining (14' x 8') | 14' 0" (4.27 m) x 8' 0" (2.44 m) | 13' 11" (4.24 m) x 8' 3" (2.50 m) | +0.6%, -2.6% | ok |
| Bath+ Toilet (7' x 5') | 7' 0" (2.13 m) x 5' 0" (1.52 m) | 6' 11" (2.10 m) x 4' 11" (1.50 m) | +1.5%, +1.7% | ok |
| Bed Room (11' x 10') | 11' 0" (3.35 m) x 10' 0" (3.05 m) | 10' 11" (3.33 m) x 9' 11" (3.03 m) | +0.6%, +0.7% | ok |
| Bed Room (11' x 10') | 11' 0" (3.35 m) x 10' 0" (3.05 m) | 10' 11" (3.33 m) x 9' 11" (3.03 m) | +0.7%, +0.7% | ok |

- real01_photo.jpg p1: provisional scale from 1 dimension text ('50'): 0.012712 m/unit; needs >= 3 room-size labels within 5%
- scale from one dimension, corroborated by 8 room sizes

## Room size labels

| Room | Label size | Measured | Status |
|---|---|---|---|
| r_L0_bed_room | 11' x 10' | 10' 11" (3.33 m) x 9' 11" (3.03 m) | ok |
| r_L0_bath_toilet | 7' x 5' | 6' 11" (2.10 m) x 4' 11" (1.50 m) | ok |
| r_L0_drawing_room | 14' x 14' | 14' 3" (4.34 m) x 13' 11" (4.24 m) | ok |
| r_L0_pooja | 4' x 4' 9" | 3' 11" (1.20 m) x 4' 8" (1.42 m) | ok |
| r_L0_store | 4' x 5' | 3' 11" (1.20 m) x 4' 11" (1.50 m) | ok |
| r_L0_bed_room_2 | 11' x 10' | 10' 11" (3.33 m) x 9' 11" (3.03 m) | ok |
| r_L0_kitchen | 9' 3" x 10' 3" | 9' 2" (2.79 m) x 10' 2" (3.10 m) | ok |
| r_L0_dining | 14' x 8' | 13' 11" (4.24 m) x 8' 3" (2.50 m) | ok |

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sw_L0_001 | boundary wall (other) | 1' 7" (0.48 m) long, 0' 4" (0.10 m) thick |
| sw_L0_002 | boundary wall (plot) | 50' 2" (15.29 m) long, 0' 7" (0.18 m) thick |
| sw_L0_003 | boundary wall (plot) | 50' 1" (15.27 m) long, 0' 7" (0.19 m) thick |
| sw_L0_004 | boundary wall (plot) | 28' 11" (8.82 m) long, 0' 7" (0.18 m) thick |
| sw_L0_005 | boundary wall (plot) | 17' 9" (5.41 m) long, 0' 7" (0.18 m) thick |
| sa_L0_parking | area 'Parking' | label size -, measured - (-), no closed outline |
| sd_L0_001 | decor (other) | 10' 5" (3.17 m) x 1' 2" (0.35 m) |
| sd_L0_002 | decor (other) | 1' 7" (0.47 m) x 4' 8" (1.41 m) |
| sd_L0_003 | decor (other) | 3' 9" (1.14 m) x 14' 4" (4.37 m) |
| sd_L0_004 | decor (other) | 0' 9" (0.23 m) x 0' 10" (0.26 m) |
| sd_L0_005 | decor (other) | 1' 2" (0.34 m) x 0' 3" (0.08 m) |
| sd_L0_006 | decor (other) | 0' 9" (0.22 m) x 1' 0" (0.31 m) |
| sd_L0_007 | decor (other) | 3' 8" (1.13 m) x 14' 4" (4.37 m) |
| sd_L0_008 | decor (other) | 0' 6" (0.15 m) x 1' 1" (0.32 m) |
| sd_L0_009 | decor (other) | 8' 10" (2.69 m) x 0' 10" (0.26 m) |

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| real01_photo.jpg | end_to_wall | 4' 1" (1.25 m) | yes | two room names shared one face |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| real01_photo.jpg | run | window | 4' 9" (1.46 m) | seg:1030, seg:1032, seg:1036, seg:1037, seg:1042 |
| real01_photo.jpg | run | window | 4' 11" (1.50 m) | seg:1031, seg:1033, seg:1038, seg:1043 |
| real01_photo.jpg | run | window | 1' 10" (0.57 m) | seg:647, seg:656, seg:675, seg:684 |
| real01_photo.jpg | run | unclassified | 2' 7" (0.78 m) | - |
| real01_photo.jpg | run | window | 4' 11" (1.50 m) | seg:113, seg:115, seg:116, seg:119, seg:122, seg:127 |
| real01_photo.jpg | run | window | 4' 11" (1.49 m) | seg:117, seg:120, seg:123, seg:125 |
| real01_photo.jpg | run | window | 3' 10" (1.18 m) | seg:118, seg:121, seg:124, seg:126 |
| real01_photo.jpg | run | window | 3' 11" (1.19 m) | seg:695, seg:697, seg:698, seg:699 |
| real01_photo.jpg | run | window | 3' 11" (1.20 m) | seg:368, seg:370, seg:371, seg:372, seg:529, seg:530 (+2) |
| real01_photo.jpg | split | door | 2' 8" (0.82 m) | arc:26, seg:584, seg:674 |
| real01_photo.jpg | split | door | 2' 9" (0.84 m) | arc:22, seg:573 |
| real01_photo.jpg | run | empty | 5' 10" (1.78 m) | seg:538 |
| real01_photo.jpg | run | door | 3' 4" (1.02 m) | arc:43, seg:1012, seg:1020, seg:773, seg:774 |
| real01_photo.jpg | run | empty | 3' 3" (0.98 m) | - |
| real01_photo.jpg | run | empty | 5' 1" (1.56 m) | - |
| real01_photo.jpg | run | window | 3' 10" (1.18 m) | seg:347, seg:348, seg:350, seg:351, seg:435 |
| real01_photo.jpg | end | door | 2' 3" (0.69 m) | arc:32, seg:694 |
| real01_photo.jpg | end | door | 2' 11" (0.88 m) | arc:20, seg:550, seg:551, seg:553, seg:558, seg:559 |
| real01_photo.jpg | end | empty | 4' 1" (1.25 m) | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L0_001 | unknown | none (possible group of 6 pieces) | - | yes | unverified |
| f_L0_002 | unknown | none (possible group of 6 pieces) | - | yes | unverified |
| f_L0_003 | unknown | none (fits no size-table type) | - | yes | unverified |
| f_L0_004 | unknown | none (fits no size-table type) | - | yes | unverified |
| f_L0_005 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_006 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_007 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_008 | unknown | none (possible group of 5 pieces) | - | yes | unverified |
| f_L0_009 | unknown | none (possible group of 4 pieces) | - | yes | unverified |
| f_L0_010 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_011 | unknown | none (possible group of 2 pieces) | - | yes | unverified |
| f_L0_012 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_013 | unknown | none | pass 1: not_furniture; pass 2: not_furniture | no (drawn symbol, not built) | unverified |
| f_L0_014 | stair | ai_two_pass | pass 1: stair; pass 2: stair | yes | unverified |
| f_L0_015 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_016 | unknown | none | pass 1: wardrobe; pass 2: sofa | yes | unverified |
| f_L0_017 | sofa | ai_two_pass | pass 1: sofa; pass 2: sofa | yes | verified |
| f_L0_018 | unknown | none | pass 1: unknown; pass 2: unknown | yes | unverified |
| f_L0_019 | unknown | none | pass 1: side_table; pass 2: potted_plant | yes | unverified |
| f_L0_020 | unknown | none | pass 1: nightstand; pass 2: floor_lamp | yes | unverified |
| f_L0_021 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |

Recognition questions: 19 (`recognition/requests.json`), 0 without a complete pair of answers.

## Assumed values

- real01_photo.jpg p1: photo aspect assumed: the page quad measures 1.4050 (width / height, side_ratio), snapped to the ISO (sqrt 2) sheet ratio 1.4142 (0.7 % off; no dimension groups to check it)
- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2.70 m (assumed_default)
- win_L0_001 (window): height 3' 11" (1.20 m)
- win_L0_001 (window): sill height 2' 11" (0.90 m)
- win_L0_002 (window): height 3' 11" (1.20 m)
- win_L0_002 (window): sill height 2' 11" (0.90 m)
- win_L0_003 (window): height 3' 11" (1.20 m)
- win_L0_003 (window): sill height 2' 11" (0.90 m)
- o_L0_001 (opening): height 6' 11" (2.10 m)
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
- d_L0_001 (door): height 6' 11" (2.10 m)
- d_L0_002 (door): height 6' 11" (2.10 m)
- o_L0_002 (opening): height 6' 11" (2.10 m)
- d_L0_003 (door): height 6' 11" (2.10 m)
- o_L0_003 (opening): height 6' 11" (2.10 m)
- o_L0_004 (opening): height 6' 11" (2.10 m)
- win_L0_009 (window): height 3' 11" (1.20 m)
- win_L0_009 (window): sill height 2' 11" (0.90 m)
- d_L0_004 (door): height 6' 11" (2.10 m)
- d_L0_005 (door): height 6' 11" (2.10 m)

## Notes

### real01_photo.jpg p1

- image file
- page quad (58.1, 26.7), (1723.0, 36.1), (1686.3, 1177.9), (102.7, 1195.7)
- aspect measured 1.4050 (side_ratio; side ratio 1.4050)
- aspect snapped to ISO (sqrt 2) 1.4142 (0.7 % off): assumed
- deskew: rotated by -0.758 deg (dominant direction of 421 long strokes)
- length text '1' read with confidence 0.00 < 0.85: not used
- length text '4' read with confidence 0.00 < 0.85: not used
- length text '7' read with confidence 0.00 < 0.85: not used
- length text '28' read with confidence 0.70 < 0.85: not used
- length text '25' read with confidence 0.73 < 0.85: not used
- wall 18: a 0.050 m strip along one face over 0.81 m, where the leaf of door swing arc:32 rests (a leaf fused to the wall face in the wall mask), is not counted as wall: thickness 0.180 m as the rest of the run, not 0.240 m
- wall 7: a 0.040 m piece (0.140 m thick) at the end of a 0.190 m wall is a frame or nub of that wall's end, not a wall end of its own (no gap is cast from or to it)
- wall 19: a 0.030 m piece (0.140 m thick) at the end of a 0.250 m wall is a frame or nub of that wall's end, not a wall end of its own (no gap is cast from or to it)
- wall 20: a 0.040 m piece (0.110 m thick) at the end of a 0.250 m wall is a frame or nub of that wall's end, not a wall end of its own (no gap is cast from or to it)
- 8 raster wall ends moved onto the wall face they stop short of by <= 1.5 px: wall 14 end +0 mm, wall 17 start +1 mm, wall 17 end +0 mm, wall 18 start +1 mm, wall 18 end +0 mm, wall 21 start +1 mm, wall 21 end +0 mm, wall 23 end +0 mm
- furniture size checks use the wenart/recognition/size_table.yaml
- 327 glyph strokes inside text boxes ignored
- 17 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- unknown piece 0.23 x 0.17 m at (14.34, 8.78): possible group of 6 pieces
- unknown piece 0.11 x 0.34 m at (5.96, 10.35): possible group of 6 pieces
- unknown piece 0.43 x 0.05 m at (11.03, 9.39): fits no size-table type
- unknown piece 0.20 x 0.12 m at (6.11, 7.71): fits no size-table type
- unknown piece 0.09 x 0.23 m at (5.27, 6.17): possible group of 2 pieces
- unknown piece 0.07 x 0.23 m at (5.92, 7.71): possible group of 2 pieces
- unknown piece 0.07 x 0.23 m at (10.72, 6.90): possible group of 2 pieces
- unknown piece 0.07 x 0.21 m at (10.15, 6.90): possible group of 5 pieces
- unknown piece 0.22 x 0.06 m at (10.91, 6.87): possible group of 4 pieces
- unknown piece 0.06 x 0.21 m at (6.03, 6.18): possible group of 2 pieces
- unknown piece 0.06 x 0.21 m at (5.46, 6.18): possible group of 2 pieces
- 28 drawn details smaller than 0.2 m ignored
- 5 line details (minimum rectangle thinner than 0.05 m: single lines, not furniture) ignored: seg:186,seg:542,seg:575,seg:581,seg:1009
- 27 site edge or boundary line groups outside the building (not decor)

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_016 | f_L0_016: sym_L0_005: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) wardrobe, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_type_disagreement | f_L0_019 | f_L0_019: sym_L0_008: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) side_table, pass 2 (zai-org/GLM-4.6V-Flash) potted_plant | unresolved: the drawn footprint is kept as unknown, unverified |
| c_003 | symbol_type_disagreement | f_L0_020 | f_L0_020: sym_L0_009: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) nightstand, pass 2 (zai-org/GLM-4.6V-Flash) floor_lamp | unresolved: the drawn footprint is kept as unknown, unverified |
| c_004 | symbol_front_disagreement | f_L0_017 | f_L0_017: sym_L0_006: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_005 | symbol_front_disagreement | f_L0_019 | f_L0_019: sym_L0_008: AI front [90.0] (pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_006 | symbol_front_disagreement | f_L0_021 | f_L0_021: sym_L0_010: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |

## Unverified

- o_L0_001
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
- f_L0_011
- f_L0_013
- f_L0_014
- f_L0_016
- f_L0_018
- f_L0_019
- f_L0_020

## Warnings

- level title missing: assumed L0 Ground floor
- real01_photo.jpg p1: wall component without room labels at (17.39, 0.28) m (0.48 x 0.10 m) is not part of the building: recorded in site, not built
- real01_photo.jpg p1: scale from one dimension, corroborated by 8 room sizes
- sym_L0_001: bed_double without an agreed front: front unknown: width and depth follow the bed_double size convention; the side the builder faces is assumed
- sym_L0_002: both passes say not_furniture: kept as an obstacle, not built
- sym_L0_003: stair named by both passes, but the stair rule found no treads there: flights unknown, unverified
- sym_L0_003: stair without an agreed front: front unknown: width and depth follow the stair size convention (footprint turned 90 deg); the side the builder faces is assumed
- sym_L0_004: bed_double without an agreed front: front unknown: width and depth follow the bed_double size convention (footprint turned 90 deg); the side the builder faces is assumed
- sym_L0_006: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_007: both passes say unknown: type left open
- sym_L0_008: AI front [90.0] (pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- sym_L0_010: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- real01_photo.jpg p1: photo aspect assumed: the page quad measures 1.4050 (width / height, side_ratio), snapped to the ISO (sqrt 2) sheet ratio 1.4142 (0.7 % off; no dimension groups to check it)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- L0: room at (3.47, 2.5514) (6.82 m²) has no label: unlabelled face holding the stair
