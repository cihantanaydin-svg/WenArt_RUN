# AI layout: synthetic-01

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L0_hol) | hall | 2/1/1 (4.5 s) | 1/1/0 (1.4 s) | 2 | dresser (0.6) | ok |
| Mutfak (r_L0_mutfak) | kitchen | 7/4/3 (8.0 s) | 6/5/1 (7.1 s) | 2 | kitchen_counter (0.6), sink_kitchen (0.6), stove (0.9), fridge (0.9), table_dining (0.6) | ok |
| Ebeveyn Yatak Odası (r_L1_ebeveyn_yatak_odasi) | bedroom | 6/4/2 (6.9 s) | 6/6/0 (6.9 s) | 2 | bed_double (0.6), nightstand (0.6), nightstand (0.6), wardrobe (0.6), desk (0.9), chair (0.9) | ok |
| Hol (r_L1_hol) | hall | 2/2/0 (2.5 s) | 2/2/0 (2.5 s) | 1 | dresser (0.9), chair (0.6) | ok |
| Yatak Odası (r_L1_yatak_odasi) | bedroom | 6/4/2 (6.9 s) | 6/3/3 (7.0 s) | 1 | bed_double (0.9), nightstand (0.9), nightstand (0.9), chair (0.6) | ok |
| Banyo (r_L1_banyo) | bathroom | 3/3/0 (3.9 s) | 3/3/0 (3.7 s) | 1 | shower (0.6), toilet (0.6), washbasin (0.6) | ok |
| Çocuk Odası (r_L1_cocuk_odasi) | bedroom | 6/5/1 (6.9 s) | 5/4/1 (5.8 s) | 1 | bed_single (0.9), nightstand (0.9), wardrobe (0.9), chair (0.9), bookshelf (0.6) | ok |

