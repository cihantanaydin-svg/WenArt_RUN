# AI layout: synthetic-03

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L-1_hol) | hall | 2/2/0 (1.9 s) | 1/1/0 (1.0 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L-1_yatak_odasi) | bedroom | 6/4/2 (5.1 s) | 6/4/2 (5.3 s) | 1 | bed_double (0.9), nightstand (0.9), nightstand (0.9), desk (0.9) | ok |
| WC (r_L-1_wc) | wc | 2/2/0 (2.0 s) | 2/2/0 (2.0 s) | 1 | toilet (0.9), washbasin (0.6) | ok |
| Banyo (r_L-1_banyo) | bathroom | 3/3/0 (2.8 s) | 3/3/0 (2.8 s) | 1 | shower (0.6), toilet (0.6), washbasin (0.6) | ok |
| Hol (r_L0_hol) | hall | 2/2/0 (2.0 s) | 1/1/0 (1.1 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Antre (r_L0_antre) | hall | 2/1/1 (2.0 s) | 1/1/0 (1.1 s) | 2 | dresser (0.9) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/4/2 (5.3 s) | 6/6/0 (5.3 s) | 2 | bed_double (0.9), nightstand (0.9), nightstand (0.9), wardrobe (0.9), desk (0.6), chair (0.6) | ok |
| Hol (r_L1_hol) | hall | 2/2/0 (2.0 s) | 1/1/0 (1.0 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/5/1 (5.3 s) | 6/4/2 (5.3 s) | 1 | bed_double (0.6), nightstand (0.6), nightstand (0.6), wardrobe (0.6), desk (0.6) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 6/6/0 (5.2 s) | 6/5/1 (5.6 s) | 1 | bed_single (0.9), nightstand (0.9), nightstand (0.9), wardrobe (0.6), desk (0.6), chair (0.6) | ok |
| Banyo (r_L1_banyo) | bathroom | 3/3/0 (2.9 s) | 3/3/0 (2.9 s) | 1 | shower (0.6), washbasin (0.6), toilet (0.6) | ok |

Repair steps of the chosen proposals: 110

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L-1_hol | snap | chair #1 | [4.35, 4.8] | [4.616, 4.501] | inside_room |
| r_L-1_hol | snap | dresser #0 | [4.35, 1.1] | [4.596, 1.1] | inside_room, wall_contact |
| r_L-1_yatak_odasi | slide | chair #5 | [9.1, 3.3] | [9.1, 4.1] | no_overlap, doors_free |
| r_L-1_yatak_odasi | shrink | chair #5 | [9.1, 4.1] | [9.1, 4.1] | doors_free |
| r_L-1_yatak_odasi | slide | chair #5 | [9.1, 4.1] | [9.0, 4.1] | doors_free |
| r_L-1_yatak_odasi | shrink | chair #5 | [9.0, 4.1] | [9.0, 4.1] | doors_free |
| r_L-1_yatak_odasi | slide | chair #5 | [9.0, 4.1] | [8.9, 4.1] | doors_free |
| r_L-1_yatak_odasi | drop | chair #5 | [8.9, 4.1] | [8.9, 4.1] | doors_free |
| r_L-1_yatak_odasi | snap | desk #4 | [9.0, 3.5] | [9.579, 3.5] | doors_free, wall_contact |
| r_L-1_yatak_odasi | snap | wardrobe #3 | [6.0, 1.0] | [6.371, 1.171] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | no_overlap, clearance_ok, doors_free |
| r_L-1_yatak_odasi | shrink | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | no_overlap, clearance_ok, doors_free |
| r_L-1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L-1_yatak_odasi | relocate | wardrobe #3 | [6.371, 1.171] | [6.671, 0.571] | doors_free |
| r_L-1_yatak_odasi | drop | wardrobe #3 | [6.671, 0.571] | [6.671, 0.571] | doors_free |
| r_L-1_yatak_odasi | snap | nightstand #2 | [7.5, 3.0] | [6.271, 3.0] | no_overlap, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | nightstand #2 | [6.271, 3.0] | [6.271, 4.3] | no_overlap, doors_free |
| r_L-1_yatak_odasi | snap | nightstand #1 | [6.5, 3.0] | [6.271, 3.0] | no_overlap, doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | nightstand #1 | [6.271, 3.0] | [6.271, 4.8] | no_overlap, doors_free |
| r_L-1_yatak_odasi | snap | bed_double #0 | [7.0, 3.0] | [7.071, 3.0] | doors_free, wall_contact |
| r_L-1_yatak_odasi | slide | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | shrink | bed_double #0 | [7.071, 3.0] | [7.071, 3.0] | doors_free |
| r_L-1_yatak_odasi | slide | bed_double #0 | [7.071, 3.0] | [7.071, 1.1] | doors_free |
| r_L-1_wc | snap | washbasin #1 | [6.5, 6.05] | [6.296, 6.05] | doors_free, wall_contact |
| r_L-1_wc | slide | washbasin #1 | [6.296, 6.05] | [6.296, 6.05] | doors_free |
| r_L-1_wc | shrink | washbasin #1 | [6.296, 6.05] | [6.271, 6.05] | doors_free |
| r_L-1_wc | slide | washbasin #1 | [6.271, 6.05] | [6.271, 6.05] | doors_free |
| r_L-1_wc | relocate | washbasin #1 | [6.271, 6.05] | [6.971, 5.796] | doors_free |
| r_L-1_wc | snap | toilet #0 | [7.4, 6.55] | [7.554, 6.55] | wall_contact |
| r_L-1_banyo | snap | shower #0 | [8.5, 6.5] | [8.471, 6.5] | doors_free, wall_contact |
| r_L-1_banyo | slide | shower #0 | [8.471, 6.5] | [8.471, 6.8] | doors_free |
| r_L-1_banyo | snap | washbasin #2 | [8.0, 5.8] | [8.296, 5.871] | inside_room, doors_free, wall_contact |
| r_L-1_banyo | slide | washbasin #2 | [8.296, 5.871] | [8.296, 5.871] | doors_free |
| r_L-1_banyo | shrink | washbasin #2 | [8.296, 5.871] | [8.271, 5.871] | doors_free |
| r_L-1_banyo | slide | washbasin #2 | [8.271, 5.871] | [8.271, 5.871] | doors_free |
| r_L-1_banyo | relocate | washbasin #2 | [8.271, 5.871] | [9.704, 6.671] | doors_free |
| r_L-1_banyo | snap | toilet #1 | [9.3, 6.0] | [9.579, 6.0] | doors_free, wall_contact |
| r_L-1_banyo | slide | toilet #1 | [9.579, 6.0] | [9.579, 7.2] | doors_free |
| r_L0_hol | snap | chair #1 | [6.95, 4.0] | [6.702, 3.969] | inside_room |
| r_L0_hol | snap | dresser #0 | [5.35, 1.5] | [5.596, 1.5] | inside_room, wall_contact |
| r_L0_antre | snap | dresser #0 | [3.65, 6.8] | [3.896, 6.8] | inside_room, doors_free, wall_contact |
| r_L0_antre | slide | dresser #0 | [3.896, 6.8] | [3.896, 6.8] | doors_free |
| r_L0_antre | relocate | dresser #0 | [3.896, 6.8] | [4.171, 5.296] | doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | chair #5 | [2.0, 0.3] | [2.033, 0.548] | inside_room, no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [2.033, 0.548] | [1.833, 1.148] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | desk #4 | [2.0, 0.5] | [2.0, 0.621] | inside_room, no_overlap, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | shrink | chair #5 | [1.833, 1.148] | [1.833, 1.148] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [1.833, 1.148] | [2.133, 1.848] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [2.0, 0.621] | [1.4, 0.621] | no_overlap, clearance_ok |
| r_L1_ebeveyn_yatak_odasi | snap | wardrobe #3 | [3.0, 1.0] | [3.0, 0.571] | clearance_ok, doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [3.0, 0.571] | [3.0, 0.571] | windows_free |
| r_L1_ebeveyn_yatak_odasi | shrink | wardrobe #3 | [3.0, 0.571] | [3.0, 0.571] | windows_free |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [3.0, 0.571] | [3.0, 0.571] | windows_free |
| r_L1_ebeveyn_yatak_odasi | relocate | wardrobe #3 | [3.0, 0.571] | [3.0, 3.829] | windows_free |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #2 | [1.4, 3.0] | [1.4, 3.929] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [1.4, 3.929] | [1.4, 3.929] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | shrink | nightstand #2 | [1.4, 3.929] | [1.4, 3.929] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [1.4, 3.929] | [1.4, 3.929] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | relocate | nightstand #2 | [1.4, 3.929] | [2.4, 0.471] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #1 | [0.6, 3.0] | [0.471, 3.0] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #1 | [0.471, 3.0] | [0.471, 1.1] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | bed_double #0 | [1.0, 3.0] | [1.171, 3.129] | inside_room, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | bed_double #0 | [1.171, 3.129] | [1.171, 3.129] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | shrink | bed_double #0 | [1.171, 3.129] | [1.171, 3.129] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | slide | bed_double #0 | [1.171, 3.129] | [1.071, 3.129] | clearance_ok |
| r_L1_hol | snap | chair #1 | [5.95, 3.0] | [5.651, 3.336] | inside_room |
| r_L1_hol | snap | dresser #0 | [4.35, 1.0] | [4.596, 1.0] | inside_room, wall_contact |
| r_L1_yatak_odasi | slide | chair #5 | [8.5, 2.3] | [8.5, 3.1] | no_overlap, doors_free |
| r_L1_yatak_odasi | shrink | chair #5 | [8.5, 3.1] | [8.5, 3.1] | doors_free |
| r_L1_yatak_odasi | slide | chair #5 | [8.5, 3.1] | [8.4, 3.1] | doors_free |
| r_L1_yatak_odasi | shrink | chair #5 | [8.4, 3.1] | [8.4, 3.1] | doors_free |
| r_L1_yatak_odasi | slide | chair #5 | [8.4, 3.1] | [8.3, 3.1] | doors_free |
| r_L1_yatak_odasi | drop | chair #5 | [8.3, 3.1] | [8.3, 3.1] | doors_free |
| r_L1_yatak_odasi | snap | desk #4 | [8.5, 2.5] | [8.5, 3.779] | no_overlap, clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | desk #4 | [8.5, 3.779] | [8.5, 3.779] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | shrink | desk #4 | [8.5, 3.779] | [8.5, 3.829] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | slide | desk #4 | [8.5, 3.829] | [8.5, 3.829] | doors_free |
| r_L1_yatak_odasi | relocate | desk #4 | [8.5, 3.829] | [9.579, 2.529] | doors_free |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 1.0] | [6.371, 1.171] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 1.171] | [9.629, 1.171] | doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [7.5, 3.0] | [7.5, 3.929] | no_overlap, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #2 | [7.5, 3.929] | [9.679, 3.929] | no_overlap |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.5, 3.0] | [6.271, 3.0] | no_overlap, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 3.0] | [6.271, 0.8] | no_overlap, doors_free |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.0, 3.0] | [7.0, 3.129] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.0, 3.129] | [7.0, 3.129] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.0, 3.129] | [7.0, 3.129] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.0, 3.129] | [7.0, 3.129] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.0, 3.129] | [7.0, 3.129] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.0, 3.129] | [7.0, 3.129] | doors_free |
| r_L1_yatak_odasi | relocate | bed_double #0 | [7.0, 3.129] | [7.8, 1.271] | doors_free |
| r_L1_cocuk_odasi | snap | chair #5 | [2.5, 4.2] | [2.449, 4.546] | inside_room |
| r_L1_cocuk_odasi | slide | chair #5 | [2.449, 4.546] | [1.549, 4.546] | no_overlap |
| r_L1_cocuk_odasi | snap | desk #4 | [2.5, 4.8] | [2.5, 4.621] | clearance_ok, wall_contact |
| r_L1_cocuk_odasi | snap | wardrobe #3 | [3.5, 6.5] | [3.929, 6.5] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | wardrobe #3 | [3.929, 6.5] | [3.929, 6.5] | doors_free |
| r_L1_cocuk_odasi | shrink | wardrobe #3 | [3.929, 6.5] | [3.929, 6.5] | doors_free |
| r_L1_cocuk_odasi | slide | wardrobe #3 | [3.929, 6.5] | [3.929, 6.5] | doors_free |
| r_L1_cocuk_odasi | relocate | wardrobe #3 | [3.929, 6.5] | [3.629, 7.229] | doors_free |
| r_L1_cocuk_odasi | snap | nightstand #2 | [1.6, 6.5] | [1.6, 7.329] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #2 | [1.6, 7.329] | [2.0, 7.329] | no_overlap |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.6, 6.5] | [0.471, 6.5] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 6.5] | [0.471, 4.6] | no_overlap |
| r_L1_banyo | snap | shower #0 | [7.0, 6.0] | [7.479, 6.0] | doors_free, wall_contact |
| r_L1_banyo | snap | toilet #2 | [7.0, 4.5] | [7.0, 4.621] | inside_room, wall_contact |
| r_L1_banyo | snap | washbasin #1 | [6.0, 5.0] | [6.296, 5.0] | inside_room, doors_free, wall_contact |
| r_L1_banyo | slide | washbasin #1 | [6.296, 5.0] | [6.296, 4.8] | doors_free |

Dropped pieces (chosen proposals):

- r_L-1_yatak_odasi: chair at [9.1, 3.3]: no repair left (doors_free)
- r_L-1_yatak_odasi: wardrobe at [6.0, 1.0]: no repair left (doors_free)
- r_L1_yatak_odasi: chair at [8.5, 2.3]: no repair left (doors_free)
