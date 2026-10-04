# Ingest report: real01

Status: **ok**
Source: `projects/real01`, pipeline commit `714dcc50e`, created 2026-10-04T10:00:12Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| real01.pdf | 1 | floor_plan | vector | L0 | 0.0245111 m/unit (dimension_text) | 0.60 | - | debug/real01_pdf_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Ground floor (assumed) | 0 | 0.00 | 2.70 (assumed_default) | 13 | 18 | 9 | 20 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_bed_room | L0 | Bed Room | Bed Room | bedroom | 10,23 | - | yes | verified |
| r_L0_bath_toilet | L0 | Bath+ Toilet | Bath+ Toilet | bathroom | 3,25 | - | no | verified |
| r_L0_drawing_room | L0 | Drawing Room | Drawing Room | living | 18,31 | - | yes | verified |
| r_L0_room | L0 | Room | — | hall | 6,98 | - | yes | unverified |
| r_L0_pooja | L0 | Pooja | Pooja | prayer | 1,76 | - | no | verified |
| r_L0_store | L0 | Store | Store | storage | 1,86 | - | no | verified |
| r_L0_bed_room_2 | L0 | Bed Room | Bed Room | bedroom | 10,23 | - | yes | verified |
| r_L0_kitchen | L0 | Kitchen | Kitchen | kitchen | 8,82 | - | yes | verified |
| r_L0_dining | L0 | Dining | Dining | dining | 10,51 | - | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_kitchen | kitchen_counter | - | from_documents | 0.99 x 0.61 | 270 | verified | real01.pdf |
| f_L0_002 | L0 | r_L0_kitchen | kitchen_counter | - | from_documents | 2.57 x 0.61 | 0 | verified | real01.pdf |
| f_L0_003 | L0 | r_L0_room | stair | - | from_documents | 2.44 x 1.53 | 90 | verified | real01.pdf |
| f_L0_004 | L0 | r_L0_bed_room_2 | bed_double | - | from_documents | 1.78 x 2.03 | 0 | verified | real01.pdf |
| f_L0_005 | L0 | r_L0_bed_room_2 | nightstand | - | from_documents | 0.50 x 0.49 | 0 | verified | real01.pdf |
| f_L0_006 | L0 | r_L0_bed_room_2 | nightstand | - | from_documents | 0.45 x 0.50 | 270 | verified | real01.pdf |
| f_L0_007 | L0 | r_L0_bed_room | bed_double | - | from_documents | 1.78 x 2.03 | 180 | verified | real01.pdf |
| f_L0_008 | L0 | r_L0_bed_room | nightstand | - | from_documents | 0.50 x 0.49 | 0 | verified | real01.pdf |
| f_L0_009 | L0 | r_L0_bed_room | nightstand | - | from_documents | 0.50 x 0.45 | 0 | verified | real01.pdf |
| f_L0_010 | L0 | r_L0_dining | table_dining | - | from_documents | 1.24 x 0.74 | 90 | verified | real01.pdf |
| f_L0_011 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.46 | 180 | verified | real01.pdf |
| f_L0_012 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.46 | 0 | verified | real01.pdf |
| f_L0_013 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.46 | 90 | verified | real01.pdf |
| f_L0_014 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.46 | 90 | verified | real01.pdf |
| f_L0_015 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.46 | 270 | verified | real01.pdf |
| f_L0_016 | L0 | r_L0_dining | chair | - | from_documents | 0.38 x 0.46 | 270 | verified | real01.pdf |
| f_L0_017 | L0 | r_L0_drawing_room | sofa | - | from_documents | 1.89 x 0.71 | 180 | verified | real01.pdf |
| f_L0_018 | L0 | r_L0_drawing_room | unknown | - | from_documents | 1.90 x 0.70 | 270 | unverified | real01.pdf |
| f_L0_019 | L0 | r_L0_drawing_room | table_coffee | - | from_documents | 1.13 x 1.12 | 0 | verified | real01.pdf |
| f_L0_020 | L0 | r_L0_drawing_room | floor_lamp | - | from_documents | 0.42 x 0.42 | 79 | verified | real01.pdf |

## Units

Project unit system: **imperial** (lengths in feet and inches, metres in brackets)

| Document | Unit system | Source kind |
|---|---|---|
| real01.pdf | imperial | cad_pdf |

## Scale

**real01.pdf p1**: 0.0245111 m/unit, method `dimension_text`, confidence 0.85

