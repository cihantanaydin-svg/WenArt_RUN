# AI layout: synthetic-04

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L3_hol) | hall | 2/1/1 (3.0 s) | 1/1/0 (1.1 s) | 2 | dresser (0.6) | ok |
| Çocuk Odası (r_L3_cocuk_odasi) | bedroom | 6/4/2 (5.5 s) | 6/5/1 (5.7 s) | 2 | bed_single (0.9), nightstand (0.6), nightstand (0.6), desk (0.9), chair (0.6) | ok |

Repair steps of the chosen proposals: 22

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L3_hol | snap | dresser #0 | [3.6, 7.6] | [4.071, 7.504] | inside_room, doors_free, wall_contact |
| r_L3_hol | slide | dresser #0 | [4.071, 7.504] | [4.071, 7.504] | doors_free |
| r_L3_hol | relocate | dresser #0 | [4.071, 7.504] | [3.796, 6.304] | doors_free |
| r_L3_cocuk_odasi | slide | chair #5 | [10.6, 6.3] | [10.6, 7.1] | no_overlap, doors_free |
| r_L3_cocuk_odasi | snap | desk #4 | [10.5, 6.5] | [10.5, 7.379] | no_overlap, clearance_ok, doors_free, wall_contact |
| r_L3_cocuk_odasi | shrink | chair #5 | [10.6, 7.1] | [10.6, 7.1] | no_overlap |
| r_L3_cocuk_odasi | slide | chair #5 | [10.6, 7.1] | [11.4, 7.1] | no_overlap |
| r_L3_cocuk_odasi | slide | desk #4 | [10.5, 7.379] | [10.5, 7.379] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | shrink | desk #4 | [10.5, 7.379] | [10.5, 7.429] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | slide | desk #4 | [10.5, 7.429] | [10.6, 7.429] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | relocate | desk #4 | [10.6, 7.429] | [11.379, 6.129] | doors_free |
| r_L3_cocuk_odasi | snap | wardrobe #3 | [8.05, 7.0] | [8.371, 6.829] | inside_room, clearance_ok, wall_contact |
| r_L3_cocuk_odasi | slide | wardrobe #3 | [8.371, 6.829] | [8.371, 6.829] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | shrink | wardrobe #3 | [8.371, 6.829] | [8.371, 6.829] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | slide | wardrobe #3 | [8.371, 6.829] | [8.371, 6.829] | no_overlap, clearance_ok |
| r_L3_cocuk_odasi | relocate | wardrobe #3 | [8.371, 6.829] | [8.371, 6.829] | no_overlap, clearance_ok |
| r_L3_cocuk_odasi | drop | wardrobe #3 | [8.371, 6.829] | [8.371, 6.829] | no_overlap, clearance_ok |
| r_L3_cocuk_odasi | snap | nightstand #2 | [9.8, 6.2] | [9.8, 7.529] | no_overlap, wall_contact |
| r_L3_cocuk_odasi | snap | nightstand #1 | [8.9, 6.2] | [8.271, 6.2] | no_overlap, wall_contact |
| r_L3_cocuk_odasi | slide | nightstand #1 | [8.271, 6.2] | [8.271, 6.3] | doors_free |
| r_L3_cocuk_odasi | snap | bed_single #0 | [9.35, 6.2] | [9.35, 6.729] | clearance_ok, doors_free, wall_contact |
| r_L3_cocuk_odasi | slide | nightstand #2 | [9.8, 7.529] | [10.2, 7.529] | no_overlap |

Dropped pieces (chosen proposals):

- r_L3_cocuk_odasi: wardrobe at [8.05, 7.0]: no repair left (no_overlap, clearance_ok)
