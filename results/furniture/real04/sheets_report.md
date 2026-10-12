# Sheet analysis: real04

Status: **ok**; 21 regions, 7 strays, 6 conflicts; code `7283ccdcd`, created 2026-10-11T15:47:11Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| deneme1.dwg | dwg | 4 | 0.01 | unit_check | $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used |

| File | Check | Unit | Score | Samples | Note |
|---|---|---|---|---|---|
| deneme1.dwg | area_labels | cm | 1.0 | 6 | 0 labels alone in a closed outline, 6 regions with >= 2 labels |
| deneme1.dwg | level_marks | - | 0.038 | 53 | 53 mark pair(s): 0.06501 m/unit, 0.002694 m/unit, 0.002142 m/unit, 0.0003792 m/unit; no unit fits 50% of the samples |
| deneme1.dwg | door_widths | cm | 0.907 | 43 | median door radius 81.83 units |
| deneme1.dwg | wall_thickness | - | 0.435 | 2951 | median face-pair distance 10 units; no unit fits 50% of the samples |
| deneme1.dwg | text_height | - | - | 201 | median text height 60.27 units; no unit fits |
| deneme1.dwg | dimensions | - | - | 0 | 0 sample(s), fewer than 2 |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | deneme1.dwg | floor_plan | ai (0.95) | unverified | - | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) | 93.26 x 135.24 | - |
| r2 | deneme1.dwg | other | none (0.00) | unverified | - | - | - | ignored (no title and no geometry rule gives a class) | 93.26 x 67.62 | - |
| r3 | deneme1.dwg | other | none (0.00) | unverified | - | - | - | ignored (no title and no geometry rule gives a class) | 56.00 x 15.83 | - |
| r4 | deneme1.dwg | other | none (0.00) | unverified | - | - | - | ignored (no title and no geometry rule gives a class) | 53.34 x 39.81 | - |
| r5 | deneme1.dwg | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI BRÜT 92M2 | L0 | base | read | 17.17 x 12.00 | reference, rot 0, shift [0.0, 0.0], residual 0.0, stairs aligned |
| r6 | deneme1.dwg | title_block | geometry (0.90) | verified | BEYKOZ ÇAYAĞZI MAHALLESİ 2086 ve 2296 PARSEL | - | - | ignored (title block) | 56.59 x 7.21 | - |
| r7 | deneme1.dwg | title_block | geometry (0.90) | verified | E:0.25 / H:2K / PROJE ALANI : 1165 M2(621+544) | - | - | ignored (title block) | 56.59 x 7.21 | - |
| r8 | deneme1.dwg | title_block | geometry (0.90) | verified | m2 : 1165 M2(621+544) TAKS %40 : 466 M2 1165x0,25: 291,25 M2 291,25x1.3 : 378,625 M2( %30 dahil) 94.6 M2 / 4 ADET VİLLA | - | - | ignored (title block) | 56.59 x 12.18 | - |
| r9 | deneme1.dwg | title_block | geometry (0.90) | verified | PLANLAR | - | - | ignored (title block) | 56.59 x 7.21 | - |
| r10 | deneme1.dwg | title_block | geometry (0.90) | verified | m2 : 1165 M2(621+544) TAKS %40 : 466 M2 1165x0,25: 291,25 M2 291,25x1.3 : 378,625 M2( %30 dahil) 94.6 M2 / 4 ADET VİLLA | - | - | ignored (title block) | 56.59 x 12.18 | - |
| r11 | deneme1.dwg | floor_plan | title (0.99) | verified | BODRUM KAT PLANI BRÜT 92 M2 | L-1 | base | read | 15.17 x 12.00 | columns, rot 0, shift [-21.415948, 38.254231], residual 0.2477, stairs aligned |
| r12 | deneme1.dwg | site_plan | ai (0.95) | unverified | - | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) | 48.72 x 39.81 | - |
| r13 | deneme1.dwg | site_plan | ai (0.95) | unverified | - | - | - | ignored (AI-only class: unverified, never read as a drawing (AI proposes, title and geometry decide)) | 48.72 x 39.81 | - |
| r14 | deneme1.dwg | site_plan | geometry (0.70) | verified | - | - | - | exterior | 53.34 x 44.28 | site_buildings, rot 79, shift [42673.9906, -15718.3098], residual 0.025 |
| r15 | deneme1.dwg | alternative_floor_plan | title (0.99) | verified | BODRUM KAT PLANI BRÜT 92 M2 ( Açık mutfak) | L-1b | Açık mutfak | read | 15.17 x 12.01 | columns, rot 0, shift [-21.41692, 53.798078], residual 0.2477, stairs aligned |
| r16 | deneme1.dwg | floor_plan | title (0.99) | verified | ZEMİN KAT PLANI BRÜT 92M2 | L0 | base | read | 15.17 x 12.00 | columns, rot 0, shift [0.0, 53.989111], residual 0.2467, stairs aligned |
| r17 | deneme1.dwg | other | none (0.00) | unverified | - | - | - | ignored (no title and no geometry rule gives a class) | 11.80 x 9.00 | - |
| r18 | deneme1.dwg | floor_plan | title (0.99) | verified | ÇATI KAT PLANI | L1 | base | read | 16.17 x 13.00 | columns, rot 0, shift [-9.359466, 74.402102], residual 0.2477, stairs aligned |
| r19 | deneme1.dwg | section | geometry (0.85) | verified | - | - | - | heights | 28.89 x 8.96 | - |
| r20 | deneme1.dwg | section | geometry (0.85) | verified | - | - | - | heights | 33.55 x 9.94 | - |
| r21 | deneme1.dwg | other | none (0.00) | unverified | - | - | - | ignored (no title and no geometry rule gives a class) | 0.01 x 0.02 | - |