| Dimension text | Printed | Measured (page units) | Measured | Ratio (m/unit) | Off | End marks |
|---|---|---|---|---|---|---|
| 30' | 30' 0" (9.14 m) | 373.08 | 30' 0" (9.14 m) | 0.0245095 | -0.01% | arrow / arrow (gap) |
| 50' | 50' 0" (15.24 m) | 621.72 | 50' 0" (15.24 m) | 0.0245126 | +0.01% | arrow / arrow (gap) |

| Room-size label | Printed | Measured (clear size) | Off | Status |
|---|---|---|---|---|
| Kitchen (9' 3" x 10' 3") | 9' 3" (2.82 m) x 10' 3" (3.12 m) | 9' 3" (2.82 m) x 10' 3" (3.12 m) | -0.1%, +0.0% | ok |
| Store (4' x 5') | 4' 0" (1.22 m) x 5' 0" (1.52 m) | 4' 0" (1.22 m) x 5' 0" (1.52 m) | +0.0%, +0.1% | ok |
| Pooja (4' x 4' 9") | 4' 0" (1.22 m) x 4' 9" (1.45 m) | 4' 0" (1.22 m) x 4' 9" (1.45 m) | +0.0%, +0.2% | ok |
| Drawing Room (14' x 14') | 14' 0" (4.27 m) x 14' 0" (4.27 m) | 14' 3" (4.34 m) x 14' 0" (4.27 m) | -1.7%, +0.0% | ok |
| Dining (14' x 8') | 14' 0" (4.27 m) x 8' 0" (2.44 m) | 14' 0" (4.27 m) x 8' 3" (2.51 m) | +0.0%, -3.0% | ok |
| Bath+ Toilet (7' x 5') | 7' 0" (2.13 m) x 5' 0" (1.52 m) | 7' 0" (2.13 m) x 5' 0" (1.53 m) | +0.1%, -0.1% | ok |
| Bed Room (11' x 10') | 11' 0" (3.35 m) x 10' 0" (3.05 m) | 11' 0" (3.35 m) x 10' 0" (3.05 m) | -0.1%, -0.1% | ok |
| Bed Room (11' x 10') | 11' 0" (3.35 m) x 10' 0" (3.05 m) | 11' 0" (3.35 m) x 10' 0" (3.05 m) | -0.1%, -0.1% | ok |

- real01.pdf p1: provisional scale from 2 dimension texts ('30'', '50'', 0.013% apart): 0.024511 m/unit; needs >= 2 room-size labels within 5%
- scale from 2 dimensions, corroborated by 8 room sizes

## Room size labels

| Room | Label size | Measured | Status |
|---|---|---|---|
| r_L0_bed_room | 11' x 10' | 11' 0" (3.35 m) x 10' 0" (3.05 m) | ok |
| r_L0_bath_toilet | 7' x 5' | 7' 0" (2.13 m) x 5' 0" (1.53 m) | ok |
| r_L0_drawing_room | 14' x 14' | 14' 3" (4.34 m) x 14' 0" (4.27 m) | ok |
| r_L0_pooja | 4' x 4' 9" | 4' 0" (1.22 m) x 4' 9" (1.45 m) | ok |
| r_L0_store | 4' x 5' | 4' 0" (1.22 m) x 5' 0" (1.52 m) | ok |
| r_L0_bed_room_2 | 11' x 10' | 11' 0" (3.35 m) x 10' 0" (3.05 m) | ok |
| r_L0_kitchen | 9' 3" x 10' 3" | 9' 3" (2.82 m) x 10' 3" (3.12 m) | ok |
| r_L0_dining | 14' x 8' | 14' 0" (4.27 m) x 8' 3" (2.52 m) | ok |

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sw_L0_001 | boundary wall (plot) | 50' 0" (15.24 m) long, 0' 6" (0.15 m) thick |
| sw_L0_002 | boundary wall (plot) | 50' 0" (15.24 m) long, 0' 6" (0.15 m) thick |
| sw_L0_003 | boundary wall (plot) | 29' 0" (8.85 m) long, 0' 6" (0.15 m) thick |
| sw_L0_004 | boundary wall (plot) | 17' 9" (5.41 m) long, 0' 6" (0.15 m) thick |
| sa_L0_parking | area 'Parking' | label size 11' 3" x 15' 3", measured 15' 6" (4.72 m) x 11' 3" (3.43 m) (unchecked), no closed outline |
| sd_L0_001 | decor (other) | 1' 7" (0.49 m) x 4' 6" (1.37 m) |
| sd_L0_002 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.40 m) |
| sd_L0_003 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.41 m) |
| sd_L0_004 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.40 m) |
| sd_L0_005 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.41 m) |
| sd_L0_006 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.41 m) |
| sd_L0_007 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.41 m) |
| sd_L0_008 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.41 m) |
| sd_L0_009 | decor (plant) | 1' 5" (0.42 m) x 1' 4" (0.41 m) |
| sd_L0_010 | decor (plant) | 1' 5" (0.43 m) x 1' 4" (0.41 m) |

