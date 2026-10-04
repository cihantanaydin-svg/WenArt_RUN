# AI layout: synthetic-06

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Lobby (r_L0_lobby) | hall | 2/1/1 (1.9 s) | 2/1/1 (1.8 s) | 1 | chair (0.6) | ok |
| Bed Room (r_L0_bed_room) | bedroom | 6/3/3 (5.2 s) | 6/3/3 (5.0 s) | 1 | bed_double (0.6), nightstand (0.6), nightstand (0.6) | ok |

Repair steps of the chosen proposals: 28

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_lobby | slide | chair #1 | [4.12, 5.2] | [4.82, 5.2] | doors_free |
| r_L0_lobby | snap | dresser #0 | [2.51, 5.2] | [2.76, 5.042] | inside_room, doors_free, wall_contact |
| r_L0_lobby | slide | dresser #0 | [2.76, 5.042] | [2.76, 5.042] | doors_free |
| r_L0_lobby | relocate | dresser #0 | [2.76, 5.042] | [2.76, 5.042] | doors_free |
| r_L0_lobby | drop | dresser #0 | [2.76, 5.042] | [2.76, 5.042] | doors_free |
| r_L0_bed_room | snap | chair #5 | [2.9, 4.8] | [2.404, 6.002] | inside_room, no_overlap |
| r_L0_bed_room | slide | chair #5 | [2.404, 6.002] | [3.004, 6.802] | no_overlap, doors_free |
| r_L0_bed_room | shrink | chair #5 | [3.004, 6.802] | [3.004, 6.802] | doors_free |
| r_L0_bed_room | slide | chair #5 | [3.004, 6.802] | [3.004, 6.902] | doors_free |
| r_L0_bed_room | shrink | chair #5 | [3.004, 6.902] | [3.004, 6.902] | doors_free |
| r_L0_bed_room | slide | chair #5 | [3.004, 6.902] | [2.904, 6.902] | doors_free |
| r_L0_bed_room | drop | chair #5 | [2.904, 6.902] | [2.904, 6.902] | doors_free |
| r_L0_bed_room | snap | desk #4 | [2.8, 5.0] | [2.708, 6.088] | inside_room, clearance_ok, wall_contact |
| r_L0_bed_room | slide | desk #4 | [2.708, 6.088] | [2.708, 6.088] | no_overlap, clearance_ok, doors_free |
| r_L0_bed_room | shrink | desk #4 | [2.708, 6.088] | [2.708, 6.038] | no_overlap, clearance_ok, doors_free |
| r_L0_bed_room | slide | desk #4 | [2.708, 6.038] | [2.708, 6.038] | no_overlap, clearance_ok, doors_free |
| r_L0_bed_room | relocate | desk #4 | [2.708, 6.038] | [2.708, 6.038] | no_overlap, clearance_ok, doors_free |
| r_L0_bed_room | drop | desk #4 | [2.708, 6.038] | [2.708, 6.038] | no_overlap, clearance_ok, doors_free |
| r_L0_bed_room | snap | wardrobe #3 | [0.5, 6.0] | [0.551, 6.639] | inside_room, no_overlap, clearance_ok, wall_contact |
| r_L0_bed_room | slide | wardrobe #3 | [0.551, 6.639] | [0.551, 6.639] | clearance_ok, doors_free, windows_free |
| r_L0_bed_room | shrink | wardrobe #3 | [0.551, 6.639] | [0.551, 6.639] | clearance_ok, doors_free, windows_free |
| r_L0_bed_room | slide | wardrobe #3 | [0.551, 6.639] | [0.551, 6.639] | clearance_ok, doors_free, windows_free |
| r_L0_bed_room | relocate | wardrobe #3 | [0.551, 6.639] | [0.551, 6.639] | clearance_ok, doors_free, windows_free |
| r_L0_bed_room | drop | wardrobe #3 | [0.551, 6.639] | [0.551, 6.639] | clearance_ok, doors_free, windows_free |
| r_L0_bed_room | snap | nightstand #2 | [2.3, 6.8] | [3.208, 6.8] | no_overlap, doors_free, wall_contact |
| r_L0_bed_room | slide | nightstand #2 | [3.208, 6.8] | [3.208, 6.9] | doors_free |
| r_L0_bed_room | snap | nightstand #1 | [1.3, 6.8] | [0.451, 6.8] | no_overlap, wall_contact |
| r_L0_bed_room | snap | bed_double #0 | [1.8, 7.0] | [1.8, 8.047] | clearance_ok, doors_free, wall_contact |

Dropped pieces (chosen proposals):

- r_L0_lobby: dresser at [2.51, 5.2]: no repair left (doors_free)
- r_L0_bed_room: chair at [2.9, 4.8]: no repair left (doors_free)
- r_L0_bed_room: desk at [2.8, 5.0]: no repair left (no_overlap, clearance_ok, doors_free)
- r_L0_bed_room: wardrobe at [0.5, 6.0]: no repair left (clearance_ok, doors_free, windows_free)
