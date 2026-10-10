# Sheet analysis: real02

Status: **ok**; 6 regions, 3 strays, 2 conflicts; code `cddf61aa`, created 2026-10-10T01:03:46Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| one_building.dwg | dwg | 4 | 0.01 | unit_check | $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| one_building.dwg | area_labels | cm | 1.0 | 4 | 0 labels alone in a closed outline, 4 regions with >= 2 labels |
| one_building.dwg | level_marks | cm | 1.0 | 1 | 1 mark pair(s): 0.009524 m/unit |
| one_building.dwg | door_widths | cm | 1.0 | 26 | median door radius 81.83 units |
| one_building.dwg | wall_thickness | - | 0.571 | 1514 | median face-pair distance 11.8 units; no unit fits 50% of the samples |
| one_building.dwg | text_height | - | - | 40 | median text height 15 units; cm and in fit equally well |
| one_building.dwg | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | one_building.dwg | title_block | geometry (0.90) | verified | PLANLAR | - | - | ignored (title block) | 56.59 x 7.21 | - |
| r2 | one_building.dwg | floor_plan | title (0.99) | verified | BODRUM KAT PLANI BRÜT 92 M2 | L-1 | base | read | 15.17 x 12.00 | columns, rot 0, shift [-21.415948, -15.73488], residual 0.0001, stairs aligned |
| r3 | one_building.dwg | alternative_floor_plan | title (0.99) | verified | BODRUM KAT PLANI BRÜT 92 M2 ( Açık mutfak) | L-1b | Açık mutfak | read | 15.17 x 12.01 | columns, rot 0, shift [-21.41692, -0.191033], residual 0.0001, stairs aligned |
| r4 | one_building.dwg | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI BRÜT 92M2 | L0 | base | read | 15.17 x 12.00 | reference, rot 0, shift [0.0, 0.0], residual 0.0, stairs aligned |
| r5 | one_building.dwg | floor_plan | title (0.99) | verified | ÇATI KAT PLANI | L1 | base | read | 16.17 x 13.00 | columns, rot 0, shift [-9.359466, 20.412991], residual 0.0001, stairs aligned |
| r6 | one_building.dwg | section | geometry (0.85) | verified | - | - | - | heights | 33.55 x 9.94 | - |

## Strays

| File | Entity | Type | Layer | Distance (m) | Reason |
|---|---|---|---|---|---|
| one_building.dwg | HATCH:6633 | HATCH | _P3_S_Duvar_T | 317.86 | far outside the frame, 1 entity (0.01 % of the document) |
| one_building.dwg | DIMENSION:34CEC | DIMENSION | Deko_Olcu Ic | 20.95 | far outside the frame; on a layer that is off or frozen (not drawn) |
| one_building.dwg | DIMENSION:34CF2 | DIMENSION | Deko_Olcu Ic | 20.96 | far outside the frame; on a layer that is off or frozen (not drawn) |

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L-1 | -1 | Bodrum Kat | basement | r2 | L-1b r3 'Açık mutfak' |
| L0 | 0 | Zemin Kat | floor | r4 | - |
| L1 | 1 | Çatı Katı | attic | r5 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r2, r4, r5 |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r3, r4, r5 |

## Heights

Sections: r6; cut axis x; datum 43.00 (vector)

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L-1 | -3.00 (vector) | 2.85 (vector) | 3.00 (vector) | -3.00 (vector) |
| L0 | 0.00 (vector) | 3.00 (vector) | 3.15 (vector) | 0.00 (vector) |
| L1 | 3.15 (vector) | 3.43 (vector) | - | - |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L-1 | -3.00 (vector) | 0.15 (vector) |
| L-1 / L0 | 0.00 (vector) | 0.15 (vector) |
| L0 / L1 | 3.15 (vector) | 0.15 (vector) |

| Roof | Value |
|---|---|
| eaves_z | 3.65 (vector) - 0.50 m above the top floor |
| ridge_z | 6.79 (vector) - 3.64 m above the top floor |
| overhang | 0.50 (vector) - left 0.50 m, right 0.50 m |
| thickness | 0.20 (vector) - perpendicular to the first slope |
| knee_wall | 0.93 (vector) - the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 0.66 m above the floor |
| pitches | 40.40 (vector), 13.30 (vector) |
| ground left | 0.00 (vector) |
| ground right | 0.00 (vector) |

## Exterior

Roof: **mansard** (plan_roof_lines); roof outline 16.17 x 13.00 m on r5; closed line inside it 11.77 x 8.60 m (LWPOLYLINE:2F87A): the slope changes there (mansard)
Facade entries: 0; elevations: 0; site plan: no; north: -

## Conflicts

| Id | Kind | Regions | Description | Resolution |
|---|---|---|---|---|
| sc_001 | unit_mismatch | r1, r2, r3, r4, r5, r6 | one_building.dwg: $INSUNITS 4 says mm, but 3 independent checks (area_labels, level_marks, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| sc_002 | level_mark_mismatch | r6 | section r6: the level mark 40.00 (MTEXT:304DD) gives -3.00 m but points at -3.15 m (the bottom of a slab) (0.15 m apart) | geometry wins: slab tops from the slab lines |

## Needs review

None.

## AI questions

Only regions whose class neither the title nor the geometry decided are asked (two passes). 0 `sheet_region` questions (`sheets/requests.json`); 0 waiting for answers; answers folder: -.

## Warnings

- the largest drawn polylines of the plans differ in size: r2 (L-1) LWPOLYLINE:366F8 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r3 (L-1b) LWPOLYLINE:2C4A5 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r4 (L0) LWPOLYLINE:2DA7F on DBM_w_sld 7.59 x 10.50 m (open, ends 0.40 m apart); r5 (L1) LWPOLYLINE:2F87A on _P3_S_Duvar_Ç 11.77 x 8.60 m (closed); the registered outlines (all long strokes, columns included) give residuals r2 0.0001, r3 0.0001, r5 0.0001 m; each level is kept as drawn
- section r6: 2 horizontal lines outside the left wall; the upper one (+0.00 m) is read as the terrain, the others (-3.15 m (LWPOLYLINE:304DE)) are not
- section r6: 2 horizontal lines outside the right wall; the upper one (+0.00 m) is read as the terrain, the others (-3.15 m (LWPOLYLINE:304DF)) are not
- section r6: no cut line on the plans: the section's left end is taken as the building's min side along the cut axis (flipped unknown)
- roof: the break line on r5 (LWPOLYLINE:2F87A) is 11.77 m wide along the cut, the section's slope changes 12.17 m apart (0.40 m); both kept as drawn
- no elevation drawn: facade materials and outside openings are not drawn (facade empty)