## Separators

| Page | Kind | Length | Kept | Reason |
|---|---|---|---|---|
| real01.pdf p1 | end_to_wall | 4' 3" (1.29 m) | yes | two room names shared one face |

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| real01.pdf p1 | run | window | 5' 0" (1.52 m) | path:11612, path:11613, path:11614, path:11615, path:11616, path:11617 |
| real01.pdf p1 | run | window | 5' 0" (1.52 m) | path:11618, path:11619, path:11620, path:11621, path:36871, path:36872 |
| real01.pdf p1 | run | window | 2' 0" (0.61 m) | path:11622, path:11623, path:11624, path:11625 |
| real01.pdf p1 | run | window | 5' 0" (1.52 m) | path:11047, path:11050, path:11053, path:11056, path:11059, path:11062 (+5) |
| real01.pdf p1 | run | window | 5' 0" (1.52 m) | path:11605, path:11606, path:11607, path:11608, path:2516, path:2520 (+7) |
| real01.pdf p1 | run | window | 4' 0" (1.22 m) | path:11600, path:11601, path:11602, path:11603, path:36873, path:36874 (+1) |
| real01.pdf p1 | run | window | 4' 0" (1.22 m) | path:17127, path:17128, path:36867, path:36868, path:36869, path:9077 (+1) |
| real01.pdf p1 | run | window | 4' 0" (1.22 m) | path:17129, path:17130, path:17131, path:17132, path:6035, path:6041 (+8) |
| real01.pdf p1 | split | door | 3' 0" (0.92 m) | path:11558, path:11559, path:11560, path:11561, path:11562, path:11564 (+8) |
| real01.pdf p1 | split | door | 3' 0" (0.92 m) | path:11528, path:11571, path:11572, path:11573, path:11574, path:11575 (+11) |
| real01.pdf p1 | run | empty | 6' 0" (1.83 m) | path:11147, path:16605 |
| real01.pdf p1 | run | door | 3' 6" (1.06 m) | path:11497, path:11543, path:11544, path:11545, path:11546, path:11547 (+8) |
| real01.pdf p1 | run | empty | 3' 4" (1.02 m) | path:11502, path:11503, path:3611, path:9065, path:9068 |
| real01.pdf p1 | run | empty | 5' 3" (1.60 m) | path:11516, path:9070 |
| real01.pdf p1 | run | window | 4' 0" (1.22 m) | path:11514, path:11515, path:11597, path:11598, path:11599, path:36876 |
| real01.pdf p1 | end | door | 2' 6" (0.76 m) | path:11490, path:16606, path:16607, path:16608, path:16609, path:16610 (+5) |
| real01.pdf p1 | end | door | 3' 0" (0.91 m) | path:11584, path:11585, path:11586, path:11587, path:11588, path:11590 (+7) |
| real01.pdf p1 | end | empty | 4' 3" (1.29 m) | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L0_001 | kitchen_counter | rule (kitchen counter rule: chained legs between wall faces) | - | yes | verified |
| f_L0_002 | kitchen_counter | rule (kitchen counter rule: chained legs between wall faces) | - | yes | verified |
| f_L0_003 | stair | rule (stair rule: 2 flight(s), 8, 8 tread lines) | - | yes | verified |
| f_L0_004 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_005 | nightstand | ai_two_pass | pass 1: nightstand; pass 2: nightstand | yes | verified |
| f_L0_006 | nightstand | ai_two_pass | pass 1: nightstand; pass 2: nightstand | yes | verified |
| f_L0_007 | bed_double | ai_two_pass | pass 1: bed_double; pass 2: bed_double | yes | verified |
| f_L0_008 | nightstand | ai_two_pass | pass 1: nightstand; pass 2: nightstand | yes | verified |
| f_L0_009 | nightstand | ai_two_pass | pass 1: nightstand; pass 2: nightstand | yes | verified |
| f_L0_010 | table_dining | ai_two_pass | pass 1: table_dining; pass 2: table_dining | yes | verified |
| f_L0_011 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_012 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_013 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_014 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_015 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_016 | chair | ai_two_pass | pass 1: chair; pass 2: chair | yes | verified |
| f_L0_017 | sofa | ai_two_pass | pass 1: sofa; pass 2: sofa | yes | verified |
| f_L0_018 | unknown | none | pass 1: wardrobe; pass 2: sofa | yes | unverified |
| f_L0_019 | table_coffee | ai_two_pass | pass 1: table_coffee; pass 2: table_coffee | yes | verified |
| f_L0_020 | floor_lamp | ai_two_pass | pass 1: floor_lamp; pass 2: floor_lamp | yes | verified |

