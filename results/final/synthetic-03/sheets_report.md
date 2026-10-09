# Sheet analysis: synthetic-03

Status: **ok**; 4 regions, 0 strays, 0 conflicts; code `b18dad1f`, created 2026-10-09T09:29:51Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| kat_planlari.pdf | pdf | - | 0.035277777777777776 | pdf_scale_text | - |
| mobilya_plani.dxf | dxf | 4 | 0.001 | dxf_insunits | - |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| mobilya_plani.dxf | area_labels | - | - | 0 | 0 labels alone in a closed outline, 0 regions with >= 2 labels |
| mobilya_plani.dxf | level_marks | - | - | 0 | 0 sample(s), fewer than 1 |
| mobilya_plani.dxf | door_widths | mm | 1.0 | 7 | median door radius 800 units |
| mobilya_plani.dxf | wall_thickness | - | 0.521 | 96 | median face-pair distance 100 units; no unit fits 50% of the samples |
| mobilya_plani.dxf | text_height | mm | 1.0 | 8 | median text height 200 units |
| mobilya_plani.dxf | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | kat_planlari.pdf | floor_plan | title (0.99) | verified | BODRUM KAT PLANI | L-1 | base | read | 40.94 x 28.64 | - |
| r2 | kat_planlari.pdf | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI | L0 | base | read | 40.94 x 28.64 | - |
| r3 | kat_planlari.pdf | floor_plan | title (0.99) | verified | 1. KAT PLANI | L1 | base | read | 40.94 x 28.64 | - |
| r4 | mobilya_plani.dxf | furniture_plan | title (0.99) | verified | ZEMİN KAT MOBİLYA PLANI | L0 | base | read | 10.20 x 7.80 | - |

## Strays

None.

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L-1 | -1 | Bodrum Kat | basement | r1 | - |
| L0 | 0 | Zemin Kat | floor | r2 | - |
| L1 | 1 | 1. Kat | floor | r3 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r1, r2, r3 |

## Heights

Sections: none; cut axis -; datum -

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L-1 | -3.00 (assumed) | 2.70 (assumed) | 3.00 (assumed) | - |
| L0 | 0.00 (assumed) | 2.70 (assumed) | 3.00 (assumed) | - |
| L1 | 3.00 (assumed) | 2.70 (assumed) | 3.00 (assumed) | - |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L-1 | -3.00 (assumed) | 0.20 (assumed) |
| L-1 / L0 | 0.00 (assumed) | 0.20 (assumed) |
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
