# AI layout: synthetic-07

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Oyun Odası (r_L1_oyun_odasi) | other | 4/4/0 (4.1 s) | 4/4/0 (3.4 s) | 1 | desk (0.9), bookshelf (0.9), armchair (0.6), chair (0.6) | ok |

Repair steps of the chosen proposals: 2

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L1_oyun_odasi | snap | bookshelf #1 | [0.5, 6.5] | [0.446, 6.5] | inside_room, no_overlap, wall_contact |
| r_L1_oyun_odasi | snap | desk #0 | [1.5, 6.5] | [1.5, 7.379] | wall_contact |
