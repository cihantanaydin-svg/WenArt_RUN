# Sheet analysis: synthetic-01

Status: **ok**; 3 regions, 0 strays, 0 conflicts; code `9909871b`, created 2026-10-10T00:06:44Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| 1_kat.pdf | pdf | - | 0.035277777777777776 | pdf_scale_text | - |
| 1_kat_scan.png | image | - | - | raster | - |
| zemin_kat.dxf | dxf | 4 | 0.001 | dxf_insunits | - |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| zemin_kat.dxf | area_labels | - | - | 0 | 0 labels alone in a closed outline, 0 regions with >= 2 labels |
| zemin_kat.dxf | level_marks | - | - | 0 | 0 sample(s), fewer than 1 |
| zemin_kat.dxf | door_widths | mm | 1.0 | 5 | median door radius 800 units |
| zemin_kat.dxf | wall_thickness | - | 0.552 | 67 | median face-pair distance 100 units; no unit fits 50% of the samples |
| zemin_kat.dxf | text_height | mm | 1.0 | 6 | median text height 200 units |
| zemin_kat.dxf | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | 1_kat.pdf | floor_plan | title (0.99) | verified | 1. KAT PLANI | L1 | base | read | 40.94 x 28.64 | - |
| r2 | 1_kat_scan.png | other | none (0.00) | unverified | - | - | - | ignored (raster page: classified and read by the pipeline's OCR path) | - | - |
| r3 | zemin_kat.dxf | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI | L0 | base | read | 10.70 x 8.30 | - |

## Strays

None.

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L0 | 0 | Zemin Kat | floor | r3 | - |
| L1 | 1 | 1. Kat | floor | r1 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L0, L1 | r3, r1 |

## Heights

Sections: none; cut axis -; datum -

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L0 | 0.00 (assumed) | 2.70 (assumed) | 3.00 (assumed) | - |
| L1 | 3.00 (assumed) | 2.70 (assumed) | 3.00 (assumed) | - |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L0 | 0.00 (assumed) | 0.20 (assumed) |
| L0 / L1 | 3.00 (assumed) | 0.20 (assumed) |

| Roof | Value |
|---|---|
| eaves_z | - |
| ridge_z | - |
| overhang | - |
| thickness | - |
| knee_wall | - |
| pitches | - |

## Exterior

Roof: nothing drawn.
Facade entries: 0; elevations: 0; site plan: no; north: -

## Conflicts

None.

## Needs review

None.

## AI questions

Only regions whose class neither the title nor the geometry decided are asked (two passes). 0 `sheet_region` questions (`sheets/requests.json`); 0 waiting for answers; answers folder: -.

## Warnings

None.
