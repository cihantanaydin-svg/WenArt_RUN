# Ingest report: real03

Status: **ok**
Source: `projects/real03`, pipeline commit `87831c156`, created 2026-10-10T10:52:18Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| tekkat.dwg | 1 | floor_plan | vector | L0 | 0.01 m/unit (dxf_insunits) | 0.60 | - | debug/tekkat_dwg_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Ground floor (assumed) | 0 | 0.00 | 2.70 (assumed_default) | 30 | 4 | 5 | 3 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|
| r_L0_ruzgarlik | L0 | Rüzgarlık | RÜZGARLIK | other | 9,64 | 9,64 | no | verified |
| r_L0_kat_holu | L0 | Kat Holü | KAT HOLÜ | hall | 46,94 | 46,94 | yes | verified |
| r_L0_guvenlik_holu | L0 | Güvenlik Holü | GÜVENLİK HOLÜ | hall | 3,38 | 3,38 | no | verified |
| r_L0_yangin_merdiveni | L0 | Yangın Merdiveni | YANGIN MERDİVENİ | other | 14,17 | 14,17 | yes | verified |
| r_L0_kat_merdiveni | L0 | Kat Merdiveni | KAT MERDİVENİ | other | 14,17 | 14,17 | yes | verified |

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | L0 | r_L0_yangin_merdiveni | kitchen_counter | - | from_documents | 2.60 x 0.55 | 0 | unverified | tekkat.dwg |
| f_L0_002 | L0 | r_L0_kat_merdiveni | kitchen_island | - | from_documents | 2.60 x 0.55 | 0 | unverified | tekkat.dwg |
| f_L0_003 | L0 | r_L0_kat_holu | unknown | - | from_documents | 0.90 x 0.34 | 167 | unverified | tekkat.dwg |

## Inferred (Milestone 11)

Walls inferred from room outlines: 30 (the documents do not draw them; evidence method inferred, status unverified).

