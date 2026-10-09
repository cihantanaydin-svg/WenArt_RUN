# Sheet analysis: synthetic-07

Status: **ok**; 10 regions, 1 strays, 0 conflicts; code `7e95d4e1`, created 2026-10-09T13:51:55Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| sheet.dxf | dxf | 5 | 0.01 | dxf_insunits | - |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| sheet.dxf | area_labels | cm | 1.0 | 4 | 0 labels alone in a closed outline, 4 regions with >= 2 labels |
| sheet.dxf | level_marks | cm | 1.0 | 3 | 3 mark pair(s): 0.01 m/unit, 0.01 m/unit, 0.01 m/unit |
| sheet.dxf | door_widths | cm | 1.0 | 12 | median door radius 85 units |
| sheet.dxf | wall_thickness | cm | 0.875 | 295 | median face-pair distance 25 units |
| sheet.dxf | text_height | - | - | 38 | median text height 20 units; cm and in fit equally well |
| sheet.dxf | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | sheet.dxf | floor_plan | title (0.99) | verified | BODRUM KAT PLANI | L-1 | base | read | 10.00 x 8.00 | columns, rot 0, shift [34.0, -1.6], residual 0.0, stairs aligned |
| r2 | sheet.dxf | alternative_floor_plan | title (0.99) | verified | BODRUM KAT PLANI (AÇIK MUTFAK) | L-1b | Açık mutfak | read | 10.00 x 8.00 | columns, rot 0, shift [17.0, -1.35], residual 0.0, stairs aligned |
| r3 | sheet.dxf | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI | L0 | base | read | 10.00 x 10.40 | reference, rot 0, shift [0.0, 0.0], residual 0.0, stairs aligned |
| r4 | sheet.dxf | floor_plan | title (0.99) | verified | ÇATI KAT PLANI | L1 | base | read | 11.00 x 9.00 | columns, rot 0, shift [-17.5, -0.35], residual 0.0, stairs aligned |
| r5 | sheet.dxf | site_plan | title (0.99) | verified | VAZİYET PLANI | - | - | exterior | 28.00 x 24.50 | site_outline, rot 0, shift [-46.0, 13.4], residual 0.0 |
| r6 | sheet.dxf | section | title (0.99) | verified | A-A KESİTİ | - | - | heights | 14.55 x 10.31 | - |
| r7 | sheet.dxf | elevation | title (0.99) | verified | GÜNEY GÖRÜNÜŞÜ | - | - | exterior | 16.00 x 7.11 | - |
| r8 | sheet.dxf | elevation | title (0.99) | verified | DOĞU GÖRÜNÜŞÜ | - | - | exterior | 14.00 x 7.11 | - |
| r9 | sheet.dxf | legend | title (0.99) | verified | LEJANT | - | - | ignored (legend) | 18.00 x 7.50 | - |
| r10 | sheet.dxf | title_block | geometry (0.90) | verified | - | - | - | ignored (title block) | 60.00 x 3.60 | - |

## Strays

| File | Entity | Type | Layer | Distance (m) | Reason |
|---|---|---|---|---|---|
| sheet.dxf | LINE:297 | LINE | 0 | 1175.38 | far outside the frame, 1 entity (0.30 % of the document) |

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L-1 | -1 | Bodrum Kat | basement | r1 | L-1b r2 'Açık mutfak' |
| L0 | 0 | Zemin Kat | floor | r3 | - |
| L1 | 1 | Çatı Katı | attic | r4 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r1, r3, r4 |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r2, r3, r4 |

## Heights

Sections: r6; cut axis y; datum 0.00 (vector)

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L-1 | -3.00 (vector) | 2.80 (vector) | 3.00 (vector) | -3.00 (vector) |
| L0 | 0.00 (vector) | 2.80 (vector) | 3.00 (vector) | 0.00 (vector) |
| L1 | 3.00 (vector) | 3.80 (vector) | - | 3.00 (vector) |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L-1 | -3.00 (vector) | 0.20 (vector) |
| L-1 / L0 | 0.00 (vector) | 0.20 (vector) |
| L0 / L1 | 3.00 (vector) | 0.20 (vector) |

| Roof | Value |
|---|---|
| eaves_z | 3.96 (vector) - 0.96 m above the top floor |
| ridge_z | 7.11 (vector) - 4.11 m above the top floor |
| overhang | 0.50 (vector) - left 0.50 m, right 0.50 m |
| thickness | 0.25 (vector) - perpendicular to the first slope |
| knee_wall | 1.30 (vector) - the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 1.00 m above the floor |
| pitches | 35.00 (vector) |
| ground front | 0.00 (vector) |
| ground back | 0.00 (vector) |

## Exterior

Roof: **gable** (section)
Facade entries: 3; elevations: 2; site plan: registered (site_outline); north: 0.00 (vector)

## Conflicts

None.

## Needs review

None.

## AI questions

Only regions whose class neither the title nor the geometry decided are asked (two passes). 0 `sheet_region` questions (`sheets/requests.json`); 0 waiting for answers; answers folder: -.

## Warnings

- site plan r5: its building outline LWPOLYLINE:269 fits at 0 and 180 deg alike (symmetric): 0 deg kept
