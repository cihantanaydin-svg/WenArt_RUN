# AI layout: real01

Rooms without documented furniture. Every added piece is `added_by_ai`, `verified` by the placer checks (inside room, no overlap, clearance, doors free, windows free, wall contact), confidence 0.9 when both passes proposed it (same type, centre within 0.5 m), else 0.6.

| Room | Type | Pass 1 (proposed/placed/dropped, s) | Pass 2 | Chosen | Added | Result |
|---|---|---|---|---|---|---|
| Pooja (r_L0_pooja) | prayer | - | - | - | - | room stays empty: prayer room: never furnished by AI (docs/milestone7.md §0) |
| Bath+ Toilet (r_L0_bath_toilet) | bathroom | 3/2/1 (3.3 s) | 3/2/1 (2.5 s) | 1 | toilet (0.6), washbasin (0.6) | ok |

Repair steps of the chosen proposals: 9

| Room | Step | Piece | Before | After | Failed checks |
|---|---|---|---|---|---|
| r_L0_bath_toilet | snap | shower #0 | [4.0, 1.5] | [4.485, 1.5] | doors_free, wall_contact |
| r_L0_bath_toilet | slide | shower #0 | [4.485, 1.5] | [4.485, 1.1] | doors_free |
| r_L0_bath_toilet | snap | washbasin #2 | [3.0, 0.5] | [3.676, 0.551] | inside_room, no_overlap, wall_contact |
| r_L0_bath_toilet | snap | toilet #1 | [3.0, 1.0] | [3.801, 1.0] | inside_room, wall_contact |
| r_L0_bath_toilet | shrink | shower #0 | [4.485, 1.1] | [4.535, 1.1] | no_overlap |
| r_L0_bath_toilet | slide | shower #0 | [4.535, 1.1] | [4.535, 1.1] | no_overlap |
| r_L0_bath_toilet | relocate | shower #0 | [4.535, 1.1] | [4.535, 1.1] | no_overlap |
| r_L0_bath_toilet | drop | shower #0 | [4.535, 1.1] | [4.535, 1.1] | no_overlap |
| r_L0_bath_toilet | slide | washbasin #2 | [3.676, 0.551] | [3.676, 1.551] | no_overlap |

Dropped pieces (chosen proposals):

- r_L0_bath_toilet: shower at [4.0, 1.5]: no repair left (no_overlap)
