# AI layout: synthetic-03

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L-1_hol) | hall | 2/2/0 (2.5 s) | 2/2/0 (2.6 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L-1_yatak_odasi) | bedroom | 6/4/2 (6.8 s) | 6/2/4 (7.0 s) | 1 | bed_double (0.9), nightstand (0.6), nightstand (0.9), desk (0.9) | ok |
| WC (r_L-1_wc) | wc | 2/2/0 (2.6 s) | 2/2/0 (2.5 s) | 1 | toilet (0.9), washbasin (0.6) | ok |
| Banyo (r_L-1_banyo) | bathroom | 3/3/0 (3.9 s) | 3/3/0 (3.7 s) | 1 | shower (0.9), toilet (0.6), washbasin (0.6) | ok |
| Hol (r_L0_hol) | hall | 2/2/0 (2.5 s) | 1/1/0 (1.4 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Antre (r_L0_antre) | hall | 2/1/1 (2.6 s) | 1/1/0 (1.4 s) | 2 | dresser (0.9) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/4/2 (6.9 s) | 6/4/2 (6.9 s) | 1 | bed_double (0.6), nightstand (0.6), nightstand (0.6), chair (0.6) | ok |
| Hol (r_L1_hol) | hall | 2/2/0 (2.5 s) | 1/1/0 (1.4 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/4/2 (6.9 s) | 6/4/2 (6.9 s) | 1 | bed_double (0.6), nightstand (0.6), nightstand (0.6), wardrobe (0.6) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 5/5/0 (5.8 s) | 6/6/0 (6.9 s) | 1 | bed_single (0.9), nightstand (0.9), wardrobe (0.9), desk (0.9), chair (0.9) | ok |
| Banyo (r_L1_banyo) | bathroom | 3/3/0 (3.8 s) | 3/3/0 (3.7 s) | 1 | shower (0.9), toilet (0.6), washbasin (0.9) | ok |

Repair steps of the chosen proposals: 112

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L-1_hol | snap | chair #1 | [5.95, 3.0] | [5.684, 3.299] | inside_room, doors_free |
| r_L-1_hol | slide | chair #1 | [5.684, 3.299] | [5.684, 3.599] | doors_free |
| r_L-1_hol | snap | dresser #0 | [4.35, 1.1] | [4.596, 1.1] | inside_room, wall_contact |
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
| r_L-1_yatak_odasi | snap | nightstand #2 | [7.5, 3.2] | [6.271, 3.2] | no_overlap, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | nightstand #2 | [6.271, 3.2] | [6.271, 4.3] | no_overlap, doors_free |
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
| r_L-1_wc | snap | toilet #0 | [7.4, 6.55] | [7.554, 6.55] | wall_contact |
| r_L-1_banyo | snap | shower #0 | [9.0, 6.55] | [9.479, 6.55] | doors_free, wall_contact |
| r_L-1_banyo | slide | shower #0 | [9.479, 6.55] | [9.479, 6.85] | doors_free |
| r_L-1_banyo | snap | washbasin #2 | [8.05, 5.55] | [8.296, 5.871] | inside_room, doors_free, wall_contact |
| r_L-1_banyo | slide | washbasin #2 | [8.296, 5.871] | [8.296, 7.229] | doors_free |
| r_L-1_banyo | snap | toilet #1 | [8.05, 6.55] | [8.421, 6.55] | inside_room, wall_contact |
| r_L0_hol | snap | chair #1 | [6.95, 3.5] | [6.682, 3.634] | inside_room, doors_free |
| r_L0_hol | snap | dresser #0 | [5.35, 1.5] | [5.596, 1.5] | inside_room, wall_contact |
| r_L0_antre | snap | dresser #0 | [3.65, 6.8] | [3.896, 6.8] | inside_room, doors_free, wall_contact |
| r_L0_antre | slide | dresser #0 | [3.896, 6.8] | [3.896, 6.8] | doors_free |
| r_L0_antre | relocate | dresser #0 | [3.896, 6.8] | [4.171, 5.296] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [2.55, 0.75] | [1.55, 0.75] | no_overlap, doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | desk #4 | [2.5, 0.8] | [2.5, 0.621] | clearance_ok, doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [2.5, 0.621] | [2.5, 0.621] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | shrink | desk #4 | [2.5, 0.621] | [2.5, 0.571] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [2.5, 0.571] | [2.5, 0.571] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | relocate | desk #4 | [2.5, 0.571] | [2.6, 3.779] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | snap | wardrobe #3 | [3.0, 1.5] | [3.929, 1.5] | doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | shrink | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | relocate | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | drop | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #2 | [1.25, 3.2] | [1.25, 3.929] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [1.25, 3.929] | [3.55, 3.929] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #1 | [0.75, 2.8] | [0.471, 2.8] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #1 | [0.471, 2.8] | [0.471, 1.1] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | bed_double #0 | [1.0, 3.0] | [1.171, 3.129] | inside_room, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | drop | desk #4 | [2.6, 3.779] | [2.6, 3.779] | no_overlap, clearance_ok |
| r_L1_hol | snap | chair #1 | [5.95, 3.0] | [5.684, 3.299] | inside_room |
| r_L1_hol | snap | dresser #0 | [4.35, 1.0] | [4.596, 1.0] | inside_room, wall_contact |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.0, 2.0] | [7.071, 2.0] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | relocate | bed_double #0 | [7.071, 2.0] | [7.871, 1.271] | doors_free |
| r_L1_yatak_odasi | anchor_first | bed_double #0 | [7.0, 2.0] | [7.871, 1.271] | - |
| r_L1_yatak_odasi | slide | chair #5 | [8.6, 2.8] | [8.3, 3.6] | no_overlap, doors_free |
| r_L1_yatak_odasi | shrink | chair #5 | [8.3, 3.6] | [8.3, 3.6] | doors_free |
| r_L1_yatak_odasi | slide | chair #5 | [8.3, 3.6] | [8.2, 3.6] | doors_free |
| r_L1_yatak_odasi | shrink | chair #5 | [8.2, 3.6] | [8.2, 3.6] | doors_free |
| r_L1_yatak_odasi | slide | chair #5 | [8.2, 3.6] | [8.1, 3.6] | doors_free |
| r_L1_yatak_odasi | drop | chair #5 | [8.1, 3.6] | [8.1, 3.6] | doors_free |
| r_L1_yatak_odasi | snap | desk #4 | [8.5, 3.0] | [8.5, 3.779] | clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | desk #4 | [8.5, 3.779] | [7.9, 3.779] | doors_free |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 3.5] | [6.371, 3.229] | inside_room, clearance_ok, wall_contact |
| r_L1_yatak_odasi | shrink | desk #4 | [7.9, 3.779] | [7.9, 3.829] | doors_free |
| r_L1_yatak_odasi | slide | desk #4 | [7.9, 3.829] | [8.0, 3.829] | doors_free |
| r_L1_yatak_odasi | relocate | desk #4 | [8.0, 3.829] | [8.0, 3.829] | doors_free |
| r_L1_yatak_odasi | drop | desk #4 | [8.0, 3.829] | [8.0, 3.829] | doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 3.229] | [6.371, 3.229] | doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 3.229] | [6.371, 3.229] | doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 3.229] | [6.371, 3.529] | doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [7.5, 2.0] | [6.271, 2.0] | no_overlap, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #2 | [6.271, 2.0] | [6.271, 0.8] | no_overlap, doors_free |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.5, 2.0] | [6.271, 2.0] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 2.0] | [6.271, 2.0] | doors_free |
| r_L1_yatak_odasi | shrink | nightstand #1 | [6.271, 2.0] | [6.271, 2.0] | doors_free |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 2.0] | [6.271, 2.0] | doors_free |
| r_L1_yatak_odasi | relocate | nightstand #1 | [6.271, 2.0] | [6.671, 0.471] | doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 3.529] | [6.971, 3.829] | doors_free |
| r_L1_cocuk_odasi | snap | chair #4 | [2.0, 4.0] | [2.072, 4.545] | inside_room, no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [2.072, 4.545] | [2.072, 5.145] | no_overlap |
| r_L1_cocuk_odasi | snap | desk #3 | [2.0, 4.5] | [2.0, 4.621] | inside_room, clearance_ok, wall_contact |
| r_L1_cocuk_odasi | shrink | chair #4 | [2.072, 5.145] | [2.072, 5.145] | no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [2.072, 5.145] | [2.072, 5.845] | no_overlap |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.621] | [2.3, 4.621] | clearance_ok |
| r_L1_cocuk_odasi | snap | wardrobe #2 | [3.0, 7.0] | [3.0, 7.229] | doors_free, windows_free, wall_contact |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.0, 7.229] | [3.0, 7.229] | windows_free |
| r_L1_cocuk_odasi | shrink | wardrobe #2 | [3.0, 7.229] | [3.0, 7.229] | windows_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.0, 7.229] | [3.5, 7.229] | windows_free |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.7, 6.5] | [0.471, 6.5] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 6.5] | [0.471, 4.6] | no_overlap |
| r_L1_banyo | snap | shower #0 | [7.0, 6.0] | [7.479, 6.0] | doors_free, wall_contact |
| r_L1_banyo | snap | washbasin #2 | [6.5, 4.5] | [6.5, 4.496] | inside_room, wall_contact |
| r_L1_banyo | snap | toilet #1 | [6.0, 6.5] | [6.421, 6.5] | inside_room, doors_free, wall_contact |
| r_L1_banyo | slide | shower #0 | [7.479, 6.0] | [7.479, 4.9] | doors_free |
| r_L1_banyo | slide | toilet #1 | [6.421, 6.5] | [6.421, 6.9] | doors_free |

Dropped pieces (chosen proposals):

- r_L-1_yatak_odasi: chair at [8.6, 3.3]: no repair left (doors_free)
- r_L-1_yatak_odasi: wardrobe at [6.0, 1.0]: no repair left (doors_free)
- r_L1_ebeveyn_yatak_odasi: wardrobe at [3.0, 1.5]: no repair left (doors_free)
- r_L1_ebeveyn_yatak_odasi: desk at [2.5, 0.8]: no repair left (no_overlap, clearance_ok)
- r_L1_yatak_odasi: chair at [8.6, 2.8]: no repair left (doors_free)
- r_L1_yatak_odasi: desk at [8.5, 3.0]: no repair left (doors_free)
