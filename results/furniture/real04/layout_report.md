# AI layout: real04

Rooms without documented furniture, furnished in functional groups (docs/milestone12.md §4.3-§4.5): the room's program, the group solver's top candidates (every one checked: inside the room, no overlap, doors, windows, walkways, use zones, group checks G1-G14), the vision model's choice (else the solver's best). Every added piece is `added_by_ai`, `method: rule`, with its group.

| Room | Type | Groups (options) | Candidates (score, hard) | Chosen | By | Added | Solve s | Result |
|---|---|---|---|---|---|---|---|---|
| Oda (r_L-1b_oda) | bedroom | sleeping_double (bed_nightstands), storage (wardrobe) | #1 30.8 0, #2 30.7 0, #3 29.3 0 | 1 | vlm | bed_double, nightstand, nightstand, wardrobe | 1.15 | ok |
| Oda (r_L-1b_oda_2) | bedroom | - | - | - | - | bed_double, nightstand, nightstand, wardrobe | 0.00 | copied from r_L-1b_oda (twin) |
| Koridor (r_L0_koridor) | hall | entrance (shoe_cabinet/console) | #1 8.2 0, #2 8.1 0, #3 7.9 0 | 1 | vlm | shoe_cabinet | 0.21 | ok |
| Koridor (r_L0_koridor_2) | hall | - | - | - | - | shoe_cabinet | 0.00 | copied from r_L0_koridor (twin) |
| Teras (r_L1_teras_2) | balcony | balcony (table_2_chairs) | #1 6.3 0, #2 6.3 0, #3 6.1 0 | 2 | vlm | table_dining, chair, chair | 0.15 | ok |

Choices of the vision model:

- r_L-1b_oda: candidate 1: Bed is positioned with free sides and headboard against the wall, both nightstands are present for symmetry, and the wardrobe placement leaves a clear, balanced circulation path from the door.
- r_L0_koridor: candidate 1: The shoe cabinet is placed lower on the left wall, keeping the entrance area near the top door clear and balanced, which supports better circulation and a more open feel in the narrow corridor.
- r_L1_teras_2: candidate 2: Better balance score than candidate 1 while keeping strong daylight, and the dining set is positioned to use the window light effectively.
