# AI layout: synthetic-01

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L0_hol) | hall | 3/2/1 (2.7 s) | 1/1/0 (1.0 s) | 2 | console_table (0.9) | ok |
| Mutfak (r_L0_mutfak) | kitchen | 12/3/9 (10.3 s) | 5/4/1 (4.4 s) | 2 | kitchen_counter (0.6), sink_kitchen (0.6), fridge (0.9), tall_cabinet (0.9) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/6/0 (5.1 s) | 6/5/1 (5.2 s) | 1 | bed_double (0.6), nightstand (0.9), nightstand (0.6), wardrobe (0.6), desk (0.6), office_chair (0.6) | ok |
| Hol (r_L1_hol) | hall | 3/3/0 (2.8 s) | 1/1/0 (1.0 s) | 1 | console_table (0.9), shoe_cabinet (0.6), bench (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/3/3 (5.1 s) | 6/3/3 (5.2 s) | 1 | bed_double (0.9), nightstand (0.6), nightstand (0.6) | ok |
| Banyo (r_L1_banyo) | bathroom | 4/4/0 (3.7 s) | 3/3/0 (2.7 s) | 1 | shower (0.9), toilet (0.6), washbasin (0.6), bathtub (0.6) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 6/4/2 (5.1 s) | 5/4/1 (4.3 s) | 2 | bed_single (0.9), nightstand (0.6), wardrobe (0.9), desk (0.6) | ok |

Repair steps of the chosen proposals: 99

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_hol | snap | console_table #0 | [5.35, 6.95] | [5.971, 6.754] | inside_room, doors_free, wall_contact |
| r_L0_hol | slide | console_table #0 | [5.971, 6.754] | [5.971, 6.754] | doors_free |
| r_L0_hol | shrink | console_table #0 | [5.971, 6.754] | [5.971, 6.779] | doors_free |
| r_L0_hol | slide | console_table #0 | [5.971, 6.779] | [5.971, 6.779] | doors_free |
| r_L0_hol | relocate | console_table #0 | [5.971, 6.779] | [6.779, 4.479] | doors_free |
| r_L0_mutfak | snap | tall_cabinet #4 | [0.25, 6.95] | [0.571, 6.629] | inside_room, no_overlap, clearance_ok, wall_contact |
| r_L0_mutfak | slide | tall_cabinet #4 | [0.571, 6.629] | [0.571, 6.629] | no_overlap |
| r_L0_mutfak | shrink | tall_cabinet #4 | [0.571, 6.629] | [0.571, 6.639] | no_overlap |
| r_L0_mutfak | slide | tall_cabinet #4 | [0.571, 6.639] | [0.871, 6.639] | no_overlap |
| r_L0_mutfak | snap | fridge #3 | [0.25, 6.95] | [0.621, 6.579] | inside_room, wall_contact |
| r_L0_mutfak | relocate | tall_cabinet #4 | [0.871, 6.639] | [0.571, 5.839] | no_overlap, clearance_ok |
| r_L0_mutfak | snap | stove #2 | [2.75, 6.95] | [2.75, 6.629] | inside_room, no_overlap, wall_contact |
| r_L0_mutfak | slide | stove #2 | [2.75, 6.629] | [2.75, 6.629] | no_overlap |
| r_L0_mutfak | shrink | stove #2 | [2.75, 6.629] | [2.75, 6.629] | no_overlap |
| r_L0_mutfak | slide | stove #2 | [2.75, 6.629] | [2.75, 6.629] | no_overlap |
| r_L0_mutfak | relocate | stove #2 | [2.75, 6.629] | [2.75, 5.571] | no_overlap |
| r_L0_mutfak | snap | sink_kitchen #1 | [2.75, 6.95] | [2.75, 6.679] | inside_room, no_overlap, wall_contact |
| r_L0_mutfak | slide | sink_kitchen #1 | [2.75, 6.679] | [2.75, 6.679] | no_overlap |
| r_L0_mutfak | relocate | sink_kitchen #1 | [2.75, 6.679] | [2.15, 5.521] | no_overlap |
| r_L0_mutfak | snap | kitchen_counter #0 | [2.75, 6.95] | [2.75, 6.629] | inside_room, wall_contact |
| r_L0_mutfak | drop | stove #2 | [2.75, 5.571] | [2.75, 5.571] | doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | office_chair #5 | [0.5, 1.2] | [0.587, 1.25] | inside_room, no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | office_chair #5 | [0.587, 1.25] | [0.587, 0.85] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | desk #4 | [0.5, 1.5] | [0.571, 1.5] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | shrink | office_chair #5 | [0.587, 0.85] | [0.587, 0.85] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | office_chair #5 | [0.587, 0.85] | [0.587, 0.55] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [0.571, 1.5] | [0.571, 1.5] | no_overlap, clearance_ok, doors_free |
| r_L1_ebeveyn_yatak_odasi | relocate | desk #4 | [0.571, 1.5] | [1.471, 0.571] | no_overlap, clearance_ok, doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | wardrobe #3 | [3.0, 1.5] | [3.929, 1.5] | doors_free, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | shrink | wardrobe #3 | [3.929, 1.5] | [3.929, 1.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | wardrobe #3 | [3.929, 1.5] | [3.929, 3.5] | doors_free |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #2 | [1.5, 3.5] | [1.5, 3.929] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [1.5, 3.929] | [2.7, 3.929] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #1 | [1.5, 2.5] | [0.471, 2.5] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #1 | [0.471, 2.5] | [0.471, 1.1] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | bed_double #0 | [1.5, 3.0] | [1.5, 3.129] | wall_contact |
| r_L1_hol | snap | bench #2 | [5.95, 3.0] | [5.729, 3.0] | inside_room, wall_contact |
| r_L1_hol | slide | bench #2 | [5.729, 3.0] | [5.729, 3.1] | doors_free |
| r_L1_hol | snap | shoe_cabinet #1 | [4.35, 5.5] | [4.531, 5.5] | inside_room, doors_free, wall_contact |
| r_L1_hol | slide | shoe_cabinet #1 | [4.531, 5.5] | [4.531, 6.3] | doors_free |
| r_L1_hol | snap | console_table #0 | [4.35, 1.0] | [4.546, 1.0] | inside_room, wall_contact |
| r_L1_hol | slide | console_table #0 | [4.546, 1.0] | [4.546, 0.9] | doors_free |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.0, 2.5] | [7.0, 2.929] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.0, 2.929] | [7.9, 2.929] | doors_free |
| r_L1_yatak_odasi | anchor_first | bed_double #0 | [7.0, 2.5] | [7.9, 2.929] | - |
| r_L1_yatak_odasi | slide | office_chair #5 | [8.0, 1.7] | [8.0, 1.0] | no_overlap |
| r_L1_yatak_odasi | shrink | office_chair #5 | [8.0, 1.0] | [8.0, 1.0] | doors_free |
| r_L1_yatak_odasi | slide | office_chair #5 | [8.0, 1.0] | [7.9, 1.0] | doors_free |
| r_L1_yatak_odasi | drop | office_chair #5 | [7.9, 1.0] | [7.9, 1.0] | doors_free |
| r_L1_yatak_odasi | snap | desk #4 | [8.0, 2.0] | [8.979, 2.0] | no_overlap, wall_contact |
| r_L1_yatak_odasi | slide | desk #4 | [8.979, 2.0] | [8.979, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | shrink | desk #4 | [8.979, 2.0] | [9.029, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | slide | desk #4 | [9.029, 2.0] | [9.029, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | relocate | desk #4 | [9.029, 2.0] | [8.629, 0.621] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | drop | desk #4 | [8.629, 0.621] | [8.629, 0.621] | doors_free |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 1.0] | [6.371, 1.171] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | clearance_ok, doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | clearance_ok, doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | drop | wardrobe #3 | [6.371, 1.171] | [6.371, 1.171] | doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [7.5, 2.5] | [7.5, 3.729] | no_overlap, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #2 | [7.5, 3.729] | [6.7, 3.729] | no_overlap |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.5, 2.5] | [6.271, 2.5] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 2.5] | [6.271, 3.2] | doors_free |
| r_L1_banyo | snap | bathtub #3 | [8.0, 6.0] | [8.0, 6.554] | doors_free, wall_contact |
| r_L1_banyo | slide | bathtub #3 | [8.0, 6.554] | [7.9, 6.554] | doors_free |
| r_L1_banyo | shrink | bathtub #3 | [7.9, 6.554] | [7.9, 6.579] | doors_free |
| r_L1_banyo | slide | bathtub #3 | [7.9, 6.579] | [7.8, 6.579] | doors_free |
| r_L1_banyo | relocate | bathtub #3 | [7.8, 6.579] | [8.954, 6.079] | doors_free |
| r_L1_banyo | snap | shower #0 | [7.0, 5.5] | [6.521, 5.5] | no_overlap, doors_free, wall_contact |
| r_L1_banyo | slide | shower #0 | [6.521, 5.5] | [6.521, 5.5] | no_overlap, doors_free |
| r_L1_banyo | shrink | shower #0 | [6.521, 5.5] | [6.471, 5.5] | no_overlap, doors_free |
| r_L1_banyo | slide | shower #0 | [6.471, 5.5] | [6.471, 5.5] | no_overlap, doors_free |
| r_L1_banyo | relocate | shower #0 | [6.471, 5.5] | [7.171, 4.521] | no_overlap, doors_free |
| r_L1_banyo | snap | washbasin #2 | [6.0, 4.5] | [6.296, 4.5] | inside_room, doors_free, wall_contact |
| r_L1_banyo | slide | washbasin #2 | [6.296, 4.5] | [6.296, 4.4] | doors_free |
| r_L1_banyo | snap | toilet #1 | [6.5, 6.2] | [6.5, 6.579] | doors_free, wall_contact |
| r_L1_banyo | slide | toilet #1 | [6.5, 6.579] | [6.6, 6.579] | doors_free |
| r_L1_cocuk_odasi | slide | office_chair #4 | [2.5, 6.0] | [2.3, 5.8] | no_overlap, doors_free |
| r_L1_cocuk_odasi | shrink | office_chair #4 | [2.3, 5.8] | [2.3, 5.8] | doors_free |
| r_L1_cocuk_odasi | slide | office_chair #4 | [2.3, 5.8] | [2.2, 5.8] | doors_free |
| r_L1_cocuk_odasi | snap | desk #3 | [2.5, 6.5] | [2.5, 6.579] | no_overlap, clearance_ok, doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | desk #3 | [2.5, 6.579] | [2.5, 6.579] | no_overlap, clearance_ok, doors_free |
| r_L1_cocuk_odasi | shrink | desk #3 | [2.5, 6.579] | [2.5, 6.629] | no_overlap, clearance_ok, doors_free |
| r_L1_cocuk_odasi | slide | desk #3 | [2.5, 6.629] | [2.5, 6.629] | clearance_ok, doors_free |
| r_L1_cocuk_odasi | relocate | desk #3 | [2.5, 6.629] | [2.5, 4.621] | clearance_ok, doors_free |
| r_L1_cocuk_odasi | snap | wardrobe #2 | [3.5, 6.0] | [3.329, 6.629] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_cocuk_odasi | drop | office_chair #4 | [2.2, 5.8] | [2.2, 5.8] | doors_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.329, 6.629] | [3.329, 6.629] | windows_free |
| r_L1_cocuk_odasi | shrink | wardrobe #2 | [3.329, 6.629] | [3.329, 6.629] | windows_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.329, 6.629] | [3.529, 6.629] | windows_free |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.7, 5.5] | [0.471, 5.5] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 5.5] | [0.471, 5.5] | no_overlap |
| r_L1_cocuk_odasi | shrink | nightstand #1 | [0.471, 5.5] | [0.471, 5.5] | no_overlap |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 5.5] | [0.471, 6.7] | no_overlap |
| r_L1_cocuk_odasi | snap | bed_single #0 | [1.0, 5.5] | [1.0, 5.929] | clearance_ok, wall_contact |
| r_L1_cocuk_odasi | relocate | nightstand #1 | [0.471, 6.7] | [1.871, 6.729] | no_overlap |

Dropped pieces (chosen proposals):

- r_L0_mutfak: stove at [2.75, 6.95]: no repair left (doors_free)
- r_L1_yatak_odasi: office_chair at [8.0, 1.7]: no repair left (doors_free)
- r_L1_yatak_odasi: desk at [8.0, 2.0]: no repair left (doors_free)
- r_L1_yatak_odasi: wardrobe at [6.0, 1.0]: no repair left (doors_free)
- r_L1_cocuk_odasi: office_chair at [2.5, 6.0]: no repair left (doors_free)