Repair steps of the chosen proposals: 84

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_hol | snap | dresser #0 | [6.95, 6.5] | [6.679, 6.329] | inside_room, doors_free, wall_contact |
| r_L0_hol | slide | dresser #0 | [6.679, 6.329] | [6.679, 6.329] | doors_free |
| r_L0_hol | shrink | dresser #0 | [6.679, 6.329] | [6.704, 6.329] | doors_free |
| r_L0_hol | slide | dresser #0 | [6.704, 6.329] | [6.704, 4.429] | doors_free |
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
| r_L0_mutfak | relocate | sink_kitchen #1 | [2.75, 6.679] | [0.75, 5.521] | no_overlap |
| r_L0_mutfak | snap | kitchen_counter #0 | [2.75, 6.95] | [2.75, 6.629] | inside_room, wall_contact |
| r_L0_mutfak | shrink | table_dining #4 | [2.45, 5.75] | [2.45, 5.75] | doors_free |
| r_L0_mutfak | slide | table_dining #4 | [2.45, 5.75] | [2.25, 5.75] | doors_free |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [2.6, 0.6] | [3.1, 1.1] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | desk #4 | [2.5, 0.5] | [2.5, 0.621] | inside_room, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | shrink | chair #5 | [3.1, 1.1] | [3.1, 1.1] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | chair #5 | [3.1, 1.1] | [3.5, 1.0] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [2.5, 0.621] | [2.5, 0.621] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | shrink | desk #4 | [2.5, 0.621] | [2.5, 0.571] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | snap | wardrobe #3 | [3.0, 3.5] | [3.0, 3.829] | inside_room, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #2 | [1.4, 2.0] | [0.471, 2.0] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #2 | [0.471, 2.0] | [0.471, 3.3] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | nightstand #1 | [0.6, 2.0] | [0.471, 2.0] | no_overlap, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | nightstand #1 | [0.471, 2.0] | [0.471, 3.8] | no_overlap |
| r_L1_ebeveyn_yatak_odasi | snap | bed_double #0 | [1.0, 2.0] | [1.271, 2.0] | inside_room, clearance_ok, wall_contact |
| r_L1_ebeveyn_yatak_odasi | slide | desk #4 | [2.5, 0.571] | [2.5, 0.571] | clearance_ok |
| r_L1_ebeveyn_yatak_odasi | relocate | desk #4 | [2.5, 0.571] | [1.5, 3.829] | clearance_ok |
| r_L1_hol | slide | chair #1 | [5.15, 3.0] | [4.75, 3.0] | doors_free |
| r_L1_hol | snap | dresser #0 | [4.35, 1.0] | [4.596, 1.0] | inside_room, wall_contact |
| r_L1_yatak_odasi | snap | bed_double #0 | [7.2, 2.0] | [7.2, 2.929] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | bed_double #0 | [7.2, 2.929] | [7.9, 2.929] | doors_free |
| r_L1_yatak_odasi | anchor_first | bed_double #0 | [7.2, 2.0] | [7.9, 2.929] | - |
| r_L1_yatak_odasi | slide | chair #5 | [9.0, 1.8] | [9.0, 0.8] | no_overlap |
| r_L1_yatak_odasi | snap | desk #4 | [9.0, 2.0] | [8.979, 2.0] | inside_room, no_overlap, clearance_ok, wall_contact |
| r_L1_yatak_odasi | slide | desk #4 | [8.979, 2.0] | [8.979, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | shrink | desk #4 | [8.979, 2.0] | [9.029, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | slide | desk #4 | [9.029, 2.0] | [9.029, 2.0] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | relocate | desk #4 | [9.029, 2.0] | [8.029, 0.621] | no_overlap, clearance_ok |
| r_L1_yatak_odasi | snap | wardrobe #3 | [6.0, 3.0] | [6.371, 3.0] | inside_room, clearance_ok, doors_free, wall_contact |
| r_L1_yatak_odasi | drop | desk #4 | [8.029, 0.621] | [8.029, 0.621] | doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 3.0] | [6.371, 3.0] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | shrink | wardrobe #3 | [6.371, 3.0] | [6.371, 3.0] | no_overlap, clearance_ok, doors_free |
| r_L1_yatak_odasi | slide | wardrobe #3 | [6.371, 3.0] | [6.371, 3.0] | clearance_ok, doors_free |
| r_L1_yatak_odasi | relocate | wardrobe #3 | [6.371, 3.0] | [6.371, 3.0] | clearance_ok, doors_free |
| r_L1_yatak_odasi | drop | wardrobe #3 | [6.371, 3.0] | [6.371, 3.0] | clearance_ok, doors_free |
| r_L1_yatak_odasi | snap | nightstand #2 | [7.7, 2.0] | [9.129, 2.0] | no_overlap, wall_contact |
| r_L1_yatak_odasi | snap | nightstand #1 | [6.7, 2.0] | [6.271, 2.0] | doors_free, wall_contact |
| r_L1_yatak_odasi | slide | nightstand #1 | [6.271, 2.0] | [6.271, 3.2] | doors_free |
| r_L1_banyo | snap | shower #0 | [7.15, 5.5] | [7.15, 4.521] | doors_free, wall_contact |
| r_L1_banyo | snap | washbasin #2 | [6.05, 4.2] | [6.296, 4.371] | inside_room, wall_contact |
| r_L1_banyo | snap | toilet #1 | [6.05, 6.2] | [6.421, 6.2] | inside_room, doors_free, wall_contact |
| r_L1_banyo | slide | toilet #1 | [6.421, 6.2] | [6.421, 6.5] | doors_free |
| r_L1_cocuk_odasi | snap | bookshelf #5 | [1.0, 3.5] | [1.0, 4.446] | inside_room, wall_contact |
| r_L1_cocuk_odasi | slide | bookshelf #5 | [1.0, 4.446] | [3.2, 4.446] | no_overlap |
| r_L1_cocuk_odasi | snap | chair #4 | [2.0, 4.2] | [2.053, 4.495] | inside_room, no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [2.053, 4.495] | [1.853, 5.095] | no_overlap |
| r_L1_cocuk_odasi | snap | desk #3 | [2.0, 4.5] | [2.0, 4.621] | inside_room, clearance_ok, wall_contact |
| r_L1_cocuk_odasi | shrink | chair #4 | [1.853, 5.095] | [1.853, 5.095] | no_overlap |
| r_L1_cocuk_odasi | slide | chair #4 | [1.853, 5.095] | [1.853, 5.795] | no_overlap |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.621] | [2.0, 4.621] | clearance_ok |
| r_L1_cocuk_odasi | shrink | desk #3 | [2.0, 4.621] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | slide | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | relocate | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | drop | desk #3 | [2.0, 4.571] | [2.0, 4.571] | clearance_ok |
| r_L1_cocuk_odasi | snap | wardrobe #2 | [3.0, 6.0] | [3.0, 6.629] | doors_free, wall_contact |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.0, 6.629] | [3.0, 6.629] | windows_free |
| r_L1_cocuk_odasi | shrink | wardrobe #2 | [3.0, 6.629] | [3.0, 6.629] | windows_free |
| r_L1_cocuk_odasi | slide | wardrobe #2 | [3.0, 6.629] | [3.5, 6.629] | windows_free |
| r_L1_cocuk_odasi | snap | nightstand #1 | [0.8, 5.8] | [0.471, 5.8] | no_overlap, wall_contact |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 5.8] | [0.471, 5.8] | no_overlap |
| r_L1_cocuk_odasi | shrink | nightstand #1 | [0.471, 5.8] | [0.471, 5.8] | no_overlap |
| r_L1_cocuk_odasi | slide | nightstand #1 | [0.471, 5.8] | [0.471, 5.8] | no_overlap |
| r_L1_cocuk_odasi | relocate | nightstand #1 | [0.471, 5.8] | [1.871, 6.729] | no_overlap |
| r_L1_cocuk_odasi | snap | bed_single #0 | [1.0, 6.0] | [1.0, 5.929] | inside_room |

Dropped pieces (chosen proposals):

- r_L0_mutfak: chair at [2.75, 5.25]: no repair left (no_overlap)
- r_L1_yatak_odasi: desk at [9.0, 2.0]: no repair left (doors_free)
- r_L1_yatak_odasi: wardrobe at [6.0, 3.0]: no repair left (clearance_ok, doors_free)
- r_L1_cocuk_odasi: desk at [2.0, 4.5]: no repair left (clearance_ok)
