# Dataset bench: Swiss Dwellings in a Turkish drafting style

107 projects (76 orthogonal, 31 with angled walls), 198 floors, 106 scored, 1 failed. Mean project total 76.22 (all); where the drawing scale was read: 79.99 (101 projects, 186 floors), orthogonal 82.0 (71 projects), angled 75.23 (30 projects).

| kind | truth | read | matched | recall | precision | F1 all | F1 scale read | F1 orthogonal | F1 angled |
|---|---|---|---|---|---|---|---|---|---|
| levels | 198 | 219 | 185 | 0.934 | 0.845 | 0.887 | 0.914 | 0.916 | 0.907 |
| rooms | 3324 | 3403 | 2598 | 0.782 | 0.763 | 0.772 | 0.795 | 0.821 | 0.721 |
| walls | 11167 | 11892 | 8611 | 0.771 | 0.724 | 0.747 | 0.767 | 0.815 | 0.657 |
| doors | 3605 | 3504 | 2898 | 0.804 | 0.827 | 0.815 | 0.840 | 0.864 | 0.773 |
| windows | 2535 | 2815 | 2067 | 0.815 | 0.734 | 0.773 | 0.795 | 0.837 | 0.676 |
| stairs | 59 | 86 | 55 | 0.932 | 0.639 | 0.759 | 0.759 | 0.788 | 0.696 |
| walls, length-weighted (m) | 38495 | 33591 | 30718 | 0.798 | 0.909 | 0.850 | 0.875 | 0.895 | 0.815 |
| room types (of matched rooms) | 2598 | | 2546 | | | 0.98 | 0.98 | 0.9805 | 0.9784 |

The class columns count the projects whose drawing scale was read (a floor not read says nothing about walls at an angle). Walls are scored twice: one to one (the bench's own `bench_match_walls` and `wall_verdicts` since 23 Nov 2026: the longest overlap first, a match covers 30 % of the truth wall, a thickness misread is one error, a block on the drawing's wall material and a wall inside two overlapping truth walls are not counted; a drawn wall read in pieces counts one piece) and length-weighted (`wall_coverage`: the length of the truth's walls that read walls of the same thickness cover on their line, and of the read walls on truth walls; pieces that build the same solid count as the wall).

## Error classes

| class | count | example |
|---|---|---|
| wall missed | 624 | swiss-b1074 L0: w_L0_008 [0.215, 0.005]-[0.215, 11.88] t=0.425 |
| wall invented (on no drawn wall line) | 520 | swiss-b1128 L0: [9.215, 11.815]-[14.37, 11.815] t=0.13 |
| wall split (a piece of a drawn wall read as a wall of its own) | 457 | swiss-b1128 L0: [22.326, 3.505]-[22.88, 3.505] t=0.275 |
| walls merged (read as part of a neighbouring wall on its line) | 411 | swiss-b1074 L0: w_L0_006 [0.21, 15.26]-[6.7, 15.26] t=0.04 |
| door missed | 394 | swiss-b1128 L0: d_L0_002 0.75 m at [19.655, 3.5] |
| angled wall missed | 306 | swiss-b154 L0: w_L0_044 [11.495, 15.385]-[12.145, 14.735] t=0.04 |
| window missed | 296 | swiss-b1167 L1: win_L1_006 3.35 m at [-1.645, 0.835] |
| wall read with another thickness | 259 | swiss-b1074 L0: w_L0_046 [4.365, 10.35]-[4.365, 11.55] t=0.225 |
| window invented | 217 | swiss-b1074 L0: 1.46 m at [7.42, 15.251] |
| thin wall (< 10 cm) missed | 177 | swiss-b1074 L1: w_L1_028 [12.985, 6.105]-[13.335, 6.105] t=0.08 |
| rooms merged (two drawn rooms read as one) | 154 | swiss-b1128 L0: SALON + MUTFAK 88.7655 m2 at [5.152528, 5.558537] |
| room split (one drawn room read as several) | 151 | swiss-b1074 L1: Oda at [10.72, 6.813] |
| door invented | 130 | swiss-b1074 L0: 0.9 m at [9.094, 6.506] |
| parapet wall missed | 120 | swiss-b1074 L0: w_L0_002 [0.215, 11.87]-[0.215, 13.09] t=0.065 |
| room missed (balcony) | 106 | swiss-b1141 L0: TERAS 82.1314 m2 at [54.992932, 5.638961] |
| room invented | 106 | swiss-b1074 L0: Oda at [10.578, 12.236] |
| angled wall read as axis-aligned steps | 103 | swiss-b1737 L0: [9.211, 2.01]-[9.272, 2.01] t=0.28 |
| door read as opening | 74 | swiss-b1128 L0: d_L0_018 0.85 m at [26.16, 11.21] |
| room missed (living) | 62 | swiss-b1128 L0: SALON + MUTFAK 42.9542 m2 at [19.983352, 8.043793] |
| room missed (bedroom) | 60 | swiss-b1141 L0: ODA 20.7865 m2 at [49.10625, 4.8175] |
| room label wrong | 53 | swiss-b15161 L2: ANTRE read Oda at [7.195967, 7.190588] |
| room invented in a wall cavity or a narrow gap | 46 | swiss-b1074 L1: Depo at [12.063, 6.409] |
| frame offset (a level read in another origin or turned) | 37 | swiss-b1074 L0: shift [-0.24, 0.0] m, turn 0.0 deg |
| room missed (bathroom) | 34 | swiss-b1141 L0: BANYO 4.6013 m2 at [7.46, 8.2525] |
| level invented | 34 | swiss-b1128 L1: L1 |
