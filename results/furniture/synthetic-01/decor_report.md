# Decor: synthetic-01

24 decor pieces (rule-based, `added_by_ai`, max 0.6 m except rugs and wall art). Cushions on sofas and beds, books on shelves and desks, one plant per living room or bedroom in a free corner (never on a door approach, a swing or a 0.9 m walkway). Rugs under the sofa + coffee table group, the lower two thirds of a double bed and dining tables (+ 0.6 m for the chairs), group + 0.3 m, inside the room shrunk by 0.3 m, never under a door swing; one wall art piece per living room, bedroom or dining room above a sofa, bed or dresser (0.25 m above its top, at most 0.6 x its width, never over a door or window; built only from a library model).

| Room | Cushions | Books | Plant | Rugs | Wall art | Note |
|---|---|---|---|---|---|---|
| Salon (r_L0_salon) | 2 | 1 | none | 1 | over f_L0_001 (1.32 m wide) | no free corner ((0.5, 0.5): windows_free; (5.0, 0.5): walkway; (5.0, 4.9): doors_free; (0.5, 4.9): no_overlap) |
| Yatak Odası (r_L0_yatak_odasi) | 2 | 0 | 5.6, 0.5 | 1 | over f_L0_006 (0.96 m wide) |  |
| Hol (r_L0_hol) | 0 | 0 | - | 0 | - |  |
| Banyo (r_L0_banyo) | 0 | 0 | - | 0 | - |  |
| Mutfak (r_L0_mutfak) | 0 | 0 | - | 0 | - | no rug under f_L0_019: cut to 2.10 x 0.76 m, below 0.8 m |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | 2 | 1 | 4.0, 0.5 | 1 | over f_L1_001 (1.08 m wide) |  |
| Hol (r_L1_hol) | 0 | 0 | - | 0 | - |  |
| Yatak Odası (r_L1_yatak_odasi) | 2 | 0 | 6.3, 0.5 | 1 | over f_L1_008 (1.08 m wide) |  |
| Banyo (r_L1_banyo) | 0 | 0 | - | 0 | - |  |
| Çocuk Odası (r_L1_cocuk_odasi) | 1 | 1 | none | 0 | over f_L1_016 (0.72 m wide) | no free corner ((0.5, 4.5): clearance of another piece; (4.0, 4.5): no_overlap; (4.0, 6.7): no_overlap; (0.5, 6.7): no_overlap) |
