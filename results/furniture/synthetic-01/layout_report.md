# AI layout: synthetic-01

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L0_hol) | hall | 2/1/1 (1.9 s) | 1/1/0 (1.0 s) | 2 | dresser (0.6) | ok |
| Mutfak (r_L0_mutfak) | kitchen | 9/5/4 (7.6 s) | 6/5/1 (5.2 s) | 2 | kitchen_counter (0.6), sink_kitchen (0.6), stove (0.6), fridge (0.9), table_dining (0.6) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/4/2 (5.1 s) | 6/5/1 (4.9 s) | 2 | bed_double (0.6), nightstand (0.9), nightstand (0.6), wardrobe (0.6), desk (0.6) | ok |
| Hol (r_L1_hol) | hall | 2/2/0 (1.9 s) | 2/2/0 (1.8 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/4/2 (5.1 s) | 6/4/2 (5.2 s) | 1 | bed_double (0.6), nightstand (0.6), nightstand (0.6), chair (0.6) | ok |
| Banyo (r_L1_banyo) | bathroom | 4/4/0 (3.7 s) | 3/3/0 (2.8 s) | 1 | shower (0.9), toilet (0.6), washbasin (0.6), bathtub (0.6) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 6/5/1 (5.1 s) | 5/4/1 (4.3 s) | 1 | bed_single (0.6), nightstand (0.6), wardrobe (0.9), chair (0.6), bookshelf (0.6) | ok |

Repair steps of the chosen proposals: 106

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_hol | snap | dresser #0 | [6.95, 6.0] | [6.679, 6.0] | inside_room, doors_free, wall_contact |
| r_L0_hol | slide | dresser #0 | [6.679, 6.0] | [6.679, 6.0] | doors_free |
| r_L0_hol | shrink | dresser #0 | [6.679, 6.0] | [6.704, 6.0] | doors_free |
| r_L0_hol | slide | dresser #0 | [6.704, 6.0] | [6.704, 4.5] | doors_free |
| r_L0_mutfak | snap | chair #5 | [2.75, 5.25] | [2.75, 5.5] | inside_room, no_overlap |
| r_L0_mutfak | slide | chair #5 | [2.75, 5.5] | [2.75, 6.0] | no_overlap |
| r_L0_mutfak | snap | table_dining #4 | [2.75, 5.25] | [2.75, 5.75] | inside_room |
| r_L0_mutfak | shrink | chair #5 | [2.75, 6.0] | [2.75, 6.0] | no_overlap |
| r_L0_mutfak | slide | chair #5 | [2.75, 6.0] | [2.75, 6.4] | no_overlap |
| r_L0_mutfak | slide | table_dining #4 | [2.75, 5.75] | [2.45, 5.75] | doors_free |
| r_L0_mutfak | snap | fridge #3 | [0.25, 6.95] | [0.621, 6.579] | inside_room, wall_contact |
| r_L0_mutfak | snap | stove #2 | [2.75, 6.95] | [2.75, 6.629] | inside_room, no_overlap, wall_contact |
| r_L0_mutfak | drop | chair #5 | [2.75, 6.4] | [2.75, 6.4] | no_overlap |
| r_L0_mutfak | slide | stove #2 | [2.75, 6.629] | [2.75, 6.629] | no_overlap |
| r_L0_mutfak | shrink | stove #2 | [2.75, 6.629] | [2.75, 6.629] | no_overlap |
| r_L0_mutfak | slide | stove #2 | [2.75, 6.629] | [2.75, 6.629] | no_overlap |
| r_L0_mutfak | relocate | stove #2 | [2.75, 6.629] | [1.35, 5.571] | no_overlap |
| r_L0_mutfak | snap | sink_kitchen #1 | [2.75, 6.95] | [2.75, 6.679] | inside_room, no_overlap, wall_contact |
| r_L0_mutfak | slide | sink_kitchen #1 | [2.75, 6.679] | [2.75, 6.679] | no_overlap |
| r_L0_mutfak | shrink | sink_kitchen #1 | [2.75, 6.679] | [2.75, 6.679] | no_overlap |
| r_L0_mutfak | slide | sink_kitchen #1 | [2.75, 6.679] | [2.75, 6.679] | no_overlap |
| r_L0_mutfak | relocate | sink_kitchen #1 | [2.75, 6.679] | [0.75, 5.521] | no_overlap |
| r_L0_mutfak | snap | kitchen_counter #0 | [2.75, 6.95] | [2.75, 6.629] | inside_room, wall_contact |
| r_L0_mutfak | shrink | table_dining #4 | [2.45, 5.75] | [2.45, 5.75] | doors_free |
| r_L0_mutfak | slide | table_dining #4 | [2.45, 5.75] | [2.25, 5.75] | doors_free |
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
| r_L1_hol | snap | chair #1 | [5.95, 3.0] | [5.67, 3.21] | inside_room |
| r_L1_hol | snap | dresser #0 | [4.35, 1.0] | [4.596, 1.0] | inside_room, wall_contact |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.2, 2.5] | [7.2, 2.929] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.2, 2.929] | [7.9, 2.929] | doors_free |
| r_L1_yatak_odasi | anchor_first | bed_double #0 | [7.2, 2.5] | [7.9, 2.929] | - |
| r_L1_yatak_odasi | slide | chair #5 | [8.1, 1.9] | [8.1, 1.9] | no_overlap |
| r_L1_yatak_odasi | shrink | chair #5 | [8.1, 1.9] | [8.1, 1.9] | no_overlap |
| r_L1_yatak_odasi | slide | chair #5 | [8.1, 1.9] | [9.1, 1.9] | no_overlap |
| r_L1_yatak_odasi | snap | desk #4 | [8.0, 2.0] | [8.979, 2.0] | no_overlap, wall_contact |
| r_L1_yatak_odasi | shrink | chair #5 | [9.1, 1.9] | [9.1, 1.9] | no_overlap |
| r_L1_yatak_odasi | slide | chair #5 | [9.1, 1.9] | [9.1, 1.1] | no_overlap |
| r_L1_yatak_odasi | slide | desk #4 | [8.979, 2.0] | [8.979, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | shrink | desk #4 | [8.979, 2.0] | [9.029, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | slide | desk #4 | [9.029, 2.0] | [9.029, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | relocate | desk #4 | [9.029, 2.0] | [8.129, 0.621] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | drop | desk #4 | [8.129, 0.621] | [8.129, 0.621] | doors_free |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 1.5] | [6.371, 1.5] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.5] | [6.371, 1.5] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 1.5] | [6.371, 1.5] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 1.5] | [6.371, 1.5] | clearance_ok, doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 1.5] | [6.371, 1.5] | clearance_ok, doors_free |
| r_L1_yatak_odasi | drop | wardrobe #3 | [6.371, 1.5] | [6.371, 1.5] | clearance_ok, doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [7.8, 2.5] | [7.8, 3.729] | no_overlap, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #2 | [7.8, 3.729] | [6.7, 3.729] | no_overlap |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.6, 2.5] | [6.271, 2.5] | doors_free, wall_contact |
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
| r_L1_cocuk_odasi | snap | bookshelf #5 | [3.5, 5.5] | [4.054, 5.5] | doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | bookshelf #5 | [4.054, 5.5] | [4.054, 5.5] | no_overlap, doors_free |
| r_L1_cocuk_odasi | shrink | bookshelf #5 | [4.054, 5.5] | [4.079, 5.5] | no_overlap, doors_free |
| r_L1_cocuk_odasi | slide | bookshelf #5 | [4.079, 5.5] | [4.079, 5.5] | doors_free |
| r_L1_cocuk_odasi | relocate | bookshelf #5 | [4.079, 5.5] | [3.729, 4.446] | doors_free |
| r_L1_cocuk_odasi | snap | chair #4 | [2.0, 4.0] | [2.085, 4.543] | inside_room, no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [2.085, 4.543] | [2.985, 4.543] | no_overlap |
| r_L1_cocuk_odasi | snap | desk #3 | [2.0, 4.5] | [2.0, 4.621] | inside_room, clearance_ok, wall_contact |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.621] | [2.0, 4.621] | clearance_ok |
| r_L1_cocuk_odasi | shrink | desk #3 | [2.0, 4.621] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | relocate | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | drop | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | snap | wardrobe #2 | [3.0, 6.0] | [3.0, 6.629] | doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.0, 6.629] | [3.0, 6.629] | windows_free |
| r_L1_cocuk_odasi | shrink | wardrobe #2 | [3.0, 6.629] | [3.0, 6.629] | windows_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.0, 6.629] | [3.5, 6.629] | windows_free |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.7, 6.0] | [0.471, 6.0] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 6.0] | [0.471, 6.0] | no_overlap |
| r_L1_cocuk_odasi | shrink | nightstand #1 | [0.471, 6.0] | [0.471, 6.0] | no_overlap |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 6.0] | [0.471, 6.0] | no_overlap |
| r_L1_cocuk_odasi | relocate | nightstand #1 | [0.471, 6.0] | [1.871, 6.729] | no_overlap |
| r_L1_cocuk_odasi | snap | bed_single #0 | [1.0, 6.0] | [1.0, 5.929] | inside_room |

Dropped pieces (chosen proposals):

- r_L0_mutfak: chair at [2.75, 5.25]: no repair left (no_overlap)
- r_L1_ebeveyn_yatak_odasi: chair at [3.1, 1.6]: no repair left (doors_free)
- r_L1_yatak_odasi: desk at [8.0, 2.0]: no repair left (doors_free)
- r_L1_yatak_odasi: wardrobe at [6.0, 1.5]: no repair left (clearance_ok, doors_free)
- r_L1_cocuk_odasi: desk at [2.0, 4.5]: no repair left (clearance_ok)
