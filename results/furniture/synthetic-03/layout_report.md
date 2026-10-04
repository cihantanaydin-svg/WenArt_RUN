# AI layout: synthetic-03

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L-1_hol) | hall | 2/2/0 (2.7 s) | 2/2/0 (1.9 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L-1_yatak_odasi) | bedroom | 6/4/2 (5.2 s) | 6/4/2 (5.2 s) | 1 | bed_double (0.9), nightstand (0.6), nightstand (0.9), desk (0.9) | ok |
| WC (r_L-1_wc) | wc | 2/2/0 (1.9 s) | 2/2/0 (1.9 s) | 1 | toilet (0.9), washbasin (0.6) | ok |
| Banyo (r_L-1_banyo) | bathroom | 3/2/1 (2.8 s) | 3/3/0 (2.7 s) | 2 | shower (0.6), toilet (0.6), washbasin (0.6) | ok |
| Hol (r_L0_hol) | hall | 2/2/0 (1.9 s) | 1/1/0 (1.0 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Antre (r_L0_antre) | hall | 2/1/1 (1.9 s) | 1/1/0 (1.0 s) | 2 | dresser (0.9) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/4/2 (4.9 s) | 6/5/1 (5.1 s) | 2 | bed_double (0.6), nightstand (0.9), nightstand (0.6), wardrobe (0.6), desk (0.6) | ok |
| Hol (r_L1_hol) | hall | 2/2/0 (1.9 s) | 1/1/0 (1.0 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/4/2 (5.0 s) | 6/5/1 (5.2 s) | 2 | bed_double (0.9), nightstand (0.9), nightstand (0.6), desk (0.6), chair (0.6) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 6/6/0 (5.3 s) | 6/6/0 (5.3 s) | 1 | bed_single (0.9), nightstand (0.6), wardrobe (0.6), desk (0.6), chair (0.6), bookshelf (0.6) | ok |
| Banyo (r_L1_banyo) | bathroom | 3/3/0 (2.8 s) | 3/3/0 (2.7 s) | 1 | shower (0.9), washbasin (0.6), toilet (0.6) | ok |

Repair steps of the chosen proposals: 112

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L-1_hol | snap | chair #1 | [5.95, 3.0] | [5.684, 3.299] | inside_room, doors_free |
| r_L-1_hol | slide | chair #1 | [5.684, 3.299] | [5.684, 3.599] | doors_free |
| r_L-1_hol | snap | dresser #0 | [4.35, 1.0] | [4.596, 1.0] | inside_room, wall_contact |
| r_L-1_yatak_odasi | slide | chair #5 | [8.6, 3.3] | [8.6, 4.1] | no_overlap, doors_free |
| r_L-1_yatak_odasi | shrink | chair #5 | [8.6, 4.1] | [8.6, 4.1] | doors_free |
| r_L-1_yatak_odasi | slide | chair #5 | [8.6, 4.1] | [8.5, 4.1] | doors_free |
| r_L-1_yatak_odasi | shrink | chair #5 | [8.5, 4.1] | [8.5, 4.1] | doors_free |
| r_L-1_yatak_odasi | slide | chair #5 | [8.5, 4.1] | [8.4, 4.1] | doors_free |
| r_L-1_yatak_odasi | drop | chair #5 | [8.4, 4.1] | [8.4, 4.1] | doors_free |
| r_L-1_yatak_odasi | snap | desk #4 | [8.5, 3.5] | [9.579, 3.5] | no_overlap, clearance_ok, doors_free, wall_contact |
| r_L-1_yatak_odasi | snap | wardrobe #3 | [6.0, 1.0] | [6.371, 1.171] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | no_overlap, clearance_ok, doors_free |
| r_L-1_yatak_odasi | shrink | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | no_overlap, clearance_ok, doors_free |
| r_L-1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L-1_yatak_odasi | relocate | wardrobe #3 | [6.371, 1.171] | [6.671, 0.571] | doors_free |
| r_L-1_yatak_odasi | drop | wardrobe #3 | [6.671, 0.571] | [6.671, 0.571] | doors_free |
| r_L-1_yatak_odasi | snap | nightstand #2 | [7.5, 2.8] | [6.271, 2.8] | no_overlap, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | nightstand #2 | [6.271, 2.8] | [6.271, 4.3] | no_overlap, doors_free |
| r_L-1_yatak_odasi | snap | nightstand #1 | [6.5, 2.8] | [6.271, 2.8] | no_overlap, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | nightstand #1 | [6.271, 2.8] | [6.271, 1.1] | no_overlap, doors_free |
| r_L-1_yatak_odasi | snap | bed_double #0 | [7.0, 3.0] | [7.071, 3.0] | doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | shrink | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | slide | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | shrink | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | slide | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | relocate | bed_double #0 | [7.071, 3.0] | [7.471, 4.429] | doors_free |
| r_L-1_wc | snap | washbasin #1 | [6.5, 6.05] | [6.296, 6.05] | doors_free, wall_contact |
| r_L-1_wc | slide | washbasin #1 | [6.296, 6.05] | [6.296, 6.05] | doors_free |
| r_L-1_wc | shrink | washbasin #1 | [6.296, 6.05] | [6.271, 6.05] | doors_free |
| r_L-1_wc | slide | washbasin #1 | [6.271, 6.05] | [6.271, 6.05] | doors_free |
| r_L-1_wc | relocate | washbasin #1 | [6.271, 6.05] | [6.971, 5.796] | doors_free |
| r_L-1_wc | snap | toilet #0 | [7.2, 6.55] | [7.2, 7.154] | wall_contact |
| r_L-1_banyo | snap | shower #0 | [9.0, 7.0] | [9.479, 7.0] | wall_contact |
| r_L-1_banyo | snap | washbasin #2 | [8.5, 5.0] | [8.5, 5.796] | inside_room, wall_contact |
| r_L-1_banyo | slide | washbasin #2 | [8.5, 5.796] | [8.5, 5.796] | no_overlap, doors_free |
| r_L-1_banyo | shrink | washbasin #2 | [8.5, 5.796] | [8.5, 5.771] | no_overlap, doors_free |
| r_L-1_banyo | slide | washbasin #2 | [8.5, 5.771] | [8.5, 5.771] | no_overlap, doors_free |
| r_L-1_banyo | relocate | washbasin #2 | [8.5, 5.771] | [8.296, 6.671] | no_overlap, doors_free |
| r_L-1_banyo | snap | toilet #1 | [8.5, 6.0] | [8.421, 6.0] | doors_free, wall_contact |
| r_L-1_banyo | slide | toilet #1 | [8.421, 6.0] | [8.421, 7.2] | doors_free |
| r_L0_hol | snap | chair #1 | [6.95, 3.5] | [6.682, 3.634] | inside_room, doors_free |
| r_L0_hol | snap | dresser #0 | [5.35, 1.5] | [5.596, 1.5] | inside_room, wall_contact |
| r_L0_antre | snap | dresser #0 | [3.65, 6.8] | [3.896, 6.8] | inside_room, doors_free, wall_contact |
| r_L0_antre | slide | dresser #0 | [3.896, 6.8] | [3.896, 6.8] | doors_free |
| r_L0_antre | relocate | dresser #0 | [3.896, 6.8] | [4.171, 5.296] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [3.1, 1.6] | [3.1, 2.1] | no_overlap, doors_free |
| r_L1_ebeveyn_yatak_odasi | shrink | chair #5 | [3.1, 2.1] | [3.1, 2.1] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [3.1, 2.1] | [3.0, 2.1] | doors_free |
| r_L1_ebeveyn_yatak_odasi | shrink | chair #5 | [3.0, 2.1] | [3.0, 2.1] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [3.0, 2.1] | [2.9, 2.1] | doors_free |
| r_L1_ebeveyn_yatak_odasi | drop | chair #5 | [2.9, 2.1] | [2.9, 2.1] | doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | desk #4 | [3.0, 1.5] | [3.879, 1.5] | no_overlap, doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [3.879, 1.5] | [3.879, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | shrink | desk #4 | [3.879, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [3.929, 1.5] | [3.929, 3.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | wardrobe #3 | [0.5, 1.5] | [0.571, 1.5] | inside_room, no_overlap, clearance_ok, windows_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [0.571, 1.5] | [0.571, 1.5] | clearance_ok, windows_free |
| r_L1_ebeveyn_yatak_odasi | shrink | wardrobe #3 | [0.571, 1.5] | [0.571, 1.5] | clearance_ok, windows_free |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [0.571, 1.5] | [0.571, 0.9] | clearance_ok, windows_free |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #2 | [2.3, 2.5] | [2.3, 3.929] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #1 | [1.3, 2.5] | [0.471, 2.5] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | snap | bed_double #0 | [1.8, 2.5] | [1.8, 3.129] | doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [2.3, 3.929] | [0.6, 3.929] | no_overlap |
| r_L1_hol | snap | chair #1 | [5.95, 3.0] | [5.684, 3.299] | inside_room |
| r_L1_hol | snap | dresser #0 | [4.35, 1.0] | [4.596, 1.0] | inside_room, wall_contact |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.5, 2.5] | [7.5, 3.129] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.5, 3.129] | [7.5, 3.129] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.5, 3.129] | [7.5, 3.129] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.5, 3.129] | [7.8, 3.129] | doors_free |
| r_L1_yatak_odasi | anchor_first | bed_double #0 | [7.5, 2.5] | [7.8, 3.129] | - |
| r_L1_yatak_odasi | slide | chair #5 | [9.1, 1.7] | [9.1, 0.8] | no_overlap, doors_free |
| r_L1_yatak_odasi | snap | desk #4 | [9.0, 2.0] | [9.579, 2.0] | no_overlap, doors_free, wall_contact |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 1.0] | [6.371, 1.171] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | drop | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [8.2, 2.5] | [8.2, 3.929] | no_overlap, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #2 | [8.2, 3.929] | [6.7, 3.929] | no_overlap, doors_free |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.8, 2.5] | [6.271, 2.5] | no_overlap, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 2.5] | [6.271, 3.2] | doors_free |
| r_L1_yatak_odasi | slide | desk #4 | [9.579, 2.0] | [9.579, 2.0] | doors_free |
| r_L1_yatak_odasi | shrink | desk #4 | [9.579, 2.0] | [9.629, 2.0] | doors_free |
| r_L1_yatak_odasi | slide | desk #4 | [9.629, 2.0] | [9.629, 2.0] | doors_free |
| r_L1_yatak_odasi | relocate | desk #4 | [9.629, 2.0] | [8.129, 0.621] | doors_free |
| r_L1_cocuk_odasi | snap | bookshelf #5 | [0.5, 4.0] | [0.771, 4.446] | inside_room, wall_contact |
| r_L1_cocuk_odasi | snap | chair #4 | [2.0, 3.8] | [2.083, 4.495] | inside_room, no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [2.083, 4.495] | [2.083, 4.595] | no_overlap |
| r_L1_cocuk_odasi | snap | desk #3 | [2.0, 4.0] | [2.0, 4.621] | inside_room, clearance_ok, wall_contact |
| r_L1_cocuk_odasi | shrink | chair #4 | [2.083, 4.595] | [2.083, 4.595] | no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [2.083, 4.595] | [2.983, 4.595] | no_overlap |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.621] | [2.0, 4.621] | clearance_ok |
| r_L1_cocuk_odasi | shrink | desk #3 | [2.0, 4.621] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | relocate | desk #3 | [2.0, 4.571] | [2.2, 7.229] | clearance_ok |
| r_L1_cocuk_odasi | snap | wardrobe #2 | [3.0, 6.0] | [3.929, 6.0] | doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.929, 6.0] | [3.929, 6.0] | doors_free |
| r_L1_cocuk_odasi | shrink | wardrobe #2 | [3.929, 6.0] | [3.929, 6.0] | doors_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.929, 6.0] | [3.929, 6.0] | doors_free |
| r_L1_cocuk_odasi | relocate | wardrobe #2 | [3.929, 6.0] | [3.629, 7.229] | doors_free |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.8, 6.0] | [0.471, 6.0] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 6.0] | [0.471, 7.279] | no_overlap |
| r_L1_cocuk_odasi | snap | bed_single #0 | [1.0, 6.0] | [1.0, 6.529] | clearance_ok, wall_contact |
| r_L1_cocuk_odasi | shrink | nightstand #1 | [0.471, 7.279] | [0.471, 7.279] | no_overlap |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 7.279] | [0.471, 7.279] | no_overlap |
| r_L1_cocuk_odasi | relocate | nightstand #1 | [0.471, 7.279] | [1.571, 4.471] | no_overlap |
| r_L1_banyo | snap | shower #0 | [7.2, 6.0] | [7.479, 6.0] | no_overlap, doors_free, wall_contact |
| r_L1_banyo | slide | shower #0 | [7.479, 6.0] | [7.479, 6.3] | no_overlap |
| r_L1_banyo | snap | toilet #2 | [7.5, 5.5] | [7.579, 5.5] | wall_contact |
| r_L1_banyo | snap | washbasin #1 | [6.5, 4.5] | [6.296, 4.571] | wall_contact |

Dropped pieces (chosen proposals):

- r_L-1_yatak_odasi: chair at [8.6, 3.3]: no repair left (doors_free)
- r_L-1_yatak_odasi: wardrobe at [6.0, 1.0]: no repair left (doors_free)
- r_L1_ebeveyn_yatak_odasi: chair at [3.1, 1.6]: no repair left (doors_free)
- r_L1_yatak_odasi: wardrobe at [6.0, 1.0]: no repair left (doors_free)
