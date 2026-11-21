# Dataset bench: Swiss Dwellings in a Turkish drafting style

107 projects (76 orthogonal, 31 with angled walls), 201 floors, 107 scored, 0 failed. Mean project total 56.93 (all); where the drawing scale was read: 71.9 (80 projects, 166 floors), orthogonal 74.94 (59 projects), angled 63.39 (21 projects).

| kind | truth | read | matched | recall | precision | F1 all | F1 scale read | F1 orthogonal | F1 angled |
|---|---|---|---|---|---|---|---|---|---|
| levels | 201 | 206 | 172 | 0.856 | 0.835 | 0.845 | 0.898 | 0.909 | 0.864 |
| rooms | 3432 | 3033 | 2205 | 0.642 | 0.727 | 0.682 | 0.753 | 0.793 | 0.612 |
| walls | 11519 | 15554 | 7139 | 0.620 | 0.459 | 0.527 | 0.573 | 0.700 | 0.359 |
| doors | 3707 | 3029 | 2439 | 0.658 | 0.805 | 0.724 | 0.808 | 0.841 | 0.698 |
| windows | 2595 | 2571 | 1735 | 0.669 | 0.675 | 0.672 | 0.738 | 0.790 | 0.574 |
| stairs | 59 | 60 | 27 | 0.458 | 0.450 | 0.454 | 0.505 | 0.550 | 0.370 |
| walls, length-weighted (m) | 39474 | 28618 | 25086 | 0.635 | 0.870 | 0.735 | 0.820 | 0.857 | 0.689 |
| room types (of matched rooms) | 2205 | | 2163 | | | 0.981 | 0.981 | 0.9828 | 0.9724 |

The class columns count the projects whose drawing scale was read (a floor not read says nothing about walls at an angle). Walls are scored twice: one to one (`match_walls`: a drawn wall read in pieces counts one piece) and length-weighted (`wall_coverage`: the length of the truth's walls that read walls of the same thickness cover on their line, and of the read walls on truth walls; pieces that build the same solid count as the wall).

## Error classes

| class | count | example |
|---|---|---|
| wall split (a piece of a drawn wall read as a wall of its own) | 3612 | swiss-b1074 L0: [6.493, 10.58]-[6.493, 13.25] t=0.335 |
| wall invented (on no drawn wall line) | 1744 | swiss-b1074 L0: [12.966000000000001, 0.415]-[13.120000000000001, 0.415] t=0.83 |
| wall missed | 745 | swiss-b1074 L0: w_L0_008 [0.215, 0.005]-[0.215, 11.88] t=0.425 |
| angled wall read as axis-aligned steps | 693 | swiss-b15161 L1: [13.88, 11.607]-[13.9, 11.607] t=0.1 |
| wall read with another thickness | 670 | swiss-b1074 L0: w_L0_014 [9.96, 0.695]-[13.3, 0.695] t=0.295 |
| door missed | 459 | swiss-b1128 L0: d_L0_002 0.75 m at [19.655, 3.5] |
| window missed | 358 | swiss-b1167 L1: win_L1_006 3.35 m at [-1.645, 0.835] |
| window invented | 281 | swiss-b1074 L0: 1.46 m at [7.42, 15.25] |
| angled wall missed | 247 | swiss-b154 L0: w_L0_044 [11.495, 15.385]-[12.145, 14.735] t=0.04 |
| thin wall (< 10 cm) missed | 239 | swiss-b1074 L1: w_L1_028 [12.985, 6.105]-[13.335, 6.105] t=0.08 |
| parapet wall missed | 198 | swiss-b1074 L0: w_L0_002 [0.215, 11.87]-[0.215, 13.09] t=0.065 |
| room split (one drawn room read as several) | 151 | swiss-b1074 L1: Oda at [10.72, 6.812] |
| door invented | 133 | swiss-b1074 L0: 0.9 m at [9.094, 6.505] |
| rooms merged (two drawn rooms read as one) | 130 | swiss-b1128 L0: SALON + MUTFAK 88.7655 m2 at [5.152528, 5.558537] |
| room invented in a wall cavity or a narrow gap | 119 | swiss-b1074 L0: Oda at [13.092, 5.797] |
| room invented | 106 | swiss-b1074 L0: Oda at [10.578, 12.235] |
| room missed (balcony) | 95 | swiss-b1167 L1: ORTAK TERAS 12.9156 m2 at [-1.755877, -1.182133] |
| room missed (bedroom) | 81 | swiss-b1167 L1: ODA 15.2102 m2 at [2.556166, 2.569135] |
| room missed (living) | 73 | swiss-b1128 L0: SALON + MUTFAK 42.9542 m2 at [19.983352, 8.043793] |
| door read as opening | 59 | swiss-b1128 L0: d_L0_018 0.85 m at [26.16, 11.21] |
| room missed (bathroom) | 46 | swiss-b1613 L0: DUS 3.0743 m2 at [20.439042, 7.189598] |
| room label wrong | 46 | swiss-b15161 L2: ANTRE read Oda at [7.195967, 7.190588] |
| room missed (shaft) | 43 | swiss-b1128 L0: ASANSOR 0.6044 m2 at [23.27625, 10.1625] |
| frame offset (a level read in another origin or turned) | 38 | swiss-b1074 L0: shift [-0.24, 0.0] m, turn 0.0 deg |
| floor not read: drawing scale not found or misread | 35 | swiss-b1141 L0: unit cm, $INSUNITS 0, dimensions as DIMENSION entities |
