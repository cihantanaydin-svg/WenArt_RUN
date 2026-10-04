# Decor: synthetic-04

13 decor pieces (rule-based, `added_by_ai`, max 0.6 m except rugs and wall art). Cushions on sofas and beds, books on shelves and desks, one plant per living room or bedroom in a free corner (never on a door approach, a swing or a 0.9 m walkway). Rugs under the sofa + coffee table group, the lower two thirds of a double bed and dining tables (+ 0.6 m for the chairs), group + 0.3 m, inside the room shrunk by 0.3 m, never under a door swing; one wall art piece per living room, bedroom or dining room above a sofa, bed or dresser (0.25 m above its top, at most 0.6 x its width, never over a door or window; built only from a library model).

| Room | Cushions | Books | Plant | Rugs | Wall art | Note |
|---|---|---|---|---|---|---|
| Salon + Mutfak (r_L3_salon_mutfak) | 2 | 1 | none | 2 | none | no free corner ((0.5, 0.5): walkway; (6.7, 0.5): walkway; (6.7, 4.3): no_overlap; (3.2, 7.5): no_overlap; (0.5, 7.5): no_overlap); no wall art: f_L3_010 has no wall behind it |
| Yatak Odası (r_L3_yatak_odasi) | 2 | 0 | 11.5, 0.5 | 1 | over f_L3_015 (0.96 m wide) |  |
| Hol (r_L3_hol) | 0 | 0 | - | 0 | - |  |
| Çocuk Odası (r_L3_cocuk_odasi) | 1 | 0 | 11.5, 7.5 | 0 | over f_L3_023 (0.72 m wide) |  |
| Banyo (r_L3_banyo) | 0 | 0 | - | 0 | - |  |
