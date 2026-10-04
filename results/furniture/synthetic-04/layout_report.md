# AI layout: synthetic-04

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L3_hol) | hall | 2/1/1 (1.9 s) | 1/1/0 (1.0 s) | 2 | dresser (0.6) | ok |
| Çocuk Odası (r_L3_cocuk_odasi) | bedroom | 5/4/1 (4.4 s) | 6/4/2 (5.3 s) | 1 | bed_single (0.9), nightstand (0.6), wardrobe (0.9), chair (0.6) | ok |

Repair steps of the chosen proposals: 23

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L3_hol | snap | dresser #0 | [3.7, 7.6] | [4.071, 7.504] | inside_room, doors_free, wall_contact |
| r_L3_hol | slide | dresser #0 | [4.071, 7.504] | [4.071, 7.504] | doors_free |
| r_L3_hol | relocate | dresser #0 | [4.071, 7.504] | [3.796, 6.304] | doors_free |
| r_L3_cocuk_odasi | slide | chair #4 | [10.5, 5.0] | [11.5, 5.0] | no_overlap |
| r_L3_cocuk_odasi | snap | desk #3 | [10.5, 5.5] | [10.5, 5.021] | no_overlap, clearance_ok, doors_free, wall_contact |
| r_L3_cocuk_odasi | slide | desk #3 | [10.5, 5.021] | [10.5, 5.021] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | shrink | desk #3 | [10.5, 5.021] | [10.5, 4.971] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | slide | desk #3 | [10.5, 4.971] | [10.6, 4.971] | no_overlap, clearance_ok, doors_free |
| r_L3_cocuk_odasi | relocate | desk #3 | [10.6, 4.971] | [11.379, 5.971] | doors_free |
| r_L3_cocuk_odasi | drop | desk #3 | [11.379, 5.971] | [11.379, 5.971] | doors_free |
| r_L3_cocuk_odasi | snap | wardrobe #2 | [8.05, 6.5] | [8.371, 6.5] | inside_room, no_overlap, clearance_ok, doors_free, wall_contact |
| r_L3_cocuk_odasi | slide | wardrobe #2 | [8.371, 6.5] | [8.371, 6.5] | clearance_ok, doors_free |
| r_L3_cocuk_odasi | shrink | wardrobe #2 | [8.371, 6.5] | [8.371, 6.5] | clearance_ok, doors_free |
| r_L3_cocuk_odasi | slide | wardrobe #2 | [8.371, 6.5] | [8.371, 6.5] | clearance_ok, doors_free |
| r_L3_cocuk_odasi | relocate | wardrobe #2 | [8.371, 6.5] | [10.671, 4.971] | clearance_ok, doors_free |
| r_L3_cocuk_odasi | snap | nightstand #1 | [9.375, 5.7] | [9.375, 4.871] | no_overlap, wall_contact |
| r_L3_cocuk_odasi | snap | bed_single #0 | [9.375, 6.2] | [9.375, 6.729] | clearance_ok, doors_free, wall_contact |
| r_L3_cocuk_odasi | slide | bed_single #0 | [9.375, 6.729] | [9.375, 6.729] | doors_free |
| r_L3_cocuk_odasi | shrink | bed_single #0 | [9.375, 6.729] | [9.375, 6.729] | doors_free |
| r_L3_cocuk_odasi | slide | bed_single #0 | [9.375, 6.729] | [9.375, 6.729] | doors_free |
| r_L3_cocuk_odasi | shrink | bed_single #0 | [9.375, 6.729] | [9.375, 6.779] | doors_free |
| r_L3_cocuk_odasi | slide | bed_single #0 | [9.375, 6.779] | [9.375, 6.779] | doors_free |
| r_L3_cocuk_odasi | relocate | bed_single #0 | [9.375, 6.779] | [9.071, 6.779] | doors_free |

Dropped pieces (chosen proposals):

- r_L3_cocuk_odasi: desk at [10.5, 5.5]: no repair left (doors_free)
