# Sheet analysis: real01

Status: **ok**; 1 regions, 0 strays, 0 conflicts; code `9909871b`, created 2026-10-10T00:06:25Z

## Documents and units

| File | Format | $INSUNITS | Metres per unit | Method | Conflict |
|---|---|---|---|---|---|
| real01.pdf | pdf | - | - | none | - |

## Regions

| Region | File | Class | Decided by | Status | Title | Level | Variant | Use | Size (m) | Registration |
|---|---|---|---|---|---|---|---|---|---|---|
| r1 | real01.pdf | floor_plan | geometry (0.70) | verified | - | L0 (assumed) | base | read | - | - |

## Strays

None.

## Levels and variants

| Level | Order | Label | Kind | Base region | Alternatives |
|---|---|---|---|---|---|
| L0 | 0 | Ground floor | floor | r1 | - |

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

- real01.pdf r1: plan without a level title, the project's only plan: level L0 'Ground floor' assumed