Recognition questions: 17 (`recognition/requests.json`), 0 without a complete pair of answers.

## Assumed values

- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2.70 m (assumed_default)
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
- d_L0_001 (door): height 6' 11" (2.10 m)
- d_L0_002 (door): height 6' 11" (2.10 m)
- o_L0_001 (opening): height 6' 11" (2.10 m)
- d_L0_003 (door): height 6' 11" (2.10 m)
- o_L0_002 (opening): height 6' 11" (2.10 m)
- o_L0_003 (opening): height 6' 11" (2.10 m)
- win_L0_009 (window): height 3' 11" (1.20 m)
- win_L0_009 (window): sill height 2' 11" (0.90 m)
- d_L0_004 (door): height 6' 11" (2.10 m)
- d_L0_005 (door): height 6' 11" (2.10 m)
- f_L0_003 (stair): direction, turn, void assumed (no UP arrow, break line or riser text drawn: rise direction and flight order are assumed; two side-by-side flights read as a U-turn (dog-leg) stair)

## Notes

### real01.pdf p1

- furniture size checks use the wenart/recognition/size_table.yaml
- 155 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- stair at (8.25, 9.18): 2 flight(s) of 0.761, 0.765 m
- 5 drawn details smaller than 0.2 m ignored
- 2 site edge or boundary line groups outside the building (not decor)

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_018 | f_L0_018: sym_L0_015: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) wardrobe, pass 2 (zai-org/GLM-4.6V-Flash) sofa | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_front_disagreement | f_L0_004 | f_L0_004: sym_L0_001: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_003 | symbol_front_disagreement | f_L0_007 | f_L0_007: sym_L0_004: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_004 | symbol_front_disagreement | f_L0_011 | f_L0_011: sym_L0_008: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_005 | symbol_front_disagreement | f_L0_012 | f_L0_012: sym_L0_009: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_006 | symbol_front_disagreement | f_L0_013 | f_L0_013: sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_007 | symbol_front_disagreement | f_L0_014 | f_L0_014: sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_008 | symbol_front_disagreement | f_L0_015 | f_L0_015: sym_L0_012: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_009 | symbol_front_disagreement | f_L0_016 | f_L0_016: sym_L0_013: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table) | the drawn front is kept (trust order: vector geometry > AI suggestions) |
| c_010 | symbol_front_disagreement | f_L0_017 | f_L0_017: sym_L0_014: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back) | the drawn front is kept (trust order: vector geometry > AI suggestions) |

## Unverified

- r_L0_room
- f_L0_018

## Warnings

- level title missing: assumed L0 Ground floor
- real01.pdf p1: scale from 2 dimensions, corroborated by 8 room sizes
- sym_L0_001: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes): the drawn front is kept (vector geometry > AI)
- sym_L0_002: nightstand without an agreed front: front unknown: width and depth follow the nightstand size convention; the side the builder faces is assumed
- sym_L0_004: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back; head = side with >= 2 small closed shapes): the drawn front is kept (vector geometry > AI)
- sym_L0_005: nightstand without an agreed front: front unknown: width and depth follow the nightstand size convention; the side the builder faces is assumed
- sym_L0_006: nightstand without an agreed front: front unknown: width and depth follow the nightstand size convention; the side the builder faces is assumed
- sym_L0_008: AI front [90.0, 270.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) bottom, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L0_009: AI front [90.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) top, pass 2 (zai-org/GLM-4.6V-Flash) top) disagrees with the drawn front 270 deg (only side within 0.25 m of a wall is the back; chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L0_010: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L0_011: AI front [0.0, 180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 0 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L0_012: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L0_013: AI front [0.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) right, pass 2 (zai-org/GLM-4.6V-Flash) right) disagrees with the drawn front 180 deg (chair faces the nearest table): the drawn front is kept (vector geometry > AI)
- sym_L0_014: AI front [180.0] (pass 1 (Qwen/Qwen3-VL-8B-Instruct) left, pass 2 (zai-org/GLM-4.6V-Flash) left) disagrees with the drawn front 90 deg (only side within 0.25 m of a wall is the back): the drawn front is kept (vector geometry > AI)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- L0: room at (3.43, 2.5165) (6.98 m²) has no label: unlabelled face holding the stair
