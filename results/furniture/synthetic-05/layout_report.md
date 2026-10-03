# AI layout: synthetic-05

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L0_hol) | hall | 2/0/2 (2.0 s) | 0/0/0 (0.2 s) | - | - | room stays empty: model answered nothing usable (pass 1: no usable piece; pass 2: no usable piece) |
| Çalışma Odası (r_L0_calisma_odasi) | other | 4/4/0 (3.7 s) | 4/4/0 (3.6 s) | 1 | desk (0.6), chair (0.6), bookshelf (0.6), armchair (0.6) | ok |
| Antre (r_L0_antre) | hall | 2/1/1 (1.9 s) | 1/1/0 (1.1 s) | 2 | dresser (0.6) | ok |

Repair steps of the chosen proposals: 11

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_calisma_odasi | slide | armchair #3 | [12.0, 6.5] | [11.9, 6.5] | doors_free |
| r_L0_calisma_odasi | snap | bookshelf #2 | [10.0, 8.0] | [10.446, 8.0] | inside_room, wall_contact |
| r_L0_calisma_odasi | slide | chair #1 | [11.0, 6.7] | [11.0, 6.0] | no_overlap |
| r_L0_calisma_odasi | snap | desk #0 | [11.0, 7.0] | [10.621, 7.0] | clearance_ok, wall_contact |
| r_L0_calisma_odasi | slide | bookshelf #2 | [10.446, 8.0] | [10.446, 8.2] | no_overlap |
| r_L0_calisma_odasi | slide | desk #0 | [10.621, 7.0] | [10.621, 7.0] | clearance_ok |
| r_L0_calisma_odasi | shrink | desk #0 | [10.621, 7.0] | [10.571, 7.0] | clearance_ok |
| r_L0_calisma_odasi | slide | desk #0 | [10.571, 7.0] | [10.571, 7.0] | clearance_ok |
| r_L0_calisma_odasi | relocate | desk #0 | [10.571, 7.0] | [11.371, 8.379] | clearance_ok |
| r_L0_antre | snap | dresser #0 | [3.55, 8.2] | [3.796, 8.2] | inside_room, doors_free, wall_contact |
| r_L0_antre | slide | dresser #0 | [3.796, 8.2] | [3.796, 7.3] | doors_free |