## Strays

| File | Entity | Type | Layer | Distance (m) | Reason |
|---|---|---|---|---|---|
| deneme1.dwg | HATCH:5303 | HATCH | _P6_BT_Yesil_T | 206.59 | far outside the frame, 1 entity (0.01 % of the document) |
| deneme1.dwg | HATCH:2AC24 | HATCH | 0 | 15.96 | far outside the frame, 4 entities (0.03 % of the document) |
| deneme1.dwg | HATCH:2AC25 | HATCH | 0 | 15.96 | far outside the frame, 4 entities (0.03 % of the document) |
| deneme1.dwg | LWPOLYLINE:2AC26 | LWPOLYLINE | _P2_D_4_Ç | 15.96 | far outside the frame, 4 entities (0.03 % of the document) |
| deneme1.dwg | HATCH:2AC27 | HATCH | 0 | 15.96 | far outside the frame, 4 entities (0.03 % of the document) |
| deneme1.dwg | LWPOLYLINE:2B018 | LWPOLYLINE | _P3_S_Duvar_Ç | 6.66 | far outside the frame, 2 entities (0.02 % of the document) |
| deneme1.dwg | LWPOLYLINE:2B019 | LWPOLYLINE | _P3_S_Duvar_Ç | 6.66 | far outside the frame, 2 entities (0.02 % of the document) |

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L-1 | -1 | Bodrum Kat | basement | r11 | L-1b r15 'Açık mutfak' |
| L0 | 0 | Zemin Kat | floor | r5 | - |
| L1 | 1 | Çatı Katı | attic | r18 | - |

| Variant | Label | Levels | Regions |
|---|---|---|---|
| base | Base | L-1, L0, L1 | r11, r5, r18 |
| l-1b-acik-mutfak | Bodrum Kat: Açık mutfak (open kitchen) | L-1b, L0, L1 | r15, r5, r18 |

## Heights

Sections: r19; cut axis -; datum -

| Level | Floor z | Ceiling | Floor to floor | Level mark |
|---|---|---|---|---|
| L-1 | -3.00 (vector) | 2.85 (vector) | 3.00 (vector) | - |
| L0 | 0.00 (vector) | 3.00 (vector) | 3.15 (vector) | - |
| L1 | 3.15 (vector) | 2.45 (vector) | - | - |

| Slab between | Top z | Thickness |
|---|---|---|
| - / L-1 | -3.00 (vector) | 0.15 (vector) |
| L-1 / L0 | 0.00 (vector) | 0.15 (vector) |
| L0 / L1 | 3.15 (vector) | 0.15 (vector) |

