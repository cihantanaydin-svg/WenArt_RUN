# Final report: synthetic-02 (needs review)

Status: **needs_review**. The project stopped before the 3D stages: nothing was built, rendered or polished in this run, and nothing was guessed or filled in. Every reason is listed below; after fixing them, run the project again.

## Reasons

- no vector floor plan page could be used (raster pages need the recognition path)

## What to do

- add a DXF or vector PDF floor plan; scans and photos need the recognition path

## Documents and pages

| file | page | class | kind | level | scale | confidence | skip reason | debug image |
|---|---|---|---|---|---|---|---|---|
| plan_photo.jpg | 1 | other | photo | - | - | 0.00 | no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here | [debug/plan_photo_jpg_p1.jpg](debug/plan_photo_jpg_p1.jpg) |
| plan_scan.png | 1 | other | scan | - | - | 0.00 | no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here | [debug/plan_scan_png_p1.jpg](debug/plan_scan_png_p1.jpg) |

## Building JSON

| status | levels | walls | openings | rooms | furniture | conflicts | unverified |
|---|---|---|---|---|---|---|---|
| needs_review | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Pipeline warnings:

- plan_photo.jpg p1: photo page skipped (no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here)
- plan_scan.png p1: scan page skipped (no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here)
- needs review: no vector floor plan page could be used (raster pages need the recognition path)

## Stages

This run (`20261003-030812-full-20261003T031435Z`):

| stage | status | seconds | note |
|---|---|---|---|
| intake | skipped | 0.0 s | private only |
| pipeline | needs_review | 12.2 s | building needs review (report.md); earlier outputs without run records moved to /workspace/outputs-archive/synthetic-02-20261003T031435Z |

The report stage itself is recorded after this report.

## Warnings

None.