| Wall | Level | Start | End | Thickness | Outlines | Reason |
|---|---|---|---|---|---|---|
| w_L0_001 | L0 | (10.00, 0.12) | (13.16, 0.12) | 0.250 | INSERT:7C9C9/13 | inferred from the labelled room outlines (outer wall along a room outline: 'RÜZGARLIK'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_002 | L0 | (9.90, 0.42) | (10.25, 0.42) | 0.260 | INSERT:7C9C9/13 | inferred from the labelled room outlines (outer wall along a room outline: 'RÜZGARLIK'); thickness 0.260 m (assumed); the drawn walls do not close |
| w_L0_003 | L0 | (9.90, 3.33) | (13.16, 3.33) | 0.150 | INSERT:7C9C9/25,INSERT:7C9C9/13 | inferred from the labelled room outlines (inner wall between two room outlines: 'KAT HOLÜ', 'RÜZGARLIK'); thickness 0.150 m = the gap between the outlines; the drawn walls do not close |
| w_L0_004 | L0 | (9.90, 5.38) | (9.95, 5.38) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_005 | L0 | (0.00, 5.97) | (10.20, 5.97) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_006 | L0 | (13.15, 5.97) | (26.20, 5.97) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_007 | L0 | (0.00, 7.62) | (3.35, 7.62) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_008 | L0 | (3.35, 7.58) | (6.21, 7.58) | 0.150 | INSERT:7C9C9/59,INSERT:7C9C9/25 | inferred from the labelled room outlines (inner wall between two room outlines: 'GÜVENLİK HOLÜ', 'KAT HOLÜ'); thickness 0.150 m = the gap between the outlines; the drawn walls do not close |
| w_L0_009 | L0 | (6.21, 7.62) | (10.75, 7.62) | 0.250 | INSERT:7C9C9/59,INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_010 | L0 | (10.75, 7.70) | (11.00, 7.70) | 0.400 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.400 m (assumed); the drawn walls do not close |
| w_L0_011 | L0 | (15.21, 7.70) | (15.46, 7.70) | 0.400 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.400 m (assumed); the drawn walls do not close |
| w_L0_012 | L0 | (15.46, 7.62) | (21.35, 7.62) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_013 | L0 | (22.85, 7.62) | (26.20, 7.62) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_014 | L0 | (11.00, 7.78) | (15.21, 7.78) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_015 | L0 | (20.00, 8.97) | (21.35, 8.97) | 0.250 | INSERT:7C9C9/60,INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_016 | L0 | (3.60, 9.03) | (6.21, 9.03) | 0.150 | INSERT:7C9C9/58,INSERT:7C9C9/59 | inferred from the labelled room outlines (inner wall between two room outlines: 'YANGIN MERDİVENİ', 'GÜVENLİK HOLÜ'); thickness 0.150 m = the gap between the outlines; the drawn walls do not close |
| w_L0_017 | L0 | (21.35, 9.03) | (22.61, 9.03) | 0.150 | INSERT:7C9C9/60,INSERT:7C9C9/25 | inferred from the labelled room outlines (inner wall between two room outlines: 'KAT MERDİVENİ', 'KAT HOLÜ'); thickness 0.150 m = the gap between the outlines; the drawn walls do not close |
| w_L0_018 | L0 | (3.60, 14.68) | (6.21, 14.68) | 0.250 | INSERT:7C9C9/58 | inferred from the labelled room outlines (outer wall along a room outline: 'YANGIN MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_019 | L0 | (20.00, 14.68) | (22.61, 14.68) | 0.250 | INSERT:7C9C9/60 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_020 | L0 | (13.28, 0.00) | (13.28, 5.85) | 0.250 | INSERT:7C9C9/25,INSERT:7C9C9/13 | inferred from the labelled room outlines (outer wall along a room outline: 'RÜZGARLIK'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_021 | L0 | (10.12, 0.24) | (10.12, 0.29) | 0.250 | INSERT:7C9C9/13 | inferred from the labelled room outlines (outer wall along a room outline: 'RÜZGARLIK'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_022 | L0 | (9.78, 0.30) | (9.78, 5.50) | 0.250 | INSERT:7C9C9/25,INSERT:7C9C9/13 | inferred from the labelled room outlines (outer wall along a room outline: 'RÜZGARLIK'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_023 | L0 | (10.07, 5.25) | (10.07, 5.85) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_024 | L0 | (0.12, 6.09) | (0.12, 7.50) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_025 | L0 | (26.07, 6.09) | (26.07, 7.50) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_026 | L0 | (22.73, 7.50) | (22.73, 14.80) | 0.250 | INSERT:7C9C9/60,INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_027 | L0 | (3.48, 7.65) | (3.48, 14.80) | 0.250 | INSERT:7C9C9/58,INSERT:7C9C9/59 | inferred from the labelled room outlines (outer wall along a room outline: 'YANGIN MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_028 | L0 | (6.33, 7.75) | (6.33, 14.80) | 0.250 | INSERT:7C9C9/58,INSERT:7C9C9/59 | inferred from the labelled room outlines (outer wall along a room outline: 'YANGIN MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_029 | L0 | (21.23, 7.75) | (21.23, 8.85) | 0.250 | INSERT:7C9C9/25 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT HOLÜ'); thickness 0.250 m (assumed); the drawn walls do not close |
| w_L0_030 | L0 | (19.88, 8.85) | (19.88, 14.80) | 0.250 | INSERT:7C9C9/60 | inferred from the labelled room outlines (outer wall along a room outline: 'KAT MERDİVENİ'); thickness 0.250 m (assumed); the drawn walls do not close |

Pieces whose type, front or role the documents left unclear; inferred by code (the agent may change them on the plan crop).

| Piece | Room | Type | Front | Built | Reason |
|---|---|---|---|---|---|
| f_L0_001 | r_L0_yangin_merdiveni | kitchen_counter | - | yes | kitchen_counter: named by an AI pass and the only named type that fits the size (2.60 x 0.55 m), the other room and the position (others fitting: kitchen_island, sideboard, tv_unit, wardrobe) |
| f_L0_002 | r_L0_kat_merdiveni | kitchen_island | - | yes | kitchen_island: named by an AI pass and the only named type that fits the size (2.60 x 0.55 m), the other room and the position (others fitting: kitchen_counter, sideboard, tv_unit, wardrobe) |

## Units

Project unit system: **metric**

| Document | Unit system | Source kind |
|---|---|---|
| tekkat.dwg | metric | dxf |

## Scale

**tekkat.dwg**: 0.01 m/unit, method `dxf_insunits`, confidence 1.00

- tekkat.dwg p1: drawing units known (0.01 m per unit)

## Room size labels

None.

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sd_L0_001 | decor (other) | 3,25 m x 1,00 m |
| sd_L0_002 | decor (other) | 0,42 m x 0,86 m |
| sd_L0_003 | decor (other) | 3,25 m x 1,00 m |
| sd_L0_004 | decor (other) | 1,00 m x 3,25 m |
| sd_L0_005 | decor (other) | 0,86 m x 0,42 m |
| sd_L0_006 | decor (other) | 0,86 m x 0,42 m |
| sd_L0_007 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_008 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_009 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_010 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_011 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_012 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_013 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_014 | decor (other) | 0,49 m x 0,49 m |
| sd_L0_015 | decor (other) | 0,42 m x 0,86 m |
| sd_L0_016 | decor (other) | 1,00 m x 3,25 m |

## Separators

None considered.

## Gaps

| Page | Kind | Class | Width | Owned strokes |
|---|---|---|---|---|
| tekkat.dwg | continuous | door | 0,90 m | - |
| tekkat.dwg | continuous | door | 0,90 m | - |
| tekkat.dwg | continuous | door | 0,90 m | - |
| tekkat.dwg | continuous | door | 0,90 m | - |

## Furniture typing

| Piece | Type | Method | Candidates | Build | Status |
|---|---|---|---|---|---|
| f_L0_001 | kitchen_counter | none | pass 1: unknown; pass 2: kitchen_counter | yes | unverified |
| f_L0_002 | kitchen_island | none | pass 1: unknown; pass 2: kitchen_island | yes | unverified |
| f_L0_003 | unknown | none | pass 1: unknown; pass 2: console_table | yes | unverified |

Recognition questions: 3 (`recognition/requests.json`), 0 without a complete pair of answers.

## Assumed values

- L0: level 'Ground floor' assumed (no level title on the page)
- L0: ceiling height 2.70 m (assumed_default)
- d_L0_001 (door): height 2,10 m
- d_L0_002 (door): height 2,10 m
- d_L0_003 (door): height 2,10 m
- d_L0_004 (door): height 2,10 m

## Notes

### tekkat.dwg

- sheet frame block INSERT:7C135 (*U62, layer MYD - LEJAND): 29 strokes (frame and title block at the frame edge) are not plan geometry
- room outlines used for the inferred walls: 'YANGIN MERDİVENİ' INSERT:7C9C9/58 (14.17 m², printed 14.17 m²); 'KAT MERDİVENİ' INSERT:7C9C9/60 (14.17 m², printed 14.17 m²); 'GÜVENLİK HOLÜ' INSERT:7C9C9/59 (3.38 m², printed 3.38 m²); 'KAT HOLÜ' INSERT:7C9C9/25 (46.94 m², printed 46.94 m²); 'RÜZGARLIK' INSERT:7C9C9/13 (9.64 m², printed 9.64 m²)
- inferred walls: 8 inferred wall ends moved onto the perpendicular wall face they stopped short of by <= 1.5 mask pixels
- 4 drawn door/window symbols read on the inferred walls
- furniture size checks use the wenart/recognition/size_table.yaml
- 153 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 24 sides of outlines larger than 4.5 m both ways are no furniture: INSERT:7C9C9/0/0,INSERT:7C9C9/0/1,INSERT:7C9C9/0/2,INSERT:7C9C9/24/2/0,INSERT:7C9C9/24/2/1,INSERT:7C9C9/24/2/2
- 2 straight strokes longer than 4.5 m that cross the building outline are no furniture: INSERT:7C9C9/24/0/0,INSERT:7C9C9/24/1/0

## Conflicts

| Id | Kind | Elements | Description | Resolution |
|---|---|---|---|---|
| c_001 | symbol_type_disagreement | f_L0_001 | f_L0_001: sym_L0_001: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) kitchen_counter | unresolved: the drawn footprint is kept as unknown, unverified |
| c_002 | symbol_type_disagreement | f_L0_002 | f_L0_002: sym_L0_002: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) kitchen_island | unresolved: the drawn footprint is kept as unknown, unverified |
| c_003 | symbol_type_disagreement | f_L0_003 | f_L0_003: sym_L0_003: the passes disagree: pass 1 (Qwen/Qwen3-VL-8B-Instruct) unknown, pass 2 (zai-org/GLM-4.6V-Flash) console_table | unresolved: the drawn footprint is kept as unknown, unverified |