| Roof | Value |
|---|---|
| eaves_z | 3.75 (vector) - 0.60 m above the top floor |
| ridge_z | 5.80 (vector) - 2.66 m above the top floor |
| overhang | 0.50 (vector) - left 0.50 m, right 0.50 m |
| thickness | 0.20 (vector) - perpendicular to the first slope |
| knee_wall | 0.92 (vector) - the roof's top surface at the outer face of the outer wall above the top floor (a cross-check); the underside meets the outer face 0.68 m above the floor |
| pitches | 32.50 (vector), 11.30 (vector) |
| ground left | -3.15 (vector) |
| ground right | 0.00 (vector) |

## Exterior

Roof: **mansard** (plan_roof_lines); roof outline 16.17 x 13.00 m on r18; closed line inside it 11.77 x 8.60 m (LWPOLYLINE:2F87A): the slope changes there (mansard)
Facade entries: 0; elevations: 0; site plan: registered (site_buildings: b1 modelled; b2 turned 0.0 deg, moved -0.00 / 18.57 m, dz +3.00 m (entrances)); north: -

## Conflicts

| Id | Kind | Regions | Description | Resolution |
|---|---|---|---|---|
| sc_001 | unit_mismatch | r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21 | deneme1.dwg: $INSUNITS 4 says mm, but 2 independent checks (area_labels, door_widths) agree on cm and none supports mm: cm used | cm used (user decision 8 of 8 Oct 2026: >= 2 independent checks agree) |
| sc_002 | registration_residual | r11, r5 | deneme1.dwg r11 (L-1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_003 | registration_residual | r15, r5 | deneme1.dwg r15 (L-1b) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_004 | registration_residual | r16, r5 | deneme1.dwg r16 (L0) registered onto r5 (L0) with an RMS outline distance of 0.247 m (492 of 550 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_005 | registration_residual | r18, r5 | deneme1.dwg r18 (L1) registered onto r5 (L0) with an RMS outline distance of 0.248 m (488 of 546 outline points within 5 cm; outlines 15.17 x 12.00 m vs 17.17 x 12.00 m) | unresolved: each level is built as drawn |
| sc_006 | section_width_mismatch | r19 | section r19 is 10.80 m wide between its outer walls; the reference plan's outline is 17.17 x 12.00 m | unresolved: heights kept, cut direction unknown |

## Needs review

None.

## AI questions

Only regions whose class neither the title nor the geometry decided are asked (two passes). 8 `sheet_region` questions (`sheets/requests.json`) for r1, r2, r3, r4, r12, r13, r17, r21; 0 waiting for answers; answers folder: outputs/real04/sheets.

## Warnings

- deneme1.dwg r1: class floor_plan from the two AI passes only: unverified, not read
- deneme1.dwg r12: class site_plan from the two AI passes only: unverified, not read
- deneme1.dwg r13: class site_plan from the two AI passes only: unverified, not read
- the largest drawn polylines of the plans differ in size: r5 (L0) LWPOLYLINE:39F34 on DBM_w_sld 7.59 x 10.50 m (open, ends 5.31 m apart); r11 (L-1) LWPOLYLINE:366F8 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r15 (L-1b) LWPOLYLINE:2C4A5 on DBM_w_sld 7.19 x 10.50 m (open, ends 12.50 m apart); r16 (L0) LWPOLYLINE:2DA7F on DBM_w_sld 7.59 x 10.50 m (open, ends 0.40 m apart); r18 (L1) LWPOLYLINE:2F87A on _P3_S_Duvar_Ç 11.77 x 8.60 m (closed); the registered outlines (all long strokes, columns included) give residuals r11 0.2477, r15 0.2477, r16 0.2467, r18 0.2477 m; each level is kept as drawn
- 2 sections: heights from r19; r20 not read for heights
- section r19: no cut line on the plans: the section's left end is taken as the building's min side along the cut axis (flipped unknown)
- section r19: the cut direction is unknown: the ground levels keep the section's left/right
- roof: the break line on r18 (LWPOLYLINE:2F87A) is 8.60 m wide along the cut, the section's slope changes 7.80 m apart (0.80 m); both kept as drawn
- site plan r14: 2 buildings on the plot (b1: turned 0.0 deg, dz +0.00 m, b2: turned 0.0 deg, dz +3.00 m)
- no elevation drawn: facade materials and outside openings are not drawn (facade empty)
