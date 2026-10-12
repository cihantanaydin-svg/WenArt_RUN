# AI completion of furnished rooms: real04

Mode `furnished_rooms: complete`, keep size false, twin rooms `one` (assumed: furnished_rooms, furnished_rooms_keep, furnished_rooms_keep_size, render.twin_rooms). Drawn pieces stay as drawn; the group solver adds only what the room's groups miss (the partners of a drawn anchor, the missing members of a drawn set, the groups the room type misses whole); the vision model picks one of its top candidates (else the solver's best). Wall cabinets follow the rule of docs/milestone10.md §4.4.

| Room | Type | State | Drawn groups | Candidates (score, hard) | Chosen | By | Added | Solve s | Note |
|---|---|---|---|---|---|---|---|---|---|
| Salon (r_L-1_salon) | living | completed | - | #1 8.4 0, #2 3.0 0 | 1 | default | bookshelf | 0.22 | - |
| Salon (r_L-1_salon_2) | living | mirrored | - | - | - | - | bookshelf | 0.00 | decisions of r_L-1_salon (twin), not asked again |
| Mutfak (r_L-1_mutfak) | kitchen | completed | kitchen_run | #1 2.8 0, #2 8.8 2, #3 8.8 2 | - | - | wall_cabinet, wall_cabinet, wall_cabinet | 0.14 | nothing fits: kitchen_run: no place passes the checks; dining: no place passes the checks |
| Mutfak (r_L-1_mutfak_2) | kitchen | mirrored | - | - | - | - | wall_cabinet, wall_cabinet, wall_cabinet | 0.00 | decisions of r_L-1_mutfak (twin), not asked again |
| Koridor (r_L-1_koridor) | hall | mirrored | - | - | - | - | shoe_cabinet | 0.00 | decisions of r_L-1_koridor_2 (twin), not asked again |
| Koridor (r_L-1_koridor_2) | hall | completed | - | #1 8.0 0, #2 8.0 0, #3 8.0 0 | 1 | vlm | shoe_cabinet | 0.19 | - |
| Banyo (r_L-1_banyo) | bathroom | completed | bathroom_set | - | - | - | - | 0.00 | nothing missing: the drawn groups are complete |
| Banyo (r_L-1_banyo_2) | bathroom | mirrored | - | - | - | - | - | 0.00 | decisions of r_L-1_banyo (twin), not asked again |
| Salon (r_L-1b_salon) | living | completed | kitchen_run, dining, island, island | #1 2.8 0 | - | - | wall_cabinet, wall_cabinet, wall_cabinet | 0.07 | nothing fits: kitchen_run: no candidate position fits the room |
| Salon (r_L-1b_salon_2) | living | completed | kitchen_run, dining, island, island | #1 2.8 0 | - | - | wall_cabinet, wall_cabinet, wall_cabinet | 0.07 | nothing fits: kitchen_run: no candidate position fits the room; partner r_L-1b_salon (twin) not used: the twin's drawn furniture does not map onto this room: drawn unknown f_L-1b_046 has no counterpart here; completed itself |
| Koridor (r_L-1b_koridor) | hall | completed | - | #1 8.0 0, #2 8.0 0, #3 8.0 0 | 1 | vlm | shoe_cabinet | 0.12 | - |
| Koridor (r_L-1b_koridor_2) | hall | mirrored | - | - | - | - | shoe_cabinet | 0.00 | decisions of r_L-1b_koridor (twin), not asked again |
| Banyo (r_L-1b_banyo) | bathroom | copied | - | - | - | - | - | 0.00 | decisions of r_L-1_banyo (same_as), not asked again |
| Banyo (r_L-1b_banyo_2) | bathroom | copied | - | - | - | - | - | 0.00 | decisions of r_L-1_banyo_2 (same_as), not asked again |
| Yatak Odası (r_L0_yatak_odasi) | bedroom | completed | sleeping_double, storage, storage | #1 24.2 0, #2 16.4 0 | 1 | vlm | nightstand, nightstand, desk, office_chair | 0.09 | - |
| E.yatak Odası (r_L0_e_yatak_odasi) | bedroom | completed | - | #1 2.9 0 | - | - | - | 0.05 | nothing fits: storage: no candidate position fits the room; work: no place passes the checks |
| E.yatak Odası (r_L0_e_yatak_odasi_2) | bedroom | mirrored | - | - | - | - | - | 0.00 | decisions of r_L0_e_yatak_odasi (twin), not asked again |
| Yatak Odası (r_L0_yatak_odasi_2) | bedroom | completed | sleeping_double, storage, storage | #1 24.2 0, #2 16.4 0 | 1 | vlm | nightstand, nightstand, desk, office_chair | 0.09 | partner r_L0_yatak_odasi (twin) not used: 2 of 4 copied pieces fail a check here (office_chair: the copy fails doors_free here; desk: the copy fails doors_free here); completed itself |
| E.banyo (r_L0_e_banyo) | bathroom | completed | bathroom_set | - | - | - | - | 0.00 | nothing missing: the drawn groups are complete |
| E.banyo (r_L0_e_banyo_2) | bathroom | mirrored | - | - | - | - | - | 0.00 | decisions of r_L0_e_banyo (twin), not asked again |
| Yatak Odası (r_L0_yatak_odasi_3) | bedroom | mirrored | - | - | - | - | - | 0.00 | decisions of r_L0_yatak_odasi_4 (twin), not asked again |
| Merdiven (r_L0_merdiven) | hall | completed | - | #1 1.0 0 | - | - | - | 0.11 | nothing fits: entrance: no candidate position fits the room |
| Merdiven (r_L0_merdiven_2) | hall | mirrored | - | - | - | - | - | 0.00 | decisions of r_L0_merdiven (twin), not asked again |
| Yatak Odası (r_L0_yatak_odasi_4) | bedroom | completed | storage, work | - | - | - | - | 0.00 | nothing missing: the drawn groups are complete |
| Banyo (r_L0_banyo) | bathroom | completed | bathroom_set | #1 2.7 0 | - | - | - | 0.05 | nothing fits: bathroom_set: no candidate position fits the room |
| Banyo (r_L0_banyo_2) | bathroom | mirrored | - | - | - | - | - | 0.00 | decisions of r_L0_banyo (twin), not asked again |
| Teras (r_L1_teras) | balcony | completed | - | #1 6.5 0, #2 6.3 0, #3 6.2 0 | 1 | vlm | table_dining, chair, chair | 0.21 | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi) | other | completed | seating, seating | #1 11.6 0, #2 11.5 0, #3 10.9 0 | 1 | vlm | desk, office_chair | 0.12 | - |
| Oyun Aktivite Ve Dinlenme Odası (r_L1_oyun_aktivite_ve_dinlenme_odasi_2) | other | completed | seating, seating | #1 11.6 0, #2 11.4 0, #3 10.9 0 | 1 | vlm | desk, office_chair | 0.19 | partner r_L1_oyun_aktivite_ve_dinlenme_odasi (twin) not used: the twin's drawn furniture does not map onto this room: drawn unknown f_L1_033 has no counterpart here; completed itself |
| Koridor (r_L1_koridor) | hall | completed | - | #1 8.1 0, #2 8.1 0, #3 8.1 0 | 2 | vlm | console_table | 0.19 | - |
| Koridor (r_L1_koridor_2) | hall | completed | - | #1 8.2 0, #2 8.2 0, #3 8.1 0 | 1 | vlm | shoe_cabinet | 0.14 | - |
| Banyo (r_L1_banyo) | bathroom | completed | bathroom_set | - | - | - | - | 0.00 | nothing missing: the drawn groups are complete |
| Banyo (r_L1_banyo_2) | bathroom | mirrored | - | - | - | - | - | 0.00 | decisions of r_L1_banyo (twin), not asked again |

