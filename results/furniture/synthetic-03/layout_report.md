# AI layout: synthetic-03

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L-1_hol) | hall | 2/2/0 (1.8 s) | 1/1/0 (0.9 s) | 1 | console_table (0.6), shoe_cabinet (0.6) | ok |
| Yatak Odası (r_L-1_yatak_odasi) | bedroom | 6/4/2 (4.8 s) | 6/4/2 (4.9 s) | 1 | bed_double (0.9), nightstand (0.9), nightstand (0.6), desk (0.9) | ok |
| WC (r_L-1_wc) | wc | 2/2/0 (1.8 s) | 2/2/0 (1.7 s) | 1 | toilet (0.9), washbasin (0.6) | ok |
| Banyo (r_L-1_banyo) | bathroom | 3/2/1 (2.5 s) | 3/3/0 (2.5 s) | 2 | shower (0.6), toilet (0.6), washbasin (0.6) | ok |
| Hol (r_L0_hol) | hall | 2/2/0 (1.7 s) | 1/1/0 (0.9 s) | 1 | console_table (0.9), shoe_cabinet (0.6) | ok |
| Antre (r_L0_antre) | hall | 3/2/1 (2.6 s) | 1/1/0 (0.9 s) | 2 | console_table (0.6) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/5/1 (4.6 s) | 6/6/0 (4.7 s) | 2 | bed_double (0.6), nightstand (0.9), nightstand (0.6), wardrobe (0.6), desk (0.6), office_chair (0.6) | ok |
| Hol (r_L1_hol) | hall | 2/2/0 (1.7 s) | 1/1/0 (0.9 s) | 1 | console_table (0.6), shoe_cabinet (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/4/2 (4.7 s) | 6/4/2 (4.8 s) | 1 | bed_double (0.9), nightstand (0.9), nightstand (0.9), wardrobe (0.9) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 5/5/0 (3.8 s) | 5/5/0 (4.2 s) | 1 | bed_single (0.9), nightstand (0.6), wardrobe (0.6), desk (0.9), office_chair (0.9) | ok |
| Banyo (r_L1_banyo) | bathroom | 3/3/0 (2.6 s) | 3/3/0 (2.5 s) | 1 | shower (0.9), washbasin (0.6), toilet (0.6) | ok |

Repair steps of the chosen proposals: 117

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L-1_hol | snap | shoe_cabinet #1 | [4.35, 5.7] | [4.531, 5.7] | inside_room, doors_free, wall_contact |
| r_L-1_hol | slide | shoe_cabinet #1 | [4.531, 5.7] | [4.531, 4.9] | doors_free |
| r_L-1_hol | snap | console_table #0 | [4.35, 2.0] | [4.546, 2.0] | inside_room, doors_free, wall_contact |
| r_L-1_hol | slide | console_table #0 | [4.546, 2.0] | [4.546, 1.0] | doors_free |
| r_L-1_yatak_odasi | slide | office_chair #5 | [8.5, 3.2] | [8.5, 2.8] | no_overlap, doors_free |
| r_L-1_yatak_odasi | shrink | office_chair #5 | [8.5, 2.8] | [8.5, 2.8] | doors_free |
| r_L-1_yatak_odasi | slide | office_chair #5 | [8.5, 2.8] | [8.4, 2.8] | doors_free |
| r_L-1_yatak_odasi | drop | office_chair #5 | [8.4, 2.8] | [8.4, 2.8] | doors_free |
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
| r_L0_hol | snap | shoe_cabinet #1 | [5.35, 1.5] | [5.531, 1.5] | inside_room, wall_contact |
| r_L0_hol | snap | console_table #0 | [5.35, 7.2] | [5.546, 6.929] | inside_room, doors_free, wall_contact |
| r_L0_hol | slide | console_table #0 | [5.546, 6.929] | [5.546, 4.829] | doors_free |
| r_L0_antre | snap | console_table #0 | [3.65, 6.8] | [3.846, 6.8] | inside_room, doors_free, wall_contact |
| r_L0_antre | slide | console_table #0 | [3.846, 6.8] | [3.846, 6.8] | doors_free |
| r_L0_antre | shrink | console_table #0 | [3.846, 6.8] | [3.821, 6.8] | doors_free |
| r_L0_antre | slide | console_table #0 | [3.821, 6.8] | [3.821, 6.8] | doors_free |
| r_L0_antre | relocate | console_table #0 | [3.821, 6.8] | [4.271, 5.246] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | office_chair #5 | [3.1, 3.0] | [3.1, 3.7] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | desk #4 | [3.0, 3.0] | [3.0, 3.779] | no_overlap, clearance_ok, doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | shrink | office_chair #5 | [3.1, 3.7] | [3.1, 3.7] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | office_chair #5 | [3.1, 3.7] | [3.1, 3.1] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [3.0, 3.779] | [3.4, 3.779] | no_overlap, clearance_ok |
| r_L1_ebeveyn_yatak_odasi | snap | wardrobe #3 | [0.25, 1.0] | [0.571, 1.171] | inside_room, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [0.571, 1.171] | [0.571, 1.171] | clearance_ok, windows_free |
| r_L1_ebeveyn_yatak_odasi | shrink | wardrobe #3 | [0.571, 1.171] | [0.571, 1.171] | clearance_ok, windows_free |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [0.571, 1.171] | [0.571, 0.871] | clearance_ok, windows_free |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #2 | [2.3, 2.5] | [2.3, 3.929] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #1 | [1.3, 2.5] | [0.471, 2.5] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | snap | bed_double #0 | [1.8, 2.5] | [1.8, 3.129] | doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [2.3, 3.929] | [0.6, 3.929] | no_overlap |
| r_L1_hol | snap | shoe_cabinet #1 | [4.35, 6.5] | [4.531, 6.5] | inside_room, wall_contact |
| r_L1_hol | slide | shoe_cabinet #1 | [4.531, 6.5] | [4.531, 6.7] | doors_free |
| r_L1_hol | snap | console_table #0 | [4.35, 1.0] | [4.546, 1.0] | inside_room, wall_contact |
| r_L1_hol | slide | console_table #0 | [4.546, 1.0] | [4.546, 0.9] | doors_free |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.0, 2.0] | [7.071, 2.0] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | shrink | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.071, 2.0] | [7.071, 2.0] | doors_free |
| r_L1_yatak_odasi | relocate | bed_double #0 | [7.071, 2.0] | [7.871, 1.271] | doors_free |
| r_L1_yatak_odasi | anchor_first | bed_double #0 | [7.0, 2.0] | [7.871, 1.271] | - |
| r_L1_yatak_odasi | slide | office_chair #5 | [8.5, 2.3] | [9.1, 1.8] | no_overlap |
| r_L1_yatak_odasi | snap | desk #4 | [8.5, 2.5] | [8.5, 3.779] | no_overlap, clearance_ok, wall_contact |
| r_L1_yatak_odasi | shrink | office_chair #5 | [9.1, 1.8] | [9.1, 1.8] | doors_free |
| r_L1_yatak_odasi | slide | office_chair #5 | [9.1, 1.8] | [9.1, 1.7] | doors_free |
| r_L1_yatak_odasi | drop | office_chair #5 | [9.1, 1.7] | [9.1, 1.7] | doors_free |
| r_L1_yatak_odasi | slide | desk #4 | [8.5, 3.779] | [7.9, 3.779] | doors_free |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 3.5] | [6.371, 3.229] | inside_room, clearance_ok, wall_contact |
| r_L1_yatak_odasi | shrink | desk #4 | [7.9, 3.779] | [7.9, 3.829] | doors_free |
| r_L1_yatak_odasi | slide | desk #4 | [7.9, 3.829] | [8.0, 3.829] | doors_free |
| r_L1_yatak_odasi | relocate | desk #4 | [8.0, 3.829] | [8.0, 3.829] | doors_free |
| r_L1_yatak_odasi | drop | desk #4 | [8.0, 3.829] | [8.0, 3.829] | doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 3.229] | [6.371, 3.229] | doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 3.229] | [6.371, 3.229] | doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 3.229] | [6.371, 3.529] | doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [7.5, 1.9] | [6.271, 1.9] | no_overlap, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #2 | [6.271, 1.9] | [6.271, 0.8] | no_overlap, doors_free |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.5, 1.9] | [6.271, 1.9] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 1.9] | [6.271, 1.9] | doors_free |
| r_L1_yatak_odasi | shrink | nightstand #1 | [6.271, 1.9] | [6.271, 1.9] | doors_free |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 1.9] | [6.271, 1.9] | doors_free |
| r_L1_yatak_odasi | relocate | nightstand #1 | [6.271, 1.9] | [6.671, 0.471] | doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 3.529] | [6.971, 3.829] | doors_free |
| r_L1_cocuk_odasi | snap | office_chair #4 | [2.0, 4.2] | [2.058, 4.596] | inside_room, no_overlap |
| r_L1_cocuk_odasi | slide | office_chair #4 | [2.058, 4.596] | [3.058, 4.596] | no_overlap |
| r_L1_cocuk_odasi | snap | desk #3 | [2.0, 4.5] | [2.0, 4.621] | inside_room, clearance_ok, wall_contact |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.621] | [2.0, 4.621] | clearance_ok |
| r_L1_cocuk_odasi | shrink | desk #3 | [2.0, 4.621] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | relocate | desk #3 | [2.0, 4.571] | [2.2, 7.229] | clearance_ok |
| r_L1_cocuk_odasi | snap | wardrobe #2 | [3.0, 6.0] | [3.929, 6.0] | doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.929, 6.0] | [3.929, 6.0] | doors_free |
| r_L1_cocuk_odasi | shrink | wardrobe #2 | [3.929, 6.0] | [3.929, 6.0] | doors_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.929, 6.0] | [3.929, 6.0] | doors_free |
| r_L1_cocuk_odasi | relocate | wardrobe #2 | [3.929, 6.0] | [3.629, 7.229] | doors_free |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.8, 5.8] | [0.471, 5.8] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 5.8] | [0.471, 7.279] | no_overlap |
| r_L1_cocuk_odasi | snap | bed_single #0 | [1.0, 6.0] | [1.0, 6.529] | wall_contact |
| r_L1_cocuk_odasi | shrink | nightstand #1 | [0.471, 7.279] | [0.471, 7.279] | no_overlap |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 7.279] | [0.471, 7.279] | no_overlap |
| r_L1_cocuk_odasi | relocate | nightstand #1 | [0.471, 7.279] | [0.521, 4.471] | no_overlap |
| r_L1_banyo | snap | shower #0 | [7.2, 6.0] | [7.479, 6.0] | no_overlap, doors_free, wall_contact |
| r_L1_banyo | slide | shower #0 | [7.479, 6.0] | [7.479, 6.3] | no_overlap |
| r_L1_banyo | snap | toilet #2 | [7.5, 5.5] | [7.579, 5.5] | wall_contact |
| r_L1_banyo | snap | washbasin #1 | [6.5, 4.5] | [6.296, 4.571] | wall_contact |

Dropped pieces (chosen proposals):

- r_L-1_yatak_odasi: office_chair at [8.5, 3.2]: no repair left (doors_free)
- r_L-1_yatak_odasi: wardrobe at [6.0, 1.0]: no repair left (doors_free)
- r_L1_yatak_odasi: office_chair at [8.5, 2.3]: no repair left (doors_free)
- r_L1_yatak_odasi: desk at [8.5, 2.5]: no repair left (doors_free)
