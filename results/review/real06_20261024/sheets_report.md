# Sheet analysis: real06

Status: **ok**; 9 regions, 0 strays, 1 conflicts; code `36d1b2049d`, created 2026-10-24T05:38:05Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| real06.dwg | dwg | 0 | 50.0 | unit_check | - |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| real06.dwg | area_labels | - | 0.0 | 3 | 1 labels alone in a closed outline, 2 regions with >= 2 labels; no unit fits 50% of the samples |
| real06.dwg | level_marks | m 1:50 | 0.982 | 164 | 164 mark pair(s): 50 m/unit, 50 m/unit, 50 m/unit, 50 m/unit; no unit fits 50% of the samples |
| real06.dwg | door_widths | m 1:50 | 1.0 | 10 | median door radius 0.014 units; no unit fits 50% of the samples |
| real06.dwg | wall_thickness | - | 0.0 | 2468 | median face-pair distance 0.0014 units; no unit fits 50% of the samples |
| real06.dwg | text_height | m 1:50 | 1.0 | 803 | median text height 0.0016 units; no unit fits |
| real06.dwg | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |
| real06.dwg | dimension_texts | - | - | 565 | 565 dimension text(s) with a dimension line, median 50 m/unit |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | real06.dwg | elevation | geometry (0.70) | verified | - | - | - | exterior | 13.96 x 8.29 | - |
| r2 | real06.dwg | elevation | geometry (0.70) | verified | - | - | - | exterior | 13.96 x 8.29 | - |
| r3 | real06.dwg | floor_plan | geometry (0.70) | verified | - | L0 (assumed) | base | read | 15.67 x 21.90 | reference, rot 0, shift [0.0, 0.0], residual 0.0, stairs NOT aligned |
| r4 | real06.dwg | floor_plan | geometry (0.70) | verified | - | L1 (assumed) | base | read | 15.37 x 21.90 | outline_icp, rot 0, shift [-18.583843, -1.2e-05], residual 0.1299, stairs NOT aligned |
| r5 | real06.dwg | section | geometry (0.85) | verified | - | - | - | heights | 22.47 x 9.15 | - |
| r6 | real06.dwg | roof_plan | geometry (0.60) | verified | - | - | - | exterior | 13.35 x 21.10 | - |
| r7 | real06.dwg | elevation | geometry (0.70) | verified | - | - | - | exterior | 21.49 x 8.31 | - |
| r8 | real06.dwg | elevation | geometry (0.70) | verified | - | - | - | exterior | 19.82 x 8.29 | - |
| r9 | real06.dwg | section | geometry (0.85) | verified | - | - | - | heights | 14.94 x 9.15 | - |

## Strays

None.

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L0 | 0 | Ground floor | floor | r3 | - |
| L1 | 1 | Level 1 | floor | r4 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L0, L1 | r3, r4 |

## Heights

Sections: r5; cut axis y; datum 0.50 (vector)

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L0 | 0.00 (vector) | 2.85 (vector) | 3.00 (vector) | 0.00 (vector) |
| L1 | 3.00 (vector) | 2.85 (vector) | 3.00 (vector) | 3.00 (vector) |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L0 | 0.00 (vector) | 0.15 (vector) |
| L0 / L1 | 3.00 (vector) | 0.15 (vector) |
| L1 / - | 6.00 (vector) | 0.15 (vector) |

| Roof | Value |
|---|---|
| eaves_z | 6.00 (vector) - 3.00 m above the top floor |
| ridge_z | 7.77 (vector) - 4.77 m above the top floor |
| overhang | 0.47 (vector) - left 0.50 m, right 0.48 m |
| thickness | - (assumed) - not drawn: the roof is one line in the section |
| knee_wall | 3.00 (vector) - the roof's top surface at the outer face of the outer wall above the top floor (a cross-check) |
| pitches | 16.90 (vector), 40.10 (vector), 45.00 (vector), 37.80 (vector), 38.80 (vector), 80.10 (vector), 14.40 (vector), 18.30 (vector) |

## Exterior

Roof: **hip** (roof_plan); 10 slope texts on r6 all give 33 % (18.3 degrees), 13 hip lines: a hip roof
Facade entries: 0; elevations: 4; site plan: no; north: -

## Conflicts

| Id | Kind | Regions | Description | Resolution |
|---|---|---|---|---|
| sc_001 | registration_residual | r4, r3 | real06.dwg r4 (L1) registered onto r3 (L0) with an RMS outline distance of 0.130 m (826 of 1016 outline points within 5 cm; outlines 14.17 x 20.70 m vs 14.47 x 20.70 m) | unresolved: each level is built as drawn |

## Needs review

None.

## AI questions

Only regions whose class neither the title nor the geometry decided are asked (two passes). 0 `sheet_region` questions (`sheets/requests.json`); 0 waiting for answers; answers folder: -.

## Warnings

- real06.dwg: $INSUNITS 0 names no unit; the drawing is scaled: drawn in m at 1:50 (50 m per unit), inferred from 3 agreeing checks (level_marks 98%, door_widths 100%, text_height 100%); no plain unit fits
- real06.dwg r1: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r2: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r7: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r8: slab bands but no room name, beside sections with rooms: an elevation (inferred)
- real06.dwg r3: plan without a level title: level L0 'Ground floor' inferred from its floor mark +0.50 m (2 untitled plans ordered by their floor marks)
- real06.dwg r4: plan without a level title: level L1 'Level 1' inferred from its floor mark +3.50 m (2 untitled plans ordered by their floor marks)
- registration: r3 (L0): stairs drawn on this level only
- registration: r4 (L1): stairs drawn on the level next to it only
- 2 sections: heights from r5; r9 not read for heights
- section r5: 16.32 m wide, no outline extent fits; the cut line on r3 gives the axis y
- roof: the roof plan r6 gives a hip roof at 33 %; the section's profile reads as gambrel (its outline also draws trusses and trims): the roof plan wins
- elevation r1: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r2: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r7: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
- elevation r8: no side in its title: its facade entries are listed for side 'all' (not mapped onto a side)