## Unverified

- w_L0_001
- w_L0_002
- w_L0_003
- w_L0_004
- w_L0_005
- w_L0_006
- w_L0_007
- w_L0_008
- w_L0_009
- w_L0_010
- w_L0_011
- w_L0_012
- w_L0_013
- w_L0_014
- w_L0_015
- w_L0_016
- w_L0_017
- w_L0_018
- w_L0_019
- w_L0_020
- w_L0_021
- w_L0_022
- w_L0_023
- w_L0_024
- w_L0_025
- w_L0_026
- w_L0_027
- w_L0_028
- w_L0_029
- w_L0_030
- f_L0_001
- f_L0_002
- f_L0_003

## Warnings

- level title missing: assumed L0 Ground floor
- tekkat.dwg: 30 entities on layers that are off or frozen (or invisible) were not read
- tekkat.dwg: entity types not read: DIMENSION in a block x204
- tekkat.dwg: the drawn walls do not close (no building walls): walls inferred from room outlines: 30 (108.3 m; outer thickness 0.25 m, assumed); evidence method inferred, status unverified
- tekkat.dwg: room 'YANGIN MERDİVENİ' (walls inferred from its outline) has no door in the documents; none invented (the agent may add one)
- tekkat.dwg: room 'KAT MERDİVENİ' (walls inferred from its outline) has no door in the documents; none invented (the agent may add one)
- tekkat.dwg: room 'GÜVENLİK HOLÜ' (walls inferred from its outline) has no door in the documents; none invented (the agent may add one)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- f_L0_001: inferred kitchen_counter: kitchen_counter: named by an AI pass and the only named type that fits the size (2.60 x 0.55 m), the other room and the position (others fitting: kitchen_island, sideboard, tv_unit, wardrobe)
- f_L0_002: inferred kitchen_island: kitchen_island: named by an AI pass and the only named type that fits the size (2.60 x 0.55 m), the other room and the position (others fitting: kitchen_counter, sideboard, tv_unit, wardrobe)