## Added pieces (35)

| Room | Piece | Type | Group | Centre | Size | Method | From |
|---|---|---|---|---|---|---|---|
| r_L-1_salon | f_L-1_089 | bookshelf | living_storage (anchor, anchor f_L-1_089) | [8.19, 1.80] | 1.00 x 0.35 | rule | - |
| r_L-1_salon_2 | f_L-1_094 | bookshelf | living_storage (anchor, anchor f_L-1_094) | [8.98, 1.80] | 1.00 x 0.35 | rule | f_L-1_089 |
| r_L-1_mutfak | f_L-1_090 | wall_cabinet | - | [3.95, 10.12] | 3.35 x 0.35 | rule | - |
| r_L-1_mutfak | f_L-1_091 | wall_cabinet | - | [1.86, 11.63] | 0.69 x 0.35 | rule | - |
| r_L-1_mutfak | f_L-1_092 | wall_cabinet | - | [3.24, 11.63] | 0.56 x 0.35 | rule | - |
| r_L-1_mutfak_2 | f_L-1_095 | wall_cabinet | - | [13.23, 10.12] | 3.36 x 0.35 | rule | - |
| r_L-1_mutfak_2 | f_L-1_096 | wall_cabinet | - | [13.93, 11.63] | 0.56 x 0.35 | rule | - |
| r_L-1_mutfak_2 | f_L-1_097 | wall_cabinet | - | [15.32, 11.63] | 0.69 x 0.35 | rule | - |
| r_L-1_koridor | f_L-1_098 | shoe_cabinet | entrance (partner, anchor -) | [12.63, 11.63] | 0.60 x 0.30 | rule | f_L-1_093 |
| r_L-1_koridor_2 | f_L-1_093 | shoe_cabinet | entrance (partner, anchor -) | [4.54, 11.63] | 0.60 x 0.30 | rule | - |
| r_L-1b_salon | f_L-1b_079 | wall_cabinet | - | [1.50, 7.17] | 0.59 x 0.35 | rule | - |
| r_L-1b_salon | f_L-1b_080 | wall_cabinet | - | [3.29, 7.17] | 1.47 x 0.35 | rule | - |
| r_L-1b_salon | f_L-1b_081 | wall_cabinet | - | [1.38, 5.53] | 2.42 x 0.35 | rule | - |
| r_L-1b_salon_2 | f_L-1b_083 | wall_cabinet | - | [13.88, 7.17] | 1.47 x 0.35 | rule | - |
| r_L-1b_salon_2 | f_L-1b_084 | wall_cabinet | - | [15.67, 7.17] | 0.60 x 0.35 | rule | - |
| r_L-1b_salon_2 | f_L-1b_085 | wall_cabinet | - | [15.80, 5.53] | 2.42 x 0.35 | rule | - |
| r_L-1b_koridor | f_L-1b_082 | shoe_cabinet | entrance (partner, anchor -) | [4.64, 11.63] | 0.60 x 0.30 | rule | - |
| r_L-1b_koridor_2 | f_L-1b_086 | shoe_cabinet | entrance (partner, anchor -) | [12.54, 11.63] | 0.60 x 0.30 | rule | f_L-1b_082 |
| r_L0_yatak_odasi | f_L0_049 | nightstand | sleeping_double (partner, anchor f_L0_017) | [1.43, 4.00] | 0.40 x 0.40 | rule | - |
| r_L0_yatak_odasi | f_L0_050 | nightstand | sleeping_double (partner, anchor f_L0_017) | [1.43, 2.01] | 0.40 x 0.40 | rule | - |
| r_L0_yatak_odasi | f_L0_051 | desk | work (anchor, anchor f_L0_051) | [3.90, 5.02] | 1.20 x 0.60 | rule | - |
| r_L0_yatak_odasi | f_L0_052 | office_chair | work (partner, anchor f_L0_051) | [3.25, 5.02] | 0.60 x 0.60 | rule | - |
| r_L0_yatak_odasi_2 | f_L0_053 | nightstand | sleeping_double (partner, anchor f_L0_018) | [15.75, 2.01] | 0.40 x 0.40 | rule | - |
| r_L0_yatak_odasi_2 | f_L0_054 | nightstand | sleeping_double (partner, anchor f_L0_018) | [15.75, 4.00] | 0.40 x 0.40 | rule | - |
| r_L0_yatak_odasi_2 | f_L0_055 | desk | work (anchor, anchor f_L0_055) | [13.28, 5.02] | 1.20 x 0.60 | rule | - |
| r_L0_yatak_odasi_2 | f_L0_056 | office_chair | work (partner, anchor f_L0_055) | [13.93, 5.02] | 0.60 x 0.60 | rule | - |
| r_L1_teras | f_L1_040 | table_dining | balcony (anchor, anchor f_L1_040) | [2.25, 4.75] | 0.70 x 0.70 | rule | - |
| r_L1_teras | f_L1_041 | chair | balcony (partner, anchor f_L1_040) | [2.25, 4.13] | 0.45 x 0.45 | rule | - |
| r_L1_teras | f_L1_042 | chair | balcony (partner, anchor f_L1_040) | [2.25, 5.38] | 0.45 x 0.45 | rule | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_043 | desk | work (anchor, anchor f_L1_043) | [3.12, 4.12] | 1.20 x 0.60 | rule | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi | f_L1_044 | office_chair | work (partner, anchor f_L1_043) | [3.77, 4.12] | 0.60 x 0.60 | rule | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_047 | desk | work (anchor, anchor f_L1_047) | [14.05, 4.12] | 1.20 x 0.60 | rule | - |
| r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | f_L1_048 | office_chair | work (partner, anchor f_L1_047) | [13.40, 4.12] | 0.60 x 0.60 | rule | - |
| r_L1_koridor | f_L1_045 | console_table | entrance (partner, anchor -) | [4.79, 11.63] | 0.90 x 0.30 | rule | - |
| r_L1_koridor_2 | f_L1_046 | shoe_cabinet | entrance (partner, anchor -) | [12.68, 11.48] | 0.60 x 0.30 | rule | - |

