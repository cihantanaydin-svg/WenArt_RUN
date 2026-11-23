# Dataset bench: Swiss Dwellings in a Turkish drafting style

107 projects (76 orthogonal, 31 with angled walls), 198 floors, 106 scored, 1 failed. Mean project total 73.79 (all); where the drawing scale was read: 77.44 (101 projects, 186 floors), orthogonal 80.08 (71 projects), angled 71.19 (30 projects).

| kind | truth | read | matched | recall | precision | F1 all | F1 scale read | F1 orthogonal | F1 angled |
|---|---|---|---|---|---|---|---|---|---|
| levels | 198 | 217 | 183 | 0.924 | 0.843 | 0.882 | 0.908 | 0.916 | 0.887 |
| rooms | 3324 | 3404 | 2520 | 0.758 | 0.740 | 0.749 | 0.771 | 0.799 | 0.688 |
| walls | 11297 | 12941 | 8491 | 0.752 | 0.656 | 0.701 | 0.719 | 0.766 | 0.612 |
| doors | 3605 | 3438 | 2857 | 0.792 | 0.831 | 0.811 | 0.836 | 0.864 | 0.756 |
| windows | 2535 | 2912 | 2035 | 0.803 | 0.699 | 0.747 | 0.768 | 0.812 | 0.644 |
| stairs | 59 | 53 | 30 | 0.508 | 0.566 | 0.536 | 0.536 | 0.588 | 0.370 |
| walls, length-weighted (m) | 38495 | 33135 | 29966 | 0.778 | 0.898 | 0.834 | 0.859 | 0.882 | 0.789 |
| room types (of matched rooms) | 2520 | | 2474 | | | 0.9817 | 0.9817 | 0.9821 | 0.9804 |

The class columns count the projects whose drawing scale was read (a floor not read says nothing about walls at an angle). Walls are scored twice: one to one (`match_walls`: a drawn wall read in pieces counts one piece) and length-weighted (`wall_coverage`: the length of the truth's walls that read walls of the same thickness cover on their line, and of the read walls on truth walls; pieces that build the same solid count as the wall).

## Error classes

| class | count | example |
|---|---|---|
| wall split (a piece of a drawn wall read as a wall of its own) | 1151 | swiss-b1074 L0: [16.525, 13.08]-[16.525, 13.29] t=0.19 |
| wall invented (on no drawn wall line) | 1089 | swiss-b1074 L1: [3.675, 6.029]-[3.8949999999999996, 6.029] t=0.075 |
| wall read with another thickness | 791 | swiss-b1074 L0: w_L0_014 [9.96, 0.695]-[13.3, 0.695] t=0.295 |
| wall missed | 603 | swiss-b1074 L0: w_L0_008 [0.215, 0.005]-[0.215, 11.88] t=0.425 |
| door missed | 405 | swiss-b1128 L0: d_L0_002 0.75 m at [19.655, 3.5] |
| window missed | 313 | swiss-b1167 L1: win_L1_006 3.35 m at [-1.645, 0.835] |
| window invented | 302 | swiss-b1074 L0: 1.46 m at [7.42, 15.251] |
| angled wall missed | 251 | swiss-b154 L0: w_L0_044 [11.495, 15.385]-[12.145, 14.735] t=0.04 |
| thin wall (< 10 cm) missed | 240 | swiss-b1074 L1: w_L1_028 [12.985, 6.105]-[13.335, 6.105] t=0.08 |
| angled wall read as axis-aligned steps | 220 | swiss-b15161 L1: [13.79, 13.892]-[13.81, 13.892] t=0.53 |
| parapet wall missed | 174 | swiss-b1074 L0: w_L0_002 [0.215, 11.87]-[0.215, 13.09] t=0.065 |
| room split (one drawn room read as several) | 171 | swiss-b1074 L1: Oda at [10.72, 6.813] |
| rooms merged (two drawn rooms read as one) | 148 | swiss-b1128 L0: SALON + MUTFAK 88.7655 m2 at [5.152528, 5.558537] |
| room invented | 131 | swiss-b1074 L0: Oda at [10.578, 12.236] |
| door invented | 123 | swiss-b1074 L0: 0.9 m at [9.094, 6.506] |
| room invented in a wall cavity or a narrow gap | 122 | swiss-b1074 L0: Oda at [13.092, 5.798] |
| room missed (balcony) | 108 | swiss-b1141 L0: TERAS 82.1314 m2 at [54.992932, 5.638961] |
| door read as opening | 74 | swiss-b1128 L0: d_L0_018 0.85 m at [26.16, 11.21] |
| room missed (bedroom) | 67 | swiss-b1141 L0: ODA 20.7865 m2 at [49.10625, 4.8175] |
| room missed (living) | 66 | swiss-b1128 L0: SALON + MUTFAK 42.9542 m2 at [19.983352, 8.043793] |
| room label wrong | 48 | swiss-b15161 L2: ANTRE read Oda at [7.195967, 7.190588] |
| room missed (shaft) | 45 | swiss-b1128 L0: ASANSOR 0.6044 m2 at [23.27625, 10.1625] |
| room missed (bathroom) | 38 | swiss-b1141 L0: BANYO 4.6013 m2 at [7.46, 8.2525] |
| frame offset (a level read in another origin or turned) | 37 | swiss-b1074 L0: shift [-0.24, 0.0] m, turn 0.0 deg |
| level invented | 34 | swiss-b1128 L1: L1 |
