# Final report: real02 (needs review)

Status: **needs_review**. The project stopped before the 3D stages: nothing was built, rendered or polished in this run, and nothing was guessed or filled in. Every reason is listed below; after fixing them, run the project again.

## Reasons

- one_building.dwg: no building walls found
- one_building.dwg: outer walls do not close (no building walls)

## What to do

- DWG is read with LibreDWG 0.14 (beta); if it fails, export DXF
- close the walls around every labelled room in the drawing

## Documents and pages

| file | page | class | kind | level | scale | confidence | skip reason | debug image |
|---|---|---|---|---|---|---|---|---|
| one_building.dwg | 1 | floor_plan | vector | L0 | 0.001 m/unit (dxf_insunits) | 1.00 | - | [debug/one_building_dwg_p1.jpg](debug/one_building_dwg_p1.jpg) |

## Building JSON

| status | levels | walls | openings | rooms | furniture | conflicts | unverified |
|---|---|---|---|---|---|---|---|
| needs_review | 1 | 0 | 0 | 0 | 0 | 0 | 0 |

Pipeline warnings:

- one_building.dwg: 2 entities on layers that are off or frozen (or invisible) were not read
- one_building.dwg: entity types not read: WIPEOUT x40
- needs review: one_building.dwg: no building walls found
- needs review: one_building.dwg: outer walls do not close (no building walls)
- Level L0: ceiling height assumed 2.70 m (no section drawing found)
- L0: no walls

## Stages

This run (`20261006-144127-full-20261006T144622Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | needs_review | 86.0 s | building needs review (report.md) |

The report stage itself is recorded after this report.

## Warnings

None.
