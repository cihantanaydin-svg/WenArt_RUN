# Sheet analysis: real03

Status: **ok**; 1 regions, 0 strays, 0 conflicts; code `87831c156`, created 2026-10-10T10:47:16Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| tekkat.dwg | dwg | 5 | 0.01 | dxf_insunits | - |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| tekkat.dwg | area_labels | cm | 0.833 | 6 | 5 labels alone in a closed outline, 1 regions with >= 2 labels |
| tekkat.dwg | level_marks | - | - | 0 | 0 sample(s), fewer than 1 |
| tekkat.dwg | door_widths | cm | 1.0 | 4 | median door radius 90 units |
| tekkat.dwg | wall_thickness | - | 0.462 | 78 | median face-pair distance 25 units; no unit fits 50% of the samples |
| tekkat.dwg | text_height | - | - | 46 | median text height 12.5 units; cm and in fit equally well |
| tekkat.dwg | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | tekkat.dwg | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI | L0 | base | read | 52.50 x 53.00 | - |

## Strays

None.

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L0 | 0 | Zemin Kat | floor | r1 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L0 | r1 |

## Heights

Sections: none; cut axis -; datum -

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L0 | 0.00 (assumed) | 2.70 (assumed) | 3.00 (assumed) | - |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L0 | 0.00 (assumed) | 0.20 (assumed) |

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
