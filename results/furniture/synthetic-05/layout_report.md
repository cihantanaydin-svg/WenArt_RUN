# AI layout: synthetic-05

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Hol (r_L0_hol) | hall | 2/0/2 (1.9 s) | 1/0/1 (1.0 s) | - | - | room stays empty: model answered nothing usable (pass 1: no usable piece; pass 2: no usable piece) |
| Çalışma Odası (r_L0_calisma_odasi) | other | 3/3/0 (2.8 s) | 3/3/0 (2.7 s) | 1 | desk (0.9), bookshelf (0.9), chair (0.9) | ok |
| Antre (r_L0_antre) | hall | 2/1/1 (1.8 s) | 2/1/1 (1.8 s) | 1 | dresser (0.9) | ok |

Repair steps of the chosen proposals: 12

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_calisma_odasi | slide | chair #2 | [11.0, 6.5] | [11.0, 6.0] | no_overlap |
| r_L0_calisma_odasi | snap | bookshelf #1 | [10.5, 5.5] | [10.446, 5.5] | doors_free, wall_contact |
| r_L0_calisma_odasi | slide | bookshelf #1 | [10.446, 5.5] | [10.446, 5.5] | doors_free |
| r_L0_calisma_odasi | shrink | bookshelf #1 | [10.446, 5.5] | [10.421, 5.5] | doors_free |
| r_L0_calisma_odasi | slide | bookshelf #1 | [10.421, 5.5] | [10.421, 5.5] | doors_free |
| r_L0_calisma_odasi | relocate | bookshelf #1 | [10.421, 5.5] | [11.721, 4.346] | doors_free |
| r_L0_calisma_odasi | snap | desk #0 | [11.0, 7.0] | [10.621, 7.0] | clearance_ok, wall_contact |
| r_L0_antre | slide | chair #1 | [4.3, 7.1] | [3.9, 6.6] | doors_free |
| r_L0_antre | snap | dresser #0 | [3.55, 7.1] | [3.796, 7.1] | inside_room, wall_contact |
| r_L0_antre | shrink | chair #1 | [3.9, 6.6] | [3.9, 6.6] | no_overlap |
| r_L0_antre | slide | chair #1 | [3.9, 6.6] | [3.9, 6.6] | no_overlap |
| r_L0_antre | drop | chair #1 | [3.9, 6.6] | [3.9, 6.6] | no_overlap |

Dropped pieces (chosen proposals):

- r_L0_antre: chair at [4.3, 7.1]: no repair left (no_overlap)