## Choices of the vision model

- r_L-1_koridor_2: candidate 1: The shoe cabinet is the most functional entrance piece for a corridor, and its placement against the top wall keeps the main walkway clear and balanced.
- r_L-1b_koridor: candidate 1: The shoe cabinet is the most functional entrance piece for a corridor, and its placement against the top wall keeps the main walkway clear with the best circulation score.
- r_L0_yatak_odasi: candidate 1: Includes a functional desk and chair setup for a complete bedroom, with good circulation and the bed positioned to see the door, despite slightly lower circulation score than candidate 2.
- r_L0_yatak_odasi_2: candidate 1: Includes a functional desk area with good side lighting and maintains a balanced layout, whereas Candidate 2 leaves the work zone empty.
- r_L1_teras: candidate 1: Dining set is positioned to keep the main walkway clear and offers the best balance of circulation and daylight for the terrace.
- r_L1_oyun_aktivite_ve_dinlenme_odasi: candidate 1: Desk is positioned near the window for optimal natural light and the layout maintains good circulation and balance in the room.
- r_L1_oyun_aktivite_ve_dinlenme_odasi_2: candidate 1: Desk is placed by the window for natural side light, keeping the central walkway open and the room balanced.
- r_L1_koridor: candidate 2: The console table is a more appropriate and elegant piece for a modern natural hallway entrance than a bulky shoe cabinet, keeping the space open and balanced.
- r_L1_koridor_2: candidate 1: Shoe cabinet is placed at the entrance alcove, keeping the main walkway clear and the layout balanced.

## Groups not completed and copies dropped (9)

- r_L-1_salon: dining: no place passes the checks
- r_L-1_mutfak: kitchen_run: no place passes the checks
- r_L-1_mutfak: dining: no place passes the checks
- r_L-1b_salon: kitchen_run: no candidate position fits the room
- r_L-1b_salon_2: kitchen_run: no candidate position fits the room
- r_L0_e_yatak_odasi: storage: no candidate position fits the room
- r_L0_e_yatak_odasi: work: no place passes the checks
- r_L0_merdiven: entrance: no candidate position fits the room
- r_L0_banyo: bathroom_set: no candidate position fits the room

## Locked check: pass

