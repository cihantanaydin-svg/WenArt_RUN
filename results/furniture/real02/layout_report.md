# AI layout: real02

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Oda (r_L-1b_oda) | other | 5/5/0 (4.8 s) | 4/4/0 (3.2 s) | 1 | desk (0.9), bookshelf (0.6), armchair (0.6), chair (0.6), table_dining (0.6) | ok |
| Oda (r_L-1b_oda_2) | other | - | - | - | desk (0.9), bookshelf (0.6), armchair (0.6), chair (0.6), table_dining (0.6) | copied from r_L-1b_oda (twin) |
| Koridor (r_L0_koridor) | hall | 4/2/2 (3.4 s) | 2/2/0 (1.8 s) | 2 | console_table (0.6), shoe_cabinet (0.6) | ok |
| Koridor (r_L0_koridor_2) | hall | - | - | - | console_table (0.6), shoe_cabinet (0.6) | copied from r_L0_koridor (twin) |

Repair steps of the chosen proposals: 11

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L-1b_oda | slide | table_dining #4 | [1.5, 8.0] | [1.4, 8.0] | no_overlap |
| r_L-1b_oda | slide | chair #3 | [2.5, 8.5] | [2.7, 9.3] | no_overlap, doors_free |
| r_L-1b_oda | snap | bookshelf #1 | [0.5, 6.0] | [0.722, 7.639] | inside_room, wall_contact |
| r_L-1b_oda | shrink | table_dining #4 | [1.4, 8.0] | [1.4, 8.0] | no_overlap |
| r_L-1b_oda | slide | table_dining #4 | [1.4, 8.0] | [0.9, 8.3] | no_overlap |
| r_L-1b_oda | snap | desk #0 | [1.0, 11.0] | [1.0, 11.43] | wall_contact |
| r_L0_koridor | snap | shoe_cabinet #1 | [3.32, 7.69] | [3.499, 7.69] | inside_room, doors_free, wall_contact |
| r_L0_koridor | slide | shoe_cabinet #1 | [3.499, 7.69] | [3.499, 8.49] | doors_free |
| r_L0_koridor | snap | console_table #0 | [3.32, 6.51] | [3.489, 6.51] | inside_room, doors_free, wall_contact |
| r_L0_koridor | slide | console_table #0 | [3.489, 6.51] | [3.489, 6.51] | doors_free |
| r_L0_koridor | relocate | console_table #0 | [3.489, 6.51] | [4.447, 6.51] | doors_free |
