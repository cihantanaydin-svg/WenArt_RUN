# Ingest report: real02

Status: **needs_review** (one_building.dwg: no building walls found; one_building.dwg: outer walls do not close (no building walls))
Source: `projects/real02`, pipeline commit `24f4694e7`, created 2026-10-06T14:46:32Z

## Documents

| File | Page | Class | Kind | Level | Scale | Confidence | Skip reason | Debug image |
|---|---|---|---|---|---|---|---|---|
| one_building.dwg | 1 | floor_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | debug/one_building_dwg_p1.png |

## Levels

| Level | Label | Order | Elevation | Ceiling | Walls | Openings | Rooms | Furniture |
|---|---|---|---|---|---|---|---|---|
| L0 | Zemin Kat | 0 | 0.00 | 2.70 (assumed_default) | 0 | 0 | 0 | 0 |

## Rooms

| Room | Level | Label | As drawn | Type | Area computed | Area label | Furniture in documents | Status |
|---|---|---|---|---|---|---|---|---|

## Furniture

| Piece | Level | Room | Type | As drawn | Source | Size (m) | Rotation | Status | File |
|---|---|---|---|---|---|---|---|---|---|

## Units

Project unit system: **metric**

| Document | Unit system | Source kind |
|---|---|---|
| one_building.dwg | metric | dxf |

## Scale

**one_building.dwg**: 0.001 m/unit, method `dxf_insunits`, confidence 1.00

- one_building.dwg p1: drawing units known (0.001 m per unit)

## Room size labels

None.

## Site

Recorded, not built.

| Id | What | Detail |
|---|---|---|
| sd_L0_001 | decor (other) | 3,35 m x 0,99 m |
| sd_L0_002 | decor (plant) | 1,52 m x 1,20 m |
| sd_L0_003 | decor (other) | 1,62 m x 1,30 m |
| sd_L0_004 | decor (other) | 0,23 m x 0,06 m |
| sd_L0_005 | decor (other) | 0,23 m x 0,06 m |
| sd_L0_006 | decor (other) | 0,16 m x 0,29 m |
| sd_L0_007 | decor (other) | 0,16 m x 0,29 m |
| sd_L0_008 | decor (other) | 0,09 m x 0,21 m |
| sd_L0_009 | decor (other) | 0,09 m x 0,21 m |
| sd_L0_010 | decor (plant) | 1,52 m x 1,20 m |
| sd_L0_011 | decor (plant) | 1,52 m x 1,20 m |
| sd_L0_012 | decor (other) | 0,47 m x 0,18 m |
| sd_L0_013 | decor (other) | 0,18 m x 0,47 m |
| sd_L0_014 | decor (other) | 0,16 m x 0,34 m |
| sd_L0_015 | decor (other) | 0,16 m x 0,34 m |
| sd_L0_016 | decor (plant) | 1,52 m x 1,20 m |

## Separators

None considered.

## Gaps

None.

## Furniture typing

None.

## Assumed values

- L0: ceiling height 2.70 m (assumed_default)

## Notes

### one_building.dwg

- furniture size checks use the wenart/recognition/size_table.yaml
- 16 glyph strokes inside text boxes ignored
- 0 stroke segments dropped as wall outline (>= 90 % within 20 mm of walls/openings)
- 3 site edge or boundary line groups outside the building (not decor)

## Conflicts

None.

## Unverified

None.

## Warnings

- one_building.dwg: 2 entities on layers that are off or frozen (or invisible) were not read
- one_building.dwg: entity types not read: WIPEOUT x40
- needs review: one_building.dwg: no building walls found
- needs review: one_building.dwg: outer walls do not close (no building walls)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- L0: no walls
