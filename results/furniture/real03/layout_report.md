# AI layout: real03

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Rüzgarlık (r_L0_ruzgarlik) | other | 5/2/3 (4.6 s) | 4/2/2 (3.6 s) | 2 | desk (0.6), bookshelf (0.6) | ok |
| Güvenlik Holü (r_L0_guvenlik_holu) | hall | 4/4/0 (3.6 s) | 0/0/0 (0.1 s) | 1 | console_table (0.6), shoe_cabinet (0.6), bench (0.6), bookshelf (0.6) | ok |

Repair steps of the chosen proposals: 24

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_ruzgarlik | snap | chair #3 | [12.65, 3.0] | [12.617, 2.963] | inside_room, no_overlap, doors_free |
| r_L0_ruzgarlik | slide | chair #3 | [12.617, 2.963] | [12.617, 2.963] | no_overlap, doors_free |
| r_L0_ruzgarlik | shrink | chair #3 | [12.617, 2.963] | [12.617, 2.963] | no_overlap, doors_free |
| r_L0_ruzgarlik | slide | chair #3 | [12.617, 2.963] | [12.617, 2.963] | no_overlap, doors_free |
| r_L0_ruzgarlik | shrink | chair #3 | [12.617, 2.963] | [12.617, 2.963] | no_overlap, doors_free |
| r_L0_ruzgarlik | slide | chair #3 | [12.617, 2.963] | [12.617, 2.963] | no_overlap, doors_free |
| r_L0_ruzgarlik | drop | chair #3 | [12.617, 2.963] | [12.617, 2.963] | no_overlap, doors_free |
| r_L0_ruzgarlik | snap | armchair #2 | [12.65, 3.0] | [12.45, 2.777] | inside_room, no_overlap, clearance_ok, doors_free |
| r_L0_ruzgarlik | slide | armchair #2 | [12.45, 2.777] | [12.45, 2.777] | no_overlap, clearance_ok, doors_free |
| r_L0_ruzgarlik | shrink | armchair #2 | [12.45, 2.777] | [12.45, 2.777] | no_overlap, clearance_ok, doors_free |
| r_L0_ruzgarlik | slide | armchair #2 | [12.45, 2.777] | [12.45, 2.777] | no_overlap, clearance_ok, doors_free |
| r_L0_ruzgarlik | drop | armchair #2 | [12.45, 2.777] | [12.45, 2.777] | no_overlap, clearance_ok, doors_free |
| r_L0_ruzgarlik | snap | bookshelf #1 | [12.65, 1.2] | [12.954, 1.2] | doors_free, wall_contact |
| r_L0_ruzgarlik | snap | desk #0 | [12.65, 2.5] | [12.779, 2.5] | doors_free, wall_contact |
| r_L0_ruzgarlik | slide | desk #0 | [12.779, 2.5] | [12.779, 2.5] | doors_free |
| r_L0_ruzgarlik | shrink | desk #0 | [12.779, 2.5] | [12.829, 2.5] | doors_free |
| r_L0_ruzgarlik | slide | desk #0 | [12.829, 2.5] | [12.829, 2.5] | doors_free |
| r_L0_ruzgarlik | relocate | desk #0 | [12.829, 2.5] | [10.271, 1.8] | doors_free |
| r_L0_guvenlik_holu | snap | bookshelf #3 | [5.7, 7.75] | [5.688, 7.846] | inside_room, wall_contact |
| r_L0_guvenlik_holu | slide | bookshelf #3 | [5.688, 7.846] | [5.588, 7.846] | inside_room |
| r_L0_guvenlik_holu | snap | bench #2 | [5.7, 8.3] | [5.579, 8.729] | inside_room, wall_contact |
| r_L0_guvenlik_holu | snap | shoe_cabinet #1 | [3.9, 7.75] | [4.021, 7.831] | inside_room, wall_contact |
| r_L0_guvenlik_holu | snap | console_table #0 | [3.9, 8.3] | [3.796, 8.3] | inside_room, wall_contact |
| r_L0_guvenlik_holu | slide | shoe_cabinet #1 | [4.021, 7.831] | [4.421, 7.831] | no_overlap |

Dropped pieces (chosen proposals):

- r_L0_ruzgarlik: chair at [12.65, 3.0]: no repair left (no_overlap, doors_free)
- r_L0_ruzgarlik: armchair at [12.65, 3.0]: no repair left (no_overlap, clearance_ok, doors_free)
